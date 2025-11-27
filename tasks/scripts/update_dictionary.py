import json
import os
from collections import defaultdict, Counter

def load_json(path):
    print(f"Loading {path}...")
    with open(path, 'r') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    base_path = "/Users/mike/repos/voynych2/results"
    
    # Load inputs
    root_dict_path = os.path.join(base_path, "root_dictionary_v2.json")
    clusters_path = os.path.join(base_path, "word_clusters.json")
    parsed_text_path = os.path.join(base_path, "parsed_text.json")
    
    if not os.path.exists(clusters_path):
        print(f"Error: {clusters_path} not found.")
        return

    root_dict = load_json(root_dict_path)
    word_clusters = load_json(clusters_path)
    
    # Build word-to-root mapping
    print("Building word-to-root mapping...")
    word_to_root = {}
    try:
        with open(parsed_text_path, 'r') as f:
            parsed_data = json.load(f)
            for entry in parsed_data:
                original = entry.get("original")
                root = entry.get("root")
                if original and root:
                    word_to_root[original] = root
    except Exception as e:
        print(f"Error reading parsed_text.json: {e}")
        return
    
    print(f"Mapped {len(word_to_root)} unique words to roots.")

    # Analyze clusters
    root_categories = defaultdict(Counter)
    
    print("Analyzing clusters...")
    for word, data in word_clusters.items():
        category = data.get("predicted_category")
        confidence = data.get("confidence", 0)
        
        if not category or category == "Other" or confidence < 0.4:
            continue
            
        # Find root
        root = word_to_root.get(word)
        if not root:
            # Fallback: check root_dict source_words
            for r_key, r_val in root_dict.get("roots", {}).items():
                if word in r_val.get("source_words", []):
                    root = r_key
                    break
        
        if root:
            root_categories[root][category] += 1
    
    # Update dictionary
    print("Updating dictionary...")
    updated_roots_count = 0
    
    for root, counts in root_categories.items():
        most_common = counts.most_common(1)[0]
        category = most_common[0]
        count = most_common[1]
        total = sum(counts.values())
        
        if count / total >= 0.5:
            if "roots" in root_dict and root in root_dict["roots"]:
                entry = root_dict["roots"][root]
                entry["semantic_category"] = category
                updated_roots_count += 1
            elif root in word_to_root.values():
                # Root exists in text but not in dictionary. 
                # We could add it, but let's stick to updating existing for now 
                # as per "Update Dictionary" instruction which implies existing.
                # Actually, adding new roots with clear categories is good.
                pass

    root_dict["version"] = "1.1"
    if "stats" not in root_dict:
        root_dict["stats"] = {}
    root_dict["stats"]["roots_with_semantic_category"] = updated_roots_count
    
    output_path = os.path.join(base_path, "root_dictionary_v3.json")
    save_json(root_dict, output_path)
    print(f"Saved updated dictionary to {output_path}")
    print(f"Updated {updated_roots_count} roots with semantic categories.")

if __name__ == "__main__":
    main()
