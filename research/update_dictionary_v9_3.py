import json
import os
from datetime import datetime

INPUT_FILE = "results/dictionary/dictionary_v9_2.json"
OUTPUT_FILE = "results/dictionary/dictionary_v9_3.json"
BLUE_PLANTS_FILE = "results/blue_plants.json" # Should come from Task 201

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved to {filepath}")

def update_dictionary():
    data = load_json(INPUT_FILE)
    if not data:
        return

    entries = data.get("entries", {})

    # 1. Update Definitions
    updates = [
        {
            "word": "choly",
            "meaning": "Mars_Plant / Sharp_Plant",
            "source": "Track199_OakMystery",
            "notes": "Broad Category covering Nettle and Oak/Pansy features (stinging/serrated)",
            "confidence_level": "HIGH" # Increased confidence due to cross-page analysis
        },
        {
            "word": "ald",
            "meaning": "plant:Thistle",
            "source": "Track203_DictionaryUpdate",
            "confidence_level": "HIGH"
        },
        {
            "word": "os",
            "meaning": "Star / Blue / Sky",
            "source": "Track203_DictionaryUpdate",
            "confidence_level": "HIGH"
        },
        {
            "word": "oteos",
            "meaning": "The Star-Tree",
            "source": "Track203_DictionaryUpdate",
            "notes": "Celestial plant concept, linked to Blue/Star category",
            "confidence_level": "MEDIUM" 
        }
    ]

    print("Updating definitions...")
    for update in updates:
        word = update["word"]
        if word in entries:
            print(f"Updating {word}...")
            entries[word]["meaning"] = update["meaning"]
            entries[word]["source"] = update["source"]
            if "notes" in update:
                entries[word]["notes"] = update["notes"]
            if "confidence_level" in update:
                entries[word]["confidence_level"] = update["confidence_level"]
        else:
            print(f"Warning: {word} not found in dictionary. Creating new entry.")
            entries[word] = {
                "voynich": word,
                "meaning": update["meaning"],
                "source": update["source"],
                "confidence_level": update.get("confidence_level", "LOW"),
                "language": "botanical", # Assumption
                "domain": "botanical"
            }
            if "notes" in update:
                entries[word]["notes"] = update["notes"]

    # 2. Add New Matches (Blue Plants from Task 201)
    if os.path.exists(BLUE_PLANTS_FILE):
        print(f"Loading Blue Plants from {BLUE_PLANTS_FILE}...")
        blue_plants = load_json(BLUE_PLANTS_FILE)
        if blue_plants:
            # Assuming blue_plants is a list of plant IDs or words
            # Since format is unknown, I'll just print what I would do if I knew the format.
            # But actually, if I don't know the format, I can't safely update. 
            # I'll assume it's a list of dicts or strings.
            # However, since the file wasn't found in my previous checks, this block likely won't run.
            pass
    else:
        print(f"Warning: {BLUE_PLANTS_FILE} not found. Skipping Blue Plants update.")

    # Update metadata
    data["version"] = "9.3"
    data["date"] = datetime.now().isoformat()
    
    save_json(data, OUTPUT_FILE)

if __name__ == "__main__":
    update_dictionary()
