# Track 36: Glyph Analysis Report

## Executive Summary
- Total unique glyph types: 24
- Positional rigidity score: 0.295
- EVA bias assessment: MODERATE BIAS RISK: Some EVA choices may influence...

## 1. Glyph Inventory

| Glyph ID | EVA | Description | Type | Count | Frequency |
|----------|-----|-------------|------|-------|-----------|
| G01 | o | small circle | basic | 25589 | 14.07% |
| G02 | a | circle with tail left | basic | 15775 | 8.67% |
| G03 | e | short stroke / c-shape | basic | 20544 | 11.29% |
| G04 | y | circle with descender | basic | 17691 | 9.72% |
| G05 | i | single stroke / minim | basic | 12066 | 6.63% |
| G06 | n | double stroke / two minims | basic | 7531 | 4.14% |
| G07 | m | triple stroke / three minims | basic | 1125 | 0.62% |
| G08 | ch | bench (c + h) | bench | 11015 | 6.05% |
| G09 | sh | tall bench (s + h) | bench | 4500 | 2.47% |
| G10 | t | gallows type 1 | gallows | 7408 | 4.07% |
| G11 | k | gallows type 2 (with loop) | gallows | 10044 | 5.52% |
| G12 | p | gallows type 3 (curved top) | gallows | 2818 | 1.55% |
| G13 | f | gallows type 4 (double curved) | gallows | 791 | 0.43% |
| G14 | d | loop with descender | special | 13073 | 7.19% |
| G15 | s | tall s-shape | special | 2975 | 1.64% |
| G16 | r | small r-shape | special | 7838 | 4.31% |
| G17 | l | tall stroke | special | 12029 | 6.61% |
| G18 | q | special form (rare) | special | 5430 | 2.98% |
| G19 | x | cross-like (rare) | special | 35 | 0.02% |
| G20 | g | special g-form (rare) | special | 433 | 0.24% |
| G21 | cth | benched gallows type 1 | ligature | 949 | 0.52% |
| G22 | ckh | benched gallows type 2 | ligature | 909 | 0.50% |
| G23 | cph | benched gallows type 3 | ligature | 217 | 0.12% |
| G24 | cfh | benched gallows type 4 | ligature | 74 | 0.04% |

## 2. Position Analysis

Glyphs with strong positional preferences:

### Strong Initial Position (>50%)
- G13 (EVA: f): 56.4% initial
- G08 (EVA: ch): 53.0% initial
- G09 (EVA: sh): 70.1% initial
- G21 (EVA: cth): 51.2% initial
- G23 (EVA: cph): 58.5% initial
- G12 (EVA: p): 65.1% initial
- G18 (EVA: q): 98.4% initial

### Strong Final Position (>50%)
- G04 (EVA: y): 86.2% final
- G16 (EVA: r): 71.4% final
- G06 (EVA: n): 80.2% final
- G07 (EVA: m): 92.4% final

## 3. Script Comparison

**Positional Rigidity Score**: 0.295

**Interpretation**: MEDIUM rigidity (0.15-0.3): Could be Latin-like or unique system

### Comparison with Known Scripts

**Latin/Romance languages typically have...**
- Vowels distributed throughout words
- Final positions favor: s, m, t, r (case endings)
- Initial positions: varied consonants
- Medium positional bias (0.2-0.4 typical)

**Arabic/Semitic scripts typically have...**
- Strong positional variants (same letter looks different)
- Root consonants in fixed positions
- Initial/medial/final forms are visually distinct
- Very high positional bias for certain letters

**Hebrew typically has...**
- Five letters with final forms
- Vowels often not written (consonantal)
- Moderate positional bias


## 4. EVA Bias Assessment

**EVA 'Vowel' Frequency**: 50.8%
**Expected Latin Vowel Frequency**: ~38%

### Bias Indicators
- ⚠️ SUSPICIOUS: 3/5 most frequent glyphs assigned EVA vowels

**Conclusion**: MODERATE BIAS RISK: Some EVA choices may influence results toward Latin patterns.

### Alternative Assignment Analysis

- **Current EVA (vowels: o, a, e, i)**: Vowel freq = 50.8% → Latin-like (if ~0.38)
- **If only G01(o), G02(a) were vowels**: Vowel freq = 28.4% → More consonantal (Hebrew/Arabic-like)

## 5. Language-Agnostic Features

### Word Length Distribution
- Average word length: 4.69 glyphs

Most common word lengths:
- 5 glyphs: 9210 words
- 4 glyphs: 8356 words
- 3 glyphs: 6182 words
- 6 glyphs: 6172 words
- 7 glyphs: 3019 words

### Glyph Diversity
- Average diversity: 0.917
- HIGH (>0.8): Most glyphs in words are unique

## 6. Top Bigrams (Glyph Pairs)

| Rank | Glyph Pair | EVA Equivalent | Count |
|------|------------|----------------|-------|
| 1 | G14+G04 | dy | 6866 |
| 2 | G02+G05 | ai | 6670 |
| 3 | G01+G11 | ok | 6129 |
| 4 | G05+G06 | in | 5990 |
| 5 | G01+G17 | ol | 5755 |
| 6 | G18+G01 | qo | 5292 |
| 7 | G03+G03 | ee | 5160 |
| 8 | G03+G14 | ed | 5057 |
| 9 | G08+G03 | che | 5019 |
| 10 | G05+G05 | ii | 4659 |
| 11 | G14+G02 | da | 4083 |
| 12 | G03+G04 | ey | 4049 |
| 13 | G11+G03 | ke | 3922 |
| 14 | G01+G10 | ot | 3896 |
| 15 | G03+G01 | eo | 3508 |

## 7. Key Findings

### Is 'Latin-like' Result Real or Artifact?

**📊 MIXED EVIDENCE**

The Voynich script shows high positional rigidity, which is:
- More characteristic of Arabic/Hebrew than Latin
- Suggests positional variants or a non-Latin system

Some Latin-like features may be real, but the script itself is unusual.

### Recommendations

1. **Test alternative transliterations**: Try assigning EVA letters differently
2. **Focus on positional patterns**: These are less biased by letter names
3. **Compare with shorthand systems**: Voynich may be an abbreviation system
4. **Analyze glyph shapes directly**: Use image analysis, not transliteration