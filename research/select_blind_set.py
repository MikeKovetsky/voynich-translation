import re
import random
import os

def select_blind_set(input_file, output_file_raw, output_file_manifest):
    """
    Selects 5 pages that are:
    1. High text density (>10 lines).
    2. NOT in Quire 20 (Recipe) or Bio (f75-f84).
    3. Ideally 'Paragraph' heavy.
    """
    pages = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r"<(f\d+[rv]\d?)\.(\d+).*?;H>\s+(.*)", line)
            if match:
                pid = match.group(1)
                text = match.group(3)
                if pid not in pages:
                    pages[pid] = []
                pages[pid].append(text)
                
    # Filter Candidates
    candidates = []
    for pid, lines in pages.items():
        # Exclude Recipes (f103-f116)
        if pid.startswith("f10") or pid.startswith("f11"): continue
        # Exclude Bio (f75-f84)
        num = int(re.search(r'\d+', pid).group())
        if 75 <= num <= 84: continue
        
        # Must have > 15 lines
        if len(lines) > 15:
            candidates.append(pid)
            
    print(f"Found {len(candidates)} candidate pages.")
    
    # Select 5 Random
    selected = random.sample(candidates, 5)
    
    # Write Manifest
    with open(output_file_manifest, 'w', encoding='utf-8') as f:
        f.write("# Track 314: Blind Set Manifest\n\n")
        f.write("The following pages were selected for Blind Translation (No Images allowed).\n\n")
        for pid in selected:
            f.write(f"- **{pid}**: {len(pages[pid])} lines.\n")
            
    # Write Raw Text
    with open(output_file_raw, 'w', encoding='utf-8') as f:
        for pid in selected:
            f.write(f"# PAGE {pid}\n")
            for line in pages[pid]:
                f.write(line + "\n")
            f.write("\n")

    print(f"Selection complete. Manifest: {output_file_manifest}")

if __name__ == "__main__":
    select_blind_set("data/eva_ivtff.txt", "data/blind_set_raw.txt", "results/blind_set_manifest.md")
