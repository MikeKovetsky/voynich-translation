"""
Track 51: Expand Dictionary by Semantic Domains
Search for botanical, medical, astronomical, and pharmaceutical vocabulary.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import voynich_data as vd

PHONETIC_KEY = {
    'a': ['o', 'a'],
    'e': ['e', 'a'],
    'i': ['i', 'e', 'ai', 'ii'],
    'o': ['o', 'a'],
    'u': ['o', 'a'],
    'b': ['p'],
    'c': ['k', 'ch', 'sh'],
    'd': ['d', 't'],
    'f': ['f', 'p'],
    'g': ['k', 'ch'],
    'h': [],
    'k': ['k', 'ch'],
    'l': ['l'],
    'm': ['m', 'aiin'],
    'n': ['n', 'ain', 'in'],
    'p': ['p'],
    'q': ['q'],
    'r': ['r', 'ar', 'or'],
    's': ['s', 'sh'],
    't': ['t', 'ch', 'd'],
    'v': ['f'],
    'z': ['s', 'sh', 'ts'],
}

VOWELS = set('aeiou')

BOTANICAL_ITALIAN = {
    'foglia': 'leaf', 'radice': 'root', 'corteccia': 'bark',
    'seme': 'seed', 'bacca': 'berry', 'frutto': 'fruit',
    'gambo': 'stem', 'petalo': 'petal', 'spina': 'thorn',
    'fiore': 'flower', 'erba': 'herb', 'ramo': 'branch',
    'grano': 'grain', 'olivo': 'olive', 'rosa': 'rose',
    'giglio': 'lily', 'lauro': 'laurel', 'cipolla': 'onion',
    'aglio': 'garlic', 'menta': 'mint', 'salvia': 'sage',
    'rosmarino': 'rosemary', 'basilico': 'basil', 'pepe': 'pepper',
    'zenzero': 'ginger', 'cannella': 'cinnamon', 'noce': 'walnut',
    'mandorla': 'almond', 'pesco': 'peach', 'melo': 'apple',
    'vite': 'vine', 'uva': 'grape', 'fico': 'fig',
    'orzo': 'barley', 'grano': 'wheat', 'avena': 'oat',
    'lino': 'flax', 'canapa': 'hemp', 'papavero': 'poppy',
    'anice': 'anise', 'finocchio': 'fennel', 'cumino': 'cumin',
    'coriandolo': 'coriander', 'zafferano': 'saffron', 'mastice': 'mastic',
    'incenso': 'incense', 'mirra': 'myrrh', 'aloe': 'aloe',
    'succo': 'juice', 'resina': 'resin', 'gomma': 'gum',
    'cenere': 'ash', 'polvere': 'powder', 'fogliame': 'foliage',
}

BOTANICAL_HEBREW = {
    'aleh': 'leaf', 'shoresh': 'root', 'pri': 'fruit',
    'ets': 'tree', 'gefen': 'vine', 'deshe': 'grass',
    'esev': 'herb', 'dagan': 'grain', 'chitah': 'wheat',
    'seorah': 'barley', 'tapuach': 'apple', 'rimon': 'pomegranate',
    'tena': 'fig', 'gezer': 'carrot', 'shum': 'garlic',
    'batsal': 'onion', 'kishuim': 'cucumber', 'avatiach': 'watermelon',
    'egoz': 'nut', 'shaked': 'almond', 'tamar': 'date',
    'zeitim': 'olive', 'kerem': 'vineyard', 'perach': 'flower',
    'shoshana': 'rose/lily', 'levona': 'frankincense', 'mor': 'myrrh',
    'bosem': 'spice', 'karkom': 'saffron', 'nard': 'nard',
    'kinamon': 'cinnamon', 'tsori': 'balm', 'gad': 'coriander',
    'kamon': 'cumin', 'shevet': 'dill', 'luz': 'almond tree',
}

MEDICAL_ITALIAN = {
    'fegato': 'liver', 'polmone': 'lung', 'stomaco': 'stomach',
    'rene': 'kidney', 'occhio': 'eye', 'orecchio': 'ear',
    'febbre': 'fever', 'tosse': 'cough', 'sangue': 'blood',
    'osso': 'bone', 'muscolo': 'muscle', 'nervo': 'nerve',
    'vena': 'vein', 'arteria': 'artery', 'cervello': 'brain',
    'testa': 'head', 'mano': 'hand', 'piede': 'foot',
    'gamba': 'leg', 'braccio': 'arm', 'dito': 'finger',
    'pancia': 'belly', 'petto': 'chest', 'collo': 'neck',
    'schiena': 'back', 'spalla': 'shoulder', 'ginocchio': 'knee',
    'dolore': 'pain', 'malattia': 'disease', 'ferita': 'wound',
    'piaga': 'sore', 'gonfiore': 'swelling', 'infezione': 'infection',
    'veleno': 'poison', 'antidoto': 'antidote', 'cura': 'cure',
    'morte': 'death', 'vita': 'life', 'salute': 'health',
    'gravidanza': 'pregnancy', 'parto': 'birth', 'latte': 'milk',
    'urina': 'urine', 'feci': 'feces', 'sudore': 'sweat',
    'bile': 'bile', 'flemma': 'phlegm', 'umore': 'humor',
}

MEDICAL_HEBREW = {
    'lev': 'heart', 'kaved': 'liver', 'regel': 'foot/leg',
    'yad': 'hand', 'rosh': 'head', 'choleh': 'sick',
    'refuah': 'medicine', 'makkah': 'wound', 'tsaraas': 'leprosy',
    'dam': 'blood', 'basar': 'flesh', 'etsem': 'bone',
    'ayin': 'eye', 'ozen': 'ear', 'peh': 'mouth',
    'lashon': 'tongue', 'shen': 'tooth', 'af': 'nose',
    'beten': 'belly', 'guf': 'body', 'nefesh': 'soul/life',
    'neshamah': 'breath', 'mavet': 'death', 'chayim': 'life',
    'chom': 'heat/fever', 'kar': 'cold', 'keev': 'pain',
    'tsarah': 'trouble', 'yoledes': 'birthing', 'chalav': 'milk',
    'shemen': 'oil', 'mayim': 'water', 'yayin': 'wine',
    'mar': 'bitter', 'matok': 'sweet', 'melach': 'salt',
}

ASTRONOMICAL_ITALIAN = {
    'stella': 'star', 'cielo': 'sky', 'notte': 'night',
    'giorno': 'day', 'luna': 'moon', 'sole': 'sun',
    'pianeta': 'planet', 'cometa': 'comet', 'eclissi': 'eclipse',
    'alba': 'dawn', 'tramonto': 'sunset', 'mezzanotte': 'midnight',
    'mezzogiorno': 'noon', 'orizzonte': 'horizon', 'zodiaco': 'zodiac',
    'ariete': 'aries', 'toro': 'taurus', 'gemelli': 'gemini',
    'cancro': 'cancer', 'leone': 'leo', 'vergine': 'virgo',
    'bilancia': 'libra', 'scorpione': 'scorpio', 'sagittario': 'sagittarius',
    'capricorno': 'capricorn', 'acquario': 'aquarius', 'pesci': 'pisces',
    'marzo': 'march', 'aprile': 'april', 'maggio': 'may',
    'giugno': 'june', 'luglio': 'july', 'agosto': 'august',
    'settembre': 'september', 'ottobre': 'october', 'novembre': 'november',
}

ASTRONOMICAL_HEBREW = {
    'kochav': 'star', 'shamayim': 'sky/heaven', 'layla': 'night',
    'yom': 'day', 'yareach': 'moon', 'shemesh': 'sun',
    'mazal': 'constellation', 'galgal': 'wheel/sphere', 'rakia': 'firmament',
    'or': 'light', 'choshech': 'darkness', 'boker': 'morning',
    'erev': 'evening', 'shachar': 'dawn', 'tsohoraim': 'noon',
    'chodesh': 'month', 'shana': 'year', 'shavua': 'week',
    'nisan': 'nisan', 'iyar': 'iyar', 'sivan': 'sivan',
    'tamuz': 'tamuz', 'av': 'av', 'elul': 'elul',
    'tishrei': 'tishrei', 'cheshvan': 'cheshvan', 'kislev': 'kislev',
    'tevet': 'tevet', 'shevat': 'shevat', 'adar': 'adar',
    'taleh': 'aries', 'shor': 'taurus', 'teomim': 'gemini',
    'sartan': 'cancer', 'aryeh': 'leo', 'betulah': 'virgo',
    'moznayim': 'libra', 'akrav': 'scorpio', 'keshet': 'sagittarius',
    'gedi': 'capricorn', 'deli': 'aquarius', 'dagim': 'pisces',
}

PHARMACEUTICAL_ITALIAN = {
    'mescolare': 'mix', 'bollire': 'boil', 'macinare': 'grind',
    'applicare': 'apply', 'bere': 'drink', 'olio': 'oil',
    'acqua': 'water', 'vino': 'wine', 'aceto': 'vinegar',
    'miele': 'honey', 'zucchero': 'sugar', 'sale': 'salt',
    'unguento': 'ointment', 'sciroppo': 'syrup', 'pillola': 'pill',
    'polvere': 'powder', 'infuso': 'infusion', 'decotto': 'decoction',
    'impiastro': 'poultice', 'elettuario': 'electuary', 'collirio': 'eye drops',
    'clistere': 'enema', 'supposta': 'suppository', 'bagno': 'bath',
    'vapore': 'steam', 'fumo': 'smoke', 'cataplasma': 'cataplasm',
    'dose': 'dose', 'misura': 'measure', 'peso': 'weight',
    'dramma': 'dram', 'oncia': 'ounce', 'libbra': 'pound',
    'parte': 'part', 'prendere': 'take', 'dare': 'give',
    'curare': 'heal', 'preparare': 'prepare', 'conservare': 'preserve',
    'seccare': 'dry', 'filtrare': 'filter', 'distillare': 'distill',
}

PHARMACEUTICAL_HEBREW = {
    'mayim': 'water', 'shemen': 'oil', 'melach': 'salt',
    'dvash': 'honey', 'yayin': 'wine', 'chomets': 'vinegar',
    'sam': 'medicine/drug', 'terufah': 'remedy', 'mishcha': 'ointment',
    'mar': 'bitter', 'matok': 'sweet', 'cham': 'hot',
    'kar': 'cold', 'yavesh': 'dry', 'lach': 'moist',
    'zahav': 'gold', 'kesef': 'silver', 'nechoshet': 'copper',
    'barzel': 'iron', 'oferet': 'lead', 'gofrit': 'sulfur',
    'shiur': 'measure', 'mishkal': 'weight', 'chelek': 'part',
    'rapa': 'heal', 'nasah': 'try', 'kach': 'take',
    'hishka': 'give drink', 'shatah': 'drink', 'achal': 'eat',
    'mashach': 'anoint', 'sachak': 'grind', 'ratach': 'boil',
    'nisakh': 'pour', 'erv': 'mix', 'tavar': 'break',
}


def get_skeleton(word):
    return ''.join(c for c in word.lower() if c not in 'aeiou')


def generate_variants(word, max_variants=50):
    variants = set()
    word_lower = word.lower()
    
    def build_variant(remaining, current):
        if len(variants) >= max_variants:
            return
        if not remaining:
            if current:
                variants.add(current)
            return
            
        char = remaining[0]
        rest = remaining[1:]
        
        if char in PHONETIC_KEY:
            options = PHONETIC_KEY[char]
            if options:
                for opt in options:
                    build_variant(rest, current + opt)
            else:
                build_variant(rest, current)
        else:
            build_variant(rest, current + char)
    
    build_variant(word_lower, '')
    
    prefix_variants = set()
    for v in list(variants):
        prefix_variants.add('o' + v)
        prefix_variants.add('y' + v)
        prefix_variants.add('qo' + v)
        prefix_variants.add('cho' + v)
    variants.update(prefix_variants)
    
    suffix_variants = set()
    for v in list(variants):
        suffix_variants.add(v + 'y')
        suffix_variants.add(v + 'in')
        suffix_variants.add(v + 'aiin')
        if v.endswith('r'):
            suffix_variants.add(v[:-1] + 'ar')
            suffix_variants.add(v[:-1] + 'or')
    variants.update(suffix_variants)
    
    return variants


def search_corpus(target_variants, word_freq, threshold=5):
    matches = []
    for voynich_word, freq in word_freq.items():
        if freq < threshold:
            continue
        if voynich_word in target_variants:
            matches.append((voynich_word, freq, 'exact'))
        else:
            v_skel = get_skeleton(voynich_word)
            for variant in target_variants:
                t_skel = get_skeleton(variant)
                if v_skel == t_skel and len(v_skel) >= 2:
                    matches.append((voynich_word, freq, 'skeleton'))
                    break
    return matches


def get_word_section_dist(word, eva_pages, section_folios):
    dist = defaultdict(int)
    for section, folios in section_folios.items():
        for folio in folios:
            if folio in eva_pages:
                for text in eva_pages[folio].values():
                    text_clean = re.sub(r'[!?<>@$\d]', '', text)
                    words = re.split(r'[.\-=,\s]', text_clean)
                    for w in words:
                        if w == word:
                            dist[section] += 1
    return dict(dist)


def analyze_domain(domain_name, italian_dict, hebrew_dict, word_freq, eva_pages, sections):
    entries = []
    seen_voynich = set()
    
    for source_word, meaning in italian_dict.items():
        variants = generate_variants(source_word)
        matches = search_corpus(variants, word_freq)
        for voynich_word, freq, match_type in matches:
            if voynich_word not in seen_voynich:
                section_dist = get_word_section_dist(voynich_word, eva_pages, sections)
                entries.append({
                    'voynich': voynich_word,
                    'source': source_word,
                    'language': 'Italian',
                    'meaning': meaning,
                    'frequency': freq,
                    'match_type': match_type,
                    'section_dist': section_dist,
                    'skeleton': get_skeleton(voynich_word),
                })
                seen_voynich.add(voynich_word)
    
    for source_word, meaning in hebrew_dict.items():
        variants = generate_variants(source_word)
        matches = search_corpus(variants, word_freq)
        for voynich_word, freq, match_type in matches:
            if voynich_word not in seen_voynich:
                section_dist = get_word_section_dist(voynich_word, eva_pages, sections)
                entries.append({
                    'voynich': voynich_word,
                    'source': source_word,
                    'language': 'Hebrew',
                    'meaning': meaning,
                    'frequency': freq,
                    'match_type': match_type,
                    'section_dist': section_dist,
                    'skeleton': get_skeleton(voynich_word),
                })
                seen_voynich.add(voynich_word)
    
    return sorted(entries, key=lambda x: -x['frequency'])


def validate_botanical(entries):
    valid = []
    for e in entries:
        dist = e.get('section_dist', {})
        herbal = dist.get('herbal_a', 0) + dist.get('herbal_b', 0)
        pharm = dist.get('pharmaceutical', 0)
        total = sum(dist.values()) if dist else 1
        if herbal + pharm > total * 0.3 or e['frequency'] > 50:
            valid.append(e)
    return valid


def validate_medical(entries):
    valid = []
    for e in entries:
        dist = e.get('section_dist', {})
        bio = dist.get('biological', 0)
        recipes = dist.get('recipes', 0)
        pharm = dist.get('pharmaceutical', 0)
        total = sum(dist.values()) if dist else 1
        if bio + recipes + pharm > total * 0.2 or e['frequency'] > 30:
            valid.append(e)
    return valid


def validate_astronomical(entries):
    valid = []
    for e in entries:
        dist = e.get('section_dist', {})
        astro = dist.get('astronomical', 0)
        total = sum(dist.values()) if dist else 1
        if astro > 0 or e['frequency'] > 20:
            valid.append(e)
    return valid


def validate_pharmaceutical(entries):
    valid = []
    for e in entries:
        dist = e.get('section_dist', {})
        pharm = dist.get('pharmaceutical', 0)
        recipes = dist.get('recipes', 0)
        total = sum(dist.values()) if dist else 1
        if pharm + recipes > total * 0.3 or e['frequency'] > 30:
            valid.append(e)
    return valid


def main():
    print("=" * 60)
    print("Track 51: Semantic Domain Dictionary Expansion")
    print("=" * 60)
    
    print("\n[1/6] Loading corpus...")
    word_freq = vd.get_word_frequencies()
    eva_pages = vd.get_eva_pages()
    print(f"  Unique words: {len(word_freq)}")
    print(f"  Pages: {len(eva_pages)}")
    
    sections = vd.FOLIO_SECTIONS
    
    print("\n[2/6] Loading existing dictionary...")
    existing = set()
    
    hybrid_path = Path('results/hybrid_dictionary.json')
    if hybrid_path.exists():
        try:
            data = json.loads(hybrid_path.read_text())
            if 'entries' in data and isinstance(data['entries'], dict):
                for voynich_word in data['entries'].keys():
                    existing.add(voynich_word)
        except Exception as e:
            print(f"  Warning: Could not load hybrid dictionary: {e}")
    
    proto_path = Path('results/proto_romance_analysis.json')
    if proto_path.exists():
        try:
            data = json.loads(proto_path.read_text())
            for cat in ['italian_roots', 'hebrew_roots']:
                if cat in data:
                    for match_type in ['exact', 'contains']:
                        if match_type in data[cat]:
                            for entry in data[cat][match_type]:
                                existing.add(entry.get('voynich', ''))
            for m in data.get('hybrid_mappings', []):
                existing.add(m.get('voynich', ''))
        except:
            pass
    
    print(f"  Existing entries: {len(existing)}")
    
    results = {'domains': {}, 'new_entries': []}
    
    print("\n[3/6] Analyzing BOTANICAL domain...")
    botanical_entries = analyze_domain(
        'botanical', BOTANICAL_ITALIAN, BOTANICAL_HEBREW,
        word_freq, eva_pages, sections
    )
    botanical_valid = validate_botanical(botanical_entries)
    botanical_new = [e for e in botanical_valid if e['voynich'] not in existing]
    results['domains']['botanical'] = {
        'raw_matches': len(botanical_entries),
        'validated': len(botanical_valid),
        'new': len(botanical_new),
        'entries': botanical_new[:50]
    }
    print(f"  Raw: {len(botanical_entries)}, Validated: {len(botanical_valid)}, New: {len(botanical_new)}")
    
    print("\n[4/6] Analyzing MEDICAL domain...")
    medical_entries = analyze_domain(
        'medical', MEDICAL_ITALIAN, MEDICAL_HEBREW,
        word_freq, eva_pages, sections
    )
    medical_valid = validate_medical(medical_entries)
    medical_new = [e for e in medical_valid if e['voynich'] not in existing]
    results['domains']['medical'] = {
        'raw_matches': len(medical_entries),
        'validated': len(medical_valid),
        'new': len(medical_new),
        'entries': medical_new[:30]
    }
    print(f"  Raw: {len(medical_entries)}, Validated: {len(medical_valid)}, New: {len(medical_new)}")
    
    print("\n[5/6] Analyzing ASTRONOMICAL domain...")
    astronomical_entries = analyze_domain(
        'astronomical', ASTRONOMICAL_ITALIAN, ASTRONOMICAL_HEBREW,
        word_freq, eva_pages, sections
    )
    astronomical_valid = validate_astronomical(astronomical_entries)
    astronomical_new = [e for e in astronomical_valid if e['voynich'] not in existing]
    results['domains']['astronomical'] = {
        'raw_matches': len(astronomical_entries),
        'validated': len(astronomical_valid),
        'new': len(astronomical_new),
        'entries': astronomical_new[:15]
    }
    print(f"  Raw: {len(astronomical_entries)}, Validated: {len(astronomical_valid)}, New: {len(astronomical_new)}")
    
    print("\n[6/6] Analyzing PHARMACEUTICAL domain...")
    pharm_entries = analyze_domain(
        'pharmaceutical', PHARMACEUTICAL_ITALIAN, PHARMACEUTICAL_HEBREW,
        word_freq, eva_pages, sections
    )
    pharm_valid = validate_pharmaceutical(pharm_entries)
    pharm_new = [e for e in pharm_valid if e['voynich'] not in existing]
    results['domains']['pharmaceutical'] = {
        'raw_matches': len(pharm_entries),
        'validated': len(pharm_valid),
        'new': len(pharm_new),
        'entries': pharm_new[:20]
    }
    print(f"  Raw: {len(pharm_entries)}, Validated: {len(pharm_valid)}, New: {len(pharm_new)}")
    
    all_new = []
    seen = set()
    for domain in ['botanical', 'medical', 'astronomical', 'pharmaceutical']:
        for e in results['domains'][domain]['entries']:
            if e['voynich'] not in seen:
                all_new.append(e)
                seen.add(e['voynich'])
    
    results['total_new_entries'] = len(all_new)
    results['new_entries'] = all_new
    
    json_path = Path('results/dictionary_expansion_semantic.json')
    json_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nJSON saved: {json_path}")
    
    report = generate_report(results)
    report_path = Path('results/dictionary_expansion_semantic_report.md')
    report_path.write_text(report)
    print(f"Report saved: {report_path}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Botanical:      +{results['domains']['botanical']['new']} entries")
    print(f"  Medical:        +{results['domains']['medical']['new']} entries")
    print(f"  Astronomical:   +{results['domains']['astronomical']['new']} entries")
    print(f"  Pharmaceutical: +{results['domains']['pharmaceutical']['new']} entries")
    print(f"  TOTAL NEW:      {results['total_new_entries']} entries")


def generate_report(results):
    lines = [
        "# Dictionary Expansion: Semantic Domains",
        "",
        "Track 51 Results - Expanding vocabulary by semantic field.",
        "",
        "## Summary",
        "",
        f"- **Botanical**: {results['domains']['botanical']['new']} new entries",
        f"- **Medical**: {results['domains']['medical']['new']} new entries", 
        f"- **Astronomical**: {results['domains']['astronomical']['new']} new entries",
        f"- **Pharmaceutical**: {results['domains']['pharmaceutical']['new']} new entries",
        f"- **TOTAL**: {results['total_new_entries']} new entries",
        "",
    ]
    
    lines.extend([
        "## Botanical Terms",
        "",
        "| Voynich | Source | Language | Meaning | Frequency | Match |",
        "|---------|--------|----------|---------|-----------|-------|",
    ])
    for e in results['domains']['botanical']['entries'][:30]:
        lines.append(
            f"| {e['voynich']} | {e['source']} | {e['language']} | "
            f"{e['meaning']} | {e['frequency']} | {e['match_type']} |"
        )
    
    lines.extend([
        "",
        "## Medical Terms",
        "",
        "| Voynich | Source | Language | Meaning | Frequency | Match |",
        "|---------|--------|----------|---------|-----------|-------|",
    ])
    for e in results['domains']['medical']['entries'][:20]:
        lines.append(
            f"| {e['voynich']} | {e['source']} | {e['language']} | "
            f"{e['meaning']} | {e['frequency']} | {e['match_type']} |"
        )
    
    lines.extend([
        "",
        "## Astronomical Terms",
        "",
        "| Voynich | Source | Language | Meaning | Frequency | Match |",
        "|---------|--------|----------|---------|-----------|-------|",
    ])
    for e in results['domains']['astronomical']['entries'][:15]:
        lines.append(
            f"| {e['voynich']} | {e['source']} | {e['language']} | "
            f"{e['meaning']} | {e['frequency']} | {e['match_type']} |"
        )
    
    lines.extend([
        "",
        "## Pharmaceutical Terms", 
        "",
        "| Voynich | Source | Language | Meaning | Frequency | Match |",
        "|---------|--------|----------|---------|-----------|-------|",
    ])
    for e in results['domains']['pharmaceutical']['entries'][:15]:
        lines.append(
            f"| {e['voynich']} | {e['source']} | {e['language']} | "
            f"{e['meaning']} | {e['frequency']} | {e['match_type']} |"
        )
    
    lines.extend([
        "",
        "## Section Distribution Analysis",
        "",
        "Showing where new terms appear most frequently:",
        "",
    ])
    
    for domain_name, domain_data in results['domains'].items():
        lines.append(f"### {domain_name.title()}")
        lines.append("")
        top_entries = domain_data['entries'][:5]
        for e in top_entries:
            dist = e.get('section_dist', {})
            if dist:
                lines.append(f"- **{e['voynich']}** ({e['meaning']}): {dict(dist)}")
        lines.append("")
    
    lines.extend([
        "## Methodology",
        "",
        "1. Generated phonetic variants for Italian and Hebrew domain vocabulary",
        "2. Searched corpus for exact and skeleton matches",
        "3. Validated by section distribution (botanical→herbal, medical→biological/recipes, etc.)",
        "4. Filtered against existing dictionary to avoid duplicates",
        "",
        "---",
        "*Generated by expand_dict_semantic.py*"
    ])
    
    return '\n'.join(lines)


if __name__ == '__main__':
    main()
