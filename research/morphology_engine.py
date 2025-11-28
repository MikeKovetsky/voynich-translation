import re
from collections import Counter
import os

def load_words(filepath):
    words = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#"): continue
            match = re.match(r"<(f\d+[rv]\d?)\.(\d+).*?;H>\s+(.*)", line)
            if match:
                text = match.group(3).strip().replace("!", "").replace("*", "")
                line_words = [w for w in text.split('.') if w and w != "-"]
                words.extend(line_words)
    return words

def strip_suffixes(word):
    # Common EVA suffixes based on visual structure
    suffixes = [
        ('y', 1), ('dy', 2), ('oly', 3), ('ary', 3), 
        ('aiin', 4), ('iin', 3), ('in', 2), 
        ('ol', 2), ('or', 2), ('al', 2), 
        ('s', 1), ('r', 1), ('l', 1), ('n', 1)
    ]
    
    # Try to match longest suffix first
    # Only strip if remainder is at least 2 chars (to avoid stripping 'or' to '')
    for suff, length in suffixes:
        if word.endswith(suff) and len(word) > length + 1:
            return word[:-length], suff
            
    return word, ""

def analyze_morphology(input_file, output_file):
    words = load_words(input_file)
    print(f"Loaded {len(words)} words.")
    
    vocab = set(words)
    vocab_size = len(vocab)
    
    roots = []
    suffix_counts = Counter()
    root_counts = Counter()
    
    for word in words:
        root, suff = strip_suffixes(word)
        roots.append(root)
        root_counts[root] += 1
        if suff:
            suffix_counts[suff] += 1
            
    unique_roots = set(roots)
    root_size = len(unique_roots)
    
    compression = (1 - (root_size / vocab_size)) * 100
    
    # Top Roots
    top_roots = root_counts.most_common(50)
    top_suffixes = suffix_counts.most_common(20)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Track 312: Morphology Report\n\n")
        f.write(f"- **Total Tokens:** {len(words)}\n")
        f.write(f"- **Original Vocabulary:** {vocab_size}\n")
        f.write(f"- **Root Vocabulary:** {root_size}\n")
        f.write(f"- **Compression Rate:** {compression:.2f}% (Higher = More Inflected)\n\n")
        
        f.write("## Top 20 Suffixes\n")
        f.write("| Suffix | Count | %\n|---|---|---|\n")
        for s, c in top_suffixes:
            pct = (c / len(words)) * 100
            f.write(f"| -{s} | {c} | {pct:.1f}% |\n")
            
        f.write("\n## Top 50 Roots\n")
        f.write("| Root | Count | Orig Examples\n|---|---|---|\n")
        for r, c in top_roots:
            # Find original words that map to this root
            examples = [w for w in vocab if w.startswith(r) and w != r][:3]
            ex_str = ", ".join(examples)
            f.write(f"| {r} | {c} | {ex_str} |\n")

    print(f"Analysis complete. Report: {output_file}")

if __name__ == "__main__":
    analyze_morphology("data/eva_ivtff.txt", "results/morphology_report_v1.md")
