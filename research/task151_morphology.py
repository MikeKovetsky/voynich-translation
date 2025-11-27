import json
import re
import collections
import os

def load_vocab(path):
    with open(path, 'r') as f:
        text = f.read()
    words = []
    for line in text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        clean_line = re.sub(r'<[^>]+>', '', line)
        clean_line = clean_line.replace('.', ' ') # CRITICAL FIX
        clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
        words.extend(clean_line.split())
    return collections.Counter(words)

def find_affixes(vocab_counter):
    words = list(vocab_counter.keys())
    total_tokens = sum(vocab_counter.values())
    
    prefixes = collections.defaultdict(int)
    suffixes = collections.defaultdict(int)
    
    for word in words:
        count = vocab_counter[word]
        if len(word) > 3:
            for i in range(1, 4):
                pre = word[:i]
                suf = word[-i:]
                prefixes[pre] += count
                suffixes[suf] += count
                
    common_prefixes = {k: v for k, v in prefixes.items() if v > total_tokens * 0.01} 
    common_suffixes = {k: v for k, v in suffixes.items() if v > total_tokens * 0.05} 
    
    return common_prefixes, common_suffixes

def main():
    print("Re-running Morphology Discovery with Fixed Parsing...")
    input_path = 'data/eva_ivtff.txt'
    
    if not os.path.exists(input_path):
        print("Data file not found.")
        return

    vocab = load_vocab(input_path)
    print(f"Vocabulary Size: {len(vocab)}")
    
    prefixes, suffixes = find_affixes(vocab)
    
    # Save results
    with open('results/morphology_rules.json', 'w') as f:
        json.dump({'prefixes': list(prefixes.keys()), 'suffixes': list(suffixes.keys())}, f, indent=2)
        
    print("Updated morphology_rules.json")

if __name__ == "__main__":
    main()
