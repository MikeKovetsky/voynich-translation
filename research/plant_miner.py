import re
import json
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        return json.load(f)

def parse_ivtff(path):
    """
    Parses the IVTFF file and yields (folio, text) for Herbal pages (f1-f66).
    """
    # Pattern to match lines like <f1r.1,@P0;H> ...
    # We are interested in the folio number and the transcription text.
    # We'll use a simple heuristic: if the line starts with <f(\d+), and \1 is <= 66.
    
    line_pattern = re.compile(r"^<f(\d+)([rv])\..*?>\s+(.*)$")
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = line_pattern.match(line)
            if match:
                folio_num = int(match.group(1))
                folio_side = match.group(2)
                text = match.group(3)
                
                # Herbal section is roughly f1 to f66 (Book II usually refers to this range in VMS studies context, 
                # though strictly Book I is herbal, but the task says Book II: f1-f66. 
                # f1-f66 is the first large section, mostly herbal).
                if 1 <= folio_num <= 66:
                    yield f"{folio_num}{folio_side}", text

def clean_token(token):
    # Remove garbage characters like !, ?, *, {}, []
    # Keep a-z, 0-9 for now, though EVA is mostly a-z.
    # Patterns like <!@252> should be removed.
    token = re.sub(r"<[^>]+>", "", token) # Remove tags
    token = re.sub(r"\{[^}]+\}", "", token) # Remove comments
    token = re.sub(r"[!?,*]", "", token) # Remove punctuation
    return token.strip()

def is_unknown(word, dictionary):
    return word not in dictionary.get('entries', {})

def main():
    data_path = "data/eva_ivtff.txt"
    dict_path = "results/dictionary/dictionary.json"
    output_path = "results/mining/plant_candidates.json"
    
    print(f"Loading dictionary from {dict_path}...")
    dictionary = load_dictionary(dict_path)
    known_words = set(dictionary['entries'].keys())
    
    print(f"Scanning {data_path} for plant candidates...")
    
    plant_candidates = {} # word -> {count, contexts, score}
    
    # Regex for splitting words. In EVA, words are separated by . or spaces.
    # We'll normalize by splitting on [. ]
    
    # We need to process text to find patterns like "o-[UNKNOWN]", "[UNKNOWN] otar", "[UNKNOWN] oteey"
    # This requires looking at sequences of words.
    
    processed_count = 0
    
    for folio, line_text in parse_ivtff(data_path):
        # Basic cleaning of the line before splitting
        # Remove inline comments/tags first to avoid breaking word sequences
        clean_line = re.sub(r"<[^>]+>", "", line_text)
        clean_line = re.sub(r"\{[^}]+\}", "", clean_line)
        clean_line = re.sub(r"[!?,*]", "", clean_line)
        
        words = [w for w in re.split(r'[.\s]+', clean_line) if w]
        
        for i, word in enumerate(words):
            if not word: continue
            
            is_word_unknown = word not in known_words
            
            # Logic: 
            # 1. Extract unknowns from Herbal pages.
            # 2. Prioritize words starting with o- or ch-
            # 3. Context patterns: "o-[UNKNOWN]", "[UNKNOWN] otar", "[UNKNOWN] oteey"
            
            if not is_word_unknown:
                continue

            # Initialize candidate if new
            if word not in plant_candidates:
                plant_candidates[word] = {
                    "word": word,
                    "count": 0,
                    "score": 0,
                    "reasons": [],
                    "pages": set(),
                    "contexts": []
                }
            
            cand = plant_candidates[word]
            cand["count"] += 1
            cand["pages"].add(folio)
            
            # Context capturing (simple window)
            start = max(0, i - 2)
            end = min(len(words), i + 3)
            context_snippet = " ".join(words[start:end])
            if len(cand["contexts"]) < 5: # limit contexts
                cand["contexts"].append(context_snippet)
            
            # SCORING LOGIC
            
            # Pattern: Starts with o-
            if word.startswith('o'):
                cand["score"] += 1
                if "starts_with_o" not in cand["reasons"]:
                    cand["reasons"].append("starts_with_o")
            
            # Pattern: Starts with ch-
            if word.startswith('ch'):
                cand["score"] += 1
                if "starts_with_ch" not in cand["reasons"]:
                    cand["reasons"].append("starts_with_ch")
                    
            # Context Patterns
            # "o-[UNKNOWN]" -> Check previous word
            if i > 0 and words[i-1] == "o":
                cand["score"] += 3
                if "preceded_by_o" not in cand["reasons"]:
                    cand["reasons"].append("preceded_by_o")
            
            # "[UNKNOWN] otar" -> Check next word
            if i < len(words) - 1 and words[i+1] == "otar":
                cand["score"] += 5
                if "followed_by_otar" not in cand["reasons"]:
                    cand["reasons"].append("followed_by_otar")

            # "[UNKNOWN] oteey" -> Check next word
            if i < len(words) - 1 and words[i+1] == "oteey":
                cand["score"] += 5
                if "followed_by_oteey" not in cand["reasons"]:
                    cand["reasons"].append("followed_by_oteey")

        processed_count += 1
        if processed_count % 1000 == 0:
            print(f"Processed {processed_count} lines...")

    # Filter candidates
    # We only want "likely" candidates. 
    # Let's say score > 0 is a requirement? Or simply being an unknown in Herbal is enough?
    # The task says "Extract unknowns from Herbal pages" then "Prioritize...".
    # So we should probably list all unknowns found in Herbal pages, but sort/score them.
    # However, raw unknowns might be too many (typos etc).
    # Let's filter for min_count or min_score.
    # Since goal is "Mass-identify", maybe keep all but sort by score.
    
    sorted_candidates = sorted(
        plant_candidates.values(), 
        key=lambda x: (x['score'], x['count']), 
        reverse=True
    )
    
    # Convert sets to lists for JSON serialization
    final_output = []
    for c in sorted_candidates:
        c['pages'] = sorted(list(c['pages']))
        final_output.append(c)
        
    print(f"Found {len(final_output)} plant candidates.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
