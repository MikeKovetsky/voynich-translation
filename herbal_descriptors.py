#!/usr/bin/env python3
import re
import json
from collections import defaultdict, Counter
from pathlib import Path

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

INPUT_TEXT = 'data/eva_ivtff.txt'
MASTER_DICT = 'results/master_dictionary_v6.json'
OUTPUT_REPORT = 'results/herbal_descriptors_report.md'
OUTPUT_JSON = 'results/descriptor_mapping.json'

# Known Plant Attributes (derived from results/plant_identifications.json and visual inspection context)
# In a full research scenario, this would be loaded from a comprehensive visual database.
# For this task, we use the high-confidence identifications and mappings we have.
PLANT_METADATA = {
    'f17r': {'color': ['blue', 'purple'], 'leaves': 'linear', 'root': 'fibrous'}, # Cornflower
    'f6r':  {'color': ['red'], 'leaves': 'lobed', 'root': 'taproot'},            # Poppy (inferred Red)
    'f5r':  {'color': ['white', 'green'], 'leaves': 'palmate', 'root': 'spreading'}, # Hellebore
    'f2v':  {'color': ['pink', 'red'], 'leaves': 'round', 'root': 'tuber'},      # Cyclamen
    'f25v': {'color': ['green', 'red'], 'leaves': 'palmate', 'root': 'fibrous'}, # Castor Bean
    'f17v': {'color': ['unknown'], 'leaves': 'unknown', 'root': 'unknown'},
    'f3r':  {'color': ['green', 'yellow'], 'leaves': 'succulent', 'root': 'fibrous'}, # Aloe
    'f9r':  {'color': ['green'], 'leaves': 'lobed', 'root': 'woody'},            # Oak
    # Adding some hypothetical mappings based on task hints
    # The task asks to check 'dam' (red) on pages with Red plants.
    # We will assume pages with 'dam' might be red if we don't know.
    # But better to test the hypothesis: Does 'dam' appear on KNOWN red pages?
}

# Words to investigate
TARGET_WORDS = {
    'red': ['dam'],
    'yellow': ['old'],
    'white': ['olk', 'or'],
    'big': ['dal'],
    'small': ['par'],
    'blue_root': [] # No specific word given, but will look for correlations
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def load_text_data(filepath):
    """Parses the EVA text file into a dictionary: {folio: [words]}"""
    pages = defaultdict(list)
    current_folio = None
    
    # Pattern to extract folio from line ID: <f17r.P.1>
    # Line format example: f17r.P.1:    word.word.word-
    line_pattern = re.compile(r'^(f\d+[rv])\.[A-Z0-9]+\.(\d+):\s+(.*)$')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            match = line_pattern.match(line)
            if match:
                folio, line_num, content = match.groups()
                
                # Clean content: remove uncertain characters, expand abbreviations if needed
                # For now, simple splitting by '.'
                clean_content = re.sub(r'[-=]', '', content) # Remove line breaks
                words = [w for w in clean_content.split('.') if w and w.strip()]
                
                pages[folio].extend(words)
    
    return pages

def calculate_hit_rate(pages, target_words, target_folios):
    """
    Calculates how often target words appear on target folios vs other folios.
    """
    target_hits = 0
    target_word_count = 0
    
    other_hits = 0
    other_word_count = 0
    
    for folio, words in pages.items():
        # Only consider Herbal pages (f1r - f66r roughly, or those in PLANT_METADATA)
        # For this specific test, we compare "Target Folios" vs "All Other Pages"
        
        is_target = folio in target_folios
        
        # Count occurrences
        count = sum(1 for w in words if w in target_words)
        total = len(words)
        
        if is_target:
            target_hits += count
            target_word_count += total
        else:
            other_hits += count
            other_word_count += total
            
    target_rate = (target_hits / target_word_count * 1000) if target_word_count > 0 else 0
    other_rate = (other_hits / other_word_count * 1000) if other_word_count > 0 else 0
    
    return {
        'target_hits': target_hits,
        'target_total_words': target_word_count,
        'target_rate_per_1k': target_rate,
        'other_hits': other_hits,
        'other_total_words': other_word_count,
        'other_rate_per_1k': other_rate,
        'ratio': target_rate / other_rate if other_rate > 0 else 0
    }

def analyze_first_words(pages):
    """Analyzes the first word of the first sentence of each page."""
    first_words = []
    
    # Sort folios to ensure order (though not strictly necessary for counting)
    sorted_folios = sorted(pages.keys())
    
    for folio in sorted_folios:
        words = pages[folio]
        if words:
            first_words.append(words[0])
            
    return Counter(first_words)

def analyze_size_descriptors(pages, metadata):
    """Analyzes correlation between descriptors and leaf/plant size."""
    # Group pages by leaf type
    palmate_pages = [f for f, m in metadata.items() if 'palmate' in m.get('leaves', '')]
    linear_pages = [f for f, m in metadata.items() if 'linear' in m.get('leaves', '')]
    small_pages = [f for f, m in metadata.items() if 'small' in m.get('leaves', '')] # Hypothesized
    
    # Words to check
    big_words = ['dal']
    small_words = ['par']
    
    results = {}
    
    # Check 'dal' on Palmate (assumed big) vs Linear (assumed small/thin)
    if palmate_pages:
        results['dal_palmate'] = calculate_hit_rate(pages, big_words, palmate_pages)
    if linear_pages:
        results['dal_linear'] = calculate_hit_rate(pages, big_words, linear_pages)
        
    return results

def run_analysis():
    print("Loading text data...")
    pages = load_text_data(INPUT_TEXT)
    print(f"Loaded {len(pages)} pages.")
    
    report_lines = []
    report_lines.append("# Herbal Descriptor Analysis Report")
    report_lines.append(f"**Date:** {json.dumps(str(Path(OUTPUT_REPORT).stat().st_mtime if Path(OUTPUT_REPORT).exists() else 'Now'))}")
    report_lines.append("\n## 1. Color Mapping Analysis")
    
    # 1. Color Mapping
    # Define target groups based on metadata
    red_pages = [f for f, m in PLANT_METADATA.items() if 'red' in m.get('color', [])]
    yellow_pages = [f for f, m in PLANT_METADATA.items() if 'yellow' in m.get('color', [])]
    white_pages = [f for f, m in PLANT_METADATA.items() if 'white' in m.get('color', [])]
    blue_pages = [f for f, m in PLANT_METADATA.items() if 'blue' in m.get('color', [])]
    
    color_tests = [
        ('Red', ['dam'], red_pages),
        ('Yellow', ['old'], yellow_pages),
        ('White', ['olk', 'or'], white_pages),
        ('Blue', [], blue_pages) # No word hypothesis yet
    ]
    
    report_lines.append("| Color | Target Word | Target Pages | Rate (per 1k) | Baseline Rate | Ratio |")
    report_lines.append("|-------|-------------|--------------|---------------|---------------|-------|")
    
    for color, words, target_folios in color_tests:
        if not words and not target_folios: continue
        if not words: 
            report_lines.append(f"| {color} | (None) | {len(target_folios)} | - | - | - |")
            continue
            
        stats = calculate_hit_rate(pages, words, target_folios)
        report_lines.append(f"| {color} | {', '.join(words)} | {len(target_folios)} | {stats['target_rate_per_1k']:.2f} | {stats['other_rate_per_1k']:.2f} | {stats['ratio']:.2f}x |")

    report_lines.append("\n## 2. Size/Shape Descriptors")
    
    # 2. Size/Shape
    size_results = analyze_size_descriptors(pages, PLANT_METADATA)
    
    report_lines.append("\n### Hypothesis: 'dal' = Big/Great")
    if 'dal_palmate' in size_results:
        s = size_results['dal_palmate']
        report_lines.append(f"- **On Palmate (Large) Leaves:** {s['target_rate_per_1k']:.2f} per 1k words (Ratio: {s['ratio']:.2f}x)")
    if 'dal_linear' in size_results:
        s = size_results['dal_linear']
        report_lines.append(f"- **On Linear (Narrow) Leaves:** {s['target_rate_per_1k']:.2f} per 1k words (Ratio: {s['ratio']:.2f}x)")

    report_lines.append("\n## 3. The 'This is' Pattern (First Words)")
    
    # 3. First Words
    first_word_counts = analyze_first_words(pages)
    top_starts = first_word_counts.most_common(10)
    
    report_lines.append("| Word | Count | Possible Meaning |")
    report_lines.append("|------|-------|------------------|")
    
    # Load dictionary for meanings if available
    dictionary = {}
    try:
        with open(MASTER_DICT, 'r') as f:
            d = json.load(f)
            dictionary = d.get('entries', {})
    except FileNotFoundError:
        pass

    for word, count in top_starts:
        meaning = dictionary.get(word, {}).get('meaning', '???')
        report_lines.append(f"| `{word}` | {count} | {meaning} |")

    # Write Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Report generated: {OUTPUT_REPORT}")
    
    # Write JSON mapping
    with open(OUTPUT_JSON, 'w') as f:
        json.dump({
            'metadata_used': PLANT_METADATA,
            'first_word_stats': dict(first_word_counts),
            'color_stats': {
                'red': calculate_hit_rate(pages, ['dam'], red_pages),
                'yellow': calculate_hit_rate(pages, ['old'], yellow_pages)
            }
        }, f, indent=2)
    print(f"JSON mapping saved: {OUTPUT_JSON}")

if __name__ == '__main__':
    run_analysis()
