"""
Assembler for unified API responses.
"""

import uuid
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional
import time
import asyncio
import sys
import os

from models import (
    UnifiedResponse, RequestInfo, Source, SourceData,
    Derived, IChingDerived, EggDerived, Metadata, MetadataChecks
)
from fetchers import (
    fetch_anu_uint16, fetch_lfd_hex, read_curby_local,
    generate_fallback_uint16_from_quantum, compute_sha256, compute_monobit_ratio
)
from iching_unified import cast_iching_hexagram

# Import egg data fetcher
_egg_module_available = False
_egg_import_error = None
get_eggdata = None

try:
    # Add parent directory to path
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from egg.getdata import get_eggdata
    _egg_module_available = True
except ImportError as e:
    _egg_import_error = str(e)
    # Try alternative import
    try:
        egg_path = os.path.join(os.path.dirname(__file__), '..', 'egg')
        sys.path.insert(0, egg_path)
        from getdata import get_eggdata
        _egg_module_available = True
        _egg_import_error = None
    except ImportError as e2:
        _egg_import_error = str(e2)


def build_unified_response(
    anu_len: int = 6,
    lfd_bytes: int = 64,
    curby_kind: str = "u32",
    curby_path: str = "random_packed_u32be.csv",
    curby_count: int = 1,
    include_iching: bool = True,
    include_egg: bool = False
) -> UnifiedResponse:
    """
    Build a complete unified response by fetching all sources.
    
    Args:
        anu_len: Number of uint16 values to fetch from ANU
        lfd_bytes: Number of bytes to fetch from LfD
        curby_kind: 'u8' or 'u32' for CURBy data type
        curby_path: Path to CURBy CSV file
        curby_count: Number of values (currently only 1 supported)
        include_iching: Whether to include I Ching derivation
        include_egg: Whether to include Global Consciousness Project egg data
        
    Returns:
        UnifiedResponse object
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    sources = []
    errors = []
    all_bytes = bytearray()
    
    # Fetch Source 2 (LfD) FIRST for fallback use
    lfd_result = fetch_lfd_hex(lfd_bytes)
    lfd_data_bytes = None
    
    if lfd_result["success"]:
        lfd_data_bytes = lfd_result["data_bytes"]
        sha256 = compute_sha256(lfd_data_bytes)
        all_bytes.extend(lfd_data_bytes)
        
        sources.append(Source(
            id="lfd",
            name="LfD Laboratorium QRNG",
            endpoint=lfd_result["url"],
            method="https-get",
            technique="quantum_photonics_IDQ",
            format_in="hex",
            encoding="hex",
            unit_bits=8,
            count=lfd_bytes,
            data=SourceData(
                hex=lfd_result["data_hex"],
                uint8=lfd_result["data_uint8"],
                bytes_b64=base64.b64encode(lfd_data_bytes).decode()
            ),
            transform=["decode:hex"],
            sha256_hex=sha256,
            fallback_used=False
        ))
    else:
        errors.append(f"LfD QRNG: {lfd_result['error']}")
    
    # Fetch Source 1 (ANU) with fallback
    anu_result = fetch_anu_uint16(anu_len)
    anu_fallback = False
    
    if not anu_result["success"] and lfd_data_bytes:
        # Use fallback
        anu_result = generate_fallback_uint16_from_quantum(lfd_data_bytes, anu_len)
        anu_fallback = True
        if not anu_result["success"]:
            errors.append(f"ANU QRNG (fallback): {anu_result['error']}")
    elif not anu_result["success"]:
        errors.append(f"ANU QRNG: {anu_result['error']}")
    
    if anu_result["success"]:
        anu_data_bytes = anu_result["data_bytes"]
        sha256 = compute_sha256(anu_data_bytes)
        all_bytes.extend(anu_data_bytes)
        
        technique = "quantum_photonics_IDQ_seeded" if anu_fallback else "vacuum_fluctuation_optics"
        
        sources.append(Source(
            id="anu",
            name="ANU Quantum Random Numbers",
            endpoint=anu_result["url"],
            method="https-get" if not anu_fallback else "https-get",
            technique=technique,
            format_in="uint16",
            encoding="none",
            unit_bits=16,
            count=anu_len,
            data=SourceData(
                uint16=anu_result["data_uint16"],
                bytes_b64=base64.b64encode(anu_data_bytes).decode()
            ),
            transform=["none"] if not anu_fallback else ["derive:lfd[0..11]"],
            sha256_hex=sha256,
            fallback_used=anu_fallback
        ))
        
        # Use first value as seed for CURBy
        seed = anu_result["data_uint16"][0]
    else:
        seed = None
    
    # Fetch Source 3 (CURBy local) if we have a seed
    if seed is not None:
        curby_result = read_curby_local(curby_path, seed, curby_kind)
        
        if curby_result["success"]:
            curby_data_bytes = curby_result["data_bytes"]
            sha256 = compute_sha256(curby_data_bytes)
            all_bytes.extend(curby_data_bytes)
            
            data_obj = SourceData(bytes_b64=base64.b64encode(curby_data_bytes).decode())
            
            if curby_kind == "u32":
                data_obj.uint32 = curby_result["data_uint32"]
            elif curby_kind == "u8":
                data_obj.uint8 = curby_result["data_uint8"]
            
            sources.append(Source(
                id="curby_local",
                name="CURBy Local Quantum Data",
                endpoint=f"file://{curby_result['file_path']}",
                method="file",
                technique="sha3_extracted_quantum",
                format_in="uint32" if curby_kind == "u32" else "uint8",
                encoding="none",
                unit_bits=32 if curby_kind == "u32" else 8,
                count=curby_count,
                data=data_obj,
                transform=[
                    "packing:1->0,2->1(msb)",
                    "extractor:sha3-256-block"
                ],
                sha256_hex=sha256,
                fallback_used=False
            ))
        else:
            errors.append(f"CURBy local: {curby_result['error']}")
    else:
        errors.append("CURBy local: No seed available (ANU fetch failed)")
    
    # Derive I Ching hexagram if requested and LfD data available
    derived = Derived()
    if include_iching and lfd_data_bytes and len(lfd_data_bytes) >= 18:
        try:
            iching_bytes = lfd_data_bytes[12:18]
            iching_result = cast_iching_hexagram(iching_bytes, "lfd[bytes 12..17]")
            derived.iching = IChingDerived(**iching_result)
        except Exception as e:
            errors.append(f"I Ching derivation: {str(e)}")
    
    # Fetch Global Consciousness Project egg data if requested
    if include_egg:
        if not _egg_module_available or get_eggdata is None:
            error_msg = "Egg data: Module not available"
            if _egg_import_error:
                error_msg += f" ({_egg_import_error})"
            if "playwright" in str(_egg_import_error).lower():
                error_msg += ". Install with: pip install playwright && playwright install chromium"
            errors.append(error_msg)
        else:
            try:
                # Run async function in sync context
                egg_result = asyncio.run(get_eggdata())
                if egg_result:
                    derived.egg = EggDerived(
                        source="global-mind.org",
                        persec=egg_result.get('persec'),
                        persecz=egg_result.get('persecz'),
                        perseczcs=egg_result.get('perseczcs'),
                        stouffer=egg_result.get('stouffer')
                    )
                else:
                    errors.append("Egg data: Failed to fetch data")
            except Exception as e:
                errors.append(f"Egg data: {str(e)}")
    
    # Compute metadata
    monobit = compute_monobit_ratio(bytes(all_bytes)) if all_bytes else None
    
    metadata = Metadata(
        description="Combined quantum randomness with I Ching derivation and Global Consciousness Project egg data (https://global-mind.org/realtime/)",
        checks=MetadataChecks(
            byte_len_total=len(all_bytes),
            monobit_ratio=monobit
        )
    )
    
    # Build request info
    latency_ms = int((time.time() - start_time) * 1000)
    request = RequestInfo(
        request_id=request_id,
        timestamp=timestamp,
        success=len(errors) == 0,
        latency_ms=latency_ms,
        errors=errors
    )
    
    return UnifiedResponse(
        version="1.0",
        request=request,
        sources=sources,
        derived=derived,
        metadata=metadata
    )

