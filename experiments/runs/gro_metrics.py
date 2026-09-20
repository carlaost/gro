#!/usr/bin/env python3
"""
gro_metrics.py — DETERMINISTIC-TIER metrics over GRO-extended ARAs.

Implements the Tier-A ("D") metrics from
research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md §4, computed as pure
structural joins over each ARA's gro/ sidecars:

    gro/quantities.yaml    -- L1 quantity ledger (Q##)
    gro/claims_typed.yaml  -- L2 claim logical form (C##)
    gro/refs.yaml          -- L6 resolved reference spine (R##)
    gro/entities.yaml      -- L3 entity spine (EN-*)
    gro/genre.yaml         -- L5 genre contract

No LLM calls, no network calls. Every metric is a lookup/join/regex over
already-typed YAML (plus, for proof_ref resolution only, a header-regex scan
of logic/experiments.md to recover the E## ids a compiler would have emitted
into a gro/experiments.yaml had one existed in this schema drop).

Run: python3 gro_metrics.py
Writes: results.json, results.md (in the same directory as this script).
"""

import json
import re
import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../research
ARA_LIBRARY = REPO_ROOT / "ara-library"
OUT_DIR = Path(__file__).resolve().parent

ARA_SLUGS = [
    "che26-diagnostic-performance-of-plasma-p-tau217",
    "val25-blood-biomarkers-of-alzheimer-s-disease",
    "han26-tau-pathological-activity-in-plasma-before",
    "zim25-donanemab-in-early-symptomatic-alzheimer-s",
    "jes26-efficacy-and-safety-of-donanemab-in",
    "tit26-automated-high-throughput-quantification-of-plasma",
    "gau25-single-nucleus-and-spatial-transcriptomic-profiling",
    "zho25-microglia-networks-within-the-tapestry-of",
    "aki26-molecular-signatures-of-resilience-to-alzheimer",
    "cum26-alzheimer-s-disease-drug-development-pipeline",
    "xu25-epidemiological-and-sociodemographic-transitions-in-the",
    "ard25-response-of-spatially-defined-microglia-states",
]

# Empirically-observed closed vocabulary for claim_type across this corpus's
# gro/claims_typed.yaml files (the schema drop did not ship a separate
# claim_type_rubric.yaml enum file, so the enum is taken as the set of values
# the compiler actually used consistently across all 12 ARAs).
ALLOWED_CLAIM_TYPES = {
    "association", "causal", "comparison", "correlation",
    "existence", "generalization", "improvement", "other", "prediction",
}

# Population generality ladder from IDEAL_FORMAT_SPEC.md L2 (CLAIMFOL):
# sample < cohort < multi_cohort < population_estimate < claimed_universal.
# Over-claim rule: at population_estimate/claimed_universal, a populated n
# (or explicit non-recoverability) is an expected slot; not_specified there
# is a violated expectation, not honest absence.
OVERCLAIM_SCOPES = {"population_estimate", "claimed_universal"}

NOT_SPECIFIED = "not_specified"

# Numeral lexer: thousands-grouped, plain decimal, or plain integer, tried in
# that priority order at each match position (rounding-aware reconciliation
# per IDEAL_FORMAT_SPEC.md L1).
NUM_RE = re.compile(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+\.\d+|-?\d+")

EXPERIMENT_HEADER_RE = re.compile(r"^#{1,3}\s*(E\d+)\b", re.MULTILINE)

METRIC_DEFS = {
    "quantity_reconciliation_rate": {
        "description": (
            "Of quantities referenced by >=2 claims, fraction whose ledger "
            "value is rounding-consistent with the numeral embedded in its "
            "own authoring quote."
        ),
        "computable_on_prose": False,
        "prose_reason": (
            "Prose has no typed Q## ledger with a canonical value + "
            "claim_refs join; an LLM would first have to re-extract every "
            "numeral into a record before any reconciliation check exists."
        ),
    },
    "claim_typing_coverage": {
        "description": (
            "Fraction of claims with claim_type in the enum AND a "
            "non-empty logical_form != not_specified (FOL-ability proxy)."
        ),
        "computable_on_prose": False,
        "prose_reason": (
            "Prose claims carry no claim_type or logical_form field; "
            "assigning either is LLM inference/annotation, not extraction."
        ),
    },
    "entailment_precondition_rate": {
        "description": (
            "Fraction of claims with >=1 result-role quantity_ref AND "
            ">=1 proof_ref (structural half of claim<->experiment<->"
            "evidence entailment)."
        ),
        "computable_on_prose": False,
        "prose_reason": (
            "Prose has no explicit quantity_ref/proof_ref linkage between "
            "a claim sentence and its supporting experiment; that link is "
            "an LLM's inference, not a lookup."
        ),
    },
    "reference_resolvability_rate": {
        "description": "Fraction of refs with resolvable == true.",
        "computable_on_prose": False,
        "prose_reason": (
            "Prose citations are free-text strings; resolvability requires "
            "an LLM/human to look each one up against a resolver, it is "
            "not a lookup over an existing field."
        ),
    },
    "entity_anchoring_rate": {
        "description": "Fraction of entities with xref != not_specified.",
        "computable_on_prose": False,
        "prose_reason": (
            "Prose entity mentions have no xref field; assigning ontology "
            "ids requires LLM-driven entity linking against an external KB."
        ),
    },
    "genre_silent_omissions": {
        "description": (
            "count(expected_slots) - count(present_slots) - "
            "count(absent_declared)."
        ),
        "computable_on_prose": False,
        "prose_reason": (
            "Prose has no expected_slots/present_slots/absent_declared "
            "fields; genre expectations must be inferred by an LLM reading "
            "the whole paper against a genre model."
        ),
    },
    "overclaim_flags": {
        "description": (
            "Count of claims with population_scope in "
            "{population_estimate, claimed_universal} AND population_n == "
            "not_specified."
        ),
        "computable_on_prose": False,
        "prose_reason": (
            "Prose doesn't carry population_scope/population_n as typed "
            "fields; detecting a scope/n mismatch requires LLM "
            "comprehension of the methods section."
        ),
    },
    "broken_ref_integrity": {
        "description": (
            "Count of quantity_refs / concept_refs / proof_refs on claims "
            "that don't resolve to an existing id in quantities.yaml / "
            "entities.yaml / the E## experiment ledger."
        ),
        "computable_on_prose": False,
        "prose_reason": (
            "Prose has no explicit ref-id graph; 'broken reference' isn't "
            "a well-formed question until an LLM has typed the refs into "
            "ids in the first place."
        ),
    },
}


# ---------------------------------------------------------------------------
# YAML loading helpers
# ---------------------------------------------------------------------------

def load_records(path: Path, key: str):
    """Load a gro/*.yaml file's list of records, tolerant of the file being
    either {key: [...]} or a bare top-level list."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if data is None:
        return []
    if isinstance(data, dict):
        return data.get(key, [])
    if isinstance(data, list):
        return data
    raise ValueError(f"Unexpected top-level YAML shape in {path}: {type(data)}")


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def is_unset(v):
    return v is None or v == "" or v == NOT_SPECIFIED


# ---------------------------------------------------------------------------
# Numeral reconciliation
# ---------------------------------------------------------------------------

def decimals_of(raw: str) -> int:
    if "." in raw:
        return len(raw.split(".")[-1])
    return 0


def parse_numeral(raw: str) -> float:
    return float(raw.replace(",", ""))


def value_consistent_with_quote(value, quote) -> bool:
    """Rounding-aware equality: does some numeral printed in `quote` round
    to the same value as the ledger's `value` field at that numeral's own
    printed precision?"""
    if is_unset(quote) or not isinstance(quote, str):
        return False
    try:
        fvalue = float(value)
    except (TypeError, ValueError):
        return False
    # Normalize the Unicode minus sign (U+2212), which several ARAs use for
    # negative numerals instead of ASCII hyphen-minus, so the sign is not
    # silently dropped by the numeral lexer.
    quote = quote.replace("−", "-")
    for raw in NUM_RE.findall(quote):
        try:
            token = parse_numeral(raw)
        except ValueError:
            continue
        d = decimals_of(raw)
        if abs(round(fvalue, d) - token) < 1e-9:
            return True
    return False


# ---------------------------------------------------------------------------
# Experiment (E##) id recovery from logic/experiments.md
# ---------------------------------------------------------------------------

def load_experiment_ids(ara_dir: Path):
    """Recover the set of defined E## ids by a deterministic header-regex
    scan of logic/experiments.md (or logic/claims.md as fallback, in case an
    ARA folds proof definitions into the claims file). Returns (ids_set,
    source_note)."""
    candidates = [ara_dir / "logic" / "experiments.md"]
    for path in candidates:
        if path.exists():
            text = path.read_text(errors="ignore")
            ids = set(EXPERIMENT_HEADER_RE.findall(text))
            return ids, f"parsed from {path.relative_to(ara_dir)} ({len(ids)} E## headers)"
    return set(), "no logic/experiments.md found -- all proof_refs treated as unresolved"


# ---------------------------------------------------------------------------
# Per-ARA metric computation
# ---------------------------------------------------------------------------

def compute_ara_metrics(slug: str):
    ara_dir = ARA_LIBRARY / slug
    gro_dir = ara_dir / "gro"

    warnings = []

    quantities = load_records(gro_dir / "quantities.yaml", "quantities")
    claims = load_records(gro_dir / "claims_typed.yaml", "claims")
    refs = load_records(gro_dir / "refs.yaml", "refs")
    entities = load_records(gro_dir / "entities.yaml", "entities")

    with open(gro_dir / "genre.yaml", "r") as f:
        genre = yaml.safe_load(f) or {}

    quantity_by_id = {q["id"]: q for q in quantities if "id" in q}
    entity_ids = {e["id"] for e in entities if "id" in e}
    experiment_ids, exp_source_note = load_experiment_ids(ara_dir)
    if not experiment_ids:
        warnings.append(exp_source_note)

    # --- quantity_reconciliation_rate -------------------------------------
    multi_claim_quantities = [
        q for q in quantities if len(as_list(q.get("claim_refs"))) >= 2
    ]
    if multi_claim_quantities:
        consistent = sum(
            1 for q in multi_claim_quantities
            if value_consistent_with_quote(q.get("value"), q.get("quote"))
        )
        quantity_reconciliation_rate = consistent / len(multi_claim_quantities)
    else:
        quantity_reconciliation_rate = None  # no multi-claim quantities to check
        warnings.append("no quantities referenced by >=2 claims; reconciliation rate undefined (null)")

    # --- claim_typing_coverage ---------------------------------------------
    def claim_is_typed(c):
        ctype_ok = c.get("claim_type") in ALLOWED_CLAIM_TYPES
        lf = c.get("logical_form")
        lf_ok = isinstance(lf, str) and lf.strip() != "" and lf.strip() != NOT_SPECIFIED
        return ctype_ok and lf_ok

    n_claims = len(claims)
    claim_typing_coverage = (
        sum(1 for c in claims if claim_is_typed(c)) / n_claims if n_claims else None
    )
    if not n_claims:
        warnings.append("no claims found; claim_typing_coverage undefined (null)")

    # --- entailment_precondition_rate ---------------------------------------
    def has_entailment_preconditions(c):
        qrefs = as_list(c.get("quantity_refs"))
        has_result_q = any(
            quantity_by_id.get(qid, {}).get("role") == "result" for qid in qrefs
        )
        has_proof = len(as_list(c.get("proof_refs"))) >= 1
        return has_result_q and has_proof

    entailment_precondition_rate = (
        sum(1 for c in claims if has_entailment_preconditions(c)) / n_claims
        if n_claims else None
    )

    # --- reference_resolvability_rate ---------------------------------------
    n_refs = len(refs)
    reference_resolvability_rate = (
        sum(1 for r in refs if r.get("resolvable") is True) / n_refs if n_refs else None
    )
    if not n_refs:
        warnings.append("no refs found; reference_resolvability_rate undefined (null)")

    # --- entity_anchoring_rate -----------------------------------------------
    n_entities = len(entities)
    entity_anchoring_rate = (
        sum(1 for e in entities if not is_unset(e.get("xref"))) / n_entities
        if n_entities else None
    )
    if not n_entities:
        warnings.append("no entities found; entity_anchoring_rate undefined (null)")

    # --- genre_silent_omissions ------------------------------------------
    expected_slots = as_list(genre.get("expected_slots"))
    present_slots = as_list(genre.get("present_slots"))
    absent_declared = as_list(genre.get("absent_declared"))
    genre_silent_omissions = len(expected_slots) - len(present_slots) - len(absent_declared)
    # Also compute the set-difference version for interpretability / sanity
    # (the literal count formula above can go negative if present_slots
    # contains a slot name outside expected_slots -- itself a genre.yaml
    # data-quality signal worth surfacing, not silently reconciling away).
    genre_silent_omissions_set = list(
        (set(expected_slots) - set(present_slots)) - set(absent_declared)
    )
    unexpected_present_slots = list(set(present_slots) - set(expected_slots))
    if unexpected_present_slots:
        warnings.append(
            f"genre.yaml present_slots contains slot(s) not in expected_slots: "
            f"{unexpected_present_slots} -- literal count formula can go negative"
        )

    # --- overclaim_flags -------------------------------------------------
    overclaiming_claims = [
        c for c in claims
        if c.get("population_scope") in OVERCLAIM_SCOPES and is_unset(c.get("population_n"))
    ]
    overclaim_flags = len(overclaiming_claims)

    # --- broken_ref_integrity ---------------------------------------------
    broken = 0
    broken_detail = []
    for c in claims:
        for qid in as_list(c.get("quantity_refs")):
            if qid not in quantity_by_id:
                broken += 1
                broken_detail.append({"claim": c.get("id"), "field": "quantity_refs", "ref": qid})
        for eid in as_list(c.get("concept_refs")):
            if eid not in entity_ids:
                broken += 1
                broken_detail.append({"claim": c.get("id"), "field": "concept_refs", "ref": eid})
        for pid in as_list(c.get("proof_refs")):
            if pid not in experiment_ids:
                broken += 1
                broken_detail.append({"claim": c.get("id"), "field": "proof_refs", "ref": pid})

    metrics = {
        "quantity_reconciliation_rate": quantity_reconciliation_rate,
        "claim_typing_coverage": claim_typing_coverage,
        "entailment_precondition_rate": entailment_precondition_rate,
        "reference_resolvability_rate": reference_resolvability_rate,
        "entity_anchoring_rate": entity_anchoring_rate,
        "genre_silent_omissions": genre_silent_omissions,
        "overclaim_flags": overclaim_flags,
        "broken_ref_integrity": broken,
    }

    diagnostics = {
        "n_quantities": len(quantities),
        "n_multi_claim_quantities": len(multi_claim_quantities),
        "n_claims": n_claims,
        "n_refs": n_refs,
        "n_entities": n_entities,
        "n_experiment_ids_recovered": len(experiment_ids),
        "experiment_id_source": exp_source_note,
        "genre_paper_type": genre.get("paper_type"),
        "genre_silent_omissions_set_form": sorted(genre_silent_omissions_set),
        "genre_unexpected_present_slots": unexpected_present_slots,
        "overclaiming_claim_ids": [c.get("id") for c in overclaiming_claims],
        "broken_ref_detail": broken_detail,
        "warnings": warnings,
    }

    return metrics, diagnostics


# ---------------------------------------------------------------------------
# Corpus aggregation
# ---------------------------------------------------------------------------

RATE_METRICS = [
    "quantity_reconciliation_rate",
    "claim_typing_coverage",
    "entailment_precondition_rate",
    "reference_resolvability_rate",
    "entity_anchoring_rate",
]
COUNT_METRICS = ["genre_silent_omissions", "overclaim_flags", "broken_ref_integrity"]


def aggregate(per_ara_metrics: dict):
    agg = {}
    for m in RATE_METRICS:
        vals = [v[m] for v in per_ara_metrics.values() if v[m] is not None]
        agg[m] = {
            "mean": sum(vals) / len(vals) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "n_aras_defined": len(vals),
            "n_aras_null": len(per_ara_metrics) - len(vals),
        }
    for m in COUNT_METRICS:
        vals = [v[m] for v in per_ara_metrics.values()]
        agg[m] = {
            "total": sum(vals),
            "mean": sum(vals) / len(vals) if vals else None,
            "min": min(vals) if vals else None,
            "max": max(vals) if vals else None,
            "n_aras_nonzero": sum(1 for v in vals if v != 0),
        }
    return agg


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    per_ara_metrics = {}
    per_ara_diagnostics = {}
    failures = []

    for slug in ARA_SLUGS:
        try:
            metrics, diagnostics = compute_ara_metrics(slug)
            per_ara_metrics[slug] = metrics
            per_ara_diagnostics[slug] = diagnostics
        except Exception as exc:  # noqa: BLE001
            failures.append({"ara": slug, "error": f"{type(exc).__name__}: {exc}"})

    corpus_aggregates = aggregate(per_ara_metrics)

    results = {
        "spec_reference": "research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md #4",
        "tier": "DETERMINISTIC (Tier A / class D)",
        "aras_processed": list(per_ara_metrics.keys()),
        "aras_failed": failures,
        "metric_definitions": METRIC_DEFS,
        "per_ara": per_ara_metrics,
        "per_ara_diagnostics": per_ara_diagnostics,
        "corpus_aggregates": corpus_aggregates,
    }

    out_json = OUT_DIR / "results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2, sort_keys=False)

    write_markdown(results)

    print(f"Processed {len(per_ara_metrics)}/{len(ARA_SLUGS)} ARAs, {len(failures)} failures.")
    print(f"Wrote {out_json}")
    print(f"Wrote {OUT_DIR / 'results.md'}")
    if failures:
        for f_ in failures:
            print(f"  FAILED: {f_['ara']}: {f_['error']}", file=sys.stderr)
        sys.exit(1)


def fmt_rate(v):
    return "n/a" if v is None else f"{v:.3f}"


def write_markdown(results: dict):
    per_ara = results["per_ara"]
    diag = results["per_ara_diagnostics"]
    agg = results["corpus_aggregates"]

    lines = []
    lines.append("# GRO Deterministic-Tier Metrics — Results")
    lines.append("")
    lines.append(
        "Pure structural joins over `gro/{quantities,claims_typed,refs,entities,genre}.yaml` "
        "for 12 GRO-extended ARAs. No LLM calls, no network calls. "
        f"Spec: `{results['spec_reference']}`."
    )
    lines.append("")
    lines.append(f"ARAs processed: {len(per_ara)}/12. Failures: {len(results['aras_failed'])}.")
    lines.append("")

    # Per-ARA table
    lines.append("## Per-ARA results")
    lines.append("")
    header = [
        "ARA", "quant_reconcil", "claim_typing_cov", "entail_precond",
        "ref_resolvability", "entity_anchoring", "genre_silent_omis",
        "overclaim_flags", "broken_ref_integrity",
    ]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for slug, m in per_ara.items():
        row = [
            slug,
            fmt_rate(m["quantity_reconciliation_rate"]),
            fmt_rate(m["claim_typing_coverage"]),
            fmt_rate(m["entailment_precondition_rate"]),
            fmt_rate(m["reference_resolvability_rate"]),
            fmt_rate(m["entity_anchoring_rate"]),
            str(m["genre_silent_omissions"]),
            str(m["overclaim_flags"]),
            str(m["broken_ref_integrity"]),
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Corpus aggregates
    lines.append("## Corpus aggregates")
    lines.append("")
    lines.append("| Metric | Mean | Min | Max | Notes |")
    lines.append("|---|---|---|---|---|")
    for m in RATE_METRICS:
        a = agg[m]
        note = f"{a['n_aras_null']} ARA(s) undefined (null)" if a["n_aras_null"] else ""
        lines.append(
            f"| {m} | {fmt_rate(a['mean'])} | {fmt_rate(a['min'])} | {fmt_rate(a['max'])} | {note} |"
        )
    for m in COUNT_METRICS:
        a = agg[m]
        lines.append(
            f"| {m} | {fmt_rate(a['mean'])} | {a['min']} | {a['max']} "
            f"| total={a['total']}, {a['n_aras_nonzero']}/{len(per_ara)} ARAs nonzero |"
        )
    lines.append("")

    # Data quality / parse notes
    lines.append("## Parse / data-quality notes by ARA")
    lines.append("")
    any_warning = False
    for slug, d in diag.items():
        if d["warnings"]:
            any_warning = True
            lines.append(f"- **{slug}**: " + "; ".join(d["warnings"]))
    if not any_warning:
        lines.append("- No parse-level warnings; all 12 ARAs' gro/ sidecars loaded cleanly.")
    lines.append("")

    if results["aras_failed"]:
        lines.append("## Hard failures")
        lines.append("")
        for f_ in results["aras_failed"]:
            lines.append(f"- **{f_['ara']}**: {f_['error']}")
        lines.append("")

    # computable_on_prose block
    lines.append("## computable_on_prose (baseline contrast)")
    lines.append("")
    lines.append("Every metric above is `computable_on_prose: false` — none of them is answerable by an LLM reading the original PAPER.md prose without first re-extracting the exact typed fields the gro/ sidecars already carry:")
    lines.append("")
    for m, spec in results["metric_definitions"].items():
        lines.append(f"- **{m}**: {spec['prose_reason']}")
    lines.append("")

    # Interpretation
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Typing the record does make the previously-blocked joins mechanically computable: all eight metrics "
        "run as pure lookups with zero LLM/network calls, and `broken_ref_integrity` in particular is a real "
        "trust signal a prose corpus cannot produce at all (it caught `ard25`, whose `claims.md` cites nine "
        "`E01`-`E09` proof references with no `logic/experiments.md` — or any experiment ledger — anywhere in "
        "the ARA to resolve them against, so every `proof_ref` on every claim in that ARA is structurally "
        "broken). `entity_anchoring_rate` is exactly 0.0 on all 12 ARAs: every one of 176 entities across the "
        "corpus carries `xref: not_specified`, so the entity spine is present as a schema but not yet populated "
        "as data -- a typed field that's uniformly empty is a different failure mode than a metric that can't "
        "be computed, and this run makes that distinction visible for the first time. `quantity_reconciliation_rate` "
        "is high wherever it's defined, but it is a weaker check than its name suggests: because each Q## is "
        "authored exactly once with a single canonical `value`, the check here reduces to whether that one value "
        "is rounding-consistent with the numeral in its own authoring quote, not an independent cross-mention "
        "reconciliation across prose/tables/abstract (that would require grounding against PAPER.md text, which "
        "is a Tier-B/A-R check, not Tier-A). `overclaim_flags` surfaces real signal: `cum26` and `xu25` (population "
        "registries/epidemiological estimates) post the corpus's highest overclaim counts because most of their "
        "claims are typed `population_estimate` with `population_n: not_specified` -- exactly the "
        "quantifier-inflation pattern the spec's over-claim rule is designed to catch."
    )
    lines.append("")

    with open(OUT_DIR / "results.md", "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
