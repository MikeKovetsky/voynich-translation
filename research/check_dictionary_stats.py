import json
from collections import Counter

def check_stats():
    try:
        with open('results/dictionary/dictionary_v9_4.json', 'r') as f:
            data = json.load(f)
            
        entries = data.get('entries', {})
        print(f"Total entries: {len(entries)}")
        
        domains = Counter()
        confidences = []
        unknown_meanings = 0
        
        for word, details in entries.items():
            domains[details.get('domain')] += 1
            confidences.append(details.get('confidence', 0))
            if not details.get('meaning') or details.get('meaning').lower() == 'unknown':
                unknown_meanings += 1
                
        print("\nDomains:")
        for d, c in domains.most_common():
            print(f"  {d}: {c}")
            
        print(f"\nMin confidence: {min(confidences)}")
        print(f"Max confidence: {max(confidences)}")
        print(f"Unknown meanings in dictionary: {unknown_meanings}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_stats()
