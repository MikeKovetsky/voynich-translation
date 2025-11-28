import csv
import os
import re
from research.voynich_data import get_folio_text

# 1. Load Sherwood Mapping
SHERWOOD_FILE = "data/external_corpora/sherwood_plant_mapping.csv"
OUTPUT_FILE = "results/loose_descriptors.csv"
FREQ_THRESHOLD = 0.2

# Define Descriptor Categories
# Based on the Sherwood Descriptions
DESCRIPTORS = {
    "poison": ["toxic", "poison", "death", "fatal", "kill", "warning"],
    "water": ["aquatic", "water", "pond", "lake", "float", "wet"],
    "food": ["edible", "eat", "food", "cook", "salad", "vegetable", "root"],
    "medicine": ["medical", "cure", "heal", "wound", "pain", "remedy"],
    "sticky": ["sticky", "glue", "catch", "trap", "insect"]
}

def main():
    if not os.path.exists(SHERWOOD_FILE):
        print(f"Error: {SHERWOOD_FILE} not found.")
        return

    # Load mapping
    folio_data = []
    with open(SHERWOOD_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 3:
                folio_data.append(row)

    # Classify Pages
    page_categories = {} # category -> list of folios
    
    # Hardcoded heuristics based on Latin Names or known properties
    print("Classifying Pages...")
    for folio, common, latin in folio_data:
        text_blob = (common + " " + latin).lower()
        
        # Heuristics
        if "water" in text_blob or "nymphaea" in text_blob:
            page_categories.setdefault("water", []).append(folio)
        if "nightshade" in text_blob or "poison" in text_blob or "hellebore" in text_blob:
            page_categories.setdefault("poison", []).append(folio)
        if "lettuce" in text_blob or "spinach" in text_blob or "sorrel" in text_blob:
            page_categories.setdefault("food", []).append(folio)
        if "drosera" in text_blob: # Sundew
            page_categories.setdefault("sticky", []).append(folio)

    # Pre-cache page words to avoid repetitive I/O
    print("Caching page words...")
    all_sherwood_folios = set()
    for cat, folios in page_categories.items():
        all_sherwood_folios.update(folios)
        
    page_words_map = {}
    for folio in all_sherwood_folios:
        # Clean folio name
        clean_folio = folio.lower().replace("left", "").replace("right", "").replace(" ", "")
        if not clean_folio.startswith('f'): clean_folio = 'f' + clean_folio
        
        text_map = get_folio_text(clean_folio)
        words = set()
        if text_map:
            for line in text_map.values():
                # Improved Tokenization
                # Remove markup chars like <, >, !, ?, $, digits
                text_clean = re.sub(r'[!?<>@$\d]', ' ', line)
                # Split on dots, hyphens, commas, spaces
                tokens = re.split(r'[.\-=,\s]+', text_clean)
                for w in tokens:
                    if len(w) > 1:
                        words.add(w)
        page_words_map[folio] = words

    # Scan Text for Shared Words with Specificity Boost
    print(f"Scanning Text (Threshold: {FREQ_THRESHOLD})...")
    
    hypotheses = []
    
    for cat, folios_in_cat in page_categories.items():
        folios_in_cat_set = set(folios_in_cat)
        folios_outside = all_sherwood_folios - folios_in_cat_set
        
        if len(folios_in_cat) < 2: continue 

        num_in_cat = len(folios_in_cat)
        num_outside = len(folios_outside)
        if num_outside == 0: num_outside = 1 

        # Count words in this category
        cat_word_counts = {}
        for folio in folios_in_cat:
            for w in page_words_map.get(folio, set()):
                cat_word_counts[w] = cat_word_counts.get(w, 0) + 1
                
        # Count words outside
        outside_word_counts = {}
        for folio in folios_outside:
             for w in page_words_map.get(folio, set()):
                outside_word_counts[w] = outside_word_counts.get(w, 0) + 1

        for word, count in cat_word_counts.items():
            freq_in_cat = count / num_in_cat
            
            if freq_in_cat >= FREQ_THRESHOLD:
                count_outside = outside_word_counts.get(word, 0)
                freq_outside = count_outside / num_outside
                
                # Specificity Score calculation
                specificity_score = freq_in_cat / (freq_outside + 0.001)
                
                # Only keep if specificity is decent
                if specificity_score > 1.5:
                    hypotheses.append({
                        'category': cat,
                        'voynich_word': word,
                        'freq_in_cat': f"{freq_in_cat:.2f}",
                        'freq_outside': f"{freq_outside:.2f}",
                        'specificity': f"{specificity_score:.2f}"
                    })

    # Sort by Specificity (descending)
    hypotheses.sort(key=lambda x: float(x['specificity']), reverse=True)

    # Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['category', 'voynich_word', 'freq_in_cat', 'freq_outside', 'specificity']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(hypotheses)
        
    print(f"Generated {len(hypotheses)} descriptor hypotheses in {OUTPUT_FILE}.")
    
    # Simple console heatmap/list of top shared words per category
    print("\nTop Shared Words per Category:")
    categories = sorted(list(page_categories.keys()))
    for cat in categories:
        print(f"\nCategory: {cat.upper()} (n={len(page_categories[cat])})")
        top_words = [h for h in hypotheses if h['category'] == cat][:10]
        if not top_words:
            print("  No strong candidates found.")
        for item in top_words:
            print(f"  {item['voynich_word']}: In Cat {float(item['freq_in_cat'])*100:.0f}%, Outside {float(item['freq_outside'])*100:.0f}%, Score {item['specificity']}")

if __name__ == "__main__":
    main()
