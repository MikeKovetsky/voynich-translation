import json
import re
import collections
import os

def load_vocab(path):
    with open(path, 'r') as f:
        text = f.read()
    words = []
    for line in text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        # Filter for Takahashi (H) transcription to avoid duplicates
        if ';H>' not in line:
            continue

        clean_line = re.sub(r'<[^>]+>', '', line)
        # Replace IVTFF delimiters with spaces
        clean_line = re.sub(r'[.,!=]', ' ', clean_line)
        clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
        words.extend(clean_line.split())
    return words

def load_rules(path):
    with open(path, 'r') as f:
        return json.load(f)

def recursive_strip(word, prefixes, suffixes):
    # Heuristic: Always strip longest valid affix first
    # Keep stripping until no affix matches or root is too short (<2 chars)
    
    current_word = word
    found_prefixes = []
    found_suffixes = []
    
    changed = True
    while changed:
        changed = False
        if len(current_word) <= 2:
            break
            
        # Try prefix
        best_p = ""
        for p in prefixes:
            if current_word.startswith(p) and len(p) > len(best_p):
                # Check if remaining is valid (heuristic)
                rem = current_word[len(p):]
                if len(rem) >= 2:
                    best_p = p
        
        if best_p:
            found_prefixes.append(best_p)
            current_word = current_word[len(best_p):]
            changed = True
            continue # Restart loop to handle stacked prefixes like qo-k-
            
        # Try suffix
        best_s = ""
        for s in suffixes:
            if current_word.endswith(s) and len(s) > len(best_s):
                rem = current_word[:len(current_word)-len(s)]
                if len(rem) >= 2:
                    best_s = s
                    
        if best_s:
            found_suffixes.insert(0, best_s) # Insert at start to maintain order
            current_word = current_word[:len(current_word)-len(best_s)]
            changed = True
            
    return {
        "original": word,
        "prefix": found_prefixes,
        "root": current_word,
        "suffix": found_suffixes
    }

def main():
    print("Starting Morphological Parser...")
    text_path = 'data/eva_ivtff.txt'
    rules_path = 'results/morphology_rules.json'
    
    if not os.path.exists(text_path) or not os.path.exists(rules_path):
        print("Files not found.")
        return
        
    words = load_vocab(text_path)
    rules = load_rules(rules_path)
    
    # Sort rules by length desc for greedy match
    prefixes = sorted(rules['prefixes'], key=len, reverse=True)
    suffixes = sorted(rules['suffixes'], key=len, reverse=True)
    
    parsed_data = []
    root_counts = collections.Counter()
    prefix_counts = collections.Counter()
    
    for w in words:
        parsed = recursive_strip(w, prefixes, suffixes)
        parsed_data.append(parsed)
        root_counts[parsed['root']] += 1
        for p in parsed['prefix']:
            prefix_counts[p] += 1
            
    # Save Results
    with open('results/parsed_text.json', 'w') as f:
        json.dump(parsed_data, f, indent=2)
        
    print(f"Processed {len(words)} words.")
    print(f"Unique Roots found: {len(root_counts)}")
    print("Top 10 Roots:")
    for r, c in root_counts.most_common(10):
        print(f"- {r}: {c}")

    print("\nTop 10 Prefixes:")
    for p, c in prefix_counts.most_common(10):
        print(f"- {p}: {c}")

if __name__ == "__main__":
    main()
