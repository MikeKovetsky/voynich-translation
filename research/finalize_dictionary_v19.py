import json
import os
import csv

def finalize_dictionary(input_dict_file, plant_file, astro_file, output_dict_file, report_file):
    print(f"Finalizing Dictionary v19...")
    
    # Load Data
    with open(input_dict_file, 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    entries = dictionary.get("entries", {})
    
    updates = 0
    new_entries = 0
    
    # 1. Update Plants (from CSV)
    if os.path.exists(plant_file):
        with open(plant_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row['voynich_word']
                profile = row['profile']
                candidates = row['candidates']
                
                if word in entries:
                    # Update Definition
                    if "Generic" in entries[word]['meaning']:
                        entries[word]['meaning'] = f"{profile} ({candidates})"
                    else:
                        entries[word]['meaning'] += f" / {profile}"
                    
                    entries[word]['confidence'] = 0.8
                    entries[word]['source'] = "Track330_FunctionalID"
                    updates += 1

    # 2. Update Astro (from MD)
    if os.path.exists(astro_file):
        with open(astro_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Parse the MD sections
        current_freq = 0
        for line in lines:
            if "appearing 12 times" in line:
                current_freq = 12
            elif "appearing 11 times" in line or "appearing 13 times" in line:
                current_freq = 11 # Close enough
            elif "appearing" in line:
                current_freq = 0
                
            if current_freq > 0 and "," in line:
                words = [w.strip().replace("*", "") for w in line.split(",")]
                for w in words:
                    if not w or w == "?": continue
                    
                    label = "[ZODIAC_CANDIDATE]" if current_freq == 12 else "[ZODIAC_POSSIBLE]"
                    
                    if w in entries:
                        entries[w]['meaning'] = label
                        entries[w]['confidence'] = 0.7
                        updates += 1
                    else:
                        entries[w] = {
                            "voynich": w,
                            "meaning": label,
                            "confidence": 0.7,
                            "source": "Track331_AstroMiner"
                        }
                        new_entries += 1

    # Save
    dictionary["version"] = "19.0"
    dictionary["entries"] = entries
    
    with open(output_dict_file, 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, indent=2)
        
    # Report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Dictionary v19 Stats\n\n")
        f.write(f"- **Total Entries:** {len(entries)}\n")
        f.write(f"- **Updates:** {updates}\n")
        f.write(f"- **New Entries:** {new_entries}\n")
        f.write("\n## Key Functional Definitions\n")
        
        # List examples
        example_count = 0
        for w, d in entries.items():
            if "Boil" in d['meaning'] or "Infusion" in d['meaning']:
                f.write(f"- **{w}**: {d['meaning']}\n")
                example_count += 1
                if example_count > 10: break

    print(f"Finalization complete: {output_dict_file}")

if __name__ == "__main__":
    finalize_dictionary(
        "results/dictionary/master_dictionary_v18.json",
        "results/plant_id_proposals.csv",
        "results/astro_structure_analysis.md",
        "results/dictionary/master_dictionary_v19.json",
        "results/dictionary_v19_stats.md"
    )
