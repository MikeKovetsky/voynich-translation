# Dictionary Conflict Analysis Report

## Summary

| Metric | Value |
|--------|-------|
| Total entries analyzed | 409 |
| Clean entries | 324 |
| Conflicting entries | 85 |
| Conflict rate | 20.8% |
| Clean coverage | 43.26% |

## Conflicts by Type

### Same Domain (31 words)

**Minor conflicts** - multiple related meanings within same domain.

- **okar**: heart, cure
- **okor**: heart, cure
- **ykar**: heart, cure
- **kor**: heart, cure
- **okair**: heart, cure
- **kair**: heart, cure
- **okeor**: heart, cure
- **okary**: heart, cure
- **okear**: heart, cure
- **okeeor**: heart, cure
- ... and 21 more

### Cross Domain (48 words)

**These are SERIOUS conflicts** - same word means different things in unrelated domains.

- **kar**: heart, hebrew: kar, cure
- **sol**: sun, salt
- **sal**: sun, salt
- **sam**: medicine/drug, seed
- **osal**: sun, salt
- **saly**: sun, salt
- **dam**: hebrew: dam, blood
- **qokedy**: wheat, capricorn, vinegar, medical/cardiac term
- **dain**: blood, fig
- **qokal**: eat, modifier of which/that, sky, sick
- ... and 38 more

### Grammar Vs Content (6 words)

**Grammar vs content** - word acts as both grammar marker and content word.

- **qokeedy**: wheat, links which/that to is/has (verb), capricorn, vinegar
- **saiin**: ear, links -ed/-ing verb to to, without, medicine/drug
- **chos**: tree, verb (unknown)
- **choty**: wheat, verb (unknown)
- **ain**: one, preposition/conjunction
- **oiin**: one, preposition/conjunction

## Worst Offenders

| Word | # Meanings | Examples | Type |
|------|------------|----------|------|
| saiin | 6 | ear, links -ed/-ing verb to to, without | grammar_vs_content |
| qokal | 5 | eat, modifier of which/that, sky | cross_domain |
| okal | 5 | all/voice, eat, sky | cross_domain |
| qokol | 5 | links the to of the/from, eat, sky | cross_domain |
| okol | 5 | links to to priest/cohen, all/voice, eat | cross_domain |
| sain | 5 | ear, without, medicine/drug | cross_domain |
| sheol | 5 | salt, medical/cardiac term, sky | cross_domain |
| qokeedy | 4 | wheat, links which/that to is/has (verb), capricorn | grammar_vs_content |
| qokedy | 4 | wheat, capricorn, vinegar | cross_domain |
| okedy | 4 | wheat, capricorn, vinegar | cross_domain |
| okeedy | 4 | wheat, capricorn, vinegar | cross_domain |
| odaiin | 4 | blood, fig, noun (genitive) | cross_domain |
| kar | 3 | heart, hebrew: kar, cure | cross_domain |
| chdy | 3 | wheat, capricorn, vinegar | cross_domain |
| chody | 3 | wheat, vinegar, medical/cardiac term | cross_domain |

## Critical Assessment

### Red Flags Identified

1. **48 cross-domain conflicts**: Same words mean completely different things
   - Example: `kar` = heart, hebrew: kar, cure

2. **6 grammar/content conflicts**: Words serving dual purposes

### Honest Assessment

- **Before cleaning**: ~409 entries with potential overfitting
- **After cleaning**: 324 reliable entries
- **Real coverage**: 43.26%
- **Top 100 words in clean**: 56/100
- **Top 100 coverage**: 65.93%

### Implications

✅ **Core dictionary is relatively solid**

Most entries have consistent meanings across sources.

## Recommendations

1. Use only entries from `clean_dictionary.json` for translation
2. Cross-domain conflicts need manual review
3. Re-run translation with clean dictionary to get honest metrics
