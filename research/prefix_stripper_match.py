import csv
import os
from collections import Counter

# 1. Load Unique Keywords
KEYWORDS_FILE = "results/unique_page_keywords.csv"
SHERWOOD_FILE = "data/external_corpora/sherwood_plant_mapping.csv"
OUTPUT_FILE = "results/stripped_matches.csv"

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

def strip_prefixes(word):
    variants = [word]
    
    # Prefix o-
    if word.startswith('o'): variants.append(word[1:])
    # Prefix qo-
    if word.startswith('qo'): variants.append(word[2:])
    # Prefix y-
    if word.startswith('y'): variants.append(word[1:])
    # Prefix d-
    if word.startswith('d'): variants.append(word[1:])
    # Prefix l-
    if word.startswith('l'): variants.append(word[1:])
    
    # Suffixes
    if word.endswith('y'): variants.append(word[:-1])
    if word.endswith('dy'): variants.append(word[:-2])
    if word.endswith('ol'): variants.append(word[:-2])
    
    # Prefix + Suffix combo (e.g. qo-k-edy -> k)
    if word.startswith('qo') and word.endswith('y'): variants.append(word[2:-1])
    
    return list(set([v for v in variants if len(v) >= 3]))

def main():
    if not os.path.exists(KEYWORDS_FILE):
        print(f"Error: {KEYWORDS_FILE} not found.")
        return

    # Load Sherwood Map for Latin/Common names
    folio_names = {}
    with open(SHERWOOD_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 3:
                # Simplify Folio
                f_clean = row[0].replace(" ", "").lower()
                if not f_clean.startswith('f'): f_clean = 'f' + f_clean
                if 'v' in f_clean: f_clean = f_clean[:f_clean.index('v')+1]
                if 'r' in f_clean: f_clean = f_clean[:f_clean.index('r')+1]
                
                folio_names[f_clean] = {
                    'common': row[1],
                    'latin': row[2]
                }

    matches = []
    
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            folio = row['Folio']
            # Clean folio key
            f_key = folio
            if 'v' in f_key and len(f_key) > f_key.index('v') + 1: f_key = f_key[:f_key.index('v')+1]
            if 'r' in f_key and len(f_key) > f_key.index('r') + 1: f_key = f_key[:f_key.index('r')+1]
            
            target_info = folio_names.get(f_key)
            if not target_info: continue
            
            targets = [target_info['latin']]
            targets.extend(target_info['common'].split('/'))
            
            # Clean targets
            clean_targets = []
            for t in targets:
                t = t.strip().split()[0] # Take first word of latin name (e.g. Pisum from Pisum sativum)
                clean_targets.append(t.lower())
            
            # Check Keywords
            for kw_key in ['Keyword 1', 'Keyword 2', 'Keyword 3']:
                word = row[kw_key]
                if not word: continue
                
                # Strip Prefixes
                roots = strip_prefixes(word)
                
                for root in roots:
                    for target in clean_targets:
                        if len(target) < 3: continue
                        
                        ratio = levenshtein_ratio(root, target)
                        if ratio > 0.65: # Strict
                            matches.append([
                                folio,
                                word,
                                root,
                                target,
                                f"{ratio:.2f}"
                            ])

    # Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['folio', 'voynich_word', 'stripped_root', 'target_word', 'similarity'])
        writer.writerows(matches)
        
    print(f"Found {len(matches)} stripped root matches.")

if __name__ == "__main__":
    main()
