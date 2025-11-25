
import json
import voynich_data
from collections import Counter
import re
import sys

def analyze_cohen_sanity():
    print("\n--- TRACK 84: COHEN SANITY CHECK ---")
    
    # Get all text
    pages = voynich_data.get_eva_pages()
    all_lines = []
    for folio in pages.values():
        for line in folio.values():
            clean_line = re.sub(r'[^\w\s.-]', '', line).strip()
            if clean_line:
                all_lines.append(clean_line.split('.')) # Split by word separator

    # Target patterns (EVA)
    # qok (Claston 4oh) -> "cohen"?
    targets = ['qok', 'qoke', 'qokedy', 'qokey'] 
    
    total_words = 0
    target_counts = Counter()
    position_stats = {t: {'start': 0, 'middle': 0, 'end': 0} for t in targets}
    next_words = {t: Counter() for t in targets}
    
    for line_words in all_lines:
        words = [w for w in line_words if w]
        total_words += len(words)
        
        for i, w in enumerate(words):
            for t in targets:
                if w.startswith(t): # Match prefix
                    target_counts[t] += 1
                    
                    # Position
                    if i == 0:
                        position_stats[t]['start'] += 1
                    elif i == len(words) - 1:
                        position_stats[t]['end'] += 1
                    else:
                        position_stats[t]['middle'] += 1
                        
                    # Next word
                    if i < len(words) - 1:
                        next_words[t][words[i+1]] += 1

    print(f"Total words analyzed: {total_words}")
    for t in targets:
        count = target_counts[t]
        if count == 0: continue
        freq = (count / total_words) * 100
        print(f"\nPattern: {t}")
        print(f"Count: {count} ({freq:.2f}%)")
        print(f"Positions: Start={position_stats[t]['start']} ({position_stats[t]['start']/count*100:.1f}%), "
              f"End={position_stats[t]['end']} ({position_stats[t]['end']/count*100:.1f}%), "
              f"Middle={position_stats[t]['middle']} ({position_stats[t]['middle']/count*100:.1f}%)")
        print("Top 5 following words:")
        for word, c in next_words[t].most_common(5):
            print(f"  + {word}: {c}")

def analyze_plant_distribution():
    print("\n--- TRACK 85: PLANT DISTRIBUTION ---")
    
    # Load candidate words
    try:
        with open('results/plant_pair_validation.json', 'r') as f:
            data = json.load(f)
            # Extract words - assuming structure based on previous interactions
            # Adapting to unknown structure, looking for high confidence keys
            if isinstance(data, list):
                candidates = [item['word'] for item in data if item.get('confidence') == 'ultra_high']
            elif isinstance(data, dict):
                 # Try to find a list inside
                 if 'ultra_high_confidence' in data:
                     candidates = [x['word'] for x in data['ultra_high_confidence']]
                 else:
                     # Fallback: just take top keys if it's a dict of words
                     candidates = list(data.keys())[:54]
    except Exception as e:
        print(f"Error loading plant validation: {e}")
        candidates = ['ckhal', 'chodar', 'opol', 'pchey', 'okshy', 'chekar', 'alam', 'qokeod', 'soy', 'checkhey'] # Fallback from summary
    
    print(f"Analyzing {len(candidates)} candidates")
    
    # Define sections
    sections = {
        'Herbal': voynich_data.get_section_text('herbal_a'), # + herbal_b
        'Recipes': voynich_data.get_section_text('recipes'),
        'Astrology': voynich_data.get_section_text('astronomical'),
        'Biology': voynich_data.get_section_text('biological'),
        'Cosmology': voynich_data.get_section_text('pharmaceutical') # naming in voynich_data is weird, using pharma as proxy or check definitions
    }
    # Add herbal_b to herbal
    herbal_b = voynich_data.get_section_text('herbal_b')
    sections['Herbal'].update(herbal_b)

    # Count occurrences
    results = {}
    
    for word in candidates:
        results[word] = {s: 0 for s in sections}
        total = 0
        for sec_name, sec_data in sections.items():
            count = 0
            for folio in sec_data.values():
                for line in folio.values():
                    if word in line: # Simple check, better with tokenization
                        count += line.count(word)
            results[word][sec_name] = count
            total += count
        results[word]['total'] = total
        
        # Calculate specificity (Herbal + Recipes) / Total
        if total > 0:
            spec = (results[word]['Herbal'] + results[word]['Recipes']) / total
            results[word]['specificity'] = spec
        else:
            results[word]['specificity'] = 0

    # Sort by specificity
    sorted_words = sorted(results.items(), key=lambda x: x[1]['specificity'], reverse=True)
    
    print(f"\nTop 10 Most Specific Plant Words (Herbal+Recipe / Total):")
    for w, stats in sorted_words[:10]:
        print(f"{w}: {stats['specificity']:.2f} (H={stats['Herbal']}, R={stats['Recipes']}, A={stats['Astrology']}, B={stats['Biology']})")

    print(f"\nTop 10 LEAST Specific (Leaking words):")
    for w, stats in sorted_words[-10:]:
        print(f"{w}: {stats['specificity']:.2f} (H={stats['Herbal']}, R={stats['Recipes']}, A={stats['Astrology']}, B={stats['Biology']})")

def analyze_recipe_syntax():
    print("\n--- TRACK 86: RECIPE SYNTAX ---")
    
    recipes = voynich_data.get_section_text('recipes')
    starters = Counter()
    
    # Collect lines
    lines = []
    for folio in recipes.values():
        for loc, text in folio.items():
            # Clean
            text = re.sub(r'[^\w\s.-]', '', text).strip()
            words = [w for w in text.split('.') if w]
            if words:
                lines.append(words)
                starters[words[0]] += 1
                
    print("\nTop 10 Sentence Starters in Recipes:")
    for w, c in starters.most_common(10):
        print(f"{w}: {c}")
        
    # Check "ol" (the?) context
    ol_next = Counter()
    for line in lines:
        for i, w in enumerate(line):
            if w == 'ol' and i < len(line)-1:
                ol_next[line[i+1]] += 1
                
    print("\nTop words after 'ol' (potential nouns):")
    for w, c in ol_next.most_common(10):
        print(f"{w}: {c}")

if __name__ == "__main__":
    analyze_cohen_sanity()
    analyze_plant_distribution()
    analyze_recipe_syntax()

