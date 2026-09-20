# M17 expansion: Novelty vs literature (+ impact)

## Metric intent

This metric asks whether the ARA has identified a real, literature-relative contribution rather than merely restating the source paper's own novelty language. It scores the novelty and impact of the problem layer's claims, insight, gaps, method/concept framing, and impact-if-solved against external literature.

The core signal is: if the Observations, Gaps, Key Insight, Claims, Concepts, Related Work, and Solution layer collectively describe a problem that was already solved or substantially done before, the score should be low even if the artifact is internally coherent. If they identify a specific unsolved gap, a nontrivial conceptual or methodological move, and plausible scientific or societal value if solved, the score should be high.

This metric is deliberately net-new relative to an internal verifier. A verifier can judge whether the ARA is well-formed, grounded, and internally scoped; it usually cannot decide whether the paper's claimed gap, method, insight, or concept was already present in the external literature. M17 therefore uses external search and semantic comparison as first-class inputs.

## What to reward

Reward:

- Specific novelty objects: clearly extractable candidate novelty units from `logic/problem.md`, especially each Gap statement, the Key Insight, and any method/conceptual leap implied by `Enables`.
- Literature-relative gap precision: the gap should name what prior attempts did, why they failed, and what remains unsolved, rather than saying only that prior work was "limited."
- Cross-layer consistency: novelty units from the problem layer should line up with falsifiable claims in `logic/claims.md`, specialized terms in `logic/concepts.md`, dependency deltas in `logic/related_work.md`, and method choices or boundary conditions in `logic/solution/`.
- Done-before resistance: external literature searches should not find substantially equivalent earlier work solving the same gap with the same key idea, method, or concept.
- Honest incrementalism: a narrow but real extension can score well if the ARA scopes it as an extension and explains why the incremental gain matters; it should not get credit for inflated "first ever" framing.
- Impact-if-solved: the gap should matter scientifically, clinically, technically, or socially. Impact is stronger when the artifact connects the gap to downstream claims, affected populations/systems, practical decisions, or a large dependency graph.
- Related-work breadth: `related_work.md` should expose the relevant prior literature footprint, including technical deltas and brief background references, so the novelty claim is tested against a meaningful neighborhood.

## What not to reward

Do not reward:

- Novelty language with no concrete object to compare externally.
- A Key Insight that is only the paper's method name, model name, dataset name, or result headline.
- A gap that is only "no one has studied X in this exact sample" unless the artifact explains why the sample/context changes the scientific conclusion.
- Differences in branding, notation, or implementation detail when an earlier paper already made the same conceptual or methodological move.
- Impact claims that are generic to the field but not specifically connected to the stated gap or claims.
- Related-work thinness disguised as novelty. Missing or abstract-only related work is a penalty, not a reason to assume novelty.

## Failure modes and gaming routes

Common failure modes:

- Overclaiming novelty by using vague units such as "novel framework" or "first comprehensive analysis" without defining what is new.
- Under-searching the literature neighborhood, especially by comparing only against citations already in the source paper.
- Treating absence of captured related work as evidence that prior work does not exist.
- Confusing internal scope novelty with external novelty: an ARA may correctly state what the paper does, while the external literature already contains the same idea.
- Rewarding fashionable or high-impact topics even when the paper's actual contribution is routine.
- Penalizing mature fields too harshly: a work in a crowded field can still be novel if it resolves a precise bottleneck or supplies decisive evidence.

Goodhart routes:

- Inflate the number of gaps or concepts to create the appearance of more novelty.
- Rewrite prior attempts as strawmen with generic failure modes.
- Omit close competitors from related work.
- Frame all prior work as "background" rather than `baseline`, `extends`, `bounds`, or `refutes` edges.
- Add broad societal-impact language that is not entailed by the artifact's claims or method.

The metric counters these by scoring per novelty unit, requiring external search for closest prior art, penalizing missing/thin inputs, and giving impact credit only when the impact chain is artifact-grounded.

## Assumptions

Assumption: the compute runner receives parsed markdown for `logic/problem.md`, `logic/claims.md`, `logic/concepts.md`, `logic/related_work.md`, and all files under `logic/solution/`. If a cross-layer artifact is unavailable to the runner, it is represented as missing and penalized; it is never skipped.

Assumption: external calls are available through Semantic Scholar search and an LLM semantic comparator. If external calls fail, the metric assigns conservative low confidence and applies explicit penalties rather than returning N/A.

## Generation / compute workflow

### Inputs

Primary:

- `problem_md`: full text of `logic/problem.md`
- Parsed problem fields: Observations `O*`, Gaps `G*`, `Key Insight` fields, Assumptions `A*`

Cross-layer:

- `claims_md`: full text of `logic/claims.md`
- Parsed claim blocks: `Statement`, `Status`, `Falsification criteria`, `Evidence basis`, `Interpretation`, `Dependencies`, `Sources`, `Tags`
- `concepts_md`: full text of `logic/concepts.md`
- Parsed concepts: term, `Definition`, `Boundary conditions`, `Related concepts`
- `related_work_md`: full text of `logic/related_work.md`
- Parsed RW blocks and brief references: DOI/arXiv, Type, Delta, Claims affected, Adopted elements
- `solution_files`: dictionary of `logic/solution/*.md`, always including `constraints.md` when present

### Step 1: Parse and grade input availability

Parse the expected markdown fields using heading and bold-field patterns from the documented shapes. Record field availability and thinness. Missing/thin inputs reduce the score. They never remove a case from the denominator.

Minimum availability checks:

- `problem_md` has at least one Observation, at least one Gap, one Key Insight, and at least one Assumption.
- each Gap has `Statement`, `Caused by`, `Existing attempts`, and `Why they fail`.
- Key Insight has `Insight`, `Derived from`, and `Enables`.
- `claims_md`, `concepts_md`, `related_work_md`, and `solution/constraints.md` are present or marked missing.
- related work includes at least one full `RW##` block and some representation of brief/background citation footprint unless the source context is demonstrably abstract-only.

Thinness penalties include: all Observation evidence is `Abstract`; generic "prior work is limited" language; Key Insight is only a method name; missing claim sources; concepts dominated by `Boundary conditions: Not specified in paper`; related work lacks brief references; constraints have no real limitations.

### Step 2: Generate novelty units

Create a list of novelty units from artifact text:

- one unit for each Gap: `kind="gap"`, `text=G.Statement + Existing attempts + Why they fail`
- one unit for Key Insight: `kind="insight"`, `text=Insight + Derived from + Enables`
- one method unit from `solution_files`: summarize the central method/design move and constraints
- up to five claim units from `claims_md`: use claims whose `Statement` and `Evidence basis` appear central, prioritizing claims referenced by gaps or related work
- up to five concept units from `concepts_md`: use concepts whose definitions are specific to the paper's contribution rather than generic field vocabulary

If a source section is missing, create a placeholder unit with `missing=True` and score it as zero evidence for that component. This implements penalize-don't-skip.

### Step 3: External literature retrieval

For each novelty unit, run three Semantic Scholar queries. Use the paper's field terms from concepts/tags when available; otherwise use terms from the unit text.

Query templates:

1. `"{{main_entities}} {{gap_or_insight_text_keywords}} {{method_keywords}}"`
2. `"{{existing_attempts_keywords}} {{why_they_fail_keywords}} {{domain_keywords}}"`
3. `"{{claim_or_concept_keywords}} {{baseline_or_comparator_keywords}}"`

For each query, retrieve top 10 papers with title, abstract, year, venue, DOI/arXiv, citation count, influential citation count, and Semantic Scholar paper ID. Merge duplicates. If a `related_work.md` DOI/arXiv appears in the retrieved set, preserve the link between retrieved paper and RW block.

External-call failure handling:

- If Semantic Scholar returns no results for a query, assign that query `retrieval_quality=0.4`, not 1.0.
- If Semantic Scholar is unavailable, use only artifact related work as the candidate set and apply an external-availability penalty of 0.25 to the final score.
- If abstracts are missing for retrieved papers, keep titles and metadata but mark comparator confidence lower.

### Step 4: Semantic done-before comparison

For each novelty unit and each retrieved prior paper, call an LLM comparator with this exact prompt:

```text
You are judging whether a proposed scientific novelty unit was already done in prior literature.

Novelty unit:
{unit_text}

Candidate prior paper:
Title: {title}
Year: {year}
Abstract: {abstract}
Related-work delta from artifact, if any: {rw_delta}

Return JSON only:
{
  "same_problem": 0.0-1.0,
  "same_gap": 0.0-1.0,
  "same_key_idea": 0.0-1.0,
  "same_method_or_concept": 0.0-1.0,
  "already_solved": 0.0-1.0,
  "incremental_extension": 0.0-1.0,
  "impact_relevance": 0.0-1.0,
  "rationale": "one short sentence"
}
```

Convert each candidate to a done-before score:

`candidate_done_before = max(already_solved, 0.35*same_gap + 0.35*same_key_idea + 0.20*same_method_or_concept + 0.10*same_problem)`

The unit's done-before risk is the maximum `candidate_done_before` across candidates, multiplied by comparator confidence. Comparator confidence is `1.0` when title and abstract are present, `0.75` when only title and related-work delta are present, and `0.5` when only title is present.

### Step 5: Score impact-if-solved

Compute impact from artifact-grounded signals plus external metadata:

- claim centrality: fraction of extracted claims whose statements/evidence basis depend on this gap or insight
- dependency centrality: number and diversity of related-work edges linked to affected claims or adopted elements
- constraint realism: whether solution constraints define the boundary where the impact applies
- external field weight: median citations/influential citations of nearest-neighbor literature, log-scaled
- societal/scientific specificity: LLM score from 0 to 1 using the prompt below

Impact prompt:

```text
Judge the impact-if-solved of this scientific gap using only the artifact-grounded text.

Gap/insight:
{unit_text}

Relevant claims:
{claim_summaries}

Relevant constraints:
{constraint_summaries}

Return JSON only:
{
  "scientific_impact": 0.0-1.0,
  "societal_or_clinical_impact": 0.0-1.0,
  "specificity": 0.0-1.0,
  "overclaim_risk": 0.0-1.0,
  "rationale": "one short sentence"
}
```

`impact = max(scientific_impact, societal_or_clinical_impact) * specificity * (1 - 0.5*overclaim_risk)`

### Step 6: Deterministic scoring function

```python
import math
import re
from statistics import mean, median

GENERIC_GAP_PATTERNS = [
    r"\bprior work (is|was|has been)?\s*(limited|scarce|insufficient)\b",
    r"\bnot well understood\b",
    r"\bmore research is needed\b",
    r"\bremains unclear\b",
]

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))

def has_generic_gap_text(text):
    t = text.lower()
    return any(re.search(p, t) for p in GENERIC_GAP_PATTERNS)

def log_weight(n):
    return clamp(math.log1p(max(0, n)) / math.log1p(500))

def availability_score(parsed):
    checks = [
        bool(parsed.get("observations")),
        bool(parsed.get("gaps")),
        bool(parsed.get("key_insight")),
        bool(parsed.get("assumptions")),
        bool(parsed.get("claims_present")),
        bool(parsed.get("concepts_present")),
        bool(parsed.get("related_work_present")),
        bool(parsed.get("constraints_present")),
    ]
    base = sum(checks) / len(checks)
    thin = 0.0
    thin += 0.10 if parsed.get("all_observation_evidence_abstract") else 0.0
    thin += 0.10 if parsed.get("key_insight_method_name_only") else 0.0
    thin += 0.10 if parsed.get("generic_gap_fraction", 0) > 0.5 else 0.0
    thin += 0.10 if parsed.get("missing_claim_sources_fraction", 0) > 0.25 else 0.0
    thin += 0.08 if parsed.get("concept_boundary_not_specified_fraction", 0) > 0.5 else 0.0
    thin += 0.10 if not parsed.get("related_work_has_brief_tier") else 0.0
    thin += 0.07 if parsed.get("constraints_thin") else 0.0
    return clamp(base - thin)

def unit_specificity(unit):
    text = unit.get("text", "")
    if unit.get("missing"):
        return 0.0
    score = 0.35
    score += 0.20 if len(text.split()) >= 35 else 0.0
    score += 0.15 if re.search(r"\b(O\d+|G\d+|C\d+|RW\d+|A\d+)\b", text) else 0.0
    score += 0.15 if re.search(r"\b(because|whereas|unlike|fails?|cannot|enables?)\b", text.lower()) else 0.0
    score += 0.15 if not has_generic_gap_text(text) else -0.15
    return clamp(score)

def unit_novelty_score(unit):
    if unit.get("missing"):
        return 0.0
    done_before_risk = clamp(unit.get("done_before_risk", 1.0))
    specificity = unit_specificity(unit)
    retrieval_quality = clamp(unit.get("retrieval_quality", 0.5))
    cross_layer_support = clamp(unit.get("cross_layer_support", 0.0))
    novelty = (1.0 - done_before_risk)
    return clamp(0.45 * novelty + 0.20 * specificity + 0.20 * cross_layer_support + 0.15 * retrieval_quality)

def impact_score(unit):
    if unit.get("missing"):
        return 0.0
    llm_impact = clamp(unit.get("llm_impact", 0.0))
    claim_centrality = clamp(unit.get("claim_centrality", 0.0))
    dependency_centrality = clamp(unit.get("dependency_centrality", 0.0))
    constraint_realism = clamp(unit.get("constraint_realism", 0.0))
    citation_weight = log_weight(unit.get("median_neighbor_citations", 0))
    return clamp(
        0.35 * llm_impact
        + 0.20 * claim_centrality
        + 0.15 * dependency_centrality
        + 0.15 * constraint_realism
        + 0.15 * citation_weight
    )

def metric_m17(parsed, units, external_available=True):
    avail = availability_score(parsed)
    if not units:
        units = [{"missing": True, "text": ""}]

    novelty_scores = [unit_novelty_score(u) for u in units]
    impact_scores = [impact_score(u) for u in units]
    specificity_scores = [unit_specificity(u) for u in units]

    novelty = mean(novelty_scores)
    impact = mean(impact_scores)
    specificity = mean(specificity_scores)

    # Penalize any high-risk done-before match heavily: one fatal prior-art hit matters.
    max_done_before = max(clamp(u.get("done_before_risk", 1.0 if u.get("missing") else 0.0)) for u in units)
    fatal_prior_art_penalty = 0.35 * max_done_before

    external_penalty = 0.0 if external_available else 0.25

    raw = (
        0.35 * novelty
        + 0.25 * impact
        + 0.20 * specificity
        + 0.20 * avail
        - fatal_prior_art_penalty
        - external_penalty
    )
    return clamp(raw)
```

### Step 7: Reporting fields

The metric should emit:

- `score`: final 0-1 score
- `availability_score`
- `novelty_score`
- `impact_score`
- `specificity_score`
- `max_done_before_risk`
- `top_prior_art_matches`: up to five papers with DOI/arXiv, title, year, and done-before rationale
- `penalties`: missing/thin fields and external-call failures
- `unit_scores`: per novelty unit score with linked gaps/claims/concepts/RW/method evidence

## Why this is hard to Goodhart

It is hard to Goodhart because the score is not based on how emphatically the artifact claims novelty. It compares extracted novelty units against external literature and treats the closest prior-art match as a possible fatal penalty. Padding more gaps or concepts can backfire because weak or generic units remain in the denominator. Omitting related work also backfires because related-work absence lowers availability and retrieval quality instead of being interpreted as novelty.

The impact portion is similarly constrained: broad social value gets discounted unless it is connected to claims, constraints, dependency edges, and a specific gap. This makes generic "important problem" language insufficient.

## Composition with the suite

M17 complements internal-grounding and verifier-like metrics by asking a different question: not "is the artifact faithful and internally complete?" but "does this artifact identify a contribution that survives contact with the external literature?" It composes well with claim grounding, related-work coverage, concept quality, method validity, and constraint realism. Those metrics make the extracted units trustworthy; M17 then uses them to judge novelty and impact. When those inputs are missing or thin, M17 scores down directly, preserving the penalize-don't-skip principle.
