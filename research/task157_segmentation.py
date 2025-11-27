import json
import collections
import os
import re

def load_text(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def load_roots(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # Extract roots from the dict structure or list
    # Assuming root_dictionary_v1.json format: {"root": {...}, ...}
    if isinstance(data, dict) and 'roots' in data:
        return set(data['roots'].keys())
    elif isinstance(data, dict):
        return set(data.keys())
    return set()

def split_line(line, valid_roots):
    # Heuristic: Break by known roots
    # This is tricky without prefixes. We need the parsed structure.
    # Actually, better to use the parsed_text.json from Task 156 if available?
    # But Task 157 says "Apply it to every line of the raw text".
    
    # Let's re-implement the greedy splitter but include prefixes this time.
    # We'll assume words in raw text are space-separated, but some are "compounds".
    
    # Simplified approach: Just join the output of parsed_text_v2.json
    # That file already has "original" -> "roots" mapping.
    # We just need to reconstruct the text flow.
    return line # Placeholder if we use the JSON map approach

def main():
    print("Starting Full Text Segmentation...")
    
    parsed_json_path = 'results/parsed_text_v2.json'
    raw_text_path = 'data/eva_ivtff.txt'
    
    if not os.path.exists(parsed_json_path):
        print("Parsed text v2 not found. Run Task 156 first.")
        return

    with open(parsed_json_path, 'r') as f:
        parsed_data = json.load(f)
        
    # Create a map: original_word -> segmented_string
    # e.g. "qokaiinchol" -> "qok-aiin chol"
    
    word_map = {}
    new_word_count = 0
    total_len_reduction = 0
    
    for entry in parsed_data:
        original = entry['original']
        prefixes = entry.get('prefix', [])
        roots = entry.get('roots', []) # From Task 156 split
        suffixes = entry.get('suffix', [])
        
        # Reconstruct
        # Attach prefixes to the FIRST root
        # Attach suffixes to the LAST root
        # Separate roots with spaces
        
        if not roots:
            # Fallback for empty roots (shouldn't happen often)
            roots = [entry.get('root', '')]
            
        segments = []
        
        # 1. First Segment: Prefixes + Root 1
        first = "".join(prefixes) + roots[0]
        segments.append(first)
        
        # 2. Middle Segments: Roots
        for r in roots[1:-1]:
            segments.append(r)
            
        # 3. Last Segment: Root N + Suffixes (if >1 root)
        if len(roots) > 1:
            last = roots[-1] + "".join(suffixes)
            segments.append(last)
        else:
            # If only 1 root, append suffixes to the first segment
            segments[0] += "".join(suffixes)
            
        segmented_str = " ".join(segments)
        word_map[original] = segmented_str
        
        if len(segments) > 1:
            new_word_count += (len(segments) - 1)
            
    # Now process the raw text line by line to preserve structure
    lines = load_text(raw_text_path)
    output_lines = []
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            output_lines.append(line)
            continue
            
        # Split into tokens, replace, join
        # Handle line tags <...>
        tokens = line.split()
        new_tokens = []
        for t in tokens:
            # Remove punctuation for lookup
            clean_t = re.sub(r'[^a-zA-Z0-9]', '', t)
            if clean_t in word_map:
                # Apply the split
                # We simply replace the token with the segmented version
                new_tokens.append(word_map[clean_t])
            else:
                new_tokens.append(t)
                
        output_lines.append(" ".join(new_tokens))
        
    # Output
    with open('results/segmented_text.txt', 'w') as f:
        f.write("\n".join(output_lines))
        
    # Stats
    with open('results/segmentation_stats.md', 'w') as f:
        f.write(f"# Segmentation Stats\n")
        f.write(f"- New words created: {new_word_count}\n")
        # Calculate avg length?
        
    print(f"Segmentation complete. {new_word_count} new breaks inserted.")

if __name__ == "__main__":
    main()
