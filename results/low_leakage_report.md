# Track 89: Low-Leakage Ingredient Analysis

## Methodology
Focus on words with <20% leakage into non-herbal sections.
Cross-reference with visual elements (roots, flowers, leaves) on expert-identified pages.

## Key Findings

### Target Word Analysis

#### `char`
- Herbal: 28, Recipe: 27
- Dominant visual: **flowers** (92.9%)
- Top plants: [('veratrum', 2), ('ipomea', 1), ('ricinus', 2)]
- **Inferred meaning: flower/blossom** [HIGH]

#### `chl`
- Herbal: 7, Recipe: 15
- Dominant visual: **roots** (100.0%)
- Top plants: [('atriplex', 1), ('lilium', 2), ('rumex', 1)]
- **Inferred meaning: root/underground part** [HIGH]

#### `ar`
- Herbal: 59, Recipe: 142
- Dominant visual: **flowers** (96.6%)
- Top plants: [('ipomea', 1), ('tussilago', 1), ('tragopogon', 2)]
- **Inferred meaning: flower/blossom** [HIGH]

#### `chol`
- Herbal: 216, Recipe: 62
- Dominant visual: **leaves** (93.1%)
- Top plants: [('veratrum', 5), ('arctostaphylis', 13), ('dictamnus', 7)]
- **Inferred meaning: leaf/foliage** [HIGH]

#### `chor`
- Herbal: 141, Recipe: 19
- Dominant visual: **leaves** (96.5%)
- Top plants: [('cyanus(', 1), ('arctostaphylis', 14), ('dictamnus', 6)]
- **Inferred meaning: leaf/foliage** [HIGH]

#### `kal`
- Herbal: 2, Recipe: 8
- Dominant visual: **roots** (100.0%)
- Top plants: [('eryngium', 1), ('glycyrrhiza', 1)]
- **Inferred meaning: root/underground part** [HIGH]

#### `kar`
- Herbal: 18, Recipe: 18
- Dominant visual: **roots** (100.0%)
- Top plants: [('lycopsis or a nearly allied boraginace plant', 3), ('mentha', 1), ('scabiosa', 1)]
- **Inferred meaning: root/underground part** [HIGH]

### Verified Ingredients (Zero/Low Leakage ≤10%)

| Word | Herbal | Recipe | Leakage | Visual | Meaning | Confidence |
|------|--------|--------|---------|--------|---------|------------|
| chan | 9 | 2 | 0.0% | roots (100%) | root/underground | HIGH |
| ochor | 5 | 1 | 0.0% | roots (100%) | root/underground | HIGH |
| qot | 6 | 2 | 0.0% | roots (100%) | root/underground | HIGH |
| cphor | 5 | 1 | 0.0% | roots (100%) | root/underground | HIGH |
| cphaiin | 6 | 1 | 0.0% | roots (100%) | root/underground | HIGH |
| chotaiin | 6 | 2 | 0.0% | leaves (100%) | leaf/foliage | HIGH |
| qod | 6 | 2 | 0.0% | flowers (100%) | flower/blossom | HIGH |
| ypchedy | 6 | 4 | 0.0% | roots (100%) | root/underground | HIGH |
| chain | 9 | 7 | 5.9% | roots (100%) | root/underground | HIGH |
| chokchy | 11 | 2 | 7.1% | flowers (100%) | flower/blossom | HIGH |
| opchy | 7 | 6 | 7.1% | roots (100%) | root/underground | HIGH |
| qotcho | 8 | 2 | 9.1% | roots (100%) | root/underground | HIGH |
| cthor | 39 | 1 | 7.0% | leaves (97%) | leaf/foliage | HIGH |
| chaiin | 34 | 7 | 6.8% | roots (94%) | root/underground | HIGH |
| kchy | 28 | 1 | 3.3% | roots (93%) | root/underground | HIGH |
| shaiin | 14 | 6 | 0.0% | roots (86%) | root/underground | HIGH |
| shory | 5 | 1 | 0.0% | roots (80%) | root/underground | HIGH |
| cthar | 19 | 1 | 4.8% | flowers (71%) | flower/blossom | MEDIUM |

### High-Confidence Plant Part Vocabulary

Based on visual correlation analysis:

**flower/blossom**: qod, chokchy
  - `qod`: [('sedum', 1), ('lychnis', 1), ('parietaria', 1)]
  - `chokchy`: [('polygonum', 1), ('botrychium', 1), ('delphinium', 1)]

**leaf/foliage**: chotaiin, cthor
  - `chotaiin`: [('geranium', 1), ('sedum', 1), ('lychnis', 1)]
  - `cthor`: [('cyanus(', 1), ('geranium', 3), ('ricinus', 1)]

**root/underground**: chan, ochor, qot, cphor, cphaiin, ypchedy, chain, opchy, qotcho, chaiin, kchy, shaiin, shory
  - `chan`: [('cyanus(', 1), ('arctostaphylis', 2), ('paris', 1)]
  - `ochor`: [('dictamnus', 1), ('hypericum', 1), ('uva quercina', 1)]
  - `qot`: [('dictamnus', 1), ('helleborus', 1), ('arctostaphylis', 1)]


## Summary Statistics
- Expert-identified folios: 134
- Low-leakage candidates: 42
- Verified ingredients: 18

## Recommendations
1. Words with HIGH confidence visual correlation should be added to dictionary
2. Focus on words appearing in 'Golden Intersection' (after daiin/ol)
3. Cross-validate with recipe context before finalizing meanings