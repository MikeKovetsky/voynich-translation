import re
import os

def load_transcription(filepath, target_pages):
    # Dictionary: page -> line_id -> {transcriber -> content}
    data = {p: {} for p in target_pages}
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            
            match = re.match(r'<f([^.]+)\.([^;]+);(\w+)>', line)
            if match:
                page_id = f"f{match.group(1)}"
                line_id = match.group(2)
                transcriber = match.group(3)
                
                if page_id in target_pages:
                    content = line.split('>', 1)[1].strip()
                    if line_id not in data[page_id]:
                        data[page_id][line_id] = {}
                    data[page_id][line_id][transcriber] = content

    final_pages = {}
    preferred_transcribers = ['H', 'C', 'F', 'U', 'N'] 
    
    for page in target_pages:
        final_pages[page] = []
        def sort_key(x):
            parts = x.split('.')
            if len(parts) > 1 and parts[-1].isdigit():
                return (parts[0], int(parts[-1]))
            elif x.isdigit():
                return ('', int(x))
            return (x, 0)
            
        sorted_lines = sorted(data[page].keys(), key=sort_key)
        
        for lid in sorted_lines:
            line_dict = data[page][lid]
            selected_content = None
            for t in preferred_transcribers:
                if t in line_dict:
                    selected_content = line_dict[t]
                    break
            if selected_content is None and line_dict:
                selected_content = list(line_dict.values())[0]
            
            if selected_content:
                final_pages[page].append(selected_content)
                
    return final_pages

def clean_word(w):
    w = re.sub(r'\{[^}]+\}', '', w)
    w = re.sub(r'<[^>]+>', '', w)
    w = w.strip('.,!?-')
    return w

def analyze_page(page_id, lines):
    print(f"\nAnalyzing {page_id}...")
    words = []
    raw_lines_words = []
    
    for line in lines:
        tokens = line.replace('.', ' ').split()
        line_words = []
        for t in tokens:
            cw = clean_word(t)
            if cw:
                line_words.append(cw)
        words.extend(line_words)
        raw_lines_words.append(line_words)
    
    subjects = [w for w in words if w.startswith('y')]
    verbs_a = [w for w in words if w.endswith('a')]
    verbs_n_strict = [w for w in words if w.endswith('n') and w != 'daiin']
    connectors = [w for w in words if w == 'daiin']
    
    print(f"Total words: {len(words)}")
    print(f"Potential Subjects (y-): {len(subjects)} ({', '.join(subjects[:5])}...)")
    print(f"Potential Verbs (-a): {len(verbs_a)} ({', '.join(verbs_a[:5])}...)")
    print(f"Potential Verbs (-n): {len(verbs_n_strict)} ({', '.join(verbs_n_strict[:5])}...)")
    print(f"Connectors (daiin): {len(connectors)}")
    
    return words, raw_lines_words

def translate_word(word):
    # Priority: daiin > Proper Nouns > y- > -a/-n
    if word == 'daiin':
        return "**THEN**"
    elif word in ['dam', 'tol', 'eain']: 
        return word.upper()
    elif word.startswith('y'):
        return f"the_{word[1:]}" 
    elif word.endswith('a'):
        return f"VERBED({word})"
    elif word.endswith('n'):
        return f"VERBED({word})"
    else:
        return word.title()

def translate_f67v2_lines(raw_lines_words):
    print("\nTranslation Attempt for f67v2 (Line by Line):")
    translated_lines = []
    for i, line_words in enumerate(raw_lines_words):
        line_trans = [translate_word(w) for w in line_words]
        line_str = f"Line {i+1}: " + " ".join(line_trans)
        translated_lines.append(line_str)
        print(line_str)
    return "\n".join(translated_lines)

def main():
    filepath = 'data/eva_ivtff.txt'
    target_pages = ['f67v2', 'f8v', 'f90r1']
    pages = load_transcription(filepath, target_pages)
    
    for p in target_pages:
        if pages[p]:
            words, raw_lines = analyze_page(p, pages[p])
            if p == 'f67v2':
                translate_f67v2_lines(raw_lines)
        else:
            print(f"Page {p} not found in transcription or empty.")

if __name__ == "__main__":
    main()
