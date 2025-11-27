import json
import re
from pathlib import Path
import sys

# Add research directory to path to import voynich_data
sys.path.append(str(Path(__file__).parent))
from voynich_data import get_section_text, FOLIO_SECTIONS

# Configuration
DICT_FILE = Path("results/dictionary/dictionary.json")
OUTPUT_MD = Path("results/recipe_translations_v4.md")
OUTPUT_SUMMARY = Path("results/track-202-results_summary.md")

# Target words to find recipes
TARGET_WORDS = {"choly", "ald"}

# Semantic Overrides / New Knowledge
SEMANTIC_OVERRIDES = {
    "choly": "Mars Plant",
    "ordaiin": "Golden Extract",
    "ald": "Golden Extract",  
    "ol": "the",
    "or": "the", # or 'from'
    "ar": "of/from", # or 'earth'
    "daiin": "take",
    "dain": "take",
    "sain": "take",
    "tain": "take",
    "daiiin": "take", # variation
    "qok": "of", # preposition
}

def load_dictionary():
    if not DICT_FILE.exists():
        print(f"Warning: Dictionary file {DICT_FILE} not found.")
        return {}
    try:
        data = json.loads(DICT_FILE.read_text())
        entries = data.get("entries", data)
        simple_dict = {}
        for w, info in entries.items():
            if isinstance(info, dict):
                simple_dict[w] = info.get("meaning", "?")
            else:
                simple_dict[w] = str(info)
        return simple_dict
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def get_meaning(word, base_dict):
    if word in SEMANTIC_OVERRIDES:
        return SEMANTIC_OVERRIDES[word]
    return base_dict.get(word, None)

def parse_recipe_line(words, base_dict):
    translation_parts = []
    for i, w in enumerate(words):
        meaning = get_meaning(w, base_dict)
        if w.endswith("y") and not w.endswith("dy") and not meaning:
            root = w[:-1]
            root_meaning = get_meaning(root, base_dict)
            if root == "ed":
                translation_parts.append("[MIX!]")
            elif root_meaning:
                translation_parts.append(f"[{root_meaning}!(imp)]")
            else:
                translation_parts.append(f"[{w}!(imp)]")
        elif w.endswith("dy") and not meaning:
            root = w[:-2]
            root_meaning = get_meaning(root, base_dict)
            if root == "ed":
                translation_parts.append("[mixed]")
            elif root_meaning:
                translation_parts.append(f"[{root_meaning}(past)]")
            else:
                 translation_parts.append(f"[{w}(past)]")
        elif w.startswith("qok") and not meaning:
             translation_parts.append("of/with")
             rest = w[3:]
             rest_meaning = get_meaning(rest, base_dict)
             if rest_meaning:
                 translation_parts.append(f"[{rest_meaning}]")
             else:
                 translation_parts.append(f"[{rest}]")
        else:
            if meaning:
                translation_parts.append(f"[{meaning}]")
            else:
                translation_parts.append(f"[{w}]")
    return " ".join(translation_parts)

def check_logic(words, target_word):
    mix_roots = ["ed", "edy", "qoked"]
    context_actions = []
    for w in words:
        if any(r in w for r in mix_roots):
            context_actions.append("Mixing")
        if "fch" in w or "cfh" in w: 
             context_actions.append("Heating/Processing")
        if "yk" in w or "cph" in w:
             context_actions.append("Cutting")
        if "daiin" in w or "dain" in w:
             context_actions.append("Taking")

    if target_word == "choly":
        if any(a in ["Heating/Processing", "Cutting"] for a in context_actions):
            return f"PASS: Found {', '.join(set(context_actions) & {'Heating/Processing', 'Cutting'})}"
        return f"Uncertain: Found {', '.join(set(context_actions)) if context_actions else 'None'}"
        
    if target_word == "ald" or target_word == "ordaiin":
        if "Mixing" in context_actions:
             return "PASS: Found Mixing"
        return f"Uncertain: Found {', '.join(set(context_actions)) if context_actions else 'None'}"
        
    return "N/A"

def get_multi_transcriber_data(sections):
    """
    Get text from specified sections across multiple transcribers.
    Returns a list of items: {loc, folio, transcriber, text}
    """
    transcribers = ['H', 'C', 'F', 'U', 'm', 'G'] # G is extra
    all_data = []
    
    # We need to patch voynich_data logic slightly or just loop
    # Since voynich_data filters strict matches, and get_eva_pages reads the whole file once?
    # No, get_eva_pages reads file each time with lru_cache?
    # Actually get_eva_pages is cached but the arg changes.
    
    for section in sections:
        folios = FOLIO_SECTIONS.get(section, [])
        for tr in transcribers:
            try:
                # We can't easily use get_section_text because it returns {folio: {loc: text}}
                # We want to check all transcribers.
                # Note: get_section_text calls get_folio_text calls get_eva_pages(tr).
                # This might be slow to reload for each transcriber?
                # get_eva_pages reads the raw file (cached) then filters.
                # The filter is fast.
                
                data = get_section_text(section, system='EVA', transcriber=tr)
                for folio, lines in data.items():
                    for loc, text in lines.items():
                        all_data.append({
                            "section": section,
                            "folio": folio,
                            "location": loc,
                            "transcriber": tr,
                            "text": text
                        })
            except Exception as e:
                # Ignore errors (e.g. G not supported if validation exists, or empty results)
                continue
                
    return all_data

def main():
    print("Starting Task 202: Recipe Decoding II (Extended Search)")
    
    # 1. Load Data
    base_dict = load_dictionary()
    print(f"Loaded dictionary with {len(base_dict)} entries")
    
    # Search in Recipes and Pharmaceutical
    sections_to_search = ['recipes', 'pharmaceutical']
    print(f"Scanning sections: {sections_to_search} across transcribers H, C, F, U, m, G...")
    
    raw_data = get_multi_transcriber_data(sections_to_search)
    print(f"Loaded {len(raw_data)} lines of text.")
    
    results = []
    seen_locs = set() # avoid duplicates if multiple transcribers have same text? 
    # Actually we want to find the TARGET word. If H misses it but G has it, we want G.
    # If both have it, maybe just pick one (H preferred).
    
    candidates = []
    
    for item in raw_data:
        text = item["text"]
        text_clean = re.sub(r'[!?<>@$\d]', '', text)
        words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 1]
        
        target_found = None
        for w in words:
            if w in TARGET_WORDS:
                target_found = w
                break
        
        if target_found:
            candidates.append({
                "item": item,
                "words": words,
                "target": target_found
            })
            
    # Deduplicate: Group by location. If multiple transcribers match, pick H > m > others.
    grouped = {}
    for c in candidates:
        loc = c["item"]["location"]
        if loc not in grouped:
            grouped[loc] = []
        grouped[loc].append(c)
        
    print(f"Found {len(grouped)} unique locations with target words.")
    
    final_results = []
    priority = {'H': 0, 'm': 1, 'C': 2, 'F': 3, 'U': 4, 'G': 5}
    
    for loc, group in grouped.items():
        # Sort by priority
        group.sort(key=lambda x: priority.get(x["item"]["transcriber"], 99))
        best = group[0]
        
        translation = parse_recipe_line(best["words"], base_dict)
        logic_result = check_logic(best["words"], best["target"])
        
        final_results.append({
            "folio": best["item"]["folio"],
            "location": loc,
            "transcriber": best["item"]["transcriber"],
            "original": best["item"]["text"],
            "translation": translation,
            "target": best["target"],
            "logic_check": logic_result
        })

    # 3. Generate Output
    md_lines = []
    md_lines.append("# Recipe Translations v4 (Task 202)")
    md_lines.append("")
    md_lines.append("## Summary")
    md_lines.append(f"Targeting recipes/pharma containing: {', '.join(TARGET_WORDS)}")
    md_lines.append(f"Sections searched: {', '.join(sections_to_search)}")
    md_lines.append(f"Found **{len(final_results)}** matching lines.")
    md_lines.append("")
    
    md_lines.append("## Translations")
    md_lines.append("")
    
    # Group by Target
    for target in TARGET_WORDS:
        target_results = [r for r in final_results if r["target"] == target]
        if not target_results:
            continue
            
        md_lines.append(f"### Target: `{target}`")
        md_lines.append("")
        
        for r in target_results:
            md_lines.append(f"**{r['location']}** ({r['transcriber']})")
            md_lines.append(f"- Original: `{r['original']}`")
            md_lines.append(f"- Translation: {r['translation']}")
            md_lines.append(f"- Logic Check: *{r['logic_check']}*")
            md_lines.append("")
            
    OUTPUT_MD.write_text("\n".join(md_lines))
    print(f"Written {OUTPUT_MD}")
    
    # Summary File
    summary_lines = []
    summary_lines.append("# Task 202 Results Summary")
    summary_lines.append("")
    summary_lines.append("## Overview")
    summary_lines.append(f"Successfully re-translated {len(final_results)} recipe/pharma lines containing target keywords.")
    summary_lines.append("")
    summary_lines.append("## Key Findings")
    
    pass_count = sum(1 for r in final_results if "PASS" in r["logic_check"])
    summary_lines.append(f"- Logic Verification: {pass_count}/{len(final_results)} passed the context check.")
    
    if pass_count == 0:
        summary_lines.append("- Note: 'PASS' criteria might be strict or context words missing from dictionary.")

    OUTPUT_SUMMARY.write_text("\n".join(summary_lines))
    print(f"Written {OUTPUT_SUMMARY}")

if __name__ == "__main__":
    main()
