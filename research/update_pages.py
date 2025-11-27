import os
import json

files = sorted([f for f in os.listdir('images') if f.endswith('.jpg')])
# Sort naturally (f1, f2, ... f10 instead of f1, f10, f100)
def sort_key(f):
    name = f.replace('.jpg', '')
    num_part = ''.join(filter(str.isdigit, name))
    return int(num_part) if num_part else 0

files.sort(key=sort_key)

with open('web/src/data/pages.json', 'w') as f:
    json.dump(files, f, indent=2)
