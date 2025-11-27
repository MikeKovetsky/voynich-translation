import json

def inspect_draft_entries():
    with open('results/dictionary_update_v10_draft.json', 'r') as f:
        data = json.load(f)
    
    keys = ['ol', 'o']
    for k in keys:
        if k in data:
            print(f"Draft Entry {k}:")
            print(json.dumps(data[k], indent=2))
        else:
            print(f"Draft Entry {k} not found")

inspect_draft_entries()
