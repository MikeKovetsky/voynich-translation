import json
import datetime

def update_dictionary():
    input_path = 'results/dictionary/dictionary.json'
    output_path = 'results/dictionary_update_v10_1.json'
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {input_path} not found.")
        return

    entries = data.get('entries', {})
    
    # Words to update
    updates = {
        'aiin': {
            'meaning': 'Star / Eye (of Heaven)',
            'evidence': 'High frequency on "Dry" pages; association with os (Star).',
            'element': 'Fire/Ether'
        },
        'daiin': {
            'meaning': 'The Star / Of the Star',
            'grammar': 'd- is likely the demonstrative/definite article here.'
        },
        'oaiin': {
            'meaning': 'Stars (Plural) / The Star (Essence)',
            'grammar': 'o- (Dry/Hot marker) + aiin'
        },
        'os': {
            'meaning': 'Star / Blue Star'
        }
    }
    
    summary_changes = []
    
    for word, new_attrs in updates.items():
        if word in entries:
            entry = entries[word]
            old_meaning = entry.get('meaning', 'N/A')
            
            # Apply updates
            for key, value in new_attrs.items():
                entry[key] = value
            
            # Update metadata if missing or strictly defined
            # ensuring we keep existing fields unless overwritten
            
            entries[word] = entry
            summary_changes.append(f"- **{word}**: Changed meaning from '{old_meaning}' to '{new_attrs['meaning']}'.")
        else:
            # If word doesn't exist, create it (though task implies updates)
            # For now, assuming they exist or we add them if they are critical.
            # The task implies redefinition, so likely they exist.
            # If they don't, I'll create a basic entry.
            new_entry = {
                'voynich': word,
                'meaning': new_attrs['meaning'],
                'confidence': 0.5, # Default low confidence for new manual add
                'source': 'Track237_AstralShift'
            }
            new_entry.update(new_attrs)
            entries[word] = new_entry
            summary_changes.append(f"- **{word}**: Added new entry with meaning '{new_attrs['meaning']}'.")

    # Update version and date
    data['version'] = '10.1'
    data['date'] = datetime.datetime.now().isoformat()
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully wrote {output_path}")
    print("Changes made:")
    for change in summary_changes:
        print(change)

if __name__ == '__main__':
    update_dictionary()
