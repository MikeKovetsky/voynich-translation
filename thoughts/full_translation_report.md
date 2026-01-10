# Full translation (cipher-first) — current status

This is the “cipher-first, with proof” implementation from the plan. It does **not** claim a decipherment yet; it sets up the key-search + validation loop and records the current results.

## Code added
- [`scripts/lm.py`](scripts/lm.py): character n‑gram language model + corpus normalization helpers.
- [`scripts/key_fit.py`](scripts/key_fit.py): Naibbe-like key parameterization + scoring harness + key search + negative controls.
- [`scripts/seg.py`](scripts/seg.py): Latin/Italian lexicon segmentation + coverage metrics.
- [`scripts/dec.py`](scripts/dec.py): decode VMS lines with a key and optionally segment output.

## Data used
- VMS transliteration: `data/transliteration/RF1b-e.txt`
- Naibbe tables (cipher structure prototype): `data/nb.json`
- Control corpora (LM + lexicon): `data/ctrl/la_0218.txt`, `data/ctrl/it_1012.txt`

## What “success” must look like (guardrails)
We only promote a hypothesis if it **generalizes** and beats negative controls.

Minimum pass criteria (current defaults in `scripts/key_fit.py`):
- `gain(test) = test(best) - test(nb)` must be **> +0.05** logp/char
- `test(best)` must also beat token-shuffle baseline by **> +0.05**
- `PASS` must hold under at least one split mode (`--split sec` and/or `--split folio`)

## Baseline: scoring harness (no fitting)
Run:
```bash
python3 scripts/key_fit.py --mode score --split sec
```

Observed:
- `nb` beats a shuffled key by a lot (expected; Naibbe tables are tuned to VMS-like inventories).
- The baseline still does not imply readability; it’s just a score.

## Key fitting (search) + strict controls
Run:
```bash
python3 scripts/key_fit.py --mode fit --split sec --lang latin --starts 2 --iters 400 --samp 150 --negfit
```

Observed (representative run):
- `best` did **not** improve on `nb` on held-out test (gain was negative) → **FAIL**.
- `negfit` on token-shuffled lines shows the optimizer can also “improve” shuffled data, so any small gains are suspicious unless they generalize strongly.

## Segmentation (dictionary coverage)
Run:
```bash
python3 scripts/seg.py --lang latin --lines 200
```

This reports:
- decode score on that subset, and
- word/character coverage by a Latin lexicon built from the control corpus.

Coverage on current decoded outputs is not yet persuasive (chance matches are common in long uppercase strings).

## Decoding output (for inspection)
If you want a plaintext-letter dump for manual inspection:
```bash
python3 scripts/dec.py --lang latin --key data/key_best.json --out data/plain.txt
python3 scripts/dec.py --lang latin --key data/key_best.json --out data/plain_seg.txt --seg
```

## Conclusion (today)
We now have a working pipeline to:
- define train/test splits,
- fit a Naibbe-like key under a language model objective,
- and reject overfit keys via controls.

Right now, the fitted keys **do not pass** the held-out/generalization thresholds, so we do **not** proceed to “full translation” yet.

## Next options (if we keep pushing)
- Expand controls: run the same optimization on multiple random shuffles and require a large margin above that distribution.
- Add richer objectives: incorporate a word-lexicon likelihood term (Latin/Italian) into the fit objective, not just trigram letters.
- Try alternative families: relax the Naibbe prefix/suffix inventory, or allow a small number of additional “null” symbols / token boundary rules.

