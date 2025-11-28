# Compression Analysis (Information Density)

| Dataset | Original Size | Zlib Size | LZMA Size | Zlib BPC | LZMA BPC | Ratio (Zlib) |
|---|---|---|---|---|---|---|
| Voynich (EVA) | 257258 | 82247 | 75008 | 2.56 | 2.33 | 3.13 |
| Latin (Medical) | 257258 | 5275 | 2920 | 0.16 | 0.09 | 48.77 |
| Random Scramble | 257258 | 155840 | 142412 | 4.85 | 4.43 | 1.65 |
| English (Sample) | 263070 | 833 | 216 | 0.03 | 0.01 | 315.81 |

## Character Entropy (0-order)

- **Voynich (EVA):** 4.2805 bits/char
- **Latin (Medical):** 4.0826 bits/char
- **Random Scramble:** 4.2805 bits/char
- **English (Sample):** 4.4411 bits/char