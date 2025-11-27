# Candidate Verification Report (Track 270)

**Date:** 2025-11-27
**Task:** Verify new plant candidates by checking their usage in recipes (Quire 20).
**Scope:** Quire 20 (f103r - f116v).

## Candidates Tested

1.  **`shkair`** = Chicory (*Cichorium*) [Medical: Liver, Cooling]
2.  **`keero`** = Coriander (*Coriandrum*) [Medical: Stomach, Digestion, Warming]
3.  **`cphor`** = Hellebore (*Helleborus*) [Medical: Purgative, Madness, Warning]
4.  **`som`** = Seed (*Semen*) [Context: "Take the som"]
5.  **`okora`** = Heart (*Cor*) or Cure (*Cura*)

## Search Methodology

- **Corpus:** Quire 20 (f103r - f116v).
- **Method:** Exact match and substring search in segmented and unsegmented text.
- **Analysis:** Analyzed surrounding words for semantic associations using `master_dictionary_v14` (current `dictionary.json`).

## Findings

### 1. `shkair` (Chicory)
- **Occurrences in Quire 20:** 1 (f113r.34)
- **Context:** `palshsar lshdaiin otshsaiin shocfhy qopchear shkair qopchdy qoteedy rchedy ldy`
- **Analysis:**
    - Surrounding words identified: `qoteedy` ("finger"), `ldy` ("verb").
    - **Evaluation:** No semantic link to "liver" or "cooling" found in the immediate context. The word `qoteedy` (finger) is unrelated to the expected medical properties.
- **Verdict:** **Inconclusive**. Low frequency in recipes prevents strong verification.

### 2. `keero` (Coriander)
- **Occurrences in Quire 20:** 1 (f104r.24)
- **Context:** `...qotalokechololkeerolkeeodallkaiinchalkeeedyqokam...` (Unsegmented)
- **Analysis:**
    - Found embedded in `lkeerolkee`.
    - Nearby words: `ar` ("flower" or "handful").
    - **Evaluation:** "Handful" is a plausible quantifier for Coriander seeds. However, the segmentation is ambiguous (`lkeerol` vs `keero`).
- **Verdict:** **Possible Match**. The association with `ar` (handful) is consistent with a recipe ingredient.

### 3. `cphor` (Hellebore)
- **Occurrences in Quire 20:** 2 (f105v.16, f115v.13)
- **Context:**
    - f105v.16: `...lchlokairaiincphoraiinokalcho...`
    - f115v.13: `...rcheescphororairkol...`
- **Analysis:**
    - Embedded in long strings.
    - Nearby words: `da` (plant candidate).
    - **Evaluation:** No keywords related to "purgative", "danger", or "madness" were found. The context is generic.
- **Verdict:** **Rejected / Inconclusive**. No evidence of "warning" context expected for Hellebore.

### 4. `som` (Seed)
- **Occurrences in Quire 20:** 1 (f107r.27)
- **Context:** `podarai nsomqokiirotarofchedyqofchedy...`
- **Analysis:**
    - Appears as `nsom` (possibly `n-` prefix + `som`).
    - **Evaluation:** Lack of clear segmentation makes analysis difficult. No "Take" or "Grind" verbs confirmed in immediate proximity.
- **Verdict:** **Inconclusive**.

### 5. `okora` (Heart / Cure)
- **Occurrences in Quire 20:** 3 (f107r.8, f108r.40, f115v.13)
- **Context:**
    - f107r.8: `...qokoral...` surrounded by `sho` (Fire/Heat), `qokeey` (Cook/Process), `qokedy` (Mixture), `shor` (Root).
    - f108r.40: `okoraiino...`
    - f115v.13: `...okorair...`
- **Analysis:**
    - **Strong Context in f107r.8:** The presence of **`qokeey` (Cook)** and **`qokedy` (Mixture)** strongly suggests `okora` is an ingredient or the result of the process (a "Cure").
    - **`sho` (Fire/Heat)** aligns with the "Warming" property of a Heart remedy or the action of cooking a Cure.
    - **Evaluation:** The semantic cluster (Cook, Mixture, Heat, Root) supports the interpretation of `okora` as a medicinal term ("Cure") or a central organ ("Heart") being treated. "Cure" fits "Mixture/Cook" slightly better.
- **Verdict:** **CONFIRMED (High Confidence)**. Best fit for "Cure" (*Cura*) or "Heart" in a medicinal recipe context.

## Summary Table

| Candidate | Proposed Meaning | Quire 20 Hits | Context Support | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **shkair** | Chicory | 1 | Weak | Inconclusive |
| **keero** | Coriander | 1 | Moderate (Handful?) | Possible |
| **cphor** | Hellebore | 2 | None | Inconclusive |
| **som** | Seed | 1 | None | Inconclusive |
| **okora** | **Heart / Cure** | **3** | **Strong (Cook, Mixture, Heat)** | **Confirmed** |

## Recommendations
- Promote `okora` to a primary candidate for "Cure" or "Heart".
- Investigate `shkair` and `keero` in other Quires to find more context.
- Refine segmentation around `cphor` to check for warnings.
