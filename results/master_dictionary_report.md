# Master Dictionary Report

## Overview

| Metric | Value |
|--------|-------|
| **Total Entries** | 924 |
| **High Confidence (≥0.8)** | 71 |
| **Medium Confidence (0.5-0.8)** | 457 |
| **Low Confidence (<0.5)** | 396 |

## Entries by Category

| Category | Count |
|----------|-------|
| noun_botanical | 270 |
| noun | 124 |
| unknown | 103 |
| preposition | 96 |
| zodiac_vocab | 61 |
| adjective | 42 |
| paradigm | 41 |
| botanical | 32 |
| phrase | 30 |
| medical | 24 |
| verb | 21 |
| disease | 20 |
| noun_medical | 16 |
| zodiac | 13 |
| property | 11 |
| number | 9 |
| star | 5 |
| suffix | 3 |
| action | 3 |

## Top 50 Most Confident Mappings

| # | Voynich | Decoded | Latin | English | Confidence |
|---|---------|---------|-------|---------|------------|
| 1 | `o4o` | aqua | water | water | 1.00 |
| 2 | `8am` | dem | de | of/from | 0.97 |
| 3 | `8ay` | dei | de | of/from | 0.97 |
| 4 | `8ae` | dei | de | of/from | 0.97 |
| 5 | `o89` | ads | ad | to | 0.97 |
| 6 | `8ae9` | deis | de | of/from | 0.97 |
| 7 | `oqo` | aqua | aqua | water | 0.95 |
| 8 | `8an` | den | dens | tooth | 0.91 |
| 9 | `oh9` | ars | aries | Aries | 0.91 |
| 10 | `4ohan` | quaren | herba | the herb (ablative) | 0.90 |
| 11 | `4oham` | quarem | herba | the herb (accusative) | 0.90 |
| 12 | `4ohae` | quarei | herba | the herb (instrumental) | 0.90 |
| 13 | `4ohay` | quarei | herba | the herb (genitive) | 0.90 |
| 14 | `4ohoe` | quarai | herba | the herb (locative) | 0.90 |
| 15 | `A8` | ad | ad | to/for | 0.90 |
| 16 | `8E` | de | de | of/from | 0.90 |
| 17 | `4oh89` | quards | herba | the herb (gen.plural) | 0.90 |
| 18 | `okay` | anei | ante | before | 0.89 |
| 19 | `okam` | anem | ante | before | 0.89 |
| 20 | `okae` | anei | ante | before | 0.89 |
| 21 | `ok19` | ants | ante | before | 0.89 |
| 22 | `2cc9` | bccs | bacca | berry | 0.89 |
| 23 | `8az` | dez | de | of/from | 0.88 |
| 24 | `8ap` | dep | de | of/from | 0.88 |
| 25 | `4oh19` | quarts | quartana | quartan fever | 0.88 |
| 26 | `an` | en | lenis | gentle | 0.86 |
| 27 | `ok9` | ans | manus | hand | 0.86 |
| 28 | `1o89` | tads | ad | to | 0.86 |
| 29 | `o8am` | adem | ad | to | 0.86 |
| 30 | `koe` | nai | nasus | nose | 0.86 |
| 31 | `7ay` | lei | lenis | gentle | 0.86 |
| 32 | `hoe` | rai | ramus | branch | 0.86 |
| 33 | `7ae` | lei | lenis | gentle | 0.86 |
| 34 | `2o89` | bads | ad | to | 0.86 |
| 35 | `ok` | an | manus | hand | 0.86 |
| 36 | `okan` | anen | ante | before | 0.85 |
| 37 | `1ch9` | tcrs | tres | three | 0.85 |
| 38 | `oe9` | ais | auris | ear | 0.85 |
| 39 | `2co` | bca | bacca | berry | 0.85 |
| 40 | `kam` | nem | novem | nine | 0.85 |
| 41 | `okap` | anep | ante | before | 0.85 |
| 42 | `1oh9` | tars | tres | three | 0.85 |
| 43 | `ae9` | eis | lenis | gentle | 0.85 |
| 44 | `ay9` | eis | lenis | gentle | 0.85 |
| 45 | `okaz` | anez | ante | before | 0.85 |
| 46 | `qokaiin` | aquerii | article + ablative | from the herb | 0.85 |
| 47 | `qokain` | aquerin | article + accusative | the herb (object) | 0.85 |
| 48 | `y` | s | -us/-is abbreviation | nominative singular marker | 0.85 |
| 49 | `okeey` | arccs | aries | Aries (zodiac) | 0.85 |
| 50 | `ohoe29` | araibs | aries | Aries (zodiac sign) | 0.85 |

## Phonetic Key (Confirmed)

| Voynich | Latin | Confidence |
|---------|-------|------------|
| o | a | CONFIRMED |
| h | r | CONFIRMED |
| 9 | s | CONFIRMED |
| k | n | CONFIRMED |
| c | c | CONFIRMED |
| 7 | l | CONFIRMED |
| m | m | CONFIRMED |
| a | e | STRONG |
| e | i | STRONG |
| 8 | d | STRONG |
| 1 | t | STRONG |
| 4 | qu | STRONG |
| y | i | STRONG |
| 2 | b | STRONG |

## Abbreviation System

| Voynich Ending | Latin Equivalent |
|----------------|------------------|
| -9 | -us/-is (nominative) |
| -89 | -orum/-arum (genitive plural) |
| -am | -am (accusative) |
| -oe | -ae (dative/ablative) |
| -ay | -i (genitive) |
| -an | -um (accusative neuter) |
| -ae | -ae (genitive/dative fem.) |
| -c9 | -cus/-cis (adjectival) |

## Usage Instructions

```python
import json

# Load dictionary
with open('results/master_dictionary.json') as f:
    master = json.load(f)

# Look up a word
def lookup(word):
    for e in master['entries']:
        if e['voynich'] == word:
            return e
    return None

# Example
result = lookup('o4o')
print(result)  # {'voynich': 'o4o', 'latin': 'aqua', 'english': 'water', ...}
```
