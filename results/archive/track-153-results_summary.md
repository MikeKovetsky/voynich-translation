# Track 153 Results Summary: Morphological Parser

**Date:** 2025-11-26
**Task:** Track 153 - Morphological Parser (The Engine)
**Status:** Completed

## 1. Objective
The goal of this task was to move beyond treating VMS words as unique strings (e.g., `qokeedy`) and instead treat them as composite structures (`qo-keed-y`). By stripping defined prefixes and suffixes, we aimed to isolate the "Core" roots of the language.

## 2. Methodology
- **Script:** `research/morph_parser.py`
- **Input:** `data/eva_ivtff.txt` (Stolfi 'H' transcription layers)
- **Rules:** `results/morphology_rules.json` (58 prefixes, 12 suffixes)
- **Algorithm:**
  - **Greedy Recursive Stripping:** Longest matching prefixes/suffixes were removed recursively until no match was found.
  - **Order:** Prefixes stripped from left-to-right, Suffixes stripped from right-to-left.
  - **Output:** Structured JSON preserving original word, component parts, and the remaining root.

## 3. Key Findings

### 3.1 Dataset Statistics
- **Lines Processed:** 5,206
- **Total Words Analyzed:** ~38,000 (across all lines)

### 3.2 Top Roots (The "Core")
A surprising finding is the dominance of "Empty" roots, where the entire word was consumed by prefix/suffix rules (e.g., `y-k-al`).

| Rank | Root | Frequency | Notes |
|------|------|-----------|-------|
| 1 | `[EMPTY]` | 21,319 | Indicates words composed entirely of affixes (e.g., `yk`, `ol`, `daiin`). |
| 2 | `e` | 2,586 | extremely common single-letter root. |
| 3 | `a` | 1,824 | |
| 4 | `ee` | 1,535 | |
| 5 | `eo` | 745 | |
| 6 | `ai!` | 567 | |
| 7 | `!` | 482 | Uncertainty marker treated as root in some contexts. |
| 8 | `he` | 407 | |
| 9 | `ho` | 374 | |
| 10 | `ai` | 299 | |

### 3.3 Top Prefixes
These "grammatical handles" attach to the front of words.

1. `y` (7,435)
2. `l` (4,276)
3. `d` (4,090)
4. `k` (3,759)
5. `che` (3,652)

### 3.4 Top Suffixes
These likely indicate tense, plurality, or aspect.

1. `y` (3,700)
2. `dy` (3,282)
3. `iin` (2,790)
4. `r` (2,686)
5. `ar` (1,867)

## 4. Interpretation & Next Steps
The high volume of `[EMPTY]` roots (approx. 55%) suggests that the VMS "vocabulary" is heavily constructed from a small set of combinable morphemes. What we see as "roots" might often just be stable combinations of these affixes.

**Next Steps:**
1. **Task 154 (Prefix Logic):** Analyze the grammar of `y-`, `l-`, `d-` to understand their functional roles.
2. **Task 156 (Compound Splitter):** Address the "Word Soup" issue where roots like `aiinchkaiincthor` remain; these need to be split further.
3. **Task 155 (Root Dictionary):** Begin assigning semantic meaning to the stable roots (`e`, `a`, `ee`).

## 5. Artifacts
- **Parsed Data:** `results/parsed_text.json`
- **Frequency Data:** `results/root_frequency.csv`
