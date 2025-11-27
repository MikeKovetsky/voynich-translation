# Deep Sweep Results (Track 223-225)

**Date:** 2025-11-27
**Status:** Complete

## 1. Top Unknowns (Track 223)
We identified the Top 100 most frequent words still missing from the dictionary.
*   **#1 Unknown:** `qokeedy` (Freq: 1643).
*   **#2 Unknown:** `qokedy` (Freq: 1511).
*   **#3 Unknown:** `qokal` (Freq: 1113).

**Observation:** The top unknowns are overwhelmingly **Prefix Variations** of known words. This confirms that our dictionary has good "Root Coverage" (65%) but poor "Morphological Coverage". We have defined `okeedy` but not `qokeedy`.

## 2. Morphology Matches (Track 224)
We successfully mapped **45 of the Top 100** unknowns to known roots using simple prefix stripping.

| Unknown | Root | Affix | Meaning Guess |
|---|---|---|---|
| `qokeedy` | `keedy` | `qo-` | With/In Mixture |
| `qokedy` | `kedy` | `qo-` | With/In Mixture (Variant) |
| `odaiin` | `daiin` | `o-` | The Ingredient |
| `qodaiin` | `daiin` | `qo-` | With the Ingredient |
| `qotor` | `tor` | `qo-` | With Earth/Taurus |
| `oaiin` | `aiin` | `o-` | The One/Star |

## 3. Contextual Guesses (Track 225)
Using `daiin` (Take) and `ol` (The) as anchors, we generated **457** high-confidence guesses for Noun candidates.

*   **Examples:**
    *   `daiin [UNKNOWN]` -> Candidate for "Ingredient".
    *   `ol [UNKNOWN]` -> Candidate for "Object/Noun".

## 4. Recommendations
1.  **Immediate Merge:** Add the 45 morphological matches to the Master Dictionary. This alone will boost "Word Coverage" significantly (since `qokeedy` alone is ~1% of the text).
2.  **Pattern Rule:** Instead of adding every `q-` word manually, implemented a "Runtime Stripper" in the translation engine? (Or just bulk-add the top 1000 variants).
3.  **Cleanup:** The unknowns list contained English metadata (`crease`, `fold`). We need to clean the corpus source file.
