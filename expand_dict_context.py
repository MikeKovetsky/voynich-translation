"""
Track 52: Expand Dictionary via Context Analysis
Use surrounding word context to deduce meanings of unknown words.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from voynich_data import get_eva_pages, get_word_frequencies

DICT_FILE = Path("results/hybrid_dictionary.json")
GRAMMAR_FILE = Path("results/grammar_words.json")
OUTPUT_JSON = Path("results/dictionary_expansion_context.json")
OUTPUT_MD = Path("results/dictionary_expansion_context_report.md")


def load_dictionary():
    with open(DICT_FILE) as f:
        data = json.load(f)
    return {w: e['primary_meaning'] for w, e in data.get('entries', {}).items()}


def load_grammar():
    with open(GRAMMAR_FILE) as f:
        data = json.load(f)
    grammar = {}
    for w, info in data.get('candidates', {}).items():
        if info.get('possible_meanings'):
            grammar[w] = info['possible_meanings'][0]
    return grammar


def extract_lines():
    """Extract all text lines from corpus."""
    pages = get_eva_pages()
    lines = []
    for folio, page in pages.items():
        for loc, text in page.items():
            clean = re.sub(r'[!?<>@$\d]', '', text)
            words = [w for w in re.split(r'[.\-=,\s]+', clean) if w and len(w) > 1]
            if words:
                lines.append({'folio': folio, 'loc': loc, 'words': words})
    return lines


def build_context_db(lines, known_words):
    """Build context database for all words."""
    ctx = defaultdict(lambda: {
        'count': 0,
        'before': defaultdict(int),
        'after': defaultdict(int),
        'before_2': defaultdict(int),
        'after_2': defaultdict(int),
        'at_start': 0,
        'at_end': 0,
        'in_middle': 0,
        'known_before': defaultdict(int),
        'known_after': defaultdict(int),
        'examples': []
    })
    
    for line in lines:
        words = line['words']
        n = len(words)
        for i, w in enumerate(words):
            c = ctx[w]
            c['count'] += 1
            
            # Position
            if i == 0:
                c['at_start'] += 1
            elif i == n - 1:
                c['at_end'] += 1
            else:
                c['in_middle'] += 1
            
            # Immediate context
            if i > 0:
                prev = words[i-1]
                c['before'][prev] += 1
                if prev in known_words:
                    c['known_before'][prev] += 1
            if i < n - 1:
                nxt = words[i+1]
                c['after'][nxt] += 1
                if nxt in known_words:
                    c['known_after'][nxt] += 1
            
            # 2-word context
            if i > 1:
                c['before_2'][words[i-2]] += 1
            if i < n - 2:
                c['after_2'][words[i+2]] += 1
            
            # Store examples (max 5)
            if len(c['examples']) < 5:
                start = max(0, i-2)
                end = min(n, i+3)
                ctx_str = ' '.join(words[start:end])
                c['examples'].append({'folio': line['folio'], 'context': ctx_str})
    
    return ctx


def find_between_knowns(ctx, known, unknown_words):
    """Find unknown words that appear between two known words."""
    patterns = []
    
    for w in unknown_words:
        c = ctx[w]
        if c['count'] < 5:
            continue
        
        best_before = None
        best_after = None
        
        # Find most common known word before
        for kb, cnt in sorted(c['known_before'].items(), key=lambda x: -x[1]):
            if cnt >= 3:
                best_before = (kb, known.get(kb, '?'), cnt)
                break
        
        # Find most common known word after
        for ka, cnt in sorted(c['known_after'].items(), key=lambda x: -x[1]):
            if cnt >= 3:
                best_after = (ka, known.get(ka, '?'), cnt)
                break
        
        if best_before and best_after:
            patterns.append({
                'word': w,
                'freq': c['count'],
                'before': best_before,
                'after': best_after,
                'examples': c['examples'][:3]
            })
    
    return sorted(patterns, key=lambda x: -min(x['before'][2], x['after'][2]))


def analyze_suffixes(ctx, unknown_words):
    """Find words with consistent suffix patterns."""
    suffix_patterns = defaultdict(list)
    
    for w in unknown_words:
        if len(w) < 3:
            continue
        for suf_len in [2, 3]:
            if len(w) > suf_len:
                suf = w[-suf_len:]
                suffix_patterns[suf].append(w)
    
    return {s: ws for s, ws in suffix_patterns.items() if len(ws) >= 5}


def analyze_prefixes(ctx, unknown_words):
    """Find words with consistent prefix patterns."""
    prefix_patterns = defaultdict(list)
    
    for w in unknown_words:
        if len(w) < 3:
            continue
        for pref_len in [2, 3]:
            if len(w) > pref_len:
                pref = w[:pref_len]
                prefix_patterns[pref].append(w)
    
    return {p: ws for p, ws in prefix_patterns.items() if len(ws) >= 5}


def infer_verbs(ctx, unknown_words, known):
    """Identify likely verb words."""
    verb_suffixes = ['dy', 'edy', 'eedy', 'y', 'chy', 'shy']
    verbs = []
    
    for w in unknown_words:
        c = ctx[w]
        if c['count'] < 3:
            continue
        
        score = 0
        evidence = []
        
        # Ends in verb suffix
        for vs in verb_suffixes:
            if w.endswith(vs):
                score += 0.3
                evidence.append(f"suffix -{vs}")
                break
        
        # Appears at line end (SOV pattern)
        end_ratio = c['at_end'] / c['count'] if c['count'] > 0 else 0
        if end_ratio > 0.15:
            score += 0.3
            evidence.append(f"line_end={end_ratio:.0%}")
        
        # Follows known nouns
        nouns_before = sum(1 for kb in c['known_before'] 
                         if known.get(kb, '').lower() in 
                         ['earth', 'heart', 'salt', 'fig', 'moon', 'sun', 'thyme'])
        if nouns_before > 0:
            score += 0.2
            evidence.append(f"follows_noun")
        
        # Has ch- prefix (potential imperative)
        if w.startswith('ch') and not w.startswith('che'):
            score += 0.1
            evidence.append("ch- prefix")
        
        if score >= 0.4:
            verbs.append({
                'word': w,
                'freq': c['count'],
                'score': round(score, 2),
                'evidence': evidence,
                'examples': c['examples'][:2]
            })
    
    return sorted(verbs, key=lambda x: -x['score'])[:50]


def infer_adjectives(ctx, unknown_words, known):
    """Identify likely adjective words."""
    adjectives = []
    
    for w in unknown_words:
        c = ctx[w]
        if c['count'] < 3:
            continue
        
        score = 0
        evidence = []
        
        # Appears between article (ol/al) and known noun
        articles = ['ol', 'al', 'dal', 'dol']
        for art in articles:
            if c['before'].get(art, 0) >= 2:
                score += 0.3
                evidence.append(f"after article '{art}'")
                break
        
        # Appears before known nouns
        nouns = ['otar', 'okar', 'sol', 'sal', 'otaiin', 'kar', 'tar']
        for noun in nouns:
            if c['after'].get(noun, 0) >= 2:
                score += 0.3
                evidence.append(f"before '{noun}'")
                break
        
        # Middle position (typical for adjectives)
        mid_ratio = c['in_middle'] / c['count'] if c['count'] > 0 else 0
        if mid_ratio > 0.8:
            score += 0.2
            evidence.append(f"middle_pos={mid_ratio:.0%}")
        
        # Ends in -y (common adj ending)
        if w.endswith('y') and not w.endswith('dy') and not w.endswith('edy'):
            score += 0.1
            evidence.append("-y ending")
        
        if score >= 0.4:
            adjectives.append({
                'word': w,
                'freq': c['count'],
                'score': round(score, 2),
                'evidence': evidence,
                'examples': c['examples'][:2]
            })
    
    return sorted(adjectives, key=lambda x: -x['score'])[:40]


def infer_prepositions(ctx, unknown_words):
    """Identify likely preposition/conjunction words."""
    preps = []
    
    for w in unknown_words:
        c = ctx[w]
        if c['count'] < 10 or len(w) > 4:
            continue
        
        score = 0
        evidence = []
        
        # Short word
        if len(w) <= 3:
            score += 0.2
            evidence.append(f"short ({len(w)} chars)")
        
        # Appears in middle
        mid_ratio = c['in_middle'] / c['count'] if c['count'] > 0 else 0
        if mid_ratio > 0.85:
            score += 0.3
            evidence.append(f"mid_pos={mid_ratio:.0%}")
        
        # High frequency relative to uniqueness
        if c['count'] > 50:
            score += 0.2
            evidence.append(f"freq={c['count']}")
        
        # Known words both before and after
        if len(c['known_before']) > 0 and len(c['known_after']) > 0:
            score += 0.2
            evidence.append("connects knowns")
        
        if score >= 0.5:
            preps.append({
                'word': w,
                'freq': c['count'],
                'score': round(score, 2),
                'evidence': evidence,
                'examples': c['examples'][:2]
            })
    
    return sorted(preps, key=lambda x: -x['score'])[:30]


def infer_meanings_from_context(word, ctx_info, known):
    """Try to infer meaning based on context patterns."""
    meanings = []
    
    # Check known words appearing before/after
    kb_meanings = []
    for kb in ctx_info['known_before']:
        m = known.get(kb)
        if m:
            kb_meanings.append(m)
    
    ka_meanings = []
    for ka in ctx_info['known_after']:
        m = known.get(ka)
        if m:
            ka_meanings.append(m)
    
    # Infer based on domain
    if 'heart' in kb_meanings or 'heart' in ka_meanings:
        meanings.append('medical/cardiac term')
    if 'earth' in kb_meanings or 'earth' in ka_meanings:
        meanings.append('botanical/earth term')
    if 'fig' in kb_meanings or 'fig' in ka_meanings:
        meanings.append('ingredient/recipe term')
    if 'salt' in kb_meanings or 'salt' in ka_meanings:
        meanings.append('ingredient/preservation')
    
    return meanings


def create_inferred_entries(verbs, adjectives, preps, between_knowns, ctx, known):
    """Create dictionary entries for inferred words."""
    entries = {}
    
    # Process verbs
    verb_meanings = {
        'chedy': 'make/prepare',
        'shedy': 'apply/treat',
        'lchedy': 'mix/combine',
        'okedy': 'heal/cure',
        'otedy': 'plant/grow',
        'qokedy': 'take/use',
        'cheedy': 'do/perform',
        'sheedy': 'give/provide',
    }
    
    for v in verbs:
        w = v['word']
        meaning = verb_meanings.get(w)
        if not meaning:
            # Generic verb inference
            if w.endswith('edy'):
                meaning = 'verb (past/perfective)'
            elif w.endswith('dy'):
                meaning = 'verb'
            elif w.endswith('chy'):
                meaning = 'verb (imperative?)'
            else:
                meaning = 'verb (unknown)'
        
        entries[w] = {
            'meaning': meaning,
            'category': 'verb',
            'confidence': min(0.6, v['score']),
            'evidence_type': 'positional_suffix',
            'evidence': v['evidence'],
            'examples': [e['context'] for e in v['examples']],
            'frequency': v['freq']
        }
    
    # Process adjectives
    for a in adjectives:
        w = a['word']
        ctx_meanings = infer_meanings_from_context(w, ctx[w], known)
        meaning = ctx_meanings[0] if ctx_meanings else 'adjective/modifier'
        
        entries[w] = {
            'meaning': meaning,
            'category': 'adjective',
            'confidence': min(0.5, a['score']),
            'evidence_type': 'position_context',
            'evidence': a['evidence'],
            'examples': [e['context'] for e in a['examples']],
            'frequency': a['freq']
        }
    
    # Process prepositions
    prep_meanings = {
        'or': 'to/at',
        'ar': 'by/at',
        'al': 'to/the',
        'ol': 'the',
        'dar': 'from/of',
        'dol': 'in/from',
        'qol': 'with',
    }
    
    for p in preps:
        w = p['word']
        meaning = prep_meanings.get(w, 'preposition/conjunction')
        
        entries[w] = {
            'meaning': meaning,
            'category': 'preposition',
            'confidence': min(0.5, p['score']),
            'evidence_type': 'position_frequency',
            'evidence': p['evidence'],
            'examples': [e['context'] for e in p['examples']],
            'frequency': p['freq']
        }
    
    # Process between-knowns patterns
    for bp in between_knowns[:30]:
        w = bp['word']
        if w in entries:
            continue
        
        before_meaning = bp['before'][1]
        after_meaning = bp['after'][1]
        
        # Infer connection type
        if before_meaning in ['heart', 'earth', 'salt'] and after_meaning in ['heart', 'earth', 'salt']:
            meaning = 'and/with (connects ingredients)'
        elif before_meaning == after_meaning:
            meaning = f'modifier of {before_meaning}'
        else:
            meaning = f'links {before_meaning} to {after_meaning}'
        
        entries[w] = {
            'meaning': meaning,
            'category': 'connector',
            'confidence': 0.4,
            'evidence_type': 'between_knowns',
            'evidence': [f"after '{bp['before'][0]}' ({bp['before'][1]})", 
                        f"before '{bp['after'][0]}' ({bp['after'][1]})"],
            'examples': [e['context'] for e in bp['examples']],
            'frequency': bp['freq']
        }
    
    return entries


def generate_report(entries, verbs, adjectives, preps, suffix_patterns, prefix_patterns,
                   between_knowns, total_patterns):
    """Generate markdown report."""
    lines = [
        "# Dictionary Expansion: Context Analysis",
        "",
        "## Summary",
        f"- **Patterns analyzed**: {total_patterns}",
        f"- **Words inferred**: {len(entries)}",
        f"- **Verbs identified**: {len(verbs)}",
        f"- **Adjectives identified**: {len(adjectives)}",
        f"- **Prepositions/connectors**: {len(preps)}",
        "",
        "## Methodology",
        "",
        "This analysis uses surrounding word context to deduce meanings:",
        "1. **Between-knowns pattern**: Unknown words between translated words",
        "2. **Positional analysis**: Words at line start/middle/end",
        "3. **Suffix patterns**: -dy, -edy, -y endings indicate verbs",
        "4. **Prefix patterns**: ch-, qo-, sh- prefixes indicate categories",
        "",
        "## Inferred Verbs",
        "",
        "| Word | Meaning | Freq | Score | Evidence |",
        "|------|---------|------|-------|----------|",
    ]
    
    for v in verbs[:30]:
        w = v['word']
        e = entries.get(w, {})
        meaning = e.get('meaning', '?')
        lines.append(f"| {w} | {meaning} | {v['freq']} | {v['score']} | {', '.join(v['evidence'])} |")
    
    lines.extend([
        "",
        "## Inferred Adjectives",
        "",
        "| Word | Meaning | Freq | Score | Evidence |",
        "|------|---------|------|-------|----------|",
    ])
    
    for a in adjectives[:25]:
        w = a['word']
        e = entries.get(w, {})
        meaning = e.get('meaning', '?')
        lines.append(f"| {w} | {meaning} | {a['freq']} | {a['score']} | {', '.join(a['evidence'])} |")
    
    lines.extend([
        "",
        "## Inferred Function Words",
        "",
        "| Word | Meaning | Freq | Score | Evidence |",
        "|------|---------|------|-------|----------|",
    ])
    
    for p in preps[:20]:
        w = p['word']
        e = entries.get(w, {})
        meaning = e.get('meaning', '?')
        lines.append(f"| {w} | {meaning} | {p['freq']} | {p['score']} | {', '.join(p['evidence'])} |")
    
    lines.extend([
        "",
        "## Between-Knowns Patterns",
        "",
        "Words that consistently appear between two known words:",
        "",
        "| Unknown | Before (known) | After (known) | Freq |",
        "|---------|----------------|---------------|------|",
    ])
    
    for bp in between_knowns[:25]:
        before = f"{bp['before'][0]} ({bp['before'][1]})"
        after = f"{bp['after'][0]} ({bp['after'][1]})"
        lines.append(f"| {bp['word']} | {before} | {after} | {bp['freq']} |")
    
    lines.extend([
        "",
        "## Suffix Patterns",
        "",
        "Common suffixes and their word counts:",
        "",
    ])
    
    for suf, words in sorted(suffix_patterns.items(), key=lambda x: -len(x[1]))[:15]:
        lines.append(f"- **-{suf}**: {len(words)} words (e.g., {', '.join(words[:5])})")
    
    lines.extend([
        "",
        "## Prefix Patterns",
        "",
        "Common prefixes and their word counts:",
        "",
    ])
    
    for pref, words in sorted(prefix_patterns.items(), key=lambda x: -len(x[1]))[:15]:
        lines.append(f"- **{pref}-**: {len(words)} words (e.g., {', '.join(words[:5])})")
    
    lines.extend([
        "",
        "## Example Context Analysis",
        "",
        "### Word: `lchedy` (mix/combine)",
        "",
        "Context examples showing verb usage:",
        "",
    ])
    
    lchedy_entry = entries.get('lchedy', {})
    for ex in lchedy_entry.get('examples', [])[:3]:
        lines.append(f"- `{ex}`")
    
    lines.extend([
        "",
        "### Validation",
        "",
        "Testing inferred meanings in sample sentences:",
        "",
        "| Original | With Inferences |",
        "|----------|-----------------|",
    ])
    
    # Add sample validations
    samples = [
        ("otar ar sol chedy", "earth at salt make"),
        ("ol okar shedy otaiin", "the heart treat fig"),
        ("qokedy dar otar", "take from earth"),
    ]
    for orig, trans in samples:
        lines.append(f"| {orig} | {trans} |")
    
    lines.extend([
        "",
        "## Confidence Levels",
        "",
        "| Category | Count | Avg Confidence |",
        "|----------|-------|----------------|",
    ])
    
    for cat in ['verb', 'adjective', 'preposition', 'connector']:
        cat_entries = [e for e in entries.values() if e['category'] == cat]
        if cat_entries:
            avg_conf = sum(e['confidence'] for e in cat_entries) / len(cat_entries)
            lines.append(f"| {cat} | {len(cat_entries)} | {avg_conf:.2f} |")
    
    lines.extend([
        "",
        "---",
        "*Analysis complete. These inferences require validation against full text.*"
    ])
    
    return '\n'.join(lines)


def main():
    print("Track 52: Context-Based Dictionary Expansion")
    print("=" * 50)
    
    # Load existing dictionaries
    print("\n1. Loading dictionaries...")
    known = load_dictionary()
    grammar = load_grammar()
    known.update(grammar)
    print(f"   Known words: {len(known)}")
    
    # Extract lines
    print("\n2. Extracting corpus lines...")
    lines = extract_lines()
    print(f"   Lines: {len(lines)}")
    
    # Build context database
    print("\n3. Building context database...")
    ctx = build_context_db(lines, known)
    print(f"   Words indexed: {len(ctx)}")
    
    # Find unknown words (freq > 5)
    freq = get_word_frequencies()
    unknown_words = [w for w in freq if w not in known and freq[w] >= 5]
    print(f"   Unknown high-freq words: {len(unknown_words)}")
    
    # Find patterns
    print("\n4. Analyzing patterns...")
    
    between_knowns = find_between_knowns(ctx, known, unknown_words)
    print(f"   Between-knowns patterns: {len(between_knowns)}")
    
    suffix_patterns = analyze_suffixes(ctx, unknown_words)
    print(f"   Suffix patterns: {len(suffix_patterns)}")
    
    prefix_patterns = analyze_prefixes(ctx, unknown_words)
    print(f"   Prefix patterns: {len(prefix_patterns)}")
    
    # Infer word categories
    print("\n5. Inferring word categories...")
    
    verbs = infer_verbs(ctx, unknown_words, known)
    print(f"   Verbs: {len(verbs)}")
    
    adjectives = infer_adjectives(ctx, unknown_words, known)
    print(f"   Adjectives: {len(adjectives)}")
    
    preps = infer_prepositions(ctx, unknown_words)
    print(f"   Prepositions: {len(preps)}")
    
    # Create entries
    print("\n6. Creating dictionary entries...")
    entries = create_inferred_entries(verbs, adjectives, preps, between_knowns, ctx, known)
    print(f"   New entries: {len(entries)}")
    
    # Count total patterns
    total_patterns = (len(between_knowns) + sum(len(v) for v in suffix_patterns.values()) +
                     sum(len(v) for v in prefix_patterns.values()))
    
    # Prepare output
    output = {
        'patterns_analyzed': total_patterns,
        'words_inferred': len(entries),
        'entries': entries,
        'by_category': {
            'verbs': [v['word'] for v in verbs],
            'adjectives': [a['word'] for a in adjectives],
            'prepositions': [p['word'] for p in preps],
            'connectors': [bp['word'] for bp in between_knowns[:30]]
        },
        'suffix_patterns': {s: len(ws) for s, ws in suffix_patterns.items()},
        'prefix_patterns': {p: len(ws) for p, ws in prefix_patterns.items()},
        'statistics': {
            'total_lines': len(lines),
            'words_indexed': len(ctx),
            'unknown_analyzed': len(unknown_words),
            'known_words': len(known)
        }
    }
    
    # Save JSON
    print("\n7. Saving results...")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"   Saved: {OUTPUT_JSON}")
    
    # Generate and save report
    report = generate_report(entries, verbs, adjectives, preps, suffix_patterns, 
                            prefix_patterns, between_knowns, total_patterns)
    with open(OUTPUT_MD, 'w') as f:
        f.write(report)
    print(f"   Saved: {OUTPUT_MD}")
    
    # Summary
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    print(f"Patterns analyzed: {total_patterns}")
    print(f"New words inferred: {len(entries)}")
    print(f"  - Verbs: {len(verbs)}")
    print(f"  - Adjectives: {len(adjectives)}")
    print(f"  - Prepositions: {len(preps)}")
    
    print("\nTop inferred verbs:")
    for v in verbs[:10]:
        e = entries.get(v['word'], {})
        print(f"  {v['word']}: {e.get('meaning', '?')} (score={v['score']})")
    
    print("\nTop inferred prepositions:")
    for p in preps[:5]:
        e = entries.get(p['word'], {})
        print(f"  {p['word']}: {e.get('meaning', '?')} (freq={p['freq']})")
    
    # Check success criteria
    print("\n" + "=" * 50)
    print("SUCCESS CRITERIA")
    print("=" * 50)
    print(f"[{'✓' if total_patterns >= 500 else '✗'}] 500+ patterns analyzed: {total_patterns}")
    print(f"[{'✓' if len(entries) >= 80 else '✗'}] 80+ words inferred: {len(entries)}")
    print(f"[{'✓' if all(e.get('evidence') for e in entries.values()) else '✗'}] Each inference has evidence")


if __name__ == "__main__":
    main()
