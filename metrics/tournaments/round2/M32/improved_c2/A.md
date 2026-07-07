## Changes (cycle 2)

This is a direct revision of `proposals/exp1.md` (RANK 1 in `critique_c1.md`), fixing the four
named weaknesses (a)–(d) without disturbing what the critique called "the strongest
Goodhart-resistance in the field" (tier-first branching, min-weighted aggregation, UNKNOWN
treated as at-least-as-demanding-as-ADJACENT):

- **(a) Missing "& verification status" axis** — exp1 scored only *validity* (tier × disclosure),
  never *verification* (did the paper check the method's own fitness — calibration, ablation,
  assumption test, benchmarking vs. ground truth — as opposed to reporting a results/accuracy
  number). Fixed in §3 Step 1 (extended extraction schema adds `verification_quote` per method)
  and §3 Step 5 (new `verification_bonus` term in the per-method score, capped and additive, never
  a substitute for disclosure — see rationale in §5).
- **(b) Ungrounded disclosure judgment** — `JUSTIFIED` in Step 3 was a bare LLM label with no
  textual anchor, so an LLM could assert "justified" without a real citation/argument in the text.
  Fixed by a `sanitize_field` quote-grounding pass (§3, new Step 3b) applied to every non-default
  semantic label the workflow produces — `JUSTIFIED` disclosure, `verification_quote`, and (new)
  `tier` labels asserted by the fallback classifier — before any of them reach the scorer.
- **(c) "Prominence" undefined** — §3 Step 1 now defines it operationally: a deterministic mention
  count over the concatenated artifact text, tie-broken by order of first appearance (§3, Step 1a).
- **(d) No backstop when external search is unavailable** — §3 Step 2 now distinguishes
  *infra failure* (the `[sem]` call itself errors/times out) from *search executed, zero relevant
  hits* (the latter is legitimately `UNKNOWN`, unchanged from cycle 1). Only the former triggers a
  self-contained fallback classifier, which is deliberately handicapped (cannot output `STANDARD`,
  must name a specific guideline/consensus source or default to `UNKNOWN`) so it cannot be used to
  launder a favorable score in place of real external grounding.

Everything else — the D6-orthogonality argument (§1–2), the tier-first/disclosure-second
branching order, the 0.4·mean + 0.6·min aggregation, and the numeric floors for
penalize-don't-skip (§4) — is carried over from exp1 unchanged, since the critique rated those the
strongest part of the design and none of the four weaknesses touch them.

---

# M32 — Method validity & verification status — Expansion 1, Cycle 2

## 1. What this metric is actually for

The one-line indicator is: *"Is the method sound — a widely-accepted validated method vs one
over-generalized beyond its warrant (and is that justified/explained)? [And, now made explicit:
did the paper itself verify the method's fitness for this use?]"* This is deliberately **narrower**
than general methodological rigor (verifier D6). D6 asks "was the chosen method executed
correctly" (adequate sample size, correct test given the data, blinding, controls, reproducible
protocol). M32 asks a logically prior pair of questions: **(i) is the chosen method itself the
right tool, validated for the context it's actually being applied in — or has the paper reached
for a technique whose validity is established elsewhere and quietly carried it over here; and
(ii) independent of (i), did the paper itself take any step to check that this specific method
holds up in this specific application (a calibration check, an assumption test, an ablation, a
benchmark against a gold standard) — as opposed to only reporting the results the method produced?**

A paper can pass D6 (impeccable execution) while failing M32 on either axis: a well-executed but
unwarranted method transplant (e.g. a diagnostic threshold validated on a MS-platform cohort
applied without comment to a Simoa-platform cohort) fails the validity axis; a method used exactly
within its established domain but never checked for fitness even where a cheap check was
available (e.g. no proportional-hazards diagnostic ever run for a Cox model, despite space to do
so) is weaker on the verification axis even though it would pass the validity axis outright. A
paper can also fail D6 (small n, no blinding) while passing both M32 axes (the method itself is
completely standard, squarely within its validated domain, and its fitness is checked). Keeping
D6 and M32 orthogonal is the reason M32 survived the assessment-critique ranking as net-new — this
revision preserves that separation deliberately (see §5) while now also honoring the literal
"verification status" half of the metric's own name, which cycle-1 critique correctly flagged as
missing.

### What it must reward
- Using a technique that is established/guideline-recommended **for this exact
  application** (same domain, population, scale, platform as the validation literature).
- Using a technique **beyond** its established domain, but doing so **transparently and with an
  argument** — an explicit statement of the extension plus a reason, citation, or sensitivity
  check for why it should still hold (e.g. "threshold derived on Simoa is applied to MSD data;
  §4.5 cross-platform correlation of r=0.91 supports transfer").
- Constraints/limitations text that names the *specific* method-context mismatch, not generic
  hedging.
- **A genuine method-fitness verification step** — internal or external validation, calibration
  check, benchmarking against a gold standard/ground truth, an ablation isolating whether a
  component is load-bearing, or a stated assumption test (e.g. Schoenfeld residuals for
  proportional hazards). This must be a check *on the method itself*, not a reported
  accuracy/results number — those belong to the evidence layer, not here.
- Internal coherence between what the method files claim to do and what the boundary-conditions
  section says the method is good for.

### What it must NOT reward
- Merely **naming** a well-known method ("we used a Cox model") — name-dropping a validated
  technique is not the same as using it within its validated envelope; the metric must check the
  *application context*, not just the *label*.
- A bare, contentless "no limitations" statement — per the artifact-shape notes this is itself a
  red flag (essentially every paper has some caveat), not a clean bill of health.
- Boilerplate limitations padding (generic "results may not generalize to other populations"
  sprinkled everywhere) used to simulate self-awareness while the *actual* substantive
  over-generalization goes unaddressed.
- A reported accuracy/results number, or a generic "our results were validated on a held-out set"
  sentence with no described mechanism, credited as method-fitness verification — the check must
  be traceable to a concrete procedure aimed at the method's own assumptions/behavior, not at
  overall predictive performance.
- Conflating this with general statistical rigor — adequate power, correct model diagnostics,
  proper blinding are D6's job; M32 must not re-score those or it becomes redundant.

### Failure modes / gaming routes this design must close
1. **Citation-as-shield gaming**: paper cites the original validation paper for a method by name,
   without addressing that its own use-case differs from that validation's scope. → closed by
   checking `stated_domain` against the domain the [sem] lookup actually finds validated, not just
   whether *a* citation exists.
2. **Boilerplate-caveat gaming**: stuffing constraints.md with generic disclaimers to look
   self-aware. → closed by requiring the disclosure-check to find *specific, quote-grounded*
   acknowledgment of *this* method/domain pairing, not any limitations text (§3 Step 3b).
3. **Silent-default gaming**: a paper using a totally standard method for a totally standard
   problem wins by default with zero justification language, which is *correct* — but the design
   must not accidentally also reward a paper that *needed* to justify an extension and didn't, just
   because both have "no justification prose." → closed by branching the score on the external
   validity tier first; justification is only required (and only scored) when the tier is anything
   other than STANDARD.
4. **Genre-forcing gaming**: dressing up a paper with method files from the wrong genre
   (`architecture.md` for a paper that trained no model) to appear methodologically sophisticated.
   → closed by a direct structural penalty (§3, step 4).
5. **Thin-artifact gaming**: relying on an abstract-only compile (no method file at all) to make
   the metric fall back to some neutral/default score. → explicitly forbidden by the hard
   constraint; unavailability is scored, and scored low (§3, step 5; §4 floors).
6. **Verification-claim laundering (new)**: an LLM extraction step asserting a method was
   "verified" or "calibrated" on the strength of surrounding confident prose, with no actual
   described check. → closed by requiring `verification_quote` to survive the same quote-grounding
   pass as disclosure (§3 Step 3b); an ungrounded verification claim is downgraded to "absent"
   before scoring.
7. **Fallback-tier laundering (new)**: when the external `[sem]` call is unavailable, a naive
   backstop could let the LLM's own confident world-knowledge assert `STANDARD` and effectively
   re-introduce self-report gaming exactly where external grounding was supposed to prevent it. →
   closed by handicapping the fallback classifier so it structurally cannot output `STANDARD` and
   must name a specific, checkable guideline/consensus source to output anything but `UNKNOWN`
   (§3 Step 2b).

## 2. How the assessment-critique notes reshape the design

The ledger note says this metric is net-new / tighter-scoped than D6 specifically because it
targets *method-context fit*, not *execution quality*. The cycle-1 critique additionally noted
that the metric's own name has two halves — *validity* and *verification status* — and exp1 only
built the first. Four design consequences now follow, all baked into the workflow below:

- The workflow's central validity operation remains an **external validity lookup** ([sem]), not
  an internal statistics check — this is what makes it genuinely different data than D6 consumes
  (D6 can be computed from the paper alone; M32's validity axis requires an outside reference
  point).
- The workflow's **verification** operation is deliberately internal (drawn from the artifact's
  own method files/constraints.md, not from an external lookup) — it asks whether the *paper*
  checked its own method's fitness, which is a fact about the paper, not about the literature. This
  keeps the two axes epistemically distinct: validity is "does the outside world agree this method
  belongs here," verification is "did the authors themselves stress-test that belief."
- The scoring function never inspects sample size, p-values, or study-design quality fields —
  doing so would re-derive D6 and blur the boundary the critique rewarded. The verification check
  is scoped identically: it asks *whether* a fitness check exists and *what it targets*, never
  *whether the check was executed well* (that residual quality question is D6's, not M32's).
- Because it's a "tighter facet," the workflow deliberately caps scope to **method-domain
  transfer validity + self-verification presence**, explicitly excluding adjacent-but-different
  questions (e.g. whether the *statistical test* was appropriate given the data's distribution —
  that's D6 territory) so the two verifiers stay decomposable and auditable independently.

## 3. Generation / compute workflow

**Artifact inputs** (from `logic/solution/`, §7 of the ARA shape):
- `constraints.md` → `boundary_conditions[]`, `assumptions[]` (id + text), `known_limitations[]`
  (name + text), optional `data_quality_caveats[]`.
- Zero or more method files (`study_design.md`, `method.md`, `architecture.md`, `algorithm.md`,
  `heuristics.md`, ...) → raw markdown text each.
- Filenames themselves are a signal (genre-fit check, step 4).

No other artifact section is read by this metric (kept within primary-artifact scope, §7 only).

### Step 1 — Method identification + verification-mention extraction (local LLM extraction, no external call)
Concatenate `constraints.md` + all present method files. Run:

> **Prompt (extraction):**
> "You are extracting method identifications from a scientific paper's method-layer artifact.
> Given the text below, list every named technique/method/instrument/model/statistical-test/
> algorithm the paper actually *uses to produce its results* (not methods only mentioned as
> background or comparison baselines). For each, output: `name` (canonical name), `role` (one
> sentence — what it's used for here), `stated_domain` (the population/data-type/platform/scale it
> is applied to *in this paper*, exactly as stated), `verification_quote` (a verbatim span from the
> text describing a check ON THIS METHOD's fitness — calibration, an assumption test, an ablation
> isolating a component, benchmarking against a gold standard/ground truth — or `null` if no such
> check is described; a reported accuracy/results number alone does NOT count and must not be
> quoted here). Output a JSON list. If method files are non-empty but you cannot identify any
> concrete method, output `[]` and set `extraction_failed: true`.
> TEXT: {constraints.md + method files, concatenated}"

Output: `methods: list[{name, role, stated_domain, verification_quote}]`, `extraction_failed: bool`.

### Step 1a — Prominence ranking (deterministic, fixes cycle-1 weakness (c))
"Prominence" is defined operationally, not left to judgment:

```python
import re

def prominence_rank(methods: list[dict], full_text: str) -> list[dict]:
    """Rank extracted methods by mention count in the concatenated artifact text
    (case-insensitive, whole-word/phrase match on `name`), descending; ties broken
    by order of first appearance in the Step-1 output list (which itself follows
    the paper's own textual order). Return the top 3."""
    def mention_count(name: str) -> int:
        pattern = re.escape(name.strip())
        return len(re.findall(pattern, full_text, flags=re.IGNORECASE))

    indexed = list(enumerate(methods))  # (original_order, method)
    ranked = sorted(
        indexed,
        key=lambda pair: (-mention_count(pair[1]["name"]), pair[0]),
    )
    return [m for _, m in ranked[:3]]
```

Only the top-3-by-prominence methods proceed to Steps 2–3; this caps external-lookup cost while
making the selection rule auditable and non-arbitrary (a strict function of the text, not a
free judgment call).

### Step 2 — [sem] external validity-tier lookup (per prominence-ranked method)
For each of the top-3 methods, issue a semantic-scholar / undermind query:

> **Query:** `validation OR guideline OR benchmark of "{method.name}" for "{method.stated_domain}"`

Then classify the returned abstracts/snippets with:

> **Prompt (validity tier):**
> "Given these search results, classify whether \"{method.name}\" is established/validated
> practice specifically for \"{method.stated_domain}\" (not just validated in general). Choose
> exactly one: `STANDARD` (multiple independent sources show this exact application is routine or
> guideline-recommended); `ADJACENT` (well-validated for a related-but-different
> population/scale/platform/regime, and its use *here* would be an extension); `NOVEL_OR_CONTESTED`
> (no clear validation literature for this exact application, or literature shows active
> disagreement/known failure modes for it); `UNKNOWN` (insufficient relevant results to judge —
> absence of evidence is NOT evidence of validity, treat as requiring justification same as
> ADJACENT). Respond with the label plus one supporting sentence and a verbatim snippet from the
> search results backing the label."
> SEARCH RESULTS: {sem output}"

Output per method: `tier ∈ {STANDARD, ADJACENT, NOVEL_OR_CONTESTED, UNKNOWN}`, `tier_evidence`
(the supporting snippet), `tier_source = "SEM"`.

### Step 2b — Self-contained fallback when the [sem] call itself is unavailable (fixes cycle-1 weakness (d))

This is distinct from a `[sem]` call that *executes successfully and returns nothing relevant* —
that case is already handled correctly by cycle 1's `UNKNOWN` tier and is left unchanged (it is
real evidence: absence of a literature footprint). The fallback below only triggers when the
external call itself **fails to execute** (API error, timeout, index unavailable), so that a niche
but genuinely well-attested method doesn't get penalized purely by infrastructure flakiness.

> **Prompt (fallback tier — deliberately handicapped):**
> "The external literature search for \"{method.name}\" used for \"{method.stated_domain}\" is
> currently unavailable. Using only your own knowledge, judge this conservatively. You may output
> `ADJACENT` or `NOVEL_OR_CONTESTED` ONLY if you can name a *specific*, checkable guideline body,
> consensus statement, standards document, or canonical benchmark paper that governs this exact
> method/domain pairing (name it in `tier_evidence`). You may NEVER output `STANDARD` from
> memory alone — a favorable-sounding recollection of a method's fame in general is not
> domain-specific external evidence. If you cannot name a specific, checkable source, output
> `UNKNOWN`. Fame is not warrant — respond based on named, checkable evidence only."

Output per method (fallback path only): `tier ∈ {ADJACENT, NOVEL_OR_CONTESTED, UNKNOWN}`,
`tier_evidence` (the named source, or empty if `UNKNOWN`), `tier_source = "FALLBACK"`.

`tier_source` is carried through to the final output payload (not into the numeric score itself)
so that suite-level orchestration can, if it chooses, flag or down-weight `FALLBACK`-sourced
assessments for later re-verification once the external lookup is back online — but the score
computed *now* is always a real number either way (penalize-don't-skip is satisfied regardless of
which path produced the tier).

### Step 3 — Disclosure/justification check (only for methods with tier ≠ STANDARD)

> **Prompt (disclosure):**
> "Method \"{method.name}\" is used here for \"{method.stated_domain}\", which is not clearly
> established practice for that exact application (tier: {tier}). Does the constraints/limitations
> text below explicitly acknowledge that THIS SPECIFIC method-application pairing goes beyond
> established validation? Answer exactly one: `JUSTIFIED` (acknowledged, AND a reason, citation,
> sensitivity analysis, or argument is given for why it should still hold — quote the specific
> reason verbatim); `ACKNOWLEDGED_UNJUSTIFIED` (acknowledged, but no reason given for proceeding
> anyway); `SILENT` (no acknowledgment of this specific concern — generic unrelated hedging does
> not count). If `JUSTIFIED`, include the supporting verbatim span in `justification_quote`.
> CONSTRAINTS TEXT: {full constraints.md text}"

Output per non-STANDARD method: `disclosure ∈ {JUSTIFIED, ACKNOWLEDGED_UNJUSTIFIED, SILENT}`,
`justification_quote` (verbatim, or empty).

### Step 3b — Quote-grounding pass (fixes cycle-1 weakness (b))

Every non-default semantic label produced above — `disclosure = JUSTIFIED`, a non-null
`verification_quote`, and any `FALLBACK` tier other than `UNKNOWN` — must survive a grounding
check against the actual source text before it is allowed to reach the scorer. An unmatched claim
is a hallucinated assertion, not evidence, and is downgraded to its conservative default.

```python
def _normalized(s: str) -> str:
    return " ".join(s.lower().split())

def is_quote_grounded(quote: str, source_text: str, min_len: int = 8) -> bool:
    """Cheap, efficient grounding check: normalized substring containment first
    (handles the overwhelming majority of real quotes exactly); falls back to a
    single whole-string difflib ratio only on a substring miss, rather than the
    O(n * windows) sliding-window scan flagged as inefficient in exp3's design."""
    if not quote or len(quote.strip()) < min_len:
        return False
    q, s = _normalized(quote), _normalized(source_text)
    if q in s:
        return True
    from difflib import SequenceMatcher
    return SequenceMatcher(None, q, s).ratio() >= 0.6  # coarse fallback for light paraphrase

def sanitize_field(value, quote: str, source_text: str, default):
    """Downgrade any non-default field lacking a grounded quote to its default."""
    if value == default:
        return value, None
    if is_quote_grounded(quote, source_text):
        return value, quote
    return default, None

# Applied per method:
#   disclosure, justification_quote = sanitize_field(disclosure, justification_quote,
#                                                      constraints_text, default="SILENT")
#   verification_present = bool(verification_quote) and is_quote_grounded(
#                                                      verification_quote, full_text)
#   if tier_source == "FALLBACK" and tier != "UNKNOWN":
#       tier, tier_evidence = sanitize_field(tier, tier_evidence, general_knowledge_text=None,
#                                             default="UNKNOWN")  # fallback claims need a named,
#                                             # checkable source string in tier_evidence itself;
#                                             # an empty/generic tier_evidence downgrades to UNKNOWN.
```

This closes weakness (b) directly (`JUSTIFIED` cannot survive without a source-matched span) and
also closes gaming route 6 (verification-claim laundering): a `verification_quote` that doesn't
actually appear in the text is treated as no verification at all.

### Step 4 — Structural / availability checks (deterministic, no LLM)
- `constraints_missing`: `constraints.md` absent entirely → per artifact shape this file is
  *always* present; its absence is a hard-floor artifact-compilation failure.
- `bare_no_limitations`: `known_limitations` section present but contains only a negation
  ("no limitations were identified" / empty) with zero substantive bullets.
- `genre_mismatch`: a method file's apparent genre contradicts what the paper did (e.g.
  `architecture.md`/`algorithm.md` present with content describing training a model, but no
  model-training evidence anywhere in `role` fields extracted in Step 1; or a pure statistical-
  synthesis paper carrying a `training.md`). Detected via a cheap LLM/keyword check: does any
  extracted method's `role` involve model training/inference, matching the presence of
  architecture/algorithm files? Flag boolean.
- `abstract_only_floor`: only `constraints.md` present, zero method files, and `extraction_failed`
  or `methods == []` — the documented "stark, easily-detected floor case."

### Step 5 — Deterministic scoring

```python
from dataclasses import dataclass
from enum import Enum

class Tier(str, Enum):
    STANDARD = "STANDARD"
    ADJACENT = "ADJACENT"
    NOVEL_OR_CONTESTED = "NOVEL_OR_CONTESTED"
    UNKNOWN = "UNKNOWN"

class Disclosure(str, Enum):
    JUSTIFIED = "JUSTIFIED"
    ACKNOWLEDGED_UNJUSTIFIED = "ACKNOWLEDGED_UNJUSTIFIED"
    SILENT = "SILENT"
    NOT_APPLICABLE = "NOT_APPLICABLE"  # only for STANDARD-tier methods

@dataclass
class MethodAssessment:
    name: str
    tier: Tier
    disclosure: Disclosure
    verification_present: bool  # NEW: quote-grounded per Step 3b
    tier_source: str = "SEM"    # "SEM" | "FALLBACK", audit-only, does not itself gate the score

# Per-method base score: branches on tier first (closes "silent-default gaming", failure mode 3),
# then on disclosure quality (closes "citation-as-shield" and "boilerplate-caveat" gaming).
# Unchanged from cycle 1 -- the critique rated this table's structure as the strongest in the field.
_SCORE_TABLE = {
    (Tier.STANDARD, Disclosure.NOT_APPLICABLE): 1.00,
    (Tier.ADJACENT, Disclosure.JUSTIFIED): 0.85,
    (Tier.UNKNOWN, Disclosure.JUSTIFIED): 0.80,
    (Tier.NOVEL_OR_CONTESTED, Disclosure.JUSTIFIED): 0.70,
    (Tier.ADJACENT, Disclosure.ACKNOWLEDGED_UNJUSTIFIED): 0.40,
    (Tier.UNKNOWN, Disclosure.ACKNOWLEDGED_UNJUSTIFIED): 0.35,
    (Tier.NOVEL_OR_CONTESTED, Disclosure.ACKNOWLEDGED_UNJUSTIFIED): 0.25,
    (Tier.ADJACENT, Disclosure.SILENT): 0.15,
    (Tier.UNKNOWN, Disclosure.SILENT): 0.15,
    (Tier.NOVEL_OR_CONTESTED, Disclosure.SILENT): 0.00,
}

# NEW: verification bonus (fixes cycle-1 weakness (a)). Flat, capped, additive -- never a
# substitute for disclosure. A method that is silently over-extended AND happens to include a
# real fitness check for itself is less risky than one with neither, but it is still an
# undisclosed over-generalization; the bonus moves it from e.g. 0.00 -> 0.10, not into a passing
# range. Verification and disclosure are independent facts about the paper and are scored as such.
_VERIFICATION_BONUS = 0.10

def per_method_score(m: MethodAssessment) -> float:
    base = _SCORE_TABLE[(m.tier, m.disclosure)]
    if m.verification_present:
        base = min(1.0, base + _VERIFICATION_BONUS)
    return base

def aggregate_methods(assessments: list[MethodAssessment]) -> float:
    """Blend mean and min, weighted toward min, so one silently-mismatched method
    cannot be diluted away by several fine ones (closes hide-the-bad-method gaming)."""
    if not assessments:
        return 0.0
    scores = [per_method_score(m) for m in assessments]
    mean_s, min_s = sum(scores) / len(scores), min(scores)
    return 0.4 * mean_s + 0.6 * min_s

def score_m32(
    constraints_present: bool,
    bare_no_limitations: bool,
    genre_mismatch: bool,
    abstract_only_floor: bool,
    extraction_failed: bool,
    assessments: list[MethodAssessment],
) -> float:
    """
    Real scoring function against the §7 logic/solution/ artifact shape.
    Returns a value in [0.0, 1.0]. Never returns None/NA — unavailable or thin
    inputs are penalized in-band per the hard constraint (penalize, don't skip).
    """
    # Hard floor: constraints.md is documented as always-present; its absence is a
    # compilation-level failure, not a neutral "can't assess" case.
    if not constraints_present:
        return 0.0

    # Documented floor case: abstract-only source, nothing to verify against.
    # Unavailability of method detail IS the score, not a skip.
    if abstract_only_floor:
        return 0.05

    # Non-empty method files but nothing extractable: thin/degenerate artifact.
    if extraction_failed or not assessments:
        return 0.15

    base = aggregate_methods(assessments)

    # Structural penalties stack after the semantic score; they catch degenerate
    # or misleading artifacts even if the LLM steps above were fooled.
    if bare_no_limitations:
        base -= 0.30
    if genre_mismatch:
        base -= 0.25

    return max(0.0, min(1.0, base))
```

### Worked examples

**che26-style (unchanged validity axis, cycle-1 example, now with verification axis added):**
- `constraints_present = True`, one method file (`study_design.md`).
- Method extracted: `{"name": "P-score relative ranking vs p181_IA baseline",
  "stated_domain": "blood-based p-tau biomarkers, MS/Simoa/MSD/Lumipulse platforms pooled",
  "verification_quote": null}` — no fitness check on the cross-platform pooling itself is
  described anywhere (only the results of the pooling are reported).
- [sem] tier lookup → `ADJACENT` (cross-platform pooling is a known extension point, not routine),
  `tier_source = "SEM"`.
- Disclosure check against constraints.md's "Known limitations (§4.5): batch effects... may still
  exist" → names the cross-platform concern but gives no correction/sensitivity check →
  `ACKNOWLEDGED_UNJUSTIFIED`, quote-grounded (the §4.5 sentence itself matches verbatim) → base
  per-method score 0.40. `verification_present = False` → no bonus → final 0.40.
- No genre mismatch, no bare-no-limitations, one method only → aggregate = 0.4·0.40 + 0.6·0.40 =
  0.40. **Final score 0.40/1.0** — unchanged from cycle 1, since this paper never claimed a
  verification step either.

**New worked example illustrating the verification axis:**
- A paper applies a Cox proportional-hazards model (`stated_domain` matches its guideline-backed
  use case) → tier `STANDARD`, disclosure `NOT_APPLICABLE` → base 1.00.
- `method.md` states: *"Schoenfeld residual test confirmed no significant departure from the
  proportional-hazards assumption (p=0.41, Fig. S3)."* → `verification_quote` set, and the quote
  is found verbatim in the source text → `verification_present = True`.
- Per-method score = min(1.0, 1.00 + 0.10) = **1.00** (already capped — verification is icing on an
  already-fully-validated method, not a lever to exceed the ceiling; this correctly reflects that
  verification cannot make a method "more standard," only more trustworthy where trust was already
  incomplete).
- Contrast: the same Cox model used on a population outside its guideline scope (`ADJACENT`),
  disclosed and justified (`JUSTIFIED`, base 0.85), *and* with the same Schoenfeld-residual quote
  present → 0.85 + 0.10 = **0.95** — here the bonus is meaningful, because verification is doing
  real work offsetting a genuine extension, exactly the case cycle-1 critique wanted captured.

## 4. Why penalize-don't-skip is honored throughout
Every branch in `score_m32` terminates in a numeric score, never `None`/`NA`:
- Missing `constraints.md` (an artifact-shape violation, since it's documented as mandatory) → 0.0.
- Abstract-only compiles (documented floor case in the shape notes) → 0.05, not skipped.
- Non-extractable method content despite non-empty files → 0.15, not skipped.
- `UNKNOWN` validity tier (search returned nothing usable) is explicitly *not* mapped to a neutral
  score — it is scored as at least as demanding as `ADJACENT` (never more lenient than not knowing),
  because absence of external evidence must not read as evidence of validity. This holds
  identically whether `UNKNOWN` came from a real `[sem]` null result or from the fallback
  classifier defaulting when it couldn't name a specific source (§3 Step 2b) — the workflow never
  blocks or waits on external-service availability; it always resolves to a number now.
- An ungrounded `verification_quote` (fails Step 3b) is treated as `verification_present = False`,
  i.e. no bonus — never as an error state or a skipped field.

## 5. Why this is hard to Goodhart, and how it composes with the rest of the suite

- **External grounding breaks self-report gaming on validity.** The validity tier comes from a
  semantic-scholar/undermind lookup, not from parsing the paper's own confident prose. A paper
  cannot make itself look STANDARD just by asserting a method is standard — and, new in this
  revision, neither can it do so by hoping the external service is briefly unavailable: the
  fallback path (§3 Step 2b) is structurally forbidden from ever outputting STANDARD and requires a
  named, checkable source for anything better than UNKNOWN, so an outage cannot be exploited as a
  softer scoring path.
- **Disclosure ≠ mention, and now neither does verification.** The Step 3 prompt requires
  acknowledgment of the *specific* method/domain pairing plus a *reason*; the Step 3b grounding
  pass additionally requires that reason (and any verification claim) to be a real, matchable span
  in the source text — generic hedging, boilerplate caveats, or a fabricated "we verified this"
  sentence with no textual anchor cannot satisfy `JUSTIFIED` or `verification_present`, closing
  both the boilerplate-caveat route and the new verification-laundering route.
- **Verification is additive, never a substitute for disclosure.** A silently over-extended method
  that happens to include a real fitness check still scores low (e.g. 0.00 + 0.10 = 0.10 for
  NOVEL_OR_CONTESTED/SILENT) — the bonus cannot be used to buy back the much larger penalty for
  never disclosing the extension at all, which keeps the "&verification status" addition from
  accidentally opening a new escape hatch around the disclosure requirement that was cycle-1's
  centerpiece defense.
- **Min-weighted aggregation prevents dilution.** A paper can't bury one badly-extended, silently-
  used method inside several genuinely standard ones and average its way to a good score — the
  0.6-weighted min term ensures the worst offender dominates. Prominence ranking (§3 Step 1a) is
  now a fixed, auditable function of mention count rather than an undefined judgment call, so this
  defense can't be quietly weakened by cherry-picking which 3 methods get evaluated.
- **Cheap structural tripwires sit under the semantic layer.** `constraints_missing`,
  `bare_no_limitations`, `genre_mismatch`, and `abstract_only_floor` are non-LLM, hard-to-spoof
  checks on document structure that floor the score independent of how the semantic steps land —
  so even if an adversarial artifact fooled the LLM extraction/classification, gross degeneracy
  (missing file, wrong genre, empty limitations) still tanks the score.
- **Orthogonal to D6 by construction, on both axes.** The workflow never reads sample size,
  statistical test choice, blinding, or reproducibility fields — only method identity, its
  external validity tier for the stated application, whether that gap is disclosed/justified, and
  whether the paper itself checked the method's fitness. A paper can score high on D6
  (well-executed) and low on M32 (wrong tool for the domain, undisclosed, unverified), or vice
  versa; the two are measuring different failure surfaces and a suite score that includes both
  cannot be satisfied by optimizing either one alone. This preserves the "net-new / tighter-scoped"
  edge that put M32 in the top 10, while now actually covering both halves of its own name.
- **Composes as a multiplicative-style gate, not an additive bonus.** Because a single silently-
  contested method can floor the aggregate near 0, M32 is best combined with the rest of the suite
  as a term that can veto an otherwise-strong composite score, rather than one more point among
  many that can be traded off — consistent with "good science" requiring the *method itself* be
  sound (and its fitness checked) as a near-necessary condition, not merely a nice-to-have.
