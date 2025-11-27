#!/usr/bin/env python3
"""
Voynich Manuscript Decipherment Attempt
Testing the Pahlavi hypothesis and other approaches
"""

import re
from collections import Counter
from pathlib import Path

# Glen Claston notation to EVA-like mapping (best guess based on patterns)
# Based on character frequency and position analysis
CLASTON_TO_EVA = {
    # High frequency characters likely to be vowels or common consonants
    'o': 'o',  # Most common (15.8%) - likely a vowel
    '9': 'y',  # Common at word end (37.8%) - likely suffix marker
    'a': 'a',  # High freq (9.1%) - likely a vowel  
    'c': 'ch', # High freq (8.7%) - could be ch sound
    '1': 'k',  # Common at start (15.7%) - likely consonant
    'e': 'e',  # Vowel-like frequency
    '8': 'd',  # Common in patterns
    'h': 'h',  # Aspirated consonant
    'y': 'i',  # Vowel
    'k': 'k',  # Consonant
    '4': 'q',  # Often word-initial 
    'm': 'm',  # Likely nasal consonant
    '2': 'sh', # Could be sh sound
    'C': 'ch', # Variant of c
    '7': 'l',  # Based on position patterns
    's': 's',  # Sibilant
    'n': 'n',  # Nasal
    'p': 'p',  # Stop consonant
    'K': 'k',  # Variant
    'g': 'g',  # Voiced stop
}

# Potential Pahlavi-inspired mapping (experimental)
# Based on the hypothesis that Voynich chars are inverted Pahlavi
PAHLAVI_MAP = {
    # These are speculative based on the arxiv paper description
    # Pahlavi is Middle Persian - vowels are often omitted
    'o': 'a',   # Could map to aleph-like vowel marker
    '9': 'n/d', # Final marker - in Pahlavi often final letters  
    'a': 'ā',   # Long a vowel
    'c': 'š',   # sh sound
    '1': 'y',   # yod - common in Pahlavi
    '8': 'd',   # daleth
    'h': 'h',   # he
    '4': 'p',   # pe
    'm': 'm',   # mem
}

def load_text():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    lines = []
    for line in text.split('\n'):
        clean = re.sub(r'<[^>]+>', '', line)
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            lines.append(clean.strip())
    return '\n'.join(lines)

def get_words(text):
    words = re.split(r'[.,\s]+', text)
    return [w for w in words if w and len(w) > 0]

def analyze_word_structure(words):
    """Analyze word structure to identify prefixes, stems, suffixes"""
    
    # Find common prefixes (first 1-2 chars)
    prefixes = Counter()
    for w in words:
        if len(w) >= 2:
            prefixes[w[:1]] += 1
            prefixes[w[:2]] += 1
    
    # Find common suffixes (last 1-2 chars)
    suffixes = Counter()
    for w in words:
        if len(w) >= 2:
            suffixes[w[-1:]] += 1
            suffixes[w[-2:]] += 1
    
    return prefixes, suffixes

def identify_root_patterns(words):
    """Try to identify root/stem patterns by removing common affixes"""
    
    # Most common endings
    common_endings = ['9', '89', 'am', 'oe', 'ay', 'c9', 'ae', 'oy', '79', 'an']
    
    roots = Counter()
    for w in words:
        root = w
        # Strip endings
        for ending in sorted(common_endings, key=len, reverse=True):
            if root.endswith(ending) and len(root) > len(ending) + 1:
                root = root[:-len(ending)]
                break
        if len(root) >= 2:
            roots[root] += 1
    
    return roots

def try_substitution(text, mapping):
    """Apply a simple substitution cipher"""
    result = []
    for char in text:
        if char in mapping:
            result.append(mapping[char])
        else:
            result.append(char)
    return ''.join(result)

def analyze_patterns():
    """Deep pattern analysis for decipherment clues"""
    text = load_text()
    words = get_words(text)
    
    print("=" * 60)
    print("🔮 VOYNICH DECIPHERMENT ANALYSIS 🔮")
    print("=" * 60)
    
    # Word structure analysis
    prefixes, suffixes = analyze_word_structure(words)
    
    print("\n📊 TOP 10 WORD BEGINNINGS (likely prefixes/articles):")
    for pref, count in prefixes.most_common(10):
        pct = count / len(words) * 100
        print(f"  '{pref}': {count} ({pct:.1f}%)")
    
    print("\n📊 TOP 10 WORD ENDINGS (likely suffixes/case markers):")
    for suff, count in suffixes.most_common(10):
        pct = count / len(words) * 100
        print(f"  '{suff}': {count} ({pct:.1f}%)")
    
    # Root analysis
    roots = identify_root_patterns(words)
    print("\n📊 TOP 20 POTENTIAL ROOT WORDS:")
    for root, count in roots.most_common(20):
        print(f"  '{root}': {count}")
    
    # Look for repeated phrases
    print("\n📊 LOOKING FOR REPEATED STRUCTURES...")
    
    # Tri-grams
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
    trigram_counts = Counter(trigrams)
    print("\n  Top 10 word trigrams:")
    for trig, count in trigram_counts.most_common(10):
        if count > 5:
            print(f"    '{trig}': {count}")
    
    # Self-citation patterns (words that appear near themselves)
    print("\n📊 CHECKING FOR SELF-CITATION (words appearing near themselves):")
    from collections import defaultdict
    near_self = defaultdict(int)
    for i, w in enumerate(words[:-5]):
        window = words[i+1:i+6]
        if w in window:
            near_self[w] += 1
    
    print("  Words that repeat within 5-word window:")
    for word, count in sorted(near_self.items(), key=lambda x: -x[1])[:10]:
        print(f"    '{word}': {count} self-citations")

def attempt_translation():
    """Attempt basic translation using hypothetical mappings"""
    text = load_text()
    words = get_words(text)
    
    print("\n" + "=" * 60)
    print("🔮 TRANSLATION ATTEMPT (EXPERIMENTAL) 🔮")  
    print("=" * 60)
    
    # Get some sample words/phrases
    sample_words = words[:50]
    
    print("\n📝 FIRST 50 WORDS (original):")
    print(' '.join(sample_words))
    
    # Apply experimental EVA-like mapping
    print("\n📝 WITH EVA-LIKE MAPPING:")
    mapped = [try_substitution(w, CLASTON_TO_EVA) for w in sample_words]
    print(' '.join(mapped))
    
    # Look for potential Latin/Romance cognates
    print("\n📊 LOOKING FOR POTENTIAL COGNATES...")
    
    # Common short Voynich words that might be function words
    common_short = [w for w, c in Counter(words).most_common(100) if len(w) <= 3]
    print(f"\n  Most common short words (likely articles/prepositions):")
    for w in common_short[:15]:
        count = words.count(w)
        print(f"    '{w}': {count}")
    
    # Words with '4o' prefix (very common) might be articles
    words_4o = [w for w in words if w.startswith('4o')]
    print(f"\n  Words starting with '4o' (possible article pattern): {len(words_4o)} words")
    print(f"    Examples: {list(set(words_4o))[:10]}")
    
    # Words ending in 'am' might be accusative/dative
    words_am = [w for w in words if w.endswith('am')]
    print(f"\n  Words ending in 'am' (possible case ending): {len(words_am)} words")
    print(f"    Examples: {list(set(words_am))[:10]}")
    
    # Words ending in '89' 
    words_89 = [w for w in words if w.endswith('89')]
    print(f"\n  Words ending in '89' (most common ending): {len(words_89)} words")
    print(f"    Examples: {list(set(words_89))[:10]}")

def main():
    analyze_patterns()
    attempt_translation()
    
    print("\n" + "=" * 60)
    print("🔬 PRELIMINARY CONCLUSIONS:")
    print("=" * 60)
    print("""
Based on the analysis:

1. The text has VERY structured word-formation rules:
   - Limited set of beginnings (o, 1, 4, 8 dominate)
   - Limited set of endings (9, 89, am, oe, ay dominate)
   - This is NOT random - it's highly systematic

2. The '9' character (~38% of word endings) could be:
   - A grammatical suffix (like definite article suffix)
   - A case marker (nominative/absolutive)
   - Or part of the encoding system itself

3. The '4o' prefix pattern is very common:
   - Could be an article (like 'the')
   - Or a preposition (like 'to', 'of')
   - Or indicates a word class (nouns?)

4. Self-citation patterns suggest:
   - Possible lists or repeated structures
   - Or a writing style that uses echoing

5. HYPOTHESIS for next step:
   - '9' = grammatical ending (ignore for root identification)
   - '4o' = article/determiner
   - 'am/oe/ay' = case/tense markers
   - Core roots are 2-3 characters

Next: Try frequency-based substitution cipher with Latin/Italian
""")

if __name__ == '__main__':
    main()





