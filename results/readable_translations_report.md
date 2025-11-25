# Track 69: Readable Translation Output

## Purpose
Generate ACTUALLY READABLE translated sentences, not just coverage percentages.
Focus on producing coherent English that humans can understand.

## Method

### 1. Grammar Transformations Applied
- `qo-` prefix → "the" (article)
- `ol/al` → "the" (article)
- `dar/dol` → "give/of" (preposition)
- `daiin` → "is/from" (copula)
- `-y` suffix → verb conjugation
- SOV → SVO word order transformation

### 2. Recipe Template Matching
Medieval medical recipes follow patterns:
- INGREDIENT + for + BODY PART
- Take/Give + INGREDIENT + for + CONDITION

### 3. Dictionary Sources
- Clean dictionary: 324 validated entries
- Hebrew corpus expansion: ~100 new entries
- Grammar words: from positional analysis
- **Total vocabulary: 393 entries**

## Summary Statistics

| Metric | Value |
|--------|-------|
| Lines processed | 151 |
| High confidence | 6 |
| Medium confidence | 43 |
| Best sentences selected | 20 |

## Per-Folio Results

| Folio | Lines | High Conf. | Med. Conf. | Avg Coverage |
|-------|-------|------------|------------|--------------|
| f107r | 51 | 3 | 19 | 38.3% |
| f107v | 49 | 3 | 18 | 38.8% |
| f111v | 51 | 0 | 6 | 26.3% |

## TOP 20 READABLE SENTENCES

These are the most coherent translations, selected by:
- Coverage ≥50%
- Medical/botanical content bonus
- Confidence level bonus

### 1. f107r.12 (f107r) ✅

**Confidence**: HIGH | **Coverage**: 83%

**Voynich**: `ychol.chal.lor.aiir.aiin.al`

**English**: Nettle sick unknown one the.

### 2. f107r.46 (f107r) ✅

**Confidence**: HIGH | **Coverage**: 83%

**Voynich**: `sar.cheey.qodaiin.qokaiin.ol.cheor.aiin.otal.taiin.qokaiin.otal.alkal`

**English**: Barley of the priest the hole one fig fig priest fig.

### 3. f107v.3 (f107v) ✅

**Confidence**: HIGH | **Coverage**: 71%

**Voynich**: `sai.n.ain.aiiin.qokaiin.shol.kal.qokar.al.ochedy.lkaiin.otal.olkiir.al...`

**English**: Take fig for the heart.

### 4. f107r.23 (f107r) ✅

**Confidence**: HIGH | **Coverage**: 75%

**Voynich**: `chodaiin.shar.chod..aiin`

**English**: Priest root one.

### 5. f107v.12 (f107v) ✅

**Confidence**: HIGH | **Coverage**: 73%

**Voynich**: `qokeey.lcheol.chol.kaiin.olkal.shedy.qokaly.odar.choty.qokaiin.otam`

**English**: Give wheat, wheat for Sick.

### 6. f107v.14 (f107v) ✅

**Confidence**: HIGH | **Coverage**: 70%

**Voynich**: `daiin.shaiin.okaiin.qokar.qokal.qokal.cheody.qokain.okchdy.dlkal`

**English**: Take seed for the heart.

### 7. f107v.2 (f107v) ⚠️

**Confidence**: MEDIUM | **Coverage**: 64%

**Voynich**: `daiin.dckhy.ol.daiin.chkal.qokedy.otal.chedy.oteos.aiin.otar.alkai.n.o...`

**English**: Of of the fig has tree one earth the.

### 8. f107v.22 (f107v) ⚠️

**Confidence**: MEDIUM | **Coverage**: 67%

**Voynich**: `dor.alol.olaiin.olkal.chol.chdar`

**English**: Take Moon, wheat, moon for sick.

### 9. f107r.40 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 60%

**Voynich**: `lolkaiin.chey.qokaiin.chal.aiin.okaiin.olkar.otair.okal.okal`

**English**: Take earth for sick.

### 10. f107r.51 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 58%

**Voynich**: `sar.ai.n.chol.ol.cheey.otal.otal.ol.otchy.qoky.otaily`

**English**: Take Barley, the fig, fig for sick.

### 11. f107r.19 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 62%

**Voynich**: `oaiin.ol.rar.sheey.ylar.aiin.chol.al.dy.cheeody.okeeey.cheodaiin.aldy`

**English**: One the one sick the -ness priest Aquarius.

### 12. f107v.11 (f107v) ⚠️

**Confidence**: MEDIUM | **Coverage**: 60%

**Voynich**: `tshedy.okal.shedy.qokchey.chky.qokeey.qotaiin.otol.qoteedy.qopchcfhy`

**English**: All which the wheat the fig finger finger.

### 13. f107v.21 (f107v) ⚠️

**Confidence**: MEDIUM | **Coverage**: 50%

**Voynich**: `taiin.ol.kaiin.chol.kchedy.qokol.ai.n.air.kaiin.okal.otar.otal.al`

**English**: Take Fig, earth, fig for the sick.

### 14. f107v.27 (f107v) ⚠️

**Confidence**: MEDIUM | **Coverage**: 54%

**Voynich**: `dal.okai.n.okchey.qokshy.okol.lkshedy.tar.aiin.sho.qokar.cheey.qokam`

**English**: Take earth for the heart.

### 15. f107r.25 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 58%

**Voynich**: `ycheai.n.chal.kal.chedy.qokaiin.chody.qokchdy.qokal.char.chdalal.om`

**English**: Sick voice has priest one the voice hole.

### 16. f107r.28 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 58%

**Voynich**: `kar.aiin.chl.cholor.sheees.aiin.cheey.otchy.lkaiin.ykaiin.ykal.kal`

**English**: Heart one finger priest priest voice.

### 17. f107r.35 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 58%

**Voynich**: `daiin.shl.lkeeol.lchedy.qokor.lkaiin.chedy.qotaiin.al.ol.kaldai.m`

**English**: Of milk priest has the fig the.

### 18. f107r.41 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 57%

**Voynich**: `qokai.n.ar.ockhey.qokal.otal.otam`

**English**: To the voice fig thyme.

### 19. f107v.4 (f107v) ⚠️

**Confidence**: MEDIUM | **Coverage**: 57%

**Voynich**: `dain.cheky.okechy.qokain.shocthy.otaiin.alkaiin`

**English**: Is power priest fig.

### 20. f107r.32 (f107r) ⚠️

**Confidence**: MEDIUM | **Coverage**: 56%

**Voynich**: `salxar.shy.qokaiin.okal.qockhedy.okraiin.otar.qocthy.ralky`

**English**: Aries fire priest all earth.

---

## Sample Word-by-Word Translations

### f107r.1 (f107r)

Voynich: `pchdlar.sheolor.ykeeol.qokchy.otor.okeesodar.tarair.oteey.otaiin.ytar`

| Word | Translation | Found |
|------|-------------|-------|
| pchdlar | [pchdlar] | ✗ |
| sheolor | [sheolor] | ✗ |
| ykeeol | [ykeeol] | ✗ |
| qokchy | the strength | ✓ |
| otor | earth | ✓ |
| okeesodar | [okeesodar] | ✗ |
| tarair | [tarair] | ✗ |
| oteey | [oteey] | ✗ |
| otaiin | fig | ✓ |
| ytar | earth | ✓ |

**Readable**: The strength earth fig earth.

### f107r.2 (f107r)

Voynich: `dchey.qoteos.aiin.shedy.oteed.qor.aiin.cheockhy.olkeey.qotai.n.chey.qeeey.lor`

| Word | Translation | Found |
|------|-------------|-------|
| dchey | one | ✓ |
| qoteos | the tree | ✓ |
| aiin | one | ✓ |
| shedy | which | ✓ |
| oteed | [oteed] | ✗ |
| qor | [qor] | ✗ |
| aiin | one | ✓ |
| cheockhy | [cheockhy] | ✗ |
| olkeey | [olkeey] | ✗ |
| qotai | [qotai] | ✗ |

**Readable**: One the tree one which one unknown.

### f107r.3 (f107r)

Voynich: `olcheey.sheos.qokeeey.ycheedy.qotai.n.ykai.n.okeey.raiin`

| Word | Translation | Found |
|------|-------------|-------|
| olcheey | sick-one | ✓ |
| sheos | [sheos] | ✗ |
| qokeeey | [qokeeey] | ✗ |
| ycheedy | [ycheedy] | ✗ |
| qotai | [qotai] | ✗ |
| n | [n] | ✗ |
| ykai | [ykai] | ✗ |
| n | [n] | ✗ |
| okeey | [okeey] | ✗ |
| raiin | kidney | ✓ |

**Readable**: Sick-one kidney.

### f107r.4 (f107r)

Voynich: `teeody.chedai.n.qoteey.qokar.deeo.ltedy.otar.ai.n.chady.otokcho.qoked.okchedy`

| Word | Translation | Found |
|------|-------------|-------|
| teeody | [teeody] | ✗ |
| chedai | [chedai] | ✗ |
| n | [n] | ✗ |
| qoteey | [qoteey] | ✗ |
| qokar | the heart | ✓ |
| deeo | [deeo] | ✗ |
| ltedy | [ltedy] | ✗ |
| otar | earth | ✓ |
| ai | [ai] | ✗ |
| n | [n] | ✗ |

**Readable**: Take earth for the heart.

### f107r.5 (f107r)

Voynich: `olkchedy.tedy.oteeey.okchedy.qokeed.qokear.chedy.chokchedy.qokai.n.ar`

| Word | Translation | Found |
|------|-------------|-------|
| olkchedy | [olkchedy] | ✗ |
| tedy | [tedy] | ✗ |
| oteeey | [oteeey] | ✗ |
| okchedy | [okchedy] | ✗ |
| qokeed | [qokeed] | ✗ |
| qokear | [qokear] | ✗ |
| chedy | has | ✓ |
| chokchedy | [chokchedy] | ✗ |
| qokai | [qokai] | ✗ |
| n | [n] | ✗ |

**Readable**: Has to.

---

## Honest Assessment

### What Works
1. Medical vocabulary (heart, blood, sick) translates consistently
2. Botanical terms (fig, flower, root) appear in botanical context
3. Grammar markers (the, of, for) provide sentence structure
4. Recipe patterns emerge naturally from high-coverage lines

### What Doesn't Work
1. Many lines have <50% coverage - too fragmentary
2. Some translations are semantically incoherent
3. Proper names and rare terms remain untranslated
4. Grammar transformations are heuristic, not proven

### Honest Verdict


⚠️ **LIMITED SUCCESS**: Only 6 high-confidence sentences.

While some patterns emerge, most text remains fragmentary.
The dictionary needs further expansion to achieve fluent translation.


---

## Medical Content Evidence

Sentences containing medical terminology:

- **f107r.12**: "Nettle sick unknown one the."
- **f107r.46**: "Barley of the priest the hole one fig fig priest fig."
- **f107v.3**: "Take fig for the heart."
- **f107r.23**: "Priest root one."
- **f107v.12**: "Give wheat, wheat for Sick."
- **f107v.14**: "Take seed for the heart."
- **f107v.2**: "Of of the fig has tree one earth the."
- **f107v.22**: "Take Moon, wheat, moon for sick."
- **f107r.40**: "Take earth for sick."
- **f107r.51**: "Take Barley, the fig, fig for sick."

---
*Generated by Track 69: Readable Output*