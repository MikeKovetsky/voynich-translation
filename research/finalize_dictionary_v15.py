import json
import os
from datetime import datetime

INPUT_FILE = 'results/dictionary/dictionary_v15_draft.json'
OUTPUT_FILE = 'results/dictionary/master_dictionary_v15.json'
STATS_FILE = 'results/dictionary_v15_stats.md'

UPDATES = {
    'okora': {'meaning': "Cure / Heart Remedy", 'confidence': 0.8},
    'qokeey': {'meaning': "Cook / Boil", 'confidence': 0.9},
    'qokedy': {'meaning': "Mixture / Decoction", 'confidence': 0.9},
    'sho': {'meaning': "Heat / Fire", 'confidence': 0.8},
    'keero': {'meaning': "Coriander (candidate)", 'confidence': 0.6},
    'shkair': {'meaning': "Chicory (candidate)", 'confidence': 0.5},
}

REVERTS = {
    'cphor': {'meaning': "Generic Plant", 'confidence': 0.3},
    'som': {'meaning': "Generic Ingredient", 'confidence': 0.3},
}

def load_dictionary(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_dictionary(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def finalize_dictionary():
    print(f"Loading {INPUT_FILE}...")
    data = load_dictionary(INPUT_FILE)
    entries = data.get('entries', {})
    
    changes_log = []

    # Apply Updates
    for word, info in UPDATES.items():
        if word in entries:
            old_meaning = entries[word].get('meaning', 'N/A')
            old_conf = entries[word].get('confidence', 0.0)
            
            entries[word]['meaning'] = info['meaning']
            entries[word]['confidence'] = info['confidence']
            entries[word]['source'] = "Track273_Finalize"
            
            changes_log.append(f"- Updated `{word}`: '{old_meaning}' ({old_conf}) -> '{info['meaning']}' ({info['confidence']})")
        else:
            entries[word] = {
                "voynich": word,
                "meaning": info['meaning'],
                "confidence": info['confidence'],
                "source": "Track273_Finalize",
                "language": "unknown", 
                "domain": "unknown"
            }
            changes_log.append(f"- Added `{word}`: '{info['meaning']}' ({info['confidence']})")

    # Apply Reverts
    for word, info in REVERTS.items():
        if word in entries:
            old_meaning = entries[word].get('meaning', 'N/A')
            old_conf = entries[word].get('confidence', 0.0)
            
            entries[word]['meaning'] = info['meaning']
            entries[word]['confidence'] = info['confidence']
            entries[word]['source'] = "Track273_Finalize_Revert"
            
            changes_log.append(f"- Reverted `{word}`: '{old_meaning}' ({old_conf}) -> '{info['meaning']}' ({info['confidence']})")
        else:
             # Should usually exist if we revert, but just in case
            entries[word] = {
                "voynich": word,
                "meaning": info['meaning'],
                "confidence": info['confidence'],
                "source": "Track273_Finalize_Revert",
                "language": "unknown",
                "domain": "unknown"
            }
            changes_log.append(f"- Added (Revert) `{word}`: '{info['meaning']}' ({info['confidence']})")

    # Update Metadata
    data['version'] = "15.0_master"
    data['date'] = datetime.now().isoformat()
    
    # Save
    print(f"Saving to {OUTPUT_FILE}...")
    save_dictionary(data, OUTPUT_FILE)
    
    # Stats Generation
    high_conf = 0
    med_conf = 0
    low_conf = 0
    total = len(entries)
    
    for word, entry in entries.items():
        conf = entry.get('confidence', 0)
        if conf >= 0.8:
            high_conf += 1
        elif conf >= 0.5:
            med_conf += 1
        else:
            low_conf += 1
            
    stats_content = f"""# Dictionary v15 Master Stats

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Entries:** {total}

## Confidence Distribution
- **High Confidence (>= 0.8):** {high_conf} ({high_conf/total*100:.1f}%)
- **Medium Confidence (0.5 - 0.79):** {med_conf} ({med_conf/total*100:.1f}%)
- **Low Confidence (< 0.5):** {low_conf} ({low_conf/total*100:.1f}%)

## Changes in v15 Finalize
{chr(10).join(changes_log)}
"""
    
    print(f"Writing stats to {STATS_FILE}...")
    with open(STATS_FILE, 'w') as f:
        f.write(stats_content)

if __name__ == "__main__":
    finalize_dictionary()
