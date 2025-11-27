# Task 168: Noun Clustering Results

## Findings
Clustered 1725 nouns into 72 semantic groups based on context. We used TF-IDF to identify the most significant "Context Root" for each noun.

## Top Clusters & Hypotheses

| Context Root | Count | Possible Meaning (from Task 165/167) | Hypothesis for Cluster |
|--------------|-------|--------------------------------------|------------------------|
| **ed** | 48 | Unknown (suffix/root?) | **Processed Items?** (Verbal adjective context) |
| **al** | 44 | Associated with `ol` (The/Of)? | **Genitive Nouns?** (Possessed items) |
| **ar** | 44 | "Earth" / "To" | **Locations / Materials** (Found in ground?) |
| **ai** | 39 | "Water" / "One" | **Liquids / Units** |
| **hy** | 35 | Unknown | **Abstract Concepts?** |
| **ey** | 34 | Unknown | **Descriptive Category A** |
| **or** | 34 | Variant of `ar`? | **Locations B** |
| **ee** | 33 | "Do" / "Make" (Verb) | **Crafted Items / Ingredients** (Things that are "made") |
| **eo** | 32 | Unknown | **Descriptive Category B** |
| **in** | 30 | Suffix-like? | **Properties?** |

## Conclusion
The nouns strictly group by their associated roots. The presence of distinct clusters around `ai` (Water) and `ar` (Earth) supports the semantic clustering hypothesis. The largest cluster `ed` requires further investigation into the meaning of root `ed`.
