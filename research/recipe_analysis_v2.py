import json
import re
import collections
from pathlib import Path

# Configuration
INPUT_FILE = 'data/eva_ivtff.txt'
DICT_FILE = 'results/master_dictionary_v7.json'
OUTPUT_JSON = 'results/recipe_ingredients.json'
OUTPUT_MD = 'results/recipe_structure_report.md'

TARGET_WORD = 'daiin'
TARGET_VARIANTS = ['daiin', 'dai!n', 'dain', 'da?in'] 

def is_quire_20(page_str):
    if not page_str: return False
    num_part = re.findall(r'\d+', page_str)
    if not num_part: return False
    val = int(num_part[0])
    return 103 <= val <= 116

def load_text(path):
    print(f"Loading text from {path}...")
    raw_lines = []
    current_page = ""
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            page_match = re.match(r'^<f(\d+[rv])>', line)
            if page_match:
                current_page = 'f' + page_match.group(1)
                
            if '\t' in line and line.startswith('<f'):
                parts = line.split('\t', 1)
                meta = parts[0]
                text = parts[1].strip()
                
                meta_page_match = re.search(r'<(f\d+[rv])\.', meta)
                if meta_page_match:
                    page_in_meta = meta_page_match.group(1)
                    if is_quire_20(page_in_meta):
                        source_match = re.search(r';([a-zA-Z0-9])>', meta)
                        source = source_match.group(1) if source_match else '?'
                        
                        raw_lines.append({
                            'page': page_in_meta,
                            'meta': meta,
                            'source': source,
                            'text': text
                        })
    return raw_lines

def consolidate_lines(raw_lines):
    lines_map = {}
    
    def score_source(s):
        if s == 'H': return 10
        if s == 'U': return 5
        if s == 'F': return 4
        return 1
        
    for item in raw_lines:
        match = re.search(r'<(f\d+[rv]\.\d+)', item['meta'])
        if not match: continue
        line_id = match.group(1)
        
        if line_id not in lines_map:
            lines_map[line_id] = item
        else:
            curr = lines_map[line_id]
            if score_source(item['source']) > score_source(curr['source']):
                lines_map[line_id] = item
                
    def sort_key(k):
        m = re.match(r'f(\d+)([rv])\.(\d+)', k)
        if m:
            return (int(m.group(1)), m.group(2), int(m.group(3)))
        return (0, '', 0)
        
    sorted_keys = sorted(lines_map.keys(), key=sort_key)
    return [lines_map[k] for k in sorted_keys]

def analyze_recipes(lines):
    print("Analyzing recipes...")
    
    ingredients = collections.Counter()
    phrases = []
    end_verbs = collections.Counter()
    
    all_tokens = []
    
    # Build a stream of tokens including paragraph breaks
    for line in lines:
        # Some lines end with <$>, marking end of paragraph
        text = line['text'].replace('.', ' ')
        raw_tokens = text.split()
        
        for t in raw_tokens:
            # Check if token contains paragraph end marker
            is_end = False
            if '<$>' in t:
                is_end = True
                t = t.replace('<$>', '')
            
            clean = re.sub(r'[^a-zA-Z0-9]', '', t)
            if clean:
                all_tokens.append(clean)
            
            if is_end:
                all_tokens.append('<END>')

    # Analyze Daiin (Ingredients)
    for i in range(len(all_tokens)):
        word = all_tokens[i]
        if word == '<END>': continue
        
        if word in TARGET_VARIANTS or word == TARGET_WORD:
            if i + 1 < len(all_tokens) and all_tokens[i+1] != '<END>':
                ingredient = all_tokens[i+1]
                ingredients[ingredient] += 1
                
                start = max(0, i)
                end = min(len(all_tokens), i + 5)
                phrase_tokens = [t for t in all_tokens[start:end] if t != '<END>']
                phrases.append(" ".join(phrase_tokens))

    # Analyze End Verbs (Process Verbs)
    # Look for word immediately preceding <END>
    for i in range(len(all_tokens)):
        if all_tokens[i] == '<END>':
            if i > 0 and all_tokens[i-1] != '<END>':
                verb = all_tokens[i-1]
                end_verbs[verb] += 1

    return ingredients, phrases, end_verbs

def main():
    raw_lines = load_text(INPUT_FILE)
    lines = consolidate_lines(raw_lines)
    print(f"Processed {len(lines)} unique lines in Quire 20.")
    
    ingredient_counts, phrases, end_verbs = analyze_recipes(lines)
    
    try:
        with open(DICT_FILE, 'r') as f:
            master_dict = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {DICT_FILE} not found.")
        master_dict = {}

    output_data = {
        "target_word": TARGET_WORD,
        "top_ingredients": [],
        "top_end_verbs": [],
        "phrases": phrases[:50]
    }
    
    for word, count in ingredient_counts.most_common(30):
        dict_entry = master_dict.get(word, {})
        meaning = dict_entry.get('possible_meanings', []) or dict_entry.get('definition', '?')
        output_data["top_ingredients"].append({"word": word, "count": count, "meaning": meaning})

    for word, count in end_verbs.most_common(30):
        dict_entry = master_dict.get(word, {})
        meaning = dict_entry.get('possible_meanings', []) or dict_entry.get('definition', '?')
        output_data["top_end_verbs"].append({"word": word, "count": count, "meaning": meaning})
        
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    with open(OUTPUT_MD, 'w') as f:
        f.write("# Recipe Section Analysis (Quire 20)\n\n")
        f.write(f"**Hypothesis**: `{TARGET_WORD}` (From Spring/Take Water) starts recipes.\n\n")
        
        f.write(f"## Task 1: Ingredients (Words after `{TARGET_WORD}`)\n")
        f.write("| Word | Count | Meaning |\n|---|---|---|\n")
        for item in output_data["top_ingredients"]:
            m = item['meaning']
            if isinstance(m, list): m = ", ".join(m)
            f.write(f"| `{item['word']}` | {item['count']} | {m} |\n")
            
        f.write(f"\n## Task 3: Process Verbs (End of Paragraphs)\n")
        f.write("Possible verbs indicating 'mix', 'boil', 'drink', or completion.\n\n")
        f.write("| Word | Count | Meaning |\n|---|---|---|\n")
        for item in output_data["top_end_verbs"]:
            m = item['meaning']
            if isinstance(m, list): m = ", ".join(m)
            f.write(f"| `{item['word']}` | {item['count']} | {m} |\n")
            
        f.write("\n## Task 2: Structure & Amounts\n")
        f.write("Sample Phrases starting with `daiin`:\n")
        for p in phrases[:20]:
            f.write(f"- `{p}`\n")
            
    print(f"Written {OUTPUT_MD}")

if __name__ == "__main__":
    main()
