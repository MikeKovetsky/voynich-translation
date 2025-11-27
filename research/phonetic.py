#!/usr/bin/env python3
"""
Phonetic mapping attempt - what if Voynich encodes sounds?
Try multiple phonetic hypotheses
"""

import re
from collections import Counter
from pathlib import Path

# Different phonetic mapping hypotheses
# Based on frequency analysis mapped to common language sound frequencies

# Hypothesis 1: Latin-like phonetics
LATIN_MAP = {
    'o': 'a',   # Most common vowel
    '9': 'is',  # Common ending
    'a': 'e',   # Second vowel
    'c': 'k',   # Consonant
    '1': 't',   # Common initial consonant
    'e': 'o',   # Third vowel
    '8': 'd',   # Voiced stop
    'h': 'r',   # Liquid
    'y': 'i',   # High vowel
    'k': 'n',   # Nasal
    '4': 'qu',  # Initial cluster
    'm': 'm',   # Nasal
    '2': 's',   # Sibilant
    'C': 'ch',  # Variant
    '7': 'l',   # Liquid
    's': 'x',   # Rare sound
    'n': 'um',  # Ending
    'p': 'p',   # Stop
    'K': 'c',   # Variant
    'g': 'g',   # Voiced stop
}

# Hypothesis 2: Hebrew-like (consonant-heavy)
HEBREW_MAP = {
    'o': 'a',   # Vowel filler
    '9': 'n',   # Final nun
    'a': 'i',   # Vowel
    'c': 'sh',  # Shin
    '1': 'y',   # Yod
    'e': 'e',   # Vowel
    '8': 'd',   # Dalet
    'h': 'h',   # He
    'y': 'i',   # Yod as vowel
    'k': 'k',   # Kaf
    '4': 'b',   # Bet
    'm': 'm',   # Mem
    '2': 'ts',  # Tsade
    'C': 'ch',  # Chet
    '7': 'l',   # Lamed
    's': 's',   # Samech
    'n': 'n',   # Nun
}

# Hypothesis 3: Romance/Italian
ROMANCE_MAP = {
    'o': 'o',   # Common vowel
    '9': 'ne',  # Suffix
    'a': 'a',   # Vowel
    'c': 'c',   # Consonant
    '1': 'l',   # Liquid
    'e': 'e',   # Vowel
    '8': 'd',   # Consonant
    'h': 'r',   # Trill
    'y': 'i',   # Vowel
    'k': 'n',   # Nasal
    '4': 'qu',  # Q cluster
    'm': 'mo',  # Suffix
    '2': 's',   # Sibilant
    'C': 'ce',  # Variant
    '7': 'gn',  # Nasal cluster
    's': 'z',   # Voiced s
    'n': 'n',   # Nasal
}

# Hypothesis 4: Turkish-like (agglutinative fits)
TURKISH_MAP = {
    'o': 'a',   # Low vowel
    '9': 'lar', # Plural suffix!
    'a': 'e',   # Front vowel
    'c': 'k',   # Consonant
    '1': 'y',   # Consonant
    'e': 'i',   # High vowel
    '8': 'd',   # Consonant
    'h': 'r',   # Liquid
    'y': 'ı',   # Back unrounded
    'k': 'n',   # Nasal
    '4': 'b',   # Consonant
    'm': 'm',   # Nasal
    '2': 'ş',   # Sh sound
    'C': 'ç',   # Ch sound
    '7': 'l',   # Liquid
    's': 's',   # Sibilant
}

def load_words():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    words = []
    for line in text.split('\n'):
        clean = re.sub(r'<[^>]+>', '', line)
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            ws = re.split(r'[.,\s]+', clean)
            words.extend([w for w in ws if w and len(w) > 0])
    return words

def apply_map(word, mapping):
    """Apply phonetic mapping to a word"""
    result = []
    for char in word:
        if char in mapping:
            result.append(mapping[char])
        elif char.lower() in mapping:
            result.append(mapping[char.lower()])
        else:
            result.append(char)
    return ''.join(result)

def check_for_words(decoded_words, known_words):
    """Check if any decoded words match known words"""
    matches = []
    for orig, decoded in decoded_words:
        clean = ''.join(c for c in decoded.lower() if c.isalpha())
        if clean in known_words:
            matches.append((orig, decoded, clean))
    return matches

# Common words in various languages
LATIN_WORDS = {
    'aqua', 'herba', 'radix', 'folium', 'flos', 'semen', 'de', 'et', 'in',
    'est', 'qui', 'quod', 'per', 'cum', 'ad', 'terra', 'luna', 'sol',
    'medicina', 'planta', 'natura', 'virtus', 'color', 'odor', 'sapor',
}

ITALIAN_WORDS = {
    'acqua', 'erba', 'radice', 'foglia', 'fiore', 'seme', 'di', 'e', 'in',
    'il', 'la', 'le', 'del', 'della', 'per', 'con', 'a', 'terra', 'luna',
    'sole', 'medicina', 'pianta', 'natura', 'colore', 'odore', 'sapore',
}

def main():
    print("=" * 70)
    print("🔊 PHONETIC MAPPING ANALYSIS 🔊")
    print("=" * 70)
    
    words = load_words()
    word_counts = Counter(words)
    
    # Get most common words for testing
    common_words = [w for w, c in word_counts.most_common(100)]
    
    # Test each hypothesis
    hypotheses = [
        ("Latin-like", LATIN_MAP),
        ("Hebrew-like", HEBREW_MAP),
        ("Romance", ROMANCE_MAP),
        ("Turkish-like", TURKISH_MAP),
    ]
    
    for name, mapping in hypotheses:
        print(f"\n{'='*70}")
        print(f"📊 HYPOTHESIS: {name.upper()} PHONETICS")
        print(f"{'='*70}")
        
        print("\n  TOP 30 DECODED WORDS:")
        decoded = [(w, apply_map(w, mapping)) for w in common_words[:30]]
        
        for orig, dec in decoded:
            print(f"    {orig:15} → {dec}")
        
        # Check for matches with known words
        all_decoded = [(w, apply_map(w, mapping)) for w in word_counts.keys()]
        
        if name == "Latin-like":
            matches = check_for_words(all_decoded, LATIN_WORDS)
            if matches:
                print(f"\n  POTENTIAL LATIN MATCHES:")
                for orig, dec, match in matches[:10]:
                    print(f"    {orig} → {dec} ≈ {match}")
        
        if name == "Romance":
            matches = check_for_words(all_decoded, ITALIAN_WORDS)
            if matches:
                print(f"\n  POTENTIAL ITALIAN MATCHES:")
                for orig, dec, match in matches[:10]:
                    print(f"    {orig} → {dec} ≈ {match}")
    
    # Try specific plant name patterns
    print("\n" + "=" * 70)
    print("🌿 BOTANICAL TERM ANALYSIS WITH LATIN MAP")
    print("=" * 70)
    
    # Focus on '4oh' prefix words
    botanical = [w for w in word_counts if w.startswith('4oh')][:20]
    
    print("\n  BOTANICAL TERMS (4oh- prefix = 'qua-r-' in Latin map):")
    for word in botanical:
        latin = apply_map(word, LATIN_MAP)
        print(f"    {word:15} → {latin}")
    
    # Try '8am' pattern (very common)
    print("\n  COMMON SUFFIX PATTERN '8am' = 'dim' in Latin map:")
    am_words = [w for w, c in word_counts.items() if w.endswith('8am') or w.endswith('am')][:15]
    for word in am_words:
        latin = apply_map(word, LATIN_MAP)
        print(f"    {word:15} → {latin}")
    
    # Summary
    print("\n" + "=" * 70)
    print("💡 PHONETIC ANALYSIS CONCLUSIONS")
    print("=" * 70)
    print("""
OBSERVATIONS:

1. No phonetic mapping produces clearly recognizable text
   → Either the encoding is more complex than simple substitution
   → Or the source language is not Latin/Italian/Hebrew/Turkish

2. Some patterns are suggestive:
   - Latin map: '4oh' → 'quar' (like 'quartus', 'quare'?)
   - '8am' → 'dim' or 'dam' (like Latin suffixes?)
   
3. The most likely scenarios:
   a) A language we haven't mapped correctly
   b) A more complex encoding (polyalphabetic, etc.)
   c) A constructed/artificial language
   d) An extinct/undocumented language

4. IMPORTANT: The grammatical structure we found is REAL
   regardless of what the sounds/words mean!

NEXT STEPS FOR FULL DECIPHERMENT:
   
   1. Find a bilingual text or known passage
   2. Identify proper nouns (star names, place names)
   3. Match illustrations to known medieval botanical illustrations
   4. Compare with Pahlavi/Middle Persian more carefully
""")

if __name__ == '__main__':
    main()





