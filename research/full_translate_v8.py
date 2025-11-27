import json
import re
import os
import voynich_data

DICT_FILE = "results/master_dictionary_v8_0.json"
OUT_MD = "results/voynich_full_translation_v8.md"
OUT_JSON = "web/src/data/translations.json"
TRANSLATED_DIR = "translated"

GRAMMAR = {
    "y-": {"meaning": "AND", "type": "prefix"},
    "sh-": {"meaning": "THAT", "type": "prefix"},
    "qok-": {"meaning": "IN", "type": "prefix"},
}

MORPHOLOGY = {
    "-dy": "ed",
    "-y": "ing"
}

def load_dictionary():
    print(f"Loading dictionary from {DICT_FILE}...")
    try:
        with open(DICT_FILE, 'r') as f:
            data = json.load(f)
        
        if "entries" in data:
            return data["entries"]
        return data
    except FileNotFoundError:
        print(f"Error: Dictionary file {DICT_FILE} not found.")
        return {}

def apply_grammar(word):
    meaning_parts = []
    current_word = word
    prefix_found = False
    for prefix, info in GRAMMAR.items():
        p_clean = prefix.replace("-", "")
        if current_word.startswith(p_clean) and len(current_word) > len(p_clean):
            meaning_parts.append(info["meaning"])
            current_word = current_word[len(p_clean):]
            prefix_found = True
            break 
    return prefix_found, meaning_parts, current_word

def strip_morphology(word):
    stem = word
    suffix_meaning = ""
    for suffix, replacement in MORPHOLOGY.items():
        s_clean = suffix.replace("-", "")
        if stem.endswith(s_clean) and len(stem) > len(s_clean):
            stem = stem[:-len(s_clean)]
            suffix_meaning = replacement
            break
    return stem, suffix_meaning

def format_meaning(text):
    # Identify brackets [] and bold/italicize them
    # Using regex to find [ANYTHING]
    return re.sub(r'\[([^\]]+)\]', r'**[\1]**', text)

def translate_word(word, dictionary):
    if word in dictionary:
        return dictionary[word].get("meaning", "?")
        
    has_prefix, prefix_meanings, stem = apply_grammar(word)
    
    if has_prefix:
        if stem in dictionary:
            base = dictionary[stem].get("meaning", "?")
            return " ".join(prefix_meanings + [base])
            
    # Suffixes
    check_word = stem if has_prefix else word
    base, suffix = strip_morphology(check_word)
    
    if suffix:
        if base in dictionary:
            base_mean = dictionary[base].get("meaning", "?")
            full = f"{base_mean}-{suffix}"
            if has_prefix:
                full = " ".join(prefix_meanings + [full])
            return full
            
    return "?"

def translate_line(text, dictionary):
    # Clean text
    clean_text = re.sub(r'[!?,]', '.', text).strip()
    if not clean_text: return ""
    
    words = clean_text.split(".")
    translations = []
    
    for w in words:
        if not w: continue
        mean = translate_word(w, dictionary)
        # Format if it contains categories like [PLANT]
        mean = format_meaning(mean)
        translations.append(mean)
        
    return " ".join(translations)

def main():
    dictionary = load_dictionary()
    print(f"Dictionary loaded: {len(dictionary)} entries")
    
    print("Loading manuscript pages...")
    pages = voynich_data.get_eva_pages()
    
    # Sorting folios nicely (f1r, f1v, f2r...)
    def sort_key(f):
        nums = re.findall(r'\d+', f)
        if nums:
            return int(nums[0])
        return 999
        
    folios = sorted(pages.keys(), key=sort_key)
    
    full_md_content = "# Voynich Manuscript Final Translation (v8.0)\n\n"
    # Try to get date from dict, else today
    full_md_content += "Dictionary v8.0\n\n"
    
    web_translations = {}
    
    if not os.path.exists(TRANSLATED_DIR):
        os.makedirs(TRANSLATED_DIR)
        
    print("Translating...")
    for folio in folios:
        lines = pages[folio]
        folio_md = f"# Translated Page: {folio}\n\n"
        
        # Sort lines by location. Loc format: f1r.1, f1r.P.1, etc.
        # We want to sort by the last number if possible, or just string sort.
        # Default string sort usually works ok for f1r.1, f1r.10, so we need numeric sort for the last part.
        def line_sort_key(loc):
            parts = loc.split('.')
            if parts[-1].isdigit():
                return float(parts[-1])
            # Handle cases like f1r.P.1 -> P=0 maybe? or just 0.
            # If we have f1r.1 and f1r.10, string sort puts f1r.10 before f1r.2.
            # Let's try to find the last number in the string.
            nums = re.findall(r'\d+', loc)
            if nums:
                return int(nums[-1])
            return 0
            
        sorted_locs = sorted(lines.keys(), key=line_sort_key)
        
        for loc in sorted_locs:
            text = lines[loc]
            trans = translate_line(text, dictionary)
            
            # Markdown block
            block = f"**{loc}**: {trans}\n> `{text}`\n\n"
            folio_md += block
            
        # Add to full md (strip header to avoid dups)
        content_only = folio_md.replace(f"# Translated Page: {folio}\n\n", "")
        full_md_content += f"## Folio {folio}\n\n{content_only}"
        
        # Save individual file
        with open(f"{TRANSLATED_DIR}/{folio}.md", "w") as f:
            f.write(folio_md)
            
        # Add to web json
        web_translations[folio] = folio_md
        
    # Save full translation
    print(f"Saving {OUT_MD}...")
    with open(OUT_MD, "w") as f:
        f.write(full_md_content)
        
    # Update web/src/data/translations.json
    print(f"Updating {OUT_JSON}...")
    with open(OUT_JSON, "w") as f:
        json.dump(web_translations, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    main()
