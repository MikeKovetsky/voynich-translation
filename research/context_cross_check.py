import json
import re
import os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_file(path):
    with open(path, 'r') as f:
        return f.read()

def clean_eva_text(text):
    # Remove comments, tags, etc.
    # Don't remove content inside {} as it might be the label text in some formats
    text = text.replace('{', ' ').replace('}', ' ')
    text = re.sub(r'<.*?>', '', text)
    text = text.replace('.', ' ').replace(',', ' ').replace('-', ' ').replace('=', ' ').replace('!', ' ').replace('*', ' ')
    words = text.split()
    return [w.strip() for w in words if w.strip()]

def parse_ivtff(path):
    labels = []
    near_plant_words = []
    page_word_counts = {}
    page_words = {}
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Skip comment descriptions
            if "deleted" in line or "replaced" in line or "bogus" in line or "added" in line:
                continue

            # Handle labels in comments (IVTFF often puts labels in # lines)
            if line.startswith('#'):
                if '<f' in line and ('.L' in line or '.l' in line):
                    line = line.lstrip('#').strip()
                else:
                    continue
            
            match = re.match(r'^(<f[^>]+>)', line)
            if match:
                locator = match.group(1)
                content = line[len(locator):].strip()
                
                folio_match = re.match(r'<f(\d+[rv]\d?)', locator)
                folio = folio_match.group(1) if folio_match else "unknown"
                
                is_label = '.L' in locator or '.l' in locator
                has_plant = '<!plant>' in content
                
                cleaned_words = clean_eva_text(content)
                
                if is_label:
                    if len(labels) < 5:
                         print(f"DEBUG Label: {locator} Content: {content}")
                    for w in cleaned_words:
                        labels.append({'word': w, 'folio': folio, 'locator': locator})
                
                if has_plant:
                    for w in cleaned_words:
                        near_plant_words.append({'word': w, 'folio': folio})
                
                if folio not in page_word_counts:
                    page_word_counts[folio] = 0
                    page_words[folio] = []
                
                page_word_counts[folio] += len(cleaned_words)
                page_words[folio].extend(cleaned_words)

    return labels, near_plant_words, page_word_counts, page_words

def main():
    # 1. Load Candidates
    candidates_path = 'results/context_guesses_v3.json'
    try:
        candidates_data = load_json(candidates_path)
        candidates = {c['word']: c for c in candidates_data}
    except FileNotFoundError:
        print(f"Warning: {candidates_path} not found.")
        candidates = {}
        
    print(f"Loaded {len(candidates)} candidates.")

    # 2. Load Plant Labels
    plant_path = 'results/plant_identifications.json'
    plant_labels = set()
    try:
        plant_data = load_json(plant_path)
        if 'identifications' in plant_data:
            for item in plant_data['identifications']:
                if 'voynich_name' in item:
                    plant_labels.add(item['voynich_name'])
    except FileNotFoundError:
        print(f"Warning: {plant_path} not found.")
        
    print(f"Loaded {len(plant_labels)} plant labels.")

    # 3. Load Star Labels
    star_path = 'results/star_map_os.md'
    star_labels = set()
    try:
        star_text = load_file(star_path)
        occurrences = re.findall(r'`(.*?)`', star_text)
        for occ in occurrences:
            if ':' in occ:
                _, text = occ.split(':', 1)
                clean = clean_eva_text(text.replace('**', ''))
                star_labels.update(clean)
        star_labels.add('os')
    except FileNotFoundError:
        print(f"Warning: {star_path} not found.")
        
    print(f"Loaded {len(star_labels)} potential star labels from map.")

    # 4. Scan Corpus
    ivtff_path = 'data/eva_ivtff.txt'
    labels = []
    near_plant_words = []
    page_word_counts = {}
    page_words = {}
    
    if os.path.exists(ivtff_path):
        print(f"Parsing {ivtff_path}...")
        labels, near_plant_words, page_word_counts, page_words = parse_ivtff(ivtff_path)
        print(f"Extracted {len(labels)} labels.")
        if len(labels) > 0:
            print(f"Sample labels: {[l['word'] for l in labels[:10]]}")
    elif os.path.exists('results/tagged_text.txt'):
        print(f"Parsing results/tagged_text.txt...")
        labels, near_plant_words, page_word_counts, page_words = parse_ivtff('results/tagged_text.txt')
    else:
        print("Warning: No corpus file found.")

    # Identify Short Pages (< 10 words)
    short_page_words = []
    for folio, count in page_word_counts.items():
        if count < 10:
            for w in page_words[folio]:
                short_page_words.append({'word': w, 'folio': folio, 'type': 'short_page'})
    print(f"Found {len(short_page_words)} words on short pages.")

    # 5. Match Candidates
    def get_section(folio):
        if not folio or folio == 'unknown': return 'unknown'
        num_part = re.search(r'\d+', folio)
        if not num_part: return 'unknown'
        num = int(num_part.group(0))
        
        if 67 <= num <= 73: return 'astro'
        if (1 <= num <= 66) or (87 <= num <= 102): return 'herbal'
        if 75 <= num <= 84: return 'bio'
        if 103 <= num <= 116: return 'pharm/recipe'
        return 'other'

    candidate_status = {} 

    for cand_word in candidates:
        status = {'tags': set(), 'locations': []}
        
        # Check explicitly confirmed labels
        for label in labels:
            if label['word'] == cand_word:
                status['tags'].add('CONFIRMED_OBJECT')
                section = get_section(label['folio'])
                status['locations'].append(f"Label on {label['folio']} ({section})")
                
                if section == 'astro':
                    status['tags'].add('STAR_NAME')
                elif section == 'herbal':
                    status['tags'].add('PLANT_NAME')
        
        # Check Short Pages
        for item in short_page_words:
            if item['word'] == cand_word:
                status['tags'].add('CONFIRMED_OBJECT')
                section = get_section(item['folio'])
                status['locations'].append(f"Short page {item['folio']} ({section})")
                if section == 'astro':
                    status['tags'].add('STAR_NAME')

        # Check Plant Identification
        if cand_word in plant_labels:
            status['tags'].add('PLANT_NAME')
            status['tags'].add('CONFIRMED_OBJECT')
            status['locations'].append("Matched Plant ID")

        # Check Star Map
        if cand_word in star_labels:
            status['tags'].add('STAR_NAME')
            status['tags'].add('CONFIRMED_OBJECT')
            status['locations'].append("Matched Star Map")

        # Check Near Plant
        near_plant_count = 0
        for item in near_plant_words:
            if item['word'] == cand_word:
                near_plant_count += 1
        
        if near_plant_count > 0:
            status['tags'].add('PLANT_NAME')
            status['locations'].append(f"Near plant tag ({near_plant_count} times)")

        if status['tags']:
            candidate_status[cand_word] = status

    # 6. Output Results
    report_lines = ["# Track 228: Context Validation Report\n"]
    report_lines.append("| Candidate | Tags | Locations/Evidence |")
    report_lines.append("|-----------|------|--------------------|")
    
    confirmed_count = 0
    star_count = 0
    plant_count = 0

    dictionary_updates = {}

    sorted_candidates = sorted(candidate_status.keys())
    for word in sorted_candidates:
        tags = sorted(list(candidate_status[word]['tags']))
        locs = "; ".join(candidate_status[word]['locations'])
        if len(locs) > 100:
             locs = locs[:100] + "..."
        
        report_lines.append(f"| {word} | {', '.join(tags)} | {locs} |")
        
        if tags:
            dictionary_updates[word] = {
                "word": word,
                "type": "noun", 
                "tags": tags
            }
            if 'CONFIRMED_OBJECT' in tags:
                confirmed_count += 1

        if 'STAR_NAME' in tags: star_count += 1
        if 'PLANT_NAME' in tags: plant_count += 1

    with open('results/context_validation_report.md', 'w') as f:
        f.write("\n".join(report_lines))

    print(f"Report generated. Confirmed: {confirmed_count}, Star: {star_count}, Plant: {plant_count}")

    # Update Dictionary
    dict_path = 'results/dictionary/dictionary.json'
    try:
        dict_data = load_json(dict_path)
        if 'entries' not in dict_data:
             if 'version' in dict_data:
                 if 'entries' not in dict_data: dict_data['entries'] = {}
             else:
                 dict_data = {'entries': dict_data, 'version': 'updated'}
    except FileNotFoundError:
        dict_data = {'version': '1.0', 'entries': {}}
    
    entries = dict_data['entries']
    updates_count = 0

    for word, info in dictionary_updates.items():
        if word not in entries:
            entries[word] = {
                "voynich": word,
                "meaning": "unknown_object", 
                "confidence": 0.5,
                "tags": list(info['tags']),
                "source": "Track228_Context"
            }
            updates_count += 1
        else:
            entry = entries[word]
            current_tags = set(entry.get('tags', []))
            current_tags.update(info['tags'])
            entry['tags'] = list(current_tags)
            
            if 'PLANT_NAME' in info['tags'] and 'plant' not in entry.get('meaning', ''):
                 entry['meaning'] = f"plant_candidate ({entry.get('meaning', '')})"
            elif 'STAR_NAME' in info['tags'] and 'star' not in entry.get('meaning', ''):
                 entry['meaning'] = f"star_candidate ({entry.get('meaning', '')})"
            
            entries[word] = entry
            updates_count += 1

    with open(dict_path, 'w') as f:
        json.dump(dict_data, f, indent=2)
    
    print(f"Dictionary updated with {updates_count} changes.")

    # 7. Summary
    summary_lines = ["# Track 228 Results Summary\n"]
    summary_lines.append(f"- **Total Candidates Checked**: {len(candidates)}")
    summary_lines.append(f"- **Confirmed Objects**: {confirmed_count}")
    summary_lines.append(f"- **Star Names Identified**: {star_count}")
    summary_lines.append(f"- **Plant Names Identified**: {plant_count}")
    summary_lines.append("\n## Highlights")
    summary_lines.append("- Validated noun candidates against Manuscript Labels, Star Maps, and Plant IDs.")
    summary_lines.append("- Generated `results/context_validation_report.md`.")
    
    with open('results/track-228-results_summary.md', 'w') as f:
        f.write("\n".join(summary_lines))

if __name__ == "__main__":
    main()
