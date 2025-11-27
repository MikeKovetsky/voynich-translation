import os
import json
import re
from collections import defaultdict

# Configuration
INPUT_FILE = 'data/eva_ivtff.txt'
OUTPUT_JSON = 'results/grammar_density_map.json'
OUTPUT_MD = 'results/track-280-results_summary.md'

# Markers
MARKERS = {
    'imperative_suffix': 'y',  # ends with -y
    'ingredient_prefix': 'ol', # starts with ol-
    'process_suffix': 'ed',    # ends with -ed
    'standard_command': 'daiin' # exact match
}

SECTION_RANGES = {
    'Herbal (Q1-Q8)': (1, 66),
    'Bio (Q11)': (75, 84),
    'Pharma (Q13)': (87, 96),
    'Recipes (Q19-Q20)': (103, 116)
}

def parse_eva_line(line):
    """
    Parses a line from EVA IVTFF file.
    Format: <PageID.LineID>Text
    Example: <1r.1>fa19s.9,hae.ay.Akam...
    Returns: (page_id, list_of_words)
    """
    line = line.strip()
    if not line.startswith('<'):
        return None, []
    
    match = re.match(r'<([^>]+)>(.*)', line)
    if not match:
        return None, []
    
    ref_id = match.group(1) # e.g., 1r.1 or f1r.1 (need to normalize)
    text = match.group(2)
    
    # Extract Page ID (remove line number)
    if '.' in ref_id:
        page_id = ref_id.split('.')[0]
    else:
        page_id = ref_id
        
    # Normalize page_id to start with 'f'
    if not page_id.startswith('f') and page_id[0].isdigit():
        page_id = 'f' + page_id

    # Remove comments
    text = re.sub(r'\{.*?\}', '', text)
    
    # Split into words
    words = re.split(r'[.,\s]+', text)
    
    clean_words = []
    for w in words:
        w = w.strip()
        # Remove punctuation
        w_clean = re.sub(r'[^a-zA-Z0-9]', '', w) 
        if w_clean:
            clean_words.append(w_clean)
            
    return page_id, clean_words

def analyze_page(words):
    marker_count = 0
    total_words = len(words)
    
    if total_words == 0:
        return 0, 0
        
    for word in words:
        # Check Standard Command
        if word == MARKERS['standard_command']:
            marker_count += 1
        
        # Check Imperative Suffix -y
        elif word.endswith(MARKERS['imperative_suffix']):
             marker_count += 1
             
        # Check Process Suffix -ed
        elif word.endswith(MARKERS['process_suffix']):
            marker_count += 1
            
        # Check Ingredient Prefix ol-
        elif word.startswith(MARKERS['ingredient_prefix']):
            marker_count += 1
            
    return marker_count, total_words

def get_page_number(page_id):
    # Extract number from f1r, f103v, etc.
    match = re.search(r'f(\d+)', page_id)
    if match:
        return int(match.group(1))
    return 0

def main():
    print(f"Reading {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    page_data = defaultdict(list)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'): continue
            page_id, words = parse_eva_line(line)
            if page_id:
                page_data[page_id].extend(words)
    
    print(f"Processed {len(page_data)} pages.")
    
    density_map = {}
    
    # Calculate density
    for page_id, words in page_data.items():
        marker_count, total_words = analyze_page(words)
        if total_words > 0:
            score = marker_count / total_words
            density_map[page_id] = round(score, 4)
        else:
            density_map[page_id] = 0.0
            
    # Sort by density desc
    sorted_density = dict(sorted(density_map.items(), key=lambda item: item[1], reverse=True))
    
    # Save JSON
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(sorted_density, f, indent=4)
    print(f"Saved map to {OUTPUT_JSON}")
    
    # Analyze Sections
    section_stats = {}
    
    for section_name, (start, end) in SECTION_RANGES.items():
        pages_in_section = []
        scores = []
        for page, score in density_map.items():
            pg_num = get_page_number(page)
            if start <= pg_num <= end:
                pages_in_section.append(page)
                scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        section_stats[section_name] = avg_score

    # Generate Markdown Report
    with open(OUTPUT_MD, 'w') as f:
        f.write("# Grammar Density Map (Track 280) Analysis\n\n")
        f.write("## Overview\n")
        f.write("This analysis calculates the density of 'Recipe Grammar' markers (Imperatives, Ingredients, Processes) across the manuscript sections.\n\n")
        
        f.write("## Markers Used\n")
        f.write(f"- Imperative Suffix: `-{MARKERS['imperative_suffix']}`\n")
        f.write(f"- Ingredient Prefix: `{MARKERS['ingredient_prefix']}-`\n")
        f.write(f"- Process Suffix: `-{MARKERS['process_suffix']}`\n")
        f.write(f"- Standard Command: `{MARKERS['standard_command']}`\n\n")
        
        f.write("## Section Analysis\n")
        f.write("| Section | Average Density | Interpretation |\n")
        f.write("|---|---|---|\n")
        for name, avg in section_stats.items():
            interp = "High (Instructional)" if avg > 0.4 else "Medium/Mixed" if avg > 0.2 else "Low (Narrative)"
            f.write(f"| {name} | **{avg:.4f}** | {interp} |\n")
        f.write("\n")
        
        f.write("## Top High Density Pages (Potential Recipes)\n")
        for page in list(sorted_density.keys())[:20]:
            f.write(f"- {page}: {sorted_density[page]}\n")
        f.write("\n")
        
        f.write("## Low Density Pages (Narrative/Descriptive)\n")
        for page in list(sorted_density.keys())[-20:]:
             f.write(f"- {page}: {sorted_density[page]}\n")
        f.write("\n")
        
        f.write("## Conclusion\n")
        # Determine the most instructional section
        max_section = max(section_stats, key=section_stats.get)
        f.write(f"The **{max_section}** section shows the highest density of grammar markers, suggesting it is the most 'Instructional' or 'Recipe-like' part of the manuscript.\n")
        
        if section_stats['Recipes (Q19-Q20)'] > section_stats['Herbal (Q1-Q8)']:
             f.write("The traditional Recipe section confirms its instructional nature compared to the Herbal section.\n")

    print(f"Saved report to {OUTPUT_MD}")

if __name__ == "__main__":
    main()
