import csv
import os
from collections import Counter
from research.voynich_data import get_section_text

INPUT_SCOPE = "results/scope_analysis.csv"
OUTPUT_FILE = "results/local_variable_map.csv"

def main():
    if not os.path.exists(INPUT_SCOPE):
        print(f"Error: {INPUT_SCOPE} not found.")
        return

    # 1. Extract Local Variables for Astro and Bio
    astro_vars = []
    bio_vars = []
    
    with open(INPUT_SCOPE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Local Variable' in row['classification']:
                if 'Astro' in row['dominant_scope']:
                    astro_vars.append(row['word'])
                elif 'Bio' in row['dominant_scope']:
                    bio_vars.append(row['word'])
    
    # Take top 20 by some metric? The CSV is sorted by count.
    # Let's take top 30.
    astro_vars = astro_vars[:30]
    bio_vars = bio_vars[:30]
    
    print(f"Mapping {len(astro_vars)} Astro vars and {len(bio_vars)} Bio vars...")
    
    # 2. Astro Mapping: Check Distribution across Folios
    # Does variable X appear only on f70r (Aries)?
    astro_text = get_section_text("astronomical")
    
    results = []
    
    # Astro
    for var in astro_vars:
        pages = []
        for folio, lines in astro_text.items():
            full_text = " ".join(lines.values())
            if var in full_text.split():
                pages.append(folio)
        
        # Heuristic: Map to Zodiac?
        # Aries=f70r/f71r, Taurus=f71v, etc.
        # Simplified: Just list the pages
        results.append(['Astro', var, ", ".join(pages)])

    # Bio
    bio_text = get_section_text("biological")
    for var in bio_vars:
        pages = []
        for folio, lines in bio_text.items():
            full_text = " ".join(lines.values())
            if var in full_text.split():
                pages.append(folio)
        results.append(['Bio', var, ", ".join(pages)])

    # Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['section', 'variable', 'appears_on'])
        writer.writerows(results)
        
    print(f"Mapped local variables to pages.")

if __name__ == "__main__":
    main()
