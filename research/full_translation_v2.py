import json
import re
from pathlib import Path
import voynich_data

DICT_PATH = Path("results/dictionary/master_dictionary_v17.json")
OUTPUT_MD = Path("results/full_translation_v2.md")
SUMMARY_MD = Path("results/track-305-results_summary.md")

def get_section(folio):
    # Extract number
    match = re.search(r'(\d+)', folio)
    if not match:
        return "unknown"
    num = int(match.group(1))
    
    if 1 <= num <= 25: return "Herbal A"
    if 26 <= num <= 57: return "Herbal B"
    if 58 <= num <= 66: return "Gap/Missing" # traditionally gap
    if 67 <= num <= 73: return "Astronomical"
    if 75 <= num <= 84: return "Biological"
    if 85 <= num <= 86: return "Rosettes" # f85-86 foldout
    if 87 <= num <= 102: return "Pharmaceutical"
    if 103 <= num <= 116: return "Recipes"
    return "Unknown"

def load_dict():
    with open(DICT_PATH) as f:
        data = json.load(f)
    return data.get("entries", {})

def translate_word(word, dictionary):
    entry = dictionary.get(word)
    if entry:
        meaning = entry.get("meaning")
        # Filter out technical/empty meanings if needed, but "Suffix" etc are useful.
        # If meaning is "unknown", skip.
        if meaning and "unknown" not in meaning.lower():
            return meaning
    return None

def main():
    print("Loading dictionary...")
    dictionary = load_dict()
    print(f"Loaded {len(dictionary)} entries.")
    
    print("Loading pages...")
    pages = voynich_data.get_eva_pages()
    print(f"Loaded {len(pages)} folios.")
    
    full_md = []
    full_md.append("# Full Voynich Manuscript Translation (v2)")
    full_md.append(f"**Dictionary Version**: v17")
    full_md.append(f"**Generated**: 2025-11-27")
    full_md.append("")
    
    total_words = 0
    translated_words = 0
    
    section_stats = {}
    
    # Sort folios naturally
    def sort_key(f):
        match = re.search(r'(\d+)', f)
        if not match: return 999999
        num = int(match.group(1))
        # suffix priority: r < v
        is_v = 'v' in f
        # sub-suffix: r1, r2 etc.
        suffix_num = 0
        end_match = re.search(r'\d+$', f)
        if end_match and end_match.group(0) != str(num):
            suffix_num = int(end_match.group(0))
        
        return num * 100 + (50 if is_v else 0) + suffix_num

    sorted_folios = sorted(pages.keys(), key=sort_key)

    print("Translating...")
    for folio in sorted_folios:
        section = get_section(folio)
        if section not in section_stats:
            section_stats[section] = {"total": 0, "translated": 0}
            
        lines = pages[folio]
        
        full_md.append(f"## Folio {folio} ({section})")
        full_md.append("")
        
        for loc, text in lines.items():
            # Tokenize
            clean_text = re.sub(r'[!?<>@$\d]', '', text)
            words = [w for w in re.split(r'[.\-=,\s]+', clean_text) if w]
            
            trans_line = []
            for w in words:
                total_words += 1
                section_stats[section]["total"] += 1
                
                trans = translate_word(w, dictionary)
                if trans:
                    translated_words += 1
                    section_stats[section]["translated"] += 1
                    trans_line.append(f"**{trans}**")
                else:
                    trans_line.append(w)
            
            # Add line to MD
            full_md.append(f"- **{loc}**: {' '.join(trans_line)}")
        
        full_md.append("")

    # Save Full Translation
    print(f"Writing translation to {OUTPUT_MD}...")
    with open(OUTPUT_MD, "w") as f:
        f.write("\n".join(full_md))
    
    # Calculate Stats
    coverage = (translated_words / total_words * 100) if total_words > 0 else 0
    
    # Summary
    summary = []
    summary.append("# Track 305 Results Summary: Full Translation v2")
    summary.append("")
    summary.append(f"## Global Coverage")
    summary.append(f"- **Total Words**: {total_words}")
    summary.append(f"- **Translated**: {translated_words}")
    summary.append(f"- **Coverage**: {coverage:.2f}%")
    summary.append(f"- **Comparison**: v1 was 19.1%. Improvement: {coverage - 19.1:.2f}%")
    summary.append("")
    summary.append("## Coverage by Section")
    summary.append("| Section | Total Words | Translated | Coverage |")
    summary.append("|---------|-------------|------------|----------|")
    
    for sec, stats in sorted(section_stats.items(), key=lambda x: x[0]):
        if stats["total"] > 0:
            cov = (stats["translated"] / stats["total"] * 100)
            summary.append(f"| {sec} | {stats['total']} | {stats['translated']} | {cov:.2f}% |")
            
    print(f"Writing summary to {SUMMARY_MD}...")
    with open(SUMMARY_MD, "w") as f:
        f.write("\n".join(summary))

    print(f"Done. Coverage: {coverage:.2f}%")

if __name__ == "__main__":
    main()
