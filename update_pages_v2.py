import os
import json

# Scan the actual images directory
image_files = sorted([f for f in os.listdir('images') if f.endswith('.jpg')])

# Helper to sort naturally
def sort_key(f):
    name = f.replace('.jpg', '')
    num_part = ''.join(filter(str.isdigit, name))
    return int(num_part) if num_part else 0

image_files.sort(key=sort_key)

# Write to pages.json
with open('web/src/data/pages.json', 'w') as f:
    json.dump(image_files, f, indent=2)

print(f"Updated pages.json with {len(image_files)} pages.")
