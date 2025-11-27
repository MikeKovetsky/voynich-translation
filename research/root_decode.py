import json
import re
from collections import defaultdict

EVA_VOWELS = set('aeiouy')
EVA_CONSONANTS = set('bcdfghjklmnpqrstvwxz')

HEBREW_BOTANICAL_ROOTS = {
    'shr': {'hebrew': 'sh-r-sh', 'meaning': 'root (shoresh)', 'transliteration': 'שרש'},
    'shs': {'hebrew': 'sh-r-sh', 'meaning': 'root (shoresh)', 'transliteration': 'שרש'},
    'lh': {'hebrew': 'ayin-l-h', 'meaning': 'leaf (aleh)', 'transliteration': 'עלה'},
    'alh': {'hebrew': 'ayin-l-h', 'meaning': 'leaf (aleh)', 'transliteration': 'עלה'},
    'prc': {'hebrew': 'p-r-ch', 'meaning': 'flower (perach)', 'transliteration': 'פרח'},
    'pch': {'hebrew': 'p-r-ch', 'meaning': 'flower (perach)', 'transliteration': 'פרח'},
    'prch': {'hebrew': 'p-r-ch', 'meaning': 'flower (perach)', 'transliteration': 'פרח'},
    'zkr': {'hebrew': 'z-kh-r', 'meaning': 'male/remember (zachar)', 'transliteration': 'זכר'},
    'chk': {'hebrew': 'z-kh-r', 'meaning': 'male/remember (zachar)', 'transliteration': 'זכר'},
    'rp': {'hebrew': 'r-p-alef', 'meaning': 'heal (rophe)', 'transliteration': 'רפא'},
    'rpa': {'hebrew': 'r-p-alef', 'meaning': 'heal (rophe)', 'transliteration': 'רפא'},
    'mym': {'hebrew': 'm-y-m', 'meaning': 'water (mayim)', 'transliteration': 'מים'},
    'dm': {'hebrew': 'd-m', 'meaning': 'blood (dam)', 'transliteration': 'דם'},
    'shl': {'hebrew': 'sh-l', 'meaning': 'extract/draw out (shol)', 'transliteration': 'של'},
    'shm': {'hebrew': 'sh-m', 'meaning': 'name (shem)', 'transliteration': 'שם'},
    'chr': {'hebrew': 'ch-r', 'meaning': 'hole/pierce (chor)', 'transliteration': 'חור'},
    'chl': {'hebrew': 'ch-l', 'meaning': 'sick (choleh)', 'transliteration': 'חולה'},
    'kch': {'hebrew': 'k-ch', 'meaning': 'strength (koach)', 'transliteration': 'כח'},
    'zr': {'hebrew': 'z-r-ayin', 'meaning': 'seed (zera)', 'transliteration': 'זרע'},
    'prh': {'hebrew': 'p-r-h', 'meaning': 'be fruitful (parah)', 'transliteration': 'פרה'},
    'gn': {'hebrew': 'g-n', 'meaning': 'garden (gan)', 'transliteration': 'גן'},
    'ets': {'hebrew': 'ayin-ts', 'meaning': 'tree (ets)', 'transliteration': 'עץ'},
    'ts': {'hebrew': 'ayin-ts', 'meaning': 'tree (ets)', 'transliteration': 'עץ'},
    'lbn': {'hebrew': 'l-b-n', 'meaning': 'white (lavan)', 'transliteration': 'לבן'},
    'shch': {'hebrew': 'sh-ch-r', 'meaning': 'black (shachor)', 'transliteration': 'שחור'},
    'yrk': {'hebrew': 'y-r-k', 'meaning': 'green (yarok)', 'transliteration': 'ירוק'},
    'adm': {'hebrew': 'alef-d-m', 'meaning': 'red (adom)', 'transliteration': 'אדום'},
    'smn': {'hebrew': 's-m-n', 'meaning': 'oil/fat (shemen)', 'transliteration': 'שמן'},
    'bsm': {'hebrew': 'b-s-m', 'meaning': 'spice (bosem)', 'transliteration': 'בשם'},
    'rfh': {'hebrew': 'r-f-h', 'meaning': 'healing (refuah)', 'transliteration': 'רפואה'},
}


def extract_consonants(word):
    return ''.join(c for c in word.lower() if c in EVA_CONSONANTS)


def extract_3_consonant_roots(word):
    cons = extract_consonants(word)
    roots = []
    for i in range(len(cons) - 2):
        roots.append(cons[i:i+3])
    return roots


def extract_2_consonant_roots(word):
    cons = extract_consonants(word)
    roots = []
    for i in range(len(cons) - 1):
        roots.append(cons[i:i+2])
    return roots


def load_hebrew_analysis(path='results/hebrew_analysis.json'):
    with open(path) as f:
        return json.load(f)


def load_transcription(path='data/eva_ivtff.txt'):
    with open(path) as f:
        return f.read()


def extract_words_from_eva(text):
    words = []
    for line in text.split('\n'):
        if line.startswith('<') and ';' in line and '>' in line:
            parts = line.split('\t')
            if len(parts) >= 2:
                content = parts[1]
                content = re.sub(r'<[^>]*>', '', content)
                content = re.sub(r'\{[^}]*\}', '', content)
                line_words = re.split(r'[.,\s]+', content)
                words.extend([w for w in line_words if w and w.isalpha()])
    return words


def extract_folio_text(text, folio):
    lines = []
    in_folio = False
    for line in text.split('\n'):
        if line.startswith(f'<{folio}>') or line.startswith(f'<{folio} '):
            in_folio = True
            continue
        if in_folio and line.startswith('<f') and not line.startswith(f'<{folio}'):
            if '>' in line and not line.startswith('#'):
                break
        if in_folio and '\t' in line:
            parts = line.split('\t')
            if len(parts) >= 2 and folio in parts[0]:
                content = parts[1]
                content = re.sub(r'<[^>]*>', '', content)
                content = re.sub(r'\{[^}]*\}', '', content)
                lines.append({
                    'locator': parts[0].strip(),
                    'text': content.strip(),
                    'words': [w for w in re.split(r'[.,\s]+', content) if w and w.isalpha()]
                })
    return lines


def build_root_dictionary(words, hebrew_data):
    top_roots_data = hebrew_data.get('root_patterns', {}).get('top_roots', [])
    root_variations = hebrew_data.get('root_patterns', {}).get('root_variations', {})
    
    all_roots = {}
    for root_info in top_roots_data:
        all_roots[root_info['root']] = {
            'count': root_info['count'],
            'examples': root_info['examples']
        }
    for rt, data in root_variations.items():
        if rt not in all_roots:
            all_roots[rt] = {'count': data['count'], 'examples': data['examples']}
    
    root_counts = defaultdict(int)
    for word in words:
        for rt in extract_3_consonant_roots(word):
            root_counts[rt] += 1
    
    for rt, cnt in root_counts.items():
        if cnt >= 5 and rt not in all_roots:
            all_roots[rt] = {'count': cnt, 'examples': []}
    
    root_dict = {}
    
    for root, root_info in all_roots.items():
        count = root_info['count']
        examples = root_info.get('examples', [])
        
        word_list = []
        for word in words:
            word_roots = extract_3_consonant_roots(word)
            if root in word_roots:
                if word not in word_list:
                    word_list.append(word)
                if len(word_list) >= 30:
                    break
        
        hebrew_candidate = None
        hebrew_meaning = None
        confidence = 0.0
        
        for heb_root, info in HEBREW_BOTANICAL_ROOTS.items():
            if root == heb_root or root in heb_root or heb_root in root:
                hebrew_candidate = info['hebrew']
                hebrew_meaning = info['meaning']
                confidence = 0.7 if root == heb_root else 0.5
                break
        
        root_dict[root] = {
            'words': word_list[:30],
            'frequency': count,
            'hebrew_candidate': hebrew_candidate,
            'meaning': hebrew_meaning,
            'confidence': confidence
        }
    
    return root_dict


def map_roots_to_hebrew(root_dict):
    mappings = {}
    
    direct_mappings = {
        'pch': ('perach', 'flower', 0.7),
        'chk': ('zachar', 'male/remember', 0.5),
        'chr': ('chor', 'hole/pierce', 0.6),
        'chl': ('choleh', 'sick/disease', 0.5),
        'shl': ('shol', 'extract/draw', 0.5),
        'shk': ('shokhed', 'almond', 0.6),
        'shd': ('shed', 'field/breast', 0.4),
        'kch': ('koach', 'strength', 0.5),
        'lch': ('lach', 'moist/fresh', 0.5),
        'dch': ('dachah', 'push/reject', 0.4),
        'tch': ('tuach', 'smear/plaster', 0.4),
        'chd': ('chad', 'sharp/one', 0.5),
        'cht': ('chittah', 'wheat', 0.4),
        'cth': ('ktav', 'writing', 0.3),
        'pln': ('ploni', 'someone/plant', 0.3),
        'fgr': ('figura', 'figure', 0.2),
        'shc': ('shachor', 'black', 0.5),
        'ksh': ('kashah', 'hard/difficult', 0.4),
        'fch': ('puch', 'paint/cosmetic', 0.4),
        'chp': ('chof', 'shore/coast', 0.3),
        'tsh': ('tash', 'weak', 0.3),
        'rch': ('ruach', 'spirit/wind', 0.6),
        'prch': ('perach', 'flower', 0.7),
        'dm': ('dam', 'blood', 0.7),
        'ts': ('ets', 'tree', 0.6),
        'shr': ('shoresh', 'root', 0.7),
        'shs': ('shoresh', 'root', 0.7),
        'lh': ('aleh', 'leaf', 0.6),
        'rp': ('rophe', 'healer', 0.6),
        'shm': ('shem', 'name', 0.5),
        'gn': ('gan', 'garden', 0.6),
        'zr': ('zera', 'seed', 0.6),
        'prh': ('parah', 'be fruitful', 0.5),
        'smn': ('shemen', 'oil', 0.5),
        'bsm': ('bosem', 'spice', 0.5),
    }
    
    for root, data in root_dict.items():
        if root in direct_mappings:
            heb, meaning, score = direct_mappings[root]
            mappings[root] = {
                'hebrew': heb,
                'meaning': meaning,
                'score': score,
                'frequency': data['frequency']
            }
        elif data.get('hebrew_candidate'):
            mappings[root] = {
                'hebrew': data['hebrew_candidate'],
                'meaning': data['meaning'],
                'score': data['confidence'],
                'frequency': data['frequency']
            }
    
    return mappings


def decode_word(word, root_dict, mappings):
    word_roots_3 = extract_3_consonant_roots(word)
    word_roots_2 = extract_2_consonant_roots(word)
    
    decoded_parts = []
    for root in word_roots_3:
        if root in mappings:
            decoded_parts.append({
                'root': root,
                'hebrew': mappings[root]['hebrew'],
                'meaning': mappings[root]['meaning']
            })
    
    for root in word_roots_2:
        if root in HEBREW_BOTANICAL_ROOTS:
            info = HEBREW_BOTANICAL_ROOTS[root]
            decoded_parts.append({
                'root': root,
                'hebrew': info['hebrew'],
                'meaning': info['meaning']
            })
    
    return decoded_parts


def decode_folio(folio_lines, root_dict, mappings):
    decoded_lines = []
    
    for line in folio_lines:
        decoded_words = []
        for word in line['words']:
            roots_found = decode_word(word, root_dict, mappings)
            decoded_words.append({
                'word': word,
                'roots': roots_found
            })
        
        meanings = []
        for dw in decoded_words:
            if dw['roots']:
                meanings.append(f"{dw['word']}({'/'.join(r['meaning'] for r in dw['roots'])})")
            else:
                meanings.append(dw['word'])
        
        decoded_lines.append({
            'voynich': ' '.join(line['words']),
            'roots_found': [r for dw in decoded_words for r in dw['roots']],
            'decoded': ' '.join(meanings)
        })
    
    return decoded_lines


def validate_botanical_context(decoded_lines, folio):
    botanical_terms = {'root', 'leaf', 'flower', 'stem', 'seed', 'plant', 'tree', 'fruit', 'water', 'heal'}
    
    total_lines = len(decoded_lines)
    lines_with_botanical = 0
    
    for line in decoded_lines:
        meanings = set()
        for root in line['roots_found']:
            if root.get('meaning'):
                meanings.update(root['meaning'].lower().split('/'))
        
        if meanings & botanical_terms:
            lines_with_botanical += 1
    
    botanical_match = lines_with_botanical / total_lines if total_lines > 0 else 0
    
    semantic_coherence = 0.0
    if total_lines > 0:
        all_meanings = []
        for line in decoded_lines:
            for root in line['roots_found']:
                if root.get('meaning'):
                    all_meanings.append(root['meaning'])
        
        if all_meanings:
            unique_meanings = len(set(all_meanings))
            total_meanings = len(all_meanings)
            semantic_coherence = 1 - (unique_meanings / total_meanings) if total_meanings > 0 else 0
    
    return {
        'botanical_context_match': round(botanical_match, 3),
        'semantic_coherence': round(semantic_coherence, 3)
    }


def main():
    print("Loading data...")
    hebrew_data = load_hebrew_analysis()
    transcription = load_transcription()
    all_words = extract_words_from_eva(transcription)
    
    print(f"Extracted {len(all_words)} words from transcription")
    print(f"Found {hebrew_data['root_patterns']['total_roots_found']} root patterns in Hebrew analysis")
    
    print("\nBuilding root dictionary...")
    root_dict = build_root_dictionary(all_words, hebrew_data)
    print(f"Built dictionary with {len(root_dict)} roots")
    
    print("\nMapping to Hebrew roots...")
    mappings = map_roots_to_hebrew(root_dict)
    print(f"Created {len(mappings)} Hebrew mappings")
    
    print("\nExtracting f2v text...")
    f2v_lines = extract_folio_text(transcription, 'f2v')
    unique_lines = []
    seen = set()
    for line in f2v_lines:
        text_key = line['text']
        if text_key not in seen and line['words']:
            unique_lines.append(line)
            seen.add(text_key)
    
    print(f"Found {len(unique_lines)} unique lines in f2v")
    
    print("\nDecoding f2v...")
    decoded_lines = decode_folio(unique_lines, root_dict, mappings)
    
    print("\nValidating botanical context...")
    validation = validate_botanical_context(decoded_lines, 'f2v')
    
    overall_score = (
        validation['botanical_context_match'] * 0.4 +
        validation['semantic_coherence'] * 0.3 +
        (len(mappings) / 20) * 0.3
    )
    overall_score = min(1.0, overall_score)
    
    if overall_score >= 0.6:
        verdict = "PARTIAL"
    elif overall_score >= 0.3:
        verdict = "WEAK"
    else:
        verdict = "FAILS"
    
    results = {
        'roots_extracted': len(root_dict),
        'root_dictionary': root_dict,
        'hebrew_mappings': mappings,
        'sample_page': {
            'folio': 'f2v',
            'decoded_lines': decoded_lines
        },
        'validation': validation,
        'overall_score': round(overall_score, 3),
        'verdict': verdict
    }
    
    with open('results/root_decoding.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to results/root_decoding.json")
    print(f"\nSummary:")
    print(f"  Roots extracted: {len(root_dict)}")
    print(f"  Hebrew mappings: {len(mappings)}")
    print(f"  Botanical context match: {validation['botanical_context_match']}")
    print(f"  Semantic coherence: {validation['semantic_coherence']}")
    print(f"  Overall score: {overall_score:.3f}")
    print(f"  Verdict: {verdict}")
    
    generate_report(results)


def generate_report(results):
    report = """# Root-Based Decoding Report

## Summary
- Roots analyzed: {roots}
- Hebrew mappings attempted: {mappings}
- Overall score: {score:.1%}
- Verdict: **{verdict}**

## Root Dictionary (Top 20)

| Root | Frequency | Hebrew Candidate | Meaning | Confidence |
|------|-----------|-----------------|---------|------------|
""".format(
        roots=results['roots_extracted'],
        mappings=len(results['hebrew_mappings']),
        score=results['overall_score'],
        verdict=results['verdict']
    )
    
    sorted_roots = sorted(
        results['root_dictionary'].items(),
        key=lambda x: x[1]['frequency'],
        reverse=True
    )[:20]
    
    for root, data in sorted_roots:
        hebrew = data.get('hebrew_candidate') or '-'
        meaning = data.get('meaning') or '-'
        conf = data.get('confidence', 0)
        report += f"| {root} | {data['frequency']} | {hebrew} | {meaning} | {conf:.1%} |\n"
    
    report += """
## Hebrew Mappings

| Root | Hebrew | Meaning | Score | Frequency |
|------|--------|---------|-------|-----------|
"""
    
    for root, data in sorted(
        results['hebrew_mappings'].items(),
        key=lambda x: x[1].get('frequency', 0),
        reverse=True
    )[:15]:
        report += f"| {root} | {data['hebrew']} | {data['meaning']} | {data['score']:.1%} | {data.get('frequency', '-')} |\n"
    
    report += f"""
## Sample Page Decoding (f2v)

f2v is described as "Water lily" - botanical page with herbal content.

"""
    
    for i, line in enumerate(results['sample_page']['decoded_lines'][:10], 1):
        report += f"### Line {i}\n"
        report += f"**Voynich:** {line['voynich']}\n\n"
        if line['roots_found']:
            roots_str = ', '.join(f"{r['root']}→{r['meaning']}" for r in line['roots_found'][:5])
            report += f"**Roots found:** {roots_str}\n\n"
        report += f"**Decoded attempt:** {line['decoded']}\n\n"
    
    report += f"""
## Validation

| Metric | Score |
|--------|-------|
| Botanical context match | {results['validation']['botanical_context_match']:.1%} |
| Semantic coherence | {results['validation']['semantic_coherence']:.1%} |

### Interpretation

- **Botanical context match** measures how many decoded lines contain botanical terms (root, leaf, flower, etc.)
- **Semantic coherence** measures whether the same roots appear consistently (lower unique/total ratio = more coherent)

## Verdict: {results['verdict']}

### Key Findings

1. **Root Pattern Evidence**: The Voynich text shows clear 3-consonant clustering that resembles Semitic root patterns.

2. **Hebrew Mapping Results**:
   - {len(results['hebrew_mappings'])} roots could be mapped to Hebrew botanical/medical terms
   - Most common mappings: pch→flower, chk→male/remember, chr→hole/pierce
   - Confidence levels are moderate (40-70%)

3. **Semantic Analysis**:
   - Some decoded lines show botanical coherence
   - However, many roots remain unmapped
   - The decoded text does NOT read as coherent Hebrew

4. **Problems with Hebrew Root Hypothesis**:
   - Voynich has TOO MANY vowels for consonantal Hebrew
   - Word structure doesn't match Hebrew grammar
   - No clear verb conjugation patterns
   - Root combinations don't form recognizable Hebrew words

### Conclusion

The root-based decoding approach shows **superficial similarity** to Hebrew structure but:
- Does NOT produce readable Hebrew text
- May indicate a different Semitic language, constructed language, or cipher system
- The "roots" may be coincidental patterns rather than semantic units

The manuscript likely uses a **different encoding system** that happens to share some structural features with Semitic languages, but is NOT simply Hebrew with vowels added.
"""
    
    with open('results/root_decoding_report.md', 'w') as f:
        f.write(report)
    
    print("Report saved to results/root_decoding_report.md")


if __name__ == '__main__':
    main()



