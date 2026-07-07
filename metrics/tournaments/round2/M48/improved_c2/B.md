# M48 — End-to-end reproducibility bundle (cycle-2 improvement of exp3)

## Changes (cycle 2)

Judge critique (`critique_c1.md`) named exp3 as co-winner with four specific weaknesses/directions.
All four are fixed here, plus two workflow/Goodhart sharpenings that fall out of fixing them
correctly rather than cosmetically:

1. **Credit-ordering bug fixed.** `GENRE_CORRECT_DISCLOSED` (0.45) scored *below*
   `DISCLOSED_BUT_DEAD` (0.55) in exp3 — a legitimately-absent, honestly-disclosed leg was worth
   less than a leg whose promised link rotted. That's backwards: a dead link means the artifact
   asserted reproducibility infrastructure that no longer exists (a broken promise), whereas
   genre-correct disclosure never promised it and said so up front (an honest scope statement).
   §2.3 now sets `GENRE_CORRECT_DISCLOSED = 0.60 > DISCLOSED_BUT_DEAD = 0.55`, restoring the
   ordering the brief's honesty framing implies.
2. **Claims-weighting imported into the FIG leg (from exp1).** exp3 previously scored FIG
   completeness as a flat filed/total ratio, so a headline table missing counted the same as a
   padding table missing. §2.2 STEP 1 and §2.3 `score_fig_leg` now weight each numbered object by
   `1 + |claims it supports|` (per `evidence/README.md`'s `Claims` column), so an unfiled or
   unaccounted object tied to many claims costs the score far more than an unfiled object tied to
   none. This is the one place claims-weighting belongs in this metric — FIG is the only
   object-indexed leg (§9 is enumerable "Table N/Figure N"); DATA/CODE/SCOPE are whole-file checks
   with no natural per-claim decomposition, so the weighting is intentionally *not* smeared across
   all four legs (that would blur exp3's clean whole-leg arithmetic for no gain).
3. **SCOPE demoted from co-equal leg to gating floor.** The critique flagged that grading SCOPE
   (`constraints.md`) as a fourth co-equal member of the harmonic mean risks re-litigating whatever
   metric elsewhere in the suite owns limitations-statement *quality* (§7). Fixed: SCOPE no longer
   enters the weakest-link combinator at all. It becomes a post-combination multiplicative gate
   (`scope_gate`, §2.3) applied only to reproduction-relevant presence/thinness/fabrication — never
   to how thoughtfully-written the limitations are. This is deliberately shallow and non-redundant:
   M48 asks only "can a reproducer correctly interpret a re-run result," not "is this a good
   limitations section." Because it's a gate rather than a leg, it still enforces
   penalize-don't-skip (missing/thin scope still drags the final score down hard) without letting
   verbose-but-generic `constraints.md` prose buy differentiating credit the way a co-equal graded
   leg would allow.
4. **`cross_leg_coherence` moved out of the LLM entirely (imports exp4's anchor idea, more strictly
   than exp4 itself).** exp3's STEP 3 previously had the LLM self-report a bare 0–3 coherence
   integer — free-form judgment, the single softest point in an otherwise fixed-arithmetic design.
   §2.2 STEP 2.5 (new) replaces this with a fully deterministic anchor-extraction-and-match pass:
   regex/structured extraction of literal, checkable anchors (accession IDs, `n=` sample sizes,
   dependency versions, random seeds, config parameter values) from each leg's text, followed by a
   fixed function that buckets 0–3 from *counted, literal* matches and contradictions across legs.
   No LLM touches coherence scoring at all now — strictly tighter than exp4, which still let an LLM
   judge "anchor agreement." STEP 3's LLM role shrinks to exactly what regex cannot do: classifying
   *why* a leg is absent/thin (genre-correct vs. silent vs. fabricated), which unavoidably requires
   reading the artifact's prose.

Net effect: same core design (four-input reasoning, weakest-link-not-mean philosophy, graded
honest/silent/fabricated credit table) survives from exp3 because the critique validated it as
"best in field" — but the aggregation is now claims-aware where it should be, non-redundant where
it should be, and has strictly less surface for an LLM to freehand a favorable number.

---

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
  number nobody can correctly interpret as confirming or refuting the original claim. Note the verb:
  *interpret*, not *execute* — this is why SCOPE is handled as a gate on interpretability rather
  than a fourth executability leg (see §1.5 and §2.3).
- `evidence/` can transcribe exact table values while nothing in `src/` or `data/` explains how those
  values were derived — the reproduction target exists but the reproduction path does not.

So the correct mental model is a **weighted chain with an interpretability gate**: FIG, DATA, and
CODE are three links whose executability is bounded by the weakest of the three (soft-min, not
mean); SCOPE sits outside that chain as a multiplicative check on whether a technically-successful
re-run can be correctly read against the original claim. A bundle strong on FIG/DATA/CODE but with
a missing or fabricated `constraints.md` is not "75% good" — it is executable but not trustworthy,
which the gate captures without diluting the FIG/DATA/CODE weakest-link signal with a fourth
graded term.

### 1.2 What it must reward
- **Genuine specificity that lets an outsider act**, not just narrative completeness: exact version
  pins in `environment.md`, exact accession IDs + access tier in `dataset.md`, exact parameter
  values (not "see Methods") in `configs/*.md`, exact boundary conditions in `constraints.md`.
- **Headline-object fidelity over uniform coverage** in the FIG leg specifically: an evidence object
  that anchors many claims must be filed/accounted-for more than a peripheral one — see §2.3's
  claims-weighted `fig_completeness_ratio`. Uniform per-object credit (as in cycle-1 exp3) lets an
  artifact hide one missing headline table behind several well-filed minor ones; weighting closes
  that.
- **Honest, reasoned absence** over silence: §10's own availability notes are explicit that a pure
  meta-analysis correctly has no `src/execution/` (fabricating a stub would be worse, not better),
  and that a huge external repo intentionally not cloned should be disclosed in `artifacts.md` rather
  than silently dropped. This metric must reward the *disclosure*, while still scoring the *ceiling*
  on end-to-end reproducibility lower than a fully-captured leg — disclosure earns partial credit,
  never full credit, because the reproduction is still, factually, harder or impossible. Cycle 2
  additionally requires that disclosure be ranked *above* a decayed/dead link (§2.3 `LEG_CREDIT`
  ordering fix) — honesty about scope should never score worse than a broken promise.
- **Cross-leg coherence, now checkable rather than asserted**: literal, shared anchors — an
  accession ID that appears in both `dataset.md` and an evidence table's `Notes`; a parameter value
  in `configs/*.md` that matches a number named in `constraints.md`'s boundary conditions; a
  dependency version pinned once and referenced consistently. §2.2 STEP 2.5 makes this a grep-able
  computation, not an LLM impression.
- **Comprehensive reporting of setup**, meaning the specific things called out in §10: random seeds
  (or an honest "not specified in paper"), hardware, key dependency versions, and per-parameter
  rationale/sensitivity in `configs/*.md`.

### 1.3 What it must NOT reward
- Padding: an `environment.md` or `configs/*.md` that is present and long but full of "Not specified
  in paper" placeholders and vague values. Presence of the file is necessary but not sufficient.
- Padding the *evidence* layer specifically: filing several claims-irrelevant tables/figures cleanly
  while a headline, claims-dense object goes missing. Flat per-object credit would reward this;
  claims-weighted credit does not (§2.3).
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
  this itself as a red flag since virtually every paper states some caveat. This still zeroes the
  `scope_gate` (§2.3) even though SCOPE is no longer a graded leg — presence-only credit would be
  gameable by filing an empty-but-existing file.
- A verbose but generic `constraints.md`/`configs/*.md` written to farm co-equal-leg credit — no
  longer possible for SCOPE by construction (it's a boolean-ish gate, capped at 1.0 regardless of
  length), and structurally discouraged for CODE by `config_specificity_ratio` being computed over
  literal value fields, not prose length.
- An LLM emitting a generous coherence score because the surrounding prose reads fluently — no
  longer possible at all; coherence is computed from literal string/number matches (§2.2 STEP 2.5).

### 1.4 Failure modes / gaming routes and mitigations
| Gaming route | Mitigation |
|---|---|
| Inflate leg-count by filing thin/boilerplate files in all locations | Score each leg on *specificity density* (concrete values/IDs/version numbers per file), not mere file existence |
| Claim "honestly disclosed absence" to dodge the fabrication penalty when a repo was actually dropped silently | External liveness check ([ext] step): resolve any repo/accession URL named in `artifacts.md`/`dataset.md`; a *named, disclosed* URL that's unreachable is a lesser problem (staleness) than an *undisclosed* absence |
| Reconstructed code stub dressed up as faithful capture | Grounding-tag audit: presence of `# Grounding: transcribed`/`reconstructed` header is mandatory; STEP 3's classification flags invented identifiers not traceable to `environment.md`/method files |
| Mark `exact_from_labels` when actually eyeballed | Cross-check `Reading confidence` against whether the same figure's trend-summary hedges ("appears to," "approximately") — mismatch flagged as a coherence defect |
| Bury a missing leg's effect by only reporting an arithmetic mean across legs | Weakest-link (soft-min / harmonic-mean-like) combinator over FIG/DATA/CODE, so no amount of over-performing on two legs can buy back a third that's silently missing |
| **(cycle-2)** File several claims-irrelevant tables/figures cleanly while a headline object goes missing, banking on flat per-object averaging | Claims-weighted `fig_completeness_ratio` (§2.3): objects tied to more claims cost proportionally more when unfiled/unaccounted |
| **(cycle-2)** Write a long, generic `constraints.md` purely to farm graded co-equal-leg credit | SCOPE is a presence/non-thin/non-fabricated *gate* (capped at 1.0), not a graded leg — extra prose above the non-thin bar earns nothing |
| **(cycle-2)** Prompt/phrase STEP 3's classification call to talk the LLM into a generous free-form coherence number | Coherence is no longer an LLM output at all; it's computed from literal anchor extraction + match/contradiction counting (STEP 2.5), auditable against the source text independent of any model call |
| Genre-game: claim "this is a pure-theory paper, no data/code expected" to justify blanket absence | Cross-check the claim against `PAPER.md`/`logic/solution/` method files and `logic/problem.md`: if any method file names a computational pipeline, dataset, or tool, the "correctly absent" credit is revoked and it scores as a silent gap instead |

### 1.5 How the assessment-critique's notes change the design
The ledger explicitly flags this metric as ranking top-10 **because** it is net-new versus the ARA
verifier's D6 (which merely checks that reproducibility is *mentioned*) and tighter-scoped than a
generic reproducibility check. Design consequences preserved and (in cycle 2) sharpened:
1. The metric must produce a signal D6 cannot: D6 passes on a single sentence claiming
   reproducibility; M48 requires the actual cross-layer artifacts to be present, specific, and
   mutually consistent — now checked via literal anchor matches rather than an LLM's read of
   "consistency," which is a strictly harder bar for a compiler to satisfy by prose alone.
2. "Tighter-scoped" means this metric should resist the temptation to re-litigate each layer's
   internal quality (that's other metrics' job — e.g. an evidence-completeness metric, a
   code-grounding metric, and — newly explicit in cycle 2 — a limitations/constraints-quality
   metric that would own the depth of `constraints.md` content). M48's unique contribution is the
   AND/coherence/weakest-link-plus-interpretability-gate layer on top; keeping SCOPE as a gate
   rather than a graded leg is precisely what prevents M48 from quietly duplicating that other
   metric's job while still honoring penalize-don't-skip on the reproduction-relevant slice of
   `constraints.md` (does a reproducer have the boundary conditions to interpret a re-run, not is
   the limitations section well-written).

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields)
- `evidence/README.md` — completeness note, per-object `File`/`Source`/`Claims` rows. The `Claims`
  column is now load-bearing for scoring (cycle 2), not just descriptive.
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
  pipeline elsewhere, and as one of the four text pools scanned during anchor extraction.

### 2.2 Step-by-step procedure

```
STEP 0 — Load & existence map
  For each of FIG, DATA, CODE, SCOPE, record which files exist:
    FIG   = evidence/README.md + evidence/tables/* + evidence/figures/*
    DATA  = data/dataset.md (+ preprocessing.md)
    CODE  = src/environment.md + src/artifacts.md + src/configs/* + src/execution/*
    SCOPE = logic/solution/constraints.md (+ relevant method files for genre cross-check)

STEP 1 — Deterministic structural checks (no LLM)
  FIG:
    - fig_structural_ok = for every quantitative_plot figure, (has data table) OR
      (Reading confidence == low AND has Trend summary). Else flag structural_failure.
    - per_object_weight[i] = 1 + count(Claims listed for object i in README.md row)   # (cycle 2)
    - fig_completeness_ratio = sum(weight_i for filed-or-accounted objects i)
                                / sum(weight_i for all numbered objects i)
      Parse numbered-object universe by regex-counting "Table \d+"/"Figure \d+" against
      Source/PAPER.md references, files present, and names in the completeness-note prose;
      unaccounted objects get weight_i but contribute 0 to the numerator.
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

STEP 2.5 — [NEW, deterministic] Anchor extraction and cross-leg matching
  Purpose: replace the free-form LLM coherence rating with a literal, checkable computation.
  For each of the four text pools {FIG, DATA, CODE, SCOPE}, extract anchors by fixed pattern:
    - ACCESSION:  \b(GSE\d+|GDS\d+|PRJNA\d+|PRJEB\d+|SRP\d+|dbGaP\s*phs\d+|NCT\d{8}|
                  PROSPERO\s*CRD\d+|10\.\d{4,9}/\S+)\b
    - SAMPLE_N:   \bn\s*=\s*(\d+)\b  (case-insensitive), keyed by nearest cohort/dataset name
                  if one appears in the same sentence, else keyed generically as "n"
    - VERSION:    \b([A-Za-z][\w\-]*)\s+v?(\d+\.\d+(?:\.\d+)?)\b  (dependency name + version)
    - SEED:       \b(?:random\s+seed[s]?|seed)\s*[:=]?\s*(\d+)\b
    - PARAM:      src/configs/*.md **Value** fields, read structurally (name -> literal value),
                  not regex over prose
  Build ANCHOR_KEY = (type, normalized_label); for keys appearing in >=2 of the four pools:
    - values_match  -> increment `matches`
    - values_differ -> increment `contradictions` (e.g. dataset.md says n=482 for "cohort A,"
      constraints.md says n=410 for the same named cohort)
  Bucket into cross_leg_coherence (0-3), fixed rule, no model call:
    contradictions > 0        -> 0
    matches == 0               -> 1   (legs plausible in isolation, no verifiable linkage)
    matches in {1, 2}          -> 2
    matches >= 3                -> 3
  Every match/contradiction is a literal substring pair, independently greppable in the source
  files — this is the audit trail that replaces the old free-text `one_line_justification`.

STEP 3 — [LLM] Absence/thinness classification only (narrowed from cycle 1)
  One structured call per artifact. This is the only place judgment enters, and it now answers a
  strictly narrower question than cycle 1: it no longer touches coherence or scoring, only *why* a
  leg that STEP 1 already found absent/thin is absent/thin.

  PROMPT (verbatim template):
  """
  You are auditing ONE compiled research artifact for cross-layer reproducibility. You are given
  four excerpts: (A) evidence/README.md + any structural-failure flags already computed, (B) the
  full text of data/dataset.md (or "ABSENT"), (C) the full text of src/environment.md +
  src/artifacts.md + src/configs/*.md excerpts (or "ABSENT"), (D) the full text of
  logic/solution/constraints.md + one-line summaries of any other logic/solution/*.md method files.

  For each of the three legs DATA, CODE, SCOPE that STEP 1 found ABSENT or materially thin,
  classify its absence as exactly one of:
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

  You do NOT rate cross-leg coherence — that is computed separately from literal anchor matches.
  Only classify the reason for absence/thinness of each flagged leg.

  Output STRICT JSON:
  {
    "data_leg": "genre_correct_disclosed"|"silent_gap"|"fabricated_or_mismatched"|"n/a_full_present",
    "code_leg": same enum,
    "scope_leg": same enum,
    "one_line_justification_per_field": {...}
  }
  """

  Turn the JSON into deterministic sub-scores via the fixed lookup table in STEP 4 (Step 3 never
  free-hands a numeric score itself — only a categorical label — so the LLM cannot directly inflate
  the metric; it only supplies the classification, the arithmetic is fixed code).

STEP 4 — Deterministic scoring (real Python)
  See §2.3 for the executable scoring function that consumes STEP 1/2/2.5/3 outputs.
```

### 2.3 Scoring function (Python, against the documented artifact shape)

```python
from dataclasses import dataclass
from enum import Enum


class LegStatus(Enum):
    FULL = "full"                          # present, specific, not flagged
    GENRE_CORRECT_DISCLOSED = "genre_correct_disclosed"
    DISCLOSED_BUT_DEAD = "disclosed_but_dead"   # STEP 2 liveness result
    SILENT_GAP = "silent_gap"
    FABRICATED_OR_MISMATCHED = "fabricated_or_mismatched"


# Per-leg credit for each status. Honest disclosure earns partial credit (the reproduction
# ceiling really is lower), silent gaps earn much less (undisclosed, so a reproducer wastes
# effort discovering the gap themselves), fabrication is zeroed (actively misleading).
#
# (cycle 2 fix) GENRE_CORRECT_DISCLOSED (0.60) now scores ABOVE DISCLOSED_BUT_DEAD (0.55): an
# honestly-disclosed, legitimately-absent leg never promised reproducibility, whereas a dead link
# is a broken promise. The ordering in cycle 1 (0.45 < 0.55) had this backwards.
LEG_CREDIT = {
    LegStatus.FULL: 1.00,
    LegStatus.GENRE_CORRECT_DISCLOSED: 0.60,
    LegStatus.DISCLOSED_BUT_DEAD: 0.55,
    LegStatus.SILENT_GAP: 0.10,
    LegStatus.FABRICATED_OR_MISMATCHED: 0.00,
}

COHERENCE_MULTIPLIER = {0: 0.55, 1: 0.75, 2: 0.90, 3: 1.00}

# (cycle 2, new) SCOPE is no longer a co-equal leg in the weakest-link pool — see §1.5/#3 of the
# Changes note. It is a post-combination gate on *interpretability*, scaled by the same
# honest/silent/fabricated spectrum but deliberately capped well below 1.0 penalty range so it
# cannot silently reintroduce a fourth graded leg through the back door, while still enforcing
# penalize-don't-skip (a thin/missing/fabricated SCOPE meaningfully discounts the final score).
SCOPE_GATE = {
    LegStatus.FULL: 1.00,
    LegStatus.GENRE_CORRECT_DISCLOSED: 1.00,   # constraints.md is mandatory core in practice, but
                                                # this enum value is retained for completeness/
                                                # symmetry with the other legs' classification path
    LegStatus.SILENT_GAP: 0.35,
    LegStatus.FABRICATED_OR_MISMATCHED: 0.00,
}


@dataclass
class Step1Structural:
    fig_structural_ok: bool
    fig_completeness_ratio: float          # 0..1, CLAIMS-WEIGHTED (cycle 2) filed+accounted / total
    data_present: bool
    access_tier_stated: bool
    env_present: bool
    grounding_all_tagged: bool
    config_specificity_ratio: float        # 0..1
    scope_present: bool
    scope_thin: bool


@dataclass
class Step2Anchors:
    """Output of the new deterministic STEP 2.5 anchor pass — no LLM involved."""
    cross_leg_coherence: int               # 0..3, computed from literal match/contradiction counts
    matches: int
    contradictions: int


@dataclass
class Step3Semantic:
    data_leg: LegStatus
    code_leg: LegStatus
    scope_leg: LegStatus


_JSON_LABEL_TO_STATUS = {
    "n/a_full_present": LegStatus.FULL,
    "genre_correct_disclosed": LegStatus.GENRE_CORRECT_DISCLOSED,
    "silent_gap": LegStatus.SILENT_GAP,
    "fabricated_or_mismatched": LegStatus.FABRICATED_OR_MISMATCHED,
}


def parse_step3_response(raw_json: dict) -> Step3Semantic:
    """Deterministic parse of the STEP 3 [LLM] JSON output into the closed LegStatus enum — the
    only place a model output touches the pipeline, and it is a single dict lookup restricted to
    the absence/thinness classification, so an unrecognized label fails loudly (KeyError) rather
    than silently defaulting to a favorable status. Coherence no longer flows through this path."""
    return Step3Semantic(
        data_leg=_JSON_LABEL_TO_STATUS[raw_json["data_leg"]],
        code_leg=_JSON_LABEL_TO_STATUS[raw_json["code_leg"]],
        scope_leg=_JSON_LABEL_TO_STATUS[raw_json["scope_leg"]],
    )


def compute_cross_leg_coherence(matches: int, contradictions: int) -> int:
    """Fixed bucket rule over literal anchor match/contradiction counts (STEP 2.5). No model call;
    every input is a pair of literal substrings found by regex/structural extraction, independently
    greppable against the source files."""
    if contradictions > 0:
        return 0
    if matches == 0:
        return 1
    if matches in (1, 2):
        return 2
    return 3


def score_fig_leg(s: Step1Structural) -> float:
    """FIG is scored structurally only — evidence/ is mandatory core per §9, so any degree of
    absence here is always a defect, never a genre-correct absence (a paper with zero numbered
    objects still must say so honestly in README.md, which fig_completeness_ratio captures).
    fig_completeness_ratio is claims-weighted (cycle 2): objects tied to more claims cost
    proportionally more when unfiled, so padding minor objects cannot mask a missing headline one."""
    if not s.fig_structural_ok:
        return min(0.15, s.fig_completeness_ratio * 0.15)
    return s.fig_completeness_ratio


def score_leg(status: LegStatus, specificity_ratio: float = 1.0) -> float:
    base = LEG_CREDIT[status]
    if status == LegStatus.FULL:
        # even "full" presence is discounted by how specific/concrete the content actually is
        # (defends against padding: files exist but are full of "Not specified in paper")
        return base * max(0.3, specificity_ratio)
    return base


def weakest_link_combine(leg_scores: list[float]) -> float:
    """Soft-min via harmonic mean over FIG/DATA/CODE ONLY (cycle 2: SCOPE removed from this pool,
    see scope_gate below). Punishes any single weak leg far more than an arithmetic mean would,
    without the brittleness of a hard min() (which would make two artifacts with scores
    [0.01, 1, 1] and [0.01, 0.01, 0.01] score identically)."""
    eps = 1e-6
    n = len(leg_scores)
    return n / sum(1.0 / max(s, eps) for s in leg_scores)


def compute_m48(step1: Step1Structural, step2: Step2Anchors, step3: Step3Semantic,
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

    # (cycle 2) SCOPE: weakest-link pool now excludes SCOPE entirely; it becomes a gate applied
    # after the FIG/DATA/CODE combination. True absence or a degenerate ("no limitations stated")
    # stub still hard-floors it, consistent with §7's own red-flag note and penalize-don't-skip.
    if not step1.scope_present or step1.scope_thin:
        scope_gate = SCOPE_GATE[LegStatus.SILENT_GAP] if scope_status != LegStatus.FABRICATED_OR_MISMATCHED else 0.0
    else:
        scope_gate = SCOPE_GATE.get(scope_status, 1.00)

    leg_scores = [fig_score, data_score, code_score]
    combined = weakest_link_combine(leg_scores)
    final = combined * scope_gate * COHERENCE_MULTIPLIER[step2.cross_leg_coherence]

    return {
        "fig_leg": round(fig_score, 3),
        "data_leg": round(data_score, 3),
        "code_leg": round(code_score, 3),
        "scope_gate": round(scope_gate, 3),
        "cross_leg_coherence": step2.cross_leg_coherence,
        "coherence_matches": step2.matches,
        "coherence_contradictions": step2.contradictions,
        "weakest_link_combined_fig_data_code": round(combined, 3),
        "final_score": round(final, 3),   # 0.0 - 1.0
    }
```

Notes on the function:
- `score_fig_leg` never returns a "genre-correct absence" credit — §9's availability notes are
  explicit that evidence/ absence (even for paywalled/abstract-only sources) should "read as a
  near-total loss of grounding capacity," so FIG has no honest-absence discount, only the
  claims-weighted completeness-ratio floor. This matches the brief's "penalize missing... never
  skip" instruction most literally for this leg, and (cycle 2) does so proportionally to how much
  each missing object actually mattered to the artifact's claims.
- `data`/`code` legs *do* get the honest-disclosure discount because §10/§11's own availability
  notes explicitly validate genre-correct absence as a legitimate, non-defective state for those
  layers — but the discount is capped well below 1.0 because the metric's subject (end-to-end
  reproducibility) is a real capability question, not just an honesty question: a
  legitimately-absent-and-disclosed leg still means the work cannot be computationally reproduced,
  whatever the reason. (Cycle 2) that discount is now correctly ordered above a dead-link discount.
- Worked example of the cycle-2 SCOPE change: an artifact with FIG/DATA/CODE all near-1.0 but a
  silently-thin `constraints.md` now scores `harmonic_mean([1,1,1]) * 0.35 * coherence_mult` —
  still heavily penalized (thin scope halves-plus the final number before any coherence discount),
  but the penalty is legible as "you can run this but can't correctly interpret the result,"
  rather than being folded into the same weakest-link pool that answers "can you run this at all,"
  which is what cycle 1's four-leg harmonic mean conflated.
- `cross_leg_coherence` is a final multiplier (0.55-1.00) computed entirely from STEP 2.5's literal
  anchor matches/contradictions (cycle 2) — never an LLM-asserted integer — so a bundle with four
  individually-strong-looking legs whose texts share zero verifiable literal anchors is capped at
  90% of its combined score, one with active numeric contradictions (e.g. mismatched cohort `n=`)
  is capped at 55%, and no amount of fluent prose can move this number without also embedding a
  matching literal accession/version/parameter/seed string in a second file.

## 3. Why hard to Goodhart, and composition with the suite

**Hard to Goodhart because:**
1. The scoring arithmetic (STEP 4) is entirely fixed code; the only LLM touchpoint (STEP 3) emits
   categorical labels from a closed enum, restricted to *why a leg is absent/thin* — a question
   that unavoidably requires reading prose but never emits a number. Cross-leg coherence, the one
   place cycle 1 let an LLM freehand a score, is now (cycle 2) a fully deterministic computation
   over literal anchor strings (STEP 2.5), closing the softest surface in the cycle-1 design.
2. An artifact author (or an ARA-compiler trying to game this specific metric) cannot simply write
   more words into `constraints.md` or `configs/*.md` to move the score: `config_specificity_ratio`
   and `fig_completeness_ratio` are computed over concrete value-bearing fields (numbers, IDs,
   version strings, claim-linkage), so padding with prose doesn't move the score, and (cycle 2)
   `constraints.md` specifically cannot farm additional credit beyond clearing its non-thin gate,
   since SCOPE is capped at a 1.0 multiplier ceiling rather than being a graded leg with headroom.
3. The weakest-link combinator over FIG/DATA/CODE specifically defeats the most obvious gaming
   strategy (over-invest in two legs, drop the third quietly); the SCOPE gate separately defeats a
   different strategy (pad `constraints.md` to look like a strong fourth leg) without letting either
   strategy compensate for the other, since they now operate as genuinely independent checks
   (executability vs. interpretability) rather than one blended pool.
4. Claims-weighting on the FIG leg (cycle 2, from exp1) closes a gaming route the cycle-1 flat
   ratio left open: filing several claims-irrelevant objects cleanly while a headline,
   claims-dense table/figure goes missing no longer buys back the score it used to, because that
   object's weight in the denominator (and its zero contribution to the numerator when missing)
   dominates the ratio.
5. The honest-disclosure vs. silent-gap distinction, cross-checked against `PAPER.md`/other
   `logic/solution/*.md` files in STEP 3, closes the loop on the most tempting cheap win: claiming
   "genre-correct absence" for a leg that the rest of the artifact's own text contradicts (e.g. a
   method file that clearly describes running code, next to an `environment.md` claiming "analytical
   — none"). This is checkable and catchable precisely because ARAs are internally cross-referenced
   by design (§9-§11 all point back to claims/methods).
6. The optional [ext] liveness/accession-format check (STEP 2) adds a ground-truth anchor outside
   the artifact's own text — a fabricated or long-dead repo URL / malformed accession ID cannot be
   talked around by better prose, since it's checked against the real world, not the document.

**Composition with the rest of the suite:** M48 deliberately does *not* re-score single-layer
quality (evidence transcription fidelity, code style, dataset documentation completeness in
isolation, or — made explicit in cycle 2 — the depth/quality of a limitations statement) — those
are the province of other metrics and of the ARA verifier's per-layer checks (e.g. §11 Evidence
Ledger Completeness for Seal Level 1, or a dedicated constraints/limitations-quality metric
elsewhere in the suite that would own how thoughtfully `constraints.md` is written). M48's unique
contribution, preserved from the ledger's top-10 ranking rationale and sharpened in cycle 2, is the
**AND-of-executability-legs, gated-by-interpretability, plus cross-reference-and-honesty** layer on
top: it is possible for an ARA to score well on every individual per-layer metric and still score
low on M48 (each leg locally fine, but the legs don't compose into an actually-reproducible-and-
interpretable whole, or a headline evidence object silently didn't make it into the bundle), and
that gap is exactly the net-new signal this metric is scoped to catch. It remains complementary to,
and strictly tighter than, the ARA verifier's D6 "reproducibility is mentioned" check: D6 can pass
on a single sentence, M48 requires the sentence to be backed by concrete, literally
cross-referenced, and honestly scoped artifacts across three executability layers plus one
interpretability gate.

M48 cycle-2 improvement (B): done
