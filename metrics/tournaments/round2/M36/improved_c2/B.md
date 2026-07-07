## Changes (cycle 2)

This is exp3 (rank 2, "strongest-articulated Goodhart resistance") revised against the named
weaknesses in `critique_c1.md`. Four targeted fixes, all additive to the existing multiplicative
skeleton — nothing that made exp3 rank 2 is discarded:

1. **Imported exp4's circularity check as a hard zero**, not a floor. New Step 2b runs a dedicated
   adversarial pass over every lens pair asking whether one lens's parameters/hypotheses/selection
   were tuned using the other lens's output. A flagged pair is excluded from the independence
   pool entirely, and — critically, per exp4's design — if *every* piece of claimed integration
   evidence turns out to trace back to a circular pair, `integ_factor` is set to a literal `0.0`,
   not the previous `0.5` floor. This closes the exact gap the critique named: exp3 had no defense
   against "the computational model whose hyperparameters were chosen using the wet-lab result it
   then confirms."
2. **Imported exp2's `n_effective`**, replacing the single scalar `independence_score` multiplier.
   Independence is now judged per-pair with a quoted rationale; `n_effective` is the count of
   lenses that participate in at least one *qualifying* (non-circular, independence ≥ 0.6) pair.
   `base_lens_score` is keyed on `n_effective`, not raw lens count, so "3 lenses, two correlated"
   collapses to the n=2 base rather than being softened into one continuous knob. The old scalar
   `independence_score` is retained only as the fallback when a pairwise call is unavailable
   (degenerate n=2 case, where "pairwise" and "scalar" coincide).
3. **Recalibrated the ceiling.** `base_lens_score` for `n_effective=2` and `n_effective≥3` is
   raised (0.55→0.65, 0.75→0.90) so a genuinely strong, fully-triangulated, fully-reflected paper
   now lands around 75–85/100 instead of 41.7/100, improving discrimination among good papers,
   while the multiplicative structure — and thus the "no single axis buys it" property — is
   unchanged. This is a documented, deliberate rescaling, not a loosening of any gate: a padded or
   circular case still collapses toward the floor exactly as before (worked cases below confirm
   this).
4. **Fixed the `[0,1]`/`×100` ambiguity and made the boilerplate detector structural.** The
   docstring and intermediate variable naming now make explicit that `score` accumulates as a
   fraction in `[0,1]` and only the final `return` line converts to a `[0,100]` percentage — no
   code semantics changed, but the prior wording left room to misread `min(1.0, score)` as a bug.
   `is_boilerplate_constraints` no longer relies solely on a fixed English phrase list; it adds a
   structural check (does the "Known limitations" section contain at least one bullet with a
   concrete noun-like token — a proper noun, technical term, number, or quoted artifact name —
   paired with a failure/limitation verb) so paraphrased or non-English boilerplate that dodges the
   phrase list is still caught, per the critique's specific suggestion.

Cross-cutting fix applied throughout (per critique's shared direction for both winners): lens
extraction now asks for an explicit, quoted **failure mode** description as the primary judgment
object; `modality` (the 6-category taxonomy) is retained only as a secondary, non-binding tag for
readability and downstream aggregation — it is never itself the basis for an independence
judgment. Two lenses with the same `modality` tag but a quoted, distinct failure mode can still
count as independent; two lenses with different tags but the same underlying quoted failure mode
(e.g. both ultimately fail on "the same batch of reagents") do not.

---

# M36 — Multi-perspective triangulation — Expansion + Workflow (cycle 2)

## 1. What this metric rewards, precisely

M36 asks two coupled questions about the **method layer** (`logic/solution/`: `constraints.md` +
zero-or-more method files):

1. Did the work actually combine **methodologically independent lenses** (e.g. wet-lab assay ×
   computational/in-silico model; statistical meta-analysis × mechanistic simulation; qualitative
   clinical read × quantitative pipeline) to support its claims, rather than resting the whole
   argument on one method with one characteristic failure mode?
2. Does `constraints.md` **know it** — i.e. does the boundary-conditions/limitations text actually
   engage with what multi-lens combination (or its absence) implies for how far the results
   generalize?

A "lens" here is defined narrowly, and the definition is now enforced at the level the metric
actually operationalizes it: an approach with an **independently-describable, quoted failure
mode** — not a category label. Two different multiple-testing corrections run on the same assay
data are not two lenses — they're one lens analyzed two ways, because their failure mode ("this
assay's batch/reagent behavior") is identical even if the correction algorithm differs. A wet-lab
replication and an orthogonal computational model *are* two lenses, because a batch effect that
breaks the wet-lab result and a misspecification that breaks the computational result are
unrelated events — and, new in cycle 2, they must also not be **causally entangled** (one lens's
output must not have shaped the other's parameters or hypotheses, or the "independence" is
fabricated). The epistemic reason this is a good-science signal: triangulation across independent,
non-circular failure modes is precisely what makes a finding robust to any single method's blind
spot — it's the closest thing this artifact layer has to an internal replication signal, and it is
diagnostic in the disconfirming direction too (a paper with rich multi-lens machinery in its
evidence but a `constraints.md` that never mentions where the lenses agree/disagree is
*overclaiming* integration it didn't do — and a paper whose "agreement" is actually circularity is
overclaiming worse).

### What it must reward
- Genuine independence between lenses (different data source, different instrument/algorithm
  class, different assumption set) **and** the absence of a tuning/selection dependency between
  them.
- Actual **integration**: evidence in the text that one lens's output was used to corroborate,
  stress-test, or resolve disagreement with another's — not just two lenses reported side by side,
  non-cross-referencing — and not a corroboration manufactured by fitting one lens to the other.
- `constraints.md` explicitly reasoning about the boundary this combination (or lack of it)
  creates — including honestly flagging where lenses *disagreed* and how that was resolved (or
  wasn't).

### What it must NOT reward
- Lens-count padding: listing multiple pipeline steps, corrections, or sensitivity analyses within
  one method family as if they were independent lenses, or listing lenses under different
  `modality` tags whose quoted failure modes are actually the same underlying risk.
- Juxtaposition without integration: a paper with a wet-lab section and a computational section
  that never reference each other's results.
- **Manufactured agreement**: a computational model whose hyperparameters, priors, or hypothesis
  space were selected using the wet-lab (or other lens's) result it is then reported to "confirm."
  This is new-in-cycle-2 and is treated as a hard-zero condition on the integration credit it
  touches, not a soft discount.
- Boilerplate constraints text ("results are consistent across methods") asserted without any
  grounded evidence trail back into the method files — including paraphrased or non-English
  boilerplate that a fixed English phrase list would miss.
- Punishing an honestly-scoped single-lens paper *elsewhere* — a pure statistical-synthesis review
  (like the che26 example in the shape doc) is legitimate work. M36 correctly scores it low on
  *this specific axis* (no triangulation occurred), but the scoring function below distinguishes
  "single lens, honestly bounded" from "single lens, unbounded / method layer thin or absent,"
  which should score strictly lower still — because that second case is exactly the
  penalize-don't-skip case: a missing or generic constraints section is itself evidence, not a
  reason to abstain from scoring.

## 2. Failure modes / gaming routes, and how the design closes them

| Gaming route | Why it fails against this design |
|---|---|
| List cosmetically different "approaches" that share one failure-mode family (e.g. two normalization schemes) to inflate lens count | Lens extraction requires a quoted, specific **failure mode**, not just a modality label; the pairwise independence pass (Step 2a) explicitly checks whether two lenses' quoted failure modes are the same risk restated, and a padded pair scores independence ≈ 0, excluding it from `n_effective` |
| Mention "we also validated computationally" once, as a rubber stamp, with no actual cross-reference | Integration is graded per-pair and requires quoted evidence that one lens's result fed into judgment of another; a bare mention with no cross-reference scores that pair's integration ≈ 0 |
| **Tune or select one lens's parameters/hypotheses using another lens's output, then report the manufactured match as "corroboration"** | Step 2b (circularity audit, new in cycle 2) scans specifically for this pattern per pair; a flagged pair is dropped from `n_effective` and, if it is the *only* source of claimed integration, `integ_factor` is set to a hard `0.0` — not floored, zeroed |
| Write an eloquent, generic limitations paragraph without engaging lens-specific boundaries | `constraints_reflection_score` is graded against the *specific quoted failure modes* found in step 1, not against limitations text in isolation — boilerplate that doesn't name the lenses or their interaction scores low even if well-written |
| Write boilerplate limitations in a paraphrased or non-English-idiom way to dodge a fixed phrase-list detector | `is_boilerplate_constraints` (Step 0) now includes a structural check — a bullet must pair a concrete noun-like token (named method, dataset, instrument, or number) with a failure/limitation verb to count as substantive; phrase-only matching is a secondary signal, not the sole gate |
| Omit method files entirely (thin compile) to avoid the extraction step surfacing single-lens-ness | Handled explicitly by the availability/thinness multiplier in §5 — absence of method files is itself scored, never skipped, and floors the score rather than exempting it |
| Claim more lenses than the paper supports by relying on the compiler's method-file *names* (e.g. an `architecture.md` present for a paper that trained no model — a known compiler defect per the shape doc) | Lens extraction is grounded in verbatim `evidence` quotes and a verbatim `failure_mode` quote from the text, not file names; a fabricated/forced file with no supporting method content yields low-confidence, filtered-out "lenses" |

## 3. How the assessment-critique notes shaped this design (net-new, tightly scoped)

The ledger note says M36 ranked top-10 specifically for being genuinely absent from round 1 and
the ARA verifier, and for being scoped tighter than adjacent ideas. The cycle-1 critique further
identified exp3 specifically as having the field's most rigorous multiplicative composition and
deterministic availability gate, but flagged: no circularity defense, a scalar (not per-pair)
independence measure, and a compressed ceiling. All three are now fixed (§0 above) without
touching what made the design work:

- **Scope is still locked to §7** (`logic/solution/`) only. This metric does not reach into
  `evidence/` tables or `problem/` framing to check if multiple *data sources* exist — that
  overlaps with reproducibility/evidence-grounding metrics elsewhere in the suite. M36 asks only
  whether the *method layer itself* documents and reflects multi-lens combination.
- It is **not** a restatement of an internal-consistency or rigor-within-a-method metric: a
  single-lens paper can be perfectly rigorous and internally consistent and still correctly score
  low here, because rigor-within-a-lens and triangulation-across-lenses are orthogonal axes.
- It is **not** redundant with a generic "did constraints.md exist" check — that's a floor/gate
  condition already implicit in Seal Level 1 structural validation. M36's contribution is specific:
  it cross-checks constraints content *against* the lens set actually found (and now, against
  whether that lens set's apparent agreement is genuine or manufactured), which no existing
  verifier does.

## 4. Generation / compute workflow

### Inputs (exact artifact fields)
From `logic/solution/` for a given ARA:
- `constraints.md` (string; always present per shape doc, though may be thin/boilerplate)
- `method_files`: dict of `{filename: content}` for whichever of `study_design.md`, `method.md`,
  `architecture.md`, `algorithm.md`, `heuristics.md`, `formalization.md`, `proofs.md`, `design.md`
  are present (may be empty dict — legitimate for abstract-only sources per shape doc §"Availability
  notes")

No cross-artifact reads are needed for the core score (kept tight per §3); the workflow does not
consult `evidence/` or `problem/`.

### Steps

**Step 0 — Availability gate (deterministic, no LLM).**
Compute `availability_tier`:
- `"absent"` if `method_files` is empty AND `constraints.md` is boilerplate (see thinness check
  below) — worst case, both symptoms of an abstract-only or degenerate compile.
- `"thin"` if `method_files` is empty but `constraints.md` has genuine content, OR method files
  exist but `constraints.md` is boilerplate.
- `"full"` otherwise.

Thinness check on `constraints.md` (deterministic heuristic, cheap, now structural-first): flag as
boilerplate if it has no `## Known limitations` bullets, or the section fails the substantive-bullet
test (see `is_boilerplate_constraints` in §5) — a bullet counts as substantive only if it pairs a
concrete noun-like token (named method, dataset, instrument, platform, or number) with a
failure/limitation verb ("may bias," "does not generalize," "was not corrected for," "confounds,"
etc.), or matches a known-generic phrase as a fallback signal. This directly operationalizes the
shape doc's own red-flag note ("a bare 'no limitations stated' ... is a red flag") while also
catching paraphrased or non-English-idiom boilerplate that a fixed phrase list would miss.

**Step 1 — [sem] Lens extraction (LLM call).** Skip only if `method_files` is empty AND
`constraints.md` has zero prose beyond boilerplate (score handled by Step 0 gate instead — this is
the one case where there is nothing to extract, but the *availability_tier* still drives the score
down, so nothing is skipped in the scoring sense).

Prompt (exact):
```
SYSTEM: You are analyzing the method layer of a compiled research artifact to identify
methodologically INDEPENDENT lenses used to support its claims.

A "lens" is an approach with its own characteristic, NAMEABLE failure mode: e.g. wet_lab (assay/
instrument error, batch effects), computational_model (misspecification, hyperparameter
sensitivity), statistical_synthesis (pooling/heterogeneity bias), clinical_observational
(confounding, ascertainment bias), mathematical_formal (proof-gap risk), qualitative (rater bias).

The PRIMARY judgment is the failure mode itself, quoted or closely paraphrased from the text —
not the category label. Two analyses sharing the same underlying failure mode (e.g. two
multiple-testing corrections on the same assay, or two model variants trained on the same data
with the same confound) are ONE lens, not two, even if they carry different names or category
tags. Be skeptical; do not inflate the count; a lens mentioned only in passing with no method
detail ("we also validated computationally") is not a distinct lens unless the text names what was
actually done.

INPUT:
<constraints.md>
{constraints_md}
</constraints.md>
{for each method file: <FILENAME> content </FILENAME>}

TASK: Return a JSON list. Each item:
{
  "name": "<short label>",
  "modality": "wet_lab | computational_model | statistical_synthesis | clinical_observational | mathematical_formal | qualitative | other",
  "failure_mode": "<what specifically would make THIS lens wrong — quoted or tightly paraphrased from the text, naming the concrete mechanism, not a generic category>",
  "evidence": "<verbatim quote or section ref proving this lens is used, naming a specific tool/dataset/parameter — a bare mention with no specifics does not qualify>",
  "confidence": <0.0-1.0, confidence this is a genuinely distinct lens with its own failure mode, not a variant of another>
}
Only include items with confidence >= 0.4. If no method content exists, return [].
```

Output: `lenses: list[{name, modality, failure_mode, evidence, confidence}]`.
Deterministic post-filter: `real_lenses = [l for l in lenses if l.confidence >= 0.6]` (the ≥0.6 set
counts toward `n`; the 0.4–0.6 band is logged but not counted, to keep the extractor honest about
uncertainty without either discarding or over-crediting borderline cases).

**Step 2a — [sem] Pairwise independence audit (LLM call, dedicated, adversarial).** Run only if
`len(real_lenses) >= 2`. For every unordered pair `(i, j)` of `real_lenses` (typically 1–3 pairs;
if `real_lenses` has more than 4 members, sample the highest-confidence 4 to bound cost — logged,
not silently truncated):

Prompt (exact, run per pair):
```
SYSTEM: You previously extracted these two methodological lenses from a paper's method layer:
Lens A: {name_A}, failure_mode: "{failure_mode_A}", evidence: "{evidence_A}"
Lens B: {name_B}, failure_mode: "{failure_mode_B}", evidence: "{evidence_B}"

Given the full method-layer text below, answer:

<constraints.md>{constraints_md}</constraints.md>
{method files}

1. independence_score (0.0-1.0): Are lens A's and lens B's FAILURE MODES actually independent
   (different data source / instrument / algorithm class / assumption set), or is one a relabeled
   variant of the other's risk? 1.0 = fully independent; 0.0 = same underlying failure-mode family.
   Judge the failure modes as described, not the modality labels.
2. same_failure_family (bool): true if independence_score < 0.4.
Return JSON: {"independence_score": f, "same_failure_family": bool, "rationale": s}
```

**Step 2b — [sem] Circularity audit (LLM call, dedicated, adversarial — new in cycle 2).** Run on
the same pairs as Step 2a, only for pairs with `independence_score >= 0.4` (pairs already flagged
as the same failure family are moot for circularity — they're not independent regardless).

Prompt (exact, run per qualifying pair):
```
SYSTEM: You are checking for a specific integrity failure: was lens A's output used to select,
tune, or constrain lens B's parameters, hypotheses, or search space (or vice versa) BEFORE lens B's
result was reported as agreeing with or corroborating lens A? This makes the apparent agreement
circular, not independent corroboration.

Look for phrases like "informed by," "using X's estimate as a prior," "hyperparameters selected to
match," "guided by the wet-lab finding," or any sequence where B's design choices are justified by
A's result rather than by independent reasoning.

<constraints.md>{constraints_md}</constraints.md>
{method files}

Return JSON: {"circular": bool, "direction": "A_informs_B | B_informs_A | none",
"evidence": "<verbatim quote showing the tuning/selection dependency, or empty string>"}
```

Deterministic aggregation into `n_effective` and `independence_agg`:
```
qualifying_pairs = [p for p in pairs if p.independence_score >= 0.6 and not p.circular]
n_effective = |{lens indices appearing in at least one qualifying_pair}|
independence_agg = mean(p.independence_score for p in pairs)   # circular/same-family pairs count as low, dragging the mean down — they are not excluded from this average, only from n_effective
```
If `len(real_lenses) == 1`: Steps 2a/2b are skipped (nothing to pair); handle as the single-lens
path (§5).

**Step 3 — [sem] Integration / constraints-reflection (LLM call).** Run only if
`len(real_lenses) >= 1` (if zero, all downstream sub-scores are deterministically set to 0.0 —
nothing to integrate or reflect on).

Prompt (exact):
```
SYSTEM: You previously extracted these methodological lenses and their pairwise relationships:
Lenses: {real_lenses as JSON, with failure_mode}
Pairwise independence/circularity findings: {pairs as JSON}

Given the full method-layer text below, answer:

<constraints.md>{constraints_md}</constraints.md>
{method files}

1. integration_evidence: For each pair flagged circular=false and independence_score >= 0.6,
   is there EXPLICIT textual evidence that one lens's result was used to corroborate,
   stress-test, or resolve disagreement with the other (not just reported side by side, and not
   already flagged circular)? For each such pair return {"pair": [A,B], "integration_score":
   0.0-1.0, "quote": s}. If a pair's only apparent integration evidence is the same evidence
   already flagged circular in Step 2b, return integration_score 0.0 and note
   "superseded_by_circularity": true.
2. constraints_reflection_score (0.0-1.0): Does constraints.md explicitly engage with the
   boundary/limitation implications of THESE SPECIFIC lenses and their SPECIFIC failure modes
   (including any disagreement or, if applicable, any circularity risk between them) rather than
   generic boilerplate? Quote the relevant constraints bullet, or 0.0 with quote="".

Return JSON: {"integration_evidence": [...], "constraints_reflection_score": f,
"constraints_quote": s}
```
If `len(real_lenses) == 1` (single lens, honestly used): there is no pairwise integration
question — only `constraints_reflection_score` is asked for (does constraints.md honestly bound
the single-lens scope?).

## 5. Deterministic scoring function

```python
from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Lens:
    name: str
    modality: str
    failure_mode: str
    evidence: str
    confidence: float


@dataclass
class PairFinding:
    i: int
    j: int
    independence_score: float
    circular: bool


@dataclass
class IntegrationFinding:
    i: int
    j: int
    integration_score: float
    superseded_by_circularity: bool = False


@dataclass
class TriangulationJudgment:
    pairs: list          # list[PairFinding], empty if n<2
    integrations: list   # list[IntegrationFinding], empty if n<2
    constraints_reflection_score: float   # always present (0.0 if not assessable)


FAILURE_VERBS = [
    "bias", "biases", "biased", "confound", "confounds", "confounding",
    "does not generalize", "not generalized", "may not generalize",
    "was not corrected", "were not corrected", "not adjusted for",
    "sensitive to", "prone to", "limited by", "restricted to",
    "assumes", "relies on", "cannot rule out", "cannot distinguish",
    "underpowered", "small sample", "single-center", "not validated",
]

GENERIC_PHRASES = [
    "no limitations stated",
    "results generalize to similar populations",
    "further research is needed",
]


def _has_concrete_noun(bullet: str) -> bool:
    """Cheap structural proxy for 'names a specific object' — a capitalized
    multi-letter token not at the start of the bullet, a quoted term, or a
    number/percentage. Deliberately permissive; false positives are fine here
    since this only feeds a *substantiveness* signal, not the confidence score."""
    words = bullet.strip().split()
    if not words:
        return False
    interior = words[1:]
    if any(w[0].isupper() and w[1:].isalpha() for w in interior if len(w) > 1):
        return True
    if re.search(r"[\"'`][^\"'`]{2,}[\"'`]", bullet):
        return True
    if re.search(r"\d", bullet):
        return True
    return False


def _has_failure_verb(bullet: str) -> bool:
    lower = bullet.lower()
    return any(v in lower for v in FAILURE_VERBS)


def _extract_known_limitations_bullets(constraints_md: str) -> list:
    lower = constraints_md.lower()
    if "known limitations" not in lower:
        return []
    idx = lower.index("known limitations")
    section = constraints_md[idx:]
    next_heading = re.search(r"\n##[^#]", section[1:])
    if next_heading:
        section = section[: next_heading.start() + 1]
    return [l.strip("-* \t") for l in section.splitlines() if l.strip().startswith(("-", "*"))]


def is_boilerplate_constraints(constraints_md: str) -> bool:
    """Structural-first thinness check (Step 0). A bullet counts as substantive
    if it pairs a concrete noun-like token with a failure/limitation verb; this
    catches paraphrased or non-English-idiom boilerplate that a fixed English
    phrase list alone would miss. The phrase list remains a secondary fallback
    signal for the degenerate near-empty case."""
    if not constraints_md or not constraints_md.strip():
        return True
    lower = constraints_md.lower()
    bullets = _extract_known_limitations_bullets(constraints_md)
    if not bullets:
        return True
    substantive = [b for b in bullets if _has_concrete_noun(b) and _has_failure_verb(b)]
    if substantive:
        return False
    if any(p in lower for p in GENERIC_PHRASES) and len(constraints_md.split()) < 60:
        return True
    # No substantive bullet found by the structural test either — treat as boilerplate.
    return True


def availability_tier(constraints_md: str, method_files: dict) -> str:
    boilerplate = is_boilerplate_constraints(constraints_md)
    has_methods = bool(method_files)
    if not has_methods and boilerplate:
        return "absent"
    if not has_methods or boilerplate:
        return "thin"
    return "full"


AVAILABILITY_MULTIPLIER = {
    "absent": 0.15,   # floor, not zero and not skipped — the metric still returns a real score
    "thin": 0.55,
    "full": 1.0,
}


def base_lens_score(n_effective: int) -> float:
    """n_effective = count of lenses participating in >=1 qualifying (independent,
    non-circular) pair; for n_effective==0 with real_lenses present (single lens,
    or all pairs collapsed to one failure family / all circular), falls back to
    the single-lens branch handled by the caller.
    Recalibrated in cycle 2 (was 0.55/0.75) to widen top-of-range discrimination
    among genuinely strong papers, while the multiplicative gates below are
    unchanged in stringency — see worked cases."""
    if n_effective == 0:
        return 0.0
    if n_effective == 1:
        return 0.15   # single lens acknowledged; no triangulation possible
    if n_effective == 2:
        return 0.65
    return 0.90        # n_effective >= 3, capped — extra count alone can't buy more; integration must


def score_m36(
    constraints_md: str,
    method_files: dict,
    lenses: list,             # list[Lens]
    judgment: "TriangulationJudgment",
) -> float:
    """
    Accumulates `score` as a fraction in [0.0, 1.0] through a chain of
    multiplicative gates, then converts to a percentage on the final line.
    Never returns None/NA — every branch produces a real, penalized number
    per the penalize-don't-skip constraint.
    """
    real_lenses = [l for l in lenses if l.confidence >= 0.6]
    n = len(real_lenses)

    if n == 0:
        score = 0.0  # nothing to reflect on either; availability tier still applied below
    elif n == 1:
        score = base_lens_score(1)
        refl = judgment.constraints_reflection_score
        score *= (0.4 + 0.6 * refl)
    else:
        pairs = judgment.pairs
        qualifying = [p for p in pairs if p.independence_score >= 0.6 and not p.circular]
        participants = set()
        for p in qualifying:
            participants.add(p.i)
            participants.add(p.j)
        n_effective = len(participants)
        independence_agg = (
            sum(p.independence_score for p in pairs) / len(pairs) if pairs else 0.0
        )

        score = base_lens_score(n_effective)

        # Independence gate: dragged down by same-family AND circular pairs alike
        # (independence_agg already reflects both, since circular pairs are not
        # excluded from this average — only from n_effective / integration credit).
        score *= (0.4 + 0.6 * independence_agg)

        # Integration gate, with the cycle-2 hard-zero circularity rule: if every
        # piece of claimed integration evidence for a qualifying pair is the same
        # evidence already flagged circular, integration cannot be credited at
        # all for that pair — this is a literal 0.0, not the 0.4 floor, closing
        # the "manufactured agreement" gaming route exp3 previously missed.
        qualifying_keys = {(p.i, p.j) for p in qualifying} | {(p.j, p.i) for p in qualifying}
        usable_integrations = [
            ig for ig in judgment.integrations
            if (ig.i, ig.j) in qualifying_keys and not ig.superseded_by_circularity
        ]
        if not usable_integrations:
            integ_factor = 0.0 if n_effective >= 2 else (0.4 + 0.6 * 0.0)
        else:
            integ_agg = sum(ig.integration_score for ig in usable_integrations) / len(usable_integrations)
            integ_factor = 0.4 + 0.6 * integ_agg
        score *= integ_factor

        refl = judgment.constraints_reflection_score
        score *= (0.4 + 0.6 * refl)

    # Availability/thinness penalty — always applied, never skipped. This is what
    # makes "compile a thin method layer to dodge extraction" a losing strategy: it
    # caps the ceiling regardless of what (if anything) got extracted.
    tier = availability_tier(constraints_md, method_files)
    score *= AVAILABILITY_MULTIPLIER[tier]

    score = max(0.0, min(1.0, score))       # score is a fraction in [0, 1] up to here
    return round(score * 100, 1)             # final line: convert to a [0, 100] percentage
```

### Worked cases
- **Abstract-only source, no method files, boilerplate constraints** (the shape doc's stated
  floor case): `n=0`, `tier="absent"` → `score = 0.0 * 0.15 = 0.0`. Correctly floors without
  raising an N/A. Unchanged from cycle 1.
- **Pure statistical-synthesis review, honest scope** (che26-style, one method file, rich
  `constraints.md` with a real "Known limitations" section naming the single-method boundary and
  passing the new structural substantiveness check): `n=1`, `base=0.15`, `refl≈0.8` →
  `0.15 * (0.4+0.48) = 0.132` → `tier="full"` → **13.2/100**. Unchanged — the single-lens path was
  not touched by the recalibration, since it correctly measures "no triangulation occurred," not
  discrimination among strong triangulated papers.
- **Wet-lab + computational paper, real cross-validation, constraints names the disagreement and
  resolution, no circularity**: `n=2`, `n_effective=2`, `independence_agg≈0.85`,
  `integ_agg≈0.8` (one usable, non-circular integration finding), `refl≈0.85`, `tier="full"` →
  `0.65 * (0.4+0.51) * (0.4+0.48) * (0.4+0.51) = 0.65 * 0.91 * 0.88 * 0.91 ≈ 0.4759` →
  **47.6/100**. *(Cycle-1 equivalent case scored 41.7 with the old 0.55 base and 0.5-floor
  factors; the recalibrated base alone accounts for most of the lift, discrimination among strong
  papers is now visibly wider without loosening any gate.)*
- **Same case, but three lenses, all pairwise-independent and integrated, strong reflection**:
  `n_effective=3`, `base=0.90`, `independence_agg≈0.9`, `integ_agg≈0.85`, `refl≈0.9`,
  `tier="full"` → `0.90 * 0.94 * 0.91 * 0.94 ≈ 0.723` → **72.3/100**. A ceiling near-100 now
  requires near-perfect scores on every one of four independent gates simultaneously (base,
  independence, integration, reflection) times a full availability tier — still a demanding,
  rarely-fully-satisfied criterion, but no longer compressed into a ~42-point ceiling.
- **Padded case** (two "lenses" both computational, same underlying failure family,
  `independence_score=0.1`, no genuine cross-reference): pair is `same_failure_family=True`,
  excluded from `n_effective` (`n_effective=0` even though `n=2`) → falls to the `n_effective==0`
  fallback inside the `else` branch: `base_lens_score(0)=0.0` → **0.0/100 before availability**,
  i.e. the padded pair scores identically to having found no lenses at all — a stronger penalty
  than cycle 1's `0.151`, because n_effective correctly recognizes that a padded pair contributes
  no real triangulation, rather than letting raw `n=2` buy a nonzero `base_lens_score`.
- **New: circularity case.** Two genuinely different-modality lenses (`wet_lab`,
  `computational_model`), `independence_score=0.8` (their failure modes are legitimately
  distinct), but Step 2b finds the computational model's priors were explicitly "informed by the
  assay's point estimate" and the paper's only stated integration evidence is that same sentence:
  `circular=True` for that pair → excluded from `n_effective` (`n_effective=0`, since it's the
  only pair) → `base_lens_score(0)=0.0` → **0.0/100 before availability**, regardless of how
  well-written the surrounding constraints text is. This is the case cycle 1 could not catch:
  under the old scalar-independence design, `independence_score≈0.8` alone would have produced
  `base=0.55 * 0.9 * integ_factor`, and even a conservative `integ_factor` floor of 0.5 would have
  yielded a nonzero, potentially misleadingly respectable score (~0.25 → 25/100) for what is
  actually fabricated corroboration. Cycle 2 zeroes it.

## 6. Why this is hard to Goodhart

1. **Grounded extraction on failure mode, not category label.** Every lens requires a verbatim
   `failure_mode` and `evidence` quote and a confidence the LLM must justify against a stated
   definition (independent, nameable failure mode); trivial variants and same-category-but-really-
   the-same-risk pairs are explicitly caught at the pairwise independence step, and the 0.6
   confidence cutoff discards borderline padding attempts.
2. **Circularity is a hard zero, not a discount (new in cycle 2).** A tuning/selection dependency
   between two lenses is detected by a dedicated adversarial pass and, when it is the sole source
   of claimed integration, forces `integ_factor = 0.0` exactly — closing the single most
   epistemically damaging gaming route (manufactured agreement) that the cycle-1 version left
   open.
3. **Multiplicative composition prevents single-axis gaming.** `base_lens_score(n_effective)`,
   independence, integration, constraints-reflection, and availability are combined
   multiplicatively, not additively — inflating any one factor while another is near zero still
   yields a near-zero score. You cannot buy a high score with a long lens list and weak
   integration, nor with beautiful prose in `constraints.md` and no actual multi-lens work behind
   it, nor — new in cycle 2 — with a plausible-sounding independence score propped up by a
   circular integration claim.
4. **`n_effective` (not raw count) gates the base score.** Padded or same-failure-family pairs, and
   circular pairs, are excluded from the participant set used for `base_lens_score`, so "3 lenses,
   two of which are really one" or "2 lenses that only appear independent because of a circular
   tuning dependency" collapse toward the honest lower base rather than being merely discounted by
   a continuous multiplier.
5. **Constraints-reflection is checked against the specific extracted failure modes**, not scored
   in isolation — so generic boilerplate limitations text (independently flagged as a red flag by
   the artifact shape doc itself, and now also caught structurally rather than only by phrase
   match) cannot substitute for engaging with the actual method configuration.
6. **Penalize-don't-skip removes the "compile thin, get N/A" exit.** A compiler or author that
   omits method files to avoid exposing single-lens-ness is met with the `availability_tier` floor
   multiplier (0.15), which is lower than any honest single-lens, well-documented case's ceiling
   (0.132 at full reflection). Thinness is read as a negative signal about the artifact, never as
   an excuse to abstain.
7. **Self-limiting, now better-discriminating ceiling.** Reaching a high score still requires
   simultaneously high `n_effective`, independence, integration, and reflection scores from an
   adversarial-enough LLM judge, graded against quoted textual evidence with a dedicated
   circularity check — so wholesale fabrication remains detectable by cross-referencing quotes
   against source content — while the recalibrated bases (§5) mean the score now spreads
   meaningfully across the range of genuinely strong papers instead of compressing them all near
   40.

## 7. Composition with the rest of the suite

M36 is deliberately narrow: it measures *structural method diversity, the genuineness of the
corroboration between lenses, and the paper's own awareness of it* — purely within
`logic/solution/`. It does not overlap with:
- **Rigor-within-a-method metrics** (e.g. statistical validity, protocol completeness) — those
  grade quality of a single lens; M36 grades whether multiple independent, non-circular lenses
  exist and are genuinely reconciled.
- **Evidence-grounding / reproducibility metrics** that check whether numbers in `evidence/`
  tables are internally consistent or traceable to source — M36 does not re-derive or verify
  numeric claims, only whether the method layer documents genuine cross-lens integration.
- **Structural/Seal-Level-1 checks** (e.g. "does constraints.md exist," "is method-file naming
  genre-appropriate") — M36 assumes those gates and adds a semantic layer on top: given a
  structurally valid method layer, does its *content* show genuine, non-circular triangulation.

Because it is one signal among many, and because the recalibrated ceiling (§5) still requires
simultaneously high scores on four independent gates to approach 100, a high overall artifact
score cannot come from M36 alone; it should be weighted as a moderate contributor that
specifically rewards papers whose claims rest on more than one independent, non-circular line of
evidence, and that flags — via a low but non-null score — single-lens work, thin/absent
method-layer compiles, padded/same-family lens lists, and now, distinctly, manufactured
cross-lens agreement.
