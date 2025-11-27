import json
import re
import os
import random

def main():
    print("Starting Syntax Translation...")
    
    tagged_path = 'results/tagged_text.txt'
    dict_path = 'results/root_dictionary_v1.json'
    
    if not os.path.exists(tagged_path) or not os.path.exists(dict_path):
        print("Files missing.")
        return
        
    with open(dict_path, 'r') as f:
        root_dict = json.load(f)
        
    # Build a Root -> Meaning map (flattened)
    # We need to strip prefixes from the tagged word to find the root lookup key
    # Or rely on the fact that root_dict keys are ROOTS.
    # We need a way to strip the prefix again to lookup.
    # Re-using the morphology rules or a simple heuristic.
    
    # Simplification: In Task 153/156 we generated 'parsed_text.json'. 
    # We can use that to map 'word' -> 'root' -> 'meaning'.
    # But here we are working with 'tagged_text.txt' which has segmented words.
    # Let's assume the segment AFTER the prefix is the root (mostly).
    
    # Map: Tag -> English Grammar
    TAG_MAP = {
        'VERB': '[VERB]',
        'IMP': 'Take/Do',
        'CONJ': 'and',
        'NOUN': 'the',
        'PREP': 'to',
        'REL': 'that',
        'ROOT': '' 
    }
    
    # Helper to get meaning
    def get_meaning(word_part):
        # Try exact match
        if word_part in root_dict and 'roots' in root_dict: # Check dict structure
             # Note: Task 155 output format is {"root": entry...} directly or inside a wrapper?
             # The previous read showed {"roots": {...}}
             entry = root_dict['roots'].get(word_part)
             if entry and entry['meanings']:
                 return entry['meanings'][0]
        
        # Flattened check (if dict structure varies)
        if word_part in root_dict:
             entry = root_dict[word_part]
             if isinstance(entry, dict) and 'meanings' in entry and entry['meanings']:
                 return entry['meanings'][0]
                 
        return f"[{word_part}]" # Unknown

    # Translation Logic
    translation_output = []
    
    with open(tagged_path, 'r') as f:
        lines = f.read().splitlines()
        
    # Pick Sample Pages (or just dump all?)
    # Let's do full but only save a sample to report for analysis
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            translation_output.append(line)
            continue
            
        tokens = line.split()
        translated_line = []
        
        for token in tokens:
            if ':' not in token:
                translated_line.append(token)
                continue
                
            tag, word = token.split(':', 1)
            
            # 1. Translate Grammar (Tag)
            grammar_word = TAG_MAP.get(tag, "")
            
            # 2. Translate Root
            # We need to strip the prefix to find the root
            # Heuristic: matches tag logic
            root_candidate = word
            if tag == 'VERB' and word.startswith('qo'): root_candidate = word[2:]
            elif tag == 'VERB' and word.startswith('qok'): root_candidate = word[3:]
            elif tag == 'IMP' and word.startswith('d'): root_candidate = word[1:]
            elif tag == 'IMP' and word.startswith('dai'): root_candidate = word[3:]
            elif tag == 'CONJ' and word.startswith('y'): root_candidate = word[1:]
            elif tag == 'NOUN' and word.startswith('o'): root_candidate = word[1:]
            
            meaning = get_meaning(root_candidate)
            
            # Combine
            if grammar_word:
                translated_line.append(f"{grammar_word} {meaning}")
            else:
                translated_line.append(meaning)
                
        translation_output.append(" ".join(translated_line))
        
    # Save Sample
    with open('results/syntax_translation_sample.md', 'w') as f:
        f.write("# Syntax Translation Sample\n\n")
        # Write random 50 lines
        sample_lines = [l for l in translation_output if not l.startswith('#') and len(l) > 20]
        if len(sample_lines) > 50:
            sample_lines = random.sample(sample_lines, 50)
            
        f.write("\n\n".join(sample_lines))
        
    print("Translation sample generated.")

if __name__ == "__main__":
    main()
