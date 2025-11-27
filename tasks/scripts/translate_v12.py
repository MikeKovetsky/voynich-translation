import json
import os
import re

def load_json(path):
    print(f"Loading {path}...")
    with open(path, 'r') as f:
        return json.load(f)

def translate_word(word, root_dict, word_clusters, word_to_root):
    # Clean word of non-alpha
    word = re.sub(r'[^a-zA-Z]', '', word)
    if not word: return ""

    # 1. Identify Root
    root = word_to_root.get(word)
    
    dict_entry = None
    if root and root in root_dict.get("roots", {}):
        dict_entry = root_dict["roots"][root]
    
    # 2. check for semantic category in dictionary
    dict_category = dict_entry.get("semantic_category") if dict_entry else None
    
    # 3. check for meanings in dictionary
    meanings = dict_entry.get("meanings", []) if dict_entry else []
    primary_meaning = meanings[0] if meanings else None
    is_weak_meaning = not primary_meaning or primary_meaning.startswith("*") or "unknown" in primary_meaning.lower() or "verb" in primary_meaning.lower()
    
    # 4. check cluster category
    cluster_data = word_clusters.get(word, {})
    cluster_category = cluster_data.get("predicted_category")
    cluster_conf = cluster_data.get("confidence", 0)
    
    if cluster_category == "Other" or cluster_conf < 0.4:
        cluster_category = None

    # Decision Logic
    
    # A. Strong Dictionary Meaning overrides everything?
    if primary_meaning and not is_weak_meaning:
        return f"**{primary_meaning}**" # Bold for known words
    
    # B. Semantic Category (Dictionary or Cluster)
    if dict_category:
        return f"[{dict_category}]"
    
    if cluster_category:
        return f"[{cluster_category}]"
        
    # C. Weak Dictionary Meaning
    if primary_meaning:
        clean = primary_meaning.replace("*", "")
        return f"_{clean}_" # Italic for weak/structural
        
    # D. Fallback
    return f"`{word}`"

def main():
    base_path = "/Users/mike/repos/voynych2"
    results_path = os.path.join(base_path, "results")
    tagged_text_path = os.path.join(base_path, "data/eva_ivtff.txt")
    root_dict_path = os.path.join(results_path, "root_dictionary_v3.json")
    clusters_path = os.path.join(results_path, "word_clusters.json")
    parsed_text_path = os.path.join(results_path, "parsed_text.json")
    
    if not os.path.exists(tagged_text_path):
        print(f"Error: {tagged_text_path} not found.")
        return

    root_dict = load_json(root_dict_path)
    word_clusters = load_json(clusters_path)
    
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
        print(f"Error: {e}")
        return

    print("Translating text...")
    translated_lines = []
    translated_lines.append("# Translation v12 (Grammar-First + Semantic Clustering)\n")
    
    current_page = ""
    
    with open(tagged_text_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Parse IVTFF format: <ID> text
            # Only process 'H' version (High-level / Hand?) or just picking one
            # ID example: <f1r.1,@P0;H>
            if line.startswith("<") and ";H>" in line:
                parts = line.split(">", 1)
                if len(parts) == 2:
                    label = parts[0] + ">"
                    content = parts[1].strip()
                    
                    # Extract page ID: f1r
                    match = re.search(r'<f(\d+[rv])', label)
                    page_id = match.group(1) if match else "Unknown"
                    
                    if page_id != current_page:
                        translated_lines.append(f"\n### Page {page_id}")
                        current_page = page_id
                    
                    # Process content
                    # Split by '.'
                    words = content.split(".")
                    translated_words = []
                    for w in words:
                        w = w.strip()
                        if not w: continue
                        
                        trans = translate_word(w, root_dict, word_clusters, word_to_root)
                        if trans:
                            translated_words.append(trans)
                    
                    if translated_words:
                        translated_lines.append(" ".join(translated_words))
    
    output_path = os.path.join(results_path, "translation_v12.md")
    with open(output_path, 'w') as f:
        f.write("\n".join(translated_lines))
    
    print(f"Saved translation to {output_path}")

if __name__ == "__main__":
    main()
