import json
import re
import os

DICTIONARY_PATH = 'results/dictionary/dictionary_v9_1.json'
TEXT_PATH = 'results/segmented_text.txt'
OUTPUT_PATH = 'results/astro_translations_v1.md'
SUMMARY_PATH = 'results/track-193-results_summary.md'

def load_dictionary():
    with open(DICTIONARY_PATH, 'r') as f:
        data = json.load(f)
    return data.get('entries', {})

def clean_text(line):
    # Remove line ID <...>
    line = re.sub(r'^<[^>]+>\s*', '', line)
    # Remove comments #...
    line = re.sub(r'#.*$', '', line)
    # Remove tags <...>
    line = re.sub(r'<[^>]+>', '', line)
    # Remove specific chars like ! ? ,
    line = re.sub(r'[!?,]', '', line)
    return line.strip()

def get_sentences():
    sentences = []
    seen_sentences = set()
    
    with open(TEXT_PATH, 'r') as f:
        for line in f:
            if line.strip().startswith('#'): continue
            
            cleaned = clean_text(line)
            if not cleaned: continue
            
            # Split into words by dot or space
            words = [w for w in re.split(r'[.\s]+', cleaned) if w]
            if len(words) < 3: continue
            
            # Filter out junk with very long words
            if any(len(w) > 25 for w in words): continue

            # Deduplicate
            original = ".".join(words)
            if original in seen_sentences:
                continue
            seen_sentences.add(original)
            
            # Criteria: os and (chol or shos)
            # Check for 'os' ending or exact 'os'
            has_star = any(w.endswith('os') or w == 'os' for w in words)
            # Check for 'chol' or 'shos' or 'cheol' substring
            has_plant = any('chol' in w or 'shos' in w or 'cheol' in w for w in words)
            
            if has_star and has_plant:
                sentences.append(words)
                if len(sentences) >= 30: # Get enough candidates
                    break
    return sentences

def translate_word(word, dictionary):
    # Grammar Rules
    prefix = ""
    root = word
    role = ""
    
    # Check for prefixes
    # ol- (The/Subject)
    if word.startswith('ol') and len(word) > 2:
        prefix = 'ol'
        root = word[2:]
        role = "The (Subject)"
    # ok- (With/Object)
    elif word.startswith('ok') and len(word) > 2:
        prefix = 'ok'
        root = word[2:]
        role = "With (Object)"
    # ot- (From/Source)
    elif word.startswith('ot') and len(word) > 2:
        prefix = 'ot'
        root = word[2:]
        role = "From (Source)"
    # qok- (Verb)
    elif word.startswith('qok') and len(word) > 3:
        prefix = 'qok'
        root = word[3:]
        role = "Verb"
    
    # Lookup root in dictionary
    meaning = ""
    
    # Helper to get meaning
    def get_mean(w):
        entry = dictionary.get(w)
        if entry:
            return entry.get('meaning') or entry.get('voynich') or w
        return None

    # Try root
    found_meaning = get_mean(root)
    
    # If not found and we stripped a prefix, maybe the prefix wasn't a prefix?
    # Or try looking up the full word.
    full_word_meaning = get_mean(word)
    
    if not found_meaning:
        if full_word_meaning:
            # Fallback to full word meaning if root not found
            meaning = full_word_meaning
            role = "" # Reset role if we used full word
        else:
            meaning = f"[{root}?]"
    else:
        meaning = found_meaning

    # Format
    if role == "Verb":
        return f"make-{meaning}" # "makes X" or similar
    elif role == "The (Subject)":
        return f"The {meaning}"
    elif role == "With (Object)":
        return f"with {meaning}"
    elif role == "From (Source)":
        return f"from {meaning}"
    else:
        return meaning

def process():
    dictionary = load_dictionary()
    sentences = get_sentences()
    
    # Select best 10 (shortest/cleanest?)
    # Or just first 10 valid ones.
    selected_sentences = sentences[:10]
    
    with open(OUTPUT_PATH, 'w') as f:
        f.write("# Astro Sentences Translations (v1)\n\n")
        
        count = 0
        for words in selected_sentences:
            original = ".".join(words)
            translated_words = [translate_word(w, dictionary) for w in words]
            gloss = " ".join(translated_words)
            
            f.write(f"## Sentence {count + 1}\n\n")
            f.write(f"**Original:** `{original}`\n\n")
            f.write(f"**Gloss:** {gloss}\n\n")
            
            # Rough smoothing for Draft
            draft = gloss.replace('[', '').replace('?]', '')
            draft = draft.replace('make-', 'makes ')
            f.write(f"**Draft:** {draft}\n\n")
            f.write("---\n\n")
            count += 1
            
    # Summary
    with open(SUMMARY_PATH, 'w') as f:
        f.write("# Track 193 Results Summary\n\n")
        f.write("## Overview\n")
        f.write(f"Selected and translated {count} sentences matching 'os' (Star) and 'chol/shos' (Plant) criteria.\n\n")
        f.write("## Output\n")
        f.write(f"- Translations: `{OUTPUT_PATH}`\n")
        f.write("## Process\n")
        f.write("1. Filtered `results/segmented_text.txt` for sentences with 'os' and 'chol'/'shos'.\n")
        f.write("2. Applied grammar rules: `ol-` (The), `ok-` (With), `ot-` (From), `qok-` (Verb).\n")
        f.write("3. Looked up roots in `results/dictionary/dictionary_v9_1.json`.\n")

if __name__ == "__main__":
    process()
