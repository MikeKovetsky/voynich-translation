import json
import re
import os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def parse_transcription(path, page_ids):
    pages = {pid: [] for pid in page_ids}
    current_page = None
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Check for page start
            # Format: <f65r> ...
            page_match = re.match(r'^<([a-z0-9]+)>', line)
            if page_match:
                current_page = page_match.group(1)
                continue
            
            if current_page in page_ids:
                if line.startswith(f"<{current_page}"):
                    parts = line.split(maxsplit=1)
                    if len(parts) > 1:
                        content = parts[1]
                        if content.startswith("<!") or content.startswith("#"):
                            continue
                        words = content.split('.')
                        clean_words = [w.strip() for w in words if w.strip()]
                        pages[current_page].extend(clean_words)
    return pages

def apply_grammar(word, grammar):
    analysis = []
    base_word = word
    
    prefixes = grammar.get("morphology_rules", {}).get("prefixes", {})
    for pre, meaning in prefixes.items():
        if base_word.startswith(pre.replace("-", "")):
            analysis.append(f"[Pre: {meaning}]")
            base_word = base_word[len(pre.replace("-", "")):]
            break 
            
    suffixes = grammar.get("morphology_rules", {}).get("suffixes", {})
    for suf, meaning in suffixes.items():
        s_clean = suf.replace("-", "")
        if base_word.endswith(s_clean):
            analysis.append(f"[Suf: {meaning}]")
            base_word = base_word[:-len(s_clean)]
            break 
            
    return base_word, analysis

def translate_page(words, dictionary, grammar):
    translation = []
    
    # Access the entries dictionary if it exists
    dict_entries = dictionary.get("entries", dictionary)
    
    for word in words:
        base_word, grammar_notes = apply_grammar(word, grammar)
        
        definition = dict_entries.get(word) or dict_entries.get(base_word)
        
        english = "???"
        if definition:
            if isinstance(definition, dict):
                english = definition.get("meaning", definition.get("english", definition.get("definition", "???")))
            else:
                english = definition
        
        item = {
            "voynich": word,
            "base": base_word,
            "english": english,
            "grammar": grammar_notes
        }
        translation.append(item)
        
    return translation

def main():
    transcription_path = "data/eva_ivtff.txt"
    dict_path = "results/dictionary/master_dictionary_v16.json"
    grammar_path = "config/recipe_grammar.json"
    
    print(f"Loading dictionary from {dict_path}...")
    dictionary = load_json(dict_path)
    
    print(f"Loading grammar from {grammar_path}...")
    grammar = load_json(grammar_path)
    
    target_pages = ["f65r", "f41r"]
    print(f"Parsing pages {target_pages} from {transcription_path}...")
    pages_data = parse_transcription(transcription_path, target_pages)
    
    for pid in target_pages:
        print(f"\n=== Processing {pid} ===")
        words = pages_data.get(pid, [])
        if not words:
            print(f"No words found for {pid}")
            continue
            
        translated_items = translate_page(words, dictionary, grammar)
        
        print(f"\n--- Rough Translation for {pid} ---")
        
        for item in translated_items:
            eng = item['english']
            if isinstance(eng, list):
                eng = eng[0]
            
            note = ""
            if item['grammar']:
                note = f" ({', '.join(item['grammar'])})"
            
            print(f"{item['voynich']:<15} -> {eng:<20} {note}")

if __name__ == "__main__":
    main()
