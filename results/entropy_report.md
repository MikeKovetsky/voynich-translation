# Entropy Analysis Report
    
**Date:** 2025-11-27
**Input:** `data/eva_ivtff.txt`
**Script:** `research/entropy_check.py`

## 1. Voynich Entropy (Morphology)
Using standard morphology rules (prefixes/suffixes from `results/morphology_rules.json`).

| Component | Count | Unique | Entropy (Bits) |
|---|---|---|---|
| **Roots** | 10856 | 1922 | **7.0322** |
| **Suffixes** | 20406 | 11 | **3.0356** |
| **Prefixes** | 74783 | 38 | **4.7268** |

**Ratio (Root / Suffix):** 2.32

## 2. English Control (Comparison)
Sample text: `results/final_report_v10.md` (Final Report)
Simple stripping of (-s, -ed, -ing, -ly, -tion, -er, -est).

| Component | Count | Unique | Entropy (Bits) |
|---|---|---|---|
| **Roots** | 714 | 312 | **7.3389** |
| **Suffixes** | 168 | 7 | **2.1494** |

**Ratio (Root / Suffix):** 3.41

## 3. Conclusion
- **Hypothesis:** Roots should have High Entropy (Open Class), Suffixes should have Low Entropy (Closed Class).
- **Voynich Result:** The Root entropy is 7.03, and Suffix entropy is 3.04.
- **Interpretation:** 
  - If Root Entropy >> Suffix Entropy, the morphology model is likely correct (Suffixes are grammatical markers).
  - If Root Entropy is close to Suffix Entropy, the "Suffixes" might be part of the root (splitting is wrong).

**VERDICT: SUPPORTS HYPOTHESIS.** The high entropy gap suggests 'Root' and 'Suffix' function as distinct Open vs Closed classes, typical of natural language.
