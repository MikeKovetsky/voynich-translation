import re
import csv
from collections import Counter, defaultdict

TRANSCRIPTION_FILE = 'results/tagged_text.txt'
OUTPUT_CSV = 'results/recipe_starters.csv'
OUTPUT_SUMMARY = 'results/track-213-results_summary.md'

# Regex to match the line identifier and content
# Example: ROOT:f103r1P0H ROOT:pched ...
# Removed ^ anchor and added handling for potential whitespace
LINE_PATTERN = re.compile(r'ROOT:(f\d+[rv])(\d+)P0H\s+(.*)')

def get_clean_word(token):
    # Remove TAG: prefix (e.g., ROOT:, CONJ:, NOUN:)
    if ':' in token:
        return token.split(':', 1)[1]
    return token

def main():
    starters = []
    all_words = Counter()
    starter_positions = defaultdict(list) # word -> list of positions (0=start, >0=middle)
    
    paragraphs_found = 0
    lines_processed = 0
    matches_found = 0
    
    try:
        with open(TRANSCRIPTION_FILE, 'r') as f:
            for line in f:
                lines_processed += 1
                line = line.strip()
                match = LINE_PATTERN.search(line) # Use search instead of match
                if match:
                    matches_found += 1
                    page = match.group(1)
                    para_num = match.group(2)
                    content = match.group(3)
                    
                    # Check page range
                    # Parse page number
                    page_match = re.search(r'f(\d+)', page)
                    if page_match:
                        page_num = int(page_match.group(1))
                        
                        if 103 <= page_num <= 116:
                            paragraphs_found += 1
                            tokens = content.split()
                            clean_tokens = [get_clean_word(t) for t in tokens]
                            
                            if clean_tokens:
                                starter = clean_tokens[0]
                                starters.append(starter)
                                
                                for i, word in enumerate(clean_tokens):
                                    all_words[word] += 1
                                    starter_positions[word].append(i)
                                
    except FileNotFoundError:
        print(f"File not found: {TRANSCRIPTION_FILE}")
        return

    print(f"Processed {lines_processed} lines.")
    print(f"Found {matches_found} lines matching pattern.")
    print(f"Analyzed {paragraphs_found} paragraphs in range f103r-f116v.")
    
    # Count starters
    starter_counts = Counter(starters)
    
    # Analyze categories
    # Group them: saiin, daiin, ol-, qok-
    categories = defaultdict(int)
    
    categorized_starters = []
    
    for word, count in starter_counts.most_common():
        category = 'other'
        if word == 'saiin':
            category = 'saiin'
        elif word == 'daiin':
            category = 'daiin'
        elif word.startswith('ol'):
            category = 'ol-'
        elif word.startswith('qok'):
            category = 'qok-'
        else:
            pass
            
        categories[category] += count
        
        # Check if it appears in middle
        positions = starter_positions[word]
        total_occurrences = len(positions)
        starts = positions.count(0)
        middles = total_occurrences - starts
        
        is_exclusive_starter = (middles == 0)
        
        categorized_starters.append({
            'word': word,
            'count': count,
            'category': category,
            'total_occurrences': total_occurrences,
            'start_count': starts,
            'middle_count': middles,
            'exclusive_start': is_exclusive_starter
        })

    # Write CSV
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        fieldnames = ['word', 'count', 'category', 'total_occurrences', 'start_count', 'middle_count', 'exclusive_start']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in categorized_starters:
            writer.writerow(row)
            
    print(f"Wrote results to {OUTPUT_CSV}")
    
    # Write Summary
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("# Track 213: Bullet Analysis Results\n\n")
        f.write(f"**Total Paragraphs Analyzed:** {paragraphs_found}\n\n")
        
        f.write("## Top Starters\n\n")
        f.write("| Word | Count | Category | Exclusive Starter? |\n")
        f.write("|---|---|---|---|\n")
        for row in categorized_starters[:20]:
            f.write(f"| {row['word']} | {row['count']} | {row['category']} | {row['exclusive_start']} |\n")
            
        f.write("\n## Category Distribution\n\n")
        for cat in ['saiin', 'daiin', 'ol-', 'qok-', 'other']:
             count = categories.get(cat, 0)
             f.write(f"- **{cat}**: {count}\n")
            
        f.write("\n## Observations\n\n")
        f.write("Most frequent starters often serve as bullet points in the recipe section.\n")
        f.write("Exclusive starters are strong candidates for structural markers.\n")

    print(f"Wrote summary to {OUTPUT_SUMMARY}")

if __name__ == "__main__":
    main()
