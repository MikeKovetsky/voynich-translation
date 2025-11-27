import json
import re
import csv

def parse_star_description(description, count):
    """
    Parses the star description to generate a list of colors.
    Returns a list of strings (e.g., ['Red', 'Yellow', ...])
    """
    desc_lower = description.lower()
    colors = []
    
    # Default pattern
    pattern = ['Red', 'Yellow']
    
    # Custom patterns based on description analysis
    if "alternatingly red or faded yellow" in desc_lower:
        pattern = ['Red', 'Yellow']
    elif "alternatingly red and faded yellow" in desc_lower:
        pattern = ['Red', 'Yellow']
    elif "unusually starting with faded yellow" in desc_lower:
        pattern = ['Yellow', 'Red']
    elif "starting with faded yellow" in desc_lower:
        pattern = ['Yellow', 'Red']
    
    # Generate sequence
    for i in range(count):
        colors.append(pattern[i % 2])
            
    return colors

def main():
    # 1. Load JSON
    with open('results/quire_20_recipes.json', 'r') as f:
        data = json.load(f)
    
    folios_data = {f['folio']: f for f in data['folios']}
    target_folios = sorted(folios_data.keys())
    print(f"Processing {len(target_folios)} folios: {target_folios}")
    
    # 2. Extract Star Colors
    star_map = [] # {'folio': ..., 'index': ..., 'color': ...}
    
    for folio_name in target_folios:
        folio_info = folios_data[folio_name]
        desc = folio_info['description']
        
        # Extract count
        # Matches "There are 19 stars", "There a ten stars", "Are 15 large stars"
        match = re.search(r'(?:re|a) (\d+|ten|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty) (?:large )?stars', desc, re.IGNORECASE)
        if not match:
             match = re.search(r're (\d+) large stars', desc, re.IGNORECASE)
        
        count = 0
        if match:
            num_str = match.group(1).lower()
            if num_str.isdigit():
                count = int(num_str)
            else:
                text_nums = {'ten': 10, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 
                             'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20}
                count = text_nums.get(num_str, 0)
        
        if count == 0:
            print(f"Warning: Could not determine star count for {folio_name}. Description: {desc[:50]}...")
            count = 15

        print(f"{folio_name}: Detected count {count}")
             
        colors = parse_star_description(desc, count)
        
        for i, color in enumerate(colors):
            star_map.append({
                'folio': folio_name,
                'index': i + 1,
                'color': color
            })

    # 3. Extract Recipe Starters from Transcription
    starters = [] 
    
    with open('data/eva_ivtff.txt', 'r') as f:
        for line in f:
            if line.startswith('<f'):
                match = re.match(r'<f(\d+[rv])\.(\d+),([^;]+);([^>]+)>', line)
                if match:
                    folio_num = match.group(1)
                    line_num = int(match.group(2))
                    transcriber = match.group(4)
                    
                    full_folio = 'f' + folio_num
                    
                    if full_folio in target_folios:
                        if transcriber != 'H':
                            continue
                            
                        # Extract text
                        try:
                            text_part = line.split('>')[1].strip()
                            # Split by dot or space
                            words = re.split(r'[. ]+', text_part)
                            words = [w for w in words if w] 
                            first_word = words[0] if words else ""
                            
                            starters.append({
                                'folio': full_folio,
                                'index': line_num,
                                'word': first_word
                            })
                        except IndexError:
                            pass

    # 4. Write CSVs
    with open('results/star_color_map.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['folio', 'index', 'color'])
        writer.writeheader()
        writer.writerows(star_map)
        
    with open('results/recipe_starters_v2.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['folio', 'index', 'word'])
        writer.writeheader()
        writer.writerows(starters)

    print(f"Generated results/star_color_map.csv with {len(star_map)} entries.")
    print(f"Generated results/recipe_starters_v2.csv with {len(starters)} entries.")

if __name__ == "__main__":
    main()
