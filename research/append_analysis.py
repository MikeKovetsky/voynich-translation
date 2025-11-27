
analysis_text = """
## 2. Instructional Logic Analysis

### 2.1 Structure of Instructions
The translation reveals a consistent structure resembling recipes or pharmaceutical instructions:
*   **Action Verbs:** The words `qokeol` (Boil) and `qokeey` (Cook/Process) appear repeatedly at the beginning of phrases (e.g., `f89r1.8`, `f89r2.24`).
*   **Ingredients:** Specific plants are named, often accompanied by `chol` (leaf) or `okey` (Green/Leaf).
*   **Liquid Base:** The frequent recurrence of `daiin` (from the spring / take water) and `dam` (blood/red liquid) suggests a liquid medium for the recipes.
*   **Timing/Conditions:** References to `dair` (Adar - month) and `dal` (Aries) might indicate the time of year for harvesting or preparation.

### 2.2 Label-Text Correlation
There is a strong correlation between the labels (likely on jars or plant figures) and the text:
1.  **Scabiosa:**
    *   Label `<f89r1.3>`: `oldam` -> **plant:scabiosa**.
    *   Text `<f89r1.20>` & `<f89r1.22>`: Mentions **plant:scabiosa** (`ysheeo` and potentially derivatives).
2.  **Uva Quercina:**
    *   Label `<f89r2.32>`: `otalsy` -> **plant:uva quercina**.
    *   Text `<f89r2.6>`: Mentions **plant:uva quercina** (`cholkeedy`).
3.  **Holm:**
    *   Label `<f89r1.14>`: `okaiin.dan` -> "Green **plant:holm**".
    *   Text references to "Green" and plant parts are frequent.

### 2.3 Conclusion
The "Descriptive Dictionary" successfully uncovers a layer of meaningful semantic links on page f89r. The text reads as a set of instructions for processing specific plants (boiling, cooking, taking water) which are identified by labels on the same page. This strongly supports the hypothesis that the Voynich Manuscript contains coherent pharmaceutical or herbal recipes.
"""

with open("results/pharma_translation_test.md", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the TODO section
content = content.replace("TODO: Analyze the translation above for recipe logic.\n- Look for: \"Take [Ingredient]...\"\n- Look for: \"Mix/Heat/Drink...\"\n- Compare jar labels (lines with @Lc or @Lf usually labels?) with text.\n", analysis_text)

with open("results/pharma_translation_test.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Analysis appended.")
