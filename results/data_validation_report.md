# Data Validation Report

## Critical Finding

Two transcription systems in use: Claston (voynich_raw.txt) and EVA (eva_ivtff.txt). 24 scripts use Claston, 6 use EVA. This inconsistency could explain analysis failures.

## Scripts Audit

| System | Count |
|--------|-------|
| Claston | 24 |
| EVA | 6 |

### Scripts Using Claston (voynich_raw.txt)

- `botanical_decode.py`
- `latin_decoder.py`
- `cross_section.py`
- `phrase_patterns.py`
- `verb_hunting.py`
- `vocab.py`
- `herbal_compare.py`
- `latin_abbrev.py`
- `hungarian_turkish.py`
- `anchor.py`
- `basque_validation.py`
- `track1_language_comparison.py`
- `identify_plants.py`
- `phonetic.py`
- `decoder.py`
- `botanical.py`
- `word_grammar.py`
- `compare_languages.py`
- `analyze.py`
- `latin_cipher.py`
- `decode.py`
- `plants.py`
- `cipher.py`
- `astro.py`

### Scripts Using EVA (eva_ivtff.txt)

- `eva_analysis.py` (transcriber: H)
- `sentence.py` (transcriber: H)
- `verb_context.py` (transcriber: H)
- `common_words.py` (transcriber: H)
- `translate.py` (transcriber: H)
- `key_validation.py` (transcriber: H)

## Character Mapping Verification

| Claston | EVA | Verified |
|---------|-----|----------|
| o | o | ✓ |
| a | a | ✓ |
| s | s | ✓ |
| f | f | ✓ |
| i | i | ✓ |
| n | n | ✓ |
| 9 | y | ✓ |
| 8 | d | ✓ |
| h | k | ✓ |
| k | t | ✓ |
| e | l | ✓ |
| y | r | ✓ |
| c | e | ✓ |
| 4 | q | ✓ |
| g | p | ✓ |
| p | m | ✓ |
| am | aiin | ✓ |
| aim | aiiin | ✗ |
| an | ain | ✓ |
| M | iin | ✓ |

## Transcriber Comparison

- Words sampled: 471
- Recommended transcriber: **H** (Takahashi)

| Comparison | Disagreements |
|------------|---------------|
| H_vs_H | 115 |
| H_vs_C | 165 |
| H_vs_F | 137 |
| H_vs_N | 81 |
| H_vs_U | 93 |

## Data Reconciliation

- Lines compared: 75
- Full matches: 24
- Partial matches: 18
- Mismatches: 10

### Sample Conversions

| Claston | Converted | EVA | Match |
|---------|-----------|-----|-------|
| fa19s | fachys | fachys | ✓ |
| 9,hae | ykal | ykal | ✓ |
| ay | ar | ar | ✓ |
| Akam | taiin | ataiin | ✗ |
| 2oe | shol | shol | ✓ |
| soy9 | sory | sory | ✓ |
| Hay | ar | ckhar | ✗ |
| oy,9 | ory | y | ✗ |
| hacy | kaer | kair | ✗ |
| 1kam | chtaiin | chtaiin | ✓ |

## Recommendation

**Standardize on: EVA**

Reasons:
- EVA is the standard in Voynich research literature
- EVA has multiple transcribers for cross-validation
- EVA is more widely documented and referenced
- Takahashi's (H) transcription is complete and recent

## Next Steps

1. Use `voynich_data.py` as the single data access module
2. Update analysis scripts to use EVA via the master module
3. Re-run key analyses with consistent data source
4. Deprecate direct use of voynich_raw.txt in new scripts
