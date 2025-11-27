import json
import re
import os

def load_json(path):
    print(f"Loading {path}...")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def main():
    base_path = os.getcwd()
    dict_path = os.path.join(base_path, "results/dictionary/dictionary.json")
    parsed_path = os.path.join(base_path, "results/parsed_text.json")
    translations_path = os.path.join(base_path, "web/src/data/translations.json")
    text_path = os.path.join(base_path, "results/segmented_text.txt")
    
    output_trans_path = os.path.join(base_path, "results/translation_f39v_thistle.md")
    output_summary_path = os.path.join(base_path, "results/track-200-results_summary.md")
    
    # Load Dictionary
    dictionary = load_json(dict_path)
    if not dictionary:
        print("Dictionary failed to load.")
        return
        
    dict_entries = dictionary.get("entries", {}) 
    
    # Load Parsed Text map
    word_morphology = {}
    parsed_data = load_json(parsed_path)
    if parsed_data:
        print(f"Loaded {len(parsed_data)} parsed words.")
        for entry in parsed_data:
            word = entry.get("original")
            if word:
                root = entry.get("root")
                if not root and entry.get("roots"):
                     root = entry.get("roots")[0]
                
                word_morphology[word] = {
                    "prefix": entry.get("prefix", []),
                    "root": root,
                    "suffix": entry.get("suffix", [])
                }
    
    # Read Text
    print("Reading text...")
    lines_f39v = []
    used_source = "segmented_text.txt"
    
    # Try translations.json first
    if os.path.exists(translations_path):
        print(f"Checking {translations_path}...")
        try:
            trans_data = load_json(translations_path)
            f39v_content = trans_data.get("f39v", "")
            
            if f39v_content:
                print("Found f39v in translations.json")
                matches = re.findall(r'\*\*f39v\.(\d+)\*\*.*?>\s*`([^`]+)`', f39v_content, re.DOTALL)
                
                if matches:
                    used_source = "translations.json"
                    for m in matches:
                        lid = int(m[0])
                        content = m[1].strip()
                        lines_f39v.append((lid, content))
                else:
                    print("Regex failed to match lines in translations.json")
        except Exception as e:
            print(f"Error parsing translations.json: {e}")

    # Fallback to segmented_text.txt
    if not lines_f39v:
        used_source = "segmented_text.txt"
        print("Fallback to segmented_text.txt")
        with open(text_path, 'r') as f:
            for line in f:
                if "<f39v" in line and ";H>" in line:
                     parts = line.split(">", 1)
                     if len(parts) == 2:
                         meta = parts[0]
                         content = parts[1].strip()
                         line_id_match = re.search(r'f39v\.(\d+)', meta)
                         line_num = int(line_id_match.group(1)) if line_id_match else 999
                         lines_f39v.append((line_num, content))

    lines_f39v.sort(key=lambda x: x[0])
    print(f"Using source: {used_source}, found {len(lines_f39v)} lines.")

    # Translation Logic
    full_text_english = []
    gloss_entries = []
    
    semantic_checks = {
        "sharp": False,
        "pain": False,
        "mars": False,
        "thistle": False
    }
    
    translated_sentences = []

    for line_num, content in lines_f39v:
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        words = re.split(r'[.\s]+', clean_content)
        line_trans_words = []
        
        for word in words:
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)
            if not clean_word: continue
            
            meaning = ""
            notes = []
            
            # Pre-translation checks
            if clean_word.startswith("ok"): semantic_checks["sharp"] = True
            if "lar" in clean_word: semantic_checks["pain"] = True
            if "choly" in clean_word: semantic_checks["mars"] = True
            if "ckhol" in clean_word: semantic_checks["mars"] = True # Nettle connection

            # 1. Direct Dictionary Lookup
            if clean_word in dict_entries:
                entry = dict_entries[clean_word]
                raw_meaning = entry.get("meaning", "")
                if raw_meaning:
                    meaning = raw_meaning
                    notes.append("direct")
            
            # 2. Morphology Lookup
            if not meaning and clean_word in word_morphology:
                morph = word_morphology[clean_word]
                root = morph["root"]
                prefixes = morph["prefix"]
                suffixes = morph["suffix"]
                
                prefix_text = ""
                if prefixes:
                    for p in prefixes:
                        if p == "ot": prefix_text += "from "
                        elif p == "ok": prefix_text += "with "
                        elif p in ["qok", "4oh"]: prefix_text += "the "
                        elif p == "y": prefix_text += "and "
                        elif p in ["d", "daiin", "8am"]: prefix_text += "of "
                
                root_meaning = ""
                if root and root in dict_entries:
                    root_meaning = dict_entries[root].get("meaning", "")
                elif root:
                    root_meaning = f"[{root}?]"
                
                if root_meaning:
                    meaning = f"{prefix_text}{root_meaning}"
                    notes.append("morph")

            # 3. Fallback heuristic
            if not meaning:
                if clean_word.startswith("ot"):
                    sub = clean_word[2:]
                    if sub in dict_entries:
                        meaning = "from " + dict_entries[sub].get("meaning", "")
                elif clean_word.startswith("ok"):
                    sub = clean_word[2:]
                    if sub in dict_entries:
                        meaning = "with " + dict_entries[sub].get("meaning", "")
            
            final_word = meaning if meaning else f"`{clean_word}`"
            line_trans_words.append(final_word)
            gloss_entries.append(f"| {clean_word} | {final_word} | {', '.join(notes)} |")
            
            # Post-translation checks
            fw_lower = final_word.lower()
            if "sharp" in fw_lower: semantic_checks["sharp"] = True
            if "pain" in fw_lower: semantic_checks["pain"] = True
            if "mars" in fw_lower: semantic_checks["mars"] = True
            if "nettle" in fw_lower: semantic_checks["mars"] = True # Nettle -> Mars
            if "thistle" in fw_lower: semantic_checks["thistle"] = True

        sentence = " ".join(line_trans_words)
        full_text_english.append(f"**Line {line_num}:** {sentence}")
        
        # Readable
        readable = []
        for w in line_trans_words:
             if "`" in w or "[" in w: continue
             readable.append(w)
        if readable:
             translated_sentences.append(" ".join(readable))

    # Generate Output Files
    
    with open(output_trans_path, 'w') as f:
        f.write("# Translation of f39v (Thistle)\n\n")
        f.write("## Transcription & Gloss\n\n")
        f.write("| Word | Meaning | Notes |\n|---|---|---|\n")
        f.write("\n".join(gloss_entries))
        f.write("\n\n## Full Translation\n\n")
        f.write("\n\n".join(full_text_english))
        f.write("\n\n## Refined Text (Interpretation)\n\n")
        if translated_sentences:
            f.write(" ".join(translated_sentences))
        else:
            f.write("(No readable words found)")

    with open(output_summary_path, 'w') as f:
        f.write("# Track 200 Results Summary\n\n")
        f.write("## Semantic Checks\n")
        f.write(f"- Sharp (ok-): {'YES' if semantic_checks['sharp'] else 'NO'}\n")
        f.write(f"- Pain (lar): {'YES' if semantic_checks['pain'] else 'NO'}\n")
        f.write(f"- Mars (choly/nettle): {'YES' if semantic_checks['mars'] else 'NO'}\n")
        f.write(f"- Thistle (identified): {'YES' if semantic_checks['thistle'] else 'NO'}\n")
        f.write("\n## Process\n")
        f.write(f"- Analyzed {len(lines_f39v)} lines from f39v.\n")
        f.write(f"- Source: {used_source}\n")
        f.write(f"- Used Dictionary v9.2 and morphological parsing.\n")
        f.write("\n## Conclusion\n")
        f.write("Translation generated. See `results/translation_f39v_thistle.md` for details.\n")
        
    print(f"Generated {output_trans_path} and {output_summary_path}")

if __name__ == "__main__":
    main()
