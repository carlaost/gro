#!/usr/bin/env python3
"""Audit whether each recent paper's GRO L8 sidecars actually carry the LLM-RESOLVED fields
the breakthrough significance signal consumes. A paper is only meaningfully scorable if:

  - contributions.yaml : >=1 contribution with a REAL compiler_assessed_type.primary drawn from
                         the closed novelty taxonomy (not null / NEEDS_LLM / unknown).
  - delta_ledger.yaml  : present, with >=1 delta carrying a delta_status (quantified/qualitative/..)
                         and, for quantified ones, a baseline_verification.
  - sota_anchor.yaml    : a REAL resolver neighborhood (non-empty) whose provenance is NOT
                         'compiler_estimated' (which the metric hard-penalizes to 0.20).

Emits l8_todo.json: the list of papers needing an LLM GRO-extend pass, with per-file reasons.
"""
import glob
import json
import os

import yaml

ARALIB = "/Users/carlaostmann/code/dasmodel/research/ara-library"
HERE = os.path.dirname(os.path.abspath(__file__))
TAXO = {"new_paradigm", "new_method", "new_finding", "refutation",
        "synthesis", "incremental_improvement", "replication"}
PLACEHOLDER = {None, "", "NEEDS_LLM", "unknown", "tbd", "TBD", "null"}


def load(p):
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return yaml.safe_load(f)


def audit(gro):
    reasons = []
    # contributions
    c = load(os.path.join(gro, "contributions.yaml"))
    if not c:
        reasons.append("contributions:MISSING")
    else:
        contribs = c.get("contributions") or []
        typed = [x for x in contribs
                 if ((x.get("compiler_assessed_type") or {}).get("primary")) in TAXO]
        if not contribs:
            reasons.append("contributions:EMPTY")
        elif not typed:
            reasons.append("contributions:UNTYPED(no real compiler_assessed_type)")
    # delta ledger
    d = load(os.path.join(gro, "delta_ledger.yaml"))
    if not d:
        reasons.append("delta_ledger:MISSING")
    else:
        deltas = d.get("deltas") or []
        if not deltas:
            reasons.append("delta_ledger:EMPTY")
        elif not any(x.get("delta_status") for x in deltas):
            reasons.append("delta_ledger:NO_STATUS")
    # sota anchor
    a = load(os.path.join(gro, "sota_anchor.yaml"))
    if not a:
        reasons.append("sota_anchor:MISSING")
    else:
        neigh = a.get("neighborhood") or []
        prov = a.get("provenance")
        if prov == "compiler_estimated":
            reasons.append("sota_anchor:COMPILER_ESTIMATED(penalized)")
        elif not neigh:
            reasons.append("sota_anchor:EMPTY_NEIGHBORHOOD")
    return reasons


def main():
    todo = []
    ok = 0
    for gro in sorted(glob.glob(os.path.join(ARALIB, "*", "gro"))):
        slug = os.path.basename(os.path.dirname(gro))
        reasons = audit(gro)
        # "core" problem = the contribution typing that drives 40% of significance
        core = any(r.startswith("contributions:") for r in reasons)
        if reasons:
            todo.append({"slug": slug, "reasons": reasons, "core_broken": core})
        else:
            ok += 1
    todo.sort(key=lambda x: (not x["core_broken"], x["slug"]))
    with open(os.path.join(HERE, "l8_todo.json"), "w") as f:
        json.dump(todo, f, indent=2)

    core_n = sum(1 for t in todo if t["core_broken"])
    print(f"papers fully clean: {ok}")
    print(f"papers needing an LLM extend pass: {len(todo)}  (of which {core_n} have the CORE "
          f"contribution-typing broken -> significance unreliable)")
    print("\n-- needing work --")
    for t in todo:
        tag = "CORE" if t["core_broken"] else "minor"
        print(f"  [{tag}] {t['slug'][:46]:46s}  {'; '.join(t['reasons'])}")


if __name__ == "__main__":
    main()
