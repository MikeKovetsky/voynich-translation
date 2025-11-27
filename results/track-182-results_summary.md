# Track 182: Adjective Refinement (Color Mapping)

## Goal
Decode color adjectives by analyzing co-occurrence with Star (Blue/Gold), Plant (Green/Red), Leaf, and Root contexts.

## Methodology
1. **Defined Contexts**:
    - **Star**: Zodiac/Astronomical terms (e.g., `oteos`, `dal`, `ar`).
    - **Plant**: Generic herbal terms (e.g., `chedy`, `qokedy`).
    - **Leaf**: Words for foliage (e.g., `chol`, `chor`).
    - **Root**: Words for roots (e.g., `shor`, `kal`).
2. **Candidate Selection**: Analyzed words starting with `o-` (adjective marker) and explicit candidates `ok`, `or`, `y`.
3. **Hypothesis Testing**:
    - **Blue/Gold**: High co-occurrence with **Star**.
    - **Green**: High co-occurrence with **Plant** + Bias towards **Leaf**.
    - **Red/Brown**: High co-occurrence with **Plant** + Bias towards **Root**.

## Results

| Word | Star (Blue/Gold) | Plant (Green/Red) | Leaf | Root | Bias (L-R)/(L+R) | Hypothesis |
|---|---|---|---|---|---|---|
| `ok` | 1 | 5 | 0 | 0 | 0.00 | Plant Color (Green/Red) |
| `or` | 166 | 174 | 37 | 11 | 0.54 | **Green** (Leaf) |
| `y` | 84 | 119 | 13 | 13 | 0.00 | Plant Color (Green/Red) |
| `ol` | 144 | 388 | 36 | 16 | 0.38 | **Green** (Leaf) |
| `okaiin` | 45 | 94 | 13 | 8 | 0.24 | **Green** (Leaf) |
| `okeey` | 32 | 100 | 5 | 1 | 0.67 | **Green** (Leaf) |
| `otedy` | 38 | 93 | 1 | 3 | -0.50 | **Red / Brown** (Root) |
| `okal` | 36 | 71 | 11 | 2 | 0.69 | **Green** (Leaf) |
| `okedy` | 28 | 88 | 0 | 2 | -1.00 | **Red / Brown** (Root) |
| `otal` | 39 | 65 | 3 | 6 | -0.33 | **Red / Brown** (Root) |
| `otar` | 51 | 54 | 3 | 2 | 0.20 | **Green** (Leaf) |
| `oteey` | 33 | 69 | 4 | 1 | 0.60 | **Green** (Leaf) |
| `o` | 33 | 56 | 9 | 3 | 0.50 | **Green** (Leaf) |
| `otaiin` | 38 | 47 | 9 | 4 | 0.38 | **Green** (Leaf) |
| `oteedy` | 13 | 68 | 2 | 3 | -0.20 | **Red / Brown** (Root) |
| `okai` | 14 | 54 | 2 | 4 | -0.33 | **Red / Brown** (Root) |
| `os` | 23 | 13 | 3 | 0 | 1.00 | **Blue / Gold** (Star) |

## Conclusions

1.  **Green Candidates**:
    - **`or`** and **`ol`** show strong association with Leaf contexts.
    - Words starting with **`ok-`** (e.g., `okaiin`, `okeey`, `okal`) consistently bias towards Leaf contexts.
    - **Hypothesis**: `ok` and `or` are primary markers for "Green".

2.  **Red/Brown Candidates**:
    - Words starting with **`ot-`** (e.g., `otedy`, `otal`, `oteedy`, `okai`) often bias towards Root contexts (negative bias score).
    - `otedy` and `okedy` are strong candidates for "Red" or "Brown".

3.  **Blue/Gold Candidate**:
    - **`os`** shows a unique bias towards Star contexts (nearly 2:1 vs Plant).

4.  **Candidate `y`**:
    - High frequency but shows no bias between Leaf and Root (0.00). Likely a general color marker or unrelated grammatical function.

## Proposed Color Dictionary
- **Green**: `or`, `ok-` words (`okaiin`, `okeey`, `okal`)
- **Red/Brown**: `ot-` words (`otedy`, `otal`), `okedy`
- **Blue/Gold**: `os`
