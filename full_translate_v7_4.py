#!/usr/bin/env python3
"""Full Manuscript Translation using Dictionary v7.4"""

import json
import re
from pathlib import Path
from collections import defaultdict
import voynich_data

DICTIONARY_FILE = "results/master_dictionary_v7_4.json"
OUTPUT_JSON = "results/full_translation_v7_4.json"
OUTPUT_MD = "results/voynich_full_translation_v7_4.md"

GRAMMAR = {
    "y-": {"meaning": "AND", "type": "prefix"},
    "sh-": {"meaning": "THAT", "type": "prefix"},
    "qok-": {"meaning": "IN", "type": "prefix"},
}

MORPHOLOGY = {
    "-dy": "ed", # Past tense
    "-y": "ing"  # Participle (simplified)
}

SECTIONS_MAP = {
    "herbal_a": "Herbal",
    "herbal_b": "Herbal",
    "astronomical": "Astro",
    "biological": "Bio",
    "pharmaceutical": "Pharma",
    "recipes": "Recipes"
}

def load_dictionary():
    print(f"Loading dictionary from {DICTIONARY_FILE}...")
    try:
        with open(DICTIONARY_FILE, 'r') as f:
            data = json.load(f)
            
        # Normalize dictionary structure
        entries = data
        metadata = {}
        if "entries" in data:
            entries = data["entries"]
            metadata = {k:v for k,v in data.items() if k != "entries"}
            
        return entries, metadata
    except FileNotFoundError:
        print(f"Error: Dictionary file {DICTIONARY_FILE} not found.")
        return {}, {}

def apply_grammar(word):
    """Apply grammar prefixes and suffixes."""
    meaning_parts = []
    current_word = word
    
    # Prefixes
    prefix_found = False
    for prefix, info in GRAMMAR.items():
        # Check for prefix (e.g. 'y' + word, but 'y' itself is a word)
        # The grammar keys are 'y-', 'sh-', 'qok-'.
        # We need to check if word starts with the prefix (minus hyphen) and is longer.
        p_clean = prefix.replace("-", "")
        if current_word.startswith(p_clean) and len(current_word) > len(p_clean):
            meaning_parts.append(info["meaning"])
            current_word = current_word[len(p_clean):]
            prefix_found = True
            break # Assuming only one prefix for now
            
    return prefix_found, meaning_parts, current_word

def strip_morphology(word):
    """Strip suffixes."""
    suffix_meaning = ""
    stem = word
    
    for suffix, replacement in MORPHOLOGY.items():
        s_clean = suffix.replace("-", "")
        if stem.endswith(s_clean) and len(stem) > len(s_clean):
            stem = stem[:-len(s_clean)]
            suffix_meaning = replacement
            break
            
    return stem, suffix_meaning

def translate_word(word, dictionary):
    """Translate a single word with grammar/morphology rules."""
    original = word
    
    # 1. Direct lookup
    if word in dictionary:
        return dictionary[word].get("meaning", "?"), dictionary[word].get("confidence", 0)
        
    # 2. Grammar prefixes
    has_prefix, prefix_meanings, stem = apply_grammar(word)
    
    if has_prefix:
        # Try looking up the stem
        if stem in dictionary:
            base_meaning = dictionary[stem].get("meaning", "?")
            full_meaning = " ".join(prefix_meanings + [base_meaning])
            return full_meaning, dictionary[stem].get("confidence", 0) * 0.9
            
    # 3. Morphology (Suffixes)
    # Try stripping suffix from original or stem
    check_word = stem if has_prefix else word
    base, suffix = strip_morphology(check_word)
    
    if suffix:
        if base in dictionary:
            base_meaning = dictionary[base].get("meaning", "?")
            # Construct meaning: AND EAT-ed -> AND EATed
            if has_prefix:
                full_meaning = " ".join(prefix_meanings + [f"{base_meaning}-{suffix}"])
            else:
                full_meaning = f"{base_meaning}-{suffix}"
            return full_meaning, dictionary[base].get("confidence", 0) * 0.8

    # 4. Prefix + Suffix combination (already handled sequentially above if strict)
    # but let's ensure we checked the stripped stem if we had a prefix.
    # (The logic above: apply prefix -> stem. Then strip suffix from stem -> base. Check base.)
    
    return "?", 0

def translate_line(text, dictionary):
    words = text.split(".")
    translations = []
    total_conf = 0
    found_count = 0
    
    for w in words:
        if not w: continue
        mean, conf = translate_word(w, dictionary)
        translations.append(mean)
        if mean != "?":
            total_conf += conf
            found_count += 1
            
    avg_conf = total_conf / len(words) if words else 0
    translation_text = " ".join(translations)
    
    return {
        "voynich": text,
        "translation": translation_text,
        "confidence": avg_conf,
        "found_count": found_count,
        "total_words": len(words)
    }

def main():
    dictionary, metadata = load_dictionary()
    print(f"Dictionary loaded: {len(dictionary)} entries")
    
    # Get all pages
    print("Loading manuscript pages...")
    pages = voynich_data.get_eva_pages() # Returns {folio: {loc: text}}
    
    # Organize by section
    section_folios = voynich_data.FOLIO_SECTIONS
    
    # Invert mapping for easy lookup
    folio_to_section = {}
    for sec, folios in section_folios.items():
        group = SECTIONS_MAP.get(sec, "Other")
        for f in folios:
            folio_to_section[f] = group
            
    # Translate
    results = defaultdict(list)
    stats = {"total_lines": 0, "translated_lines": 0, "total_words": 0, "translated_words": 0}
    
    print("Translating...")
    for folio, lines in pages.items():
        section = folio_to_section.get(folio, "Other")
        
        for loc, text in lines.items():
            # Clean text
            clean_text = re.sub(r'[!?,]', '.', text).strip()
            if not clean_text: continue
            
            trans_res = translate_line(clean_text, dictionary)
            
            res_entry = {
                "folio": folio,
                "loc": loc,
                "section": section,
                **trans_res
            }
            
            results[section].append(res_entry)
            
            stats["total_lines"] += 1
            stats["total_words"] += trans_res["total_words"]
            stats["translated_words"] += trans_res["found_count"]
            if trans_res["found_count"] > 0:
                stats["translated_lines"] += 1
                
    # Generate Markdown Report
    print(f"Generating report {OUTPUT_MD}...")
    with open(OUTPUT_MD, "w") as f:
        f.write("# Voynich Manuscript - Full Translation (v7.4)\n\n")
        f.write(f"**Date:** {metadata.get('date', 'Unknown')}\n")
        f.write(f"**Dictionary Size:** {len(dictionary)}\n")
        f.write(f"**Coverage:** {stats['translated_words']}/{stats['total_words']} words ({stats['translated_words']/stats['total_words']*100:.1f}%)\n\n")
        
        # Order: Herbal, Astro, Bio, Pharma, Recipes
        order = ["Herbal", "Astro", "Bio", "Pharma", "Recipes", "Other"]
        
        for sec in order:
            if sec not in results: continue
            
            section_data = results[sec]
            if not section_data: continue
            
            f.write(f"## {sec} Section\n\n")
            f.write("| Location | Voynich | Translation | Conf |\n")
            f.write("|----------|---------|-------------|------|\n")
            
            # Sort by location
            sorted_lines = sorted(section_data, key=lambda x: x["loc"])
            
            for line in sorted_lines:
                f.write(f"**{line['loc']}**: {line['translation']}\n")
                f.write(f"> `{line['voynich']}`\n\n")

    print("Done.")

if __name__ == "__main__":
    main()
