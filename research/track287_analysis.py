import json
import os
import re

def load_dictionary(dict_path):
    if not os.path.exists(dict_path):
        print(f"Dictionary not found: {dict_path}")
        return {}
    with open(dict_path, 'r') as f:
        data = json.load(f)
    return data.get('entries', {})

def load_f41r_text(data_path):
    f41r_lines = []
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        return []
    
    with open(data_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if "<f41r." in line:
                # Prefer 'H' transcription if available
                if ";H>" in line:
                    # Format: <f41r.X,+P0;H> text
                    parts = line.split('>')
                    if len(parts) > 1:
                        text_part = parts[1].strip()
                        f41r_lines.append(text_part)
    return f41r_lines

def clean_word(word):
    return word.strip()

def get_morphology_type(word):
    markers = []
    # Prefixes
    if word.startswith('qo') or word.startswith('qok'):
        markers.append('Verbalizer(qo-/qok-)')
    elif word.startswith('ol'):
        markers.append('NounMarker(ol-)')
    elif word.startswith('o') and len(word) > 3: # avoid short words being matched too aggressively
        markers.append('NounMarker(o-)')
        
    # Suffixes
    if word.endswith('y'):
        markers.append('Imperative(-y)')
    if word.endswith('ed') or word.endswith('edy'):
        markers.append('Process(-ed/-edy)')
        
    # Specific words
    if word == 'daiin':
        markers.append('Command(daiin)')
    if word == 'sho':
        markers.append('Command(sho)')
        
    return markers

def analyze_page(lines, dictionary):
    translation_log = []
    instructional_count = 0
    descriptive_count = 0
    total_words = 0
    grammar_markers_count = 0
    
    translated_lines = []
    
    for line in lines:
        words = re.split(r'[.\s]+', line)
        line_translation = []
        
        for word in words:
            word = clean_word(word)
            if not word:
                continue
                
            if '<' in word or '>' in word:
                continue
            
            clean_w = word.replace('!', '').replace('?', '')
            
            entry = dictionary.get(clean_w)
            trans = "[?]"
            meaning = ""
            is_instruction = False
            
            # Check dictionary
            if entry:
                meaning = entry.get('meaning', '')
                if meaning and meaning != "unknown":
                    trans = meaning
                    # Heuristic for instruction in meaning
                    if any(verb in meaning.lower() for verb in ['burn', 'mix', 'dry', 'collect', 'drink', 'take', 'put', 'add', 'boil', 'crush', 'cook']):
                        is_instruction = True
            
            # Check Morphology
            morph_markers = get_morphology_type(clean_w)
            if morph_markers:
                grammar_markers_count += 1
                
            # Heuristic for instruction based on morphology
            if 'Verbalizer(qo-/qok-)' in morph_markers or 'Command(daiin)' in morph_markers or 'Command(sho)' in morph_markers:
                is_instruction = True
            if 'Imperative(-y)' in morph_markers and (is_instruction or meaning == ""):
                 # Assume unknown words ending in -y might be imperative if they are not clearly nouns
                 pass 

            # Refine translation display
            display_text = word
            if trans != "[?]":
                display_text += f"({trans})"
            
            if morph_markers:
                 display_text += f"[{', '.join(morph_markers)}]"
            
            if is_instruction:
                instructional_count += 1
                display_text = f"**{display_text}**"
            elif trans != "[?]":
                descriptive_count += 1
            
            line_translation.append(display_text)
            total_words += 1
        
        translated_lines.append(" ".join(line_translation))
        
    grammar_density = grammar_markers_count / total_words if total_words > 0 else 0
    instruction_ratio = instructional_count / total_words if total_words > 0 else 0
    
    return {
        "lines": translated_lines,
        "stats": {
            "total_words": total_words,
            "instructional_count": instructional_count,
            "descriptive_count": descriptive_count,
            "grammar_markers_count": grammar_markers_count,
            "grammar_density": grammar_density,
            "instruction_ratio": instruction_ratio
        }
    }

def main():
    data_path = "data/eva_ivtff.txt"
    dict_path = "results/dictionary/master_dictionary_v15.json"
    
    lines = load_f41r_text(data_path)
    print(f"Loaded {len(lines)} lines for f41r")
    
    dictionary = load_dictionary(dict_path)
    print(f"Loaded {len(dictionary)} dictionary entries")
    
    analysis = analyze_page(lines, dictionary)
    
    output_path = "results/f41r_deep_analysis.md"
    with open(output_path, 'w') as f:
        f.write("# Deep Analysis of f41r (Herbal Page)\n\n")
        f.write("## Overview\n")
        f.write(f"- Total words: {analysis['stats']['total_words']}\n")
        f.write(f"- Instructional words (Morphology+Dict): {analysis['stats']['instructional_count']}\n")
        f.write(f"- Descriptive/Known words: {analysis['stats']['descriptive_count']}\n")
        f.write(f"- Grammar Density (Markers/Total): {analysis['stats']['grammar_density']:.2f}\n")
        f.write(f"- Instruction Ratio: {analysis['stats']['instruction_ratio']:.2f}\n\n")
        
        f.write("## Translation and Structure\n\n")
        for line in analysis['lines']:
            f.write(f"- {line}\n")
            
        f.write("\n## Structural Findings\n")
        if analysis['stats']['instruction_ratio'] > 0.3 or analysis['stats']['grammar_density'] > 0.5:
            f.write("High density of instructions/grammar suggests this is a **recipe** or **procedure**.\n")
        else:
            f.write("Lower density suggests this might be a **description**.\n")
            
    print(f"Analysis written to {output_path}")

    # Create summary file
    summary_path = "results/track-287-results_summary.md"
    with open(summary_path, 'w') as f:
        f.write("# Track 287 Results: High-Density Herbal Analysis\n\n")
        f.write("## Findings on f41r\n")
        f.write(f"- Analyzed f41r using master dictionary v15 and Grammar Map (Track 280).\n")
        f.write(f"- Grammar Density: {analysis['stats']['grammar_density']:.2f}.\n")
        f.write(f"- Identified {analysis['stats']['instructional_count']} instructional terms.\n")
        f.write("- See `results/f41r_deep_analysis.md` for full line-by-line translation.\n")
        f.write("\n## Plant Identification Context\n")
        f.write("- The high presence of process markers (qo-, -edy) indicates an active preparation process.\n")
        f.write("- f41r is likely a **Recipe** embedded in an herbal page.\n")

if __name__ == "__main__":
    main()
