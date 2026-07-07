#!/usr/bin/env python3
"""
Good-science metrics — V3.

Answers the round-2 backlog (research/metrics/v2/critiques-round2.md, RC1-RC11) under the
compiler model adopted as ground truth (research/metrics/v3/compiler-model.md):

  - Two output axes, not one score (RC10):
      * paper_rankers   — computed on extractive layers; the ONLY things that rank papers.
      * artifact_trust  — compiler-determined signals reduced to a trust-weight w (geometric mean);
                          w scales an ARA's contribution to library metrics, NEVER its own paper rank.
  - Validity axis parallel to variance (RC1): every ranker carries {variance_verdict, validity_verdict};
    usable = discriminating AND validity in {validated, source_bound}. No bare "discriminating".
  - Three-tier genre + gold labels (RC8) and a K_MIN=3 resolution ladder (RC9): no singleton rankings.
  - Detectors (RC3/4/5), grounding (RC6/7), external validation (RC2) live in SEPARATE MODULES with a
    frozen interface (see below); this spine imports them and degrades gracefully to `pending` stubs
    when a module is absent or a required LLM/MCP call is unavailable.

This file is the SPINE. It owns: corpus, genre, context-building, the validity+variance scaffold,
the K_MIN ladder, routing, the trust-weight, and all writers. It does NOT own the detector/grounding/
external logic — those are plugged in from detectors.py / grounding.py / external.py.

Module interface (frozen — the three module files must match this):

  detectors.py:
    dead_end_density(ctx)        -> {value, validity, n_genuine, n_synthetic, source_binding_ratio, detail}
    corrective_science(ctx)      -> {value, validity, n_corrective_edges, detail}
    negative_result_share(ctx)   -> {value, validity, n_negative, detail}
  grounding.py:
    grounding_trust(ctx)         -> {value, trust_class, self_contained_ratio, coverage, detail}
    semantic_grounding(ctx)      -> {value, validity, detail}
  external.py:
    external_validation(all_ctx) -> {clinicaltrials, retraction, expert, summary}   # corpus-level

`ctx` schema is built by build_context() below. `value` is a float, or the string "N/A"
(not applicable to this genre/artifact) or "pending" (needs an unavailable LLM/MCP pass).
`validity` is one of VALIDITY_LATTICE.

Pure stdlib + PyYAML. Reuses V1 parsers by import. Writes:
  - per ARA:  research/ara-library/<slug>/metrics/v3/metrics.json
  - library:  research/metrics/v3/library_metrics_v3.{json,md}
  - compare:  research/metrics/v3/comparison_v2_v3.md
"""
from __future__ import annotations
import importlib.util, json, math, re, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve()
V3_DIR = HERE.parent                       # research/metrics/v3
METRICS_DIR = V3_DIR.parent                # research/metrics
V2_DIR = METRICS_DIR / "v2"
RESEARCH = METRICS_DIR.parent              # research/
ARA_LIB = RESEARCH / "ara-library"
DATA_LIB = RESEARCH / "data" / "lib"

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v1 = _load(METRICS_DIR / "compute_metrics.py", "v1")


# ============================ corpus (RC / user decision: the 12 scored ARAs) ============================
CORPUS_12 = [
    "ahm26b-trends-and-disparities-in-alzheimer-disease",
    "che26-diagnostic-performance-of-plasma-p-tau217",
    "cum26-alzheimer-s-disease-drug-development-pipeline",
    "huu25-apoe-e4-alzheimer-s-risk-converges",
    "jes26-efficacy-and-safety-of-donanemab-in",
    "kes25-the-alzheimer-s-disease-diagnosis-and",
    "pal25-alzheimer-s-association-clinical-practice-guideline",
    "sal25-trailblazer-alz-4-a-phase-3",
    "sal26-plasma-emtbr-tau243-and-p-tau217",
    "the25-blood-phosphorylated-tau-for-the-diagnosis",
    "tit26-automated-high-throughput-quantification-of-plasma",
    "woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms",
]


# ============================ RC8: three-tier genre + gold labels ============================
# Fine taxonomy (fixed enum) -> coarse evidence class (RC9 rollup).
GENRE_TO_COARSE = {
    "systematic_review_meta_analysis": "SYNTHESIS",
    "narrative_review_survey":         "SYNTHESIS",
    "clinical_practice_guideline":     "SYNTHESIS",
    "randomized_controlled_trial":     "PRIMARY_CLINICAL",
    "diagnostic_accuracy_study":       "PRIMARY_CLINICAL",
    "observational_epidemiology":      "PRIMARY_CLINICAL",
    "primary_experimental":            "PRIMARY_LAB",
}

# Tier A/B/C gold labels for the 12 (spec RC8). Used as the source of truth and the CI assertion.
GENRE_GOLD = {
    "ahm26b-trends-and-disparities-in-alzheimer-disease":                 "observational_epidemiology",
    "che26-diagnostic-performance-of-plasma-p-tau217":                    "systematic_review_meta_analysis",
    "cum26-alzheimer-s-disease-drug-development-pipeline":                "narrative_review_survey",
    "huu25-apoe-e4-alzheimer-s-risk-converges":                          "primary_experimental",
    "jes26-efficacy-and-safety-of-donanemab-in":                         "randomized_controlled_trial",
    "kes25-the-alzheimer-s-disease-diagnosis-and":                       "diagnostic_accuracy_study",
    "pal25-alzheimer-s-association-clinical-practice-guideline":         "clinical_practice_guideline",
    "sal25-trailblazer-alz-4-a-phase-3":                                 "randomized_controlled_trial",
    "sal26-plasma-emtbr-tau243-and-p-tau217":                            "diagnostic_accuracy_study",
    "the25-blood-phosphorylated-tau-for-the-diagnosis":                  "systematic_review_meta_analysis",
    "tit26-automated-high-throughput-quantification-of-plasma":          "diagnostic_accuracy_study",
    "woj25-immunoassay-detection-of-multiphosphorylated-tau-proteoforms": "primary_experimental",
}

# Tier C deterministic rules: word-boundary, over STRUCTURED FIELDS ONLY, synthesis/guideline first
# (so a trial keyword inside a review does not win). Used to populate/audit when no gold label.
GENRE_RULES = [
    ("clinical_practice_guideline",     [r"practice guideline", r"\bguideline\b", r"\brecommendations?\b"]),
    ("systematic_review_meta_analysis", [r"meta-?analysis", r"network meta-?analysis", r"\bnma\b",
                                         r"systematic review", r"prospero"]),
    ("narrative_review_survey",         [r"\bpipeline\b", r"narrative review", r"\bsurvey\b",
                                         r"landscape", r"comprehensive review", r"review of"]),
    ("randomized_controlled_trial",     [r"randomi[sz]ed", r"phase [123]", r"double-?blind",
                                         r"placebo-?controlled", r"trailblazer"]),
    ("diagnostic_accuracy_study",       [r"diagnostic accuracy", r"diagnostic performance", r"\bauc\b",
                                         r"sensitivity and specificity", r"immunoassay", r"quantification"]),
    ("observational_epidemiology",      [r"\bcohort\b", r"prevalence", r"incidence", r"mortality",
                                         r"disparit", r"population-?based", r"attributable fraction"]),
    ("primary_experimental",            [r"single-?cell", r"single-?nucleus", r"snrna", r"scrna",
                                         r"spatial transcriptomic", r"ex vivo", r"in vitro", r"western blot"]),
]


def classify_genre_tierC(base: Path, slug: str) -> str:
    """Deterministic fallback: structured fields only (PAPER.md title/type lines + slug), word-boundary."""
    paper = v1.read(base / "PAPER.md")
    # structured signal only: the title line + any 'type:'/'venue:' frontmatter + the slug, not the full blob
    head = "\n".join(paper.splitlines()[:12])
    typ = " ".join(re.findall(r"(?im)^\s*(?:type|venue|study\s*type|design)\s*[:=]\s*(.+)$", paper))
    text = (head + " " + typ + " " + slug.replace("-", " ")).lower()
    for genre, pats in GENRE_RULES:
        if any(re.search(p, text) for p in pats):
            return genre
    return "primary_experimental"   # neutral default rather than "other"


def genre_for(slug: str, base: Path) -> tuple[str, str]:
    """Tier A (gold) wins; else Tier C deterministic. Returns (fine_genre, source_tier)."""
    if slug in GENRE_GOLD:
        return GENRE_GOLD[slug], "gold"
    return classify_genre_tierC(base, slug), "tierC"


# ============================ parsers the spine adds on top of V1 ============================
def parse_rw_blocks(md: str) -> list[dict]:
    """Full RW blocks with Type / Delta / Claims-affected, for the RC4 corrective detector."""
    out = []
    for rid, body in re.findall(r"(?m)^##\s+(RW\d+):(.*?)(?=(?:\n##\s)|\Z)", md, re.S):
        out.append({
            "id": rid,
            "type": v1._field(body, "Type").lower(),
            "delta": v1._field(body, "Delta"),
            "claims_affected": re.findall(r"C\d+", v1._field(body, "Claims affected")
                                          or v1._field(body, "Claims")),
            "doi": v1._field(body, "DOI").lower(),
            "body": body,
        })
    return out


# ============================ context builder (frozen ctx schema) ============================
def build_context(slug: str) -> dict:
    base = ARA_LIB / slug
    a1 = v1.compute_ara(slug)
    claims = v1.parse_claims(v1.read(base / "logic/claims.md"))
    tree_nodes = v1.parse_tree(v1.read(base / "trace/exploration_tree.yaml"))
    rw_md = v1.read(base / "logic/related_work.md")
    genre, tier = genre_for(slug, base)
    src = v1.load_sources(slug)
    headline = [c["statement"] for c in claims if c["status"] == "supported"]
    return {
        "slug": slug,
        "base": base,
        "genre": genre,
        "genre_source": tier,
        "coarse": GENRE_TO_COARSE.get(genre, "OTHER"),
        "claims": claims,
        "claims_md": v1.read(base / "logic/claims.md"),
        "headline_claims": headline,
        "tree_nodes": tree_nodes,
        "related_work_md": rw_md,
        "rw_blocks": parse_rw_blocks(rw_md),
        "ncts": [n for n in a1["_ncts"] if n],
        "sources": src,
        "has_code": bool(src.get("code")),
        "has_open_data": any((d.get("access") or "").lower() in ("open", "public", "download")
                             for d in (src.get("data") or [])),
        "v1": a1,
    }


# ============================ module loading (graceful) ============================
VALIDITY_LATTICE = {"validated", "source_bound", "artifact_bound", "invalid_fabricated", "pending_sem", "pending"}


def _pending(value="pending", validity="pending", **extra):
    return {"value": value, "validity": validity, **extra}


def _stub_module(name: str, funcs: dict):
    """Return an object exposing `funcs` names, each returning pending — used when the real module
    (detectors/grounding/external) has not been built yet, so the spine still runs end-to-end."""
    class _M:  # noqa
        pass
    m = _M()
    for fn, default in funcs.items():
        setattr(m, fn, default)
    m.__stub__ = True
    return m


def load_module(fname: str, required_funcs: list[str], stub_defaults: dict):
    path = V3_DIR / fname
    if not path.exists():
        print(f"  [spine] {fname} absent -> using pending stub")
        return _stub_module(fname, stub_defaults)
    try:
        mod = _load(path, fname[:-3])
    except Exception as e:  # noqa
        print(f"  [spine] {fname} failed to import ({e}) -> using pending stub")
        return _stub_module(fname, stub_defaults)
    missing = [f for f in required_funcs if not hasattr(mod, f)]
    if missing:
        print(f"  [spine] {fname} missing {missing} -> filling with pending stubs")
        for f in missing:
            setattr(mod, f, stub_defaults[f])
    return mod


DETECTORS = load_module(
    "detectors.py",
    ["dead_end_density", "corrective_science", "negative_result_share"],
    {"dead_end_density": lambda ctx: _pending(n_genuine=0, n_synthetic=0, source_binding_ratio=None, detail="stub"),
     "corrective_science": lambda ctx: _pending(n_corrective_edges=0, detail="stub"),
     "negative_result_share": lambda ctx: _pending(n_negative=0, detail="stub")},
)
GROUNDING = load_module(
    "grounding.py",
    ["grounding_trust", "semantic_grounding"],
    {"grounding_trust": lambda ctx: _pending(trust_class="pending", self_contained_ratio=None, coverage=None, detail="stub"),
     "semantic_grounding": lambda ctx: _pending(detail="stub")},
)
EXTERNAL = load_module(
    "external.py",
    ["external_validation"],
    {"external_validation": lambda all_ctx: {"clinicaltrials": _pending(), "retraction": _pending(),
                                             "expert": _pending(), "summary": "stub"}},
)
SEM = load_module(
    "sem_metrics.py",
    ["sem_metrics"],
    {"sem_metrics": lambda ctx: {k: _pending() for k in
                                 ("evidence_relevance", "falsifiability_quality", "scope_calibration",
                                  "novel_claim_count", "compilation_fidelity")}},
)
LIBGRAPH = load_module(
    "library_graph.py",
    ["library_graph"],
    {"library_graph": lambda all_ctx: {"deterministic": {}, "fol": {"status": "pending"}, "summary": "stub"}},
)
CLAIMGRAPH = load_module(
    "claim_graph.py",
    ["claim_graph"],
    {"claim_graph": lambda all_ctx: {"clusters": [], "corroboration": [], "external_anchors": {},
                                     "summary": "stub"}},
)
EXTFID = load_module(
    "extractive_fidelity.py",
    ["extractive_fidelity"],
    {"extractive_fidelity": lambda ctx: {"value": "pending", "validity": "pending",
                                         "n_claims_checked": 0, "n_faithful": 0, "infidelities": [],
                                         "detail": "stub"}},
)
OUTSWITCH = load_module(
    "outcome_switching.py",
    ["outcome_switching"],
    {"outcome_switching": lambda all_ctx: {"checked": [], "summary": "stub"}},
)

# Cycle-3 C3 / Cycle-4 R3: measured extractive fidelity vs FULL TEXT gates paper-ranking (resolves
# N47/C16 as "gate, don't withdraw"). The gate is SEVERITY-WEIGHTED, not a flat ratio threshold: a
# `polarity_inversion` or `number_mismatch` on any claim is a ranking-flipping error → HARD FAIL, while
# `unsupported_addition` (interpretive clause, numbers correct) is a soft demerit that does NOT exclude.
# (The old flat 0.9 cutoff was arbitrary and got the one case it decided wrong: it admitted jes26 — a
# confirmed conclusion inversion — while excluding che26 — all numbers correct, only added prose.)
FIDELITY_HARD_FAIL_TYPES = {"polarity_inversion", "number_mismatch"}

# Cycle-1 P4: ARAs with no full text (only an abstract) cannot support paper-quality judgments; their
# paper-ranker values are `abstract_bound` (unverifiable against the paper). From fulltext/coverage.md.
ABSTRACT_ONLY = {"ahm26b-trends-and-disparities-in-alzheimer-disease",
                 "the25-blood-phosphorylated-tau-for-the-diagnosis"}


# ============================ per-ARA assembly ============================
# Routing table (RC10). axis decides whether a signal can rank papers or only feeds trust-weight w.
# Cycle-1 P2/P6: the three [sem] fidelity judges are NO LONGER paper-rankers (moved to trust axis).
PAPER_RANKERS = ["corrective_science_score", "negative_result_share", "dead_end_density",
                 "translation_trial_linkage", "semantic_grounding", "novel_claim_count"]
TRUST_SIGNALS = ["grounding_trust", "environment_completeness", "falsifiability_presence",
                 "compiler_fidelity", "falsification_writing_quality"]
TRUST_GATES = ["all_links_resolve", "seal_L1", "no_orphan_experiments", "grounding_layer_present"]


def _num_or_none(x):
    return x if isinstance(x, (int, float)) else None


def _fidelity_hard_fail(extfid: dict) -> bool:
    """R3: an ARA hard-fails the fidelity gate if any claim carries a severe infidelity (a flipped
    conclusion or a wrong number) — regardless of how many claims are otherwise faithful. An
    unsupported_addition (interpretive clause, numbers correct) is a soft demerit, not a hard fail."""
    return any((inf.get("type") in FIDELITY_HARD_FAIL_TYPES)
               for inf in (extfid.get("infidelities") or []))


def compute_ara_v3(ctx: dict) -> dict:
    slug = ctx["slug"]
    a1 = ctx["v1"]
    d1, d6, d7 = a1["D1_reproducibility"], a1["D6_realworld_grounding"], a1["D7_artifact_quality"]

    # ---- detectors (RC3/4/5) ----
    dead = DETECTORS.dead_end_density(ctx)
    corr = DETECTORS.corrective_science(ctx)
    neg = DETECTORS.negative_result_share(ctx)

    # ---- grounding (RC6 trust + RC7 semantic paper-ranker) ----
    gtrust = GROUNDING.grounding_trust(ctx)
    gsem = GROUNDING.semantic_grounding(ctx)

    # ---- [sem] judges (frozen findings -> deterministic scores) ----
    sem = SEM.sem_metrics(ctx)

    # ---- extractive fidelity vs full text (C3): the gate on whether this ARA may be paper-ranked ----
    extfid = EXTFID.extractive_fidelity(ctx)

    # ---- translation linkage: DEMOTED (Cycle-2 C1/P7). This is an unnormalized NCT-mention count that
    # rewards trial name-dropping (cum26=8.0 wins by citing 8 trials its own RC2 harness calls
    # not_applicable). It is `ref_string_bound` (a ref-string exists), NOT source_bound → never usable.
    # Its principled replacement is per-claim trial concordance in claim_graph (promoted at library level).
    trial = {"value": float(d6["n_clinical_trials_linked"]), "validity": "ref_string_bound",
             "detail": {"ncts": ctx["ncts"], "verified": d6["verified_ncts"],
                        "note": "name-drop count; superseded by claim_graph per_claim_trial_concordance"}}

    # ---- paper rankers (only extractive / de-fabricated signals) ----
    # Cycle-1 critique P2/P6: evidence_relevance, scope_calibration, falsifiability_quality were
    # REMOVED from paper_rankers. The judges proved they detect COMPILER infidelity (added/inverted
    # clauses), not paper quality — so ranking papers on them re-imports the woj25 bug. They now feed
    # the trust axis instead (a single compiler_fidelity signal + falsification-writing quality).
    paper_rankers = {
        "corrective_science_score": corr,
        "negative_result_share": neg,
        "dead_end_density": dead,
        "translation_trial_linkage": trial,
        "semantic_grounding": gsem,
        "novel_claim_count": sem["novel_claim_count"],   # pending_sem; compiler-chunking caveat (P-list)
    }

    # ---- artifact-trust axis (RC6/RC10): homogenization + compiler-determined signals ----
    gates = {
        "seal_L1": d7["seal_L1_structural_score"] == 1.0,
        "all_links_resolve": d1["cross_layer_binding_resolvability"] == 1.0,
        "no_orphan_experiments": len(d7["auditor_blindspot_orphan_experiments"]) == 0,
        "grounding_layer_present": (gtrust.get("coverage") or 0) > 0 or _num_or_none(gtrust["value"]) not in (None, 0),
    }
    # Cycle-1 P2-C (stop triple-counting one compiler defect across two axes): fold the three
    # compiler-fidelity judges into ONE compiler_fidelity signal (mean of the numeric ones), so a single
    # compiler error moves the trust weight once, not three times. Falsification-writing quality (P6) is
    # a distinct compiler-prose signal, kept separate.
    _fid = [_num_or_none(sem[k].get("value")) for k in
            ("evidence_relevance", "scope_calibration", "compilation_fidelity")]
    _fid = [x for x in _fid if x is not None]
    compiler_fidelity = round(sum(_fid) / len(_fid), 4) if _fid else None
    trust_components = {
        "grounding_trust": _num_or_none(gtrust["value"]),
        "environment_completeness": d1["environment_completeness"],
        "falsifiability_presence": a1["D2_claim_evidence_integrity"]["falsifiability_presence_proxy"],
        "compiler_fidelity": compiler_fidelity,                    # unified (was compilation_fidelity only)
        "gate_pass_ratio": sum(1 for v in gates.values() if v) / len(gates),
    }
    # Cycle-1 P6 + P8: falsification_writing_quality has κ=−0.031 (chance) between independent raters —
    # noise. Reported for transparency but EXCLUDED from the trust weight `w`.
    falsification_writing_quality = _num_or_none(sem["falsifiability_quality"].get("value"))
    w = trust_weight(trust_components)

    return {
        "slug": slug, "genre": ctx["genre"], "genre_source": ctx["genre_source"], "coarse": ctx["coarse"],
        "n_claims": a1["n_claims"], "n_experiments": a1["n_experiments"],
        "artifact_facts": {"has_code": ctx["has_code"], "has_open_data": ctx["has_open_data"],
                           "n_trials": d6["n_clinical_trials_linked"]},
        "abstract_bound": slug in ABSTRACT_ONLY,   # P4: no full text — paper-quality signals unverifiable
        "extractive_fidelity": extfid,             # C3: measured vs full text
        "fidelity_hard_fail": _fidelity_hard_fail(extfid),   # R3: any polarity_inversion/number_mismatch
        "rank_eligible": (slug not in ABSTRACT_ONLY)
                         and isinstance(extfid.get("value"), (int, float))
                         and not _fidelity_hard_fail(extfid),
        "paper_rankers": paper_rankers,
        "artifact_trust": {"weight_w": w, "components": trust_components, "gates": gates,
                           "falsification_writing_quality_reportonly": falsification_writing_quality,
                           "grounding_detail": gtrust, "low_trust": w is not None and w < 0.5},
    }


def trust_weight(components: dict) -> float | None:
    """Geometric mean of the normalized [0,1] trust components (RC10). None if none are numeric."""
    vals = [v for v in components.values() if isinstance(v, (int, float))]
    vals = [min(max(v, 0.0), 1.0) for v in vals]
    if not vals:
        return None
    # geometric mean; floor zeros to a small epsilon so one missing component doesn't zero the whole weight
    eps = 1e-3
    logs = [math.log(max(v, eps)) for v in vals]
    return round(math.exp(sum(logs) / len(logs)), 3)


# ============================ RC1: variance + validity, RC9: K_MIN ladder ============================
K_MIN = 3


def variance_verdict(vals: list[float]) -> dict:
    if len(vals) < 2:
        return {"n": len(vals), "verdict": "insufficient_data"}
    sd = statistics.pstdev(vals); rng = max(vals) - min(vals)
    verdict = ("non_discriminating" if rng < 1e-6
               else "low_variance" if (sd < 0.05 and rng < 0.2)
               else "discriminating")
    return {"n": len(vals), "mean": round(statistics.mean(vals), 3),
            "stdev": round(sd, 4), "range": round(rng, 3), "verdict": verdict}


def rollup_validity(validities: list[str]) -> str:
    """A ranker's corpus-level validity = the weakest link among ARAs that produced a real value.
    Cycle-1 P1: `judge_scored` (an LLM judge ran, internally consistent) ranks BELOW source_bound and
    is deliberately NOT in the usable set — 'an LLM produced discriminating output' is not validation.
    `validated` is now reserved for a measured association to a science-quality signal external to the
    compiler (expert/retraction/reproduction); nothing earns it yet on this corpus."""
    order = ["invalid_fabricated", "pending", "pending_sem", "judge_scored", "ref_string_bound",
             "artifact_bound", "source_bound", "validated"]
    present = [v for v in validities if v in order]
    if not present:
        return "pending"
    return min(present, key=lambda v: order.index(v))


def diagnose(aras: list[dict]) -> dict:
    """Per paper-ranker: variance_verdict + validity_verdict + usable. No bare 'discriminating' (RC1).
    Cycle-2 C2: abstract_bound ARAs are EXCLUDED from paper-quality diagnosis — their claim-level signals
    are unverifiable against a full paper, so they must not contribute to (or be ranked by) any metric."""
    out = {}
    rankable = [a for a in aras if a.get("rank_eligible")]   # C2 abstract_bound + C3 extractive_fidelity gate
    for k in PAPER_RANKERS:
        vals, valids = [], []
        for a in rankable:
            r = a["paper_rankers"].get(k, {})
            valids.append(r.get("validity", "pending"))
            v = _num_or_none(r.get("value"))
            if v is not None:
                vals.append(v)
        var = variance_verdict(vals)
        validity = rollup_validity(valids)
        usable = (var.get("verdict") == "discriminating") and (validity in ("validated", "source_bound"))
        out[k] = {"variance_verdict": var.get("verdict"), "n": var.get("n"),
                  "mean": var.get("mean"), "stdev": var.get("stdev"), "range": var.get("range"),
                  "validity_verdict": validity, "usable": usable,
                  "n_excluded_not_rank_eligible": len(aras) - len(rankable)}
    return out


def scoped_ranking(aras: list[dict], metric: str) -> dict:
    """RC9 ladder: fine genre if n>=K_MIN -> else coarse if n>=K_MIN -> else bucket_too_small_to_rank.
    Never emits a singleton ranking. Cycle-2 C2: abstract_bound ARAs excluded (unverifiable vs paper).
    Cycle-2 C7: n<K_MIN buckets are NO LONGER emitted as rankings (was pairwise_caveated) — listed as
    too-small only, so an n=2 pair is never presented as a rank."""
    rankable = [a for a in aras if a.get("rank_eligible")]   # C2 abstract_bound + C3 extractive_fidelity gate

    def collect(key):
        buckets = {}
        for a in rankable:
            r = a["paper_rankers"].get(metric, {})
            v = _num_or_none(r.get("value"))
            if v is not None:
                buckets.setdefault(a[key], []).append((a["slug"], v))
        return buckets

    result = {}
    fine = collect("genre")
    coarse = collect("coarse")
    handled = set()
    for g, members in fine.items():
        if len(members) >= K_MIN:
            result[f"fine:{g}"] = {"level": "fine", "ranking": sorted(members, key=lambda t: -t[1])}
            handled |= {s for s, _ in members}
    for cclass, members in coarse.items():
        rest = [(s, v) for s, v in members if s not in handled]
        if len(rest) >= K_MIN:
            result[f"coarse:{cclass}"] = {"level": "coarse_provisional", "ranking": sorted(rest, key=lambda t: -t[1])}
            handled |= {s for s, _ in rest}
    # leftovers: below K_MIN -> NOT ranked (C7), just listed
    leftover = [a["slug"] for a in rankable
                if a["slug"] not in handled
                and _num_or_none(a["paper_rankers"].get(metric, {}).get("value")) is not None]
    if leftover:
        result["unranked"] = {"level": "bucket_too_small_to_rank", "members": leftover}
    return result


# ============================ writers ============================
def write_ara_v3(a: dict):
    d = ARA_LIB / a["slug"] / "metrics" / "v3"
    d.mkdir(parents=True, exist_ok=True)
    (d / "metrics.json").write_text(json.dumps(a, indent=2), encoding="utf-8")


def _claim_level_validation(claimgraph: dict) -> dict:
    """Cycle-2 C1: the honest positive result is claim-level, not paper-level. Count claims whose OWN
    number reproduces a registered clinical-trial primary-outcome value (concordant) — the one
    Goodhart-resistant, externally-anchored 'validated' signal on this corpus. Reported as 'N claims
    validated across M ARAs', NOT as a paper ranking."""
    trials = (claimgraph.get("external_anchors") or {}).get("trials") or []
    concordant = [t for t in trials if str(t.get("label")).lower() == "concordant"]
    discordant = [t for t in trials if str(t.get("label")).lower() == "discordant"]
    aras_val = sorted({t["slug"] for t in concordant})
    return {
        "unit": "claim",
        "n_claims_endpoint_concordant": len(concordant),
        "n_claims_endpoint_discordant": len(discordant),
        "n_claim_trial_pairs_checked": len(trials),
        "aras_with_a_validated_claim": aras_val,
        "concordant_claims": [f"{t['slug'].split('-')[0]}:{t['claim_id']}" for t in concordant],
        "note": "The only external, non-gameable validation on this corpus. Paper-ranker usable count is "
                "separately 0 — no paper-level metric is validated; validation lives at the claim level.",
    }


def _novelty_audit(claimgraph: dict, aras: list[dict]) -> dict:
    """Cycle-3 R4: novelty is an audited SPOTLIGHT, not a corpus metric. Suppress overclaim_risk on
    abstract_bound ARAs (an abstract's 'novel' tags are uncheckable — this removes the ahm26b artifacts),
    and report coverage honestly rather than quoting a corpus rate over a mostly-pending pool."""
    abstract = {a["slug"] for a in aras if a.get("abstract_bound")}
    nov = (claimgraph.get("external_anchors") or {}).get("novelty") or []
    flags = [n for n in nov if n.get("overclaim_risk")]
    verified = [n for n in flags if n.get("slug") not in abstract]
    suppressed = [n for n in flags if n.get("slug") in abstract]
    checked = [n for n in nov if str(n.get("verdict")) not in ("pending", "None", "")]
    return {
        "status": "audited_spotlight_not_corpus_metric",
        "n_headline_claims": len(nov),
        "n_checked": len(checked),
        "n_pending": len(nov) - len(checked),
        "verified_priority_overclaims": [f"{n['slug'].split('-')[0]}:{n.get('claim_id')}" for n in verified],
        "n_verified_priority_overclaims": len(verified),
        "n_suppressed_abstract_bound_artifacts": len(suppressed),
        "note": "Coverage is partial (many claims pending); do NOT read n_verified as a corpus rate. "
                "abstract_bound ARAs' novelty flags are suppressed as uncheckable.",
    }


def write_library(aras: list[dict], ext: dict, libgraph: dict | None = None, claimgraph: dict | None = None,
                  outswitch: dict | None = None):
    V3_DIR.mkdir(exist_ok=True)
    diag = diagnose(aras)
    lib = {
        "n_aras": len(aras),
        "corpus": "12 scored ARAs (v3-spec set)",
        "abstract_bound": sorted(ABSTRACT_ONLY),
        "genres": {a["slug"]: {"fine": a["genre"], "coarse": a["coarse"], "source": a["genre_source"]} for a in aras},
        "diagnostic": diag,
        "scoped_rankings": {m: scoped_ranking(aras, m) for m in PAPER_RANKERS},
        "artifact_trust": {a["slug"]: a["artifact_trust"]["weight_w"] for a in aras},
        "external_validation": ext,
        "library_graph_D5": libgraph or {},
        "claim_graph": claimgraph or {},
        "claim_level_validation": _claim_level_validation(claimgraph or {}),
        "outcome_switching": outswitch or {},
        "novelty_audit": _novelty_audit(claimgraph or {}, aras),
        "paper_ranking_axis_status": "RETIRED (R1): 0/6 usable on any corpus tested; ranking collapses to "
                                     "1 genre bucket. The `diagnostic`/`scoped_rankings` blocks below are an "
                                     "appendix, not the headline. The unit of record is the claim (see "
                                     "claim_level_validation + novelty_audit + per-ARA extractive_fidelity).",
        "per_ara": aras,
    }
    (V3_DIR / "library_metrics_v3.json").write_text(json.dumps(lib, indent=2), encoding="utf-8")

    L = ["# Library metrics — V3", "",
         f"Two-axis (paper_rankers vs artifact_trust), validity+variance gate, K_MIN={K_MIN} genre ladder. "
         f"{len(aras)} ARAs.", "",
         "## Genres (Tier A gold / Tier C deterministic)", ""]
    for a in aras:
        L.append(f"- `{a['slug']}` → **{a['genre']}** [{a['coarse']}] ({a['genre_source']}); "
                 f"trust w={a['artifact_trust']['weight_w']}"
                 + ("  ⚠ low-trust" if a["artifact_trust"]["low_trust"] else ""))
    L += ["", "## RC1 diagnostic — variance AND validity (no bare 'discriminating')", "",
          "| Paper ranker | n | variance | validity | usable |", "|---|---|---|---|---|"]
    for k, v in diag.items():
        L.append(f"| {k} | {v['n']} | {v['variance_verdict']} | {v['validity_verdict']} | "
                 f"{'✅' if v['usable'] else '—'} |")
    n_usable = sum(1 for v in diag.values() if v["usable"])
    L += ["", f"**Usable paper-rankers on this corpus: {n_usable}/{len(diag)}.** "
          "(Master's predicted honest outcome: 0–1. That is the validity gate working, not a bug.)", ""]
    L += ["## Genre-scoped rankings (K_MIN ladder; no singleton rankings)", ""]
    for m, buckets in {m: scoped_ranking(aras, m) for m in PAPER_RANKERS}.items():
        L.append(f"### {m}")
        if not buckets:
            L.append("- (no numeric values)")
        for b, info in buckets.items():
            if "ranking" in info:
                L.append(f"- **{b}** ({info['level']}): " + " > ".join(f"{s} ({v})" for s, v in info["ranking"]))
            else:
                L.append(f"- **{b}** ({info['level']}): {info['members']}")
        L.append("")
    (V3_DIR / "library_metrics_v3.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_comparison(aras: list[dict]):
    """comparison_v2_v3.md — check each acceptance criterion against V2 outputs."""
    v2 = json.loads(v1.read(V2_DIR / "library_metrics_v2.json") or "{}")
    v2_by = {p["slug"]: p for p in v2.get("per_ara", [])}
    by = {a["slug"]: a for a in aras}

    def v2_rank(slug, key):
        p = v2_by.get(slug)
        if not p:
            return "—"
        return p["rankers"].get(key, {}).get("value", "—")

    def v3_val(slug, key):
        r = by[slug]["paper_rankers"].get(key, {}) if slug in by else {}
        return r.get("value", "—")

    C = ["# V2 → V3 comparison (acceptance criteria)", "",
         "Each row is a round-2 acceptance criterion (critiques-round2.md) checked against the V2 number "
         "and the V3 number. `pending` = a module/LLM/MCP pass that degraded gracefully.", "",
         "## RC3 — fabricated dead-ends stripped", "",
         "| ARA | V2 dead_end_density | V3 dead_end_density | V3 synthetic excluded |", "|---|---|---|---|"]
    for a in aras:
        dd = a["paper_rankers"]["dead_end_density"]
        C.append(f"| {a['slug']} | {v2_rank(a['slug'], 'dead_end_density')} | {dd['value']} | "
                 f"{dd.get('n_synthetic', '—')} |")
    C += ["", "**Acceptance:** che26 dead_end_density → 0 (all its dead-ends are synthetic).", "",
          "## RC4 — corrective_science requires an evidence-addressing edge", "",
          "| ARA | V2 corrective | V3 corrective | V3 corrective edges |", "|---|---|---|---|"]
    for a in aras:
        cc = a["paper_rankers"]["corrective_science_score"]
        C.append(f"| {a['slug']} | {v2_rank(a['slug'], 'corrective_science_score')} | {cc['value']} | "
                 f"{cc.get('n_corrective_edges', '—')} |")
    C += ["", "**Acceptance:** corrective collapses toward ~0 corpus-wide (refutes=0; bounds=baseline).", "",
          "## RC5 — negative results detected by semantics, not status", "",
          "| ARA | V2 negative_share | V3 negative_share | V3 n_negative |", "|---|---|---|---|"]
    for a in aras:
        ng = a["paper_rankers"]["negative_result_share"]
        C.append(f"| {a['slug']} | {v2_rank(a['slug'], 'negative_result_share')} | {ng['value']} | "
                 f"{ng.get('n_negative', '—')} |")
    C += ["", "**Acceptance:** woj25 counts its real null (C04) as negative knowledge.", "",
          "## RC8 — genre classifier matches gold", "",
          "| ARA | V2 genre | V3 genre (gold/tierC) |", "|---|---|---|"]
    for a in aras:
        v2g = v2_by.get(a["slug"], {}).get("genre", "—")
        C.append(f"| {a['slug']} | {v2g} | {a['genre']} ({a['genre_source']}) |")
    C += ["", "**Acceptance:** cum26 → narrative_review_survey (was clinical_trial in V2).", "",
          "## RC1 — every ranker carries a validity verdict; usable count", ""]
    diag = diagnose(aras)
    n_usable = sum(1 for v in diag.values() if v["usable"])
    C.append(f"- Usable paper-rankers: **{n_usable}/{len(diag)}** "
             f"(V2 marked several bare 'discriminating' with no validity check).")
    C += ["", "## RC10 — homogenization/compiler signals routed off the paper ranking", "",
          "| ARA | trust w | low-trust? |", "|---|---|---|"]
    for a in aras:
        t = a["artifact_trust"]
        C.append(f"| {a['slug']} | {t['weight_w']} | {'yes' if t['low_trust'] else 'no'} |")
    C += ["", "**Acceptance:** grounding/falsifiability/env now feed w, never a paper rank; "
          "two ARAs differing only in environment.md get the same paper rank, different w."]
    (V3_DIR / "comparison_v2_v3.md").write_text("\n".join(C) + "\n", encoding="utf-8")


# ============================ main ============================
def assert_gold_classifier():
    """RC8 CI: Tier-C classifier reproduces gold where gold exists (audit; gold still wins at runtime)."""
    mism = []
    for slug, gold in GENRE_GOLD.items():
        base = ARA_LIB / slug
        if not base.exists():
            continue
        pred = classify_genre_tierC(base, slug)
        if pred != gold:
            mism.append((slug, pred, gold))
    return mism


def main():
    present = [s for s in CORPUS_12 if (ARA_LIB / s / "logic/claims.md").exists()]
    missing = [s for s in CORPUS_12 if s not in present]
    print(f"V3 over {len(present)}/12 scored ARAs" + (f"  (missing: {missing})" if missing else ""))

    ctxs = [build_context(s) for s in present]
    aras = [compute_ara_v3(c) for c in ctxs]
    for a in aras:
        write_ara_v3(a)

    ext = EXTERNAL.external_validation(ctxs)
    libgraph = LIBGRAPH.library_graph(ctxs)
    claimgraph = CLAIMGRAPH.claim_graph(ctxs)
    outswitch = OUTSWITCH.outcome_switching(ctxs)
    write_library(aras, ext, libgraph, claimgraph, outswitch)
    write_comparison(aras)

    diag = diagnose(aras)
    n_usable = sum(1 for v in diag.values() if v["usable"])
    print("\n=== V3 diagnostic (variance × validity) ===")
    for k, v in diag.items():
        print(f"  {k:28s} variance={v['variance_verdict']:18s} validity={v['validity_verdict']:16s} "
              f"usable={v['usable']}")
    print(f"\nusable paper-rankers: {n_usable}/{len(diag)}")

    mism = assert_gold_classifier()
    print(f"RC8 tierC-vs-gold mismatches (audit only): {len(mism)}" + (f" {mism}" if mism else ""))
    print(f"wrote per-ARA metrics/v3/ + {V3_DIR}/library_metrics_v3.* + comparison_v2_v3.md")


if __name__ == "__main__":
    main()
