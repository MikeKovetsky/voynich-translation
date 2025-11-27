import json
import collections
import re
import os

def load_parsed_data(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_tag(prefixes, word_text):
    # Default tag
    tag = "ROOT"
    
    # Helper to check if any prefix starts with pattern
    def has_prefix(pat):
        return any(p.startswith(pat) for p in prefixes)
    
    if has_prefix('qo'):
        tag = "VERB"
    elif has_prefix('d') or word_text == 'daiin' or word_text.startswith('daiin'): # explicit check
        tag = "IMP"
    elif has_prefix('y'):
        tag = "CONJ"
    elif has_prefix('o'):
        tag = "NOUN"
    elif has_prefix('l'):
        tag = "PREP"
    elif prefixes:
        tag = "OTHER" 
        
    return tag

def main():
    print("Loading data...")
    parsed_data = load_parsed_data('results/parsed_text_v2.json')
    
    tagged_output = []
    segmented_output = []
    
    tag_stats = collections.Counter()
    bigrams = collections.defaultdict(int)
    trigrams = collections.defaultdict(int)
    
    tag_history = [] 
    
    for entry in parsed_data:
        prefixes = entry.get('prefix', [])
        roots = entry.get('roots', [])
        suffixes = entry.get('suffix', [])
        original = entry.get('original', '')
        
        if not roots:
            continue
            
        segments = []
        
        # First root
        root0 = roots[0]
        p_str = "-".join(prefixes) + "-" if prefixes else ""
        
        if len(roots) == 1:
            s_str = "-" + "-".join(suffixes) if suffixes else ""
            seg_text = f"{p_str}{root0}{s_str}"
            tag = get_tag(prefixes, original)
            segments.append((tag, seg_text))
        else:
            # Multiple roots
            seg1_text = f"{p_str}{root0}"
            tag1 = get_tag(prefixes, original)
            segments.append((tag1, seg1_text))
            
            for r in roots[1:-1]:
                segments.append(("ROOT", r))
                
            last_root = roots[-1]
            s_str = "-" + "-".join(suffixes) if suffixes else ""
            seg_last_text = f"{last_root}{s_str}"
            segments.append(("ROOT", seg_last_text))
            
        for tag, text in segments:
            tagged_output.append(f"{tag}:{text}")
            segmented_output.append(text)
            
            tag_stats[tag] += 1
            tag_history.append(tag)
            if len(tag_history) >= 2:
                bigrams[tuple(tag_history[-2:])] += 1
            if len(tag_history) >= 3:
                trigrams[tuple(tag_history[-3:])] += 1
    
    print("Writing results...")
    
    # Helper to write with line wrapping
    def write_wrapped(path, items, width=15):
        with open(path, 'w') as f:
            for i in range(0, len(items), width):
                chunk = items[i:i+width]
                f.write(" ".join(chunk) + "\n")
    
    write_wrapped('results/tagged_text.txt', tagged_output)
    write_wrapped('results/segmented_text.txt', segmented_output)
        
    # Generate Report
    with open('results/grammar_patterns.md', 'w') as f:
        f.write("# Grammar Patterns Analysis\n\n")
        
        f.write("## Tag Frequencies\n")
        for tag, count in tag_stats.most_common():
            f.write(f"- **{tag}**: {count}\n")
            
        f.write("\n## Top 10 Bigrams (2-Tag Sequences)\n")
        f.write("| Sequence | Count | Description |\n")
        f.write("|----------|-------|-------------|\n")
        for gram, count in sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[:10]:
            seq = " -> ".join(gram)
            desc = describe_ngram(gram)
            f.write(f"| {seq} | {count} | {desc} |\n")
            
        f.write("\n## Top 10 Trigrams (Sentence Structure)\n")
        f.write("| Sequence | Count |\n")
        f.write("|----------|-------|\n")
        for gram, count in sorted(trigrams.items(), key=lambda x: x[1], reverse=True)[:10]:
            seq = " -> ".join(gram)
            f.write(f"| {seq} | {count} |\n")
            
        f.write("\n## Analysis\n")
        f.write("### Common Structures\n")
        top_bi = sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[0][0]
        f.write(f"- Most common pair: **{' + '.join(top_bi)}**\n")
        
        imp_noun = bigrams.get(('IMP', 'NOUN'), 0)
        imp_root = bigrams.get(('IMP', 'ROOT'), 0)
        f.write(f"- IMP often followed by NOUN ({imp_noun}) or ROOT ({imp_root}). Total: {imp_noun + imp_root}\n")

def describe_ngram(gram):
    descriptions = {
        "VERB": "Action",
        "NOUN": "Object",
        "IMP": "Command",
        "CONJ": "Connector",
        "PREP": "Preposition",
        "ROOT": "Generic",
        "OTHER": "Unknown"
    }
    return " + ".join([descriptions.get(t, t) for t in gram])

if __name__ == "__main__":
    main()
