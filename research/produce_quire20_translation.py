import json
import re
import os

# Configuration
DICTIONARY_PATH = 'results/dictionary/dictionary_v15_draft.json'
TRANSCRIPTION_PATH = 'data/eva_ivtff.txt'
GRAMMAR_PATH = 'config/recipe_grammar.json'
OUTPUT_MD_PATH = 'results/final_translated_quire20.md'
OUTPUT_JSON_PATH = 'results/final_translated_quire20.json'

QUIRE_20_PAGES = [
    'f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v',
    'f106r', 'f106v', 'f107r', 'f107v', 'f108r', 'f108v',
    'f109r', 'f109v', 'f110r', 'f110v', 'f111r', 'f111v',
    'f112r', 'f112v', 'f113r', 'f113v', 'f114r', 'f114v',
    'f115r', 'f115v', 'f116r', 'f116v'
]

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}")
        return None

def load_transcription(path):
    pages = {}
    current_page = None
    found_file = False
    
    try:
        with open(path, 'r') as f:
            found_file = True
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Only use Takahashi (H) transcription
                if ';H>' not in line:
                    continue

                # Check for page header <f...>
                if line.startswith('<f'):
                    parts = line.split('>')
                    if len(parts) > 0:
                        tag = parts[0][1:] # remove <
                        # Extract page name
                        page_name_match = re.match(r'(f\d+[rv]\d?)', tag)
                        if page_name_match:
                            current_page = page_name_match.group(1)
                            if current_page in QUIRE_20_PAGES:
                                if current_page not in pages:
                                    pages[current_page] = []
                                    
                                if '>' in line:
                                    content = line.split('>')[-1].strip()
                                    if content:
                                        # Clean text
                                        content = re.sub(r'\{[^}]*\}', '', content)
                                        content = content.replace('.', ' ')
                                        content = re.sub(r'[!?,%*]', '', content)
                                        content = re.sub(r'<[^>]*>', '', content)
                                        
                                        words = content.split()
                                        if words:
                                            pages[current_page].append(words)
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        return {}
        
    if found_file and not pages:
        print(f"Warning: No pages found in {path} matching target list.")
        
    return pages

def apply_grammar(words, dictionary, grammar):
    translated_sentence = []
    
    token_roles = grammar.get('token_roles', {})
    morphology_rules = grammar.get('morphology_rules', {})
    
    for word in words:
        # 1. Direct Dictionary Lookup
        meaning = None
        if word in dictionary.get('entries', {}):
            entry = dictionary['entries'][word]
            meaning = entry.get('meaning')
            
        # 2. Morphology
        if not meaning:
            # Check Suffixes
            for suffix, role in morphology_rules.get('suffixes', {}).items():
                clean_suffix = suffix.replace('-', '')
                if word.endswith(clean_suffix):
                    base = word[:-len(clean_suffix)]
                    if base in dictionary.get('entries', {}):
                        base_meaning = dictionary['entries'][base].get('meaning')
                        meaning = f"{role} {base_meaning}"
                        break
            
            # Check Prefixes
            if not meaning:
                for prefix, role in morphology_rules.get('prefixes', {}).items():
                     clean_prefix = prefix.replace('-', '')
                     if word.startswith(clean_prefix):
                        base = word[len(clean_prefix):]
                        if base in dictionary.get('entries', {}):
                            base_meaning = dictionary['entries'][base].get('meaning')
                            meaning = f"{role} {base_meaning}"
                            break
        
        # 3. Fallback or Token Roles
        if not meaning:
             if word in token_roles:
                 meaning = token_roles[word]
             else:
                 meaning = word 
        
        translated_sentence.append(meaning)
        
    return translated_sentence

def smooth_translation(translated_words, grammar):
    final_words = []
    
    function_words = ['with', 'and', 'or', 'step', 'mix', 'cook', 'take', 'process', 'imperative', 'verb', 'noun', 'marker', 'then']
    
    replacements = {
        "plant_candidate": "Plant",
        "ingredient_candidate": "Ingredient",
        "unknown_object": "Object",
        "Verbalizer (Process/Action)": "Process",
        "Noun Marker (The Object)": "the",
        "Sentence Starter / Conjunction": "Then",
        "Suffix: -orium/noun?": "Place",
        "verb form": "Verb",
        "verb (unknown)": "Verb",
        "[COLOR_RED]": "Red",
        "[PLANT NAME]": "Plant",
        "morphological_derivative": "Derived", # Fallback
        "flower (perach)": "Flower",
        "star_candidate": "Star",
        "tree_candidate": "Tree"
    }

    for i, word in enumerate(translated_words):
        if not word: continue
        
        # Basic Cleaning
        for old, new in replacements.items():
            word = word.replace(old, new)
            
        # Specific regex cleanups
        # morphological_derivative (A + B) -> A-B
        word = re.sub(r'Derived \(([^)]+)\)', lambda m: m.group(1).replace(' + ', '').replace('-', ''), word)
        
        # Clean up parens if they just contain technical info
        word = re.sub(r'\(adjectival/suffix\)', '', word)
        word = re.sub(r'\(imperative/action\)', '', word)
        word = re.sub(r'\(plural/collective\)', '(s)', word)
        word = re.sub(r'\(derivative\)', '', word)
        
        word = word.strip()
        
        is_noun = True
        lower_word = word.lower()
        
        # Check if it is a known function word or phrase
        for fw in function_words:
            if fw in lower_word:
                is_noun = False
                break
        
        if lower_word in ['the', 'a', 'an', 'of', 'in', 'on', 'to', 'then', 'process', 'take']:
            is_noun = False
            
        if is_noun:
             # Check previous word
             prev_word = final_words[-1] if final_words else ""
             prev_lower = prev_word.lower()
             if not prev_lower.endswith(('the', 'a', 'an', 'of', 'with', 'process', 'take', 'mix', 'verb')):
                 if not word.lower().startswith('the '):
                     word = "the " + word
        
        final_words.append(word)

    sentence = " ".join(final_words)
    
    # Deduplicate "the the"
    sentence = re.sub(r'(?i)\bthe\s+the\b', 'the', sentence)
    
    if sentence:
        sentence = sentence[0].upper() + sentence[1:]
    
    return sentence

def format_cookbook(pages):
    md_output = "# Voynich Manuscript - Quire 20 Translation (Recipe Section)\n\n"
    json_output = {}
    
    for page_name in sorted(pages.keys()):
        md_output += f"## Page {page_name}\n\n"
        md_output += f"### Recipe Set {page_name}\n\n"
        
        json_output[page_name] = []
        
        lines = pages[page_name]
        for i, line in enumerate(lines):
             step_num = i + 1
             md_output += f"**Step {step_num}:** {line}\n\n"
             json_output[page_name].append({
                 "step": step_num,
                 "text": line
             })
             
    return md_output, json_output

def main():
    print("Loading data...")
    dictionary = load_json(DICTIONARY_PATH)
    if dictionary is None: return
    
    grammar = load_json(GRAMMAR_PATH)
    if grammar is None: return
    
    pages = load_transcription(TRANSCRIPTION_PATH)
    if not pages:
        print("No pages loaded.")
        return

    print(f"Loaded {len(pages)} pages from Quire 20.")
    
    translated_pages = {}
    
    print("Translating...")
    for page_name, text_lines in pages.items():
        translated_lines = []
        for words in text_lines:
            translated_words = apply_grammar(words, dictionary, grammar)
            smoothed_line = smooth_translation(translated_words, grammar)
            translated_lines.append(smoothed_line)
        translated_pages[page_name] = translated_lines
        
    print("Formatting...")
    md_content, json_content = format_cookbook(translated_pages)
    
    print("Saving results...")
    with open(OUTPUT_MD_PATH, 'w') as f:
        f.write(md_content)
        
    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(json_content, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    main()
