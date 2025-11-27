import json
import os
from datetime import datetime

def load_json(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found.")
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # Input paths
    base_path = 'results/master_dictionary_v8_0.json'
    color_path = 'results/color_dictionary.json'
    
    # Output paths
    output_json_path = 'results/dictionary/dictionary.json'
    output_summary_path = 'results/track-183-results_summary.md'

    # Load inputs
    base_dict = load_json(base_path)
    color_dict = load_json(color_path)

    # Prepare new dictionary structure
    new_dict = {
        "version": "9.0",  # Incrementing version
        "date": datetime.now().isoformat(),
        "entries": base_dict.get("entries", {})
    }
    
    entries = new_dict["entries"]
    changes_log = []

    # Helper to update or add entry
    def update_entry(key, meaning, part_of_speech=None, note=None, source="Track183"):
        original = entries.get(key, {})
        new_entry = original.copy()
        new_entry['voynich'] = key
        new_entry['meaning'] = meaning
        
        if part_of_speech:
            new_entry['part_of_speech'] = part_of_speech
        
        # Merge or set source
        prev_source = new_entry.get('source', '')
        if source not in prev_source:
            new_entry['source'] = f"{prev_source}, {source}" if prev_source else source

        if note:
            new_entry['note'] = note

        # Log change
        if key not in entries:
            changes_log.append(f"Added {key}: {meaning} ({part_of_speech})")
        elif original.get('meaning') != meaning:
            changes_log.append(f"Updated {key}: '{original.get('meaning')}' -> '{meaning}'")
        
        entries[key] = new_entry

    # 1. Integrate Color Dictionary
    # color_dict is simple key:value. 
    # We should be careful not to overwrite high-confidence meanings unless necessary, 
    # but the task implies these are "Semantic Breakthroughs" or at least valuable.
    # Task 183 says: "results/color_dictionary.json (From Task 182)" is an input.
    # But step 4 says: "If `or` was "Earth" in v8.0, change it to "Green/Gold" based on Task 182 evidence."
    # This suggests Task 182/Color Dictionary overrides.
    
    for word, meaning in color_dict.items():
        # We'll treat these as Adjectives or Nouns depending on context, but the simple dict doesn't have POS.
        # We'll just update the meaning.
        update_entry(word, meaning, source="Task182_Color")

    # 2. Update Grammar (Step 2)
    update_entry("ed", "mix/process", part_of_speech="Verb", source="Track183_Grammar")
    update_entry("qok-", "prefix:verb_marker", part_of_speech="Prefix", source="Track183_Grammar")
    update_entry("-y", "suffix:imperative", part_of_speech="Suffix", source="Track183_Grammar")

    # 3. Update Semantics (Step 3)
    update_entry("ordaiin", "golden_extract", part_of_speech="Noun", source="Track183_Semantics")
    update_entry("or", "green/gold", part_of_speech="Adjective", source="Track183_Semantics")
    update_entry("ot", "red/brown", part_of_speech="Adjective", source="Track183_Semantics")
    update_entry("os", "star/blue", part_of_speech="Noun/Adjective", source="Track183_Semantics")

    # 4. Conflict Resolution (Step 4)
    # Explicit check for 'or'
    if entries.get("or", {}).get("meaning") == "Earth":
        update_entry("or", "green/gold", part_of_speech="Adjective", source="Track183_ConflictResolution")
        changes_log.append("Resolved conflict for 'or': Earth -> Green/Gold")

    # Recalculate stats
    new_dict["total_entries"] = len(entries)

    # Save Dictionary
    save_json(new_dict, output_json_path)
    print(f"Saved dictionary to {output_json_path}")

    # Generate Summary
    summary_content = f"""# Track 183 Results Summary

## Overview
Integration of dictionary updates from Task 182 (Colors), Grammar analysis, and semantic refinements.
Generated definitive `dictionary.json` (v9.0).

## Key Changes
- **Total Entries**: {new_dict['total_entries']}
- **Base**: Master Dictionary v8.0

### Grammar Updates
- `ed`: mix/process (Verb)
- `qok-`: prefix:verb_marker
- `-y`: suffix:imperative

### Semantic Updates
- `ordaiin`: golden_extract
- `or`: green/gold
- `ot`: red/brown
- `os`: star/blue

### Integration Logs
{chr(10).join(['- ' + log for log in changes_log[:50]])}
{f'- ... and {len(changes_log) - 50} more updates.' if len(changes_log) > 50 else ''}
"""
    with open(output_summary_path, 'w') as f:
        f.write(summary_content)
    print(f"Saved summary to {output_summary_path}")

if __name__ == "__main__":
    main()
