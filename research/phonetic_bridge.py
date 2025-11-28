
import json
import csv
import os

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

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

def load_dictionary(path):
    if not os.path.exists(path):
        print(f"Dictionary not found at {path}")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    words = []
    for key in data.get("entries", {}):
        clean_key = key.replace("!", "").strip()
        if clean_key:
            words.append(clean_key)
    return list(set(words)) # Unique words

def load_latin_corpus(path):
    if not os.path.exists(path):
        print(f"Latin corpus not found at {path}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def load_abbreviations(path):
    if not os.path.exists(path):
        print(f"Abbreviations not found at {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Paths
    dict_path = "results/dictionary/master_dictionary_v20.json"
    latin_path = "data/external_corpora/latin_medical.txt"
    abbrev_path = "data/external_corpora/abbreviations.json"
    output_csv = "results/phonetic_candidates.csv"

    # Load Data
    print("Loading data...")
    voynich_words = load_dictionary(dict_path)
    latin_words = load_latin_corpus(latin_path)
    abbreviations = load_abbreviations(abbrev_path)

    # Expand Latin words with abbreviations? 
    # Or simply treat abbreviations as valid target "words" (e.g. 'p' matches Voynich 'p')
    # The task says: "Does Voynich `air` match Latin `aer` or `aur`?"
    # And lists abbreviations separately. I will add abbreviations as potential targets.
    
    targets = {} # target_word -> type (Latin or Abbreviation)
    for word in latin_words:
        targets[word] = "Latin"
    
    for abbr, expansions in abbreviations.items():
        # Add the abbreviation itself as a target
        targets[abbr] = f"Abbrev ({'/'.join(expansions)})"
        # Also add expansions? Maybe not, expansions are usually full latin words already.

    print(f"Loaded {len(voynich_words)} Voynich words and {len(targets)} targets.")

    results = []

    # Fuzzy Match
    print("Running fuzzy match...")
    # Heuristic: Only match if lengths are similar (within 2 chars)
    # Only check if distance is small relative to length.
    
    count = 0
    for v_word in voynich_words:
        # Skip very short voynich words for fuzzy matching against long latin words
        # But allow short ones to match abbreviations.
        
        for t_word, t_type in targets.items():
            if abs(len(v_word) - len(t_word)) > 2:
                continue
            
            dist = levenshtein_distance(v_word, t_word)
            
            # Match criteria
            is_match = False
            if len(v_word) <= 3:
                if dist == 0: is_match = True # Exact match for short words
                elif dist == 1 and len(v_word) > 1: is_match = True # 1 char diff allowed for len 2-3? Maybe too loose.
            else:
                if dist <= 1: is_match = True
                elif dist <= 2 and len(v_word) >= 5: is_match = True
            
            if is_match:
                similarity = 1.0 - (dist / max(len(v_word), len(t_word)))
                results.append({
                    "voynich_word": v_word,
                    "target_word": t_word,
                    "target_type": t_type,
                    "distance": dist,
                    "similarity": round(similarity, 2)
                })
        
        count += 1
        if count % 1000 == 0:
            print(f"Processed {count} Voynich words...")

    # Sort by similarity (descending) and then Voynich word
    results.sort(key=lambda x: (-x["similarity"], x["voynich_word"]))

    # Write results
    print(f"Found {len(results)} candidates. Writing to {output_csv}...")
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["voynich_word", "target_word", "target_type", "distance", "similarity"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("Done.")

if __name__ == "__main__":
    main()
