import json
import re
import os

def load_dictionary(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return set(data['entries'].keys()), data['entries']

def parse_eva_text(path):
    # page_id -> line_id -> {transcriber: text}
    pages_lines = {}
    priority = {'H': 10, 'C': 9, 'F': 8, 'N': 7, 'U': 6, 'm': 5, 'T': 4}
    tag_pattern = re.compile(r'<f([^.]+)\.([^;]+);([^>]+)>')
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.match(r'(<[^>]+>)\s*(.*)', line)
            if not match:
                continue
            full_tag = match.group(1)
            text_content = match.group(2)
            inner_tag = full_tag[1:-1]
            parts = inner_tag.split(';')
            if len(parts) < 2:
                continue
            locators = parts[0].split('.')
            transcriber = parts[1]
            if len(locators) < 2:
                continue
            page_id = locators[0]
            line_id = ".".join(locators[1:])
            
            if page_id not in pages_lines:
                pages_lines[page_id] = {}
            
            current_score = priority.get(transcriber, 0)
            if line_id in pages_lines[page_id]:
                existing = pages_lines[page_id][line_id]
                existing_score = priority.get(existing['transcriber'], 0)
                if current_score > existing_score:
                    pages_lines[page_id][line_id] = {'transcriber': transcriber, 'text': text_content}
            else:
                pages_lines[page_id][line_id] = {'transcriber': transcriber, 'text': text_content}

    final_pages = {}
    for page_id, lines_dict in pages_lines.items():
        sorted_line_ids = sorted(lines_dict.keys(), key=lambda x: parse_line_order(x))
        all_words = []
        raw_lines = []
        for lid in sorted_line_ids:
            text = lines_dict[lid]['text']
            words = text.split('.')
            clean_words = []
            for w in words:
                w = w.strip()
                w_clean = re.sub(r'[^a-zA-Z0-9]', '', w)
                if w_clean:
                    clean_words.append(w_clean)
            if clean_words:
                all_words.extend(clean_words)
                raw_lines.append(clean_words)
        final_pages[page_id] = {
            'words': all_words,
            'lines': raw_lines
        }
    return final_pages

def parse_line_order(line_id):
    match = re.match(r'(\d+)', line_id)
    if match:
        return int(match.group(1))
    return 0

def calculate_scores(pages_data, known_words):
    page_scores = []
    for page_id, data in pages_data.items():
        words = data['words']
        total = len(words)
        if total < 20: 
            continue
        known_count = 0
        grammar_bonus_count = 0
        for w in words:
            if w in known_words:
                known_count += 1
            if w.startswith('qok') and 'ed' in w and w.endswith('y'):
                grammar_bonus_count += 1
        
        base_score = (known_count / total) * 100
        bonus = grammar_bonus_count * 5
        final_score = base_score + bonus
        
        page_scores.append({
            'page_id': page_id,
            'score': final_score,
            'base_score': base_score,
            'total': total,
            'known': known_count,
            'grammar_bonus': grammar_bonus_count,
            'words': words,
            'lines': data['lines']
        })
    
    page_scores.sort(key=lambda x: x['score'], reverse=True)
    return page_scores

def generate_translation(page_data, dictionary_entries):
    page_id = page_data['page_id']
    lines = []
    lines.append(f"# Golden Page Translation: {page_id}")
    lines.append("")
    lines.append("## Statistics")
    lines.append(f"- **Total Words:** {page_data['total']}")
    lines.append(f"- **Known Words:** {page_data['known']}")
    lines.append(f"- **Base Score:** {page_data['base_score']:.2f}%")
    lines.append(f"- **Grammar Bonus:** {page_data['grammar_bonus']} occurrences (+{page_data['grammar_bonus'] * 5})")
    lines.append(f"- **Final Score:** {page_data['score']:.2f}")
    lines.append("")
    lines.append("## Translation")
    lines.append("")
    lines.append("| Original | Translation | Confidence |")
    lines.append("| :--- | :--- | :--- |")
    
    full_text_trans = []
    
    for line_words in page_data['lines']:
        orig_line = []
        trans_line = []
        
        for w in line_words:
            orig_line.append(w)
            if w in dictionary_entries:
                entry = dictionary_entries[w]
                meaning = entry.get('meaning', '???')
                
                # Filter bad entries
                if "Jason Davies Voyager" in meaning:
                    meaning = "[Unknown/Bad Entry]"
                
                if meaning.startswith('plant:'):
                    meaning = f"**{meaning.split(':')[1].title()}**"
                elif meaning == "plant_name":
                    meaning = "[Plant Name]"
                
                trans_line.append(meaning)
            else:
                trans_line.append(f"_{w}_")
        
        lines.append(f"**Original:** `{' '.join(orig_line)}`")
        lines.append(f"**Translation:** {' '.join(trans_line)}")
        lines.append("")
        
        full_text_trans.extend(trans_line)
    
    lines.append("## Coherent Text")
    
    # Format coherent text
    coherent_text = ""
    word_count = 0
    for word in full_text_trans:
        coherent_text += word + " "
        word_count += 1
        
        # Break paragraph on 'Mix!' or 'Process!' equivalents if identified, or just length
        # 'qokeedy' usually maps to 'cook/process' or similar.
        if "cook/process" in word or "Mix!" in word:
             # Maybe break?
             pass
        
        if word_count > 30 and (word.endswith('.') or "process" in word or "Mix" in word):
            coherent_text += "\n\n"
            word_count = 0
            
    lines.append(coherent_text.strip())
    
    return "\n".join(lines)

def main():
    dict_path = 'results/dictionary/dictionary_v10_0.json'
    eva_path = 'data/eva_ivtff.txt'
    
    print(f"Loading dictionary from {dict_path}...")
    known_words, dictionary_entries = load_dictionary(dict_path)
    
    print(f"Parsing text from {eva_path}...")
    pages_data = parse_eva_text(eva_path)
    print(f"Parsed {len(pages_data)} pages.")
    
    print("Calculating scores...")
    scores = calculate_scores(pages_data, known_words)
    
    if not scores:
        print("No valid pages found.")
        return

    top_page = scores[0]
    print(f"Winner: {top_page['page_id']} with score {top_page['score']:.2f}")
    print(f"Stats: {top_page['known']}/{top_page['total']} known, {top_page['grammar_bonus']} grammar bonuses.")
    
    print("Generating translation...")
    translation_md = generate_translation(top_page, dictionary_entries)
    
    out_path = 'results/golden_page_translation.md'
    with open(out_path, 'w') as f:
        f.write(translation_md)
    print(f"Translation written to {out_path}")
    
    summary_path = 'results/track-220-results_summary.md'
    with open(summary_path, 'w') as f:
        f.write(f"# Track 220 Results Summary\n\n")
        f.write(f"## Golden Page Selection\n")
        f.write(f"- **Winner:** {top_page['page_id']}\n")
        f.write(f"- **Score:** {top_page['score']:.2f}\n")
        f.write(f"- **Coverage:** {top_page['base_score']:.2f}%\n")
        f.write(f"\nSee `{out_path}` for full translation.\n")
        
        f.write("\n## Top 5 Candidates\n")
        f.write("| Page | Score | Known/Total | Bonus |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for p in scores[:5]:
            f.write(f"| {p['page_id']} | {p['score']:.2f} | {p['known']}/{p['total']} ({p['base_score']:.1f}%) | {p['grammar_bonus']} |\n")
            
    print(f"Summary written to {summary_path}")

if __name__ == '__main__':
    main()
