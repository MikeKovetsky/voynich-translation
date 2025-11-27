import re
import os

def main():
    print("Starting POS Tagging...")
    
    input_path = 'results/segmented_text.txt'
    if not os.path.exists(input_path):
        print("Segmented text not found.")
        return
        
    with open(input_path, 'r') as f:
        lines = f.read().splitlines()
        
    tagged_lines = []
    tag_stats = {}
    
    # Grammar Rules (Hypothesis)
    # Order matters! Longest match first.
    PREFIX_MAP = {
        'qo': 'VERB',
        'qok': 'VERB', # Variant
        'y': 'CONJ',
        'd': 'IMP', # Imperative
        'dai': 'IMP',
        'da': 'IMP',
        'o': 'NOUN', # Determiner/Noun marker
        'l': 'PREP',
        's': 'REL', # Relative/Connector
        'sh': 'REL'
    }
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            tagged_lines.append(line)
            continue
            
        words = line.split()
        tagged_words = []
        
        for w in words:
            # Clean
            clean_w = re.sub(r'[^a-zA-Z0-9]', '', w)
            if not clean_w:
                tagged_words.append(w)
                continue
                
            # Determine Tag
            tag = 'ROOT' # Default
            
            # Check prefixes
            # Sort prefixes by length to match specific first
            for p, t in sorted(PREFIX_MAP.items(), key=lambda x: len(x[0]), reverse=True):
                if clean_w.startswith(p):
                    # Heuristic: Only if remaining length is sufficient?
                    if len(clean_w) > len(p):
                        tag = t
                        break
            
            # Special override for known high-freq words?
            if clean_w == 'daiin': tag = 'IMP'
            
            tagged_words.append(f"{tag}:{clean_w}")
            tag_stats[tag] = tag_stats.get(tag, 0) + 1
            
        tagged_lines.append(" ".join(tagged_words))
        
    # Output Tagged Text
    with open('results/tagged_text.txt', 'w') as f:
        f.write("\n".join(tagged_lines))
        
    # Pattern Analysis (Bigrams)
    bigrams = {}
    tags_only = [w.split(':')[0] for line in tagged_lines if not line.startswith('#') for w in line.split() if ':' in w]
    
    for i in range(len(tags_only)-1):
        pair = f"{tags_only[i]}-{tags_only[i+1]}"
        bigrams[pair] = bigrams.get(pair, 0) + 1
        
    # Report
    with open('results/grammar_patterns.md', 'w') as f:
        f.write("# Grammar Pattern Report\n\n")
        f.write("## Tag Counts\n")
        for t, c in sorted(tag_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {t}: {c}\n")
            
        f.write("\n## Top 10 Tag Sequences (Bigrams)\n")
        for b, c in sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"- {b}: {c}\n")
            
    print("Tagging complete.")

if __name__ == "__main__":
    main()
