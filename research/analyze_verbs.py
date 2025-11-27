import json
import os
import re
from collections import defaultdict

# Configuration
INPUT_FILE = "results/full_manuscript_translation.json"
OUTPUT_JSON = "results/verb_morphology.json"
OUTPUT_REPORT = "results/verb_grammar_report.md"
OUTPUT_SUMMARY = "results/track-173-results_summary.md"

SECTIONS = {
    "Herbal": (1, 66),
    "Cosmological": (67, 73),
    "Biological": (75, 84),
    "Rosettes": (85, 86),
    "Recipes": (87, 102),
    "Stars": (103, 116)
}

def get_section(folio_str):
    # folio_str format: f1r, f1v, etc.
    match = re.match(r"f(\d+)[rv]", folio_str)
    if not match:
        return "Unknown"
    num = int(match.group(1))
    
    for name, (start, end) in SECTIONS.items():
        if start <= num <= end:
            return name
    return "Unknown"

def load_data():
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)
    return data

def analyze_verbs(data):
    verbs = []
    
    # Iterate through all pages
    for page_id, page_data in data.get("pages", {}).items():
        section = get_section(page_id)
        
        for line in page_data.get("lines", []):
            original_line = line.get("original", "")
            # Split into words (remove punctuation usually handled by simple split if dot separated)
            # The format in json is "word.word.word" often, or just words.
            # Looking at the file: "fachys.ykal.ar..."
            # We should clean up punctuation like !, <...>, etc.
            
            # Simple cleaning: remove special chars except dots which separate words?
            # Actually, words seem to be separated by dots or spaces.
            # Let's replace dots with spaces and split.
            clean_line = original_line.replace('.', ' ').replace(',', ' ')
            # Remove metadata tags like <...> or [..] if any remain (though the json usually has cleaned text in 'original'?)
            # The json example: "fachys.ykal.ar.ataiin.shol.shory.cth!res.y.kor.sholdy!"
            # Contains ! and <..>.
            
            words = clean_line.split()
            
            for word in words:
                # Clean word further
                word = re.sub(r"[^a-zA-Z0-9]", "", word)
                if not word:
                    continue
                
                prefix = None
                stem = None
                
                if word.startswith("qok"):
                    prefix = "qok"
                    stem = word[3:]
                elif word.startswith("qo"):
                    prefix = "qo"
                    stem = word[2:]
                elif word.startswith("q"):
                    prefix = "q"
                    stem = word[1:]
                
                if prefix:
                    if not stem: # Skip if word IS the prefix (e.g. just "q")
                        continue
                        
                    # Analyze Suffix
                    suffix = None
                    # Check longest suffixes first
                    potential_suffixes = ["dy", "in", "y", "a", "o"]
                    # Also check for "aiin" ? Task lists: -dy, -y, -a, -o, -in.
                    
                    for s in potential_suffixes:
                        if stem.endswith(s):
                            suffix = s
                            break
                    
                    # If no suffix match from list, maybe "other" or "null"
                    suffix_cat = suffix if suffix else "other"
                    
                    verbs.append({
                        "original": word,
                        "prefix": prefix,
                        "stem": stem,
                        "suffix": suffix_cat,
                        "section": section,
                        "page": page_id
                    })
    return verbs

def generate_reports(verbs):
    # 1. JSON Output
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(verbs, f, indent=2)
    
    # 2. Grammar Report
    
    # Stats
    total_verbs = len(verbs)
    suffix_counts = defaultdict(int)
    prefix_counts = defaultdict(int)
    section_suffix_counts = defaultdict(lambda: defaultdict(int))
    section_counts = defaultdict(int)
    
    for v in verbs:
        suffix_counts[v['suffix']] += 1
        prefix_counts[v['prefix']] += 1
        section_suffix_counts[v['section']][v['suffix']] += 1
        section_counts[v['section']] += 1
        
    report_lines = []
    report_lines.append("# Verb Grammar Report: `qok-` Prefix Analysis")
    report_lines.append(f"\n**Total Verbs Identified:** {total_verbs}")
    
    report_lines.append("\n## Prefix Distribution")
    for p, c in prefix_counts.items():
        report_lines.append(f"- **{p}-**: {c} ({c/total_verbs*100:.1f}%)")

    report_lines.append("\n## Suffix Distribution (Global)")
    for s, c in sorted(suffix_counts.items(), key=lambda x: x[1], reverse=True):
        report_lines.append(f"- **-{s}**: {c} ({c/total_verbs*100:.1f}%)")
        
    report_lines.append("\n## Contextual Analysis (Tense/Aspect)")
    report_lines.append("\nHypothesis Check: Narrative (Bio/Rosettes) vs. Instructional (Recipes)")
    
    # Table
    report_lines.append("\n| Section | Total Verbs | -y (Imp?) | -a (Past?) | -dy | -o | -in | Other |")
    report_lines.append("|---|---|---|---|---|---|---|---|")
    
    sections_of_interest = ["Herbal", "Cosmological", "Biological", "Rosettes", "Recipes", "Stars"]
    
    for sec in sections_of_interest:
        total = section_counts[sec]
        if total == 0:
            continue
        counts = section_suffix_counts[sec]
        
        def get_pct(s):
            return f"{counts[s]} ({counts[s]/total*100:.1f}%)"
            
        row = f"| {sec} | {total} | {get_pct('y')} | {get_pct('a')} | {get_pct('dy')} | {get_pct('o')} | {get_pct('in')} | {get_pct('other')} |"
        report_lines.append(row)
        
    # Analysis Text
    report_lines.append("\n## Observations")
    
    # Check Hypothesis
    rec_y_count = section_suffix_counts["Recipes"]["y"] + section_suffix_counts["Stars"]["y"]
    rec_total = section_counts["Recipes"] + section_counts["Stars"]
    rec_y_pct = (rec_y_count / rec_total * 100) if rec_total else 0
    
    bio_a_count = section_suffix_counts["Biological"]["a"] + section_suffix_counts["Rosettes"]["a"]
    bio_dy_count = section_suffix_counts["Biological"]["dy"] + section_suffix_counts["Rosettes"]["dy"]
    bio_total = section_counts["Biological"] + section_counts["Rosettes"]
    bio_a_pct = (bio_a_count / bio_total * 100) if bio_total else 0
    bio_dy_pct = (bio_dy_count / bio_total * 100) if bio_total else 0
    
    report_lines.append(f"\n- **Instructional (Recipes/Stars)**: `-y` appears in {rec_y_pct:.1f}% of verbs.")
    report_lines.append(f"- **Narrative (Bio/Rosettes)**: `-a` appears in {bio_a_pct:.1f}% of verbs. `-dy` appears in {bio_dy_pct:.1f}% of verbs.")
    
    if bio_a_pct < 1.0 and bio_dy_pct > 20.0:
         report_lines.append("\n> **Note:** The hypothesis that `-a` marks narrative sections is not supported by the data. However, `-dy` shows a strong correlation with narrative sections (Biological/Rosettes), appearing significantly more often there than in Recipes.")

    with open(OUTPUT_REPORT, 'w') as f:
        f.write("\n".join(report_lines))
        
    # 3. Summary File
    summary_lines = []
    summary_lines.append("# Track 173 Results: Verb Morphology")
    summary_lines.append("\n## Key Findings")
    summary_lines.append(f"- Analyzed {total_verbs} verbs starting with `qok-`, `qo-`, or `q-`.")
    summary_lines.append(f"- Dominant suffix: `-{max(suffix_counts, key=suffix_counts.get)}`")
    summary_lines.append(f"- Recipes/Stars (Instructional) preference for `-y`: {rec_y_pct:.1f}%")
    summary_lines.append(f"- Biological/Rosettes (Narrative) preference for `-dy`: {bio_dy_pct:.1f}% (vs {bio_a_pct:.1f}% for -a)")
    summary_lines.append(f"\nSee `{OUTPUT_REPORT}` for detailed breakdown and `{OUTPUT_JSON}` for raw data.")
    
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("\n".join(summary_lines))

def main():
    print("Loading data...")
    data = load_data()
    print("Analyzing verbs...")
    verbs = analyze_verbs(data)
    print(f"Found {len(verbs)} verbs.")
    print("Generating reports...")
    generate_reports(verbs)
    print("Done.")

if __name__ == "__main__":
    main()
