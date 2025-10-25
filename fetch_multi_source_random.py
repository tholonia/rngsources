#!/usr/bin/env python3
"""
Multi-source random number fetcher that combines data from:
1. ANU QRNG (Australian National University) - 6 uint16 values
2. LfD QRNG (Germany) - 64 bytes hexadecimal
3. Local CSV file - seeded selection from random_packed_u32be.csv
4. I Ching hexagram - using yarrow stick method
"""

import json
import random
import requests

# King Wen sequence lookup table
# Maps binary representation (bottom to top) to hexagram number
# Binary: lower trigram (bits 0-2) + upper trigram (bits 3-5)
KING_WEN_SEQUENCE = [
    2, 23, 8, 20, 16, 35, 45, 12,  # 000xxx (☷ Earth below)
    15, 52, 39, 53, 62, 56, 31, 33,  # 001xxx (☶ Mountain below)
    7, 4, 29, 59, 40, 64, 47, 6,   # 010xxx (☵ Water below)
    46, 18, 48, 57, 32, 50, 28, 44,  # 011xxx (☴ Wind below)
    24, 27, 3, 42, 51, 21, 17, 25,  # 100xxx (☳ Thunder below)
    36, 22, 63, 37, 55, 30, 49, 13,  # 101xxx (☲ Fire below)
    19, 41, 60, 61, 54, 38, 58, 10,  # 110xxx (☱ Lake below)
    11, 26, 5, 9, 34, 14, 43, 1    # 111xxx (☰ Heaven below)
]


def cast_yarrow_line(random_value):
    """
    Cast a single I Ching line using yarrow stick method probabilities.
    
    Traditional yarrow stick probabilities:
    - 6 (Old Yin, changing):  1/16 = 0.0625
    - 7 (Young Yang, stable): 5/16 = 0.3125
    - 8 (Young Yin, stable):  7/16 = 0.4375
    - 9 (Old Yang, changing): 3/16 = 0.1875
    
    Args:
        random_value (int): Random integer (e.g., 0-255 from a byte)
        
    Returns:
        int: Line value (6, 7, 8, or 9)
    """
    # Normalize to 0-1 range
    normalized = (random_value % 256) / 256.0
    
    # Map to yarrow stick probabilities
    if normalized < 1/16:
        return 6  # Old Yin
    elif normalized < 6/16:
        return 7  # Young Yang
    elif normalized < 13/16:
        return 8  # Young Yin
    else:
        return 9  # Old Yang


def lines_to_hexagram_number(lines):
    """
    Convert six I Ching lines to a hexagram number (1-64) using King Wen sequence.
    
    Args:
        lines (list): List of 6 line values (6, 7, 8, or 9)
                     Ordered from bottom to top
        
    Returns:
        int: Hexagram number (1-64)
    """
    # Convert lines to binary (Yang=1, Yin=0)
    binary = 0
    for i, line in enumerate(lines):
        if line in (7, 9):  # Yang lines
            binary |= (1 << i)
    
    # Look up in King Wen sequence
    return KING_WEN_SEQUENCE[binary]


def transform_changing_lines(lines):
    """
    Transform changing lines (6→7, 9→8) to get the resulting hexagram.
    
    Args:
        lines (list): List of 6 line values (6, 7, 8, or 9)
        
    Returns:
        list: Transformed lines with changing lines flipped
    """
    transformed = []
    for line in lines:
        if line == 6:  # Old Yin → Young Yang
            transformed.append(7)
        elif line == 9:  # Old Yang → Young Yin
            transformed.append(8)
        else:  # Stable lines remain unchanged
            transformed.append(line)
    return transformed


def lines_to_binary(lines):
    """
    Convert six I Ching lines to binary representation.
    
    Args:
        lines (list): List of 6 line values (6, 7, 8, or 9)
                     Ordered from bottom to top
        
    Returns:
        int: Binary representation (0-63) where Yang=1, Yin=0
    """
    binary = 0
    for i, line in enumerate(lines):
        if line in (7, 9):  # Yang lines
            binary |= (1 << i)
    return binary


def cast_iching_hexagram(random_bytes):
    """
    Cast a complete I Ching hexagram using the yarrow stick method.
    
    Args:
        random_bytes (bytes): At least 6 bytes of random data
        
    Returns:
        dict: Contains original hexagram, resulting hexagram, and line details
    """
    if len(random_bytes) < 6:
        raise ValueError("Need at least 6 bytes of random data to cast hexagram")
    
    # Cast six lines (bottom to top)
    lines = [cast_yarrow_line(random_bytes[i]) for i in range(6)]
    
    # Get binary representations
    original_binary = lines_to_binary(lines)
    
    # Get original hexagram number
    original_hexagram = lines_to_hexagram_number(lines)
    
    # Transform changing lines
    transformed_lines = transform_changing_lines(lines)
    
    # Get binary representation of resulting hexagram
    resulting_binary = lines_to_binary(transformed_lines)
    
    # Get resulting hexagram number
    resulting_hexagram = lines_to_hexagram_number(transformed_lines)
    
    # Check if there are any changing lines
    has_changing_lines = any(line in (6, 9) for line in lines)
    
    return {
        "lines": lines,
        "original_hexagram": original_hexagram,
        "original_hexagram_binary": original_binary,
        "original_hexagram_bin2dec": original_binary,
        "resulting_hexagram": resulting_hexagram,
        "resulting_hexagram_binary": resulting_binary,
        "resulting_hexagram_bin2dec": resulting_binary,
        "has_changing_lines": has_changing_lines,
        "changing_line_positions": [i + 1 for i, line in enumerate(lines) if line in (6, 9)]
    }


def fetch_multi_source_random(csv_path="random_packed_u32be.csv"):
    """
    Fetches random data from four sources:
    
    Source 1: ANU QRNG API - array of 6 uint16 values (or quantum-seeded fallback)
    Source 2: LfD QRNG API - 64 byte hexadecimal string (fetched first)
    Source 3: Local CSV file - one value randomly selected using first uint16 as seed
    Source 4: I Ching hexagram - cast using yarrow stick method with Source 2 data
    
    Args:
        csv_path (str): Path to the CSV file containing uint32 values
        
    Returns:
        dict: JSON object containing all four random data sources
    """
    
    # Source 2: Fetch 64 byte hex value from LfD QRNG (fetch FIRST for fallback use)
    lfd_url = "https://lfdr.de/qrng_api/qrng?length=64&format=HEX"
    try:
        lfd_response = requests.get(lfd_url, timeout=10)
        lfd_response.raise_for_status()
        lfd_data = lfd_response.json()
        
        lfd_hex = lfd_data.get("qrn", "")
        if len(lfd_hex) != 128:  # 64 bytes = 128 hex characters
            raise ValueError(f"Expected 128 hex characters (64 bytes), got {len(lfd_hex)}")
        
        # Convert to bytes for later use
        lfd_bytes = bytes.fromhex(lfd_hex)
            
    except Exception as e:
        raise RuntimeError(f"Failed to fetch from LfD QRNG: {e}")
    
    # Source 1: Fetch 6 uint16 values from ANU QRNG (with fallback to quantum-seeded PRNG)
    anu_url = "https://qrng.anu.edu.au/API/jsonI.php?length=6&type=uint16"
    anu_fallback_used = False
    
    try:
        anu_response = requests.get(anu_url, timeout=10)
        anu_response.raise_for_status()
        anu_data = anu_response.json()
        
        if not anu_data.get("success"):
            raise ValueError("ANU QRNG API request was not successful")
        
        anu_values = anu_data.get("data", [])
        if len(anu_values) < 6:
            raise ValueError(f"Expected 6 values from ANU QRNG, got {len(anu_values)}")
        
        anu_generation_technique = "vacuum_fluctuation_optics"
        anu_technique_description = "Measures quantum vacuum fluctuations via beam-split light intensity"
            
    except Exception as e:
        # Fallback: Use first 6 uint16 values from Source 2 hex data
        print(f"Warning: ANU QRNG failed ({e}), using quantum-seeded fallback")
        anu_fallback_used = True
        anu_url = "locally_determined"
        
        # Extract 6 uint16 values from first 12 bytes of LfD data
        anu_values = []
        for i in range(6):
            # Each uint16 is 2 bytes, big-endian
            uint16_val = int.from_bytes(lfd_bytes[i*2:(i*2)+2], byteorder='big')
            anu_values.append(uint16_val)
        
        anu_generation_technique = "quantum_photonics_IDQ_seeded"
        anu_technique_description = "One-off first generation Mersenne Twister seeded with quantum photonic entropy"
    
    # Source 3: Read from local CSV and select using seed
    try:
        # Use the first uint16 value as seed
        seed = anu_values[0]
        
        # Read all lines from CSV
        with open(csv_path, 'r') as f:
            csv_lines = [line.strip() for line in f if line.strip()]
        
        if not csv_lines:
            raise ValueError(f"CSV file {csv_path} is empty")
        
        # Seed the random number generator and select an index
        random.seed(seed)
        selected_index = random.randint(0, len(csv_lines) - 1)
        selected_value = int(csv_lines[selected_index])
        
    except FileNotFoundError:
        raise RuntimeError(f"CSV file not found: {csv_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to read from local CSV: {e}")
    
    # Source 4: Cast I Ching hexagram using yarrow stick method
    try:
        # Use bytes 12-17 from Source 2 (to avoid overlap with Source 1 fallback which uses bytes 0-11)
        hexagram_bytes = lfd_bytes[12:18]
        hexagram_result = cast_iching_hexagram(hexagram_bytes)
        
    except Exception as e:
        raise RuntimeError(f"Failed to cast I Ching hexagram: {e}")
    
    # Build the result JSON
    result = {
        "sources": {
            "source1_anu_qrng": {
                "type": "uint16",
                "length": 6,
                "data": anu_values,
                "url": anu_url,
                "generation_technique": anu_generation_technique,
                "technique_description": anu_technique_description,
                "fallback_used": anu_fallback_used
            },
            "source2_lfd_qrng": {
                "type": "hex",
                "length": 64,
                "data": lfd_hex,
                "url": lfd_url,
                "generation_technique": "quantum_photonics_IDQ",
                "technique_description": "Uses ID Quantique hardware (quantum photonic entropy source)"
            },
            "source3_local_csv": {
                "type": "uint32",
                "seed": seed,
                "selected_index": selected_index,
                "data": selected_value,
                "file": csv_path,
                "total_lines": len(csv_lines),
                "generation_technique": "sha3_extracted_quantum",
                "technique_description": "Quantum entropy post-processed with SHA3-256 block hashing"
            },
            "source4_iching": {
                "lines": hexagram_result["lines"],
                "original_hexagram": hexagram_result["original_hexagram"],
                "original_hexagram_binary": hexagram_result["original_hexagram_binary"],
                "original_hexagram_bin2dec": hexagram_result["original_hexagram_bin2dec"],
                "resulting_hexagram": hexagram_result["resulting_hexagram"],
                "resulting_hexagram_binary": hexagram_result["resulting_hexagram_binary"],
                "resulting_hexagram_bin2dec": hexagram_result["resulting_hexagram_bin2dec"],
                "has_changing_lines": hexagram_result["has_changing_lines"],
                "changing_line_positions": hexagram_result["changing_line_positions"],
                "random_source": "source2_lfd_qrng (bytes 12-17)",
                "generation_technique": "yarrow_stick",
                "technique_description": "Traditional yarrow stick divination method applied to quantum random entropy source"
            }
        },
        "metadata": {
            "description": "Combined random data from four sources including I Ching hexagram",
            "timestamp": None  # Can add timestamp if needed
        }
    }
    
    return result


def main():
    """
    Example usage of the fetch_multi_source_random function
    """
    try:
        result = fetch_multi_source_random()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=__import__('sys').stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

