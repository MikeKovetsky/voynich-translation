import re
import collections
import json
import os

INPUT_FILE = 'data/eva_ivtff.txt'
OUTPUT_FILE = 'results/sentence_starters.md'
DICTIONARY_FILE = 'results/dictionary/dictionary_v15_draft.json'

def load_dictionary(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Warning: Dictionary not found at {path}")
        return {}

def analyze_starters():
    print("Starting analysis...")
    total_counts = collections.Counter()
    start_counts = collections.Counter()
    
    dictionary = load_dictionary(DICTIONARY_FILE)
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    line_count = 0
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            
            # Use Takahashi (H) transcription
            if ';H>' not in line:
                continue
            
            line_count += 1
            
            # Extract content
            try:
                content_part = line.split('>', 1)[1]
            except IndexError:
                continue
                
            content = content_part.strip()
            
            # Clean
            content = re.sub(r'\{[^}]*\}', '', content)
            content = content.replace('.', ' ')
            content = re.sub(r'[!?,%*]', '', content)
            content = re.sub(r'<[^>]*>', '', content)
            
            words = content.split()
            
            if not words:
                continue
            
            # Process words
            for i, word in enumerate(words):
                total_counts[word] += 1
                if i == 0:
                    start_counts[word] += 1
    
    print(f"Processed {line_count} lines.")

    # Filter and Calculate Stats
    candidates = []
    for word, total in total_counts.items():
        if total > 50:
            start_count = start_counts[word]
            prob = (start_count / total) * 100
            
            candidates.append({
                'word': word,
                'total': total,
                'start': start_count,
                'prob': prob,
                'meaning': dictionary.get(word, {}).get('meaning', 'Unknown')
            })
    
    # Sort by Start Probability (descending)
    candidates.sort(key=lambda x: x['prob'], reverse=True)
    
    top_20 = candidates[:20]
    print(f"Found {len(candidates)} words with frequency > 50.")
    
    # Generate Output
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Sentence Starters Analysis\n\n")
        f.write("## Goal\n")
        f.write("Identify words that appear at Position 1 (Start of line) with high frequency.\n")
        f.write("Criteria: Total Count > 50. Sorted by Start Probability.\n\n")
        
        f.write("## Top 20 Candidates\n\n")
        f.write("| Word | Meaning | Start Prob | Starts | Total |\n")
        f.write("|---|---|---|---|---|\n")
        
        for c in top_20:
            meaning = c['meaning']
            if meaning is None:
                meaning = "-"
            # Bold if meets the original > 40% criteria
            bold = "**" if c['prob'] > 40 else ""
            f.write(f"| {bold}{c['word']}{bold} | {meaning} | {c['prob']:.1f}% | {c['start']} | {c['total']} |\n")
            
        f.write("\n## Hypothesis\n")
        f.write("- High start probability suggests these words function as Sentence Starters, Particles, or Conjunctions.\n")
        f.write("- Words with > 40% start probability are highlighted.\n")
        
        # Check specific words mentioned in task
        star_eye_words = ['aiin', 'saiin', 'sho', 'or', 'qokeey', 'daiin']
        f.write("\n## Star/Eye & Common Words Check\n")
        f.write("Checking specific words of interest:\n\n")
        f.write("| Word | Start Prob | Starts | Total | Meaning |\n")
        f.write("|---|---|---|---|---|\n")
        for word in star_eye_words:
            total = total_counts[word]
            start = start_counts[word]
            prob = (start / total * 100) if total > 0 else 0
            meaning = dictionary.get(word, {}).get('meaning', 'Unknown')
            f.write(f"| **{word}** | {prob:.1f}% | {start} | {total} | {meaning} |\n")
            
    print(f"Results written to {OUTPUT_FILE}")

if __name__ == '__main__':
    analyze_starters()
