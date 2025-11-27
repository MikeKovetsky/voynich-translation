import json
import shutil
from datetime import datetime

MASTER_PATH = 'results/dictionary/dictionary.json'
DRAFT_PATH = 'results/dictionary_update_v10_draft.json'
OUTPUT_PATH = 'results/dictionary/dictionary.json'
REPORT_PATH = 'results/track-234-merge_report.md'

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def merge_dictionaries():
    print("Loading dictionaries...")
    master = load_json(MASTER_PATH)
    draft = load_json(DRAFT_PATH)

    print(f"Master version: {master.get('version', 'unknown')}")
    print(f"Master entries: {len(master.get('entries', {}))}")
    print(f"Draft entries: {len(draft)}")

    # Backup master
    backup_path = MASTER_PATH.replace('.json', '_backup_v9.1.json')
    shutil.copy(MASTER_PATH, backup_path)
    print(f"Backed up master to {backup_path}")

    merged_count = 0
    new_count = 0
    updated_count = 0

    report_lines = []
    report_lines.append("# Track 234 Merge Report: Dictionary v10.0")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Base Version:** {master.get('version')}")
    report_lines.append("")

    # Merge draft into master
    entries = master['entries']
    
    for key, draft_entry in draft.items():
        if key in entries:
            # Update existing
            # We do a field-level update to preserve existing fields not in draft if any?
            # Or do we overwrite? "Update the Master Dictionary with the proven Elemental Logic".
            # Usually we merge fields.
            original_entry = entries[key]
            
            # Check if anything changed
            changed = False
            changes = []
            for k, v in draft_entry.items():
                if original_entry.get(k) != v:
                    original_entry[k] = v
                    changed = True
                    changes.append(k)
            
            if changed:
                updated_count += 1
                # report_lines.append(f"- Updated `{key}`: {', '.join(changes)}")
        else:
            # New entry
            entries[key] = draft_entry
            new_count += 1
            # report_lines.append(f"- Added `{key}`")

    merged_count = updated_count + new_count
    
    report_lines.append("## Merge Statistics")
    report_lines.append(f"- **Total Entries Processed from Draft:** {len(draft)}")
    report_lines.append(f"- **New Entries Added:** {new_count}")
    report_lines.append(f"- **Existing Entries Updated:** {updated_count}")
    report_lines.append("")

    # Specific Overrides
    report_lines.append("## Specific Overrides Applied")
    
    # 1. ald and choly humoral_quality
    for word in ['ald', 'choly']:
        if word in entries:
            entries[word]['humoral_quality'] = "Hot/Dry"
            report_lines.append(f"- `{word}`: Set `humoral_quality` to `Hot/Dry`")
        else:
             report_lines.append(f"- Warning: `{word}` not found for override.")

    # 2. ol and o tagged as Elemental Particles
    for word in ['ol', 'o']:
        if word in entries:
            # Assuming "tagged as Elemental Particles" means adding a field
            # Based on analysis, I will add "type": "elemental_particle"
            # and ensure "category" is "elemental" if not present.
            entries[word]['type'] = "elemental_particle"
            entries[word]['category'] = "elemental" # reinforcing
            report_lines.append(f"- `{word}`: Tagged as `elemental_particle` (type) and `elemental` (category)")
        else:
            report_lines.append(f"- Warning: `{word}` not found for override.")

    # Bump version
    master['version'] = "10.0"
    master['date'] = datetime.now().isoformat()
    
    report_lines.append("")
    report_lines.append(f"## Final Status")
    report_lines.append(f"- **New Version:** 10.0")
    report_lines.append(f"- **Total Entries in Master:** {len(entries)}")

    # Save
    save_json(master, OUTPUT_PATH)
    print(f"Saved v10.0 to {OUTPUT_PATH}")

    # Save Report
    with open(REPORT_PATH, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"Saved report to {REPORT_PATH}")

if __name__ == "__main__":
    merge_dictionaries()
