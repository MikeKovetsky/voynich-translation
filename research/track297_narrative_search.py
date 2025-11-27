
import re
from collections import Counter
import os

# Configuration
INPUT_FILE = 'data/eva_ivtff.txt'
TARGET_PAGES = ['f67v2', 'f8v', 'f90r1']
OUTPUT_ANALYSIS = 'results/narrative_analysis.md'
OUTPUT_SUMMARY = 'results/track-297-results_summary.md'

# Grammar definitions (from recipe_grammar.json and heuristic)
RECIPE_PREFIXES = ['ol', 'qo', 'qok', 'o', 'y']
RECIPE_SUFFIXES = ['y'] # Imperative
CONNECTORS = ['so', 'do', 'ka']
COMMON_VERBS = ['daiin']

def parse_ivtff(file_path, target_pages):
    """Extracts text for target pages from IVTFF file."""
    page_data = {page: [] for page in target_pages}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('<'):
                continue
            
            # Parse line ID
            match = re.match(r'<([^>]+)>\s+(.*)', line)
            if not match:
                continue
            
            line_id_full = match.group(1)
            content = match.group(2)
            
            # Extract page ID (e.g., f8v from f8v.1,@P0;H)
            page_id_match = re.match(r'([^.]+)', line_id_full)
            if not page_id_match:
                continue
            page_id = page_id_match.group(1)
            
            if page_id not in target_pages:
                continue
                
            # Prefer version H
            if ';H' not in line_id_full:
                # If we already have this line number from H, skip. 
                # If not, and it's another version, maybe take it?
                # For simplicity, let's just take H lines. 
                # If H is missing, we might miss some text, but usually H is present.
                # Let's actually try to be robust: stick to H for consistency.
                continue

            # Clean content
            # Remove comments/tags like <->, <!plant>, {plant}, $
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\{[^}]+\}', '', content)
            content = content.replace('$', '').replace('!', '').replace('?', '').replace(',', '.')
            
            words = [w for w in content.split('.') if w]
            page_data[page_id].extend(words)
            
    return page_data

def is_potential_name(word):
    """Heuristic for identifying potential names."""
    if len(word) < 3:
        return False
    
    # Check prefixes
    for prefix in RECIPE_PREFIXES:
        if word.startswith(prefix):
            return False
            
    # Check if it's a known connector or common verb
    if word in CONNECTORS or word in COMMON_VERBS:
        return False
        
    return True

def analyze_page(words):
    """Analyzes a list of words from a page."""
    analysis = {}
    
    analysis['word_count'] = len(words)
    analysis['connectors'] = Counter([w for w in words if w in CONNECTORS])
    
    potential_names = [w for w in words if is_potential_name(w)]
    analysis['potential_names'] = Counter(potential_names).most_common(10)
    
    # Try to find patterns: Name Connector Name, or Name Verb Name
    patterns = []
    for i in range(len(words) - 2):
        w1, w2, w3 = words[i], words[i+1], words[i+2]
        
        # Pattern 1: Name Connector Name (X and Y)
        if is_potential_name(w1) and w2 in CONNECTORS and is_potential_name(w3):
            patterns.append(f"{w1} {w2} {w3} (Name-Conn-Name)")
            
        # Pattern 2: Name Verb Name (SVO?)
        if is_potential_name(w1) and w2 in COMMON_VERBS and is_potential_name(w3):
             patterns.append(f"{w1} {w2} {w3} (SVO?)")

    analysis['patterns'] = patterns
    
    return analysis

def main():
    print(f"Reading {INPUT_FILE}...")
    data = parse_ivtff(INPUT_FILE, TARGET_PAGES)
    
    full_analysis = {}
    for page in TARGET_PAGES:
        print(f"Analyzing {page}...")
        if not data[page]:
            print(f"Warning: No data found for {page}")
            full_analysis[page] = {'word_count': 0, 'connectors': {}, 'potential_names': [], 'patterns': []}
        else:
            full_analysis[page] = analyze_page(data[page])

    # Generate Output
    print("Generating reports...")
    
    # Detailed Analysis
    with open(OUTPUT_ANALYSIS, 'w') as f:
        f.write("# Narrative Analysis (Track 297)\n\n")
        f.write("Goal: Identify 'Narrative Islands' in low-density pages.\n\n")
        
        for page in TARGET_PAGES:
            stats = full_analysis[page]
            f.write(f"## Page {page}\n")
            f.write(f"- **Word Count:** {stats['word_count']}\n")
            
            f.write("- **Connectors Found:**\n")
            if stats['connectors']:
                for conn, count in stats['connectors'].items():
                    f.write(f"  - `{conn}`: {count}\n")
            else:
                f.write("  - None\n")
                
            f.write("- **Top Potential Names (Non-Recipe Nouns):**\n")
            if stats['potential_names']:
                for name, count in stats['potential_names']:
                    f.write(f"  - `{name}` ({count})\n")
            else:
                f.write("  - None\n")
                
            f.write("- **Narrative Patterns (SVO / Connected Entities):**\n")
            if stats['patterns']:
                for pat in stats['patterns']:
                    f.write(f"  - {pat}\n")
            else:
                f.write("  - None detected with current heuristics.\n")
            f.write("\n")

    # Summary
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("# Track 297 Results Summary: Narrative Search\n\n")
        f.write("## Hypothesis\n")
        f.write("The low-density pages (`f67v2`, `f8v`, `f90r1`) exhibit a different grammatical structure than the recipe sections. ")
        f.write("The presence of connectors and distinct vocabulary suggests a narrative or descriptive content, potentially historical or mythological in nature.\n\n")
        
        f.write("## Key Findings\n")
        for page in TARGET_PAGES:
            stats = full_analysis[page]
            top_names = ", ".join([n[0] for n in stats['potential_names'][:3]])
            f.write(f"- **{page}**: {stats['word_count']} words. Top candidates for proper nouns: {top_names}. ")
            if stats['connectors']:
                conns = ", ".join([f"{k}({v})" for k,v in stats['connectors'].items()])
                f.write(f"Connectors: {conns}.\n")
            else:
                f.write("No standard connectors found.\n")
        
        f.write("\n## Next Steps\n")
        f.write("- Refine 'Name' detection by cross-referencing with high-frequency common words.\n")
        f.write("- Investigate the context of 'Potential Names' in other sections.\n")

    print("Done.")

if __name__ == '__main__':
    main()
