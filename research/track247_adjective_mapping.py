
import json
import re
import collections
from pathlib import Path

# Paths
DICTIONARY_PATH = "results/dictionary/dictionary.json"
TEXT_PATH = "data/eva_ivtff.txt"
OUTPUT_PATH = "results/adjective_map.md"

# Focus Adjectives
FOCUS_ADJECTIVES = ["or", "ol", "ok", "dal", "chedy"]

# Load Dictionary
def load_dictionary():
    with open(DICTIONARY_PATH, 'r') as f:
        data = json.load(f)
    
    plant_candidates = set()
    star_candidates = set()
    noun_map = {} # word -> meaning/info

    for word, entry in data.get("entries", {}).items():
        meaning = entry.get("meaning", "").lower()
        domain = entry.get("domain", "").lower()
        
        is_plant = "plant" in meaning or "botanical" in domain
        is_star = "star" in meaning or "astronomy" in domain or "astro" in domain

        if is_plant:
            plant_candidates.add(word)
        if is_star:
            star_candidates.add(word)
        
        if is_plant or is_star:
            noun_map[word] = entry

    return plant_candidates, star_candidates, noun_map

# Parse IVTFF
def parse_ivtff():
    # Store lines by location ID to handle duplicates (different transcribers)
    # Location ID: e.g. <f11r.1>
    lines_by_loc = collections.defaultdict(dict)
    
    with open(TEXT_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse tag and text
            # <f11r.1,@P0;H> text...
            match = re.match(r"^<([^>]+)>\s+(.*)$", line)
            if match:
                tag_content = match.group(1)
                text = match.group(2)
                
                # Extract location and source
                # tag_content might be "f11r.1,@P0;H"
                # We want "f11r.1" or similar as unique line id
                # simple split by ';' to get source
                parts = tag_content.split(';')
                loc_info = parts[0] # e.g. f11r.1,@P0
                source = parts[1] if len(parts) > 1 else "unknown"
                
                # Simplify loc_info to just page.line if possible, but sticking to full loc is safer
                lines_by_loc[loc_info][source] = text

    # Select preferred source for each line
    preferred_sources = ['H', 'C', 'F', 'U', 'V']
    final_lines = []
    
    for loc, variants in lines_by_loc.items():
        selected_text = None
        for src in preferred_sources:
            if src in variants:
                selected_text = variants[src]
                break
        if selected_text is None:
            # Take first available
            selected_text = next(iter(variants.values()))
        
        final_lines.append(selected_text)
        
    return final_lines

def analyze():
    print("Loading dictionary...")
    plant_candidates, star_candidates, noun_map = load_dictionary()
    print(f"Found {len(plant_candidates)} plant candidates and {len(star_candidates)} star candidates.")

    print("Parsing text...")
    lines = parse_ivtff()
    print(f"Processed {len(lines)} lines of text.")

    # Bigram Analysis
    # Structure: noun -> list of adjectives
    noun_adj_counts = collections.defaultdict(collections.Counter)
    
    # Reverse: adjective -> list of nouns it modifies
    adj_noun_counts = collections.defaultdict(collections.Counter)

    for line in lines:
        # Clean and split
        # Replace . with space, remove unknown chars maybe?
        # Voynich text in EVA often uses . as word separator
        words = line.replace('.', ' ').split()
        words = [w for w in words if w and not w.startswith('!') and not w.startswith('%')] # Filter garbage

        for i in range(len(words) - 1):
            noun = words[i]
            adj = words[i+1]
            
            is_plant = noun in plant_candidates
            is_star = noun in star_candidates
            
            if is_plant or is_star:
                noun_adj_counts[noun][adj] += 1
                adj_noun_counts[adj][noun] += 1

    # Generate Report
    output_lines = []
    output_lines.append("# Adjective Mapping Report (Task 247)\n")
    
    output_lines.append("## Focus Adjectives Analysis\n")
    
    for adj in FOCUS_ADJECTIVES:
        output_lines.append(f"### Adjective: `{adj}`")
        
        # Get top nouns modified by this adj
        top_nouns = adj_noun_counts[adj].most_common(20)
        
        if not top_nouns:
            output_lines.append("  - No occurrences finding modifying known plant/star candidates.\n")
            continue
            
        output_lines.append(f"  - **Total Occurrences with Candidates**: {sum(adj_noun_counts[adj].values())}")
        output_lines.append("  - **Top Nouns Modified**:")
        
        for noun, count in top_nouns:
            meaning = noun_map[noun].get("meaning", "unknown")
            domain = noun_map[noun].get("domain", "unknown")
            output_lines.append(f"    - `{noun}` ({count}): {meaning} [{domain}]")
        output_lines.append("")

    output_lines.append("## Definitive Meanings Proposal (Top 10 Adjectives)\n")
    output_lines.append("Based on co-occurrence with known entities:\n")
    
    # Find top overall adjectives modifying candidates
    all_adjs = collections.Counter()
    for adj, nouns in adj_noun_counts.items():
        all_adjs[adj] = sum(nouns.values())
    
    for adj, count in all_adjs.most_common(10):
        output_lines.append(f"### `{adj}` (Count: {count})")
        
        # Check top nouns for this adj to guess meaning
        top_nouns = adj_noun_counts[adj].most_common(5)
        examples = []
        for noun, c in top_nouns:
            meaning = noun_map[noun].get("meaning", "?")
            examples.append(f"{noun}({meaning})")
        
        output_lines.append(f"- **Context**: {', '.join(examples)}")
        output_lines.append(f"- **Proposed Meaning**: [To be filled based on analysis]")
        output_lines.append("")

    # Write Output
    with open(OUTPUT_PATH, 'w') as f:
        f.write("\n".join(output_lines))
    
    print(f"Report generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    analyze()
