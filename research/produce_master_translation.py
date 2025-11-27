import json
import re
import os

# Configuration
TRANSCRIPTION_FILE = "data/eva_ivtff.txt"
DICTIONARY_FILE = "results/dictionary/master_dictionary_v15.json"
OUTPUT_FILE = "results/full_draft_translation_v1.md"
SUMMARY_FILE = "results/track-283-results_summary.md"

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get("entries", {})

def parse_eva_line(line):
    # Matches lines like <f34v.3,+P0;H> text...
    # We prefer H (Takahashi) as it is usually complete EVA
    match = re.match(r'<([^>]+;H)>\s+(.*)', line)
    if match:
        tag = match.group(1)
        text = match.group(2)
        # Extract page ID from tag: f34v.3... -> f34v
        page_match = re.match(r'(f\d+[rv]\d?)', tag)
        page_id = page_match.group(1) if page_match else "unknown"
        return page_id, text.strip()
    return None, None

def translate_text(text, dictionary):
    words = text.split('.')
    translated_words = []
    known_count = 0
    total_count = 0

    for word in words:
        word = word.strip()
        if not word:
            continue
        
        # Handle punctuation/modifiers attached to words if necessary
        # For now, assume simple splitting by dot is sufficient for EVA
        # But EVA files might have commas etc? 
        # In eva_ivtff, words are dot-separated. 
        # Some might have punctuation like , or - attached. 
        # We'll simple strip non-alpha for lookup but keep original for display if needed?
        # Task says: "Keep unknown words as raw_word".
        
        clean_word = re.sub(r'[^a-zA-Z0-9]', '', word) # Basic cleaning for lookup
        
        total_count += 1
        if clean_word in dictionary:
            # Use the "meaning" field
            meaning = dictionary[clean_word].get("meaning", word)
            translated_words.append(f"[{meaning}]")
            known_count += 1
        else:
            translated_words.append(word)
            
    return " ".join(translated_words), known_count, total_count

def main():
    print(f"Loading dictionary from {DICTIONARY_FILE}...")
    dictionary = load_dictionary(DICTIONARY_FILE)
    print(f"Loaded {len(dictionary)} entries.")

    print(f"Reading transcription from {TRANSCRIPTION_FILE}...")
    
    current_page = None
    translated_lines = []
    
    total_words = 0
    total_translated = 0
    page_stats = {} # page_id -> {total, translated}

    try:
        with open(TRANSCRIPTION_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('<'):
                    continue
                
                # Only process H lines
                if ';H>' not in line:
                    continue
                    
                page_id, text = parse_eva_line(line)
                if not page_id or not text:
                    continue
                
                if page_id != current_page:
                    translated_lines.append(f"\n## {page_id}\n")
                    current_page = page_id
                    page_stats[page_id] = {'total': 0, 'translated': 0}
                
                trans_line, k, t = translate_text(text, dictionary)
                
                if t > 0:
                    confidence = (k / t) * 100
                    translated_lines.append(f"> {trans_line} *(Conf: {confidence:.1f}%)*")
                    
                    total_words += t
                    total_translated += k
                    page_stats[page_id]['total'] += t
                    page_stats[page_id]['translated'] += k

    except FileNotFoundError:
        print(f"Error: File {TRANSCRIPTION_FILE} not found.")
        return

    print(f"Writing translation to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Master Translation Draft v1\n\n")
        f.write("\n".join(translated_lines))
        
    # Calculate summary stats
    overall_coverage = (total_translated / total_words * 100) if total_words > 0 else 0
    
    # Find best pages
    page_coverages = []
    for pid, stats in page_stats.items():
        if stats['total'] > 0:
            cov = (stats['translated'] / stats['total']) * 100
            page_coverages.append((pid, cov))
            
    page_coverages.sort(key=lambda x: x[1], reverse=True)
    top_20_pages = page_coverages[:20]
    
    print(f"Writing summary to {SUMMARY_FILE}...")
    with open(SUMMARY_FILE, 'w') as f:
        f.write("# Master Translation Summary (Track 283)\n\n")
        f.write(f"- **Total Words:** {total_words}\n")
        f.write(f"- **Translated Words:** {total_translated}\n")
        f.write(f"- **Overall Coverage:** {overall_coverage:.2f}%\n\n")
        f.write("## Top 20 Translated Pages\n\n")
        f.write("| Page | Coverage % |\n")
        f.write("|---|---|\n")
        for pid, cov in top_20_pages:
            f.write(f"| {pid} | {cov:.2f}% |\n")
            
    print("Done.")

if __name__ == "__main__":
    main()
