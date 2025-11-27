import json
import re
import os

DICT_PATH = 'results/dictionary/dictionary.json'

def get_translation_status(meaning):
    if not meaning:
        return 0
    
    meaning = meaning.strip()
    meaning_lower = meaning.lower()
    
    # Status 0: Not translated / Placeholder / Unknown
    if meaning == "plant_name":
        return 0
    if meaning.startswith("[") and meaning.endswith("]"):
        return 0
    if meaning in ["???", "?", "???"]:
        return 0
    if meaning_lower == "unknown":
        return 0
        
    # Status 1: Uncertain / Partial
    # Contains ? but is not just ? or ???
    if "?" in meaning:
        return 1
    # Contains "unknown" but is not just "unknown"
    if "unknown" in meaning_lower:
        return 1
        
    # Status 2: Translated
    return 2

def main():
    if not os.path.exists(DICT_PATH):
        print(f"File not found: {DICT_PATH}")
        return

    with open(DICT_PATH, 'r') as f:
        data = json.load(f)
        
    entries = data.get("entries", {})
    
    updated_count = 0
    stats = {0: 0, 1: 0, 2: 0}
    
    for key, entry in entries.items():
        meaning = entry.get("meaning", "")
        status = get_translation_status(meaning)
        entry["translation_status"] = status
        stats[status] += 1
        updated_count += 1
        
    data["entries"] = entries
    
    with open(DICT_PATH, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Updated {updated_count} entries.")
    print("Status counts:")
    for s, count in stats.items():
        print(f"  Status {s}: {count}")

if __name__ == "__main__":
    main()
