"""
Zodiac Key Derivation - Known plaintext attack on Voynich month labels.
Uses known month names (Martius, Aprilis, etc.) to derive the phonetic key.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

EVA_FILE = Path("data/eva_ivtff.txt")
RESULTS_DIR = Path("results")

ZODIAC_MONTHS = {
    'pisces': {'month': 'martius', 'alt': ['march', 'marzius', 'marcius']},
    'aries': {'month': 'aprilis', 'alt': ['april', 'aprile']},
    'taurus': {'month': 'maius', 'alt': ['may', 'maio']},
    'gemini': {'month': 'iunius', 'alt': ['june', 'junius', 'iunio']},
    'cancer': {'month': 'iulius', 'alt': ['july', 'julius', 'iulio']},
    'leo': {'month': 'augustus', 'alt': ['august', 'augusto']},
    'virgo': {'month': 'september', 'alt': ['septembris']},
    'libra': {'month': 'october', 'alt': ['octobris', 'octobre']},
    'scorpio': {'month': 'november', 'alt': ['novembris', 'novembre']},
    'sagittarius': {'month': 'december', 'alt': ['decembris', 'decembre']}
}

ZODIAC_FOLIOS = {
    'f70v2': 'pisces',
    'f70v1': 'aries',
    'f71r': 'aries',
    'f71v': 'taurus',
    'f72r1': 'taurus',
    'f72r2': 'gemini',
    'f72r3': 'cancer',
    'f72v3': 'leo',
    'f72v2': 'virgo',
    'f72v1': 'libra',
    'f73r': 'scorpio',
    'f73v': 'sagittarius'
}

KNOWN_PHONETIC_MAP = {
    'o': 'a', 'h': 'r', '9': 's', 'k': 'n', 'c': 'c', '7': 'l', 'm': 'm',
    'a': 'e', 'e': 'i', '8': 'd', '1': 't', '4': 'qu', 'y': 'i', '2': 'b',
    'C': 'ch', 's': 'x', 'n': 'n', 'p': 'p', 'g': 'g', 'j': 'i', 'W': 'u',
    'H': 'h', 'z': 'z', 'u': 'u', 'f': 'f', 'A': 'a', 'd': 'v', 'J': 'i',
    'Z': 'z', 'K': 'c', 'i': 'i', 'S': 's', 't': 't', 'b': 'b', 'l': 'l'
}


def load_zodiac_labels():
    """Extract labels from zodiac folios."""
    labels = defaultdict(list)
    raw = EVA_FILE.read_text(encoding='utf-8')
    
    for line in raw.split('\n'):
        if not line.startswith('<f7'):
            continue
        
        m = re.match(r'<([^;]+);H>\s*(.+)', line)
        if not m:
            continue
        
        loc, text = m.groups()
        folio_base = loc.split('.')[0]
        
        for folio_key, zodiac in ZODIAC_FOLIOS.items():
            if loc.startswith(folio_key):
                is_label = '@Lz' in loc or '&Lz' in loc
                if is_label:
                    text_clean = re.sub(r'[!?<>].*?[>]|[!?]', '', text).strip()
                    words = [w for w in re.split(r'[.\s]', text_clean) if w]
                    for word in words:
                        labels[folio_key].append({
                            'word': word,
                            'zodiac': zodiac,
                            'loc': loc
                        })
                break
    
    return dict(labels)


def derive_char_mapping(voynich_word, latin_word):
    """
    Attempt to derive character mappings from a Voynich-Latin pair.
    Returns list of derived mappings with positions.
    """
    derivations = []
    v_len = len(voynich_word)
    l_len = len(latin_word)
    
    if abs(v_len - l_len) > 3:
        return derivations
    
    for i, v_char in enumerate(voynich_word):
        if i < l_len:
            l_char = latin_word[i]
            derivations.append({
                'voynich': v_char,
                'latin': l_char,
                'position': i,
                'voynich_word': voynich_word,
                'latin_word': latin_word
            })
    
    return derivations


def align_and_score(voynich_word, target_word):
    """Score alignment between Voynich word and target."""
    decoded = decode_word(voynich_word, KNOWN_PHONETIC_MAP)
    
    v_len = len(decoded)
    t_len = len(target_word)
    
    if v_len == 0 or t_len == 0:
        return 0.0, decoded
    
    matches = sum(1 for i, c in enumerate(decoded) if i < t_len and c == target_word[i])
    score = matches / max(v_len, t_len)
    
    prefix_match = 0
    for i in range(min(v_len, t_len)):
        if decoded[i] == target_word[i]:
            prefix_match += 1
        else:
            break
    score += prefix_match * 0.1
    
    common = set(decoded) & set(target_word)
    score += len(common) * 0.05
    
    return min(score, 1.0), decoded


def decode_word(word, phonetic_map):
    """Decode a Voynich word using phonetic map."""
    result = []
    for char in word:
        if char in phonetic_map:
            result.append(phonetic_map[char])
        else:
            pass
    return ''.join(result)


def find_best_month_candidates(labels):
    """Find labels that best match expected month names."""
    candidates = []
    
    for folio, label_list in labels.items():
        if folio not in ZODIAC_FOLIOS:
            continue
        
        zodiac = ZODIAC_FOLIOS[folio]
        month_info = ZODIAC_MONTHS.get(zodiac, {})
        expected_month = month_info.get('month', '')
        alt_months = month_info.get('alt', [])
        all_targets = [expected_month] + alt_months
        
        for label in label_list:
            word = label['word']
            best_score = 0
            best_target = ''
            best_decoded = ''
            
            for target in all_targets:
                if not target:
                    continue
                score, decoded = align_and_score(word, target)
                if score > best_score:
                    best_score = score
                    best_target = target
                    best_decoded = decoded
            
            if best_score > 0.3:
                candidates.append({
                    'folio': folio,
                    'zodiac': zodiac,
                    'voynich': word,
                    'decoded': best_decoded,
                    'expected': best_target,
                    'score': round(best_score, 3),
                    'length_diff': abs(len(word) - len(best_target))
                })
    
    return sorted(candidates, key=lambda x: -x['score'])


def derive_key_from_candidates(candidates, min_score=0.5):
    """Derive character mappings from best candidates."""
    char_derivations = defaultdict(list)
    
    high_score = [c for c in candidates if c['score'] >= min_score]
    
    for cand in high_score:
        voynich = cand['voynich']
        expected = cand['expected']
        
        min_len = min(len(voynich), len(expected))
        
        for i in range(min_len):
            v_char = voynich[i]
            l_char = expected[i]
            
            char_derivations[v_char].append({
                'latin': l_char,
                'source_word': voynich,
                'target_word': expected,
                'position': i,
                'score': cand['score']
            })
    
    return dict(char_derivations)


def build_consensus_key(char_derivations):
    """Build a consensus key from derived mappings."""
    derived_key = {}
    conflicts = []
    
    for v_char, mappings in char_derivations.items():
        latin_counts = defaultdict(list)
        for m in mappings:
            latin_counts[m['latin']].append(m)
        
        if len(latin_counts) == 1:
            best_latin = list(latin_counts.keys())[0]
            derived_key[v_char] = {
                'latin': best_latin,
                'confidence': 1.0,
                'occurrences': len(mappings),
                'sources': list(set(m['source_word'] for m in mappings))
            }
        else:
            sorted_options = sorted(latin_counts.items(), key=lambda x: -len(x[1]))
            best_latin, best_mappings = sorted_options[0]
            total = len(mappings)
            conf = len(best_mappings) / total
            
            derived_key[v_char] = {
                'latin': best_latin,
                'confidence': round(conf, 2),
                'occurrences': len(best_mappings),
                'sources': list(set(m['source_word'] for m in best_mappings))
            }
            
            conflicts.append({
                'char': v_char,
                'values': {k: len(v) for k, v in latin_counts.items()},
                'contexts': [m['source_word'] for m in mappings[:5]]
            })
    
    return derived_key, conflicts


def validate_derived_key(derived_key, candidates):
    """Test derived key against candidates."""
    test_key = {k: v['latin'] for k, v in derived_key.items()}
    
    full_key = {**KNOWN_PHONETIC_MAP}
    for k, v in test_key.items():
        full_key[k] = v
    
    results = []
    for cand in candidates[:20]:
        voynich = cand['voynich']
        expected = cand['expected']
        
        decoded_old = decode_word(voynich, KNOWN_PHONETIC_MAP)
        decoded_new = decode_word(voynich, full_key)
        
        old_score, _ = align_and_score(voynich, expected)
        
        new_matches = sum(1 for i, c in enumerate(decoded_new) 
                        if i < len(expected) and c == expected[i])
        new_score = new_matches / max(len(decoded_new), len(expected)) if decoded_new else 0
        
        results.append({
            'voynich': voynich,
            'expected': expected,
            'old_decoded': decoded_old,
            'new_decoded': decoded_new,
            'old_score': round(old_score, 3),
            'new_score': round(new_score, 3),
            'improvement': round(new_score - old_score, 3)
        })
    
    return results


def test_on_plant_labels():
    """Test derived key on plant labels from herbal section."""
    raw = EVA_FILE.read_text(encoding='utf-8')
    plant_words = []
    
    for line in raw.split('\n'):
        if not line.startswith('<f'):
            continue
        m = re.match(r'<(f[1-9]|f1[0-9]|f2[0-5])[rv][^;]*;H>\s*(.+)', line)
        if m:
            loc, text = m.groups()
            text_clean = re.sub(r'[!?<>].*?[>]|[!?]', '', text)
            words = [w for w in re.split(r'[.\s\-=,]', text_clean) if w and len(w) > 3]
            plant_words.extend(words[:3])
    
    return list(set(plant_words))[:50]


def main():
    print("=" * 60)
    print("ZODIAC KEY DERIVATION - Known Plaintext Attack")
    print("=" * 60)
    
    print("\n1. Extracting zodiac labels...")
    labels = load_zodiac_labels()
    total_labels = sum(len(v) for v in labels.values())
    print(f"   Found {total_labels} labels across {len(labels)} folios")
    
    for folio in sorted(labels.keys()):
        zodiac = ZODIAC_FOLIOS.get(folio, 'unknown')
        print(f"   {folio}: {len(labels[folio])} labels ({zodiac})")
    
    print("\n2. Finding month name candidates...")
    candidates = find_best_month_candidates(labels)
    print(f"   Found {len(candidates)} potential month labels")
    
    print("\n   Top 15 candidates:")
    for c in candidates[:15]:
        print(f"   {c['voynich']:15} -> {c['expected']:12} "
              f"(decoded: {c['decoded']:12}) score: {c['score']:.3f}")
    
    print("\n3. Deriving character mappings...")
    char_derivations = derive_key_from_candidates(candidates, min_score=0.4)
    print(f"   Derived mappings for {len(char_derivations)} characters")
    
    print("\n4. Building consensus key...")
    derived_key, conflicts = build_consensus_key(char_derivations)
    
    print("\n   DERIVED MAPPINGS:")
    print("   " + "-" * 50)
    for v_char in sorted(derived_key.keys()):
        info = derived_key[v_char]
        known = KNOWN_PHONETIC_MAP.get(v_char, '?')
        match = "✓" if info['latin'] == known else "≠"
        print(f"   {v_char} -> {info['latin']} "
              f"(conf: {info['confidence']:.2f}, n={info['occurrences']}) "
              f"[known: {known}] {match}")
    
    if conflicts:
        print("\n   CONFLICTS:")
        for conf in conflicts[:10]:
            print(f"   {conf['char']}: {conf['values']}")
    
    print("\n5. Validating derived key...")
    validation = validate_derived_key(derived_key, candidates)
    
    print("\n   VALIDATION RESULTS:")
    print("   " + "-" * 70)
    improvements = 0
    for v in validation[:15]:
        change = "+" if v['improvement'] > 0 else ""
        if v['improvement'] > 0:
            improvements += 1
        print(f"   {v['voynich']:12} -> {v['expected']:12} "
              f"old:{v['old_decoded']:10} new:{v['new_decoded']:10} "
              f"({change}{v['improvement']:.2f})")
    
    avg_improvement = sum(v['improvement'] for v in validation) / len(validation) if validation else 0
    print(f"\n   Average improvement: {avg_improvement:.3f}")
    print(f"   Labels improved: {improvements}/{len(validation)}")
    
    print("\n6. Testing on botanical section...")
    plant_words = test_on_plant_labels()
    full_key = {**KNOWN_PHONETIC_MAP}
    for k, v in derived_key.items():
        full_key[k] = v['latin']
    
    print(f"\n   Sample plant word decodings with derived key:")
    for word in plant_words[:10]:
        decoded = decode_word(word, full_key)
        print(f"   {word:15} -> {decoded}")
    
    results = {
        'labels_extracted': [
            {'folio': f, 'labels': [l['word'] for l in labs], 
             'zodiac': ZODIAC_FOLIOS.get(f, 'unknown'),
             'expected_month': ZODIAC_MONTHS.get(ZODIAC_FOLIOS.get(f, ''), {}).get('month', '')}
            for f, labs in labels.items()
        ],
        'month_candidates': candidates[:30],
        'character_derivations': [
            {'voynich': k, 'derived_latin': v['latin'], 
             'confidence': v['confidence'], 'occurrences': v['occurrences']}
            for k, v in derived_key.items()
        ],
        'derived_key': {k: v['latin'] for k, v in derived_key.items()},
        'key_confidence': round(sum(v['confidence'] for v in derived_key.values()) / 
                               len(derived_key) if derived_key else 0, 3),
        'conflicts': conflicts,
        'validation_results': {
            'average_improvement': round(avg_improvement, 3),
            'samples': validation[:20]
        },
        'comparison_with_known': [
            {'char': k, 'derived': derived_key[k]['latin'], 
             'known': KNOWN_PHONETIC_MAP.get(k, '?'),
             'match': derived_key[k]['latin'] == KNOWN_PHONETIC_MAP.get(k, '')}
            for k in derived_key.keys()
        ]
    }
    
    RESULTS_DIR.mkdir(exist_ok=True)
    
    with open(RESULTS_DIR / "zodiac_key_derivation.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    report = generate_report(results, derived_key, conflicts, validation, candidates)
    with open(RESULTS_DIR / "zodiac_key_report.md", 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print("Results saved to:")
    print("  - results/zodiac_key_derivation.json")
    print("  - results/zodiac_key_report.md")
    print("=" * 60)


def generate_report(results, derived_key, conflicts, validation, candidates):
    """Generate markdown report."""
    lines = [
        "# Zodiac Key Derivation Report",
        "",
        "## Overview",
        "This analysis attempts to derive the Voynich phonetic key using",
        "a \"known plaintext attack\" - we know the zodiac sections should",
        "contain month names (Martius, Aprilis, etc.).",
        "",
        "## Labels Extracted",
        f"Total labels found: {sum(len(l['labels']) for l in results['labels_extracted'])}",
        "",
        "| Folio | Zodiac | Expected Month | Labels |",
        "|-------|--------|----------------|--------|"
    ]
    
    for entry in results['labels_extracted']:
        labels_str = ', '.join(entry['labels'][:5])
        if len(entry['labels']) > 5:
            labels_str += f"... (+{len(entry['labels'])-5})"
        lines.append(f"| {entry['folio']} | {entry['zodiac']} | "
                    f"{entry['expected_month']} | {labels_str} |")
    
    lines.extend([
        "",
        "## Top Month Name Candidates",
        "",
        "| Voynich | Decoded | Expected | Score |",
        "|---------|---------|----------|-------|"
    ])
    
    for c in candidates[:20]:
        lines.append(f"| {c['voynich']} | {c['decoded']} | "
                    f"{c['expected']} | {c['score']:.3f} |")
    
    lines.extend([
        "",
        "## Derived Character Mappings",
        "",
        "| Voynich | Derived | Known | Match | Confidence |",
        "|---------|---------|-------|-------|------------|"
    ])
    
    for k in sorted(derived_key.keys()):
        v = derived_key[k]
        known = KNOWN_PHONETIC_MAP.get(k, '?')
        match = "✓" if v['latin'] == known else "✗"
        lines.append(f"| {k} | {v['latin']} | {known} | {match} | {v['confidence']:.2f} |")
    
    if conflicts:
        lines.extend([
            "",
            "## Conflicts Found",
            ""
        ])
        for conf in conflicts:
            lines.append(f"- **{conf['char']}**: {conf['values']}")
    
    lines.extend([
        "",
        "## Validation Results",
        f"",
        f"Average improvement: {results['validation_results']['average_improvement']:.3f}",
        "",
        "| Voynich | Expected | Old | New | Change |",
        "|---------|----------|-----|-----|--------|"
    ])
    
    for v in validation[:15]:
        change = f"+{v['improvement']:.2f}" if v['improvement'] > 0 else f"{v['improvement']:.2f}"
        lines.append(f"| {v['voynich']} | {v['expected']} | "
                    f"{v['old_decoded']} | {v['new_decoded']} | {change} |")
    
    matching = sum(1 for c in results['comparison_with_known'] if c['match'])
    total = len(results['comparison_with_known'])
    
    lines.extend([
        "",
        "## Summary",
        "",
        f"- Characters derived: {len(derived_key)}",
        f"- Matching known key: {matching}/{total} ({100*matching/total:.1f}%)" if total else "- No derivations",
        f"- Key confidence: {results['key_confidence']:.3f}",
        f"- Conflicts: {len(conflicts)}",
        "",
        "## Conclusion",
        ""
    ])
    
    if matching > total * 0.6:
        lines.append("The derived key shows **strong agreement** with the known phonetic map,")
        lines.append("validating the approach. The zodiac month labels appear to be ")
        lines.append("readable as Latin month names with the existing key.")
    elif matching > total * 0.4:
        lines.append("The derived key shows **partial agreement** with the known map.")
        lines.append("Some refinements to the phonetic mapping may be needed.")
    else:
        lines.append("The derived key shows **significant divergence** from the known map.")
        lines.append("This could indicate: (a) the labels aren't month names, ")
        lines.append("(b) different orthography/language, or (c) transcription issues.")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    main()
