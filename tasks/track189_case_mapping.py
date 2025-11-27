import json
import re
import os
from collections import Counter

# Configuration
SEGMENTED_TEXT_PATH = "results/segmented_text.txt"
DICTIONARY_PATH = "results/dictionary/dictionary.json"
OUTPUT_REPORT_PATH = "results/case_system_v1.md"
OUTPUT_SUMMARY_PATH = "results/track-189-results_summary.md"

PREFIXES = ["ot", "ok", "or", "op", "ol"]

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    
    verbs = set()
    for word, entry in data.get("entries", {}).items():
        meaning = entry.get("meaning", "").lower()
        if "verb" in meaning or "action" in meaning:
            verbs.add(word)
    return verbs

def parse_segmented_text(path):
    sentences = []
    with open(path, 'r') as f:
        for line in f:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Extract the text part (after the >)
            if ">" in line:
                meta, content = line.split(">", 1)
                clean_content = content.strip()
            else:
                clean_content = line.strip()
            
            # Remove tags like <->, <!plant>, numbers, punctuation
            # We want to keep the words. Words are separated by dots.
            # Also handle spaces if any.
            
            # Replace <...> with empty
            clean_content = re.sub(r'<[^>]+>', '', clean_content)
            
            # Split by dots
            words = [w.strip() for w in clean_content.split('.') if w.strip()]
            
            # Clean words (remove !, ?, numbers, etc)
            clean_words = []
            for w in words:
                w = re.sub(r'[!?0-9,;]', '', w)
                if w:
                    clean_words.append(w)
            
            if clean_words:
                sentences.append(clean_words)
    return sentences

def analyze_prefixes(sentences, verbs):
    prefix_correlations = {p: Counter() for p in PREFIXES}
    sample_sentences = []
    
    for sent in sentences:
        for i, word in enumerate(sent):
            # Check if word starts with one of the prefixes
            matched_prefix = None
            for p in PREFIXES:
                if word.startswith(p) and len(word) > len(p):
                    matched_prefix = p
                    break
            
            if matched_prefix:
                # Check preceding word
                if i > 0:
                    prev_word = sent[i-1]
                    # Identify if prev_word is a verb
                    # Even if not in dictionary, we capture it for stats, 
                    # but we flag if it is a known verb.
                    is_verb = prev_word in verbs
                    
                    prefix_correlations[matched_prefix][prev_word] += 1
                    
                    # Collect sample if prev_word is a known verb or high freq
                    if is_verb:
                        sample_sentences.append({
                            "prefix": matched_prefix,
                            "word": word,
                            "verb": prev_word,
                            "sentence": sent,
                            "pattern": f"{prev_word} (VERB) + {word} ({matched_prefix}-...)"
                        })
                else:
                    # Sentence start
                    pass

    return prefix_correlations, sample_sentences

def generate_report(prefix_correlations, sample_sentences, verbs):
    lines = []
    lines.append("# Case System V1 Analysis\n")
    
    lines.append("## Prefix-Verb Correlations\n")
    for prefix in PREFIXES:
        lines.append(f"### Prefix `{prefix}-`")
        lines.append("| Preceding Word | Is Known Verb? | Count |")
        lines.append("|---|---|---|")
        
        # Get top 10 preceding words
        top_preceding = prefix_correlations[prefix].most_common(10)
        for word, count in top_preceding:
            is_verb = "Yes" if word in verbs else "No"
            lines.append(f"| {word} | {is_verb} | {count} |")
        lines.append("\n")
        
        # Hypothesis generation based on top verbs could go here
        # But for now we list the data.

    lines.append("## Sample Sentence Diagrams\n")
    lines.append("Displaying 20 samples where `[Verb] + [Prefix-Noun]` pattern is found.\n")
    
    # Filter samples to ensure we have unique sentences and prioritize known verbs
    # We want 20 samples, ideally distributed across prefixes
    
    selected_samples = []
    seen_sents = set()
    
    # Group by prefix to ensure variety
    samples_by_prefix = {p: [] for p in PREFIXES}
    for s in sample_sentences:
        if tuple(s['sentence']) not in seen_sents:
            samples_by_prefix[s['prefix']].append(s)
            seen_sents.add(tuple(s['sentence']))
            
    # Round robin selection
    while len(selected_samples) < 20:
        added = False
        for p in PREFIXES:
            if samples_by_prefix[p]:
                selected_samples.append(samples_by_prefix[p].pop(0))
                added = True
                if len(selected_samples) >= 20:
                    break
        if not added:
            break
            
    for i, sample in enumerate(selected_samples, 1):
        lines.append(f"**{i}. {sample['pattern']}**")
        # Format sentence: highlight verb and target word
        formatted_sent = []
        for w in sample['sentence']:
            if w == sample['verb']:
                formatted_sent.append(f"**{w}** (V)")
            elif w == sample['word']:
                formatted_sent.append(f"**{w}** (O)")
            else:
                formatted_sent.append(w)
        lines.append(f"> {' '.join(formatted_sent)}\n")

    with open(OUTPUT_REPORT_PATH, 'w') as f:
        f.write('\n'.join(lines))
        
    # Also generate summary
    summary = []
    summary.append("# Track 189 Results Summary\n")
    summary.append("## Findings\n")
    summary.append("Analysis of prefixes `ot-`, `ok-`, `or-`, `op-`, `ol-` and their preceding verbs.\n")
    summary.append(f"- Analyzed correlations for {len(PREFIXES)} prefixes.")
    summary.append(f"- Generated {len(selected_samples)} sample sentence diagrams in `{OUTPUT_REPORT_PATH}`.\n")
    
    with open(OUTPUT_SUMMARY_PATH, 'w') as f:
        f.write('\n'.join(summary))

def main():
    print("Loading dictionary...")
    verbs = load_dictionary(DICTIONARY_PATH)
    print(f"Loaded {len(verbs)} potential verbs.")
    
    print("Parsing text...")
    sentences = parse_segmented_text(SEGMENTED_TEXT_PATH)
    print(f"Parsed {len(sentences)} sentences.")
    
    print("Analyzing prefixes...")
    prefix_correlations, sample_sentences = analyze_prefixes(sentences, verbs)
    
    print("Generating report...")
    generate_report(prefix_correlations, sample_sentences, verbs)
    print("Done.")

if __name__ == "__main__":
    main()
