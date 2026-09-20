# M17 Expansion: Novelty vs Literature (+ Impact) — Cycle 2 (Improved)

## Changes (cycle 2)

This revision fixes the three weaknesses named in `critique_c1.md` for exp2 (Rank 2 winner),
without touching the parts the critique explicitly said to preserve (dimension-separated
overlap classification, multiplicative per-target gating, penalize-don't-skip preconditions).

1. **`literature_coverage` is no longer multiplied into novelty.** The old formula
   (`specificity * literature_coverage * delta_quality * (1 - done_before_penalty)`) meant a
   genuinely novel gap in a sparse literature collapsed toward zero purely because retrieval
   returned few candidates — conflating "we couldn't find a comparator set" with "not novel."
   Coverage is now split into a `retrieval_confidence` term (§4) that *discounts the verdict
   toward a skeptical neutral prior* rather than multiplying it toward zero. This keeps the
   penalize-don't-skip property (sparse/failed retrieval still lowers the score below what a
   confirmed clean search would earn) while no longer being able to crash a well-specified,
   well-differentiated target to ~0 just because comparators were thin. See §4 and §5 for the
   exact mechanism and worked regimes.
2. **A second, differently-biased retrieval family is now required.** The original design
   queried only the Semantic Scholar lexical/citation-graph family, so the whole relabeling
   defense rested on a single LLM classifier reading lexically-retrieved abstracts — an author
   who fully replaces vocabulary (same mechanism, new words) could reduce the odds any lexical
   query surfaces the true predecessor. §3 now adds a mandatory embedding/semantic-recall pass
   (arXiv + PubMed/bioRxiv abstract embeddings, cosine top-K) run independently of exact phrase
   matching. `done_before_penalty` is the max over the *union* of both families' candidates (a
   strong match from either family still fully penalizes — this is a strict widening, not a
   requirement of corroboration to trigger a penalty), and retrieval_confidence is capped unless
   both families actually executed. This closes the "rename the mechanism" gap the critique
   flagged and brings the design's relabeling defense to parity with exp1's dual-index approach.
3. **Impact no longer silently reuses the novelty retrieval bundle.** The critique noted impact
   and novelty leaned on the same retrieved-metadata bundle, risking double-counting: retrieval
   noise that inflates or deflates a target's `literature_coverage` could also move
   `evidence_grounding` and `problem_scale` in the same direction for the same reason, making the
   two halves of the final score correlated through a shared error term rather than independent
   checks. §6 now draws impact's external signals from a *separate, gap-level* query
   (field-activity counts: citing-paper count and active-trial count for the gap's domain as a
   whole) rather than from the per-target overlap-classification candidates, and
   `evidence_grounding` is computed only from ARA-internal fields (whether the impact claim is
   backed by an Observation, a Gap's `Caused by` chain, or a related-work dependency block), never
   from the novelty classifier's output. This makes novelty and impact fail independently rather
   than sharing a noise source.

Everything else — the four-granularity target construction, the dimension-separated overlap
classifier, the multiplicative per-target novelty gate, the availability/precondition multipliers,
and the failure-mode analysis — is retained from `proposals/exp2.md` because the critique ranked
those as the design's strongest, correctly-net-new elements.

## Metric Definition

M17 scores whether the ARA's problem framing, claims, concepts, and method describe a genuinely
new scientific contribution relative to external literature, while also weighting how much
scientific or societal value the contribution would have if solved. It is not a generic "paper
importance" score and it is not a verifier for internal consistency. The core question is: after
reconstructing the paper's asserted observations, gaps, key insight, claims, technical concepts,
related-work graph, and method, does the ARA identify something that was not already done in the
literature, and is the unresolved problem worth solving?

The metric uses `logic/problem.md` as the primary artifact and cross-checks `logic/claims.md`,
`logic/concepts.md`, `logic/related_work.md`, and `logic/solution/` only to scope the novelty
target and avoid rewarding vague problem statements. Missing, thin, malformed, or uncomputable
inputs are penalized inside the score. No case is skipped or marked N/A.

## What It Rewards

- Observations identify what was empirically known before the work, with concrete facts and
  citations rather than generic background.
- Gaps name a specific missing capability, unresolved contradiction, untested regime,
  methodological limitation, or conceptual ambiguity.
- Existing attempts and why-they-fail fields distinguish the paper's target from close prior work.
- The Key Insight states the creative leap that closes the gap, not merely the paper's method name.
- Claims, concepts, and method files give enough specificity to search for "done before" at the
  right granularity.
- Related work captures close predecessors, baselines, imported datasets, bounds, extensions, and
  refutations, so the external novelty check is not starting from an artificially small literature
  footprint.
- Impact-if-solved is argued from the scale, centrality, clinical/social relevance, or
  field-enabling value of the problem, not from hype words.

High scores should go to artifacts where external search finds adjacent or enabling work but not a
prior paper that already made the same claim, resolved the same gap, introduced the same key
insight, or used the same method for the same purpose. A replication or confirmatory study can
still score well only when the ARA makes a credible novelty case around population, scale, regime,
independent validation, contradiction resolution, or practical deployment relevance.

A target sitting in a genuinely sparse literature (both retrieval families run cleanly and turn up
few or no relevant candidates) is *not* automatically rewarded as novel — see §4/§5. Sparse
retrieval earns cautious, capped credit, not full credit, because "nobody has published on this"
is evidence of low confidence, not proof of novelty.

## What It Must Not Reward

- Empty novelty phrasing such as "little is known", "first study", or "novel approach" without a
  specific comparator.
- A gap that exists only because `related_work.md` failed to capture close prior work.
- Method novelty when the method is standard and the actual novelty is only an application domain,
  dataset, endpoint, or synthesis.
- Broad social importance without a new scientific contribution.
- Incremental parameter, cohort, or benchmark changes described as conceptual novelty unless the
  ARA explains why the change creates a materially new scientific test.
- Overclaiming that ignores known failed attempts, negative trials, replication failures, or
  already solved variants.
- Missing or thin artifacts. If an input is absent, malformed, abstract-only, or too generic for a
  fair search, the score goes down rather than excluding that artifact from evaluation.
- Picking an obscure or under-published niche as a way to guarantee empty retrieval. This is
  addressed directly by the retrieval-confidence mechanism in §4/§5: empty-but-well-executed
  retrieval is scored as *unconfirmed*, capped below the "likely novel" band, not rewarded.

## Inputs

Primary input:

- `logic/problem.md`: Observations, Gaps, Key Insight, and Assumptions.

Cross-layer inputs:

- `logic/claims.md`: claim statements, statuses, falsification criteria, evidence bases,
  dependencies, sources, and tags.
- `logic/concepts.md`: technical terms, notation, definitions, boundary conditions, and related
  concepts.
- `logic/related_work.md`: full `RW##` dependency blocks and brief citation-footprint references.
- `logic/solution/constraints.md` and any warranted method files under `logic/solution/`: boundary
  conditions, assumptions, limitations, and method details.

Availability is itself a score component. Mandatory artifacts that are missing, unreadable,
malformed, or content-thin receive penalties in the corresponding sub-scores and in the final
coverage multiplier.

## Generation / Compute Workflow

### 1. Parse Artifacts

Parse `logic/problem.md` into:

- `observations`: each `O#` title plus `Statement`, `Evidence`, and `Implication`.
- `gaps`: each `G#` title plus `Statement`, `Caused by`, `Existing attempts`, and `Why they fail`.
- `key_insight`: `Insight`, `Derived from`, and `Enables`.
- `assumptions`: all `A#` entries.

Parse cross-layer artifacts into:

- `claims`: each `C##` statement, status, falsification criteria, evidence basis, interpretation,
  dependencies, sources, and tags.
- `concepts`: term name, notation, definition, boundary conditions, and related concepts.
- `related_work`: every full `RW##` block with DOI/arXiv, type, delta, claims affected, and
  adopted elements, plus brief-tier references.
- `solution`: constraints, assumptions, known limitations, data-quality caveats, and method-file
  headings/content.

If a file or required field is missing, insert an explicit placeholder record with
`available=False` and a defect reason. Do not drop the item from later scoring.

### 2. Build Novelty Targets

Construct search targets at four granularities:

- Claim targets: one target per supported or hypothesis claim, using `Statement`,
  `Evidence basis`, `Tags`, and `Falsification criteria`.
- Gap targets: one target per gap, using `Statement`, `Existing attempts`, `Why they fail`, and
  linked observations from `Caused by`.
- Insight target: one target from `Key Insight`, `Derived from`, `Enables`, and the most relevant
  method details from `solution/`.
- Concept/method targets: one target per distinctive concept or method element that appears in
  claims, gaps, or key insight.

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

If a target cannot be normalized because its source text is too vague, keep it with
`normalization_quality=0` and score it as weak rather than skipping it.

### 3. External Literature Retrieval (dual, differently-biased families)

Two independent retrieval families are mandatory per target. Each is queried, scored, and
classified separately; results are merged only at the `done_before_penalty` step (§4). This dual
structure is the design's primary defense against relabeling: an author controls their own prose,
but not two independently-biased external indexes.

**Family L — lexical / citation-graph (Semantic Scholar):**

- Relevance query: `"${problem} ${intervention_or_method} ${outcome_or_claim} ${population_or_domain}"`.
  Retrieve top 20 by relevance and top 10 by recency.
- Exact-phrase query: quoted distinctive phrases from `claimed_delta`, technical concept names,
  and method names. Retrieve top 10.
- For each result, store title, abstract, year, DOI/arXiv, venue, citation count when available,
  and URL.
- If this family's calls fail outright, set `family_L_status="failed"` and apply the
  `external_search_failed` precondition penalty (§7).

**Family S — semantic / embedding recall (arXiv + PubMed/bioRxiv abstract embeddings):**

- Embed the target's `problem` + `intervention_or_method` + `outcome_or_claim` text and run
  cosine-similarity top-K (K=15) retrieval over an arXiv/PubMed/bioRxiv abstract embedding index,
  independent of exact wording. This is the family that catches paraphrase and terminology
  substitution: same mechanism, different vocabulary, no shared quoted phrase.
  - Retain candidates above cosine similarity 0.55; discard the rest, but record
    `family_S_candidate_count_above_threshold` regardless of downstream relevance filtering.
- If this family's calls fail outright, set `family_S_status="failed"` and apply the
  `external_search_failed` precondition penalty (§7) — the same flag as Family L, since either
  family failing is a retrieval precondition failure.
- If `family_S_status` cannot be executed because no embedding index is configured for the
  artifact's domain (e.g. a non-arXiv/PubMed/bioRxiv genre with no available embedding corpus),
  record `family_S_status="unavailable"`, which is scored identically to `"failed"` for the
  precondition penalty — unavailability of the second index is a retrieval limitation to be
  penalized, not grounds to silently fall back to single-family evidence.

**Genre-conditional calls (either family may trigger these):**

- If the target is clinical, interventional, epidemiological, or trial-like, query clinical-trial
  registries for the intervention/method, population, and outcome. If the call fails or the genre
  classifier is uncertain, set `trial_lookup_status="failed_or_uncertain"` and apply the
  precondition penalty.
- If the target includes formal methods, algorithms, architectures, or mathematical concepts,
  query arXiv/Semantic Scholar with the formal notation and concept names. Failure to query is
  penalized.

**Classification (run once per family, per candidate):**

The deterministic LLM prompt used to classify retrieved items, applied identically to Family L and
Family S candidates (the prompt is family-agnostic; only the candidate pool differs):

```text
You are judging whether a prior work already did the same scientific contribution as an ARA target.
Target:
{target_summary_json}

Candidate prior work:
Title: {title}
Year: {year}
Abstract: {abstract}
Retrieval family: {"lexical" | "semantic"}
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

Use temperature 0. Classifier failures receive `candidate_overlap="unknown"` and
`confidence=0`; unknown candidates are penalized as partial close-predecessor risk, not ignored.

### 4. Score Target Novelty

For each target, compute, per family, then merge:

- `specificity`: 1.0 if problem, method/insight, domain/population, outcome/claim, and boundary
  are all concrete; 0.6 if one or two are vague; 0.3 if mostly generic; 0.0 if unparseable.
  (Family-independent — computed once from the target itself.)
- `done_before_penalty`: maximum overlap penalty among **all candidates from both families
  combined** (a strong match found by either the lexical or the semantic family still fully
  applies — the union, not the intersection, of the two families' findings is what counts against
  the target):
  - `already_done`: 1.0
  - `close_predecessor`: 0.45 * confidence
  - `unknown`: 0.25
  - `enabling_background` or `unrelated`: 0.0
- `delta_quality`: 1.0 if the ARA clearly explains the material difference from close
  predecessors; 0.7 if the difference is concrete but under-argued; 0.4 if only implied; 0.0 if
  absent.
- `retrieval_confidence` (replaces the old `literature_coverage` multiplier — see §5 for why this
  is a discount toward a neutral prior rather than a multiplier toward zero):

  ```python
  def retrieval_confidence(family_L_status, family_S_status,
                            relevant_candidates_L, relevant_candidates_S,
                            exact_phrase_query_succeeded,
                            related_work_missing_or_too_thin):
      if family_L_status == "failed" or family_S_status in ("failed", "unavailable"):
          return 0.0  # a required family did not run; precondition_penalty (§7) also fires
      if related_work_missing_or_too_thin:
          return 0.3  # can't scope the target fairly regardless of what retrieval found
      total_relevant = relevant_candidates_L + relevant_candidates_S
      if total_relevant >= 3 and exact_phrase_query_succeeded:
          return 1.0   # confirmed: enough comparators seen, exact-phrase query ran clean
      if total_relevant >= 1:
          return 0.7   # some comparators seen, partial confirmation
      # both families executed cleanly and found nothing relevant: genuinely uncertain,
      # not proof of novelty and not proof of non-novelty
      return 0.5
  ```

Per-target novelty:

```python
raw_novelty = specificity * delta_quality * (1.0 - done_before_penalty)
NEUTRAL_PRIOR = 0.35  # deliberately below the "likely novel" band (0.65+); see §5
target_novelty = max(
    0.0,
    retrieval_confidence * raw_novelty + (1.0 - retrieval_confidence) * NEUTRAL_PRIOR
)
```

Targets with missing fields remain in the denominator. Their low specificity, delta_quality, and
retrieval_confidence naturally reduce the score; they are never dropped.

### 5. Why the Confidence Blend Replaces the Coverage Multiplier

The prior design (`exp2.md`, flagged in `critique_c1.md`) multiplied `literature_coverage` (a
retrieved-candidate count, capped at 1.0) directly into `target_novelty`. That made "few relevant
candidates retrieved" mathematically indistinguishable from "not novel" — a target with perfect
specificity, a strong argued delta, and zero found overlap in a genuinely sparse sub-field would
still score near zero, because coverage alone throttled the whole product toward zero.

The fix is to treat retrieval outcome as a *confidence* signal on the verdict, not as a factor of
the verdict itself, and to blend toward a fixed skeptical prior (`NEUTRAL_PRIOR = 0.35`) rather
than toward either extreme:

| Regime | retrieval_confidence | Effect |
|---|---|---|
| Family failed/unavailable | 0.0 | `target_novelty = 0.35` flat, regardless of computed `raw_novelty` — retrieval could not be trusted at all, so the target is scored at the skeptical floor, and `precondition_penalty` (§7) also fires on top of this. |
| Related work too thin to scope fairly | 0.3 | Mostly the neutral prior (0.35), slightly influenced by `raw_novelty` — can't fairly credit or discredit. |
| Both families ran clean, found nothing relevant | 0.5 | Half-and-half blend of `raw_novelty` and 0.35 — "no evidence of overlap" is treated as weak, capped support for novelty, not proof of it. A perfectly specific, well-argued target in a sparse literature now lands around `0.5*raw_novelty + 0.175`, materially above the old design's near-zero, but still below the "confirmed novel" ceiling. |
| Some relevant candidates found | 0.7 | Verdict is mostly trusted; small pull toward the prior. |
| Comparator set is substantial and both queries succeeded | 1.0 | `target_novelty = raw_novelty` exactly — full trust, no discount. |

This keeps penalize-don't-skip intact (failed or thin retrieval never earns full credit, and
failure still separately triggers `precondition_penalty`), while removing the incentive
distortion the critique identified: an ARA can no longer be pushed toward zero purely because a
sub-field is small, and an ARA can no longer win purely by choosing an obscure sub-field to force
empty retrieval, since empty-but-clean retrieval caps at 0.5 confidence toward a low (0.35) prior,
not toward 1.0.

### 6. Score Impact-if-Solved (decoupled from novelty's retrieval bundle)

Impact draws on a **separate, gap-level external query**, not on the per-target overlap-candidate
pools from §3/§4. This is the fix for the critique's third weakness: reusing the novelty
retrieval bundle for impact meant a single noisy retrieval call could move both halves of the
final score in the same direction for the same (unrelated to actual novelty or impact) reason.

- `field_activity_query`: run once per gap (not per claim/concept target), querying citation count
  of papers on the gap's domain as a whole and, if clinical/interventional, the count of active
  trials in that condition/intervention space. This produces a single scale signal
  (`citing_paper_count`, `active_trial_count`) independent of whether any specific candidate was
  classified `already_done` for a claim or gap target.
- `problem_scale`: disease burden, affected population, cost, field bottleneck centrality, or
  breadth of downstream use — informed by `field_activity_query` counts and the ARA's own
  Observations, not by novelty's candidate classifications.
- `scientific_leverage`: whether solving the gap unlocks new measurement, causal discrimination,
  unification of inconsistent findings, reproducibility, or method reuse — read from the ARA's
  Gaps/Key Insight/Enables fields.
- `practical_actionability`: whether the result changes clinical, policy, engineering,
  experimental, or theoretical decisions — read from claims and solution/constraints.
- `evidence_grounding`: computed **only from ARA-internal fields** — whether the impact claim is
  backed by a specific Observation, a Gap's `Caused by` chain, a Claim's evidence basis, or a
  `related_work.md` dependency block. This dimension never reads the novelty classifier's overlap
  output or the per-target candidate list, so a noisy or lucky novelty retrieval cannot spill into
  the impact score.

```text
Score the impact-if-solved of this scientific gap using only the provided ARA fields and the
gap-level field-activity signal (NOT the per-target novelty candidate classifications).
ARA problem/gap/insight:
{problem_gap_insight_text}
Claims:
{claim_summaries}
Related work context:
{related_work_summaries}
Gap-level field-activity signal (citing_paper_count, active_trial_count):
{field_activity_summary}

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

If impact cannot be computed because the artifact is thin, set missing dimensions to 0 rather than
excluding them. If `field_activity_query` itself fails, set `field_activity_query_failed=True` and
apply the corresponding precondition penalty (§7) — this failure is scored independently of
whether `family_L`/`family_S` (novelty retrieval) succeeded, preserving the decoupling.

### 7. Penalize Input Thinness and Precondition Failures

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

- `problem_quality`: required sections present; observations cite evidence; gaps have specific
  existing attempts and failure modes; key insight is not just a method name.
- `claims_quality`: claims have falsifiable statements, sources with quotes, evidence bases, and
  tags.
- `concepts_quality`: concepts are genuine technical terms with definitions and boundary
  conditions; generic glossary padding is penalized.
- `related_work_quality`: full typed dependency blocks and a brief citation-footprint tier are
  present; close predecessors are not omitted.
- `solution_quality`: constraints are substantive; method files match the paper genre; limitations
  and relevant caveats are captured.

Apply precondition penalties:

```python
precondition_penalty = 0.0
if family_L_status == "failed" or family_S_status in ("failed", "unavailable"):
    precondition_penalty += 0.20
if clinical_target and trial_lookup_failed:
    precondition_penalty += 0.10
if more_than_half_targets_unparseable:
    precondition_penalty += 0.25
if related_work_missing_or_too_thin:
    precondition_penalty += 0.20
if field_activity_query_failed:
    precondition_penalty += 0.10
precondition_multiplier = max(0.0, 1.0 - precondition_penalty)
```

These penalties implement penalize-don't-skip: unavailable artifact fields, failed or unavailable
retrieval families, unknown candidate classification, malformed targets, missing related-work
context, and failed impact field-activity queries all lower the metric value. Note that a missing
second retrieval family (`family_S == "unavailable"`) is penalized exactly like a failed one — the
metric never silently falls back to single-family evidence and calls it clean.

### 8. Final Scoring Function

Reference Python:

```python
from statistics import mean

def clamp01(x):
    return max(0.0, min(1.0, float(x)))

NEUTRAL_PRIOR = 0.35

def retrieval_confidence(t):
    if t.get("family_L_status") == "failed" or t.get("family_S_status") in ("failed", "unavailable"):
        return 0.0
    if t.get("related_work_missing_or_too_thin", False):
        return 0.3
    total_relevant = t.get("relevant_candidates_L", 0) + t.get("relevant_candidates_S", 0)
    if total_relevant >= 3 and t.get("exact_phrase_query_succeeded", False):
        return 1.0
    if total_relevant >= 1:
        return 0.7
    return 0.5

def m17_score(targets, impact_dims, quality_dims, flags):
    # targets are never filtered out; malformed targets should have low component values
    if not targets:
        target_scores = [0.0]
    else:
        target_scores = []
        for t in targets:
            specificity = clamp01(t.get("specificity", 0.0))
            delta = clamp01(t.get("delta_quality", 0.0))
            done_before_penalty = clamp01(t.get("done_before_penalty", 0.25))
            raw_novelty = specificity * delta * (1.0 - done_before_penalty)
            conf = clamp01(retrieval_confidence(t))
            blended = conf * raw_novelty + (1.0 - conf) * NEUTRAL_PRIOR
            target_scores.append(max(0.0, blended))

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
    if flags.get("family_L_failed", False) or flags.get("family_S_failed_or_unavailable", False):
        precondition_penalty += 0.20
    if flags.get("clinical_target", False) and flags.get("trial_lookup_failed", False):
        precondition_penalty += 0.10
    if flags.get("more_than_half_targets_unparseable", False):
        precondition_penalty += 0.25
    if flags.get("related_work_missing_or_too_thin", False):
        precondition_penalty += 0.20
    if flags.get("field_activity_query_failed", False):
        precondition_penalty += 0.10

    precondition_multiplier = max(0.0, 1.0 - precondition_penalty)

    raw = 0.65 * novelty + 0.35 * impact
    return clamp01(raw * availability_quality * precondition_multiplier)
```

Suggested interpretation:

- `0.85-1.00`: precise, externally checked (both retrieval families) novelty with high impact and
  strong artifact coverage.
- `0.65-0.84`: likely novel and useful, with some uncertainty or weaker scoping.
- `0.40-0.64`: partially novel, incremental, or under-supported by artifact/literature coverage;
  includes the "clean retrieval, sparse comparator set" regime for otherwise strong targets.
- `0.15-0.39`: mostly done before, vague, low impact, seriously under-scoped, or resting on
  unconfirmed (low-confidence) retrieval; this is also where a target sitting at the
  `NEUTRAL_PRIOR` floor lands.
- `0.00-0.14`: unparseable, unsupported, missing, contradicted by prior literature, or produced
  under a failed/unavailable retrieval family.

## Failure Modes and Gaming Routes

The main gaming route is hiding close predecessors by writing a narrow problem statement or a thin
related-work graph. M17 counters this by querying claims, gaps, concepts, and method details
independently through *two* differently-biased retrieval families; an omitted predecessor can
still appear through claim or method search in either family, and a term-substituted predecessor
that a lexical query misses is exactly what Family S (embedding recall) is built to surface.

A second route is novelty inflation: using new labels for old ideas. The dimension-separated
classifier compares problem, method, claim, population/domain, outcome, and concept dimensions
separately, and Family S's cosine-similarity retrieval is specifically resistant to vocabulary
substitution, so terminological novelty alone cannot produce a high score even if the ARA author
picks unfamiliar terms.

A third route is impact inflation: attaching a common high-burden disease or broad societal phrase
to a low-leverage technical delta. The impact sub-score requires field leverage, actionability, and
internal evidence grounding rather than external retrieval metadata shared with novelty, so scale
alone is insufficient, and gaming impact cannot be done by simply steering the novelty retrieval
queries.

A fourth route is strategic vagueness. Vague gaps and insights lower target specificity and
normalization quality, and because they remain in the denominator, they reduce the final score.

A fifth route, closed in this cycle, is **strategic obscurity**: picking a niche narrow enough that
both retrieval families plausibly return nothing, hoping empty retrieval reads as "confirmed
novel." Under §4/§5, empty-but-clean retrieval caps `retrieval_confidence` at 0.5 and blends toward
a `NEUTRAL_PRIOR` of 0.35 — below the "likely novel" band — so this route yields a mediocre score,
not a high one, while still not being crushed to zero the way a merely under-published (but
legitimately novel) sub-field would be under the old coverage-as-multiplier design.

## Why It Is Hard to Goodhart

M17 is hard to Goodhart because it triangulates novelty from multiple ARA layers and two
independently-biased external retrieval channels rather than trusting a single self-description or
a single search family. A compiler cannot simply add the word "novel," rename the mechanism, or
write in unfamiliar vocabulary; it must provide concrete gaps, prior attempts, failure modes,
claims, concepts, and method boundaries that survive both lexical and semantic external search. The
score also distinguishes close predecessor, enabling background, and already-done cases, which
prevents both excessive punishment for legitimate dependencies and excessive reward for
rediscovered work.

The penalize-don't-skip rule further reduces gaming. Missing sources, failed or unavailable
retrieval families, malformed fields, abstract-only thinness, absent brief citation footprints, and
unknown classifications all lower the score, and a missing second retrieval family is treated
exactly as a failure — it cannot be silently dropped to make a single-family search look
sufficient. At the same time, the retrieval-confidence blend (§4/§5) ensures this penalty regime
does not accidentally create its own gaming route: an author cannot win by making retrieval fail to
find anything, because unconfirmed novelty is capped well below the confirmed-novel band, not
promoted into it.

## Composition with the Suite

This metric is net-new relative to an internal verifier because it asks whether the paper's
contribution was already present in the external literature and whether solving it matters.
Internal verifiers can judge whether claims are grounded, sections are present, and dependencies
are coherent; M17 judges external priority and value using two independent external retrieval
channels the verifier never touches.

It composes well with grounding, claim-quality, related-work-completeness, method-validity, and
constraint metrics. Those metrics answer whether the ARA faithfully represents the source. M17
uses that representation to answer a different question: whether the represented contribution is
meaningfully new and worth attention. When the other metrics are low, M17 should usually fall
through the availability multiplier rather than pretending novelty can be assessed independently
of artifact quality. Impact's evidence-grounding term is deliberately restricted to internal
artifact fields (never the novelty retrieval bundle) so that M17's two halves — external novelty
and impact — remain independently falsifiable rather than sharing a single noisy data source.

## Assumptions

This expansion assumes external retrieval can access at least Semantic Scholar-style title/abstract
metadata, an arXiv/PubMed/bioRxiv abstract embedding index for the semantic-recall family, and,
where relevant, clinical-trial registry metadata. If only partial external access is available, the
workflow still runs, but retrieval failure or unavailability in either family is scored as
uncertainty and penalized (both via `retrieval_confidence` capping and via `precondition_penalty`)
rather than skipped, and the metric never substitutes single-family evidence for the required dual
family without penalty.

It also assumes all candidate targets from the artifact are evaluated, including weak or malformed
ones. This is intentional: an ARA that cannot state what is new at claim, gap, insight, or method
level should receive a lower novelty score. It further assumes that a target with high specificity
and a well-argued delta, sitting in a genuinely sparse literature confirmed by two independently
clean but empty retrieval passes, deserves a cautious middle score rather than either a top score
(unconfirmed) or a near-zero score (previously conflated with "not novel").
