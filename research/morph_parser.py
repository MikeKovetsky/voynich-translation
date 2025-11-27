import json
import csv
import re
from collections import Counter
import os

# Configuration
INPUT_TEXT = "data/eva_ivtff.txt"
RULES_FILE = "results/morphology_rules.json"
OUTPUT_JSON = "results/parsed_text.json"
OUTPUT_CSV = "results/root_frequency.csv"

def load_rules():
    if not os.path.exists(RULES_FILE):
        print(f"Error: Rules file {RULES_FILE} not found.")
        return [], []
    
    with open(RULES_FILE, 'r') as f:
        data = json.load(f)
        
    prefixes = data.get("prefixes", [])
    suffixes = data.get("suffixes", [])
    
    # Sort by length descending to ensure greedy matching (longest match first)
    prefixes.sort(key=len, reverse=True)
    suffixes.sort(key=len, reverse=True)
    
    return prefixes, suffixes

def clean_text(text):
    # Remove comments inside the line (if any, though usually # starts a line)
    # Remove {...} and <...> tags
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'<.*?>', '', text)
    # Remove other special markers like $, %, etc. if they are not part of words
    # But be careful not to remove ! or ? which are used in EVA for uncertain chars.
    # Standard EVA uses lowercase.
    # We'll allow [a-z0-9!*?]+
    return text

def parse_line(line_content, prefixes, suffixes):
    # Clean the content first
    cleaned_content = clean_text(line_content)
    
    # Replace . with space and split
    words = cleaned_content.replace('.', ' ').split()
    parsed_words = []
    
    for word in words:
        word = word.strip()
        if not word:
            continue
            
        # Skip 'words' that are just punctuation marks or non-EVA symbols
        # valid EVA chars are roughly a-z, 0-9, !, *, ?, -, '
        # Allowing !, *, ? as part of words or uncertainty markers
        if not re.match(r'^[a-z0-9!*?\-\']+$', word):
             continue
        
        # Skip words that are just punctuation
        if all(char in "!?,.*-'" for char in word):
             continue

        original = word
        current = word
        found_prefixes = []
        found_suffixes = []
        
        # Recursive Stripping of Prefixes
        while True:
            matched = False
            for p in prefixes:
                if current.startswith(p):
                    found_prefixes.append(p)
                    current = current[len(p):]
                    matched = True
                    break # Restart with the new current string (greedy recursive)
            if not matched:
                break
                
        # Recursive Stripping of Suffixes
        while True:
            matched = False
            for s in suffixes:
                if current.endswith(s):
                    found_suffixes.insert(0, s) 
                    current = current[:-len(s)]
                    matched = True
                    break 
            if not matched:
                break
        
        parsed_words.append({
            "original": original,
            "prefix": found_prefixes,
            "root": current,
            "suffix": found_suffixes
        })
        
    return parsed_words

def main():
    prefixes, suffixes = load_rules()
    print(f"Loaded {len(prefixes)} prefixes and {len(suffixes)} suffixes.")
    
    parsed_data = []
    root_counter = Counter()
    prefix_counter = Counter()
    suffix_counter = Counter()
    
    if not os.path.exists(INPUT_TEXT):
        print(f"Error: Input file {INPUT_TEXT} not found.")
        return

    print("Processing text...")
    processed_lines = 0
    with open(INPUT_TEXT, 'r') as f:
        for line in f:
            line = line.strip()
            # Filter for H transcription (Stolfi/Hybrid)
            if ";H>" in line:
                # Format: <f1r.1;H>       word1.word2...
                parts = line.split('>', 1)
                if len(parts) == 2:
                    line_id = parts[0] + '>'
                    content = parts[1].strip()
                    
                    parsed_line_words = parse_line(content, prefixes, suffixes)
                    
                    if parsed_line_words:
                        parsed_data.append({
                            "id": line_id,
                            "words": parsed_line_words
                        })
                        
                        for pw in parsed_line_words:
                            root = pw["root"]
                            if not root:
                                root = "[EMPTY]"
                            root_counter[root] += 1
                            for p in pw["prefix"]:
                                prefix_counter[p] += 1
                            for s in pw["suffix"]:
                                suffix_counter[s] += 1
                        
                        processed_lines += 1

    print(f"Processed {processed_lines} lines.")
    
    # Output JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(parsed_data, f, indent=2)
    print(f"Saved parsed text to {OUTPUT_JSON}")
    
    # Output CSV (Root Frequency)
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "root", "frequency"])
        for rank, (root, freq) in enumerate(root_counter.most_common(), 1):
            writer.writerow([rank, root, freq])
    print(f"Saved root frequencies to {OUTPUT_CSV}")

    # Optional: Print top stats
    print("\nTop 10 Roots:")
    for root, count in root_counter.most_common(10):
        print(f"{root}: {count}")
        
    print("\nTop 5 Prefixes:")
    for p, count in prefix_counter.most_common(5):
        print(f"{p}: {count}")

    print("\nTop 5 Suffixes:")
    for s, count in suffix_counter.most_common(5):
        print(f"{s}: {count}")

if __name__ == "__main__":
    main()
