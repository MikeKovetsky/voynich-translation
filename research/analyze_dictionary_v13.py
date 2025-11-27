import json
from collections import Counter
import os

def analyze_dictionary():
    dict_path = 'results/dictionary/dictionary_v13.json'
    if not os.path.exists(dict_path):
        print(f"Error: {dict_path} not found.")
        return

    with open(dict_path, 'r') as f:
        data = json.load(f)

    entries = data.get('entries', {})
    total_entries = len(entries)
    
    domains = Counter()
    confidences = Counter()
    languages = Counter()
    
    for word, details in entries.items():
        domains[details.get('domain', 'unknown')] += 1
        confidences[details.get('confidence_level', 'unknown')] += 1
        languages[details.get('language', 'unknown')] += 1

    print(f"Total Entries: {total_entries}")
    print("\nDomain Distribution:")
    for d, c in domains.most_common():
        print(f"  {d}: {c}")
        
    print("\nConfidence Levels:")
    for c, count in confidences.most_common():
        print(f"  {c}: {count}")

    print("\nLanguage/Type Distribution:")
    for l, c in languages.most_common():
        print(f"  {l}: {c}")

if __name__ == "__main__":
    analyze_dictionary()
