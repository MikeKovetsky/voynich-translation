import re
import os
from collections import Counter

def mine_astro_stars(input_file, output_file):
    print("Mining Astro Structures...")
    
    stars = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Filter for Astro Section (f67-f73)
            match = re.match(r"<(f\d+[rv]\d?)\.", line)
            if not match: continue
            
            page_id = match.group(1)
            num = int(re.search(r'\d+', page_id).group())
            if not (67 <= num <= 73): continue
            
            # Find labels (short words near <star> tags usually, or just short lines)
            # In IVTFF, labels often appear in specific streams.
            # Let's look for unique words in this section that don't appear elsewhere.
            
            cleaned = line.replace(".", " ").replace("!", "").replace("*", "")
            words = [w for w in cleaned.split() if not w.startswith("<") and w != "-"]
            stars.extend(words)
            
    # Frequency Analysis
    counts = Counter(stars)
    
    # Group by frequency (looking for sets of 12, 7, 28)
    # This is a heuristic: if 12 words appear exactly once on a Zodiac page, they are the signs.
    
    freq_map = {}
    for w, c in counts.items():
        if c not in freq_map: freq_map[c] = []
        freq_map[c].append(w)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Astro Structure Analysis\n\n")
        
        f.write("## Potential Zodiac Candidates (Set of 12?)\n")
        # Look for counts around 12 (or multiples)
        found = False
        for count in range(10, 15): 
            if count in freq_map:
                words = freq_map[count]
                f.write(f"### Words appearing {count} times: {len(words)} words\n")
                f.write(", ".join(words[:20]) + "\n")
                found = True
        
        if not found:
            f.write("No clear set of 12 found by simple frequency.\n")
            
        f.write("\n## Top Astro Terms (Frequency > 20)\n")
        top = counts.most_common(50)
        for w, c in top:
            f.write(f"- **{w}**: {c}\n")

    print(f"Mining complete: {output_file}")

if __name__ == "__main__":
    mine_astro_stars(
        "data/eva_ivtff.txt",
        "results/astro_structure_analysis.md"
    )
