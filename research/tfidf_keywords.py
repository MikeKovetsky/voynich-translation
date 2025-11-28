
import csv
import re
import os
from collections import defaultdict, Counter
import math

# Output file path
OUTPUT_FILE = "results/unique_page_keywords.csv"
SHERWOOD_MAPPING_FILE = "data/external_corpora/sherwood_plant_mapping.csv"
TRANSCRIPTION_FILE = "data/eva_ivtff.txt"

def load_sherwood_mapping(filepath):
    """
    Loads the Sherwood folio to plant name mapping.
    Returns a dictionary: {folio: plant_name}
    """
    mapping = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            folio = row['Folio'].strip()
            # Normalize folio: sometimes 2r, sometimes f2r. The mapping file has "2r".
            # The transcription has "<f2r."
            # We'll store as simple "f" + folio (e.g. "f2r") to match typical usage, 
            # or handle normalization later.
            if not folio.startswith('f'):
                folio = 'f' + folio
            
            plant_name = row['Common Name'].strip()
            if not plant_name:
                plant_name = row['Latin Name'].strip()
            
            mapping[folio] = plant_name
    return mapping

def load_transcription(filepath):
    """
    Parses the EVA transcription file.
    Returns:
        page_corpus: {page_id: [list of words]}
        all_words_counts: Counter of all words in the manuscript (for IDF if needed manually, though we use sklearn)
    """
    page_corpus = defaultdict(list)
    current_page = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # Detect Page ID: <f100r.P.1;F> or similar
            match = re.match(r"<(f\d+[rv]\d?)\.", line)
            if match:
                current_page = match.group(1)
            
            if line.startswith("#"): continue
            if not current_page: continue
            
            # Clean line
            cleaned = line.strip()
            
            # Remove the page tag at start if it wasn't caught by regex (regex just extracted, didn't remove)
            # Use regex to remove ALL tags <...> including <plant>, <->, etc.
            # Replace with space to avoid merging words that are separated by tags.
            cleaned = re.sub(r"<[^>]+>", " ", cleaned)
            
            # Replace dots with spaces (often used as separators)
            cleaned = cleaned.replace(".", " ")
            
            # Remove "!" and "*" and "," and other punctuation
            for char in "!*,;=%$":
                cleaned = cleaned.replace(char, "")
                
            words = cleaned.split()
            
            valid_words = []
            for w in words:
                if w == "-" or w == "=": continue
                # Basic validation: at least one char
                if not w: continue
                # Skip if it's just non-alphanumeric noise (though EVA has some special chars, mostly ascii)
                valid_words.append(w)
                
            page_corpus[current_page].extend(valid_words)
            
    return page_corpus

def calculate_tfidf(page_corpus):
    """
    Calculates TF-IDF for all words in all pages.
    """
    # We can use sklearn's TfidfVectorizer
    # But we need to map back to pages.
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import pandas as pd
    except ImportError:
        print("sklearn or pandas not found. Please install them.")
        return None, None, None

    page_ids = list(page_corpus.keys())
    # Join words back to string for vectorizer
    docs = [" ".join(page_corpus[pid]) for pid in page_ids]
    
    # Initialize Vectorizer
    # min_df=1 means word must appear in at least 1 doc (default)
    # use_idf=True (default)
    # Token pattern to accept words (EVA is ascii based mostly)
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\S+") 

    tfidf_matrix = vectorizer.fit_transform(docs)
    feature_names = vectorizer.get_feature_names_out()
    
    return page_ids, tfidf_matrix, feature_names

def main():
    print("Loading Sherwood mapping...")
    sherwood_mapping = load_sherwood_mapping(SHERWOOD_MAPPING_FILE)
    print(f"Loaded {len(sherwood_mapping)} Sherwood folios.")
    
    print("Loading transcription...")
    page_corpus = load_transcription(TRANSCRIPTION_FILE)
    print(f"Loaded {len(page_corpus)} pages from transcription.")
    
    # Calculate TF-IDF
    print("Calculating TF-IDF...")
    page_ids, tfidf_matrix, feature_names = calculate_tfidf(page_corpus)
    
    if page_ids is None:
        return

    # Create a helper to look up word indices
    word_to_idx = {w: i for i, w in enumerate(feature_names)}
    
    # Helper for Validation: Plant map for all pages (just Sherwood ones)
    # And we need to check if a word appears in other plants
    
    # Pre-calculate word-to-plant presence
    # dict: word -> set of plant_names
    word_plant_occurences = defaultdict(set)
    
    # Also need word counts per page for the "> 3 times" rule
    # We can compute this from page_corpus directly or from CountVectorizer
    # Let's just use page_corpus for count checks to be safe and simple
    page_word_counts = {pid: Counter(words) for pid, words in page_corpus.items()}
    
    for pid, words in page_corpus.items():
        if pid in sherwood_mapping:
            plant = sherwood_mapping[pid]
            unique_words = set(words)
            for w in unique_words:
                word_plant_occurences[w].add(plant)

    results = []

    # Process each Sherwood page
    for idx, pid in enumerate(page_ids):
        if pid not in sherwood_mapping:
            continue
            
        current_plant = sherwood_mapping[pid]
        
        # Get row from sparse matrix
        row = tfidf_matrix[idx]
        # Convert to dense to sort (row is small enough, it's vocabulary size)
        # Better: use .tocoo() to get non-zero elements
        coo = row.tocoo()
        
        # List of (word_idx, score)
        word_scores = list(zip(coo.col, coo.data))
        
        # Sort by score desc
        word_scores.sort(key=lambda x: x[1], reverse=True)
        
        top_keywords = []
        
        # Iterate through candidates to find top 3 valid ones
        for word_idx, score in word_scores:
            word = feature_names[word_idx]
            
            # Rule: Appears > 3 times on the page
            count_on_page = page_word_counts[pid][word]
            if count_on_page <= 3:
                continue
            
            # Rule: Unique to that page or shared only with other pages of SAME plant
            # Check word_plant_occurences[word]
            # It should only contain current_plant
            plants_with_word = word_plant_occurences.get(word, set())
            
            # Check if there are any OTHER plants
            other_plants = plants_with_word - {current_plant}
            
            if len(other_plants) > 0:
                # Found in other plants -> not unique
                continue
                
            # If we pass filters, add to list
            top_keywords.append((word, score))
            
            if len(top_keywords) >= 3:
                break
        
        # Prepare row
        # Folio, Plant Name, Top Keyword 1 (Score), Top Keyword 2 (Score), Top Keyword 3 (Score)
        row_data = {
            "Folio": pid,
            "Plant Name": current_plant
        }
        
        for i in range(3):
            if i < len(top_keywords):
                w, s = top_keywords[i]
                row_data[f"Top Keyword {i+1}"] = f"{w} ({s:.4f})"
            else:
                row_data[f"Top Keyword {i+1}"] = ""
                
        results.append(row_data)

    # Sort results by Folio for niceness
    results.sort(key=lambda x: x["Folio"])
    
    # Write CSV
    print(f"Writing results to {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    fieldnames = ["Folio", "Plant Name", "Top Keyword 1", "Top Keyword 2", "Top Keyword 3"]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
        
    print("Done.")

if __name__ == "__main__":
    main()
