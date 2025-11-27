import json

dictionary_path = 'results/dictionary/dictionary.json'

with open(dictionary_path, 'r') as f:
    data = json.load(f)

entries = data.get('entries')
print(f"Type of entries: {type(entries)}")

if isinstance(entries, dict):
    words_to_check = ['ol', 'o', 'qokeedy', 'qokedy', 'cheol']
    for word in words_to_check:
        if word in entries:
            print(f"Current {word}: {entries[word]}")
        else:
            print(f"{word} not found in entries.")
elif isinstance(entries, list):
    print(f"Sample entry: {entries[0]}")
