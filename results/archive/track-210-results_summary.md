# Track 210 Results Summary: Dictionary Update v9.4

## Overview
This update incorporates newly discovered measurement units and numbers into the Voynich dictionary, specifically focusing on units derived from Latin medical texts (Cyathus, Manipulus) and basic numerals.

## Changes
### New/Updated Entries
| Voynich | Meaning | Category | Note |
| :--- | :--- | :--- | :--- |
| `saiin` | unit:cup | Measurement | Cyathus |
| `ar` | unit:handful | Measurement | Manipulus |
| `ii` | number:2 | Measurement | |
| `daiin` | unit:cup_variant/verb:take_water | Measurement | |
| `qok` | verb:take/mix | Measurement | Refined definition (Rx context) |

## Methodology
- **Source**: Track 210 analysis.
- **Integration**: Entries were tagged with `semantic_category: "Measurement"` to facilitate downstream parsing of recipes.
- **Refinement**: The verb `qok` was refined to reflect its usage in recipe contexts as "take" or "mix", aligning with standard medical recipe structures.

## Next Steps
- Apply these new definitions to re-translate recipe sections.
- Validate the "cup" vs "take water" ambiguity for `daiin` in more contexts.
