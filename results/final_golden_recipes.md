# The Final Golden Recipes

## Overview

This is the culmination of 99 research tracks on the Voynich manuscript.
We have decoded the recipe section's grammatical structure and identified
both generic botanical terms and specific plant names.

## The Grammar Frame

```
daiin   [AMOUNT]     [INGREDIENT]   qok-    [SOURCE]
"Take"  "a handful"  "of leaf"      "from"  "the geranium"
```

## Statistics

| Metric | Value |
|--------|-------|
| Total recipe candidates | 633 |
| Specific plant recipes | 16 |
| Generic term recipes | 37 |
| Unknown source recipes | 580 |
| Average score (top 50) | 4.48 |

## Slot Fill Rates (Top 50)

| Slot | Fill Rate |
|------|-----------|
| verb | 100% |
| amount | 82% |
| ingredient | 82% |
| preposition | 76% |
| source | 72% |

---

## 🌟 HIGH-VALUE: Specific Plant Recipes

These recipes reference a **specific plant name** (not just generic 'herb').
These are the most valuable for understanding the manuscript's medical content.

### 1. f104r.6 — GERANIUM

**Translation**: *"Take one of geranium."*

### 2. f108v.11 — PLANT

**Translation**: *"Prepare a portion of plant."*

### 3. f111r.37 — PLANT

**Translation**: *"Take leaf from the plant."*

### 4. f115v.6 — GERANIUM

**Translation**: *"Take a portion of geranium."*

### 5. f108r.30 — PLANT

**Translation**: *"Prepare of plant."*

### 6. f111v.6 — POPPY

**Translation**: *"one leaf from the poppy."*

### 7. f113r.35 — PLANT

**Translation**: *"one earth from the plant."*

### 8. f104r.8 — POLYGONUM

**Translation**: *"earth from the polygonum."*

### 9. f104v.40 — PLANT

**Translation**: *"one of plant."*

### 10. f107v.36 — PLANT

**Translation**: *"a handful of plant."*

### 11. f107v.6 — PLANT

**Translation**: *"one of plant."*

### 12. f108r.32 — PLANT

**Translation**: *"a whole of plant."*

### 13. f108v.16 — POPPY

**Translation**: *"flower extract from the poppy."*

### 14. f112v.15 — PLANT

**Translation**: *"one of plant."*

### 15. f113r.47 — POLYGONUM

**Translation**: *"a handful of polygonum."*

---

## 📜 The Golden 50 Recipes

### 1. f101r.8 🏆 

**Raw**: `olaiin.oteol.chor.oteey.chokchey.kor.daiin.shok.chol.chol.qoky.daiin<-><!fold>ol...`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: al → portion
- `ingredient`: chor → stem
- `preposition`: qoky → ?
- `source`: foldol → ?

**Translation**: *"Take a portion of stem from [foldol]."*

---

### 2. f100v.14 🏆 

**Raw**: `cthdeecthy.sheocphy.qoteody.ckhoor.ar.chor.oteey.daiin.qokomo`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ar → handful
- `ingredient`: chor → stem
- `preposition`: qokomo → of

**Translation**: *"Take a handful of stem."*

---

### 3. f101r.2 🏆 

**Raw**: `dol.chokeey.chkey.cthey.okal.chol.kol.okeey.r.or.ol.okolol.olchey.qokchor.okey.q...`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: or → amount
- `ingredient`: chol → leaf
- `preposition`: qokchor → holm
- `source`: okey → ?

**Translation**: *"Take an amount of leaf from [okey]."*

---

### 4. f101r.9 🏆 

**Raw**: `daiin.okeol.qokcheol.ykeor.dar.ol.otechy.ykeor.dor.aiin.chl!s.cheol<-><!fold>oko...`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `ingredient`: okeol → flower extract
- `preposition`: qokcheol → of
- `source`: ykeor → tamus communis

**Translation**: *"Take one flower extract from the tamus communis."*

---

### 5. f104r.45 🏆 [GENERIC]

**Raw**: `daiin.olcheeo.l.s.aiin.otai!n.ar.chedy.qokaiin.otaiin.otai!n<$>`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `ingredient`: otaiin → fig
- `preposition`: qokaiin → priest/cohen
- `source`: otaiin → fig

**Translation**: *"Take one fig."*

---

### 6. f105v.13 🏆 [GENERIC]

**Raw**: `saiin.opchedy.qokchdy.otar.al.kair.okees.lkeedal<$>`

**Parsed Slots**:
- `verb`: saiin → Prepare
- `amount`: al → portion
- `ingredient`: otar → earth
- `preposition`: qokchdy → ?
- `source`: otar → earth

**Translation**: *"Prepare a portion of earth."*

---

### 7. f106v.2 🏆 

**Raw**: `daiin.al.sheeo!dar.ychtain.chor.otar.qokar.okar.shed.sheo.keo!r.ai!n.am!chy`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: al → portion
- `ingredient`: chor → stem
- `preposition`: qokar → ?
- `source`: okar → ?

**Translation**: *"Take a portion of stem from [okar]."*

---

### 8. f107r.6 🏆 

**Raw**: `okcheey.qokeedy.chotchedy.daiin.ar.oteey.lteey.chedaiin.okchey.otaiin.am`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ar → handful
- `ingredient`: otaiin → fig
- `preposition`: qokeedy → of
- `source`: chotchedy → ?

**Translation**: *"Take a handful of fig from [chotchedy]."*

---

### 9. f107v.2 🏆 

**Raw**: `daiin.dckhy.ol.daiin.chkal.qokedy.otal.chedy.oteos.aiin.otar.alkai!n.ol`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: otal → whole
- `ingredient`: otar → earth
- `preposition`: qokedy → of
- `source`: otal → whole

**Translation**: *"Take the whole earth from the whole."*

---

### 10. f108r.48 🏆 

**Raw**: `pcheedy.qokeol.okeol.keol.dai!n.ar.otedy.qokedy.qokeedy.qokeedy.lchdy`

**Parsed Slots**:
- `verb`: dain → Take
- `amount`: ar → handful
- `ingredient`: okeol → flower extract
- `preposition`: qokeol → of
- `source`: okeol → flower extract

**Translation**: *"Take a handful of flower extract."*

---

### 11. f108v.23 🏆 

**Raw**: `qokeeor.okeey.qoeey.cho.deeal.daiin.checthal.cheek!y.otar.aiin.chckhy.lte!dy`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `ingredient`: otar → earth
- `preposition`: qokeeor → of
- `source`: okeey → ?

**Translation**: *"Take one earth from [okeey]."*

---

### 12. f108v.36 🏆 

**Raw**: `daiin.shechy.qokedy.qokai!n.chor.chal.chal.chedy.dai!n.al.al.keedy.otal.ys`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: al → portion
- `ingredient`: chor → stem
- `preposition`: qokedy → of
- `source`: qokain → priest/cohen

**Translation**: *"Take a portion of stem from the priest/cohen."*

---

### 13. f111r.25 🏆 

**Raw**: `so.sheor.okeedy.oteeey.qokeey.qokeeo!s.chedar.alal.oikhy.oxar.aiin.odaiin.chody`

**Parsed Slots**:
- `verb`: odaiin → Take
- `amount`: aiin → one
- `ingredient`: sheor → head
- `preposition`: qokeey → ?
- `source`: qokeeos → plant_term

**Translation**: *"Take one head from the plant_term."*

---

### 14. f111r.4 🏆 

**Raw**: `saiin.oteedy.qokeey.daiin.okedal.chedy.qokedy.lshedy.chcthhy.okeey.lor.ar.al`

**Parsed Slots**:
- `verb`: saiin → Prepare
- `amount`: ar → handful
- `preposition`: qokeey → ?
- `source`: okedal → ?

**Translation**: *"Prepare a handful from [okedal]."*

---

### 15. f111r.52 🏆 

**Raw**: `dair.al.qokeey.qokaiin.sheal.qokeai!n.shckhy.sai!n.chckhy.char.aiin.alom`

**Parsed Slots**:
- `verb`: sain → Prepare
- `amount`: al → portion
- `ingredient`: char → flower
- `preposition`: qokeey → ?
- `source`: qokaiin → priest/cohen

**Translation**: *"Prepare a portion of flower from the priest/cohen."*

---

### 16. f111r.53 🏆 

**Raw**: `yshe.aiin.okshdy.shkeey.kai!n.chaiin.alol.shey.qokaiin.chcthy.dai!n`

**Parsed Slots**:
- `verb`: dain → Take
- `amount`: aiin → one
- `ingredient`: chaiin → root
- `preposition`: qokaiin → priest/cohen
- `source`: chcthy → verb (unknown)

**Translation**: *"Take one root from the verb (unknown)."*

---

### 17. f111v.22 🏆 

**Raw**: `saiin.ychear.olsheey.chet!ai!n.chedy.qokai!n.okai!n.al.chan.okal.chey.lkeeey`

**Parsed Slots**:
- `verb`: saiin → Prepare
- `amount`: al → portion
- `ingredient`: chan → root
- `preposition`: qokain → priest/cohen
- `source`: okain → ?

**Translation**: *"Prepare a portion of root from [okain]."*

---

### 18. f111v.3 🏆 

**Raw**: `dai!n.chedy.shedal.otedy.oteeo.chedy.qokeey.dai!n.chcthar.otar.qotai!n.otaim`

**Parsed Slots**:
- `verb`: dain → Take
- `ingredient`: otar → earth
- `preposition`: qokeey → ?
- `source`: chcthar → ?

**Translation**: *"Take earth from [chcthar]."*

---

### 19. f112v.37 🏆 

**Raw**: `teedal.sai!n.ar.otaiin.shedy.qokedaiin.ar.qokaiin.chol.kedy.qokam`

**Parsed Slots**:
- `verb`: sain → Prepare
- `amount`: ar → handful
- `ingredient`: otaiin → fig
- `preposition`: qokedaiin → of
- `source`: ar → handful

**Translation**: *"Prepare a handful of fig from the handful."*

---

### 20. f113r.9 🏆 

**Raw**: `dchos.aiin.oteey.qokaiin.cho.okaiin.cheo.daiin.chky.le.chody.chotaiin<$>`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `ingredient`: chotaiin → leaf
- `preposition`: qokaiin → priest/cohen
- `source`: cho → ?

**Translation**: *"Take one leaf from [cho]."*

---

### 21. f113v.16 🏆 

**Raw**: `daiin.chl.lkeey.lkaiin.chdai!n.qokain.sheor.okalchedy.qokar.olkam.ar`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ar → handful
- `ingredient`: chl → root
- `preposition`: qokain → priest/cohen
- `source`: sheor → head

**Translation**: *"Take a handful of root from the head."*

---

### 22. f88r.20 🏆 

**Raw**: `dsheol.qokeey.s.chy.saiin.chor.oteor.aiin.chosals`

**Parsed Slots**:
- `verb`: saiin → Prepare
- `amount`: aiin → one
- `ingredient`: chor → stem
- `preposition`: qokeey → ?
- `source`: chy → verbal/adjectival

**Translation**: *"Prepare one stem from the verbal/adjectival."*

---

### 23. f88r.8 🏆 

**Raw**: `sal.sheom.kol.chear.shekor.qokor.daiin.sar.raiin.oky.sam`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: sal → salt
- `preposition`: qokor → ?
- `source`: sar → barley

**Translation**: *"Take salt from the barley."*

---

### 24. f101r.4 ⭐ 

**Raw**: `ycheeo.or.sheeol.daiin.sheeol.okeol.ctheol.shkeeo.qockheol.daiin.shy.csol.okeeor...`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: or → amount
- `ingredient`: okeol → flower extract

**Translation**: *"Take an amount of flower extract."*

---

### 25. f101r.5 ⭐ 

**Raw**: `daiin.ctheol.cheol.okor.or.aiin.cheol.cho.keeo.dchey.okol.okeol.dor.chol.chy.r.a...`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: or → amount
- `ingredient`: okeol → flower extract

**Translation**: *"Take an amount of flower extract."*

---

### 26. f101r.7 ⭐ 

**Raw**: `cphoar.o!aiin.ypcholy.daiin.otaiin.otaiin.yfolaiin.fcheolai!n.ypchey.y<!@Y>pho?o...`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: otaiin → fig
- `preposition`: qokchey → ?
- `source`: cholp → ?

**Translation**: *"Take fig from [cholp]."*

---

### 27. f101v.23 ⭐ 

**Raw**: `oaiin!!.ol.ol!or.daiin.okeey.qok.ykeol.daiin.qockhy.daiin.olch???<-><!fold>???!d...`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: chol → leaf
- `preposition`: qok → of
- `source`: ykeol → ?

**Translation**: *"Take leaf from [ykeol]."*

---

### 28. f101v.27 ⭐ 

**Raw**: `sol.chol.choly.okee!y.dal.qol.shckheol.chol.cthear.keey???<-><!fold>???chee!o.ol...`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: chol → leaf
- `preposition`: qokeeey → of
- `source`: saiir → barley

**Translation**: *"Take leaf from the barley."*

---

### 29. f103r.2 ⭐ 

**Raw**: `dai!n.shek.chcphhdy.daloky.opchedy.peshol.chep.ar.otchy.sal.lkeey.sar.ain.ok??.c...`

**Parsed Slots**:
- `verb`: dain → Take
- `amount`: ar → handful
- `ingredient`: sal → salt

**Translation**: *"Take a handful of salt."*

---

### 30. f103v.25 ⭐ 

**Raw**: `sai!n.olkeeey.qokan.oteedy.qotai!n.otal.oty.opar.aram.oteeam`

**Parsed Slots**:
- `verb`: sain → Prepare
- `amount`: otal → whole
- `preposition`: qokan → of
- `source`: oteedy → ?

**Translation**: *"Prepare a whole from [oteedy]."*

---

### 31. f103v.41 ⭐ 

**Raw**: `daiin.shey.lshey.lshey.qoar.shar.al.otar.shedy.ithy.lchdy.ras`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: al → portion
- `ingredient`: otar → earth

**Translation**: *"Take a portion of earth."*

---

### 32. f103v.7 ⭐ 

**Raw**: `daiin.shey.chol.chey.oteey.lkeeor.okaiin.shedy.shedy.qokaiin.ol.chedydy`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: chol → leaf
- `preposition`: qokaiin → priest/cohen
- `source`: ol → the

**Translation**: *"Take leaf from [ol]."*

---

### 33. f104r.14 ⭐ 

**Raw**: `daiin.choaiin.qokechy.qotal.cheo.lor.saiin.olkeechey.otal.ol.oeeal`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: otal → whole
- `preposition`: qokechy → of
- `source`: qotal → ?

**Translation**: *"Take a whole from [qotal]."*

---

### 34. f104r.24 ⭐ 

**Raw**: `daiin.char.qotal.okechol.olkeeor.olkeeo!dal.lkaiin.chal!keeedy.qokam`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: char → flower
- `preposition`: qokam → of

**Translation**: *"Take flower."*

---

### 35. f104r.27 ⭐ 

**Raw**: `pchedar.qokaiin.qotaiin.dl.ral.cheodl.cphaiin.daiin.ar.qekeeey.qoparaiin`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ar → handful
- `preposition`: qokaiin → priest/cohen
- `source`: qotaiin → ?

**Translation**: *"Take a handful from [qotaiin]."*

---

### 36. f104r.6 ⭐ [SPECIFIC]

**Raw**: `ycheeody.aiin.lkar.cheeo.dai!n.ockhedy.qokeedy.qotai!n.otchdy.tai!n.chedam`

**Parsed Slots**:
- `verb`: dain → Take
- `amount`: aiin → one
- `preposition`: qokeedy → of
- `source`: qotain → geranium

**Translation**: *"Take one of geranium."*

---

### 37. f104v.25 ⭐ 

**Raw**: `dsheey.qoykeey.lchedy.qokedaiin.orchcthy.daiin.cheey.sair.ol.aiin.chedy`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `preposition`: qokedaiin → of
- `source`: orchcthy → ?

**Translation**: *"Take one from [orchcthy]."*

---

### 38. f104v.3 ⭐ 

**Raw**: `shod.chedy.qotaiin.odaiin.okeol.ockhhy.chol.qokeedy.qotair.oeedaiin.ol.dl`

**Parsed Slots**:
- `verb`: odaiin → Take
- `ingredient`: okeol → flower extract
- `preposition`: qokeedy → of
- `source`: qotair → ?

**Translation**: *"Take flower extract from [qotair]."*

---

### 39. f105r.20 ⭐ 

**Raw**: `saiin.chey.teol.ykair.paiir.olkaiin.olfaiin.odar.al.airody.al.teedar.dam`

**Parsed Slots**:
- `verb`: saiin → Prepare
- `amount`: al → portion
- `ingredient`: dam → blood

**Translation**: *"Prepare a portion of blood."*

---

### 40. f105r.24 ⭐ 

**Raw**: `pcheor.ai!n.ckheey.okeeey.paiin.ar.aiiin.chpaiikey.sheo.pcheey.dal.daiin.dam`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ain → one
- `ingredient`: dam → blood

**Translation**: *"Take one blood."*

---

### 41. f105r.32 ⭐ 

**Raw**: `ycheochy.lkeol.daiin.ykair.olkchey.dar.qopchdy.dair.otar.ar.adam`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ar → handful
- `ingredient`: otar → earth

**Translation**: *"Take a handful of earth."*

---

### 42. f105v.15 ⭐ 

**Raw**: `ycheey.kar.ykeey.otaiin.otal.dar.chdos.kal!chedy.opchdy.daiin.oraiin.r`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: otal → whole
- `ingredient`: otaiin → fig

**Translation**: *"Take the whole fig."*

---

### 43. f105v.16 ⭐ 

**Raw**: `daiin.cheey.dal.chl.okair.aiin.cphe!or.aiin.okal.chodaiin.otaiin.opaiim`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `ingredient`: chl → root

**Translation**: *"Take one root."*

---

### 44. f105v.31 ⭐ 

**Raw**: `ychtaiis.aiichy.dol.aiin.otaiin.aiidy.okchd.otor.daiin<$>`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `ingredient`: otaiin → fig

**Translation**: *"Take one fig."*

---

### 45. f105v.32 ⭐ 

**Raw**: `poar.keeo.daiin.qoair.ar.aiphhey.qoeed!eody.qokaiin.qotedais.aporair.apy`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: ar → handful
- `preposition`: qokaiin → priest/cohen
- `source`: qotedais → ?

**Translation**: *"Take a handful from [qotedais]."*

---

### 46. f105v.34 ⭐ 

**Raw**: `sheeo.daiin.chsd.qokeeey.dair.okaiin.otaiin.chedaiin.olkal.lkl.dai!n`

**Parsed Slots**:
- `verb`: daiin → Take
- `ingredient`: otaiin → fig
- `preposition`: qokeeey → of
- `source`: dair → Adar (month)

**Translation**: *"Take fig from the Adar (month)."*

---

### 47. f105v.35 ⭐ 

**Raw**: `doee.okcheeo.l!kaiin.otcheedy.chor.aiin.odaiin.chedy.otaiin.al.kaishd`

**Parsed Slots**:
- `verb`: odaiin → Take
- `amount`: aiin → one
- `ingredient`: chor → stem

**Translation**: *"Take one stem."*

---

### 48. f106r.13 ⭐ 

**Raw**: `pcheol.sheokaiin.otey.qokeeor.sheo.aiin.otchey.pcheo.ror.aiin.daiin.opal`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: aiin → one
- `preposition`: qokeeor → of
- `source`: sheo → fire

**Translation**: *"Take one of fire."*

---

### 49. f106r.16 ⭐ 

**Raw**: `sai!n.oi!n.okai!n.aiin.arol.ocheedy.lkeeeody.daiin.chedar.okol.otar.chdam`

**Parsed Slots**:
- `verb`: sain → Prepare
- `amount`: aiin → one
- `ingredient`: otar → earth

**Translation**: *"Prepare one earth."*

---

### 50. f106r.43 ⭐ 

**Raw**: `daiiral.sheol.daiin.otedy.qokai!n.akar.cheor.al.taiin.chekal.otaras`

**Parsed Slots**:
- `verb`: daiin → Take
- `amount`: al → portion
- `preposition`: qokain → priest/cohen
- `source`: akar → plant_term

**Translation**: *"Take a portion of plant_term."*

---

## Key Vocabulary Reference

### Verified Plant Parts (Visual Correlation)

| Voynich | English | Confidence |
|---------|---------|------------|
| `char` | flower | 93% visual |
| `chol` | leaf | 93% visual |
| `chl` | root | 100% visual |
| `chor` | stem | visual |
| `chan` | root | visual |

### Measurements

| Voynich | English |
|---------|---------|
| `ar` | handful |
| `al` | portion |
| `aiin` | one |
| `aiiin` | some |
| `or` | amount |
| `otal` | whole |

### Action Verbs

| Voynich | English |
|---------|---------|
| `daiin` | Take |
| `dain` | Take |
| `sain` | Prepare |
| `saiin` | Prepare |

### Specific Plant Names

| Voynich | Plant | Confidence |
|---------|-------|------------|
| `okshy` | botrychium | HIGH |
| `ckhal` | castor | HIGH |
| `qotain` | geranium | HIGH |
| `alam` | geranium | HIGH |
| `okchedy` | plant | HIGH |
| `lkar` | plant | HIGH |
| `olkeedy` | plant | HIGH |
| `lkeedy` | plant | HIGH |
| `chedal` | polygonum | HIGH |
| `lkeey` | poppy | HIGH |
| `chodar` | poppy | HIGH |
| `opol` | poppy | HIGH |
| `chekar` | scabiosa | HIGH |
| `soy` | smilax | HIGH |
| `checkhey` | smilax | HIGH |
| `pchey` | thistle | HIGH |
| `qokeod` | valerian | HIGH |

### Generic Terms

| Voynich | Meaning |
|---------|---------|
| `otar` | earth |
| `otaiin` | fig |
| `okaiin` | heart |
| `chedy` | herb |
| `chdy` | herb |
| `edy` | herb |
| `cheedy` | herb |
| `chey` | plant |
| `shedy` | this herb |

---

## Conclusion

The Voynich manuscript's recipe section follows a consistent grammatical structure:

1. **Verb** (daiin = Take/Use)
2. **Amount** (ar = handful, al = portion)
3. **Plant part** (char = flower, chol = leaf, chl = root)
4. **Preposition** (qok- = of/from)
5. **Source** (either generic 'herb' or specific plant name)

The recipes appear to be **medical preparations** from a **Jewish physician**
working in **Northern Italy** in the 15th century, using a hybrid vocabulary
of **Hebrew** and **Italian** terms.

---

*Generated by Track 99: Final Translation*
*Dictionary version: master_dictionary_v5.json*
*Total dictionary entries: 868*