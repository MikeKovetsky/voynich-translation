# 'sara' Investigation Profile

## Goal
Identify the meaning of `sara`, a frequent recipe starter word in Quire 20.

## Findings

### 1. Frequency and Position
- **Occurrences:** 14 times in Quire 20.
- **Position:** In **100%** of cases (14/14), `sara` appears at the **start of a line**.
- **Role:** This strongly confirms its role as a **Recipe Starter** or Section Header.

### 2. Context (Following Words)
The words immediately following `sara` are highly consistent:
- **`ii`**: 7 occurrences (50%)
- **`in`**: 5 occurrences (36%)
- **`ro`**: 1 occurrence
- **`lchal...`** (long compound): 1 occurrence

### 3. Semantic Analysis
- **`sara`**:
  - **Hypothesis:** "Syrup" (Arabic *Sharab*, Latin *Saccharum*).
  - **Fit:** Excellent fit for a recipe starter ("Syrup of...").
  - **Etymology:** Phonetically similar to *Sarah* / *Saccharum* / *Sharab*.

- **Followers (`ii`, `in`)**:
  - **`ii`**: In `root_dictionary_v3.json`, `ii` is mapped to **"Adar (month)"**. 
    - *Interpretation:* "Syrup of Adar" (Seasonal syrup?) or `ii` as a numeral/placeholder.
  - **`in`**: In `root_dictionary_v3.json`, `in` is classified as **"Plant Name"** (Unknown).
    - *Interpretation:* "Syrup of [Plant]".
  - **Negative Result:** No direct instances of `sara ol` ("Syrup of...") were found. `ii` and `in` seem to serve the function of the ingredient or preposition+ingredient.

### 4. Correlation with Water/Sweet
- The task asked to check for "Water" (`saiin`) or "Sweet" (`sheedy`/`honey`) nearby.
- **Result:** These specific words do **not** appear immediately after `sara`. 
- **Implication:** If `sara` means "Syrup", the "sweetness" or "liquid" nature is intrinsic to the word, and the following word specifies the *type* or *ingredient* (e.g., Adar/Plant), rather than describing the syrup itself (e.g., "Sweet Syrup").

## Conclusion
`sara` is a definitive **Recipe Starter** in Quire 20, appearing exclusively at line beginnings. It is most likely a noun indicating the **type of preparation** (e.g., "Syrup", "Decoction", "Mixture"). It is followed by `ii` or `in` in 86% of cases, which likely denote the **key ingredient** or **season/time** associated with the recipe.

**Recommendation:** Treat `sara` as "Syrup" or "Preparation" in translation models, with `ii` and `in` as specific modifiers (Adar/Plant).
