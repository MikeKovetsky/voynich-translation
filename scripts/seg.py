import argparse
import json
import math
import os
from collections import Counter

from scripts.key_fit import Key, load_nb, mk_cand, parse_vms, score
from scripts.lm import LM, let_txt, words_txt

ROOT = os.path.dirname(os.path.dirname(__file__))
LAT = os.path.join(ROOT, "data/ctrl/la_0218.txt")
ITA = os.path.join(ROOT, "data/ctrl/it_1012.txt")


def mk_lex(path, ab, min_len=2, top=50000):
    ws = words_txt(path, min_len=min_len)
    c = Counter(ws)
    lex = Counter()
    for w, n in c.most_common(top):
        up = []
        ok = True
        for ch in w:
            L = ch.upper()
            if L == "J":
                L = "I"
            if L == "K":
                L = "C"
            if L == "W":
                L = "V"
            if L not in ab:
                ok = False
                break
            up.append(L)
        if ok and up:
            lex["".join(up)] += n
    return lex


def viterbi(txt, lex: Counter, max_w=20, unk=-6.0):
    n = len(txt)
    dp = [-1e18] * (n + 1)
    bp = [-1] * (n + 1)
    bw = [""] * (n + 1)
    dp[0] = 0.0

    for i in range(n):
        if dp[i] <= -1e17:
            continue
        jmax = min(n, i + max_w)
        for j in range(i + 1, jmax + 1):
            w = txt[i:j]
            if w in lex:
                sc = dp[i] + math.log(lex[w] + 1.0)
            else:
                sc = dp[i] + unk * (j - i)
            if sc > dp[j]:
                dp[j] = sc
                bp[j] = i
                bw[j] = w

    out = []
    i = n
    while i > 0 and bp[i] >= 0:
        out.append(bw[i])
        i = bp[i]
    out.reverse()
    return out


def cov(words, lex: Counter):
    if not words:
        return {"w": 0, "wk": 0, "ck": 0, "c": 0}
    wk = sum(1 for w in words if w in lex)
    ck = sum(len(w) for w in words if w in lex)
    c = sum(len(w) for w in words)
    return {"w": len(words), "wk": wk, "ck": ck, "c": c}


def load_key(path, ab, u0, p0, s0):
    if not path:
        return Key(ab, u0, p0, s0)
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    k = Key(ab, u0, p0, s0)
    k.u = [ab.index(d["u"][c]) for c in k.u_codes]
    k.p = [ab.index(d["p"][c]) for c in k.p_codes]
    k.s = [ab.index(d["s"][c]) for c in k.s_codes]
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["latin", "ital"], default="latin")
    ap.add_argument("--key", default="")
    ap.add_argument("--lines", type=int, default=1000)
    args = ap.parse_args()

    _, lines, fols, secs = parse_vms()
    ab, _, _, u0, p0, s0, u_set, p_set, s_set = load_nb()
    cand = mk_cand(u_set, p_set, s_set)
    key = load_key(args.key, ab, u0, p0, s0)

    lm = LM(ab)
    if args.lang == "latin":
        lm.add(let_txt(LAT, set(ab)))
        lex = mk_lex(LAT, ab)
    else:
        lm.add(let_txt(ITA, set(ab)))
        lex = mk_lex(ITA, ab)

    idxs = list(range(min(args.lines, len(lines))))
    spc, n, cov0 = score(lines, idxs, cand, key, lm)
    print(f"decode {args.lang} spc={spc:.4f} n={n} cov={cov0}")

    tot = Counter()
    for ln in lines[: args.lines]:
        sc, nn, *_ = score([ln], [0], cand, key, lm)
        # greedy decode output isn't returned by score(); so rebuild per line by reusing score() logic:
        # decode via best-per-token in score() is deterministic under LM; we reconstruct by rerunning locally.
        ctx = lm.s0
        out = []
        for w in ln:
            cs = cand(w)
            best = None
            for c in cs:
                if c[0] == "u":
                    txt = key.u_ch(c[1])
                else:
                    txt = key.p_ch(c[1]) + key.s_ch(c[2])
                ctx2 = ctx
                sc2 = 0.0
                for ch in txt:
                    d, ctx2 = lm.step(ctx2, ch)
                    sc2 += d
                if best is None or sc2 > best[0]:
                    best = (sc2, ctx2, txt)
            if best:
                out.append(best[2])
                ctx = best[1]
        txt = "".join(out)
        if not txt:
            continue
        ws = viterbi(txt, lex)
        tot.update(cov(ws, lex))

    if tot["w"]:
        print(f"seg words={tot['w']} known={tot['wk']} ({tot['wk']/tot['w']:.3f})")
        print(f"seg chars={tot['c']} known={tot['ck']} ({tot['ck']/tot['c']:.3f})")


if __name__ == "__main__":
    main()

