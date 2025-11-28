import csv
import os
from collections import Counter, defaultdict
from research.voynich_data import get_all_words, get_folio_text

INPUT_SCOPE = "results/scope_analysis.csv"
OUTPUT_FILE = "results/semantic_clusters.csv"

def main():
    if not os.path.exists(INPUT_SCOPE):
        print(f"Error: {INPUT_SCOPE} not found.")
        return

    # 1. Identify Targets (Local Variables)
    targets = set()
    with open(INPUT_SCOPE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Local Variable' in row['classification'] or 'Mixed' in row['classification']:
                targets.add(row['word'])
                
    print(f"Analyzing context for {len(targets)} target words...")
    
    # 2. Scan Context
    # We need the full text stream.
    # Let's use get_folio_text to iterate through pages.
    # Building neighbor profiles: word -> {left: {w:count}, right: {w:count}}
    
    neighbor_profiles = defaultdict(lambda: {'left': Counter(), 'right': Counter()})
    
    # Iterate all folios (slow but accurate)
    # For speed, let's limit to a sample if needed, but full scan is better.
    # We can iterate by section using get_section_text? No, just get all pages.
    # Actually, we can just iterate over the 129 Sherwood pages + some others?
    # Let's use get_folio_text for ALL pages.
    
    # Optimization: Load all text into memory first?
    # Text size is manageable.
    
    all_folios = [] # List of folio IDs
    # How to get list of all folios? voynich_data doesn't expose it directly but get_eva_pages does.
    from research.voynich_data import get_eva_pages
    pages = get_eva_pages()
    
    for folio, lines in pages.items():
        full_text = " ".join(lines.values())
        words = full_text.split()
        
        for i, word in enumerate(words):
            if word in targets:
                # Left Neighbor
                if i > 0:
                    left = words[i-1]
                    neighbor_profiles[word]['left'][left] += 1
                
                # Right Neighbor
                if i < len(words) - 1:
                    right = words[i+1]
                    neighbor_profiles[word]['right'][right] += 1

    # 3. Cluster by Neighbors
    # Simplify: Group words that share the same Top Left Neighbor
    # or Top Right Neighbor.
    
    clusters = defaultdict(list)
    
    for word, profile in neighbor_profiles.items():
        if not profile['left'] and not profile['right']: continue
        
        # Primary Feature: Most common Left Neighbor (Preceding Adjective?)
        if profile['left']:
            top_left = profile['left'].most_common(1)[0][0]
            clusters[f"Preceded by {top_left}"].append(word)
            
        # Secondary Feature: Most common Right Neighbor
        if profile['right']:
            top_right = profile['right'].most_common(1)[0][0]
            clusters[f"Followed by {top_right}"].append(word)

    # Output Top Clusters
    cluster_data = []
    for desc, members in clusters.items():
        if len(members) > 5: # Only significant clusters
            # Sort members by frequency? We don't have frequency here easily.
            # Just list top 10
            sample = ", ".join(members[:10])
            cluster_data.append([desc, len(members), sample])
            
    cluster_data.sort(key=lambda x: x[1], reverse=True)

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['cluster_description', 'size', 'sample_members'])
        writer.writerows(cluster_data)
        
    print(f"Generated {len(cluster_data)} semantic clusters.")

if __name__ == "__main__":
    main()
