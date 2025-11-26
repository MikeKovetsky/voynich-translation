
import voynich_data
import re
import json
from collections import Counter

# Output files
OUTPUT_REPORT = "results/herbal_grammar_report.md"
OUTPUT_JSON = "results/herbal_grammar_structure.json"

def get_herbal_pages(start=10, end=30):
    pages = {}
    for i in range(start, end + 1):
        for side in ['r', 'v']:
            folio = f"f{i}{side}"
            text = voynich_data.get_folio_text(folio)
            if text:
                pages[folio] = text
    return pages

def analyze_paragraph_starts(pages):
    starts = []
    # In EVA, paragraph starts are not strictly defined, but we can look at the first word of the first line
    # or lines that seem to start a block.
    # For this analysis, we'll take the first word of the page, and maybe lines that are indented?
    # EVA doesn't strictly show indentation in the text content.
    # We will treat the first word of the page as a definite start.
    
    start_words = []
    
    for folio, lines in pages.items():
        # Sort lines by location to ensure order
        sorted_locs = sorted(lines.keys(), key=lambda x: float(x.split('.')[-1]) if x.split('.')[-1].replace('+', '').isdigit() else 0)
        
        if not sorted_locs:
            continue
            
        first_line_loc = sorted_locs[0]
        first_line_text = lines[first_line_loc]
        
        # Fix splitting logic to handle periods as separators
        words = [w for w in re.split(r'[.\s]', first_line_text) if w and '-' not in w]
        
        if words:
            first_word = words[0]
            start_words.append({
                "folio": folio,
                "word": first_word,
                "line": first_line_text
            })
            
    return start_words

def check_grammar_frame(pages):
    # Frame: daiin [OBJ] qok- [SOURCE]
    # We look for the sequence: "daiin" ... "qok" ...
    # or similar patterns.
    
    matches = []
    
    for folio, lines in pages.items():
        full_text = []
        for loc in sorted(lines.keys(), key=lambda x: float(x.split('.')[-1]) if x.split('.')[-1].replace('+', '').isdigit() else 0):
            # Fix splitting logic
            full_text.extend([w for w in re.split(r'[.\s]', lines[loc]) if w])
            
        # Naive search in the stream of words
        for i in range(len(full_text)):
            word = full_text[i]
            
            # Check for daiin (8am) or similar
            if word in ['daiin', '8am', 'daiin.']:
                # Look ahead for qok (4oh)
                # Window of say 5 words
                window = full_text[i+1 : min(i+6, len(full_text))]
                for j, next_word in enumerate(window):
                    if next_word.startswith('qok') or next_word.startswith('4oh'):
                        matches.append({
                            "folio": folio,
                            "pattern": f"{word} {' '.join(window[:j+1])} ...",
                            "object": window[0] if j > 0 else "UNKNOWN"
                        })
                        
    return matches

def identify_descriptors(pages):
    # Look for 'dam' (red)
    dam_occurrences = []
    
    for folio, lines in pages.items():
        for loc, line in lines.items():
            # Fix splitting logic
            words = [w for w in re.split(r'[.\s]', line) if w]
            if 'dam' in words:
                dam_occurrences.append({
                    "folio": folio,
                    "loc": loc,
                    "context": line
                })
                
    return dam_occurrences

def generate_report(starts, frame_matches, dam_matches):
    report = "# Herbal Grammar Analysis Report\n\n"
    
    report += "## Task 1: Paragraph Starts\n"
    report += "Analyzed the first word of text blocks on pages f10r-f30r.\n\n"
    
    daiin_starts = [s for s in starts if 'daiin' in s['word'] or '8am' in s['word']]
    
    report += f"- **Total Pages Analyzed**: {len(starts)}\n"
    report += f"- **Starts with 'daiin' (Take)**: {len(daiin_starts)}\n"
    
    if len(daiin_starts) > 0:
        report += "  - Examples: " + ", ".join([s['folio'] for s in daiin_starts[:5]]) + "\n"
    else:
        report += "  - RESULT: No pages start with the imperative 'Take'. This suggests a Descriptive rather than Imperative style.\n"
        
    report += "\n### Top Start Words:\n"
    word_counts = Counter([s['word'] for s in starts])
    for word, count in word_counts.most_common(5):
        report += f"- `{word}`: {count}\n"
        
    report += "\n## Task 2: Grammar Frame Test\n"
    report += "Searching for `daiin [OBJ] qok- [SOURCE]` pattern.\n\n"
    
    if frame_matches:
        report += f"- **Matches Found**: {len(frame_matches)}\n"
        for m in frame_matches[:5]:
            report += f"- {m['folio']}: `{m['pattern']}`\n"
    else:
        report += "- **Matches Found**: 0\n"
        report += "- RESULT: The Recipe grammar frame does NOT appear in the Herbal section.\n"
        
    report += "\n## Task 3: Descriptors (Colors)\n"
    report += "Searching for `dam` (red/blood).\n\n"
    
    if dam_matches:
        report += f"- **Occurrences of 'dam'**: {len(dam_matches)}\n"
        for m in dam_matches:
            report += f"- {m['folio']} ({m['loc']}): `{m['context']}`\n"
    else:
        report += "- **Occurrences of 'dam'**: 0\n"
        
    return report

def main():
    print("Loading herbal pages (f10r-f30r)...")
    pages = get_herbal_pages()
    print(f"Loaded {len(pages)} pages.")
    
    print("Analyzing paragraph starts...")
    starts = analyze_paragraph_starts(pages)
    
    print("Checking grammar frames...")
    frame_matches = check_grammar_frame(pages)
    
    print("Identifying descriptors...")
    dam_matches = identify_descriptors(pages)
    
    print("Generating report...")
    report = generate_report(starts, frame_matches, dam_matches)
    
    with open(OUTPUT_REPORT, "w") as f:
        f.write(report)
        
    data = {
        "starts": starts,
        "frame_matches": frame_matches,
        "dam_matches": dam_matches
    }
    
    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Done. Results saved to {OUTPUT_REPORT} and {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

