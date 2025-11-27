import json
import re
import os

def load_transcription(filepath, pages):
    """
    Reads the IVTFF file and extracts words for the specified pages.
    Prefers transcription 'H' (Takahashi) if available, otherwise first available.
    """
    page_words = {page: [] for page in pages}
    
    with open(filepath, 'r') as f:
        for line in f:
            # Check if line belongs to one of our pages
            # Format example: <f41r.1,@P0;H>
            match = re.match(r'^<([a-z0-9]+)\.[^>]+>(\s*)(.*)$', line)
            if match:
                page_id = match.group(1)
                if page_id in pages:
                    # We only want the 'H' transcription or if not available, maybe just use H for consistency
                    # The line usually ends with transcription code, e.g. ;H>
                    # Let's check the tag content
                    tag_content = line.split('>')[0]
                    if ';H' in tag_content: 
                        # Extract text content
                        # content is after the first >
                        content = line.split('>', 1)[1].strip()
                        
                        # Remove comments/tags within text like <-><!plant> or <...>
                        # Also remove inline comments { ... } if any, though usually IVTFF puts them differently
                        # Clean <...> tags
                        content = re.sub(r'<[^>]+>', ' ', content)
                        
                        # Clean uncertain characters like !, ?, * 
                        # We'll keep simple EVA chars. 
                        # Words are separated by . or spaces
                        words = content.replace('.', ' ').split()
                        
                        clean_words = []
                        for w in words:
                            # Remove punctuation/special chars
                            w_clean = re.sub(r'[^a-z0-9]', '', w)
                            if w_clean:
                                clean_words.append(w_clean)
                        
                        page_words[page_id].extend(clean_words)
                        
    return page_words

def analyze_zodiac_links(zodiac_data, page_words, target_page, fire_signs, water_signs):
    results = {
        "page": target_page,
        "fire_links": [],
        "water_links": [],
        "top_matches": [],
        "details": {}
    }
    
    if target_page not in zodiac_data:
        print(f"Warning: {target_page} not in zodiac data")
        return results

    page_zodiac = zodiac_data[target_page]
    all_matches = page_zodiac.get("all_matches", [])
    
    # Sort matches by score descending
    sorted_matches = sorted(all_matches, key=lambda x: x['score'], reverse=True)
    results["top_matches"] = sorted_matches[:3]
    
    # Filter for Fire and Water signs
    fire_matches = [m for m in all_matches if m['sign'] in fire_signs]
    water_matches = [m for m in all_matches if m['sign'] in water_signs]
    
    results["fire_links"] = fire_matches
    results["water_links"] = water_matches
    
    # Analyze words specifically for Fire signs
    fire_words = set()
    for m in fire_matches:
        for w in m.get("shared_words", []):
            fire_words.add(w)
            
    results["details"]["fire_words"] = list(fire_words)
    
    # Check "Hot" words (morphology) - simple heuristic based on task description
    # Task mentions: sho, qokeey (Burn, Cook)
    hot_words_found = []
    hot_stems = ["sho", "qok"] 
    
    for w in fire_words:
        if any(stem in w for stem in hot_stems):
            hot_words_found.append(w)
            
    results["details"]["hot_words"] = hot_words_found
    
    return results

def main():
    # Inputs
    zodiac_file = "results/herbal_zodiac_links_v2.json"
    transcription_file = "data/eva_ivtff.txt"
    
    target_page = "f41r" # Thistle/Nettle
    spiky_pages = ["f21r", "f24r"]
    watery_page = "f2v" # Nymphaea
    
    pages_to_load = [target_page] + spiky_pages + [watery_page]
    
    print("Loading transcription...")
    page_words = load_transcription(transcription_file, pages_to_load)
    
    print("Loading zodiac links...")
    with open(zodiac_file, 'r') as f:
        zodiac_data = json.load(f)
        
    fire_signs = ["Aries", "Leo", "Sagittarius"]
    water_signs = ["Pisces", "Cancer", "Scorpio"]
    
    # 1. Analyze f41r (Thistle)
    print(f"Analyzing {target_page}...")
    f41r_analysis = analyze_zodiac_links(zodiac_data, page_words, target_page, fire_signs, water_signs)
    
    # 2. Cross-check Spiky plants (f21r, f24r)
    spiky_analysis = {}
    for p in spiky_pages:
        print(f"Analyzing {p}...")
        spiky_analysis[p] = analyze_zodiac_links(zodiac_data, page_words, p, fire_signs, water_signs)
        
    # 3. Cross-check Watery plant (f2v)
    print(f"Analyzing {watery_page}...")
    watery_analysis = analyze_zodiac_links(zodiac_data, page_words, watery_page, fire_signs, water_signs) # Check Water signs for this one
    
    # Generate Report
    output_lines = []
    output_lines.append("# Zodiac-Herbal Validation Report (Track 294)")
    output_lines.append("## 1. Analysis of f41r (Thistle/Nettle)")
    
    # Show Top Matches
    top = f41r_analysis["top_matches"]
    output_lines.append("### Top 3 Zodiac Matches:")
    for m in top:
        output_lines.append(f"- **{m['sign']}**: Score {m['score']}")
        
    fire_links = f41r_analysis["fire_links"]
    if fire_links:
        output_lines.append("\n### Fire Sign Links (Specific):")
        for m in fire_links:
            output_lines.append(f"  - **{m['sign']}**: Score {m['score']}, Jaccard {m['jaccard']:.4f}")
            output_lines.append(f"    - Shared Words: {', '.join(m['shared_words'])}")
    else:
        output_lines.append("- No significant linkage to Fire Signs found.")
        
    hot_words = f41r_analysis["details"]["hot_words"]
    output_lines.append(f"\n### Vocabulary Analysis")
    output_lines.append(f"- **'Hot' Words identified**: {', '.join(hot_words) if hot_words else 'None'}")
    output_lines.append("  - (Checking for stems: sho, qok)")

    output_lines.append("\n## 2. Cross-Check: Spiky Plants (f21r, f24r)")
    for p, data in spiky_analysis.items():
        links = data["fire_links"]
        output_lines.append(f"### {p}")
        # Top matches for context
        top = data["top_matches"]
        output_lines.append(f"  - Top Matches: {', '.join([f'{m['sign']} ({m['score']})' for m in top])}")
        if links:
             for m in links:
                output_lines.append(f"  - **{m['sign']}** (Fire): Score {m['score']}")
        else:
            output_lines.append("  - No Fire Sign links.")

    output_lines.append("\n## 3. Cross-Check: Watery Plant (f2v)")
    w_links = watery_analysis["water_links"]
    output_lines.append(f"### {watery_page} (Nymphaea)")
    top = watery_analysis["top_matches"]
    output_lines.append(f"  - Top Matches: {', '.join([f'{m['sign']} ({m['score']})' for m in top])}")
    if w_links:
        for m in w_links:
            output_lines.append(f"  - **{m['sign']}** (Water): Score {m['score']}")
            output_lines.append(f"    - Shared Words: {', '.join(m['shared_words'][:10])}...")
    else:
        output_lines.append("  - No Water Sign links.")

    # Write Report
    with open("results/zodiac_plant_validation.md", "w") as f:
        f.write("\n".join(output_lines))
        
    print("Report generated: results/zodiac_plant_validation.md")
    
    # Summary
    summary = []
    summary.append("# Track 294 Results Summary")
    summary.append("## Does the Astrology hypothesis hold?")
    
    # Refined heuristic
    # f41r: Is a Fire sign in top 3?
    f41r_top_signs = [m['sign'] for m in f41r_analysis["top_matches"]]
    f41r_fire_in_top = any(s in fire_signs for s in f41r_top_signs)
    
    # f2v: Is a Water sign in top 3?
    f2v_top_signs = [m['sign'] for m in watery_analysis["top_matches"]]
    f2v_water_in_top = any(s in water_signs for s in f2v_top_signs)
    
    if f41r_fire_in_top:
        status = "CONFIRMED" if f2v_water_in_top else "PARTIAL"
        desc = "f41r strongly links to Fire signs, " + ("and f2v links to Water signs." if f2v_water_in_top else "but f2v does not link to Water signs.")
    else:
        status = "NEGATIVE"
        desc = "f41r does not prioritize Fire signs."

    summary.append(f"{status}. {desc}")
    summary.append(f"\n- **f41r Top Signs**: {', '.join(f41r_top_signs)}")
    summary.append(f"- **f2v Top Signs**: {', '.join(f2v_top_signs)}")
    
    with open("results/track-294-results_summary.md", "w") as f:
        f.write("\n".join(summary))
        
    print("Summary generated: results/track-294-results_summary.md")

if __name__ == "__main__":
    main()
