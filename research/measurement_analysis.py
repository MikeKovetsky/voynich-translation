"""
Track 93: Measurement Analysis
Identify words that function as measurements (amounts, durations) in recipes.
"""

import json
import re
from collections import Counter, defaultdict
from voynich_data import get_eva_pages, get_section_text

INGREDIENTS = {'char', 'chol', 'chl', 'chor', 'ar'}
CONNECTORS = {'daiin', 'ol', 'qok', 'qokeey', 'qoky'}


def extract_words(text):
    """Clean and split text into words."""
    text_clean = re.sub(r'[!?<>@$\d\[\]]', '', text)
    return [w for w in re.split(r'[.\-=,\s]+', text_clean) if w and len(w) > 1]


def analyze_daiin_patterns(recipe_data):
    """Find words appearing between daiin and ingredients."""
    patterns = defaultdict(Counter)
    daiin_contexts = []
    
    for folio, lines in recipe_data.items():
        for loc, text in lines.items():
            words = extract_words(text)
            for i, word in enumerate(words):
                if word == 'daiin' and i + 1 < len(words):
                    next_word = words[i + 1]
                    # Pattern: daiin [X] ingredient
                    if i + 2 < len(words):
                        following = words[i + 2]
                        if following in INGREDIENTS or following.startswith(tuple(INGREDIENTS)):
                            patterns['daiin_X_ingredient'][next_word] += 1
                            daiin_contexts.append({
                                'folio': folio,
                                'loc': loc,
                                'pattern': f"daiin {next_word} {following}",
                                'candidate': next_word,
                                'context': ' '.join(words[max(0,i-2):min(len(words),i+5)])
                            })
                    # Pattern: daiin [ingredient] - check if next is ingredient
                    if next_word in INGREDIENTS or next_word.startswith(tuple(INGREDIENTS)):
                        patterns['daiin_ingredient'][next_word] += 1
                    else:
                        patterns['daiin_X'][next_word] += 1
                        
    return patterns, daiin_contexts


def analyze_line_endings(recipe_data):
    """Find words that frequently end recipe lines."""
    endings = Counter()
    ending_contexts = []
    
    for folio, lines in recipe_data.items():
        for loc, text in lines.items():
            words = extract_words(text)
            if words:
                last_word = words[-1]
                endings[last_word] += 1
                if len(words) >= 3:
                    ending_contexts.append({
                        'folio': folio,
                        'loc': loc,
                        'last_word': last_word,
                        'context': ' '.join(words[-5:])
                    })
    
    return endings, ending_contexts


def cluster_words(recipe_data):
    """Cluster words by syntactic slot (before/after ingredients/connectors)."""
    slots = {
        'before_ingredient': Counter(),
        'after_ingredient': Counter(),
        'before_daiin': Counter(),
        'after_daiin': Counter(),
        'line_initial': Counter(),
        'line_final': Counter()
    }
    
    for folio, lines in recipe_data.items():
        for loc, text in lines.items():
            words = extract_words(text)
            if not words:
                continue
            
            slots['line_initial'][words[0]] += 1
            slots['line_final'][words[-1]] += 1
            
            for i, word in enumerate(words):
                if word in INGREDIENTS or word.startswith(tuple(INGREDIENTS)):
                    if i > 0:
                        slots['before_ingredient'][words[i-1]] += 1
                    if i + 1 < len(words):
                        slots['after_ingredient'][words[i+1]] += 1
                
                if word == 'daiin':
                    if i > 0:
                        slots['before_daiin'][words[i-1]] += 1
                    if i + 1 < len(words):
                        slots['after_daiin'][words[i+1]] += 1
    
    return slots


def find_number_candidates(recipe_data):
    """Find words that might be numbers/amounts based on position."""
    candidates = defaultdict(lambda: {'count': 0, 'positions': [], 'contexts': []})
    
    for folio, lines in recipe_data.items():
        for loc, text in lines.items():
            words = extract_words(text)
            for i, word in enumerate(words):
                # After daiin, before ingredient
                if i > 0 and words[i-1] == 'daiin':
                    if i + 1 < len(words) and (words[i+1] in INGREDIENTS or 
                                               words[i+1].startswith(tuple(INGREDIENTS))):
                        candidates[word]['count'] += 1
                        candidates[word]['positions'].append('daiin_X_ingr')
                        candidates[word]['contexts'].append({
                            'folio': folio, 'loc': loc,
                            'context': ' '.join(words[max(0,i-2):min(len(words),i+4)])
                        })
                
                # After qok-, before ingredient
                if word.startswith('qok') and i + 1 < len(words):
                    next_w = words[i+1]
                    if i + 2 < len(words) and (words[i+2] in INGREDIENTS or
                                               words[i+2].startswith(tuple(INGREDIENTS))):
                        candidates[next_w]['count'] += 1
                        candidates[next_w]['positions'].append('qok_X_ingr')
                        candidates[next_w]['contexts'].append({
                            'folio': folio, 'loc': loc,
                            'context': ' '.join(words[max(0,i-1):min(len(words),i+5)])
                        })
    
    return dict(candidates)


def find_repeated_patterns(recipe_data):
    """Find repeated 2-3 word sequences (likely fixed phrases)."""
    bigrams = Counter()
    trigrams = Counter()
    
    for folio, lines in recipe_data.items():
        for loc, text in lines.items():
            words = extract_words(text)
            for i in range(len(words) - 1):
                bigrams[' '.join(words[i:i+2])] += 1
            for i in range(len(words) - 2):
                trigrams[' '.join(words[i:i+3])] += 1
    
    return bigrams, trigrams


def main():
    print("Track 93: Measurement Analysis")
    print("=" * 50)
    
    # Load recipe section
    recipe_data = get_section_text('recipes', 'EVA', 'H')
    print(f"Loaded {len(recipe_data)} recipe folios")
    
    total_words = sum(len(extract_words(text)) 
                     for lines in recipe_data.values() 
                     for text in lines.values())
    print(f"Total words in recipes: {total_words}")
    
    # Task 1: daiin collocations
    print("\n" + "=" * 50)
    print("TASK 1: daiin Collocations")
    print("=" * 50)
    
    daiin_patterns, daiin_contexts = analyze_daiin_patterns(recipe_data)
    
    print("\nWords after 'daiin' (daiin [X]):")
    for word, count in daiin_patterns['daiin_X'].most_common(20):
        print(f"  {word}: {count}")
    
    print("\nWords in 'daiin [X] ingredient' pattern:")
    for word, count in daiin_patterns['daiin_X_ingredient'].most_common(15):
        print(f"  {word}: {count}")
    
    # Task 2: Line endings
    print("\n" + "=" * 50)
    print("TASK 2: Line Endings (action candidates)")
    print("=" * 50)
    
    endings, ending_contexts = analyze_line_endings(recipe_data)
    
    print("\nMost common line endings:")
    for word, count in endings.most_common(25):
        print(f"  {word}: {count}")
    
    # Task 3: Clustering
    print("\n" + "=" * 50)
    print("TASK 3: Word Clusters by Syntactic Position")
    print("=" * 50)
    
    slots = cluster_words(recipe_data)
    
    for slot_name, counter in slots.items():
        print(f"\n{slot_name.upper()}:")
        for word, count in counter.most_common(15):
            print(f"  {word}: {count}")
    
    # Number candidates
    print("\n" + "=" * 50)
    print("NUMBER/AMOUNT CANDIDATES")
    print("=" * 50)
    
    num_candidates = find_number_candidates(recipe_data)
    sorted_candidates = sorted(num_candidates.items(), 
                               key=lambda x: x[1]['count'], reverse=True)
    
    print("\nWords in measurement slots:")
    for word, data in sorted_candidates[:20]:
        if data['count'] > 0:
            positions = list(set(data['positions']))
            print(f"  {word}: {data['count']} ({', '.join(positions)})")
    
    # Repeated patterns
    print("\n" + "=" * 50)
    print("REPEATED PHRASES (potential fixed formulas)")
    print("=" * 50)
    
    bigrams, trigrams = find_repeated_patterns(recipe_data)
    
    print("\nTop bigrams:")
    for phrase, count in bigrams.most_common(20):
        print(f"  '{phrase}': {count}")
    
    print("\nTop trigrams:")
    for phrase, count in trigrams.most_common(15):
        print(f"  '{phrase}': {count}")
    
    # Identify measurement candidates
    measurement_candidates = identify_measurements(slots, daiin_patterns, endings)
    
    # Save results
    results = {
        'daiin_patterns': {k: dict(v.most_common(30)) for k, v in daiin_patterns.items()},
        'line_endings': dict(endings.most_common(50)),
        'word_slots': {k: dict(v.most_common(30)) for k, v in slots.items()},
        'number_candidates': {k: {'count': v['count'], 
                                   'positions': list(set(v['positions'])),
                                   'example_contexts': v['contexts'][:3]} 
                              for k, v in sorted_candidates[:30]},
        'bigrams': dict(bigrams.most_common(50)),
        'trigrams': dict(trigrams.most_common(30)),
        'measurement_candidates': measurement_candidates,
        'daiin_contexts_sample': daiin_contexts[:30]
    }
    
    with open('results/measurement_candidates.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    generate_report(results, recipe_data)
    
    print("\n✅ Results saved to results/measurement_candidates.json")
    print("✅ Report saved to results/measurement_report.md")


def identify_measurements(slots, daiin_patterns, endings):
    """Identify measurement words from combined evidence."""
    candidates = {}
    
    # Words that appear before ingredients but NOT as endings
    before_ingr = set(slots['before_ingredient'].keys())
    line_final = set(endings.keys())
    
    # Potential amounts: high before_ingredient, low line_final
    for word in before_ingr:
        before_count = slots['before_ingredient'][word]
        final_count = endings.get(word, 0)
        if before_count >= 3:
            ratio = before_count / max(final_count, 1)
            candidates[word] = {
                'before_ingredient': before_count,
                'line_final': final_count,
                'ratio': round(ratio, 2),
                'after_daiin': slots['after_daiin'].get(word, 0),
                'type': 'amount_candidate' if ratio > 2 else 'mixed'
            }
    
    # Words that only appear after daiin + before ingredient
    for word, count in daiin_patterns['daiin_X_ingredient'].most_common(20):
        if word not in candidates:
            candidates[word] = {
                'in_daiin_X_ingr': count,
                'type': 'strong_amount_candidate'
            }
        else:
            candidates[word]['in_daiin_X_ingr'] = count
            if count >= 2:
                candidates[word]['type'] = 'strong_amount_candidate'
    
    # Action candidates: high line_final count, specific suffixes
    action_suffixes = ['y', 'dy', 'chy', 'shy']
    for word, count in endings.most_common(50):
        if count >= 5:
            has_action_suffix = any(word.endswith(s) for s in action_suffixes)
            if word not in candidates:
                candidates[word] = {'line_final': count}
            candidates[word]['possible_action'] = has_action_suffix or count >= 10
    
    return candidates


def generate_report(results, recipe_data):
    """Generate markdown report."""
    report = """# Track 93: Measurement Analysis Report

## Summary

This analysis identifies words that likely function as measurements (amounts, durations) 
based on their grammatical position within recipe text.

## Methodology

1. **daiin Collocations**: Analyzed words appearing between `daiin` and ingredients
2. **Line Endings**: Found words that frequently end recipe lines (action candidates)
3. **Syntactic Clustering**: Clustered words by position relative to ingredients/connectors

---

## Key Findings

### 1. "daiin [X] ingredient" Pattern

Words appearing between `daiin` and confirmed ingredients may be AMOUNTS:

| Word | Count | Interpretation |
|------|-------|----------------|
"""
    
    for word, count in list(results['daiin_patterns'].get('daiin_X_ingredient', {}).items())[:15]:
        report += f"| `{word}` | {count} | amount candidate |\n"
    
    report += """
### 2. Line Endings (Action Candidates)

Words that frequently end recipe lines may be VERBS/ACTIONS:

| Word | Count | Pattern |
|------|-------|---------|
"""
    
    for word, count in list(results['line_endings'].items())[:20]:
        suffix = "[-y]" if word.endswith('y') else ""
        report += f"| `{word}` | {count} | {suffix} |\n"
    
    report += """
### 3. Words BEFORE Ingredients

Words appearing immediately before ingredients (potential amounts/modifiers):

| Word | Count | Also Line-Final | Interpretation |
|------|-------|-----------------|----------------|
"""
    
    before_ingr = results['word_slots'].get('before_ingredient', {})
    line_final = results['line_endings']
    
    for word, count in list(before_ingr.items())[:15]:
        final = line_final.get(word, 0)
        interp = "AMOUNT" if final < count/2 else "mixed"
        report += f"| `{word}` | {count} | {final} | {interp} |\n"
    
    report += """
### 4. Repeated Phrases (Fixed Formulas)

Common word combinations that may be formulaic expressions:

| Phrase | Count | Notes |
|--------|-------|-------|
"""
    
    for phrase, count in list(results['bigrams'].items())[:15]:
        note = ""
        if 'daiin' in phrase:
            note = "contains daiin"
        elif any(ing in phrase for ing in INGREDIENTS):
            note = "contains ingredient"
        report += f"| `{phrase}` | {count} | {note} |\n"
    
    report += """
---

## Measurement Candidate Summary

### HIGH CONFIDENCE (Amount/Number)

Words consistently appearing in measurement slots:

"""
    
    strong_candidates = [
        (w, d) for w, d in results['measurement_candidates'].items()
        if d.get('type') == 'strong_amount_candidate' or 
           (d.get('ratio', 0) > 3 and d.get('before_ingredient', 0) >= 5)
    ]
    
    for word, data in strong_candidates[:10]:
        report += f"- **`{word}`**: {data}\n"
    
    report += """
### MEDIUM CONFIDENCE (Possible Actions/Verbs)

Line-final words with action-like patterns:

"""
    
    action_candidates = [
        (w, d) for w, d in results['measurement_candidates'].items()
        if d.get('possible_action') and d.get('line_final', 0) >= 8
    ]
    
    for word, data in action_candidates[:10]:
        report += f"- **`{word}`**: {data.get('line_final', 0)} occurrences\n"
    
    report += """
---

## Sample Contexts

### "daiin [X] ingredient" examples:

"""
    
    for ctx in results['daiin_contexts_sample'][:10]:
        report += f"- **{ctx['folio']}**: `{ctx['context']}`\n"
    
    report += """
---

## Conclusions

1. **Potential Amount Words**: Words appearing between `daiin` and ingredients are 
   strong candidates for numbers or quantities.

2. **Action Words**: Line-final words, especially those with `-y` suffix, may be 
   verbs like "mix", "boil", "apply".

3. **Grammar Pattern**: Recipe structure appears to be:
   - `daiin [AMOUNT] [INGREDIENT]` - "Take [X] [herb]"
   - `[INSTRUCTION] [ACTION-y]` - "[do something] [verb]"

4. **Next Steps**:
   - Cross-reference amount candidates with zodiac/calendar pages for number validation
   - Compare action candidates across recipe sections
   - Build semantic clusters for translation refinement

"""
    
    with open('results/measurement_report.md', 'w') as f:
        f.write(report)


if __name__ == '__main__':
    main()



