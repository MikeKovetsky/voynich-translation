import re
import json
from collections import Counter, defaultdict

INPUT_FILE = "data/eva_ivtff.txt"
OUTPUT_RULES = "results/morphology_rules.json"
OUTPUT_MAPPING = "results/root_mapping.json"
OUTPUT_REPORT = "results/coverage_report.md"

TARGET_PREFIXES = ['qo', 'y', 'o']
TARGET_SUFFIXES = ['dy', 'ol', 'y']

def load_words(filepath):
    print(f"Loading words from {filepath}...")
    words = Counter()
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            # Extract text part. Format: <id> \t text
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            text = parts[1].strip()
            
            # Clean text
            # Remove punctuation and split
            # Keeping it simple for EVA: lowercase a-z, numbers, ? ! 
            # But we want to split on . and , and - and = and spaces
            tokens = re.split(r'[.,\-= \t]+', text)
            
            for token in tokens:
                token = token.strip('!?*') # Strip special transcription chars
                if not token:
                    continue
                # Only keep token if it looks like a word (mostly letters)
                # EVA uses a-z, 0-9.
                if re.match(r'^[a-z0-9]+$', token):
                    words[token] += 1
    print(f"Found {len(words)} unique words.")
    return words

def find_affixes(words):
    # Calculate frequency of start/end sequences
    prefix_counts = Counter()
    suffix_counts = Counter()
    
    total_tokens = sum(words.values())
    
    for word, count in words.items():
        # Prefixes length 1-3
        for i in range(1, 4):
            if len(word) > i:
                prefix = word[:i]
                prefix_counts[prefix] += count
        
        # Suffixes length 1-3
        for i in range(1, 4):
            if len(word) > i:
                suffix = word[-i:]
                suffix_counts[suffix] += count
                
    return prefix_counts, suffix_counts

def consolidate_roots(words, prefixes, suffixes):
    mapping = {} # derived -> root
    
    # Sort affixes by length descending to match longest first? 
    # Or just apply iteratively. 
    # Task says targets: `qo-`, `y-`, `o-`, `-dy`, `-ol`, `-y`.
    # I will attempt to strip these.
    
    # Recursive or single pass?
    # Example: ychol -> chol.
    # cholody -> chol. (strip ody? or dy then o?)
    # If I strip 'dy', I get 'cholo'. 'cholo' might strip 'o' -> 'chol'.
    # So iterative stripping seems appropriate.
    
    # We need to decide order: prefix then suffix? or both?
    # Let's try to find the "minimal" root by iteratively stripping known affixes
    # until no more can be stripped OR the remaining part is too short (e.g. < 2 chars).
    
    sorted_prefixes = sorted(prefixes, key=len, reverse=True)
    sorted_suffixes = sorted(suffixes, key=len, reverse=True)
    
    for word in words:
        original = word
        current = word
        changed = True
        
        while changed:
            changed = False
            
            # Try prefixes
            for p in sorted_prefixes:
                if current.startswith(p) and len(current) > len(p) + 1: # Ensure root has some length
                    current = current[len(p):]
                    changed = True
                    break # Restart loop to handle multiple/order
            
            if changed: continue

            # Try suffixes
            for s in sorted_suffixes:
                if current.endswith(s) and len(current) > len(s) + 1:
                    current = current[:-len(s)]
                    changed = True
                    break
        
        if current != original:
            mapping[original] = current
            
    return mapping

def generate_report(words, mapping, prefix_stats, suffix_stats):
    # Coverage logic:
    # Known words: words that exist in the corpus.
    # Unknown words: conceptually, we are reducing vocabulary.
    # But the task asks: "Count how many 'unknown' words in our dictionary can be reduced to 'known' roots"
    # Assuming "dictionary" = set of all types observed.
    # "Unknown" here likely means "derived forms that we treat as separate words".
    # "Known roots" = roots that actually exist as standalone words in the corpus.
    
    total_tokens = sum(words.values())
    total_types = len(words)
    
    mapped_types = len(mapping)
    
    # How many derived words map to a root that exists in the corpus?
    valid_root_mappings = 0
    valid_root_tokens = 0
    
    # How many derived words map to a root that DOES NOT exist (virtual)?
    virtual_root_mappings = 0
    
    roots_found = set(mapping.values())
    existing_words = set(words.keys())
    
    for derived, root in mapping.items():
        if root in existing_words:
            valid_root_mappings += 1
            valid_root_tokens += words[derived]
        else:
            virtual_root_mappings += 1
            
    lines = []
    lines.append("# Morphology Coverage Report")
    lines.append(f"Total Word Types: {total_types}")
    lines.append(f"Total Word Tokens: {total_tokens}")
    lines.append("")
    lines.append("## Affix Statistics")
    lines.append("### Top Prefixes (Detected)")
    for p, c in prefix_stats.most_common(10):
        lines.append(f"- `{p}-`: {c}")
    lines.append("")
    lines.append("### Top Suffixes (Detected)")
    for s, c in suffix_stats.most_common(10):
        lines.append(f"- `-{s}`: {c}")
    lines.append("")
    lines.append("## Segmentation Results")
    lines.append(f"Words reduced to roots: {mapped_types} ({mapped_types/total_types*100:.1f}%)")
    lines.append(f"Mappings to EXISTING roots: {valid_root_mappings} types")
    lines.append(f"Mappings to VIRTUAL roots: {virtual_root_mappings} types")
    lines.append(f"Token coverage increase: {valid_root_tokens} tokens ({(valid_root_tokens/total_tokens)*100:.1f}%)")
    lines.append("")
    lines.append("## Sample Mappings")
    
    # Show some examples
    examples = list(mapping.items())[:20]
    for d, r in examples:
        lines.append(f"- `{d}` -> `{r}`")
        
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(lines))
        
    # Save rules
    rules = {
        "prefixes": TARGET_PREFIXES,
        "suffixes": TARGET_SUFFIXES,
        "top_detected_prefixes": [p for p, c in prefix_stats.most_common(10)],
        "top_detected_suffixes": [s for s, c in suffix_stats.most_common(10)]
    }
    with open(OUTPUT_RULES, 'w') as f:
        json.dump(rules, f, indent=2)

    # Save mapping
    with open(OUTPUT_MAPPING, 'w') as f:
        json.dump(mapping, f, indent=2)

def main():
    words = load_words(INPUT_FILE)
    prefix_stats, suffix_stats = find_affixes(words)
    
    # We use the TARGET lists for the actual mapping as per instructions, 
    # but we report on what we found.
    mapping = consolidate_roots(words, TARGET_PREFIXES, TARGET_SUFFIXES)
    
    generate_report(words, mapping, prefix_stats, suffix_stats)
    print("Done.")

if __name__ == "__main__":
    main()

