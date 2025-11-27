import json
import os

def merge_candidates():
    print("Merging candidates into Dictionary v12...")
    
    # Load Base Dictionary
    base_path = "results/dictionary/dictionary.json"
    with open(base_path, 'r') as f:
        dictionary = json.load(f)
        
    entries = dictionary.get("entries", dictionary)
    
    # Load Candidates
    files = {
        "plant_candidate": "results/mining/plant_candidates.json",
        "star_candidate": "results/mining/astral_candidates.json",
        "ingredient_candidate": "results/mining/ingredient_candidates.json"
    }
    
    count_added = 0
    
    for type_label, path in files.items():
        if os.path.exists(path):
            with open(path, 'r') as f:
                candidates = json.load(f)
                
            # Handle list of strings vs list of objects
            for item in candidates:
                if isinstance(item, str):
                    word = item
                    meta = {}
                else:
                    word = item.get("word")
                    meta = item
                
                # Skip existing
                if word in entries:
                    continue
                    
                # Clean word (remove <...>)
                clean_word = word.split("<")[0].strip()
                if not clean_word or len(clean_word) < 2: continue
                
                # Add Entry
                entries[clean_word] = {
                    "voynich": clean_word,
                    "meaning": type_label, # e.g. plant_candidate
                    "language": "voynich_inferred",
                    "confidence": 0.5,
                    "domain": "mining",
                    "source": "Track246_MassMining",
                    "evidence": "Contextual Slot Mining",
                    "confidence_level": "PROPOSED",
                    "translation_status": 1 # 1 = Proposed/Inferred
                }
                count_added += 1
                
    # Update Version
    dictionary["version"] = "12.0"
    if "entries" in dictionary:
        dictionary["entries"] = entries
    else:
        dictionary = {"version": "12.0", "entries": entries}
        
    # Save
    output_path = "results/dictionary/dictionary_v12.json"
    with open(output_path, 'w') as f:
        json.dump(dictionary, f, indent=2)
        
    # Overwrite Master (for future steps)
    with open("results/dictionary/dictionary.json", 'w') as f:
        json.dump(dictionary, f, indent=2)
        
    print(f"Added {count_added} new entries.")
    print(f"Total entries: {len(entries)}")
    return output_path

if __name__ == "__main__":
    merge_candidates()
