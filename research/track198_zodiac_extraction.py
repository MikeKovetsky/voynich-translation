import json
import re
import os
import csv
from collections import Counter, defaultdict

# Constants
IVTFF_PATH = 'data/eva_ivtff.txt'
ZODIAC_PLANTS_PATH = 'results/zodiac_plants.json'
OUTPUT_CSV = 'results/zodiac_herbal_map.csv'
OUTPUT_SUMMARY = 'results/track-198-results_summary.md'

TARGET_SIGNS = {
    "Taurus", "Gemini", "Cancer", "Leo", "Libra", 
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
}

# Manual mapping if json is incomplete
# Based on standard Voynich structure
DEFAULT_ZODIAC_MAPPING = {
    "f70r1": "Pisces", "f70r2": "Pisces",
    "f70v1": "Aries", "f70v2": "Aries",
    "f71r": "Taurus", 
    "f71v": "Gemini",
    "f72r1": "Cancer",
    "f72r2": "Leo",
    "f72r3": "Virgo",
    "f72v1": "Libra",
    "f72v2": "Scorpio",
    "f72v3": "Sagittarius",
    "f73r": "Capricorn",
    "f73v": "Aquarius"
}

def parse_ivtff_structured(path):
    """
    Parses IVTFF to return pages[page_id] = [ [word, ...], [word, ...] ]
    Each inner list is a line.
    """
    pages = defaultdict(list)
    line_regex = re.compile(r'^<([^>]+)>\s+(.*)$')
    page_lines = {} # (page_id, line_id) -> (priority, words)

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('<'): continue
            
            match = line_regex.match(line)
            if not match: continue
            
            tag_content = match.group(1)
            text_content = match.group(2)
            
            parts = tag_content.split('.')
            page_id = parts[0]
            
            priority = 1
            if ';H' in tag_content: priority = 4
            elif ';C' in tag_content: priority = 3
            elif ';U' in tag_content: priority = 2
            
            # Line ID (simplified)
            line_id = tag_content.split(';')[0]
            
            if (page_id, line_id) not in page_lines or priority > page_lines[(page_id, line_id)][0]:
                clean_text = re.sub(r'<![^>]*>', '', text_content)
                clean_text = re.sub(r'\{[^}]*\}', '', clean_text)
                clean_text = re.sub(r'[^a-z0-9. ]', '', clean_text)
                words = [w for w in clean_text.split('.') if w]
                if words:
                    page_lines[(page_id, line_id)] = (priority, words)

    # Sort lines by line_id and assemble
    # line_id usually like f70r1.1, f70r1.P.1, etc.
    # We group by page
    pages_temp = defaultdict(list)
    for (pid, lid), (prio, words) in page_lines.items():
        pages_temp[pid].append((lid, words))
        
    for pid, lines in pages_temp.items():
        # Sort by line id (string sort is okay-ish for basic ordering)
        lines.sort(key=lambda x: x[0])
        pages[pid] = [words for lid, words in lines]
        
    return pages

def get_flat_pages(structured_pages):
    flat = {}
    for pid, lines in structured_pages.items():
        all_words = []
        for line in lines:
            all_words.extend(line)
        flat[pid] = all_words
    return flat

def get_corpus_frequency(flat_pages):
    all_words = []
    for words in flat_pages.values():
        all_words.extend(words)
    return Counter(all_words)

def identify_herbal_pages(all_page_ids):
    herbal = []
    for pid in all_page_ids:
        match = re.match(r'f(\d+)[rv]?', pid)
        if match:
            num = int(match.group(1))
            # Standard herbal ranges: 1-66, 87-102
            if (1 <= num <= 66) or (87 <= num <= 102):
                herbal.append(pid)
    return set(herbal)

def main():
    print("Parsing IVTFF...")
    pages_struct = parse_ivtff_structured(IVTFF_PATH)
    pages_flat = get_flat_pages(pages_struct)
    corpus_freq = get_corpus_frequency(pages_flat)
    print(f"Total pages parsed: {len(pages_flat)}")
    print(f"Corpus size: {len(corpus_freq)} unique words.")

    # Zodiac Mapping
    zodiac_map = DEFAULT_ZODIAC_MAPPING.copy()
    if os.path.exists(ZODIAC_PLANTS_PATH):
        try:
            with open(ZODIAC_PLANTS_PATH, 'r') as f:
                data = json.load(f)
                for page, info in data.items():
                    if 'sign' in info:
                        zodiac_map[page] = info['sign']
        except Exception as e:
            print(f"Warning: Could not load {ZODIAC_PLANTS_PATH}: {e}")
            
    # Identify target pages
    target_pages = [p for p, s in zodiac_map.items() if s in TARGET_SIGNS]
    print(f"Processing {len(target_pages)} Zodiac pages for signs: {TARGET_SIGNS}")
    
    # Herbal Pages
    herbal_pages = identify_herbal_pages(pages_flat.keys())
    print(f"Herbal pages count: {len(herbal_pages)}")
    
    matches = []
    
    for z_page in target_pages:
        if z_page not in pages_flat:
            print(f"Skipping {z_page} (no text found)")
            continue
            
        sign = zodiac_map[z_page]
        z_words = pages_flat[z_page]
        
        # Extract nouns
        candidates = set()
        for w in z_words:
            # Condition: o- prefix OR unique/rare
            # "Unique" interpreted as freq <= 5 in whole corpus (or maybe freq <= 2?)
            # Let's use freq <= 10 to be generous, or startswith o
            if w.startswith('o') or corpus_freq[w] <= 5:
                candidates.add(w)
                
        print(f"  {sign} ({z_page}): {len(candidates)} candidate nouns")
        
        # Search in Herbal
        for word in candidates:
            for h_page in herbal_pages:
                if h_page not in pages_struct: continue
                
                h_lines = pages_struct[h_page]
                h_words_flat = pages_flat[h_page]
                
                if word in h_words_flat:
                    # Check Constraints
                    h_counts = Counter(h_words_flat)
                    count = h_counts[word]
                    
                    # Label: First word of any line?
                    is_label = False
                    for line in h_lines:
                        if line and line[0] == word:
                            is_label = True
                            break
                            
                    # High Frequency: > 1 (appears more than once on the page)
                    is_high_freq = count >= 2
                    
                    if is_label or is_high_freq:
                        matches.append({
                            "Sign": sign,
                            "ZodiacPage": z_page,
                            "Word": word,
                            "HerbalPage": h_page,
                            "Count": count,
                            "IsLabel": is_label,
                            "Type": "Label" if is_label else "HighFreq"
                        })
                        
    # Write CSV
    print(f"Found {len(matches)} links.")
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Sign", "ZodiacPage", "Word", "HerbalPage", "Count", "IsLabel", "Type"])
        writer.writeheader()
        writer.writerows(matches)
        
    # Write Summary
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("# Track 198 Results Summary\n\n")
        f.write(f"Processed Signs: {', '.join(sorted(TARGET_SIGNS))}\n")
        f.write(f"Total Links Found: {len(matches)}\n\n")
        f.write("## Top Matches\n")
        
        # Group by Sign
        by_sign = defaultdict(list)
        for m in matches:
            by_sign[m['Sign']].append(m)
            
        for sign in sorted(by_sign.keys()):
            ms = by_sign[sign]
            f.write(f"\n### {sign} ({len(ms)} links)\n")
            # Show top 5 by count
            top_ms = sorted(ms, key=lambda x: x['Count'], reverse=True)[:5]
            for tm in top_ms:
                f.write(f"- **{tm['Word']}** found on {tm['HerbalPage']} (Count: {tm['Count']}, Label: {tm['IsLabel']})\n")

if __name__ == "__main__":
    main()
