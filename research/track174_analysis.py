import json
import re
import os
from collections import Counter

# Configuration
INPUT_EVA = 'data/eva_ivtff.txt'
INPUT_PARSED = 'results/parsed_text.json'
OUTPUT_TYPES = 'results/page_types.json'
OUTPUT_MAP = 'results/genre_map.md'
OUTPUT_SUMMARY = 'results/track-174-results_summary.md'

def load_ed_root_words():
    """Load words that have 'ed' as root from parsed_text.json"""
    print("Loading ed root words...")
    with open(INPUT_PARSED, 'r') as f:
        data = json.load(f)
    
    ed_words = set()
    for item in data:
        if item.get('root') == 'ed':
            ed_words.add(item['original'])
            
    print(f"Found {len(ed_words)} unique words with root 'ed'.")
    return ed_words

def parse_pages(filepath):
    """Parse pages from EVA file (H transcription)"""
    print("Parsing pages from EVA...")
    pages = {}
    current_page = None
    
    # Regex for page header
    page_pattern = re.compile(r"#\s*<(f\d+[rv])")
    
    with open(filepath, 'r') as f:
        for line in f:
            # Check for page header
            match = page_pattern.search(line)
            if match:
                current_page = match.group(1)
                if current_page not in pages:
                    pages[current_page] = []
                continue
            
            # Only process H transcription lines
            if ';H>' in line:
                parts = line.strip().split('\t')
                if len(parts) < 2:
                    parts = line.strip().split()
                    if len(parts) < 2:
                        continue
                    text = parts[-1]
                else:
                    text = parts[-1]
                
                # Split words
                words = re.split(r'[.!,-]', text)
                words = [w for w in words if w]
                
                if current_page:
                    pages[current_page].extend(words)
                    
    print(f"Parsed {len(pages)} pages.")
    return pages

def classify_pages(pages, ed_words):
    print("Classifying pages...")
    page_types = {}
    page_scores = {}
    
    for page_id, words in pages.items():
        if not words:
            continue
            
        count = len(words)
        if count < 10: # Skip empty/tiny pages
            continue
            
        n_y = 0
        n_dy = 0
        n_ed = 0
        n_o = 0 # Nouns (o-)
        
        for w in words:
            # Imperative (-y) vs Narrative (-dy)
            if w.endswith('dy'):
                n_dy += 1
            elif w.endswith('y'):
                n_y += 1
                
            # Process (ed root)
            if w in ed_words:
                n_ed += 1
            
            # Descriptive (o- nouns)
            if w.startswith('o'):
                n_o += 1
                
        # Normalize scores (per 100 words)
        score_y = (n_y / count) * 100
        score_dy = (n_dy / count) * 100
        score_ed = (n_ed / count) * 100
        score_o = (n_o / count) * 100
        
        # Classification Logic
        label = "Unknown"
        reason = ""
        
        # Revised Priorities
        # 1. Instructional: Process-heavy (ed) and Imperative (y > dy)
        # 2. Narrative: Narrative-heavy (dy > y)
        # 3. Descriptive: Noun-heavy (o)
        
        if score_ed > 1.0 and score_y > score_dy:
            label = "Instructional"
            reason = "Process (ed) + Imperative (y)"
        elif score_dy > score_y:
            label = "Narrative"
            reason = "Dominant Narrative (dy > y)"
        elif score_o > 20.0: # High Noun Density
            label = "Descriptive"
            reason = "High Noun Density (o)"
        elif score_dy > 10.0:
            label = "Narrative"
            reason = "Significant Narrative (dy)"
        else:
            label = "Descriptive"
            reason = "Default / Low Activity"
                
        page_types[page_id] = label
        page_scores[page_id] = {
            "y": round(score_y, 2),
            "dy": round(score_dy, 2),
            "ed": round(score_ed, 2),
            "o": round(score_o, 2),
            "count": count,
            "reason": reason
        }
        
    return page_types, page_scores

def generate_reports(page_types, page_scores):
    print("Generating reports...")
    
    # Save page types JSON
    with open(OUTPUT_TYPES, 'w') as f:
        json.dump(page_types, f, indent=2)
        
    # Generate Map (Markdown)
    sections = {
        "Herbal A": (1, 66),
        "Astro": (67, 73),
        "Bio": (75, 84),
        "Rosettes": (85, 86),
        "Herbal B": (87, 102),
        "Recipes": (103, 116)
    }
    
    def get_section(pid):
        # pid format f103r
        m = re.match(r'f(\d+)', pid)
        if m:
            num = int(m.group(1))
            for name, (start, end) in sections.items():
                if start <= num <= end:
                    return name
        return "Unknown"
        
    # Map content
    md_content = "# Voynich Manuscript Genre Map\n\n"
    md_content += "| Page | Section | Type | Scores (y / dy / ed / o) | Reason |\n"
    md_content += "|---|---|---|---|---|\n"
    
    # Sort pages naturally
    def sort_key(pid):
        m = re.match(r'f(\d+)([rv])', pid)
        if m:
            return int(m.group(1)) * 10 + (0 if m.group(2) == 'r' else 1)
        return 0
        
    sorted_pids = sorted(page_types.keys(), key=sort_key)
    
    summary_counts = Counter()
    section_counts = {s: Counter() for s in sections}
    section_counts["Unknown"] = Counter()
    
    for pid in sorted_pids:
        ptype = page_types[pid]
        scores = page_scores[pid]
        section = get_section(pid)
        
        summary_counts[ptype] += 1
        section_counts[section][ptype] += 1
        
        score_str = f"{scores['y']} / {scores['dy']} / {scores['ed']} / {scores['o']}"
        md_content += f"| {pid} | {section} | {ptype} | {score_str} | {scores['reason']} |\n"
        
    with open(OUTPUT_MAP, 'w') as f:
        f.write(md_content)
        
    # Summary Report
    summary_md = "# Text Type Classification Results (Task 174)\n\n"
    summary_md += "## Overview\n"
    summary_md += f"Classified {len(page_types)} pages.\n\n"
    summary_md += "### Distribution\n"
    for ptype, count in summary_counts.items():
        summary_md += f"- **{ptype}:** {count} pages\n"
        
    summary_md += "\n## Section Analysis\n"
    for sec in sorted(sections.keys()):
        if sum(section_counts[sec].values()) == 0: continue
        summary_md += f"### {sec}\n"
        total = sum(section_counts[sec].values())
        for ptype, count in section_counts[sec].items():
            pct = (count / total) * 100
            summary_md += f"- {ptype}: {count} ({pct:.1f}%)\n"
        summary_md += "\n"
        
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write(summary_md)

def main():
    ed_words = load_ed_root_words()
    pages = parse_pages(INPUT_EVA)
    types, scores = classify_pages(pages, ed_words)
    generate_reports(types, scores)
    print("Done.")

if __name__ == "__main__":
    main()
