import math
import re
import unicodedata
from collections import Counter, defaultdict


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


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower()


def let_txt(path, ab):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    s = norm("".join(strip_gut(lines)))
    s = s.translate(str.maketrans({"j": "i", "k": "c", "w": "v"}))
    out = []
    for c in s:
        if "a" <= c <= "z":
            L = c.upper()
            if L in ab:
                out.append(L)
    return "".join(out)


def words_txt(path, min_len=2):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    s = norm("".join(strip_gut(lines)))
    ws = re.findall(r"[a-z]+", s)
    return [w for w in ws if len(w) >= min_len]


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

    def spc(self, txt: str):
        ctx = self.s0
        sc = 0.0
        n = 0
        for ch in txt:
            if ch not in self.ab:
                continue
            d, ctx = self.step(ctx, ch)
            sc += d
            n += 1
        return (sc / n if n else 0.0), n

