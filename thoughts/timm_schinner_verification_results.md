# Verification of Timm & Schinner (2019) Claims

## Data
- **File**: `data/transliteration/RF1b-e.txt` (IVTFF, Eva)
- **Tokens**: 37,781
- **Unique**: 8,766
- **Lines**: 5,377

## Zipf
- **Slope**: -0.8725

Top 10 tokens:
1. daiin (711)
2. aiin (565)
3. ol (520)
4. chey (495)
5. ar (406)
6. qokeey (366)
7. chol (360)
8. or (357)
9. shey (339)
10. chedy (327)

## Local similarity (edit-distance)
Window = 10. MMLD evaluated on the first 10,000 comparisons.

### Flat window (global)
- **actual**: 2.2938
- **full shuffle**: 2.7037
- **gap**: 0.4099

### Line-aware (actual)
- **flat**: 2.2938 (n=10000)
- **same line**: 3.2142 (n=8542)
- **prev line**: 2.7082 (n=10000)

### Null models (preserve line lengths)
- **keep_shape** (shuffle all tokens, keep line lengths): flat=2.6936 line=3.6623 prev=3.0331
- **within_line** (shuffle tokens within each line): flat=2.2975 line=3.2264 prev=2.7072
- **line_order** (shuffle order of lines): flat=2.5792 line=3.1765 prev=3.5526

## What this suggests
- **Local similarity is real**: actual vs shuffle shows a ~0.41 MMLD gap.
- **The strongest structure is line-to-line**: shuffling line order makes `prev` much worse (2.71 → 3.55), consistent with adjacency between consecutive lines.
- **Within-line order matters surprisingly little**: shuffling within lines barely changes the flat-window score (2.2938 vs 2.2975), so the signal is not mainly from exact word order within a line.

## Controls (natural language, reshaped to VMS line lengths)
We reshaped each control text into the same line-length sequence as VMS (same number of tokens per line), then measured the **prev-line** MMLD before and after shuffling the order of lines.

Metric shown: `prev(actual)`, `prev(line_order)`, and Δ = `line_order - actual` (bigger Δ = stronger dependence on adjacent-line order).

- **VMS**: 2.7082 → 3.5526 (Δ=0.8444, rel=0.3118)
- **English (Gutenberg 1661)**: 3.0487 → 3.3458 (Δ=0.2971, rel=0.0975)
- **Italian (Gutenberg 1012)**: 2.9475 → 3.2559 (Δ=0.3084, rel=0.1046)
- **Latin (Gutenberg 218)**: 4.4031 → 4.9270 (Δ=0.5239, rel=0.1190)

Takeaway: **yes**, naturally written text shows an adjacent-line effect too, but in these samples the VMS adjacent-line effect is ~2.5–3× larger in relative terms.

## Naibbe cipher (Greshko 2025) ciphertext controls
We implemented a minimal Naibbe-cipher generator using the six encryption tables (α, β1–β3, γ1–γ2) from the paper and generated ciphertexts from Latin/Italian plaintexts.

Implementation notes:
- Plaintext is reduced to letters and respaced into unigrams/bigrams using the paper’s 2-dice scheme (47.2%–52.8% split).
- Each plaintext letter is encrypted using one of the six tables sampled with weights 5:2:2:2:1:1.
- Unigrams become a full “Voynichese” word; bigrams become prefix+suffix concatenations.
- Ciphertexts are reshaped into the VMS line-length sequence so our line-aware metrics are comparable.

Results (same Δprev metric as above; and normalized k-curves):
- **nb_it_1012**: prev(actual)=3.0652 prev(line_order)=3.3849 Δ=0.3197; k10(prev)=0.469
- **nb_la_0218**: prev(actual)=3.0395 prev(line_order)=3.3513 Δ=0.3118; k10(prev)=0.465

Interpretation:
- Naibbe ciphertexts land **between** VMS and natural-language plaintexts on k10(prev) (closer to VMS than plaintext controls), showing that **ciphertext can reproduce part of the “low-distance” signature**.
- But Naibbe ciphertexts do **not** reproduce VMS’s large global adjacent-line Δprev; their Δprev is similar to English/Italian plaintext controls. This supports the idea that VMS’s big Δprev is dominated by **folio/section mixing** (topic/vocabulary clustering), not only by a local word-generation mechanism.

## Deeper check: k-curves (normalized edit distance)
To reduce sensitivity to different word lengths, we also measured **normalized** Levenshtein distance \(d / \max(|a|,|b|)\).

For each token, we take the last \(k\) tokens from the candidate pool and record the **minimum** distance; then average across many tokens. We show two pools:
- **prev**: last \(k\) tokens of the previous line
- **line**: last \(k\) tokens earlier in the same line

Window max \(k=10\). Values below are means.

- **VMS**
  - prev: k1=0.813 k2=0.686 k3=0.616 k5=0.536 k10=0.445
  - line: k1=0.770 k2=0.670 k3=0.611 k5=0.549 k10=0.539
- **English (1661)**
  - prev: k1=0.884 k2=0.807 k3=0.752 k5=0.678 k10=0.575
  - line: k1=0.896 k2=0.822 k3=0.767 k5=0.693 k10=0.601
- **Italian (1012)**
  - prev: k1=0.883 k2=0.809 k3=0.756 k5=0.687 k10=0.576
  - line: k1=0.890 k2=0.823 k3=0.766 k5=0.699 k10=0.599
- **Latin (218)**
  - prev: k1=0.861 k2=0.793 k3=0.753 k5=0.699 k10=0.620
  - line: k1=0.861 k2=0.798 k3=0.755 k5=0.705 k10=0.624

Interpretation:
- The VMS curve drops **much faster** as \(k\) increases, especially for **prev-line** candidates (0.813 → 0.445 by k=10).
- In the controls, curves are flatter; even at k=10, normalized distances stay around ~0.57–0.62.
- VMS also shows a notable divergence between **prev** and **line** at k=10 (0.445 vs 0.539), consistent with “best matches” being unusually concentrated in the immediately preceding line rather than within the same line.

## Multi-seed sims (null stability)
We repeated the null-model shuffles across 20 random seeds, using only the first 2,000 comparisons (faster, but stable enough for variance).

### Adjacent-line dependence (line_order)
Statistic: Δprev = `prev(line_order) - prev(actual)` (bigger Δ = stronger dependence on real adjacent-line order).

- **VMS**: 0.7424 ± 0.0641 (eff=11.59)
- **English (1661)**: 0.1744 ± 0.0632 (eff=2.76)
- **Italian (1012)**: 0.3281 ± 0.0675 (eff=4.86)
- **Latin (218)**: 0.5892 ± 0.0614 (eff=9.60)

### VMS group shuffles (where does Δprev come from?)
Same Δprev statistic, but shuffling line order **within** groups:

- **within_fol** (shuffle lines within each folio/page only): 0.0699 ± 0.0288 (eff=2.43)
- **within_sec** (shuffle lines within each section only): 0.4409 ± 0.0586 (eff=7.53)

Interpretation:
- Most of the global `line_order` effect is **not** “line order within a page”; it is explained by **mixing across folios/pages** (and their different vocab/structure).
- There is still a smaller residual effect inside a folio (within_fol), but it’s much weaker.

## Position check: are line-start edits special?
We computed nearest-neighbor ops separately for:
- **start**: first token of a line matched to the last 10 tokens of the previous line
- **inln**: non-first tokens matched to the previous 10 tokens within the same line

Sample size: first ~2,000 in-line comparisons, and 361 line starts (shape-matched across corpora).

Fractions shown: `d1` (edit distance 1) and a few coarse op classes.

- **VMS**
  - start: d1=0.12 pre_add=0.07 suf_add=0.02 pre_sub=0.03 other=0.82
  - inln : d1=0.10 pre_add=0.05 suf_add=0.02 pre_sub=0.01 other=0.85
- **English (1661)**
  - start: d1=0.04 pre_add=0.02 suf_add=0.03 pre_sub=0.01 other=0.80
  - inln : d1=0.05 pre_add=0.01 suf_add=0.03 pre_sub=0.02 other=0.87
- **Italian (1012)**
  - start: d1=0.16 pre_add=0.07 suf_add=0.07 pre_sub=0.06 other=0.68
  - inln : d1=0.09 pre_add=0.06 suf_add=0.02 pre_sub=0.05 other=0.80
- **Latin (218)**
  - start: d1=0.04 pre_add=0.00 suf_add=0.01 pre_sub=0.01 other=0.93
  - inln : d1=0.02 pre_add=0.00 suf_add=0.01 pre_sub=0.01 other=0.95

### VMS line-start pre_add under group shuffles
To see if line-start “prefix additions” depend on real adjacency, we shuffled line order within groups and recomputed `pre_add(start)`:

- **actual**: 0.069
- **within_fol**: 0.065 ± 0.012
- **within_sec**: 0.058 ± 0.014

Takeaway:
- VMS has a small start-vs-in-line difference in this coarse metric, but **it does not strongly depend on adjacency** (stable under within-folio shuffles).
- Some natural text (Italian here) can show equal or stronger line-start editability under the same coarse measurement, so this is **not yet diagnostic** of a copy/modify generator.

### k-curves under nulls (prev, normalized; k up to 10)
We compare actual `k10(prev)` to the distribution under nulls.

- **VMS**: k10(prev)=0.408
  - keep_shape mean k10(prev)=0.486 (z10=5.60)
  - within_line mean k10(prev)=0.409 (z10=0.75)
- **Latin (218)**: k10(prev)=0.578
  - keep_shape mean k10(prev)=0.638 (z10=5.26)
  - within_line mean k10(prev)=0.579 (z10=0.77)

Takeaway:
- `within_line` barely changes the prev-line curve, so the signal is not mainly “within-line word order”.
- `keep_shape` is much worse than actual (high z10) for both VMS and Latin, so this effect is not unique to VMS; it can also arise in natural language under this metric.

## Nearest-neighbor “edit op” fingerprint (actual)
Window = 10. First 10,000 comparisons.

- **flat**: d0=0.07 d1=0.20 d2=0.32; other=0.71 pre_add=0.09 same=0.07 pre_sub=0.04 suf_sub=0.03 suf_add=0.03
- **line_start**: n=1861 d0=0.01 d1=0.13 d2=0.21; other=0.83 pre_add=0.07 pre_sub=0.04 suf_add=0.02 same=0.01 both_add=0.01
- **in_line**: n=10000 d0=0.03 d1=0.11 d2=0.20; other=0.83 pre_add=0.06 same=0.03 pre_sub=0.02 suf_add=0.02 suf_sub=0.02

## Reproduce
```bash
python3 scripts/verify_timm_schinner.py
```
