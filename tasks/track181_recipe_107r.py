import re
import json
import os

# Files
INPUT_IVTFF = 'data/eva_ivtff.txt'
INPUT_DICT = 'results/root_dictionary_v3.json'
INPUT_MATCHES = 'results/recipe_plant_matches.json'

OUTPUT_TRANS = 'results/translation_f107r.md'
OUTPUT_SUMMARY = 'results/track-181-results_summary.md'

# Target Words
TARGET_INGREDIENTS = {'ordaiin', 'oaiin', 'olchdy', 'otaiin', 'ordal'} # Added variations based on observation
TARGET_ACTIONS = {'qok-ed-y', 'qokedy', 'qokeey', 'qokchy', 'qok'} # Added variations

def load_dictionary():
    with open(INPUT_DICT, 'r') as f:
        data = json.load(f)
    return data.get('roots', {})

def load_matches():
    if not os.path.exists(INPUT_MATCHES):
        return []
    with open(INPUT_MATCHES, 'r') as f:
        return json.load(f)

def extract_text(page_id):
    lines = []
    capturing = False
    
    with open(INPUT_IVTFF, 'r') as f:
        for line in f:
            if line.startswith(f'<{page_id}'):
                parts = line.split('>', 1)
                if len(parts) > 1:
                    content = parts[1].strip()
                    content = re.sub(r'\{.*?\}', '', content)
                    if content:
                        lines.append(content)
    return lines

def translate_word(word, root_dict):
    clean_word = word.strip('.,-!?:;')
    
    # Exact match check
    if clean_word in TARGET_INGREDIENTS:
        return f"**[INGREDIENT: {clean_word}]**"
    
    if clean_word in TARGET_ACTIONS or clean_word.replace('-', '') in TARGET_ACTIONS:
        return f"**[ACTION: MIX/PROCESS ({clean_word})]**"
    
    # Partial match for targets (e.g. ordaiin appearing as ordaiin.r)
    for target in TARGET_INGREDIENTS:
        if target in clean_word:
             return f"**[INGREDIENT: {clean_word} (matches {target})]**"

    for target in TARGET_ACTIONS:
        if target in clean_word:
             return f"**[ACTION: MIX/PROCESS ({clean_word})]**"

    found_meaning = None
    for root, info in root_dict.items():
        if clean_word in info.get('source_words', []):
            if info.get('meanings'):
                found_meaning = f"[{info['meanings'][0]}]"
                break
    
    if found_meaning:
        return found_meaning
        
    return clean_word

def main():
    print("Starting Task 181...")
    
    # 1. Isolate Text
    raw_lines = extract_text('f107r')
    
    # Process words properly (split by . and space)
    all_words = []
    for line in raw_lines:
        # Replace . with space to split easily, but keep structure in line processing
        words = line.replace('.', ' ').split()
        all_words.extend(words)
        
    print(f"Extracted {len(all_words)} words from f107r.")
    
    # 2. Load Data
    root_dict = load_dictionary()
    
    # 3. Translate & Tag
    translated_lines = []
    
    for line in raw_lines:
        # We want to preserve the visual structure but translate the tokens
        # Tokens are separated by . or spaces
        # We'll split by . to respect the EVA format, assuming . is the separator
        tokens = line.split('.')
        trans_tokens = []
        for t in tokens:
            if not t.strip(): continue
            # Also handle spaces inside tokens if any (though usually . is the separator)
            sub_tokens = t.split()
            sub_trans = []
            for st in sub_tokens:
                sub_trans.append(translate_word(st, root_dict))
            trans_tokens.append(" ".join(sub_trans))
        
        translated_lines.append(".".join(trans_tokens))
        
    # 4. Output Translation
    with open(OUTPUT_TRANS, 'w') as f:
        f.write("# Translation of f107r\n\n")
        f.write("## Original vs Translation\n\n")
        for i, (raw, trans) in enumerate(zip(raw_lines, translated_lines)):
            f.write(f"**Line {i+1}:**\n")
            f.write(f"> {raw}\n\n")
            f.write(f"{trans}\n\n")
            
    # 5. Context Check & Summary
    word_count = len(all_words)
    theriac_avg = 150 
    
    match_note = "Length matches typical complex medical recipes." if 100 < word_count < 600 else "Length is atypical."
    
    # Count targets
    ing_count = 0
    act_count = 0
    for w in all_words:
        clean = w.strip('.,')
        is_ing = clean in TARGET_INGREDIENTS
        is_act = clean in TARGET_ACTIONS or clean.replace('-', '') in TARGET_ACTIONS
        
        if not is_ing:
            for t in TARGET_INGREDIENTS:
                if t in clean: is_ing = True; break
        
        if not is_act:
             for t in TARGET_ACTIONS:
                if t in clean: is_act = True; break
        
        if is_ing: ing_count += 1
        if is_act: act_count += 1

    summary = f"""# Task 181 Results Summary

## Overview
Successfully isolated and translated Page f107r.

## Statistics
- **Total Words:** {word_count}
- **Target Ingredients Found:** {ing_count}
- **Target Actions Found:** {act_count}

## Context Check
- **Word Count:** {word_count}
- **Assessment:** {match_note}

## Key Findings
- **Ingredients:** Looked for `ordaiin`, `oaiin`, `olchdy` (and variations). Found {ing_count}.
- **Actions:** Looked for `qok-ed-y` (and variations). Found {act_count}.
- See `results/translation_f107r.md` for full line-by-line analysis.
"""

    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write(summary)
        
    print("Task 181 Complete.")

if __name__ == "__main__":
    main()
