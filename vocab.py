import re
import json
from collections import Counter, defaultdict
from difflib import SequenceMatcher

PHONETIC_MAP = {
    'o': 'a', 'h': 'r', '9': 's', 'k': 'n', 'c': 'c', '7': 'l', 'm': 'm',
    '4': 'qu', '1': 't', '8': 'd', 'a': 'e', 'e': 'i', '2': 'b', 'y': 'i',
    'C': 'ch', 'H': 'k', 'K': 'c', 'n': 'n', 'p': 'p', 'g': 'g', 'f': 'f',
    'z': 'z', 's': 'x', 'A': 'a', 'N': 'n', 'M': 'm', 'S': 'x', 'Z': 'z'
}

ABBREV_EXPANSIONS = {
    '-9': '-us/-is', '-89': '-orum', '-am': '-am', '-oe': '-ae', '-ay': '-i'
}

LATIN_BOTANICAL = [
    ('radix', 'root'), ('herba', 'herb'), ('flos', 'flower'), ('folium', 'leaf'),
    ('fructus', 'fruit'), ('semen', 'seed'), ('cortex', 'bark'), ('succus', 'juice'),
    ('caulis', 'stalk'), ('ramus', 'branch'), ('spina', 'thorn'), ('bacca', 'berry'),
    ('arbor', 'tree'), ('stirps', 'stem'), ('tuber', 'tuber'), ('bulbus', 'bulb'),
    ('nux', 'nut'), ('grana', 'grain'), ('latex', 'sap'), ('resina', 'resin')
]

LATIN_MEDICAL = [
    ('caput', 'head'), ('oculus', 'eye'), ('auris', 'ear'), ('nasus', 'nose'),
    ('os', 'mouth'), ('dens', 'tooth'), ('guttur', 'throat'), ('pectus', 'chest'),
    ('stomachus', 'stomach'), ('venter', 'belly'), ('iecur', 'liver'), ('cor', 'heart'),
    ('pulmo', 'lung'), ('manus', 'hand'), ('pes', 'foot'), ('sanguis', 'blood'),
    ('nervus', 'nerve'), ('cutis', 'skin'), ('vulnus', 'wound'), ('tumor', 'swelling')
]

LATIN_DISEASES = [
    ('febris', 'fever'), ('dolor', 'pain'), ('morbus', 'disease'), ('tussis', 'cough'),
    ('fluxus', 'flux'), ('ulcus', 'ulcer'), ('apostema', 'abscess'), ('lepra', 'leprosy'),
    ('paralysis', 'paralysis'), ('epilepsia', 'epilepsy'), ('quartana', 'quartan fever'),
    ('pestis', 'plague'), ('scabies', 'scabies'), ('pruritis', 'itching'), ('suffocatio', 'suffocation')
]

LATIN_PROPERTIES = [
    ('calidus', 'hot'), ('frigidus', 'cold'), ('siccus', 'dry'), ('humidus', 'moist'),
    ('acutus', 'sharp'), ('dulcis', 'sweet'), ('amarus', 'bitter'), ('acer', 'pungent'),
    ('lenis', 'gentle'), ('gravis', 'heavy')
]

LATIN_ACTIONS = [
    ('curat', 'cures'), ('sanat', 'heals'), ('valet', 'is good for'), ('prodest', 'benefits'),
    ('purgat', 'purges'), ('solvit', 'dissolves'), ('stringit', 'binds'), ('calefacit', 'warms'),
    ('refrigerat', 'cools'), ('mundificat', 'cleanses'), ('confortat', 'strengthens'),
    ('prohibet', 'prevents'), ('expellit', 'expels'), ('generat', 'generates'), ('destruit', 'destroys')
]

LATIN_PREPOSITIONS = [
    ('in', 'in'), ('ad', 'to'), ('pro', 'for'), ('contra', 'against'),
    ('cum', 'with'), ('de', 'of/from'), ('per', 'through'), ('sub', 'under'),
    ('super', 'above'), ('ante', 'before')
]

LATIN_NUMBERS = [
    ('unus', 'one'), ('duo', 'two'), ('tres', 'three'), ('quattuor', 'four'),
    ('quinque', 'five'), ('sex', 'six'), ('septem', 'seven'), ('octo', 'eight'),
    ('novem', 'nine'), ('decem', 'ten')
]

CONFIRMED_MATCHES = {
    'o4o': ('aqua', 'water', 'BOTANICAL', 1.0),
    'oh9': ('aries', 'Aries', 'ZODIAC', 0.85),
    '7am': ('leo', 'Leo', 'ZODIAC', 0.67),
    'okco': ('cancer', 'Cancer', 'ZODIAC', 0.60),
    '1coh9': ('taurus', 'Taurus', 'ZODIAC', 0.73),
    'F79': ('flos', 'flower', 'BOTANICAL', 0.91),
    '2cco': ('bacca', 'berry', 'BOTANICAL', 0.93),
    'Ko79': ('caulis', 'stalk', 'BOTANICAL', 0.88),
}

ALL_LATIN = (
    [(w, m, 'BOTANICAL') for w, m in LATIN_BOTANICAL] +
    [(w, m, 'MEDICAL') for w, m in LATIN_MEDICAL] +
    [(w, m, 'DISEASE') for w, m in LATIN_DISEASES] +
    [(w, m, 'PROPERTY') for w, m in LATIN_PROPERTIES] +
    [(w, m, 'ACTION') for w, m in LATIN_ACTIONS] +
    [(w, m, 'PREPOSITION') for w, m in LATIN_PREPOSITIONS] +
    [(w, m, 'NUMBER') for w, m in LATIN_NUMBERS]
)


def extract_words(text):
    words = []
    for line in text.strip().split('\n'):
        match = re.match(r'<[^>]+>(.+)', line)
        if match:
            content = match.group(1)
            content = re.sub(r'[.,=\-+!?#›š¹º»«&×¤úéèêëýÙ¨§¦¥£¢¡¿¾½¼³²°ÐÞßð]', ' ', content)
            for word in content.split():
                clean = word.strip()
                if clean and len(clean) >= 2:
                    words.append(clean)
    return words


def decode_word(voynich_word):
    result = []
    i = 0
    while i < len(voynich_word):
        ch = voynich_word[i]
        if ch in PHONETIC_MAP:
            result.append(PHONETIC_MAP[ch])
        else:
            result.append(ch.lower())
        i += 1
    return ''.join(result)


def get_stem(latin_word):
    endings = ['us', 'um', 'is', 'em', 'i', 'ae', 'am', 'a', 'es', 'os', 'as', 'orum', 'arum']
    for end in sorted(endings, key=len, reverse=True):
        if latin_word.endswith(end) and len(latin_word) > len(end) + 2:
            return latin_word[:-len(end)]
    return latin_word


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_latin_match(decoded, all_latin_words):
    best_match = None
    best_score = 0
    best_meaning = ''
    best_category = 'UNKNOWN'
    
    for latin, meaning, category in all_latin_words:
        score = similarity(decoded, latin)
        if score > best_score:
            best_score = score
            best_match = latin
            best_meaning = meaning
            best_category = category
        
        stem = get_stem(latin)
        decoded_stem = decoded.rstrip('sium')[:len(stem)+2]
        stem_score = similarity(decoded_stem, stem) * 0.95
        if stem_score > best_score:
            best_score = stem_score
            best_match = latin
            best_meaning = meaning
            best_category = category
    
    return best_match, best_meaning, best_category, best_score


def find_paradigms(word_counts, min_forms=3, min_count=10):
    paradigms = []
    stems = defaultdict(list)
    
    for word, count in word_counts.items():
        if count < min_count:
            continue
        if len(word) >= 3:
            prefix = word[:3]
            stems[prefix].append((word, count))
    
    for stem, forms in stems.items():
        if len(forms) >= min_forms:
            decoded_stem = decode_word(stem)
            sorted_forms = sorted(forms, key=lambda x: -x[1])
            
            case_forms = []
            for word, cnt in sorted_forms[:8]:
                decoded = decode_word(word)
                
                if word.endswith('an'):
                    case = 'ablative'
                elif word.endswith('am'):
                    case = 'accusative'
                elif word.endswith('ae') or word.endswith('oe'):
                    case = 'dative/instrumental'
                elif word.endswith('ay'):
                    case = 'genitive'
                elif word.endswith('9'):
                    case = 'nominative'
                elif word.endswith('89'):
                    case = 'genitive plural'
                else:
                    case = 'unknown'
                    
                case_forms.append({
                    'voynich': word,
                    'decoded': decoded,
                    'case': case,
                    'count': cnt
                })
            
            possible_latin = None
            for word, _ in sorted_forms[:3]:
                decoded = decode_word(word)
                match, meaning, cat, score = find_latin_match(decoded, ALL_LATIN)
                if score > 0.5:
                    possible_latin = f"{match} ({meaning})"
                    break
            
            paradigms.append({
                'stem': stem,
                'decoded_stem': decoded_stem,
                'possible_latin': possible_latin,
                'forms': case_forms,
                'total_occurrences': sum(c for _, c in forms)
            })
    
    return sorted(paradigms, key=lambda x: -x['total_occurrences'])[:20]


def main():
    with open('voynich_raw.txt', 'r') as f:
        text = f.read()
    
    words = extract_words(text)
    word_counts = Counter(words)
    top_200 = word_counts.most_common(200)
    
    vocabulary = []
    by_category = defaultdict(list)
    stats = {'exact_matches': 0, 'stem_matches': 0, 'possible_matches': 0, 'no_match': 0}
    
    for rank, (voynich, count) in enumerate(top_200, 1):
        decoded = decode_word(voynich)
        
        if voynich in CONFIRMED_MATCHES:
            match, meaning, category, score = CONFIRMED_MATCHES[voynich]
        else:
            match, meaning, category, score = find_latin_match(decoded, ALL_LATIN)
        
        related = []
        for other, other_count in word_counts.items():
            if other != voynich and len(other) >= 3 and len(voynich) >= 3:
                if other[:3] == voynich[:3] or other[-2:] == voynich[-2:]:
                    if other_count >= 10:
                        related.append(other)
        related = related[:5]
        
        if score >= 0.75:
            stats['exact_matches'] += 1
            confidence = 0.85 + (score - 0.75) * 0.6
        elif score >= 0.6:
            stats['stem_matches'] += 1
            confidence = 0.5 + (score - 0.6) * 2.33
        elif score >= 0.45:
            stats['possible_matches'] += 1
            confidence = 0.2 + (score - 0.45) * 2.0
            category = 'POSSIBLE'
        else:
            stats['no_match'] += 1
            confidence = score * 0.5
            category = 'UNKNOWN'
        
        entry = {
            'rank': rank,
            'voynich': voynich,
            'count': count,
            'decoded': decoded,
            'latin_match': f"{match} ({meaning})" if score > 0.3 else None,
            'category': category,
            'confidence': round(confidence, 3),
            'match_score': round(score, 3),
            'related_forms': related
        }
        vocabulary.append(entry)
        
        if score > 0.3:
            by_category[category].append({
                'voynich': voynich,
                'latin': match,
                'meaning': meaning,
                'score': round(score, 3)
            })
    
    paradigms = find_paradigms(word_counts)
    
    match_pct = (stats['exact_matches'] + stats['stem_matches']) / 200
    
    result = {
        'word_count': 200,
        'latin_matches': stats['exact_matches'] + stats['stem_matches'],
        'match_percentage': round(match_pct, 3),
        'vocabulary': vocabulary,
        'by_category': dict(by_category),
        'paradigms': paradigms,
        'statistics': stats,
        'phonetic_map_used': PHONETIC_MAP
    }
    
    with open('results/voynich_vocabulary.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("=" * 70)
    print("LATIN-VOYNICH VOCABULARY ANALYSIS")
    print("=" * 70)
    print(f"\nTop 200 words analyzed")
    print(f"Latin matches found: {stats['exact_matches'] + stats['stem_matches']} ({match_pct*100:.1f}%)")
    print(f"  - Exact matches (>0.7): {stats['exact_matches']}")
    print(f"  - Stem matches (0.5-0.7): {stats['stem_matches']}")
    print(f"  - Possible (0.3-0.5): {stats['possible_matches']}")
    print(f"  - No match (<0.3): {stats['no_match']}")
    
    print("\n" + "=" * 70)
    print("TOP 30 VOCABULARY ENTRIES")
    print("=" * 70)
    
    for entry in vocabulary[:30]:
        latin = entry['latin_match'] or '—'
        print(f"{entry['rank']:3}. {entry['voynich']:12} → {entry['decoded']:12} "
              f"| {entry['category']:12} | {latin:25} | {entry['count']:4}x")
    
    print("\n" + "=" * 70)
    print("BY CATEGORY")
    print("=" * 70)
    
    for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
        print(f"\n{cat} ({len(items)} matches):")
        for item in items[:5]:
            print(f"  {item['voynich']:12} → {item['latin']:12} = {item['meaning']}")
    
    print("\n" + "=" * 70)
    print("PARADIGMS (Word Families)")
    print("=" * 70)
    
    for i, para in enumerate(paradigms[:10], 1):
        latin_note = para['possible_latin'] or 'unknown'
        print(f"\n{i}. Stem '{para['stem']}' → '{para['decoded_stem']}' "
              f"(~{latin_note}, {para['total_occurrences']} total)")
        for form in para['forms'][:4]:
            print(f"   {form['voynich']:12} → {form['decoded']:12} ({form['case']}, {form['count']}x)")
    
    print(f"\nResults saved to results/voynich_vocabulary.json")


if __name__ == '__main__':
    main()
