# Track 155 Results Summary: Root Dictionary Alignment

## Overview
This task generated a "Root Dictionary" by aligning the existing word-based `unified_dictionary.json` with the morphological root mapping from `root_mapping.json`. The goal was to consolidate meanings at the root level and identify semantic conflicts where the same root is assigned disparate meanings from different source words.

## Output
- **File:** `results/root_dictionary_v1.json`
- **Structure:**
  ```json
  {
    "root": "os",
    "meanings": ["is (essere)", "tree"],
    "source_words": ["cheos", "okeos", "oteos"],
    "conflict_suspected": true
  }
  ```

## Statistics
- **Total Roots Created:** 132
- **Total Words Mapped:** 139
- **Unmapped Words:** 396
  *(Note: Unmapped words are either missing from the root mapping input or could not be resolved to a known root)*
- **Conflicts Detected:** 4

## Identified Conflicts
The following roots have multiple, potentially unrelated meanings derived from different source words. These require manual review or context-based disambiguation.

1.  **Root: `os`**
    -   **Meanings:** `['is (essere)', 'preposition/conjunction', 'tree']`
    -   **Source Words:** `cheos`, `okeos`, `oteos`, `os`
    -   **Issue:** High-frequency grammatical particle `os` is colliding with botanical terms ending in `-os` (likely distinct suffixes vs root).

2.  **Root: `ar`**
    -   **Meanings:** `['to/for', 'verb (unknown)']`
    -   **Source Words:** `ar`, `ary`, `chary`
    -   **Issue:** Preposition `ar` vs verb endings.

3.  **Root: `al`**
    -   **Meanings:** `['to the', 'verb (unknown)']`
    -   **Source Words:** `al`, `ykaly`
    -   **Issue:** Preposition `al` vs verb forms.

4.  **Root: `pch`**
    -   **Meanings:** `['papaver', 'verb']`
    -   **Source Words:** `opchar`, `opchdy`
    -   **Issue:** `opchar` is mapped to `papaver` (poppy), while `opchdy` is tagged as a verb. This might be a noun-verb derivation (e.g., "to drug" vs "drug") or a collision.

## Next Steps
1.  **Resolve Conflicts:** create a task to manually inspect the 4 conflicts.
2.  **Expand Mapping:** The unmapped count (396) is high. We need to improve `root_mapping.json` coverage or fallback heuristics for words that *are* roots themselves.
