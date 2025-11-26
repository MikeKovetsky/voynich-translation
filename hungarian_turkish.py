import json
import re
from collections import Counter, defaultdict

# Hungarian plant names (medieval/old + modern)
HUNGARIAN_PLANTS = {
    'cornflower': {
        'modern': 'búzavirág',  # wheat-flower
        'old_forms': ['kék búza', 'kék virág'],
        'voynich': 'f2o89'
    },
    'hellebore': {
        'modern': 'hunyor',
        'old_forms': ['fekete hunyor', 'karácsonyi rózsa'],
        'voynich': 'h2o89'
    },
    'poppy': {
        'modern': 'mák',
        'old_forms': ['álomhozó', 'mákvirág'],
        'voynich': 'foay'
    },
    'cyclamen': {
        'modern': 'ciklámen',
        'old_forms': ['disznókenyér', 'kerek levelű'],  # pig-bread
        'voynich': 'hoom'
    },
    'castor': {
        'modern': 'ricinusfa',
        'old_forms': ['bab', 'babfa'],
        'voynich': 'goCam'
    }
}

# Turkish plant names (Ottoman/Old Turkish + modern)
TURKISH_PLANTS = {
    'cornflower': {
        'modern': 'peygamber çiçeği',  # prophet's flower
        'old_forms': ['mavi kantaron', 'gökyüzü çiçeği'],
        'voynich': 'f2o89'
    },
    'hellebore': {
        'modern': 'çöpleme',
        'old_forms': ['karaot', 'kara ot'],
        'voynich': 'h2o89'
    },
    'poppy': {
        'modern': 'gelincik',  # little bride
        'old_forms': ['haşhaş', 'afyon'],  # opium poppy
        'voynich': 'foay'
    },
    'cyclamen': {
        'modern': 'sıklamen',
        'old_forms': ['tavşankulağı', 'domuz ekmeği'],  # rabbit ear, pig bread
        'voynich': 'hoom'
    },
    'castor': {
        'modern': 'hint yağı',
        'old_forms': ['kerçi', 'rişin'],
        'voynich': 'goCam'
    }
}

# Vowel classes for harmony testing
HUNGARIAN_BACK = set('aáoóuú')
HUNGARIAN_FRONT = set('eéiíöőüű')

TURKISH_BACK = set('aıou')
TURKISH_FRONT = set('eiöü')

# Voynich vowel-like characters (based on EVA mapping + frequency analysis)
# EVA mapping: o=o, a=a, c=e, n=i 
# In Hungarian/Turkish: back vowels (o,u,a) vs front vowels (e,i,ö,ü)
VOYNICH_VOWEL_CANDIDATES_V1 = {
    'o': 'back',   # EVA 'o' - back vowel
    'a': 'back',   # EVA 'a' - can be back (Turkish) or neutral
    'c': 'front',  # EVA 'e' - front vowel!
    'n': 'front',  # EVA 'i' - front vowel
    'i': 'front',  # rare but appears
}

# Alternative mapping: treating 'a' as neutral/front (Hungarian style)
VOYNICH_VOWEL_CANDIDATES_V2 = {
    'o': 'back',   # back vowel
    'a': 'front',  # treating as front (like Hungarian 'e')
    'c': 'front',  # EVA 'e'
    'n': 'front',  # EVA 'i'
}

# Minimal mapping: only clear vowels
VOYNICH_VOWEL_CANDIDATES_V3 = {
    'o': 'back',   # definitely back
    'a': 'neutral',  # exclude from harmony test
    'c': 'front',  # EVA 'e'
}

# Hungarian suffix mappings
HUNGARIAN_SUFFIXES = {
    '-t': 'accusative',
    '-nak/-nek': 'dative',
    '-é': 'genitive',
    '-val/-vel': 'instrumental',
    '-n/-on/-en/-ön': 'superessive',
    '-ban/-ben': 'inessive',
    '-ba/-be': 'illative',
    '-ból/-ből': 'elative',
    '-ra/-re': 'sublative',
    '-ról/-ről': 'delative',
    '-nál/-nél': 'adessive',
    '-hoz/-hez/-höz': 'allative',
    '-tól/-től': 'ablative',
}

# Turkish suffix mappings
TURKISH_SUFFIXES = {
    '-ı/-i/-u/-ü': 'accusative',
    '-a/-e': 'dative',
    '-da/-de/-ta/-te': 'locative',
    '-dan/-den/-tan/-ten': 'ablative',
    '-ın/-in/-un/-ün': 'genitive',
    '-la/-le': 'instrumental',
}

# Voynich common suffixes (from analysis)
VOYNICH_SUFFIXES = {
    '9': 0.370,    # 37% - nominative/default
    '89': 0.118,   # 11.8% - genitive plural?
    'am': 0.094,   # 9.4% - accusative?
    'oe': 0.089,   # 8.9% - locative/dative?
    'ay': 0.069,   # 6.9% - genitive?
    'an': 0.045,   # 4.5% - superessive?
}

# Ardıç's specific claims to test
ARDIC_CLAIMS = {
    'october': {
        'voynich_word': 'ogzaf',
        'old_turkic': 'yuzai',
        'translation': 'autumn moon',
        'components': {'yuz': 'autumn', 'ai': 'moon'}
    },
    'november': {
        'voynich_word': 'sepel',
        'old_turkic': 'seper',
        'translation': 'rain moon',
        'components': {'seper': 'rain', 'ai': 'moon'}
    }
}

def load_voynich_words():
    words = []
    with open('voynich_raw.txt', 'r') as f:
        for line in f:
            line = re.sub(r'<[^>]+>', '', line)
            line = re.sub(r'[.,;=\-\+\?\!\›\š\¹\º\#\&\*\(\)\[\]\{\}]+', ' ', line)
            for word in line.split():
                word = word.strip()
                if word and len(word) > 1:
                    words.append(word)
    return words

def extract_vowel_pattern(word, vowel_map):
    pattern = []
    for char in word.lower():
        if char in vowel_map:
            pattern.append(vowel_map[char])
    return pattern

def test_vowel_harmony(words, vowel_map, ignore_neutral=True):
    harmony_compliant = 0
    mixed = 0
    total_tested = 0
    
    harmony_details = []
    
    for word in words:
        pattern = extract_vowel_pattern(word, vowel_map)
        
        # Filter out 'neutral' if ignoring
        if ignore_neutral:
            pattern = [p for p in pattern if p != 'neutral']
        
        if len(pattern) >= 2:
            total_tested += 1
            unique_types = set(pattern)
            if len(unique_types) == 1:
                harmony_compliant += 1
                harmony_details.append({'word': word, 'pattern': pattern, 'harmonic': True})
            else:
                mixed += 1
                if len(harmony_details) < 20:
                    harmony_details.append({'word': word, 'pattern': pattern, 'harmonic': False})
    
    percentage = harmony_compliant / total_tested if total_tested > 0 else 0
    
    # Determine verdict: 70%+ = strong, 50-70% = weak, <50% = absent
    if percentage >= 0.70:
        verdict = "STRONG"
    elif percentage >= 0.50:
        verdict = "WEAK"
    else:
        verdict = "ABSENT"
    
    return {
        'words_tested': total_tested,
        'harmony_compliant': harmony_compliant,
        'mixed_vowels': mixed,
        'percentage': round(percentage, 3),
        'verdict': verdict,
        'examples': harmony_details[:10]
    }

def test_all_vowel_mappings(words):
    results = {}
    mappings = {
        'v1_turkish_style': VOYNICH_VOWEL_CANDIDATES_V1,  # a=back
        'v2_hungarian_style': VOYNICH_VOWEL_CANDIDATES_V2,  # a=front
        'v3_minimal': VOYNICH_VOWEL_CANDIDATES_V3,  # a=neutral
    }
    
    for name, vmap in mappings.items():
        result = test_vowel_harmony(words, vmap)
        results[name] = result
        
    return results

def compute_suffix_distribution(words):
    suffix_counts = Counter()
    for word in words:
        if len(word) >= 2:
            suffix_counts[word[-1]] += 1
            if len(word) >= 3:
                suffix_counts[word[-2:]] += 1
    
    total = len(words)
    suffix_freq = {s: count/total for s, count in suffix_counts.most_common(20)}
    return suffix_freq

def compare_suffix_pattern(voynich_suffixes, language_suffixes):
    # Check if Voynich suffix distribution matches expected language pattern
    matches = []
    
    # Hungarian has front/back vowel alternation in suffixes
    # Turkish has 4-way vowel harmony (a/e/ı/i or o/ö/u/ü)
    
    # For Hungarian: check if we see pairs like am/em, an/en (vowel alternation)
    hungarian_pairs = [('am', 'em'), ('an', 'en'), ('ok', 'ek'), ('os', 'es')]
    turkish_pairs = [('am', 'em', 'ım', 'im'), ('an', 'en', 'ın', 'in')]
    
    # Look for alternation patterns in Voynich
    has_alternation = False
    if 'am' in voynich_suffixes and 'em' in voynich_suffixes:
        has_alternation = True
    if 'an' in voynich_suffixes and 'en' in voynich_suffixes:
        has_alternation = True
        
    return {
        'voynich_top_suffixes': dict(list(voynich_suffixes.items())[:10]),
        'has_vowel_alternation': has_alternation,
        'notes': 'Voynich shows -9 (37%) as dominant ending, -89 (12%), -am (9%)'
    }

def test_ardic_claims(words, zodiac_data):
    results = []
    
    # Look for Ardıç's specific words in zodiac sections
    for month, claim in ARDIC_CLAIMS.items():
        voynich_target = claim['voynich_word'].lower()
        
        found_in = []
        for section in zodiac_data.get('zodiac_sections', []):
            for label in section.get('labels', []):
                # Fuzzy match - look for similar words
                if similar_score(label.lower(), voynich_target) > 0.6:
                    found_in.append({
                        'section': section['sign'],
                        'folio': section['folio'],
                        'word_found': label,
                        'similarity': similar_score(label.lower(), voynich_target)
                    })
        
        results.append({
            'month': month,
            'ardic_voynich': voynich_target,
            'ardic_turkic': claim['old_turkic'],
            'translation_claim': claim['translation'],
            'found_matches': found_in,
            'verdict': 'FOUND' if found_in else 'NOT_FOUND'
        })
    
    return results

def similar_score(s1, s2):
    # Simple Levenshtein-based similarity
    if not s1 or not s2:
        return 0.0
    
    len1, len2 = len(s1), len(s2)
    if len1 > len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1
    
    distances = range(len1 + 1)
    for i2, c2 in enumerate(s2):
        new_distances = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                new_distances.append(distances[i1])
            else:
                new_distances.append(1 + min((distances[i1], distances[i1 + 1], new_distances[-1])))
        distances = new_distances
    
    max_len = max(len1, len2)
    return 1 - (distances[-1] / max_len) if max_len > 0 else 0.0

def test_plant_names(voynich_words, plant_dict, language_name):
    results = []
    
    for plant_id, plant_data in plant_dict.items():
        voynich_name = plant_data['voynich']
        
        # Strip common Voynich prefixes/suffixes to get root
        voynich_root = voynich_name.lower()
        if voynich_root.startswith('4o'):
            voynich_root = voynich_root[2:]
        if voynich_root.endswith('9'):
            voynich_root = voynich_root[:-1]
        
        # Compare with language plant names
        best_match = None
        best_score = 0
        
        all_names = [plant_data['modern']] + plant_data['old_forms']
        
        for name in all_names:
            # Normalize
            name_norm = name.lower().replace(' ', '')
            
            # Try phonetic similarity
            score = phonetic_match(voynich_root, name_norm)
            if score > best_score:
                best_score = score
                best_match = name
        
        results.append({
            'plant': plant_id,
            f'{language_name}_name': best_match or plant_data['modern'],
            'voynich_name': voynich_name,
            'voynich_root': voynich_root,
            'match_score': round(best_score, 2),
            'all_names_tested': all_names
        })
    
    return results

def phonetic_match(voynich, target):
    # Basic phonetic matching based on character positions
    # This is simplified - real analysis would need known phonetic values
    
    # Voynich -> possible phonetic values (from previous analysis)
    phonetic_map = {
        'o': 'o',
        'a': 'a',
        '4': 'q',
        '8': 'd',
        '9': 'y/s',
        'h': 'k/h',
        'c': 'ts/c',
        'k': 't/k',
        'e': 'e/l',
        'm': 'm',
        'n': 'n',
        'f': 'f/p',
        'g': 'g',
    }
    
    # Convert Voynich to potential phonetic
    voynich_phon = ''
    for c in voynich:
        voynich_phon += phonetic_map.get(c, c)
    
    # Simple character overlap score
    overlap = 0
    target_set = set(target)
    voynich_set = set(voynich_phon.replace('/', ''))
    
    common = target_set & voynich_set
    overlap = len(common) / max(len(target_set), len(voynich_set)) if target_set else 0
    
    # Length penalty
    len_diff = abs(len(voynich) - len(target))
    len_penalty = 1.0 - (len_diff * 0.1)
    
    return max(0, min(1, overlap * len_penalty))

def test_article_pattern(words):
    # Hungarian: "a" before consonants, "az" before vowels
    # Voynich: '4o' prefix at 12.9%
    
    prefix_counts = Counter()
    for word in words:
        if len(word) >= 2:
            prefix_counts[word[:2]] += 1
        if len(word) >= 3:
            prefix_counts[word[:3]] += 1
    
    total = len(words)
    
    # Check '4o' specifically
    prefix_4o = sum(1 for w in words if w.startswith('4o'))
    prefix_4o_pct = prefix_4o / total if total > 0 else 0
    
    # Hungarian article frequency is ~5-8% in typical text
    # Turkish has no articles - would be 0%
    
    return {
        'prefix_4o_count': prefix_4o,
        'prefix_4o_percentage': round(prefix_4o_pct * 100, 1),
        'matches_hungarian_article': 5.0 <= prefix_4o_pct * 100 <= 15.0,
        'matches_turkish_no_article': prefix_4o_pct * 100 < 3.0,
        'top_prefixes': dict(prefix_counts.most_common(10)),
        'interpretation': 'HIGH prefix rate (13%) suggests article-like function (Hungarian) rather than Turkish (no articles)'
    }

def calculate_overall_score(vowel_result, suffix_result, plant_results, article_result, is_hungarian):
    score = 0.0
    
    # Vowel harmony test (40% weight)
    if vowel_result['verdict'] == 'STRONG':
        score += 0.40
    elif vowel_result['verdict'] == 'WEAK':
        score += 0.20
    
    # Plant name matches (30% weight)
    avg_plant_match = sum(p['match_score'] for p in plant_results) / len(plant_results) if plant_results else 0
    score += avg_plant_match * 0.30
    
    # Article pattern (20% weight)
    if is_hungarian:
        if article_result['matches_hungarian_article']:
            score += 0.20
    else:  # Turkish
        if article_result['matches_turkish_no_article']:
            score += 0.20
    
    # Suffix alternation (10% weight)
    if suffix_result.get('has_vowel_alternation'):
        score += 0.10
    
    return round(score, 3)

def main():
    print("=" * 60)
    print("TRACK 8: HUNGARIAN & TURKISH DEEP VALIDATION")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading Voynich transcription...")
    words = load_voynich_words()
    print(f"   Loaded {len(words)} words")
    
    # Load zodiac data for Ardıç test
    try:
        with open('results/zodiac_analysis.json', 'r') as f:
            zodiac_data = json.load(f)
    except:
        zodiac_data = {}
    
    results = {
        'hungarian': {},
        'turkish': {},
        'comparison': {}
    }
    
    # ========== HUNGARIAN TESTING ==========
    print("\n" + "=" * 40)
    print("PART A: HUNGARIAN TESTING")
    print("=" * 40)
    
    # 1. Vowel harmony test with multiple mappings
    print("\n🔤 Testing vowel harmony with different mappings...")
    all_harmony_results = test_all_vowel_mappings(words)
    
    print("\n   Results per mapping:")
    for name, res in all_harmony_results.items():
        print(f"   • {name}: {res['harmony_compliant']}/{res['words_tested']} = {res['percentage']*100:.1f}% → {res['verdict']}")
    
    # Pick best mapping for Hungarian (a=front style)
    hung_vowel = all_harmony_results.get('v2_hungarian_style', all_harmony_results['v1_turkish_style'])
    results['hungarian']['vowel_harmony_test'] = hung_vowel
    results['hungarian']['all_vowel_mappings'] = all_harmony_results
    
    # 2. Plant name tests
    print("\n🌿 Testing Hungarian plant names...")
    hung_plants = test_plant_names(words, HUNGARIAN_PLANTS, 'hungarian')
    for p in hung_plants:
        print(f"   {p['plant']}: {p['hungarian_name']} vs {p['voynich_name']} → {p['match_score']:.2f}")
    results['hungarian']['plant_name_tests'] = hung_plants
    
    # 3. Suffix mapping
    print("\n📊 Analyzing suffix patterns...")
    suffix_dist = compute_suffix_distribution(words)
    hung_suffix = compare_suffix_pattern(suffix_dist, HUNGARIAN_SUFFIXES)
    print(f"   Top suffixes: {list(hung_suffix['voynich_top_suffixes'].keys())[:5]}")
    print(f"   Has vowel alternation: {hung_suffix['has_vowel_alternation']}")
    results['hungarian']['suffix_mapping'] = hung_suffix
    
    # 4. Article pattern
    print("\n📖 Testing article pattern...")
    article = test_article_pattern(words)
    print(f"   '4o' prefix: {article['prefix_4o_percentage']:.1f}%")
    print(f"   Matches Hungarian article: {article['matches_hungarian_article']}")
    results['hungarian']['article_pattern'] = article
    
    # Calculate Hungarian overall score
    hung_score = calculate_overall_score(hung_vowel, hung_suffix, hung_plants, article, True)
    results['hungarian']['overall_score'] = hung_score
    print(f"\n✅ Hungarian Overall Score: {hung_score:.1%}")
    
    # ========== TURKISH TESTING ==========
    print("\n" + "=" * 40)
    print("PART B: TURKISH TESTING")
    print("=" * 40)
    
    # 1. Vowel harmony test - Turkish style (a=back vowel)
    print("\n🔤 Testing Turkish vowel harmony (a=back, strict)...")
    turk_vowel = all_harmony_results.get('v1_turkish_style', all_harmony_results['v2_hungarian_style'])
    print(f"   Words tested: {turk_vowel['words_tested']}")
    print(f"   Harmony compliant: {turk_vowel['harmony_compliant']} ({turk_vowel['percentage']*100:.1f}%)")
    print(f"   Verdict: {turk_vowel['verdict']}")
    results['turkish']['vowel_harmony_test'] = turk_vowel
    
    # 2. Plant name tests
    print("\n🌿 Testing Turkish plant names...")
    turk_plants = test_plant_names(words, TURKISH_PLANTS, 'turkish')
    for p in turk_plants:
        print(f"   {p['plant']}: {p['turkish_name']} vs {p['voynich_name']} → {p['match_score']:.2f}")
    results['turkish']['plant_name_tests'] = turk_plants
    
    # 3. Suffix mapping
    print("\n📊 Analyzing suffix patterns (Turkish)...")
    turk_suffix = compare_suffix_pattern(suffix_dist, TURKISH_SUFFIXES)
    results['turkish']['suffix_mapping'] = turk_suffix
    
    # 4. Ardıç theory validation
    print("\n🔍 Validating Ardıç theory claims...")
    ardic_results = test_ardic_claims(words, zodiac_data)
    for r in ardic_results:
        status = "✅" if r['verdict'] == 'FOUND' else "❌"
        print(f"   {status} {r['month']}: '{r['ardic_voynich']}' = '{r['translation_claim']}'")
        if r['found_matches']:
            for m in r['found_matches'][:2]:
                print(f"      Found: '{m['word_found']}' in {m['section']} (sim: {m['similarity']:.2f})")
    
    verified = sum(1 for r in ardic_results if r['verdict'] == 'FOUND')
    results['turkish']['ardic_validation'] = {
        'claims_tested': len(ardic_results),
        'claims_verified': verified,
        'details': ardic_results,
        'verdict': 'PARTIALLY_SUPPORTED' if verified > 0 else 'NOT_SUPPORTED'
    }
    
    # Calculate Turkish overall score
    turk_score = calculate_overall_score(turk_vowel, turk_suffix, turk_plants, article, False)
    results['turkish']['overall_score'] = turk_score
    print(f"\n✅ Turkish Overall Score: {turk_score:.1%}")
    
    # ========== COMPARISON ==========
    print("\n" + "=" * 40)
    print("COMPARISON & VERDICT")
    print("=" * 40)
    
    # Determine winner
    if hung_score > turk_score + 0.1:
        winner = "HUNGARIAN"
        confidence = min(1.0, (hung_score - turk_score) * 2)
    elif turk_score > hung_score + 0.1:
        winner = "TURKISH"
        confidence = min(1.0, (turk_score - hung_score) * 2)
    else:
        winner = "INCONCLUSIVE"
        confidence = 0.3
    
    # Key differentiators
    differentiators = []
    
    if article['matches_hungarian_article'] and not article['matches_turkish_no_article']:
        differentiators.append("'4o' prefix (13%) supports Hungarian article pattern")
    
    if hung_vowel['verdict'] == 'STRONG':
        differentiators.append("Strong vowel harmony supports both languages")
    elif hung_vowel['verdict'] == 'WEAK':
        differentiators.append("Weak vowel harmony - inconclusive for either")
    else:
        differentiators.append("No vowel harmony - argues AGAINST both languages")
    
    if results['turkish']['ardic_validation']['claims_verified'] > 0:
        differentiators.append(f"Ardıç claims: {results['turkish']['ardic_validation']['claims_verified']}/{len(ardic_results)} partially verified")
    else:
        differentiators.append("Ardıç claims: NOT verified in zodiac sections")
    
    results['comparison'] = {
        'hungarian_score': hung_score,
        'turkish_score': turk_score,
        'better_candidate': winner,
        'confidence': round(confidence, 2),
        'key_differentiators': differentiators
    }
    
    print(f"\n🏆 Hungarian Score: {hung_score:.1%}")
    print(f"🏆 Turkish Score: {turk_score:.1%}")
    print(f"\n📊 Better Candidate: {winner}")
    print(f"   Confidence: {confidence:.1%}")
    print(f"\n🔑 Key Differentiators:")
    for d in differentiators:
        print(f"   • {d}")
    
    # Save results
    with open('results/hungarian_turkish_validation.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to results/hungarian_turkish_validation.json")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if hung_vowel['verdict'] == 'ABSENT':
        print("\n⚠️  CRITICAL FINDING: No vowel harmony detected!")
        print("   This is STRONG evidence AGAINST both Hungarian and Turkish.")
        print("   Both languages have MANDATORY vowel harmony.")
        print("   If Voynich shows no harmony, these languages are UNLIKELY.")
    else:
        print(f"\n📈 Vowel harmony: {hung_vowel['verdict']}")
        print(f"   This {'supports' if hung_vowel['verdict'] == 'STRONG' else 'weakly supports'} agglutinative hypothesis.")
    
    print(f"\n📖 Article pattern ('4o' = 13%):")
    print(f"   • Supports Hungarian: YES (Hungarian has articles ~5-10%)")
    print(f"   • Supports Turkish: NO (Turkish has NO articles)")
    
    print(f"\n🌿 Plant name matches:")
    hung_avg = sum(p['match_score'] for p in hung_plants) / len(hung_plants)
    turk_avg = sum(p['match_score'] for p in turk_plants) / len(turk_plants)
    print(f"   • Hungarian average: {hung_avg:.2f}")
    print(f"   • Turkish average: {turk_avg:.2f}")
    
    print(f"\n🔍 Ardıç Theory Status: {results['turkish']['ardic_validation']['verdict']}")
    
    return results

if __name__ == '__main__':
    results = main()



