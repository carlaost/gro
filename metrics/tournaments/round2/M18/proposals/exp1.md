# M18 Expansion: Claim Drift / Reference Truthfulness

## Metric intent

This metric asks whether the references used in `logic/problem.md` and, where needed, cross-checked through `logic/related_work.md`, actually support the statements they are being cited for. It is not enough that the ARA quotes or names a source consistently inside its own text. The question is whether the real external source says what the ARA claims it says, at the level of empirical fact, methodological limitation, comparator result, dataset reuse, or prior-work gap.

The metric rewards problem statements whose Observations, Gaps, Key Insight provenance, and Assumptions are anchored to cited sources without inflating, reversing, over-generalizing, or laundering claims through vague citation strings. It penalizes missing evidence fields, abstract-only evidence, citations that cannot be resolved, and sources that are resolved but do not contain the cited claim. The score never skips unavailable inputs: if a field is absent, thin, non-specific, or externally unverifiable, that absence is treated as evidence of lower truthfulness.

## Why this signals good science

Good science depends on preserving the boundary between what prior work established, what remains uncertain, and what the current paper contributes. The problem layer is especially sensitive because it frames the whole argument: a single overstated Observation or invented Gap can make a routine method look necessary, novel, or well-motivated. Claim drift against references is therefore a direct measure of scientific reliability, not just writing quality.

This metric should reward:

- Source-faithful empirical statements with numbers, populations, assays, endpoints, and limitations matching the cited paper or cited section.
- Evidence strings that identify real sources precisely enough to verify them, not just broad citation clusters.
- Gaps whose "Existing attempts" and "Why they fail" are grounded in actual limitations of the cited prior work.
- Key Insight provenance that accurately traces which observations or gaps motivate the leap, without pretending that cited sources already made the paper's contribution.
- Related-work entries whose DOI/arXiv identifiers, dependency type, adopted elements, and technical deltas are consistent with the external source.

It must not reward:

- Correct-looking citation formatting if the cited paper supports only a weaker or different statement.
- Citation padding, where one correct source is buried among several irrelevant or contradictory sources.
- Abstract-level paraphrase when the ARA claims section-level or introduction-level support.
- "Consensus" or "known" language that exceeds the cited evidence.
- Generic gap language such as "prior work is limited" when the real prior work has specific, different limitations.

## Failure modes and gaming routes

The main failure mode is citation drift: the ARA cites a real paper, but the paper supports a neighboring claim rather than the exact claim made. Examples include changing a biomarker from association to prediction, changing diagnostic performance from one population to another, treating a review's speculation as empirical evidence, or converting a method limitation into a field-wide gap.

Gaming routes include citing many papers for each Observation, using only high-level review articles, writing claims so vaguely that they are hard to falsify, and omitting DOI-level identifiers from related work. The workflow below counters these by sampling claim-citation pairs, applying per-citation support checks, penalizing unresolved or over-broad citation bundles, and giving only partial credit for sources that support a weaker version of the claim.

The metric is net-new relative to a verifier that checks consistency inside the ARA because it reaches out to the real cited source. It evaluates whether the source itself supports the ARA's use of it, not merely whether the ARA cites the same line consistently across its own artifacts.

## Inputs

Required artifact:

- `logic/problem.md`

Cross-layer artifact:

- `logic/related_work.md`

Required parsed fields from `problem.md`:

- Observation headings `O{N}` and titles.
- Observation `Statement`, `Evidence`, and `Implication`.
- Gap headings `G{N}` and titles.
- Gap `Statement`, `Caused by`, `Existing attempts`, and `Why they fail`.
- Key Insight `Insight`, `Derived from`, and `Enables`.
- Assumptions `A{N}`.

Required parsed fields from `related_work.md`:

- Full `RW{NN}` entries with heading, DOI or arXiv ID, Type, Delta / What changed, Delta / Why, Claims affected, and Adopted elements.
- Brief/background citation tier entries, if present.

Choice on ambiguity: because the metric must penalize rather than skip, a missing `related_work.md`, missing brief tier, missing DOI/arXiv identifier, or unresolvable citation receives deterministic penalties rather than causing the pair to be excluded.

## Generation / compute workflow

### Step 1: Parse the artifacts

Parse `problem.md` into structured records:

```python
ProblemRecord = {
    "observations": [
        {"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str}
    ],
    "gaps": [
        {"id": "G1", "title": str, "statement": str, "caused_by": [str],
         "existing_attempts": str, "why_they_fail": str}
    ],
    "key_insight": {"insight": str, "derived_from": [str], "enables": str},
    "assumptions": [{"id": "A1", "text": str}]
}
```

Parse `related_work.md` into:

```python
RelatedWorkRecord = {
    "full": [
        {"id": "RW01", "label": str, "doi": str, "type": str,
         "what_changed": str, "why": str, "claims_affected": [str], "adopted_elements": str}
    ],
    "brief": [{"label": str, "identifier": str | None, "role": str}]
}
```

If either parse fails, emit empty fields for the failed sections and let downstream penalties apply.

### Step 2: Generate auditable claim-citation units

Create claim units from:

- Each Observation `Statement`.
- Each Observation `Implication` when it makes a factual or causal claim.
- Each Gap `Statement`.
- Each Gap `Existing attempts` plus `Why they fail`.
- Key Insight `Derived from` links, by checking whether the cited O/G records actually support the insight.
- Each related-work full entry's `What changed`, `Why`, and `Adopted elements`.
- Each brief-tier related-work role.

For every unit, extract cited references from the local `Evidence` string or from the corresponding `related_work.md` entry. If an Observation cites multiple papers, split it into one unit per cited source, with the same claim text and a specific cited source label. If a citation cannot be mapped to a DOI/arXiv/PMID/title through `related_work.md` or source lookup, keep the unit with `resolution_status="unresolved"`.

Minimum audit set:

- All Observation statements, up to 8 source pairs.
- All Gap statements and failure explanations, up to 6 source pairs.
- All Key Insight provenance links.
- All related-work full entries, up to 8 entries.
- If there are more than these caps, choose the units with the most numeric, causal, comparative, or novelty-bearing language first. This is deterministic by sorting units by: has_number, has_comparator, has_causal_verb, claim_length, artifact_order.

### Step 3: Resolve real sources

For each citation unit, call external tools in this order:

1. `[sem]` Semantic Scholar lookup by DOI/arXiv/PMID if available; otherwise by exact title/author-year label.
2. External source retrieval for abstract and available full text/open PDF when Semantic Scholar returns a paper.
3. Domain-specific lookup where applicable:
   - ClinicalTrials.gov for trial registrations or NCT identifiers.
   - PubMed/Europe PMC for biomedical abstracts when DOI lookup is incomplete.
   - arXiv for arXiv identifiers.

Semantic Scholar query:

```text
Find the paper matching this citation from an ARA artifact.
Citation label: {label}
Identifier if present: {doi_or_arxiv_or_pmid}
Return: canonical title, authors, year, DOI/arXiv/PMID, abstract, venue, and URL.
```

Full-text retrieval query:

```text
Retrieve the abstract and, if legally available, full text sections most relevant to this claim.
Paper: {canonical_title}
Identifier: {identifier}
Claim to verify: {claim_text}
Return concise passages or section summaries that bear on the claim, with section names.
```

If no external source is resolved, set `source_resolution_score=0` for that unit and `support_score=0`. Do not drop the unit.

### Step 4: Semantic support grading

Use an LLM or NLI model only after retrieving real-source text. The model must grade against the external source text, not against the ARA alone.

Prompt:

```text
You are grading whether an ARA claim is supported by a real cited source.

ARA claim:
{claim_text}

Cited source:
{canonical_citation}

Retrieved source evidence:
{retrieved_passages_or_section_summaries}

Grade support using exactly one label:
- exact: the source directly supports the claim with matching scope, population/system, method, direction, and strength.
- partial: the source supports a weaker, narrower, adjacent, or background version of the claim.
- contradicted: the source says the opposite or materially conflicts with the claim.
- absent: the retrieved source does not contain evidence for the claim.
- unverifiable: the source could not be resolved or the retrieved material is too thin to check.

Also return boolean flags:
scope_drift, strength_drift, entity_drift, numeric_drift, causal_drift, citation_padding.

Return JSON only:
{
  "label": "...",
  "rationale": "one sentence",
  "flags": {
    "scope_drift": false,
    "strength_drift": false,
    "entity_drift": false,
    "numeric_drift": false,
    "causal_drift": false,
    "citation_padding": false
  }
}
```

Convert labels to deterministic support points:

- `exact`: 1.00
- `partial`: 0.55
- `absent`: 0.15
- `contradicted`: 0.00
- `unverifiable`: 0.00

Apply flag penalties to the unit after label points:

- `numeric_drift`: -0.20
- `causal_drift`: -0.20
- `strength_drift`: -0.15
- `scope_drift`: -0.15
- `entity_drift`: -0.15
- `citation_padding`: -0.10

Clamp each unit score to `[0, 1]`.

### Step 5: Structural availability penalties

Compute artifact-availability sub-scores:

- `problem_completeness`: fraction of required `problem.md` fields present and non-thin. A field is thin if it is empty, says only "Abstract", or uses generic filler such as "prior work is limited" without a named method, dataset, comparator, result, or mechanism.
- `citation_specificity`: fraction of claim units with a resolvable citation label or identifier.
- `related_work_crosswalk`: fraction of non-background citations in `problem.md` that can be matched to a full or brief `related_work.md` entry.
- `related_work_depth`: score 1.0 if full RW blocks and a brief/background tier are both present; 0.6 if full blocks are present but no brief tier; 0.3 if only 1-3 sparse RW blocks exist; 0.0 if absent or unparsable.

These are penalties, not filters.

### Step 6: Final scoring function

```python
from statistics import mean

LABEL_POINTS = {
    "exact": 1.00,
    "partial": 0.55,
    "absent": 0.15,
    "contradicted": 0.00,
    "unverifiable": 0.00,
}

FLAG_PENALTIES = {
    "numeric_drift": 0.20,
    "causal_drift": 0.20,
    "strength_drift": 0.15,
    "scope_drift": 0.15,
    "entity_drift": 0.15,
    "citation_padding": 0.10,
}

def clamp01(x):
    return max(0.0, min(1.0, float(x)))

def unit_truth_score(unit_grade):
    base = LABEL_POINTS.get(unit_grade.get("label"), 0.0)
    flags = unit_grade.get("flags", {}) or {}
    penalty = sum(
        amount for flag, amount in FLAG_PENALTIES.items()
        if bool(flags.get(flag, False))
    )
    return clamp01(base - penalty)

def weighted_mean(items):
    total_weight = sum(w for _, w in items)
    if total_weight <= 0:
        return 0.0
    return sum(score * weight for score, weight in items) / total_weight

def claim_drift_reference_truthfulness_score(
    unit_grades,
    problem_completeness,
    citation_specificity,
    related_work_crosswalk,
    related_work_depth,
):
    """
    unit_grades: list of dicts returned by the support-grading step.
      Each dict may include unit_type in:
      observation, gap, key_insight, related_work_full, related_work_brief.
    Availability inputs are floats in [0, 1].
    Missing or empty values are scored as 0, never skipped.
    """
    type_weights = {
        "observation": 1.25,
        "gap": 1.25,
        "key_insight": 1.00,
        "related_work_full": 1.00,
        "related_work_brief": 0.60,
    }
    if not unit_grades:
        truth_core = 0.0
    else:
        scored = []
        for grade in unit_grades:
            unit_type = grade.get("unit_type", "observation")
            scored.append((unit_truth_score(grade), type_weights.get(unit_type, 1.0)))
        truth_core = weighted_mean(scored)

    availability = weighted_mean([
        (clamp01(problem_completeness), 0.35),
        (clamp01(citation_specificity), 0.30),
        (clamp01(related_work_crosswalk), 0.20),
        (clamp01(related_work_depth), 0.15),
    ])

    # Multiplicative availability keeps thin/unverifiable artifacts from receiving
    # high scores merely by making a few vague claims that are hard to falsify.
    return clamp01(0.80 * truth_core + 0.20 * truth_core * availability)
```

Recommended score interpretation:

- `0.85-1.00`: cited sources directly support nearly all problem and related-work claims.
- `0.65-0.84`: mostly faithful, with some partial support or mild scope/strength drift.
- `0.40-0.64`: substantial citation drift, vague evidence, or unresolved citation mapping.
- `<0.40`: unreliable problem framing; many claims are unsupported, contradicted, or externally unverifiable.

## Why it is hard to Goodhart

The metric is hard to Goodhart because it does not reward surface citation density. Every added citation creates more audit targets, and unresolved or irrelevant citations lower the score. Vague claims receive less credit because the workflow prioritizes numeric, comparative, causal, and novelty-bearing statements and treats abstract-only evidence as thin. A compiler can improve only by making claims more source-faithful, adding precise identifiers, and preserving the actual dependency graph.

The metric also resists laundering through `related_work.md`: DOI-level entries are checked against real sources, and their technical deltas must match the external paper. A polished RW block with a false "adopted elements" claim is penalized just like a false Observation.

## Composition with the suite

This metric composes as an external truthfulness layer for the problem and related-work artifacts. It complements internal consistency checks, dependency-graph comprehensiveness metrics, novelty/gap metrics, and verifier-style quote checks. Those metrics can say whether the ARA is structured, complete, and internally coherent; M18 asks whether the structure is anchored in the real scientific record. Its penalties should therefore be treated as high-signal reliability evidence when downstream metrics depend on Observations, Gaps, or prior-work claims.
