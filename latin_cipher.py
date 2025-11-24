#!/usr/bin/env python3
"""
Frequency-based cipher attempt using Latin letter frequencies
"""

import re
from collections import Counter
from pathlib import Path

# Latin letter frequencies (medieval Latin)
# From corpus analysis of medieval manuscripts
LATIN_FREQ = [
    ('e', 0.115), ('i', 0.105), ('u', 0.085), ('a', 0.080),
    ('t', 0.075), ('s', 0.070), ('n', 0.065), ('r', 0.060),
    ('o', 0.055), ('m', 0.045), ('c', 0.040), ('l', 0.035),
    ('d', 0.030), ('p', 0.025), ('b', 0.020), ('q', 0.015),
    ('f', 0.015), ('g', 0.010), ('h', 0.010), ('x', 0.005),
    ('v', 0.010), ('z', 0.003), ('k', 0.002), ('y', 0.002),
]

# Italian letter frequencies (15th century)
ITALIAN_FREQ = [
    ('e', 0.118), ('a', 0.117), ('i', 0.103), ('o', 0.097),
    ('n', 0.069), ('t', 0.062), ('r', 0.063), ('l', 0.065),
    ('s', 0.050), ('c', 0.045), ('d', 0.037), ('u', 0.030),
    ('p', 0.030), ('m', 0.025), ('g', 0.016), ('v', 0.021),
    ('h', 0.015), ('f', 0.010), ('b', 0.009), ('z', 0.007),
    ('q', 0.005),
]

def load_voynich():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    lines = []
    for line in text.split('\n'):
        clean = re.sub(r'<[^>]+>', '', line)
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            lines.append(clean.strip())
    return '\n'.join(lines)

def get_chars(text):
    chars = re.sub(r'[.,\s\n]', '', text)
    return list(chars)

def get_words(text):
    words = re.split(r'[.,\s]+', text)
    return [w for w in words if w and len(w) > 0]

def build_freq_mapping(voynich_freq, target_freq):
    """Map Voynich chars to target language by frequency"""
    mapping = {}
    sorted_voynich = sorted(voynich_freq.items(), key=lambda x: -x[1])
    
    for i, (v_char, _) in enumerate(sorted_voynich):
        if i < len(target_freq):
            mapping[v_char] = target_freq[i][0]
        else:
            mapping[v_char] = '?'
    return mapping

def apply_mapping(text, mapping):
    result = []
    for char in text:
        result.append(mapping.get(char, char))
    return ''.join(result)

def analyze_latin_words(text):
    """Check for potential Latin words in decoded text"""
    common_latin = [
        'et', 'in', 'de', 'ad', 'est', 'qui', 'non', 'cum', 'sed',
        'per', 'que', 'hoc', 'sum', 'aut', 'pro', 'ita', 'nec',
        'sic', 'sua', 'quo', 'nam', 'vel', 'ergo', 'aqua', 'terra',
        'herba', 'folia', 'radix', 'semen', 'flores', 'medicus',
    ]
    
    words = text.lower().split()
    matches = []
    for word in words:
        clean = ''.join(c for c in word if c.isalpha())
        if clean in common_latin:
            matches.append(clean)
    
    return matches

def check_latin_patterns(decoded):
    """Check for Latin morphological patterns"""
    words = decoded.lower().split()
    
    # Latin case endings
    endings = {
        'us': 'nom.sing.masc',
        'um': 'acc.sing.neut',
        'is': 'gen.sing',
        'ae': 'gen.sing.fem',
        'am': 'acc.sing.fem',
        'em': 'acc.sing',
        'orum': 'gen.plur',
        'arum': 'gen.plur.fem',
    }
    
    found = Counter()
    for word in words:
        for ending, case in endings.items():
            if word.endswith(ending):
                found[case] += 1
    
    return found

def main():
    print("=" * 60)
    print("🔮 LATIN FREQUENCY CIPHER ATTEMPT 🔮")
    print("=" * 60)
    
    text = load_voynich()
    chars = get_chars(text)
    char_freq = Counter(chars)
    total = sum(char_freq.values())
    char_probs = {c: n/total for c, n in char_freq.items()}
    
    print("\n📊 VOYNICH CHARACTER FREQUENCIES (top 20):")
    for char, count in char_freq.most_common(20):
        prob = count / total
        print(f"  '{char}': {prob:.3f}")
    
    # Try Latin mapping
    print("\n" + "=" * 60)
    print("🔤 ATTEMPTING LATIN FREQUENCY MAPPING...")
    print("=" * 60)
    
    latin_mapping = build_freq_mapping(char_probs, LATIN_FREQ)
    
    print("\n  Mapping (Voynich -> Latin):")
    for v, l in list(latin_mapping.items())[:15]:
        print(f"    '{v}' -> '{l}'")
    
    # Apply to sample
    words = get_words(text)
    sample_words = words[:100]
    decoded_words = [apply_mapping(w, latin_mapping) for w in sample_words]
    
    print("\n📝 SAMPLE DECODED TEXT (Latin mapping):")
    print("  Original:")
    print(' '.join(sample_words[:20]))
    print("\n  Decoded:")
    print(' '.join(decoded_words[:20]))
    
    # Check for Latin patterns
    decoded_text = ' '.join(decoded_words)
    matches = analyze_latin_words(decoded_text)
    
    print(f"\n  Found {len(matches)} potential Latin words:")
    for match in set(matches):
        print(f"    '{match}'")
    
    # Case ending analysis
    cases = check_latin_patterns(decoded_text)
    print("\n  Latin case endings found:")
    for case, count in cases.most_common(10):
        print(f"    {case}: {count}")
    
    # Try Italian mapping
    print("\n" + "=" * 60)
    print("🔤 ATTEMPTING ITALIAN FREQUENCY MAPPING...")
    print("=" * 60)
    
    italian_mapping = build_freq_mapping(char_probs, ITALIAN_FREQ)
    decoded_italian = [apply_mapping(w, italian_mapping) for w in sample_words]
    
    print("\n📝 SAMPLE DECODED TEXT (Italian mapping):")
    print(' '.join(decoded_italian[:20]))
    
    # Unique approach: What if some chars are multi-character?
    print("\n" + "=" * 60)
    print("💡 ALTERNATIVE HYPOTHESIS: MULTI-CHAR MAPPING")
    print("=" * 60)
    
    # The '89' ending appears so often - could it be one sound?
    # The '4o' prefix appears so often - could it be an article?
    
    alt_mapping = {
        '4o': 'la ',  # Italian article "la" or Latin preposition
        '89': 'us',   # Latin masculine ending
        '9': 'is',    # Latin genitive/nominative
        'am': 'am',   # Could stay as Latin accusative
        '1c': 'qu',   # Qu- is common in Latin
        '8': 'd',
        'o': 'o',
        'h': 'h',
        'a': 'a',
        'e': 'e',
        'y': 'i',
        'c': 'c',
        's': 's',
        'k': 'c',
        'm': 'm',
        'n': 'n',
    }
    
    def multi_apply(word, mapping):
        result = word
        # Apply multi-char mappings first
        for k in sorted(mapping.keys(), key=len, reverse=True):
            result = result.replace(k, mapping[k])
        return result
    
    decoded_multi = [multi_apply(w, alt_mapping) for w in sample_words]
    
    print("\n📝 WITH MULTI-CHARACTER MAPPING:")
    print(' '.join(decoded_multi[:20]))
    
    # Focus on potential plant names
    print("\n" + "=" * 60)
    print("🌿 LOOKING FOR BOTANICAL TERMS...")
    print("=" * 60)
    
    # Words with '4oh' might be plant-related
    plant_candidates = [w for w in words if '4oh' in w or 'oh' in w[:3]]
    print(f"\n  Potential plant name patterns (containing 'oh' root): {len(plant_candidates)} words")
    print(f"  Examples: {list(set(plant_candidates))[:15]}")

if __name__ == '__main__':
    main()


