# Quick Start Guide - Unified Quantum RNG API

## 1. Install Dependencies

```bash
cd /home/jw/KNOTS/subnets/rng/CURBy
pip install -r requirements.txt
```

## 2. Verify Installation

```bash
# Run examples to verify everything works
python example_usage.py
```

Expected output:
```
✓ I Ching hexagram casting works
✓ Yarrow stick probabilities correct
✓ SHA-256 checksums computed
✓ Unified response structure valid
✓ Backward compatibility working
```

## 3. Generate Schema

```bash
python models.py
# Creates: schema_unified.json
```

## 4. Use the CLI

### Basic usage:
```bash
python rng_unified.py --pretty
```

### With custom parameters:
```bash
python rng_unified.py \
  --anu-len 10 \
  --lfd-bytes 128 \
  --curby u32 \
  --curby-path random_packed_u32be.csv \
  --pretty
```

### Save to file:
```bash
python rng_unified.py --pretty --output mydata.json
```

### Without I Ching:
```bash
python rng_unified.py --no-iching --pretty
```

## 5. Start the API Server

```bash
# Development mode with auto-reload
uvicorn app:app --reload

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

## 6. Test the API

### Get unified random data:
```bash
curl "http://localhost:8000/random/unified?anu_len=6&lfd_bytes=64" | jq
```

### Get the JSON Schema:
```bash
curl "http://localhost:8000/schema" | jq
```

### Health check:
```bash
curl "http://localhost:8000/health"
```

### API documentation:
Open browser to: `http://localhost:8000/docs` (Swagger UI)

## 7. Run Tests

```bash
pytest test_unified.py -v
```

## 8. Use in Python Code

```python
from assembler import build_unified_response

# Fetch from all sources
response = build_unified_response(
    anu_len=6,
    lfd_bytes=64,
    curby_kind="u32",
    curby_path="random_packed_u32be.csv",
    include_iching=True
)

# Access the data
print(f"Request ID: {response.request.request_id}")
print(f"Success: {response.request.success}")
print(f"Sources: {len(response.sources)}")

# Get ANU data
anu_source = next(s for s in response.sources if s.id == "anu")
print(f"ANU values: {anu_source.data.uint16}")

# Get I Ching hexagram
if response.derived.iching:
    print(f"Hexagram: #{response.derived.iching.original_hexagram}")
    print(f"Lines: {response.derived.iching.lines}")

# Export as JSON
json_output = response.model_dump_json(indent=2)
with open("output.json", "w") as f:
    f.write(json_output)
```

## 9. Convert Legacy Format

```python
from backward_compat import legacy_to_unified

legacy_data = {
    "sources": {
        "source1_anu_qrng": {
            "type": "uint16",
            "data": [1, 2, 3],
            # ...
        }
    }
}

unified = legacy_to_unified(legacy_data)
print(unified.model_dump_json(indent=2))
```

## Common Use Cases

### 1. Generate random numbers for testing:
```bash
python rng_unified.py --anu-len 100 --output test_data.json
```

### 2. Get I Ching reading:
```bash
python rng_unified.py --pretty | jq '.derived.iching'
```

### 3. Verify data integrity:
```bash
python rng_unified.py | jq '.sources[].sha256_hex'
```

### 4. Check randomness quality:
```bash
python rng_unified.py | jq '.metadata.checks.monobit_ratio'
```

### 5. Get only quantum sources (no I Ching):
```bash
python rng_unified.py --no-iching --pretty
```

## Troubleshooting

### ANU QRNG rate limit exceeded:
- Error: "500 Server Error"
- Solution: Automatic fallback to quantum-seeded PRNG
- Check: `sources[].fallback_used` field

### CSV file not found:
- Error: "CSV file not found: ..."
- Solution: Specify correct path with `--curby-path`

### Network timeout:
- Error: "Failed to fetch from ..."
- Solution: Check internet connection, retry

### Import errors:
- Error: "ModuleNotFoundError: ..."
- Solution: `pip install -r requirements.txt`

## File Locations

- **Models**: `models.py`
- **Fetchers**: `fetchers.py`
- **I Ching**: `iching_unified.py`
- **Assembler**: `assembler.py`
- **API**: `app.py`
- **CLI**: `rng_unified.py`
- **Tests**: `test_unified.py`
- **Examples**: `example_usage.py`
- **Schema**: `schema_unified.json`
- **Docs**: `README.md`

## Next Steps

1. Read `README.md` for detailed documentation
2. Review `example_usage.py` for code examples
3. Check `IMPLEMENTATION_SUMMARY.md` for architecture details
4. Run `pytest test_unified.py -v` to verify installation
5. Start building your application!

## Support

For issues or questions, refer to:
- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `example_usage.py` - Working examples
- `test_unified.py` - Test cases

