# M32 — Method validity & verification status — Expansion 1

## 1. What this metric is actually for

The one-line indicator is: *"Is the method sound — a widely-accepted validated method vs one
over-generalized beyond its warrant (and is that justified/explained)?"* This is deliberately
**narrower** than general methodological rigor (verifier D6). D6 asks "was the chosen method
executed correctly" (adequate sample size, correct test given the data, blinding, controls,
reproducible protocol). M32 asks a logically prior question: **is the chosen method itself the
right tool, validated for the context it's actually being applied in — or has the paper reached
for a technique whose validity is established elsewhere (different population, different scale,
different assay platform, different regime) and quietly carried it over here?**

A paper can pass D6 (impeccable execution) while failing M32 (a well-executed but unwarranted
method transplant — e.g. a diagnostic threshold validated on a MS-platform cohort applied without
comment to a Simoa-platform cohort). A paper can also fail D6 (small n, no blinding) while passing
M32 (the method itself is completely standard and squarely within its validated domain for this
exact use). Keeping these orthogonal is the reason M32 survived the assessment-critique ranking as
net-new — this expansion preserves that separation deliberately (see §5).

### What it must reward
- Using a technique that is established/guideline-recommended **for this exact
  application** (same domain, population, scale, platform as the validation literature).
- Using a technique **beyond** its established domain, but doing so **transparently and with an
  argument** — an explicit statement of the extension plus a reason, citation, or sensitivity
  check for why it should still hold (e.g. "threshold derived on Simoa is applied to MSD data;
  §4.5 cross-platform correlation of r=0.91 supports transfer").
- Constraints/limitations text that names the *specific* method-context mismatch, not generic
  hedging.
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
- Conflating this with general statistical rigor — adequate power, correct model diagnostics,
  proper blinding are D6's job; M32 must not re-score those or it becomes redundant.

### Failure modes / gaming routes this design must close
1. **Citation-as-shield gaming**: paper cites the original validation paper for a method by name,
   without addressing that its own use-case differs from that validation's scope. → closed by
   checking `stated_domain` against the domain the [sem] lookup actually finds validated, not just
   whether *a* citation exists.
2. **Boilerplate-caveat gaming**: stuffing constraints.md with generic disclaimers to look
   self-aware. → closed by requiring the disclosure-check to find *specific* acknowledgment of
   *this* method/domain pairing, not any limitations text.
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

## 2. How the assessment-critique notes reshape the design

The ledger note says this metric is net-new / tighter-scoped than D6 specifically because it
targets *method-context fit*, not *execution quality*. Three design consequences follow, all baked
into the workflow below:

- The workflow's central operation is an **external validity lookup** ([sem]), not an internal
  statistics check — this is what makes it genuinely different data than D6 consumes (D6 can be
  computed from the paper alone; M32 requires an outside reference point).
- The scoring function never inspects sample size, p-values, or study-design quality fields —
  doing so would re-derive D6 and blur the boundary the critique rewarded.
- Because it's a "tighter facet," the workflow deliberately caps scope to **method-domain
  transfer validity**, explicitly excluding adjacent-but-different questions (e.g. whether the
  *statistical test* was appropriate given the data's distribution — that's D6 territory) so the
  two verifiers stay decomposable and auditable independently.

## 3. Generation / compute workflow

**Artifact inputs** (from `logic/solution/`, §7 of the ARA shape):
- `constraints.md` → `boundary_conditions[]`, `assumptions[]` (id + text), `known_limitations[]`
  (name + text), optional `data_quality_caveats[]`.
- Zero or more method files (`study_design.md`, `method.md`, `architecture.md`, `algorithm.md`,
  `heuristics.md`, ...) → raw markdown text each.
- Filenames themselves are a signal (genre-fit check, step 4).

No other artifact section is read by this metric (kept within primary-artifact scope, §7 only).

### Step 1 — Method identification (local LLM extraction, no external call)
Concatenate `constraints.md` + all present method files. Run:

> **Prompt (extraction):**
> "You are extracting method identifications from a scientific paper's method-layer artifact.
> Given the text below, list every named technique/method/instrument/model/statistical-test/
> algorithm the paper actually *uses to produce its results* (not methods only mentioned as
> background or comparison baselines). For each, output: `name` (canonical name), `role` (one
> sentence — what it's used for here), `stated_domain` (the population/data-type/platform/scale it
> is applied to *in this paper*, exactly as stated). Output a JSON list. If method files are
> non-empty but you cannot identify any concrete method, output `[]` and set
> `extraction_failed: true`.
> TEXT: {constraints.md + method files, concatenated}"

Output: `methods: list[{name, role, stated_domain}]`, `extraction_failed: bool`.

### Step 2 — [sem] external validity-tier lookup (per identified method, cap at top 3 by prominence)
For each method, issue a semantic-scholar / undermind query:

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
> ADJACENT). Respond with the label plus one supporting sentence.
> SEARCH RESULTS: {sem output}"

Output per method: `tier ∈ {STANDARD, ADJACENT, NOVEL_OR_CONTESTED, UNKNOWN}`.

### Step 3 — Disclosure/justification check (only for methods with tier ≠ STANDARD)

> **Prompt (disclosure):**
> "Method \"{method.name}\" is used here for \"{method.stated_domain}\", which is not clearly
> established practice for that exact application (tier: {tier}). Does the constraints/limitations
> text below explicitly acknowledge that THIS SPECIFIC method-application pairing goes beyond
> established validation? Answer exactly one: `JUSTIFIED` (acknowledged, AND a reason, citation,
> sensitivity analysis, or argument is given for why it should still hold); `ACKNOWLEDGED_UNJUSTIFIED`
> (acknowledged, but no reason given for proceeding anyway); `SILENT` (no acknowledgment of this
> specific concern — generic unrelated hedging does not count).
> CONSTRAINTS TEXT: {full constraints.md text}"

Output per non-STANDARD method: `disclosure ∈ {JUSTIFIED, ACKNOWLEDGED_UNJUSTIFIED, SILENT}`.

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

# Per-method base score: branches on tier first (closes "silent-default gaming", failure mode 3),
# then on disclosure quality (closes "citation-as-shield" and "boilerplate-caveat" gaming).
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

def per_method_score(m: MethodAssessment) -> float:
    return _SCORE_TABLE[(m.tier, m.disclosure)]

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

### Worked example (che26-style, per shape example)
- `constraints_present = True`, one method file (`study_design.md`).
- Method extracted: `{"name": "P-score relative ranking vs p181_IA baseline",
  "stated_domain": "blood-based p-tau biomarkers, MS/Simoa/MSD/Lumipulse platforms pooled"}`.
- [sem] tier lookup on "pooling AUC comparisons across immunoassay platforms without re-calibration"
  → likely `ADJACENT` (cross-platform pooling is a known extension point, not routine).
- Disclosure check against constraints.md's "Known limitations (§4.5): batch effects... may still
  exist" → this *does* name the cross-platform concern but gives no correction/sensitivity check →
  `ACKNOWLEDGED_UNJUSTIFIED` → per-method score 0.40.
- No genre mismatch, no bare-no-limitations, one method only → aggregate = 0.4*0.40 + 0.6*0.40 =
  0.40. Final score 0.40/1.0 — a real, mid-low score reflecting "flagged but not resolved," not a
  free pass for citing a real biomarker platform.

## 4. Why penalize-don't-skip is honored throughout
Every branch in `score_m32` terminates in a numeric score, never `None`/`NA`:
- Missing `constraints.md` (an artifact-shape violation, since it's documented as mandatory) → 0.0.
- Abstract-only compiles (documented floor case in the shape notes) → 0.05, not skipped.
- Non-extractable method content despite non-empty files → 0.15, not skipped.
- `UNKNOWN` validity tier (search returned nothing usable) is explicitly *not* mapped to a neutral
  score — it is scored as at least as demanding as `ADJACENT` (never more lenient than not knowing),
  because absence of external evidence must not read as evidence of validity.

## 5. Why this is hard to Goodhart, and how it composes with the rest of the suite

- **External grounding breaks self-report gaming.** The validity tier comes from a semantic-
  scholar/undermind lookup, not from parsing the paper's own confident prose. A paper cannot make
  itself look STANDARD just by asserting a method is standard.
- **Disclosure ≠ mention.** The Step 3 prompt requires acknowledgment of the *specific*
  method/domain pairing plus a *reason*; generic hedging or boilerplate caveats can't satisfy
  `JUSTIFIED`, closing the boilerplate-caveat gaming route directly.
- **Min-weighted aggregation prevents dilution.** A paper can't bury one badly-extended, silently-
  used method inside several genuinely standard ones and average its way to a good score — the
  0.6-weighted min term ensures the worst offender dominates.
- **Cheap structural tripwires sit under the semantic layer.** `constraints_missing`,
  `bare_no_limitations`, `genre_mismatch`, and `abstract_only_floor` are non-LLM, hard-to-spoof
  checks on document structure that floor the score independent of how the semantic steps land —
  so even if an adversarial artifact fooled the LLM extraction/classification, gross degeneracy
  (missing file, wrong genre, empty limitations) still tanks the score.
- **Orthogonal to D6 by construction.** The workflow never reads sample size, statistical test
  choice, blinding, or reproducibility fields — only method identity, its external validity tier
  for the stated application, and whether that gap is disclosed/justified. A paper can score high
  on D6 (well-executed) and low on M32 (wrong tool for the domain, undisclosed), or vice versa;
  the two are measuring different failure surfaces and a suite score that includes both cannot be
  satisfied by optimizing either one alone. This preserves the "net-new / tighter-scoped" edge that
  put M32 in the top 10.
- **Composes as a multiplicative-style gate, not an additive bonus.** Because a single silently-
  contested method can floor the aggregate near 0, M32 is best combined with the rest of the suite
  as a term that can veto an otherwise-strong composite score, rather than one more point among
  many that can be traded off — consistent with "good science" requiring the *method itself* be
  sound as a near-necessary condition, not merely a nice-to-have.
