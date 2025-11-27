import json

try:
    with open("results/proposed_morphology_entries_v3.json", "r") as f:
        matches = json.load(f)

    entries = {}
    for m in matches:
        affix = m.get("affix", "")
        stem = m.get("stem", "")
        entries[m["word"]] = {
            "voynich": m["word"],
            "meaning": "morphological_derivative (" + affix + " + " + stem + ")",
            "root": stem,
            "morphology": affix,
            "source": "Track224_Morphology_v3",
            "confidence": 0.85
        }

    with open("results/dictionary_update_v3.json", "w") as f:
        json.dump(entries, f, indent=2)

    print(f"Prepared {len(entries)} entries for merge.")

except Exception as e:
    print(f"Error: {e}")
