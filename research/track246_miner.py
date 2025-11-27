import json
import re
import os

# Configuration
DICT_PATH = 'results/dictionary/dictionary.json'
DATA_PATH = 'data/eva_ivtff.txt'
OUTPUT_DICT_PATH = 'results/dictionary/dictionary_v11.json'
REPORT_PATH = 'results/track-246-coverage_report.md'

# Folio Ranges
RANGES = {
    'astral': (67, 73),       # Book I
    'plant': (1, 66),         # Book II
    'ingredient': [(75, 84), (103, 116)] # Book III
}

def parse_folio(tag):
    # format <f1r...> or <f103v...>
    m = re.match(r'<f(\d+)', tag)
    if m:
        return int(m.group(1))
    return None

def load_dictionary():
    if not os.path.exists(DICT_PATH):
        print(f"Error: {DICT_PATH} not found.")
        return None
    with open(DICT_PATH, 'r') as f:
        return json.load(f)

def is_known(word, dictionary):
    return word in dictionary.get('entries', {})

def get_candidates():
    candidates = {
        'astral': set(),
        'plant': set(),
        'ingredient': set()
    }
    
    # Pre-compile regex for patterns
    # We need to match sequences in the line.
    # Line format: <tag> word.word.word...
    
    print("Scanning text...")
    
    with open(DATA_PATH, 'r') as f:
        for line in f:
            if not line.startswith('<f'):
                continue
            
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            
            tag = parts[0]
            text = parts[1] # The rest is text, usually no spaces, just dots.
            
            # Filter by transcriber? Let's prefer H (Takahashi)
            # format <f1r.1,@P0;H>
            if ';H>' not in tag:
                # If H is not present, maybe accept others? 
                # For now, let's try to stick to H to avoid duplicates, 
                # unless we want maximum recall. 
                # Let's allow all but maybe dedup by line? 
                # Actually, simple approach: just process all lines. 
                # The 'set' will handle duplicates of the same word.
                pass

            folio = parse_folio(tag)
            if folio is None:
                continue
                
            words = text.split('.')
            # Remove empty strings
            words = [w for w in words if w]
            
            # Track 243: Astral
            if 67 <= folio <= 73:
                for i in range(len(words) - 1):
                    w1 = words[i]
                    w2 = words[i+1]
                    
                    # Patterns: daiin [UNKNOWN], aiin [UNKNOWN], dal [UNKNOWN]
                    if w1 in ['daiin', 'aiin', 'dal']:
                        candidates['astral'].add(w2)
            
            # Track 244: Plant
            if 1 <= folio <= 66:
                # Patterns: [UNKNOWN] otar, [UNKNOWN] oteey
                for i in range(len(words) - 1):
                    w1 = words[i]
                    w2 = words[i+1]
                    if w2 in ['otar', 'oteey']:
                        candidates['plant'].add(w1)
                
                # Pattern: o-[UNKNOWN] (This is prefix, not word sequence)
                # "Prioritize words starting with o- or ch-"
                # The task says "Scan for patterns: o-[UNKNOWN]"
                # This might mean words starting with o-.
                # Let's assume it means "any word starting with o-" in this section is a candidate?
                # That seems too broad. "o-[UNKNOWN]" usually implies `o` is a prefix or a separate particle attached.
                # In EVA, `o` is a letter. `o.word`? or `oword`?
                # "o-matches" usually means words starting with `o`.
                # Task says: "Herbal pages are 'Dry' (o dominant). Unknowns here are likely plants."
                # "Prioritize words starting with o- or ch-".
                # I'll look for words starting with 'o' or 'ch' that are NOT known.
                for w in words:
                    if w.startswith('o') or w.startswith('ch'):
                        candidates['plant'].add(w)

            # Track 245: Ingredient
            # Ranges: 75-84, 103-116
            in_range = (75 <= folio <= 84) or (103 <= folio <= 116)
            if in_range:
                for i in range(len(words) - 1):
                    w1 = words[i]
                    w2 = words[i+1]
                    
                    # Patterns: ol [UNKNOWN], daiin [UNKNOWN]
                    if w1 in ['ol', 'daiin']:
                        candidates['ingredient'].add(w2)
                    
                    # Pattern: [UNKNOWN] chedy
                    if w2 == 'chedy':
                        candidates['ingredient'].add(w1)

    return candidates

def build_dictionary():
    dictionary = load_dictionary()
    if not dictionary:
        return

    # Start fresh lists or use sets
    candidates = get_candidates()
    
    print(f"Found candidates: Astral={len(candidates['astral'])}, Plant={len(candidates['plant'])}, Ingredient={len(candidates['ingredient'])}")

    # Save intermediate mining results
    os.makedirs('results/mining', exist_ok=True)
    for cat, words in candidates.items():
        mining_file = f'results/mining/{cat}_candidates.json'
        with open(mining_file, 'w') as f:
            json.dump(list(words), f, indent=2)
        print(f"Saved {cat} candidates to {mining_file}")
    
    added_count = 0
    skipped_known = 0
    
    for cat, words in candidates.items():
        meaning_map = {
            'astral': 'star_candidate',
            'plant': 'plant_candidate',
            'ingredient': 'ingredient_candidate'
        }
        meaning = meaning_map[cat]
        
        for w in words:
            # Check if known
            if is_known(w, dictionary):
                skipped_known += 1
                continue
            
            # Add new entry
            # Check if we already added it in this run (conflict?)
            # If a word is both plant and ingredient, what do we do?
            # The logic simply adds it. If it exists in 'entries', is_known returns true.
            # But we are modifying 'dictionary' in memory.
            
            # Wait, if I add a plant candidate, then process ingredient, is_known will see it?
            # Yes, if I update dictionary['entries'] immediately.
            
            # However, maybe we want to allow multiple tags?
            # The current dictionary structure shows "meaning": "string".
            # So one meaning.
            # Priority?
            # The task order: Astral (243), Plant (244), Ingredient (245).
            # I'll process them in that order.
            
            entry = {
                "voynich": w,
                "meaning": meaning,
                "confidence": 0.5,
                "source": "Track246_ContextMining",
                "confidence_level": "LOW"
            }
            dictionary['entries'][w] = entry
            added_count += 1

    # Update metadata
    dictionary['version'] = "11.0"
    
    # Save
    print(f"Saving dictionary v11 with {added_count} new entries. Skipped {skipped_known} known words.")
    with open(OUTPUT_DICT_PATH, 'w') as f:
        json.dump(dictionary, f, indent=2)

    # Calculate coverage
    # Coverage = (Known Words / Total Words in Text) * 100 ? 
    # Or (Known Types / Total Types)?
    # Usually coverage refers to token coverage in the text.
    
    # I'll implement a simple token coverage calculator.
    calculate_coverage(dictionary)

def calculate_coverage(dictionary):
    # Simple token coverage on the processed sections or whole text?
    # "Calculate new Coverage Metric (Target: >40%)."
    # Usually refers to the whole corpus or the relevant sections.
    # I'll calculate on the whole file for simplicity, or maybe per section.
    # Let's do whole file.
    
    total_tokens = 0
    known_tokens = 0
    
    known_words = set(dictionary['entries'].keys())
    
    with open(DATA_PATH, 'r') as f:
        for line in f:
            if not line.startswith('<f'): continue
            parts = line.strip().split()
            if len(parts) < 2: continue
            text = parts[1]
            words = text.split('.')
            words = [w for w in words if w]
            
            total_tokens += len(words)
            for w in words:
                if w in known_words:
                    known_tokens += 1
                    
    coverage = (known_tokens / total_tokens) * 100 if total_tokens > 0 else 0
    print(f"Coverage: {coverage:.2f}%")
    
    report = f"""# Track 246 Coverage Report

- **Version**: 11.0
- **Total Tokens**: {total_tokens}
- **Known Tokens**: {known_tokens}
- **Coverage**: {coverage:.2f}%
- **Target**: >40%
- **Status**: {"MET" if coverage > 40 else "MISSED"}
"""
    with open(REPORT_PATH, 'w') as f:
        f.write(report)

if __name__ == "__main__":
    build_dictionary()
