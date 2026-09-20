# M18 Expansion: Claim Drift / Reference Truthfulness

## Metric intent

This metric asks whether the citations used in `logic/problem.md` actually support the propositions they are attached to when checked against the real cited sources, not just against the compiler's local prose or a nearby quoted line. It targets the problem layer because Observations, Gaps, and the Key Insight are the ARA's causal story for why the work matters. If that layer cites sources for stronger, narrower, broader, or different claims than the sources actually make, downstream agents inherit a distorted problem formulation even when the rest of the ARA is internally coherent.

The metric should reward citation use that is faithful at the level of claim scope, population, intervention/method, outcome, direction, magnitude, uncertainty, and evidential status. A source that says "associated with" must not be cited as proving causation; a study in a narrow cohort must not be used as evidence for a general field-wide fact; a speculative review sentence must not be cited as if it were a primary result; and a paper showing one biomarker performs well must not be used to claim it is optimal across all stages. The metric should also reward citations that are sufficiently locatable: DOI/PMID/arXiv/title-year-author signals, section names, and enough surrounding wording to retrieve the true source.

The metric must not reward merely having many citations. Citation density can hide drift. It also must not reward citations that are faithful only to an intermediate ARA artifact, because the ranked-ledger point of M18 is net-new external reach: the check goes against the real source wherever possible. Missing, ambiguous, paywalled, abstract-only, or non-resolvable sources are not skipped. They are scored as weaker evidence with explicit penalties because availability and verifiability are part of source truthfulness.

## What counts as drift

Drift is any material mismatch between an ARA problem-layer assertion and what the cited real source supports. Major drift includes citing a source for an opposite conclusion, a result absent from the source, a fabricated number, a wrong study design, or a conclusion generalized far beyond the source's population or endpoint. Moderate drift includes overclaiming certainty, turning a secondary citation into primary evidence, omitting an important qualifier, using a method-comparison paper for a biological mechanism, or citing a source that only partially supports a multi-part sentence. Minor drift includes imprecise but directionally correct paraphrase, missing sample/context details that do not change the inference, or citation bundles where some but not all sources support the exact sentence.

For `logic/problem.md`, the load-bearing units are:

- Observation `Statement` plus its `Evidence`.
- Observation `Implication` when it makes an inference from the evidence.
- Gap `Statement`, `Existing attempts`, and `Why they fail` when they cite or depend on prior work.
- Key Insight `Derived from` chain only insofar as the cited observations/gaps truthfully establish the need it claims to resolve.

Assumptions are checked only if they contain source citations or externally factual claims. Otherwise they contribute to a small availability/context component, not the source-truthfulness denominator.

## Failure modes and gaming routes

The easiest gaming route is to write vague Observations with broad review citations that are hard to falsify. This should score lower on specificity and source-locatability, even if no direct contradiction is found. Another route is citation stuffing: attach eight papers to a sentence where only one supports it. The workflow samples and scores citation-claim pairs, then penalizes unsupported citations inside bundles rather than giving the bundle full credit. A third route is quote laundering: include a true phrase from the source while using it to support a broader claim the source does not support. The scoring prompt explicitly separates "quoted text exists" from "the cited source supports this assertion."

This metric overlaps slightly with generic citation verification, but is tighter and deeper: it evaluates source-to-claim semantics for the problem formulation, not just whether references are real, lines contain similar words, or the ARA quotes a source passage. It composes well with internal-consistency metrics because an internally consistent ARA can still be externally false; conversely, this metric does not judge whether the problem story is complete or elegant except through the truthfulness and verifiability of its source grounding.

## Inputs

Primary input:

- `logic/problem.md` parsed according to the §4 shape: Observations, Gaps, Key Insight, and Assumptions.

Optional cross-layer input used only for source resolution and context:

- `logic/related_work.md` from §6 if available through the ARA, because M18 is cross §6. It may provide a typed reference graph and bibliographic hints. If absent or thin, source resolution receives the appropriate penalty.

External inputs:

- Semantic Scholar lookup for cited paper metadata and abstracts.
- DOI/arXiv/PubMed/open web lookup for full text or landing pages when identifiers are present.
- Optional full-text retrieval where legally accessible.
- LLM semantic judgment over bounded snippets and abstracts/full text.

All unavailable fields and failed lookups are retained as scored records. No unresolved citation is dropped from the denominator.

## Generation / compute workflow

### 1. Parse problem artifact

Parse `logic/problem.md` into structured records:

```python
ProblemRecord = {
    "unit_id": "O1.Statement",
    "unit_type": "observation_statement",
    "text": "...",
    "evidence_text": "...",
    "local_context": "heading/title plus adjacent fields",
    "declared_refs": ["Karikari et al., 2020", "Mila-Aloma et al., 2022"],
}
```

Citation extraction accepts parenthetical citations, DOI/arXiv/PMID strings, named references, section refs such as `§1 Introduction`, and mixed evidence strings. If an Observation has `Evidence: Abstract` or no parseable external source, create a record with `declared_refs=[]` and score it through the missing/thin pathway.

### 2. Normalize atomic claims

Split each load-bearing unit into one to three atomic assertions. Preserve numeric values, comparison terms, populations, interventions/methods, outcomes, and modality words such as "causes", "predicts", "correlates", "best", "first", "significant", or "early". Use deterministic sentence splitting first; use an LLM only when a sentence contains multiple semicolon/comma-joined factual assertions.

LLM prompt for atomization:

```text
You are extracting checkable factual assertions from an ARA problem-layer sentence.
Return JSON only: {"claims":[{"claim":"...", "must_be_supported_by_citation":true|false, "key_terms":["..."]}]}.
Keep numbers, populations, outcomes, comparisons, and certainty words exactly.
Do not add facts not present in the input.

Sentence: {unit_text}
Evidence field: {evidence_text}
Context: {local_context}
```

If atomization fails, use the original sentence as one claim and apply a 0.05 process penalty to that unit.

### 3. Resolve cited sources

For each declared citation, query:

```text
Semantic Scholar: title/author/year query = "{citation_string}" with context terms "{key_terms}"
Fallback web/DOI/PubMed/arXiv lookup: "{citation_string}" "{top key terms}".
```

Resolution score per citation:

- `1.0`: exact title/author/year or persistent identifier match.
- `0.75`: high-confidence title/author/year match with minor ambiguity.
- `0.45`: plausible source family but ambiguous among multiple papers.
- `0.20`: only a secondary landing page, abstract stub, or citation string with no confident source.
- `0.0`: no resolvable external source.

Unresolved sources remain in the denominator and receive support score `0.0` unless the claim has other resolved citations that support it. The unresolved citation still lowers the bundle score.

### 4. Retrieve source evidence

For each resolved source, collect evidence snippets in this order:

1. Full-text passages matching key terms and numeric values.
2. Abstract passages from Semantic Scholar/PubMed/arXiv/DOI page.
3. Title and metadata only.

Retrieval quality:

- `1.0`: full text or source passage sufficient to verify the claim.
- `0.75`: abstract sufficient for the specific claim.
- `0.45`: abstract available but too thin for full specificity.
- `0.20`: title/metadata only.
- `0.0`: no content retrieved.

Paywalled or inaccessible full text is not skipped; it receives the best available retrieval score, usually abstract-only.

### 5. Semantic support judgment

For each atomic claim and each cited source, ask an LLM to judge support using only retrieved source text. The model must return JSON with a label and rationale.

Prompt:

```text
You are checking whether a real cited source supports an ARA problem-layer claim.
Use ONLY the provided source text. Do not use outside knowledge.

ARA claim:
{atomic_claim}

Citation string:
{citation_string}

Source metadata:
{metadata_json}

Retrieved source text:
{snippets}

Return JSON only:
{
  "support_label": "direct_support" | "partial_support" | "weak_context" | "unsupported" | "contradicted" | "unverifiable",
  "scope_match": 0.0-1.0,
  "polarity_match": 0.0-1.0,
  "specificity_match": 0.0-1.0,
  "number_match": 0.0-1.0 or null,
  "evidence_role": "primary_result" | "review_background" | "method_source" | "editorial_or_speculative" | "unknown",
  "rationale": "one concise sentence"
}

Definitions:
- direct_support: source directly establishes the claim at comparable scope.
- partial_support: source supports direction/topic but misses material scope, population, endpoint, comparison, or certainty.
- weak_context: source is relevant background but does not establish the assertion.
- unsupported: source text does not support the assertion.
- contradicted: source says the opposite or materially conflicts.
- unverifiable: retrieved text is too thin to decide.
```

Map labels to base support:

- `direct_support`: `1.0`
- `partial_support`: `0.65`
- `weak_context`: `0.35`
- `unverifiable`: `0.20`
- `unsupported`: `0.0`
- `contradicted`: `-0.35`

Then multiply by `(0.35*scope_match + 0.30*polarity_match + 0.20*specificity_match + 0.15*number_match_or_1)`. Cap negative scores at `-0.35`.

### 6. Bundle scoring

For a claim with multiple cited sources, score both best support and citation hygiene:

```python
claim_support = max(source_support_scores) if source_support_scores else 0.0
mean_citation_truth = mean(max(0.0, s) for s in source_support_scores) if source_support_scores else 0.0
unsupported_fraction = count(s <= 0.05 for s in source_support_scores) / max(1, len(source_support_scores))
bundle_score = 0.70 * max(0.0, claim_support) + 0.30 * mean_citation_truth
bundle_score -= 0.15 * unsupported_fraction
bundle_score = clamp(bundle_score, 0.0, 1.0)
```

This prevents one good citation from fully laundering a bundle of bad citations while still recognizing that a sentence can be sufficiently supported by one source.

### 7. Unit and artifact scoring

Weight units by importance:

- Observation Statement: `1.00`
- Observation Implication: `0.70`
- Gap Statement: `0.85`
- Existing attempts / Why they fail: `0.75`
- Key Insight source-derived bridge: `0.60`
- Source-bearing Assumption: `0.50`

Apply availability/thinness penalties:

- No `logic/problem.md`: score `0.0` overall.
- Missing `Evidence` field for an Observation: that Observation Statement unit score max `0.30`.
- `Evidence: Abstract` for every Observation: artifact-level multiplier `0.75`.
- No parseable external citations anywhere: artifact-level multiplier `0.35`.
- More than half of citations unresolved: artifact-level multiplier `0.70`.
- Related-work/bibliographic context absent when citations are ambiguous: subtract `0.05` from final score, not below zero.

Final Python scoring function:

```python
from statistics import mean

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

LABEL_BASE = {
    "direct_support": 1.0,
    "partial_support": 0.65,
    "weak_context": 0.35,
    "unverifiable": 0.20,
    "unsupported": 0.0,
    "contradicted": -0.35,
}

UNIT_WEIGHTS = {
    "observation_statement": 1.00,
    "observation_implication": 0.70,
    "gap_statement": 0.85,
    "existing_attempts": 0.75,
    "why_they_fail": 0.75,
    "key_insight_bridge": 0.60,
    "source_bearing_assumption": 0.50,
}

def source_support(judgment):
    base = LABEL_BASE.get(judgment.get("support_label"), 0.0)
    number = judgment.get("number_match")
    if number is None:
        number = 1.0
    match = (
        0.35 * float(judgment.get("scope_match", 0.0)) +
        0.30 * float(judgment.get("polarity_match", 0.0)) +
        0.20 * float(judgment.get("specificity_match", 0.0)) +
        0.15 * float(number)
    )
    return max(-0.35, base * match)

def atomic_claim_score(source_judgments):
    scores = [source_support(j) for j in source_judgments]
    if not scores:
        return 0.0
    claim_support = max(scores)
    mean_truth = mean(max(0.0, s) for s in scores)
    unsupported_fraction = sum(1 for s in scores if s <= 0.05) / len(scores)
    return clamp(0.70 * max(0.0, claim_support) + 0.30 * mean_truth - 0.15 * unsupported_fraction)

def unit_score(unit):
    claim_scores = [atomic_claim_score(c["source_judgments"]) for c in unit["atomic_claims"]]
    score = mean(claim_scores) if claim_scores else 0.0
    if unit.get("missing_evidence_field"):
        score = min(score, 0.30)
    if unit.get("atomization_failed"):
        score = max(0.0, score - 0.05)
    return score

def m18_score(parsed_artifact):
    if not parsed_artifact.get("problem_present"):
        return 0.0
    weighted = []
    for unit in parsed_artifact.get("units", []):
        weight = UNIT_WEIGHTS.get(unit["unit_type"], 0.50)
        weighted.append((unit_score(unit), weight))
    if not weighted:
        return 0.0
    raw = sum(s * w for s, w in weighted) / sum(w for _, w in weighted)

    multiplier = 1.0
    if parsed_artifact.get("all_observation_evidence_is_abstract"):
        multiplier *= 0.75
    if parsed_artifact.get("parseable_external_citation_count", 0) == 0:
        multiplier *= 0.35
    total_citations = max(1, parsed_artifact.get("citation_count", 0))
    unresolved = parsed_artifact.get("unresolved_citation_count", 0)
    if unresolved / total_citations > 0.5:
        multiplier *= 0.70

    final = raw * multiplier
    if parsed_artifact.get("related_work_needed_but_absent"):
        final -= 0.05
    return clamp(final)
```

## Why the metric is hard to Goodhart

The score depends on external source agreement at the atomic-claim level, so superficial citation formatting, long bibliographies, or internally polished prose are insufficient. Vague claims avoid contradiction but lose specificity and locatability credit. Citation bundles are not treated as all-or-nothing: unsupported members drag down the score even when another citation supports the sentence. Missing or inaccessible evidence is penalized in the denominator, which makes abstract-only compilation visibly weaker without fabricating certainty.

The metric composes with the suite as an external-grounding check for the ARA's "why" layer. Other metrics can judge completeness, causal structure, novelty, or internal traceability; M18 asks whether the cited prior literature really says what the problem statement says it says. That makes it especially valuable before using the ARA for downstream literature synthesis, hypothesis generation, or automated research planning.
