#!/usr/bin/env python3
"""Breakthrough metric — SIGNIFICANCE signal from the GRO L8 sidecars.

This is the THIRD tier-separated signal from shapes/12_breakthrough.md. Unlike the two
graph signals (uptake, disruption) it does NOT touch the citation network; it reads only
the per-ARA L8 sidecars: contributions.yaml, delta_ledger.yaml, sota_anchor.yaml.

WHY THIS SIGNAL EXISTS (the v1 Goodhart hole):
  Graph uptake is recency-confounded: a 2025 "facts and figures" report can rack up a high
  uptake-per-year while contributing nothing new. And an ML paper (aks25) can shout "99.18%
  accuracy" — lots of impressive-looking numbers — yet those numbers are within-paper, never
  differenced against a source-verified prior baseline. Significance is designed to be blind
  to raw quantity-of-numbers and instead reward *verified novelty*:
    (a) contribution TYPE   — new_paradigm / new_method / new_finding > synthesis >
                              incremental_improvement / replication,
    (b) delta LEDGER        — quantified deltas whose baseline is source_verified (not
                              self_reported, not qualitative, not claimed-but-unresolved),
    (c) sota ANCHOR         — a real resolver-produced precedence neighborhood with a second
                              resolver, NOT an empty/compiler_estimated one.
  PENALIZE-DON'T-SKIP: empty / qualitative_only / claimed_unresolved / compiler_estimated /
  puffery (realized_in: []) all score LOW but are still scored, never dropped.

Output: significance in [0,1] per labelled paper, plus the three sub-scores and the raw
counts the score was built from (so the number is auditable, not a black box).
"""
import json
import os
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))

# --- The labelled set: every paper for which GRO L8 sidecars were emitted. -----------------
# All 5 positives now carry a full GRO shape (incl. L8) on disk; paths are as handed to this pass.
POSITIVES = {
    "lecanemab": "/Users/carlaostmann/code/dasmodel/.claude/worktrees/wf_a3176248-fee-1/research/metrics/v5-breakthrough/corpus/labelled/lecanemab/gro",
    "donanemab": "/Users/carlaostmann/code/dasmodel/research/metrics/v5-breakthrough/corpus/labelled/donanemab/gro",
    "ptau217":   "/Users/carlaostmann/code/dasmodel/.claude/worktrees/wf_a3176248-fee-3/research/metrics/v5-breakthrough/corpus/labelled/ptau217/gro",
    "dam_microglia": "/Users/carlaostmann/code/dasmodel/.claude/worktrees/wf_a3176248-fee-4/research/metrics/v5-breakthrough/corpus/labelled/dam_microglia/gro",
    "nia_aa_framework": "/Users/carlaostmann/code/dasmodel/.claude/worktrees/wf_a3176248-fee-5/research/metrics/v5-breakthrough/corpus/labelled/nia_aa_framework/gro",
}
ARALIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"
NEGATIVES = {
    "guo25c": ARALIB + "/guo25c-the-disease-burden-risk-factors-and/gro",
    "hao25":  ARALIB + "/hao25-trend-analysis-and-future-predictions-of/gro",
    "yu25":   ARALIB + "/yu25-global-mortality-prevalence-and-disability-adjusted/gro",
    "ami25":  ARALIB + "/ami25-prevalence-deaths-and-disability-adjusted-life/gro",
    "zhu25b": ARALIB + "/zhu25b-global-burden-of-alzheimer-s-disease/gro",
    "wan25c": ARALIB + "/wan25c-global-burden-of-alzheimer-s-disease/gro",
    "raz25":  ARALIB + "/raz25-advancements-in-deep-learning-for-early/gro",
    "kho25":  ARALIB + "/kho25-explainable-artificial-intelligence-in-neuroimaging-of/gro",
    "ali26":  ARALIB + "/ali26-privacy-preserving-multimodal-fusion-for-alzheimer/gro",
    "aks25":  ARALIB + "/aks25-an-explainable-web-based-diagnostic-system/gro",
}

# --- (a) contribution novelty weights (closed taxonomy from the shape) ---------------------
NOVELTY_W = {
    "new_paradigm": 1.00,
    "new_method": 0.80,
    "new_finding": 0.70,
    "refutation": 0.60,
    "synthesis": 0.35,
    "incremental_improvement": 0.15,
    "replication": 0.10,
}
UNASSESSED_W = 0.10  # missing/unknown compiler_assessed_type => treat as low, per shape

# --- (b) delta-ledger status weights -------------------------------------------------------
def delta_weight(status, verification):
    if status == "quantified":
        return 1.0 if verification == "source_verified" else 0.5  # self_reported = weaker
    if status == "qualitative_only":
        return 0.15
    if status == "claimed_unresolved":
        return 0.05   # frames an advance it cannot verify -> penalize
    if status == "not_claimed":
        return 0.10   # non-comparative; neutral-low
    return 0.05


def load(path, fname):
    fp = os.path.join(path, fname)
    if not os.path.exists(fp):
        return None
    with open(fp) as f:
        return yaml.safe_load(f)


def is_real_number(x):
    if isinstance(x, (int, float)):
        return True
    if isinstance(x, str):
        try:
            float(x)
            return True
        except ValueError:
            return False
    return False


def contribution_score(path):
    doc = load(path, "contributions.yaml") or {}
    contribs = doc.get("contributions") or []
    scored = []            # (weight, confidence) after anti-puffery adjustment
    n_puffery = 0
    n_unadjudicated = 0
    for c in contribs:
        cat = (c.get("compiler_assessed_type") or {})
        primary = cat.get("primary")
        conf = cat.get("confidence")
        conf = float(conf) if is_real_number(conf) else 0.3
        w = NOVELTY_W.get(primary, UNASSESSED_W)
        # ANTI-PUFFERY LOCK: realized_in empty/absent => void this contribution.
        realized = c.get("realized_in") or []
        if not realized:
            n_puffery += 1
            w = 0.0
        # conflicting typing divergence with no adjudication => unresolved, penalize.
        div = c.get("typing_divergence")
        adj = c.get("adjudication")
        if div == "conflicting" and (adj in (None, "not_triggered")):
            n_unadjudicated += 1
            w *= 0.5
        scored.append((w, conf))
    if not scored:
        return {"score": 0.0, "peak": 0.0, "wmean": 0.0, "n": 0,
                "n_puffery": n_puffery, "n_unadjudicated": n_unadjudicated}
    # peak: best confidence-weighted novelty (a breakthrough needs >=1 strong contribution)
    peak = max(w * conf for w, conf in scored)
    # wmean: confidence-weighted mean novelty (penalizes padding with incremental claims)
    tot = sum(conf for _, conf in scored) or 1.0
    wmean = sum(w * conf for w, conf in scored) / tot
    score = 0.6 * peak + 0.4 * wmean
    return {"score": round(score, 4), "peak": round(peak, 4), "wmean": round(wmean, 4),
            "n": len(scored), "n_puffery": n_puffery, "n_unadjudicated": n_unadjudicated}


def delta_score(path):
    doc = load(path, "delta_ledger.yaml") or {}
    deltas = doc.get("deltas") or []
    weights = []
    n_quant_verified = 0
    counts = {}
    for d in deltas:
        st = d.get("delta_status")
        ver = d.get("baseline_verification")
        counts[st] = counts.get(st, 0) + 1
        weights.append(delta_weight(st, ver))
        if st == "quantified" and ver == "source_verified":
            n_quant_verified += 1
    if not weights:
        return {"score": 0.0, "max": 0.0, "frac_quant_verified": 0.0,
                "n_deltas": 0, "n_quant_verified": 0, "status_counts": {}}
    mx = max(weights)
    frac = n_quant_verified / len(weights)
    score = 0.7 * mx + 0.3 * frac
    return {"score": round(score, 4), "max": round(mx, 4), "frac_quant_verified": round(frac, 4),
            "n_deltas": len(weights), "n_quant_verified": n_quant_verified,
            "status_counts": counts}


def anchor_score(path):
    doc = load(path, "sota_anchor.yaml") or {}
    neigh = doc.get("neighborhood") or []
    provenance = doc.get("provenance")
    second = doc.get("overlap_jaccard_second_resolver")
    second_real = is_real_number(second)
    # A sota_anchor is defined by the shape as resolver-produced (NOT compiler-written).
    # compiler_estimated => not a real precedence neighborhood -> penalize regardless of size.
    if provenance == "compiler_estimated":
        score = 0.20
        reason = "compiler_estimated (not resolver-produced) -> penalized"
    elif not neigh:
        score = 0.05
        reason = "empty neighborhood -> penalize ambiguity (resolver-limited, not first-in-field)"
    else:
        score = 0.60 + 0.40 * (1.0 if second_real else 0.0)
        reason = ("real neighborhood + second resolver" if second_real
                  else "real neighborhood, single resolver")
    return {"score": round(score, 4), "n_neighbors": len(neigh),
            "provenance": provenance or "unspecified",
            "second_resolver": second if second_real else None, "reason": reason}


def significance(path):
    c = contribution_score(path)
    d = delta_score(path)
    a = anchor_score(path)
    # Contributions and deltas are the core of significance; the anchor is corroboration.
    sig = 0.40 * c["score"] + 0.40 * d["score"] + 0.20 * a["score"]
    return {
        "significance": round(sig, 4),
        "contribution": c,
        "delta": d,
        "anchor": a,
    }


def main():
    rows = []
    for label, mapping in (("POSITIVE", POSITIVES), ("NEGATIVE", NEGATIVES)):
        for name, path in mapping.items():
            exists = os.path.isdir(path)
            rec = {"name": name, "label": label, "gro_dir": path, "gro_present": exists}
            if exists:
                rec.update(significance(path))
            else:
                rec.update({"significance": 0.0, "contribution": {}, "delta": {}, "anchor": {},
                            "note": "GRO dir missing -> significance 0 (penalize, don't skip)"})
            rows.append(rec)

    out = os.path.join(HERE, "significance_results.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=2)

    def mean(label):
        v = [r["significance"] for r in rows if r["label"] == label]
        return round(sum(v) / len(v), 4) if v else 0.0

    print("=== SIGNIFICANCE (GRO L8) over the labelled set ===")
    hdr = "%-9s %-17s %6s | %6s %6s %6s" % ("LABEL", "name", "SIG", "contrib", "delta", "anchor")
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(rows, key=lambda x: (x["label"], -x["significance"])):
        print("%-9s %-17s %6.3f | %6.3f %6.3f %6.3f" % (
            r["label"], r["name"], r["significance"],
            r.get("contribution", {}).get("score", 0.0),
            r.get("delta", {}).get("score", 0.0),
            r.get("anchor", {}).get("score", 0.0)))
    print("\n--- mean significance ---")
    print("  POSITIVE = %s   NEGATIVE = %s" % (mean("POSITIVE"), mean("NEGATIVE")))
    print("\nwrote", out)
    return rows


if __name__ == "__main__":
    main()
