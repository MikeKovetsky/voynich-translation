import json
import re
import os

# Configuration
TRANSCRIPTION_FILE = "voynich_raw.txt"
DICTIONARY_FILE = "results/dictionary/dictionary_v13.json"
SAFE_MERGES_FILE = "results/safe_merges.json"
SUFFIX_MINING_FILE = "results/suffix_mining.json"
GRAMMAR_FILE = "config/recipe_grammar.json"
OUTPUT_FILE = "results/quire20_translation_final.md"

TARGET_PAGES_START = "f103r"
TARGET_PAGES_END = "f116v"

def parse_page_line(line_tag):
    # Format <f103r.1> or <1r.1>
    match = re.search(r'<([\w\d]+)\.(\d+)>', line_tag)
    if match:
        return match.group(1), match.group(2)
    return None, None

def is_in_range(page, start, end):
    def parse_page_id(pid):
        m = re.match(r'f?(\d+)([rv]\d*)', pid)
        if m:
            return int(m.group(1)), m.group(2)
        return 0, ""

    p_num, p_suff = parse_page_id(page)
    s_num, s_suff = parse_page_id(start)
    e_num, e_suff = parse_page_id(end)

    if p_num < s_num or p_num > e_num:
        return False
    return True 

def load_json(path):
    if not os.path.exists(path):
        print(f"Warning: {path} not found.")
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def main():
    print("Starting translation run...")
    
    # Load data
    dictionary_data = load_json(DICTIONARY_FILE)
    dictionary = dictionary_data.get("entries", {})
    safe_merges = load_json(SAFE_MERGES_FILE)
    suffix_mining_list = load_json(SUFFIX_MINING_FILE)
    grammar = load_json(GRAMMAR_FILE)
    
    # Convert suffix_mining list to dict for lookup
    suffix_mining = {}
    if isinstance(suffix_mining_list, list):
        for item in suffix_mining_list:
            if "word" in item and "meaning" in item:
                suffix_mining[item["word"]] = item["meaning"]
    
    print(f"Loaded dictionary with {len(dictionary)} entries.")
    print(f"Loaded suffix mining with {len(suffix_mining)} entries.")
    
    grammar_suffixes = grammar.get("morphology_rules", {}).get("suffixes", {}).keys()
    grammar_prefixes = grammar.get("morphology_rules", {}).get("prefixes", {}).keys()
    token_roles = grammar.get("token_roles", {})

    # Read transcription
    lines = []
    if os.path.exists(TRANSCRIPTION_FILE):
        with open(TRANSCRIPTION_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                match = re.match(r'(<[^>]+>)(.*)', line)
                if match:
                    tag, text = match.groups()
                    page, line_num = parse_page_line(tag)
                    if page and is_in_range(page, TARGET_PAGES_START, TARGET_PAGES_END):
                        lines.append({'page': page, 'line': line_num, 'text': text})
    else:
        print(f"Error: Transcription file {TRANSCRIPTION_FILE} not found.")
        return

    print(f"Found {len(lines)} lines in target range.")

    # Process lines
    current_page = None
    output_lines = []
    
    for item in lines:
        page = item['page']
        text = item['text']
        
        if page != current_page:
            output_lines.append(f"\n## Page {page}\n")
            current_page = page
        
        clean_text = re.sub(r'[\.,\-=]', ' ', text)
        tokens = [t for t in clean_text.split() if t]
        
        translated_tokens = []
        sentence_confidence = []

        for i, token in enumerate(tokens):
            processed_token = token
            
            # Safe Merges
            has_grammar_suffix = any(token.endswith(s.replace("-", "")) for s in grammar_suffixes if s.startswith("-"))
            
            if token in safe_merges and not has_grammar_suffix:
                processed_token = safe_merges[token]
            
            # Translation Lookup
            word_data = dictionary.get(processed_token)
            meaning = None
            confidence = 0.0
            
            if word_data:
                meaning = word_data.get("meaning")
                confidence = word_data.get("confidence", 0.0)
            
            # If unknown, check suffix mining
            if not meaning:
                if processed_token in suffix_mining:
                    meaning = suffix_mining[processed_token]
                    confidence = 0.3
            
            # If still unknown, keep original
            if not meaning:
                translated_token = f"`{processed_token}`" 
                confidence = 0.0
            else:
                translated_token = meaning

            # Grammar / Syntax Assembly
            # Token roles
            if processed_token in token_roles:
                role = token_roles[processed_token]
                # Simplified mapping
                if "The/Of/With" in role: translated_token = "the" # Generic article/prep
                elif "Verbalizer" in role: translated_token = "process"
                elif "Sentence Starter" in role: translated_token = "" # often omitted
                elif "Verb (Take/Gather)" in role: translated_token = "take"
                
                # If meaning was found in dictionary, prefer dictionary? 
                # Or does grammar override? Usually specific > general.
                # If dictionary has specific meaning for 'ol' (e.g. 'The'), use it.
                # If not, use grammar role.
                if not meaning: # Only apply generic role if no specific meaning
                     confidence = 0.8 # Grammar role confidence
                
            translated_tokens.append(translated_token)
            sentence_confidence.append(confidence)

        # Syntactic Assembly - Post-Token
        final_sentence_tokens = []
        for t in translated_tokens:
            if t: # skip empty
                final_sentence_tokens.append(t)
        
        sentence_str = " ".join(final_sentence_tokens)
        
        if sentence_str:
            sentence_str = sentence_str[0].upper() + sentence_str[1:]
            
        avg_conf = sum(sentence_confidence) / len(sentence_confidence) if sentence_confidence else 0.0
        
        output_lines.append(f"- {sentence_str} (Conf: {avg_conf:.2f})")

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Quire 20 Translation (Recipe Section)\n")
        f.write(f"**Source:** {TARGET_PAGES_START} - {TARGET_PAGES_END}\n")
        f.write("\n".join(output_lines))
    
    print(f"Translation written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
