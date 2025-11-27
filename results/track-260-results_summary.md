# Control Test Results Summary

## Statistics
- Total Words Processed: 6866
- Imperative Commands (-y): 3649 (53.1%)
- Mix/Process Markers (ed): 1924 (28.0%)
- Ingredient Markers (ol): 233 (3.4%)

## Analysis
### Does it read like a recipe?
No. The application of Recipe Grammar to the Bio section produces coherent nonsense. The text becomes a repetitive stream of 'Process/Mix' commands (due to high frequency of 'ed' and '-y') with very few distinct ingredients.

### Semantic Coherence
Applying recipe grammar to biological text resulted in:
- **Repetitive Commands:** Strings of 4-5 'Imperatives' in a row.
- **Lack of Objects:** 'Mix' commands often appear without ingredients.
- **Double Markers:** 'ol ol' (With With) appears, which is syntactically invalid in the recipe grammar.
- **High Density of 'ed':** In Bio text, 'ed' (often 'chedy', 'shedy') is extremely common, leading to an absurdity of 'Process' instructions.

## Conclusion
Grammar Falsification Status: **PASS**.
The 'Recipe Grammar' (y=Command, ol=Ingredient, ed=Mix) is NOT generic. It fails to produce meaningful text when applied to the Bio section. This confirms that the grammar is likely specific to the Recipe section (or that 'shedy/chedy' function differently in Bio contexts).