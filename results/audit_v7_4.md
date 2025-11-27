# Audit Report v7.4

## 1. Entropy Analysis (2nd-order)
- **Voynich Raw Text**: 2.1398 bits/char
- **English Translation**: 3.2042 bits/char

**Conclusion:**
FAIL: Significant difference (1.06 bits).

## 2. Zipf's Law Check
- **R-squared (Log-Log)**: 0.7961
- **Top 10 Translated Words**:
  - PLANT_TERM: 660
  - LEAF/FOLIAGE: 637
  - THE/OF: 525
  - MIXTURE/DECOCTION: 496
  - PRIEST/COHEN: 487
  - SPRING/SOURCE: 457
  - WHICH/THAT: 425
  - ONE: 402
  - ARIES: 354
  - OR/AND: 350

**Conclusion:**
FAIL: Does not look like natural language distribution.

## 3. Repetition Analysis
- **Voynich Repetition Rate**: 2.7071%
- **Translation Repetition Rate**: 8.3942%

**Conclusion:**
FAIL: Repetition rate changed significantly (Diff: 5.69%).
