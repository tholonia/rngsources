"""
Unit tests for unified quantum RNG API.
"""

import pytest
import json
from models import UnifiedResponse, Source, SourceData
from iching_unified import (
    cast_yarrow_line, lines_to_binary, binary_to_string,
    lines_to_hexagram_number, transform_changing_lines, cast_iching_hexagram
)
from fetchers import compute_sha256, compute_monobit_ratio
from backward_compat import legacy_to_unified


class TestModels:
    """Test Pydantic models and validation."""
    
    def test_source_data_validation(self):
        """Test SourceData can have multiple formats."""
        data = SourceData(
            uint16=[1, 2, 3],
            hex="010203",
            bytes_b64="AQID"
        )
        assert data.uint16 == [1, 2, 3]
        assert data.hex == "010203"
    
    def test_sha256_validation(self):
        """Test SHA-256 must be 64 hex chars."""
        with pytest.raises(ValueError):
            Source(
                id="test",
                name="Test",
                endpoint="http://test",
                method="https-get",
                technique="vacuum_fluctuation_optics",
                format_in="uint8",
                encoding="none",
                unit_bits=8,
                count=1,
                data=SourceData(uint8=[1]),
                sha256_hex="invalid"  # Too short
            )
    
    def test_iching_lines_validation(self):
        """Test I Ching lines must be 6, 7, 8, or 9."""
        from models import IChingDerived
        
        with pytest.raises(ValueError):
            IChingDerived(
                technique="yarrow_stick",
                derived_from="test",
                lines=[1, 2, 3, 4, 5, 6],  # Invalid values
                original_hexagram=1,
                original_hexagram_bin="000000",
                resulting_hexagram=1,
                resulting_hexagram_bin="000000",
                has_changing_lines=False
            )


class TestIChingCasting:
    """Test I Ching hexagram casting logic."""
    
    def test_yarrow_line_probabilities(self):
        """Test yarrow stick probabilities are in correct ranges."""
        # Test boundaries
        assert cast_yarrow_line(0) == 6     # 0/256 < 1/16
        assert cast_yarrow_line(16) == 7    # 16/256 = 1/16
        assert cast_yarrow_line(96) == 8    # 96/256 = 6/16
        assert cast_yarrow_line(208) == 9   # 208/256 = 13/16
    
    def test_lines_to_binary(self):
        """Test converting lines to binary representation."""
        # All yin (8, 6)
        assert lines_to_binary([8, 8, 8, 8, 8, 8]) == 0b000000
        
        # All yang (7, 9)
        assert lines_to_binary([7, 7, 7, 7, 7, 7]) == 0b111111
        
        # Mixed
        assert lines_to_binary([7, 8, 7, 8, 7, 8]) == 0b010101
    
    def test_binary_to_string(self):
        """Test binary formatting to 6-char string."""
        assert binary_to_string(0) == "000000"
        assert binary_to_string(63) == "111111"
        assert binary_to_string(21) == "010101"
    
    def test_transform_changing_lines(self):
        """Test changing lines transform correctly."""
        lines = [6, 7, 8, 9, 7, 8]
        transformed = transform_changing_lines(lines)
        
        assert transformed[0] == 7  # 6 -> 7
        assert transformed[1] == 7  # 7 stays
        assert transformed[2] == 8  # 8 stays
        assert transformed[3] == 8  # 9 -> 8
    
    def test_cast_hexagram_structure(self):
        """Test hexagram casting returns correct structure."""
        random_bytes = bytes([100, 150, 200, 50, 75, 225])
        result = cast_iching_hexagram(random_bytes, "test_source")
        
        assert result["technique"] == "yarrow_stick"
        assert result["derived_from"] == "test_source"
        assert len(result["lines"]) == 6
        assert all(line in (6, 7, 8, 9) for line in result["lines"])
        assert 1 <= result["original_hexagram"] <= 64
        assert 1 <= result["resulting_hexagram"] <= 64
        assert len(result["original_hexagram_bin"]) == 6
        assert len(result["resulting_hexagram_bin"]) == 6
    
    def test_hexagram_no_changing_lines(self):
        """Test hexagram with no changing lines."""
        # Create bytes that will produce stable lines (7, 8 only)
        random_bytes = bytes([50, 50, 100, 100, 150, 150])
        result = cast_iching_hexagram(random_bytes)
        
        if not result["has_changing_lines"]:
            assert result["original_hexagram"] == result["resulting_hexagram"]
            assert result["original_hexagram_bin"] == result["resulting_hexagram_bin"]


class TestFetchers:
    """Test fetcher utility functions."""
    
    def test_compute_sha256(self):
        """Test SHA-256 computation."""
        data = b"Hello, World!"
        sha256 = compute_sha256(data)
        
        assert len(sha256) == 64
        assert all(c in "0123456789abcdef" for c in sha256)
        # Known hash for this string
        assert sha256 == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
    
    def test_compute_monobit_ratio(self):
        """Test monobit ratio calculation."""
        # All zeros
        assert compute_monobit_ratio(b'\x00\x00\x00\x00') == 0.0
        
        # All ones
        assert compute_monobit_ratio(b'\xff\xff\xff\xff') == 1.0
        
        # Half and half
        ratio = compute_monobit_ratio(b'\x00\xff\x00\xff')
        assert 0.4 < ratio < 0.6  # Should be close to 0.5


class TestBackwardCompat:
    """Test backward compatibility translator."""
    
    def test_legacy_conversion(self):
        """Test converting legacy format to unified."""
        legacy = {
            "sources": {
                "source1_anu_qrng": {
                    "type": "uint16",
                    "length": 3,
                    "data": [100, 200, 300],
                    "url": "https://test.example.com",
                    "generation_technique": "vacuum_fluctuation_optics",
                    "fallback_used": False
                },
                "source2_lfd_qrng": {
                    "type": "hex",
                    "length": 4,
                    "data": "deadbeef",
                    "url": "https://test.example.com",
                    "generation_technique": "quantum_photonics_IDQ"
                }
            }
        }
        
        unified = legacy_to_unified(legacy)
        
        assert unified.version == "1.0"
        assert len(unified.sources) == 2
        assert unified.sources[0].id == "anu"
        assert unified.sources[1].id == "lfd"
        assert unified.request.success is True
    
    def test_legacy_with_iching(self):
        """Test converting legacy format with I Ching data."""
        legacy = {
            "sources": {
                "source4_iching": {
                    "lines": [7, 8, 8, 6, 7, 8],
                    "original_hexagram": 4,
                    "original_hexagram_binary": 18,
                    "resulting_hexagram": 18,
                    "resulting_hexagram_binary": 50,
                    "has_changing_lines": True,
                    "changing_line_positions": [4]
                }
            }
        }
        
        unified = legacy_to_unified(legacy)
        
        assert unified.derived.iching is not None
        assert unified.derived.iching.technique == "yarrow_stick"
        assert len(unified.derived.iching.lines) == 6


class TestUnifiedResponse:
    """Test complete unified response."""
    
    def test_response_serialization(self):
        """Test response can be serialized to JSON."""
        from models import RequestInfo, Metadata, MetadataChecks
        
        response = UnifiedResponse(
            version="1.0",
            request=RequestInfo(
                request_id="test-123",
                timestamp="2025-01-01T00:00:00Z",
                success=True,
                latency_ms=100,
                errors=[]
            ),
            sources=[],
            metadata=Metadata(
                description="Test",
                checks=MetadataChecks(byte_len_total=0)
            )
        )
        
        json_str = response.model_dump_json()
        parsed = json.loads(json_str)
        
        assert parsed["version"] == "1.0"
        assert parsed["request"]["request_id"] == "test-123"
    
    def test_response_validation(self):
        """Test response validates correctly."""
        from models import RequestInfo, Metadata, MetadataChecks
        
        # Should not raise
        UnifiedResponse(
            version="1.0",
            request=RequestInfo(
                request_id="test",
                timestamp="2025-01-01T00:00:00Z",
                success=True,
                latency_ms=0,
                errors=[]
            ),
            metadata=Metadata(
                description="Test",
                checks=MetadataChecks(byte_len_total=0)
            )
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

