import json
import re
import os
from collections import defaultdict

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def translate_word(word, dictionary, specific_rules):
    # specific rules
    if word in specific_rules:
        return specific_rules[word]
    
    # Check for qok-ed-y variants specifically
    if word == 'qokeody':
        return 'Process!'
    if word == 'ordaiin':
        return 'Golden Extract'
    if word == 'os':
        return 'Star'
        
    # dictionary lookup
    if word in dictionary:
        return dictionary[word].get('meaning', word)
    
    return word

def main():
    # Paths
    translations_path = 'web/src/data/translations.json'
    dictionary_path = 'results/dictionary/dictionary.json'
    
    # Load data
    translations = load_json(translations_path)
    dictionary_data = load_json(dictionary_path)
    dictionary = dictionary_data.get('entries', {})
    
    # Specific rules from task
    specific_rules = {
        'os': 'Star',
        'ordaiin': 'Golden Extract',
        'qokeody': 'Process!',
    }
    
    # Target pages: f67r to f73v
    astro_pages = []
    for key in translations:
        if re.match(r'f(6[7-9]|7[0-3])[rv]', key):
            astro_pages.append(key)
            
    astro_pages.sort()
    
    translated_output = []
    
    # Analysis counters
    star_count = 0
    process_count = 0
    golden_extract_count = 0
    total_words = 0
    
    # Debug: collect all qok words
    qok_words = defaultdict(int)
    os_words = defaultdict(int)
    
    for page in astro_pages:
        page_content = translations[page]
        translated_output.append(f"# Page {page}\n")
        
        lines = page_content.split('\n')
        for line in lines:
            if line.startswith('> `'):
                match = re.search(r'> `([^`]+)`', line)
                if match:
                    voynich_text = match.group(1)
                    # Split by dots and spaces
                    words = re.split(r'[.\s]+', voynich_text)
                    words = [w for w in words if w] 
                    
                    line_translation = []
                    
                    for word in words:
                        total_words += 1
                        
                        # Debug collection
                        if word.startswith('qok'):
                            qok_words[word] += 1
                        if word.startswith('os'):
                            os_words[word] += 1
                            
                        trans = translate_word(word, dictionary, specific_rules)
                        
                        if trans == 'Star':
                            star_count += 1
                        elif trans == 'Process!':
                            process_count += 1
                        elif trans == 'Golden Extract':
                            golden_extract_count += 1
                        
                        line_translation.append(trans)
                        
                    translated_line = ' '.join(line_translation)
                    translated_output.append(f"- Original: {voynich_text}")
                    translated_output.append(f"- Translated: {translated_line}\n")
    
    print("Analysis Debug:")
    print(f"Qok words found: {dict(qok_words)}")
    print(f"Os words found: {dict(os_words)}")
    
    # Write translation output
    save_file('results/translation_astro.md', '\n'.join(translated_output))
    
    # Generate Analysis (Astro Logic)
    logic_content = [
        "# Astro-Alchemy Logic Analysis",
        "",
        f"## Statistics",
        f"- Total Words processed: {total_words}",
        f"- Occurrences of 'Star' (os): {star_count}",
        f"- Occurrences of 'Process!' (qok-ed-y): {process_count}",
        f"- Occurrences of 'Golden Extract' (ordaiin): {golden_extract_count}",
        "",
        "## Structural Analysis",
        "Based on the frequency and placement of these terms:",
    ]
    
    if star_count > 0:
         logic_content.append(f"- 'Star' (os) appears {star_count} times.")
    else:
         logic_content.append("- 'Star' (os) does not appear explicitly as a standalone word.")

    if process_count > 0:
        logic_content.append("- 'Process!' (qokeody) appears, suggesting active instruction.")
    else:
        logic_content.append("- 'Process!' (qokeody) is absent. This might indicate this section is descriptive rather than instructional (recipe-based).")
    
    if golden_extract_count > 0:
         logic_content.append(f"- 'Golden Extract' appears {golden_extract_count} times.")
    else:
         logic_content.append("- 'Golden Extract' (ordaiin) is absent.")
         
    # Check if other star-related words appear (from os_words)
    if len(os_words) > 0:
        logic_content.append("\n### Star Variants")
        logic_content.append(f"Other words starting with 'os': {', '.join(list(os_words.keys()))}")
        logic_content.append("These may be variations of 'Star' or related concepts.")

    # Check if other process-related words appear (from qok_words)
    if len(qok_words) > 0:
        logic_content.append("\n### Process Variants")
        logic_content.append(f"Other words starting with 'qok': {', '.join(list(qok_words.keys()))}")

    logic_content.append("")
    logic_content.append("## Conclusion")
    if process_count == 0 and star_count > 0:
        logic_content.append("The section describes stars ('os') but lacks the explicit 'Process!' command found in recipes. It likely describes the *nature* or *influence* of stars rather than a direct chemical process.")
    elif process_count > 0:
        logic_content.append("The presence of 'Process!' instructions alongside stars suggests a celestial alchemy recipe.")
    else:
        logic_content.append("The text contains limited explicit references to 'Star' (os) or 'Process!' (qokeody), suggesting a more complex or different subject matter than simple astro-alchemy.")
    
    save_file('results/astro_logic.md', '\n'.join(logic_content))
    
    # Generate Summary
    summary_content = [
        "# Track 187 Results Summary",
        "",
        "## Completed Tasks",
        "- Translated pages f67r-f73v (Astro Section).",
        "- Applied key substitutions: os->Star, ordaiin->Golden Extract.",
        "- Analyzed text structure.",
        "",
        "## Key Findings",
        f"- 'Star' (os) count: {star_count}",
        f"- 'Process!' (qokeody) count: {process_count}",
        f"- 'Golden Extract' (ordaiin) count: {golden_extract_count}",
        "",
        "## Next Steps",
        "- Investigate 'os' variants for star references.",
        "- Correlate 'qok' variants with recipe steps if any exist."
    ]
    
    save_file('results/track-187-results_summary.md', '\n'.join(summary_content))
    
if __name__ == "__main__":
    main()
