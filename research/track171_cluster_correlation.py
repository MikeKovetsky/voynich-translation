import json
import re
import pandas as pd
import os
from collections import defaultdict

# File paths
NOUN_CLUSTERS_PATH = 'results/noun_clusters.json'
IVTFF_PATH = 'data/eva_ivtff.txt'
OUTPUT_CSV = 'results/cluster_distribution.csv'
OUTPUT_REPORT = 'results/cluster_validation_report.md'
OUTPUT_SUMMARY = 'results/track-171-results_summary.md'

# Section Definitions
SECTIONS = {
    "Herbal": [
        (1, 57),
        (87, 102)
    ],
    "Astronomical": [
        (67, 73)
    ],
    "Biological": [
        (75, 84)
    ],
    "Recipes": [
        (103, 116)
    ],
    "Rosettes": [
        (85, 86)
    ]
}

def parse_folio(page_id):
    """
    Parses a page ID like 'f1r' or 'f116v' into a number and side.
    Returns (number, side) tuple, or None if invalid.
    """
    match = re.match(r'f(\d+)([rv]?)', page_id)
    if match:
        return int(match.group(1)), match.group(2)
    return None, None

def get_section(page_id):
    """
    Determines the section for a given page ID.
    Returns the section name or 'Unknown'.
    """
    num, _ = parse_folio(page_id)
    if num is None:
        return "Unknown"
    
    for section, ranges in SECTIONS.items():
        for start, end in ranges:
            if start <= num <= end:
                return section
    return "Unknown"

def load_ivtff_text(path):
    """
    Parses the IVTFF file to extract text grouped by page.
    Returns a dict: { "f1r": "word1 word2 ...", ... }
    """
    print(f"Reading {path}...")
    page_text = defaultdict(list)
    
    lines_data = defaultdict(dict) # { (page, line_num): { 'H': text, 'C': text, ... } }
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Match: <f1r.1,...;T> text
            match = re.match(r'<((f\d+[rv])[^>]*);(\w)>\s+(.*)', line)
            if match:
                full_tag = match.group(1)
                page_id = match.group(2)
                transcriber = match.group(3)
                text = match.group(4)
                
                # Use full tag as unique line identifier
                line_key = full_tag
                lines_data[line_key][transcriber] = text

    # Reconstruct pages
    PREFERRED = ['H', 'C', 'F', 'N', 'U', 'm', 'c']
    
    for line_key, versions in lines_data.items():
        page_match = re.match(r'(f\d+[rv]?)', line_key)
        if not page_match:
            continue
        page_id = page_match.group(1)
        
        selected_text = ""
        for t in PREFERRED:
            if t in versions:
                selected_text = versions[t]
                break
        if not selected_text and versions:
            selected_text = next(iter(versions.values()))
            
        if selected_text:
            # Clean text: remove comments {comment}
            selected_text = re.sub(r'\{.*?\}', '', selected_text)
            
            # Replace dots with spaces
            selected_text = selected_text.replace('.', ' ')
            
            page_text[page_id].append(selected_text)
            
    # Join lines
    final_pages = {}
    for pid, lines in page_text.items():
        final_pages[pid] = " ".join(lines)
        
    return final_pages

def main():
    print("Loading data...")
    with open(NOUN_CLUSTERS_PATH, 'r') as f:
        json_data = json.load(f)
        
    # Handle "noun_to_cluster" key if present
    if "noun_to_cluster" in json_data:
        noun_clusters = json_data["noun_to_cluster"]
    else:
        noun_clusters = json_data

    # Check format: Word -> Cluster ID
    first_val = next(iter(noun_clusters.values()))
    if isinstance(first_val, list):
        print("Inverting noun clusters map...")
        temp_clusters = {}
        for cid, words in noun_clusters.items():
            for w in words:
                temp_clusters[w] = cid
        noun_clusters = temp_clusters

    parsed_text = load_ivtff_text(IVTFF_PATH)
    print(f"Loaded text for {len(parsed_text)} pages.")

    print("Analyzing frequencies...")
    
    section_total_words = defaultdict(int)
    cluster_section_counts = defaultdict(lambda: defaultdict(int))
    
    # Iterate over pages
    for page_id, text in parsed_text.items():
        section = get_section(page_id)
        if section == "Unknown":
            continue
            
        words = text.split()
        section_total_words[section] += len(words)
        
        for word in words:
            # Clean word: keep only alpha
            clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)
            if not clean_word:
                continue
                
            if clean_word in noun_clusters:
                cid = noun_clusters[clean_word]
                cluster_section_counts[cid][section] += 1

    print("Calculating stats...")
    
    cluster_ids = sorted(cluster_section_counts.keys())
    section_names = sorted(SECTIONS.keys())
    
    rows = []
    for cid in cluster_ids:
        row = {'Cluster ID': cid}
        total_hits = 0
        for sec in section_names:
            count = cluster_section_counts[cid][sec]
            norm_freq = 0
            if section_total_words[sec] > 0:
                norm_freq = (count / section_total_words[sec]) * 10000 # Per 10k words
            
            row[f'{sec}_Count'] = count
            row[f'{sec}_Freq'] = norm_freq
            total_hits += count
        
        # Determine dominant section
        best_sec = None
        best_share = 0
        
        if total_hits > 0:
            for sec in section_names:
                share = cluster_section_counts[cid][sec] / total_hits
                if share > best_share:
                    best_share = share
                    best_sec = sec
        
        row['Dominant_Section'] = best_sec
        row['Dominant_Share'] = best_share
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    # Save CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {OUTPUT_CSV}")
    
    # Generate Report
    report_lines = []
    report_lines.append("# Cluster Validation Report")
    report_lines.append("")
    report_lines.append("## Section-Specific Clusters (>80% distribution)")
    report_lines.append("")
    
    candidates = defaultdict(list)
    
    for _, row in df.iterrows():
        if row['Dominant_Share'] >= 0.8:
            sec = row['Dominant_Section']
            candidates[sec].append(row['Cluster ID'])
            
    for sec in section_names:
        clusters = candidates[sec]
        report_lines.append(f"### {sec} Candidates")
        if clusters:
            report_lines.append(f"- Found {len(clusters)} clusters: {', '.join(str(c) for c in clusters)}")
        else:
            report_lines.append("- None")
        report_lines.append("")
        
    report_lines.append("## Stats")
    report_lines.append(f"Total Words Processed: {sum(section_total_words.values())}")
    for sec, count in section_total_words.items():
        report_lines.append(f"- {sec}: {count} words")

    # Save Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("\n".join(report_lines))
    print(f"Saved {OUTPUT_REPORT}")

    # Save Summary
    summary_lines = []
    summary_lines.append("# Task 171 Results Summary")
    summary_lines.append("")
    summary_lines.append("## Key Findings")
    summary_lines.append(f"- Analyzed {len(df)} clusters.")
    summary_lines.append("- Identified section-specific distributions.")
    for sec, clusters in candidates.items():
         summary_lines.append(f"- **{sec}**: {len(clusters)} unique clusters.")
    
    summary_lines.append("")
    summary_lines.append("## Next Steps")
    summary_lines.append("- Verify 'Herbal' clusters against plant illustrations.")
    summary_lines.append("- Investigate 'shared' clusters that appear everywhere (common nouns?).")
    
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("\n".join(summary_lines))
    print(f"Saved {OUTPUT_SUMMARY}")

if __name__ == "__main__":
    main()