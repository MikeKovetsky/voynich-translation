import json
import os
import re
from collections import Counter

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_corpus(path):
    with open(path, 'r') as f:
        return f.read()

def main():
    # Paths
    dict_path = 'results/dictionary/dictionary_v11.json'
    corpus_path = 'data/eva_ivtff.txt'
    output_dict_path = 'results/dictionary/dictionary_update_v11_1.json'
    report_path = 'results/track-248-refinement_report.md'
    
    # Load Data
    print(f"Loading dictionary from {dict_path}...")
    dictionary = load_json(dict_path)
    
    print(f"Loading corpus from {corpus_path}...")
    corpus_text = load_corpus(corpus_path)
    
    # Preprocess corpus into words
    # IVTFF format: <location> TAB text
    # text uses '.' as separator. Tags <...> should be removed.
    
    clean_words = []
    for line in corpus_text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        
        parts = line.split('\t', 1)
        if len(parts) < 2:
            continue
            
        text = parts[1]
        # Remove tags
        text = re.sub(r'<[^>]+>', '', text)
        # Replace dots and commas with spaces
        text = text.replace('.', ' ').replace(',', ' ')
        
        # Add to words
        clean_words.extend(text.split())
        
    words = clean_words
    
    # Adjective Map (Hardcoded based on Task 247 description)
    adj_map = {
        "or": "Red/Hot",
        "ol": "Liquid/Wet",
        "ok": "Green/Leafy",
        "dal": "Principal/First",
        "chedy": "Mixed"
    }
    
    # Identify Candidates
    plant_candidates = []
    star_candidates = []
    
    if 'entries' in dictionary:
        entries_dict = dictionary['entries']
    else:
        # Fallback if structure is flat list
        entries_dict = {item['voynich']: item for item in dictionary}

    for word, entry in entries_dict.items():
        meaning = entry.get('meaning', '')
        if 'plant_candidate' in meaning:
            plant_candidates.append(word)
        if 'star_candidate' in meaning:
            star_candidates.append(word)
            
    print(f"Found {len(plant_candidates)} plant candidates and {len(star_candidates)} star candidates.")
    
    candidates = set(plant_candidates + star_candidates)
    
    # Scan for Bigrams: Candidate + Adjective
    pair_counts = Counter()
    candidate_counts = Counter()
    
    print(f"Total words in corpus: {len(words)}")
    print(f"Sample words: {words[:10]}")
    
    print("Scanning corpus for bigrams...")
    for i in range(len(words) - 1):
        w1 = words[i]
        w2 = words[i+1]
        
        if w1 in candidates:
            candidate_counts[w1] += 1
            if w2 in adj_map:
                pair_counts[(w1, w2)] += 1
                # print(f"Found Pair: {w1} + {w2}")

    print(f"Total candidate occurrences: {sum(candidate_counts.values())}")
    print(f"Total pairs found: {sum(pair_counts.values())}")
    
    # Analyze and Update
    updated_entries = []
    report_lines = []
    report_lines.append("# Track 248: Candidate Refinement Report")
    report_lines.append("\n## Updates")
    report_lines.append("| Word | Type | Top Adjective | New Meaning | Confidence Bump |")
    report_lines.append("|---|---|---|---|---|")
    
    updates_count = 0
    
    for word, entry in entries_dict.items():
        if word not in candidates:
            continue
            
        if candidate_counts[word] < 5: # Skip rare words
            continue
            
        top_adj = None
        top_count = 0
        total_adj_matches = 0
        
        for adj in adj_map:
            count = pair_counts[(word, adj)]
            if count > 0:
                total_adj_matches += count
                if count > top_count:
                    top_count = count
                    top_adj = adj
        
        if top_adj and top_count >= 2:
            meaning = entry.get('meaning', '')
            if 'plant_candidate' in meaning:
                base_type = 'plant_candidate'
            else:
                base_type = 'star_candidate'
            
            adj_meaning = adj_map[top_adj]
            new_meaning = f"{base_type} ({adj_meaning})"
            
            old_confidence = entry.get('confidence', 0.5)
            new_confidence = min(1.0, old_confidence + 0.1)
            
            if adj_meaning not in meaning:
                if '(' in meaning and 'morphological' in meaning:
                     morph_part = meaning[meaning.find('('):]
                     final_meaning = f"{base_type} ({adj_meaning}) {morph_part}"
                else:
                     final_meaning = new_meaning
                
                entry['meaning'] = final_meaning
                entry['confidence'] = new_confidence
                
                updated_entries.append(entry)
                updates_count += 1
                
                report_lines.append(f"| {word} | {base_type} | {top_adj} ({top_count}) | {final_meaning} | {old_confidence} -> {new_confidence} |")

    print(f"Updated {updates_count} entries.")
    
    print(f"Saving updated dictionary to {output_dict_path}...")
    save_json(dictionary, output_dict_path)
    
    print(f"Saving report to {report_path}...")
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))

if __name__ == "__main__":
    main()
