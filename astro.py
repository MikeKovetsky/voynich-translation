#!/usr/bin/env python3
"""
Track 3: Astronomical Section Analysis
Analyze zodiac pages & circular diagrams to find star/month name candidates
"""

import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from phonetic import LATIN_MAP, apply_map

ASTRO_FOLIOS = [
    '67r1', '67r2', '67v1', '67v2',
    '68r1', '68r2', '68r3', '68v1', '68v2', '68v3',
    '69r', '69v',
    '70r1', '70r2', '70v1', '70v2',
    '71r', '71v',
    '72r1', '72r2', '72r3', '72v1', '72v2', '72v3',
    '73r', '73v'
]

ZODIAC_INFO = {
    '70v2': {'sign': 'Pisces', 'month': 'March', 'latin_month': 'Martius'},
    '70v1': {'sign': 'Aries', 'month': 'April', 'latin_month': 'Aprilis'},
    '71r': {'sign': 'Aries', 'month': 'April', 'latin_month': 'Aprilis'},
    '71v': {'sign': 'Taurus', 'month': 'May', 'latin_month': 'Maius'},
    '72r1': {'sign': 'Taurus', 'month': 'May', 'latin_month': 'Maius'},
    '72r2': {'sign': 'Gemini', 'month': 'June', 'latin_month': 'Junius'},
    '72r3': {'sign': 'Cancer', 'month': 'July', 'latin_month': 'Julius'},
    '72v3': {'sign': 'Leo', 'month': 'August', 'latin_month': 'Augustus'},
    '72v2': {'sign': 'Virgo', 'month': 'September', 'latin_month': 'September'},
    '72v1': {'sign': 'Libra', 'month': 'October', 'latin_month': 'October'},
    '73r': {'sign': 'Scorpio', 'month': 'November', 'latin_month': 'November'},
    '73v': {'sign': 'Sagittarius', 'month': 'December', 'latin_month': 'December'},
}

STAR_NAMES = {
    'Aldebaran': {'arabic': 'al-Dabaran', 'constellation': 'Taurus', 'meaning': 'the follower'},
    'Regulus': {'arabic': 'Qalb al-Asad', 'constellation': 'Leo', 'meaning': 'heart of the lion'},
    'Spica': {'arabic': 'al-Simak', 'constellation': 'Virgo', 'meaning': 'ear of grain'},
    'Antares': {'arabic': 'Qalb al-Aqrab', 'constellation': 'Scorpio', 'meaning': 'heart of the scorpion'},
    'Fomalhaut': {'arabic': 'Fam al-Hut', 'constellation': 'Pisces Austrinus', 'meaning': 'mouth of the fish'},
    'Vega': {'arabic': 'al-Nasr al-Waqi', 'constellation': 'Lyra', 'meaning': 'falling eagle'},
    'Deneb': {'arabic': 'Dhanab al-Dajaja', 'constellation': 'Cygnus', 'meaning': 'tail of the hen'},
    'Altair': {'arabic': 'al-Nasr al-Tair', 'constellation': 'Aquila', 'meaning': 'flying eagle'},
    'Sirius': {'arabic': 'al-Shira', 'constellation': 'Canis Major', 'meaning': 'the leader'},
    'Capella': {'arabic': 'al-Ayyuq', 'constellation': 'Auriga', 'meaning': 'the driver'},
    'Procyon': {'arabic': 'al-Shira al-Shamiya', 'constellation': 'Canis Minor', 'meaning': 'Syrian dog star'},
    'Betelgeuse': {'arabic': 'Yad al-Jawza', 'constellation': 'Orion', 'meaning': 'hand of Orion'},
    'Rigel': {'arabic': 'Rijl al-Jawza', 'constellation': 'Orion', 'meaning': 'foot of Orion'},
    'Pollux': {'arabic': 'Rasalhague', 'constellation': 'Gemini', 'meaning': 'head of the twin'},
    'Castor': {'arabic': 'al-Ras al-Tawam', 'constellation': 'Gemini', 'meaning': 'head of the twin'},
    'Arcturus': {'arabic': 'al-Simak al-Ramih', 'constellation': 'Bootes', 'meaning': 'the lancer'},
    'Hamal': {'arabic': 'al-Hamal', 'constellation': 'Aries', 'meaning': 'the ram'},
    'Achernar': {'arabic': 'Akhir al-Nahr', 'constellation': 'Eridanus', 'meaning': 'end of river'},
    'Elnath': {'arabic': 'al-Nath', 'constellation': 'Taurus', 'meaning': 'the butting one'},
    'Zubenelgenubi': {'arabic': 'al-Zuban al-Janubi', 'constellation': 'Libra', 'meaning': 'southern claw'},
}

LATIN_MONTHS = [
    'Januarius', 'Februarius', 'Martius', 'Aprilis', 'Maius', 'Junius',
    'Julius', 'Augustus', 'September', 'October', 'November', 'December'
]

ZODIAC_LATIN = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricornus', 'Aquarius', 'Pisces'
]


def load_raw():
    return Path('voynich_raw.txt').read_text(encoding='utf-8')


def extract_astro_pages(raw):
    """Extract all text from astronomical section"""
    pages = defaultdict(list)
    
    for line in raw.split('\n'):
        if not line.strip():
            continue
        
        match = re.match(r'<(\d+[rv]\d?)[^>]*>', line)
        if match:
            folio = match.group(1)
            folio_num = int(re.match(r'(\d+)', folio).group(1))
            
            if 67 <= folio_num <= 73:
                label_match = re.search(r'<([^>]+)>', line)
                if label_match:
                    section_id = label_match.group(1)
                    text = re.sub(r'<[^>]+>', '', line).strip()
                    text = re.sub(r'[-=]$', '', text)
                    pages[folio].append({
                        'section': section_id,
                        'text': text
                    })
    
    return pages


def extract_words(text):
    """Extract individual words from text"""
    clean = re.sub(r'[.,\-=]', ' ', text)
    words = [w.strip() for w in clean.split() if w.strip()]
    return words


def categorize_sections(pages):
    """Categorize text into labels (short) vs descriptive (long)"""
    categorized = {}
    
    for folio, sections in pages.items():
        labels = []
        descriptive = []
        rings = []
        radials = []
        
        for item in sections:
            section_id = item['section'].lower()
            text = item['text']
            words = extract_words(text)
            
            if 'ring' in section_id or 'spiral' in section_id:
                rings.append({'id': section_id, 'text': text, 'words': words})
            elif 'radial' in section_id:
                radials.append({'id': section_id, 'text': text, 'words': words})
            elif 'label' in section_id or 'center' in section_id:
                labels.extend(words)
            else:
                if len(words) <= 3:
                    labels.extend(words)
                else:
                    descriptive.append(text)
        
        categorized[folio] = {
            'labels': labels,
            'descriptive': descriptive,
            'rings': rings,
            'radials': radials
        }
    
    return categorized


def analyze_zodiac_labels(categorized):
    """Extract and analyze labels from zodiac pages"""
    zodiac_data = []
    
    for folio, info in ZODIAC_INFO.items():
        if folio in categorized:
            cat = categorized[folio]
            all_words = cat['labels'].copy()
            
            for ring in cat['rings']:
                all_words.extend(ring['words'])
            for radial in cat['radials']:
                all_words.extend(radial['words'])
            
            zodiac_data.append({
                'folio': folio,
                'sign': info['sign'],
                'month': info['month'],
                'latin_month': info['latin_month'],
                'word_count': len(all_words),
                'unique_words': len(set(all_words)),
                'labels': all_words[:50],
                'all_words': all_words
            })
    
    return zodiac_data


def find_repeated_patterns(zodiac_data):
    """Find words that repeat across multiple zodiac sections"""
    word_signs = defaultdict(list)
    
    for zd in zodiac_data:
        for word in set(zd['all_words']):
            if len(word) >= 3:
                word_signs[word].append(zd['sign'])
    
    repeated = []
    for word, signs in word_signs.items():
        if len(set(signs)) >= 3:
            repeated.append({
                'word': word,
                'appears_in': list(set(signs)),
                'count': len(signs)
            })
    
    repeated.sort(key=lambda x: -x['count'])
    return repeated[:50]


def phonetic_similarity(voynich_word, target, mapping):
    """Calculate similarity score between Voynich word and target"""
    decoded = apply_map(voynich_word, mapping).lower()
    target = target.lower()
    
    if decoded == target:
        return 1.0
    
    if target in decoded or decoded in target:
        return 0.7
    
    matches = sum(1 for c in decoded if c in target)
    return matches / max(len(decoded), len(target), 1)


def test_star_names(all_words, mapping=LATIN_MAP):
    """Test Voynich words against known star names"""
    results = []
    word_set = list(set(all_words))
    
    for star, info in STAR_NAMES.items():
        best_match = None
        best_score = 0
        
        test_names = [star.lower(), info['arabic'].lower().replace(' ', '').replace('-', '')]
        
        for voynich in word_set:
            if len(voynich) < 3:
                continue
            
            for target in test_names:
                score = phonetic_similarity(voynich, target, mapping)
                if score > best_score:
                    best_score = score
                    best_match = voynich
        
        results.append({
            'star': star,
            'arabic': info['arabic'],
            'constellation': info['constellation'],
            'best_voynich_match': best_match,
            'decoded': apply_map(best_match, mapping) if best_match else None,
            'score': round(best_score, 3)
        })
    
    results.sort(key=lambda x: -x['score'])
    return results


def test_month_names(zodiac_data, mapping=LATIN_MAP):
    """Test words in each zodiac section against expected month names"""
    results = []
    
    for zd in zodiac_data:
        expected_month = zd['latin_month'].lower()
        words = zd['all_words']
        
        best_match = None
        best_score = 0
        
        for word in words:
            if len(word) < 3:
                continue
            score = phonetic_similarity(word, expected_month, mapping)
            if score > best_score:
                best_score = score
                best_match = word
        
        results.append({
            'sign': zd['sign'],
            'folio': zd['folio'],
            'expected_month': zd['latin_month'],
            'best_match': best_match,
            'decoded': apply_map(best_match, mapping) if best_match else None,
            'score': round(best_score, 3)
        })
    
    return results


def analyze_radial_structure(categorized):
    """Analyze the structure of radial text (reading direction, patterns)"""
    analysis = []
    
    for folio, cat in categorized.items():
        if cat['radials']:
            radial_words = []
            for r in cat['radials']:
                radial_words.extend(r['words'])
            
            word_lens = [len(w) for w in radial_words]
            
            analysis.append({
                'folio': folio,
                'radial_count': len(cat['radials']),
                'total_words': len(radial_words),
                'avg_word_len': round(sum(word_lens) / len(word_lens), 2) if word_lens else 0,
                'sample_words': radial_words[:10]
            })
    
    return analysis


def find_potential_decans(zodiac_data):
    """Look for 30-word patterns (decans = 10° divisions, 3 per sign)"""
    results = []
    
    for zd in zodiac_data:
        word_count = zd['word_count']
        thirds = word_count // 3 if word_count >= 30 else 0
        
        results.append({
            'sign': zd['sign'],
            'folio': zd['folio'],
            'total_words': word_count,
            'possible_decans': thirds,
            'matches_30_pattern': 25 <= word_count <= 35
        })
    
    return results


def find_unique_zodiac_words(zodiac_data):
    """Find words unique to each zodiac section - potential star names"""
    all_words = Counter()
    section_words = {}
    
    for zd in zodiac_data:
        section_words[zd['sign'] + '_' + zd['folio']] = set(zd['all_words'])
        for w in zd['all_words']:
            all_words[w] += 1
    
    unique_per_section = {}
    for key, words in section_words.items():
        unique = [w for w in words if all_words[w] == 1 and len(w) >= 4]
        unique_per_section[key] = sorted(unique, key=len, reverse=True)
    
    return unique_per_section


def test_zodiac_star_correlation(zodiac_data, mapping=LATIN_MAP):
    """Test if stars in each constellation appear in matching zodiac section"""
    constellation_to_sign = {
        'Aries': 'Aries',
        'Taurus': 'Taurus', 
        'Gemini': 'Gemini',
        'Cancer': 'Cancer',
        'Leo': 'Leo',
        'Virgo': 'Virgo',
        'Libra': 'Libra',
        'Scorpio': 'Scorpio',
        'Sagittarius': 'Sagittarius',
    }
    
    results = []
    
    for star, info in STAR_NAMES.items():
        const = info['constellation']
        expected_sign = constellation_to_sign.get(const)
        
        if not expected_sign:
            continue
        
        matching_sections = [zd for zd in zodiac_data if zd['sign'] == expected_sign]
        
        for section in matching_sections:
            words = section['all_words']
            
            best_match = None
            best_score = 0
            
            test_names = [star.lower(), info['arabic'].lower().replace(' ', '').replace('-', '')]
            
            for word in words:
                if len(word) < 3:
                    continue
                for target in test_names:
                    score = phonetic_similarity(word, target, mapping)
                    if score > best_score:
                        best_score = score
                        best_match = word
            
            if best_score > 0.3:
                results.append({
                    'star': star,
                    'constellation': const,
                    'expected_in': expected_sign,
                    'folio': section['folio'],
                    'best_match': best_match,
                    'decoded': apply_map(best_match, mapping) if best_match else None,
                    'score': round(best_score, 3)
                })
    
    results.sort(key=lambda x: -x['score'])
    return results


def main():
    print("=" * 70)
    print("🌟 TRACK 3: ASTRONOMICAL SECTION ANALYSIS 🌟")
    print("=" * 70)
    
    raw = load_raw()
    pages = extract_astro_pages(raw)
    
    print(f"\n📊 Extracted {len(pages)} folios from astronomical section")
    print(f"   Folios: {', '.join(sorted(pages.keys()))}")
    
    categorized = categorize_sections(pages)
    
    print("\n" + "=" * 70)
    print("🔭 CIRCULAR DIAGRAMS ANALYSIS (67r-69v)")
    print("=" * 70)
    
    for folio in ['67r1', '67r2', '67v1', '67v2', '68r1', '68r2', '68r3', '68v1', '68v2', '68v3', '69r', '69v']:
        if folio in categorized:
            cat = categorized[folio]
            print(f"\n  {folio}:")
            print(f"    Labels: {len(cat['labels'])} words")
            print(f"    Rings: {len(cat['rings'])} sections")
            print(f"    Radials: {len(cat['radials'])} sections")
            if cat['labels'][:5]:
                print(f"    Sample labels: {cat['labels'][:5]}")
    
    print("\n" + "=" * 70)
    print("♈ ZODIAC SECTION ANALYSIS (70v-73v)")
    print("=" * 70)
    
    zodiac_data = analyze_zodiac_labels(categorized)
    
    for zd in zodiac_data:
        print(f"\n  {zd['sign']} (f{zd['folio']}) - {zd['month']}")
        print(f"    Words: {zd['word_count']} total, {zd['unique_words']} unique")
        print(f"    Sample: {zd['labels'][:8]}")
    
    print("\n" + "=" * 70)
    print("🔄 REPEATED PATTERNS ACROSS ZODIAC")
    print("=" * 70)
    
    repeated = find_repeated_patterns(zodiac_data)
    print(f"\n  Words appearing in 3+ zodiac sections:")
    for r in repeated[:15]:
        print(f"    '{r['word']}' -> {r['appears_in']}")
    
    print("\n" + "=" * 70)
    print("🎯 UNIQUE WORDS PER ZODIAC (potential star names)")
    print("=" * 70)
    
    unique_words = find_unique_zodiac_words(zodiac_data)
    for section, words in unique_words.items():
        print(f"\n  {section}:")
        if words:
            decoded = [(w, apply_map(w, LATIN_MAP)) for w in words[:8]]
            for orig, dec in decoded:
                print(f"    '{orig}' -> '{dec}'")
    
    print("\n" + "=" * 70)
    print("⭐ STAR NAME MATCHING")
    print("=" * 70)
    
    all_astro_words = []
    for cat in categorized.values():
        all_astro_words.extend(cat['labels'])
        for ring in cat['rings']:
            all_astro_words.extend(ring['words'])
        for radial in cat['radials']:
            all_astro_words.extend(radial['words'])
    
    star_matches = test_star_names(all_astro_words)
    
    print("\n  Top star name matches (Latin phonetic map):")
    for sm in star_matches[:10]:
        print(f"    {sm['star']:15} ({sm['constellation']:10}) -> '{sm['best_voynich_match']}' = '{sm['decoded']}' (score: {sm['score']})")
    
    high_confidence = [s for s in star_matches if s['score'] >= 0.5]
    if high_confidence:
        print(f"\n  🔥 HIGH CONFIDENCE MATCHES (score >= 0.5):")
        for sm in high_confidence:
            print(f"    {sm['star']} -> '{sm['best_voynich_match']}' ({sm['decoded']})")
    
    print("\n" + "=" * 70)
    print("🔗 STAR-ZODIAC CORRELATION (stars in expected constellations)")
    print("=" * 70)
    
    zodiac_stars = test_zodiac_star_correlation(zodiac_data)
    print("\n  Stars found in their expected zodiac sections:")
    for zs in zodiac_stars[:15]:
        print(f"    {zs['star']:15} ({zs['constellation']:10}) in f{zs['folio']}: '{zs['best_match']}' -> '{zs['decoded']}' (score: {zs['score']})")
    
    print("\n" + "=" * 70)
    print("📅 MONTH NAME MATCHING")
    print("=" * 70)
    
    month_matches = test_month_names(zodiac_data)
    
    print("\n  Month name matches by zodiac section:")
    for mm in month_matches:
        print(f"    {mm['sign']:12} expects '{mm['expected_month']:10}' -> '{mm['best_match']}' = '{mm['decoded']}' (score: {mm['score']})")
    
    print("\n" + "=" * 70)
    print("🌀 RADIAL TEXT STRUCTURE")
    print("=" * 70)
    
    radial_analysis = analyze_radial_structure(categorized)
    
    for ra in radial_analysis:
        print(f"\n  {ra['folio']}:")
        print(f"    Radial sections: {ra['radial_count']}")
        print(f"    Total words: {ra['total_words']}")
        print(f"    Avg word length: {ra['avg_word_len']}")
    
    print("\n" + "=" * 70)
    print("🎯 DECAN ANALYSIS (30 divisions per sign)")
    print("=" * 70)
    
    decan_results = find_potential_decans(zodiac_data)
    
    for dr in decan_results:
        match_mark = "✅" if dr['matches_30_pattern'] else "❌"
        print(f"  {dr['sign']:12} f{dr['folio']}: {dr['total_words']} words {match_mark}")
    
    print("\n" + "=" * 70)
    print("📁 SAVING RESULTS")
    print("=" * 70)
    
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    astro_text = {
        'pages': [{
            'folio': folio,
            'labels': cat['labels'],
            'rings': [{'id': r['id'], 'text': r['text']} for r in cat['rings']],
            'radials': [{'id': r['id'], 'text': r['text']} for r in cat['radials']],
            'descriptive': cat['descriptive']
        } for folio, cat in categorized.items()]
    }
    
    with open(results_dir / 'astronomical_text.json', 'w') as f:
        json.dump(astro_text, f, indent=2)
    print("  ✅ Saved results/astronomical_text.json")
    
    zodiac_results = {
        'zodiac_sections': [{
            'sign': zd['sign'],
            'folio': zd['folio'],
            'month': zd['month'],
            'labels': zd['labels'],
            'word_count': zd['word_count']
        } for zd in zodiac_data],
        'repeated_patterns': repeated
    }
    
    with open(results_dir / 'zodiac_analysis.json', 'w') as f:
        json.dump(zodiac_results, f, indent=2)
    print("  ✅ Saved results/zodiac_analysis.json")
    
    star_results = {
        'attempts': star_matches,
        'best_matches': [s for s in star_matches if s['score'] >= 0.4]
    }
    
    with open(results_dir / 'star_name_matches.json', 'w') as f:
        json.dump(star_results, f, indent=2)
    print("  ✅ Saved results/star_name_matches.json")
    
    print("\n" + "=" * 70)
    print("💡 CONCLUSIONS")
    print("=" * 70)
    
    print("""
  FINDINGS:
  
  1. The astronomical section contains structured circular diagrams
     with radiating text (rings + radials) - consistent with medieval
     astronomical/astrological charts
  
  2. Zodiac sections have varying word counts (not exactly 30),
     suggesting labels may not be strictly 1-per-decan
  
  3. Many words repeat across zodiac signs - these are likely
     grammatical elements, not proper nouns
  
  4. Star name matching shows some potential candidates but no
     definitive high-confidence matches yet
  
  NEXT STEPS:
  
  - Compare unique words (appearing in only one zodiac section)
    as more likely star name candidates
  - Test alternative phonetic mappings
  - Cross-reference radial positions with known star positions
""")


if __name__ == '__main__':
    main()



