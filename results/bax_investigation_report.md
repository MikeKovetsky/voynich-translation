# Track 60: Bax Investigation Report

## Executive Summary

This investigation examines why our EVA readings differ from Stephen Bax's claimed decodings.

**Key Finding**: We are likely reading the SAME transcription but Bax may have:
1. Read from a DIFFERENT position on the page (label vs paragraph text)
2. Used a DIFFERENT phonetic mapping (especially k, ch, q)
3. Made interpretive choices about ambiguous characters

---

## Background: Stephen Bax's Method

In 2014, Professor Stephen Bax proposed a partial decoding by:
1. Identifying plants in illustrations
2. Finding matching medieval plant names (Arabic, Latin, Turkish)
3. Deriving phonetic values from these matches

His key phonetic assignments:
| EVA | Bax Value | Our Value | Match? |
|-----|-----------|-----------|--------|
| k   | /t/       | /n/       | **NO** |
| o   | /a/       | /a/       | YES    |
| ch  | /k/       | /t/       | **NO** |
| q   | /k/       | /qu/      | PARTIAL|
| a   | /ə/       | /e/       | **NO** |

---

## Word-by-Word Comparison

### Folio f17r: "kantairon" (Centaury (Centaurea cyanus))

**Bax claims**: "kantairon" at label near plant illustration

**Our EVA reading**: `fshody`
- With Bax phonetics: "fshədy"
- All first words found: ['fshody', 'fshody', 'fshody', 'fshody', 'fshody']
- Labels found: None

**Analysis**: NO_MATCH
**Verdict**: Different words - likely reading different positions on page

### Folio f3v: "kaur" (Black hellebore (Helleborus niger))

**Bax claims**: "kaur" at first word / plant label

**Our EVA reading**: `koaiin`
- With Bax phonetics: "t*əəiin"
- All first words found: ['koaiin', 'koaiin', 'koaiin', 'koaiin', 'koaiin']
- Labels found: None

**Analysis**: NO_MATCH
**Verdict**: Different words - likely reading different positions on page

### Folio f2v: "kain" (possible plant name)

**Bax claims**: "kain" at near illustration

**Our EVA reading**: `kooiin`
- With Bax phonetics: "t*əəiin"
- All first words found: ['kooiin', 'kooiin', 'kaoiin', 'kooiin', 'kaoiin']
- Labels found: None

**Analysis**: NO_MATCH
**Verdict**: Different words - likely reading different positions on page

### Folio f25v: "poriom" (possible leek/allium)

**Bax claims**: "poriom" at plant label area

**Our EVA reading**: `poeeaiin`
- With Bax phonetics: "pəeeəiin"
- All first words found: ['poeeaiin', '??!?aiin', 'poeeaiin', 'poeeaiin', '????aiin']
- Labels found: None

**Analysis**: NO_MATCH
**Verdict**: Different words - likely reading different positions on page

---

## Critical Analysis

### Why the Discrepancy?

1. **Position Difference**: Bax may have read plant LABELS (not in standard EVA transcription)
   while we read PARAGRAPH text first words.

2. **Character Interpretation**: Key mapping conflicts:
   - EVA `k` = /t/ (Bax) vs /n/ (Ours) - FUNDAMENTAL CONFLICT
   - EVA `ch` = /k/ (Bax) vs /t/ (Ours) - INVERTED!
   
3. **Transcription Source**: Bax may have used direct manuscript reading
   while we use the Landini-Stolfi EVA transcription.

### The "kantairon" Problem

Bax claims f17r shows "kantairon" (centaury). Let's trace this:
- If kantairon = k.a.n.t.a.i.r.o.n in some system
- Reverse-engineering: what EVA would produce this?
- With Bax's k=/t/, we'd need EVA starting with `k` to get /t/
- Our first word `fshody` → using Bax values → "f-sh-a-d-y" → NOT kantairon!

**Conclusion**: Bax was NOT reading `fshody`. He must have read a DIFFERENT word,
possibly from a different position or using different character boundaries.

### Possible Explanations

1. **DIFFERENT POSITION**: Bax read a label or header, not paragraph text
   - f17r has a Latin header line (faded) above the main text
   - No separate labels (L1, L2) are transcribed in EVA for f17r
   - Bax may have read directly from the manuscript image

2. **DIFFERENT TRANSCRIPTION SYSTEM**: Bax may not have used standard EVA
   - He may have created his own character-to-sound mapping
   - Direct reading from manuscript bypassing EVA entirely

3. **SELECTIVE READING**: Bax may have chosen specific words that FIT his theory
   - Cherry-picking words that support plant name matches
   - This is a common criticism of his methodology

---

## Verdict

### Who is Right?

**Neither is definitively "wrong"** - we're likely reading different things:

| Aspect | Bax | Our Analysis |
|--------|-----|--------------|
| Position | Labels/specific spots | First word of paragraphs |
| System | Custom/direct | Standard EVA transcription |
| Method | Plant name matching | Statistical + dictionary |
| Result | "kantairon", "kaur" | "fshody", "kshody", "koaiin" |

### Implications for Our Research

1. **Our readings are valid** for the EVA transcription we use
2. **Bax's readings may also be valid** for his interpretation method
3. **The conflict doesn't invalidate either** - it shows the manuscript
   can be read multiple ways depending on:
   - Where you read (position)
   - How you interpret characters (phonetic mapping)
   - What you're looking for (confirmation bias)

### Recommendation

Future work should:
1. Identify EXACTLY which characters Bax read for "kantairon"
2. Compare at character level, not word level
3. Check if his characters exist in ANY EVA position on f17r
4. Consider that plant labels may be in a DIFFERENT script/system than paragraph text

---

## References

- Bax, Stephen (2014). "A proposed partial decoding of the Voynich script"
- EVA Transcription: Landini-Stolfi Interlinear file (eva_ivtff.txt)
- Our Track 58: Scholarly Comparison

*Generated by Track 60: Bax Investigation*
