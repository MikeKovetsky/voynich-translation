# Phonetic Key Validation Report

## Executive Summary

| Metric | Score | Status |
|--------|-------|--------|
| Overall Validation | **45.3%** | MODIFY |
| Consistency | 64.3% | ✓ |
| Anchor Words | 0.0% | ⚠ |
| Frequency Match | 82.2% | ✓ |
| Reverse Engineering | 15.0% | ⚠ |
| Alternative Mappings | 83.3% | ✓ |
| Bigram Match | 30.0% | ⚠ |

## Recommendation: **MODIFY**

The phonetic key shows mixed results. Consider modifying specific mappings.

## 1. Internal Consistency Analysis

| Mapping | Words Starting | Words Containing | Valid Latin Starts |
|---------|----------------|------------------|-------------------|
| o→a | 42095 | 110055 | 0 |
| k→r | 5964 | 55932 | 14 |
| y→s | 8263 | 85058 | 0 |
| t→n | 5128 | 39929 | 0 |
| e→c | 684 | 74614 | 0 |
| l→l | 6769 | 55725 | 0 |
| m→m | 14 | 5593 | 0 |
| a→e | 9113 | 73582 | 0 |
| i→i | 117 | 37519 | 0 |
| d→d | 18058 | 64807 | 0 |
| c→t | 34789 | 62604 | 0 |
| q→qu | 27931 | 28428 | 0 |
| r→i | 2141 | 38268 | 0 |
| s→b | 21820 | 35485 | 0 |

## 2. Anchor Word Re-validation

| Anchor | Decoded | Expected | Occurrences | Supporting | Contradicting |
|--------|---------|----------|-------------|------------|---------------|
| `oqo` | aqua | aqua | 6 | 0 | 0 |
| `daiin` | deiin | deiin | 4102 | 0 | 0 |
| `qokaiin` | quareiin | quareiin | 1589 | 0 | 0 |
| `oky` | ars | ars | 422 | 0 | 0 |
| `chol` | thal | tal | 1943 | 0 | 0 |
| `shol` | bhal | bal | 907 | 0 | 0 |

## 3. Frequency Distribution

**Correlation with Latin:** 0.643
**Average Difference:** 2.19%

### Top 10 Letter Frequencies

| Letter | Decoded % | Latin % | Difference |
|--------|-----------|---------|------------|
| i | 9.7 | 11.4 | 1.7 |
| e | 7.7 | 11.4 | 3.7 |
| a | 12.1 | 8.9 | 3.2 |
| t | 6.4 | 8.0 | 1.6 |
| s | 8.6 | 7.6 | 1.0 |
| n | 7.7 | 6.3 | 1.4 |
| r | 5.3 | 6.2 | 0.9 |
| u | 2.8 | 6.1 | 3.3 |
| o | 0.0 | 5.5 | 5.5 |
| m | 0.5 | 4.8 | 4.2 |

## 4. Reverse Engineering Test

**Exact Matches:** 0/10
**Partial Matches:** 3/10
**Success Rate:** 15%

| Latin | Predicted | Found | Best Alternative |
|-------|-----------|-------|------------------|
| radix | `kodix` | ✗ | `kodai` |
| folium | `folium` | ✗ | `folr` |
| curat | `eukoc` | ✗ | `-` |
| herba | `hakso` | ✗ | `-` |
| aqua | `o4` | ✗ | `oqo` |
| flos | `floy` | ✗ | `-` |
| contra | `eotcko` | ✗ | `eotar` |
| valet | `volac` | ✗ | `-` |
| dolor | `dolok` | ✗ | `dolky` |
| febris | `faskiy` | ✗ | `-` |

## 5. Alternative Mapping Tests

| Current | Alternative | Current Matches | Alt Matches | Keep? |
|---------|-------------|-----------------|-------------|-------|
| k→r | k→l | 1 | 7 | ✗ |
| d→d | d→t | 0 | 0 | ✓ |
| q→qu | q→c | 4 | 4 | ✓ |
| r→i | r→e | 0 | 0 | ✓ |
| y→s | y→x | 1 | 1 | ✓ |
| a→e | a→a | 0 | 0 | ✓ |

**Recommendation:** KEEP

## 6. Bigram Analysis

**Common Latin Bigrams Found:** 3/10

### Top Decoded Bigrams

| Bigram | Decoded % | Latin % |
|--------|-----------|---------|
| th | 6.42 | 0.00 |
| ei | 5.82 | 0.00 |
| hc | 4.77 | 0.00 |
| ds | 4.11 | 0.00 |
| ar | 3.59 | 0.20 |
| in | 3.54 | 0.85 |
| al | 3.32 | 0.18 |
| ii | 3.27 | 0.00 |
| qu | 3.22 | 1.80 |
| ua | 3.14 | 0.00 |
| cd | 3.04 | 0.00 |
| cc | 2.87 | 0.00 |
| bh | 2.68 | 0.00 |
| de | 2.40 | 0.33 |
| ha | 2.39 | 0.00 |

## Critical Issues Identified

⚠ **No exact reverse matches** - Can't find predicted Voynich forms for Latin words

⚠ **Consider changing** k→r to k→l


## Conclusion

The phonetic key validation produced an overall score of **45.3%**.

The key validation failed to demonstrate sufficient statistical alignment with Latin.
Consider:
1. Re-examining the fundamental mapping assumptions
2. Testing alternative language hypotheses
3. Looking for additional encoding layers
