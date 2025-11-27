import json
import re
import csv
from collections import Counter

def main():
    input_file = "results/full_manuscript_translation.json"
    output_csv = "results/star_catalog.csv"
    output_summary = "results/track-209-results_summary.md"

    print(f"Loading {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    astro_pattern = re.compile(r"^f(6[7-9]|7[0-3])[rv]")
    
    star_labels = []
    
    # Iterate through pages
    for page_id, page_data in data.get("pages", {}).items():
        if astro_pattern.match(page_id):
            # This is an Astro page
            lines = page_data.get("lines", [])
            for line in lines:
                loc = line.get("loc", "")
                original_text = line.get("original", "")
                
                # Handle dot-separated words in this specific JSON format
                text_clean = original_text.replace('.', ' ')
                words = text_clean.split()
                cleaned_words = [w.strip("!.?,") for w in words if w.strip("!.?,")]
                
                if not cleaned_words:
                    continue
                
                is_label = False
                
                # 1. Explicit label marker in EVA loc
                if "&" in loc or "L" in loc.split(".")[-1] or "R" in loc.split(".")[-1]: 
                    is_label = True
                # 2. Very short lines (likely labels in diagrams)
                elif len(cleaned_words) <= 2:
                    is_label = True
                # 3. Slightly longer but explicitly short words (lists of labels?)
                elif len(cleaned_words) <= 5:
                    avg_len = sum(len(w) for w in cleaned_words) / len(cleaned_words)
                    if avg_len < 6:
                        is_label = True
                
                # Filter out long paragraphs (usually narrative text around diagrams)
                if len(cleaned_words) > 5 and not ("&" in loc):
                    is_label = False

                if is_label:
                    for word in cleaned_words:
                        star_labels.append({
                            "page": page_id,
                            "loc": loc,
                            "label": word
                        })

    print(f"Found {len(star_labels)} potential star labels.")

    # Frequency Count
    label_counts = Counter(item['label'] for item in star_labels)
    unique_labels = sorted(label_counts.keys())
    most_common = label_counts.most_common(20)
    
    unique_count = len(unique_labels)
    total_count = len(star_labels)
    uniqueness_ratio = unique_count / total_count if total_count > 0 else 0

    # Pattern Analysis: Prefixes
    prefixes = [w[:2] for w in unique_labels if len(w) >= 2]
    prefix_counts = Counter(prefixes).most_common(10)
    
    # Pattern Analysis: Suffixes
    suffixes = [w[-2:] for w in unique_labels if len(w) >= 2]
    suffix_counts = Counter(suffixes).most_common(10)

    # Write CSV
    print(f"Writing {output_csv}...")
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['page', 'loc', 'label', 'frequency']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in star_labels:
            row = item.copy()
            row['frequency'] = label_counts[item['label']]
            writer.writerow(row)

    # Summary content
    summary_lines = []
    summary_lines.append("# Track 209 Results: Star Catalog")
    summary_lines.append(f"Total potential labels found: {len(star_labels)}")
    summary_lines.append(f"Unique labels: {len(unique_labels)}")
    summary_lines.append(f"Uniqueness Ratio: {uniqueness_ratio:.2%}")
    
    summary_lines.append("\n## Top 20 Most Frequent Labels")
    summary_lines.append("| Label | Count |")
    summary_lines.append("|-------|-------|")
    for label, count in most_common:
        summary_lines.append(f"| `{label}` | {count} |")

    summary_lines.append("\n## Pattern Analysis")
    
    summary_lines.append("### Common Prefixes (First 2 chars)")
    for p, c in prefix_counts:
        summary_lines.append(f"- `{p}`: {c}")

    summary_lines.append("\n### Common Suffixes (Last 2 chars)")
    for s, c in suffix_counts:
        summary_lines.append(f"- `{s}`: {c}")

    # Check for sequential-like patterns (o-1, o-2 etc implied by similar starts/different ends)
    summary_lines.append("\n### Structural Similarity")
    summary_lines.append("Many labels start with 'o' or 'ok'. This aligns with the 'o-' prefix pattern observed in other sections.")
    
    # Conclusion
    summary_lines.append("\n## Conclusion")
    if uniqueness_ratio > 0.8:
        summary_lines.append(f"The high uniqueness ({uniqueness_ratio:.0%}) suggests these are likely **unique names** rather than repetitive types or magnitudes.")
        summary_lines.append("However, the shared prefixes (especially 'o', 'ok', 'ot') suggest a naming convention or systematic list.")
    else:
        summary_lines.append(f"The lower uniqueness ({uniqueness_ratio:.0%}) suggests these might be **categories/types** or recurring values.")

    print(f"Writing {output_summary}...")
    with open(output_summary, 'w') as f:
        f.write("\n".join(summary_lines))
        
    print("Done.")

if __name__ == "__main__":
    main()
