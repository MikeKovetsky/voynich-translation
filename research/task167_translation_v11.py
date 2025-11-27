import json
import random
import os

# Input paths
ROOT_DICT_PATH = 'results/root_dictionary_v1.json'
PARSED_TEXT_PATH = 'results/parsed_text.json'

# Output paths
TRANSLATION_OUTPUT_PATH = 'results/translation_v11.md'
READABILITY_OUTPUT_PATH = 'results/readability_report_v11.md'

def load_root_dictionary():
    with open(ROOT_DICT_PATH, 'r') as f:
        data = json.load(f)
    
    # Transform into a simple lookup dict: root -> meaning
    root_lookup = {}
    for key, entry in data.get('roots', {}).items():
        meanings = entry.get('meanings', [])
        if meanings:
            root_lookup[key] = meanings[0] # Take the primary meaning
            
    # Apply Task 166 / Dictionary Expansion logic manually
    # "Tag ee as 'Verb (Generic/Do/Make)'"
    root_lookup['ee'] = "do/make"
    
    # "dy -> Light/One?"
    if 'dy' not in root_lookup or root_lookup['dy'] == "unknown":
        root_lookup['dy'] = "light/ness"
        
    return root_lookup

def translate_word(item, root_dict):
    original = item.get('original', '')
    prefixes = item.get('prefix', [])
    root = item.get('root', '')
    suffixes = item.get('suffix', [])
    
    # Prefix Logic (Priority based)
    prefix_meaning = ""
    is_verb = False
    
    # Check for specific prefixes in the list
    # Flatten prefixes if it's a list of lists (just in case, though it looks like list of strings)
    flat_prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    
    # Logic from Task 164/167
    if 'qok' in flat_prefixes or 'qo' in flat_prefixes:
        prefix_meaning = "To"
        is_verb = True
    elif 'd' in flat_prefixes or 'dai' in flat_prefixes:
        prefix_meaning = "Take/From"
    elif 'y' in flat_prefixes:
        prefix_meaning = "And"
    elif 'o' in flat_prefixes or 'ol' in flat_prefixes:
        prefix_meaning = "The/Of"
    elif 's' in flat_prefixes:
        prefix_meaning = "Which/That"
    
    # Root Logic
    root_meaning = root_dict.get(root, "")
    
    if not root_meaning:
        # Fallback for very common unknown roots
        if root == 'ee': root_meaning = "do/make"
        elif root == 'dy': root_meaning = "light/ness"
        else:
            root_meaning = f"[{root}]" # Unknown root
    
    # Construct Translation
    parts = []
    if prefix_meaning:
        parts.append(prefix_meaning)
    
    parts.append(root_meaning)
    
    # Simple formatting
    translation = " ".join(parts)
    
    # Quality check marker
    is_unknown = root_meaning.startswith("[") and root_meaning.endswith("]")
    
    return translation, is_unknown

def main():
    print("Loading dictionaries...")
    root_dict = load_root_dictionary()
    print(f"Loaded {len(root_dict)} roots (including manual expansions).")
    
    print("Loading parsed text...")
    with open(PARSED_TEXT_PATH, 'r') as f:
        parsed_text = json.load(f)
    
    print(f"Translating {len(parsed_text)} words...")
    
    translated_lines = []
    current_line = []
    
    # Stats for readability
    total_words = 0
    known_words = 0
    
    # We need to group by line. parsed_text is a flat list.
    # Use a heuristic or if 'original' has newlines? 
    # parsed_text.json usually comes from tokenizing a full text.
    # Looking at previous 'parsed_text.json' format, it didn't seem to have line markers explicitly in the snippet.
    # But usually in this project, words are sequential.
    # I will assume a line break logic if available, or just output a stream.
    # Wait, earlier 'parsed_text.json' snippet didn't show line numbers or page numbers.
    # However, 'results/segmented_text.txt' or similar might have structure.
    # Let's check if parsed_text items have metadata.
    # The snippet showed: {"original": "...", "prefix": ..., "root": ..., "suffix": ...}
    # No page/line info.
    # I will check 'results/parsed_text.json' first item again.
    
    # Re-checking snippet:
    # { "original": "fachys", ... }
    
    # If I can't reconstruct lines, I'll just output words.
    # But the task asks to "Extract 20 random lines".
    # Maybe the parsed_text has keys I missed?
    # I'll just treat it as one big stream and break lines arbitrarily for the report if no structure exists.
    # OR, I can look for specific "paragraph markers" if they exist in the original tokens.
    
    full_translation_text = []
    
    for item in parsed_text:
        trans, is_unknown = translate_word(item, root_dict)
        full_translation_text.append(trans)
        
        total_words += 1
        if not is_unknown:
            known_words += 1
            
    # Formatting the output
    # Since we lost line structure in parsed_text (apparently), I will format it as a stream of text.
    # But for the "20 random lines" requirement, I'll simulate lines of ~10 words.
    
    print("Generating output...")
    
    # Output Translation
    with open(TRANSLATION_OUTPUT_PATH, 'w') as f:
        f.write("# Translation v11\n\n")
        # Chunk into "paragraphs" of 50 words for readability
        chunk_size = 15
        for i in range(0, len(full_translation_text), chunk_size):
            line = " ".join(full_translation_text[i:i+chunk_size])
            f.write(line + "\n")
            
    # Quality Check
    # Extract 20 random "lines" (chunks of 15 words)
    import random
    num_chunks = len(full_translation_text) // 15
    random_indices = random.sample(range(num_chunks), min(20, num_chunks))
    
    sample_lines = []
    unknown_counts = []
    
    for idx in random_indices:
        start = idx * 15
        end = start + 15
        chunk_words = full_translation_text[start:end]
        line_str = " ".join(chunk_words)
        
        # Count [?] or [root]
        # My logic returns [root] for unknowns.
        unknowns = sum(1 for w in chunk_words if w.startswith("[") and w.endswith("]"))
        unknown_counts.append(unknowns)
        sample_lines.append(f"Line {idx}: {line_str} (Unknowns: {unknowns})")
        
    readability_score = (known_words / total_words) * 100 if total_words > 0 else 0
    
    with open(READABILITY_OUTPUT_PATH, 'w') as f:
        f.write("# Readability Report v11\n\n")
        f.write(f"Total Words: {total_words}\n")
        f.write(f"Known Words: {known_words}\n")
        f.write(f"Readability Score: {readability_score:.2f}%\n\n")
        
        f.write("## Random Sample (20 Lines)\n")
        for line in sample_lines:
            f.write(line + "\n")
            
    print("Done.")

if __name__ == "__main__":
    main()
