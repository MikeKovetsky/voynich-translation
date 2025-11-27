import json
import re
import os

def load_dictionary(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Warning: Dictionary not found at {path}. Proceeding with empty dictionary.")
        return {}

def is_unknown(word, dictionary):
    # Filter out obviously non-word tokens if any (like '-')
    if not word or not word.isalpha(): # simple check, EVA is alpha
        return False
        
    if word not in dictionary:
        return True
        
    entry = dictionary[word]
    meaning = entry.get('meaning', '')
    
    # If meaning is explicitly generic/unknown, treat as unknown
    if not meaning or meaning.lower() in ["unknown", "untranslated", "uncertain"]:
        return True
        
    # If it has a real meaning, it's known, so return False
    return False

def parse_ivtff(path):
    lines = []
    # Target folios ranges: 75-84, 103-116
    # Folio numbers are integers. Sides 'r' or 'v' don't affect the number check.
    
    valid_ranges = [(75, 84), (103, 116)]
    
    try:
        with open(path, 'r') as f:
            for line in f:
                if line.startswith('<f'):
                    # Extract folio ID: <f75r...
                    match = re.match(r'<f(\d+)([rv])', line)
                    if match:
                        num = int(match.group(1))
                        side = match.group(2)
                        
                        # Check if in range
                        is_valid = False
                        for start, end in valid_ranges:
                            if start <= num <= end:
                                is_valid = True
                                break
                        
                        if is_valid:
                            # Extract text content
                            # IVTFF format: <f75r.P.1;H> text...
                            parts = line.split('>', 1)
                            if len(parts) > 1:
                                text = parts[1].strip()
                                # Replace dots with spaces as they are often separators in IVTFF
                                clean_text = text.replace('.', ' ')
                                # Remove comments {- ... -} or similar if present
                                # Simple regex to remove {- ... -}
                                clean_text = re.sub(r'\{-.*?-\}', '', clean_text)
                                # Split into words
                                words = clean_text.split()
                                
                                lines.append({
                                    'folio': f"{num}{side}",
                                    'words': words,
                                    'original_line': line.strip()
                                })
    except FileNotFoundError:
        print(f"Error: Input file not found at {path}")
        return []
    return lines

def scan_for_patterns(lines, dictionary):
    candidates = []
    # Patterns:
    # ol [UNKNOWN]
    # daiin [UNKNOWN]
    # [UNKNOWN] chedy
    
    trigger_before = {'ol', 'daiin'}
    trigger_after = {'chedy'}
    
    for entry in lines:
        words = entry['words']
        folio = entry['folio']
        
        for i, word in enumerate(words):
            # Check "ol [word]" and "daiin [word]"
            if word in trigger_before:
                if i + 1 < len(words):
                    candidate = words[i+1]
                    # Remove trailing punctuation/chars if any
                    candidate = candidate.strip(',.-;') 
                    
                    if is_unknown(candidate, dictionary):
                         candidates.append({
                             'candidate': candidate,
                             'pattern': f"{word} [UNKNOWN]",
                             'trigger': word,
                             'context': ' '.join(words[max(0, i-2):min(len(words), i+4)]),
                             'folio': folio
                         })
            
            # Check "[word] chedy"
            if word in trigger_after:
                if i - 1 >= 0:
                    candidate = words[i-1]
                    candidate = candidate.strip(',.-;')
                    
                    if is_unknown(candidate, dictionary):
                        candidates.append({
                             'candidate': candidate,
                             'pattern': f"[UNKNOWN] {word}",
                             'trigger': word,
                             'context': ' '.join(words[max(0, i-3):min(len(words), i+3)]),
                             'folio': folio
                         })
    return candidates

def main():
    input_file = 'data/eva_ivtff.txt'
    dict_file = 'results/dictionary/dictionary.json'
    output_file = 'results/mining/ingredient_candidates.json'
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"Loading dictionary from {dict_file}...")
    dictionary = load_dictionary(dict_file)
    
    print(f"Parsing text from {input_file}...")
    lines = parse_ivtff(input_file)
    print(f"Parsed {len(lines)} lines from target folios.")
    
    print("Scanning for patterns...")
    candidates = scan_for_patterns(lines, dictionary)
    
    print(f"Found {len(candidates)} candidate occurrences.")
    
    # Group by candidate
    grouped = {}
    for c in candidates:
        word = c['candidate']
        if not word: continue
        
        if word not in grouped:
            grouped[word] = {
                'word': word,
                'count': 0,
                'patterns': set(),
                'folios': set(),
                'examples': []
            }
        grouped[word]['count'] += 1
        grouped[word]['patterns'].add(c['pattern'])
        grouped[word]['folios'].add(c['folio'])
        if len(grouped[word]['examples']) < 5: # Keep up to 5 examples
            grouped[word]['examples'].append(f"{c['folio']}: ...{c['context']}...")
    
    # Convert sets to lists
    output_list = []
    for word, data in grouped.items():
        data['patterns'] = list(data['patterns'])
        data['folios'] = sorted(list(data['folios']))
        output_list.append(data)
    
    # Sort by count descending
    output_list.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"Identified {len(output_list)} unique ingredient candidates.")
    
    with open(output_file, 'w') as f:
        json.dump(output_list, f, indent=2)
    
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    main()
