import json
import os
import re
from collections import Counter
import csv

def load_ivtff_transcription(path):
    print(f"Parsing IVTFF: {path}")
    lines_map = {} # id -> {ver: text}
    
    # Priority: H (Takahashi) > C (Currier) > F (First Study Group) > U (Unknown/Other)
    PRIORITY = ['H', 'C', 'F', 'U']
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'): continue
                # Regex to match <f1r.1;H> or <f1r.1,tag;H>
                match = re.match(r'<f([\w\d\.]+).*?;([A-Za-z0-9])>\s+(.*)', line)
                if match:
                    loc_id = match.group(1)
                    ver = match.group(2)
                    text = match.group(3).strip()
                    if loc_id not in lines_map:
                        lines_map[loc_id] = {}
                    lines_map[loc_id][ver] = text
    except FileNotFoundError:
        print(f"File not found: {path}")
        return []

    print(f"Found {len(lines_map)} unique line locations.")

    final_tokens = []
    used_versions = Counter()

    for loc_id, variants in lines_map.items():
        selected_text = ""
        selected_ver = ""
        for p in PRIORITY:
            if p in variants:
                selected_text = variants[p]
                selected_ver = p
                break
        if not selected_text and variants:
            selected_ver = list(variants.keys())[0]
            selected_text = variants[selected_ver]
        
        if selected_text:
            used_versions[selected_ver] += 1
            
            # Clean text
            # Remove <...> tags (often comments or glosses like <!plant>)
            text_clean = re.sub(r'<[^>]+>', '', selected_text)
            # Remove {...} tags
            text_clean = re.sub(r'\{[^}]+\}', '', text_clean)
            # Remove (...) tags? Sometimes comments.
            # IVTFF might use () for unsure chars? 
            # Takahashi usually uses ! or ? for unsure.
            # Let's assume () are comments if they contain non-EVA?
            # To be safe, I'll just remove <...> and {...} for now, and ensure tokens look "Voynich-like".
            
            # Replace dots and commas with space
            text_clean = text_clean.replace('.', ' ').replace(',', ' ')
            
            tokens = text_clean.split()
            for t in tokens:
                t = t.strip()
                # Filter out obvious non-Voynich noise
                # Voynich words are usually lowercase a-z, maybe digits, maybe !?*
                # If it contains < or > or { or }, it's bad (should be gone).
                # If it is just "-" or "=" or "%", ignore.
                if len(t) > 0 and not re.match(r'^[-%=!*]+$', t):
                    final_tokens.append(t)

    print(f"Version usage: {dict(used_versions)}")
    return final_tokens

def load_dictionary(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('entries', {})
    except FileNotFoundError:
        print(f"File not found: {path}")
        return {}

def main():
    ivtff_path = 'data/eva_ivtff.txt'
    dictionary_path = 'results/dictionary/master_dictionary_v16.json'
    
    if not os.path.exists(ivtff_path):
        if os.path.exists('eva_ivtff.txt'):
            ivtff_path = 'eva_ivtff.txt'
    
    print(f"Using transcription file: {ivtff_path}")
    print(f"Using dictionary file: {dictionary_path}")

    tokens = load_ivtff_transcription(ivtff_path)
    if not tokens:
        print("No tokens found. Exiting.")
        return

    total_words = len(tokens)
    print(f"Total tokens: {total_words}")
    
    word_counts = Counter(tokens)
    print(f"Unique words: {len(word_counts)}")

    known_entries = load_dictionary(dictionary_path)
    known_words = set(known_entries.keys())
    print(f"Known words in dictionary: {len(known_words)}")

    unknown_words = {word: count for word, count in word_counts.items() if word not in known_words}
    sorted_unknown = sorted(unknown_words.items(), key=lambda x: x[1], reverse=True)
    
    top_100 = sorted_unknown[:100]
    
    csv_path = 'results/top_100_unknowns.csv'
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Frequency'])
        writer.writerows(top_100)
    print(f"Saved {csv_path}")

    # Morphology
    sorted_known_roots = sorted([k for k in known_words if len(k) >= 3], key=len, reverse=True)
    root_hits = {} 
    
    for unknown, count in unknown_words.items():
        # Skip if unknown word contains non-alpha chars that look like noise?
        # e.g. "8am" is valid EVA (8, a, m).
        
        found_root = None
        for root in sorted_known_roots:
            if root in unknown:
                found_root = root
                break 
        
        if found_root:
            if found_root not in root_hits:
                root_hits[found_root] = {'variants': [], 'total_gain': 0}
            
            root_hits[found_root]['variants'].append(unknown)
            root_hits[found_root]['total_gain'] += count

    sorted_opportunities = sorted(root_hits.items(), key=lambda x: x[1]['total_gain'], reverse=True)
    
    output_opportunities = []
    for root, data in sorted_opportunities:
        output_opportunities.append({
            'root': root,
            'total_gain': data['total_gain'],
            'variants': sorted(data['variants'], key=lambda w: word_counts[w], reverse=True)
        })
        
    json_path = 'results/morphology_opportunities.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_opportunities, f, indent=2)
    print(f"Saved {json_path}")

    # Summary
    known_token_count = sum(word_counts[w] for w in known_words if w in word_counts)
    current_coverage = known_token_count / total_words if total_words > 0 else 0
    
    target_coverage = 0.50
    needed_coverage = max(0, target_coverage - current_coverage)
    needed_tokens = needed_coverage * total_words
    
    top_100_gain = sum(c for w, c in top_100)
    
    summary_md = f"""# Track 301: Coverage Audit Results

## Status
- **Total Tokens:** {total_words}
- **Unique Words:** {len(word_counts)}
- **Known Words (Dictionary):** {len(known_words)}
- **Current Coverage:** {current_coverage:.2%} ({known_token_count} tokens)
- **Goal:** 50% Coverage
- **Gap:** {needed_tokens:.0f} tokens needed.

## Top 100 Unknowns
- See `results/top_100_unknowns.csv`
- Cumulative coverage gain if solved: {top_100_gain} tokens ({top_100_gain/total_words:.2%})

## Morphology Opportunities
- See `results/morphology_opportunities.json`
- Top 10 Roots by potential gain:
"""
    
    for i, item in enumerate(output_opportunities[:10]):
        summary_md += f"{i+1}. **{item['root']}**: +{item['total_gain']} tokens ({len(item['variants'])} variants)\n"

    summary_path = 'results/track-301-results_summary.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_md)
    print(f"Saved {summary_path}")

if __name__ == '__main__':
    main()
