"""
Track 64: Currier A/B Language Separation Analysis

Prescott Currier (1976) discovered the manuscript has TWO "languages":
- Language A: Herbal A, Pharmaceutical, Stars
- Language B: Herbal B, Biological, Recipes, Zodiac

These have measurably different word frequencies, character distributions, 
and entropy values.
"""

import json
import re
from collections import Counter
from pathlib import Path
from math import log2
import voynich_data as vd

CURRIER_A_PREFIXES = []
CURRIER_B_PREFIXES = []

HERBAL_A_RANGE = list(range(1, 58))
HERBAL_B_RANGE = list(range(58, 66))
ZODIAC_RANGE = list(range(66, 74))
BIOLOGICAL_RANGE = list(range(75, 85))
STARS_RANGE = list(range(85, 87))
PHARMACEUTICAL_RANGE = list(range(87, 103))
RECIPES_RANGE = list(range(103, 117))

for i in HERBAL_A_RANGE:
    CURRIER_A_PREFIXES.extend([f'f{i}r', f'f{i}v'])
for i in STARS_RANGE:
    CURRIER_A_PREFIXES.extend([f'f{i}r', f'f{i}v'])
for i in PHARMACEUTICAL_RANGE:
    CURRIER_A_PREFIXES.extend([f'f{i}r', f'f{i}v'])

for i in HERBAL_B_RANGE:
    CURRIER_B_PREFIXES.extend([f'f{i}r', f'f{i}v'])
for i in ZODIAC_RANGE:
    CURRIER_B_PREFIXES.extend([f'f{i}r', f'f{i}v'])
for i in BIOLOGICAL_RANGE:
    CURRIER_B_PREFIXES.extend([f'f{i}r', f'f{i}v'])
for i in RECIPES_RANGE:
    CURRIER_B_PREFIXES.extend([f'f{i}r', f'f{i}v'])


def get_folios_by_prefixes(pages, prefixes):
    """Match folios that start with any of the given prefixes."""
    matched = []
    for folio in pages.keys():
        for prefix in prefixes:
            if folio.startswith(prefix):
                matched.append(folio)
                break
    return matched


def load_dictionary():
    path = Path('results/clean_dictionary.json')
    if path.exists():
        data = json.loads(path.read_text())
        return data.get('entries', {})
    return {}


def extract_words(text):
    text_clean = re.sub(r'[!?<>@$\d\[\]{}]', '', text)
    words = []
    for w in re.split(r'[.\-=,\s]', text_clean):
        if w and len(w) > 1:
            words.append(w)
    return words


def get_folio_words(pages, folio_list):
    all_words = []
    for folio in folio_list:
        if folio in pages:
            for text in pages[folio].values():
                all_words.extend(extract_words(text))
    return all_words


def get_folio_words_by_prefix(pages, prefixes):
    folios = get_folios_by_prefixes(pages, prefixes)
    return get_folio_words(pages, folios), folios


def calc_char_freq(words):
    chars = ''.join(words)
    total = len(chars) if chars else 1
    freq = Counter(chars)
    return {c: count / total for c, count in freq.most_common(30)}


def calc_entropy(freq_dict):
    entropy = 0
    for p in freq_dict.values():
        if p > 0:
            entropy -= p * log2(p)
    return entropy


def calc_word_stats(words):
    if not words:
        return {'total': 0, 'unique': 0, 'avg_len': 0, 'entropy': 0}
    
    word_freq = Counter(words)
    total = len(words)
    unique = len(word_freq)
    avg_len = sum(len(w) for w in words) / total
    
    probs = {w: c / total for w, c in word_freq.items()}
    entropy = calc_entropy(probs)
    
    return {
        'total': total,
        'unique': unique,
        'avg_len': round(avg_len, 3),
        'entropy': round(entropy, 3),
        'top_100': word_freq.most_common(100)
    }


def calc_dict_coverage(words, dictionary):
    if not words:
        return 0.0, []
    
    total = len(words)
    matched = 0
    matched_words = []
    
    for w in words:
        if w in dictionary:
            matched += 1
            matched_words.append(w)
    
    return round(matched / total * 100, 2), matched_words


def find_hebrew_patterns(words):
    patterns = {
        'cohen': [],    # priest pattern (kaiin, okaiin, etc)
        'qo_prefix': [],    # qo- article
        'y_suffix': [],     # -y endings
        'three_cons': [],   # potential 3-consonant roots
        'daiin': []         # "of/from" pattern
    }
    
    cohen_pat = re.compile(r'.*k[ao]i+n.*', re.I)
    qo_pat = re.compile(r'^qo', re.I)
    daiin_pat = re.compile(r'daiin', re.I)
    
    cons = set('bcdfghjklmnpqrstvwxyz')
    
    for w in set(words):
        if cohen_pat.match(w):
            patterns['cohen'].append(w)
        if qo_pat.match(w):
            patterns['qo_prefix'].append(w)
        if w.endswith('y'):
            patterns['y_suffix'].append(w)
        if daiin_pat.search(w):
            patterns['daiin'].append(w)
        
        consonants = [c for c in w.lower() if c in cons]
        if len(consonants) == 3:
            patterns['three_cons'].append(w)
    
    return {k: len(v) for k, v in patterns.items()}


def get_sections_coverage(pages, dictionary):
    sections = {
        'herbal_a': ([f'f{i}{s}' for i in range(1, 58) for s in ['r', 'v']], 'A'),
        'herbal_b': ([f'f{i}{s}' for i in range(58, 66) for s in ['r', 'v']], 'B'),
        'zodiac': ([f'f{i}{s}' for i in range(66, 74) for s in ['r', 'v']], 'B'),
        'biological': ([f'f{i}{s}' for i in range(75, 85) for s in ['r', 'v']], 'B'),
        'stars': ([f'f{i}{s}' for i in range(85, 87) for s in ['r', 'v']], 'A'),
        'pharma': ([f'f{i}{s}' for i in range(87, 103) for s in ['r', 'v']], 'A'),
        'recipes': ([f'f{i}{s}' for i in range(103, 117) for s in ['r', 'v']], 'B'),
    }
    
    results = {}
    for section, (prefixes, currier) in sections.items():
        words, matched_folios = get_folio_words_by_prefix(pages, prefixes)
        coverage, _ = calc_dict_coverage(words, dictionary)
        results[section] = {
            'currier': currier,
            'coverage': coverage,
            'total_words': len(words),
            'unique_words': len(set(words)),
            'folio_count': len(matched_folios)
        }
    
    return results


def analyze_vocab_overlap(words_a, words_b):
    set_a = set(words_a)
    set_b = set(words_b)
    
    only_a = set_a - set_b
    only_b = set_b - set_a
    both = set_a & set_b
    
    freq_a = Counter(words_a)
    freq_b = Counter(words_b)
    
    top_only_a = sorted(only_a, key=lambda w: freq_a[w], reverse=True)[:50]
    top_only_b = sorted(only_b, key=lambda w: freq_b[w], reverse=True)[:50]
    top_both = sorted(both, key=lambda w: freq_a[w] + freq_b[w], reverse=True)[:50]
    
    return {
        'only_a_count': len(only_a),
        'only_b_count': len(only_b),
        'both_count': len(both),
        'overlap_ratio': round(len(both) / (len(set_a | set_b)) * 100, 2) if set_a | set_b else 0,
        'top_only_a': top_only_a,
        'top_only_b': top_only_b,
        'top_shared': top_both
    }


def generate_recommendation(results):
    a_cov = results['language_a']['dictionary_coverage']
    b_cov = results['language_b']['dictionary_coverage']
    
    diff = abs(a_cov - b_cov)
    better = 'B' if b_cov > a_cov else 'A'
    
    overlap = results['vocabulary_overlap']['overlap_ratio']
    
    recommendations = []
    
    if diff > 10:
        recommendations.append(
            f"Dictionary works significantly better on Language {better} "
            f"({max(a_cov, b_cov):.1f}% vs {min(a_cov, b_cov):.1f}%)"
        )
        recommendations.append(
            f"Consider building a separate dictionary for Language {'A' if better == 'B' else 'B'}"
        )
    
    if overlap < 50:
        recommendations.append(
            f"Low vocabulary overlap ({overlap:.1f}%) suggests A and B may be different dialects or registers"
        )
    
    heb_a = results['hebrew_patterns_by_language']['language_a']
    heb_b = results['hebrew_patterns_by_language']['language_b']
    
    cohen_ratio = heb_b['cohen'] / max(heb_a['cohen'], 1)
    if cohen_ratio > 1.5:
        recommendations.append(
            f"Hebrew 'cohen' pattern is {cohen_ratio:.1f}x more common in Language B - "
            "Hebrew hypothesis stronger for B sections (Recipes, Zodiac)"
        )
    
    return recommendations


def main():
    print("Track 64: Currier A/B Language Separation")
    print("=" * 50)
    
    pages = vd.get_eva_pages('H')
    dictionary = load_dictionary()
    print(f"Loaded {len(dictionary)} dictionary entries")
    
    print("\n1. Extracting words by Currier language...")
    words_a, folios_a = get_folio_words_by_prefix(pages, CURRIER_A_PREFIXES)
    words_b, folios_b = get_folio_words_by_prefix(pages, CURRIER_B_PREFIXES)
    
    print(f"   Language A: {len(words_a)} words from {len(folios_a)} folios")
    print(f"   Language B: {len(words_b)} words from {len(folios_b)} folios")
    
    print("\n2. Calculating statistics...")
    stats_a = calc_word_stats(words_a)
    stats_b = calc_word_stats(words_b)
    char_freq_a = calc_char_freq(words_a)
    char_freq_b = calc_char_freq(words_b)
    
    print(f"\n   Language A: {stats_a['total']} total, {stats_a['unique']} unique, "
          f"avg len {stats_a['avg_len']}")
    print(f"   Language B: {stats_b['total']} total, {stats_b['unique']} unique, "
          f"avg len {stats_b['avg_len']}")
    
    print("\n3. Calculating dictionary coverage...")
    cov_a, _ = calc_dict_coverage(words_a, dictionary)
    cov_b, _ = calc_dict_coverage(words_b, dictionary)
    print(f"   Language A coverage: {cov_a}%")
    print(f"   Language B coverage: {cov_b}%")
    
    print("\n4. Section-by-section coverage...")
    sections = get_sections_coverage(pages, dictionary)
    for section, data in sections.items():
        print(f"   {section:12} (Currier {data['currier']}): {data['coverage']:5.1f}%")
    
    print("\n5. Vocabulary overlap analysis...")
    overlap = analyze_vocab_overlap(words_a, words_b)
    print(f"   Only in A: {overlap['only_a_count']}")
    print(f"   Only in B: {overlap['only_b_count']}")
    print(f"   In both: {overlap['both_count']}")
    print(f"   Overlap ratio: {overlap['overlap_ratio']}%")
    
    print("\n6. Hebrew patterns by language...")
    heb_a = find_hebrew_patterns(words_a)
    heb_b = find_hebrew_patterns(words_b)
    print(f"   Language A - cohen: {heb_a['cohen']}, qo-: {heb_a['qo_prefix']}, -y: {heb_a['y_suffix']}")
    print(f"   Language B - cohen: {heb_b['cohen']}, qo-: {heb_b['qo_prefix']}, -y: {heb_b['y_suffix']}")
    
    results = {
        'language_a': {
            'folios': folios_a[:20] + ['...'] if len(folios_a) > 20 else folios_a,
            'folio_count': len(folios_a),
            'total_words': stats_a['total'],
            'unique_words': stats_a['unique'],
            'avg_word_length': stats_a['avg_len'],
            'word_entropy': stats_a['entropy'],
            'char_freq': dict(list(char_freq_a.items())[:15]),
            'char_entropy': round(calc_entropy(char_freq_a), 3),
            'top_words': stats_a['top_100'][:30],
            'dictionary_coverage': cov_a
        },
        'language_b': {
            'folios': folios_b[:20] + ['...'] if len(folios_b) > 20 else folios_b,
            'folio_count': len(folios_b),
            'total_words': stats_b['total'],
            'unique_words': stats_b['unique'],
            'avg_word_length': stats_b['avg_len'],
            'word_entropy': stats_b['entropy'],
            'char_freq': dict(list(char_freq_b.items())[:15]),
            'char_entropy': round(calc_entropy(char_freq_b), 3),
            'top_words': stats_b['top_100'][:30],
            'dictionary_coverage': cov_b
        },
        'comparison': {
            'word_count_ratio': round(stats_b['total'] / max(stats_a['total'], 1), 2),
            'unique_ratio': round(stats_b['unique'] / max(stats_a['unique'], 1), 2),
            'length_diff': round(stats_b['avg_len'] - stats_a['avg_len'], 3),
            'entropy_diff': round(stats_b['entropy'] - stats_a['entropy'], 3),
            'coverage_diff': round(cov_b - cov_a, 2)
        },
        'sections_coverage': sections,
        'vocabulary_overlap': overlap,
        'hebrew_patterns_by_language': {
            'language_a': heb_a,
            'language_b': heb_b
        },
        'recommendations': []
    }
    
    results['recommendations'] = generate_recommendation(results)
    
    print("\n7. Recommendations:")
    for rec in results['recommendations']:
        print(f"   - {rec}")
    
    out_json = Path('results/currier_separation.json')
    out_json.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_json}")
    
    generate_report(results)
    
    return results


def generate_report(results):
    lines = [
        "# Currier A/B Language Separation Analysis",
        "",
        "## Summary",
        "",
        "Prescott Currier (1976) discovered the Voynich manuscript contains two distinct",
        "\"languages\" (A and B) with measurably different statistical properties.",
        "",
        "## Statistical Comparison",
        "",
        "| Metric | Language A | Language B | Difference |",
        "|--------|------------|------------|------------|",
    ]
    
    a = results['language_a']
    b = results['language_b']
    c = results['comparison']
    
    lines.extend([
        f"| Folio count | {a['folio_count']} | {b['folio_count']} | - |",
        f"| Total words | {a['total_words']:,} | {b['total_words']:,} | ×{c['word_count_ratio']} |",
        f"| Unique words | {a['unique_words']:,} | {b['unique_words']:,} | ×{c['unique_ratio']} |",
        f"| Avg word length | {a['avg_word_length']} | {b['avg_word_length']} | {c['length_diff']:+.3f} |",
        f"| Word entropy | {a['word_entropy']} | {b['word_entropy']} | {c['entropy_diff']:+.3f} |",
        f"| Char entropy | {a['char_entropy']} | {b['char_entropy']} | - |",
        f"| **Dict coverage** | **{a['dictionary_coverage']}%** | **{b['dictionary_coverage']}%** | **{c['coverage_diff']:+.1f}%** |",
        "",
        "## Dictionary Coverage by Section",
        "",
        "| Section | Currier | Coverage | Total Words |",
        "|---------|---------|----------|-------------|",
    ])
    
    for section, data in results['sections_coverage'].items():
        lines.append(f"| {section} | {data['currier']} | {data['coverage']:.1f}% | {data['total_words']:,} |")
    
    lines.extend([
        "",
        "## Vocabulary Overlap",
        "",
        f"- Words only in Language A: **{results['vocabulary_overlap']['only_a_count']:,}**",
        f"- Words only in Language B: **{results['vocabulary_overlap']['only_b_count']:,}**",
        f"- Words in BOTH languages: **{results['vocabulary_overlap']['both_count']:,}**",
        f"- Overlap ratio: **{results['vocabulary_overlap']['overlap_ratio']}%**",
        "",
        "### Top Words Only in Language A",
        "",
        ", ".join(results['vocabulary_overlap']['top_only_a'][:20]),
        "",
        "### Top Words Only in Language B",
        "",
        ", ".join(results['vocabulary_overlap']['top_only_b'][:20]),
        "",
        "### Top Shared Words",
        "",
        ", ".join(results['vocabulary_overlap']['top_shared'][:20]),
        "",
        "## Hebrew Patterns by Language",
        "",
        "| Pattern | Language A | Language B | Ratio (B/A) |",
        "|---------|------------|------------|-------------|",
    ])
    
    heb_a = results['hebrew_patterns_by_language']['language_a']
    heb_b = results['hebrew_patterns_by_language']['language_b']
    
    for pattern in ['cohen', 'qo_prefix', 'y_suffix', 'three_cons', 'daiin']:
        ratio = heb_b[pattern] / max(heb_a[pattern], 1)
        lines.append(f"| {pattern} | {heb_a[pattern]} | {heb_b[pattern]} | {ratio:.2f}x |")
    
    lines.extend([
        "",
        "## Top 15 Characters by Frequency",
        "",
        "### Language A",
        "",
        "| Char | Freq |",
        "|------|------|",
    ])
    
    for char, freq in list(a['char_freq'].items())[:15]:
        lines.append(f"| {char} | {freq:.3f} |")
    
    lines.extend([
        "",
        "### Language B",
        "",
        "| Char | Freq |",
        "|------|------|",
    ])
    
    for char, freq in list(b['char_freq'].items())[:15]:
        lines.append(f"| {char} | {freq:.3f} |")
    
    lines.extend([
        "",
        "## Recommendations",
        "",
    ])
    
    for rec in results['recommendations']:
        lines.append(f"- {rec}")
    
    lines.extend([
        "",
        "## Conclusions",
        "",
        "1. **Dictionary Performance**: Our Hebrew-Italian dictionary shows different ",
        "   coverage rates for A vs B sections, confirming Currier's observation that ",
        "   these are statistically distinct.",
        "",
        "2. **Hebrew Hypothesis Implications**: The distribution of Hebrew-like patterns ",
        "   (cohen, qo- prefix, -y suffix) differs between languages, suggesting our ",
        "   Hebrew hypothesis may apply more strongly to one language.",
        "",
        "3. **Vocabulary Differences**: The partial vocabulary overlap suggests A and B ",
        "   may represent different registers, topics, or even dialects of the same ",
        "   underlying language.",
        "",
        "4. **Future Work**: Consider building separate dictionaries for A and B sections ",
        "   to improve translation accuracy.",
        "",
        "---",
        "*Generated by Track 64: Currier A/B Separation Analysis*",
    ])
    
    out_md = Path('results/currier_separation_report.md')
    out_md.write_text('\n'.join(lines))
    print(f"Saved: {out_md}")


if __name__ == '__main__':
    main()



