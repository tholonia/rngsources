# Unified Quantum RNG API

A unified, self-describing API for multi-source quantum random number generation with strict schema validation, provenance tracking, and I Ching hexagram derivation.

## Features

- **Multi-source quantum randomness**: ANU QRNG, LfD QRNG, CURBy local data
- **Unified schema**: Versioned, self-describing format with full metadata
- **Integrity checks**: SHA-256 checksums for all data sources
- **I Ching derivation**: Traditional yarrow stick method applied to quantum entropy
- **Automatic fallback**: Quantum-seeded PRNG if primary sources fail
- **Full provenance**: Transformation history and technique descriptions
- **Type safety**: Pydantic models with strict validation
- **Backward compatibility**: Translator for legacy formats

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Default Values

The API and CLI use these default parameters:

| Parameter | Default Value | Range/Options | Description |
|-----------|--------------|---------------|-------------|
| `anu_len` | `6` | 1-1024 | Number of uint16 values from ANU QRNG |
| `lfd_bytes` | `64` | 1-4096 | Number of bytes from LfD QRNG |
| `curby_kind` | `"u32"` | `"u8"`, `"u32"` | CURBy data type |
| `curby_count` | `1` | 1-10 | Number of CURBy values to fetch |
| `curby_path` | `"random_packed_u32be.csv"` | Any valid path | Path to CURBy CSV file |
| `include_iching` | `true` | `true`, `false` | Include I Ching hexagram derivation |

**Example using all defaults:**
```bash
# CLI
python rng_unified.py

# API
curl "http://localhost:8000/random/unified"
```

### CLI Usage

```bash
# Basic usage with defaults
python rng_unified.py --pretty

# Custom parameters
python rng_unified.py --anu-len 10 --lfd-bytes 128 --curby u32 --pretty

# Generate JSON Schema
python rng_unified.py --schema

# Without I Ching derivation
python rng_unified.py --no-iching

# Save to file
python rng_unified.py --pretty --output random_data.json
```

### API Server

```bash
# Start the server
uvicorn app:app --reload

# Or run directly
python app.py
```

Access at `http://localhost:8000`

### API Endpoints

#### GET /random/unified

Main endpoint for fetching unified quantum random data.

**Parameters:**
- `anu_len` (int, default=6): Number of uint16 values from ANU
- `lfd_bytes` (int, default=64): Number of bytes from LfD
- `curby_kind` (str, default="u32"): CURBy data type ("u8" or "u32")
- `curby_count` (int, default=1): Number of CURBy values
- `curby_path` (str): Path to CURBy CSV file
- `include_iching` (bool, default=true): Include I Ching derivation

**Example:**
```bash
curl "http://localhost:8000/random/unified?anu_len=6&lfd_bytes=64&curby_kind=u32&include_iching=true" | jq
```

#### POST /random/legacy

Convert legacy format to unified schema.

#### GET /schema

Get the JSON Schema definition.

#### GET /health

Health check endpoint.

## Schema Overview

### Top-Level Structure

```json
{
  "version": "1.0",
  "request": { ... },
  "sources": [ ... ],
  "derived": { ... },
  "metadata": { ... }
}
```

### Request Block

Tracks request metadata and status.

```json
"request": {
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-10-20T12:34:56.789Z",
  "success": true,
  "latency_ms": 523,
  "errors": []
}
```

**Fields:**
- `request_id`: Unique UUID4 for this request
- `timestamp`: RFC3339 UTC timestamp
- `success`: Overall success status (false if any source failed)
- `latency_ms`: Total request latency in milliseconds
- `errors`: Array of error messages if any occurred

### Sources Array

Standardized descriptor for each quantum source.

```json
"sources": [
  {
    "id": "anu",
    "name": "ANU Quantum Random Numbers",
    "endpoint": "https://qrng.anu.edu.au/API/jsonI.php?length=6&type=uint16",
    "method": "https-get",
    "technique": "vacuum_fluctuation_optics",
    "format_in": "uint16",
    "encoding": "none",
    "unit_bits": 16,
    "count": 6,
    "data": {
      "uint16": [52766, 44842, 60913, 55109, 51858, 10022],
      "bytes_b64": "zgZu6u7R13VTnpJg"
    },
    "transform": ["none"],
    "sha256_hex": "a1b2c3d4...",
    "fallback_used": false
  }
]
```

**Fields:**
- `id`: Short identifier (anu|lfd|curby_local)
- `name`: Human-readable name
- `endpoint`: URL or file:// path
- `method`: Access method (https-get|file)
- `technique`: Quantum generation technique enum
- `format_in`: Input format type (uint8|uint16|uint32|hex)
- `encoding`: Encoding method (none|hex|base64)
- `unit_bits`: Bits per unit
- `count`: Number of elements or bytes
- `data`: Multi-format data representation
- `transform`: Ordered list of transformations applied
- `sha256_hex`: SHA-256 checksum of raw bytes
- `fallback_used`: Whether fallback mechanism was used

### Techniques

| Technique | Source | Description |
|-----------|--------|-------------|
| `vacuum_fluctuation_optics` | ANU | Measures quantum vacuum fluctuations via beam-split light intensity |
| `quantum_photonics_IDQ` | LfD | Uses ID Quantique hardware (quantum photonic entropy source) |
| `quantum_photonics_IDQ_seeded` | ANU fallback | Mersenne Twister seeded with quantum photonic entropy |
| `sha3_extracted_quantum` | CURBy | Quantum entropy post-processed with SHA3-256 block hashing |
| `yarrow_stick` | I Ching | Traditional divination applied to quantum entropy |

### Derived Block

Contains derived structures like I Ching hexagrams.

```json
"derived": {
  "iching": {
    "technique": "yarrow_stick",
    "derived_from": "lfd[bytes 12..17]",
    "lines": [7, 8, 8, 6, 7, 8],
    "original_hexagram": 4,
    "original_hexagram_bin": "010010",
    "original_hexagram_bin2dec": 18,
    "resulting_hexagram": 18,
    "resulting_hexagram_bin": "110010",
    "resulting_hexagram_bin2dec": 50,
    "has_changing_lines": true,
    "changing_line_positions": [4]
  }
}
```

**Fields:**
- `technique`: Divination method (yarrow_stick)
- `derived_from`: Source data reference
- `lines`: Six line values (6=Old Yin, 7=Young Yang, 8=Young Yin, 9=Old Yang)
- `original_hexagram`: Hexagram number (1-64) before transforming changing lines
- `original_hexagram_bin`: Binary representation (bottom to top, Yang=1, Yin=0)
- `original_hexagram_bin2dec`: Decimal value of the binary representation (0-63)
- `resulting_hexagram`: Hexagram number after transforming changing lines
- `resulting_hexagram_bin`: Binary representation of resulting hexagram
- `resulting_hexagram_bin2dec`: Decimal value of the resulting binary representation (0-63)
- `has_changing_lines`: Whether any lines are changing (6 or 9)
- `changing_line_positions`: Array of changing line positions (1-6)

### Metadata Block

Response metadata and quality checks.

```json
"metadata": {
  "description": "Combined quantum randomness with I Ching derivation",
  "checks": {
    "byte_len_total": 74,
    "monobit_ratio": 0.5108695652173914
  }
}
```

**Fields:**
- `description`: Human-readable description
- `checks.byte_len_total`: Total bytes across all sources
- `checks.monobit_ratio`: Ratio of 1-bits to total bits (quick sanity check, should be ~0.5)

## Example Response

Complete example with concrete values:

```json
{
  "version": "1.0",
  "request": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-10-20T12:34:56.789Z",
    "success": true,
    "latency_ms": 523,
    "errors": []
  },
  "sources": [
    {
      "id": "lfd",
      "name": "LfD Laboratorium QRNG",
      "endpoint": "https://lfdr.de/qrng_api/qrng?length=64&format=HEX",
      "method": "https-get",
      "technique": "quantum_photonics_IDQ",
      "format_in": "hex",
      "encoding": "hex",
      "unit_bits": 8,
      "count": 64,
      "data": {
        "hex": "e668c6cca08a8c64e6442e8048a26a0822606ee20c84a2446c2a04268642e6cca8a0a0c0848e268008e60848466660a444468ca44800ea2a4ca84648caac0ce0",
        "uint8": [230, 104, 198, 204, ...],
        "bytes_b64": "5mjGzKCKjGTmRC6ASKJqCCJgbuIMhKJEbCoEJoZC5syo..."
      },
      "transform": ["decode:hex"],
      "sha256_hex": "3f8b5c2d1a9e7f6b4c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b",
      "fallback_used": false
    },
    {
      "id": "anu",
      "name": "ANU Quantum Random Numbers",
      "endpoint": "https://qrng.anu.edu.au/API/jsonI.php?length=6&type=uint16",
      "method": "https-get",
      "technique": "vacuum_fluctuation_optics",
      "format_in": "uint16",
      "encoding": "none",
      "unit_bits": 16,
      "count": 6,
      "data": {
        "uint16": [52766, 44842, 60913, 55109, 51858, 10022],
        "bytes_b64": "zgZu6u7R13VTnpJg"
      },
      "transform": ["none"],
      "sha256_hex": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
      "fallback_used": false
    },
    {
      "id": "curby_local",
      "name": "CURBy Local Quantum Data",
      "endpoint": "file:///home/jw/KNOTS/subnets/rng/CURBy/random_packed_u32be.csv",
      "method": "file",
      "technique": "sha3_extracted_quantum",
      "format_in": "uint32",
      "encoding": "none",
      "unit_bits": 32,
      "count": 1,
      "data": {
        "uint32": [528126889],
        "bytes_b64": "H3uTqQ=="
      },
      "transform": ["packing:1->0,2->1(msb)", "extractor:sha3-256-block"],
      "sha256_hex": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
      "fallback_used": false
    }
  ],
  "derived": {
      "iching": {
        "technique": "yarrow_stick",
        "derived_from": "lfd[bytes 12..17]",
        "lines": [7, 8, 8, 6, 7, 8],
        "original_hexagram": 4,
        "original_hexagram_bin": "010010",
        "original_hexagram_bin2dec": 18,
        "resulting_hexagram": 18,
        "resulting_hexagram_bin": "110010",
        "resulting_hexagram_bin2dec": 50,
        "has_changing_lines": true,
        "changing_line_positions": [4]
      }
  },
  "metadata": {
    "description": "Combined quantum randomness with I Ching derivation",
    "checks": {
      "byte_len_total": 74,
      "monobit_ratio": 0.5108695652173914
    }
  }
}
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest test_unified.py -v

# Run with coverage
pytest test_unified.py --cov=. --cov-report=html

# Run specific test class
pytest test_unified.py::TestIChingCasting -v
```

## Backward Compatibility

Convert legacy format to unified schema:

```python
from backward_compat import legacy_to_unified

legacy_data = {
    "sources": {
        "source1_anu_qrng": { ... },
        "source2_lfd_qrng": { ... },
        # ...
    }
}

unified = legacy_to_unified(legacy_data)
print(unified.model_dump_json(indent=2))
```

## Architecture

### Components

1. **models.py**: Pydantic models and JSON Schema
2. **fetchers.py**: Source fetching with retry logic
3. **iching_unified.py**: I Ching hexagram casting
4. **assembler.py**: Response builder and orchestrator
5. **app.py**: FastAPI application
6. **rng_unified.py**: CLI tool
7. **backward_compat.py**: Legacy format translator
8. **test_unified.py**: Test suite

### Data Flow

```
CLI/API Request
    ↓
Assembler
    ↓
├─→ Fetch LfD (Source 2) ─────────────┐
│                                     │
├─→ Fetch ANU (Source 1)              │
│   ↓ (if fails)                      │
│   └─→ Fallback with LfD bytes ←────┘
│                                     
├─→ Fetch CURBy (Source 3)            
│   (seeded with ANU[0])              
│                                     
└─→ Derive I Ching ←──────────────────┘
    (using LfD[12..17])
    ↓
Unified Response
```

## Guarantees

1. **Deterministic checksums**: SHA-256 of raw bytes after all transforms
2. **Versioned schema**: Breaking changes increment version number
3. **Request tracking**: Every request has unique UUID and timestamp
4. **Error transparency**: All errors logged in `request.errors`
5. **Provenance**: Full transformation history in `transform` array
6. **Type safety**: Pydantic validation catches invalid data
7. **Idempotency**: Same seed produces same CURBy selection

## API Rate Limits

Be aware of upstream rate limits:

- **ANU QRNG**: ~1 request per second
- **LfD QRNG**: Check their current limits

The fallback mechanism ensures graceful degradation if ANU is unavailable.

## Development

Format code:
```bash
black *.py
ruff check *.py
```

Type checking:
```bash
mypy *.py --strict
```

## License

[Specify your license here]

## Contact

[Your contact information]

# rngsources
