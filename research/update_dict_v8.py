import json
import os
from datetime import datetime

def update_dictionary():
    input_file = "results/master_dictionary_v7_4.json"
    clusters_file = "results/word_clusters.json"
    synonyms_file = "results/synonym_candidates.json"
    semantic_file = "results/semantic_field_candidates.json"
    
    output_file = "results/master_dictionary_v8_0.json"
    report_file = "results/dictionary_v8_report.md"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading dictionary from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
        entries = data.get("entries", data)

    # Track updates
    updates = []
    new_entries = []
    
    # 1. Load clusters
    if os.path.exists(clusters_file):
        print("Loading clusters...")
        with open(clusters_file, 'r') as f:
            clusters = json.load(f)
            
        for word, info in clusters.items():
            conf = info.get("confidence", 0)
            category = info.get("predicted_category", "Unknown")
            
            # Threshold: 0.7 confidence, ignore "Other" or "Unknown"
            if conf >= 0.7 and category not in ["Other", "Unknown"]:
                meaning_str = f"[{category.upper()}]"
                
                if word in entries:
                    curr = entries[word]
                    old_meaning = curr.get("meaning", "")
                    # Update if current meaning is unknown or weak
                    if old_meaning in ["Unknown", ""] or old_meaning.startswith("["):
                         if old_meaning != meaning_str:
                            updates.append(f"Cluster: {word} -> {meaning_str}")
                            entries[word]["meaning"] = meaning_str
                            entries[word]["confidence"] = max(entries[word].get("confidence", 0), conf)
                            entries[word]["source"] = "Cluster Analysis"
                else:
                    entries[word] = {
                        "word": word,
                        "meaning": meaning_str,
                        "confidence": conf,
                        "source": "Cluster Analysis"
                    }
                    new_entries.append(f"Cluster: {word} -> {meaning_str}")

    # 2. Load Synonyms
    if os.path.exists(synonyms_file):
        print("Loading synonyms...")
        with open(synonyms_file, 'r') as f:
            syns = json.load(f)
            
        # Specifically handle qol -> ol
        # And general high confidence synonyms
        for item in syns:
            w1 = item["word"]
            w2 = item["match"]
            
            if w1 == "qol" and w2 == "ol":
                # Hardcode per instructions
                if w1 in entries:
                     entries[w1]["meaning"] = "The (syn: ol)"
                     updates.append(f"Synonym: qol -> The (syn: ol)")
            
            # If w2 has a strong meaning, and w1 is unknown, link them
            if w2 in entries and entries[w2].get("meaning") not in ["Unknown", ""]:
                w2_mean = entries[w2]["meaning"]
                if w1 in entries:
                    if entries[w1].get("meaning", "Unknown") == "Unknown":
                        entries[w1]["meaning"] = f"{w2_mean} (syn: {w2})"
                        updates.append(f"Synonym: {w1} -> {w2_mean} (syn: {w2})")

    # 3. Load Semantic Fields (Colors)
    if os.path.exists(semantic_file):
        print("Loading semantic fields...")
        with open(semantic_file, 'r') as f:
            sem = json.load(f)
            
        colors = sem.get("colors", {})
        for color, items in colors.items():
            for item in items:
                word = item["word"]
                # Top 5 per color or high score?
                # Let's take all unique ones or high score. The file had score 999.0.
                if item.get("score", 0) > 10: # Arbitrary threshold
                    meaning = f"[COLOR_{color.upper()}]"
                    if word in entries:
                         if entries[word].get("meaning", "Unknown") == "Unknown":
                             entries[word]["meaning"] = meaning
                             updates.append(f"Color: {word} -> {meaning}")
                    else:
                        entries[word] = {
                            "word": word,
                            "meaning": meaning,
                            "confidence": 0.6,
                            "source": "Color Analysis"
                        }
                        new_entries.append(f"Color: {word} -> {meaning}")

    # Save
    output_data = {
        "version": "8.0",
        "date": datetime.now().isoformat(),
        "total_entries": len(entries),
        "entries": entries
    }
    
    print(f"Saving {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Report
    print(f"Generating report {report_file}...")
    with open(report_file, 'w') as f:
        f.write("# Dictionary v8.0 Report\n\n")
        f.write(f"Total Entries: {len(entries)}\n")
        f.write(f"New Entries: {len(new_entries)}\n")
        f.write(f"Updates: {len(updates)}\n")
        f.write("\n## Sample Updates\n")
        for u in updates[:50]:
            f.write(f"- {u}\n")
        f.write("\n## Sample New Entries\n")
        for u in new_entries[:50]:
             f.write(f"- {u}\n")

    print("Done.")

if __name__ == "__main__":
    update_dictionary()
