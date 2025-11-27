import sys
import json
import os
import re
from pathlib import Path

# Add parent directory to path to import voynich_data
sys.path.append(str(Path(__file__).parent.parent))
from research.voynich_data import get_section_text, get_folio_text

def get_words(text):
    # Split by dots, spaces, and other separators common in EVA
    text_clean = re.sub(r'[!?<>@$\d]', '', text)
    words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w]
    return words

def normalize_word(word):
    return word.strip()

def run_analysis():
    print("Starting Track 185: 'os' Star Map Analysis...")
    
    # 1. Get Astronomical Text
    astro_pages = get_section_text('astronomical')
    print(f"Loaded {len(astro_pages)} astronomical pages.")
    
    # Debug: Print first few words of first page
    if astro_pages:
        first_folio = list(astro_pages.keys())[0]
        first_text = list(astro_pages[first_folio].values())[0]
        print(f"DEBUG: Sample text from {first_folio}: {first_text}")
        print(f"DEBUG: Words: {get_words(first_text)[:10]}")
    
    # 2. Count os/oteos
    targets = ['os', 'oteos']
    
    page_counts = {}
    label_matches = {}
    total_astro_words = 0
    
    for folio, lines in astro_pages.items():
        count = 0
        occurrences = []
        page_words = 0
        for loc, text in lines.items():
            words = get_words(text)
            page_words += len(words)
            for word in words:
                clean_word = normalize_word(word)
                if clean_word in targets:
                    count += 1
                    occurrences.append((loc, clean_word, text))
        
        page_counts[folio] = count
        label_matches[folio] = occurrences
        total_astro_words += page_words
        
    print(f"Total occurrences in Astro: {sum(page_counts.values())}")

    # 3. Herbal Comparison
    herbal_a = get_section_text('herbal_a')
    herbal_b = get_section_text('herbal_b')
    herbal_pages = {**herbal_a, **herbal_b}
    
    herbal_counts = []
    total_herbal_words = 0
    
    for folio, lines in herbal_pages.items():
        count = 0
        for text in lines.values():
            words = get_words(text)
            total_herbal_words += len(words)
            for word in words:
                if normalize_word(word) in targets:
                    count += 1
        herbal_counts.append(count)
    
    avg_astro = sum(page_counts.values()) / len(page_counts) if page_counts else 0
    avg_herbal = sum(herbal_counts) / len(herbal_counts) if herbal_counts else 0
    
    freq_astro = (sum(page_counts.values()) / total_astro_words * 1000) if total_astro_words else 0
    freq_herbal = (sum(herbal_counts) / total_herbal_words * 1000) if total_herbal_words else 0
    
    print(f"Astro Average: {avg_astro:.2f} (Freq: {freq_astro:.2f}/1000 words)")
    print(f"Herbal Average: {avg_herbal:.2f} (Freq: {freq_herbal:.2f}/1000 words)")

    # 4. Generate Reports
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Report: star_map_os.md
    with open(output_dir / "star_map_os.md", "w") as f:
        f.write("# The 'os' Star Map (Track 185)\n\n")
        f.write("## Hypothesis\n")
        f.write("`os` = 'Star' / 'Blue' / 'Gold'\n\n")
        f.write("## Heatmap (Astronomical Section)\n\n")
        f.write("| Folio | Count | Occurrences (Location: Text) |\n")
        f.write("|-------|-------|------------------------------|\n")
        
        sorted_folios = sorted(page_counts.keys())
        for folio in sorted_folios:
            count = page_counts[folio]
            occs = label_matches[folio]
            
            # Format occurrences
            formatted_occs = []
            for loc, word, text in occs:
                # Highlight word in text
                highlighted = text.replace(word, f"**{word}**")
                formatted_occs.append(f"`{loc}`: {highlighted}")
            
            occ_str = "<br>".join(formatted_occs) if formatted_occs else "-"
            # Limit occurrence string length if too long
            if len(occ_str) > 1000:
                occ_str = occ_str[:1000] + "... (truncated)"
                
            f.write(f"| {folio} | {count} | {occ_str} |\n")
            
        f.write("\n## Comparative Analysis\n\n")
        f.write("### Frequency Statistics\n")
        f.write(f"- **Astronomical Section**:\n")
        f.write(f"  - Total Occurrences: {sum(page_counts.values())}\n")
        f.write(f"  - Average per Page: {avg_astro:.2f}\n")
        f.write(f"  - Frequency: {freq_astro:.2f} per 1000 words\n")
        f.write(f"- **Herbal Section**:\n")
        f.write(f"  - Total Occurrences: {sum(herbal_counts)}\n")
        f.write(f"  - Average per Page: {avg_herbal:.2f}\n")
        f.write(f"  - Frequency: {freq_herbal:.2f} per 1000 words\n")
        
        ratio = freq_astro / freq_herbal if freq_herbal > 0 else 0
        f.write(f"\n**Ratio (Astro/Herbal Frequency)**: {ratio:.2f}x\n\n")
        
        f.write("## Interpretation\n")
        if ratio > 1.5:
            f.write(f"Strong correlation detected: `os` appears {ratio:.1f}x more frequently in the Astronomical section.\n")
            f.write("This SUPPORTS the hypothesis that `os` is related to celestial bodies (stars/planets) or sky colors.\n")
        else:
            f.write("No significant correlation with Astronomical section detected.\n")
            f.write("This WEAKENS the hypothesis that `os` is exclusively a star/sky term.\n")
            
    # Summary: track-185-results_summary.md
    with open(output_dir / "track-185-results_summary.md", "w") as f:
        f.write("# Track 185 Results Summary\n\n")
        f.write("## Key Findings\n")
        f.write(f"- Found {sum(page_counts.values())} occurrences of `os`/`oteos` in Astronomical section.\n")
        f.write(f"- Astronomical Frequency: {freq_astro:.2f}/1000 words vs Herbal: {freq_herbal:.2f}/1000 words.\n")
        if ratio > 1.5:
             f.write(f"- **VALIDATED**: `os` is {ratio:.1f}x more common in Astronomical pages.\n")
        else:
             f.write(f"- **NEGATIVE**: `os` usage is similar across sections ({ratio:.1f}x ratio).\n")

    print("Analysis complete. Reports generated.")

if __name__ == "__main__":
    run_analysis()
