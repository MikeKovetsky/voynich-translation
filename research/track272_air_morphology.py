import json
import re
import os
from collections import defaultdict

# Paths
TRANSCRIPTION_PATH = 'data/eva_ivtff.txt'
DICTIONARY_PATH = 'results/dictionary/dictionary_v13.json'
OUTPUT_PATH = 'results/suffix_air_analysis.md'

def load_transcription(path):
    text_data = [] # List of (word, preceding_word)
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Filter for H (Takahashi) transliteration for consistency
        # Lines look like: <f1r.1,@P0;H>	fachys.ykal.ar.ataiin.shol.shory.cth!res.y.kor.sholdy!
        data_lines = [line for line in lines if ';H>' in line]
        
        for line in data_lines:
            parts = line.split()
            if len(parts) < 2:
                continue
            
            # content is usually the last part or parts after the tag
            # Tag is parts[0]. content is parts[1:]
            content = " ".join(parts[1:])
            
            # Split by dot and clean
            raw_words = content.replace('!', '').replace('?', '').replace(',', '').replace('*', '').split('.')
            
            # Clean empty strings
            words = [w.strip() for w in raw_words if w.strip()]
            
            for i, word in enumerate(words):
                prev = words[i-1] if i > 0 else None
                text_data.append((word, prev))
                
    except FileNotFoundError:
        print(f"Error: File {path} not found.")
        return []
        
    return text_data

def load_dictionary(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Error: Dictionary {path} not found.")
        return {}

def analyze_air_suffix():
    text_data = load_transcription(TRANSCRIPTION_PATH)
    dictionary = load_dictionary(DICTIONARY_PATH)
    
    air_words = defaultdict(lambda: {'count': 0, 'preceded_by_ol': 0, 'total_occurrences': 0})
    
    for word, prev in text_data:
        if word.endswith('air') or word.endswith('aiir'):
            if word in ['air', 'aiir']: # Exclude root itself if it is just the suffix
                continue
                
            air_words[word]['total_occurrences'] += 1
            air_words[word]['count'] += 1
            
            if prev == 'ol' or prev == 'qol' or prev == 'l' or prev == 'chol': # expanding 'ol' check slightly for common variants
                air_words[word]['preceded_by_ol'] += 1
            
            # Check dictionary
            if word in dictionary:
                air_words[word]['dict_entry'] = dictionary[word]

    # Hypothesis Analysis
    # Identify Roots
    results = []
    for word, data in air_words.items():
        suffix = 'aiir' if word.endswith('aiir') else 'air'
        root = word[:-len(suffix)]
        
        # Simple Latin heuristic (very basic, just for suggestion)
        latin_hypothesis = []
        if root == 'shk':
            latin_hypothesis.append("Cich-orium (Chicory)")
        elif root == 'ok':
             latin_hypothesis.append("? (oc-arium?)") # Placeholder
        elif root == 'cth':
             latin_hypothesis.append("? (cith-ara?)")
        elif root == 'san':
             latin_hypothesis.append("Sanct-uarium")
             
        data['root'] = root
        data['suffix'] = suffix
        data['latin_hypothesis'] = latin_hypothesis
        results.append((word, data))
        
    # Sort by frequency
    results.sort(key=lambda x: x[1]['total_occurrences'], reverse=True)
    
    # Generate Report
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write("# Morphology Decoder v2: The `-air` Suffix Analysis\n\n")
        f.write(f"**Source:** `{TRANSCRIPTION_PATH}` (H-transliteration)\n")
        f.write(f"**Dictionary:** `v13`\n\n")
        f.write("## Hypothesis\n")
        f.write("Testing if `-air` equates to Latin suffixes like `-orium`, `-arium`, `-arius`.\n\n")
        
        f.write("## Findings\n\n")
        f.write("| Voynich Word | Count | Root | Suffix | Preceded by `ol` | Latin Match? | Dictionary Status |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        
        for word, data in results:
            root = data['root']
            suffix = data['suffix']
            ol_count = data['preceded_by_ol']
            count = data['total_occurrences']
            latin = ", ".join(data['latin_hypothesis']) if data['latin_hypothesis'] else "-"
            
            dict_info = "New"
            if 'dict_entry' in data:
                entry = data['dict_entry']
                meaning = entry.get('meaning', '')
                lang = entry.get('language', '')
                dict_info = f"**{meaning}** ({lang})"
            
            f.write(f"| `{word}` | {count} | `{root}` | `-{suffix}` | {ol_count} | {latin} | {dict_info} |\n")
            
        f.write("\n## Distribution Analysis\n")
        total_words = len(results)
        words_with_ol = sum(1 for w, d in results if d['preceded_by_ol'] > 0)
        f.write(f"- Total `-air` words types found: {total_words}\n")
        f.write(f"- Words preceded by `ol` (or variants): {words_with_ol} ({words_with_ol/total_words*100:.1f}%)\n")
        
        if words_with_ol > 0:
            f.write("\nThe high co-occurrence with `ol` (likely 'the' or 'a') suggests these may be Nouns or Places (uarium/orium).\n")
        else:
            f.write("\nLow co-occurrence with `ol` observed.\n")

if __name__ == "__main__":
    analyze_air_suffix()
