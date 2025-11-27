
import json
import re
from voynich_data import get_section_text

# File paths
DICT_FILE = "results/master_dictionary_v7.json"
OUTPUT_MD = "results/recipe_translation_v2.md"

# Key vocabulary for selection
KEY_START = "daiin"
KEY_LEAF = "chol"
KEY_ROOT = "char"

# Known grammar/markers from the task description & progress summary
GRAMMAR_MARKERS = {
    "daiin": {"meaning": "TAKE/FROM", "type": "imperative/preposition"},
    "qok": {"meaning": "WITH/IN", "type": "instrumental_prefix"},
    "qokeey": {"meaning": "DRINK/BOIL", "type": "verb"},
    "aiin": {"meaning": "SPRING/SOURCE", "type": "noun"},
    "chol": {"meaning": "LEAF", "type": "noun"},
    "char": {"meaning": "ROOT", "type": "noun"},
    "shey": {"meaning": "AMOUNT/PART", "type": "noun"},
    "y": {"meaning": "AND/PLURAL", "type": "conjunction/suffix"},
    "l": {"meaning": "TO/FOR", "type": "prefix"},
    "o": {"meaning": "THE/EITHER", "type": "article/conjunction"},
    "ol": {"meaning": "THE", "type": "article"},
    "or": {"meaning": "FOR/BY", "type": "preposition"},
    "ar": {"meaning": "TO/AT", "type": "preposition"},
    "al": {"meaning": "THE/TO", "type": "article"}
}

def load_dictionary():
    """Load the master dictionary."""
    try:
        with open(DICT_FILE, 'r') as f:
            data = json.load(f)
            return data.get("entries", {})
    except FileNotFoundError:
        print(f"Error: {DICT_FILE} not found.")
        return {}

def get_recipe_candidates():
    """
    Extract recipe chunks from the recipes section.
    A recipe is defined as a block of text starting with 'daiin'.
    """
    # Get raw text for the recipes section (Quire 20)
    # voynich_data returns {folio: {line_loc: text}}
    recipes_data = get_section_text('recipes', 'EVA', 'H')
    
    all_lines = []
    # Flatten the structure to a list of (folio, line_loc, clean_words)
    # Sort by folio and line number to ensure order
    
    # Helper to parse line loc like "f103r.1"
    def parse_loc(loc_str):
        parts = loc_str.replace('f','').replace('r','.').replace('v','.').split('.')
        # handle potential different formats, though voynich_data usually gives "f103r.P.1" or similar
        # Let's look at what get_section_text returns. 
        # It uses get_folio_text which returns keys like "f116r.1" (from earlier read of translate_f116r.py)
        # The regex in get_folio_text was f116r\.(\d+)
        # But let's be safe.
        return loc_str

    sorted_folios = sorted(recipes_data.keys(), key=lambda x: (int(re.findall(r'\d+', x)[0]), x))
    
    for folio in sorted_folios:
        lines_dict = recipes_data[folio]
        # Sort lines within folio
        # keys are like "f103r.1", "f103r.2", etc.
        sorted_locs = sorted(lines_dict.keys(), key=lambda x: int(re.search(r'\.(\d+)', x).group(1)) if re.search(r'\.(\d+)', x) else 0)
        
        for loc in sorted_locs:
            text = lines_dict[loc]
            # Clean text: remove uncertain markers, comments
            clean_text = re.sub(r"[!?<>@$]", "", text)
            words = [w for w in re.split(r"[.\-=,\s]", clean_text) if w and len(w) > 1]
            all_lines.append({
                "folio": folio,
                "loc": loc,
                "words": words,
                "raw": text
            })

    # Group into recipes
    recipes = []
    current_recipe = []
    
    for line in all_lines:
        if not line["words"]:
            continue
            
        first_word = line["words"][0].lower()
        
        if first_word.startswith(KEY_START):
            # Start of a new recipe
            if current_recipe:
                recipes.append(current_recipe)
            current_recipe = [line]
        else:
            # Continuation of current recipe
            if current_recipe:
                current_recipe.append(line)
    
    # Append the last one
    if current_recipe:
        recipes.append(current_recipe)
        
    return recipes

def score_recipe(recipe):
    """
    Score a recipe based on presence of 'chol' and 'char' and length.
    """
    flat_words = [w.lower() for line in recipe for w in line["words"]]
    text = " ".join(flat_words)
    
    score = 0
    has_leaf = KEY_LEAF in flat_words
    has_root = KEY_ROOT in flat_words
    
    if has_leaf: score += 5
    if has_root: score += 5
    if has_leaf and has_root: score += 5 # Bonus for both
    
    # Prefer medium length recipes (not too short, not too long)
    length = len(flat_words)
    if 10 <= length <= 50:
        score += 2
        
    return score, has_leaf, has_root

def translate_word(word, dictionary):
    word_lower = word.lower()
    
    # Check local grammar markers first
    if word_lower in GRAMMAR_MARKERS:
        entry = GRAMMAR_MARKERS[word_lower]
        return f"**{entry['meaning']}**", "grammar"
        
    # specific prefixes check
    if word_lower.startswith("qok"):
        base = word_lower[3:]
        meaning = "WITH/IN"
        if base:
            base_trans, _ = translate_word(base, dictionary)
            return f"WITH-({base_trans})", "grammar_compound"
        return "**WITH/IN**", "grammar"

    if word_lower.startswith("l") and len(word_lower) > 2: # l- prefix
         base = word_lower[1:]
         if base in dictionary:
             base_trans = dictionary[base].get("meaning", "?")
             return f"TO-{base_trans}", "grammar_compound"

    # Check main dictionary
    if word_lower in dictionary:
        entry = dictionary[word_lower]
        meaning = entry.get("meaning", "?")
        return meaning.upper(), entry.get("domain", "vocab")
    
    return word, "unknown"

def translate_recipe(recipe, dictionary):
    translated_lines = []
    
    for line in recipe:
        words_trans = []
        for w in line["words"]:
            trans, cat = translate_word(w, dictionary)
            words_trans.append(trans)
        
        translated_lines.append({
            "loc": line["loc"],
            "voynich": " ".join(line["words"]),
            "english": " ".join(words_trans)
        })
        
    return translated_lines

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary()
    
    print("Extracting recipes...")
    recipes = get_recipe_candidates()
    print(f"Found {len(recipes)} potential recipe chunks starting with '{KEY_START}'.")
    
    # Score and filter
    scored_recipes = []
    for i, r in enumerate(recipes):
        score, has_leaf, has_root = score_recipe(r)
        scored_recipes.append({
            "index": i,
            "recipe": r,
            "score": score,
            "has_leaf": has_leaf,
            "has_root": has_root
        })
    
    # Sort by score descending
    scored_recipes.sort(key=lambda x: x["score"], reverse=True)
    
    # Select top 10
    top_10 = scored_recipes[:10]
    
    # Generate Output
    print("Translating and generating report...")
    
    with open(OUTPUT_MD, "w") as f:
        f.write("# Track 113: Recipe Translation v2\n\n")
        f.write("## Overview\n")
        f.write("Translation of 10 selected recipes from Quire 20, prioritizing those containing keys `chol` (Leaf) and `char` (Root).\n\n")
        f.write(f"- **Dictionary Version**: 7.0\n")
        f.write(f"- **Total Recipes Scanned**: {len(recipes)}\n\n")
        
        f.write("## Legend\n")
        f.write("- **BOLD** = High Confidence / Grammar\n")
        f.write("- UPPERCASE = Dictionary Match\n")
        f.write("- lower_case = Unknown\n\n")
        
        f.write("## Selected Recipes\n\n")
        
        for item in top_10:
            r_idx = item["index"]
            recipe = item["recipe"]
            score = item["score"]
            
            start_loc = recipe[0]["loc"]
            
            f.write(f"### Recipe #{r_idx + 1} (Start: {start_loc})\n")
            f.write(f"*Score: {score} (Leaf: {item['has_leaf']}, Root: {item['has_root']})*\n\n")
            
            translations = translate_recipe(recipe, dictionary)
            
            # Print line by line
            for t in translations:
                f.write(f"> **{t['loc']}**: {t['voynich']}\n")
                f.write(f"> -> {t['english']}\n>\n")
            
            f.write("\n---\n\n")

    print(f"Done. Output written to {OUTPUT_MD}")

if __name__ == "__main__":
    main()
