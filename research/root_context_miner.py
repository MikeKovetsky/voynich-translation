import os
import re
import collections
from typing import List, Dict, Tuple

def load_eva_data(filepath):
    """Loads the EVA text data."""
    with open(filepath, 'r') as f:
        text = f.read()
    return text

def get_top_roots_from_report(report_path):
    """Parses the morphology report to get the Top 50 roots."""
    roots = []
    with open(report_path, 'r') as f:
        lines = f.readlines()
    
    # Find the table "Mutable Roots"
    in_table = False
    for line in lines:
        if "Mutable Roots" in line:
            in_table = True
            continue
        
        if in_table:
            if line.strip().startswith('|'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3 and parts[1] != "Root" and parts[1] != "---":
                    root = parts[1].replace('*', '')
                    if root:
                        roots.append(root)
                        if len(roots) >= 50:
                            break
    return roots

def clean_tokens(text_segment):
    """Cleans text segment and returns list of valid words."""
    # Remove tags like <...>
    text_segment = re.sub(r'<[^>]+>', '', text_segment)
    # Replace periods with spaces (EVA word separator)
    text_segment = text_segment.replace('.', ' ')
    
    words = text_segment.split()
    # Filter out empty or punctuation-only
    valid_words = []
    for w in words:
        w = w.strip(',').strip('!').strip('?')
        if w and not w.startswith('&') and not w.startswith('%'): 
            valid_words.append(w)
    return valid_words

def find_sentence_starters(lines, top_n=20):
    """Identifies sentence starters based on frequency and probability."""
    start_counts = collections.Counter()
    total_counts = collections.Counter()
    
    for line in lines:
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
            
        words = clean_tokens(parts[1])
        
        if not words:
            continue
            
        # First word is a starter
        starter = words[0]
        start_counts[starter] += 1
            
        for word in words:
            total_counts[word] += 1
                
    # Calculate probabilities
    candidates = []
    for word, s_count in start_counts.items():
        t_count = total_counts[word]
        if t_count < 10: 
            continue
        
        prob = s_count / t_count
        candidates.append({
            'word': word,
            'start_count': s_count,
            'total_count': t_count,
            'prob': prob
        })
    
    # Filter 1: Count > 50, Prob > 40%
    tier1 = [c for c in candidates if c['total_count'] > 50 and c['prob'] > 0.40]
    tier1.sort(key=lambda x: x['prob'], reverse=True)
    
    tier1_words = set(c['word'] for c in tier1)
    
    # Filter 2: Relaxed. Count > 20, Prob > 20%
    tier2 = [c for c in candidates if c['total_count'] > 20 and c['prob'] > 0.20 and c['word'] not in tier1_words]
    tier2.sort(key=lambda x: x['prob'], reverse=True)
    
    result = tier1 + tier2
    
    # If still not enough, fill with highest start_count from remaining
    if len(result) < top_n:
        existing_words = set(c['word'] for c in result)
        tier3 = [c for c in candidates if c['word'] not in existing_words]
        tier3.sort(key=lambda x: x['start_count'], reverse=True)
        result.extend(tier3[:top_n - len(result)])
        
    return [c['word'] for c in result[:top_n]]

def analyze_context(lines, roots):
    """Analyzes context for each root."""
    root_contexts = {root: {'pre': collections.Counter(), 'post': collections.Counter()} for root in roots}
    
    for line in lines:
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        
        words = clean_tokens(parts[1])
        
        for i, word in enumerate(words):
            current_matches = []
            for root in roots:
                # Check if word starts with root
                if word == root or word.startswith(root):
                    current_matches.append(root)
            
            for root in current_matches:
                # Record Preceding
                if i > 0:
                    root_contexts[root]['pre'][words[i-1]] += 1
                else:
                    root_contexts[root]['pre']['<START>'] += 1
                
                # Record Following
                if i < len(words) - 1:
                    root_contexts[root]['post'][words[i+1]] += 1
                else:
                    root_contexts[root]['post']['<END>'] += 1
                    
    return root_contexts

def main():
    # Paths
    data_path = 'data/eva_ivtff.txt'
    morph_report_path = 'results/morphology_report_v1.md'
    
    # Output Paths
    root_context_report_path = 'results/root_context_report.md'
    artifacts_roots_path = 'artifacts/top_roots.txt'
    artifacts_starters_path = 'artifacts/top_starters.txt'
    
    # 1. Load Data
    print("Loading data...")
    raw_text = load_eva_data(data_path)
    
    # Filter lines for Takahashi (H)
    lines = []
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ';H>' in line:
             lines.append(line)
    
    print(f"Loaded {len(lines)} lines (filtered for H).")
    
    # 2. Get Top Roots
    print("Getting top roots...")
    roots = get_top_roots_from_report(morph_report_path)
    print(f"Found {len(roots)} roots: {roots[:5]}...")
    
    # Save Top Roots Artifact
    with open(artifacts_roots_path, 'w') as f:
        for r in roots:
            f.write(f"{r}\n")
            
    # 3. Find Sentence Starters
    print("Finding sentence starters...")
    starters = find_sentence_starters(lines, top_n=20)
    print(f"Top starters: {starters}")
    
    # Save Starters Artifact
    with open(artifacts_starters_path, 'w') as f:
        for s in starters:
            f.write(f"{s}\n")
            
    # 4. Analyze Context
    print("Analyzing context...")
    contexts = analyze_context(lines, roots)
    
    # 5. Generate Report
    print("Generating report...")
    with open(root_context_report_path, 'w') as f:
        f.write("# Root Context Report\n\n")
        f.write("Analysis of the Top 50 Morphological Roots and their semantic context.\n\n")
        f.write(f"Total Lines Analyzed: {len(lines)} (Transcriber: H)\n\n")
        
        for root in roots:
            ctx = contexts[root]
            f.write(f"## Root: **{root}**\n\n")
            
            # Top 3 Preceding
            top_pre = ctx['pre'].most_common(3)
            f.write("- **Top Preceding:**\n")
            if not top_pre:
                 f.write("  - (None)\n")
            for word, count in top_pre:
                f.write(f"  - `{word}` ({count})\n")
                
            # Top 3 Following
            top_post = ctx['post'].most_common(3)
            f.write("- **Top Following:**\n")
            if not top_post:
                 f.write("  - (None)\n")
            for word, count in top_post:
                f.write(f"  - `{word}` ({count})\n")
            
            f.write("\n")
            
    print("Done.")

if __name__ == '__main__':
    main()
