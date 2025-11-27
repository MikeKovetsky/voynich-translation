import re
import json
from collections import Counter, defaultdict

EVA_FILE = "data/eva_ivtff.txt"
DICT_FILE = "results/master_dictionary_v7_1.json"
OUTPUT_REPORT = "results/grammar_sh_t_report.md"

def load_lines():
    with open(EVA_FILE, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            # Parse <f1r.1,@P0;H> text...
            m = re.match(r'<([^>]+);(\w)>\s*(.+)', line)
            if m:
                loc_full, transcriber, text = m.groups()
                if transcriber != 'H': continue # Use Takahashi
                
                # Parse location and tags
                if ',' in loc_full:
                    loc_parts = loc_full.split(',')
                    base_loc = loc_parts[0]
                else:
                    base_loc = loc_full
                
                folio = base_loc.split('.')[0]
                yield folio, text

def get_section(folio):
    # Parse folio number
    match = re.match(r'f(\d+)', folio)
    if not match: return None
    num = int(match.group(1))
    
    # Recipes: Quire 20 (f103-f116)
    if 103 <= num <= 116:
        return "Recipes"
    
    # Narrative: Herbal (f1-f57) + Bio (f75-f84)
    if 1 <= num <= 57:
        return "Narrative (Herbal)"
    if 75 <= num <= 84:
        return "Narrative (Bio)"
        
    return "Other"

def clean_text(text):
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'[^\w\s\.]', '', text)
    return text

def main():
    print("Starting Grammar sh-/t- Analysis...")
    
    # Load Dictionary
    try:
        with open(DICT_FILE, 'r') as f:
            master_dict = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {DICT_FILE} not found.")
        master_dict = {}

    # Data structures
    sh_counts = Counter()
    t_counts = Counter()
    all_word_counts = Counter()
    
    # Comparison counts
    base_comparison = defaultdict(lambda: {'base': 0, 'sh': 0, 't': 0})
    
    # Section comparison
    section_counts = defaultdict(lambda: {'total': 0, 'sh': 0, 't': 0})
    
    # Specific words context
    shdain_context = []
    tchol_context = []
    
    lines_processed = 0
    
    for folio, text in load_lines():
        section = get_section(folio)
        if section == "Other": continue # Focus on Recipe vs Narrative
        
        clean = clean_text(text)
        words = clean.replace('.', ' ').split()
        
        lines_processed += 1
        
        for i, word in enumerate(words):
            all_word_counts[word] += 1
            section_counts[section]['total'] += 1
            
            # Specific Context Capture
            if word == 'shdain':
                context = words[max(0, i-3):min(len(words), i+4)]
                shdain_context.append((folio, " ".join(context)))
            if word == 'tchol':
                context = words[max(0, i-3):min(len(words), i+4)]
                tchol_context.append((folio, " ".join(context)))

            # SH- Analysis
            if word.startswith('sh') and len(word) > 3:
                base = word[2:]
                if len(base) >= 2:
                    sh_counts[word] += 1
                    base_comparison[base]['sh'] += 1
                    section_counts[section]['sh'] += 1
                    
            # T- Analysis
            elif word.startswith('t') and len(word) > 2 and word[1] not in ['o', 'y', 'a', 'e']: 
                base = word[1:]
                if len(base) >= 2:
                    t_counts[word] += 1
                    base_comparison[base]['t'] += 1
                    section_counts[section]['t'] += 1

    # Second pass for base counts (populate base counts from all_word_counts)
    for base in base_comparison.keys():
        base_comparison[base]['base'] = all_word_counts[base]

    # Generate Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write("# Grammar Analysis: 'sh-' and 't-' Prefixes\n\n")
        f.write(f"Lines processed: {lines_processed}\n\n")
        
        # 1. Section Distribution
        f.write("## 1. Distribution by Section\n")
        f.write("| Section | Total Words | 'sh-' % | 't-' % |\n")
        f.write("|---|---|---|---|\n")
        for sec, counts in section_counts.items():
            total = counts['total']
            if total == 0: continue
            sh_pct = counts['sh'] / total * 100
            t_pct = counts['t'] / total * 100
            f.write(f"| {sec} | {total} | {sh_pct:.2f}% | {t_pct:.2f}% |\n")
            
        # 2. SH- Analysis
        f.write("\n## 2. 'sh-' Prefix (Relative Pronoun 'That/Which'?)\n")
        f.write("Comparison of `sh-word` vs `word`:\n\n")
        f.write("| Word (sh-) | Count | Base | Count | Ratio (sh/base) |\n")
        f.write("|---|---|---|---|---|\n")
        
        sorted_sh = sorted(base_comparison.items(), key=lambda x: x[1]['sh'], reverse=True)
        for base, counts in sorted_sh[:20]:
            if counts['sh'] < 2: continue
            sh_word = 'sh' + base
            ratio = counts['sh'] / counts['base'] if counts['base'] > 0 else float('inf')
            f.write(f"| {sh_word} | {counts['sh']} | {base} | {counts['base']} | {ratio:.2f} |\n")
            
        f.write("\n### Context: `shdain`\n")
        f.write(f"Total occurrences: {all_word_counts['shdain']}\n")
        if shdain_context:
            f.write("Occurrences:\n")
            for loc, ctx in shdain_context[:10]:
                f.write(f"- **{loc}**: ... {ctx} ...\n")
        else:
            f.write("No occurrences found in Recipe/Narrative sections.\n")

        f.write(f"\n### `shdain` vs `dain`\n")
        f.write(f"- `dain`: {all_word_counts['dain']}\n")
        f.write(f"- `shdain`: {all_word_counts['shdain']}\n")
            
        # 3. T- Analysis
        f.write("\n## 3. 't-' Prefix (Future/To)\n")
        f.write("Comparison of `t-word` vs `word`:\n\n")
        f.write("| Word (t-) | Count | Base | Count | Ratio (t/base) |\n")
        f.write("|---|---|---|---|---|\n")
        
        sorted_t = sorted(base_comparison.items(), key=lambda x: x[1]['t'], reverse=True)
        for base, counts in sorted_t[:20]:
            if counts['t'] < 2: continue
            t_word = 't' + base
            ratio = counts['t'] / counts['base'] if counts['base'] > 0 else float('inf')
            f.write(f"| {t_word} | {counts['t']} | {base} | {counts['base']} | {ratio:.2f} |\n")
            
        f.write("\n### Context: `tchol`\n")
        f.write(f"Total occurrences: {all_word_counts['tchol']}\n")
        f.write("Occurrences:\n")
        for loc, ctx in tchol_context[:10]:
            f.write(f"- **{loc}**: ... {ctx} ...\n")
            
        f.write(f"\n### `tchol` vs `chol`\n")
        f.write(f"- `chol`: {all_word_counts['chol']}\n")
        f.write(f"- `tchol`: {all_word_counts['tchol']}\n")

    print(f"Report written to {OUTPUT_REPORT}")

if __name__ == "__main__":
    main()
