import json
import re
from pathlib import Path
import voynich_data

# Configuration
DICTIONARY_FILE = Path("results/master_dictionary_v6.json")
OUTPUT_JSON = Path("results/full_manuscript_translation.json")
OUTPUT_HEATMAP = Path("results/readability_heatmap.md")

def load_dictionary():
    with open(DICTIONARY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Extract entries mapping: voynich_word -> meaning
    entries = data.get('entries', {})
    translation_map = {}
    for word, info in entries.items():
        translation_map[word] = info.get('meaning', '???')
    return translation_map

def get_section(folio):
    # Normalize folio to match FOLIO_SECTIONS format (e.g. "f1r")
    # voynich_data returns keys like "f1r"
    for section, folios in voynich_data.FOLIO_SECTIONS.items():
        if folio in folios:
            return section
    return "unknown"

def process_manuscript():
    print("Loading dictionary...")
    dictionary = load_dictionary()
    
    print("Loading manuscript...")
    pages = voynich_data.get_eva_pages()
    
    results = {
        "total_pages": len(pages),
        "pages": {}
    }
    
    heatmap_data = []
    
    # Grammar markers for coherence scoring
    grammar_markers = {'daiin', 'qok', 'ol', 'chey', 'chedy', 'ar', 'al', 'aiin', 'qok-'}
    
    print(f"Processing {len(pages)} pages...")
    
    for folio, lines in pages.items():
        page_data = {
            "total_words": 0,
            "translated_words": 0,
            "lines": [],
            "coherence_score": 0
        }
        
        section = get_section(folio)
        
        for loc, text in lines.items():
            # Clean text and split into words
            # EVA text can have uncertain spaces, we use voynich_data's cleaning logic as reference
            text_clean = re.sub(r'[^\w\s\-\.,]', '', text)
            words = [w for w in re.split(r'[.\-=,\s]', text_clean) if w and len(w) > 0]
            
            translated_line_parts = []
            line_score = 0
            
            has_daiin_start = False
            has_qok = False
            
            if not words:
                continue

            for i, word in enumerate(words):
                page_data["total_words"] += 1
                
                # Translation lookup
                meaning = dictionary.get(word)
                
                # Check for qok- prefix logic if not direct match
                if not meaning and word.startswith('qok') and len(word) > 3:
                     root = word[3:]
                     root_meaning = dictionary.get(root)
                     if root_meaning:
                         meaning = f"of {root_meaning}"
                         # Add virtual word for scoring
                         line_score += 1 
                
                if meaning:
                    page_data["translated_words"] += 1
                    translated_line_parts.append(meaning)
                    line_score += 1 # Base score for translation
                    
                    # Grammar bonuses
                    if word in grammar_markers or word.startswith('qok'):
                        line_score += 2
                    
                    if word == 'daiin' and i == 0:
                        has_daiin_start = True
                    if word.startswith('qok'):
                         has_qok = True
                else:
                    translated_line_parts.append(f"[{word}]")
            
            # Additional Frame Bonuses
            if has_daiin_start:
                line_score += 5
            if has_qok:
                line_score += 3
            
            # Specific Frame: daiin ... qok ...
            if has_daiin_start and has_qok:
                line_score += 5
                
            page_data["lines"].append({
                "loc": loc,
                "original": text,
                "translation": " ".join(translated_line_parts),
                "score": line_score
            })
            
            page_data["coherence_score"] += line_score

        # Calculate page metrics
        if page_data["total_words"] > 0:
            page_data["translation_rate"] = (page_data["translated_words"] / page_data["total_words"]) * 100
        else:
            page_data["translation_rate"] = 0
            
        results["pages"][folio] = page_data
        
        heatmap_data.append({
            "folio": folio,
            "rate": page_data["translation_rate"],
            "score": page_data["coherence_score"],
            "section": section
        })

    # Save JSON results
    print(f"Saving translation results to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    # Generate Heatmap Markdown
    print(f"Generating heatmap report to {OUTPUT_HEATMAP}...")
    generate_heatmap_report(heatmap_data)
    
    print("Done.")

def generate_heatmap_report(data):
    # Sort by coherence score
    sorted_data = sorted(data, key=lambda x: x["score"], reverse=True)
    
    # Filter out recipes section for "Most Readable Outside Recipes" list
    non_recipe = [d for d in sorted_data if d["section"] != "recipes"]
    
    with open(OUTPUT_HEATMAP, 'w', encoding='utf-8') as f:
        f.write("# Readability Heatmap & Mass Translation Report\n\n")
        
        f.write("## Overview\n")
        f.write(f"Total Pages Analyzed: {len(data)}\n\n")
        
        f.write("## Top 20 Most Readable Pages (Global)\n")
        f.write("| Rank | Folio | Section | Translation % | Coherence Score |\n")
        f.write("|------|-------|---------|---------------|-----------------|\n")
        for i, d in enumerate(sorted_data[:20]):
            f.write(f"| {i+1} | {d['folio']} | {d['section']} | {d['rate']:.1f}% | {d['score']} |\n")
        f.write("\n")
        
        f.write("## Top 20 Most Readable Pages (Non-Recipe)\n")
        f.write("**Goal:** Identify next targets for deep analysis.\n\n")
        f.write("| Rank | Folio | Section | Translation % | Coherence Score |\n")
        f.write("|------|-------|---------|---------------|-----------------|\n")
        for i, d in enumerate(non_recipe[:20]):
            f.write(f"| {i+1} | {d['folio']} | {d['section']} | {d['rate']:.1f}% | {d['score']} |\n")
        f.write("\n")
        
        f.write("## Section Analysis\n")
        sections = {}
        for d in data:
            s = d["section"]
            if s not in sections:
                sections[s] = {"count": 0, "total_rate": 0, "total_score": 0}
            sections[s]["count"] += 1
            sections[s]["total_rate"] += d["rate"]
            sections[s]["total_score"] += d["score"]
            
        f.write("| Section | Pages | Avg Translation % | Avg Coherence Score |\n")
        f.write("|---------|-------|-------------------|---------------------|\n")
        for s, stats in sections.items():
            avg_rate = stats["total_rate"] / stats["count"]
            avg_score = stats["total_score"] / stats["count"]
            f.write(f"| {s} | {stats['count']} | {avg_rate:.1f}% | {avg_score:.1f} |\n")

if __name__ == "__main__":
    process_manuscript()

