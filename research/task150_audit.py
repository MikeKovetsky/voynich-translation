import os
import math
import collections
import re
import glob

def calculate_entropy(text, order=1):
    if not text:
        return 0
    
    if order == 1:
        counts = collections.Counter(text)
        total = len(text)
    elif order == 2:
        pairs = [text[i:i+2] for i in range(len(text)-1)]
        counts = collections.Counter(pairs)
        total = len(pairs)
        
    entropy = 0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def load_voynich_raw(path):
    with open(path, 'r') as f:
        text = f.read()
    # Remove comments and metadata, keep only EVA text
    # Assuming format like <f1r.1> word word word
    words = []
    for line in text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        # Remove line tags <...>
        clean_line = re.sub(r'<[^>]+>', '', line)
        clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
        words.extend(clean_line.split())
    return "".join(words) # Character stream for entropy

def load_translations(path_glob):
    files = glob.glob(path_glob)
    words = []
    for fpath in files:
        with open(fpath, 'r') as f:
            content = f.read()
            # Skip markdown headers
            lines = [l for l in content.splitlines() if not l.startswith('#') and not l.startswith('---')]
            text = " ".join(lines)
            # Simple cleaning
            clean_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
            words.extend(clean_text.split())
    return words

def main():
    print("Starting Statistical Audit...")
    
    # 1. Entropy Analysis
    raw_path = 'data/eva_ivtff.txt'
    if os.path.exists(raw_path):
        raw_text = load_voynich_raw(raw_path)
        h1_raw = calculate_entropy(raw_text, 1)
        h2_raw = calculate_entropy(raw_text, 2)
        print(f"Voynich Raw Entropy (H1): {h1_raw:.4f} bits/char")
        print(f"Voynich Raw Entropy (H2): {h2_raw:.4f} bits/char")
    else:
        print(f"Warning: {raw_path} not found.")

    # 2. Translation Analysis
    trans_glob = 'translated/*.md'
    trans_words = load_translations(trans_glob)
    
    if trans_words:
        trans_text = "".join(trans_words)
        h1_trans = calculate_entropy(trans_text, 1)
        h2_trans = calculate_entropy(trans_text, 2)
        print(f"Translation Entropy (H1): {h1_trans:.4f} bits/char")
        print(f"Translation Entropy (H2): {h2_trans:.4f} bits/char")
        
        # 3. Zipf's Law
        counts = collections.Counter(trans_words)
        sorted_counts = counts.most_common()
        
        print("\nTop 20 Translated Words:")
        for word, count in sorted_counts[:20]:
            print(f"{word}: {count}")
            
        # Check for repetition "word word"
        repeats = 0
        total_pairs = len(trans_words) - 1
        for i in range(total_pairs):
            if trans_words[i] == trans_words[i+1]:
                repeats += 1
        
        repeat_rate = (repeats / total_pairs) * 100 if total_pairs > 0 else 0
        print(f"\nRepetition Rate (Immediate Bigrams): {repeat_rate:.2f}%")

    else:
        print("No translation files found to analyze.")

if __name__ == "__main__":
    main()
