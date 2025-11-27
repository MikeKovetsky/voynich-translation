import json
from collections import Counter

with open('results/parsed_text.json', 'r') as f:
    data = json.load(f)

originals = [item['original'] for item in data]
unique_originals = set(originals)

print(f"Total items: {len(originals)}")
print(f"Unique originals: {len(unique_originals)}")
print(f"Most common: {Counter(originals).most_common(5)}")
