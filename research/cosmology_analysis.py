import json
import os
import re
from collections import Counter

# Configuration
DICTIONARY_PATH = 'results/dictionary/dictionary.json'
DATA_PATH = 'data/eva_ivtff.txt'
RESULTS_PATH = 'results/cosmology_analysis.md'
SUMMARY_PATH = 'results/track-239-results_summary.md'

TARGET_FOLIOS = ['f67r1', 'f67r2', 'f68r1', 'f68r2', 'f68v1', 'f68v2', 'f68v3']

def load_dictionary(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Warning: Dictionary file not found at {path}")
        return {}

def clean_word(w):
    # Remove common EVA modifiers/punctuation
    # ! = uncertainty/variant
    # ? = illegible
    # , = separator?
    # - = break
    return w.replace('!', '').replace('?', '').replace(',', '').replace('-', '').replace(';', '')

def parse_eva_line(line):
    # Line format: <ID> [TAB] text
    # Check for comment
    if line.startswith('#'):
        return None

    # Match ID
    # We look for <...> at the start
    match = re.match(r'<([^>]+)>\s+(.*)', line)
    if not match:
        return None
    
    location_id = match.group(1)
    raw_text = match.group(2).strip()
    
    # ID: f67r1.1,@P0;H
    parts = location_id.split(';')
    if len(parts) < 2:
        return None
        
    loc_part = parts[0]
    source = parts[1]
    
    # Use 'H' transcription. 
    if source != 'H':
        return None
        
    folio_match = re.match(r'(f\d+[rv]\d*)', loc_part)
    if not folio_match:
        return None
    
    folio = folio_match.group(1)
    
    if folio not in TARGET_FOLIOS:
        return None
        
    # Determine Location Type
    location_type = "Unknown"
    if '@Ri' in loc_part:
        location_type = "Ring"
    elif '@P' in loc_part:
        location_type = "Paragraph"
    elif '@C' in loc_part:
        location_type = "Circle"
    elif '@L' in loc_part or '&L' in loc_part:
        location_type = "Label"
    elif '@R' in loc_part: 
        location_type = "Region"
    elif '@T' in loc_part:
        location_type = "Title" #?
    elif 'Pb' in loc_part:
        location_type = "Label" # Often Pb is used for labels in some transcriptions
    
    # Process Text
    # Replace '.' with space to separate words
    # In IVTFF, '.' separates words.
    text_space_sep = raw_text.replace('.', ' ')
    words = text_space_sep.split()
    
    cleaned_words = [clean_word(w) for w in words if w.strip()]
    
    return {
        'folio': folio,
        'location_id': loc_part,
        'location_type': location_type,
        'text': ' '.join(cleaned_words),
        'words': cleaned_words
    }

def main():
    dictionary = load_dictionary(DICTIONARY_PATH)
    
    folio_data = {folio: {'lines': [], 'words': [], 'counts': Counter()} for folio in TARGET_FOLIOS}
    
    print(f"Reading {DATA_PATH}...")
    with open(DATA_PATH, 'r') as f:
        for line in f:
            parsed = parse_eva_line(line)
            if parsed:
                folio = parsed['folio']
                folio_data[folio]['lines'].append(parsed)
                folio_data[folio]['words'].extend(parsed['words'])
                folio_data[folio]['counts'].update(parsed['words'])

    print("Generating output...")
    # Generate Report
    with open(RESULTS_PATH, 'w') as f:
        f.write("# Cosmology Deep Dive Analysis\n\n")
        f.write(f"Target Folios: {', '.join(TARGET_FOLIOS)}\n\n")
        
        # Overall Analysis
        f.write("## Folio Analysis\n\n")
        
        for folio in TARGET_FOLIOS:
            data = folio_data[folio]
            total_words = len(data['words'])
            unique_words = len(data['counts'])
            
            aiin_count = data['counts'].get('aiin', 0)
            o_count = data['counts'].get('o', 0)
            ol_count = data['counts'].get('ol', 0)
            
            # Wet/Dry
            status = "Neutral"
            if o_count > ol_count * 1.5:
                status = "Dry (o dominant)"
            elif ol_count > o_count * 1.5:
                status = "Wet (ol dominant)"
            elif o_count == 0 and ol_count == 0:
                status = "Indeterminate (no 'o' or 'ol')"
            else:
                status = "Mixed"
                
            f.write(f"### {folio}\n")
            f.write(f"- **Total Words**: {total_words}\n")
            f.write(f"- **Unique Words**: {unique_words}\n")
            f.write(f"- **'aiin' count**: {aiin_count}\n")
            f.write(f"- **'o' count**: {o_count}\n")
            f.write(f"- **'ol' count**: {ol_count}\n")
            f.write(f"- **Status**: {status}\n")
            
            # Aiin usage
            aiin_lines = [l for l in data['lines'] if 'aiin' in l['words']]
            if aiin_lines:
                f.write("\n#### 'aiin' Occurrences:\n")
                for l in aiin_lines:
                    is_label = l['location_type'] in ['Label', 'Ring', 'Circle', 'Region']
                    loc_str = f"**{l['location_type']}**" if is_label else l['location_type']
                    
                    # Translate
                    translated_line = []
                    for w in l['words']:
                        # Check if aiin
                        md_w = w
                        if w == 'aiin':
                            md_w = "**aiin**"
                        
                        if w in dictionary:
                            trans = dictionary[w].get('meaning', '?')
                            translated_line.append(f"{md_w}({trans})")
                        else:
                            translated_line.append(md_w)
                    
                    f.write(f"- [{l['location_id']}] ({loc_str}): {' '.join(translated_line)}\n")
            
            f.write("\n")

    # Summary
    with open(SUMMARY_PATH, 'w') as f:
        f.write("# Track 239: Cosmology Deep Dive Summary\n\n")
        f.write("## Key Findings\n\n")
        
        total_aiin = sum(folio_data[fol]['counts'].get('aiin', 0) for fol in TARGET_FOLIOS)
        f.write(f"- Total `aiin` occurrences across folios: {total_aiin}\n")
        
        # Check if aiin appears in rings/labels
        ring_aiin_lines = []
        for folio in TARGET_FOLIOS:
            for l in folio_data[folio]['lines']:
                if 'aiin' in l['words'] and l['location_type'] in ['Ring', 'Label']:
                     ring_aiin_lines.append(l)
        
        f.write(f"- `aiin` in Rings/Labels: {len(ring_aiin_lines)}\n")
        
        if len(ring_aiin_lines) > 0:
            f.write("- **Confirmation**: `aiin` appears in positions suggesting it is a label for a heavenly body or star.\n")
            f.write("\n### Examples in Rings/Labels:\n")
            for l in ring_aiin_lines:
                f.write(f"- {l['folio']} {l['location_id']} ({l['location_type']}): {l['text']}\n")
        else:
            f.write("- **Observation**: `aiin` does not appear as a standalone label in the identified rings/labels.\n")

        f.write("\n## Dictionary Coverage\n")
        # Simple coverage stat
        all_words = []
        for folio in TARGET_FOLIOS:
            all_words.extend(folio_data[folio]['words'])
        
        unique_all = set(all_words)
        known = [w for w in unique_all if w in dictionary]
        coverage = len(known) / len(unique_all) if unique_all else 0
        
        f.write(f"- Unique words: {len(unique_all)}\n")
        f.write(f"- Known words: {len(known)}\n")
        f.write(f"- Coverage: {coverage:.1%}\n")

if __name__ == "__main__":
    main()
