import csv
import os
import math
import json
from collections import Counter
from research.voynich_data import get_section_text, FOLIO_SECTIONS

OUTPUT_FILE = "results/scope_analysis.csv"
DICTIONARY_FILE = "results/dictionary/master_dictionary_v20.json"

def calculate_entropy(distribution):
    """Calculate Shannon entropy for a probability distribution."""
    total = sum(distribution.values())
    if total == 0: return 0
    entropy = 0
    for count in distribution.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def main():
    # 1. Load Text by Scope
    print("Loading text by scope...")
    scopes = {
        "Herbal": get_section_text("herbal_a"), # Combine A and B for now? Or keep separate? 
                                                # Let's separate to see if A/B distinction holds
        "Herbal_A": get_section_text("herbal_a"),
        "Herbal_B": get_section_text("herbal_b"),
        "Astro": get_section_text("astronomical"),
        "Bio": get_section_text("biological"),
        "Pharma": get_section_text("pharmaceutical"),
        "Recipes": get_section_text("recipes")
    }
    
    # 2. Count words per scope
    print("Counting words...")
    word_scope_counts = {} # word -> {scope: count}
    scope_totals = {s: 0 for s in scopes}
    
    for scope_name, pages in scopes.items():
        for folio_text in pages.values():
            for line in folio_text.values():
                # Simple split, rely on previous cleaning or do basic here
                words = line.replace('.', ' ').split()
                for w in words:
                    if len(w) < 2: continue # Skip artifacts
                    if w not in word_scope_counts:
                        word_scope_counts[w] = Counter()
                    word_scope_counts[w][scope_name] += 1
                    scope_totals[scope_name] += 1

    # 3. Load Dictionary for comparison
    existing_domains = {}
    if os.path.exists(DICTIONARY_FILE):
        with open(DICTIONARY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for k, v in data.get('entries', {}).items():
                existing_domains[k] = v.get('domain', 'unknown')

    # 4. Calculate Metrics
    print("Calculating scope metrics...")
    results = []
    
    num_scopes = len(scopes)
    max_entropy = math.log2(num_scopes)
    
    for word, counts in word_scope_counts.items():
        total_count = sum(counts.values())
        if total_count < 5: continue # Skip rare words
        
        # Normalize counts by scope size (frequency per 1000 words)
        # This prevents larger scopes from dominating
        normalized_dist = {}
        for s, c in counts.items():
            normalized_dist[s] = (c / scope_totals[s]) * 1000
            
        entropy = calculate_entropy(normalized_dist)
        
        # Determine Dominant Scope
        dominant_scope = max(normalized_dist, key=normalized_dist.get)
        dominance_score = normalized_dist[dominant_scope] / sum(normalized_dist.values())
        
        # Classification
        if entropy > 2.0: # High entropy = Global
            classification = "Global Keyword"
        elif dominance_score > 0.8:
            classification = f"Local Variable ({dominant_scope})"
        else:
            classification = "Mixed"
            
        results.append({
            "word": word,
            "total_count": total_count,
            "entropy": f"{entropy:.2f}",
            "max_possible_entropy": f"{max_entropy:.2f}",
            "dominant_scope": dominant_scope,
            "classification": classification,
            "existing_domain": existing_domains.get(word, "unknown")
        })

    # Sort by count descending
    results.sort(key=lambda x: x['total_count'], reverse=True)

    # Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Analyzed {len(results)} words. See {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
