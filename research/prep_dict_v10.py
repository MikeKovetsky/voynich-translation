import json

def prep_dict_v10():
    # Load Dictionary v9.1
    try:
        with open("results/dictionary/dictionary.json", "r") as f:
            dictionary = json.load(f)
            # Handle legacy vs new format
            if "entries" in dictionary:
                entries = dictionary["entries"]
                metadata = {k:v for k,v in dictionary.items() if k != "entries"}
            else:
                entries = dictionary
                metadata = {"version": "9.1"}
    except:
        entries = {}
        metadata = {"version": "9.1"}

    # Updates
    updates = {
        "ol": {
            "meaning": "The (Wet/Cold) / Water-of",
            "element": "Water/Venus",
            "grammar_type": "Article/Preposition"
        },
        "o": {
            "meaning": "The (Dry/Hot) / Essence-of",
            "element": "Fire/Mars",
            "grammar_type": "Article/Preposition"
        },
        "qokeedy": {
            "meaning": "The Mixture (Wet/Decoction)",
            "element": "Water",
            "grammar_type": "Noun"
        },
        "qokedy": {
            "meaning": "The Mixture (Dry/Powder)",
            "element": "Fire/Earth",
            "grammar_type": "Noun"
        },
        "cheol": {
            "meaning": "Cold Sickness / Phlegmatic Condition",
            "element": "Water",
            "grammar_type": "Noun"
        }
    }
    
    # Apply Updates
    for word, data in updates.items():
        if word in entries:
            # Merge
            entries[word]["meaning"] = data["meaning"]
            entries[word]["element"] = data.get("element")
            entries[word]["grammar_type"] = data.get("grammar_type")
            entries[word]["confidence"] = 0.9
            entries[word]["source"] = "Track233_Elemental_Grammar"
        else:
            # Create
            entries[word] = {
                "voynich": word,
                "meaning": data["meaning"],
                "element": data.get("element"),
                "grammar_type": data.get("grammar_type"),
                "confidence": 0.9,
                "source": "Track233_Elemental_Grammar"
            }

    # Save Draft
    with open("results/dictionary_update_v10_draft.json", "w") as f:
        json.dump(entries, f, indent=2)
        
    # Summary
    summary = f"# Track 233: Dictionary v10 Prep\n\nUpdated {len(updates)} core grammatical markers to reflect Humoral/Elemental logic.\n\n"
    for w, d in updates.items():
        summary += f"- **{w}**: {d['meaning']}\n"
        
    with open("results/track-233-results_summary.md", "w") as f:
        f.write(summary)

if __name__ == "__main__":
    prep_dict_v10()
