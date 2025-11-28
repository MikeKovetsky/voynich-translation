import sys
import os
import csv
from collections import defaultdict, Counter
import re

# Ensure we can import voynich_data from current directory
sys.path.append(os.getcwd())
import research.voynich_data as voynich_data

def get_section_mapping():
    """
    Creates a mapping from folio name to section category.
    """
    folio_to_section = {}
    
    # Map voynich_data sections to our target categories
    # Target: Bio, Astro, Herbal, Pharma, Recipes
    section_map = {
        'herbal_a': 'Herbal',
        'herbal_b': 'Herbal',
        'astronomical': 'Astro',
        'biological': 'Bio',
        'pharmaceutical': 'Pharma',
        'recipes': 'Recipes'
    }

    for internal_section, target_category in section_map.items():
        # Access the private dictionary if needed, or use the exposed one
        # voynich_data.FOLIO_SECTIONS is available
        folios = voynich_data.FOLIO_SECTIONS.get(internal_section, [])
        for folio in folios:
            folio_clean = folio.lower() # Ensure consistent casing
            folio_to_section[folio_clean] = target_category
            
    return folio_to_section

def analyze_root_distribution():
    print("Loading Voynich data...")
    # Get all pages (EVA, Takahashi)
    pages = voynich_data.get_eva_pages(transcriber='H')
    
    folio_to_section = get_section_mapping()
    
    # Count word frequencies per section
    # Structure: {word: {total: 0, 'Herbal': 0, 'Astro': 0, ...}}
    word_stats = defaultdict(lambda: defaultdict(int))
    global_freq = Counter()
    
    print("Analyzing word distribution across sections...")
    for folio, lines in pages.items():
        folio_clean = folio.lower()
        section = folio_to_section.get(folio_clean, 'Other')
        
        for loc, line_text in lines.items():
            # Remove IVTFF tags like <plant>, <figure>, etc. BEFORE other cleanup
            text_no_tags = re.sub(r'<[^>]+>', '', line_text)
            
            # Simple tokenization matching voynich_data logic
            text_clean = re.sub(r'[!?<>@$\d]', '', text_no_tags)
            words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 1]
            
            for word in words:
                global_freq[word] += 1
                word_stats[word]['total'] += 1
                word_stats[word][section] += 1

    # Identify Top 50 Roots
    top_50_roots = [w for w, c in global_freq.most_common(50)]
    print(f"Identified Top 50 roots: {top_50_roots}")

    # Prepare output data
    results = []
    
    # Categories to check for dominance
    categories = ['Herbal', 'Astro', 'Bio', 'Pharma', 'Recipes']
    
    report_lines = []
    report_lines.append("# Visual-Root Grounding Report (Track 321)")
    report_lines.append("\n## Methodology")
    report_lines.append("Analysis of the Top 50 most frequent roots in the Voynich Manuscript.")
    report_lines.append("Calculated distribution across sections (Herbal, Astro, Bio, Pharma, Recipes).")
    report_lines.append("Threshold for specialization: **90%** occurrences in a single section.\n")
    
    specialized_roots = []
    general_roots = []
    
    csv_rows = []

    print("Calculating distributions...")
    for root in top_50_roots:
        stats = word_stats[root]
        total = stats['total']
        
        # Find primary section
        primary_section = "None"
        max_pct = 0.0
        
        dist_str = []
        
        for cat in categories:
            count = stats[cat]
            pct = (count / total) * 100 if total > 0 else 0
            dist_str.append(f"{cat}: {pct:.1f}%")
            
            if pct > max_pct:
                max_pct = pct
                primary_section = cat
        
        # Determine if specialized
        is_specialized = max_pct >= 90.0
        confidence = "High" if is_specialized else "Low"
        
        # Tagging
        tag = ""
        if is_specialized:
            tag = f"[{primary_section.upper()}_TERM]"
            specialized_roots.append((root, primary_section, max_pct))
        else:
            general_roots.append((root, primary_section, max_pct))
            
        # Add to CSV data
        # Columns: Root, PrimarySection, Frequency, Confidence, Distribution
        csv_rows.append({
            'Root': root,
            'PrimarySection': primary_section if is_specialized else "General",
            'Frequency': total,
            'Confidence': f"{max_pct:.1f}%" if is_specialized else "N/A", # Or keep the percentage
            'Distribution': ", ".join(dist_str)
        })

    # Build Report
    report_lines.append("## Specialized Roots (>= 90% in one section)")
    if specialized_roots:
        report_lines.append("| Root | Section | Dominance |")
        report_lines.append("|---|---|---|")
        for root, sec, pct in specialized_roots:
            report_lines.append(f"| **{root}** | {sec} | {pct:.1f}% |")
    else:
        report_lines.append("No roots found with >= 90% dominance in a single section among the Top 50.")

    # Add Near-Specialized
    near_specialized = [r for r in general_roots if r[2] >= 80.0]
    if near_specialized:
        report_lines.append("\n## Near-Specialized Roots (80-90% in one section)")
        report_lines.append("| Root | Section | Dominance |")
        report_lines.append("|---|---|---|")
        for root, sec, pct in near_specialized:
            report_lines.append(f"| **{root}** | {sec} | {pct:.1f}% |")

    report_lines.append("\n## General Roots (Distributed)")
    report_lines.append("| Root | Primary Section | Dominance | Distribution |")
    report_lines.append("|---|---|---|---|")
    for root, sec, pct in general_roots:
        dist = ", ".join([f"{k}: {v/word_stats[root]['total']*100:.0f}%" for k,v in word_stats[root].items() if k in categories and v > 0])
        report_lines.append(f"| {root} | {sec} | {pct:.1f}% | {dist} |")

    # Save Report
    report_path = "results/visual_root_link_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Report saved to {report_path}")

    # Save CSV
    # Create artifacts directory if it doesn't exist
    os.makedirs("artifacts", exist_ok=True)
    csv_path = "artifacts/roots_by_section.csv"
    
    with open(csv_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Root', 'PrimarySection', 'Frequency', 'Confidence', 'Distribution'])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"CSV saved to {csv_path}")

if __name__ == "__main__":
    analyze_root_distribution()
