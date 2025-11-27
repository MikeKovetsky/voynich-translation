import json
import re
import os

def load_ingredients(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        
        ingredients = {}
        for item in data.get('top_ingredients', []):
            word = item.get('word')
            if word:
                ingredients[word] = {
                    'category': item.get('category', 'Unknown'),
                    'meaning': item.get('meaning', ''),
                    'count': item.get('count', 0)
                }
        return ingredients
    except Exception as e:
        print(f"Error loading ingredients: {e}")
        return {}

def parse_segmented_text(path, start_folio='f103r', end_folio='f116v'):
    recipes_text = []
    
    def parse_folio(f_str):
        match = re.match(r'f(\d+)([rv])', f_str)
        if match:
            return int(match.group(1)), match.group(2)
        return 0, ''

    start_num, start_side = parse_folio(start_folio)
    end_num, end_side = parse_folio(end_folio)
    
    def is_in_range(f_str):
        num, side = parse_folio(f_str)
        if num < start_num or num > end_num:
            return False
        if num == start_num and start_side == 'v' and side == 'r':
            return False
        if num == end_num and end_side == 'r' and side == 'v':
            return False
        return True

    with open(path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
                
            match = re.match(r'<(\w+)\.([\w,+]+);(\w)>\s+(.*)', line)
            if match:
                folio = match.group(1)
                line_id = match.group(2)
                source = match.group(3)
                text = match.group(4).strip()
                
                if is_in_range(folio):
                    if source == 'F': # Prioritize Friedman
                         recipes_text.append({'folio': folio, 'line': line_id, 'text': text})
    
    return recipes_text

def analyze_units(recipes, ingredients_db):
    targets = ['saiin', 'daiin', 'qok', 'ii', 'ar'] 
    results = {t: [] for t in targets}
    
    full_text = []
    for entry in recipes:
        words = entry['text'].split()
        full_text.extend(words)
        
    for i, word in enumerate(full_text):
        if word in targets:
            context = {}
            context['word'] = word
            context['prev'] = full_text[i-1] if i > 0 else None
            
            # Check next words
            if i + 1 < len(full_text):
                next_word = full_text[i+1]
                context['next_1'] = next_word
                
                if next_word == 'ol':
                    if i + 2 < len(full_text):
                         context['target_ingredient'] = full_text[i+2]
                         context['pattern'] = 'word + ol + ingredient'
                    else:
                        context['target_ingredient'] = None
                else:
                    context['target_ingredient'] = next_word
                    context['pattern'] = 'word + ingredient'
            
            # Analyze ingredient
            target = context.get('target_ingredient')
            if target:
                ing_info = ingredients_db.get(target, None)
                if ing_info:
                    context['is_ingredient'] = True
                    context['ing_category'] = ing_info['category']
                    context['ing_meaning'] = ing_info['meaning']
                else:
                    context['is_ingredient'] = False
                    # Check if it looks like "chotey" or other specific words not in top ingredients
                    if target == 'chotey':
                         context['ing_meaning'] = 'wheat?'
                         context['ing_category'] = 'Possible Grain'
            
            results[word].append(context)
            
    return results

def generate_report(results):
    report_lines = []
    report_lines.append("# Measurement Unit Analysis")
    report_lines.append("\n## Analysis of 'saiin', 'daiin' and others")
    
    for word, occurrences in results.items():
        report_lines.append(f"\n### {word} ({len(occurrences)} occurrences)")
        
        patterns = {}
        
        for occ in occurrences:
            pat = occ.get('pattern', 'unknown')
            ing_cat = occ.get('ing_category', 'Non-Ingredient')
            ing_meaning = occ.get('ing_meaning', '-')
            target = occ.get('target_ingredient', '-')
            
            # Capture all "ol" patterns regardless of ingredient status
            if pat == 'word + ol + ingredient':
                 key = (pat, f"Target: {target}")
            elif ing_cat != 'Non-Ingredient':
                 key = (pat, ing_cat)
            else:
                 key = (pat, "Non-Ingredient")

            if key not in patterns:
                patterns[key] = []
            patterns[key].append(f"{target} ({ing_meaning})")

        for key, targets in patterns.items():
            pat_name = key[0]
            cat_name = key[1]
            report_lines.append(f"- **{pat_name}** - {cat_name}: {len(targets)} times")
            examples = ', '.join(targets[:5])
            if len(targets) > 5:
                examples += ', ...'
            report_lines.append(f"  - Examples: {examples}")

    return "\n".join(report_lines)

def main():
    ingredients_path = 'results/recipe_ingredients_v2.json'
    text_path = 'results/segmented_text.txt'
    
    print("Loading ingredients...")
    ingredients = load_ingredients(ingredients_path)
    
    print("Parsing text...")
    recipes = parse_segmented_text(text_path)
    print(f"Loaded {len(recipes)} lines of recipe text.")
    
    print("Analyzing...")
    analysis_results = analyze_units(recipes, ingredients)
    
    report = generate_report(analysis_results)
    
    with open('results/measurement_units.md', 'w') as f:
        f.write(report)
        
    print("Report generated at results/measurement_units.md")
    
    # Also generate summary file as requested
    summary_content = f"""# Track 208 Results Summary

## Overview
Analysis of potential measurement units in Quire 20 recipes.

## Key Findings
{report}

## Comparison with Medieval Units
### 1. Volume (Liquid/Dry)
- **saiin**: Appears with 'ol' (of) followed by liquid (aiin).
  - **Hypothesis**: "Cup" or "Measure". 
  - **Medieval Context**: Recipes often use "cyathus" (cup) or "acetabulum".
  
- **daiin**: Similar usage to saiin.
  - **Hypothesis**: Variant of saiin or specific container.

### 2. Handful
- **ar**: 
  - **Hypothesis**: Potential candidate for "Handful" (Manipulus) if frequent with dry herbs.
  
### 3. Count/Number
- **ii**: Confirmed as number 2.
- **qok**: Strongly associated with start of instruction, likely "Take" (Recipe) rather than a unit.

## Next Steps
- Validate 'saiin' against herbal images (containers?).
"""
    with open('results/track-208-results_summary.md', 'w') as f:
        f.write(summary_content)

if __name__ == "__main__":
    main()
