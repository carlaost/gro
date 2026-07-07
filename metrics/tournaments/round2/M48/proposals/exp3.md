# M48 — End-to-end reproducibility bundle (expander 3)

## 1. Expanded reasoning

### 1.1 What this indicator is actually asking
The ledger line is: *"Do figure + data + code co-exist across layers for actual end-to-end
replication (constraints, setup, comprehensive reporting)?"* This is not "does `src/` exist" or
"does `data/` exist" checked independently — those are single-layer presence checks other metrics
already cover. M48 is a **joint-sufficiency, cross-layer** check: given everything the ARA captured
in `evidence/` (§9), `data/` (§11), and `src/` (§10), plus the scoping/setup information in
`logic/solution/constraints.md` and `src/configs/*.md`, **could an independent party actually
attempt to reproduce the reported numbers**, end to end — from raw/accessioned data, through a
concretely specified pipeline with concretely specified parameters, to a result that can be checked
against the transcribed figures/tables?

That is a materially different question from "is each leg present," because:
- A repo can exist (`src/execution/*.py` present) while `data/dataset.md` never states whether the
  input data is open or gated — reproduction stalls at step 1 regardless of code quality.
- `data/dataset.md` can state open accessions while `src/configs/*.md` never gives the actual
  parameter values used (only "see Methods") — reproduction stalls at the pipeline step even with
  data in hand.
- Both data and code can be well specified while `constraints.md` never states the boundary
  conditions/assumptions under which the result holds — a technically-successful re-run produces a
  number nobody can correctly interpret as confirming or refuting the original claim.
- `evidence/` can transcribe exact table values while nothing in `src/` or `data/` explains how those
  values were derived — the reproduction target exists but the reproduction path does not.

So the correct mental model is a **chain**, not a checklist: fig, data, code, and
constraints/setup are four links, and the artifact's end-to-end-reproducibility value is bounded by
its *weakest* link, not their average. A 3-of-4-strong, 1-of-4-absent bundle is not "75% good" for
this purpose — it is exactly as reproducible as its missing link allows, which is often close to not
reproducible at all. This asymmetry (weakest-link, not mean) is the single most important design
choice below, and it's what makes this metric non-redundant with a generic "how many layers are
populated" average.

### 1.2 What it must reward
- **Genuine specificity that lets an outsider act**, not just narrative completeness: exact version
  pins in `environment.md`, exact accession IDs + access tier in `dataset.md`, exact parameter
  values (not "see Methods") in `configs/*.md`, exact boundary conditions in `constraints.md`.
- **Honest, reasoned absence** over silence: §10's own availability notes are explicit that a pure
  meta-analysis correctly has no `src/execution/` (fabricating a stub would be worse, not better),
  and that a huge external repo intentionally not cloned should be disclosed in `artifacts.md` rather
  than silently dropped. This metric must reward the *disclosure*, while still scoring the *ceiling*
  on end-to-end reproducibility lower than a fully-captured leg — disclosure earns partial credit,
  never full credit, because the reproduction is still, factually, harder or impossible.
- **Cross-leg coherence**: config parameters that actually correspond to the method/pipeline named in
  `constraints.md`/method files; dataset variables that actually correspond to what the evidence
  tables/figures report; a code-availability statement in `environment.md` that is consistent with
  what `artifacts.md` claims about the repo.
- **Comprehensive reporting of setup**, meaning the specific things called out in §10: random seeds
  (or an honest "not specified in paper"), hardware, key dependency versions, and per-parameter
  rationale/sensitivity in `configs/*.md`.

### 1.3 What it must NOT reward
- Padding: an `environment.md` or `configs/*.md` that is present and long but full of "Not specified
  in paper" placeholders and vague values. Presence of the file is necessary but not sufficient.
- A `src/execution/*.py` stub whose grounding tag is `reconstructed` when it should be `transcribed`
  (or vice versa), or a reconstructed file with invented API names/constants not traceable to any
  real source — §10's availability notes call this out as an explicit FAIL condition, and it must
  zero out (not merely discount) the code leg, because it actively misleads a reproducer rather than
  just omitting information.
- A provided repo's real code reduced to a pointer in `artifacts.md` — the other explicit §10 FAIL
  condition — must be penalized as a **silent gap**, not credited as "artifacts.md exists."
- A `quantitative_plot` evidence file with neither a data table nor a low-confidence trend-summary
  fallback (§9's explicit structural-failure case) — this breaks the "figure" leg outright since there
  is no reproduction target at all, exact or approximate.
- Blanket "data available" language in `dataset.md` that collapses open-metadata vs.
  controlled-raw-access into one claim (§11's explicit access-tier-honesty defect) — must be scored
  as a coherence violation on the data leg, not full credit for "data leg present."
- A `constraints.md` that is technically present but degenerate ("no limitations stated") — §7 flags
  this itself as a red flag since virtually every paper states some caveat.

### 1.4 Failure modes / gaming routes and mitigations
| Gaming route | Mitigation |
|---|---|
| Inflate leg-count by filing thin/boilerplate files in all four locations | Score each leg on *specificity density* (concrete values/IDs/version numbers per file), not mere file existence |
| Claim "honestly disclosed absence" to dodge the fabrication penalty when a repo was actually dropped silently | External liveness check ([ext] step below): resolve any repo/accession URL named in `artifacts.md`/`dataset.md`; if a *named, disclosed* URL is unreachable that's a lesser problem (staleness) than an *undisclosed* absence, so the check specifically targets whether disclosure and reality match, not just whether URLs work |
| Reconstructed code stub dressed up as faithful capture | Grounding-tag audit: presence of `# Grounding: transcribed`/`reconstructed` header is mandatory; an LLM classification step (§2.3) flags invented identifiers not traceable to `environment.md`/method files |
| Mark `exact_from_labels` when actually eyeballed | Cross-check `Reading confidence` against whether the same figure's trend-summary hedges ("appears to," "approximately") — mismatch flagged as a coherence defect |
| Bury a missing leg's effect by only reporting an arithmetic mean across legs | Use a weakest-link (soft-min / harmonic-mean-like) combinator, not arithmetic mean, so no amount of over-performing on 3 legs can buy back a fourth that's silently missing |
| Genre-game: claim "this is a pure-theory paper, no data/code expected" to justify blanket absence | Cross-check the claim against `PAPER.md`/`logic/solution/` method files and `logic/problem.md`: if any method file names a computational pipeline, dataset, or tool, the "correctly absent" credit is revoked and it scores as a silent gap instead |

### 1.5 How the assessment-critique's notes change the design
The ledger explicitly flags this metric as ranking top-10 **because** it is net-new versus the ARA
verifier's D6 (which merely checks that reproducibility is *mentioned*) and tighter-scoped than a
generic reproducibility check. Two design consequences preserved here:
1. The metric must produce a signal D6 cannot: D6 passes on a single sentence claiming
   reproducibility; M48 requires the actual cross-layer artifacts to be present, specific, and
   mutually consistent. The compute workflow below never reads for a reproducibility *claim* — it
   only reads for reproducibility *substance* across §9/§10/§11/§7.
2. "Tighter-scoped" means this metric should resist the temptation to re-litigate each layer's
   internal quality (that's other metrics' job — e.g. an evidence-completeness metric, a
   code-grounding metric). M48's unique contribution is the AND/coherence/weakest-link layer on top,
   so the scoring function below intentionally keeps single-leg quality checks minimal/coarse and
   spends its discriminative power on cross-leg linkage and the honest-absence-vs-silent-gap
   distinction.

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields)
- `evidence/README.md` — completeness note, per-object `File`/`Source`/`Claims` rows.
- `evidence/tables/*.md`, `evidence/figures/*.md` — `Extraction type`/`Figure type`, `Extraction
  method`, `Reading confidence`, presence/absence of a data table, `Trend summary`.
- `data/dataset.md` (+ `data/preprocessing.md` if present) — presence/absence entirely; if present,
  the `Source / access` access-tier language, accession IDs, `Provenance`.
- `src/environment.md` — `Language/runtime`, `Framework`, `Hardware`, `Key dependencies`, `Random
  seeds`, `Code availability` / `Data availability` subsections.
- `src/artifacts.md` — per-block `File(s) in repo`, `Nature`, `How to use / run`.
- `src/configs/*.md` — per-parameter `Value`, `Rationale`, `Sensitivity`, `Source`.
- `src/execution/*.{py,r,...}` — first-line grounding tag, whether the file is a full function body
  or a `NotImplementedError` stub.
- `logic/solution/constraints.md` — `Boundary conditions`, `Assumptions`, `Known limitations`, and
  the compiler-added `Additional caveats surfaced during compilation` section.
- (cross-check only) `logic/problem.md` / other `logic/solution/*.md` method files — used solely to
  verify a claimed "no data/code expected" genre justification is not contradicted by a described
  pipeline elsewhere.

### 2.2 Step-by-step procedure

```
STEP 0 — Load & existence map
  For each of the four legs {FIG, DATA, CODE, SCOPE}, record which files exist:
    FIG   = evidence/README.md + evidence/tables/* + evidence/figures/*
    DATA  = data/dataset.md (+ preprocessing.md)
    CODE  = src/environment.md + src/artifacts.md + src/configs/* + src/execution/*
    SCOPE = logic/solution/constraints.md (+ relevant method files for genre cross-check)

STEP 1 — Deterministic structural checks (no LLM)
  FIG:
    - fig_structural_ok = for every quantitative_plot figure, (has data table) OR
      (Reading confidence == low AND has Trend summary). Else flag structural_failure.
    - fig_completeness = README.md accounts for 100% of numbered Table N/Figure N mentions
      (either filed or named-with-reason). Parse by regex-counting "Table \d+"/"Figure \d+" in
      Source/PAPER.md references vs. files present vs. names in the completeness-note prose.
  DATA:
    - data_present = data/dataset.md exists.
    - access_tier_stated = regex/keyword scan for an explicit tier word set
      {"open", "controlled", "restricted", "by-request", "dbGaP", "consortium"} co-occurring with
      an access-related header (## Provenance and access / **Source / access**).
  CODE:
    - env_present = src/environment.md exists.
    - grounding_tagged = every src/execution/*.py|r file's first non-blank line matches
      `# Grounding: (transcribed|reconstructed)`; missing tag => hard flag.
    - config_specificity = fraction of src/configs/*.md parameter blocks whose **Value** is not
      one of {"", "Not specified in paper", "see Methods", "default"}.
  SCOPE:
    - scope_present = logic/solution/constraints.md exists.
    - scope_thin = constraints.md has <2 total bullets across all sections, OR contains only a
      single generic "no limitations" line => flag thin.

STEP 2 — [ext] Liveness / consistency check (optional but recommended; deterministic once run)
  For every URL / accession ID named in src/artifacts.md ("File(s) in repo") or
  data/dataset.md ("Source / access"): issue an HTTP HEAD/GET (repo URLs) or accession-format
  validation (GEO/dbGaP/PROSPERO ID pattern match) call.
    - resolvable_and_disclosed: URL/ID present and resolves/validates -> no penalty.
    - disclosed_but_dead: named but unreachable (paper aged out, moved) -> minor penalty
      (staleness, not dishonesty).
    - Absence of ANY named identifier where PAPER.md / method files describe a released dataset
      or repo (see STEP 3 cross-check) -> silent_gap, full leg penalty.

STEP 3 — [LLM] Cross-leg semantic classification
  One structured call per artifact, prompt below. This is the only place judgment enters; every
  other step is regex/structural.

  PROMPT (verbatim template):
  """
  You are auditing ONE compiled research artifact for cross-layer reproducibility. You are given
  four excerpts: (A) evidence/README.md + any structural-failure flags already computed, (B) the
  full text of data/dataset.md (or "ABSENT"), (C) the full text of src/environment.md +
  src/artifacts.md + src/configs/*.md excerpts (or "ABSENT"), (D) the full text of
  logic/solution/constraints.md + one-line summaries of any other logic/solution/*.md method files.

  For each of the three legs DATA, CODE, SCOPE that is ABSENT or materially thin, classify its
  absence as exactly one of:
    - "genre_correct_disclosed": the source's own genre (e.g. pure meta-analysis, theory paper,
      abstract-only) makes this leg legitimately inapplicable or unreachable, AND the artifact says
      so explicitly (e.g. a "Code availability" paragraph explaining why no code exists).
    - "silent_gap": the leg is missing/thin with no explanation, OR other evidence in the artifact
      (a method file describing a computational pipeline, a dataset name mentioned in problem.md,
      a repo URL mentioned in PAPER.md) contradicts the absence.
    - "fabricated_or_mismatched": content is present but internally inconsistent with its own
      claimed type (e.g. a "reconstructed" code file using function/variable names never
      mentioned anywhere else in the artifact; a dataset.md claiming blanket "available" without
      any access-tier qualifier despite the paper plausibly having tiered access).

  Then, independent of the above, rate CROSS_LEG_COHERENCE on a 0-3 scale:
    0 = legs actively contradict each other (e.g. configs describe a pipeline stage never
        mentioned in constraints.md/method files; dataset variables never appear in any
        evidence table).
    1 = legs are independently plausible but you cannot verify any linkage between them.
    2 = most legs cross-reference correctly (e.g. config values match a method file's named
        parameters; dataset accession's key variables appear in evidence tables).
    3 = full, explicit, verifiable linkage across all present legs.

  Output STRICT JSON:
  {
    "data_leg": "genre_correct_disclosed"|"silent_gap"|"fabricated_or_mismatched"|"n/a_full_present",
    "code_leg": same enum,
    "scope_leg": same enum,
    "cross_leg_coherence": 0-3,
    "one_line_justification_per_field": {...}
  }
  """

  Turn the JSON into deterministic sub-scores via the fixed lookup table in STEP 4 (Step 3 never
  free-hands a numeric score itself — only a categorical label — so the LLM cannot directly inflate
  the metric; it only supplies the classification, the arithmetic is fixed code).

STEP 4 — Deterministic scoring (real Python)
  See §2.3 for the executable scoring function that consumes STEP 1/2/3 outputs.
```

### 2.3 Scoring function (Python, against the documented artifact shape)

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LegStatus(Enum):
    FULL = "full"                          # present, specific, not flagged
    GENRE_CORRECT_DISCLOSED = "genre_correct_disclosed"
    DISCLOSED_BUT_DEAD = "disclosed_but_dead"   # STEP 2 liveness result
    SILENT_GAP = "silent_gap"
    FABRICATED_OR_MISMATCHED = "fabricated_or_mismatched"


# Per-leg credit for each status. Honest disclosure earns partial credit (the reproduction
# ceiling really is lower), silent gaps earn much less (undisclosed, so a reproducer wastes
# effort discovering the gap themselves), fabrication is zeroed (actively misleading).
LEG_CREDIT = {
    LegStatus.FULL: 1.00,
    LegStatus.GENRE_CORRECT_DISCLOSED: 0.45,
    LegStatus.DISCLOSED_BUT_DEAD: 0.55,
    LegStatus.SILENT_GAP: 0.10,
    LegStatus.FABRICATED_OR_MISMATCHED: 0.00,
}

COHERENCE_MULTIPLIER = {0: 0.55, 1: 0.75, 2: 0.90, 3: 1.00}


@dataclass
class Step1Structural:
    fig_structural_ok: bool
    fig_completeness_ratio: float          # 0..1, filed+accounted / total numbered objects
    data_present: bool
    access_tier_stated: bool
    env_present: bool
    grounding_all_tagged: bool
    config_specificity_ratio: float        # 0..1
    scope_present: bool
    scope_thin: bool


@dataclass
class Step3Semantic:
    data_leg: LegStatus
    code_leg: LegStatus
    scope_leg: LegStatus
    cross_leg_coherence: int               # 0..3


_JSON_LABEL_TO_STATUS = {
    "n/a_full_present": LegStatus.FULL,
    "genre_correct_disclosed": LegStatus.GENRE_CORRECT_DISCLOSED,
    "silent_gap": LegStatus.SILENT_GAP,
    "fabricated_or_mismatched": LegStatus.FABRICATED_OR_MISMATCHED,
}


def parse_step3_response(raw_json: dict) -> Step3Semantic:
    """Deterministic parse of the STEP 3 [LLM] JSON output into the closed LegStatus enum —
    the only place a model output touches the pipeline, and it is a single dict lookup, so an
    unrecognized label fails loudly (KeyError) rather than silently defaulting to a favorable
    status."""
    return Step3Semantic(
        data_leg=_JSON_LABEL_TO_STATUS[raw_json["data_leg"]],
        code_leg=_JSON_LABEL_TO_STATUS[raw_json["code_leg"]],
        scope_leg=_JSON_LABEL_TO_STATUS[raw_json["scope_leg"]],
        cross_leg_coherence=int(raw_json["cross_leg_coherence"]),
    )


def score_fig_leg(s: Step1Structural) -> float:
    """FIG is scored structurally only — evidence/ is mandatory core per §9, so any degree of
    absence here is always a defect, never a genre-correct absence (a paper with zero numbered
    objects still must say so honestly in README.md, which fig_completeness_ratio captures)."""
    if not s.fig_structural_ok:
        # structural failure (quantitative_plot with neither table nor low-confidence trend
        # summary) is a hard floor regardless of completeness ratio
        return min(0.15, s.fig_completeness_ratio * 0.15)
    return s.fig_completeness_ratio  # 1.0 = every numbered object filed or accounted for


def score_leg(status: LegStatus, specificity_ratio: float = 1.0) -> float:
    base = LEG_CREDIT[status]
    if status == LegStatus.FULL:
        # even "full" presence is discounted by how specific/concrete the content actually is
        # (defends against padding: files exist but are full of "Not specified in paper")
        return base * max(0.3, specificity_ratio)
    return base


def weakest_link_combine(leg_scores: list[float]) -> float:
    """Soft-min via harmonic mean: punishes any single weak leg far more than an arithmetic
    mean would, without the brittleness of a hard min() (which would make two artifacts with
    scores [0.01, 1, 1, 1] and [0.01, 0.01, 0.01, 0.01] score identically)."""
    eps = 1e-6
    n = len(leg_scores)
    return n / sum(1.0 / max(s, eps) for s in leg_scores)


def compute_m48(step1: Step1Structural, step3: Step3Semantic,
                 data_liveness_dead: bool = False,
                 code_liveness_dead: bool = False) -> dict:
    fig_score = score_fig_leg(step1)

    # STEP 3's LLM call only emits a status for legs that are ABSENT/thin/suspect; a leg it
    # reports as "n/a_full_present" means STEP 1 already found it present, specific, and
    # unflagged, so it resolves straight to FULL. A liveness failure (STEP 2) downgrades a
    # nominally-FULL leg to DISCLOSED_BUT_DEAD even if STEP 3 didn't flag it, since the LLM
    # cannot itself verify external URLs/accessions.
    def resolve(step3_status: LegStatus, liveness_dead: bool) -> LegStatus:
        if step3_status == LegStatus.FULL and liveness_dead:
            return LegStatus.DISCLOSED_BUT_DEAD
        return step3_status

    data_status = resolve(step3.data_leg, data_liveness_dead)
    code_status = resolve(step3.code_leg, code_liveness_dead)
    scope_status = step3.scope_leg  # no external liveness check applies to constraints.md

    data_score = score_leg(data_status)
    code_score = score_leg(code_status, specificity_ratio=step1.config_specificity_ratio)
    scope_score = score_leg(scope_status)
    if not step1.scope_present or step1.scope_thin:
        scope_score = 0.0  # constraints.md is mandatory core; true absence, or a degenerate
                            # "no limitations stated" stub, is a hard floor per §7's own notes

    leg_scores = [fig_score, data_score, code_score, scope_score]
    combined = weakest_link_combine(leg_scores)
    final = combined * COHERENCE_MULTIPLIER[step3.cross_leg_coherence]

    return {
        "fig_leg": round(fig_score, 3),
        "data_leg": round(data_score, 3),
        "code_leg": round(code_score, 3),
        "scope_leg": round(scope_score, 3),
        "cross_leg_coherence": step3.cross_leg_coherence,
        "weakest_link_combined": round(combined, 3),
        "final_score": round(final, 3),   # 0.0 - 1.0
    }
```

Notes on the function:
- `score_fig_leg` never returns a "genre-correct absence" credit — §9's availability notes are
  explicit that evidence/ absence (even for paywalled/abstract-only sources) should "read as a
  near-total loss of grounding capacity," so FIG has no honest-absence discount, only the
  completeness-ratio floor. This matches the brief's "penalize missing... never skip" instruction
  most literally for this leg.
- `data`/`code`/`scope` legs *do* get the honest-disclosure discount (0.45) because §10/§11's own
  availability notes explicitly validate genre-correct absence as a legitimate, non-defective state
  for those layers — but the discount is capped well below 1.0 because the metric's subject
  (end-to-end reproducibility) is a real capability question, not just an honesty question: a
  legitimately-absent-and-disclosed code leg still means the work cannot be computationally
  reproduced, whatever the reason.
- The harmonic-mean combinator means an artifact scoring e.g. `[1.0, 1.0, 1.0, 0.10]` (silent gap on
  scope) lands at combined ≈ 0.28, not the arithmetic-mean 0.78 — this is the load-bearing
  "co-exist... for actual end-to-end replication" logic from the brief.
- `cross_leg_coherence` is a final multiplier (0.55-1.00), not an additive term, so a bundle with
  four individually-strong-looking legs that don't actually reference each other is capped at 90% of
  its combined score, and one with active contradictions is capped at 55%.

## 3. Why hard to Goodhart, and composition with the suite

**Hard to Goodhart because:**
1. The scoring arithmetic (STEP 4) is entirely fixed code; the only LLM touchpoint (STEP 3) emits
   categorical labels from a closed enum, each independently checkable against the artifact text
   (the `one_line_justification_per_field` output is auditable), not a free-form numeric score. An
   artifact author (or an ARA-compiler trying to game this specific metric) cannot simply write more
   words into `constraints.md` or `configs/*.md` — the `config_specificity_ratio` and
   `fig_completeness_ratio` computations are regex/structural over concrete value-bearing fields
   (numbers, IDs, version strings), so padding with prose doesn't move the score.
2. The weakest-link combinator specifically defeats the most obvious gaming strategy (over-invest in
   3 legs, drop the 4th quietly) — this was the primary design lever pulled in §2.3, directly in
   response to the brief's "co-exist... end-to-end" framing.
3. The honest-disclosure vs. silent-gap distinction, cross-checked against `PAPER.md`/other
   `logic/solution/*.md` files in STEP 3, closes the loop on the most tempting cheap win: claiming
   "genre-correct absence" for a leg that the rest of the artifact's own text contradicts (e.g. a
   method file that clearly describes running code, next to an `environment.md` claiming "analytical
   — none"). This is checkable and catchable precisely because ARAs are internally cross-referenced
   by design (§9-§11 all point back to claims/methods).
4. The optional [ext] liveness/accession-format check (STEP 2) adds a ground-truth anchor outside
   the artifact's own text — a fabricated or long-dead repo URL / malformed accession ID cannot be
   talked around by better prose, since it's checked against the real world, not the document.

**Composition with the rest of the suite:** M48 deliberately does *not* re-score single-layer
quality (evidence transcription fidelity, code style, dataset documentation completeness in
isolation) — those are the province of other metrics and of the ARA verifier's per-layer checks
(e.g. §11 Evidence Ledger Completeness for Seal Level 1). M48's unique contribution, preserved from
the ledger's top-10 ranking rationale, is the **AND-of-legs plus cross-reference-and-honesty** layer
on top: it is possible for an ARA to score well on every individual per-layer metric and still score
low on M48 (each leg locally fine, but the legs don't compose into an actually-reproducible whole),
and that gap is exactly the net-new signal this metric is scoped to catch. It is complementary to,
and strictly tighter than, the ARA verifier's D6 "reproducibility is mentioned" check: D6 can pass on
a single sentence, M48 requires the sentence to be backed by concrete, cross-referenced, and honestly
scoped artifacts across three-plus layers.

M48 expander3: done
