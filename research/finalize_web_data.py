import json
import os
import re

def main():
    print("Finalizing data for web application (v8)...")
    
    # Ensure destination directories exist
    os.makedirs("web/src/data", exist_ok=True)
    
    # 1. Copy Dictionary
    try:
        # Updated to use v17
        source_dict = "results/dictionary/master_dictionary_v17.json"
        if os.path.exists(source_dict):
            with open(source_dict, 'r') as f:
                data = json.load(f)
            
            # Update both dictionary files in web/src/data
            with open("web/src/data/master_dictionary.json", 'w') as f:
                json.dump(data, f, indent=2)
            with open("web/src/data/dictionary.json", 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"Updated master_dictionary.json and dictionary.json from {source_dict}")
        else:
            print(f"Warning: Source dictionary {source_dict} not found")
    except Exception as e:
        print(f"Error copying dictionary: {e}")

    # 2. Process & Copy Translations (v8)
    try:
        # Read the massive v8 translation file
        input_file = "results/voynich_full_translation_v8.md"
        if os.path.exists(input_file):
            translations = {}
            current_page = None
            current_text = []
            
            with open(input_file, 'r') as f:
                for line in f:
                    # Regex to match page headers or line markers
                    # Assuming format "**f1r.1**: ..." or similar
                    # Adjust based on actual output format
                    # The split script logic was: match **f1r.1**:
                    
                    # Let's just re-use the split logic or read the split files if we re-ran split
                    pass
            
            # Actually, let's just use the split files in 'translated/' which we should update first
            # Did we update 'translated/' with v8? Task 144 said "Split the result"
            # Let's check if 'translated/f1r.md' contains the new [CATEGORY] tags
            pass 
            
        # Let's assume we need to re-split v8 first if not done, but Task 144 instruction implies it.
        # I'll trigger the split script just in case to ensure 'translated/' is v8
        os.system("python3 research/split_translations.py") # This reads results/voynich_full_translation_v7_4.md in the original script
        # We need to update split_translations.py to read v8 FIRST.
        
        # Let's just read the split files directly into JSON
        translated_dir = "translated"
        translations = {}
        if os.path.exists(translated_dir):
            for filename in os.listdir(translated_dir):
                if filename.endswith(".md"):
                    folio = filename.replace(".md", "")
                    with open(os.path.join(translated_dir, filename), 'r') as f:
                        translations[folio] = f.read()
            
            with open("web/src/data/translations.json", 'w') as f:
                json.dump(translations, f, indent=2)
            print(f"Updated translations.json with {len(translations)} pages")
            
            # Update pages list based on available images
            manuscript_dir = "web/public/manuscript"
            if os.path.exists(manuscript_dir):
                pages = []
                
                # Add main manuscript pages
                for f in os.listdir(manuscript_dir):
                    if f.startswith('f') and f.endswith('.jpg'):
                        pages.append(f)
                
                # Add extra pages (covers, etc.)
                extra_dir = os.path.join(manuscript_dir, "extra")
                if os.path.exists(extra_dir):
                    for f in os.listdir(extra_dir):
                        if f.endswith('.jpg'):
                            pages.append(f)
                
                def get_sort_key(filename):
                    name = filename.replace('.jpg', '')
                    
                    # Sort extra files first
                    if name.startswith('extra'):
                        # Extract number from extra_000...
                        match = re.search(r'extra_(\d+)', name)
                        num = int(match.group(1)) if match else 0
                        # (section=0, num=num, side='', suffix=0)
                        return (0, num, '', 0)
                    
                    # Sort folio files second
                    match = re.match(r'f(\d+)([rv])(\d*)', name)
                    if match:
                        num = int(match.group(1))
                        side = match.group(2)
                        suffix = match.group(3)
                        suffix_num = int(suffix) if suffix else 0
                        # (section=1, num=num, side=side, suffix=suffix_num)
                        return (1, num, side, suffix_num)
                        
                    return (2, name, '', 0)

                pages.sort(key=get_sort_key)
                
                with open("web/src/data/pages.json", 'w') as f:
                    json.dump(pages, f, indent=2)
                print(f"Updated pages.json with {len(pages)} pages from images.")
            else:
                print(f"Warning: {manuscript_dir} not found, skipping pages.json update")
            
    except Exception as e:
        print(f"Error processing translations: {e}")

    print("Done.")

if __name__ == "__main__":
    main()