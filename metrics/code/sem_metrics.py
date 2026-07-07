#!/usr/bin/env python3
"""
V3 [sem] metrics — the LLM-judge tier the earlier versions left as `pending_model`.

Per the project's own anti-Goodhart principle (metrics-directions.md; observation O03 / the ARA
paper's N13 finding that LLM judges inflate grades): the LLM's job is to emit a FROZEN, per-item
FINDINGS list; the NUMBER here is computed DETERMINISTICALLY from those findings — this module never
asserts a holistic score itself.

Findings are produced OFFLINE by a judge pass (a different model/session than the compiler) and
frozen to research/metrics/v3/sem_findings/<slug>.yaml:

  claims:                      # one entry per logic/claims.md ## Cxx: block
    - claim_id: "C01"
      evidence_relevance: {relevant: bool, note: str}
      falsifiability: {criteria_present: bool,
                        verdict: "post_hoc_inversion" | "real_precommitted" | "trivial" | "absent",
                        note: str}
      scope_calibration: {verdict: "calibrated" | "over_claim" | "under_claim", note: str}
      novelty: {verdict: "novel" | "incremental" | "restatement", note: str}
  compilation_fidelity_samples:   # PDF-accessible facts sampled and checked against the ARA
    - fact: str
      pdf_location: str
      captured_in_ara: bool
      note: str

If sem_findings/<slug>.yaml is absent (or unreadable / has no `claims`), EVERY metric degrades to
value="pending", validity="pending" (never fabricate a score). When a metric is scored from the real
frozen findings, validity="validated" — the judge findings ARE the [sem] pass; scoring them by simple
deterministic tally avoids the holistic-score self-grading the paper documents (N13). `novel_claim_count`
is the one exception: it stays validity="pending_sem" even with findings present, because it is only a
within-ARA judge approximation of D4's real definition (cross-library FOL-dedup of `Claim.original==true`
against the oshima store), which this corpus doesn't have wired up.

The companion RC7 grounding pass (per-(number,quote) support judgments) is produced by the same judge
step but written to the path grounding.py's semantic_grounding() actually reads:
research/ara-library/<slug>/logic/grounding_findings.yaml (NOT under this directory) — see grounding.py.

`ctx` = the per-ARA context (see detectors.py / compute_metrics_v3.build_context; only ctx["slug"] is
used here). Validity: `validated` when scored from real frozen findings; `pending_sem` when the finding
itself is an approximation (novel_claim_count only); `pending` when no findings file exists.

Return schema (frozen):
  sem_metrics(ctx) -> {"evidence_relevance": {...}, "falsifiability_quality": {...},
                       "scope_calibration": {...}, "novel_claim_count": {...},
                       "compilation_fidelity": {...}}
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path

V3_DIR = Path(__file__).resolve().parent
SEM_FINDINGS_DIR = V3_DIR / "sem_findings"

_PENDING = {"value": "pending", "validity": "pending", "detail": "stub — no sem_findings/<slug>.yaml"}


def _empty_result():
    return {
        "evidence_relevance": dict(_PENDING),
        "falsifiability_quality": dict(_PENDING),
        "scope_calibration": dict(_PENDING),
        "novel_claim_count": dict(_PENDING),
        "compilation_fidelity": dict(_PENDING),
    }


def _load_findings(slug: str):
    path = SEM_FINDINGS_DIR / f"{slug}.yaml"
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


def sem_metrics(ctx):
    slug = ctx["slug"]
    data, path = _load_findings(slug)
    if data is None:
        return _empty_result()

    claims = [c for c in (data.get("claims") or []) if isinstance(c, dict)]
    samples = [s for s in (data.get("compilation_fidelity_samples") or []) if isinstance(s, dict)]
    n = len(claims)
    fname = path.name

    if not n:
        out = _empty_result()
        out["_source"] = fname
        return out

    # ---- evidence_relevance (D1/D2): fraction of claims whose cited evidence actually bears on it ----
    n_relevant = sum(1 for c in claims if bool((c.get("evidence_relevance") or {}).get("relevant")))
    evidence_relevance = {
        "value": round(n_relevant / n, 4),
        "validity": "judge_scored",
        "detail": f"{n_relevant}/{n} claims judged to have cited evidence that substantively bears on "
                  f"the claim (frozen judge findings, {fname}); a judge score is a share of pass/fail "
                  "findings, never an asserted holistic grade.",
    }

    # ---- falsifiability_quality (D2): share of claims with a real, pre-committable criterion ----
    fals_verdicts = Counter((c.get("falsifiability") or {}).get("verdict") or "absent" for c in claims)
    n_real = fals_verdicts.get("real_precommitted", 0)
    falsifiability_quality = {
        "value": round(n_real / n, 4),
        "validity": "judge_scored",
        "verdict_counts": dict(fals_verdicts),
        "detail": f"{n_real}/{n} claims have a falsification criterion judged actionable, non-trivial, "
                  f"and independent of a mechanical negation of the Statement itself; verdict breakdown: "
                  f"{dict(fals_verdicts)} (frozen judge findings, {fname}).",
    }

    # ---- scope_calibration (D3): share of claims whose stated scope matches the evidence ----
    scope_verdicts = Counter((c.get("scope_calibration") or {}).get("verdict") or "unknown" for c in claims)
    n_calibrated = scope_verdicts.get("calibrated", 0)
    n_over = scope_verdicts.get("over_claim", 0)
    scope_calibration = {
        "value": round(n_calibrated / n, 4),
        "validity": "judge_scored",
        "n_over_claim": n_over,
        "verdict_counts": dict(scope_verdicts),
        "detail": f"{n_calibrated}/{n} claims calibrated to what their evidence supports; {n_over} flagged "
                  f"over_claim; verdict breakdown: {dict(scope_verdicts)} (frozen judge findings, {fname}).",
    }

    # ---- novel_claim_count (D4): absolute count of claims judged genuinely novel ----
    # NOTE: D4's real definition is Claim.original==true FOL-deduped against the whole 140-paper oshima
    # store; that infrastructure isn't wired into this corpus. This is a within-ARA judge substitute —
    # stays pending_sem even though the findings are real, per the validity lattice's own definition of
    # "a deterministic tally standing in for a fuller [sem]/graph pass."
    nov_verdicts = Counter((c.get("novelty") or {}).get("verdict") or "unknown" for c in claims)
    n_novel = nov_verdicts.get("novel", 0)
    novel_claim_count = {
        "value": float(n_novel),
        "validity": "pending_sem",
        "verdict_counts": dict(nov_verdicts),
        "detail": f"{n_novel}/{n} claims judged genuinely novel (within-ARA judge approximation only; "
                  "real D4 needs cross-library FOL-dedup of Claim.original against the oshima store, not "
                  f"available on this corpus); verdict breakdown: {dict(nov_verdicts)} (frozen judge "
                  f"findings, {fname}).",
    }

    # ---- compilation_fidelity (D7): sampled PDF-vs-ARA recall ----
    if samples:
        n_captured = sum(1 for s in samples if bool(s.get("captured_in_ara")))
        n_samples = len(samples)
        compilation_fidelity = {
            "value": round(n_captured / n_samples, 4),
            "validity": "judge_scored",
            "n_samples": n_samples,
            "detail": f"{n_captured}/{n_samples} PDF-sampled, checkable facts faithfully captured in the "
                      f"ARA (frozen judge findings, {fname}).",
        }
    else:
        compilation_fidelity = {
            "value": "pending", "validity": "pending",
            "detail": f"{fname} present but carries no compilation_fidelity_samples",
        }

    return {
        "evidence_relevance": evidence_relevance,
        "falsifiability_quality": falsifiability_quality,
        "scope_calibration": scope_calibration,
        "novel_claim_count": novel_claim_count,
        "compilation_fidelity": compilation_fidelity,
    }
