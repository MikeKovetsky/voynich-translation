import json
from datetime import datetime

def update_dictionary():
    input_path = 'results/dictionary/dictionary_v9_3.json'
    output_path = 'results/dictionary/dictionary_v9_4.json'

    with open(input_path, 'r') as f:
        data = json.load(f)

    entries = data.get("entries", {})

    # Updates based on Task 210
    updates = [
        {
            "voynich": "saiin",
            "meaning": "unit:cup",
            "source": "Track210",
            "semantic_category": "Measurement",
            "note": "Cyathus"
        },
        {
            "voynich": "ar",
            "meaning": "unit:handful",
            "source": "Track210",
            "semantic_category": "Measurement",
            "note": "Manipulus"
        },
        {
            "voynich": "ii",
            "meaning": "number:2",
            "source": "Track210",
            "semantic_category": "Measurement"
        },
        {
            "voynich": "daiin",
            "meaning": "unit:cup_variant", # Initial primary meaning, logic below handles dual possibilities if needed, but structure usually takes one meaning or splits. 
            # Task says: "unit:cup_variant" or "verb:take_water". I will put both in meaning for now or use notes.
            # Let's stick to one string for meaning if possible or use a slash.
            "source": "Track210",
            "semantic_category": "Measurement"
        },
        {
            "voynich": "qok",
            "meaning": "verb:take/mix",
            "source": "Track210", # updating source as well? or keeping old? usually update source if it refines it.
            "semantic_category": "Measurement",
            "note": "Refined from previous version (Rx)"
        }
    ]

    for update in updates:
        word = update["voynich"]
        if word in entries:
            # Update existing
            entry = entries[word]
            entry["meaning"] = update["meaning"]
            if "semantic_category" in update:
                entry["semantic_category"] = update["semantic_category"]
            if "note" in update:
                entry["note"] = update.get("note")
            # Update source only if it's a refinement or new info? 
            # Task says "Refine Verbs", implies update.
            # For "Add Units", it might be new or overwrite.
            entry["source"] = update["source"]
            entry["confidence"] = 0.85 # Set high confidence for these findings
        else:
            # Create new
            entries[word] = {
                "voynich": word,
                "meaning": update["meaning"],
                "confidence": 0.85,
                "source": update["source"],
                "semantic_category": update.get("semantic_category", ""),
                "language": "voynich" # default
            }
            if "note" in update:
                entries[word]["note"] = update["note"]

    # Specific handling for daiin to match "unit:cup_variant" or "verb:take_water"
    # If it's a new entry, I set it above. If I want to capture the ambiguity:
    if "daiin" in entries:
        entries["daiin"]["meaning"] = "unit:cup_variant/verb:take_water"

    data["version"] = "9.4"
    data["date"] = datetime.now().isoformat()
    data["entries"] = entries

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Dictionary updated and saved to {output_path}")

if __name__ == "__main__":
    update_dictionary()
