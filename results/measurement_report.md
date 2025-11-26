# Track 93: Measurement Analysis Report

## Summary

This analysis identifies words that likely function as measurements (amounts, durations) 
based on their grammatical position within recipe text.

## Methodology

1. **daiin Collocations**: Analyzed words appearing between `daiin` and ingredients
2. **Line Endings**: Found words that frequently end recipe lines (action candidates)
3. **Syntactic Clustering**: Clustered words by position relative to ingredients/connectors

---

## Key Findings

### 1. "daiin [X] ingredient" Pattern

Words appearing between `daiin` and confirmed ingredients may be AMOUNTS:

| Word | Count | Interpretation |
|------|-------|----------------|
| `chedy` | 1 | amount candidate |
| `shey` | 1 | amount candidate |
| `qoair` | 1 | amount candidate |

### 2. Line Endings (Action Candidates)

Words that frequently end recipe lines may be VERBS/ACTIONS:

| Word | Count | Pattern |
|------|-------|---------|
| `am` | 24 |  |
| `al` | 19 |  |
| `chedy` | 17 | [-y] |
| `otam` | 12 |  |
| `qokam` | 11 |  |
| `ol` | 10 |  |
| `dam` | 10 |  |
| `ram` | 9 |  |
| `dal` | 8 |  |
| `lchedy` | 8 | [-y] |
| `ary` | 8 | [-y] |
| `qoky` | 7 | [-y] |
| `aiin` | 7 |  |
| `qokeey` | 7 | [-y] |
| `chdy` | 7 | [-y] |
| `oly` | 7 | [-y] |
| `dy` | 6 | [-y] |
| `qoty` | 6 | [-y] |
| `qotam` | 6 |  |
| `om` | 6 |  |

### 3. Words BEFORE Ingredients

Words appearing immediately before ingredients (potential amounts/modifiers):

| Word | Count | Also Line-Final | Interpretation |
|------|-------|-----------------|----------------|
| `ar` | 14 | 4 | AMOUNT |
| `al` | 9 | 19 | mixed |
| `qokaiin` | 8 | 4 | mixed |
| `qokain` | 8 | 0 | AMOUNT |
| `otain` | 7 | 5 | mixed |
| `or` | 7 | 0 | AMOUNT |
| `okar` | 6 | 0 | AMOUNT |
| `daiin` | 6 | 6 | mixed |
| `otar` | 6 | 0 | AMOUNT |
| `aiin` | 6 | 7 | mixed |
| `dain` | 6 | 6 | mixed |
| `ol` | 5 | 10 | mixed |
| `chedy` | 4 | 17 | mixed |
| `ain` | 4 | 0 | AMOUNT |
| `raiin` | 4 | 0 | AMOUNT |

### 4. Repeated Phrases (Fixed Formulas)

Common word combinations that may be formulaic expressions:

| Phrase | Count | Notes |
|--------|-------|-------|
| `ar al` | 17 | contains ingredient |
| `chedy qokeey` | 15 |  |
| `or aiin` | 14 |  |
| `qokeedy qokeedy` | 11 |  |
| `shey qokain` | 10 |  |
| `qokeey qokeey` | 10 |  |
| `ar aiin` | 10 | contains ingredient |
| `qokeey qokeedy` | 9 |  |
| `ar ar` | 8 | contains ingredient |
| `aiin chey` | 7 |  |
| `qokeedy qokeey` | 7 |  |
| `ol aiin` | 7 |  |
| `chedy qokaiin` | 7 |  |
| `aiin al` | 7 |  |
| `okain chey` | 6 |  |

---

## Measurement Candidate Summary

### HIGH CONFIDENCE (Amount/Number)

Words consistently appearing in measurement slots:

- **`okar`**: {'before_ingredient': 6, 'line_final': 1, 'ratio': 6.0, 'after_daiin': 2, 'type': 'amount_candidate'}
- **`ar`**: {'before_ingredient': 14, 'line_final': 4, 'ratio': 3.5, 'after_daiin': 2, 'type': 'amount_candidate'}
- **`shey`**: {'in_daiin_X_ingr': 1, 'type': 'strong_amount_candidate'}
- **`qoair`**: {'in_daiin_X_ingr': 1, 'type': 'strong_amount_candidate'}

### MEDIUM CONFIDENCE (Possible Actions/Verbs)

Line-final words with action-like patterns:

- **`ol`**: 10 occurrences
- **`al`**: 19 occurrences
- **`chedy`**: 17 occurrences
- **`am`**: 24 occurrences
- **`otam`**: 12 occurrences
- **`qokam`**: 11 occurrences
- **`dam`**: 10 occurrences
- **`lchedy`**: 8 occurrences
- **`ary`**: 8 occurrences

---

## Sample Contexts

### "daiin [X] ingredient" examples:

- **f115r**: `daiin chedy chol chedy qokaiin`
- **f103v**: `daiin shey chol chey oteey`
- **f105v**: `poar keeo daiin qoair ar aiphhey qoeedeody`

---

## Deep Analysis: Grammatical Slot Patterns

### Line-Initial Words (Recipe Starters/Imperatives)

| Word | Count | Interpretation |
|------|-------|----------------|
| `daiin` | 44 | **"Take/Use"** - primary recipe starter |
| `saiin` | 25 | variant of imperative? |
| `sain` | 22 | variant of imperative? |
| `dain` | 20 | variant of `daiin`? |
| `sar` | 13 | - |
| `ycheey` | 12 | - |
| `dar` | 11 | - |

**Finding**: `daiin` at line-initial position 44 times confirms it as the RECIPE STARTER 
(equivalent to "Recipe:" or "Take:").

### Suffix Pattern Analysis

**-am suffix** (possibly "completive" or "action done"):
- `am` (24), `otam` (12), `qokam` (11), `dam` (10), `ram` (9), `qotam` (6), `okam` (5)
- Total: 77 occurrences with `-am` ending at line end
- **Hypothesis**: `-am` may indicate "done/complete/apply"

**-y suffix** (possibly "manner/action in progress"):
- `chedy` (17), `ary` (8), `qoky` (7), `oly` (7), `dy` (6), `qoty` (6)
- Total: 51+ occurrences
- **Hypothesis**: `-y` may be a verbal suffix

### Word Position Matrix

| Word | Before Ingr | After Ingr | Line-Initial | Line-Final | Role |
|------|-------------|------------|--------------|------------|------|
| `ar` | 14 | 10 | 0 | 4 | **AMOUNT/CONNECTOR** |
| `al` | 9 | 20 | 0 | 19 | **RESULT/ACTION** |
| `daiin` | 6 | 0 | 44 | 6 | **IMPERATIVE** |
| `chedy` | 4 | 6 | 0 | 17 | **ACTION/RESULT** |
| `or` | 7 | 3 | 5 | 3 | **AMOUNT** |
| `okar` | 6 | 0 | 0 | 1 | **AMOUNT** (strong) |
| `aiin` | 6 | 18 | 0 | 7 | **CONNECTOR** |

---

## Conclusions

### 1. Recipe Grammar Structure Identified

```
[STARTER] [AMOUNT?] [INGREDIENT] [CONNECTOR] [ACTION-suffix]
```

Examples:
- `daiin chedy chol chedy qokaiin` → "Take [X] leaf [connector] [action]"
- `daiin shey chol chey oteey` → "Take [X] leaf [connector] [action]"

### 2. Strong Amount Candidates

Words that appear BEFORE ingredients but rarely at line-end:

| Word | Confidence | Before Ingr | Line-Final | Ratio |
|------|-----------|-------------|------------|-------|
| `okar` | **HIGH** | 6 | 1 | 6.0 |
| `ain` | **HIGH** | 4 | 0 | ∞ |
| `raiin` | **HIGH** | 4 | 0 | ∞ |
| `ar` | HIGH | 14 | 4 | 3.5 |
| `otar` | HIGH | 6 | 2 | 3.0 |
| `or` | MEDIUM | 7 | 3 | 2.3 |

### 3. Action Word Candidates

Words with high line-final counts (possible verbs):

| Word | Line-Final | Suffix | Possible Meaning |
|------|------------|--------|------------------|
| `am` | 24 | base | "complete/done/apply" |
| `otam` | 12 | -am | variant |
| `qokam` | 11 | -am | "of-the-[X]" + completive |
| `chedy` | 17 | -y | "mix/prepare" |
| `ary` | 8 | -y | variant |

### 4. Fixed Formulas Identified

| Formula | Count | Possible Meaning |
|---------|-------|------------------|
| `ar al` | 17 | "[amount] [result]" |
| `chedy qokeey` | 15 | "[action] [modifier]" |
| `or aiin` | 14 | "[amount] [connector]" |
| `shey qokain` | 10 | "[X] of-the-[Y]" |

### 5. Key Insight: `ar` Word Family

`ar` appears 14 times before ingredients - this is likely a QUANTIFIER:
- Possibly "one/a/some" 
- Forms: `ar`, `okar`, `otar`, `qokar`, `kar`

---

## Recommended Dictionary Updates

Based on this analysis, consider adding:

| Word | Proposed Meaning | Evidence |
|------|------------------|----------|
| `ar` | "one/some" (amount) | 14x before ingredient |
| `okar` | "one-[X]" (amount) | 6x before ingredient, ratio 6.0 |
| `ain`/`aiin` | connector | high in both positions |
| `am` | "done/apply" (action) | 24x line-final |
| `-y` | verbal suffix | consistent line-final pattern |

---

## Next Steps

1. **Cross-validate amounts** with zodiac pages (where numbers might appear)
2. **Compare action words** across all recipe folios
3. **Build semantic clusters** for refined translations
4. **Test grammar frame**: Apply `daiin [AMOUNT] [INGREDIENT] ... [ACTION]` to more lines

