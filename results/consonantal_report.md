# Consonantal Writing Hypothesis Analysis

## Executive Summary

Testing whether Voynich uses a CONSONANTAL writing system where vowels are
omitted or minimally represented (like Hebrew, Arabic, or medieval shorthand).

**Verdict: SUPPORTS CONSONANTAL** (Score: 0.75)

## 1. Vowel/Consonant Distribution

| Metric | Voynich | Expected Latin | Expected Hebrew | Expected Arabic |
|--------|---------|----------------|-----------------|-----------------|
| Vowel Ratio | 0.3681 | 0.38 | 0.0 | 0.10 |

**Analysis:** Latin-like

The vowel ratio of 0.3681 is lower than typical Latin text.

## 2. Consonant Cluster Analysis

- Total clusters found: 9281
- Unique clusters: 1121
- Maximum cluster length: 10
- Average cluster length: 2.81

### Top Consonant Clusters
- `ch`: 946 occurrences
- `dy`: 754 occurrences
- `sh`: 482 occurrences
- `pl`: 426 occurrences
- `lk`: 276 occurrences
- `ly`: 192 occurrences
- `lch`: 190 occurrences
- `pch`: 189 occurrences
- `tch`: 188 occurrences
- `nt`: 185 occurrences
- `kch`: 162 occurrences
- `yk`: 148 occurrences
- `cth`: 141 occurrences
- `ld`: 137 occurrences
- `ry`: 128 occurrences

### Phonotactic Violations
6458 violations of Latin phonotactics found.
Many violations suggest non-Latin phonotactics

## 3. Latin Consonant Skeleton Matches

Found 1137 potential matches when comparing Voynich consonant skeletons
to Latin botanical/medical vocabulary.

### Sample Matches
| alom | lm | oleum | lm |
| plantotal | plnttl | planta | plnt |
| plantotal | plnttl | luna | ln |
| plantctchy | plntctchy | planta | plnt |
| plantctchy | plntctchy | luna | ln |
| tarar | trr | terra | trr |
| plantykeeol | plntykl | planta | plnt |
| plantykeeol | plntykl | luna | ln |
| plantchol | plntchl | planta | plnt |
| plantchol | plntchl | luna | ln |
| plantydaiin | plntydn | planta | plnt |
| plantydaiin | plntydn | luna | ln |
| plantsa | plnts | planta | plnt |
| plantsa | plnts | luna | ln |
| dalom | dlm | oleum | lm |

## 4. Hebrew Consonant Skeleton Matches

Found 547 potential matches with Hebrew consonant roots.

### Sample Matches
| sprayraraldy | spryrrldy | pri | fruit |
| yteodam | ytdm | dam | blood |
| plantsa | plnts | ets | tree |
| eetees | ts | ets | tree |
| otshchor | tshchr | ets | tree |
| qopor | qpr | pri | fruit |
| oldaim | ldm | dam | blood |
| daiioam | dm | dam | blood |
| plantosain | plntsn | ets | tree |
| tshod | tshd | ets | tree |
| oteosaiin | tsn | ets | tree |
| plantotshor | plnttshr | ets | tree |
| orcho | rch | ruakh | spirit/wind |
| oltshsey | ltshsy | ets | tree |
| okoldm | kldm | dam | blood |

## 5. Word Length Analysis

| Metric | Value |
|--------|-------|
| Latin average word length | 6.6 |
| Latin consonant skeleton avg | 3.9 |
| Voynich average word length | 4.69 |

**Match:** YES

Voynich (4.69) vs predicted consonantal Latin (3.90)

## 6. Vowel Reconstruction Attempts

Sample attempts to reconstruct Latin words by adding vowels:

- **daiin** → skeleton: `dn` → possible: none
- **plant** → skeleton: `plnt` → possible: planta, planto, luna
- **ol** → skeleton: `l` → possible: planta, planto, flos
- **chedy** → skeleton: `chdy` → possible: none
- **aiin** → skeleton: `n` → possible: medicina, medicin, planta
- **shedy** → skeleton: `shdy` → possible: none
- **chol** → skeleton: `chl` → possible: none
- **or** → skeleton: `r` → possible: radix, redux, herba
- **ar** → skeleton: `r` → possible: radix, redux, herba
- **chey** → skeleton: `chy` → possible: none

## 7. Evidence Summary

- High vowel ratio contradicts consonantal
- Long consonant clusters support consonantal
- Many phonotactic violations suggest non-Latin base
- Found 1137 Latin skeleton matches
- Found 547 Hebrew skeleton matches
- Word length matches consonantal Latin prediction

## Conclusion

The consonantal hypothesis is supported by the evidence.

### Implications

If consonantal hypothesis is supported:

- Voynich may encode consonants only, requiring vowel inference for reading
- Simple substitution ciphers will always fail
- Need to look for Semitic-style root patterns
- The high EVA "vowel" frequency may indicate these glyphs have other functions

