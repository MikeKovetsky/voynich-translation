#!/usr/bin/env python3
"""
Track 9: Zodiac Month Name Extraction & Validation
Find month names in zodiac sections - a controlled test with known answers
"""

import json
from collections import Counter, defaultdict
from pathlib import Path
from difflib import SequenceMatcher

MONTH_NAMES = {
    'latin': {
        'March': 'martius', 'April': 'aprilis', 'May': 'maius',
        'June': 'iunius', 'July': 'iulius', 'August': 'augustus',
        'September': 'september', 'October': 'october', 'November': 'november',
        'December': 'december', 'January': 'ianuarius', 'February': 'februarius'
    },
    'italian': {
        'March': 'marzo', 'April': 'aprile', 'May': 'maggio',
        'June': 'giugno', 'July': 'luglio', 'August': 'agosto',
        'September': 'settembre', 'October': 'ottobre', 'November': 'novembre',
        'December': 'dicembre', 'January': 'gennaio', 'February': 'febbraio'
    },
    'basque': {
        'March': 'martxoa', 'April': 'apirila', 'May': 'maiatza',
        'June': 'ekaina', 'July': 'uztaila', 'August': 'abuztua',
        'September': 'iraila', 'October': 'urria', 'November': 'azaroa',
        'December': 'abendua', 'January': 'urtarrila', 'February': 'otsaila'
    },
    'hungarian': {
        'March': 'marcius', 'April': 'aprilis', 'May': 'majus',
        'June': 'junius', 'July': 'julius', 'August': 'augusztus',
        'September': 'szeptember', 'October': 'oktober', 'November': 'november',
        'December': 'december', 'January': 'januar', 'February': 'februar'
    }
}

ZODIAC_NAMES = {
    'latin': {
        'Pisces': 'pisces', 'Aries': 'aries', 'Taurus': 'taurus',
        'Gemini': 'gemini', 'Cancer': 'cancer', 'Leo': 'leo',
        'Virgo': 'virgo', 'Libra': 'libra', 'Scorpio': 'scorpius',
        'Sagittarius': 'sagittarius', 'Capricorn': 'capricornus', 'Aquarius': 'aquarius'
    },
    'italian': {
        'Pisces': 'pesci', 'Aries': 'ariete', 'Taurus': 'toro',
        'Gemini': 'gemelli', 'Cancer': 'cancro', 'Leo': 'leone',
        'Virgo': 'vergine', 'Libra': 'bilancia', 'Scorpio': 'scorpione',
        'Sagittarius': 'sagittario', 'Capricorn': 'capricorno', 'Aquarius': 'acquario'
    },
    'basque': {
        'Pisces': 'arrainak', 'Aries': 'aharia', 'Taurus': 'zezena',
        'Gemini': 'bikiak', 'Cancer': 'karramarroa', 'Leo': 'lehoia',
        'Virgo': 'birjina', 'Libra': 'balantza', 'Scorpio': 'eskorpioia',
        'Sagittarius': 'sagitario', 'Capricorn': 'akerra', 'Aquarius': 'akuarioa'
    },
    'hungarian': {
        'Pisces': 'halak', 'Aries': 'kos', 'Taurus': 'bika',
        'Gemini': 'ikrek', 'Cancer': 'rak', 'Leo': 'oroszlan',
        'Virgo': 'szuz', 'Libra': 'merleg', 'Scorpio': 'skorpio',
        'Sagittarius': 'nyilas', 'Capricorn': 'bak', 'Aquarius': 'vizonto'
    }
}

PHONETIC_MAPS = {
    'latin': {
        'o': 'a', '9': 's', 'a': 'e', 'c': 'c', '1': 't', 'e': 'i',
        '8': 'd', 'h': 'r', 'y': 'i', 'k': 'n', '4': 'm', 'm': 'm',
        '2': 'b', 'C': 'ch', '7': 'l', 's': 'x', 'n': 'n', 'p': 'p',
        'K': 'c', 'g': 'g', 'j': 'i', 'W': 'u', 'H': 'h', 'z': 'z',
        'u': 'u', 'f': 'f', 'A': 'a', 'd': 'v', 'J': 'i', 'Z': 'z',
        'S': 's', 'i': 'i', '%': '', '?': '', '(': '', '*': '', '¼': '',
        '½': '', 'ò': 'o', 'Ý': '', 't': 't', 'b': 'b', 'E': 'e', 'M': 'm',
        'Q': 'q', 'I': 'i', 'N': 'n', 'l': 'l',
    },
    'italian': {
        'o': 'o', '9': 'e', 'a': 'a', 'c': 'c', '1': 'l', 'e': 'e',
        '8': 'd', 'h': 'r', 'y': 'i', 'k': 'n', '4': 'qu', 'm': 'mo',
        '2': 's', 'C': 'ce', '7': 'gn', 's': 'z', 'n': 'n', 'p': 'p',
        'g': 'g', 'j': 'i', 'W': 'u', 'H': 'h', 'z': 'z', 'u': 'u',
        'K': 'c', 'f': 'f', 'A': 'a', 'd': 'v', 'i': 'i',
    },
    'basque': {
        'o': 'a', '9': 'a', 'a': 'e', 'c': 'k', '1': 'z', 'e': 'i',
        '8': 'd', 'h': 'rr', 'y': 'i', 'k': 'n', '4': 'b', 'm': 'm',
        '2': 'ts', 'C': 'tx', '7': 'l', 's': 's', 'n': 'n', 'p': 'p',
        'g': 'g', 'j': 'i', 'W': 'u', 'H': 'h', 'z': 'z', 'u': 'u',
        'K': 'k', 'f': 'f', 'A': 'a', 'd': 'b', 'i': 'i',
    },
    'hungarian': {
        'o': 'a', '9': 's', 'a': 'e', 'c': 'k', '1': 'sz', 'e': 'i',
        '8': 'd', 'h': 'r', 'y': 'i', 'k': 'n', '4': 'm', 'm': 'm',
        '2': 'b', 'C': 'cs', '7': 'l', 's': 's', 'n': 'n', 'p': 'p',
        'g': 'g', 'j': 'j', 'W': 'u', 'H': 'h', 'z': 'z', 'u': 'u',
        'K': 'k', 'f': 'f', 'A': 'a', 'd': 'v', 'i': 'i',
    }
}

def decode_word(word, lang):
    mapping = PHONETIC_MAPS.get(lang, PHONETIC_MAPS['latin'])
    result = []
    for char in word:
        if char in mapping:
            result.append(mapping[char])
        else:
            result.append(char)
    return ''.join(result).lower()

def similarity(a, b):
    a_clean = ''.join(c for c in a.lower() if c.isalpha())
    b_clean = ''.join(c for c in b.lower() if c.isalpha())
    if not a_clean or not b_clean:
        return 0.0
    return SequenceMatcher(None, a_clean, b_clean).ratio()

def consonant_skeleton(s):
    vowels = 'aeiouáéíóúàèìòù'
    return ''.join(c for c in s.lower() if c.isalpha() and c not in vowels)

def skeleton_match(decoded, target):
    sk1 = consonant_skeleton(decoded)
    sk2 = consonant_skeleton(target)
    if not sk1 or not sk2:
        return 0.0
    return SequenceMatcher(None, sk1, sk2).ratio()

def load_zodiac_data():
    with open('results/zodiac_analysis.json') as f:
        return json.load(f)

def get_unique_words(sections):
    all_words = defaultdict(list)
    for sec in sections:
        for label in sec['labels']:
            clean = label.strip()
            if len(clean) >= 2:
                all_words[clean].append(sec['sign'])
    unique_per_section = defaultdict(list)
    for sec in sections:
        sign = sec['sign']
        for label in sec['labels']:
            clean = label.strip()
            if len(clean) >= 3 and len(all_words[clean]) == 1:
                unique_per_section[sign].append(clean)
    return unique_per_section

def analyze_section(section, unique_words, lang):
    sign = section['sign']
    month = section['month']
    folio = section['folio']
    month_target = MONTH_NAMES[lang].get(month, '')
    zodiac_target = ZODIAC_NAMES[lang].get(sign, '')
    all_labels = section['labels']
    month_candidates = []
    zodiac_candidates = []
    for label in all_labels:
        if len(label) < 3:
            continue
        decoded = decode_word(label, lang)
        m_sim = similarity(decoded, month_target)
        m_skel = skeleton_match(decoded, month_target)
        m_score = (m_sim * 0.6 + m_skel * 0.4)
        if m_score > 0.25:
            month_candidates.append({
                'voynich_word': label,
                'decoded': decoded,
                'best_match': month_target,
                'language': lang,
                'score': round(m_score, 3),
                'sim_score': round(m_sim, 3),
                'skel_score': round(m_skel, 3)
            })
        z_sim = similarity(decoded, zodiac_target)
        z_skel = skeleton_match(decoded, zodiac_target)
        z_score = (z_sim * 0.6 + z_skel * 0.4)
        if z_score > 0.25:
            zodiac_candidates.append({
                'voynich_word': label,
                'decoded': decoded,
                'best_match': zodiac_target,
                'language': lang,
                'score': round(z_score, 3),
                'sim_score': round(z_sim, 3),
                'skel_score': round(z_skel, 3)
            })
    month_candidates.sort(key=lambda x: x['score'], reverse=True)
    zodiac_candidates.sort(key=lambda x: x['score'], reverse=True)
    return {
        'zodiac_sign': sign,
        'folio': folio,
        'expected_month': month,
        'unique_words': unique_words.get(sign, [])[:10],
        'month_name_candidates': month_candidates[:5],
        'zodiac_name_candidates': zodiac_candidates[:5],
    }

def main():
    print("=" * 70)
    print("🔮 TRACK 9: ZODIAC MONTH NAME ANALYSIS")
    print("=" * 70)
    
    data = load_zodiac_data()
    sections = data['zodiac_sections']
    unique_words = get_unique_words(sections)
    
    print(f"\n📊 Loaded {len(sections)} zodiac sections")
    for sign, words in unique_words.items():
        print(f"  {sign}: {len(words)} unique words")
    
    results = {
        'sections': [],
        'language_scores': {},
        'best_performing_language': None,
        'identified_month_names': [],
        'overall_success': False,
        'breakthrough': None
    }
    
    lang_totals = defaultdict(lambda: {'matches': 0, 'total_score': 0.0, 'count': 0})
    
    for lang in ['latin', 'italian', 'basque', 'hungarian']:
        print(f"\n{'='*70}")
        print(f"🔤 TESTING {lang.upper()} MAPPINGS")
        print("=" * 70)
        
        lang_sections = []
        for sec in sections:
            analysis = analyze_section(sec, unique_words, lang)
            lang_sections.append(analysis)
            if analysis['month_name_candidates']:
                best = analysis['month_name_candidates'][0]
                lang_totals[lang]['total_score'] += best['score']
                lang_totals[lang]['count'] += 1
                if best['score'] >= 0.5:
                    lang_totals[lang]['matches'] += 1
                print(f"\n  {sec['sign']} ({sec['month']}):")
                print(f"    Best month match: {best['voynich_word']} → {best['decoded']}")
                print(f"    Target: {best['best_match']}, Score: {best['score']:.3f}")
                if analysis['zodiac_name_candidates']:
                    zb = analysis['zodiac_name_candidates'][0]
                    print(f"    Best zodiac: {zb['voynich_word']} → {zb['decoded']} (score: {zb['score']:.3f})")
        
        if lang == 'latin':
            results['sections'] = lang_sections
    
    print("\n" + "=" * 70)
    print("📈 LANGUAGE COMPARISON RESULTS")
    print("=" * 70)
    
    best_lang = None
    best_score = 0.0
    
    for lang, stats in lang_totals.items():
        avg = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        results['language_scores'][lang] = {
            'matches_above_05': stats['matches'],
            'average_score': round(avg, 3),
            'sections_analyzed': stats['count']
        }
        print(f"\n  {lang.upper()}:")
        print(f"    Matches (score >= 0.5): {stats['matches']}/12")
        print(f"    Average score: {avg:.3f}")
        
        if avg > best_score:
            best_score = avg
            best_lang = lang
    
    results['best_performing_language'] = {
        'language': best_lang,
        'total_matches': lang_totals[best_lang]['matches'],
        'average_score': round(best_score, 3)
    }
    
    print("\n" + "=" * 70)
    print("🏆 BEST MONTH NAME CANDIDATES")
    print("=" * 70)
    
    high_conf = []
    for sec in sections:
        for lang in ['latin', 'italian', 'basque', 'hungarian']:
            analysis = analyze_section(sec, unique_words, lang)
            for cand in analysis['month_name_candidates']:
                if cand['score'] >= 0.5:
                    high_conf.append({
                        'month': sec['month'],
                        'sign': sec['sign'],
                        'voynich': cand['voynich_word'],
                        'decoded': cand['decoded'],
                        'language': lang,
                        'confidence': cand['score']
                    })
    
    high_conf.sort(key=lambda x: x['confidence'], reverse=True)
    results['identified_month_names'] = high_conf[:15]
    
    for item in high_conf[:15]:
        print(f"\n  {item['month']} ({item['sign']}):")
        print(f"    {item['voynich']} → {item['decoded']}")
        print(f"    Language: {item['language']}, Confidence: {item['confidence']:.3f}")
    
    if high_conf and high_conf[0]['confidence'] >= 0.6:
        results['overall_success'] = True
        results['breakthrough'] = f"Found potential month name match: {high_conf[0]['voynich']} = {high_conf[0]['decoded']} ({high_conf[0]['language']}) for {high_conf[0]['month']}"
    
    print("\n" + "=" * 70)
    print("🔍 CROSS-SECTION PATTERN ANALYSIS")
    print("=" * 70)
    
    first_words = {}
    for sec in sections:
        if sec['labels']:
            first_words[sec['sign']] = sec['labels'][0]
    
    print("\n  First word per zodiac section:")
    for sign, word in first_words.items():
        decoded_lat = decode_word(word, 'latin')
        decoded_ita = decode_word(word, 'italian')
        print(f"    {sign:12} → {word:15} → LAT:{decoded_lat:15} ITA:{decoded_ita}")
    
    results['first_word_analysis'] = first_words
    
    with open('results/zodiac_month_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to results/zodiac_month_analysis.json")
    
    generate_report(results, sections, unique_words)
    
    print("\n" + "=" * 70)
    print("💡 CONCLUSIONS")
    print("=" * 70)
    
    if results['overall_success']:
        print(f"\n  ✅ BREAKTHROUGH: {results['breakthrough']}")
    else:
        print("\n  ⚠️ No definitive month name matches found (score >= 0.6)")
        print("  This could mean:")
        print("    1. The phonetic mappings are not quite right")
        print("    2. Month names use different encoding")
        print("    3. Labels might be nymph names, not months")
        print("    4. Source language is not in our test set")

def generate_report(results, sections, unique_words):
    lines = [
        "# Zodiac Month Name Analysis Report",
        "",
        "## Summary",
        "",
        f"**Best performing language:** {results['best_performing_language']['language']}",
        f"**Average match score:** {results['best_performing_language']['average_score']:.3f}",
        f"**High-confidence matches (≥0.5):** {results['best_performing_language']['total_matches']}/12",
        "",
        "## Results by Zodiac Section",
        "",
        "| Zodiac | Month | Best Voynich | Decoded | Language | Score |",
        "|--------|-------|--------------|---------|----------|-------|",
    ]
    
    for sec in results['sections']:
        if sec['month_name_candidates']:
            best = sec['month_name_candidates'][0]
            lines.append(f"| {sec['zodiac_sign']} | {sec['expected_month']} | {best['voynich_word']} | {best['decoded']} | {best['language']} | {best['score']:.2f} |")
        else:
            lines.append(f"| {sec['zodiac_sign']} | {sec['expected_month']} | - | - | - | - |")
    
    lines.extend([
        "",
        "## Language Scores",
        "",
        "| Language | Matches ≥0.5 | Avg Score |",
        "|----------|--------------|-----------|",
    ])
    
    for lang, stats in results['language_scores'].items():
        lines.append(f"| {lang.title()} | {stats['matches_above_05']} | {stats['average_score']:.3f} |")
    
    lines.extend([
        "",
        "## High Confidence Identifications",
        "",
    ])
    
    for item in results['identified_month_names'][:10]:
        lines.append(f"- **{item['month']}** ({item['sign']}): `{item['voynich']}` → `{item['decoded']}` [{item['language']}, {item['confidence']:.2f}]")
    
    lines.extend([
        "",
        "## Unique Words Per Section",
        "",
    ])
    
    for sec in sections:
        sign = sec['sign']
        words = unique_words.get(sign, [])[:5]
        if words:
            lines.append(f"- **{sign}**: {', '.join(words)}")
    
    lines.extend([
        "",
        "## Conclusions",
        "",
    ])
    
    if results['overall_success']:
        lines.append(f"✅ **BREAKTHROUGH:** {results['breakthrough']}")
    else:
        lines.extend([
            "⚠️ No definitive month name matches found with confidence ≥0.6",
            "",
            "Possible explanations:",
            "1. Phonetic mappings need refinement",
            "2. Month names use abbreviated forms or different encoding",
            "3. Labels might be nymph names/titles rather than months",
            "4. Source language is not Latin, Italian, Basque, or Hungarian",
        ])
    
    with open('results/zodiac_month_report.md', 'w') as f:
        f.write('\n'.join(lines))
    print(f"✅ Report saved to results/zodiac_month_report.md")

if __name__ == '__main__':
    main()
