"""
FastAPI application for unified quantum RNG API.
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import sys

from models import UnifiedResponse
from assembler import build_unified_response
from backward_compat import legacy_to_unified, LegacyResponse


app = FastAPI(
    title="Unified Quantum RNG API",
    description="Multi-source quantum random number generation with unified schema",
    version="1.0.0"
)


@app.get("/")
async def root():
    """API root - health check."""
    return {
        "status": "healthy",
        "api": "Unified Quantum RNG",
        "version": "1.0.0",
        "endpoints": {
            "/random/unified": "Main unified random data endpoint",
            "/random/legacy": "Legacy format converter",
            "/schema": "JSON Schema definition"
        }
    }


@app.get("/random/unified", response_model=UnifiedResponse)
async def get_unified_random(
    anu_len: int = Query(6, ge=1, le=1024, description="Number of uint16 values from ANU"),
    lfd_bytes: int = Query(64, ge=1, le=4096, description="Number of bytes from LfD"),
    curby_kind: str = Query("u32", regex="^(u8|u32)$", description="CURBy data type"),
    curby_count: int = Query(1, ge=1, le=10, description="Number of CURBy values"),
    curby_path: str = Query(
        "random_packed_u32be.csv",
        description="Path to CURBy CSV file"
    ),
    include_iching: bool = Query(True, description="Include I Ching derivation")
) -> UnifiedResponse:
    """
    Get unified quantum random data from multiple sources.
    
    Sources:
    - ANU QRNG: Vacuum fluctuation quantum randomness
    - LfD QRNG: ID Quantique photonic quantum randomness
    - CURBy: Local SHA3-extracted quantum data
    - I Ching: Derived hexagram using yarrow stick method
    """
    try:
        response = build_unified_response(
            anu_len=anu_len,
            lfd_bytes=lfd_bytes,
            curby_kind=curby_kind,
            curby_path=curby_path,
            curby_count=curby_count,
            include_iching=include_iching
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/random/legacy")
async def convert_legacy(legacy_data: LegacyResponse) -> UnifiedResponse:
    """
    Convert legacy format to unified format.
    
    Accepts old JSON format and returns unified schema.
    """
    try:
        unified = legacy_to_unified(legacy_data.model_dump())
        return unified
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion failed: {str(e)}")


@app.get("/schema")
async def get_schema():
    """
    Get the JSON Schema for the unified response format.
    """
    return JSONResponse(content=UnifiedResponse.model_json_schema())


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "quantum-rng-unified"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

