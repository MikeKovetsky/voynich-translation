import json

def inspect_entries():
    with open('results/dictionary/dictionary.json', 'r') as f:
        data = json.load(f)
    
    keys = ['ald', 'choly', 'ol', 'o']
    for k in keys:
        if k in data['entries']:
            print(f"Entry {k}:")
            print(json.dumps(data['entries'][k], indent=2))
        else:
            print(f"Entry {k} not found in dictionary.json")

inspect_entries()
