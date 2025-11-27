import sys
import os
from pathlib import Path
import json

# Add current directory to path so we can import from research
sys.path.append(os.getcwd())

from research import voynich_data

def main():
    print("Starting Rosette Decoding (Track 282)...")

    # 1. Load Data
    try:
        pages = voynich_data.get_eva_pages()
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return

    # Identify Rosettes pages
    # f86v is a large foldout, often labeled f86v, f86v3, f86v4 etc in different transcriptions.
    # Let's find all keys starting with f86v
    rosette_keys = [k for k in pages.keys() if k.startswith('f86v')]
    print(f"Found Rosette pages: {rosette_keys}")
    
    if not rosette_keys:
        print("Error: No f86v pages found.")
        # Fallback: try searching for keys containing '86v'
        rosette_keys = [k for k in pages.keys() if '86v' in k]
        print(f"Retry found: {rosette_keys}")
        if not rosette_keys:
            return

    # 2. Extract words
    rosette_words = []
    word_locations = {} # word -> list of (page, line)
    
    for page_id in rosette_keys:
        lines = pages[page_id]
        for loc, text in lines.items():
            # Clean text
            # Remove transcribed comments/uncertainties often marked with punctuation or brackets
            text_clean = text.replace('!', '').replace('?', '').replace('<', '').replace('>', '')
            # Standardize spaces
            text_clean = text_clean.replace(',', ' ').replace('-', ' ')
            
            words = text_clean.split('.')
            for w in words:
                w = w.strip()
                if not w: continue
                rosette_words.append(w)
                if w not in word_locations:
                    word_locations[w] = []
                word_locations[w].append(f"{page_id}:{loc}")

    print(f"Total words in Rosettes: {len(rosette_words)}")

    # 3. Target Vocabulary
    targets = {
        "Fire": ["sho", "choly"],
        "Water": ["o", "ol"],
        "Air": ["shey"],
        "Earth": ["or"],
        "Star": ["os"]
    }
    
    # Flatten targets for searching
    target_map = {}
    for category, terms in targets.items():
        for term in terms:
            target_map[term] = category

    # 4. Search
    hits = {cat: [] for cat in targets}
    
    for w in rosette_words:
        # Check against all targets
        for term, category in target_map.items():
            # Match Logic
            is_match = False
            match_type = ""
            
            if w == term:
                is_match = True
                match_type = "exact"
            elif w.startswith(term):
                # For short terms (len <= 2), prefix matching is too aggressive (e.g. 'o' matches everything)
                if len(term) > 2:
                    is_match = True
                    match_type = "prefix"
            elif w.endswith(term):
                 # Similarly for suffix
                if len(term) > 2:
                    is_match = True
                    match_type = "suffix"
            elif term in w:
                 if len(term) > 3:
                    is_match = True
                    match_type = "contains"

            if is_match:
                hits[category].append({
                    "word": w,
                    "term": term,
                    "type": match_type,
                    "locations": word_locations[w]
                })

    # 5. Generate Report
    output_lines = []
    output_lines.append("# Rosette Analysis (Track 282)")
    output_lines.append(f"\nAnalyzed Pages: {', '.join(rosette_keys)}")
    output_lines.append(f"Total Words: {len(rosette_words)}")
    output_lines.append("\n## Target Vocabulary Distribution")
    
    total_hits_all = 0
    
    for cat, results in hits.items():
        unique_hits = {}
        for r in results:
            w = r['word']
            if w not in unique_hits:
                unique_hits[w] = {'count': 0, 'locs': set(), 'types': set()}
            unique_hits[w]['count'] += 1
            unique_hits[w]['locs'].update(r['locations'])
            unique_hits[w]['types'].add(r['type'])
            
        total_hits_all += len(results)
        
        output_lines.append(f"\n### {cat} (Terms: {', '.join(targets[cat])})")
        output_lines.append(f"Total Occurrences: {len(results)}")
        
        # Sort by count
        sorted_hits = sorted(unique_hits.items(), key=lambda x: x[1]['count'], reverse=True)
        
        if sorted_hits:
            output_lines.append("| Word | Count | Types | Locations (Sample) |")
            output_lines.append("|---|---|---|---|")
            for w, data in sorted_hits:
                sample_locs = list(data['locs'])[:3]
                loc_str = ", ".join(sample_locs)
                if len(data['locs']) > 3:
                    loc_str += "..."
                types_str = ", ".join(data['types'])
                output_lines.append(f"| {w} | {data['count']} | {types_str} | {loc_str} |")
        else:
            output_lines.append("No matches found.")

    # Write analysis
    with open("results/rosette_analysis.md", "w") as f:
        f.write("\n".join(output_lines))
        
    print("Written results/rosette_analysis.md")
    
    # Write summary
    summary_lines = []
    summary_lines.append("# Track 282 Results Summary: Rosette Decoding")
    summary_lines.append("\n## Findings")
    summary_lines.append(f"- Analyzed {len(rosette_words)} words across pages {', '.join(rosette_keys)}.")
    summary_lines.append(f"- Found {total_hits_all} occurrences of elemental terms.")
    
    summary_lines.append("\n## Elemental Distribution")
    for cat in hits:
        count = len(hits[cat])
        summary_lines.append(f"- **{cat}**: {count}")
        
    max_cat = max(hits, key=lambda k: len(hits[k]))
    summary_lines.append("\n## Conclusion")
    summary_lines.append(f"The analysis shows a prevalence of **{max_cat}** terms.")
    summary_lines.append("This suggests that while elemental terms are present, their distribution needs to be correlated with specific circles in the diagram for a definitive 'Cosmology' mapping.")
    summary_lines.append("Further visual grounding (Track 283) is recommended to map these words to specific coordinates on the page.")
    
    with open("results/track-282-results_summary.md", "w") as f:
        f.write("\n".join(summary_lines))

    print("Written results/track-282-results_summary.md")

if __name__ == "__main__":
    main()
