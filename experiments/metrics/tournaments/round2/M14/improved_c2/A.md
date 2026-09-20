# M14 Expansion: Reference-landscape completeness (cycle 2)

## Changes (cycle 2)

Direct responses to `critique_c1.md`'s five points on exp2 (Rank 1, this entry's basis):

1. **Hardened conceptual coverage.** The `conceptual` tier previously fired on any LLM judgment of
   "confidence >= 0.75 + one problem ID," which is exploitable by prose that name-drops concepts
   without engaging the external paper's actual contribution. It now additionally requires a
   **specific matching artifact** — a number, named method/model/dataset/cohort, or result that
   appears in *both* the external paper's abstract/TLDR and the covering ARA excerpt (`has_specific_anchor`,
   deterministic regex/string match, not LLM-judged). A **conceptual-credit cap** also caps conceptual
   coverage at 40% of total covered weight; excess conceptual weight is discounted so a "real"
   footprint must still be mostly direct/near-direct citations.
2. **Defined `importance`.** It is no longer a hand-waved `p.get("importance", 0.5)`. It is now
   computed deterministically at landscape-construction time as
   `importance = 0.5*relevance + 0.3*citation_percentile_in_knn500 + 0.2*relation_boost_norm`,
   documented in Step 3.5 below, with each term itself deterministically sourced (S2 similarity rank,
   citation-count percentile within the candidate pool, and a normalized relation-type boost).
3. **Replaced keyword-counting `cross_layer_score` with `role_alignment_score`.** The old version
   scored `related_work.md` by regex-counting words like "baseline/contradict/prior" — directly
   stuffable. It now parses typed `### RW{N}` blocks and requires `Type`, `Delta`, and
   `Claims affected` fields to be present, requires `Claims affected` to reference real
   `logic/problem.md` IDs, and — the external tie-in the critique demanded — requires each RW entry to
   **resolve by title-similarity to a real paper in the independently generated landscape**
   (`island`/`knn500`), not merely contain relation-flavored words. Trace lit-grounding is verified the
   same way: exploration-tree text is checked for actual overlap with external landscape paper
   titles/authors, not a generic `literature|related|search` regex.
4. **Gated the contradiction no-contradiction default on search success.** `contradiction_score`
   previously returned a flat `0.65` whenever no contradictory paper was found, conflating "search ran
   cleanly and genuinely found nothing" with "search failed." It now takes a `search_available` flag;
   the default is `0.65` only when search ran and returned a non-empty candidate pool, and drops to
   `0.10` when retrieval failed or returned nothing to search over.
5. **Added an asymmetric high-importance miss penalty.** `coverage_score` previously averaged all
   expected papers uniformly (importance-weighted, but still an average), so missing the single most
   canonical or contradictory neighbor cost little. A new `high_importance_miss_penalty` component
   scores the top-10-by-importance canonical/contradictory/competing papers specifically and penalizes
   missed coverage there directly, borrowed and adapted from exp1's `miss_penalty` per the critique's
   cycle-2 direction. It is a first-class weighted component in the final score, not folded silently
   into the average.

Also carried over and tightened: gap-specificity scoring, availability scoring, and all
penalize-don't-skip rules, with two additions (see the Penalize-Don't-Skip section) closing the
search-failure-vs-genuine-absence gap and making `role_alignment_score` explicitly zero-not-N/A when
`related_work.md` is missing.

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

## What It Must Not Reward

Do not reward:

- long citation lists that are only copied from the source paper but omit obvious search-neighbor
  work.
- citations without semantic use in the problem statement.
- generic claims of contradiction without identifying the contradicting study or result.
- over-inclusive bibliography dumps that mention many papers but do not connect them to observations,
  gaps, or assumptions.
- fabricated precision: if a title, DOI, or claim cannot be verified externally, it should not count
  as covered.
- vague "conceptual coverage" that only shares topic vocabulary with an external paper. Conceptual
  credit requires a concrete shared anchor (a number, named method/model/dataset/cohort, or specific
  result) — see `has_specific_anchor` below. Topic overlap alone is `missed`.
- a related-work or trace layer padded with relation-flavored vocabulary (e.g. sprinkling
  "baseline," "contradicts," "prior") that does not attach to a real, externally-resolvable paper.
- availability excuses. Missing `related_work.md`, inaccessible external search, abstract-only source
  material, or thin citation footprints all reduce the score.

## Failure Modes And Gaming Routes

The main gaming route is citation stuffing: adding many references to `Evidence` fields or
`related_work.md` without showing how they shape the problem. The metric counters this by measuring
both coverage and role alignment: each covered external paper must be tied to an Observation, Gap,
Existing attempt, Why they fail, Assumption, or a `related_work.md` entry with a real `Type`/`Delta`/
`Claims affected` triple that resolves to that paper.

A second route is source-paper anchoring: reproducing the paper's introduction citations while missing
nearby work that the paper did not cite. The external k-nearest-neighbor search counters this by
creating an independent expectation set, and the asymmetric `high_importance_miss_penalty` (cycle-2
addition) makes missing the very top of that set costly even when average coverage looks fine.

A third route is contradiction laundering: omitting negative, failed, or competing studies so that the
Key Insight looks cleaner than the field warrants. The contradiction subscore separately searches for
negative or competing findings and penalizes omissions — and, as of cycle 2, no longer lets a failed
search masquerade as "genuinely no contradictions exist" (see `search_available` gating).

A fourth route is generic gap language. The workflow penalizes gaps whose `Existing attempts` and
`Why they fail` fields lack named approaches, papers, cohorts, models, methods, or numeric result
contrasts.

A fifth route, closed in cycle 2, is **conceptual-coverage laundering**: describing an external
paper's topic in vague terms to earn "conceptual" credit without engaging its actual contribution, or
relying heavily on the conceptual tier instead of building a real citation footprint. The
`has_specific_anchor` gate and the 40%-of-covered-weight cap on conceptual credit close this.

A sixth route, also closed in cycle 2, is **cross-layer keyword stuffing**: writing a `related_work.md`
or `exploration_tree.yaml` full of relation-flavored words ("extends," "contradicts," "baseline") that
never attach to a resolvable external paper. `role_alignment_score` and `trace_external_grounding` both
require resolution against the independently generated landscape, not vocabulary presence.

## Inputs

Primary artifact:

- `logic/problem.md`
  - Observations: heading titles, `Statement`, `Evidence`, `Implication`
  - Gaps: heading titles, `Statement`, `Caused by`, `Existing attempts`, `Why they fail`
  - Key Insight: `Insight`, `Derived from`, `Enables`
  - Assumptions: `A{N}: ...`

Optional cross-layer artifacts, scored as available-or-missing inputs:

- `logic/related_work.md` from DATA_SHAPES section 6, if present in the ARA. Parsed as typed
  `### RW{N}` entries with `Type`, `Delta`, `Claims affected` fields.
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
Normalize citation strings to Semantic Scholar paper IDs where possible.

Also collect the set of valid problem-layer reference IDs, `problem_ids = {O1, O2, ..., G1, G2, ..., A1, ...}`,
used later by `role_alignment_score` to check that `related_work.md`'s `Claims affected` fields point
at real entries rather than invented ones.

### Step 2: Build Search Queries

Use `PAPER.md` when available. If not, derive from `problem.md` terms and penalize metadata absence in
the availability component.

Queries:

1. Exact paper query:

```text
"{paper_title}" {first_author_last_name}
```

2. Problem-neighborhood query:

```text
{top_8_keywords_from_problem_and_paper} {domain_terms} review OR benchmark OR comparison
```

3. Gap-specific queries, one per gap:

```text
{gap_statement_key_terms} {existing_attempts_key_terms} limitation OR failure OR contradictory OR inconsistent
```

4. Contradiction query:

```text
{paper_title_or_core_claim_terms} contradicts OR inconsistent OR negative result OR failed to replicate OR no improvement
```

### Step 3: Semantic Scholar Retrieval

Call Semantic Scholar:

- `GET /graph/v1/paper/search` for each query with `limit=100`, requesting
  `paperId,title,abstract,year,venue,authors,citationCount,influentialCitationCount,externalIds,references,citations,fieldsOfStudy,tldr`.
- If the focal paper is resolved, call:
  - `GET /graph/v1/paper/{paperId}/references`
  - `GET /graph/v1/paper/{paperId}/citations`
  - recommendations endpoint for similar papers, `limit=500`, if available.

Construct the independent expected landscape:

- `island`: focal paper references plus papers citing the focal paper, restricted to topically similar
  abstracts/titles.
- `knn500`: top 500 nearest papers from search/recommendations by embedding similarity to the focal
  paper and problem statement.
- `canonical`: top citation-count and influential-citation papers among `knn500`.
- `recent`: papers from focal year minus 3 through current year among `knn500`.
- `contradictory`: papers whose title/abstract or LLM classification indicate negative, inconsistent,
  failed-replication, or competing-result relation.

Set `search_available = True` if at least one query returned a non-error, non-empty result set;
`False` if all Semantic Scholar calls errored, timed out, or returned zero candidates across every
query. This flag is load-bearing for `contradiction_score` (Step 3.5 is downstream of it) — see
Penalize-Don't-Skip.

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

`importance` is attached to every expected-paper record before coverage classification runs. This
replaces the undefined `p.get("importance", 0.5)` placeholder from cycle 1 with a fully deterministic,
reproducible pipeline term.

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
before `importance` is computed, so Undermind-sourced papers are ranked on equal footing. If Undermind
is unavailable, set `undermind_available = False`; this lowers the search-depth component but does not
skip the metric.

## Deterministic Coverage Classification

For each expected external paper, classify whether the ARA covers it:

- `direct`: exact DOI/S2 ID/title match in `problem.md` or `related_work.md`.
- `near_direct`: same first author/year and high title similarity >= 0.90.
- `conceptual`: no citation match, but the paper's key idea/result is summarized in a relevant
  Observation/Gap/`related_work.md` entry **and** a specific matching artifact anchors that summary to
  the external paper (see `has_specific_anchor` below), determined by an LLM verifier with evidence
  text and confirmed deterministically.
- `missed`: no sufficient match.

### `has_specific_anchor`: the conceptual-coverage guard

Cycle-1's conceptual tier was gameable by vague topic-overlap prose. Cycle 2 requires a concrete,
checkable anchor shared between the external paper and the ARA excerpt claiming to cover it:

```python
def extract_anchors(text):
    if not text:
        return []
    anchors = set()
    anchors.update(re.findall(r"\b\d+(?:\.\d+)?\s?%|\bn\s?=\s?\d+\b|\b\d{2,5}\b", text))
    anchors.update(re.findall(r"\b[A-Z][a-zA-Z0-9]{2,}(?:-[A-Za-z0-9]+)?\b", text))  # named methods/models
    anchors.update(re.findall(r"\b[A-Z][a-zA-Z]+\d+\b", text))  # e.g. GPT4, p217
    return [a for a in anchors if len(a) >= 2]


def has_specific_anchor(external_paper, ara_excerpt):
    ext_text = (external_paper.get("abstract_or_tldr") or "") + " " + (external_paper.get("title") or "")
    anchors = extract_anchors(ext_text)
    if not anchors:
        return False
    excerpt_lower = ara_excerpt.lower()
    return any(a.lower() in excerpt_lower for a in anchors if len(a) >= 3)
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
  excerpt corresponding to the returned `covered_by_ids`. An LLM-claimed anchor that does not actually
  appear in the excerpt (checked deterministically) is discarded.
- otherwise `missed`.

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
    # expected_papers entries contain relation_type, importance in [0,1] (deterministic, Step 3.5),
    # and coverage. Applies the cycle-2 conceptual-credit cap.
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
        values.append({"direct": 1.0, "near_direct": 0.85, "conceptual": 0.55, "missed": 0.0}.get(cov, 0.0))

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


def high_importance_miss_penalty(expected_papers, top_k=10):
    # Cycle-2 addition: asymmetric penalty for missing the most important canonical/
    # contradictory/competing neighbors. Averaging alone (coverage_score) under-punishes
    # missing the single most important paper if many low-importance papers are covered.
    pool = [p for p in expected_papers if p.get("relation_type") in {"canonical", "contradictory", "competing"}]
    if not pool:
        return 1.0  # nothing high-stakes to miss; not this component's job to penalize
    top = sorted(pool, key=lambda p: p.get("importance", 0.0), reverse=True)[:top_k]
    total_importance = sum(p.get("importance", 0.0) for p in top)
    if total_importance == 0:
        return 1.0
    missed_importance = sum(p.get("importance", 0.0) for p in top if p.get("coverage", "missed") == "missed")
    return clamp01(1.0 - (missed_importance / total_importance))


def contradiction_score(expected_papers, search_available):
    contradictory = [p for p in expected_papers if p.get("relation_type") in {"contradictory", "competing"}]
    if not contradictory:
        # Cycle-2 gate: a clean search that genuinely found no contradictions earns partial
        # credit. A failed/empty search earns almost none — it must not look like a clean result.
        return 0.65 if search_available else 0.10
    vals = [{"direct": 1.0, "near_direct": 0.85, "conceptual": 0.60, "missed": 0.0}.get(p.get("coverage"), 0.0) for p in contradictory]
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
        blocks.append({
            "id": f"RW{m.group(1)}",
            "title": m.group(2).strip(),
            "type": type_m.group(1).strip() if type_m else None,
            "delta": delta_m.group(1).strip() if delta_m else None,
            "claims_affected": [x.strip() for x in re.split(r"[,;]", claims_m.group(1))] if claims_m else [],
        })
    return blocks


def title_similarity(a, b):
    # Placeholder for a real string-similarity function (e.g. token-set ratio); >= 0.85 counts as a match.
    a_tokens, b_tokens = set(a.lower().split()), set(b.lower().split())
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def role_alignment_score(related_work_text, problem_ids, expected_papers):
    # Cycle-2 replacement for keyword-counted cross_layer_score. Requires structural
    # completeness AND resolution against the independently generated external landscape.
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
        if any(title_similarity(b["title"], p.get("title", "")) >= 0.85 for p in expected_papers)
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
                                     search_available=True):
    if not problem:
        return 0.0
    problem_ids = (
        [o.get("id") for o in problem.get("observations", [])]
        + [g.get("id") for g in problem.get("gaps", [])]
        + [a.get("id") for a in problem.get("assumptions", [])]
    )
    return clamp01(weighted_mean([
        (coverage_score(expected_papers), 0.28),
        (high_importance_miss_penalty(expected_papers), 0.12),
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
  cap ensuring conceptual (uncited) coverage cannot supply more than 40% of covered weight.
- `high_importance_miss_penalty`: cycle-2 addition. Separately punishes missing the very top of the
  importance-ranked canonical/contradictory/competing set, so a broad-but-shallow coverage average
  cannot hide a missed landmark paper.
- `contradiction_score`: protects against one-sided novelty narratives, now gated so search failure
  cannot be rewarded as if it were a clean negative result.
- `citation_footprint_score`: penalizes abstract-only and thin problem evidence.
- `gap_specificity_score`: checks that missed/broken prior attempts are actually named and explained.
- `cross_layer_score`: checks whether `related_work.md` (via structural + externally-resolved
  `role_alignment_score`) and the exploration trace (via title/author overlap with the real landscape)
  support the problem layer. No longer scorable by keyword density alone.
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
  thin or empty, `contradiction_score`'s no-contradiction default drops from `0.65` to `0.10` instead
  of being treated as a clean negative result, and availability loses the search-success credit. This
  closes the cycle-1 gap where a failed search and a genuinely contradiction-free field scored
  identically.
- Undermind unavailable: Semantic Scholar-only mode runs, but search-depth availability credit is
  zero.
- No expected papers returned: external coverage score is zero, `high_importance_miss_penalty` returns
  `1.0` (nothing high-stakes was constructible, so it does not compound the zero), not N/A, because a
  usable literature audit was not produced.
- Abstract-only evidence in observations materially reduces citation-footprint credit.
- An LLM-claimed conceptual match whose anchor does not actually appear in the cited excerpt
  (`has_specific_anchor` fails) is downgraded to `missed`, not left as a partial "trust the LLM" credit.

## Why This Is Hard To Goodhart

The metric is hard to Goodhart because the target set is generated independently of the ARA. A
compiler cannot maximize the score by merely adding more citations; it must cover the papers that
external retrieval identifies as canonical, nearby, competing, or contradictory. The role-weighted
scoring further requires the right kind of use: contradictory work must be surfaced as contradiction
or tension, method neighbors must inform existing attempts, and canonical work must ground
observations.

Cycle 2 closes the specific holes a prior judge found in this independence property:

- **The conceptual-coverage tier can no longer be gamed by vague prose.** Crediting a paraphrased
  finding without a formal citation is valuable — it rewards real landscape awareness over citation
  formatting — but only if the paraphrase demonstrably engages the external paper's specific
  contribution. `has_specific_anchor` requires a concrete shared number, method, dataset, or named
  result, and the 40%-of-covered-weight cap prevents a compiler from substituting cheap conceptual
  credit for real engagement at scale.
- **Averaging can no longer hide a landmark miss.** `high_importance_miss_penalty` makes it costly to
  skip the single most-cited or most directly contradictory neighbor even while padding coverage with
  many low-importance papers.
- **A stalled or failed external search can no longer pass as a clean result.** `contradiction_score`
  and `availability_score` are both keyed to `search_available`, so an ARA compiled under degraded
  external access is scored as degraded, not as if the literature were quietly free of tension.
- **The related-work and trace layers can no longer be padded with relation vocabulary.**
  `role_alignment_score` requires structurally complete entries whose claims resolve to real
  `problem.md` IDs and whose subject papers resolve, by title similarity, to the independently
  generated landscape. Trace grounding likewise requires literal overlap with real external paper
  titles/authors, not a "did it mention the word literature" check.

It also resists generic prose because gap specificity is scored separately from citation count. A gap
that says "prior studies are limited" receives little credit even if a bibliography is present.
Conversely, a concise but accurate problem statement can score well if it covers the expected
high-importance landscape and clearly states what prior approaches failed to resolve.

## Composition With The Suite

M14 complements internal verifier-style metrics. Grounding metrics can say whether a cited quote
supports a local statement; this metric asks whether the artifact knew what it should have cited in
the first place. Problem-structure metrics can say whether Observations, Gaps, and Key Insight exist;
this metric asks whether they are situated in the true research neighborhood. Related-work metrics can
inspect dependency graph quality; this metric uses that layer as supporting evidence — now via
structural role-alignment tied to the same externally generated landscape — but preserves the primary
pressure on external landscape recall.

The result is a net-new good-science signal: literature humility. Strong science does not only make
claims; it knows the field well enough to state what is already known, where the disagreement lies,
and which prior work might make the contribution less novel or less certain.
