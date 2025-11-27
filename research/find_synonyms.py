import json
import re
import os
from collections import defaultdict, Counter
import difflib

# --- Configuration ---
INPUT_DICT = "results/master_dictionary_v7_4.json"
INPUT_TEXT = "data/eva_ivtff.txt"
OUTPUT_JSON = "results/synonym_candidates.json"
OUTPUT_REPORT = "results/synonym_report.md"

# Transcriber priority: Currier, Takahashi, First Study Group, others
PRIORITY = ['C', 'H', 'F', 'X', 'U'] 

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return set(data['entries'].keys())

def load_text(path):
    """
    Parses IVTFF file.
    Returns a list of words in order.
    """
    lines_by_id = defaultdict(dict)
    
    # Regex to parse line ID and content
    # Example: <f1r.1,@P0;H> text...
    # We want to capture: Page, Line, Transcriber, Text
    # Simplified ID: <(page)(line_info);(transcriber)> or <(page)(line_info)>
    
    pattern = re.compile(r"^<([^>]+)>\s+(.*)$")
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            match = pattern.match(line)
            if match:
                full_id = match.group(1)
                text = match.group(2)
                
                # Parse ID
                parts = full_id.split(';')
                base_id = parts[0]
                transcriber = parts[1] if len(parts) > 1 else '?'
                
                # Clean text (remove formatting chars if any)
                # Keep it simple for now.
                
                lines_by_id[base_id][transcriber] = text

    # Resolve duplicates based on priority
    ordered_text = []
    
    # Sort keys to maintain document order (alphanumeric sort might be needed)
    # Basic sort: f1r, f1v, f2r... 
    # We'll trust the order in the file if we processed line by line? 
    # IVTFF is usually sorted. But we stored in dict.
    # Let's try to preserve order by storing keys in a list as we see them.
    
    # Re-reading to preserve order might be better or just store order.
    pass

    # Let's do a second pass or change structure to:
    # list of (base_id, {transcriber: text})
    
    line_data = []
    seen_ids = set()
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = pattern.match(line)
            if match:
                full_id = match.group(1)
                text = match.group(2)
                parts = full_id.split(';')
                base_id = parts[0]
                transcriber = parts[1] if len(parts) > 1 else '?'
                
                if base_id not in seen_ids:
                    line_data.append({'id': base_id, 'variants': {}})
                    seen_ids.add(base_id)
                
                # Find the dict entry (inefficient for large files, but OK for 50k lines)
                # Optimize: use a dict to map base_id to index
                pass

    # Optimization
    lines_map = {} # base_id -> dict of variants
    lines_order = [] # list of base_ids
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = pattern.match(line)
            if match:
                full_id = match.group(1)
                text = match.group(2)
                parts = full_id.split(';')
                base_id = parts[0]
                transcriber = parts[1] if len(parts) > 1 else '?'
                
                if base_id not in lines_map:
                    lines_map[base_id] = {}
                    lines_order.append(base_id)
                
                lines_map[base_id][transcriber] = text

    # Build final word list
    final_words = []
    
    for base_id in lines_order:
        variants = lines_map[base_id]
        selected_text = ""
        
        # Pick best transcriber
        found = False
        for t in PRIORITY:
            if t in variants:
                selected_text = variants[t]
                found = True
                break
        if not found:
            # Pick any
            if variants:
                selected_text = next(iter(variants.values()))
        
        if not selected_text:
            continue
            
        # Tokenize
        # Split by '.'
        # Remove invalid chars (!, ?, *, %)
        # Handle line continuation if needed? 
        # For now, treat words ending in - as distinct or stripped.
        # Prompt says "daiin" vs "daiiin".
        
        words = selected_text.split('.')
        for w in words:
            w = w.strip()
            # Basic cleaning: remove non-alpha characters except maybe -
            # EVA is mostly a-z0-9.
            # Let's keep it raw but stripped of empty strings
            if w:
                final_words.append(w)
                
    return final_words

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def get_contexts(words, window=1):
    # map word -> list of (prev, next) tuples
    contexts = defaultdict(list)
    for i in range(window, len(words) - window):
        w = words[i]
        prev_w = words[i-1]
        next_w = words[i+1]
        contexts[w].append((prev_w, next_w))
    return contexts

def analyze_synonyms():
    print("Loading dictionary...")
    known_words = load_dictionary(INPUT_DICT)
    print(f"Loaded {len(known_words)} known words.")

    print("Loading text...")
    all_words = load_text(INPUT_TEXT)
    print(f"Loaded {len(all_words)} words from text.")
    
    # Filter unique words
    word_counts = Counter(all_words)
    unique_words = list(word_counts.keys())
    unknown_words = [w for w in unique_words if w not in known_words]
    
    print(f"Found {len(unique_words)} unique words, {len(unknown_words)} unknown.")

    # Build Contexts
    print("Building contexts...")
    word_contexts = get_contexts(all_words)
    
    # Pre-calculate context sets for faster comparison (optional, or just iterate)
    # For slot analysis, we want detailed context overlap.
    
    candidates = []

    # TASK 1: Levenshtein Matching
    print("Running Levenshtein analysis...")
    # Optimization: group by length to avoid comparing all-to-all
    # Only compare unknown word W with known words of length len(W)-1, len(W), len(W)+1
    
    known_by_len = defaultdict(list)
    for w in known_words:
        known_by_len[len(w)].append(w)
        
    for unknown in unknown_words:
        # Skip very short words/noise
        if len(unknown) < 3: 
            continue
            
        possible_matches = []
        # Check lengths +/- 1 and same length
        for l in range(len(unknown)-1, len(unknown)+2):
            possible_matches.extend(known_by_len[l])
            
        for known in possible_matches:
            dist = levenshtein_distance(unknown, known)
            if dist == 1:
                # Found a match. Check context.
                # We define context similarity as sharing at least one (prev, next) frame
                # OR having significant overlap in neighbors.
                
                ctx_u = set(word_contexts[unknown])
                ctx_k = set(word_contexts[known])
                
                common_contexts = ctx_u.intersection(ctx_k)
                
                if common_contexts:
                    candidates.append({
                        "type": "spelling_variant",
                        "word": unknown,
                        "match": known,
                        "distance": dist,
                        "common_contexts": list(common_contexts)[:5], # store first 5 examples
                        "common_count": len(common_contexts),
                        "freq_unknown": word_counts[unknown],
                        "freq_known": word_counts[known]
                    })

    # TASK 2: Slot Analysis (Synonyms)
    print("Running Slot Analysis...")
    # We look for words (unknown OR known) that share contexts with known words.
    # Focus on unknown words that might be synonyms of known words.
    # Or known words that are synonyms of other known words.
    
    # Let's limit to unknown vs known for now, as per "Consolidate dictionary" goal (implied finding new words)
    # Actually, the prompt says "Find words that are interchangeable". 
    # But let's focus on finding mappings for unknown words first to expand coverage.
    
    # Heuristic: if two words share >= 2 identical full contexts (prev, next), they are likely related.
    # Or if they share many left-neighbors AND many right-neighbors.
    
    # For efficiency, let's invert the context map: (prev, next) -> list of words
    context_to_words = defaultdict(list)
    for w, ctx_list in word_contexts.items():
        for ctx in set(ctx_list): # Use set to avoid counting duplicates for the same word
            context_to_words[ctx].append(w)
            
    # Now find pairs of words that appear together in multiple contexts
    pair_counts = defaultdict(int)
    for ctx, w_list in context_to_words.items():
        # w_list contains words that fit in this slot
        if len(w_list) < 2: continue
        
        # Sort to avoid (A,B) and (B,A) duplicates
        w_list = sorted(list(set(w_list))) # Unique words in this slot
        
        for i in range(len(w_list)):
            for j in range(i+1, len(w_list)):
                w1 = w_list[i]
                w2 = w_list[j]
                
                # We are interested if at least one is Known (to anchor the meaning)
                # or if both are unknown (clustering).
                # Let's focus on Unknown <-> Known pairs for the "Synonym" report
                
                w1_known = w1 in known_words
                w2_known = w2 in known_words
                
                if not (w1_known or w2_known):
                    continue # Skip unknown-unknown pairs for now to reduce noise
                
                pair_counts[(w1, w2)] += 1
                
    # Filter pairs with high overlap
    for (w1, w2), count in pair_counts.items():
        if count >= 3: # Threshold: share at least 3 distinct contexts
             # Check Levenshtein to distinguish variant vs synonym
             dist = levenshtein_distance(w1, w2)
             cat = "synonym" if dist > 1 else "spelling_variant_high_conf"
             
             candidates.append({
                 "type": cat,
                 "word": w1,
                 "match": w2,
                 "distance": dist,
                 "common_count": count,
                 "freq_w1": word_counts[w1],
                 "freq_w2": word_counts[w2]
             })

    # Deduplicate candidates
    # A candidate might appear in both tasks
    unique_candidates = {}
    for c in candidates:
        key = tuple(sorted((c['word'], c['match'])))
        if key in unique_candidates:
            # update if better info?
            pass
        else:
            unique_candidates[key] = c
            
    final_list = list(unique_candidates.values())
    
    # Sort by common_count descending
    final_list.sort(key=lambda x: x.get('common_count', 0), reverse=True)

    # Output JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(final_list, f, indent=2)
        
    # Output Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Synonym & Variant Candidates Report\n\n")
        f.write(f"Total candidates found: {len(final_list)}\n\n")
        
        f.write("## Top Candidates (Context > 5)\n")
        f.write("| Word 1 | Word 2 | Type | Dist | Shared Contexts | Freq 1 | Freq 2 |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        
        for c in final_list:
            if c.get('common_count', 0) > 5:
                w1 = c['word']
                w2 = c['match']
                f.write(f"| {w1} | {w2} | {c['type']} | {c['distance']} | {c.get('common_count', 0)} | {c['freq_w1'] if 'freq_w1' in c else c['freq_unknown']} | {c['freq_w2'] if 'freq_w2' in c else c['freq_known']} |\n")

        f.write("\n## Levenshtein Variants (Dist=1, Context >= 1)\n")
        for c in final_list:
            if c['type'] == 'spelling_variant' and c.get('common_count', 0) <= 5:
                w1 = c['word']
                w2 = c['match']
                 # Use freq keys correctly based on type
                f1 = c.get('freq_w1', c.get('freq_unknown', 0))
                f2 = c.get('freq_w2', c.get('freq_known', 0))
                
                f.write(f"- **{w1}** ({f1}) ~ **{w2}** ({f2}) [Contexts: {c.get('common_count', 0)}]\n")
                if 'common_contexts' in c:
                    for ctx in c['common_contexts']:
                        f.write(f"  - `... {ctx[0]} _ {ctx[1]} ...`\n")

if __name__ == "__main__":
    analyze_synonyms()
