# Track 198 Results Summary

## Methodology
1.  **Source Text**: Parsed `data/eva_ivtff.txt` to extract text for all pages.
2.  **Zodiac Extraction**: Identified nouns from Zodiac pages (Taurus through Pisces) based on `results/zodiac_plants.json` mapping.
    -   Criteria: Words starting with 'o-' OR words with low corpus frequency (<= 5).
3.  **Herbal Search**: Searched for these nouns in the Herbal Section (Quires 1-8, 13, 14).
    -   Constraint: Matches must be a **Label** (first word of a line) or **High Frequency** (>= 2 occurrences on the herbal page).

## Results Overview
-   **Processed Signs**: Aquarius, Cancer, Capricorn, Gemini, Leo, Libra, Pisces, Sagittarius, Taurus.
-   **Total Links Found**: 1136.
-   **Output**: `results/zodiac_herbal_map.csv`

## Top Matches by Sign

### Cancer (149 links)
- **or** found on f39v (Count: 9, Label: False)
- **o** found on f57v (Count: 7, Label: True)
- **or** found on f55r (Count: 7, Label: False)
- **or** found on f101v (Count: 7, Label: True)
- **o** found on f66r (Count: 6, Label: True)

### Gemini (134 links)
- **okal** found on f58v (Count: 9, Label: False)
- **ol** found on f66r (Count: 7, Label: True)
- **okeol** found on f99r (Count: 6, Label: False)
- **ol** found on f101r (Count: 6, Label: False)
- **otal** found on f58v (Count: 5, Label: False)

### Leo (134 links)
- **or** found on f39v (Count: 9, Label: False)
- **or** found on f55r (Count: 7, Label: False)
- **or** found on f101v (Count: 7, Label: True)
- **okeol** found on f99r (Count: 6, Label: False)
- **okey** found on f102v2 (Count: 6, Label: False)

### Libra (59 links)
- **okeol** found on f99r (Count: 6, Label: False)
- **okeol** found on f101r (Count: 5, Label: False)
- **okeey** found on f99r (Count: 5, Label: False)
- **okeey** found on f101r (Count: 5, Label: False)
- **okeol** found on f99v (Count: 4, Label: False)

### Pisces (336 links)
- **okal** found on f58v (Count: 9, Label: False)
- **okal** found on f58v (Count: 9, Label: False)
- **or** found on f39v (Count: 9, Label: False)
- **o** found on f57v (Count: 7, Label: True)
- **ol** found on f66r (Count: 7, Label: True)

### Sagittarius (61 links)
- **okal** found on f58v (Count: 9, Label: False)
- **okey** found on f102v2 (Count: 6, Label: False)
- **okol** found on f99v (Count: 5, Label: False)
- **okol** found on f89v1 (Count: 4, Label: False)
- **otedy** found on f48v (Count: 4, Label: False)

### Taurus (263 links)
- **or** found on f39v (Count: 9, Label: False)
- **okal** found on f58v (Count: 9, Label: False)
- **or** found on f55r (Count: 7, Label: False)
- **or** found on f101v (Count: 7, Label: True)
- **o** found on f57v (Count: 7, Label: True)
