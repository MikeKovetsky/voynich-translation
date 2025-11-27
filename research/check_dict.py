import json

with open('results/dictionary/dictionary.json', 'r') as f:
    data = json.load(f)
    print(f"or: {data.get('or')}")
    print(f"ol: {data.get('ol')}")
