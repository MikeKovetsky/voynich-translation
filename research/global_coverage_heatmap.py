import json
import os
import sys
import re
from collections import defaultdict

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

try:
    import research.voynich_data as voynich_data
    from research.morphology_engine import strip_suffixes
except ImportError:
    # Fallback if running from research directory
    sys.path.append(os.path.join(os.getcwd(), '..'))
    import research.voynich_data as voynich_data
    from research.morphology_engine import strip_suffixes

def load_dictionary(path):
    print(f"Loading dictionary from {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('entries', {})
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at {path}")
        sys.exit(1)

def get_section_mapping():
    """
    Creates a mapping from folio name to section category.
    Handles foldouts (e.g., f67r1 -> f67r) and missing definitions.
    """
    folio_to_section = {}
    
    # 1. Base mapping from voynich_data
    # Target: Bio, Astro, Herbal, Pharma, Recipes, Cosmo
    section_map = {
        'herbal_a': 'Herbal',
        'herbal_b': 'Herbal',
        'astronomical': 'Astro',
        'biological': 'Bio',
        'pharmaceutical': 'Pharma',
        'recipes': 'Recipes',
        'zodiac': 'Astro',
        'cosmological': 'Cosmo'
    }

    # Check if FOLIO_SECTIONS exists in voynich_data
    if hasattr(voynich_data, 'FOLIO_SECTIONS'):
        for internal_section, target_category in section_map.items():
            folios = voynich_data.FOLIO_SECTIONS.get(internal_section, [])
            for folio in folios:
                folio_clean = folio.lower()
                folio_to_section[folio_clean] = target_category
    
    # 2. Manual Overrides / Additions for complex pages
    # Cosmo / Rosettes
    for i in [85, 86]:
        folio_to_section[f"f{i}r"] = "Cosmo"
        folio_to_section[f"f{i}v"] = "Cosmo"
    
    # Pharma Foldouts & Gaps (f87-f102)
    # Note: voynich_data might miss foldouts like f89r1
    # We will handle suffixes in the lookup, but we need base definitions
    for i in range(87, 103): # 87 to 102
        if f"f{i}r" not in folio_to_section: folio_to_section[f"f{i}r"] = "Pharma"
        if f"f{i}v" not in folio_to_section: folio_to_section[f"f{i}v"] = "Pharma"

    # Herbal Gaps
    for i in range(57, 67):
         if f"f{i}r" not in folio_to_section: folio_to_section[f"f{i}r"] = "Herbal"
         if f"f{i}v" not in folio_to_section: folio_to_section[f"f{i}v"] = "Herbal"

    return folio_to_section

def get_section_for_folio(folio, mapping):
    """
    Resolves section for a folio, handling suffixes like 'f67r1'.
    """
    folio = folio.lower()
    
    # 1. Exact match
    if folio in mapping:
        return mapping[folio]
    
    # 2. Strip foldout suffixes (r1, r2, v1, v2, v3)
    # Match f123r or f123v
    base_match = re.match(r"(f\d+[rv])\d?", folio)
    if base_match:
        base_folio = base_match.group(1)
        if base_folio in mapping:
            return mapping[base_folio]
            
    return 'Unknown'

def analyze_coverage():
    # Paths
    dict_path = "results/dictionary/master_dictionary_v18.json"
    output_report = "results/global_coverage_report.md"
    
    # Load Dictionary
    dictionary = load_dictionary(dict_path)
    
    # Load Pages
    print("Loading pages...")
    pages = voynich_data.get_eva_pages(transcriber='H')
    
    # Section Mapping
    folio_to_section_map = get_section_mapping()
    
    # Statistics storage
    # page_stats: {folio: {'total': 0, 'known': 0, 'root_match': 0, 'coverage': 0.0, 'section': ''}}
    page_stats = {}
    
    # Section stats: {section: {'total': 0, 'known': 0, 'root_match': 0}}
    section_stats = defaultdict(lambda: {'total': 0, 'known': 0, 'root_match': 0})
    
    print("Analyzing coverage...")
    for folio, lines in pages.items():
        folio_clean = folio.lower()
        section = get_section_for_folio(folio_clean, folio_to_section_map)
        
        total_words = 0
        known_words = 0
        root_matches = 0
        
        for loc, line_text in lines.items():
            # Cleanup text (remove tags, punctuation)
            text_no_tags = re.sub(r'<[^>]+>', '', line_text)
            text_clean = re.sub(r'[!?<>@$\d]', '', text_no_tags)
            # Split by space, dot, comma
            words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 1]
            
            for word in words:
                total_words += 1
                
                # 1. Check Exact Match
                if word in dictionary:
                    known_words += 1
                else:
                    # 2. Check Root Match
                    root, suffix = strip_suffixes(word)
                    if root in dictionary:
                        root_matches += 1
        
        # Calculate Page Coverage
        readable = known_words + root_matches
        coverage = (readable / total_words * 100) if total_words > 0 else 0.0
        
        page_stats[folio] = {
            'total': total_words,
            'known': known_words,
            'root_match': root_matches,
            'coverage': coverage,
            'section': section
        }
        
        # Add to Section Stats
        section_stats[section]['total'] += total_words
        section_stats[section]['known'] += known_words
        section_stats[section]['root_match'] += root_matches

    # Generate Report
    print(f"Generating report to {output_report}...")
    
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write("# Global Coverage Heatmap (Track 327)\n\n")
        f.write(f"**Dictionary Version:** {dict_path}\n")
        f.write(f"**Total Pages Analyzed:** {len(page_stats)}\n\n")
        
        # 1. Section Summary
        f.write("## 1. Readability by Section\n")
        f.write("| Section | Total Words | Known (Exact) | Root Matches | **Total Readability** |\n")
        f.write("|---|---|---|---|---|\n")
        
        # Sort sections by readability
        sorted_sections = []
        for sec, stats in section_stats.items():
            total = stats['total']
            if total == 0: continue
            known = stats['known']
            roots = stats['root_match']
            readability = ((known + roots) / total) * 100
            sorted_sections.append((sec, total, known, roots, readability))
            
        sorted_sections.sort(key=lambda x: x[4], reverse=True)
        
        for sec, total, known, roots, read in sorted_sections:
            f.write(f"| **{sec}** | {total} | {known} ({known/total*100:.1f}%) | {roots} ({roots/total*100:.1f}%) | **{read:.1f}%** |\n")
            
        # 2. Dark Zones (Pages < 40%)
        f.write("\n## 2. Dark Zones (Pages < 40% Coverage)\n")
        f.write("These pages are likely unreadable with the current dictionary/grammar.\n\n")
        f.write("| Page | Section | Coverage | Missing Words |\n")
        f.write("|---|---|---|---|\n")
        
        dark_zones = []
        for folio, stats in page_stats.items():
            if stats['coverage'] < 40.0 and stats['total'] > 10: # Filter out empty/low-content pages
                missing = stats['total'] - (stats['known'] + stats['root_match'])
                dark_zones.append((folio, stats['section'], stats['coverage'], missing))
        
        # Sort by coverage (lowest first)
        dark_zones.sort(key=lambda x: x[2])
        
        for folio, sec, cov, miss in dark_zones:
            f.write(f"| {folio} | {sec} | **{cov:.1f}%** | {miss} |\n")
            
        if not dark_zones:
            f.write("No Dark Zones found! All pages > 40% coverage.\n")

        # 3. Recipe Section Audit
        f.write("\n## 3. Recipe Section Audit (Quire 20)\n")
        recipes_stats = section_stats.get('Recipes', {'total': 0, 'known': 0, 'root_match': 0})
        total_recipes = recipes_stats['total']
        if total_recipes > 0:
            read_recipes = ((recipes_stats['known'] + recipes_stats['root_match']) / total_recipes) * 100
            status = "READY" if read_recipes >= 80.0 else "NEEDS WORK"
            if read_recipes < 60.0: status = "CRITICAL FAILURE"
            
            f.write(f"- **Total Words:** {total_recipes}\n")
            f.write(f"- **Readability:** {read_recipes:.1f}%\n")
            f.write(f"- **Status:** **{status}**\n")
            
            if status == "READY":
                f.write("\n> The Recipe section meets the 80% readability threshold. Proceed with translation.\n")
            else:
                f.write(f"\n> The Recipe section is at {read_recipes:.1f}%, below the 80% target. Refine the dictionary for cooking terms.\n")
        else:
            f.write("No Recipe pages found.\n")

    print("Done.")

if __name__ == "__main__":
    analyze_coverage()
