# Track 244: Plant Noun Miner Results

## Overview
- **Goal**: Mass-identify unknown words likely to be Plant names in the Herbal Section (f1-f66).
- **Input**: `data/eva_ivtff.txt` (Book II: f1-f66), `results/dictionary/dictionary.json`.
- **Output**: `results/mining/plant_candidates.json`.

## Methodology
1.  **Data Source**: Parsed `eva_ivtff.txt`, extracting lines for folios 1r to 66v.
2.  **Filtration**: Filtered for words NOT present in the current `dictionary.json`.
3.  **Scoring**:
    -   Base score: Frequency of appearance (across all transcription versions H, C, F, N, U, etc., acting as a consensus mechanism).
    -   Bonus +1: Word starts with `o-` (common noun marker in Herbal).
    -   Bonus +1: Word starts with `ch-`.
    -   Bonus +3: Preceded by `o`.
    -   Bonus +5: Followed by `otar` (Green [Plant]).
    -   Bonus +5: Followed by `oteey` (Leafy [Plant]).

## Findings
- **Total Candidates Found**: 4,967 unique unknown words.

### Top Candidates by Score/Frequency
| Word | Score | Count | Patterns |
|------|-------|-------|----------|
| **okam** | 83 | 83 | `starts_with_o` |
| **chky** | 64 | 64 | `starts_with_ch` |
| **chckhy** | 51 | 51 | `starts_with_ch` |
| **oteody** | 51 | 51 | `starts_with_o` |
| **oteeo** | 46 | 46 | `starts_with_o` |

### Contextual Highlights
Candidates found in specific structural contexts (likely strong plant name candidates):

#### Followed by "otar"
- **okar**: `starts_with_o`, `followed_by_otar`
- **okal**: `starts_with_o`, `followed_by_otar`
- **qokal**: `followed_by_otar`

#### Followed by "oteey"
- **oiin**: `starts_with_o`, `followed_by_oteey`
- **okaiin**: `starts_with_o`, `followed_by_oteey`

## Notes & Limitations
- **Transcription Redundancy**: The script processes all available transcription versions (H, C, F, N, U) for each line. This inflates the absolute `count`, but serves as a useful "validity check"—words that appear in multiple transcriptions will naturally bubble up.
- **Noise**: Many low-frequency candidates (count < 5) are likely transcription errors or hapax legomena.
- **Next Steps**: These candidates should be cross-referenced with morphology rules to filter out likely verbs or grammatical particles.
