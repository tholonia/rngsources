"""
Fetcher functions for quantum random number sources.
"""

import hashlib
import base64
import time
from typing import Dict, List, Tuple, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def create_session_with_retry() -> requests.Session:
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 checksum of bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_monobit_ratio(data: bytes, max_bytes: int = 1024) -> float:
    """Compute ratio of 1-bits to total bits in first max_bytes."""
    sample = data[:max_bytes]
    if not sample:
        return 0.0
    
    ones = sum(bin(b).count('1') for b in sample)
    total_bits = len(sample) * 8
    return ones / total_bits if total_bits > 0 else 0.0


def fetch_anu_uint16(length: int = 6, timeout: int = 10) -> Dict:
    """
    Fetch uint16 values from ANU QRNG.
    
    Returns dict with:
        - success: bool
        - data_uint16: List[int]
        - data_bytes: bytes (MSB order)
        - error: Optional[str]
    """
    url = f"https://qrng.anu.edu.au/API/jsonI.php?length={length}&type=uint16"
    session = create_session_with_retry()
    
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            return {
                "success": False,
                "error": "ANU API returned success=false"
            }
        
        values = data.get("data", [])
        if len(values) != length:
            return {
                "success": False,
                "error": f"Expected {length} values, got {len(values)}"
            }
        
        # Convert to bytes (big-endian/MSB)
        data_bytes = b''.join(v.to_bytes(2, byteorder='big') for v in values)
        
        return {
            "success": True,
            "data_uint16": values,
            "data_bytes": data_bytes,
            "url": url
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def fetch_lfd_hex(length_bytes: int = 64, timeout: int = 10) -> Dict:
    """
    Fetch hex string from LfD QRNG.
    
    Returns dict with:
        - success: bool
        - data_hex: str
        - data_bytes: bytes
        - data_uint8: List[int]
        - error: Optional[str]
    """
    url = f"https://lfdr.de/qrng_api/qrng?length={length_bytes}&format=HEX"
    session = create_session_with_retry()
    
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        hex_string = data.get("qrn", "")
        expected_chars = length_bytes * 2
        
        if len(hex_string) != expected_chars:
            return {
                "success": False,
                "error": f"Expected {expected_chars} hex chars, got {len(hex_string)}"
            }
        
        # Decode to bytes
        data_bytes = bytes.fromhex(hex_string)
        data_uint8 = list(data_bytes)
        
        return {
            "success": True,
            "data_hex": hex_string,
            "data_bytes": data_bytes,
            "data_uint8": data_uint8,
            "url": url
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_fallback_uint16_from_quantum(
    quantum_bytes: bytes,
    length: int = 6
) -> Dict:
    """
    Generate fallback uint16 values from quantum bytes.
    
    Uses first 2*length bytes to create uint16 values.
    """
    if len(quantum_bytes) < length * 2:
        return {
            "success": False,
            "error": "Insufficient quantum bytes for fallback"
        }
    
    values = []
    for i in range(length):
        uint16_val = int.from_bytes(
            quantum_bytes[i*2:(i*2)+2],
            byteorder='big'
        )
        values.append(uint16_val)
    
    data_bytes = quantum_bytes[:length*2]
    
    return {
        "success": True,
        "data_uint16": values,
        "data_bytes": data_bytes,
        "url": "locally_determined"
    }


def read_curby_local(
    csv_path: str,
    seed: int,
    kind: str = "u32"
) -> Dict:
    """
    Read from local CURBy CSV file.
    
    Args:
        csv_path: Path to CSV file
        seed: Random seed for selection
        kind: 'u8' or 'u32'
    
    Returns dict with:
        - success: bool
        - data_uint32: List[int] (if u32)
        - data_uint8: List[int] (if u8)
        - data_bytes: bytes
        - selected_index: int
        - total_lines: int
        - error: Optional[str]
    """
    import random
    
    try:
        with open(csv_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            return {
                "success": False,
                "error": f"CSV file {csv_path} is empty"
            }
        
        # Seed and select
        random.seed(seed)
        selected_index = random.randint(0, len(lines) - 1)
        value = int(lines[selected_index])
        
        if kind == "u32":
            # Convert uint32 to bytes (big-endian)
            data_bytes = value.to_bytes(4, byteorder='big')
            return {
                "success": True,
                "data_uint32": [value],
                "data_bytes": data_bytes,
                "selected_index": selected_index,
                "total_lines": len(lines),
                "file_path": csv_path
            }
        elif kind == "u8":
            # Treat as uint8
            if value > 255:
                return {
                    "success": False,
                    "error": f"Value {value} exceeds uint8 range"
                }
            data_bytes = bytes([value])
            return {
                "success": True,
                "data_uint8": [value],
                "data_bytes": data_bytes,
                "selected_index": selected_index,
                "total_lines": len(lines),
                "file_path": csv_path
            }
        else:
            return {
                "success": False,
                "error": f"Unknown kind: {kind}"
            }
            
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"File not found: {csv_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

