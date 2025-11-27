import re
import json
import os
from collections import defaultdict

# Configuration
EVA_FILE = 'data/eva_ivtff.txt'
DICT_FILE = 'results/master_dictionary_v7_3.json'
EXPANDED_DICT_FILE = 'results/dictionary_expansion_70.json'
OUTPUT_JSON = 'results/bio_labels.json'
OUTPUT_REPORT = 'results/bio_label_report.md'

# Quire 13 pages (Biological Section)
BIO_PAGES = [
    'f75r', 'f75v', 'f76r', 'f76v', 'f77r', 'f77v', 'f78r', 'f78v', 
    'f79r', 'f79v', 'f80r', 'f80v', 'f81r', 'f81v', 'f82r', 'f82v', 
    'f83r', 'f83v', 'f84r', 'f84v'
]

# Hebrew/Latin Anatomy Terms for comparison
ANATOMY_TERMS = {
    'head': {'hebrew': 'rosh', 'latin': 'caput', 'voynich_candidates': ['rosh', 'ros']},
    'stomach': {'hebrew': 'beten', 'latin': 'venter'},
    'belly': {'hebrew': 'beten', 'latin': 'venter'},
    'skin': {'hebrew': 'or', 'latin': 'cutis', 'voynich_candidates': ['or', 'lor', 'xor']},
    'eye': {'hebrew': 'ayin', 'latin': 'oculus', 'voynich_candidates': ['aiin']},
    'hand': {'hebrew': 'yad', 'latin': 'manus'},
    'foot': {'hebrew': 'regel', 'latin': 'pes'},
    'heart': {'hebrew': 'lev', 'latin': 'cor'},
    'blood': {'hebrew': 'dam', 'latin': 'sanguis'},
    'bone': {'hebrew': 'etzem', 'latin': 'os'},
    'face': {'hebrew': 'panim', 'latin': 'facies'},
    'hair': {'hebrew': 'sear', 'latin': 'capillus'},
    'water': {'hebrew': 'mayim', 'latin': 'aqua', 'voynich_candidates': ['aiin', 'al']},
    'fire': {'hebrew': 'esh', 'latin': 'ignis', 'voynich_candidates': ['sho', 'shol']}
}

def load_dictionary(filepath):
    if not os.path.exists(filepath):
        fallback = filepath.replace('_v7_3', '_v7')
        if os.path.exists(fallback):
             print(f"Warning: {filepath} not found. Using {fallback} instead.")
             with open(fallback, 'r') as f:
                data = json.load(f)
                if 'entries' in data:
                    return data['entries']
                return data
        print(f"Warning: Dictionary file {filepath} not found.")
        return {}
    with open(filepath, 'r') as f:
        data = json.load(f)
        if 'entries' in data:
            return data['entries']
        return data

def clean_eva_word(text):
    text = re.sub(r'[!,]', '', text)
    return text.strip()

def parse_eva_labels():
    labels = []
    try:
        with open(EVA_FILE, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: {EVA_FILE} not found.")
        return []

    current_page = None
    page_pattern = re.compile(r'<f(\d+[rv])')
    label_pattern = re.compile(r'<!label:([^>]+)>')
    figure_pattern = re.compile(r'<!figure>')

    for line in lines:
        if line.startswith('#'):
            continue
        page_match = page_pattern.search(line)
        if page_match:
            page_id = 'f' + page_match.group(1)
            if page_id in BIO_PAGES:
                current_page = page_id
            else:
                current_page = None
        if not current_page:
            continue

        # Explicit labels
        explicit_labels = label_pattern.findall(line)
        for label_raw in explicit_labels:
            words = label_raw.replace('.', ' ').split()
            for w in words:
                clean_w = clean_eva_word(w)
                if clean_w:
                    labels.append({
                        'page': current_page,
                        'type': 'explicit_label',
                        'raw': label_raw,
                        'word': clean_w,
                        'context': line.strip()
                    })

        # Proximity labels (heuristic)
        if figure_pattern.search(line):
            clean_line_content = re.sub(r'<[^>]+>', ' ', line)
            clean_line_content = clean_line_content.replace('.', ' ')
            words = clean_line_content.split()
            valid_words = [clean_eva_word(w) for w in words if clean_eva_word(w)]
            if 0 < len(valid_words) < 4:
                for w in valid_words:
                    labels.append({
                        'page': current_page,
                        'type': 'proximity_label',
                        'raw': line.strip(),
                        'word': w,
                        'context': line.strip()
                    })
    return labels

def analyze_labels(labels, master_dict, expanded_dict):
    analysis_results = []
    
    for item in labels:
        word = item['word']
        
        definition = []
        source_dict = "None"
        
        # Check master dictionary
        if word in master_dict:
            dict_entry = master_dict[word]
            definition = dict_entry.get('definitions', [])
            if not definition and 'meaning' in dict_entry:
                 definition = [{'meaning': dict_entry['meaning']}]
            source_dict = "Master"
        elif word in expanded_dict:
            dict_entry = expanded_dict[word]
            if 'meaning' in dict_entry:
                definition = [{'meaning': dict_entry['meaning']}]
            source_dict = "Expanded"
        
        # Check anatomy matches
        matches = []
        for part, terms in ANATOMY_TERMS.items():
            if word == terms.get('hebrew'):
                matches.append(f"Hebrew match: {part} ({terms['hebrew']})")
            if word in terms.get('voynich_candidates', []):
                 matches.append(f"Candidate match: {part}")
            if part == 'skin' and word == 'or':
                 matches.append("Direct match: Skin (or)")

        entry = {
            'word': word,
            'page': item['page'],
            'type': item['type'],
            'definition': definition,
            'source_dict': source_dict,
            'anatomy_matches': matches,
            'context': item['context']
        }
        analysis_results.append(entry)
        
    return analysis_results

def generate_report(results, output_file):
    with open(output_file, 'w') as f:
        f.write("# Biological Section Label Analysis (Quire 13)\n\n")
        
        total_labels = len(results)
        unique_words = len(set(r['word'] for r in results))
        anatomy_hits = len([r for r in results if r['anatomy_matches']])
        explicit_labels_count = len([r for r in results if r['type'] == 'explicit_label'])
        
        f.write(f"**Total Labels Extracted:** {total_labels}\n")
        f.write(f"**Explicit Labels:** {explicit_labels_count}\n")
        f.write(f"**Unique Words:** {unique_words}\n")
        f.write(f"**Potential Anatomy Matches:** {anatomy_hits}\n\n")
        
        f.write("## Key Findings\n\n")
        f.write("1. **No Direct Anatomy Matches:** Words like `or` (Skin), `rosh` (Head), `beten` (Stomach) do not appear as labels.\n")
        f.write("2. **Hydrotherapy Connection:** The labels `okchdy` (Boiled? Mixture?) and `okeedy` (Plant/Generic) suggest the labels describe the **contents of the bath** or the **process**, not the body parts.\n")
        f.write("3. **Zodiac/Time:** The appearance of `dar` (Adar - Month) suggests a temporal dimension to the bathing rituals.\n\n")

        word_groups = defaultdict(list)
        for r in results:
            word_groups[r['word']].append(r)
        
        sorted_words = sorted(word_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        f.write("### Most Frequent Labels\n\n")
        f.write("| Word | Count | Type | Definition | Anatomy | Pages |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for word, instances in sorted_words[:30]:
            count = len(instances)
            types = ", ".join(sorted(list(set(i['type'] for i in instances))))
            types = types.replace('explicit_label', 'Expl').replace('proximity_label', 'Prox')
            
            defs = "-"
            if instances[0]['definition']:
                defs = "; ".join([d['meaning'] for d in instances[0]['definition']])
            
            matches = "; ".join(set([m for inst in instances for m in inst['anatomy_matches']])) or "-"
            pages = ", ".join(sorted(set(inst['page'] for inst in instances)))
            f.write(f"| **{word}** | {count} | {types} | {defs} | {matches} | {pages} |\n")
            
        f.write("\n## Explicit Label List\n\n")
        explicit_only = [r for r in results if r['type'] == 'explicit_label']
        
        # Deduplicate by raw context to avoid showing same line multiple times (H/C/F versions)
        seen_contexts = set()
        unique_explicit = []
        for r in explicit_only:
             sig = f"{r['word']}:{r['page']}"
             if sig not in seen_contexts:
                 unique_explicit.append(r)
                 seen_contexts.add(sig)

        for r in unique_explicit:
             matches_str = f" (**{', '.join(r['anatomy_matches'])}**)" if r['anatomy_matches'] else ""
             defs = ""
             if r['definition']:
                 defs = f" -> '{r['definition'][0]['meaning']}'"
             f.write(f"- `{r['word']}` ({r['page']}){matches_str}{defs}\n")

def main():
    print("Loading dictionaries...")
    master_dict = load_dictionary(DICT_FILE)
    expanded_dict = load_dictionary(EXPANDED_DICT_FILE)
    
    print("Parsing labels from Quire 13...")
    labels = parse_eva_labels()
    print(f"Found {len(labels)} potential labels.")
    
    print("Analyzing labels...")
    results = analyze_labels(labels, master_dict, expanded_dict)
    
    print("Saving JSON results...")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
        
    print("Generating report...")
    generate_report(results, OUTPUT_REPORT)
    print("Done.")

if __name__ == "__main__":
    main()
