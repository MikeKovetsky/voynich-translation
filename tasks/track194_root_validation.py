import json
import re
import csv
import os

def load_page_types():
    with open('results/page_types.json', 'r') as f:
        return json.load(f)

def parse_ivtff(filepath):
    pages = {}
    current_page = None
    seen_lines = set()
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Check for page header or line start
            # Format: <f1r.P1.1;H>
            # We need to capture the unique line ID to avoid duplicates (multiple transcribers)
            match = re.match(r'<f(\d+[rv])\.([^;]+);([^>]+)>', line)
            if match:
                page_num = match.group(1)
                line_id = match.group(2)
                transcriber = match.group(3)
                
                page_id = 'f' + page_num
                full_line_id = f"{page_id}.{line_id}"
                
                # Strategy: Prefer 'H' transcription, or just take the first one encountered.
                # IVTFF usually groups them. We'll just take the first one we see for each line ID.
                if full_line_id in seen_lines:
                    continue
                seen_lines.add(full_line_id)
                
                if page_id != current_page:
                    current_page = page_id
                    if current_page not in pages:
                        pages[current_page] = []
                
                # Extract text content (after the tag)
                tag_end = line.find('>')
                if tag_end != -1:
                    text_part = line[tag_end+1:].strip()
                    
                    # Remove inline comments/tags like <...>
                    text_part = re.sub(r'<[^>]+>', '', text_part)
                    
                    # Remove uncertainty markers !, ?, *, ,
                    text_part = re.sub(r'[!?*,]', '', text_part)
                    
                    if text_part:
                        pages[current_page].append(text_part)
    return pages

def analyze_positions(pages, page_types):
    herbal_pages = [p for p, t in page_types.items() if t == 'Descriptive']
    
    results = [] # List of (word_type, zone_index)
    
    zone_counts = {
        'Top': {'chol': 0, 'shos': 0},
        'Middle': {'chol': 0, 'shos': 0},
        'Bottom': {'chol': 0, 'shos': 0}
    }
    
    processed_pages = 0
    
    for page_id in herbal_pages:
        if page_id not in pages:
            continue
            
        lines = pages[page_id]
        if not lines:
            continue
            
        processed_pages += 1
        total_lines = len(lines)
        
        # Define zones
        one_third = total_lines / 3.0
        
        for i, line in enumerate(lines):
            if i < one_third:
                zone = 'Top'
                zone_idx = 0
            elif i < 2 * one_third:
                zone = 'Middle'
                zone_idx = 1
            else:
                zone = 'Bottom'
                zone_idx = 2
            
            # Split by dot . or space
            words = re.split(r'[.\s]+', line)
            for word in words:
                clean_word = word.strip()
                if not clean_word:
                    continue
                
                if clean_word == 'chol':
                    zone_counts[zone]['chol'] += 1
                    results.append((0, zone_idx))
                elif clean_word == 'shos':
                    zone_counts[zone]['shos'] += 1
                    results.append((1, zone_idx))
                    
    return zone_counts, results, processed_pages

def calculate_correlation(data):
    if not data:
        return 0.0
    
    n = len(data)
    x = [d[0] for d in data] # Word Type (0=chol, 1=shos)
    y = [d[1] for d in data] # Zone (0, 1, 2)
    
    if len(set(x)) < 2 or len(set(y)) < 2:
        return 0.0
    
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
    sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
    
    denominator = (sum_sq_x * sum_sq_y) ** 0.5
    
    if denominator == 0:
        return 0.0
        
    return numerator / denominator

def main():
    page_types = load_page_types()
    pages = parse_ivtff('data/eva_ivtff.txt')
    
    zone_counts, correlation_data, num_pages = analyze_positions(pages, page_types)
    
    correlation = calculate_correlation(correlation_data)
    
    # Output CSV
    with open('results/anatomical_distribution.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Zone', 'chol (Leaf)', 'shos (Root)'])
        writer.writerow(['Top', zone_counts['Top']['chol'], zone_counts['Top']['shos']])
        writer.writerow(['Middle', zone_counts['Middle']['chol'], zone_counts['Middle']['shos']])
        writer.writerow(['Bottom', zone_counts['Bottom']['chol'], zone_counts['Bottom']['shos']])
        
    # Output Summary
    with open('results/track-194-results_summary.md', 'w') as f:
        f.write('# Task 194: Root Validation Results\n\n')
        f.write(f'## Overview\n')
        f.write(f'- **Pages Analyzed:** {num_pages} (Descriptive/Herbal)\n')
        f.write(f'- **Total Occurrences:** `chol`: {sum(z["chol"] for z in zone_counts.values())}, `shos`: {sum(z["shos"] for z in zone_counts.values())}\n\n')
        
        f.write('## Distribution\n')
        f.write('| Zone | chol (Leaf) | shos (Root) |\n')
        f.write('|---|---|---|\n')
        for zone in ['Top', 'Middle', 'Bottom']:
            f.write(f'| {zone} | {zone_counts[zone]["chol"]} | {zone_counts[zone]["shos"]} |\n')
            
        f.write(f'\n## Correlation\n')
        f.write(f'- **Correlation Coefficient:** {correlation:.4f}\n')
        f.write(f'  - Positive correlation implies `shos` tends towards Bottom and `chol` towards Top (since Leaf=0, Root=1; Top=0, Bot=2).\n')
        
        # Interpretation
        f.write('\n## Hypothesis Check\n')
        if correlation > 0.1:
            f.write('- **Supported:** Positive correlation suggests anatomical alignment.\n')
        elif correlation < -0.1:
            f.write('- **Contradicted:** Negative correlation suggests inverse alignment.\n')
        else:
            f.write('- **Inconclusive:** No significant correlation found.\n')

if __name__ == '__main__':
    main()
