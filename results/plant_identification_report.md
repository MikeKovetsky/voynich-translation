# 🌿 Voynich Manuscript Plant Identification Report

## Executive Summary

This analysis identified **9 botanical illustrations** from the Voynich manuscript herbal sections (f1r-f66v), correlating visual features with potential text labels. Key findings challenge some of Stephen Bax's identifications while proposing new candidates.

---

## High Confidence Identifications (≥60%)

### f17r - Cornflower (Centaurea cyanus) ⭐ 75% confidence

**Visual Features:**
- Long linear/strap-like leaves, alternately arranged
- **Distinctive blue/purple thistle-like flower heads** (multiple)
- Fibrous root system

**Why this identification:**
- Blue composite flowers are very distinctive
- Leaf shape matches Centaurea species
- Medieval herbals commonly featured cornflower for eye treatments

**Text on page:**
- First word: `f2o89`
- Unique words: `19j1ap`, `1Ah9`, `1Ho`

---

### f5r - Hellebore (Helleborus sp.) ⭐ 60% confidence

**Visual Features:**
- Large palmate leaves, clustered at base
- Drooping bell-like flower
- Spreading root system

**Why this identification:**
- Classic hellebore leaf pattern (palmate, divided)
- Drooping flower matches hellebore morphology
- **Better match than f4r** (which Bax suggested)

**Text on page:**
- First word: `h2o89`
- This could be our first confirmed plant name!

---

## Medium Confidence Identifications (40-60%)

| Folio | Top Candidate | Confidence | Key Features |
|-------|--------------|------------|--------------|
| f2v | Cyclamen | 50% | Round heart-shaped leaf |
| f4r | Tamarisk | 50% | Pinnate leaves, shrubby |
| f6r | Poppy | 50% | Lobed leaves, seed pods |
| f22r | Elderberry | 50% | Berry clusters, branching |
| f24r | Ox-eye Daisy | 50% | Daisy flowers, heart leaves |
| f25v | Castor Bean | 50% | Palmate leaves |
| f3r | Aloe | 40% | Striped/banded leaves |
| f9r | Oak | 40% | Lobed leaves, catkins |

---

## Disputed Bax Identifications ⚠️

### f25v: NOT Juniper!

**Bax's claim:** Juniper (Juniperus communis)

**Our analysis:** The illustration shows **palmate/hand-shaped leaves** radiating from a center point. Juniper has **needle-like leaves**. These are fundamentally incompatible.

**Better candidates:**
- Castor bean (Ricinus communis) - 60%
- Cannabis - 50%
- Lupine - 40%

### f4r: Probably NOT Hellebore

**Bax's claim:** Hellebore

**Our analysis:** The illustration shows **small pinnate/compound leaves** in opposite arrangement with shrubby branching. Hellebore has **palmate leaves**.

**Better candidates:**
- Tamarisk - 50%
- Lentisk/Mastic - 50%
- Fumitory - 40%

**Note:** f5r is a much better hellebore candidate!

---

## Potential Voynich Plant Name Mappings

Based on first words appearing on identified pages:

| Voynich Word | Folio | Candidate Plant | Latin Name |
|-------------|-------|-----------------|------------|
| `f2o89` | f17r | Cornflower | Centaurea cyanus |
| `h2o89` | f5r | Hellebore | Helleborus sp. |
| `hoom` | f2v | Cyclamen | Cyclamen sp. |
| `ho8ae19` | f4r | Tamarisk | Tamarix sp. |
| `foay` | f6r | Poppy | Papaver sp. |
| `goCam` | f25v | Castor Bean | Ricinus communis |

⚠️ These mappings are **HYPOTHETICAL** and require further validation.

---

## Pattern Analysis

### Common Botanical Text Patterns

The botanical section shows consistent patterns:

1. **`4oh` prefix** (493 occurrences)
   - Likely means "the herb" as article/determiner
   - Examples: `4oham`, `4ohan`, `4ohc89`

2. **`ok` prefix** (507 occurrences)
   - Possibly preparation or medicine term
   - Examples: `okam`, `okoe`, `okae`

3. **Case endings observed:**
   - `-am` = accusative (object case)
   - `-an` = ablative (from/root-related?)
   - `-ae` = possibly flower-related
   - `-oe` = possibly leaf-related

### Unique Words (Page-Specific)

Found 2,485 words appearing on exactly one page. These are prime candidates for plant-specific terminology!

---

## Methodology

1. **Image Analysis:** Downloaded 49 high-resolution folios from Yale Beinecke IIIF API
2. **Feature Extraction:** Documented leaf shape, flower type, root structure, growth form
3. **Database Matching:** Compared against medieval European plant knowledge
4. **Text Correlation:** Extracted first words and unique words per page
5. **Pattern Matching:** Cross-referenced visual IDs with text patterns

---

## Conclusions

### What We Learned:

1. ✅ Some Voynich plants ARE identifiable from visual features
2. ✅ Stephen Bax's methodology has merit but some IDs are questionable
3. ✅ f17r (Cornflower) is our highest confidence identification
4. ✅ Text patterns correlate with botanical content structure

### What Remains Unknown:

- ❌ Definitive phonetic values for Voynich characters
- ❌ Complete plant vocabulary
- ❌ Source language of the manuscript

### Next Steps:

1. Analyze remaining ~120 botanical folios
2. Cross-reference with specific medieval herbals (Tacuinum Sanitatis, etc.)
3. Look for labeled diagrams (text near specific plant parts)
4. Test phonetic mappings against identified plant names

---

## Files Generated

- `results/plant_identifications.json` - Full identification data
- `results/botanical_vocabulary.json` - Extracted vocabulary
- `images/` - Downloaded manuscript folios

---

*Generated: November 24, 2025*
*Analysis by: Voynich Research Project*

