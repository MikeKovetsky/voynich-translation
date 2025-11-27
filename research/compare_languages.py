#!/usr/bin/env python3
"""
Compare Voynich text patterns with known languages
"""

import re
from collections import Counter
from pathlib import Path
import math

# Known language characteristics (character frequencies normalized)
# These are rough approximations for comparison
LANGUAGE_PROFILES = {
    'Latin': {
        'top_chars': ['e', 'i', 'u', 'a', 't', 's', 'n', 'r', 'o', 'm'],
        'avg_word_len': 5.5,
        'vowel_ratio': 0.48,
        'common_endings': ['us', 'um', 'is', 'am', 'em'],
    },
    'Italian': {
        'top_chars': ['e', 'a', 'i', 'o', 'n', 'r', 'l', 't', 's', 'c'],
        'avg_word_len': 4.5,
        'vowel_ratio': 0.48,
        'common_endings': ['re', 'to', 'te', 'no', 'ne'],
    },
    'German': {
        'top_chars': ['e', 'n', 'i', 'r', 's', 't', 'a', 'd', 'h', 'u'],
        'avg_word_len': 5.5,
        'vowel_ratio': 0.40,
        'common_endings': ['en', 'er', 'ch', 'nd', 'ng'],
    },
    'Hebrew': {
        'top_chars': ['י', 'ו', 'ה', 'א', 'מ', 'ל', 'ב', 'ת', 'נ', 'ש'],
        'avg_word_len': 4.0,
        'vowel_ratio': 0.0,  # No written vowels
        'common_endings': [],
    },
    'Arabic': {
        'top_chars': ['ا', 'ل', 'ي', 'م', 'و', 'ن', 'ه', 'ب', 'ر', 'ع'],
        'avg_word_len': 4.5,
        'vowel_ratio': 0.20,
        'common_endings': [],
    },
    'Turkish': {
        'top_chars': ['a', 'e', 'i', 'n', 'r', 'l', 'ı', 'd', 'k', 'y'],
        'avg_word_len': 6.0,  # Agglutinative!
        'vowel_ratio': 0.45,
        'common_endings': ['lar', 'ler', 'dan', 'den'],
    },
    'Greek': {
        'top_chars': ['α', 'ο', 'ε', 'ι', 'ν', 'τ', 'σ', 'η', 'ρ', 'κ'],
        'avg_word_len': 5.0,
        'vowel_ratio': 0.45,
        'common_endings': ['ος', 'ον', 'ου', 'ων'],
    },
}

def load_voynich():
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

def get_chars(text):
    chars = re.sub(r'[.,\s\n]', '', text)
    return list(chars)

def entropy(data):
    """Calculate Shannon entropy"""
    counter = Counter(data)
    total = sum(counter.values())
    probs = [count/total for count in counter.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def conditional_entropy(bigrams, unigrams):
    """Calculate conditional entropy H(X|Y)"""
    bigram_counts = Counter(bigrams)
    unigram_counts = Counter(unigrams)
    
    total_bigrams = sum(bigram_counts.values())
    h = 0
    for bigram, count in bigram_counts.items():
        p_xy = count / total_bigrams
        p_y = unigram_counts[bigram[0]] / len(unigrams)
        p_x_given_y = p_xy / p_y if p_y > 0 else 0
        if p_x_given_y > 0:
            h -= p_xy * math.log2(p_x_given_y)
    return h

def analyze_voynich():
    text = load_voynich()
    words = get_words(text)
    chars = get_chars(text)
    
    # Basic stats
    char_counter = Counter(chars)
    word_counter = Counter(words)
    
    # Entropy
    char_entropy = entropy(chars)
    word_entropy = entropy(words)
    
    # Bigrams
    bigrams = [''.join(chars[i:i+2]) for i in range(len(chars)-1)]
    bigram_entropy = entropy(bigrams)
    cond_entropy = conditional_entropy(bigrams, chars)
    
    # Word length
    avg_word_len = sum(len(w) for w in words) / len(words)
    
    # First/last char analysis
    first_chars = Counter([w[0] for w in words])
    last_chars = Counter([w[-1] for w in words])
    
    # Most common ending patterns
    endings = Counter([w[-2:] for w in words if len(w) >= 2])
    
    return {
        'char_entropy': char_entropy,
        'word_entropy': word_entropy,
        'bigram_entropy': bigram_entropy,
        'cond_entropy': cond_entropy,
        'avg_word_len': avg_word_len,
        'top_chars': [c for c, _ in char_counter.most_common(10)],
        'top_endings': endings.most_common(10),
        'first_char_concentration': first_chars.most_common(1)[0][1] / len(words),
        'last_char_concentration': last_chars.most_common(1)[0][1] / len(words),
    }

def main():
    print("=" * 60)
    print("🔮 VOYNICH LANGUAGE COMPARISON ANALYSIS 🔮")
    print("=" * 60)
    
    stats = analyze_voynich()
    
    print("\n📊 VOYNICH MANUSCRIPT STATISTICS:")
    print(f"  Character entropy: {stats['char_entropy']:.3f} bits")
    print(f"  Word entropy: {stats['word_entropy']:.3f} bits")
    print(f"  Bigram entropy: {stats['bigram_entropy']:.3f} bits")
    print(f"  Conditional entropy: {stats['cond_entropy']:.3f} bits")
    print(f"  Average word length: {stats['avg_word_len']:.2f}")
    print(f"  First char concentration: {stats['first_char_concentration']:.1%}")
    print(f"  Last char concentration: {stats['last_char_concentration']:.1%}")
    
    print("\n📊 COMPARISON WITH NATURAL LANGUAGES:")
    print("\n  Typical entropy values for natural languages:")
    print("    English: ~4.0-4.5 bits/char")
    print("    Latin: ~4.0-4.3 bits/char")
    print("    Hebrew: ~4.1-4.4 bits/char")
    print(f"    Voynich: {stats['char_entropy']:.2f} bits/char")
    
    # Entropy is within natural language range
    if 3.5 <= stats['char_entropy'] <= 5.0:
        print("    ✅ Entropy is consistent with natural language")
    else:
        print("    ⚠️ Entropy is unusual for natural language")
    
    print("\n  Conditional entropy (predictability):")
    print("    English: ~2.5-3.0 bits")
    print("    Random: equals character entropy")
    print(f"    Voynich: {stats['cond_entropy']:.2f} bits")
    
    reduction = (stats['char_entropy'] - stats['cond_entropy']) / stats['char_entropy']
    print(f"    Entropy reduction: {reduction:.1%}")
    if reduction > 0.2:
        print("    ✅ Shows character patterns (not random)")
    
    print("\n📊 MOST COMMON WORD ENDINGS:")
    for ending, count in stats['top_endings']:
        print(f"    '{ending}': {count}")
    
    print("\n📊 SPECIAL OBSERVATIONS:")
    print(f"  - Top first char covers {stats['first_char_concentration']:.1%} of words")
    print(f"  - Top last char covers {stats['last_char_concentration']:.1%} of words")
    print("  - For comparison: English ~8% for top first, ~15% for top last")
    
    if stats['last_char_concentration'] > 0.30:
        print("\n  🔥 ANOMALY: Extremely high last-character concentration!")
        print("     This suggests either:")
        print("     1. Heavy use of grammatical suffixes")
        print("     2. A self-consistent abbreviation system")
        print("     3. An agglutinative language structure")
        print("     4. A constructed encoding with positional rules")
    
    # Repetition analysis
    print("\n📊 REPETITION PATTERN ANALYSIS:")
    text = load_voynich()
    words = get_words(text)
    
    # Check for repeated sequences
    word_pairs = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    pair_counter = Counter(word_pairs)
    
    print("  Top 10 repeated word pairs:")
    for pair, count in pair_counter.most_common(10):
        print(f"    '{pair}': {count}")
    
    # Check for "echoing" (words that differ by just first/last char)
    print("\n  Checking for 'gallows' pattern (related word families):")
    word_families = {}
    for w in words:
        if len(w) >= 3:
            stem = w[1:-1]  # middle portion
            if stem not in word_families:
                word_families[stem] = set()
            word_families[stem].add(w)
    
    # Find stems with many variants
    large_families = [(stem, variants) for stem, variants in word_families.items() 
                      if len(variants) >= 5]
    large_families.sort(key=lambda x: len(x[1]), reverse=True)
    
    print("  Stems with 5+ variants (suggesting prefix/suffix patterns):")
    for stem, variants in large_families[:10]:
        print(f"    '{stem}' -> {sorted(variants)[:6]}...")

if __name__ == '__main__':
    main()





