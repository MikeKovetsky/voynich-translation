import os
import csv
from collections import Counter
from research.voynich_data import get_folio_text
from research.eva_to_ava import to_ava

OUTPUT_FILE = "results/sherwood_falsification.md"

# Sherwood's Claims
CLAIMS = [
    {"folio": "f4r", "plant": "Sumac", "target": "sumac", "anagram": "ccamus"},
    {"folio": "f37v", "plant": "Pimpernel", "target": "corcoro", "anagram": "orcocor"},
    {"folio": "f2v", "plant": "Water Lily", "target": "ninfea", "anagram": "ninfea"}, # Italian for Water Lily
]

# Controls (False Targets)
CONTROLS = ["banana", "pizza", "gelato", "toscana", "milano"]

def is_anagram_in_text(target, text_words):
    """
    Check if 'target' can be formed by:
    1. A single word in the text (Exact Anagram)
    2. Two adjacent words combined (Split Anagram)
    """
    target_counts = Counter(target)
    target_len = len(target)
    
    # 1. Single Words
    for word in text_words:
        if len(word) == target_len and Counter(word) == target_counts:
            return f"Single: {word}"
            
    # 2. Adjacent Words (Sherwood allows splitting)
    for i in range(len(text_words) - 1):
        combined = text_words[i] + text_words[i+1]
        # Combined might be longer than target, check subset?
        # Sherwood says "split into two parts". 
        # Let's check if combined == target (strict split)
        if len(combined) == target_len and Counter(combined) == target_counts:
            return f"Split: {text_words[i]}+{text_words[i+1]}"
            
        # Loose split: does the combined string CONTAIN the target?
        # "ccam us" -> "ccamus".
        if len(combined) >= target_len:
             # Check if we can form target from combined
             combined_counts = Counter(combined)
             if all(combined_counts[c] >= target_counts[c] for c in target_counts):
                 return f"Loose Split: {text_words[i]}+{text_words[i+1]}"

    return None

def main():
    results = []
    
    for claim in CLAIMS:
        folio = claim['folio']
        target = claim['target']
        
        # Get AVA Text
        text_map = get_folio_text(folio)
        if not text_map:
            results.append(f"### {folio}: Text Not Found\n")
            continue
            
        full_eva = " ".join(text_map.values())
        full_ava = to_ava(full_eva)
        ava_words = full_ava.split()
        
        results.append(f"### Folio {folio} ({claim['plant']})\n")
        results.append(f"- **Target:** `{target}`\n")
        
        # Test Claim
        match = is_anagram_in_text(target, ava_words)
        if match:
            results.append(f"- **Result:** ✅ FOUND ({match})\n")
        else:
            results.append(f"- **Result:** ❌ NOT FOUND\n")
            
        # Test Controls (Falsification)
        results.append("- **Control Tests:**\n")
        for ctrl in CONTROLS:
            ctrl_match = is_anagram_in_text(ctrl, ava_words)
            if ctrl_match:
                results.append(f"  - `{ctrl}`: ⚠️ FOUND ({ctrl_match}) - False Positive?\n")
            else:
                results.append(f"  - `{ctrl}`: ✅ Not Found\n")
        
        results.append("\n---\n")

    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Sherwood Hypothesis Validation\n\n")
        f.write("Testing if claimed Italian anagrams appear in AVA-converted text.\n\n")
        f.writelines(results)
        
    print(f"Validation complete. See {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
