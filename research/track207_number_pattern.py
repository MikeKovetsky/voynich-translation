
import re
import json
import os
from collections import defaultdict

def parse_ivtff_structure(filepath):
    """
    Parses IVTFF to extract labels based on tags.
    Returns:
        star_labels: {page: [list of words]} (from @Ls)
        zodiac_labels: {page: [list of words]} (from &Lz)
        all_words: [list of all words in the file]
    """
    star_labels = defaultdict(list)
    zodiac_labels = defaultdict(list)
    all_words = []
    
    current_page = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Detect page
            if line.startswith('<'):
                match = re.match(r'<f(\d+[rv]\d*)', line)
                if match:
                    current_page = f"f{match.group(1)}"
            
            # Check for tags
            # We prefer the 'H' version or 'U' if available, or just the first one.
            # Actually, let's just take the line as is and strip the tag.
            # But we must avoid duplicates if multiple versions (H, C, F, U...) exist for the same line ID.
            # The line ID is the part before semicolon e.g. <f68r1.12,@Ls
            
            # Let's just filter for lines containing ";H>" to be consistent (Stolfi/Landini standard)
            if ";H>" not in line:
                 continue
                 
            tag_part = line.split('>')[0]
            content = line.split('>')[-1].strip()
            
            words = re.split(r'[\s\.\,\-]+', content)
            words = [w for w in words if w]
            
            all_words.extend(words)
            
            if current_page:
                base_page = re.match(r'f\d+[rv]', current_page).group(0)
                
                if "@Ls" in tag_part:
                    star_labels[base_page].extend(words)
                elif "&Lz" in tag_part:
                    zodiac_labels[base_page].extend(words)
                    
    return star_labels, zodiac_labels, all_words

def check_sequences(labels):
    """
    Checks for sequential patterns in a list of labels.
    """
    roman_numerals = ['i', 'ii', 'iii', 'iiii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']
    found_roman = [w for w in labels if w in roman_numerals]
    
    # Check for single letter sequences (a, b, c...) or similar glyphs
    # Glyph alphabet: o, y, d, s, r...
    
    return {
        'count': len(labels),
        'roman_like': found_roman,
        'first_5': labels[:5]
    }

def analyze_glyph_sequences(all_words):
    """
    Global search for specific sequences.
    """
    target_glyphs = ['i', 'ii', 'iii', 'iiii', 'iv', 'v', 'vi']
    counts = {g: 0 for g in target_glyphs}
    
    for w in all_words:
        if w in counts:
            counts[w] += 1
            
    # Look for d, r, s sequences in the *list* of words (assuming they appear sequentially)
    drs_count = 0
    drs_found = []
    for i in range(len(all_words) - 2):
        if all_words[i] == 'd' and all_words[i+1] == 'r' and all_words[i+2] == 's':
            drs_count += 1
            drs_found.append(all_words[i:i+3])
            
    return {
        'glyph_counts': counts,
        'drs_sequence_count': drs_count
    }

def main():
    input_file = 'data/eva_ivtff.txt'
    if not os.path.exists(input_file):
        input_file = '../data/eva_ivtff.txt'
        
    print(f"Parsing {input_file}...")
    star_labels, zodiac_labels, all_words = parse_ivtff_structure(input_file)
    
    results = {
        "star_analysis": {},
        "zodiac_analysis": {},
        "glyph_stats": {}
    }
    
    # 1. Star Ring Analysis
    print("\n--- Star Ring Analysis (Labels Only) ---")
    for page, labels in star_labels.items():
        if page in ['f68r', 'f68v', 'f69r', 'f69v']:
            seq_data = check_sequences(labels)
            results["star_analysis"][page] = seq_data
            print(f"Page {page}: {seq_data['count']} labels")

    # 2. Zodiac Degree Marks
    print("\n--- Zodiac Degree Marks (Labels Only) ---")
    zodiac_pages_of_interest = ['f70v', 'f71r', 'f71v', 'f72r', 'f72v', 'f73r', 'f73v']
    for page in zodiac_pages_of_interest:
        if page in zodiac_labels:
            count = len(zodiac_labels[page])
            results["zodiac_analysis"][page] = count
            print(f"Page {page}: {count} labels")
        else:
            print(f"Page {page}: 0 labels found")

    # 3. Glyph Sequences
    print("\n--- Global Glyph Sequences ---")
    glyph_stats = analyze_glyph_sequences(all_words)
    results["glyph_stats"] = glyph_stats
    
    # Save results
    with open('results/number_system.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nSaved results to results/number_system.json")

if __name__ == "__main__":
    main()
