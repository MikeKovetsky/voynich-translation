import json
import re
from collections import defaultdict, Counter
import os

# Paths
DATA_PATH = 'data/eva_ivtff.txt'
DICT_PATH = 'results/dictionary/master_dictionary_v18.json'
OUTPUT_PATH = 'results/plant_recipe_match_report.md'

# Medieval Herb DB (Simple approximation for matching logic)
MEDIEVAL_HERBS = {
    "Betony": {"actions": ["boil", "drink"], "context": ["liquid", "water", "march"]},
    "Sage": {"actions": ["grind", "eat"], "context": ["solid"]},
    "Rue": {"actions": ["mix", "drink"], "context": ["liquid"]},
    "Mugwort": {"actions": ["boil", "wash"], "context": ["water", "liquid"]},
    "Fennel": {"actions": ["boil", "drink"], "context": ["liquid"]},
    "Mint": {"actions": ["grind", "mix"], "context": ["solid"]},
    "Plantain": {"actions": ["grind", "wash"], "context": ["water"]},
    "Vervain": {"actions": ["boil", "mix"], "context": ["wine", "liquid"]},
    "Spinach": {"actions": ["boil", "eat"], "context": ["liquid", "water"]},
    "Roots": {"actions": ["grind", "eat"], "context": ["solid"]},
    "Spices": {"actions": ["grind", "mix"], "context": ["solid"]}
}

# Voynich Mappings based on task description and common findings
ACTIONS = {
    "qokeey": "boil",
    "chedy": "drink",
    "saiin": "wash",
    "chdy": "eat",
    "sal": "grind",
    "ok": "mix" 
}

CONTEXTS = {
    "ol": "liquid",
    "aiin": "water",
    "dar": "march", 
    "dal": "aries",
}

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def load_text(path):
    with open(path, 'r') as f:
        return f.read()

def get_plant_candidates(dictionary):
    candidates = set()
    for word, data in dictionary['entries'].items():
        meaning = data.get('meaning', '').lower()
        # Filter out obviously non-Voynich keys if any, but mainly check meaning
        # Also exclude words that are themselves actions or contexts to avoid self-matching
        # Filter out 'plant' specifically as it seems to be an artifact
        if word == 'plant' or len(word) < 2:
            continue
            
        if ('plant' in meaning or 'herb' in meaning or 'ingredient' in meaning or 'leaf' in meaning) and \
           word not in ACTIONS and word not in CONTEXTS:
            candidates.add(word)
    return candidates

def analyze_recipes(text, candidates):
    lines = text.split('\n')
    
    # Store signatures: word -> counter of features
    signatures = defaultdict(Counter)
    
    # Simple window-based context analysis
    WINDOW_SIZE = 5
    
    for line in lines:
        if line.strip().startswith('#'):
            continue
        
        # Filter for a specific transcription to avoid duplication (e.g., ;H>)
        if ';H>' not in line and ';C>' not in line: 
             if not re.search(r'<f\d+[rv]\.', line):
                 continue

        # Extract text part
        parts = line.strip().split()
        if len(parts) < 2:
            continue
            
        # The text is usually the last part or after the ID
        content = " ".join(parts[1:])
        
        # Replace dots with spaces
        content = content.replace('.', ' ')
        
        # Remove weird characters and split
        words = content.split()
        
        for i, word in enumerate(words):
            # Clean word (remove punctuation like !, -, etc)
            clean_word = re.sub(r'[^\w]', '', word)
            
            if clean_word in candidates:
                # Look around
                start = max(0, i - WINDOW_SIZE)
                end = min(len(words), i + WINDOW_SIZE + 1)
                context_window = words[start:end]
                
                for cw in context_window:
                    cw_clean = re.sub(r'[^\w]', '', cw)
                    
                    # Check actions
                    if cw_clean in ACTIONS:
                        signatures[clean_word][ACTIONS[cw_clean]] += 1
                        
                    # Check contexts
                    if cw_clean in CONTEXTS:
                        signatures[clean_word][CONTEXTS[cw_clean]] += 1
                        
    return signatures

def match_candidates(signatures):
    matches = []
    
    for word, sig in signatures.items():
        total_actions = sum(sig.values())
        if total_actions < 3: # Back to 3 to ensure quality
            continue
            
        # Normalize signature to top features
        top_features = [k for k, v in sig.most_common(3)]
        
        best_match = "Unknown"
        max_score = 0
        
        for herb, profile in MEDIEVAL_HERBS.items():
            score = 0
            for feature in top_features:
                if feature in profile['actions'] or feature in profile['context']:
                    score += 1
            
            if score > max_score:
                max_score = score
                best_match = herb
        
        matches.append({
            "word": word,
            "signature": dict(sig),
            "proposed_match": best_match if max_score > 0 else "None",
            "score": max_score
        })
        
    # Sort by total evidence
    matches.sort(key=lambda x: sum(x['signature'].values()), reverse=True)
    return matches

def generate_report(matches):
    lines = []
    lines.append("# Plant Recipe Match Report")
    lines.append("## Top Plant Candidates by Process Profile\n")
    lines.append("| Candidate (Voynich) | Top Actions/Context | Proposed Medieval Match | Confidence Score |")
    lines.append("|---|---|---|---|")
    
    for m in matches[:20]: # Top 20
        sig_str = ", ".join([f"{k}({v})" for k, v in Counter(m['signature']).most_common(3)])
        lines.append(f"| `{m['word']}` | {sig_str} | **{m['proposed_match']}** | {m['score']} |")
        
    lines.append("\n## Detailed Analysis\n")
    for m in matches[:10]:
        lines.append(f"### Candidate: `{m['word']}`")
        lines.append(f"- **Proposed Match:** {m['proposed_match']}")
        lines.append(f"- **Full Signature:** {m['signature']}")
        lines.append(f"- **Reasoning:** Matches typical profile of {m['proposed_match']} (e.g., usage in {', '.join(list(m['signature'].keys())[:2])}).\n")
        
    with open(OUTPUT_PATH, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Report generated at {OUTPUT_PATH}")

def main():
    print("Loading dictionary...")
    dictionary = load_json(DICT_PATH)
    candidates = get_plant_candidates(dictionary)
    print(f"Found {len(candidates)} plant/ingredient candidates.")
    
    print("Loading text...")
    text = load_text(DATA_PATH)
    
    print("Analyzing recipes...")
    signatures = analyze_recipes(text, candidates)
    
    print("Matching candidates...")
    matches = match_candidates(signatures)
    
    print("Generating report...")
    generate_report(matches)
    print("Done.")

if __name__ == "__main__":
    main()
