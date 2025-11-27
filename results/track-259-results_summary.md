# Track 259: Merge Context Audit Results

## Overview
- **Input Dictionary**: results/dictionary/dictionary_v13.json
- **Total Candidates Identified**: 681
- **Safe Merges Approved**: 652
- **Merges Rejected**: 29

## Rejection Breakdown
- **Section Mismatches (Astro vs Recipe)**: 1
- **Suffix Conflicts (Root + Suffix)**: 28

## Methodology
1. **Candidate Identification**: Found pairs with Levenshtein distance = 1 (Unknown vs Anchor).
2. **Section Audit**: Checked for mutually exclusive sections (specifically Astronomical vs Recipes).
3. **Grammar Audit**: Checked if the difference between words corresponds to a known suffix (from `morphology_rules.json`).

## Examples of Rejected Merges
- **cthol** vs **ctho**: Suffix Conflict: cthol = ctho + -l (Known Suffix)
- **cthol** vs **ctholy**: Suffix Conflict: ctholy = cthol + -y (Known Suffix)
- **lol** vs **loly**: Suffix Conflict: loly = lol + -y (Known Suffix)
- **lor** vs **lory**: Suffix Conflict: lory = lor + -y (Known Suffix)
- **olor** vs **olo**: Suffix Conflict: olor = olo + -r (Known Suffix)
- **ckha** vs **ckhal**: Suffix Conflict: ckhal = ckha + -l (Known Suffix)
- **choa** vs **choar**: Suffix Conflict: choar = choa + -r (Known Suffix)
- **tchee** vs **tcheey**: Suffix Conflict: tcheey = tchee + -y (Known Suffix)
- **salr** vs **sal**: Suffix Conflict: salr = sal + -r (Known Suffix)
- **doii** vs **doiir**: Suffix Conflict: doiir = doii + -r (Known Suffix)
