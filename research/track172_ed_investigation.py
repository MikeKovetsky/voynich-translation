import json
import os
import sys
from collections import Counter, defaultdict
import re

# Add research directory to path to import voynich_data
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from research import voynich_data

def load_parsed_text():
    with open("results/parsed_text.json", "r") as f:
        return json.load(f)

def load_noun_clusters():
    with open("results/noun_clusters.json", "r") as f:
        return json.load(f)

def get_ed_forms(parsed_data):
    """Identify all word forms that map to the 'ed' root."""
    ed_forms = set()
    ed_morphology = []
    
    for entry in parsed_data:
        if entry.get("root") == "ed":
            ed_forms.add(entry["original"])
            ed_morphology.append(entry)
    
    return ed_forms, ed_morphology

def analyze_morphology(ed_morphology):
    """Analyze prefixes and suffixes of 'ed' root words."""
    stats = {
        "prefix_counts": Counter(),
        "suffix_counts": Counter(),
        "total_occurrences": len(ed_morphology)
    }
    
    for entry in ed_morphology:
        for p in entry.get("prefix", []):
            stats["prefix_counts"][p] += 1
        for s in entry.get("suffix", []):
            stats["suffix_counts"][s] += 1
            
    return stats

def find_concordance(ed_forms, pages):
    """Find all occurrences of 'ed' forms in the text."""
    concordance = []
    
    # Flatten text for context window analysis
    # But we also want line references
    
    for folio, lines in pages.items():
        for loc, text in lines.items():
            # Clean text roughly to split into words
            words = text.split('.')
            for i, word in enumerate(words):
                # Handle EVA special chars if needed, but parsed_text usually has cleaned words
                # We'll stripping some common punctuation just in case
                clean_word = word.strip(',-') 
                
                if clean_word in ed_forms:
                    # Found a match
                    
                    # Get context (prev 5 words, next 5 words)
                    # This is tricky line-by-line. 
                    # For now, just take the whole line and the words around it in the line
                    
                    left_context = words[max(0, i-3):i]
                    right_context = words[i+1:min(len(words), i+4)]
                    
                    concordance.append({
                        "folio": folio,
                        "loc": loc,
                        "word": clean_word,
                        "line_text": text,
                        "left_context": left_context,
                        "right_context": right_context
                    })
    
    return concordance

def analyze_collocations(concordance):
    """Analyze words appearing near 'ed'."""
    left_words = Counter()
    right_words = Counter()
    
    for item in concordance:
        for w in item["left_context"]:
            if w: left_words[w] += 1
        for w in item["right_context"]:
            if w: right_words[w] += 1
            
    return left_words, right_words

def check_hypothesis(concordance, parsed_data):
    """
    Check distributions against hypotheses.
    """
    # Check section distribution
    section_counts = Counter()
    
    # Fix mapping logic
    # FOLIO_SECTIONS keys are like 'f1r', 'f1v'
    # pages keys are like 'f1r', 'f1v' (from voynich_data.get_eva_pages logic)
    
    folio_to_section = {}
    for section, folios in voynich_data.FOLIO_SECTIONS.items():
        for f in folios:
            # Normalize to match pages keys: 'f' + number + 'r'/'v'
            # Input in FOLIO_SECTIONS is already 'f1r'
            folio_to_section[f] = section
            
    for item in concordance:
        f = item["folio"]
        sec = folio_to_section.get(f, "unknown")
        section_counts[sec] += 1
        
    # Check semantic associations
    # Hypothesis: ed is related to "Light", "Fire", "Air", "Mix", "Stone"
    # We check co-occurrence with proxy words for these concepts
    
    semantic_proxies = {
        "Light/Star": ["ees", "eos", "heo", "rol", "lor"],
        "Mix/Process": ["fch", "qo", "saiin", "laiin"],
        "Stone/Earth": ["ar", "al", "or"],
        "Air": ["or", "ol"], 
        "Fire": ["fa", "fal"] # Guessing based on sound/common patterns or just checking near 'fch'
    }
    
    semantic_associations = defaultdict(int)
    
    for item in concordance:
        context = item["left_context"] + item["right_context"]
        for w in context:
            for category, proxies in semantic_proxies.items():
                if w in proxies:
                    semantic_associations[category] += 1
                    
    return section_counts, semantic_associations

def main():
    print("Loading data...")
    parsed_data = load_parsed_text()
    noun_clusters = load_noun_clusters()
    pages = voynich_data.get_eva_pages()
    
    print("Identifying 'ed' forms...")
    ed_forms, ed_morphology = get_ed_forms(parsed_data)
    print(f"Found {len(ed_forms)} unique forms for root 'ed'.")
    
    print("Analyzing morphology...")
    morph_stats = analyze_morphology(ed_morphology)
    
    print("Finding concordance...")
    concordance = find_concordance(ed_forms, pages)
    print(f"Found {len(concordance)} occurrences in text.")
    
    print("Analyzing collocations...")
    left_col, right_col = analyze_collocations(concordance)
    
    print("Testing hypotheses (Distribution & Semantics)...")
    section_dist, semantic_assocs = check_hypothesis(concordance, parsed_data)
    
    # Prepare Output
    output_lines = []
    output_lines.append("# Root `ed` Analysis")
    output_lines.append(f"\nTotal unique forms: {len(ed_forms)}")
    output_lines.append(f"Total text occurrences: {len(concordance)}")
    
    output_lines.append("\n## Morphology")
    output_lines.append("### Prefixes")
    for p, c in morph_stats["prefix_counts"].most_common(10):
        output_lines.append(f"- `{p}`: {c}")
    # Check specifically for 'o'
    if 'o' in morph_stats["prefix_counts"]:
        output_lines.append(f"- `o`: {morph_stats['prefix_counts']['o']} (Specific check)")
        
    output_lines.append("\n### Suffixes")
    for s, c in morph_stats["suffix_counts"].most_common(10):
        output_lines.append(f"- `{s}`: {c}")
    # Check specifically for 'dy'
    if 'dy' in morph_stats["suffix_counts"]:
        output_lines.append(f"- `dy`: {morph_stats['suffix_counts']['dy']} (Specific check)")
        
    output_lines.append("\n## Collocation Analysis")
    output_lines.append("### Top Preceding Words (Left Context)")
    for w, c in left_col.most_common(20):
        output_lines.append(f"- `{w}`: {c}")
        
    output_lines.append("\n### Top Following Words (Right Context)")
    for w, c in right_col.most_common(20):
        output_lines.append(f"- `{w}`: {c}")

    output_lines.append("\n## Section Distribution")
    for sec, c in section_dist.most_common():
        output_lines.append(f"- {sec}: {c}")
        
    output_lines.append("\n## Semantic Associations (Hypothesis Test)")
    output_lines.append("Co-occurrence with proxy words:")
    for cat, c in sorted(semantic_assocs.items(), key=lambda x: -x[1]):
        output_lines.append(f"- {cat}: {c}")
        
    output_lines.append("\n## Sample Concordance")
    for item in concordance[:20]:
        output_lines.append(f"- **{item['folio']} {item['loc']}**: ... {' '.join(item['left_context'])} **{item['word']}** {' '.join(item['right_context'])} ...")

    # Write detailed report
    with open("results/root_ed_analysis.md", "w") as f:
        f.write("\n".join(output_lines))
        
    # Write summary
    summary = []
    summary.append("# Task 172 Results Summary")
    summary.append("\n## Key Findings")
    summary.append(f"- `ed` root appears {len(concordance)} times.")
    
    top_prefix = morph_stats["prefix_counts"].most_common(1)[0] if morph_stats["prefix_counts"] else ("none", 0)
    summary.append(f"- Most common prefix: `{top_prefix[0]}` ({top_prefix[1]} times).")
    
    top_section = section_dist.most_common(1)[0] if section_dist else ("none", 0)
    summary.append(f"- Most frequent in section: {top_section[0]} ({top_section[1]} occurrences).")
    
    with open("results/track-172-results_summary.md", "w") as f:
        f.write("\n".join(summary))

    print("Done. Results written to results/root_ed_analysis.md and results/track-172-results_summary.md")

if __name__ == "__main__":
    main()
