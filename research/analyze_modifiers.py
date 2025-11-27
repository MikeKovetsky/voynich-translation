import json
import re
from collections import defaultdict, Counter

def load_eva():
    lines = []
    with open('data/eva_ivtff.txt', 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            if '<f' in line:
                match = re.match(r'<(f\d+[rv]\d*)\.', line)
                if match:
                    folio = match.group(1)
                    text_start = line.find('>')
                    if text_start > -1:
                        text = line[text_start+1:].strip()
                        text = re.sub(r'\{[^}]*\}', '', text)
                        text = re.sub(r'[<>\[\]]', '', text)
                        words = text.replace('.', ' ').replace('-', ' ').replace('=', ' ').split()
                        words = [w.strip() for w in words if w.strip() and not w.startswith('!')]
                        if words:
                            lines.append((folio, words))
    return lines

def load_scholarly():
    with open('results/scholarly_master.json', 'r') as f:
        data = json.load(f)
    plant_map = {}
    
    for entry in data.get('new_vocabulary', []):
        plant = entry.get('latin', '')
        for folio in entry.get('folios', []):
            if folio not in plant_map:
                plant_map[folio] = []
            if plant and plant not in plant_map[folio]:
                plant_map[folio].append(plant)
    
    for plant, info in data.get('top_plants', {}).items():
        if plant in ['o\'neill', 'holm', 'beinecke digital library', 'jason davies voyager']:
            continue
        for folio in info.get('folios', []):
            if folio not in plant_map:
                plant_map[folio] = []
            if plant and plant not in plant_map[folio]:
                plant_map[folio].append(plant)
    
    return plant_map

def load_modifiers():
    with open('results/full_recipe_translation.json', 'r') as f:
        data = json.load(f)
    return data.get('modifier_words', {})

def is_herbal_page(folio):
    num_match = re.match(r'f(\d+)', folio)
    if not num_match:
        return False
    num = int(num_match.group(1))
    if num >= 1 and num <= 66:
        return True
    if num >= 87 and num <= 102:
        return True
    return False

def main():
    print("=== Track 96: Modifier Analysis (The Plant Hunt) ===\n")
    
    eva_lines = load_eva()
    plant_map = load_scholarly()
    modifiers = load_modifiers()
    
    top_modifiers = sorted(modifiers.items(), key=lambda x: -x[1])[:50]
    print(f"TOP 30 MODIFIERS (words following qok-):")
    print("-" * 50)
    for word, count in top_modifiers[:30]:
        print(f"  {word:15} : {count:3} occurrences")
    
    word_to_folios = defaultdict(list)
    folio_words = defaultdict(set)
    for folio, words in eva_lines:
        for word in words:
            folio_words[folio].add(word)
    
    for folio, words in folio_words.items():
        for word in words:
            word_to_folios[word].append(folio)
    
    print("\n\n=== CROSS-REFERENCE: Modifiers on Herbal Pages ===\n")
    
    results = []
    for word, recipe_count in top_modifiers:
        herbal_folios = [f for f in word_to_folios.get(word, []) if is_herbal_page(f)]
        unique_herbals = sorted(set(herbal_folios))
        
        plants_found = []
        for folio in unique_herbals:
            if folio in plant_map:
                plants_found.extend(plant_map[folio])
        plants_found = list(set(plants_found))
        
        specificity = 'UNKNOWN'
        if len(unique_herbals) == 0:
            specificity = 'NO_HERBAL_MATCH'
        elif len(unique_herbals) == 1:
            specificity = 'ULTRA_SPECIFIC'
        elif len(unique_herbals) <= 3:
            specificity = 'SPECIFIC'
        elif len(unique_herbals) <= 10:
            specificity = 'MODERATE'
        else:
            specificity = 'GENERIC'
        
        results.append({
            'word': word,
            'recipe_count': recipe_count,
            'herbal_pages': unique_herbals,
            'herbal_count': len(unique_herbals),
            'plants_identified': plants_found,
            'specificity': specificity
        })
    
    ultra_specific = [r for r in results if r['specificity'] == 'ULTRA_SPECIFIC']
    specific = [r for r in results if r['specificity'] == 'SPECIFIC']
    moderate = [r for r in results if r['specificity'] == 'MODERATE']
    generic = [r for r in results if r['specificity'] == 'GENERIC']
    no_match = [r for r in results if r['specificity'] == 'NO_HERBAL_MATCH']
    
    print("ULTRA-SPECIFIC (1 herbal page only) → Likely PLANT NAME:")
    print("-" * 60)
    for r in ultra_specific:
        plant_str = ', '.join(r['plants_identified']) if r['plants_identified'] else '?'
        print(f"  {r['word']:15} → {r['herbal_pages'][0]:8} = {plant_str}")
    
    print(f"\nSPECIFIC (2-3 herbal pages) → Likely PLANT NAME:")
    print("-" * 60)
    for r in specific:
        plant_str = ', '.join(r['plants_identified']) if r['plants_identified'] else '?'
        pages = ', '.join(r['herbal_pages'][:3])
        print(f"  {r['word']:15} → [{pages}] = {plant_str}")
    
    print(f"\nMODERATE (4-10 pages) → Possibly generic term:")
    print("-" * 60)
    for r in moderate[:15]:
        print(f"  {r['word']:15} → {r['herbal_count']:2} pages")
    
    print(f"\nGENERIC (>10 pages) → General botanical term:")
    print("-" * 60)
    for r in generic[:10]:
        print(f"  {r['word']:15} → {r['herbal_count']:2} pages")
    
    print("\n\n=== DISTRIBUTION ANALYSIS ===\n")
    print(f"  ULTRA_SPECIFIC (1 page)    : {len(ultra_specific):3} modifiers")
    print(f"  SPECIFIC (2-3 pages)       : {len(specific):3} modifiers")
    print(f"  MODERATE (4-10 pages)      : {len(moderate):3} modifiers")
    print(f"  GENERIC (>10 pages)        : {len(generic):3} modifiers")
    print(f"  NO_HERBAL_MATCH            : {len(no_match):3} modifiers")
    
    plant_links = {}
    for r in results:
        if r['specificity'] in ['ULTRA_SPECIFIC', 'SPECIFIC'] and r['plants_identified']:
            for plant in r['plants_identified']:
                if plant not in plant_links:
                    plant_links[plant] = []
                plant_links[plant].append({
                    'word': r['word'],
                    'pages': r['herbal_pages'],
                    'recipe_count': r['recipe_count'],
                    'confidence': 'HIGH' if r['specificity'] == 'ULTRA_SPECIFIC' else 'MEDIUM'
                })
    
    print("\n\n=== PLANT → VOYNICH WORD MAPPINGS ===\n")
    for plant, words in sorted(plant_links.items()):
        print(f"\n{plant.upper()}:")
        for w in words:
            conf = w['confidence']
            print(f"  → {w['word']:15} (pages: {', '.join(w['pages'])}, conf: {conf})")
    
    print("\n\n=== REVERSE ANALYSIS: Plant Pages → Unique Modifiers ===\n")
    
    all_modifiers = set(modifiers.keys())
    plant_specific_words = {}
    
    for folio, plants in sorted(plant_map.items()):
        if not is_herbal_page(folio):
            continue
        folio_words = set()
        for f, words in eva_lines:
            if f == folio:
                folio_words.update(words)
        
        mods_on_page = folio_words & all_modifiers
        
        specific_mods = []
        for mod in mods_on_page:
            mod_pages = [f for f in word_to_folios.get(mod, []) if is_herbal_page(f)]
            if len(set(mod_pages)) <= 3:
                specific_mods.append((mod, len(set(mod_pages)), modifiers.get(mod, 0)))
        
        if specific_mods and plants:
            plant_specific_words[folio] = {
                'plants': plants,
                'specific_modifiers': sorted(specific_mods, key=lambda x: -x[2])
            }
    
    print("Plant Pages with Specific Modifiers:")
    print("-" * 70)
    for folio, data in sorted(plant_specific_words.items()):
        plants = ', '.join(data['plants'])
        mods = data['specific_modifiers'][:5]
        if mods:
            mod_str = ', '.join([f"{m[0]}({m[2]}x)" for m in mods])
            print(f"  {folio:8} = {plants:20} → {mod_str}")
    
    output = {
        'summary': {
            'total_modifiers_analyzed': len(results),
            'ultra_specific': len(ultra_specific),
            'specific': len(specific),
            'moderate': len(moderate),
            'generic': len(generic),
            'no_herbal_match': len(no_match),
            'plants_linked': len(plant_links),
            'plants_with_specific_mods': len(plant_specific_words)
        },
        'plant_links': plant_links,
        'plant_specific_words': plant_specific_words,
        'modifier_analysis': results,
        'methodology': (
            "Words following qok- in recipes were cross-referenced with herbal pages. "
            "If a modifier appears on only 1-3 herbal pages, it likely names that plant."
        )
    }
    
    with open('results/modifier_plant_links.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    with open('results/modifier_report.md', 'w') as f:
        f.write("# Track 96: Modifier Analysis Report\n\n")
        f.write("## Goal\n")
        f.write("Identify the source plants (words following `qok-` = \"of [plant]\").\n\n")
        
        f.write("## Methodology\n")
        f.write("1. Extract top modifiers from recipe section\n")
        f.write("2. Cross-reference each modifier with herbal pages\n")
        f.write("3. If modifier appears on few pages → likely plant name\n")
        f.write("4. If modifier appears on many pages → generic term\n\n")
        
        f.write("## Distribution Summary\n\n")
        f.write("| Category | Count | Interpretation |\n")
        f.write("|----------|-------|----------------|\n")
        f.write(f"| ULTRA_SPECIFIC | {len(ultra_specific)} | Single page → Plant name |\n")
        f.write(f"| SPECIFIC | {len(specific)} | 2-3 pages → Plant name |\n")
        f.write(f"| MODERATE | {len(moderate)} | 4-10 pages → Possibly generic |\n")
        f.write(f"| GENERIC | {len(generic)} | >10 pages → General term |\n")
        f.write(f"| NO_MATCH | {len(no_match)} | Recipe-only terms |\n\n")
        
        f.write("## Key Findings: Plant Name Candidates\n\n")
        f.write("### ULTRA-SPECIFIC (HIGH confidence)\n\n")
        f.write("| Voynich Word | Herbal Page | Expert Plant ID |\n")
        f.write("|--------------|-------------|------------------|\n")
        for r in ultra_specific:
            plant_str = ', '.join(r['plants_identified']) if r['plants_identified'] else '?'
            f.write(f"| `{r['word']}` | {r['herbal_pages'][0]} | {plant_str} |\n")
        
        f.write("\n### SPECIFIC (MEDIUM confidence)\n\n")
        f.write("| Voynich Word | Herbal Pages | Expert Plant ID |\n")
        f.write("|--------------|--------------|------------------|\n")
        for r in specific:
            plant_str = ', '.join(r['plants_identified']) if r['plants_identified'] else '?'
            pages = ', '.join(r['herbal_pages'][:3])
            f.write(f"| `{r['word']}` | {pages} | {plant_str} |\n")
        
        f.write("\n## Plant → Voynich Mappings\n\n")
        for plant, words in sorted(plant_links.items()):
            f.write(f"\n### {plant.title()}\n\n")
            for w in words:
                f.write(f"- `{w['word']}` (pages: {', '.join(w['pages'])}, confidence: {w['confidence']})\n")
        
        f.write("\n## Reverse Analysis: Plant Pages → Specific Modifiers\n\n")
        f.write("For each known plant page, which modifiers appear specifically (on ≤3 pages)?\n\n")
        f.write("| Folio | Expert Plant ID | Specific Modifiers |\n")
        f.write("|-------|-----------------|--------------------|\n")
        for folio, data in sorted(plant_specific_words.items()):
            plants = ', '.join(data['plants'][:2])
            mods = data['specific_modifiers'][:3]
            mod_str = ', '.join([f"`{m[0]}`" for m in mods])
            f.write(f"| {folio} | {plants} | {mod_str} |\n")
        
        f.write("\n## Conclusion\n\n")
        plant_count = len(plant_links)
        specific_count = len(ultra_specific) + len(specific)
        reverse_count = len(plant_specific_words)
        f.write(f"**{specific_count} modifier words** show page-specific distribution, suggesting they are **plant names**.\n\n")
        f.write(f"**{plant_count} plants** have direct matches via forward analysis.\n\n")
        f.write(f"**{reverse_count} plant pages** have specific modifiers that could be plant names.\n\n")
        f.write("### Key Insight\n\n")
        f.write("Most top modifiers (`chedy`, `chey`, etc.) are **GENERIC** - they appear on 20-60+ pages. ")
        f.write("These likely represent common botanical terms (leaf, root, flower) rather than plant names.\n\n")
        f.write("The **ULTRA_SPECIFIC** and **SPECIFIC** modifiers are rare but valuable - they likely ARE plant names.\n")
    
    print("\n\nOUTPUT FILES:")
    print("  → results/modifier_plant_links.json")
    print("  → results/modifier_report.md")
    print("\nDone!")

if __name__ == '__main__':
    main()



