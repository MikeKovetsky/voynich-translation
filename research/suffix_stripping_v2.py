import json
import re
import os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_corpus(path):
    # Returns list of words from Takahashi (H) transcription
    words = set()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Expect format: <location> \t text
            parts = line.split('\t', 1)
            if len(parts) < 2:
                continue
            
            location = parts[0]
            text = parts[1]
            
            # Filter for Takahashi transcription (H)
            if ';H>' not in location:
                continue
            
            # Clean text
            # Remove inline comments/tags if any (though usually tags are at start)
            # Text uses . as separator
            # Also sometimes ,
            
            # Remove any <> tags in text if they exist
            text = re.sub(r'<[^>]+>', '', text)
            
            # Split by . and ,
            tokens = re.split(r'[.,]', text)
            
            for token in tokens:
                token = token.strip()
                # Basic validation: only allow EVA chars roughly (a-z, 0-9, ! etc)
                # Voynich words usually don't have spaces inside.
                if token:
                    words.add(token)
    return words

def main():
    corpus_path = 'data/eva_ivtff.txt'
    dictionary_path = 'results/dictionary/dictionary.json'
    output_path = 'results/suffix_mining.json'
    
    # Focus Suffixes
    suffixes = ['dy', 'ol', 'y', 'm']
    
    print(f"Loading dictionary from {dictionary_path}...")
    dictionary_data = load_json(dictionary_path)
    dictionary_entries = dictionary_data.get('entries', {})
    
    print(f"Loading corpus from {corpus_path}...")
    corpus_words = load_corpus(corpus_path)
    print(f"Found {len(corpus_words)} unique words in corpus (H transcription).")
    
    unknown_words = []
    for word in corpus_words:
        if word not in dictionary_entries:
            unknown_words.append(word)
            
    print(f"Found {len(unknown_words)} unknown words.")
    
    proposed_entries = {}
    
    for word in unknown_words:
        for suffix in suffixes:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if not stem: # empty stem
                    continue
                    
                if stem in dictionary_entries:
                    # Found a match!
                    stem_entry = dictionary_entries[stem]
                    stem_meaning = stem_entry.get('meaning', 'unknown')
                    
                    # Construct new entry
                    new_meaning = f"{stem_meaning} (modified)"
                    
                    # Logic to describe the entry
                    # If word already proposed by another suffix logic, we might overwrite or skip.
                    # Task implies simple mapping.
                    # If multiple suffixes match (e.g. 'dy' and 'y'), usually longer suffix is more specific.
                    # But here we iterate in order. 'dy' comes before 'y'.
                    # If 'dy' matches, we add it.
                    # Should we continue to 'y'? 
                    # Example: word "shedy". Stem "she" (known).
                    # Suffix 'y' -> stem "shed". If "shed" is also known.
                    # We might want both possibilities or just one.
                    # I will allow overwrite but prioritize order in list (so later ones overwrite earlier ones? Or first match wins?)
                    # If I want 'dy' to take precedence over 'y', I should check 'dy' first.
                    # If I find 'dy' match, and break, then 'dy' wins.
                    
                    proposed_entries[word] = {
                        "voynich": word,
                        "meaning": new_meaning,
                        "status": 1, # Proposed
                        "source": "Track251_SuffixStripping",
                        "derived_from": stem,
                        "suffix_stripped": suffix,
                        "original_meaning": stem_meaning
                    }
                    # Break here ensures we take the first matching suffix in our priority list
                    break 
                    
    print(f"Generated {len(proposed_entries)} proposed entries.")
    save_json(proposed_entries, output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
