# Track 96: Modifier Analysis Report

## Goal
Identify the source plants (words following `qok-` = "of [plant]").

## Methodology
1. Extract top modifiers from recipe section
2. Cross-reference each modifier with herbal pages
3. If modifier appears on few pages → likely plant name
4. If modifier appears on many pages → generic term

## Distribution Summary

| Category | Count | Interpretation |
|----------|-------|----------------|
| ULTRA_SPECIFIC | 3 | Single page → Plant name |
| SPECIFIC | 4 | 2-3 pages → Plant name |
| MODERATE | 7 | 4-10 pages → Possibly generic |
| GENERIC | 36 | >10 pages → General term |
| NO_MATCH | 0 | Recipe-only terms |

## Key Findings: Plant Name Candidates

### ULTRA-SPECIFIC (HIGH confidence)

| Voynich Word | Herbal Page | Expert Plant ID |
|--------------|-------------|------------------|
| `qotain` | f58v | geranium |
| `okchedy` | f50r | ? |
| `lkar` | f66r | ? |

### SPECIFIC (MEDIUM confidence)

| Voynich Word | Herbal Pages | Expert Plant ID |
|--------------|--------------|------------------|
| `olkeedy` | f50r, f94r, f95r1 | ? |
| `lkeey` | f48v, f56v | papaver, thistle, scammonia, poppy, tamus communis, papaver somniferum |
| `chedal` | f31v, f43v, f58v | polygonum, geranium |
| `lkeedy` | f55r, f66r | ? |

## Plant → Voynich Mappings


### Geranium

- `qotain` (pages: f58v, confidence: HIGH)
- `chedal` (pages: f31v, f43v, f58v, confidence: MEDIUM)

### Papaver

- `lkeey` (pages: f48v, f56v, confidence: MEDIUM)

### Papaver Somniferum

- `lkeey` (pages: f48v, f56v, confidence: MEDIUM)

### Polygonum

- `chedal` (pages: f31v, f43v, f58v, confidence: MEDIUM)

### Poppy

- `lkeey` (pages: f48v, f56v, confidence: MEDIUM)

### Scammonia

- `lkeey` (pages: f48v, f56v, confidence: MEDIUM)

### Tamus Communis

- `lkeey` (pages: f48v, f56v, confidence: MEDIUM)

### Thistle

- `lkeey` (pages: f48v, f56v, confidence: MEDIUM)

## Reverse Analysis: Plant Pages → Specific Modifiers

For each known plant page, which modifiers appear specifically (on ≤3 pages)?

| Folio | Expert Plant ID | Specific Modifiers |
|-------|-----------------|--------------------|
| f100v | botrychium | `chols` |
| f101v | baldrian, valerian | `otoly`, `otarar` |
| f102r2 | gemswurz | `roiin`, `doaiin` |
| f13r | tussilago | `doaiin` |
| f17v | tamus communis, tamus? thp: smilax | `oy` |
| f20r | arctostaphylis, poterium? thp: moss polytrichnum | `shosaiin` |
| f21r | polygonum | `qoteeol` |
| f2v | arctostaphylis, poterium? thp: moss polytrichnum | `chodain` |
| f32r | mentastrum | `chckhol` |
| f33r | scabiosa | `shdar` |
| f34r | scabiosa | `ochey`, `qoteedy`, `olar` |
| f35r | uva quercina | `qokeeaiin`, `shosaiin` |
| f37r | baldrian, valerian | `otoly` |
| f39v | thistle | `lkedy` |
| f3v | hypericum, centaurium erythaea | `ch`, `qoteeol`, `chckhol` |
| f40v | scabiosa, papaver | `chkal`, `aram` |
| f41r | thistle | `lchdy`, `qokeed` |
| f42v | elv | `checthey` |
| f43v | polygonum | `chedal`, `teedy`, `qokedal` |
| f46v | gemswurz | `olar` |
| f47r | gemswurz | `shokeey` |
| f48r | cyanus, papaver | `qoteo`, `lkeeedy` |
| f48v | papaver, poppy | `lkeey`, `chdor`, `teedy` |
| f50v | lycopsis or a nearly allied boraginace plant, symphytum | `dalol` |
| f51v | lycopsis or a nearly allied boraginace plant, symphytum | `qokcheody` |
| f56v | tamus communis, scammonia | `lkeey`, `ochey` |
| f57r | geranium | `okeeody` |
| f58r | geranium | `dalol`, `cheoly`, `aram` |
| f58v | geranium | `qotain`, `chedal`, `qokeeos` |
| f5v | geranium | `chols` |
| f66v | geranium | `okchdal`, `shedar` |
| f89r1 | scabiosa, geranium | `chepy` |
| f89r2 | uva quercina | `oy`, `qokcheody` |
| f89v1 | papaver, poppy | `chodain`, `rol` |
| f89v2 | cyanus | `rary` |
| f8r | atriplex, elv | `lody` |
| f90r1 | papaver, poppy | `rary`, `qokeed` |
| f90v2 | papaver, poppy | `okeeom` |
| f93r | scabiosa | `qotchd` |
| f95r2 | thistle | `aram` |
| f9v | viola | `opy` |

## Conclusion

**7 modifier words** show page-specific distribution, suggesting they are **plant names**.

**8 plants** have direct matches via forward analysis.

**41 plant pages** have specific modifiers that could be plant names.

### Key Insight

Most top modifiers (`chedy`, `chey`, etc.) are **GENERIC** - they appear on 20-60+ pages. These likely represent common botanical terms (leaf, root, flower) rather than plant names.

The **ULTRA_SPECIFIC** and **SPECIFIC** modifiers are rare but valuable - they likely ARE plant names.
