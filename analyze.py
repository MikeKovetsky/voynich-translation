#!/usr/bin/env python3
"""
Voynich Manuscript Analysis
Statistical analysis of character and word frequencies
"""

import re
from collections import Counter
from pathlib import Path

def load_transcription(path):
    """Load and parse the transcription file"""
    text = Path(path).read_text(encoding='utf-8')
    
    # Parse lines, removing page/line markers
    lines = []
    for line in text.split('\n'):
        # Remove page markers like <1r.1>
        clean = re.sub(r'<[^>]+>', '', line)
        # Remove line ending markers
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            lines.append(clean.strip())
    
    return '\n'.join(lines)

def get_words(text):
    """Extract words from text"""
    # Split on dots, commas, and spaces
    words = re.split(r'[.,\s]+', text)
    return [w for w in words if w and len(w) > 0]

def get_chars(text):
    """Get all characters excluding punctuation"""
    chars = re.sub(r'[.,\s\n]', '', text)
    return list(chars)

def analyze_frequencies(items):
    """Analyze frequency distribution"""
    counter = Counter(items)
    total = sum(counter.values())
    return {
        'total': total,
        'unique': len(counter),
        'top_20': counter.most_common(20),
        'hapax': sum(1 for c, n in counter.items() if n == 1),  # words appearing once
    }

def zipf_analysis(counter):
    """Check if distribution follows Zipf's law"""
    sorted_freqs = sorted(counter.values(), reverse=True)
    if len(sorted_freqs) < 2:
        return None
    
    # Calculate Zipf coefficient (rank * frequency should be roughly constant)
    zipf_products = []
    for rank, freq in enumerate(sorted_freqs[:50], 1):
        zipf_products.append(rank * freq)
    
    avg = sum(zipf_products) / len(zipf_products)
    variance = sum((x - avg) ** 2 for x in zipf_products) / len(zipf_products)
    
    return {
        'zipf_products': zipf_products[:10],
        'avg': avg,
        'variance': variance,
        'cv': (variance ** 0.5) / avg  # coefficient of variation
    }

def main():
    print("=" * 60)
    print("🔮 VOYNICH MANUSCRIPT STATISTICAL ANALYSIS 🔮")
    print("=" * 60)
    
    text = load_transcription('voynich_raw.txt')
    
    # Word analysis
    words = get_words(text)
    word_stats = analyze_frequencies(words)
    word_counter = Counter(words)
    
    print("\n📊 WORD STATISTICS:")
    print(f"  Total words: {word_stats['total']}")
    print(f"  Unique words: {word_stats['unique']}")
    print(f"  Hapax legomena (words appearing once): {word_stats['hapax']}")
    print(f"  Type-token ratio: {word_stats['unique'] / word_stats['total']:.4f}")
    
    print("\n📈 TOP 20 MOST FREQUENT WORDS:")
    for i, (word, count) in enumerate(word_stats['top_20'], 1):
        pct = count / word_stats['total'] * 100
        print(f"  {i:2}. {word:15} - {count:5} ({pct:.2f}%)")
    
    # Character analysis
    chars = get_chars(text)
    char_stats = analyze_frequencies(chars)
    char_counter = Counter(chars)
    
    print("\n📊 CHARACTER STATISTICS:")
    print(f"  Total characters: {char_stats['total']}")
    print(f"  Unique characters: {char_stats['unique']}")
    
    print("\n📈 TOP 20 MOST FREQUENT CHARACTERS:")
    for i, (char, count) in enumerate(char_stats['top_20'], 1):
        pct = count / char_stats['total'] * 100
        print(f"  {i:2}. '{char}' - {count:5} ({pct:.2f}%)")
    
    # Zipf's law analysis
    print("\n📊 ZIPF'S LAW ANALYSIS (Natural Language Indicator):")
    zipf = zipf_analysis(word_counter)
    if zipf:
        print(f"  First 10 rank*freq products: {[round(x) for x in zipf['zipf_products']]}")
        print(f"  Average: {zipf['avg']:.1f}")
        print(f"  Coefficient of variation: {zipf['cv']:.3f}")
        print(f"  (Lower CV = more Zipf-like = more natural language-like)")
        if zipf['cv'] < 0.3:
            print("  ✅ Distribution is consistent with natural language!")
        else:
            print("  ⚠️ Distribution deviates from typical natural language")
    
    # Word length distribution
    print("\n📊 WORD LENGTH DISTRIBUTION:")
    lengths = [len(w) for w in words]
    length_counter = Counter(lengths)
    avg_len = sum(lengths) / len(lengths)
    print(f"  Average word length: {avg_len:.2f}")
    print("  Distribution:")
    for length in sorted(length_counter.keys())[:15]:
        count = length_counter[length]
        pct = count / len(lengths) * 100
        bar = '█' * int(pct)
        print(f"    {length:2} chars: {count:5} ({pct:5.1f}%) {bar}")
    
    # First/Last character analysis (important for Voynich!)
    print("\n📊 FIRST CHARACTER OF WORDS:")
    first_chars = Counter([w[0] for w in words if w])
    for char, count in first_chars.most_common(10):
        pct = count / len(words) * 100
        print(f"  '{char}': {count:5} ({pct:.2f}%)")
    
    print("\n📊 LAST CHARACTER OF WORDS:")
    last_chars = Counter([w[-1] for w in words if w])
    for char, count in last_chars.most_common(10):
        pct = count / len(words) * 100
        print(f"  '{char}': {count:5} ({pct:.2f}%)")
    
    # Bigram analysis
    print("\n📊 TOP 15 CHARACTER BIGRAMS:")
    bigrams = [''.join(chars[i:i+2]) for i in range(len(chars)-1)]
    bigram_counter = Counter(bigrams)
    for bigram, count in bigram_counter.most_common(15):
        pct = count / len(bigrams) * 100
        print(f"  '{bigram}': {count:5} ({pct:.2f}%)")
    
    return word_counter, char_counter

if __name__ == '__main__':
    main()

