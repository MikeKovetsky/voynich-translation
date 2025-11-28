import re
from collections import defaultdict, Counter
import os

# Configuration
INPUT_FILE = 'data/eva_ivtff.txt'
OUTPUT_FILE = 'results/suffix_position_report.md'

# Suffix list from morphology_report_v1.md (ordered by length/precedence)
SUFFIXES = [
    'aiin', 'edy', 'air', 'iin', 'eey', 'or', 'ey', 'al', 'in', 'hy', 
    'dy', 'ol', 'ar', 'l', 'n', 'r', 'y'
]

def load_data(filepath):
    sentences = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Filter for Takahashi transcription
            if ';H>' not in line:
                continue
            
            # Format is usually: <tag>    text
            # We split by > and take the last part
            parts = line.split('>')
            if len(parts) < 2:
                continue
            
            text_part = parts[-1].strip()
            
            # Tokenization: split by dots
            raw_words = text_part.split('.')
            
            clean_words = []
            for w in raw_words:
                # Remove unwanted characters (punctuation, etc.)
                # Keep only a-z
                w_clean = re.sub(r'[^a-z]', '', w)
                if w_clean:
                    clean_words.append(w_clean)
            
            if clean_words:
                sentences.append(clean_words)
    return sentences

def get_suffix(word):
    """Returns the longest matching suffix for the word, or None."""
    for suffix in SUFFIXES:
        if word.endswith(suffix):
            if len(word) > len(suffix): 
                return suffix
    return None

def analyze_positions(sentences):
    # Structure: suffix -> position -> count
    stats = defaultdict(Counter)
    suffix_counts = Counter()
    
    # Global stats for baseline
    global_stats = Counter()
    total_words = 0

    for sent in sentences:
        length = len(sent)
        for i, word in enumerate(sent):
            position = None
            if length == 1:
                position = 'Single'
            elif i == 0:
                position = 'Start'
            elif i == length - 1:
                position = 'End'
            else:
                position = 'Middle'
            
            global_stats[position] += 1
            total_words += 1
            
            suffix = get_suffix(word)
            if suffix:
                stats[suffix][position] += 1
                suffix_counts[suffix] += 1
            
    return stats, suffix_counts, global_stats, total_words

def generate_report(stats, suffix_counts, global_stats, total_words):
    lines = []
    lines.append("# Suffix-Position Correlation Report")
    lines.append("")
    lines.append("**Input Data:** `data/eva_ivtff.txt` (Takahashi `;H>` transcription)")
    lines.append(f"**Suffixes Analyzed:** {', '.join(SUFFIXES)}")
    lines.append("")
    
    # Calculate Baseline Probabilities
    base_start = (global_stats['Start'] / total_words) * 100
    base_middle = (global_stats['Middle'] / total_words) * 100
    base_end = (global_stats['End'] / total_words) * 100
    base_single = (global_stats['Single'] / total_words) * 100
    
    lines.append("## Baseline Statistics (All Words)")
    lines.append(f"- **Start**: {base_start:.1f}%")
    lines.append(f"- **Middle**: {base_middle:.1f}%")
    lines.append(f"- **End**: {base_end:.1f}%")
    lines.append(f"- **Single**: {base_single:.1f}%")
    lines.append("")

    lines.append("## Statistical Table: P(Position | Suffix)")
    lines.append("")
    lines.append("| Suffix | Count | Start % | Middle % | End % | Single % | Notable Deviation |")
    lines.append("|---|---|---|---|---|---|---|")
    
    sorted_suffixes = sorted(suffix_counts.keys(), key=lambda s: suffix_counts[s], reverse=True)
    
    candidates = []

    for suff in sorted_suffixes:
        total = suffix_counts[suff]
        counts = stats[suff]
        
        p_start = (counts['Start'] / total) * 100
        p_middle = (counts['Middle'] / total) * 100
        p_end = (counts['End'] / total) * 100
        p_single = (counts['Single'] / total) * 100
        
        # Calculate Lift (observed / expected)
        lift_start = p_start / base_start if base_start > 0 else 0
        lift_middle = p_middle / base_middle if base_middle > 0 else 0
        lift_end = p_end / base_end if base_end > 0 else 0
        lift_single = p_single / base_single if base_single > 0 else 0
        
        deviation_note = ""
        # Check for significant lifts (> 1.5x or 2x)
        max_lift = max(lift_start, lift_middle, lift_end, lift_single)
        
        if lift_end > 1.5:
            deviation_note = f"**End +{lift_end:.1f}x**"
            candidates.append(f"- **-{suff}**: Strongly favors **End** ({p_end:.1f}% vs baseline {base_end:.1f}%). Lift: {lift_end:.1f}x.")
        elif lift_start > 1.5:
            deviation_note = f"**Start +{lift_start:.1f}x**"
            candidates.append(f"- **-{suff}**: Strongly favors **Start** ({p_start:.1f}% vs baseline {base_start:.1f}%). Lift: {lift_start:.1f}x.")
        elif lift_single > 2.0: # Single is rare, so higher threshold
             deviation_note = f"**Single +{lift_single:.1f}x**"
             candidates.append(f"- **-{suff}**: Often appears in **Single-word lines** ({p_single:.1f}% vs baseline {base_single:.1f}%).")
        
        lines.append(f"| -{suff} | {total} | {p_start:.1f}% | {p_middle:.1f}% | {p_end:.1f}% | {p_single:.1f}% | {deviation_note} |")

    lines.append("")
    lines.append("## Grammar Rule Candidates")
    lines.append("")
    if candidates:
        for c in candidates:
            lines.append(c)
    else:
        lines.append("No significant deviations found from baseline.")
        
    lines.append("")
    lines.append("## Analysis")
    lines.append("High 'Lift' (deviation from baseline) suggests grammatical function.")
    lines.append("- Suffixes with high **End** lift might be sentence terminators or specific grammatical cases (e.g., verbs at end?).")
    lines.append("- Suffixes with high **Start** lift might be sentence initiators.")
    
    return "\n".join(lines)

def main():
    print("Loading data...")
    sentences = load_data(INPUT_FILE)
    print(f"Loaded {len(sentences)} sentences/lines.")
    
    print("Analyzing suffix positions...")
    stats, suffix_counts, global_stats, total_words = analyze_positions(sentences)
    
    print("Generating report...")
    report_content = generate_report(stats, suffix_counts, global_stats, total_words)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
