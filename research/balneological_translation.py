import json
import re
import os

# Configuration
DICTIONARY_PATH = 'results/dictionary/dictionary_v10_0.json'
DATA_PATH = 'data/eva_ivtff.txt'
TARGET_FOLIOS = ['f75r', 'f77v', 'f78r']
OUTPUT_MD_PATH = 'results/balneological_translation.md'
SUMMARY_MD_PATH = 'results/track-236-results_summary.md'

WATER_WORDS = {
    'okeedy': 'Mixture',
    'shedy': 'Flowing/Which/That',
    'qokeey': 'Drink/Wash'
}

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # Check if it has 'entries' key
    if 'entries' in data:
        return data['entries']
    return data

def parse_ivtff(path, target_folios):
    """
    Extracts text and labels from the IVTFF file for specific folios.
    Uses 'V' (Takeshi Takahashi) transcription for text.
    Scans all transcriptions for labels.
    """
    extracted_data = {folio: {} for folio in target_folios} # Use dict for line matching
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'): 
                continue
                
            # Check if line belongs to one of the target folios
            for folio in target_folios:
                if line.startswith(f'<{folio}'):
                    # Parse line metadata: <f75r.1,@P0;V>
                    # We want to key by 'f75r.1' (unit id)
                    match = re.match(r'<([^;]+);([^>]+)>(.*)', line)
                    if match:
                        unit_id = match.group(1) # e.g. f75r.1,@P0
                        transcriber = match.group(2) # e.g. V
                        content = match.group(3)
                        
                        # Initialize line entry if not exists
                        if unit_id not in extracted_data[folio]:
                            extracted_data[folio][unit_id] = {
                                'line_id': unit_id,
                                'original_content': '',
                                'clean_words': [],
                                'labels': set()
                            }
                        
                        # Extract labels from ANY transcription
                        labels = re.findall(r'<!label:([^>]+)>', content)
                        for label in labels:
                            extracted_data[folio][unit_id]['labels'].add(label)
                            
                        # Extract text only from V
                        if transcriber == 'V':
                            extracted_data[folio][unit_id]['original_content'] = content
                            
                            # Clean content
                            clean_text = re.sub(r'<[^>]+>', '', content)
                            clean_text = clean_text.replace('.', ' ').replace(',', ' ')
                            clean_text = clean_text.replace('!', '') 
                            clean_text = clean_text.replace('-', '') 
                            
                            words = clean_text.split()
                            words = [w.strip() for w in words if w.strip()]
                            
                            extracted_data[folio][unit_id]['clean_words'] = words
                    
                    break
    
    # Convert back to list and sort?
    # The order in IVTFF is sequential, so if we iterate the dict, it might be ordered or we rely on insertion order (Python 3.7+)
    # Better to just return list sorted by unit_id if possible, but unit_id has complex structure.
    # Actually, IVTFF file order is the reading order.
    # But I'm storing in a dict.
    # Let's re-read the file order or just rely on the fact that I populated the dict in file order.
    
    final_data = {}
    for folio, units in extracted_data.items():
        # Filter out units that didn't have V transcription (if any)?
        # Or keep them if they have labels?
        # Let's keep only units that have 'clean_words' (meaning V was found)
        # OR units that have labels.
        
        # But if I only have labels and no text, it might be weird in the translation table.
        # Let's keep units with V transcription.
        
        ordered_units = []
        # We rely on the fact that dicts preserve insertion order in recent Python
        for unit_id, data in units.items():
            if data['clean_words']:
                data['labels'] = sorted(list(data['labels']))
                ordered_units.append(data)
            elif data['labels']:
                 # It has labels but no V text. Maybe use empty text?
                 pass
        
        final_data[folio] = ordered_units
        
    return final_data

def get_translation(word, dictionary):
    if word in dictionary:
        entry = dictionary[word]
        if isinstance(entry, dict):
            return entry.get('meaning')
    return None

def generate_translation(extracted_data, dictionary):
    results = {}
    
    for folio, lines in extracted_data.items():
        folio_res = []
        for line in lines:
            translated_line = []
            for word in line['clean_words']:
                trans = get_translation(word, dictionary)
                
                is_water = False
                if word in WATER_WORDS:
                    trans = f"**{WATER_WORDS[word]}** ({word})"
                    is_water = True
                elif word == 'ol':
                     trans = "**Water/Lotion** (ol)" 
                     is_water = True
                
                if is_water:
                    translated_line.append(trans)
                elif trans:
                    translated_line.append(f"{trans} ({word})")
                else:
                    translated_line.append(word)

            folio_res.append({
                'line_id': line['line_id'],
                'original': line['original_content'],
                'translation': ' '.join(translated_line),
                'labels': line['labels']
            })
        results[folio] = folio_res
    return results

def main():
    print(f"Loading dictionary from {DICTIONARY_PATH}...")
    dictionary = load_dictionary(DICTIONARY_PATH)
    
    print(f"Parsing IVTFF data from {DATA_PATH}...")
    data = parse_ivtff(DATA_PATH, TARGET_FOLIOS)
    
    print("Generating translations...")
    translation_results = generate_translation(data, dictionary)
    
    # Generate markdown
    with open(OUTPUT_MD_PATH, 'w') as f:
        f.write("# Balneological Translation (f75-f84)\n\n")
        f.write("Translation using Dictionary v10.\n\n")
        
        for folio in TARGET_FOLIOS:
            f.write(f"## Folio {folio}\n\n")
            lines = translation_results[folio]
            if not lines:
                f.write("No text found for this folio in the IVTFF file.\n\n")
                continue
                
            f.write("| Line | Original | Translation |\n")
            f.write("|---|---|---|\n")
            
            for res in lines:
                # Format for table
                orig = res['original'].replace('|', '\|')
                trans = res['translation'].replace('|', '\|')
                line_id = res['line_id'].replace('<', '&lt;').replace('>', '&gt;')
                
                f.write(f"| {line_id} | `{orig}` | {trans} |\n")
                
                if res['labels']:
                    # Also check if labels have meaning
                    label_trans = []
                    for label in res['labels']:
                        parts = label.split('.')
                        trans_parts = []
                        for p in parts:
                            t = get_translation(p, dictionary)
                            if p in WATER_WORDS:
                                t = WATER_WORDS[p]
                            elif p == 'ol':
                                t = "Water/Lotion"
                            
                            if t:
                                trans_parts.append(f"{t}({p})")
                            else:
                                trans_parts.append(p)
                        label_trans.append(" ".join(trans_parts))
                    
                    f.write(f"| | **Labels found:** {', '.join(res['labels'])} | **Label Translation:** {', '.join(label_trans)} |\n")
            f.write("\n")

    # Generate Summary
    with open(SUMMARY_MD_PATH, 'w') as f:
        f.write("# Track 236 Results Summary\n\n")
        f.write("## Overview\n")
        f.write(f"Translated folios {', '.join(TARGET_FOLIOS)} (Balneological section).\n\n")
        f.write("## Key Findings\n")
        f.write("- **Dictionary Stats**: Used v10 dictionary.\n")
        
        total_lines = sum(len(lines) for lines in data.values())
        f.write(f"- **Extracted**: {total_lines} lines of text across 3 folios.\n")
        
        # Count water words occurences
        water_counts = {w: 0 for w in WATER_WORDS}
        water_counts['ol'] = 0
        
        for folio in TARGET_FOLIOS:
            for line in data[folio]:
                for word in line['clean_words']:
                    if word in water_counts:
                        water_counts[word] += 1
        
        f.write("### Water Words Frequency\n")
        for word, count in water_counts.items():
            meaning = WATER_WORDS.get(word, "Water/Lotion")
            f.write(f"- `{word}` ({meaning}): {count}\n")
            
        f.write("\n## Blue Nymphs Analysis\n")
        f.write("Labels found near figures (Blue Nymphs?):\n")
        found_labels = False
        for folio in TARGET_FOLIOS:
            for line in translation_results[folio]:
                if line['labels']:
                    found_labels = True
                    for label in line['labels']:
                         f.write(f"- **{folio}**: {label}\n")
        
        if not found_labels:
            f.write("- No specific labels found embedded in the text lines for these folios.\n")

    print(f"Done. Results saved to {OUTPUT_MD_PATH} and {SUMMARY_MD_PATH}")

if __name__ == "__main__":
    main()
