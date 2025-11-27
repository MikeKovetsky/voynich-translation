import json
import re

# Load markdown content
with open('translated/f1r.md', 'r') as f:
    content = f.read()

# Extract line IDs using regex
line_ids = re.findall(r'\*\*([a-z0-9]+\.\d+)\*\*:', content)

# Generate coordinates
# Distribute evenly for now since we don't have real boxes
# f1r typically has text blocks. We'll just stack them for the demo.
coords = {}
total_lines = len(line_ids)
start_top = 10  # Start at 10%
line_height = 80 / total_lines  # Distribute over 80% of height

for i, line_id in enumerate(line_ids):
    top = start_top + (i * line_height)
    coords[line_id] = {
        "top": f"{top:.1f}%",
        "left": "10%",
        "width": "80%"
    }

full_coords = {
    "f1r.jpg": coords
}

with open('web/src/data/coordinates.json', 'w') as f:
    json.dump(full_coords, f, indent=2)

print(f"Generated coordinates for {len(line_ids)} lines.")
