import json

def extract_top_words():
    with open('results/dictionary/dictionary_v9_4.json', 'r') as f:
        data = json.load(f)
    
    entries = data.get('entries', {})
    
    # List of specific words to look for
    target_words = ['choly', 'ald', 'os', 'saiin']
    
    # Collect all high confidence words
    high_conf_words = []
    target_found = []
    
    for word, details in entries.items():
        if 'voynich' not in details:
            details['voynich'] = word
            
        conf = details.get('confidence', 0)
        conf_level = details.get('confidence_level', '')
        
        if word in target_words:
            target_found.append(details)
        elif conf_level == 'ULTRA_HIGH' or conf >= 0.9:
            high_conf_words.append(details)
            
    # Sort high_conf_words by confidence descending
    high_conf_words.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    # Combine target words first, then high confidence
    all_words = target_found + high_conf_words
    
    # Dedup based on voynich word
    seen = set()
    unique_words = []
    for w in all_words:
        if w['voynich'] not in seen:
            unique_words.append(w)
            seen.add(w['voynich'])
            
    # Print top 20
    print("Top 20 Words (Prioritizing targets):")
    for i, w in enumerate(unique_words[:20]):
        print(f"| `{w['voynich']}` | **{w.get('meaning', 'Unknown')}** | {w.get('confidence_level', 'High')} |")

if __name__ == "__main__":
    extract_top_words()
