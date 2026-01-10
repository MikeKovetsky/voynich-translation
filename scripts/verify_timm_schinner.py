import json
import math
import os
import random
import re
from collections import Counter
import statistics
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
try:
    from data.sections import get_section_for_folio
except Exception:
    get_section_for_folio = None

# --- Configuration ---
INPUT_FILE = 'data/transliteration/RF1b-e.txt'
# Fallback if the above doesn't exist, check data/RF1b-e.txt
INPUT_FILE_ALT = 'data/RF1b-e.txt'
WINDOW_SIZE = 10  # Look back 10 words for self-citation
MAX_N = 10000
CTRL_DIR = 'data/ctrl'
NB_FILE = 'data/nb.json'
SEED = 0
SIM_S = 20
SIM_N = 2000
KS = [1, 2, 3, 5, 10]

# --- Levenshtein Distance ---
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# --- Parsing ---
def _read_lines(path):
    cands = [path]
    if path.startswith('data/transliteration'):
        cands.append(INPUT_FILE_ALT)
    for p in cands:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                return p, f.readlines()
        except FileNotFoundError:
            continue
    msg = f"Error: Could not find input file at {path}"
    if path.startswith('data/transliteration'):
        msg += f" or {INPUT_FILE_ALT}"
    print(msg)
    sys.exit(1)

def _clean_tok(w: str) -> str:
    w = re.sub(r'\{[^}]+\}', '', w)
    w = re.sub(r'@[0-9]+;?', '', w)
    w = w.strip(" ,-'?!*;")
    return w

def _tok_line(s: str) -> list[str]:
    s = s.replace('<->', ' ')
    parts = re.split(r'[.\s]+', s)
    out = []
    for p in parts:
        w = _clean_tok(p)
        if w:
            out.append(w)
    return out

def parse_ivtff_lines(path):
    src, raw = _read_lines(path)
    print(f"Reading from {src}...")
    out = []
    for line in raw:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('<'):
            if '>' not in line:
                continue
            content = line.split('>', 1)[-1].strip()
        else:
            content = line
        if content.startswith('<!'):
            continue
        toks = _tok_line(content)
        if toks:
            out.append(toks)
    return out

def parse_ivtff(path):
    lines = parse_ivtff_lines(path)
    return [w for ln in lines for w in ln]

def parse_vms(path):
    src, raw = _read_lines(path)
    print(f"Reading from {src}...")
    lines = []
    fols = []
    secs = []
    fid = None
    for line in raw:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('<'):
            if '>' not in line:
                continue
            tag, rest = line[1:].split('>', 1)
            m = re.match(r'(f\d+[rv])', tag)
            if m:
                fid = m.group(1)
            content = rest.strip()
        else:
            content = line

        if content.startswith('<!'):
            continue
        toks = _tok_line(content)
        if not toks:
            continue

        lines.append(toks)
        fols.append(fid)
        if fid and get_section_for_folio:
            m2 = re.match(r'f(\d+)', fid)
            secs.append(get_section_for_folio(int(m2.group(1))) if m2 else None)
        else:
            secs.append(None)

    return lines, fols, secs

# --- Control corpora (plain text) ---
def _strip_gut(lines):
    a = 0
    b = len(lines)
    for i, ln in enumerate(lines):
        if '*** start of' in ln.lower():
            a = i + 1
            break
    for i in range(len(lines) - 1, -1, -1):
        if '*** end of' in lines[i].lower():
            b = i
            break
    return lines[a:b]

def _norm_txt(s: str) -> str:
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def tok_txt(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    lines = _strip_gut(lines)
    s = _norm_txt(''.join(lines))
    return re.findall(r"[a-z]+(?:'[a-z]+)?", s)

def shape_lines(toks, lens):
    out = []
    i = 0
    for k in lens:
        if i + k > len(toks):
            break
        out.append(toks[i:i + k])
        i += k
    return out

def nb_load(path=NB_FILE):
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    return d["w"], d["t"]

def nb_pick(rng, w):
    keys = list(w.keys())
    tot = sum(w.values())
    x = rng.randrange(tot)
    s = 0
    for k in keys:
        s += w[k]
        if x < s:
            return k
    return keys[-1]

def nb_let(path, ab):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    lines = _strip_gut(lines)
    s = _norm_txt(''.join(lines))
    s = s.translate(str.maketrans({'j': 'i', 'k': 'c', 'w': 'v'}))
    out = []
    for c in s:
        if 'a' <= c <= 'z':
            L = c.upper()
            if L in ab:
                out.append(L)
    return out

def nb_roll(rng):
    d1 = rng.randint(1, 6)
    d2 = rng.randint(1, 6)
    if d1 % 2 == 1 and not (d1 == 1 and d2 == 1):
        return 1
    return 2

def nb_enc(path, lens, seed=SEED):
    if not os.path.isfile(NB_FILE):
        return []
    w, t = nb_load()
    ab = set(t["alpha"].keys())
    need = sum(lens)

    letters = nb_let(path, ab)
    letters = letters[:need * 2] if len(letters) > need * 2 else letters

    rng = random.Random(seed)
    out = []
    i = 0
    while i < len(letters) and len(out) < need:
        n = nb_roll(rng)
        if i + n > len(letters):
            n = 1

        if n == 1:
            a = letters[i]
            i += 1
            tb = nb_pick(rng, w)
            out.append(t[tb][a]["u"])
        else:
            a, b = letters[i], letters[i + 1]
            i += 2
            tb1 = nb_pick(rng, w)
            tb2 = nb_pick(rng, w)
            out.append(t[tb1][a]["p"] + t[tb2][b]["s"])

    return shape_lines(out, lens)

# --- Analysis ---
def calculate_zipf_slope(tokens):
    counts = Counter(tokens)
    freqs = sorted(counts.values(), reverse=True)
    
    X = []
    Y = []
    for rank, freq in enumerate(freqs, 1):
        if freq > 0:
            X.append(math.log(rank))
            Y.append(math.log(freq))
        
    if len(X) < 2: return 0, [], []
    
    # Linear regression
    n = len(X)
    sum_x = sum(X)
    sum_y = sum(Y)
    sum_xy = sum(x*y for x,y in zip(X,Y))
    sum_xx = sum(x*x for x in X)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
    return slope, X, Y

def calculate_autocopying_metric(tokens, window=WINDOW_SIZE, limit=5000):
    """
    For each token, calculate the minimum Levenshtein distance 
    to any token in the previous 'window' tokens.
    Returns the average of these minimum distances.
    """
    if len(tokens) <= window:
        return 0
        
    min_distances = []
    
    # Analyze up to 'limit' tokens to save time, but start after the window
    end_index = min(len(tokens), window + limit)
    
    for i in range(window, end_index):
        current_word = tokens[i]
        history = tokens[i-window:i]
        
        # Find min distance to history
        dists = [levenshtein(current_word, h) for h in history]
        if dists:
            min_dist = min(dists)
            min_distances.append(min_dist)
        
    return statistics.mean(min_distances) if min_distances else 0

def _flat(lines):
    toks = []
    idx = []
    for li, ln in enumerate(lines):
        for ti, w in enumerate(ln):
            toks.append(w)
            idx.append((li, ti))
    return toks, idx

def mml_ctx(lines, window=WINDOW_SIZE, n=MAX_N):
    toks, idx = _flat(lines)
    n = min(len(toks), n)

    acc = {"flat": [], "line": [], "prev": []}
    for i in range(n):
        li, ti = idx[i]
        w = toks[i]

        if i >= window:
            prev = toks[i - window:i]
            acc["flat"].append(min(levenshtein(w, x) for x in prev))

        if ti > 0:
            a = max(0, ti - window)
            prev = lines[li][a:ti]
            if prev:
                acc["line"].append(min(levenshtein(w, x) for x in prev))

        if li > 0:
            prev_ln = lines[li - 1]
            if prev_ln:
                prev = prev_ln[-window:]
                acc["prev"].append(min(levenshtein(w, x) for x in prev))

    res = {}
    for k, v in acc.items():
        res[k] = (statistics.mean(v) if v else 0, len(v))
    return res, n

def _shuf_lines(lines, rng=None):
    if rng is None:
        rng = random
    out = []
    for ln in lines:
        a = ln.copy()
        rng.shuffle(a)
        out.append(a)
    return out

def _shuf_keep_shape(lines, rng=None):
    if rng is None:
        rng = random
    toks = [w for ln in lines for w in ln]
    rng.shuffle(toks)
    out = []
    i = 0
    for ln in lines:
        k = len(ln)
        out.append(toks[i:i + k])
        i += k
    return out

def _shuf_line_order(lines, rng=None):
    if rng is None:
        rng = random
    out = lines.copy()
    rng.shuffle(out)
    return out

def shuf_in_grp(lines, gids, rng=None):
    if rng is None:
        rng = random
    pos = {}
    for i, g in enumerate(gids):
        pos.setdefault(g, []).append(i)
    out = list(lines)
    for g, idxs in pos.items():
        blk = [lines[i] for i in idxs]
        rng.shuffle(blk)
        for i, ln in zip(idxs, blk):
            out[i] = ln
    return out

def _lcp(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

def _lcs(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[-1 - i] == b[-1 - i]:
        i += 1
    return i

def _op(a, b):
    if a == b:
        return "same"

    if a in b or b in a:
        if len(a) <= len(b):
            s, l = a, b
        else:
            s, l = b, a
        if l.startswith(s):
            return "suf_add"
        if l.endswith(s):
            return "pre_add"
        return "both_add"

    if len(a) == len(b):
        p = _lcp(a, b)
        s = _lcs(a, b)
        if p + s == len(a) - 1:
            if p == 0:
                return "pre_sub"
            if s == 0:
                return "suf_sub"
            return "mid_sub"

    return "other"

def _best(prev, w):
    best_w = None
    best_d = 10**9
    for x in prev:
        d = levenshtein(w, x)
        if d < best_d:
            best_d = d
            best_w = x
            if best_d == 0:
                break
    return best_w, best_d

def ops_flat(tokens, window=WINDOW_SIZE, limit=MAX_N):
    cnt = Counter()
    dist = Counter()
    end = min(len(tokens), window + limit)
    for i in range(window, end):
        w = tokens[i]
        prev = tokens[i - window:i]
        bw, bd = _best(prev, w)
        if bw is None:
            continue
        cnt[_op(bw, w)] += 1
        dist[bd] += 1
    return cnt, dist

def ops_line(lines, window=WINDOW_SIZE, limit=MAX_N):
    cnt_start = Counter()
    dist_start = Counter()
    cnt_in = Counter()
    dist_in = Counter()

    seen = 0
    for li, ln in enumerate(lines):
        if not ln:
            continue

        if li > 0 and lines[li - 1]:
            w0 = ln[0]
            prev = lines[li - 1][-window:]
            bw, bd = _best(prev, w0)
            if bw is not None:
                cnt_start[_op(bw, w0)] += 1
                dist_start[bd] += 1

        for ti in range(1, len(ln)):
            w = ln[ti]
            a = max(0, ti - window)
            prev = ln[a:ti]
            bw, bd = _best(prev, w)
            if bw is not None:
                cnt_in[_op(bw, w)] += 1
                dist_in[bd] += 1

            seen += 1
            if seen >= limit:
                return (cnt_start, dist_start), (cnt_in, dist_in)

    return (cnt_start, dist_start), (cnt_in, dist_in)

def ops_sum(cnt, dist):
    tot = sum(cnt.values())
    if tot == 0:
        return {"n": 0}
    out = {"n": tot}
    out["d0"] = dist.get(0, 0) / tot
    out["d1"] = dist.get(1, 0) / tot
    out["d2"] = dist.get(2, 0) / tot
    for k in ("pre_add", "suf_add", "both_add", "pre_sub", "suf_sub", "mid_sub", "same", "other"):
        out[k] = cnt.get(k, 0) / tot
    return out

def lev_n(a, b):
    d = levenshtein(a, b)
    m = max(len(a), len(b))
    return d / m if m else 0.0

def curve_k(lines, w=WINDOW_SIZE, n=MAX_N, norm=False):
    toks, idx = _flat(lines)
    n = min(len(toks), n)
    dist = lev_n if norm else levenshtein

    acc = {"line": {k: [] for k in range(1, w + 1)}, "prev": {k: [] for k in range(1, w + 1)}}
    for i in range(n):
        li, ti = idx[i]
        w0 = toks[i]

        if ti > 0:
            prev = lines[li][max(0, ti - w):ti]
            m = len(prev)
            if m:
                ds = [dist(w0, x) for x in prev]
                mn = None
                for k in range(1, m + 1):
                    mn = ds[-k] if mn is None else min(mn, ds[-k])
                    acc["line"][k].append(mn)

        if li > 0 and lines[li - 1]:
            prev = lines[li - 1][-w:]
            m = len(prev)
            if m:
                ds = [dist(w0, x) for x in prev]
                mn = None
                for k in range(1, m + 1):
                    mn = ds[-k] if mn is None else min(mn, ds[-k])
                    acc["prev"][k].append(mn)

    res = {"line": {}, "prev": {}}
    for side in ("line", "prev"):
        for k in range(1, w + 1):
            v = acc[side][k]
            res[side][k] = (statistics.mean(v) if v else 0, len(v))
    return res

def mml_sum(lines, limit=MAX_N):
    toks = [w for ln in lines for w in ln]
    flat = calculate_autocopying_metric(toks, window=WINDOW_SIZE, limit=limit)
    mm, _ = mml_ctx(lines, window=WINDOW_SIZE, n=WINDOW_SIZE + limit)
    return {"flat": flat, "line": mm["line"][0], "prev": mm["prev"][0]}

def cmp_lines(lines, limit=MAX_N, seed=SEED):
    a = mml_sum(lines, limit=limit)
    ks = mml_sum(_shuf_keep_shape(lines, rng=random.Random(seed + 1)), limit=limit)
    wl = mml_sum(_shuf_lines(lines, rng=random.Random(seed + 2)), limit=limit)
    lo = mml_sum(_shuf_line_order(lines, rng=random.Random(seed + 3)), limit=limit)
    return {"actual": a, "keep_shape": ks, "within_line": wl, "line_order": lo}

def mean_sd(xs):
    if not xs:
        return 0.0, 0.0
    if len(xs) == 1:
        return float(xs[0]), 0.0
    return statistics.mean(xs), statistics.stdev(xs)

def main():
    print("Parsing text...")
    lines, fols, secs = parse_vms(INPUT_FILE)
    tokens = [w for ln in lines for w in ln]
    print(f"Total tokens found: {len(tokens)}")
    print(f"Unique tokens: {len(set(tokens))}")
    print(f"Total lines: {len(lines)}")
    lens = [len(ln) for ln in lines]
    
    # 1. Zipf Analysis
    print("\n--- Zipf's Law Analysis ---")
    slope, log_ranks, log_freqs = calculate_zipf_slope(tokens)
    print(f"Zipf Slope: {slope:.4f}")
    print("(Natural languages typically have a slope around -1.0)")
    
    # Simple ASCII plot for top 10 frequencies
    print("\nTop 10 Most Frequent Words:")
    counts = Counter(tokens)
    for w, c in counts.most_common(10):
        print(f"  {w:10}: {c}")

    # 2. Autocopying Analysis
    print(f"\n--- Autocopying/Self-Citation Analysis (Window={WINDOW_SIZE}) ---")
    limit = MAX_N
    actual_metric = calculate_autocopying_metric(tokens, window=WINDOW_SIZE, limit=limit)

    shuffled_tokens = tokens.copy()
    random.Random(SEED + 10).shuffle(shuffled_tokens)
    control_metric = calculate_autocopying_metric(shuffled_tokens, window=WINDOW_SIZE, limit=limit)

    diff = control_metric - actual_metric
    print(f"Flat window MMLD (actual) : {actual_metric:.4f}")
    print(f"Flat window MMLD (shuffle): {control_metric:.4f}")
    print(f"Difference               : {diff:.4f}")

    m, n = mml_ctx(lines, window=WINDOW_SIZE, n=WINDOW_SIZE + limit)
    print("\nLine-aware MMLD (actual):")
    print(f"  flat: {m['flat'][0]:.4f} (n={m['flat'][1]})")
    print(f"  line: {m['line'][0]:.4f} (n={m['line'][1]})")
    print(f"  prev: {m['prev'][0]:.4f} (n={m['prev'][1]})")

    def show_mml(name, lines2):
        t2 = [w for ln in lines2 for w in ln]
        flat = calculate_autocopying_metric(t2, window=WINDOW_SIZE, limit=limit)
        mm, _ = mml_ctx(lines2, window=WINDOW_SIZE, n=WINDOW_SIZE + limit)
        print(f"{name:12} flat={flat:.4f} line={mm['line'][0]:.4f} prev={mm['prev'][0]:.4f}")
        return flat, mm

    print("\n--- Null models (same line shape) ---")
    show_mml("keep_shape", _shuf_keep_shape(lines, rng=random.Random(SEED + 1)))
    show_mml("within_line", _shuf_lines(lines, rng=random.Random(SEED + 2)))
    show_mml("line_order", _shuf_line_order(lines, rng=random.Random(SEED + 3)))

    print("\n--- Nearest-neighbor ops (actual) ---")
    def show_ops(name, cnt, dist):
        tot = sum(cnt.values())
        if tot == 0:
            print(f"{name}: n=0")
            return
        top = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
        parts = " ".join(f"{k}={v/tot:.2f}" for k, v in top)
        d0 = dist.get(0, 0) / tot
        d1 = dist.get(1, 0) / tot
        d2 = dist.get(2, 0) / tot
        print(f"{name:10} n={tot} d0={d0:.2f} d1={d1:.2f} d2={d2:.2f} {parts}")

    c_flat, d_flat = ops_flat(tokens, window=WINDOW_SIZE, limit=limit)
    (c_start, d_start), (c_in, d_in) = ops_line(lines, window=WINDOW_SIZE, limit=limit)
    show_ops("flat", c_flat, d_flat)
    show_ops("line_start", c_start, d_start)
    show_ops("in_line", c_in, d_in)
    
    # Interpretation
    print("\n--- Conclusion ---")
    if abs(slope + 1.0) < 0.2:
        print(f"[+] Zipf's Law: The slope {slope:.2f} is close to -1.0, consistent with natural language (or a good mimic).")
    else:
        print(f"[-] Zipf's Law: The slope {slope:.2f} deviates from -1.0.")

    if diff > 0.5:
        print(f"[+] Self-Citation: The text is significantly more similar to neighbors than random ({diff:.2f} difference).")
        print("    This SUPPORTS the Timm & Schinner hypothesis.")
    else:
        print(f"[-] Self-Citation: No strong local similarity found ({diff:.2f} difference).")
        print("    This WEAKENS the Timm & Schinner hypothesis (or requires different parameters).")

    if m["line"][1] and m["prev"][1]:
        d = m["prev"][0] - m["line"][0]
        if d > 0:
            print(f"[+] Line-locality: Same-line is closer than cross-line by {d:.2f} MMLD.")
        else:
            print(f"[-] Line-locality: No same-line advantage ({abs(d):.2f} MMLD).")

    # --- Controls ---
    try:
        files = []
        if os.path.isdir(CTRL_DIR):
            for fn in sorted(os.listdir(CTRL_DIR)):
                if fn.endswith('.txt'):
                    files.append(os.path.join(CTRL_DIR, fn))
    except Exception:
        files = []

    if files:
        corps = [("VMS", lines)]
        f_map = []
        for p in files:
            toks = tok_txt(p)
            cl = shape_lines(toks, lens)
            if not cl:
                continue
            name = os.path.basename(p).replace('.txt', '')
            corps.append((name, cl))
            f_map.append((name, p))

        if os.path.isfile(NB_FILE):
            for name, p in f_map:
                if not (name.startswith('la_') or name.startswith('it_')):
                    continue
                nb = nb_enc(p, lens, seed=SEED + 123)
                if nb:
                    corps.append((f"nb_{name}", nb))
        sim_corps = [(n, c) for n, c in corps if not n.startswith('nb_')]

        print("\n--- Controls (same line-length shape as VMS) ---")
        v = cmp_lines(lines, limit=limit, seed=SEED)
        print(f"VMS         prev(actual)={v['actual']['prev']:.4f} prev(line_order)={v['line_order']['prev']:.4f} Δ={v['line_order']['prev']-v['actual']['prev']:.4f}")
        for name, cl in corps[1:]:
            c = cmp_lines(cl, limit=limit, seed=SEED)
            dp = c['line_order']['prev'] - c['actual']['prev']
            print(f"{name:11} prev(actual)={c['actual']['prev']:.4f} prev(line_order)={c['line_order']['prev']:.4f} Δ={dp:.4f}")

        print("\n--- k-curves (min distance to last k tokens) ---")
        cv = curve_k(lines, w=WINDOW_SIZE, n=WINDOW_SIZE + limit, norm=True)
        def show_curve(tag, cvv):
            a = " ".join(f"k{k}={cvv['prev'][k][0]:.3f}" for k in KS)
            b = " ".join(f"k{k}={cvv['line'][k][0]:.3f}" for k in KS)
            print(f"{tag:11} prev {a}")
            print(f"{'':11} line {b}")

        for name, cl in corps:
            cc = curve_k(cl, w=WINDOW_SIZE, n=WINDOW_SIZE + limit, norm=True)
            show_curve(name, cc)

        print("\n--- ops by position (actual; fractions) ---")
        def show_ops_pos(name, cl):
            (cs, ds), (ci, di) = ops_line(cl, window=WINDOW_SIZE, limit=SIM_N)
            ss = ops_sum(cs, ds)
            si = ops_sum(ci, di)
            if ss.get("n", 0) == 0 or si.get("n", 0) == 0:
                return
            print(
                f"{name:11} start n={ss['n']} d1={ss['d1']:.2f} pre_add={ss['pre_add']:.2f} suf_add={ss['suf_add']:.2f} pre_sub={ss['pre_sub']:.2f} other={ss['other']:.2f}"
            )
            print(
                f"{'':11} inln  n={si['n']} d1={si['d1']:.2f} pre_add={si['pre_add']:.2f} suf_add={si['suf_add']:.2f} pre_sub={si['pre_sub']:.2f} other={si['other']:.2f}"
            )

        for name, cl in corps:
            show_ops_pos(name, cl)

        print(f"\n--- sims (seeds={SIM_S}, n={SIM_N}, norm) ---")
        def sim_corp(name, cl):
            act = mml_sum(cl, limit=SIM_N)["prev"]
            cv_act = curve_k(cl, w=WINDOW_SIZE, n=WINDOW_SIZE + SIM_N, norm=True)
            act_k10 = cv_act["prev"][10][0]

            lo = []
            for i in range(SIM_S):
                rng = random.Random(1000 + i)
                x = _shuf_line_order(cl, rng=rng)
                lo.append(mml_sum(x, limit=SIM_N)["prev"] - act)
            lo_mu, lo_sd = mean_sd(lo)
            lo_eff = (lo_mu / lo_sd) if lo_sd else 0.0

            def sim_curve(model, base):
                vals = {k: [] for k in KS}
                for i in range(SIM_S):
                    rng = random.Random(base + i)
                    x = model(cl, rng=rng)
                    cv = curve_k(x, w=WINDOW_SIZE, n=WINDOW_SIZE + SIM_N, norm=True)
                    for k in KS:
                        vals[k].append(cv["prev"][k][0])
                mu = {k: statistics.mean(vals[k]) for k in KS}
                sd10 = statistics.stdev(vals[10]) if len(vals[10]) > 1 else 0.0
                z10 = ((mu[10] - act_k10) / sd10) if sd10 else 0.0
                return mu, sd10, z10

            ks_mu, ks_sd10, ks_z10 = sim_curve(_shuf_keep_shape, 2000)
            wl_mu, wl_sd10, wl_z10 = sim_curve(_shuf_lines, 3000)

            print(f"{name:11} Δprev(line_order)={lo_mu:.4f}±{lo_sd:.4f} eff={lo_eff:.2f}  k10(prev)={act_k10:.3f}")
            print(f"{'':11} keep_shape prev " + " ".join(f"k{k}={ks_mu[k]:.3f}" for k in KS) + f"  z10={ks_z10:.2f}")
            print(f"{'':11} within_line prev " + " ".join(f"k{k}={wl_mu[k]:.3f}" for k in KS) + f"  z10={wl_z10:.2f}")

        for name, cl in sim_corps:
            sim_corp(name, cl)

        print("\n--- VMS group shuffles (Δprev) ---")
        def sim_grp(tag, gids, base):
            act = mml_sum(lines, limit=SIM_N)["prev"]
            ds = []
            for i in range(SIM_S):
                rng = random.Random(base + i)
                x = shuf_in_grp(lines, gids, rng=rng)
                ds.append(mml_sum(x, limit=SIM_N)["prev"] - act)
            mu, sd = mean_sd(ds)
            eff = (mu / sd) if sd else 0.0
            print(f"{tag:11} Δprev={mu:.4f}±{sd:.4f} eff={eff:.2f}")

        sim_grp("within_fol", fols, 4000)
        sim_grp("within_sec", secs, 5000)

        print("\n--- VMS start ops under group shuffles ---")
        def sim_start(tag, gids, base):
            vals = []
            for i in range(SIM_S):
                rng = random.Random(base + i)
                x = shuf_in_grp(lines, gids, rng=rng)
                (cs, ds), _ = ops_line(x, window=WINDOW_SIZE, limit=SIM_N)
                s = ops_sum(cs, ds)
                if s.get("n", 0):
                    vals.append(s["pre_add"])
            mu, sd = mean_sd(vals)
            print(f"{tag:11} pre_add(start)={mu:.3f}±{sd:.3f}")

        (cs0, ds0), _ = ops_line(lines, window=WINDOW_SIZE, limit=SIM_N)
        s0 = ops_sum(cs0, ds0)
        print(f"{'actual':11} pre_add(start)={s0.get('pre_add', 0):.3f} n={s0.get('n', 0)}")
        sim_start("within_fol", fols, 6000)
        sim_start("within_sec", secs, 7000)

if __name__ == "__main__":
    main()
