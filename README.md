# Unified Quantum RNG API

A unified, self-describing API for multi-source quantum random number generation with strict schema validation, provenance tracking, and I Ching hexagram derivation.

## Features

- **Multi-source quantum randomness**: ANU QRNG, LfD QRNG, CURBy local data, Global Consciousness Project (GCP) Egg network
- **Unified schema**: Versioned, self-describing format with full metadata
- **Integrity checks**: SHA-256 checksums for all data sources
- **I Ching derivation**: Traditional yarrow stick method applied to quantum entropy
- **GCP Egg data**: Real-time quantum randomness from global network of Random Event Generators
- **Automatic fallback**: Quantum-seeded PRNG if primary sources fail
- **Full provenance**: Transformation history and technique descriptions
- **Type safety**: Pydantic models with strict validation
- **Backward compatibility**: Translator for legacy formats

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

**Optional: For GCP Egg Data Integration**

```bash
pip install playwright
playwright install chromium
```

This is only required if you want to use the `--egg` flag to fetch Global Consciousness Project data.

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
| `include_egg` | `false` | `true`, `false` | Include Global Consciousness Project egg data |

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

# Include GCP Egg data
python rng_unified.py --egg --pretty

# Generate JSON Schema
python rng_unified.py --schema

# Without I Ching derivation
python rng_unified.py --no-iching

# Save to file
python rng_unified.py --pretty --output random_data.json

# All features enabled
python rng_unified.py --egg --pretty --output full_data.json
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
- `include_egg` (bool, default=false): Include Global Consciousness Project egg data

**Examples:**
```bash
# Standard request
curl "http://localhost:8000/random/unified?anu_len=6&lfd_bytes=64&curby_kind=u32&include_iching=true" | jq

# Include GCP Egg data
curl "http://localhost:8000/random/unified?include_egg=true" | jq
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
| `distributed_quantum_network` | GCP Eggs | Global network of quantum Random Event Generators |
| `yarrow_stick` | I Ching | Traditional divination applied to quantum entropy |

### Derived Block

Contains derived structures like I Ching hexagrams and GCP egg data.

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
  },
  "egg": {
    "source": "global-mind.org",
    "persec": {
      "1761338700": [96, 107, 100, 92, 110, 101, 103, 98, 95, 111],
      "1761338701": [101, 94, 102, 95, 104, 98, 107, 100, 103, 99]
    },
    "persecz": {
      "1761338700": [-0.566, 0.990, 0.0, -1.131, 1.414, 0.141, 0.424, -0.283, -0.707, 1.556],
      "1761338701": [0.141, -0.849, 0.283, -0.707, 0.566, -0.283, 0.990, 0.0, 0.424, -0.141]
    },
    "perseczcs": {
      "1761338700": [-0.566, -0.142, -0.142, -1.273, 0.141, 0.282, 0.706, 0.423, -0.284, 1.272],
      "1761338701": [0.141, -0.708, -0.425, -1.132, -0.566, -0.849, 0.141, 0.141, 0.565, 0.424]
    },
    "stouffer": {
      "1761338760": {"StoufferZ": -1.431, "CSZ2-1": 1.048},
      "1761338761": {"StoufferZ": 0.268, "CSZ2-1": 0.120}
    }
  }
}
```

**I Ching Fields:**
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

**GCP Egg Fields:**
- `source`: Data source URL (global-mind.org)
- `persec`: Per-second raw bit counts from each egg (dict keyed by Unix timestamp, values are lists of 10 integers)
- `persecz`: Per-second Z-scores showing deviations from expected randomness (dict keyed by Unix timestamp, values are lists of 10 floats)
- `perseczcs`: Cumulative sum of Z-scores over time (dict keyed by Unix timestamp, values are lists of 10 floats)
- `stouffer`: Combined network statistics (dict keyed by Unix timestamp)
  - `StoufferZ`: Meta-analysis statistic combining all eggs
  - `CSZ2-1`: Cumulative Stouffer Z squared minus one

### Metadata Block

Response metadata and quality checks.

```json
"metadata": {
  "description": "Combined quantum randomness with I Ching derivation and Global Consciousness Project egg data (https://global-mind.org/realtime/)",
  "checks": {
    "byte_len_total": 74,
    "monobit_ratio": 0.5108695652173914
  }
}
```

**Fields:**
- `description`: Human-readable description (includes GCP info when egg data is included)
- `checks.byte_len_total`: Total bytes across all sources
- `checks.monobit_ratio`: Ratio of 1-bits to total bits (quick sanity check, should be ~0.5)

## Global Consciousness Project (GCP) Integration

### About GCP

The Global Consciousness Project is an international collaboration studying whether human consciousness can be detected by physical systems. Started in 1998, the project maintains a worldwide network of quantum Random Event Generators (REGs), nicknamed "Eggs," that continuously generate random data.

**Website:** https://global-mind.org/realtime/

### How It Works

- **Network:** ~50-70 quantum random event generators distributed globally
- **Continuous Operation:** 24/7 data collection since 1998
- **Update Frequency:** Real-time data with minute-by-minute updates
- **Data Source:** Each Egg generates ~200 random bits per second from quantum processes

### Data Structure

The API fetches four types of statistical data:

1. **persec** (Per-Second Raw Data)
   - Raw bit counts from each Egg per second
   - Expected value: ~100 (from 200 trials expecting 50% ones)
   - Format: Dict keyed by Unix timestamp, values are lists of integers (one per Egg)
   - Example: `{1761338700: [96, 107, 100, 92, 110, 101, 103, 98, 95, 111]}`

2. **persecz** (Per-Second Z-Scores)
   - Standard deviations from expected randomness
   - Shows how far each second deviates from pure randomness
   - Typically ranges from -3 to +3
   - Positive = more ones; Negative = fewer ones
   - Format: Dict keyed by Unix timestamp, values are lists of floats

3. **perseczcs** (Cumulative Z-Score Sum)
   - Running sum of Z-scores over time
   - Shows long-term trends and persistent deviations
   - Random walk pattern expected for pure randomness
   - Format: Dict keyed by Unix timestamp, values are lists of floats

4. **stouffer** (Network-Wide Statistics)
   - **StoufferZ**: Meta-analysis combining all Eggs into single measure
   - **CSZ²-1**: Cumulative Stouffer Z squared minus one
   - Shows whether the entire network is deviating from randomness
   - Format: Dict keyed by Unix timestamp with {StoufferZ, CSZ2-1} values

### Research Applications

- Consciousness studies and global coherence research
- Time-stamped quantum randomness for correlational studies
- Distributed quantum system analysis
- High-quality entropy source with global provenance
- Long-term quantum randomness data (20+ years of history)

### Technical Requirements

To use GCP egg data integration:

```bash
# Install Playwright for web scraping
pip install playwright
playwright install chromium

# Use the --egg flag
python rng_unified.py --egg --pretty
```

The integration automatically:
- Downloads latest data from global-mind.org
- Extracts CSV data from ZIP archive
- Processes specific line ranges (30-91, 96-155, 160-219, 223-283)
- Returns structured data in unified schema

### Data Lineage

- **Lines 30-91**: Per-second raw trial data (persec)
- **Lines 96-155**: Per-second Z-scores (persecz)
- **Lines 160-219**: Cumulative Z-scores (perseczcs)
- **Lines 223-283**: Stouffer combined statistics (stouffer)

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
9. **../egg/getdata.py**: GCP egg data fetcher and processor

### Data Flow

```
CLI/API Request (with optional --egg flag)
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
├─→ Derive I Ching ←──────────────────┘
│   (using LfD[12..17])
│
└─→ Fetch GCP Egg Data (optional)
    ├─→ Download from global-mind.org
    ├─→ Extract ZIP archive
    ├─→ Process CSV (lines 30-283)
    └─→ Structure: persec, persecz, perseczcs, stouffer
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

## Additional Documentation

For comprehensive information about all quantum data sources, including detailed descriptions of how each source works, the organizations behind them, and their scientific foundations, see:

- **[SOURCES.md](SOURCES.md)**: Detailed documentation of all quantum RNG sources (ANU, LfD, CURBy, GCP Eggs, I Ching)
- **[QUICKSTART.md](QUICKSTART.md)**: Quick start guide and examples
- **[INTEGRATION_SUMMARY.md](../INTEGRATION_SUMMARY.md)**: Project integration summary

## License

[Specify your license here]

## Contact

[Your contact information]
