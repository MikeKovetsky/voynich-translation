import json
import os
import csv

def patch_dictionary(roots_file, starters_file, section_file, input_dict_file, output_dict_file, report_file):
    print(f"Patching dictionary...")
    
    # Load Data
    with open(input_dict_file, 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    
    roots = []
    if os.path.exists(roots_file):
        with open(roots_file, 'r', encoding='utf-8') as f:
            roots = [line.strip() for line in f if line.strip()]
            
    starters = {}
    if os.path.exists(starters_file):
        with open(starters_file, 'r', encoding='utf-8') as f:
            # Format: Rank | Word | ...
            for line in f:
                if "|" in line and "Rank" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) > 2:
                        word = parts[2].replace("**", "")
                        starters[word] = "Sentence Starter / Particle"

    section_map = {}
    if os.path.exists(section_file):
        with open(section_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None) # Skip header
            for row in reader:
                if len(row) >= 3:
                    root = row[0]
                    section = row[1]
                    try:
                        dom_str = row[2].replace("%", "").strip()
                        if dom_str:
                            dom = float(dom_str)
                            if dom > 50:
                                section_map[root] = f"{section} Term"
                            if dom > 80:
                                section_map[root] = f"Specialized {section} Term"
                    except ValueError:
                        continue

    # Patching
    added_roots = 0
    updated_starters = 0
    updated_syntax = 0
    
    entries = dictionary.get("entries", {})
    
    # 1. Add Roots
    for root in roots:
        if root not in entries:
            meaning = section_map.get(root, "Morphological Root")
            entries[root] = {
                "voynich": root,
                "meaning": f"[ROOT] {meaning}",
                "confidence": 0.5,
                "source": "Track322_AutoPatch"
            }
            added_roots += 1
        else:
            # Update existing
            if root in section_map:
                 entries[root]["meaning"] += f" ({section_map[root]})"

    # 2. Add Starters
    for word, meaning in starters.items():
        if word in entries:
            entries[word]["meaning"] += f" / {meaning}"
            entries[word]["pos"] = "Particle"
        else:
            entries[word] = {
                "voynich": word,
                "meaning": f"[STARTER] {meaning}",
                "confidence": 0.6,
                "source": "Track322_AutoPatch"
            }
        updated_starters += 1
        
    # 3. Syntax Updates (Hardcoded from findings)
    syntax_updates = {
        "qokeey": "Cook (Verb - Pos 3)",
        "sho": "Fire/Heat (Noun/Imperative - Pos 1)",
        "saiin": "Star/Topic (Particle - Pos 1)",
        "sal": "Salt (Object - Pos End)"
    }
    
    for word, defn in syntax_updates.items():
        if word in entries:
            entries[word]["meaning"] = defn
            entries[word]["confidence"] = 0.9
            updated_syntax += 1

    dictionary["entries"] = entries
    dictionary["version"] = "18.0"
    
    # Save
    with open(output_dict_file, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, indent=2)
        
    # Report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Dictionary Patch Report v18\n\n")
        f.write(f"- **Added Roots:** {added_roots}\n")
        f.write(f"- **Updated Starters:** {updated_starters}\n")
        f.write(f"- **Syntax Fixes:** {updated_syntax}\n")
        f.write(f"- **Total Entries:** {len(entries)}\n\n")
        f.write("## Key Definitions Updated\n")
        for w in syntax_updates:
            f.write(f"- **{w}**: {entries[w]['meaning']}\n")

    print(f"Patch complete. Report: {report_file}")

if __name__ == "__main__":
    patch_dictionary(
        "artifacts/top_roots.txt",
        "artifacts/top_starters.txt",
        "artifacts/roots_by_section.csv",
        "results/dictionary/master_dictionary_v17.json",
        "results/dictionary/master_dictionary_v18.json",
        "results/dictionary_patch_report.md"
    )
