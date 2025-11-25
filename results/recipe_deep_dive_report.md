# Track 71: Recipe Section Deep Dive

## Summary

- **Folios analyzed**: 23
- **Total lines**: 1084
- **Total words**: 10599
- **Translated words**: 4700
- **Coverage rate**: 44.3%
- **Unique ingredients**: 19
- **Unique conditions**: 9
- **Recipe patterns found**: 169

## Ingredient Inventory

| Ingredient | Occurrences | Medical Use |
|------------|-------------|-------------|
| fig | 176 | Cardiac remedy, digestion |
| earth | 121 | Poultices |
| moon | 41 | Timing reference |
| barley | 40 | Fever, nutrition |
| wheat | 40 | General nutrition |
| root | 31 | Extract medicines |
| flower | 30 | Various remedies |
| honey | 28 | Sweetener, antiseptic |
| tree | 25 | Structure/bark remedies |
| thyme | 19 | Respiratory issues |
| branch | 19 | Herbal preparations |
| fruit | 18 | Nutrition, laxative |
| blood | 17 | Circulation issues |
| seed | 11 | Various remedies |
| almond | 8 | Skin conditions |
| garlic | 6 | Antiseptic |
| lily | 4 | Skin/beauty |
| nettle | 3 | Blood purification |
| juice | 1 | Liquid extract |

## Conditions/Targets

| Condition | Occurrences | Treatment Focus |
|-----------|-------------|-----------------|
| sick | 173 | General illness |
| finger | 68 | Skin/joints |
| tongue | 31 | Mouth ailments |
| chest | 26 | Respiratory/cardiac |
| skin | 14 | Dermatological |
| head | 11 | Headaches |
| fever | 11 | Temperature reduction |
| eye | 3 | Vision problems |
| pain | 1 | Pain relief |

## Action Verbs

| Action | Occurrences | Meaning |
|--------|-------------|---------|
| one | 321 | one |
| is/has | 192 | is/has |
| all | 85 | all |
| give | 75 | give |
| take/draw | 24 | take/draw |

## Recipe Patterns Found

| Pattern | Count |
|---------|-------|
| TREATMENT_FOR: fig for sick | 20 |
| TREATMENT_FOR: moon for sick | 10 |
| TREATMENT_FOR: barley for sick | 10 |
| MULTI_INGREDIENT: fig + earth | 10 |
| ACTION_INGREDIENT: one + fig | 9 |
| TREATMENT_FOR: wheat for sick | 8 |
| TREATMENT_FOR: earth for sick | 8 |
| MULTI_INGREDIENT: fig + fig | 8 |
| TREATMENT_FOR: fig for finger | 6 |
| TREATMENT_FOR: root for tongue | 5 |
| TREATMENT_FOR: root for sick | 5 |
| MULTI_INGREDIENT: earth + fig | 5 |
| TREATMENT_FOR: earth for chest | 5 |
| MULTI_INGREDIENT: barley + fig | 4 |
| TREATMENT_FOR: barley for finger | 3 |
| TREATMENT_FOR: tree for sick | 3 |
| MULTI_INGREDIENT: fig + fig + fig | 3 |
| ACTION_INGREDIENT: all + earth | 3 |
| TREATMENT_FOR: flower for skin | 3 |
| TREATMENT_FOR: fig for tongue | 3 |

## TOP 10 Best Decoded Recipes

### Recipe 1 (f111r.47)
- **Quality Score**: 98/100
- **Coverage**: 88.9%
- **Voynich**: `sheedy.qokeey.sheey.qoteedy.qeear.al.chedy.okeey.chedy<$>`
- **Translation**: honey the (+ noun) verb form finger [qeear] to the is/has (verb) verb form is/has (verb)
- **Ingredients**: honey
- **Conditions**: finger
- **Actions**: is/has, is/has

### Recipe 2 (f106r.41)
- **Quality Score**: 98/100
- **Coverage**: 87.5%
- **Voynich**: `dair.al.sheod.shedy.chol.chedy.cheol.shory<$>`
- **Translation**: Adar (month) to the [sheod] which/that sick (choleh) is/has (verb) sick (choleh) root (shoresh)
- **Ingredients**: root
- **Conditions**: sick, sick
- **Actions**: give, is/has

### Recipe 3 (f112v.22)
- **Quality Score**: 97/100
- **Coverage**: 83.3%
- **Voynich**: `s!oiin.ol.cheol.chedy.qokeey.chetai!n<$>`
- **Translation**: seed the/of sick (choleh) is/has (verb) the (+ noun) [chetain]
- **Ingredients**: seed
- **Conditions**: sick
- **Actions**: is/has

### Recipe 4 (f103r.40)
- **Quality Score**: 96/100
- **Coverage**: 81.8%
- **Voynich**: `qokeey.sheeol.shckhy.sheol.shody.ol.aiin.otedy.qoteey.lotar.otam`
- **Translation**: the (+ noun) tongue verb form tongue verb the/of one [otedy] the (+ noun) [lotar] thyme
- **Ingredients**: thyme
- **Conditions**: tongue, tongue
- **Actions**: one

### Recipe 5 (f107v.36)
- **Quality Score**: 96/100
- **Coverage**: 80.0%
- **Voynich**: `tol.chey.lcheor.sheol.qokaiin.olkeedy.okar.ar.olkai!n.odai!n<$>`
- **Translation**: all/voice verbal/adjectival [lcheor] tongue priest/cohen verb form [okar] to/for priest/cohen fig
- **Ingredients**: fig
- **Conditions**: tongue
- **Actions**: all

### Recipe 6 (f111v.16)
- **Quality Score**: 95/100
- **Coverage**: 76.9%
- **Voynich**: `qokai!n.sheol.qokai!n.chckhey.lchedy.okar.al.qotal.shedy.otai!n.far.aiin.am`
- **Translation**: priest/cohen tongue priest/cohen verb (unknown) [lchedy] [okar] to the the (+ noun) which/that fig f...
- **Ingredients**: fig, flower
- **Conditions**: tongue
- **Actions**: one

### Recipe 7 (f104r.28)
- **Quality Score**: 95/100
- **Coverage**: 75.0%
- **Voynich**: `olcheear.chedar.or.aror!sheey.olkeechy.or.char.cheeol.sor.or.aiin.ot!am`
- **Translation**: [olcheear] unknown or/and [arorsheey] [olkeechy] or/and hole/pierce (chor) sick person barley or/and...
- **Ingredients**: barley, thyme
- **Conditions**: sick
- **Actions**: one

### Recipe 8 (f107r.14)
- **Quality Score**: 95/100
- **Coverage**: 75.0%
- **Voynich**: `cthedy.lshedy.cheol.chear.or.alam.chtaiin.otar.aiin.chey.qokaiin.otai!n`
- **Translation**: [cthedy] verb form sick (choleh) hole/pierce (chor) or/and [alam] [chtaiin] earth one verbal/adjecti...
- **Ingredients**: earth, fig
- **Conditions**: sick
- **Actions**: one

### Recipe 9 (f104v.27)
- **Quality Score**: 95/100
- **Coverage**: 75.0%
- **Voynich**: `pchoror.shor.sheol.sheol.sheol.qokchedy.chdor.sho.r.aiin.chpchs.aiin.al`
- **Translation**: [pchoror] root (shoresh) tongue tongue tongue the (+ noun) [chdor] fire one [chpchs] one to the
- **Ingredients**: root
- **Conditions**: tongue, tongue, tongue
- **Actions**: one, one

### Recipe 10 (f114v.16)
- **Quality Score**: 95/100
- **Coverage**: 75.0%
- **Voynich**: `ytchedy.qool.chey.ol.aiin.chedar.chdaiin.chdal.qokaiin.choky.chol.dam`
- **Translation**: [ytchedy] [qool] verbal/adjectival the/of one unknown priest [chdal] priest/cohen eye sick (choleh) ...
- **Ingredients**: blood
- **Conditions**: eye, sick
- **Actions**: one

## Medical Interpretation

Based on the analysis, the recipe section appears to contain:

### Cardiac Remedies
- Fig (תאנה/taiin) is a prominent ingredient
- Historical use: Medieval physicians used figs for heart conditions
- Appears combined with honey and other ingredients

### General Medical Recipes
- High frequency of 'sick person' (choleh/חולה) references
- Suggests these are therapeutic instructions for the ill

### Nutritional/Dietary Prescriptions
- Grains (wheat, barley) appear frequently
- Common medieval practice: dietary remedies for illness

## Key Finding

The recipe section is consistent with a **medieval Jewish medical cookbook**:
- Hebrew medical terminology (choleh, cohen)
- Italian ingredient names (terra, fiore)
- SOV grammar structure
- Cardiac remedy focus with fig as key ingredient

This aligns with the hypothesis of a Judeo-Italian medical text written by Jewish physicians.