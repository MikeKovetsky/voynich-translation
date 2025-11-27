# Progress Summary 2

... (previous content) ...

## Iteration 59: Semantic Verification & The "ed" Mystery 🕵️‍♂️

**Status:** Complete
**Date:** 2025-11-26

**Findings:**
1.  **Cluster-Section Correlation (Task 171):**
    - Confirmed distinct vocabularies.
    - **Herbal:** 98 unique noun clusters (Plant names/parts?).
    - **Astro:** 74 unique clusters (Star names/sky terms?).
    - **Recipes:** 44 unique clusters (Ingredients/Tools?).
    - **Bio:** 10 unique clusters (Anatomy?).
2.  **The `ed` Investigation (Task 172):**
    - `ed` (or `edy`) is the **"Recipe Verb"**.
    - It appears 490 times in Bio and 429 times in Recipes, but is *absent* in Astro/Herbal.
    - It takes the `qok-` (Verb) prefix and `-y` suffix.
    - **Conclusion:** `ed` = "Mix", "Process", or "Treat". It is the core action of the manuscript's "practical" sections.
3.  **Verb Morphology (Task 173):**
    - **`-y` Suffix:** Dominates in "Instructional" sections (Recipes). Likely **Imperative** ("Mix!").
    - **`-dy` Suffix:** Dominates in "Narrative" sections (Bio). Likely **Past/Passive** ("It was mixed").

## Iteration 60: The Grammar of Action 🎬

**Status:** In Progress
**Date:** 2025-11-26

**Goal:**
Apply our new grammatical rules (`-y` = Imperative, `-dy` = Narrative, `ed` = Process) to generate context-aware translations. We will try to read the Recipes as a list of instructions and the Bio section as a story.

**Tasks Created:**
1.  **Task 174 (Text Type Classification):**
    - Split the manuscript into "Instructional" (Recipes/Stars) and "Narrative" (Bio/Rosettes) based on the `-y`/`-dy` ratio.
    - Create separate translation rules for each mode.
2.  **Task 175 (Recipe Decoding):**
    - Translate the Recipe section (Quire 20) using the specific hypothesis:
    - `qok-ed-y` = "Process!" / "Mix!"
    - `ol [Noun]` = "The [Ingredient]"
    - `dy` = End of step.
3.  **Task 176 (Herbal Noun Differentiation):**
    - Analyze the 98 "Herbal Clusters".
    - **Hypothesis:**
        - Words appearing on *only one page* = **Plant Names**.
        - Words appearing on *many pages* = **Plant Parts** (Root, Leaf).
    - Tag these accordingly in the dictionary.

**Hypothesis:**
The manuscript is not just one text; it's a **Lab Notebook**.
- **Herbal/Astro:** Reference Data (Nouns).
- **Recipes:** Instructions (Imperative Verbs).
- **Bio:** Observations/Results (Narrative Verbs).
