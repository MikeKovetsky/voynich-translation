import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher

RAW_FILE = "voynich_raw.txt"
OUTPUT_JSON = "results/cross_section.json"
OUTPUT_REPORT = "results/cross_section_report.md"

PHONETIC_MAP = {
    'o': 'a', 'h': 'r', '9': 's', 'k': 'n', 'c': 'c', '7': 'l', 'm': 'm',
    'a': 'e', 'e': 'i', '8': 'd', '1': 't', '4': 'qu', 'y': 'i', '2': 'b',
    'C': 'ch', 's': 'x', 'n': 'n', 'p': 'p', 'g': 'g', 'j': 'i', 'W': 'u',
    'H': 'h', 'z': 'z', 'u': 'u', 'f': 'f', 'A': 'a', 'd': 'v', 'J': 'i',
    'Z': 'z', 'K': 'c', 'i': 'i', 'S': 's', 't': 't', 'b': 'b', 'E': 'e',
    'M': 'm', 'Q': 'q', 'I': 'i', 'N': 'n', 'l': 'l', '3': 'e', 'Þ': 'th',
    '%': '', '?': '', '(': '', '*': '', '°': '', 'Ý': '', ',': '',
    'ü': 'u', '¼': '', '½': '', 'ò': 'o', 'T': 't', 'G': 'g', 'ç': 'c',
    'R': 'r', 'B': 'b', 'P': 'p', 'L': 'l', 'V': 'v', 'F': 'f', 'D': 'd',
}

ABBREV_EXPANSIONS = {
    '89': '-orum',
    '9': '-us',
    'am': '-am',
    'oe': '-ae',
    'ay': '-i',
    'an': '-um',
    'ae': '-ae',
}

SECTIONS = {
    'botanical': {'start': 1, 'end': 57, 'name': 'Botanical'},
    'astronomical': {'start': 67, 'end': 73, 'name': 'Astronomical'},
    'biological': {'start': 75, 'end': 84, 'name': 'Biological/Nymphs'},
    'cosmological': {'start': 85, 'end': 87, 'name': 'Cosmological'},
    'pharmaceutical': {'start': 88, 'end': 102, 'name': 'Pharmaceutical'},
    'recipes': {'start': 103, 'end': 116, 'name': 'Recipes'},
}

LATIN_BOTANICAL = [
    'radix', 'herba', 'flos', 'folium', 'fructus', 'semen', 'cortex', 'succus',
    'caulis', 'ramus', 'spina', 'bacca', 'arbor', 'stirps', 'aqua', 'oleum',
    'vinum', 'mel', 'sal', 'acetum', 'lac', 'cera', 'pix', 'tuber', 'bulbus'
]

LATIN_MEDICAL = [
    'febris', 'dolor', 'caput', 'stomachus', 'oculus', 'sanguis', 'vulnus', 'morbus',
    'tussis', 'tumor', 'ulcus', 'dens', 'auris', 'nasus', 'cor', 'iecur', 'venter', 
    'manus', 'pes', 'corpus', 'cutis', 'membrum', 'nervus', 'musculus'
]

LATIN_PREPOSITIONS = [
    'in', 'ad', 'pro', 'contra', 'cum', 'de', 'per', 'sub', 'super', 'ex', 'ab'
]

LATIN_VERBS = [
    'est', 'sunt', 'habet', 'facit', 'curat', 'sanat', 'valet', 'prodest',
    'bibitur', 'coquitur', 'datur', 'ponitur', 'lavatur', 'miscetur', 'purgat', 'solvit'
]

LATIN_ADJECTIVES = [
    'calidus', 'frigidus', 'siccus', 'humidus', 'bonus', 'magnus', 'parvus',
    'albus', 'niger', 'viridis', 'dulcis', 'amarus', 'acris', 'ruber'
]

LATIN_PLANT_NAMES = [
    'centaurea', 'absinthium', 'artemisia', 'plantago', 'urtica', 'mentha',
    'salvia', 'rosmarinus', 'origanum', 'calendula', 'papaver', 'cannabis',
    'helleborus', 'cyclamen', 'ricinus', 'viola', 'rosa', 'lilium', 'crocus',
    'juniperus', 'betonica', 'verbena', 'melissa', 'malva', 'foeniculum'
]

LATIN_ASTRONOMICAL = [
    'stella', 'stellae', 'sol', 'luna', 'caelum', 'astrum', 'orbis', 'circulus',
    'centrum', 'radius', 'sphaera', 'mundus', 'polus', 'axis', 'ecliptica',
    'zodiacus', 'signum', 'gradus', 'minutum', 'ascendens', 'descendens',
    'septentrio', 'meridies', 'oriens', 'occidens'
]

LATIN_ZODIAC = [
    'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
    'libra', 'scorpio', 'sagittarius', 'capricornus', 'aquarius', 'pisces'
]

LATIN_MONTHS = [
    'ianuarius', 'februarius', 'martius', 'aprilis', 'maius', 'iunius',
    'iulius', 'augustus', 'september', 'october', 'november', 'december'
]

STAR_NAMES = [
    'sirius', 'arcturus', 'vega', 'capella', 'rigel', 'procyon', 'betelgeuse',
    'altair', 'aldebaran', 'antares', 'spica', 'pollux', 'fomalhaut', 'deneb',
    'regulus', 'canopus', 'castor'
]

LATIN_BODY_PARTS = [
    'caput', 'corpus', 'manus', 'pes', 'brachium', 'crus', 'femur', 'humerus',
    'venter', 'pectus', 'dorsum', 'collum', 'facies', 'oculus', 'auris', 'nasus',
    'os', 'lingua', 'dens', 'capillus', 'cutis', 'sanguis', 'os', 'nervus',
    'musculus', 'vena', 'arteria', 'cor', 'pulmo', 'hepar', 'ren', 'vesica',
    'uterus', 'matrix', 'vulva', 'mamilla', 'umbilicus'
]

LATIN_WATER = [
    'aqua', 'fons', 'fluvius', 'rivus', 'stagnum', 'lacus', 'mare', 'unda',
    'humor', 'liquor', 'succus', 'latex', 'ros', 'pluvia', 'gutta', 'balneum'
]

LATIN_PHARMACEUTICAL = [
    'recipe', 'misce', 'coque', 'cola', 'distilla', 'solve', 'coagula',
    'pulvis', 'unguentum', 'emplastrum', 'syrupus', 'electuarium', 'pilula',
    'decoctum', 'infusum', 'tinctura', 'oleum', 'aqua', 'spiritus',
    'dosis', 'drachma', 'uncia', 'libra', 'gutta', 'manipulus'
]

ALL_LATIN = (LATIN_BOTANICAL + LATIN_MEDICAL + LATIN_PREPOSITIONS + LATIN_VERBS + 
             LATIN_ADJECTIVES + LATIN_PLANT_NAMES + LATIN_ASTRONOMICAL + LATIN_ZODIAC +
             LATIN_MONTHS + STAR_NAMES + LATIN_BODY_PARTS + LATIN_WATER + LATIN_PHARMACEUTICAL)


def load_transcription():
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def extract_section(text, section_name):
    section = SECTIONS[section_name]
    pages = {}
    pattern = re.compile(r'<(\d+[rv])\.(\d+)>([^<]+)')
    
    for match in pattern.finditer(text):
        folio_str = match.group(1)
        line_num = int(match.group(2))
        content = match.group(3).rstrip('-=\n')
        
        folio_num = int(re.match(r'(\d+)', folio_str).group(1))
        
        if folio_num < section['start'] or folio_num > section['end']:
            continue
        
        folio = 'f' + folio_str
        if folio not in pages:
            pages[folio] = {'lines': [], 'words': []}
        
        words = [w.strip() for w in content.split('.') if w.strip()]
        clean_words = []
        for w in words:
            w = re.sub(r'[^\w]', '', w)
            if w:
                clean_words.append(w)
        
        pages[folio]['lines'].append({
            'num': line_num,
            'raw': content,
            'words': clean_words
        })
        pages[folio]['words'].extend(clean_words)
    
    return pages


def decode_char(ch):
    return PHONETIC_MAP.get(ch, ch)


def decode_word(word):
    return ''.join(decode_char(c) for c in word)


def decode_expanded(word):
    decoded = decode_word(word)
    for ending, expansion in sorted(ABBREV_EXPANSIONS.items(), key=lambda x: -len(x[0])):
        if word.endswith(ending):
            base_len = len(decode_word(ending))
            base = decoded[:-base_len] if base_len > 0 else decoded
            return base + expansion
    return decoded


def similarity(s1, s2):
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def consonant_skeleton(word):
    return re.sub(r'[aeiou]', '', word.lower())


def find_latin_match(decoded, domain_vocab=None):
    vocab = ALL_LATIN if domain_vocab is None else ALL_LATIN + domain_vocab
    best_match = None
    best_score = 0
    match_type = 'none'
    
    for latin in vocab:
        exact = similarity(decoded, latin)
        if exact > best_score:
            best_score = exact
            best_match = latin
            match_type = 'exact' if exact >= 0.75 else 'stem' if exact >= 0.6 else 'phonetic' if exact >= 0.45 else 'none'
    
    if best_score < 0.45:
        dec_skel = consonant_skeleton(decoded)
        for latin in vocab:
            lat_skel = consonant_skeleton(latin)
            skel_sim = similarity(dec_skel, lat_skel)
            if skel_sim > best_score:
                best_score = skel_sim
                best_match = latin
                match_type = 'phonetic' if skel_sim >= 0.45 else 'none'
    
    return best_match, best_score, match_type


def find_domain_matches(decoded_words, domain_vocab, vocab_name):
    matches = []
    for word in decoded_words:
        for domain_word in domain_vocab:
            sim = similarity(word, domain_word)
            if sim >= 0.55:
                matches.append({
                    'decoded': word,
                    'domain_match': domain_word,
                    'similarity': round(sim, 3)
                })
    unique_matches = {}
    for m in matches:
        key = m['domain_match']
        if key not in unique_matches or m['similarity'] > unique_matches[key]['similarity']:
            unique_matches[key] = m
    return list(unique_matches.values())


def analyze_section(section_name, pages):
    all_words = []
    word_freq = Counter()
    matches = {'exact': 0, 'stem': 0, 'phonetic': 0, 'none': 0}
    decoded_list = []
    
    for folio, page_data in sorted(pages.items()):
        for word in page_data['words']:
            decoded = decode_expanded(word)
            match, score, match_type = find_latin_match(decoded)
            matches[match_type] += 1
            word_freq[decoded] += 1
            decoded_list.append(decoded)
            all_words.append({
                'voynich': word,
                'decoded': decoded,
                'latin_match': match if match_type != 'none' else None,
                'score': round(score, 3),
                'type': match_type
            })
    
    total = len(all_words)
    if total == 0:
        return None
    
    latin_count = matches['exact'] + matches['stem'] + matches['phonetic']
    latin_rate = latin_count / total
    
    domain_specific = {}
    if section_name == 'astronomical':
        domain_specific['zodiac_found'] = find_domain_matches(decoded_list, LATIN_ZODIAC, 'zodiac')
        domain_specific['months_found'] = find_domain_matches(decoded_list, LATIN_MONTHS, 'months')
        domain_specific['stars_found'] = find_domain_matches(decoded_list, STAR_NAMES, 'stars')
        domain_specific['astro_terms'] = find_domain_matches(decoded_list, LATIN_ASTRONOMICAL, 'astronomical')
    elif section_name == 'biological':
        domain_specific['body_parts_found'] = find_domain_matches(decoded_list, LATIN_BODY_PARTS, 'body')
        domain_specific['water_terms_found'] = find_domain_matches(decoded_list, LATIN_WATER, 'water')
        domain_specific['medical_terms'] = find_domain_matches(decoded_list, LATIN_MEDICAL, 'medical')
    elif section_name == 'pharmaceutical':
        domain_specific['pharma_terms'] = find_domain_matches(decoded_list, LATIN_PHARMACEUTICAL, 'pharma')
        domain_specific['botanical_terms'] = find_domain_matches(decoded_list, LATIN_BOTANICAL, 'botanical')
    
    top_decoded = []
    for decoded, count in word_freq.most_common(30):
        match, score, mtype = find_latin_match(decoded)
        top_decoded.append({
            'decoded': decoded,
            'count': count,
            'latin_match': match if mtype != 'none' else None
        })
    
    return {
        'name': SECTIONS[section_name]['name'],
        'folios': sorted(pages.keys()),
        'total_words': total,
        'unique_words': len(word_freq),
        'latin_match_rate': round(latin_rate, 3),
        'match_breakdown': matches,
        'top_decoded_words': top_decoded,
        'domain_specific': domain_specific,
        'word_analysis': all_words[:200]
    }


def calculate_vocabulary_overlap(sections_data):
    vocab_sets = {}
    for name, data in sections_data.items():
        if data:
            words = set(w['decoded'] for w in data.get('word_analysis', []))
            vocab_sets[name] = words
    
    if 'botanical' not in vocab_sets:
        return {}
    
    botanical_vocab = vocab_sets['botanical']
    overlap = {}
    
    for name, vocab in vocab_sets.items():
        if name != 'botanical' and vocab:
            shared = botanical_vocab & vocab
            overlap[name] = {
                'shared_count': len(shared),
                'botanical_total': len(botanical_vocab),
                'section_total': len(vocab),
                'overlap_pct': round(len(shared) / len(vocab), 3) if vocab else 0,
                'sample_shared': list(shared)[:20]
            }
    
    all_words = set()
    for v in vocab_sets.values():
        all_words |= v
    
    universal = all_words.copy()
    for v in vocab_sets.values():
        universal &= v
    
    return {
        'section_overlaps': overlap,
        'universal_words': list(universal)[:30],
        'total_unique_across_all': len(all_words)
    }


def analyze_all_sections():
    print("🔬 Track 25: Cross-Section Validation")
    print("=" * 70)
    
    text = load_transcription()
    results = {
        'sections': {},
        'comparison': {},
        'vocabulary_analysis': {},
        'consistency_assessment': {}
    }
    
    for section_name in SECTIONS.keys():
        print(f"\n📑 Extracting {SECTIONS[section_name]['name']} section...")
        pages = extract_section(text, section_name)
        
        if pages:
            print(f"   Found {len(pages)} folios")
            analysis = analyze_section(section_name, pages)
            if analysis:
                results['sections'][section_name] = analysis
                print(f"   📊 Words: {analysis['total_words']}, Latin match: {analysis['latin_match_rate']:.1%}")
            else:
                print(f"   ⚠️ No words extracted")
        else:
            print(f"   ⚠️ No pages found for this section")
    
    if 'botanical' in results['sections']:
        bot_rate = results['sections']['botanical']['latin_match_rate']
        comparison = {'botanical': bot_rate}
        
        for name, data in results['sections'].items():
            if name != 'botanical':
                comparison[name] = data['latin_match_rate']
        
        results['comparison'] = {
            'match_rates': comparison,
            'botanical_baseline': bot_rate,
            'deviations': {
                name: round(rate - bot_rate, 3) 
                for name, rate in comparison.items() 
                if name != 'botanical'
            }
        }
    
    results['vocabulary_analysis'] = calculate_vocabulary_overlap(results['sections'])
    
    rates = [d['latin_match_rate'] for d in results['sections'].values() if d]
    if rates:
        avg_rate = sum(rates) / len(rates)
        variance = sum((r - avg_rate) ** 2 for r in rates) / len(rates)
        std_dev = variance ** 0.5
        
        consistency = 'HIGH' if std_dev < 0.1 else 'MEDIUM' if std_dev < 0.2 else 'LOW'
        
        results['consistency_assessment'] = {
            'average_match_rate': round(avg_rate, 3),
            'std_deviation': round(std_dev, 3),
            'consistency_level': consistency,
            'interpretation': get_interpretation(consistency, std_dev, rates)
        }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Saved to {OUTPUT_JSON}")
    
    generate_report(results)
    
    return results


def get_interpretation(consistency, std_dev, rates):
    if consistency == 'HIGH':
        return ("Same phonetic cipher appears to work consistently across all sections. "
                "This strongly supports the hypothesis that the entire manuscript uses "
                "a unified encoding system.")
    elif consistency == 'MEDIUM':
        return ("Moderate variation in match rates between sections. This could indicate: "
                "1) Different scribes with slight variations, 2) Topic-specific vocabulary "
                "not captured in Latin word lists, or 3) Some sections may use modified encoding.")
    else:
        return ("Significant variation between sections. This may indicate: "
                "1) Different cipher systems for different sections, 2) The botanical mapping "
                "may be overfitting to that section, or 3) Some sections may be in a different "
                "language entirely.")


def generate_report(results):
    r = []
    r.append("# Cross-Section Validation Report")
    r.append("")
    r.append("## Overview")
    r.append("Testing if the phonetic mapping developed for botanical section works across other manuscript sections.")
    r.append("")
    
    r.append("## Section Summary")
    r.append("")
    r.append("| Section | Folios | Words | Unique | Latin Match |")
    r.append("|---------|--------|-------|--------|-------------|")
    for name, data in results['sections'].items():
        if data:
            r.append(f"| {data['name']} | {len(data['folios'])} | {data['total_words']} | {data['unique_words']} | {data['latin_match_rate']:.1%} |")
    r.append("")
    
    r.append("## Match Rate Comparison")
    r.append("")
    if results['comparison']:
        bot = results['comparison'].get('botanical_baseline', 0)
        r.append(f"**Botanical baseline**: {bot:.1%}")
        r.append("")
        r.append("| Section | Match Rate | Deviation from Botanical |")
        r.append("|---------|------------|-------------------------|")
        for name, rate in results['comparison'].get('match_rates', {}).items():
            dev = results['comparison'].get('deviations', {}).get(name, 0)
            if name == 'botanical':
                r.append(f"| {name} | {rate:.1%} | baseline |")
            else:
                sign = '+' if dev >= 0 else ''
                r.append(f"| {name} | {rate:.1%} | {sign}{dev:.1%} |")
    r.append("")
    
    r.append("## Domain-Specific Vocabulary")
    r.append("")
    for name, data in results['sections'].items():
        if data and data.get('domain_specific'):
            r.append(f"### {data['name']}")
            for domain_name, matches in data['domain_specific'].items():
                if matches:
                    r.append(f"\n**{domain_name.replace('_', ' ').title()}**: {len(matches)} matches")
                    r.append("")
                    r.append("| Decoded | Latin Match | Similarity |")
                    r.append("|---------|-------------|------------|")
                    for m in sorted(matches, key=lambda x: -x['similarity'])[:10]:
                        r.append(f"| {m['decoded']} | {m['domain_match']} | {m['similarity']:.1%} |")
            r.append("")
    
    r.append("## Vocabulary Overlap")
    r.append("")
    vocab = results.get('vocabulary_analysis', {})
    if vocab.get('section_overlaps'):
        r.append("### Overlap with Botanical Section")
        r.append("")
        r.append("| Section | Shared Words | Overlap % |")
        r.append("|---------|--------------|-----------|")
        for name, overlap in vocab['section_overlaps'].items():
            r.append(f"| {name} | {overlap['shared_count']} | {overlap['overlap_pct']:.1%} |")
        r.append("")
    
    if vocab.get('universal_words'):
        r.append("### Universal Words (in all sections)")
        r.append("")
        r.append(", ".join(vocab['universal_words'][:20]))
        r.append("")
    
    r.append("## Consistency Assessment")
    r.append("")
    assess = results.get('consistency_assessment', {})
    if assess:
        r.append(f"- **Average match rate**: {assess.get('average_match_rate', 0):.1%}")
        r.append(f"- **Standard deviation**: {assess.get('std_deviation', 0):.3f}")
        r.append(f"- **Consistency level**: {assess.get('consistency_level', 'N/A')}")
        r.append("")
        r.append(f"**Interpretation**: {assess.get('interpretation', '')}")
    r.append("")
    
    r.append("## Conclusion")
    r.append("")
    if assess.get('consistency_level') == 'HIGH':
        r.append("✅ **VALIDATION SUCCESSFUL**: The phonetic mapping appears to work consistently")
        r.append("across all manuscript sections, supporting the unified cipher hypothesis.")
    elif assess.get('consistency_level') == 'MEDIUM':
        r.append("⚠️ **PARTIAL VALIDATION**: The mapping shows moderate consistency. Some sections")
        r.append("may require vocabulary expansion or mapping refinement.")
    else:
        r.append("❌ **VALIDATION CONCERNS**: Significant variation between sections suggests the")
        r.append("botanical mapping may not generalize well, or different sections use different systems.")
    r.append("")
    
    r.append("## Top Decoded Words by Section")
    r.append("")
    for name, data in results['sections'].items():
        if data and data.get('top_decoded_words'):
            r.append(f"### {data['name']}")
            r.append("")
            r.append("| Decoded | Count | Latin Match |")
            r.append("|---------|-------|-------------|")
            for w in data['top_decoded_words'][:15]:
                latin = w['latin_match'] if w['latin_match'] else '-'
                r.append(f"| {w['decoded']} | {w['count']} | {latin} |")
            r.append("")
    
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(r))
    print(f"✅ Saved to {OUTPUT_REPORT}")


if __name__ == '__main__':
    analyze_all_sections()
