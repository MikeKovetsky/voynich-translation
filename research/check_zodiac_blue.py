import re
import json
from collections import Counter

def parse_eva_file(filepath):
    pages = {}
    current_page = None
    
    with open(filepath, 'r') as f:
        for line in f:
            page_match = re.match(r'#\s*<f(\d+[rv])\S*>', line)
            if page_match:
                current_page = 'f' + page_match.group(1)
                pages[current_page] = []
                continue
            
            if line.startswith('#') or not current_page:
                continue
                
            parts = line.strip().split()
            for part in parts:
                if '<' in part and '>' in part:
                    continue
                words = part.split('.')
                for w in words:
                    clean_w = w.strip()
                    clean_w = re.sub(r'[^a-z0-9]', '', clean_w)
                    if clean_w:
                        pages[current_page].append(clean_w)
                        
    return pages

def main():
    eva_path = 'data/eva_ivtff.txt'
    pages = parse_eva_file(eva_path)
    
    # Zodiac pages (approximate range, check specific pages for Taurus/Libra)
    # Taurus: f71r, f71v
    # Libra: f72v, f73r
    zodiac_targets = ['f71r', 'f71v', 'f72v', 'f73r']
    words_of_interest = ['os', 'oteos']
    
    print("Zodiac Analysis:")
    for page in zodiac_targets:
        if page in pages:
            content = pages[page]
            counts = Counter(content)
            print(f"Page {page}:")
            for w in words_of_interest:
                print(f"  {w}: {counts.get(w, 0)}")
        else:
            print(f"Page {page} not found.")

if __name__ == "__main__":
    main()
