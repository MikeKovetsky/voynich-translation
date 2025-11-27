import json
import os
from datetime import datetime

def update_dictionary():
    input_file = "results/master_dictionary_v7_1.json"
    output_file = "results/master_dictionary_v7_2.json"
    report_file = "results/dictionary_v7_2_report.md"

    print(f"Loading dictionary from {input_file}...")
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
        return

    entries = data.get("entries", {})
    
    updates = []
    new_entries = []

    # Updates definition
    # Prefixes
    prefixes = [
        {
            "voynich": "sh-",
            "meaning": "that/which (Relative Pronoun)",
            "language": "voynich_grammar",
            "domain": "grammar",
            "confidence": 0.85,
            "source": "Track122_Grammar",
            "evidence": "Appears in narrative descriptions, never with imperative daiin. Relative pronoun behavior."
        },
        {
            "voynich": "t-",
            "meaning": "to (Preposition) / Future Marker",
            "language": "voynich_grammar",
            "domain": "grammar",
            "confidence": 0.80,
            "source": "Track122_Grammar",
            "evidence": "Can stack with sh- (tshedy). Contextual analysis suggests prepositional or future tense usage."
        }
    ]

    # Verbs
    verbs = [
        {
            "voynich": "okeol",
            "meaning": "boil",
            "language": "voynich_recipe",
            "domain": "recipe",
            "confidence": 0.85,
            "source": "Track122_Recipe",
            "evidence": "Context: Water action. Appears immediately after 'daiin ol oain' (take water)."
        },
        {
            "voynich": "qokeey",
            "meaning": "cook/process",
            "language": "voynich_recipe",
            "domain": "recipe",
            "confidence": 0.90,
            "source": "Track122_Recipe",
            "evidence": "General recipe verb. Most common action verb in recipes."
        },
        {
            "voynich": "qokeol",
            "meaning": "boil (variant)",
            "language": "voynich_recipe",
            "domain": "recipe",
            "confidence": 0.80,
            "source": "Track122_Recipe",
            "evidence": "Variant of okeol, likely similar meaning."
        }
    ]

    # Special Review
    chedy_update = {
        "voynich": "chedy",
        "meaning": "Ambiguous: Herb/Plant OR Drink",
        "language": "voynich_recipe",
        "domain": "recipe/botanical",
        "confidence": 0.60,
        "source": "Track122_Review",
        "evidence": "Suspiciously frequent at end of recipes. Could be noun (plant) or verb (drink/serve)."
    }

    # Apply updates
    for item in prefixes + verbs:
        key = item["voynich"]
        if key in entries:
            old_entry = entries[key]
            entries[key].update(item)
            entries[key]["last_updated"] = datetime.now().isoformat()
            updates.append(f"Updated {key}: {item['meaning']}")
        else:
            item["created"] = datetime.now().isoformat()
            entries[key] = item
            new_entries.append(f"Added {key}: {item['meaning']}")

    # Apply chedy update
    if "chedy" in entries:
        entries["chedy"].update(chedy_update)
        entries["chedy"]["last_updated"] = datetime.now().isoformat()
        updates.append(f"Updated chedy: {chedy_update['meaning']}")
    else:
        chedy_update["created"] = datetime.now().isoformat()
        entries["chedy"] = chedy_update
        new_entries.append(f"Added chedy: {chedy_update['meaning']}")

    # Save new dictionary
    data["version"] = "7.2"
    data["total_entries"] = len(entries)
    data["entries"] = entries

    print(f"Saving updated dictionary to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    # Generate Report
    print(f"Generating report to {report_file}...")
    with open(report_file, 'w') as f:
        f.write("# Dictionary Update v7.2 Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Input Version:** 7.1\n")
        f.write(f"**Output Version:** 7.2\n")
        f.write(f"**Total Entries:** {len(entries)}\n\n")

        f.write("## New Entries\n")
        if new_entries:
            for entry in new_entries:
                f.write(f"- {entry}\n")
        else:
            f.write("- No new entries added.\n")
        
        f.write("\n## Updated Entries\n")
        if updates:
            for entry in updates:
                f.write(f"- {entry}\n")
        else:
            f.write("- No entries updated.\n")

        f.write("\n## Key Changes\n")
        f.write("### Grammar Prefixes\n")
        f.write("- **sh-**: Defined as Relative Pronoun ('that/which').\n")
        f.write("- **t-**: Defined as Preposition ('to') or Future Marker.\n")

        f.write("\n### Recipe Verbs\n")
        f.write("- **okeol**: Defined as 'boil' (water context).\n")
        f.write("- **qokeey**: Defined as 'cook/process' (general).\n")
        f.write("- **qokeol**: Defined as 'boil' (variant).\n")

        f.write("\n### Ambiguity Review\n")
        f.write("- **chedy**: Marked as Ambiguous (Herb/Plant OR Drink). Needs resolution in Track 123.\n")

    print("Done.")

if __name__ == "__main__":
    update_dictionary()
