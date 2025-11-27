"""
Track 39: Consonantal Writing Hypothesis Analysis
Tests whether Voynich uses a consonantal writing system where vowels are
omitted or minimally represented (like Hebrew, Arabic, or medieval shorthand).
"""

import json
import re
from collections import Counter
from pathlib import Path
from voynich_data import get_all_words, get_word_frequencies, get_eva_pages

EVA_VOWELS = {'o', 'a', 'e', 'i'}
EVA_CONSONANTS = {'y', 'd', 'l', 'r', 's', 'n', 'm', 'c', 'h', 'k', 't', 'p', 'f', 'q', 'x', 'g'}

LATIN_BOTANICAL = [
    ('radix', 'rdx'),
    ('folium', 'flm'),
    ('herba', 'hrb'),
    ('aqua', 'q'),
    ('medicina', 'mdcn'),
    ('flos', 'fls'),
    ('semen', 'smn'),
    ('cortex', 'crtx'),
    ('succus', 'sccs'),
    ('oleum', 'lm'),
    ('pulvis', 'plvs'),
    ('decoctio', 'dccti'),
    ('infusum', 'nfsm'),
    ('unguentum', 'ngntm'),
    ('pilula', 'pll'),
    ('planta', 'plnt'),
    ('arbor', 'rbr'),
    ('fructus', 'frcts'),
    ('caulis', 'cls'),
    ('ramus', 'rms'),
    ('petra', 'ptr'),
    ('terra', 'trr'),
    ('luna', 'ln'),
    ('stella', 'stll'),
    ('caelum', 'clm'),
    ('corpus', 'crps'),
    ('sanguis', 'sngs'),
    ('spiritus', 'sprts'),
    ('anima', 'nm'),
    ('virtus', 'vrts'),
]

HEBREW_BOTANICAL = [
    ('tsemach', 'tsmch', 'plant'),
    ('shoresh', 'shrsh', 'root'),
    ('aleh', 'lh', 'leaf'),
    ('mayim', 'mym', 'water'),
    ('perach', 'prch', 'flower'),
    ('zera', 'zr', 'seed'),
    ('ets', 'ts', 'tree'),
    ('pri', 'pr', 'fruit'),
    ('shamayim', 'shmym', 'sky/heavens'),
    ('yareakh', 'yrch', 'moon'),
    ('kokhav', 'kchv', 'star'),
    ('shemesh', 'shmsh', 'sun'),
    ('ruakh', 'rch', 'spirit/wind'),
    ('nefesh', 'nfsh', 'soul'),
    ('dam', 'dm', 'blood'),
    ('guf', 'gf', 'body'),
    ('refuah', 'rfh', 'medicine'),
    ('boker', 'bkr', 'morning'),
    ('layla', 'lyl', 'night'),
    ('yom', 'ym', 'day'),
]


def extract_consonants(word, eva_vowels=EVA_VOWELS):
    """Extract consonant skeleton from a word by removing vowels."""
    return ''.join(c for c in word.lower() if c not in eva_vowels)


def analyze_vowel_distribution(words, word_freq):
    """Analyze the distribution of vowels vs consonants in Voynich."""
    total_chars = 0
    vowel_chars = 0
    consonant_chars = 0
    
    for word, count in word_freq.items():
        word_clean = re.sub(r'[^a-z]', '', word.lower())
        for char in word_clean:
            total_chars += count
            if char in EVA_VOWELS:
                vowel_chars += count
            elif char in EVA_CONSONANTS:
                consonant_chars += count
    
    vowel_ratio = vowel_chars / total_chars if total_chars > 0 else 0
    consonant_ratio = consonant_chars / total_chars if total_chars > 0 else 0
    
    return {
        'total_chars': total_chars,
        'vowel_chars': vowel_chars,
        'consonant_chars': consonant_chars,
        'vowel_ratio': round(vowel_ratio, 4),
        'consonant_ratio': round(consonant_ratio, 4),
        'expected_latin_vowel_ratio': 0.38,
        'expected_hebrew_vowel_ratio': 0.0,
        'expected_arabic_vowel_ratio': 0.10,
        'resembles': 'Latin-like' if vowel_ratio > 0.3 else ('Arabic-like' if vowel_ratio > 0.05 else 'Hebrew-like')
    }


def analyze_consonant_clusters(words, word_freq):
    """Find consonant clusters (sequences without EVA vowels)."""
    clusters = []
    cluster_lengths = []
    
    for word in words:
        word_clean = re.sub(r'[^a-z]', '', word.lower())
        current_cluster = ''
        
        for char in word_clean:
            if char not in EVA_VOWELS:
                current_cluster += char
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                    cluster_lengths.append(len(current_cluster))
                current_cluster = ''
        
        if len(current_cluster) >= 2:
            clusters.append(current_cluster)
            cluster_lengths.append(len(current_cluster))
    
    cluster_counts = Counter(clusters)
    
    return {
        'total_clusters': len(clusters),
        'unique_clusters': len(cluster_counts),
        'max_length': max(cluster_lengths) if cluster_lengths else 0,
        'avg_length': round(sum(cluster_lengths) / len(cluster_lengths), 2) if cluster_lengths else 0,
        'top_clusters': cluster_counts.most_common(30),
        'length_distribution': dict(Counter(cluster_lengths).most_common(10)),
        'latin_phonotactic_violations': count_violations(clusters)
    }


def count_violations(clusters):
    """Count consonant clusters that violate Latin phonotactics."""
    violations = []
    latin_impossible = [
        'kk', 'tt', 'pp', 'ff', 'dd', 'ss', 'nn', 'mm', 'll', 'rr',
        'hh', 'ch', 'sh', 'ckh', 'cth', 'cph', 'cfh',
        'ky', 'ty', 'dy', 'chk', 'shk', 'dch', 'tch',
    ]
    
    for cluster in clusters:
        for pattern in latin_impossible:
            if pattern in cluster:
                violations.append((cluster, pattern))
                break
    
    return {
        'count': len(violations),
        'examples': violations[:20],
        'interpretation': 'Many violations suggest non-Latin phonotactics' if len(violations) > 50 else 'Few violations'
    }


def search_skeleton_matches(words, skeletons, skeleton_type='latin'):
    """Search for consonant skeleton matches in Voynich words."""
    matches = []
    
    for word in words:
        word_clean = re.sub(r'[^a-z]', '', word.lower())
        voynich_skeleton = extract_consonants(word_clean)
        
        for original, skeleton, *rest in (skeletons if skeleton_type == 'hebrew' else [(s[0], s[1]) for s in skeletons]):
            if len(skeleton) < 2:
                continue
            
            if skeleton in voynich_skeleton or voynich_skeleton == skeleton:
                meaning = rest[0] if rest else ''
                matches.append({
                    'voynich_word': word,
                    'voynich_skeleton': voynich_skeleton,
                    f'{skeleton_type}_word': original,
                    f'{skeleton_type}_skeleton': skeleton,
                    'match_type': 'exact' if voynich_skeleton == skeleton else 'contains',
                    'meaning': meaning
                })
    
    return matches


def simulate_word_lengths():
    """Simulate if Voynich word lengths match consonantal Latin hypothesis."""
    latin_test = [
        ('medicina', 8, 4),
        ('aqua', 4, 1),
        ('herba', 5, 3),
        ('folium', 6, 3),
        ('radix', 5, 3),
        ('planta', 6, 4),
        ('fructus', 7, 5),
        ('decoctio', 8, 5),
        ('unguentum', 9, 6),
        ('spiritus', 8, 5),
    ]
    
    latin_avg = sum(x[1] for x in latin_test) / len(latin_test)
    consonant_avg = sum(x[2] for x in latin_test) / len(latin_test)
    voynich_avg = 4.69
    
    return {
        'latin_avg_length': round(latin_avg, 2),
        'latin_consonant_skeleton_avg': round(consonant_avg, 2),
        'voynich_avg_length': voynich_avg,
        'hypothesis_prediction': round(consonant_avg, 2),
        'match': abs(voynich_avg - consonant_avg) < 1.5,
        'interpretation': f"Voynich ({voynich_avg}) vs predicted consonantal Latin ({consonant_avg:.2f})"
    }


def attempt_vowel_reconstruction(common_words, top_n=30):
    """Attempt to reconstruct Latin words by adding vowels to Voynich words."""
    
    latin_patterns = {
        'rdx': ['radix', 'redux'],
        'hrb': ['herba', 'hierba'],
        'mdcn': ['medicina', 'medicin'],
        'plnt': ['planta', 'planto'],
        'fls': ['flos', 'files'],
        'smn': ['semen', 'somnium'],
        'crtx': ['cortex'],
        'sccs': ['succus'],
        'lm': ['oleum', 'ulmus', 'alum'],
        'plvs': ['pulvis'],
        'ptr': ['petra', 'pater', 'puter'],
        'trr': ['terra'],
        'ln': ['luna', 'lino'],
        'stll': ['stella'],
        'clm': ['caelum', 'calamus'],
    }
    
    reconstructions = []
    
    for word, count in list(common_words.items())[:top_n]:
        word_clean = re.sub(r'[^a-z]', '', word.lower())
        skeleton = extract_consonants(word_clean)
        
        possible_latin = []
        for pattern, words_list in latin_patterns.items():
            if pattern == skeleton or pattern in skeleton or skeleton in pattern:
                possible_latin.extend(words_list)
        
        insertion_attempts = []
        for vowel in ['a', 'e', 'i', 'o', 'u']:
            attempt = vowel + word_clean
            insertion_attempts.append(attempt)
            for i in range(1, len(word_clean)):
                attempt = word_clean[:i] + vowel + word_clean[i:]
                insertion_attempts.append(attempt)
        
        reconstructions.append({
            'voynich_word': word,
            'frequency': count,
            'consonant_skeleton': skeleton,
            'possible_latin_matches': possible_latin[:5],
            'sample_vowel_insertions': insertion_attempts[:10]
        })
    
    return reconstructions


def calculate_hypothesis_score(vowel_analysis, cluster_analysis, latin_matches, hebrew_matches, length_sim):
    """Calculate overall score for consonantal hypothesis."""
    score = 0.0
    evidence = []
    
    if vowel_analysis['vowel_ratio'] < 0.25:
        score += 0.25
        evidence.append("Low vowel ratio supports consonantal")
    elif vowel_analysis['vowel_ratio'] > 0.35:
        score -= 0.1
        evidence.append("High vowel ratio contradicts consonantal")
    
    if cluster_analysis['avg_length'] > 2.5:
        score += 0.15
        evidence.append("Long consonant clusters support consonantal")
    
    if cluster_analysis['latin_phonotactic_violations']['count'] > 50:
        score += 0.2
        evidence.append("Many phonotactic violations suggest non-Latin base")
    
    if len(latin_matches) > 10:
        score += 0.2
        evidence.append(f"Found {len(latin_matches)} Latin skeleton matches")
    
    if len(hebrew_matches) > 10:
        score += 0.15
        evidence.append(f"Found {len(hebrew_matches)} Hebrew skeleton matches")
    
    if length_sim['match']:
        score += 0.15
        evidence.append("Word length matches consonantal Latin prediction")
    
    score = max(0, min(1, score))
    
    return {
        'score': round(score, 3),
        'evidence': evidence,
        'verdict': 'SUPPORTS CONSONANTAL' if score > 0.5 else ('INCONCLUSIVE' if score > 0.3 else 'DOES NOT SUPPORT CONSONANTAL')
    }


def run_analysis():
    """Run the full consonantal hypothesis analysis."""
    print("Track 39: Consonantal Writing Hypothesis Analysis")
    print("=" * 60)
    
    print("\nLoading Voynich data...")
    words = get_all_words()
    word_freq = get_word_frequencies()
    print(f"Loaded {len(words)} unique words")
    
    print("\n1. Analyzing vowel/consonant distribution...")
    vowel_analysis = analyze_vowel_distribution(words, word_freq)
    print(f"   Vowel ratio: {vowel_analysis['vowel_ratio']} (Latin expects: 0.38)")
    print(f"   Resembles: {vowel_analysis['resembles']}")
    
    print("\n2. Analyzing consonant clusters...")
    cluster_analysis = analyze_consonant_clusters(words, word_freq)
    print(f"   Found {cluster_analysis['total_clusters']} clusters")
    print(f"   Max length: {cluster_analysis['max_length']}, Avg: {cluster_analysis['avg_length']}")
    print(f"   Phonotactic violations: {cluster_analysis['latin_phonotactic_violations']['count']}")
    
    print("\n3. Testing Latin consonant skeletons...")
    latin_matches = search_skeleton_matches(words, LATIN_BOTANICAL, 'latin')
    print(f"   Found {len(latin_matches)} potential matches")
    for m in latin_matches[:5]:
        print(f"      {m['voynich_word']} ({m['voynich_skeleton']}) ~ {m['latin_word']} ({m['latin_skeleton']})")
    
    print("\n4. Testing Hebrew consonant skeletons...")
    hebrew_matches = search_skeleton_matches(words, HEBREW_BOTANICAL, 'hebrew')
    print(f"   Found {len(hebrew_matches)} potential matches")
    for m in hebrew_matches[:5]:
        print(f"      {m['voynich_word']} ({m['voynich_skeleton']}) ~ {m['hebrew_word']} ({m['hebrew_skeleton']}) = '{m['meaning']}'")
    
    print("\n5. Simulating word lengths...")
    length_sim = simulate_word_lengths()
    print(f"   Latin avg: {length_sim['latin_avg_length']} letters")
    print(f"   Consonant skeleton avg: {length_sim['latin_consonant_skeleton_avg']}")
    print(f"   Voynich avg: {length_sim['voynich_avg_length']}")
    print(f"   Match: {length_sim['match']}")
    
    print("\n6. Attempting vowel reconstruction...")
    reconstructions = attempt_vowel_reconstruction(word_freq)
    for r in reconstructions[:5]:
        print(f"   {r['voynich_word']} -> skeleton: {r['consonant_skeleton']}")
        if r['possible_latin_matches']:
            print(f"      Possible Latin: {', '.join(r['possible_latin_matches'])}")
    
    print("\n7. Calculating hypothesis score...")
    hypothesis_score = calculate_hypothesis_score(
        vowel_analysis, cluster_analysis, latin_matches, hebrew_matches, length_sim
    )
    print(f"   Score: {hypothesis_score['score']}")
    print(f"   Verdict: {hypothesis_score['verdict']}")
    for e in hypothesis_score['evidence']:
        print(f"      - {e}")
    
    results = {
        'vowel_distribution': vowel_analysis,
        'consonant_clusters': cluster_analysis,
        'skeleton_matches': {
            'latin': latin_matches[:50],
            'latin_total': len(latin_matches),
            'hebrew': hebrew_matches[:50],
            'hebrew_total': len(hebrew_matches),
        },
        'word_length_simulation': length_sim,
        'vowel_reconstruction_attempts': reconstructions,
        'hypothesis_score': hypothesis_score
    }
    
    out_json = Path('results/consonantal_analysis.json')
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nResults saved to {out_json}")
    
    generate_report(results)
    
    return results


def generate_report(results):
    """Generate markdown report."""
    report = """# Consonantal Writing Hypothesis Analysis

## Executive Summary

Testing whether Voynich uses a CONSONANTAL writing system where vowels are
omitted or minimally represented (like Hebrew, Arabic, or medieval shorthand).

**Verdict: {verdict}** (Score: {score})

## 1. Vowel/Consonant Distribution

| Metric | Voynich | Expected Latin | Expected Hebrew | Expected Arabic |
|--------|---------|----------------|-----------------|-----------------|
| Vowel Ratio | {vowel_ratio} | 0.38 | 0.0 | 0.10 |

**Analysis:** {resembles}

The vowel ratio of {vowel_ratio} is {comparison} than typical Latin text.

## 2. Consonant Cluster Analysis

- Total clusters found: {total_clusters}
- Unique clusters: {unique_clusters}
- Maximum cluster length: {max_length}
- Average cluster length: {avg_length}

### Top Consonant Clusters
{top_clusters}

### Phonotactic Violations
{violations_count} violations of Latin phonotactics found.
{violations_interpretation}

## 3. Latin Consonant Skeleton Matches

Found {latin_total} potential matches when comparing Voynich consonant skeletons
to Latin botanical/medical vocabulary.

### Sample Matches
{latin_matches}

## 4. Hebrew Consonant Skeleton Matches

Found {hebrew_total} potential matches with Hebrew consonant roots.

### Sample Matches
{hebrew_matches}

## 5. Word Length Analysis

| Metric | Value |
|--------|-------|
| Latin average word length | {latin_avg} |
| Latin consonant skeleton avg | {consonant_avg} |
| Voynich average word length | {voynich_avg} |

**Match:** {length_match}

{length_interpretation}

## 6. Vowel Reconstruction Attempts

Sample attempts to reconstruct Latin words by adding vowels:

{reconstructions}

## 7. Evidence Summary

{evidence_list}

## Conclusion

{conclusion}

### Implications

If consonantal hypothesis is {confirmed}:
{implications}
""".format(
        verdict=results['hypothesis_score']['verdict'],
        score=results['hypothesis_score']['score'],
        vowel_ratio=results['vowel_distribution']['vowel_ratio'],
        resembles=results['vowel_distribution']['resembles'],
        comparison='higher' if results['vowel_distribution']['vowel_ratio'] > 0.38 else 'lower',
        total_clusters=results['consonant_clusters']['total_clusters'],
        unique_clusters=results['consonant_clusters']['unique_clusters'],
        max_length=results['consonant_clusters']['max_length'],
        avg_length=results['consonant_clusters']['avg_length'],
        top_clusters='\n'.join([f"- `{c[0]}`: {c[1]} occurrences" for c in results['consonant_clusters']['top_clusters'][:15]]),
        violations_count=results['consonant_clusters']['latin_phonotactic_violations']['count'],
        violations_interpretation=results['consonant_clusters']['latin_phonotactic_violations']['interpretation'],
        latin_total=results['skeleton_matches']['latin_total'],
        latin_matches='\n'.join([f"| {m['voynich_word']} | {m['voynich_skeleton']} | {m['latin_word']} | {m['latin_skeleton']} |" 
                                  for m in results['skeleton_matches']['latin'][:15]]),
        hebrew_total=results['skeleton_matches']['hebrew_total'],
        hebrew_matches='\n'.join([f"| {m['voynich_word']} | {m['voynich_skeleton']} | {m['hebrew_word']} | {m['meaning']} |" 
                                   for m in results['skeleton_matches']['hebrew'][:15]]),
        latin_avg=results['word_length_simulation']['latin_avg_length'],
        consonant_avg=results['word_length_simulation']['latin_consonant_skeleton_avg'],
        voynich_avg=results['word_length_simulation']['voynich_avg_length'],
        length_match='YES' if results['word_length_simulation']['match'] else 'NO',
        length_interpretation=results['word_length_simulation']['interpretation'],
        reconstructions='\n'.join([f"- **{r['voynich_word']}** → skeleton: `{r['consonant_skeleton']}` → possible: {', '.join(r['possible_latin_matches'][:3]) or 'none'}" 
                                   for r in results['vowel_reconstruction_attempts'][:10]]),
        evidence_list='\n'.join([f"- {e}" for e in results['hypothesis_score']['evidence']]),
        conclusion=f"The consonantal hypothesis {'is supported' if results['hypothesis_score']['score'] > 0.5 else 'is not strongly supported'} by the evidence.",
        confirmed='supported' if results['hypothesis_score']['score'] > 0.5 else 'not supported',
        implications="""
- Voynich may encode consonants only, requiring vowel inference for reading
- Simple substitution ciphers will always fail
- Need to look for Semitic-style root patterns
- The high EVA "vowel" frequency may indicate these glyphs have other functions
""" if results['hypothesis_score']['score'] > 0.5 else """
- Voynich likely uses full vowel representation
- The EVA vowel assignments may be approximately correct
- Look for other explanations (abbreviation, cipher, constructed language)
"""
    )
    
    out_md = Path('results/consonantal_report.md')
    out_md.write_text(report)
    print(f"Report saved to {out_md}")


if __name__ == "__main__":
    run_analysis()



