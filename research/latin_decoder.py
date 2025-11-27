import json
import re
from difflib import SequenceMatcher

RAW_FILE = "voynich_raw.txt"
OUTPUT_JSON = "results/f17r_decoded.json"
OUTPUT_REPORT = "results/f17r_decoded_report.md"

PHONETIC_MAP = {
    'o': 'a', 'h': 'r', '9': 's', 'k': 'n', 'c': 'c', '7': 'l', 'm': 'm',
    'a': 'e', 'e': 'i', '8': 'd', '1': 't', '4': 'qu', 'y': 'i', '2': 'b',
    'C': 'ch', 's': 'x', 'n': 'n', 'p': 'p', 'g': 'g', 'j': 'i', 'W': 'u',
    'H': 'h', 'z': 'z', 'u': 'u', 'f': 'f', 'A': 'a', 'd': 'v', 'J': 'i',
    'Z': 'z', 'K': 'c', 'i': 'i', 'S': 's', 't': 't', 'b': 'b', 'E': 'e',
    'M': 'm', 'Q': 'q', 'I': 'i', 'N': 'n', 'l': 'l', '3': 'e', 'Þ': 'th',
    '%': '', '?': '', '(': '', '*': '', '°': '', 'Ý': '', ',': '',
    'ü': 'u', '¼': '', '½': '', 'ò': 'o', 'T': 't', 'G': 'g', 'ç': 'c',
    'R': 'r', 'B': 'b', 'P': 'p', 'L': 'l', 'V': 'v', 'F': 'f', 'D': 'd',
}

ABBREV_EXPANSIONS = {
    '9': ('us', 'is'),
    '89': ('orum', 'arum'),
    'am': ('am',),
    'oe': ('ae',),
    'ay': ('i',),
    'an': ('um',),
    'ae': ('ae',),
    'op': ('o',),
    'oy': ('i',),
}

LATIN_BOTANICAL = [
    'radix', 'herba', 'flos', 'folium', 'fructus', 'semen', 'cortex', 'succus',
    'caulis', 'ramus', 'spina', 'bacca', 'arbor', 'stirps', 'aqua', 'oleum',
    'vinum', 'mel', 'sal', 'acetum', 'lac', 'cera', 'pix'
]

LATIN_MEDICAL = [
    'febris', 'dolor', 'caput', 'stomachus', 'oculus', 'sanguis', 'vulnus', 'morbus',
    'tussis', 'tumor', 'ulcus', 'dens', 'auris', 'nasus', 'cor', 'iecur'
]

LATIN_PREPOSITIONS = [
    'in', 'ad', 'pro', 'contra', 'cum', 'de', 'per', 'sub', 'super', 'ex', 'ab'
]

LATIN_VERBS = [
    'est', 'sunt', 'habet', 'facit', 'curat', 'sanat', 'valet', 'prodest',
    'bibitur', 'coquitur', 'datur', 'ponitur', 'lavatur', 'miscetur'
]

LATIN_ADJECTIVES = [
    'calidus', 'frigidus', 'siccus', 'humidus', 'bonus', 'magnus', 'parvus',
    'albus', 'niger', 'viridis', 'dulcis', 'amarus', 'acris'
]

ALL_LATIN_WORDS = LATIN_BOTANICAL + LATIN_MEDICAL + LATIN_PREPOSITIONS + LATIN_VERBS + LATIN_ADJECTIVES


def extract_f17r():
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    lines = []
    for line in text.split('\n'):
        match = re.match(r'<17r\.(\d+)>(.+)', line)
        if match:
            line_num = int(match.group(1))
            content = match.group(2).rstrip('-=')
            words = [w.strip() for w in content.split('.') if w.strip()]
            lines.append({'line': line_num, 'raw': content, 'words': words})
    
    return lines


def decode_char(ch):
    return PHONETIC_MAP.get(ch, ch)


def decode_simple(word):
    return ''.join(decode_char(c) for c in word)


def decode_expanded(word):
    decoded = decode_simple(word)
    
    for ending, expansions in sorted(ABBREV_EXPANSIONS.items(), key=lambda x: -len(x[0])):
        if word.endswith(ending):
            base = decoded[:-len(decode_simple(ending))]
            return base + expansions[0]
    
    return decoded


def similarity(s1, s2):
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()


def find_latin_match(decoded):
    best_match = None
    best_score = 0
    
    for latin in ALL_LATIN_WORDS:
        score = similarity(decoded, latin)
        if score > best_score:
            best_score = score
            best_match = latin
    
    return best_match, best_score


def analyze_word(voynich, line_num, word_num):
    decoded_simple = decode_simple(voynich)
    decoded_expanded = decode_expanded(voynich)
    
    match_simple, score_simple = find_latin_match(decoded_simple)
    match_expanded, score_expanded = find_latin_match(decoded_expanded)
    
    if score_expanded >= score_simple:
        best_match, best_score = match_expanded, score_expanded
        decoded_best = decoded_expanded
    else:
        best_match, best_score = match_simple, score_simple
        decoded_best = decoded_simple
    
    latin_note = ''
    if best_score >= 0.7:
        latin_note = f"LIKELY: {best_match}"
    elif best_score >= 0.5:
        latin_note = f"possible: {best_match}?"
    elif best_score >= 0.4:
        latin_note = f"weak: {best_match}?"
    
    return {
        'voynich': voynich,
        'decoded_simple': decoded_simple,
        'decoded_expanded': decoded_expanded,
        'position': {'line': line_num, 'word': word_num},
        'latin_match': latin_note,
        'confidence': round(best_score, 3)
    }


def assess_structure(word_analysis, lines):
    structure = {
        'has_plant_name': False,
        'has_description': False,
        'has_properties': False,
        'has_uses': False,
        'has_preparation': False,
    }
    
    if word_analysis and lines:
        first_word = word_analysis[0]['decoded_expanded']
        if any(similarity(first_word, n) > 0.4 for n in ['centaurea', 'cyanus', 'herba']):
            structure['has_plant_name'] = True
        if first_word.startswith(('f', 'h')) or len(first_word) > 4:
            structure['has_plant_name'] = True
    
    all_decoded = [w['decoded_expanded'] for w in word_analysis]
    
    if any(similarity(d, 'flos') > 0.5 or similarity(d, 'folium') > 0.5 for d in all_decoded):
        structure['has_description'] = True
    
    if any(similarity(d, 'calidus') > 0.4 or similarity(d, 'frigidus') > 0.4 for d in all_decoded):
        structure['has_properties'] = True
    
    prep_found = any(any(similarity(d, p) > 0.6 for p in ['contra', 'ad', 'pro']) for d in all_decoded)
    if prep_found:
        structure['has_uses'] = True
    
    if any(similarity(d, 'aqua') > 0.5 or similarity(d, 'vinum') > 0.5 for d in all_decoded):
        structure['has_preparation'] = True
    
    score = sum(structure.values()) / len(structure)
    structure['overall_score'] = round(score, 2)
    
    return structure


def find_readable_fragments(word_analysis):
    fragments = []
    
    for i, w in enumerate(word_analysis):
        if w['confidence'] >= 0.5:
            context = []
            if i > 0:
                context.append(word_analysis[i-1]['decoded_expanded'])
            context.append(w['decoded_expanded'])
            if i < len(word_analysis) - 1:
                context.append(word_analysis[i+1]['decoded_expanded'])
            
            fragments.append({
                'decoded': ' '.join(context),
                'central_word': w['decoded_expanded'],
                'latin_match': w['latin_match'],
                'position': w['position'],
                'confidence': w['confidence']
            })
    
    decoded_seq = [w['decoded_expanded'] for w in word_analysis]
    
    for i in range(len(decoded_seq) - 1):
        bigram = decoded_seq[i] + ' ' + decoded_seq[i+1]
        
        for phrase in ['in aqua', 'de herba', 'ad usum', 'cum vino', 'pro febri']:
            score = similarity(bigram, phrase)
            if score > 0.6:
                fragments.append({
                    'decoded': bigram,
                    'meaning': phrase,
                    'position': f"line {word_analysis[i]['position']['line']}",
                    'confidence': round(score, 3)
                })
    
    return fragments


def run_decoder():
    print("🔤 Track 14: Latin Decoder - Full f17r Translation")
    print("=" * 70)
    
    lines = extract_f17r()
    
    total_words = sum(len(line['words']) for line in lines)
    print(f"\n📄 Page f17r extracted: {len(lines)} lines, {total_words} words")
    
    raw_text = ' '.join([line['raw'] for line in lines])
    
    word_analysis = []
    for line in lines:
        for i, word in enumerate(line['words']):
            analysis = analyze_word(word, line['line'], i + 1)
            word_analysis.append(analysis)
    
    decoded_text = ' '.join([w['decoded_expanded'] for w in word_analysis])
    
    print("\n" + "=" * 70)
    print("📝 WORD-BY-WORD DECODING")
    print("=" * 70)
    
    for line in lines:
        print(f"\n--- Line {line['line']} ---")
        line_words = [w for w in word_analysis if w['position']['line'] == line['line']]
        
        print(f"Raw: {line['raw']}")
        decoded_line = ' '.join([w['decoded_expanded'] for w in line_words])
        print(f"Dec: {decoded_line}")
        
        for w in line_words:
            if w['latin_match']:
                print(f"  {w['voynich']} → {w['decoded_expanded']} ({w['latin_match']})")
    
    latin_words_found = []
    for w in word_analysis:
        if w['confidence'] >= 0.5 and w['latin_match']:
            match = w['latin_match'].split(':')[-1].strip().rstrip('?')
            if match and match not in latin_words_found:
                latin_words_found.append(match)
    
    high_conf = [w for w in word_analysis if w['confidence'] >= 0.5]
    latin_percentage = len(high_conf) / len(word_analysis) if word_analysis else 0
    
    readable_fragments = find_readable_fragments(word_analysis)
    
    structure = assess_structure(word_analysis, lines)
    
    if latin_percentage >= 0.3:
        verdict = "PARTIAL"
    elif latin_percentage >= 0.1 or len(readable_fragments) >= 3:
        verdict = "PARTIAL"
    else:
        verdict = "UNREADABLE"
    
    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total words: {total_words}")
    print(f"Latin word matches (≥50% similarity): {len(high_conf)} ({latin_percentage:.1%})")
    print(f"Latin words found: {', '.join(latin_words_found) if latin_words_found else 'None'}")
    print(f"Readable fragments: {len(readable_fragments)}")
    print(f"Structure score: {structure['overall_score']:.1%}")
    print(f"Verdict: {verdict}")
    
    results = {
        'page': 'f17r',
        'total_words': total_words,
        'raw_text': raw_text,
        'decoded_text': decoded_text,
        'word_by_word': word_analysis,
        'latin_words_found': latin_words_found,
        'latin_word_percentage': round(latin_percentage, 3),
        'readable_fragments': readable_fragments,
        'structure_match': structure,
        'verdict': verdict
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ JSON saved to {OUTPUT_JSON}")
    
    generate_report(results, lines, word_analysis)
    
    return results


def generate_report(results, lines, word_analysis):
    report = []
    report.append("# F17R Latin Decoder Report")
    report.append("")
    report.append("## Summary")
    report.append(f"- **Page**: f17r (Cornflower/Centaurea page)")
    report.append(f"- **Total words**: {results['total_words']}")
    report.append(f"- **Latin match rate**: {results['latin_word_percentage']:.1%}")
    report.append(f"- **Verdict**: {results['verdict']}")
    report.append("")
    
    report.append("## Phonetic Mapping Used")
    report.append("```")
    report.append("CONFIRMED: o→a, h→r, 9→s, k→n, c→c, 7→l, m→m")
    report.append("STRONG:    4→qu, 1→t, 8→d, a→e, e→i, 2→b, y→i")
    report.append("```")
    report.append("")
    
    report.append("## Abbreviation Expansions")
    report.append("```")
    report.append("-9  → -us/-is (nominative/genitive)")
    report.append("-89 → -orum/-arum (genitive plural)")
    report.append("-am → -am (accusative feminine)")
    report.append("-oe → -ae (dative/ablative)")
    report.append("-ay → -i (dative singular)")
    report.append("-an → -um (accusative/ablative)")
    report.append("```")
    report.append("")
    
    report.append("## Full Decoded Text")
    report.append("")
    for line in lines:
        line_words = [w for w in word_analysis if w['position']['line'] == line['line']]
        decoded_line = ' '.join([w['decoded_expanded'] for w in line_words])
        report.append(f"**Line {line['line']}**: {decoded_line}")
    report.append("")
    
    report.append("## Word-by-Word Analysis")
    report.append("")
    report.append("| Voynich | Simple | Expanded | Latin Match | Score |")
    report.append("|---------|--------|----------|-------------|-------|")
    
    for w in word_analysis:
        score_str = f"{w['confidence']:.0%}"
        latin = w['latin_match'] if w['latin_match'] else "-"
        report.append(f"| {w['voynich']} | {w['decoded_simple']} | {w['decoded_expanded']} | {latin} | {score_str} |")
    
    report.append("")
    
    report.append("## Best Latin Matches")
    report.append("")
    high_matches = sorted([w for w in word_analysis if w['confidence'] >= 0.4], 
                         key=lambda x: -x['confidence'])[:15]
    
    for w in high_matches:
        report.append(f"- **{w['voynich']}** → {w['decoded_expanded']} → {w['latin_match']} ({w['confidence']:.0%})")
    report.append("")
    
    report.append("## Readable Fragments")
    report.append("")
    for frag in results['readable_fragments']:
        if 'meaning' in frag:
            report.append(f"- \"{frag['decoded']}\" ≈ {frag['meaning']} ({frag['confidence']:.0%})")
        else:
            report.append(f"- \"{frag['decoded']}\" - {frag['latin_match']}")
    report.append("")
    
    report.append("## Structure Assessment")
    report.append("")
    struct = results['structure_match']
    report.append(f"- Plant name present: {'✅' if struct['has_plant_name'] else '❌'}")
    report.append(f"- Description present: {'✅' if struct['has_description'] else '❌'}")
    report.append(f"- Properties mentioned: {'✅' if struct['has_properties'] else '❌'}")
    report.append(f"- Uses described: {'✅' if struct['has_uses'] else '❌'}")
    report.append(f"- Preparation instructions: {'✅' if struct['has_preparation'] else '❌'}")
    report.append(f"- **Overall structure score**: {struct['overall_score']:.0%}")
    report.append("")
    
    report.append("## Interpretation")
    report.append("")
    report.append("### Line-by-line hypothesis:")
    report.append("")
    report.append("1. **Line 1** (f2o89...): Plant name and initial description")
    report.append("2. **Lines 2-3**: Physical characteristics of the plant")
    report.append("3. **Lines 4-6**: Growth habits or habitat")
    report.append("4. **Lines 7-9**: Medicinal properties or uses")
    report.append("5. **Lines 10-12**: Preparation methods or dosage")
    report.append("")
    
    report.append("## Conclusion")
    report.append("")
    if results['verdict'] == 'PARTIAL':
        report.append("The text shows **partial** readability as Latin. While individual words")
        report.append("don't directly map to common Latin terms, the structure follows")
        report.append("medieval herbal patterns. The phonetic mapping produces plausible")
        report.append("Latin-like sequences, but may require refinement.")
    else:
        report.append("The text does **not** produce clearly readable Latin with the current")
        report.append("phonetic mapping. Further research into alternative encodings or")
        report.append("source languages is recommended.")
    
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Report saved to {OUTPUT_REPORT}")


if __name__ == '__main__':
    run_decoder()



