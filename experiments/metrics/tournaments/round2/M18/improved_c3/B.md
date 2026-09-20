## Changes (cycle 3)

`critique_c2.md` ranked B (this proposal) as having correctly closed the contradiction-laundering
hole (worked example, hard bundle cap) while A's cycle-2 revision claimed the same fix in prose but
shipped code that still laundered it. The cross-cutting note told B to import A's one genuine
strength — the semantic, RW-existence-independent dependency signal — while fixing three
B-specific weaknesses. This revision does all three, concretely:

1. **Broadened the Step 7 trigger beyond literal `RW##`/title-token matching (critique's #1).**
   Step 1 now also computes a semantic `external_dependency_signal` directly from the
   `logic/problem.md` unit text alone — independent of whether `related_work.md` exists or what it
   contains — so paraphrasing away an explicit RW id/title no longer defeats the audit, and
   deleting `related_work.md` no longer dodges it either (this was named as A's specific strength
   over B; B now has it too, plus a semantic detector instead of a keyword-verb detector, which is
   the axis the critique separately flagged as still-evadable even in A). Step 7 now fires on
   `referenced_rw_ids non-empty OR external_dependency_signal true`, with a new match-then-audit
   path for the semantic-only case and an explicit worked example showing the paraphrase-evasion
   route closing.
2. **Made the `resolution_only` overflow score fully deterministic (critique's #2).** Per-citation
   resolution scores now aggregate to the unit level by `max` (matching the best-supporting-source
   logic used everywhere else in this metric), exactly as the critique recommended, removing the
   previously-unspecified aggregation. The flat ceiling is now risk-tiered (`0.35` for
   number/comparator/causal-verb-bearing units, `0.5` otherwise) so a drift-prone overflow claim
   cannot float to the same ceiling as a low-stakes one with zero entailment checking. A new
   artifact-level `overflow_fraction` penalty (Step 8) additionally discounts artifacts that push
   more than 30% of units into the unaudited pool, closing the "pad the artifact to bury a claim in
   the unaudited overflow" route the critique asked to be ruled out rather than merely asserted
   away.
3. **Decided and documented unit-level contradiction propagation (critique's #3).** A single
   `contradicted` atomic claim inside a unit now caps the whole unit's score at `0.35` — looser than
   the `0.15` bundle/atomic-claim cap (since sibling claims in the same unit may be genuinely
   separate assertions with independent evidence) but tight enough that a contradicted claim cannot
   be diluted into a passing-looking unit average by clean siblings. Worked example included in
   Step 8.
4. **Minor (critique's #4): tied the Step 0 caps to expected cardinality.** Added one sentence
   noting the caps (8/8/6/6/6/5/5) sit well above the §4-typical 3–5 Observations / 2–4 Gaps, so for
   a real single-paper artifact they almost never bind — they exist as a deterministic ceiling on
   cost and on the overflow route addressed in #2, not as a routine sampling mechanism.

Also fixed, while locking the final version: three prose cross-references in "What counts as
drift," "Failure modes," and "Inputs" pointed to "Step 6" for the role-drift audit, which is
actually Step 7 (Step 6 is bundle scoring) — a leftover numbering slip from cycle 2. All now read
Step 7, matching the actual step listing and the "Why the metric is hard to Goodhart" section,
which already had it right.

Everything else — the major/moderate/minor drift taxonomy, the quote-exists-vs-support-exists
separation, the graded resolution/retrieval scores, the rubric-anchored multi-dimensional match
scores, the JSON-schema validation with bounded retry, and the bundle-level contradiction cap with
its worked example — is retained from cycle 2 since the critique found no correctness issues there
and explicitly called the bundle-cap fix "the standout fix" of the field.

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
(imports/baseline/bounds/extends/refutes) — whether it names that dependency explicitly or only
describes it — the metric additionally checks that those typed roles are themselves truthful
against the real source — a dependency graph can be internally tidy while mischaracterizing what a
source actually is or found. Missing, ambiguous, paywalled, abstract-only, or non-resolvable
sources are not skipped. They are scored as weaker evidence with explicit penalties because
availability and verifiability are part of source truthfulness.

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
"refutes Y") — whether that dependency is named explicitly by RW id/title or only described in
plain language (e.g. "we build on the network meta-analysis approach" without citing it by id) —
and the real source does not actually occupy that role relative to this work; for instance, a
source tagged `baseline` that the real paper never positions as comparable, or a source tagged
`refutes` that in fact only partially disagrees. This is scored only when the problem layer
actually depends on such a role, detected either literally or semantically (see Step 7); it is not
a tax on artifacts that don't lean on prior work at all.

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
unsupported citations inside bundles rather than giving the bundle full credit — and a bundle
containing even one `contradicted` source is hard-capped regardless of how strong a co-cited
supporter is, closing the laundering route the cycle-1 formula left open (see the worked example
in Step 6). A third route is quote laundering: include a true phrase from the source while using it
to support a broader claim the source does not support. The scoring prompt explicitly separates
"quoted text exists" from "the cited source supports this assertion." A fourth route, specific to
cross-layer dependency graphs, is role laundering: tag a source with a flattering typed role in
`related_work.md` (e.g. calling a source you merely skimmed a "baseline" or an "extends"
precursor) so the ARA reads as more rigorously situated than it is; Step 7 checks the typed role
against the real source when the problem layer depends on it. A fifth route, specific to defeating
Step 7 itself, is dependency paraphrase: describe a reused external method, dataset, or comparator
in plain language without naming the RW id or the entry's title/author, hoping the role audit never
triggers. This is closed in cycle 3: Step 1's `external_dependency_signal` is computed from the
problem-layer text alone, so a described-but-unnamed dependency still triggers Step 7, and if it
cannot be resolved to a specific `related_work.md` entry (including when `related_work.md` is
missing entirely — a sixth route, dependency deletion, that this same signal defeats because it
does not require `related_work.md` to exist in order to fire) the penalize-don't-skip floor still
applies rather than the audit being silently skipped. The residual evasion — describing a
dependency so thinly that even a semantic classifier cannot detect it as a dependency at all — is
not free: that thinness is exactly what the specificity/locatability penalties in "Metric intent"
already catch, so there is no describe-a-dependency-but-escape-all-scrutiny zone.

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
  extends/refutes) that are separately audited in Step 7 **when the problem layer's text
  references an RW id or an RW-covered source, OR when the problem layer's own text independently
  signals a semantic dependency on an external method/dataset/comparator** (Step 1's
  `external_dependency_signal`, computed without needing `related_work.md` to exist). If
  `related_work.md` is absent entirely, source resolution receives the appropriate penalty and Step
  7 contributes its penalize-don't-skip floor rather than being omitted — this applies whether the
  trigger was literal or semantic.

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
select the units that receive the full pipeline (Steps 1–7) versus a cheaper resolution-only pass
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
Step 3 (source resolution) and receive a risk-tiered, deterministically-aggregated score — see
Step 8's `resolution_only_score`. This bounds the number of Semantic Scholar/web/LLM calls to a
fixed function of artifact size while never letting overflow units default to a free pass or a
silent drop. Per §4, real single-paper artifacts typically carry 3–5 Observations and 2–4 Gaps, so
these caps sit well above the typical unit count per type and almost never bind in practice; they
exist as a deterministic cost ceiling and to close the overflow-padding route (Step 8), not as a
routine sampling step.

The semantic-dependency classification added to Step 1 below is a cheap internal text
classification (no external network call), so it is computed for **every** unit regardless of
whether that unit falls in `full_pass` or `resolution_only` — it does not draw on this step's
external-call budget, and it is what gates Step 7's audit independent of Step 0's sampling.

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
    "referenced_rw_ids": ["RW03"],           # literal RW## ids or RW-covered titles/authors named
    "external_dependency_signal": False,      # new: semantic dependency detected from text alone
    "dependency_signal_confidence": 0.0,      # new: 0.0-1.0
    "dependency_terms": [],                   # new: method/dataset/comparator phrases driving it
}
```

Citation extraction accepts parenthetical citations, DOI/arXiv/PMID strings, named references,
section refs such as `§1 Introduction`, and mixed evidence strings. `referenced_rw_ids` is
populated by matching `RW##` tokens or `related_work.md` entry titles/authors appearing in
`Existing attempts`, `Why they fail`, or `Evidence` text. If an Observation has `Evidence:
Abstract` or no parseable external source, create a record with `declared_refs=[]` and score it
through the missing/thin pathway.

**Semantic dependency signal (new in cycle 3).** For every unit whose text is a Gap's `Existing
attempts`/`Why they fail`, an Observation's `Evidence`/`Statement`, or the Key Insight's `Derived
from` bridge, run a text-only LLM classification — no `related_work.md` lookup, no external
network call — to catch dependencies described in plain language instead of by RW id/title:

```text
You are checking whether this ARA problem-layer text relies on a SPECIFIC external method,
dataset, comparator, tool, or prior finding, even if it is not cited by name/id.
Generic phrases like "prior work" or "existing studies" with no identifiable specific referent do
NOT count. A named approach, dataset, comparator, or finding described in enough detail to look
up (even without a citation) DOES count.

Text: {unit_text}
Adjacent context: {local_context}

Return JSON only:
{"external_dependency": true|false, "confidence": 0.0-1.0, "dependency_terms": ["..."]}
```

Validate against the schema; on malformed output, retry once with the standard invalid-JSON
correction prompt; on a second failure, set `external_dependency_signal=false,
dependency_signal_confidence=0.0` and flag `dependency_classification_fallback=true` (this cannot
silently over-trigger Step 7, only under-trigger it, and an under-trigger here still leaves the
literal `referenced_rw_ids` path as a backstop). This field is set independently of whether
`related_work.md` exists, so it cannot be neutralized by deleting or omitting that file, and it
does not require exact RW-id/title phrasing, so it is not defeated by paraphrase alone.

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

This `0.15` cap applies at the atomic-claim/bundle level — the specific assertion that was
contradicted. Step 8 adds a second, looser cap at the unit level so that a contradicted claim
cannot be diluted into invisibility by clean sibling claims sharing the same unit (see Step 8's
worked example).

### 7. Cross-layer role-drift audit (gated on RW dependency, literal or semantic)

Run this step for units where **either** condition holds (Step 1):

- `referenced_rw_ids` is non-empty (literal RW id/title/author match), or
- `external_dependency_signal` is `true` with `dependency_signal_confidence >= 0.6` (semantic
  dependency detected from the problem-layer text alone).

**Literal-match path.** If `referenced_rw_ids` resolves to a `related_work.md` entry, take that
entry's typed role (`imports` / `baseline` / `bounds` / `extends` / `refutes`) and its stated
`Delta`, and reuse the Step 5 support-judgment prompt with the role claim substituted in:

```text
ARA claim:
"This work's related-work graph asserts source {source} occupies the role '{role}'
 relative to this work, specifically: {delta_text}"
```

**Semantic-only path (new in cycle 3).** If only `external_dependency_signal` fired (no literal
RW id/title named), attempt to match the unit's `dependency_terms` against every
`related_work.md` entry's title/method/dataset keywords using the same resolution scoring as Step
3 (title/keyword-overlap match, not a fresh external lookup — `related_work.md` is already loaded
ARA content). If a match resolves at `>= 0.45` (the same "plausible source family" floor used in
Step 3), proceed with that entry exactly as the literal-match path above. This is what catches, for
example, a Gap's `Why they fail` that describes "the pairwise meta-analysis approach" without
naming it, when `related_work.md` has an entry for exactly that method tagged `baseline`.

**Unresolved in either path.** If `related_work.md` is absent, or no entry resolves at `>= 0.45`
for either path, do not skip: apply the penalize-don't-skip floor, `role_support = 0.0`, retained
in the denominator, exactly as an unresolved citation. This is the same floor whether the trigger
was literal or semantic, and whether the failure is "no `related_work.md`" (dependency-deletion
route) or "no matching entry" (dependency-paraphrase route past the point Step 7 can resolve it) —
both are closed the same way rather than being treated as a free pass.

**Worked example (paraphrase evasion closed).** A Gap's `Why they fail` reads: "Individual
head-to-head studies and pairwise meta-analyses compare limited assay pairs and cannot integrate
indirect evidence" — no RW id, no title, no author named. `referenced_rw_ids = []`, so cycle-2 B
would never trigger Step 7 here. Cycle-3 Step 1 classifies this text: `external_dependency_signal
= true`, `confidence = 0.8`, `dependency_terms = ["pairwise meta-analysis", "head-to-head
studies"]` — specific enough named methodologies to count, not generic "prior work." Step 7 then
matches `dependency_terms` against `related_work.md` and finds an entry titled "Pairwise
meta-analytic comparison of p-tau assays" tagged `baseline`. The role audit now runs against that
entry's real content instead of silently passing this Gap through untouched, which is what
happened in cycle 2.

Score with the same label/match machinery as Step 5, producing `role_support` per triggered unit
via `source_support()`:

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
- RW role dependency triggered (literal or semantic) but unresolved (`related_work.md` absent,
  or no entry resolves at `>= 0.45`): subtract an additional `0.05` (distinct from the ambiguity
  penalty above, since this is a dependency the problem layer itself created, whether it named the
  dependency explicitly or only described it).
- More than 30% of all units fall in `resolution_only` (Step 0 overflow): artifact-level
  multiplier `0.85`. Heavy reliance on the unaudited pass is itself a compression/padding signal —
  see "Why hard to Goodhart" — distinct from and multiplicative with the other multipliers above.

**Unit-level contradiction cap (new in cycle 3, worked example).** If any atomic claim inside a
unit carries a `contradicted` source judgment, the whole unit's score is capped at `0.35` — looser
than the `0.15` atomic-claim/bundle cap (siblings may be genuinely separate, independently-cited
assertions) but tight enough that a contradicted claim cannot vanish into a clean unit average.
Example: a unit with two atomic claims, `claim_1` bundle `= 0.15` (contradicted per Step 6's
worked example) and `claim_2` bundle `= 0.90` (clean, direct support). Plain mean `=
(0.15+0.90)/2 = 0.525` — a unit score that reads as roughly "mostly fine," burying the
contradiction. With the unit-level cap: `unit_score = min(0.525, 0.35) = 0.35`, correctly keeping
the unit in clearly-degraded territory without flattening it to the atomic-claim floor (`0.15`),
since `claim_2`'s independent support is still real and distinguishable from a unit where every
claim is contradicted.

**Resolution-only (overflow) scoring, made deterministic.** Per-citation resolution scores
(Step 3) aggregate to the unit level by `max` — matching the best-supporting-source logic used
throughout this metric — and the ceiling is risk-tiered so a numerically/causally loaded overflow
claim cannot float to the same ceiling as a low-stakes one with zero entailment checking:

```python
def resolution_only_score(unit):
    per_citation_scores = [resolve_citation_score(c) for c in unit.get("declared_refs", [])]
    resolution_score = max(per_citation_scores) if per_citation_scores else 0.0
    is_high_risk = unit.get("has_number") or unit.get("has_comparator") or unit.get("has_causal_verb")
    ceiling = 0.35 if is_high_risk else 0.5
    return min(ceiling, resolution_score)
```

Because Step 0's tie-break already sorts high-risk units (numbers/comparators/causal verbs) into
`full_pass` first, high-risk units land in `resolution_only` only when a single unit type has more
high-risk units than its cap — an atypical/adversarially inflated artifact, not a normal one — and
even then they are capped tighter (`0.35`, not `0.5`). Combined with the artifact-level
`overflow_fraction > 0.30` multiplier above, this bounds how much a large batch of unaudited units
can inflate the artifact mean: any single overflow unit contributes at most `0.5` (usually `0.35`)
with zero truthfulness verification, and pushing enough units into overflow to matter triggers the
`0.85` compression penalty on the whole artifact.

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

RW_ROLE_WEIGHT = 0.15  # only applied when Step 7 is triggered (literal or semantic)

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

def resolution_only_score(unit):
    per_citation_scores = [resolve_citation_score(c) for c in unit.get("declared_refs", [])]
    resolution_score = max(per_citation_scores) if per_citation_scores else 0.0
    is_high_risk = unit.get("has_number") or unit.get("has_comparator") or unit.get("has_causal_verb")
    ceiling = 0.35 if is_high_risk else 0.5
    return min(ceiling, resolution_score)

def unit_score(unit):
    if unit.get("resolution_only"):
        # Step 0 overflow: never audited past resolution, deterministically aggregated, risk-capped.
        return resolution_only_score(unit)
    claim_scores = [atomic_claim_score(c["source_judgments"]) for c in unit["atomic_claims"]]
    score = mean(claim_scores) if claim_scores else 0.0
    any_contradicted = any(
        j.get("support_label") == "contradicted"
        for c in unit["atomic_claims"] for j in c["source_judgments"]
    )
    if any_contradicted:
        score = min(score, 0.35)  # unit-level cap: prevents dilution by clean sibling claims
    if unit.get("missing_evidence_field"):
        score = min(score, 0.30)
    if unit.get("atomization_failed"):
        score = max(0.0, score - 0.05)
    return score

def m18_score(parsed_artifact):
    if not parsed_artifact.get("problem_present"):
        return 0.0
    units = parsed_artifact.get("units", [])
    if not units:
        return 0.0
    weighted = [(unit_score(u), UNIT_WEIGHTS.get(u["unit_type"], 0.50)) for u in units]
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
    resolution_only_count = sum(1 for u in units if u.get("resolution_only"))
    if resolution_only_count / len(units) > 0.30:
        multiplier *= 0.85  # overflow-heavy artifact: padding/compression signal

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
supports the sentence, and a single `contradicted` member hard-caps the whole bundle at `0.15` no
matter how strong a co-cited supporter is, closing the laundering path the worked example in Step 6
demonstrates was open in cycle 1. A second, looser `0.35` cap at the unit level (Step 8) closes a
narrower dilution path: a contradicted claim cannot be washed out into a passing unit average by
clean sibling claims sharing the same unit, while remaining distinguishable from a unit where
everything is contradicted. Missing or inaccessible evidence is penalized in the denominator,
which makes abstract-only compilation visibly weaker without fabricating certainty.

The role-drift audit (Step 7) closes a route specific to cross-layer dependency graphs — tagging a
source with a flattering typed role in `related_work.md` without the real source actually
occupying that role. As of cycle 3, the trigger for this audit is dual: a literal `RW##`/title
match, or a semantic dependency signal computed from the problem-layer text alone, independent of
whether `related_work.md` exists or what it contains. This closes two evasions at once —
paraphrasing away the RW id/title (the audit still fires on the described dependency) and deleting
`related_work.md` altogether (the signal doesn't need it to exist in order to trigger, and an
unresolved trigger is penalized, not skipped). The only residual evasion is describing a dependency
so thinly that it reads as generic ("prior work") rather than as a specific, checkable referent —
but that thinness is exactly what the specificity/locatability penalties already tax, so there is
no cost-free way to lean on unnamed prior work while avoiding all scrutiny of it.

The Step 0 audit-set cap plus deterministic tie-break sort bounds the external-call budget without
letting an adversary hide drift past the sampled window: priority favors claims with numbers,
comparators, and causal verbs — exactly where drift is cheapest to introduce and most consequential
— and overflow units are still scored, just at a capped, deterministically-aggregated ceiling
(`max` over per-citation resolution scores, tiered `0.35`/`0.5` by risk) rather than being silently
exempted or scored by an unspecified rule. An artifact that pushes more than 30% of its units into
this overflow pool — the only way to meaningfully exploit the ceiling at scale — additionally
triggers a whole-artifact `0.85` compression penalty, so padding an artifact with enough low-value
units to force real ones into the unaudited pass is a net loss, not a net gain.

The metric composes with the suite as an external-grounding check for the ARA's "why" layer.
Other metrics can judge completeness, causal structure, novelty, or internal traceability; M18
asks whether the cited prior literature really says what the problem statement says it says, and
whether the typed dependency graph, where it exists and is relied upon — explicitly or only by
description — tells the truth about the sources it names. That makes it especially valuable before
using the ARA for downstream literature synthesis, hypothesis generation, or automated research
planning.
