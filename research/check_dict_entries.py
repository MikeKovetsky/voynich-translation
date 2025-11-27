import json

try:
    with open("results/dictionary/dictionary_v10_0.json", "r") as f:
        data = json.load(f)

    print("aiin:", json.dumps(data["entries"].get("aiin"), indent=2))
    print("daiin:", json.dumps(data["entries"].get("daiin"), indent=2))
except Exception as e:
    print(e)
