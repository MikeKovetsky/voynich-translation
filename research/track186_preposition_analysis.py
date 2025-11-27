import json
import re
import os
from collections import Counter

def load_json(path):
    print(f"Loading {path}...")
    with open(path, 'r') as f:
        return json.load(f)

def load_text(path):
    print(f"Loading {path}...")
    with open(path, 'r') as f:
        return f.readlines()

def main():
    parsed_text = load_json('results/parsed_text.json')
    tagged_lines = load_text('results/tagged_text.txt')

    # Get unique words from parsed_text
    unique_words = set(item.get('original', '') for item in parsed_text if item.get('original'))
    print(f"Loaded {len(unique_words)} unique words.")
    
    prefixes = ['ot', 'ok', 'or', 'op', 'ol']
    target_words = {p: [] for p in prefixes}
    
    # Find words starting with prefixes
    for word in unique_words:
        for p in prefixes:
            # We want words that definitely have the prefix + something else
            if word.startswith(p) and len(word) > len(p):
                target_words[p].append(word)
    
    for p in prefixes:
        print(f"Found {len(target_words[p])} words starting with {p}-")

    # 1. Context Analysis: Select sentences (lines) containing these prefixes
    print("Analyzing context...")
    
    clean_lines = []
    for line in tagged_lines:
        if line.startswith('#'): continue
        # Remove tags like ROOT:, CONJ:
        # Also remove line ID which is usually the first token but looks like text
        # Line format: ROOT:f1r1P0H ROOT:fa ...
        
        parts = line.strip().split()
        if not parts: continue
        
        # Remove tags
        clean_parts = []
        for part in parts:
            if ':' in part:
                clean_parts.append(part.split(':', 1)[1])
            else:
                clean_parts.append(part)
        
        # Skip line ID if it looks like a file ID (f\d+[rv]...)
        if clean_parts and re.match(r'f\d+[rv]', clean_parts[0]):
            clean_parts = clean_parts[1:]
            
        if clean_parts:
            clean_lines.append(clean_parts)

    # Analyze position
    position_stats = {p: {'start': 0, 'total': 0} for p in prefixes}
    examples = []
    found_count = 0
    
    # We want to find where our target words appear
    # But wait, target_words are from parsed_text.json which might be different tokenization than tagged_text.txt
    # Let's assume similar enough.
    
    target_set = set()
    for p in prefixes:
        for w in target_words[p]:
            target_set.add(w)
            
    for line_tokens in clean_lines:
        for i, word in enumerate(line_tokens):
            # Check if word starts with prefix
            matched_prefix = None
            for p in prefixes:
                if word.startswith(p) and len(word) > len(p):
                    matched_prefix = p
                    break
            
            if matched_prefix:
                position_stats[matched_prefix]['total'] += 1
                if i == 0:
                    position_stats[matched_prefix]['start'] += 1
                
                if found_count < 50:
                    examples.append({
                        'prefix': matched_prefix,
                        'word': word,
                        'line': ' '.join(line_tokens),
                        'position': 'Start' if i == 0 else 'Middle'
                    })
                    found_count += 1

    # 2. Contrast Pairs
    print("Finding contrast pairs...")
    contrast_pairs = {p: [] for p in prefixes}
    
    for p in prefixes:
        for word in target_words[p]:
            root = word[len(p):]
            if root in unique_words:
                contrast_pairs[p].append((word, root))

    # Generate Report
    print("Generating reports...")
    with open('results/grammar_cases.md', 'w') as f:
        f.write("# Grammar Case Analysis: `o-` Prefixes\n\n")
        
        f.write("## 1. Context Analysis\n")
        f.write("### Position Statistics (Start of Phrase)\n")
        f.write("| Prefix | Total Occurrences | Start of Phrase | % Start |\n")
        f.write("|---|---|---|---|\n")
        for p in prefixes:
            stats = position_stats[p]
            pct = (stats['start'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"| `{p}-` | {stats['total']} | {stats['start']} | {pct:.1f}% |\n")
        
        f.write("\n### Sample Sentences\n")
        for ex in examples:
            f.write(f"- **{ex['word']}**: `{ex['line']}` ({ex['position']})\n")

        f.write("\n## 2. Contrast Pairs\n")
        f.write("Pairs where `Prefix+Root` and `Root` both exist as independent words.\n\n")
        
        for p in prefixes:
            f.write(f"### Prefix `{p}-` ({len(contrast_pairs[p])} pairs)\n")
            pairs = sorted(contrast_pairs[p], key=lambda x: len(x[1]))[:20] # Shortest roots first
            for word, root in pairs:
                f.write(f"- `{word}` vs `{root}`\n")
            f.write("\n")

        f.write("## 3. Hypothesis Mapping\n")
        f.write("### Proposed Mapping Evaluation\n")
        
        # Simple heuristic evaluation
        f.write("| Prefix | Hypothesis | Observation | Fit? |\n")
        f.write("|---|---|---|---|\n")
        
        # ol = The (Definite). Should be high freq, potentially start of noun phrases.
        ol_stats = position_stats['ol']
        ol_pct = (ol_stats['start'] / ol_stats['total'] * 100) if ol_stats['total'] else 0
        ol_fit = "Possible" if ol_pct > 10 else "Unlikely (Low start freq)"
        f.write(f"| `ol-` | Nominative/Definite | Start Freq: {ol_pct:.1f}% | {ol_fit} |\n")
        
        # ot = From (Ablative). 
        ot_stats = position_stats['ot']
        ot_pct = (ot_stats['start'] / ot_stats['total'] * 100) if ot_stats['total'] else 0
        ot_fit = "Likely" if ot_pct > 20 else "Unclear"
        f.write(f"| `ot-` | Ablative/Origin | Start Freq: {ot_pct:.1f}% | {ot_fit} |\n")

        # or = To/For (Dative).
        or_stats = position_stats['or']
        or_pct = (or_stats['start'] / or_stats['total'] * 100) if or_stats['total'] else 0
        f.write(f"| `or-` | Dative/Benefactive | Start Freq: {or_pct:.1f}% | - |\n")

        # ok = With (Instrumental).
        ok_stats = position_stats['ok']
        ok_pct = (ok_stats['start'] / ok_stats['total'] * 100) if ok_stats['total'] else 0
        f.write(f"| `ok-` | Instrumental | Start Freq: {ok_pct:.1f}% | - |\n")
        
    # Summary
    with open('results/track-186-results_summary.md', 'w') as f:
        f.write("# Track 186 Results Summary\n\n")
        f.write("## Goal\nRe-evaluate `o-` prefixed words as Case Markers or Prepositions.\n\n")
        f.write("## Key Findings\n")
        
        top_p = max(prefixes, key=lambda x: position_stats[x]['total'])
        f.write(f"- Most frequent prefix: `{top_p}-` ({position_stats[top_p]['total']} occurrences).\n")
        
        start_heavy = [p for p in prefixes if position_stats[p]['total'] > 0 and (position_stats[p]['start']/position_stats[p]['total']) > 0.25]
        if start_heavy:
            f.write(f"- Prefixes appearing frequently at start of phrases (>25%): {', '.join([f'`{p}-`' for p in start_heavy])}.\n")
        else:
            f.write("- No prefixes appear predominantly at the start of phrases.\n")
            
        f.write(f"- Contrast pairs identified: {sum(len(contrast_pairs[p]) for p in prefixes)} total pairs.\n")
        f.write("\n## Recommendation\n")
        if 'ol' in start_heavy:
            f.write("- `ol-` is a strong candidate for a sentence-initial marker (Definite/Nominative).\n")
        else:
            f.write("- `ol-` does not show strong sentence-initial bias.\n")
            
        f.write("\nSee `results/grammar_cases.md` for full details.\n")

if __name__ == "__main__":
    main()
