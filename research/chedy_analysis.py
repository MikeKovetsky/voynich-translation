import re
from collections import Counter
from pathlib import Path
import json

EVA_FILE = Path("data/eva_ivtff.txt")

# Folio ranges
RECIPE_FOLIOS = [f'f{i}r' for i in range(103, 117)] + [f'f{i}v' for i in range(103, 117)]
HERBAL_FOLIOS = [f'f{i}r' for i in range(1, 58)] + [f'f{i}v' for i in range(1, 58)]

def load_data(transcriber='H'):
    """
    Parses EVA file, preserving paragraph (@P) and label (@L) attributes.
    Returns:
        dict: { folio: [ { 'type': 'P'|'L', 'id': 'P0', 'text': '...' }, ... ] }
    """
    if not EVA_FILE.exists():
        raise FileNotFoundError(f"{EVA_FILE} not found")
        
    folios = {}
    
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            m = re.match(r'<([^.]+)\.([^,]+),([@+])([^;]+);(\w)>\s*(.+)', line)
            if not m:
                 continue

            folio, line_num, attr_type_char, attr_id, trans, text = m.groups()
            
            if trans != transcriber:
                continue
                
            text = re.sub(r'\{[^}]*\}', '', text)
            
            if folio not in folios:
                folios[folio] = {}
            
            if attr_id not in folios[folio]:
                folios[folio][attr_id] = {
                    'type': 'L' if 'L' in attr_id else 'P',
                    'lines': []
                }
            
            folios[folio][attr_id]['lines'].append(text)

    consolidated = {}
    for folio, units in folios.items():
        consolidated[folio] = []
        for unit_id, data in units.items():
            full_text = " ".join(data['lines'])
            consolidated[folio].append({
                'id': unit_id,
                'type': data['type'],
                'text': full_text
            })
            
    return consolidated

def get_words(text):
    """Split text into words, handling dots and cleanup."""
    text = re.sub(r'[!?,]', '', text)
    raw_words = re.split(r'[.\s]+', text)
    return [w for w in raw_words if w and not w.startswith('%') and not w.startswith('<')]

def analyze_chedy():
    data = load_data()
    print(f"Loaded data for {len(data)} folios.")
    
    # --- Analysis 1: Recipe Distribution ---
    all_recipe_text = ""
    recipe_words_for_bigrams = []
    
    for folio in RECIPE_FOLIOS:
        if folio in data:
            for unit in data[folio]:
                if unit['type'] == 'P':
                    all_recipe_text += " " + unit['text']
                    recipe_words_for_bigrams.extend(get_words(unit['text']))

    words = get_words(all_recipe_text)
    
    start_markers = ['daiin', 'pchedal', 'dain'] 
    
    recipe_starts = 0
    chedy_at_end_of_prev = 0
    pre_marker_words = []
    
    for i, w in enumerate(words):
        # Check if w is a start marker
        if w in start_markers:
             recipe_starts += 1
             if i > 0:
                 prev = words[i-1]
                 pre_marker_words.append(prev)
                 if 'chedy' in prev or 'shedy' in prev:
                     chedy_at_end_of_prev += 1
    
    # Also check last word of the whole stream
    if words:
        pre_marker_words.append(words[-1])
        if 'chedy' in words[-1]:
            chedy_at_end_of_prev += 1
            
    end_word_dist = Counter(pre_marker_words)
                    
    # --- Analysis 2: Herbal Labels ---
    label_hits = []
    for folio in HERBAL_FOLIOS:
        if folio in data:
            for unit in data[folio]:
                if unit['type'] == 'L' or 'L' in unit['id']:
                    wds = get_words(unit['text'])
                    # Check exactly for chedy or variants
                    for w in wds:
                        if 'chedy' in w or 'shedy' in w:
                             label_hits.append(f"{folio}:{unit['id']} -> {w}")

    # --- Analysis 3: Bigrams ---
    bigrams = Counter()
    for i in range(len(recipe_words_for_bigrams) - 1):
        w1 = recipe_words_for_bigrams[i]
        w2 = recipe_words_for_bigrams[i+1]
        if 'chedy' in w2 or 'shedy' in w2: # Preceding
            bigrams[f"{w1} {w2}"] += 1
        if 'chedy' in w1 or 'shedy' in w1: # Following
            bigrams[f"{w1} {w2}"] += 1
            
    # --- Analysis 4: Morphology ---
    morph_counts = Counter()
    targets = ['qokchedy', 'lchedy', 'chedy', 'sheedy', 'qokeey', 'okeol']
    
    for w in recipe_words_for_bigrams:
        if w in targets:
            morph_counts[w] += 1
        
    # --- Output Report ---
    report_lines = []
    report_lines.append("# Chedy Analysis Report")
    report_lines.append("## 1. Distribution in Recipes")
    report_lines.append(f"- Total Recipe Starts (inferred via 'daiin/pchedal'): {recipe_starts}")
    report_lines.append(f"- 'chedy' at END of recipe (before 'daiin'): {chedy_at_end_of_prev} ({chedy_at_end_of_prev/(recipe_starts or 1)*100:.1f}%)")
    
    report_lines.append("\nTop 10 Recipe Ending Words:")
    for w, c in end_word_dist.most_common(10):
        report_lines.append(f"- {w}: {c}")
    
    report_lines.append("\n## 2. Herbal Labels")
    if label_hits:
        report_lines.append("- Found 'chedy' in herbal labels:")
        for hit in label_hits:
            report_lines.append(f"  - {hit}")
    else:
        report_lines.append("- No herbal labels found containing 'chedy'.")
        
    report_lines.append("\n## 3. Common Phrases (Bigrams)")
    report_lines.append("Top 20 bigrams involving chedy/shedy:")
    for phrase, count in bigrams.most_common(20):
        report_lines.append(f"- {phrase}: {count}")
        
    report_lines.append("\n## 4. Morphology & Variants (Recipe Section)")
    for t in targets:
        report_lines.append(f"- {t}: {morph_counts[t]}")
        
    # Write Report
    report_path = Path("results/chedy_investigation_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding='utf-8')
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    analyze_chedy()
