# Recipe Verb Analysis Report

**Date:** 2025-11-26
**Task:** Track 120 - Validate `qokeey` / `qokeol` as "Boil" or "Drink".

## 1. Hypothesis
Previous iterations suggested `qokeey` or `qokeol` might mean "Boil" or "Drink" based on their presence in recipes involving water (`daiin`).

## 2. Data Analysis (Quire 20)
Analyzed 289 recipe paragraphs from Quire 20 (Folios 103r - 116v).

### Frequency
- **`qokeey`**: 159 occurrences (Very frequent process word)
- **`qokeol`**: 13 occurrences
- **`okeol`**: 13 occurrences
- **`okam`**: 11 occurrences

### Position: End of Recipe
Checked if these words appear as the final instruction (implying "Drink this" or "Serve").
- `chedy`: 9 times (Top end-word)
- `qokeey`: 5 times
- `qokeol`: 0 times
- `okam`: 1 time

**Observation:** `chedy` is a stronger candidate for the final action ("Drink" / "Serve" / "Done"). `qokeey` is primarily a mid-process action.

### Context: Water (`daiin`)
Checked proximity to `daiin` (within 5 words).
- **`qokeey`**: Found **20 times** near `daiin`.
  - Often appears immediately before or after water (distances: -1, +2, etc.).
- **`qokeol`**: Found 1 time near `daiin`.
- **`okeol`**: Found 1 time near `daiin`.
  - Specific instance: `daiin ol oain okeol` ("Take water ... [okeol]"). This strongly suggests `okeol` (and potentially `qokeol`) is an action applied to the water immediately, like "Boil" or "Heat".

## 3. Conclusions & Theory Refinement

1.  **`qokeey` = General Cooking Process ("Cook" / "Prepare")**
    - High frequency (159) and mid-sentence position suggest it is the main recurring action in recipes.
    - Frequent association with water supports "Boil" or "Cook".

2.  **`okeol` / `qokeol` = Specific Water Action ("Boil"?)**
    - The phrase `daiin ol oain okeol` is distinct. If `daiin ol oain` is "Take spring water", then `okeol` is likely the immediate action: "Take spring water [and] Boil [it]".
    - `qokeol` might be a morphological variant (Prefix `q-` + `okeol`).

3.  **`chedy` = Final Action ("Drink" / "Serve")**
    - Appearing most frequently at the very end of recipes suggests it marks the conclusion.

## 4. Recommendation
- Treat `qokeey` as the general verb for "Process/Cook".
- Investigate `chedy` as "Drink" or "Administer".
- `okeol` remains a strong candidate for "Boil" specifically when next to water.

## Generated Files
- `recipe_verb_analysis.py`: Analysis script.
