import json
import os

def inspect_file(filepath):
    print(f"Inspecting {filepath}...")
    if not os.path.exists(filepath):
        print("File not found.")
        return

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, list):
            print(f"Type: List with {len(data)} items")
            if len(data) > 0:
                print("Sample item:", json.dumps(data[0], indent=2))
                # Check for page keys in a few items
                pages = set()
                for item in data[:100]:
                    if 'page' in item:
                        pages.add(item['page'])
                print(f"Found pages in first 100 items: {list(pages)}")
                
                # Check for 'o-' words in verb_morphology if that's the file
                if 'verb' in filepath:
                     o_words = [item['original'] for item in data if item.get('original', '').startswith('o')]
                     print(f"Found {len(o_words)} words starting with 'o'")
                     print(f"Sample o-words: {o_words[:5]}")

        elif isinstance(data, dict):
            print(f"Type: Dict with keys: {list(data.keys())[:10]}")
            # Check content of first key
            first_key = list(data.keys())[0]
            print(f"Sample content for key '{first_key}':", str(data[first_key])[:200])
            
    except Exception as e:
        print(f"Error reading file: {e}")

inspect_file('results/parsed_text.json')
print("-" * 20)
inspect_file('results/verb_morphology.json')
