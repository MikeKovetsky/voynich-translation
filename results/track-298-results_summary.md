# Track 298 Results Summary: Narrative Deep Dive

## Hypothesis Evaluation
The "Narrative Grammar" model (SVO with `y-` articles and `-a/-n` verbs) was applied to f67v2.

### Findings
1. **Grammar Fit**:
   - **SVO Structure**: Weak fit. The text often starts lines with Verbs or Nouns without clear Subjects.
   - **Verbs**: The `-a/-n` suffix identifies about 12% of words as verbs. This is lower than expected for a narrative (usually 15-20%).
   - **Connectors**: `daiin` appears in f67v2 and f8v, supporting its role as a temporal marker ("Then").

2. **Proper Nouns**:
   - `TOL`, `EAIN`, `DAM` appear in key positions (e.g., Line 14, 18, 20).
   - Their placement (often at end of phrases or in lists) supports them being entities (People/Places).

3. **Comparison**:
   - **f67v2** (59 words): 1 `daiin`, 2 `y-` words.
   - **f8v** (102 words): 4 `daiin`, 0 `y-` words.
   - **f90r1** (69 words): 0 `daiin`, 7 `y-` words.
   - **Conclusion**: These pages are heterogeneous. f67v2 and f8v might be narrative, while f90r1 (high `y-` count) might be descriptive or a list of "The X".

## Next Steps
- Investigate the `y-` prefix in f90r1: Is it "The" or a preposition "In/At"?
- Refine Verb detection: Are there prefixes for verbs (e.g. `o-`, `q-`)?
