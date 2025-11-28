import json
import math
import os
import re
from collections import Counter

# Configuration
INPUT_TEXT = "data/eva_ivtff.txt"
RULES_FILE = "results/morphology_rules.json"
ENGLISH_TEXT = "results/final_report_v10.md" # Use the report as English sample
OUTPUT_REPORT = "results/entropy_report.md"

def load_rules():
    if not os.path.exists(RULES_FILE):
        print(f"Error: Rules file {RULES_FILE} not found.")
        return [], []
    
    with open(RULES_FILE, 'r') as f:
        data = json.load(f)
        
    prefixes = data.get("prefixes", [])
    suffixes = data.get("suffixes", [])
    
    # Sort by length descending to ensure greedy matching
    prefixes.sort(key=len, reverse=True)
    suffixes.sort(key=len, reverse=True)
    
    return prefixes, suffixes

def clean_text(text):
    text = re.sub(r'\{.*?\}', '', text)
    text = re.sub(r'<.*?>', '', text)
    return text

def parse_voynich_word(word, prefixes, suffixes):
    # Simple recursive stripping based on morph_parser.py
    original = word
    current = word
    found_prefixes = []
    found_suffixes = []
    
    # Strip Prefixes
    while True:
        matched = False
        for p in prefixes:
            if current.startswith(p):
                found_prefixes.append(p)
                current = current[len(p):]
                matched = True
                break
        if not matched:
            break
            
    # Strip Suffixes
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
            
    return current, found_prefixes, found_suffixes

def parse_english_word(word):
    # Simple heuristic for English
    suffixes = ['tion', 'ing', 'ed', 'ly', 'er', 'est', 's']
    word = word.lower().strip('.,;:"\'()[]{}')
    if not word.isalpha():
        return None, []
        
    found_suffixes = []
    root = word
    
    # Only strip one suffix for simplicity in English (or iterate)
    for s in suffixes:
        if root.endswith(s) and len(root) > len(s) + 2: # Ensure root is long enough
            found_suffixes.append(s)
            root = root[:-len(s)]
            break
            
    return root, found_suffixes

def calculate_entropy(tokens):
    if not tokens:
        return 0.0
    
    counts = Counter(tokens)
    total = sum(counts.values())
    entropy = 0.0
    
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
        
    return entropy

def main():
    # 1. Load Rules
    prefixes, suffixes = load_rules()
    print(f"Loaded {len(prefixes)} prefixes and {len(suffixes)} suffixes.")
    
    # 2. Process Voynich
    voynich_roots = []
    voynich_suffixes = []
    voynich_prefixes = []
    
    print(f"Processing Voynich text: {INPUT_TEXT}")
    with open(INPUT_TEXT, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Use H transcription (High confidence / Stolfi)
            if ";H>" in line:
                parts = line.split('>', 1)
                if len(parts) == 2:
                    content = clean_text(parts[1])
                    words = content.replace('.', ' ').split()
                    
                    for w in words:
                        w = w.strip()
                        if not w or not re.match(r'^[a-z0-9!*?\-\']+$', w):
                            continue
                        
                        root, p_list, s_list = parse_voynich_word(w, prefixes, suffixes)
                        
                        if root:
                            voynich_roots.append(root)
                        voynich_prefixes.extend(p_list)
                        voynich_suffixes.extend(s_list)

    # 3. Process English (Control)
    english_roots = []
    english_suffixes = []
    
    print(f"Processing English text: {ENGLISH_TEXT}")
    if os.path.exists(ENGLISH_TEXT):
        with open(ENGLISH_TEXT, 'r') as f:
            content = f.read()
            words = content.split()
            for w in words:
                root, s_list = parse_english_word(w)
                if root:
                    english_roots.append(root)
                    english_suffixes.extend(s_list)
    else:
        print("English text not found, skipping control.")

    # 4. Calculate Entropies
    h_v_root = calculate_entropy(voynich_roots)
    h_v_suffix = calculate_entropy(voynich_suffixes)
    h_v_prefix = calculate_entropy(voynich_prefixes)
    
    h_e_root = calculate_entropy(english_roots)
    h_e_suffix = calculate_entropy(english_suffixes)
    
    # 5. Generate Report
    print("Generating Report...")
    
    report = f"""# Entropy Analysis Report
    
**Date:** 2025-11-27
**Input:** `{INPUT_TEXT}`
**Script:** `research/entropy_check.py`

## 1. Voynich Entropy (Morphology)
Using standard morphology rules (prefixes/suffixes from `results/morphology_rules.json`).

| Component | Count | Unique | Entropy (Bits) |
|---|---|---|---|
| **Roots** | {len(voynich_roots)} | {len(set(voynich_roots))} | **{h_v_root:.4f}** |
| **Suffixes** | {len(voynich_suffixes)} | {len(set(voynich_suffixes))} | **{h_v_suffix:.4f}** |
| **Prefixes** | {len(voynich_prefixes)} | {len(set(voynich_prefixes))} | **{h_v_prefix:.4f}** |

**Ratio (Root / Suffix):** {h_v_root / h_v_suffix if h_v_suffix else 0:.2f}

## 2. English Control (Comparison)
Sample text: `{ENGLISH_TEXT}` (Final Report)
Simple stripping of (-s, -ed, -ing, -ly, -tion, -er, -est).

| Component | Count | Unique | Entropy (Bits) |
|---|---|---|---|
| **Roots** | {len(english_roots)} | {len(set(english_roots))} | **{h_e_root:.4f}** |
| **Suffixes** | {len(english_suffixes)} | {len(set(english_suffixes))} | **{h_e_suffix:.4f}** |

**Ratio (Root / Suffix):** {h_e_root / h_e_suffix if h_e_suffix else 0:.2f}

## 3. Conclusion
- **Hypothesis:** Roots should have High Entropy (Open Class), Suffixes should have Low Entropy (Closed Class).
- **Voynich Result:** The Root entropy is {h_v_root:.2f}, and Suffix entropy is {h_v_suffix:.2f}.
- **Interpretation:** 
  - If Root Entropy >> Suffix Entropy, the morphology model is likely correct (Suffixes are grammatical markers).
  - If Root Entropy is close to Suffix Entropy, the "Suffixes" might be part of the root (splitting is wrong).

"""
    
    # Add interpretation logic
    if h_v_suffix > 0 and (h_v_root / h_v_suffix) > 1.5:
        report += "**VERDICT: SUPPORTS HYPOTHESIS.** The high entropy gap suggests 'Root' and 'Suffix' function as distinct Open vs Closed classes, typical of natural language.\n"
    else:
        report += "**VERDICT: INCONCLUSIVE / WEAK.** The entropy gap is small. The 'Suffixes' might carry too much information to be purely grammatical, or the list of suffixes is too broad.\n"

    with open(OUTPUT_REPORT, 'w') as f:
        f.write(report)
        
    print(f"Report saved to {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
