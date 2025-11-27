import json
import os

INPUT_FILE = "results/master_dictionary_v7.json"
OUTPUT_FILE = "results/master_dictionary_v7_1.json"
REPORT_FILE = "results/dictionary_v7_1_report.md"

def update_dictionary():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    try:
        with open(INPUT_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON: {e}")
        return

    entries = data.get("entries", {})
    updated_count = 0
    
    # 1. Update definition of 'y'
    if 'y' in entries:
        entries['y']['meaning'] = "Conjunction (And/Then)"
        entries['y']['confidence'] = 0.85
        entries['y']['notes'] = "Connects steps in recipes and items in lists. Rarely appears in labels."
        entries['y']['type'] = "conjunction"
        # Keep source if it exists, or append
        if "source" in entries['y']:
             if "Track115" not in entries['y']['source']:
                entries['y']['source'] += ", Track115"
        else:
             entries['y']['source'] = "Track115"
             
        updated_count += 1
        print("Updated 'y'")
    else:
        # Create if not exists
        entries['y'] = {
            "voynich": "y",
            "meaning": "Conjunction (And/Then)",
            "confidence": 0.85,
            "notes": "Connects steps in recipes and items in lists. Rarely appears in labels.",
            "type": "conjunction",
            "source": "Track115"
        }
        updated_count += 1
        print("Created 'y'")

    # 2. Review y- words
    y_compounds = []
    
    # Iterate over a copy of keys since we might modify entries (though here we modify values, not keys)
    for word in list(entries.keys()):
        if word.startswith('y') and len(word) > 1:
            remainder = word[1:]
            
            # Check if remainder is a known word in the dictionary
            if remainder in entries:
                base_entry = entries[remainder]
                base_meaning = base_entry.get('meaning', '')
                base_conf = base_entry.get('confidence', 0)
                
                # Avoid using undefined base words
                if base_meaning and "unknown" not in base_meaning.lower() and base_meaning != "star_name":
                    original_meaning = entries[word].get('meaning', 'unknown')
                    original_conf = entries[word].get('confidence', 0)
                    
                    # Create the new proposed meaning
                    new_meaning = f"And {base_meaning}"
                    
                    # Special check for ytaiin/ychol as per task
                    special_interest = word in ['ytaiin', 'ychol']
                    
                    y_compounds.append({
                        "word": word,
                        "remainder": remainder,
                        "base_meaning": base_meaning,
                        "current_meaning": original_meaning,
                        "proposed_meaning": new_meaning
                    })
                    
                    # Logic to update:
                    # We are more aggressive now.
                    # Update if:
                    # 1. Original is "unknown"
                    # 2. Original confidence is low (< 0.7)
                    # 3. Base word confidence is high (>= 0.8)
                    # 4. Special interest words (ytaiin, ychol)
                    # 5. Original meaning seems to be a noun/plant when the structure implies conjunction
                    
                    should_update = False
                    
                    if special_interest:
                        should_update = True
                    elif "unknown" in original_meaning.lower():
                        should_update = True
                    elif original_conf < 0.7:
                         should_update = True
                    elif base_conf >= 0.8 and original_conf < 0.95: # If base is very sure, we trust the structure
                         should_update = True
                    
                    if should_update:
                        entries[word]['meaning'] = new_meaning
                        entries[word]['notes'] = f"Parsed as y- (And) + {remainder} ({base_meaning}). Prev: {original_meaning}"
                        # Set confidence. If base is confident, we are confident.
                        # But cap it slightly below base just in case.
                        new_conf = min(base_conf, 0.85)
                        entries[word]['confidence'] = new_conf
                        entries[word]['source'] = "Track115_Compound"
                        
                        # Special handling for ytaiin note
                        if word == 'ytaiin':
                             entries[word]['notes'] += " (Possible 'And take' if taiin=take)"
                        
                        updated_count += 1

    # Save output
    data['version'] = "7.1"
    data['total_entries'] = len(entries)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved {OUTPUT_FILE}")
    
    # Generate Report
    generate_report(updated_count, y_compounds)
    print(f"Saved {REPORT_FILE}")

def generate_report(updated_count, y_compounds):
    with open(REPORT_FILE, 'w') as f:
        f.write("# Dictionary Update v7.1 Report\n\n")
        f.write(f"**Total Updates:** {updated_count}\n\n")
        f.write("## Major Changes\n")
        f.write("- **y**: Redefined as Conjunction (And/Then).\n\n")
        f.write("## `y-` Compound Analysis\n")
        f.write("Words starting with `y` where the remainder is a known word.\n\n")
        f.write("| Word | Remainder | Base Meaning | Old Meaning | New Meaning |\n")
        f.write("|------|-----------|--------------|-------------|-------------|\n")
        
        # Sort by word
        y_compounds.sort(key=lambda x: x['word'])
        
        for item in y_compounds:
            # Clean up strings for markdown table
            w = item['word']
            r = item['remainder']
            bm = str(item['base_meaning']).replace('|', '/')
            cm = str(item['current_meaning']).replace('|', '/')
            pm = str(item['proposed_meaning']).replace('|', '/')
            f.write(f"| {w} | {r} | {bm} | {cm} | {pm} |\n")

if __name__ == "__main__":
    update_dictionary()
