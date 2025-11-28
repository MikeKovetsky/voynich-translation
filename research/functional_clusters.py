import csv
import os
from collections import Counter
from research.voynich_data import get_folio_text

# 1. Load Sherwood Mapping
SHERWOOD_FILE = "data/external_corpora/sherwood_plant_mapping.csv"
OUTPUT_FILE = "results/functional_cluster_words.csv"

# Functional Groups (Hardcoded for now based on common medieval usage)
CLUSTERS = {
    "Stomach": ["f25r", "f31v", "f29r", "f41v", "f52r", "f37v"], # Balm, Fennel, Lettuce, Coriander, Lovage, Mint
    "Skin_Wound": ["f28r", "f87r", "f30r", "f47r", "f6r"], # Plantago, Aloe, Comfrey, Houseleek, Acanthus
    "Sleep_Head": ["f38r", "f44r", "f19r", "f1v"], # Poppy, Mandrake, Valerian, Nightshade
    "Eye": ["f32r", "f55r", "f48v"], # Speedwell, Fumitory, Celandine
    "Respiratory": ["f47v", "f53v"], # Lungwort, Hawkweed
    "Women": ["f57r", "f29v"] # Ladys Mantle, Nigella
}

def main():
    if not os.path.exists(SHERWOOD_FILE):
        print(f"Error: {SHERWOOD_FILE} not found.")
        return

    cluster_data = []
    
    print("Analyzing Functional Clusters...")
    for cluster_name, folios in CLUSTERS.items():
        # Collect all words from these folios
        word_counts = Counter()
        folio_count = len(folios)
        
        for folio in folios:
            text_map = get_folio_text(folio)
            if not text_map: continue
            
            unique_words_on_page = set()
            for line in text_map.values():
                for w in line.split():
                    w = w.replace('.', '').replace(',', '')
                    if len(w) > 2:
                        unique_words_on_page.add(w)
            
            word_counts.update(unique_words_on_page)
            
        # Find Intersection words (present in > 60% of pages)
        threshold = folio_count * 0.6
        
        for word, count in word_counts.items():
            if count >= threshold:
                # Check Specificity (is it just 'daiin'?)
                # In a real run, we'd check global freq. Here we assume short words are generic.
                if len(word) > 3: 
                    cluster_data.append([cluster_name, word, f"{count}/{folio_count}", "High"])

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['cluster', 'word', 'frequency', 'specificity'])
        writer.writerows(cluster_data)
        
    print(f"Found {len(cluster_data)} cluster words.")

if __name__ == "__main__":
    main()
