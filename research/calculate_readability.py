import json
import re
import os

# Paths
DICTIONARY_PATH = 'results/dictionary/dictionary_v10_0.json'
MANUSCRIPT_DATA_PATH = 'web/src/data/manuscript_data.json'
OUTPUT_REPORT = 'results/final_readability_stats.md'
OUTPUT_SUMMARY = 'results/track-219-results_summary.md'

# Section definitions
SECTIONS = {
    'Herbal': (1, 66),
    'Astro': (67, 73),
    'Bio': (75, 84),
    'Recipes': (103, 116)
}

def get_page_number(folio):
    # Extract number from f1r, f100v etc
    match = re.match(r'f(\d+)[rv]', folio)
    if match:
        return int(match.group(1))
    return 0

def get_section(folio):
    page_num = get_page_number(folio)
    for section, (start, end) in SECTIONS.items():
        if start <= page_num <= end:
            return section
    return 'Other'

def clean_token(token):
    # Remove <...> tags
    token = re.sub(r'<[^>]+>', '', token)
    # Remove backticks if any (though we split line by line)
    token = token.replace('`', '')
    return token.strip()

def load_data():
    print("Loading dictionary...")
    with open(DICTIONARY_PATH, 'r') as f:
        dictionary = json.load(f)
    
    print("Loading manuscript data...")
    with open(MANUSCRIPT_DATA_PATH, 'r') as f:
        manuscript = json.load(f)
        
    return dictionary, manuscript

def calculate_stats():
    dictionary_data, manuscript_data = load_data()
    dictionary = dictionary_data.get('entries', {})
    
    total_words = 0
    found_words = 0
    
    section_stats = {sec: {'total': 0, 'found': 0} for sec in SECTIONS.keys()}
    section_stats['Other'] = {'total': 0, 'found': 0}
    
    # Process each page
    for folio, data in manuscript_data.items():
        section = get_section(folio)
        
        # Get text from structured lines to ensure we get all lines
        lines = data.get('structured_lines', [])
        
        for line in lines:
            text = line.get('text', '')
            # Remove backticks
            text = text.replace('`', '')
            # Split by dot
            tokens = text.split('.')
            
            for token in tokens:
                cleaned = clean_token(token)
                if not cleaned:
                    continue
                
                # Check if word exists in dictionary and has confidence > 0
                in_dict = False
                if cleaned in dictionary:
                    entry = dictionary[cleaned]
                    if entry.get('confidence', 0) > 0.0:
                        in_dict = True
                
                total_words += 1
                section_stats[section]['total'] += 1
                
                if in_dict:
                    found_words += 1
                    section_stats[section]['found'] += 1
                    
    # Calculate percentages
    overall_coverage = (found_words / total_words * 100) if total_words > 0 else 0
    
    print(f"Total Words: {total_words}")
    print(f"Found Words: {found_words}")
    print(f"Overall Coverage: {overall_coverage:.2f}%")
    
    report_lines = []
    report_lines.append("# Final Readability Statistics (Dictionary v10.0)")
    report_lines.append("")
    report_lines.append("## Overall Corpus")
    report_lines.append(f"- **Total Tokens**: {total_words:,}")
    report_lines.append(f"- **Translated Tokens**: {found_words:,}")
    report_lines.append(f"- **Global Coverage**: {overall_coverage:.2f}%")
    report_lines.append("")
    report_lines.append("## Section Analysis")
    report_lines.append("| Section | Total Tokens | Translated | Coverage |")
    report_lines.append("|---------|--------------|------------|----------|")
    
    for section in ['Herbal', 'Astro', 'Bio', 'Recipes', 'Other']:
        stats = section_stats[section]
        total = stats['total']
        found = stats['found']
        pct = (found / total * 100) if total > 0 else 0
        report_lines.append(f"| {section} | {total:,} | {found:,} | {pct:.2f}% |")
        
    # Write report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(report_lines))
        
    # Write summary
    summary_lines = []
    summary_lines.append("# Track 219 Results Summary")
    summary_lines.append("")
    summary_lines.append("## Key Findings")
    summary_lines.append(f"1. Achieved **{overall_coverage:.1f}%** total coverage across the entire corpus.")
    
    # Find best section
    best_section = max(SECTIONS.keys(), key=lambda s: section_stats[s]['found'] / section_stats[s]['total'] if section_stats[s]['total'] > 0 else 0)
    best_pct = (section_stats[best_section]['found'] / section_stats[best_section]['total'] * 100)
    summary_lines.append(f"2. Highest readability in **{best_section}** section ({best_pct:.1f}%).")
    
    summary_lines.append("")
    summary_lines.append("## Artifacts")
    summary_lines.append(f"- `{OUTPUT_REPORT}`")
    
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write('\n'.join(summary_lines))

if __name__ == '__main__':
    calculate_stats()
