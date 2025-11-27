import json
import os
import re

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_zodiac_pages_text(translation_file):
    data = load_json(translation_file)
    pages = {}
    # Regex to match f70, f71, f72, f73 followed by r/v and numbers
    pattern = re.compile(r'f(70|71|72|73)[rv]\d*')
    
    for page_id, page_data in data['pages'].items():
        if pattern.match(page_id):
            words = []
            for line in page_data.get('lines', []):
                # Extract words from 'original' text (EVA)
                # The original text format in full_manuscript_translation.json is like "fachys.ykal..."
                # We split by '.' and other separators
                raw_text = line.get('original', '')
                # Clean text: remove non-EVA characters if any, split by dots
                # EVA usually has lower case letters. '!' and other chars might be present as markers.
                # We will normalize.
                clean_text = re.sub(r'[^a-z0-9.]', '', raw_text) 
                line_words = [w for w in clean_text.split('.') if w]
                words.extend(line_words)
            pages[page_id] = words
    return pages

def extract_plant_terms(pages, dictionary_file):
    dictionary = load_json(dictionary_file)
    # Check structure of dictionary
    # The dictionary file provided in context has "entries" key.
    entries = dictionary.get('entries', {})
    
    page_plants = {}
    
    for page_id, words in pages.items():
        found_plants = []
        for word in words:
            if word in entries:
                entry = entries[word]
                # Check if it's a plant term
                domain = entry.get('domain', '')
                meaning = entry.get('meaning', '')
                
                if domain == 'botanical' or 'plant' in meaning or 'herb' in meaning:
                    found_plants.append({
                        'word': word,
                        'meaning': meaning,
                        'confidence': entry.get('confidence', 0)
                    })
        
        if found_plants:
            page_plants[page_id] = found_plants
            
    return page_plants

def main():
    translation_path = 'results/full_manuscript_translation.json'
    dictionary_path = 'results/dictionary/dictionary.json'
    
    if not os.path.exists(translation_path):
        print(f"Error: {translation_path} not found.")
        return

    print("Loading pages...")
    pages = get_zodiac_pages_text(translation_path)
    print(f"Found {len(pages)} Zodiac pages.")
    print("Pages found:", sorted(pages.keys()))

    print("Extracting plant terms...")
    page_plants = extract_plant_terms(pages, dictionary_path)
    
    # Print summary
    for page, plants in page_plants.items():
        print(f"Page {page}: {len(plants)} potential plant terms found.")
        unique_plants = set(p['meaning'] for p in plants)
        print(f"  Unique meanings: {unique_plants}")
        
    # Save intermediate result
    with open('temp_zodiac_plants_extraction.json', 'w') as f:
        json.dump(page_plants, f, indent=2)

if __name__ == "__main__":
    main()
