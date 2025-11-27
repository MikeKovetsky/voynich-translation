import json
import os
import math
from collections import Counter, defaultdict

# Configuration
INPUT_FILE = 'results/parsed_text.json'
OUTPUT_CLUSTERS_JSON = 'results/noun_clusters.json'
OUTPUT_REPORT_MD = 'results/noun_clusters_report.md'
OUTPUT_SUMMARY_MD = 'results/track-168-results_summary.md'

# Stop words (roots that are too common/grammatical to be semantic cluster centers)
# Based on previous analysis: dy (particle), ol (article), o (noun marker itself)
STOP_ROOTS = {'dy', 'ol', 'o', 'y', 's', 'd', 'q', 'k', 't', 'p', 'f', 'm', 'n', 'r', 'l'} 
# Also exclude very short roots that might be noise, unless they are known high-freq roots.
# Actually, let's rely on IDF to filter common ones. If 'dy' is everywhere, its IDF will be near 0.

def load_data():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
    return data

def aggregate_contexts(parsed_data, window_size=3):
    # Map: Noun -> Counter of context roots
    noun_contexts = defaultdict(Counter)
    
    print("Aggregating contexts...")
    for i, token in enumerate(parsed_data):
        word = token.get('original', '')
        
        # Filter for Nouns (start with o-)
        if word.startswith('o') and len(word) > 1:
            start = max(0, i - window_size)
            end = min(len(parsed_data), i + window_size + 1)
            
            for j in range(start, end):
                if i == j: continue
                ctx_token = parsed_data[j]
                root = ctx_token.get('root')
                
                if root and len(root) > 1: # Ignore 1-letter roots as noise?
                    noun_contexts[word][root] += 1
                    
    print(f"Found {len(noun_contexts)} unique nouns.")
    return noun_contexts

def cluster_by_tfidf(noun_contexts):
    # 1. Calculate DF (Document Frequency)
    # In how many nouns' context does each root appear?
    root_df = Counter()
    total_nouns = len(noun_contexts)
    
    for noun, counts in noun_contexts.items():
        for root in counts:
            root_df[root] += 1
            
    # 2. Calculate TF-IDF and find max for each noun
    noun_clusters = {} # Noun -> Cluster Label (Top Root)
    
    print("Calculating TF-IDF and assigning clusters...")
    for noun, counts in noun_contexts.items():
        best_root = None
        best_score = -1.0
        
        for root, count in counts.items():
            if root in STOP_ROOTS:
                continue
                
            # TF: Raw count (or log normalized: 1 + log(count))
            tf = count 
            
            # IDF: log(N / df)
            df = root_df[root]
            idf = math.log(total_nouns / (df + 1))
            
            score = tf * idf
            
            if score > best_score:
                best_score = score
                best_root = root
        
        if best_root:
            noun_clusters[noun] = best_root
        else:
            noun_clusters[noun] = "unknown"

    return noun_clusters

def generate_reports(noun_clusters, noun_contexts):
    print("Generating reports...")
    
    # Group by cluster
    clusters = defaultdict(list)
    for noun, cluster_root in noun_clusters.items():
        clusters[cluster_root].append(noun)
        
    # Filter small clusters
    valid_clusters = {k: v for k, v in clusters.items() if len(v) >= 5 and k != "unknown"}
    
    # JSON Output
    output_data = {
        "noun_to_cluster": noun_clusters,
        "clusters": valid_clusters
    }
    with open(OUTPUT_CLUSTERS_JSON, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    # Markdown Report
    with open(OUTPUT_REPORT_MD, 'w') as f:
        f.write("# Noun Clustering Report (Task 168)\n\n")
        f.write("## Methodology\n")
        f.write("- **Algorithm:** TF-IDF on context roots (±3 window). Cluster = Root with highest TF-IDF score.\n")
        f.write(f"- **Total Nouns:** {len(noun_clusters)}\n")
        f.write(f"- **Clusters Found:** {len(valid_clusters)} (with >= 5 members)\n\n")
        
        # Sort clusters by size
        sorted_clusters = sorted(valid_clusters.items(), key=lambda x: len(x[1]), reverse=True)
        
        for root, words in sorted_clusters:
            f.write(f"### Cluster: context '{root}'\n")
            f.write(f"**Size:** {len(words)}\n")
            
            # Show sample
            words.sort()
            preview = ", ".join(words[:20])
            if len(words) > 20:
                preview += f" ... (+{len(words)-20})"
            f.write(f"**Words:** {preview}\n\n")
            
    # Summary Report for Summary File
    with open(OUTPUT_SUMMARY_MD, 'w') as f:
        f.write("# Task 168: Noun Clustering Results\n\n")
        f.write("## Findings\n")
        f.write(f"Clustered {len(noun_clusters)} nouns into {len(valid_clusters)} semantic groups based on context.\n\n")
        f.write("| Context Root | Count | Interpretation |\n")
        f.write("|--------------|-------|----------------|\n")
        
        # Top 10 clusters
        for root, words in sorted_clusters[:15]:
            f.write(f"| **{root}** | {len(words)} | Nouns associated with '{root}' |\n")

def main():
    parsed_data = load_data()
    noun_contexts = aggregate_contexts(parsed_data)
    noun_clusters = cluster_by_tfidf(noun_contexts)
    generate_reports(noun_clusters, noun_contexts)
    print("Done.")

if __name__ == "__main__":
    main()
