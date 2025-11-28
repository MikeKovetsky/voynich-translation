import json
import re
import os
import csv
from collections import Counter, defaultdict

def load_dictionary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)["entries"]

def load_corpus(filepath):
    text = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#"): continue
            # Simple tokenization: split by dot or space
            cleaned = line.replace(".", " ").replace("!", "").replace("*", "")
            words = cleaned.split()
            text.extend([w for w in words if not w.startswith("<") and w != "-"])
    return text

def cluster_ingredients(text_file, dict_file, output_csv, report_file):
    print("Clustering Ingredients...")
    entries = load_dictionary(dict_file)
    corpus = load_corpus(text_file)
    
    # Define Verb Categories
    liquid_verbs = ["chedy", "shedy", "saiin", "ol", "qokeedy"] # Drink, Mix, Wash, Liquid, Decoction
    solid_verbs = ["qokeey", "qoke", "chdy", "sal", "ar", "or"] # Cook, Eat, Salt, Grind, Harvest
    
    # Identify Candidates (Objects/Ingredients)
    # We scan for words appearing +1 or -1 from these verbs
    candidates = defaultdict(lambda: {"liquid": 0, "solid": 0, "total": 0})
    
    for i in range(len(corpus)):
        word = corpus[i]
        
        # Context Check
        prev_word = corpus[i-1] if i > 0 else ""
        next_word = corpus[i+1] if i < len(corpus)-1 else ""
        
        context_words = [prev_word, next_word]
        
        is_liquid_context = any(w in liquid_verbs for w in context_words)
        is_solid_context = any(w in solid_verbs for w in context_words)
        
        if is_liquid_context:
            candidates[word]["liquid"] += 1
            candidates[word]["total"] += 1
        if is_solid_context:
            candidates[word]["solid"] += 1
            candidates[word]["total"] += 1

    # Filter and Classify
    classified = []
    
    for word, counts in candidates.items():
        if counts["total"] < 10: continue # Noise filter
        
        # Calculate Ratios
        liq_ratio = counts["liquid"] / counts["total"]
        sol_ratio = counts["solid"] / counts["total"]
        
        category = "Neutral"
        if liq_ratio > 0.7: category = "Liquid"
        elif sol_ratio > 0.7: category = "Solid"
        
        # Check Dictionary Meaning if exists
        meaning = "Unknown"
        if word in entries:
            meaning = entries[word]["meaning"]
            
        classified.append({
            "word": word,
            "category": category,
            "liquid_score": f"{liq_ratio:.2f}",
            "solid_score": f"{sol_ratio:.2f}",
            "total_context": counts["total"],
            "current_meaning": meaning
        })
        
    # Sort by frequency
    classified.sort(key=lambda x: x["total_context"], reverse=True)
    
    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["word", "category", "liquid_score", "solid_score", "total_context", "current_meaning"])
        writer.writeheader()
        writer.writerows(classified)
        
    # Write Report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Ingredient Cluster Report\n\n")
        f.write("## Methodology\n")
        f.write("- **Liquid Verbs:** chedy (Mix), shedy, saiin, ol, qokeedy\n")
        f.write("- **Solid Verbs:** qokeey (Cook), chdy, sal, ar, or\n")
        f.write("- **Threshold:** > 70% association\n\n")
        
        f.write("## Top Liquid Ingredients (Solvents)\n")
        f.write("| Word | Score | Count | Current Meaning |\n|---|---|---|---|\n")
        for item in classified:
            if item["category"] == "Liquid" and item["total_context"] > 20:
                f.write(f"| **{item['word']}** | {item['liquid_score']} | {item['total_context']} | {item['current_meaning']} |\n")
                
        f.write("\n## Top Solid Ingredients (Solutes)\n")
        f.write("| Word | Score | Count | Current Meaning |\n|---|---|---|---|\n")
        for item in classified:
            if item["category"] == "Solid" and item["total_context"] > 20:
                f.write(f"| **{item['word']}** | {item['solid_score']} | {item['total_context']} | {item['current_meaning']} |\n")

    print(f"Clustering complete: {report_file}")

if __name__ == "__main__":
    cluster_ingredients(
        "data/eva_ivtff.txt",
        "results/dictionary/master_dictionary_v18.json",
        "artifacts/ingredient_clusters.csv",
        "results/ingredient_cluster_report.md"
    )
