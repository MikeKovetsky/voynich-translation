import json
import datetime

def update_dictionary():
    input_path = 'results/dictionary/dictionary.json'
    output_path = 'results/dictionary/dictionary_v9_2.json'
    summary_path = 'results/track-197-results_summary.md'
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return

    updates = {
        "ald": {
            "meaning": "plant:thistle",
            "source_note": "Aries/Mars match",
            "verification": "zodiac",
            "domain": "botanical",
            "is_tentative": False
        },
        "choly": {
            "meaning": "plant:nettle",
            "source_note": "Aries/Mars match",
            "verification": "zodiac",
            "domain": "botanical",
            "is_tentative": False
        },
        "chotey": {
            "meaning": "plant:wheat",
            "source_note": "Virgo match",
            "verification": "zodiac",
            "domain": "botanical",
            "is_tentative": False
        },
        "opaiin": {
            "meaning": "plant:geranium",
            "source_note": "Scorpio match - Tentative",
            "verification": "zodiac",
            "domain": "botanical",
            "is_tentative": True
        }
    }
    
    entries = data['entries']
    updated_count = 0
    
    for word, update_info in updates.items():
        if word not in entries:
            entries[word] = {
                "voynich": word,
                "folios": []
            }
            
        entry = entries[word]
        
        # Update fields
        entry['meaning'] = update_info['meaning']
        entry['domain'] = update_info['domain']
        
        # Handle verification
        if 'verification' not in entry:
            entry['verification'] = update_info['verification']
        elif update_info['verification'] not in entry['verification']:
             entry['verification'] = f"{entry['verification']}, {update_info['verification']}"
             
        # Handle source
        if 'source' not in entry:
            entry['source'] = update_info['source_note']
        else:
            # Append if not already present
            if update_info['source_note'] not in entry['source']:
                 entry['source'] = f"{entry['source']}; {update_info['source_note']}"
        
        # Set confidence
        if update_info['is_tentative']:
             # Keep existing if higher, or set to medium/0.6
             if entry.get('confidence', 0) < 0.6:
                 entry['confidence'] = 0.6
                 entry['confidence_level'] = "MEDIUM"
        else:
             entry['confidence'] = 0.95
             entry['confidence_level'] = "ULTRA_HIGH" # Using ULTRA_HIGH as seen in 'ksheody' for confirmed matches
             
        entries[word] = entry
        updated_count += 1

    # Calculate stats
    known_plants = 0
    for k, v in entries.items():
        if v.get('domain') == 'botanical' and v.get('meaning', '').startswith('plant:'):
            known_plants += 1
            
    data['version'] = "9.2"
    data['date'] = datetime.datetime.now().isoformat()
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
        
    # Generate summary
    summary = f"""# Track 197 Results Summary

## Dictionary Update v9.2

Updated dictionary with confirmed Zodiac plant matches.

### Updates
| Word | Meaning | Source | Verification |
|------|---------|--------|--------------|
| ald | thistle | Aries/Mars match | zodiac |
| choly | nettle | Aries/Mars match | zodiac |
| chotey | wheat | Virgo match | zodiac |
| opaiin | geranium | Scorpio match - Tentative | zodiac |

### Statistics
- **Total Entries:** {len(entries)}
- **Known Plants:** {known_plants}
- **Version:** 9.2
"""
    
    with open(summary_path, 'w') as f:
        f.write(summary)
        
    print(f"Updated {updated_count} entries. Saved to {output_path}")
    print(f"Summary saved to {summary_path}")

if __name__ == "__main__":
    update_dictionary()
