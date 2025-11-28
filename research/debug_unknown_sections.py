import sys
import os
sys.path.append(os.getcwd())
import research.voynich_data as voynich_data

def check_unknowns():
    pages = voynich_data.get_eva_pages(transcriber='H')
    
    # Replicate logic
    section_map = {
        'herbal_a': 'Herbal',
        'herbal_b': 'Herbal',
        'astronomical': 'Astro',
        'biological': 'Bio',
        'pharmaceutical': 'Pharma',
        'recipes': 'Recipes',
        'zodiac': 'Astro',
        'cosmological': 'Cosmo'
    }
    
    folio_to_section = {}
    if hasattr(voynich_data, 'FOLIO_SECTIONS'):
        for internal_section, target_category in section_map.items():
            folios = voynich_data.FOLIO_SECTIONS.get(internal_section, [])
            for folio in folios:
                folio_clean = folio.lower()
                folio_to_section[folio_clean] = target_category

    unknown_counts = {}
    
    for folio in pages.keys():
        folio_clean = folio.lower()
        if folio_clean not in folio_to_section:
            # Count words
            lines = pages[folio]
            count = 0
            for line in lines.values():
                count += len(line.split()) # Rough count
            unknown_counts[folio] = count

    print("Unknown Pages:")
    for f, c in sorted(unknown_counts.items()):
        print(f"{f}: {c}")

if __name__ == "__main__":
    check_unknowns()
