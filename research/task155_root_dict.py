
import json
import os
from collections import defaultdict

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # Paths
    unified_dict_path = 'results/unified_dictionary.json'
    root_mapping_path = 'results/root_mapping.json'
    output_path = 'results/root_dictionary_v1.json'

    # Load data
    if not os.path.exists(unified_dict_path):
        print(f"Error: {unified_dict_path} not found.")
        return
    if not os.path.exists(root_mapping_path):
        print(f"Error: {root_mapping_path} not found.")
        return

    unified_dict = load_json(unified_dict_path)
    root_mapping = load_json(root_mapping_path)

    # Extract entries from unified dict
    # Structure: {"entries": {"word": {"meaning": "...", ...}}}
    entries = unified_dict.get('entries', {})
    
    # Identify all known roots from the mapping values
    known_roots = set(root_mapping.values())
    
    # Build Root Dictionary
    roots_data = defaultdict(lambda: {'meanings': set(), 'source_words': set(), 'entries': []})
    
    mapped_count = 0
    unmapped_count = 0
    
    for word, entry in entries.items():
        # The word key in entries is the voynich word
        # root_mapping keys might be voynich words too.
        
        # Check if word is in root_mapping
        root = root_mapping.get(word)
        
        if not root:
            # Try cleaning the word (trim whitespace, etc just in case)
            root = root_mapping.get(word.strip())
            
        if not root:
            # Check if the word itself is a known root (appear as value in mapping)
            # This helps if the root word itself is in the dictionary but not explicitly mapped to itself in root_mapping
            if word in known_roots:
                root = word
        
        if not root:
            # If not found, maybe the word itself is the root?
            # But we only trust the mapping or known roots.
            unmapped_count += 1
            continue
            
        mapped_count += 1
        meaning = entry.get('meaning')
        
        if meaning:
            # Normalize meaning (optional: lowercase)
            # meaning_norm = meaning.lower()
            meaning_norm = meaning # Keep original case for now
            
            roots_data[root]['meanings'].add(meaning_norm)
            roots_data[root]['source_words'].add(word)
            roots_data[root]['entries'].append({
                'word': word,
                'meaning': meaning,
                'source': entry.get('source', 'unknown'),
                'confidence': entry.get('confidence', 0)
            })

    # Format output
    final_roots = {}
    conflicts = []
    
    for root, data in roots_data.items():
        meanings_list = sorted(list(data['meanings']))
        source_words_list = sorted(list(data['source_words']))
        
        root_entry = {
            "root": root,
            "meanings": meanings_list,
            "source_words": source_words_list,
            # "details": data['entries'] # Optional: include details if needed, but task didn't explicitly ask for it in the compact format
        }
        
        # Conflict detection
        # If > 1 meaning, it's a potential conflict
        if len(meanings_list) > 1:
            # Check if meanings are similar (simple check)
            # E.g. "mix" vs "mixture"
            # We won't do complex NLP here, just flag them.
            root_entry['conflict_suspected'] = True
            conflicts.append({
                'root': root,
                'meanings': meanings_list,
                'words': source_words_list
            })
        else:
            root_entry['conflict_suspected'] = False
            
        final_roots[root] = root_entry

    # Construct final JSON structure
    output_data = {
        "version": "1.0",
        "description": "Root dictionary generated from unified_dictionary.json and root_mapping.json",
        "stats": {
            "total_roots": len(final_roots),
            "mapped_words": mapped_count,
            "unmapped_words": unmapped_count,
            "conflicts_detected": len(conflicts)
        },
        "roots": final_roots,
        "conflicts": conflicts 
    }
    
    save_json(output_path, output_data)
    
    print(f"Generated {output_path}")
    print(f"Total Roots: {len(final_roots)}")
    print(f"Mapped Words: {mapped_count}")
    print(f"Unmapped Words: {unmapped_count}")
    print(f"Conflicts Detected: {len(conflicts)}")
    if conflicts:
        print("Top 5 Conflicts:")
        for c in conflicts[:5]:
            print(f"  Root: {c['root']}, Meanings: {c['meanings']}")

if __name__ == '__main__':
    main()
