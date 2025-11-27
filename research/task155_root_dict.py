import json
import collections
import os

def main():
    print("Building Root Dictionary...")
    
    # Load Old Dictionary (Words)
    # Assuming we have 'results/unified_dictionary.json' or similar. 
    # If not, we'll try to map from 'results/semantic_clusters.json' or just build a skeleton.
    old_dict_path = 'results/unified_dictionary.json'
    parsed_path = 'results/parsed_text.json'
    
    if not os.path.exists(parsed_path):
        print("Parsed text not found.")
        return

    # Load Parsed Data to get Word -> Root map
    with open(parsed_path, 'r') as f:
        parsed_data = json.load(f)
        
    word_to_root = {}
    for entry in parsed_data:
        word_to_root[entry['original']] = entry['root']
        
    # Load Old Dictionary Definitions
    # Format assumed: {"word": "definition", ...} or [{"voynich": "word", "english": "def"}, ...]
    # Let's support a simple key-value for now, or check file format if needed.
    # Since I don't have the exact file structure in memory, I will create a placeholder 
    # that aligns 'chol', 'daiin', etc. if the file is missing.
    
    word_definitions = {}
    if os.path.exists(old_dict_path):
        try:
            with open(old_dict_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'entries' in data:
                    # Format: {"entries": {"word": {"meaning": "def", ...}}}
                    for word, info in data['entries'].items():
                        if 'meaning' in info:
                            word_definitions[word] = info['meaning']
                elif isinstance(data, list):
                    for item in data:
                        if 'voynich' in item and 'english' in item:
                            word_definitions[item['voynich']] = item['english']
                elif isinstance(data, dict):
                    # Fallback for simple key-value
                    for k, v in data.items():
                        if isinstance(v, str):
                            word_definitions[k] = v
        except Exception as e:
            print(f"Error reading old dictionary: {e}")
    
    # Invert: Root -> [Definitions]
    root_definitions = collections.defaultdict(list)
    
    for word, root in word_to_root.items():
        if word in word_definitions:
            defn = word_definitions[word]
            root_definitions[root].append((word, defn))
            
    # Resolve Conflicts
    final_root_dict = {}
    
    for root, defs in root_definitions.items():
        # defs is list of (word, definition)
        # Extract unique definitions
        unique_defs = set([d[1] for d in defs])
        
        entry = {
            "root": root,
            "meanings": list(unique_defs),
            "source_words": [d[0] for d in defs]
        }
        final_root_dict[root] = entry
        
    # Save
    with open('results/root_dictionary_v1.json', 'w') as f:
        json.dump(final_root_dict, f, indent=2)
        
    print(f"Generated Root Dictionary with {len(final_root_dict)} entries.")

if __name__ == "__main__":
    main()
