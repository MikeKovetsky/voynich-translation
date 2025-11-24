# Track 1: Agglutinative Language Comparison Report

## Summary

Analyzed Voynich grammatical patterns against 5 agglutinative languages:
Turkish, Finnish, Hungarian, Basque, and Georgian.

## Rankings

| Rank | Language | Score | Key Matches |
|------|----------|-------|-------------|
| 1 | Basque | 81.9% | Article system matches, Strong case system match |
| 2 | Georgian | 79.1% | Word length closely matches |
| 3 | Turkish | 73.4% | Strong case system match, Vowel harmony could explain patterns |
| 4 | Hungarian | 70.1% | Article system matches, Vowel harmony could explain patterns |
| 5 | Finnish | 53.6% | Vowel harmony could explain patterns |

## Top Candidate: Basque

Confidence: 81.9%

## Key Findings

1. **Case System**: Voynich has ~8 case-like endings, most similar to Basque (12) and Georgian (7)

2. **Article Pattern**: The '4o-' prefix appears in 12.9% of words, suggesting a definite article
   - Hungarian has articles (suffix-based)
   - Basque has suffix articles
   - Turkish, Finnish, Georgian have no articles

3. **Word Length**: Voynich avg 3.91 chars
   - Georgian closest at 5.0
   - Finnish highest at 7.5
   - This difference may indicate abbreviation in Voynich

4. **Suffix Structure**: Voynich suffixes are short (1-2 chars), similar to Georgian and Basque

## Recommendations

1. Focus deeper analysis on top 2-3 candidates
2. Look for specific vocabulary matches (botanical terms)
3. Test phonetic mappings more thoroughly
4. Compare with historical forms of these languages (15th century)

## Files Generated

- results/language_scores.json - Full scoring data
- results/case_mapping.json - Case ending comparisons
