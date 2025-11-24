#!/usr/bin/env python3
"""
Attempt to identify plant names by pattern matching with known medieval plants
"""

import re
from collections import Counter, defaultdict
from pathlib import Path

# Known medieval plant names (Latin) and their common characteristics
MEDIEVAL_PLANTS = {
    # Common herbal plants with their Latin names
    'centaurea': {'syllables': 4, 'starts': 'c', 'ends': 'a'},
    'helleborus': {'syllables': 4, 'starts': 'h', 'ends': 's'},
    'artemisia': {'syllables': 4, 'starts': 'a', 'ends': 'a'},
    'ocimum': {'syllables': 3, 'starts': 'o', 'ends': 'm'},  # basil
    'melissa': {'syllables': 3, 'starts': 'm', 'ends': 'a'},
    'mentha': {'syllables': 2, 'starts': 'm', 'ends': 'a'},
    'salvia': {'syllables': 3, 'starts': 's', 'ends': 'a'},
    'rosmarinus': {'syllables': 4, 'starts': 'r', 'ends': 's'},
    'cannabis': {'syllables': 3, 'starts': 'c', 'ends': 's'},
    'papaver': {'syllables': 3, 'starts': 'p', 'ends': 'r'},  # poppy
    'viola': {'syllables': 3, 'starts': 'v', 'ends': 'a'},
    'urtica': {'syllables': 3, 'starts': 'u', 'ends': 'a'},  # nettle
    'plantago': {'syllables': 3, 'starts': 'p', 'ends': 'o'},
    'aquilegia': {'syllables': 4, 'starts': 'a', 'ends': 'a'},
    'mandragora': {'syllables': 4, 'starts': 'm', 'ends': 'a'},  # mandrake
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

def find_unique_patterns(words):
    """Find words with unique patterns that might be plant names"""
    # Count words
    word_counts = Counter(words)
    
    # Words appearing 10-100 times (plant-name-like frequency)
    candidates = [(w, c) for w, c in word_counts.items() 
                  if 10 <= c <= 100 and 5 <= len(w) <= 9]
    
    return sorted(candidates, key=lambda x: -x[1])

def strip_affixes(word):
    """Strip known grammatical affixes to get potential root"""
    # Known prefixes
    prefixes = ['4oh', '4ok', '4o', 'oh', 'ok', '1c', '1o', '1', '8a', '8', 's', 'e', 'a', 'o']
    # Known suffixes
    suffixes = ['89', 'c89', '79', 'c9', 'am', 'oe', 'ay', 'ae', 'an', '9', 'y', 'e', 'm']
    
    root = word
    prefix_found = ''
    suffix_found = ''
    
    # Strip prefix
    for p in sorted(prefixes, key=len, reverse=True):
        if root.startswith(p):
            prefix_found = p
            root = root[len(p):]
            break
    
    # Strip suffix
    for s in sorted(suffixes, key=len, reverse=True):
        if root.endswith(s) and len(root) > len(s):
            suffix_found = s
            root = root[:-len(s)]
            break
    
    return prefix_found, root, suffix_found

def analyze_roots(words):
    """Analyze root morphemes after stripping affixes"""
    roots = defaultdict(list)
    
    for w in words:
        pref, root, suff = strip_affixes(w)
        if 2 <= len(root) <= 5:  # Reasonable root length
            roots[root].append((w, pref, suff))
    
    return roots

def main():
    print("=" * 70)
    print("🌿 PLANT NAME IDENTIFICATION ATTEMPT 🌿")
    print("=" * 70)
    
    words = load_words()
    
    # Find potential plant name candidates
    print("\n📊 POTENTIAL PLANT NAME CANDIDATES (5-9 chars, freq 10-100):\n")
    candidates = find_unique_patterns(words)[:30]
    
    for word, count in candidates:
        pref, root, suff = strip_affixes(word)
        print(f"  {word:15} (×{count:3}) → prefix='{pref}' root='{root}' suffix='{suff}'")
    
    # Analyze roots
    print("\n" + "=" * 70)
    print("📊 ROOT MORPHEME ANALYSIS")
    print("=" * 70)
    
    roots = analyze_roots(words)
    
    # Find roots with multiple attestations (different affixes)
    multi_roots = [(root, forms) for root, forms in roots.items() 
                   if len(set(f[0] for f in forms)) >= 5]
    multi_roots.sort(key=lambda x: -len(x[1]))
    
    print("\n  ROOTS WITH 5+ DIFFERENT WORD FORMS (potential lexemes):\n")
    for root, forms in multi_roots[:20]:
        unique_words = set(f[0] for f in forms)
        total = len(forms)
        print(f"  Root '{root:8}' → {len(unique_words)} forms, {total} occurrences")
        print(f"    Examples: {list(unique_words)[:5]}")
    
    # Look for patterns similar to Latin plant names
    print("\n" + "=" * 70)
    print("🔬 PATTERN MATCHING WITH LATIN PLANT NAMES")
    print("=" * 70)
    
    word_counts = Counter(words)
    
    # Latin plant names often end in -a, -um, -us
    # In Voynich, these might map to -oe, -am, -9
    
    print("\n  Words ending in 'am' (potential Latin -um/-am nouns):")
    am_words = [(w, c) for w, c in word_counts.items() 
                if w.endswith('am') and 5 <= len(w) <= 9 and c >= 10]
    for w, c in sorted(am_words, key=lambda x: -x[1])[:15]:
        pref, root, suff = strip_affixes(w)
        print(f"    {w:15} (×{c:3}) root='{root}'")
    
    print("\n  Words with '4oh' prefix (most common, likely plant terms):")
    oh_words = [(w, c) for w, c in word_counts.items() 
                if w.startswith('4oh') and 6 <= len(w) <= 10]
    for w, c in sorted(oh_words, key=lambda x: -x[1])[:15]:
        pref, root, suff = strip_affixes(w)
        print(f"    {w:15} (×{c:3}) root='{root}'")
    
    # Hypothesis: specific root-to-plant mapping
    print("\n" + "=" * 70)
    print("💡 HYPOTHETICAL PLANT NAME MAPPINGS")
    print("=" * 70)
    print("""
Based on pattern analysis, here are hypothetical mappings:

VOYNICH ROOT → POSSIBLE MEANING (speculative!)

  'c' / 'hc'  → Could be "herb" generic (Latin: herba)
  'C' / 'HC'  → Variant of above (capital = different herb?)
  'ok'        → Could be preparation/medicine term
  'h' / 'oh'  → Core botanical term  
  'an'        → Might relate to "root" (Latin: radix)
  'ae'        → Might relate to "flower" (Latin: flos)
  'ay'        → Might relate to "leaf" (Latin: folium)
  'am'        → Might relate to "seed/fruit" (Latin: semen)

COMMON WORD INTERPRETATIONS (highly speculative):

  '4ohan'  (266×) → "of/from the herb" (generic plant reference)
  '4oham'  (235×) → "the herb [object]"  
  '4ohC9'  (237×) → "the [specific] herb [nominative]"
  'okc79'  (48×)  → "preparation for [something]"
  '1co89'  (46×)  → "root of the [plant]"

POTENTIAL PLANT NAMES (words with unique patterns):

  Words that DON'T follow common patterns might be proper nouns!
  These include words with unusual characters or letter combinations.
""")
    
    # Find words with unusual characters (potential proper nouns)
    print("\n  WORDS WITH UNUSUAL CHARACTERS (potential proper nouns):")
    unusual = []
    for w, c in word_counts.items():
        # Words containing capital letters mid-word or unusual symbols
        if any(ch.isupper() and i > 0 for i, ch in enumerate(w)):
            unusual.append((w, c))
        elif any(ch in '!@#$%^&*()' for ch in w):
            unusual.append((w, c))
    
    for w, c in sorted(unusual, key=lambda x: -x[1])[:20]:
        print(f"    {w:15} (×{c:3})")

if __name__ == '__main__':
    main()

