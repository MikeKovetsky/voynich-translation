import json
import re
import os
from collections import defaultdict

def load_dictionary(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)["entries"]

def get_section(page_id):
    # Robust Page ID parsing
    # Format is usually f100r or f1r
    if not page_id: return "Unknown"
    
    if page_id.startswith("f10") or page_id.startswith("f11"): return "Recipes"
    
    # Extract numeric part
    match = re.search(r'\d+', page_id)
    if not match: return "Unknown"
    
    num = int(match.group())
    
    if num <= 66: return "Herbal"
    if 67 <= num <= 73: return "Astro"
    if 75 <= num <= 84: return "Bio"
    if 85 <= num <= 86: return "Cosmo"
    if 87 <= num <= 102: return "Pharma"
    
    return "Unknown"

def generate_coverage_heatmap(text_file, dict_file, report_file):
    print("Generating Global Coverage Heatmap...")
    entries = load_dictionary(dict_file)
    
    # Stats Storage
    page_stats = defaultdict(lambda: {"total": 0, "known": 0})
    section_stats = defaultdict(lambda: {"total": 0, "known": 0})
    
    # Iterate Pages
    current_page = "Unknown"
    with open(text_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Detect Page ID
            match = re.match(r"<(f\d+[rv]\d?)\.", line)
            if match:
                current_page = match.group(1)
            
            if line.startswith("#"): continue
            
            cleaned = line.replace(".", " ").replace("!", "").replace("*", "")
            words = cleaned.split()
            
            for w in words:
                if w.startswith("<") or w == "-": continue
                
                # Check Dictionary
                is_known = False
                if w in entries:
                    is_known = True
                else:
                    # Root check (simple suffix stripping)
                    for suff in ['y', 'ol', 'dy', 'aiin']:
                        if w.endswith(suff) and w[:-len(suff)] in entries:
                            is_known = True
                            break
                            
                page_stats[current_page]["total"] += 1
                if is_known: page_stats[current_page]["known"] += 1
                
                sect = get_section(current_page)
                section_stats[sect]["total"] += 1
                if is_known: section_stats[sect]["known"] += 1

    # Report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Global Coverage Report (Dictionary v18)\n\n")
        
        f.write("## Section Summary\n")
        f.write("| Section | Total Words | Known Words | Coverage % |\n|---|---|---|---|\n")
        for sect, stats in section_stats.items():
            pct = (stats["known"] / stats["total"] * 100) if stats["total"] > 0 else 0
            f.write(f"| {sect} | {stats['total']} | {stats['known']} | **{pct:.1f}%** |\n")
            
        f.write("\n## Dark Zones (< 50% Coverage)\n")
        f.write("| Page | Section | Coverage % |\n|---|---|---|\n")
        for page, stats in sorted(page_stats.items()):
            if stats["total"] < 10: continue
            pct = (stats["known"] / stats["total"] * 100)
            if pct < 50:
                f.write(f"| {page} | {get_section(page)} | {pct:.1f}% |\n")

    print(f"Heatmap complete: {report_file}")

if __name__ == "__main__":
    generate_coverage_heatmap(
        "data/eva_ivtff.txt",
        "results/dictionary/master_dictionary_v18.json",
        "results/global_coverage_report.md"
    )
