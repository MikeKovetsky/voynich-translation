import json
import os

def merge_cleanup_v13():
    print("Creating Dictionary v13 (Cleanup)...")
    
    base_path = "results/dictionary/dictionary.json"
    with open(base_path, 'r') as f:
        dictionary = json.load(f)
    entries = dictionary.get("entries", dictionary)
    
    # 1. Merge Suffixes
    with open("results/suffix_mining.json", 'r') as f:
        suffixes = json.load(f)
        
    for s in suffixes:
        if s["word"] not in entries:
            entries[s["word"]] = {
                "voynich": s["word"],
                "meaning": s["meaning"],
                "root": s["root"],
                "language": "voynich_inferred",
                "confidence": 0.6,
                "source": "Track251_Suffix",
                "translation_status": 1
            }
            
    # 2. Merge Fuzzy Typos
    with open("results/fuzzy_merges.json", 'r') as f:
        typos = json.load(f)
        
    for t in typos:
        if t["hapax"] not in entries:
            target_meaning = entries.get(t["target"], {}).get("meaning", "unknown")
            entries[t["hapax"]] = {
                "voynich": t["hapax"],
                "meaning": f"Variant of {t['target']} ({target_meaning})",
                "variant_of": t["target"],
                "language": "voynich_inferred",
                "confidence": 0.4, # Lower confidence for typos
                "source": "Track252_Fuzzy",
                "translation_status": 1
            }

    # Update Version
    dictionary["version"] = "13.0"
    if "entries" in dictionary:
        dictionary["entries"] = entries
        
    # Save
    with open("results/dictionary/dictionary_v13.json", 'w') as f:
        json.dump(dictionary, f, indent=2)
    
    # Overwrite Master
    with open("results/dictionary/dictionary.json", 'w') as f:
        json.dump(dictionary, f, indent=2)
        
    print(f"Dictionary v13 created with {len(entries)} entries.")

if __name__ == "__main__":
    merge_cleanup_v13()
