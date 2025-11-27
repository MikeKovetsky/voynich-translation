
import json
from collections import Counter
import re
from pathlib import Path
import voynich_data

# Load dictionary
DICT_FILE = Path("results/master_dictionary_v6.json")

def load_dictionary():
    if not DICT_FILE.exists():
        print(f"Dictionary file not found: {DICT_FILE}")
        return {}
    with open(DICT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("entries", {})

def analyze_biological_section():
    print("Loading data...")
    dictionary = load_dictionary()
    
    # Get biological section text
    bio_text_map = voynich_data.get_section_text('biological')
    
    all_words = []
    lines = []
    
    for folio, page_data in bio_text_map.items():
        for loc, line in page_data.items():
            # Improved cleaning: remove stuff in angle brackets first
            clean_line = re.sub(r'<[^>]+>', '', line)
            clean_line = re.sub(r'[!?<>@$\d]', '', clean_line).strip()
            words = [w for w in re.split(r'[.\-=,\s]', clean_line) if w]
            # Filter out known artifacts
            words = [w for w in words if w not in ['figure', 'null']]
            
            all_words.extend(words)
            lines.append({
                "folio": folio,
                "loc": loc,
                "text": words,
                "raw": line
            })
            
    total_words = len(all_words)
    unique_words = set(all_words)
    print(f"Biological Section: {total_words} words, {len(unique_words)} unique.")
    
    # Task 1: Frequency Analysis
    print("\n--- Task 1: Frequency Analysis ---")
    word_counts = Counter(all_words)
    top_words = word_counts.most_common(20)
    
    print("Top 20 words in Biological Section:")
    known_top_nouns = []
    
    for word, count in top_words:
        meaning = "Unknown"
        domain = "N/A"
        if word in dictionary:
            entry = dictionary[word]
            meaning = entry.get("meaning", "Unknown")
            domain = entry.get("domain", "N/A")
        
        print(f"  {word}: {count} ({meaning}) [{domain}]")
        
    # Check for specific words mentioned in hypothesis
    check_words = ['chol', 'char', 'otaiin']
    print("\nHypothesis check:")
    for w in check_words:
        count = word_counts.get(w, 0)
        meaning = dictionary.get(w, {}).get("meaning", "Unknown")
        print(f"  {w}: {count} ({meaning})")

    # Task 2: Grammar Application
    print("\n--- Task 2: Grammar Application (daiin) ---")
    daiin_usage = []
    
    for line_data in lines:
        words = line_data["text"]
        if "daiin" in words:
            try:
                idx = words.index("daiin")
                # Look at next word
                if idx + 1 < len(words):
                    obj = words[idx + 1]
                    obj_meaning = dictionary.get(obj, {}).get("meaning", "Unknown")
                    daiin_usage.append({
                        "loc": line_data["loc"],
                        "phrase": f"daiin {obj}",
                        "object": obj,
                        "meaning": obj_meaning
                    })
            except ValueError:
                pass
                
    print(f"Found {len(daiin_usage)} occurrences of 'daiin'.")
    if daiin_usage:
        print("Sample usages:")
        for usage in daiin_usage[:10]:
            print(f"  {usage['loc']}: {usage['phrase']} -> Take {usage['meaning']}")

    # Task 3: Dictionary Expansion (Bio)
    print("\n--- Task 3: Dictionary Expansion ---")
    
    # Identify words unique to this section (or highly overrepresented)
    # To do this properly, we need global frequencies. 
    # For now, we'll just list high freq words in this section that are NOT in the dictionary.
    
    unknown_freq = []
    for word, count in word_counts.most_common():
        if word not in dictionary:
            unknown_freq.append((word, count))
            
    print(f"Top 10 Unknown words in Bio Section:")
    for w, c in unknown_freq[:10]:
        print(f"  {w}: {c}")
        
    # Cross-reference with Hebrew terms
    # Hebrew roots provided in plan
    hebrew_terms = {
        "bath": ["mikveh", "rachatz"],
        "water": ["mayim"],
        "woman": ["ishah", "nashim"],
        "skin": ["or"]
    }
    
    print("\nExisting dictionary matches for bio terms:")
    found_bio_terms = False
    for word, entry in dictionary.items():
        meaning = entry.get("meaning", "").lower()
        meaning_words = re.split(r'[\s/(),]+', meaning)
        for category, terms in hebrew_terms.items():
            if category in meaning_words or any(term in meaning_words for term in terms):
                print(f"  {word}: {meaning} (Matches {category})")
                found_bio_terms = True
                
    if not found_bio_terms:
        print("  No direct dictionary matches found for bio terms.")

    # Generate Output Files
    
    # 1. bio_vocabulary.json
    bio_vocab = {
        "section": "biological",
        "top_words": [{"word": w, "count": c, "meaning": dictionary.get(w, {}).get("meaning", "Unknown")} for w, c in top_words],
        "daiin_objects": [u["object"] for u in daiin_usage],
        "unknown_high_freq": [{"word": w, "count": c} for w, c in unknown_freq[:50]]
    }
    
    with open("results/bio_vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(bio_vocab, f, indent=2)
    print("\nSaved results/bio_vocabulary.json")
    
    # 2. results/bio_section_report.md
    report = f"""# Biological Section Decoding Report

## Overview
- **Section**: Biological (Quire 13)
- **Folios**: {list(bio_text_map.keys())[0]} - {list(bio_text_map.keys())[-1]}
- **Total Words**: {total_words}
- **Unique Words**: {len(unique_words)}

## Task 1: Frequency Analysis
Top 20 words in the section:
| Word | Count | Meaning | Domain |
|------|-------|---------|--------|
"""
    for w, c in top_words:
        entry = dictionary.get(w, {})
        meaning = entry.get("meaning", "Unknown")
        domain = entry.get("domain", "N/A")
        report += f"| {w} | {c} | {meaning} | {domain} |\n"

    report += """
### Hypothesis Check
Frequency of key ingredients found in other sections:
"""
    for w in check_words:
        count = word_counts.get(w, 0)
        meaning = dictionary.get(w, {}).get("meaning", "Unknown")
        report += f"- **{w}** ({meaning}): {count}\n"
        
    report += """
## Task 2: Grammar Application
Analysis of `daiin` (to take/from) usage:
"""
    if daiin_usage:
        report += f"- **Total occurrences**: {len(daiin_usage)}\n"
        report += "- **Sample Phrases**:\n"
        for u in daiin_usage[:20]:
            report += f"  - `{u['phrase']}` ({u['loc']}) -> Object: **{u['object']}** ({u['meaning']})\n"
    else:
        report += "- No occurrences of `daiin` found in this section.\n"
        
    report += """
## Task 3: Dictionary Expansion
### Top Unknown Words
Words frequent in this section but missing from Master Dictionary:
"""
    for w, c in unknown_freq[:20]:
        report += f"- **{w}**: {c}\n"
        
    report += """
### Bio-Specific Vocabulary Candidates
Potential matches for Hebrew bio terms (Bath, Water, Woman, Skin):
"""
    # Add any found matches
    matches = []
    for word, entry in dictionary.items():
        meaning = entry.get("meaning", "").lower()
        meaning_words = re.split(r'[\s/(),]+', meaning)
        for category, terms in hebrew_terms.items():
            if category in meaning_words or any(term in meaning_words for term in terms):
               matches.append(f"- **{word}**: {meaning} (Matches {category})")
    
    if matches:
        report += "\n".join(matches)
    else:
        report += "No direct matches found in current dictionary."
        
    with open("results/bio_section_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Saved results/bio_section_report.md")

if __name__ == "__main__":
    analyze_biological_section()

