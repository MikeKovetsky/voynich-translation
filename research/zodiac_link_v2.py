import os
import re
import json
import sys
from collections import defaultdict

# Ensure we can import from local modules
sys.path.append('research')
try:
    from voynich_data import get_eva_pages
except ImportError:
    try:
        import voynich_data
        get_eva_pages = voynich_data.get_eva_pages
    except ImportError:
        print("Error: Could not import voynich_data module.")
        sys.exit(1)

# Config
OUTPUT_FILE = 'results/herbal_zodiac_links_v2.json'
SUMMARY_FILE = 'results/track-289-results_summary.md' # Updating output file as per task flow

# Zodiac Page Ranges (Updated based on results/zodiac_key_report.md and standard knowledge)
ZODIAC_RANGES = {
    "Pisces": ["f70r1", "f70r2", "f70v2"], 
    "Aries": ["f70v1", "f71r"],
    "Taurus": ["f71v", "f72r1"],
    "Gemini": ["f72r2"],
    "Cancer": ["f72r3"],
    "Leo": ["f72v3"],
    "Virgo": ["f72v2"],
    "Libra": ["f72v1"],
    "Scorpio": ["f73r"],
    "Sagittarius": ["f73v"],
}

HERBAL_RANGE_START = 1
HERBAL_RANGE_END = 66

STOPWORDS = set(['daiin', 'ol', 'or', 'dy', 'qokain', 'chedy', 'shey', 'aiin', 'chol', 's', 'd', 'o', 'y'])

def load_transcription():
    print("Loading transcription using voynich_data...")
    eva_data = get_eva_pages()
    pages = defaultdict(list)
    
    for folio, lines in eva_data.items():
        page_words = []
        for text in lines.values():
            # Simple word extraction
            words = re.findall(r'[a-zA-Z0-9\*\?]+', text)
            page_words.extend(words)
        pages[folio] = page_words
            
    print(f"Loaded {len(pages)} pages.")
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
            else:
                pass
        zodiac_vocabs[sign] = get_unique_vocab(sign_words)
        print(f"Zodiac {sign}: {len(zodiac_vocabs[sign])} unique words")

    # 2. Analyze Herbal Pages
    results = {}
    
    # Get list of herbal pages (f1r to f66v)
    herbal_pages = []
    for p in pages.keys():
        if not p.startswith('f'): continue
        m = re.search(r'f(\d+)', p)
        if m:
            num = int(m.group(1))
            if HERBAL_RANGE_START <= num <= HERBAL_RANGE_END:
                herbal_pages.append(p)
    
    for page in herbal_pages:
        page_vocab = get_unique_vocab(pages[page])
        if len(page_vocab) < 10: continue # Skip empty/small pages
        
        sign_matches = []
        
        for sign, sign_vocab in zodiac_vocabs.items():
            intersection = page_vocab.intersection(sign_vocab)
            score = len(intersection)
            
            # Jaccard: intersection / union
            union = page_vocab.union(sign_vocab)
            jaccard = score / len(union) if union else 0
            
            if score > 0:
                sign_matches.append({
                    "sign": sign,
                    "score": score,
                    "jaccard": round(jaccard, 4),
                    "shared_words": list(intersection)
                })
        
        # Sort by Jaccard first, then Score
        sign_matches.sort(key=lambda x: x['jaccard'], reverse=True)
        
        if sign_matches:
            best = sign_matches[0]
            # Keep top 3
            top_matches = sign_matches[:3]
            
            results[page] = {
                "ruler": best['sign'],
                "score": best['score'],
                "jaccard": best['jaccard'],
                "shared_words": best['shared_words'],
                "all_matches": top_matches 
            }

    # 3. Write Output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
        
    # 4. Write Summary
    os.makedirs(os.path.dirname(SUMMARY_FILE), exist_ok=True)
    with open(SUMMARY_FILE, 'w') as f:
        f.write("# Herbal-Zodiac Link Results (v2.1)\n\n")
        f.write("Methodology: Vocabulary intersection between Herbal pages and Zodiac sections. Sorted by Jaccard Index.\n\n")
        f.write("| Page | Best Sign | Score | Jaccard | Top 3 Candidates |\n")
        f.write("|---|---|---|---|---|\n")
        
        # Sort by Jaccard desc
        sorted_pages = sorted(results.items(), key=lambda x: x[1]['jaccard'], reverse=True)
        
        for page, data in sorted_pages[:50]: # Top 50
            candidates = ", ".join([f"{m['sign']}({m['score']})" for m in data['all_matches']])
            f.write(f"| {page} | **{data['ruler']}** | {data['score']} | {data['jaccard']} | {candidates} |\n")

        f.write("\n## Specific Check: f41r\n")
        if 'f41r' in results:
            d = results['f41r']
            f.write(f"- Best Sign: {d['ruler']}\n")
            f.write(f"- Score: {d['score']}\n")
            f.write("- Candidates:\n")
            for m in d['all_matches']:
                f.write(f"  - {m['sign']}: Score {m['score']}, Jaccard {m['jaccard']}\n")
        else:
             f.write("f41r not found or low score.\n")

    print("Done.")

if __name__ == "__main__":
    main()