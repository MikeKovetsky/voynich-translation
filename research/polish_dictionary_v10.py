import json
import os
from collections import Counter

DICTIONARY_PATH = 'results/dictionary/dictionary_v9_4.json'
PARSED_TEXT_PATH = 'results/parsed_text_v2.json'
OUTPUT_PATH = 'results/dictionary/dictionary_v10_0.json'
SUMMARY_PATH = 'results/track-217-results_summary.md'

def main():
    print(f"Loading {DICTIONARY_PATH}...")
    with open(DICTIONARY_PATH, 'r') as f:
        data = json.load(f)

    entries = data.get('entries', {})
    print(f"Loaded {len(entries)} dictionary entries.")

    print(f"Loading {PARSED_TEXT_PATH}...")
    if not os.path.exists(PARSED_TEXT_PATH):
        print(f"Error: {PARSED_TEXT_PATH} not found.")
        return

    with open(PARSED_TEXT_PATH, 'r') as f:
        parsed_data = json.load(f)

    # Extract words
    words = [item.get('original', '') for item in parsed_data if item.get('original')]
    
    print(f"Total words in parsed text: {len(words)}")
    
    word_counts = Counter(words)
    print(f"Unique words: {len(word_counts)}")

    # Identify unknowns
    unknowns = []
    for word, count in word_counts.most_common():
        if word in entries:
            meaning = entries[word].get('meaning', '')
            if not meaning or meaning.lower() == 'unknown':
                unknowns.append((word, count, "Known (No Meaning)"))
        else:
            # Only consider if frequency > 1 to avoid noise?
            # Task says "Review top 50".
            unknowns.append((word, count, "New"))

    top_50_unknowns = unknowns[:50]

    # Domain Standardization
    domain_map = {
        'astronomical': 'astro',
        'recipe/chemistry': 'recipe',
        'medical': 'recipe', 
        'element': 'recipe',
        # Keep 'grammar', 'botanical' as is
    }
    
    cleaned_entries = {}
    changed_domains = 0
    
    for word, entry in entries.items():
        # 1. Confidence
        conf = entry.get('confidence', 0)
        try:
            conf = float(conf)
        except:
            conf = 0.0
        
        entry['confidence'] = round(max(0.0, min(1.0, conf)), 2)

        # 2. Domain
        dom = entry.get('domain')
        if dom in domain_map:
            entry['domain'] = domain_map[dom]
            changed_domains += 1
        
        # 3. Ensure domain is consistent
        cleaned_entries[word] = entry

    print(f"Standardized domains for {changed_domains} entries.")

    # Generate Summary
    summary_content = f"# Track 217: Dictionary Polish Summary\n\n"
    summary_content += f"## Stats\n"
    summary_content += f"- Total Words in Text: {len(words)}\n"
    summary_content += f"- Unique Words in Text: {len(word_counts)}\n"
    summary_content += f"- Dictionary Size: {len(cleaned_entries)}\n"
    
    # Calculate coverage correctly
    known_tokens_count = sum(1 for w in words if w in cleaned_entries and cleaned_entries[w].get('meaning', '').lower() not in ['', 'unknown'])
    
    summary_content += f"- Token Coverage: {known_tokens_count / len(words):.2%}\n\n"

    summary_content += f"## Top 50 Unknown Words\n"
    summary_content += f"| Word | Count | Status | Morphology Hint |\n"
    summary_content += f"|---|---|---|---|\n"
    
    def guess_category(word):
        if word.endswith('dy'): return 'Verbal/Suffix?'
        if word.endswith('ol'): return 'Noun?'
        if word.startswith('qo'): return 'Prefix:qo'
        return '?'

    for word, count, status in top_50_unknowns:
        hint = guess_category(word)
        summary_content += f"| `{word}` | {count} | {status} | {hint} |\n"

    with open(SUMMARY_PATH, 'w') as f:
        f.write(summary_content)
    
    print(f"Summary written to {SUMMARY_PATH}")

    # Save Dictionary
    data['entries'] = cleaned_entries
    data['version'] = '10.0'
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Dictionary v10.0 written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
