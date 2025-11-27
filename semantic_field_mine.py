import json
import glob
import re
import os
from collections import Counter, defaultdict

def load_master_dict():
    try:
        with open('results/master_dictionary_v7_4.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"entries": {}}

def load_page_descriptions():
    page_desc = {}
    for filepath in glob.glob('results/quire_*.json'):
        with open(filepath, 'r') as f:
            data = json.load(f)
            if 'folios' in data:
                for folio in data['folios']:
                    page_desc[folio['folio']] = folio.get('description', '').lower()
    return page_desc

def load_corpus():
    corpus = defaultdict(list)
    with open('data/eva_ivtff.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            match = re.match(r'<f(\d+[rv]\d?).*?>\s+(.*)', line)
            if match:
                page_id = f"f{match.group(1)}"
                text = match.group(2)
                # Remove inline tags like <...>
                text = re.sub(r'<[^>]+>', '', text)
                # Replace non-word chars with space
                text = re.sub(r'[^\w.]', ' ', text) 
                
                words = text.replace('-', '.').split('.')
                clean_words = [w.strip() for w in words if w.strip()]
                corpus[page_id].extend(clean_words)
    return corpus

def analyze_colors(corpus, page_desc):
    colors = {
        'blue': ['blue'],
        'red': ['red'],
        'white': ['white'],
        'green': ['green'] 
    }
    
    page_sets = {c: set() for c in colors}
    
    for page, desc in page_desc.items():
        for color, keywords in colors.items():
            if any(k in desc for k in keywords):
                page_sets[color].add(page)
    
    results = {}
    
    # Get unions of other colors to exclude shared words
    page_sets_union = set().union(*page_sets.values())
    
    for color, target_pages in page_sets.items():
        if not target_pages:
            continue
            
        # Control is ALL pages NOT in target (standard TF-IDF approach)
        # But for "Unique Blue", we want words that are high in Blue and LOW in Red/White.
        
        target_words = []
        for p in target_pages:
            target_words.extend(corpus[p])
            
        # Words in other colors
        other_color_pages = set()
        for c, p_set in page_sets.items():
            if c != color:
                other_color_pages.update(p_set)
        
        other_words = []
        for p in other_color_pages:
            other_words.extend(corpus[p])

        target_counts = Counter(target_words)
        other_counts = Counter(other_words)
        
        total_target = len(target_words) or 1
        total_other = len(other_words) or 1
        
        scores = []
        for word, count in target_counts.items():
            if count < 3: 
                continue
            
            # Check if it appears in other colors
            if word in other_counts:
                # Penalty if it appears in other colors
                other_freq = other_counts[word] / total_other
                target_freq = count / total_target
                ratio = target_freq / (other_freq + 1e-9)
                
                # We want High Ratio
                if ratio > 2.0: # At least 2x more frequent in this color
                    scores.append({
                        'word': word,
                        'score': ratio,
                        'count_target': count,
                        'count_other': other_counts[word]
                    })
            else:
                # Truly unique to this color (among color pages)
                scores.append({
                    'word': word,
                    'score': 999.0, # distinct marker
                    'count_target': count,
                    'count_other': 0
                })
            
        scores.sort(key=lambda x: (x['score'], x['count_target']), reverse=True)
        results[color] = scores[:20]
        
    return results

def analyze_recipes(corpus):
    recipe_pages = []
    for i in range(103, 117):
        recipe_pages.append(f"f{i}r")
        recipe_pages.append(f"f{i}v")
        
    recipe_words = []
    for p in recipe_pages:
        if p in corpus:
            recipe_words.extend(corpus[p])
            
    bigrams = []
    for i in range(len(recipe_words) - 1):
        bigrams.append((recipe_words[i], recipe_words[i+1]))
        
    bigram_counts = Counter(bigrams)
    
    # Look for what follows 'chol'
    chol_followers = []
    for i in range(len(recipe_words) - 1):
        if recipe_words[i] == 'chol':
            chol_followers.append(recipe_words[i+1])
            
    chol_follower_counts = Counter(chol_followers)
    
    return bigram_counts.most_common(50), chol_follower_counts.most_common(20)

def main():
    master_dict = load_master_dict()
    page_desc = load_page_descriptions()
    corpus = load_corpus()
    
    print("Analyzing Colors...")
    color_results = analyze_colors(corpus, page_desc)
    
    print("Analyzing Recipes...")
    recipe_bigrams, chol_followers = analyze_recipes(corpus)
    
    # Generate Report
    report = """# Semantic Field Analysis Report

## Task 1: Color Candidates (Unique or Dominant)

"""
    for color, candidates in color_results.items():
        report += f"### {color.capitalize()}\n"
        report += "| Word | Score (Ratio) | Count (Target) | Count (Other Colors) | Dictionary Meaning |\n"
        report += "|---|---|---|---|---|\n"
        for c in candidates:
            meaning = master_dict['entries'].get(c['word'], {}).get('meaning', '-')
            report += f"| `{c['word']}` | {c['score']:.2f} | {c['count_target']} | {c['count_other']} | {meaning} |\n"
        report += "\n"
        
    report += "## Task 2: Recipe Patterns (Texture/State)\n\n"
    report += "### Top Bigrams in Recipe Section (f103-f116):\n\n"
    report += "| Bigram | Count |\n"
    report += "|---|---|\n"
    for bg, count in recipe_bigrams:
        report += f"| `{bg[0]} {bg[1]}` | {count} |\n"

    report += "\n### Words following `chol` (Ingredient?):\n\n"
    report += "| Word | Count |\n"
    report += "|---|---|\n"
    for word, count in chol_followers:
         report += f"| `chol {word}` | {count} |\n"
        
    with open('results/semantic_field_report.md', 'w') as f:
        f.write(report)
    
    # Dump candidates to JSON
    with open('results/semantic_field_candidates.json', 'w') as f:
        json.dump({
            "colors": color_results,
            "recipes": {
                "bigrams": [{"word1": b[0][0], "word2": b[0][1], "count": b[1]} for b in recipe_bigrams],
                "chol_followers": [{"word": w[0], "count": w[1]} for w in chol_followers]
            }
        }, f, indent=2)

if __name__ == "__main__":
    main()
