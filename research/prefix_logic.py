import json
import re
import collections
import os

def load_parsed_data(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_text_with_meta(path):
    meta_stream = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ';H>' not in line:
                continue
            is_para_start = '<f' in line or '<P' in line
            is_line_start = True
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'[.,!=]', ' ', clean_line)
            clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
            words = clean_line.split()
            for i, w in enumerate(words):
                meta_stream.append({
                    "is_line_start": is_line_start and (i == 0),
                    "is_para_start": is_para_start and (i == 0)
                })
    return meta_stream

def analyze_prefixes(parsed_data, meta_stream):
    if len(parsed_data) != len(meta_stream):
        limit = min(len(parsed_data), len(meta_stream))
        parsed_data = parsed_data[:limit]
        meta_stream = meta_stream[:limit]

    stats = {
        "qo_pos": {"total": 0, "line_start": 0},
        "y_pos": {"total": 0, "line_start": 0},
        "d_pos": {"total": 0, "line_start": 0},
        "o_pos": {"total": 0, "line_start": 0},
        "s_pos": {"total": 0, "line_start": 0},
        "y_context": collections.defaultdict(int),
        "d_context": collections.defaultdict(int),
        "root_forms": collections.defaultdict(set),
        "root_counts": collections.Counter()
    }

    for i, (entry, meta) in enumerate(zip(parsed_data, meta_stream)):
        prefixes = entry.get('prefix', [])
        root = entry.get('root', '')
        suffixes = entry.get('suffix', [])
        
        stats['root_counts'][root] += 1
        
        form_type = []
        if not prefixes and not suffixes: form_type.append('bare')
        if prefixes: form_type.append('prefix')
        if suffixes: form_type.append('suffix')
        stats['root_forms'][root].add(tuple(sorted(form_type)))

        # Helper to check prefix family
        def has_prefix(p_start):
            return any(p.startswith(p_start) for p in prefixes)

        if has_prefix('qo'):
            stats['qo_pos']['total'] += 1
            if meta['is_line_start']: stats['qo_pos']['line_start'] += 1

        if has_prefix('y'):
            stats['y_pos']['total'] += 1
            if meta['is_line_start']: stats['y_pos']['line_start'] += 1
            # Context check
            prev_word = parsed_data[i-1] if i > 0 else None
            next_word = parsed_data[i+1] if i < len(parsed_data)-1 else None
            if prev_word and next_word:
                p_len = len(prev_word.get('root', ''))
                n_len = len(next_word.get('root', ''))
                if p_len > 2 and n_len > 2:
                     stats['y_context']['between_long_roots'] += 1
                else:
                     stats['y_context']['between_short'] += 1

        if has_prefix('d'): # Matches d, da, dai...
            stats['d_pos']['total'] += 1
            if meta['is_line_start']: stats['d_pos']['line_start'] += 1
            
            # Check for 'aiin' relation (accounting for misparsing 'daiin' -> 'dai'+'in')
            # If original is 'daiin', it counts.
            if entry.get('original') == 'daiin':
                stats['d_context']['is_daiin'] += 1
            
            # Check near 'air'
            window = parsed_data[max(0, i-3):min(len(parsed_data), i+4)]
            for w in window:
                if w.get('original') in ['air', 'aiir']:
                     stats['d_context']['near_air'] += 1
                     break

        if has_prefix('o'):
            stats['o_pos']['total'] += 1
            if meta['is_line_start']: stats['o_pos']['line_start'] += 1

        if has_prefix('s') or has_prefix('sh'): # 's' or 'sh'
            stats['s_pos']['total'] += 1
            if meta['is_line_start']: stats['s_pos']['line_start'] += 1

    return stats

def generate_report(stats, output_path):
    lines = []
    lines.append("# Task 154: Prefix Grammar Analysis")
    lines.append("\n## 1. Positional Analysis")
    
    def report_prefix(name, data):
        pct = (data['line_start'] / data['total'] * 100) if data['total'] else 0
        lines.append(f"### Prefix `{name}`")
        lines.append(f"- Total: {data['total']}")
        lines.append(f"- At Line Start: {data['line_start']} ({pct:.1f}%)")
        return pct

    pct_qo = report_prefix("qo- (incl qok-)", stats['qo_pos'])
    pct_y = report_prefix("y-", stats['y_pos'])
    lines.append(f"- Context: Between long roots ({stats['y_context']['between_long_roots']}) vs short ({stats['y_context']['between_short']})")
    
    pct_d = report_prefix("d- (incl dai-)", stats['d_pos'])
    lines.append(f"- Is 'daiin': {stats['d_context']['is_daiin']}")
    lines.append(f"- Near 'air': {stats['d_context']['near_air']}")
    
    pct_o = report_prefix("o-", stats['o_pos'])
    pct_s = report_prefix("s- (incl sh-)", stats['s_pos'])

    lines.append("\n## 2. Co-occurrence Matrix")
    
    common_roots = {r for r, c in stats['root_counts'].items() if c > 5}
    phobic = []
    obligatory_suffix = []
    
    for root in common_roots:
        forms = stats['root_forms'][root]
        has_prefix = any('prefix' in f for f in forms)
        if not has_prefix:
            phobic.append(root)
            
        has_bare = any('bare' in f for f in forms)
        if not has_bare:
            if all('suffix' in f for f in forms):
                obligatory_suffix.append(root)

    lines.append(f"\n- **Prefix-Phobic Roots** (Freq > 5): {len(phobic)}")
    if phobic:
        lines.append(f"  - Examples: {', '.join(sorted(list(phobic))[:10])}")
    
    lines.append(f"\n- **Suffix-Obligatory Roots** (Freq > 5): {len(obligatory_suffix)}")
    if obligatory_suffix:
        lines.append(f"  - Examples: {', '.join(sorted(list(obligatory_suffix))[:10])}")

    lines.append("\n## 3. Hypotheses")
    lines.append(f"1. **`qo-`**: **Verb Prefix / Process Marker**. ({pct_qo:.1f}% start). Likely 'To [Action]'.")
    lines.append(f"2. **`y-`**: **Conjunction ('And')**. ({pct_y:.1f}% start). Links phrases.")
    lines.append(f"3. **`d-`**: **Imperative / Preposition**. ({pct_d:.1f}% start). 'daiin' (Take Water) is a major form.")
    lines.append(f"4. **`o-`**: **Determiner / Article**. ({pct_o:.1f}% start). Very common.")
    lines.append(f"5. **`s-`**: **Relative Pronoun / Connector**. ({pct_s:.1f}% start).")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Report generated at {output_path}")

def main():
    parsed = load_parsed_data('results/parsed_text.json')
    meta = load_text_with_meta('data/eva_ivtff.txt')
    
    stats = analyze_prefixes(parsed, meta)
    generate_report(stats, 'results/prefix_grammar_report.md')

if __name__ == "__main__":
    main()
