import csv
import os

def propose_plants(profile_file, output_file):
    print("Proposing Plant IDs...")
    
    proposals = []
    
    # Define Functional Knowledge Base (Medieval)
    # Source: Tractatus de Herbis / Dioscorides
    kb = {
        "Boil": ["Betony", "Mallow", "Radish", "Mandrake (Root)", "Fennel"],
        "Infusion": ["Mint", "Sage", "Wormwood", "Rue", "Lavender"],
        "Spice": ["Pepper", "Ginger", "Cumin", "Resin"],
        "Spring": ["Nettle", "Dandelion", "Primrose", "Violet"]
    }
    
    with open(profile_file, 'r', encoding='utf-8') as f:
        # Skip header lines until table
        lines = f.readlines()
        
    for line in lines:
        if "|" not in line or "Plant Word" in line or "---" in line: continue
        
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8: continue
        
        word = parts[1].replace("**", "")
        profile = parts[7] # Proposed ID column from previous report
        
        candidates = []
        confidence = "Low"
        
        if "Pot Herb" in profile or "Boil" in profile:
            candidates = kb["Boil"]
            confidence = "Medium (Functional Match)"
        elif "Infusion" in profile:
            candidates = kb["Infusion"]
            confidence = "Medium (Functional Match)"
        elif "Dry" in profile:
            candidates = kb["Spice"]
        elif "Spring" in profile:
            candidates = kb["Spring"]
            confidence = "High (Seasonal Match)"
            
        cand_str = ", ".join(candidates) if candidates else "Generic"
        
        proposals.append({
            "voynich_word": word,
            "profile": profile,
            "candidates": cand_str,
            "confidence": confidence
        })
        
    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["voynich_word", "profile", "candidates", "confidence"])
        writer.writeheader()
        writer.writerows(proposals)
        
    print(f"Proposals generated: {output_file}")

if __name__ == "__main__":
    propose_plants(
        "results/plant_recipe_match_report.md",
        "results/plant_id_proposals.csv"
    )
