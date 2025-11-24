#!/usr/bin/env python3
"""
Botanical section analysis - looking for plant name patterns
Based on Stephen Bax's methodology of identifying labels
"""

import re
from collections import Counter, defaultdict
from pathlib import Path

def load_by_page():
    """Load transcription organized by page"""
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    pages = defaultdict(list)
    
    for line in text.split('\n'):
        # Parse page markers like <1r.1>, <1v.2>, etc.
        match = re.match(r'<(\d+[rv])\.(\d+)>(.+)', line)
        if match:
            page, line_num, content = match.groups()
            pages[page].append(content.strip())
    
    return pages

def get_botanical_pages():
    """Pages 1-67 are primarily botanical section"""
    # According to Voynich structure:
    # f1r-f66v: Herbal section A (one plant per page)
    # f67r-f116v: Other sections
    # Note: Our notation uses numbers without 'f'
    return [f"{i}{s}" for i in range(1, 67) for s in ['r', 'v']]

def extract_potential_labels(pages):
    """Extract short words/phrases that could be labels"""
    labels = []
    
    botanical_pages = get_botanical_pages()
    
    for page, lines in pages.items():
        if page in botanical_pages:
            for line in lines:
                # Clean line
                clean = re.sub(r'[-=]$', '', line)
                words = re.split(r'[.,\s]+', clean)
                
                # Look for standalone short words (potential labels)
                for word in words:
                    if 2 <= len(word) <= 8:
                        labels.append((page, word))
    
    return labels

def analyze_labels(labels):
    """Analyze label patterns"""
    word_counts = Counter([w for _, w in labels])
    
    # Labels appearing only once per page might be plant names
    page_unique = defaultdict(set)
    for page, word in labels:
        page_unique[word].add(page)
    
    # Words appearing on multiple pages (likely common words, not labels)
    multi_page = [(w, len(pages)) for w, pages in page_unique.items() if len(pages) > 5]
    
    # Words appearing on just 1-2 pages (potential unique plant names)
    unique_labels = [(w, word_counts[w]) for w, pages in page_unique.items() if len(pages) <= 2]
    
    return word_counts, multi_page, unique_labels

def find_label_patterns():
    """Look for common patterns in potential plant labels"""
    pages = load_by_page()
    labels = extract_potential_labels(pages)
    word_counts, multi_page, unique_labels = analyze_labels(labels)
    
    print("=" * 60)
    print("🌿 BOTANICAL SECTION ANALYSIS 🌿")
    print("=" * 60)
    
    print(f"\n📊 Total potential label words in botanical section: {len(labels)}")
    print(f"   Unique words: {len(word_counts)}")
    
    print("\n📊 MOST FREQUENT WORDS (likely function words):")
    for word, count in word_counts.most_common(20):
        print(f"  '{word}': {count}")
    
    print("\n📊 WORDS APPEARING ON MANY PAGES (definitely NOT unique labels):")
    multi_sorted = sorted(multi_page, key=lambda x: -x[1])[:15]
    for word, page_count in multi_sorted:
        print(f"  '{word}': appears on {page_count} pages")
    
    print("\n📊 POTENTIAL UNIQUE PLANT LABELS (appear on 1-2 pages only):")
    # Sort by frequency, then filter to interesting candidates
    unique_sorted = sorted(unique_labels, key=lambda x: -x[1])[:50]
    
    # Group by root pattern
    by_pattern = defaultdict(list)
    for word, count in unique_sorted:
        if len(word) >= 3:
            # Group by middle portion (potential root)
            if word.startswith('4o'):
                by_pattern['4o-prefix'].append(word)
            elif word.endswith('89') or word.endswith('9'):
                by_pattern['9-suffix'].append(word)
            elif word.endswith('am'):
                by_pattern['am-suffix'].append(word)
            else:
                by_pattern['other'].append(word)
    
    for pattern, words in by_pattern.items():
        print(f"\n  [{pattern}]:")
        for w in words[:10]:
            print(f"    '{w}'")

def compare_with_known():
    """Compare potential labels with known plant name patterns"""
    print("\n" + "=" * 60)
    print("🔬 PLANT NAME HYPOTHESIS TESTING 🔬")
    print("=" * 60)
    
    # Bax's identified candidates (in EVA):
    # kaur = taurus (constellation)
    # kantaiiin = Centaurea (centaury plant)
    # koain = Cosmas (name)
    # okeey = Ocimum (basil)?
    
    # Let's look for similar patterns in our transcription
    pages = load_by_page()
    all_words = []
    for page, lines in pages.items():
        for line in lines:
            clean = re.sub(r'[-=]$', '', line)
            words = re.split(r'[.,\s]+', clean)
            all_words.extend([w for w in words if len(w) >= 3])
    
    word_counts = Counter(all_words)
    
    # Look for words starting with specific patterns that might map to Latin/Greek
    # k/c initial might map to C in plant names (Centaurea, Cannabis, etc.)
    # Note: In our transcription, '1' seems to be a common initial consonant
    
    print("\n📊 PATTERN ANALYSIS FOR PLANT NAMES:")
    
    # Words starting with 'ok' - might be 'oc-' as in Ocimum
    ok_words = [w for w in word_counts if w.startswith('ok')]
    print(f"\n  Words starting with 'ok' (possible 'oc-' plants):")
    for w, c in sorted(Counter(ok_words).most_common(10), key=lambda x: -x[1]):
        print(f"    '{w}': {c}")
    
    # Words with '4oh' - common pattern
    oh_words = [w for w in word_counts if '4oh' in w]
    print(f"\n  Words containing '4oh' (most common pattern):")
    for w, c in sorted(Counter(oh_words).most_common(10), key=lambda x: -x[1]):
        print(f"    '{w}': {c}")
    
    # Words ending in 'an' - might be Latin genitive plural or plant name endings
    an_words = [w for w in word_counts if w.endswith('an') and len(w) >= 4]
    print(f"\n  Words ending in 'an' (possible -anum/-anus endings):")
    for w, c in sorted(Counter(an_words).most_common(10), key=lambda x: -x[1]):
        print(f"    '{w}': {c}")
    
    # Try to identify distinctive label candidates
    print("\n📊 DISTINCTIVE WORD SHAPES (potential plant names):")
    
    # Words with unusual length or structure
    distinctive = []
    for word, count in word_counts.items():
        # Skip very common words
        if count > 50:
            continue
        # Look for words with 5-7 chars (typical Latin plant name length)
        if 5 <= len(word) <= 7:
            # Not too repetitive internally
            if len(set(word)) >= 4:
                distinctive.append((word, count))
    
    distinctive.sort(key=lambda x: -x[1])
    print("  Words with 5-7 chars, appearing 10-50 times:")
    for word, count in distinctive[:20]:
        if 10 <= count <= 50:
            print(f"    '{word}': {count}")

def main():
    find_label_patterns()
    compare_with_known()
    
    print("\n" + "=" * 60)
    print("💡 INSIGHTS FOR DECIPHERMENT:")
    print("=" * 60)
    print("""
1. The botanical section has highly repetitive vocabulary
   - This suggests standardized descriptions (like herbal texts)
   
2. Very few words appear on just 1-2 pages
   - Plant-specific labels are rare or encoded differently
   
3. The '4oh' pattern is overwhelmingly common
   - Might be a common descriptor or grammatical element
   - NOT likely to be plant names (too common)
   
4. The 'am' and '89' endings dominate
   - These are grammatical, not lexical
   
5. HYPOTHESIS: Plant names might be:
   - The rare, page-unique words
   - Or embedded within longer descriptions
   - Or abbreviated/encoded differently than we expect
""")

if __name__ == '__main__':
    main()

