import json
import re

def run_recipe_elemental_check():
    # Load Page Map
    try:
        with open("results/elemental_page_map.json", "r") as f:
            page_map = json.load(f)
    except:
        print("Run Task 231 first.")
        return

    # Load Dictionary for Ingredient Lookup
    try:
        with open("results/dictionary/dictionary.json", "r") as f:
            dictionary = json.load(f)
            # Handle v9.1 structure (entries key)
            entries = dictionary.get("entries", dictionary)
    except:
        entries = {}

    # Load Corpus for Recipe Text
    with open("data/eva_ivtff.txt", "r") as f:
        text = f.read()
        
    recipes = []
    # Split corpus into lines to associate with pages
    lines = text.split("\n")
    
    current_folio = ""
    
    wet_ingredients = {}
    dry_ingredients = {}

    for line in lines:
        # Update Folio
        match = re.search(r"<f(\d+[rv])", line)
        if match:
            current_folio = match.group(1)
            
        if not current_folio: continue
        
        # Get Page Class
        page_class = page_map.get(current_folio, {}).get("class", "Neutral")
        if page_class == "Neutral": continue
        
        # Find Ingredients: Words after 'daiin' or 'ol'
        words = re.findall(r"[a-z]+", line.lower())
        for i in range(len(words)-1):
            curr = words[i]
            next_w = words[i+1]
            
            if curr in ["daiin", "ol", "o", "al", "or"]:
                # next_w is likely ingredient
                if len(next_w) < 3: continue
                
                if page_class == "Wet":
                    wet_ingredients[next_w] = wet_ingredients.get(next_w, 0) + 1
                else:
                    dry_ingredients[next_w] = dry_ingredients.get(next_w, 0) + 1

    # Filter significant ones
    sig_wet = sorted(wet_ingredients.items(), key=lambda x: x[1], reverse=True)[:20]
    sig_dry = sorted(dry_ingredients.items(), key=lambda x: x[1], reverse=True)[:20]

    # Compare
    report = "# Track 232: Recipe Elemental Analysis\n\n"
    
    report += "## Top Ingredients on Wet Pages (Venus/Water)\n"
    report += "| Ingredient | Count | Dictionary Meaning |\n|---|---|---|\n"
    for w, c in sig_wet:
        meaning = entries.get(w, {}).get("meaning", "UNKNOWN") if isinstance(entries.get(w), dict) else "UNKNOWN"
        report += f"| {w} | {c} | {meaning} |\n"

    report += "\n## Top Ingredients on Dry Pages (Mars/Fire)\n"
    report += "| Ingredient | Count | Dictionary Meaning |\n|---|---|---|\n"
    for w, c in sig_dry:
        meaning = entries.get(w, {}).get("meaning", "UNKNOWN") if isinstance(entries.get(w), dict) else "UNKNOWN"
        report += f"| {w} | {c} | {meaning} |\n"
        
    # Specific Checks
    report += "\n## Specific Markers Check\n"
    report += f"- **oteaiin** (Water Lily): Wet={wet_ingredients.get('oteaiin',0)}, Dry={dry_ingredients.get('oteaiin',0)}\n"
    report += f"- **ald** (Thistle/Mars): Wet={wet_ingredients.get('ald',0)}, Dry={dry_ingredients.get('ald',0)}\n"
    report += f"- **choly** (Nettle/Mars): Wet={wet_ingredients.get('choly',0)}, Dry={dry_ingredients.get('choly',0)}\n"

    with open("results/recipe_humoral_analysis.md", "w") as f:
        f.write(report)
        
    with open("results/track-232-results_summary.md", "w") as f:
        f.write(report) # Same content for summary

if __name__ == "__main__":
    run_recipe_elemental_check()
