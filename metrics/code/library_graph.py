#!/usr/bin/env python3
"""
V3 D5 — the flagship cross-library claim graph (restored).

This is the library-level (corpus-wide) module the spine will call once per run as
`library_graph(all_ctx)`. It has TWO halves:

  (a) DETERMINISTIC proxies — computable today, no external service:
        - shared_trial_clusters: ARAs citing the same NCT (corroboration via shared evidence)
        - citation_reuse_edges: one ARA's related_work cites another ARA's DOI (in-library reuse)
        - claim_redundancy: pairwise token-Jaccard over claim statements (near-duplicate proxy)
      (Adapted from V1's compute_metrics.compute_library_graph.)

  (b) FOL claim-graph — the real thing: run the oshima nl2fol pipeline
        (research/ara/src/execution/app/services/nlp2fol/) over every claim statement to get a
        first-order-logic representation, then group FOL-equivalent claims ACROSS papers to compute
        corroboration (n independent papers asserting an equivalent claim) and contradiction.

      FEASIBILITY SPIKE RESULT (recorded here, re-checked live on every call via `_spike_oshima`):
      the oshima subsystem is a PARTIALLY CAPTURED artifact. Only two of the ~15 modules
      `complete_pipeline_processor.py` imports actually exist in this repo:
      `logic_mapper.py` and `complete_pipeline_processor.py` itself. Missing, repo-wide (verified
      by `find research/ara -iname '*nlp2fol*' -o -iname '*sumo*'` — no hits beyond the two files
      above): `composer.py`, `logic_feature_detector.py`, `parser.py`, `splitter.py`,
      `triple_wrapper.py`, `variable_binder.py`, and the ENTIRE `ontologies/sumo/` subpackage
      (`s0_resources.py` .. `s6_typing_hints.py`) that would load the actual SUMO+WordNet
      ontology resource files. `import app.services.nlp2fol.complete_pipeline_processor` fails
      immediately with `ModuleNotFoundError: No module named 'app.services.nlp2fol.composer'`
      before SUMO/WordNet resource loading is ever reached. `spacy` and `nltk` are also not
      installed in this environment, but that is moot — the pipeline can't even be imported.
      This is not a missing-dependency problem; it is a missing-source-code problem. Building the
      12 absent modules ourselves would mean fabricating the FOL pipeline, which is out of scope
      (and would BE the fabrication this module exists to avoid). Per the stub contract: status is
      "pending" with this precise account, no fabricated FOL/corroboration.

      If the missing modules are ever added to the repo, `_spike_oshima()` will detect success on
      its next run and `_run_fol_pipeline()` (implemented below, never yet exercised end-to-end)
      will produce real FOL, freeze it to `fol/<slug>.json`, and compute corroboration/contradiction
      by canonical-AST grouping across papers.

`all_ctx` = list of per-ARA ctx dicts (see detectors.py / compute_metrics_v3.build_context for the
ctx schema); each has ctx["claims"] (list of dicts with .id/.statement), ctx["ncts"],
ctx["related_work_md"], ctx["v1"]["_rw_dois"] / ctx["v1"]["doi"] / ctx["v1"]["_ncts"].

Return schema (frozen):
  library_graph(all_ctx) -> {
    "deterministic": {
       "shared_trial_clusters": {nct: [slug,...]}, "n_shared_trial_clusters": int,
       "citation_reuse_edges": [{"from": slug, "cites": slug, "doi": ...}],
       "claim_redundancy": {"near_duplicate_pairs": int, "redundancy_rate": float, "examples": [...]},
    },
    "fol": {"status": "computed"|"pending", "n_claims_fol": int,
            "corroboration": [{"claim_group": [...], "n_papers": int}], "contradiction": [...],
            "detail": str},
    "summary": str,
  }

Note the honest expectation (compiler-model.md / metrics-critique.md §5): on this 12-ARA single-topic
corpus the deterministic proxies will be near-zero (few shared trials, ~no in-library citation), and
even a working FOL graph would find little corroboration at n=12. The value of building it is to have
the flagship PRESENT and honest rather than silently missing — and ready for a larger corpus.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
V3_DIR = HERE.parent                                  # research/metrics/v3
RESEARCH = V3_DIR.parent.parent                       # research/
ARA_SRC_ROOT = RESEARCH / "ara" / "src" / "execution"  # contains the `app` package
NLP2FOL_DIR = ARA_SRC_ROOT / "app" / "services" / "nlp2fol"
FOL_OUT_DIR = V3_DIR / "fol"

# Every submodule complete_pipeline_processor.py needs, in the order it imports them.
_REQUIRED_SUBMODULES = [
    "app.services.nlp2fol.composer",
    "app.services.nlp2fol.logic_feature_detector",
    "app.services.nlp2fol.logic_mapper",
    "app.services.nlp2fol.ontologies.sumo.s0_resources",
    "app.services.nlp2fol.ontologies.sumo.s1_mention_extractor",
    "app.services.nlp2fol.ontologies.sumo.s2_normalizer",
    "app.services.nlp2fol.ontologies.sumo.s3_wn_candidates",
    "app.services.nlp2fol.ontologies.sumo.s4_sumo_join",
    "app.services.nlp2fol.ontologies.sumo.s5_ranker",
    "app.services.nlp2fol.ontologies.sumo.s6_typing_hints",
    "app.services.nlp2fol.parser",
    "app.services.nlp2fol.splitter",
    "app.services.nlp2fol.triple_wrapper",
    "app.services.nlp2fol.variable_binder",
]


# ============================ (a) deterministic proxies ============================
def _tokset(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(w) > 3}


def _deterministic_proxies(all_ctx: list[dict]) -> dict:
    # shared clinical-trial NCT clusters (corroboration-by-shared-evidence proxy)
    nct_map: dict[str, list[str]] = {}
    for ctx in all_ctx:
        slug = ctx["slug"]
        for nct in ctx.get("v1", {}).get("_ncts", []) or []:
            if nct:
                nct_map.setdefault(nct, []).append(slug)
    shared_ncts = {n: s for n, s in nct_map.items() if len(s) > 1}

    # in-library citation reuse: does one ARA's related_work cite another ARA's DOI?
    doi_owner: dict[str, str] = {}
    for ctx in all_ctx:
        doi = (ctx.get("v1", {}).get("doi") or "").lower()
        if doi:
            doi_owner[doi] = ctx["slug"]
    reuse_edges = []
    for ctx in all_ctx:
        slug = ctx["slug"]
        for d in ctx.get("v1", {}).get("_rw_dois", []) or []:
            d = (d or "").lower()
            if d and d in doi_owner and doi_owner[d] != slug:
                reuse_edges.append({"from": slug, "cites": doi_owner[d], "doi": d})

    # claim redundancy proxy: pairwise Jaccard over claim-statement tokens (>=0.5 = near-dup)
    all_claims = [
        (ctx["slug"], c.get("id"), _tokset(c.get("statement", "")))
        for ctx in all_ctx
        for c in ctx.get("claims", []) or []
    ]
    near_dup = 0
    examples = []
    for i in range(len(all_claims)):
        for j in range(i + 1, len(all_claims)):
            s1, c1, t1 = all_claims[i]
            s2, c2, t2 = all_claims[j]
            if s1 == s2 or not t1 or not t2:
                continue
            jac = len(t1 & t2) / len(t1 | t2)
            if jac >= 0.5:
                near_dup += 1
                examples.append({"a": f"{s1}:{c1}", "b": f"{s2}:{c2}", "jaccard": round(jac, 2)})
    total_claims = len(all_claims)
    redundancy_rate = round(near_dup / total_claims, 4) if total_claims else 0.0

    return {
        "shared_trial_clusters": shared_ncts,
        "n_shared_trial_clusters": len(shared_ncts),
        "citation_reuse_edges": reuse_edges,
        "claim_redundancy": {
            "near_duplicate_pairs": near_dup,
            "redundancy_rate": redundancy_rate,
            "examples": examples[:10],
        },
    }


# ============================ (b) FOL claim-graph via oshima nl2fol ============================
def _nlp2fol_files_present() -> list[str]:
    if not NLP2FOL_DIR.exists():
        return []
    return sorted(p.name for p in NLP2FOL_DIR.glob("*.py"))


def _missing_report(import_error: str) -> str:
    present = _nlp2fol_files_present()
    present_set = {p[:-3] for p in present}  # strip .py
    missing_mods = [m for m in _REQUIRED_SUBMODULES if m.rsplit(".", 1)[-1] not in present_set]
    return (
        f"import failed: {import_error}. "
        f"nlp2fol dir = {NLP2FOL_DIR}; files present: {present or '(dir absent)'}; "
        f"missing submodules required by complete_pipeline_processor.py "
        f"(not found anywhere in the repo): {missing_mods}. "
        f"The entire ontologies/sumo/ subpackage (s0_resources..s6_typing_hints) that would load "
        f"the SUMO+WordNet ontology resource files is absent, so resource-file presence "
        f"(e.g. ontologies/sumo/s0_resources.load_resources targets) was never reached -- the "
        f"import fails at the top of complete_pipeline_processor.py before any resource loading "
        f"code runs. spacy/nltk dependency availability is likewise moot: the pipeline source "
        f"code it would call does not exist in this repo. This is a missing-source-code gap, not "
        f"a missing-dependency gap -- pip install / nltk.download cannot fix it."
    )


def _spike_oshima():
    """Feasibility spike: try to import + instantiate the oshima nl2fol pipeline and run it on one
    sentence. Never raises. Returns (ok: bool, detail: str, processor_or_none)."""
    added = False
    try:
        if str(ARA_SRC_ROOT) not in sys.path:
            sys.path.insert(0, str(ARA_SRC_ROOT))
            added = True
        # Clear any stale partial imports from a previous failed attempt in this process.
        for m in list(sys.modules):
            if m == "app" or m.startswith("app."):
                del sys.modules[m]
        mod = importlib.import_module("app.services.nlp2fol.complete_pipeline_processor")
        processor = mod.CompletePipelineProcessor()
        # one-sentence smoke test
        smoke = processor.process_claims_and_evidence({
            "claims": [{"id": "spike1",
                        "text": "Plasma p-tau217 differentiates Alzheimer's disease from controls."}],
            "evidence": [], "acronyms": {},
        })
        ok = bool(smoke.get("nlp2fol_results")) and \
            smoke["nlp2fol_results"][0].get("status") == "completed"
        detail = "spike import + one-sentence run succeeded" if ok else \
            f"spike ran but did not complete cleanly: {smoke['nlp2fol_results'][0].get('pipeline_error')}"
        return ok, detail, (processor if ok else None)
    except Exception as e:  # noqa - deliberately broad: this is a feasibility probe
        return False, _missing_report(f"{type(e).__name__}: {e}"), None
    finally:
        if added:
            try:
                sys.path.remove(str(ARA_SRC_ROOT))
            except ValueError:
                pass


def _canonical_ast(ast) -> str:
    """Canonicalize a logical_ast node to a comparable string (arg order doesn't matter)."""
    if not isinstance(ast, dict):
        return repr(ast)
    t = ast.get("type")
    if t in ("and", "or"):
        args = sorted(_canonical_ast(a) for a in ast.get("args", []))
        return f"{t}({','.join(args)})"
    if t == "not":
        inner = ast.get("arg", ast.get("lhs", {}))
        return f"not({_canonical_ast(inner)})"
    if t in ("forall", "exists"):
        return f"{t}({sorted(ast.get('vars', []))},{_canonical_ast(ast.get('body', {}))})"
    if t == "impl":
        return f"impl({_canonical_ast(ast.get('lhs', {}))}->{_canonical_ast(ast.get('rhs', {}))})"
    if t == "atom":
        pred = ast.get("predicate") or ast.get("pred") or ast.get("name")
        return f"atom({pred}:{ast.get('args', [])})"
    return json.dumps(ast, sort_keys=True)


def _run_fol_pipeline(all_ctx: list[dict], processor) -> dict:
    """Run oshima over every claim statement in every ARA, freeze per-ARA output, then group
    FOL-equivalent claims across papers for corroboration/contradiction. Not yet exercised
    end-to-end on this corpus (the spike currently fails) -- kept ready for when it isn't."""
    FOL_OUT_DIR.mkdir(exist_ok=True)
    all_claims_fol = []  # list of {slug, id, statement, canonical}
    for ctx in all_ctx:
        slug = ctx["slug"]
        claims_in = [{"id": c.get("id"), "text": c.get("statement", "")}
                     for c in ctx.get("claims", []) or [] if c.get("statement")]
        result = processor.process_claims_and_evidence(
            {"claims": claims_in, "evidence": [], "acronyms": {}})
        (FOL_OUT_DIR / f"{slug}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        for item in result.get("nlp2fol_results", []):
            if item.get("status") != "completed":
                continue
            ast = (item.get("logical_ast") or {}).get("ast", {})
            all_claims_fol.append({
                "slug": slug, "id": item.get("id"),
                "statement": item.get("original_text", ""),
                "canonical": _canonical_ast(ast),
            })

    groups: dict[str, list[dict]] = {}
    for c in all_claims_fol:
        groups.setdefault(c["canonical"], []).append(c)

    corroboration = []
    for canon, members in groups.items():
        papers = sorted({m["slug"] for m in members})
        if len(papers) > 1:
            corroboration.append({
                "claim_group": [f"{m['slug']}:{m['id']}" for m in members],
                "n_papers": len(papers),
            })

    contradiction = []
    canon_keys = set(groups.keys())
    for canon in canon_keys:
        neg = f"not({canon})"
        if neg in canon_keys:
            a_members, b_members = groups[canon], groups[neg]
            contradiction.append({
                "asserts": [f"{m['slug']}:{m['id']}" for m in a_members],
                "negates": [f"{m['slug']}:{m['id']}" for m in b_members],
            })

    return {
        "status": "computed",
        "n_claims_fol": len(all_claims_fol),
        "corroboration": corroboration,
        "contradiction": contradiction,
        "detail": (f"oshima nl2fol ran on {len(all_claims_fol)} claims across {len(all_ctx)} ARAs; "
                   f"froze per-ARA output to {FOL_OUT_DIR}/<slug>.json; grouped by canonical AST."),
    }


def _fol_claim_graph(all_ctx: list[dict]) -> dict:
    ok, detail, processor = _spike_oshima()
    if not ok:
        return {"status": "pending", "n_claims_fol": 0, "corroboration": [], "contradiction": [],
                "detail": detail}
    try:
        return _run_fol_pipeline(all_ctx, processor)
    except Exception as e:  # noqa - degrade gracefully, never fabricate
        return {"status": "pending", "n_claims_fol": 0, "corroboration": [], "contradiction": [],
                "detail": f"spike succeeded but full corpus run raised {type(e).__name__}: {e}"}


# ============================ entry point ============================
def library_graph(all_ctx: list[dict]) -> dict:
    det = _deterministic_proxies(all_ctx)
    fol = _fol_claim_graph(all_ctx)

    n_papers = len(all_ctx)
    parts = [
        f"D5 over {n_papers} ARAs.",
        f"Deterministic: {det['n_shared_trial_clusters']} shared-trial clusters, "
        f"{len(det['citation_reuse_edges'])} in-library citation-reuse edges, "
        f"{det['claim_redundancy']['near_duplicate_pairs']} near-duplicate claim pairs "
        f"(rate {det['claim_redundancy']['redundancy_rate']}) -- "
        + ("near-zero as expected on this single-topic corpus."
           if det['n_shared_trial_clusters'] + len(det['citation_reuse_edges'])
           + det['claim_redundancy']['near_duplicate_pairs'] <= 2
           else "non-trivial overlap found -- see details."),
        f"FOL: {fol['status']}"
        + (f" ({fol['n_claims_fol']} claims, {len(fol['corroboration'])} corroboration groups, "
           f"{len(fol['contradiction'])} contradictions)."
           if fol["status"] == "computed"
           else " -- oshima nl2fol pipeline is not runnable in this repo (source incomplete, "
                "see fol.detail); no FOL fabricated."),
    ]
    return {"deterministic": det, "fol": fol, "summary": " ".join(parts)}
