import csv
import re
from collections import Counter, defaultdict
import os

def load_sherwood_mapping(filepath):
    mapping = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping.append(row)
    return mapping

def parse_ivtff(filepath):
    folio_words = defaultdict(set)
    
    # Regex to capture folio: <f(identifier)...>
    # e.g. <f86v6.14,+P0;F> -> identifier = 86v6
    # e.g. <f2r.1;H> -> identifier = 2r
    folio_pattern = re.compile(r'^<f([^.]+)\.')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = folio_pattern.match(line)
            if not match:
                continue
                
            folio_id = match.group(1)
            
            # Extract text content (everything after the tag)
            # Tag ends with >
            try:
                tag_end = line.index('>')
                content = line[tag_end+1:].strip()
            except ValueError:
                continue
            
            # Split by dots and spaces
            # IVTFF uses dots as separators, sometimes spaces
            tokens = re.split(r'[.\s]+', content)
            
            for token in tokens:
                # Clean token
                # Remove uncertain chars like ?, !, *, %, (, ), etc.
                # Keep only a-z and maybe standard EVA chars if needed, but for anagrams usually we want letters.
                # EVA is lowercase.
                clean_token = re.sub(r'[^a-z]', '', token)
                if clean_token:
                    folio_words[folio_id].add(clean_token)
                    
    return folio_words

def is_anagram(word1, word2):
    return sorted(word1) == sorted(word2)

def is_subset(subset, superset):
    # Can subset be formed using letters from superset?
    c_sub = Counter(subset)
    c_super = Counter(superset)
    for char, count in c_sub.items():
        if c_super[char] < count:
            return False
    return True

def run_anagram_validation():
    mapping_file = 'data/external_corpora/sherwood_plant_mapping.csv'
    ivtff_file = 'data/eva_ivtff.txt'
    output_file = 'results/anagram_candidates.csv'
    
    print("Loading mapping...")
    plant_mapping = load_sherwood_mapping(mapping_file)
    
    print("Parsing IVTFF...")
    folio_text = parse_ivtff(ivtff_file)
    
    results = []
    
    print("Running validation...")
    for entry in plant_mapping:
        folio = entry['Folio']
        latin_name = entry['Latin Name']
        
        # Normalize Latin Name
        # Remove spaces, lowercase
        latin_clean = re.sub(r'[^a-z]', '', latin_name.lower())
        if not latin_clean:
            continue
            
        # Get Voynich words for this folio
        # Handle potential mapping issues (e.g. 86v vs 86v6)
        # For now, try exact match.
        # If no exact match, try to see if folio starts with the csv folio (e.g. csv 86v matches 86v1, 86v2...)
        
        # But wait, the CSV usually has simple folios like 2r.
        # Let's gather all words that match the folio prefix if exact match missing?
        # Or just check exact first.
        
        candidates = set()
        if folio in folio_text:
            candidates.update(folio_text[folio])
        else:
            # Fallback: check for extended folios
            # e.g. if CSV has '86v', and IVTFF has '86v1', '86v2'
            # Actually, looking at IVTFF lines like <f86v6...>, the folio ID extracted is 86v6.
            # If CSV has 86v, we might want to include 86v6 words?
            # It's safer to exact match first. If CSV has '2r', IVTFF has '2r'.
            for f_key in folio_text:
                if f_key == folio or f_key.startswith(folio + '.') or (folio + '1' in f_key and folio.endswith('v')): 
                    # This logic is a bit fuzzy. Let's stick to:
                    # If exact match, use it.
                    # If CSV folio is prefix of IVTFF folio, use it?
                    if f_key.startswith(folio):
                        candidates.update(folio_text[f_key])

        if not candidates:
            # print(f"Warning: No text found for folio {folio}")
            continue
            
        for v_word in candidates:
            # Test 1: Full Anagram
            if is_anagram(latin_clean, v_word):
                results.append({
                    'Folio': folio,
                    'Latin Name': latin_name,
                    'Voynich Word': v_word,
                    'Test': 'Full Anagram',
                    'Details': f"{latin_clean} == {v_word}"
                })
            
            # Test 2: Subset Anagram (Voynich word is subset of Latin Name)
            # "Is there any Voynich word that can be formed using only the letters from the Latin name?"
            # This means v_word is made from latin_clean.
            # We should filter out very short words to avoid noise? The prompt doesn't say so, but "a" is always a subset.
            # Let's strictly follow prompt. "Is there any Voynich word..."
            # I will filter length > 2 maybe? Or just output all.
            # The prompt implies we want meaningful hits. But "using only the letters" is the criteria.
            if is_subset(v_word, latin_clean):
                 # To avoid explosion of results (e.g. "o", "a", "d" matching "Pisum"), let's verify.
                 # Actually, if I output all subsets, it might be huge.
                 # But the prompt asks to "Test" it.
                 # "Is there any Voynich word that is an exact anagram...?"
                 # "Is there any Voynich word that can be formed using only the letters..."
                 # I will assume reasonable length > 2 to be useful.
                 if len(v_word) >= 3:
                    results.append({
                        'Folio': folio,
                        'Latin Name': latin_name,
                        'Voynich Word': v_word,
                        'Test': 'Subset (Voynich from Latin)',
                        'Details': f"{v_word} in {latin_clean}"
                    })

            # Test 3: Super-set Anagram (Latin name from Voynich word)
            # "Can the Latin name be formed using the letters of a Voynich word?"
            # i.e. latin_clean is subset of v_word.
            if is_subset(latin_clean, v_word):
                results.append({
                    'Folio': folio,
                    'Latin Name': latin_name,
                    'Voynich Word': v_word,
                    'Test': 'Superset (Latin from Voynich)',
                    'Details': f"{latin_clean} in {v_word}"
                })

    # Write results
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Folio', 'Latin Name', 'Voynich Word', 'Test', 'Details']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Done. Found {len(results)} candidates.")

if __name__ == "__main__":
    run_anagram_validation()
