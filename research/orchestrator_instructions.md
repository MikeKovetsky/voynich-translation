# Orchestrator Pre-Flight Instructions ✈️📋

Before starting ANY new research task or iteration, you MUST perform this check.

## 1. The Memory Check (Do not reinvent the wheel)
*   **Read:** `artifacts/established_truths.md`
*   **Read:** `artifacts/rejected_hypotheses.md`
*   **Action:** If your proposed task overlaps with a "Rejected Hypothesis" (e.g. Phonetic Latin), **STOP**. If it overlaps with an "Established Truth" (e.g. `daiin` analysis), **STOP**.

## 2. The Status Check (Where are we?)
*   **Read:** `results/dictionary/master_dictionary_v20.json` (Just the metadata/stats, not the whole file).
*   **Metric:** Look for `translation_status` distribution.
    *   **Status 0 (Confirmed):** The anchors.
    *   **Status 1 (Proposed):** The theories.
*   **Action:**
    *   If Confirmed Coverage is **< 10%**: Your PRIORITY is **Grounding** (finding anchors). Do not do syntax/grammar until you have anchors.
    *   If Confirmed Coverage is **> 50%**: Your PRIORITY is **Grammar/Syntax** (connecting the anchors).

## 3. The Conflict Check (Do not contradict)
*   **Before:** Defining a word (e.g. "Let's assume `chol` is Star").
*   **Action:** Grep `master_dictionary_v20.json` for `chol`.
*   **Logic:** If `chol` is already defined as "Leaf" (Status 0), you CANNOT redefine it without overwhelming evidence.

## 4. The Context Check (Look at the picture)
*   **Before:** Translating any folio (e.g. `f70r`).
*   **Action:** Grep `data/external_corpora/sherwood_plant_mapping.csv` and `results/local_variable_map.csv`.
*   **Logic:**
    *   If Sherwood says f70r is "Aries/Nettle", you MUST look for "Mars/Fire/Sting" words.
    *   If `local_variable_map` says `oteos` appears on f70r, you MUST account for `oteos`.

## 5. The Web Sync Check
*   **Action:** Ensure `web/src/data/dictionary.json` is updated with the latest `results/dictionary/master_dictionary_v20.json` periodically.
*   **Logic:** The Web UI is our "Scoreboard". If it's outdated, we are flying blind.

---
**Run Command:** `python3 research/preflight_check.py` (To be created in Track 365)
