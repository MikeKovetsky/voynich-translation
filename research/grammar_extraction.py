import csv
import os
from collections import Counter, defaultdict
from research.voynich_data import get_eva_pages

INPUT_SCOPE = "results/scope_analysis.csv"
OUTPUT_FILE = "results/grammar_rules.md"

def main():
    if not os.path.exists(INPUT_SCOPE):
        print(f"Error: {INPUT_SCOPE} not found.")
        return

    # 1. Identify Global Keywords
    keywords = set()
    with open(INPUT_SCOPE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'Global Keyword' in row['classification']:
                keywords.add(row['word'])
                
    print(f"Analyzing grammar for {len(keywords)} keywords...")
    
    # 2. Scan Positions
    pages = get_eva_pages()
    
    # Stats: word -> {start: count, end: count, middle: count, total: count}
    stats = defaultdict(lambda: {'start': 0, 'end': 0, 'middle': 0, 'total': 0})
    followers = defaultdict(Counter) # word -> Counter(next_word)
    
    for folio, lines in pages.items():
        # Treat each LINE as a unit? Or Sentence?
        # Voynich syntax often wraps lines. Let's treat paragraphs (folio text) as units?
        # Or split by '.'?
        # Let's split by '.' if present, else line breaks.
        # Actually, many lines start with gallows. Line-initial is significant.
        
        for line in lines.values():
            # Clean punctuation
            clean_line = line.replace('.', ' ').replace(',', ' ')
            words = clean_line.split()
            if not words: continue
            
            for i, w in enumerate(words):
                if w not in keywords: continue
                
                stats[w]['total'] += 1
                
                if i == 0:
                    stats[w]['start'] += 1
                elif i == len(words) - 1:
                    stats[w]['end'] += 1
                else:
                    stats[w]['middle'] += 1
                    # Track follower
                    followers[w][words[i+1]] += 1

    # 3. Generate Rules
    rules = []
    
    for w, s in stats.items():
        if s['total'] < 20: continue
        
        start_pct = s['start'] / s['total'] * 100
        end_pct = s['end'] / s['total'] * 100
        
        role = "Connector"
        if start_pct > 40: role = "Prefix/Starter"
        if end_pct > 40: role = "Suffix/Terminator"
        
        # Analyze Followers
        top_followers = followers[w].most_common(3)
        follower_str = ", ".join([f"{k}({v})" for k, v in top_followers])
        
        rules.append({
            'word': w,
            'role': role,
            'start_pct': start_pct,
            'end_pct': end_pct,
            'follows': follower_str
        })
        
    # Sort by role then freq
    rules.sort(key=lambda x: (x['role'], -x['start_pct']))
    
    # Output Report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Grammar Rules (Global Keywords)\n\n")
        f.write("| Word | Role | Start % | End % | Top Followers |\n")
        f.write("|---|---|---|---|---|\n")
        for r in rules:
            f.write(f"| **{r['word']}** | {r['role']} | {r['start_pct']:.1f}% | {r['end_pct']:.1f}% | {r['follows']} |\n")
            
    print(f"Generated grammar rules for {len(rules)} words.")

if __name__ == "__main__":
    main()
