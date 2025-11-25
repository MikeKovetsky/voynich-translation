# Root-Based Decoding Report

## Summary
- Roots analyzed: 643
- Hebrew mappings attempted: 53
- Overall score: 100.0%
- Verdict: **PARTIAL**

## Root Dictionary (Top 20)

| Root | Frequency | Hebrew Candidate | Meaning | Confidence |
|------|-----------|-----------------|---------|------------|
| chr | 4747 | ch-r | hole/pierce (chor) | 70.0% |
| ckh | 4412 | - | - | 0.0% |
| qkd | 3893 | - | - | 0.0% |
| hck | 2748 | - | - | 0.0% |
| shl | 2440 | sh-l | extract/draw out (shol) | 70.0% |
| qkl | 2235 | - | - | 0.0% |
| qkn | 2172 | - | - | 0.0% |
| chs | 1768 | - | - | 0.0% |
| hct | 1580 | - | - | 0.0% |
| shr | 1561 | sh-r-sh | root (shoresh) | 70.0% |
| qkc | 1553 | - | - | 0.0% |
| hdn | 1311 | - | - | 0.0% |
| qkr | 1308 | - | - | 0.0% |
| qtd | 1232 | - | - | 0.0% |
| lsh | 1149 | - | - | 0.0% |
| hdr | 1108 | - | - | 0.0% |
| lkd | 1075 | - | - | 0.0% |
| qtc | 1060 | - | - | 0.0% |
| hdl | 1024 | - | - | 0.0% |
| cph | 1019 | - | - | 0.0% |

## Hebrew Mappings

| Root | Hebrew | Meaning | Score | Frequency |
|------|--------|---------|-------|-----------|
| chr | chor | hole/pierce | 60.0% | 4747 |
| shl | shol | extract/draw | 50.0% | 2440 |
| shr | shoresh | root | 70.0% | 1561 |
| rch | ruach | spirit/wind | 60.0% | 534 |
| shs | shoresh | root | 70.0% | 533 |
| pln | ploni | someone/plant | 30.0% | 429 |
| hch | sh-ch-r | black (shachor) | 50.0% | 405 |
| chk | zachar | male/remember | 50.0% | 239 |
| tch | tuach | smear/plaster | 40.0% | 215 |
| pch | perach | flower | 70.0% | 198 |
| kch | koach | strength | 50.0% | 197 |
| hdm | d-m | blood (dam) | 50.0% | 187 |
| qts | ayin-ts | tree (ets) | 50.0% | 184 |
| chd | chad | sharp/one | 50.0% | 169 |
| cht | chittah | wheat | 40.0% | 156 |

## Sample Page Decoding (f2v)

f2v is described as "Water lily" - botanical page with herbal content.

### Line 1
**Voynich:** kooiin cheo pchor otaiin o dain chordair shty

**Roots found:** pch→flower, chr→hole/pierce, chr→hole/pierce

**Decoded attempt:** kooiin cheo pchor(flower/hole/pierce) otaiin o dain chordair(hole/pierce) shty

### Line 2
**Voynich:** kooiin otaiin chordair shty

**Roots found:** chr→hole/pierce

**Decoded attempt:** kooiin otaiin chordair(hole/pierce) shty

### Line 3
**Voynich:** kaoiin otaiin chordair shty

**Roots found:** chr→hole/pierce

**Decoded attempt:** kaoiin otaiin chordair(hole/pierce) shty

### Line 4
**Voynich:** kooiin cheo pchor otaiin chordair shty

**Roots found:** pch→flower, chr→hole/pierce, chr→hole/pierce

**Decoded attempt:** kooiin cheo pchor(flower/hole/pierce) otaiin chordair(hole/pierce) shty

### Line 5
**Voynich:** kaoiin cheo pchor otaiin chordair shty

**Roots found:** pch→flower, chr→hole/pierce, chr→hole/pierce

**Decoded attempt:** kaoiin cheo pchor(flower/hole/pierce) otaiin chordair(hole/pierce) shty

### Line 6
**Voynich:** cheo pchor otaiin o dain chordair shty

**Roots found:** pch→flower, chr→hole/pierce, chr→hole/pierce

**Decoded attempt:** cheo pchor(flower/hole/pierce) otaiin o dain chordair(hole/pierce) shty

### Line 7
**Voynich:** kcho kchy sho shol qotcho loeees qotychor daiin

**Roots found:** kch→strength, kch→strength, shl→extract/draw, tch→smear/plaster, tch→smear/plaster

**Decoded attempt:** kcho(strength) kchy(strength) sho shol(extract/draw) qotcho(smear/plaster) loeees qotychor(smear/plaster/hole/pierce) daiin

### Line 8
**Voynich:** sho shol qotcho loeees qotychor daiin

**Roots found:** shl→extract/draw, tch→smear/plaster, tch→smear/plaster, chr→hole/pierce

**Decoded attempt:** sho shol(extract/draw) qotcho(smear/plaster) loeees qotychor(smear/plaster/hole/pierce) daiin

### Line 9
**Voynich:** sho shol qotcho loeees qotychor daiin

**Roots found:** shl→extract/draw, tch→smear/plaster, tch→smear/plaster, chr→hole/pierce

**Decoded attempt:** sho shol(extract/draw) qotcho(smear/plaster) loeees qotychor(smear/plaster/hole/pierce) daiin

### Line 10
**Voynich:** kchy sho shol qotsho loeees qotychor daiin

**Roots found:** kch→strength, shl→extract/draw, qts→tree (ets), tsh→weak, ts→tree (ets)

**Decoded attempt:** kchy(strength) sho shol(extract/draw) qotsho(tree (ets)/weak/tree (ets)) loeees qotychor(smear/plaster/hole/pierce) daiin


## Validation

| Metric | Score |
|--------|-------|
| Botanical context match | 13.8% |
| Semantic coherence | 87.4% |

### Interpretation

- **Botanical context match** measures how many decoded lines contain botanical terms (root, leaf, flower, etc.)
- **Semantic coherence** measures whether the same roots appear consistently (lower unique/total ratio = more coherent)

## Verdict: PARTIAL

### Key Findings

1. **Root Pattern Evidence**: The Voynich text shows clear 3-consonant clustering that resembles Semitic root patterns.

2. **Hebrew Mapping Results**:
   - 53 roots could be mapped to Hebrew botanical/medical terms
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
