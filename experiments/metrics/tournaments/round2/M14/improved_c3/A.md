## Changes (cycle 3)

Direct responses to `critique_c2.md`'s four cycle-3 directions for A (all four addressed; nothing
deferred):

1. **Fixed the anchor extractor (was the single most important fix).** Cycle 2's `has_specific_anchor`
   named-entity regex (`\b[A-Z][a-zA-Z0-9]{2,}\b`) matched any capitalized word >= 3 chars — "The,"
   "Alzheimer," "Introduction" — and the numeric regex (`\b\d{2,5}\b`) matched every bare year and
   incidental integer, so on-topic-but-vague prose passed the gate almost automatically. The extractor
   is rewritten (`extract_anchors` below) to: (a) drop bare 2–5 digit integers and bare `19xx`/`20xx`
   years entirely — numeric anchors now require a decimal, a percent sign, or an `n=` form; (b) filter
   every candidate token/phrase against a curated `COMMON_TOKENS` stoplist of generic English and
   generic-science vocabulary; (c) require named-entity anchors to be either mixed alphanumeric
   (`p-tau217`, `GPT4`, `COVID19`), an uncommon acronym, or a multi-word capitalized phrase where not
   every word is common. A vague topical paraphrase no longer contains a qualifying anchor by
   construction.
2. **Replaced the `title_similarity` placeholder.** Jaccard-over-raw-tokens at an unreachable `>= 0.85`
   threshold rewarded almost nothing and made `external_grounding` (30% of `role_alignment_score`)
   float near zero even for honest `related_work.md` layers. It is replaced with a token-set ratio
   (stopword-filtered, `difflib.SequenceMatcher` over the intersection-augmented token strings — the
   standard fuzzy token-set-ratio construction) at a reachable, stated `>= 0.60` threshold, and — the
   preferred path — an exact DOI/S2-ID/arXiv-ID match via an optional `**Ref**` field on `related_work.md`
   entries, checked before falling back to title similarity at all.
3. **Specified S2-only `relation_type` assignment.** `relation_type` is load-bearing for `importance`,
   `high_importance_miss_penalty`, and `contradiction_score`, but cycle 2 never said how Semantic
   Scholar-only candidates (Undermind off) get one, so the miss-penalty pool could silently empty and
   the component could return a free-pass `1.0` in exactly the degraded mode where it matters most. Step
   3.5a now assigns `relation_type` deterministically from retrieval provenance (which query/endpoint
   surfaced the candidate) plus title/abstract signal, with a non-empty default (`method_neighbor`) so no
   candidate is ever left unclassified. `high_importance_miss_penalty` now takes a
   `relation_classification_ran` flag and returns `0.0` — not `1.0` — when real candidates exist but were
   never classified, distinguishing a pipeline defect from a genuine absence of high-stakes neighbors.
4. **Added a use-requirement to `near_direct`.** Cycle 2's `near_direct` (author/year + high title
   similarity) earned 0.85 with no check that the ARA actually engaged the paper, so a stuffed
   `related_work.md` bibliography of correct author-year strings scored near-full credit per line. Each
   `near_direct` match is now checked with `field_role_signal` against the field or RW block it was found
   in; matches with no substantive content beyond the bare citation (a bibliography-style mention) are
   downgraded from 0.85 to 0.35 (`cited_but_unused`). `direct` citations are untouched — the direction
   scoped this to `near_direct` specifically, since a formal, unambiguous citation is itself a form of use
   that a bare fuzzy-matched mention is not.

Also, per this cycle's instruction to make the workflow maximally concrete and runnable, an
**End-to-End Runbook** section is added at the end with a single orchestrating `run_m14(...)` function
that chains every step (parse → query → retrieve → classify relations → compute importance → classify
coverage → score) into one callable pipeline with explicit typed inputs/outputs, so the metric can be
implemented directly from this document without inventing glue code.

---

## Indicator

Reference-landscape completeness asks whether the ARA's problem framing is grounded in the real
prior-work neighborhood around the paper, rather than only in the source paper's own selective
citations or a generic background summary. A good `logic/problem.md` should surface the empirical
observations, gaps, failed attempts, and key insight in a way that is recognizably connected to the
broader literature landscape: canonical precursors, nearest-neighbor work, competing approaches, and
work that contradicts or weakens the paper's motivating gap.

This metric is intentionally external-facing. Many internal ARA checks can verify that a statement has
a source quote or that problem fields are structurally present. They cannot tell whether the compiler
missed the papers that a competent literature search would immediately find. M14 fills that hole by
comparing the ARA's cited and named landscape against an independently generated landscape from
Semantic Scholar and an optional deep-search agent such as Undermind.

## What It Rewards

Reward high scores when:

- `logic/problem.md` contains specific, citable observations drawn from prior work rather than
  abstract-only background sentences.
- observations and gaps name concrete prior attempts, not just "prior work is limited."
- the cited literature covers canonical, recent, and methodologically adjacent work.
- the ARA names contradicting or tension-producing findings where they exist.
- the Key Insight is positioned as resolving a real landscape-level gap, not merely restating the
  paper's method.
- cross-layer `logic/related_work.md` confirms a typed dependency graph (`Type`/`Delta`/
  `Claims affected` per entry) with enough breadth to support the problem framing, and those entries
  resolve to real external papers rather than being unverifiable assertions.
- cross-layer `trace/exploration_tree.yaml` shows that literature exploration was part of the compiler
  trajectory — verified by overlap with the independently generated landscape's actual paper
  titles/authors, not generic vocabulary — especially when the source paper's claim depends on
  novelty, superiority, or gap claims.
- a `near_direct` or `direct` match is embedded in a field that actually does something with it
  (contrasts, motivates, extends), not merely a bibliography-style citation drop.

## What It Must Not Reward

Do not reward:

- long citation lists that are only copied from the source paper but omit obvious search-neighbor
  work.
- citations without semantic use in the problem statement. As of cycle 3, `near_direct` matches with no
  role context beyond the bare citation are scored as `cited_but_unused`, not full credit.
- generic claims of contradiction without identifying the contradicting study or result.
- over-inclusive bibliography dumps that mention many papers but do not connect them to observations,
  gaps, or assumptions.
- fabricated precision: if a title, DOI, or claim cannot be verified externally, it should not count
  as covered.
- vague "conceptual coverage" that only shares topic vocabulary with an external paper. Conceptual
  credit requires a concrete shared anchor (a number, named method/model/dataset/cohort, or specific
  result) — see the cycle-3 `has_specific_anchor` and `extract_anchors` below, which exclude bare years,
  bare integers, and common vocabulary so topic overlap alone cannot pass the gate.
- a related-work or trace layer padded with relation-flavored vocabulary (e.g. sprinkling
  "baseline," "contradicts," "prior") that does not attach to a real, externally-resolvable paper.
- availability excuses. Missing `related_work.md`, inaccessible external search, abstract-only source
  material, or thin citation footprints all reduce the score.
- a degraded run (real candidates retrieved, but `relation_type` never classified) presenting as if it
  were a clean run with no high-stakes neighbors. Cycle 3's `relation_classification_ran` gate keys the
  `high_importance_miss_penalty` component off this distinction explicitly.

## Failure Modes And Gaming Routes

The main gaming route is citation stuffing: adding many references to `Evidence` fields or
`related_work.md` without showing how they shape the problem. The metric counters this by measuring
both coverage and role alignment: each covered external paper must be tied to an Observation, Gap,
Existing attempt, Why they fail, Assumption, or a `related_work.md` entry with a real `Type`/`Delta`/
`Claims affected` triple that resolves to that paper, and — as of cycle 3 — `near_direct` matches
specifically must show role context beyond the bare citation or they are scored as `cited_but_unused`.

A second route is source-paper anchoring: reproducing the paper's introduction citations while missing
nearby work that the paper did not cite. The external k-nearest-neighbor search counters this by
creating an independent expectation set, and the asymmetric `high_importance_miss_penalty` makes
missing the very top of that set costly even when average coverage looks fine — and, as of cycle 3,
this penalty cannot be silently defused by leaving retrieved candidates unclassified (see
`relation_classification_ran`).

A third route is contradiction laundering: omitting negative, failed, or competing studies so that the
Key Insight looks cleaner than the field warrants. The contradiction subscore separately searches for
negative or competing findings and penalizes omissions, does not let a failed search masquerade as
"genuinely no contradictions exist" (`search_available` gating), and — as of cycle 3 — `contradictory`
and `competing` relation types are populated deterministically even in Semantic Scholar-only mode, so
this route cannot be exploited simply by running without Undermind.

A fourth route is generic gap language. The workflow penalizes gaps whose `Existing attempts` and
`Why they fail` fields lack named approaches, papers, cohorts, models, methods, or numeric result
contrasts.

A fifth route is **conceptual-coverage laundering**: describing an external paper's topic in vague
terms to earn "conceptual" credit without engaging its actual contribution, or relying heavily on the
conceptual tier instead of building a real citation footprint. The 40%-of-covered-weight cap bounds the
blast radius, and, as of cycle 3, the `extract_anchors`/`has_specific_anchor` gate itself is hardened so
vague on-topic prose no longer trivially clears it (cycle 2's version matched on "the," "2023," and
similar noise tokens).

A sixth route is **cross-layer keyword stuffing**: writing a `related_work.md` or
`exploration_tree.yaml` full of relation-flavored words ("extends," "contradicts," "baseline") that
never attach to a resolvable external paper. `role_alignment_score` and `trace_external_grounding` both
require resolution against the independently generated landscape via a real string-similarity function
at a reachable threshold (cycle 3), or an exact DOI/S2-ID match, not vocabulary presence.

A seventh route, closed in cycle 3, is **bare-citation stuffing inside `near_direct`**: dropping many
correctly-formatted author/year strings into a bibliography-style list to harvest 0.85 credit per line
without engaging any of them. `field_role_signal` requires each `near_direct` match to sit in a field
that carries real content beyond the citation token itself.

An eighth route, closed in cycle 3, is **degraded-run laundering via relation-type collapse**: running
the metric with Undermind unavailable and never assigning `relation_type` to Semantic Scholar
candidates, causing the canonical/contradictory/competing pool to empty and `high_importance_miss_penalty`
to return a free `1.0`. Step 3.5a's deterministic S2-only classifier and the `relation_classification_ran`
gate close this: an unclassified-but-nonempty candidate set now scores `0.0` on this component, not `1.0`.

## Inputs

Primary artifact:

- `logic/problem.md`
  - Observations: heading titles, `Statement`, `Evidence`, `Implication`
  - Gaps: heading titles, `Statement`, `Caused by`, `Existing attempts`, `Why they fail`
  - Key Insight: `Insight`, `Derived from`, `Enables`
  - Assumptions: `A{N}: ...`

Optional cross-layer artifacts, scored as available-or-missing inputs:

- `logic/related_work.md` from DATA_SHAPES section 6, if present in the ARA. Parsed as typed
  `### RW{N}` entries with `Type`, `Delta`, `Claims affected` fields, and an optional `Ref` field
  (DOI/S2 paperId/arXiv ID) used for exact-match resolution (cycle 3).
- `trace/exploration_tree.yaml` from DATA_SHAPES section 8, if present in the ARA.
- `PAPER.md` metadata if needed to form exact search queries: title, authors, year, DOI, abstract,
  keywords, domain.

External inputs:

- Semantic Scholar API search and recommendations.
- Undermind or equivalent literature-search bot when configured.

Missing or thin inputs never produce N/A. They receive low component scores.

## External Landscape Generation

### Step 1: Parse ARA Problem Landscape

Parse `logic/problem.md` into:

```python
ProblemLandscape = {
    "observations": [{"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str}],
    "gaps": [{"id": "G1", "title": str, "statement": str, "caused_by": [str], "existing_attempts": str, "why_fail": str}],
    "key_insight": {"insight": str, "derived_from": [str], "enables": str},
    "assumptions": [{"id": "A1", "text": str}],
}
```

Extract citation candidates from all fields using DOI regexes, author-year patterns, bracketed numeric
references where resolvable through `related_work.md`, and named study/model/dataset strings.
Normalize citation strings to Semantic Scholar paper IDs where possible. For each extracted citation
candidate, retain the source field name (`Evidence`, `Existing attempts`, `Why they fail`,
`Derived from`) and a span of surrounding text — this is required by `field_role_signal` (cycle 3) to
judge role context for `near_direct` matches.

Also collect the set of valid problem-layer reference IDs, `problem_ids = {O1, O2, ..., G1, G2, ..., A1, ...}`,
used later by `role_alignment_score` to check that `related_work.md`'s `Claims affected` fields point
at real entries rather than invented ones.

### Step 2: Build Search Queries

Use `PAPER.md` when available. If not, derive from `problem.md` terms and penalize metadata absence in
the availability component.

Queries, each tagged with a `provenance` label used by Step 3.5a's relation classifier:

1. Exact paper query (`provenance = "focal_query"`):

```text
"{paper_title}" {first_author_last_name}
```

2. Problem-neighborhood query (`provenance = "problem_neighborhood_query"`):

```text
{top_8_keywords_from_problem_and_paper} {domain_terms} review OR benchmark OR comparison
```

3. Gap-specific queries, one per gap (`provenance = "gap_query"`):

```text
{gap_statement_key_terms} {existing_attempts_key_terms} limitation OR failure OR contradictory OR inconsistent
```

4. Contradiction query (`provenance = "contradiction_query"`):

```text
{paper_title_or_core_claim_terms} contradicts OR inconsistent OR negative result OR failed to replicate OR no improvement
```

### Step 3: Semantic Scholar Retrieval

Call Semantic Scholar:

- `GET /graph/v1/paper/search` for each query with `limit=100`, requesting
  `paperId,title,abstract,year,venue,authors,citationCount,influentialCitationCount,externalIds,references,citations,fieldsOfStudy,tldr`.
- If the focal paper is resolved, call:
  - `GET /graph/v1/paper/{paperId}/references` (`provenance = "focal_references"`)
  - `GET /graph/v1/paper/{paperId}/citations` (`provenance = "focal_citations"`)
  - recommendations endpoint for similar papers, `limit=500`, if available (`provenance = "recommendations"`).

Every retrieved candidate record retains its `provenance` tag — the query or endpoint that first
surfaced it. If a candidate is surfaced by more than one query, keep the highest-priority provenance in
this order: `focal_references` > `contradiction_query` > `focal_citations` > `gap_query` >
`problem_neighborhood_query` > `recommendations` > `focal_query`. This tag feeds both
`relevance_component` (Step 3.5, via `query_rank_by_id`) and the new deterministic `relation_type`
classifier (Step 3.5a).

Construct the independent expected landscape:

- `island`: focal paper references plus papers citing the focal paper, restricted to topically similar
  abstracts/titles.
- `knn500`: top 500 nearest papers from search/recommendations by embedding similarity to the focal
  paper and problem statement.
- `canonical`: top citation-count and influential-citation papers among `knn500`.
- `recent`: papers from focal year minus 3 through current year among `knn500`.
- `contradictory`: papers whose title/abstract or classification indicate negative, inconsistent,
  failed-replication, or competing-result relation.

Set `search_available = True` if at least one query returned a non-error, non-empty result set;
`False` if all Semantic Scholar calls errored, timed out, or returned zero candidates across every
query. This flag is load-bearing for `contradiction_score` and, as of cycle 3, for
`high_importance_miss_penalty` — see Penalize-Don't-Skip.

If the focal paper cannot be resolved, still build `knn500` from title/domain/problem queries and
assign the focal-resolution subscore to zero.

### Step 3.5: Deterministic `importance` Assignment

Every expected paper `p` in `island ∪ knn500` (deduplicated) receives a deterministic `importance ∈ [0,1]`,
computed at landscape-construction time — never left to a downstream default:

```python
def relevance_component(p, query_rank_by_id):
    # p['paperId'] rank position across the search/recommendation calls that surfaced it,
    # inverse-rank normalized: rank 1 of N -> 1.0, rank N of N -> ~0.0
    rank = query_rank_by_id.get(p["paperId"])
    pool_size = len(query_rank_by_id)
    if rank is None or pool_size <= 1:
        return 0.5
    return clamp01(1.0 - (rank - 1) / (pool_size - 1))


def citation_percentile(p, knn500):
    counts = sorted(q.get("citationCount", 0) or 0 for q in knn500)
    if not counts:
        return 0.5
    idx = sum(1 for c in counts if c <= (p.get("citationCount", 0) or 0))
    return clamp01(idx / len(counts))


def relation_boost_norm(relation_type):
    boost = {
        "canonical": 1.35, "contradictory": 1.45, "competing": 1.30,
        "method_neighbor": 1.10, "empirical_neighbor": 1.05,
        "review": 1.00, "dataset_resource": 0.90,
    }.get(relation_type, 1.0)
    lo, hi = 0.90, 1.45
    return clamp01((boost - lo) / (hi - lo))


def compute_importance(p, query_rank_by_id, knn500):
    return clamp01(
        0.5 * relevance_component(p, query_rank_by_id)
        + 0.3 * citation_percentile(p, knn500)
        + 0.2 * relation_boost_norm(p.get("relation_type"))
    )
```

`importance` is attached to every expected-paper record before coverage classification runs, and it is
computed *after* Step 3.5a assigns `relation_type`, so `relation_boost_norm` always has a real,
non-default input to work with.

### Step 3.5a: Deterministic `relation_type` Assignment (cycle 3)

Cycle 2 left `relation_type` fully dependent on Undermind's output. When Undermind is unavailable (an
explicitly supported mode), Semantic Scholar-only candidates never received a `relation_type`, which
silently emptied the canonical/contradictory/competing pool that `high_importance_miss_penalty` and
`contradiction_score` both key off — exactly the mode where those components matter most. This step
closes that gap with a deterministic classifier that runs whenever Undermind did not already supply a
`relation_type` for a candidate:

```python
CONTRADICTION_TERMS = re.compile(
    r"\b(contradict|inconsisten|fail(?:ed)? to replicat|negative result|no improvement|null result)\b",
    re.I,
)
COMPETING_TERMS = re.compile(r"\b(alternative|competing|versus|compared to|outperform)\b", re.I)
DATASET_TERMS = re.compile(r"\b(dataset|corpus|benchmark suite|cohort registry)\b", re.I)
REVIEW_TERMS = re.compile(r"\b(review|survey|meta-analysis)\b", re.I)

PROVENANCE_PRIORITY = [
    "focal_references", "contradiction_query", "focal_citations",
    "gap_query", "problem_neighborhood_query", "recommendations", "focal_query",
]


def assign_relation_type_s2_only(p, knn500, focal_year):
    if p.get("relation_type"):  # Undermind already classified this one; do not overwrite
        return p["relation_type"]
    title_l = (p.get("title") or "").lower()
    abstract_l = (p.get("abstract_or_tldr") or p.get("abstract") or "").lower()
    provenance = p.get("provenance")

    if provenance == "contradiction_query" or CONTRADICTION_TERMS.search(abstract_l):
        return "contradictory"
    if DATASET_TERMS.search(title_l):
        return "dataset_resource"
    if provenance == "gap_query" or COMPETING_TERMS.search(abstract_l):
        return "competing"
    if provenance == "focal_references" and citation_percentile(p, knn500) >= 0.70:
        return "canonical"
    if provenance == "problem_neighborhood_query" and REVIEW_TERMS.search(title_l):
        return "review"
    if p.get("year") and focal_year and abs(p["year"] - focal_year) <= 1 and provenance in {"focal_citations", "recommendations"}:
        return "empirical_neighbor"
    return "method_neighbor"  # deterministic non-empty default — never None, never skipped


def classify_all_relations(expected_papers, knn500, focal_year):
    for p in expected_papers:
        p["relation_type"] = assign_relation_type_s2_only(p, knn500, focal_year)
    return expected_papers
```

`classify_all_relations` runs over every candidate in `island ∪ knn500` whenever `search_available` is
`True`, regardless of whether Undermind ran. Set `relation_classification_ran = True` once this pass
completes over a non-empty candidate set; it stays `False` only when `search_available` is `False`
(there was nothing to classify). This flag feeds `high_importance_miss_penalty` (see below), preventing
an unclassified-but-nonempty pool from masquerading as "genuinely no high-stakes neighbors."

### Step 4: Optional Undermind Retrieval

Prompt:

```text
You are auditing whether a research artifact captures the relevant literature landscape for a paper.
Paper title: {title}
Authors/year/venue/DOI: {metadata}
Problem statement observations and gaps:
{compact_problem_json}

Find the 25-40 most relevant prior or concurrent works that a rigorous related-work section should
consider. Include canonical precursors, nearest methodological neighbors, directly competing work,
and contradictory or negative-result work. For each item return:
title, authors, year, DOI/arXiv if available, one-sentence relevance, relation_type in
{canonical, method_neighbor, empirical_neighbor, competing, contradictory, dataset_resource, review}.
```

Require JSON output. Resolve returned works through Semantic Scholar and fold them into `knn500`
before `relation_type` and `importance` are computed (Steps 3.5a then 3.5), so Undermind-sourced papers
carry their supplied `relation_type` (Step 3.5a does not overwrite it) and are ranked on equal footing.
If Undermind is unavailable, set `undermind_available = False`; this lowers the search-depth component
but does not skip the metric — Step 3.5a's deterministic classifier covers the resulting Semantic
Scholar-only candidate set instead.

## Deterministic Coverage Classification

For each expected external paper, classify whether the ARA covers it:

- `direct`: exact DOI/S2 ID/title match in `problem.md` or `related_work.md`.
- `near_direct`: same first author/year and title-set similarity >= 0.90 (`token_set_ratio`, defined
  below). As of cycle 3, each `near_direct` match also carries a `role_context_ok` boolean (see
  `field_role_signal` below), used by the scoring function to distinguish an engaged near-match from a
  bare bibliography-style mention.
- `conceptual`: no citation match, but the paper's key idea/result is summarized in a relevant
  Observation/Gap/`related_work.md` entry **and** a specific matching artifact anchors that summary to
  the external paper (see `has_specific_anchor` below), determined by an LLM verifier with evidence
  text and confirmed deterministically.
- `missed`: no sufficient match.

### `extract_anchors` / `has_specific_anchor`: the conceptual-coverage guard (hardened, cycle 3)

Cycle 2's anchor extractor was gameable: its named-entity regex matched any capitalized word >= 3
characters ("The," "Alzheimer," "Introduction," "Plasma," "Network") and its numeric regex matched
every bare year and incidental 2–5 digit integer, so on-topic-but-vague prose cleared the gate almost
by default. Cycle 3 requires anchors to be *distinctive* — the kind of token a vague paraphrase would
not naturally contain:

```python
import difflib
import re

COMMON_TOKENS = {
    "the", "this", "that", "with", "from", "study", "studies", "results", "result", "paper",
    "analysis", "method", "methods", "model", "models", "approach", "approaches", "framework",
    "system", "group", "groups", "patient", "patients", "data", "dataset", "datasets", "research",
    "introduction", "background", "discussion", "conclusion", "table", "figure", "review",
    "comparison", "benchmark", "network", "networks", "plasma", "cohort", "cohorts", "biomarker",
    "biomarkers", "disease", "clinical", "significant", "significantly", "novel", "new", "recent",
    "prior", "previous", "current", "using", "used", "use", "based", "across", "among", "between",
    "these", "those", "such", "most", "some", "many", "found", "show", "shows", "showed", "showing",
    "demonstrate", "demonstrated", "demonstrates", "present", "presented", "propose", "proposed",
    "provides", "provide", "provided", "related", "work", "works", "literature", "field", "fields",
    "level", "levels", "high", "low", "score", "scores", "value", "values", "test", "tests",
    "testing", "training", "trained", "abstract", "introduction",
}


def is_common_token(word):
    return len(word) < 4 or word.lower() in COMMON_TOKENS


def extract_anchors(text):
    if not text:
        return []
    anchors = set()

    # Precise numeric anchors only: a decimal, a percent, or an explicit n= form.
    # Bare integers and bare years (19xx/20xx) are never anchors on their own.
    anchors.update(re.findall(r"\bn\s?=\s?\d+\b", text, re.I))
    anchors.update(re.findall(r"\b\d+\.\d+%?\b", text))
    anchors.update(re.findall(r"\b\d+%\b", text))

    # Mixed alphanumeric named entities: model/method/dataset names like p-tau217, GPT4, COVID19.
    anchors.update(re.findall(r"\b[A-Za-z]+-?\d+[A-Za-z0-9]*\b", text))

    # Uncommon all-caps acronyms (>=2 letters), filtered against the stoplist.
    for tok in re.findall(r"\b[A-Z]{2,6}\b", text):
        if not is_common_token(tok):
            anchors.add(tok)

    # Multi-word proper-noun phrases, kept only if not every word is common.
    for m in re.finditer(r"\b(?:[A-Z][a-zA-Z]+\s){1,3}[A-Z][a-zA-Z]+\b", text):
        words = m.group(0).split()
        if not all(is_common_token(w) for w in words):
            anchors.add(m.group(0))

    # Single capitalized tokens, filtered against the stoplist.
    for tok in re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", text):
        if not is_common_token(tok):
            anchors.add(tok)

    # Belt-and-suspenders: never let a bare year slip through via another rule.
    anchors = {a for a in anchors if not re.fullmatch(r"(19|20)\d{2}", a)}
    return [a for a in anchors if len(re.sub(r"[^A-Za-z0-9]", "", a)) >= 3]


def has_specific_anchor(external_paper, ara_excerpt):
    ext_text = (external_paper.get("abstract_or_tldr") or "") + " " + (external_paper.get("title") or "")
    anchors = extract_anchors(ext_text)
    if not anchors or not ara_excerpt:
        return False
    excerpt_lower = ara_excerpt.lower()
    return any(a.lower() in excerpt_lower for a in anchors)
```

LLM prompt for conceptual coverage:

```text
Decide if the ARA text substantively covers the external paper's contribution, even without citing it.

External paper:
Title: {title}
Abstract/TLDR: {abstract_or_tldr}
Relation type: {relation_type}

ARA excerpts:
{problem_observations_gaps_related_work_excerpts}

Return JSON:
{
  "coverage": "direct|conceptual|missed",
  "covered_by_ids": ["O2", "G1"],
  "matched_anchor": "the specific number, named method, dataset, cohort, or result shared by both texts, or null",
  "rationale": "one sentence",
  "confidence": 0.0-1.0
}

Use conceptual only when a specific result, method, dataset, or contradiction from the external paper
is present in the ARA excerpt — not generic topic overlap. If no specific anchor exists, coverage must
be "missed" even if the general subject matter overlaps.
```

Convert LLM output deterministically:

- `direct` from string/ID matching overrides LLM.
- `conceptual` counts only if **all** of: `confidence >= 0.75`, at least one concrete problem ID is
  returned, **and** `has_specific_anchor(external_paper, matched_ara_excerpt)` is `True` on the
  excerpt corresponding to the returned `covered_by_ids`, using the hardened cycle-3 extractor. An
  LLM-claimed anchor that does not actually appear in the excerpt (checked deterministically) is
  discarded.
- otherwise `missed`.

### `field_role_signal`: the `near_direct` use-requirement (cycle 3)

A `near_direct` match earns full credit only if the field or `related_work.md` block it appears in
carries real content beyond the bare citation — otherwise it is a bibliography-style drop and is
downgraded:

```python
def field_role_signal(field_text, citation_span):
    if not field_text:
        return False
    remainder = field_text.replace(citation_span, "", 1).strip() if citation_span else field_text
    tokens = re.findall(r"[A-Za-z0-9]+", remainder)
    has_numeric_result = bool(re.search(r"\d+(\.\d+)?%|\bn\s?=\s?\d+\b", remainder))
    return len(tokens) >= 12 or has_numeric_result


def rw_block_role_ok(block):
    # For a near_direct match found only in related_work.md: the block must be structurally
    # complete (mirrors role_alignment_score's completeness requirement), not a bare title line.
    return bool(block.get("type") and block.get("delta") and block.get("claims_affected"))


def near_direct_role_context_ok(match_location):
    # match_location = {"kind": "problem_field" | "related_work_block",
    #                    "field_text": str, "citation_span": str} or
    #                   {"kind": "related_work_block", "block": dict}
    if match_location["kind"] == "problem_field":
        return field_role_signal(match_location["field_text"], match_location["citation_span"])
    return rw_block_role_ok(match_location["block"])
```

If a `near_direct` match occurs in more than one location (e.g., both `problem.md` and
`related_work.md`), `role_context_ok` is `True` if any location clears its check.

## Title Similarity And External Resolution (cycle 3, replaces the cycle-2 placeholder)

```python
TITLE_STOPWORDS = {
    "a", "an", "the", "of", "and", "or", "for", "in", "on", "with", "to", "via", "using",
    "toward", "towards", "into", "from", "study", "analysis", "approach",
}


def normalize_title_tokens(title):
    tokens = re.findall(r"[a-z0-9]+", (title or "").lower())
    return [t for t in tokens if t not in TITLE_STOPWORDS and len(t) > 1]


def token_set_ratio(a, b):
    ta, tb = set(normalize_title_tokens(a)), set(normalize_title_tokens(b))
    if not ta or not tb:
        return 0.0
    common = ta & tb
    sorted_common = " ".join(sorted(common))
    s1 = (sorted_common + " " + " ".join(sorted(ta - common))).strip()
    s2 = (sorted_common + " " + " ".join(sorted(tb - common))).strip()
    return difflib.SequenceMatcher(None, s1, s2).ratio()


TITLE_MATCH_THRESHOLD = 0.60  # reachable for genuine title correspondence; recalibrated from the
                              # cycle-2 Jaccard/0.85 pairing, which rewarded almost nothing


def resolve_external_reference(candidate_ref, expected_papers):
    # candidate_ref: {"title": str, "ref_id": str|None}  — ref_id is an optional DOI/S2 paperId/
    # arXiv ID parsed from an ARA-side **Ref** field or inline identifier. Exact-ID match is
    # preferred and checked first; title-set similarity is the fallback.
    ref_id = candidate_ref.get("ref_id")
    if ref_id:
        for p in expected_papers:
            if ref_id in {p.get("doi"), p.get("paperId"), p.get("arxiv_id")}:
                return True
    return any(
        token_set_ratio(candidate_ref.get("title", ""), p.get("title", "")) >= TITLE_MATCH_THRESHOLD
        for p in expected_papers
    )
```

This function is the single shared resolution path used by both `near_direct`/`direct` classification
against `related_work.md` entries and by `role_alignment_score`'s `external_grounding` term — replacing
the cycle-2 placeholder Jaccard function and its unreachable `0.85` threshold everywhere it was used.

## Scoring Function

All components are in `[0, 1]`. Final score is also `[0, 1]`.

```python
import math
import re
from collections import Counter


def clamp01(x):
    return max(0.0, min(1.0, float(x)))


def weighted_mean(parts):
    total_w = sum(w for _, w in parts)
    return sum(score * w for score, w in parts) / total_w if total_w else 0.0


def richness_score(text):
    if not text:
        return 0.0
    tokens = re.findall(r"[A-Za-z0-9_\-]+", text)
    has_specifics = sum(bool(re.search(p, text, re.I)) for p in [
        r"\b[A-Z][a-z]+ et al\.",
        r"\b19\d{2}|20\d{2}\b",
        r"\b\d+(\.\d+)?%?\b",
        r"\bcohort|dataset|model|assay|benchmark|trial|meta-analysis|ablation\b",
        r"\bfail|limited|inconsistent|contradict|outperform|replicat|negative\b",
    ])
    return clamp01(0.45 * min(len(tokens) / 80.0, 1.0) + 0.55 * min(has_specifics / 4.0, 1.0))


def citation_footprint_score(problem):
    evidence_text = "\n".join(o.get("evidence", "") for o in problem.get("observations", []))
    all_problem_text = "\n".join([
        evidence_text,
        "\n".join(g.get("existing_attempts", "") + " " + g.get("why_fail", "") for g in problem.get("gaps", [])),
    ])
    author_year = len(re.findall(r"[A-Z][A-Za-z'\-]+ et al\.,?\s*(19|20)\d{2}", all_problem_text))
    years = len(set(re.findall(r"\b(19\d{2}|20\d{2})\b", all_problem_text)))
    doi = len(re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", all_problem_text))
    section_refs = len(re.findall(r"§\s*\d|Introduction|Related Work|Background|Methods", evidence_text, re.I))
    abstract_only = evidence_text and not re.search(r"§\s*\d|Introduction|Related Work|Background", evidence_text, re.I)
    base = 0.35 * min((author_year + doi) / 12.0, 1.0) + 0.25 * min(years / 6.0, 1.0) + 0.25 * min(section_refs / max(1, len(problem.get("observations", []))), 1.0)
    if len(problem.get("observations", [])) >= 3:
        base += 0.15
    if abstract_only:
        base *= 0.45
    return clamp01(base)


def coverage_score(expected_papers):
    # expected_papers entries contain relation_type, importance in [0,1] (Steps 3.5a/3.5),
    # coverage, and — for near_direct entries — role_context_ok (cycle 3). Applies the
    # conceptual-credit cap (cycle 2) and the near_direct use-requirement (cycle 3).
    if not expected_papers:
        return 0.0
    weights = []
    for p in expected_papers:
        relation_boost = {
            "canonical": 1.35,
            "contradictory": 1.45,
            "competing": 1.30,
            "method_neighbor": 1.10,
            "empirical_neighbor": 1.05,
            "review": 1.00,
            "dataset_resource": 0.90,
        }.get(p.get("relation_type"), 1.0)
        weights.append(max(0.2, p.get("importance", 0.0)) * relation_boost)

    values = []
    for p in expected_papers:
        cov = p.get("coverage", "missed")
        if cov == "near_direct":
            values.append(0.85 if p.get("role_context_ok", False) else 0.35)
        else:
            values.append({"direct": 1.0, "conceptual": 0.55, "missed": 0.0}.get(cov, 0.0))

    covered_weight = sum(w for w, p in zip(weights, expected_papers) if p.get("coverage") != "missed")
    conceptual_weight = sum(w for w, p in zip(weights, expected_papers) if p.get("coverage") == "conceptual")
    if covered_weight > 0 and conceptual_weight / covered_weight > 0.40:
        # Discount conceptual credit so it cannot supply more than 40% of covered weight.
        discount = (0.40 * covered_weight) / conceptual_weight
        values = [
            v * discount if p.get("coverage") == "conceptual" else v
            for v, p in zip(values, expected_papers)
        ]

    return clamp01(sum(v * w for v, w in zip(values, weights)) / sum(weights))


def high_importance_miss_penalty(expected_papers, search_available, relation_classification_ran, top_k=10):
    # Cycle-2 asymmetric-miss mechanism, cycle-3 hardened against relation-type collapse.
    if not expected_papers or not search_available:
        # No candidates were retrievable at all. coverage_score already reflects this as zero;
        # this component does not compound that failure a second time.
        return 1.0
    if not relation_classification_ran:
        # Cycle-3 guard: real candidates exist but were never tagged with relation_type. This is
        # a pipeline defect (Step 3.5a did not run), not evidence of a benign landscape, and must
        # not present as a clean pass.
        return 0.0
    pool = [p for p in expected_papers if p.get("relation_type") in {"canonical", "contradictory", "competing"}]
    if not pool:
        # Candidates exist and were classified, but genuinely none fell into a high-stakes
        # bucket. This is a verified absence, not a classification gap, so it earns the pass.
        return 1.0
    top = sorted(pool, key=lambda p: p.get("importance", 0.0), reverse=True)[:top_k]
    total_importance = sum(p.get("importance", 0.0) for p in top)
    if total_importance == 0:
        return 1.0
    missed_importance = sum(p.get("importance", 0.0) for p in top if p.get("coverage", "missed") == "missed")
    return clamp01(1.0 - (missed_importance / total_importance))


def contradiction_score(expected_papers, search_available):
    contradictory = [p for p in expected_papers if p.get("relation_type") in {"contradictory", "competing"}]
    if not contradictory:
        # A clean search that genuinely found no contradictions earns partial credit. A
        # failed/empty search earns almost none — it must not look like a clean result.
        return 0.65 if search_available else 0.10
    vals = []
    for p in contradictory:
        cov = p.get("coverage")
        if cov == "near_direct":
            vals.append(0.85 if p.get("role_context_ok", False) else 0.35)
        else:
            vals.append({"direct": 1.0, "conceptual": 0.60, "missed": 0.0}.get(cov, 0.0))
    return clamp01(sum(vals) / len(vals))


def gap_specificity_score(problem):
    gaps = problem.get("gaps", [])
    if not gaps:
        return 0.0
    per_gap = []
    for g in gaps:
        per_gap.append(weighted_mean([
            (richness_score(g.get("existing_attempts", "")), 0.45),
            (richness_score(g.get("why_fail", "")), 0.45),
            (1.0 if g.get("caused_by") else 0.0, 0.10),
        ]))
    return clamp01(sum(per_gap) / len(per_gap))


def parse_related_work_blocks(text):
    if not text:
        return []
    chunks = re.split(r"\n(?=###\s*RW\d+)", text)
    blocks = []
    for c in chunks:
        m = re.match(r"###\s*RW(\d+):?\s*(.*)", c.strip())
        if not m:
            continue
        type_m = re.search(r"\*\*Type\*\*:\s*(.+)", c)
        delta_m = re.search(r"\*\*Delta\*\*:\s*(.+)", c)
        claims_m = re.search(r"\*\*Claims affected\*\*:\s*(.+)", c)
        ref_m = re.search(r"\*\*Ref\*\*:\s*(\S+)", c)  # optional DOI/S2-ID/arXiv-ID, cycle 3
        blocks.append({
            "id": f"RW{m.group(1)}",
            "title": m.group(2).strip(),
            "type": type_m.group(1).strip() if type_m else None,
            "delta": delta_m.group(1).strip() if delta_m else None,
            "claims_affected": [x.strip() for x in re.split(r"[,;]", claims_m.group(1))] if claims_m else [],
            "ref_id": ref_m.group(1).strip() if ref_m else None,
        })
    return blocks


def role_alignment_score(related_work_text, problem_ids, expected_papers):
    # Cycle-2 replacement for keyword-counted cross_layer_score, cycle-3 resolution function.
    blocks = parse_related_work_blocks(related_work_text)
    if not blocks:
        return 0.0
    complete = [b for b in blocks if b["type"] and b["delta"] and b["claims_affected"]]
    completeness = len(complete) / len(blocks)
    valid_claims = [
        b for b in complete
        if any(cid in problem_ids for cid in b["claims_affected"])
    ]
    claim_validity = len(valid_claims) / len(blocks)
    resolved = [
        b for b in blocks
        if resolve_external_reference({"title": b["title"], "ref_id": b.get("ref_id")}, expected_papers)
    ]
    external_grounding = len(resolved) / len(blocks)
    return weighted_mean([
        (completeness, 0.40),
        (claim_validity, 0.30),
        (external_grounding, 0.30),
    ])


def trace_external_grounding(exploration_tree_text, expected_papers):
    if not exploration_tree_text or not expected_papers:
        return False
    text_lower = exploration_tree_text.lower()
    for p in expected_papers[:100]:
        title = (p.get("title") or "").lower()
        if len(title) >= 8 and title in text_lower:
            return True
        for author in (p.get("authors") or [])[:3]:
            last = str(author).split()[-1].lower() if author else ""
            if len(last) >= 4 and last in text_lower:
                return True
    return False


def cross_layer_score(related_work, exploration_tree, problem_ids, expected_papers):
    rw_available = bool(related_work and related_work.get("text"))
    rw_text = related_work.get("text", "") if related_work else ""
    rw_role = role_alignment_score(rw_text, problem_ids, expected_papers) if rw_available else 0.0
    trace_available = bool(exploration_tree)
    trace_grounded = trace_external_grounding(str(exploration_tree) if exploration_tree else "", expected_papers)
    return weighted_mean([
        (1.0 if rw_available else 0.0, 0.20),
        (rw_role, 0.50),
        (1.0 if trace_available else 0.0, 0.10),
        (1.0 if trace_grounded else 0.0, 0.20),
    ])


def availability_score(problem, metadata_available, related_work, exploration_tree, focal_resolved,
                        undermind_available, search_available):
    problem_present = bool(problem)
    observations_ok = len(problem.get("observations", [])) >= 3 if problem else False
    gaps_ok = len(problem.get("gaps", [])) >= 2 if problem else False
    return weighted_mean([
        (1.0 if problem_present else 0.0, 0.22),
        (1.0 if observations_ok else 0.0, 0.14),
        (1.0 if gaps_ok else 0.0, 0.10),
        (1.0 if metadata_available else 0.0, 0.10),
        (1.0 if related_work and related_work.get("text") else 0.0, 0.14),
        (1.0 if exploration_tree else 0.0, 0.05),
        (1.0 if focal_resolved else 0.0, 0.13),
        (1.0 if undermind_available else 0.0, 0.05),
        (1.0 if search_available else 0.0, 0.07),
    ])


def reference_landscape_completeness(problem, expected_papers, related_work=None,
                                     exploration_tree=None, metadata_available=False,
                                     focal_resolved=False, undermind_available=False,
                                     search_available=True, relation_classification_ran=True):
    if not problem:
        return 0.0
    problem_ids = (
        [o.get("id") for o in problem.get("observations", [])]
        + [g.get("id") for g in problem.get("gaps", [])]
        + [a.get("id") for a in problem.get("assumptions", [])]
    )
    return clamp01(weighted_mean([
        (coverage_score(expected_papers), 0.28),
        (high_importance_miss_penalty(expected_papers, search_available, relation_classification_ran), 0.12),
        (contradiction_score(expected_papers, search_available), 0.14),
        (citation_footprint_score(problem), 0.12),
        (gap_specificity_score(problem), 0.12),
        (cross_layer_score(related_work or {}, exploration_tree, problem_ids, expected_papers), 0.13),
        (availability_score(problem, metadata_available, related_work or {}, exploration_tree,
                            focal_resolved, undermind_available, search_available), 0.09),
    ]))
```

## Component Interpretation

- `coverage_score`: main signal. It asks whether the independent landscape appears in the ARA, with a
  cap ensuring conceptual (uncited) coverage cannot supply more than 40% of covered weight, and — cycle
  3 — `near_direct` credit is halved-and-more (0.85 -> 0.35) when the match is a bare citation with no
  surrounding role context.
- `high_importance_miss_penalty`: separately punishes missing the very top of the importance-ranked
  canonical/contradictory/competing set, so a broad-but-shallow coverage average cannot hide a missed
  landmark paper. Cycle 3 adds a `relation_classification_ran` gate so an unclassified candidate pool
  scores `0.0`, not a free `1.0`.
- `contradiction_score`: protects against one-sided novelty narratives, gated so search failure cannot
  be rewarded as if it were a clean negative result, and — cycle 3 — no longer dependent on Undermind to
  populate `contradictory`/`competing` relation types.
- `citation_footprint_score`: penalizes abstract-only and thin problem evidence.
- `gap_specificity_score`: checks that missed/broken prior attempts are actually named and explained.
- `cross_layer_score`: checks whether `related_work.md` (via structural + externally-resolved
  `role_alignment_score`, now using a reachable token-set-ratio threshold or exact ID match) and the
  exploration trace (via title/author overlap with the real landscape) support the problem layer.
- `availability_score`: makes field, external-resolution, and search-success availability part of the
  score.

## Penalize-Don't-Skip Rules

- Missing `logic/problem.md`: final score `0.0`.
- Missing `PAPER.md` metadata: query generation falls back to problem terms, availability subscore
  loses metadata credit.
- Missing or empty `related_work.md`: `role_alignment_score` is `0.0` (not skipped), and cross-layer
  score loses the related-work-availability credit as well.
- Missing `trace/exploration_tree.yaml`: cross-layer score loses both the trace-availability and
  trace-grounding credit.
- Semantic Scholar cannot resolve focal paper: expected landscape is still built from search queries,
  but focal-resolution availability credit is zero.
- Semantic Scholar retrieval fails entirely (`search_available = False`): the expected landscape may be
  thin or empty, `contradiction_score`'s no-contradiction default drops from `0.65` to `0.10`,
  `high_importance_miss_penalty` returns `1.0` (nothing was constructible to penalize further beyond
  `coverage_score`'s own zero), and availability loses the search-success credit.
- Real candidates retrieved but relation classification never ran (`search_available = True`,
  `relation_classification_ran = False`): **cycle-3 addition.** `high_importance_miss_penalty` returns
  `0.0`, not `1.0` — this is a pipeline defect, not a benign landscape, and must not present as a clean
  pass.
- Undermind unavailable: Semantic Scholar-only mode runs, Step 3.5a's deterministic classifier assigns
  `relation_type` to every candidate so `contradiction_score` and `high_importance_miss_penalty` remain
  fully live, but search-depth availability credit is still zero.
- No expected papers returned: external coverage score is zero, `high_importance_miss_penalty` returns
  `1.0` (nothing high-stakes was constructible, so it does not compound the zero), not N/A, because a
  usable literature audit was not produced.
- Abstract-only evidence in observations materially reduces citation-footprint credit.
- An LLM-claimed conceptual match whose anchor does not actually appear in the cited excerpt
  (`has_specific_anchor` fails under the cycle-3 hardened extractor) is downgraded to `missed`, not left
  as a partial "trust the LLM" credit.
- A `near_direct` match with no role context (`role_context_ok = False`) is scored as
  `cited_but_unused` (0.35), not full `near_direct` credit (0.85) and not `missed` — it is real but weak
  evidence, penalized rather than skipped or over-credited.

## Why This Is Hard To Goodhart

The metric is hard to Goodhart because the target set is generated independently of the ARA. A
compiler cannot maximize the score by merely adding more citations; it must cover the papers that
external retrieval identifies as canonical, nearby, competing, or contradictory. The role-weighted
scoring further requires the right kind of use: contradictory work must be surfaced as contradiction
or tension, method neighbors must inform existing attempts, and canonical work must ground
observations.

Cycle 3 closes the four holes the round-2 judge found in cycle 2's execution of this independence
property:

- **The conceptual-coverage anchor can no longer be satisfied by vague, on-topic prose.** Cycle 2's
  extractor matched any capitalized word and any 2–5 digit number, so a compiler writing confidently
  about the right subfield ("Alzheimer... 2023... Network...") could clear the gate without engaging
  the paper's actual contribution. The cycle-3 extractor requires a decimal/percent/`n=` numeric form or
  a stoplist-filtered named entity — the exact class of vague prose the guard exists to stop no longer
  qualifies by construction.
- **`role_alignment_score`'s external-grounding term is no longer unreachable.** The cycle-2 Jaccard
  function at `>= 0.85` rewarded almost no honest `related_work.md` layer, which — paradoxically — made
  the score insensitive to whether entries were externally grounded at all (everyone scored near zero on
  this sub-term, honest and gamed ARAs alike). A reachable, real string-similarity function restores this
  term's discriminating power, with exact DOI/S2-ID matching preferred where available.
- **`high_importance_miss_penalty` and `contradiction_score` no longer collapse when Undermind is
  off.** A compiler could not previously game degraded-mode operation, but the metric's *own* pipeline
  could accidentally simulate a clean pass in that mode by leaving `relation_type` unset. Step 3.5a's
  deterministic classifier and the `relation_classification_ran` gate ensure a Semantic Scholar-only run
  is scored on its actual merits, not waved through as data-unavailable.
- **`near_direct` bibliography stuffing no longer earns near-full credit.** `field_role_signal` requires
  each near-match to sit in a field with real content beyond the citation token, so padding
  `related_work.md` with correctly-formatted author-year strings that are never actually engaged now
  scores as weak (`cited_but_unused`) evidence rather than strong coverage.

It also resists generic prose because gap specificity is scored separately from citation count. A gap
that says "prior studies are limited" receives little credit even if a bibliography is present.
Conversely, a concise but accurate problem statement can score well if it covers the expected
high-importance landscape, engages what it cites, and clearly states what prior approaches failed to
resolve.

## Composition With The Suite

M14 complements internal verifier-style metrics. Grounding metrics can say whether a cited quote
supports a local statement; this metric asks whether the artifact knew what it should have cited in
the first place. Problem-structure metrics can say whether Observations, Gaps, and Key Insight exist;
this metric asks whether they are situated in the true research neighborhood. Related-work metrics can
inspect dependency graph quality; this metric uses that layer as supporting evidence — via structural
role-alignment tied to the same externally generated landscape and, as of cycle 3, a resolution function
that actually reaches real matches — but preserves the primary pressure on external landscape recall.

The result is a net-new good-science signal: literature humility. Strong science does not only make
claims; it knows the field well enough to state what is already known, where the disagreement lies,
and which prior work might make the contribution less novel or less certain.

## End-to-End Runbook (cycle 3)

To make the workflow directly implementable, this is the single orchestrating pipeline. Every function
referenced was defined above; this section only sequences them with explicit types.

```python
def run_m14(ara_paths: dict, paper_metadata: dict | None, use_undermind: bool = True) -> dict:
    """
    ara_paths: {"problem_md": str, "related_work_md": str | None, "exploration_tree_yaml": str | None}
    paper_metadata: {"title", "authors", "year", "doi", "abstract", "keywords", "domain"} or None
    Returns: {"score": float, "components": dict, "expected_papers": list, "flags": dict}
    """
    # Step 1: parse the ARA's own problem landscape
    problem = parse_problem_md(ara_paths["problem_md"])  # -> ProblemLandscape or None
    if not problem:
        return {"score": 0.0, "components": {}, "expected_papers": [], "flags": {"problem_present": False}}

    related_work_text = read_if_exists(ara_paths.get("related_work_md"))
    exploration_tree_text = read_if_exists(ara_paths.get("exploration_tree_yaml"))
    metadata_available = bool(paper_metadata)

    # Step 2: build queries (tagged with provenance)
    queries = build_search_queries(problem, paper_metadata)  # list[{"text": str, "provenance": str}]

    # Step 3: retrieve from Semantic Scholar
    retrieval = semantic_scholar_retrieve(queries, paper_metadata)
    # retrieval: {"island": [...], "knn500": [...], "focal_resolved": bool, "search_available": bool,
    #             "query_rank_by_id": dict}
    expected_papers = dedupe_by_paper_id(retrieval["island"] + retrieval["knn500"])
    search_available = retrieval["search_available"]
    focal_year = paper_metadata.get("year") if paper_metadata else None

    # Step 4: optional Undermind retrieval, folded in before relation/importance assignment
    undermind_available = False
    if use_undermind:
        undermind_results = undermind_retrieve(paper_metadata, problem)  # None if unavailable
        if undermind_results:
            undermind_available = True
            expected_papers = dedupe_by_paper_id(expected_papers + resolve_via_semantic_scholar(undermind_results))

    # Step 3.5a: deterministic relation_type assignment (Undermind-supplied types are preserved)
    relation_classification_ran = False
    if search_available and expected_papers:
        expected_papers = classify_all_relations(expected_papers, retrieval["knn500"], focal_year)
        relation_classification_ran = True

    # Step 3.5: deterministic importance assignment (after relation_type is set)
    for p in expected_papers:
        p["importance"] = compute_importance(p, retrieval["query_rank_by_id"], retrieval["knn500"])

    # Coverage classification: direct/near_direct/conceptual/missed, with role_context_ok for
    # near_direct and has_specific_anchor-gated conceptual credit
    expected_papers = classify_coverage(
        expected_papers, problem, related_work_text,
        resolve_fn=resolve_external_reference, anchor_fn=has_specific_anchor,
        role_context_fn=near_direct_role_context_ok,
    )

    related_work = {"text": related_work_text} if related_work_text else None
    score = reference_landscape_completeness(
        problem, expected_papers, related_work=related_work,
        exploration_tree=exploration_tree_text, metadata_available=metadata_available,
        focal_resolved=retrieval["focal_resolved"], undermind_available=undermind_available,
        search_available=search_available, relation_classification_ran=relation_classification_ran,
    )

    problem_ids = (
        [o["id"] for o in problem["observations"]] + [g["id"] for g in problem["gaps"]]
        + [a["id"] for a in problem["assumptions"]]
    )
    components = {
        "coverage_score": coverage_score(expected_papers),
        "high_importance_miss_penalty": high_importance_miss_penalty(
            expected_papers, search_available, relation_classification_ran),
        "contradiction_score": contradiction_score(expected_papers, search_available),
        "citation_footprint_score": citation_footprint_score(problem),
        "gap_specificity_score": gap_specificity_score(problem),
        "cross_layer_score": cross_layer_score(related_work or {}, exploration_tree_text, problem_ids, expected_papers),
        "availability_score": availability_score(
            problem, metadata_available, related_work or {}, exploration_tree_text,
            retrieval["focal_resolved"], undermind_available, search_available),
    }

    return {
        "score": score,
        "components": components,
        "expected_papers": expected_papers,
        "flags": {
            "search_available": search_available,
            "relation_classification_ran": relation_classification_ran,
            "undermind_available": undermind_available,
            "focal_resolved": retrieval["focal_resolved"],
            "metadata_available": metadata_available,
        },
    }
```

`parse_problem_md`, `build_search_queries`, `semantic_scholar_retrieve`, `undermind_retrieve`,
`resolve_via_semantic_scholar`, `dedupe_by_paper_id`, `read_if_exists`, and `classify_coverage` are thin
I/O or bookkeeping wrappers around the API calls and prompts specified in Steps 2–4 and the Deterministic
Coverage Classification section; every scoring and classification decision they feed into is fully
specified above, so no part of the pipeline is left to an implementer's discretion.
