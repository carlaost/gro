# M14 Expansion: Reference-landscape completeness

## Indicator

Reference-landscape completeness asks whether the ARA's problem framing is grounded in the real prior-work neighborhood around the paper, rather than only in the source paper's own selective citations or a generic background summary. A good `logic/problem.md` should surface the empirical observations, gaps, failed attempts, and key insight in a way that is recognizably connected to the broader literature landscape: canonical precursors, nearest-neighbor work, competing approaches, and work that contradicts or weakens the paper's motivating gap.

This metric is intentionally external-facing. Many internal ARA checks can verify that a statement has a source quote or that problem fields are structurally present. They cannot tell whether the compiler missed the papers that a competent literature search would immediately find. M14 fills that hole by comparing the ARA's cited and named landscape against an independently generated landscape from Semantic Scholar and an optional deep-search agent such as Undermind.

## What It Rewards

Reward high scores when:

- `logic/problem.md` contains specific, citable observations drawn from prior work rather than abstract-only background sentences.
- observations and gaps name concrete prior attempts, not just "prior work is limited."
- the cited literature covers canonical, recent, and methodologically adjacent work.
- the ARA names contradicting or tension-producing findings where they exist.
- the Key Insight is positioned as resolving a real landscape-level gap, not merely restating the paper's method.
- cross-layer `logic/related_work.md` confirms a typed dependency graph with enough breadth to support the problem framing.
- cross-layer `trace/exploration_tree.yaml` shows that literature exploration was part of the compiler trajectory, especially when the source paper's claim depends on novelty, superiority, or gap claims.

## What It Must Not Reward

Do not reward:

- long citation lists that are only copied from the source paper but omit obvious search-neighbor work.
- citations without semantic use in the problem statement.
- generic claims of contradiction without identifying the contradicting study or result.
- over-inclusive bibliography dumps that mention many papers but do not connect them to observations, gaps, or assumptions.
- fabricated precision: if a title, DOI, or claim cannot be verified externally, it should not count as covered.
- availability excuses. Missing `related_work.md`, inaccessible external search, abstract-only source material, or thin citation footprints all reduce the score.

## Failure Modes And Gaming Routes

The main gaming route is citation stuffing: adding many references to `Evidence` fields or `related_work.md` without showing how they shape the problem. The metric counters this by measuring both coverage and role alignment: each covered external paper must be tied to an Observation, Gap, Existing attempt, Why they fail, Assumption, or related-work dependency type.

A second route is source-paper anchoring: reproducing the paper's introduction citations while missing nearby work that the paper did not cite. The external k-nearest-neighbor search counters this by creating an independent expectation set.

A third route is contradiction laundering: omitting negative, failed, or competing studies so that the Key Insight looks cleaner than the field warrants. The contradiction subscore separately searches for negative or competing findings and penalizes omissions.

A fourth route is generic gap language. The workflow penalizes gaps whose `Existing attempts` and `Why they fail` fields lack named approaches, papers, cohorts, models, methods, or numeric result contrasts.

## Inputs

Primary artifact:

- `logic/problem.md`
  - Observations: heading titles, `Statement`, `Evidence`, `Implication`
  - Gaps: heading titles, `Statement`, `Caused by`, `Existing attempts`, `Why they fail`
  - Key Insight: `Insight`, `Derived from`, `Enables`
  - Assumptions: `A{N}: ...`

Optional cross-layer artifacts, scored as available-or-missing inputs:

- `logic/related_work.md` from DATA_SHAPES section 6, if present in the ARA.
- `trace/exploration_tree.yaml` from DATA_SHAPES section 8, if present in the ARA.
- `PAPER.md` metadata if needed to form exact search queries: title, authors, year, DOI, abstract, keywords, domain.

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

Extract citation candidates from all fields using DOI regexes, author-year patterns, bracketed numeric references where resolvable through `related_work.md`, and named study/model/dataset strings. Normalize citation strings to Semantic Scholar paper IDs where possible.

### Step 2: Build Search Queries

Use `PAPER.md` when available. If not, derive from `problem.md` terms and penalize metadata absence in the availability component.

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

- `GET /graph/v1/paper/search` for each query with `limit=100`, requesting `paperId,title,abstract,year,venue,authors,citationCount,influentialCitationCount,externalIds,references,citations,fieldsOfStudy,tldr`.
- If the focal paper is resolved, call:
  - `GET /graph/v1/paper/{paperId}/references`
  - `GET /graph/v1/paper/{paperId}/citations`
  - recommendations endpoint for similar papers, `limit=500`, if available.

Construct the independent expected landscape:

- `island`: focal paper references plus papers citing the focal paper, restricted to topically similar abstracts/titles.
- `knn500`: top 500 nearest papers from search/recommendations by embedding similarity to the focal paper and problem statement.
- `canonical`: top citation-count and influential-citation papers among `knn500`.
- `recent`: papers from focal year minus 3 through current year among `knn500`.
- `contradictory`: papers whose title/abstract or LLM classification indicate negative, inconsistent, failed-replication, or competing-result relation.

If the focal paper cannot be resolved, still build `knn500` from title/domain/problem queries and assign the focal-resolution subscore to zero.

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

Require JSON output. Resolve returned works through Semantic Scholar. If Undermind is unavailable, set `undermind_available = False`; this lowers the search-depth component but does not skip the metric.

## Deterministic Coverage Classification

For each expected external paper, classify whether the ARA covers it:

- `direct`: exact DOI/S2 ID/title match in `problem.md` or `related_work.md`.
- `near_direct`: same first author/year and high title similarity >= 0.90.
- `conceptual`: no citation match, but the paper's key idea/result is summarized in a relevant Observation/Gap, determined by an LLM verifier with evidence text.
- `missed`: no sufficient match.

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
  "rationale": "one sentence",
  "confidence": 0.0-1.0
}

Use conceptual only when a specific result, method, dataset, or contradiction from the external paper
is present. Generic topic overlap is missed.
```

Convert LLM output deterministically:

- `direct` from string/ID matching overrides LLM.
- `conceptual` counts only if `confidence >= 0.75` and at least one concrete problem ID is returned.
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
    # expected_papers entries contain relation_type, importance in [0,1], and coverage.
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
        weights.append(max(0.2, p.get("importance", 0.5)) * relation_boost)
    values = []
    for p in expected_papers:
        cov = p.get("coverage", "missed")
        values.append({"direct": 1.0, "near_direct": 0.85, "conceptual": 0.55, "missed": 0.0}.get(cov, 0.0))
    return clamp01(sum(v * w for v, w in zip(values, weights)) / sum(weights))


def contradiction_score(expected_papers):
    contradictory = [p for p in expected_papers if p.get("relation_type") in {"contradictory", "competing"}]
    if not contradictory:
        # No known contradiction is acceptable, but only partial credit because search may be incomplete.
        return 0.65
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


def cross_layer_score(related_work, exploration_tree):
    rw_available = bool(related_work and related_work.get("text"))
    trace_available = bool(exploration_tree)
    rw_text = related_work.get("text", "") if related_work else ""
    rw_citation_count = len(re.findall(r"10\.\d{4,9}/|[A-Z][A-Za-z'\-]+ et al\.,?\s*(19|20)\d{2}", rw_text))
    rw_relation_words = len(re.findall(r"extends|contrasts|depends|compares|baseline|contradict|prior|concurrent|review", rw_text, re.I))
    trace_text = str(exploration_tree) if exploration_tree else ""
    trace_lit = bool(re.search(r"literature|related|search|citation|prior|semantic scholar|undermind", trace_text, re.I))
    return weighted_mean([
        (1.0 if rw_available else 0.0, 0.25),
        (min(rw_citation_count / 25.0, 1.0), 0.25),
        (min(rw_relation_words / 20.0, 1.0), 0.20),
        (1.0 if trace_available else 0.0, 0.10),
        (1.0 if trace_lit else 0.0, 0.20),
    ])


def availability_score(problem, metadata_available, related_work, exploration_tree, focal_resolved, undermind_available):
    problem_present = bool(problem)
    observations_ok = len(problem.get("observations", [])) >= 3 if problem else False
    gaps_ok = len(problem.get("gaps", [])) >= 2 if problem else False
    return weighted_mean([
        (1.0 if problem_present else 0.0, 0.25),
        (1.0 if observations_ok else 0.0, 0.15),
        (1.0 if gaps_ok else 0.0, 0.10),
        (1.0 if metadata_available else 0.0, 0.10),
        (1.0 if related_work and related_work.get("text") else 0.0, 0.15),
        (1.0 if exploration_tree else 0.0, 0.05),
        (1.0 if focal_resolved else 0.0, 0.15),
        (1.0 if undermind_available else 0.0, 0.05),
    ])


def reference_landscape_completeness(problem, expected_papers, related_work=None,
                                     exploration_tree=None, metadata_available=False,
                                     focal_resolved=False, undermind_available=False):
    if not problem:
        return 0.0
    return clamp01(weighted_mean([
        (coverage_score(expected_papers), 0.34),
        (contradiction_score(expected_papers), 0.16),
        (citation_footprint_score(problem), 0.14),
        (gap_specificity_score(problem), 0.13),
        (cross_layer_score(related_work or {}, exploration_tree), 0.13),
        (availability_score(problem, metadata_available, related_work or {}, exploration_tree,
                            focal_resolved, undermind_available), 0.10),
    ]))
```

## Component Interpretation

- `coverage_score`: main signal. It asks whether the independent landscape appears in the ARA.
- `contradiction_score`: protects against one-sided novelty narratives.
- `citation_footprint_score`: penalizes abstract-only and thin problem evidence.
- `gap_specificity_score`: checks that missed/broken prior attempts are actually named and explained.
- `cross_layer_score`: checks whether related-work and exploration artifacts support the problem layer.
- `availability_score`: makes field and external-resolution availability part of the score.

## Penalize-Don't-Skip Rules

- Missing `logic/problem.md`: final score `0.0`.
- Missing `PAPER.md` metadata: query generation falls back to problem terms, availability subscore loses metadata credit.
- Missing or empty `related_work.md`: cross-layer score loses related-work credit.
- Missing `trace/exploration_tree.yaml`: cross-layer score loses exploration credit.
- Semantic Scholar cannot resolve focal paper: expected landscape is still built from search queries, but focal-resolution availability credit is zero.
- Undermind unavailable: Semantic Scholar-only mode runs, but search-depth availability credit is zero.
- No expected papers returned: external coverage score is zero, not N/A, because a usable literature audit was not produced.
- Abstract-only evidence in observations materially reduces citation-footprint credit.

## Why This Is Hard To Goodhart

The metric is hard to Goodhart because the target set is generated independently of the ARA. A compiler cannot maximize the score by merely adding more citations; it must cover the papers that external retrieval identifies as canonical, nearby, competing, or contradictory. The role-weighted scoring further requires the right kind of use: contradictory work must be surfaced as contradiction or tension, method neighbors must inform existing attempts, and canonical work must ground observations.

It also resists generic prose because gap specificity is scored separately from citation count. A gap that says "prior studies are limited" receives little credit even if a bibliography is present. Conversely, a concise but accurate problem statement can score well if it covers the expected high-importance landscape and clearly states what prior approaches failed to resolve.

## Composition With The Suite

M14 complements internal verifier-style metrics. Grounding metrics can say whether a cited quote supports a local statement; this metric asks whether the artifact knew what it should have cited in the first place. Problem-structure metrics can say whether Observations, Gaps, and Key Insight exist; this metric asks whether they are situated in the true research neighborhood. Related-work metrics can inspect dependency graph quality; this metric uses that layer as supporting evidence but preserves the primary pressure on external landscape recall.

The result is a net-new good-science signal: literature humility. Strong science does not only make claims; it knows the field well enough to state what is already known, where the disagreement lies, and which prior work might make the contribution less novel or less certain.
