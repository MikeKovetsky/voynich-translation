import json
import re
import os

def run_elemental_analysis():
    print("Loading Corpus...")
    try:
        with open("data/eva_ivtff.txt", "r") as f:
            text = f.read()
    except FileNotFoundError:
        print("Corpus not found. Creating dummy.")
        text = "<f1r> daiin ol oain <f1v> daiin o oain"

    # Split into Pages
    # EVA format usually has <fXXX> tags.
    pages = re.split(r"<f(\d+[rv])>", text)
    
    page_map = {}
    # re.split with capturing group returns [pre, tag, post, tag, post...]
    # If text starts with tag, pre is empty.
    
    current_folio = "unknown"
    
    # If the file is line-based with ID at start of line, logic differs. 
    # Standard EVA is often line based. Let's check line format.
    # Assuming <fXXX> tags or line IDs like <f76r.P.1>
    
    page_counts = {}

    lines = text.split("\n")
    for line in lines:
        # Extract Folio ID
        # Typical format: <f76r.P.1>;H       word word...
        match = re.search(r"<f(\d+[rv])", line)
        if match:
            folio = match.group(1)
            if folio not in page_counts:
                page_counts[folio] = {"ol": 0, "o": 0, "total": 0}
            
            words = re.findall(r"[a-z]+", line.lower())
            for w in words:
                if w == "ol" or w.startswith("ol") or w.endswith("ol"):
                    page_counts[folio]["ol"] += 1
                if w == "o" or w.startswith("o") or w.endswith("o"):
                    # Exclude 'ol' from 'o' count if it was just counted?
                    # 'ol' starts with 'o'. 
                    # Task says: count_ol: ol, ol-, -ol. count_o: o, o-, -o (excluding ol).
                    if "ol" not in w: 
                        page_counts[folio]["o"] += 1
                page_counts[folio]["total"] += 1

    # Classify
    results = {}
    wet_pages = []
    dry_pages = []
    
    for folio, counts in page_counts.items():
        ol = counts["ol"]
        o = counts["o"]
        total_elemental = ol + o
        
        if total_elemental == 0:
            ratio = 0.5 # Neutral
        else:
            ratio = ol / total_elemental
        
        classification = "Neutral"
        if ratio > 0.6:
            classification = "Wet"
            wet_pages.append(folio)
        elif ratio < 0.4:
            classification = "Dry"
            dry_pages.append(folio)
            
        results[folio] = {
            "ol": ol,
            "o": o,
            "ratio": round(ratio, 2),
            "class": classification
        }

    # Save Map
    with open("results/elemental_page_map.json", "w") as f:
        json.dump(results, f, indent=2)
        
    # Generate Summary
    summary = f"""# Track 231: Elemental Page Tagging Results

- **Total Pages Analyzed**: {len(results)}
- **Wet Pages (High 'ol')**: {len(wet_pages)}
- **Dry Pages (High 'o')**: {len(dry_pages)}

## Wettest Pages (Venus/Water)
{', '.join(sorted(wet_pages, key=lambda x: results[x]['ratio'], reverse=True)[:10])}

## Driest Pages (Mars/Fire)
{', '.join(sorted(dry_pages, key=lambda x: results[x]['ratio'])[:10])}

## Zodiac Correlation Check
- **Aries (f71r):** {results.get('71r', 'N/A')}
- **Taurus (f71v):** {results.get('71v', 'N/A')}
- **Gemini (f72r):** {results.get('72r', 'N/A')}
- **Cancer (f72v):** {results.get('72v', 'N/A')}
- **Leo (f73r):** {results.get('73r', 'N/A')}
- **Virgo (f73v):** {results.get('73v', 'N/A')}
- **Libra (f74r):** {results.get('74r', 'N/A')}
- **Scorpio (f74v):** {results.get('74v', 'N/A')}
- **Pisces (f70v):** {results.get('70v', 'N/A')}
"""
    with open("results/track-231-results_summary.md", "w") as f:
        f.write(summary)
        
    return results

if __name__ == "__main__":
    run_elemental_analysis()
