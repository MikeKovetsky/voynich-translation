import json
import re
import os

def load_dictionary(filepath):
    print(f"Loading dictionary from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("entries", {})

def strip_suffixes(word):
    # Logic from research/morphology_engine.py
    # Common EVA suffixes based on visual structure
    suffixes = [
        ('y', 1), ('dy', 2), ('oly', 3), ('ary', 3), 
        ('aiin', 4), ('iin', 3), ('in', 2), 
        ('ol', 2), ('or', 2), ('al', 2), 
        ('s', 1), ('r', 1), ('l', 1), ('n', 1)
    ]
    
    # Try to match longest suffix first
    # Only strip if remainder is at least 2 chars (to avoid stripping 'or' to '')
    for suff, length in suffixes:
        if word.endswith(suff) and len(word) > length + 1:
            return word[:-length]
            
    return word

def translate_blind_set(input_file, dict_file, output_file):
    dictionary = load_dictionary(dict_file)
    
    print(f"Reading input from {input_file}...")
    translated_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("###"):
                translated_lines.append(f"\n{line}\n")
                continue
                
            # Clean and split
            # Remove markers like <->, <!plant>, <$>
            cleaned_line = re.sub(r"<[^>]+>", " ", line)
            # Remove ! and *
            cleaned_line = cleaned_line.replace("!", "").replace("*", "")
            
            words = [w for w in cleaned_line.split('.') if w and w != "-"]
            
            line_translation = []
            for word in words:
                root = strip_suffixes(word)
                
                # Look up in dictionary
                entry = dictionary.get(root)
                if entry:
                    meaning = entry.get("meaning", "???")
                    # simplified output for readability
                    line_translation.append(f"[{meaning}]")
                else:
                    # Try looking up original word if root lookup failed?
                    # The requirement says "Look up the Root". 
                    # If I strictly follow "Translate ... using ONLY the Root Dictionary", 
                    # I should probably only check the root. 
                    # However, if the word didn't have a suffix, root == word.
                    # If it had a suffix, checking the unstripped word might be cheating the "Root Only" test.
                    # But usually if the root isn't found, it might be because it's a proper noun or exact match.
                    # I will stick to the stripped root lookup as per instructions:
                    # "Strip the suffix... Look up the Root... If Root not found, output [ROOT-?]"
                    line_translation.append(f"[{root}-?]")
            
            if line_translation:
                translated_lines.append(" ".join(line_translation))

    print(f"Writing translation to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Blind Root Translation (Track 318)\n")
        f.write("Method: Strip Suffix -> Lookup Root -> Output Meaning\n")
        f.write("Dictionary: master_dictionary_v17.json\n\n")
        
        for line in translated_lines:
            f.write(line + "\n")
            
    print("Done.")

if __name__ == "__main__":
    INPUT_FILE = "data/blind_set_raw.txt"
    DICT_FILE = "results/dictionary/master_dictionary_v17.json"
    OUTPUT_FILE = "results/blind_translation_v1.md"
    
    translate_blind_set(INPUT_FILE, DICT_FILE, OUTPUT_FILE)
