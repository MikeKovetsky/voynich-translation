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
        
    # 1. Build Atomic Root List
    # Task: Scan parsed_text.json for roots that are: Short (length 2-5), Frequent (count > 10)
    root_counts = collections.Counter([d['root'] for d in data])
    
    valid_roots = set()
    for root, count in root_counts.items():
        if count > 10 and 2 <= len(root) <= 5:
            valid_roots.add(root)
            
    # Add manual overrides as per task example/implication (e.g. 'aiin', 'chol', 'daiin', 'or')
    # The task mentions these specifically.
    manual_roots = {'aiin', 'chol', 'daiin', 'or', 'ol', 'ar', 'am', 'edy', 'qok', 'she', 'che'}
    valid_roots.update(manual_roots)
    
    print(f"Identified {len(valid_roots)} atomic roots.")
    
    # Sort by length desc for greedy matching
    sorted_roots = sorted(list(valid_roots), key=len, reverse=True)
    
    # 2. Split Compounds
    def split_root(text):
        # If the text itself is a valid root, return it
        if text in valid_roots:
            return [text]
        
        # If too short to split
        if len(text) < 2:
            return [text]
            
        # Greedy match
        for r in sorted_roots:
            if text.startswith(r):
                remainder = text[len(r):]
                if remainder == "":
                    return [r]
                
                # Recursively split remainder
                splits = split_root(remainder)
                
                return [r] + splits
                    
        # If no valid root matches the start, we can't split this part.
        # Return as is.
        return [text]

    new_data = []
    compound_counts = collections.Counter()
    
    for entry in data:
        original_root = entry['root']
        
        # Task: For every root in parsed_text.json longer than 6 characters
        if len(original_root) > 6:
             # Try to decompose
            split_roots = split_root(original_root)
            
            # If we actually split it (more than 1 part)
            if len(split_roots) > 1:
                compound_counts["-".join(split_roots)] += 1
        else:
            split_roots = [original_root]
            
        new_entry = entry.copy()
        new_entry['roots'] = split_roots
        del new_entry['root'] 
        new_data.append(new_entry)
        
    # 3. Re-assemble Data & Save
    with open('results/parsed_text_v2.json', 'w') as f:
        json.dump(new_data, f, indent=2)
        
    # 4. Output Report
    with open('results/compound_analysis.md', 'w') as f:
        f.write("# Compound Analysis Report\n\n")
        f.write(f"Total atomic roots identified: {len(valid_roots)}\n")
        f.write("## Top 50 Compounds Found\n")
        f.write("| Compound | Count |\n")
        f.write("|----------|-------|\n")
        for c, count in compound_counts.most_common(50):
            f.write(f"| {c} | {count} |\n")
            
    print("Splitting complete. Saved to results/parsed_text_v2.json")
    print("Report saved to results/compound_analysis.md")

if __name__ == "__main__":
    main()
