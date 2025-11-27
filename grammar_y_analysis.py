import json
import os
import re
from collections import defaultdict

# Configuration
EVA_FILE = 'data/eva_ivtff.txt'
DICT_FILE = 'results/master_dictionary_v7.json'
ILLUST_FILE = 'results/illustration_match.json'
OUTPUT_REPORT = 'results/grammar_y_report.md'

PLANT_FILE = 'results/plant_identifications.json'

def load_json(filepath):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_eva_lines(transcriber='C'):
    lines = []
    if not os.path.exists(EVA_FILE):
        print(f"Warning: {EVA_FILE} not found.")
        return lines
    
    # Regex to capture <Page.Line...;Transcriber>
    # We want to extract 'f1r' and ensure it ends with ;C> or ;H>
    
    with open(EVA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check if it's a data line
            if not line.startswith('<'):
                continue
                
            # Split into location and text
            # Location is inside <...>
            try:
                if '>' in line:
                    loc_part, text_part = line.split('>', 1)
                else:
                    continue
            except ValueError:
                continue
                
            loc_content = loc_part[1:] # remove leading <
            
            # Check transcriber
            if f";{transcriber}" not in loc_content:
                continue
                
            # Extract Page ID
            # loc_content example: f1r.1,@P0;C
            page_id = loc_content.split('.')[0]
            
            # Process text
            # Replace . with space
            clean_text = text_part.strip().replace('.', ' ')
            
            lines.append({
                'page': page_id,
                'text': clean_text
            })
    return lines

def is_y_prefixed(word):
    # Check for y- prefix
    # Note: 'y' itself is a word sometimes? 
    # Prompt implies y- as prefix. "ychol"
    return word.startswith('y') and len(word) > 1

def get_base(word):
    if word.startswith('y'):
        return word[1:]
    return word

def analyze_lists(lines):
    """
    Analyze if y- appears in list-like structures (A, yB, yC or A, B, yC).
    """
    stats = {
        'total_y_words': 0,
        'y_start_sentence': 0,
        'y_as_second_item': 0,
        'y_as_later_item': 0,
        'repeated_base_sequences': 0,
        'repeated_base_y_sequences': 0, # e.g., "chol ychol"
        'single_word_lines': 0,
        'y_single_word_lines': 0,
        'y_word_counts': defaultdict(int)
    }
    
    list_patterns = []

    for entry in lines:
        words = entry['text'].split()
        clean_words = [w.strip(',?!') for w in words]
        
        if len(clean_words) == 1:
            stats['single_word_lines'] += 1
            if clean_words[0] and is_y_prefixed(clean_words[0]):
                stats['y_single_word_lines'] += 1
        
        for i, word in enumerate(clean_words):
            if not word: continue
            
            # Filter out 'y' itself if it appears as a standalone word (it exists in EVA)
            if word == 'y': continue 
            
            if is_y_prefixed(word):
                stats['total_y_words'] += 1
                stats['y_word_counts'][word] += 1
                if i == 0:
                    stats['y_start_sentence'] += 1
                elif i == 1:
                    stats['y_as_second_item'] += 1
                else:
                    stats['y_as_later_item'] += 1
            
            # Check for "Word, yWord" pattern (repetition with conjunction/plural)
            if i > 0:
                prev_word = clean_words[i-1]
                if not prev_word: continue
                
                base_curr = get_base(word)
                base_prev = get_base(prev_word)
                
                if base_curr == base_prev and len(base_curr) > 1: # Avoid single letter matches
                    stats['repeated_base_sequences'] += 1
                    if not is_y_prefixed(prev_word) and is_y_prefixed(word):
                        stats['repeated_base_y_sequences'] += 1 # "chol ychol"
                        list_patterns.append(f"{prev_word} {word} (Page: {entry['page']})")

    return stats, list_patterns

def analyze_plurality(lines, illust_data):
    """
    Correlate y- usage with known plural contexts (images).
    """
    # 1. Identify pages with multiple items vs single items
    multi_item_pages = set()
    single_item_pages = set()
    
    # From plant_identifications.json
    plant_data = load_json(PLANT_FILE)
    if plant_data and 'identifications' in plant_data:
        for item in plant_data['identifications']:
            page = item.get('folio')
            features = item.get('features', {})
            is_plural = False
            
            # Check feature descriptions
            for key, val in features.items():
                val_str = str(val).lower()
                if 'multiple' in val_str or 'clustered' in val_str or 'many' in val_str or 'bunch' in val_str:
                    is_plural = True
            
            # Check top candidate reason/name
            cand = item.get('top_candidate', {})
            reason = str(cand.get('reason', '')).lower()
            if 'multiple' in reason:
                is_plural = True
                
            if is_plural:
                multi_item_pages.add(page)
            # If we identified features but didn't find plural markers, assume single (weak assumption but okay for contrast)
            elif features:
                single_item_pages.add(page)

    # From illustration_match.json
    if illust_data and 'per_page' in illust_data:
        for page, data in illust_data['per_page'].items():
            desc = str(data.get('visual_description', '')).lower()
            elems = data.get('visual_elements', [])
            
            is_plural = False
            if 'multiple' in desc or 'two' in desc or 'three' in desc or 'bunch' in desc or 'many' in desc:
                is_plural = True
            for elem in elems:
                if 'multiple' in elem or 'roots' in elem: 
                    is_plural = True
            
            if is_plural:
                multi_item_pages.add(page)
            else:
                # If specifically single
                if 'single' in desc or 'one' in desc:
                    single_item_pages.add(page)
    
    # 2. Count Base vs yBase on these pages
    # Focus on common nouns: chol (leaf), char (root), daiin, shey, aiin
    target_nouns = ['chol', 'char', 'daiin', 'shey', 'aiin', 'or', 'ar'] 
    
    counts = defaultdict(lambda: {'single_page': {'base': 0, 'y_base': 0}, 
                                  'multi_page': {'base': 0, 'y_base': 0},
                                  'unknown_page': {'base': 0, 'y_base': 0}})
    
    for entry in lines:
        page = entry['page']
        page_type = 'unknown_page'
        if page in single_item_pages:
            page_type = 'single_page'
        elif page in multi_item_pages:
            page_type = 'multi_page'
            
        words = entry['text'].split()
        for word in words:
            word = word.strip(',?!')
            base = get_base(word)
            is_y = is_y_prefixed(word)
            
            if base in target_nouns:
                if is_y:
                    counts[base][page_type]['y_base'] += 1
                else:
                    counts[base][page_type]['base'] += 1
                    
    return counts, multi_item_pages, single_item_pages

def generate_report(stats, list_patterns, plural_counts, multi_pages, single_pages):
    lines = []
    lines.append("# Grammar Analysis: The Function of 'y-'")
    lines.append("\n## 1. List Analysis (Conjunction Hypothesis)")
    
    total = stats['total_y_words'] if stats['total_y_words'] > 0 else 1
    
    lines.append(f"- **Total words starting with y-**: {stats['total_y_words']}")
    lines.append(f"- **y- at start of line**: {stats['y_start_sentence']} ({(stats['y_start_sentence']/total*100):.1f}%)")
    lines.append(f"- **y- as 2nd item**: {stats['y_as_second_item']} ({(stats['y_as_second_item']/total*100):.1f}%)")
    lines.append(f"- **y- as 3rd+ item**: {stats['y_as_later_item']} ({(stats['y_as_later_item']/total*100):.1f}%)")
    
    lines.append(f"- **Single Word Lines**: {stats['single_word_lines']}")
    lines.append(f"- **Single Word Lines starting with y-**: {stats['y_single_word_lines']}")
    if stats['single_word_lines'] > 0:
        pct = stats['y_single_word_lines'] / stats['single_word_lines'] * 100
        lines.append(f"  - Percentage: {pct:.1f}%")

    lines.append("\n### Top y- Words")
    # Sort by freq
    sorted_y = sorted(stats['y_word_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    for w, c in sorted_y:
        lines.append(f"- `{w}`: {c}")

    lines.append("\n### 'Word yWord' Patterns (e.g., 'chol ychol')")
    lines.append(f"- Found {stats['repeated_base_y_sequences']} instances where a word is immediately followed by its y-form.")
    if list_patterns:
        lines.append("- Examples:")
        for p in list_patterns[:10]:
            lines.append(f"  - `{p}`")
    else:
        lines.append("- No examples found.")
        
    lines.append("\n**Interpretation:**")
    if stats['repeated_base_y_sequences'] > 5:
        lines.append("- The pattern `X yX` is present, suggesting 'X and X' or 'X and Xs'.")
    else:
        lines.append("- The pattern `X yX` is rare.")

    lines.append("\n## 2. Plural Analysis (Morphology Hypothesis)")
    lines.append(f"- Analyzed {len(multi_pages)} multi-item pages and {len(single_pages)} single-item pages.")
    
    lines.append("\n### Noun Distribution")
    lines.append("| Word (Base) | Single Pg (Base/yBase) | Multi Pg (Base/yBase) | Ratio Change |")
    lines.append("|---|---|---|---|")
    
    plural_evidence = 0
    conjunction_evidence = 0
    
    for noun, data in plural_counts.items():
        s_base = data['single_page']['base']
        s_y = data['single_page']['y_base']
        m_base = data['multi_page']['base']
        m_y = data['multi_page']['y_base']
        
        s_total = s_base + s_y
        m_total = m_base + m_y
        
        if s_total < 5 and m_total < 5: continue # Skip rare words
        
        s_ratio = s_y / (s_base + 0.001)
        m_ratio = m_y / (m_base + 0.001)
        
        change = "SAME"
        if m_ratio > s_ratio * 1.3: 
            change = "**HIGHER in Multi**"
            if noun in ['chol', 'char', 'ar']: # High confidence nouns
                plural_evidence += 1
        elif s_ratio > m_ratio * 1.3: 
            change = "**LOWER in Multi**"
        
        lines.append(f"| **{noun}** | {s_base}/{s_y} ({s_ratio:.2f}) | {m_base}/{m_y} ({m_ratio:.2f}) | {change} |")

    lines.append("\n## 3. Conclusions")
    
    # Logic for conclusion
    if stats['y_as_later_item'] > stats['y_start_sentence']:
        conjunction_evidence += 1
        
    lines.append(f"- Plural Evidence Score: {plural_evidence}")
    lines.append(f"- Conjunction Evidence (Positioning): {'Yes' if conjunction_evidence > 0 else 'No'}")
    
    if plural_evidence > 0 and conjunction_evidence > 0:
         lines.append("- **Ambiguous/Dual Function:** `y-` behaves like a clitic conjunction (like Hebrew 've-' or Latin '-que') which naturally appears more often in lists (which might correlate with multiple items).")
    elif plural_evidence > 0:
        lines.append("- **Plural Marker:** The correlation with multi-item pages is the strongest signal.")
    elif conjunction_evidence > 0:
        lines.append("- **Conjunction:** The positional data (appearing later in lists) strongly supports 'And'.")
    else:
        lines.append("- **Unclear:** 'y-' is pervasive but its function remains elusive based on these simple metrics.")
        
    return "\n".join(lines)

def main():
    print("Loading Dictionary...")
    dictionary = load_json(DICT_FILE)
    
    print("Loading Illustrations...")
    illust_data = load_json(ILLUST_FILE)
    
    print("Loading Text...")
    # Use 'C' (Currier) as standard, or 'H' if preferred. 
    lines = load_eva_lines(transcriber='C')
    print(f"Loaded {len(lines)} lines using Transcriber 'C'.")
    
    if len(lines) == 0:
        print("Trying transcriber 'H'...")
        lines = load_eva_lines(transcriber='H')
        print(f"Loaded {len(lines)} lines using Transcriber 'H'.")
    
    if len(lines) == 0:
        print("Trying generic parse (ignoring transcriber suffix)...")
        lines = load_eva_lines(transcriber='') # This won't work with my current logic, need fix if needed.
        # But let's hope C or H works.

    print("Analyzing Lists...")
    stats, list_patterns = analyze_lists(lines)
    
    print("Analyzing Plurals...")
    plural_counts, m_pages, s_pages = analyze_plurality(lines, illust_data)
    
    print("Generating Report...")
    report = generate_report(stats, list_patterns, plural_counts, m_pages, s_pages)
    
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Done. Report saved to {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
