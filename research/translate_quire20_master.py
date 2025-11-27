import json
import re
import os

# File paths
IVTFF_PATH = 'data/eva_ivtff.txt'
DICTIONARY_PATH = 'results/dictionary/dictionary_v9_3.json'
OUTPUT_TRANSLATION_PATH = 'results/quire20_translation_master.md'
OUTPUT_SUMMARY_PATH = 'results/track-204-results_summary.md'

# Special substitutions
SEMANTIC_SUBSTITUTIONS = {
    'choly': '[Mars Plant]',
    'ald': '[Thistle]',
    'os': '[Blue Star]',
    'ordaiin': '[Golden Extract]'
}

# Grammar Rules
PREFIX_MAP = {
    'ol': 'The',
    'ot': 'From',
    'ok': 'With'
}

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File {path} not found.")
        return {}

def parse_ivtff(path, start_page='f103r', end_page='f116v'):
    pages = {}
    
    # Quire 20 pages range
    start_num = int(re.search(r'\d+', start_page).group())
    end_num = int(re.search(r'\d+', end_page).group())
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('<'):
                continue
            
            # Extract page ID
            match = re.match(r'<f(\d+[rv])', line)
            if not match:
                continue
            
            page_id = 'f' + match.group(1)
            page_num = int(re.search(r'\d+', page_id).group())
            
            if not (start_num <= page_num <= end_num):
                continue
                
            if page_id not in pages:
                pages[page_id] = []
            
            # Format: <f103r.1,@P0;H> ...
            parts = line.split('>')
            if len(parts) < 2:
                continue
            
            header = parts[0] + '>'
            content = parts[1].strip()
            
            if not content:
                continue

            # Check for paragraph marker in header
            is_new_paragraph = '.P' in header or 'P0' in header # Heuristic for paragraph start

            # Extract line number
            line_num_match = re.search(r'\.(\d+)', header)
            line_num = int(line_num_match.group(1)) if line_num_match else 0
            
            # Extract transcriber
            transcriber = '?'
            if ';' in header:
                transcriber = header.split(';')[-1].replace('>', '')

            # Clean words
            # Remove comments {..}, etc.
            clean_content = re.sub(r'\{[^}]*\}', '', content)
            words = [w for w in clean_content.split('.') if w and w != '-' and not w.startswith('<')]
            
            pages[page_id].append({
                'line': line_num,
                'transcriber': transcriber,
                'words': words,
                'is_new_paragraph': is_new_paragraph
            })

    # Filter best transcription
    final_pages = {}
    for page_id, lines in pages.items():
        lines_by_num = {}
        for l in lines:
            ln = l['line']
            if ln not in lines_by_num:
                lines_by_num[ln] = []
            lines_by_num[ln].append(l)
        
        sorted_lines = []
        for ln in sorted(lines_by_num.keys()):
            versions = lines_by_num[ln]
            # Priority: H, C, F, N, U
            best = None
            for code in ['H', 'C', 'F', 'N', 'U']:
                for v in versions:
                    if v['transcriber'] == code:
                        best = v
                        break
                if best: break
            
            if not best and versions:
                best = versions[0]
                
            if best:
                sorted_lines.append(best)
        
        final_pages[page_id] = sorted_lines
        
    return final_pages

def apply_grammar_and_translate(word, dictionary_entries):
    # 1. Specific Substitutions (Highest Priority)
    if word in SEMANTIC_SUBSTITUTIONS:
        return SEMANTIC_SUBSTITUTIONS[word]
    
    # Explicit Fix for qokedy
    if word == 'qokedy':
        return "**Mix!**"

    # 2. Grammar Application (Prioritized over Dictionary for specific patterns)
    
    # Parse Prefix
    prefix = ""
    root = word
    suffix = ""
    
    # Check known prefixes
    # Sort by length to match longest prefix first (qok before qo)
    for p in sorted(list(PREFIX_MAP.keys()) + ['qok', 'qot', 'qo'], key=len, reverse=True):
        if word.startswith(p):
            # Ensure remaining part is substantial (heuristic)
            if len(word) > len(p) + 1: 
                prefix = p
                root = word[len(p):]
                break
    
    # Check Suffixes (-y, -dy)
    # Note: qokedy -> qok-ed-y. If we check dy first, we get e-dy.
    # Heuristic: If root ends in 'edy', treat as 'ed-y' if prefix is 'qo/qok'
    
    if prefix.startswith('qo') and root == 'edy':
         suffix = 'y'
         root = 'ed'
    elif root.endswith('dy'):
        suffix = 'dy'
        root = root[:-2]
    elif root.endswith('y'):
        suffix = 'y'
        root = root[:-1]
        
    # Rule: qok-ed-y -> Mix!
    if prefix.startswith('qo') and root == 'ed' and suffix == 'y':
        return "**Mix!**"
        
    # Rule: qok-[Verb]-y -> [Action]! (Imperative)
    if prefix.startswith('qo') and suffix == 'y':
        # Try to find root meaning
        root_meaning = "[Action]"
        if root in dictionary_entries:
             m = dictionary_entries[root].get('meaning')
             if m: root_meaning = m
        # Only apply if we found a meaning or if it looks like a verb structure
        if root_meaning != "[Action]" or (root == 'ed'):
             return f"**{root_meaning.title()}!**"

    # Rule: Particles (ol-, ot-, ok-)
    grammar_prefix = ""
    if prefix in PREFIX_MAP:
        grammar_prefix = PREFIX_MAP[prefix]
    
    if grammar_prefix:
        # Translate root
        translated_root = root
        if root in dictionary_entries:
             m = dictionary_entries[root].get('meaning')
             if m: translated_root = f"[{m}]"
        elif root in SEMANTIC_SUBSTITUTIONS:
             translated_root = SEMANTIC_SUBSTITUTIONS[root]
        
        # If we found a translation for the root, OR if the root is long enough to be a noun
        if translated_root != root:
             return f"{grammar_prefix} {translated_root}"
        # If root is unknown, we might still want to show structure: "The [unknown]"
        # But let's check if the full word is in dictionary first.
        
    # 3. Dictionary Lookup (Exact Match) - now fallback for non-grammar words
    if word in dictionary_entries:
        entry = dictionary_entries[word]
        # Check if meaning is valid
        if entry.get('meaning') and not entry['meaning'].startswith('unknown'):
             meaning = entry['meaning']
             if meaning.startswith("plant:"):
                 return f"[{meaning.split(':')[1].title()}]"
             return meaning

    # 4. Fallback for Particles if full word not in dictionary
    if grammar_prefix:
         return f"{grammar_prefix} [{root}]"

    # 5. Fallback: Dictionary Lookup for Root (if word not found, maybe root is)
    if root in dictionary_entries and root != word:
         m = dictionary_entries[root].get('meaning')
         if m: return f"[{m}]"

    return word

def main():
    print("Loading dictionary...")
    dictionary_data = load_json(DICTIONARY_PATH)
    dictionary_entries = dictionary_data.get('entries', {})
    
    print("Parsing IVTFF...")
    pages = parse_ivtff(IVTFF_PATH)
    print(f"Found {len(pages)} pages.")
    
    translation_output = []
    
    translation_output.append("# Task 204: Quire 20 Master Translation")
    translation_output.append(f"**Source:** {DICTIONARY_PATH}")
    translation_output.append("**Date:** 2025-11-27")
    translation_output.append("")
    
    processed_recipes = 0
    
    for page_id in sorted(pages.keys()):
        lines = pages[page_id]
        translation_output.append(f"## Folio {page_id}")
        translation_output.append("")
        
        current_recipe = []
        
        for line_data in lines:
            words = line_data['words']
            
            # Check for recipe break
            if line_data.get('is_new_paragraph', False) and current_recipe:
                # Finish previous recipe
                translation_output.append(f"**Recipe #{processed_recipes + 1}**")
                translation_output.append(" ".join(current_recipe))
                translation_output.append("")
                current_recipe = []
                processed_recipes += 1
            
            translated_line = []
            for word in words:
                trans = apply_grammar_and_translate(word, dictionary_entries)
                translated_line.append(trans)
            
            line_str = " ".join(translated_line)
            current_recipe.append(line_str)
        
        # Flush last recipe of page
        if current_recipe:
            translation_output.append(f"**Recipe #{processed_recipes + 1}**")
            translation_output.append(" ".join(current_recipe))
            translation_output.append("")
            processed_recipes += 1
            
        translation_output.append("---")
        translation_output.append("")

    print(f"Writing translation to {OUTPUT_TRANSLATION_PATH}...")
    with open(OUTPUT_TRANSLATION_PATH, 'w') as f:
        f.write("\n".join(translation_output))
        
    print("Generating summary...")
    summary = f"""# Task 204 Results Summary

## Overview
Comprehensive translation of Quire 20 (Recipes) using Dictionary v9.3 and Grammar v2.

## Statistics
- **Pages Processed:** {len(pages)} (f103r - f116v)
- **Recipes Identified:** {processed_recipes}
- **Dictionary Version:** v9.3

## Key Translations Applied
- **Imperatives:** `qok-ed-y` -> **Mix!**
- **Grammar Particles:** `ol-` (The), `ot-` (From), `ok-` (With)
- **Key Substitutions:**
  - `choly` -> [Mars Plant]
  - `ald` -> [Thistle]
  - `os` -> [Blue Star]
  - `ordaiin` -> [Golden Extract]

## Next Steps
- Review "Unknown" nouns in the translation.
- Correlate [Blue Star] recipes with Astro section.
"""
    with open(OUTPUT_SUMMARY_PATH, 'w') as f:
        f.write(summary)
        
    print("Done.")

if __name__ == "__main__":
    main()
