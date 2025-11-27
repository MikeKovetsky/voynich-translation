import re
import json
import os
from collections import Counter, defaultdict

def load_ingredients(path):
    with open(path, 'r') as f:
        data = json.load(f)
    # Extract ingredient words
    ingredients = set()
    for item in data.get('top_ingredients', []):
        ingredients.add(item['word'])
    return ingredients

def parse_tagged_text(path, start_page=103, end_page=116):
    # Pattern to match line ID: ROOT:f(Page)(Side)(Line)P(Panel)(Source)
    # Example: ROOT:f103r1P0F
    line_pattern = re.compile(r"ROOT:f(\d+)([rv])(\d+)P\d+([A-Za-z])\s+(.*)")
    
    pages = defaultdict(dict) # page -> line_num -> source -> text
    
    with open(path, 'r') as f:
        for line in f:
            match = line_pattern.match(line)
            if match:
                page_num = int(match.group(1))
                side = match.group(2)
                line_num = int(match.group(3))
                source = match.group(4)
                content = match.group(5)
                
                if start_page <= page_num <= end_page:
                    page_id = f"f{page_num}{side}"
                    if page_id not in pages:
                        pages[page_id] = defaultdict(dict)
                    pages[page_id][line_num][source] = content

    # Select best source for each line
    # Preference: F > H > U > m > c
    preferences = ['F', 'H', 'U', 'm', 'c']
    
    ordered_lines = []
    
    # Sort pages
    sorted_page_ids = sorted(pages.keys(), key=lambda x: (int(re.search(r'\d+', x).group()), x[-1]))
    
    for page_id in sorted_page_ids:
        lines = pages[page_id]
        sorted_line_nums = sorted(lines.keys())
        for ln in sorted_line_nums:
            sources = lines[ln]
            selected_content = None
            for pref in preferences:
                if pref in sources:
                    selected_content = sources[pref]
                    break
            if not selected_content and sources:
                selected_content = list(sources.values())[0]
            
            if selected_content:
                ordered_lines.append(selected_content)
                
    return ordered_lines

def clean_word(tagged_word):
    # Remove TAG: prefix if present
    if ':' in tagged_word:
        return tagged_word.split(':', 1)[1]
    return tagged_word

def analyze_dosages(lines, ingredients):
    repeated_glyphs = Counter()
    dosage_candidates = Counter()
    dosage_ingredient_pairs = Counter()
    
    dal_followers = Counter()
    dair_followers = Counter()
    ol_predecessors = Counter()

    for line in lines:
        words = line.split()
        cleaned_words = [clean_word(w) for w in words]
        
        for i, word in enumerate(cleaned_words):
            # Repeated glyphs
            if re.fullmatch(r"(.)\1+", word):
                repeated_glyphs[word] += 1
            
            # Dosage slot (before ingredient)
            if i + 1 < len(cleaned_words):
                next_word = cleaned_words[i+1]
                if next_word in ingredients:
                    dosage_candidates[word] += 1
                    dosage_ingredient_pairs[(word, next_word)] += 1
            
            # Check dal/dair followers
            if word == 'dal' and i + 1 < len(cleaned_words):
                dal_followers[cleaned_words[i+1]] += 1
            if word == 'dair' and i + 1 < len(cleaned_words):
                dair_followers[cleaned_words[i+1]] += 1
                
            # Check ol predecessors
            if word == 'ol':
                if i > 0:
                    ol_predecessors[cleaned_words[i-1]] += 1

    return repeated_glyphs, dosage_candidates, dosage_ingredient_pairs, dal_followers, dair_followers, ol_predecessors

def main():
    tagged_text_path = 'results/tagged_text.txt'
    ingredients_path = 'results/recipe_ingredients_v2.json'
    
    if not os.path.exists(tagged_text_path):
        print(f"Error: {tagged_text_path} not found.")
        return
    if not os.path.exists(ingredients_path):
        print(f"Error: {ingredients_path} not found.")
        return

    print("Loading ingredients...")
    ingredients = load_ingredients(ingredients_path)
    print(f"Loaded {len(ingredients)} ingredients.")
    
    print("Parsing text...")
    lines = parse_tagged_text(tagged_text_path)
    print(f"Parsed {len(lines)} lines from Quire 20.")
    
    print("Analyzing...")
    repeated_glyphs, dosage_candidates, dosage_pairs, dal_followers, dair_followers, ol_predecessors = analyze_dosages(lines, ingredients)
    
    # Filter candidates
    min_count = 2
    top_dosages = {k: v for k, v in dosage_candidates.items() if v >= min_count}
    
    # Format output
    output_data = {
        "repeated_glyph_words": dict(repeated_glyphs.most_common(20)),
        "dosage_candidates": dict(sorted(top_dosages.items(), key=lambda x: x[1], reverse=True)),
        "top_pairs": [{"dosage": k[0], "ingredient": k[1], "count": v} for k, v in dosage_pairs.most_common(30)],
        "dal_followers": dict(dal_followers.most_common(10)),
        "dair_followers": dict(dair_followers.most_common(10)),
        "ol_predecessors": dict(ol_predecessors.most_common(10))
    }
    
    save_path = 'results/dosage_candidates.json'
    with open(save_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"Saved results to {save_path}")
    
    # Generate Summary
    summary_path = 'results/track-205-results_summary.md'
    with open(summary_path, 'w') as f:
        f.write("# Track 205: Dosage Detection Results\n\n")
        f.write("## Repeated Glyph Candidates (Potential Numbers)\n")
        for word, count in repeated_glyphs.most_common(10):
            f.write(f"- **{word}**: {count}\n")
        
        f.write("\n## Contextual Dosage Candidates (Preceding Ingredients)\n")
        f.write("Words appearing most frequently immediately before an ingredient:\n")
        for word, count in sorted(top_dosages.items(), key=lambda x: x[1], reverse=True)[:15]:
            f.write(f"- **{word}**: {count}\n")
            
        f.write("\n## Top Dosage-Ingredient Pairs\n")
        for item in output_data['top_pairs']:
            f.write(f"- `{item['dosage']} {item['ingredient']}`: {item['count']}\n")
            
        f.write("\n## 'Dal' Context (Potential Number 1/Aries)\n")
        f.write("Words appearing after `dal`:\n")
        for word, count in dal_followers.most_common(10):
            f.write(f"- `dal {word}`: {count}\n")

        f.write("\n## 'Dair' Context\n")
        f.write("Words appearing after `dair`:\n")
        for word, count in dair_followers.most_common(10):
            f.write(f"- `dair {word}`: {count}\n")
            
        f.write("\n## 'Ol' Predecessors (Pattern: [Amount] ol [Noun]?)\n")
        for word, count in ol_predecessors.most_common(10):
            f.write(f"- `{word} ol`: {count}\n")

if __name__ == "__main__":
    main()
