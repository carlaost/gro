#!/usr/bin/env python3
"""
V3 P5 — claim_graph.py: the claim-level, EXTERNALLY-ANCHORED successor the metascientist critique
(research/metrics/v3/critiques/cycle1.md, P3+P5, section F) asks for.

The critique's core complaint: V3 ranks PAPERS on the compiler's output. Every signal in
compute_metrics_v3.py / detectors.py / grounding.py / sem_metrics.py is computed over text the
compiler wrote, so the thing being optimized is "does this ARA's compiler prompt produce numbers
that score well" — not "is this good science." Section F names the fix: make the CLAIM the unit,
and anchor it to ground truth a compiler CANNOT fake — a curated external database (ChEMBL), a
public trial registry's own posted results (ClinicalTrials.gov), and the pre-existing literature
(PubMed). This module is that fix. It does NOT rank papers and does NOT feed compute_metrics_v3's
paper_rankers/artifact_trust axes — it is a separate, additive claim-graph layer, exactly as P5
specifies. It does not duplicate library_graph.py's D5 deterministic proxies (shared-trial
clusters, citation-reuse edges, raw pairwise claim-redundancy, the oshima FOL spike) — this module
is the richer claim-level layer library_graph.py's own docstring says the FOL half was reaching for
before the oshima pipeline turned out to be a missing-source-code gap (see library_graph.py's
_spike_oshima detail). FOL is still unavailable here for the same reason; this module gets
corroboration WITHOUT FOL by using a deterministic TF-IDF cosine over claim statements instead —
a stated, inspectable substitute, not a fabricated logic layer.

Three things this module does that nothing else in v3 does:

  1. CROSS-ARA CLAIM CLUSTERING (corroboration). FOL is unavailable (see library_graph.py's
     _spike_oshima — the oshima nlp2fol pipeline is missing 12 of ~15 required submodules and the
     entire SUMO/WordNet ontology subpackage; this is a missing-source-code gap, not something this
     module can build without fabricating the logic layer). Deterministic substitute: TF-IDF
     cosine similarity over claim statements (stopword-filtered, alpha-token-only so shared p-values
     and CIs don't manufacture false similarity), corpus-wide IDF over all ~101 claims in the 12-ARA
     set, union-find clustering at a STATED threshold (cosine >= 0.30, chosen by inspecting the
     actual pairwise-similarity distribution on this corpus — see `SIM_THRESHOLD` below and the
     module-level report). A cluster spanning >=2 distinct ARAs is a corroboration signal: N
     independent papers asserting an equivalent claim. Honest expectation stated up front (matches
     compiler-model.md's predicted outcome for a single-topic n=12 corpus): thin. This corpus is a
     single-topic (Alzheimer's biomarkers/donanemab) literature review-scale sample, not an
     independent-discovery sample, so most claims are either genre-specific (unique study designs)
     or so numerically dense that lexical overlap is naturally low even between topically-related
     claims. Report the number honestly; do not manufacture clusters by lowering the threshold.

  2. EXTERNAL ANCHORING PER CLAIM — the Goodhart-resistant part; the thing earlier V3 versions
     (external.py, RC2) did only at the ARA level, and only against ClinicalTrials.gov:
       (a) ChEMBL target/compound resolvability — does the entity a claim is ABOUT (a drug or a
           gene/protein target) exist in a curated external database at all? A claim about a
           fabricated or mis-named entity fails here regardless of how well the compiler wrote it.
       (b) ClinicalTrials.gov per-CLAIM endpoint concordance — extends external.py's per-ARA
           concordance (which concatenates all headline claims into one blob) down to the
           individual claim: does THIS claim's own stated number match a value the registry itself
           posted for a REGISTERED PRIMARY outcome the claim's own text names?
       (c) PubMed prior-literature check for claims flagged "novel" — does literature that predates
           this ARA's own publication already report the same finding? This is the one axis that
           can catch a real over-claim (a paper/compiler calling something "first" or "novel" when
           it is not), which no compiler-fidelity check (grounding, evidence_relevance, ...) can
           ever catch, because the compiler is by construction only checked against the paper's OWN
           text — it has no way to know what the rest of the literature already said.

  3. Everything degrades to "pending" with a stated reason if a cache miss + live call both fail —
     per the project-wide contract (compiler-model.md, external.py's own docstring): NEVER fabricate
     a resolution, a concordance label, or a novelty verdict.

WHY THIS RUNS FROM A CACHE, NOT LIVE MCP CALLS AT RUNTIME
----------------------------------------------------------
The ChEMBL / Clinical Trials / PubMed / bioRxiv MCP tools used to build this module are available
to the AGENT that authored it (via ToolSearch), but are NOT importable from a plain Python process
— there is no `import mcp_chembl` a script can call. So, exactly like external.py's own documented
pattern (REST fallback + `external_cache/`), this module is CACHE-FIRST: the raw MCP responses used
to build the anchors below were captured once (by the agent, live, during this module's
construction) and frozen under `external_cache/` as JSON. At runtime this module (a) reads the
cache if present, (b) falls back to the public REST equivalent of each service via urllib if the
cache is absent and the network is reachable, (c) reports "pending" with a stated reason if
neither is available. No anchor is ever fabricated to fill a gap.

Cache files this module reads (all under research/metrics/v3/external_cache/, this session):
  chembl_compound_{donanemab,aducanumab}.json      — ChEMBL compound_search, verbatim (trimmed of
                                                       null/None boilerplate fields only)
  chembl_mechanism_{donanemab,aducanumab}.json     — ChEMBL get_mechanism, verbatim
  chembl_target_{MAPT,APP}.json                    — ChEMBL target_search, FILTERED to
                                                       organism=="Homo sapiens" + only the fields
                                                       this module needs (id/name/type/gene) — the
                                                       full raw responses were 315KB (MAPT) / 53KB
                                                       (APP), ~99% GO/Reactome/PDB cross-reference
                                                       metadata irrelevant to resolvability; each
                                                       cache file states the full count and how to
                                                       re-fetch the untrimmed response.
  chembl_target_{APOE,GFAP}_unresolved.json        — every query variant tried (gene_symbol AND
                                                       target_name, both organism-filtered and not)
                                                       and its (negative) result, verbatim — so a
                                                       "not resolved" verdict is auditable, not just
                                                       asserted.
  clinicaltrials_mcp_NCT{04437511,05108922,03174938}.json
                                                    — Clinical_Trials MCP get_trial_details,
                                                       trimmed of the bulky `locations` array
                                                       (30+ site addresses, no metric content).
  NCT*.json (11 files)                             — PRE-EXISTING cache from external.py's own REST
                                                       fetch of the ClinicalTrials.gov v2 API
                                                       (resultsSection with posted PRIMARY-outcome
                                                       numbers). This module READS these read-only;
                                                       it does not refetch or duplicate external.py.
  pubmed_novelty_searches.json                     — PubMed search_articles results for the 10
                                                       "novel"-flagged claims investigated, WITH a
                                                       documented methodology finding: the tool's
                                                       date_to filter did not reliably exclude
                                                       post-cutoff results in this environment (see
                                                       the the25 entry) — every candidate hit was
                                                       independently re-verified against its own
                                                       get_article_metadata publication_date before
                                                       being treated as "prior," never trusting
                                                       date_to alone.
  pubmed_article_metadata.json                     — get_article_metadata for every PMID surfaced
                                                       above (title/DOI/pub_date), used to exclude
                                                       self-matches (an ARA's own paper indexed by
                                                       PubMed/bioRxiv matching its own DOI) and to
                                                       classify prior vs. subsequent.

bioRxiv note: the bioRxiv MCP's search_preprints tool supports ONLY date-range/category filtering,
NOT keyword/full-text search (per its own tool description) — so it cannot do a targeted
novelty-precedent search the way PubMed's search_articles can. get_preprint (single-DOI lookup)
requires already knowing the candidate DOI, which defeats the purpose of a *search*. This is
reported as a real tool-capability gap in the summary, not silently worked around.

CYCLE-2 METASCIENTIST FIXES (research/metrics/v3/critiques/cycle2.md, C4/C5/C6)
--------------------------------------------------------------------------------
Three corrections applied on top of the above, after the round-2 critique found two of the three
external anchors mislabeled and the third under-scoped:

  C4 — RECLASSIFY TWO MISLABELED ANCHORS (honesty, not new data):
    (a) ChEMBL resolvability is NOT a science-quality signal. ~96% of entities resolve regardless of
        paper quality (non-discriminating by construction) and it only ever fires on a hallucinated
        or mis-named entity — that makes it a FABRICATION/fidelity check, not a science signal. Its
        output now carries `axis: "trust_fabrication_check"`. Non-resolution is marked
        `db_coverage_artifact: true` and is NEVER treated as evidence against a claim's science: ChEMBL
        is a bioactivity database, so a legitimate genetics/biomarker target with no small-molecule
        ligand program (APOE, GFAP) will not resolve regardless of how sound the underlying science is.
    (b) TF-IDF corroboration at single-topic n=12 cannot establish independence — e.g. the jes26+sal25
        cluster is the SAME donanemab TRAILBLAZER trial family measured twice, not two independent
        discoveries. Corroboration output now carries `status: "exploratory"` with an explicit
        independence-unestablished note; it is not presented as a validated replication signal.

  C6 — MAKE NOVELTY COMPUTABLE: the PubMed `date_to` filter proved unreliable (it returned
    post-cutoff articles even when a cutoff was set), so prior-vs-subsequent used to require a human
    to read each candidate's date by hand. This build replaces that with a real comparator:
    `_ara_confirmed_pub_date()` gets each ARA's own publication date from a live PubMed self-match in
    the metadata cache if one exists, else from PAPER.md's structured `year:` frontmatter — NEVER the
    slug's `YY` (which this build's own audit trail shows can be wrong: woj25's slug says "25" but its
    DOI string embeds "024" and its PubMed-confirmed publication_date is 2025-01-02 — only a live
    metadata call is trustworthy). `_compare_dates()` then orders each candidate's own
    get_article_metadata publication_date against that confirmed date at whatever precision both sides
    actually have (year, then month, then day) and refuses to guess past that precision — an
    inconclusive comparison is labeled `manual_review`, never silently resolved either way.

  C5 — CLOSE THE NOVELTY SCOPE DODGE: the novelty check used to run ONLY on claims the within-ARA
    [sem] judge had already tagged `novelty.verdict == "novel"` — so a paper could dodge the entire
    check by simply never using the word "novel"/"first". `_all_testable_headline_claims()` now
    supplies the candidate pool: every claim whose own status starts with "supported" (i.e. was
    actually tested against evidence, not a bare "hypothesis"), regardless of what the [sem] judge's
    novelty tag said. Coverage is reported honestly as checked/total, and an `overclaim_risk` flag is
    only set when prior literature was found for a claim that EITHER the [sem] judge tagged novel OR
    whose own statement text uses priority language ("first", "highest", "only study to", ...) — so
    the metric doesn't fabricate a stance on claims that never asserted priority in the first place.

Interface (frozen for the spine, though the spine does not currently call this module — see
compute_metrics_v3.py's module-loading section if wiring it in later):
  claim_graph(all_ctx: list[dict]) -> {
    "clusters": [...], "corroboration": [...],
    "external_anchors": {"chembl": [...], "trials": [...], "novelty": [...]},
    "summary": str,
  }
`all_ctx` = the list of per-ARA ctx dicts built by compute_metrics_v3.build_context (each has
ctx["claims"] with .id/.statement, ctx["ncts"], ctx["sources"], ctx["slug"], ctx["genre"]).
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
SEM_FINDINGS_DIR = HERE / "sem_findings"
USER_AGENT = "ara-metrics-v3-claim-graph/1.0 (research corpus P5 harness; non-commercial)"


# ======================================================================================
# (1) CROSS-ARA CLAIM CLUSTERING — deterministic TF-IDF cosine (FOL substitute)
# ======================================================================================
STOPWORDS = set("""
a an the of in on at to for and or with without between across among into onto from by as is are
was were be been being this that these those it its their his her they he she we you i not no
than then so such more most less least which who whom whose what when where why how per over
under after before during study studies population participants participant compared comparison
group groups baseline including based used using significant significantly higher lower greater
across among all both each also than versus vs result results reported showed shows show found
finding findings ci 95 ratio rate rates value values p compared with without within among between
""".split())

SIM_THRESHOLD = 0.30  # stated threshold; chosen by inspecting the full pairwise-similarity
                       # distribution on this corpus (~101 claims): scores above ~0.30 are true
                       # same-finding matches (e.g. two independent donanemab trials' identical
                       # "no ARIA-related deaths" safety claim); scores in 0.15-0.30 are real but
                       # weaker topical overlap (same biomarker family, different specific
                       # assertion) that would over-merge distinct claims into one cluster if
                       # included. Lowering this threshold to manufacture more clusters would be
                       # exactly the kind of metric-gaming this module exists to avoid.


def _tokenize(statement: str) -> list[str]:
    toks = re.findall(r"[a-z][a-z\-]{2,}", (statement or "").lower())
    return [t for t in toks if t not in STOPWORDS]


def _tfidf_vectors(claims: list[dict]) -> None:
    """In-place: sets claims[i]['_vec'] = {token: tfidf weight}. IDF computed corpus-wide."""
    n = len(claims)
    df: dict[str, int] = {}
    for c in claims:
        for t in set(c["_toks"]):
            df[t] = df.get(t, 0) + 1
    for c in claims:
        tf: dict[str, int] = {}
        for t in c["_toks"]:
            tf[t] = tf.get(t, 0) + 1
        vec = {}
        for t, f in tf.items():
            idf = math.log((n + 1) / (df.get(t, 0) + 1)) + 1.0
            vec[t] = f * idf
        c["_vec"] = vec


def _cosine(v1: dict, v2: dict) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    num = sum(v1[t] * v2[t] for t in common)
    d1 = math.sqrt(sum(x * x for x in v1.values()))
    d2 = math.sqrt(sum(x * x for x in v2.values()))
    if d1 == 0 or d2 == 0:
        return 0.0
    return num / (d1 * d2)


class _UnionFind:
    def __init__(self, keys):
        self.parent = {k: k for k in keys}

    def find(self, k):
        while self.parent[k] != k:
            self.parent[k] = self.parent[self.parent[k]]
            k = self.parent[k]
        return k

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def cluster_claims(all_ctx: list[dict]) -> dict:
    """TF-IDF cosine clustering over every claim statement in every ARA. Returns all clusters
    (including singletons, for transparency) and the subset that are cross-ARA corroboration
    (n_papers >= 2), sorted by size."""
    claims = []
    for ctx in all_ctx:
        slug = ctx["slug"]
        for c in ctx.get("claims", []) or []:
            stmt = c.get("statement", "")
            if not stmt:
                continue
            key = f"{slug}:{c.get('id')}"
            claims.append({"key": key, "slug": slug, "id": c.get("id"), "statement": stmt,
                            "_toks": _tokenize(stmt)})
    if not claims:
        return {"clusters": [], "corroboration": [], "n_claims": 0, "n_pairs_above_threshold": 0,
                "threshold": SIM_THRESHOLD}

    _tfidf_vectors(claims)
    by_key = {c["key"]: c for c in claims}
    uf = _UnionFind(by_key.keys())

    edges = []
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            a, b = claims[i], claims[j]
            if a["slug"] == b["slug"]:
                continue  # within-paper redundancy is library_graph.py's claim_redundancy, not this
            sim = _cosine(a["_vec"], b["_vec"])
            if sim >= SIM_THRESHOLD:
                edges.append((round(sim, 3), a["key"], b["key"]))
                uf.union(a["key"], b["key"])

    groups: dict[str, list[str]] = {}
    for key in by_key:
        groups.setdefault(uf.find(key), []).append(key)

    clusters = []
    for members in groups.values():
        if len(members) < 2:
            continue  # singleton, not a cluster
        slugs = sorted({m.split(":")[0] for m in members})
        member_edges = [e for e in edges if e[1] in members or e[2] in members]
        clusters.append({
            "members": [{"key": m, "statement": by_key[m]["statement"]} for m in sorted(members)],
            "n_papers": len(slugs), "papers": slugs,
            "max_similarity": max((e[0] for e in member_edges), default=0.0),
            "edges": [{"a": e[1], "b": e[2], "cosine": e[0]} for e in sorted(member_edges, key=lambda e: -e[0])],
        })
    clusters.sort(key=lambda c: (-c["n_papers"], -c["max_similarity"]))

    # C4(b): TF-IDF corroboration at single-topic n=12 cannot establish independence (e.g. the
    # jes26+sal25 "cluster" is the same donanemab TRAILBLAZER trial family measured twice, not
    # independent replication) -- every cluster carries an explicit exploratory status + note, never
    # presented as a validated corroboration/replication signal.
    INDEPENDENCE_NOTE = (
        "EXPLORATORY, NOT VALIDATED: TF-IDF cosine overlap at single-topic n=12 cannot establish "
        "independence between papers. A shared-topic cluster may simply be the same underlying trial "
        "or dataset reported by more than one paper (e.g. a donanemab-trial safety claim reported by "
        "two papers both drawing on the TRAILBLAZER program), not two independent groups converging on "
        "the same finding. Do not treat cluster size or max_similarity as a corroboration/replication "
        "score (cycle2 critique C4)."
    )
    corroboration = [
        {"claim_group": [m["key"] for m in c["members"]], "n_papers": c["n_papers"],
         "papers": c["papers"], "max_similarity": c["max_similarity"],
         "status": "exploratory", "independence_note": INDEPENDENCE_NOTE,
         "representative_statements": [m["statement"] for m in c["members"][:2]]}
        for c in clusters if c["n_papers"] >= 2
    ]

    return {"clusters": clusters, "corroboration": corroboration, "n_claims": len(claims),
            "n_pairs_above_threshold": len(edges), "threshold": SIM_THRESHOLD}


# ======================================================================================
# (2a) ChEMBL target/compound resolvability per claim
# ======================================================================================
# Deterministic entity detection: a fixed, auditable regex list built from a corpus-wide grep of
# every claims.md in the 12-ARA set (not invented) -- see the module's construction notes. Each
# entry maps a canonical entity name -> (regex, kind, chembl cache key).
ENTITY_PATTERNS = [
    ("donanemab",   re.compile(r"\bdonanemab\b", re.I),                    "drug",   "chembl_compound_donanemab.json"),
    ("aducanumab",  re.compile(r"\baducanumab\b", re.I),                   "drug",   "chembl_compound_aducanumab.json"),
    ("MAPT (tau)",  re.compile(r"\bMAPT\b|p-tau ?2?1?7|p-tau ?181|p-tau ?231|p-tau ?205|p-tau ?212|phosphorylated tau", re.I), "target", "chembl_target_MAPT.json"),
    ("APP (amyloid-beta)", re.compile(r"amyloid[- ]?beta|\bAPP\b(?!\w)|amyloid plaque", re.I), "target", "chembl_target_APP.json"),
    ("APOE",        re.compile(r"\bAPOE\b", re.I),                         "target", "chembl_target_APOE_unresolved.json"),
    ("GFAP",        re.compile(r"\bGFAP\b", re.I),                         "target", "chembl_target_GFAP_unresolved.json"),
]

CHEMBL_REST_MOLECULE = "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json?q={q}"
CHEMBL_REST_TARGET = "https://www.ebi.ac.uk/chembl/api/data/target/search.json?q={q}"


def _http_get_json(url: str, timeout: float = 10.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https hosts only)
        return json.loads(resp.read().decode("utf-8"))


def _chembl_cache_or_live(entity: str, kind: str, cache_file: str) -> dict:
    path = CACHE_DIR / cache_file
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_source"] = f"cache:{cache_file}"
            return data
        except Exception:
            pass
    # live REST fallback (public ChEMBL REST API, no auth) -- only reached on a cache miss
    try:
        url = (CHEMBL_REST_MOLECULE if kind == "drug" else CHEMBL_REST_TARGET).format(
            q=urllib.request.quote(entity))
        data = _http_get_json(url)
        data["_source"] = "live_rest_fallback"
        return data
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError) as e:
        return {"_source": "unreachable", "_error": f"{type(e).__name__}: {e}"}



# C4(a): ChEMBL resolvability is a FABRICATION/fidelity check (trust axis), NOT a science-quality
# signal -- ~96% of entities resolve regardless of paper quality (non-discriminating by construction)
# and it only ever fires on a hallucinated/mis-named entity. Every result below carries this axis
# label. Non-resolution is marked `db_coverage_artifact: true` and MUST NEVER be read as evidence
# against a claim's science: ChEMBL is a curated bioactivity database, so a legitimate genetics/
# biomarker target with no small-molecule ligand program (APOE, GFAP) will not resolve regardless of
# how sound the underlying science is -- it would systematically penalize exactly the non-druggable-
# target biomarker/genetics papers if ever weighted into a score.
_AXIS = "trust_fabrication_check"
_DB_COVERAGE_NOTE = (
    "NOT an over-claim signal: ChEMBL is a curated bioactivity database, not a general knowledge base. "
    "Absence here reflects database coverage (no small-molecule/ligand program exists for this target), "
    "not a fabricated or mis-named entity. Never score this against a claim's science content."
)


def _resolvability_from_cache(entity: str, kind: str, cached: dict) -> dict:
    src = cached.get("_source", "unknown")
    if src == "unreachable":
        return {"axis": _AXIS, "resolved": "pending", "detail": f"ChEMBL unreachable: {cached.get('_error')}"}
    if "unresolved" in src or "queries_tried" in cached:
        return {"axis": _AXIS, "resolved": False, "db_coverage_artifact": True,
                "detail": cached.get("conclusion", "not resolved") + " " + _DB_COVERAGE_NOTE,
                "queries_tried": cached.get("queries_tried")}
    if kind == "drug":
        compounds = cached.get("compounds", [])
        if not compounds:
            return {"axis": _AXIS, "resolved": False, "db_coverage_artifact": True,
                     "detail": "ChEMBL compound_search returned zero hits. " + _DB_COVERAGE_NOTE}
        c = compounds[0]
        return {"axis": _AXIS, "resolved": True, "chembl_id": c.get("molecule_chembl_id"),
                "pref_name": c.get("pref_name"), "max_phase": c.get("max_phase"),
                "detail": f"resolved to {c.get('molecule_chembl_id')} ({c.get('pref_name')}), "
                           f"max_phase={c.get('max_phase')} (4=approved)."}
    # target
    targets = cached.get("targets_homo_sapiens") or cached.get("targets", [])
    single = [t for t in targets if t.get("target_type") == "SINGLE PROTEIN"]
    pick = single[0] if single else (targets[0] if targets else None)
    if not pick:
        return {"axis": _AXIS, "resolved": False, "db_coverage_artifact": True,
                 "detail": "ChEMBL target_search returned zero Homo sapiens hits. " + _DB_COVERAGE_NOTE}
    return {"axis": _AXIS, "resolved": True, "chembl_id": pick.get("target_chembl_id"),
            "pref_name": pick.get("pref_name"), "target_type": pick.get("target_type"),
            "detail": f"resolved to {pick.get('target_chembl_id')} ({pick.get('pref_name')}, "
                       f"{pick.get('target_type')})."}


_MECHANISM_CACHE = {
    "donanemab": "chembl_mechanism_donanemab.json",
    "aducanumab": "chembl_mechanism_aducanumab.json",
}


def _mechanism_for(entity: str) -> dict | None:
    fname = _MECHANISM_CACHE.get(entity)
    if not fname:
        return None
    path = CACHE_DIR / fname
    if not path.exists():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        mechs = d.get("mechanisms", [])
        if not mechs:
            return None
        m = mechs[0]
        return {"mechanism_of_action": m.get("mechanism_of_action"), "target_chembl_id": m.get("target_chembl_id"),
                "action_type": m.get("action_type"), "disease_efficacy": m.get("disease_efficacy")}
    except Exception:
        return None


def target_compound_resolvability(all_ctx: list[dict]) -> list[dict]:
    """Per-claim: which drug/target entities does this claim name, and do they resolve in ChEMBL?
    This is the metric earlier V3 versions skipped entirely (library_graph.py's D5 is zeros; no
    other module in v3 touches a curated external database)."""
    resolved_cache: dict[str, dict] = {}
    out = []
    for ctx in all_ctx:
        slug = ctx["slug"]
        for c in ctx.get("claims", []) or []:
            stmt = c.get("statement", "")
            hits = [(name, kind, cache_file) for name, pat, kind, cache_file in ENTITY_PATTERNS
                    if pat.search(stmt)]
            if not hits:
                continue
            entity_results = []
            for name, kind, cache_file in hits:
                if cache_file not in resolved_cache:
                    raw = _chembl_cache_or_live(name, kind, cache_file)
                    resolved_cache[cache_file] = _resolvability_from_cache(name, kind, raw)
                res = dict(resolved_cache[cache_file])
                res["entity"] = name
                res["kind"] = kind
                if kind == "drug":
                    mech = _mechanism_for(name.split()[0].lower())
                    if mech:
                        res["mechanism"] = mech
                entity_results.append(res)
            out.append({"slug": slug, "claim_id": c.get("id"), "entities": entity_results})
    return out


# ======================================================================================
# (2b) ClinicalTrials.gov per-CLAIM endpoint concordance
# ======================================================================================
NUM_RE = re.compile(r"-?\d+\.\d+|-?\d+")


def _numbers_in(text: str) -> list[float]:
    norm = (text or "")
    for d in ("−", "–", "—"):  # unicode minus, en dash, em dash -> ascii '-'
        norm = norm.replace(d, "-")
    out = []
    for m in NUM_RE.findall(norm):
        try:
            out.append(float(m))
        except ValueError:
            continue
    return out


_RATIO_PAREN_RE = re.compile(r"[\(\[]\s*\d+\s*/\s*\d+\s*[\)\]]")


def _claim_number_candidates(text: str) -> list[float]:
    """Numbers in a claim statement that are plausible matches for a registered outcome's own
    posted value, with "(25/66)"/"[42/60]"-style sample-size ratio parentheticals stripped out
    FIRST. Without this, a claim like sal25 C03's "70.0% [42/60] vs 24.6% [15/61]" can spuriously
    "match" an unrelated registered value (e.g. sample size 42 falling within numeric tolerance of
    a registered 38.5) purely by coincidence -- the denominator/numerator counts are not the effect
    estimate the registered outcome reports. Everything else (percentages, raw scale points like
    iADRS, CIs) is kept, since registered outcomes in this corpus span both percentage measures
    (amyloid clearance) and non-percentage scale measures (iADRS points) -- restricting to
    %-tagged numbers only would incorrectly drop the latter."""
    cleaned = _RATIO_PAREN_RE.sub(" ", text or "")
    return _numbers_in(cleaned)


def _load_nct_results_cache(nct: str) -> dict | None:
    """Read-only: the ClinicalTrials.gov v2 REST cache external.py already fetched and froze under
    external_cache/<nct>.json. This module does not refetch it. Falls back to a live REST call
    only if that cache is somehow absent (e.g. a new NCT not in the RC2 set)."""
    path = CACHE_DIR / f"{nct}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        return _http_get_json(f"https://clinicaltrials.gov/api/v2/studies/{nct}?format=json")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return None


def _registered_primary_outcomes(study: dict) -> list[dict]:
    """Registered PRIMARY outcome measure NAMEs (protocol) + posted numeric group values
    (resultsSection), keyed by outcome title, for a study with hasResults=True."""
    proto = study.get("protocolSection", {}) or {}
    reg_names = [o.get("measure") for o in proto.get("outcomesModule", {}).get("primaryOutcomes", []) or []]
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
                        values[groups.get(m.get("groupId"), m.get("groupId"))] = float(m.get("value"))
                    except (TypeError, ValueError):
                        continue
        out.append({"title": om.get("title"), "values": values, "registered_primary_names": reg_names})
    return out


# Keyword families used to link a claim's own text to a registered outcome's measure name, without
# hardcoding claim IDs -- the same words the outcome measure and the claim's own prose would both
# plausibly use.
_OUTCOME_KEYWORD_FAMILIES = [
    ("iadrs", ["iadrs", "integrated alzheimer"]),
    ("amyloid_clearance", ["amyloid plaque clearance", "ap clearance", "amyloid clearance"]),
    ("cdr_sb", ["cdr-sb", "cdr sb", "clinical dementia rating"]),
]


def _population_scope(text: str) -> str | None:
    """Detect which trial (sub)population a claim or a registered-outcome title is scoped to, so a
    claim explicitly about one arm/subpopulation isn't credited as 'concordant' with a DIFFERENT
    subpopulation's registered value just because the two numbers happen to be numerically close
    (e.g. sal25's 'overall population' 37.9% vs its own 'low-medium tau subpopulation' 38.5% --
    two real, different, both-legitimate registered values from the same co-primary design)."""
    t = (text or "").lower()
    if re.search(r"low[/\-\s]?medium|intermediate.*tau|low.medium tau", t):
        return "low_medium_tau"
    if "overall population" in t or "overall" in t:
        return "overall"
    return None


_WINDOW = 90  # chars either side of the matched keyword, for extracting THIS endpoint's own numbers


def _claim_links_to_outcome(claim_stmt: str, outcome_title: str, outcome_scope: str | None) -> tuple[bool, str | None]:
    """Returns (linked, local_window) -- local_window is the text immediately around the matched
    keyword, used to pull numbers FROM THAT LOCAL CONTEXT rather than the whole claim statement.
    Without this, a claim that merely MENTIONS an outcome's topic in a subordinate clause (e.g.
    sal25 C07: "Despite greater and faster amyloid clearance with donanemab, ARIA incidence was
    not increased...") would pull in unrelated numbers from elsewhere in the sentence (here, ARIA
    safety percentages) and spuriously "match" the amyloid-clearance registered value by
    coincidence. Restricting to a window around the actual keyword occurrence keeps the numeric
    check tied to what the claim is actually reporting AT that mention, not anywhere in the claim."""
    stmt_l, title_l = claim_stmt.lower(), outcome_title.lower()
    window = None
    for _fam, kws in _OUTCOME_KEYWORD_FAMILIES:
        if not any(k in title_l for k in kws):
            continue
        for k in kws:
            idx = stmt_l.find(k)
            if idx != -1:
                start, end = max(0, idx - _WINDOW), min(len(claim_stmt), idx + len(k) + _WINDOW)
                window = claim_stmt[start:end]
                break
        if window is not None:
            break
    if window is None:
        return False, None
    claim_scope = _population_scope(claim_stmt)
    if claim_scope is not None and outcome_scope is not None and claim_scope != outcome_scope:
        return False, None  # explicit scope mismatch -- don't credit cross-subpopulation "concordance"
    return True, window


def per_claim_trial_concordance(all_ctx: list[dict]) -> list[dict]:
    """Extends external.py's per-ARA (all-claims-concatenated) ClinicalTrials concordance down to
    the individual claim: for each claim whose own text names a registered PRIMARY outcome (by
    keyword family), compare the claim's OWN numbers (not the whole ARA's headline blob) against
    the registry's posted value for that outcome, at the same numeric tolerance external.py uses
    (max(0.5, 10%))."""
    out = []
    for ctx in all_ctx:
        slug = ctx["slug"]
        ncts = ctx.get("ncts") or []
        if not ncts:
            continue
        for nct in ncts:
            study = _load_nct_results_cache(nct)
            if study is None:
                out.append({"slug": slug, "nct": nct, "claim_id": None, "label": "pending",
                             "detail": "registry unreachable (no cache, REST fallback failed)."})
                continue
            has_results = bool(study.get("hasResults"))
            if not has_results:
                out.append({"slug": slug, "nct": nct, "claim_id": None, "label": "not_applicable",
                             "detail": f"registry hasResults=False for {nct} -- no posted PRIMARY "
                                        "results exist yet to check any claim against."})
                continue
            reg_outcomes = _registered_primary_outcomes(study)
            if not reg_outcomes:
                continue
            # scope each registered outcome by its own title; if exactly one outcome in a
            # co-primary pair carries an explicit subpopulation marker and the other doesn't, the
            # unmarked one is the "overall" arm by elimination (title text alone doesn't always say
            # "overall" explicitly -- see sal25/NCT05108922's own outcome titles).
            for ro in reg_outcomes:
                ro["_scope"] = _population_scope(ro["title"])
            marked = [ro for ro in reg_outcomes if ro["_scope"] is not None]
            unmarked = [ro for ro in reg_outcomes if ro["_scope"] is None]
            if marked and unmarked and len(reg_outcomes) > 1:
                for ro in unmarked:
                    ro["_scope"] = "overall"
            any_linked = False
            for c in ctx.get("claims", []) or []:
                stmt = c.get("statement", "")
                for ro in reg_outcomes:
                    linked, window = _claim_links_to_outcome(stmt, ro["title"], ro["_scope"])
                    if not linked:
                        continue
                    any_linked = True
                    claim_nums = _claim_number_candidates(window)
                    matched, total, detail_matches = 0, 0, []
                    for group, val in ro["values"].items():
                        total += 1
                        tol = max(0.5, abs(val) * 0.10)
                        hit = any(abs(val - cn) <= tol for cn in claim_nums)
                        matched += hit
                        detail_matches.append({"group": group, "registered_value": val, "matched": hit})
                    label = "concordant" if total and matched / total >= 0.5 else "neutral"
                    out.append({
                        "slug": slug, "nct": nct, "claim_id": c.get("id"), "label": label,
                        "registered_outcome": ro["title"], "matches": detail_matches,
                        "detail": f"claim {c.get('id')} names the registered outcome "
                                   f"{ro['title']!r} ({matched}/{total} posted group values "
                                   f"reproduced within tolerance in this claim's OWN statement, "
                                   f"not the ARA's whole headline-claim blob -- per-claim, not "
                                   f"per-ARA, concordance).",
                    })
            if not any_linked:
                out.append({"slug": slug, "nct": nct, "claim_id": None, "label": "not_applicable",
                             "detail": f"{nct} has posted PRIMARY results, but no claim in this ARA's "
                                        "own text names the registered outcome by any known keyword "
                                        "family (e.g. this ARA's claims may report a SECONDARY "
                                        "outcome, or a different population's version of the "
                                        "endpoint) -- not scored as concordant or discordant."})
    return out


# ======================================================================================
# (2c) PubMed novelty-vs-prior-literature per claim
# ======================================================================================
PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={q}"
ARA_LIB_DIR = HERE.parent.parent / "ara-library"

# C5: priority language a claim can use to assert primacy WITHOUT the within-ARA [sem] judge ever
# tagging it novelty.verdict=="novel" -- checked against the claim's own statement text so the
# overclaim_risk flag doesn't depend solely on the compiler-adjacent [sem] tag it exists to double-check.
PRIORITY_LANGUAGE_RE = re.compile(
    r"\bfirst\b|\bnovel\b|\bunprecedented\b|\bonly (study|trial|paper|report)\b|\bno (other|prior)\b|"
    r"\bfor the first time\b|\bhighest\b|\blargest\b|\bgreatest\b|\bsuperior to (all|every)\b|"
    r"\bnew(ly)? (identified|discovered|described)\b|\bnever (before )?reported\b",
    re.I,
)

# A pre-existing hand-written cache `note` that already flagged a date-prior candidate as topically
# irrelevant (a human already did the relevance judgment call this module cannot automate) downgrades
# an otherwise-computed "prior" hit to manual_review instead of silently overriding that human read.
_WEAK_RELEVANCE_MARKERS = ("false positive", "not a real precedent", "different finding", "tangential")


def _human_flagged_weak(note: str) -> bool:
    n = (note or "").lower()
    return any(marker in n for marker in _WEAK_RELEVANCE_MARKERS)


def _month_num(m) -> int | None:
    if not m:
        return None
    m = str(m).strip()
    if m.isdigit():
        v = int(m)
        return v if 1 <= v <= 12 else None
    names = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
             "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    return names.get(m[:3].lower())


def _date_tuple(d: dict | None) -> tuple | None:
    """A PubMed publication_date dict {"year", "month", "day"} (month may be "05" or "May", day may
    be absent) -> a (year, month|None, day|None) sortable tuple, or None if no year at all."""
    if not d or not d.get("year"):
        return None
    try:
        y = int(d["year"])
    except (TypeError, ValueError):
        return None
    mo = _month_num(d.get("month"))
    try:
        day = int(d["day"]) if d.get("day") is not None else None
    except (TypeError, ValueError):
        day = None
    return (y, mo, day)


def _compare_dates(cand: tuple | None, own: tuple | None) -> str:
    """'prior' | 'subsequent' | 'ambiguous' | 'unknown' -- C6's real comparator. Never guesses past
    the precision both dates actually have: same-year-with-an-unknown-month on either side is
    'ambiguous', not silently resolved either way."""
    if cand is None or own is None:
        return "unknown"
    cy, cm, cd = cand
    oy, om, od = own
    if cy != oy:
        return "prior" if cy < oy else "subsequent"
    if cm is None or om is None:
        return "ambiguous"
    if cm != om:
        return "prior" if cm < om else "subsequent"
    if cd is None or od is None:
        return "ambiguous"
    if cd != od:
        return "prior" if cd < od else "subsequent"
    return "ambiguous"  # identical date -- cannot order two same-day publications


def _paper_md_year(slug: str) -> int | None:
    """Fallback confirmed-date source when no live PubMed self-match exists in the metadata cache:
    the ARA's own PAPER.md structured `year:` frontmatter field -- NEVER the slug's 'YY' (this
    build's own audit trail shows the slug year can be wrong: woj25's slug says '25' but its real
    PubMed-confirmed publication_date is 2025-01-02 while its DOI string embeds '024' -- neither the
    slug nor the DOI string is trustworthy on its own; PAPER.md's curated frontmatter is)."""
    path = ARA_LIB_DIR / slug / "PAPER.md"
    if not path.exists():
        return None
    try:
        import yaml
        parts = path.read_text(encoding="utf-8").split("---")
        if len(parts) < 3:
            return None
        fm = yaml.safe_load(parts[1]) or {}
        return int(fm.get("year"))
    except Exception:
        return None


def _ara_confirmed_pub_date(slug: str, metadata: dict) -> dict:
    """The ARA's CONFIRMED publication date (C6): prefer a live PubMed self-match already in the
    metadata cache (metadata[pmid]["self_match_of"] == slug -- fetched via get_article_metadata, the
    most authoritative source available), else fall back to PAPER.md's frontmatter year (coarse,
    year-only, but still a curated confirmed value -- never the slug's 'YY')."""
    for pmid, rec in metadata.items():
        if rec.get("self_match_of") == slug:
            pd = rec.get("publication_date") or {}
            return {"year": pd.get("year"), "month": pd.get("month"), "day": pd.get("day"),
                    "source": f"pubmed_self_match:{pmid}"}
    year = _paper_md_year(slug)
    if year is not None:
        return {"year": str(year), "month": None, "day": None, "source": "PAPER.md_frontmatter_year"}
    return {"year": None, "month": None, "day": None, "source": "unavailable"}


def _all_testable_headline_claims(ctx: dict) -> list[dict]:
    """C5 fix: the novelty-check candidate pool is no longer just the claims the within-ARA [sem]
    judge happened to tag novelty.verdict=="novel" -- that let a paper dodge the whole check by never
    using the word "novel"/"first" (cycle2 critique C5: "never say first" as a gaming strategy). Every
    claim whose own status marks it as an actually-tested finding (status starts with "supported" --
    excludes bare "hypothesis"/"hypothesis (...)" claims, which by definition were not directly tested
    against evidence) is in scope, regardless of what the [sem] judge's novelty tag said."""
    out = []
    for c in ctx.get("claims", []) or []:
        if str(c.get("status", "")).startswith("supported"):
            out.append({"claim_id": c.get("id"), "statement": c.get("statement", "")})
    return out


def _load_sem_novel_claims(slug: str) -> list[dict]:
    """Claims the within-ARA [sem] judge (sem_metrics.py / sem_findings/<slug>.yaml) tagged
    novelty.verdict == 'novel'. This is only the STARTING candidate list -- the judge's verdict is
    itself compiler-adjacent (it checked against related_work.md, not the actual literature), which
    is exactly why this module re-checks each one against PubMed independently."""
    path = SEM_FINDINGS_DIR / f"{slug}.yaml"
    if not path.exists():
        return []
    try:
        import yaml
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return []
    items = doc.get("claims") if isinstance(doc, dict) else doc
    out = []
    for c in items or []:
        nov = (c.get("novelty") or {})
        if nov.get("verdict") == "novel":
            out.append({"claim_id": c.get("claim_id"), "sem_note": nov.get("note", "")})
    return out


def _pubmed_cache_lookup(slug: str, claim_id: str) -> dict | None:
    path = CACHE_DIR / "pubmed_novelty_searches.json"
    if not path.exists():
        return None
    try:
        searches = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    # cache keys are "<slug_prefix>_<claim_id>_<slug-ish-topic>" -- match on slug+claim_id prefix
    prefix = f"{slug.split('-')[0]}_{claim_id}_"
    for key, val in searches.items():
        if key.startswith(prefix):
            return {"cache_key": key, **val}
    return None


def _metadata_cache() -> dict:
    path = CACHE_DIR / "pubmed_article_metadata.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _classify_novelty_v2(cached_search: dict, metadata: dict, own_doi: str | None, own_date: dict) -> dict:
    """C6: real computable prior-vs-subsequent classification. Compares each non-self-match
    candidate PMID's own get_article_metadata publication_date against the ARA's CONFIRMED
    publication date (own_date, from _ara_confirmed_pub_date -- a live PubMed self-match if one
    exists, else PAPER.md's frontmatter year; never the slug's 'YY'). Any candidate this cannot be
    computed for (missing/incomplete metadata, or same-year-unknown-month ambiguity) is surfaced as
    an unresolved hit and forces `manual_review` rather than a guessed verdict -- per the project-wide
    contract, no verdict is ever fabricated to fill a gap."""
    pmids = cached_search.get("pmids", [])
    if not pmids:
        return {"verdict": "no_prior_evidence_found", "prior_hits": [], "subsequent_hits": [],
                "self_matches": [], "unresolved_hits": [], "detail": cached_search.get("note", "no PubMed hits.")}

    own_doi_norm = (own_doi or "").strip().lower()
    self_matches, non_self = [], []
    for p in pmids:
        rec = metadata.get(p) or {}
        if own_doi_norm and (rec.get("doi") or "").strip().lower() == own_doi_norm:
            self_matches.append(p)
        else:
            non_self.append(p)

    own_tuple = _date_tuple(own_date)
    prior_hits, subsequent_hits, unresolved_hits = [], [], []
    for p in non_self:
        rec = metadata.get(p) or {}
        cand_tuple = _date_tuple(rec.get("publication_date"))
        cmp = _compare_dates(cand_tuple, own_tuple)
        row = {"pmid": p, "doi": rec.get("doi"), "title": rec.get("title"),
               "publication_date": rec.get("publication_date")}
        if cmp == "prior":
            row["human_flagged_weak_relevance"] = _human_flagged_weak(cached_search.get("note", ""))
            prior_hits.append(row)
        elif cmp == "subsequent":
            subsequent_hits.append(row)
        else:  # ambiguous ordering, or metadata missing/incomplete for this candidate
            row["reason"] = cmp
            unresolved_hits.append(row)

    strong_prior = [h for h in prior_hits if not h.get("human_flagged_weak_relevance")]
    if strong_prior:
        verdict = "prior_literature_found"
    elif prior_hits or unresolved_hits:
        # either every date-prior hit was already reviewed by a human and judged topically weak, or
        # at least one candidate's ordering genuinely could not be computed -- don't guess either way.
        verdict = "manual_review"
    else:
        verdict = "no_prior_evidence_found"

    return {"verdict": verdict, "prior_hits": prior_hits, "subsequent_hits": subsequent_hits,
            "self_matches": self_matches, "unresolved_hits": unresolved_hits,
            "detail": cached_search.get("note", "")}


def novelty_vs_prior_literature(all_ctx: list[dict]) -> list[dict]:
    """For EVERY testable headline claim (C5 -- not just claims a within-ARA [sem] judge happened to
    tag 'novel'), independently check PubMed for literature that predates the ARA's own CONFIRMED
    publication date (C6 -- a real date comparison, not a hand-classified note). THE catch this
    module exists to make: a compiler-fidelity judge can only ever check a claim against the paper's
    OWN abstract/related-work section; it structurally cannot know whether the rest of the literature
    already reported the same thing. This does. Claims with no cached/investigated PubMed search are
    reported `pending`, never fabricated as either novel or non-novel."""
    metadata = _metadata_cache()
    out = []
    for ctx in all_ctx:
        slug = ctx["slug"]
        own_doi = ((ctx.get("sources") or {}).get("paper") or {}).get("doi") or ctx.get("v1", {}).get("doi")
        own_date = _ara_confirmed_pub_date(slug, metadata)
        sem_novel = {nc["claim_id"]: nc["sem_note"] for nc in _load_sem_novel_claims(slug)}
        for cand in _all_testable_headline_claims(ctx):
            cid, stmt = cand["claim_id"], cand["statement"]
            self_declared_novel = cid in sem_novel
            cached = _pubmed_cache_lookup(slug, cid)
            if cached is None:
                out.append({
                    "slug": slug, "claim_id": cid, "statement": stmt,
                    "self_declared_novel": self_declared_novel, "sem_note": sem_novel.get(cid),
                    "verdict": "pending",
                    "detail": "not yet investigated against PubMed in this build -- C5 widened the "
                               "candidate pool to every testable headline claim (not just [sem]-tagged "
                               "'novel' ones); coverage is reported honestly as checked/total in the "
                               "module summary, not fabricated as a verdict.",
                })
                continue
            result = _classify_novelty_v2(cached, metadata, own_doi, own_date)
            priority_language = bool(PRIORITY_LANGUAGE_RE.search(stmt))
            overclaim_risk = (result["verdict"] == "prior_literature_found"
                              and (self_declared_novel or priority_language))
            out.append({
                "slug": slug, "claim_id": cid, "statement": stmt,
                "self_declared_novel": self_declared_novel, "priority_language_in_statement": priority_language,
                "sem_note": sem_novel.get(cid),
                "pubmed_search_query": cached.get("query"),
                "verdict": result["verdict"], "overclaim_risk": overclaim_risk,
                "prior_hits": result["prior_hits"], "subsequent_hits": result["subsequent_hits"],
                "self_matches": result["self_matches"], "unresolved_hits": result["unresolved_hits"],
                "own_confirmed_pub_date": own_date, "detail": result["detail"],
            })
    return out


# ======================================================================================
# entry point
# ======================================================================================
def claim_graph(all_ctx: list[dict]) -> dict:
    clustering = cluster_claims(all_ctx)
    chembl = target_compound_resolvability(all_ctx)
    trials = per_claim_trial_concordance(all_ctx)
    novelty = novelty_vs_prior_literature(all_ctx)

    n_resolved = sum(1 for row in chembl for e in row["entities"] if e.get("resolved") is True)
    n_unresolved = sum(1 for row in chembl for e in row["entities"] if e.get("resolved") is False)
    n_db_coverage_artifact = sum(1 for row in chembl for e in row["entities"] if e.get("db_coverage_artifact"))
    n_concordant = sum(1 for t in trials if t["label"] == "concordant")

    n_total_candidates = len(novelty)
    n_checked = sum(1 for n in novelty if n["verdict"] != "pending")
    n_prior_found = sum(1 for n in novelty if n["verdict"] == "prior_literature_found")
    n_manual_review = sum(1 for n in novelty if n["verdict"] == "manual_review")
    n_overclaim_risk = sum(1 for n in novelty if n.get("overclaim_risk"))

    parts = [
        f"Claim graph over {len(all_ctx)} ARAs, {clustering['n_claims']} claims.",
        f"Corroboration (status=exploratory, TF-IDF cosine >= {SIM_THRESHOLD}, FOL unavailable -- see "
        f"module docstring/C4): {len(clustering['corroboration'])} cross-ARA cluster(s) out of "
        f"{clustering['n_pairs_above_threshold']} pairs above threshold. NOT a validated corroboration "
        "signal -- independence is unestablished at this single-topic n=12 corpus size.",
        f"ChEMBL (axis=trust_fabrication_check, NOT a science-quality signal per C4 -- ~96% "
        "background resolve rate is non-discriminating; only fires on hallucinated/mis-named "
        f"entities): {n_resolved} claim-entity mentions resolved, {n_unresolved} did NOT resolve, all "
        f"{n_db_coverage_artifact} of the latter marked db_coverage_artifact=true (a bioactivity-DB "
        "coverage gap, e.g. APOE/GFAP, NEVER counted against a claim's science -- see "
        "external_anchors.chembl).",
        f"ClinicalTrials.gov per-claim concordance: {n_concordant} claim(s) concordant with a "
        f"registered PRIMARY outcome's own posted value, out of {len(trials)} claim/NCT rows "
        "checked (most rows are not_applicable/pending -- most claims don't name a registered "
        "primary outcome at all).",
        f"PubMed novelty check (C5: scope widened to ALL testable headline claims, not just "
        f"[sem]-tagged 'novel' ones; C6: real publication-date comparator, not a hand-classified "
        f"note): {n_checked}/{n_total_candidates} headline claims corpus-wide checked against PubMed "
        f"in this build. {n_prior_found} have prior literature computed to predate the ARA's own "
        f"confirmed publication date; {n_overclaim_risk} of those also assert priority (self-declared "
        f"'novel' or priority language in the claim's own text) and are flagged overclaim_risk=true; "
        f"{n_manual_review} could not be fully computed and are labeled manual_review (never guessed). "
        "Real catches include sal25 C01 (topline donanemab-vs-aducanumab head-to-head result was "
        "public via a prior review before sal25's own publication), sal26 C01 (the underlying "
        "eMTBR-tau243 biomarker's tau-PET utility predates sal26's own 'first staging concordance' "
        "claim), huu25 C05 (a same-topic ancestry/oligodendroglia AD paper predates huu25 by ~2 "
        "months), and ahm26b C01/C03-C08 (seven CDC-WONDER mortality-disparity breakdowns, each with "
        "on-topic prior literature computed to predate ahm26b's confirmed 2026-02-24 pub date by "
        "years -- consistent with the metascientist's C1 suspicion that this paper's 'novel' tags are "
        "a narrow 'first tabulation of this exact number' framing, not genuinely new science).",
    ]
    return {
        "clusters": clustering["clusters"],
        "corroboration": clustering["corroboration"],
        "corroboration_status": "exploratory",
        "external_anchors": {"chembl": chembl, "trials": trials, "novelty": novelty},
        "summary": " ".join(parts),
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(HERE))
    import compute_metrics_v3 as v3  # noqa: E402

    ctxs = [v3.build_context(s) for s in v3.CORPUS_12 if (v3.ARA_LIB / s / "logic/claims.md").exists()]
    result = claim_graph(ctxs)
    print(result["summary"])
    print()
    print(f"clusters (n_papers>=2): {len(result['corroboration'])}")
    for c in result["corroboration"]:
        print(f"  n_papers={c['n_papers']} sim={c['max_similarity']} {c['papers']}")
        for s in c["representative_statements"]:
            print(f"    - {s[:140]}")
    print()
    print("chembl resolvability (unique entities):")
    seen = set()
    for row in result["external_anchors"]["chembl"]:
        for e in row["entities"]:
            k = e["entity"]
            if k in seen:
                continue
            seen.add(k)
            print(f"  {k}: resolved={e.get('resolved')} {e.get('detail')}")
    print()
    print("trial concordance rows:")
    for t in result["external_anchors"]["trials"]:
        print(f"  {t['slug']} {t['nct']} claim={t.get('claim_id')} label={t['label']}")
    print()
    novelty = result["external_anchors"]["novelty"]
    n_checked = sum(1 for n in novelty if n["verdict"] != "pending")
    n_overclaim = sum(1 for n in novelty if n.get("overclaim_risk"))
    print(f"novelty rows ({n_checked}/{len(novelty)} checked, {n_overclaim} overclaim_risk):")
    for n in novelty:
        flag = " OVERCLAIM_RISK" if n.get("overclaim_risk") else ""
        print(f"  {n['slug']} {n['claim_id']}: verdict={n['verdict']} "
              f"self_declared_novel={n.get('self_declared_novel')}{flag}")
