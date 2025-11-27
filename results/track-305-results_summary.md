# Track 305 Results Summary: Full Translation v2

## Global Coverage
- **Total Words**: 38782
- **Translated**: 29395
- **Coverage**: 75.80%
- **Comparison**: v1 was 19.1%. Improvement: 56.70%

## Coverage by Section
| Section | Total Words | Translated | Coverage |
|---------|-------------|------------|----------|
| Astronomical | 3068 | 1970 | 64.21% |
| Biological | 7144 | 5724 | 80.12% |
| Gap/Missing | 1243 | 976 | 78.52% |
| Herbal A | 4247 | 3285 | 77.35% |
| Herbal B | 6467 | 4920 | 76.08% |
| Pharmaceutical | 4094 | 2931 | 71.59% |
| Recipes | 10683 | 8202 | 76.78% |
| Rosettes | 1836 | 1387 | 75.54% |

## Analysis of Improvements
The **Biological Section** shows the highest coverage at **80.12%**, followed closely by the **Gap/Missing** pages (78.52%) and **Herbal A** (77.35%).
This suggests that our Contextual Mining (Track 303) and Morphology (Track 302) were particularly effective at capturing the repetitive technical vocabulary found in the biological and herbal descriptions.
The **Astronomical** section remains the most challenging (64.21%), likely due to unique label vocabulary not present in the training set for context mining.

## Next Steps
- Investigate the untranslated 20-35% in Astronomical/Pharmaceutical sections.
- Refine the "High Frequency Unknown" mappings (s, r, l) to ensure they aren't over-matching.
- Begin semantic analysis of the translated Biological text to extract narrative.
