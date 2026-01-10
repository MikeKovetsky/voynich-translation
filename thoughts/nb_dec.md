# Naibbe-key decipher attempt

Goal: treat Greshko (2025) Naibbe cipher tables as a candidate key, decode VMS EVA tokens into plaintext letters, and score whether output looks like Latin/Italian.

## What was implemented
- Naibbe tables extracted to `data/nb.json` (α, β1–β3, γ1–γ2).
- Decoder + scorer in `scripts/nb_dec.py`:
  - token → candidates (unigram word or prefix+suffix split)
  - beam search per VMS line with a trigram letter LM
  - Latin + Italian LMs trained from `data/ctrl/la_0218.txt` and `data/ctrl/it_1012.txt`
  - baselines: shuffled-token VMS, randomized keys, and a Naibbe-cipher positive control

Run:
```bash
python3 scripts/nb_dec.py
```

## Main result (full VMS)
Naibbe-key decoding does **not** yield Latin/Italian-like output.

- **Latin LM**: logp/char = **-3.2974** (n=44694)
- **Italian LM**: logp/char = **-3.3998** (n=44514)

Decoded snippets with high scores exist, but they look like letter-salad (e.g. `ISEINIREATENTATIMEOTE`) rather than readable text.

### Coverage / ambiguity (full VMS, by token)
Counts over all 37,781 tokens:
- **cand0**: 9,138 tokens (no Naibbe decode)
- **cand1**: 15,299 tokens (unique decode)
- **cand2+**: 13,344 tokens (ambiguous decode)

This high decode coverage is expected because the Naibbe tables were constructed from common VMS word-types/affixes; coverage alone is not evidence of correct decipherment.

### Section-level scores (Latin LM)
Higher (less negative) is “more Latin-like”:
- Biological: -3.210
- Recipes: -3.265
- Cosmological: -3.314
- Herbal: -3.329
- Pharmaceutical: -3.384
- Astronomical: -3.393

## Baselines (sanity checks)
All baseline values below are on the first 1,000 VMS lines (faster), using the same scoring.

### Positive control (works)
We generate Naibbe ciphertext from real Latin/Italian plaintext and decode it with the same key.

- **Latin**: det_spc = **-2.2090** (n=9985)
  - true_spc = -2.0800
  - hit=1.000 (true decode always in candidates)
  - det_ok=0.965 (Naibbe “unigram-first” heuristic is mostly right)
- **Italian**: det_spc = **-2.2434** (n=10078)
  - true_spc = -2.1211
  - hit=1.000, det_ok=0.969

So the tables + decoder pipeline are capable of producing very language-like scores when the input really is Naibbe ciphertext.

### Shuffled-token VMS (order doesn’t help much)
Shuffling tokens (keeping the same token multiset + line lengths) gives similar scores:
- shuf: latin=-3.3388, ital=-3.3867

This suggests the Naibbe-key score on VMS is dominated by token distribution (unigram/affix inventory), not by strong sequential constraints.

### Randomized keys (real key beats random, but that’s not a decipherment)
We randomize letter assignments inside the Naibbe tables (same table sizes, permuted letters) and rescore:
- randkey Latin: mean=-3.6802 sd=0.0448, z≈+7.5
- randkey Italian: mean=-3.7250 sd=0.0462, z≈+6.9

Interpretation: the published Naibbe key is *tuned* (built from VMS word-types/affixes) and so it yields more Latin/Italian-like letter frequencies than a random key, even when applied to VMS. That is **not** the same as successfully decrypting meaningful text.

## Conclusion
Using the **published Naibbe cipher tables as a direct key does not decipher the VMS** into Latin or Italian under this test. The decoded output’s language-model scores are far from the positive-control Naibbe ciphertext and far from real plaintext.

## Next options (more aggressive)
If you want to keep pushing toward “decipher” rather than “compatibility test”, the next meaningful step is to **fit** a Naibbe-like key to the VMS (optimize a constrained mapping to maximize Latin/Italian LM score), then check whether the fitted key generalizes across sections/folios instead of overfitting.

