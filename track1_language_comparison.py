#!/usr/bin/env python3
"""
Track 1: Agglutinative Language Comparison
Compare Voynich grammar patterns with Turkish, Finnish, Hungarian, Basque, Georgian
"""

import re
import json
import math
from collections import Counter
from pathlib import Path

# Language case systems and characteristics
LANGUAGE_DATA = {
    'Turkish': {
        'case_endings': {
            'nominative': '',        # unmarked
            'accusative': '-ı/-i/-u/-ü',
            'dative': '-a/-e',
            'locative': '-da/-de/-ta/-te',
            'ablative': '-dan/-den/-tan/-ten',
            'genitive': '-ın/-in/-un/-ün',
            'instrumental': '-la/-le',
        },
        'num_cases': 6,
        'has_articles': False,
        'word_order': 'SOV',
        'avg_word_length': 6.5,
        'vowel_harmony': True,
        'common_suffixes': ['lar', 'ler', 'dan', 'den', 'da', 'de', 'ı', 'i'],
    },
    'Finnish': {
        'case_endings': {
            'nominative': '',        # unmarked
            'accusative': '-n/-t',
            'genitive': '-n',
            'partitive': '-a/-ä/-ta/-tä',
            'inessive': '-ssa/-ssä',
            'elative': '-sta/-stä',
            'illative': '-an/-en/-iin',
            'adessive': '-lla/-llä',
            'ablative': '-lta/-ltä',
            'allative': '-lle',
            'essive': '-na/-nä',
            'translative': '-ksi',
            'instructive': '-n',
            'abessive': '-tta/-ttä',
            'comitative': '-ne-',
        },
        'num_cases': 15,
        'has_articles': False,
        'word_order': 'SVO',
        'avg_word_length': 7.5,
        'vowel_harmony': True,
        'common_suffixes': ['ssa', 'sta', 'lla', 'lta', 'lle', 'na', 'ksi'],
    },
    'Hungarian': {
        'case_endings': {
            'nominative': '',
            'accusative': '-t/-at/-ot/-et/-öt',
            'dative': '-nak/-nek',
            'instrumental': '-val/-vel',
            'causal-final': '-ért',
            'translative': '-vá/-vé',
            'terminative': '-ig',
            'essive-formal': '-ként',
            'essive-modal': '-ul/-ül',
            'inessive': '-ban/-ben',
            'superessive': '-n/-on/-en/-ön',
            'adessive': '-nál/-nél',
            'illative': '-ba/-be',
            'sublative': '-ra/-re',
            'allative': '-hoz/-hez/-höz',
            'elative': '-ból/-ből',
            'delative': '-ról/-ről',
            'ablative': '-tól/-től',
        },
        'num_cases': 18,
        'has_articles': True,  # 'a/az' definite, 'egy' indefinite
        'word_order': 'SVO/flexible',
        'avg_word_length': 6.0,
        'vowel_harmony': True,
        'common_suffixes': ['ban', 'ben', 'nak', 'nek', 'val', 'vel', 'ra', 're'],
    },
    'Basque': {
        'case_endings': {
            'absolutive': '',  # unmarked (like nominative)
            'ergative': '-k',
            'dative': '-i/-ri',
            'genitive': '-ren/-en',
            'comitative': '-rekin/-ekin',
            'benefactive': '-rentzat/-entzat',
            'instrumental': '-z',
            'inessive': '-n',
            'allative': '-ra/-ra',
            'ablative': '-tik',
            'local-genitive': '-ko',
            'partitive': '-rik',
        },
        'num_cases': 12,
        'has_articles': True,  # suffix article '-a'
        'word_order': 'SOV',
        'avg_word_length': 5.5,
        'vowel_harmony': False,
        'common_suffixes': ['ak', 'ek', 'ik', 'ra', 'tik', 'ko', 'ren'],
    },
    'Georgian': {
        'case_endings': {
            'nominative': '-i',
            'ergative': '-ma',
            'dative': '-s',
            'genitive': '-is',
            'instrumental': '-it',
            'adverbial': '-ad',
            'vocative': '-o',
        },
        'num_cases': 7,
        'has_articles': False,
        'word_order': 'SOV',
        'avg_word_length': 5.0,
        'vowel_harmony': False,
        'common_suffixes': ['ma', 'is', 'it', 'ad', 's', 'i'],
    },
}

# Voynich patterns from our analysis
VOYNICH_PATTERNS = {
    'suffixes': {
        '9': {'freq': 0.37, 'likely_function': 'nominative/unmarked'},
        '89': {'freq': 0.118, 'likely_function': 'genitive_plural'},
        'am': {'freq': 0.094, 'likely_function': 'accusative'},
        'oe': {'freq': 0.089, 'likely_function': 'locative'},
        'ay': {'freq': 0.069, 'likely_function': 'genitive'},
        'ae': {'freq': 0.054, 'likely_function': 'instrumental'},
        'an': {'freq': 0.042, 'likely_function': 'ablative'},
        'c9': {'freq': 0.063, 'likely_function': 'genitive'},
    },
    'prefixes': {
        '4o': {'freq': 0.129, 'likely_function': 'article/determiner'},
        'o': {'freq': 0.211, 'likely_function': 'word_class_marker'},
        '1': {'freq': 0.156, 'likely_function': 'verb_marker'},
        '8': {'freq': 0.080, 'likely_function': 'preposition/genitive'},
    },
    'avg_word_length': 3.91,
    'num_case_like_endings': 8,
    'has_article_like_prefix': True,
}

def load_voynich_words():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    words = []
    for line in text.split('\n'):
        clean = re.sub(r'<[^>]+>', '', line)
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            ws = re.split(r'[.,\s]+', clean)
            words.extend([w for w in ws if w and len(w) > 0])
    return words

def calculate_case_similarity(lang_name, lang_data):
    """Score how well Voynich case system matches this language"""
    score = 0
    max_score = 100
    
    # Number of cases comparison (Voynich has ~8 case-like endings)
    case_diff = abs(lang_data['num_cases'] - VOYNICH_PATTERNS['num_case_like_endings'])
    if case_diff == 0:
        score += 25
    elif case_diff <= 2:
        score += 20
    elif case_diff <= 4:
        score += 15
    elif case_diff <= 6:
        score += 10
    else:
        score += 5
    
    # Article system match
    if lang_data['has_articles'] == VOYNICH_PATTERNS['has_article_like_prefix']:
        score += 20
    else:
        score += 10
    
    # Unmarked nominative (Voynich '9' is very common - 37%)
    # Languages with unmarked/simple nominative should score higher
    if lang_data['case_endings'].get('nominative', '') == '':
        score += 15
    else:
        score += 5
    
    # Word order - agglutinative languages often SOV
    if lang_data['word_order'] in ['SOV', 'SVO/flexible']:
        score += 10
    else:
        score += 5
    
    # Vowel harmony (could explain some Voynich patterns)
    if lang_data['vowel_harmony']:
        score += 10
    else:
        score += 5
    
    # Word length comparison
    len_diff = abs(lang_data['avg_word_length'] - VOYNICH_PATTERNS['avg_word_length'])
    if len_diff <= 1.0:
        score += 20
    elif len_diff <= 2.0:
        score += 15
    elif len_diff <= 3.0:
        score += 10
    else:
        score += 5
    
    return score / max_score

def analyze_suffix_patterns(lang_name, lang_data):
    """Compare suffix patterns"""
    voynich_suffixes = list(VOYNICH_PATTERNS['suffixes'].keys())
    lang_suffixes = lang_data['common_suffixes']
    
    # Check for length similarity
    voynich_suffix_lens = [len(s) for s in voynich_suffixes]
    lang_suffix_lens = [len(s) for s in lang_suffixes]
    
    avg_voynich = sum(voynich_suffix_lens) / len(voynich_suffix_lens)
    avg_lang = sum(lang_suffix_lens) / len(lang_suffix_lens)
    
    len_match = 1.0 - min(abs(avg_voynich - avg_lang) / 3.0, 1.0)
    
    # Check for similar ending patterns
    voynich_final_chars = set(s[-1] for s in voynich_suffixes if s)
    lang_final_chars = set(s[-1] for s in lang_suffixes if s)
    
    # Simple Jaccard-like comparison won't work across scripts, so use structural metrics
    
    return {
        'avg_suffix_length_voynich': avg_voynich,
        'avg_suffix_length_lang': avg_lang,
        'length_match_score': len_match,
        'num_voynich_suffixes': len(voynich_suffixes),
        'num_lang_suffixes': len(lang_suffixes),
    }

def test_phonetic_mapping(lang_name, words):
    """Create and test a phonetic mapping for this language"""
    # Get Voynich character frequencies
    all_chars = ''.join(words)
    char_freq = Counter(all_chars)
    total = sum(char_freq.values())
    sorted_chars = [c for c, _ in sorted(char_freq.items(), key=lambda x: -x[1])]
    
    # Target language common letters (approximation)
    lang_letters = {
        'Turkish': 'aeiınorulmkdybşçğüstz',
        'Finnish': 'aitenslokumärvjhpyd',
        'Hungarian': 'aetlnskomirgyzbvdjéá',
        'Basque': 'aeikonrtuzsbdglmphj',
        'Georgian': 'აეირნოსთმლკდბგვზხც',  # Georgian script
    }
    
    target = lang_letters.get(lang_name, 'aeiounrtslmkdpbgfvhz')
    
    # Create frequency-based mapping
    mapping = {}
    for i, vchar in enumerate(sorted_chars[:len(target)]):
        if i < len(target):
            mapping[vchar] = target[i]
    
    # Apply to sample words
    sample = words[:100]
    decoded = []
    for word in sample:
        d = ''.join(mapping.get(c, c) for c in word)
        decoded.append(d)
    
    return {
        'mapping_sample': dict(list(mapping.items())[:10]),
        'decoded_sample': decoded[:10],
    }

def calculate_ngram_similarity(words, lang_name):
    """Compare bigram patterns"""
    # Get Voynich bigrams
    all_text = ''.join(words)
    voynich_bigrams = Counter([all_text[i:i+2] for i in range(len(all_text)-1)])
    
    # Normalize
    total = sum(voynich_bigrams.values())
    voynich_probs = {k: v/total for k, v in voynich_bigrams.items()}
    
    # Compare entropy
    entropy = -sum(p * math.log2(p) for p in voynich_probs.values() if p > 0)
    
    # Expected entropy ranges for each language (approximation)
    expected_entropy = {
        'Turkish': 7.5,
        'Finnish': 7.8,
        'Hungarian': 7.6,
        'Basque': 7.2,
        'Georgian': 7.4,
    }
    
    target = expected_entropy.get(lang_name, 7.5)
    diff = abs(entropy - target)
    similarity = max(0, 1.0 - diff/3.0)
    
    return {
        'voynich_bigram_entropy': entropy,
        'expected_entropy': target,
        'similarity': similarity,
    }

def main():
    print("=" * 70)
    print("TRACK 1: AGGLUTINATIVE LANGUAGE COMPARISON")
    print("=" * 70)
    
    words = load_voynich_words()
    print(f"\nLoaded {len(words)} Voynich words")
    
    results = {
        'languages': [],
        'voynich_baseline': VOYNICH_PATTERNS,
    }
    
    for lang_name, lang_data in LANGUAGE_DATA.items():
        print(f"\n{'='*50}")
        print(f"Analyzing: {lang_name}")
        print(f"{'='*50}")
        
        # Calculate scores
        case_sim = calculate_case_similarity(lang_name, lang_data)
        suffix_analysis = analyze_suffix_patterns(lang_name, lang_data)
        phonetic = test_phonetic_mapping(lang_name, words)
        ngram = calculate_ngram_similarity(words, lang_name)
        
        # Word length match
        len_diff = abs(lang_data['avg_word_length'] - VOYNICH_PATTERNS['avg_word_length'])
        word_len_score = max(0, 1.0 - len_diff/5.0)
        
        # Overall score
        overall = (
            case_sim * 0.35 +
            suffix_analysis['length_match_score'] * 0.20 +
            word_len_score * 0.25 +
            ngram['similarity'] * 0.20
        )
        
        lang_result = {
            'name': lang_name,
            'case_similarity': round(case_sim, 3),
            'suffix_match': round(suffix_analysis['length_match_score'], 3),
            'word_length_match': round(word_len_score, 3),
            'ngram_similarity': round(ngram['similarity'], 3),
            'overall_score': round(overall, 3),
            'num_cases': lang_data['num_cases'],
            'has_articles': lang_data['has_articles'],
            'vowel_harmony': lang_data['vowel_harmony'],
            'phonetic_sample': phonetic['decoded_sample'][:5],
            'notes': [],
        }
        
        # Add notes
        if lang_data['has_articles'] == VOYNICH_PATTERNS['has_article_like_prefix']:
            lang_result['notes'].append('Article system matches')
        if case_sim > 0.7:
            lang_result['notes'].append('Strong case system match')
        if lang_data['vowel_harmony']:
            lang_result['notes'].append('Vowel harmony could explain patterns')
        if word_len_score > 0.7:
            lang_result['notes'].append('Word length closely matches')
        
        results['languages'].append(lang_result)
        
        print(f"  Case similarity: {case_sim:.1%}")
        print(f"  Suffix match: {suffix_analysis['length_match_score']:.1%}")
        print(f"  Word length match: {word_len_score:.1%}")
        print(f"  N-gram similarity: {ngram['similarity']:.1%}")
        print(f"  OVERALL SCORE: {overall:.1%}")
        print(f"  Notes: {', '.join(lang_result['notes']) or 'None'}")
    
    # Sort by overall score
    results['languages'].sort(key=lambda x: -x['overall_score'])
    results['top_candidate'] = results['languages'][0]['name']
    results['confidence'] = results['languages'][0]['overall_score']
    
    print("\n" + "=" * 70)
    print("FINAL RANKINGS")
    print("=" * 70)
    
    for i, lang in enumerate(results['languages'], 1):
        print(f"{i}. {lang['name']:12} - Score: {lang['overall_score']:.1%}")
    
    print(f"\nTop candidate: {results['top_candidate']}")
    print(f"Confidence: {results['confidence']:.1%}")
    
    # Save results
    Path('results').mkdir(exist_ok=True)
    with open('results/language_scores.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save case mapping
    case_mapping = {
        'voynich_suffixes': VOYNICH_PATTERNS['suffixes'],
        'best_matches': {}
    }
    for suffix, info in VOYNICH_PATTERNS['suffixes'].items():
        case_mapping['best_matches'][suffix] = {
            'voynich_function': info['likely_function'],
            'frequency': info['freq'],
            'possible_matches': []
        }
        for lang_name, lang_data in LANGUAGE_DATA.items():
            for case_name, ending in lang_data['case_endings'].items():
                if info['likely_function'].split('_')[0] in case_name.lower():
                    case_mapping['best_matches'][suffix]['possible_matches'].append({
                        'language': lang_name,
                        'case': case_name,
                        'ending': ending,
                    })
    
    with open('results/case_mapping.json', 'w') as f:
        json.dump(case_mapping, f, indent=2)
    
    # Generate report
    report = f"""# Track 1: Agglutinative Language Comparison Report

## Summary

Analyzed Voynich grammatical patterns against 5 agglutinative languages:
Turkish, Finnish, Hungarian, Basque, and Georgian.

## Rankings

| Rank | Language | Score | Key Matches |
|------|----------|-------|-------------|
"""
    for i, lang in enumerate(results['languages'], 1):
        notes = ', '.join(lang['notes'][:2]) if lang['notes'] else 'None'
        report += f"| {i} | {lang['name']} | {lang['overall_score']:.1%} | {notes} |\n"
    
    report += f"""
## Top Candidate: {results['top_candidate']}

Confidence: {results['confidence']:.1%}

## Key Findings

1. **Case System**: Voynich has ~8 case-like endings, most similar to Basque (12) and Georgian (7)

2. **Article Pattern**: The '4o-' prefix appears in 12.9% of words, suggesting a definite article
   - Hungarian has articles (suffix-based)
   - Basque has suffix articles
   - Turkish, Finnish, Georgian have no articles

3. **Word Length**: Voynich avg 3.91 chars
   - Georgian closest at 5.0
   - Finnish highest at 7.5
   - This difference may indicate abbreviation in Voynich

4. **Suffix Structure**: Voynich suffixes are short (1-2 chars), similar to Georgian and Basque

## Recommendations

1. Focus deeper analysis on top 2-3 candidates
2. Look for specific vocabulary matches (botanical terms)
3. Test phonetic mappings more thoroughly
4. Compare with historical forms of these languages (15th century)

## Files Generated

- results/language_scores.json - Full scoring data
- results/case_mapping.json - Case ending comparisons
"""
    
    with open('results/language_comparison_report.md', 'w') as f:
        f.write(report)
    
    print("\nResults saved to results/")
    print("  - language_scores.json")
    print("  - case_mapping.json")
    print("  - language_comparison_report.md")

if __name__ == '__main__':
    main()





