import json
import os
from datetime import datetime

INPUT_FILE = 'results/dictionary/master_dictionary_v15.json'
OUTPUT_FILE = 'results/dictionary/master_dictionary_v16.json'

def load_dictionary(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_dictionary(data, filepath):
    # Sort entries by key
    data['entries'] = dict(sorted(data['entries'].items()))
    data['version'] = '16.0_master'
    data['date'] = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_entry(entries, word, updates):
    if word in entries:
        print(f"Updating existing entry: {word}")
        entry = entries[word]
        for key, value in updates.items():
            if key == "meaning":
                # Append to existing meaning if it exists and is different
                if value not in entry.get("meaning", ""):
                    entry["meaning"] = f"{entry.get('meaning', '')}; {value}".strip("; ")
            elif key == "evidence":
                 if value not in entry.get("evidence", ""):
                    entry["evidence"] = f"{entry.get('evidence', '')}; {value}".strip("; ")
            else:
                entry[key] = value
    else:
        print(f"Creating new entry: {word}")
        entries[word] = {
            "voynich": word,
            "translation_status": 1, # Default for new manually added entries
            **updates
        }

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    data = load_dictionary(INPUT_FILE)
    entries = data['entries']

    # 1. New Entries
    # sal: "Salt" (Ingredient) - Found in f41r.
    update_entry(entries, "sal", {
        "meaning": "Salt",
        "language": "hebrew/latin", # sal is latin, also salt
        "confidence": 0.8,
        "domain": "recipe_ingredient",
        "source": "Track292_DictCleanup",
        "evidence": "Found in f41r",
        "confidence_level": "HIGH"
    })

    # qokedy: "Mixture/Decoction" -> Refine to include "Bath Mixture"
    # First check what it has
    if "qokedy" in entries:
        current_meaning = entries["qokedy"].get("meaning", "")
        if "Bath Mixture" not in current_meaning:
             update_entry(entries, "qokedy", {
                "meaning": "Bath Mixture", # This will append
                "domain": "bio_recipe",
                "source": "Track292_DictCleanup"
            })
    else:
         # If it doesn't exist (though instructions imply it might), add it
         update_entry(entries, "qokedy", {
            "meaning": "Mixture/Decoction; Bath Mixture",
            "domain": "bio_recipe",
            "source": "Track292_DictCleanup",
            "confidence": 0.7,
             "confidence_level": "MEDIUM"
        })

    # shkair: "Chicory"
    update_entry(entries, "shkair", {
        "meaning": "Chicory",
        "language": "botanical", 
        "confidence": 0.7,
        "domain": "botanical",
        "source": "Track292_DictCleanup",
        "evidence": "Proposed by user",
        "confidence_level": "MEDIUM"
    })

    # keero: "Coriander"
    update_entry(entries, "keero", {
        "meaning": "Coriander",
        "language": "botanical",
        "confidence": 0.7,
        "domain": "botanical",
        "source": "Track292_DictCleanup",
        "evidence": "Proposed by user",
        "confidence_level": "MEDIUM"
    })

    # 2. Refine Definitions
    # sho: Add "Fumigate/Burn" context
    update_entry(entries, "sho", {
        "meaning": "Fumigate/Burn", # Will append
        "domain": "recipe_action", # Update domain if appropriate
        "source": "Track292_DictCleanup"
    })

    # Save v16
    save_dictionary(data, OUTPUT_FILE)
    print(f"Successfully created {OUTPUT_FILE} with {len(entries)} entries.")

if __name__ == "__main__":
    main()
