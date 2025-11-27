import re
import json
from collections import Counter

def parse_eva_file(filepath):
    pages = {}
    current_page = None
    
    with open(filepath, 'r') as f:
        for line in f:
            # Check for page header
            page_match = re.match(r'#\s*<f(\d+[rv])\S*>', line)
            if page_match:
                current_page = 'f' + page_match.group(1)
                pages[current_page] = []
                continue
            
            # Skip comments and headers
            if line.startswith('#'):
                continue
                
            if not current_page:
                continue
                
            # Extract text content (remove line numbers/codes)
            # Format usually: <f1r.1>       word1.word2.word3
            parts = line.strip().split()
            if not parts:
                continue
                
            # Text is usually the last part, but let's be careful
            # EVA text often uses dots as separators
            for part in parts:
                if '<' in part and '>' in part: # Skip codes
                    continue
                
                # Split words by dot
                words = part.split('.')
                for w in words:
                    clean_w = w.strip()
                    # Remove some common EVA markers if present (like - or !)
                    clean_w = re.sub(r'[^a-z0-9]', '', clean_w)
                    if clean_w:
                        pages[current_page].append(clean_w)
                        
    return pages

def main():
    eva_path = 'data/eva_ivtff.txt'
    page_types_path = 'results/page_types.json'
    
    # Load page types
    with open(page_types_path, 'r') as f:
        page_types = json.load(f)
    
    # Parse text
    print(f"Parsing {eva_path}...")
    pages = parse_eva_file(eva_path)
    print(f"Parsed {len(pages)} pages.")
    
    # Filter for Herbal pages (Descriptive + range check for safety)
    # Herbal sections: f1r-f66v (Quire 1-8), f87r-f102v (Quire 15-16/Pharmaceutical/Herbal)
    # Actually, let's rely on the "Descriptive" tag but also keep an eye on the page number.
    
    herbal_pages = []
    for page, content in pages.items():
        # Heuristic: Herbal pages are often "Descriptive"
        # Also explicit ranges
        is_herbal_range = False
        
        # Extract number
        try:
            num = int(re.search(r'\d+', page).group())
            if (1 <= num <= 66) or (87 <= num <= 102):
                is_herbal_range = True
        except:
            pass
            
        # Combine criteria
        # Task says "Herbal pages".
        if is_herbal_range: # Broadest definition
             herbal_pages.append(page)
             
    print(f"Identified {len(herbal_pages)} candidate Herbal pages.")
    
    # Search for 'os' and 'oteos'
    targets = ['os', 'oteos']
    results = []
    
    for page in herbal_pages:
        words = pages[page]
        counts = Counter(words)
        
        hits = {}
        total_hits = 0
        for t in targets:
            c = counts.get(t, 0)
            if c > 0:
                hits[t] = c
                total_hits += c
        
        if total_hits > 0:
            # Check if it's a "label" (heuristic: short page, or isolated?)
            # Or just high frequency relative to page length?
            # For now, just list them.
            results.append({
                'page': page,
                'hits': hits,
                'total_words': len(words),
                'type': page_types.get(page, 'Unknown')
            })
            
    # Sort by hits
    results.sort(key=lambda x: sum(x['hits'].values()), reverse=True)
    
    print("\nTop candidates:")
    for r in results:
        print(f"{r['page']} ({r['type']}): {r['hits']}")
        
    # Save to simple JSON for next step
    with open('results/blue_candidates_temp.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
