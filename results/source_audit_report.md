# Voynich Source Audit Report

## 1. Images
**Status: INCOMPLETE**
- **Available:** 49 images (f1r - f26r, approximately).
- **Missing:** 153 folios (f26v onwards).
- **Coverage:** ~25% of the manuscript.

## 2. Transliteration
**Status: COMPLETE & CORRECT**
- **Source File:** `data/eva_ivtff.txt`
- **Format:** IVTFF (Interlinear Archive)
- **Folio Count:** 202 entries (102 unique folio numbers, 101 recto / 101 verso).
- **Sequence:** Covers f1 to f116.
- **Gaps:** The missing folio numbers (12, 59-64, 74, 91-92, 97-98, 109-110) correspond to known missing leaves in the manuscript history.
- **Data Quality:** The file contains valid IVTFF markup. Some lines contain special markup characters (`<...>`, `$`, `!`) which are standard for this format but may need cleaning for pure text analysis.

## 3. Recommendations
1.  **Acquire Missing Images:** We need to download or add the remaining images (f26v - f116v) to perform visual analysis on the full manuscript.
2.  **Transliteration Parser:** Ensure any analysis scripts can handle or strip the IVTFF specific markup (`<...>`, `$`) found within the text lines.
