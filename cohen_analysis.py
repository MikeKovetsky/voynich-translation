#!/usr/bin/env python3
"""Analyze "Cohen" pattern in the Voynich Manuscript."""

import re
import json
from collections import Counter, defaultdict
from pathlib import Path


SECTIONS = {
    'botanical': list(range(1, 67)),
    'astronomical': list(range(67, 74)),
    'biological': list(range(75, 85)),
    'cosmological': list(range(85, 87)),
    'pharmaceutical': list(range(87, 103)),
    'recipes': list(range(103, 117))
}

COHEN_PATTERNS = [
    r'q?o?k[oa]?[ie]*[ia]*n',
    r'[yl]?k[ae]?i+n',
    r'ch[eo]?k[ae]?i+n',
    r'sh[eo]?k[ae]?i+n',
    r's?k[ae]?i+n',
    r'[ao]l?k[ae]?i+n',
]


def get_skeleton(word):
    vowels = set('aeiouy')
    return ''.join(c for c in word.lower() if c not in vowels)


def is_cohen_variant(word):
    skeleton = get_skeleton(word)
    if 'kn' in skeleton or 'cn' in skeleton:
        return True
    clean = re.sub(r'[^a-z]', '', word.lower())
    for pattern in COHEN_PATTERNS:
        if re.search(pattern, clean):
            return True
    return False


def parse_folio(line):
    match = re.match(r'<f(\d+)', line)
    if match:
        folio = match.group(1)
        return int(re.sub(r'[^\d]', '', folio)) if folio.isdigit() else int(re.sub(r'[^\d]', '', folio))
    return None


def get_section(folio_num):
    if folio_num is None:
        return 'unknown'
    for section, folios in SECTIONS.items():
        if folio_num in folios:
            return section
    return 'other'


def parse_line(text):
    text = re.sub(r'[!?]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    words = re.split(r'[.,\-=]', text)
    return [w.strip() for w in words if w.strip() and re.match(r'^[a-z]+$', w.strip())]


def analyze_position(word, words):
    if not words:
        return 'unknown'
    idx = None
    for i, w in enumerate(words):
        if w == word:
            idx = i
            break
    if idx is None:
        return 'unknown'
    if idx == 0:
        return 'line_start'
    elif idx == len(words) - 1:
        return 'line_end'
    else:
        return 'line_middle'


def load_transcription(path):
    lines = []
    current_folio = None
    current_folio_num = None
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            
            if line.startswith('<f') and '>' in line:
                folio_match = re.match(r'<f(\d+[rv]?)\.?', line)
                if folio_match:
                    current_folio = folio_match.group(1)
                    current_folio_num = int(re.sub(r'[^\d]', '', current_folio))
            
            if '\t' in line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    header, text = parts
                    folio_match = re.match(r'<f(\d+[rv]?)\.(\d+)', header)
                    if folio_match:
                        folio = folio_match.group(1)
                        line_num = folio_match.group(2)
                        folio_num = int(re.sub(r'[^\d]', '', folio))
                        
                        is_para_start = '=P' in header or '@P' in header
                        transcriber = None
                        trans_match = re.search(r';([A-Za-z])>', header)
                        if trans_match:
                            transcriber = trans_match.group(1)
                        
                        lines.append({
                            'folio': folio,
                            'folio_num': folio_num,
                            'line_num': line_num,
                            'text': text,
                            'transcriber': transcriber,
                            'is_para_start': is_para_start,
                            'header': header
                        })
    
    return lines


def find_cohen_variants(lines):
    variants = defaultdict(lambda: {'count': 0, 'positions': [], 'contexts': []})
    all_occurrences = []
    
    for line_data in lines:
        text = line_data['text']
        words = parse_line(text)
        
        for i, word in enumerate(words):
            if is_cohen_variant(word):
                clean_word = word.lower()
                
                position = 'line_middle'
                if i == 0:
                    position = 'line_start'
                elif i == len(words) - 1:
                    position = 'line_end'
                
                before = words[i-1] if i > 0 else None
                after = words[i+1] if i < len(words) - 1 else None
                
                variants[clean_word]['count'] += 1
                variants[clean_word]['positions'].append({
                    'folio': line_data['folio'],
                    'line': line_data['line_num'],
                    'position': position
                })
                
                all_occurrences.append({
                    'word': clean_word,
                    'folio': line_data['folio'],
                    'folio_num': line_data['folio_num'],
                    'line_num': line_data['line_num'],
                    'position': position,
                    'word_before': before,
                    'word_after': after,
                    'is_para_start': line_data['is_para_start'],
                    'transcriber': line_data['transcriber']
                })
    
    return dict(variants), all_occurrences


def analyze_positions(occurrences):
    pos_counts = Counter(occ['position'] for occ in occurrences)
    return {
        'line_start': pos_counts.get('line_start', 0),
        'line_middle': pos_counts.get('line_middle', 0),
        'line_end': pos_counts.get('line_end', 0)
    }


def analyze_sections(occurrences):
    section_counts = Counter(get_section(occ['folio_num']) for occ in occurrences)
    return dict(section_counts)


def analyze_context(occurrences):
    words_before = Counter(occ['word_before'] for occ in occurrences if occ['word_before'])
    words_after = Counter(occ['word_after'] for occ in occurrences if occ['word_after'])
    
    return {
        'words_before': dict(words_before.most_common(30)),
        'words_after': dict(words_after.most_common(30))
    }


def analyze_folios(occurrences):
    folio_counts = Counter(occ['folio'] for occ in occurrences)
    return dict(folio_counts.most_common(30))


def test_signature_hypothesis(occurrences, lines):
    para_boundary_count = sum(1 for occ in occurrences if occ['is_para_start'])
    line_start_count = sum(1 for occ in occurrences if occ['position'] == 'line_start')
    line_end_count = sum(1 for occ in occurrences if occ['position'] == 'line_end')
    total = len(occurrences)
    
    folio_first_lines = set()
    folio_last_lines = defaultdict(int)
    
    for line_data in lines:
        folio = line_data['folio']
        line_num = int(line_data['line_num']) if line_data['line_num'].isdigit() else 0
        if folio not in folio_first_lines:
            folio_first_lines.add(folio)
        folio_last_lines[folio] = max(folio_last_lines[folio], line_num)
    
    page_boundary_count = 0
    for occ in occurrences:
        folio = occ['folio']
        line_num = int(occ['line_num']) if occ['line_num'].isdigit() else 0
        if line_num <= 1 or line_num >= folio_last_lines.get(folio, 0):
            page_boundary_count += 1
    
    para_rate = para_boundary_count / total if total > 0 else 0
    page_rate = page_boundary_count / total if total > 0 else 0
    start_rate = line_start_count / total if total > 0 else 0
    end_rate = line_end_count / total if total > 0 else 0
    
    pattern_found = []
    if para_rate > 0.15:
        pattern_found.append(f"high paragraph boundary rate ({para_rate:.1%})")
    if page_rate > 0.15:
        pattern_found.append(f"high page boundary rate ({page_rate:.1%})")
    if start_rate > 0.20:
        pattern_found.append(f"high line-start rate ({start_rate:.1%})")
    if end_rate > 0.20:
        pattern_found.append(f"high line-end rate ({end_rate:.1%})")
    
    return {
        'at_page_boundaries': page_rate > 0.15,
        'at_paragraph_boundaries': para_rate > 0.15,
        'at_line_starts': start_rate > 0.20,
        'at_line_ends': end_rate > 0.20,
        'para_boundary_count': para_boundary_count,
        'page_boundary_count': page_boundary_count,
        'line_start_count': line_start_count,
        'line_end_count': line_end_count,
        'total_occurrences': total,
        'pattern_found': '; '.join(pattern_found) if pattern_found else "no clear signature pattern"
    }


def determine_verdict(section_dist, signature, context):
    botanical = section_dist.get('botanical', 0)
    pharma = section_dist.get('pharmaceutical', 0)
    total = sum(section_dist.values())
    
    if signature['at_page_boundaries'] and signature['at_paragraph_boundaries']:
        return "SIGNATURE - strong boundary pattern suggests author attribution"
    
    if botanical / total > 0.5 if total > 0 else False:
        return "SECTION_MARKER - concentrated in botanical section, may mark herb preparations"
    
    words_before = context.get('words_before', {})
    words_after = context.get('words_after', {})
    
    common_words = {'daiin', 'ol', 'qol', 'chol', 'ar', 'or', 'shol', 'chor', 'dar', 'okar'}
    if set(list(words_before.keys())[:5]).intersection(common_words):
        return "GRAMMATICAL - appears in regular word sequences, likely meaningful word"
    
    return "UNCERTAIN - distributed throughout text, may be common word element"


def generate_report(variants, occurrences, pos_analysis, section_dist, 
                   context, folio_dist, signature, verdict):
    sorted_variants = sorted(variants.items(), key=lambda x: x[1]['count'], reverse=True)
    total = len(occurrences)
    
    report = f"""# Cohen Pattern Analysis Report

## Summary
- **Total cohen variant occurrences**: {total}
- **Unique variant forms**: {len(variants)}
- **Most common variant**: {sorted_variants[0][0] if sorted_variants else 'N/A'} ({sorted_variants[0][1]['count'] if sorted_variants else 0} occurrences)

## Variant Frequencies

| Variant | Count | Skeleton | % of Total |
|---------|-------|----------|------------|
"""
    for word, data in sorted_variants[:30]:
        pct = (data['count'] / total * 100) if total > 0 else 0
        skeleton = get_skeleton(word)
        report += f"| {word} | {data['count']} | {skeleton} | {pct:.1f}% |\n"

    report += f"""
## Positional Analysis

Cohen variants appear in lines at these positions:
- **Line start**: {pos_analysis['line_start']} ({pos_analysis['line_start']/total*100:.1f}% if total > 0)
- **Line middle**: {pos_analysis['line_middle']} ({pos_analysis['line_middle']/total*100:.1f}%)
- **Line end**: {pos_analysis['line_end']} ({pos_analysis['line_end']/total*100:.1f}%)

## Section Distribution

| Section | Count | % of Total |
|---------|-------|------------|
"""
    for section, count in sorted(section_dist.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        report += f"| {section} | {count} | {pct:.1f}% |\n"

    report += f"""
## Top Folios with Cohen Variants

| Folio | Count |
|-------|-------|
"""
    for folio, count in list(folio_dist.items())[:15]:
        report += f"| {folio} | {count} |\n"

    report += f"""
## Context Patterns

### Words appearing BEFORE cohen variants (top 20):
| Word | Count |
|------|-------|
"""
    for word, count in list(context['words_before'].items())[:20]:
        report += f"| {word} | {count} |\n"

    report += f"""
### Words appearing AFTER cohen variants (top 20):
| Word | Count |
|------|-------|
"""
    for word, count in list(context['words_after'].items())[:20]:
        report += f"| {word} | {count} |\n"

    report += f"""
## Signature Hypothesis Test

Testing whether "cohen" could be an author signature or section marker:

- **At page boundaries**: {signature['at_page_boundaries']} ({signature['page_boundary_count']} of {signature['total_occurrences']})
- **At paragraph boundaries**: {signature['at_paragraph_boundaries']} ({signature['para_boundary_count']} of {signature['total_occurrences']})
- **At line starts**: {signature['at_line_starts']} ({signature['line_start_count']} of {signature['total_occurrences']})
- **At line ends**: {signature['at_line_ends']} ({signature['line_end_count']} of {signature['total_occurrences']})

**Pattern Analysis**: {signature['pattern_found']}

## Conclusion

**Verdict**: {verdict}

### Interpretation

The "cohen" pattern (skeleton: kn) appears {total} times across the manuscript in {len(variants)} different orthographic variants. 

Key observations:
1. The most common variants ({', '.join([v[0] for v in sorted_variants[:5]])}) account for the majority of occurrences
2. Distribution across sections: {max(section_dist.items(), key=lambda x: x[1])[0] if section_dist else 'unknown'} has the highest concentration
3. Position analysis shows these words appear predominantly in {max(pos_analysis.items(), key=lambda x: x[1])[0]} position

### Hebrew "Cohen" Connection

If this truly maps to Hebrew כהן (cohen = priest):
- In medieval Jewish texts, "Cohen" often indicated priestly lineage
- Medical manuscripts by Jewish physicians sometimes noted the author's priestly status
- The high frequency suggests this is either a common grammatical element OR a significant concept

### Recommendations for Further Research

1. Cross-reference with folios containing medical/pharmaceutical content
2. Examine if "cohen" variants cluster near plant identification labels
3. Compare frequency with other hypothesized Hebrew-origin words
4. Investigate if the pattern correlates with any visual elements in illustrations
"""
    return report


def main():
    data_path = Path('data/eva_ivtff.txt')
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    print("Loading transcription...")
    lines = load_transcription(data_path)
    print(f"Loaded {len(lines)} text lines")
    
    print("Finding cohen variants...")
    variants, occurrences = find_cohen_variants(lines)
    print(f"Found {len(occurrences)} occurrences of {len(variants)} unique variants")
    
    print("Analyzing positions...")
    pos_analysis = analyze_positions(occurrences)
    
    print("Analyzing sections...")
    section_dist = analyze_sections(occurrences)
    
    print("Analyzing context...")
    context = analyze_context(occurrences)
    
    print("Analyzing folio distribution...")
    folio_dist = analyze_folios(occurrences)
    
    print("Testing signature hypothesis...")
    signature = test_signature_hypothesis(occurrences, lines)
    
    print("Determining verdict...")
    verdict = determine_verdict(section_dist, signature, context)
    
    variants_summary = {}
    for word, data in sorted(variants.items(), key=lambda x: x[1]['count'], reverse=True):
        variants_summary[word] = {
            'count': data['count'],
            'skeleton': get_skeleton(word),
            'sample_positions': data['positions'][:10]
        }
    
    results = {
        'cohen_variants': variants_summary,
        'total_occurrences': len(occurrences),
        'unique_variants': len(variants),
        'positional_analysis': pos_analysis,
        'section_distribution': section_dist,
        'folio_distribution': folio_dist,
        'context_patterns': context,
        'signature_hypothesis': signature,
        'verdict': verdict
    }
    
    json_path = results_dir / 'cohen_analysis.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Saved JSON results to {json_path}")
    
    report = generate_report(variants, occurrences, pos_analysis, section_dist,
                           context, folio_dist, signature, verdict)
    
    report_path = results_dir / 'cohen_report.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Saved report to {report_path}")
    
    print("\n" + "="*60)
    print("COHEN PATTERN ANALYSIS COMPLETE")
    print("="*60)
    print(f"Total occurrences: {len(occurrences)}")
    print(f"Unique variants: {len(variants)}")
    top5 = [f"{k}({v['count']})" for k, v in list(variants_summary.items())[:5]]
    print(f"Top 5 variants: {', '.join(top5)}")
    print(f"\nVerdict: {verdict}")


if __name__ == '__main__':
    main()



