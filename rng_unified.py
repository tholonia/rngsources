#!/usr/bin/env python3
"""
CLI tool for unified quantum RNG API.

This tool fetches random data from multiple quantum sources and provides
optional derivations including I Ching hexagrams and Global Consciousness Project data.

DATA SOURCES:
=============

1. ANU Quantum Random Number Generator (QRNG)
   Organization: Australian National University (ANU)
   URL: https://qrng.anu.edu.au/
   
   Description:
   The ANU QRNG generates true random numbers in real-time by measuring quantum
   fluctuations of the vacuum. The quantum random number generator is based on the
   quantum optical process of measuring photons (light particles) in a beam of light.
   
   How it works:
   - Uses vacuum state fluctuations measured via homodyne detection
   - Measures the quantum fluctuations of the electromagnetic field vacuum state
   - These fluctuations are fundamentally random due to Heisenberg's uncertainty principle
   - The generator produces uint16 values (0-65535)
   
   The School of Physics at the ANU has been a leader in quantum optics research
   for over 30 years, and this service provides quantum randomness to researchers
   and the public worldwide.

2. LfD Laboratorium für Datenverarbeitung QRNG
   Organization: Laboratorium für Datenverarbeitung (Laboratory for Data Processing)
   URL: https://lfdr.de/qrng_api/
   
   Description:
   LfD provides quantum random numbers generated using quantum photonic technology
   from IDQ (ID Quantique), a Swiss company specializing in quantum cryptography
   and quantum random number generation.
   
   How it works:
   - Uses IDQ's Quantis QRNG technology
   - Based on the quantum process of photon detection
   - Measures the arrival time of single photons at a beam splitter
   - The path taken by each photon is fundamentally random (quantum superposition)
   - Outputs random bytes in hexadecimal format
   
   IDQ's technology is used in commercial cryptographic systems and provides
   certified random numbers meeting stringent security requirements.

3. CURBy Local Quantum Data
   Organization: Local data file (random_packed_u32be.csv)
   
   Description:
   CURBy (Cosmic Ultra-high-energy Radiation Background) data derived from
   quantum measurements and processed through cryptographic extractors.
   
   How it works:
   - Data is pre-generated and stored locally in CSV format
   - Uses SHA-3 (Secure Hash Algorithm 3) extraction on quantum source data
   - Packing algorithm: 1→0, 2→1 (MSB - Most Significant Bit first)
   - Extractor: SHA3-256-block processing
   - Seeds from ANU QRNG determine which pre-computed value to use
   - Provides uint32 or uint8 values depending on configuration
   
   The SHA-3 extractor ensures uniform distribution and removes any bias
   from the original quantum source, providing cryptographically secure
   random numbers.

4. Global Consciousness Project (GCP) Egg Data (Optional: --egg flag)
   Organization: Global Consciousness Project / Institute of Noetic Sciences
   URL: https://global-mind.org/realtime/
   
   Description:
   The Global Consciousness Project is an international collaboration studying
   whether human consciousness can be detected by physical systems. The project
   maintains a network of quantum Random Event Generators (REGs), nicknamed "Eggs,"
   distributed around the world.
   
   How it works:
   - Network of ~50-70 quantum random event generators worldwide
   - Each "Egg" continuously generates random bits from quantum processes
   - Data is analyzed for correlations and deviations from randomness
   - Statistical measures include:
     * persec: Raw bits per second from each egg
     * persecz: Z-score (standard deviations from expected randomness)
     * perseczcs: Cumulative Z-score sum
     * Stouffer Z: Combined statistic across all eggs
     * CSZ²-1: Cumulative Stouffer Z squared minus one
   
   The project hypothesizes that large-scale events affecting human consciousness
   may create detectable patterns in the network's data. The data provides unique
   time-stamped quantum randomness with global correlation analysis.
   
   Research founded by Princeton Engineering Anomalies Research (PEAR) lab and
   continues under the Institute of Noetic Sciences and independent researchers.

5. I Ching Hexagram Derivation (Default: enabled, disable with --no-iching)
   Tradition: Ancient Chinese divination system (易經)
   
   Description:
   The I Ching (Book of Changes) is an ancient Chinese divination text dating
   back over 3,000 years. It consists of 64 hexagrams, each made of six lines
   that are either broken (yin) or unbroken (yang).
   
   How it works in this implementation:
   - Uses quantum random bytes from LfD QRNG as source
   - Simulates traditional yarrow stick method
   - Derives 6 lines, each with value 6, 7, 8, or 9
     * 6 = old yin (changing to yang)
     * 7 = young yang (stable)
     * 8 = young yin (stable)
     * 9 = old yang (changing to yin)
   - Produces original hexagram and resulting hexagram (after changes)
   - Each hexagram (1-64) has traditional interpretations for divination
   
   Traditional method uses 50 yarrow stalks in an elaborate ritual. This
   implementation uses quantum randomness to simulate the traditional
   probabilities of the yarrow stick method, maintaining the proper
   distribution: 6 (1/16), 7 (5/16), 8 (7/16), 9 (3/16).

USAGE:
======
    python rng_unified.py --anu-len 6 --lfd-bytes 64 --curby u32
    python rng_unified.py --pretty
    python rng_unified.py --no-iching
    python rng_unified.py --egg --pretty
    
OUTPUT FORMAT:
==============
    JSON structure containing:
    - request: metadata (ID, timestamp, success status, latency)
    - sources: array of quantum data sources with their raw data
    - derived: optional I Ching and GCP egg data
    - metadata: quality checks (byte count, monobit ratio)
"""

import argparse
import json
import sys

from assembler import build_unified_response


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Quantum RNG - Fetch from multiple quantum sources"
    )
    
    parser.add_argument(
        "--anu-len",
        type=int,
        default=6,
        help="Number of uint16 values from ANU QRNG (default: 6)"
    )
    
    parser.add_argument(
        "--lfd-bytes",
        type=int,
        default=64,
        help="Number of bytes from LfD QRNG (default: 64)"
    )
    
    parser.add_argument(
        "--curby",
        "--curby-kind",
        dest="curby_kind",
        choices=["u8", "u32"],
        default="u32",
        help="CURBy data type (default: u32)"
    )
    
    parser.add_argument(
        "--curby-path",
        default="random_packed_u32be.csv",
        help="Path to CURBy CSV file (default: random_packed_u32be.csv)"
    )
    
    parser.add_argument(
        "--curby-count",
        type=int,
        default=1,
        help="Number of CURBy values (default: 1)"
    )
    
    parser.add_argument(
        "--no-iching",
        action="store_true",
        help="Disable I Ching derivation"
    )
    
    parser.add_argument(
        "--egg",
        action="store_true",
        help="Include Global Consciousness Project egg data"
    )
    
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file (default: stdout)"
    )
    
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Generate JSON Schema and exit"
    )
    
    args = parser.parse_args()
    
    # Handle schema generation
    if args.schema:
        from models import generate_schema_file
        output_path = args.output or "schema_unified.json"
        generate_schema_file(output_path)
        return 0
    
    # Build unified response
    try:
        response = build_unified_response(
            anu_len=args.anu_len,
            lfd_bytes=args.lfd_bytes,
            curby_kind=args.curby_kind,
            curby_path=args.curby_path,
            curby_count=args.curby_count,
            include_iching=not args.no_iching,
            include_egg=args.egg
        )
        
        # Convert to JSON
        if args.pretty:
            json_output = response.model_dump_json(indent=2)
        else:
            json_output = response.model_dump_json()
        
        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(json_output)
        
        # Exit with appropriate code
        return 0 if response.request.success else 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

