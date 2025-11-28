import json
import re
import os

def load_dictionary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)["entries"]

def strip_suffixes(word):
    suffixes = [
        ('y', 1), ('dy', 2), ('oly', 3), ('ary', 3), 
        ('aiin', 4), ('iin', 3), ('in', 2), 
        ('ol', 2), ('or', 2), ('al', 2), 
        ('s', 1), ('r', 1), ('l', 1), ('n', 1)
    ]
    for suff, length in suffixes:
        if word.endswith(suff) and len(word) > length + 1:
            return word[:-length], suff
    return word, ""

def get_section(page_id):
    if not page_id: return "Unknown"
    if page_id.startswith("f10") or page_id.startswith("f11"): return "Recipes"
    
    match = re.search(r'\d+', page_id)
    if not match: return "Unknown"
    num = int(match.group())
    
    if 75 <= num <= 84: return "Bio"
    return "Other"

def produce_translation(input_file, dict_file, output_file):
    print("Generating The Medical Manual...")
    entries = load_dictionary(dict_file)
    
    lines_out = []
    current_page = ""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Page Header
            match = re.match(r"<(f\d+[rv]\d?)\.", line)
            if match:
                new_page = match.group(1)
                if new_page != current_page:
                    current_page = new_page
                    section = get_section(current_page)
                    if section in ["Recipes", "Bio"]:
                        lines_out.append(f"\n## Page {current_page} ({section})\n")
                    else:
                        continue # Skip non-target pages
            
            if get_section(current_page) not in ["Recipes", "Bio"]: continue
            if line.startswith("#"): continue
            
            # Tokenize
            cleaned = line.replace(".", " ").replace("!", "").replace("*", "")
            words = cleaned.split()
            translated_line = []
            
            for w in words:
                if w.startswith("<") or w == "-": continue
                
                word_clean = w
                
                # Lookup
                defn = ""
                suffix = ""
                
                if word_clean in entries:
                    defn = entries[word_clean]['meaning']
                else:
                    root, suff = strip_suffixes(word_clean)
                    if root in entries:
                        defn = entries[root]['meaning']
                        suffix = suff
                    else:
                        defn = f"?{word_clean}"
                
                # Semantic Polish
                # Clean up the definition string
                defn = defn.split(';')[0].split('/')[0].strip()
                defn = defn.replace("[ROOT]", "").strip()
                defn = defn.replace("Morphological Root", "").strip()
                
                # Capitalize Verbs/Nouns
                if "Cook" in defn: defn = "**Cook**"
                if "Mix" in defn: defn = "**Mix**"
                if "Liquid" in defn: defn = "Liquid"
                if "Star" in defn: defn = "Star"
                
                # Suffix grammar hints (from Track 317)
                grammar = ""
                if suffix == "y": grammar = " (End)"
                if suffix == "ol": grammar = " (Noun)"
                
                # Final Token
                if defn.startswith("?"):
                    translated_line.append(defn)
                else:
                    translated_line.append(f"[{defn}]")
            
            if translated_line:
                lines_out.append(" ".join(translated_line))

    # Write File
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# The Voynich Medical Manual\n")
        f.write("## Translated by Cursor Agent (Iteration 102)\n")
        f.write("### Sections: Recipes (Quire 20) & Bio (Quire 13)\n\n")
        f.write("---\n")
        for l in lines_out:
            f.write(l + "\n")
            
    print(f"Translation saved to {output_file}")

if __name__ == "__main__":
    produce_translation(
        "data/eva_ivtff.txt",
        "results/dictionary/master_dictionary_v18.json",
        "translated/THE_VOYNICH_MEDICAL_MANUAL.md"
    )
