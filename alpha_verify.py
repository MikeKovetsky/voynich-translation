#!/usr/bin/env python3
"""Verify Voynich alphabet - EVA and Claston character sets."""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

EVA_BASIC = set('acdefghiklmnopqrsty')
EVA_DIGRAPHS = ['cth', 'ckh', 'cph', 'cfh', 'ch', 'sh']
EVA_SPECIAL = ['aiin', 'aiiin', 'daiin', 'ain', 'iin', 'dy', 'ey', 'eey', 'eedy', 'edy']

CLASTON_TO_EVA = {
    'o': 'o', 'a': 'a', 's': 's', 'f': 'f', 'i': 'i', 'n': 'n',
    '9': 'y', '8': 'd', 'h': 'k', 'k': 't', 'e': 'l', 'y': 'r',
    'c': 'e', '4': 'q', 'g': 'p', 'p': 'm'
}

CLASTON_DIGRAPHS = {
    '1': 'ch', '2': 'sh', 'K': 'ckh', 'H': 'ckh',
    '1h': 'cth', '1g': 'cph', 'fh': 'cfh',
    'am': 'aiin', 'an': 'ain', 'M': 'iin',
    'oe': 'ol', 'oy': 'or', 'ae': 'al', 'ay': 'ar', 'iy': 'ir',
    '89': 'dy', 'c9': 'ey', 'cc9': 'eey', 'cc89': 'eedy', 'c89': 'edy'
}

CLASTON_EXTENDED = {
    'C': 'e (variant)', 'A': 'a (variant)', 'I': 'i (variant)',
    'N': 'n (final)', 'Z': 'n (final variant)', 'M': 'iin',
    '3': 'g?', '5': 'b?', '7': 'j?', '6': 'x?',
    'j': 'p (variant)', 'J': 'f (variant)', 'G': 'p (tall)',
    'F': 'f (tall)', 'L': 't (variant)', 'W': 'w?',
    'd': 'd (variant in claston)', 'm': 'm/ending', 'z': 'z (word-end)',
    'u': 'u (rare)', 'x': 'x (rare)', 'E': 'e (variant)'
}


def extract_eva_chars(filepath):
    """Extract unique characters and frequencies from EVA transcription."""
    chars = Counter()
    words = []
    digraph_counts = defaultdict(int)
    position_stats = defaultdict(lambda: {'initial': 0, 'medial': 0, 'final': 0})
    weirdos = Counter()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.startswith('<f0'):
                continue
            
            match = re.match(r'<f\d+[rv](?:\.\d+)?[^>]*>\s*(.+)', line)
            if not match:
                continue
            
            text = match.group(1)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\{[^}]+\}', '', text)
            
            tokens = re.split(r'[.,\-=\s]+', text)
            for token in tokens:
                token = re.sub(r'[!?%\*\[\]]', '', token)
                if not token:
                    continue
                
                words.append(token)
                
                for digraph in EVA_DIGRAPHS:
                    count = token.count(digraph)
                    if count:
                        digraph_counts[digraph] += count
                
                for c in token:
                    if c.isupper():
                        weirdos[c] += 1
                    elif c.islower():
                        chars[c] += 1
                
                clean = token.lower()
                if len(clean) >= 1:
                    position_stats[clean[0]]['initial'] += 1
                    if len(clean) >= 2:
                        position_stats[clean[-1]]['final'] += 1
                        for mc in clean[1:-1]:
                            position_stats[mc]['medial'] += 1
                    else:
                        position_stats[clean[0]]['final'] += 1
    
    return {
        'chars': dict(chars),
        'digraphs': dict(digraph_counts),
        'positions': {k: dict(v) for k, v in position_stats.items()},
        'weirdos': dict(weirdos),
        'total_words': len(words),
        'unique_words': len(set(words))
    }


def extract_claston_chars(filepath):
    """Extract unique characters and frequencies from Claston transcription."""
    chars = Counter()
    words = []
    special_chars = Counter()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'<[^>]+>(.+)', line)
            if not match:
                continue
            
            text = match.group(1)
            tokens = re.split(r'[.,\-=\s]+', text)
            
            for token in tokens:
                token = re.sub(r'[!?%\*\[\]<>]', '', token)
                if not token:
                    continue
                
                words.append(token)
                
                for c in token:
                    if c in CLASTON_TO_EVA or c in '0123456789':
                        chars[c] += 1
                    elif c.isalpha():
                        chars[c] += 1
                    else:
                        special_chars[c] += 1
    
    return {
        'chars': dict(chars),
        'special': dict(special_chars),
        'total_words': len(words),
        'unique_words': len(set(words))
    }


def verify_eva_alphabet(eva_chars):
    """Verify EVA characters against official alphabet."""
    found = set(eva_chars['chars'].keys())
    expected = EVA_BASIC
    
    correct = found & expected
    unknown = found - expected - set('uvwxz')
    missing = expected - found
    
    return {
        'found': sorted(found),
        'expected': sorted(expected),
        'correct': sorted(correct),
        'unknown': sorted(unknown),
        'missing': sorted(missing),
        'all_basic_present': len(missing) == 0
    }


def verify_claston_mapping(claston_chars, eva_chars):
    """Verify Claston to EVA character mapping."""
    verified = []
    issues = []
    unmapped = []
    extended = []
    
    for claston_char, count in claston_chars['chars'].items():
        if claston_char in CLASTON_TO_EVA:
            eva_equiv = CLASTON_TO_EVA[claston_char]
            if eva_equiv in eva_chars['chars']:
                verified.append({
                    'claston': claston_char,
                    'eva': eva_equiv,
                    'claston_count': count,
                    'eva_count': eva_chars['chars'].get(eva_equiv, 0)
                })
            else:
                issues.append({
                    'claston': claston_char,
                    'expected_eva': eva_equiv,
                    'issue': 'EVA equivalent not found in data'
                })
        elif claston_char in CLASTON_DIGRAPHS:
            verified.append({
                'claston': claston_char,
                'eva': CLASTON_DIGRAPHS[claston_char],
                'type': 'digraph',
                'count': count
            })
        elif claston_char in CLASTON_EXTENDED:
            extended.append({
                'char': claston_char,
                'likely_eva': CLASTON_EXTENDED[claston_char],
                'count': count
            })
        else:
            unmapped.append({
                'char': claston_char,
                'count': count
            })
    
    return {
        'verified': verified,
        'issues': issues,
        'extended': extended,
        'unmapped': unmapped,
        'verified_count': len(verified),
        'issue_count': len(issues),
        'extended_count': len(extended),
        'unmapped_count': len(unmapped)
    }


def analyze_digraphs(eva_chars):
    """Analyze digraph occurrences and parsing."""
    analysis = {}
    
    for digraph in EVA_DIGRAPHS:
        count = eva_chars['digraphs'].get(digraph, 0)
        analysis[digraph] = {
            'count': count,
            'type': 'gallows' if digraph in ['cth', 'ckh', 'cph', 'cfh'] else 'basic'
        }
    
    parsing_issues = []
    ambiguous = []
    for d1 in EVA_DIGRAPHS:
        for d2 in EVA_DIGRAPHS:
            if d1 != d2 and d1 in d2:
                ambiguous.append(f'{d1} is substring of {d2}')
    
    return {
        'digraph_counts': analysis,
        'parsing_notes': ambiguous,
        'parsing_issues': parsing_issues
    }


def analyze_rare_chars(eva_chars, threshold=100):
    """Find rare characters that might be errors or variants."""
    rare = []
    
    for char, count in eva_chars['chars'].items():
        if count < threshold:
            rare.append({
                'char': char,
                'count': count,
                'in_basic': char in EVA_BASIC,
                'note': 'variant' if char not in EVA_BASIC else 'low frequency'
            })
    
    for char, count in eva_chars['weirdos'].items():
        rare.append({
            'char': char,
            'count': count,
            'type': 'weirdo',
            'note': 'uppercase/special marker'
        })
    
    return sorted(rare, key=lambda x: x['count'])


def generate_report(results):
    """Generate markdown report."""
    lines = ['# Voynich Alphabet Verification Report\n']
    
    lines.append('## EVA Character Analysis\n')
    lines.append(f"- Total unique characters: {len(results['eva']['chars'])}")
    lines.append(f"- Total words analyzed: {results['eva']['total_words']}")
    lines.append(f"- Unique words: {results['eva']['unique_words']}\n")
    
    lines.append('### Character Frequencies (top 20)\n')
    sorted_chars = sorted(results['eva']['chars'].items(), key=lambda x: -x[1])[:20]
    for char, count in sorted_chars:
        lines.append(f"- `{char}`: {count:,}")
    
    lines.append('\n### Digraph Occurrences\n')
    for digraph, data in results['digraph_analysis']['digraph_counts'].items():
        lines.append(f"- `{digraph}` ({data['type']}): {data['count']:,}")
    
    lines.append('\n## Claston Character Analysis\n')
    lines.append(f"- Total unique characters: {len(results['claston']['chars'])}")
    lines.append(f"- Total words: {results['claston']['total_words']}")
    
    lines.append('\n## EVA Alphabet Verification\n')
    v = results['eva_verification']
    lines.append(f"- All basic EVA present: {'✓' if v['all_basic_present'] else '✗'}")
    lines.append(f"- Correct characters: {len(v['correct'])}")
    if v['missing']:
        lines.append(f"- Missing from data: {', '.join(v['missing'])}")
    if v['unknown']:
        lines.append(f"- Unknown characters: {', '.join(v['unknown'])}")
    
    lines.append('\n## Claston-EVA Mapping Verification\n')
    m = results['mapping_verification']
    lines.append(f"- Verified basic mappings: {m['verified_count']}")
    lines.append(f"- Extended/variant chars: {m['extended_count']}")
    lines.append(f"- Issues found: {m['issue_count']}")
    lines.append(f"- Truly unmapped: {m['unmapped_count']}")
    
    if m['extended']:
        lines.append('\n### Extended Claston Characters (variants)\n')
        for item in sorted(m['extended'], key=lambda x: -x['count'])[:15]:
            lines.append(f"- `{item['char']}` → {item['likely_eva']}: {item['count']:,}")
    
    if m['unmapped']:
        lines.append('\n### Unmapped Claston Characters\n')
        for item in sorted(m['unmapped'], key=lambda x: -x['count'])[:20]:
            lines.append(f"- `{item['char']}`: {item['count']:,}")
    
    lines.append('\n## Weirdo Characters\n')
    if results['eva']['weirdos']:
        for char, count in sorted(results['eva']['weirdos'].items(), key=lambda x: -x[1]):
            lines.append(f"- `{char}`: {count:,}")
    else:
        lines.append('No weirdo characters found.')
    
    lines.append('\n## Rare Characters (<100 occurrences)\n')
    for item in results['rare_chars'][:15]:
        char_type = item.get('type', 'standard')
        lines.append(f"- `{item['char']}` ({char_type}): {item['count']} - {item['note']}")
    
    lines.append('\n## Position Distribution (sample)\n')
    lines.append('Key characters and their position tendencies:\n')
    for char in ['o', 'a', 'd', 'y', 'k', 'q', 'ch']:
        if char in results['eva']['positions']:
            pos = results['eva']['positions'][char]
            total = pos['initial'] + pos['medial'] + pos['final']
            if total > 0:
                lines.append(f"- `{char}`: initial {pos['initial']/total*100:.1f}%, medial {pos['medial']/total*100:.1f}%, final {pos['final']/total*100:.1f}%")
    
    lines.append('\n## Recommendations\n')
    if results['mapping_verification']['unmapped']:
        lines.append('- Review unmapped Claston characters for completeness')
    if results['eva_verification']['unknown']:
        lines.append('- Investigate unknown characters in EVA data')
    if not results['eva_verification']['all_basic_present']:
        lines.append('- Check for missing EVA basic characters')
    lines.append('- Ensure digraph parsing order (longer first: cth before ch)')
    
    return '\n'.join(lines)


def main():
    eva_file = Path('data/eva_ivtff.txt')
    claston_file = Path('voynich_raw.txt')
    
    print("Extracting EVA characters...")
    eva_data = extract_eva_chars(eva_file)
    
    print("Extracting Claston characters...")
    claston_data = extract_claston_chars(claston_file)
    
    print("Verifying EVA alphabet...")
    eva_verify = verify_eva_alphabet(eva_data)
    
    print("Verifying Claston mapping...")
    mapping_verify = verify_claston_mapping(claston_data, eva_data)
    
    print("Analyzing digraphs...")
    digraph_analysis = analyze_digraphs(eva_data)
    
    print("Finding rare characters...")
    rare = analyze_rare_chars(eva_data)
    
    results = {
        'eva': eva_data,
        'claston': claston_data,
        'eva_verification': eva_verify,
        'mapping_verification': mapping_verify,
        'digraph_analysis': digraph_analysis,
        'rare_chars': rare
    }
    
    print("\nSaving results...")
    with open('results/alphabet_verification.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    report = generate_report(results)
    with open('results/alphabet_report.md', 'w') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    print(f"EVA unique chars: {len(eva_data['chars'])}")
    print(f"Claston unique chars: {len(claston_data['chars'])}")
    print(f"All basic EVA present: {eva_verify['all_basic_present']}")
    print(f"Mapping issues: {mapping_verify['issue_count']}")
    print(f"Weirdos found: {len(eva_data['weirdos'])}")
    print(f"\nTop 10 EVA chars: {sorted(eva_data['chars'].items(), key=lambda x: -x[1])[:10]}")
    print(f"\nResults saved to results/alphabet_verification.json")
    print(f"Report saved to results/alphabet_report.md")


if __name__ == '__main__':
    main()
