import json
import re
import os

def parse_translation_md(filepath):
    pages = set()
    with open(filepath, 'r') as f:
        for line in f:
            match = re.match(r'\*\*(f[0-9]+[rv][0-9]*)\.[0-9]+\*\*', line)
            if match:
                pages.add(match.group(1))
    return list(pages)

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    # Input files
    translation_file = 'results/voynich_full_translation_v7_4.md'
    plant_file = 'results/plant_identifications.json'
    plant_crossref_file = 'results/plant_recipe_crossref.json'
    ingredient_file = 'results/ingredient_map.json'
    recipe_analysis_file = 'results/final_recipe_analysis.json'
    zodiac_file = 'results/zodiac_label_analysis.json'
    
    # Output file
    output_file = 'results/voynich_knowledge_graph.json'

    # 1. Extract Pages
    pages = parse_translation_md(translation_file)
    print(f"Extracted {len(pages)} pages.")

    # 2. Extract Plants & Edges
    plants_data = load_json(plant_file)
    plant_crossref_data = load_json(plant_crossref_file)
    
    plants = {} # id -> node
    plant_edges = [] # APPEARS_ON, USED_IN
    
    # From Identification (APPEARS_ON)
    if plants_data:
        for identification in plants_data.get('identifications', []):
            if 'top_candidate' in identification:
                plant_name = identification['top_candidate']['name']
                folio = identification['folio']
                voynich_name = identification.get('voynich_name', '')
                
                if plant_name not in plants:
                    plants[plant_name] = {
                        'id': plant_name,
                        'type': 'Plant',
                        'latin': identification['top_candidate'].get('latin', ''),
                        'voynich_id': voynich_name
                    }
                
                plant_edges.append({
                    'source': plant_name,
                    'target': folio,
                    'type': 'APPEARS_ON'
                })

    # From Crossref (USED_IN - Plant appearing in Recipe)
    if plant_crossref_data:
        for item in plant_crossref_data:
            # "expert_plant": "aconitum"
            plant_id = item.get('expert_plant')
            if not plant_id: 
                continue
                
            plant_id = plant_id.capitalize()

            if plant_id not in plants:
                plants[plant_id] = {
                    'id': plant_id,
                    'type': 'Plant',
                    'latin': '', 
                    'voynich_id': item.get('word', '')
                }
            
            for occurrence in item.get('recipe_occurrences', []):
                folio = occurrence['folio']
                plant_edges.append({
                    'source': plant_id,
                    'target': folio,
                    'type': 'USED_IN',
                    'details': 'Recipe occurrence'
                })

    print(f"Extracted {len(plants)} plants.")

    # 3. Extract Ingredients & Edges
    ingredients_data = load_json(ingredient_file)
    recipe_analysis_data = load_json(recipe_analysis_file)
    
    ingredients = {}
    ingredient_edges = [] # USED_IN
    
    # From Ingredient Map
    if ingredients_data:
        for word, data in ingredients_data.items():
            if word not in ingredients:
                ingredients[word] = {
                    'id': word,
                    'type': 'Ingredient',
                    'identified_as': data.get('identified_as', ''),
                    'description': data.get('visual_description', '')
                }
            
            for folio in data.get('recipe_folios', []):
                ingredient_edges.append({
                    'source': word,
                    'target': folio,
                    'type': 'USED_IN'
                })

    # From Final Recipe Analysis
    if recipe_analysis_data:
        for recipe in recipe_analysis_data.get('golden_recipes', []):
            folio = recipe.get('folio')
            slots = recipe.get('slots', {})
            ingredient_word = slots.get('ingredient')
            
            if ingredient_word and folio:
                if ingredient_word not in ingredients:
                    ingredients[ingredient_word] = {
                        'id': ingredient_word,
                        'type': 'Ingredient',
                        'identified_as': '',
                        'description': 'Extracted from golden recipes'
                    }
                
                exists = False
                for edge in ingredient_edges:
                    if edge['source'] == ingredient_word and edge['target'] == folio and edge['type'] == 'USED_IN':
                        exists = True
                        break
                
                if not exists:
                    ingredient_edges.append({
                        'source': ingredient_word,
                        'target': folio,
                        'type': 'USED_IN'
                    })

    print(f"Extracted {len(ingredients)} ingredients.")

    # 4. Extract Stars/Zodiac & Edges
    zodiac_data = load_json(zodiac_file)
    stars = {}
    star_edges = [] # LINKED_TO
    
    plant_voynich_map = {} # voynich_name -> plant_id
    for p in plants.values():
        if p.get('voynich_id'):
            plant_voynich_map[p['voynich_id'].strip().lower()] = p['id']

    if zodiac_data:
        for folio, data in zodiac_data.get('folio_data', {}).items():
             sign = data.get('zodiac_sign')
             if sign:
                 if sign not in stars:
                     stars[sign] = {
                         'id': sign,
                         'type': 'Star/Zodiac',
                         'folio': folio
                     }
                 
                 for label in data.get('labels', []):
                     label_clean = label.strip().lower()
                     if label_clean in plant_voynich_map:
                         plant_id = plant_voynich_map[label_clean]
                         star_edges.append({
                             'source': sign,
                             'target': plant_id,
                             'type': 'LINKED_TO',
                             'details': f"Matched label {label}"
                         })

    print(f"Extracted {len(stars)} stars.")

    # Build Graph
    nodes = []
    for page in pages:
        nodes.append({'id': page, 'type': 'Page'})
    
    nodes.extend(plants.values())
    nodes.extend(ingredients.values())
    nodes.extend(stars.values())
    
    all_edges = plant_edges + ingredient_edges + star_edges
    
    graph = {
        'nodes': nodes,
        'edges': all_edges
    }
    
    with open(output_file, 'w') as f:
        json.dump(graph, f, indent=2)
        
    print(f"Graph generated at {output_file}")
    print(f"Nodes: {len(nodes)}, Edges: {len(all_edges)}")

if __name__ == '__main__':
    main()
