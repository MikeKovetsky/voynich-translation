import json
import os
import Levenshtein

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("Loading Dictionary v13...")
    master_dict = load_json('results/dictionary/dictionary_v13.json')
    if not master_dict:
        print("Error: dictionary_v13.json not found")
        return
    
    entries = master_dict.get('entries', {})
    print(f"Initial entries: {len(entries)}")

    # 1. Ingest Suffix Mining
    print("Ingesting Suffix Mining...")
    suffixes = load_json('results/suffix_mining.json')
    suffix_added = 0
    suffix_updated = 0
    
    if suffixes:
        for item in suffixes:
            word = item['word']
            meaning = item['meaning']
            root = item.get('root', '')
            suffix = item.get('suffix', '')
            
            if word in entries:
                # Update existing
                entries[word]['morphology'] = {
                    'root': root,
                    'suffix': suffix,
                    'type': 'suffix_derived'
                }
                if entries[word].get('confidence', 0) < 0.5:
                     entries[word]['meaning'] = meaning
                     entries[word]['confidence'] = 0.6
                     entries[word]['source'] = 'Track251_SuffixMining'
                suffix_updated += 1
            else:
                # Add new
                entries[word] = {
                    "voynich": word,
                    "meaning": meaning,
                    "morphology": {
                        'root': root,
                        'suffix': suffix,
                        'type': 'suffix_derived'
                    },
                    "confidence": 0.6,
                    "source": "Track251_SuffixMining",
                    "domain": "inferred"
                }
                suffix_added += 1
    
    print(f"Suffixes: Added {suffix_added}, Updated {suffix_updated}")

    # 2. Ingest Visual Validation
    print("Ingesting Visual Validation...")
    # Hardcoded based on report
    visual_updates = {
        "or": {"meaning": "Red / Gold (Visual)", "confidence": 1.0},
        "ol": {"meaning": "Blue / Water / Wet (Visual)", "confidence": 1.0},
        "ok": {"meaning": "Green / Leafy (Inferred)", "confidence": 0.8}
    }
    
    for word, data in visual_updates.items():
        if word in entries:
            entries[word]['meaning'] = data['meaning']
            entries[word]['confidence'] = data['confidence']
            entries[word]['source'] = 'Track250_VisualValidation'
        else:
             entries[word] = {
                "voynich": word,
                "meaning": data['meaning'],
                "confidence": data['confidence'],
                "source": "Track250_VisualValidation",
                "domain": "visual"
            }

    # 3. Fuzzy Matching (Simple version)
    print("Running Fuzzy Matching (Experimental)...")
    # Get "Anchors" (High confidence words)
    anchors = [k for k, v in entries.items() if v.get('confidence', 0) >= 0.8]
    unknowns = [k for k, v in entries.items() if v.get('confidence', 0) < 0.3]
    
    print(f"Anchors: {len(anchors)}, Unknowns: {len(unknowns)}")
    
    fuzzy_links = 0
    
    # We limit this to avoid O(N^2) explosion. Only check unknowns against anchors.
    # And only if lengths are close.
    
    for u in unknowns:
        if len(u) < 4: continue # Skip short words
        
        best_match = None
        min_dist = 2 # Threshold
        
        for a in anchors:
            if abs(len(u) - len(a)) > 1: continue
            
            dist = Levenshtein.distance(u, a)
            if dist == 1:
                best_match = a
                break # Take first match for speed
        
        if best_match:
            entries[u]['meaning'] = f"Variant of {best_match} ({entries[best_match].get('meaning', '')})"
            entries[u]['confidence'] = 0.5
            entries[u]['source'] = 'Track255_FuzzyMatch'
            entries[u]['linked_root'] = best_match
            fuzzy_links += 1
            
    print(f"Fuzzy Links Established: {fuzzy_links}")

    # Save
    master_dict['version'] = "14.0"
    master_dict['entries'] = entries
    
    save_path = 'results/dictionary/master_dictionary_v14.json'
    save_json(master_dict, save_path)
    print(f"Saved Master Dictionary v14 to {save_path}")
    print(f"Total Entries: {len(entries)}")

if __name__ == "__main__":
    main()
