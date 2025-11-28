import json
import re
from pathlib import Path

INPUT_FILE = Path("results/dictionary/master_dictionary_v19.json")
OUTPUT_FILE = Path("results/dictionary/master_dictionary_v20.json")
REPORT_FILE = Path("results/sanitization_report.md")

def sanitize_dictionary():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_count = len(data['entries'])
    kept_entries = {}
    removed_entries = []

    # Regex for valid Voynich words:
    # - Must contain at least one letter (a-z)
    # - Can contain specific Voynich symbols if mapped (we assume lower case ascii for EVA)
    # - Should NOT contain !, ?, digits, or special punctuation other than maybe - or '
    # - Length limit: 15 chars (Voynich words are rarely that long)
    
    valid_pattern = re.compile(r'^[a-z\-\']+$')

    for key, entry in data['entries'].items():
        # 1. Basic cleaning of the key
        clean_key = key.strip()
        
        # 2. Filtering Logic
        reason = None
        
        if not clean_key:
            reason = "Empty key"
        elif "!" in clean_key or "?" in clean_key:
            reason = "Contains invalid punctuation (!?)"
        elif len(clean_key) > 15:
            reason = "Too long (>15 chars)"
        elif len(clean_key) < 1:
             reason = "Too short"
        elif not valid_pattern.match(clean_key):
            # Allow standard EVA chars. If it has *, @, numbers, reject.
            reason = "Invalid characters (non-EVA)"
        
        if reason:
            removed_entries.append((key, reason))
        else:
            kept_entries[clean_key] = entry

    # Save v20
    data['entries'] = kept_entries
    data['version'] = "20.0"
    data['description'] = "Sanitized version of v19. Removed parser artifacts."
    
    print(f"Saving {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=True)

    # Generate Report
    report = [
        "# Dictionary Sanitization Report (v19 -> v20)",
        f"",
        f"- **Original Entries:** {original_count}",
        f"- **Kept Entries:** {len(kept_entries)}",
        f"- **Removed Entries:** {len(removed_entries)}",
        f"- **Reduction:** {len(removed_entries)/original_count*100:.2f}%",
        "",
        "## Removal Examples",
        "| Key | Reason |",
        "| --- | --- |"
    ]
    
    # Show first 20 and last 20 removals
    sample = removed_entries[:20] + removed_entries[-20:] if len(removed_entries) > 40 else removed_entries
    
    for key, reason in sample:
        report.append(f"| `{key}` | {reason} |")

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"Sanitization complete. Removed {len(removed_entries)} entries.")

if __name__ == "__main__":
    sanitize_dictionary()
