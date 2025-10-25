#!/bin/bash

python extract_random_bytes.py \
  --input Data \
  --json-out random_u32.json \
  --json-format u32 \
  --u32-endian little
