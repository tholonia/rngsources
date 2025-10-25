#!/bin/bash

python extract_random_bytes.py \
  --input Data.raw --raw \
  --source packed \
  --hex-out random_packed.hex \
  --u32csv-out random_packed_u32be.csv --u32-endian big \
  --json-out random_packed.json --json-format hex --json-bytes-per-value 64
