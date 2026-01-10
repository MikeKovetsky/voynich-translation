import json
import math
import os
import random
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from data.sections import get_section_for_folio
except Exception:
    get_section_for_folio = None

VMS = "data/transliteration/RF1b-e.txt"
VMS_ALT = "data/RF1b-e.txt"
NB = "data/nb.json"
LAT = "data/ctrl/la_0218.txt"
ITA = "data/ctrl/it_1012.txt"

WIN = 10
BEAM = 50
SEED = 0
N_LINES = 1000
MIN_BEST = 20
TOP = 5

MULTI = ["cfh", "ckh", "cph", "cth", "sh", "ch"]
T1 = {"ch", "sh", "cfh", "ckh", "cph", "cth", "f", "k", "p", "t", "x"}
T2 = {"a", "e", "g", "m", "n"}

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


def read_lines(path):
    cands = [path]
    if path.startswith("data/transliteration"):
        cands.append(VMS_ALT)
    for p in cands:
        try:
            with open(os.path.join(ROOT, p), "r", encoding="utf-8") as f:
                return p, f.readlines()
        except FileNotFoundError:
            pass
    raise FileNotFoundError(path)


def clean_tok(w: str) -> str:
    w = re.sub(r"\{[^}]+\}", "", w)
    w = re.sub(r"@[0-9]+;?", "", w)
    w = w.strip(" ,-'?!*;")
    return w


def tok_line(s: str) -> list[str]:
    s = s.replace("<->", " ")
    parts = re.split(r"[.\s]+", s)
    out = []
    for p in parts:
        w = clean_tok(p)
        if w:
            out.append(w)
    return out


def parse_vms(path=VMS):
    src, raw = read_lines(path)
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

        toks = tok_line(s)
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


def nb_load(path=NB):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        d = json.load(f)
    return d["w"], d["t"]


def nb_inv(tab):
    u = defaultdict(set)
    p = defaultdict(set)
    s = defaultdict(set)
    for tn, t in tab.items():
        for L, v in t.items():
            u[v["u"]].add(L)
            p[v["p"]].add(L)
            s[v["s"]].add(L)
    return u, p, s


def inv_key(tab, seed=0):
    rng = random.Random(seed)
    out = {}
    for tn, t in tab.items():
        lets = list(t.keys())
        for k in ("u", "p", "s"):
            vals = [t[L][k] for L in lets]
            rng.shuffle(vals)
            for L, v in zip(lets, vals):
                out.setdefault(tn, {}).setdefault(L, {})[k] = v
    return out


def mk_dec(u, p, s):
    cache = {}

    def dec(w: str):
        if w in cache:
            return cache[w]
        out = []
        if w in u:
            out.extend(u[w])

        g = glyphs(w)
        if len(g) > 1:
            pe = 0
            for i, x in enumerate(g):
                if x in T1:
                    pe = i + 1
            ss = len(g)
            for i, x in enumerate(g):
                if x in T2:
                    ss = i
                    break
            cand = []

            def try_split(ok):
                for j in range(1, len(g)):
                    if ok and pe <= ss and not (pe <= j <= ss):
                        continue
                    a = "".join(g[:j])
                    b = "".join(g[j:])
                    if a in p and b in s:
                        cand.append(next(iter(p[a])) + next(iter(s[b])))

            try_split(True)
            if not cand:
                try_split(False)
            if not cand:
                for j in range(1, len(w)):
                    a = w[:j]
                    b = w[j:]
                    if a in p and b in s:
                        cand.append(next(iter(p[a])) + next(iter(s[b])))
            out.extend(cand)
        out = sorted(set(out))
        cache[w] = out
        return out

    return dec


def mk_det(u, p, s):
    u1 = {k: next(iter(v)) for k, v in u.items()}
    p1 = {k: next(iter(v)) for k, v in p.items()}
    s1 = {k: next(iter(v)) for k, v in s.items()}

    def det(w: str):
        if w in u1:
            return u1[w]
        g = glyphs(w)
        pe = 0
        for i, x in enumerate(g):
            if x in T1:
                pe = i + 1
        ss = len(g)
        for i, x in enumerate(g):
            if x in T2:
                ss = i
                break

        def scan(ok):
            for j in range(1, len(g)):
                if ok and pe <= ss and not (pe <= j <= ss):
                    continue
                a = "".join(g[:j])
                b = "".join(g[j:])
                if a in p1 and b in s1:
                    return p1[a] + s1[b]
            return None

        x = scan(True) or scan(False)
        if x:
            return x
        for j in range(1, len(w)):
            a = w[:j]
            b = w[j:]
            if a in p1 and b in s1:
                return p1[a] + s1[b]
        return ""

    return det


class LM:
    def __init__(self, ab: str, n=3, a=0.5):
        self.ab = ab
        self.n = n
        self.a = a
        self.v = len(ab)
        self.c = defaultdict(Counter)
        self.t = Counter()
        self.s0 = "^" * (n - 1)

    def add(self, txt: str):
        ctx = self.s0
        for ch in txt:
            if ch not in self.ab:
                continue
            self.c[ctx][ch] += 1
            self.t[ctx] += 1
            ctx = (ctx + ch)[-(self.n - 1) :]

    def step(self, ctx: str, ch: str):
        num = self.c[ctx][ch] + self.a
        den = self.t[ctx] + self.a * self.v
        return math.log(num / den), (ctx + ch)[-(self.n - 1) :]


def lm_spc(lm: LM, txt: str):
    ctx = lm.s0
    sc = 0.0
    n = 0
    for ch in txt:
        if ch not in lm.ab:
            continue
        d, ctx = lm.step(ctx, ch)
        sc += d
        n += 1
    return sc / n if n else 0.0, n


def strip_gut(lines):
    a = 0
    b = len(lines)
    for i, ln in enumerate(lines):
        if "*** start of" in ln.lower():
            a = i + 1
            break
    for i in range(len(lines) - 1, -1, -1):
        if "*** end of" in lines[i].lower():
            b = i
            break
    return lines[a:b]


def norm_txt(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def let_txt(path, ab):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    lines = strip_gut(lines)
    s = norm_txt("".join(lines))
    s = s.translate(str.maketrans({"j": "i", "k": "c", "w": "v"}))
    out = []
    for c in s:
        if "a" <= c <= "z":
            L = c.upper()
            if L in ab:
                out.append(L)
    return out


def beam_line(toks, dec, lm: LM):
    beams = [(0.0, lm.s0, "")]
    cov = {"z": 0, "o": 0, "m": 0}
    for w in toks:
        cands = dec(w)
        if not cands:
            cov["z"] += 1
            continue
        if len(cands) == 1:
            cov["o"] += 1
        else:
            cov["m"] += 1

        nxt = []
        for sc, ctx, out in beams:
            for add in cands:
                sc2 = sc
                ctx2 = ctx
                for ch in add:
                    d, ctx2 = lm.step(ctx2, ch)
                    sc2 += d
                nxt.append((sc2, ctx2, out + add))
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:BEAM]

    return beams, cov


def score_lines(lines, dec, lm: LM, fols=None, secs=None, n_lines=N_LINES):
    out = []
    cov = Counter()
    for i, ln in enumerate(lines[:n_lines]):
        beams, c = beam_line(ln, dec, lm)
        cov.update(c)
        if not beams:
            continue
        sc, _, txt = beams[0]
        if not txt:
            continue
        out.append(
            {
                "i": i,
                "fol": fols[i] if fols else None,
                "sec": secs[i] if secs else None,
                "n": len(txt),
                "sc": sc,
                "spc": sc / len(txt),
                "txt": txt,
            }
        )
    return out, cov


def sum_score(rows):
    if not rows:
        return None
    n = sum(r["n"] for r in rows)
    sc = sum(r["sc"] for r in rows)
    return {"n": n, "spc": sc / n if n else 0.0}

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


def nb_pick(rng, w):
    ks = list(w.keys())
    tot = sum(w.values())
    x = rng.randrange(tot)
    s = 0
    for k in ks:
        s += w[k]
        if x < s:
            return k
    return ks[-1]


def nb_roll(rng):
    d1 = rng.randint(1, 6)
    d2 = rng.randint(1, 6)
    if d1 % 2 == 1 and not (d1 == 1 and d2 == 1):
        return 1
    return 2


def nb_enc(lets, n_tok, w, tab, seed=0):
    rng = random.Random(seed)
    tok = []
    tru = []
    i = 0
    while i < len(lets) and len(tok) < n_tok:
        n = nb_roll(rng)
        if i + n > len(lets):
            n = 1
        if n == 1:
            a = lets[i]
            i += 1
            tru.append(a)
            tb = nb_pick(rng, w)
            tok.append(tab[tb][a]["u"])
        else:
            a, b = lets[i], lets[i + 1]
            i += 2
            tru.append(a + b)
            tb1 = nb_pick(rng, w)
            tb2 = nb_pick(rng, w)
            tok.append(tab[tb1][a]["p"] + tab[tb2][b]["s"])
    return tok, tru


def join_best(rows):
    return "".join(r["txt"] for r in rows)

def join_det(lines, det, n_lines=N_LINES):
    out = []
    for ln in lines[:n_lines]:
        for w in ln:
            x = det(w)
            if x:
                out.append(x)
    return "".join(out)


def main():
    src, lines, fols, secs = parse_vms()
    print(f"VMS src={src} lines={len(lines)} toks={sum(len(x) for x in lines)}")

    w, tab = nb_load()
    ab = "".join(sorted(next(iter(tab.values())).keys()))
    u, p, s = nb_inv(tab)
    dec = mk_dec(u, p, s)
    det = mk_det(u, p, s)
    print(f"Naibbe ab={ab} u={len(u)} p={len(p)} s={len(s)}")

    lm_la = LM(ab)
    lm_it = LM(ab)
    lm_la.add("".join(let_txt(LAT, set(ab))))
    lm_it.add("".join(let_txt(ITA, set(ab))))

    def show(tag, xs, cov):
        if not xs:
            print(f"{tag}: no decoded output")
            return
        s = sum_score(xs)
        cand = [r for r in xs if r["n"] >= MIN_BEST]
        best = max(cand or xs, key=lambda r: r["spc"])
        print(f"{tag}: logp/char={s['spc']:.4f} n={s['n']} cov={dict(cov)}")
        print(f"{tag}: best_line spc={best['spc']:.4f} fol={best['fol']} sec={best['sec']} txt={best['txt'][:120]}")

        top = sorted((r for r in xs if r["n"] >= MIN_BEST), key=lambda r: r["spc"], reverse=True)[:TOP]
        if top:
            print(f"{tag}: top")
            for r in top:
                print(f"  spc={r['spc']:.3f} n={r['n']:3d} fol={r['fol']} txt={r['txt'][:80]}")

        by = defaultdict(list)
        for r in xs:
            if r["sec"]:
                by[r["sec"]].append(r)
        if by:
            top = sorted(
                ((k, sum_score(v)["spc"], sum_score(v)["n"]) for k, v in by.items()),
                key=lambda x: x[1],
                reverse=True,
            )
            print(f"{tag}: sec " + " ".join(f"{k}={v:.3f}" for k, v, _ in top))

    la, cov_la = score_lines(lines, dec, lm_la, fols=fols, secs=secs, n_lines=len(lines))
    it, cov_it = score_lines(lines, dec, lm_it, fols=fols, secs=secs, n_lines=len(lines))

    show("latin", la, cov_la)
    show("ital", it, cov_it)

    print("\n-- baselines --")
    lines0 = lines[:N_LINES]
    lens = [len(ln) for ln in lines0]
    la0, _ = score_lines(lines0, dec, lm_la, n_lines=N_LINES)
    it0, _ = score_lines(lines0, dec, lm_it, n_lines=N_LINES)
    s_la = sum_score(la0)
    s_it = sum_score(it0)

    def shape(tok, lens):
        out = []
        i = 0
        for k in lens:
            out.append(tok[i:i + k])
            i += k
        return out

    sh = shuf_keep_shape(lines0, seed=SEED + 1)
    la_sh, _ = score_lines(sh, dec, lm_la, n_lines=N_LINES)
    it_sh, _ = score_lines(sh, dec, lm_it, n_lines=N_LINES)
    print(f"shuf: latin={sum_score(la_sh)['spc']:.4f} ital={sum_score(it_sh)['spc']:.4f}")

    n_tok = sum(lens)
    lets_la = let_txt(LAT, set(ab))
    lets_it = let_txt(ITA, set(ab))
    tok_la, pl_la = nb_enc(lets_la, n_tok, w, tab, seed=SEED + 2)
    tok_it, pl_it = nb_enc(lets_it, n_tok, w, tab, seed=SEED + 3)
    la_c = shape(tok_la, lens)
    it_c = shape(tok_it, lens)
    la_d = join_det(la_c, det, n_lines=N_LINES)
    it_d = join_det(it_c, det, n_lines=N_LINES)
    la_spc, la_n = lm_spc(lm_la, la_d)
    it_spc, it_n = lm_spc(lm_it, it_d)
    print(f"pos: la det_spc={la_spc:.4f} n={la_n}")
    print(f"pos: it det_spc={it_spc:.4f} n={it_n}")

    def pos_stat(tok, tru, lm):
        z = o = m = 0
        hit = 0
        dok = 0
        for tk, tr in zip(tok, tru):
            c = dec(tk)
            if not c:
                z += 1
            elif len(c) == 1:
                o += 1
            else:
                m += 1
            if tr in c:
                hit += 1
            if det(tk) == tr:
                dok += 1
        spc, n = lm_spc(lm, "".join(tru))
        n0 = len(tok)
        print(f"  true_spc={spc:.4f} hit={hit/n0:.3f} det_ok={dok/n0:.3f} cand0={z/n0:.3f} cand1={o/n0:.3f} cand2p={m/n0:.3f}")

    print("pos: la stats")
    pos_stat(tok_la, pl_la, lm_la)
    print("pos: it stats")
    pos_stat(tok_it, pl_it, lm_it)

    k = 10
    la_r = []
    it_r = []
    for i in range(k):
        rt = inv_key(tab, seed=100 + i)
        ru, rp, rs = nb_inv(rt)
        rdec = mk_dec(ru, rp, rs)
        x_la, _ = score_lines(lines, rdec, lm_la, n_lines=N_LINES)
        x_it, _ = score_lines(lines, rdec, lm_it, n_lines=N_LINES)
        la_r.append(sum_score(x_la)["spc"])
        it_r.append(sum_score(x_it)["spc"])
    mu_la = statistics.mean(la_r)
    sd_la = statistics.pstdev(la_r) if len(la_r) > 1 else 0.0
    mu_it = statistics.mean(it_r)
    sd_it = statistics.pstdev(it_r) if len(it_r) > 1 else 0.0
    z_la = ((s_la["spc"] - mu_la) / sd_la) if sd_la else 0.0
    z_it = ((s_it["spc"] - mu_it) / sd_it) if sd_it else 0.0
    print(f"rand: latin mean={mu_la:.4f} sd={sd_la:.4f} z={z_la:.2f}")
    print(f"rand: ital  mean={mu_it:.4f} sd={sd_it:.4f} z={z_it:.2f}")


if __name__ == "__main__":
    main()

