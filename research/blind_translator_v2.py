import json
import re
import os

def load_dictionary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def strip_suffixes(word):
    # Simple suffix stripper matching Track 312 logic
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

def translate_blind_v2(input_file, dict_file, output_file):
    print("Running Blind Translation v2...")
    
    dictionary = load_dictionary(dict_file)
    entries = dictionary.get("entries", {})
    
    lines_out = []
    total_words = 0
    known_words = 0
    root_matches = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                lines_out.append(line)
                continue
            
            # Handle <tags> separately if they exist
            # But for EVA data like "word.word.word", we need to split by dot
            # First, preserve tags
            
            # Remove tags for simple text processing (or keep them)
            # Let's just grab the text part.
            # The format in blind_set_raw.txt is just raw lines of text, likely containing dots.
            
            # Replace dots with spaces to normalize
            normalized_line = line.replace(".", " ")
            words = normalized_line.split()
            
            translated_line = []
            
            for word in words:
                # Skip tags like <f1r...> or <->
                if word.startswith("<") or word.startswith("$"):
                    translated_line.append(word)
                    continue
                
                word_clean = word.replace("!", "").replace("*", "")
                if not word_clean or word_clean == "-": continue
                
                total_words += 1
                
                # 1. Exact Match
                if word_clean in entries:
                    defn = entries[word_clean]['meaning']
                    defn = defn.split(';')[0].split('/')[0].strip()
                    translated_line.append(f"[{defn}]")
                    known_words += 1
                    
                # 2. Root Match
                else:
                    root, suff = strip_suffixes(word_clean)
                    if root in entries:
                        defn = entries[root]['meaning']
                        defn = defn.split(';')[0].split('/')[0].strip()
                        defn = defn.replace("[ROOT]", "").strip()
                        translated_line.append(f"[{defn} +{suff}]")
                        root_matches += 1
                    else:
                        translated_line.append(f"[?{root}]")
                        
            lines_out.append(" ".join(translated_line))

    # Write Output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Blind Translation Round 2\n\n")
        
        # Stats
        known_pct = 0
        root_pct = 0
        total_readable = 0
        
        if total_words > 0:
            known_pct = (known_words / total_words) * 100
            root_pct = (root_matches / total_words) * 100
            total_readable = known_pct + root_pct
        
        f.write(f"- **Total Words:** {total_words}\n")
        f.write(f"- **Exact Matches:** {known_words} ({known_pct:.1f}%)\n")
        f.write(f"- **Root Matches:** {root_matches} ({root_pct:.1f}%)\n")
        f.write(f"- **Total Readability:** {total_readable:.1f}%\n\n")
        f.write("---\n\n")
        
        for line in lines_out:
            f.write(line + "\n")

    print(f"Translation complete. Readability: {total_readable:.1f}%")

if __name__ == "__main__":
    translate_blind_v2(
        "data/blind_set_raw.txt",
        "results/dictionary/master_dictionary_v18.json",
        "results/blind_translation_v2.md"
    )
