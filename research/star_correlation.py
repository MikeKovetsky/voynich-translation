import csv
import re
import collections
from pathlib import Path

def read_star_colors(path):
    """Reads the star color map CSV."""
    star_map = {}
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row['folio'], int(row['index']))
            star_map[key] = row['color']
    return star_map

def read_paragraphs(path):
    """
    Reads results/segmented_text.txt and extracts paragraphs for Quire 20 (f103r-f116v).
    Returns a dict: {(folio, index): first_word}
    """
    paragraphs = {}
    
    # Pattern matches: <f103r.1,@P0;F> pched ...
    # Matches lines starting with <f...
    pattern = re.compile(r"^<([a-z0-9]+)\.(\d+).*?;([A-Z])>\s+(.*)")
    
    temp_data = collections.defaultdict(dict)
    
    with open(path, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        match = pattern.match(line)
        if match:
            folio = match.group(1)
            index = int(match.group(2))
            transcriber = match.group(3)
            text = match.group(4).strip()
            
            if not (folio.startswith('f10') or folio.startswith('f11')):
                continue
            
            # Remove comments { }
            text = re.sub(r"\{.*?\}", "", text).strip()
            if not text:
                continue
                
            words = text.split()
            if not words:
                continue
            
            first_word = words[0]
            
            # Cleanup
            first_word = first_word.replace('.', '').strip()
            
            temp_data[(folio, index)][transcriber] = first_word

    # Select best transcriber (F > H > U > m > c)
    priority = ['F', 'H', 'U', 'm', 'c']
    
    for key, transcribers in temp_data.items():
        selected = None
        for t in priority:
            if t in transcribers:
                selected = transcribers[t]
                break
        if not selected and transcribers:
            selected = list(transcribers.values())[0]
            
        paragraphs[key] = selected
            
    return paragraphs

def analyze_correlations(star_map, paragraphs):
    """
    Correlates Star Color with First Word.
    """
    data = []
    
    all_keys = set(star_map.keys()) | set(paragraphs.keys())
    
    relevant_keys = []
    for k in all_keys:
        folio = k[0]
        if folio.startswith('f10') or folio.startswith('f11'):
             if folio < 'f103r': continue
             if folio > 'f116v': continue
             relevant_keys.append(k)
    
    relevant_keys.sort()
    
    stats = collections.defaultdict(lambda: collections.Counter())
    
    for key in relevant_keys:
        color = star_map.get(key, "Unknown")
        word = paragraphs.get(key, "N/A")
        
        data.append({
            'folio': key[0],
            'index': key[1],
            'color': color,
            'word': word
        })
        
        if word != "N/A" and not word.startswith("?"):
            stats[color][word] += 1
            
    return data, stats

def main():
    star_map_path = 'results/star_color_map.csv'
    # Use segmented_text.txt which has spaces
    text_path = 'results/segmented_text.txt'
    
    if not Path(star_map_path).exists():
        print(f"Error: {star_map_path} not found.")
        return
    if not Path(text_path).exists():
        print(f"Error: {text_path} not found.")
        return

    star_map = read_star_colors(star_map_path)
    paragraphs = read_paragraphs(text_path)
    
    data, stats = analyze_correlations(star_map, paragraphs)
    
    output_csv = 'results/star_color_map.csv'
    with open(output_csv, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['folio', 'index', 'color', 'word'])
        writer.writeheader()
        writer.writerows(data)
        
    summary_path = 'results/track-214-results_summary.md'
    with open(summary_path, 'w') as f:
        f.write("# Task 214: Star Correlation Results\n\n")
        
        f.write("## 1. Color Distribution\n")
        total_stars = len(data)
        color_counts = collections.Counter([d['color'] for d in data])
        for c, count in color_counts.items():
            f.write(f"- **{c}**: {count}\n")
        f.write(f"\nTotal Paragraphs Analyzed: {total_stars}\n\n")
        
        f.write("## 2. Top Starter Words by Color\n")
        
        for color in ['Red', 'Yellow', 'Unknown']:
            f.write(f"### Color: {color}\n")
            if color not in stats:
                f.write("No data.\n")
                continue
            
            top_words = stats[color].most_common(10)
            f.write("| Word | Count | Percentage |\n")
            f.write("|---|---|---|\n")
            total_color = color_counts[color]
            for w, c in top_words:
                pct = (c / total_color) * 100 if total_color > 0 else 0
                f.write(f"| `{w}` | {c} | {pct:.1f}% |\n")
            f.write("\n")
            
        f.write("## 3. Specific Correlations\n")
        
        red_saiin = stats['Red'].get('saiin', 0)
        red_total = color_counts['Red']
        f.write(f"- **Red + `saiin`**: {red_saiin}/{red_total} ({red_saiin/red_total*100:.1f}%)\n" if red_total else "- **Red + `saiin`**: 0/0\n")
        
        yellow_daiin = stats['Yellow'].get('daiin', 0)
        yellow_total = color_counts['Yellow']
        f.write(f"- **Yellow + `daiin`**: {yellow_daiin}/{yellow_total} ({yellow_daiin/yellow_total*100:.1f}%)\n" if yellow_total else "- **Yellow + `daiin`**: 0/0\n")
        
        all_saiin = sum(s.get('saiin', 0) for s in stats.values())
        all_daiin = sum(s.get('daiin', 0) for s in stats.values())
        
        f.write(f"- **`saiin` (Total)**: {all_saiin}\n")
        f.write(f"- **`daiin` (Total)**: {all_daiin}\n")
        
        f.write("\n## 4. Hypothesis Testing\n")
        f.write("- **Hypothesis 1: Red = Hot/Mars/Iron?**\n")
        if red_saiin > 0 and red_saiin > (red_total * 0.5):
             f.write("  - **SUPPORTED**. Strong correlation found.\n")
        else:
             f.write("  - **Refuted/Weak**. No strong correlation observed.\n")
             
        f.write("- **Hypothesis 2: Blue = Cool/Venus/Water?**\n")
        f.write("  - Note: No 'Blue' stars found in dataset (only Red, Yellow, Unknown).\n")
        
    print(f"Analysis complete. Results written to {summary_path} and {output_csv}")

if __name__ == "__main__":
    main()
