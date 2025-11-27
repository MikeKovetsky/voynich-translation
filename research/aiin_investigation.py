import json
import re
from collections import Counter

def load_page_map(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_dictionary(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_page_class(page_map, page_id):
    # Handle page ids like "f1v", "1v"
    if page_id in page_map:
        return page_map[page_id].get('class')
    # Try without 'f' if present
    if page_id.startswith('f'):
        pid = page_id[1:]
        if pid in page_map:
            return page_map[pid].get('class')
    return None

def parse_eva_file(path):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            # Match lines like <f34v.2,+P0;H> text...
            # We prefer H source
            if ';H>' in line:
                match = re.match(r'<f(\d+[rv])\.\d+.*?>\s+(.*)', line)
                if match:
                    page_id = match.group(1)
                    text = match.group(2).strip()
                    lines.append({'page': page_id, 'text': text})
    return lines

def find_collocations(lines, target_word, context_window=2):
    collocations = []
    for line in lines:
        words = line['text'].split('.')
        # Remove empty strings
        words = [w for w in words if w]
        for i, word in enumerate(words):
            if word == target_word:
                start = max(0, i - context_window)
                end = min(len(words), i + context_window + 1)
                context = words[start:end]
                collocations.append({
                    'page': line['page'],
                    'context': context,
                    'prev': words[i-1] if i > 0 else None,
                    'next': words[i+1] if i < len(words)-1 else None
                })
    return collocations

def search_dictionary_by_meaning(dictionary, keywords):
    found = {}
    for word, entry in dictionary['entries'].items():
        meaning = entry.get('meaning', '').lower()
        for kw in keywords:
            if kw in meaning:
                if kw not in found:
                    found[kw] = []
                found[kw].append(word)
    return found

def analyze_aiin():
    page_map = load_page_map('results/elemental_page_map.json')
    dictionary = load_dictionary('results/dictionary/dictionary.json')
    
    all_lines = parse_eva_file('data/eva_ivtff.txt')
    
    dry_lines = []
    wet_lines = []
    
    for line in all_lines:
        p_class = get_page_class(page_map, line['page'])
        if p_class == 'Dry':
            dry_lines.append(line)
        elif p_class == 'Wet':
            wet_lines.append(line)
            
    print(f"Found {len(dry_lines)} Dry lines and {len(wet_lines)} Wet lines.")
    
    target = 'aiin'
    dry_collocs = find_collocations(dry_lines, target)
    wet_collocs = find_collocations(wet_lines, target)
    
    print(f"Found {len(dry_collocs)} instances of '{target}' in Dry pages.")
    print(f"Found {len(wet_collocs)} instances of '{target}' in Wet pages.")
    
    # Extract 50 examples
    dry_examples = dry_collocs[:50]
    wet_examples = wet_collocs[:50]
    
    # Search dictionary for relevant verbs/concepts
    keywords = ['drink', 'drunk', 'mix', 'see', 'star', 'take', 'eat', 'substance', 'essence', 'water', 'fire']
    relevant_words = search_dictionary_by_meaning(dictionary, keywords)
    
    # Check if relevant words appear in collocations
    def check_matches(collocs, relevant_map):
        matches = Counter()
        for item in collocs:
            context = item['context']
            for w in context:
                if w == target: continue
                for meaning, words in relevant_map.items():
                    if w in words:
                        matches[f"{w} ({meaning})"] += 1
        return matches

    dry_matches = check_matches(dry_collocs, relevant_words)
    wet_matches = check_matches(wet_collocs, relevant_words)
    
    # Check morphological variants
    variants = ['oaiin', 'daiin', 'kaiin']
    variant_counts = {'Dry': Counter(), 'Wet': Counter()}
    
    for v in variants:
        d_c = find_collocations(dry_lines, v)
        w_c = find_collocations(wet_lines, v)
        variant_counts['Dry'][v] = len(d_c)
        variant_counts['Wet'][v] = len(w_c)
        
    # Generate Report
    report = f"# Analysis of '{target}' in Dry vs Wet Pages\n\n"
    
    report += "## Statistics\n"
    report += f"- Total Dry Lines: {len(dry_lines)}\n"
    report += f"- Total Wet Lines: {len(wet_lines)}\n"
    report += f"- '{target}' in Dry: {len(dry_collocs)}\n"
    report += f"- '{target}' in Wet: {len(wet_collocs)}\n\n"
    
    report += "## Morphological Variants\n"
    report += "| Variant | Dry Count | Wet Count |\n"
    report += "|---|---|---|\n"
    for v in variants:
        report += f"| {v} | {variant_counts['Dry'][v]} | {variant_counts['Wet'][v]} |\n"
    report += "\n"

    report += "## Collocations with Meaningful Words\n"
    report += "### Dry Pages\n"
    for m, c in dry_matches.most_common(10):
        report += f"- {m}: {c}\n"
    report += "\n### Wet Pages\n"
    for m, c in wet_matches.most_common(10):
        report += f"- {m}: {c}\n"
    
    report += "\n## Examples (Dry)\n"
    for item in dry_examples:
        ctx = " ".join(item['context'])
        report += f"- [{item['page']}] ... {ctx} ...\n"
        
    report += "\n## Examples (Wet)\n"
    for item in wet_examples:
        ctx = " ".join(item['context'])
        report += f"- [{item['page']}] ... {ctx} ...\n"
        
    with open('results/aiin_analysis.md', 'w') as f:
        f.write(report)
        
    # Also write summary
    summary = f"# Track 235 Summary\n\n"
    summary += "## Findings\n"
    summary += f"- Analyzed {len(dry_collocs)} instances in Dry pages and {len(wet_collocs)} in Wet pages.\n"
    summary += "- Morphological patterns:\n"
    for v in variants:
        summary += f"  - {v}: Dry={variant_counts['Dry'][v]}, Wet={variant_counts['Wet'][v]}\n"
    summary += "\n## Recommendation\n"
    summary += "Based on the collocations and distribution..." # Placeholder
    
    with open('results/track-235-results_summary.md', 'w') as f:
        f.write(summary)

if __name__ == "__main__":
    analyze_aiin()
