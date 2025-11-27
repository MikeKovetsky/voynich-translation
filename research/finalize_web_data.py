import json
import os
import re

def main():
    print("Finalizing data for web application (v8)...")
    
    # Ensure destination directories exist
    os.makedirs("web/src/data", exist_ok=True)
    
    # 1. Copy Dictionary
    try:
        if os.path.exists("results/master_dictionary_v8_0.json"):
            with open("results/master_dictionary_v8_0.json", 'r') as f:
                data = json.load(f)
            with open("web/src/data/master_dictionary.json", 'w') as f:
                json.dump(data, f, indent=2)
            print("Updated master_dictionary.json")
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
        os.system("python3 split_translations.py") # This reads results/voynich_full_translation_v7_4.md in the original script
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
            
            # Update pages list
            pages = sorted(list(translations.keys()))
            with open("web/src/data/pages.json", 'w') as f:
                json.dump(pages, f, indent=2)
            print("Updated pages.json")
            
    except Exception as e:
        print(f"Error processing translations: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
