#!/usr/bin/env python3
"""
V3 detectors — RC3 (genuine dead-ends), RC4 (evidence-addressing corrective), RC5 (semantic negatives).

Implements the rules in research/metrics/v3/plan.md ("Module A — detectors.py (RC3, RC4, RC5)")
against the compiler model in research/metrics/v3/compiler-model.md: the ARA schema demands an
exploration trace and a typed related-work graph even for genres (systematic reviews, meta-analyses,
guidelines) that structurally have no first-person exploration process. Where the schema outruns the
source, the compiler fills the gap by manufacturing content (dead-ends that are just a negated
headline conclusion; "bounds" edges that are baseline-relabeling, not refutation). These detectors
strip that fabrication before counting, per the operational rule "never rank a paper on a layer the
compiler fabricated."

Shared input `ctx` (built by the spine's build_context; treat as read-only) provides:
  ctx["slug"]              str
  ctx["genre"]             fine genre (e.g. "systematic_review_meta_analysis")
  ctx["coarse"]            "SYNTHESIS" | "PRIMARY_CLINICAL" | "PRIMARY_LAB"
  ctx["claims"]            list of dicts: {id, status, statement, has_falsification, proof_ids, dep_ids,
                                           statement_nums, grounded_nums, n_source_quotes}
  ctx["claims_md"]         raw logic/claims.md text
  ctx["headline_claims"]   list of statement strings whose status == "supported"
  ctx["tree_nodes"]        list of raw exploration_tree nodes; a dead_end node typically has keys
                           type, hypothesis, failure_mode, lesson, source_refs, support_level
  ctx["related_work_md"]   raw logic/related_work.md
  ctx["rw_blocks"]         list of {id, type, delta, claims_affected, doi, body}
  ctx["ncts"]              list of NCT ids

Return schema (frozen):
  dead_end_density(ctx)      -> {"value": float|"N/A", "validity": <lattice>, "n_genuine": int,
                                 "n_synthetic": int, "source_binding_ratio": float|None, "detail": str}
  corrective_science(ctx)    -> {"value": float, "validity": <lattice>, "n_corrective_edges": int, "detail": str}
  negative_result_share(ctx) -> {"value": float, "validity": <lattice>, "n_negative": int, "detail": str}

Validity lattice: "validated" | "source_bound" | "artifact_bound" | "invalid_fabricated" | "pending_sem" | "pending".
- source_bound  = the value is bound to real author-documented content (a genuine dead-end / evidence-
                  addressing edge / semantic null found in the paper's own claims).
- invalid_fabricated = every contributing signal was a compiler fabrication (e.g. all dead-ends synthetic,
                  source_binding_ratio == 0).
- pending_sem  = a deterministic regex approximation stands in for a real [sem] pass.

See research/metrics/v3/plan.md (RC3/RC4/RC5) for the exact rules to implement.
"""
from __future__ import annotations
import re

# ============================ RC3: genuine dead-ends ============================
# Refs that point to the paper's *conclusion-reporting* apparatus (a results table, an outcome
# summary, the abstract, or the discussion/conclusion narrative) rather than to a specific
# methods/analysis location where an attempt was actually made and failed. A dead-end whose ONLY
# source_refs are of this shape is presumed to be the compiler negating a supported conclusion into
# a straw "abandoned hypothesis" (che26 N11/N12: source_refs = Table 2 / §4.1, hypothesis = a flip of
# the paper's own obsolescence conclusion).
_EXCLUDE_REF_RE = re.compile(r"(Table|Outcome|Abstract|§?\s*[34]\.|Results|Discussion|Conclusion)", re.I)

_STOPWORDS = {
    "this", "that", "with", "from", "were", "have", "has", "had", "its", "than", "then",
    "into", "over", "under", "not", "but", "all", "any", "each", "both", "more", "most",
    "some", "such", "only", "also", "been", "being", "could", "would", "might", "should",
    "will", "shall", "does", "did", "doing", "done", "here", "there", "when", "which",
    "while", "these", "those", "about", "across", "against", "between", "given", "based",
    "used", "using", "however", "remain", "remained", "still",
}


def _tokset(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower())
            if len(w) >= 4 and w not in _STOPWORDS}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _mirrors_headline(hypothesis: str, headline_claims: list[str], threshold: float = 0.22) -> tuple[bool, float]:
    """Does a dead-end's `hypothesis` read as a negation/mirror of an already-supported headline
    claim? An empty hypothesis cannot mirror anything (some genuine dead-ends only carry a
    `description`, e.g. jes26 N11/N12) -> not a mirror."""
    h_tok = _tokset(hypothesis)
    if not h_tok:
        return False, 0.0
    best = 0.0
    for stmt in headline_claims:
        j = _jaccard(h_tok, _tokset(stmt))
        best = max(best, j)
    return best >= threshold, round(best, 3)


def _classify_dead_end(node: dict, ctx: dict) -> tuple[bool, list[str], list[str]]:
    """Returns (genuine, reasons_if_synthetic, kept_refs). ALL of 1-3 must hold, else synthetic;
    rule 4 (SYNTHESIS genre) demands a strictly stronger bar even when 1-3 nominally pass, because
    review/meta-analysis/guideline genres structurally lack a first-person exploration process."""
    reasons = []

    support_ok = node.get("support_level") == "explicit"
    if not support_ok:
        reasons.append(f"support_level={node.get('support_level')!r} (need explicit)")

    refs = node.get("source_refs") or []
    kept_refs = [r for r in refs if not _EXCLUDE_REF_RE.search(str(r))]
    refs_ok = len(kept_refs) > 0
    if not refs_ok:
        reasons.append("source_refs only point to Table/Outcome/Abstract/§3-4/Results/Discussion/"
                        "Conclusion (conclusion-reporting apparatus, not a documented attempt)")

    hypothesis = str(node.get("hypothesis") or "")
    mirrors, jac = _mirrors_headline(hypothesis, ctx.get("headline_claims") or [])
    hyp_ok = not mirrors
    if mirrors:
        reasons.append(f"hypothesis mirrors/negates a supported headline claim (jaccard={jac})")

    genuine = support_ok and refs_ok and hyp_ok

    if ctx.get("coarse") == "SYNTHESIS":
        # Reviews/meta-analyses/guidelines have no first-person exploration process; default to
        # synthetic unless 1-3 STRONGLY hold, i.e. more than a single, borderline surviving ref.
        strong = genuine and len(kept_refs) >= 2
        if genuine and not strong:
            reasons.append("SYNTHESIS genre: only a single surviving non-generic ref — not a strong "
                            "enough binding for a genre with no native exploration process")
        genuine = strong

    return genuine, reasons, kept_refs


def _genuine_dead_end_nodes(ctx: dict) -> list[dict]:
    return [n for n in ctx["tree_nodes"]
            if n.get("type") == "dead_end" and _classify_dead_end(n, ctx)[0]]


def dead_end_density(ctx):
    claims = ctx["claims"]
    n_claims = len(claims)
    dead_nodes = [n for n in ctx["tree_nodes"] if n.get("type") == "dead_end"]

    if not dead_nodes:
        return {"value": round(0.0, 4) if n_claims else "N/A", "validity": "source_bound",
                "n_genuine": 0, "n_synthetic": 0, "source_binding_ratio": None,
                "detail": "no dead_end nodes in exploration_tree — nothing to fabricate or bind"}

    genuine_ids, synthetic_ids, detail_lines = [], [], []
    for n in dead_nodes:
        ok, reasons, _kept = _classify_dead_end(n, ctx)
        nid = n.get("id", "?")
        if ok:
            genuine_ids.append(nid)
            detail_lines.append(f"{nid}: genuine")
        else:
            synthetic_ids.append(nid)
            detail_lines.append(f"{nid}: synthetic ({'; '.join(reasons)})")

    n_genuine, n_synthetic = len(genuine_ids), len(synthetic_ids)
    total = n_genuine + n_synthetic
    ratio = round(n_genuine / total, 4) if total else None
    value = round(n_genuine / n_claims, 4) if n_claims else "N/A"
    validity = "source_bound" if n_genuine > 0 else "invalid_fabricated"

    return {"value": value, "validity": validity, "n_genuine": n_genuine, "n_synthetic": n_synthetic,
            "source_binding_ratio": ratio, "detail": "; ".join(detail_lines)}


# ============================ RC4: evidence-addressing corrective edges ============================
# Contrastive language an edge's Delta must contain to count as actually addressing the prior work's
# evidence (as opposed to just relabeling "we beat the prior standard", which is a baseline, not a
# refutation/bound).
_CORRECTIVE_RE = re.compile(
    r"(contradict|fails to replicate|overturn|did not hold|lower than reported|"
    r"not reproducible|refut|revises? down)",
    re.I,
)
_BASELINE_DELTA_RE = re.compile(r"prior standard we improve on", re.I)


def corrective_science(ctx):
    edges = ctx.get("rw_blocks") or []
    qualifying = []
    for e in edges:
        typ = (e.get("type") or "")
        delta = (e.get("delta") or "")
        claims_affected = e.get("claims_affected") or []

        is_bounds_or_refutes = ("refutes" in typ) or ("bounds" in typ)
        if not is_bounds_or_refutes:
            continue
        if "baseline" in typ or _BASELINE_DELTA_RE.search(delta):
            continue  # baseline-naming scores 0
        if not claims_affected:
            continue
        if not _CORRECTIVE_RE.search(delta):
            continue

        weight = 2.0 if "refutes" in typ else 1.0  # refutes > bounds
        qualifying.append((e.get("id", "?"), typ, weight))

    n_edges = len(qualifying)
    value = round(float(sum(w for _, _, w in qualifying)), 4)
    validity = "source_bound" if n_edges > 0 else "invalid_fabricated"
    if qualifying:
        detail = (f"{n_edges}/{len(edges)} rw_blocks are evidence-addressing: "
                  + ", ".join(f"{i}[{t}](w={w})" for i, t, w in qualifying))
    else:
        n_bounds_refutes = sum(1 for e in edges if "refutes" in (e.get("type") or "")
                               or "bounds" in (e.get("type") or ""))
        detail = (f"0/{len(edges)} rw_blocks qualify ({n_bounds_refutes} typed refutes/bounds present "
                  "but baseline-relabeling / no contrastive Delta language / no claims_affected)")

    return {"value": value, "validity": validity, "n_corrective_edges": n_edges, "detail": detail}


# ============================ RC5: semantic negative-result detection ============================
_NEG_RE = re.compile(
    r"(no significant difference|did not (?:\w+\s+){0,2}differ|was not (?:\w+\s+){0,2}associated|"
    r"failed to|no correlation|does not correlate|do not correlate|not superior|did not improve|"
    r"no benefit|non-?significant|cohen'?s d\s*<\s*0\.2|auc\s*(?:=|of)?\s*0\.5\d*|CI[^.]*cross)",
    re.I,
)


def _linked_claim_ids(node: dict) -> set[str]:
    ev = node.get("evidence")
    if isinstance(ev, list):
        return set(re.findall(r"C\d+", " ".join(str(x) for x in ev)))
    if isinstance(ev, str):
        return set(re.findall(r"C\d+", ev))
    return set()


def negative_result_share(ctx):
    claims = ctx["claims"]
    n_claims = len(claims)
    if not n_claims:
        return {"value": "N/A", "validity": "pending_sem", "n_negative": 0, "detail": "no claims"}

    neg_ids, detail_lines = set(), []
    for c in claims:
        if c["status"] == "refuted":
            neg_ids.add(c["id"])
            detail_lines.append(f"{c['id']} (status=refuted)")
        elif _NEG_RE.search(c.get("statement") or ""):
            neg_ids.add(c["id"])
            detail_lines.append(f"{c['id']} (semantic null despite status={c['status']!r})")

    # Genuine dead-ends (RC3) add negative knowledge NOT already captured by a claim above — a
    # dead-end whose evidence links to a claim id already in neg_ids does not add a second unit.
    extra = 0
    covered = set(neg_ids)
    for n in _genuine_dead_end_nodes(ctx):
        linked = _linked_claim_ids(n)
        if linked & covered:
            continue
        covered |= linked
        extra += 1
        detail_lines.append(f"{n.get('id', '?')} (genuine dead-end, RC3, not claim-duplicated)")

    n_negative = len(neg_ids) + extra
    value = round(n_negative / n_claims, 4)
    detail = "; ".join(detail_lines) if detail_lines else "no semantic nulls, refuted claims, or genuine dead-ends found"

    return {"value": value, "validity": "pending_sem", "n_negative": n_negative, "detail": detail}
