import os
import re
import json
from collections import Counter

# Configuration
RAW_FILE = "voynich_raw.txt"
OUTPUT_JSON = "results/astronomical_candidates.json"
OUTPUT_REPORT = "results/track-306-results_summary.md"

def parse_raw_file(filepath):
    data = {}
    processed_count = 0
    target_count = 0
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                processed_count += 1
                line = line.strip()
                if not line or not line.startswith('<'):
                    continue
                
                match = re.match(r'<([^>]+)>(.*)', line)
                if match:
                    loc = match.group(1)
                    text = match.group(2).strip()
                    
                    # loc format: 67r1.1 or f67r1.1
                    # We need to check if it starts with 67..73 or f67..f73
                    
                    page_part = loc.split('.')[0]
                    
                    is_target = False
                    for i in range(67, 74):
                        if page_part.startswith(str(i)) or page_part.startswith(f"f{i}"):
                            is_target = True
                            break
                    
                    if is_target:
                        target_count += 1
                        # Replace dots with spaces
                        text_clean = text.replace('.', ' ')
                        words = [w.strip() for w in text_clean.split(' ') if w.strip() and w.strip() not in ['-', '=', ',']] 
                        
                        clean_words = []
                        for w in words:
                            w_clean = w.replace(',', '').replace('-', '').replace('=', '')
                            w_clean = w_clean.replace('!', '').replace('?', '').replace('*', '') 
                            if w_clean:
                                clean_words.append(w_clean)
                                
                        if clean_words: 
                            data[loc] = clean_words
                
        print(f"Processed {processed_count} lines.")
        print(f"Found {target_count} lines in target range (f67-f73).")

    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
    return data

def analyze_candidates(data):
    candidates = []
    star_patterns = []
    
    for loc, words in data.items():
        # 1. Label Identification: 1-2 word lines
        if 1 <= len(words) <= 2:
            candidates.append({
                "location": loc,
                "words": words,
                "type": "label_candidate"
            })
            
        # 2. Star Map Pattern
        for i, word in enumerate(words):
            is_star = False
            if word.endswith('y'):
                is_star = True
            if word.startswith('o'):
                is_star = True
            
            if is_star:
                star_patterns.append({
                    "location": loc,
                    "word": word,
                    "index": i,
                    "context": words
                })

    return candidates, star_patterns

def generate_report(candidates, star_patterns):
    with open(OUTPUT_JSON, 'w') as f:
        json.dump({"labels": candidates, "stars": star_patterns}, f, indent=2)
        
    # Generate markdown report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Track 306: Astronomical Deep Dive Results\n\n")
        
        f.write("## 1. Label Candidates (1-2 word lines)\n")
        f.write(f"Found {len(candidates)} candidates.\n\n")
        f.write("These are short lines (1-2 words) that might be labels for stars or months.\n\n")
        f.write("| Location | Words | Notes |\n")
        f.write("|---|---|---|\n")
        
        for cand in candidates[:100]: 
            f.write(f"| {cand['location']} | {', '.join(cand['words'])} | |\n")
        if len(candidates) > 100:
            f.write(f"| ... | ... | ({len(candidates)-100} more) |\n")
            
        f.write("\n## 2. Star Candidates (ending in -y or starting with o-)\n")
        f.write(f"Found {len(star_patterns)} occurrences.\n\n")
        
        star_counts = Counter([s['word'] for s in star_patterns])
        
        f.write("### Top 50 Potential Star Names\n")
        f.write("| Word | Count | Pattern |\n")
        f.write("|---|---|---|\n")
        for word, count in star_counts.most_common(50):
            pattern = []
            if word.endswith('y'): pattern.append("-y")
            if word.startswith('o'): pattern.append("o-")
            f.write(f"| {word} | {count} | {', '.join(pattern)} |\n")

        f.write("\n## 3. Coverage Impact\n")
        f.write("This analysis identifies potential labels and star names in the astronomical section (f67r-f73v).\n")
        f.write("Next steps: Compare these candidates with specific astronomical tables.\n")

if __name__ == "__main__":
    data = parse_raw_file(RAW_FILE)
    candidates, star_patterns = analyze_candidates(data)
    generate_report(candidates, star_patterns)
    print("Done.")
