import json
import datetime
import os

def update_dictionary():
    input_path = "results/dictionary/dictionary.json"
    output_path = "results/dictionary_update_v10_draft.json"
    summary_path = "results/track-233-results_summary.md"

    print(f"Loading {input_path}...")
    with open(input_path, "r") as f:
        data = json.load(f)

    entries = data["entries"]
    updates = []
    
    # Define the updates
    target_updates = {
        "ol": {
            "meaning": "The (Wet/Cold) / Water-of",
            "note": "Updated based on Elemental/Humoral grammatical markers hypothesis"
        },
        "o": {
            "meaning": "The (Dry/Hot) / Essence-of",
            "note": "Updated based on Elemental/Humoral grammatical markers hypothesis"
        },
        "qokeedy": {
            "meaning": "The Mixture (Wet/Decoction)",
            "note": "Updated based on Elemental/Humoral grammatical markers hypothesis"
        },
        "qokedy": {
            "meaning": "The Mixture (Dry/Powder)",
             "note": "Hypothesis: q-ol-keedy vs q-o-kedy"
        },
        "cheol": {
            "meaning": "Cold Sickness (Phlegmatic/Melancholic)",
            "note": "Updated: if ol is Wet/Cold, cheol might be Cold Sickness"
        }
    }

    # Apply updates
    for word, changes in target_updates.items():
        if word in entries:
            old_entry = entries[word]
            old_meaning = old_entry.get("meaning", "N/A")
            
            # Update fields
            entries[word]["meaning"] = changes["meaning"]
            entries[word]["source"] = "Track233_Elemental" 
            # Add a custom note or evidence if needed, but adhering to schema usually just updates fields.
            # We'll append to evidence if it exists or create it
            current_evidence = entries[word].get("evidence", "")
            if current_evidence:
                entries[word]["evidence"] = current_evidence + "; " + changes["note"]
            else:
                entries[word]["evidence"] = changes["note"]
            
            updates.append({
                "word": word,
                "old_meaning": old_meaning,
                "new_meaning": changes["meaning"]
            })
        else:
            print(f"Warning: Word '{word}' not found in dictionary.")
            # Create if not exists? The task says "Updates Required", usually implying existing entries.
            # But if they don't exist, we should probably add them.
            # Let's assume they exist based on the task context, but if not, we create new entry.
            entries[word] = {
                "voynich": word,
                "meaning": changes["meaning"],
                "language": "voynich_construct",
                "confidence": 0.5, # Speculative
                "domain": "elemental",
                "source": "Track233_Elemental",
                "evidence": changes["note"],
                "translation_status": 1
            }
            updates.append({
                "word": word,
                "old_meaning": "NEW_ENTRY",
                "new_meaning": changes["meaning"]
            })

    # Update metadata
    data["version"] = "10.0"
    data["date"] = datetime.datetime.now().isoformat()

    print(f"Saving to {output_path}...")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    # Write summary
    print(f"Writing summary to {summary_path}...")
    with open(summary_path, "w") as f:
        f.write("# Track 233 Results Summary: Dictionary v10 Prep\n\n")
        f.write("## Goal\n")
        f.write("Update the Master Dictionary to reflect the Elemental/Humoral grammatical markers.\n\n")
        f.write("## Updates Applied\n")
        f.write("| Word | Old Meaning | New Meaning | Notes |\n")
        f.write("|---|---|---|---|\n")
        for update in updates:
            f.write(f"| `{update['word']}` | {update['old_meaning']} | {update['new_meaning']} | |\n")
        
        f.write("\n## Notes\n")
        f.write("- Updated version to 10.0.\n")
        f.write(f"- Processed {len(updates)} entries.\n")

    print("Done.")

if __name__ == "__main__":
    update_dictionary()
