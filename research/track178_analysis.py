import json
import os
from collections import defaultdict

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    # 1. Load Inputs
    herbal_taxonomy = load_json('results/herbal_taxonomy.json')
    parsed_text = load_json('results/parsed_text.json')
    root_dictionary = load_json('results/root_dictionary_v3.json')
    noun_clusters_data = load_json('results/noun_clusters.json')
    
    noun_to_cluster = noun_clusters_data.get('noun_to_cluster', {})

    # Filter for Plant Parts
    plant_parts = set()
    for word, data in herbal_taxonomy.items():
        if data.get('category') == 'PLANT_PART':
            plant_parts.add(word)
    
    # Add specific targets from task if not already included
    target_parts = {'oty', 'otol', 'okol'}
    plant_parts.update(target_parts)

    print(f"Identified {len(plant_parts)} plant part candidates.")

    # Create Root Meaning Map
    root_meanings = {}
    for root, data in root_dictionary.get('roots', {}).items():
        root_meanings[root] = data.get('meanings', [])

    # 2. Context Extraction
    # Store adjectives and verbs for each plant part
    # Structure: { plant_part: { 'adjectives': [roots], 'verbs': [roots] } }
    context_data = defaultdict(lambda: {'adjectives': [], 'verbs': []})

    # Helper to check if token is an adjective (o- prefix)
    def is_adjective(token):
        return 'o' in token.get('prefix', [])

    # Helper to check if token is a verb (qok- prefix)
    def is_verb(token):
        return 'qok' in token.get('prefix', [])

    # Iterate through text
    # We'll look at a window of neighbors. Let's say +/- 3 tokens.
    window_size = 3
    text_len = len(parsed_text)

    for i, token in enumerate(parsed_text):
        original_word = token.get('original')
        
        if original_word in plant_parts:
            # Look around
            start = max(0, i - window_size)
            end = min(text_len, i + window_size + 1)
            
            for j in range(start, end):
                if i == j: continue
                
                neighbor = parsed_text[j]
                
                if is_adjective(neighbor):
                    context_data[original_word]['adjectives'].append(neighbor.get('root'))
                
                if is_verb(neighbor):
                    context_data[original_word]['verbs'].append(neighbor.get('root'))

    # 3. Semantic Profiling & Analysis
    profiles = []

    for part, data in context_data.items():
        if not data['adjectives'] and not data['verbs']:
            continue

        # Count frequencies
        adj_counts = defaultdict(int)
        for root in data['adjectives']:
            adj_counts[root] += 1
            
        verb_counts = defaultdict(int)
        for root in data['verbs']:
            verb_counts[root] += 1

        # Analyze meanings
        profile = {
            'term': part,
            'cluster': noun_to_cluster.get(part, "Unknown"),
            'adjectives': [],
            'verbs': [],
            'likely_meaning': []
        }

        # Top adjectives
        sorted_adjs = sorted(adj_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for root, count in sorted_adjs:
            meanings = root_meanings.get(root, ["Unknown"])
            profile['adjectives'].append(f"{root} ({count}): {', '.join(meanings)}")
            
            # Inference Logic (simplified based on task)
            # Note: Real dictionary meanings might not literally be "Green" or "Red" yet, 
            # but we look for keywords if present, or just report them.
            # The task implies we might find "Green/Red" meanings.
            # Let's check for keywords in meanings.
            for m in meanings:
                m_lower = m.lower()
                if 'green' in m_lower or 'red' in m_lower:
                    if "Leaf/Flower" not in profile['likely_meaning']: profile['likely_meaning'].append("Leaf/Flower")
                if 'long' in m_lower or 'white' in m_lower:
                    if "Root/Stalk" not in profile['likely_meaning']: profile['likely_meaning'].append("Root/Stalk")

        # Top verbs
        sorted_verbs = sorted(verb_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for root, count in sorted_verbs:
            meanings = root_meanings.get(root, ["Unknown"])
            profile['verbs'].append(f"{root} ({count}): {', '.join(meanings)}")
            
            for m in meanings:
                m_lower = m.lower()
                if 'dig' in m_lower or 'cut' in m_lower:
                    if "Root" not in profile['likely_meaning']: profile['likely_meaning'].append("Root")
                if 'pluck' in m_lower or 'gather' in m_lower:
                    if "Fruit/Flower" not in profile['likely_meaning']: profile['likely_meaning'].append("Fruit/Flower")

        profiles.append(profile)

    # 4. Output Generation
    
    # Sort profiles by most frequent usage (sum of total adj + verb occurrences)
    def get_total_occurrences(p):
        # Extract counts from strings like "root (5): meaning"
        count = 0
        for s in p['adjectives'] + p['verbs']:
            try:
                c = int(s.split('(')[1].split(')')[0])
                count += c
            except:
                pass
        return count

    profiles.sort(key=get_total_occurrences, reverse=True)

    # Write detailed report
    with open('results/plant_part_profiles.md', 'w') as f:
        f.write('# Plant Part Profiles\n\n')
        f.write('Analysis of "Plant Part" terms based on associated adjectives (o-) and verbs (qok-).\n\n')
        
        for p in profiles:
            f.write(f"## {p['term']}\n")
            f.write(f"- **Cluster:** {p['cluster']}\n")
            f.write(f"- **Likely Meaning:** {', '.join(p['likely_meaning']) if p['likely_meaning'] else 'Undetermined'}\n")
            
            f.write("- **Top Adjectives:**\n")
            if p['adjectives']:
                for a in p['adjectives']:
                    f.write(f"  - {a}\n")
            else:
                f.write("  - None found\n")
                
            f.write("- **Top Verbs:**\n")
            if p['verbs']:
                for v in p['verbs']:
                    f.write(f"  - {v}\n")
            else:
                f.write("  - None found\n")
            f.write("\n")

    # Write summary
    with open('results/track-178-results_summary.md', 'w') as f:
        f.write('# Task 178: Plant Part Decoding Summary\n\n')
        f.write('## Overview\n')
        f.write('Identified probable meanings for generic plant parts by analyzing modifier and verb associations.\n\n')
        f.write('| Term | Cluster | Likely Meaning | Key Associations |\n')
        f.write('|---|---|---|---|\n')
        
        for p in profiles[:20]: # Summary of top 20
            meaning = ', '.join(p['likely_meaning']) if p['likely_meaning'] else '?'
            key_assoc = []
            if p['adjectives']: key_assoc.append(f"Adj: {p['adjectives'][0].split('(')[0]}")
            if p['verbs']: key_assoc.append(f"Verb: {p['verbs'][0].split('(')[0]}")
            assoc_str = '; '.join(key_assoc)
            f.write(f"| {p['term']} | {p['cluster']} | {meaning} | {assoc_str} |\n")

if __name__ == "__main__":
    main()
