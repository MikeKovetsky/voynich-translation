import json
import os
from datetime import datetime

MASTER_DICT_PATH = "results/dictionary/dictionary.json"
UPDATE_FILE_PATH = "results/dictionary_update_v3.json"
TOP_UNKNOWNS_PATH = "results/top_unknowns_v3.md"
REPORT_PATH = "results/track-226-merge_report.md"

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def parse_top_unknowns():
    freq_map = {}
    try:
        with open(TOP_UNKNOWNS_PATH, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                # Expected format: | Rank | Word | Freq | ...
                # split results in ['', 'Rank', 'Word', 'Freq', '']
                if len(parts) >= 4 and parts[2] != 'Word' and parts[2] != '---':
                    word = parts[2]
                    try:
                        freq = int(parts[3])
                        freq_map[word] = freq
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"Warning: {TOP_UNKNOWNS_PATH} not found.")
    return freq_map

def main():
    print("Loading dictionaries...")
    master_data = load_json(MASTER_DICT_PATH)
    update_data = load_json(UPDATE_FILE_PATH)
    freq_map = parse_top_unknowns()

    master_entries = master_data.get("entries", {})
    
    added_count = 0
    updated_count = 0
    added_words = []
    
    print("Merging entries...")
    # The update file format might be a dict of entries or a list. 
    # Usually dictionary updates are dicts {word: {details}}. 
    # Let's assume dict based on standard format.
    # If update_data has "entries" key, use that, else assume it's the entries dict itself.
    updates = update_data.get("entries", update_data)

    for word, details in updates.items():
        # Ensure word is lowercase for consistency
        word = word.lower() 
        
        if word not in master_entries:
            # New entry
            new_entry = details.copy()
            new_entry["source"] = "Track224_Morphology_v3"
            new_entry["confidence"] = 0.85
            new_entry["voynich"] = word
            master_entries[word] = new_entry
            added_count += 1
            added_words.append(word)
        else:
            # Existing entry - check if we should update
            current_entry = master_entries[word]
            current_meaning = current_entry.get("meaning", "")
            new_meaning = details.get("meaning", "")
            
            # Update if current is vague and new is specific
            is_current_vague = not current_meaning or current_meaning == "unknown" or "uncertain" in current_meaning
            is_new_specific = new_meaning and new_meaning != "unknown"
            
            if is_current_vague and is_new_specific:
                # Update meaning and potentially other fields, but preserve original source history if possible?
                # The task says "Update it (but log the change)".
                # We will overwrite for now but maybe append to source or notes if we want to be careful.
                # Task says "If so, update it".
                master_entries[word]["meaning"] = new_meaning
                master_entries[word]["source"] = f"{current_entry.get('source', 'Unknown')} + Track224_Morphology_v3"
                # Merge other fields if present in update
                for k, v in details.items():
                    if k not in ["source", "confidence"]: # Don't lower confidence if existing is higher?
                        master_entries[word][k] = v
                
                updated_count += 1

    # Update metadata
    master_data["version"] = "9.1"
    master_data["date"] = datetime.now().isoformat()
    master_data["entries"] = master_entries
    
    print(f"Saving merged dictionary to {MASTER_DICT_PATH}...")
    save_json(master_data, MASTER_DICT_PATH)
    
    # Generate Report
    print("Generating report...")
    
    # Find top added words by frequency
    added_with_freq = []
    for w in added_words:
        freq = freq_map.get(w, 0)
        added_with_freq.append((w, freq))
    
    # Sort by freq desc
    added_with_freq.sort(key=lambda x: x[1], reverse=True)
    top_5 = added_with_freq[:5]
    
    report_content = f"""# Track 226 Merge Report

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Dictionary Version:** 9.1

## Summary
- **Total Entries Added:** {added_count}
- **Total Entries Updated:** {updated_count}

## Top 5 Added Words (by Frequency)
"""
    
    if top_5:
        report_content += "| Word | Frequency | Meaning |\n|---|---|---|\n"
        for w, freq in top_5:
            meaning = master_entries[w].get("meaning", "unknown")
            report_content += f"| {w} | {freq} | {meaning} |\n"
    else:
        report_content += "No new words found in Top Unknowns list.\n"

    with open(REPORT_PATH, 'w') as f:
        f.write(report_content)
        
    print(f"Report saved to {REPORT_PATH}")
    print("Done.")

if __name__ == "__main__":
    main()
