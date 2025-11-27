import json
import collections
import os

def main():
    print("Analyzing Prefix Logic...")
    parsed_path = 'results/parsed_text.json'
    
    if not os.path.exists(parsed_path):
        print("Parsed text not found. Run Task 153 first.")
        return
        
    with open(parsed_path, 'r') as f:
        data = json.load(f)
        
    # 1. Co-occurrence Matrix (Prefix -> Root)
    prefix_root = collections.defaultdict(collections.Counter)
    # 2. Positional (Start of line?)
    # We need line info, but parsed_text is a flat list.
    # We will infer sentence structure if possible, but for now let's stick to word-internal logic.
    
    # 3. Prefix Stacking
    stacking = collections.Counter()
    
    for entry in data:
        prefixes = entry['prefix']
        root = entry['root']
        
        if prefixes:
            # Last prefix is closest to root
            immediate_prefix = prefixes[-1]
            prefix_root[immediate_prefix][root] += 1
            
            # Stacking patterns
            if len(prefixes) > 1:
                stacking[tuple(prefixes)] += 1
                
    # Output Report
    report = []
    report.append("# Prefix Logic Report\n")
    
    report.append("## 1. Top Stacking Patterns")
    for stack, count in stacking.most_common(10):
        report.append(f"- {' + '.join(stack)}: {count}")
        
    report.append("\n## 2. Prefix Preferences")
    target_prefixes = ['qo', 'y', 'd', 'o', 's']
    
    for p in target_prefixes:
        report.append(f"\n### Prefix '{p}'")
        total_uses = sum(prefix_root[p].values())
        report.append(f"Total occurrences: {total_uses}")
        report.append("Top roots:")
        for r, c in prefix_root[p].most_common(5):
            report.append(f"- {r}: {c} ({c/total_uses:.1%})")
            
    with open('results/prefix_grammar_report.md', 'w') as f:
        f.write("\n".join(report))
        
    print("Report generated at results/prefix_grammar_report.md")

if __name__ == "__main__":
    main()
