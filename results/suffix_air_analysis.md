# Morphology Decoder v2: The `-air` Suffix Analysis

**Source:** `data/eva_ivtff.txt` (H-transliteration)
**Dictionary:** `v13`

## Hypothesis
Testing if `-air` equates to Latin suffixes like `-orium`, `-arium`, `-arius`.

## Findings

| Voynich Word | Count | Root | Suffix | Preceded by `ol` | Latin Match? | Dictionary Status |
|---|---|---|---|---|---|---|
| `dair` | 99 | `d` | `-air` | 2 | - | **Adar (month)** (Hebrew) |
| `sair` | 26 | `s` | `-air` | 0 | - | **barley** (Hebrew) |
| `daiir` | 22 | `d` | `-aiir` | 1 | - | New |
| `okair` | 21 | `ok` | `-air` | 1 | ? (oc-arium?) | **plant_candidate** (voynich_inferred) |
| `otair` | 21 | `ot` | `-air` | 0 | - | **earth** (Italian) |
| `qokair` | 17 | `qok` | `-air` | 0 | - | New |
| `kair` | 14 | `k` | `-air` | 0 | - | New |
| `tair` | 13 | `t` | `-air` | 0 | - | **earth** (Italian) |
| `okaiir` | 6 | `ok` | `-aiir` | 0 | ? (oc-arium?) | **plant_candidate** (voynich_inferred) |
| `rair` | 6 | `r` | `-air` | 0 | - | New |
| `saiir` | 6 | `s` | `-aiir` | 0 | - | **barley** (Hebrew) |
| `ykair` | 6 | `yk` | `-air` | 0 | - | **unknown_object** () |
| `qotair` | 6 | `qot` | `-air` | 0 | - | New |
| `orair` | 5 | `or` | `-air` | 0 | - | **plant_term** (botanical) |
| `odair` | 5 | `od` | `-air` | 0 | - | **Adar (month)** (Hebrew) |
| `qoair` | 4 | `qo` | `-air` | 0 | - | **plant:ricinus** (botanical) |
| `otaiir` | 4 | `ot` | `-aiir` | 0 | - | **plant:tamus communis** (botanical) |
| `pchdair` | 4 | `pchd` | `-air` | 0 | - | **plant_term** (botanical) |
| `olkair` | 4 | `olk` | `-air` | 0 | - | **[PLANT NAME]** () |
| `opair` | 4 | `op` | `-air` | 0 | - | **fruit** (Hebrew) |
| `lkair` | 4 | `lk` | `-air` | 0 | - | **ingredient_candidate** (voynich_inferred) |
| `qodair` | 3 | `qod` | `-air` | 0 | - | **plant_term** (botanical) |
| `oair` | 3 | `o` | `-air` | 0 | - | **plant_term** (botanical) |
| `ypair` | 3 | `yp` | `-air` | 0 | - | **And plant:scabiosa** (botanical) |
| `ytair` | 3 | `yt` | `-air` | 0 | - | **And earth** (Italian) |
| `qokaiir` | 3 | `qok` | `-aiir` | 0 | - | **plant_term** (botanical) |
| `chodair` | 2 | `chod` | `-air` | 0 | - | **plant_candidate** (voynich_inferred) |
| `ydair` | 2 | `yd` | `-air` | 0 | - | New |
| `odaiir` | 2 | `od` | `-aiir` | 0 | - | **plant_candidate** (voynich_inferred) |
| `podair` | 2 | `pod` | `-air` | 0 | - | **plant_term** (botanical) |
| `pair` | 2 | `p` | `-air` | 0 | - | **plant:scabiosa** (botanical) |
| `shkair` | 2 | `shk` | `-air` | 0 | Cich-orium (Chicory) | **plant:scabiosa** (botanical) |
| `podaiir` | 2 | `pod` | `-aiir` | 0 | - | **plant:geranium** (botanical) |
| `olaiir` | 2 | `ol` | `-aiir` | 0 | - | **plant_candidate** (voynich_inferred) |
| `ykaiir` | 2 | `yk` | `-aiir` | 0 | - | New |
| `yair` | 2 | `y` | `-air` | 0 | - | **plant_term** (botanical) |
| `qofair` | 2 | `qof` | `-air` | 0 | - | New |
| `shdair` | 2 | `shd` | `-air` | 1 | - | New |
| `tedair` | 2 | `ted` | `-air` | 0 | - | New |
| `chdair` | 2 | `chd` | `-air` | 0 | - | New |
| `dairair` | 2 | `dair` | `-air` | 0 | - | **plant:cyanus** (botanical) |
| `paiir` | 2 | `p` | `-aiir` | 0 | - | New |
| `lkaiir` | 2 | `lk` | `-aiir` | 0 | - | New |
| `oaiir` | 2 | `o` | `-aiir` | 0 | - | **plant_candidate** (voynich_inferred) |
| `syaiir` | 1 | `sy` | `-aiir` | 0 | - | **barley** (Hebrew) |
| `chor<-><plant>dair` | 1 | `chor<-><plant>d` | `-air` | 0 | - | New |
| `otcham<-><plant>yaiir` | 1 | `otcham<-><plant>y` | `-aiir` | 0 | - | New |
| `chaiir` | 1 | `ch` | `-aiir` | 0 | - | **plant_candidate** (voynich_inferred) |
| `chair` | 1 | `ch` | `-air` | 0 | - | **plant_candidate** (voynich_inferred) |
| `koair` | 1 | `ko` | `-air` | 0 | - | New |
| `cphaldy<-><plant>dair` | 1 | `cphaldy<-><plant>d` | `-air` | 0 | - | New |
| `ychair` | 1 | `ych` | `-air` | 0 | - | New |
| `s<-><plant>yteair` | 1 | `s<-><plant>yte` | `-air` | 0 | - | New |
| `shair` | 1 | `sh` | `-air` | 0 | - | New |
| `deeaiir` | 1 | `dee` | `-aiir` | 0 | - | New |
| `saraiir` | 1 | `sar` | `-aiir` | 0 | - | New |
| `yshedair` | 1 | `yshed` | `-air` | 0 | - | New |
| `qoky<-><plant>olk<-><plant>checkhy<-><plant><\>ysair` | 1 | `qoky<-><plant>olk<-><plant>checkhy<-><plant><\>ys` | `-air` | 0 | - | New |
| `lshaiir` | 1 | `lsh` | `-aiir` | 0 | - | New |
| `dal<-><plant>dair` | 1 | `dal<-><plant>d` | `-air` | 0 | - | New |
| `daiin<-><plant>dair` | 1 | `daiin<-><plant>d` | `-air` | 0 | - | New |
| `pdair` | 1 | `pd` | `-air` | 0 | - | New |
| `oraly<-><plant>olaiir` | 1 | `oraly<-><plant>ol` | `-aiir` | 0 | - | New |
| `ofair` | 1 | `of` | `-air` | 0 | - | **plant_candidate** (voynich_inferred) |
| `pchair` | 1 | `pch` | `-air` | 0 | - | New |
| `kedair` | 1 | `ked` | `-air` | 0 | - | New |
| `qoaiir` | 1 | `qo` | `-aiir` | 0 | - | **Variant of qoaiin (plant_candidate (morphological_derivative (qo- + aiin)))** (voynich_inferred) |
| `yshealkair` | 1 | `yshealk` | `-air` | 0 | - | New |
| `faiir` | 1 | `f` | `-aiir` | 0 | - | New |
| `tolair` | 1 | `tol` | `-air` | 0 | - | New |
| `okorair` | 1 | `okor` | `-air` | 0 | - | New |
| `yfair` | 1 | `yf` | `-air` | 0 | - | New |
| `shekair` | 1 | `shek` | `-air` | 0 | - | New |
| `shokaiir` | 1 | `shok` | `-aiir` | 0 | - | New |
| `chedair` | 1 | `ched` | `-air` | 0 | - | **plant_candidate** (voynich_inferred) |
| `sosaiir` | 1 | `sos` | `-aiir` | 0 | - | New |
| `solair` | 1 | `sol` | `-air` | 0 | - | New |
| `okinaiir` | 1 | `okin` | `-aiir` | 0 | - | New |
| `cheodaiir` | 1 | `cheod` | `-aiir` | 0 | - | New |
| `chykar<-><gap>okair` | 1 | `chykar<-><gap>ok` | `-air` | 0 | - | New |
| `doair` | 1 | `do` | `-air` | 0 | - | New |
| `otaldal<-><gap>dair` | 1 | `otaldal<-><gap>d` | `-air` | 0 | - | New |
| `okolair` | 1 | `okol` | `-air` | 0 | - | New |
| `ykeeeedaiir` | 1 | `ykeeeed` | `-aiir` | 0 | - | New |
| `chtam<-><wide gap>opaiir` | 1 | `chtam<-><wide gap>op` | `-aiir` | 0 | - | New |
| `ytaiir` | 1 | `yt` | `-aiir` | 0 | - | New |
| `okalair` | 1 | `okal` | `-air` | 0 | - | New |
| `oiair` | 1 | `oi` | `-air` | 0 | - | New |
| `qolair` | 1 | `qol` | `-air` | 0 | - | New |
| `otedair` | 1 | `oted` | `-air` | 0 | - | New |
| `darair` | 1 | `dar` | `-air` | 0 | - | New |
| `schedair` | 1 | `sched` | `-air` | 0 | - | New |
| `chtair` | 1 | `cht` | `-air` | 0 | - | New |
| `sodair` | 1 | `sod` | `-air` | 0 | - | New |
| `ykdair` | 1 | `ykd` | `-air` | 0 | - | New |
| `schedaiir` | 1 | `sched` | `-aiir` | 0 | - | New |
| `dtedair` | 1 | `dted` | `-air` | 0 | - | New |
| `olair` | 1 | `ol` | `-air` | 1 | - | New |
| `octhair` | 1 | `octh` | `-air` | 0 | - | New |
| `losair` | 1 | `los` | `-air` | 0 | - | New |
| `lshodair` | 1 | `lshod` | `-air` | 0 | - | New |
| `qoeair` | 1 | `qoe` | `-air` | 0 | - | New |
| `ykodair` | 1 | `ykod` | `-air` | 0 | - | New |
| `eair` | 1 | `e` | `-air` | 0 | - | New |
| `shy<-><crease>daiir` | 1 | `shy<-><crease>d` | `-aiir` | 0 | - | New |
| `oty<-><plant>daiin<-><plant>otal<-><plant>dair` | 1 | `oty<-><plant>daiin<-><plant>otal<-><plant>d` | `-air` | 0 | - | New |
| `cheeoldair` | 1 | `cheeold` | `-air` | 0 | - | New |
| `y<-><plant>ypchdair` | 1 | `y<-><plant>ypchd` | `-air` | 0 | - | New |
| `ytolaiir` | 1 | `ytol` | `-aiir` | 0 | - | New |
| `qokeodair` | 1 | `qokeod` | `-air` | 0 | - | New |
| `lsair` | 1 | `ls` | `-air` | 0 | - | New |
| `arair` | 1 | `ar` | `-air` | 0 | - | New |
| `yaiir` | 1 | `y` | `-aiir` | 0 | - | New |
| `okeeodair` | 1 | `okeeod` | `-air` | 0 | - | New |
| `oteodair` | 1 | `oteod` | `-air` | 0 | - | New |
| `alkair` | 1 | `alk` | `-air` | 0 | - | New |
| `porair` | 1 | `por` | `-air` | 0 | - | New |
| `aporair` | 1 | `apor` | `-air` | 0 | - | New |
| `pshoair` | 1 | `psho` | `-air` | 0 | - | New |
| `tshodair` | 1 | `tshod` | `-air` | 0 | - | New |
| `akair` | 1 | `ak` | `-air` | 0 | - | New |
| `chdalkair` | 1 | `chdalk` | `-air` | 0 | - | New |
| `sholkair` | 1 | `sholk` | `-air` | 0 | - | New |
| `lolkair` | 1 | `lolk` | `-air` | 0 | - | New |
| `tarair` | 1 | `tar` | `-air` | 0 | - | New |
| `parair` | 1 | `par` | `-air` | 0 | - | New |
| `dyair` | 1 | `dy` | `-air` | 0 | - | New |
| `olpair` | 1 | `olp` | `-air` | 0 | - | New |
| `fcheokair` | 1 | `fcheok` | `-air` | 0 | - | New |
| `oteolair` | 1 | `oteol` | `-air` | 0 | - | New |
| `opcheodair` | 1 | `opcheod` | `-air` | 0 | - | New |
| `chokedair` | 1 | `choked` | `-air` | 0 | - | New |
| `alair` | 1 | `al` | `-air` | 0 | - | New |
| `otalair` | 1 | `otal` | `-air` | 0 | - | New |
| `shedair` | 1 | `shed` | `-air` | 0 | - | New |
| `pchodair` | 1 | `pchod` | `-air` | 0 | - | New |
| `chtaiir` | 1 | `cht` | `-aiir` | 0 | - | New |
| `chotair` | 1 | `chot` | `-air` | 0 | - | **plant_candidate** (voynich_inferred) |
| `chokair` | 1 | `chok` | `-air` | 0 | - | New |
| `lair` | 1 | `l` | `-air` | 0 | - | New |
| `otchedair` | 1 | `otched` | `-air` | 0 | - | New |
| `dkair` | 1 | `dk` | `-air` | 0 | - | New |
| `tchedair` | 1 | `tched` | `-air` | 0 | - | New |
| `olkaiir` | 1 | `olk` | `-aiir` | 0 | - | **ingredient_candidate** (voynich_inferred) |
| `qokeedair` | 1 | `qokeed` | `-air` | 0 | - | New |
| `oedair` | 1 | `oed` | `-air` | 0 | - | New |
| `poedair` | 1 | `poed` | `-air` | 0 | - | New |

## Distribution Analysis
- Total `-air` words types found: 147
- Words preceded by `ol` (or variants): 5 (3.4%)

Low co-occurrence with `ol` (likely 'the' or 'a') observed. This weak correlation suggests they might not be standard nouns, or `ol` is not the primary determiner for this class of words. Alternatively, these could be proper nouns (places) or abstract concepts (calendar months, as seen with `dair`/`Adar`) that don't take the article.
