# M18 Expansion: Claim Drift / Reference Truthfulness

## Metric intent

This metric asks whether the citations used in `logic/problem.md` and the cross-layer citation graph in
`logic/related_work.md` truthfully support the claims they are attached to. It rewards ARA artifacts whose
Observations, Gaps, Key Insight provenance, and related-work deltas remain faithful to the real cited
sources, not merely internally consistent inside the ARA.

The good-science signal is source discipline: a strong ARA should not turn a background citation into an
empirical result, overstate a source's population or effect size, cite a paper for a claim it never made,
or hide uncertainty behind a vague citation cluster. This is tighter than checking whether a citation appears
near a quoted line in the artifact. The metric compares each ARA claim against the external source itself,
using DOI/arXiv/semantic lookup where available, and penalizes claims that cannot be traced because the
artifact gave too little source identity.

## What to reward

Reward:

- Specific claim-source alignment: cited sources actually support the numerical, causal, comparative,
  methodological, or background claim they are used for.
- Accurate citation granularity: a multi-source Evidence field is not treated as valid if only one weakly
  related source supports a broad bundle of claims.
- Faithful related-work deltas: each `RW##` block's type, "What changed", "Why", adopted elements, and
  claims affected match the cited source's contribution.
- Honest uncertainty: qualified source claims remain qualified in the ARA instead of becoming stronger,
  broader, or more causal.
- Recoverable provenance: DOI/arXiv IDs, recognizable author-year references, and section references make
  truth checking feasible.

## What not to reward

Do not reward:

- Citations that are real but attached to the wrong proposition.
- Verbatim-looking text that is not in the cited source or is taken from a secondary source while implying
  primary support.
- Citation stuffing, where many references are listed but none is mapped to the specific claim.
- Thin `Evidence: Abstract` support when the claim contains detailed prior-work, numerical, or comparative
  assertions requiring full-source grounding.
- Related-work entries whose DOI is missing and whose author-year label is too vague to identify the source.

## Failure modes and gaming routes

The main failure modes are source drift, scope drift, and granularity drift. Source drift occurs when a
citation is used for a claim from a different paper. Scope drift occurs when the cited paper studied a
different population, endpoint, method, organism, or setting than the ARA claim implies. Granularity drift
occurs when a citation cluster supports some nearby background but not the exact detailed sentence.

Gaming routes include adding many citations to dilute responsibility, copying abstracts without checking
what the paper actually showed, using vague "section ref" evidence without bibliographic identity, and
putting broad claims in `Implication`, `Why they fail`, or `RW##` delta fields where ordinary citation
checks may not look. The workflow below samples and scores claim-citation pairs at field level, so unsupported
detail still loses credit even if the source exists.

## Effect of the critique notes

The ledger note says this metric is net-new because it checks against the real source, not just quote-at-line
inside the ARA. The design therefore requires external retrieval for every scored citation where possible and
treats missing source identity as a defect rather than skipping it. It also scopes tightly to truthfulness of
source use, avoiding redundancy with metrics that judge novelty, dependency graph breadth, or problem quality
in the abstract. `logic/related_work.md` is used only because M18 is cross §6: the source-truth check must
cover related-work deltas that justify the problem framing.

## Required inputs

Inputs assumed available:

- `logic/problem.md`
- `logic/related_work.md`
- External source lookup by DOI, arXiv ID, Semantic Scholar title/author-year search, and optional full-text
  or abstract retrieval.

Missing or thin inputs are penalized. The metric never returns N/A. If an artifact field, DOI, citation, or
retrieved source is unavailable, that unavailability becomes a low-confidence or failed support judgment.

## Claim units

Extract scored claim units from `logic/problem.md`:

- Observation `Statement` plus its `Evidence`.
- Observation `Implication` plus the same `Evidence`.
- Gap `Statement`, `Existing attempts`, and `Why they fail`, with cited observation IDs expanded to the
  evidence sources of their upstream Observations.
- Key Insight `Insight` and `Enables`, with `Derived from` IDs expanded to Observation and Gap evidence.
- Assumptions, using any inline citations if present; if none are present, evaluate only whether the assumption
  is over-specific relative to the available problem evidence.

Extract scored claim units from `logic/related_work.md`:

- Each `RW##` block: `Type`, `Delta / What changed`, `Delta / Why`, `Claims affected`, and `Adopted elements`,
  checked against that block's DOI/arXiv/author-year source.
- Each brief background/supporting reference bullet: one-line role checked against its DOI or author-year
  source.

## Generation / compute workflow

1. Parse `logic/problem.md` into Observation, Gap, Key Insight, and Assumption records according to the
   documented shape.
2. Parse `logic/related_work.md` into full `RW##` records and brief background records according to the
   documented shape.
3. Build a citation inventory. For problem Observations, parse `Evidence` into citation handles and section
   references. For Gaps and Key Insight, expand `Caused by` and `Derived from` references to the cited
   Observations and Gaps. For related work, use DOI/arXiv when present; otherwise use the heading or bullet
   author-year label.
4. Resolve each source:
   - DOI/arXiv: query Semantic Scholar by external ID.
   - Author-year with no DOI: query Semantic Scholar with exact author-year plus distinctive title terms if
     present in the ARA text.
   - Section-only evidence with no bibliographic handle: mark unresolved unless the section contains a
     parseable citation.
5. Retrieve source evidence:
   - Prefer full text when available through an allowed external source.
   - Otherwise use Semantic Scholar title, abstract, venue/year, fields of study, citation contexts if
     available, and metadata.
   - Record retrieval level as `full_text`, `abstract_metadata`, or `unresolved`.
6. Decompose each claim unit into atomic assertions. Use the LLM prompt below, then normalize to JSON.
7. For each atomic assertion and each assigned source, run the LLM source-support prompt below using retrieved
   source snippets/abstract/metadata. Convert output to deterministic numeric values.
8. Aggregate at claim-unit level, then artifact level, applying explicit availability and thinness penalties.

### External calls

Semantic Scholar DOI/arXiv lookup:

```text
Query: externalIds.DOI == "{doi}" OR externalIds.ArXiv == "{arxiv_id}"
Return: paperId, title, year, authors, abstract, externalIds, fieldsOfStudy, url, openAccessPdf
```

Semantic Scholar author-year lookup:

```text
Query: "{author_surname} {year}" plus any quoted title phrase or distinctive technical term from the ARA citation context
Return top 5 candidates; accept only if author surname and year match and title/topic is semantically consistent.
```

Optional full-text lookup:

```text
Input: DOI/arXiv/openAccessPdf URL
Return searchable full text or extracted abstract. If unavailable, proceed with abstract/metadata and apply retrieval penalty.
```

### LLM atomic-claim prompt

```text
You are decomposing an ARA claim into source-checkable atomic assertions.
Return JSON only:
{
  "atomic_assertions": [
    {
      "assertion": "...",
      "claim_type": "numeric|causal|comparative|method|population|background|limitation|adoption|other",
      "requires_primary_support": true/false
    }
  ]
}

ARA field:
{field_name}

Claim text:
{claim_text}
```

### LLM source-support prompt

```text
You are checking whether a real cited source supports an ARA assertion.
Use only the source material provided. Do not infer beyond it.
Return JSON only:
{
  "support": "supported|partially_supported|contradicted|not_found|source_unavailable",
  "drift_type": "none|wrong_source|scope_drift|strength_drift|population_drift|method_drift|number_drift|citation_too_vague|unavailable",
  "confidence": 0.0-1.0,
  "rationale": "one sentence"
}

ARA assertion:
{atomic_assertion}

Cited source identity:
{source_identity}

Retrieved source material:
{source_material}
```

The deterministic mapper is:

- `supported`: 1.0
- `partially_supported`: 0.55
- `not_found`: 0.20
- `contradicted`: 0.0
- `source_unavailable`: 0.0

Multiply by confidence clamped to `[0.25, 1.0]`, so low-confidence positive judgments do not receive full
credit but unavailable or contradicted sources remain zero.

## Final scoring function

```python
import re
from dataclasses import dataclass
from statistics import mean


@dataclass
class SourceJudgment:
    support: str
    confidence: float
    retrieval_level: str
    has_resolvable_id: bool
    claim_requires_primary_support: bool = False


SUPPORT_VALUE = {
    "supported": 1.0,
    "partially_supported": 0.55,
    "not_found": 0.20,
    "contradicted": 0.0,
    "source_unavailable": 0.0,
}

RETRIEVAL_MULTIPLIER = {
    "full_text": 1.0,
    "abstract_metadata": 0.82,
    "unresolved": 0.0,
}


def parse_nonempty_field_count(markdown: str) -> int:
    fields = re.findall(r"- \*\*[^*]+\*\*:\s*(.+)", markdown)
    return sum(1 for value in fields if value.strip())


def availability_score(problem_md: str, related_work_md: str) -> float:
    score = 1.0
    if not problem_md.strip():
        score -= 0.55
    if not related_work_md.strip():
        score -= 0.30
    if parse_nonempty_field_count(problem_md) < 8:
        score -= 0.20
    if "## RW" not in related_work_md:
        score -= 0.15
    return max(0.0, score)


def thinness_penalty(problem_md: str, related_work_md: str) -> float:
    penalty = 0.0
    evidence_fields = re.findall(r"\*\*Evidence\*\*:\s*(.+)", problem_md)
    if evidence_fields:
        abstract_only = sum(1 for e in evidence_fields if e.strip().lower() == "abstract")
        penalty += 0.18 * (abstract_only / len(evidence_fields))
    else:
        penalty += 0.20

    unspecified_dois = len(re.findall(r"\*\*DOI\*\*:\s*Not specified in paper", related_work_md, re.I))
    rw_blocks = max(1, len(re.findall(r"^## RW\d+", related_work_md, re.M)))
    penalty += 0.12 * min(1.0, unspecified_dois / rw_blocks)

    if "brief" not in related_work_md.lower() and rw_blocks > 0:
        penalty += 0.08

    return min(0.35, penalty)


def judgment_score(j: SourceJudgment) -> float:
    base = SUPPORT_VALUE.get(j.support, 0.0)
    confidence = min(1.0, max(0.25, float(j.confidence)))
    retrieval = RETRIEVAL_MULTIPLIER.get(j.retrieval_level, 0.0)
    id_multiplier = 1.0 if j.has_resolvable_id else 0.65
    primary_multiplier = 1.0
    if j.claim_requires_primary_support and j.retrieval_level != "full_text":
        primary_multiplier = 0.75
    return base * confidence * retrieval * id_multiplier * primary_multiplier


def claim_unit_score(judgments: list[SourceJudgment]) -> float:
    if not judgments:
        return 0.0
    per_source = [judgment_score(j) for j in judgments]
    # A claim with many citations should not get full credit from one good source if the rest are irrelevant.
    best_support = max(per_source)
    average_support = mean(per_source)
    return 0.65 * best_support + 0.35 * average_support


def m18_score(problem_md: str, related_work_md: str, claim_units: list[list[SourceJudgment]]) -> float:
    """
    claim_units is produced by the workflow above. Each inner list contains all source judgments
    for one atomic or field-level claim unit. Missing fields, missing sources, and unresolved
    citations must be represented as empty judgment lists or SourceJudgment(... source_unavailable ...),
    never dropped.
    """
    if not claim_units:
        source_truth = 0.0
    else:
        source_truth = mean(claim_unit_score(unit) for unit in claim_units)

    availability = availability_score(problem_md, related_work_md)
    penalty = thinness_penalty(problem_md, related_work_md)
    final = (0.78 * source_truth + 0.22 * availability) - penalty
    return round(max(0.0, min(1.0, final)), 4)
```

## Why it is hard to Goodhart

It is hard to Goodhart because the scoring target is the real cited source, not citation count, fluent prose,
or internal ARA consistency. Adding more citations creates more source-claim obligations. Making claims more
specific helps only if the source really supports the specifics. Removing source identifiers lowers
availability and resolvability scores. Using only abstracts caps retrieval quality and penalizes detailed
primary claims that require full-text support.

## Composition with the suite

This metric composes as a provenance-truth layer. Other metrics can reward novelty, problem framing, dependency
graph breadth, or methodological contribution, but M18 asks whether the documentary basis for those signals is
honest. It should be interpreted as a reliability multiplier: a bold gap, elegant insight, or rich related-work
graph is less valuable if its citations drift away from what the sources actually say.
