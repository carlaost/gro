#!/usr/bin/env python3
"""
V3 extractive_fidelity — Cycle-2 critique C3 (research/metrics/v3/critiques/cycle2.md): the
compiler-model axiom C16 (research/metrics/v3/compiler-model.md) — "the compiler's extractive
layer (claims, load-bearing numbers) is a faithful re-view of the paper" — was ASSUMED and never
measured against the actual papers. Full text is now on disk for 10/12 ARAs
(research/metrics/v3/fulltext/coverage.md). This module measures it.

`extractive_fidelity(ctx)` does NOT itself judge fidelity. It reads a FROZEN per-ARA finding at
research/metrics/v3/extractive_fidelity/<slug>.yaml and tallies it deterministically — the same
anti-self-grading discipline as sem_metrics.py and grounding.py's semantic_grounding(). The frozen
finding is produced by an independent adversarial pass (a different agent/session than the
compiler that wrote logic/claims.md) that:
  - took every claim in logic/claims.md,
  - extracted its load-bearing numbers and its asserted direction/polarity,
  - checked BOTH against fulltext/<slug>.txt (the extracted full paper text) — NOT against
    metadata.md / the abstract, and NOT by re-trusting the compiler's own quoted «Sources» blindly
    (a compiler could cite a quote that doesn't actually appear in, or doesn't actually support,
    the paper),
  - marked the claim FAITHFUL iff the numbers match AND the direction/polarity matches AND no
    clause in the Statement is an addition unsupported anywhere in the paper text,
  - and for each infidelity, classified it as number_mismatch | polarity_inversion |
    unsupported_addition with the contradicting paper quote attached.

Per-ARA yaml schema (frozen, hand-authored by the adversarial pass; see
research/metrics/v3/extractive_fidelity/*.yaml):
    slug: <slug>
    fulltext_file: research/metrics/v3/fulltext/<slug>.txt
    n_claims_checked: <int>
    n_faithful: <int>
    claims:
      - claim_id: "C01"
        faithful: true|false
        note: str
        infidelity_type: "number_mismatch"|"polarity_inversion"|"unsupported_addition"   # if faithful=false
        paper_quote: str                                                                  # if faithful=false
    infidelities:            # the unfaithful claims only, repeated for easy aggregation
      - claim_id: str
        type: str
        paper_quote: str
        note: str

Return schema (frozen — matches the task spec):
    extractive_fidelity(ctx) -> {"value": float|"unverifiable", "validity": str,
                                 "n_claims_checked": int, "n_faithful": int,
                                 "infidelities": [...], "detail": str}

Validity:
  - "abstract_bound" for the 2 ARAs with no full text on disk (ahm26b, the25 — closed OA, no PMC
    route, no accessible author copy per fulltext/coverage.md). value="unverifiable": an ARA
    compiled from the abstract cannot have its extractive layer checked against a paper that isn't
    available here. This is NOT the same as "faithful" — it is explicitly unknown.
  - "source_bound" when scored against the real full paper text. Deliberately NOT "validated":
    per compiler-model.md's own caveat, "compiler-fidelity and metric-validity are independent
    axes... even a perfectly faithful re-view adds no external ground truth." This module measures
    fidelity TO THE PAPER (the strongest internal grounding tier this corpus offers), not the
    paper's scientific validity — conflating the two is exactly the mistake C16 risked.
  - "pending" if a slug is expected to have a frozen finding (not in ABSTRACT_ONLY) but the file is
    missing/unreadable — degrades gracefully rather than fabricating a score.

ctx: the standard per-ARA context from compute_metrics_v3.build_context(); only ctx["slug"] is used.
"""
from __future__ import annotations
from pathlib import Path

V3_DIR = Path(__file__).resolve().parent
FIDELITY_DIR = V3_DIR / "extractive_fidelity"

# fulltext/coverage.md: these 2 of 12 ARAs have no full text on disk (paywalled, no PMC route, no
# reachable OA/author copy) — their extractive layer is structurally unverifiable against a paper
# that does not exist in this corpus. Mirrors compute_metrics_v3.ABSTRACT_ONLY (kept independent
# per the task's "do not edit other .py modules" constraint, not imported, so this module has no
# hard dependency on the spine).
ABSTRACT_ONLY = {
    "ahm26b-trends-and-disparities-in-alzheimer-disease",
    "the25-blood-phosphorylated-tau-for-the-diagnosis",
}


def _load_finding(slug: str):
    path = FIDELITY_DIR / f"{slug}.yaml"
    if not path.exists():
        return None, path
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None, path
    if not isinstance(data, dict):
        return None, path
    return data, path


def extractive_fidelity(ctx: dict) -> dict:
    slug = ctx["slug"]

    if slug in ABSTRACT_ONLY:
        return {
            "value": "unverifiable",
            "validity": "abstract_bound",
            "n_claims_checked": 0,
            "n_faithful": 0,
            "infidelities": [],
            "detail": (
                f"{slug} has no full text on disk (fulltext/coverage.md: paywalled / no PMC route / "
                "no reachable OA or author copy). Its logic/claims.md was compiled from the abstract "
                "alone, so its load-bearing numbers and claim direction cannot be checked against a "
                "source paper that isn't available here. Per compiler-model.md, an ARA in this state "
                "is unverifiable against the paper — not assumed faithful by default."
            ),
        }

    data, path = _load_finding(slug)
    if data is None:
        return {
            "value": "pending",
            "validity": "pending",
            "n_claims_checked": 0,
            "n_faithful": 0,
            "infidelities": [],
            "detail": (
                f"no frozen extractive_fidelity/{slug}.yaml on disk and {slug} is not in "
                "ABSTRACT_ONLY — an independent adversarial full-text fidelity check has not been "
                "produced for it yet; degrading to pending rather than fabricating a score."
            ),
        }

    claims = [c for c in (data.get("claims") or []) if isinstance(c, dict)]
    header_n = data.get("n_claims_checked")
    header_faithful = data.get("n_faithful")

    # Reconcile from the per-claim list when present (source of truth); fall back to the file's own
    # header counts only if the per-claim list is empty/malformed. Never trust a hand-authored
    # summary count that disagrees with its own itemized list without re-deriving it.
    if claims:
        n = len(claims)
        n_faithful = sum(1 for c in claims if bool(c.get("faithful")))
        infidelities = [
            {
                "claim_id": c.get("claim_id"),
                "type": c.get("infidelity_type") or c.get("type"),
                "paper_quote": c.get("paper_quote"),
                "note": c.get("note"),
            }
            for c in claims if not bool(c.get("faithful"))
        ]
    elif isinstance(header_n, int) and isinstance(header_faithful, int) and header_n > 0:
        n = header_n
        n_faithful = header_faithful
        infidelities = [f for f in (data.get("infidelities") or []) if isinstance(f, dict)]
    else:
        n = 0
        n_faithful = 0
        infidelities = []

    if n <= 0:
        return {
            "value": "pending",
            "validity": "pending",
            "n_claims_checked": 0,
            "n_faithful": 0,
            "infidelities": [],
            "detail": f"extractive_fidelity/{path.name} present but carries no checkable claims",
        }

    value = round(n_faithful / n, 4)
    infid_types = ", ".join(sorted({str(i.get("type")) for i in infidelities})) or "none"

    return {
        "value": value,
        "validity": "source_bound",
        "n_claims_checked": n,
        "n_faithful": n_faithful,
        "infidelities": infidelities,
        "detail": (
            f"{n_faithful}/{n} claims in logic/claims.md judged faithful (load-bearing numbers AND "
            "asserted direction/polarity both match, no unsupported added clauses) against the actual "
            f"full paper text ({data.get('fulltext_file') or f'research/metrics/v3/fulltext/{slug.split(chr(45))[0]}.txt'}), "
            f"per a frozen independent adversarial check (extractive_fidelity/{path.name}) run by a "
            "different pass than the compiler that wrote claims.md. Infidelity types found: "
            f"{infid_types}. source_bound, not validated: this measures fidelity TO THE PAPER, not "
            "the paper's scientific validity (compiler-model.md's independent-axes caveat) — no "
            "paper-ranker should be treated as sound on this axis alone."
        ),
    }
