import json

path = 'results/dictionary/master_dictionary_v16.json'
with open(path, 'r') as f:
    data = json.load(f)

entries = data.get('entries', {})
high_conf = 0
high_conf_with_meaning = 0

for k, v in entries.items():
    conf = v.get('confidence_level', '')
    meaning = v.get('meaning', '')
    if conf == 'HIGH' or conf == 'PROVEN':
        high_conf += 1
        if meaning:
            high_conf_with_meaning += 1
        else:
            print(f"No meaning: {k}")

print(f"Total entries: {len(entries)}")
print(f"High/Proven: {high_conf}")
print(f"High/Proven with meaning: {high_conf_with_meaning}")
