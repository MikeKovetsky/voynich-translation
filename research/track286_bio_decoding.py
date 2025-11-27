
import json
import re
import os

# Constants
INPUT_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/dictionary/master_dictionary_v15.json"
OUTPUT_TRANS = "results/bio_section_translation_v1.md"
OUTPUT_SUMMARY = "results/track-286-results_summary.md"

TARGET_PAGES = ["f75r", "f76r", "f77r", "f78r"]

RECIPE_GRAMMAR = {
    "daiin": "Take",
    "dain": "Take", # Variant
    "sho": "Heat/Fire",
    "shol": "Heat/Fire", # Variant
    "shor": "Heat/Fire", # Variant
    "okora": "Cure/Solution",
    "okorar": "Cure/Solution", # Variant
    "okor": "Cure/Solution", # Root
    # Special rules implemented in code:
    # qok-* -> Mix/Process
    # ol-* -> The *
}

def load_dictionary(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Dictionary file {path} not found.")
        return {"entries": {}}

def parse_ivtff(path, pages):
    content = {}
    with open(path, 'r') as f:
        for line in f:
            # Match lines like <f75r.1,@P0;V>
            match = re.search(r'<((f\d+[rv])\.[^>]+);V>\s+(.*)', line)
            if match:
                full_ref = match.group(1)
                page = match.group(2)
                text = match.group(3)
                
                if page in pages:
                    if page not in content:
                        content[page] = []
                    content[page].append(text)
    return content

def clean_text(text):
    # Remove comments/tags like <...>
    text = re.sub(r'<[^>]+>', ' ', text)
    # Replace ! with space (uncertainty/null)
    text = text.replace('!', ' ')
    # Replace . with space (word separator)
    text = text.replace('.', ' ')
    # Replace , with space
    text = text.replace(',', ' ')
    # Collapse spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def translate_word(word, dictionary):
    # 1. Recipe Grammar Strict Rules
    if word in RECIPE_GRAMMAR:
        return f"**{RECIPE_GRAMMAR[word]}**"
    
    # 2. Morphology Rules
    if word.startswith("ol"):
        # Try to translate the stem
        stem = word[2:]
        if stem:
            stem_trans = translate_word(stem, dictionary)
            # Avoid double bolding if stem is bolded
            clean_stem = stem_trans.replace("**", "")
            return f"The {clean_stem}"
    
    if word.startswith("qok") or word.startswith("qo"):
        # Catch qokedy, qokain, etc.
        # Heuristic: if it starts with qok, it's likely a process verb in this context
        return "**Mix/Process**"

    # 3. Dictionary Lookup
    entries = dictionary.get("entries", {})
    if word in entries:
        meaning = entries[word].get("meaning")
        if meaning:
            return meaning
    
    # 4. Unknown
    return word

def generate_markdown(content, dictionary):
    output_lines = ["# Bio Section Translation (Q11)", ""]
    output_lines.append("Translation focused on 'Recipe Grammar' and Balneology context.\n")
    
    for page in TARGET_PAGES:
        if page not in content:
            continue
            
        output_lines.append(f"## Folio {page}")
        lines = content[page]
        
        for i, line in enumerate(lines):
            cleaned = clean_text(line)
            words = cleaned.split()
            translated_words = []
            for w in words:
                trans = translate_word(w, dictionary)
                translated_words.append(trans)
            
            # Interlinear format
            output_lines.append(f"> {cleaned}")
            output_lines.append(f"**TR:** {' '.join(translated_words)}")
            output_lines.append("")
            
    return "\n".join(output_lines)

def generate_summary(content, dictionary):
    # Analyze for balneology terms
    keywords = ["Water", "Bath", "Pool", "Women", "Skin", "Heat", "Mix", "Cure"]
    found_counts = {k: 0 for k in keywords}
    
    total_words = 0
    processed_words = 0
    
    for page in content:
        for line in content[page]:
            cleaned = clean_text(line)
            words = cleaned.split()
            for w in words:
                trans = translate_word(w, dictionary)
                total_words += 1
                if "**" in trans: # Count grammar matches
                     processed_words += 1
                
                # Check for keywords in translation
                trans_clean = trans.replace("**", "").lower()
                for k in keywords:
                    if k.lower() in trans_clean:
                        found_counts[k] += 1

    summary = ["# Track 286 Results Summary: Bio Section Decoding", ""]
    summary.append("## Hypothesis Verification")
    summary.append("Hypothesis: The Bio Section contains instructions for medicated baths (Balneology).")
    summary.append("")
    summary.append("## Key Findings")
    summary.append(f"- Analyzed Folios: {', '.join(TARGET_PAGES)}")
    summary.append(f"- Total Words Processed: {total_words}")
    summary.append(f"- Recipe Grammar Density: {processed_words/total_words:.1%}")
    summary.append("")
    summary.append("### Keyword Frequency")
    for k, v in found_counts.items():
        summary.append(f"- {k}: {v}")
    
    summary.append("")
    summary.append("## Conclusion")
    if found_counts["Mix"] > 10 and found_counts["Heat"] > 5:
        summary.append("The high frequency of processing terms ('Mix', 'Heat') supports the procedural nature of the text.")
        if found_counts["Bath"] > 0 or found_counts["Water"] > 0:
             summary.append("Presence of water-related terms supports the Balneology hypothesis.")
        else:
             summary.append("However, direct references to 'Bath' or 'Water' are scarce, suggesting implicit context or metaphorical imagery.")
    else:
        summary.append("The text structure is consistent with recipes, but specific balneological terms are not dominant.")
        
    return "\n".join(summary)

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary(DICT_FILE)
    
    print("Parsing transcription...")
    content = parse_ivtff(INPUT_FILE, TARGET_PAGES)
    
    print("Generating translation...")
    md_output = generate_markdown(content, dictionary)
    with open(OUTPUT_TRANS, 'w') as f:
        f.write(md_output)
    
    print("Generating summary...")
    summary_output = generate_summary(content, dictionary)
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write(summary_output)
        
    print("Done.")

if __name__ == "__main__":
    main()
