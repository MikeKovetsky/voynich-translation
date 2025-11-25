"""
Hebrew/Semitic Language Analysis for Voynich Manuscript.
Based on Track 37 finding that Voynich scores highest for Hebrew (0.415).
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from voynich_data import get_all_words, get_word_frequencies, get_eva_pages

HEBREW_LETTER_FREQ = {
    'yod': 0.1106, 'he': 0.1087, 'vav': 0.1038, 'mem': 0.0836,
    'lamed': 0.0711, 'alef': 0.0618, 'resh': 0.0564, 'bet': 0.0533,
    'nun': 0.0510, 'shin': 0.0463, 'tav': 0.0450, 'kaf': 0.0378,
    'ayin': 0.0325, 'dalet': 0.0317, 'het': 0.0253, 'samekh': 0.0186,
    'pe': 0.0175, 'gimel': 0.0165, 'zayin': 0.0157, 'qof': 0.0147,
    'tsade': 0.0089, 'tet': 0.0063
}

HEBREW_PREFIXES = ['ha', 've', 'be', 'le', 'mi', 'she', 'ke']
HEBREW_SUFFIXES = ['im', 'ot', 'i', 'o', 'ah', 'cha', 'nu', 'hem', 'hen']

EVA_GLYPH_TO_HEBREW = {
    'o': 'he', 'a': 'alef', 'e': 'vav', 'y': 'yod', 'i': 'nun', 'n': 'mem',
    'd': 'dalet', 'l': 'lamed', 'r': 'resh', 's': 'samekh', 'k': 'kaf',
    'ch': 'khet', 'sh': 'shin', 't': 'tav', 'p': 'pe', 'f': 'pe',
    'q': 'qof', 'm': 'mem', 'g': 'gimel'
}

HEBREW_BOTANICAL_TERMS = [
    'shumshum', 'kamon', 'kusbar', 'shevet', 'hyssop', 'lavan', 'zahav',
    'shoshen', 'vered', 'tapuah', 'gefen', 'tamar', 'zayit', 'rimmon',
    'dekel', 'oren', 'alon', 'egoz', 'luz', 'shaked', 'teen', 'teomim',
    'alharsuf', 'karpas', 'gazar', 'batzal', 'shum', 'shumar', 'dagan',
    'hita', 'seora', 'shibolet', 'kusmet', 'ezov', 'lavender', 'menta',
    'marvah', 'rosmarin', 'thyme', 'zaatar', 'basil', 'rehan', 'parsley',
    'petrozelinum', 'koriander', 'dill', 'shabat', 'fennel', 'anis'
]

HEBREW_MEDICAL_TERMS = [
    'refuah', 'rofe', 'holeh', 'makhov', 'keev', 'dam', 'lev', 'kelayot',
    'kaved', 'mechem', 'rishon', 'beten', 'rosh', 'regel', 'yad', 'ayin',
    'ozen', 'af', 'peh', 'lashon', 'shen', 'tzavar', 'garon', 'katef',
    'zroa', 'etzba', 'berekh', 'keshet', 'shok', 'yarekh', 'gab', 'hazeh',
    'takhton', 'elyon', 'pnim', 'hutz', 'mar', 'matok', 'ham', 'kar'
]


def get_voynich_letter_freq():
    words = get_all_words()
    all_chars = ''.join(words)
    total = len(all_chars)
    freq = Counter(all_chars)
    return {char: count/total for char, count in freq.most_common()}


def analyze_consonantal():
    """Test if Voynich has consonantal writing pattern (vowels omitted)."""
    words = get_all_words()
    eva_vowels = set('oaei')
    
    vowel_ratios = []
    for word in words:
        if len(word) < 3:
            continue
        vowels = sum(1 for c in word if c in eva_vowels)
        vowel_ratios.append(vowels / len(word))
    
    avg_vowel_ratio = sum(vowel_ratios) / len(vowel_ratios) if vowel_ratios else 0
    
    return {
        'voynich_vowel_ratio': round(avg_vowel_ratio, 4),
        'expected_consonantal': 0.15,
        'expected_full_vowel': 0.40,
        'is_consonantal': avg_vowel_ratio < 0.25,
        'interpretation': 'CONSONANTAL' if avg_vowel_ratio < 0.25 else 
                         'VOWEL-RICH' if avg_vowel_ratio > 0.35 else 'MIXED'
    }


def find_root_patterns():
    """Search for 3-consonant root patterns (Hebrew root system)."""
    words = get_all_words()
    eva_consonants = set('dklmnprsfghcqtx')
    
    def extract_consonants(word):
        return ''.join(c for c in word if c in eva_consonants)
    
    roots = Counter()
    word_by_root = defaultdict(list)
    
    for word in words:
        cons = extract_consonants(word)
        if len(cons) >= 3:
            root = cons[:3]
            roots[root] += 1
            if len(word_by_root[root]) < 10:
                word_by_root[root].append(word)
    
    top_roots = roots.most_common(30)
    
    root_variations = {}
    for root, count in top_roots[:15]:
        if len(word_by_root[root]) >= 3:
            root_variations[root] = {
                'count': count,
                'examples': word_by_root[root][:8]
            }
    
    root_score = len([r for r, c in top_roots if c >= 10]) / 30 if top_roots else 0
    
    return {
        'top_roots': [{
            'root': root,
            'count': count,
            'examples': word_by_root[root][:5]
        } for root, count in top_roots[:20]],
        'root_variations': root_variations,
        'root_pattern_score': round(root_score, 4),
        'total_roots_found': len([r for r, c in roots.items() if c >= 5]),
        'interpretation': 'ROOT_SYSTEM_LIKELY' if root_score > 0.5 else 'ROOT_SYSTEM_WEAK'
    }


def analyze_affixes():
    """Search for Hebrew-like prefix/suffix patterns."""
    words = get_all_words()
    word_freq = get_word_frequencies()
    
    prefix_counts = Counter()
    suffix_counts = Counter()
    
    for word in words:
        if len(word) < 3:
            continue
        prefix_counts[word[:2]] += 1
        suffix_counts[word[-2:]] += 1
        if len(word) >= 4:
            prefix_counts[word[:3]] += 1
            suffix_counts[word[-3:]] += 1
    
    top_prefixes = prefix_counts.most_common(20)
    top_suffixes = suffix_counts.most_common(20)
    
    eva_prefix_map = {
        'ch': 'ha', 'qo': 'ha', 'da': 've', 'sh': 'she', 
        'ol': 'le', 'ok': 'be', 'ot': 'mi'
    }
    
    eva_suffix_map = {
        'dy': 'i', 'in': 'im', 'al': 'ah', 'ol': 'o',
        'ar': 'cha', 'am': 'hem', 'an': 'hen', 'ey': 'ot'
    }
    
    prefix_matches = []
    for prefix, count in top_prefixes[:10]:
        if prefix in eva_prefix_map:
            prefix_matches.append({
                'eva': prefix,
                'hebrew': eva_prefix_map[prefix],
                'count': count
            })
    
    suffix_matches = []
    for suffix, count in top_suffixes[:10]:
        if suffix in eva_suffix_map:
            suffix_matches.append({
                'eva': suffix,
                'hebrew': eva_suffix_map[suffix],
                'count': count
            })
    
    total_words = len(words)
    prefix_coverage = sum(c for _, c in top_prefixes[:5]) / total_words
    suffix_coverage = sum(c for _, c in top_suffixes[:5]) / total_words
    
    return {
        'top_prefixes': [{'prefix': p, 'count': c} for p, c in top_prefixes[:15]],
        'top_suffixes': [{'suffix': s, 'count': c} for s, c in top_suffixes[:15]],
        'hebrew_prefix_matches': prefix_matches,
        'hebrew_suffix_matches': suffix_matches,
        'prefix_concentration': round(prefix_coverage, 4),
        'suffix_concentration': round(suffix_coverage, 4),
        'affix_pattern_score': round((prefix_coverage + suffix_coverage) / 2, 4)
    }


def compare_word_length():
    """Compare Voynich word length with Hebrew patterns."""
    words = get_all_words()
    lengths = [len(w) for w in words]
    
    length_dist = Counter(lengths)
    total = len(lengths)
    
    avg_length = sum(lengths) / len(lengths)
    
    return {
        'voynich_avg_length': round(avg_length, 2),
        'hebrew_typical_range': '3-5 letters',
        'voynich_distribution': {
            str(k): round(v/total, 4) for k, v in sorted(length_dist.items()) if k <= 10
        },
        'short_words_ratio': round(sum(1 for l in lengths if l <= 4) / total, 4),
        'length_similarity': round(1 - abs(avg_length - 4.5) / 4.5, 4),
        'interpretation': 'SIMILAR_TO_HEBREW' if 3.5 <= avg_length <= 5.5 else 'DIFFERENT'
    }


def frequency_mapping():
    """Attempt to map Voynich glyphs to Hebrew letters by frequency."""
    voynich_freq = get_voynich_letter_freq()
    
    voynich_sorted = sorted(voynich_freq.items(), key=lambda x: -x[1])[:22]
    hebrew_sorted = sorted(HEBREW_LETTER_FREQ.items(), key=lambda x: -x[1])
    
    mapping = {}
    freq_similarity = []
    
    for i, ((v_char, v_freq), (h_letter, h_freq)) in enumerate(zip(voynich_sorted, hebrew_sorted)):
        mapping[v_char] = {
            'hebrew_letter': h_letter,
            'voynich_freq': round(v_freq, 4),
            'hebrew_freq': round(h_freq, 4),
            'difference': round(abs(v_freq - h_freq), 4)
        }
        freq_similarity.append(1 - abs(v_freq - h_freq))
    
    avg_similarity = sum(freq_similarity) / len(freq_similarity) if freq_similarity else 0
    
    return {
        'frequency_based_mapping': mapping,
        'average_frequency_similarity': round(avg_similarity, 4),
        'top_5_matches': {
            voynich_sorted[i][0]: hebrew_sorted[i][0] for i in range(min(5, len(voynich_sorted)))
        },
        'mapping_quality': 'HIGH' if avg_similarity > 0.85 else 'MEDIUM' if avg_similarity > 0.7 else 'LOW'
    }


def vocabulary_comparison():
    """Compare Voynich words with Hebrew botanical/medical terms."""
    words = get_all_words()
    word_set = set(words)
    
    all_hebrew_terms = HEBREW_BOTANICAL_TERMS + HEBREW_MEDICAL_TERMS
    
    direct_matches = [term for term in all_hebrew_terms if term.lower() in word_set]
    
    partial_matches = []
    for term in all_hebrew_terms:
        term_lower = term.lower()
        for word in words:
            if len(word) >= 4 and len(term_lower) >= 4:
                if term_lower[:4] in word or word[:4] in term_lower:
                    partial_matches.append({
                        'hebrew_term': term,
                        'voynich_word': word,
                        'match_type': 'prefix'
                    })
                    break
    
    pattern_matches = []
    for term in all_hebrew_terms[:30]:
        consonants = ''.join(c for c in term.lower() if c not in 'aeiou')
        for word in words[:1000]:
            word_cons = ''.join(c for c in word if c not in 'oaei')
            if len(consonants) >= 3 and consonants[:3] == word_cons[:3]:
                pattern_matches.append({
                    'hebrew_term': term,
                    'voynich_word': word,
                    'consonant_pattern': consonants[:3]
                })
                break
    
    return {
        'direct_matches': direct_matches,
        'partial_matches': partial_matches[:20],
        'consonant_pattern_matches': pattern_matches[:20],
        'total_hebrew_terms_tested': len(all_hebrew_terms),
        'match_rate': round(len(partial_matches) / len(all_hebrew_terms), 4),
        'interpretation': 'SOME_SIMILARITY' if len(partial_matches) > 10 else 'WEAK_SIMILARITY'
    }


def positional_analysis():
    """Analyze positional patterns (Hebrew has 5 final letter forms)."""
    words = get_all_words()
    
    initial = Counter()
    final = Counter()
    medial = Counter()
    
    for word in words:
        if len(word) >= 2:
            initial[word[0]] += 1
            final[word[-1]] += 1
            for c in word[1:-1]:
                medial[c] += 1
    
    final_only = {}
    for char, count in final.most_common():
        init_count = initial.get(char, 0)
        if count > init_count * 3:
            final_only[char] = {
                'final_count': count,
                'initial_count': init_count,
                'ratio': round(count / (init_count + 1), 2)
            }
    
    initial_only = {}
    for char, count in initial.most_common():
        fin_count = final.get(char, 0)
        if count > fin_count * 3:
            initial_only[char] = {
                'initial_count': count,
                'final_count': fin_count,
                'ratio': round(count / (fin_count + 1), 2)
            }
    
    positional_score = (len(final_only) + len(initial_only)) / 10
    
    return {
        'strong_final_glyphs': dict(list(final_only.items())[:10]),
        'strong_initial_glyphs': dict(list(initial_only.items())[:10]),
        'hebrew_final_letters': 5,
        'voynich_position_specific_glyphs': len(final_only) + len(initial_only),
        'positional_score': round(min(positional_score, 1.0), 4),
        'interpretation': 'SIMILAR_TO_HEBREW' if 4 <= len(final_only) <= 7 else 'DIFFERENT'
    }


def run_analysis():
    print("Running Hebrew/Semitic Analysis...")
    
    print("  Analyzing consonantal patterns...")
    consonantal = analyze_consonantal()
    
    print("  Searching for root patterns...")
    roots = find_root_patterns()
    
    print("  Analyzing affixes...")
    affixes = analyze_affixes()
    
    print("  Comparing word lengths...")
    lengths = compare_word_length()
    
    print("  Attempting frequency mapping...")
    freq_map = frequency_mapping()
    
    print("  Comparing vocabulary...")
    vocab = vocabulary_comparison()
    
    print("  Analyzing positional patterns...")
    positions = positional_analysis()
    
    consonantal_score = 0.7 if consonantal['is_consonantal'] else 0.3
    root_score = roots['root_pattern_score']
    affix_score = affixes['affix_pattern_score']
    length_score = lengths['length_similarity']
    freq_score = freq_map['average_frequency_similarity']
    position_score = positions['positional_score']
    
    overall_score = (
        consonantal_score * 0.2 +
        root_score * 0.25 +
        affix_score * 0.15 +
        length_score * 0.15 +
        freq_score * 0.15 +
        position_score * 0.10
    )
    
    results = {
        'structural_comparison': {
            'consonantal_analysis': consonantal,
            'consonantal_score': round(consonantal_score, 4)
        },
        'root_patterns': roots,
        'affix_analysis': affixes,
        'word_length_comparison': lengths,
        'glyph_to_hebrew_mapping': freq_map,
        'vocabulary_comparison': vocab,
        'positional_analysis': positions,
        'overall_hebrew_score': round(overall_score, 4),
        'component_scores': {
            'consonantal': round(consonantal_score, 4),
            'root_patterns': round(root_score, 4),
            'affixes': round(affix_score, 4),
            'word_length': round(length_score, 4),
            'frequency_mapping': round(freq_score, 4),
            'positional': round(position_score, 4)
        },
        'verdict': 'STRONG_HEBREW_CHARACTERISTICS' if overall_score > 0.6 else
                  'MODERATE_HEBREW_CHARACTERISTICS' if overall_score > 0.4 else
                  'WEAK_HEBREW_CHARACTERISTICS'
    }
    
    Path('results').mkdir(exist_ok=True)
    
    with open('results/hebrew_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    generate_report(results)
    
    print(f"\nOverall Hebrew Score: {overall_score:.4f}")
    print(f"Verdict: {results['verdict']}")
    
    return results


def generate_report(results):
    report = """# Hebrew/Semitic Language Analysis Report

## Executive Summary
Track 37 revealed Voynich scores highest for Hebrew (0.415) among all tested languages.
This analysis deep-dives into Hebrew structural characteristics.

## Overall Hebrew Score: {overall:.4f}

**Verdict: {verdict}**

---

## 1. Consonantal Writing Analysis

Hebrew traditionally omits vowels (consonantal writing).

| Metric | Value |
|--------|-------|
| Voynich vowel ratio | {vowel_ratio} |
| Expected for consonantal | ~0.15 |
| Expected with full vowels | ~0.40 |
| Interpretation | {consonantal_interp} |

**Score: {consonantal_score:.4f}**

---

## 2. Root Pattern Analysis

Hebrew uses 3-consonant roots. Example: K-T-B (write) → katav, kotev, ktiva.

### Top Root Patterns Found

| Root | Count | Example Words |
|------|-------|---------------|
""".format(
        overall=results['overall_hebrew_score'],
        verdict=results['verdict'],
        vowel_ratio=results['structural_comparison']['consonantal_analysis']['voynich_vowel_ratio'],
        consonantal_interp=results['structural_comparison']['consonantal_analysis']['interpretation'],
        consonantal_score=results['component_scores']['consonantal']
    )
    
    for root in results['root_patterns']['top_roots'][:10]:
        examples = ', '.join(root['examples'][:3])
        report += f"| {root['root']} | {root['count']} | {examples} |\n"
    
    report += f"""
**Total roots with 5+ occurrences: {results['root_patterns']['total_roots_found']}**

**Root Pattern Score: {results['component_scores']['root_patterns']:.4f}**

---

## 3. Prefix/Suffix Analysis

Hebrew common prefixes: ha- (the), ve- (and), be- (in), le- (to), mi- (from)
Hebrew common suffixes: -im (plural masc), -ot (plural fem), -i (my)

### Top Voynich Prefixes

| Prefix | Count |
|--------|-------|
"""
    
    for item in results['affix_analysis']['top_prefixes'][:8]:
        report += f"| {item['prefix']} | {item['count']} |\n"
    
    report += """
### Top Voynich Suffixes

| Suffix | Count |
|--------|-------|
"""
    
    for item in results['affix_analysis']['top_suffixes'][:8]:
        report += f"| {item['suffix']} | {item['count']} |\n"
    
    report += f"""
**Affix Score: {results['component_scores']['affixes']:.4f}**

---

## 4. Word Length Distribution

Hebrew words typically 3-5 letters (root-based).

| Metric | Value |
|--------|-------|
| Voynich average | {results['word_length_comparison']['voynich_avg_length']} |
| Hebrew typical | {results['word_length_comparison']['hebrew_typical_range']} |
| Short words ratio | {results['word_length_comparison']['short_words_ratio']} |
| Similarity | {results['word_length_comparison']['length_similarity']} |

**Length Score: {results['component_scores']['word_length']:.4f}**

---

## 5. Glyph-to-Hebrew Frequency Mapping

Attempting to map Voynich glyphs to Hebrew letters by frequency.

| Voynich | Hebrew | V.Freq | H.Freq | Diff |
|---------|--------|--------|--------|------|
"""
    
    for v_char, data in list(results['glyph_to_hebrew_mapping']['frequency_based_mapping'].items())[:10]:
        report += f"| {v_char} | {data['hebrew_letter']} | {data['voynich_freq']} | {data['hebrew_freq']} | {data['difference']} |\n"
    
    report += f"""
**Mapping Quality: {results['glyph_to_hebrew_mapping']['mapping_quality']}**

**Frequency Score: {results['component_scores']['frequency_mapping']:.4f}**

---

## 6. Positional Analysis

Hebrew has 5 letters with special final forms (ך, ם, ן, ף, ץ).

### Strong Final Glyphs (like Hebrew final forms)
"""
    
    for glyph, data in list(results['positional_analysis']['strong_final_glyphs'].items())[:5]:
        report += f"- **{glyph}**: final={data['final_count']}, initial={data['initial_count']}, ratio={data['ratio']}\n"
    
    report += f"""
### Strong Initial Glyphs
"""
    
    for glyph, data in list(results['positional_analysis']['strong_initial_glyphs'].items())[:5]:
        report += f"- **{glyph}**: initial={data['initial_count']}, final={data['final_count']}, ratio={data['ratio']}\n"
    
    report += f"""
| Metric | Voynich | Hebrew |
|--------|---------|--------|
| Position-specific glyphs | {results['positional_analysis']['voynich_position_specific_glyphs']} | 5 |

**Positional Score: {results['component_scores']['positional']:.4f}**

---

## 7. Vocabulary Comparison

Tested {results['vocabulary_comparison']['total_hebrew_terms_tested']} Hebrew botanical/medical terms.

### Consonant Pattern Matches
"""
    
    for match in results['vocabulary_comparison']['consonant_pattern_matches'][:10]:
        report += f"- Hebrew: **{match['hebrew_term']}** ↔ Voynich: **{match['voynich_word']}** (pattern: {match['consonant_pattern']})\n"
    
    report += f"""
**Match Rate: {results['vocabulary_comparison']['match_rate']:.4f}**

---

## Summary of Scores

| Component | Score |
|-----------|-------|
| Consonantal Writing | {results['component_scores']['consonantal']:.4f} |
| Root Patterns | {results['component_scores']['root_patterns']:.4f} |
| Affix Patterns | {results['component_scores']['affixes']:.4f} |
| Word Length | {results['component_scores']['word_length']:.4f} |
| Frequency Mapping | {results['component_scores']['frequency_mapping']:.4f} |
| Positional Patterns | {results['component_scores']['positional']:.4f} |
| **OVERALL** | **{results['overall_hebrew_score']:.4f}** |

---

## Conclusion

{results['verdict']}

### Key Findings:
1. **Consonantal Pattern**: {results['structural_comparison']['consonantal_analysis']['interpretation']}
2. **Root System**: {results['root_patterns']['interpretation']}
3. **Word Length**: {results['word_length_comparison']['interpretation']}
4. **Positional Forms**: {results['positional_analysis']['interpretation']}

### Historical Context:
- Medieval Jewish communities existed in Northern Italy
- Hebrew medical/botanical manuscripts were common
- Kabbalah manuscripts used encoded text
- Some Jewish scribes wrote Hebrew in Latin scripts

### Implications:
If Voynich shows Hebrew characteristics, possible interpretations:
1. Hebrew written in disguised/invented script
2. Judeo-Romance language (like Ladino)
3. Hebrew-Latin hybrid text
4. Kabbalistic encoded manuscript
"""
    
    with open('results/hebrew_report.md', 'w') as f:
        f.write(report)
    
    print("Report saved to results/hebrew_report.md")


if __name__ == '__main__':
    run_analysis()
