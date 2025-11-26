
import voynich_data
import re
from collections import Counter
import json

def run_syntax_test():
    print("=== SYNTAX HYPOTHESIS TEST ===")
    
    # Load data
    pages = voynich_data.get_eva_pages()
    
    # --- TEST 1: 'chan' CONTEXT ---
    print("\n[1] ANALYSIS OF 'chan' (Specific Plant Anchor)")
    print("Hypothesis: If 'chan' is a plant/noun, words around it are Adjectives or Verbs.")
    
    chan_contexts = []
    
    for folio, lines in pages.items():
        for loc, text in lines.items():
            # Clean punctuation for word splitting
            clean = re.sub(r'[^\w\s.-]', '', text)
            words = [w for w in clean.split('.') if w]
            
            if 'chan' in words:
                indices = [i for i, x in enumerate(words) if x == 'chan']
                for idx in indices:
                    prev_w = words[idx-1] if idx > 0 else "[START]"
                    next_w = words[idx+1] if idx < len(words)-1 else "[END]"
                    chan_contexts.append({
                        'folio': folio,
                        'loc': loc,
                        'prev': prev_w,
                        'next': next_w,
                        'line': words
                    })

    print(f"Found {len(chan_contexts)} occurrences of 'chan'.")
    print(f"{'FOLIO':<8} | {'PREV':<15} | {'TARGET':<6} | {'NEXT':<15} | {'FULL LINE'}")
    print("-" * 80)
    for c in chan_contexts:
        # Format line for display (truncated)
        line_str = ".".join(c['line'])
        if len(line_str) > 40: line_str = line_str[:37] + "..."
        print(f"{c['folio']:<8} | {c['prev']:<15} | chan   | {c['next']:<15} | {line_str}")

    # --- TEST 2: 'daiin' AS IMPERATIVE VERB ---
    print("\n[2] ANALYSIS OF 'daiin' (Proposed: 'Take'/'Mix')")
    print("Hypothesis: In recipes, 'daiin' + [NOUN] = 'Take [Ingredient]'")
    
    recipes = voynich_data.get_section_text('recipes')
    herbal = voynich_data.get_section_text('herbal_a') # First half
    herbal.update(voynich_data.get_section_text('herbal_b'))
    
    potential_ingredients = []
    
    # Analyze Recipes specifically
    print("\nScanning RECIPE section for sentences starting with 'daiin'...")
    count = 0
    
    # Sorting to keep order
    sorted_folios = sorted(recipes.keys())
    
    for folio in sorted_folios:
        lines = recipes[folio]
        for loc, text in lines.items():
            clean = re.sub(r'[^\w\s.-]', '', text)
            words = [w for w in clean.split('.') if w]
            
            if not words: continue
            
            if words[0] == 'daiin':
                count += 1
                ingredient = words[1] if len(words) > 1 else "[NONE]"
                potential_ingredients.append(ingredient)
                if count <= 10: # Show first 10 examples
                    print(f"  {loc}: daiin + {ingredient}")

    print(f"Total 'daiin'-started lines in Recipes: {count}")
    
    # Analyze the extracted "Ingredients"
    ing_counts = Counter(potential_ingredients)
    print("\nTop Words following 'daiin' (Candidate Ingredients):")
    for w, c in ing_counts.most_common(10):
        print(f"  {w}: {c} times")
        
    # Check if these ingredients appear in Herbal section (Cross-Validation)
    print("\n[3] CROSS-VALIDATION: Do 'daiin' objects appear in Herbal Section?")
    
    valid_ingredients = []
    for ing, count in ing_counts.most_common(15):
        if ing in ["[NONE]", "[END]"]: continue
        
        # Search in herbal
        herbal_hits = 0
        herbal_pages = set()
        for h_folio, h_lines in herbal.items():
            for h_text in h_lines.values():
                if f".{ing}." in h_text or h_text.startswith(f"{ing}.") or h_text.endswith(f".{ing}"):
                    herbal_hits += 1
                    herbal_pages.add(h_folio)
        
        status = "✅ MATCH" if herbal_hits > 0 else "❌ NO MATCH"
        print(f"  {ing:<15} | Recipe Freq: {count:<3} | Herbal Hits: {herbal_hits:<3} | Pages: {len(herbal_pages)} | {status}")
        
        if herbal_hits > 0:
            valid_ingredients.append(ing)

    # Check specifically for the overlap
    print(f"\nPotential VALIDATED Ingredients (Recipe Object + Herbal Existence):")
    print(f"{', '.join(valid_ingredients)}")

if __name__ == "__main__":
    run_syntax_test()



