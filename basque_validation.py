#!/usr/bin/env python3
"""
Track 7: Basque Hypothesis Validation
Rigorous testing of whether Voynich could be Basque (Euskara)
"""

import re
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BASQUE_PLANT_NAMES = {
    'Cornflower': {
        'basque': 'anabasa',
        'alt': ['ehunbelarra', 'zentaurea'],
        'latin': 'Centaurea cyanus'
    },
    'Hellebore': {
        'basque': 'neguko arrosa',
        'alt': ['negulorea', 'negubelia'],
        'latin': 'Helleborus sp.'
    },
    'Poppy': {
        'basque': 'mitxoleta',
        'alt': ['lobelarra', 'olobelarra'],
        'latin': 'Papaver sp.'
    },
    'Cyclamen': {
        'basque': 'basoko ziklamena',
        'alt': ['txerribelarr', 'ziklameno'],
        'latin': 'Cyclamen sp.'
    },
    'Castor Bean': {
        'basque': 'errizinoa',
        'alt': ['rizinoa'],
        'latin': 'Ricinus communis'
    },
    'Oak': {
        'basque': 'haritza',
        'alt': ['arte', 'artea'],
        'latin': 'Quercus sp.'
    }
}

BASQUE_CASE_ENDINGS = {
    'absolutive_sg': '-a',
    'absolutive_pl': '-ak',
    'ergative_sg': '-ak',
    'ergative_pl': '-ek',
    'dative_sg': '-ari',
    'dative_pl': '-ei',
    'genitive_sg': '-aren',
    'genitive_pl': '-en',
    'comitative_sg': '-arekin',
    'comitative_pl': '-ekin',
    'benefactive_sg': '-arentzat',
    'benefactive_pl': '-entzat',
    'instrumental_sg': '-az',
    'instrumental_pl': '-ez',
    'inessive_sg': '-an',
    'inessive_pl': '-etan',
    'allative_sg': '-ra',
    'allative_pl': '-etara',
    'ablative_sg': '-tik',
    'ablative_pl': '-etatik',
    'local_gen_sg': '-ko',
    'local_gen_pl': '-etako',
    'partitive': '-rik',
}

BASQUE_FUNCTION_WORDS = {
    'eta': 'and',
    'edo': 'or',
    'baina': 'but',
    'da': 'is (3sg intrans)',
    'du': 'has (3sg trans)',
    'dira': 'are (3pl intrans)',
    'dute': 'have (3pl trans)',
    'bat': 'one/a',
    'bi': 'two',
    'hiru': 'three',
    'lau': 'four',
    'bost': 'five',
    'sei': 'six',
    'zazpi': 'seven',
    'zortzi': 'eight',
    'bederatzi': 'nine',
    'hamar': 'ten',
    'ez': 'not',
    'bai': 'yes',
    'hau': 'this',
    'hori': 'that',
    'zer': 'what',
    'nor': 'who',
    'non': 'where',
}

VOYNICH_SUFFIXES = {
    '9': {'freq': 0.37, 'function': 'nominative/unmarked'},
    '89': {'freq': 0.118, 'function': 'genitive_plural'},
    'am': {'freq': 0.094, 'function': 'accusative'},
    'oe': {'freq': 0.089, 'function': 'locative'},
    'ay': {'freq': 0.069, 'function': 'genitive'},
    'ae': {'freq': 0.054, 'function': 'instrumental'},
    'an': {'freq': 0.042, 'function': 'ablative'},
    'c9': {'freq': 0.063, 'function': 'genitive'},
}

def load_voynich_words():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    words = []
    for line in text.split('\n'):
        clean = re.sub(r'<[^>]+>', '', line)
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            ws = re.split(r'[.,\s]+', clean)
            words.extend([w for w in ws if w and len(w) > 0])
    return words

def load_plant_mappings():
    try:
        data = json.loads(Path('results/plant_identifications.json').read_text())
        return data.get('name_mappings', [])
    except:
        return []

def create_phonetic_mapping(words):
    """Create frequency-based mapping Voynich → Basque phonemes"""
    all_chars = ''.join(words)
    char_freq = Counter(all_chars)
    sorted_chars = [c for c, _ in sorted(char_freq.items(), key=lambda x: -x[1]) if c.isalnum()]
    
    basque_letters = 'aeikonrtuzsbdglmphj'
    
    mapping = {}
    for i, vchar in enumerate(sorted_chars):
        if i < len(basque_letters):
            mapping[vchar] = basque_letters[i]
        else:
            mapping[vchar] = '?'
    
    return mapping

def apply_mapping(word, mapping):
    return ''.join(mapping.get(c, c) for c in word)

def phonetic_similarity(s1, s2):
    """Calculate phonetic similarity between two strings"""
    if not s1 or not s2:
        return 0.0
    
    s1, s2 = s1.lower(), s2.lower()
    
    matches = sum(1 for c in s1 if c in s2)
    max_len = max(len(s1), len(s2))
    overlap = matches / max_len if max_len > 0 else 0
    
    len_sim = 1.0 - abs(len(s1) - len(s2)) / max(len(s1), len(s2))
    
    first_match = 1.0 if s1[0] == s2[0] else 0.0
    last_match = 1.0 if s1[-1] == s2[-1] else 0.0
    
    return (overlap * 0.4 + len_sim * 0.3 + first_match * 0.15 + last_match * 0.15)

def test_plant_names(words, mapping, plant_mappings):
    """Test if Voynich plant labels could be Basque plant names"""
    results = []
    
    voynich_plants = {
        'f2o89': 'Cornflower',
        'h2o89': 'Hellebore',
        'foay': 'Poppy',
        'hoom': 'Cyclamen',
        'goCam': 'Castor Bean',
        'k98eo': 'Oak'
    }
    
    for mp in plant_mappings:
        v_name = mp.get('voynich', '')
        plant = mp.get('candidate', '')
        if v_name in voynich_plants:
            voynich_plants[v_name] = plant
    
    for voynich_name, plant in voynich_plants.items():
        if plant not in BASQUE_PLANT_NAMES:
            continue
            
        basque_info = BASQUE_PLANT_NAMES[plant]
        decoded = apply_mapping(voynich_name, mapping)
        
        all_basque_names = [basque_info['basque']] + basque_info.get('alt', [])
        all_basque_names = [n.replace(' ', '') for n in all_basque_names]
        
        best_match = ''
        best_score = 0.0
        for bname in all_basque_names:
            score = phonetic_similarity(decoded, bname)
            if score > best_score:
                best_score = score
                best_match = bname
        
        results.append({
            'plant': plant,
            'basque_name': basque_info['basque'],
            'voynich_name': voynich_name,
            'decoded_as': decoded,
            'best_basque_match': best_match,
            'match_score': round(best_score, 3),
            'notes': f"Latin: {basque_info['latin']}"
        })
    
    return results

def test_ergative_absolutive(words):
    """Test if Voynich shows ergative-absolutive patterns"""
    endings_count = defaultdict(Counter)
    
    for word in words:
        if len(word) < 2:
            continue
        
        root = word[:-1] if len(word) > 2 else word[:1]
        ending = word[-1] if len(word) > 1 else ''
        ending2 = word[-2:] if len(word) > 2 else word
        
        if root:
            endings_count[root][ending] += 1
            if len(word) > 2:
                endings_count[root][ending2] += 1
    
    paradigm_examples = []
    for root, endings in endings_count.items():
        if len(endings) >= 3:
            most_common = endings.most_common(5)
            total = sum(c for _, c in most_common)
            if total >= 10:
                paradigm_examples.append({
                    'root': root,
                    'endings': dict(most_common),
                    'total_occurrences': total
                })
    
    paradigm_examples.sort(key=lambda x: -x['total_occurrences'])
    
    absolutive_like = 0
    ergative_like = 0
    
    for word in words:
        if word.endswith('9'):
            absolutive_like += 1
        if word.endswith('89') or word.endswith('ae'):
            ergative_like += 1
    
    ratio = ergative_like / absolutive_like if absolutive_like > 0 else 0
    
    if ratio > 0.3 and ratio < 0.7:
        result = 'INCONCLUSIVE'
        explanation = f"Ergative/Absolutive ratio {ratio:.2f} is between expected ranges. Basque expects subject marking to differ based on transitivity."
    elif ratio < 0.3:
        result = 'RULES_OUT'
        explanation = f"Low ergative/absolutive ratio ({ratio:.2f}) suggests nominative-accusative system, not ergative like Basque."
    else:
        result = 'POSSIBLE'
        explanation = f"Ergative/absolutive ratio ({ratio:.2f}) could be consistent with ergative marking."
    
    dominant_ending = '9' if absolutive_like > ergative_like else '89'
    
    return {
        'result': result,
        'absolutive_count': absolutive_like,
        'ergative_count': ergative_like,
        'ratio': round(ratio, 3),
        'evidence': [
            f"Words ending in '9' (absolutive-like): {absolutive_like}",
            f"Words ending in '89' or 'ae' (ergative-like): {ergative_like}",
            f"Dominant ending: {dominant_ending} ({(absolutive_like/(absolutive_like+ergative_like))*100:.1f}%)" if absolutive_like + ergative_like > 0 else "No data"
        ],
        'paradigm_examples': paradigm_examples[:5],
        'explanation': explanation,
        'critical_note': "Basque ergative-absolutive: transitive subjects get different marking than intransitive subjects. Voynich '9' at 37% suggests a dominant unmarked case like absolutive."
    }

def test_suffix_mapping():
    """Map Voynich suffixes to potential Basque equivalents"""
    mappings = {}
    
    voynich_to_basque = {
        '9': {
            'basque_candidates': ['-a (absolutive sg)', '-ak (absolutive pl)'],
            'confidence': 0.6,
            'notes': "37% frequency matches absolutive being the most common case"
        },
        '89': {
            'basque_candidates': ['-ek (ergative pl)', '-en (genitive pl)'],
            'confidence': 0.5,
            'notes': "Could be ergative plural or genitive plural"
        },
        'am': {
            'basque_candidates': [],
            'confidence': 0.2,
            'notes': "No clear Basque equivalent - Basque doesn't have -am ending"
        },
        'oe': {
            'basque_candidates': ['-ez (instrumental pl)?'],
            'confidence': 0.3,
            'notes': "Weak match - Basque uses -z not -oe for instrumental"
        },
        'ay': {
            'basque_candidates': ['-ai (rare)?'],
            'confidence': 0.2,
            'notes': "Not a typical Basque ending"
        },
        'ae': {
            'basque_candidates': [],
            'confidence': 0.1,
            'notes': "No Basque equivalent"
        },
        'an': {
            'basque_candidates': ['-an (inessive sg)'],
            'confidence': 0.8,
            'notes': "GOOD MATCH! -an is Basque inessive/locative"
        },
        'c9': {
            'basque_candidates': [],
            'confidence': 0.1,
            'notes': "Not a Basque pattern"
        }
    }
    
    total_confidence = 0
    matched = 0
    
    for suffix, info in VOYNICH_SUFFIXES.items():
        mapping_info = voynich_to_basque.get(suffix, {'basque_candidates': [], 'confidence': 0, 'notes': 'Unknown'})
        
        mappings[suffix] = {
            'basque_equivalent': mapping_info['basque_candidates'][0] if mapping_info['basque_candidates'] else 'NO MATCH',
            'all_candidates': mapping_info['basque_candidates'],
            'confidence': mapping_info['confidence'],
            'voynich_freq': info['freq'],
            'notes': mapping_info['notes']
        }
        
        total_confidence += mapping_info['confidence']
        if mapping_info['confidence'] >= 0.5:
            matched += 1
    
    avg_confidence = total_confidence / len(VOYNICH_SUFFIXES)
    
    return {
        'mappings': mappings,
        'match_rate': matched / len(VOYNICH_SUFFIXES),
        'avg_confidence': round(avg_confidence, 3),
        'strong_matches': ['an → -an (inessive)'],
        'partial_matches': ['9 → -a (absolutive)', '89 → -en (genitive)'],
        'no_matches': ['am', 'ae', 'ay', 'c9']
    }

def search_function_words(words):
    """Search for Basque function words in Voynich text"""
    word_counts = Counter(words)
    
    short_words = {w: c for w, c in word_counts.items() if 1 <= len(w) <= 4}
    short_words_sorted = sorted(short_words.items(), key=lambda x: -x[1])[:50]
    
    potential_matches = []
    
    basque_short = {k: v for k, v in BASQUE_FUNCTION_WORDS.items() if len(k) <= 4}
    
    for vword, count in short_words_sorted:
        for bword, meaning in basque_short.items():
            sim = phonetic_similarity(vword.lower(), bword.lower())
            if sim > 0.5:
                potential_matches.append({
                    'voynich': vword,
                    'basque': bword,
                    'meaning': meaning,
                    'similarity': round(sim, 2),
                    'occurrences': count
                })
    
    potential_matches.sort(key=lambda x: (-x['similarity'], -x['occurrences']))
    
    direct_matches = []
    for bword, meaning in basque_short.items():
        for vword, count in short_words_sorted:
            if vword.lower() == bword.lower():
                direct_matches.append({
                    'voynich': vword,
                    'basque': bword,
                    'meaning': meaning,
                    'occurrences': count
                })
    
    return {
        'direct_matches': direct_matches,
        'potential_matches': potential_matches[:10],
        'most_common_short_words': [{'word': w, 'count': c} for w, c in short_words_sorted[:15]],
        'notes': "No direct matches found" if not direct_matches else f"Found {len(direct_matches)} direct matches"
    }

def calculate_verdict(plant_results, ergative_result, suffix_mapping, function_words):
    """Calculate overall verdict"""
    scores = []
    evidence = []
    
    plant_avg = sum(p['match_score'] for p in plant_results) / len(plant_results) if plant_results else 0
    scores.append(plant_avg)
    evidence.append(f"Plant name match: {plant_avg:.1%}")
    
    if ergative_result['result'] == 'RULES_OUT':
        scores.append(0.2)
        evidence.append("Ergative test: FAILS (nominative-accusative pattern)")
    elif ergative_result['result'] == 'POSSIBLE':
        scores.append(0.7)
        evidence.append("Ergative test: POSSIBLE")
    else:
        scores.append(0.4)
        evidence.append("Ergative test: INCONCLUSIVE")
    
    scores.append(suffix_mapping['avg_confidence'])
    evidence.append(f"Suffix mapping confidence: {suffix_mapping['avg_confidence']:.1%}")
    
    func_score = 0.5 if function_words['potential_matches'] else 0.3
    if function_words['direct_matches']:
        func_score = 0.8
    scores.append(func_score)
    evidence.append(f"Function words: {'direct matches!' if function_words['direct_matches'] else 'weak matches'}")
    
    overall = sum(scores) / len(scores)
    
    if overall >= 0.5 or ergative_result['result'] == 'POSSIBLE' or suffix_mapping['match_rate'] > 0.5:
        recommendation = 'PURSUE'
    elif overall >= 0.35 or plant_avg > 0.3:
        recommendation = 'DEPRIORITIZE'
    else:
        recommendation = 'RULE_OUT'
    
    critical_issue = None
    if ergative_result['result'] == 'RULES_OUT':
        critical_issue = "CRITICAL: Voynich appears to use nominative-accusative case system (37% unmarked '9' ending), not ergative-absolutive like Basque."
    if suffix_mapping['match_rate'] < 0.3:
        critical_issue = "CRITICAL: Most Voynich suffixes don't match Basque case endings."
    
    return {
        'basque_plausibility': round(overall, 3),
        'recommendation': recommendation,
        'key_evidence': evidence,
        'critical_issue': critical_issue,
        'component_scores': {
            'plant_names': round(plant_avg, 3),
            'ergative_test': round(scores[1], 3),
            'suffix_mapping': round(suffix_mapping['avg_confidence'], 3),
            'function_words': round(func_score, 3)
        }
    }

def main():
    print("=" * 70)
    print("TRACK 7: BASQUE HYPOTHESIS VALIDATION")
    print("=" * 70)
    
    words = load_voynich_words()
    print(f"\nLoaded {len(words)} Voynich words")
    
    plant_mappings = load_plant_mappings()
    print(f"Loaded {len(plant_mappings)} plant mappings")
    
    print("\n1. Creating phonetic mapping...")
    mapping = create_phonetic_mapping(words)
    print(f"   Mapped {len(mapping)} characters")
    print(f"   Sample: {dict(list(mapping.items())[:8])}")
    
    print("\n2. Testing plant names...")
    plant_results = test_plant_names(words, mapping, plant_mappings)
    for p in plant_results:
        print(f"   {p['plant']}: {p['voynich_name']} → {p['decoded_as']} vs {p['basque_name']} (score: {p['match_score']:.2f})")
    
    print("\n3. Testing ergative-absolutive pattern...")
    ergative_result = test_ergative_absolutive(words)
    print(f"   Result: {ergative_result['result']}")
    print(f"   Absolutive-like endings: {ergative_result['absolutive_count']}")
    print(f"   Ergative-like endings: {ergative_result['ergative_count']}")
    print(f"   Ratio: {ergative_result['ratio']:.3f}")
    
    print("\n4. Mapping Voynich suffixes to Basque cases...")
    suffix_mapping = test_suffix_mapping()
    print(f"   Match rate: {suffix_mapping['match_rate']:.1%}")
    print(f"   Strong matches: {suffix_mapping['strong_matches']}")
    print(f"   No matches: {suffix_mapping['no_matches']}")
    
    print("\n5. Searching for Basque function words...")
    function_words = search_function_words(words)
    print(f"   Direct matches: {len(function_words['direct_matches'])}")
    print(f"   Potential matches: {len(function_words['potential_matches'])}")
    if function_words['potential_matches']:
        for m in function_words['potential_matches'][:3]:
            print(f"      {m['voynich']} ≈ {m['basque']} ({m['meaning']}) - sim: {m['similarity']}")
    
    print("\n6. Calculating verdict...")
    verdict = calculate_verdict(plant_results, ergative_result, suffix_mapping, function_words)
    
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print(f"\n   Basque Plausibility: {verdict['basque_plausibility']:.1%}")
    print(f"   Recommendation: {verdict['recommendation']}")
    print(f"\n   Evidence:")
    for e in verdict['key_evidence']:
        print(f"      - {e}")
    if verdict['critical_issue']:
        print(f"\n   ⚠️  {verdict['critical_issue']}")
    
    results = {
        'plant_name_tests': plant_results,
        'ergative_test': ergative_result,
        'suffix_mapping': suffix_mapping,
        'function_word_matches': function_words,
        'overall_verdict': verdict,
        'phonetic_mapping_sample': dict(list(mapping.items())[:15])
    }
    
    Path('results').mkdir(exist_ok=True)
    
    with open('results/basque_validation.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("Results saved to results/basque_validation.json")

if __name__ == '__main__':
    main()



