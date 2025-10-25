"""
Pydantic models for the unified random number API schema.
"""

from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import json


class RequestInfo(BaseModel):
    """Request metadata and status."""
    request_id: str = Field(..., description="Unique UUID4 for this request")
    timestamp: str = Field(..., description="RFC3339 timestamp in UTC")
    success: bool = Field(..., description="Overall success status")
    latency_ms: int = Field(..., ge=0, description="Total request latency in milliseconds")
    errors: List[str] = Field(default_factory=list, description="Error messages if any")


class SourceData(BaseModel):
    """Data payload in multiple formats."""
    uint8: Optional[List[int]] = Field(None, description="Array of uint8 values (0-255)")
    uint16: Optional[List[int]] = Field(None, description="Array of uint16 values (0-65535)")
    uint32: Optional[List[int]] = Field(None, description="Array of uint32 values")
    hex: Optional[str] = Field(None, description="Hexadecimal string representation")
    bytes_b64: Optional[str] = Field(None, description="Base64 encoded raw bytes")


class Source(BaseModel):
    """Standardized source descriptor."""
    id: str = Field(..., description="Short identifier (anu|lfd|curby_local)")
    name: str = Field(..., description="Human-readable name")
    endpoint: str = Field(..., description="URL or file:// path")
    method: Literal["https-get", "file"] = Field(..., description="Access method")
    technique: Literal[
        "vacuum_fluctuation_optics",
        "quantum_photonics_IDQ",
        "quantum_photonics_IDQ_seeded",
        "sha3_extracted_quantum",
        "yarrow_stick"
    ] = Field(..., description="Quantum generation technique")
    format_in: Literal["uint8", "uint16", "uint32", "hex"] = Field(
        ..., description="Input format type"
    )
    encoding: Literal["none", "hex", "base64"] = Field(..., description="Encoding method")
    unit_bits: int = Field(..., description="Bits per unit")
    count: int = Field(..., ge=0, description="Number of elements or bytes")
    data: SourceData = Field(..., description="Data in multiple formats")
    transform: List[str] = Field(
        default_factory=lambda: ["none"],
        description="Ordered list of transformations applied"
    )
    sha256_hex: str = Field(..., min_length=64, max_length=64, description="SHA-256 checksum")
    fallback_used: bool = Field(default=False, description="Whether fallback was used")

    @field_validator("sha256_hex")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        """Ensure SHA-256 is valid hex."""
        if not all(c in "0123456789abcdef" for c in v.lower()):
            raise ValueError("sha256_hex must be valid hexadecimal")
        return v.lower()


class IChingDerived(BaseModel):
    """I Ching hexagram derivation."""
    technique: Literal["yarrow_stick"] = Field(
        default="yarrow_stick",
        description="Divination method"
    )
    derived_from: str = Field(..., description="Source data reference")
    lines: List[int] = Field(..., min_length=6, max_length=6, description="Six line values (6-9)")
    original_hexagram: int = Field(..., ge=1, le=64, description="Original hexagram number")
    original_hexagram_bin: str = Field(
        ..., min_length=6, max_length=6, description="Binary representation"
    )
    original_hexagram_bin2dec: int = Field(
        ..., ge=0, le=63, description="Decimal value of binary representation"
    )
    resulting_hexagram: int = Field(..., ge=1, le=64, description="Resulting hexagram number")
    resulting_hexagram_bin: str = Field(
        ..., min_length=6, max_length=6, description="Binary representation"
    )
    resulting_hexagram_bin2dec: int = Field(
        ..., ge=0, le=63, description="Decimal value of binary representation"
    )
    has_changing_lines: bool = Field(..., description="Whether any lines are changing")
    changing_line_positions: List[int] = Field(
        default_factory=list,
        description="Positions of changing lines (1-6)"
    )

    @field_validator("lines")
    @classmethod
    def validate_lines(cls, v: List[int]) -> List[int]:
        """Ensure all line values are valid (6, 7, 8, or 9)."""
        if not all(line in (6, 7, 8, 9) for line in v):
            raise ValueError("Line values must be 6, 7, 8, or 9")
        return v

    @field_validator("original_hexagram_bin", "resulting_hexagram_bin")
    @classmethod
    def validate_binary(cls, v: str) -> str:
        """Ensure binary string is valid."""
        if not all(c in "01" for c in v):
            raise ValueError("Binary representation must contain only 0 and 1")
        return v


class EggDataPoint(BaseModel):
    """Data point for a single egg."""
    persec: Optional[Union[int, float]] = Field(None, description="Per-second value")
    persecz: Optional[float] = Field(None, description="Per-second Z-score")
    perseczcs: Optional[float] = Field(None, description="Per-second Z-score cumulative sum")


class EggStoufferData(BaseModel):
    """Stouffer combined data for a timestamp."""
    StoufferZ: Optional[float] = Field(None, description="Stouffer Z statistic")
    CSZ2_1: Optional[float] = Field(None, alias="CSZ2-1", description="Cumulative Stouffer Z squared minus 1")


class EggDerived(BaseModel):
    """Global Consciousness Project egg data."""
    source: str = Field(default="global-mind.org", description="Data source")
    persec: Optional[dict] = Field(None, description="Per-second data: dict keyed by Unix time with list values (lines 30-91, column A excluded)")
    persecz: Optional[dict] = Field(None, description="Per-second Z-score: dict keyed by Unix time with list values (lines 96-155, column A excluded)")
    perseczcs: Optional[dict] = Field(None, description="Per-second Z-score cumulative sum: dict keyed by Unix time with list values (lines 160-219, column A excluded)")
    stouffer: Optional[dict] = Field(None, description="Stouffer statistics: dict keyed by Unix time with dict values {StoufferZ, CSZ2-1} (lines 223-283)")


class Derived(BaseModel):
    """Derived data structures."""
    iching: Optional[IChingDerived] = Field(None, description="I Ching hexagram data")
    egg: Optional[EggDerived] = Field(None, description="Global Consciousness Project egg data")


class MetadataChecks(BaseModel):
    """Quality checks and statistics."""
    byte_len_total: int = Field(..., ge=0, description="Total bytes across all sources")
    monobit_ratio: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Ratio of 1-bits to total bits (sanity check)"
    )


class Metadata(BaseModel):
    """Response metadata."""
    description: str = Field(..., description="Human-readable description")
    checks: MetadataChecks = Field(..., description="Quality checks")


class UnifiedResponse(BaseModel):
    """Complete unified API response."""
    version: str = Field(default="1.0", description="Schema version")
    request: RequestInfo = Field(..., description="Request metadata")
    sources: List[Source] = Field(default_factory=list, description="Data sources")
    derived: Derived = Field(default_factory=Derived, description="Derived structures")
    metadata: Metadata = Field(..., description="Response metadata")

    def model_dump_json_schema(self) -> str:
        """Export as JSON Schema."""
        return json.dumps(self.model_json_schema(), indent=2)


# Export JSON Schema
def generate_schema_file(output_path: str = "schema_unified.json") -> None:
    """Generate and save the JSON Schema to a file."""
    schema = UnifiedResponse.model_json_schema()
    with open(output_path, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Schema written to {output_path}")


if __name__ == "__main__":
    generate_schema_file()

