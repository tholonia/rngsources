#!/bin/bash
python extract_random_bytes.py \
  --input Data \
  --hex-out random.hex \
  --hex-bytes-per-line 32 \
  --u32csv-out random_u32le.csv \
  --u32-endian little \
  --json-out random.json \
  --json-format bytes \
  --json-bytes-per-value 32
