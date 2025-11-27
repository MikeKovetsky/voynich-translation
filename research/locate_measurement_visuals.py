import re
import os

input_file = "results/quire20_translation_master.md"
output_file = "results/measurement_locations.txt"

def parse_locations():
    current_folio = None
    current_recipe = None
    locations = []
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("## Folio"):
                current_folio = line.replace("## Folio", "").strip()
                current_recipe = None
            elif line.startswith("**Recipe"):
                current_recipe = line.replace("**", "").strip()
            elif line and not line.startswith("#") and not line.startswith("*"):
                # This is likely a text line
                words = line.split()
                # Normalize words to remove punctuation attached to them
                # But careful not to lose 'saiin' vs 'saiin.'
                
                # Simple check for target words
                targets = ["saiin", "sain", "daiin", "dain", "ar", "aral"]
                
                found = []
                for word in words:
                    # Remove some punctuation
                    clean_word = word.replace("!", "").replace("?", "").replace(".", "").replace(",", "")
                    if clean_word in targets:
                         found.append(clean_word)
                    elif "saiin" in word: # Catch compounds
                        found.append(word)
                    elif "ar" == clean_word: # Strict for ar
                        found.append(word)
                
                if found:
                    locations.append({
                        "folio": current_folio,
                        "recipe": current_recipe,
                        "terms": found,
                        "context": line[:100] + "..."
                    })

    return locations

locs = parse_locations()
print(f"Found {len(locs)} locations.")
for loc in locs:
    print(f"Folio: {loc['folio']}, Recipe: {loc['recipe']}, Terms: {loc['terms']}")
    print(f"  Context: {loc['context']}")
