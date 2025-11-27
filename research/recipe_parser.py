import json
import re
import os
from collections import Counter

DICTIONARY_PATH = "results/dictionary/dictionary.json"
IVTFF_PATH = "data/eva_ivtff.txt"
OUTPUT_PATTERNS = "results/recipe_structure_v3.json"
OUTPUT_GUESSES = "results/structural_guesses.json"

# Specific mappings from task
OVERRIDE_MAP = {
    "daiin": "COMMAND_TAKE",
    "y": "CONNECTOR_AND",
    "ol": "ARTICLE_THE",
    "qokeedy": "NOUN_MIXTURE"
}

def load_dictionary():
    if not os.path.exists(DICTIONARY_PATH):
        print(f"Dictionary not found at {DICTIONARY_PATH}")
        return {}
    
    with open(DICTIONARY_PATH, 'r') as f:
        data = json.load(f)
        
    entries = data.get("entries", {})
    # Map word -> meaning/class
    word_map = {}
    for word, info in entries.items():
        # normalize word just in case
        w = word.strip()
        meaning = info.get("meaning", "UNKNOWN")
        word_map[w] = meaning
        
    return word_map

def clean_word(w):
    # Remove common punctuation
    w = w.strip(".,:;!?()[]{}<>\"'")
    # If word contains '?' or '!', it's likely garbage or uncertain read
    if '?' in w or '!' in w:
        return None
    if not w:
        return None
    # remove starting/ending non-alpha if needed, but keep it simple
    return w

def load_sentences():
    # Quire 20: f103r (103) to f116v (116)
    sentences = []
    
    # Pattern for IVTFF line: <f103r.1;H> content
    # We prioritize 'F' transcriber, then 'H', then others.
    # We need to read the whole file, collect lines by (folio, side, line_idx).
    
    lines_map = {} # (folio, side, line_idx) -> { transcriber: content }
    
    with open(IVTFF_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith("<f"):
                continue
            
            # Regex to parse <f103r.1;H>
            match = re.match(r"<f(\d+)([rv])\.([^;]+);(\w+)>\s+(.*)", line)
            if not match:
                continue
            
            folio_str = match.group(1)
            folio_num = int(folio_str)
            side = match.group(2)
            line_idx = match.group(3)
            transcriber = match.group(4)
            content = match.group(5)
            
            if 103 <= folio_num <= 116:
                key = (folio_num, side, line_idx)
                if key not in lines_map:
                    lines_map[key] = {}
                lines_map[key][transcriber] = content

    # Sort keys to process in order
    # keys are (int, str, str). line_idx is string, numerical sort preferred?
    # line_idx can be '1', '2', ..., 'P.1'.
    # We'll try to sort by line_idx logically.
    
    def sort_key(k):
        # k = (folio, side, line_idx)
        # folio, side ('r' < 'v'?), line_idx
        # parse line_idx: try to extract numbers.
        # 'P.1' -> 1? '10' -> 10.
        # rough sort:
        nums = re.findall(r'\d+', k[2])
        n = int(nums[0]) if nums else 0
        return (k[0], k[1], n, k[2])
        
    sorted_keys = sorted(lines_map.keys(), key=sort_key)
    
    # Process lines in order
    for key in sorted_keys:
        variants = lines_map[key]
        # Prefer F, then H, then m, then others
        content = variants.get('F') or variants.get('H') or variants.get('m') or list(variants.values())[0]
        
        # Remove comments like {comment} if any (rare in content part usually, but good practice)
        content = re.sub(r'\{.*?\}', '', content)
        
        # Tokenize
        # Remove punctuation attached to words?
        # IVTFF: words separated by spaces. Periods usually spaces in some transcriptions.
        # We will replace . with space and split
        content = content.replace('.', ' ')
        words = content.split()
        
        # Process words for sentence splitting
        # "Tokenize the Recipe Section sentences (splitting by daiin or newlines)"
        # This means each LINE is a potential boundary, AND `daiin` is a boundary.
        
        line_tokens = []
        for word in words:
            w = clean_word(word)
            if not w: continue
            # Check for invalid chars or garbage
            if w.startswith('&') or w.startswith('%'): continue 
            
            line_tokens.append(w)
            
        # Now split line_tokens by 'daiin'
        # "daiin" starts a new sentence.
        
        temp_sentence = []
        for w in line_tokens:
            if w == "daiin":
                # Start new sentence.
                # If we have accumulated words, push them.
                if temp_sentence:
                    sentences.append(temp_sentence)
                    temp_sentence = []
                # Add daiin to the new sentence
                temp_sentence.append(w)
            else:
                temp_sentence.append(w)
        
        if temp_sentence:
            sentences.append(temp_sentence)
            
    return sentences

def map_to_classes(sentences, word_map):
    patterns = []
    structural_data = [] # (word, class, pattern_context)
    
    for sent in sentences:
        pattern = []
        # For identifying slots, we need the original sentence and classes
        sent_classes = []
        
        for word in sent:
            # Check override
            if word in OVERRIDE_MAP:
                cls = OVERRIDE_MAP[word]
            elif word in word_map:
                # Use dictionary meaning
                # Dictionary meanings might be like "plant_name", "star_name".
                # We should probably uppercase them or keep as is.
                # Task examples: NOUN_MIXTURE, COMMAND_TAKE.
                # If dict has "plant_name", maybe map to "NOUN_PLANT"?
                # For now, use the raw meaning string but cleaned.
                m = word_map[word]
                if m.startswith("NOUN_") or m.startswith("COMMAND_") or m.startswith("CONNECTOR_") or m.startswith("ARTICLE_"):
                     cls = m
                else:
                    # normalize patterns?
                    cls = m.upper().replace(" ", "_")
            else:
                cls = "UNKNOWN"
                
            pattern.append(cls)
            sent_classes.append(cls)
            
        patterns.append(" + ".join(pattern))
        
        # Analyze UNKNOWN slots
        for i, (word, cls) in enumerate(zip(sent, sent_classes)):
            if cls == "UNKNOWN":
                prev_cls = sent_classes[i-1] if i > 0 else "START"
                next_cls = sent_classes[i+1] if i < len(sent_classes) - 1 else "END"
                structural_data.append({
                    "word": word,
                    "prev": prev_cls,
                    "next": next_cls
                })
                
    return patterns, structural_data

def analyze_structure(structural_data):
    # Group by word to see if a word consistently appears in a slot
    word_contexts = {}
    for item in structural_data:
        w = item['word']
        if w not in word_contexts:
            word_contexts[w] = []
        word_contexts[w].append((item['prev'], item['next']))
        
    guesses = {}
    
    # Heuristics
    # "If UNKNOWN is always between ol and y, it is 99% an Ingredient Noun."
    # "If UNKNOWN is always at the end of a sentence, it is likely a Verb/Process."
    
    for word, contexts in word_contexts.items():
        total = len(contexts)
        
        # Check for ARTICLE_THE + UNKNOWN + CONNECTOR_AND
        # 'ol' -> ARTICLE_THE, 'y' -> CONNECTOR_AND
        
        ingr_count = sum(1 for p, n in contexts if p == "ARTICLE_THE" and n == "CONNECTOR_AND")
        
        # Check for End of Sentence
        end_count = sum(1 for p, n in contexts if n == "END")
        
        guessed_type = "UNKNOWN"
        confidence = "low"
        reason = ""
        
        if ingr_count == total and total > 0:
            guessed_type = "NOUN_INGREDIENT"
            confidence = "high" if total > 1 else "medium"
            reason = "Always between ARTICLE_THE and CONNECTOR_AND"
        elif ingr_count / total > 0.8:
            guessed_type = "NOUN_INGREDIENT"
            confidence = "medium"
            reason = f"Mostly ({ingr_count}/{total}) between ARTICLE_THE and CONNECTOR_AND"
        elif end_count == total and total > 0:
            guessed_type = "VERB_PROCESS"
            confidence = "high" if total > 1 else "medium"
            reason = "Always at end of sentence"
        elif end_count / total > 0.8:
             guessed_type = "VERB_PROCESS"
             confidence = "medium"
             reason = f"Mostly ({end_count}/{total}) at end of sentence"
             
        if guessed_type != "UNKNOWN":
            guesses[word] = {
                "inferred_type": guessed_type,
                "confidence": confidence,
                "reason": reason,
                "count": total,
                "examples": contexts[:3]
            }
            
    return guesses

def main():
    print("Loading dictionary...")
    word_map = load_dictionary()
    
    print("Loading sentences...")
    sentences = load_sentences()
    print(f"Loaded {len(sentences)} sentences.")
    
    print("Mapping classes...")
    patterns, structural_data = map_to_classes(sentences, word_map)
    
    print("Analyzing slots...")
    guesses = analyze_structure(structural_data)
    
    print("Writing outputs...")
    with open(OUTPUT_PATTERNS, 'w') as f:
        json.dump(patterns, f, indent=2)
        
    with open(OUTPUT_GUESSES, 'w') as f:
        json.dump(guesses, f, indent=2)
        
    print("Done.")

if __name__ == "__main__":
    main()
