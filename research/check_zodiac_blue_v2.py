import re
from collections import Counter

def parse_eva_file(filepath):
    pages = {}
    current_page = None
    
    with open(filepath, 'r') as f:
        for line in f:
            # Try to detect page change from various formats
            # <f71r>
            # # <f71r.R1>
            # <f71r.1...>
            
            # Simple regex for page code
            match = re.search(r'<f(\d+[rv]\d?)[^>]*>', line)
            if match:
                # Update current page if it's a new page code
                # But we only want the base page e.g., f71r from f71r.R1
                base_page = 'f' + match.group(1)
                # Clean up (remove .R1 etc if included in group 1, though \d+[rv]\d? should catch f71r or f72v1)
                # Actually, f72r1 is a valid page identifier in some contexts, but EVA might treat it as f72r section 1.
                # Let's stick to the identifier found.
                
                # If the page ID changes, update current_page
                if base_page != current_page:
                    current_page = base_page
                    if current_page not in pages:
                        pages[current_page] = []
            
            if not current_page:
                continue
                
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Extract text content
            parts = line.strip().split()
            for part in parts:
                if '<' in part and '>' in part: # Skip codes
                    continue
                
                # Split words by dot
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
    
    # Taurus: f71v, f72r (or f72r1)
    # Libra: f73v
    # Also checking f72v (Cancer) just in case
    target_pages = ['f71v', 'f72r', 'f72r1', 'f73v', 'f72v']
    words = ['os', 'oteos']
    
    print("Zodiac Analysis:")
    for p in target_pages:
        # Check if the page exists or is a substring of existing keys
        # (e.g. f72r1 might be stored as f72r or f72r1)
        found_key = None
        if p in pages:
            found_key = p
        else:
            # Try fuzzy match
            for k in pages.keys():
                if k.startswith(p):
                    found_key = k
                    break
        
        if found_key:
            content = pages[found_key]
            counts = Counter(content)
            print(f"Page {found_key}:")
            for w in words:
                print(f"  {w}: {counts.get(w, 0)}")
        else:
            print(f"Page {p} not found.")

if __name__ == "__main__":
    main()
