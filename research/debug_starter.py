import sys
from pathlib import Path
import re
sys.path.append(str(Path(__file__).parent))
import voynich_data

pages = voynich_data.get_eva_pages(transcriber='H')
start_counts = {}
total_counts = {}

for folio, lines in pages.items():
    for loc, text in lines.items():
        text_clean = re.sub(r'[!?<>@$\d]', '', text)
        words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 1]
        if not words: continue
        
        start_counts[words[0]] = start_counts.get(words[0], 0) + 1
        for w in words:
            total_counts[w] = total_counts.get(w, 0) + 1

print(f"{'Word':<10} | {'Total':<6} | {'Start':<6} | {'Prob':<6}")
print("-" * 35)
count = 0
for w, tot in total_counts.items():
    if tot > 50:
        st = start_counts.get(w, 0)
        prob = st/tot
        if prob > 0.30:
            print(f"{w:<10} | {tot:<6} | {st:<6} | {prob:.1%}")
            count += 1
print(f"\nFound {count} words with > 30% start probability and > 50 count.")
