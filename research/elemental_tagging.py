import os
import re
import json

# Configuration
INPUT_FILE = 'data/eva_ivtff.txt'
ZODIAC_MAP_FILE = 'results/zodiac_plants.json'
OUTPUT_JSON = 'results/elemental_page_map.json'
OUTPUT_MD = 'results/track-231-results_summary.md'

# Regex for IVTFF lines
# Format: <f1r.1,@P0;H> text...
# We capture page_id (e.g. 1r), line_num, transcriber, text
LINE_REGEX = re.compile(r'^<f([a-z0-9]+)\.(\d+).*?;(\w)>\s+(.*)$')

# Transcriber preference
TRANSCRIBER_PREF = ['H', 'C', 'F', 'U', 'N', 'm', 'c']

def parse_ivtff(filepath):
    """
    Parses the IVTFF file and returns a dictionary of pages.
    pages[page_id] = [list of tokens]
    """
    print(f"Parsing {filepath}...")
    
    # Store lines: pages[page_id][line_id] = {transcriber: text}
    raw_pages = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('<f'):
                continue
            
            match = LINE_REGEX.match(line)
            if not match:
                continue
            
            page_part, line_num, transcriber, text = match.groups()
            page_id = 'f' + page_part # Prepend 'f' to match standard ID (e.g. f1r)
            
            if page_id not in raw_pages:
                raw_pages[page_id] = {}
            
            if line_num not in raw_pages[page_id]:
                raw_pages[page_id][line_num] = {}
            
            raw_pages[page_id][line_num][transcriber] = text

    # Process into final token lists based on transcriber preference
    final_pages = {}
    
    for page_id, lines in raw_pages.items():
        page_tokens = []
        # Sort lines by line number (handling numeric/alphanumeric sort if needed)
        # Simple string sort might be enough, or numeric if line_num is integer
        # Line IDs in IVTFF can be '1', '2', 'P.1', etc. standard sort is okay.
        sorted_line_nums = sorted(lines.keys(), key=lambda x: float(x) if x.replace('.','',1).isdigit() else 999)
        
        for line_num in sorted_line_nums:
            transcriptions = lines[line_num]
            selected_text = ""
            
            # Pick preferred transcriber
            for t in TRANSCRIBER_PREF:
                if t in transcriptions:
                    selected_text = transcriptions[t]
                    break
            
            if not selected_text and transcriptions:
                selected_text = list(transcriptions.values())[0]
            
            if selected_text:
                # Tokenize
                # Remove tags like <...> 
                clean_text = re.sub(r'<[^>]+>', '', selected_text)
                # Split by dots or spaces (EVA usually uses dots)
                tokens = [t.strip() for t in re.split(r'[.\s]+', clean_text) if t.strip()]
                page_tokens.extend(tokens)
        
        final_pages[page_id] = page_tokens
        
    print(f"Parsed {len(final_pages)} pages.")
    return final_pages

def analyze_pages(pages, zodiac_map):
    """
    Calculates Wetness Index for each page and correlates with Zodiac.
    """
    results = {}
    zodiac_correlation = []
    
    wet_signs = ['Pisces', 'Cancer', 'Scorpio']
    dry_signs = ['Aries', 'Leo', 'Sagittarius']
    
    for page_id, tokens in pages.items():
        count_ol = 0
        count_o = 0
        
        for token in tokens:
            # Clean token: remove non-alpha chars (like !, ?, * from EVA)
            # Keep standard EVA chars (a-z, 0-9 for some extended)
            # Basic EVA is a-z.
            t = re.sub(r'[^a-z0-9]', '', token)
            if not t:
                continue
            
            is_ol = False
            is_o = False
            
            # Check ol pattern: ^ol or ol$
            if t.startswith('ol') or t.endswith('ol'):
                count_ol += 1
                is_ol = True
            
            # Check o pattern: ^o or o$ (excluding if already ol)
            if not is_ol:
                if t.startswith('o') or t.endswith('o'):
                    count_o += 1
                    is_o = True
        
        total = count_ol + count_o
        wetness_index = count_ol / total if total > 0 else 0.0
        
        classification = "Neutral"
        if wetness_index > 0.6:
            classification = "Wet"
        elif wetness_index < 0.4:
            classification = "Dry"
            
        page_result = {
            "count_ol": count_ol,
            "count_o": count_o,
            "wetness_index": round(wetness_index, 3),
            "classification": classification,
            "zodiac_sign": zodiac_map.get(page_id, {}).get("sign", None)
        }
        
        results[page_id] = page_result
        
        # Correlation check
        sign = page_result['zodiac_sign']
        if sign:
            expected = "Neutral"
            if sign in wet_signs:
                expected = "Wet"
            elif sign in dry_signs:
                expected = "Dry"
            
            match = (classification == expected)
            # If expected is Wet/Dry but classification is Neutral, it's a partial mismatch (False)
            # If expected is Neutral (e.g. Taurus), we don't strictly check Wet/Dry match, 
            # but task focuses on Wet/Dry signs.
            
            if expected in ["Wet", "Dry"]:
                zodiac_correlation.append({
                    "page": page_id,
                    "sign": sign,
                    "expected": expected,
                    "actual": classification,
                    "index": wetness_index,
                    "match": match
                })

    return results, zodiac_correlation

def generate_report(results, correlation, output_json, output_md):
    # Save JSON
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print(f"Saved JSON to {output_json}")
    
    # Generate MD
    lines = []
    lines.append("# Track 231: Elemental Page Tagging Results")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"Total Pages Analyzed: {len(results)}")
    
    wet_pages = [p for p, d in results.items() if d['classification'] == 'Wet']
    dry_pages = [p for p, d in results.items() if d['classification'] == 'Dry']
    
    lines.append(f"- Wet Pages (>0.6): {len(wet_pages)}")
    lines.append(f"- Dry Pages (<0.4): {len(dry_pages)}")
    lines.append(f"- Neutral Pages: {len(results) - len(wet_pages) - len(dry_pages)}")
    lines.append("")
    
    lines.append("## Zodiac Correlation Check")
    lines.append("| Page | Sign | Expected | Actual | Index | Match |")
    lines.append("|---|---|---|---|---|---|")
    
    matches = 0
    total_checks = len(correlation)
    
    for item in correlation:
        match_icon = "✅" if item['match'] else "❌"
        if item['match']:
            matches += 1
        lines.append(f"| {item['page']} | {item['sign']} | {item['expected']} | {item['actual']} | {item['index']:.3f} | {match_icon} |")
    
    lines.append("")
    if total_checks > 0:
        accuracy = (matches / total_checks) * 100
        lines.append(f"**Correlation Accuracy:** {accuracy:.1f}% ({matches}/{total_checks})")
    else:
        lines.append("**Correlation Accuracy:** N/A (No Zodiac pages found)")
        
    lines.append("")
    lines.append("## Detailed Page List (Top 20 Wettest)")
    sorted_wet = sorted(results.items(), key=lambda x: x[1]['wetness_index'], reverse=True)[:20]
    for p, d in sorted_wet:
        lines.append(f"- **{p}**: {d['wetness_index']} ({d['count_ol']}/{d['count_o']+d['count_ol']})")

    lines.append("")
    lines.append("## Detailed Page List (Top 20 Driest)")
    sorted_dry = sorted(results.items(), key=lambda x: x[1]['wetness_index'])[:20]
    for p, d in sorted_dry:
        lines.append(f"- **{p}**: {d['wetness_index']} ({d['count_ol']}/{d['count_o']+d['count_ol']})")
        
    with open(output_md, 'w') as f:
        f.write("\n".join(lines))
    print(f"Saved Report to {output_md}")

def main():
    # Load Zodiac Map
    if os.path.exists(ZODIAC_MAP_FILE):
        with open(ZODIAC_MAP_FILE, 'r') as f:
            zodiac_map = json.load(f)
    else:
        print("Warning: Zodiac map not found.")
        zodiac_map = {}
        
    # Parse Corpus
    pages = parse_ivtff(INPUT_FILE)
    
    # Analyze
    results, correlation = analyze_pages(pages, zodiac_map)
    
    # Output
    generate_report(results, correlation, OUTPUT_JSON, OUTPUT_MD)

if __name__ == "__main__":
    main()
