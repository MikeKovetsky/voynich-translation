import csv
import os
import requests
from collections import Counter

# 1. Load Unique Keywords
KEYWORDS_FILE = "results/unique_page_keywords.csv"
OUTPUT_FILE = "results/multilang_matches.csv"

# Simplified Multilingual Dictionary (Proof of Concept)
# In a real scenario, we would load a massive JSON or query an API
PLANT_DICT = {
    "cannabis": {
        "latin": "cannabis",
        "hebrew": "kaneh",
        "arabic": "qunnab",
        "german": "hanf",
        "italian": "canapa",
        "greek": "kannabis"
    },
    "poppy": {
        "latin": "papaver",
        "hebrew": "pereg",
        "arabic": "khashkhash",
        "german": "mohn",
        "italian": "papavero",
        "greek": "mekon"
    },
    "balm": {
        "latin": "melissa",
        "hebrew": "melissa",
        "arabic": "taranjan",
        "german": "melisse",
        "italian": "melissa",
        "greek": "melissophyllon"
    },
    "fennel": {
        "latin": "foeniculum",
        "hebrew": "shumar",
        "arabic": "shamar",
        "german": "fenchel",
        "italian": "finocchio",
        "greek": "marathron"
    },
    "clove": {
        "latin": "caryophyllus",
        "hebrew": "tziporen",
        "arabic": "qaranful",
        "german": "nelke",
        "italian": "garofano",
        "greek": "karyophyllon"
    }
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

def normalize(text):
    return "".join([c for c in text.lower() if c.isalpha()])

def main():
    if not os.path.exists(KEYWORDS_FILE):
        print(f"Error: {KEYWORDS_FILE} not found.")
        return

    keywords = []
    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract the plant name (simplify)
            plant_raw = row['Plant Name'].lower()
            plant_key = None
            for k in PLANT_DICT:
                if k in plant_raw:
                    plant_key = k
                    break
            
            if plant_key:
                keywords.append({
                    'folio': row['Folio'],
                    'plant': plant_key,
                    'kw1': row['Keyword 1'],
                    'kw2': row['Keyword 2'],
                    'kw3': row['Keyword 3']
                })

    matches = []
    
    print(f"Scanning {len(keywords)} identified plants against 5 languages...")
    
    for item in keywords:
        plant = item['plant']
        targets = PLANT_DICT[plant]
        
        for kw_key in ['kw1', 'kw2', 'kw3']:
            word = item[kw_key]
            if not word: continue
            
            # Check against all languages
            for lang, target_word in targets.items():
                # Normalize
                w_norm = normalize(word)
                t_norm = normalize(target_word)
                
                if len(w_norm) < 3 or len(t_norm) < 3: continue
                
                ratio = levenshtein_ratio(w_norm, t_norm)
                
                # High threshold for "Codebreaking"
                if ratio > 0.6:
                    matches.append([
                        item['folio'],
                        word,
                        plant,
                        lang,
                        target_word,
                        f"{ratio:.2f}"
                    ])

    # Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['folio', 'voynich_word', 'plant', 'language', 'target_word', 'similarity'])
        writer.writerows(matches)
        
    print(f"Found {len(matches)} potential language matches.")

if __name__ == "__main__":
    main()
