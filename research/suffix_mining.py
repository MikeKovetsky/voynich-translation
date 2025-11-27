import json
import re

def run_suffix_mining():
    print("Mining suffixes from corpus...")
    
    # Load Dictionary
    try:
        with open("results/dictionary/dictionary.json", "r") as f:
            dictionary = json.load(f)
            entries = dictionary.get("entries", dictionary)
    except:
        print("Error loading dictionary")
        return

    known_roots = set(entries.keys())
    
    # Load Corpus
    with open("data/eva_ivtff.txt", "r") as f:
        text = f.read()
    
    words = re.findall(r"[a-z]+", text.lower())
    unique_words = set(words)
    unknowns = [w for w in unique_words if w not in known_roots]
    
    suffixes = {
        "dy": " (adjectival/suffix)",
        "ol": " (derivative)",
        "y": " (imperative/action)",
        "m": " (plural/collective)",
        "in": " (diminutive?)"
    }
    
    new_entries = []
    
    for word in unknowns:
        for suffix, meaning_mod in suffixes.items():
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if stem in known_roots:
                    root_meaning = entries[stem].get("meaning", "unknown")
                    new_entries.append({
                        "word": word,
                        "root": stem,
                        "suffix": suffix,
                        "meaning": f"{root_meaning}{meaning_mod}",
                        "source": "Track251_SuffixMining"
                    })
                    break # Only match longest valid suffix
                    
    # Save
    with open("results/suffix_mining.json", "w") as f:
        json.dump(new_entries, f, indent=2)
        
    print(f"Found {len(new_entries)} suffix-derived candidates.")

if __name__ == "__main__":
    run_suffix_mining()
