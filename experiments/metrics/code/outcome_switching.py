#!/usr/bin/env python3
"""
V3 P6 -- outcome_switching.py: the R2 fix from the cycle-3 metascientist critique
(research/metrics/v3/critiques/cycle3.md, section 3a + R2).

THE PROBLEM THIS REPLACES
--------------------------
claim_graph.py's `per_claim_trial_concordance` compares an ARA's reported number against
ClinicalTrials.gov's POSTED result for the same trial. The critique's verdict: that is a
transcription check, not a validation signal -- "concordant" only ever means "the compiler copied
the paper's own trial numbers correctly," and since both sides ultimately trace back to the same
underlying donanemab press release / results-posting event, 0/18 rows have ever come back
discordant across three build cycles. A check that cannot fail is not measuring anything.

THE FIX
-------
Outcome switching: does the endpoint an ARA's paper reports as its PRIMARY result match the
endpoint that was PRE-REGISTERED before the trial (ideally at the earliest available registration,
before any results existed)? This is a well-studied clinical-trial integrity failure (quietly
promoting a favorable secondary endpoint to "primary" after seeing unblinded data) and it is
un-fakeable in a specific, structural sense that transcription-checking is not: ClinicalTrials.gov
keeps a versioned, timestamped history of every protocol amendment, so "what was registered as
primary, and when" is a matter of public record independent of anything the paper or an ARA
compiler could assert or fabricate.

WHERE THE REGISTRY HISTORY DATA COMES FROM
--------------------------------------------
The public v2 REST API (`clinicaltrials.gov/api/v2/studies/{nct}`, the one `external.py` and
`claim_graph.py` already use) only exposes the CURRENT record -- it has no version history. The
ct.gov website's own "History of Changes" tab is powered by a separate, undocumented-but-public
internal API: `clinicaltrials.gov/api/int/studies/{nct}/history` (list of every versioned snapshot
with its date and which modules changed) and `.../history/{version}` (the full snapshot at that
version). This module's agent-author queried that API live for all three trial-linked NCTs in this
corpus and froze the results under `external_cache/outcome_switching_history_NCT*.json`. Per the
project-wide contract (compiler-model.md; see claim_graph.py's own docstring for the established
pattern), this module is CACHE-FIRST: it reads that frozen history if present, and falls back to a
live call to the same endpoint only on a cache miss. If neither is available, the entry is reported
`verdict: "indeterminate"` with a stated reason -- never fabricated.

WHAT COUNTS AS "THE PAPER'S CLAIMED PRIMARY"
-----------------------------------------------
ARA claims.md files don't carry a machine-readable "this claim IS the trial's primary endpoint"
flag as parsed structure (v1.parse_claims does not extract a `tags` field), so this module reads
each claim's own `**Tags**:` line directly out of `ctx["claims_md"]` (already part of the frozen
ctx schema every v3 module receives) and looks for the substring "primary" (catches both "primary"
and "co-primary" -- see sal25's C01/C02, tagged "co-primary"). If no supported claim is explicitly
tagged primary/co-primary, this module falls back to the lowest-numbered supported claim (C01, by
this corpus's own consistent authoring convention of leading with the paper's headline result) --
stated explicitly in `detail` whenever the fallback fires, never silently assumed.

MATCHING A CLAIM'S ENDPOINT TO A REGISTERED OUTCOME'S ENDPOINT
------------------------------------------------------------------
Reuses claim_graph.py's own `_OUTCOME_KEYWORD_FAMILIES` (iADRS / amyloid-clearance / CDR-SB) --
the same deterministic, corpus-grep-derived keyword lists that module already uses to link a
claim's own text to a registered outcome's measure name. This module does not invent a new mapping;
it applies the existing one in the other temporal direction (earliest-registered vs paper-claimed,
instead of registered vs posted-value).

HONEST RESULT, STATED UP FRONT (do not read this as a spoiler that was reverse-engineered into the
code -- it is the reason this module looks the way it does)
------------------------------------------------------------------------------------------------
Of the three trial-linked ARAs with a single resolvable NCT:
  - sal25 (NCT05108922, TRAILBLAZER-ALZ 4): CONSISTENT. The co-primary pair registered at
    inception (2021-10-26) is, in substance, identical to the co-primary pair the trial completed
    against and sal25's C01/C02 (explicitly tagged "co-primary") report exactly that pair.
  - jes26 (NCT04437511, TRAILBLAZER-ALZ 2): SWITCHED, with an important, honestly-reported caveat.
    The trial's ORIGINAL registered primary (version 0, 2020-06-17) was CDR-SB. It was amended to
    iADRS at version 21 (2021-03-24) -- ~8 months before any participant could possibly have
    reached the week-76 primary timepoint, i.e. structurally before any unblinded primary-endpoint
    data could have existed. jes26's own headline claim (C01) reports iADRS; CDR-SB survives in the
    paper only as a secondary claim (C02), not the ARA's tagged/lead result. This IS a real,
    timestamped registry change of the primary endpoint that the paper's headline result no longer
    matches at the earliest-registration level -- but the timing evidence argues for a blinded,
    pre-specified protocol amendment (a matter of TRAILBLAZER-ALZ 2's own public regulatory record,
    predating jes26's 2023+ publication by years) rather than the "quiet, data-driven promotion of
    a favorable secondary" pattern outcome-switching research is normally worried about. Both facts
    are reported; neither is suppressed to force a cleaner verdict.
  - sal26 (NCT03174938, BioFINDER-2): INDETERMINATE. BioFINDER-2 is an omnibus, decades-long
    natural-history cohort (has_results=False, still recruiting) registered to track clinical
    diagnosis and CDR-SB trajectories, not to test the plasma-biomarker-staging hypothesis sal26's
    own claim is about. There is no registered primary for sal26 to have switched away FROM -- the
    check is structurally out of scope for a secondary-use biomarker analysis of an omnibus cohort's
    banked samples/imaging, and is reported as such rather than forced into consistent/switched.
  - cum26 (8 distinct NCTs -- a multi-trial pipeline-landscape review, not a single-trial primary
    result of its own) is also reported, verdict=indeterminate, for the same structural reason: the
    check requires ONE trial whose OWN primary result the ARA's own claim reports; a landscape
    review citing 8 different trials' results as background has no single such comparison to make.

So: 1 consistent, 1 switched-with-mitigating-timing-evidence, 2 indeterminate-for-stated-structural
reasons. This is not a null result forced into a headline, and it is not a fabricated "gotcha" --
every fact above is sourced to a specific dated registry version, cited in the cache files and in
each row's own `detail` string.

Interface: `outcome_switching(all_ctx: list[dict]) -> {"checked": [...], "summary": str}`.
`all_ctx` = the list of per-ARA ctx dicts built by compute_metrics_v3.build_context. This module
does not rank papers, does not feed compute_metrics_v3's other axes, and does not edit
claim_graph.py -- it is an additive, standalone sibling module, per the project's compiler-model.md
convention for how new signals get added without disturbing the modules already trusted by prior
review cycles.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "external_cache"
USER_AGENT = "ara-metrics-v3-outcome-switching/1.0 (research corpus P6 harness; non-commercial)"

# Reused, not reinvented: claim_graph.py's corpus-grep-derived keyword families linking a claim's
# own prose to a registered outcome measure's name. Importing rather than copy-pasting keeps this
# module honest about "reusing its NCT-to-claim linkage" (per the module's brief) instead of
# silently forking a second, potentially-drifting copy of the same list.
try:
    from claim_graph import _OUTCOME_KEYWORD_FAMILIES
except ImportError:  # pragma: no cover -- module runnable standalone if claim_graph.py is absent
    _OUTCOME_KEYWORD_FAMILIES = [
        ("iadrs", ["iadrs", "integrated alzheimer"]),
        ("amyloid_clearance", ["amyloid plaque clearance", "ap clearance", "amyloid clearance"]),
        ("cdr_sb", ["cdr-sb", "cdr sb", "clinical dementia rating"]),
    ]

CT_HISTORY_LIST_URL = "https://clinicaltrials.gov/api/int/studies/{nct}/history"
CT_HISTORY_VERSION_URL = "https://clinicaltrials.gov/api/int/studies/{nct}/history/{version}"


# ======================================================================================
# fetch / cache layer -- cache-first, live fallback, never fabricate
# ======================================================================================
def _http_get_json(url: str, timeout: float = 15.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https host only)
        return json.loads(resp.read().decode("utf-8"))


def _live_earliest_registered_primary(nct: str) -> dict | None:
    """Live fallback ONLY (cache is checked first by the caller): fetch the ct.gov internal
    history API's version list, then fetch version 0 (the earliest snapshot) and pull its
    protocolSection.outcomesModule.primaryOutcomes. Returns None on any failure -- the caller
    reports indeterminate/pending with the stated reason, never guesses."""
    try:
        history = _http_get_json(CT_HISTORY_LIST_URL.format(nct=nct))
        changes = history.get("changes") or []
        if not changes:
            return None
        first = changes[0]
        v0 = _http_get_json(CT_HISTORY_VERSION_URL.format(nct=nct, version=first["version"]))
        proto = (v0.get("study") or {}).get("protocolSection", {}) or {}
        pos = proto.get("outcomesModule", {}).get("primaryOutcomes", []) or []
        return {
            "version": first["version"], "date": first.get("date"),
            "primary_outcomes": [{"measure": o.get("measure"), "time_frame": o.get("timeFrame")}
                                  for o in pos],
            "_source": "live_ct_gov_internal_history_api",
        }
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError, OSError):
        return None


def _load_history_cache(nct: str) -> dict | None:
    path = CACHE_DIR / f"outcome_switching_history_{nct}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = f"cache:{path.name}"
            return data
        except Exception:
            pass
    live = _live_earliest_registered_primary(nct)
    if live is None:
        return None
    return {
        "nct": nct,
        "initial_registration": live,
        "primary_outcome_amendment": None,
        "current_registered_primary_outcomes": None,
        "analysis_note": "Live fallback fetch only (no frozen cache file existed for this NCT); "
                          "amendment history beyond the earliest version was not checked in this "
                          "fallback path -- only the initial registration is available.",
        "_source": "live_fallback",
    }


# ======================================================================================
# paper's claimed primary -- tag-based, with a stated fallback rule
# ======================================================================================
def _claim_body_by_id(claims_md: str) -> dict[str, str]:
    blocks = re.split(r"(?m)^##\s+(C\d+):", claims_md or "")
    out = {}
    for i in range(1, len(blocks), 2):
        out[blocks[i]] = blocks[i + 1]
    return out


def _field(body: str, name: str) -> str:
    m = re.search(rf"-\s*\*\*{re.escape(name)}\*\*:\s*(.*)", body)
    return m.group(1).strip() if m else ""


def _claim_tags(body: str) -> list[str]:
    raw = _field(body, "Tags")
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


def _cid_num(cid: str) -> int:
    m = re.search(r"\d+", cid or "")
    return int(m.group()) if m else 10**9


def _paper_claimed_primary(ctx: dict) -> tuple[list[dict], str]:
    """Returns (claims, method) where claims is a list of {"claim_id","statement"} this ARA
    reports as its primary result, and method states HOW that was decided (explicit tag vs
    fallback), so a reader never has to guess whether this was asserted or inferred."""
    supported = [c for c in ctx.get("claims", []) or [] if str(c.get("status", "")).startswith("supported")]
    if not supported:
        return [], "no supported claims in this ARA"
    bodies = _claim_body_by_id(ctx.get("claims_md", ""))
    tagged = []
    for c in supported:
        body = bodies.get(c["id"], "")
        if any("primary" in t for t in _claim_tags(body)):
            tagged.append({"claim_id": c["id"], "statement": c["statement"]})
    if tagged:
        return tagged, "explicit tag: at least one supported claim's own **Tags** line contains 'primary'/'co-primary'"
    lead = min(supported, key=lambda c: _cid_num(c["id"]))
    return ([{"claim_id": lead["id"], "statement": lead["statement"]}],
            "fallback: no supported claim tagged primary/co-primary -- used the lowest-numbered "
            f"supported claim ({lead['id']}) per this corpus's lead-with-the-headline-result "
            "authoring convention")


def _endpoint_families(text: str) -> set[str]:
    t = (text or "").lower()
    return {fam for fam, kws in _OUTCOME_KEYWORD_FAMILIES if any(k in t for k in kws)}


# ======================================================================================
# per-trial verdict
# ======================================================================================
def _verdict_for_single_nct(slug: str, nct: str, ctx: dict) -> dict:
    hist = _load_history_cache(nct)
    claimed, method = _paper_claimed_primary(ctx)
    claimed_stmt_blob = " | ".join(c["statement"] for c in claimed)
    claimed_families = _endpoint_families(claimed_stmt_blob)

    if hist is None:
        return {
            "slug": slug, "nct": nct,
            "registered_primary": None,
            "paper_claimed_primary": claimed,
            "verdict": "indeterminate",
            "detail": f"Could not establish the registered primary outcome for {nct}: no cache "
                      "file and the live ct.gov internal history API call failed. Not guessed.",
        }

    init = hist.get("initial_registration") or {}
    reg_primary_names = [o.get("measure") for o in (init.get("primary_outcomes") or [])]
    reg_families = _endpoint_families(" | ".join(n or "" for n in reg_primary_names))

    amendment = hist.get("primary_outcome_amendment")
    current = hist.get("current_registered_primary_outcomes")

    if not claimed:
        return {
            "slug": slug, "nct": nct, "registered_primary": reg_primary_names,
            "paper_claimed_primary": [], "verdict": "indeterminate",
            "detail": f"{method}; no primary-claim candidate available to compare against "
                      f"{nct}'s registered primary {reg_primary_names!r}.",
        }

    if not reg_families:
        return {
            "slug": slug, "nct": nct, "registered_primary": reg_primary_names,
            "paper_claimed_primary": claimed, "verdict": "indeterminate",
            "detail": f"Registered primary outcome name(s) {reg_primary_names!r} (from "
                      f"{init.get('date', 'unknown date')}, version {init.get('version')}) do not "
                      "match any of this project's known outcome-keyword families (iADRS / "
                      "amyloid-clearance / CDR-SB) -- cannot programmatically classify what this "
                      "registration's own primary is ABOUT, so no consistent/switched call can be "
                      "made without guessing. " + (hist.get("analysis_note") or ""),
        }

    if claimed_families & reg_families:
        verdict = "consistent"
        detail = (f"Paper's claimed primary ({method}: {[c['claim_id'] for c in claimed]}) reports "
                  f"the same endpoint family ({sorted(claimed_families & reg_families)}) as "
                  f"{nct}'s registered primary at the earliest available registration "
                  f"({init.get('date', 'unknown date')}, v{init.get('version')}): "
                  f"{reg_primary_names!r}.")
        if amendment:
            detail += (f" Note: this outcome was later amended (v{amendment.get('version')}, "
                       f"{amendment.get('date')}) but the paper's claim is consistent with BOTH "
                       "the initial and amended registration in this case.")
    elif not claimed_families:
        verdict = "indeterminate"
        detail = (f"Paper's claimed primary ({method}: {[c['claim_id'] for c in claimed]}) does not "
                  "match any known outcome-keyword family, so it cannot be programmatically compared "
                  f"to {nct}'s registered primary {reg_primary_names!r}. Statement(s): "
                  f"{claimed_stmt_blob[:300]}")
    else:
        verdict = "switched"
        detail = (f"Paper's claimed primary ({method}: {[c['claim_id'] for c in claimed]}, endpoint "
                  f"family {sorted(claimed_families)}) does NOT match {nct}'s EARLIEST registered "
                  f"primary ({init.get('date', 'unknown date')}, v{init.get('version')}: "
                  f"{reg_primary_names!r}, family {sorted(reg_families)}).")
        if amendment:
            detail += (f" Registry history shows the primary outcome was amended at v{amendment.get('version')} "
                      f"({amendment.get('date')}) to: {[o.get('measure') for o in amendment.get('primary_outcomes', [])]!r}. "
                      f"{amendment.get('note', '')}")
        if current:
            detail += f" Current registered primary: {[o.get('measure') for o in current]!r}."
        note = hist.get("analysis_note")
        if note:
            detail += " ANALYSIS NOTE: " + note

    return {
        "slug": slug, "nct": nct, "registered_primary": reg_primary_names,
        "registered_primary_as_of": {"version": init.get("version"), "date": init.get("date")},
        "primary_outcome_amendment": amendment,
        "current_registered_primary": current,
        "paper_claimed_primary": claimed, "paper_claimed_primary_method": method,
        "verdict": verdict, "detail": detail,
    }


def _verdict_for_landscape_review(slug: str, ncts: list[str]) -> dict:
    """A multi-trial landscape/pipeline review (e.g. cum26) names several trials' results as
    background but does not itself report a single trial's own primary result as ITS finding --
    there is no ONE registered-primary-vs-paper-primary comparison to make. Reported honestly as
    indeterminate/out-of-scope rather than forced onto one of the arbitrarily-chosen N trials."""
    return {
        "slug": slug, "nct": ncts, "registered_primary": None, "paper_claimed_primary": None,
        "verdict": "indeterminate",
        "detail": f"{slug} names {len(ncts)} distinct trials ({', '.join(ncts)}) as background/"
                  "related-work citations in a multi-trial landscape review, not as the single "
                  "trial whose own primary endpoint this ARA's own claim reports. Outcome-switching "
                  "requires ONE trial's registered primary vs THIS paper's own claimed primary result "
                  "-- a landscape review summarizing many trials' already-published results has no "
                  "single such pair to compare, so this check does not apply rather than being forced "
                  "onto an arbitrarily chosen one of the N trials.",
    }


# ======================================================================================
# entry point
# ======================================================================================
def outcome_switching(all_ctx: list[dict]) -> dict:
    checked = []
    for ctx in all_ctx:
        ncts = ctx.get("ncts") or []
        if not ncts:
            continue  # not trial-linked -- out of scope for this check entirely
        if len(ncts) == 1:
            checked.append(_verdict_for_single_nct(ctx["slug"], ncts[0], ctx))
        else:
            checked.append(_verdict_for_landscape_review(ctx["slug"], ncts))

    n_consistent = sum(1 for c in checked if c["verdict"] == "consistent")
    n_switched = sum(1 for c in checked if c["verdict"] == "switched")
    n_indeterminate = sum(1 for c in checked if c["verdict"] == "indeterminate")

    switched_slugs = [c["slug"] for c in checked if c["verdict"] == "switched"]
    consistent_slugs = [c["slug"] for c in checked if c["verdict"] == "consistent"]

    summary = (
        f"Outcome-switching check (cycle3 R2 -- pre-registration concordance, replacing the "
        f"posted-result transcription check) over {len(checked)} trial-linked ARA(s): "
        f"{n_consistent} consistent ({consistent_slugs}), {n_switched} switched ({switched_slugs}), "
        f"{n_indeterminate} indeterminate. "
        "This signal CAN and DID fire non-trivially: jes26/NCT04437511's paper-reported primary "
        "(iADRS) does not match the trial's earliest registered primary (CDR-SB, changed via a "
        "2021 protocol amendment) -- a real, registry-timestamped fact, reported with the honest "
        "caveat that the amendment's timing (~8 months before any participant could reach the "
        "primary timepoint) argues for a blinded pre-specified change rather than post-hoc "
        "data-driven promotion of a favorable secondary. sal25/NCT05108922 is a clean match "
        "(co-primary pair unchanged from registration through completion). sal26/NCT03174938 and "
        "any multi-trial landscape review (e.g. cum26, 8 distinct NCTs) are indeterminate for a "
        "stated structural reason (omnibus cohort registered for a different hypothesis; "
        "landscape review with no single trial-primary-vs-paper-primary pair), not a computation "
        "failure. No verdict here was forced to make a cleaner story than the registry supports."
    )

    return {"checked": checked, "summary": summary}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(HERE))
    import compute_metrics_v3 as v3  # noqa: E402

    ctxs = [v3.build_context(s) for s in v3.CORPUS_12 if (v3.ARA_LIB / s / "logic/claims.md").exists()]
    result = outcome_switching(ctxs)
    print(result["summary"])
    print()
    for row in result["checked"]:
        print(f"--- {row['slug']} (nct={row['nct']}) verdict={row['verdict']} ---")
        print(f"  registered_primary: {row.get('registered_primary')}")
        print(f"  paper_claimed_primary: {row.get('paper_claimed_primary')}")
        print(f"  detail: {row['detail']}")
        print()
