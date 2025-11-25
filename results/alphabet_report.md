# Voynich Alphabet Verification Report

## EVA Character Analysis

- Total unique characters: 25
- Total words analyzed: 193582
- Unique words: 14056

### Character Frequencies (top 20)

- `o`: 127,607
- `e`: 100,730
- `h`: 92,426
- `y`: 91,737
- `a`: 73,563
- `c`: 68,473
- `d`: 67,482
- `i`: 60,940
- `k`: 56,188
- `l`: 54,157
- `r`: 37,882
- `s`: 36,909
- `t`: 35,436
- `n`: 31,709
- `q`: 28,433
- `p`: 8,270
- `m`: 5,583
- `f`: 2,379
- `g`: 273
- `x`: 150

### Digraph Occurrences

- `cth` (gallows): 5,074
- `ckh` (gallows): 4,893
- `cph` (gallows): 1,152
- `cfh` (gallows): 381
- `ch` (basic): 56,582
- `sh` (basic): 23,588

## Claston Character Analysis

- Total unique characters: 125
- Total words: 40681

## EVA Alphabet Verification

- All basic EVA present: ✓
- Correct characters: 19
- Unknown characters: b, j

## Claston-EVA Mapping Verification

- Verified basic mappings: 21
- Extended/variant chars: 21
- Issues found: 0
- Truly unmapped: 83

### Extended Claston Characters (variants)

- `m` → m/ending: 4,112
- `C` → e (variant): 2,844
- `7` → j?: 2,715
- `A` → a (variant): 769
- `j` → p (variant): 564
- `3` → g?: 516
- `z` → z (word-end): 511
- `5` → b?: 409
- `d` → d (variant in claston): 336
- `u` → u (rare): 177
- `Z` → n (final variant): 154
- `N` → n (final): 132
- `J` → f (variant): 122
- `6` → x?: 115
- `I` → i (variant): 98

### Unmapped Claston Characters

- `Y`: 55
- `t`: 40
- `P`: 38
- `S`: 38
- `l`: 36
- `U`: 32
- `ä`: 30
- `b`: 28
- `Q`: 27
- `T`: 27
- `w`: 24
- `V`: 23
- `X`: 14
- `r`: 12
- `q`: 11
- `R`: 11
- `µ`: 11
- `ý`: 10
- `v`: 10
- `º`: 10

## Weirdo Characters

No weirdo characters found.

## Rare Characters (<100 occurrences)

- `z` (standard): 2 - variant
- `b` (standard): 7 - variant
- `u` (standard): 7 - variant
- `v` (standard): 47 - variant
- `j` (standard): 81 - variant

## Position Distribution (sample)

Key characters and their position tendencies:

- `o`: initial 33.1%, medial 62.0%, final 4.9%
- `a`: initial 13.6%, medial 85.4%, final 1.0%
- `d`: initial 27.8%, medial 67.5%, final 4.7%
- `y`: initial 9.8%, medial 5.2%, final 85.0%
- `k`: initial 11.6%, medial 87.5%, final 0.9%
- `q`: initial 98.7%, medial 1.2%, final 0.1%

## Recommendations

- Review unmapped Claston characters for completeness
- Investigate unknown characters in EVA data
- Ensure digraph parsing order (longer first: cth before ch)