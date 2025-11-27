import re
import json
from collections import Counter
import os

# Config
DATA_FILE = 'data/eva_ivtff.txt'
DICTIONARY_FILE = 'results/dictionary/dictionary.json'
OUTPUT_CANDIDATES = 'results/color_correlation_candidates.json'
OUTPUT_SUMMARY = 'results/track-230-results_summary.md'

RED_PAGES = ['25v', '39v', '57v']
BLUE_PAGES = ['13r', '101v', '34v']

# Transcriber priority
PRIORITY = ['U', 'H', 'F', 'C', 'm']

def parse_eva_data(filepath):
    """
    Parses the IVTFF file and extracts text for each page.
    Returns a dict: { '1r': ['word1', 'word2', ...], ... }
    """
    page_transcriptions = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('<f'):
                continue
            
            # Parse tag: <fPage.Line;Transcriber>
            match = re.match(r'<f(\d+[rv]\d?).*?;([A-Za-z])>', line)
            if not match:
                continue
            
            page_id = match.group(1)
            transcriber = match.group(2)
            
            content_start = line.find('>') + 1
            content = line[content_start:].strip()
            
            # Clean content
            content = re.sub(r'<[^>]+>', '', content) # Remove comments
            content = content.replace('!', '').replace('?', '').replace('*', '').replace('%', '')
            
            # Split words
            # U uses spaces, others often use dots
            content = content.replace('.', ' ')
            words = content.split()
            
            clean_words = []
            for w in words:
                # Remove remaining punctuation or non-word chars
                w = re.sub(r'[^a-z0-9]', '', w)
                if w:
                    clean_words.append(w)
            
            if not clean_words:
                continue

            if page_id not in page_transcriptions:
                page_transcriptions[page_id] = {}
            
            if transcriber not in page_transcriptions[page_id]:
                page_transcriptions[page_id][transcriber] = []
            
            page_transcriptions[page_id][transcriber].extend(clean_words)
            
    # Select best transcription for each page
    final_page_text = {}
    for page_id, trans_dict in page_transcriptions.items():
        selected_words = []
        chosen_transcriber = None
        
        for t in PRIORITY:
            if t in trans_dict:
                selected_words = trans_dict[t]
                chosen_transcriber = t
                break
        
        if not selected_words and trans_dict:
            # Fallback to first available
            chosen_transcriber = list(trans_dict.keys())[0]
            selected_words = trans_dict[chosen_transcriber]
            
        final_page_text[page_id] = selected_words
        # print(f"Page {page_id}: Using transcriber {chosen_transcriber} ({len(selected_words)} words)")
            
    return final_page_text

def analyze_colors(page_text, dictionary):
    red_words = []
    blue_words = []
    
    print("Processing Red Pages...")
    for p in RED_PAGES:
        if p in page_text:
            print(f"  Found {p} ({len(page_text[p])} words)")
            red_words.extend(page_text[p])
        else:
            print(f"  WARNING: Red page {p} not found in data")

    print("Processing Blue Pages...")
    for p in BLUE_PAGES:
        if p in page_text:
            print(f"  Found {p} ({len(page_text[p])} words)")
            blue_words.extend(page_text[p])
        else:
            print(f"  WARNING: Blue page {p} not found in data")
            
    red_counts = Counter(red_words)
    blue_counts = Counter(blue_words)
    
    total_red = len(red_words)
    total_blue = len(blue_words)
    
    print(f"Total Red Words: {total_red}")
    print(f"Total Blue Words: {total_blue}")
    
    candidates = []
    
    # Analyze all unique words found
    all_words = set(red_counts.keys()) | set(blue_counts.keys())
    
    for w in all_words:
        red_freq = red_counts[w]
        blue_freq = blue_counts[w]
        
        # Min total frequency check
        if red_freq + blue_freq < 5:
            continue
            
        red_norm = red_freq / total_red if total_red > 0 else 0
        blue_norm = blue_freq / total_blue if total_blue > 0 else 0
        
        # Avoid division by zero
        ratio_red = (red_norm / blue_norm) if blue_norm > 0 else 999.0
        ratio_blue = (blue_norm / red_norm) if red_norm > 0 else 999.0
            
        # Check Red Spike
        if ratio_red >= 3.0 and red_freq >= 3:
            candidates.append({
                'word': w,
                'color': 'Red',
                'ratio': round(ratio_red, 2),
                'freq_red': red_freq,
                'freq_blue': blue_freq,
                'norm_red': red_norm,
                'norm_blue': blue_norm,
                'known_meaning': dictionary.get(w, None)
            })
            
        # Check Blue Spike
        if ratio_blue >= 3.0 and blue_freq >= 3:
            candidates.append({
                'word': w,
                'color': 'Blue',
                'ratio': round(ratio_blue, 2),
                'freq_red': red_freq,
                'freq_blue': blue_freq,
                'norm_red': red_norm,
                'norm_blue': blue_norm,
                'known_meaning': dictionary.get(w, None)
            })
            
    # Sort by Ratio desc
    candidates.sort(key=lambda x: x['ratio'], reverse=True)
    
    return candidates

def main():
    print("Parsing EVA Data...")
    page_text = parse_eva_data(DATA_FILE)
    print(f"Parsed {len(page_text)} pages.")
    
    print("Loading Dictionary...")
    try:
        with open(DICTIONARY_FILE, 'r') as f:
            data = json.load(f)
            dictionary = data.get('entries', {})
    except FileNotFoundError:
        print("Dictionary not found, using empty.")
        dictionary = {}
        
    print("Analyzing Colors...")
    candidates = analyze_colors(page_text, dictionary)
    
    print(f"Found {len(candidates)} candidates.")
    
    # Save JSON
    with open(OUTPUT_CANDIDATES, 'w') as f:
        json.dump(candidates, f, indent=2)
    print(f"Saved {OUTPUT_CANDIDATES}")
    
    # Generate Summary Markdown
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("# Track 230 Results: The Color Hunt\n\n")
        f.write("## Methodology\n")
        f.write(f"- **Red Pages:** {', '.join(RED_PAGES)}\n")
        f.write(f"- **Blue Pages:** {', '.join(BLUE_PAGES)}\n")
        f.write("- **Metric:** >3x Normalized Frequency Difference (min 3 occurrences).\n\n")
        
        f.write("## Red Candidates (Mars/Hot)\n")
        f.write("| Word | Ratio (Red/Blue) | Freq (R/B) | Dictionary |\n")
        f.write("|---|---|---|---|\n")
        for c in candidates:
            if c['color'] == 'Red':
                meaning_entry = c.get('known_meaning', {}) or {}
                meaning = meaning_entry.get('meaning', '-') if isinstance(meaning_entry, dict) else '-'
                f.write(f"| `{c['word']}` | {c['ratio']}x | {c['freq_red']}/{c['freq_blue']} | {meaning} |\n")
                
        f.write("\n## Blue Candidates (Venus/Cold)\n")
        f.write("| Word | Ratio (Blue/Red) | Freq (B/R) | Dictionary |\n")
        f.write("|---|---|---|---|\n")
        for c in candidates:
            if c['color'] == 'Blue':
                meaning_entry = c.get('known_meaning', {}) or {}
                meaning = meaning_entry.get('meaning', '-') if isinstance(meaning_entry, dict) else '-'
                f.write(f"| `{c['word']}` | {c['ratio']}x | {c['freq_blue']}/{c['freq_red']} | {meaning} |\n")

    print(f"Saved {OUTPUT_SUMMARY}")

if __name__ == "__main__":
    main()
