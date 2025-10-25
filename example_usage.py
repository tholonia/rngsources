#!/usr/bin/env python3
"""
Example usage of the unified quantum RNG API.

This demonstrates the core functionality without requiring external services.
"""

import json
from models import UnifiedResponse, RequestInfo, Source, SourceData, Metadata, MetadataChecks, Derived, IChingDerived
from iching_unified import cast_iching_hexagram, cast_yarrow_line, lines_to_binary, binary_to_string
from fetchers import compute_sha256, compute_monobit_ratio
from backward_compat import legacy_to_unified
import uuid
from datetime import datetime, timezone


def example_iching():
    """Example: Cast an I Ching hexagram from quantum bytes."""
    print("=== I Ching Hexagram Casting ===\n")
    
    # Simulate quantum bytes
    quantum_bytes = bytes([100, 150, 200, 50, 75, 225])
    
    result = cast_iching_hexagram(quantum_bytes, "example[bytes 0..5]")
    
    print(f"Lines (bottom to top): {result['lines']}")
    print(f"Original hexagram: #{result['original_hexagram']} (binary: {result['original_hexagram_bin']})")
    print(f"Resulting hexagram: #{result['resulting_hexagram']} (binary: {result['resulting_hexagram_bin']})")
    print(f"Has changing lines: {result['has_changing_lines']}")
    if result['changing_line_positions']:
        print(f"Changing line positions: {result['changing_line_positions']}")
    print()


def example_unified_response():
    """Example: Build a minimal unified response."""
    print("=== Unified Response Structure ===\n")
    
    # Create a minimal response
    response = UnifiedResponse(
        version="1.0",
        request=RequestInfo(
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            success=True,
            latency_ms=100,
            errors=[]
        ),
        sources=[
            Source(
                id="example",
                name="Example Source",
                endpoint="https://example.com",
                method="https-get",
                technique="vacuum_fluctuation_optics",
                format_in="uint16",
                encoding="none",
                unit_bits=16,
                count=3,
                data=SourceData(uint16=[100, 200, 300]),
                transform=["none"],
                sha256_hex=compute_sha256(b'\x00d\x00\xc8\x01,'),
                fallback_used=False
            )
        ],
        metadata=Metadata(
            description="Example unified response",
            checks=MetadataChecks(
                byte_len_total=6,
                monobit_ratio=0.5
            )
        )
    )
    
    print(json.dumps(json.loads(response.model_dump_json()), indent=2))
    print()


def example_backward_compat():
    """Example: Convert legacy format to unified."""
    print("=== Backward Compatibility ===\n")
    
    legacy = {
        "sources": {
            "source1_anu_qrng": {
                "type": "uint16",
                "length": 2,
                "data": [12345, 54321],
                "url": "https://example.com/anu",
                "generation_technique": "vacuum_fluctuation_optics",
                "fallback_used": False
            },
            "source4_iching": {
                "lines": [7, 8, 8, 7, 7, 8],
                "original_hexagram": 10,
                "original_hexagram_binary": 19,
                "resulting_hexagram": 10,
                "resulting_hexagram_binary": 19,
                "has_changing_lines": False,
                "changing_line_positions": []
            }
        }
    }
    
    unified = legacy_to_unified(legacy)
    
    print("Converted legacy format to unified schema:")
    print(f"  - Sources: {len(unified.sources)}")
    print(f"  - Request ID: {unified.request.request_id}")
    print(f"  - I Ching included: {unified.derived.iching is not None}")
    if unified.derived.iching:
        print(f"  - I Ching hexagram: #{unified.derived.iching.original_hexagram}")
    print()


def example_checksums():
    """Example: SHA-256 checksums and monobit ratio."""
    print("=== Integrity Checks ===\n")
    
    # Test data
    data1 = b"Hello, Quantum World!"
    data2 = bytes([0xFF] * 10)  # All ones
    data3 = bytes([0x00] * 10)  # All zeros
    data4 = bytes([0xAA] * 10)  # Alternating bits
    
    print(f"Data: {data1.decode()}")
    print(f"SHA-256: {compute_sha256(data1)}")
    print(f"Monobit ratio: {compute_monobit_ratio(data1):.4f}")
    print()
    
    print(f"Data: All 1's (10 bytes)")
    print(f"Monobit ratio: {compute_monobit_ratio(data2):.4f} (expected: 1.0)")
    print()
    
    print(f"Data: All 0's (10 bytes)")
    print(f"Monobit ratio: {compute_monobit_ratio(data3):.4f} (expected: 0.0)")
    print()
    
    print(f"Data: Alternating bits (10 bytes)")
    print(f"Monobit ratio: {compute_monobit_ratio(data4):.4f} (expected: 0.5)")
    print()


def example_yarrow_probabilities():
    """Example: Yarrow stick line casting probabilities."""
    print("=== Yarrow Stick Probabilities ===\n")
    
    # Sample 1000 casts to verify distribution
    from collections import Counter
    
    sample_bytes = bytes(range(256))
    lines = [cast_yarrow_line(b) for b in sample_bytes]
    counts = Counter(lines)
    
    print("Distribution from 256 samples:")
    print(f"  6 (Old Yin):   {counts[6]:3d} ({counts[6]/256:.1%}) - expected: 6.25%")
    print(f"  7 (Young Yang): {counts[7]:3d} ({counts[7]/256:.1%}) - expected: 31.25%")
    print(f"  8 (Young Yin):  {counts[8]:3d} ({counts[8]/256:.1%}) - expected: 43.75%")
    print(f"  9 (Old Yang):   {counts[9]:3d} ({counts[9]/256:.1%}) - expected: 18.75%")
    print()


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("  Unified Quantum RNG API - Examples")
    print("="*60 + "\n")
    
    example_iching()
    example_yarrow_probabilities()
    example_checksums()
    example_unified_response()
    example_backward_compat()
    
    print("="*60)
    print("All examples completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

