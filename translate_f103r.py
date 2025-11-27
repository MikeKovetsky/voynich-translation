import json
import re
import os

def load_dictionary(path):
    if not os.path.exists(path):
        print(f"Error: Dictionary not found at {path}")
        return {"entries": {}, "version": "0.0"}
    with open(path, 'r') as f:
        return json.load(f)

def save_dictionary(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def extract_f103r_lines(file_path):
    raw_lines = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            if "<f103r." in line:
                # parse id like <f103r.1,@P0;H>
                match = re.search(r'<f103r\.(\d+)[^>]*;([A-Za-z])>', line)
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
        if 'H' in versions:
            text = versions['H']
        elif 'U' in versions:
            text = versions['U']
        elif 'F' in versions:
            text = versions['F']
        else:
            # fallback
            text = next(iter(versions.values()))
            
        final_lines.append(text)
        
    return final_lines

def translate_word(word, dictionary):
    # Clean word
    clean_word = word.replace('!', '').replace('?', '').replace(',', '')
    
    if not clean_word:
        return ""

    # Direct lookup
    if clean_word in dictionary['entries']:
        return dictionary['entries'][clean_word]['meaning']
    
    # 'y-' prefix logic
    # Rule: if starts with 'y' AND (rest is in dict OR rest looks like a valid word)
    if clean_word.startswith('y') and len(clean_word) > 1:
        root = clean_word[1:]
        if root in dictionary['entries']:
            return f"AND {dictionary['entries'][root]['meaning']}"
        else:
             return f"AND [{root}]"

    return f"[{clean_word}]"

def main():
    # 1. Load Dictionary v7
    dict_path = 'results/master_dictionary_v7.json'
    data = load_dictionary(dict_path)
    
    # 2. Update to v7.1
    if 'y' not in data['entries']:
        data['entries']['y'] = {
            "voynich": "y",
            "meaning": "AND",
            "language": "grammar",
            "confidence": 0.9,
            "domain": "grammar",
            "source": "Track117_Analysis"
        }
    
    data['version'] = "7.1"
    save_dictionary(data, 'results/master_dictionary_v7_1.json')
    print("Created results/master_dictionary_v7_1.json")
    
    # 3. Extract f103r
    lines = extract_f103r_lines('data/eva_ivtff.txt')
    print(f"Extracted {len(lines)} lines for f103r")
    
    # 4. Translate
    translation_output = []
    translation_output.append("# Translation of f103r (Recipes)")
    translation_output.append("Using Master Dictionary v7.1 (with y- = AND)")
    translation_output.append("")
    
    for i, line in enumerate(lines):
        # Split by dot, but sometimes EVA has multiple dots or other separators?
        # Standard EVA uses dot as space.
        words = line.split('.')
        translated_line = []
        voynich_line = []
        
        for w in words:
            w = w.strip()
            if not w: continue
            if w.startswith('%') or w.startswith('$') or w.startswith('<'): continue 
            
            voynich_line.append(w)
            trans = translate_word(w, data)
            translated_line.append(trans)
            
        translation_output.append(f"## Line {i+1}")
        translation_output.append(f"**Source:** `{' '.join(voynich_line)}`")
        translation_output.append(f"**Trans:** `{' '.join(translated_line)}`")
        translation_output.append("")

    # 5. Save Output
    with open('results/f103r_translation.md', 'w') as f:
        f.write('\n'.join(translation_output))
    
    print("Created results/f103r_translation.md")

if __name__ == "__main__":
    main()
