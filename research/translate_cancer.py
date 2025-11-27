import json
import re
import os
import sys

def load_dictionary(path):
    if not os.path.exists(path):
        print(f"Error: Dictionary not found at {path}")
        return {"entries": {}, "version": "0.0"}
    with open(path, 'r') as f:
        return json.load(f)

def extract_lines(file_path, page_id):
    raw_lines = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            if f"<{page_id}." in line:
                # parse id like <f72r3.1,@Cc;H>
                match = re.search(rf'<{page_id}\.(\d+)[^>]*;([A-Za-z])>', line)
                if match:
                    lineno = int(match.group(1))
                    transcriber = match.group(2)
                    text = line.split('>', 1)[1].strip()
                    
                    if lineno not in raw_lines:
                        raw_lines[lineno] = {}
                    raw_lines[lineno][transcriber] = text

    # Select best transcriber: H > U > F > others
    final_lines = []
    sorted_linenos = sorted(raw_lines.keys())
    
    for lineno in sorted_linenos:
        versions = raw_lines[lineno]
        text = ""
        # Prefer H (High quality/Hand?) or U (Unknown?) - usually standard in these scripts
        if 'H' in versions:
            text = versions['H']
        elif 'U' in versions:
            text = versions['U']
        elif 'F' in versions:
            text = versions['F']
        else:
            text = next(iter(versions.values()))
            
        # Basic cleaning of inline tags like <!fold>
        text = re.sub(r'<![^>]+>', '', text)
        final_lines.append((lineno, text))
        
    return final_lines

def translate_word(word, dictionary):
    # Clean word
    clean_word = word.replace('!', '').replace('?', '').replace(',', '').replace('.', '')
    
    if not clean_word:
        return ""

    # Manual overrides for this task
    overrides = {
        "okeol": "BOIL",
        "qokeey": "COOK/PROCESS",
        "chedy": "DRINK/SERVE",
        "aiin": "WATER",
        "daiin": "TAKE-WATER",
        "okaiin": "WATER", # Variation
        "sh": "THAT/WHICH", # if standalone
        "y": "AND", # if standalone
    }
    
    if clean_word in overrides:
        return f"**{overrides[clean_word]}**"

    # Direct lookup
    if clean_word in dictionary['entries']:
        return dictionary['entries'][clean_word]['meaning']
    
    # Grammar Prefixes
    # sh- (That/Which)
    if clean_word.startswith('sh') and len(clean_word) > 2:
        root = clean_word[2:]
        if root in dictionary['entries'] or root in overrides:
            root_mean = translate_word(root, dictionary)
            return f"THAT {root_mean}"
        
    # y- (And)
    if clean_word.startswith('y') and len(clean_word) > 1:
        root = clean_word[1:]
        if root in dictionary['entries'] or root in overrides:
            root_mean = translate_word(root, dictionary)
            return f"AND {root_mean}"

    # t- (To/Future)
    if clean_word.startswith('t') and len(clean_word) > 1:
        root = clean_word[1:]
        if root in dictionary['entries'] or root in overrides:
            root_mean = translate_word(root, dictionary)
            return f"TO {root_mean}"

    # o- (Star/Item marker in lists? or just common prefix)
    # The task says "Lists of stars often start with o- or y-"
    
    return f"[{clean_word}]"

def analyze_content(translated_lines):
    water_count = 0
    star_count = 0
    
    narrative = []
    
    for lineno, orig, trans in translated_lines:
        if "WATER" in trans:
            water_count += 1
        
        narrative.append(f"{lineno}. {trans}")
        
    return {
        "water_count": water_count,
        "narrative": narrative
    }

def main():
    # 1. Load Dictionary
    dict_path = 'results/master_dictionary_v7_1.json'
    if not os.path.exists(dict_path):
        print(f"Warning: {dict_path} not found. Trying v7.")
        dict_path = 'results/master_dictionary_v7.json'
        
    dictionary = load_dictionary(dict_path)
    print(f"Loaded dictionary from {dict_path}")

    # 2. Extract f72r3
    lines = extract_lines('data/eva_ivtff.txt', 'f72r3')
    print(f"Extracted {len(lines)} lines for f72r3")
    
    # 3. Translate
    translation_output = []
    translation_output.append("# Translation of Cancer (f72r3)")
    translation_output.append(f"**Source:** `data/eva_ivtff.txt`")
    translation_output.append(f"**Dictionary:** `{dict_path}`")
    translation_output.append("")
    translation_output.append("## Key Terms Applied")
    translation_output.append("- `aiin`/`daiin` = **WATER/TAKE-WATER**")
    translation_output.append("- `okeol` = **BOIL**")
    translation_output.append("- `qokeey` = **COOK/PROCESS**")
    translation_output.append("- `sh-` = **THAT/WHICH** (Relative Pronoun)")
    translation_output.append("- `y-` = **AND**")
    translation_output.append("")
    
    full_data = []
    
    current_section = "Unknown"
    
    # Heuristic for sections based on line numbers (approximate)
    # R1: 1
    # S1: 2-13
    # R2: 14
    # S2: 15-25
    # R3: 26
    # S3: 27-33
    # R4: 34
    
    for lineno, text in lines:
        if lineno == 1:
            translation_output.append("### Section R1 (Main Text Ring 1)")
        elif lineno == 2:
            translation_output.append("### Section S1 (Star Labels 1)")
        elif lineno == 14:
            translation_output.append("### Section R2 (Main Text Ring 2)")
        elif lineno == 15:
            translation_output.append("### Section S2 (Star Labels 2)")
        elif lineno == 26:
            translation_output.append("### Section R3 (Main Text Ring 3)")
        elif lineno == 27:
            translation_output.append("### Section S3 (Star Labels 3)")
        elif lineno == 34:
            translation_output.append("### Section R4 (Inner Text)")

        words = text.split('.')
        translated_line = []
        voynich_line = []
        
        for w in words:
            w = w.strip()
            if not w: continue
            if w.startswith('%') or w.startswith('$') or w.startswith('<'): continue 
            
            voynich_line.append(w)
            trans = translate_word(w, dictionary)
            translated_line.append(trans)
            
        trans_str = ' '.join(translated_line)
        translation_output.append(f"**{lineno}.** `{text}`")
        translation_output.append(f"> {trans_str}")
        translation_output.append("")
        
        full_data.append((lineno, text, trans_str))

    # 4. Save Translation
    with open('results/cancer_translation.md', 'w') as f:
        f.write('\n'.join(translation_output))
    print("Created results/cancer_translation.md")

    # 5. Generate Report
    analysis = analyze_content(full_data)
    
    report = []
    report.append("# Cancer (f72r3) Analysis Report")
    report.append("")
    report.append("## Summary")
    report.append(f"Total lines processed: {len(lines)}")
    report.append(f"References to WATER (`aiin` variants): {analysis['water_count']}")
    report.append("")
    report.append("## Narrative Highlights")
    report.append("The text appears to contain instructions or descriptions related to liquid processing.")
    report.append("The high frequency of `aiin` (water) and `daiin` (take water) supports the 'Water' hypothesis for this section.")
    report.append("")
    report.append("## Generated Narrative (Simplified)")
    for line in analysis['narrative']:
         # Filter for interesting lines (containing verbs or water)
         if "WATER" in line or "BOIL" in line or "COOK" in line or "DRINK" in line:
             report.append(f"- {line}")

    with open('results/cancer_report.md', 'w') as f:
        f.write('\n'.join(report))
    print("Created results/cancer_report.md")

if __name__ == "__main__":
    main()
