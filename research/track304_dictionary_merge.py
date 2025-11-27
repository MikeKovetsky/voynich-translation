import json
import csv
import os
from datetime import datetime

def load_json(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found.")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_csv(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found.")
        return []
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def main():
    # File paths
    v16_path = "results/dictionary/master_dictionary_v16.json"
    algo_path = "results/dictionary_expansion_v17_algo.json"
    context_path = "results/context_inferred_candidates.json"
    top100_path = "results/top_100_unknowns.csv"
    output_path = "results/dictionary/master_dictionary_v17.json"
    summary_path = "results/track-304-results_summary.md"

    # 1. Load inputs
    print("Loading inputs...")
    v16_data = load_json(v16_path)
    master_entries = v16_data.get("entries", {})
    
    algo_entries = load_json(algo_path)
    
    context_list = load_json(context_path)
    
    top100_rows = load_csv(top100_path)

    print(f"Loaded v16: {len(master_entries)} entries")
    print(f"Loaded Algo: {len(algo_entries)} entries")
    print(f"Loaded Context: {len(context_list)} candidates")
    print(f"Loaded Top 100: {len(top100_rows)} rows")

    # Check rcheo in inputs
    if "rcheo" in master_entries:
        print(f"DEBUG: rcheo in v16: {master_entries['rcheo']}")
    else:
        print("DEBUG: rcheo NOT in v16")

    # 2. Process Context list into dictionary format
    # Handling duplicates in context list: prefer Higher confidence
    context_entries = {}
    confidence_map = {"High": 0.8, "Medium": 0.5, "Low": 0.3}
    
    for item in context_list:
        word = item.get("unknown_word")
        if not word:
            continue
            
        inference = item.get("inference", "")
        conf_str = item.get("confidence", "Low")
        conf_val = confidence_map.get(conf_str, 0.3)
        
        entry = {
            "voynich": word,
            "meaning": inference,
            "language": "voynich_inferred",
            "confidence": conf_val,
            "domain": "context_analysis",
            "source": "context_v17",
            "evidence": item.get("context_frame", ""),
            "confidence_level": "INFERRED",
            "translation_status": 1
        }
        
        # If already exists, check confidence
        if word in context_entries:
            if conf_val > context_entries[word]["confidence"]:
                context_entries[word] = entry
        else:
            context_entries[word] = entry

    print(f"Processed Context: {len(context_entries)} unique entries")
    if "rcheo" in context_entries:
        print(f"DEBUG: rcheo in context_entries: {context_entries['rcheo']}")
    else:
        print("DEBUG: rcheo NOT in context_entries")

    # 3. Merge Logic
    # Start with v16
    merged_entries = master_entries.copy()
    
    # Add Algo (Source: algo_v17)
    # Task: "If a word is in both Algo and Context lists, prefer Context"
    # So we add Algo first, then Context overwrites.
    
    for word, entry in algo_entries.items():
        # Update source tag as per task
        entry["source"] = "algo_v17" 
        merged_entries[word] = entry

    # Add Context (Source: context_v17)
    for word, entry in context_entries.items():
        # Context overwrites Algo and v16 (prefer context)
        merged_entries[word] = entry
        
    if "rcheo" in merged_entries:
        print(f"DEBUG: rcheo in merged_entries: {merged_entries['rcheo']}")

    # 4. Top 100 Definitions
    # "Add definitions for Top 100 Unknowns where possible (e.g. s = Suffix/Marker, r = Marker, l = Liquid/Oil)"
    special_defs = {
        "s": "Suffix/Marker",
        "r": "Marker",
        "l": "Liquid/Oil"
    }
    
    for row in top100_rows:
        word = row.get("Word")
        if word in special_defs:
            entry = {
                "voynich": word,
                "meaning": special_defs[word],
                "language": "voynich_struct",
                "confidence": 0.9,
                "domain": "grammar",
                "source": "manual_top100_v17",
                "evidence": "high_frequency_marker",
                "confidence_level": "HIGH",
                "translation_status": 1
            }
            merged_entries[word] = entry

    # 5. Cleanup
    # Remove duplicates (keys are unique in dict, so implicit)
    # Sort alphabetically
    sorted_keys = sorted(merged_entries.keys())
    sorted_entries = {k: merged_entries[k] for k in sorted_keys}

    # 6. Output
    output_data = {
        "version": "17.0_master",
        "date": datetime.now().isoformat(),
        "entries": sorted_entries
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"Written {output_path} with {len(sorted_entries)} entries.")

    # Generate Summary
    total_entries = len(sorted_entries)
    new_entries = total_entries - len(master_entries)
    
    summary_content = f"""# Track 304 Results Summary: Dictionary v17

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Version:** 17.0

## Overview
Merged findings from Algorithmic Expansion (Track 302) and Contextual Inference (Track 303) into the Master Dictionary.

## Stats
- **Total Entries:** {total_entries}
- **New Entries Added:** {new_entries} (Approximate, includes updates)
- **Base (v16):** {len(master_entries)}
- **Algo Inputs:** {len(algo_entries)}
- **Context Inputs:** {len(context_entries)}

## Changes
- Integrated {len(algo_entries)} algorithmic morphology expansions.
- Integrated {len(context_entries)} context-inferred candidates (High priority).
- Defined key structural markers from Top 100 Unknowns (`s`, `r`, `l`).

## Files
- `results/dictionary/master_dictionary_v17.json`
"""
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"Written summary to {summary_path}")

if __name__ == "__main__":
    main()
