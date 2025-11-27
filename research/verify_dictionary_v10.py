import json

def verify_updates():
    with open('results/dictionary/dictionary.json', 'r') as f:
        data = json.load(f)
    
    entries = data['entries']
    
    # Verify version
    print(f"Version: {data.get('version')}")
    
    # Verify overrides
    print("\nVerifying overrides:")
    for k in ['ald', 'choly']:
        if k in entries:
            print(f"{k}: humoral_quality = {entries[k].get('humoral_quality')}")
    
    for k in ['ol', 'o']:
        if k in entries:
            print(f"{k}: type = {entries[k].get('type')}, category = {entries[k].get('category')}")

verify_updates()
