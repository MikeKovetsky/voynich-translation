import json
import os
from collections import defaultdict

def load_dictionary(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def save_text(text, path):
    with open(path, 'w') as f:
        f.write(text)

def strip_prefixes(word):
    """
    Applies stripping rules to identify potential roots and prefixes.
    Returns a list of (prefix, root) tuples.
    """
    potential_analyses = []
    
    # Rule: qok- -> q- + ok- + ROOT
    if word.startswith('qok') and len(word) > 3:
        root = word[3:]
        potential_analyses.append(('qok-', root))
        
    # Rule: ok- -> ok- + ROOT
    # Added to capture the ok- component implied by qok-
    if word.startswith('ok') and len(word) > 2:
        root = word[2:]
        potential_analyses.append(('ok-', root))
        
    # Rule: q- -> q- + ROOT
    if word.startswith('q') and len(word) > 1 and not word.startswith('qok'):
        root = word[1:]
        potential_analyses.append(('q-', root))
        
    # Rule: d- -> d- + ROOT
    if word.startswith('d') and len(word) > 1:
        root = word[1:]
        potential_analyses.append(('d-', root))
        
    # Rule: o- -> o- + ROOT
    if word.startswith('o') and len(word) > 1:
        root = word[1:]
        potential_analyses.append(('o-', root))
    
    # Rule: y- -> y- + ROOT
    if word.startswith('y') and len(word) > 1:
        root = word[1:]
        potential_analyses.append(('y-', root))
        
    # Special case: daiin
    if word == 'daiin':
        if ('d-', 'aiin') not in potential_analyses:
            potential_analyses.append(('d-', 'aiin'))
        
    return potential_analyses

def main():
    input_path = 'results/master_dictionary_v6.json'
    output_root_dict_path = 'results/root_dictionary.json'
    output_report_path = 'results/morphology_report.md'
    output_updated_dict_path = 'results/master_dictionary_v7.json'
    
    print(f"Loading {input_path}...")
    try:
        full_data = load_dictionary(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return

    if 'entries' in full_data:
        dictionary = full_data['entries']
    else:
        dictionary = full_data
        print("Warning: 'entries' key not found, assuming flat dictionary.")

    roots = defaultdict(lambda: {'variations': [], 'total_count': 0, 'meanings': set(), 'base_exists': False})
    
    all_words = set(dictionary.keys())
    
    print("Analyzing morphology...")
    for word, data in dictionary.items():
        count = data.get('count', 1) 
        
        meanings_raw = data.get('meaning', '')
        if isinstance(meanings_raw, list):
             meanings = meanings_raw
        elif meanings_raw:
             meanings = [meanings_raw]
        else:
             meanings = []
             
        if 'definitions' in data:
             if isinstance(data['definitions'], list):
                 meanings.extend(data['definitions'])

        analyses = strip_prefixes(word)
        
        # Update dictionary with morphology
        if analyses:
            data['morphology'] = []
            for prefix, root in analyses:
                data['morphology'].append({
                    'prefix': prefix,
                    'root': root
                })
        else:
             data['morphology'] = None
        
        if analyses:
            for prefix, root in analyses:
                roots[root]['variations'].append({
                    'word': word,
                    'prefix': prefix,
                    'count': count,
                    'meanings': meanings
                })
                roots[root]['total_count'] += count
                for m in meanings:
                    roots[root]['meanings'].add(m)
                    
                if root in all_words:
                    roots[root]['base_exists'] = True
        
        # Add the word itself
        roots[word]['variations'].append({
            'word': word,
            'prefix': None,
            'count': count,
            'meanings': meanings
        })
        roots[word]['total_count'] += count
        for m in meanings:
            roots[word]['meanings'].add(m)
        if word in all_words:
            roots[word]['base_exists'] = True

    final_roots = {}
    
    for root, data in roots.items():
        variations = data['variations']
        has_prefix_variation = any(v['prefix'] is not None for v in variations)
        
        if has_prefix_variation or data['base_exists']:
            final_roots[root] = {
                'total_count': data['total_count'],
                'base_word_exists': data['base_exists'],
                'possible_meanings': list(data['meanings']),
                'variations': variations
            }

    sorted_roots = sorted(final_roots.items(), key=lambda x: x[1]['total_count'], reverse=True)
    
    report_lines = []
    report_lines.append("# Morphology & Root Analysis Report")
    report_lines.append(f"Source: {input_path}")
    report_lines.append("")
    report_lines.append("## Top High-Frequency Roots")
    report_lines.append("| Root | Exists? | Total Freq | Variations (Prefix: Word) | Potential Meanings |")
    report_lines.append("|---|---|---|---|---|")
    
    for root, data in sorted_roots[:50]:
        seen_vars = set()
        display_vars = []
        for v in data['variations']:
            key = f"{v['prefix']}:{v['word']}"
            if key not in seen_vars:
                seen_vars.add(key)
                display_vars.append(v)
        
        variations_str = ", ".join([f"{v['prefix'] or 'Base'}: {v['word']}" for v in display_vars[:5]])
        if len(display_vars) > 5:
            variations_str += ", ..."
        meanings_str = ", ".join(list(data['possible_meanings'])[:3])
        exists_mark = "✅" if data['base_word_exists'] else "❌"
        
        report_lines.append(f"| **{root}** | {exists_mark} | {data['total_count']} | {variations_str} | {meanings_str} |")
        
    report_lines.append("")
    report_lines.append("## Specific Analysis: 'aiin'")
    if 'aiin' in final_roots:
        data = final_roots['aiin']
        report_lines.append(f"- **Root**: aiin")
        report_lines.append(f"- **Base Exists**: {data['base_word_exists']}")
        report_lines.append(f"- **Total Frequency**: {data['total_count']}")
        report_lines.append(f"- **Variations**:")
        for v in data['variations']:
            report_lines.append(f"  - {v['word']} ({v['prefix'] or 'Base'}) - Count: {v['count']} - Meanings: {v['meanings']}")
    else:
        report_lines.append("Root 'aiin' not found in analysis.")

    report_lines.append("")
    report_lines.append("## Specific Analysis: 'eedy' (Hypothetical Root)")
    if 'eedy' in final_roots:
        data = final_roots['eedy']
        report_lines.append(f"- **Root**: eedy")
        report_lines.append(f"- **Base Exists**: {data['base_word_exists']}")
        report_lines.append(f"- **Total Frequency**: {data['total_count']}")
        report_lines.append(f"- **Variations**:")
        for v in data['variations']:
            report_lines.append(f"  - {v['word']} ({v['prefix'] or 'Base'}) - Count: {v['count']}")
    else:
        report_lines.append("Root 'eedy' not found in analysis.")
        
    report_lines.append("")
    report_lines.append("## Specific Analysis: 'okeedy'")
    if 'okeedy' in final_roots:
        data = final_roots['okeedy']
        report_lines.append(f"- **Root**: okeedy")
        report_lines.append(f"- **Base Exists**: {data['base_word_exists']}")
        report_lines.append(f"- **Variations**:")
        for v in data['variations']:
            report_lines.append(f"  - {v['word']} ({v['prefix'] or 'Base'}) - Count: {v['count']}")
    
    print(f"Saving roots to {output_root_dict_path}...")
    json_output = {}
    for root, data in final_roots.items():
        json_output[root] = data
    
    save_json(json_output, output_root_dict_path)
    
    print(f"Saving updated dictionary to {output_updated_dict_path}...")
    if 'version' in full_data:
        full_data['version'] = "7.0"
    save_json(full_data, output_updated_dict_path)

    print(f"Saving report to {output_report_path}...")
    save_text("\n".join(report_lines), output_report_path)
    
    print("Done.")

if __name__ == "__main__":
    main()
