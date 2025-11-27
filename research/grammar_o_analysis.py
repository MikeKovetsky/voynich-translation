import re
import json
from collections import defaultdict, Counter
import os

EVA_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/master_dictionary_v7.json"
OUTPUT_REPORT = "results/grammar_o_report.md"

def load_lines():
    with open(EVA_FILE, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            # Parse <f1r.1,@P0;H> text...
            m = re.match(r'<([^>]+);(\w)>\s*(.+)', line)
            if m:
                loc_full, transcriber, text = m.groups()
                if transcriber != 'H': continue # Use Takahashi
                
                # Parse location and tags
                if ',' in loc_full:
                    loc_parts = loc_full.split(',')
                    base_loc = loc_parts[0]
                    tags = loc_parts[1:]
                else:
                    base_loc = loc_full
                    tags = []
                
                folio = base_loc.split('.')[0]
                yield folio, tags, text

def clean_text(text):
    # Remove comments/markup like {comment} or &char;
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'[^\w\s\.]', '', text) # Keep dots for sentence boundary
    return text

def main():
    print("Starting Grammar O Analysis...")
    
    # Load Dictionary
    try:
        with open(DICT_FILE, 'r') as f:
            master_dict = json.load(f)
        known_words = set(master_dict.get('entries', {}).keys())
    except FileNotFoundError:
        print(f"Warning: {DICT_FILE} not found. Proceeding without dictionary context.")
        known_words = set()
    
    # Counters
    o_counts = Counter()
    ol_counts = Counter()
    all_words_count = 0
    
    label_o_counts = Counter()
    label_total = 0
    
    start_o_counts = Counter()
    start_total = 0
    
    plural_o_labels = Counter()
    plural_label_total = 0
    
    singular_o_labels = Counter()
    singular_label_total = 0
    
    daiin_followers = Counter()
    
    o_following_chars = Counter()
    ol_following_chars = Counter()
    
    # Define folio groups
    star_folios = set()
    for i in range(67, 74):
        star_folios.add(f'f{i}r1')
        star_folios.add(f'f{i}r2')
        star_folios.add(f'f{i}v1')
        star_folios.add(f'f{i}v2')
        star_folios.add(f'f{i}r')
        star_folios.add(f'f{i}v')
    
    bio_folios = set([f'f{i}r' for i in range(75, 85)] + [f'f{i}v' for i in range(75, 85)])
    herbal_folios = set([f'f{i}r' for i in range(1, 58)] + [f'f{i}v' for i in range(1, 58)])
    
    # Processing
    for folio, tags, text in load_lines():
        is_label = any(t.startswith('@L') or t.startswith('@R') or t.startswith('@K') for t in tags)
        clean = clean_text(text)
        words = clean.replace('.', ' ').split()
        
        # Skip empty
        if not words: continue
        
        for i, word in enumerate(words):
            all_words_count += 1
            
            # Check o- prefix
            has_o = word.startswith('o') and len(word) > 2 and word[1] not in ['o'] 
            has_ol = word.startswith('ol') and len(word) > 3
            
            prefix = ""
            
            if has_ol:
                prefix = "ol"
            elif has_o:
                prefix = "o"
            
            if prefix:
                if prefix == 'o': 
                    o_counts[word] += 1
                    if len(word) > 1: o_following_chars[word[1]] += 1
                if prefix == 'ol': 
                    ol_counts[word] += 1
                    if len(word) > 2: ol_following_chars[word[2]] += 1
                
                if is_label:
                    label_o_counts[word] += 1
                    
                    is_star = any(sf in folio for sf in star_folios)
                    is_bio = folio in bio_folios
                    is_herbal = folio in herbal_folios
                    
                    if is_star or is_bio:
                        plural_o_labels[word] += 1
                    elif is_herbal:
                        singular_o_labels[word] += 1
                
                if i == 0:
                    start_o_counts[word] += 1
            
            if is_label:
                label_total += 1
                is_star = any(sf in folio for sf in star_folios)
                is_bio = folio in bio_folios
                is_herbal = folio in herbal_folios
                
                if is_star or is_bio:
                    plural_label_total += 1
                elif is_herbal:
                    singular_label_total += 1
            
            if i == 0:
                start_total += 1

            # Daiin check
            if i > 0 and words[i-1] in ['daiin', 'ytaiin', 'cthaiin']:
                daiin_followers[word] += 1

    # Generate Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Grammar Analysis: The 'o-' Prefix\n\n")
        
        # 1. Distribution
        f.write("## 1. General Distribution\n")
        total_o = sum(o_counts.values())
        total_ol = sum(ol_counts.values())
        f.write(f"- Total words analyzed: {all_words_count}\n")
        f.write(f"- Total 'o-' words: {total_o} ({total_o/all_words_count*100:.2f}%)\n")
        f.write(f"- Total 'ol-' words: {total_ol} ({total_ol/all_words_count*100:.2f}%)\n")
        
        f.write(f"\n### Top 'o-' words:\n")
        for w, c in o_counts.most_common(15):
            f.write(f"  - {w}: {c}\n")

        f.write(f"\n### Top 'ol-' words:\n")
        for w, c in ol_counts.most_common(10):
            f.write(f"  - {w}: {c}\n")
            
        # Phonetic Analysis
        f.write("\n## 2. Phonetic Analysis (Next Character)\n")
        f.write("What follows 'o-'?\n")
        for char, count in o_following_chars.most_common(5):
            f.write(f"- {char}: {count} ({count/total_o*100:.1f}%)\n")
            
        f.write("\nWhat follows 'ol-'?\n")
        for char, count in ol_following_chars.most_common(5):
            f.write(f"- {char}: {count} ({count/total_ol*100:.1f}%)\n")

        # 3. Label Analysis
        f.write("\n## 3. Label Analysis\n")
        f.write(f"- Total Labels: {label_total}\n")
        o_label_pct = sum(label_o_counts.values()) / label_total * 100 if label_total else 0
        f.write(f"- Labels starting with 'o-'/'ol-': {sum(label_o_counts.values())} ({o_label_pct:.2f}%)\n")
        
        f.write("\n### Plurality Test (Stars/Bio vs Herbal)\n")
        plural_pct = sum(plural_o_labels.values()) / plural_label_total * 100 if plural_label_total else 0
        singular_pct = sum(singular_o_labels.values()) / singular_label_total * 100 if singular_label_total else 0
        
        f.write(f"- Plural Pages (Stars/Bio) 'o-' Label Frequency: {plural_pct:.2f}% ({sum(plural_o_labels.values())}/{plural_label_total})\n")
        f.write(f"- Singular Pages (Herbal) 'o-' Label Frequency: {singular_pct:.2f}% ({sum(singular_o_labels.values())}/{singular_label_total})\n")
        
        f.write(f"\n**Comparison:** Plural pages have {plural_pct/singular_pct if singular_pct else 0:.2f}x frequency of 'o-' labels compared to singular pages.\n")
        
        if plural_pct > singular_pct * 1.5:
            f.write("\n**Hypothesis Supported:** 'o-' appears significantly more often on plural/collective pages.\n")
        elif singular_pct > plural_pct * 1.5:
            f.write("\n**Hypothesis Rejected:** 'o-' appears more on singular pages.\n")
        else:
            f.write("\n**Result:** No strong correlation with page type found in labels.\n")
            
        f.write("\n### Top Plural Page Labels with o-:\n")
        for w, c in plural_o_labels.most_common(10):
            f.write(f"- {w}: {c}\n")

        # 4. Daiin Context
        f.write("\n## 4. 'Daiin' (Take) Context\n")
        f.write("Words following 'daiin', 'ytaiin', 'cthaiin':\n")
        
        daiin_o_count = sum(c for w, c in daiin_followers.items() if w.startswith('o') or w.startswith('ol'))
        daiin_total = sum(daiin_followers.values())
        daiin_o_pct = daiin_o_count / daiin_total * 100 if daiin_total else 0
        
        f.write(f"- Total followers: {daiin_total}\n")
        f.write(f"- Followers starting with 'o-'/'ol-': {daiin_o_count} ({daiin_o_pct:.2f}%)\n")
        f.write("- Top followers:\n")
        for w, c in daiin_followers.most_common(15):
            is_o = w.startswith('o') or w.startswith('ol')
            mark = "**" if is_o else ""
            f.write(f"  - {mark}{w}{mark}: {c}\n")
            
    print(f"Analysis complete. Report written to {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
