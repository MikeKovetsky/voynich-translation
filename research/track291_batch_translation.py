import json
import re
from pathlib import Path
import sys
import os

# Add the current directory to sys.path to import voynich_data
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import voynich_data

# Configuration
TARGET_PAGES = ['f41r', 'f14v', 'f43r', 'f26r', 'f57r']
OUTPUT_TRANSLATION_FILE = Path("results/high_density_herbals_translation.md")
OUTPUT_SUMMARY_FILE = Path("results/track-291-results_summary.md")
DICTIONARY_FILE = Path("results/dictionary/master_dictionary_v15.json")

# Translation Rules
# qok- -> "Process/Cook"
# ol- -> "The [Ingredient]"
# -y -> "Imperative"
# sho -> "Burn/Heat"

def load_dictionary():
    if not DICTIONARY_FILE.exists():
        print(f"Warning: Dictionary file not found at {DICTIONARY_FILE}")
        return {}
    
    try:
        with open(DICTIONARY_FILE, 'r') as f:
            data = json.load(f)
            return data.get("entries", {})
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def translate_word(word, dictionary):
    """
    Apply simple recipe grammar translation rules and dictionary lookup.
    Returns a tuple (translated_word, is_ingredient, ingredient_text)
    """
    original_word = word
    translated = word # Start with original word
    is_ingredient = False
    ingredient_text = None
    
    is_imperative = False
    prefix_trans = None
    
    # Rule 1: qok- (Prefix)
    if word.startswith("qok"):
        prefix_trans = "**Process/Cook**"
    
    # Rule 4: sho (Whole word or prefix?)
    if word == "sho" or word.startswith("sho"):
        prefix_trans = "**Burn/Heat**"

    # Rule 3: -y (Suffix) -> "Imperative"
    if word.endswith("y") or word.endswith("9"): 
        is_imperative = True

    # Rule 2: ol- -> "The [Ingredient]"
    if word.startswith("ol"):
        ingredient = word[2:]
        if ingredient:
            prefix_trans = "The" # Actually handles the whole structure
            is_ingredient = True
            ingredient_text = ingredient
            # For ol-, we usually treat the rest as the ingredient name.
            
            term_display = f"**{ingredient}** [Ingredient]"
            
            # Check dictionary for ingredient
            if ingredient in dictionary:
                meaning = dictionary[ingredient].get("meaning", "")
                if meaning:
                    term_display += f" ({meaning})"
            
            translated = f"The {term_display}"
            if is_imperative:
                translated += " **[Imperative]**"
                
            return translated, is_ingredient, ingredient_text
        else:
            translated = "The"

    if word == "or":
        translated = "or"
        return translated, False, None

    # Dictionary Lookup for the core word (if not handled by ol-)
    # We need to strip prefixes/suffixes to find the root sometimes, but let's try exact match first.
    dict_meaning = ""
    if word in dictionary:
        dict_meaning = dictionary[word].get("meaning", "")
    
    # Construct Output
    # If we have a prefix translation (Process/Cook), we use that.
    # Else we use the word.
    
    if prefix_trans:
        # e.g. Process/Cook (qokedy)
        translated = f"{prefix_trans} ({word})"
    else:
        translated = word
        
    if dict_meaning:
        translated += f" ({dict_meaning})"
        
    if is_imperative:
        translated += " **[Imperative]**"
        
    return translated, is_ingredient, ingredient_text

def process_page(folio, dictionary):
    text_data = voynich_data.get_folio_text(folio, system='EVA')
    if not text_data:
        return None, []
    
    translated_lines = []
    all_ingredients = []
    
    # Sort lines by location
    sorted_locs = sorted(text_data.keys(), key=lambda x: float(x.split('.')[-1]) if '.' in x and x.split('.')[-1].isdigit() else 0)
    
    for loc in sorted_locs:
        line_text = text_data[loc]
        
        # Split by dots, hyphens, commas, whitespace
        words = [w for w in re.split(r'[.\-=,\s]+', line_text) if w]
        
        translated_words = []
        
        for i, word in enumerate(words):
            # Handle "words following or"
            is_after_or = False
            if i > 0 and words[i-1] == "or":
                is_after_or = True
            
            clean_word = word.replace('!', '').replace('?', '')
            
            trans, is_ing, ing_text = translate_word(clean_word, dictionary)
            
            if is_ing:
                all_ingredients.append(ing_text)
            elif is_after_or:
                # If previous word was "or", this is likely an ingredient
                term_display = f"**{clean_word}** [Ingredient]"
                if clean_word in dictionary:
                     meaning = dictionary[clean_word].get("meaning", "")
                     if meaning:
                         term_display += f" ({meaning})"
                
                trans = term_display
                all_ingredients.append(clean_word)
            
            translated_words.append(trans)
            
        translated_lines.append(f"**{loc}**: " + " ".join(translated_words))
        
    return "\n".join(translated_lines), all_ingredients

def main():
    print("Starting Batch Translation...")
    
    dictionary = load_dictionary()
    print(f"Loaded dictionary with {len(dictionary)} entries.")
    
    summary_content = "# Batch Translation Summary (Track 291)\n\n"
    summary_content += "## Common Ingredients Found\n\n"
    
    full_translation_content = "# High Density Herbals Translation\n\n"
    
    global_ingredients = {}
    
    for folio in TARGET_PAGES:
        print(f"Processing {folio}...")
        full_translation_content += f"## Page {folio}\n\n"
        
        translation, ingredients = process_page(folio, dictionary)
        
        if translation:
            full_translation_content += translation + "\n\n---\n\n"
            
            for ing in ingredients:
                global_ingredients[ing] = global_ingredients.get(ing, 0) + 1
        else:
            full_translation_content += "No text found.\n\n"
            
    # Generate Summary
    sorted_ingredients = sorted(global_ingredients.items(), key=lambda x: x[1], reverse=True)
    
    summary_content += "| Ingredient (EVA) | Count | Dictionary Meaning |\n"
    summary_content += "|---|---|---|\n"
    for ing, count in sorted_ingredients:
        meaning = ""
        if ing in dictionary:
            meaning = dictionary[ing].get("meaning", "-")
        else:
            meaning = "-"
        summary_content += f"| {ing} | {count} | {meaning} |\n" 
        
    # Write files
    with open(OUTPUT_TRANSLATION_FILE, 'w') as f:
        f.write(full_translation_content)
    
    with open(OUTPUT_SUMMARY_FILE, 'w') as f:
        f.write(summary_content)
        
    print(f"Done. \nTranslations: {OUTPUT_TRANSLATION_FILE}\nSummary: {OUTPUT_SUMMARY_FILE}")

if __name__ == "__main__":
    main()
