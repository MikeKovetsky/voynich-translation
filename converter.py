#!/usr/bin/env python3
"""Claston <-> EVA Transcription Converter"""

import re

# EVA to Claston mapping (EVA is the standard, Claston is Glen Claston v101)
# Built from comparing word frequencies and paradigms

# The key insight: EVA uses more digraphs while Claston uses single characters

# Single character mappings (applied AFTER digraphs)
EVA_CHAR_TO_CLASTON = {
    # Direct matches
    'o': 'o',
    'a': 'a',
    's': 's',
    'f': 'f',
    'i': 'i',
    'n': 'n',
    # Different mappings
    'y': '9',      # Word-final marker (37% of words!)
    'd': '8',      # Different
    'k': 'h',      # Different (EVA k = Claston h)
    't': 'k',      # Different (EVA t = Claston k)
    'l': 'e',      # Different (but 'ol' -> 'oe' handled as digraph)
    'r': 'y',      # Different (but 'ar' -> 'ay' handled as digraph)
    'e': 'c',      # Different (EVA e = Claston c)
    'q': '4',      # Article prefix (qo = 4o)
    'p': 'g',      # Different
    'm': 'p',      # Different
}

# Digraph/multi-char mappings (EVA -> Claston) - applied FIRST
# Sorted by length (longest first) during processing
EVA_DIGRAPH_TO_CLASTON = {
    # Word endings (most specific first)
    'aiiin': 'aim',  # Rare triple-i ending
    'aiin': 'am',    # Accusative ending: daiin -> 8am, qokaiin -> 4oham
    'eedy': 'cc89',  # qokeedy -> 4ohcc89
    'edy': 'c89',    # qokedy -> 4ohc89, chedy -> 1c89
    'eey': 'cc9',    # qokeey -> 4ohcc9
    'ey': 'c9',      # chey -> 1c9
    'dy': '89',      # Genitive plural
    'ain': 'an',     # dain -> 8an
    'iin': 'M',      # Alternative
    # Position-specific endings
    'ol': 'oe',      # chol -> 1oe
    'or': 'oy',      # chor -> 1oy
    'al': 'ae',      # dal -> 8ae
    'ar': 'ay',      # dar -> 8ay
    'ir': 'iy',      # dair -> 8aiy
    # Consonant clusters
    'ckh': 'K',      # Special marker
    'cth': '1h',     # cth digraph
    'cph': '1g',     # cph digraph
    'cfh': 'fh',     # cfh digraph
    'ch': '1',       # Most important digraph (AFTER ckh, cth, cph)
    'sh': '2',       # Second most important
}

# Claston to EVA (reverse of above)
CLASTON_CHAR_TO_EVA = {v: k for k, v in EVA_CHAR_TO_CLASTON.items()}

# Claston digraphs to EVA - applied first, longest first
CLASTON_DIGRAPH_TO_EVA = {
    # Endings (longest first)
    'cc89': 'eedy',
    'c89': 'edy',
    'cc9': 'eey',
    'c9': 'ey',
    '89': 'dy',
    'am': 'aiin',
    'aim': 'aiiin',
    'an': 'ain',
    'M': 'iin',
    # Positional
    'oe': 'ol',
    'oy': 'or',
    'ae': 'al',
    'ay': 'ar',
    'iy': 'ir',
    # Consonant clusters
    'K': 'ckh',
    'H': 'ckh',
    '1h': 'cth',
    '1g': 'cph',
    'fh': 'cfh',
    '1': 'ch',   # AFTER 1h, 1g
    '2': 'sh',
}


def eva_to_claston(word):
    """Convert EVA word to Claston notation."""
    result = word
    
    # Apply digraph replacements using unique placeholders to avoid double-mapping
    placeholders = {}
    placeholder_id = 0
    
    for eva, claston in sorted(EVA_DIGRAPH_TO_CLASTON.items(), key=lambda x: -len(x[0])):
        if eva in result:
            placeholder = f'\x00{placeholder_id}\x00'
            placeholders[placeholder] = claston
            result = result.replace(eva, placeholder)
            placeholder_id += 1
    
    # Apply single character replacements to remaining EVA chars
    out = []
    i = 0
    while i < len(result):
        if result[i] == '\x00':
            # Find end of placeholder
            end = result.index('\x00', i + 1) + 1
            placeholder = result[i:end]
            out.append(placeholders[placeholder])
            i = end
        else:
            out.append(EVA_CHAR_TO_CLASTON.get(result[i], result[i]))
            i += 1
    
    return ''.join(out)


def claston_to_eva(word):
    """Convert Claston word to EVA notation."""
    result = word
    
    # Apply digraph replacements using unique placeholders to avoid double-mapping
    placeholders = {}
    placeholder_id = 0
    
    for claston, eva in sorted(CLASTON_DIGRAPH_TO_EVA.items(), key=lambda x: -len(x[0])):
        if claston in result:
            placeholder = f'\x00{placeholder_id}\x00'
            placeholders[placeholder] = eva
            result = result.replace(claston, placeholder)
            placeholder_id += 1
    
    # Apply single character replacements to remaining Claston chars
    out = []
    i = 0
    while i < len(result):
        if result[i] == '\x00':
            # Find end of placeholder
            end = result.index('\x00', i + 1) + 1
            placeholder = result[i:end]
            out.append(placeholders[placeholder])
            i = end
        else:
            out.append(CLASTON_CHAR_TO_EVA.get(result[i], result[i]))
            i += 1
    
    return ''.join(out)


def test_conversions():
    """Test key conversions."""
    tests = [
        # (EVA, expected Claston)
        ('daiin', '8am'),
        ('qokaiin', '4oham'),
        ('chedy', '1c89'),
        ('qokeey', '4ohcc9'),
        ('dar', '8ay'),
        ('dal', '8ae'),
        ('chol', '1oe'),
        ('chey', '1c9'),
        ('qokeedy', '4ohcc89'),
        ('qokedy', '4ohc89'),
    ]
    
    print("EVA → Claston Conversion Tests:")
    print("-" * 50)
    
    all_pass = True
    for eva, expected in tests:
        result = eva_to_claston(eva)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_pass = False
        print(f"  {status} {eva:15s} → {result:15s} (expected: {expected})")
    
    print("\nClaston → EVA Conversion Tests:")
    print("-" * 50)
    
    reverse_tests = [
        ('8am', 'daiin'),
        ('4oham', 'qokaiin'),
        ('1c89', 'chedy'),
    ]
    
    for claston, expected in reverse_tests:
        result = claston_to_eva(claston)
        status = "✅" if result == expected else "❌"
        if result != expected:
            all_pass = False
        print(f"  {status} {claston:15s} → {result:15s} (expected: {expected})")
    
    return all_pass


if __name__ == '__main__':
    print("=" * 60)
    print("CLASTON <-> EVA TRANSCRIPTION CONVERTER")
    print("=" * 60)
    print()
    
    success = test_conversions()
    
    print()
    print("=" * 60)
    print("MAPPING REFERENCE")
    print("=" * 60)
    print("""
KEY CHARACTER MAPPINGS:
  EVA     Claston    Notes
  ---     -------    -----
  y       9          Word-final marker (37% of words)
  d       8          
  k       h          
  t       k          
  l       e          
  r       y          
  e       c          
  q       4          Article prefix
  
KEY DIGRAPH MAPPINGS:
  EVA     Claston    Notes
  ---     -------    -----
  ch      1          Verbal stem marker
  sh      2          
  aiin    am         Accusative ending
  dy      89         Genitive plural
  eey     cc9        Nominative ending variant
  ol      oe         Locative
  ar      ay         Genitive
""")
    
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed - mappings need refinement")
