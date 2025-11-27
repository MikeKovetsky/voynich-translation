# Track 229: Recipe Structural Parser Summary

## Overview
This task focused on analyzing the sentence structure of Quire 20 (Recipe Section, f103r-f116v) using Dictionary v9.1 definitions. The goal was to identify "Slots" for unknown words by observing their context relative to known markers like `ARTICLE_THE` (`ol`) and `CONNECTOR_AND` (`y`).

## Methodology
1. **Input**: 
   - Dictionary: `results/dictionary/dictionary.json` (v9.1)
   - Text: `data/eva_ivtff.txt` (Quire 20)
2. **Tokenization**:
   - Sentences were split by newlines (original physical lines) and the word `daiin` (COMMAND_TAKE).
   - Words were cleaned of standard punctuation.
3. **Mapping**:
   - `daiin` -> `COMMAND_TAKE`
   - `y` -> `CONNECTOR_AND`
   - `ol` -> `ARTICLE_THE`
   - `qokeedy` -> `NOUN_MIXTURE`
   - Other words mapped to dictionary `meaning`.
   - Words not in dictionary -> `UNKNOWN`.

## Results

### Files Produced
- `results/recipe_structure_v3.json`: Contains abstract patterns for ~1200 sentences.
- `results/structural_guesses.json`: Contains inferred types for unknown words based on their slots.

### Key Findings
1. **Sentence Structure**:
   - `COMMAND_TAKE` (`daiin`) effectively segments the text into instruction-like units.
   - `ARTICLE_THE` (`ol`) is a frequent marker.

2. **Slot Analysis**:
   - **Noun Ingredients**: We looked for the pattern `ARTICLE_THE + UNKNOWN + CONNECTOR_AND` (`ol ... y`). While `ARTICLE_THE` and `CONNECTOR_AND` appear, this specific rigid slot did not yield high-frequency candidates for a single unknown word. This suggests that either the structure is more flexible (e.g., multiple words between markers) or `y` often functions as a prefix rather than a standalone word in the transcription.
   - **Verbs/Processes**: Words appearing at the end of sentences were flagged as potential `VERB_PROCESS`. Candidates include `olshedy`, `ofcho`, `sarain`.
   - **Artifacts**: Some candidates retained transcription markers (e.g., `olshedy<$`), indicating complex line-end phenomena or attached metadata in the source text.

## Limitations & Next Steps
- **Tokenization**: The "word" concept in Voynich is fluid. `y` often appears attached to other words (`y-`), which simple space-based tokenization misses. Future parsers should handle prefix splitting.
- **Dictionary Coverage**: Many words remain `UNKNOWN`, limiting the resolution of patterns.
- **Transcription**: Using `F` (Friedman) or `H` (Takahashi) transcriptions yields different segmentation. We prioritized `F` where available.

## Conclusion
The structural parsing successfully generated abstract patterns. While "magic bullets" (unknowns with 99% certainly due to fixed slots) were rare, the generated patterns provide a foundation for syntactic analysis.
