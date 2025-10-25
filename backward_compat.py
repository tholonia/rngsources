"""
Backward compatibility translator for legacy format.
"""

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel

from models import (
    UnifiedResponse, RequestInfo, Source, SourceData,
    Derived, IChingDerived, Metadata, MetadataChecks
)


class LegacyResponse(BaseModel):
    """Legacy response format (for API input validation)."""
    sources: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 checksum."""
    return hashlib.sha256(data).hexdigest()


def legacy_to_unified(legacy_json: Dict[str, Any]) -> UnifiedResponse:
    """
    Convert legacy format to unified schema.
    
    Legacy format example:
    {
      "sources": {
        "source1_anu_qrng": {
          "type": "uint16",
          "length": 6,
          "data": [52766, 44842, 60913, 55109, 51858, 10022],
          "url": "...",
          "generation_technique": "vacuum_fluctuation_optics",
          "technique_description": "...",
          "fallback_used": false
        },
        "source2_lfd_qrng": {
          "type": "hex",
          "length": 64,
          "data": "e668c6cc...",
          "url": "...",
          "generation_technique": "quantum_photonics_IDQ",
          "technique_description": "..."
        },
        "source3_local_csv": {
          "type": "uint32",
          "seed": 52766,
          "selected_index": 754533,
          "data": 528126889,
          "file": "random_packed_u32be.csv",
          "total_lines": 949405,
          "generation_technique": "sha3_extracted_quantum",
          "technique_description": "..."
        },
        "source4_iching": {
          "lines": [7, 8, 8, 6, 7, 8],
          "original_hexagram": 4,
          "original_hexagram_binary": 18,
          "resulting_hexagram": 18,
          "resulting_hexagram_binary": 50,
          "has_changing_lines": true,
          "changing_line_positions": [4],
          "random_source": "...",
          "generation_technique": "yarrow_stick",
          "technique_description": "..."
        }
      },
      "metadata": {...}
    }
    """
    sources_list = []
    legacy_sources = legacy_json.get("sources", {})
    
    all_bytes = bytearray()
    
    # Convert source1_anu_qrng
    if "source1_anu_qrng" in legacy_sources:
        s1 = legacy_sources["source1_anu_qrng"]
        uint16_data = s1.get("data", [])
        
        # Convert to bytes (big-endian)
        data_bytes = b''.join(v.to_bytes(2, byteorder='big') for v in uint16_data)
        all_bytes.extend(data_bytes)
        
        technique = s1.get("generation_technique", "vacuum_fluctuation_optics")
        fallback = s1.get("fallback_used", False)
        
        sources_list.append(Source(
            id="anu",
            name="ANU Quantum Random Numbers",
            endpoint=s1.get("url", "unknown"),
            method="https-get",
            technique=technique,
            format_in="uint16",
            encoding="none",
            unit_bits=16,
            count=len(uint16_data),
            data=SourceData(
                uint16=uint16_data,
                bytes_b64=base64.b64encode(data_bytes).decode()
            ),
            transform=["derive:lfd[0..11]"] if fallback else ["none"],
            sha256_hex=compute_sha256(data_bytes),
            fallback_used=fallback
        ))
    
    # Convert source2_lfd_qrng
    if "source2_lfd_qrng" in legacy_sources:
        s2 = legacy_sources["source2_lfd_qrng"]
        hex_data = s2.get("data", "")
        
        # Convert to bytes
        data_bytes = bytes.fromhex(hex_data)
        all_bytes.extend(data_bytes)
        
        sources_list.append(Source(
            id="lfd",
            name="LfD Laboratorium QRNG",
            endpoint=s2.get("url", "unknown"),
            method="https-get",
            technique=s2.get("generation_technique", "quantum_photonics_IDQ"),
            format_in="hex",
            encoding="hex",
            unit_bits=8,
            count=len(data_bytes),
            data=SourceData(
                hex=hex_data,
                uint8=list(data_bytes),
                bytes_b64=base64.b64encode(data_bytes).decode()
            ),
            transform=["decode:hex"],
            sha256_hex=compute_sha256(data_bytes),
            fallback_used=False
        ))
    
    # Convert source3_local_csv
    if "source3_local_csv" in legacy_sources:
        s3 = legacy_sources["source3_local_csv"]
        value = s3.get("data", 0)
        
        # Determine type
        if s3.get("type") == "uint32":
            data_bytes = value.to_bytes(4, byteorder='big')
            all_bytes.extend(data_bytes)
            
            sources_list.append(Source(
                id="curby_local",
                name="CURBy Local Quantum Data",
                endpoint=f"file://{s3.get('file', 'unknown')}",
                method="file",
                technique=s3.get("generation_technique", "sha3_extracted_quantum"),
                format_in="uint32",
                encoding="none",
                unit_bits=32,
                count=1,
                data=SourceData(
                    uint32=[value],
                    bytes_b64=base64.b64encode(data_bytes).decode()
                ),
                transform=["packing:1->0,2->1(msb)", "extractor:sha3-256-block"],
                sha256_hex=compute_sha256(data_bytes),
                fallback_used=False
            ))
    
    # Convert source4_iching
    derived = Derived()
    if "source4_iching" in legacy_sources:
        s4 = legacy_sources["source4_iching"]
        
        # Convert binary integers to binary strings
        orig_bin = s4.get("original_hexagram_binary", 0)
        result_bin = s4.get("resulting_hexagram_binary", 0)
        
        derived.iching = IChingDerived(
            technique="yarrow_stick",
            derived_from=s4.get("random_source", "unknown"),
            lines=s4.get("lines", []),
            original_hexagram=s4.get("original_hexagram", 1),
            original_hexagram_bin=format(orig_bin, '06b'),
            original_hexagram_bin2dec=orig_bin,
            resulting_hexagram=s4.get("resulting_hexagram", 1),
            resulting_hexagram_bin=format(result_bin, '06b'),
            resulting_hexagram_bin2dec=result_bin,
            has_changing_lines=s4.get("has_changing_lines", False),
            changing_line_positions=s4.get("changing_line_positions", [])
        )
    
    # Build request info
    request = RequestInfo(
        request_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        success=True,
        latency_ms=0,
        errors=[]
    )
    
    # Build metadata
    metadata = Metadata(
        description="Converted from legacy format",
        checks=MetadataChecks(
            byte_len_total=len(all_bytes),
            monobit_ratio=None
        )
    )
    
    return UnifiedResponse(
        version="1.0",
        request=request,
        sources=sources_list,
        derived=derived,
        metadata=metadata
    )

