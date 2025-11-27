import re
import collections
import os
import json

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.readlines()

def parse_eva_line(line):
    match = re.match(r"^<f(\d+)([rv])\.([^;]+);([A-Z])>\s+(.*)$", line)
    if match:
        return int(match.group(1)), match.group(2), match.group(3), match.group(4), match.group(5)
    return None

def get_quire_20_text(lines):
    extracted_text = []
    current_paragraph = []
    
    for line in lines:
        parsed = parse_eva_line(line)
        if not parsed: continue
        folio_num, side, section, transcriber, text = parsed
        if not (103 <= folio_num <= 116): continue
        if transcriber != 'H': continue
        
        text = text.replace('%', '').replace('?', '')
        is_end_of_paragraph = '<$>' in text
        text = text.replace('<$>', '')
        
        words = [w.strip() for w in text.split('.') if w.strip()]
        words = [w.replace('!', '').replace(',', '') for w in words]
        
        current_paragraph.extend(words)
        
        if is_end_of_paragraph:
            extracted_text.append(current_paragraph)
            current_paragraph = []
            
    return extracted_text

def analyze_end_verbs(paragraphs):
    last_words = []
    for p in paragraphs:
        if p:
            last_words.append(p[-1])
    return collections.Counter(last_words)

def analyze_proximity(paragraphs, target_word, ref_word, window=5):
    count = 0
    distances = []
    
    for p in paragraphs:
        if target_word in p and ref_word in p:
            # Find indices
            t_indices = [i for i, x in enumerate(p) if x == target_word]
            r_indices = [i for i, x in enumerate(p) if x == ref_word]
            
            for ti in t_indices:
                for ri in r_indices:
                    dist = ti - ri
                    if abs(dist) <= window:
                        count += 1
                        distances.append(dist)
                        
    return count, distances

def main():
    input_file = 'data/eva_ivtff.txt'
    lines = load_file(input_file)
    paragraphs = get_quire_20_text(lines)
    
    print(f"Analyzed {len(paragraphs)} paragraphs in Quire 20.")
    
    # 1. End words
    last_counts = analyze_end_verbs(paragraphs)
    print("\n--- End Words ---")
    print(f"qokeey: {last_counts['qokeey']}")
    print(f"qokeol: {last_counts['qokeol']}")
    print(f"okeol: {last_counts['okeol']}")
    print(f"okam: {last_counts['okam']}")
    print(f"chedy: {last_counts['chedy']}")

    # 2. Total counts in Quire 20
    all_words = [w for p in paragraphs for w in p]
    total_counts = collections.Counter(all_words)
    print("\n--- Total Counts in Quire 20 ---")
    print(f"qokeey: {total_counts['qokeey']}")
    print(f"qokeol: {total_counts['qokeol']}")
    print(f"okeol: {total_counts['okeol']}")
    
    # 3. Proximity
    print("\n--- Proximity to 'daiin' (within 5 words) ---")
    for word in ['qokeey', 'qokeol', 'okeol', 'okam']:
        count, dists = analyze_proximity(paragraphs, word, 'daiin', window=5)
        print(f"{word} near 'daiin': {count} times. Distances: {dists}")

    # 4. Check what 'qokeey' usually follows
    print("\n--- Words preceding 'qokeey' ---")
    preceding = []
    for p in paragraphs:
        for i, w in enumerate(p):
            if w == 'qokeey' and i > 0:
                preceding.append(p[i-1])
    print(collections.Counter(preceding).most_common(5))

if __name__ == "__main__":
    main()
