import json
import os
from datetime import datetime

def update_dictionary():
    input_file = "results/master_dictionary_v7_2.json"
    output_file = "results/master_dictionary_v7_3.json"
    report_file = "results/dictionary_v7_3_report.md"

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
    conflicts = []

    # Task 1: Update Key Terms
    key_terms = [
        {
            "voynich": "chedy",
            "meaning": "Mixture/Decoction",
            "language": "voynich",
            "domain": "recipe",
            "confidence": 0.95,
            "source": "Track127_WaterOfLife",
            "evidence": "Result of cooking process (qokeey chedy). Object of consumption. Replaces 'Ambiguous' status."
        },
        {
            "voynich": "shol",
            "meaning": "Extract/Draw out",
            "language": "voynich",
            "domain": "recipe/chemistry",
            "confidence": 0.90,
            "source": "Track127_WaterOfLife",
            "evidence": "Associated with extraction process. Root likely 'sho' (Fire/Heat)?"
        },
        {
            "voynich": "sho",
            "meaning": "Fire/Heat",
            "language": "voynich",
            "domain": "element",
            "confidence": 0.85,
            "source": "Track127_WaterOfLife",
            "evidence": "Root context for cooking/extraction."
        },
        {
            "voynich": "saiin",
            "meaning": "Water/Spring (variant)",
            "language": "voynich",
            "domain": "element",
            "confidence": 0.90,
            "source": "Track127_WaterOfLife",
            "evidence": "Variant of aiin (Water)."
        },
        {
            "voynich": "qokeol",
            "meaning": "Boil",
            "language": "voynich",
            "domain": "recipe",
            "confidence": 0.95,
            "source": "Track127_WaterOfLife",
            "evidence": "Confirmed as 'Boil' in recipe context."
        }
    ]

    for item in key_terms:
        key = item["voynich"]
        if key in entries:
            old_entry = entries[key]
            # Check for conflicts (major meaning change)
            old_meaning = old_entry.get("meaning", "").lower()
            new_meaning = item["meaning"].lower()
            
            # Simple heuristic for conflict: if old meaning exists and is different enough
            # For chedy, we expect a change.
            if key == "chedy":
                updates.append(f"Updated {key}: '{old_entry.get('meaning')}' -> '{item['meaning']}'")
            elif key == "shol" and "plant" in old_meaning:
                conflicts.append(f"Conflict resolved for {key}: Was '{old_entry.get('meaning')}', now '{item['meaning']}'")
                updates.append(f"Updated {key} (Resolved Conflict): '{item['meaning']}'")
            elif old_meaning != new_meaning:
                updates.append(f"Updated {key}: '{old_entry.get('meaning')}' -> '{item['meaning']}'")
            
            entries[key].update(item)
            entries[key]["last_updated"] = datetime.now().isoformat()
        else:
            item["created"] = datetime.now().isoformat()
            entries[key] = item
            new_entries.append(f"Added {key}: {item['meaning']}")

    # Task 2: Clean Up
    # Ensure y- (And) is correctly applied to compound words
    y_compounds_updated = 0
    for word, entry in entries.items():
        if word.startswith("y") and len(word) > 1 and word != "y":
            stem = word[1:]
            if stem in entries:
                stem_meaning = entries[stem].get("meaning", "Unknown")
                expected_meaning = f"And {stem_meaning}"
                
                # If current meaning is missing or explicitly marks it as unknown/variant without detail
                current_meaning = entry.get("meaning", "")
                
                # We update if it doesn't look like it already has the "And" definition
                if not current_meaning.lower().startswith("and ") and "variant" not in current_meaning.lower():
                    entry["meaning"] = expected_meaning
                    entry["notes"] = f"Compound of y- (And) + {stem}"
                    entry["derived_from"] = stem
                    entry["last_updated"] = datetime.now().isoformat()
                    y_compounds_updated += 1
                    # updates.append(f"Updated compound {word}: {expected_meaning}") # Optional: too many might clutter report

    if y_compounds_updated > 0:
        updates.append(f"Systematically updated {y_compounds_updated} 'y-' compound words.")

    # Save new dictionary
    data["version"] = "7.3"
    data["total_entries"] = len(entries)
    data["entries"] = entries

    print(f"Saving updated dictionary to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    # Generate Report
    print(f"Generating report to {report_file}...")
    with open(report_file, 'w') as f:
        f.write("# Dictionary Update v7.3 Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Input Version:** 7.2\n")
        f.write(f"**Output Version:** 7.3\n")
        f.write(f"**Total Entries:** {len(entries)}\n\n")

        f.write("## Key Updates (Water of Life)\n")
        f.write("The following terms were finalized based on the Hydrotherapy/Herbal investigation:\n\n")
        
        f.write("| Term | New Meaning | Previous/Context |\n")
        f.write("|------|-------------|------------------|\n")
        f.write(f"| **chedy** | Mixture/Decoction | Formerly 'Ambiguous'. The liquid product of cooking. |\n")
        f.write(f"| **shol** | Extract/Draw out | Associated with extraction. |\n")
        f.write(f"| **sho** | Fire/Heat | Root element. |\n")
        f.write(f"| **saiin** | Water/Spring | Variant of `aiin`. |\n")
        f.write(f"| **qokeol** | Boil | Confirmed recipe verb. |\n")

        f.write("\n## Changes Log\n")
        
        if new_entries:
            f.write("### New Entries\n")
            for entry in new_entries:
                f.write(f"- {entry}\n")
        
        if conflicts:
            f.write("\n### Conflicts Resolved\n")
            for conflict in conflicts:
                f.write(f"- {conflict}\n")

        if updates:
            f.write("\n### Updates\n")
            for entry in updates:
                f.write(f"- {entry}\n")
        
        if y_compounds_updated > 0:
            f.write(f"\n### Structural Clean-up\n")
            f.write(f"- Processed {y_compounds_updated} words starting with 'y-'. Mapped them as 'And + [Root Meaning]'.\n")

    print("Done.")

if __name__ == "__main__":
    update_dictionary()
