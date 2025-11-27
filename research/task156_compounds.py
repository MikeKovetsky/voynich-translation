import json
import collections
import os

def main():
    print("Starting Compound Splitter...")
    
    parsed_path = 'results/parsed_text.json'
    if not os.path.exists(parsed_path):
        print("Parsed text not found. Run Task 153 first.")
        return
        
    with open(parsed_path, 'r') as f:
        data = json.load(f)
        
    # 1. Build Valid Root List
    root_counts = collections.Counter([d['root'] for d in data])
    
    valid_roots = set()
    for root, count in root_counts.items():
        # Heuristic: Valid roots are frequent OR look like standard Voynich words (length 2-5)
        if count >= 10 and 2 <= len(root) <= 6:
            valid_roots.add(root)
            
    # Add manual overrides if known high-value roots are missing
    manual_roots = {'aiin', 'chol', 'daiin', 'or', 'ol', 'ar', 'am', 'edy'}
    valid_roots.update(manual_roots)
    
    print(f"Identified {len(valid_roots)} atomic roots.")
    
    # Sort by length desc for greedy matching
    sorted_roots = sorted(list(valid_roots), key=len, reverse=True)
    
    # 2. Split Compounds
    def split_root(text):
        if text in valid_roots:
            return [text]
        
        if len(text) < 2:
            return []
            
        # Greedy match
        for r in sorted_roots:
            if text.startswith(r):
                remainder = text[len(r):]
                # Recursively split remainder
                if remainder == "":
                    return [r]
                
                splits = split_root(remainder)
                if splits:
                    return [r] + splits
                    
        # If no split found, return original as single chunk (failed split)
        return [text]

    new_data = []
    compound_counts = collections.Counter()
    
    for entry in data:
        original_root = entry['root']
        
        if len(original_root) > 6 and original_root not in valid_roots:
            split_roots = split_root(original_root)
            if len(split_roots) > 1:
                compound_counts["-".join(split_roots)] += 1
        else:
            split_roots = [original_root]
            
        new_entry = entry.copy()
        new_entry['roots'] = split_roots
        del new_entry['root'] # Remove old single root
        new_data.append(new_entry)
        
    # 3. Save Results
    with open('results/parsed_text_v2.json', 'w') as f:
        json.dump(new_data, f, indent=2)
        
    # 4. Report
    with open('results/compound_analysis.md', 'w') as f:
        f.write("# Compound Analysis Report\n\n")
        f.write(f"Total atomic roots identified: {len(valid_roots)}\n")
        f.write("## Top 20 Compounds Found\n")
        for c, count in compound_counts.most_common(20):
            f.write(f"- {c}: {count}\n")
            
    print("Splitting complete. Saved to results/parsed_text_v2.json")
    print("Report saved to results/compound_analysis.md")

if __name__ == "__main__":
    main()
