import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import voynich_data

# Configuration
MASTER_DICT_PATH = Path("results/master_dictionary_v7_4.json")
OUTPUT_JSON_PATH = Path("results/word_clusters.json")
OUTPUT_REPORT_PATH = Path("results/clustering_report.md")
MIN_FREQUENCY = 3  # Minimum frequency for an unknown word to be analyzed

def load_master_dict():
    if not MASTER_DICT_PATH.exists():
        # Fallback to v7_3 if 7.4 doesn't exist (though we checked it exists)
        fallback = Path("results/master_dictionary_v7_3.json")
        if fallback.exists():
            print(f"Warning: {MASTER_DICT_PATH} not found. Using {fallback}")
            with open(fallback, 'r', encoding='utf-8') as f:
                return json.load(f)
        raise FileNotFoundError(f"Master dictionary not found at {MASTER_DICT_PATH}")
        
    with open(MASTER_DICT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_category(entry):
    """
    Extract a high-level category from a dictionary entry.
    Prioritize explicit domain/meaning.
    """
    meaning = entry.get("meaning", "").lower()
    domain = entry.get("domain", "").lower()
    
    # Heuristics for categories based on meaning/domain
    if "plant" in meaning or "botanical" in domain:
        if "part" in meaning or "leaf" in meaning or "root" in meaning:
            return "Plant Part"
        return "Plant Name"
    
    if "star" in meaning or "constellation" in meaning or "astronomical" in domain:
        return "Star Name"
        
    if "recipe" in domain or "process" in meaning or "verb" in meaning:
        if "verb" in meaning:
            return "Process Verb"
        return "Ingredient" # Default for recipe items
        
    if "month" in meaning or "zodiac" in meaning:
        return "Time/Zodiac"
    
    if "color" in meaning:
        return "Color"
        
    if "measure" in meaning or "number" in meaning:
        return "Measurement"
        
    if domain:
        return domain.capitalize()
        
    return "Unknown"

def extract_corpus_words():
    """
    Load the full corpus using voynich_data and flatten to a list of words.
    """
    print("Loading corpus...")
    pages = voynich_data.get_eva_pages(transcriber='H')
    
    all_words = []
    # Sort pages to maintain some order (though context is local)
    # Helper to sort folios: f1r, f1v, f2r...
    def folio_sort_key(folio):
        num = int(''.join(filter(str.isdigit, folio)))
        side = folio[-1]
        return (num, side)
        
    sorted_folios = sorted(pages.keys(), key=folio_sort_key)
    
    for folio in sorted_folios:
        lines = pages[folio]
        # Sort lines
        sorted_locs = sorted(lines.keys())
        for loc in sorted_locs:
            text = lines[loc]
            # Clean text: remove comments, identifiers if any remained (voynich_data usually cleans them)
            # voynich_data.get_eva_pages returns the text part.
            # We need to split by dots/spaces and remove punctuation.
            # Standard EVA words are separated by dots or spaces.
            words = text.replace('.', ' ').split()
            for w in words:
                # Remove punctuation like !, ?, *
                w_clean = ''.join(c for c in w if c.isalpha() or c.isdigit()) # Keep simple EVA chars
                if w_clean:
                    all_words.append(w_clean)
                    
    print(f"Corpus loaded: {len(all_words)} words.")
    return all_words

def vectorize_contexts(words):
    """
    Build feature vectors for each unique word based on its contexts.
    Features: (position, neighbor_word)
    """
    print("Vectorizing contexts...")
    # We need to collect features for each word type
    word_features = defaultdict(Counter)
    word_counts = Counter(words)
    
    for i, w in enumerate(words):
        # Context window: [-2, -1, +1, +2]
        # Left 1
        if i > 0:
            word_features[w][f"L1_{words[i-1]}"] += 1
        # Left 2
        if i > 1:
            word_features[w][f"L2_{words[i-2]}"] += 1
        # Right 1
        if i < len(words) - 1:
            word_features[w][f"R1_{words[i+1]}"] += 1
        # Right 2
        if i < len(words) - 2:
            word_features[w][f"R2_{words[i+2]}"] += 1
            
    return word_features, word_counts

def compute_cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two Counter objects (sparse vectors).
    """
    intersection = set(vec1.keys()) & set(vec2.keys())
    if not intersection:
        return 0.0
        
    numerator = sum(vec1[k] * vec2[k] for k in intersection)
    
    sum1 = sum(v**2 for v in vec1.values())
    sum2 = sum(v**2 for v in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    if denominator == 0:
        return 0.0
        
    return numerator / denominator

def analyze_clusters():
    # 1. Load Dictionary
    master_dict = load_master_dict()
    known_words = set(master_dict['entries'].keys())
    print(f"Master Dictionary: {len(known_words)} known words.")
    
    # Map known words to their categories for quick lookup
    word_to_category = {w: get_category(data) for w, data in master_dict['entries'].items()}
    
    # 2. Process Corpus
    corpus = extract_corpus_words()
    word_features, word_counts = vectorize_contexts(corpus)
    
    # 3. Identify Target Unknowns
    # Filter unknowns that appear at least MIN_FREQUENCY times
    unknown_targets = [w for w in word_counts if w not in known_words and word_counts[w] >= MIN_FREQUENCY]
    print(f"Analyzing {len(unknown_targets)} unknown words (freq >= {MIN_FREQUENCY}).")
    
    # Pre-calculate norms for known words to speed up similarity? 
    # Actually, compute_cosine_similarity calculates norms on the fly. 
    # Since we have many unknowns and many knowns, this is O(N*M).
    # Optimization: Only compare against known words that share at least one feature?
    # Inverted index: Feature -> List of Words
    
    print("Building inverted index for known words...")
    feature_to_known_words = defaultdict(list)
    known_words_list = [w for w in known_words if w in word_features]
    
    for w in known_words_list:
        for feat in word_features[w]:
            feature_to_known_words[feat].append(w)
            
    results = {}
    
    print("Clustering unknowns...")
    for i, unknown in enumerate(unknown_targets):
        if i % 100 == 0:
            print(f"Processed {i}/{len(unknown_targets)}...")
            
        u_vec = word_features[unknown]
        if not u_vec:
            continue
            
        # Find candidate known words (those sharing features)
        candidates = set()
        for feat in u_vec:
            candidates.update(feature_to_known_words[feat])
            
        if not candidates:
            continue
            
        # Calculate similarity for candidates
        scores = []
        for candidate in candidates:
            sim = compute_cosine_similarity(u_vec, word_features[candidate])
            if sim > 0.1: # Threshold to keep relevant matches
                scores.append((candidate, sim))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_matches = scores[:5]
        
        if not top_matches:
            continue
            
        # Vote for category
        votes = Counter()
        weighted_votes = defaultdict(float)
        
        match_details = []
        for match_word, score in top_matches:
            cat = word_to_category.get(match_word, "Unknown")
            votes[cat] += 1
            weighted_votes[cat] += score
            match_details.append({
                "word": match_word,
                "similarity": round(score, 3),
                "category": cat
            })
            
        # Fix: weighted_votes is defaultdict
        sorted_votes = sorted(weighted_votes.items(), key=lambda x: x[1], reverse=True)
        best_cat = sorted_votes[0][0]
        
        confidence = weighted_votes[best_cat] / sum(weighted_votes.values()) if sum(weighted_votes.values()) > 0 else 0
        
        results[unknown] = {
            "predicted_category": best_cat,
            "confidence": round(confidence, 2),
            "frequency": word_counts[unknown],
            "top_matches": match_details
        }
        
    # Sort results by frequency (importance)
    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]['frequency'], reverse=True))
    
    # Write JSON output
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_results, f, indent=2)
        
    print(f"Saved clusters to {OUTPUT_JSON_PATH}")
    
    # Write Report
    generate_report(sorted_results)

def generate_report(results):
    lines = []
    lines.append("# Clustering Analysis Report")
    lines.append(f"Total Unknowns Analyzed: {len(results)}")
    lines.append("")
    
    # Group by predicted category
    by_category = defaultdict(list)
    for word, data in results.items():
        by_category[data['predicted_category']].append((word, data))
        
    lines.append("## Category Distribution")
    for cat, items in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True):
        lines.append(f"- **{cat}**: {len(items)} words")
        
    lines.append("")
    lines.append("## Top Discoveries (High Confidence)")
    
    # Filter for high confidence
    high_conf = [
        (w, d) for w, d in results.items() 
        if d['confidence'] > 0.6 and d['frequency'] >= 5
    ]
    high_conf.sort(key=lambda x: x[1]['frequency'], reverse=True)
    
    for w, data in high_conf[:50]:
        lines.append(f"### `{w}` (Freq: {data['frequency']})")
        lines.append(f"- **Predicted**: {data['predicted_category']} (Conf: {data['confidence']})")
        lines.append("- **Similar to**:")
        for m in data['top_matches']:
            lines.append(f"  - `{m['word']}` ({m['category']}): {m['similarity']}")
        lines.append("")

    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
        
    print(f"Saved report to {OUTPUT_REPORT_PATH}")

if __name__ == "__main__":
    analyze_clusters()
