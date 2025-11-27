# Track 258: Syntax Mapper Results

## Function Words Analysis

| Word | Role | Confidence | Frequency | Evidence |
|---|---|---|---|---|
| **ol** | Preposition | 0.47 | 516 | Freq: 516, P(Start): 0.06, P(End): 0.10, P(PreNoun): 0.23, P(PreVerb): 0.09 |
| **ar** | Preposition | 0.46 | 350 | Freq: 350, P(Start): 0.02, P(End): 0.11, P(PreNoun): 0.23, P(PreVerb): 0.06 |
| **or** | Preposition | 0.45 | 346 | Freq: 346, P(Start): 0.10, P(End): 0.09, P(PreNoun): 0.23, P(PreVerb): 0.06 |
| **dar** | Preposition | 0.5 | 283 | Freq: 283, P(Start): 0.13, P(End): 0.18, P(PreNoun): 0.25, P(PreVerb): 0.03 |
| **al** | Preposition | 0.48 | 252 | Freq: 252, P(Start): 0.00, P(End): 0.17, P(PreNoun): 0.24, P(PreVerb): 0.04 |
| **dal** | Preposition | 0.54 | 226 | Freq: 226, P(Start): 0.05, P(End): 0.20, P(PreNoun): 0.27, P(PreVerb): 0.04 |
| **dy** | Particle/Suffix | 0.45 | 197 | Freq: 197, P(Start): 0.02, P(End): 0.45, P(PreNoun): 0.16, P(PreVerb): 0.03 |
| **s** | Preposition | 0.55 | 184 | Freq: 184, P(Start): 0.10, P(End): 0.22, P(PreNoun): 0.28, P(PreVerb): 0.05 |
| **qol** | Preposition | 0.36 | 145 | Freq: 145, P(Start): 0.13, P(End): 0.06, P(PreNoun): 0.18, P(PreVerb): 0.09 |
| **chy** | Preposition | 0.48 | 132 | Freq: 132, P(Start): 0.03, P(End): 0.11, P(PreNoun): 0.24, P(PreVerb): 0.05 |
| **y** | Preposition | 0.42 | 130 | Freq: 130, P(Start): 0.33, P(End): 0.22, P(PreNoun): 0.21, P(PreVerb): 0.03 |
| **sho** | Preposition | 0.76 | 121 | Freq: 121, P(Start): 0.29, P(End): 0.04, P(PreNoun): 0.38, P(PreVerb): 0.12 |
| **dol** | Preposition | 0.59 | 109 | Freq: 109, P(Start): 0.15, P(End): 0.10, P(PreNoun): 0.29, P(PreVerb): 0.06 |
| **oty** | Preposition | 0.49 | 103 | Freq: 103, P(Start): 0.05, P(End): 0.27, P(PreNoun): 0.24, P(PreVerb): 0.03 |
| **shy** | Preposition | 0.55 | 88 | Freq: 88, P(Start): 0.05, P(End): 0.14, P(PreNoun): 0.27, P(PreVerb): 0.05 |
| **ain** | Preposition | 0.42 | 86 | Freq: 86, P(Start): 0.02, P(End): 0.15, P(PreNoun): 0.21, P(PreVerb): 0.05 |
| **r** | Preposition | 0.35 | 85 | Freq: 85, P(Start): 0.08, P(End): 0.14, P(PreNoun): 0.18, P(PreVerb): 0.05 |
| **oky** | Particle/Suffix | 0.35 | 80 | Freq: 80, P(Start): 0.09, P(End): 0.35, P(PreNoun): 0.33, P(PreVerb): 0.04 |
| **am** | Particle/Suffix | 0.74 | 80 | Freq: 80, P(Start): 0.00, P(End): 0.74, P(PreNoun): 0.09, P(PreVerb): 0.00 |
| **sar** | Preposition | 0.41 | 79 | Freq: 79, P(Start): 0.35, P(End): 0.19, P(PreNoun): 0.20, P(PreVerb): 0.05 |
| **o** | Preposition | 0.45 | 76 | Freq: 76, P(Start): 0.30, P(End): 0.18, P(PreNoun): 0.22, P(PreVerb): 0.04 |
| **air** | Preposition | 0.43 | 74 | Freq: 74, P(Start): 0.01, P(End): 0.11, P(PreNoun): 0.22, P(PreVerb): 0.07 |
| **dam** | Particle/Suffix | 0.66 | 73 | Freq: 73, P(Start): 0.01, P(End): 0.66, P(PreNoun): 0.10, P(PreVerb): 0.00 |
| **dor** | Preposition | 0.8 | 70 | Freq: 70, P(Start): 0.34, P(End): 0.07, P(PreNoun): 0.40, P(PreVerb): 0.09 |
| **sol** | Preposition | 0.41 | 63 | Freq: 63, P(Start): 0.60, P(End): 0.05, P(PreNoun): 0.21, P(PreVerb): 0.10 |
| **cho** | Preposition | 0.4 | 60 | Freq: 60, P(Start): 0.05, P(End): 0.00, P(PreNoun): 0.20, P(PreVerb): 0.05 |
| **l** | Preposition | 0.47 | 55 | Freq: 55, P(Start): 0.16, P(End): 0.16, P(PreNoun): 0.24, P(PreVerb): 0.02 |
| **kar** | Preposition | 0.58 | 52 | Freq: 52, P(Start): 0.04, P(End): 0.13, P(PreNoun): 0.29, P(PreVerb): 0.06 |

## Methodology
- **Input**: `data/eva_ivtff.txt` (transcription) and `results/dictionary/dictionary_v13.json`.
- **Function Words**: Freq > 50, Length <= 3.
- **Classification Rules**:
  - **Particle/Suffix**: High P(End of Sentence)
  - **Pronoun**: High P(Precedes Verb)
  - **Preposition**: High P(Precedes Noun)
  - **Conjunction**: High P(Start of Sentence)
