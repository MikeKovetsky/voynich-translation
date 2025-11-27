import json
import os
from datetime import datetime
from pathlib import Path

def update_dictionary():
    # Determine input file
    possible_inputs = [
        "results/master_dictionary_v7_3.json",
        "results/unified_dictionary.json",
        "results/master_dictionary_v5.json"
    ]
    
    input_file = None
    for fpath in possible_inputs:
        if os.path.exists(fpath):
            input_file = fpath
            break
            
    if not input_file:
        print("Error: No suitable input dictionary found.")
        return

    output_file = "results/master_dictionary_v7_4.json"
    report_file = "results/dictionary_v7_4_report.md"

    print(f"Loading dictionary from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Handle structure differences (some have "entries" key, some might be direct or different)
    # unified_dictionary.json might have a different structure.
    if "entries" in data:
        entries = data["entries"]
    else:
        # If it's a flat dict or different structure, we might need to adapt.
        # Assuming unified_dictionary.json has a structure we can work with or is just the entries.
        # Let's inspect the structure if we can, but for now assume it might need normalization.
        # If data is a list or flat dict, we wrap it.
        if isinstance(data, dict) and not "entries" in data:
             # Check if it looks like entries (keys are words)
             sample_key = next(iter(data))
             if isinstance(data[sample_key], dict):
                 entries = data
             else:
                 print("Unknown dictionary format.")
                 return
        else:
            entries = {}

    updates = []
    new_entries = []
    
    # Task 1: Add Plant IDs
    plant_updates = [
        {"voynich": "chtol", "meaning": "Papaver (Poppy)", "confidence": 0.95, "source": "Track133_PlantID"},
        {"voynich": "tsho", "meaning": "Smilax", "confidence": 0.95, "source": "Track133_PlantID"},
        {"voynich": "shoaiin", "meaning": "Cannabis (Hemp)", "confidence": 0.95, "source": "Track133_PlantID"},
        {"voynich": "shkaiin", "meaning": "Hypericum (St John's Wort)", "confidence": 0.95, "source": "Track133_PlantID"},
        {"voynich": "keedal", "meaning": "Papaver (variant?)", "confidence": 0.85, "source": "Track133_PlantID"},
        {"voynich": "ckhal", "meaning": "Ricinus", "confidence": 0.90, "source": "Track133_PlantID"},
    ]

    # Task 2: Star Name Roots
    star_updates = [
        {"voynich": "teos", "meaning": "Tree", "confidence": 0.85, "source": "Track133_StarID"},
        {"voynich": "oteos", "meaning": "The Tree", "confidence": 0.85, "source": "Track133_StarID"},
        {"voynich": "kar", "meaning": "Root", "confidence": 0.85, "source": "Track133_StarID"},
        {"voynich": "okar", "meaning": "The Root", "confidence": 0.85, "source": "Track133_StarID"},
    ]

    all_updates = plant_updates + star_updates

    for item in all_updates:
        key = item["voynich"]
        if key in entries:
            old_entry = entries[key]
            old_meaning = old_entry.get("meaning", "Unknown")
            new_meaning = item["meaning"]
            
            if old_meaning != new_meaning:
                updates.append(f"Updated {key}: '{old_meaning}' -> '{new_meaning}'")
                entries[key].update(item)
                entries[key]["last_updated"] = datetime.now().isoformat()
        else:
            item["created"] = datetime.now().isoformat()
            # Ensure minimal fields
            if "language" not in item: item["language"] = "voynich"
            entries[key] = item
            new_entries.append(f"Added {key}: {item['meaning']}")

    # Save new dictionary
    output_data = {
        "version": "7.4",
        "base_source": input_file,
        "date": datetime.now().isoformat(),
        "total_entries": len(entries),
        "entries": entries
    }

    print(f"Saving updated dictionary to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Generate Report
    print(f"Generating report to {report_file}...")
    with open(report_file, 'w') as f:
        f.write("# Dictionary Update v7.4 Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Base Dictionary:** {input_file}\n")
        f.write(f"**Total Entries:** {len(entries)}\n\n")
        
        f.write("## Updates\n\n")
        if new_entries:
            f.write("### New Entries\n")
            for e in new_entries:
                f.write(f"- {e}\n")
        
        if updates:
            f.write("\n### Modified Entries\n")
            for u in updates:
                f.write(f"- {u}\n")

    print("Done.")

if __name__ == "__main__":
    update_dictionary()
