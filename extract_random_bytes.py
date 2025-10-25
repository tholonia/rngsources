#!/usr/bin/env python3
import argparse, base64, binascii, hashlib, json, sys, time, zlib
from datetime import datetime, timezone

def read_data(path):
    with open(path, "rb") as f:
        return f.read().strip()

def maybe_base64_decode(buf):
    try:
        return base64.b64decode(buf, validate=True), True
    except binascii.Error:
        return buf, False

def maybe_zlib_decompress(buf):
    try:
        return zlib.decompress(buf), True
    except Exception:
        return buf, False

def extract_12_symbols_from_words(buf):
    """
    Observed layout (Colorado 'Data'):
      repeating 4-byte words: [b0, b1, b2, b3]
      b0,b1 are symbols in {1,2}; b2,b3 ~ always 0 (padding).
    Return a bytes object containing only the {1,2} symbols (order-preserving).
    """
    out = bytearray()
    n = len(buf)
    for i in range(0, n - (n % 4), 4):
        b0, b1 = buf[i], buf[i+1]
        if b0 in (1, 2): out.append(b0)
        if b1 in (1, 2): out.append(b1)
    return bytes(out)

def pack_bits_from_12(sym12):
    """Map {1,2}->{0,1} and pack 8 bits per byte."""
    out = bytearray()
    acc = 0
    nbits = 0
    for b in sym12:
        bit = 0 if b == 1 else 1
        acc = (acc << 1) | bit
        nbits += 1
        if nbits == 8:
            out.append(acc)
            acc = 0
            nbits = 0
    return bytes(out)

def sha3_extract(buf, block=4096):
    """
    Strong extractor: hash fixed-size blocks with SHA3-256 and concatenate digests.
    (Not reversible; intended to remove tiny bias.)
    """
    out = bytearray()
    for i in range(0, len(buf), block):
        out.extend(hashlib.sha3_256(buf[i:i+block]).digest())
    return bytes(out)

def write_hex_lines(buf, path, bytes_per_line=32):
    with open(path, "w") as f:
        for i in range(0, len(buf), bytes_per_line):
            f.write(buf[i:i+bytes_per_line].hex() + "\n")

def write_u32_csv(buf, path, endian="little"):
    n = len(buf) - (len(buf) % 4)
    with open(path, "w") as f:
        for i in range(0, n, 4):
            chunk = buf[i:i+4]
            val = int.from_bytes(chunk, endian)
            f.write(f"{val}\n")

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def make_json_payload(buf, fmt="bytes", json_bytes_per_value=32, endian="little",
                      source_meta=None, params_meta=None):
    """
    Build a compact JSON object you'll be happy to serve from your API.
    fmt: "bytes" (base64 array), "hex" (hex strings), "u32" (integers), "u8" (integers 0..255)
    """
    data = {}
    if fmt == "bytes":
        values = []
        for i in range(0, len(buf), json_bytes_per_value):
            values.append(base64.b64encode(buf[i:i+json_bytes_per_value]).decode())
        data = {"values": values, "encoding": "base64", "bytes_per_value": json_bytes_per_value}
    elif fmt == "hex":
        values = []
        for i in range(0, len(buf), json_bytes_per_value):
            values.append("0x" + buf[i:i+json_bytes_per_value].hex())
        data = {"values": values, "encoding": "hex", "bytes_per_value": json_bytes_per_value}
    elif fmt == "u32":
        n = len(buf) - (len(buf) % 4)
        vals = [int.from_bytes(buf[i:i+4], endian) for i in range(0, n, 4)]
        data = {"values": vals, "type": f"uint32_{endian}"}
    elif fmt == "u8":
        data = {"values": list(buf), "type": "uint8"}
    else:
        raise ValueError("Unsupported json format")

    payload = {
        "version": "1.0",
        "request": {
            "request_id": hashlib.sha3_256(str(time.time_ns()).encode()).hexdigest()[:16],
            "timestamp": now_iso(),
            "params": params_meta or {}
        },
        "data": data,
        "metadata": {
            "source": source_meta or {},
            "performance": {
                "bytes": len(buf)
            }
        },
        "integrity": {
            "value_hash": "sha3-256:" + hashlib.sha3_256(buf).hexdigest()
        }
    }
    return payload

def main():
    p = argparse.ArgumentParser(description="Extract uniform random bytes from Colorado 'Data' and write multiple formats.")
    p.add_argument("--input", default="Data", help="Input file: 'Data' (Base64+zlib) or Data.raw if --raw is set")
    p.add_argument("--raw", action="store_true", help="Treat input as already raw (skip Base64+zlib)")
    p.add_argument("--source", choices=["sha3", "packed"], default="sha3",
                   help="Which byte stream to export (default: sha3-extracted)")
    # basic binary outputs
    p.add_argument("--packed-out", default="random.bin", help="Raw packed bytes (1/2→0/1) output path")
    p.add_argument("--sha3-out", default="random_sha3.bin", help="SHA3-extracted bytes output path")
    # hex
    p.add_argument("--hex-out", default=None, help="Write hex lines to this file")
    p.add_argument("--hex-bytes-per-line", type=int, default=32, help="Bytes per hex line (default 32)")
    # u32 CSV
    p.add_argument("--u32csv-out", default=None, help="Write uint32 CSV to this file")
    p.add_argument("--u32-endian", choices=["little", "big"], default="little", help="Endianness for uint32 CSV")
    # JSON
    p.add_argument("--json-out", default=None, help="Write JSON payload to this file")
    p.add_argument("--json-format", choices=["bytes","hex","u32","u8"], default="bytes",
                   help="JSON data format (default: bytes)")
    p.add_argument("--json-bytes-per-value", type=int, default=32,
                   help="For bytes/hex JSON formats: chunk size per value (default 32)")
    args = p.parse_args()

    buf = read_data(args.input)
    if not args.raw:
        buf, _ = maybe_base64_decode(buf)
        buf, _ = maybe_zlib_decompress(buf)

    # extract symbol stream {1,2} and pack to bits→bytes
    sym12 = extract_12_symbols_from_words(buf)
    if not sym12:
        print("No {1,2} symbols found. Are you sure this is the expected format?", file=sys.stderr)
        sys.exit(1)
    packed = pack_bits_from_12(sym12)
    with open(args.packed_out, "wb") as f:
        f.write(packed)

    extracted = sha3_extract(packed)
    with open(args.sha3_out, "wb") as f:
        f.write(extracted)

    # choose active buffer for the extra outputs
    active = extracted if args.source == "sha3" else packed

    # optional hex output
    if args.hex_out:
        write_hex_lines(active, args.hex_out, args.hex_bytes_per_line)

    # optional u32 CSV output
    if args.u32csv_out:
        write_u32_csv(active, args.u32csv_out, args.u32_endian)

    # optional JSON output
    if args.json_out:
        source_meta = {
            "provider": "random.colorado.edu",
            "mechanism": "physical RNG (decoded; 1/2 symbol stream → packed; SHA3 extractor)" if args.source=="sha3"
                         else "physical RNG (decoded; 1/2 symbol stream → packed)",
            "note": "Decompressed from Base64+zlib; positions 2–3 per 4-byte word were padding"
        }
        params_meta = {
            "decoder": {"base64": not args.raw, "zlib": not args.raw},
            "packing": "1->0, 2->1 (MSB first), 8 bits per output byte",
            "extractor": "SHA3-256 block hashing" if args.source=="sha3" else "none",
        }
        payload = make_json_payload(
            active, fmt=args.json_format,
            json_bytes_per_value=args.json_bytes_per_value,
            endian=args.u32_endian,
            source_meta=source_meta,
            params_meta=params_meta
        )
        with open(args.json_out, "w") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    # brief summary
    ones = sum(bin(b).count("1") for b in active)
    total_bits = len(active) * 8
    print(f"symbols={len(sym12):,}  packed={len(packed):,} bytes  extracted(sha3)={len(extracted):,} bytes")
    print(f"active='{args.source}'  monobit ones fraction={ones/total_bits:.6f}")
    if args.hex_out: print(f"hex  -> {args.hex_out}  ({args.hex_bytes_per_line} bytes/line)")
    if args.u32csv_out: print(f"u32  -> {args.u32csv_out}  (endian={args.u32_endian})")
    if args.json_out: print(f"json -> {args.json_out}  (format={args.json_format})")

if __name__ == "__main__":
    main()
