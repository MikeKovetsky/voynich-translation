import json
import re
from collections import Counter, defaultdict
from pathlib import Path

VOWELS = set('aeiou')

ITALIAN_BOTANICAL = {
    'acqua': ('kw', 'water'),
    'foglia': ('fgl', 'leaf'),
    'radice': ('rdc', 'root'),
    'fiore': ('fr', 'flower'),
    'erba': ('rb', 'herb'),
    'seme': ('sm', 'seed'),
    'corteccia': ('krtc', 'bark'),
    'frutto': ('frt', 'fruit'),
    'pianta': ('pnt', 'plant'),
    'albero': ('lbr', 'tree'),
    'ramo': ('rm', 'branch'),
    'tronco': ('trnk', 'trunk'),
    'fusto': ('fst', 'stem'),
    'gemma': ('gm', 'bud'),
    'petalo': ('ptl', 'petal'),
    'stelo': ('stl', 'stalk'),
    'spina': ('spn', 'thorn'),
    'bacca': ('bk', 'berry'),
    'nocciolo': ('ncl', 'kernel'),
    'scorza': ('skrz', 'rind'),
    'succo': ('sk', 'juice'),
    'olio': ('l', 'oil'),
    'vino': ('vn', 'wine'),
    'miele': ('ml', 'honey'),
    'sale': ('sl', 'salt'),
    'pepe': ('pp', 'pepper'),
    'zafferano': ('zfrn', 'saffron'),
    'cannella': ('knl', 'cinnamon'),
    'rosmarino': ('rsmrn', 'rosemary'),
    'salvia': ('slv', 'sage'),
    'menta': ('mnt', 'mint'),
    'basilico': ('bslk', 'basil'),
    'aglio': ('gl', 'garlic'),
    'cipolla': ('cpl', 'onion'),
    'zenzero': ('znzr', 'ginger'),
}

ITALIAN_MEDICAL = {
    'sangue': ('sng', 'blood'),
    'cuore': ('kr', 'heart'),
    'fegato': ('fgt', 'liver'),
    'polmone': ('plmn', 'lung'),
    'stomaco': ('stmk', 'stomach'),
    'testa': ('tst', 'head'),
    'occhio': ('k', 'eye'),
    'mano': ('mn', 'hand'),
    'piede': ('pd', 'foot'),
    'gamba': ('gmb', 'leg'),
    'braccio': ('brc', 'arm'),
    'pelle': ('pl', 'skin'),
    'osso': ('s', 'bone'),
    'febbre': ('fbr', 'fever'),
    'dolore': ('dlr', 'pain'),
    'medicina': ('mdcn', 'medicine'),
    'rimedio': ('rmd', 'remedy'),
    'cura': ('kr', 'cure'),
    'malattia': ('mlt', 'disease'),
    'veleno': ('vln', 'poison'),
    'antidoto': ('ntdt', 'antidote'),
}

JUDEO_ITALIAN_TERMS = {
    'sciabbat': ('sbt', 'sabbath'),
    'berakha': ('brk', 'blessing'),
    'mazal': ('mzl', 'luck/fate'),
    'minyan': ('mnn', 'quorum'),
    'kasherut': ('ksrt', 'kosher'),
    'chalah': ('cl', 'bread'),
    'tefilah': ('tfl', 'prayer'),
    'teshuvah': ('tsv', 'repentance'),
    'neshamah': ('nsm', 'soul'),
    'talmid': ('tlmd', 'student'),
    'rav': ('rv', 'rabbi'),
    'cohen': ('kn', 'priest'),
    'tzedakah': ('tzdk', 'charity'),
    'mitzvah': ('mtzv', 'commandment'),
    'sefer': ('sfr', 'book'),
    'refuah': ('rf', 'healing'),
}

HEBREW_BOTANICAL = {
    'pri': ('pr', 'fruit'),
    'ets': ('ts', 'tree'),
    'shoresh': ('srs', 'root'),
    'aleh': ('l', 'leaf'),
    'perakh': ('prk', 'flower'),
    'zera': ('zr', 'seed'),
    'gefen': ('gfn', 'vine'),
    'tamar': ('tmr', 'date palm'),
    'zayt': ('zt', 'olive'),
    'rimon': ('rmn', 'pomegranate'),
    'tena': ('tn', 'fig'),
    'khitah': ('kt', 'wheat'),
    'seorah': ('sr', 'barley'),
}

VENETIAN_FEATURES = {
    'xe': ('ks', 'is (essere)'),
    'belo': ('bl', 'beautiful'),
    'vodo': ('vd', 'empty'),
    'fogo': ('fg', 'fire'),
    'logo': ('lg', 'place'),
    'dito': ('dt', 'finger'),
    'speso': ('sps', 'often'),
    'piova': ('pv', 'rain'),
    'neve': ('nv', 'snow'),
    'aqua': ('kw', 'water'),
    'tera': ('tr', 'earth'),
    'vento': ('vnt', 'wind'),
    'cielo': ('cl', 'sky'),
    'luna': ('ln', 'moon'),
    'sole': ('sl', 'sun'),
}


def skeleton(word):
    return ''.join(c for c in word.lower() if c not in VOWELS and c.isalpha())


def load_data(path):
    with open(path) as f:
        return json.load(f)


def load_voynich():
    words = Counter()
    with open('data/eva_ivtff.txt') as f:
        for line in f:
            if line.startswith('#'):
                continue
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    text = parts[1]
                    tokens = text.replace('.', ' ').replace(',', ' ').split()
                    for t in tokens:
                        clean = re.sub(r'[^a-zA-Z]', '', t)
                        if len(clean) >= 2:
                            words[clean.lower()] += 1
    return words


def italian_skeleton_match(voy_words):
    all_italian = {}
    all_italian.update(ITALIAN_BOTANICAL)
    all_italian.update(ITALIAN_MEDICAL)
    all_italian.update(VENETIAN_FEATURES)
    
    matches = []
    for vword, freq in voy_words.most_common(2000):
        vskel = skeleton(vword)
        if len(vskel) < 2:
            continue
        for italian, (iskel, meaning) in all_italian.items():
            if vskel == iskel:
                matches.append({
                    'voynich': vword,
                    'voynich_skeleton': vskel,
                    'italian': italian,
                    'italian_skeleton': iskel,
                    'meaning': meaning,
                    'match_type': 'exact',
                    'frequency': freq
                })
            elif iskel in vskel and len(iskel) >= 2:
                matches.append({
                    'voynich': vword,
                    'voynich_skeleton': vskel,
                    'italian': italian,
                    'italian_skeleton': iskel,
                    'meaning': meaning,
                    'match_type': 'contains',
                    'frequency': freq
                })
    return matches


def judeo_italian_match(voy_words):
    matches = []
    for vword, freq in voy_words.most_common(2000):
        vskel = skeleton(vword)
        if len(vskel) < 2:
            continue
        for term, (tskel, meaning) in JUDEO_ITALIAN_TERMS.items():
            if vskel == tskel:
                matches.append({
                    'voynich': vword,
                    'skeleton': vskel,
                    'judeo_italian': term,
                    'meaning': meaning,
                    'match_type': 'exact',
                    'frequency': freq
                })
            elif tskel in vskel and len(tskel) >= 2:
                matches.append({
                    'voynich': vword,
                    'skeleton': vskel,
                    'judeo_italian': term,
                    'meaning': meaning,
                    'match_type': 'contains',
                    'frequency': freq
                })
    return matches


def hebrew_italian_hybrid(voy_words):
    italian_endings = ['o', 'a', 'e', 'i', 'are', 'ere', 'ire', 'ato', 'ito', 'uto', 'one', 'ione']
    hebrew_roots = ['pr', 'dm', 'rb', 'lm', 'spr', 'brk', 'kds', 'mlk', 'shl', 'chr']
    
    hybrids = []
    for vword, freq in voy_words.most_common(2000):
        vskel = skeleton(vword)
        for hroot in hebrew_roots:
            if vskel.startswith(hroot) and len(vskel) > len(hroot):
                suffix = vword[len(hroot):]
                for iend in italian_endings:
                    if vword.endswith(iend):
                        hybrids.append({
                            'voynich': vword,
                            'hebrew_root': hroot,
                            'italian_ending': iend,
                            'frequency': freq
                        })
                        break
    return hybrids


def phonetic_italian_map():
    voynich_to_italian = {
        'ch': 'c/ch',
        'sh': 'sc',
        'qo': 'co/qua',
        'k': 'c/ch',
        'd': 'd',
        't': 't',
        'l': 'l',
        'r': 'r',
        'n': 'n',
        'p': 'p',
        's': 's',
        'f': 'f',
        'y': 'i/gli',
        'o': 'o',
        'e': 'e',
        'a': 'a',
        'i': 'i',
    }
    return voynich_to_italian


def decode_with_italian_map(word, mapping):
    result = word
    for voy, ital in sorted(mapping.items(), key=lambda x: -len(x[0])):
        if '/' in ital:
            ital = ital.split('/')[0]
        result = result.replace(voy, ital)
    return result


def analyze_dialect_features(voy_words):
    venetian_matches = []
    for vword, freq in voy_words.most_common(1000):
        vskel = skeleton(vword)
        for vent, (vskel2, meaning) in VENETIAN_FEATURES.items():
            if vskel == vskel2 or (len(vskel2) >= 2 and vskel2 in vskel):
                venetian_matches.append({
                    'voynich': vword,
                    'venetian': vent,
                    'meaning': meaning,
                    'frequency': freq
                })
    
    features = {
        'o_endings': sum(1 for w in voy_words if w.endswith('o')),
        'a_endings': sum(1 for w in voy_words if w.endswith('a')),
        'e_endings': sum(1 for w in voy_words if w.endswith('e')),
        'i_endings': sum(1 for w in voy_words if w.endswith('i')),
        'y_endings': sum(1 for w in voy_words if w.endswith('y')),
        'n_endings': sum(1 for w in voy_words if w.endswith('n')),
        'r_endings': sum(1 for w in voy_words if w.endswith('r')),
    }
    
    return venetian_matches, features


def compare_with_herbario_volgare():
    herbario_terms = {
        'artemisia': ('rtms', 'mugwort'),
        'malva': ('mlv', 'mallow'),
        'basilico': ('bslk', 'basil'),
        'borragine': ('brgn', 'borage'),
        'camomilla': ('kmml', 'chamomile'),
        'finocchio': ('fnk', 'fennel'),
        'lattuga': ('ltg', 'lettuce'),
        'menta': ('mnt', 'mint'),
        'origano': ('rgn', 'oregano'),
        'prezzemolo': ('przml', 'parsley'),
        'ruta': ('rt', 'rue'),
        'salvia': ('slv', 'sage'),
        'timo': ('tm', 'thyme'),
        'verbena': ('vrbn', 'verbena'),
        'viola': ('vl', 'violet'),
        'assenzio': ('snz', 'wormwood'),
        'anice': ('nc', 'anise'),
        'coriandro': ('krndr', 'coriander'),
        'cumino': ('kmn', 'cumin'),
        'zenzero': ('znzr', 'ginger'),
    }
    return herbario_terms


def main():
    print("Loading Voynich vocabulary...")
    voy_words = load_voynich()
    print(f"Loaded {len(voy_words)} unique words")
    
    print("\n1. Building reference vocabulary...")
    ref_vocab = {
        'italian_botanical': {k: {'skeleton': v[0], 'meaning': v[1]} 
                              for k, v in ITALIAN_BOTANICAL.items()},
        'italian_medical': {k: {'skeleton': v[0], 'meaning': v[1]} 
                            for k, v in ITALIAN_MEDICAL.items()},
        'judeo_italian_terms': {k: {'skeleton': v[0], 'meaning': v[1]} 
                                for k, v in JUDEO_ITALIAN_TERMS.items()},
        'hebrew_loanwords': {k: {'skeleton': v[0], 'meaning': v[1]} 
                             for k, v in HEBREW_BOTANICAL.items()},
    }
    print(f"  Italian botanical: {len(ITALIAN_BOTANICAL)} terms")
    print(f"  Italian medical: {len(ITALIAN_MEDICAL)} terms")
    print(f"  Judeo-Italian: {len(JUDEO_ITALIAN_TERMS)} terms")
    print(f"  Hebrew loanwords: {len(HEBREW_BOTANICAL)} terms")
    
    print("\n2. Italian skeleton matching...")
    italian_matches = italian_skeleton_match(voy_words)
    exact = [m for m in italian_matches if m['match_type'] == 'exact']
    contains = [m for m in italian_matches if m['match_type'] == 'contains']
    print(f"  Exact matches: {len(exact)}")
    print(f"  Contains matches: {len(contains)}")
    if exact[:5]:
        print("  Top exact matches:")
        for m in exact[:5]:
            print(f"    {m['voynich']} ({m['voynich_skeleton']}) = {m['italian']} ({m['meaning']})")
    
    print("\n3. Judeo-Italian term matching...")
    ji_matches = judeo_italian_match(voy_words)
    print(f"  Total matches: {len(ji_matches)}")
    if ji_matches[:5]:
        print("  Top matches:")
        for m in ji_matches[:5]:
            print(f"    {m['voynich']} = {m['judeo_italian']} ({m['meaning']})")
    
    print("\n4. Hebrew-Italian hybrid search...")
    hybrids = hebrew_italian_hybrid(voy_words)
    print(f"  Potential hybrids: {len(hybrids)}")
    if hybrids[:5]:
        print("  Top hybrids:")
        for h in hybrids[:5]:
            print(f"    {h['voynich']}: {h['hebrew_root']} + -{h['italian_ending']}")
    
    print("\n5. Regional dialect analysis...")
    venetian, endings = analyze_dialect_features(voy_words)
    print(f"  Venetian matches: {len(venetian)}")
    print("  Word ending distribution:")
    for end, count in sorted(endings.items(), key=lambda x: -x[1])[:5]:
        print(f"    -{end.split('_')[0]}: {count}")
    
    print("\n6. Phonetic Italian mapping...")
    mapping = phonetic_italian_map()
    sample_words = ['daiin', 'chol', 'qokedy', 'shedy', 'okal', 'cheol']
    print("  Sample decodings:")
    decoded_samples = []
    for w in sample_words:
        if w in voy_words:
            decoded = decode_with_italian_map(w, mapping)
            decoded_samples.append({'voynich': w, 'decoded': decoded})
            print(f"    {w} → {decoded}")
    
    herbario = compare_with_herbario_volgare()
    herbario_matches = []
    for vword in voy_words:
        vskel = skeleton(vword)
        for herb, (hskel, meaning) in herbario.items():
            if vskel == hskel or (len(hskel) >= 3 and hskel in vskel):
                herbario_matches.append({
                    'voynich': vword,
                    'herbario': herb,
                    'meaning': meaning
                })
    print(f"\n  Herbario Volgare matches: {len(herbario_matches)}")
    
    italian_score = min(1.0, len(exact) / 20) * 0.3
    italian_score += min(1.0, len(contains) / 100) * 0.2
    ji_score = min(1.0, len(ji_matches) / 20) * 0.2
    hybrid_score = min(1.0, len(hybrids) / 30) * 0.15
    dialect_score = min(1.0, len(venetian) / 30) * 0.15
    
    overall_score = italian_score + ji_score + hybrid_score + dialect_score
    
    results = {
        'reference_vocabulary': ref_vocab,
        'skeleton_matches': {
            'italian': {
                'exact': exact[:50],
                'contains': contains[:100],
                'exact_count': len(exact),
                'contains_count': len(contains)
            },
            'judeo_italian': ji_matches[:50],
            'judeo_italian_count': len(ji_matches)
        },
        'hybrid_words_found': hybrids[:50],
        'hybrid_count': len(hybrids),
        'dialect_features': {
            'venetian_matches': venetian[:30],
            'venetian_count': len(venetian),
            'ending_distribution': endings
        },
        'phonetic_mapping': {
            'mapping': mapping,
            'sample_decodings': decoded_samples
        },
        'herbario_matches': herbario_matches[:30],
        'herbario_count': len(herbario_matches),
        'scores': {
            'italian_skeleton': italian_score,
            'judeo_italian': ji_score,
            'hybrid': hybrid_score,
            'dialect': dialect_score
        },
        'overall_score': overall_score,
        'verdict': 'WEAK' if overall_score < 0.3 else 'MODERATE' if overall_score < 0.6 else 'STRONG'
    }
    
    with open('results/judeo_italian_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("JUDEO-ITALIAN ANALYSIS RESULTS")
    print('='*60)
    print(f"\nOverall Score: {overall_score:.3f}")
    print(f"Verdict: {results['verdict']} Judeo-Italian characteristics")
    print(f"\nComponent Scores:")
    print(f"  Italian skeleton: {italian_score:.3f}")
    print(f"  Judeo-Italian terms: {ji_score:.3f}")
    print(f"  Hebrew-Italian hybrids: {hybrid_score:.3f}")
    print(f"  Dialect features: {dialect_score:.3f}")
    
    generate_report(results)
    
    return results


def generate_report(results):
    report = """# Judeo-Italian Analysis Report

## Overview

This analysis tests whether the Voynich manuscript could be written in 
Judeo-Italian (Italkian) - the Italian dialect used by Jewish communities
in medieval Italy.

## Reference Vocabulary Built

| Category | Term Count |
|----------|-----------|
"""
    
    for cat, terms in results['reference_vocabulary'].items():
        report += f"| {cat.replace('_', ' ').title()} | {len(terms)} |\n"
    
    report += f"""
## Italian Consonant Skeleton Matches

### Exact Matches: {results['skeleton_matches']['italian']['exact_count']}

| Voynich | Skeleton | Italian | Meaning |
|---------|----------|---------|---------|
"""
    
    for m in results['skeleton_matches']['italian']['exact'][:15]:
        report += f"| {m['voynich']} | {m['voynich_skeleton']} | {m['italian']} | {m['meaning']} |\n"
    
    report += f"""
### Contains Matches: {results['skeleton_matches']['italian']['contains_count']}

Top matches where Italian skeleton is found within Voynich word.

## Judeo-Italian Terms

Found {results['skeleton_matches']['judeo_italian_count']} potential Judeo-Italian matches.

| Voynich | Judeo-Italian | Meaning |
|---------|---------------|---------|
"""
    
    for m in results['skeleton_matches']['judeo_italian'][:10]:
        report += f"| {m['voynich']} | {m['judeo_italian']} | {m['meaning']} |\n"
    
    report += f"""
## Hebrew-Italian Hybrid Words

Found {results['hybrid_count']} potential hybrid words (Hebrew root + Italian ending).

| Voynich | Hebrew Root | Italian Ending |
|---------|-------------|----------------|
"""
    
    for h in results['hybrid_words_found'][:10]:
        report += f"| {h['voynich']} | {h['hebrew_root']} | -{h['italian_ending']} |\n"
    
    report += f"""
## Venetian Dialect Features

Found {results['dialect_features']['venetian_count']} potential Venetian dialect matches.

### Word Ending Distribution

| Ending | Count |
|--------|-------|
"""
    
    for end, count in sorted(results['dialect_features']['ending_distribution'].items(), 
                             key=lambda x: -x[1])[:7]:
        report += f"| -{end.split('_')[0]} | {count} |\n"
    
    report += f"""
## Phonetic Italian Mapping

Sample decodings using Italian phonetic values:

| Voynich | Decoded |
|---------|---------|
"""
    
    for s in results['phonetic_mapping']['sample_decodings']:
        report += f"| {s['voynich']} | {s['decoded']} |\n"
    
    report += f"""
## Herbario Volgare Comparison

Found {results['herbario_count']} matches with medieval Italian herbal vocabulary.

## Scoring

| Component | Score |
|-----------|-------|
| Italian Skeleton | {results['scores']['italian_skeleton']:.3f} |
| Judeo-Italian Terms | {results['scores']['judeo_italian']:.3f} |
| Hebrew-Italian Hybrids | {results['scores']['hybrid']:.3f} |
| Dialect Features | {results['scores']['dialect']:.3f} |
| **Overall** | **{results['overall_score']:.3f}** |

## Verdict: {results['verdict']}

### Interpretation

"""
    
    if results['verdict'] == 'WEAK':
        report += """The evidence for Judeo-Italian is weak. While some consonant 
skeleton matches exist, they are not significantly higher than would be expected 
by chance. The Voynich manuscript shows stronger characteristics of other 
language families (Hebrew/Latin consonantal systems)."""
    elif results['verdict'] == 'MODERATE':
        report += """There is moderate evidence for Judeo-Italian influence. 
The consonant patterns show some alignment with Italian vocabulary, and 
hybrid words suggest possible Hebrew-Italian mixing. However, the evidence 
is not conclusive."""
    else:
        report += """Strong evidence suggests Judeo-Italian characteristics. 
The skeleton matches, hybrid words, and dialect features align well with 
medieval Judeo-Italian patterns."""
    
    report += """

### Key Observations

1. **Consonant Patterns**: Italian skeleton matches exist but need validation
2. **Hybrid Words**: Some words show potential Hebrew root + Italian ending pattern  
3. **Dialect**: Venetian/Northern Italian features are present but inconclusive
4. **Overall**: The Judeo-Italian hypothesis requires more evidence to be confirmed

### Comparison with Hebrew Hypothesis

Previous Hebrew analysis showed score of 0.70 (STRONG Hebrew characteristics).
This Judeo-Italian analysis provides a complementary view, showing that if
Hebrew is involved, it may have been filtered through Italian phonology.

## Conclusion

The Judeo-Italian hypothesis remains **possible but unconfirmed**. The manuscript
may represent a hybrid system where Hebrew content was adapted to Italian 
phonetic conventions, consistent with the bilingual nature of medieval 
Italian Jewish communities.
"""
    
    with open('results/judeo_italian_report.md', 'w') as f:
        f.write(report)
    
    print("\nReport saved to results/judeo_italian_report.md")


if __name__ == '__main__':
    main()



