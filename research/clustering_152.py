import json
import re
import os
from gensim.models import Word2Vec
import logging

# Configure logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

DICTIONARY_PATH = 'results/master_dictionary_v8_0.json'
TRANSCRIPTION_PATH = 'data/eva_ivtff.txt'
OUTPUT_CLUSTERS = 'results/semantic_clusters.json'
OUTPUT_SYNONYMS = 'results/synonym_candidates.md'

def load_dictionary():
    with open(DICTIONARY_PATH, 'r') as f:
        data = json.load(f)
    return data['entries']

def load_corpus():
    sentences = []
    with open(TRANSCRIPTION_PATH, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            # Use 'm' version
            if ';m>' in line:
                parts = line.split('\t')
                if len(parts) > 1:
                    text = parts[1].strip()
                    # Split by dot
                    words = [w.strip() for w in text.split('.') if w.strip()]
                    
                    clean_words = []
                    for w in words:
                        # Remove punctuation like !, ?, etc.
                        # EVA basic chars: a-z, 0-9.
                        w_clean = re.sub(r'[^a-z0-9]', '', w)
                        if w_clean:
                            clean_words.append(w_clean)
                    
                    if clean_words:
                        sentences.append(clean_words)
    return sentences

def train_model(sentences):
    # Window size: 3, Vector size: 50 as per requirements
    # Using Skip-gram (sg=1) and more epochs for small dataset
    model = Word2Vec(sentences, vector_size=50, window=3, min_count=1, workers=4, sg=1, epochs=50)
    return model

def find_synonyms(model, dictionary_entries):
    clusters = {} # key: meaning/domain, value: list of words
    
    # Initialize clusters with known words
    for word, info in dictionary_entries.items():
        meaning = info.get('meaning', 'unknown')
        if meaning not in clusters:
            clusters[meaning] = []
        if word not in clusters[meaning]:
            clusters[meaning].append(word)

    known_words = set(dictionary_entries.keys())
    
    lines_for_report = ["# Synonym Candidates\n"]
    
    # Sort keys for consistent output
    sorted_keys = sorted(dictionary_entries.keys())
    
    for word in sorted_keys:
        info = dictionary_entries[word]
        if word in model.wv:
            try:
                neighbors = model.wv.most_similar(word, topn=5)
                candidates = []
                for neighbor, score in neighbors:
                    if neighbor not in known_words:
                        candidates.append(f"{neighbor} ({score:.2f})")
                        
                        # Add to cluster if score is high enough
                        if score > 0.7:
                            meaning = info.get('meaning', 'unknown')
                            if meaning not in clusters:
                                clusters[meaning] = []
                            if neighbor not in clusters[meaning]:
                                clusters[meaning].append(neighbor)
                                
                if candidates:
                    lines_for_report.append(f"## {word} ({info.get('meaning', 'unknown')})")
                    lines_for_report.append(f"- Candidates: {', '.join(candidates)}")
                    lines_for_report.append("")
            except KeyError:
                continue
                
    with open(OUTPUT_SYNONYMS, 'w') as f:
        f.write('\n'.join(lines_for_report))
        
    with open(OUTPUT_CLUSTERS, 'w') as f:
        json.dump(clusters, f, indent=2)

def main():
    print("Loading dictionary...")
    entries = load_dictionary()
    
    print("Loading corpus...")
    sentences = load_corpus()
    print(f"Loaded {len(sentences)} sentences.")
    
    print("Training Word2Vec...")
    model = train_model(sentences)
    
    print("Finding synonyms and clustering...")
    find_synonyms(model, entries)
    print("Done.")

if __name__ == "__main__":
    main()

