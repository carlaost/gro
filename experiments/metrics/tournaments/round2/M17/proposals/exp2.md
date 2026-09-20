# M17 Expansion: Novelty vs Literature (+ Impact)

## Metric Definition

M17 scores whether the ARA's problem framing, claims, concepts, and method describe a genuinely new scientific contribution relative to external literature, while also weighting how much scientific or societal value the contribution would have if solved. It is not a generic "paper importance" score and it is not a verifier for internal consistency. The core question is: after reconstructing the paper's asserted observations, gaps, key insight, claims, technical concepts, related-work graph, and method, does the ARA identify something that was not already done in the literature, and is the unresolved problem worth solving?

The metric uses `logic/problem.md` as the primary artifact and cross-checks `logic/claims.md`, `logic/concepts.md`, `logic/related_work.md`, and `logic/solution/` only to scope the novelty target and avoid rewarding vague problem statements. Missing, thin, malformed, or uncomputable inputs are penalized inside the score. No case is skipped or marked N/A.

## What It Rewards

This metric rewards ARAs that make a precise, source-bounded novelty case:

- Observations identify what was empirically known before the work, with concrete facts and citations rather than generic background.
- Gaps name a specific missing capability, unresolved contradiction, untested regime, methodological limitation, or conceptual ambiguity.
- Existing attempts and why-they-fail fields distinguish the paper's target from close prior work.
- The Key Insight states the creative leap that closes the gap, not merely the paper's method name.
- Claims, concepts, and method files give enough specificity to search for "done before" at the right granularity.
- Related work captures close predecessors, baselines, imported datasets, bounds, extensions, and refutations, so the external novelty check is not starting from an artificially small literature footprint.
- Impact-if-solved is argued from the scale, centrality, clinical/social relevance, or field-enabling value of the problem, not from hype words.

High scores should go to artifacts where external search finds adjacent or enabling work but not a prior paper that already made the same claim, resolved the same gap, introduced the same key insight, or used the same method for the same purpose. A replication or confirmatory study can still score well only when the ARA makes a credible novelty case around population, scale, regime, independent validation, contradiction resolution, or practical deployment relevance.

## What It Must Not Reward

The metric must not reward:

- Empty novelty phrasing such as "little is known", "first study", or "novel approach" without a specific comparator.
- A gap that exists only because `related_work.md` failed to capture close prior work.
- Method novelty when the method is standard and the actual novelty is only an application domain, dataset, endpoint, or synthesis.
- Broad social importance without a new scientific contribution.
- Incremental parameter, cohort, or benchmark changes described as conceptual novelty unless the ARA explains why the change creates a materially new scientific test.
- Overclaiming that ignores known failed attempts, negative trials, replication failures, or already solved variants.
- Missing or thin artifacts. If an input is absent, malformed, abstract-only, or too generic for a fair search, the score goes down rather than excluding that artifact from evaluation.

## Inputs

Primary input:

- `logic/problem.md`: Observations, Gaps, Key Insight, and Assumptions.

Cross-layer inputs:

- `logic/claims.md`: claim statements, statuses, falsification criteria, evidence bases, dependencies, sources, and tags.
- `logic/concepts.md`: technical terms, notation, definitions, boundary conditions, and related concepts.
- `logic/related_work.md`: full `RW##` dependency blocks and brief citation-footprint references.
- `logic/solution/constraints.md` and any warranted method files under `logic/solution/`: boundary conditions, assumptions, limitations, and method details.

Availability is itself a score component. Mandatory artifacts that are missing, unreadable, malformed, or content-thin receive penalties in the corresponding sub-scores and in the final coverage multiplier.

## Generation / Compute Workflow

### 1. Parse Artifacts

Parse `logic/problem.md` into:

- `observations`: each `O#` title plus `Statement`, `Evidence`, and `Implication`.
- `gaps`: each `G#` title plus `Statement`, `Caused by`, `Existing attempts`, and `Why they fail`.
- `key_insight`: `Insight`, `Derived from`, and `Enables`.
- `assumptions`: all `A#` entries.

Parse cross-layer artifacts into:

- `claims`: each `C##` statement, status, falsification criteria, evidence basis, interpretation, dependencies, sources, and tags.
- `concepts`: term name, notation, definition, boundary conditions, and related concepts.
- `related_work`: every full `RW##` block with DOI/arXiv, type, delta, claims affected, and adopted elements, plus brief-tier references.
- `solution`: constraints, assumptions, known limitations, data-quality caveats, and method-file headings/content.

If a file or required field is missing, insert an explicit placeholder record with `available=False` and a defect reason. Do not drop the item from later scoring.

### 2. Build Novelty Targets

Construct search targets at four granularities:

- Claim targets: one target per supported or hypothesis claim, using `Statement`, `Evidence basis`, `Tags`, and `Falsification criteria`.
- Gap targets: one target per gap, using `Statement`, `Existing attempts`, `Why they fail`, and linked observations from `Caused by`.
- Insight target: one target from `Key Insight`, `Derived from`, `Enables`, and the most relevant method details from `solution/`.
- Concept/method targets: one target per distinctive concept or method element that appears in claims, gaps, or key insight.

For each target, produce a normalized target summary with:

```json
{
  "target_id": "G1",
  "type": "gap",
  "problem": "...",
  "intervention_or_method": "...",
  "population_or_domain": "...",
  "outcome_or_claim": "...",
  "claimed_delta": "...",
  "boundary_conditions": "...",
  "query_terms": ["..."]
}
```

If a target cannot be normalized because its source text is too vague, keep it with `normalization_quality=0` and score it as weak rather than skipping it.

### 3. External Literature Retrieval

Use external literature search for each target. Required calls:

- Semantic Scholar query for close prior work:
  - Query template: `"${problem} ${intervention_or_method} ${outcome_or_claim} ${population_or_domain}"`.
  - Retrieve top 20 by relevance and top 10 by recency.
  - For each result, store title, abstract, year, DOI/arXiv, venue, citation count when available, and URL.
- Semantic Scholar query for exact key phrases:
  - Query template: quoted distinctive phrases from `claimed_delta`, technical concept names, and method names.
  - Retrieve top 10.
- If the target is clinical, interventional, epidemiological, or trial-like, query clinical-trial registries for the intervention/method, population, and outcome. If the call fails or the genre classifier is uncertain, set `trial_lookup_status="failed_or_uncertain"` and apply the precondition penalty.
- If the target includes formal methods, algorithms, architectures, or mathematical concepts, query arXiv/Semantic Scholar with the formal notation and concept names. Failure to query is penalized.

The deterministic LLM prompt used to classify retrieved items is:

```text
You are judging whether a prior work already did the same scientific contribution as an ARA target.
Target:
{target_summary_json}

Candidate prior work:
Title: {title}
Year: {year}
Abstract: {abstract}
Known relation from ARA related_work, if any: {rw_relation_or_none}

Classify candidate_overlap as one of:
- already_done: same problem/domain, same key claim or gap resolution, and substantially same method or insight
- close_predecessor: same problem and adjacent method/claim, but the ARA target has a material new delta
- enabling_background: supplies data, tool, theory, or motivation but does not solve the target
- unrelated: not materially relevant

Return JSON only:
{
  "candidate_overlap": "...",
  "reason": "one sentence",
  "matched_dimensions": ["problem", "method", "claim", "population", "outcome", "concept"],
  "missing_dimensions": ["..."],
  "confidence": 0.0
}
```

Use temperature 0. Classifier failures receive `candidate_overlap="unknown"` and `confidence=0`; unknown candidates are penalized as partial close-predecessor risk, not ignored.

### 4. Score Target Novelty

For each target, compute:

- `specificity`: 1.0 if problem, method/insight, domain/population, outcome/claim, and boundary are all concrete; 0.6 if one or two are vague; 0.3 if mostly generic; 0.0 if unparseable.
- `literature_coverage`: min(1.0, retrieved_relevant_candidates / 10), capped by 0.6 if no exact-phrase query succeeded and capped by 0.5 if the ARA has no useful related-work comparators.
- `done_before_penalty`: maximum overlap penalty among candidates:
  - `already_done`: 1.0
  - `close_predecessor`: 0.45 * confidence
  - `unknown`: 0.25
  - `enabling_background` or `unrelated`: 0.0
- `delta_quality`: 1.0 if the ARA clearly explains the material difference from close predecessors; 0.7 if the difference is concrete but under-argued; 0.4 if only implied; 0.0 if absent.

Per-target novelty:

```python
target_novelty = max(
    0.0,
    specificity * literature_coverage * delta_quality * (1.0 - done_before_penalty)
)
```

Targets with missing fields remain in the denominator. Their low specificity and coverage naturally reduce the score.

### 5. Score Impact-if-Solved

Compute an impact score from the parsed artifact plus external signals:

- `problem_scale`: disease burden, affected population, cost, field bottleneck centrality, or breadth of downstream use.
- `scientific_leverage`: whether solving the gap unlocks new measurement, causal discrimination, unification of inconsistent findings, reproducibility, or method reuse.
- `practical_actionability`: whether the result changes clinical, policy, engineering, experimental, or theoretical decisions.
- `evidence_grounding`: whether impact claims are supported by observations, related work, constraints, and claims rather than unsupported rhetoric.

Use this LLM prompt for impact classification:

```text
Score the impact-if-solved of this scientific gap using only the provided ARA fields and retrieved literature metadata.
ARA problem/gap/insight:
{problem_gap_insight_text}
Claims:
{claim_summaries}
Related work context:
{related_work_summaries}
External metadata:
{retrieved_metadata_summary}

Return JSON only with numeric values in [0,1]:
{
  "problem_scale": ...,
  "scientific_leverage": ...,
  "practical_actionability": ...,
  "evidence_grounding": ...,
  "reason": "one sentence"
}
```

Impact score:

```python
impact = (
    0.30 * problem_scale +
    0.30 * scientific_leverage +
    0.20 * practical_actionability +
    0.20 * evidence_grounding
)
```

If impact cannot be computed because the artifact is thin, set missing dimensions to 0 rather than excluding them.

### 6. Penalize Input Thinness and Precondition Failures

Compute `availability_quality`:

```python
availability_quality = (
    0.35 * problem_quality +
    0.20 * claims_quality +
    0.15 * concepts_quality +
    0.20 * related_work_quality +
    0.10 * solution_quality
)
```

Where each component is in `[0,1]`:

- `problem_quality`: required sections present; observations cite evidence; gaps have specific existing attempts and failure modes; key insight is not just a method name.
- `claims_quality`: claims have falsifiable statements, sources with quotes, evidence bases, and tags.
- `concepts_quality`: concepts are genuine technical terms with definitions and boundary conditions; generic glossary padding is penalized.
- `related_work_quality`: full typed dependency blocks and a brief citation-footprint tier are present; close predecessors are not omitted.
- `solution_quality`: constraints are substantive; method files match the paper genre; limitations and relevant caveats are captured.

Apply precondition penalties:

```python
precondition_penalty = 0.0
if external_search_failed:
    precondition_penalty += 0.20
if clinical_target and trial_lookup_failed:
    precondition_penalty += 0.10
if more_than_half_targets_unparseable:
    precondition_penalty += 0.25
if related_work_missing_or_too_thin:
    precondition_penalty += 0.20
precondition_multiplier = max(0.0, 1.0 - precondition_penalty)
```

These penalties implement penalize-don't-skip: unavailable artifact fields, failed retrieval, unknown candidate classification, malformed targets, and missing related-work context all lower the metric value.

### 7. Final Scoring Function

Reference Python:

```python
from statistics import mean

def clamp01(x):
    return max(0.0, min(1.0, float(x)))

def m17_score(targets, impact_dims, quality_dims, flags):
    # targets are never filtered out; malformed targets should have low component values
    if not targets:
        target_scores = [0.0]
    else:
        target_scores = []
        for t in targets:
            specificity = clamp01(t.get("specificity", 0.0))
            coverage = clamp01(t.get("literature_coverage", 0.0))
            delta = clamp01(t.get("delta_quality", 0.0))
            done_before_penalty = clamp01(t.get("done_before_penalty", 0.25))
            target_scores.append(max(0.0, specificity * coverage * delta * (1.0 - done_before_penalty)))

    novelty = mean(target_scores)

    impact = (
        0.30 * clamp01(impact_dims.get("problem_scale", 0.0)) +
        0.30 * clamp01(impact_dims.get("scientific_leverage", 0.0)) +
        0.20 * clamp01(impact_dims.get("practical_actionability", 0.0)) +
        0.20 * clamp01(impact_dims.get("evidence_grounding", 0.0))
    )

    availability_quality = (
        0.35 * clamp01(quality_dims.get("problem_quality", 0.0)) +
        0.20 * clamp01(quality_dims.get("claims_quality", 0.0)) +
        0.15 * clamp01(quality_dims.get("concepts_quality", 0.0)) +
        0.20 * clamp01(quality_dims.get("related_work_quality", 0.0)) +
        0.10 * clamp01(quality_dims.get("solution_quality", 0.0))
    )

    precondition_penalty = 0.0
    if flags.get("external_search_failed", False):
        precondition_penalty += 0.20
    if flags.get("clinical_target", False) and flags.get("trial_lookup_failed", False):
        precondition_penalty += 0.10
    if flags.get("more_than_half_targets_unparseable", False):
        precondition_penalty += 0.25
    if flags.get("related_work_missing_or_too_thin", False):
        precondition_penalty += 0.20

    precondition_multiplier = max(0.0, 1.0 - precondition_penalty)

    raw = 0.65 * novelty + 0.35 * impact
    return clamp01(raw * availability_quality * precondition_multiplier)
```

Suggested interpretation:

- `0.85-1.00`: precise, externally checked novelty with high impact and strong artifact coverage.
- `0.65-0.84`: likely novel and useful, with some uncertainty or weaker scoping.
- `0.40-0.64`: partially novel, incremental, or under-supported by artifact/literature coverage.
- `0.15-0.39`: mostly done before, vague, low impact, or seriously under-scoped.
- `0.00-0.14`: unparseable, unsupported, missing, or contradicted by prior literature.

## Failure Modes and Gaming Routes

The main gaming route is hiding close predecessors by writing a narrow problem statement or a thin related-work graph. M17 counters this by querying claims, gaps, concepts, and method details independently; an omitted predecessor can still appear through claim or method search and reduce the score.

A second route is novelty inflation: using new labels for old ideas. The workflow compares problem, method, claim, population/domain, outcome, and concept dimensions separately, so terminological novelty alone cannot produce a high score.

A third route is impact inflation: attaching a common high-burden disease or broad societal phrase to a low-leverage technical delta. The impact sub-score requires field leverage, actionability, and grounding in observations or literature, so scale alone is insufficient.

A fourth route is strategic vagueness. Vague gaps and insights lower target specificity and normalization quality, and because they remain in the denominator, they reduce the final score.

## Why It Is Hard to Goodhart

M17 is hard to Goodhart because it triangulates novelty from multiple ARA layers and external literature rather than trusting a single self-description. A compiler cannot simply add the word "novel"; it must provide concrete gaps, prior attempts, failure modes, claims, concepts, and method boundaries that survive external search. The score also distinguishes close predecessor, enabling background, and already-done cases, which prevents both excessive punishment for legitimate dependencies and excessive reward for rediscovered work.

The penalize-don't-skip rule further reduces gaming. Missing sources, failed searches, malformed fields, abstract-only thinness, absent brief citation footprints, and unknown classifications all lower the score. This makes it costly to avoid hard comparisons.

## Composition with the Suite

This metric is net-new relative to an internal verifier because it asks whether the paper's contribution was already present in the external literature and whether solving it matters. Internal verifiers can judge whether claims are grounded, sections are present, and dependencies are coherent; M17 judges external priority and value.

It composes well with grounding, claim-quality, related-work-completeness, method-validity, and constraint metrics. Those metrics answer whether the ARA faithfully represents the source. M17 uses that representation to answer a different question: whether the represented contribution is meaningfully new and worth attention. When the other metrics are low, M17 should usually fall through the availability multiplier rather than pretending novelty can be assessed independently of artifact quality.

## Assumptions

This expansion assumes external retrieval can access at least Semantic Scholar-style title/abstract metadata and, where relevant, clinical-trial registry metadata. If only partial external access is available, the workflow still runs, but retrieval failure is scored as uncertainty and penalized rather than skipped.

It also assumes all candidate targets from the artifact are evaluated, including weak or malformed ones. This is intentional: an ARA that cannot state what is new at claim, gap, insight, or method level should receive a lower novelty score.
