# Track 205: Dosage Detection Results

## Goal
Identify words that function as "Numbers" or "Dosages" in the recipes (Quire 20).

## Methodology
1.  **Parsing:** Extracted text from Quire 20 (f103r-f116v) using the `F` (Friedman) transcription where available, as it tends to have better segmentation.
2.  **Pattern Search:**
    -   **Repeated Glyphs:** Searched for standalone words consisting of repeated characters (e.g., `ii`, `iii`).
    -   **Dosage Slot:** Analyzed words appearing immediately before known "Ingredients" (from `recipe_ingredients_v2.json`).
    -   **'Ol' Pattern:** Analyzed words appearing before `ol` (The/Of), assuming the structure `[Amount] ol [Ingredient]`.

## Findings

### 1. Repeated Glyphs (Numeric Candidates)
The most significant finding is the high frequency of **`ii`** as a standalone word.
-   **`ii`**: 62 occurrences. (Strong candidate for **2**).
-   **`ee`**: 32 occurrences. (Could be a number or a marker).
-   `iii`: 0 occurrences (likely merged or rare).

### 2. Contextual Dosage Candidates
Words appearing immediately before ingredients or `ol`.

#### Pattern: `[Word] [Ingredient]`
-   **`qok`** (17): High frequency. Likely "Take" or "Process" (Imperative Verb) rather than a number.
-   **`yd`** (4): "And"? Or a measurement?
-   **`aiin`** (3): "Water" / "One".
-   **`daiin`** (2): "Take Water"?

#### Pattern: `[Word] ol [Ingredient]`
This pattern yielded more consistent results, suggesting `ol` acts as a separator (e.g., "Amount **of** Ingredient").
-   **`saiin`** (6): Strong candidate for a specific amount or instruction.
-   **`che`** (6): "And" or "Then"?
-   **`daiin`** (4): consistent with "Take water of...".
-   **`sh` / `she`** (8 total): High frequency grammatical particles.

### 3. The `dal` / `dair` Hypothesis
-   **`dal`** and **`dair`** (Aries/Adar) were checked as potential candidates for "1".
-   **Result:** They appear **0 times** as standalone words immediately before ingredients or `ol` in this section.
-   **Implication:** They are likely either:
    -   Compounded with other words (e.g., `daloky`).
    -   Not used as numbers in the recipes.
    -   Parsing artifacts (merged into longer strings).

## Conclusion & Candidates
The structure of the recipes seems to favor **Imperative Verbs** (`qok`, `daiin`) over explicit numeric digits, except for **`ii`**.

| Candidate | Count | Context | Hypothesis |
| :--- | :--- | :--- | :--- |
| **`ii`** | 62 | Standalone | **Number 2** |
| **`saiin`** | 6 | Before `ol` | **Measurement** / "One"? |
| **`daiin`** | 6 | Before `ol`/Ingr | **"Take Water"** (Instruction + Amount) |
| **`qok`** | 17 | Before Ingr | **"Take"** / "Process" (Verb) |

## Next Steps
-   Investigate `saiin` as a potential number "1" or specific dosage unit ("Cup"?).
-   Analyze `ii` contexts to see if it pairs with specific ingredients (e.g., "2 leaves").
