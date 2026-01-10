import argparse
import json
import os

from scripts.key_fit import Key, load_nb, mk_cand, parse_vms
from scripts.lm import LM, let_txt
from scripts.seg import mk_lex, viterbi

ROOT = os.path.dirname(os.path.dirname(__file__))
LAT = os.path.join(ROOT, "data/ctrl/la_0218.txt")
ITA = os.path.join(ROOT, "data/ctrl/it_1012.txt")


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


def dec_line(toks, cand, key: Key, lm: LM):
    ctx = lm.s0
    out = []
    for w in toks:
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
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["latin", "ital"], default="latin")
    ap.add_argument("--key", default=os.path.join(ROOT, "data/key_best.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data/plain.txt"))
    ap.add_argument("--seg", action="store_true")
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

    with open(args.out, "w", encoding="utf-8") as f:
        for i, ln in enumerate(lines):
            txt = dec_line(ln, cand, key, lm)
            if args.seg and txt:
                ws = viterbi(txt, lex)
                txt = " ".join(ws)
            fol = fols[i] or ""
            sec = secs[i] or ""
            f.write(f"{fol}\t{sec}\t{txt}\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

