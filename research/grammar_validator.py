import re
from collections import Counter, defaultdict
import os

def load_eva_data(filepath):
    """
    Parses EVA data, returning a dict of {page_id: [lines_of_words]}
    Focuses on 'H' transcription (Takahashi) for consistency.
    """
    pages = defaultdict(list)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return {}
        
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#"):
                continue
            
            # Match format: <f11r.1,@P0;H> text...
            # We want 'H' transcription
            match = re.match(r"<(f\d+[rv]\d?)\.(\d+).*?;H>\s+(.*)", line)
            if match:
                page_id = match.group(1)
                text = match.group(3).strip()
                
                # Basic EVA cleanup
                # Remove uncertain chars marked with ! or *
                text = text.replace("!", "").replace("*", "")
                # Split by dot
                words = [w for w in text.split('.') if w and w != "-"]
                
                if words:
                    pages[page_id].append(words)
    return pages

def analyze_grammar(input_file, output_file):
    pages = load_eva_data(input_file)
    print(f"Loaded {len(pages)} pages.")
    
    # Define Hypothesized Classes
    verbs = ["qokeey", "qokedy", "qokeedy", "shedy", "chedy", "okeey"] # "Cook", "Mix", "Drink"
    nouns = ["chol", "or", "ald", "daiin", "oteol", "sho"] # "Leaf", "Gold", "Thistle", "Star", "Root", "Fire"
    
    verb_positions = defaultdict(Counter)
    noun_positions = defaultdict(Counter)
    
    # Scan
    total_lines = 0
    svo_hits = 0
    vso_hits = 0
    
    for page, lines in pages.items():
        for line_idx, words in enumerate(lines):
            total_lines += 1
            
            # Position Analysis
            for i, word in enumerate(words):
                if word in verbs:
                    pos_type = "Start" if i == 0 else "Middle" if i < len(words)-1 else "End"
                    verb_positions[word][pos_type] += 1
                if word in nouns:
                    pos_type = "Start" if i == 0 else "Middle" if i < len(words)-1 else "End"
                    noun_positions[word][pos_type] += 1
                    
            # Sequence Analysis (V-N vs N-V)
            # Simple check: is there a Verb followed by a Noun?
            has_verb = -1
            has_noun = -1
            
            for i, word in enumerate(words):
                if word in verbs: has_verb = i
                if word in nouns: has_noun = i
                
            if has_verb != -1 and has_noun != -1:
                if has_verb < has_noun:
                    vso_hits += 1 # Verb before Noun (Imperative/VSO)
                else:
                    svo_hits += 1 # Noun before Verb (SVO)

    # Write Report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Track 311: Grammar Baseline Report\n\n")
        f.write(f"Analyzed {total_lines} lines from {len(pages)} pages.\n\n")
        
        f.write("## 1. Verb Position (Imperative Check)\n")
        f.write("Hypothesis: Verbs should appear at the 'Start' of lines in Recipes.\n\n")
        f.write("| Verb | Start | Middle | End | Primary |\n|---|---|---|---|---|\n")
        for v in verbs:
            counts = verb_positions[v]
            total = sum(counts.values())
            if total == 0: continue
            primary = max(counts, key=counts.get)
            f.write(f"| {v} | {counts['Start']} | {counts['Middle']} | {counts['End']} | **{primary}** |\n")
            
        f.write("\n## 2. Noun Position (Object Check)\n")
        f.write("Hypothesis: Nouns should appear in 'Middle/End'.\n\n")
        f.write("| Noun | Start | Middle | End | Primary |\n|---|---|---|---|---|\n")
        for n in nouns:
            counts = noun_positions[n]
            total = sum(counts.values())
            if total == 0: continue
            primary = max(counts, key=counts.get)
            f.write(f"| {n} | {counts['Start']} | {counts['Middle']} | {counts['End']} | **{primary}** |\n")
            
        f.write("\n## 3. Syntax Order (SVO vs VSO)\n")
        f.write(f"- **Verb-Noun (VSO/Imperative):** {vso_hits} lines\n")
        f.write(f"- **Noun-Verb (SVO/Declarative):** {svo_hits} lines\n")
        
        ratio = vso_hits / (svo_hits + 1)
        f.write(f"\n**Ratio (V-N / N-V):** {ratio:.2f}\n")
        if ratio > 1.5:
            f.write("Conclusion: **Strong VSO/Imperative Bias** (Consistent with Recipes).\n")
        elif ratio < 0.6:
            f.write("Conclusion: **Strong SVO Bias** (Narrative).\n")
        else:
            f.write("Conclusion: **Mixed/Inconclusive**.\n")

    print(f"Analysis complete. Report: {output_file}")

if __name__ == "__main__":
    analyze_grammar("data/eva_ivtff.txt", "results/grammar_baseline_report.md")
