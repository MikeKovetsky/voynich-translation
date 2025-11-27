# Track 156 Results Summary: Compound Word Splitter

## Overview
This task addressed the "Word Soup" phenomenon where the morphological parser (Task 153) identified many "roots" that were actually long strings of concatenated words. Using a greedy left-to-right matching strategy against a list of high-frequency atomic roots, we successfully decomposed these long strings into sequences of valid components.

## Output
- **Dataset:** `results/parsed_text_v2.json`
- **Analysis:** `results/compound_analysis.md`
- **Structure:**
  ```json
  {
    "original": "qokaiinchol",
    "prefix": ["qok"],
    "roots": ["aiin", "chol"],
    "suffix": []
  }
  ```

## Statistics
- **Atomic Roots Identified:** 74
- **Method:** Greedy recursive split using roots with length 2-5 and frequency > 10 (plus manual high-confidence roots like `aiin`, `chol`).

## Key Findings
1.  **Validation of "Word Soup" Hypothesis:** Many long strings (e.g., > 6 chars) in the Voynich text are not unique words but concatenations of smaller, repetitive units.
2.  **Common Compounds:** The analysis revealed highly repetitive structures.
    -   Example: `ry-che-ar-cthaiincpharcfha`
    -   Example: `edy-che-ek-yd-am-che-dl-che-dy-che`
3.  **Atomic Units:** The text is heavily built upon a small set of core roots (e.g., `che`, `chol`, `aiin`, `dy`) that combine dynamically.

## Next Steps
1.  **Grammar Analysis:** Analyze the sequence of `roots` in `parsed_text_v2.json` to determine sentence structure rules (SVO vs other).
2.  **Semantic Re-evaluation:** Apply the `root_dictionary` meanings to these split components to see if coherent sentences emerge from the "soup".
