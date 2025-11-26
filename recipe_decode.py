"""
Track 48: Decode Recipes Section using hybrid dictionary.
Applies Italian/Hebrew skeleton matching to high-signal recipe folios.
"""

import json
import re
from collections import Counter
from pathlib import Path

from voynich_data import get_folio_text, get_eva_pages


TARGET_FOLIOS = ['f111v', 'f107v', 'f107r', 'f80r', 'f80v']

RECIPE_VERBS = {
    'take', 'grind', 'boil', 'mix', 'add', 'apply', 'drink', 'heat',
    'prepare', 'wash', 'strain', 'cook', 'burn', 'pour', 'dry', 'cure'
}

MEDICAL_TERMS = {
    'heart', 'blood', 'skin', 'head', 'foot', 'pain', 'fever', 'wound',
    'cure', 'remedy', 'medicine', 'drug', 'potion', 'balm', 'oil'
}

BOTANICAL_TERMS = {
    'earth', 'root', 'leaf', 'seed', 'flower', 'branch', 'tree', 'fruit',
    'herb', 'plant', 'sun', 'moon', 'salt', 'water', 'juice', 'thyme',
    'fig', 'barley'
}


def load_proto_romance():
    path = Path('results/proto_romance_analysis.json')
    if not path.exists():
        return None
    return json.load(open(path))


def load_master_dict():
    path = Path('results/master_dictionary.json')
    if not path.exists():
        return {}
    data = json.load(open(path))
    return {e['voynich']: e for e in data.get('entries', [])}


def build_hybrid_dict(proto):
    dictionary = {}
    
    if proto and 'italian_roots' in proto:
        for entry in proto['italian_roots'].get('exact', []):
            v = entry['voynich']
            if v not in dictionary:
                dictionary[v] = {
                    'meaning': entry['meaning'],
                    'source': 'italian',
                    'word': entry['italian'],
                    'confidence': 0.6,
                    'frequency': entry.get('frequency', 0)
                }
        
        for entry in proto['italian_roots'].get('contains', []):
            v = entry['voynich']
            if v not in dictionary:
                dictionary[v] = {
                    'meaning': entry['meaning'],
                    'source': 'italian_partial',
                    'word': entry['italian'],
                    'confidence': 0.4,
                    'frequency': entry.get('frequency', 0)
                }
    
    if proto and 'hebrew_roots' in proto:
        for entry in proto['hebrew_roots'].get('exact', []):
            v = entry['voynich']
            if v not in dictionary:
                dictionary[v] = {
                    'meaning': entry['meaning'],
                    'source': 'hebrew',
                    'word': entry['hebrew'],
                    'confidence': 0.5,
                    'frequency': entry.get('frequency', 0)
                }
            elif dictionary[v]['confidence'] < 0.5:
                dictionary[v] = {
                    'meaning': entry['meaning'],
                    'source': 'hebrew',
                    'word': entry['hebrew'],
                    'confidence': 0.5,
                    'frequency': entry.get('frequency', 0)
                }
        
        for entry in proto['hebrew_roots'].get('contains', []):
            v = entry['voynich']
            if v not in dictionary:
                dictionary[v] = {
                    'meaning': entry['meaning'],
                    'source': 'hebrew_partial',
                    'word': entry['hebrew'],
                    'confidence': 0.3,
                    'frequency': entry.get('frequency', 0)
                }
    
    return dictionary


def clean_word(w):
    return re.sub(r'[!?<>@$\d]', '', w).strip()


def extract_folio_lines(folio):
    text = get_folio_text(folio, 'EVA', 'H')
    lines = []
    for loc, content in sorted(text.items()):
        words_raw = re.split(r'[.\s]+', content)
        words = [clean_word(w) for w in words_raw if clean_word(w)]
        lines.append({
            'location': loc,
            'raw': content,
            'words': words
        })
    return lines


def translate_line(words, dictionary):
    translated = []
    unknown = []
    
    for w in words:
        if w in dictionary:
            entry = dictionary[w]
            translated.append(f"{entry['meaning']}({entry['confidence']:.1f})")
        else:
            translated.append(f"[{w}]")
            unknown.append(w)
    
    return translated, unknown


def calc_coherence(meanings):
    known = [m for m in meanings if not m.startswith('[')]
    if not known:
        return 0.0
    
    score = 0
    for m in known:
        term = m.split('(')[0]
        if term in MEDICAL_TERMS or term in BOTANICAL_TERMS:
            score += 1
    
    return score / len(known) if known else 0


def find_recipe_patterns(meanings):
    patterns = []
    text_lower = ' '.join(meanings).lower()
    
    botanical_count = sum(1 for m in meanings if any(t in m.lower() for t in BOTANICAL_TERMS))
    medical_count = sum(1 for m in meanings if any(t in m.lower() for t in MEDICAL_TERMS))
    
    if botanical_count >= 2:
        patterns.append('ingredient_list')
    if medical_count >= 2:
        patterns.append('medical_instruction')
    if 'heart' in text_lower or 'cure' in text_lower:
        patterns.append('cardiac_remedy')
    if 'blood' in text_lower:
        patterns.append('blood_remedy')
    if 'skin' in text_lower or 'foot' in text_lower:
        patterns.append('external_application')
    if 'fig' in text_lower or 'barley' in text_lower:
        patterns.append('dietary_recipe')
    
    return patterns


def decode_folio(folio, dictionary):
    lines = extract_folio_lines(folio)
    
    total_words = 0
    translated_words = 0
    all_unknown = []
    decoded_lines = []
    all_patterns = Counter()
    meaning_counts = Counter()
    
    for line in lines:
        words = line['words']
        total_words += len(words)
        
        translated, unknown = translate_line(words, dictionary)
        translated_words += len(words) - len(unknown)
        all_unknown.extend(unknown)
        
        coherence = calc_coherence(translated)
        patterns = find_recipe_patterns(translated)
        
        for p in patterns:
            all_patterns[p] += 1
        
        for t in translated:
            if not t.startswith('['):
                meaning = t.split('(')[0]
                meaning_counts[meaning] += 1
        
        decoded_lines.append({
            'location': line['location'],
            'voynich': ' '.join(words),
            'translated': ' '.join(translated),
            'confidence': (len(words) - len(unknown)) / len(words) if words else 0,
            'unknown_words': unknown,
            'patterns': patterns
        })
    
    translation_rate = translated_words / total_words if total_words else 0
    
    coherent = [l for l in decoded_lines if l['confidence'] > 0.3 and l['patterns']]
    
    return {
        'folio': folio,
        'total_words': total_words,
        'translated_words': translated_words,
        'translation_rate': translation_rate,
        'lines': decoded_lines,
        'coherent_phrases': [{
            'line': l['location'],
            'translation': l['translated'],
            'patterns': l['patterns']
        } for l in coherent[:10]],
        'recipe_patterns_found': dict(all_patterns),
        'top_meanings': dict(meaning_counts.most_common(15)),
        'unknown_words': list(set(all_unknown))[:50]
    }


def determine_verdict(results):
    rates = [r['translation_rate'] for r in results.values()]
    avg_rate = sum(rates) / len(rates) if rates else 0
    
    total_coherent = sum(len(r['coherent_phrases']) for r in results.values())
    total_patterns = sum(len(r['recipe_patterns_found']) for r in results.values())
    
    if avg_rate > 0.5 and total_coherent > 10:
        return 'READABLE'
    elif avg_rate > 0.3 or total_coherent > 5:
        return 'PARTIAL'
    else:
        return 'UNREADABLE'


def generate_report(results, overall, verdict):
    lines = ['# Recipe Section Translation Attempt\n']
    lines.append(f'**Overall Verdict: {verdict}**\n')
    lines.append(f'- Average translation rate: {overall["translation_rate"]:.1%}')
    lines.append(f'- Total words attempted: {overall["total_words_attempted"]}')
    lines.append(f'- Successfully translated: {overall["successfully_translated"]}\n')
    
    for folio, data in results.items():
        lines.append(f'## {folio.upper()} ({data["total_words"]} words)\n')
        lines.append(f'Translation rate: {data["translation_rate"]:.1%}\n')
        
        lines.append('### Sample Translations\n')
        for i, line in enumerate(data['lines'][:5]):
            lines.append(f'**Line {line["location"]}**')
            lines.append(f'- Voynich: `{line["voynich"][:60]}...`' if len(line["voynich"]) > 60 else f'- Voynich: `{line["voynich"]}`')
            lines.append(f'- Decoded: {line["translated"][:80]}...' if len(line["translated"]) > 80 else f'- Decoded: {line["translated"]}')
            lines.append(f'- Confidence: {line["confidence"]:.1%}\n')
        
        if data['coherent_phrases']:
            lines.append('### Coherent Phrases Found\n')
            for p in data['coherent_phrases'][:5]:
                lines.append(f'- **{p["line"]}**: {p["translation"][:60]}')
                lines.append(f'  - Patterns: {", ".join(p["patterns"])}\n')
        
        if data['recipe_patterns_found']:
            lines.append('### Recipe Patterns\n')
            for pat, count in data['recipe_patterns_found'].items():
                lines.append(f'- {pat}: {count} occurrences')
            lines.append('')
        
        if data['top_meanings']:
            lines.append('### Most Frequent Meanings\n')
            for meaning, count in list(data['top_meanings'].items())[:10]:
                lines.append(f'- {meaning}: {count}')
            lines.append('')
    
    lines.append('## Interpretation\n')
    if verdict == 'READABLE':
        lines.append('The recipe section shows consistent translation patterns suggesting')
        lines.append('the hybrid Italian/Hebrew dictionary captures meaningful content.')
        lines.append('Medical and botanical terminology appears systematically.')
    elif verdict == 'PARTIAL':
        lines.append('Partial readability achieved. Some coherent phrases found but')
        lines.append('significant portions remain untranslatable. The dictionary')
        lines.append('captures some meaning but is incomplete.')
    else:
        lines.append('The current dictionary does not produce readable translations.')
        lines.append('Either the encoding system is more complex, or the skeleton')
        lines.append('matching approach requires refinement.')
    
    return '\n'.join(lines)


def main():
    print('Track 48: Recipe Section Decoding')
    print('=' * 50)
    
    proto = load_proto_romance()
    if not proto:
        print('ERROR: proto_romance_analysis.json not found')
        return
    
    dictionary = build_hybrid_dict(proto)
    print(f'Loaded {len(dictionary)} dictionary entries')
    
    results = {}
    total_words = 0
    total_translated = 0
    
    for folio in TARGET_FOLIOS:
        print(f'\nProcessing {folio}...')
        data = decode_folio(folio, dictionary)
        results[folio] = data
        total_words += data['total_words']
        total_translated += data['translated_words']
        print(f'  Words: {data["total_words"]}, Translated: {data["translated_words"]} ({data["translation_rate"]:.1%})')
        print(f'  Patterns: {data["recipe_patterns_found"]}')
    
    overall = {
        'total_words_attempted': total_words,
        'successfully_translated': total_translated,
        'translation_rate': total_translated / total_words if total_words else 0,
        'coherence_score': sum(len(r['coherent_phrases']) for r in results.values()) / len(results)
    }
    
    verdict = determine_verdict(results)
    
    output = {
        'target_folios': TARGET_FOLIOS,
        'translations': results,
        'overall_stats': overall,
        'verdict': verdict,
        'dictionary_size': len(dictionary)
    }
    
    Path('results').mkdir(exist_ok=True)
    with open('results/recipe_translation.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    report = generate_report(results, overall, verdict)
    with open('results/recipe_translation_report.md', 'w') as f:
        f.write(report)
    
    print('\n' + '=' * 50)
    print(f'VERDICT: {verdict}')
    print(f'Translation rate: {overall["translation_rate"]:.1%}')
    print(f'Results saved to results/recipe_translation.json')
    print(f'Report saved to results/recipe_translation_report.md')


if __name__ == '__main__':
    main()



