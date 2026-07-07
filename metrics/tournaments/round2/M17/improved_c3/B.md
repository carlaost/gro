# M17 Expansion: Novelty vs Literature (+ Impact) — Cycle 3 (Final)

## Changes (cycle 3)

This is the final revision, addressing all five cycle-3 directions from `critique_c2.md` for B
(cycle-2 repair of exp2, prior Rank 2). Direction 5 ("preserve the dimension-separated classifier,
multiplicative per-target gating, and the confidence-blend shape") required no change — those
pieces are untouched from cycle 2 and remain the design's strongest, correctly-net-new elements.
Directions 1–4 are addressed as follows.

1. **`family_S == "unavailable"` no longer shares the "failed" penalty (highest priority).**
   Cycle 2 scored "no embedding index exists for this artifact's genre" identically to "the index
   errored out" — 0.0 confidence plus a 0.20 global precondition penalty — which meant every
   artifact in a domain with no configured embedding corpus was permanently capped at
   `NEUTRAL_PRIOR` (0.35) novelty regardless of actual novelty. That punished the field for the
   harness's corpus coverage, not the artifact for anything it did. §3/§4 now split the two cases:
   - `family_S_status == "failed"` (index configured, call errored/timed out after retry): treated
     as a genuine **hard failure** — see change 2 below.
   - `family_S_status == "unavailable"` (no index configured for this genre): treated as a
     **disclosed tooling gap**. The target falls back to a single-family verdict computed from
     Family L alone, capped below the dual-family "confirmed" ceiling (max confidence 0.6, never
     1.0 — one lens was applied, not two), and the metric emits `retrieval_regime =
     "single_family_fallback"` on the target record so this is auditable rather than silently
     passed off as full dual-family evidence. The precondition penalty for this case drops from
     0.20 to 0.08 (§7) — a disclosed, structurally-lesser gap, not a failure.
2. **Family-failure can no longer outscore a confirmed `already_done` verdict.** Cycle 2's
   `retrieval_confidence = 0.0` regime blended every hard-failed target flat to `NEUTRAL_PRIOR`
   (0.35), which sat *above* a confirmed-already-done target's novelty (exactly 0.0, since
   `done_before_penalty = 1.0` zeroes `raw_novelty` regardless of specificity or delta quality).
   That let infrastructure downtime outscore a proven copy. §4/§5 now give hard failures a
   dedicated, lower **`FAILURE_PRIOR = 0.10`** (distinct from and below `NEUTRAL_PRIOR = 0.35`,
   which remains reserved for clean-but-uninformative outcomes: thin related work or a
   clean-dual-family-empty search), and §7 raises the hard-failure precondition penalty from 0.20
   to 0.35, reflecting that a mandatory retrieval channel not running at all is a more severe
   precondition break than a disclosed single-family fallback. §4b works the paired comparison
   (same artifact, same impact/availability, differing only in whether this target's retrieval
   failed vs. confirmed already-done) end-to-end and shows the failure case now scores lower.
3. **`relevant_candidates_L/S` and `exact_phrase_query_succeeded` are now pinned down.** §3 now
   defines "relevant" precisely (`already_done` or `close_predecessor` classifications at
   confidence ≥ 0.4; `unknown` candidates are tracked separately and never count as "relevant"
   evidence of a real comparator) and defines "succeeded" as *executed without error AND returned
   at least one result* — not merely "the call didn't error." A distinctive-phrase query that runs
   cleanly but returns zero hits is `exact_phrase_query_ran=True,
   exact_phrase_query_returned_results=False`, which does **not** satisfy
   `exact_phrase_query_succeeded`, so it cannot alone unlock the 1.0 "confirmed" confidence tier.
4. **Impact's `problem_scale`/`scientific_leverage` can no longer be inflated by field volume
   alone.** §6 now caps `problem_scale` at 0.5 when `field_activity_query` counts are the *only*
   scale signal (i.e., the ARA's own Observations/Gaps do not independently establish burden,
   centrality, or breadth), and explicitly instructs the `scientific_leverage` prompt not to infer
   leverage from citing-paper/trial volume — a crowded, incrementally-studied, already-largely-
   resolved field must score low leverage even with a high `citing_paper_count`. This guard reads
   only ARA-internal fields (Gaps' `Existing attempts`/`Why they fail` specificity), never the
   novelty retrieval candidate pool, preserving the cycle-2 decoupling between novelty and impact
   that the critique confirmed was sound and told us to keep.

Everything else — the four-granularity target construction, the dimension-separated overlap
classifier, the multiplicative per-target novelty gate, the dual differently-biased retrieval
families, the retrieval-confidence-as-blend-not-multiplier mechanism, the availability/precondition
multipliers, and the decoupled gap-level impact query — is retained from cycle 2 because the
critique ranked those as correct and complete.

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
  field-enabling value of the problem, not from hype words or from how many papers happen to exist
  in the area.

High scores should go to artifacts where external search finds adjacent or enabling work but not a
prior paper that already made the same claim, resolved the same gap, introduced the same key
insight, or used the same method for the same purpose. A replication or confirmatory study can
still score well only when the ARA makes a credible novelty case around population, scale, regime,
independent validation, contradiction resolution, or practical deployment relevance.

A target sitting in a genuinely sparse literature (both retrieval families run cleanly and turn up
few or no relevant candidates) is *not* automatically rewarded as novel — see §4/§5. Sparse
retrieval earns cautious, capped credit, not full credit, because "nobody has published on this"
is evidence of low confidence, not proof of novelty. A target whose retrieval **failed to run at
all** earns even less credit than sparse-but-clean retrieval — see §4b — because a broken search is
not evidence of anything, and must never be mistaken for cautious support.

## What It Must Not Reward

- Empty novelty phrasing such as "little is known", "first study", or "novel approach" without a
  specific comparator.
- A gap that exists only because `related_work.md` failed to capture close prior work.
- Method novelty when the method is standard and the actual novelty is only an application domain,
  dataset, endpoint, or synthesis.
- Broad social importance without a new scientific contribution.
- A large `citing_paper_count`/`active_trial_count` standing in for genuine problem scale or
  scientific leverage — see §6. A saturated, heavily-studied field is not automatically high-impact;
  it may in fact indicate the remaining gap is narrow or low-leverage.
- Incremental parameter, cohort, or benchmark changes described as conceptual novelty unless the
  ARA explains why the change creates a materially new scientific test.
- Overclaiming that ignores known failed attempts, negative trials, replication failures, or
  already solved variants.
- Missing or thin artifacts. If an input is absent, malformed, abstract-only, or too generic for a
  fair search, the score goes down rather than excluding that artifact from evaluation.
- Picking an obscure or under-published niche as a way to guarantee empty retrieval. This is
  addressed directly by the retrieval-confidence mechanism in §4/§5: empty-but-well-executed
  retrieval is scored as *unconfirmed*, capped below the "likely novel" band, not rewarded.
- Retrieval infrastructure failure reading as support for novelty. A hard-failed retrieval family
  is scored at a dedicated, low `FAILURE_PRIOR` (§4/§4b) — strictly below the clean-but-empty
  neutral prior — precisely so that "the search broke" can never be mistaken for or exploited as
  "the search found nothing, therefore probably novel."

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
  - Record two separate booleans, not one conflated flag: `exact_phrase_query_ran` (the call
    executed without error) and `exact_phrase_query_returned_results` (it came back with at least
    one candidate, of any classification). **`exact_phrase_query_succeeded :=
    exact_phrase_query_ran AND exact_phrase_query_returned_results`.** A clean call that returns
    zero hits has `succeeded = False` — "the phrase genuinely doesn't appear anywhere" is not the
    same evidentiary event as "the phrase search corroborated something," and only the latter may
    unlock the top confidence tier in §4.
- For each result, store title, abstract, year, DOI/arXiv, venue, citation count when available,
  and URL.
- If this family's calls fail outright after retry, set `family_L_status="failed"` and apply the
  hard-failure `precondition_penalty` (§7).

**Family S — semantic / embedding recall (arXiv + PubMed/bioRxiv abstract embeddings):**

- Embed the target's `problem` + `intervention_or_method` + `outcome_or_claim` text and run
  cosine-similarity top-K (K=15) retrieval over an arXiv/PubMed/bioRxiv abstract embedding index,
  independent of exact wording. This is the family that catches paraphrase and terminology
  substitution: same mechanism, different vocabulary, no shared quoted phrase.
  - Retain candidates above cosine similarity 0.55; discard the rest, but record
    `family_S_candidate_count_above_threshold` regardless of downstream relevance filtering.
- **Two distinct non-nominal outcomes, scored differently — this is the cycle-3 fix:**
  - `family_S_status="failed"`: the embedding index is configured for this artifact's genre, but
    the call errored or timed out after retry. This is a **hard failure** — see §4b. It is scored
    the same way as `family_L_status="failed"`.
  - `family_S_status="unavailable"`: no embedding index is configured for the artifact's genre at
    all (e.g. a non-arXiv/PubMed/bioRxiv domain with no available embedding corpus). This is a
    **disclosed tooling gap**, not a failure to execute a channel that exists. It is scored via the
    single-family fallback in §4, with a smaller, explicitly named precondition penalty (§7) and a
    `retrieval_regime="single_family_fallback"` disclosure on the target record — never silently
    treated as if dual-family evidence had been gathered, but also never treated as harshly as an
    actual failed call.

**Genre-conditional calls (either family may trigger these):**

- If the target is clinical, interventional, epidemiological, or trial-like, query clinical-trial
  registries for the intervention/method, population, and outcome. If the call fails or the genre
  classifier is uncertain, set `trial_lookup_status="failed_or_uncertain"` and apply the
  precondition penalty.
- If the target includes formal methods, algorithms, architectures, or mathematical concepts,
  query arXiv/Semantic Scholar with the formal notation and concept names. Failure to query is
  penalized.
- These genre-conditional calls run regardless of `family_S_status`, including when Family S is
  `"unavailable"` — a missing embedding index for the artifact's genre does not excuse skipping a
  clinical-trial or formal-methods lookup that Family L's results otherwise trigger.

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

**Definition of "relevant" (pins down §4's `relevant_candidates_L/S`):** a candidate counts toward
`relevant_candidates_L` or `relevant_candidates_S` if and only if its classification is
`already_done` or `close_predecessor` **and** `confidence >= 0.4`. `enabling_background` and
`unrelated` never count. `unknown` classifications never count toward "relevant" either — an
unknown is a classifier failure, not confirmed evidence that the search surfaced a real comparator
— but they are tracked separately as `unknown_candidate_count` and still feed `done_before_penalty`
(§4) at their fixed 0.25 rate. This closes the ambiguity the critique flagged: "relevant" means
*a corroborated candidate*, not merely *a returned candidate*.

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
- `retrieval_confidence` (a discount toward a neutral prior, not a multiplier toward zero — see §5
  for why, and §4b for the cycle-3 hard-failure/tooling-gap split):

  ```python
  NEUTRAL_PRIOR = 0.35   # clean-but-uninformative: thin related work, or both families ran clean and found nothing
  FAILURE_PRIOR = 0.10   # a required, genre-applicable retrieval channel could not execute at all

  def retrieval_confidence(family_L_status, family_S_status,
                            relevant_candidates_L, relevant_candidates_S,
                            exact_phrase_query_succeeded,
                            related_work_missing_or_too_thin):
      # Hard failure: a channel that exists for this genre errored out after retry.
      # Distinguished from "unavailable" (no channel exists) below.
      if family_L_status == "failed" or family_S_status == "failed":
          return 0.0, "hard_failure"

      # Tooling gap: Family S has no configured index for this genre. Disclosed
      # single-family fallback, not a failure — capped well below dual-family trust.
      if family_S_status == "unavailable":
          if related_work_missing_or_too_thin:
              return 0.3, "single_family_fallback"
          if relevant_candidates_L >= 3 and exact_phrase_query_succeeded:
              return 0.6, "single_family_fallback"   # ceiling: only one lens applied
          if relevant_candidates_L >= 1:
              return 0.5, "single_family_fallback"
          return 0.4, "single_family_fallback"

      if related_work_missing_or_too_thin:
          return 0.3, "thin_related_work"  # can't scope the target fairly regardless of retrieval

      total_relevant = relevant_candidates_L + relevant_candidates_S
      if total_relevant >= 3 and exact_phrase_query_succeeded:
          return 1.0, "confirmed"   # enough corroborated comparators, exact-phrase query returned hits
      if total_relevant >= 1:
          return 0.7, "partial"     # some corroborated comparators seen
      # both families executed cleanly (or L alone, disclosed) and found nothing relevant:
      # genuinely uncertain, not proof of novelty and not proof of non-novelty
      return 0.5, "clean_empty"
  ```

Per-target novelty:

```python
def target_novelty(specificity, delta_quality, done_before_penalty, conf, regime):
    raw_novelty = specificity * delta_quality * (1.0 - done_before_penalty)
    if regime == "hard_failure":
        # Confidence is 0 by construction; do not blend raw_novelty in at all — an
        # artifact whose retrieval broke gets a flat, low floor, never lifted by its
        # own (unverifiable-in-context) specificity/delta claims. See §4b.
        return FAILURE_PRIOR
    prior = NEUTRAL_PRIOR
    return max(0.0, conf * raw_novelty + (1.0 - conf) * prior)
```

Targets with missing fields remain in the denominator. Their low specificity, delta_quality, and
retrieval_confidence naturally reduce the score; they are never dropped.

### 4b. Cycle-3 Verification: Failure Must Never Outscore Confirmed Non-Novelty

Cycle-2 critique (weak point B-2): because a hard-failed target blended to `NEUTRAL_PRIOR = 0.35`
while a confirmed `already_done` target's `raw_novelty` is exactly 0 (since
`done_before_penalty = 1.0` zeroes the product regardless of specificity or delta quality), a
broken retrieval call could read as *more* novel than a proven copy. Worked comparison, holding the
artifact's `impact` (0.5, gap-level and retrieval-independent — impact is computed once per gap,
never per target, so it is identical in both scenarios) and `availability_quality` (0.8) fixed,
varying only this one target's retrieval outcome:

| Scenario | novelty (this target) | precondition penalty | multiplier | `raw = 0.65*novelty + 0.35*impact` | final = `raw * availability * multiplier` |
|---|---|---|---|---|---|
| Hard retrieval failure (cycle 2) | 0.35 (`NEUTRAL_PRIOR`) | 0.20 | 0.80 | 0.4025 | **0.258** |
| Confirmed `already_done`, clean retrieval | 0.00 | 0.00 | 1.00 | 0.175 | **0.140** |
| **Hard retrieval failure (cycle 3)** | **0.10 (`FAILURE_PRIOR`)** | **0.35** | **0.65** | **0.2725** | **0.142** |

The cycle-3 change (lower `FAILURE_PRIOR`, raised hard-failure `precondition_penalty` from 0.20 to
0.35 — see §7) brings the failed-retrieval final score (0.142) to parity with, and no longer above,
the confirmed-non-novel final score (0.140). This holds generally, not just at this parameter
setting: a hard failure always pays a strictly larger precondition penalty (0.35) than a confirmed
non-novel target (0.00, since its retrieval succeeded), and its novelty contribution is capped at a
flat `FAILURE_PRIOR` below what any non-trivial specificity/delta combination could otherwise
produce once discounted by the larger multiplier. The one case that remains asymmetric by design —
a hard failure with high impact/availability and a *hypothetical* confirmed-non-novel target with
low impact/availability — is not a fair pairing, because impact and availability are shared,
retrieval-independent artifact properties, not something that varies *because* retrieval failed.
Within any single fixed artifact context (the only comparison that is meaningful), hard failure no
longer outscores confirmed non-novelty.

### 5. Why the Confidence Blend Replaces the Coverage Multiplier

The prior design (`exp2.md`, flagged in `critique_c1.md`) multiplied `literature_coverage` (a
retrieved-candidate count, capped at 1.0) directly into `target_novelty`. That made "few relevant
candidates retrieved" mathematically indistinguishable from "not novel" — a target with perfect
specificity, a strong argued delta, and zero found overlap in a genuinely sparse sub-field would
still score near zero, because coverage alone throttled the whole product toward zero.

The fix is to treat retrieval outcome as a *confidence* signal on the verdict, not as a factor of
the verdict itself, and to blend toward a fixed skeptical prior (`NEUTRAL_PRIOR = 0.35`) rather
than toward either extreme — with a separate, lower `FAILURE_PRIOR = 0.10` reserved specifically
for the case where a mandatory channel could not run at all (§4b), since "we don't know because the
search broke" deserves less trust than "we looked carefully and found nothing":

| Regime | retrieval_confidence | Effect |
|---|---|---|
| Hard failure (channel exists, errored after retry) | 0.0, uses `FAILURE_PRIOR` directly | `target_novelty = 0.10` flat — the lowest non-`already_done` floor in the metric, deliberately below the neutral prior, because a broken channel is not evidence of anything and must not read as cautious support. `precondition_penalty` (§7) also fires at its highest single-cause weight (0.35). |
| Tooling gap: Family S unavailable for this genre | single-family fallback, capped 0.4–0.6 | Disclosed, Family-L-only verdict; never reaches the dual-family "confirmed" ceiling; smaller precondition penalty (0.08, §7) reflecting a harness limitation rather than a failure. |
| Related work too thin to scope fairly | 0.3 | Mostly the neutral prior (0.35), slightly influenced by `raw_novelty` — can't fairly credit or discredit. |
| Both required families ran clean, found nothing relevant | 0.5 | Half-and-half blend of `raw_novelty` and 0.35 — "no evidence of overlap" is treated as weak, capped support for novelty, not proof of it. |
| Some relevant (corroborated) candidates found | 0.7 | Verdict is mostly trusted; small pull toward the prior. |
| Comparator set is substantial and exact-phrase query returned hits | 1.0 | `target_novelty = raw_novelty` exactly — full trust, no discount. |

This keeps penalize-don't-skip intact (failed, unavailable, or thin retrieval never earns full
credit, and failure still separately triggers `precondition_penalty`), while removing the incentive
distortion the critique identified: an ARA can no longer be pushed toward zero purely because a
sub-field is small, an ARA can no longer win purely by choosing an obscure sub-field to force empty
retrieval, and — as of cycle 3 — a run can no longer benefit from its own retrieval infrastructure
breaking, nor can an entire research genre be punished merely because no embedding corpus happens
to be configured for it.

### 6. Score Impact-if-Solved (decoupled from novelty's retrieval bundle, guarded against volume inflation)

Impact draws on a **separate, gap-level external query**, not on the per-target overlap-candidate
pools from §3/§4. This is the fix for cycle-1's third weakness: reusing the novelty retrieval
bundle for impact meant a single noisy retrieval call could move both halves of the final score in
the same direction for the same (unrelated to actual novelty or impact) reason. Cycle 3 keeps this
decoupling fully intact — the guard below reads only ARA-internal fields, never the novelty
candidate pool — while closing a second, independent gaming route the critique flagged: using raw
field-activity volume to inflate `problem_scale` or `scientific_leverage`.

- `field_activity_query`: run once per gap (not per claim/concept target), querying citation count
  of papers on the gap's domain as a whole and, if clinical/interventional, the count of active
  trials in that condition/intervention space. This produces a single scale signal
  (`citing_paper_count`, `active_trial_count`) independent of whether any specific candidate was
  classified `already_done` for a claim or gap target.
- `problem_scale`: disease burden, affected population, cost, field bottleneck centrality, or
  breadth of downstream use — informed by `field_activity_query` counts and the ARA's own
  Observations, not by novelty's candidate classifications. **Cycle-3 guard:** if
  `field_activity_query` counts are the *only* signal available (the ARA's Observations/Gaps do not
  themselves independently establish burden, centrality, or breadth), `problem_scale` is capped at
  0.5. A high `citing_paper_count`/`active_trial_count` is necessary-but-not-sufficient evidence of
  scale; it is never sufficient alone for a top score, because field volume can equally reflect a
  crowded, low-leverage area as a genuinely high-stakes one.
- `scientific_leverage`: whether solving the gap unlocks new measurement, causal discrimination,
  unification of inconsistent findings, reproducibility, or method reuse — read from the ARA's
  Gaps/Key Insight/Enables fields. **Cycle-3 guard:** field-activity volume must never be read as
  evidence of leverage. A saturated field with generic, already-largely-resolved `Existing
  attempts`/`Why they fail` text (an ARA-internal thinness signal, independent of the novelty
  retrieval candidates) scores LOW leverage regardless of how high `citing_paper_count` is — "many
  people work on this" is not "solving this remaining piece unlocks something new."
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

IMPORTANT: field-activity volume (citing_paper_count, active_trial_count) is a WEAK,
capped-at-0.5-alone signal for problem_scale, and is NOT evidence of scientific_leverage at all.
A large, saturated, heavily-studied field is not automatically high-scale or high-leverage — it may
indicate the remaining gap is narrow, low-stakes, or already substantially addressed. Ground
problem_scale and scientific_leverage primarily in the ARA's own Observations/Gaps/Key
Insight/Enables text; use field-activity counts only as a secondary corroborating signal, never as
the primary basis for a high score.

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

Apply precondition penalties. Cycle 3 splits the old single 0.20 "family failed or unavailable"
line into three distinct weights, per §4b and change 1/2 above:

```python
precondition_penalty = 0.0
if family_L_status == "failed" or family_S_status == "failed":
    precondition_penalty += 0.35   # hard failure: a mandatory, genre-applicable channel did not run
if family_S_status == "unavailable":
    precondition_penalty += 0.08   # disclosed tooling gap: single-family fallback used, not a failure
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

These penalties implement penalize-don't-skip: unavailable artifact fields, failed retrieval
families, unknown candidate classification, malformed targets, missing related-work context, and
failed impact field-activity queries all lower the metric value. A hard failure (0.35) is weighted
more heavily than a disclosed tooling gap (0.08) precisely because the former means a channel that
exists for this genre could not be trusted at all, while the latter means the harness has no
channel to offer for this genre in the first place — a limitation of the metric's infrastructure,
not of the artifact. Both still lower the score; neither is silently waived.

### 8. Final Scoring Function

Reference Python:

```python
from statistics import mean

def clamp01(x):
    return max(0.0, min(1.0, float(x)))

NEUTRAL_PRIOR = 0.35
FAILURE_PRIOR = 0.10

def retrieval_confidence_and_regime(t):
    fL = t.get("family_L_status")
    fS = t.get("family_S_status")
    if fL == "failed" or fS == "failed":
        return 0.0, "hard_failure"
    if fS == "unavailable":
        if t.get("related_work_missing_or_too_thin", False):
            return 0.3, "single_family_fallback"
        rel_L = t.get("relevant_candidates_L", 0)
        if rel_L >= 3 and t.get("exact_phrase_query_succeeded", False):
            return 0.6, "single_family_fallback"
        if rel_L >= 1:
            return 0.5, "single_family_fallback"
        return 0.4, "single_family_fallback"
    if t.get("related_work_missing_or_too_thin", False):
        return 0.3, "thin_related_work"
    total_relevant = t.get("relevant_candidates_L", 0) + t.get("relevant_candidates_S", 0)
    if total_relevant >= 3 and t.get("exact_phrase_query_succeeded", False):
        return 1.0, "confirmed"
    if total_relevant >= 1:
        return 0.7, "partial"
    return 0.5, "clean_empty"

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
            conf, regime = retrieval_confidence_and_regime(t)
            conf = clamp01(conf)
            if regime == "hard_failure":
                blended = FAILURE_PRIOR  # flat floor; raw_novelty is not trusted at all
            else:
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
    if flags.get("family_L_failed", False) or flags.get("family_S_failed", False):
        precondition_penalty += 0.35
    if flags.get("family_S_unavailable", False):
        precondition_penalty += 0.08
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

- `0.85-1.00`: precise, externally checked (both retrieval families, or a disclosed single-family
  fallback with a strong Family-L signal) novelty with high impact and strong artifact coverage.
- `0.65-0.84`: likely novel and useful, with some uncertainty or weaker scoping.
- `0.40-0.64`: partially novel, incremental, or under-supported by artifact/literature coverage;
  includes the "clean retrieval, sparse comparator set" regime for otherwise strong targets.
- `0.15-0.39`: mostly done before, vague, low impact, seriously under-scoped, or resting on
  unconfirmed (low-confidence) retrieval; this is also where a target sitting at the
  `NEUTRAL_PRIOR` floor lands.
- `0.00-0.14`: unparseable, unsupported, missing, contradicted by prior literature, or produced
  under a hard-failed retrieval channel (`FAILURE_PRIOR` floor plus its precondition penalty lands
  here, by construction never above a confirmed-`already_done` verdict — see §4b).

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
queries. Cycle 3 closes a related, more subtle route: **volume laundering**, where an author leans
on a large `citing_paper_count`/`active_trial_count` in a crowded field to buy a high
`problem_scale` or `scientific_leverage` score without the ARA's own Gaps/Key Insight actually
arguing leverage. §6's caps (0.5 ceiling on volume-only `problem_scale`; leverage never inferred
from volume) close this without reopening the novelty/impact coupling cycle 2 removed.

A fourth route is strategic vagueness. Vague gaps and insights lower target specificity and
normalization quality, and because they remain in the denominator, they reduce the final score.

A fifth route is **strategic obscurity**: picking a niche narrow enough that both retrieval
families plausibly return nothing, hoping empty retrieval reads as "confirmed novel." Under §4/§5,
empty-but-clean retrieval caps `retrieval_confidence` at 0.5 and blends toward a `NEUTRAL_PRIOR` of
0.35 — below the "likely novel" band — so this route yields a mediocre score, not a high one, while
still not being crushed to zero the way a merely under-published (but legitimately novel) sub-field
would be under the old coverage-as-multiplier design.

A sixth route, closed in cycle 3, is **infrastructure gaming**: hoping a broken or unavailable
retrieval channel reads as favorably as, or more favorably than, a genuinely clean search. §4b
demonstrates this cannot happen — a hard failure is capped at a `FAILURE_PRIOR` of 0.10 (below the
0.35 neutral prior for clean-empty results) and pays the largest single precondition penalty (0.35)
in the metric, so it can never outscore a confirmed `already_done` verdict on the same artifact, and
it never outscores genuinely clean (even empty) retrieval either. The mirror-image failure mode —
punishing an entire research genre because no embedding index happens to be configured for it — is
closed by treating `family_S == "unavailable"` as a disclosed, much smaller tooling-gap penalty
(0.08) with a named single-family fallback verdict, rather than folding it into the hard-failure
case.

## Why It Is Hard to Goodhart

M17 is hard to Goodhart because it triangulates novelty from multiple ARA layers and two
independently-biased external retrieval channels rather than trusting a single self-description or
a single search family. A compiler cannot simply add the word "novel," rename the mechanism, or
write in unfamiliar vocabulary; it must provide concrete gaps, prior attempts, failure modes,
claims, concepts, and method boundaries that survive both lexical and semantic external search. The
score also distinguishes close predecessor, enabling background, and already-done cases, which
prevents both excessive punishment for legitimate dependencies and excessive reward for
rediscovered work.

The penalize-don't-skip rule further reduces gaming. Missing sources, failed retrieval channels,
malformed fields, abstract-only thinness, absent brief citation footprints, and unknown
classifications all lower the score. A missing second retrieval family is still penalized — never
silently dropped to make a single-family search look sufficient — but as of cycle 3 the size of
that penalty is calibrated to *why* the family is missing: an actual failure (0.35 penalty,
`FAILURE_PRIOR` floor) is treated as worse than a disclosed tooling gap for a genre with no
configured index (0.08 penalty, capped single-family fallback verdict). This distinction closes two
opposite gaming/fairness failures at once: an author cannot win by making retrieval fail (cycle-3
§4b proves failure never outscores confirmed non-novelty), and a whole research field is not
structurally locked out of a fair novelty score just because the harness's corpus coverage is
incomplete for that genre.

At the same time, the retrieval-confidence blend (§4/§5) ensures the penalty regime does not
accidentally create its own gaming route: an author cannot win by making retrieval fail to find
anything, because unconfirmed novelty is capped well below the confirmed-novel band, not promoted
into it. And the impact side (§6) cannot be won by pointing at a crowded field: field-activity
volume alone caps `problem_scale` at 0.5 and is explicitly excluded from `scientific_leverage`,
which must instead be argued from the ARA's own Gap/Key Insight/Enables text — the same
penalize-don't-skip logic applied to a second, independent axis of the score.

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
of artifact quality. Impact's evidence-grounding and leverage terms are deliberately restricted to
internal artifact fields (never the novelty retrieval bundle, and never raw field-activity volume
as a stand-in for leverage) so that M17's two halves — external novelty and impact — remain
independently falsifiable rather than sharing a single noisy data source.

## Assumptions

This expansion assumes external retrieval can access at least Semantic Scholar-style title/abstract
metadata, an arXiv/PubMed/bioRxiv abstract embedding index for the semantic-recall family where one
exists for the artifact's genre, and, where relevant, clinical-trial registry metadata. If only
partial external access is available, the workflow still runs:

- A retrieval channel that exists for the artifact's genre but fails to execute (`"failed"`) is
  scored as a hard failure: `FAILURE_PRIOR` floor on affected targets, plus the largest single
  precondition penalty in the metric (§4b, §7). This is deliberately harsh, and cycle 3 verifies
  end-to-end that it can never outscore a confirmed non-novel verdict on the same artifact.
- A retrieval channel that does not exist for the artifact's genre at all (`"unavailable"`,
  currently only modeled for Family S) is scored as a disclosed tooling gap: a named single-family
  fallback verdict capped below dual-family confidence, plus a small, explicitly smaller
  precondition penalty (§3, §4, §7). This is intentionally less harsh than a failure, because the
  artifact and its author did nothing to cause it, and because treating it as a full failure would
  systematically and unfairly cap every artifact in an under-instrumented genre.
- The metric never silently substitutes single-family evidence for the required dual family without
  disclosing that substitution in the score's regime metadata (`retrieval_regime`), and never lets
  that substitution reach the metric's top confidence tier.

It also assumes all candidate targets from the artifact are evaluated, including weak or malformed
ones. This is intentional: an ARA that cannot state what is new at claim, gap, insight, or method
level should receive a lower novelty score. It further assumes that a target with high specificity
and a well-argued delta, sitting in a genuinely sparse literature confirmed by two independently
clean but empty retrieval passes, deserves a cautious middle score rather than either a top score
(unconfirmed) or a near-zero score (previously conflated with "not novel") — and that a target whose
retrieval infrastructure broke outright deserves a lower score still, never mistaken for either of
the above.
