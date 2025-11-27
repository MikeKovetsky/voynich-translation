import json
import re
import os

# Configuration
DICTIONARY_PATH = 'results/dictionary/dictionary.json'
CORPUS_PATH = 'data/eva_ivtff.txt'
OUTPUT_MD_PATH = 'results/recipe_retranslation_v3.md'
SUMMARY_PATH = 'results/track-227-results_summary.md'
TARGET_WORDS = {'qokeedy', 'qokedy', 'qokal', 'qol'}

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # Handle both "entries" key and direct dictionary
    if 'entries' in data:
        return data['entries']
    return data

def parse_line(line):
    # Format: <f111v.1,@P0;H>	koshey.qokal...
    match = re.match(r'<f(\d+[rv])\.([^;]+);([A-Za-z])>\s+(.+)', line)
    if not match:
        return None
    
    folio_full = match.group(1) # e.g. 111v
    folio_num = int(re.match(r'\d+', folio_full).group(0))
    source = match.group(3)
    content = match.group(4)
    
    # Filter for Quire 20 (f103 - f116) and Source H
    if not (103 <= folio_num <= 116):
        return None
    if source != 'H':
        return None
        
    # Clean content
    # Remove comments like {comment}
    content = re.sub(r'\{.*?\}', '', content)
    # Replace . with space
    content = content.replace('.', ' ')
    # Remove !
    content = content.replace('!', '')
    # Remove multiple spaces
    content = re.sub(r'\s+', ' ', content).strip()
    
    return {
        'folio': f'f{folio_full}',
        'location': f'f{folio_full}.{match.group(2)}',
        'voynich': content
    }

def translate_word(word, dictionary):
    clean_word = word.strip()
    if clean_word in dictionary:
        entry = dictionary[clean_word]
        # Prefer 'meaning', then 'semantic_category'
        if entry.get('meaning'):
            return f"[{entry['meaning']}]"
        if entry.get('semantic_category'):
            return f"[{entry['semantic_category']}]"
    return f"[{clean_word}]"

def is_translated(word, dictionary):
    return word in dictionary and (dictionary[word].get('meaning') or dictionary[word].get('semantic_category'))

def main():
    print(f"Loading dictionary from {DICTIONARY_PATH}...")
    dictionary = load_dictionary(DICTIONARY_PATH)
    print(f"Dictionary loaded. Entries: {len(dictionary)}")
    
    print(f"Reading corpus from {CORPUS_PATH}...")
    sentences = []
    with open(CORPUS_PATH, 'r') as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                sentences.append(parsed)
    
    print(f"Extracted {len(sentences)} sentences for Quire 20 (f103-f116).")
    
    # Translate and Analyze
    output_lines = []
    summary_examples = []
    
    total_words = 0
    translated_count = 0
    
    q20_text = ""
    
    output_lines.append("# Recipe Re-Translation (Quire 20)\n")
    
    current_folio = ""
    
    for sent in sentences:
        words = sent['voynich'].split()
        trans_words = []
        
        has_target = any(w in TARGET_WORDS for w in words)
        sentence_translated_count = 0
        
        for w in words:
            total_words += 1
            tr = translate_word(w, dictionary)
            trans_words.append(tr)
            if is_translated(w, dictionary):
                translated_count += 1
                sentence_translated_count += 1
        
        translated_sent = " ".join(trans_words)
        
        if sent['folio'] != current_folio:
            current_folio = sent['folio']
            output_lines.append(f"\n## Folio {current_folio}\n")
        
        output_lines.append(f"**{sent['location']}**")
        output_lines.append(f"> {sent['voynich']}")
        output_lines.append(f"> {translated_sent}")
        output_lines.append("")
        
        # Collect examples
        if has_target and len(summary_examples) < 10: # Get a few candidates
            # Calculate readability for this sentence
            readability = sentence_translated_count / len(words) if words else 0
            if readability > 0.3: # Only pick interesting ones
                summary_examples.append({
                    'voynich': sent['voynich'],
                    'translated': translated_sent,
                    'target_words': [w for w in words if w in TARGET_WORDS]
                })

    # Write Full Translation
    with open(OUTPUT_MD_PATH, 'w') as f:
        f.write("\n".join(output_lines))
    print(f"Wrote full translation to {OUTPUT_MD_PATH}")
    
    # Generate Summary
    readability_pct = (translated_count / total_words * 100) if total_words else 0
    
    summary = []
    summary.append("# Track 227 Results Summary")
    summary.append(f"- **Quire 20 Readability:** {readability_pct:.2f}%")
    summary.append(f"- **Total Words:** {total_words}")
    summary.append(f"- **Translated Words:** {translated_count}")
    summary.append("\n## Key Before vs After Examples")
    summary.append("Focusing on sentences with `qokeedy`, `qokedy`, `qokal`, `qol`.\n")
    
    for ex in summary_examples[:5]:
        summary.append(f"**Original:** `{ex['voynich']}`")
        summary.append(f"**Translation:** `{ex['translated']}`")
        summary.append(f"**Key Words:** {', '.join(ex['target_words'])}")
        summary.append("")

    with open(SUMMARY_PATH, 'w') as f:
        f.write("\n".join(summary))
    print(f"Wrote summary to {SUMMARY_PATH}")

if __name__ == "__main__":
    main()
