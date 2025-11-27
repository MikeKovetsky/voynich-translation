import re
from collections import defaultdict

def load_data(filepath):
    sentences = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('<'):
                continue
            match = re.match(r'(<f(\d+[rv])[^>]*>)\s+(.*)', line)
            if match:
                ref = match.group(1)
                page = 'f' + match.group(2)
                text = match.group(3)
                sentences.append({'ref': ref, 'page': page, 'text': text})
    return sentences

def analyze_grammar(sentences):
    # specific pairs to look for
    targets = [
        ('daiin', 'qokeey'),
        ('aiin', 'chedy'),
        ('daiin', 'ol'),
        ('aiin', 'ol'),
        ('os', 'ol'),
        ('dar', 'ol')
    ]
    
    grammar_hits = defaultdict(list)
    
    for item in sentences:
        words = re.findall(r'\b[a-z0-9]+\b', item['text'])
        
        for w1, w2 in targets:
            if w1 in words and w2 in words:
                # Find distance
                indices1 = [i for i, w in enumerate(words) if w == w1]
                indices2 = [i for i, w in enumerate(words) if w == w2]
                
                for i1 in indices1:
                    for i2 in indices2:
                        dist = i2 - i1
                        if 1 <= dist <= 3: # w2 follows w1 within 3 words
                            grammar_hits[(w1, w2)].append({
                                'ref': item['ref'],
                                'page': item['page'],
                                'text': item['text'],
                                'context': " ".join(words[max(0, i1-2):min(len(words), i2+2)])
                            })
    return grammar_hits

def main():
    sentences = load_data('data/eva_ivtff.txt')
    hits = analyze_grammar(sentences)
    
    with open('results/astro_medicine_grammar.md', 'w') as f:
        f.write("# Astro-Medicine Grammar Analysis\n\n")
        
        for pair, items in hits.items():
            f.write(f"## Pattern: {pair[0]} -> {pair[1]} (Count: {len(items)})\n")
            # Group by page
            by_page = defaultdict(list)
            for item in items:
                by_page[item['page']].append(item)
            
            # Sort pages by frequency
            sorted_pages = sorted(by_page.items(), key=lambda x: len(x[1]), reverse=True)
            
            f.write(f"**Top Pages:** {', '.join([f'{p} ({len(l)})' for p, l in sorted_pages[:5]])}\n\n")
            
            f.write("### Examples:\n")
            for item in items[:10]:
                f.write(f"- **{item['page']}** {item['ref']}: ... `{item['context']}` ...\n")
            f.write("\n")

if __name__ == '__main__':
    main()
