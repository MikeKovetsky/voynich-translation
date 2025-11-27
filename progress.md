# Research Progress

## Current Status: Iteration 49 (Nov 26, 2025)
**Focus:** Visualization, Website, Validation

## Recent Achievements
*   **Full Translation (Task 134):** Manuscript fully translated. Split into individual page files.
*   **Plant ID (Task 133):** `chtol` (Poppy), `shoaiin` (Cannabis), `shkaiin` (Hypericum) integrated into dictionary.
*   **Final Report (Task 135):** "Voynich Decoded" report generated.

## Current Hypotheses
1.  **The System:** The manuscript describes a closed loop system:
    *   **Stars** determine the time.
    *   **Plants** are harvested.
    *   **Recipes** process them into `chedy`.
    *   **Baths** apply them to the body.

## Tasks
### Active Iteration (50)
*   **Task 136 (Knowledge Graph):** Generate a JSON graph connecting Plants, Recipes, and Folios.
    *   Nodes: Plant, Page, Ingredient, Recipe.
    *   Edges: APPEARS_ON, CONTAINS, USED_IN.
*   **Task 137 (Website):** Copy translation data to the `web/src/data` folder so the frontend works.
*   **Task 138 (Validation):** Programmatic check:
    *   If a recipe uses `chtol`, is `chtol` illustrated nearby?
    *   Or is there a specific "Poppy Section"?

## Metric Tracking
*   **Dictionary Coverage:** 55%
*   **Translation Completeness:** 100% of pages processed.
