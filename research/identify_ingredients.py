import json
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    # Input files
    ingredients_path = 'results/recipe_ingredients_v2.json'
    mined_plants_path = 'results/mined_plant_names.json'
    dictionary_path = 'results/master_dictionary_v7_3.json'
    
    # Load data
    print(f"Loading {ingredients_path}...")
    try:
        ingredients_data = load_json(ingredients_path)
        top_ingredients = ingredients_data.get('top_ingredients', [])
    except FileNotFoundError:
        print(f"Error: {ingredients_path} not found.")
        return

    print(f"Loading {mined_plants_path}...")
    try:
        mined_plants_data = load_json(mined_plants_path)
        mined_entries = mined_plants_data.get('entries', [])
    except FileNotFoundError:
        print(f"Error: {mined_plants_path} not found.")
        mined_entries = []

    print(f"Loading {dictionary_path}...")
    try:
        full_dictionary_data = load_json(dictionary_path)
        
        if 'entries' in full_dictionary_data:
            dictionary = full_dictionary_data['entries']
            print(f"Dictionary loaded with {len(dictionary)} entries (from 'entries' key).")
        else:
            dictionary = full_dictionary_data
            print(f"Dictionary loaded with {len(dictionary)} entries (root).")
            
        if 'chtol' in dictionary:
            print("Confirmed 'chtol' is in dictionary.")
        else:
            print("WARNING: 'chtol' NOT found in dictionary keys.")
            
    except FileNotFoundError:
        print(f"Error: {dictionary_path} not found.")
        return

    # Target words to identify
    target_words = ['chtol', 'tsho', 'shoaiin', 'shkaiin']
    
    # Map target words to findings
    results = {}
    
    # Helper to find mined data for a word
    def find_mined_info(word):
        candidates = [e for e in mined_entries if e['voynich'] == word]
        if candidates:
            # Return the one with highest confidence or first
            best = max(candidates, key=lambda x: 1 if x.get('confidence') == 'high' else 0)
            return best
        return None

    # Manual/Known descriptions (simulated based on task context and expert IDs)
    plant_descriptions = {
        'papaver': "Plant with large flower (often red in nature, but manuscript colors vary), distinct seed pod.",
        'smilax': "Climbing plant with heart-shaped or triangular leaves, often prickly stem.",
        'cannabis': "Plant with palmate leaves (serrated leaflets), distinctive tall structure.",
        'hypericum': "Plant with opposite leaves, yellow flowers (often star-shaped), perforated leaves (St John's Wort)."
    }

    for word in target_words:
        print(f"Analyzing {word}...")
        
        info = find_mined_info(word)
        
        if info:
            expert_id = info.get('evidence', {}).get('expert_id')
            page = info.get('evidence', {}).get('appears_on_plant_page')
            
            description = plant_descriptions.get(expert_id, "Description not available in local database.")
            
            results[word] = {
                "word": word,
                "identified_as": expert_id,
                "confidence": info.get('confidence', 'unknown'),
                "herbal_page": page,
                "visual_description": description,
                "evidence": info.get('evidence', {})
            }
        else:
            results[word] = {
                "word": word,
                "identified_as": "Unknown",
                "confidence": "None",
                "herbal_page": "Not found as label",
                "visual_description": "N/A",
                "evidence": {}
            }

    # Generate Report
    report_lines = [
        "# Ingredient Identification Report",
        "",
        "## Goal",
        "Identify the botanical identity of top specific ingredients found in recipes.",
        "",
        "## Findings",
        ""
    ]
    
    for word in target_words:
        res = results[word]
        report_lines.append(f"### Word: `{word}`")
        report_lines.append(f"- **Identified As:** {res['identified_as'].capitalize() if res['identified_as'] else 'Unknown'}")
        report_lines.append(f"- **Herbal Page:** {res['herbal_page']}")
        report_lines.append(f"- **Confidence:** {res['confidence'].upper()}")
        report_lines.append(f"- **Visual Description:** {res['visual_description']}")
        report_lines.append(f"- **Evidence:** {res['evidence']}")
        report_lines.append("")

    # Update Dictionary
    updated_count = 0
    for word, res in results.items():
        if res['identified_as'] and res['identified_as'] != 'Unknown':
            if word in dictionary:
                print(f"Updating {word} with {res['identified_as']}...")
                dictionary[word]['possible_id'] = res['identified_as']
                dictionary[word]['herbal_page'] = res['herbal_page']
                
                # Update meaning/definition if generic
                current_meaning = dictionary[word].get('meaning', '')
                
                # If meaning is generic or unknown, update it
                if current_meaning in ['plant_term', 'unknown_plant', 'herb/plant (generic)', 'unknown'] or not current_meaning:
                     dictionary[word]['meaning'] = res['identified_as']
                
                # Always add note
                dictionary[word]['note'] = f"Identified as {res['identified_as']} on {res['herbal_page']}. {res['visual_description']}"
                updated_count += 1
            else:
                print(f"Warning: {word} not found in dictionary for update.")

    # Save Outputs
    output_map_path = 'results/ingredient_map.json'
    save_json(output_map_path, results)
    print(f"Saved ingredient map to {output_map_path}")

    report_path = 'results/ingredient_identification.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"Saved report to {report_path}")
    
    # Save updated dictionary (v7.4)
    dict_out_path = 'results/master_dictionary_v7_4.json'
    
    # Update version info
    if 'version' in full_dictionary_data:
        full_dictionary_data['version'] = "7.4"
        
    save_json(dict_out_path, full_dictionary_data)
    print(f"Saved updated dictionary to {dict_out_path} (Updated {updated_count} entries)")

if __name__ == "__main__":
    main()
