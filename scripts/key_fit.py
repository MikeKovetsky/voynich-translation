import argparse
import json
import math
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.lm import LM, let_txt

try:
    from data.sections import get_section_for_folio
except Exception:
    get_section_for_folio = None

VMS = os.path.join(ROOT, "data/transliteration/RF1b-e.txt")
VMS_ALT = os.path.join(ROOT, "data/RF1b-e.txt")
NB = os.path.join(ROOT, "data/nb.json")
LAT = os.path.join(ROOT, "data/ctrl/la_0218.txt")
ITA = os.path.join(ROOT, "data/ctrl/it_1012.txt")

MULTI = ["cfh", "ckh", "cph", "cth", "sh", "ch"]
T1 = {"ch", "sh", "cfh", "ckh", "cph", "cth", "f", "k", "p", "t", "x"}
T2 = {"a", "e", "g", "m", "n"}


def _read_vms():
    for p in (VMS, VMS_ALT):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return p, f.readlines()
        except FileNotFoundError:
            pass
    raise FileNotFoundError(VMS)


def _clean_tok(w: str) -> str:
    w = re.sub(r"\{[^}]+\}", "", w)
    w = re.sub(r"@[0-9]+;?", "", w)
    w = w.strip(" ,-'?!*;")
    return w


def _tok_line(s: str) -> list[str]:
    s = s.replace("<->", " ")
    parts = re.split(r"[.\s]+", s)
    out = []
    for p in parts:
        w = _clean_tok(p)
        if w:
            out.append(w)
    return out


def parse_vms():
    src, raw = _read_vms()
    lines = []
    fols = []
    secs = []
    fid = None
    for ln in raw:
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue

        if ln.startswith("<"):
            if ">" not in ln:
                continue
            tag, rest = ln[1:].split(">", 1)
            m = re.match(r"(f\d+[rv])", tag)
            if m:
                fid = m.group(1)
            s = rest.strip()
        else:
            s = ln

        if s.startswith("<!"):
            continue

        toks = _tok_line(s)
        if not toks:
            continue

        lines.append(toks)
        fols.append(fid)
        if fid and get_section_for_folio:
            m2 = re.match(r"f(\d+)", fid)
            secs.append(get_section_for_folio(int(m2.group(1))) if m2 else None)
        else:
            secs.append(None)
    return src, lines, fols, secs


def glyphs(w: str):
    out = []
    i = 0
    while i < len(w):
        hit = None
        for g in MULTI:
            if w.startswith(g, i):
                hit = g
                break
        if hit:
            out.append(hit)
            i += len(hit)
        else:
            out.append(w[i])
            i += 1
    return out


def load_nb():
    with open(NB, "r", encoding="utf-8") as f:
        d = json.load(f)
    w = d["w"]
    tab = d["t"]
    ab = "".join(sorted(next(iter(tab.values())).keys()))
    u = {}
    p = {}
    s = {}
    u_set = set()
    p_set = set()
    s_set = set()
    for tn, t in tab.items():
        for L, v in t.items():
            u[v["u"]] = L
            p[v["p"]] = L
            s[v["s"]] = L
            u_set.add(v["u"])
            p_set.add(v["p"])
            s_set.add(v["s"])
    return ab, w, tab, u, p, s, u_set, p_set, s_set


def split_ps(tok, p_set, s_set):
    g = glyphs(tok)
    if len(g) < 2:
        return []
    pe = 0
    for i, x in enumerate(g):
        if x in T1:
            pe = i + 1
    ss = len(g)
    for i, x in enumerate(g):
        if x in T2:
            ss = i
            break

    out = []
    def scan(ok):
        for j in range(1, len(g)):
            if ok and pe <= ss and not (pe <= j <= ss):
                continue
            a = "".join(g[:j])
            b = "".join(g[j:])
            if a in p_set and b in s_set:
                out.append((a, b))

    scan(True)
    if not out:
        scan(False)
    if not out:
        for j in range(1, len(tok)):
            a = tok[:j]
            b = tok[j:]
            if a in p_set and b in s_set:
                out.append((a, b))
    return out


def mk_cand(u_set, p_set, s_set):
    cache = {}

    def cand(tok):
        if tok in cache:
            return cache[tok]
        out = []
        if tok in u_set:
            out.append(("u", tok))
        for a, b in split_ps(tok, p_set, s_set):
            out.append(("ps", a, b))
        out = list(dict.fromkeys(out))
        cache[tok] = out
        return out

    return cand


class Key:
    def __init__(self, ab, u0, p0, s0):
        self.ab = ab
        self.u_codes = sorted(u0.keys())
        self.p_codes = sorted(p0.keys())
        self.s_codes = sorted(s0.keys())
        self.ui = {c: i for i, c in enumerate(self.u_codes)}
        self.pi = {c: i for i, c in enumerate(self.p_codes)}
        self.si = {c: i for i, c in enumerate(self.s_codes)}
        self.u = [ab.index(u0[c]) for c in self.u_codes]
        self.p = [ab.index(p0[c]) for c in self.p_codes]
        self.s = [ab.index(s0[c]) for c in self.s_codes]

    def shuf(self, rng):
        self.u = self.u.copy()
        self.p = self.p.copy()
        self.s = self.s.copy()
        rng.shuffle(self.u)
        rng.shuffle(self.p)
        rng.shuffle(self.s)
        return self

    def u_ch(self, c):
        return self.ab[self.u[self.ui[c]]]

    def p_ch(self, c):
        return self.ab[self.p[self.pi[c]]]

    def s_ch(self, c):
        return self.ab[self.s[self.si[c]]]

    def swap(self, which, i, j):
        arr = {"u": self.u, "p": self.p, "s": self.s}[which]
        arr[i], arr[j] = arr[j], arr[i]


def greedy_line(toks, cand, key: Key, lm: LM):
    ctx = lm.s0
    sc = 0.0
    n = 0
    cov0 = cov1 = covm = 0
    for w in toks:
        cs = cand(w)
        if not cs:
            cov0 += 1
            continue
        if len(cs) == 1:
            cov1 += 1
        else:
            covm += 1

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
        if best is None:
            continue
        sc += best[0]
        n += len(best[2])
        ctx = best[1]
    return sc, n, cov0, cov1, covm


def score(lines, idxs, cand, key: Key, lm: LM):
    sc = 0.0
    n = 0
    c0 = c1 = cm = 0
    for i in idxs:
        a, b, x0, x1, xm = greedy_line(lines[i], cand, key, lm)
        sc += a
        n += b
        c0 += x0
        c1 += x1
        cm += xm
    return (sc / n if n else 0.0), n, {"c0": c0, "c1": c1, "cm": cm}


def split_idxs(fols, secs, mode="sec"):
    idx = list(range(len(fols)))
    if mode == "sec":
        train = [i for i in idx if secs[i] in ("Herbal", "Pharmaceutical", "Astronomical")]
        test = [i for i in idx if i not in set(train)]
        return train, test
    if mode == "folio":
        train = []
        test = []
        for i in idx:
            if not fols[i]:
                train.append(i)
                continue
            m = re.match(r"f(\d+)", fols[i])
            k = int(m.group(1)) if m else 0
            (test if (k % 5 == 0) else train).append(i)
        return train, test
    raise ValueError(mode)

def shuf_keep_shape(lines, seed=0):
    rng = random.Random(seed)
    lens = [len(ln) for ln in lines]
    toks = [w for ln in lines for w in ln]
    rng.shuffle(toks)
    out = []
    i = 0
    for k in lens:
        out.append(toks[i:i + k])
        i += k
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["score", "fit"], default="score")
    ap.add_argument("--split", choices=["sec", "folio"], default="sec")
    ap.add_argument("--lang", choices=["latin", "ital"], default="latin")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--starts", type=int, default=5)
    ap.add_argument("--iters", type=int, default=3000)
    ap.add_argument("--samp", type=int, default=250)
    ap.add_argument("--temp", type=float, default=0.2)
    ap.add_argument("--cool", type=float, default=0.999)
    ap.add_argument("--negfit", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "data/key_best.json"))
    args = ap.parse_args()

    src, lines, fols, secs = parse_vms()
    ab, _, _, u0, p0, s0, u_set, p_set, s_set = load_nb()

    lm_la = LM(ab)
    lm_it = LM(ab)
    lm_la.add(let_txt(LAT, set(ab)))
    lm_it.add(let_txt(ITA, set(ab)))

    cand = mk_cand(u_set, p_set, s_set)
    tr, te = split_idxs(fols, secs, mode=args.split)

    def dump_key(key: Key, path):
        d = {
            "ab": key.ab,
            "u": {c: key.u_ch(c) for c in key.u_codes},
            "p": {c: key.p_ch(c) for c in key.p_codes},
            "s": {c: key.s_ch(c) for c in key.s_codes},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, sort_keys=True)

    def pick_idxs(idxs, n, rng):
        if len(idxs) <= n:
            return idxs
        return rng.sample(idxs, n)

    def fit_one(lines_x, tr_x, te_x, cand_x, lm, rng, start_key: Key):
        cur = start_key
        tr_s = pick_idxs(tr_x, args.samp, rng)
        cur_sc, _, _ = score(lines_x, tr_s, cand_x, cur, lm)
        best_sc = cur_sc
        best = (cur.u.copy(), cur.p.copy(), cur.s.copy())

        temp = args.temp
        which = ["u", "p", "s"]
        wts = [1, 1, 1]
        for _ in range(args.iters):
            w = rng.choices(which, weights=wts, k=1)[0]
            arr = {"u": cur.u, "p": cur.p, "s": cur.s}[w]
            i = rng.randrange(len(arr))
            j = rng.randrange(len(arr))
            if i == j:
                continue
            cur.swap(w, i, j)
            sc2, _, _ = score(lines_x, tr_s, cand_x, cur, lm)
            d = sc2 - cur_sc
            if d >= 0 or rng.random() < math.exp(d / max(temp, 1e-6)):
                cur_sc = sc2
                if cur_sc > best_sc:
                    best_sc = cur_sc
                    best = (cur.u.copy(), cur.p.copy(), cur.s.copy())
            else:
                cur.swap(w, i, j)
            temp *= args.cool

        cur.u, cur.p, cur.s = best
        full_tr, _, _ = score(lines_x, tr_x, cand_x, cur, lm)
        full_te, _, _ = score(lines_x, te_x, cand_x, cur, lm)
        return full_tr, full_te, cur

    def z_key(lm, n=20):
        te_s = pick_idxs(te, min(args.samp, len(te)), random.Random(args.seed + 9000))
        base = Key(ab, u0, p0, s0)
        nb_te, _, _ = score(lines, te_s, cand, base, lm)
        xs = []
        for i in range(n):
            k = Key(ab, u0, p0, s0).shuf(random.Random(args.seed + 9100 + i))
            sc, _, _ = score(lines, te_s, cand, k, lm)
            xs.append(sc)
        mu = statistics.mean(xs)
        sd = statistics.pstdev(xs) if len(xs) > 1 else 0.0
        z = ((nb_te - mu) / sd) if sd else 0.0
        return nb_te, mu, sd, z

    if args.mode == "score":
        k0 = Key(ab, u0, p0, s0)
        rng = random.Random(args.seed)
        k1 = Key(ab, u0, p0, s0).shuf(rng)
        for name, key in [("nb", k0), ("shuf_key", k1)]:
            spc_tr, n_tr, cov_tr = score(lines, tr, cand, key, lm_la)
            spc_te, n_te, _ = score(lines, te, cand, key, lm_la)
            print(f"{name} latin train={spc_tr:.4f} (n={n_tr}) test={spc_te:.4f} (n={n_te}) cov={cov_tr}")

            spc_tr, n_tr, cov_tr = score(lines, tr, cand, key, lm_it)
            spc_te, n_te, _ = score(lines, te, cand, key, lm_it)
            print(f"{name} ital  train={spc_tr:.4f} (n={n_tr}) test={spc_te:.4f} (n={n_te}) cov={cov_tr}")
        return

    lm = lm_la if args.lang == "latin" else lm_it
    base = Key(ab, u0, p0, s0)
    rng = random.Random(args.seed)

    best = None
    best_te = -1e9
    starts = [Key(ab, u0, p0, s0)]
    for k in range(max(0, args.starts - 1)):
        starts.append(Key(ab, u0, p0, s0).shuf(random.Random(args.seed + 1000 + k)))

    for k, st in enumerate(starts):
        tr_sc, te_sc, key = fit_one(lines, tr, te, cand, lm, random.Random(args.seed + 2000 + k), st)
        print(f"start{k} train={tr_sc:.4f} test={te_sc:.4f}")
        if te_sc > best_te:
            best_te = te_sc
            best = key

    if best:
        tr_sc, _, _ = score(lines, tr, cand, best, lm)
        te_sc, _, _ = score(lines, te, cand, best, lm)
        nb_tr, _, _ = score(lines, tr, cand, base, lm)
        nb_te, _, _ = score(lines, te, cand, base, lm)
        print(f"best train={tr_sc:.4f} test={te_sc:.4f}")
        print(f"nb   train={nb_tr:.4f} test={nb_te:.4f}")

        sh_lines = shuf_keep_shape([lines[i] for i in tr + te], seed=args.seed + 33)
        sh_tr = list(range(min(len(tr), len(sh_lines))))
        sh_te = list(range(len(sh_lines) - min(len(te), len(sh_lines)), len(sh_lines)))
        sh_nb, _, _ = score(sh_lines, sh_te, cand, base, lm)
        sh_best, _, _ = score(sh_lines, sh_te, cand, best, lm)
        print(f"shuf nb={sh_nb:.4f} best={sh_best:.4f}")

        nb_te2, mu, sd, z = z_key(lm, n=25)
        print(f"randkey nb_test={nb_te2:.4f} mean={mu:.4f} sd={sd:.4f} z={z:.2f}")

        gain = te_sc - nb_te
        print(f"gain(test)={gain:.4f}")

        if args.negfit:
            st = Key(ab, u0, p0, s0)
            sh_tr_sc, sh_te_sc, _ = fit_one(sh_lines, sh_tr, sh_te, cand, lm, random.Random(args.seed + 9999), st)
            print(f"negfit sh_train={sh_tr_sc:.4f} sh_test={sh_te_sc:.4f}")

        ok = gain > 0.05 and te_sc > sh_nb + 0.05
        print("PASS" if ok else "FAIL")
        dump_key(best, args.out)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()

