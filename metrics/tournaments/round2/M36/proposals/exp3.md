# M36 — Multi-perspective triangulation — Expansion + Workflow (expander 3)

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

A "lens" here is defined narrowly: an approach with an **independent failure-mode profile**. Two
different multiple-testing corrections run on the same assay data are not two lenses — they're one
lens analyzed two ways. A wet-lab replication and an orthogonal computational model *are* two
lenses, because a batch effect that breaks the wet-lab result and a misspecification that breaks
the computational result are unrelated events. The epistemic reason this is a good-science signal:
triangulation across independent failure modes is precisely what makes a finding robust to any
single method's blind spot — it's the closest thing this artifact layer has to an internal
replication signal, and it is diagnostic in the disconfirming direction too (a paper with rich
multi-lens machinery in its evidence but a `constraints.md` that never mentions where the lenses
agree/disagree is *overclaiming* integration it didn't do).

### What it must reward
- Genuine independence between lenses (different data source, different instrument/algorithm
  class, different assumption set).
- Actual **integration**: evidence in the text that one lens's output was used to corroborate,
  stress-test, or resolve disagreement with another's — not just two lenses reported in
  side-by-side, non-cross-referencing sections.
- `constraints.md` explicitly reasoning about the boundary this combination (or lack of it)
  creates — including honestly flagging where lenses *disagreed* and how that was resolved (or
  wasn't).

### What it must NOT reward
- Lens-count padding: listing multiple pipeline steps, corrections, or sensitivity analyses within
  one method family as if they were independent lenses.
- Juxtaposition without integration: a paper with a wet-lab section and a computational section
  that never reference each other's results.
- Boilerplate constraints text ("results are consistent across methods") asserted without any
  grounded evidence trail back into the method files.
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
| List cosmetically different "approaches" that share one failure-mode family (e.g. two normalization schemes) to inflate lens count | Lens extraction requires a `confidence` that the lens is genuinely distinct, filtered at ≥0.4, and independence is scored *separately* from count — a padded lens count with low independence caps the final score multiplicatively |
| Mention "we also validated computationally" once, as a rubber stamp, with no actual cross-reference | Integration score requires quoted evidence that one lens's result fed into judgment of another; a bare mention with no cross-reference scores integration ≈ 0, which multiplicatively suppresses the multi-lens bonus |
| Write an eloquent, generic limitations paragraph without engaging lens-specific boundaries | `constraints_reflection_score` is graded against the *specific* lenses found in step 1, not against limitations text in isolation — boilerplate that doesn't name the lenses or their interaction scores low even if well-written |
| Omit method files entirely (thin compile) to avoid the extraction step surfacing single-lens-ness | Handled explicitly by the availability/thinness multiplier in §4 — absence of method files is itself scored, never skipped, and floors the score rather than exempting it |
| Claim more lenses than the paper supports by relying on the compiler's method-file *names* (e.g. an `architecture.md` present for a paper that trained no model — a known compiler defect per the shape doc) | Lens extraction is grounded in verbatim `evidence` quotes from the text, not file names; a fabricated/forced file with no supporting method content yields low-confidence, filtered-out "lenses" |

## 3. How the assessment-critique notes shaped this design (net-new, tightly scoped)

The ledger note says M36 ranked top-10 specifically for being genuinely absent from round 1 and
the ARA verifier, and for being scoped tighter than adjacent ideas. To preserve that edge:

- **Scope is locked to §7** (`logic/solution/`) only. This metric does not reach into `evidence/`
  tables or `problem/` framing to check if multiple *data sources* exist — that overlaps with
  reproducibility/evidence-grounding metrics elsewhere in the suite. M36 asks only whether the
  *method layer itself* documents and reflects multi-lens combination.
- It is **not** a restatement of an internal-consistency or rigor-within-a-method metric: a
  single-lens paper can be perfectly rigorous and internally consistent and still correctly score
  low here, because rigor-within-a-lens and triangulation-across-lenses are orthogonal axes. The
  scoring function below never conflates "how good is the method" with "how many independent
  method families corroborate the claim."
- It is **not** redundant with a generic "did constraints.md exist" check — that's a floor/gate
  condition already implicit in Seal Level 1 structural validation. M36's contribution is specific:
  it cross-checks constraints content *against* the lens set actually found, which no existing
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

Thinness check on `constraints.md` (deterministic heuristic, cheap): flag as boilerplate if it has
no `## Known limitations` bullets, or every bullet under 15 words, or the file matches a
near-generic pattern (e.g. "no limitations stated", "results generalize to similar populations").
This directly operationalizes the shape doc's own red-flag note ("a bare 'no limitations stated'
... is a red flag").

**Step 1 — [sem] Lens extraction (LLM call).** Skip only if `method_files` is empty AND
`constraints.md` has zero prose beyond boilerplate (score handled by Step 0 gate instead — this is
the one case where there is nothing to extract, but the *availability_tier* still drives the score
down, so nothing is skipped in the scoring sense).

Prompt (exact):
```
SYSTEM: You are analyzing the method layer of a compiled research artifact to identify
methodologically INDEPENDENT lenses used to support its claims.

A "lens" is an approach with its own characteristic failure mode: e.g. wet_lab (assay/instrument
error, batch effects), computational_model (misspecification, hyperparameter sensitivity),
statistical_synthesis (pooling/heterogeneity bias), clinical_observational (confounding,
ascertainment bias), mathematical_formal (proof-gap risk), qualitative (rater bias).

Two analyses sharing the same failure-mode family (e.g. two multiple-testing corrections on the
same assay) are ONE lens, not two. Be skeptical; do not inflate the count.

INPUT:
<constraints.md>
{constraints_md}
</constraints.md>
{for each method file: <FILENAME> content </FILENAME>}

TASK: Return a JSON list. Each item:
{
  "name": "<short label>",
  "modality": "wet_lab | computational_model | statistical_synthesis | clinical_observational | mathematical_formal | qualitative | other",
  "evidence": "<verbatim quote or section ref proving this lens is used>",
  "confidence": <0.0-1.0, confidence this is a genuinely distinct lens, not a variant of another>
}
Only include items with confidence >= 0.4. If no method content exists, return [].
```

Output: `lenses: list[{name, modality, evidence, confidence}]`.
Deterministic post-filter: `real_lenses = [l for l in lenses if l.confidence >= 0.6]` (the ≥0.6 set
counts toward `n`; the 0.4–0.6 band is logged but not counted, to keep the extractor honest about
uncertainty without either discarding or over-crediting borderline cases).

**Step 2 — [sem] Independence / integration / constraints-reflection (LLM call).** Run only if
`len(real_lenses) >= 1` (if zero, these three sub-scores are deterministically set to 0.0 — nothing
to integrate).

Prompt (exact):
```
SYSTEM: You previously extracted these methodological lenses from a paper's method layer:
{real_lenses as JSON}

Given the full method-layer text below, answer three questions.

<constraints.md>{constraints_md}</constraints.md>
{method files}

1. independence_score (0.0-1.0): Among the listed lenses, how independent are their failure
   modes (different data source / instrument / algorithm class / assumption set)? 1.0 = fully
   independent; 0.0 = same failure-mode family relabeled.
2. integration_score (0.0-1.0): Is there EXPLICIT textual evidence that one lens's result was
   used to corroborate, stress-test, or resolve disagreement with another (not just reported
   side by side)? Quote the integration evidence, or return 0.0 with quote="".
3. constraints_reflection_score (0.0-1.0): Does constraints.md explicitly engage with the
   boundary/limitation implications of THESE SPECIFIC lenses (including any disagreement between
   them) rather than generic boilerplate? Quote the relevant constraints bullet, or 0.0 with
   quote="".

Return JSON: {"independence_score": f, "integration_score": f,
"constraints_reflection_score": f, "independence_quote": s, "integration_quote": s,
"constraints_quote": s}
```
If `len(real_lenses) == 1` (single lens, honestly used): `independence_score` and
`integration_score` are not meaningful (no second lens to integrate with) — set both to `None`
and handle in scoring as "single-lens path" (see §5); only `constraints_reflection_score` is asked
for (does constraints.md honestly bound the single-lens scope?).

### 5. Deterministic scoring function

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class Lens:
    name: str
    modality: str
    evidence: str
    confidence: float


@dataclass
class TriangulationJudgment:
    independence_score: Optional[float]   # None if n<2
    integration_score: Optional[float]    # None if n<2
    constraints_reflection_score: float   # always present (0.0 if not assessable)


def is_boilerplate_constraints(constraints_md: str) -> bool:
    """Cheap deterministic thinness check (Step 0)."""
    if not constraints_md or not constraints_md.strip():
        return True
    lower = constraints_md.lower()
    generic_phrases = [
        "no limitations stated",
        "results generalize to similar populations",
        "further research is needed",
    ]
    if any(p in lower for p in generic_phrases) and len(constraints_md.split()) < 60:
        return True
    if "## known limitations" not in lower and "known limitations" not in lower:
        return True
    return False


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


def base_lens_score(n: int) -> float:
    """n = count of lenses with confidence >= 0.6."""
    if n == 0:
        return 0.0
    if n == 1:
        return 0.15   # single lens acknowledged; no triangulation possible
    if n == 2:
        return 0.55
    return 0.75        # n >= 3, capped — extra count alone can't buy more; integration must


def score_m36(
    constraints_md: str,
    method_files: dict,
    lenses: list[Lens],
    judgment: TriangulationJudgment,
) -> float:
    """
    Returns a score in [0, 100]. Never returns None/NA — every branch produces a
    real, penalized number per the penalize-don't-skip constraint.
    """
    real_lenses = [l for l in lenses if l.confidence >= 0.6]
    n = len(real_lenses)

    score = base_lens_score(n)

    if n >= 2:
        # Guard against padded lens counts with low true independence, and against
        # juxtaposition-without-integration. Multiplicative so neither can be bought
        # by inflating the other.
        indep = judgment.independence_score if judgment.independence_score is not None else 0.0
        integ = judgment.integration_score if judgment.integration_score is not None else 0.0
        score *= (0.5 + 0.5 * indep)
        score *= (0.5 + 0.5 * integ)

    # Constraints-reflection: does the paper KNOW what its lens configuration implies?
    # Applies whether n==1 (did it honestly bound single-lens scope?) or n>=2 (did it
    # address multi-lens boundary/disagreement?). n==0 gets no credit here — nothing to
    # reflect on, and the base score is already 0.
    if n >= 1:
        refl = judgment.constraints_reflection_score
        score *= (0.4 + 0.6 * refl)

    # Availability/thinness penalty — always applied, never skipped. This is what
    # makes "compile a thin method layer to dodge extraction" a losing strategy: it
    # caps the ceiling regardless of what (if anything) got extracted.
    tier = availability_tier(constraints_md, method_files)
    score *= AVAILABILITY_MULTIPLIER[tier]

    return round(max(0.0, min(1.0, score)) * 100, 1)
```

### Worked cases
- **Abstract-only source, no method files, boilerplate constraints** (the shape doc's stated
  floor case): `n=0`, `tier="absent"` → `score = 0.0 * 0.15 = 0.0`. Correctly floors without
  raising an N/A.
- **Pure statistical-synthesis review, honest scope** (che26-style, one method file, rich
  `constraints.md` with a real "Known limitations" section naming the single-method boundary):
  `n=1`, `base=0.15`, `refl≈0.8` → `0.15 * (0.4+0.48) = 0.132` → `tier="full"` → **13.2/100**. Low,
  as intended — this metric specifically measures triangulation, which genuinely didn't occur —
  but not zero, and not penalized for thinness since the method layer and constraints are both
  substantive.
- **Wet-lab + computational paper, real cross-validation, constraints names the disagreement and
  resolution**: `n=2`, `base=0.55`, `indep≈0.85`, `integ≈0.8`, `refl≈0.85`, `tier="full"` →
  `0.55 * 0.925 * 0.9 * 0.91 ≈ 0.417` → **41.7/100**. Note this is *not* near the ceiling even in
  a strong case — deliberately, since the multiplicative chain means only a paper with high scores
  on every sub-dimension simultaneously (independence, integration, reflection, availability)
  approaches 100, which is appropriate for a demanding, rarely-fully-satisfied criterion.
- **Padded case**: two "lenses" both computational, low independence (`indep=0.1`), no
  cross-reference (`integ=0.0`): `n=2, base=0.55` → `0.55 * 0.55 * 0.5 = 0.151`, further cut by
  `refl` and `tier` — padding cannot approach the genuine two-lens case above.

## 6. Why this is hard to Goodhart

1. **Grounded extraction, not keyword matching.** Every lens requires a verbatim `evidence` quote
   and a confidence the LLM must justify against a stated definition (independent failure mode);
   trivial variants are explicitly instructed to be merged, and the 0.6 confidence cutoff discards
   borderline padding attempts.
2. **Multiplicative composition prevents single-axis gaming.** Lens count, independence,
   integration, constraints-reflection, and availability are combined multiplicatively, not
   additively — inflating any one factor while another is near zero still yields a near-zero
   score. You cannot buy a high score with a long lens list and weak integration, nor with
   beautiful prose in `constraints.md` and no actual multi-lens work behind it.
3. **Constraints-reflection is checked against the specific extracted lens set**, not scored in
   isolation — so generic boilerplate limitations text (already independently flagged as a red
   flag by the artifact shape doc itself) cannot substitute for engaging with the actual method
   configuration.
4. **Penalize-don't-skip removes the "compile thin, get N/A" exit.** A compiler or author that
   omits method files to avoid exposing single-lens-ness is met with the `availability_tier`
   floor multiplier (0.15), which is *lower* than the honest single-lens, well-documented case
   (0.132 in the worked example above is close but for a genuinely well-reflected single-lens
   paper — thinness alone still caps harder for degenerate compiles with also-boilerplate
   constraints). Thinness is read as a negative signal about the artifact, never as an excuse to
   abstain.
5. **Self-limiting ceiling.** Because reaching a high score requires simultaneously high
   independence, integration, and reflection scores from an adversarial-enough LLM judge, and
   because these are graded against quoted textual evidence, wholesale fabrication is
   detectable by cross-referencing quotes against source content in the same call.

## 7. Composition with the rest of the suite

M36 is deliberately narrow: it measures *structural method diversity and the paper's own
awareness of it*, purely within `logic/solution/`. It does not overlap with:
- **Rigor-within-a-method metrics** (e.g. statistical validity, protocol completeness) — those
  grade quality of a single lens; M36 grades whether multiple independent lenses exist and are
  reconciled.
- **Evidence-grounding / reproducibility metrics** that check whether numbers in `evidence/`
  tables are internally consistent or traceable to source — M36 does not re-derive or verify
  numeric claims, only whether the method layer documents cross-lens integration.
- **Structural/Seal-Level-1 checks** (e.g. "does constraints.md exist," "is method-file naming
  genre-appropriate") — M36 assumes those gates and adds a semantic layer on top: given a
  structurally valid method layer, does its *content* show genuine triangulation.

Because it is one signal among many and is capped well below 100 even in strong cases (§5), a high
overall artifact score cannot come from M36 alone; it should be weighted as a moderate contributor
that specifically rewards papers whose claims rest on more than one independent line of evidence,
and that flags — via a low but non-null score — both single-lens work (whether or not honestly
scoped) and thin/absent method-layer compiles.
