import json
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
        return data.get('entries', {})

def lookup_word(word, dictionary):
    if word in dictionary:
        return dictionary[word]
    # Case insensitive check
    for k, v in dictionary.items():
        if k.lower() == word.lower():
            return v
    return {}

def main():
    dict_path = 'results/dictionary/master_dictionary_v16.json'
    dictionary = load_dictionary(dict_path)
    
    words_to_check = [
        'sol', 'adar', 'okal', 'shedy', 'okalshedy', 'sols', 'daro'
    ]
    
    results = {}
    for word in words_to_check:
        res = lookup_word(word, dictionary)
        results[word] = res
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
