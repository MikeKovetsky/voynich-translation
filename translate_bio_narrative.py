import json
import re
import os

def load_dictionary(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at {path}")
        return {}

def clean_text(text):
    # Remove tags like <...>
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special marker characters often found in IVTFF like !, ?, %, *
    text = text.replace('!', '').replace('?', '').replace('%', '').replace('*', '')
    # Replace dots with spaces (common in EVA for word separation)
    text = text.replace('.', ' ')
    # Collapse spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_eva_file(path, target_folios):
    # Structure: { "f75r.P.1": { "H": "text...", "C": "text..." } }
    paragraph_variants = {}
    
    # Priority list for transcribers
    priority = ['H', 'C', 'F', 'U', 'M'] 
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Pattern: <f75r.P.1;H> or <f75r.1;H> etc.
                # Trying to match <folio.unit;transcriber> text
                match = re.match(r'<([a-z0-9]+)\.([^;>]+);?([a-zA-Z0-9]*)?>+(.*)', line)
                if match:
                    folio = match.group(1)
                    unit_id = match.group(2)
                    transcriber = match.group(3) if match.group(3) else 'Unknown'
                    text = match.group(4).strip()
                    
                    if folio in target_folios:
                        full_id = f"{folio}.{unit_id}"
                        if full_id not in paragraph_variants:
                            paragraph_variants[full_id] = {}
                        
                        paragraph_variants[full_id][transcriber] = text
                        
    except FileNotFoundError:
        print(f"Error: EVA data file not found at {path}")
        
    # Select best variant
    final_paragraphs = []
    
    # Sort by folio/unit naturally
    sorted_keys = sorted(paragraph_variants.keys(), key=lambda x: (
        int(re.search(r'f(\d+)', x).group(1)) if re.search(r'f(\d+)', x) else 0,
        x
    ))
    
    for pid in sorted_keys:
        variants = paragraph_variants[pid]
        selected_text = ""
        selected_source = ""
        
        # Try priority list
        for t in priority:
            if t in variants:
                selected_text = variants[t]
                selected_source = t
                break
        
        # Fallback to first available if none in priority list
        if not selected_text and variants:
            selected_source = list(variants.keys())[0]
            selected_text = variants[selected_source]
            
        if selected_text:
            final_paragraphs.append({
                'id': pid,
                'folio': pid.split('.')[0],
                'unit': pid.split('.', 1)[1],
                'transcriber': selected_source,
                'text': clean_text(selected_text)
            })
            
    return final_paragraphs

def translate_text(text, dictionary):
    words = text.split() # Split by spaces
    translated_words = []
    
    # Extended lists based on task description + common sense
    medical_verbs = ["cure", "heal", "wash", "cleanse", "treat", "remedy", "mix", "drink", "apply", "boil", "extract", "infuse"]
    sensation_words = ["hot", "cold", "pain", "burn", "ache", "wet", "dry", "warm", "cool", "sweet", "bitter", "sour"]
    
    found_medical = []
    found_sensation = []

    for word in words:
        # Strip punctuation attached to word
        clean_word = word.strip(".,;:")
        
        entry = dictionary.get(clean_word)
        translation = word 
        
        if entry:
            meaning = entry.get('meaning', '')
            if meaning:
                # Format meaning
                display_meaning = meaning.upper()
                translation = f"**[{display_meaning}]**" if any(v in meaning.lower() for v in medical_verbs) else \
                             f"*[{display_meaning}]*" if any(s in meaning.lower() for s in sensation_words) else \
                             f"[{display_meaning}]"
                
                if any(v in meaning.lower() for v in medical_verbs):
                    found_medical.append(meaning)
                elif any(s in meaning.lower() for s in sensation_words):
                    found_sensation.append(meaning)
        
        translated_words.append(translation)
        
    return " ".join(translated_words), found_medical, found_sensation

def analyze_structure(text):
    words = text.split()
    if not words:
        return "Unknown"
    
    first_word = words[0].strip(".,;:")
    # Common instruction starters
    if first_word in ['daiin', 'dain', 'daiin', 'day', 'daiiin']: 
        return "Instruction"
    
    return "Description"

def main():
    # Configuration
    dictionary_path = 'results/master_dictionary_v7_3.json'
    data_path = 'data/eva_ivtff.txt'
    output_path = 'results/bio_narrative_full.md'
    
    # Define target folios (Bio section Quire 13)
    # f75r - f84v
    target_folios = set()
    for i in range(75, 85):
        target_folios.add(f"f{i}r")
        target_folios.add(f"f{i}v")
        
    print(f"Loading dictionary from {dictionary_path}...")
    dictionary = load_dictionary(dictionary_path)
    
    print(f"Parsing EVA data from {data_path}...")
    paragraphs = parse_eva_file(data_path, target_folios)
    
    print(f"Processing {len(paragraphs)} unique paragraphs...")
    
    output_lines = []
    output_lines.append("# Bio Narrative Translation (Quire 13)")
    output_lines.append(f"**Source:** {data_path}")
    output_lines.append(f"**Dictionary:** {dictionary_path}")
    output_lines.append("")
    
    current_folio = ""
    
    total_medical = 0
    total_sensation = 0
    structure_counts = {"Instruction": 0, "Description": 0}
    
    for p in paragraphs:
        if p['folio'] != current_folio:
            current_folio = p['folio']
            output_lines.append(f"\n## Folio {current_folio}")
        
        translation, medical, sensation = translate_text(p['text'], dictionary)
        structure = analyze_structure(p['text'])
        
        total_medical += len(medical)
        total_sensation += len(sensation)
        structure_counts[structure] += 1
            
        output_lines.append(f"\n**{p['unit']} ({structure})**")
        output_lines.append(f"> {translation}")
        
        notes = []
        if medical: notes.append(f"**Medical:** {', '.join(set(medical))}")
        if sensation: notes.append(f"*Sensation:* {', '.join(set(sensation))}")
        
        if notes:
            output_lines.append(f"> {' | '.join(notes)}")

    # Summary
    output_lines.insert(4, f"**Summary Statistics:**")
    output_lines.insert(5, f"- Total Paragraphs: {len(paragraphs)}")
    output_lines.insert(6, f"- Instruction Style (starts with daiin): {structure_counts['Instruction']}")
    output_lines.insert(7, f"- Descriptive Style: {structure_counts['Description']}")
    output_lines.insert(8, f"- Medical Terms Found: {total_medical}")
    output_lines.insert(9, f"- Sensation Terms Found: {total_sensation}")
    output_lines.insert(10, "---")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
        
    print(f"Translation complete. Saved to {output_path}")

if __name__ == "__main__":
    main()
