# M18 Expansion: Claim Drift / Reference Truthfulness

## Metric Intent

This metric asks whether the ARA's problem-layer citations still mean what the real cited sources mean. It is not enough for `logic/problem.md` to contain plausible observations, local citation strings, or even source-like phrasing. A good ARA should preserve the actual epistemic role of cited work: the cited papers, registrations, datasets, or methods should support the specific empirical facts, gaps, existing-attempts summaries, and assumptions they are invoked to support.

The metric rewards a problem statement whose Observations, Gaps, Key Insight derivation, and Assumptions are grounded in sources that actually say the attributed thing, at the right level of specificity. It penalizes citation drift: overclaiming, reversing findings, laundering speculative background into established fact, citing a paper for a different population/outcome/method, using a review as if it directly measured a result, citing only an abstract when the claim needs full-text support, or assigning an imported dataset/method role in `logic/related_work.md` that the source does not actually have.

The metric is deliberately external-source-facing. The ARA verifier can check whether a quote exists at a cited line inside the compiled artifact; this metric checks the harder question: whether the real source behind the citation supports the ARA's use of it.

## What It Should Reward

- Problem Observations with precise, source-faithful empirical statements, including correct populations, interventions/exposures, outcome definitions, effect directions, measurement modality, and numerical values where present.
- Evidence fields that name real citations or section-level references with enough specificity to retrieve and audit the source.
- Gaps whose "Existing attempts" and "Why they fail" accurately summarize prior work rather than inventing limitations for narrative convenience.
- Key Insight derivations that follow from the stated Observations/Gaps and do not cite sources for a leap they do not motivate.
- Assumptions that are honestly identified as assumptions, not disguised as settled results from a citation.
- Cross-layer agreement with `logic/related_work.md`: sources described as imports, baselines, bounds, extensions, or refutations should have the same role when checked against the real source.
- Explicit uncertainty when source access is partial; partial access is still scored downward, not skipped.

## What It Must Not Reward

- Citation-shaped decoration: author-year strings appended to claims without a retrievable bibliographic target.
- Verbatim local quoting that is copied from another ARA artifact but not confirmed against the external source.
- Generic background citations used to support specific quantitative or causal claims.
- "Abstract-only" support for claims that require methods/results details.
- Correct paper identity with incorrect role assignment, e.g. citing a methods paper as if it reported a dataset result.
- Drift hidden by paraphrase, such as changing "associated with" to "predicts", "in mice" to "in patients", "may improve" to "improves", or "prior work is limited" to a specific nonexistent failure mode.

## Failure Modes And Gaming Routes

The easiest gaming route is to make the problem layer vague enough that almost any source could appear to support it. This metric counters that by extracting atomic claim-source pairs and penalizing low-specificity statements. Another route is to cite review papers for broad facts; that can be acceptable for background, but the scoring distinguishes direct support from indirect support and penalizes direct empirical claims that rely only on a review when primary evidence is named or required.

A compiler might also inflate `related_work.md` with many plausible RW blocks. The cross-layer part checks whether each cited source's typed role matches the real source. More citations do not help if they are thin, unretrievable, or role-drifted.

Finally, a system might avoid citations when unsure. Under penalize-don't-skip, uncited or underspecified problem claims receive low source-availability and support scores. Missing evidence is evidence of lower truthfulness.

## Required Inputs

Primary input:

- `logic/problem.md`

Cross-layer input when available:

- `logic/related_work.md`

External inputs:

- DOI/arXiv/title lookup via Semantic Scholar or equivalent bibliographic search.
- Source retrieval via DOI landing page, PubMed/PMC, publisher pages, arXiv, Crossref metadata, clinical-trial or registration lookup where the citation is a registration, and any accessible full text.

If `logic/related_work.md` is missing, malformed, or thin, the metric still computes and applies the cross-layer availability penalty. No item is skipped because a source is hard to retrieve.

## Generation / Compute Workflow

### Step 1: Parse `logic/problem.md`

Extract:

- Observation blocks `O{N}` with title, `Statement`, `Evidence`, and `Implication`.
- Gap blocks `G{N}` with title, `Statement`, `Caused by`, `Existing attempts`, and `Why they fail`.
- Key Insight fields: `Insight`, `Derived from`, and `Enables`.
- Assumptions `A{N}`.

Create atomic audit units:

- One unit for every Observation `Statement`.
- One unit for every Observation `Implication` that contains a causal, comparative, quantitative, or novelty claim.
- One unit for every Gap `Statement`.
- One unit for every Gap `Existing attempts` and `Why they fail`.
- One unit for every Key Insight sentence that cites or depends on `Derived from` IDs.
- One unit for every Assumption that contains a source-backed factual premise.

Each unit stores `unit_id`, `section`, `text`, `local_refs`, `needs_support`, and `specificity_features` such as numbers, named methods, named datasets, populations, outcomes, comparators, and modality terms.

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
- `rw_full_footprint = 1` if it contains both full RW blocks and a brief/additional citation footprint tier.
- `rw_thin = 1` if it has fewer than 3 full RW blocks and no brief tier.

For each problem audit unit, link candidate RW entries by author-year, DOI, title terms, cited dataset/method names, and citation strings in the Evidence field.

### Step 3: Resolve Sources

For every citation or source reference in a unit:

1. If DOI/arXiv/registration ID is present, query it directly.
2. Else query Semantic Scholar with:

```text
title/authoryear query:
{citation_string} {paper_title_or_domain_terms_if_available}
Return DOI, title, authors, year, abstract, venue, URL, citationCount, openAccessPdf, externalIds.
```

3. If multiple candidates are returned, choose the highest-confidence match by exact DOI, then exact title, then author-year plus domain-term overlap.
4. Retrieve full text where accessible; otherwise use abstract and bibliographic metadata.
5. Mark retrieval status as `full_text`, `abstract_only`, `metadata_only`, `unresolved`, or `contradictory_identity`.

Unresolved or metadata-only sources are not skipped. They contribute low availability and support scores.

### Step 4: Source-Support Judging

For each audit unit and each candidate source, run a constrained semantic check. The LLM prompt is:

```text
You are auditing citation truthfulness.

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
- Use "direct" only when the source itself states or demonstrates the claim at comparable specificity.
- Use "partial" when the source supports the broad point but misses important qualifiers.
- Use "indirect" when it is background/review support for a claim that is not directly shown.
- Use "unsupported" when no provided source content supports the claim.
- Use "contradicted" when the source says the opposite or materially different thing.
- Use "unverifiable" when access is too thin to determine support.
```

The returned JSON is validated against the schema. Invalid JSON is retried once with the same prompt plus "Return only valid JSON." If still invalid, assign `support = unverifiable`, `confidence = 0`.

### Step 5: Deterministic Unit Scoring

Map source support to numeric values:

- `direct`: 1.00
- `partial`: 0.70
- `indirect`: 0.45
- `unverifiable`: 0.25
- `unsupported`: 0.10
- `contradicted`: 0.00

Apply modifiers:

- Retrieval status: `full_text` +0.00, `abstract_only` -0.15, `metadata_only` -0.35, `unresolved` -0.55, `contradictory_identity` -0.70.
- Specificity penalty: if the ARA unit contains numbers, named cohorts, named methods, or exact rankings and the source support is not `direct`, subtract 0.10.
- Missing citation penalty: if `needs_support = true` and no local reference is present, score the unit 0.05.
- Vague claim penalty: if a unit has fewer than two specificity features and uses generic phrases such as "prior work is limited" or "existing methods fail" without a named target, cap the unit at 0.65 even if a broad source partly supports it.
- Contradiction cap: any `contradicted` judgment caps the unit at 0.10.

For units with multiple cited sources, use the maximum support score as the primary support, but subtract 0.05 for each additional unresolved or unsupported cited source beyond the first, capped at -0.20. This rewards at least one real supporting source while penalizing citation padding.

### Step 6: Cross-Layer Role Drift

For each `RW##` entry linked to a problem unit, audit whether the real source matches the typed role:

- `imports`: source actually supplies a dataset, method, cohort, software, protocol, or external result reused by this paper.
- `baseline`: source is actually a comparator or standard of comparison.
- `bounds`: source actually defines a limitation, boundary condition, or known constraint.
- `extends`: this paper plausibly builds beyond the source's result/method.
- `refutes`: source is actually the target of a contrary finding.

Use the same source-support prompt with `ARA claim` replaced by the RW role and Delta fields. Score role support with the same mapping. Compute:

- `rw_role_score`: mean role-support score across audited RW entries.
- `rw_coverage_score`: 1.0 if related work has full RW blocks plus brief footprint; 0.7 if it has full RW blocks only; 0.4 if only brief references; 0.2 if missing/thin; 0.0 if absent or unparsable.

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

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def score_unit(unit):
    if unit["needs_support"] and not unit["local_refs"]:
        return 0.05

    source_scores = []
    unresolved_or_bad = 0
    for judgment in unit["judgments"]:
        base = SUPPORT_VALUE.get(judgment["support"], 0.25)
        base -= RETRIEVAL_PENALTY.get(judgment["retrieval_status"], 0.55)

        if unit["has_high_specificity"] and judgment["support"] != "direct":
            base -= 0.10

        if judgment["support"] in {"unsupported", "unverifiable"}:
            unresolved_or_bad += 1

        if judgment["support"] == "contradicted":
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

def metric_score(problem_units, rw_role_scores, rw_coverage_score, parse_ok=True):
    if not parse_ok:
        return 0.05

    obs_gap_units = [u for u in problem_units if u["section"] in {"observation", "gap"}]
    insight_assumption_units = [u for u in problem_units if u["section"] in {"key_insight", "assumption"}]

    obs_gap_score = mean([score_unit(u) for u in obs_gap_units]) if obs_gap_units else 0.10
    insight_assumption_score = mean([score_unit(u) for u in insight_assumption_units]) if insight_assumption_units else 0.20
    role_score = mean(rw_role_scores) if rw_role_scores else 0.20

    final = (
        0.55 * obs_gap_score +
        0.20 * insight_assumption_score +
        0.15 * role_score +
        0.10 * rw_coverage_score
    )
    return clamp(final)
```

## Interpretation

Scores near 1.0 mean the problem layer's cited sources directly support the ARA's empirical setup, gap diagnosis, and motivating logic, with cross-layer related-work roles matching the real source record. Scores around 0.5 indicate broad plausibility but notable source drift, abstract-only support, vague claims, or weak related-work role agreement. Scores below 0.3 indicate that the ARA is citing sources unreliably, using unavailable or unresolved references, or making problem/gap claims that the real sources do not support.

## Why It Is Hard To Goodhart

This metric is hard to Goodhart because it evaluates source-use semantics, not citation count, quote count, or formatting. Adding more citations creates more audit surface and can lower the score if they are unsupported. Making claims vague triggers specificity caps. Omitting citations triggers missing-support penalties. Copying local ARA quotes is insufficient because the audit resolves and checks the real external source.

The metric also composes well with the rest of the suite. It does not duplicate local verifier checks for line quotes or schema validity; instead, it asks whether the ARA's scientific narrative remains faithful to the literature it invokes. It complements problem-quality, related-work-comprehensiveness, and claim-grounding metrics by measuring truthfulness of the bridge between them.

## Assumptions

- If only `logic/problem.md` is available, compute the problem-unit portions and assign the related-work components their missing/thin penalties.
- If full text cannot be retrieved, use abstract and metadata, but penalize retrieval status.
- If a citation string cannot be resolved confidently, treat it as unresolved rather than excluding it from the denominator.
