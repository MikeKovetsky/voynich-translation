import json
import os
import shutil

def main():
    print("Preparing data for web application...")
    
    # Ensure destination directories exist
    os.makedirs("web/src/data", exist_ok=True)
    
    # Copy translations
    try:
        # Convert markdown splits into a single JSON for the web app
        translations = {}
        translated_dir = "translated"
        
        if os.path.exists(translated_dir):
            for filename in os.listdir(translated_dir):
                if filename.endswith(".md"):
                    folio = filename.replace(".md", "")
                    with open(os.path.join(translated_dir, filename), 'r') as f:
                        translations[folio] = f.read()
            
            with open("web/src/data/translations.json", 'w') as f:
                json.dump(translations, f, indent=2)
            print("Generated translations.json")
        else:
            print(f"Warning: {translated_dir} directory not found")
            
    except Exception as e:
        print(f"Error processing translations: {e}")

    # Copy pages structure (if available or generate basic)
    try:
        # Basic page list from translations
        pages = sorted(list(translations.keys()))
        with open("web/src/data/pages.json", 'w') as f:
            json.dump(pages, f, indent=2)
        print("Generated pages.json")
    except Exception as e:
        print(f"Error generating pages.json: {e}")

    # Copy manuscript data (Knowledge Graph)
    try:
        if os.path.exists("results/voynich_knowledge_graph.json"):
            shutil.copy("results/voynich_knowledge_graph.json", "web/src/data/knowledge_graph.json")
            print("Copied knowledge_graph.json")
    except Exception as e:
        print(f"Error copying knowledge graph: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
