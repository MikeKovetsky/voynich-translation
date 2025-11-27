
import json
import re
import collections
import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def load_parsed_data(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_page_structure(text_path, parsed_data):
    print(f"Loading structure from {text_path}...")
    pages = collections.defaultdict(list)
    
    parsed_iter = iter(parsed_data)
    
    with open(text_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            if ';H>' not in line:
                continue
                
            # Extract page ID
            # Format: <f1r.1,@P0;H>
            match = re.search(r'<([a-z0-9]+)\.', line)
            if not match:
                continue
            page_id = match.group(1)
            
            # Clean line logic from task153
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'[.,!=]', ' ', clean_line)
            clean_line = re.sub(r'[^a-zA-Z0-9\s]', '', clean_line)
            words = clean_line.split()
            
            for w in words:
                try:
                    parsed_item = next(parsed_iter)
                except StopIteration:
                    print("Warning: parsed_text.json ended before text file.")
                    return pages
                
                # Verify alignment (optional but good for safety)
                # Note: cleaning might have slight diffs if logic changed, but should match
                # parsed_item['original'] vs w
                
                # We add the ROOT to the page document
                root = parsed_item.get('root', '')
                if root and len(root) >= 2:
                    pages[page_id].append(root)
                    
    return pages

def identify_sections(page_id):
    # Heuristic mapping based on standard VMS sections
    # f1r-f66v: Herbal
    # f67r-f73v: Astronomical
    # f75r-f84v: Biological
    # f85r-f86v: Cosmological (Rosettes) -> Included in Cosmo/Astro usually
    # f87r-f102v: Herbal II (Pharma?) - Actually usually called Herbal II or Pharma
    # f103r-f116v: Recipes (Stars)
    
    # Simplified check
    try:
        if page_id.startswith('f'):
            num_part = int(re.findall(r'\d+', page_id)[0])
        else:
            return "Unknown"
            
        if 1 <= num_part <= 66:
            return "Herbal I"
        elif 67 <= num_part <= 73:
            return "Astronomical"
        elif 75 <= num_part <= 84:
            return "Biological"
        elif 85 <= num_part <= 86:
            return "Rosettes"
        elif 87 <= num_part <= 102:
            return "Herbal II"
        elif 103 <= num_part <= 116:
            return "Recipes"
        else:
            return "Other"
    except:
        return "Unknown"

def run_lda(documents, num_topics, doc_ids):
    print(f"Running LDA with {num_topics} topics...")
    
    # Vectorize
    # max_df=0.9: ignore terms that appear in >90% of documents (too common)
    # min_df=2: ignore terms that appear in <2 documents (too rare)
    tf_vectorizer = CountVectorizer(max_df=0.90, min_df=2, stop_words=None) # We'll handle stop words manually or let max_df handle it
    tf = tf_vectorizer.fit_transform(documents)
    feature_names = tf_vectorizer.get_feature_names_out()
    
    lda = LatentDirichletAllocation(n_components=num_topics, max_iter=10, learning_method='online', random_state=42)
    lda.fit(tf)
    
    return lda, tf, feature_names

def get_top_words(model, feature_names, n_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
        top_words = [feature_names[i] for i in top_features_ind]
        topics.append(top_words)
    return topics

def main():
    parsed_path = 'results/parsed_text.json'
    text_path = 'data/eva_ivtff.txt'
    
    if not os.path.exists(parsed_path):
        print(f"Error: {parsed_path} not found.")
        return

    parsed_data = load_parsed_data(parsed_path)
    pages = load_page_structure(text_path, parsed_data)
    
    print(f"Loaded {len(pages)} pages.")
    
    # Prepare documents
    # Join roots by space
    doc_ids = sorted(pages.keys())
    documents = [" ".join(pages[pid]) for pid in doc_ids]
    
    # Pre-analysis: Identify top common roots to use as stop words?
    # Let's rely on max_df=0.90 to remove words present in almost all pages
    # But Voynich has some words that are frequent but not in ALL pages.
    # Let's remove the top 20 most frequent roots explicitly.
    
    all_roots = [root for page in pages.values() for root in page]
    root_counts = collections.Counter(all_roots)
    top_30_roots = {r for r, c in root_counts.most_common(30)}
    
    print(f"Top 30 roots (will be excluded): {', '.join(list(top_30_roots)[:10])}...")
    
    # Filter documents
    filtered_docs = []
    for doc in documents:
        words = doc.split()
        filtered = [w for w in words if w not in top_30_roots]
        filtered_docs.append(" ".join(filtered))
        
    documents = filtered_docs
    
    results_summary = []
    
    for n_topics in [5, 10, 20]:
        lda, tf, feature_names = run_lda(documents, n_topics, doc_ids)
        top_words = get_top_words(lda, feature_names, 10)
        
        results_summary.append(f"\n## LDA Model with {n_topics} Topics\n")
        
        topic_map = {} # topic_idx -> topic_name (Topic 1, Topic 2...)
        
        for i, words in enumerate(top_words):
            results_summary.append(f"### Topic {i+1}")
            results_summary.append(f"- Top words: {', '.join(words)}")
            topic_map[i] = f"Topic {i+1}"
            
        # Assign pages to topics
        doc_topic_dist = lda.transform(tf)
        
        # Correlate with sections
        section_topic_counts = collections.defaultdict(lambda: collections.Counter())
        
        page_topic_mapping = {}
        
        for i, doc_dist in enumerate(doc_topic_dist):
            topic_idx = doc_dist.argmax()
            page_id = doc_ids[i]
            section = identify_sections(page_id)
            section_topic_counts[section][topic_idx] += 1
            page_topic_mapping[page_id] = {
                "topic": int(topic_idx),
                "section": section,
                "top_words": top_words[topic_idx]
            }
            
        results_summary.append("\n### Section Correlation\n")
        results_summary.append("| Section | Primary Topic | Distribution |")
        results_summary.append("|---|---|---|")
        
        for section in sorted(section_topic_counts.keys()):
            counts = section_topic_counts[section]
            if not counts: continue
            primary_topic = counts.most_common(1)[0][0]
            dist_str = ", ".join([f"T{t+1}: {c}" for t, c in counts.most_common(3)])
            results_summary.append(f"| {section} | Topic {primary_topic+1} | {dist_str} |")

        # If n_topics == 10, save detailed JSON
        if n_topics == 10:
            with open('results/topic_model.json', 'w') as f:
                json.dump({
                    "num_topics": n_topics,
                    "topics": {i: words for i, words in enumerate(top_words)},
                    "page_mapping": page_topic_mapping
                }, f, indent=2)
            print("Saved results/topic_model.json (for k=10)")
            
            # Generate detailed markdown distribution
            with open('results/topic_distribution.md', 'w') as f:
                f.write(f"# Topic Distribution (k={n_topics})\n\n")
                for section in sorted(section_topic_counts.keys()):
                    f.write(f"## {section}\n")
                    counts = section_topic_counts[section]
                    total_pages = sum(counts.values())
                    f.write(f"Total pages: {total_pages}\n\n")
                    for t_idx, count in counts.most_common():
                        pct = count / total_pages * 100
                        f.write(f"- **Topic {t_idx+1}** ({pct:.1f}%): {', '.join(top_words[t_idx][:5])}\n")
                    f.write("\n")
    
    with open('results/track-169-results_summary.md', 'w') as f:
        f.write("# Task 169: Topic Modeling Results\n")
        f.write("\n".join(results_summary))
        
    print("Analysis complete. Saved results.")

if __name__ == "__main__":
    main()
