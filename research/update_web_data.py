import json
import re
import os

def update_dictionary():
    src_path = 'results/dictionary/master_dictionary_v19.json'
    dest_path = 'web/src/data/dictionary.json'
    
    print(f"Reading dictionary from {src_path}...")
    with open(src_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # We might want to filter or just pass it through. 
    # The task says "Minified for web". 
    # Let's keep the structure but minify the JSON.
    
    print(f"Writing minified dictionary to {dest_path}...")
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))
    
    print("Dictionary updated.")

def update_translations():
    src_path = 'translated/THE_VOYNICH_MEDICAL_MANUAL_CLEAN.md'
    dest_path = 'web/src/data/translations.json'
    
    print(f"Reading translations from {src_path}...")
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    translations = {}
    
    # Regex to match page headers like "## Page f10r (Recipes)"
    # We assume the content for a page continues until the next "## Page" or end of file.
    pattern = re.compile(r'^## Page ([a-z0-9]+).*$', re.MULTILINE)
    
    matches = list(pattern.finditer(content))
    
    for i, match in enumerate(matches):
        folio = match.group(1)
        start_pos = match.end()
        
        if i + 1 < len(matches):
            end_pos = matches[i+1].start()
        else:
            end_pos = len(content)
            
        page_content = content[start_pos:end_pos].strip()
        translations[folio] = page_content
        
    print(f"Found {len(translations)} pages.")
    
    print(f"Writing translations to {dest_path}...")
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, indent=2)
        
    print("Translations updated.")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('web/src/data', exist_ok=True)
    
    update_dictionary()
    update_translations()
