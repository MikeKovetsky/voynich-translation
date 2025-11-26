#!/usr/bin/env python3
"""
Track 20: Phrase Pattern Analysis
Move beyond word-by-word decoding to identify multi-word Latin phrases.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from difflib import SequenceMatcher

PHONETIC_MAP = {
    'o': 'a', 'h': 'r', '9': 's', 'k': 'n', 'c': 'c', '7': 'l', 'm': 'm',
    'a': 'e', 'e': 'i', '8': 'd', '1': 't', '4': 'qu', 'y': 'i', '2': 'b',
    'C': 'ch', 's': 'x', 'n': 'n', 'p': 'p', 'g': 'g', 'H': 'rr', 'K': 'nn',
    'A': 'ae', 'N': 'an', 'M': 'am', 'Z': 'as', 'Y': 'ai', 'u': 'u', 'w': 'w',
    'W': 'uu', 'U': 'uu', 'i': 'i', 'I': 'ii', 'j': 'j', 'J': 'j', 'F': 'f',
    'G': 'g', 'L': 'll', 'f': 'f', 'd': 'd', 'x': 'x', 'z': 'z', 'v': 'v',
}

LATIN_INVERSE = {
    'a': 'o', 'r': 'h', 's': '9', 'n': 'k', 'c': 'c', 'l': '7', 'm': 'm',
    'e': 'a', 'i': 'e/y', 'd': '8', 't': '1', 'qu': '4', 'b': '2', 'u': 'u',
    'o': 'o', 'x': 's', 'p': 'p', 'g': 'g', 'f': 'f', 'v': 'v', 'h': 'h',
}

TARGET_PHRASES = {
    'preparation_phrases': [
        ('in aqua', 'in water'),
        ('cum vino', 'with wine'),
        ('cum melle', 'with honey'),
        ('cum aceto', 'with vinegar'),
        ('in vino', 'in wine'),
    ],
    'use_phrases': [
        ('contra dolorem', 'against pain'),
        ('ad stomachum', 'for stomach'),
        ('ad oculos', 'for eyes'),
        ('pro febribus', 'for fevers'),
        ('contra venenum', 'against poison'),
    ],
    'action_phrases': [
        ('valet contra', 'is good against'),
        ('prodest ad', 'helps for'),
        ('curat', 'cures'),
    ],
    'description_phrases': [
        ('folia habet', 'has leaves'),
        ('radix est', 'the root is'),
        ('flos est', 'the flower is'),
    ],
}


def decode_word(word):
    result = []
    i = 0
    while i < len(word):
        char = word[i]
        if char in PHONETIC_MAP:
            result.append(PHONETIC_MAP[char])
        else:
            result.append(char)
        i += 1
    return ''.join(result)


def latin_to_voynich(latin_word):
    """Predict Voynich form from Latin word."""
    predictions = []
    latin_word = latin_word.lower()
    
    mapping = {
        'a': ['o'], 'b': ['2'], 'c': ['c'], 'd': ['8'],
        'e': ['a', 'e'], 'f': ['f', 'F'], 'g': ['g'],
        'h': [], 'i': ['e', 'y'], 'k': ['c'],
        'l': ['7'], 'm': ['m', 'M'], 'n': ['k', 'K'],
        'o': ['o'], 'p': ['p'], 'qu': ['4'],
        'r': ['h'], 's': ['9'], 't': ['1'],
        'u': ['u', 'o'], 'v': ['v'], 'x': ['s'],
    }
    
    result = []
    i = 0
    while i < len(latin_word):
        if i < len(latin_word) - 1 and latin_word[i:i+2] == 'qu':
            result.append('4')
            i += 2
        elif latin_word[i] in mapping:
            options = mapping[latin_word[i]]
            result.append(options[0] if options else '')
            i += 1
        else:
            i += 1
    
    return ''.join(result)


def predict_phrase_voynich(phrase):
    """Predict possible Voynich bigram for a Latin phrase."""
    words = phrase.lower().split()
    voynich_words = [latin_to_voynich(w) for w in words]
    return ' '.join(voynich_words)


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def load_text():
    """Load and parse Voynich transcription."""
    text_file = Path('voynich_raw.txt')
    lines = []
    pages = defaultdict(list)
    
    with open(text_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'<([^>]+)>(.+)', line)
            if match:
                page_id = match.group(1).split('.')[0]
                text = match.group(2)
                text = re.sub(r'[.=\-,]', ' ', text)
                text = re.sub(r'[;:!?*#@$%^&(){}[\]<>|/\\`~"\'+]', '', text)
                words = text.split()
                clean_words = []
                for w in words:
                    clean = re.sub(r'[^a-zA-Z0-9]', '', w)
                    if clean and len(clean) >= 1:
                        clean_words.append(clean)
                if clean_words:
                    lines.append((page_id, clean_words))
                    pages[page_id].extend(clean_words)
    
    return lines, pages


def extract_ngrams(lines, n):
    """Extract n-grams with page locations."""
    ngrams = Counter()
    ngram_pages = defaultdict(set)
    
    for page_id, words in lines:
        for i in range(len(words) - n + 1):
            ngram = tuple(words[i:i+n])
            ngrams[ngram] += 1
            ngram_pages[ngram].add(page_id)
    
    return ngrams, ngram_pages


def analyze_de_patterns(lines, bigrams):
    """Find and analyze '8am' (de) patterns."""
    de_variants = ['8am', '8aM', '8an', '8ay', '8ae', '8a', '8aN']
    
    de_sequences = []
    de_nouns = Counter()
    
    for bigram, count in bigrams.most_common(2000):
        if len(bigram) != 2:
            continue
        first, second = bigram
        is_de = False
        for v in de_variants:
            if first == v:
                is_de = True
                break
        if is_de:
            decoded_second = decode_word(second)
            de_sequences.append({
                'voynich': f"{first} {second}",
                'decoded': f"de {decoded_second}",
                'x_decoded': decoded_second,
                'count': count,
            })
            de_nouns[second] += count
    
    for page_id, words in lines:
        for i, word in enumerate(words):
            if word in de_variants and i < len(words) - 1:
                next_word = words[i+1]
                de_nouns[next_word] += 1
    
    return de_sequences, de_nouns.most_common(30)


def analyze_aqua_patterns(lines, bigrams, all_words):
    """Find and analyze 'o4o' (aqua) and '4oh' (herb) patterns."""
    aqua_exact = ['o4o']
    herb_prefixes = ['4oh', '4ok', '4o']
    
    aqua_before = Counter()
    aqua_after = Counter()
    aqua_contexts = []
    herb_contexts = []
    
    for page_id, words in lines:
        for i, word in enumerate(words):
            if word in aqua_exact:
                if i > 0:
                    aqua_before[words[i-1]] += 1
                if i < len(words) - 1:
                    aqua_after[words[i+1]] += 1
                context = {
                    'word': word,
                    'page': page_id,
                    'decoded': decode_word(word),
                    'before': words[i-1] if i > 0 else None,
                    'after': words[i+1] if i < len(words) - 1 else None,
                }
                aqua_contexts.append(context)
            
            for prefix in herb_prefixes:
                if word.startswith(prefix):
                    herb_contexts.append({
                        'word': word,
                        'page': page_id,
                        'decoded': decode_word(word),
                        'prefix': prefix,
                    })
                    break
    
    for bigram, count in bigrams.most_common(3000):
        first, second = bigram
        if first in aqua_exact or second in aqua_exact:
            decoded = f"{decode_word(first)} {decode_word(second)}"
            aqua_contexts.append({
                'voynich': f"{first} {second}",
                'decoded': decoded,
                'count': count,
                'type': 'bigram',
            })
        for prefix in herb_prefixes:
            if first.startswith(prefix) or second.startswith(prefix):
                decoded = f"{decode_word(first)} {decode_word(second)}"
                herb_contexts.append({
                    'voynich': f"{first} {second}",
                    'decoded': decoded,
                    'count': count,
                    'type': 'bigram',
                })
                break
    
    unique_aqua = {}
    for ctx in aqua_contexts:
        key = ctx.get('voynich') or f"{ctx.get('word')}_{ctx.get('page')}"
        if key not in unique_aqua:
            unique_aqua[key] = ctx
    
    unique_herb = {}
    for ctx in herb_contexts:
        key = ctx.get('voynich') or f"{ctx.get('word')}_{ctx.get('page')}"
        if key not in unique_herb:
            unique_herb[key] = ctx
    
    return list(unique_aqua.values()), list(unique_herb.values())[:100], aqua_before.most_common(20), aqua_after.most_common(20)


def search_phrase_matches(bigrams, trigrams, target_phrases):
    """Search for matches to target Latin phrases."""
    results = {}
    
    for category, phrases in target_phrases.items():
        category_results = []
        
        for latin_phrase, meaning in phrases:
            predicted = predict_phrase_voynich(latin_phrase)
            latin_words = latin_phrase.split()
            
            matches_found = []
            
            if len(latin_words) == 2:
                for bigram, count in bigrams.most_common(500):
                    decoded = f"{decode_word(bigram[0])} {decode_word(bigram[1])}"
                    score = similarity(decoded, latin_phrase)
                    if score >= 0.4:
                        matches_found.append({
                            'voynich': f"{bigram[0]} {bigram[1]}",
                            'decoded': decoded,
                            'count': count,
                            'confidence': round(score, 3),
                        })
            elif len(latin_words) == 1:
                for bigram, count in bigrams.most_common(300):
                    for word in bigram:
                        decoded = decode_word(word)
                        score = similarity(decoded, latin_phrase)
                        if score >= 0.5:
                            matches_found.append({
                                'voynich': word,
                                'decoded': decoded,
                                'count': count,
                                'confidence': round(score, 3),
                            })
            
            matches_found = sorted(matches_found, key=lambda x: (-x['confidence'], -x['count']))[:10]
            
            best_match = matches_found[0] if matches_found else None
            overall_conf = best_match['confidence'] if best_match else 0
            
            category_results.append({
                'latin': latin_phrase,
                'meaning': meaning,
                'predicted_voynich': [predicted],
                'matches_found': matches_found,
                'best_match': best_match['voynich'] if best_match else None,
                'overall_confidence': round(overall_conf, 3),
            })
        
        results[category] = category_results
    
    return results


def find_in_prefix_patterns(bigrams, all_words):
    """Find patterns with 'in' (yk or ek) prefix."""
    in_variants = ['yk', 'ek', 'ak', 'ok']
    patterns = []
    
    for bigram, count in bigrams.most_common(500):
        first, second = bigram
        if first in in_variants or (len(first) <= 3 and first.endswith('k')):
            decoded = f"{decode_word(first)} {decode_word(second)}"
            patterns.append({
                'voynich': f"{first} {second}",
                'decoded': decoded,
                'count': count,
                'possible_meaning': f"in {decode_word(second)}",
            })
    
    return patterns[:30]


def find_ad_prefix_patterns(bigrams):
    """Find patterns with 'ad' (o8) prefix."""
    ad_variants = ['o8', 'o8a', 'o8e', 'a8']
    patterns = []
    
    for bigram, count in bigrams.most_common(500):
        first, second = bigram
        if first in ad_variants or first.startswith('o8'):
            decoded = f"{decode_word(first)} {decode_word(second)}"
            patterns.append({
                'voynich': f"{first} {second}",
                'decoded': decoded,
                'count': count,
                'possible_meaning': f"ad/to {decode_word(second)}",
            })
    
    return patterns[:30]


def find_article_noun_patterns(bigrams):
    """Find '4oh-' article + noun patterns."""
    patterns = []
    article_prefixes = ['4oh', '4ok', '4o']
    
    for bigram, count in bigrams.most_common(3000):
        first, second = bigram
        for prefix in article_prefixes:
            if first.startswith(prefix):
                decoded = f"{decode_word(first)} {decode_word(second)}"
                patterns.append({
                    'voynich': f"{first} {second}",
                    'decoded': decoded,
                    'count': count,
                    'structure': 'ARTICLE + NOUN',
                    'article_form': first,
                    'noun': second,
                })
                break
    
    return sorted(patterns, key=lambda x: -x['count'])[:50]


def main():
    print("=" * 70)
    print("TRACK 20: PHRASE PATTERN ANALYSIS")
    print("=" * 70)
    
    print("\n📖 Loading Voynich transcription...")
    lines, pages = load_text()
    
    all_words = []
    for _, words in lines:
        all_words.extend(words)
    
    print(f"   Total words: {len(all_words)}")
    print(f"   Total pages: {len(pages)}")
    
    print("\n📊 Extracting n-grams...")
    bigrams, bigram_pages = extract_ngrams(lines, 2)
    trigrams, trigram_pages = extract_ngrams(lines, 3)
    
    print(f"   Unique bigrams: {len(bigrams)}")
    print(f"   Unique trigrams: {len(trigrams)}")
    
    print("\n🔍 Task 1: Predicting Voynich phrase forms...")
    for category, phrases in TARGET_PHRASES.items():
        print(f"\n   {category}:")
        for latin, meaning in phrases:
            predicted = predict_phrase_voynich(latin)
            print(f"      {latin} ({meaning}) → {predicted}")
    
    print("\n🔍 Task 2: Searching for phrase matches...")
    phrase_matches = search_phrase_matches(bigrams, trigrams, TARGET_PHRASES)
    
    confirmed_phrases = 0
    high_conf_phrases = 0
    for category, results in phrase_matches.items():
        print(f"\n   {category}:")
        for result in results:
            status = "❌"
            if result['overall_confidence'] >= 0.6:
                status = "✅"
                confirmed_phrases += 1
                high_conf_phrases += 1
            elif result['overall_confidence'] >= 0.45:
                status = "🔶"
                confirmed_phrases += 1
            print(f"      {status} {result['latin']}: {result['overall_confidence']:.1%}")
            if result['best_match']:
                print(f"         → {result['best_match']} = {result['matches_found'][0]['decoded']}")
    
    print("\n🔍 Task 4: Analyzing '8am' (de) patterns...")
    de_sequences, de_nouns = analyze_de_patterns(lines, bigrams)
    print(f"   Found {len(de_sequences)} 'de + X' sequences")
    print(f"   Most common nouns after 'de':")
    for noun, count in de_nouns[:10]:
        print(f"      {noun} ({decode_word(noun)}): {count}x")
    
    print("\n🔍 Task 5: Analyzing 'o4o' (aqua) and '4oh-' (herb) patterns...")
    aqua_contexts, herb_contexts, aqua_before, aqua_after = analyze_aqua_patterns(lines, bigrams, all_words)
    print(f"   Found {len(aqua_contexts)} aqua-related contexts")
    print(f"   Found {len(herb_contexts)} herb-related contexts (4oh-/4ok-/4o- prefixes)")
    
    in_patterns = find_in_prefix_patterns(bigrams, all_words)
    print(f"\n🔍 'in + X' patterns found: {len(in_patterns)}")
    for p in in_patterns[:5]:
        print(f"      {p['voynich']} → {p['decoded']} ({p['count']}x)")
    
    ad_patterns = find_ad_prefix_patterns(bigrams)
    print(f"\n🔍 'ad + X' patterns found: {len(ad_patterns)}")
    for p in ad_patterns[:5]:
        print(f"      {p['voynich']} → {p['decoded']} ({p['count']}x)")
    
    article_patterns = find_article_noun_patterns(bigrams)
    print(f"\n🔍 'ARTICLE + NOUN' patterns: {len(article_patterns)}")
    for p in article_patterns[:5]:
        print(f"      {p['voynich']} → {p['decoded']} ({p['count']}x)")
    
    top_bigrams = []
    for bigram, count in bigrams.most_common(50):
        decoded = f"{decode_word(bigram[0])} {decode_word(bigram[1])}"
        latin_match = None
        for category, phrases in TARGET_PHRASES.items():
            for latin, _ in phrases:
                if similarity(decoded, latin) >= 0.4:
                    latin_match = latin
                    break
        top_bigrams.append({
            'voynich': f"{bigram[0]} {bigram[1]}",
            'decoded': decoded,
            'count': count,
            'latin_match': latin_match,
            'pages': list(bigram_pages[bigram])[:5],
        })
    
    top_trigrams = []
    for trigram, count in trigrams.most_common(30):
        decoded = f"{decode_word(trigram[0])} {decode_word(trigram[1])} {decode_word(trigram[2])}"
        top_trigrams.append({
            'voynich': f"{trigram[0]} {trigram[1]} {trigram[2]}",
            'decoded': decoded,
            'count': count,
            'pages': list(trigram_pages[trigram])[:5],
        })
    
    results = {
        'preparation_phrases': phrase_matches.get('preparation_phrases', []),
        'use_phrases': phrase_matches.get('use_phrases', []),
        'action_phrases': phrase_matches.get('action_phrases', []),
        'description_phrases': phrase_matches.get('description_phrases', []),
        'de_patterns': {
            'sequences_found': de_sequences[:50],
            'most_common_nouns_after_de': [
                {'noun': n, 'decoded': decode_word(n), 'count': c} 
                for n, c in de_nouns
            ],
        },
        'aqua_patterns': {
            'sequences_with_aqua': aqua_contexts[:30],
            'words_before_aqua': [
                {'word': w, 'decoded': decode_word(w), 'count': c}
                for w, c in aqua_before
            ],
            'words_after_aqua': [
                {'word': w, 'decoded': decode_word(w), 'count': c}
                for w, c in aqua_after
            ],
        },
        'herb_patterns': herb_contexts[:50],
        'in_patterns': in_patterns,
        'ad_patterns': ad_patterns,
        'article_noun_patterns': article_patterns[:30],
        'top_bigrams': top_bigrams,
        'top_trigrams': top_trigrams,
        'summary': {
            'total_bigrams': len(bigrams),
            'total_trigrams': len(trigrams),
            'phrases_confirmed': confirmed_phrases,
            'high_confidence': high_conf_phrases,
            'de_patterns_found': len(de_sequences),
            'aqua_contexts_found': len(aqua_contexts),
            'herb_patterns_found': len(herb_contexts),
            'in_patterns_found': len(in_patterns),
            'ad_patterns_found': len(ad_patterns),
            'article_noun_patterns_found': len(article_patterns),
        },
    }
    
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    with open(results_dir / 'phrase_patterns.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n📊 Total bigrams analyzed: {len(bigrams)}")
    print(f"📊 Total trigrams analyzed: {len(trigrams)}")
    print(f"✅ Phrases confirmed (≥45% conf): {confirmed_phrases}")
    print(f"🔥 High confidence (≥60%): {high_conf_phrases}")
    print(f"📋 'de + X' patterns: {len(de_sequences)}")
    print(f"💧 'aqua' contexts: {len(aqua_contexts)}")
    print(f"🌿 'herb' patterns (4oh-/4ok-): {len(herb_contexts)}")
    print(f"📍 'ARTICLE + NOUN' patterns: {len(article_patterns)}")
    
    generate_report(results)
    
    print(f"\n📁 Results saved to results/phrase_patterns.json")
    print(f"📁 Report saved to results/phrase_patterns_report.md")
    
    return results


def generate_report(results):
    """Generate markdown report."""
    report = []
    report.append("# Track 20: Phrase Pattern Analysis Report\n")
    report.append("## Summary\n")
    
    summary = results['summary']
    report.append(f"- **Total bigrams analyzed:** {summary['total_bigrams']}")
    report.append(f"- **Total trigrams analyzed:** {summary['total_trigrams']}")
    report.append(f"- **Phrases confirmed (≥45%):** {summary['phrases_confirmed']}")
    report.append(f"- **High confidence (≥60%):** {summary['high_confidence']}")
    report.append(f"- **'de + X' patterns found:** {summary['de_patterns_found']}")
    report.append(f"- **'aqua' contexts found:** {summary['aqua_contexts_found']}")
    report.append(f"- **'herb' patterns found (4oh-/4ok-):** {summary.get('herb_patterns_found', 0)}")
    report.append(f"- **ARTICLE + NOUN patterns:** {summary.get('article_noun_patterns_found', 0)}")
    report.append("")
    
    report.append("## Latin Phrase Matches\n")
    
    for category in ['preparation_phrases', 'use_phrases', 'action_phrases', 'description_phrases']:
        phrases = results.get(category, [])
        report.append(f"### {category.replace('_', ' ').title()}\n")
        report.append("| Latin | Meaning | Best Match | Decoded | Confidence |")
        report.append("|-------|---------|------------|---------|------------|")
        
        for p in phrases:
            best = p['best_match'] or '-'
            decoded = p['matches_found'][0]['decoded'] if p['matches_found'] else '-'
            conf = f"{p['overall_confidence']:.1%}"
            report.append(f"| {p['latin']} | {p['meaning']} | {best} | {decoded} | {conf} |")
        report.append("")
    
    report.append("## 'de' (8am) Patterns\n")
    report.append("### Most Common Nouns After 'de'\n")
    report.append("| Voynich | Decoded | Count |")
    report.append("|---------|---------|-------|")
    for item in results['de_patterns']['most_common_nouns_after_de'][:15]:
        report.append(f"| {item['noun']} | {item['decoded']} | {item['count']} |")
    report.append("")
    
    report.append("## Top 20 Bigrams\n")
    report.append("| Voynich | Decoded | Count | Latin Match |")
    report.append("|---------|---------|-------|-------------|")
    for b in results['top_bigrams'][:20]:
        latin = b['latin_match'] or '-'
        report.append(f"| {b['voynich']} | {b['decoded']} | {b['count']} | {latin} |")
    report.append("")
    
    report.append("## Top 15 Trigrams\n")
    report.append("| Voynich | Decoded | Count |")
    report.append("|---------|---------|-------|")
    for t in results['top_trigrams'][:15]:
        report.append(f"| {t['voynich']} | {t['decoded']} | {t['count']} |")
    report.append("")
    
    report.append("## Article + Noun Patterns (4oh- prefix)\n")
    report.append("| Voynich | Decoded | Count |")
    report.append("|---------|---------|-------|")
    for p in results.get('article_noun_patterns', [])[:15]:
        report.append(f"| {p['voynich']} | {p['decoded']} | {p['count']} |")
    report.append("")
    
    report.append("## Herb Patterns (4oh-/4ok-/4o- words)\n")
    report.append("| Voynich | Decoded | Count | Type |")
    report.append("|---------|---------|-------|------|")
    for p in results.get('herb_patterns', [])[:20]:
        voy = p.get('voynich') or p.get('word', '-')
        dec = p.get('decoded', '-')
        cnt = p.get('count', '-')
        ptype = p.get('type', 'word')
        report.append(f"| {voy} | {dec} | {cnt} | {ptype} |")
    report.append("")
    
    with open('results/phrase_patterns_report.md', 'w') as f:
        f.write('\n'.join(report))


if __name__ == '__main__':
    main()



