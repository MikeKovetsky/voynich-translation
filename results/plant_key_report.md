# Plant Label Key Derivation Report

## Summary
- **Conclusion**: NEGATIVE: Derived mappings show LOW similarity to expected Latin names
- **Recommendation**: Labels are likely NOT direct plant names

## Metrics
- Average direct similarity: 0.176
- Conflict rate: 0.667
- Plants analyzed: 8
- Consistent character mappings: 5
- Conflicting character mappings: 10

## Visual Identifications Used

| Folio | Plant | Confidence | Label (Claston) | Label (EVA) |
|-------|-------|------------|-----------------|-------------|
| f17r | Cornflower | 0.75 | f2o89 | fshody |
| f5r | Hellebore | 0.6 | h2o89 | kshody |
| f2v | Cyclamen | 0.5 | hoom | koom |
| f4r | Tamarisk | 0.5 | ho8ae19 | kodalchy |
| f6r | Poppy | 0.5 | foay | foar |
| f25v | Castor Bean | 0.5 | goCam | poCaiin |
| f3r | Aloe | 0.4 | k2cos | tsheos |
| f9r | Oak | 0.4 | k98eo | tydlo |

## Derivation Attempts

### f17r → centaurea
- Label (EVA): `fshody`
- Expected: `centaurea`
- Direct similarity: 0.0
- Length match: False (diff: 3)
- Plausibility score: 0.0

Character mappings:
```
  1: f → c
  2: s → e
  3: h → n
  4: o → t
  5: d → a
  6: y → u
```

### f17r → cyanus
- Label (EVA): `fshody`
- Expected: `cyanus`
- Direct similarity: 0.167
- Length match: True (diff: 0)
- Plausibility score: 0.125

Character mappings:
```
  1: f → c
  2: s → y
  3: h → a
  4: o → n
  5: d → u
  6: y → s
```

### f5r → helleborus
- Label (EVA): `kshody`
- Expected: `helleborus`
- Direct similarity: 0.125
- Length match: False (diff: 4)
- Plausibility score: 0.075

Character mappings:
```
  1: k → h
  2: s → e
  3: h → l
  4: o → l
  5: d → e
  6: y → b
```

### f2v → cyclamen
- Label (EVA): `koom`
- Expected: `cyclamen`
- Direct similarity: 0.167
- Length match: False (diff: 4)
- Plausibility score: 0.083

Character mappings:
```
  1: k → c
  2: o → y
  3: o → c
  4: m → l
```

### f4r → tamarix
- Label (EVA): `kodalchy`
- Expected: `tamarix`
- Direct similarity: 0.133
- Length match: False (diff: 1)
- Plausibility score: 0.067

Character mappings:
```
  1: k → t
  2: o → a
  3: d → m
  4: a → a
  5: l → r
  6: c → i
  7: h → x
```

### f6r → papaver
- Label (EVA): `foar`
- Expected: `papaver`
- Direct similarity: 0.364
- Length match: False (diff: 3)
- Plausibility score: 0.182

Character mappings:
```
  1: f → p
  2: o → a
  3: a → p
  4: r → a
```

### f25v → ricinus
- Label (EVA): `poCaiin`
- Expected: `ricinus`
- Direct similarity: 0.429
- Length match: True (diff: 0)
- Plausibility score: 0.214

Character mappings:
```
  1: p → r
  2: o → i
  3: c → c
  4: a → i
  5: i → n
  6: i → u
  7: n → s
```

### f3r → aloe
- Label (EVA): `tsheos`
- Expected: `aloe`
- Direct similarity: 0.2
- Length match: False (diff: 2)
- Plausibility score: 0.08

Character mappings:
```
  1: t → a
  2: s → l
  3: h → o
  4: e → e
```

### f9r → quercus
- Label (EVA): `tydlo`
- Expected: `quercus`
- Direct similarity: 0.0
- Length match: False (diff: 2)
- Plausibility score: 0.0

Character mappings:
```
  1: t → q
  2: y → u
  3: d → e
  4: l → r
  5: o → c
```

## Cross-Check Results

### Consistent Mappings

- `m` → `l` (seen 1 times)
- `l` → `r` (seen 1 times)
- `r` → `a` (seen 1 times)
- `p` → `r` (seen 1 times)
- `n` → `s` (seen 1 times)

### Conflicts

- `f` → [p, c]
- `s` → [y, e]
- `h` → [x, a, n, l]
- `o` → [c, y, t, n, a, l, i]
- `d` → [a, e, u, m]
- `y` → [u, b, s]
- `k` → [t, h, c]
- `a` → [a, p, i]
- `c` → [i, c]
- `i` → [u, n]

## Alternative Hypotheses

### Labels as Descriptors

**f17r** (fshody)
  - Best descriptor match: {'descriptor': 'flos', 'similarity': 0.4}

**f2v** (koom)
  - Best descriptor match: {'descriptor': 'folium', 'similarity': 0.4}
  - Best use match: {'descriptor': 'dolorem', 'similarity': 0.545}

**f4r** (kodalchy)
  - Best descriptor match: {'descriptor': 'folia', 'similarity': 0.308}

**f6r** (foar)
  - Best descriptor match: {'descriptor': 'folia', 'similarity': 0.667}
  - Best use match: {'descriptor': 'contra', 'similarity': 0.4}

**f25v** (poCaiin)
  - Best descriptor match: {'descriptor': 'radix', 'similarity': 0.333}
  - Best use match: {'descriptor': 'pro', 'similarity': 0.4}


## Label Patterns

Starting characters: {'f': 2, 'h': 3, 'g': 1, 'k': 2}

Ending characters: {'9': 3, 'm': 2, 'y': 1, 's': 1, 'o': 1}

Length distribution: {5: 5, 4: 2, 7: 1}

## Conclusion

NEGATIVE: Derived mappings show LOW similarity to expected Latin names

### Key Findings

1. **Low similarity**: Average similarity between labels and expected plant names is only 0.176, suggesting labels are NOT direct plant names.
2. **High conflict rate**: 67% of character derivations conflict across plants, indicating no consistent cipher.

### Implications

The plant labels in the Voynich manuscript likely:
- Are NOT direct Latin botanical names
- May be abbreviated or coded descriptions
- Could represent medicinal uses or locations
- Might be in a non-Latin language entirely

This negative result is valuable - it rules out simple substitution cipher for plant names.