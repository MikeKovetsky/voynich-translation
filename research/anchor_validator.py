import csv
import os
from research.voynich_data import get_folio_text, convert_eva_to_claston

# 1. Load Sherwood Mapping
SHERWOOD_FILE = "data/external_corpora/sherwood_plant_mapping.csv"
PHONETIC_FILE = "results/phonetic_candidates.csv"
OUTPUT_FILE = "results/gold_anchors.csv"
REPORT_FILE = "results/anchor_report.md"

def normalize_text(text):
    return text.lower().strip()

def main():
    if not os.path.exists(SHERWOOD_FILE):
        print(f"Error: {SHERWOOD_FILE} not found.")
        return

    print("Loading Sherwood Mapping...")
    folio_map = []
    with open(SHERWOOD_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Skip header
        for row in reader:
            if len(row) >= 3:
                folio_map.append({
                    'folio': row[0].strip(),
                    'common': row[1].strip(),
                    'latin': row[2].strip()
                })

    print(f"Loaded {len(folio_map)} plant mappings.")

    print("Loading Phonetic Candidates...")
    phonetic_map = {} # latin_target -> list of voynich_words
    if os.path.exists(PHONETIC_FILE):
        with open(PHONETIC_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                target = row['target_word']
                voynich = row['voynich_word']
                if target not in phonetic_map:
                    phonetic_map[target] = []
                phonetic_map[target].append(voynich)
    
    gold_anchors = []
    hits_log = []

    print("Scanning Folios...")
    for entry in folio_map:
        folio = entry['folio']
        latin_name = entry['latin']
        common_name = entry['common']
        
        # Normalize Folio (Sherwood uses '2r', we need 'f2r')
        # Also handle '87vleft' -> 'f87v'
        clean_folio = folio.lower().replace("left", "").replace("right", "").replace(" ", "")
        if not clean_folio.startswith('f'):
            clean_folio = 'f' + clean_folio
            
        # Special handling for split folios (e.g. f87v)
        # get_folio_text should handle standard names
        
        voynich_text_lines = get_folio_text(clean_folio, system='EVA')
        if not voynich_text_lines:
            # Try cleaning up suffix numbers e.g. 90v1 -> 90v
            base_folio = "".join([c for c in clean_folio if not c.isdigit() or c == 'f' or clean_folio.index(c) < 4])
            # This regex is tricky. Let's just try basic names.
            if '1' in clean_folio or '2' in clean_folio:
                 base_folio = clean_folio.replace('1', '').replace('2', '')
                 voynich_text_lines = get_folio_text(base_folio, system='EVA')
        
        if not voynich_text_lines:
            print(f"Warning: Text not found for {folio} ({clean_folio})")
            continue
            
        full_text = " ".join(voynich_text_lines.values())
        words = full_text.split()
        
        # Target Words to match
        # 1. The Latin Name parts (e.g. 'Pisum', 'sativum')
        target_parts = latin_name.split()
        target_parts.extend(common_name.split('/')) # Add common names
        
        # Clean targets
        clean_targets = [t.strip().lower().replace('(', '').replace(')', '') for t in target_parts if len(t) > 2]
        
        found_match = False
        
        for t in clean_targets:
            # Strategy 1: Check Phonetic Candidates (Is there a word in the text that is phonetic match to t?)
            candidates = phonetic_map.get(t, [])
            
            for cand in candidates:
                if cand in words:
                    gold_anchors.append([folio, cand, t, "1.0", "Phonetic Match in Text"])
                    hits_log.append(f"- **{folio}:** Found `{cand}` (matches target *{t}*)")
                    found_match = True
            
            # Strategy 2: Direct Substring (Desperate fuzzy match)
            # If 'pis' is in the text and target is 'pisum'
            # Need to be careful not to match 'o' to 'potato'
            if not found_match:
                # Check first 3 chars of target if len > 4
                if len(t) >= 4:
                    prefix = t[:3]
                    for w in words:
                        if w.startswith(prefix):
                             # Potential
                             pass

    # Output
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['folio', 'voynich_word', 'latin_target', 'confidence', 'method'])
        writer.writerows(gold_anchors)
        
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Anchor Validation Report\n\nFound {len(gold_anchors)} potential anchors.\n\n")
        f.write("\n".join(hits_log))
        
    print(f"Found {len(gold_anchors)} anchors.")

if __name__ == "__main__":
    main()
