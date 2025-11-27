import logging
import os
import re
import json
from gensim.models import Word2Vec
import multiprocessing

# Configure logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def load_sentences(path):
    with open(path, 'r') as f:
        text = f.read()
        
    sentences = []
    # Treat each line as a sentence/paragraph
    for line in text.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        clean_line = re.sub(r'<[^>]+>', '', line)
        clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
        tokens = clean_line.split()
        if tokens:
            sentences.append(tokens)
    return sentences

def main():
    print("Starting Contextual Clustering (Word2Vec)...")
    input_path = 'data/eva_ivtff.txt'
    
    if not os.path.exists(input_path):
        print("Data file not found.")
        return

    sentences = load_sentences(input_path)
    print(f"Loaded {len(sentences)} sentences/lines.")
    
    # Train Word2Vec
    model = Word2Vec(sentences, vector_size=50, window=3, min_count=5, workers=multiprocessing.cpu_count())
    
    print("Model trained.")
    
    # Find synonyms for known keys
    targets = ['chol', 'daiin', 'aiin', 'okeol', 'chedy']
    results = {}
    
    for target in targets:
        if target in model.wv:
            print(f"\nNeighbors for '{target}':")
            neighbors = model.wv.most_similar(target, topn=10)
            results[target] = neighbors
            for n, sim in neighbors:
                print(f"- {n}: {sim:.4f}")
        else:
            print(f"\nTarget '{target}' not in vocabulary (min_count=5).")

    # Save clusters
    # Simple clustering: For every word in vocab, find top 1 neighbor
    vocab = list(model.wv.index_to_key)
    clusters = {}
    for word in vocab:
        try:
            n = model.wv.most_similar(word, topn=1)[0][0]
            clusters[word] = n
        except:
            pass
            
    with open('results/semantic_clusters.json', 'w') as f:
        json.dump(clusters, f, indent=2)

if __name__ == "__main__":
    main()
