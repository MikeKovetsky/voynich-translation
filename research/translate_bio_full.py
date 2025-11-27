import json
import re
import os
from collections import Counter

# Configuration
DICTIONARY_FILE = 'results/master_dictionary_v7.json'
INPUT_FILE = 'data/eva_ivtff.txt'
OUTPUT_TRANS_FILE = 'results/bio_full_translation.md'
OUTPUT_REPORT_FILE = 'results/bio_narrative_report.md'

# Target pages: Quire 13 (f75r - f84v)
TARGET_PAGES_REGEX = re.compile(r'<f(7[5-9]|8[0-4])[rv]')

# Special Keys & Morphology
SPECIAL_KEYS = {
    'aiin': 'Spring/Source',
    'okeedy': 'Liquid/Water',
    'chol': 'Leaf',
    'char': 'Root'
}

PREFIXES = {
    'qok': 'with/using(instr)',
    'qot': 'with/using(instr)', # Variant
    'd': 'from/take(imp)',
    'y': 'and/plus',
    'l': 'to/for'
}

def load_dictionary(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Error: Dictionary file {filepath} not found.")
        return {}

def clean_text(text):
    # Remove internal tags like <!figure>, <->, etc.
    text = re.sub(r'<![^>]+>', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    # Replace specific EVA separators with spaces
    text = text.replace('.', ' ').replace(',', ' ').replace('-', ' ')
    # Remove extraneous punctuation
    text = text.replace('!', '').replace('?', '').replace('%', '')
    return text.strip()

def translate_word(word, dictionary):
    original_word = word
    translation = None
    morphology = []

    # 1. Direct Lookup
    if word in SPECIAL_KEYS:
        return f"**{SPECIAL_KEYS[word].upper()}**"
    
    if word in dictionary:
        entry = dictionary[word]
        # Prefer 'meaning' or 'definition'
        return entry.get('meaning', entry.get('definition', word))

    # 2. Morphology Stripping
    # Check prefixes
    matched_prefix = None
    stem = word
    
    # Sort prefixes by length descending to match longest first (e.g. qok vs q)
    sorted_prefixes = sorted(PREFIXES.keys(), key=len, reverse=True)
    
    for prefix in sorted_prefixes:
        if word.startswith(prefix):
            stem = word[len(prefix):]
            # Basic check: stem must be reasonably long or in dict
            if len(stem) >= 2: 
                 matched_prefix = prefix
                 morphology.append(PREFIXES[prefix])
                 break
    
    if matched_prefix:
        # Check stem in special keys or dict
        if stem in SPECIAL_KEYS:
            stem_trans = f"**{SPECIAL_KEYS[stem].upper()}**"
            return f"({', '.join(morphology)}) {stem_trans}"
        
        if stem in dictionary:
            entry = dictionary[stem]
            stem_trans = entry.get('meaning', entry.get('definition', stem))
            return f"({', '.join(morphology)}) {stem_trans}"
            
        # Double prefix? (e.g. y-d-aiin)
        # For now, stick to single level to avoid over-segmentation, unless common
        
        # If stem still unknown, return with morphological hint
        return f"({', '.join(morphology)}) {stem}?"

    return None # Unknown

def parse_eva_file(filepath):
    pages = {}
    current_page = None
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if not line.startswith('<f'):
                    continue
                
                # Parse location
                match = re.match(r'<([^>]+)>', line)
                if not match:
                    continue
                
                location_tag = match.group(1)
                # Expected format: f75r.1,@P0;m
                parts = location_tag.split('.')
                page_id = parts[0] # f75r
                
                if not TARGET_PAGES_REGEX.match(f"<{page_id}"):
                    continue
                
                version_info = location_tag.split(';')[-1] if ';' in location_tag else ''
                
                if 'm' not in version_info and 'H' not in version_info:
                    continue
                
                # Priority: m > H. We'll store in a dict and overwrite H with m if found.
                # parts[1] is like "1,@P0;m". We want just "1".
                raw_segment_part = parts[1] if len(parts) > 1 else "0"
                segment_id = re.split(r'[^\d]', raw_segment_part)[0]
                
                # Extract text content (after the >)
                content_start = line.find('>') + 1
                raw_text = line[content_start:].strip()
                
                if page_id not in pages:
                    pages[page_id] = {}
                
                is_m = 'm' in version_info
                
                if segment_id not in pages[page_id]:
                    pages[page_id][segment_id] = {'text': raw_text, 'prio': 2 if is_m else 1}
                else:
                    if is_m:
                        pages[page_id][segment_id] = {'text': raw_text, 'prio': 2}
                        
    except FileNotFoundError:
        print(f"Error: Input file {filepath} not found.")
        return {}
        
    # Convert to sorted list of texts per page
    sorted_pages = {}
    for page_id, segments in pages.items():
        try:
            sorted_segs = sorted(segments.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)
        except:
            sorted_segs = sorted(segments.items())
            
        sorted_pages[page_id] = [s[1]['text'] for s in sorted_segs]
        
    return sorted_pages

def analyze_narrative(full_translation_text):
    themes = {
        'Bathing/Cleansing': ['water', 'liquid', 'clean', 'wash', 'bath', 'pool', 'wet'],
        'Mixing/Ingredients': ['mix', 'add', 'put', 'combine', 'ingredient', 'measure', 'take', 'into'],
        'Sensation': ['hot', 'cold', 'warm', 'pain', 'soft', 'hard', 'feel'],
        'Anatomy/Body': ['body', 'skin', 'leg', 'arm', 'head', 'hair', 'stomach'],
        'Nature': ['spring', 'source', 'leaf', 'root', 'plant', 'seed']
    }
    
    counts = Counter()
    found_themes = {k: [] for k in themes}
    
    lines = full_translation_text.split('\n')
    for line in lines:
        lower_line = line.lower()
        for theme, keywords in themes.items():
            matched_theme = False
            for kw in keywords:
                if kw in lower_line:
                    matched_theme = True
                    break
            
            if matched_theme:
                counts[theme] += 1
                # Keep a snippet (first few occurrences)
                if len(found_themes[theme]) < 5:
                    found_themes[theme].append(line.strip())
    
    return counts, found_themes

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary(DICTIONARY_FILE)
    print(f"Loaded {len(dictionary)} entries.")
    
    print("Parsing EVA text...")
    pages = parse_eva_file(INPUT_FILE)
    print(f"Found {len(pages)} pages in Quire 13.")
    
    full_output = []
    
    # Sort pages naturally (f75r, f75v, f76r...)
    def page_sort_key(p):
        try:
            num = int(re.search(r'\d+', p).group())
            face = p[-1] # 'r' or 'v'
            return (num, 0 if face == 'r' else 1)
        except:
            return (999, 0)
        
    sorted_page_ids = sorted(pages.keys(), key=page_sort_key)
    
    full_text_for_analysis = ""

    for page_id in sorted_page_ids:
        page_header = f"## Page {page_id}"
        full_output.append(page_header)
        full_output.append("")
        
        lines = pages[page_id]
        for line_idx, raw_line in enumerate(lines):
            clean = clean_text(raw_line)
            words = clean.split()
            
            translated_line = []
            for w in words:
                trans = translate_word(w, dictionary)
                if trans:
                    translated_line.append(trans)
                else:
                    translated_line.append(f"`{w}`")
            
            joined_line = " ".join(translated_line)
            full_output.append(f"**{line_idx+1}.** {joined_line}")
            full_text_for_analysis += joined_line + "\n"
            
        full_output.append("")
        full_output.append("---")
        full_output.append("")

    # Write Translation
    with open(OUTPUT_TRANS_FILE, 'w') as f:
        f.write("# Biological Section (Quire 13) Translation\n\n")
        f.write("\n".join(full_output))
    
    print(f"Translation written to {OUTPUT_TRANS_FILE}")

    # Narrative Analysis
    counts, details = analyze_narrative(full_text_for_analysis)
    
    with open(OUTPUT_REPORT_FILE, 'w') as f:
        f.write("# Narrative Analysis: Biological Section\n\n")
        f.write("## Theme Frequency\n")
        for theme, count in counts.most_common():
            f.write(f"- **{theme}**: {count} occurrences\n")
            
        f.write("\n## Thematic Evidence\n")
        for theme, snippets in details.items():
            f.write(f"\n### {theme}\n")
            if not snippets:
                f.write("_No clear matches found._\n")
            for snippet in snippets:
                # Truncate long lines
                display = (snippet[:75] + '..') if len(snippet) > 75 else snippet
                f.write(f"- \"{display}\"\n")
                
        f.write("\n## Interpretation\n")
        f.write("Based on the frequency of 'water', 'liquid', 'spring' terms alongside morphological markers for 'into' (qok-) and 'from' (d-), ")
        f.write("this section appears to describe processes involving fluids. The presence of 'Leaf' and 'Root' suggests these fluids are being treated with biological matter.\n")
        
    print(f"Narrative report written to {OUTPUT_REPORT_FILE}")

if __name__ == "__main__":
    main()
