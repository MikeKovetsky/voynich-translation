import csv
import json
import re
import os
from collections import Counter

def load_gold_anchors(filepath):
    anchors = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            anchors.append({
                'word': row['Voynich Word'].strip(),
                'latin': row['Latin Match'],
                'confidence': row['Confidence']
            })
    return anchors

def load_manuscript(filepath):
    words = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            
            # Extract text after the tag <...>
            # Typical line: <f1r.1...> transcribed text
            match = re.search(r'<[^>]+>\s*(.*)', line)
            if match:
                text = match.group(1)
                
                # Cleanup IVTFF specific markers
                # Remove comments {comment}
                text = re.sub(r'\{[^}]+\}', '', text)
                # Remove tags like <...>
                text = re.sub(r'<[^>]+>', '', text)
                # Replace . and , with space
                text = text.replace('.', ' ').replace(',', ' ')
                # Remove other punctuation
                text = re.sub(r'[?!*;:="]', '', text)
                
                parts = text.split()
                for p in parts:
                    p = p.strip()
                    # Filter out clearly non-word tokens
                    if not p or re.search(r'[^a-z0-9]', p): 
                        # If it contains non-alphanumeric, check if it's just some noise or valid EVA
                        # strict EVA is a-z0-9 mostly. 
                        # If it has < or > or $, skip it
                        continue
                        
                    words.append(p)
    return words

def process_anchors(anchors, manuscript_words):
    suffix_counter = Counter()
    anchor_hits = {a['word']: [] for a in anchors}
    
    for word in manuscript_words:
        for anchor in anchors:
            root = anchor['word']
            # strict prefix match
            if word.startswith(root):
                remainder = word[len(root):]
                if remainder:
                    anchor_hits[root].append(remainder)
                    suffix_counter[remainder] += 1
                else:
                    pass
    
    return suffix_counter, anchor_hits

def main():
    gold_anchors_path = 'results/gold_anchors.csv'
    manuscript_path = 'data/eva_ivtff.txt'
    output_suffixes = 'results/proven_suffixes.json'
    
    print("Loading anchors...")
    anchors = load_gold_anchors(gold_anchors_path)
    print(f"Loaded {len(anchors)} anchors.")
    
    print("Loading manuscript...")
    words = load_manuscript(manuscript_path)
    print(f"Loaded {len(words)} words (cleaned).")
    
    print("Processing suffixes...")
    suffix_counts, anchor_hits = process_anchors(anchors, words)
    
    # Identify Top 10
    top_10 = suffix_counts.most_common(10)
    print("Top 10 Proven Suffixes:")
    for s, c in top_10:
        print(f"  -{s}: {c}")
        
    proven_suffixes = []
    for suffix, count in top_10:
        examples = []
        for root, remainders in anchor_hits.items():
            if suffix in remainders:
                examples.append({'root': root, 'word': root + suffix})
                if len(examples) >= 5:
                    break
        proven_suffixes.append({
            'suffix': suffix,
            'count': count,
            'examples': examples
        })
        
    with open(output_suffixes, 'w') as f:
        json.dump(proven_suffixes, f, indent=2)
    print(f"Saved proven suffixes to {output_suffixes}")

    # Update Dictionary v20 -> v21
    v20_path = 'results/dictionary/master_dictionary_v20.json'
    v21_path = 'results/dictionary/master_dictionary_v21.json'
    
    if not os.path.exists(v20_path):
        print(f"Warning: {v20_path} not found. Checking alternatives.")
        v20_path = 'results/dictionary/master_dictionary_v19.json' # Fallback
        
    with open(v20_path, 'r') as f:
        data = json.load(f)
        
    dictionary_entries = data.get('entries', {})
    
    # Update suffixes
    for suffix_info in proven_suffixes:
        s = "-" + suffix_info['suffix'] # Convention: suffixes start with - in dictionary keys? 
        # Looking at v20 snippet: "-y": { ... }
        # So yes, keys for suffixes seem to start with "-"
        
        # Also check if the suffix word itself exists without dash?
        # The task says "Add the Proven Suffixes as grammatical modifiers."
        
        key = s
        if key not in dictionary_entries:
             dictionary_entries[key] = {
                'word': key,
                'part_of_speech': 'Suffix',
                'meaning': f"Grammatical suffix (proven) e.g. {suffix_info['examples'][0]['word']}",
                'confidence': 0.9,
                'source': 'grounded_morphology_v3'
             }
        else:
             entry = dictionary_entries[key]
             entry['confidence'] = 0.9
             entry['source'] = 'grounded_morphology_v3'
             entry['meaning'] = entry.get('meaning', '') + f"; Proven suffix"

    # Update anchors
    for anchor in anchors:
        word = anchor['word']
        latin = anchor['latin']
        
        if word in dictionary_entries:
            entry = dictionary_entries[word]
            entry['latin_match'] = latin
            entry['confidence'] = 1.0
            entry['source'] = 'gold_anchor'
        else:
             dictionary_entries[word] = {
                'word': word,
                'latin_match': latin,
                'confidence': 1.0,
                'source': 'gold_anchor',
                'meaning': f"Anchor: {latin}"
             }
             
    # Save v21
    data['entries'] = dictionary_entries
    data['description'] = "Updated with Gold Anchors and Proven Suffixes (v3)"
    # update date?
    
    with open(v21_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved dictionary v21 to {v21_path}")

if __name__ == "__main__":
    main()
