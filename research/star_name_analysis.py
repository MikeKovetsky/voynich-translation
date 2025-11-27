import re
import json
import os
import glob

def load_dictionary():
    # Find latest dictionary
    files = glob.glob('results/master_dictionary_v*.json')
    if not files:
        print("No dictionary found in results/")
        return None
    # Sort by version
    latest = sorted(files)[-1]
    print(f"Loading dictionary: {latest}")
    with open(latest, 'r') as f:
        return json.load(f)

def parse_ivtff(path):
    print(f"Parsing {path} for sections f67r-f73v...")
    
    data = {}
    
    with open(path, 'r') as f:
        for line in f:
            if not line.startswith('<f'):
                continue
            
            parts = line.strip().split('\t', 1)
            if len(parts) < 2:
                continue
            
            tag = parts[0]
            text = parts[1]
            
            content = tag[1:-1]
            tag_parts = content.split(';')
            if len(tag_parts) < 2:
                continue
                
            id_part = tag_parts[0]
            transcriber = tag_parts[1]
            
            if not re.match(r'^f(6[789]|7[0123])[rv]', id_part):
                continue
            
            id_subparts = id_part.split(',')
            main_id = id_subparts[0]
            location = id_subparts[1] if len(id_subparts) > 1 else ""
            
            if main_id not in data:
                data[main_id] = {}
            data[main_id][transcriber] = (text, location)
            
    words = []
    for uid, trans_dict in data.items():
        if 'H' in trans_dict:
            text, loc = trans_dict['H']
        elif 'C' in trans_dict:
            text, loc = trans_dict['C']
        elif 'U' in trans_dict:
            text, loc = trans_dict['U']
        else:
            text, loc = next(iter(trans_dict.values()))
            
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('!', '').replace('?', '').replace('*', '').replace(',', '.')
        
        # Determine if it is a label
        # Criteria: explicit tag @L, @R, @S, &L... OR very short text (1 word)
        is_label = False
        if '@' in loc or '&' in loc:
            if 'P' not in loc and 'text' not in loc.lower(): # Exclude paragraphs or long text
                is_label = True
        elif len(text.split()) <= 2: # Heuristic for untagged labels
            is_label = True
            
        tokens = text.split('.')
        for t in tokens:
            t = t.strip()
            if not t: continue
            words.append({
                'word': t,
                'id': uid,
                'location': loc,
                'is_label': is_label
            })
            
    print(f"Extracted {len(words)} words.")
    return words

def analyze_subset(words, dictionary, name):
    y_prefixed = []
    o_prefixed = []
    matches = []
    valid_roots = dictionary.get('entries', {})
    
    for w_obj in words:
        w = w_obj['word']
        prefix = None
        root = None
        
        if w.startswith('y') and len(w) > 1:
            prefix = 'y'
            root = w[1:]
            y_prefixed.append(w_obj)
        elif w.startswith('o') and len(w) > 1:
            prefix = 'o'
            root = w[1:]
            o_prefixed.append(w_obj)
        
        if root:
            if root in valid_roots:
                entry = valid_roots[root]
                matches.append({
                    'original': w,
                    'prefix': prefix,
                    'root': root,
                    'meaning': entry.get('meaning', 'unknown'),
                    'id': w_obj['id'],
                    'location': w_obj['location']
                })
                
    return y_prefixed, o_prefixed, matches

def generate_report(all_words, dictionary):
    labels = [w for w in all_words if w['is_label']]
    text = [w for w in all_words if not w['is_label']]
    
    y_all, o_all, m_all = analyze_subset(all_words, dictionary, "All")
    y_lbl, o_lbl, m_lbl = analyze_subset(labels, dictionary, "Labels")
    y_txt, o_txt, m_txt = analyze_subset(text, dictionary, "Text")
    
    report = []
    report.append("# Star Name Analysis Report")
    report.append(f"Total words analyzed: {len(all_words)}")
    report.append(f"- Labels (approx): {len(labels)}")
    report.append(f"- Running Text: {len(text)}")
    report.append("")
    
    report.append("## 1. Prefix Analysis")
    report.append("Comparison of prefix frequency in Labels vs Running Text.")
    report.append("")
    report.append("| Metric | Labels | Text | All |")
    report.append("|---|---|---|---|")
    report.append(f"| Total Words | {len(labels)} | {len(text)} | {len(all_words)} |")
    report.append(f"| `o-` Prefix | {len(o_lbl)} ({len(o_lbl)/len(labels)*100:.1f}%) | {len(o_txt)} ({len(o_txt)/len(text)*100:.1f}%) | {len(o_all)} ({len(o_all)/len(all_words)*100:.1f}%) |")
    report.append(f"| `y-` Prefix | {len(y_lbl)} ({len(y_lbl)/len(labels)*100:.1f}%) | {len(y_txt)} ({len(y_txt)/len(text)*100:.1f}%) | {len(y_all)} ({len(y_all)/len(all_words)*100:.1f}%) |")
    report.append("")
    
    report.append("## 2. Root Matching")
    report.append("Words where stripping the prefix results in a known dictionary ingredient/term.")
    report.append("")
    report.append(f"- **Labels**: {len(m_lbl)} matches ({len(m_lbl)/len(labels)*100:.1f}%)")
    report.append(f"- **Text**: {len(m_txt)} matches ({len(m_txt)/len(text)*100:.1f}%)")
    report.append("")
    
    report.append("### Top Matches in Labels")
    root_counts = {}
    for m in m_lbl:
        r = m['root']
        meaning = m['meaning']
        key = f"{r} ({meaning})"
        root_counts[key] = root_counts.get(key, 0) + 1
    
    sorted_roots = sorted(root_counts.items(), key=lambda x: x[1], reverse=True)
    
    report.append("| Root | Meaning | Frequency | Example |")
    report.append("|---|---|---|---|")
    for key, count in sorted_roots[:20]:
        root_val = key.split(' ')[0]
        example = next((m['original'] for m in m_lbl if m['root'] == root_val), "")
        report.append(f"| {root_val} | {key.split('(', 1)[1][:-1]} | {count} | {example} |")
        
    report.append("")
    report.append("### Specific Ingredient Checks (in Labels)")
    targets = ['chol', 'char', 'chedy', 'aiin', 'shey']
    for t in targets:
        found = [m for m in m_lbl if m['root'] == t]
        if found:
            report.append(f"- **{t}**: Found {len(found)} times. Examples: {', '.join(set([m['original'] for m in found]))}")
        else:
            report.append(f"- **{t}**: Not found in labels.")
            
    # Save matches to JSON
    with open('results/star_name_matches.json', 'w') as f:
        json.dump(m_lbl, f, indent=2)
        
    with open('results/star_name_report.md', 'w') as f:
        f.write('\n'.join(report))
    print("Report generated at results/star_name_report.md")

def main():
    dictionary = load_dictionary()
    if not dictionary:
        return
        
    words = parse_ivtff('data/eva_ivtff.txt')
    generate_report(words, dictionary)

if __name__ == "__main__":
    main()
