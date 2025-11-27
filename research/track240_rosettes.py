import json
import re
import collections
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
        # Handle structure where entries are nested under "entries"
        if 'entries' in data:
            return data['entries']
        return data

def parse_eva_ivtff(path):
    # Structure: { section_id: [ (line_id, text) ] }
    data = collections.defaultdict(list)
    
    # Regex for the tag: <f86v(section)(\.sub)?;(transcriber)>
    # We prioritize transcriber H.
    
    # First pass: collect all lines by key (section, sub) -> {transcriber: text}
    lines_map = collections.defaultdict(dict)
    
    count_matched = 0
    with open(path, 'r') as f:
        for line in f:
            if not line.startswith('<f86v'):
                continue
            
            # Robust regex: <f86v(ID_PART);(TRANSCRIBER)>[whitespace]TEXT
            match = re.match(r'<f86v([^;>]+);([^>]+)>\s*(.*)', line)
            if match:
                id_part = match.group(1) # e.g. 4.1,@Cc
                transcriber = match.group(2)
                text = match.group(3).strip()
                
                lines_map[id_part][transcriber] = text
                count_matched += 1
            else:
                pass

    print(f"Matched {count_matched} lines.")
    
    # Select best transcriber
    # Priority: H, U, F, m, c
    priority = ['H', 'U', 'F', 'm', 'c']
    
    sorted_keys = sorted(lines_map.keys())
    
    for id_part in sorted_keys:
        # Extract section from id_part (first number)
        section_match = re.match(r'^([0-9]+)', id_part)
        section = section_match.group(1) if section_match else "unknown"
        
        versions = lines_map[id_part]
        selected_text = ""
        for p in priority:
            if p in versions:
                selected_text = versions[p]
                break
        if not selected_text and versions:
             # Fallback to any
            selected_text = list(versions.values())[0]
            
        if selected_text:
            # Clean text
            clean_text = re.sub(r'<[^>]+>', '', selected_text)
            clean_text = clean_text.replace('.', ' ')
            clean_text = ' '.join(clean_text.split())
            
            if clean_text:
                data[section].append(clean_text)
            
    return data

def analyze_elements(text_list):
    # Keys:
    # aiin / daiin (Star/Fire)
    # o / oteos (Earth/Tree)
    # ol / okeedy (Water/Mixture)
    
    counts = collections.Counter()
    found_words = []
    
    targets = {
        'Star (aiin/daiin)': {'aiin', 'daiin'},
        'Earth (o/oteos)': {'o', 'oteos'},
        'Water (ol/okeedy)': {'ol', 'okeedy'}
    }

    # Tokenize
    words = []
    for line in text_list:
        words.extend(line.split())
        
    for w in words:
        w_clean = w.strip(',!?.')
        
        # Check simple exact matches first
        for cat, keywords in targets.items():
            if w_clean in keywords:
                counts[cat] += 1
            
    return counts, words

def translate_words(words, dictionary):
    translations = []
    for w in words:
        w_clean = w.strip(',!?.')
        if w_clean in dictionary:
            entry = dictionary[w_clean]
            defs = []
            if isinstance(entry, dict):
                if 'meaning' in entry:
                    defs = [entry['meaning']]
                elif 'definitions' in entry:
                    defs = entry['definitions']
                elif 'english' in entry:
                    defs = [entry['english']]
            elif isinstance(entry, list):
                defs = entry
            elif isinstance(entry, str):
                defs = [entry]
                
            trans = "/".join(defs[:2]) if defs else "?"
            translations.append(f"{w_clean} ({trans})")
        else:
            translations.append(w_clean)
    return translations

def main():
    dict_path = 'results/dictionary/dictionary.json'
    eva_path = 'data/eva_ivtff.txt'
    output_path = 'results/rosettes_translation.md'
    
    dictionary = load_dictionary(dict_path)
    sections = parse_eva_ivtff(eva_path)
    
    output_lines = []
    output_lines.append("# Track 240: Rosettes Translation (The System Map)")
    output_lines.append("\n## Goal")
    output_lines.append("Translate the Rosettes Foldout (f86v) to validate the 'Flow of Influence' theory (Stars -> Earth -> Water).")
    
    output_lines.append("\n## Analysis by Section")
    
    summary_stats = collections.defaultdict(lambda: collections.Counter())
    
    sorted_sections = sorted(sections.keys(), key=lambda x: int(x) if x.isdigit() else 999)
    
    for sec in sorted_sections:
        text_list = sections[sec]
        counts, words = analyze_elements(text_list)
        
        # Store stats
        summary_stats[sec] = counts
        
        # Translate
        translated = translate_words(words, dictionary)
        
        output_lines.append(f"\n### Section f86v.{sec}")
        output_lines.append(f"**Element Counts:** {dict(counts)}")
        output_lines.append("\n**Extracted Text:**")
        # Limit extracted text length if too long
        full_text = " ".join(words)
        output_lines.append("> " + (full_text[:500] + "..." if len(full_text) > 500 else full_text))
        output_lines.append("\n**Translation:**")
        full_trans = " ".join(translated)
        output_lines.append("> " + (full_trans[:500] + "..." if len(full_trans) > 500 else full_trans))
        
    output_lines.append("\n## Flow of Influence Analysis")
    output_lines.append("| Section | Star (aiin/daiin) | Earth (o/oteos) | Water (ol/okeedy) | Dominant |")
    output_lines.append("|---|---|---|---|---|")
    
    for sec in sorted_sections:
        c = summary_stats[sec]
        s = c['Star (aiin/daiin)']
        e = c['Earth (o/oteos)']
        w = c['Water (ol/okeedy)']
        
        dom = "Mixed"
        if s > e and s > w: dom = "Star"
        elif e > s and e > w: dom = "Earth"
        elif w > s and w > e: dom = "Water"
        
        output_lines.append(f"| f86v.{sec} | {s} | {e} | {w} | {dom} |")

    with open(output_path, 'w') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Analysis complete. Saved to {output_path}")

if __name__ == '__main__':
    main()
