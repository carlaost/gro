# M17 Expansion: Novelty vs Literature (+ Impact)

## Metric intent

This metric scores whether the ARA's problem layer identifies a genuinely non-routine scientific move: a claim, gap, method, concept, or insight that was not already done in the external literature, and whose solution would matter scientifically or societally. The primary artifact is `logic/problem.md`, with cross-checks into `logic/claims.md`, `logic/concepts.md`, `logic/related_work.md`, and `logic/solution/`.

The metric is deliberately not a generic internal consistency verifier. Internal checks can ask whether the problem statement is coherent, whether gaps cite observations, or whether claims are grounded. M17 asks a different question: after turning the ARA's stated problem, key insight, method move, and claims into search queries against external literature, does the contribution still look new, well-scoped, and worth solving?

Good science is not just "new words." The metric rewards novelty that is anchored to a real gap and bounded by prior art. It should score high when:

- Observations and gaps identify a specific prior-work frontier rather than generic background.
- The Key Insight states the creative leap, not merely a method name.
- Related work captures close predecessors and gives technical deltas, allowing novelty to be evaluated against the right comparison set.
- Claims and solution files show that the novelty is attached to a testable result or method, not only rhetorical framing.
- External literature search finds no close predecessor that already made the same claim/method/concept move.
- Solving the gap would change scientific understanding, measurement practice, intervention choice, benchmark behavior, or downstream societal/clinical/technical decisions.

It should not reward:

- A paper being first only because the ARA used narrow synonyms.
- Trivial parameter, cohort, organism, dataset, or venue changes unless the artifact explains why those changes alter the scientific question.
- "No one has studied X in Y" gaps where Y is an arbitrary slice and the impact-if-solved is weak.
- Replication, validation, or negative-result work pretending to be conceptual novelty. Replication can score well on impact and literature positioning, but not on "never done before."
- Thin abstract-only problem statements that cannot expose prior attempts, why they fail, or the actual insight.

## Failure modes and gaming routes

The main Goodhart route is to write a hyper-specific gap so no exact prior paper matches it. The metric counters this by searching at several abstraction levels: exact claim, normalized concept/method, and broader problem family. A "novel" claim loses credit if it differs only by minor domain substitution, sample choice, dataset, or terminology while preserving the same mechanism and test.

Another route is to omit close prior work. The metric treats missing or shallow `related_work.md` as evidence against novelty, not as a lack of contradicting evidence. If related work has few RW blocks, no brief citation footprint, no baselines, or deltas like "prior work is limited," the external search penalty increases.

A third route is impact inflation. Impact is not scored from adjectives. It is scored from the artifact's claims, affected scientific decisions, constraints, and external literature signals such as citation context, guideline relevance, clinical-trial relevance, benchmark prevalence, disease burden, or method reuse. Unsupported "important problem" language does little.

## Inputs

Mandatory primary input:

- `logic/problem.md`: Observations, Gaps, Key Insight, Assumptions.

Cross-layer inputs:

- `logic/claims.md`: claim statements, falsification criteria, evidence basis, dependencies, tags.
- `logic/concepts.md`: technical definitions, notation, boundary conditions, related concepts.
- `logic/related_work.md`: RW blocks, type, DOI/arXiv ID, technical delta, adopted elements, affected claims, brief citation footprint.
- `logic/solution/constraints.md` and warranted method files under `logic/solution/`: method description, boundary conditions, assumptions, limitations, heuristics if present.

Missing files or thin fields are never skipped. They receive explicit zero or low availability/richness sub-scores and lower confidence in external novelty.

## Generation / compute workflow

### Step 1: Parse artifacts deterministically

Parse the ARA markdown into structured records:

- Observations: id, title, statement, evidence, implication.
- Gaps: id, title, statement, caused-by ids, existing attempts, why-they-fail.
- Key Insight: insight, derived-from ids, enables.
- Assumptions: id, text.
- Claims: id, title, statement, falsification criteria, proof ids, evidence basis, interpretation, dependencies, sources, tags.
- Concepts: term, notation, definition, boundary conditions, related concepts.
- Related work: RW id, citation title string, DOI/arXiv, type, what changed, why, claims affected, adopted elements; plus count and roles of brief references.
- Solution: constraints, assumptions, known limitations, method headings and method prose.

Availability penalties:

- Missing `problem.md`: final score <= 0.10.
- Missing Key Insight block: final score <= 0.25.
- No Gaps or only generic gaps: gap specificity sub-score <= 0.30.
- Missing `related_work.md` or fewer than 3 technical RW blocks: literature positioning sub-score <= 0.35.
- Abstract-only signals (`Evidence: Abstract` dominating observations, claims grounded only to abstract, no method file beyond bare constraints): final score multiplied by 0.65.

### Step 2: Build novelty units

Create 4 to 12 novelty units. Each unit is a compact proposition to check externally.

Unit types:

- `gap`: each Gaps statement plus existing attempts and why they fail.
- `insight`: the Key Insight plus Enables.
- `claim`: each central claim, prioritizing claims referenced by Gaps or RW deltas.
- `method`: solution-method moves not reducible to generic tools.
- `concept`: paper-specific technical terms whose definitions appear central to the insight or claims.

Use an LLM only to normalize units, not to score them directly.

Prompt:

```text
You are extracting literature-checkable novelty units from an ARA.
Return JSON array. Each item must have:
id, type in [gap, insight, claim, method, concept],
canonical_statement (one sentence),
essential_entities (3-8 strings),
method_or_mechanism (0-3 strings),
outcome_or_objective (0-3 strings),
broader_family (one sentence),
near_duplicate_criteria (one sentence),
minor_variation_criteria (one sentence).
Do not invent content. Use only the supplied ARA text.

ARA text:
<problem, selected claims, concepts, related_work deltas, solution method excerpts>
```

Reject malformed JSON. If the LLM fails, fall back to deterministic units from headings and field text. Penalize normalization quality by 0.15.

### Step 3: External search plan

For each novelty unit, run three query classes:

1. Exact-proposition query:
   - `"<essential entity 1>" "<essential entity 2>" "<outcome>" "<method/mechanism>"`
2. Broader-family query:
   - `<broader family terms> <method/mechanism> <outcome/objective>`
3. Prior-art delta query:
   - `<gap title terms> "systematic review" OR "review" OR "benchmark" OR "meta-analysis" OR "trial" OR "dataset"` as domain-appropriate.

External calls:

- `[sem] semantic_scholar.search(query, limit=20)` for title, abstract, venue, year, DOI, citationCount, influentialCitationCount.
- `[sem] semantic_scholar.paper(doi_or_paperId)` for abstracts and references of high-similarity candidates.
- Optional `[ext] Crossref/OpenAlex` if DOI metadata is missing.
- Optional `[ext] clinicaltrials.gov` for clinical intervention, diagnostic, or device claims: query by disease, intervention/test, and endpoint.
- Optional `[ext] benchmark/dataset registry` for ML benchmark novelty when the ARA's solution or claims are benchmark-centered.

The workflow records all queries and top candidates; absence of search results is not treated as proof of novelty unless query breadth and artifact richness are adequate.

### Step 4: Candidate similarity classification

For each returned candidate, compute lexical and semantic similarity to the novelty unit.

Deterministic features:

- Entity overlap: Jaccard over normalized essential entities.
- Mechanism overlap: Jaccard over method/mechanism strings.
- Objective overlap: Jaccard over outcome/objective strings.
- Year relation: candidate older than source paper year, same year, or newer.
- Citation proximity: candidate DOI appears in `related_work.md`, sources, or source-paper citation footprint.
- Title/abstract embedding cosine similarity if embeddings are available; otherwise token cosine over TF-IDF.

LLM classification prompt for top 5 candidates per unit:

```text
Compare an ARA novelty unit to a candidate prior work.
Return JSON only:
{
  "relation": "same_done_before" | "near_duplicate" | "minor_variation" | "partial_predecessor" | "background_only" | "unrelated",
  "reason": "one sentence",
  "overlap_axes": ["problem", "claim", "method", "concept", "data", "outcome"],
  "missing_from_candidate": ["..."],
  "missing_from_ara_unit": ["..."]
}

Novelty unit:
<unit JSON>

Candidate:
title: <title>
year: <year>
abstract: <abstract>
known relation from related_work.md if any: <RW delta or none>
```

The LLM output is converted to numeric prior-art penalty:

- `same_done_before`: 1.00 penalty
- `near_duplicate`: 0.80
- `minor_variation`: 0.55
- `partial_predecessor`: 0.30
- `background_only`: 0.10
- `unrelated`: 0.00

If a candidate predates the paper and is absent from `related_work.md`, add a 0.10 omission penalty for that unit, capped at 0.25. If the candidate is already in `related_work.md` with a precise delta explaining what is new, reduce the penalty by 0.10, because the ARA has scoped the novelty honestly.

### Step 5: Impact-if-solved scoring

Score each unit's impact on four axes, each 0 to 1:

- Scientific leverage: would resolving this gap alter theory, causal mechanism, measurement validity, model selection, or interpretation of a field?
- Decision leverage: would it change clinical, policy, engineering, benchmark, or experimental-design decisions?
- Scope: how broad is the affected population, dataset family, method family, biological system, or research community?
- Tractability-to-value: are claims and methods concrete enough that solving the gap produces reusable knowledge rather than an isolated observation?

Signals come from ARA fields first: `Enables`, claim falsification criteria, evidence basis, RW type/deltas, solution constraints, and concept boundary conditions. External signals can raise or lower the score: high citation/influential-citation counts for the problem family, clinical-trial/guideline relevance, benchmark prevalence, or many imported/baselined works in related literature. Thin ARA support caps impact at 0.50 even if external literature suggests the domain is broadly important.

### Step 6: Compose sub-scores

Sub-scores:

- `availability_richness` (0.15): required fields present, non-generic, not abstract-only.
- `gap_specificity` (0.15): gaps name what is missing, prior attempts, and failure modes.
- `external_novelty` (0.35): inverse of done-before penalties across units, weighted toward insight and central claims.
- `literature_positioning` (0.15): related work has close predecessors, typed deltas, baselines/imports/bounds, and brief footprint.
- `impact_if_solved` (0.15): impact axes above.
- `scope_honesty` (0.05): constraints and assumptions prevent overclaiming; replication/validation is labeled as such.

The final score is multiplied by penalties for artifact thinness, omitted close prior work, and unsupported impact inflation.

## Reference Python scoring function

```python
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchCandidate:
    title: str
    year: int | None
    abstract: str = ""
    doi: str | None = None
    relation: str = "unrelated"
    in_related_work: bool = False


@dataclass
class NoveltyUnit:
    id: str
    type: str
    text: str
    weight: float = 1.0
    candidates: list[SearchCandidate] = field(default_factory=list)
    impact_axes: dict[str, float] = field(default_factory=dict)


RELATION_PENALTY = {
    "same_done_before": 1.00,
    "near_duplicate": 0.80,
    "minor_variation": 0.55,
    "partial_predecessor": 0.30,
    "background_only": 0.10,
    "unrelated": 0.00,
}


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def present_text(x: Any) -> str:
    return x if isinstance(x, str) else ""


def genericness_penalty(text: str) -> float:
    t = text.lower()
    generic = [
        "limited", "not well understood", "unclear", "further research",
        "prior work is limited", "not specified", "unknown"
    ]
    hits = sum(1 for g in generic if g in t)
    length_bonus = 1.0 if len(t.split()) >= 18 else 0.65
    return clamp((hits * 0.12) + (1.0 - length_bonus) * 0.30)


def field_richness(fields: list[str]) -> float:
    if not fields:
        return 0.0
    vals = []
    for f in fields:
        text = present_text(f).strip()
        if not text:
            vals.append(0.0)
        else:
            vals.append(clamp((len(text.split()) / 24.0) - genericness_penalty(text)))
    return sum(vals) / len(vals)


def score_availability(artifact: dict[str, Any]) -> tuple[float, dict[str, float]]:
    problem = artifact.get("problem") or {}
    claims = artifact.get("claims") or []
    concepts = artifact.get("concepts") or []
    related = artifact.get("related_work") or []
    solution = artifact.get("solution") or {}

    obs = problem.get("observations") or []
    gaps = problem.get("gaps") or []
    insight = problem.get("key_insight") or {}

    components = {
        "observations": clamp(len(obs) / 3.0),
        "gaps": clamp(len(gaps) / 2.0),
        "key_insight": 1.0 if insight.get("insight") else 0.0,
        "claims": clamp(len(claims) / 4.0),
        "concepts": clamp(len(concepts) / 5.0),
        "related_work": clamp(len([r for r in related if r.get("type")]) / 6.0),
        "solution": 1.0 if solution.get("constraints") or solution.get("methods") else 0.0,
    }
    score = sum(components.values()) / len(components)
    return clamp(score), components


def score_gap_specificity(problem: dict[str, Any]) -> float:
    gaps = problem.get("gaps") or []
    if not gaps:
        return 0.0
    vals = []
    for g in gaps:
        fields = [
            g.get("statement", ""),
            g.get("existing_attempts", ""),
            g.get("why_they_fail", ""),
        ]
        caused = g.get("caused_by") or []
        vals.append(clamp(0.85 * field_richness(fields) + 0.15 * clamp(len(caused) / 2.0)))
    return sum(vals) / len(vals)


def score_lit_positioning(related_work: list[dict[str, Any]]) -> float:
    if not related_work:
        return 0.0
    full = [r for r in related_work if r.get("id", "").startswith("RW")]
    typed = [r for r in full if r.get("type")]
    close_types = [r for r in typed if any(k in r.get("type", "").lower()
                                           for k in ["imports", "baseline", "extends", "bounds", "refutes"])]
    delta_rich = field_richness(
        [r.get("what_changed", "") + " " + r.get("why", "") + " " + r.get("adopted_elements", "")
         for r in close_types]
    )
    brief_count = sum(1 for r in related_work if r.get("brief", False))
    return clamp(
        0.30 * clamp(len(full) / 8.0)
        + 0.25 * clamp(len(close_types) / 5.0)
        + 0.30 * delta_rich
        + 0.15 * clamp(brief_count / 10.0)
    )


def unit_prior_art_penalty(unit: NoveltyUnit, source_year: int | None = None) -> float:
    if not unit.candidates:
        return 0.25  # no evidence gathered; penalize uncertainty, do not skip
    penalties = []
    omission = 0.0
    for c in unit.candidates:
        p = RELATION_PENALTY.get(c.relation, 0.0)
        if c.in_related_work:
            p = max(0.0, p - 0.10)
        elif source_year and c.year and c.year <= source_year and p >= 0.30:
            omission += 0.10
        penalties.append(p)
    return clamp(max(penalties) + min(omission, 0.25))


def score_external_novelty(units: list[NoveltyUnit], source_year: int | None = None) -> float:
    if not units:
        return 0.0
    weighted = []
    for u in units:
        type_boost = {"insight": 1.4, "claim": 1.2, "gap": 1.1, "method": 1.1, "concept": 0.8}.get(u.type, 1.0)
        novelty = 1.0 - unit_prior_art_penalty(u, source_year)
        weighted.append((clamp(novelty), u.weight * type_boost))
    denom = sum(w for _, w in weighted) or 1.0
    return clamp(sum(v * w for v, w in weighted) / denom)


def score_impact(units: list[NoveltyUnit], artifact_richness: float) -> float:
    if not units:
        return 0.0
    vals = []
    for u in units:
        axes = u.impact_axes or {}
        vals.append(sum(clamp(axes.get(k, 0.0)) for k in [
            "scientific_leverage", "decision_leverage", "scope", "tractability_to_value"
        ]) / 4.0)
    raw = sum(vals) / len(vals)
    if artifact_richness < 0.45:
        raw = min(raw, 0.50)
    return clamp(raw)


def score_scope_honesty(problem: dict[str, Any], solution: dict[str, Any], claims: list[dict[str, Any]]) -> float:
    assumptions = problem.get("assumptions") or []
    constraints_text = present_text(solution.get("constraints", ""))
    falsifiers = [c.get("falsification_criteria", "") for c in claims]
    return clamp(
        0.35 * clamp(len(assumptions) / 3.0)
        + 0.35 * field_richness([constraints_text])
        + 0.30 * field_richness(falsifiers)
    )


def abstract_only_multiplier(artifact: dict[str, Any]) -> float:
    problem = artifact.get("problem") or {}
    observations = problem.get("observations") or []
    evidence_fields = [o.get("evidence", "") for o in observations]
    if evidence_fields and sum("abstract" in e.lower() for e in evidence_fields) / len(evidence_fields) >= 0.75:
        return 0.65
    claims = artifact.get("claims") or []
    claim_basis = " ".join(c.get("evidence_basis", "") for c in claims).lower()
    if claims and claim_basis.count("abstract") >= max(2, len(claims) // 2):
        return 0.75
    return 1.0


def score_m17(artifact: dict[str, Any], novelty_units: list[NoveltyUnit], source_year: int | None = None) -> dict[str, float]:
    problem = artifact.get("problem") or {}
    claims = artifact.get("claims") or []
    related = artifact.get("related_work") or []
    solution = artifact.get("solution") or {}

    availability, availability_parts = score_availability(artifact)
    gap_specificity = score_gap_specificity(problem)
    literature_positioning = score_lit_positioning(related)
    external_novelty = score_external_novelty(novelty_units, source_year)
    impact = score_impact(novelty_units, availability)
    scope_honesty = score_scope_honesty(problem, solution, claims)

    raw = (
        0.15 * availability
        + 0.15 * gap_specificity
        + 0.35 * external_novelty
        + 0.15 * literature_positioning
        + 0.15 * impact
        + 0.05 * scope_honesty
    )

    multiplier = abstract_only_multiplier(artifact)
    if not problem.get("key_insight", {}).get("insight"):
        raw = min(raw, 0.25)
    if not problem:
        raw = min(raw, 0.10)
    if literature_positioning < 0.25:
        multiplier *= 0.85

    final = clamp(raw * multiplier)
    return {
        "m17_novelty_vs_literature_impact": final,
        "availability_richness": availability,
        "gap_specificity": gap_specificity,
        "external_novelty": external_novelty,
        "literature_positioning": literature_positioning,
        "impact_if_solved": impact,
        "scope_honesty": scope_honesty,
        "thinness_multiplier": multiplier,
        **{f"availability_{k}": v for k, v in availability_parts.items()},
    }
```

The `artifact` dictionary above is the parsed representation of the documented ARA files. `novelty_units` are produced by Step 2 and filled with externally searched candidates and impact axes from Steps 3 to 5.

## Why this is hard to Goodhart

The metric checks novelty against multiple external paraphrases, not against the ARA's own wording. Hyper-specific gap phrasing is penalized when broader-family queries find prior art. Omitting close related work also hurts because external candidates absent from `related_work.md` create omission penalties.

It also separates novelty from impact. A tiny variation can be genuinely new but still low-impact; a high-impact domain can be crowded and therefore low-novelty. The final score requires both.

Finally, the metric composes well with the rest of the suite because it does not replace grounding, verifier, or internal-coherence metrics. It consumes their artifact fields but adds the external "done before?" and "would it matter?" layer. If another metric proves claims are well grounded, M17 asks whether those grounded claims are net-new and important. If another metric scores related-work coverage, M17 uses that coverage to judge novelty honestly rather than redundantly checking formatting.
