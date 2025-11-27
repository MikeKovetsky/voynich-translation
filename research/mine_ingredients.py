import json
import re
import collections
import os

# Configuration
INPUT_TEXT = "data/eva_ivtff.txt"
INPUT_DICT = "results/master_dictionary_v7_2.json"
PLANT_IDS = "results/plant_identifications.json"
MINED_PLANT_NAMES = "results/mined_plant_names.json"
OUTPUT_JSON = "results/recipe_ingredients_v2.json"
OUTPUT_REPORT = "results/ingredient_analysis_report.md"

def load_file(path):
    if not os.path.exists(path):
        print(f"Error: File not found {path}")
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: JSON file not found {path}")
        return {}

def parse_quire20(text):
    start_marker = "<f103r"
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return text 
    end_idx = text.find("<f117", start_idx)
    if end_idx == -1:
        end_idx = len(text)
    return text[start_idx:end_idx]

def mine_ingredients(text):
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        if line.startswith('#'): continue
        line = re.sub(r'<[^>]+>', ' ', line)
        line = re.sub(r'\{[^}]+\}', ' ', line)
        clean_lines.append(line)
        
    full_text = " ".join(clean_lines)
    full_text = re.sub(r'\s+', ' ', full_text)
    
    pattern = r'\bdaiin\b(.*?)\b(okeol|qokeey)\b'
    matches = re.findall(pattern, full_text)
    
    ingredients = []
    grammar_words = {
        'ol', 'or', 'y', 'al', 'o', 'ar', 'daiin', 'okeol', 'qokeey', 
        'chedy', 's', 't', 'k', 'd', 'da', 'dy', 'qok'
    }
    
    valid_matches = 0
    for content, end_verb in matches:
        words = re.split(r'[.\s]+', content.strip())
        if not words: continue
        valid_matches += 1
        for w in words:
            w_clean = w.strip(',.')
            if w_clean not in grammar_words and len(w_clean) > 1:
                ingredients.append(w_clean)
        
    return ingredients, valid_matches

def main():
    text = load_file(INPUT_TEXT)
    dictionary = load_json(INPUT_DICT)
    plant_data = load_json(PLANT_IDS)
    mined_plants = load_json(MINED_PLANT_NAMES)
    
    quire20_text = parse_quire20(text)
    ingredients, match_count = mine_ingredients(quire20_text)
    counts = collections.Counter(ingredients)
    
    # Extract plant labels
    plant_labels = set()
    label_meanings = {}
    
    if 'identifications' in plant_data:
        for item in plant_data['identifications']:
            if 'voynich_name' in item:
                v_name = item['voynich_name']
                plant_labels.add(v_name)
                label_meanings[v_name] = item.get('top_candidate', {}).get('name', 'Unknown')
                
    if 'name_mappings' in plant_data:
        for item in plant_data['name_mappings']:
            if 'voynich' in item:
                v_name = item['voynich']
                plant_labels.add(v_name)
                label_meanings[v_name] = item.get('candidate', 'Unknown')

    if 'entries' in mined_plants:
        for entry in mined_plants['entries']:
            if 'voynich' in entry:
                v_name = entry['voynich']
                plant_labels.add(v_name)
                label_meanings[v_name] = entry.get('meaning', 'Unknown')
    
    analysis = []
    # Top 100
    for word, count in counts.most_common(100):
        category = "Unknown"
        meaning = ""
        if 'entries' in dictionary and word in dictionary['entries']:
             meaning = dictionary['entries'][word].get('meaning', '')
        
        is_herbal = word in plant_labels
        
        if meaning and "plant" in meaning.lower():
            category = "Plant (Dict)"
        elif is_herbal:
            category = "Specific (Herbal Label)"
        elif word in ['chol', 'char', 'kor', 'dol']: 
            category = "Part (Leaf/Root/etc)"
        elif word.startswith('sh') or word in ['al', 'ar', 'shey']: 
            category = "Quantity/grammar?"
        elif word in ['saiin', 'aiin']:
             category = "Liquid/Water?"
        
        analysis.append({
            "word": word,
            "count": count,
            "category": category,
            "meaning": meaning,
            "is_herbal_label": is_herbal
        })
        
    # Find ALL label matches
    all_label_matches = []
    for word, count in counts.items():
        if word in plant_labels:
             all_label_matches.append({
                 "word": word,
                 "count": count,
                 "meaning": label_meanings.get(word, "Unknown")
             })
    all_label_matches.sort(key=lambda x: x['count'], reverse=True)

    # Save JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            "recipe_matches": match_count,
            "top_ingredients": analysis,
            "label_matches": all_label_matches,
            "all_counts": dict(counts)
        }, f, indent=2)
        
    # Write Report
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("# Ingredient Analysis Report\n\n")
        f.write(f"**Source:** Quire 20 (Recipes)\n")
        f.write(f"**Pattern:** `daiin` ... `okeol/qokeey`\n")
        f.write(f"**Matches Found:** {match_count}\n\n")
        
        f.write("## 1. Common Ingredient Terms (Top 50)\n\n")
        f.write("| Word | Count | Category | Meaning | Label? |\n")
        f.write("|---|---|---|---|---|\n")
        for item in analysis[:50]:
            label_check = "✅" if item['is_herbal_label'] else ""
            meaning_str = item['meaning'] if item['meaning'] else "-"
            f.write(f"| **{item['word']}** | {item['count']} | {item['category']} | {meaning_str} | {label_check} |\n")
            
        f.write("\n## 2. Cross-Reference: Herbal Labels in Recipes\n")
        f.write("The following words appear as labels in the Herbal/Pharma sections AND as ingredients in recipes:\n\n")
        f.write("| Word | Frequency | Known Meaning/ID |\n")
        f.write("|---|---|---|\n")
        for m in all_label_matches:
            f.write(f"| **{m['word']}** | {m['count']} | {m['meaning']} |\n")
            
        f.write("\n## 3. Classification Summary\n")
        f.write(f"- **Total Unique Label Matches:** {len(all_label_matches)}\n")
        f.write(f"- **Generic Parts (chol/char/dol):** Found frequently (chol: {counts['chol']}, char: {counts['char']})\n")
        f.write(f"- **Liquids (aiin/saiin):** Found frequently (aiin: {counts['aiin']}, saiin: {counts['saiin']})\n")

    print(f"Done. Saved to {OUTPUT_JSON} and {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
