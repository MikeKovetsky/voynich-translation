import re
from collections import defaultdict
import os

def load_words_by_line(filepath):
    lines_data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("#"): continue
            match = re.match(r"<(f\d+[rv]\d?)\.(\d+).*?;H>\s+(.*)", line)
            if match:
                text = match.group(3).strip().replace("!", "").replace("*", "")
                words = [w for w in text.split('.') if w and w != "-"]
                if words:
                    lines_data.append(words)
    return lines_data

def generate_heatmap(input_file, output_file):
    lines = load_words_by_line(input_file)
    print(f"Loaded {len(lines)} lines.")
    
    # Identify Top 20 Words
    word_counts = defaultdict(int)
    for line in lines:
        for w in line:
            word_counts[w] += 1
            
    top_words = sorted(word_counts, key=word_counts.get, reverse=True)[:20]
    
    # Calculate Position Distribution (0.0 = Start, 1.0 = End)
    # We'll bucket into 5 bins: 0-20%, 20-40%, etc.
    bins = defaultdict(lambda: [0]*5)
    
    for line in lines:
        length = len(line)
        if length == 0: continue
        
        for i, word in enumerate(line):
            if word in top_words:
                # Normalize position
                pos = i / length # 0.0 to 0.99
                bin_idx = int(pos * 5) 
                if bin_idx > 4: bin_idx = 4
                bins[word][bin_idx] += 1
                
    # Write Report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Track 313: Syntax Heatmap\n\n")
        f.write("Distribution of Top 20 Words across the line (Start -> End).\n\n")
        f.write("| Word | Rank | 0-20% (Start) | 20-40% | 40-60% (Mid) | 60-80% | 80-100% (End) | Dominant |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        
        for i, w in enumerate(top_words):
            b = bins[w]
            total = sum(b)
            if total == 0: continue
            
            # Normalize to percentages
            b_pct = [f"{(x/total)*100:.0f}%" for x in b]
            
            # Find Dominant
            max_val = max(b)
            max_idx = b.index(max_val)
            dom = ["Start", "Early-Mid", "Mid", "Late-Mid", "End"][max_idx]
            
            # Add Bold to highest
            b_pct[max_idx] = f"**{b_pct[max_idx]}**"
            
            f.write(f"| {w} | #{i+1} | {b_pct[0]} | {b_pct[1]} | {b_pct[2]} | {b_pct[3]} | {b_pct[4]} | {dom} |\n")
            
    print(f"Analysis complete. Report: {output_file}")

if __name__ == "__main__":
    generate_heatmap("data/eva_ivtff.txt", "results/syntax_heatmap.md")
