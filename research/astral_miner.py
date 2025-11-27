import re
import json
import os
from collections import defaultdict

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return set(data.get('entries', {}).keys())

def parse_ivtff(path):
    lines = []
    # Pages f67 to f73
    target_prefixes = [f"f{i}" for i in range(67, 74)]
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('<'):
                continue
            
            # Extract tag and content
            # Format: <tag> content
            match = re.match(r'<([^>]+)>\s*(.*)', line)
            if not match:
                continue
            
            tag_content = match.group(1)
            text_content = match.group(2)
            
            # Parse tag: page.line;source
            # Example: f11r.1,@P0;H
            parts = tag_content.split(';')
            
            location_part = parts[0] # f11r.1,@P0
            source_part = parts[-1] if len(parts) > 1 else ""
            
            # Filter by source 'H' (Takahashi)
            if 'H' not in source_part:
                continue

            # Filter by page
            # location_part starts with page
            page_match = re.match(r'(f\d+[rv])', location_part)
            if not page_match:
                continue
            page = page_match.group(1)
            
            is_target = False
            for prefix in target_prefixes:
                if page.startswith(prefix):
                    is_target = True
                    break
            
            if not is_target:
                continue
                
            # Process text
            # Remove inline comments {comment} if any? 
            # EVA usually uses raw chars.
            # Split by dot
            words = text_content.split('.')
            # Clean words (remove empty)
            words = [w.strip() for w in words if w.strip()]
            
            lines.append({
                'page': page,
                'line_id': location_part,
                'words': words
            })
                
    return lines

def clean_eva_word(w):
    # Remove <...> tags
    w = re.sub(r'<[^>]+>', '', w)
    # Remove non-az characters (EVA specific)
    w = re.sub(r'[^a-z]', '', w)
    return w

def miner():
    data_path = 'data/eva_ivtff.txt'
    dict_path = 'results/dictionary/dictionary.json'
    output_path = 'results/mining/astral_candidates.json'
    
    print(f"Loading dictionary from {dict_path}...")
    if os.path.exists(dict_path):
        known_words = load_dictionary(dict_path)
    else:
        print(f"Warning: Dictionary not found at {dict_path}. Using empty set.")
        known_words = set()
        
    print(f"Loaded {len(known_words)} known words.")
    
    print(f"Parsing {data_path}...")
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    lines = parse_ivtff(data_path)
    print(f"Parsed {len(lines)} lines from target pages (f67-f73).")
    
    patterns = ['daiin', 'aiin', 'dal']
    
    candidates = defaultdict(lambda: {
        'word': '',
        'patterns': set(),
        'locations': [],
        'count': 0
    })
    
    for entry in lines:
        words = entry['words']
        line_id = entry['line_id']
        
        for i in range(len(words) - 1):
            curr_word_raw = words[i]
            curr_word = clean_eva_word(curr_word_raw)
            
            next_word_raw = words[i+1]
            next_word = clean_eva_word(next_word_raw)
            
            if not curr_word or not next_word:
                continue

            if curr_word in patterns:
                # Check if known
                if next_word in known_words:
                    continue
                
                # Basic filtering: 
                if len(next_word) < 2: 
                    continue
                
                cand = candidates[next_word]
                cand['word'] = next_word
                cand['patterns'].add(curr_word)
                cand['locations'].append(f"{line_id}")
                cand['count'] += 1
    
    # Convert to list
    result_list = []
    for word, data in candidates.items():
        data['patterns'] = list(data['patterns'])
        result_list.append(data)
        
    # Sort by count desc
    result_list.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"Found {len(result_list)} candidates.")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result_list, f, indent=2)
        
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    miner()
