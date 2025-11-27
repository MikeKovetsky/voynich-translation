import re
from collections import defaultdict

EVA_FILE = 'data/eva_ivtff.txt'
BLUE_PAGES = ['13r', '101v', '34v']
RED_PAGES = ['25v', '39v', '57v']

def check_pages():
    counts = defaultdict(lambda: defaultdict(int))
    
    with open(EVA_FILE, 'r') as f:
        for line in f:
            match = re.match(r'<f(\d+[rv]).*?>', line)
            if match:
                page_id = match.group(1)
                content = line.split('>', 1)[1]
                words = re.split(r'[.\s]+', content)
                for w in words:
                    w = w.strip()
                    if w in ['ol', 'or']:
                        counts[page_id][w] += 1

    print("Blue Pages:")
    for p in BLUE_PAGES:
        print(f"  {p}: ol={counts[p]['ol']}, or={counts[p]['or']}")
        
    print("\nRed Pages:")
    for p in RED_PAGES:
        print(f"  {p}: ol={counts[p]['ol']}, or={counts[p]['or']}")

check_pages()
