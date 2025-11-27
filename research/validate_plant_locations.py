import json
from collections import defaultdict

INGREDIENT_MAP = "results/ingredient_map.json"
RECIPE_INGREDIENTS = "results/recipe_ingredients_v2.json"
OUTPUT_REPORT = "results/plant_recipe_correlation_report.md"

def main():
    print("Validating Plant-Recipe Correlations...")
    
    try:
        with open(INGREDIENT_MAP, 'r') as f:
            plants = json.load(f)
            
        with open(RECIPE_INGREDIENTS, 'r') as f:
            recipe_data = json.load(f)
            
        # Extract recipe ingredient list (simplified)
        recipe_ingredients = set()
        # Assuming recipe_ingredients_v2 structure, or just using the list of ingredients mined
        # Let's look at the structure of recipe_ingredients_v2.json if it exists, otherwise fallback
        # Since we don't have the content of recipe_ingredients_v2 in context, we'll use the graph data or re-mine
        # Actually, let's use the voynich_knowledge_graph.json which has "USED_IN" edges
        
        with open("results/voynich_knowledge_graph.json", 'r') as f:
            graph = json.load(f)
            
        # Build map of Plant -> Recipe Pages
        plant_usage = defaultdict(list)
        for edge in graph['edges']:
            if edge['type'] == 'USED_IN':
                plant_usage[edge['source']].append(edge['target'])
                
        # Generate Report
        lines = []
        lines.append("# Plant-Recipe Correlation Report")
        lines.append("")
        lines.append("## Goal")
        lines.append("Validate if plants drawn in the Herbal section appear in the Recipe section (Pharma).")
        lines.append("")
        
        lines.append("## Summary Statistics")
        lines.append(f"- Total Plants Analyzed: {len(plants)}")
        used_count = sum(1 for p in plants if p in plant_usage)
        lines.append(f"- Plants appearing in Recipes: {used_count} ({used_count/len(plants)*100:.1f}%)")
        lines.append("")
        
        lines.append("## Detailed Findings")
        lines.append("")
        lines.append("| Plant Word | ID | Drawn On | Recipe Occurrences | Bio Occurrences | Closest Recipe | Distance |")
        lines.append("|------------|----|----------|-------------------|-----------------|----------------|----------|")
        
        for plant, details in plants.items():
            word = plant # Using the key as the word
            # Adjust if structure is different
            
            # Find usage
            uses = plant_usage.get(word, []) # word might be 'chtol' or 'Papaver' depending on graph
            # The graph uses IDs like 'Poppy' or 'chtol'. Let's check graph nodes.
            # Graph nodes have ID 'Poppy' and voynich_id 'chtol'.
            
            # Let's find the node for this plant
            node = next((n for n in graph['nodes'] if n.get('voynich_id') == word or n['id'] == word), None)
            plant_id = node['id'] if node else word
            
            uses = plant_usage.get(plant_id, [])
            
            recipe_count = sum(1 for u in uses if 'f1' in u) # Recipes are f103+
            bio_count = sum(1 for u in uses if 'f7' in u or 'f8' in u) # Bio is f75-84
            
            drawn_on = details.get('appears_on_plant_page', 'Unknown')
            
            lines.append(f"| `{word}` | {details.get('expert_id', '?')} | {drawn_on} | {recipe_count} | {bio_count} | {uses[0] if uses else '-'} | {0} |")

        with open(OUTPUT_REPORT, 'w') as f:
            f.write('\n'.join(lines))
            
        print(f"Report generated: {OUTPUT_REPORT}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
