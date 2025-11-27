import json
import re
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_dictionary(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def update_dictionary(dictionary, updates):
    for word, info in updates.items():
        if word not in dictionary['entries']:
            dictionary['entries'][word] = {'voynich': word}
        
        entry = dictionary['entries'][word]
        entry['meaning'] = info['meaning']
        entry['confidence'] = info['confidence']
        # Add other fields if necessary, preserving existing ones
        if 'source' not in entry:
            entry['source'] = 'manual_update_v15'
    
    # Propagation
    # If shkair is Chicory, then shkair-y is "Use Chicory"
    if 'shkair' in dictionary['entries']:
        shkairy = 'shkairy' # In eva transcription it might be different, e.g. shkair.y? No, usually y is a suffix.
        # Let's look for shkairy or similar forms in the dictionary or just add it if not present.
        # The task says "shkair-y". In EVA 'y' is a character. 'shkairy' is a valid word.
        # But wait, Voynich words are often separated by dots. 'shkair.y' is two words. 
        # However, 'y' is often a suffix attached to the word. 
        # Let's assume 'shkairy' (one word) for now, or maybe the task means the token 'shkairy'.
        
        # Let's check if 'shkairy' exists in the dictionary
        target_word = 'shkairy'
        if target_word not in dictionary['entries']:
             dictionary['entries'][target_word] = {'voynich': target_word}
        
        dictionary['entries'][target_word]['meaning'] = "Use Chicory"
        dictionary['entries'][target_word]['confidence'] = 0.7
        dictionary['entries'][target_word]['source'] = 'derived_v15'

    return dictionary

def extract_f33v_text(eva_path):
    lines = []
    with open(eva_path, 'r') as f:
        for line in f:
            if line.startswith('<f33v') and ';H>' in line:
                # Extract text content
                # Format: <f33v.1,@P0;H>	tar.ar.daiin<-><!plant>ydain.cthey.dol!r<-><!plant>sheky.ar.aiin.cs
                parts = line.strip().split('\t')
                if len(parts) > 1:
                    text_part = parts[1]
                    # Clean up comments like <-><!plant>
                    text_part = re.sub(r'<[^>]+>', ' ', text_part)
                    # Replace ! with . (or remove it? ! usually means unsure space or break)
                    # In EVA, . is word separator. ! might be a variant or uncertain separator.
                    # Let's treat ! as . for splitting words
                    text_part = text_part.replace('!', '.')
                    text_part = text_part.replace(',', '.') # sometimes , is used
                    lines.append(text_part)
    return lines

def translate_text(lines, dictionary):
    translation = []
    
    for line in lines:
        words = line.split('.')
        line_trans = []
        for word in words:
            word = word.strip()
            if not word:
                continue
            
            entry = dictionary['entries'].get(word)
            if entry and 'meaning' in entry:
                line_trans.append(f"{word}({entry['meaning']})")
            else:
                line_trans.append(word)
        
        translation.append(" ".join(line_trans))
    return translation

def main():
    base_dict_path = 'results/dictionary/dictionary.json'
    output_dict_path = 'results/dictionary/dictionary_v15_draft.json'
    eva_path = 'data/eva_ivtff.txt'
    translation_output_path = 'results/f33v_translation_v15.md'

    print(f"Loading dictionary from {base_dict_path}...")
    dictionary = load_dictionary(base_dict_path)

    updates = {
       "shkair": {"meaning": "Chicory (Cichorium)", "confidence": 0.7},
       "keero": {"meaning": "Coriander", "confidence": 0.7},
       "keer": {"meaning": "Coriander", "confidence": 0.7},
       "cphor": {"meaning": "Hellebore", "confidence": 0.6},
       "som": {"meaning": "Seed (Semen)", "confidence": 0.6},
       "seal": {"meaning": "Salt (Sale)", "confidence": 0.6},
       "sal": {"meaning": "Salt (Sale)", "confidence": 0.6},
       "air": {"meaning": "Suffix: -orium/noun?", "confidence": 0.5}
    }

    print("Updating dictionary...")
    dictionary = update_dictionary(dictionary, updates)
    dictionary['version'] = '15.0_draft'

    print(f"Saving dictionary to {output_dict_path}...")
    save_dictionary(dictionary, output_dict_path)

    print("Extracting f33v text...")
    lines = extract_f33v_text(eva_path)
    
    print("Translating f33v...")
    translated_lines = translate_text(lines, dictionary)

    print(f"Saving translation to {translation_output_path}...")
    with open(translation_output_path, 'w') as f:
        f.write("# Translation of f33v using Dictionary v15\n\n")
        for i, (original, trans) in enumerate(zip(lines, translated_lines)):
            f.write(f"## Line {i+1}\n")
            f.write(f"**Original:** {original}\n\n")
            f.write(f"**Translation:** {trans}\n\n")

if __name__ == "__main__":
    main()
