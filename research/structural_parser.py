import json
import re
import os

def load_dictionary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)["entries"]

def parse_structure(input_file, dict_file, output_file):
    print("Running Structural Parser...")
    entries = load_dictionary(dict_file)
    
    parsed_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                parsed_lines.append(line.strip())
                continue
                
            # Fix: Split by dot and space
            normalized_line = line.replace(".", " ")
            words = normalized_line.split()
            
            structure = []
            
            # States: START -> PARTICLE -> TOPIC -> VERB -> OBJECT
            
            for word in words:
                if word.startswith("<"): continue
                w = word.replace("!", "").replace("*", "")
                if not w or w == "-": continue
                
                role = "UNK"
                if w in entries:
                    meaning = entries[w]["meaning"].lower()
                    if "particle" in meaning or "starter" in meaning or "fire/heat" in meaning:
                        role = "PART"
                    elif "verb" in meaning or "cook" in meaning or "mix" in meaning:
                        role = "VERB"
                    elif "object" in meaning or "salt" in meaning or "ingredient" in meaning:
                        role = "OBJ"
                
                # Root fallback for Verbs
                if role == "UNK":
                    if w.startswith("qok"): role = "VERB"
                    
                # Formatting
                if role == "PART":
                    structure.append(f"**({role}) {w}**")
                elif role == "VERB":
                    structure.append(f"__({role}) {w}__")
                elif role == "OBJ":
                    structure.append(f"[({role}) {w}]")
                else:
                    structure.append(w)
            
            parsed_lines.append(" ".join(structure))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Structural Parse v1 (Particle-Topic-Verb)\n\n")
        f.write("Legend: **(PART) Particle** | __(VERB) Action__ | [(OBJ) Object]\n\n")
        for line in parsed_lines:
            f.write(line + "\n")
            
    print(f"Parsing complete: {output_file}")

if __name__ == "__main__":
    parse_structure(
        "data/blind_set_raw.txt",
        "results/dictionary/master_dictionary_v18.json",
        "results/structural_parse_v1.md"
    )
