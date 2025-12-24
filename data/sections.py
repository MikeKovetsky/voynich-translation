from typing import Optional, Dict

class Section:
    HERBAL = "Herbal"
    ASTRONOMICAL = "Astronomical"
    BIOLOGICAL = "Biological"
    COSMOLOGICAL = "Cosmological"
    PHARMACEUTICAL = "Pharmaceutical"
    RECIPES = "Recipes"
    UNKNOWN = "Unknown"

# Mapping of folio ranges to sections
# Ranges are inclusive and approximate based on scholarly consensus (e.g., Wikipedia)
_SECTION_RANGES = [
    (1, 66, Section.HERBAL),
    (67, 73, Section.ASTRONOMICAL),
    (75, 84, Section.BIOLOGICAL),
    (85, 86, Section.COSMOLOGICAL),
    (87, 102, Section.PHARMACEUTICAL),
    (103, 116, Section.RECIPES),
]

def get_section_for_folio(folio_number: int) -> str:
    """
    Returns the section name for a given folio number.
    
    Args:
        folio_number: The integer number of the folio (e.g., 1 for '1r', 42 for '42v')
    """
    for start, end, section in _SECTION_RANGES:
        if start <= folio_number <= end:
            return section
    return Section.UNKNOWN

def get_section_for_filename(filename: str) -> str:
    """
    Extracts folio number from filename and returns the section.
    Expected format: '003_1r.jpg' or similar where the second part is the folio.
    """
    try:
        # Example: 003_1r.jpg -> 1
        # Example: 082_41v.jpg -> 41
        parts = filename.split('_')
        if len(parts) >= 2:
            folio_part = parts[1]
            # Extract digits from '1r', '41v', etc.
            digits = ''.join(filter(str.isdigit, folio_part))
            if digits:
                return get_section_for_folio(int(digits))
    except Exception:
        pass
    return Section.UNKNOWN
