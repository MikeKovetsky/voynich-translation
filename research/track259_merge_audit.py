import json
import os
import sys
import Levenshtein
import re
from collections import defaultdict

# Add current directory to path to import voynich_data
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import voynich_data

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def build_word_section_map():
    print("Building Word-Section Map...")
    word_sections = defaultdict(set)
    
    # Sections to scan
    sections = [
        'herbal_a', 'herbal_b', 'astronomical', 
        'biological', 'pharmaceutical', 'recipes'
    ]
    
    for section in sections:
        try:
            # Get all text for this section
            section_text = voynich_data.get_section_text(section)
            # section_text is {folio: {line: text}}
            
            for folio, lines in section_text.items():
                for line_text in lines.values():
                    # Clean and split
                    text_clean = re.sub(r'[!?<>@$\d]', '', line_text)
                    words = re.split(r'[.\-=,\s]', text_clean)
                    for w in words:
                        if w and len(w) > 1:
                            word_sections[w].add(section)
        except Exception as e:
            print(f"Warning: Could not process section {section}: {e}")
            
    return word_sections

def main():
    print("Starting Merge Audit (Track 259)...")
    
    # 1. Load Inputs
    dict_path = 'results/dictionary/dictionary_v13.json'
    morph_path = 'results/morphology_rules.json'
    
    print(f"Loading dictionary from {dict_path}...")
    master_dict = load_json(dict_path)
    if not master_dict:
        print("Error: Dictionary not found.")
        return

    print(f"Loading morphology from {morph_path}...")
    morph_rules = load_json(morph_path)
    suffixes = set(morph_rules.get('suffixes', [])) if morph_rules else set()
    
    entries = master_dict.get('entries', {})
    
    # 2. Build Section Map
    word_sections = build_word_section_map()
    print(f"Mapped sections for {len(word_sections)} words.")
    
    # 3. Identify Candidates
    # Anchors: High confidence (>= 0.8)
    # Unknowns: Low confidence (< 0.5 to be broader, or < 0.3 as in original)
    # The original script used < 0.3 for unknowns. I'll use < 0.5 to catch more potential merges.
    
    anchors = [k for k, v in entries.items() if v.get('confidence', 0) >= 0.8]
    unknowns = [k for k, v in entries.items() if v.get('confidence', 0) < 0.5]
    
    print(f"Anchors: {len(anchors)}, Unknowns: {len(unknowns)}")
    
    candidates = []
    
    # Optimization: Length buckets
    anchors_by_len = defaultdict(list)
    for a in anchors:
        anchors_by_len[len(a)].append(a)
        
    print("Finding fuzzy candidates (dist=1)...")
    for u in unknowns:
        if len(u) < 3: continue # Skip very short words
        
        u_len = len(u)
        # Check anchors with len = u_len, u_len-1, u_len+1
        potential_anchors = []
        potential_anchors.extend(anchors_by_len[u_len])
        potential_anchors.extend(anchors_by_len[u_len-1])
        potential_anchors.extend(anchors_by_len[u_len+1])
        
        for a in potential_anchors:
            dist = Levenshtein.distance(u, a)
            if dist == 1:
                candidates.append((u, a))
    
    print(f"Found {len(candidates)} candidates.")
    
    # 4. Audit Candidates
    safe_merges = []
    rejected_merges = []
    
    section_rejects = 0
    suffix_rejects = 0
    
    for u, a in candidates:
        reason = None
        
        # -- Section Check --
        u_sections = word_sections.get(u, set())
        a_sections = word_sections.get(a, set())
        
        # If disjoint and both present
        if u_sections and a_sections and u_sections.isdisjoint(a_sections):
            # Check for specific incompatibility: Astro vs Recipe
            # Or just generally disjoint domains might be risky.
            # Task says: "If A is only in Astro and B is only in Recipes -> REJECT"
            
            u_is_astro = 'astronomical' in u_sections and len(u_sections) == 1
            a_is_recipe = 'recipes' in a_sections and len(a_sections) == 1
            
            u_is_recipe = 'recipes' in u_sections and len(u_sections) == 1
            a_is_astro = 'astronomical' in a_sections and len(a_sections) == 1
            
            if (u_is_astro and a_is_recipe) or (u_is_recipe and a_is_astro):
                reason = f"Section Mismatch: {u}({list(u_sections)}) vs {a}({list(a_sections)})"
                section_rejects += 1
            
            # We can optionally be stricter and reject ANY disjoint set, 
            # but the prompt specifically highlights Astro vs Recipe. 
            # I'll stick to the specific instruction for rejection, 
            # maybe flag others as warnings? 
            # "prevent destructive merging... by checking their semantic context"
            # I'll add a generic disjoint warning but only reject on strong mismatch?
            # The instruction says "If A is only in Astro and B is only in Recipes -> REJECT".
            # I'll implement that strict rule.
        
        if not reason:
            # -- Grammar Check --
            # Check if difference is a suffix
            # Dist is 1.
            # Case 1: one is prefix of other
            if len(u) != len(a):
                longer = u if len(u) > len(a) else a
                shorter = a if len(u) > len(a) else u
                
                if longer.startswith(shorter):
                    diff = longer[len(shorter):]
                    if diff in suffixes:
                        reason = f"Suffix Conflict: {longer} = {shorter} + -{diff} (Known Suffix)"
                        suffix_rejects += 1
            
            # Case 2: Substitution (same length)
            # e.g. daiin vs daiir (n vs r). If both n and r are suffixes?
            # Task example is `daiin` vs `daiiny` (length diff).
            # It doesn't explicitly ask for substitution checks for suffixes, 
            # but "Does the 'error' look like a suffix?" implies length diff usually.
        
        if reason:
            rejected_merges.append({
                "unknown": u,
                "anchor": a,
                "reason": reason,
                "u_sections": list(u_sections),
                "a_sections": list(a_sections)
            })
        else:
            safe_merges.append({
                "unknown": u,
                "anchor": a,
                "type": "fuzzy_match_v1",
                "confidence_penalty": 0.1
            })
            
    print(f"Audit Complete.")
    print(f"Safe Merges: {len(safe_merges)}")
    print(f"Rejected: {len(rejected_merges)} (Section: {section_rejects}, Suffix: {suffix_rejects})")
    
    # 5. Outputs
    save_json(safe_merges, 'results/safe_merges.json')
    
    # Generate Summary
    summary = f"""# Track 259: Merge Context Audit Results

## Overview
- **Input Dictionary**: {dict_path}
- **Total Candidates Identified**: {len(candidates)}
- **Safe Merges Approved**: {len(safe_merges)}
- **Merges Rejected**: {len(rejected_merges)}

## Rejection Breakdown
- **Section Mismatches (Astro vs Recipe)**: {section_rejects}
- **Suffix Conflicts (Root + Suffix)**: {suffix_rejects}

## Methodology
1. **Candidate Identification**: Found pairs with Levenshtein distance = 1 (Unknown vs Anchor).
2. **Section Audit**: Checked for mutually exclusive sections (specifically Astronomical vs Recipes).
3. **Grammar Audit**: Checked if the difference between words corresponds to a known suffix (from `morphology_rules.json`).

## Examples of Rejected Merges
"""
    
    # Add some examples
    for i, r in enumerate(rejected_merges[:10]):
        summary += f"- **{r['unknown']}** vs **{r['anchor']}**: {r['reason']}\n"
        
    with open('results/track-259-results_summary.md', 'w') as f:
        f.write(summary)
        
    print("Summary written to results/track-259-results_summary.md")

if __name__ == "__main__":
    main()
