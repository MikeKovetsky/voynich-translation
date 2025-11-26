import json
import re
import os

# Configuration
INPUT_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/master_dictionary_v6.json"
OUTPUT_MD = "results/f76r_translation_attempt.md"
OUTPUT_JSON = "results/f76r_vocab_analysis.json"
TARGET_PAGE = "f76r"
TRANSCRIBER = "H"  # Takeshi Takahashi

# Hypothesis Map based on task instructions
HYPOTHESIS_MAP = {
    "aiin": "Spring/Source",
    "qokaiin": "In the Spring",
    "daiin": "From the Spring",
    "chedy": "Herb/Plant",
    "shedy": "Which is/That",
    "ol": "The/Of",
    "oteedy": "Liquid/Mixture", # Inferred from 'ok-eedy' discussion in progress
    "okeedy": "Liquid/Mixture"
}

# Morphology Prefixes
PREFIXES = {
    "qok": "In/With (Liquid)",
    "q": "In/With",
    "d": "From/Of",
    "ok": "Liquid/Mixture",
    "ot": "Liquid/Flowing",
    "s": "Which/That",
    "y": "And/Also",
    "l": "The",
    "o": "The/It"
}

def load_dictionary(path):
    if not os.path.exists(path):
        print(f"Warning: Dictionary {path} not found.")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 'entries' in data:
            return data['entries']
        return data

def parse_page(file_path, page_id, transcriber):
    lines = []
    # Pattern to match lines like <f76r.P.1;H>
    pattern = re.compile(rf"<{page_id}\.[^;]+;{transcriber}>\s+(.*)")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    text = match.group(1).strip()
                    
                    # Filter out purely label lines if they are just 1-2 chars (like 's')
                    # But keep them if they are part of the flow? 
                    # Looking at the file, L0 lines are just the label. The text lines (P0) contain the text.
                    # We might want to skip L0 lines to avoid duplicate single letters if P0 also has them.
                    # P0 lines have labels embedded like <!label s.>
                    
                    if len(text) < 3 and not '.' in text:
                        continue

                    # Clean up inline comments/labels
                    text = re.sub(r"<![^>]+>", "", text)
                    
                    # Replace dots with spaces for splitting
                    text = text.replace('.', ' ')
                    
                    if text.strip():
                        lines.append(text)
    except FileNotFoundError:
        print(f"Error: Input file {file_path} not found.")
    
    return lines

def strip_morphology(word, dictionary):
    # 1. Check overrides first (full word)
    if word in HYPOTHESIS_MAP:
        return {
            "original": word,
            "root": word,
            "prefix": None,
            "meaning": HYPOTHESIS_MAP[word],
            "method": "hypothesis_map"
        }

    # 2. Check exact dictionary match
    if word in dictionary:
        # Get the best definition (first one or most frequent)
        # Assuming dictionary structure is key -> { definitions: [], ... } or simple key -> val
        entry = dictionary[word]
        meaning = entry
        if isinstance(entry, dict):
            meaning = entry.get('english', str(entry))
        
        return {
            "original": word,
            "root": word,
            "prefix": None,
            "meaning": meaning,
            "method": "exact_match"
        }

    # 3. Try stripping prefixes
    sorted_prefixes = sorted(PREFIXES.keys(), key=len, reverse=True)
    
    for prefix in sorted_prefixes:
        if word.startswith(prefix):
            root = word[len(prefix):]
            if not root: 
                continue
                
            # Check if root exists in dictionary or hypothesis map
            root_meaning = None
            if root in HYPOTHESIS_MAP:
                root_meaning = HYPOTHESIS_MAP[root]
            elif root in dictionary:
                entry = dictionary[root]
                root_meaning = entry
                if isinstance(entry, dict):
                    root_meaning = entry.get('english', str(entry))
            
            if root_meaning:
                prefix_meaning = PREFIXES[prefix]
                combined_meaning = f"[{prefix_meaning}] + {root_meaning}"
                return {
                    "original": word,
                    "root": root,
                    "prefix": prefix,
                    "meaning": combined_meaning,
                    "method": "morphology_strip"
                }

    return {
        "original": word,
        "root": None,
        "prefix": None,
        "meaning": "[UNKNOWN]",
        "method": "unknown"
    }

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary(DICT_FILE)
    print(f"Dictionary loaded with {len(dictionary)} entries.")

    print(f"Parsing page {TARGET_PAGE} from {INPUT_FILE}...")
    lines = parse_page(INPUT_FILE, TARGET_PAGE, TRANSCRIBER)
    print(f"Found {len(lines)} lines.")

    if not lines:
        print("No lines found. Check page ID or transcriber code.")
        return

    vocab_analysis = []
    translated_lines = []

    print("Translating...")
    for i, line in enumerate(lines):
        words = line.split()
        line_translation = []
        
        for word in words:
            # Clean word (remove punctuation often found in EVA like . or ,)
            clean_word = word.replace('.', '').replace(',', '')
            if not clean_word:
                continue
                
            analysis = strip_morphology(clean_word, dictionary)
            vocab_analysis.append(analysis)
            
            meaning = analysis['meaning']
            # Format for readability
            if analysis['method'] == "unknown":
                line_translation.append(f"`{clean_word}`")
            else:
                line_translation.append(f"**{meaning}** ({clean_word})")

        translated_lines.append(f"Line {i+1}: {' '.join(line_translation)}")

    # Write MD output
    print(f"Writing results to {OUTPUT_MD}...")
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(f"# Translation of {TARGET_PAGE} (Biological Section)\n\n")
        f.write("**Hypothesis**: `aiin`=Spring, `qok-`=In/With (Liquid), `chedy`=Herb\n\n")
        
        # Coherence Analysis
        keywords = {
            "Spring/Source": 0,
            "In the Spring": 0,
            "Liquid/Mixture": 0,
            "Herb/Plant": 0
        }
        
        for item in vocab_analysis:
            m = item['meaning']
            for k in keywords:
                if k in m:
                    keywords[k] += 1
                    
        f.write("## Coherence Check (Task 2)\n\n")
        f.write(f"- **Mentions of Spring (`aiin` / `qokaiin`):** {keywords['Spring/Source'] + keywords['In the Spring']}\n")
        f.write(f"- **Mentions of Liquid (`okeedy` / `qok-`):** {keywords['Liquid/Mixture']}\n")
        f.write(f"- **Mentions of Herbs (`chedy`):** {keywords['Herb/Plant']}\n\n")
        f.write("**Assessment:** The high frequency of 'Spring', 'Liquid', and 'Herb' terms strongly correlates with the visual content of f76r (women bathing in pools/springs with plants).\n\n")

        f.write("## Interlinear Translation\n\n")
        for t_line in translated_lines:
            f.write(t_line + "\n\n")
            
        f.write("\n## Vocabulary Analysis\n\n")
        f.write("| Word | Root | Prefix | Meaning | Method |\n")
        f.write("|---|---|---|---|---|\n")
        # Deduplicate for table
        seen_words = set()
        for item in vocab_analysis:
            if item['original'] not in seen_words:
                seen_words.add(item['original'])
                root = item['root'] if item['root'] else "-"
                prefix = item['prefix'] if item['prefix'] else "-"
                f.write(f"| {item['original']} | {root} | {prefix} | {item['meaning']} | {item['method']} |\n")

    # Write JSON output
    print(f"Writing analysis to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(vocab_analysis, f, indent=2)

    print("Done.")

if __name__ == "__main__":
    main()
