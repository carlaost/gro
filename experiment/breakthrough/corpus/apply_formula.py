#!/usr/bin/env python3
"""Apply a tournament-produced breakthrough formula to the corpus and measure its alignment
with the blind expert panel. Closes the loop: design tournament -> concrete formula -> new
Spearman vs expert, compared against the current metric's -0.10.

Usage:
  python3 apply_formula.py "0.5*(r['contrib_peak'] or 0) + 0.3*(1-(r['anchor_mean_overlap'] or 0)) - 0.1*(r['n_puffery'] or 0)"
  python3 apply_formula.py --file formula.txt   [--name my_metric]
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = "/private/tmp/claude-501/-Users-carlaostmann-code-dasmodel/5417ea35-0ea7-4fac-96ea-536bdcb259ba/tasks/wvi1w1ro5.output"


def median(xs):
    xs = sorted(xs); n = len(xs)
    return None if not n else (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2)


def ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i]); r = [0.0] * len(vals); i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    rx, ry = ranks(xs), ranks(ys); n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    sx = math.sqrt(sum((v - mx) ** 2 for v in rx)); sy = math.sqrt(sum((v - my) ** 2 for v in ry))
    return cov / (sx * sy) if sx and sy else 0.0


def load_expert():
    # Stable persisted file first; fall back to the (ephemeral) panel output.
    stable = os.path.join(HERE, "expert_scores.json")
    if os.path.exists(stable):
        return {k: float(v) for k, v in json.load(open(stable)).items()}
    raw = json.load(open(PANEL)); res = raw.get("result", raw)
    if isinstance(res, str):
        res = json.loads(res)
    out = {}
    for row in res["expert"]:
        sc = [v["breakthrough_score"] for v in row.get("votes", []) if "breakthrough_score" in v]
        if sc:
            out[row["slug"]] = median(sc)
    return out


def safe_eval(formula, r):
    # None-safe: expose fields; also expose helpers min/max/abs
    env = {"r": {k: (0 if v is None else v) for k, v in r.items()},
           "min": min, "max": max, "abs": abs}
    try:
        return float(eval(formula, {"__builtins__": {}}, env))
    except Exception as e:
        return None, str(e)


def load_split(which):
    """which in {'train','test','all'}. Returns a slug-set or None for all."""
    sp = os.path.join(HERE, "split.json")
    if which == "all" or not os.path.exists(sp):
        return None
    d = json.load(open(sp))
    return set(d[which])


def main():
    args = sys.argv[1:]
    name = "candidate"
    split = "all"
    if "--name" in args:
        i = args.index("--name"); name = args[i + 1]; del args[i:i + 2]
    if "--split" in args:
        i = args.index("--split"); split = args[i + 1]; del args[i:i + 2]
    if args and args[0] == "--file":
        formula = open(args[1]).read().strip()
    else:
        formula = args[0]

    rows = json.load(open(os.path.join(HERE, "corpus_scored.json")))
    expert = load_expert()
    keep = load_split(split)

    scored = []
    for r in rows:
        val = safe_eval(formula, r)
        if isinstance(val, tuple):
            print("FORMULA ERROR on", r["slug"], ":", val[1]); return
        if r["slug"] in expert and (keep is None or r["slug"] in keep):
            scored.append({"slug": r["slug"], name: round(val, 4),
                           "expert": expert[r["slug"]], "significance": r["significance"]})
    scored.sort(key=lambda x: -x[name])

    new_vals = [s[name] for s in scored]; exp = [s["expert"] for s in scored]
    old_vals = [s["significance"] for s in scored]
    rho_new = spearman(new_vals, exp); rho_old = spearman(old_vals, exp)

    print(f"formula: {formula}")
    print(f"split: {split}\n")
    print(f"n={len(scored)}   Spearman(new vs expert) = {rho_new:.3f}   "
          f"(current significance was {rho_old:.3f})\n")
    print("%-52s %8s %7s" % ("paper", name, "expert"))
    print("-" * 70)
    for s in scored:
        print("%-52s %8.3f %7.1f" % (s["slug"][:52], s[name], s["expert"]))

    with open(os.path.join(HERE, "formula_result.json"), "w") as f:
        json.dump({"formula": formula, "name": name, "n": len(scored),
                   "spearman_new": round(rho_new, 4), "spearman_old": round(rho_old, 4),
                   "rows": scored}, f, indent=2)
    print("\nwrote formula_result.json")


if __name__ == "__main__":
    main()
