# Grammar Baseline Report: Positional Analysis

## Methodology
- **Verbs**: Ends with `-y` or is `shol`.
- **Nouns**: Starts with `o-` or `c-`.
- **Analysis**: 
  1. Probability of being at Start given Word Type.
  2. VN vs NV structure at line start.

### Astrological ($I=A)
**Positional Bias** (Baseline P(Start) = 25.1%):
- **Verbs**: 82/351 at start (23.4%). Delta: **-1.7%**
- **Nouns**: 76/264 at start (28.8%). Delta: **+3.7%**
  -> Verbs are neutral
  -> Nouns are neutral

**Structure** (First 2 words):
- VN: 15 (9.8%)
- NV: 17 (11.1%)
  -> NV > VN (Supports Narrative/SVO)

### Biological ($I=B)
**Positional Bias** (Baseline P(Start) = 10.8%):
- **Verbs**: 327/3588 at start (9.1%). Delta: **-1.7%**
- **Nouns**: 78/1295 at start (6.0%). Delta: **-4.8%**
  -> Verbs are neutral
  -> Nouns AVOID start

**Structure** (First 2 words):
- VN: 54 (6.7%)
- NV: 36 (4.5%)
  -> VN > NV (Supports Imperative)

### Cosmological ($I=C)
**Positional Bias** (Baseline P(Start) = 13.5%):
- **Verbs**: 143/972 at start (14.7%). Delta: **+1.2%**
- **Nouns**: 124/831 at start (14.9%). Delta: **+1.4%**
  -> Verbs are neutral
  -> Nouns are neutral

**Structure** (First 2 words):
- VN: 38 (11.8%)
- NV: 33 (10.2%)
  -> VN > NV (Supports Imperative)

### Herbal ($I=H)
**Positional Bias** (Baseline P(Start) = 11.7%):
- **Verbs**: 431/3749 at start (11.5%). Delta: **-0.2%**
- **Nouns**: 262/3063 at start (8.6%). Delta: **-3.1%**
  -> Verbs are neutral
  -> Nouns AVOID start

**Structure** (First 2 words):
- VN: 172 (10.6%)
- NV: 88 (5.4%)
  -> VN > NV (Supports Imperative)

### Section P ($I=P)
**Positional Bias** (Baseline P(Start) = 15.1%):
- **Verbs**: 127/805 at start (15.8%). Delta: **+0.7%**
- **Nouns**: 115/837 at start (13.7%). Delta: **-1.4%**
  -> Verbs are neutral
  -> Nouns are neutral

**Structure** (First 2 words):
- VN: 23 (8.2%)
- NV: 17 (6.1%)
  -> VN > NV (Supports Imperative)

### Recipes (Quire 20) ($I=S)
**Positional Bias** (Baseline P(Start) = 9.1%):
- **Verbs**: 309/4325 at start (7.1%). Delta: **-2.0%**
- **Nouns**: 123/2553 at start (4.8%). Delta: **-4.3%**
  -> Verbs AVOID start
  -> Nouns AVOID start

**Structure** (First 2 words):
- VN: 100 (9.2%)
- NV: 75 (6.9%)
  -> VN > NV (Supports Imperative)

### Text ($I=T)
**Positional Bias** (Baseline P(Start) = 13.1%):
- **Verbs**: 55/611 at start (9.0%). Delta: **-4.1%**
- **Nouns**: 25/391 at start (6.4%). Delta: **-6.7%**
  -> Verbs AVOID start
  -> Nouns AVOID start

**Structure** (First 2 words):
- VN: 16 (8.8%)
- NV: 9 (5.0%)
  -> VN > NV (Supports Imperative)

### Zodiac ($I=Z)
**Positional Bias** (Baseline P(Start) = 22.4%):
- **Verbs**: 138/524 at start (26.3%). Delta: **+3.9%**
- **Nouns**: 160/523 at start (30.6%). Delta: **+8.2%**
  -> Verbs are neutral
  -> Nouns PREFER start (Subject?)

**Structure** (First 2 words):
- VN: 7 (6.0%)
- NV: 28 (24.1%)
  -> NV > VN (Supports Narrative/SVO)

## Conclusion
1. **Recipe Imperative Hypothesis**: Weakly supported. While `VN` structures are slightly more common than `NV` (9.2% vs 6.9%), 'Verbs' defined as ending in `-y` generally **avoid** the start of lines relative to random chance (Delta -2.0%). This suggests either the definition of 'Verb' is incomplete or the Imperative structure is not strictly line-initial.
2. **Narrative Structure**: Herbal and Biological sections also show a slight preference for `VN` over `NV`, contradicting the expectation of a distinct SVO structure for narratives compared to recipes. Nouns consistently **avoid** the start of lines in these sections.
3. **Zodiac/Astrological Anomaly**: These sections show a distinct `NV > VN` pattern and Nouns **prefer** the start, likely reflecting label-heavy content.
