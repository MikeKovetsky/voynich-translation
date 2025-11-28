import json
import re
import os
import csv
from collections import defaultdict

def load_dictionary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)["entries"]

def load_corpus(filepath):
    text = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#"): continue
            cleaned = line.replace(".", " ").replace("!", "").replace("*", "")
            words = cleaned.split()
            text.extend([w for w in words if not w.startswith("<") and w != "-"])
    return text

def load_clusters(filepath):
    clusters = {"Liquid": [], "Solid": []}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["category"] in clusters:
                    clusters[row["category"]].append(row["word"])
    return clusters

def match_plants(text_file, dict_file, cluster_file, report_file):
    print("Matching Plants via Recipes...")
    
    entries = load_dictionary(dict_file)
    corpus = load_corpus(text_file)
    clusters = load_clusters(cluster_file)
    
    liquids = set(clusters["Liquid"])
    solids = set(clusters["Solid"])
    
    # Verbs
    boil_verbs = ["qokeey", "qoke", "qokedy", "qokeedy"] # Cook/Boil
    mix_verbs = ["chedy", "shedy"] # Mix
    
    # Plant Candidates (from Dictionary)
    plant_candidates = [w for w, d in entries.items() if "plant" in d["meaning"].lower() or "herb" in d["meaning"].lower()]
    
    # Profile Accumulator
    profiles = defaultdict(lambda: {"boil": 0, "mix_liquid": 0, "mix_solid": 0, "adar": 0, "total": 0})
    
    for i in range(len(corpus)):
        word = corpus[i]
        if word not in plant_candidates: continue
        
        profiles[word]["total"] += 1
        
        # Window scan (+/- 3 words)
        start = max(0, i-3)
        end = min(len(corpus), i+4)
        context = corpus[start:end]
        
        # Check Profile
        if any(v in context for v in boil_verbs):
            profiles[word]["boil"] += 1
            
        if any(v in context for v in mix_verbs):
            # Check what it is mixed WITH
            if any(l in context for l in liquids):
                profiles[word]["mix_liquid"] += 1
            if any(s in context for s in solids):
                profiles[word]["mix_solid"] += 1
                
        if "dar" in context or "adar" in context: # Adar/March
            profiles[word]["adar"] += 1

    # Analyze and Propose Matches
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Plant Recipe Match Report\n\n")
        f.write("## Methodology\n")
        f.write("Profiling plants based on: Boiling (Decoction), Mixing with Liquid (Infusion), Mixing with Solid (Poultice).\n\n")
        
        f.write("## Top Plant Candidates & Profiles\n")
        f.write("| Plant Word | Count | Boil % | Mix-Liq % | Mix-Sol % | Adar % | Proposed ID |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        
        sorted_plants = sorted(profiles.items(), key=lambda x: x[1]["total"], reverse=True)
        
        for word, p in sorted_plants:
            if p["total"] < 5: continue
            
            boil_pct = (p["boil"] / p["total"]) * 100
            liq_pct = (p["mix_liquid"] / p["total"]) * 100
            sol_pct = (p["mix_solid"] / p["total"]) * 100
            adar_pct = (p["adar"] / p["total"]) * 100
            
            # Logic for ID
            proposal = "Generic Herb"
            if boil_pct > 30:
                proposal = "Pot Herb / Root (e.g. Betony, Radish)"
            if liq_pct > 30:
                proposal = "Infusion Herb (e.g. Mint, Sage)"
            if sol_pct > 10:
                proposal = "Dry Spice / Resin"
            if adar_pct > 10:
                proposal = "Spring Tonic (e.g. Nettle, Dandelion)"
                
            f.write(f"| **{word}** | {p['total']} | {boil_pct:.1f}% | {liq_pct:.1f}% | {sol_pct:.1f}% | {adar_pct:.1f}% | {proposal} |\n")

    print(f"Matching complete: {report_file}")

if __name__ == "__main__":
    match_plants(
        "data/eva_ivtff.txt",
        "results/dictionary/master_dictionary_v18.json",
        "artifacts/ingredient_clusters.csv",
        "results/plant_recipe_match_report.md"
    )
