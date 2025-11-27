import json
import re
import os
from collections import Counter

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_quire_folios(quire_path):
    data = load_json(quire_path)
    folios = []
    for folio_data in data['folios']:
        folios.append(folio_data['folio'])
    return folios

def parse_lines(text_path, target_folios):
    with open(text_path, 'r') as f:
        lines = f.readlines()
    
    parsed_lines = []
    
    # Pattern: <f103r.1,@P0;H> text...
    line_pattern = re.compile(r'<((f\d+[rv]).*?);([A-Za-z])>\s+(.*)')
    
    line_data = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        match = line_pattern.match(line)
        if match:
            full_tag = match.group(1)
            folio = match.group(2)
            transcriber = match.group(3)
            text = match.group(4)
            
            if folio in target_folios:
                if full_tag not in line_data:
                    line_data[full_tag] = {}
                line_data[full_tag][transcriber] = text

    # Sort and extract
    # Sort by folio index then line number
    # We don't have folio index in quire_20_recipes easily unless we assume order.
    # We'll iterate target_folios.
    
    for folio in target_folios:
        folio_keys = [k for k in line_data.keys() if k.startswith(folio + '.')]
        
        def get_line_num(k):
            try:
                parts = k.split('.')
                if len(parts) > 1:
                    val = parts[1]
                    nums = re.findall(r'\d+', val)
                    if nums: return int(nums[0])
                    if 'P' in val: return 0
            except:
                pass
            return 9999
            
        folio_keys.sort(key=get_line_num)
        
        for key in folio_keys:
            versions = line_data[key]
            text = versions.get('H') or versions.get('F') or versions.get('U') or next(iter(versions.values()))
            
            # Clean
            text = re.sub(r'\{.*?\}', '', text)
            text = text.replace('?', '')
            text = text.replace('.', ' ')
            
            words = text.split()
            if words:
                parsed_lines.append(words)
                
    return parsed_lines

def lookup_meaning(word, dictionary):
    entries = dictionary.get('entries', {})
    if word in entries:
        entry = entries[word]
        if isinstance(entry, dict):
            return entry.get('meaning') or entry.get('english') or "Defined"
        return str(entry)
    return "Unknown"

def analyze(lines, dictionary):
    sara_starts = 0
    sara_total = 0
    sara_followers = []
    
    print(f"Total lines in Quire 20: {len(lines)}")
    
    for words in lines:
        if not words: continue
        
        # Check if line starts with sara
        if words[0] == 'sara':
            sara_starts += 1
            if len(words) > 1:
                sara_followers.append(words[1])
        
        # Check all occurrences
        for i, w in enumerate(words):
            if w == 'sara':
                sara_total += 1
                if i + 1 < len(words):
                    # Add to followers list only if not already added by start check (optional, but let's separate)
                    pass 
                    
    print(f"'sara' total occurrences: {sara_total}")
    print(f"'sara' at start of line: {sara_starts}")
    
    # Analyze followers of 'sara' (all occurrences)
    all_followers = []
    for words in lines:
        for i, w in enumerate(words):
            if w == 'sara':
                if i + 1 < len(words):
                    all_followers.append(words[i+1])
    
    print("\nFollowers of 'sara':")
    counts = Counter(all_followers)
    results = []
    for word, count in counts.most_common(20):
        meaning = lookup_meaning(word, dictionary)
        print(f"- {word}: {count} ({meaning})")
        results.append({'word': word, 'count': count, 'meaning': meaning})
        
    return results

def main():
    base_path = '/Users/mike/repos/voynych2'
    quire_path = os.path.join(base_path, 'results/quire_20_recipes.json')
    text_path = os.path.join(base_path, 'results/segmented_text.txt')
    dict_path = os.path.join(base_path, 'results/dictionary/dictionary.json')
    
    dictionary = load_json(dict_path)
    folios = get_quire_folios(quire_path)
    lines = parse_lines(text_path, folios)
    
    analysis = analyze(lines, dictionary)
    
    # Write output
    report = "# 'sara' Profile\n\n"
    report += "## Investigation\n"
    report += "Analyzed text in Quire 20 (Recipes).\n\n"
    
    # Stats
    sara_count = sum(1 for l in lines for w in l if w == 'sara')
    sara_start = sum(1 for l in lines if l and l[0] == 'sara')
    
    report += f"- Total 'sara' occurrences: {sara_count}\n"
    report += f"- 'sara' at start of line: {sara_start}\n\n"
    
    report += "## Followers\n"
    for item in analysis:
        report += f"- **{item['word']}** ({item['count']}): {item['meaning']}\n"
        
    # Hypothesis Check
    report += "\n## Hypothesis Check: 'Syrup'\n"
    report += "Context: Does it appear with Water (saiin), Sweet (honey/sugar)?\n"
    
    # Check specific words
    check_words = ['saiin', 'sheedy', 'qok', 'ol'] # saiin=water, sheedy=honey?, qok=generic?, ol=preposition?
    
    for w in check_words:
        present = any(x['word'] == w for x in analysis)
        meaning = lookup_meaning(w, dictionary)
        report += f"- {w} ({meaning}): {'Found' if present else 'Not found immediately after sara'}\n"
        
    with open(os.path.join(base_path, 'results/sara_profile.md'), 'w') as f:
        f.write(report)
        
    with open(os.path.join(base_path, 'results/track-216-results_summary.md'), 'w') as f:
        f.write(f"Analyzed 'sara'. Found {sara_count} occurrences. Top followers analyzed in sara_profile.md.")

if __name__ == "__main__":
    main()
