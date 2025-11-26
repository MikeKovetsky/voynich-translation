import json

try:
    with open("results/master_dictionary_v6.json", "r") as f:
        data = json.load(f)
        print(f"Keys: {list(data.keys())}")
        if "entries" in data:
            print(f"Sample entry: {list(data['entries'].items())[0]}")
        elif "words" in data:
            print(f"Sample entry: {list(data['words'].items())[0]}")
        else:
            # Maybe it's a direct map?
            print(f"Sample entry: {list(data.items())[0]}")
except Exception as e:
    print(e)
