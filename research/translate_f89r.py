import json
import re
import os

def load_dictionary(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('entries', {})

def translate_text(text_file, dict_file, output_file):
    print("Loading dictionary...")
    dictionary = load_dictionary(dict_file)
    
    print("Reading text...")
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    translated_lines = []
    
    for line in lines:
        parts = line.strip().split(' ', 1)
        if len(parts) < 2:
            continue
            
        tag = parts[0]
        content = parts[1]
        
        # Tokenize by dot, space, or other punctuation
        # We keep the structure to reconstruct the sentence
        # But for translation we need clean words.
        
        # Strategy: Split by dots/spaces to get words, translate them, join back.
        # Note: The original text uses dots as separators often.
        
        words = re.split(r'[.\s]+', content)
        translated_words = []
        
        for word in words:
            # Clean word for lookup (remove !, ?, etc)
            clean_word = re.sub(r"[^a-zA-Z0-9]", "", word)
            
            meaning = ""
            entry = dictionary.get(clean_word)
            if entry:
                meaning = entry.get('meaning', '???')
            else:
                meaning = f"[{clean_word}]" # Unknown
                
            # Add confidence or other info if needed? For now just meaning.
            translated_words.append(meaning)
            
        translation = " ".join(translated_words)
        translated_lines.append({
            'tag': tag,
            'original': content,
            'translation': translation
        })

    print("Generating report...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Track 249: Pharma Translation Test (f89r)\n\n")
        f.write("## 1. Extracted Text & Translation\n\n")
        f.write("| Line | Original | Translation |\n")
        f.write("|------|----------|-------------|\n")
        
        for item in translated_lines:
            # Escape pipes in text
            orig = item['original'].replace("|", "\\|")
            trans = item['translation'].replace("|", "\\|")
            f.write(f"| {item['tag']} | `{orig}` | {trans} |\n")
            
        f.write("\n## 2. Instructional Logic Analysis\n\n")
        f.write("TODO: Analyze the translation above for recipe logic.\n")
        f.write("- Look for: \"Take [Ingredient]...\"\n")
        f.write("- Look for: \"Mix/Heat/Drink...\"\n")
        f.write("- Compare jar labels (lines with @Lc or @Lf usually labels?) with text.\n")

    print(f"Report saved to {output_file}")

if __name__ == "__main__":
    translate_text(
        "results/f89r_text.txt",
        "results/dictionary/dictionary.json",
        "results/pharma_translation_test.md"
    )
