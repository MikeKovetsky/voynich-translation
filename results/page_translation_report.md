# Page Translation Attempt: f2v

## Summary
- Total sentences/lines: 8
- Readable sentences (>50% coherence): 3
- Overall coherence: 37.9%

## Best Sentence
- Voynich: `otchy chor lshy chol chody chodainchcthy daiin`
- Latin: `atcs ex lbs ad radix cil`
- English: The ?noun prep: ex ?noun prep: ad noun: radix
- Coherence: 59.3%

## Sentence-by-Sentence Analysis

### Line 1
**Voynich:** `kooiin cheo pchor otaiin o dain chordair shty`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| kooiin | naaiin | naaiin | ? | 10% |
| cheo | cia | cia | ? | 10% |
| pchor | pcex | pcex | ? | 10% |
| otaiin | atiiin | atiiin | ? | 10% |
| o | a | ad | prep: ad | 70% |
| dain | dein | Latin | Latin preposition 'de' (of/from) with case endings | 80% |
| chordair | cexdeir | ex | prep: ex | 70% |
| shty | bts | bts | ?noun | 20% |

**Grammar Parse:**
- Subject: shty
- Verb: (none)
- Object: (none)
- Prepositions: [('o', 'dain'), ('chordair', 'shty')]

**Latin Reconstruction:** `bts ad Latin ex bts`
**English:** The ?noun prep: ad Latin preposition 'de' (of/from) with case endings prep: ex ?noun
**Coherence Score:** 36.8%
- Factors: high_conf_words: 1/8, has_subject, has_prepositions: 2, latin_words: 2/5

---

### Line 2
**Voynich:** `kcho kchy sho shol qotcho loeees qotychor daiin`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| kcho | nca | nca | ? | 10% |
| kchy | ncs | ncs | ?noun | 20% |
| sho | ba | ba | ? | 10% |
| shol | bil | bil | ? | 10% |
| qotcho | quatca | quatca | ? | 10% |
| loeees | laiiix | laiiix | ? | 10% |
| qotychor | quatscex | quatscex | ? | 10% |
| daiin | deii | de + acc. marker | of/from (+ object) | 80% |

**Grammar Parse:**
- Subject: kchy
- Verb: (none)
- Object: (none)

**Latin Reconstruction:** `ncs`
**English:** The ?noun
**Coherence Score:** 18.8%
- Factors: high_conf_words: 1/8, has_subject, latin_words: 0/1

---

### Line 3
**Voynich:** `otchy chor lshy chol chody chodainchcthy daiin`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| otchy | atcs | atcs | ?noun | 20% |
| chor | cex | ex | prep: ex | 70% |
| lshy | lbs | lbs | ?noun | 20% |
| chol | cil | cil | ? | 10% |
| chody | cadr | ad | prep: ad | 70% |
| chodainchcthy | cadiincrcs | radix | noun: radix | 50% |
| daiin | deii | de + acc. marker | of/from (+ object) | 80% |

**Grammar Parse:**
- Subject: otchy
- Verb: chol
- Object: (none)
- Prepositions: [('chor', 'lshy'), ('chody', 'chodainchcthy')]

**Latin Reconstruction:** `atcs ex lbs ad radix cil`
**English:** The ?noun prep: ex ?noun prep: ad noun: radix
**Coherence Score:** 59.3%
- Factors: high_conf_words: 1/7, has_subject, has_verb, has_prepositions: 2, latin_words: 3/6

---

### Line 4
**Voynich:** `sho cholo cheor chodaiin`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| sho | ba | ba | ? | 10% |
| cholo | cila | cila | ? | 10% |
| cheor | ciex | ciex | ? | 10% |
| chodaiin | cadiiin | radix | noun: radix | 50% |

**Grammar Parse:**
- Subject: chodaiin
- Verb: (none)
- Object: (none)

**Latin Reconstruction:** `radix`
**English:** The noun: radix
**Coherence Score:** 35.0%
- Factors: high_conf_words: 0/4, has_subject, latin_words: 1/1

---

### Line 5
**Voynich:** `kchor shy daiiin chckhoys shey dor chol daiin`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| kchor | ncex | ncex | ? | 10% |
| shy | bs | bs | ?noun | 20% |
| daiiin | deiiin | Latin | Latin preposition 'de' (of/from) with case endings | 80% |
| chckhoys | crnasx | crnasx | ? | 10% |
| shey | bir | bir | ? | 10% |
| dor | dex | de | prep: de | 70% |
| chol | cil | cil | ? | 10% |
| daiin | deii | de + acc. marker | of/from (+ object) | 80% |

**Grammar Parse:**
- Subject: shy
- Verb: chol
- Object: (none)
- Prepositions: [('dor', 'chol')]

**Latin Reconstruction:** `bs de cil cil`
**English:** The ?noun
**Coherence Score:** 57.5%
- Factors: high_conf_words: 2/8, has_subject, has_verb, has_prepositions: 1, latin_words: 1/4

---

### Line 6
**Voynich:** `dor chol chor chol keol chy chtydaiin otchor chan`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| dor | dex | de | prep: de | 70% |
| chol | cil | cil | ? | 10% |
| chor | cex | ex | prep: ex | 70% |
| chol | cil | cil | ? | 10% |
| keol | niil | niil | ? | 10% |
| chy | cs | cs | ?noun | 20% |
| chtydaiin | ctsdiiin | ctsdiiin | ? | 10% |
| otchor | atcex | atcex | ? | 10% |
| chan | cen | ren | noun: ren | 50% |

**Grammar Parse:**
- Subject: chy
- Verb: chol
- Object: (none)
- Prepositions: [('dor', 'chol'), ('chor', 'chol')]

**Latin Reconstruction:** `cs de cil ex cil cil`
**English:** The ?noun
**Coherence Score:** 51.7%
- Factors: high_conf_words: 0/9, has_subject, has_verb, has_prepositions: 2, latin_words: 2/6

---

### Line 7
**Voynich:** `daiin chotchey qoteeey chokeoschees chr cheaiin`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| daiin | deii | de + acc. marker | of/from (+ object) | 80% |
| chotchey | catcir | catcir | ? | 10% |
| qoteeey | quatiiir | quatiiir | ? | 10% |
| chokeoschees | caniaxciix | caniaxciix | ? | 10% |
| chr | cr | cr | ? | 10% |
| cheaiin | ciiiin | ciiiin | ? | 10% |

**Grammar Parse:**
- Subject: (none)
- Verb: (none)
- Object: (none)

**Latin Reconstruction:** `de + acc. marker catcir quatiiir caniaxciix cr ciiiin`
**English:** [translation unclear]
**Coherence Score:** 7.2%
- Factors: high_conf_words: 1/6, latin_words: 1/9

---

### Line 8
**Voynich:** `chokoishe chor cheol chol dolody`

**Word-by-word decode:**
| EVA | Decoded | Latin | English | Confidence |
|-----|---------|-------|---------|------------|
| chokoishe | canaibi | sanat | verb: sanat | 60% |
| chor | cex | ex | prep: ex | 70% |
| cheol | ciil | ciil | ? | 10% |
| chol | cil | cil | ? | 10% |
| dolody | diladr | diladr | ? | 10% |

**Grammar Parse:**
- Subject: (none)
- Verb: chol
- Object: (none)
- Prepositions: [('chor', 'cheol')]

**Latin Reconstruction:** `ex ciil cil`
**English:** [translation unclear]
**Coherence Score:** 36.7%
- Factors: high_conf_words: 0/5, has_verb, has_prepositions: 1, latin_words: 1/3

---

## Honest Assessment

**MARGINALLY READABLE**: A few sentences may contain meaningful content.

### What Works
- 3 sentences with coherence >50%
- 6 high-confidence word matches

### Problems Identified
- 37 words decoded with <50% confidence

### Next Steps
1. Expand high-confidence vocabulary through more anchor words
2. Improve verb identification from context patterns
3. Cross-reference with specific plant illustrations
4. Try different pages or sections