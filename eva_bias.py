"""
EVA Transliteration Bias Test - Track 37
Tests if "Latin-like" findings are artifacts of EVA design
"""

import json
import random
from pathlib import Path
from collections import Counter
import re

from voynich_data import get_eva_pages

RESULTS_DIR = Path("results")

EVA_GLYPHS = ['a', 'o', 'i', 'e', 'y', 'd', 'l', 'r', 's', 'n', 
              'k', 't', 'p', 'f', 'c', 'h', 'q', 'm', 'g']

LATIN_FREQ = {'e': 0.127, 'a': 0.082, 'i': 0.070, 'o': 0.075, 'u': 0.028,
              't': 0.091, 's': 0.063, 'r': 0.060, 'n': 0.067, 'm': 0.025,
              'l': 0.040, 'c': 0.027, 'd': 0.043, 'p': 0.019, 'b': 0.015,
              'q': 0.005, 'f': 0.011, 'g': 0.020, 'h': 0.006, 'v': 0.010}

LATIN_ENDINGS = ['us', 'um', 'is', 'ae', 'am', 'em', 'as', 'es', 'os', 'orum',
                 'ibus', 'arum', 'ens', 'ans', 'unt', 'tur', 'ere', 'ire']

ARABIC_FREQ = {'a': 0.165, 'l': 0.084, 'm': 0.047, 'n': 0.054, 'r': 0.042,
               'w': 0.039, 'y': 0.058, 'h': 0.029, 'b': 0.024, 't': 0.030,
               's': 0.035, 'd': 0.015, 'k': 0.021, 'f': 0.014, 'q': 0.010,
               'z': 0.005, 'j': 0.008, 'sh': 0.020, 'kh': 0.010, 'gh': 0.008}

ARABIC_PATTERNS = ['al', 'wa', 'la', 'fi', 'min', 'an', 'ma', 'li', 'bi', 'ya']

HEBREW_FREQ = {'h': 0.098, 'v': 0.082, 'y': 0.066, 'l': 0.062, 'm': 0.055,
               'a': 0.051, 'sh': 0.049, 'r': 0.047, 'n': 0.045, 't': 0.044,
               'b': 0.038, 'k': 0.035, 's': 0.032, 'd': 0.028, 'p': 0.025,
               'g': 0.015, 'z': 0.012, 'ts': 0.010, 'q': 0.008, 'ch': 0.007}

HEBREW_PATTERNS = ['ha', 'be', 'le', 'mi', 'el', 've', 'shel', 'al', 'et', 'im']


def get_voynich_glyphs():
    """Extract raw glyph data from EVA"""
    pages = get_eva_pages()
    all_text = []
    for page in pages.values():
        for text in page.values():
            clean = re.sub(r'[!?<>@$\[\]\{\}\d]', '', text)
            all_text.append(clean)
    return ' '.join(all_text)


def get_eva_glyph_freq():
    """Get frequency of EVA glyphs"""
    text = get_voynich_glyphs()
    chars = [c for c in text if c.isalpha()]
    total = len(chars)
    freq = Counter(chars)
    return {k: v/total for k, v in freq.items()}


def create_transliteration_maps():
    """Create different transliteration schemes"""
    eva_freq = get_eva_glyph_freq()
    sorted_eva = sorted(eva_freq.keys(), key=lambda x: eva_freq.get(x, 0), reverse=True)
    
    eva_original = {g: g for g in EVA_GLYPHS}
    
    arabic_letters = ['a', 'l', 'm', 'n', 'r', 'w', 'y', 'h', 'b', 't',
                      's', 'd', 'k', 'f', 'q', 'z', 'j', 'x', 'g', 'p']
    arabic_map = {}
    for i, g in enumerate(sorted_eva[:len(arabic_letters)]):
        arabic_map[g] = arabic_letters[i]
    for g in sorted_eva[len(arabic_letters):]:
        arabic_map[g] = g
    
    hebrew_letters = ['h', 'v', 'y', 'l', 'm', 'a', 's', 'r', 'n', 't',
                      'b', 'k', 'z', 'd', 'p', 'g', 'q', 'c', 'x', 'f']
    hebrew_map = {}
    for i, g in enumerate(sorted_eva[:len(hebrew_letters)]):
        hebrew_map[g] = hebrew_letters[i]
    for g in sorted_eva[len(hebrew_letters):]:
        hebrew_map[g] = g
    
    random.seed(42)
    letters = list('abcdefghijklmnopqrstuvwxyz')[:len(EVA_GLYPHS)]
    random.shuffle(letters)
    random_map = {g: letters[i % len(letters)] for i, g in enumerate(EVA_GLYPHS)}
    
    vowels = set('aeiou')
    consonants = set('bcdfghjklmnpqrstvwxyz')
    inverted_map = {}
    for g in EVA_GLYPHS:
        if g in vowels:
            inverted_map[g] = 't'
        elif g in consonants:
            inverted_map[g] = 'a'
        else:
            inverted_map[g] = g
    
    vowel_swap = {'a': 'k', 'e': 's', 'i': 'n', 'o': 't', 'u': 'r',
                  'k': 'a', 's': 'e', 'n': 'i', 't': 'o', 'r': 'u'}
    swapped_map = {g: vowel_swap.get(g, g) for g in EVA_GLYPHS}
    
    return {
        'eva_original': eva_original,
        'arabic_biased': arabic_map,
        'hebrew_biased': hebrew_map,
        'random': random_map,
        'vowel_consonant_swap': swapped_map
    }


def apply_transliteration(text, trans_map):
    """Apply transliteration mapping to text"""
    result = []
    for c in text:
        if c.isalpha():
            result.append(trans_map.get(c, c))
        else:
            result.append(c)
    return ''.join(result)


def calc_letter_freq(text):
    """Calculate letter frequencies"""
    chars = [c for c in text.lower() if c.isalpha()]
    total = len(chars) if chars else 1
    freq = Counter(chars)
    return {k: v/total for k, v in freq.items()}


def freq_similarity(freq1, freq2):
    """Calculate similarity between two frequency distributions"""
    all_keys = set(freq1.keys()) | set(freq2.keys())
    diff_sum = sum(abs(freq1.get(k, 0) - freq2.get(k, 0)) for k in all_keys)
    return max(0, 1 - diff_sum / 2)


def calc_ending_score(words, target_endings):
    """Calculate how many words end with target endings"""
    if not words:
        return 0
    matches = sum(1 for w in words if any(w.endswith(e) for e in target_endings))
    return matches / len(words)


def calc_pattern_score(text, patterns):
    """Calculate how many target patterns appear in text"""
    text_lower = text.lower()
    found = sum(1 for p in patterns if p in text_lower)
    return found / len(patterns)


def analyze_transliteration(name, trans_map, raw_text):
    """Analyze one transliteration scheme"""
    trans_text = apply_transliteration(raw_text, trans_map)
    
    words = [w for w in re.split(r'[\s.\-,=]+', trans_text) if len(w) > 1 and w.isalpha()]
    letter_freq = calc_letter_freq(trans_text)
    
    latin_freq_sim = freq_similarity(letter_freq, LATIN_FREQ)
    arabic_freq_sim = freq_similarity(letter_freq, ARABIC_FREQ)
    hebrew_freq_sim = freq_similarity(letter_freq, HEBREW_FREQ)
    
    latin_ending = calc_ending_score(words, LATIN_ENDINGS)
    arabic_pattern = calc_pattern_score(trans_text, ARABIC_PATTERNS)
    hebrew_pattern = calc_pattern_score(trans_text, HEBREW_PATTERNS)
    
    latin_score = (latin_freq_sim * 0.5 + latin_ending * 0.5)
    arabic_score = (arabic_freq_sim * 0.5 + arabic_pattern * 0.5)
    hebrew_score = (hebrew_freq_sim * 0.5 + hebrew_pattern * 0.5)
    
    total = latin_score + arabic_score + hebrew_score
    if total > 0:
        latin_score /= total
        arabic_score /= total  
        hebrew_score /= total
    
    return {
        'name': name,
        'mapping_sample': {k: v for k, v in list(trans_map.items())[:10]},
        'letter_frequencies': dict(sorted(letter_freq.items(), key=lambda x: -x[1])[:10]),
        'scores': {
            'latin': round(latin_score, 4),
            'arabic': round(arabic_score, 4),
            'hebrew': round(hebrew_score, 4)
        },
        'details': {
            'latin_freq_similarity': round(latin_freq_sim, 4),
            'latin_ending_score': round(latin_ending, 4),
            'arabic_freq_similarity': round(arabic_freq_sim, 4),
            'arabic_pattern_score': round(arabic_pattern, 4),
            'hebrew_freq_similarity': round(hebrew_freq_sim, 4),
            'hebrew_pattern_score': round(hebrew_pattern, 4)
        },
        'sample_words': words[:20]
    }


def detect_bias(results):
    """Determine if EVA shows bias toward Latin"""
    eva_result = next((r for r in results if r['name'] == 'eva_original'), None)
    if not eva_result:
        return False, "EVA original not found"
    
    eva_latin = eva_result['scores']['latin']
    other_latin_scores = [r['scores']['latin'] for r in results if r['name'] != 'eva_original']
    
    avg_other = sum(other_latin_scores) / len(other_latin_scores) if other_latin_scores else 0
    
    bias_threshold = 0.05
    bias_detected = eva_latin > avg_other + bias_threshold
    
    if bias_detected:
        conclusion = (f"BIAS DETECTED: EVA shows {(eva_latin - avg_other)*100:.1f}% higher Latin score "
                     f"than alternatives. Latin-like findings may be artifacts of EVA design.")
    else:
        diff = eva_latin - avg_other
        if abs(diff) < bias_threshold:
            conclusion = (f"NO SIGNIFICANT BIAS: EVA Latin score ({eva_latin:.3f}) is similar to "
                         f"alternatives (avg {avg_other:.3f}). Latin-like findings appear genuine.")
        else:
            conclusion = (f"ANTI-BIAS: EVA shows {(avg_other - eva_latin)*100:.1f}% LOWER Latin score "
                         f"than alternatives. This suggests Voynich may NOT be Latin-based.")
    
    return bias_detected, conclusion


def run_bias_test():
    """Run the complete EVA bias test"""
    print("=" * 60)
    print("EVA TRANSLITERATION BIAS TEST - Track 37")
    print("=" * 60)
    
    print("\n[1/4] Loading Voynich manuscript data...")
    raw_text = get_voynich_glyphs()
    print(f"  Loaded {len(raw_text)} characters")
    
    print("\n[2/4] Creating alternative transliterations...")
    trans_maps = create_transliteration_maps()
    for name in trans_maps:
        print(f"  - {name}")
    
    print("\n[3/4] Analyzing each transliteration...")
    results = []
    for name, trans_map in trans_maps.items():
        result = analyze_transliteration(name, trans_map, raw_text)
        results.append(result)
        print(f"  {name}: Latin={result['scores']['latin']:.3f}, "
              f"Arabic={result['scores']['arabic']:.3f}, Hebrew={result['scores']['hebrew']:.3f}")
    
    print("\n[4/4] Testing for bias...")
    bias_detected, conclusion = detect_bias(results)
    
    output = {
        'transliterations_tested': results,
        'bias_detected': bias_detected,
        'conclusion': conclusion,
        'methodology': {
            'description': 'Created 5 different letter-to-glyph mappings and compared language scores',
            'transliterations': list(trans_maps.keys()),
            'metrics': ['letter frequency similarity', 'ending patterns', 'common patterns']
        }
    }
    
    RESULTS_DIR.mkdir(exist_ok=True)
    
    with open(RESULTS_DIR / 'eva_bias_test.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    print("\n LANGUAGE SCORES BY TRANSLITERATION:")
    print("-" * 50)
    print(f"{'Transliteration':<25} {'Latin':>8} {'Arabic':>8} {'Hebrew':>8}")
    print("-" * 50)
    for r in results:
        print(f"{r['name']:<25} {r['scores']['latin']:>8.3f} {r['scores']['arabic']:>8.3f} {r['scores']['hebrew']:>8.3f}")
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print(f"\n{conclusion}")
    
    if bias_detected:
        print("\n⚠️  IMPLICATIONS:")
        print("   - All 'Latin-like' findings should be treated with caution")
        print("   - The EVA system may have embedded Latin assumptions")
        print("   - Consider Voynich as unknown script family")
    else:
        print("\n✅ IMPLICATIONS:")
        print("   - Latin-like findings appear to be genuine properties")
        print("   - Focus on Latin/Romance language hypothesis")
        print("   - Continue abbreviation/encoding analysis")
    
    print(f"\n📁 Results saved to {RESULTS_DIR / 'eva_bias_test.json'}")
    
    return output


if __name__ == "__main__":
    run_bias_test()
