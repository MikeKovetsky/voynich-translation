#!/usr/bin/env python3
"""
Word Grammar Analysis - Finding the internal structure of Voynich words
Trying to identify PREFIX-ROOT-SUFFIX patterns
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
import itertools

def load_words():
    text = Path('voynich_raw.txt').read_text(encoding='utf-8')
    words = []
    for line in text.split('\n'):
        clean = re.sub(r'<[^>]+>', '', line)
        clean = re.sub(r'[-=]$', '', clean)
        if clean.strip():
            ws = re.split(r'[.,\s]+', clean)
            words.extend([w for w in ws if w and len(w) > 0])
    return words

def identify_affixes(words, min_freq=100):
    """Identify likely prefixes and suffixes based on frequency"""
    # Prefix analysis (first 1-3 characters)
    prefixes = Counter()
    for w in words:
        for i in range(1, min(4, len(w))):
            prefixes[w[:i]] += 1
    
    # Suffix analysis (last 1-3 characters)  
    suffixes = Counter()
    for w in words:
        for i in range(1, min(4, len(w))):
            suffixes[w[-i:]] += 1
    
    # Filter by frequency
    common_pref = {p for p, c in prefixes.items() if c >= min_freq}
    common_suff = {s for s, c in suffixes.items() if c >= min_freq}
    
    return common_pref, common_suff, prefixes, suffixes

def decompose_word(word, prefixes, suffixes):
    """Try to decompose a word into prefix-root-suffix"""
    best_decomp = None
    best_score = -1
    
    # Sort by length (prefer longer matches)
    sorted_pref = sorted([p for p in prefixes if word.startswith(p)], 
                        key=len, reverse=True)
    sorted_suff = sorted([s for s in suffixes if word.endswith(s)],
                        key=len, reverse=True)
    
    for pref in [''] + sorted_pref[:3]:
        for suff in [''] + sorted_suff[:3]:
            # Check for overlap
            if len(pref) + len(suff) >= len(word):
                continue
            
            root = word[len(pref):len(word)-len(suff)] if suff else word[len(pref):]
            
            if len(root) >= 1:  # Must have some root
                # Score: prefer balanced decomposition
                score = len(pref) + len(suff) + (1 if len(root) >= 2 else 0)
                if score > best_score:
                    best_score = score
                    best_decomp = (pref, root, suff)
    
    return best_decomp or ('', word, '')

def analyze_word_grammar(words):
    """Analyze grammatical patterns in word formation"""
    common_pref, common_suff, pref_counts, suff_counts = identify_affixes(words)
    
    print("=" * 60)
    print("🔤 VOYNICH WORD GRAMMAR ANALYSIS 🔤")
    print("=" * 60)
    
    # Most common affixes
    print("\n📊 TOP 15 PREFIXES (by frequency):")
    for pref, count in sorted(pref_counts.items(), key=lambda x: -x[1])[:15]:
        pct = count / len(words) * 100
        print(f"  '{pref}': {count} ({pct:.1f}%)")
    
    print("\n📊 TOP 15 SUFFIXES (by frequency):")
    for suff, count in sorted(suff_counts.items(), key=lambda x: -x[1])[:15]:
        pct = count / len(words) * 100
        print(f"  '{suff}': {count} ({pct:.1f}%)")
    
    # Decompose all words
    print("\n📊 WORD DECOMPOSITION ANALYSIS:")
    
    decompositions = []
    for w in words:
        decomp = decompose_word(w, common_pref, common_suff)
        decompositions.append((w, decomp))
    
    # Analyze roots
    roots = Counter([d[1] for _, d in decompositions if d[1]])
    
    print("\n  TOP 20 ROOT MORPHEMES:")
    for root, count in roots.most_common(20):
        pct = count / len(words) * 100
        print(f"    '{root}': {count} ({pct:.1f}%)")
    
    # Prefix-Root patterns
    pref_root = Counter([(d[0], d[1]) for _, d in decompositions if d[0]])
    print("\n  TOP 15 PREFIX+ROOT COMBINATIONS:")
    for (pref, root), count in pref_root.most_common(15):
        print(f"    '{pref}'+'{root}': {count}")
    
    # Root-Suffix patterns
    root_suff = Counter([(d[1], d[2]) for _, d in decompositions if d[2]])
    print("\n  TOP 15 ROOT+SUFFIX COMBINATIONS:")
    for (root, suff), count in root_suff.most_common(15):
        print(f"    '{root}'+'{suff}': {count}")
    
    return decompositions, roots

def find_paradigms(decompositions):
    """Find inflectional paradigms (same root, different affixes)"""
    print("\n" + "=" * 60)
    print("🔬 INFLECTIONAL PARADIGM ANALYSIS 🔬")
    print("=" * 60)
    
    # Group words by root
    by_root = defaultdict(list)
    for word, (pref, root, suff) in decompositions:
        if len(root) >= 2:
            by_root[root].append((word, pref, suff))
    
    # Find roots with multiple forms
    paradigms = [(root, forms) for root, forms in by_root.items() 
                 if len(set(forms)) >= 4]
    paradigms.sort(key=lambda x: -len(x[1]))
    
    print(f"\n📊 ROOTS WITH 4+ DIFFERENT WORD FORMS (paradigms):")
    
    for root, forms in paradigms[:15]:
        unique_forms = set(forms)
        print(f"\n  Root '{root}' ({len(forms)} occurrences, {len(unique_forms)} forms):")
        
        # Group by prefix
        by_pref = defaultdict(list)
        for word, pref, suff in unique_forms:
            by_pref[pref].append((word, suff))
        
        for pref, word_suffs in sorted(by_pref.items()):
            print(f"    Prefix '{pref}':")
            for word, suff in sorted(word_suffs, key=lambda x: x[0])[:5]:
                print(f"      '{word}' (suffix: '{suff}')")

def propose_grammar():
    """Propose a grammatical analysis"""
    print("\n" + "=" * 60)
    print("💡 PROPOSED VOYNICH WORD GRAMMAR 💡")
    print("=" * 60)
    print("""
Based on the analysis, here's a proposed word structure:

┌─────────────────────────────────────────────────────────┐
│ VOYNICH WORD = [DETERMINER] + [ROOT] + [CASE ENDING]   │
└─────────────────────────────────────────────────────────┘

DETERMINERS (prefixes):
  '4o'  → Definite article? ("the")
  '1'   → Verbal/action marker?
  'o'   → Direct object marker?
  '8'   → Genitive marker? ("of")

ROOTS (lexical morphemes):
  'h'/'ha'/'oh' → Very common - might be a semantically rich root
  'c'/'1c'     → Another common root class
  'k'/'ok'     → Third root class

CASE ENDINGS (suffixes):
  '9'   → Nominative/default case (37% of words!)
  '89'  → Genitive plural? ("of the X")
  'am'  → Accusative/object case
  'oe'  → Dative/locative case
  'ay'  → Genitive singular?
  'ae'  → Instrumental case?
  'an'  → Some grammatical function

This is consistent with an AGGLUTINATIVE language structure
similar to Turkish, Finnish, Hungarian, or Basque.

The extremely high frequency of '9' as an ending suggests it 
might be a default/unmarked case (like nominative).
""")

def main():
    words = load_words()
    print(f"Loaded {len(words)} words")
    
    decompositions, roots = analyze_word_grammar(words)
    find_paradigms(decompositions)
    propose_grammar()

if __name__ == '__main__':
    main()

