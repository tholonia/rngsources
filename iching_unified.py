"""
I Ching hexagram casting for unified API.
"""

from typing import Dict, List


# King Wen sequence lookup table
KING_WEN_SEQUENCE = [
    2, 23, 8, 20, 16, 35, 45, 12,   # 000xxx (☷ Earth below)
    15, 52, 39, 53, 62, 56, 31, 33, # 001xxx (☶ Mountain below)
    7, 4, 29, 59, 40, 64, 47, 6,    # 010xxx (☵ Water below)
    46, 18, 48, 57, 32, 50, 28, 44, # 011xxx (☴ Wind below)
    24, 27, 3, 42, 51, 21, 17, 25,  # 100xxx (☳ Thunder below)
    36, 22, 63, 37, 55, 30, 49, 13, # 101xxx (☲ Fire below)
    19, 41, 60, 61, 54, 38, 58, 10, # 110xxx (☱ Lake below)
    11, 26, 5, 9, 34, 14, 43, 1     # 111xxx (☰ Heaven below)
]


def cast_yarrow_line(random_value: int) -> int:
    """
    Cast a single I Ching line using yarrow stick method probabilities.
    
    Traditional yarrow stick probabilities:
    - 6 (Old Yin, changing):  1/16 = 0.0625
    - 7 (Young Yang, stable): 5/16 = 0.3125
    - 8 (Young Yin, stable):  7/16 = 0.4375
    - 9 (Old Yang, changing): 3/16 = 0.1875
    """
    normalized = (random_value % 256) / 256.0
    
    if normalized < 1/16:
        return 6  # Old Yin
    elif normalized < 6/16:
        return 7  # Young Yang
    elif normalized < 13/16:
        return 8  # Young Yin
    else:
        return 9  # Old Yang


def lines_to_binary(lines: List[int]) -> int:
    """
    Convert six I Ching lines to binary representation.
    
    Args:
        lines: List of 6 line values (6, 7, 8, or 9), bottom to top
        
    Returns:
        Binary representation (0-63) where Yang=1, Yin=0
    """
    binary = 0
    for i, line in enumerate(lines):
        if line in (7, 9):  # Yang lines
            binary |= (1 << i)
    return binary


def binary_to_string(binary: int) -> str:
    """Convert binary int to 6-character binary string."""
    return format(binary, '06b')


def lines_to_hexagram_number(lines: List[int]) -> int:
    """
    Convert six I Ching lines to hexagram number (1-64) using King Wen sequence.
    """
    binary = lines_to_binary(lines)
    return KING_WEN_SEQUENCE[binary]


def transform_changing_lines(lines: List[int]) -> List[int]:
    """
    Transform changing lines (6→7, 9→8) to get the resulting hexagram.
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


def cast_iching_hexagram(random_bytes: bytes, source_ref: str = "unknown") -> Dict:
    """
    Cast a complete I Ching hexagram using the yarrow stick method.
    
    Args:
        random_bytes: At least 6 bytes of random data
        source_ref: Reference to the source data (e.g., "lfd[bytes 12..17]")
        
    Returns:
        Dict matching IChingDerived schema
    """
    if len(random_bytes) < 6:
        raise ValueError("Need at least 6 bytes of random data to cast hexagram")
    
    # Cast six lines (bottom to top)
    lines = [cast_yarrow_line(random_bytes[i]) for i in range(6)]
    
    # Get binary representations
    original_binary = lines_to_binary(lines)
    original_binary_str = binary_to_string(original_binary)
    
    # Get original hexagram number
    original_hexagram = lines_to_hexagram_number(lines)
    
    # Transform changing lines
    transformed_lines = transform_changing_lines(lines)
    
    # Get binary representation of resulting hexagram
    resulting_binary = lines_to_binary(transformed_lines)
    resulting_binary_str = binary_to_string(resulting_binary)
    
    # Get resulting hexagram number
    resulting_hexagram = lines_to_hexagram_number(transformed_lines)
    
    # Check if there are any changing lines
    has_changing_lines = any(line in (6, 9) for line in lines)
    
    return {
        "technique": "yarrow_stick",
        "derived_from": source_ref,
        "lines": lines,
        "original_hexagram": original_hexagram,
        "original_hexagram_bin": original_binary_str,
        "original_hexagram_bin2dec": original_binary,
        "resulting_hexagram": resulting_hexagram,
        "resulting_hexagram_bin": resulting_binary_str,
        "resulting_hexagram_bin2dec": resulting_binary,
        "has_changing_lines": has_changing_lines,
        "changing_line_positions": [i + 1 for i, line in enumerate(lines) if line in (6, 9)]
    }

