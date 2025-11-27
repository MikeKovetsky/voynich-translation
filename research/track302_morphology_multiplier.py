import json
import re
import os

DICTIONARY_PATH = 'results/dictionary/master_dictionary_v16.json'
TRANSCRIPTION_PATH = 'data/eva_ivtff.txt'
OUTPUT_JSON = 'results/dictionary_expansion_v17_algo.json'
OUTPUT_SUMMARY = 'results/track-302-results_summary.md'

# Transformation Rules
RULES = [
    {'type': 'suffix', 'affix': 'aiin', 'meaning_append': ' (Collection of / Set of)'},
    {'type': 'suffix', 'affix': 'dy', 'meaning_append': ' (Related to / Adjective)'},
    {'type': 'prefix', 'affix': 'o', 'meaning_prepend': 'The / Essence of '},
    {'type': 'prefix', 'affix': 'qok', 'meaning_prepend': 'Process / Cook '}
]

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('entries', {})

def load_words_from_ivtff(path):
    words = set()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for H version (Takahashi)
            # Format: <locator;H> text
            match = re.match(r'^<[^>]+;H>\s+(.+)$', line)
            if match:
                text = match.group(1)
                # Split by dots
                parts = text.split('.')
                for p in parts:
                    p = p.strip()
                    if p:
                        words.add(p)
    return words

def main():
    print("Loading dictionary...")
    if not os.path.exists(DICTIONARY_PATH):
        print(f"Error: {DICTIONARY_PATH} not found.")
        return

    dictionary = load_dictionary(DICTIONARY_PATH)
    
    print("Loading transcription...")
    if not os.path.exists(TRANSCRIPTION_PATH):
        print(f"Error: {TRANSCRIPTION_PATH} not found.")
        return

    all_words = load_words_from_ivtff(TRANSCRIPTION_PATH)
    print(f"Found {len(all_words)} unique words in transcription.")

    # Identify Known Roots
    known_roots = {}
    for word, entry in dictionary.items():
        conf = entry.get('confidence_level', '')
        meaning = entry.get('meaning', '')
        # Check for HIGH/PROVEN confidence and non-empty meaning
        if (conf == 'HIGH' or conf == 'PROVEN') and meaning:
            known_roots[word] = meaning
    
    print(f"Found {len(known_roots)} known roots.")

    # Identify Unknown words
    unknown_words = [w for w in all_words if w not in known_roots]
    print(f"Found {len(unknown_words)} unknown words.")

    # Apply Rules
    new_entries = {}
    
    for word in unknown_words:
        for rule in RULES:
            root = None
            affix = rule['affix']
            
            if rule['type'] == 'suffix':
                if word.endswith(affix):
                    potential_root = word[:-len(affix)]
                    if potential_root in known_roots:
                        root = potential_root
            elif rule['type'] == 'prefix':
                if word.startswith(affix):
                    potential_root = word[len(affix):]
                    if potential_root in known_roots:
                        root = potential_root
            
            if root:
                root_meaning = known_roots[root]
                new_meaning = ""
                if 'meaning_append' in rule:
                    new_meaning = f"{root_meaning}{rule['meaning_append']}"
                elif 'meaning_prepend' in rule:
                    new_meaning = f"{rule['meaning_prepend']}{root_meaning}"
                
                new_entries[word] = {
                    "voynich": word,
                    "meaning": new_meaning,
                    "language": "voynich_algo",
                    "confidence": 0.4,
                    "confidence_level": "ALGORITHMIC",
                    "domain": "morphology",
                    "source": "Track302_Morphology",
                    "derived_from": root,
                    "rule": f"{rule['type']}_{affix}"
                }
                break 
                
    print(f"Generated {len(new_entries)} new entries.")
    
    # Save Output
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(new_entries, f, indent=2)
        
    # Calculate Statistics for Summary
    word_counts = {}
    total_tokens = 0
    with open(TRANSCRIPTION_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.match(r'^<[^>]+;H>\s+(.+)$', line)
            if match:
                text = match.group(1)
                parts = text.split('.')
                for p in parts:
                    p = p.strip()
                    if p:
                        total_tokens += 1
                        word_counts[p] = word_counts.get(p, 0) + 1
                        
    newly_covered_tokens = 0
    for word in new_entries:
        newly_covered_tokens += word_counts.get(word, 0)
        
    coverage_gain_percent = (newly_covered_tokens / total_tokens) * 100 if total_tokens > 0 else 0
    
    summary = f"""# Track 302 Results Summary

## Overview
- **Goal**: Algorithmic expansion of the dictionary by applying known grammar rules.
- **Input Dictionary**: `{DICTIONARY_PATH}`
- **Transcription**: `{TRANSCRIPTION_PATH}`

## Statistics
- **Total Unique Words in Transcription**: {len(all_words)}
- **Known Roots (High Confidence)**: {len(known_roots)}
- **Unknown Words Processed**: {len(unknown_words)}
- **New Algorithmic Entries Generated**: {len(new_entries)}

## Coverage Impact
- **Total Tokens in Corpus**: {total_tokens}
- **Tokens Covered by New Entries**: {newly_covered_tokens}
- **Estimated Coverage Gain**: {coverage_gain_percent:.2f}%

## Rules Applied
- Suffix `-aiin` -> "Collection of / Set of"
- Suffix `-dy` -> "Related to / Adjective"
- Prefix `o-` -> "The / Essence of"
- Prefix `qok-` -> "Process / Cook"

## Outputs
- `{OUTPUT_JSON}`
"""

    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write(summary)
    print("Summary written.")

if __name__ == "__main__":
    main()
