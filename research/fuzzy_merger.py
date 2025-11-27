import json
import re
from collections import Counter

# Simple Levenshtein implementation
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def run_fuzzy_merger():
    print("Identifying fuzzy merges...")
    
    # Load Corpus
    with open("data/eva_ivtff.txt", "r") as f:
        text = f.read()
    
    words = re.findall(r"[a-z]+", text.lower())
    counts = Counter(words)
    
    hapax = [w for w, c in counts.items() if c == 1 and len(w) > 3]
    high_freq = [w for w, c in counts.items() if c > 50 and len(w) > 3]
    
    merges = []
    
    for h in hapax:
        for f in high_freq:
            if abs(len(h) - len(f)) > 1: continue
            
            dist = levenshtein(h, f)
            if dist == 1:
                merges.append({
                    "hapax": h,
                    "target": f,
                    "edit_distance": 1,
                    "type": "typo_candidate"
                })
                break # Found a match
                
    # Save
    with open("results/fuzzy_merges.json", "w") as f:
        json.dump(merges, f, indent=2)
        
    print(f"Identified {len(merges)} potential typos.")

if __name__ == "__main__":
    run_fuzzy_merger()
