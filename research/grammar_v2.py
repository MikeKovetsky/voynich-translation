import json
import re
import os
from collections import Counter, defaultdict

def load_parsed_data(path):
    print(f"Loading parsed data from {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_lines_from_raw(raw_path, parsed_data):
    print(f"Reconstructing lines from {raw_path}...")
    with open(raw_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = []
    parsed_index = 0
    total_parsed = len(parsed_data)
    
    for line in text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        if ';H>' not in line:
            continue
            
        # Same cleaning as task153_morph_parser.py
        clean_line = re.sub(r'<[^>]+>', '', line)
        clean_line = re.sub(r'[.,!=]', ' ', clean_line)
        clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
        words_in_line = clean_line.split()
        
        reconstructed_line = []
        for _ in words_in_line:
            if parsed_index < total_parsed:
                word_obj = parsed_data[parsed_index]
                parsed_index += 1
                
                # Construct Prefix-ROOT representation
                prefixes = "".join(word_obj.get('prefix', []))
                root = word_obj.get('root', '')
                
                if prefixes:
                    rep = f"{prefixes}-{root}"
                else:
                    rep = root
                
                reconstructed_line.append({
                    'rep': rep,
                    'prefix': prefixes,
                    'root': root,
                    'obj': word_obj
                })
            else:
                # Should not happen if files match
                break
        
        if reconstructed_line:
            lines.append(reconstructed_line)
            
    print(f"Reconstructed {len(lines)} lines.")
    return lines

def analyze_ngrams(lines):
    print("Analyzing N-grams...")
    
    # What follows qok-?
    qok_followers = Counter()
    # What follows d-?
    d_followers = Counter()
    
    line_starts = Counter()
    line_ends = Counter()
    
    for line in lines:
        if not line:
            continue
            
        # Line start/end
        line_starts[line[0]['rep']] += 1
        line_ends[line[-1]['rep']] += 1
        
        for i in range(len(line) - 1):
            curr = line[i]
            next_word = line[i+1]
            
            # Check qok- (prefix is 'qok' or 'qo'+'k' -> 'qok')
            # We store joined prefix in 'prefix'
            if curr['prefix'] == 'qok':
                qok_followers[next_word['rep']] += 1
            
            if curr['prefix'] == 'd':
                d_followers[next_word['rep']] += 1
                
    return {
        'qok_followers': qok_followers,
        'd_followers': d_followers,
        'line_starts': line_starts,
        'line_ends': line_ends
    }

def analyze_key_words(lines):
    print("Analyzing Key Verbs and Nouns...")
    
    # Roots that take qok-
    qok_roots = Counter()
    
    # Roots that take o- or ol-
    o_roots = Counter()
    ol_roots = Counter() # identifying specifically ol- roots
    noun_roots = Counter() # combined o- and ol-
    
    for line in lines:
        for word in line:
            p = word['prefix']
            r = word['root']
            rep = word['rep']
            
            if p == 'qok':
                qok_roots[rep] += 1 # "e.g. qok-ee" -> store full rep or just root?
                # Task says: "List the top 10 roots that take qok-. (e.g., qok-ee, qok-ed, qok-ai)"
                # The example shows the full form 'qok-ee'. So I'll count the full form.
                # But wait, "List the top 10 ROOTS that take qok-".
                # If I list 'qok-ee', I am listing the word.
                # If I list 'ee', I am listing the root.
                # The example `qok-ee` suggests listing the combination.
                # I will list the combination.
                
            if p == 'o':
                noun_roots[rep] += 1
            elif p == 'ol':
                noun_roots[rep] += 1

    return {
        'qok_roots': qok_roots,
        'noun_roots': noun_roots
    }

def main():
    parsed_path = 'results/parsed_text.json'
    raw_path = 'data/eva_ivtff.txt'
    output_path = 'results/sentence_structure_v2.md'
    
    if not os.path.exists(parsed_path) or not os.path.exists(raw_path):
        print("Input files missing.")
        return

    parsed_data = load_parsed_data(parsed_path)
    lines = load_lines_from_raw(raw_path, parsed_data)
    
    ngram_stats = analyze_ngrams(lines)
    keyword_stats = analyze_key_words(lines)
    
    # Generate Report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Sentence Structure Analysis (Grammar v2)\n\n")
        
        f.write("## 1. Sentence Reconstruction\n")
        f.write(f"- Reconstructed {len(lines)} lines/sentences.\n")
        f.write("- Representing words as `Prefix-ROOT`.\n\n")
        
        f.write("## 2. N-gram Analysis\n\n")
        
        f.write("### What follows `qok-`?\n")
        for word, count in ngram_stats['qok_followers'].most_common(10):
            f.write(f"- `{word}`: {count}\n")
        f.write("\n")
        
        f.write("### What follows `d-`?\n")
        for word, count in ngram_stats['d_followers'].most_common(10):
            f.write(f"- `{word}`: {count}\n")
        f.write("\n")
        
        f.write("### Common Line Starters\n")
        for word, count in ngram_stats['line_starts'].most_common(10):
            f.write(f"- `{word}`: {count}\n")
        f.write("\n")

        f.write("### Common Line Enders\n")
        for word, count in ngram_stats['line_ends'].most_common(10):
            f.write(f"- `{word}`: {count}\n")
        f.write("\n")
        
        f.write("## 3. Key Verbs (qok-)\n")
        f.write("Top roots/words with `qok-` prefix:\n")
        for word, count in keyword_stats['qok_roots'].most_common(15):
            f.write(f"- `{word}`: {count}\n")
        f.write("\n")
        f.write("**Analysis:** Do these correspond to 'Mix', 'Take', 'Put'?\n")
        f.write("(Subjective analysis required based on context and root dictionary)\n\n")
        
        f.write("## 4. Key Nouns (o-, ol-)\n")
        f.write("Top roots/words with `o-` or `ol-` prefix:\n")
        for word, count in keyword_stats['noun_roots'].most_common(15):
            f.write(f"- `{word}`: {count}\n")
            
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    main()
