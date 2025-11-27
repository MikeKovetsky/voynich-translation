import json
import re
from collections import defaultdict, Counter
import os

# Configuration
DICTIONARY_PATH = 'results/dictionary/dictionary_v13.json'
TRANSCRIPTION_PATH = 'data/eva_ivtff.txt'
OUTPUT_JSON = 'results/syntax_map_v1.json'
OUTPUT_MD = 'results/track-258-results_summary.md'

def load_dictionary():
    if not os.path.exists(DICTIONARY_PATH):
        print(f"Dictionary not found at {DICTIONARY_PATH}")
        return {}
    
    with open(DICTIONARY_PATH, 'r') as f:
        data = json.load(f)
    
    entries = data.get('entries', data)
    return entries

def get_pos(word, dictionary):
    """Determine broad POS (Noun, Verb) from dictionary."""
    if word not in dictionary:
        return None
    
    entry = dictionary[word]
    
    # Check explicit POS
    if 'part_of_speech' in entry:
        pos = entry['part_of_speech'].lower()
        if 'noun' in pos: return 'Noun'
        if 'verb' in pos: return 'Verb'
        if 'adjective' in pos: return 'Adjective'
    
    # Check meaning/domain
    if 'meaning' in entry:
        meaning = str(entry['meaning']).lower()
        if 'plant' in meaning or 'star' in meaning or 'noun' in meaning: return 'Noun'
        if 'action' in meaning or 'verb' in meaning: return 'Verb'
    
    return None

def parse_transcription():
    """
    Parses eva_ivtff.txt to extract sentences (lines).
    Returns a list of lists of words.
    """
    if not os.path.exists(TRANSCRIPTION_PATH):
        print(f"Transcription not found at {TRANSCRIPTION_PATH}")
        return []

    sentences = []
    seen_locations = set()
    
    with open(TRANSCRIPTION_PATH, 'r') as f:
        for line in f:
            # Only process lines with location tags
            if not line.startswith('<'): 
                continue
            
            # Regex to capture location, transcriber code, and text
            # Example: <f1r.1;H> text...
            match = re.match(r'<([^;]+);([^>]+)>\s+(.*)', line)
            if not match:
                continue
            
            loc, transcriber, text = match.groups()
            
            # Prioritize the first transcriber encountered for each location
            # (File usually has H or C first which are good)
            if loc in seen_locations:
                continue
            seen_locations.add(loc)
            
            # Clean text
            # Remove comments in {}
            text = re.sub(r'\{[^}]*\}', '', text)
            
            # Split by dots or spaces (EVA uses dots primarily)
            # Also handle standard spaces just in case
            raw_words = text.replace('.', ' ').split()
            
            clean_words = []
            for w in raw_words:
                w = w.strip()
                # Remove punctuation/uncertainty markers
                w = re.sub(r'[!?,*;]', '', w)
                
                # Skip empty strings and non-word tokens (like simple numbers or symbols if any)
                # EVA words are letters.
                if w and w.isalpha(): 
                    clean_words.append(w)
            
            if clean_words:
                sentences.append(clean_words)
                
    return sentences

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary()
    print(f"Loaded {len(dictionary)} dictionary entries.")

    print("Parsing transcription...")
    sentences = parse_transcription()
    print(f"Parsed {len(sentences)} lines/sentences.")

    if not sentences:
        print("No sentences found. Aborting.")
        return

    # 1. Identify Function Words
    print("Identifying function words...")
    word_counts = Counter()
    for s in sentences:
        word_counts.update(s)
    
    function_words = []
    for w, count in word_counts.items():
        # Criteria: Frequency > 50, Length <= 3
        if count > 50 and len(w) <= 3:
            function_words.append(w)
    
    print(f"Found {len(function_words)} function words.")

    # 2. Analyze Positional Probability
    print("Analyzing positions...")
    # Stats structure
    stats = defaultdict(lambda: {
        'total': 0, 
        'start': 0, 
        'end': 0, 
        'pre_noun': 0, 
        'fol_verb': 0,
        'pre_verb': 0  # Added for Pronoun check
    })
    
    for s in sentences:
        length = len(s)
        for i, w in enumerate(s):
            if w in function_words:
                stats[w]['total'] += 1
                
                # Start of Sentence
                if i == 0:
                    stats[w]['start'] += 1
                
                # End of Sentence
                if i == length - 1:
                    stats[w]['end'] += 1
                
                # Precedes Noun (Word is BEFORE a Noun)
                if i + 1 < length:
                    next_w = s[i+1]
                    if get_pos(next_w, dictionary) == 'Noun':
                        stats[w]['pre_noun'] += 1
                    if get_pos(next_w, dictionary) == 'Verb':
                        stats[w]['pre_verb'] += 1
                
                # Follows Verb (Word is AFTER a Verb)
                if i - 1 >= 0:
                    prev_w = s[i-1]
                    if get_pos(prev_w, dictionary) == 'Verb':
                        stats[w]['fol_verb'] += 1

    # 3. Classify
    print("Classifying...")
    results = []
    
    for w in function_words:
        data = stats[w]
        total = data['total']
        
        if total == 0: continue
        
        p_start = data['start'] / total
        p_end = data['end'] / total
        p_pre_noun = data['pre_noun'] / total
        p_fol_verb = data['fol_verb'] / total
        p_pre_verb = data['pre_verb'] / total
        
        role = "Unknown"
        confidence = 0.0
        
        # Classification Logic based on Task
        # - Conjunction: Appears between two clauses (high P(Start) or P(Mid)).
        # - Preposition: Precedes Nouns (high P(Precedes Noun)).
        # - Particle/Suffix: Appears at end of words/lines (high P(End)).
        # - Pronoun: Precedes Verbs.
        
        # We use thresholds. Since data is sparse, thresholds might need tuning.
        
        # 1. Check for Particle/Suffix (End of line)
        if p_end > 0.30:
            role = "Particle/Suffix"
            confidence = p_end
        
        # 2. Check for Pronoun (Precedes Verb)
        elif p_pre_verb > 0.15:
            role = "Pronoun"
            confidence = p_pre_verb * 2 # Boost confidence slightly as verb detection is hard
            if confidence > 1.0: confidence = 0.95
            
        # 3. Check for Preposition (Precedes Noun)
        elif p_pre_noun > 0.15:
            role = "Preposition"
            confidence = p_pre_noun * 2
            if confidence > 1.0: confidence = 0.95

        # 4. Check for Conjunction (Start or general connector)
        elif p_start > 0.20:
            role = "Conjunction"
            confidence = p_start
            
        # Fallback/Refinement: If highly frequent but undefined, might be a common conjunction or particle.
        
        # Format output
        results.append({
            "word": w,
            "role": role,
            "confidence": round(confidence, 2),
            "stats": {
                "total_count": total,
                "p_start": round(p_start, 3),
                "p_end": round(p_end, 3),
                "p_pre_noun": round(p_pre_noun, 3),
                "p_pre_verb": round(p_pre_verb, 3),
                "p_fol_verb": round(p_fol_verb, 3)
            },
            "evidence": (
                f"Freq: {total}, P(Start): {p_start:.2f}, P(End): {p_end:.2f}, "
                f"P(PreNoun): {p_pre_noun:.2f}, P(PreVerb): {p_pre_verb:.2f}"
            )
        })
        
    # Sort by frequency or role? Task doesn't specify. Frequency is good.
    results.sort(key=lambda x: x['stats']['total_count'], reverse=True)

    # 4. Output JSON
    print(f"Writing to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
        
    # 5. Generate Summary Markdown
    print(f"Writing to {OUTPUT_MD}...")
    with open(OUTPUT_MD, 'w') as f:
        f.write("# Track 258: Syntax Mapper Results\n\n")
        f.write("## Function Words Analysis\n\n")
        f.write("| Word | Role | Confidence | Frequency | Evidence |\n")
        f.write("|---|---|---|---|---|\n")
        
        for r in results:
            # Only show top results or all? All function words is fine (likely < 100)
            row = (
                f"| **{r['word']}** | {r['role']} | {r['confidence']} | "
                f"{r['stats']['total_count']} | {r['evidence']} |"
            )
            f.write(row + "\n")
            
        f.write("\n## Methodology\n")
        f.write("- **Input**: `data/eva_ivtff.txt` (transcription) and `results/dictionary/dictionary_v13.json`.\n")
        f.write("- **Function Words**: Freq > 50, Length <= 3.\n")
        f.write("- **Classification Rules**:\n")
        f.write("  - **Particle/Suffix**: High P(End of Sentence)\n")
        f.write("  - **Pronoun**: High P(Precedes Verb)\n")
        f.write("  - **Preposition**: High P(Precedes Noun)\n")
        f.write("  - **Conjunction**: High P(Start of Sentence)\n")
    
    print("Done.")

if __name__ == "__main__":
    main()
