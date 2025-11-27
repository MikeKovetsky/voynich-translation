import json
import collections
import os

def main():
    print("Analyzing Prefix Logic (Fixed Data)...")
    parsed_path = 'results/parsed_text.json'
    
    if not os.path.exists(parsed_path):
        print("Parsed text not found.")
        return
        
    with open(parsed_path, 'r') as f:
        data = json.load(f)
        
    prefix_root = collections.defaultdict(collections.Counter)
    
    for entry in data:
        prefixes = entry['prefix']
        root = entry['root']
        
        if prefixes:
            immediate_prefix = prefixes[-1]
            prefix_root[immediate_prefix][root] += 1
            
    report = []
    report.append("# Prefix Logic Report (Fixed)\n")
    
    target_prefixes = ['qo', 'y', 'd', 'o', 's', 'qok']
    
    for p in target_prefixes:
        report.append(f"\n### Prefix '{p}'")
        total_uses = sum(prefix_root[p].values())
        report.append(f"Total occurrences: {total_uses}")
        report.append("Top roots:")
        for r, c in prefix_root[p].most_common(10):
            report.append(f"- {r}: {c} ({c/total_uses:.1%})")
            
    with open('results/prefix_grammar_report.md', 'w') as f:
        f.write("\n".join(report))
        
    print("Report generated.")

if __name__ == "__main__":
    main()
