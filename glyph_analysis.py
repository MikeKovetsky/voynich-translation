"""
Track 36: Original Glyph Pattern Analysis
Analyze Voynich at the GLYPH level, without Latin-letter assumptions.
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
import voynich_data as vd

# Voynich Glyph Inventory
# Based on scholarly consensus about distinct glyph shapes
# NOT using EVA letter names - using neutral glyph IDs

GLYPH_INVENTORY = {
    # Basic characters (circles, loops)
    'G01': {'eva': 'o', 'desc': 'small circle', 'type': 'basic'},
    'G02': {'eva': 'a', 'desc': 'circle with tail left', 'type': 'basic'},
    'G03': {'eva': 'e', 'desc': 'short stroke / c-shape', 'type': 'basic'},
    'G04': {'eva': 'y', 'desc': 'circle with descender', 'type': 'basic'},
    'G05': {'eva': 'i', 'desc': 'single stroke / minim', 'type': 'basic'},
    'G06': {'eva': 'n', 'desc': 'double stroke / two minims', 'type': 'basic'},
    'G07': {'eva': 'm', 'desc': 'triple stroke / three minims', 'type': 'basic'},
    
    # Bench characters (c-shape with stroke)
    'G08': {'eva': 'ch', 'desc': 'bench (c + h)', 'type': 'bench'},
    'G09': {'eva': 'sh', 'desc': 'tall bench (s + h)', 'type': 'bench'},
    
    # Gallows (tall letters)
    'G10': {'eva': 't', 'desc': 'gallows type 1', 'type': 'gallows'},
    'G11': {'eva': 'k', 'desc': 'gallows type 2 (with loop)', 'type': 'gallows'},
    'G12': {'eva': 'p', 'desc': 'gallows type 3 (curved top)', 'type': 'gallows'},
    'G13': {'eva': 'f', 'desc': 'gallows type 4 (double curved)', 'type': 'gallows'},
    
    # Special characters
    'G14': {'eva': 'd', 'desc': 'loop with descender', 'type': 'special'},
    'G15': {'eva': 's', 'desc': 'tall s-shape', 'type': 'special'},
    'G16': {'eva': 'r', 'desc': 'small r-shape', 'type': 'special'},
    'G17': {'eva': 'l', 'desc': 'tall stroke', 'type': 'special'},
    'G18': {'eva': 'q', 'desc': 'special form (rare)', 'type': 'special'},
    'G19': {'eva': 'x', 'desc': 'cross-like (rare)', 'type': 'special'},
    'G20': {'eva': 'g', 'desc': 'special g-form (rare)', 'type': 'special'},
    
    # Benched gallows (ligatures)
    'G21': {'eva': 'cth', 'desc': 'benched gallows type 1', 'type': 'ligature'},
    'G22': {'eva': 'ckh', 'desc': 'benched gallows type 2', 'type': 'ligature'},
    'G23': {'eva': 'cph', 'desc': 'benched gallows type 3', 'type': 'ligature'},
    'G24': {'eva': 'cfh', 'desc': 'benched gallows type 4', 'type': 'ligature'},
}

EVA_TO_GLYPH = {}
for gid, info in GLYPH_INVENTORY.items():
    EVA_TO_GLYPH[info['eva']] = gid

LIGATURES = ['cth', 'ckh', 'cph', 'cfh', 'ch', 'sh', 'iin', 'iiin', 'ain', 'aiin', 'aiiin']


def eva_to_glyphs(word):
    """Convert EVA word to glyph sequence."""
    glyphs = []
    i = 0
    sorted_eva = sorted(EVA_TO_GLYPH.keys(), key=len, reverse=True)
    
    while i < len(word):
        matched = False
        for eva in sorted_eva:
            if word[i:i+len(eva)] == eva:
                glyphs.append(EVA_TO_GLYPH[eva])
                i += len(eva)
                matched = True
                break
        if not matched:
            glyphs.append(f'?{word[i]}')
            i += 1
    
    return glyphs


def get_all_eva_text():
    """Get all EVA text as list of words."""
    pages = vd.get_eva_pages()
    words = []
    for page in pages.values():
        for text in page.values():
            text_clean = re.sub(r'[!?<>@$\[\]\d]', '', text)
            for w in re.split(r'[.\-=,\s]', text_clean):
                w = w.strip()
                if w and len(w) > 0:
                    words.append(w)
    return words


def analyze_glyph_frequencies():
    """Analyze frequency of each glyph."""
    words = get_all_eva_text()
    glyph_count = Counter()
    
    for word in words:
        glyphs = eva_to_glyphs(word)
        glyph_count.update(glyphs)
    
    total = sum(glyph_count.values())
    freq = {}
    for gid, count in glyph_count.most_common():
        freq[gid] = {'count': count, 'freq': count / total if total else 0}
    
    return freq


def analyze_positions():
    """Analyze glyph position frequencies (initial, medial, final)."""
    words = get_all_eva_text()
    positions = defaultdict(lambda: {'initial': 0, 'medial': 0, 'final': 0, 'solo': 0})
    
    for word in words:
        glyphs = eva_to_glyphs(word)
        if len(glyphs) == 1:
            positions[glyphs[0]]['solo'] += 1
        elif len(glyphs) >= 2:
            positions[glyphs[0]]['initial'] += 1
            positions[glyphs[-1]]['final'] += 1
            for g in glyphs[1:-1]:
                positions[g]['medial'] += 1
    
    # Convert to frequencies
    result = {}
    for gid, pos in positions.items():
        total = sum(pos.values())
        if total > 0:
            result[gid] = {
                'initial': pos['initial'] / total,
                'medial': pos['medial'] / total,
                'final': pos['final'] / total,
                'solo': pos['solo'] / total,
                'total_occurrences': total
            }
    
    return result


def analyze_bigrams():
    """Analyze glyph bigram frequencies."""
    words = get_all_eva_text()
    bigrams = Counter()
    
    for word in words:
        glyphs = eva_to_glyphs(word)
        for i in range(len(glyphs) - 1):
            bg = (glyphs[i], glyphs[i+1])
            bigrams[bg] += 1
    
    return dict(bigrams.most_common(100))


def analyze_word_lengths():
    """Analyze word length distribution in glyphs."""
    words = get_all_eva_text()
    lengths = Counter()
    
    for word in words:
        glyphs = eva_to_glyphs(word)
        lengths[len(glyphs)] += 1
    
    return dict(sorted(lengths.items()))


def compare_with_scripts():
    """
    Compare Voynich glyph statistics with known scripts.
    Uses positional bias as a key metric.
    """
    pos_data = analyze_positions()
    
    # Calculate positional bias metrics
    initial_bias = []
    final_bias = []
    
    for gid, pos in pos_data.items():
        if pos['total_occurrences'] > 100:
            initial_bias.append((gid, pos['initial']))
            final_bias.append((gid, pos['final']))
    
    # Sort by bias
    initial_bias.sort(key=lambda x: x[1], reverse=True)
    final_bias.sort(key=lambda x: x[1], reverse=True)
    
    # Known script characteristics for comparison
    comparisons = {
        'voynich': {
            'description': 'Voynich manuscript',
            'strong_initial_glyphs': initial_bias[:5],
            'strong_final_glyphs': final_bias[:5],
        },
        'latin_reference': {
            'description': 'Latin/Romance languages typically have...',
            'characteristics': [
                'Vowels distributed throughout words',
                'Final positions favor: s, m, t, r (case endings)',
                'Initial positions: varied consonants',
                'Medium positional bias (0.2-0.4 typical)',
            ]
        },
        'arabic_reference': {
            'description': 'Arabic/Semitic scripts typically have...',
            'characteristics': [
                'Strong positional variants (same letter looks different)',
                'Root consonants in fixed positions',
                'Initial/medial/final forms are visually distinct',
                'Very high positional bias for certain letters',
            ]
        },
        'hebrew_reference': {
            'description': 'Hebrew typically has...',
            'characteristics': [
                'Five letters with final forms',
                'Vowels often not written (consonantal)',
                'Moderate positional bias',
            ]
        }
    }
    
    # Calculate similarity metrics
    results = {}
    
    # Count glyphs with strong positional preference (>50%)
    strong_initial = sum(1 for _, bias in initial_bias if bias > 0.5)
    strong_final = sum(1 for _, bias in final_bias if bias > 0.5)
    strong_medial = sum(1 for gid, pos in pos_data.items() 
                        if pos['total_occurrences'] > 100 and pos['medial'] > 0.5)
    
    voynich_profile = {
        'glyphs_with_strong_initial_bias': strong_initial,
        'glyphs_with_strong_final_bias': strong_final,
        'glyphs_with_strong_medial_bias': strong_medial,
        'top_initial_glyphs': initial_bias[:5],
        'top_final_glyphs': final_bias[:5],
    }
    
    results['voynich_positional_profile'] = voynich_profile
    results['reference_scripts'] = comparisons
    
    # Calculate overall positional rigidity score
    # High score = letters strongly prefer specific positions (like Arabic)
    # Low score = letters appear freely in any position (less constrained)
    total_glyphs = len([g for g in pos_data if pos_data[g]['total_occurrences'] > 100])
    rigidity_score = (strong_initial + strong_final + strong_medial) / (total_glyphs * 3) if total_glyphs else 0
    
    results['positional_rigidity_score'] = rigidity_score
    results['interpretation'] = (
        'HIGH rigidity (>0.3): Like Arabic/Hebrew - positional writing system' if rigidity_score > 0.3
        else 'MEDIUM rigidity (0.15-0.3): Could be Latin-like or unique system' if rigidity_score > 0.15
        else 'LOW rigidity (<0.15): Very free positional distribution'
    )
    
    return results


def assess_eva_bias():
    """
    Assess how EVA design may have introduced bias toward Latin-like results.
    """
    freq = analyze_glyph_frequencies()
    pos = analyze_positions()
    
    # Which EVA letters were assigned to most frequent glyphs?
    most_frequent = sorted(freq.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
    
    # Check EVA vowel assignments
    eva_vowels = {'a', 'e', 'i', 'o'}
    eva_consonants = {'d', 's', 'r', 'l', 'n', 'm', 'k', 't', 'p', 'f', 'q', 'x', 'g'}
    
    vowel_glyph_ids = [gid for gid, info in GLYPH_INVENTORY.items() 
                       if info['eva'] in eva_vowels]
    consonant_glyph_ids = [gid for gid, info in GLYPH_INVENTORY.items() 
                           if info['eva'] in eva_consonants]
    
    # Calculate frequency of "vowels" vs "consonants"
    vowel_freq = sum(freq.get(gid, {}).get('count', 0) for gid in vowel_glyph_ids)
    cons_freq = sum(freq.get(gid, {}).get('count', 0) for gid in consonant_glyph_ids)
    total = vowel_freq + cons_freq
    
    vowel_ratio = vowel_freq / total if total else 0
    
    # Latin typically has ~40% vowels in text
    # If Voynich "vowels" are around 40%, EVA may have been designed to match Latin
    
    bias_assessment = {
        'eva_vowel_frequency': vowel_ratio,
        'expected_latin_vowel_freq': 0.38,
        'difference_from_latin': abs(vowel_ratio - 0.38),
        'most_frequent_glyphs': [
            {
                'glyph_id': gid,
                'eva_letter': GLYPH_INVENTORY.get(gid, {}).get('eva', '?'),
                'is_eva_vowel': GLYPH_INVENTORY.get(gid, {}).get('eva', '') in eva_vowels,
                'count': info['count']
            }
            for gid, info in most_frequent if gid in GLYPH_INVENTORY
        ],
        'bias_indicators': [],
        'conclusion': ''
    }
    
    # Check for bias indicators
    if abs(vowel_ratio - 0.38) < 0.05:
        bias_assessment['bias_indicators'].append(
            'SUSPICIOUS: EVA "vowel" frequency matches Latin exactly')
    
    # Check if frequent glyphs got vowel letters
    freq_got_vowels = sum(1 for gid, _ in most_frequent[:5] 
                          if GLYPH_INVENTORY.get(gid, {}).get('eva', '') in eva_vowels)
    if freq_got_vowels >= 3:
        bias_assessment['bias_indicators'].append(
            f'SUSPICIOUS: {freq_got_vowels}/5 most frequent glyphs assigned EVA vowels')
    
    # Alternative assignment analysis
    # What if we assigned vowels DIFFERENTLY?
    bias_assessment['alternative_analysis'] = {
        'question': 'What if we assigned EVA vowels to DIFFERENT glyphs?',
        'scenarios': [
            {
                'scenario': 'Current EVA (vowels: o, a, e, i)',
                'vowel_freq': vowel_ratio,
                'resembles': 'Latin-like (if ~0.38)'
            },
            {
                'scenario': 'If only G01(o), G02(a) were vowels',
                'vowel_freq': sum(freq.get(g, {}).get('count', 0) 
                                  for g in ['G01', 'G02']) / total if total else 0,
                'resembles': 'More consonantal (Hebrew/Arabic-like)'
            }
        ]
    }
    
    # Final conclusion
    if len(bias_assessment['bias_indicators']) >= 2:
        bias_assessment['conclusion'] = (
            'HIGH BIAS RISK: EVA design appears calibrated to produce Latin-like frequencies. '
            'The Latin-like results may be artifacts of transliteration, not genuine features.'
        )
    elif len(bias_assessment['bias_indicators']) == 1:
        bias_assessment['conclusion'] = (
            'MODERATE BIAS RISK: Some EVA choices may influence results toward Latin patterns.'
        )
    else:
        bias_assessment['conclusion'] = (
            'LOW BIAS RISK: EVA assignments do not obviously favor Latin-like frequencies.'
        )
    
    return bias_assessment


def extract_agnostic_features():
    """Extract features that don't depend on transliteration."""
    words = get_all_eva_text()
    
    # Word length distribution (in glyphs)
    lengths = []
    for word in words:
        glyphs = eva_to_glyphs(word)
        lengths.append(len(glyphs))
    
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    
    # Character diversity per word
    diversity = []
    for word in words:
        glyphs = eva_to_glyphs(word)
        if glyphs:
            unique = len(set(glyphs))
            diversity.append(unique / len(glyphs))
    
    avg_diversity = sum(diversity) / len(diversity) if diversity else 0
    
    # Repetition patterns
    repetitions = Counter()
    for word in words:
        glyphs = eva_to_glyphs(word)
        for i in range(len(glyphs) - 1):
            if glyphs[i] == glyphs[i+1]:
                repetitions[glyphs[i]] += 1
    
    # Line position analysis (first word vs last word patterns)
    pages = vd.get_eva_pages()
    first_words = []
    last_words = []
    
    for page in pages.values():
        for line_text in page.values():
            text_clean = re.sub(r'[!?<>@$\[\]\d]', '', line_text)
            line_words = [w.strip() for w in re.split(r'[.\-=,\s]', text_clean) if w.strip()]
            if line_words:
                first_words.append(line_words[0])
                last_words.append(line_words[-1])
    
    first_word_glyphs = Counter()
    last_word_glyphs = Counter()
    
    for w in first_words:
        glyphs = eva_to_glyphs(w)
        if glyphs:
            first_word_glyphs[glyphs[0]] += 1
    
    for w in last_words:
        glyphs = eva_to_glyphs(w)
        if glyphs:
            last_word_glyphs[glyphs[-1]] += 1
    
    return {
        'word_length': {
            'average_glyphs': avg_len,
            'distribution': dict(Counter(lengths).most_common(10))
        },
        'glyph_diversity': {
            'average': avg_diversity,
            'interpretation': (
                'HIGH (>0.8): Most glyphs in words are unique' if avg_diversity > 0.8
                else 'MEDIUM (0.5-0.8): Mix of unique and repeated glyphs' if avg_diversity > 0.5
                else 'LOW (<0.5): High glyph repetition within words'
            )
        },
        'repetitions': {
            'most_repeated_glyphs': dict(repetitions.most_common(10)),
            'total_adjacent_repetitions': sum(repetitions.values())
        },
        'line_position_patterns': {
            'common_line_initial_glyphs': dict(first_word_glyphs.most_common(10)),
            'common_line_final_glyphs': dict(last_word_glyphs.most_common(10)),
        }
    }


def generate_report(results):
    """Generate markdown report."""
    lines = [
        "# Track 36: Glyph Analysis Report",
        "",
        "## Executive Summary",
        f"- Total unique glyph types: {results['glyph_inventory']['total_unique']}",
        f"- Positional rigidity score: {results['script_comparison']['positional_rigidity_score']:.3f}",
        f"- EVA bias assessment: {results['eva_bias']['conclusion'][:50]}...",
        "",
        "## 1. Glyph Inventory",
        "",
        "| Glyph ID | EVA | Description | Type | Count | Frequency |",
        "|----------|-----|-------------|------|-------|-----------|",
    ]
    
    for shape in results['glyph_inventory']['shapes']:
        freq_info = results['frequencies'].get(shape['id'], {})
        lines.append(
            f"| {shape['id']} | {shape['eva']} | {shape['desc']} | "
            f"{shape['type']} | {freq_info.get('count', 0)} | "
            f"{freq_info.get('freq', 0)*100:.2f}% |"
        )
    
    lines.extend([
        "",
        "## 2. Position Analysis",
        "",
        "Glyphs with strong positional preferences:",
        "",
        "### Strong Initial Position (>50%)",
    ])
    
    for gid, pos in results['positions'].items():
        if pos['initial'] > 0.5 and pos['total_occurrences'] > 100:
            eva = GLYPH_INVENTORY.get(gid, {}).get('eva', '?')
            lines.append(f"- {gid} (EVA: {eva}): {pos['initial']*100:.1f}% initial")
    
    lines.extend([
        "",
        "### Strong Final Position (>50%)",
    ])
    
    for gid, pos in results['positions'].items():
        if pos['final'] > 0.5 and pos['total_occurrences'] > 100:
            eva = GLYPH_INVENTORY.get(gid, {}).get('eva', '?')
            lines.append(f"- {gid} (EVA: {eva}): {pos['final']*100:.1f}% final")
    
    lines.extend([
        "",
        "## 3. Script Comparison",
        "",
        f"**Positional Rigidity Score**: {results['script_comparison']['positional_rigidity_score']:.3f}",
        "",
        f"**Interpretation**: {results['script_comparison']['interpretation']}",
        "",
        "### Comparison with Known Scripts",
        "",
    ])
    
    for script, info in results['script_comparison']['reference_scripts'].items():
        if 'characteristics' in info:
            lines.append(f"**{info['description']}**")
            for char in info['characteristics']:
                lines.append(f"- {char}")
            lines.append("")
    
    lines.extend([
        "",
        "## 4. EVA Bias Assessment",
        "",
        f"**EVA 'Vowel' Frequency**: {results['eva_bias']['eva_vowel_frequency']*100:.1f}%",
        f"**Expected Latin Vowel Frequency**: ~38%",
        "",
        "### Bias Indicators",
    ])
    
    for indicator in results['eva_bias']['bias_indicators']:
        lines.append(f"- ⚠️ {indicator}")
    
    if not results['eva_bias']['bias_indicators']:
        lines.append("- ✓ No strong bias indicators detected")
    
    lines.extend([
        "",
        f"**Conclusion**: {results['eva_bias']['conclusion']}",
        "",
        "### Alternative Assignment Analysis",
        "",
    ])
    
    for scenario in results['eva_bias']['alternative_analysis']['scenarios']:
        lines.append(f"- **{scenario['scenario']}**: Vowel freq = {scenario['vowel_freq']*100:.1f}% → {scenario['resembles']}")
    
    lines.extend([
        "",
        "## 5. Language-Agnostic Features",
        "",
        "### Word Length Distribution",
        f"- Average word length: {results['agnostic_features']['word_length']['average_glyphs']:.2f} glyphs",
        "",
        "Most common word lengths:",
    ])
    
    for length, count in list(results['agnostic_features']['word_length']['distribution'].items())[:5]:
        lines.append(f"- {length} glyphs: {count} words")
    
    lines.extend([
        "",
        "### Glyph Diversity",
        f"- Average diversity: {results['agnostic_features']['glyph_diversity']['average']:.3f}",
        f"- {results['agnostic_features']['glyph_diversity']['interpretation']}",
        "",
        "## 6. Top Bigrams (Glyph Pairs)",
        "",
        "| Rank | Glyph Pair | EVA Equivalent | Count |",
        "|------|------------|----------------|-------|",
    ])
    
    for i, (pair, count) in enumerate(list(results['bigrams'].items())[:15], 1):
        g1, g2 = pair.split('+') if '+' in pair else (pair, '?')
        eva1 = GLYPH_INVENTORY.get(g1, {}).get('eva', g1)
        eva2 = GLYPH_INVENTORY.get(g2, {}).get('eva', g2)
        lines.append(f"| {i} | {g1}+{g2} | {eva1}{eva2} | {count} |")
    
    lines.extend([
        "",
        "## 7. Key Findings",
        "",
        "### Is 'Latin-like' Result Real or Artifact?",
        "",
    ])
    
    # Make determination
    bias_score = len(results['eva_bias']['bias_indicators'])
    rigidity = results['script_comparison']['positional_rigidity_score']
    
    if bias_score >= 2:
        lines.extend([
            "**⚠️ LIKELY ARTIFACT**",
            "",
            "Multiple indicators suggest EVA was designed to produce Latin-like output:",
            "- EVA 'vowel' frequency matches Latin expectations",
            "- Most frequent glyphs assigned vowel letters",
            "",
            "The 'Latin-like' patterns in decoded text may be circular reasoning.",
        ])
    elif rigidity > 0.2:
        lines.extend([
            "**📊 MIXED EVIDENCE**",
            "",
            "The Voynich script shows high positional rigidity, which is:",
            "- More characteristic of Arabic/Hebrew than Latin",
            "- Suggests positional variants or a non-Latin system",
            "",
            "Some Latin-like features may be real, but the script itself is unusual.",
        ])
    else:
        lines.extend([
            "**✓ POSSIBLY GENUINE**",
            "",
            "EVA bias indicators are low, and positional patterns are moderate.",
            "Latin-like features could reflect genuine properties of the underlying text.",
        ])
    
    lines.extend([
        "",
        "### Recommendations",
        "",
        "1. **Test alternative transliterations**: Try assigning EVA letters differently",
        "2. **Focus on positional patterns**: These are less biased by letter names",
        "3. **Compare with shorthand systems**: Voynich may be an abbreviation system",
        "4. **Analyze glyph shapes directly**: Use image analysis, not transliteration",
    ])
    
    return '\n'.join(lines)


def main():
    print("Track 36: Original Glyph Pattern Analysis")
    print("=" * 50)
    
    print("\nAnalyzing glyph frequencies...")
    frequencies = analyze_glyph_frequencies()
    
    print("Analyzing positional patterns...")
    positions = analyze_positions()
    
    print("Analyzing bigrams...")
    bigrams = analyze_bigrams()
    
    print("Comparing with known scripts...")
    script_comparison = compare_with_scripts()
    
    print("Assessing EVA bias...")
    eva_bias = assess_eva_bias()
    
    print("Extracting language-agnostic features...")
    agnostic = extract_agnostic_features()
    
    # Build results
    results = {
        'glyph_inventory': {
            'total_unique': len(GLYPH_INVENTORY),
            'shapes': [
                {'id': gid, 'eva': info['eva'], 'desc': info['desc'], 'type': info['type']}
                for gid, info in GLYPH_INVENTORY.items()
            ]
        },
        'frequencies': frequencies,
        'positions': positions,
        'bigrams': {f"{k[0]}+{k[1]}": v for k, v in bigrams.items()},
        'script_comparison': script_comparison,
        'eva_bias': eva_bias,
        'agnostic_features': agnostic
    }
    
    # Save JSON
    out_json = Path('results/glyph_analysis.json')
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out_json}")
    
    # Generate report
    report = generate_report(results)
    out_md = Path('results/glyph_report.md')
    with open(out_md, 'w') as f:
        f.write(report)
    print(f"Saved: {out_md}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"\nTotal glyphs cataloged: {len(GLYPH_INVENTORY)}")
    print(f"Positional rigidity: {script_comparison['positional_rigidity_score']:.3f}")
    print(f"\nEVA Bias Assessment:")
    print(f"  {eva_bias['conclusion']}")
    print(f"\nEVA 'Vowel' frequency: {eva_bias['eva_vowel_frequency']*100:.1f}%")
    print(f"Expected Latin vowels: ~38%")
    
    if eva_bias['bias_indicators']:
        print("\nBias Indicators Found:")
        for ind in eva_bias['bias_indicators']:
            print(f"  ⚠️ {ind}")
    
    print(f"\nWord length (avg): {agnostic['word_length']['average_glyphs']:.2f} glyphs")
    print(f"Glyph diversity: {agnostic['glyph_diversity']['average']:.3f}")
    
    # Key question answer
    print("\n" + "=" * 50)
    print("KEY QUESTION: Is 'Latin-like' result real or artifact?")
    print("=" * 50)
    
    if len(eva_bias['bias_indicators']) >= 2:
        print("\n⚠️ LIKELY TRANSLITERATION ARTIFACT")
        print("EVA appears calibrated to produce Latin-like frequencies.")
        print("Different letter assignments could produce Arabic/Hebrew-like results.")
    else:
        print("\n📊 MIXED EVIDENCE")
        print("Some Latin-like features may be genuine,")
        print("but EVA design could still introduce subtle bias.")


if __name__ == "__main__":
    main()
