"""
Track 40: Medieval Hebrew Text Comparison
Compare Voynich text with medieval Hebrew patterns, terminology, and structure.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from difflib import SequenceMatcher

import voynich_data as vd

HEBREW_MONTHS = {
    'Nisan': {'hebrew': 'ניסן', 'romanized': 'nisan', 'old': 'aviv', 'gregorian': 'March/April'},
    'Iyar': {'hebrew': 'אייר', 'romanized': 'iyar', 'old': 'ziv', 'gregorian': 'April/May'},
    'Sivan': {'hebrew': 'סיון', 'romanized': 'sivan', 'gregorian': 'May/June'},
    'Tammuz': {'hebrew': 'תמוז', 'romanized': 'tammuz', 'gregorian': 'June/July'},
    'Av': {'hebrew': 'אב', 'romanized': 'av', 'gregorian': 'July/August'},
    'Elul': {'hebrew': 'אלול', 'romanized': 'elul', 'gregorian': 'August/September'},
    'Tishrei': {'hebrew': 'תשרי', 'romanized': 'tishrei', 'gregorian': 'September/October'},
    'Cheshvan': {'hebrew': 'חשון', 'romanized': 'cheshvan', 'old': 'bul', 'gregorian': 'October/November'},
    'Kislev': {'hebrew': 'כסלו', 'romanized': 'kislev', 'gregorian': 'November/December'},
    'Tevet': {'hebrew': 'טבת', 'romanized': 'tevet', 'gregorian': 'December/January'},
    'Shevat': {'hebrew': 'שבט', 'romanized': 'shevat', 'gregorian': 'January/February'},
    'Adar': {'hebrew': 'אדר', 'romanized': 'adar', 'gregorian': 'February/March'},
}

HEBREW_PLANT_TERMS = {
    'shoresh': {'hebrew': 'שורש', 'meaning': 'root'},
    'aleh': {'hebrew': 'עלה', 'meaning': 'leaf'},
    'perach': {'hebrew': 'פרח', 'meaning': 'flower'},
    'pri': {'hebrew': 'פרי', 'meaning': 'fruit'},
    'zera': {'hebrew': 'זרע', 'meaning': 'seed'},
    'geza': {'hebrew': 'גזע', 'meaning': 'stem/trunk'},
    'anaf': {'hebrew': 'ענף', 'meaning': 'branch'},
    'tzamach': {'hebrew': 'צמח', 'meaning': 'plant'},
    'esev': {'hebrew': 'עשב', 'meaning': 'herb/grass'},
    'etz': {'hebrew': 'עץ', 'meaning': 'tree'},
    'kela': {'hebrew': 'קליפה', 'meaning': 'bark/peel'},
    'nikba': {'hebrew': 'נקבה', 'meaning': 'female plant'},
    'zachar': {'hebrew': 'זכר', 'meaning': 'male plant'},
}

HEBREW_BODY_PARTS = {
    'rosh': {'hebrew': 'ראש', 'meaning': 'head'},
    'lev': {'hebrew': 'לב', 'meaning': 'heart'},
    'kaved': {'hebrew': 'כבד', 'meaning': 'liver'},
    'klaya': {'hebrew': 'כליה', 'meaning': 'kidney'},
    'mea': {'hebrew': 'מעי', 'meaning': 'intestine'},
    'dam': {'hebrew': 'דם', 'meaning': 'blood'},
    'etzem': {'hebrew': 'עצם', 'meaning': 'bone'},
    'basar': {'hebrew': 'בשר', 'meaning': 'flesh'},
    'or': {'hebrew': 'עור', 'meaning': 'skin'},
    'ayin': {'hebrew': 'עין', 'meaning': 'eye'},
    'ozen': {'hebrew': 'אוזן', 'meaning': 'ear'},
    'yad': {'hebrew': 'יד', 'meaning': 'hand'},
    'regel': {'hebrew': 'רגל', 'meaning': 'foot/leg'},
    'beten': {'hebrew': 'בטן', 'meaning': 'belly'},
    'rechem': {'hebrew': 'רחם', 'meaning': 'womb'},
    'gargeret': {'hebrew': 'גרגרת', 'meaning': 'windpipe'},
    'kaneh': {'hebrew': 'קנה', 'meaning': 'trachea'},
}

HEBREW_ASTROLOGICAL = {
    'dagim': {'hebrew': 'דגים', 'meaning': 'Pisces (fish)'},
    'taleh': {'hebrew': 'טלה', 'meaning': 'Aries (lamb)'},
    'shor': {'hebrew': 'שור', 'meaning': 'Taurus (bull)'},
    'teomim': {'hebrew': 'תאומים', 'meaning': 'Gemini (twins)'},
    'sartan': {'hebrew': 'סרטן', 'meaning': 'Cancer (crab)'},
    'aryeh': {'hebrew': 'אריה', 'meaning': 'Leo (lion)'},
    'betulah': {'hebrew': 'בתולה', 'meaning': 'Virgo (virgin)'},
    'moznayim': {'hebrew': 'מאזניים', 'meaning': 'Libra (scales)'},
    'akrav': {'hebrew': 'עקרב', 'meaning': 'Scorpio (scorpion)'},
    'keshet': {'hebrew': 'קשת', 'meaning': 'Sagittarius (bow)'},
    'gedi': {'hebrew': 'גדי', 'meaning': 'Capricorn (kid)'},
    'deli': {'hebrew': 'דלי', 'meaning': 'Aquarius (bucket)'},
    'mazal': {'hebrew': 'מזל', 'meaning': 'constellation/fortune'},
    'kochav': {'hebrew': 'כוכב', 'meaning': 'star'},
    'shemesh': {'hebrew': 'שמש', 'meaning': 'sun'},
    'yareakh': {'hebrew': 'ירח', 'meaning': 'moon'},
}

HEBREW_MEDICAL = {
    'refuah': {'hebrew': 'רפואה', 'meaning': 'medicine/healing'},
    'choli': {'hebrew': 'חולי', 'meaning': 'illness'},
    'samim': {'hebrew': 'סמים', 'meaning': 'drugs/potions'},
    'marpeh': {'hebrew': 'מרפא', 'meaning': 'cure'},
    'terufah': {'hebrew': 'תרופה', 'meaning': 'remedy'},
    'segulah': {'hebrew': 'סגולה', 'meaning': 'special remedy'},
    'mishchah': {'hebrew': 'משחה', 'meaning': 'ointment'},
    'retiyah': {'hebrew': 'רטיה', 'meaning': 'poultice/plaster'},
}

GEMATRIA = {
    'a': 1, 'b': 2, 'g': 3, 'd': 4, 'h': 5, 'v': 6, 'z': 7,
    'ch': 8, 't': 9, 'y': 10, 'k': 20, 'l': 30, 'm': 40,
    'n': 50, 's': 60, 'o': 70, 'p': 80, 'tz': 90, 'q': 100,
    'r': 200, 'sh': 300, 'th': 400
}

EVA_TO_HEBREW_MAP = {
    'o': 'a', 'a': 'e', 'e': 'i', 'i': 'y', 'y': 'y',
    'd': 'd', 's': 'sh', 'r': 'r', 'l': 'l', 'n': 'n', 'm': 'm',
    'k': 'k', 't': 't', 'p': 'p', 'f': 'f', 'q': 'q', 'g': 'g',
    'ch': 'ch', 'sh': 'sh', 'x': 'tz'
}


def eva_to_hebrew_phonetic(word):
    result = []
    i = 0
    while i < len(word):
        if i + 1 < len(word) and word[i:i+2] in EVA_TO_HEBREW_MAP:
            result.append(EVA_TO_HEBREW_MAP[word[i:i+2]])
            i += 2
        elif word[i] in EVA_TO_HEBREW_MAP:
            result.append(EVA_TO_HEBREW_MAP[word[i]])
            i += 1
        else:
            result.append(word[i])
            i += 1
    return ''.join(result)


def consonant_skeleton(s):
    vowels = 'aeiouáéíóúàèìòù'
    return ''.join(c for c in s.lower() if c.isalpha() and c not in vowels)


def similarity(a, b):
    a_clean = ''.join(c for c in a.lower() if c.isalpha())
    b_clean = ''.join(c for c in b.lower() if c.isalpha())
    if not a_clean or not b_clean:
        return 0.0
    return SequenceMatcher(None, a_clean, b_clean).ratio()


def skeleton_match(decoded, target):
    sk1 = consonant_skeleton(decoded)
    sk2 = consonant_skeleton(target)
    if not sk1 or not sk2:
        return 0.0
    return SequenceMatcher(None, sk1, sk2).ratio()


def calc_gematria(word):
    total = 0
    decoded = eva_to_hebrew_phonetic(word)
    i = 0
    while i < len(decoded):
        if i + 1 < len(decoded) and decoded[i:i+2] in GEMATRIA:
            total += GEMATRIA[decoded[i:i+2]]
            i += 2
        elif decoded[i] in GEMATRIA:
            total += GEMATRIA[decoded[i]]
            i += 1
        else:
            i += 1
    return total


def build_reference_corpus():
    corpus = {
        'month_names': [],
        'plant_terms': [],
        'body_parts': [],
        'astrological': [],
        'medical': [],
    }
    
    for name, info in HEBREW_MONTHS.items():
        corpus['month_names'].append({
            'term': name,
            'romanized': info['romanized'],
            'hebrew': info['hebrew'],
            'period': info['gregorian'],
            'old_name': info.get('old', None)
        })
    
    for term, info in HEBREW_PLANT_TERMS.items():
        corpus['plant_terms'].append({
            'term': term,
            'hebrew': info['hebrew'],
            'meaning': info['meaning']
        })
    
    for term, info in HEBREW_BODY_PARTS.items():
        corpus['body_parts'].append({
            'term': term,
            'hebrew': info['hebrew'],
            'meaning': info['meaning']
        })
    
    for term, info in HEBREW_ASTROLOGICAL.items():
        corpus['astrological'].append({
            'term': term,
            'hebrew': info['hebrew'],
            'meaning': info['meaning']
        })
    
    for term, info in HEBREW_MEDICAL.items():
        corpus['medical'].append({
            'term': term,
            'hebrew': info['hebrew'],
            'meaning': info['meaning']
        })
    
    return corpus


def load_zodiac_data():
    path = Path('results/zodiac_analysis.json')
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def load_glyph_data():
    path = Path('results/glyph_analysis.json')
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def test_zodiac_hebrew_months():
    zodiac_data = load_zodiac_data()
    if not zodiac_data:
        return {'error': 'No zodiac data found'}
    
    zodiac_to_hebrew = {
        'Pisces': ['adar', 'nisan'],
        'Aries': ['nisan', 'iyar'],
        'Taurus': ['iyar', 'sivan'],
        'Gemini': ['sivan', 'tammuz'],
        'Cancer': ['tammuz', 'av'],
        'Leo': ['av', 'elul'],
        'Virgo': ['elul', 'tishrei'],
        'Libra': ['tishrei', 'cheshvan'],
        'Scorpio': ['cheshvan', 'kislev'],
        'Sagittarius': ['kislev', 'tevet'],
        'Capricorn': ['tevet', 'shevat'],
        'Aquarius': ['shevat', 'adar'],
    }
    
    zodiac_hebrew_names = {
        'Pisces': 'dagim',
        'Aries': 'taleh',
        'Taurus': 'shor',
        'Gemini': 'teomim',
        'Cancer': 'sartan',
        'Leo': 'aryeh',
        'Virgo': 'betulah',
        'Libra': 'moznayim',
        'Scorpio': 'akrav',
        'Sagittarius': 'keshet',
        'Capricorn': 'gedi',
        'Aquarius': 'deli',
    }
    
    results = []
    
    for section in zodiac_data.get('zodiac_sections', []):
        sign = section['sign']
        labels = section.get('labels', [])
        expected_months = zodiac_to_hebrew.get(sign, [])
        expected_zodiac = zodiac_hebrew_names.get(sign, '')
        
        month_matches = []
        zodiac_matches = []
        
        for label in labels:
            if len(label) < 2:
                continue
            decoded = eva_to_hebrew_phonetic(label)
            
            for month in expected_months:
                sim = similarity(decoded, month)
                skel = skeleton_match(decoded, month)
                score = sim * 0.6 + skel * 0.4
                if score > 0.25:
                    month_matches.append({
                        'voynich': label,
                        'decoded': decoded,
                        'hebrew_month': month,
                        'score': round(score, 3)
                    })
            
            sim = similarity(decoded, expected_zodiac)
            skel = skeleton_match(decoded, expected_zodiac)
            score = sim * 0.6 + skel * 0.4
            if score > 0.25:
                zodiac_matches.append({
                    'voynich': label,
                    'decoded': decoded,
                    'hebrew_sign': expected_zodiac,
                    'score': round(score, 3)
                })
        
        month_matches.sort(key=lambda x: x['score'], reverse=True)
        zodiac_matches.sort(key=lambda x: x['score'], reverse=True)
        
        results.append({
            'sign': sign,
            'folio': section.get('folio', ''),
            'expected_hebrew_months': expected_months,
            'expected_hebrew_zodiac': expected_zodiac,
            'month_matches': month_matches[:3],
            'zodiac_matches': zodiac_matches[:3],
            'best_month_score': month_matches[0]['score'] if month_matches else 0,
            'best_zodiac_score': zodiac_matches[0]['score'] if zodiac_matches else 0,
        })
    
    return results


def test_plant_hebrew_terms():
    pages = vd.get_eva_pages()
    
    herbal_folios = ['f' + str(i) + 'r' for i in range(1, 57)] + \
                    ['f' + str(i) + 'v' for i in range(1, 57)]
    
    words = []
    for folio in herbal_folios:
        if folio in pages:
            for text in pages[folio].values():
                text_clean = re.sub(r'[!?<>@$\[\]\d]', '', text)
                for w in re.split(r'[.\-=,\s]', text_clean):
                    if w and len(w) >= 2:
                        words.append(w)
    
    word_freq = Counter(words)
    
    target_terms = list(HEBREW_PLANT_TERMS.keys())
    
    matches = []
    for word, count in word_freq.most_common(500):
        decoded = eva_to_hebrew_phonetic(word)
        
        for term in target_terms:
            sim = similarity(decoded, term)
            skel = skeleton_match(decoded, term)
            score = sim * 0.6 + skel * 0.4
            
            if score > 0.3:
                matches.append({
                    'voynich': word,
                    'decoded': decoded,
                    'hebrew_term': term,
                    'meaning': HEBREW_PLANT_TERMS[term]['meaning'],
                    'score': round(score, 3),
                    'frequency': count
                })
    
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:30]


def gematria_analysis():
    words = vd.get_all_words()
    
    gematria_values = Counter()
    word_gematria = []
    
    for word in words[:1000]:
        val = calc_gematria(word)
        gematria_values[val] += 1
        word_gematria.append({
            'word': word,
            'decoded': eva_to_hebrew_phonetic(word),
            'gematria': val
        })
    
    significant_numbers = {
        18: 'chai (life)',
        26: 'YHVH (God name)',
        36: '2x chai',
        72: 'shem ha-meforash',
        137: 'kabbalah',
        248: 'positive commandments',
        365: 'negative commandments / days in year',
        613: 'total commandments',
    }
    
    significant_matches = []
    for num, meaning in significant_numbers.items():
        count = gematria_values.get(num, 0)
        if count > 0:
            words_with_val = [w for w in word_gematria if w['gematria'] == num][:5]
            significant_matches.append({
                'value': num,
                'meaning': meaning,
                'count': count,
                'examples': words_with_val
            })
    
    return {
        'value_distribution': dict(gematria_values.most_common(20)),
        'significant_numbers': significant_matches,
        'sample_words': word_gematria[:50]
    }


def kabbalistic_pattern_search():
    words = vd.get_all_words()
    word_freq = Counter(words)
    
    patterns = {
        'notarikon': [],
        'temurah': [],
        'repetition': [],
    }
    
    three_letter = [w for w in word_freq if len(w) == 3]
    if three_letter:
        patterns['notarikon'] = {
            'description': 'Three-letter words (potential acronyms)',
            'count': len(three_letter),
            'examples': three_letter[:20]
        }
    
    repeated_patterns = []
    for word in list(word_freq.keys())[:500]:
        if len(word) >= 4:
            for i in range(len(word) - 1):
                if word[i] == word[i+1]:
                    repeated_patterns.append(word)
                    break
    patterns['repetition'] = {
        'description': 'Words with repeated characters',
        'count': len(repeated_patterns),
        'examples': repeated_patterns[:20]
    }
    
    substitution_pairs = []
    common_words = list(word_freq.keys())[:200]
    for i, w1 in enumerate(common_words[:50]):
        for w2 in common_words[i+1:100]:
            if len(w1) == len(w2) and w1 != w2:
                diffs = sum(1 for a, b in zip(w1, w2) if a != b)
                if diffs == 1:
                    substitution_pairs.append((w1, w2))
    patterns['temurah'] = {
        'description': 'Word pairs differing by one character',
        'count': len(substitution_pairs),
        'examples': substitution_pairs[:20]
    }
    
    return patterns


def analyze_structural_features():
    glyph_data = load_glyph_data()
    if not glyph_data:
        return {'error': 'No glyph data found'}
    
    features = {
        'text_direction': 'left-to-right (assumed from manuscript)',
        'final_letter_forms': [],
        'positional_patterns': {},
    }
    
    positions = glyph_data.get('positions', {})
    
    final_bias_glyphs = []
    for gid, pos in positions.items():
        if pos.get('total_occurrences', 0) > 100:
            if pos.get('final', 0) > 0.5:
                final_bias_glyphs.append({
                    'glyph': gid,
                    'final_ratio': round(pos['final'], 3),
                    'total': pos['total_occurrences']
                })
    
    features['final_letter_forms'] = final_bias_glyphs
    features['final_forms_count'] = len(final_bias_glyphs)
    features['hebrew_final_forms_count'] = 5
    
    features['positional_patterns'] = {
        'strong_initial': sum(1 for g, p in positions.items() 
                             if p.get('initial', 0) > 0.5 and p.get('total_occurrences', 0) > 100),
        'strong_final': sum(1 for g, p in positions.items() 
                           if p.get('final', 0) > 0.5 and p.get('total_occurrences', 0) > 100),
        'strong_medial': sum(1 for g, p in positions.items() 
                            if p.get('medial', 0) > 0.5 and p.get('total_occurrences', 0) > 100),
    }
    
    return features


def test_judeo_italian():
    words = vd.get_all_words()
    word_freq = Counter(words)
    
    italian_endings = ['are', 'ere', 'ire', 'ato', 'ito', 'uto', 'zione', 'mente']
    hebrew_stems = ['ach', 'lech', 'shm', 'dab', 'chaz', 'seg']
    
    matches = []
    for word in list(word_freq.keys())[:500]:
        decoded = eva_to_hebrew_phonetic(word)
        
        has_italian_end = any(decoded.endswith(e) for e in italian_endings)
        has_hebrew_stem = any(s in decoded[:3] for s in hebrew_stems)
        
        if has_italian_end or has_hebrew_stem:
            matches.append({
                'voynich': word,
                'decoded': decoded,
                'italian_ending': has_italian_end,
                'hebrew_stem': has_hebrew_stem,
                'frequency': word_freq[word]
            })
    
    return {
        'hypothesis': 'Judeo-Italian (Hebrew stems + Italian morphology)',
        'matches': matches[:30],
        'match_count': len(matches)
    }


def calculate_overall_score(results):
    scores = []
    
    zodiac = results.get('zodiac_hebrew_matches', [])
    if zodiac:
        avg_month = sum(z['best_month_score'] for z in zodiac) / len(zodiac)
        avg_zodiac = sum(z['best_zodiac_score'] for z in zodiac) / len(zodiac)
        scores.append(('zodiac_month_match', avg_month))
        scores.append(('zodiac_sign_match', avg_zodiac))
    
    plant_matches = results.get('plant_hebrew_matches', [])
    if plant_matches:
        avg_plant = sum(p['score'] for p in plant_matches[:10]) / min(10, len(plant_matches))
        scores.append(('plant_term_match', avg_plant))
    
    structure = results.get('structural_comparison', {})
    final_forms = structure.get('final_forms_count', 0)
    hebrew_finals = structure.get('hebrew_final_forms_count', 5)
    if final_forms > 0:
        final_similarity = min(final_forms / hebrew_finals, 1.0)
        scores.append(('final_form_similarity', final_similarity))
    
    if not scores:
        return 0.0
    
    return round(sum(s[1] for s in scores) / len(scores), 3)


def main():
    print("=" * 70)
    print("🕎 TRACK 40: MEDIEVAL HEBREW TEXT COMPARISON")
    print("=" * 70)
    
    results = {}
    
    print("\n📚 Building reference corpus...")
    corpus = build_reference_corpus()
    results['reference_corpus'] = {
        'month_names': len(corpus['month_names']),
        'plant_terms': len(corpus['plant_terms']),
        'body_parts': len(corpus['body_parts']),
        'astrological': len(corpus['astrological']),
        'medical': len(corpus['medical']),
        'total_terms': sum(len(v) for v in corpus.values())
    }
    print(f"  Total terms: {results['reference_corpus']['total_terms']}")
    
    print("\n🔭 Testing zodiac sections with Hebrew months...")
    zodiac_results = test_zodiac_hebrew_months()
    if isinstance(zodiac_results, dict) and 'error' in zodiac_results:
        print(f"  ⚠️ {zodiac_results['error']}")
        results['zodiac_hebrew_matches'] = []
    else:
        results['zodiac_hebrew_matches'] = zodiac_results
        good_matches = sum(1 for z in zodiac_results if z['best_month_score'] >= 0.4)
        print(f"  Sections with good month matches (≥0.4): {good_matches}/{len(zodiac_results)}")
        
        for z in zodiac_results[:4]:
            print(f"\n  {z['sign']} ({z['folio']}):")
            print(f"    Expected: {z['expected_hebrew_months']}")
            if z['month_matches']:
                best = z['month_matches'][0]
                print(f"    Best match: {best['voynich']} → {best['decoded']} ≈ {best['hebrew_month']} ({best['score']:.2f})")
    
    print("\n🌿 Testing plant section with Hebrew botanical terms...")
    plant_matches = test_plant_hebrew_terms()
    results['plant_hebrew_matches'] = plant_matches
    high_conf = sum(1 for p in plant_matches if p['score'] >= 0.5)
    print(f"  High-confidence matches (≥0.5): {high_conf}")
    
    for p in plant_matches[:5]:
        print(f"    {p['voynich']} → {p['decoded']} ≈ {p['hebrew_term']} ({p['meaning']}) [{p['score']:.2f}]")
    
    print("\n🔢 Performing gematria analysis...")
    gematria = gematria_analysis()
    results['gematria_analysis'] = gematria
    print(f"  Most common values: {list(gematria['value_distribution'].keys())[:10]}")
    
    if gematria['significant_numbers']:
        print("  Significant number matches:")
        for sig in gematria['significant_numbers'][:3]:
            print(f"    {sig['value']} ({sig['meaning']}): {sig['count']} words")
    
    print("\n✡️ Searching for Kabbalistic patterns...")
    kabbalistic = kabbalistic_pattern_search()
    results['kabbalistic_patterns'] = kabbalistic
    print(f"  Three-letter words (potential notarikon): {kabbalistic['notarikon'].get('count', 0)}")
    print(f"  Substitution pairs (temurah-like): {kabbalistic['temurah'].get('count', 0)}")
    
    print("\n📐 Analyzing structural features...")
    structure = analyze_structural_features()
    results['structural_comparison'] = structure
    if 'error' not in structure:
        print(f"  Glyphs with strong final position: {structure['final_forms_count']}")
        print(f"  Hebrew has 5 final-form letters")
        print(f"  Positional patterns: {structure['positional_patterns']}")
    
    print("\n🇮🇹 Testing Judeo-Italian hypothesis...")
    judeo = test_judeo_italian()
    results['judeo_italian_test'] = judeo
    print(f"  Potential matches: {judeo['match_count']}")
    
    overall = calculate_overall_score(results)
    results['overall_hebrew_match'] = overall
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    print(f"\n  Overall Hebrew match score: {overall:.3f}")
    
    if overall >= 0.5:
        verdict = "STRONG Hebrew connection likely"
    elif overall >= 0.35:
        verdict = "MODERATE Hebrew features present"
    elif overall >= 0.2:
        verdict = "WEAK Hebrew connection"
    else:
        verdict = "NO significant Hebrew connection found"
    
    print(f"  Verdict: {verdict}")
    results['verdict'] = verdict
    
    out_json = Path('results/medieval_hebrew_comparison.json')
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Results saved to {out_json}")
    
    generate_report(results, corpus)
    
    print("\n" + "=" * 70)
    print("💡 KEY FINDINGS")
    print("=" * 70)
    
    if results['zodiac_hebrew_matches']:
        best_zodiac = max(results['zodiac_hebrew_matches'], key=lambda x: x['best_month_score'])
        print(f"\n  Best zodiac match: {best_zodiac['sign']}")
        if best_zodiac['month_matches']:
            m = best_zodiac['month_matches'][0]
            print(f"    {m['voynich']} → {m['hebrew_month']} (score: {m['score']:.2f})")
    
    if plant_matches:
        print(f"\n  Best plant term match:")
        p = plant_matches[0]
        print(f"    {p['voynich']} → {p['hebrew_term']} ({p['meaning']}) [score: {p['score']:.2f}]")
    
    print("\n  Structural comparison:")
    if 'error' not in structure:
        print(f"    Voynich final-form glyphs: {structure['final_forms_count']}")
        print(f"    Hebrew final-form letters: 5 (כמנפצ)")
        if structure['final_forms_count'] >= 3:
            print("    ✓ Similar final-form behavior suggests possible connection")


def generate_report(results, corpus):
    lines = [
        "# Track 40: Medieval Hebrew Comparison Report",
        "",
        "## Executive Summary",
        "",
        f"**Overall Hebrew Match Score:** {results['overall_hebrew_match']:.3f}",
        f"**Verdict:** {results['verdict']}",
        "",
        "## Reference Corpus",
        "",
        f"Total terms compiled: {results['reference_corpus']['total_terms']}",
        "",
        "| Category | Terms |",
        "|----------|-------|",
    ]
    
    for cat, count in results['reference_corpus'].items():
        if cat != 'total_terms':
            lines.append(f"| {cat.replace('_', ' ').title()} | {count} |")
    
    lines.extend([
        "",
        "## Zodiac Section Analysis",
        "",
        "Testing zodiac labels against Hebrew month names:",
        "",
        "| Sign | Hebrew Month | Best Match | Score |",
        "|------|--------------|------------|-------|",
    ])
    
    for z in results.get('zodiac_hebrew_matches', [])[:12]:
        months = ', '.join(z['expected_hebrew_months'])
        if z['month_matches']:
            best = z['month_matches'][0]
            lines.append(f"| {z['sign']} | {months} | {best['voynich']}→{best['decoded']} | {best['score']:.2f} |")
        else:
            lines.append(f"| {z['sign']} | {months} | - | 0.00 |")
    
    lines.extend([
        "",
        "## Plant Section Analysis",
        "",
        "Testing herbal labels against Hebrew botanical terms:",
        "",
        "| Voynich | Decoded | Hebrew Term | Meaning | Score |",
        "|---------|---------|-------------|---------|-------|",
    ])
    
    for p in results.get('plant_hebrew_matches', [])[:15]:
        lines.append(f"| {p['voynich']} | {p['decoded']} | {p['hebrew_term']} | {p['meaning']} | {p['score']:.2f} |")
    
    lines.extend([
        "",
        "## Gematria Analysis",
        "",
        "### Most Common Word Values",
        "",
    ])
    
    gematria = results.get('gematria_analysis', {})
    for val, count in list(gematria.get('value_distribution', {}).items())[:10]:
        lines.append(f"- Value {val}: {count} words")
    
    lines.extend([
        "",
        "### Significant Numbers Found",
        "",
    ])
    
    for sig in gematria.get('significant_numbers', []):
        lines.append(f"- **{sig['value']}** ({sig['meaning']}): {sig['count']} words")
    
    lines.extend([
        "",
        "## Kabbalistic Patterns",
        "",
    ])
    
    kab = results.get('kabbalistic_patterns', {})
    if kab.get('notarikon'):
        lines.append(f"**Three-letter words (Notarikon candidates):** {kab['notarikon'].get('count', 0)}")
    if kab.get('temurah'):
        lines.append(f"**Substitution pairs (Temurah-like):** {kab['temurah'].get('count', 0)}")
    
    lines.extend([
        "",
        "## Structural Comparison",
        "",
    ])
    
    struct = results.get('structural_comparison', {})
    if 'error' not in struct:
        lines.extend([
            f"**Glyphs with strong final position:** {struct.get('final_forms_count', 0)}",
            f"**Hebrew final-form letters:** 5 (ך ם ן ף ץ)",
            "",
            "Hebrew has 5 letters with special final forms. Voynich shows similar",
            "positional behavior with certain glyphs appearing predominantly at word ends.",
        ])
    
    lines.extend([
        "",
        "## Judeo-Italian Hypothesis",
        "",
    ])
    
    judeo = results.get('judeo_italian_test', {})
    lines.append(f"**Potential matches found:** {judeo.get('match_count', 0)}")
    
    lines.extend([
        "",
        "## Conclusions",
        "",
        f"### Overall Assessment: {results['verdict']}",
        "",
    ])
    
    if results['overall_hebrew_match'] >= 0.35:
        lines.extend([
            "The analysis shows notable similarities between Voynich text and Hebrew patterns:",
            "",
            "1. **Positional letter behavior** matches Hebrew's final-form system",
            "2. **Some zodiac labels** show phonetic similarity to Hebrew month names",
            "3. **Botanical section** contains words similar to Hebrew plant terminology",
            "",
            "This supports further investigation of the Hebrew hypothesis.",
        ])
    else:
        lines.extend([
            "The analysis shows limited correlation with Hebrew patterns:",
            "",
            "1. Zodiac labels do not strongly match Hebrew month names",
            "2. Plant terminology matches are weak",
            "3. While structural features show some similarity, they're not conclusive",
            "",
            "The Hebrew hypothesis requires stronger evidence.",
        ])
    
    lines.extend([
        "",
        "## Recommendations",
        "",
        "1. Compare with actual medieval Hebrew medical manuscripts",
        "2. Investigate Judeo-Italian texts from Northern Italy",
        "3. Analyze gematria patterns more deeply",
        "4. Compare with known Kabbalistic cipher systems",
    ])
    
    out_md = Path('results/medieval_hebrew_report.md')
    with open(out_md, 'w') as f:
        f.write('\n'.join(lines))
    print(f"✅ Report saved to {out_md}")


if __name__ == '__main__':
    main()
