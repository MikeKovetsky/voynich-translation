# Zodiac Key Derivation Report

## Overview
This analysis attempts to derive the Voynich phonetic key using
a "known plaintext attack" - we know the zodiac sections should
contain month names (Martius, Aprilis, etc.).

## Labels Extracted
Total labels found: 367

| Folio | Zodiac | Expected Month | Labels |
|-------|--------|----------------|--------|
| f70v2 | pisces | martius | oty, oky, ody, oty, or... (+32) |
| f70v1 | aries | aprilis | otalchy, tar, am, dy, opchey... (+21) |
| f71r | aries | aprilis | oteos, arar, okldam, oteoaldy, oteolar... (+14) |
| f71v | taurus | maius | char, orom, chfaly, okolar, otchody... (+17) |
| f72r1 | taurus | maius | oshodody, chdaiirsainy, oaiin, ar, ary... (+19) |
| f72r2 | gemini | iunius | ofchdady, oklairdy, okaram, okairy, okeolar... (+27) |
| f72r3 | cancer | iulius | ykolairol, olkalaiin, olalsy, or, aiin... (+42) |
| f72v3 | leo | augustus | ok, ogeom, oreeey, okam, okey... (+31) |
| f72v2 | virgo | september | oeedey, oeeo, daiin, okeoram, airolm... (+28) |
| f72v1 | libra | october | oeeoty, octhy, oteoly, okeoly, oeees... (+25) |
| f73r | scorpio | november | otoly, chockhy, okedy, yteeody, otey... (+25) |
| f73v | sagittarius | december | okol, oteody, oteody, cheody, okeody... (+26) |

## Top Month Name Candidates

| Voynich | Decoded | Expected | Score |
|---------|---------|----------|-------|
| opchey | apcrii | aprilis | 0.829 |
| oteolar | atiale | aprile | 0.800 |
| okeal | aniel | april | 0.650 |
| oalcheg | aelcrig | aprilis | 0.586 |
| otalsar | atelxe | aprile | 0.583 |
| oteeol | atiial | april | 0.583 |
| yfary | ifei | iulio | 0.550 |
| ypsharal | ipxreel | aprile | 0.536 |
| ytairal | iteiel | iulius | 0.533 |
| otolaiin | ataleiin | aprilis | 0.500 |
| otoloaram | atalaeem | aprile | 0.500 |
| otalchy | atelcri | aprile | 0.493 |
| oteoeey | atiaiii | aprilis | 0.486 |
| oteotey | atiatii | aprilis | 0.486 |
| ypaiin | ipeiin | iulius | 0.483 |
| otyly | atili | april | 0.450 |
| okoly | anali | april | 0.450 |
| octhy | actri | octobris | 0.450 |
| okolshy | analxri | aprilis | 0.443 |
| okeoaly | aniaeli | aprile | 0.443 |

## Derived Character Mappings

| Voynich | Derived | Known | Match | Confidence |
|---------|---------|-------|-------|------------|
| a | l | e | ✗ | 0.41 |
| c | r | c | ✗ | 0.40 |
| d | i | v | ✗ | 0.50 |
| e | r | i | ✗ | 0.59 |
| f | u | f | ✗ | 1.00 |
| g | s | g | ✗ | 1.00 |
| h | i | r | ✗ | 0.57 |
| i | i | i | ✓ | 0.62 |
| k | p | n | ✗ | 0.67 |
| l | i | l | ✗ | 0.64 |
| m | s | m | ✗ | 0.50 |
| n | s | n | ✗ | 0.50 |
| o | a | a | ✓ | 0.59 |
| p | p | p | ✓ | 0.67 |
| r | u | ? | ✗ | 0.40 |
| s | l | x | ✗ | 0.80 |
| t | p | t | ✗ | 0.88 |
| y | i | i | ✓ | 0.36 |

## Conflicts Found

- **o**: {'a': 29, 'i': 7, 'l': 3, 'r': 7, 'o': 1, 'm': 1, 'y': 1}
- **p**: {'p': 2, 'u': 1}
- **c**: {'r': 2, 'i': 1, 'l': 1, 'c': 1}
- **h**: {'i': 4, 'l': 1, 'e': 1, 'o': 1}
- **e**: {'l': 3, 'r': 10, 'i': 4}
- **y**: {'i': 5, 'o': 1, 'a': 1, 's': 3, 'r': 1, 'l': 2, 'b': 1}
- **t**: {'p': 21, 'u': 1, 'l': 1, 't': 1}
- **l**: {'l': 2, 'r': 2, 'i': 14, 'e': 4}
- **a**: {'e': 4, 'i': 2, 'p': 1, 'r': 7, 'l': 12, 's': 2, 'j': 1}
- **k**: {'p': 6, 'e': 1, 'i': 1, 'u': 1}
- **s**: {'l': 4, 'r': 1}
- **r**: {'i': 1, 'e': 1, 'u': 2, 'a': 1}
- **i**: {'i': 5, 's': 1, 'u': 2}
- **n**: {'s': 1, 'n': 1}
- **m**: {'s': 1, 'e': 1}
- **d**: {'i': 1, 'e': 1}

## Validation Results

Average improvement: -0.039

| Voynich | Expected | Old | New | Change |
|---------|----------|-----|-----|--------|
| opchey | aprilis | apcrii | apriri | -0.11 |
| oteolar | aprile | atiale | aprailu | -0.37 |
| okeal | april | aniel | aprli | -0.05 |
| oalcheg | aprilis | aelcrig | alirirs | -0.30 |
| otalsar | aprile | atelxe | aplillu | -0.01 |
| oteeol | april | atiial | aprrai | -0.08 |
| yfary | iulio | ifei | iului | +0.05 |
| ypsharal | aprile | ipxreel | ipliluli | -0.16 |
| ytairal | iulius | iteiel | ipliuli | +0.04 |
| otolaiin | aprilis | ataleiin | apailiis | +0.12 |
| otoloaram | aprile | atalaeem | apaialuls | -0.17 |
| otalchy | aprile | atelcri | aplirii | -0.06 |
| oteoeey | aprilis | atiaiii | aprarri | -0.06 |
| oteotey | aprilis | atiatii | aprapri | -0.06 |
| ypaiin | iulius | ipeiin | ipliis | +0.18 |

## Summary

- Characters derived: 18
- Matching known key: 4/18 (22.2%)
- Key confidence: 0.617
- Conflicts: 16

## Conclusion

The derived key shows **significant divergence** from the known map.
This could indicate: (a) the labels aren't month names, 
(b) different orthography/language, or (c) transcription issues.