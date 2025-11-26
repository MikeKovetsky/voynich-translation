import re
import json
import collections
from pathlib import Path

# Configuration
INPUT_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/master_dictionary_v6.json"
OUTPUT_REPORT = "results/bio_grammar_report.md"
OUTPUT_JSON = "results/bio_sentence_structure.json"

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
        return data.get("entries", {})

def parse_eva_text(path, start_page="f75r", end_page="f84v"):
    text_data = []
    
    # Generate valid page prefixes
    pages = []
    for i in range(75, 85):
        pages.append(f"f{i}r")
        pages.append(f"f{i}v")
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith("<"):
                continue
                
            # Extract page ID
            match = re.match(r"<([a-z0-9]+)[\.,]", line)
            if not match:
                continue
            
            page_id = match.group(1)
            
            if page_id not in pages:
                continue
            
            # Filter for 'H' version or 'C' if H not present? 
            # Sticking to H for consistency as per previous successful runs
            if ";H>" not in line:
                continue
                
            parts = line.split(">", 1)
            if len(parts) < 2:
                continue
                
            content = parts[1].strip()
            content = re.sub(r"<[^>]+>", "", content)
            content = re.sub(r"\{[^}]+\}", "", content)
            content = content.replace(".", " ").replace(",", " ")
            content = re.sub(r"[!%*]", "", content)
            
            if content:
                text_data.append(content)
            
    return text_data

def tokenize(text):
    return [w for w in text.split() if w]

def infer_pos(word, dictionary):
    # Known grammar words override
    grammar_map = {
        "ol": "DET", "or": "PREP", "al": "PREP", "ar": "PREP",
        "daiin": "VERB", "okeey": "VERB", "okey": "VERB",
        "shedy": "CLAUSE", "chedy": "NOUN", "chol": "NOUN",
        "otaiin": "NOUN", "y": "CONJ", "o": "CONJ"
    }
    
    if word in grammar_map:
        return grammar_map[word]
        
    if word in dictionary:
        entry = dictionary[word]
        domain = entry.get("domain", "").lower()
        meaning = entry.get("meaning", "").lower()
        
        if domain == "grammar":
            return "GRAMMAR" # Could be PREP or DET
        if "plant" in meaning or "star" in meaning or domain == "botanical":
            return "NOUN"
            
    # Guess based on morphology
    if word.startswith("qo") or word.startswith("qok"):
        return "QOK-WORD" # Special class for this section
        
    return "UNK"

def analyze_structure(sentences, dictionary):
    patterns = collections.Counter()
    
    for sent in sentences:
        tokens = tokenize(sent)
        pos_seq = [infer_pos(w, dictionary) for w in tokens]
        
        # Look for simple patterns of length 3-4
        if len(pos_seq) >= 3:
            for i in range(len(pos_seq) - 2):
                gram = tuple(pos_seq[i:i+3])
                patterns[gram] += 1
                
    return patterns

def main():
    print("Loading dictionary...")
    dictionary = load_dictionary(DICT_FILE)
    
    print("Parsing text...")
    lines = parse_eva_text(INPUT_FILE)
    # Treat each line as a potential sentence unit for now, or join and split?
    # Task says "Split text by common delimiters". Since lines are short and EVA has no explicit sentence punctuation besides paragraphs,
    # we might treat lines as sentences or look for structural breaks.
    # Let's treat lines as "phrases".
    
    full_text = " ".join(lines)
    tokens = tokenize(full_text)
    
    # Task 1: Verb Identification
    shedy_clauses = []
    shedy_indices = [i for i, x in enumerate(tokens) if x == "shedy"]
    for i in shedy_indices:
        start = max(0, i - 2)
        end = min(len(tokens), i + 3)
        # Extract POS context
        clause_tokens = tokens[start:end]
        clause_pos = [infer_pos(w, dictionary) for w in clause_tokens]
        shedy_clauses.append((tuple(clause_tokens), tuple(clause_pos)))

    # Task 2: Sentence Segmentation / POS Patterns
    # Sliding window of 4 POS tags
    pos_sequence = [infer_pos(w, dictionary) for w in tokens]
    ngram_counts = collections.Counter()
    for i in range(len(pos_sequence) - 3):
        ngram = tuple(pos_sequence[i:i+4])
        ngram_counts[ngram] += 1

    # Task 3: Subject-Object
    # Context of 'chedy'
    chedy_pre = collections.Counter()
    chedy_post = collections.Counter()
    for i, w in enumerate(tokens):
        if w == "chedy":
            if i > 0: chedy_pre[tokens[i-1]] += 1
            if i < len(tokens) - 1: chedy_post[tokens[i+1]] += 1
            
    # Terminology
    counts = collections.Counter(tokens)
    
    # Identify QOK words
    qok_words = collections.Counter([w for w in tokens if w.startswith("qok")])
    
    # Reporting
    report_lines = []
    report_lines.append("# Biological Grammar Analysis (Quire 13)")
    report_lines.append(f"\n**Section:** f75r - f84v")
    report_lines.append(f"**Total Words:** {len(tokens)}")
    report_lines.append(f"**Vocabulary Size:** {len(counts)}")
    
    report_lines.append("\n## 1. Sentence Structure (POS Patterns)")
    report_lines.append("Common 4-gram POS sequences:")
    for pat, count in ngram_counts.most_common(15):
        pat_str = " + ".join(pat)
        report_lines.append(f"- `{pat_str}`: {count}")
        
    report_lines.append("\n## 2. The Role of `shedy`")
    report_lines.append("Common contexts around `shedy` (clause marker):")
    shedy_summary = collections.Counter([p[1] for p in shedy_clauses])
    for pat, count in shedy_summary.most_common(10):
        pat_str = " ".join(pat)
        # Highlight the center
        # Logic: center is usually index 2 (0,1,2,3,4) if window is 5
        # wait, window logic above: start = i-2, end=i+3 -> length 5.
        # Center is index 2.
        if len(pat) == 5:
            pat_list = list(pat)
            pat_list[2] = "**CLAUSE**"
            pat_str = " + ".join(pat_list)
        report_lines.append(f"- `{pat_str}`: {count}")

    report_lines.append("\n## 3. Key Vocabulary Analysis")
    report_lines.append("\n### The `qok-` Prefix")
    report_lines.append("This prefix is highly specific to the Biological section.")
    report_lines.append("Top `qok-` words:")
    for w, c in qok_words.most_common(10):
        report_lines.append(f"- `{w}` ({c})")
        
    report_lines.append("\n### Context of `chedy` (Plant)")
    report_lines.append("**Preceded by:**")
    report_lines.append(", ".join([f"{w} ({c})" for w, c in chedy_pre.most_common(5)]))
    report_lines.append("\n**Followed by:**")
    report_lines.append(", ".join([f"{w} ({c})" for w, c in chedy_post.most_common(5)]))

    report_lines.append("\n### Verb Candidates")
    report_lines.append("If `daiin` (Take) is rare, what are the verbs?")
    # Look for words that commonly appear in VERB positions (e.g., after CLAUSE or NOUN)
    # Based on POS patterns, if NOUN + X + PREP is common, X might be VERB.
    
    # Find potential verbs
    potential_verbs = collections.Counter()
    for i in range(len(pos_sequence) - 2):
        p1, p2, p3 = pos_sequence[i], pos_sequence[i+1], pos_sequence[i+2]
        w2 = tokens[i+1]
        if p1 == "NOUN" and p3 == "PREP" and p2 == "UNK":
            potential_verbs[w2] += 1
        if p1 == "CLAUSE" and p2 == "UNK": # shedy X ...
            potential_verbs[w2] += 1
            
    report_lines.append("Top candidates based on position (NOUN [?] PREP or shedy [?]):")
    for w, c in potential_verbs.most_common(10):
        report_lines.append(f"- `{w}` ({c})")

    # Save
    with open(OUTPUT_REPORT, "w") as f:
        f.write("\n".join(report_lines))
        
    output_json = {
        "pos_patterns": [{"pattern": p, "count": c} for p, c in ngram_counts.most_common(20)],
        "qok_words": dict(qok_words.most_common(20)),
        "verb_candidates": dict(potential_verbs.most_common(20))
    }
    with open(OUTPUT_JSON, "w") as f:
        # Convert tuple keys to strings if necessary, but here we list them
        json.dump(output_json, f, indent=2)
        
    print(f"Analysis complete. Report written to {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
