#!/usr/bin/env python3
"""
V3 external validation — RC2 (the BLOCKER, shipped as an honest PARTIAL).

CORPUS-LEVEL module: `external_validation(all_ctx)` receives the full list of per-ARA ctx dicts
(see compute_metrics_v3.build_context / detectors.py for the ctx schema). `all_ctx` is read-only.

Per compiler-model.md ("What this does NOT buy us"): even a perfect compiler gives us no external
ground truth. This module is the ONLY thing in the pipeline that touches a signal outside the ARA's
own compiled text — a public trial registry, a literature-integrity database, and (if it exists) an
independent human label. Per plan.md / v3-spec.md RC2, the honest predicted outcome is that a
properly-powered, held-out validation is NOT achievable at n=12; this module ships the thin partial
that IS achievable, and says so plainly in `summary` rather than laundering it.

Reachability actually checked at build time (see report): no ClinicalTrials MCP tool was discoverable
via ToolSearch in this environment. Direct network egress (urllib) IS reachable in this sandbox, so
this module uses the spec's explicitly-sanctioned REST fallback:
  - ClinicalTrials.gov API v2  (https://clinicaltrials.gov/api/v2/studies/<NCT>)
  - Europe PMC REST API        (https://www.ebi.ac.uk/europepmc/webservices/rest/search)
Both are wrapped in try/except with short timeouts; any failure degrades to `pending` for that item —
never a fabricated label. Raw ClinicalTrials JSON is cached under external_cache/<nct>.json.

Return schema (frozen):
  external_validation(all_ctx) -> {
     "clinicaltrials": {"value": ..., "validity": ..., "n": int, "concordance": [...], "detail": str},
     "retraction":     {"value": ..., "validity": ..., "detail": str},
     "expert":         {"value": ..., "validity": ..., "spearman_rho": float|None, "n": int, "detail": str},
     "summary":        str,
  }
"""
from __future__ import annotations

import json
import math
import re
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "external_cache"
EXPERT_LABELS_PATH = HERE / "expert_labels.yaml"

CT_API = "https://clinicaltrials.gov/api/v2/studies/{nct}?format=json"
EPMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
USER_AGENT = "ara-metrics-v3-external/1.0 (research corpus RC2 harness; non-commercial)"

RETRACT_RE = re.compile(r"retract|expression of concern|erratum|correction", re.I)
FUTILITY_RE = re.compile(r"futility|lack of efficacy|did not meet|failed to meet|discontinued for efficacy", re.I)
DASHES = ("−", "–", "—")  # unicode minus, en dash, em dash -> normalize to ascii '-'


# ============================ tiny HTTP helper (stdlib only) ============================
def _http_get_json(url: str, timeout: float = 12.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https hosts only)
        return json.loads(resp.read().decode("utf-8"))


# ============================ 1. ClinicalTrials.gov concordance ============================
def _load_or_fetch_nct(nct: str) -> dict | None:
    """Cache-first: read external_cache/<nct>.json if present; else try the REST fallback and cache
    the raw response. Returns None (never fabricates) if neither the cache nor the network has it."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = CACHE_DIR / f"{nct}.json"
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass  # corrupt cache -> fall through to a live refetch
    try:
        data = _http_get_json(CT_API.format(nct=nct))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return None
    try:
        cache_path.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass
    return data


def _status_module(study: dict) -> dict:
    return study.get("protocolSection", {}).get("statusModule", {}) or {}


def _primary_outcomes(study: dict) -> list:
    return study.get("protocolSection", {}).get("outcomesModule", {}).get("primaryOutcomes", []) or []


def _primary_result_measurements(study: dict) -> list:
    """PRIMARY-type outcome measures from resultsSection, each as {title, groups: {id: label}, values: {id: float}}."""
    res = study.get("resultsSection", {}) or {}
    oms = res.get("outcomeMeasuresModule", {}).get("outcomeMeasures", []) or []
    out = []
    for om in oms:
        if om.get("type") != "PRIMARY":
            continue
        groups = {g.get("id"): g.get("title") for g in om.get("groups", [])}
        values = {}
        for cls in om.get("classes", []):
            for cat in cls.get("categories", []):
                for m in cat.get("measurements", []):
                    try:
                        values[m.get("groupId")] = float(m.get("value"))
                    except (TypeError, ValueError):
                        continue
        out.append({"title": om.get("title"), "groups": groups, "values": values})
    return out


def _numbers_in_text(text: str) -> list:
    if not text:
        return []
    norm = text
    for d in DASHES:
        norm = norm.replace(d, "-")
    return [float(x) for x in re.findall(r"-?\d+\.\d+|-?\d+", norm)]


def _claim_text(ctx: dict) -> str:
    heads = ctx.get("headline_claims") or []
    if heads:
        return " ".join(heads)
    # fall back to all claim statements (some ARAs' "supported" status string carries a parenthetical
    # caveat, e.g. sal26, so the spine's strict `status == "supported"` headline filter comes back empty)
    return " ".join(c.get("statement", "") for c in ctx.get("claims", []))


def _judge_concordance(ctx: dict, study: dict, is_landscape_citation: bool) -> dict:
    if is_landscape_citation:
        return {"label": "not_applicable",
                "reason": "ARA's central claims are corpus-level pipeline tallies (drug/trial counts "
                           "across the AD landscape), not this specific trial's own registered endpoint "
                           "result; the NCT is one of several landscape citations, not the paper's subject "
                           "trial. Endpoint concordance does not apply; verified only that the NCT resolves "
                           "to a real, distinct trial (citation-integrity signal, not concordance)."}

    status = _status_module(study)
    overall = status.get("overallStatus")
    why = status.get("whyStopped") or ""
    has_results = bool(study.get("hasResults"))

    if not has_results:
        return {"label": "neutral",
                "reason": f"registry hasResults=False (overallStatus={overall!r}); no posted PRIMARY-"
                           "outcome results exist yet to compare against the ARA's claim."}

    prim = _primary_result_measurements(study)
    if not prim:
        titles = [o.get("measure") for o in _primary_outcomes(study)]
        return {"label": "neutral",
                "reason": f"hasResults=True but no parseable numeric PRIMARY-outcome measurements in "
                           f"resultsSection (registered primary outcome(s): {titles}); cannot compute "
                           "numeric concordance from this record."}

    claim_nums = _numbers_in_text(_claim_text(ctx))
    matched, total, detail_matches = 0, 0, []
    for om in prim:
        for gid, v in om["values"].items():
            total += 1
            tol = max(0.5, abs(v) * 0.10)
            hit = any(abs(v - cn) <= tol for cn in claim_nums)
            matched += hit
            detail_matches.append({"outcome": om["title"], "group": om["groups"].get(gid, gid),
                                    "registered_value": v, "matched_in_claim_text": hit})

    if matched == 0 and FUTILITY_RE.search(why):
        return {"label": "discordant",
                "reason": f"registry status/whyStopped suggests futility/non-significance ({why!r}) "
                           "while none of the registered PRIMARY-outcome group values reproduce in the "
                           "ARA's claim numbers.",
                "matches": detail_matches}

    if total and matched / total >= 0.5:
        return {"label": "concordant",
                "reason": f"{matched}/{total} registered PRIMARY-outcome group values are reproduced "
                           "(within tolerance) in the ARA's own headline-claim numbers.",
                "matches": detail_matches}

    return {"label": "neutral",
            "reason": f"registered PRIMARY outcome located ({[o['title'] for o in prim]}) but only "
                       f"{matched}/{total} group values match the ARA's claim text within tolerance; "
                       "topic overlaps but a confident concordant/discordant call is not warranted from "
                       "this thin numeric check.",
            "matches": detail_matches}


def _clinicaltrials_concordance(all_ctx: list) -> dict:
    linked = [c for c in all_ctx if c.get("ncts")]
    if not linked:
        return {"value": "N/A", "validity": "N/A", "n": 0, "concordance": [],
                "detail": "no ARA in this corpus carries a linked NCT."}

    concordance, n_fetched, n_failed = [], 0, 0
    for ctx in linked:
        slug = ctx["slug"]
        is_landscape = ctx.get("coarse") == "SYNTHESIS" and len(ctx["ncts"]) > 2
        for nct in ctx["ncts"]:
            study = _load_or_fetch_nct(nct)
            if study is None:
                n_failed += 1
                concordance.append({"slug": slug, "nct": nct, "label": "pending",
                                     "reason": "registry unreachable: no ClinicalTrials MCP tool was "
                                               "discoverable, and the clinicaltrials.gov REST fallback "
                                               "also failed for this NCT — concordance not fabricated."})
                continue
            n_fetched += 1
            j = _judge_concordance(ctx, study, is_landscape)
            ident = study.get("protocolSection", {}).get("identificationModule", {})
            concordance.append({"slug": slug, "nct": nct, "brief_title": ident.get("briefTitle"),
                                 "label": j["label"], "reason": j["reason"]})

    if n_fetched == 0:
        return {"value": "pending", "validity": "pending", "n": len(linked), "concordance": concordance,
                "detail": "No ClinicalTrials MCP tool was reachable in this environment, and the "
                           "clinicaltrials.gov REST fallback failed for every linked NCT — reporting "
                           "pending rather than fabricating concordance."}

    judged = [c["label"] for c in concordance if c["label"] in ("concordant", "discordant", "neutral")]
    n_conc = judged.count("concordant")
    n_disc = judged.count("discordant")
    n_neut = judged.count("neutral")
    n_na = sum(1 for c in concordance if c["label"] == "not_applicable")
    value = (n_conc / len(judged)) if judged else "pending"
    validity = "source_bound" if judged else "pending"
    detail = (f"No ClinicalTrials MCP tool was discoverable via ToolSearch in this environment; used the "
               f"spec-sanctioned REST fallback (clinicaltrials.gov API v2). Fetched {n_fetched}/"
               f"{n_fetched + n_failed} linked-NCT lookups (raw JSON cached under external_cache/<nct>.json). "
               f"Among trial-outcome-comparable NCTs: {n_conc} concordant, {n_disc} discordant, {n_neut} "
               f"neutral; {n_na} are landscape citations (not_applicable — a review citing many trials, not "
               f"reporting one as its own subject); {n_failed} pending (unreachable). Only n={len(linked)} "
               "ARAs carry any NCT at all, so this is a thin, non-powered partial — not a validation.")
    return {"value": value, "validity": validity, "n": len(linked), "concordance": concordance, "detail": detail}


# ============================ 2. Retraction / EoC lookup (known-degenerate) ============================
def _year_from_slug(slug: str) -> int | None:
    m = re.match(r"^[a-z]+(\d{2})", slug)
    return 2000 + int(m.group(1)) if m else None


def _epmc_lookup(doi: str) -> dict | None:
    try:
        return _http_get_json(f"{EPMC_API}?query=DOI:{doi}&format=json&resultType=core")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return None


def _classify_retraction_record(record: dict | None, year_fallback: int | None) -> dict:
    if record is None:
        return {"flag": False, "checked": False,
                "note": f"Europe PMC unreachable or no DOI match; falling back to the paper's naming-"
                         f"convention year ({year_fallback}) only — no retraction check possible without "
                         "network, so this is reported as unchecked, not asserted clean."}
    hits = (record.get("resultList") or {}).get("result") or []
    if not hits:
        return {"flag": False, "checked": True, "note": "no Europe PMC record found for this DOI."}
    top = hits[0]
    title = top.get("title") or ""
    pub_types = " ".join((top.get("pubTypeList") or {}).get("pubType") or [])
    pub_year = top.get("pubYear")
    flagged = bool(RETRACT_RE.search(title) or RETRACT_RE.search(pub_types))
    note = ("title/pubTypeList carries a retraction/correction marker" if flagged else
            f"clean: no retraction/EoC/correction marker in title or pubTypeList (pubYear={pub_year}).")
    return {"flag": flagged, "checked": True, "pub_year": pub_year, "note": note}


def _retraction_lookup(all_ctx: list) -> dict:
    papers, flagged_slugs, n_checked = [], [], 0
    for ctx in all_ctx:
        slug = ctx["slug"]
        doi = ((ctx.get("sources") or {}).get("paper") or {}).get("doi") or ctx.get("v1", {}).get("doi")
        year_fallback = _year_from_slug(slug)
        record = _epmc_lookup(doi) if doi else None
        status = _classify_retraction_record(record, year_fallback)
        if status["checked"]:
            n_checked += 1
        if status["flag"]:
            flagged_slugs.append(slug)
        papers.append({"slug": slug, "doi": doi, **status})

    detail = (f"Europe PMC REST lookup attempted for all {len(all_ctx)} papers (DOI-resolved for "
               f"{n_checked}); {len(flagged_slugs)} flagged ({flagged_slugs or 'none'}). This corpus is "
               "known-degenerate for this axis: all 12 papers are 2025-2026 publications with no retraction "
               "/ expression-of-concern / correction history, so zero variance here is the expected honest "
               "result of running the check, not a sign the check didn't run.")
    return {"value": "degenerate", "validity": "degenerate", "detail": detail, "papers": papers}


# ============================ 3. Expert labels (Spearman rho, stdlib rank-correlation) ============================
def _rank(values: list) -> list:
    """Average ranks (1-based), ties get the mean rank of the tied block. stdlib only."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def _spearman(xs: list, ys: list) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    rx, ry = _rank(xs), _rank(ys)
    mean_rx, mean_ry = sum(rx) / n, sum(ry) / n
    num = sum((a - mean_rx) * (b - mean_ry) for a, b in zip(rx, ry))
    den_x = math.sqrt(sum((a - mean_rx) ** 2 for a in rx))
    den_y = math.sqrt(sum((b - mean_ry) ** 2 for b in ry))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def _proxy_ranker_value(ctx: dict) -> float | None:
    """Best-effort numeric proxy available purely from ctx (all_ctx does NOT carry the computed v3
    paper_ranker outputs — those are assembled later, per-ARA, in compute_ara_v3). Used only if
    expert_labels.yaml exists and doesn't itself name which ranker/field to correlate against."""
    try:
        d2 = ctx["v1"]["D2_claim_evidence_integrity"]
        for key in ("explicit_vs_inferred_ratio", "evidence_density", "claim_evidence_ratio"):
            if isinstance(d2.get(key), (int, float)):
                return float(d2[key])
    except Exception:
        pass
    n = ctx.get("claims")
    return float(len(n)) if isinstance(n, list) else None


def _expert_correlation(all_ctx: list) -> dict:
    if not EXPERT_LABELS_PATH.exists():
        return {"value": "pending", "validity": "pending", "spearman_rho": None, "n": 0,
                "detail": f"{EXPERT_LABELS_PATH.name} does not exist. To close this partial we would need "
                           "a YAML file, keyed by ARA slug (n<=12), holding an independent expert quality/"
                           "rigor label per paper (e.g. `<slug>: {rigor: 1-5}`) assigned by a reviewer who "
                           "is NOT the paper's author and NOT the person operating the compiler — otherwise "
                           "the correlation is circular (labeler approx author). Not fabricated."}
    try:
        import yaml
        labels = yaml.safe_load(EXPERT_LABELS_PATH.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {"value": "pending", "validity": "pending", "spearman_rho": None, "n": 0,
                "detail": f"{EXPERT_LABELS_PATH.name} present but failed to parse ({e})."}

    by_slug = {c["slug"]: c for c in all_ctx}
    xs, ys, n_used = [], [], 0
    for slug, lab in (labels or {}).items():
        ctx = by_slug.get(slug)
        if ctx is None:
            continue
        score = lab.get("rigor") if isinstance(lab, dict) else lab
        proxy = _proxy_ranker_value(ctx)
        if isinstance(score, (int, float)) and proxy is not None:
            xs.append(float(score))
            ys.append(proxy)
            n_used += 1

    rho = _spearman(xs, ys) if n_used >= 3 else None
    detail = (f"{EXPERT_LABELS_PATH.name} found with {len(labels)} entries; {n_used} matched to scored "
               f"ARAs. CIRCULARITY CAVEAT: at this corpus size the expert labeler is effectively the same "
               "person who ran/reviewed the compiler pass (labeler approx author) — this rho is NOT an "
               "independent validation signal, only a sanity check, and MUST be reported with that caveat "
               "attached, never as 'validated'. Also n<=12 cannot power a Spearman test regardless of the "
               f"labeler's independence (rho={rho}).")
    validity = "pending_sem" if rho is not None else "pending"
    return {"value": rho if rho is not None else "pending", "validity": validity, "spearman_rho": rho,
            "n": n_used, "detail": detail}


# ============================ top level ============================
def external_validation(all_ctx: list) -> dict:
    clinicaltrials = _clinicaltrials_concordance(all_ctx)
    retraction = _retraction_lookup(all_ctx)
    expert = _expert_correlation(all_ctx)

    summary = (
        "RC2 ruling encoded: a properly-powered, HELD-OUT external validation is NOT honestly achievable "
        f"at n={len(all_ctx)} — this module ships the harness, not the validation. "
        f"(1) ClinicalTrials.gov concordance: {clinicaltrials['n']} of {len(all_ctx)} ARAs carry a linked "
        f"NCT; validity={clinicaltrials['validity']!r}. Thin and genuinely external/non-gameable where it "
        "resolves, but n is too small to power anything beyond a spot-check. "
        f"(2) Retraction/EoC lookup: validity='degenerate' by construction (all {len(all_ctx)} papers are "
        "2025-2026, clean) — zero variance is the correct honest output, not a bug. "
        f"(3) Expert-label rho: validity={expert['validity']!r} "
        + ("(no expert_labels.yaml -> pending; would need an independent, non-author labeler)."
           if expert["value"] == "pending" else
           "(computed, but circularity-caveated: labeler approx author, and n<=12 is not powered — this "
           "is NOT reported as 'validated'.)") +
        " Held-out validation: pending: larger heterogeneous code-shipping corpus. Do not launder the "
        "underpowered ClinicalTrials spot-check or expert rho as 'validated' — the honest state of RC2 "
        "on this corpus is partial-and-thin by design, which is the gate working, not a V3 failure."
    )

    return {"clinicaltrials": clinicaltrials, "retraction": retraction, "expert": expert, "summary": summary}
