import re
import json
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_translation(word, dictionary):
    if word in dictionary['entries']:
        entry = dictionary['entries'][word]
        if entry.get('meaning'):
            return entry['meaning']
    return None

def parse_ivtff(path, target_pages):
    labels = []
    single_word_lines = []
    qokedy_count = 0
    qokedy_locations = []
    
    # General line pattern
    # Matches <f75r.1;V> content...
    # Allow space or tab after the tag
    line_pattern = re.compile(r'<(f\d+[rv])\.(\d+).*?;([A-Za-z])>\s+(.*)')
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = line_pattern.match(line)
            if not match:
                continue
                
            page = match.group(1)
            line_num = match.group(2)
            source = match.group(3)
            content = match.group(4)
            
            # Filter pages 75-84
            try:
                p_num = int(re.search(r'\d+', page).group())
            except:
                continue
                
            if not (75 <= p_num <= 84):
                continue

            # Filter source 'V'
            if source != 'V':
                continue

            # Clean content for analysis
            clean_text = re.sub(r'<[^>]+>', ' ', content)
            # Split by common delimiters
            words = [w for w in clean_text.replace('.', ' ').replace('!', ' ').replace(',', ' ').split() if w.strip()]
            
            for w in words:
                if w == 'qokedy':
                    qokedy_count += 1
                    qokedy_locations.append(f"{page}.{line_num}")

            # Labels
            label_matches = re.findall(r'<!label:([^>]+)>', content)
            for lm in label_matches:
                labels.append({
                    'page': page,
                    'line': line_num,
                    'type': 'explicit_label',
                    'text': lm
                })

            # Short lines
            if len(words) == 1:
                single_word_lines.append({
                    'page': page,
                    'line': line_num,
                    'type': 'single_word_line',
                    'text': words[0]
                })
            elif len(words) == 2:
                 single_word_lines.append({
                    'page': page,
                    'line': line_num,
                    'type': 'two_word_line',
                    'text': " ".join(words)
                })

    return {
        'qokedy_count': qokedy_count,
        'qokedy_locations': qokedy_locations,
        'explicit_labels': labels,
        'short_lines': single_word_lines
    }

def main():
    dict_path = 'results/dictionary/master_dictionary_v15.json'
    data_path = 'data/eva_ivtff.txt'
    
    dictionary = load_dictionary(dict_path)
    results = parse_ivtff(data_path, range(75, 85))
    
    processed_labels = []
    all_items = results['explicit_labels'] + results['short_lines']
    
    for item in all_items:
        text = item['text']
        text_clean = text.replace('.', ' ').replace('!', ' ').replace(',', ' ').strip()
        
        words = text_clean.split()
        translations = []
        for w in words:
            trans = get_translation(w, dictionary)
            translations.append(f"{w}({trans if trans else '?'})")
            
        item['translation'] = " ".join(translations)
        processed_labels.append(item)
        
    with open('results/bio_labels.json', 'w') as f:
        json.dump(processed_labels, f, indent=2)
        
    summary = []
    summary.append("# Track 290: Bio Section Visual-Text Correlation Results")
    summary.append(f"\n## Qokedy Analysis")
    summary.append(f"- Total occurrences of `qokedy` in Bio Section (f75-f84): {results['qokedy_count']}")
    if results['qokedy_locations']:
        summary.append(f"- Locations sample: {', '.join(results['qokedy_locations'][:10])}...")
    else:
        summary.append("- No `qokedy` found.")
    
    summary.append("\n## Label Analysis")
    summary.append("Found labels (Explicit tags + Single/Two word lines):")
    summary.append("| Page | Type | Text | Translation |")
    summary.append("|---|---|---|---|")
    
    for item in processed_labels:
        summary.append(f"| {item['page']} | {item['type']} | {item['text']} | {item['translation']} |")
        
    with open('results/track-290-results_summary.md', 'w') as f:
        f.write("\n".join(summary))

    print("Analysis complete. Files created.")

if __name__ == "__main__":
    main()
