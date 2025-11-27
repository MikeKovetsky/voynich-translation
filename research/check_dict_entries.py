import json
import os

dictionary_path = 'results/dictionary/dictionary.json'

if not os.path.exists(dictionary_path):
    print(f"Error: {dictionary_path} not found.")
    exit(1)

with open(dictionary_path, 'r') as f:
    data = json.load(f)

words_to_check = ['ol', 'o', 'qokeedy', 'qokedy', 'cheol']
found_words = {}

# The dictionary structure might be a list or a dict. I need to handle both or check first.
# Assuming it's a list of objects based on common dictionary structures, or a dict mapping words to definitions.
# Let's inspect the type of data first.

print(f"Type of data: {type(data)}")

if isinstance(data, dict):
    for word in words_to_check:
        if word in data:
            print(f"Current {word}: {data[word]}")
        else:
            print(f"{word} not found in keys.")
elif isinstance(data, list):
    # Assuming list of dicts with 'word' or 'voynich' key
    for entry in data:
        # Try to find the word key
        word_key = None
        if 'word' in entry:
            word_key = entry['word']
        elif 'voynich' in entry:
            word_key = entry['voynich']
        
        if word_key in words_to_check:
            print(f"Current {word_key}: {entry}")
            
