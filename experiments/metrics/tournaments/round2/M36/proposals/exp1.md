## M36 — Multi-perspective triangulation

### 1. Expanded reasoning

**Why this signals good science.** Independent methods fail in different ways. A wet-lab assay's
error modes (batch effects, reagent variance, small-n biological noise) are largely uncorrelated with
a computational model's error modes (misspecification, overfitting, distributional-shift). When a
claim is corroborated across two or more such independent lenses, the joint probability that *both*
error modes happened to point the same direction is much lower than either lens's individual error
rate — this is the classical epistemic case for triangulation, and it is a property of the *design*
of the study, not of any single result's p-value or effect size. A paper that only ever looks through
one lens (however rigorously) cannot, by construction, rule out that its entire conclusion is an
artifact of that lens's specific failure mode. This is exactly the kind of structural property that
is invisible to per-claim statistical checks and to the ARA verifier (which validates internal
consistency of a single artifact, not epistemic diversity of the underlying methodology) — which is
why the assessment-critique correctly flagged it as genuinely net-new.

**What it must reward.** Genuine cross-paradigm corroboration where:
- the lenses have *different* failure modes (wet-lab vs. computational; simulation vs. formal proof;
  observational cohort vs. RCT; algorithmic model vs. mechanistic/analytical derivation), and
- the paper's own constraints/method layer *shows its work* on how the lenses relate — i.e., it states
  where they converge, where they diverge, and what bound each one places on the others' claims.

**What it must NOT reward** (the gaming surface):
- **Padding via pipeline-splitting.** Describing sequential steps of a single pipeline (e.g.,
  "preprocessing" then "modeling" then "evaluation") as if they were separate lenses. All three share
  the same failure mode (garbage-in/garbage-out from the same data source) and are not independent.
- **Ensemble-as-triangulation.** Running several ML architectures, several hyperparameter settings, or
  several statistical tests *on the same dataset with the same assumptions* is model comparison, not
  triangulation — it does not reduce the shared-failure-mode risk (a biased/contaminated dataset
  sinks every model equally).
- **Token secondary analysis.** A one-paragraph "we also checked X computationally" bolted on without
  integration is pseudo-triangulation: it exists to be checked off, not to bound the claim.
- **Same-modality replication mislabeled as multi-perspective.** Two wet-lab assays, or two cohorts of
  the same observational design, are replication (valuable, but a different metric's job) — not
  triangulation. This metric must stay scoped to *epistemic-basis diversity*, not *count of analyses*,
  to avoid redundancy with robustness/replication-style metrics elsewhere in the suite.
- **Overclaiming past a single lens.** A single-lens paper is not itself a defect (many rigorous RCTs
  or pure formal papers are legitimately single-lens) — the defect is claiming multi-perspective
  support that isn't there, or a multi-lens paper's constraints layer failing to acknowledge the
  particular boundary the combination creates (e.g., "computational predictions were validated in only
  3 cell lines" *should* appear in `constraints.md` and often doesn't).

**How the assessment-critique's notes shape the design.** M36 ranked top-10 specifically because it
is scoped tighter than, and absent from, the ARA verifier and round-1 proposals. To preserve that
edge, this expansion deliberately narrows "multi-perspective" to *cross-failure-mode* method
combination (not method count, not dataset count) and requires the constraints layer to reflect the
combination explicitly — a check that a generic "did they use >1 method" verifier rule would not make.

### 2. Generation / compute workflow

**Inputs (artifact fields, §7 `logic/solution/`):**
- `constraints.md` — required; read all sections (`Boundary conditions`, `Assumptions`,
  `Known limitations`, and the optional `Additional caveats surfaced during compilation` subsection).
- All sibling method files present (`study_design.md`, `method.md`, `architecture.md`, `algorithm.md`,
  `heuristics.md`, `formalization.md`, `proofs.md`, `design.md`, or genre-specific equivalents) — zero
  or more, per the shape doc's cardinality notes.
- Availability of the whole `logic/solution/` directory and of each file is itself an input (per the
  hard constraint): a paper reduced to bare mandatory `constraints.md` with no method files (the
  "abstract-only" floor case in the shape doc) is informative and must be scored, not skipped.

**Step 1 — Assemble.** Concatenate `constraints.md` + every present method file into one text bundle,
tagged by source filename. If `logic/solution/` is missing entirely or `constraints.md` is
missing/empty, do not call any [sem] step — go straight to the floor score (Step 7, gate).

**Step 2 — [sem] Lens extraction.** One LLM call over the bundle:

> *Prompt:* "You are given the full text of a scientific paper's method-layer artifact
> (constraints + method files, each tagged with its source filename). List every distinct
> epistemically-independent method/evidence-generation lens actually employed in the study. Two
> activities count as genuinely distinct lenses ONLY if they have different failure modes — e.g., a
> wet-lab assay's noise sources differ from a computational model's misspecification risk. Do NOT
> split a single sequential pipeline into separate lenses. Do NOT count hyperparameter variants,
> architecture variants, or ensemble members of the same modeling paradigm as separate lenses. Do NOT
> count two datasets/cohorts of the same collection modality as separate lenses (that is replication,
> not triangulation). Choose lens labels from this list where applicable, else use 'other: <label>':
> {wet-lab/bench experiment, computational simulation, computational/ML model training or inference,
> formal proof or mathematical derivation, clinical/observational cohort data, systematic literature
> synthesis or meta-analysis, field/ecological observation, econometric or quasi-experimental design}.
> For each lens returned, quote the exact grounding sentence(s) and its source filename. Output strict
> JSON: `{"lenses": [{"name": str, "quote": str, "file": str}], "lens_count_distinct": int}`."

**Step 3 — [sem] Independence audit (anti-gaming filter on Step 2's output).** Second call, given the
Step 2 JSON plus the `study_design.md`/`method.md` data-provenance sections:

> *Prompt:* "For each pair of lenses in this list: {lenses}, state whether they share the same
> underlying data source and the same core assumptions (in which case they are NOT independent for
> triangulation purposes, regardless of what the previous step labeled them). Output JSON:
> `{"independent_lens_count": int, "collapsed_pairs": [[lens_a, lens_b, reason]]}`."
> Use `independent_lens_count` (not the raw `lens_count_distinct`) downstream.

**Step 4 — [sem] Integration check.** Given the independent lens list and the full bundle:

> *Prompt:* "Does the constraints/method text explicitly state how findings from these lenses
> converge, diverge, or bound one another (e.g., 'computational predictions were validated against
> wet-lab knockdown results'; 'cohort A's effect estimate was compared against cohort B's')? Quote the
> integration statement verbatim if present. Classify as one of `explicit` (a stated comparison/
> validation/bounding relationship), `implicit` (lenses are both used and both discussed but never
> explicitly related to each other), or `none`. Output JSON: `{"integration_level": str, "quote": str|null}`."

**Step 5 — [sem] Constraints-reflects-combination check.** Only run if `independent_lens_count >= 2`:

> *Prompt:* "Given that this work combines these independent lenses: {lenses}, does the
> `Boundary conditions` / `Known limitations` section of constraints.md state a limitation that is
> *specific to combining these lenses* (e.g., a scope mismatch between what one lens covers and what
> another claims, or an n/sample-size disparity between lenses)? Answer `true`, `false`, or
> `not_applicable_single_lens`. Output JSON: `{"constraints_reflect_multilens": bool|null, "evidence": str|null}`."

**Step 6 — Deterministic scoring.** Real Python against the artifact shape and the (now
deterministically-shaped) [sem] outputs from Steps 2–5:

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class LensRecord:
    name: str
    quote: str
    file: str


@dataclass
class SemOutputs:
    """Deterministic-shaped outputs of the Step 2-5 [sem] calls."""
    independent_lens_count: int              # Step 3 output, post anti-gaming collapse
    integration_level: str                   # Step 4: "explicit" | "implicit" | "none"
    constraints_reflect_multilens: Optional[bool]
    # Step 5: True/False, or None if independent_lens_count < 2 (legitimately n/a — see Step 7)


def score_m36(solution_files: dict[str, str], sem: Optional[SemOutputs]) -> float:
    """
    solution_files: {filename: raw_markdown_text} for everything actually present under
                     logic/solution/ (e.g. {"constraints.md": "...", "study_design.md": "..."}).
                     An empty dict means the directory itself is missing.
    sem: precomputed outputs of the Step 2-5 [sem] calls, or None if those calls could not
         be executed at all (e.g. tool failure) — this is an availability failure of the
         metric's own inputs and must be penalized, never skipped/N-A.
    Returns a score in [0.0, 1.0].
    """
    constraints_text = solution_files.get("constraints.md", "").strip()

    # --- Gate: availability of the mandatory core artifact ---
    if not solution_files or not constraints_text:
        # logic/solution/ missing, or constraints.md missing/empty: hard floor.
        # Unavailability is itself the score, not a reason to abstain.
        return 0.0

    if len(constraints_text.split()) < 25:
        # Degenerate boilerplate ("no limitations stated") is a red flag per the shape doc's
        # own availability notes — thin input, hard penalty, not a pass-through.
        return 0.05

    if sem is None:
        # The [sem] classification this metric depends on could not be run.
        # Penalize the missing evidence; do not exempt the artifact from scoring.
        return 0.05

    n = sem.independent_lens_count

    if n <= 1:
        # Legitimately single-lens (or no identifiable lens) work is not a "missing input"
        # case -- it is a real, low, substantive score on the triangulation axis. A small
        # bonus is given only if the single-lens scope limit is itself honestly stated.
        base = 0.15
        if "boundary" in constraints_text.lower() or "scope is limited" in constraints_text.lower():
            base += 0.05
        return round(min(base, 0.20), 3)

    # n >= 2: genuine triangulation candidate. Diminishing returns beyond 3 independent lenses
    # (a 4th and 5th lens add corroboration value but each increment is smaller, and very high
    # counts are themselves a padding-suspicion signal handled upstream in Step 3).
    lens_score = {2: 0.55, 3: 0.75}.get(n, 0.85)

    integration_multiplier = {
        "explicit": 1.00,
        "implicit": 0.70,
        "none": 0.40,   # parallel, disconnected lenses: still gameable, heavily discounted
    }.get(sem.integration_level, 0.40)

    score = lens_score * integration_multiplier

    # Whether constraints.md actually reflects the multi-lens combination's specific boundary.
    if sem.constraints_reflect_multilens is False:
        score *= 0.60          # combination exists but its boundary is unstated: real defect
    elif sem.constraints_reflect_multilens is None:
        score *= 0.80          # sub-check itself unavailable: penalized, not exempted

    return round(max(0.0, min(score, 1.0)), 3)
```

**Step 7 — Record provenance.** Persist the Step 2–5 JSON outputs alongside the numeric score so a
human or downstream auditor can see exactly which quotes grounded the lens count, the independence
collapse, and the integration classification — this is what makes the metric auditable rather than a
black-box LLM score.

### 3. Why it's hard to Goodhart

- **The independence filter (Step 3) is adversarial to the most obvious gaming move** — adding a
  cosmetic second analysis on the same data. Because the filter explicitly checks shared data
  source/assumptions, a padded "computational validation" run on the identical dataset with identical
  preprocessing collapses back to `independent_lens_count = 1` and scores at the single-lens floor
  (≤0.20), not the triangulation band.
- **The integration multiplier punishes disconnected-but-real lenses at 0.40–0.70×**, so simply having
  two genuinely independent lenses without ever relating them caps the score well below the ceiling —
  an author must actually do the comparative work (state where computational and wet-lab results
  agree/disagree/bound each other) to reach the top band, and that statement is itself checkable
  against the source text (verbatim quote required in Step 4).
- **Diminishing returns on lens count** (capped at 0.85 for the score component, not linear in N)
  removes the incentive to inflate lens count for its own sake, and Step 3's collapse mechanism
  actively punishes over-splitting a single pipeline into many labeled "lenses."
- **The constraints-reflects-combination check (Step 5)** is a second, independent surface an author
  would have to fabricate consistently — it requires the paper's own limitations section to name a
  boundary specific to the *combination*, not just each lens's boundary separately, which is a much
  harder text to fake plausibly than a generic limitations paragraph.
- **Penalize-don't-skip removes the "declare N/A" escape hatch**: an author cannot dodge a low score by
  omitting the method layer or leaving constraints.md boilerplate — both are floored at 0.0–0.05,
  strictly worse than an honest single-lens 0.15–0.20.

### 4. Composition with the rest of the suite

M36 is deliberately orthogonal to (a) statistical-rigor/robustness metrics that check *how well* a
single analysis was executed, (b) replication-style metrics that check *repetition within* one
modality, and (c) the ARA verifier's internal-consistency checks, which never reason about
epistemic-basis diversity at all. It shares raw inputs with any metric that also reads
`logic/solution/constraints.md` (e.g., a constraints-completeness or overclaiming metric), but its
scoring key — independent-lens count with a gaming-resistant collapse step, gated on explicit
integration language — is not derivable from those other metrics' outputs, so it adds signal rather
than restating it. Because it operates on the method/constraints layer rather than the evidence
tables, it also composes cleanly with evidence-layer metrics (e.g., a data-provenance metric) without
double-counting: this metric asks "were independent lenses combined and is that combination honestly
bounded," while an evidence-layer metric would ask "is each individual lens's data trustworthy" — the
two answers are informative even when they disagree (e.g., two well-sourced but non-integrated lenses
would score high on data-provenance and low on M36).
