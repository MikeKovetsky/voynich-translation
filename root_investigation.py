import voynich_data
import re
import json
from collections import Counter

# Constants
OUTPUT_REPORT = 'results/root_chol_char_report.md'
OUTPUT_STATS = 'results/chol_char_stats.json'
MASTER_DICT_FILE = 'results/master_dictionary_v7.json'

# Visual Metadata (Combined from herbal_descriptors.py and extended_illust.py)
# We add 'has_flowers', 'has_roots', 'leaf_size'
PAGE_METADATA = {
    'f17r': {'leaves': 'small', 'roots': True, 'flowers': True},   # Linear leaves -> Small
    'f6r':  {'leaves': 'big',   'roots': True, 'flowers': False},  # Lobed/Fern-like -> Big
    'f5r':  {'leaves': 'big',   'roots': False, 'flowers': True},  # Large round leaves. Roots minimal
    'f2v':  {'leaves': 'big',   'roots': True, 'flowers': True},   # Round -> Big
    'f25v': {'leaves': 'big',   'roots': True, 'flowers': False},  # Palmate -> Big
    'f3r':  {'leaves': 'big',   'roots': True, 'flowers': True},   # Succulent -> Big
    'f9r':  {'leaves': 'big',   'roots': True, 'flowers': False},  # Lobed -> Big
    'f4r':  {'leaves': 'small', 'roots': True, 'flowers': True},   # Small leaves
    'f4v':  {'leaves': 'small', 'roots': True, 'flowers': True},   # Star/Sickle -> Small
    'f5v':  {'leaves': 'big',   'roots': True, 'flowers': True},   # Lobed -> Big
    'f6v':  {'leaves': 'small', 'roots': True, 'flowers': True},   # Star/Pointed -> Small
}

def get_variations(root):
    """Generate variations for a root."""
    prefixes = ['qok', 'd', 'y', 'o', 'q', 's', 'l', 't']
    variations = [root]
    for p in prefixes:
        variations.append(p + root)
    return variations

def analyze_morphology(words, root):
    """Check for prefixes and variations in the text."""
    variations = get_variations(root)
    found_variations = Counter()
    for word in words:
        if word in variations:
             found_variations[word] += 1
    return found_variations

def run_analysis():
    print("Loading data...")
    eva_pages = voynich_data.get_eva_pages()
    
    all_words_flat = []
    page_words = {} # folio -> list of words
    
    for folio, lines in eva_pages.items():
        p_words = []
        for loc, text in lines.items():
            clean = text.replace('-', '').replace('=', '')
            for w in clean.split('.'):
                if w.strip():
                    p_words.append(w.strip())
                    all_words_flat.append(w.strip())
        page_words[folio] = p_words

    # TASK 1: Morphology
    chol_vars = analyze_morphology(all_words_flat, 'chol')
    char_vars = analyze_morphology(all_words_flat, 'char')
    
    # TASK 2: Visual Correlation
    big_leaf_pages = [f for f, m in PAGE_METADATA.items() if m['leaves'] == 'big']
    small_leaf_pages = [f for f, m in PAGE_METADATA.items() if m['leaves'] == 'small']
    
    flower_pages = [f for f, m in PAGE_METADATA.items() if m['flowers']]
    no_flower_pages = [f for f, m in PAGE_METADATA.items() if not m['flowers']]
    
    root_pages = [f for f, m in PAGE_METADATA.items() if m['roots']]
    no_root_pages = [f for f, m in PAGE_METADATA.items() if not m['roots']] 

    def count_on_pages(target_root, pages):
        count = 0
        total_words = 0
        target_vars = get_variations(target_root)
        for folio in pages:
            if folio in page_words:
                words = page_words[folio]
                total_words += len(words)
                for w in words:
                    if w in target_vars or w == target_root:
                        count += 1
        return count, total_words

    def rate(count, total):
        return (count / total * 1000) if total > 0 else 0

    stats = {
        'morphology': {
            'chol_variations': dict(chol_vars.most_common()),
            'char_variations': dict(char_vars.most_common()),
        },
        'visual_correlation': {
            'chol_leaves': {
                'big_leaves': {'count': count_on_pages('chol', big_leaf_pages)[0], 'rate': rate(*count_on_pages('chol', big_leaf_pages))},
                'small_leaves': {'count': count_on_pages('chol', small_leaf_pages)[0], 'rate': rate(*count_on_pages('chol', small_leaf_pages))},
            },
            'char_flowers': {
                'flowers': {'count': count_on_pages('char', flower_pages)[0], 'rate': rate(*count_on_pages('char', flower_pages))},
                'no_flowers': {'count': count_on_pages('char', no_flower_pages)[0], 'rate': rate(*count_on_pages('char', no_flower_pages))},
            },
            'char_roots': {
                'roots': {'count': count_on_pages('char', root_pages)[0], 'rate': rate(*count_on_pages('char', root_pages))},
                'no_roots': {'count': count_on_pages('char', no_root_pages)[0], 'rate': rate(*count_on_pages('char', no_root_pages))},
            }
        }
    }

    with open(OUTPUT_STATS, 'w') as f:
        json.dump(stats, f, indent=2)

if __name__ == '__main__':
    run_analysis()
