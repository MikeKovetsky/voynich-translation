import csv
import re
from collections import defaultdict

def main():
    # 1. Load Data
    print("Reading results/star_color_map.csv...")
    star_map = defaultdict(list)
    with open('results/star_color_map.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            star_map[row['folio']].append(row)
            
    print(f"Loaded {len(star_map['f103r'])} stars for f103r.")
            
    starters = defaultdict(list)
    with open('results/recipe_starters_v2.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            starters[row['folio']].append(row)

    # 2. Generate Report
    output_lines = []
    output_lines.append("# Quire 20 Structural Map")
    output_lines.append("")
    output_lines.append("This map visualizes the organization of recipes in Quire 20, aligning margin stars with potential starter words.")
    output_lines.append("Note: Starter words are taken from the corresponding line number in the transcription. Alignment is approximate.")
    output_lines.append("")
    
    # Analysis Counters
    total_stars = 0
    red_stars = 0
    yellow_stars = 0
    sequences = [] # ('Red', 'Yellow', ...)
    
    sorted_folios = sorted(star_map.keys())
    
    for folio in sorted_folios:
        stars = star_map[folio]
        folio_starters = starters[folio]
        
        # Sort by index
        stars.sort(key=lambda x: int(x['index']))
        folio_starters.sort(key=lambda x: int(x['index']))
        
        output_lines.append(f"## Folio {folio}")
        output_lines.append("| Index | Star Color | Starter Word | Line |")
        output_lines.append("|---|---|---|---|")
        
        for i, star in enumerate(stars):
            color = star['color']
            idx = int(star['index'])
            
            # Find corresponding starter
            # Assuming 1-to-1 mapping for the first N lines.
            
            word = "N/A"
            line_num = "N/A"
            
            if i < len(folio_starters):
                word = folio_starters[i]['word']
                line_num = folio_starters[i]['index']
            
            output_lines.append(f"| {idx} | {color} | `{word}` | {line_num} |")
            
            total_stars += 1
            if 'Red' in color:
                red_stars += 1
            if 'Yellow' in color:
                yellow_stars += 1
                
            sequences.append(color)
            
        output_lines.append("")

    # 3. Analysis
    output_lines.append("## Analysis")
    output_lines.append(f"- **Total Stars**: {total_stars}")
    output_lines.append(f"- **Red Stars**: {red_stars}")
    output_lines.append(f"- **Yellow Stars**: {yellow_stars}")
    
    # Check for grouping
    groupings = []
    current_group = {'color': sequences[0] if sequences else '', 'count': 0}
    
    for color in sequences:
        if color == current_group['color']:
            current_group['count'] += 1
        else:
            groupings.append(current_group)
            current_group = {'color': color, 'count': 1}
    groupings.append(current_group)
    
    avg_group_size = sum(g['count'] for g in groupings) / len(groupings) if groupings else 0
    
    output_lines.append(f"- **Average Group Size**: {avg_group_size:.2f}")
    output_lines.append("")
    output_lines.append("### Grouping Observations")
    if avg_group_size < 1.5:
        output_lines.append("The stars appear to be highly interleaved (alternating colors).")
    else:
        output_lines.append(f"There is grouping of colors (Avg size: {avg_group_size:.2f}).")

    with open('results/quire20_structure.md', 'w') as f:
        f.write('\n'.join(output_lines))
        
    # 4. Write Summary
    summary_lines = []
    summary_lines.append("# Task 215 Results Summary")
    summary_lines.append(f"- Generated structural map for {len(sorted_folios)} folios.")
    summary_lines.append(f"- Mapped {total_stars} stars to recipe lines.")
    summary_lines.append(f"- Found {red_stars} Red stars and {yellow_stars} Yellow stars.")
    summary_lines.append(f"- Average color group size: {avg_group_size:.2f} (indicates {'alternating' if avg_group_size < 1.5 else 'grouping'}).")
    summary_lines.append("- Created `results/quire20_structure.md`.")
    
    with open('results/track-215-results_summary.md', 'w') as f:
        f.write('\n'.join(summary_lines))
        
    print("Analysis complete.")

if __name__ == "__main__":
    main()
