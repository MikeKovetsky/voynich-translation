import json
import re
import os

# Paths
TRANSLATION_FILE = 'results/full_draft_translation_v1.md'
DICTIONARY_FILE = 'results/dictionary/master_dictionary_v16.json'
OUTPUT_JSON = 'results/context_inferred_candidates.json'
OUTPUT_MD = 'results/track-303-results_summary.md'

def load_dictionary():
    if not os.path.exists(DICTIONARY_FILE):
        print(f"Dictionary not found: {DICTIONARY_FILE}")
        return {}
    with open(DICTIONARY_FILE, 'r') as f:
        data = json.load(f)
    return data.get('entries', {})

def get_ol_meanings(dictionary):
    ol_entry = dictionary.get('ol')
    if not ol_entry:
        return []
    meaning = ol_entry.get('meaning', '')
    # Meaning might be "The (Wet/Cold) / Water-of" or similar
    # We'll match strict string or list
    return [meaning]

def parse_translation_file():
    sentences = []
    with open(TRANSLATION_FILE, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        if not line.startswith('>'):
            continue
        
        # Remove '>', leading/trailing whitespace
        content = line.strip()[1:].strip()
        
        # Extract confidence if present
        conf_match = re.search(r'\*\(Conf: ([\d\.]+)\%\)\*', content)
        conf = 0.0
        if conf_match:
            conf = float(conf_match.group(1))
            # Remove the confidence marker from the content for processing
            content = content.replace(conf_match.group(0), '').strip()
        
        # Tokenize
        # We need to respect brackets: [word meaning] is one token
        # We can split by space, but [word meaning] might contain spaces.
        # Regex to find tokens: bracketed or non-whitespace
        tokens = re.findall(r'\[.*?\]|\S+', content)
        
        # Calculate known ratio
        known_count = sum(1 for t in tokens if t.startswith('[') and t.endswith(']'))
        total_count = len(tokens)
        
        if total_count == 0:
            continue
            
        ratio = known_count / total_count
        
        if ratio > 0.75:
            sentences.append({
                'content': content,
                'tokens': tokens,
                'ratio': ratio,
                'conf': conf
            })
            
    return sentences

def infer_candidates(sentences, ol_meanings):
    candidates = []
    
    # Prepare set of ol meanings for fast lookup
    # Normalize to match token format [Meaning]
    ol_tokens = set()
    ol_tokens.add('ol')
    for m in ol_meanings:
        ol_tokens.add(f"[{m}]")
    
    # Debug: Print ol meanings
    # print(f"ol meanings/tokens: {ol_tokens}")
    
    for sent in sentences:
        tokens = sent['tokens']
        for i, token in enumerate(tokens):
            # Check if unknown (not bracketed)
            if not (token.startswith('[') and token.endswith(']')):
                unknown_word = token
                
                # Logic for 'ol [UNKNOWN]' -> noun/ingredient
                # Check previous token
                is_noun_candidate = False
                if i > 0:
                    prev_token = tokens[i-1]
                    # loose match for ol translation
                    # If prev_token is [The (Wet/Cold) / Water-of], it might match our ol meaning
                    # Or we can just check if 'ol' is in the previous token if we had source
                    # But here we only have [Translation].
                    # Let's assume if the previous token contains "The" or "Of" it might be a trigger,
                    # but strictly following "ol" frame:
                    # We'll try to match against dictionary definition.
                    
                    if prev_token in ol_tokens:
                        is_noun_candidate = True
                    else:
                        # Flexible matching: if any ol meaning is a substring of the token?
                        for m in ol_meanings:
                            if m and m in prev_token:
                                is_noun_candidate = True
                                break
                
                # Logic for '[UNKNOWN]-y' -> verb/imperative
                is_verb_candidate = False
                if unknown_word.endswith('y'):
                    is_verb_candidate = True
                
                inference = []
                if is_noun_candidate:
                    inference.append("noun / ingredient")
                if is_verb_candidate:
                    inference.append("verb / imperative")
                
                if inference:
                    candidates.append({
                        'sentence': sent['content'],
                        'unknown_word': unknown_word,
                        'context_frame': f"{tokens[i-1] if i>0 else 'START'} {unknown_word} {tokens[i+1] if i+1 < len(tokens) else 'END'}",
                        'inference': ", ".join(inference),
                        'confidence': "High" if len(inference) == 1 else "Medium"
                    })
                    
    return candidates

def save_results(candidates):
    # JSON output
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(candidates, f, indent=2)
    
    # MD Summary
    with open(OUTPUT_MD, 'w') as f:
        f.write("# Track 303: Context Inferred Candidates\n\n")
        f.write(f"Total Candidates Found: {len(candidates)}\n\n")
        f.write("| Unknown Word | Inference | Context | Full Sentence |\n")
        f.write("|---|---|---|---|\n")
        
        # Limit summary to top 100 or so to avoid huge file, or just list all if reasonable
        for c in candidates[:200]:
            # Escape pipes in content
            sent = c['sentence'].replace('|', '\|')
            ctx = c['context_frame'].replace('|', '\|')
            f.write(f"| **{c['unknown_word']}** | {c['inference']} | `{ctx}` | {sent} |\n")
            
    print(f"Saved {len(candidates)} candidates to {OUTPUT_JSON} and {OUTPUT_MD}")

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary()
    ol_meanings = get_ol_meanings(dictionary)
    print(f"Dictionary loaded. 'ol' meanings: {ol_meanings}")
    
    print("Parsing translation file...")
    sentences = parse_translation_file()
    print(f"Found {len(sentences)} sentences with > 75% known words.")
    
    print("Inferring candidates...")
    candidates = infer_candidates(sentences, ol_meanings)
    
    print("Saving results...")
    save_results(candidates)

if __name__ == "__main__":
    main()
