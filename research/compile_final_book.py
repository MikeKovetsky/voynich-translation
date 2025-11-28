import json
import os

def compile_book(text_file, dict_file, methodology_file, output_file):
    print("Compiling Final Book...")
    
    # Load Components
    translation = ""
    if os.path.exists(text_file):
        with open(text_file, 'r', encoding='utf-8') as f:
            translation = f.read()
        
    methodology = ""
    if os.path.exists(methodology_file):
        with open(methodology_file, 'r', encoding='utf-8') as f:
            methodology = f.read()
        
    # Create Stats from Dictionary
    entries = {}
    if os.path.exists(dict_file):
        with open(dict_file, 'r', encoding='utf-8') as f:
            d = json.load(f)
            entries = d.get("entries", {})
        
    # Build Content
    content = []
    
    content.append("# VOYNICH DECODED: The Medical-Astrological Manual")
    content.append("## A Functional Translation by The Voynich Project")
    content.append("### Date: 2025-11-27\n")
    
    content.append("## Part 1: Introduction")
    content.append("The Voynich Manuscript is a medieval handbook for preparation of herbal remedies (Quire 20) and their application in balneotherapy (Quire 13). This translation demonstrates the specific 'Boiling' and 'Infusion' instructions encoded in the text.\n")
    
    content.append("## Part 2: Methodology")
    content.append(methodology)
    
    content.append("\n## Part 3: The Translation (Quire 20 & Bio)")
    content.append(translation)
    
    content.append("\n## Part 4: The Dictionary (Top Terms)")
    content.append("| Word | Meaning | Confidence |")
    content.append("|---|---|---|")
    
    # Top 50 words
    count = 0
    sorted_entries = sorted(entries.items(), key=lambda x: x[1].get("confidence", 0), reverse=True)
    
    for w, data in sorted_entries:
        conf = data.get("confidence", 0)
        meaning = data.get("meaning", "Unknown")
        
        if conf >= 0.8:
            content.append(f"| **{w}** | {meaning} | {conf} |")
            count += 1
            if count > 100: break
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
        
    print(f"Book compiled: {output_file}")

if __name__ == "__main__":
    compile_book(
        "translated/THE_VOYNICH_MEDICAL_MANUAL_CLEAN.md",
        "results/dictionary/master_dictionary_v19.json",
        "progress/103.txt",
        "published/VOYNICH_DECODED.md"
    )
