import json
import csv
import re
import os

# Configuration
INPUT_DICTIONARY = "results/dictionary/dictionary_v13.json"
INPUT_SYNTAX = "results/syntax_map_v1.json"
INPUT_ABBREV = "results/abbreviation_patterns.json"
INPUT_MEDIEVAL = "results/medieval_validation.json"
INPUT_ROMANCE = "results/proto_romance_analysis.json"
OUTPUT_FILE = "results/etymology_candidates.csv"

SUFFIXES = ["y", "ol", "dy", "9", "89", "am", "oe", "ay"] # Added from abbreviation patterns

def load_json(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found.")
        return None
    with open(path, 'r') as f:
        return json.load(f)

def extract_skeleton(word):
    # Simple skeleton extraction: remove vowels (o, a, e, i, y in EVA context, usually)
    vowels = ['o', 'a', 'e', 'i', 'y'] 
    skeleton = "".join([c for c in word if c not in vowels])
    return skeleton

def main():
    # 1. Load Inputs
    dictionary = load_json(INPUT_DICTIONARY)
    syntax_map = load_json(INPUT_SYNTAX)
    abbrevs = load_json(INPUT_ABBREV)
    medieval = load_json(INPUT_MEDIEVAL)
    romance = load_json(INPUT_ROMANCE)

    if not dictionary:
        print("Dictionary not found. Exiting.")
        return

    entries = dictionary.get("entries", {})
    
    # Build set of function words to ignore
    function_words = set()
    if syntax_map:
        if isinstance(syntax_map, list):
            for item in syntax_map:
                if "word" in item:
                    function_words.add(item["word"])
        elif isinstance(syntax_map, dict):
             # Handle if it's a dict (unlikely based on snippet but good for safety)
             pass

    print(f"Loaded {len(function_words)} function words to ignore.")
    
    # 2. Extract Roots (Unknowns)
    rows = []
    
    print(f"Processing {len(entries)} entries...")
    
    for word, data in entries.items():
        if data.get("confidence", 0) >= 0.5:
            continue
            
        if word in function_words:
            continue
            
        # Strip suffixes
        clean_root = word
        for suffix in sorted(SUFFIXES, key=len, reverse=True):
            if word.endswith(suffix):
                clean_root = word[:-len(suffix)]
                break
        
        if len(clean_root) < 2: 
            continue
            
        skeleton = extract_skeleton(clean_root)
        
        # 3. Matching Logic
        
        # A. Check Medieval Validation
        if medieval and "ingredient_matches" in medieval:
            for ing_name, ing_data in medieval["ingredient_matches"].items():
                for v_word in ing_data.get("voynich_words", []):
                    if extract_skeleton(v_word) == skeleton:
                         rows.append({
                             "Root": clean_root,
                             "Candidate Language": "Medieval/Latin",
                             "Candidate Meaning": f"{ing_name} (via {v_word})",
                             "Confidence": data.get("confidence", 0)
                         })

        # B. Check Proto Romance
        if romance and "italian_roots" in romance:
             for match in romance["italian_roots"].get("exact", []):
                 if match.get("voynich_skeleton") == skeleton:
                     rows.append({
                         "Root": clean_root,
                         "Candidate Language": "Proto-Romance",
                         "Candidate Meaning": f"{match.get('italian')} ({match.get('meaning')})",
                         "Confidence": data.get("confidence", 0)
                     })
        
        # C. Check Abbreviation Patterns
        if clean_root.startswith("q"):
             rows.append({
                 "Root": clean_root,
                 "Candidate Language": "Latin Abbrev",
                 "Candidate Meaning": "con-/com- prefix",
                 "Confidence": data.get("confidence", 0)
             })
        if clean_root.startswith("4"):
             rows.append({
                 "Root": clean_root,
                 "Candidate Language": "Latin Abbrev",
                 "Candidate Meaning": "qu- prefix",
                 "Confidence": data.get("confidence", 0)
             })
        
        # D. Simple Latin/Romance Lookups
        latin_roots = {
            "kr": ("Latin", "cor/cura (heart/cure)"),
            "tr": ("Latin", "terra (earth)"),
            "ml": ("Latin", "mel (honey)"),
            "sl": ("Latin", "sol (sun)"),
            "nm": ("Latin", "nomen (name)"),
            "dl": ("Latin", "dolor (pain)"),
            "fr": ("Latin", "frater/frigus (brother/cold)")
        }
        if skeleton in latin_roots:
            lang, meaning = latin_roots[skeleton]
            rows.append({
                "Root": clean_root,
                "Candidate Language": lang,
                "Candidate Meaning": meaning,
                "Confidence": data.get("confidence", 0)
            })

    # Deduplicate rows
    unique_rows = []
    seen = set()
    for r in rows:
        tup = (r["Root"], r["Candidate Language"], r["Candidate Meaning"])
        if tup not in seen:
            seen.add(tup)
            unique_rows.append(r)

    # 4. Output
    print(f"Found {len(unique_rows)} candidate matches.")
    
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Root", "Candidate Language", "Candidate Meaning", "Confidence"])
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"Wrote results to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
