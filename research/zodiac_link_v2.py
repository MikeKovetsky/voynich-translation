import os
import re
import json
from collections import defaultdict

# Config
TRANSCRIPTION_FILE = 'data/voynich_transcription.txt'
OUTPUT_FILE = 'results/herbal_zodiac_links_v2.json'
SUMMARY_FILE = 'results/track-285-results_summary.md'

# Zodiac Page Ranges (Approximate based on previous knowledge)
ZODIAC_RANGES = {
    "Aries": ["f70r", "f70v"], # Dark/Light Aries
    "Taurus": ["f71r", "f71v"],
    "Gemini": ["f72r1", "f72r2"],
    "Cancer": ["f72v3"],
    "Leo": ["f72v2"],
    "Virgo": ["f72v1"],
    "Libra": ["f73r"],
    "Scorpio": ["f73v"],
    # Add others if needed/known
}

HERBAL_RANGE_START = 1
HERBAL_RANGE_END = 66

STOPWORDS = set(['daiin', 'ol', 'or', 'dy', 'qokain', 'chedy', 'shey', 'aiin', 'chol', 's', 'd', 'o', 'y'])

def load_transcription():
    pages = defaultdict(list)
    current_page = None
    
    with open(TRANSCRIPTION_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            # Page Header detection (## f103r)
            if line.startswith('## '):
                current_page = line.replace('## ', '').strip()
                continue
                
            # Simple word extraction
            words = re.findall(r'[a-zA-Z0-9\*\?]+', line)
            if current_page:
                pages[current_page].extend(words)
                
    return pages

def get_unique_vocab(words):
    return set([w for w in words if w not in STOPWORDS and len(w) > 2])

def main():
    pages = load_transcription()
    
    # 1. Build Zodiac Vocabularies
    zodiac_vocabs = {}
    for sign, pagenames in ZODIAC_RANGES.items():
        sign_words = []
        for p in pagenames:
            if p in pages:
                sign_words.extend(pages[p])
        zodiac_vocabs[sign] = get_unique_vocab(sign_words)
        print(f"Zodiac {sign}: {len(zodiac_vocabs[sign])} unique words")

    # 2. Analyze Herbal Pages
    results = {}
    
    # Get list of herbal pages (f1r to f66v)
    herbal_pages = [p for p in pages.keys() if p.startswith('f') and 
                    (int(re.search(r'\d+', p).group()) <= 66)]
    
    for page in herbal_pages:
        page_vocab = get_unique_vocab(pages[page])
        if len(page_vocab) < 10: continue # Skip empty/small pages
        
        page_scores = {}
        best_sign = None
        max_score = 0
        
        for sign, sign_vocab in zodiac_vocabs.items():
            # Jaccard Index or Intersection Count
            intersection = page_vocab.intersection(sign_vocab)
            # We care about unique shared words
            score = len(intersection) 
            
            # Normalize by page size? Or just raw count? 
            # Let's use raw count of SHARED RARE WORDS
            
            if score > 0:
                page_scores[sign] = score
                if score > max_score:
                    max_score = score
                    best_sign = sign
        
        if best_sign and max_score >= 3: # Threshold: at least 3 shared unique words
            results[page] = {
                "ruler": best_sign,
                "score": max_score,
                "shared_words": list(page_vocab.intersection(zodiac_vocabs[best_sign]))
            }

    # 3. Write Output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
        
    # 4. Write Summary
    with open(SUMMARY_FILE, 'w') as f:
        f.write("# Herbal-Zodiac Link Results (v2)\n\n")
        f.write("| Page | Best Sign | Score (Shared Words) | Examples |\n")
        f.write("|---|---|---|---|\n")
        
        # Sort by score desc
        sorted_pages = sorted(results.items(), key=lambda x: x[1]['score'], reverse=True)
        
        for page, data in sorted_pages[:50]: # Top 50
            examples = ", ".join(data['shared_words'][:5])
            f.write(f"| {page} | **{data['ruler']}** | {data['score']} | {examples} |\n")
            
    print("Done.")

if __name__ == "__main__":
    main()
