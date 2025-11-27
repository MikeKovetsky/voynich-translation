import re
import collections
import json
import os

def load_vocab(path):
    with open(path, 'r') as f:
        text = f.read()
    words = []
    for line in text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        clean_line = re.sub(r'<[^>]+>', '', line)
        # Only keep valid EVA chars
        clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
        words.extend(clean_line.split())
    return collections.Counter(words)

def find_affixes(vocab_counter):
    # Simple unsupervised approach:
    # 1. Look for frequent beginning sequences (Prefixes)
    # 2. Look for frequent ending sequences (Suffixes)
    # 3. "Root" is what remains.
    
    words = list(vocab_counter.keys())
    total_tokens = sum(vocab_counter.values())
    
    prefixes = collections.defaultdict(int)
    suffixes = collections.defaultdict(int)
    
    # Sweep for potential affixes of length 1-3
    for word in words:
        count = vocab_counter[word]
        if len(word) > 3:
            for i in range(1, 4):
                pre = word[:i]
                suf = word[-i:]
                prefixes[pre] += count
                suffixes[suf] += count
                
    # Filter common ones
    common_prefixes = {k: v for k, v in prefixes.items() if v > total_tokens * 0.01} # >1% freq
    common_suffixes = {k: v for k, v in suffixes.items() if v > total_tokens * 0.05} # >5% freq (suffixes common in Voynich)
    
    return common_prefixes, common_suffixes

def segment_word(word, prefixes, suffixes):
    # Greedy stripping
    best_p = ""
    best_s = ""
    
    # Try to match longest valid prefix
    for i in range(min(len(word)-1, 3), 0, -1):
        p = word[:i]
        if p in prefixes:
            best_p = p
            break
            
    remaining = word[len(best_p):]
    
    # Try to match longest valid suffix
    for i in range(min(len(remaining)-1, 3), 0, -1):
        s = remaining[-i:]
        if s in suffixes:
            best_s = s
            break
            
    root = remaining[:len(remaining)-len(best_s)]
    
    return best_p, root, best_s

def main():
    print("Starting Morphological Segmentation...")
    input_path = 'data/eva_ivtff.txt'
    
    if not os.path.exists(input_path):
        print("Data file not found.")
        return

    vocab = load_vocab(input_path)
    print(f"Vocabulary Size: {len(vocab)}")
    
    prefixes, suffixes = find_affixes(vocab)
    
    print("\nPotential Prefixes:")
    for p, c in sorted(prefixes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {p}: {c}")
        
    print("\nPotential Suffixes:")
    for s, c in sorted(suffixes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"- {s}: {c}")
        
    # Build Root Map
    root_map = {}
    roots = collections.defaultdict(int)
    
    for word in vocab:
        p, r, s = segment_word(word, prefixes, suffixes)
        if len(r) > 1: # Avoid single letter roots
            root_map[word] = r
            roots[r] += vocab[word]
        else:
            root_map[word] = word # Keep original if root too small
            roots[word] += vocab[word]
            
    # Save results
    with open('results/morphology_rules.json', 'w') as f:
        json.dump({'prefixes': list(prefixes.keys()), 'suffixes': list(suffixes.keys())}, f, indent=2)
        
    with open('results/root_mapping.json', 'w') as f:
        json.dump(root_map, f, indent=2)
        
    print(f"\nIdentified {len(roots)} unique roots from {len(vocab)} words.")
    print(f"Reduction factor: {len(vocab)/len(roots):.2f}x")

if __name__ == "__main__":
    main()
