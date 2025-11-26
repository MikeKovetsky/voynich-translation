"""
Track 89: Low-Leakage Ingredient Analysis
Focus on words with <20% leakage into non-herbal sections.
These are the BEST candidates for specific plants/ingredients.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from voynich_data import get_eva_pages, FOLIO_SECTIONS

RESULTS_DIR = Path("results")

HERBAL_FOLIOS = set(FOLIO_SECTIONS['herbal_a'] + FOLIO_SECTIONS['herbal_b'])
RECIPE_FOLIOS = set(FOLIO_SECTIONS['recipes'])
PHARMA_FOLIOS = set(FOLIO_SECTIONS['pharmaceutical'])
ASTRO_FOLIOS = set(FOLIO_SECTIONS['astronomical'])
BIO_FOLIOS = set(FOLIO_SECTIONS['biological'])


def load_expert_ids():
    """Load all expert plant identifications from quire files."""
    expert_data = {}
    for i in range(1, 9):
        quire_file = RESULTS_DIR / f"quire_{i:02d}_{i+1:02d}_plants.json"
        if quire_file.exists():
            with open(quire_file) as f:
                data = json.load(f)
                for folio in data.get('folios', []):
                    fid = folio['folio'].lower()
                    expert_data[fid] = {
                        'elv_id': folio.get('elv_id'),
                        'thp_id': folio.get('thp_id'),
                        'visual_elements': folio.get('visual_elements', []),
                        'description': folio.get('description', '')
                    }
    return expert_data


def get_word_locations(target_words):
    """Find all folios where target words appear."""
    pages = get_eva_pages()
    word_locs = {w: defaultdict(int) for w in target_words}
    
    for folio, lines in pages.items():
        folio_lower = folio.lower()
        for line_loc, text in lines.items():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words = re.split(r'[.\-=,\s]', text_clean)
            for word in words:
                if word in target_words:
                    word_locs[word][folio_lower] += 1
    
    return word_locs


def classify_folio(folio):
    """Classify folio into section."""
    f = folio.lower()
    if f in HERBAL_FOLIOS:
        return 'herbal'
    elif f in RECIPE_FOLIOS:
        return 'recipe'
    elif f in PHARMA_FOLIOS:
        return 'pharma'
    elif f in ASTRO_FOLIOS:
        return 'astro'
    elif f in BIO_FOLIOS:
        return 'bio'
    else:
        return 'other'


def calc_leakage(word_locs):
    """Calculate leakage percentage (non-herbal occurrences)."""
    result = {}
    for word, folios in word_locs.items():
        herbal_count = 0
        non_herbal_count = 0
        for folio, count in folios.items():
            section = classify_folio(folio)
            if section == 'herbal':
                herbal_count += count
            else:
                non_herbal_count += count
        total = herbal_count + non_herbal_count
        leakage = non_herbal_count / total if total > 0 else 0
        result[word] = {
            'herbal': herbal_count,
            'non_herbal': non_herbal_count,
            'total': total,
            'leakage': leakage
        }
    return result


def analyze_word(word, word_locs, expert_data):
    """Analyze a single word for visual correlations."""
    folios = word_locs[word]
    
    herbal_folios = []
    recipe_folios = []
    other_folios = []
    
    visual_counts = defaultdict(int)
    plant_ids = defaultdict(int)
    
    for folio, count in folios.items():
        section = classify_folio(folio)
        
        if section == 'herbal':
            herbal_folios.append((folio, count))
            if folio in expert_data:
                exp = expert_data[folio]
                for elem in exp.get('visual_elements', []):
                    visual_counts[elem] += count
                if exp.get('elv_id'):
                    plant_id = exp['elv_id'].split(',')[0].split('?')[0].strip().lower()
                    if plant_id:
                        plant_ids[plant_id] += count
        elif section == 'recipe':
            recipe_folios.append((folio, count))
        else:
            other_folios.append((folio, count))
    
    total_herbal = sum(c for _, c in herbal_folios)
    
    visual_pcts = {}
    for elem, cnt in visual_counts.items():
        visual_pcts[elem] = cnt / total_herbal if total_herbal > 0 else 0
    
    dominant_visual = max(visual_pcts.items(), key=lambda x: x[1]) if visual_pcts else (None, 0)
    dominant_plant = max(plant_ids.items(), key=lambda x: x[1]) if plant_ids else (None, 0)
    
    return {
        'word': word,
        'herbal_folios': sorted(herbal_folios, key=lambda x: -x[1]),
        'recipe_folios': sorted(recipe_folios, key=lambda x: -x[1]),
        'other_folios': sorted(other_folios, key=lambda x: -x[1]),
        'visual_correlation': dict(visual_pcts),
        'dominant_visual': dominant_visual[0],
        'dominant_visual_pct': dominant_visual[1],
        'plant_ids': dict(plant_ids),
        'dominant_plant': dominant_plant[0],
        'total_herbal': total_herbal,
        'total_recipe': sum(c for _, c in recipe_folios),
        'total_other': sum(c for _, c in other_folios)
    }


def find_golden_intersection(pages):
    """Find words that appear in 'golden intersection' (after daiin AND ol)."""
    golden_words = defaultdict(int)
    
    for folio, lines in pages.items():
        for line_loc, text in lines.items():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words = re.split(r'[.\-=,\s]', text_clean)
            words = [w for w in words if w]
            
            for i, word in enumerate(words):
                if word in ('daiin', 'dain', 'daim'):
                    if i + 1 < len(words):
                        golden_words[words[i + 1]] += 1
                if word == 'ol':
                    if i + 1 < len(words):
                        golden_words[words[i + 1]] += 1
    
    return dict(sorted(golden_words.items(), key=lambda x: -x[1])[:100])


def analyze_zero_leakage(candidates, pages, expert_data):
    """Deep analysis of zero/very-low leakage candidates."""
    results = []
    
    for cand in candidates:
        if cand['leakage'] > 0.10:
            continue
            
        word = cand['word']
        word_locs = defaultdict(list)
        
        for folio, lines in pages.items():
            for line_loc, text in lines.items():
                text_clean = re.sub(r'[!?<>@$\d]', '', text)
                words = re.split(r'[.\-=,\s]', text_clean)
                if word in words:
                    word_locs[folio.lower()].append(line_loc)
        
        herbal_pages = []
        recipe_pages = []
        visual_elements = defaultdict(int)
        plant_names = defaultdict(int)
        
        for folio, locs in word_locs.items():
            section = classify_folio(folio)
            if section == 'herbal':
                herbal_pages.append((folio, len(locs)))
                if folio in expert_data:
                    for elem in expert_data[folio].get('visual_elements', []):
                        visual_elements[elem] += len(locs)
                    elv = expert_data[folio].get('elv_id', '')
                    if elv:
                        plant = elv.split(',')[0].split('?')[0].strip().lower()
                        if plant:
                            plant_names[plant] += len(locs)
            elif section == 'recipe':
                recipe_pages.append((folio, len(locs)))
        
        total_herbal = sum(c for _, c in herbal_pages)
        
        if total_herbal == 0:
            continue
            
        visual_pcts = {k: v/total_herbal for k, v in visual_elements.items()}
        dominant = max(visual_pcts.items(), key=lambda x: x[1]) if visual_pcts else (None, 0)
        
        meaning_map = {
            'roots': 'root/underground',
            'flowers': 'flower/blossom',
            'leaves': 'leaf/foliage',
            'stem': 'stem/stalk',
            'fruits': 'fruit/seed',
            'stars': 'star-shaped'
        }
        
        confidence = 'HIGH' if dominant[1] >= 0.80 else 'MEDIUM' if dominant[1] >= 0.60 else 'LOW'
        
        results.append({
            'word': word,
            'herbal_count': cand['herbal'],
            'recipe_count': cand['recipe'],
            'leakage': cand['leakage'],
            'herbal_pages': sorted(herbal_pages, key=lambda x: -x[1]),
            'recipe_pages': sorted(recipe_pages, key=lambda x: -x[1]),
            'visual_correlation': dict(visual_pcts),
            'dominant_visual': dominant[0],
            'dominant_pct': dominant[1],
            'plant_associations': dict(plant_names),
            'inferred_meaning': meaning_map.get(dominant[0], 'UNKNOWN'),
            'confidence': confidence
        })
    
    return sorted(results, key=lambda x: (-x['dominant_pct'], x['leakage']))


def find_low_leakage_candidates(pages, expert_data, max_leakage=0.20):
    """Find all words with low leakage to non-herbal sections."""
    word_section_counts = defaultdict(lambda: defaultdict(int))
    
    for folio, lines in pages.items():
        section = classify_folio(folio)
        for line_loc, text in lines.items():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words = re.split(r'[.\-=,\s]', text_clean)
            for word in words:
                if word and len(word) > 1:
                    word_section_counts[word][section] += 1
    
    low_leakage = []
    for word, sections in word_section_counts.items():
        herbal = sections.get('herbal', 0)
        recipe = sections.get('recipe', 0)
        total = sum(sections.values())
        non_herbal = total - herbal
        
        if herbal >= 5 and recipe >= 1:
            leakage = (total - herbal - recipe) / total if total > 0 else 1
            if leakage <= max_leakage:
                low_leakage.append({
                    'word': word,
                    'herbal': herbal,
                    'recipe': recipe,
                    'other': non_herbal - recipe,
                    'total': total,
                    'leakage': leakage
                })
    
    return sorted(low_leakage, key=lambda x: x['leakage'])


def infer_meaning(analysis):
    """Infer meaning based on visual correlation."""
    visual = analysis.get('dominant_visual')
    pct = analysis.get('dominant_visual_pct', 0)
    
    if not visual or pct < 0.5:
        return 'UNKNOWN', 'LOW'
    
    meanings = {
        'roots': ('root/underground part', 'MEDIUM'),
        'flowers': ('flower/blossom', 'MEDIUM'),
        'leaves': ('leaf/foliage', 'MEDIUM'),
        'stem': ('stem/stalk', 'MEDIUM'),
        'fruits': ('fruit/seed', 'MEDIUM'),
        'stars': ('star-shaped/radial', 'LOW'),
        'figures': ('anthropomorphic', 'LOW')
    }
    
    if pct >= 0.8:
        base_meaning, _ = meanings.get(visual, ('UNKNOWN', 'LOW'))
        return base_meaning, 'HIGH'
    
    return meanings.get(visual, ('UNKNOWN', 'LOW'))


def main():
    print("=" * 60)
    print("TRACK 89: LOW-LEAKAGE INGREDIENT ANALYSIS")
    print("=" * 60)
    
    expert_data = load_expert_ids()
    print(f"\nLoaded {len(expert_data)} expert plant identifications")
    
    pages = get_eva_pages()
    print(f"Loaded {len(pages)} folios")
    
    target_words = ['char', 'chl', 'ar', 'chol', 'chor', 'kal', 'kar']
    word_locs = get_word_locations(target_words)
    
    print("\n" + "=" * 60)
    print("TASK 1: LEAKAGE CALCULATION")
    print("=" * 60)
    
    leakage = calc_leakage(word_locs)
    for word, stats in sorted(leakage.items(), key=lambda x: x[1]['leakage']):
        print(f"  {word}: {stats['herbal']} herbal, {stats['non_herbal']} other, "
              f"leakage={stats['leakage']*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("TASK 2: VISUAL CORRELATION ANALYSIS")
    print("=" * 60)
    
    analyses = {}
    for word in target_words:
        if word_locs[word]:
            analysis = analyze_word(word, word_locs, expert_data)
            analyses[word] = analysis
            
            print(f"\n--- {word.upper()} ---")
            print(f"  Herbal: {analysis['total_herbal']}, Recipe: {analysis['total_recipe']}, "
                  f"Other: {analysis['total_other']}")
            print(f"  Top herbal folios: {analysis['herbal_folios'][:5]}")
            print(f"  Visual correlation:")
            for elem, pct in sorted(analysis['visual_correlation'].items(), 
                                   key=lambda x: -x[1])[:5]:
                print(f"    {elem}: {pct*100:.1f}%")
            print(f"  Dominant: {analysis['dominant_visual']} ({analysis['dominant_visual_pct']*100:.1f}%)")
            print(f"  Top plants: {list(analysis['plant_ids'].items())[:3]}")
            
            meaning, conf = infer_meaning(analysis)
            print(f"  → INFERRED: {meaning} (confidence: {conf})")
    
    print("\n" + "=" * 60)
    print("TASK 3: FIND ALL LOW-LEAKAGE CANDIDATES")
    print("=" * 60)
    
    low_leakage_candidates = find_low_leakage_candidates(pages, expert_data)
    print(f"\nFound {len(low_leakage_candidates)} low-leakage words (herbal+recipe, ≤20% other)")
    print("\nTop 20 lowest leakage:")
    for i, cand in enumerate(low_leakage_candidates[:20]):
        print(f"  {i+1}. {cand['word']}: H={cand['herbal']}, R={cand['recipe']}, "
              f"O={cand['other']}, leak={cand['leakage']*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("TASK 4: GOLDEN INTERSECTION WORDS")
    print("=" * 60)
    
    golden = find_golden_intersection(pages)
    print("\nWords following 'daiin' or 'ol' (grammar frame positions):")
    for word, count in list(golden.items())[:15]:
        print(f"  {word}: {count}")
    
    print("\n" + "=" * 60)
    print("TASK 5: ZERO/LOW LEAKAGE DEEP ANALYSIS")
    print("=" * 60)
    
    zero_leakage = analyze_zero_leakage(low_leakage_candidates, pages, expert_data)
    print(f"\nAnalyzed {len(zero_leakage)} zero/low-leakage candidates (≤10%)")
    
    verified = []
    for z in zero_leakage:
        print(f"\n  {z['word'].upper()} [leakage: {z['leakage']*100:.1f}%]")
        print(f"    Herbal: {z['herbal_count']}, Recipe: {z['recipe_count']}")
        print(f"    Pages: {z['herbal_pages'][:3]}")
        print(f"    Dominant: {z['dominant_visual']} ({z['dominant_pct']*100:.1f}%)")
        print(f"    Plants: {list(z['plant_associations'].items())[:3]}")
        print(f"    → MEANING: {z['inferred_meaning']} [{z['confidence']}]")
        
        verified.append({
            'word': z['word'],
            'herbal_count': z['herbal_count'],
            'recipe_count': z['recipe_count'],
            'leakage': z['leakage'],
            'dominant_visual': z['dominant_visual'],
            'visual_pct': z['dominant_pct'],
            'top_plants': list(z['plant_associations'].items())[:3],
            'inferred_meaning': z['inferred_meaning'],
            'confidence': z['confidence'],
            'herbal_pages': z['herbal_pages'][:5],
            'recipe_pages': z['recipe_pages'][:5]
        })
    
    results = {
        'target_word_analysis': analyses,
        'leakage_stats': leakage,
        'low_leakage_candidates': low_leakage_candidates[:100],
        'golden_intersection': golden,
        'verified_ingredients': verified,
        'summary': {
            'total_low_leakage': len(low_leakage_candidates),
            'verified_count': len(verified),
            'expert_folios': len(expert_data)
        }
    }
    
    out_file = RESULTS_DIR / "low_leakage_analysis.json"
    with open(out_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n\nSaved to {out_file}")
    
    print("\n" + "=" * 60)
    print("REPORT SUMMARY")
    print("=" * 60)
    
    report_lines = [
        "# Track 89: Low-Leakage Ingredient Analysis",
        "",
        "## Methodology",
        "Focus on words with <20% leakage into non-herbal sections.",
        "Cross-reference with visual elements (roots, flowers, leaves) on expert-identified pages.",
        "",
        "## Key Findings",
        "",
        "### Target Word Analysis",
        ""
    ]
    
    for word, analysis in analyses.items():
        meaning, conf = infer_meaning(analysis)
        report_lines.append(f"#### `{word}`")
        report_lines.append(f"- Herbal: {analysis['total_herbal']}, Recipe: {analysis['total_recipe']}")
        report_lines.append(f"- Dominant visual: **{analysis['dominant_visual']}** ({analysis['dominant_visual_pct']*100:.1f}%)")
        report_lines.append(f"- Top plants: {list(analysis['plant_ids'].items())[:3]}")
        report_lines.append(f"- **Inferred meaning: {meaning}** [{conf}]")
        report_lines.append("")
    
    report_lines.extend([
        "### Verified Ingredients (Zero/Low Leakage ≤10%)",
        "",
        "| Word | Herbal | Recipe | Leakage | Visual | Meaning | Confidence |",
        "|------|--------|--------|---------|--------|---------|------------|"
    ])
    
    for v in sorted(verified, key=lambda x: (-x['visual_pct'], x['leakage']))[:25]:
        vis_str = f"{v['dominant_visual']} ({v['visual_pct']*100:.0f}%)" if v['dominant_visual'] else "N/A"
        report_lines.append(
            f"| {v['word']} | {v['herbal_count']} | {v['recipe_count']} | "
            f"{v['leakage']*100:.1f}% | {vis_str} | "
            f"{v['inferred_meaning']} | {v['confidence']} |"
        )
    
    report_lines.extend([
        "",
        "### High-Confidence Plant Part Vocabulary",
        "",
        "Based on visual correlation analysis:",
        ""
    ])
    
    high_conf = [v for v in verified if v['confidence'] == 'HIGH']
    by_meaning = defaultdict(list)
    for v in high_conf:
        by_meaning[v['inferred_meaning']].append(v)
    
    for meaning, words in sorted(by_meaning.items()):
        report_lines.append(f"**{meaning}**: {', '.join(w['word'] for w in words)}")
        for w in words[:3]:
            if w['top_plants']:
                report_lines.append(f"  - `{w['word']}`: {w['top_plants']}")
        report_lines.append("")
    
    report_lines.extend([
        "",
        "## Summary Statistics",
        f"- Expert-identified folios: {len(expert_data)}",
        f"- Low-leakage candidates: {len(low_leakage_candidates)}",
        f"- Verified ingredients: {len(verified)}",
        "",
        "## Recommendations",
        "1. Words with HIGH confidence visual correlation should be added to dictionary",
        "2. Focus on words appearing in 'Golden Intersection' (after daiin/ol)",
        "3. Cross-validate with recipe context before finalizing meanings"
    ])
    
    report_file = RESULTS_DIR / "low_leakage_report.md"
    with open(report_file, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"Report saved to {report_file}")


if __name__ == "__main__":
    main()



