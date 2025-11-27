import json
import re
import os

# Paths
SEGMENTED_TEXT_PATH = 'results/segmented_text.txt'
OUTPUT_REPORT = 'results/color_validation_report.md'
OUTPUT_SUMMARY = 'results/track-184-results_summary.md'

# Valid ranges for Herbal pages: f1r to f66v (approx)
HERBAL_PAGE_REGEX = re.compile(r'^f([1-9]|[1-5][0-9]|6[0-6])[rv]$')

def parse_segmented_text(path):
    pages = {}
    current_page = None
    current_text = []
    
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            # Page header: <f1r>
            # Note: The file has lines like <f1r> ...
            page_match = re.match(r'^<(f\d+[rv])>', line)
            if page_match:
                if current_page and current_text:
                    pages[current_page] = ' '.join(current_text)
                current_page = page_match.group(1)
                current_text = []
                continue
            
            # Text line with H transcriber: <f1r.P1;H> ...
            if current_page:
                if ';H>' in line:
                    parts = line.split(';H> ')
                    if len(parts) > 1:
                        text = parts[1].strip()
                        # Basic cleaning: remove comments {..}, weird chars
                        text = re.sub(r'\{.*?\}', '', text)
                        # Keep only letters, numbers, spaces, dots (sentence breaks)
                        # Voynich words often contain numbers or weird chars in EVA, but usually standard a-z.
                        # We'll keep basic structure.
                        current_text.append(text)
                        
    if current_page and current_text:
        pages[current_page] = ' '.join(current_text)
        
    return pages

def validate_colors(pages):
    # Target words
    LEAF_WORD = 'chol'
    ROOT_WORD = 'shor'
    
    WINDOW = 10 # Check within 10 words (approx sentence/phrase)
    
    herbal_pages = {k: v for k, v in pages.items() if HERBAL_PAGE_REGEX.match(k)}
    
    # Select 10 pages that contain at least one LEAF or ROOT word
    candidates = []
    for pid, text in herbal_pages.items():
        words = text.replace('.', ' ').split()
        if LEAF_WORD in words or ROOT_WORD in words:
            candidates.append(pid)
            
    # Pick first 10
    selected_pages = sorted(candidates)[:10]
    print(f"Selected pages: {selected_pages}")
    
    results = []
    total_matches = 0
    total_mismatches = 0
    
    for pid in selected_pages:
        text = herbal_pages[pid]
        # Split by . to handle sentences if possible, but simple word window is easier
        words = text.replace('.', ' ').split()
        
        page_score = 0
        details = []
        
        for i, word in enumerate(words):
            # Check Leaf
            if word == LEAF_WORD:
                start = max(0, i - WINDOW)
                end = min(len(words), i + WINDOW + 1)
                context = words[start:end]
                
                # Green: "or" or starts with "ok"
                found_green = any((w == 'or' or w.startswith('ok')) for w in context if w != word)
                # Red: starts with "ot"
                found_red = any(w.startswith('ot') for w in context if w != word)
                
                if found_green and not found_red:
                    page_score += 1
                    total_matches += 1
                    details.append(f"Leaf ({word}) + Green: MATCH (+1)")
                elif found_red and not found_green:
                    page_score -= 1
                    total_mismatches += 1
                    details.append(f"Leaf ({word}) + Red: MISMATCH (-1)")
                elif found_green and found_red:
                    details.append(f"Leaf ({word}) + Both: AMBIGUOUS (0)")
                else:
                    details.append(f"Leaf ({word}): No Color")

            # Check Root
            if word == ROOT_WORD:
                start = max(0, i - WINDOW)
                end = min(len(words), i + WINDOW + 1)
                context = words[start:end]
                
                # Red: starts with "ot"
                found_red = any(w.startswith('ot') for w in context if w != word)
                # Green: "or" or starts with "ok"
                found_green = any((w == 'or' or w.startswith('ok')) for w in context if w != word)
                
                if found_red and not found_green:
                    page_score += 1
                    total_matches += 1
                    details.append(f"Root ({word}) + Red: MATCH (+1)")
                elif found_green and not found_red:
                    page_score -= 1
                    total_mismatches += 1
                    details.append(f"Root ({word}) + Green: MISMATCH (-1)")
                elif found_green and found_red:
                    details.append(f"Root ({word}) + Both: AMBIGUOUS (0)")
                else:
                    details.append(f"Root ({word}): No Color")
                    
        results.append({
            'page': pid,
            'score': page_score,
            'details': details
        })
        
    return results, total_matches, total_mismatches

def main():
    print("Parsing segmented text...")
    pages = parse_segmented_text(SEGMENTED_TEXT_PATH)
    print(f"Parsed {len(pages)} pages.")
    
    print("Validating colors...")
    results, matches, mismatches = validate_colors(pages)
    
    # Generate Report
    report_lines = [
        "# Color Validation Report",
        "",
        f"**Total Matches:** {matches}",
        f"**Total Mismatches:** {mismatches}",
        "",
        "## Page Details",
        ""
    ]
    
    for r in results:
        report_lines.append(f"### Page {r['page']} (Score: {r['score']})")
        for d in r['details']:
            report_lines.append(f"- {d}")
        report_lines.append("")
        
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(report_lines))
    print(f"Report written to {OUTPUT_REPORT}")
    
    # Generate Summary
    summary_lines = [
        "# Task 184 Results Summary",
        "",
        "## Overview",
        "Validated the color words (`or`/`ok`=Green, `ot`=Red) against plant part words (`chol`=Leaf, `shor`=Root) on 10 herbal pages.",
        "",
        "## Findings",
        f"- **Matches:** {matches}",
        f"- **Mismatches:** {mismatches}",
        f"- **Ratio:** {matches}/{matches+mismatches} ({matches/(matches+mismatches)*100:.1f}%)" if (matches+mismatches) > 0 else "- **Ratio:** N/A",
        "",
        "## Conclusion",
        "The validation suggests..."
    ]
    
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write('\n'.join(summary_lines))
    print(f"Summary written to {OUTPUT_SUMMARY}")

if __name__ == '__main__':
    main()
