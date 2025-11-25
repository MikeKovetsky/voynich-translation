# Track 59: Clean Dictionary Translation Report

## Purpose
Re-run translation using ONLY validated dictionary entries (no conflicts).

## Summary
- **Dictionary size**: 324 entries (clean, no conflicts)
- **Total coverage**: 38.9%
- **Coherent sentences**: 86

## Comparison: Track 53 vs Track 59

| Metric | Track 53 | Track 59 | Delta |
|--------|----------|----------|-------|
| Dictionary entries | 409 | 324 | -85 |
| Translation coverage | 50.9% | 38.9% | -12.0% |
| Coherent sentences | 104 | 86 | -18 |

### Interpretation

⚠️ **Coverage dropped by 12.0%** - this is expected since we removed conflicting entries.
⚠️ Coherence dropped by 18 sentences.

## Per-Folio Results

| Folio | Words | Translated | Rate |
|-------|-------|------------|------|
| f111v | 699 | 242 | 34.6% |
| f107r | 534 | 220 | 41.2% |
| f107v | 510 | 216 | 42.4% |

## Best Translations (Highest Coherence)

### f107v.47 (f107v)
- **Coherence**: 0.65
- **Quality**: mostly_translated
- **Voynich**: `ycheey.qokeey.okeoteey.qokey.qokey.qokeey.daiin.y.okoey.odain`
- **Translation**: the (+ noun) the (+ noun) the (+ noun) the (+ noun) of the/from -s/-i (plural/genitive) fig

### f107v.46 (f107v)
- **Coherence**: 0.60
- **Quality**: mostly_translated
- **Voynich**: `soain.aiin.chey.qol.aiin.al.chedy.kedy.qoteey.oteey.qokeey.lkain`
- **Translation**: one verbal/adjectival one to the is/has verb verb form the (+ noun) verb form the (+ noun) priest/cohen

### f107r.46 (f107r)
- **Coherence**: 0.60
- **Quality**: readable_medical
- **Voynich**: `sar.cheey.qodaiin.qokaiin.ol.cheor.aiin.otal.taiin.qokaiin.otal.alkal`
- **Translation**: barley verb form the of the/from priest/cohen the/of hole/pierce chor one fig priest/cohen

### f107v.2 (f107v)
- **Coherence**: 0.60
- **Quality**: readable_medical
- **Voynich**: `daiin.dckhy.ol.daiin.chkal.qokedy.otal.chedy.oteos.aiin.otar.alkai.n.ol`
- **Translation**: of the/from the/of of the/from the verb form is/has verb tree one earth the/of

### f107r.12 (f107r)
- **Coherence**: 0.58
- **Quality**: mostly_translated
- **Voynich**: `ychol.chal.lor.aiir.aiin.al`
- **Translation**: sick choleh unknown one to the

### f107r.34 (f107r)
- **Coherence**: 0.57
- **Quality**: partially_coherent
- **Voynich**: `pairar.al.aro.lkeey.qotal.cheotai.n.dar.okaiin.otaiin.otar.opaim`
- **Translation**: to the verb form the (+ noun) fig earth

### f107v.30 (f107v)
- **Coherence**: 0.56
- **Quality**: partially_coherent
- **Voynich**: `okai.n.ol.okaiin.lkeody.otaiin.chol.lkaiin.lkeeey.qokaiin.chey.qoky`
- **Translation**: the/of fig sick choleh priest/cohen priest/cohen verbal/adjectival the (+ noun)

### f107r.17 (f107r)
- **Coherence**: 0.55
- **Quality**: mostly_translated
- **Voynich**: `sair.chey.losaiin.chey`
- **Translation**: barley verbal/adjectival verbal/adjectival

### f111v.16 (f111v)
- **Coherence**: 0.55
- **Quality**: partially_coherent
- **Voynich**: `qokai.n.sheol.qokai.n.chckhey.lchedy.okar.al.qotal.shedy.otai.n.far.aiin.am`
- **Translation**: verb unknown to the the (+ noun) which/that flower one

### f107v.12 (f107v)
- **Coherence**: 0.54
- **Quality**: mostly_translated
- **Voynich**: `qokeey.lcheol.chol.kaiin.olkal.shedy.qokaly.odar.choty.qokaiin.otam`
- **Translation**: the (+ noun) sick choleh which/that verb unknown priest/cohen thyme

### f107r.23 (f107r)
- **Coherence**: 0.54
- **Quality**: partially_coherent
- **Voynich**: `chodaiin.shar.chod..aiin`
- **Translation**: root shoresh one

### f111v.25 (f111v)
- **Coherence**: 0.51
- **Quality**: fragmented
- **Voynich**: `tair.alchedar.shykaiin.chd.y`
- **Translation**: earth -s/-i (plural/genitive)

### f111v.10 (f111v)
- **Coherence**: 0.50
- **Quality**: partially_coherent
- **Voynich**: `soiin.shed.qoksheo.lor.cheo.lol.aiin.shey.qokai.n.chear.qoteol.shcthy.ldy`
- **Translation**: seed unknown verb form one verb form hole/pierce chor verb form verb

### f111v.5 (f111v)
- **Coherence**: 0.49
- **Quality**: mostly_translated
- **Voynich**: `qokeed.o.aiin.otedy.qokedy.chedy.......qokeey.qokeedy.qokeol.shedy.qotedal.lol`
- **Translation**: one the verb form is/has verb the (+ noun) the garlic which/that verb form

### f111v.19 (f111v)
- **Coherence**: 0.47
- **Quality**: mostly_translated
- **Voynich**: `qokaiin.cheal.tai.n.qokai.n.shey.qokai.n.char.shcthey.qoky.chy.qokaiin`
- **Translation**: priest/cohen sick verb form hole/pierce chor the (+ noun) verbal/adjectival priest/cohen

## Sample Sentence Analysis

| Quality | Count |
|---------|-------|
| Readable medical | 19 |
| Partially coherent | 13 |
| Fragmented | 119 |

## Quality Assessment

⚠️ **MODERATE**: Partial readability achieved.

### Does the output make sense as medical text?

Evidence of medical content:

- f107v.2: "of the/from the/of of the/from the verb form is/has verb tre..."
- f107r.12: "sick choleh unknown one to the..."
- f107r.34: "to the verb form the (+ noun) fig earth..."
- f107v.30: "the/of fig sick choleh priest/cohen priest/cohen verbal/adje..."
- f111v.16: "verb unknown to the the (+ noun) which/that flower one..."

## Honest Verdict


**Coverage dropped by 12.0%**, but this is EXPECTED.

The removed conflicting entries DID contribute to coverage, but their meanings
were unreliable. The current 38.9% coverage is MORE HONEST.

**Real progress**: 38.9% of words can be translated with CONFIDENCE.


---
*Generated by Track 59: Clean Dictionary Translation*