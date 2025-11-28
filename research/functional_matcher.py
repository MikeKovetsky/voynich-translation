import csv
import os
from collections import Counter
from research.voynich_data import get_folio_text

# 1. Load Sherwood Mapping
SHERWOOD_FILE = "data/external_corpora/sherwood_plant_mapping.csv"
OUTPUT_FILE = "results/functional_matches.csv"

# Medical Uses Dictionary (Proof of Concept)
# Latin/English functional terms
FUNCTIONAL_TERMS = {
    "stomach": ["stomachus", "venter", "digest", "colic", "gut"],
    "head": ["caput", "cephalo", "brain", "migraine", "headache"],
    "sleep": ["somnus", "dorm", "hypno", "sleep", "narcotic"],
    "pain": ["dolor", "analgesic", "pain", "ache"],
    "skin": ["cutis", "derm", "wound", "ulcer", "burn"],
    "women": ["matrix", "womb", "uterus", "women", "menses"],
    "eye": ["oculus", "ophthalmia", "sight", "blind"],
    "liver": ["hepar", "liver", "bile", "jaundice"],
    "lung": ["pulmo", "lung", "breath", "cough", "asthma"]
}

# Plant Uses Map (Simplified)
# In production, this would come from a DB
PLANT_USES = {
    "cannabis": ["pain", "sleep", "head"],
    "poppy": ["sleep", "pain"],
    "balm": ["stomach", "head", "skin"],
    "fennel": ["stomach", "eye", "women"],
    "sage": ["head", "stomach", "skin"],
    "mint": ["stomach", "head"],
    "sorrel": ["stomach", "skin"],
    "plantago": ["skin", "wound"],
    "aloe": ["skin", "burn", "stomach"]
}

def levenshtein_ratio(s1, s2):
    if not s1 or not s2: return 0
    rows = len(s1)+1
    cols = len(s2)+1
    dist = [[0 for x in range(cols)] for x in range(rows)]
    for i in range(1, rows): dist[i][0] = i
    for i in range(1, cols): dist[0][i] = i
    for col in range(1, cols):
        for row in range(1, rows):
            if s1[row-1] == s2[col-1]: cost = 0
            else: cost = 1
            dist[row][col] = min(dist[row-1][col] + 1, dist[row][col-1] + 1, dist[row-1][col-1] + cost)
    return 1 - (dist[rows-1][cols-1] / max(len(s1), len(s2)))

def main():
    if not os.path.exists("results/unique_page_keywords.csv"):
        print("Error: Keywords file not found.")
        return

    matches = []
    
    print("Scanning Functional Matches...")
    with open("results/unique_page_keywords.csv", 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            plant_raw = row['Plant Name'].lower()
            
            # Find plant use
            uses = []
            for p, u in PLANT_USES.items():
                if p in plant_raw:
                    uses.extend(u)
            
            if not uses: continue
            
            # Check Keywords against Use Terms
            for kw_key in ['Keyword 1', 'Keyword 2', 'Keyword 3']:
                word = row[kw_key]
                if not word: continue
                
                # Check match against Functional Terms for these uses
                for use in set(uses):
                    targets = FUNCTIONAL_TERMS.get(use, [])
                    for target in targets:
                        if len(target) < 3: continue
                        # Check full word and root
                        roots = [word]
                        if word.startswith('o'): roots.append(word[1:])
                        if word.startswith('qo'): roots.append(word[2:])
                        
                        for r in roots:
                            ratio = levenshtein_ratio(r, target)
                            if ratio > 0.6:
                                matches.append([
                                    row['Folio'],
                                    word,
                                    r,
                                    use,
                                    target,
                                    f"{ratio:.2f}"
                                ])

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['folio', 'voynich_word', 'root', 'function', 'latin_term', 'similarity'])
        writer.writerows(matches)
        
    print(f"Found {len(matches)} functional matches.")

if __name__ == "__main__":
    main()
