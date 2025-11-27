import json
import os
import re

def load_dictionary(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def parse_astro_sentences(filepath):
    sentences = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    current_page = "Unknown"
    for line in lines:
        line = line.strip()
        if line.startswith("# Page"):
            current_page = line.replace("# Page", "").strip()
        elif line.startswith("- Original:"):
            text = line.replace("- Original:", "").strip()
            sentences.append({
                'page': current_page,
                'text': text
            })
    return sentences

def translate_sentence(sentence_text, dictionary):
    # Split by dot or space
    tokens = re.split(r'[\.\s]+', sentence_text)
    translated_tokens = []
    plant_vocab_found = []
    verbs_found = []
    
    entries = dictionary.get('entries', {})
    
    for token in tokens:
        if not token: continue
        
        entry = entries.get(token)
        
        meaning = token # Default to original if no translation
        if entry:
            meaning = entry.get('meaning', token)
            
            # Check for plant vocabulary
            if entry.get('domain') == 'botanical' or 'plant' in str(meaning).lower():
                plant_vocab_found.append(f"{token} ({meaning})")
            if token in ['chol', 'shor']: # Explicit check
                 plant_vocab_found.append(f"{token} (Explicit: {meaning})")
                 
            # Check for verbs
            if 'verb' in str(entry.get('pos', '')).lower() or 'verb' in str(meaning).lower():
                 verbs_found.append(f"{token} ({meaning})")
        
        translated_tokens.append(meaning)
        
    return {
        'original_tokens': tokens,
        'translated_tokens': translated_tokens,
        'plant_vocab': plant_vocab_found,
        'verbs': verbs_found
    }

def main():
    # Paths
    dict_path = 'results/dictionary/dictionary.json'
    astro_path = 'results/translation_astro.md'
    output_detail = 'results/astro_sentences.md'
    output_summary = 'results/track-190-results_summary.md'
    
    # Load data
    print("Loading dictionary...")
    dictionary = load_dictionary(dict_path)
    
    print("Parsing Astro sentences...")
    sentences = parse_astro_sentences(astro_path)
    print(f"Found {len(sentences)} sentences.")
    
    # Filter for 'os' or 'oteos'
    target_words = ['os', 'oteos']
    matches = []
    
    for s in sentences:
        tokens = re.split(r'[\.\s]+', s['text'])
        if any(w in tokens for w in target_words):
            matches.append(s)
            
    print(f"Found {len(matches)} sentences containing {target_words}.")
    
    # Translate and Analyze
    results = []
    for m in matches:
        analysis = translate_sentence(m['text'], dictionary)
        results.append({
            'page': m['page'],
            'original': m['text'],
            'analysis': analysis
        })
        
    # Generate Output
    with open(output_detail, 'w') as f:
        f.write("# Astro Sentences Analysis (Track 190)\n\n")
        for r in results:
            f.write(f"## Page {r['page']}\n\n")
            f.write(f"**Original:** `{r['original']}`\n\n")
            f.write(f"**Translation:** {' '.join(r['analysis']['translated_tokens'])}\n\n")
            
            if r['analysis']['plant_vocab']:
                f.write(f"- **Plant Vocab:** {', '.join(r['analysis']['plant_vocab'])}\n")
            else:
                f.write("- **Plant Vocab:** None\n")
                
            if r['analysis']['verbs']:
                f.write(f"- **Verbs:** {', '.join(r['analysis']['verbs'])}\n")
            else:
                f.write("- **Verbs:** None\n")
            f.write("\n---\n\n")
            
    with open(output_summary, 'w') as f:
        f.write("# Track 190: Astro-Botany Connection Summary\n\n")
        f.write(f"Found {len(matches)} sentences containing 'os' (Star) or 'oteos' in the Astro section.\n\n")
        
        plant_links = [r for r in results if r['analysis']['plant_vocab']]
        f.write(f"## Plant Connections\n")
        f.write(f"- {len(plant_links)} sentences contain plant vocabulary.\n")
        for r in plant_links:
            f.write(f"- Page {r['page']}: Contains {', '.join(r['analysis']['plant_vocab'])}\n")
            
        f.write("\n## Verb Analysis\n")
        for r in results:
            if r['analysis']['verbs']:
                 f.write(f"- Page {r['page']}: {', '.join(r['analysis']['verbs'])}\n")

    print("Done.")

if __name__ == "__main__":
    main()
