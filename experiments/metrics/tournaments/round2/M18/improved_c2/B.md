# M18 Expansion: Claim Drift / Reference Truthfulness (Cycle 2)

## Changes (cycle 2)

Judge feedback (`critique_c1.md`) ranked exp4 #2 of 4 and named this as a co-leader with exp2,
with four specific gaps to close before it becomes a genuine co-leader. This revision addresses
all four directly:

1. **Added a bounded, gated cross-layer role-drift audit** (Step 6, new). Borrowed from exp2's
   Step 6 but made conditional: it only spends weight/budget on `related_work.md` typed-role
   verification when the problem layer actually leans on RW (a Gap's `Existing attempts`/`Why
   they fail` or an Observation's `Evidence` names an `RW##` id or an entry title/author covered
   by `related_work.md`). Problem.md stays dominant-weighted in the ordinary case; the RW-role
   term only claims weight when triggered, and it is penalized (not skipped) when RW is needed
   but absent or unresolved. This closes exp4's only named gap relative to exp2 without diluting
   the problem-primary focus the critique praised exp2 for needing to fix in the other direction.

2. **Bounded the external-call budget deterministically** (new Step 0), borrowing exp1's
   audit-cap + tie-break-sort approach, which the critique called out as the one thing exp1 did
   better than exp2/exp4. Observations, Gaps, and source-bearing Assumptions above a fixed cap
   are triaged by a deterministic priority sort (not by artifact order or model choice), so cost
   is bounded reproducibly. Units beyond the cap are not dropped from the denominator — they
   receive a cheaper resolution-only pass instead of skipping penalize-don't-skip.

3. **Pinned down elicitation of the multi-dimensional match sub-scores.** The `scope_match` /
   `polarity_match` / `specificity_match` / `number_match` fields previously had no anchors,
   so two runs could disagree on what "0.6" means. Step 5's prompt now ships 0.0/0.5/1.0 rubric
   anchors for each dimension, plus JSON-schema validation with one retry and a conservative
   `unverifiable`/0.0 fallback on repeated malformed output (borrowing exp2's robustness
   pattern), so the multiplicative combination in `source_support()` is not noise-amplifying.

4. **Closed the contradiction-laundering path with a worked example.** The critique asked for a
   sanity check that a single `contradicted` source in a multi-source bundle produces a sharp
   drop and "isn't silently laundered by a co-cited supporting source." It is not sanity-checked
   in cycle 1 — worked through below, the old formula let a `direct_support` co-citation pull a
   contradicted bundle up to `0.69`, i.e. it *was* laundered. Step 6 now adds a hard
   major-drift cap (`bundle ≤ 0.15` whenever any source in the bundle is judged `contradicted`),
   independent of how strong the other citation is, with the arithmetic shown so the fix is
   verifiable rather than asserted.

Everything else — the major/moderate/minor drift taxonomy, the quote-exists-vs-support-exists
separation, the graded resolution/retrieval scores, and the availability-is-part-of-the-score
multipliers — is retained from cycle 1 since the critique found no correctness issues there.

---

## Metric intent

This metric asks whether the citations used in `logic/problem.md` actually support the
propositions they are attached to when checked against the real cited sources, not just against
the compiler's local prose or a nearby quoted line. It targets the problem layer because
Observations, Gaps, and the Key Insight are the ARA's causal story for why the work matters. If
that layer cites sources for stronger, narrower, broader, or different claims than the sources
actually make, downstream agents inherit a distorted problem formulation even when the rest of
the ARA is internally coherent.

The metric should reward citation use that is faithful at the level of claim scope, population,
intervention/method, outcome, direction, magnitude, uncertainty, and evidential status. A source
that says "associated with" must not be cited as proving causation; a study in a narrow cohort
must not be used as evidence for a general field-wide fact; a speculative review sentence must
not be cited as if it were a primary result; and a paper showing one biomarker performs well must
not be used to claim it is optimal across all stages. The metric should also reward citations
that are sufficiently locatable: DOI/PMID/arXiv/title-year-author signals, section names, and
enough surrounding wording to retrieve the true source.

The metric must not reward merely having many citations. Citation density can hide drift. It also
must not reward citations that are faithful only to an intermediate ARA artifact, because the
ranked-ledger point of M18 is net-new external reach: the check goes against the real source
wherever possible. When the problem layer leans on `related_work.md`'s typed reference graph
(imports/baseline/bounds/extends/refutes), the metric additionally checks that those typed roles
are themselves truthful against the real source — a dependency graph can be internally tidy while
mischaracterizing what a source actually is or found. Missing, ambiguous, paywalled,
abstract-only, or non-resolvable sources are not skipped. They are scored as weaker evidence with
explicit penalties because availability and verifiability are part of source truthfulness.

## What counts as drift

Drift is any material mismatch between an ARA problem-layer assertion and what the cited real
source supports. Major drift includes citing a source for an opposite conclusion, a result absent
from the source, a fabricated number, a wrong study design, or a conclusion generalized far
beyond the source's population or endpoint. Moderate drift includes overclaiming certainty,
turning a secondary citation into primary evidence, omitting an important qualifier, using a
method-comparison paper for a biological mechanism, or citing a source that only partially
supports a multi-part sentence. Minor drift includes imprecise but directionally correct
paraphrase, missing sample/context details that do not change the inference, or citation bundles
where some but not all sources support the exact sentence.

Drift also includes **role drift**: when a Gap's `Existing attempts`/`Why they fail` or an
Observation's `Evidence` leans on a `related_work.md` entry's typed role (e.g. "extends X" or
"refutes Y"), and the real source does not actually occupy that role relative to this work — for
instance, a source tagged `baseline` that the real paper never positions as comparable, or a
source tagged `refutes` that in fact only partially disagrees. This is scored only when the
problem layer actually depends on such a role (see Step 6); it is not a tax on artifacts that
don't reference `related_work.md` at all.

For `logic/problem.md`, the load-bearing units are:

- Observation `Statement` plus its `Evidence`.
- Observation `Implication` when it makes an inference from the evidence.
- Gap `Statement`, `Existing attempts`, and `Why they fail` when they cite or depend on prior
  work.
- Key Insight `Derived from` chain only insofar as the cited observations/gaps truthfully
  establish the need it claims to resolve.

Assumptions are checked only if they contain source citations or externally factual claims.
Otherwise they contribute to a small availability/context component, not the source-truthfulness
denominator.

## Failure modes and gaming routes

The easiest gaming route is to write vague Observations with broad review citations that are hard
to falsify. This should score lower on specificity and source-locatability, even if no direct
contradiction is found. Another route is citation stuffing: attach eight papers to a sentence
where only one supports it. The workflow samples and scores citation-claim pairs, then penalizes
unsupported citations inside bundles rather than giving the bundle full credit — and, per the
cycle-2 fix, a bundle containing even one `contradicted` source is hard-capped regardless of how
strong a co-cited supporter is, closing the laundering route the cycle-1 formula left open (see
the worked example in Step 6). A third route is quote laundering: include a true phrase from the
source while using it to support a broader claim the source does not support. The scoring prompt
explicitly separates "quoted text exists" from "the cited source supports this assertion." A
fourth route, specific to cross-layer dependency graphs, is role laundering: tag a source with a
flattering typed role in `related_work.md` (e.g. calling a source you merely skimmed a "baseline"
or an "extends" precursor) so the ARA reads as more rigorously situated than it is; the gated
Step 6 audit checks the typed role against the real source when the problem layer depends on it.

This metric overlaps slightly with generic citation verification, but is tighter and deeper: it
evaluates source-to-claim semantics for the problem formulation, not just whether references are
real, lines contain similar words, or the ARA quotes a source passage. It composes well with
internal-consistency metrics because an internally consistent ARA can still be externally false;
conversely, this metric does not judge whether the problem story is complete or elegant except
through the truthfulness and verifiability of its source grounding.

## Inputs

Primary input:

- `logic/problem.md` parsed according to the §4 shape: Observations, Gaps, Key Insight, and
  Assumptions.

Optional cross-layer input:

- `logic/related_work.md` from §6 if available through the ARA, because M18 is cross §6. It
  provides two things: (a) bibliographic hints used only for source resolution and context,
  applied to every unit as in cycle 1, and (b) typed roles (`RW##`: imports/baseline/bounds/
  extends/refutes) that are separately audited in Step 6 **only when the problem layer's text
  actually references an RW id or an RW-covered source**. If absent entirely, source resolution
  receives the appropriate penalty and Step 6 contributes its penalize-don't-skip floor rather
  than being omitted.

External inputs:

- Semantic Scholar lookup for cited paper metadata and abstracts.
- DOI/arXiv/PubMed/open web lookup for full text or landing pages when identifiers are present.
- Optional full-text retrieval where legally accessible.
- LLM semantic judgment over bounded snippets and abstracts/full text.

All unavailable fields and failed lookups are retained as scored records. No unresolved citation
is dropped from the denominator.

## Generation / compute workflow

### 0. Bound the audit set deterministically

Before spending any external-call budget, build the full unit list from `logic/problem.md`, then
select the units that receive the full pipeline (Steps 1–6) versus a cheaper resolution-only pass
(Step 3 only), using fixed caps and a deterministic tie-break so the choice is reproducible
across runs and cannot be gamed by unit ordering:

```python
AUDIT_CAPS = {
    "observation_statement": 8,
    "observation_implication": 8,
    "gap_statement": 6,
    "existing_attempts": 6,
    "why_they_fail": 6,
    "key_insight_bridge": 5,   # all Derived-from links audited unless the chain exceeds this
    "source_bearing_assumption": 5,
}

def tie_break_key(unit):
    # Higher priority first: numeric/comparative/causal claims are the ones drift hides in.
    return (
        unit.get("has_number", False),
        unit.get("has_comparator", False),
        unit.get("has_causal_verb", False),
        len(unit.get("text", "")),
        -unit.get("artifact_order", 0),  # stable fallback, does not itself decide ranking
    )

def select_audit_set(units_by_type, caps=AUDIT_CAPS):
    full_pass, resolution_only = [], []
    for unit_type, units in units_by_type.items():
        cap = caps.get(unit_type, len(units))
        ranked = sorted(units, key=tie_break_key, reverse=True)
        full_pass.extend(ranked[:cap])
        resolution_only.extend(ranked[cap:])
    return full_pass, resolution_only
```

Units in `resolution_only` still count in the denominator (penalize-don't-skip): they run only
Step 3 (source resolution) and receive `atomic_claim_score = min(0.5, resolution_score)` — capped
below the ceiling a full pass could earn, since an unaudited claim cannot be credited as if it
were verified. This bounds the number of Semantic Scholar/web/LLM calls to a fixed function of
artifact size while never letting overflow units default to a free pass or a silent drop.

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
    "referenced_rw_ids": ["RW03"],   # new: RW## ids or RW-covered titles named in this unit's text
}
```

Citation extraction accepts parenthetical citations, DOI/arXiv/PMID strings, named references,
section refs such as `§1 Introduction`, and mixed evidence strings. `referenced_rw_ids` is
populated by matching `RW##` tokens or `related_work.md` entry titles/authors appearing in
`Existing attempts`, `Why they fail`, or `Evidence` text; this is what gates Step 6. If an
Observation has `Evidence: Abstract` or no parseable external source, create a record with
`declared_refs=[]` and score it through the missing/thin pathway.

### 2. Normalize atomic claims

Split each load-bearing unit into one to three atomic assertions. Preserve numeric values,
comparison terms, populations, interventions/methods, outcomes, and modality words such as
"causes", "predicts", "correlates", "best", "first", "significant", or "early". Use deterministic
sentence splitting first; use an LLM only when a sentence contains multiple semicolon/comma-joined
factual assertions.

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

Validate the response against the JSON schema above. On malformed or non-conforming output,
retry once with the same prompt plus `"Your previous output was invalid JSON or missing a
required field. Return valid JSON only."`. If the retry also fails, fall back to treating the
original sentence as one claim and apply a `0.05` process penalty to that unit, exactly as in
cycle 1 — the schema-validation step only changes how failure is detected, not the fallback.

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
- `0.20`: only a secondary landing page, abstract stub, or citation string with no confident
  source.
- `0.0`: no resolvable external source.

Unresolved sources remain in the denominator and receive support score `0.0` unless the claim has
other resolved citations that support it. The unresolved citation still lowers the bundle score.

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

Paywalled or inaccessible full text is not skipped; it receives the best available retrieval
score, usually abstract-only.

### 5. Semantic support judgment

For each atomic claim and each cited source, ask an LLM to judge support using only retrieved
source text. The model must return JSON with a label and rationale.

Prompt:

```text
You are checking whether a real cited source supports an ARA problem-layer claim.
Use ONLY the provided source text. Do not use outside knowledge.
"Quoted text appears in the source" is NOT the same as "the source supports this claim" —
judge the latter.

ARA claim:
{atomic_claim}

Citation string:
{citation_string}

Source metadata:
{metadata_json}

Retrieved source text:
{snippets}

Score each dimension using these anchors:
- scope_match: 1.0 = same population/method/endpoint as the claim; 0.5 = overlapping but
  narrower or broader in one material respect; 0.0 = different population/method/endpoint.
- polarity_match: 1.0 = same direction/valence (e.g. both "increases", both "no effect");
  0.5 = same topic, ambiguous or mixed direction; 0.0 = opposite direction.
- specificity_match: 1.0 = source states the claim at comparable precision (numbers, named
  comparator); 0.5 = source is qualitatively consistent but less precise; 0.0 = source is only
  generically on-topic.
- number_match: 1.0 = cited number matches within reported uncertainty; 0.5 = same order of
  magnitude/direction but not matching; 0.0 = contradicts the reported number; null if the claim
  has no number.

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

Validate the JSON against the schema (six required keys, enums, numeric ranges). On a malformed
or out-of-range response, retry once with `"Your previous output did not match the required JSON
schema. Return valid JSON only, using only the listed enum values."`. If the retry still fails,
record `support_label="unverifiable"`, all match fields `0.0`, and flag the record
`judgment_fallback=true` — this feeds the same `0.20` unverifiable base rather than crashing the
pipeline or silently omitting the source.

Map labels to base support:

- `direct_support`: `1.0`
- `partial_support`: `0.65`
- `weak_context`: `0.35`
- `unverifiable`: `0.20`
- `unsupported`: `0.0`
- `contradicted`: `-0.35`

Then multiply by `(0.35*scope_match + 0.30*polarity_match + 0.20*specificity_match +
0.15*number_match_or_1)`. Cap negative scores at `-0.35`.

### 6. Bundle scoring (with major-drift contradiction cap)

For a claim with multiple cited sources, score both best support and citation hygiene, and apply
a hard cap when any cited source in the bundle is judged `contradicted` — a false citation is
major drift by definition (see "What counts as drift" above) and must not be offset by a
co-cited true one:

```python
def atomic_claim_score(source_judgments):
    scores = [source_support(j) for j in source_judgments]
    if not scores:
        return 0.0
    contradicted = any(j.get("support_label") == "contradicted" for j in source_judgments)
    claim_support = max(scores)
    mean_truth = mean(max(0.0, s) for s in scores)
    unsupported_fraction = sum(1 for s in scores if s <= 0.05) / len(scores)
    bundle = clamp(0.70 * max(0.0, claim_support) + 0.30 * mean_truth - 0.15 * unsupported_fraction)
    if contradicted:
        bundle = min(bundle, 0.15)
    return bundle
```

**Worked example (why the cap is needed).** Claim cited by two sources: Source A is
`direct_support` with `match=0.9` → `source_support = 1.0 * 0.9 = 0.90`. Source B is
`contradicted` with `match=0.8` → `source_support = max(-0.35, -0.35 * 0.8) = -0.28`.
`scores = [0.90, -0.28]`. Without the cap: `claim_support = max(scores) = 0.90`;
`mean_truth = mean(max(0,0.90), max(0,-0.28)) = mean(0.90, 0.0) = 0.45`;
`unsupported_fraction = 1/2 = 0.5` (only the `-0.28` entry is `≤ 0.05`);
`bundle = 0.70*0.90 + 0.30*0.45 - 0.15*0.5 = 0.63 + 0.135 - 0.075 = 0.69`. That is a passing
score for a claim one of whose two citations flatly contradicts it — exactly the laundering the
cycle-1 critique flagged. With the cap: `bundle = min(0.69, 0.15) = 0.15`, correctly landing in
major-drift territory regardless of how strong Source A is. The cap only fires on `contradicted`,
not on `unsupported`/`weak_context`, so an honestly-thin-but-not-false bundle is still scored by
the ordinary weighted formula, not flattened to the floor.

### 7. Cross-layer role-drift audit (gated on RW dependency)

Run this step only for units where `referenced_rw_ids` is non-empty (Step 1). If
`related_work.md` is absent or the referenced id cannot be resolved to an entry, do not skip:
apply the same penalize-don't-skip floor as an unresolved citation (`role_support = 0.0`,
retained in the denominator).

For each triggered unit, take the RW entry's typed role (`imports` / `baseline` / `bounds` /
`extends` / `refutes`) and its stated `Delta`, and reuse the Step 5 support-judgment prompt with
the role claim substituted in:

```text
ARA claim:
"This work's related-work graph asserts source {source} occupies the role '{role}'
 relative to this work, specifically: {delta_text}"
```

Score with the same label/match machinery as Step 5, producing `role_support` per triggered unit
via `source_support()`. This catches, for example, a source tagged `refutes` in
`related_work.md` that the real paper does not actually contest, or a `baseline` tag applied to a
source the paper never positions as comparable — a truthfulness failure in the dependency graph
itself, not just in a sentence.

```python
def rw_role_component(triggered_units):
    if not triggered_units:
        return None  # not triggered: contributes no weight, not a zero
    role_scores = [atomic_claim_score([u["role_judgment"]]) for u in triggered_units]
    return mean(role_scores)
```

### 8. Unit and artifact scoring

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
- Related-work/bibliographic context absent when citations are ambiguous: subtract `0.05` from
  final score, not below zero.
- RW role dependency triggered but `related_work.md` absent or the referenced id unresolved:
  subtract an additional `0.05` (distinct from the ambiguity penalty above, since this is a
  dependency the problem layer explicitly created by naming an RW id).

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

RW_ROLE_WEIGHT = 0.15  # only applied when Step 7 is triggered

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
    contradicted = any(j.get("support_label") == "contradicted" for j in source_judgments)
    claim_support = max(scores)
    mean_truth = mean(max(0.0, s) for s in scores)
    unsupported_fraction = sum(1 for s in scores if s <= 0.05) / len(scores)
    bundle = clamp(0.70 * max(0.0, claim_support) + 0.30 * mean_truth - 0.15 * unsupported_fraction)
    if contradicted:
        bundle = min(bundle, 0.15)
    return bundle

def unit_score(unit):
    if unit.get("resolution_only"):
        # Step 0 overflow: never audited past resolution, capped below what a full pass could earn.
        return min(0.5, unit.get("resolution_score", 0.0))
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
    problem_layer_score = sum(s * w for s, w in weighted) / sum(w for _, w in weighted)

    rw_role_score = rw_role_component(parsed_artifact.get("rw_role_triggered_units", []))
    rw_dependency_unresolved = parsed_artifact.get("rw_role_triggered_but_unresolved", False)
    if rw_role_score is None and not rw_dependency_unresolved:
        raw = problem_layer_score  # not triggered: full weight stays on problem layer
    else:
        rw_component = rw_role_score if rw_role_score is not None else 0.0
        raw = (1 - RW_ROLE_WEIGHT) * problem_layer_score + RW_ROLE_WEIGHT * rw_component

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
    if rw_dependency_unresolved:
        final -= 0.05
    return clamp(final)
```

## Why the metric is hard to Goodhart

The score depends on external source agreement at the atomic-claim level, so superficial citation
formatting, long bibliographies, or internally polished prose are insufficient. Vague claims
avoid contradiction but lose specificity and locatability credit. Citation bundles are not
treated as all-or-nothing: unsupported members drag down the score even when another citation
supports the sentence, and — after the cycle-2 fix — a single `contradicted` member hard-caps the
whole bundle at `0.15` no matter how strong a co-cited supporter is, closing the laundering path
the worked example in Step 6 demonstrates was open in cycle 1. Missing or inaccessible evidence is
penalized in the denominator, which makes abstract-only compilation visibly weaker without
fabricating certainty. The gated role-drift audit (Step 7) closes a further route specific to
cross-layer dependency graphs — tagging a source with a flattering typed role in
`related_work.md` without the real source actually occupying that role — while the gating itself
(only triggered when the problem layer names an RW id) prevents that audit from becoming an
unrelated tax on artifacts that never lean on it. The Step 0 audit-set cap plus deterministic
tie-break sort bounds the external-call budget without letting an adversary hide drift past the
sampled window: priority favors claims with numbers, comparators, and causal verbs — exactly
where drift is cheapest to introduce and most consequential — and overflow units are still scored,
just at a capped ceiling, rather than silently exempted.

The metric composes with the suite as an external-grounding check for the ARA's "why" layer.
Other metrics can judge completeness, causal structure, novelty, or internal traceability; M18
asks whether the cited prior literature really says what the problem statement says it says, and
now also whether the typed dependency graph, where it exists and is relied upon, tells the truth
about the sources it names. That makes it especially valuable before using the ARA for downstream
literature synthesis, hypothesis generation, or automated research planning.
