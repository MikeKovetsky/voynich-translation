import json

dictionary_path = 'results/dictionary/dictionary.json'

with open(dictionary_path, 'r') as f:
    data = json.load(f)

print(f"Keys sample: {list(data.keys())[:10]}")
# print sample value
first_key = list(data.keys())[0]
print(f"Value for {first_key}: {data[first_key]}")
