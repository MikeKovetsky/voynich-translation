import re
import json
from collections import Counter, defaultdict

def parse_claston(filepath):
    """Parse Glen Claston v101 transcription"""
    pages = defaultdict(list)
    with open(filepath, 'r') as f:
        for line in f:
            match = re.match(r'<(\d+[rv])\.(\d+)>(.+)', line.strip())
            if match:
                page, linenum, text = match.groups()
                text = re.sub(r'[.,!?=\-<>]', ' ', text)
                words = [w for w in text.split() if w]
                pages[page].append((int(linenum), words))
    return pages

def parse_eva_ivtff(filepath, transcriber='H'):
    """Parse EVA IVTFF format, selecting one transcriber"""
    pages = defaultdict(list)
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            match = re.match(r'<f(\d+[rv])\.(\d+),[^;]+;(\w)>\s+(.+)', line.strip())
            if match:
                page, linenum, trans, text = match.groups()
                if trans == transcriber:
                    text = re.sub(r'[.,!?=\-<>\[\]\'@{}]', ' ', text)
                    text = re.sub(r'[!?*%&]', '', text)
                    words = [w for w in text.split() if w and len(w) > 0]
                    pages[page].append((int(linenum), words))
    return pages

def char_freq(pages):
    """Get character frequencies from parsed pages"""
    chars = Counter()
    for page, lines in pages.items():
        for linenum, words in lines:
            for word in words:
                for ch in word:
                    chars[ch] += 1
    return chars

def word_freq(pages):
    """Get word frequencies from parsed pages"""
    words = Counter()
    for page, lines in pages.items():
        for linenum, wordlist in lines:
            for word in wordlist:
                words[word] += 1
    return words

def word_endings(pages):
    """Analyze word endings"""
    endings = Counter()
    for page, lines in pages.items():
        for linenum, words in lines:
            for word in words:
                if len(word) >= 2:
                    endings[word[-2:]] += 1
                if len(word) >= 1:
                    endings[word[-1]] += 1
    return endings

def word_starts(pages):
    """Analyze word beginnings"""
    starts = Counter()
    for page, lines in pages.items():
        for linenum, words in lines:
            for word in words:
                if len(word) >= 2:
                    starts[word[:2]] += 1
                if len(word) >= 1:
                    starts[word[0]] += 1
    return starts

def compare_pages(claston_pages, eva_pages, sample_pages=['1r', '1v', '2r', '2v']):
    """Compare words between Claston and EVA for alignment"""
    print("\n" + "="*70)
    print("PAGE COMPARISON: CLASTON vs EVA")
    print("="*70)
    
    for page in sample_pages:
        cl_lines = claston_pages.get(page, [])
        ev_lines = eva_pages.get(page, [])
        
        print(f"\n--- Page {page} ---")
        print(f"Claston: {len(cl_lines)} lines, EVA: {len(ev_lines)} lines")
        
        for i in range(min(3, len(cl_lines), len(ev_lines))):
            cl_num, cl_words = cl_lines[i] if i < len(cl_lines) else (0, [])
            ev_num, ev_words = ev_lines[i] if i < len(ev_lines) else (0, [])
            
            print(f"\n  Line {i+1}:")
            print(f"    CL: {' '.join(cl_words[:8])}...")
            print(f"    EV: {' '.join(ev_words[:8])}...")
            
            if len(cl_words) == len(ev_words):
                print(f"    ✓ Same word count: {len(cl_words)}")
            else:
                print(f"    ✗ Word count differs: CL={len(cl_words)}, EV={len(ev_words)}")

def build_freq_mapping(claston_chars, eva_chars, top_n=30):
    """Build character mapping based on frequency matching"""
    cl_sorted = [ch for ch, _ in claston_chars.most_common(top_n)]
    ev_sorted = [ch for ch, _ in eva_chars.most_common(top_n)]
    
    print("\n" + "="*70)
    print("CHARACTER FREQUENCY COMPARISON")
    print("="*70)
    
    print(f"\n{'Rank':<6}{'Claston':<15}{'EVA':<15}{'CL Freq':<12}{'EV Freq':<12}")
    print("-"*60)
    
    mapping = {}
    for i in range(min(len(cl_sorted), len(ev_sorted))):
        cl_ch = cl_sorted[i]
        ev_ch = ev_sorted[i]
        cl_freq = claston_chars[cl_ch]
        ev_freq = eva_chars[ev_ch]
        print(f"{i+1:<6}{repr(cl_ch):<15}{repr(ev_ch):<15}{cl_freq:<12}{ev_freq:<12}")
        mapping[cl_ch] = ev_ch
    
    return mapping

def analyze_eva_digraphs(eva_pages):
    """Identify EVA digraphs (sh, ch, etc.)"""
    digraphs = Counter()
    for page, lines in eva_pages.items():
        for linenum, words in lines:
            for word in words:
                for dg in ['sh', 'ch', 'th', 'cth', 'ckh', 'cph', 'cfh', 'ai', 'ii', 'ee', 'oi']:
                    digraphs[dg] += word.count(dg)
    return digraphs

def main():
    print("="*70)
    print("EVA TRANSCRIPTION MAPPING ANALYSIS")
    print("="*70)
    
    claston_pages = parse_claston('voynich_raw.txt')
    eva_pages = parse_eva_ivtff('data/eva_ivtff.txt', 'H')
    
    print(f"\nClaston: {len(claston_pages)} pages")
    print(f"EVA: {len(eva_pages)} pages")
    
    claston_chars = char_freq(claston_pages)
    eva_chars = char_freq(eva_pages)
    
    claston_words = word_freq(claston_pages)
    eva_words = word_freq(eva_pages)
    
    print(f"\nClaston unique chars: {len(claston_chars)}")
    print(f"EVA unique chars: {len(eva_chars)}")
    
    print(f"\nClaston unique words: {len(claston_words)}")
    print(f"EVA unique words: {len(eva_words)}")
    
    mapping = build_freq_mapping(claston_chars, eva_chars)
    
    print("\n" + "="*70)
    print("EVA DIGRAPH FREQUENCY")
    print("="*70)
    digraphs = analyze_eva_digraphs(eva_pages)
    for dg, count in digraphs.most_common(15):
        print(f"  {dg}: {count}")
    
    compare_pages(claston_pages, eva_pages)
    
    print("\n" + "="*70)
    print("WORD ENDING COMPARISON")
    print("="*70)
    
    cl_endings = word_endings(claston_pages)
    ev_endings = word_endings(eva_pages)
    
    print("\nTop Claston endings:")
    for end, cnt in cl_endings.most_common(10):
        print(f"  '{end}': {cnt}")
    
    print("\nTop EVA endings:")
    for end, cnt in ev_endings.most_common(10):
        print(f"  '{end}': {cnt}")
    
    print("\n" + "="*70)
    print("TOP WORDS COMPARISON")
    print("="*70)
    
    print("\nTop 15 Claston words:")
    for word, cnt in claston_words.most_common(15):
        print(f"  {word}: {cnt}")
    
    print("\nTop 15 EVA words:")
    for word, cnt in eva_words.most_common(15):
        print(f"  {word}: {cnt}")
    
    results = {
        'claston_chars': dict(claston_chars.most_common(50)),
        'eva_chars': dict(eva_chars.most_common(50)),
        'freq_mapping': mapping,
        'claston_top_words': dict(claston_words.most_common(30)),
        'eva_top_words': dict(eva_words.most_common(30))
    }
    
    with open('results/eva_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n\nResults saved to results/eva_analysis.json")

if __name__ == '__main__':
    main()
