import json
import os
import re

# Configuration
RAW_DATA_PATH = 'data/eva_ivtff.txt'
DICTIONARY_PATH = 'results/dictionary/dictionary.json'
OUTPUT_REPORT_PATH = 'results/aries_analysis.md'
OUTPUT_SUMMARY_PATH = 'results/track-195-results_summary.md'

TARGET_PAGE_PREFIXES = ['<f70r', '<f71r']
TARGET_WORDS = ['ald', 'choly']

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_eva_text(path, page_prefixes):
    """
    Parses the EVA transcription file and extracts text for specified pages.
    Returns a list of objects: {'page': page_id, 'text': cleaned_text}
    """
    extracted_lines = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            
            # Check if line belongs to target pages
            # Line format: <f70r1.1,@Cc;H>	text...
            match = re.match(r'^<([^>]+)>\s+(.*)$', line)
            if match:
                page_id_full = match.group(1)
                text_content = match.group(2)
                
                # Check prefix
                is_target = False
                for prefix in page_prefixes:
                    # The prefix in the file includes '<', but page_id_full doesn't.
                    # My TARGET_PAGE_PREFIXES has '<', so I should check line start or adjust logic.
                    # Simpler: Check if the line starts with prefix
                    if line.startswith(prefix):
                        is_target = True
                        break
                
                if is_target:
                    # Clean text
                    # Remove comments <! ... >
                    text_content = re.sub(r'<![^>]+>', '', text_content)
                    # Remove non-text characters often found in EVA (%, !, ?, numbers if irrelevant)
                    # Keep letters, dots, spaces.
                    # Text is usually: "word.word.word"
                    text_content = re.sub(r'[^a-zA-Z0-9\.\s]', '', text_content)
                    
                    # Extract simple page ID (e.g., f70r1)
                    page_simple = page_id_full.split('.')[0]
                    
                    if text_content.strip():
                        extracted_lines.append({
                            'page': page_simple,
                            'full_id': page_id_full,
                            'text': text_content.strip()
                        })
    return extracted_lines

def find_occurrences(lines, target_words):
    hits = []
    for line_data in lines:
        text = line_data['text']
        # EVA uses '.' as word separator
        words = text.replace('.', ' ').split()
        
        found_targets = []
        for word in words:
            for target in target_words:
                if target in word:
                    found_targets.append(word)
        
        if found_targets:
            hits.append({
                'page': line_data['page'],
                'line_id': line_data['full_id'],
                'sentence': text,
                'found_words': list(set(found_targets)),
                'words_list': words
            })
    return hits

def analyze_sentence(hit, dictionary):
    modifiers = []
    verbs = []
    translations = []
    
    # Build a map of word -> meaning for quick lookup
    # Dictionary structure: { "word": { "meaning": "..." } }
    
    for word in hit['words_list']:
        meaning = dictionary.get(word, {}).get('meaning', None)
        
        # Modifiers: starts with 'o' + root in dictionary
        if word.startswith('o') and len(word) > 1:
            root = word[1:]
            root_meaning = dictionary.get(root, {}).get('meaning', None)
            if root_meaning:
                 modifiers.append(f"{word} -> {root_meaning} (adj?)")
            elif meaning: # If the word itself has meaning
                 modifiers.append(f"{word} ({meaning})")
        
        # Verbs: qok- prefix or ed/ee/dy endings or specific roots
        if word.startswith('qok') or word.endswith('dy') or word in ['ee', 'ed']:
            v_meaning = meaning if meaning else "Unknown Verb"
            verbs.append(f"{word} ({v_meaning})")

        if meaning:
            translations.append(f"{word}: {meaning}")
            
    return {
        'modifiers': modifiers,
        'verbs': verbs,
        'translations': translations
    }

def generate_report(hits, dictionary):
    lines = ["# Aries Section (f70r-f71r) Analysis: Nettle & Thistle\n"]
    lines.append(f"Target Words: {', '.join(TARGET_WORDS)}\n")
    lines.append(f"Pages Analyzed: f70r, f71r\n\n")
    
    lines.append(f"## Overview\nFound {len(hits)} lines containing target words.\n")
    
    for i, hit in enumerate(hits):
        analysis = analyze_sentence(hit, dictionary)
        
        lines.append(f"### {i+1}. Page {hit['page']} (Line: {hit['line_id']})")
        lines.append(f"**Text:** `{hit['sentence']}`")
        lines.append(f"**Targets:** {', '.join(hit['found_words'])}")
        
        if analysis['modifiers']:
            lines.append(f"- **Modifiers:** {'; '.join(analysis['modifiers'])}")
        
        if analysis['verbs']:
            lines.append(f"- **Verbs:** {'; '.join(analysis['verbs'])}")
            
        if analysis['translations']:
            lines.append(f"- **Vocabulary:** {'; '.join(analysis['translations'])}")
            
        lines.append("\n")
        
    return "\n".join(lines)

def generate_summary(hits):
    summary = "# Task 195 Results Summary\n\n"
    summary += "## Aries Analysis Results\n"
    summary += f"- **Total Occurrences:** {len(hits)}\n"
    summary += "- **Key Findings:**\n"
    summary += "    - Analysis of Nettle (`choly`) and Thistle (`ald`) contexts completed.\n"
    summary += "    - Detailed breakdown available in `results/aries_analysis.md`.\n"
    return summary

def main():
    print("Loading data...")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Error: {RAW_DATA_PATH} not found.")
        return
    if not os.path.exists(DICTIONARY_PATH):
        print(f"Error: {DICTIONARY_PATH} not found.")
        return
        
    dictionary = load_json(DICTIONARY_PATH)
    
    print("Parsing EVA text...")
    lines = parse_eva_text(RAW_DATA_PATH, TARGET_PAGE_PREFIXES)
    
    print(f"Scanned {len(lines)} lines from target pages.")
    
    print("Locating target words...")
    hits = find_occurrences(lines, TARGET_WORDS)
    
    print("Generating report...")
    report_content = generate_report(hits, dictionary)
    summary_content = generate_summary(hits)
    
    with open(OUTPUT_REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    with open(OUTPUT_SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write(summary_content)
        
    print(f"Analysis complete. Output saved to {OUTPUT_REPORT_PATH} and {OUTPUT_SUMMARY_PATH}")

if __name__ == "__main__":
    main()
