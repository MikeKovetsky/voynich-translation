
import voynich_data
import re
from collections import Counter

def clarify_findings():
    print("=== CLARIFICATION CHECK ===")
    
    # Load sections
    recipes = voynich_data.get_section_text('recipes')
    sections = {
        'Herbal': voynich_data.get_section_text('herbal_a'),
        'Recipes': recipes,
        'Astrology': voynich_data.get_section_text('astronomical'),
        'Biology': voynich_data.get_section_text('biological'),
        'Cosmology': voynich_data.get_section_text('pharmaceutical')
    }
    herbal_b = voynich_data.get_section_text('herbal_b')
    sections['Herbal'].update(herbal_b)

    # --- Q1: daiin + qok check ---
    print("\n[Q1] Checking 'daiin' + 'qok-' adjacency in Recipes...")
    daiin_total = 0
    daiin_qok = 0
    
    for folio in recipes.values():
        for text in folio.values():
            clean = re.sub(r'[^\w\s.-]', '', text)
            words = [w for w in clean.split('.') if w]
            
            for i, w in enumerate(words):
                if w == 'daiin':
                    daiin_total += 1
                    if i < len(words) - 1:
                        next_w = words[i+1]
                        if next_w.startswith('qok') or next_w.startswith('4oh'):
                            daiin_qok += 1
                            print(f"  Found: daiin + {next_w}")

    print(f"  Total 'daiin' occurrences: {daiin_total}")
    print(f"  'daiin' followed by 'qok-' word: {daiin_qok}")
    print(f"  Percentage: {(daiin_qok/daiin_total)*100:.2f}%")
    
    # --- Q2: Golden Intersection ---
    print("\n[Q2] Generating Golden Intersection List...")
    daiin_followers = set()
    ol_followers = set()
    
    for folio in recipes.values():
        for text in folio.values():
            clean = re.sub(r'[^\w\s.-]', '', text)
            words = [w for w in clean.split('.') if w]
            
            for i, w in enumerate(words):
                if i < len(words) - 1:
                    next_w = words[i+1]
                    if w == 'daiin':
                        daiin_followers.add(next_w)
                    elif w == 'ol':
                        ol_followers.add(next_w)
                        
    intersection = daiin_followers.intersection(ol_followers)
    print(f"  Words following 'daiin': {len(daiin_followers)}")
    print(f"  Words following 'ol': {len(ol_followers)}")
    print(f"  Intersection Size: {len(intersection)}")
    print(f"  Full Intersection List: {sorted(list(intersection))}")

    # --- Q3: Distribution / Leakage ---
    print("\n[Q3] Distribution of Intersection Words (Leakage Check)...")
    print(f"{'WORD':<15} | {'HERBAL':<6} | {'RECIPE':<6} | {'ASTRO':<6} | {'BIO':<6} | {'COSMO':<6} | {'% NON-PLANT'}")
    print("-" * 80)
    
    for word in sorted(list(intersection)):
        counts = {s: 0 for s in sections}
        total = 0
        
        for sec_name, sec_data in sections.items():
            for folio in sec_data.values():
                for text in folio.values():
                    if f".{word}." in text or text.startswith(f"{word}.") or text.endswith(f".{word}"):
                        counts[sec_name] += 1
                        total += 1
        
        non_plant_count = counts['Astrology'] + counts['Biology'] + counts['Cosmology']
        leakage_pct = (non_plant_count / total * 100) if total > 0 else 0.0
        
        print(f"{word:<15} | {counts['Herbal']:<6} | {counts['Recipes']:<6} | {counts['Astrology']:<6} | {counts['Biology']:<6} | {counts['Cosmology']:<6} | {leakage_pct:.1f}%")

if __name__ == "__main__":
    clarify_findings()
