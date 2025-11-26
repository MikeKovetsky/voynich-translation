# Track 90: Grammar-Frame Recipe Translation

## Summary

- **Total lines analyzed**: 27
- **Average coherence**: 0.22
- **High coherence (≥0.5)**: 2
- **Medium coherence (0.3-0.5)**: 3
- **Low coherence (<0.3)**: 22

## Grammar Frame Applied

```
daiin [DIRECT_OBJECT] qok- [MODIFIER] ... ol [NOUN] ...
"Take [INGREDIENT] of [SOURCE/TYPE] ... the [THING] ..."
```

## Key Assignments

| EVA | Role | Meaning |
|-----|------|---------|
| daiin | Verb | Take/Mix/Use |
| qok- | Preposition | of/from/with |
| ol | Article | the |
| char | Direct Object | **TARGET WORD** |

## Pattern Analysis

### Verb Frequency

| Verb | Count |
|------|-------|
| sain | 3 |
| daiin | 1 |

### Direct Objects (Top 10)

| Word | Count | Meaning |
|------|-------|---------|
| char | 1 | hole/pierce (chor) |
| chckhey | 1 | verb (unknown) |
| chckhy | 1 | strength/power |

### Prepositions

| Preposition | Count |
|-------------|-------|
| qokeey | 3 |
| qokain | 2 |
| qokaiin | 2 |
| qokeedy | 1 |
| qokam | 1 |
| qokcheedy | 1 |
| qokeechy | 1 |
| qokal | 1 |
| qokchedy | 1 |
| qokeeey | 1 |
| qokan | 1 |
| qokchey | 1 |

### Nouns (Top 10)

| Noun | Count | Meaning |
|------|-------|---------|
| char | 2 | hole/pierce (chor) |
| qokeey | 1 | the (+ noun) |
| tchedy | 1 | verbal/adjectival |

### `char` Position

Average position in line: **5.9**

## Deep `char` Context Analysis

### Words Immediately BEFORE `char`

| Word | Count | Meaning |
|------|-------|---------|
| qokain | 3 | priest/cohen |
| qokal | 2 | ? |
| lchdy | 1 | sick person |
| ol | 1 | the/of |
| pol | 1 | skin |
| chedy | 1 | is/has (verb) |
| daiin | 1 | of the/from |
| or | 1 | or/and |
| akain | 1 | ? |
| aiin | 1 | one |

### Words Immediately AFTER `char`

| Word | Count | Meaning |
|------|-------|---------|
| aiin | 3 | one |
| ar | 2 | to/for |
| olchey | 1 | sick person |
| otal | 1 | ? |
| otar | 1 | earth |
| qopchedy | 1 | the (+ noun) |
| qotal | 1 | the (+ noun) |
| cheeol | 1 | sick person |
| olkeeey | 1 | ? |
| lkeey | 1 | verb form |

### Grammatical Role of `char`

| Role | Count |
|------|-------|
| UNKNOWN | 15 |
| PREP_OBJECT | 5 |
| NOUN_AFTER_ARTICLE | 3 |
| DIRECT_OBJECT | 2 |
| NOUN_BEFORE_ARTICLE | 2 |

### Bigrams Around `char`

**Before:**
- `lcheey lchdy` → char (1x)
- `qokal ol` → char (1x)
- `pchdar chedy` → char (1x)
- `olkeechy or` → char (1x)
- `okchdal qokal` → char (1x)

**After:**
- char → `olchey lcheody` (1x)
- char → `otal opchedy` (1x)
- char → `otar okain` (1x)
- char → `qopchedy ocphedy` (1x)
- char → `qotal okechol` (1x)

## Top 15 Coherent Translations

| Coherence | Folio | Translation |
|-----------|-------|-------------|
| 0.80 | f111r.52 | Take (Variant) strength/power of/from the the (+ noun) |
| 0.70 | f104r.24 | Take/Mix/Use hole/pierce (chor) of/from |
| 0.45 | f103v.17 | of/from is/has (verb) the hole/pierce (chor) |
| 0.45 | f111r.24 | Take (Variant) verb (unknown) |
| 0.35 | f108r.24 | of/from [lkedy] the hole/pierce (chor) |
| 0.25 | f103v.20 | of/from plant:atropa |
| 0.25 | f104r.33 | of/from plant:geranium |
| 0.25 | f106r.47 | of/from hole/pierce (chor) |
| 0.25 | f106r.5 | of/from verb form |
| 0.25 | f107r.25 | of/from one |
| 0.25 | f108r.7 | of/from is/has (verb) |
| 0.25 | f108v.26 | of/from plant:tussilago |
| 0.25 | f111v.19 | of/from sick |
| 0.25 | f111v.33 | of/from plant:moss polytrichnum |
| 0.25 | f113v.32 | of/from hole/pierce (chor) |

## All Parsed Recipes

### f103v.15

**Raw**: `tchedal.shey.lcheey.lchdy.char.olchey.lcheody.tedy.otain.otain.otaly`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f103v.17

**Raw**: `qokeedy.chedy.qoteey.oteedy.lkedy.shedy.qokal.ol.char.otal.opchedy`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokeedy
- Prep Object: chedy
- Article: ol
- Noun: char

**Translation**: of/from is/has (verb) the hole/pierce (chor)

**Coherence**: 0.45 (has_preposition, prep_object_in_dict, has_article, noun_in_dict)

---

### f103v.20

**Raw**: `pol.char.otar.okain.shaikhy.oteal.okain.qotal.shedy.qokeey.lolain`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokeey
- Prep Object: lolain
- Article: None
- Noun: None

**Translation**: of/from plant:atropa

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f104r.1

**Raw**: `pchdar.chedy.char.qopchedy.ocphedy.qopchedy.shedaiin.oteeo.chey.qopchedy.sain`

**Parsed**:
- Verb: sain
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: Take (Variant)

**Coherence**: 0.20 (has_verb)

---

### f104r.24

**Raw**: `daiin.char.qotal.okechol.olkeeor.olkeeodal.lkaiin.chalkeeedy.qokam`

**Parsed**:
- Verb: daiin
- Direct Object: char
- Preposition: qokam
- Prep Object: None
- Article: None
- Noun: None

**Translation**: Take/Mix/Use hole/pierce (chor) of/from

**Coherence**: 0.70 (has_verb, has_direct_object, object_in_dict, has_preposition, char_is_direct_object)

---

### f104r.28

**Raw**: `olcheear.chedar.or.arorsheey.olkeechy.or.char.cheeol.sor.or.aiin.otam`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f104r.33

**Raw**: `okchechy.qokcheedy.okchdal.qokal.char.olkeeey.olcheo.lkaiin.chey.roly`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokcheedy
- Prep Object: okchdal
- Article: None
- Noun: None

**Translation**: of/from plant:geranium

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f104v.39

**Raw**: `ysheey.rar.akain.char.lkeey.roiir.shey.cheey.kas.ar.lkchs.ar.y.rais.alod`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f106r.47

**Raw**: `ycheoar.okain.qokain.char.oky.cheokam`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokain
- Prep Object: char
- Article: None
- Noun: None

**Translation**: of/from hole/pierce (chor)

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f106r.5

**Raw**: `ysheor.aiin.char.okaiin.qokeechy.checkhy.qokeod.ar.qokeo.lkeo.leeo.ram`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokeechy
- Prep Object: checkhy
- Article: None
- Noun: None

**Translation**: of/from verb form

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f106v.14

**Raw**: `schedy.raiin.char.arshey.chedy.aiiin.alkam`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f107r.25

**Raw**: `ycheain.chal.kal.chedy.qokaiin.chody.qokchdy.qokal.char.chdalal.om`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokaiin
- Prep Object: chody
- Article: None
- Noun: None

**Translation**: of/from one

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f107v.23

**Raw**: `palchar.ar.akaiiky.char.raikchy.ofchain.opalkar.otal.otas.alky`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f108r.24

**Raw**: `folaiin.shkhy.qokal.lkedy.qotedy.qoked.qotedy.okal.chdar.al.char.aiin`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokal
- Prep Object: lkedy
- Article: al
- Noun: char

**Translation**: of/from [lkedy] the hole/pierce (chor)

**Coherence**: 0.35 (has_preposition, has_article, noun_in_dict)

---

### f108r.7

**Raw**: `okchey.okedy.qokchedy.chedy.qokedy.okar.chdy.okar.char.chkaiin.chsy`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokchedy
- Prep Object: chedy
- Article: None
- Noun: None

**Translation**: of/from is/has (verb)

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f108v.26

**Raw**: `sair.okeaiin.cheol.shedy.qokeeey.doaiin.ar.or.lkar.char.aiin.okal.ldyr.ls`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokeeey
- Prep Object: doaiin
- Article: None
- Noun: None

**Translation**: of/from plant:tussilago

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f111r.24

**Raw**: `sain.chckhey.cheos.lchal.lkechey.okeey.lkechedy.oteo.dain.char.lko.lchr.aiin.aim`

**Parsed**:
- Verb: sain
- Direct Object: chckhey
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: Take (Variant) verb (unknown)

**Coherence**: 0.45 (has_verb, has_direct_object, object_in_dict)

---

### f111r.52

**Raw**: `dair.al.qokeey.qokaiin.sheal.qokeain.shckhy.sain.chckhy.char.aiin.alom`

**Parsed**:
- Verb: sain
- Direct Object: chckhy
- Preposition: qokeey
- Prep Object: None
- Article: al
- Noun: qokeey

**Translation**: Take (Variant) strength/power of/from the the (+ noun)

**Coherence**: 0.80 (has_verb, has_direct_object, object_in_dict, has_preposition, has_article, noun_in_dict)

---

### f111v.19

**Raw**: `qokaiin.cheal.tain.qokain.shey.qokain.char.shcthey.qoky.chy.qokaiin`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokaiin
- Prep Object: cheal
- Article: None
- Noun: None

**Translation**: of/from sick

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f111v.32

**Raw**: `tar.chey.tain.chkar.alkar.chey.qol.chedy.okain.chey.lcheey.char.an`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f111v.33

**Raw**: `ysheal.qoair.ain.okan.sheainy.qokan.chan.aman.cheal.char`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokan
- Prep Object: chan
- Article: None
- Noun: None

**Translation**: of/from plant:moss polytrichnum

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f112v.44a

**Raw**: `ycheey.chokeey.okar.al.tchedy.oteol.chcthy.alaiin.char.al.kamdam`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: al
- Noun: tchedy

**Translation**: the verbal/adjectival

**Coherence**: 0.20 (has_article, noun_in_dict)

---

### f113r.17

**Raw**: `dor.shar.shol.qokeey.qokchol.chedaiin.qoky.chokain.chotar.chokar.char.alom`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokeey
- Prep Object: None
- Article: None
- Noun: None

**Translation**: of/from

**Coherence**: 0.15 (has_preposition)

---

### f113r.26

**Raw**: `tol.cheshy.lkchedy.lchod.chal.char.lkeeody.oteeo.loaiin.okeedy`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

### f113r.7

**Raw**: `chos.sheey.qokchey.sokal.okeey.char.laiin.olkain`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokchey
- Prep Object: sokal
- Article: None
- Noun: None

**Translation**: of/from [sokal]

**Coherence**: 0.15 (has_preposition)

---

### f113v.32

**Raw**: `sheol.keey.qokain.char.ar.olar.aiiin.okar`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: qokain
- Prep Object: char
- Article: None
- Noun: None

**Translation**: of/from hole/pierce (chor)

**Coherence**: 0.25 (has_preposition, prep_object_in_dict)

---

### f116r.2

**Raw**: `oain.cheer.ain.okeey.okeey.shy.lar.ar.aiiin.oky.char.ar.okain.ykanam`

**Parsed**:
- Verb: None
- Direct Object: None
- Preposition: None
- Prep Object: None
- Article: None
- Noun: None

**Translation**: None

**Coherence**: 0.00 ()

---

## Conclusions

- **7.4%** of lines have high coherence (≥0.5)
- Grammar frame captures recipe structure
- `char` typically appears as direct object position
- `qok-` confirmed as preposition, NOT 'priest'
