# Suffix-Position Correlation Report

**Input Data:** `data/eva_ivtff.txt` (Takahashi `;H>` transcription)
**Suffixes Analyzed:** aiin, edy, air, iin, eey, or, ey, al, in, hy, dy, ol, ar, l, n, r, y

## Baseline Statistics (All Words)
- **Start**: 11.4%
- **Middle**: 73.8%
- **End**: 11.4%
- **Single**: 3.5%

## Statistical Table: P(Position | Suffix)

| Suffix | Count | Start % | Middle % | End % | Single % | Notable Deviation |
|---|---|---|---|---|---|---|
| -edy | 3005 | 8.4% | 86.5% | 4.4% | 0.7% |  |
| -aiin | 2028 | 15.9% | 74.3% | 8.3% | 1.5% |  |
| -ol | 1723 | 16.7% | 76.1% | 4.2% | 3.0% |  |
| -y | 1681 | 5.2% | 55.7% | 29.7% | 9.3% | **End +2.6x** |
| -ar | 1615 | 12.5% | 76.2% | 8.3% | 3.0% |  |
| -dy | 1586 | 7.9% | 71.9% | 13.0% | 7.1% | **Single +2.0x** |
| -ey | 1329 | 11.0% | 84.0% | 4.1% | 0.9% |  |
| -hy | 1304 | 10.3% | 77.0% | 8.7% | 4.0% |  |
| -eey | 1283 | 12.2% | 85.4% | 1.9% | 0.5% |  |
| -al | 1279 | 9.4% | 74.7% | 11.0% | 4.9% |  |
| -in | 1191 | 12.7% | 77.5% | 8.7% | 1.1% |  |
| -or | 981 | 22.0% | 68.8% | 5.9% | 3.3% | **Start +1.9x** |
| -r | 711 | 6.2% | 84.0% | 8.9% | 1.0% |  |
| -l | 673 | 4.9% | 81.4% | 12.9% | 0.7% |  |
| -iin | 533 | 8.1% | 83.7% | 7.5% | 0.8% |  |
| -air | 275 | 24.7% | 72.4% | 2.2% | 0.7% | **Start +2.2x** |
| -n | 80 | 8.8% | 46.2% | 35.0% | 10.0% | **End +3.1x** |

## Grammar Rule Candidates

- **-y**: Strongly favors **End** (29.7% vs baseline 11.4%). Lift: 2.6x.
- **-dy**: Often appears in **Single-word lines** (7.1% vs baseline 3.5%).
- **-or**: Strongly favors **Start** (22.0% vs baseline 11.4%). Lift: 1.9x.
- **-air**: Strongly favors **Start** (24.7% vs baseline 11.4%). Lift: 2.2x.
- **-n**: Strongly favors **End** (35.0% vs baseline 11.4%). Lift: 3.1x.

## Analysis
High 'Lift' (deviation from baseline) suggests grammatical function.
- Suffixes with high **End** lift might be sentence terminators or specific grammatical cases (e.g., verbs at end?).
- Suffixes with high **Start** lift might be sentence initiators.