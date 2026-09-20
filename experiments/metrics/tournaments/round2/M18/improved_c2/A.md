## Changes (cycle 2)

Addressing `critique_c1.md`'s cycle-2 directions for exp2 (RANK 1, one of two WINNERS):

- **Calibrated the penalty constants.** Added a "Why These Constants" rationale for the
  retrieval-status ladder and the specificity/vague/multi-source penalties, plus a worked
  example (Step 8) that runs three concrete units end-to-end to final numbers, so the
  constants are checkable rather than asserted.
- **Gated the RW role/coverage weight instead of always applying it.** Step 6 now first computes
  a deterministic `rw_dependent` flag from `logic/problem.md`'s own content (named external
  methods/datasets treated as imports, baselines, or comparators) — independent of whether
  `related_work.md` exists. Step 7's final function only spends the 0.15+0.10 role/coverage
  weight when `rw_dependent = true`; otherwise it redistributes that weight to the problem-layer
  terms proportionally. Critically, `rw_dependent` is computed from problem.md, not from
  related_work.md's presence, so a compiler cannot dodge the audit by simply omitting
  `related_work.md` when the problem clearly leans on external work — penalize-don't-skip is
  preserved.
- **Stated the L1 §10 edge explicitly inside the judging prompt**, adopting exp4's framing:
  the prompt now opens with an explicit instruction that a quote existing at a cited line is
  necessary but not sufficient, and that the model's job is entailment against the real source,
  not string presence.
- **Made source-identity resolution deterministic.** Step 3 replaces "choose the highest-confidence
  match" (previously left to the model) with an explicit `match_score` formula (title-token
  Jaccard + year agreement + author-surname overlap) and fixed thresholds that mechanically
  route a candidate to clean resolve, `source_identity_uncertain`, or `contradictory_identity`,
  removing the ungrounded judgment call the critique flagged.

Everything the critique did not flag as a weakness is preserved unchanged in substance: the
drift taxonomy, the retrieval-status ladder, the cross-layer role-drift audit itself, the
missing-citation/contradiction/vague-claim caps, the multi-source anti-laundering rule, the
JSON-validation-with-retry robustness, and the additive final scoring shape.

---

# M18 Expansion: Claim Drift / Reference Truthfulness (cycle 2)

## Metric Intent

This metric asks whether the ARA's problem-layer citations still mean what the real cited
sources mean. It is not enough for `logic/problem.md` to contain plausible observations,
local citation strings, or even source-like phrasing. A good ARA should preserve the actual
epistemic role of cited work: the cited papers, registrations, datasets, or methods should
support the specific empirical facts, gaps, existing-attempts summaries, and assumptions they
are invoked to support.

The metric rewards a problem statement whose Observations, Gaps, Key Insight derivation, and
Assumptions are grounded in sources that actually say the attributed thing, at the right level
of specificity. It penalizes citation drift: overclaiming, reversing findings, laundering
speculative background into established fact, citing a paper for a different
population/outcome/method, using a review as if it directly measured a result, citing only an
abstract when the claim needs full-text support, or assigning an imported dataset/method role
in `logic/related_work.md` that the source does not actually have.

The metric is deliberately external-source-facing. The ARA verifier (L1 §10) can check whether
a quote exists at a cited line inside the compiled artifact; **that check confirms string
presence, not truth**. This metric checks the harder question the verifier cannot: whether the
real source behind the citation supports the ARA's use of it. A quote that is verbatim-correct
and still misrepresents its source is exactly the failure mode this metric exists to catch, and
Step 4 states that distinction directly inside the judging prompt so it cannot be missed by
either the model or a future maintainer reading the workflow.

## What It Should Reward

- Problem Observations with precise, source-faithful empirical statements, including correct
  populations, interventions/exposures, outcome definitions, effect directions, measurement
  modality, and numerical values where present.
- Evidence fields that name real citations or section-level references with enough specificity
  to retrieve and audit the source.
- Gaps whose "Existing attempts" and "Why they fail" accurately summarize prior work rather than
  inventing limitations for narrative convenience.
- Key Insight derivations that follow from the stated Observations/Gaps and do not cite sources
  for a leap they do not motivate.
- Assumptions that are honestly identified as assumptions, not disguised as settled results from
  a citation.
- Cross-layer agreement with `logic/related_work.md`: sources described as imports, baselines,
  bounds, extensions, or refutations should have the same role when checked against the real
  source — audited whenever the problem layer actually leans on external work (see Step 6),
  regardless of whether `related_work.md` happens to exist.
- Explicit uncertainty when source access is partial; partial access is still scored downward,
  not skipped.

## What It Must Not Reward

- Citation-shaped decoration: author-year strings appended to claims without a retrievable
  bibliographic target.
- Verbatim local quoting that is copied from another ARA artifact but not confirmed against the
  external source — a correct quote is not evidence of a correct claim.
- Generic background citations used to support specific quantitative or causal claims.
- "Abstract-only" support for claims that require methods/results details.
- Correct paper identity with incorrect role assignment, e.g. citing a methods paper as if it
  reported a dataset result.
- Drift hidden by paraphrase, such as changing "associated with" to "predicts", "in mice" to
  "in patients", "may improve" to "improves", or "prior work is limited" to a specific
  nonexistent failure mode.
- A confidently resolved but wrong paper ("contradictory identity") used to rubber-stamp support
  that a correct source would not give.

## Failure Modes And Gaming Routes

The easiest gaming route is to make the problem layer vague enough that almost any source could
appear to support it. This metric counters that by extracting atomic claim-source pairs and
penalizing low-specificity statements. Another route is to cite review papers for broad facts;
that can be acceptable for background, but the scoring distinguishes direct support from
indirect support and penalizes direct empirical claims that rely only on a review when primary
evidence is named or required.

A compiler might also inflate `related_work.md` with many plausible RW blocks. The cross-layer
part checks whether each cited source's typed role matches the real source. More citations do
not help if they are thin, unretrievable, or role-drifted.

A subtler route, closed in this cycle: a compiler could delete or thin out `related_work.md`
specifically to avoid the RW role audit. Because `rw_dependent` (Step 6) is computed from
`logic/problem.md`'s own content — does the problem lean on a named external method, dataset, or
comparator as if it were reused, baselined, bounded, extended, or refuted — rather than from
`related_work.md`'s existence, omitting `related_work.md` does not exempt a dependent problem
layer from the audit; it instead locks in the worst-case `rw_coverage_score` (0.0–0.2) while the
weight for that term stays live.

Another route is resolving a look-alike paper (same topic, wrong specifics) and letting the
LLM rate it as supporting. Step 3's deterministic `match_score` thresholds route
low-confidence matches to `source_identity_uncertain` or `contradictory_identity` before the
support judgment ever runs, so a look-alike cannot be laundered into a "direct" support label
by a generous LLM call.

Finally, a system might avoid citations when unsure. Under penalize-don't-skip, uncited or
underspecified problem claims receive low source-availability and support scores. Missing
evidence is evidence of lower truthfulness.

## Required Inputs

Primary input:

- `logic/problem.md`

Cross-layer input when available:

- `logic/related_work.md`

External inputs:

- DOI/arXiv/title lookup via Semantic Scholar or equivalent bibliographic search.
- Source retrieval via DOI landing page, PubMed/PMC, publisher pages, arXiv, Crossref metadata,
  clinical-trial or registration lookup where the citation is a registration, and any accessible
  full text.

If `logic/related_work.md` is missing, malformed, or thin, the metric still computes and, when
the problem layer is `rw_dependent` (Step 6), applies the cross-layer availability penalty at
full weight. No item is skipped because a source is hard to retrieve, and no item is skipped
because `related_work.md` is absent.

## Generation / Compute Workflow

### Step 1: Parse `logic/problem.md`

Extract:

- Observation blocks `O{N}` with title, `Statement`, `Evidence`, and `Implication`.
- Gap blocks `G{N}` with title, `Statement`, `Caused by`, `Existing attempts`, and `Why they fail`.
- Key Insight fields: `Insight`, `Derived from`, and `Enables`.
- Assumptions `A{N}`.

Create atomic audit units:

- One unit for every Observation `Statement`.
- One unit for every Observation `Implication` that contains a causal, comparative, quantitative,
  or novelty claim.
- One unit for every Gap `Statement`.
- One unit for every Gap `Existing attempts` and `Why they fail`.
- One unit for every Key Insight sentence that cites or depends on `Derived from` IDs.
- One unit for every Assumption that contains a source-backed factual premise.

Each unit stores `unit_id`, `section`, `text`, `local_refs`, `needs_support`, and
`specificity_features` such as numbers, named methods, named datasets, populations, outcomes,
comparators, and modality terms. Additionally tag each unit with `external_dependency_signal`:
true if the unit's text or `Existing attempts`/`Derived from` content names a specific external
method, dataset, cohort, or paper as something reused, compared against, bounded by, extended, or
refuted — this flag feeds Step 6.

### Step 2: Parse `logic/related_work.md`

Extract every full `RW{NN}` block:

- heading/title
- DOI
- Type
- Delta / What changed
- Delta / Why
- Claims affected
- Adopted elements

Also extract brief-tier references if present. Mark:

- `rw_available = 1` if the file exists and has parseable RW or brief references.
- `rw_full_footprint = 1` if it contains both full RW blocks and a brief/additional citation
  footprint tier.
- `rw_thin = 1` if it has fewer than 3 full RW blocks and no brief tier.

For each problem audit unit, link candidate RW entries by author-year, DOI, title terms, cited
dataset/method names, and citation strings in the Evidence field.

### Step 3: Resolve Sources

For every citation or source reference in a unit:

1. If a DOI/arXiv/registration ID is present, query it directly. Exact-ID match is a clean
   resolve; skip to retrieval.
2. Else query Semantic Scholar with:

```text
title/authoryear query:
{citation_string} {paper_title_or_domain_terms_if_available}
Return DOI, title, authors, year, abstract, venue, URL, citationCount, openAccessPdf, externalIds.
```

3. For each returned candidate, compute a deterministic identity `match_score` (this replaces
   an unconstrained "highest-confidence match" judgment call with a fixed rule):

```text
match_score = 0.5 * title_token_jaccard
            + 0.3 * year_agreement
            + 0.2 * author_surname_overlap

title_token_jaccard  = Jaccard similarity of lowercased, stopword-stripped,
                        alphanumeric tokens between the cited title/domain terms
                        and the candidate title.
year_agreement        = 1.0 if candidate year exactly matches the cited year
                        (or the year implied by "recent"/adjacent-year phrasing
                        in the ARA text, if no explicit year is cited);
                        0.5 if within 1 year; else 0.0.
author_surname_overlap = fraction of surnames present in the citation string
                        (e.g., "Karikari et al.") that appear in the
                        candidate's author list.
```

   Select the candidate with the highest `match_score`; ties break toward the candidate with
   higher `citationCount` (more likely the canonical record for a well-known result).

4. Route the selected candidate by fixed thresholds:
   - `match_score >= 0.75`: **clean resolve**. Proceed to retrieval; retrieval status is
     determined purely by text availability (`full_text` / `abstract_only` / `metadata_only`).
   - `0.45 <= match_score < 0.75`: **identity uncertain**. Proceed to retrieval and judging, but
     tag the unit's judgment with `source_identity_uncertain` (added to `drift_types` in Step 4
     regardless of the LLM's own output) and apply retrieval status `metadata_only` at minimum
     even if full text was fetched, since confidence in *which* paper the full text belongs to is
     itself in question.
   - `match_score < 0.45` and no plausible candidate shares any domain term with the citation:
     **unresolved**.
   - `match_score < 0.45` but a candidate does share domain terms with the citation (i.e., a
     real paper on the same broad topic was found but is not a plausible identity match):
     **contradictory_identity** — a wrong paper was resolved and could otherwise be mistaken for
     support.
5. Retrieve full text where accessible; otherwise use abstract and bibliographic metadata.
6. Mark retrieval status as `full_text`, `abstract_only`, `metadata_only`, `unresolved`, or
   `contradictory_identity` per the routing above.

Unresolved or metadata-only sources are not skipped. They contribute low availability and
support scores.

### Step 4: Source-Support Judging

For each audit unit and each candidate source, run a constrained semantic check. The LLM prompt
is:

```text
You are auditing citation truthfulness.

IMPORTANT: a downstream verifier has already confirmed (or will confirm) that the quoted
text for this claim exists at the cited line inside the compiled artifact. That check is
NOT your job and is NOT sufficient here. A quote can be verbatim-accurate and still
misrepresent what its source found, measured, or concluded. Your job is to judge whether the
REAL SOURCE, independent of how it is quoted or paraphrased in the ARA, actually supports the
ARA's claim as used -- same population, same outcome, same direction, same specificity.

ARA claim:
{unit_text}

ARA local evidence field:
{evidence_text}

Source metadata:
Title: {source_title}
Authors/year: {authors_year}
DOI/arXiv/ID: {source_id}

Source excerpts:
{retrieved_abstract_or_relevant_full_text_chunks}

Decide whether the real source supports the ARA claim as used.
Return strict JSON:
{
  "support": "direct" | "partial" | "indirect" | "unsupported" | "contradicted" | "unverifiable",
  "drift_types": ["none" | "wrong_population" | "wrong_outcome" | "wrong_method" | "wrong_direction" | "wrong_magnitude" | "causal_overreach" | "review_as_primary" | "speculation_as_fact" | "role_mismatch" | "too_vague" | "source_identity_uncertain"],
  "quoted_basis": "short quote or paraphrased basis from source, max 25 words",
  "reason": "one sentence",
  "confidence": 0.0
}

Rules:
- Use "direct" only when the source itself states or demonstrates the claim at comparable
  specificity.
- Use "partial" when the source supports the broad point but misses important qualifiers.
- Use "indirect" when it is background/review support for a claim that is not directly shown.
- Use "unsupported" when no provided source content supports the claim.
- Use "contradicted" when the source says the opposite or materially different thing.
- Use "unverifiable" when access is too thin to determine support.
- The quote existing at a cited line inside the ARA does not by itself justify "direct" --
  base your label only on what the source excerpts actually show.
```

The returned JSON is validated against the schema. Invalid JSON is retried once with the same
prompt plus "Return only valid JSON." If still invalid, assign `support = unverifiable`,
`confidence = 0`. If Step 3 tagged the source `source_identity_uncertain`, that drift type is
appended to `drift_types` regardless of what the model returns, and `support` is capped at
`"partial"` even if the model returns `"direct"` (an uncertain identity cannot justify direct
support).

### Step 5: Deterministic Unit Scoring

Map source support to numeric values:

- `direct`: 1.00
- `partial`: 0.70
- `indirect`: 0.45
- `unverifiable`: 0.25
- `unsupported`: 0.10
- `contradicted`: 0.00

Apply modifiers:

- Retrieval status: `full_text` +0.00, `abstract_only` -0.15, `metadata_only` -0.35, `unresolved`
  -0.55, `contradictory_identity` -0.70.
- Specificity penalty: if the ARA unit contains numbers, named cohorts, named methods, or exact
  rankings and the source support is not `direct`, subtract 0.10.
- Missing citation penalty: if `needs_support = true` and no local reference is present, score
  the unit 0.05.
- Vague claim penalty: if a unit has fewer than two specificity features and uses generic
  phrases such as "prior work is limited" or "existing methods fail" without a named target, cap
  the unit at 0.65 even if a broad source partly supports it.
- Contradiction cap: any `contradicted` judgment caps the unit at 0.10.

For units with multiple cited sources, use the maximum support score as the primary support,
but subtract 0.05 for each additional unresolved or unsupported cited source beyond the first,
capped at -0.20. This rewards at least one real supporting source while penalizing citation
padding.

**Why these constants** (added per critique): the retrieval-status ladder is ordered by how much
independent verification work remains after retrieval -- `full_text` requires none, each step
down (`abstract_only` -> `metadata_only` -> `unresolved` -> `contradictory_identity`) removes a
further layer of checkable content, and the step sizes roughly double (0.15 -> 0.35(+0.20) ->
0.55(+0.20) -> 0.70(+0.15)) so that reaching "wrong paper confidently asserted" is treated as
worse than simply "could not find the paper" (0.70 vs 0.55), reflecting that a contradictory
identity actively launders false confidence rather than merely lacking it. The 0.10 specificity
penalty and 0.65 vague-claim cap are sized so that neither can, by itself, move a unit across a
full support tier (each tier gap is >= 0.25); they nudge within a tier rather than substitute for
the entailment judgment. The 0.05-per-extra-bad-source multi-citation penalty, capped at 0.20,
is sized so that citation-stuffing with up to 4 bad extra sources costs less than one dropped
support tier, keeping the primary support judgment dominant while still making padding
strictly non-beneficial. See Step 8 for these constants run through worked examples.

### Step 6: Cross-Layer Role Drift (weight-gated)

First, compute `rw_dependent` deterministically from `logic/problem.md` alone (not from
`related_work.md`'s presence or absence):

```text
rw_dependent = true if at least one problem unit has external_dependency_signal = true
               (Step 1), i.e., at least one Observation/Gap/Key-Insight/Assumption unit
               names a specific external method, dataset, cohort, or paper as something
               this work reuses, compares against, is bounded by, extends, or refutes.
rw_dependent = false otherwise (the problem layer's claims are self-contained empirical/
               background statements that do not lean on a typed external relationship).
```

This flag cannot be dodged by deleting or thinning `related_work.md`: it is read off the
problem layer's own claims, so a genuinely import/baseline/bounds/extends/refutes-dependent
problem stays `rw_dependent = true` even with no `related_work.md` at all, and inherits the
worst-case coverage score below.

When `rw_dependent = true`, for each `RW##` entry linked to a problem unit, audit whether the
real source matches the typed role:

- `imports`: source actually supplies a dataset, method, cohort, software, protocol, or
  external result reused by this paper.
- `baseline`: source is actually a comparator or standard of comparison.
- `bounds`: source actually defines a limitation, boundary condition, or known constraint.
- `extends`: this paper plausibly builds beyond the source's result/method.
- `refutes`: source is actually the target of a contrary finding.

Use the same source-support prompt with `ARA claim` replaced by the RW role and Delta fields.
Score role support with the same mapping. Compute:

- `rw_role_score`: mean role-support score across audited RW entries. If `rw_dependent = true`
  but `related_work.md` is missing/thin (`rw_available = 0` or `rw_thin = 1`), there are no RW
  entries to link, and `rw_role_score = 0.10` (the problem depends on external work whose typed
  role cannot even be checked -- treated as near-unsupported, not skipped).
- `rw_coverage_score`: 1.0 if related work has full RW blocks plus brief footprint; 0.7 if it
  has full RW blocks only; 0.4 if only brief references; 0.2 if missing/thin; 0.0 if absent or
  unparsable.

When `rw_dependent = false`, `rw_role_score` and `rw_coverage_score` are still computed for
transparency/reporting (the audit is never skipped), but Step 7 does not spend scoring weight
on them -- a problem layer that never leans on a typed external relationship should not be
dragged down (or artificially boosted) by an `related_work.md` it never needed.

### Step 7: Final Scoring Function

```python
from statistics import mean

SUPPORT_VALUE = {
    "direct": 1.00,
    "partial": 0.70,
    "indirect": 0.45,
    "unverifiable": 0.25,
    "unsupported": 0.10,
    "contradicted": 0.00,
}

RETRIEVAL_PENALTY = {
    "full_text": 0.00,
    "abstract_only": 0.15,
    "metadata_only": 0.35,
    "unresolved": 0.55,
    "contradictory_identity": 0.70,
}

IDENTITY_UNCERTAIN_SUPPORT_CAP = "partial"  # direct is unreachable if identity is uncertain

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def score_unit(unit):
    if unit["needs_support"] and not unit["local_refs"]:
        return 0.05

    source_scores = []
    unresolved_or_bad = 0
    for judgment in unit["judgments"]:
        support = judgment["support"]
        if judgment.get("identity_uncertain") and support == "direct":
            support = IDENTITY_UNCERTAIN_SUPPORT_CAP

        base = SUPPORT_VALUE.get(support, 0.25)
        base -= RETRIEVAL_PENALTY.get(judgment["retrieval_status"], 0.55)

        if unit["has_high_specificity"] and support != "direct":
            base -= 0.10

        if support in {"unsupported", "unverifiable"}:
            unresolved_or_bad += 1

        if support == "contradicted":
            base = min(base, 0.10)

        source_scores.append(clamp(base))

    if not source_scores:
        return 0.05 if unit["needs_support"] else 0.40

    score = max(source_scores)
    if unresolved_or_bad > 1:
        score -= min(0.20, 0.05 * (unresolved_or_bad - 1))

    if unit["is_vague_generic"]:
        score = min(score, 0.65)

    return clamp(score)

def metric_score(problem_units, rw_role_scores, rw_coverage_score, rw_dependent, parse_ok=True):
    if not parse_ok:
        return 0.05

    obs_gap_units = [u for u in problem_units if u["section"] in {"observation", "gap"}]
    insight_assumption_units = [
        u for u in problem_units if u["section"] in {"key_insight", "assumption"}
    ]

    obs_gap_score = mean([score_unit(u) for u in obs_gap_units]) if obs_gap_units else 0.10
    insight_assumption_score = (
        mean([score_unit(u) for u in insight_assumption_units])
        if insight_assumption_units
        else 0.20
    )

    # Base weights when the problem layer depends on external RW-typed relationships.
    W_OBS_GAP, W_INSIGHT, W_ROLE, W_COVERAGE = 0.55, 0.20, 0.15, 0.10

    if rw_dependent:
        role_score = mean(rw_role_scores) if rw_role_scores else 0.10
        final = (
            W_OBS_GAP * obs_gap_score
            + W_INSIGHT * insight_assumption_score
            + W_ROLE * role_score
            + W_COVERAGE * rw_coverage_score
        )
    else:
        # Redistribute the 0.15 + 0.10 weight to the problem-layer terms,
        # proportional to their existing 0.55:0.20 ratio, instead of
        # spending it on an RW audit the problem never needed.
        freed = W_ROLE + W_COVERAGE
        ratio = W_OBS_GAP / (W_OBS_GAP + W_INSIGHT)
        w_obs_gap = W_OBS_GAP + freed * ratio
        w_insight = W_INSIGHT + freed * (1 - ratio)
        final = w_obs_gap * obs_gap_score + w_insight * insight_assumption_score

    return clamp(final)
```

### Step 8: Worked Example (calibration check)

Three units from a hypothetical ARA, run end-to-end, to make the constants in Step 5
checkable rather than asserted:

**Unit O2-statement** ("p-tau217 shows higher diagnostic accuracy than p-tau181 across three
independent cohorts, AUC 0.94 vs 0.81"; `Evidence: Ashton et al., 2024a`).
- `has_high_specificity = true` (named comparator isoforms, numeric AUCs, cohort count).
- Step 3: DOI resolves exactly -> clean resolve, `full_text` retrieved.
- Step 4 judgment: `support = "partial"` -- the source reports comparable AUCs but across two
  cohorts, not three, and for one of the two outcome definitions used in the ARA text.
- Step 5: `base = SUPPORT_VALUE["partial"] (0.70) - RETRIEVAL_PENALTY["full_text"] (0.00) = 0.70`;
  specificity penalty applies since support != direct: `0.70 - 0.10 = 0.60`.
- **Unit score = 0.60.**

**Unit G2-existing_attempts** ("Prior work is limited"; no named method, cites a general review
by title only, no section reference).
- `specificity_features` count = 0 (no numbers, no named method/dataset) -> `is_vague_generic =
  true`.
- Step 3: review resolves cleanly (title/author/year all match) -> `abstract_only` retrieval
  (no accessible full text).
- Step 4 judgment: `support = "indirect"` (a review can plausibly gesture at limitations but
  doesn't itself demonstrate this gap).
- Step 5: `base = 0.45 - 0.15 = 0.30`. Vague-claim cap (`min(score, 0.65)`) does not bind here
  since 0.30 < 0.65 already -- the cap only matters when an indirect/partial source would
  otherwise push the score above 0.65 despite genuine vagueness.
- **Unit score = 0.30.**

**Unit KeyInsight-derived_from** (Key Insight sentence citing `O5` which itself cites a named
external cohort dataset by an ambiguous short-form name, e.g. "the ADNI-extended cohort").
- Step 3: Semantic Scholar returns a same-topic dataset paper, but `title_token_jaccard = 0.5`,
  `year_agreement = 0.5` (one year off), `author_surname_overlap = 0.3` ->
  `match_score = 0.5*0.5 + 0.3*0.5 + 0.2*0.3 = 0.46` -> routes to **identity uncertain**
  (`0.45 <= 0.46 < 0.75`), retrieval forced to `metadata_only` at minimum.
- Step 4: model returns `support = "direct"`, but Step 4's post-processing caps this to
  `"partial"` because `identity_uncertain = true`; `drift_types` gains
  `source_identity_uncertain`.
- Step 5: `base = SUPPORT_VALUE["partial"] (0.70) - RETRIEVAL_PENALTY["metadata_only"] (0.35) =
  0.35`; this unit is not high-specificity by itself (the numeric/cohort specifics live in O5,
  not in this Key-Insight sentence), so no further penalty.
- **Unit score = 0.35.**

Rolling these into `obs_gap_score` (using O2 and G2 as a 2-unit stand-in) gives `(0.60 + 0.30)/2
= 0.45`; `insight_assumption_score` (using the Key Insight unit as a 1-unit stand-in) gives
`0.35`. If this ARA's problem layer also names, in its Gaps, a specific external
network-meta-analysis method it extends (`external_dependency_signal = true` on that unit), then
`rw_dependent = true` and the full `0.55/0.20/0.15/0.10` weighting applies; if related_work.md
is present with full RW blocks and the linked role audit scores `rw_role_score = 0.70`,
`rw_coverage_score = 0.70`, the final score is
`0.55*0.45 + 0.20*0.35 + 0.15*0.70 + 0.10*0.70 = 0.2475 + 0.07 + 0.105 + 0.07 = 0.4925`,
correctly landing in the "broad plausibility but notable source drift" band described in
Interpretation, which matches the mix of one partial-but-specific claim, one vague indirect
claim, and one identity-uncertain derivation actually present in the example.

## Interpretation

Scores near 1.0 mean the problem layer's cited sources directly support the ARA's empirical
setup, gap diagnosis, and motivating logic, with cross-layer related-work roles (when the
problem depends on them) matching the real source record. Scores around 0.5 indicate broad
plausibility but notable source drift, abstract-only support, vague claims, identity-uncertain
resolutions, or weak related-work role agreement. Scores below 0.3 indicate that the ARA is
citing sources unreliably, using unavailable, unresolved, or misidentified references, or
making problem/gap claims that the real sources do not support.

## Why It Is Hard To Goodhart

This metric is hard to Goodhart because it evaluates source-use semantics, not citation count,
quote count, or formatting. Adding more citations creates more audit surface and can lower the
score if they are unsupported. Making claims vague triggers specificity caps. Omitting
citations triggers missing-support penalties. Copying local ARA quotes is insufficient because
the audit resolves and checks the real external source, and the judging prompt explicitly tells
the model that quote-existence is not evidence of support. Deleting or thinning
`related_work.md` to dodge the cross-layer role audit does not work because `rw_dependent` is
read off the problem layer's own claims, not off `related_work.md`'s presence -- a dependent
problem is scored on the worst-case coverage band regardless. Resolving a plausible-looking but
wrong paper does not work either, because the deterministic `match_score` threshold routes it to
`source_identity_uncertain` or `contradictory_identity` before the LLM judgment can rate it as
supporting.

The metric also composes well with the rest of the suite. It does not duplicate local verifier
checks for line quotes or schema validity; instead, it asks whether the ARA's scientific
narrative remains faithful to the literature it invokes. It complements problem-quality,
related-work-comprehensiveness, and claim-grounding metrics by measuring truthfulness of the
bridge between them.

## Assumptions

- If only `logic/problem.md` is available, compute the problem-unit portions in full; compute
  `rw_dependent` from problem.md content regardless, and if `rw_dependent = true`, apply the
  missing/thin `rw_coverage_score` (0.2) and `rw_role_score` (0.10) at full weight rather than
  dropping them.
- If full text cannot be retrieved, use abstract and metadata, but penalize retrieval status.
- If a citation string cannot be resolved confidently (`match_score < 0.75`), treat it as
  identity-uncertain or unresolved per the Step 3 thresholds rather than excluding it from the
  denominator, and never let an uncertain identity justify a `direct` support label.
