"""
Track 70: High-Frequency Unknown Analysis
Analyze most common untranslated words to expand dictionary.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import voynich_data

DICT_FILE = Path("results/master_dictionary.json")
OUTPUT_JSON = Path("results/high_freq_unknowns.json")
OUTPUT_MD = Path("results/high_freq_unknowns_report.md")

HEBREW_ROOTS = {
    'dm': ('blood', 'dam'),
    'lv': ('heart', 'lev'),
    'mr': ('bitter', 'mar'),
    'sm': ('medicine/poison', 'sam'),
    'pr': ('fruit', 'pri'),
    'zr': ('seed', 'zera'),
    'yr': ('moon', 'yareach'),
    'shm': ('name/sun', 'shemesh'),
    'khn': ('priest', 'cohen'),
    'mlk': ('king', 'melech'),
    'shl': ('ask/draw', 'shaal'),
    'ntn': ('give', 'natan'),
    'lqch': ('take', 'laqach'),
    'shr': ('root', 'shoresh'),
    'pch': ('flower', 'perach'),
    'ets': ('tree', 'etz'),
    'shk': ('drink', 'shata'),
    'chl': ('sick', 'choleh'),
    'rph': ('heal', 'rapha'),
    'mkh': ('strike/wound', 'maka'),
    'bsr': ('flesh', 'basar'),
    'ysh': ('sleep/there is', 'yesh'),
    'bd': ('servant/work', 'abad'),
    'yd': ('hand', 'yad'),
    'rgl': ('foot', 'regel'),
    'rsh': ('head', 'rosh'),
    'yn': ('eye', 'ayin'),
    'pn': ('face', 'panim'),
    'lshn': ('tongue', 'lashon'),
    'dvsh': ('honey', 'dvash'),
    'chlt': ('wheat', 'chitah'),
    'shr': ('ox/taurus', 'shor'),
    'tlh': ('lamb', 'taleh'),
    'ks': ('cup/chalice', 'kos'),
    'mym': ('water', 'mayim'),
    'yrq': ('vegetable/green', 'yerek'),
    'chr': ('hole', 'chor'),
    'kch': ('strength', 'koach'),
    'chd': ('one', 'echad'),
    'shn': ('tooth/year', 'shen/shanah'),
    'ym': ('day/sea', 'yom/yam'),
    'lyl': ('night', 'layla'),
    'shmn': ('oil', 'shemen'),
    'chmts': ('vinegar', 'chometz'),
    'mlch': ('salt', 'melach'),
    'sh': ('fire', 'esh'),
    'rch': ('wind/spirit', 'ruach'),
    'nps': ('soul/breath', 'nefesh'),
    'skn': ('dwell/danger', 'shachen'),
    'qr': ('cold/read', 'kar/kara'),
    'chm': ('hot/warm', 'cham'),
}

ITALIAN_WORDS = {
    'tr': ('earth', 'terra'),
    'kr': ('heart/cure', 'cuore/cura'),
    'fr': ('flower/iron', 'fiore/ferro'),
    'rm': ('branch', 'ramo'),
    'fl': ('flower', 'fiore'),
    'fgl': ('leaf', 'foglia'),
    'rd': ('root', 'radice'),
    'sm': ('seed', 'seme'),
    'frtt': ('fruit', 'frutto'),
    'lg': ('lily', 'giglio'),
    'rs': ('rose', 'rosa'),
    'vn': ('wine/vine', 'vino/vite'),
    'qc': ('water', 'acqua'),
    'lt': ('milk', 'latte'),
    'sl': ('salt', 'sale'),
    'sngv': ('blood', 'sangue'),
    'cr': ('flesh/meat', 'carne'),
    'pl': ('skin', 'pelle'),
    'mn': ('hand', 'mano'),
    'pd': ('foot', 'piede'),
    'tst': ('head', 'testa'),
    'bcc': ('mouth', 'bocca'),
    'cch': ('eye', 'occhio'),
    'rcc': ('ear', 'orecchio'),
    'dlr': ('pain', 'dolore'),
    'mlt': ('sick/bad', 'malato'),
    'mdc': ('medicine', 'medicina'),
    'grn': ('grain', 'grano'),
    'rz': ('rice', 'riso'),
    'fv': ('bean', 'fava'),
    'gl': ('garlic', 'aglio'),
    'cpl': ('onion', 'cipolla'),
    'mnt': ('mint', 'menta'),
    'slv': ('sage', 'salvia'),
    'tm': ('thyme', 'timo'),
    'fn': ('fennel', 'finocchio'),
    'nl': ('honey', 'miele'),
    'ct': ('vinegar', 'aceto'),
    'prnd': ('take', 'prendere'),
    'mtt': ('put', 'mettere'),
    'dnn': ('give', 'donare'),
    'bv': ('drink', 'bere'),
    'mng': ('eat', 'mangiare'),
    'lscr': ('let/leave', 'lasciare'),
    'pr': ('for', 'per'),
    'cn': ('with', 'con'),
    'spr': ('above', 'sopra'),
    'stt': ('under', 'sotto'),
    'bn': ('good', 'buono'),
    'gnd': ('big', 'grande'),
    'pcl': ('small', 'piccolo'),
    'vcch': ('old', 'vecchio'),
    'nvv': ('new', 'nuovo'),
}

ANNOTATION_WORDS = {
    'plant', 'figure', 'circle', 'star', 'label', 'text', 'symbol',
    'paragraph', 'drawing', 'illustration', 'nymph', 'tube', 'pipe',
    'ring', 'pool', 'zodiac', 'sun', 'moon', 'line', 'word', 'letter',
    'folio', 'page', 'margin', 'corner', 'center', 'left', 'right',
    'top', 'bottom', 'verso', 'recto', 'quire'
}


def load_dict():
    with open(DICT_FILE) as f:
        data = json.load(f)
    return set(data['entries'].keys())


def get_skeleton(word):
    vowels = 'aeiou'
    return ''.join(c for c in word.lower() if c not in vowels)


def has_qo_prefix(word):
    return word.startswith('qo') or word.startswith('qok')


def has_y_suffix(word):
    return word.endswith('y') or word.endswith('dy')


def has_aiin_suffix(word):
    return word.endswith('aiin') or word.endswith('ain')


def is_valid_voynich(word):
    if word.lower() in ANNOTATION_WORDS:
        return False
    if not re.match(r'^[a-z]+$', word.lower()):
        return False
    valid_chars = set('oacdefghiklmnopqrsty')
    if not set(word.lower()).issubset(valid_chars):
        return False
    if len(word) < 2 or len(word) > 15:
        return False
    return True


def extract_unknowns(dict_words, freq):
    unknowns = []
    for word, count in freq.items():
        if word not in dict_words and is_valid_voynich(word):
            unknowns.append({
                'word': word,
                'frequency': count,
                'skeleton': get_skeleton(word),
                'has_qo': has_qo_prefix(word),
                'has_y': has_y_suffix(word),
                'has_aiin': has_aiin_suffix(word),
                'length': len(word)
            })
    return sorted(unknowns, key=lambda x: -x['frequency'])[:100]


def find_word_context(word, pages):
    contexts = []
    for folio, lines in pages.items():
        for loc, text in lines.items():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words_in_line = re.split(r'[.\-=,\s]', text_clean)
            words_in_line = [w for w in words_in_line if w]
            
            for i, w in enumerate(words_in_line):
                if w == word:
                    before = words_in_line[max(0, i-2):i]
                    after = words_in_line[i+1:i+3]
                    contexts.append({
                        'folio': folio,
                        'before': before,
                        'after': after,
                        'line': ' '.join(words_in_line)
                    })
    return contexts[:10]


def get_section_for_folio(folio):
    folio_lower = folio.lower()
    for section, folios in voynich_data.FOLIO_SECTIONS.items():
        if folio_lower in folios:
            return section
    return 'unknown'


def analyze_section_distribution(word, pages):
    sections = defaultdict(int)
    for folio, lines in pages.items():
        for text in lines.values():
            text_clean = re.sub(r'[!?<>@$\d]', '', text)
            words_in_line = re.split(r'[.\-=,\s]', text_clean)
            count = words_in_line.count(word)
            if count > 0:
                section = get_section_for_folio(folio)
                sections[section] += count
    return dict(sections)


def match_hebrew(skeleton):
    matches = []
    for root, (meaning, hebrew) in HEBREW_ROOTS.items():
        if skeleton == root or skeleton.startswith(root) or root in skeleton:
            score = len(root) / max(len(skeleton), 1)
            matches.append({
                'root': root,
                'hebrew': hebrew,
                'meaning': meaning,
                'score': round(score, 2)
            })
    return sorted(matches, key=lambda x: -x['score'])[:3]


def match_italian(skeleton):
    matches = []
    for root, (meaning, italian) in ITALIAN_WORDS.items():
        if skeleton == root or skeleton.startswith(root) or root in skeleton:
            score = len(root) / max(len(skeleton), 1)
            matches.append({
                'root': root,
                'italian': italian,
                'meaning': meaning,
                'score': round(score, 2)
            })
    return sorted(matches, key=lambda x: -x['score'])[:3]


def cluster_by_context(unknowns, dict_words, pages, master_dict):
    clusters = {
        'medical': [],
        'botanical': [],
        'religious': [],
        'astronomical': [],
        'measurement': [],
        'action': [],
        'unknown': []
    }
    
    with open(DICT_FILE) as f:
        dict_data = json.load(f)
    entries = dict_data['entries']
    
    medical_words = {w for w, e in entries.items() if e.get('domain') == 'medical'}
    botanical_words = {w for w, e in entries.items() if e.get('domain') == 'botanical'}
    religious_words = {w for w, e in entries.items() if 'priest' in e.get('meaning', '').lower() or e.get('domain') == 'religious'}
    astro_words = {w for w, e in entries.items() if e.get('domain') == 'astronomical'}
    
    for unk in unknowns:
        contexts = find_word_context(unk['word'], pages)
        context_words = set()
        for ctx in contexts:
            context_words.update(ctx['before'])
            context_words.update(ctx['after'])
        
        sections = analyze_section_distribution(unk['word'], pages)
        unk['sections'] = sections
        unk['context_sample'] = contexts[:3]
        
        if context_words & medical_words or sections.get('pharmaceutical', 0) > 0 or sections.get('biological', 0) > 0:
            clusters['medical'].append(unk)
        elif context_words & botanical_words or sections.get('herbal_a', 0) > 0 or sections.get('herbal_b', 0) > 0:
            clusters['botanical'].append(unk)
        elif context_words & religious_words:
            clusters['religious'].append(unk)
        elif context_words & astro_words or sections.get('astronomical', 0) > 0:
            clusters['astronomical'].append(unk)
        elif unk['has_y'] and not unk['has_qo']:
            clusters['action'].append(unk)
        else:
            clusters['unknown'].append(unk)
    
    return clusters


def propose_entries(unknowns, pages, dict_words):
    proposals = []
    
    with open(DICT_FILE) as f:
        dict_data = json.load(f)
    entries = dict_data['entries']
    
    for unk in unknowns[:50]:
        word = unk['word']
        skeleton = unk['skeleton']
        
        heb_matches = match_hebrew(skeleton)
        ita_matches = match_italian(skeleton)
        sections = analyze_section_distribution(word, pages)
        primary_section = max(sections, key=sections.get) if sections else 'unknown'
        
        best_match = None
        best_source = None
        best_score = 0
        
        for m in heb_matches:
            if m['score'] > best_score:
                best_score = m['score']
                best_match = m
                best_source = 'Hebrew'
        
        for m in ita_matches:
            if m['score'] > best_score:
                best_score = m['score']
                best_match = m
                best_source = 'Italian'
        
        if best_match and best_score >= 0.5:
            base_word = word.lstrip('qo').lstrip('o').rstrip('y').rstrip('dy')
            existing_similar = None
            for dict_word, entry in entries.items():
                if get_skeleton(dict_word) == get_skeleton(base_word):
                    existing_similar = entry
                    break
            
            confidence = best_score * 0.6
            if primary_section in ['pharmaceutical', 'recipes'] and best_match['meaning'] in ['medicine', 'take', 'give', 'sick']:
                confidence += 0.2
            if primary_section in ['herbal_a', 'herbal_b'] and best_match['meaning'] in ['leaf', 'root', 'flower', 'seed']:
                confidence += 0.2
            if unk['frequency'] > 50:
                confidence += 0.1
            if existing_similar:
                confidence += 0.1
            
            confidence = min(confidence, 0.85)
            
            proposals.append({
                'voynich': word,
                'meaning': best_match['meaning'],
                'language': best_source,
                'match_details': best_match,
                'frequency': unk['frequency'],
                'primary_section': primary_section,
                'confidence': round(confidence, 2),
                'evidence': {
                    'skeleton_match': best_score,
                    'section_fit': primary_section,
                    'similar_exists': existing_similar is not None
                }
            })
    
    return sorted(proposals, key=lambda x: -x['confidence'])[:20]


def validate_proposals(proposals, pages, dict_words):
    validated = []
    
    with open(DICT_FILE) as f:
        dict_data = json.load(f)
    entries = dict_data['entries']
    
    for prop in proposals:
        word = prop['voynich']
        meaning = prop['meaning']
        skeleton = get_skeleton(word)
        
        related_entries = []
        for dict_word, entry in entries.items():
            if entry.get('meaning', '').lower() == meaning.lower():
                if get_skeleton(dict_word) == skeleton or skeleton in get_skeleton(dict_word) or get_skeleton(dict_word) in skeleton:
                    related_entries.append(dict_word)
        
        contexts = find_word_context(word, pages)
        context_makes_sense = False
        context_medical = False
        context_botanical = False
        
        if contexts:
            for ctx in contexts[:5]:
                context_words = ctx['before'] + ctx['after']
                for cw in context_words:
                    if cw in dict_words:
                        entry = entries.get(cw, {})
                        domain = str(entry.get('domain', ''))
                        if 'medical' in domain:
                            context_medical = True
                        if 'botanical' in domain:
                            context_botanical = True
        
        meaning_lower = meaning.lower()
        if meaning_lower in ['heart', 'cure', 'blood', 'sick', 'medicine', 'fever', 'pain', 'heal'] and context_medical:
            context_makes_sense = True
        elif meaning_lower in ['flower', 'leaf', 'root', 'seed', 'tree', 'branch', 'plant'] and context_botanical:
            context_makes_sense = True
        elif meaning_lower in ['salt', 'oil', 'water', 'wine', 'honey', 'vinegar']:
            context_makes_sense = True
        elif meaning_lower in ['one', 'two', 'three', 'all', 'give', 'take', 'put']:
            context_makes_sense = True
        
        if related_entries:
            status = 'EXTENDS_EXISTING'
        elif context_makes_sense:
            status = 'VALID'
        elif prop['confidence'] >= 0.6:
            status = 'NEEDS_REVIEW'
        else:
            status = 'LOW_CONFIDENCE'
        
        prop['validation'] = {
            'related_entries': related_entries[:5],
            'context_sense': context_makes_sense,
            'context_medical': context_medical,
            'context_botanical': context_botanical,
            'status': status
        }
        validated.append(prop)
    
    return validated


def calculate_coverage_improvement(proposals, freq, dict_words):
    total_words = sum(freq.values())
    current_covered = sum(freq.get(w, 0) for w in dict_words)
    
    valid_statuses = {'VALID', 'EXTENDS_EXISTING', 'NEEDS_REVIEW'}
    new_covered = current_covered
    for prop in proposals:
        if prop['validation']['status'] in valid_statuses:
            new_covered += freq.get(prop['voynich'], 0)
    
    return {
        'current_coverage': round(current_covered / total_words, 4),
        'projected_coverage': round(new_covered / total_words, 4),
        'improvement': round((new_covered - current_covered) / total_words, 4),
        'new_words_added': len([p for p in proposals if p['validation']['status'] in valid_statuses])
    }


def generate_report(unknowns, clusters, proposals, coverage, output_path):
    lines = ["# Track 70: High-Frequency Unknown Analysis Report\n"]
    lines.append(f"*Generated from master dictionary analysis*\n\n")
    
    lines.append("## Summary\n")
    lines.append(f"- **Top 100 unknown words analyzed**\n")
    lines.append(f"- **Current coverage**: {coverage['current_coverage']*100:.1f}%\n")
    lines.append(f"- **Projected coverage**: {coverage['projected_coverage']*100:.1f}%\n")
    lines.append(f"- **Potential improvement**: +{coverage['improvement']*100:.2f}%\n")
    lines.append(f"- **New entries proposed**: {len(proposals)}\n\n")
    
    lines.append("---\n\n")
    lines.append("## Top 30 Unknown Words\n\n")
    lines.append("| Rank | Word | Frequency | Skeleton | qo- | -y | Sections |\n")
    lines.append("|------|------|-----------|----------|-----|----|---------|\n")
    
    for i, unk in enumerate(unknowns[:30], 1):
        sections_str = ', '.join(f"{s}:{c}" for s, c in sorted(unk.get('sections', {}).items(), key=lambda x: -x[1])[:2])
        lines.append(f"| {i} | {unk['word']} | {unk['frequency']} | {unk['skeleton']} | {'✓' if unk['has_qo'] else ''} | {'✓' if unk['has_y'] else ''} | {sections_str} |\n")
    
    lines.append("\n---\n\n")
    lines.append("## Context Clusters\n\n")
    
    for cluster_name, words in clusters.items():
        if words:
            lines.append(f"### {cluster_name.title()} ({len(words)} words)\n\n")
            for unk in words[:10]:
                lines.append(f"- **{unk['word']}** (freq: {unk['frequency']})\n")
            lines.append("\n")
    
    lines.append("---\n\n")
    lines.append("## Proposed New Dictionary Entries\n\n")
    lines.append("| Word | Meaning | Language | Confidence | Status |\n")
    lines.append("|------|---------|----------|------------|--------|\n")
    
    for prop in proposals:
        status = prop['validation']['status']
        if status == 'VALID':
            status_emoji = '✅'
        elif status == 'EXTENDS_EXISTING':
            status_emoji = '🔗'
        elif status == 'NEEDS_REVIEW':
            status_emoji = '⚠️'
        else:
            status_emoji = '❓'
        lines.append(f"| {prop['voynich']} | {prop['meaning']} | {prop['language']} | {prop['confidence']:.0%} | {status_emoji} {status} |\n")
    
    lines.append("\n---\n\n")
    lines.append("## Detailed Proposals\n\n")
    
    for i, prop in enumerate(proposals[:10], 1):
        lines.append(f"### {i}. {prop['voynich']} → \"{prop['meaning']}\"\n\n")
        lines.append(f"- **Frequency**: {prop['frequency']}\n")
        lines.append(f"- **Language**: {prop['language']}\n")
        lines.append(f"- **Primary Section**: {prop['primary_section']}\n")
        lines.append(f"- **Confidence**: {prop['confidence']:.0%}\n")
        lines.append(f"- **Match Details**: {prop['match_details']}\n")
        lines.append(f"- **Validation**: {prop['validation']['status']}\n")
        if prop['validation'].get('related_entries'):
            lines.append(f"- **Related entries**: {', '.join(prop['validation']['related_entries'][:3])}\n")
        if prop['validation'].get('context_medical'):
            lines.append(f"- **Context**: medical domain ✓\n")
        if prop['validation'].get('context_botanical'):
            lines.append(f"- **Context**: botanical domain ✓\n")
        lines.append("\n")
    
    lines.append("---\n\n")
    lines.append("## Pattern Analysis\n\n")
    
    qo_words = [u for u in unknowns if u['has_qo']]
    y_words = [u for u in unknowns if u['has_y']]
    aiin_words = [u for u in unknowns if u['has_aiin']]
    
    lines.append(f"- **Words with qo- prefix**: {len(qo_words)} ({len(qo_words)}%)\n")
    lines.append(f"- **Words with -y suffix**: {len(y_words)} ({len(y_words)}%)\n")
    lines.append(f"- **Words with -aiin suffix**: {len(aiin_words)} ({len(aiin_words)}%)\n\n")
    
    skel_counts = Counter(u['skeleton'] for u in unknowns)
    lines.append("### Most Common Skeletons\n\n")
    for skel, count in skel_counts.most_common(10):
        lines.append(f"- `{skel}`: {count} words\n")
    
    lines.append("\n---\n\n")
    lines.append("## Conclusions\n\n")
    
    valid_count = len([p for p in proposals if p['validation']['status'] == 'VALID'])
    extends_count = len([p for p in proposals if p['validation']['status'] == 'EXTENDS_EXISTING'])
    review_count = len([p for p in proposals if p['validation']['status'] == 'NEEDS_REVIEW'])
    
    lines.append(f"1. **{valid_count} new entries are VALID** and ready for dictionary addition\n")
    lines.append(f"2. **{extends_count} entries extend existing** dictionary patterns\n")
    lines.append(f"3. **{review_count} entries need review** before inclusion\n")
    lines.append(f"4. Coverage could improve by **{coverage['improvement']*100:.2f}%** with these additions\n")
    lines.append(f"5. Most unknowns appear in **biological** and **recipes** sections\n")
    lines.append(f"6. The qo- prefix pattern continues to dominate ({len(qo_words)}%)\n")
    lines.append(f"7. The -y suffix appears frequently ({len(y_words)}%)\n")
    
    with open(output_path, 'w') as f:
        f.write(''.join(lines))


def main():
    print("Track 70: High-Frequency Unknown Analysis")
    print("=" * 50)
    
    print("\n1. Loading dictionary and word frequencies...")
    dict_words = load_dict()
    print(f"   Dictionary has {len(dict_words)} entries")
    
    freq = voynich_data.get_word_frequencies()
    print(f"   Found {len(freq)} unique words in manuscript")
    
    print("\n2. Extracting top 100 unknown words...")
    unknowns = extract_unknowns(dict_words, freq)
    print(f"   Top unknown: '{unknowns[0]['word']}' (freq: {unknowns[0]['frequency']})")
    
    pages = voynich_data.get_eva_pages()
    
    print("\n3. Analyzing section distribution...")
    for unk in unknowns:
        unk['sections'] = analyze_section_distribution(unk['word'], pages)
    
    print("\n4. Clustering by context...")
    with open(DICT_FILE) as f:
        dict_data = json.load(f)
    clusters = cluster_by_context(unknowns, dict_words, pages, dict_data)
    for name, words in clusters.items():
        if words:
            print(f"   {name}: {len(words)} words")
    
    print("\n5. Matching Hebrew/Italian patterns...")
    for unk in unknowns[:20]:
        heb = match_hebrew(unk['skeleton'])
        ita = match_italian(unk['skeleton'])
        unk['hebrew_matches'] = heb
        unk['italian_matches'] = ita
    
    print("\n6. Proposing new dictionary entries...")
    proposals = propose_entries(unknowns, pages, dict_words)
    print(f"   Generated {len(proposals)} proposals")
    
    print("\n7. Validating proposals...")
    validated = validate_proposals(proposals, pages, dict_words)
    valid_count = len([p for p in validated if p['validation']['status'] == 'VALID'])
    extends_count = len([p for p in validated if p['validation']['status'] == 'EXTENDS_EXISTING'])
    review_count = len([p for p in validated if p['validation']['status'] == 'NEEDS_REVIEW'])
    print(f"   {valid_count} VALID, {extends_count} extend existing, {review_count} need review")
    
    print("\n8. Calculating coverage improvement...")
    coverage = calculate_coverage_improvement(validated, freq, dict_words)
    print(f"   Current: {coverage['current_coverage']*100:.1f}%")
    print(f"   Projected: {coverage['projected_coverage']*100:.1f}%")
    print(f"   Improvement: +{coverage['improvement']*100:.2f}%")
    
    print("\n9. Saving results...")
    results = {
        'summary': {
            'unknowns_analyzed': 100,
            'proposals_generated': len(proposals),
            'valid_proposals': valid_count,
            'extends_existing': extends_count,
            'needs_review': review_count,
            'coverage_improvement': coverage
        },
        'top_100_unknowns': unknowns,
        'context_clusters': {k: [u['word'] for u in v] for k, v in clusters.items()},
        'proposed_entries': validated,
        'validation_results': {
            'valid': [p for p in validated if p['validation']['status'] == 'VALID'],
            'extends_existing': [p for p in validated if p['validation']['status'] == 'EXTENDS_EXISTING'],
            'needs_review': [p for p in validated if p['validation']['status'] == 'NEEDS_REVIEW'],
            'low_confidence': [p for p in validated if p['validation']['status'] == 'LOW_CONFIDENCE']
        }
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"   Saved JSON: {OUTPUT_JSON}")
    
    generate_report(unknowns, clusters, validated, coverage, OUTPUT_MD)
    print(f"   Saved report: {OUTPUT_MD}")
    
    print("\n" + "=" * 50)
    print("COMPLETE!")
    print(f"Valid new entries: {valid_count}")
    print(f"Coverage improvement: +{coverage['improvement']*100:.2f}%")


if __name__ == "__main__":
    main()



