## Changes (cycle 2)

Starting point: exp2 (tournament-1 winner, rank 1). Critique (`critique_c1.md`) named four concrete
weaknesses and one cross-pollination directive; each is fixed below, not just discussed.

1. **Design-tier classification was brittle and its confidence was invisible to the score.**
   Cycle-1 ran the `[sem]` fallback only when the keyword heuristic matched *zero* tiers, so a
   setup that fires two or more keyword sets at once (an ML pipeline described with `cohort`
   metadata, e.g. "10x Visium... cohort of 31 donors") silently took whichever tier's keyword
   happened to be checked first — a real misclassification route, not a hypothetical one. Fixed:
   `classify_design_tier` now returns `(tier, confidence)`; confidence is `heuristic_high` only when
   exactly one keyword set fires, and *any* zero-match or multi-match case routes to `[sem]`
   (multi-match passes the competing candidates into the prompt so the model arbitrates instead of
   the heuristic guessing). A new `apply_confidence_tax` then folds that confidence into the actual
   entailment score — shaving passes down and pushing failures further down when the label is less
   certain — so "log confidence into the score" is a real scoring effect, not a diagnostic field
   nobody reads.
2. **The warrant matrix was sparse — most `(tier, type)` pairs fell to one flat, unjustified `-0.4`.**
   Replaced the hand-picked `WARRANT_MATRIX`/`OVERREACH_PENALTY` dicts with two small, independently
   justified primitives — `KIND_ELIGIBILITY` (is this the *right kind* of evidence for this claim
   type at all) and `OVERREACH_CEILING` (how far past this design's generalizability does a
   wrong-kind claim reach) — and a formula that derives every one of the 49 `(tier, type)` cells from
   them (§4.5, full grid in §2.1). The formula exactly reproduces every value cycle-1 hand-specified
   (`observational_cohort×causal = -0.6`, `cross_sectional×causal = -0.8`, `in_silico×causal = -0.8`,
   `case_study×comparative_superiority = -0.7`) and replaces the remaining ad hoc `-0.4` cells with
   principled, auditable values. It also fixes a real cycle-1 gap: case reports are the classic
   literature vehicle for a *first* adverse-event signal (thalidomide, etc.), so `case_study` now has
   `safety_adverse` in its kind-eligible set instead of being flatly overreach-penalized for the one
   thing case studies are traditionally good for.
3. **Grounding trusted verbatim/value substring presence, which is beatable by a locator-correct,
   semantically-wrong citation** — the exact citation-laundering route that beats verifier D1 (which
   only checks "does a source exist and quote-match"). Cross-pollinated exp3's re-derivation
   instruction: the deterministic substring check is now a cheap *gate*, and only sources that pass
   it go to a new `[sem]` call (Call E) that re-derives, from the evidence file's actual body text,
   whether the cited value/relationship — read in its real row/column/arm/unit context — actually
   licenses the claim's use of it. A `MISREAD` verdict (real file, real number, wrong context) floors
   the *entire* claim at `-1.0`, worse than a merely missing source, mirroring the fabricated-NCT
   pattern already in the pub-bias axis.
4. **`min()`-over-Proof vs `mean()`-over-claims aggregation was not shown to resist padding**, the
   same failure mode the tournament docked exp1 for. It was true for exp2 too: a single overreach
   claim buried among enough clean claims pushes the plain per-claim mean arbitrarily close to 1.0.
   Fixed by cross-pollinating exp3's multiplicative-floor idea into the *inter-claim* aggregation:
   `entailment_score`, `grounding_score`, and `direction_score` are now `blended_aggregate(scores) =
   0.5·mean(scores) + 0.5·min(scores)`, which provably caps the composite at `0.5 + 0.5·(worst claim's
   score)` **no matter how many additional perfect claims are added** (worked numeric example in
   §6.1). Also added a structural hard cap (borrowed from exp3's `availability_floor`): any dangling
   `Proof`/`Verifies` reference caps the *whole metric's* raw score at `-0.3` pre-rescale, so no
   combination of clean axes elsewhere can buy back an artifact part of which literally cannot be
   evaluated.
5. **Publication-bias workflow sharpened** (not flagged in critique but in scope per the brief): the
   fabrication guard now requires condition *and* intervention/drug-name overlap, not condition
   alone, with an explicit intermediate `-0.5` bucket for the one-axis-matches case (an honest
   citation of a related-but-different trial is not fabrication, but it is not a confirmed match
   either — penalize-don't-skip forbids rounding that ambiguity to either extreme). Added an explicit
   outcome-switching check (a registered secondary outcome reported with primary-outcome prominence
   while the real primary is dropped — worse than plain omission) and fully specified the previously
   hand-waved `claims_direction_conflicts_with` as a closed-label `[sem]` call (Call F) reusing the
   same `ENTAILS/CONTRADICTS/ORTHOGONAL/AMBIGUOUS` vocabulary as Call C, with `AMBIGUOUS` penalized
   rather than passed through free.

---

## 1. Why this indicator signals good science

A paper's rhetorical claims and its actual verification apparatus can drift apart in three distinct
ways, and each is a real, common defect this metric must catch:

1. **Type mismatch** — the claim asserts more than the experiment's design can license (a
   cross-sectional cohort producing a causal claim; an in-silico benchmark producing a claim about
   "real-world" performance; a single-arm case study producing a comparative-superiority claim). This
   is the "overclaiming" failure mode and is the single most common way published science overstates
   itself.
2. **Grounding mismatch** — the claim's `Sources` entries cite an evidence object, but the exact
   number/quote doesn't actually live there, or lives there but in a context (wrong arm, wrong row,
   wrong direction, wrong unit) that doesn't actually support the claim as used — hallucinated,
   misattributed, or *misread* support.
3. **Selective/directional mismatch at the population level** — the study was pre-registered (a
   clinical trial with an NCT/ISRCTN/EudraCT id) with a defined primary/secondary outcome set, and the
   paper's claims quietly report only the outcomes that came out favorably, reframe a secondary
   outcome as if it were primary, or omit that the registry shows the trial was terminated/results
   differ. This is publication bias made concrete and checkable, not a vibe — it is the one sub-check
   in this metric that reaches **outside** the artifact to an authoritative external record the
   compiler cannot rewrite.

What it must reward: claims whose asserted strength (causal / comparative / associative /
descriptive / mechanistic / non-inferiority / safety) is actually warranted by the experiment's
declared design, whose cited numbers are verbatim traceable *and correctly read in context* into
`evidence/`, and — for registered trials — whose reported outcome set, framing, and direction match
the public registry.

What it must NOT reward: verbose `Evidence basis` prose that never gets checked against the actual
table/figure cell; a long `Verifies`/`Proof` list where most links are semantically vacuous; padding
the claim list with easy, well-behaved claims to statistically dilute one bad one below detectability;
an experiment with vague, non-directional `Expected outcome` language that trivially "matches" any
claim; a `Setup` that claims "randomized" or "double-blind" language to *sound* like an RCT without a
locatable registration to back it.

## 2. Failure modes / gaming routes and how the design closes them

| Gaming route | Closed by |
|---|---|
| Pad `Verifies`/`Proof` with irrelevant claim/experiment pairs to inflate apparent "verified" coverage | Intra-claim aggregation is `min()` over the `Proof` list — one bad link taints that claim's score regardless of how many good ones surround it |
| Add many trivially-true, well-behaved claims to statistically dilute one real overclaim below detectability in the composite | Inter-claim aggregation is `blended_aggregate = 0.5·mean + 0.5·min`, which caps the composite at `0.5 + 0.5·(worst claim)` **no matter how large N gets** — a plain mean does not have this property (see §6.1 worked example) |
| Write `Setup: Design: randomized, double-blind` with no real trial id to claim RCT-tier warrant | Publication-bias sub-check requires a resolvable, condition-*and*-intervention-matched NCT/ISRCTN/EudraCT id whenever the artifact signals a clinical-intervention claim; absence or mismatch is scored down, never skipped |
| Trip two design-tier keyword sets at once (e.g. an ML pipeline described with `cohort` metadata) to nudge the heuristic toward a favorable tier | Any zero-match *or* multi-match case routes to `[sem]` as authoritative, not a heuristic guess with an LLM tiebreaker bolted on; the resulting lower confidence additionally taxes the score in the punishing direction only |
| Vague, non-directional `Expected outcome` ("results were as expected") to auto-match any claim's `Status` | `[sem]` direction classifier returns `AMBIGUOUS` for outcomes lacking directional language — `AMBIGUOUS` is penalized, never a pass |
| Leak an exact number into `Expected outcome`/`Metrics` (Critical Rule #3 violation) to make the "entailment" check trivially exact | Deterministic digit-leak probe flags it and applies an explicit deduction on top of the entailment sub-score |
| Cite `Sources` with a verbatim-matching quote that is real but attributed to the wrong arm/row/unit/direction (locator-correct, semantically wrong) | `[sem]` re-derivation (Call E) reads the value in its actual table/figure context; a `MISREAD` verdict floors the *entire claim's* grounding score at `-1.0`, worse than a missing citation |
| Cite `Evidence basis` in prose without matching `Sources` quotes, or cite a `Sources` entry to a table that doesn't contain the value | Deterministic gate requires the verbatim quote (or bare value, at reduced credit) to literally appear before re-derivation even runs; missing entirely = floor |
| Fabricate a plausible-looking NCT id | External lookup either returns nothing (fabrication penalized same as absence) or returns a trial whose `condition`/`intervention` don't overlap the artifact's subject — no-overlap is treated as worse than absence; one-axis overlap is scored at an explicit intermediate value, never rounded to a full match |
| Selectively report only the registered outcomes that came out favorably | `publication_bias_subscore` diffs `registered_primary_outcomes` against outcomes surfaced in `claims.md`; any dropped primary outcome scores down proportionally |
| Reframe a registered secondary outcome as if it were primary while quietly dropping the real primary outcome | Explicit outcome-switching check stacks an extra fixed deduction on top of the proportional drop penalty — an active reframing is scored worse than a passive omission |
| Claim causal/superiority language from an observational or in-silico design | `entailment_subscore(design_tier, claim_type)` derives a large negative from the `KIND_ELIGIBILITY` / `OVERREACH_CEILING` formula for every unwarranted pair — not just the ones someone thought to hand-enumerate |
| Have a dangling `Proof`/`Verifies` reference but otherwise polish every other axis | A structural hard cap (`raw = min(raw, -0.3)`) fires whenever any dangling reference exists, regardless of how the other four weighted axes score |

### 2.1 The full warrant grid (formula-derived, not hand-picked)

Every cell below is computed by the single `entailment_subscore` formula in §4.5 from two small,
independently justified tables (`KIND_ELIGIBILITY`, `OVERREACH_CEILING`) — none are hand-picked
per-cell. Values shown are pre-confidence-tax (i.e. `heuristic_high` classification).

| design tier ↓ / claim type → | causal | comparative_superiority | non_inferiority | associative_correlational | safety_adverse | mechanistic | descriptive_prevalence |
|---|---|---|---|---|---|---|---|
| rct | **1.0** | **1.0** | **1.0** | −0.2 | **1.0** | −0.2 | −0.2 |
| meta_analysis | −0.4 | **1.0** | **1.0** | **1.0** | **1.0** | −0.2 | −0.2 |
| observational_cohort | −0.6 | −0.4 | −0.4 | **1.0** | **1.0** | −0.2 | **1.0** |
| cross_sectional | −0.8 | −0.6 | −0.6 | **1.0** | −0.4 | −0.4 | **1.0** |
| in_vitro_wetlab | −0.8 | −0.6 | −0.6 | −0.4 | −0.4 | **1.0** | **1.0** |
| in_silico | −0.8 | −0.6 | −0.6 | −0.4 | −0.4 | **1.0** | **1.0** |
| case_study | −0.9 | −0.7 | −0.7 | −0.5 | **1.0** | −0.5 | **1.0** |

Bold = kind-eligible + strength-plausible (full warrant, `1.0`). All four cycle-1 hand-specified
values are reproduced exactly (`observational_cohort×causal = −0.6`, `cross_sectional×causal = −0.8`,
`in_silico×causal = −0.8`, `case_study×comparative_superiority = −0.7`); every other cell now has a
derivation, not a flat default.

## 3. How the assessment-critique notes change the design

The ledger note for M19 says the ARA verifier already does claim↔evidence entailment "D1
semantically," and that the **publication-bias cross-check** is the piece that beats both round-1
metrics and the verifier. Two design decisions from cycle 1 remain load-bearing in the scoring
function below (§4.5), plus one cycle-2 addition:

- **The entailment half must not duplicate the verifier's generic semantic match.** This design keeps
  entailment **type-aware and design-warranted**: it classifies the claim's assertion type and the
  experiment's design tier independently, then checks the *warrant relationship* between them via a
  fixed, fully-enumerated lookup — a strictly harder and more specific question than "is this
  supported," and one the generic verifier check does not ask.
- **The publication-bias axis keeps the largest single weight (0.30 of 1.0, §4.5)**, more than either
  the type-aware entailment (0.25) or the grounding check (0.20), because it is the genuinely net-new
  capability (external registry lookup) and the brief instructs preserving that edge.
- **Cycle-2 addition**: the tournament-1 judge explicitly named this metric's `min()`-over-Proof
  mechanism as the most Goodhart-resistant piece in the field but flagged that the *inter-claim*
  aggregation was still a plain mean — a real gap, since the whole point of `min()`-over-Proof is
  undermined if the very next aggregation step lets padding dilute it back out. §4.5/§6.1 close that
  gap with a blended mean/min composite and prove the bound numerically.

## 4. Generation/compute workflow

### 4.1 Inputs (artifact fields, per DATA_SHAPES.md / 05_experiments.md)

- `logic/claims.md` — per claim: `Statement`, `Status`, `Proof` (→E## ids), `Evidence basis`,
  `Sources` (list of `{value, ref, locator, quote, tag}`), `Dependencies`.
- `logic/experiments.md` — per experiment: `Verifies` (→C## ids), `Setup` (free-form subkeys),
  `Procedure`, `Metrics`, `Expected outcome`, `Baselines`, `Dependencies`.
- `evidence/README.md` + `evidence/tables/*.md` + `evidence/figures/*.md` — flattened body text per
  file, keyed by ref-path, for the grounding gate and re-derivation call.
- `logic/solution/constraints.md` (+ `study_design.md` if present) — searched for a trial
  registration id, a "terminated"/limitation acknowledgment, and outcome-framing language.
- `logic/problem.md` — subject terms (`subject_terms`) and, new in cycle 2, intervention/drug-name
  terms (`intervention_terms`), both used only to sanity-check a looked-up trial's registered
  `condition`/`intervention` against the paper's actual subject (fabrication/mismatch guard).

### 4.2 Step-by-step procedure

1. **Bind claims↔experiments bidirectionally** (deterministic, cheap, run first). A dangling
   reference here is scored *and* — new in cycle 2 — forces a hard cap on the whole metric's raw
   score (§4.5), since nothing downstream can even be evaluated for that claim.
2. **Classify each experiment's design tier**: keyword heuristic fires only when exactly one tier's
   keyword set matches; zero or multiple matches both route to `[sem]` (Call A / Call A'), and the
   resulting confidence label feeds a tax applied later, not just a diagnostic.
3. **Classify each claim's assertion type** via `[sem]` (Call B).
4. **Score the warrant relationship** between design tier and claim type via the formula-derived grid
   in §2.1 (no LLM call needed once both are classified — deterministic and auditable), then apply the
   confidence tax from step 2.
5. **Grounding**: deterministic verbatim/value gate first (cheap, catches outright fabrication and
   wrong-file citation without an LLM call); only sources that pass the gate go to `[sem]`
   re-derivation (Call E) against the evidence file's actual context. A `MISREAD` verdict floors the
   whole claim.
6. **Direction check**: `[sem]` (Call C) comparing `Expected outcome` against `Statement`+`Status` for
   directional entailment vs. contradiction vs. irrelevance vs. ambiguity.
7. **Digit-leak probe**: deterministic regex over `Expected outcome`/`Metrics` for exact numbers
   (excluding stated significance thresholds); applies an extra deduction, does not replace step 6.
8. **Publication-bias cross-check**:
   a. `[sem]` (Call D): does this artifact assert a clinical-intervention comparative/causal claim at
      all?
   b. If yes: search `constraints.md`/`study_design.md`/`claims.md` for an NCT/ISRCTN/EudraCT id.
   c. `[ext trial lookup]`: call the trial registry for that id, returning `condition`,
      `intervention`, outcome sets, `status`, `results_posted`, `results_summary`.
   d. Check condition *and* intervention overlap (both/one/neither — three distinct outcomes, §4.5).
   e. Diff registry `primary_outcomes` against outcomes surfaced in `claims.md`; check whether a
      dropped primary was reframed via a promoted secondary (outcome-switching); compare registry
      `status` against `constraints.md`'s disclosure; if results are posted, run `[sem]` (Call F) to
      check the claims' direction against the registry's posted-results summary.
9. **Aggregate** per §4.5: blended mean/min across claims for entailment/grounding/direction, then
   the weighted sum, then the structural hard cap, then rescale to the suite's 0–1 range.

### 4.3 `[sem]` call specifications

**Call A — design tier fallback, no keyword conflict** (heuristic matched zero tier keyword sets):
```
You are classifying an experiment's evidentiary design tier from its Setup block.
Setup: {setup_dict}
Choose exactly one: rct | observational_cohort | cross_sectional | meta_analysis |
in_vitro_wetlab | in_silico | case_study | unclassifiable
Return only the label.
```

**Call A' — design tier fallback, keyword conflict** (heuristic matched two or more tier keyword
sets — new in cycle 2, the heuristic is not trusted to arbitrate its own ambiguity):
```
You are classifying an experiment's evidentiary design tier from its Setup block. A keyword heuristic
flagged this Setup as ambiguous between multiple candidate tiers -- use full context to pick the tier
that actually governs this experiment's evidentiary warrant, not just which keyword appears.
Setup: {setup_dict}
Candidate tiers the heuristic could not disambiguate: {candidates}
Choose exactly one: rct | observational_cohort | cross_sectional | meta_analysis |
in_vitro_wetlab | in_silico | case_study | unclassifiable
Return only the label.
```

**Call B — claim assertion type**:
```
Classify the logical assertion type of this claim's Statement. Ignore whether it is true; classify
only what KIND of assertion is being made.
Statement: {statement}
Status: {status}
Choose exactly one: causal | comparative_superiority | non_inferiority |
associative_correlational | descriptive_prevalence | mechanistic | safety_adverse | unclassifiable
Return only the label.
```

**Call C — direction entailment**:
```
You are checking DIRECTIONAL consistency only -- exact numeric matching is handled by a separate
check, ignore whether numbers match.
Claim status: {status}
Claim statement: {statement}
Experiment's stated Expected outcome(s): {expected_outcome}
Does the expected outcome, if realized as described, directionally entail the claim's status and
statement?
Choose exactly one: ENTAILS | CONTRADICTS | ORTHOGONAL (outcome doesn't bear on this claim at all)
| AMBIGUOUS (too vague/non-directional to tell)
Return only the label.
```

**Call D — clinical-intervention signal** (gates whether the publication-bias axis is "applicable"):
```
Does this research artifact's problem statement and claims concern a clinical intervention (drug,
device, procedure, or behavioral/therapeutic intervention) being compared for effect, as opposed to
e.g. pure observational biomarker ranking, omics/mechanistic analysis, or a computational/ML method
with no clinical intervention arm?
Problem statement key excerpts: {problem_excerpt}
Claim statements: {claim_statements}
Answer strictly: YES | NO
```

**Call E — grounding re-derivation** (new in cycle 2; runs only after the deterministic substring
gate passes):
```
A claim cites a value from an evidence file. The value/quote is confirmed to literally appear in the
file's body text -- do NOT re-check that. Your job is different and stricter: read the value in its
ACTUAL table/figure context (which row, which column/arm, which unit, which direction) and decide
whether that context actually licenses the claim's use of it. Ignore narrative gloss elsewhere in the
evidence file; ground your answer only in the raw transcribed table/figure content.
Claim statement: {claim_statement}
Cited value: {cited_value}
Cited quote: {cited_quote}
Locator: {locator}
Evidence file body text: {evidence_body}
Choose exactly one:
CONFIRMED (the value, correctly read in context, licenses the claim as stated)
MISREAD (the value is real but the claim misattributes its arm/row/unit/direction)
UNDECIDABLE (the evidence file's context is too sparse/ambiguous to re-derive either way)
Return only the label.
```

**Call F — trial result direction check** (new in cycle 2; replaces the cycle-1 unspecified
`claims_direction_conflicts_with` helper, reusing Call C's label vocabulary for consistency):
```
You are checking DIRECTIONAL consistency only between an artifact's claims and a clinical trial
registry's posted results summary.
Claim statements: {claim_statements}
Registry's posted results summary: {results_summary}
Do the claim statements directionally align with the registry's posted results?
Choose exactly one: ENTAILS | CONTRADICTS | ORTHOGONAL | AMBIGUOUS
Return only the label.
```

### 4.4 `[ext trial lookup]` specification

- Input: an extracted registration id (regex `NCT\d{8}` or `ISRCTN\d+` or `EudraCT` pattern) found in
  `constraints.md` / `study_design.md` / `claims.md`.
- Call: `get_trial_details(id)` (ClinicalTrials.gov API v2 or equivalent registry API) →
  `{condition, intervention, primary_outcomes: [...], secondary_outcomes: [...], status,
  results_posted: bool, results_summary: str | None}`.
- Failure modes to treat explicitly, never silently: lookup returns nothing (id doesn't resolve);
  lookup resolves but neither `condition` nor `intervention` overlaps the artifact's subject
  (fabricated/wholly mismatched — worse than absence); lookup resolves with exactly one of
  `condition`/`intervention` overlapping (ambiguous — plausibly a related-but-different trial, scored
  at an explicit intermediate value, never rounded to either extreme); lookup resolves and both
  overlap (proceed to outcome/status/direction diff).

### 4.5 Scoring function (real Python against the documented shape)

```python
import re
from dataclasses import dataclass
from typing import Optional

# ---- Parsed artifact types (produced by the upstream ARA loader from the .md files) ----

@dataclass
class Claim:
    id: str                       # "C03"
    statement: str
    status: str                   # hypothesis | supported | refuted (+ optional qualifier)
    proof: list[str]              # experiment ids cited by this claim, e.g. ["E01"]
    evidence_basis: str
    sources: list[dict]           # [{"value","ref","locator","quote","tag"}, ...]
    dependencies: list[str]

@dataclass
class Experiment:
    id: str
    verifies: list[str]           # claim ids that cite this experiment back
    setup: dict                   # free-form subkeys, e.g. {"Design": "...", "Randomization": "..."}
    metrics: str
    expected_outcome: list[str]
    dependencies: list[str]

@dataclass
class EvidenceObject:
    file: str                     # ref-path, e.g. "evidence/tables/table2.md"
    body_text: str                # flattened markdown body, used for grounding checks

@dataclass
class TrialRecord:
    condition: str
    intervention: str             # NEW (cycle 2): registered drug/device/procedure name
    primary_outcomes: list[str]
    secondary_outcomes: list[str]
    status: str                   # "completed" | "terminated" | "withdrawn" | ...
    results_posted: bool
    results_summary: Optional[str]  # NEW (cycle 2): free-text posted-results summary, feeds Call F


# ---- Step 1: bidirectional binding (deterministic, cheap, runs first) ----

def check_binding(claims: list[Claim], experiments: list[Experiment]) -> list[tuple[str, str, float]]:
    exp_by_id = {e.id: e for e in experiments}
    claim_ids = {c.id for c in claims}
    findings = []
    for c in claims:
        if not c.proof:
            findings.append((c.id, "no_proof", -1.0))
            continue
        for eid in c.proof:
            e = exp_by_id.get(eid)
            if e is None:
                findings.append((c.id, f"dangling_proof:{eid}", -1.0))
            elif c.id not in e.verifies:
                findings.append((c.id, f"one_directional_binding:{eid}", -0.5))
    for e in experiments:
        for cid in e.verifies:
            if cid not in claim_ids:
                findings.append((e.id, f"dangling_verifies:{cid}", -1.0))
    return findings

def has_dangling_reference(binding_findings: list[tuple[str, str, float]]) -> bool:
    # NEW (cycle 2): feeds the structural hard cap in score_m19 -- a dangling reference means part of
    # the artifact literally cannot be evaluated, and no clean axis elsewhere should buy that back.
    return any(kind.startswith("dangling_") for _, kind, _ in binding_findings)


# ---- Step 2: design tier (heuristic only when unambiguous; [sem] otherwise, with logged confidence) ----

DESIGN_TIER_KEYWORDS = {
    "rct": ["randomiz", "double-blind", "placebo-controlled", "treatment arm"],
    "observational_cohort": ["cohort", "prospective", "retrospective", "registry-based"],
    "cross_sectional": ["cross-sectional", "single time point"],
    "meta_analysis": ["network meta-analysis", "pooled", "systematic review"],
    "in_vitro_wetlab": ["assay", "sequencing", "cell line", "spatial", "pipeline"],
    "in_silico": ["simulation", "synthetic data", "held-out split", "benchmark dataset"],
    "case_study": ["case report", "single patient", "n=1"],
}

def _matched_tiers(setup: dict) -> list[str]:
    blob = " ".join(str(v) for v in setup.values()).lower()
    return [tier for tier, kws in DESIGN_TIER_KEYWORDS.items() if any(kw in blob for kw in kws)]

def classify_design_tier(setup: dict, sem_fn) -> tuple[str, str]:
    """Returns (tier, confidence). confidence in
    {"heuristic_high", "sem_fallback_no_match", "sem_fallback_ambiguous"}.
    CYCLE-2 FIX: cycle-1 only escalated to [sem] on zero matches, letting a multi-keyword-set setup
    (e.g. an ML pipeline with 'cohort' metadata) silently pick whichever tier the heuristic checked
    first. Now any non-exactly-one-match case escalates, and [sem] gets told about the conflict."""
    hits = _matched_tiers(setup)
    if len(hits) == 1:
        return hits[0], "heuristic_high"
    if len(hits) == 0:
        return sem_fn("classify_design_tier", setup=setup), "sem_fallback_no_match"          # Call A
    return sem_fn("classify_design_tier_ambiguous", setup=setup, candidates=hits), "sem_fallback_ambiguous"  # Call A'

CONFIDENCE_TAX = {"heuristic_high": 1.0, "sem_fallback_no_match": 1.1, "sem_fallback_ambiguous": 1.15}

def apply_confidence_tax(raw_score: float, confidence: str) -> float:
    """A less-confident tier classification is weaker evidence in EITHER direction: shave passes
    toward neutral, push failures further toward the floor. Never used to inflate a score."""
    tax = CONFIDENCE_TAX[confidence]
    if raw_score >= 0:
        return raw_score / tax
    return max(raw_score * tax, -1.0)


# ---- Step 3+4: claim assertion type + warrant grid (formula-derived, not hand-picked) ----

ASSERTION_STRENGTH = {
    "descriptive_prevalence": 1,
    "associative_correlational": 2,
    "safety_adverse": 2,
    "mechanistic": 2,
    "non_inferiority": 3,
    "comparative_superiority": 3,
    "causal": 4,
}

KIND_ELIGIBILITY = {
    "rct": {"causal", "comparative_superiority", "non_inferiority", "safety_adverse"},
    "meta_analysis": {"comparative_superiority", "non_inferiority", "associative_correlational", "safety_adverse"},
    "observational_cohort": {"associative_correlational", "descriptive_prevalence", "safety_adverse"},
    "cross_sectional": {"descriptive_prevalence", "associative_correlational"},
    "in_vitro_wetlab": {"mechanistic", "descriptive_prevalence"},
    "in_silico": {"mechanistic", "descriptive_prevalence"},
    # CYCLE-2 FIX: case reports are the classic literature vehicle for a FIRST adverse-event signal
    # (thalidomide, etc.) -- cycle-1 omitted this and over-penalized a legitimate case-report use.
    "case_study": {"descriptive_prevalence", "safety_adverse"},
}

# Generalizability ceiling used ONLY to size the overreach penalty for kind-INeligible pairs -- kept
# separate from KIND_ELIGIBILITY on purpose: "is this the right kind of evidence" and "how far past
# this design's generalizability does a wrong-kind claim reach" are different questions. Conflating
# them was exactly why cycle-1's unlisted cells fell to one flat, unjustified -0.4.
OVERREACH_CEILING = {
    "rct": 4,
    "meta_analysis": 3,
    "observational_cohort": 2,
    "cross_sectional": 1,   # weaker than cohort: no temporal ordering at all
    "in_vitro_wetlab": 1,
    "in_silico": 1,
    "case_study": 1,
}

def entailment_subscore(design_tier: str, claim_type: str, tier_confidence: str) -> float:
    if design_tier == "unclassifiable" or claim_type == "unclassifiable":
        return -0.5           # classification itself failed -> thin/ambiguous artifact, penalized
    if claim_type in KIND_ELIGIBILITY.get(design_tier, set()):
        raw = 1.0
    else:
        strength = ASSERTION_STRENGTH[claim_type]
        ceiling = OVERREACH_CEILING[design_tier]
        gap = strength - ceiling
        if gap <= 0:
            # Numerically plausible strength, but structurally the wrong KIND of evidence (e.g. a
            # cohort study claiming a mechanistic finding with no assay data) -- a real defect, but
            # categorically milder than reaching past the design's generalizability ceiling.
            raw = -0.2
        else:
            raw = -min(1.0, 0.2 + 0.2 * gap)
            if design_tier == "case_study":
                raw -= 0.1    # n=1 generalizability surcharge, stacks on top of any overreach
    return apply_confidence_tax(raw, tier_confidence)


# ---- Step 5: grounding (deterministic gate + [sem] re-derivation against real evidence context) ----

def _source_gate(src: dict, ev: Optional[EvidenceObject]) -> str:
    """Cheap deterministic first gate -- decides whether the [sem] re-derivation call even runs."""
    if ev is None:
        return "MISSING"
    if src.get("quote") and src["quote"] in ev.body_text:
        return "VERBATIM_PRESENT"
    if src.get("value") and src["value"] in ev.body_text:
        return "VALUE_PRESENT"
    return "MISSING"

def grounding_subscore(claim: Claim, evidence_by_file: dict[str, EvidenceObject], sem_fn) -> float:
    if not claim.sources:
        return -1.0            # Rule 16 violation: no grounding entries at all
    per_source = []
    for src in claim.sources:
        ev = evidence_by_file.get(src["ref"])
        gate = _source_gate(src, ev)
        if gate == "MISSING":
            per_source.append(-1.0)
            continue
        # CYCLE-2 ADDITION: substring presence alone is beatable by a locator-correct, semantically
        # wrong citation -- exactly the laundering route that beats verifier D1. Re-derive from the
        # evidence file's real context before granting credit.
        verdict = sem_fn("grounding_rederivation",                                     # Call E
                          claim_statement=claim.statement, cited_value=src.get("value"),
                          cited_quote=src.get("quote"), locator=src.get("locator"),
                          evidence_body=ev.body_text)
        if verdict == "CONFIRMED":
            per_source.append(1.0 if gate == "VERBATIM_PRESENT" else 0.7)
        elif verdict == "MISREAD":
            # Worse than missing: a real file, a real number, used wrong -- laundering, not a gap.
            # One misread floors the WHOLE claim (mirrors the fabricated-NCT-worse-than-absence
            # pattern in Step 8) -- no averaging can dilute an active laundering hit.
            return -1.0
        else:  # "UNDECIDABLE"
            per_source.append(-0.3)
    return max(sum(per_source) / len(per_source), -1.0)


# ---- Step 6+7: direction entailment + digit-leak probe ----

DIRECTION_MAP = {"ENTAILS": 1.0, "AMBIGUOUS": -0.3, "ORTHOGONAL": -0.7, "CONTRADICTS": -1.0}
NUMBER_LEAK = re.compile(r"\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\b(?!\s*(?:FDR|CI|alpha)\b)")
ALLOWED_THRESHOLD = re.compile(r"(FDR|p)\s*[<=]\s*0\.\d+")

def digit_leak_penalty(text: str) -> float:
    stripped = ALLOWED_THRESHOLD.sub("", text)     # design thresholds are allowed, strip them first
    return -0.3 if NUMBER_LEAK.search(stripped) else 0.0

def direction_subscore(expected_outcome: list[str], statement: str, status: str, metrics: str, sem_fn) -> float:
    label = sem_fn("direction_entailment", expected_outcome=expected_outcome,
                    statement=statement, status=status)                       # Call C
    base = DIRECTION_MAP.get(label, -0.3)
    leak = digit_leak_penalty(" ".join(expected_outcome) + " " + metrics)
    return max(base + leak, -1.0)


# ---- Step 8: publication-bias cross-check ----

NCT_PATTERN = re.compile(r"\bNCT\d{8}\b")

def find_trial_registration(artifact) -> Optional[str]:
    text = artifact.constraints_text + " " + artifact.study_design_text + " " + artifact.claims_text
    m = NCT_PATTERN.search(text)
    return m.group(0) if m else None

def _term_overlap(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return any(term.lower() in low for term in terms)

def condition_matches(trial: TrialRecord, subject_terms: list[str]) -> bool:
    return _term_overlap(trial.condition, subject_terms)

def intervention_matches(trial: TrialRecord, intervention_terms: list[str]) -> bool:
    # NEW (cycle 2): condition-only matching let a broadly-worded condition (e.g. "type 2 diabetes")
    # pass even when the trial's actual drug/device has nothing to do with the artifact's subject.
    return _term_overlap(trial.intervention, intervention_terms)

def publication_bias_subscore(artifact, trial_lookup_fn, sem_fn) -> float:
    applicable = sem_fn("clinical_intervention_signal",                       # Call D
                         problem_excerpt=artifact.problem_excerpt,
                         claim_statements=artifact.claim_statements) == "YES"
    if not applicable:
        # Genuinely out-of-scope axis. Penalize-don't-skip: contributes at a fixed low-neutral value
        # rather than being dropped from the denominator, so a non-clinical artifact can never reach
        # ceiling on an axis it cannot be audited against.
        return -0.2

    nct_id = find_trial_registration(artifact)
    if nct_id is None:
        return -0.8            # claims a clinical comparative effect, no locatable registration

    trial = trial_lookup_fn(nct_id)                                            # [ext trial lookup]
    if trial is None:
        return -0.8            # id present but doesn't resolve -> unverifiable, same floor as absent

    cond_ok = condition_matches(trial, artifact.subject_terms)
    interv_ok = intervention_matches(trial, artifact.intervention_terms)
    if not cond_ok and not interv_ok:
        return -1.0            # nothing overlaps -> fabrication/wrong-id, worse than absence
    if cond_ok != interv_ok:
        # CYCLE-2 ADDITION: right disease/wrong drug (or vice versa) is plausibly an honest citation
        # of a related-but-different trial, not outright fabrication -- but it is NOT a confirmed
        # match either. Penalize-don't-skip: this ambiguity gets its own explicit score, not a guess
        # rounded to either extreme.
        return -0.5

    registered_primary = set(trial.primary_outcomes)
    registered_secondary = set(trial.secondary_outcomes)
    reported = set(artifact.reported_outcomes)                       # from claims.md + evidence tables
    reported_as_primary = set(artifact.reported_outcomes_framed_as_primary)  # subset of `reported`
    dropped = registered_primary - reported

    score = 1.0
    if dropped:
        score -= 0.5 * (len(dropped) / max(len(registered_primary), 1))

    # CYCLE-2 ADDITION: promoting a registered SECONDARY outcome to primary-outcome prominence while
    # simultaneously dropping the real primary is an active reframing, not a passive omission -- it
    # stacks an extra fixed penalty beyond the proportional drop deduction above.
    switched = bool(registered_secondary & reported_as_primary) and bool(dropped)
    if switched:
        score -= 0.3

    if trial.status in ("terminated", "withdrawn") and "terminated" not in artifact.constraints_text.lower():
        score -= 0.4

    if trial.results_posted and trial.results_summary:
        # CYCLE-2 FIX: cycle-1 left this as an unspecified `claims_direction_conflicts_with` helper.
        # Fully specified now as a closed-label [sem] call reusing Call C's vocabulary.
        direction = sem_fn("trial_result_direction_check",                     # Call F
                            claim_statements=artifact.claim_statements,
                            results_summary=trial.results_summary)
        if direction == "CONTRADICTS":
            score -= 0.6
        elif direction == "AMBIGUOUS":
            score -= 0.2       # penalize-don't-skip: undecidable direction is not a free pass

    return max(score, -1.0)


# ---- Step 9: aggregate ----

def blended_aggregate(scores: list[float]) -> float:
    """CYCLE-2 FIX: cycle-1 used a plain mean across claims, which the tournament judge flagged (for
    exp1, and implicitly for exp2 too) as dilutable -- enough well-behaved claims push the mean
    arbitrarily close to 1.0 regardless of one real overreach. This blend provably caps the composite
    at 0.5 + 0.5*(worst claim) no matter how many additional perfect claims exist. See §6.1."""
    if not scores:
        return -1.0
    return 0.5 * (sum(scores) / len(scores)) + 0.5 * min(scores)

WEIGHTS = {
    "binding": 0.10,
    "entailment": 0.25,
    "grounding": 0.20,
    "direction": 0.15,
    "publication_bias": 0.30,     # deliberately the largest weight: the net-new, hard-to-fake edge
}

def score_m19(artifact, trial_lookup_fn, sem_fn) -> float:
    claims, experiments = artifact.claims, artifact.experiments
    exp_by_id = {e.id: e for e in experiments}
    evidence_by_file = {ev.file: ev for ev in artifact.evidence}

    binding_findings = check_binding(claims, experiments)
    binding_score = max(1.0 + sum(p for _, _, p in binding_findings) / max(len(claims), 1), -1.0)

    per_entail, per_ground, per_direction = [], [], []
    for c in claims:
        per_ground.append(grounding_subscore(c, evidence_by_file, sem_fn))
        if not c.proof:
            per_entail.append(-1.0)
            per_direction.append(-1.0)
            continue
        claim_type = sem_fn("classify_claim_type", statement=c.statement, status=c.status)  # Call B
        exp_scores, dir_scores = [], []
        for eid in c.proof:
            e = exp_by_id.get(eid)
            if e is None:
                exp_scores.append(-1.0)
                dir_scores.append(-1.0)
                continue
            tier, confidence = classify_design_tier(e.setup, sem_fn)
            exp_scores.append(entailment_subscore(tier, claim_type, confidence))
            dir_scores.append(direction_subscore(e.expected_outcome, c.statement, c.status, e.metrics, sem_fn))
        per_entail.append(min(exp_scores))          # weakest-link WITHIN one claim's Proof list
        per_direction.append(min(dir_scores))

    entailment_score = blended_aggregate(per_entail)     # weakest-link, blended, ACROSS claims too
    grounding_score = blended_aggregate(per_ground)
    direction_score = blended_aggregate(per_direction)
    pub_bias_score = publication_bias_subscore(artifact, trial_lookup_fn, sem_fn)

    raw = (WEIGHTS["binding"] * binding_score
           + WEIGHTS["entailment"] * entailment_score
           + WEIGHTS["grounding"] * grounding_score
           + WEIGHTS["direction"] * direction_score
           + WEIGHTS["publication_bias"] * pub_bias_score)

    # CYCLE-2 ADDITION: structural hard cap (cross-pollinated from exp3's availability_floor). A
    # dangling Proof/Verifies reference means part of the artifact literally cannot be evaluated --
    # no combination of clean axes elsewhere should be able to buy that back.
    if has_dangling_reference(binding_findings):
        raw = min(raw, -0.3)

    return (raw + 1) / 2          # rescale [-1,1] -> [0,1] for the suite's reporting convention
```

## 5. Penalize-don't-skip mapping

Every sub-check has an explicit floor for the corresponding unavailable/thin case — none return
`None`/N-A:

| Condition | Behavior |
|---|---|
| Claim has no `Proof` | `entailment=-1.0`, `direction=-1.0` for that claim (not excluded from the average) |
| `Proof`/`Verifies` reference doesn't resolve | `-1.0` binding finding; still included in `binding_score`'s denominator; **new:** any dangling reference additionally hard-caps the whole metric's raw score at `-0.3` |
| Design tier classification is ambiguous (heuristic multi-match) or unresolved (zero-match) | Both route to `[sem]`, never a silent heuristic guess; resulting lower confidence taxes the eventual score further toward whichever direction it already points |
| Claim has no `Sources` entries | `grounding_subscore = -1.0` (Rule 16 violation, not "no data to check") |
| `Sources` entry passes the substring gate but re-derivation finds the context doesn't support it | `MISREAD` floors the *entire claim's* grounding score at `-1.0`, worse than a missing source |
| Re-derivation call itself can't determine context either way | `UNDECIDABLE` scores `-0.3` per source, not a free pass |
| Design tier or claim type unclassifiable even after `[sem]` fallback | `entailment_subscore = -0.5` (ambiguity itself is a defect, not a pass-through) |
| Expected outcome too vague to judge direction | `AMBIGUOUS → -0.3`, never treated as a match |
| Artifact is non-clinical (publication-bias axis inapplicable) | Fixed `-0.2` contribution at full weight — caps the achievable ceiling rather than dropping the term |
| Clinical claim with no locatable trial id | `-0.8` — unverifiable is scored as a near-floor outcome |
| Trial id resolves but condition/intervention overlap is only one-sided | `-0.5` — explicit intermediate bucket, not rounded to "match" or "fabrication" |
| Trial id resolves but neither condition nor intervention overlaps | `-1.0` — treated as worse than absence (active fabrication signal) |
| Registered secondary outcome reframed as primary while the real primary is dropped | Extra `-0.3` stacked on the proportional drop deduction |
| Trial results are posted but direction check is `AMBIGUOUS` | `-0.2` — undecidable is still scored down, never skipped |
| `evidence/` file cited in `Sources` doesn't exist | Counted as a miss (`-1.0`) in that source's grounding contribution |

## 6. Why it's hard to Goodhart

- **Two of the five sub-checks start from purely deterministic gates** (binding, the grounding
  substring gate) that operate on exact string/id matches against files the compiler cannot rewrite
  without also rewriting `evidence/` itself. There is no low-effort textual trick that raises these
  without the underlying artifact actually being more consistent.
- **The warrant grid is a fixed, fully-derived lookup, not a persuadable judge** — once design tier
  and claim type are classified, the pass/fail is deterministic and auditable (§2.1); the only surface
  for gaming is misclassifying the design tier or claim type, which the `[sem]` calls constrain to a
  small closed label set, and which cycle 2 now taxes explicitly whenever the classification itself
  was uncertain (ambiguous keyword match).
- **Grounding is now two-layered**: a cheap deterministic gate that a fabricated citation cannot pass,
  followed by a re-derivation call that a locator-correct-but-misattributed citation cannot pass
  either. Beating both simultaneously requires the cited number to actually, correctly support the
  claim — i.e. requires the artifact to actually be right, not just look right.
- **The publication-bias axis checks against an external, third-party record** that the compiler has
  zero ability to edit. An author/compiler can write arbitrarily persuasive prose inside the artifact
  and it still cannot manufacture a favorable ClinicalTrials.gov record, alter which outcomes were
  registered, or change whether results are posted. Fabricating or mismatching an id is explicitly
  caught and penalized worse than omission; cycle 2 adds a same-treatment intermediate bucket for the
  one-axis-overlap ambiguous case, so that ambiguity itself can't be laundered into either extreme.
- **Padding does not help, at either level.** Intra-claim, `min()` over the `Proof` list means one bad
  link taints that claim regardless of how many good links surround it. Inter-claim, cycle 2's
  `blended_aggregate` means adding more well-behaved claims cannot dilute a real overreach out of the
  composite below a provable bound — see the worked example below.

### 6.1 Worked example: padding cannot dilute a real overreach

Suppose one claim (`C06`) has an `in_silico → causal` overreach, `entailment_subscore = -0.8`
(`heuristic_high` confidence, no tax), and every other claim is perfectly warranted (`1.0`).

**Plain mean (cycle-1 behavior)** — with 5 other claims:
`(5·1.0 + (−0.8)) / 6 = 0.70` — the composite already looks comfortably good despite an active
overclaim. Add 50 clean claims instead of 5: `(50·1.0 + (−0.8)) / 51 ≈ 0.965` — the overreach is
statistically invisible. As the padding count `N → ∞`, the mean `→ 1.0`: **the defect can be diluted
away arbitrarily closely to a perfect score**, which is exactly the failure mode the tournament judge
flagged.

**`blended_aggregate` (cycle-2 fix)** — with 5 other claims:
`0.5·0.70 + 0.5·(−0.8) = −0.05`. With 50 other claims: `0.5·0.965 + 0.5·(−0.8) = 0.0825`. As `N → ∞`,
`mean → 1.0` but `min` stays pinned at `−0.8` forever, so the blend is bounded:

```
entailment_score ≤ 0.5·1.0 + 0.5·(−0.8) = 0.10   for ANY N, no matter how large
```

No amount of padding can push the composite above `0.10` while that one overreach claim exists. This
is the concrete, provable form of "min-not-mean at every aggregation level," extended from
intra-claim (kept from cycle 1) to inter-claim (new in cycle 2).

## 7. Composition with the rest of the suite

This metric is deliberately a **joint cross-file consistency check** (`claims.md` × `experiments.md`
× `evidence/`, cross-referencing `constraints.md`/`study_design.md` for registration) plus one
external call — it does not re-score any single file's internal completeness. It composes cleanly
alongside metrics that separately score:
- `claims.md` standalone quality (falsifiability, `Sources` formatting, comprehensiveness) — this
  metric assumes those are scored elsewhere and instead asks whether the *content* actually holds
  together across files.
- `evidence/` standalone completeness (all tables/figures filed, no fabricated data tables in
  diagram-type figures) — this metric consumes that layer's body text but doesn't re-audit its
  internal filing completeness.
- Generic ARA-verifier D1 semantic entailment — this metric is intentionally a strict superset in
  difficulty (type/design-warrant-aware, re-derived-in-context grounding, not generic support) and
  adds an entirely external publication-bias axis the verifier has no mechanism to run at all.

Because its deterministic gates (binding, grounding substring gate, digit-leak) are cheap and its
`[sem]`/`[ext]` sub-checks are narrowly scoped (closed label sets, one external API call per
artifact, re-derivation and result-direction calls only fire after a cheap gate already passed), it
stays runnable at scale without becoming a second general-purpose verifier.
