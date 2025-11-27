import json
import re
import csv
from collections import Counter, defaultdict
import os

# Paths
DICT_PATH = 'results/master_dictionary_v7.json'
TRANSCRIPTION_PATH = 'data/eva_ivtff.txt'
QUIRE20_PATH = 'results/quire20_translation_final.md'
OUTPUT_REPORT = 'results/coverage_gap_report.md'
OUTPUT_CSV = 'results/top_500_unknowns.csv'

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('entries', {})

def is_generic_meaning(meaning):
    meaning = meaning.lower()
    generics = ['plant_name', 'plant_term', 'unknown', 'candidate', 'placeholder', '[plant name]']
    if any(g in meaning for g in generics):
        return True
    if meaning.startswith('[') and meaning.endswith(']'):
        return True
    return False

def parse_transcription(path):
    # Prefer 'H' (Takahashi) > 'U' > 'C' > first available
    # Store lines by ID
    lines_by_id = defaultdict(dict)
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            
            # Format: <f103r.1,@P0;H> text
            match = re.match(r'<([^>]+)>\s+(.*)', line)
            if match:
                meta = match.group(1)
                text = match.group(2).strip()
                
                # Meta format: f103r.1,@P0;H or f103r.1;H
                # Extract ID (f103r.1) and Transcriber (H)
                parts = meta.split(';')
                if len(parts) == 2:
                    transcriber = parts[1]
                    # ID is complicated, sometimes contains comma. 
                    # We want the line reference: f103r.1
                    # meta usually: page.line,attribs;transcriber
                    # Let's take the part before the first comma or semicolon as the line ID?
                    # Actually, just use the full base ID.
                    # <f103r.1,@P0;H> -> id="f103r.1", transcriber="H"
                    
                    id_part = parts[0]
                    if ',' in id_part:
                        line_id = id_part.split(',')[0]
                    else:
                        line_id = id_part
                    
                    lines_by_id[line_id][transcriber] = text

    # Select best transcription for each line
    final_lines = []
    preferred_order = ['H', 'U', 'C', 'F', 'm']
    
    sorted_ids = sorted(lines_by_id.keys()) # Sort just for stability
    # To sort correctly (numerically/alphanumerically), we might need better sort, 
    # but for frequency analysis, order doesn't matter. For context, we might want page order.
    
    token_counts = Counter()
    corpus_lines = [] # (line_id, text)

    for line_id in sorted_ids:
        versions = lines_by_id[line_id]
        selected_text = ""
        for t in preferred_order:
            if t in versions:
                selected_text = versions[t]
                break
        if not selected_text and versions:
            selected_text = next(iter(versions.values()))
            
        if selected_text:
            # Clean text: remove comments or weird markers if any?
            # EVA uses dots for spaces.
            # Remove -? ? * ! etc if they are not part of words?
            # Standard EVA is a-z, A-Z, 0-9, punctuation.
            # Usually words are separated by dots.
            words = selected_text.replace('.', ' ').split()
            clean_words = [w for w in words if w and w not in ['-', '=', '?']]
            
            for w in clean_words:
                # Strip non-word chars? EVA words can contain strange chars? 
                # Let's keep alphanumeric for now.
                w_clean = re.sub(r'[^a-zA-Z0-9]', '', w)
                if w_clean:
                    token_counts[w_clean] += 1
            
            corpus_lines.append((line_id, selected_text))

    return token_counts, corpus_lines

def analyze_quire20(path):
    # Read file
    with open(path, 'r') as f:
        content = f.read()
    
    # Extract lines with bullet points which seem to be the translation lines
    # "- `g1c8ae` ..."
    translation_lines = [line for line in content.split('\n') if line.strip().startswith('- `')]
    
    stats = {
        'placeholders': 0,
        'untranslated': 0,
        'translated': 0,
        'total': 0
    }
    
    # Regex for tokens: 
    # Untranslated: `token`
    # Placeholder: [PLANT NAME], plant_candidate, unknown_object
    # Translated: plain text words (excluding common structural words if needed, but usually everything else is "translated")
    
    # Actually, the format is:
    # - `token` `token` Translation `token` ...
    # So we can split by spaces, but some translations have spaces "Green (Leaf)".
    # We need to tokenize carefully.
    
    # Strategy:
    # Find all backticked tokens -> Untranslated
    # Remove them.
    # Find all placeholders (known list or pattern).
    # The rest is Translated.
    
    # Placeholder patterns
    placeholder_patterns = [
        r'\[.*?\]', # [PLANT NAME]
        r'plant_\w+', # plant_candidate, plant_term
        r'unknown_\w+' # unknown_object
    ]
    
    for line in translation_lines:
        # Remove the leading "- "
        line_content = line.strip()[2:]
        
        # Find backticked tokens
        untranslated_matches = re.findall(r'`([^`]+)`', line_content)
        stats['untranslated'] += len(untranslated_matches)
        stats['total'] += len(untranslated_matches)
        
        # Remove backticked parts to analyze the rest
        rest = re.sub(r'`[^`]+`', '', line_content)
        
        # Find placeholders
        placeholders_found = 0
        for pat in placeholder_patterns:
            matches = re.findall(pat, rest, re.IGNORECASE)
            placeholders_found += len(matches)
            rest = re.sub(pat, '', rest, flags=re.IGNORECASE) # Remove found
        
        stats['placeholders'] += placeholders_found
        stats['total'] += placeholders_found
        
        # Count remaining words as translated
        # Clean up extra spaces and punctuation
        rest = re.sub(r'[(),]', ' ', rest)
        remaining_tokens = [t for t in rest.split() if t.strip()]
        
        stats['translated'] += len(remaining_tokens)
        stats['total'] += len(remaining_tokens)
        
    return stats

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary(DICT_PATH)
    known_specific = set()
    known_generic = set()
    
    for word, entry in dictionary.items():
        if is_generic_meaning(entry.get('meaning', '')):
            known_generic.add(word)
        else:
            known_specific.add(word)
            
    print(f"Dictionary: {len(known_specific)} specific, {len(known_generic)} generic.")

    print("Parsing transcription...")
    token_counts, corpus_lines = parse_transcription(TRANSCRIPTION_PATH)
    print(f"Total unique tokens: {len(token_counts)}")
    
    # Identify Top 500 Unknown/Generic
    # Criteria: Not in known_specific.
    # (If it's in known_generic, it's a target. If it's not in dict, it's a target.)
    
    hit_list_candidates = []
    for word, count in token_counts.items():
        if word not in known_specific:
            status = "Generic" if word in known_generic else "Unknown"
            hit_list_candidates.append({
                'word': word,
                'count': count,
                'status': status
            })
            
    # Sort by count desc
    hit_list_candidates.sort(key=lambda x: x['count'], reverse=True)
    top_500 = hit_list_candidates[:500]
    
    # Context Extraction for Top 20
    top_20 = top_500[:20]
    context_map = {}
    
    for item in top_20:
        word = item['word']
        examples = []
        # Scan corpus for examples
        # Ideally we want diverse examples.
        count_found = 0
        for line_id, text in corpus_lines:
            # Check if word is in line (simple check, improve if needed)
            if word in text.replace('.', ' ').split():
                examples.append(f"[{line_id}] {text}")
                count_found += 1
                if count_found >= 3:
                    break
        context_map[word] = examples

    # Analyze Quire 20 Coverage
    print("Analyzing Quire 20...")
    q20_stats = analyze_quire20(QUIRE20_PATH)
    
    # Generate Reports
    print("Generating outputs...")
    
    # CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['word', 'count', 'status'])
        writer.writeheader()
        writer.writerows(top_500)
        
    # Markdown Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Coverage Gap Report\n\n")
        
        f.write("## 1. Quire 20 Coverage Analysis\n")
        total = q20_stats['total']
        if total > 0:
            p_untrans = (q20_stats['untranslated'] / total) * 100
            p_place = (q20_stats['placeholders'] / total) * 100
            p_trans = (q20_stats['translated'] / total) * 100
            
            f.write(f"- **Total Tokens:** {total}\n")
            f.write(f"- **Untranslated (Raw):** {q20_stats['untranslated']} ({p_untrans:.2f}%)\n")
            f.write(f"- **Generic Placeholders:** {q20_stats['placeholders']} ({p_place:.2f}%)\n")
            f.write(f"- **Fully Translated:** {q20_stats['translated']} ({p_trans:.2f}%)\n")
            f.write("\n**Note:** 'Generic Placeholders' includes `[PLANT NAME]`, `plant_candidate`, etc.\n")
        else:
            f.write("No tokens found in Quire 20 analysis.\n")
            
        f.write("\n## 2. The Hit List (Top Unknowns)\n")
        f.write("Top 20 most frequent Unknown/Generic words from the corpus:\n\n")
        
        for item in top_20:
            word = item['word']
            count = item['count']
            status = item['status']
            f.write(f"### {word} ({count} occurrences) - {status}\n")
            examples = context_map.get(word, [])
            for ex in examples:
                f.write(f"- `{ex}`\n")
            f.write("\n")
            
        f.write(f"\nFull list of Top 500 available in `{OUTPUT_CSV}`.\n")

if __name__ == "__main__":
    main()
