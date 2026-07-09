#!/usr/bin/env python3
"""Breakthrough metric over the WHOLE recent corpus (not the 15-paper toy label set).

This generalizes compute_significance.py + compute_composite.py from the hardcoded
5-positive / 10-negative label set to EVERY recent Alzheimer paper in research/ara-library/
that carries GRO L8 sidecars. It is the "use the phase 2-3 outputs" step: ~60 GRO-extended
recent (2025-2026) papers, each scored on the three breakthrough signals.

For each paper:
  - significance  : from the L8 sidecars (contributions / delta_ledger / sota_anchor),
                    reusing compute_significance.significance() verbatim.
  - uptake / cd   : from the local corpus citation graph (works.json / refs_raw.json),
                    reusing compute_composite.graph_signals_local(), mapped slug -> citekey.
                    Recent papers are mostly graph-empty (too new) -> uptake ~0, which is the
                    whole point: on new papers the citation signal is unavailable, so
                    significance (age-independent, from the typed shape) has to carry it.

Output: corpus_scored.json  — one row per paper, all sub-scores, auditable.
        corpus_scored.md    — human-readable ranking by significance.
"""
import glob
import json
import os

import compute_significance as sig_mod
import compute_composite as comp_mod

HERE = os.path.dirname(os.path.abspath(__file__))
ARALIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"

# L8 files that must exist for a paper to get a real significance score.
L8_REQUIRED = ["contributions.yaml"]  # the core signal; delta/anchor degrade gracefully


def slug_to_citekey(slug):
    """ara-library dir slug -> works.json citekey. 'aks25-...' -> 'Aks25', '20225-...' -> '20225'."""
    head = slug.split("-", 1)[0]
    if head[:1].isdigit():
        return head
    return head[:1].upper() + head[1:]


def anchor_density(gro):
    """Mean neighborhood overlap = how crowded the prior art is (high = incremental/update)."""
    import yaml
    fp = os.path.join(gro, "sota_anchor.yaml")
    if not os.path.exists(fp):
        return {"anchor_mean_overlap": None, "anchor_max_overlap": None, "anchor_n": 0}
    doc = yaml.safe_load(open(fp)) or {}
    neigh = doc.get("neighborhood") or []
    ovs = [n.get("overlap") for n in neigh if isinstance(n.get("overlap"), (int, float))]
    return {"anchor_mean_overlap": round(sum(ovs) / len(ovs), 4) if ovs else None,
            "anchor_max_overlap": round(max(ovs), 4) if ovs else None,
            "anchor_n": len(neigh)}


def graph_for(citekey):
    try:
        if citekey in comp_mod.WORKS:
            return comp_mod.graph_signals_local(citekey), "local_corpus_graph"
    except Exception:
        pass
    return {"year": None, "oa_cited_by": 0, "uptake_in_corpus": 0, "uptake_per_year": 0.0,
            "consolidating_i": 0, "disrupting_j": 0, "cd_index": 0.0}, "absent_from_graph"


def main():
    rows = []
    for gro in sorted(glob.glob(os.path.join(ARALIB, "*", "gro"))):
        slug = os.path.basename(os.path.dirname(gro))
        if not all(os.path.exists(os.path.join(gro, f)) for f in L8_REQUIRED):
            continue
        s = sig_mod.significance(gro)
        citekey = slug_to_citekey(slug)
        graph, gsrc = graph_for(citekey)
        c, d, a = s["contribution"], s["delta"], s["anchor"]
        rows.append({
            "slug": slug, "citekey": citekey,
            "significance": s["significance"],
            "contribution": c["score"], "contrib_peak": c.get("peak"),
            "contrib_wmean": c.get("wmean"), "n_contribs": c.get("n"),
            "n_puffery": c.get("n_puffery"),
            "delta": d["score"], "delta_max": d.get("max"),
            "frac_quant_verified": d.get("frac_quant_verified"), "n_deltas": d.get("n_deltas"),
            "anchor": a["score"], "anchor_provenance": a.get("provenance"),
            **anchor_density(gro),
            "graph_source": gsrc, **graph,
        })

    # z-score significance across the whole corpus so it is comparable to expert judgement later
    sigvals = [r["significance"] for r in rows]
    zs = comp_mod.zscores(sigvals) if sigvals else []
    for r, z in zip(rows, zs):
        r["z_significance"] = round(z, 4)

    out_json = os.path.join(HERE, "corpus_scored.json")
    with open(out_json, "w") as f:
        json.dump(rows, f, indent=2)

    rows_sorted = sorted(rows, key=lambda x: -x["significance"])
    lines = ["# Breakthrough signals over the whole recent corpus\n",
             f"\n{len(rows)} GRO-extended recent papers scored. Ranked by significance (L8, age-independent).\n",
             "\n| # | paper | SIG | contrib | delta | anchor | uptake/yr | cd |",
             "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows_sorted, 1):
        lines.append("| %d | %s | %.3f | %.3f | %.3f | %.3f | %.2f | %.2f |" % (
            i, r["slug"][:48], r["significance"], r["contribution"], r["delta"],
            r["anchor"], r["uptake_per_year"], r["cd_index"]))
    with open(os.path.join(HERE, "corpus_scored.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"scored {len(rows)} recent papers -> {out_json}")
    print(f"significance range: {min(sigvals):.3f} .. {max(sigvals):.3f}   mean {sum(sigvals)/len(sigvals):.3f}")
    print("\ntop 8 by significance:")
    for r in rows_sorted[:8]:
        print("  %.3f  %s" % (r["significance"], r["slug"][:60]))
    print("\nbottom 5 by significance:")
    for r in rows_sorted[-5:]:
        print("  %.3f  %s" % (r["significance"], r["slug"][:60]))
    return rows


if __name__ == "__main__":
    main()
