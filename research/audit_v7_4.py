
import os
import glob
import math
import collections
import re

def calculate_entropy(text, order=1):
    """
    Calculates the conditional entropy of the text given 'order' previous characters.
    Order 0: H(X) (1st order entropy in some contexts, 0th order context)
    Order 1: H(X|Y) (2nd order entropy, 1st order context)
    
    Task says "2nd-order entropy". Usually means taking pairs.
    If order=1, we calculate H(Next|Current).
    """
    if len(text) <= order:
        return 0.0
    
    # 1. Calculate entropy of context (N-grams of size 'order')
    # 2. Calculate entropy of N+1-grams (size 'order' + 1)
    # H(Next|Context) = H(Context+Next) - H(Context)
    
    if order == 0:
        # Simple unigram entropy
        counts = collections.Counter(text)
        total = sum(counts.values())
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy
        
    # Context (size order)
    context_counts = collections.Counter()
    # Sequence (size order+1)
    seq_counts = collections.Counter()
    
    for i in range(len(text) - order):
        ctx = text[i:i+order]
        seq = text[i:i+order+1]
        context_counts[ctx] += 1
        seq_counts[seq] += 1
        
    # H(Context)
    h_context = 0.0
    total_ctx = sum(context_counts.values())
    for count in context_counts.values():
        p = count / total_ctx
        h_context -= p * math.log2(p)
        
    # H(Sequence)
    h_seq = 0.0
    total_seq = sum(seq_counts.values())
    for count in seq_counts.values():
        p = count / total_seq
        h_seq -= p * math.log2(p)
        
    return h_seq - h_context

def load_voynich_data(filepath):
    """
    Parses EVA IVTFF file.
    Returns a single string of Voynich text (cleaned).
    """
    text_parts = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            # Line format: <f1r.1,@P0;H>	text...
            # We prefer 'H' transcription, but will take others if H is missing?
            # Actually, let's stick to 'H' (Takahashi) if available, or 'C' (Currier).
            # Let's just take lines that have a transcription.
            # The part after the last '>' is the text.
            if '>' in line:
                parts = line.split('>')
                content = parts[-1].strip()
                
                # Check if it is a valid transcription line (usually has ;ID in the tag)
                # We filter for lines that look like text.
                # Avoid empty lines.
                if not content:
                    continue
                
                # Basic cleaning
                # Remove uncertainty markers like !, ?, ,
                # Remove line numbers or other artifacts if present
                content = content.replace('.', ' ') # Replace dots with spaces as they are word separators
                content = re.sub(r'[!?,]', '', content)
                content = re.sub(r'\s+', ' ', content)
                
                text_parts.append(content)
                
    return " ".join(text_parts)

def load_translation_data(directory):
    """
    Parses /translated/*.md files.
    Returns:
    1. full_text: All text content (cleaned of markdown).
    2. translated_words: List of words that are considered "translated" (e.g. **WORD**).
    3. token_list: List of all tokens in order (for repetition analysis).
    """
    full_text_parts = []
    translated_words = []
    token_list = []
    
    files = glob.glob(os.path.join(directory, "*.md"))
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                
                # Process line
                # Words are separated by spaces.
                # Translated words are like **WORD**
                
                words = line.strip().split()
                for w in words:
                    # Clean word for full text
                    clean_w = w.replace('*', '')
                    
                    # Add to full text
                    full_text_parts.append(clean_w)
                    
                    # Check if it is a translated word (starts/ends with **)
                    if w.startswith('**') and w.endswith('**'):
                        # Extract inner content
                        inner = w.strip('*')
                        # Sometimes it is **WORD (NOTE)**. 
                        # We just want the token for counting? 
                        # Task says "translated English words".
                        # Let's count the whole thing as a type for now.
                        translated_words.append(inner)
                        token_list.append(inner)
                    else:
                        token_list.append(clean_w)
                        
    return " ".join(full_text_parts), translated_words, token_list

def analyze_zipf(words):
    """
    Checks Zipf's law.
    Returns R-squared or some metric, and top 10 words.
    """
    counts = collections.Counter(words)
    sorted_counts = sorted(counts.values(), reverse=True)
    
    # Log-Log Plot data
    ranks = range(1, len(sorted_counts) + 1)
    
    # Calculate R-squared for log(freq) = a - b * log(rank)
    # x = log(rank), y = log(freq)
    if not sorted_counts:
        return 0.0, []
        
    xs = [math.log(r) for r in ranks]
    ys = [math.log(c) for c in sorted_counts]
    
    n = len(xs)
    if n < 2:
        return 0.0, counts.most_common(10)
        
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    
    numer = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(xs, ys))
    denom = sum((xi - mean_x)**2 for xi in xs)
    
    slope = numer / denom if denom != 0 else 0
    intercept = mean_y - slope * mean_x
    
    # Calculate R2
    ss_tot = sum((yi - mean_y)**2 for yi in ys)
    ss_res = sum((yi - (intercept + slope * xi))**2 for xi, yi in zip(xs, ys))
    
    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return r2, counts.most_common(10)

def analyze_repetition(tokens):
    """
    Calculates repetition rate: (w[i] == w[i+1]) / (N-1)
    """
    if len(tokens) < 2:
        return 0.0
    
    repeats = 0
    for i in range(len(tokens) - 1):
        if tokens[i] == tokens[i+1]:
            repeats += 1
            
    return repeats / (len(tokens) - 1)

def main():
    # Paths
    voynich_path = "data/eva_ivtff.txt"
    translated_dir = "translated"
    output_path = "results/audit_v7_4.md"
    
    # 1. Load Data
    print("Loading Voynich data...")
    voynich_text = load_voynich_data(voynich_path)
    voynich_tokens = voynich_text.split()
    
    print("Loading Translation data...")
    trans_text, trans_words, trans_tokens = load_translation_data(translated_dir)
    
    # 2. Entropy Analysis
    # We use character-based entropy for text as requested ("2.5 bits/char")
    # Voynich
    h2_voynich = calculate_entropy(voynich_text, order=1)
    # Translation
    h2_trans = calculate_entropy(trans_text, order=1)
    
    # 3. Zipf's Law
    r2_zipf, top_words = analyze_zipf(trans_words)
    
    # 4. Repetition Analysis
    rep_voynich = analyze_repetition(voynich_tokens)
    rep_trans = analyze_repetition(trans_tokens)
    
    # 5. Generate Report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Audit Report v7.4\n\n")
        
        f.write("## 1. Entropy Analysis (2nd-order)\n")
        f.write(f"- **Voynich Raw Text**: {h2_voynich:.4f} bits/char\n")
        f.write(f"- **English Translation**: {h2_trans:.4f} bits/char\n")
        f.write("\n**Conclusion:**\n")
        if abs(h2_voynich - h2_trans) < 1.0:
             f.write("PASS: Entropies are comparable.\n")
        else:
             f.write(f"FAIL: Significant difference ({abs(h2_voynich - h2_trans):.2f} bits).\n")
        
        f.write("\n## 2. Zipf's Law Check\n")
        f.write(f"- **R-squared (Log-Log)**: {r2_zipf:.4f}\n")
        f.write("- **Top 10 Translated Words**:\n")
        for w, c in top_words:
            f.write(f"  - {w}: {c}\n")
            
        f.write("\n**Conclusion:**\n")
        if r2_zipf > 0.9:
            f.write("PASS: Follows Power Law strongly.\n")
        elif r2_zipf > 0.8:
            f.write("WARN: Weak adherence to Power Law.\n")
        else:
            f.write("FAIL: Does not look like natural language distribution.\n")
            
        f.write("\n## 3. Repetition Analysis\n")
        f.write(f"- **Voynich Repetition Rate**: {rep_voynich:.4%}\n")
        f.write(f"- **Translation Repetition Rate**: {rep_trans:.4%}\n")
        
        f.write("\n**Conclusion:**\n")
        diff = abs(rep_voynich - rep_trans)
        if diff < 0.05: # 5% tolerance
            f.write("PASS: Repetition patterns preserved.\n")
        else:
            f.write(f"FAIL: Repetition rate changed significantly (Diff: {diff:.2%}).\n")

    print(f"Audit complete. Results written to {output_path}")

if __name__ == "__main__":
    main()

