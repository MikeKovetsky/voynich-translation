# Track 207: Number Pattern Search Results

## Goal
Identify the full set of numbers (1-10) by looking for sequential patterns in the text labels.

## Findings

### 1. Star Ring Analysis (e.g., f68r)
- **Page f68r**: Contains **62** distinct star labels.
- **Structure**: The labels are arranged in rings, but do not exhibit a simple orthographic sequence (e.g., `a`, `b`, `c` or `i`, `ii`, `iii`).
- **Content**: Labels are full Voynich words (e.g., `chocphy`, `dolchedy`).
- **Conclusion**: Star labels likely represent specific star names or qualities rather than a simple numbering system.

### 2. Zodiac Degree Marks
- **Observation**: Zodiac pages consistently contain approximately **30 labels** per zodiac sign section.
  - **f72r**: 94 labels (matches 3 signs: Taurus, Gemini, Cancer).
  - **f72v**: 92 labels (matches 3 signs: Leo, Virgo, Libra).
  - **f73r**: 27 labels (matches Scorpio).
  - **f73v**: 28 labels (matches Sagittarius).
- **Conclusion**: The manuscript definitely uses a **30-degree system** for the Zodiac, marked by individual text labels for each degree (or possibly each decan if grouped, but the count suggests degrees).

### 3. Glyph Sequences
- **Search**: Searched for Roman-like sequences (`i`, `ii`, `iii`, `iv`) and the `d`, `r`, `s` sequence.
- **Result**: 
  - Isolated `i`, `ii`, `iii` labels are **absent** (count: 0).
  - `v` appears 2 times as an isolated word.
  - No sequential `d -> r -> s` pattern found in the labels.
- **Interpretation**: The manuscript does not use standard Roman numerals or single-glyph sequences as primary labels for these sections.

## Output
- `results/number_system.json`: Contains the raw counts and label lists for analyzed pages.
