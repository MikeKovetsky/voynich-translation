
import re
import os
from collections import Counter

def analyze_recipes(input_file, output_file):
    print(f"Reading {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    recipes = []
    current_recipe = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("**Recipe #"):
            if current_recipe:
                recipes.append(current_recipe)
            current_recipe = {
                "id": line.strip("*"),
                "text": "",
                "verbs": [],
                "ingredients": [],
                "typology": [],
                "colors": []
            }
        elif current_recipe and line:
            current_recipe["text"] += " " + line

    if current_recipe:
        recipes.append(current_recipe)

    print(f"Found {len(recipes)} recipes.")

    # Keywords
    verb_keywords = ["mix", "boil", "cook", "process", "drink", "apply", "take", "gather", "clean", "heat", "cool", "wash"]
    ingredient_keywords = ["green (leaf)", "red / brown (root)", "water", "oil", "herb", "plant", "root", "flower", "seed", "leaf", "mixture", "decoction"]
    typology_keywords = ["drink", "wash", "pain", "head", "stomach", "bath", "eat", "sick", "ointment"]
    
    color_keywords = ["red", "green", "blue", "brown", "white", "black", "gold", "yellow"]
    heat_verbs = ["boil", "cook", "heat", "process"]
    cool_verbs = ["cool", "mix", "wash"] # Assuming mix/wash might be cool or neutral

    all_verbs = []
    all_ingredients = []
    
    typology_counts = Counter()
    consistency_data = {
        "red_heat": 0,
        "red_cool": 0,
        "blue_cool": 0, # Assuming Blue exists or mapping Green/Blue
        "green_heat": 0,
        "green_cool": 0
    }

    for recipe in recipes:
        text_lower = recipe["text"].lower()
        
        # Extract Verbs
        for v in verb_keywords:
            if v in text_lower:
                recipe["verbs"].append(v)
                all_verbs.append(v)
        
        # Extract Ingredients
        for i in ingredient_keywords:
            if i in text_lower:
                recipe["ingredients"].append(i)
                all_ingredients.append(i)

        # Typology
        for t in typology_keywords:
            if t in text_lower:
                recipe["typology"].append(t)
                typology_counts[t] += 1

        # Colors
        for c in color_keywords:
            if c in text_lower:
                recipe["colors"].append(c)

        # Consistency
        has_red = "red" in text_lower or "brown" in text_lower
        has_green = "green" in text_lower
        has_heat = any(hv in text_lower for hv in heat_verbs)
        has_cool = any(cv in text_lower for cv in cool_verbs)
        
        if has_red and has_heat:
            consistency_data["red_heat"] += 1
        if has_red and has_cool: # Overlap possible
            consistency_data["red_cool"] += 1
        
        if has_green and has_heat:
            consistency_data["green_heat"] += 1
        if has_green and has_cool:
            consistency_data["green_cool"] += 1

    # Frequency Analysis
    top_verbs = Counter(all_verbs).most_common(5)
    top_ingredients = Counter(all_ingredients).most_common(5)

    # Write Output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Quire 20 Recipe Analysis\n\n")
        
        f.write("## 1. Frequency Analysis\n\n")
        f.write("### Top 5 Verbs\n")
        for v, count in top_verbs:
            f.write(f"- **{v.title()}**: {count}\n")
        
        f.write("\n### Top 5 Ingredients\n")
        for i, count in top_ingredients:
            f.write(f"- **{i.title()}**: {count}\n")

        f.write("\n## 2. Typology\n\n")
        f.write("Are the recipes for *eating*, *bathing*, or *medical*?\n\n")
        if typology_counts:
            f.write("| Type/Keyword | Count |\n|---|---|\n")
            for t, count in typology_counts.most_common():
                f.write(f"| {t.title()} | {count} |\n")
        else:
            f.write("No typology keywords found.\n")

        f.write("\n## 3. Consistency Check\n\n")
        f.write("Do 'Red' ingredients appear with 'Heat' verbs? Do 'Green' ingredients appear with 'Cool' verbs?\n\n")
        
        f.write(f"- Red/Brown with Heat verbs: {consistency_data['red_heat']} recipes\n")
        f.write(f"- Red/Brown with Cool verbs: {consistency_data['red_cool']} recipes\n")
        f.write(f"- Green with Heat verbs: {consistency_data['green_heat']} recipes\n")
        f.write(f"- Green with Cool verbs: {consistency_data['green_cool']} recipes\n")
        
        f.write("\n## 4. Summary\n\n")
        f.write(f"Analyzed {len(recipes)} recipes from {input_file}.\n")
        
        # Interpretation
        f.write("### Observations:\n")
        if top_verbs:
             f.write(f"- The most common action is '{top_verbs[0][0]}'.\n")
        if top_ingredients:
             f.write(f"- The most common ingredient is '{top_ingredients[0][0]}'.\n")
        
        if consistency_data['red_heat'] > consistency_data['red_cool']:
            f.write("- Red ingredients are more frequently associated with Heat.\n")
        else:
             f.write("- Red ingredients show no strong preference for Heat.\n")

        if consistency_data['green_cool'] > consistency_data['green_heat']:
            f.write("- Green ingredients are more frequently associated with Cool/Mix actions.\n")
        else:
             f.write("- Green ingredients show no strong preference for Cool actions.\n")

    print(f"Analysis complete. Results written to {output_file}")

if __name__ == "__main__":
    analyze_recipes("results/quire20_translation_master.md", "results/quire20_analysis.md")
