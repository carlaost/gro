### M19 — Claim↔Experiment↔Evidence entailment (+ publication-bias) — Expansion 2

## 1. Why this indicator signals good science

A paper's rhetorical claims and its actual verification apparatus can drift apart in three
distinct ways, and each is a real, common defect this metric must catch:

1. **Type mismatch** — the claim asserts more than the experiment's design can license (a
   cross-sectional cohort producing a causal claim; an in-silico benchmark producing a claim about
   "real-world" performance; a single-arm case study producing a comparative-superiority claim).
   This is the "overclaiming" failure mode and is the single most common way published science
   overstates itself.
2. **Grounding mismatch** — the claim's `Sources` entries cite an evidence object, but the exact
   number/quote doesn't actually live there (hallucinated or misattributed support), or the
   evidence object cited doesn't exist at all.
3. **Selective/directional mismatch at the population level** — the study was pre-registered (a
   clinical trial with an NCT/ISRCTN/EudraCT id) with a defined primary/secondary outcome set, and
   the paper's claims quietly report only the outcomes that came out favorably, or omit that the
   registry shows the trial was terminated/results differ. This is publication bias made concrete
   and checkable, not a vibe — it is the one sub-check in this metric that reaches **outside** the
   artifact to an authoritative external record the compiler cannot rewrite.

What it must reward: claims whose asserted strength (causal / comparative / associative /
descriptive / mechanistic) is actually warranted by the experiment's declared design, whose cited
numbers are verbatim traceable into `evidence/`, and — for registered trials — whose reported
outcome set and direction match the public registry.

What it must NOT reward: verbose `Evidence basis` prose that never gets checked against the actual
table/figure cell; a long `Verifies`/`Proof` list where most links are semantically vacuous
(padding entailment surface without truthfully increasing coverage); an experiment with vague,
non-directional `Expected outcome` language that trivially "matches" any claim; a `Setup` that
claims "randomized" or "double-blind" language to *sound* like an RCT without a locatable
registration to back it.

## 2. Failure modes / gaming routes and how the design closes them

| Gaming route | Closed by |
|---|---|
| Pad `Verifies`/`Proof` with irrelevant claim/experiment pairs to inflate apparent "verified" coverage | Direction check returns `ORTHOGONAL`/`AMBIGUOUS` for vacuous pairs, and aggregation is **min over Proof list**, not mean — one bad link taints the whole claim, so padding never helps and often hurts |
| Write `Setup: Design: randomized, double-blind` with no real trial id to claim RCT-tier warrant | Publication-bias sub-check requires a resolvable, condition-matched NCT/ISRCTN/EudraCT id whenever the artifact signals a clinical-intervention claim; absence or condition-mismatch is scored down, not skipped |
| Vague, non-directional `Expected outcome` ("results were as expected") to auto-match any claim's `Status` | `[sem]` direction classifier returns `AMBIGUOUS` for outcomes lacking directional language — `AMBIGUOUS` is penalized, never a pass |
| Leak an exact number into `Expected outcome`/`Metrics` (Critical Rule #3 violation) to make the "entailment" check trivially exact | Deterministic digit-leak probe flags it and applies an explicit deduction on top of the entailment sub-score — an easy win is turned into a defect |
| Cite `Evidence basis` in prose without matching `Sources` quotes, or cite a `Sources` entry to a table that doesn't contain the value | `grounding_subscore` requires the verbatim quote (or, at reduced credit, the bare value) to literally appear in the target evidence file's body text; missing entirely = floor score |
| Fabricate a plausible-looking NCT id | External lookup either returns nothing (fabrication penalized same as absence) or returns a trial whose registered `condition` doesn't overlap the artifact's subject terms — treated as **worse** than absence, since it's an active fabrication, not a gap |
| Selectively report only the registered outcomes that came out favorably | `publication_bias_subscore` diffs `registered_primary_outcomes` against outcomes actually surfaced in `claims.md`/evidence; any dropped primary outcome scores down proportionally |
| Claim causal/superiority language from an observational or in-silico design | Warrant matrix: `entailment_subscore(design_tier, claim_type)` returns a large negative for `(observational_cohort, causal)`, `(cross_sectional, causal)`, `(in_silico, causal)`, etc. |

## 3. How the assessment-critique notes change the design

The ledger note for M19 says the ARA verifier already does claim↔evidence entailment "D1
semantically," and that the **publication-bias cross-check** is the piece that beats both round-1
metrics and the verifier. Two concrete design decisions follow from that, and both are load-bearing
in the scoring function below (§4.5):

- **The entailment half must not duplicate the verifier's generic semantic match.** A metric that
  just asks "does the evidence support the claim, yes/no" is exactly D1 and adds nothing. So this
  design makes entailment **type-aware and design-warranted**: it classifies the claim's assertion
  type (causal / comparative / associative / descriptive / mechanistic / non-inferiority / safety)
  and the experiment's design tier (RCT / observational / cross-sectional / meta-analysis /
  wet-lab / in-silico / case-study) independently, then checks the *warrant relationship* between
  them — a strictly harder and more specific question than "is this supported," and one the
  generic verifier check does not ask.
- **The publication-bias axis gets the largest single weight (0.30 of 1.0, §4.5)**, deliberately
  more than either the type-aware entailment (0.25) or the grounding check (0.20), because it is
  the genuinely net-new capability (external registry lookup, no other metric or the verifier does
  this) and the brief instructs preserving that edge rather than treating it as a minor bolt-on.

## 4. Generation/compute workflow

### 4.1 Inputs (artifact fields, per DATA_SHAPES.md / 05_experiments.md)

- `logic/claims.md` — per claim: `Statement`, `Status`, `Proof` (→E## ids), `Evidence basis`,
  `Sources` (list of `{value, ref, locator, quote, tag}`), `Dependencies`.
- `logic/experiments.md` — per experiment: `Verifies` (→C## ids), `Setup` (free-form subkeys),
  `Procedure`, `Metrics`, `Expected outcome`, `Baselines`, `Dependencies`.
- `evidence/README.md` + `evidence/tables/*.md` + `evidence/figures/*.md` — flattened body text per
  file, keyed by ref-path, for the grounding check.
- `logic/solution/constraints.md` (+ `study_design.md` if present) — searched for a trial
  registration id and for a "terminated"/limitation acknowledgment.
- `logic/problem.md` — subject terms, used only to sanity-check a looked-up trial's registered
  `condition` against the paper's actual subject (fabrication/mismatch guard).

### 4.2 Step-by-step procedure

1. **Bind claims↔experiments bidirectionally** (deterministic, cheap, run first — a dangling
   reference here means nothing downstream can even be evaluated, which itself is scored, not
   skipped).
2. **Classify each experiment's design tier** from `Setup` via keyword heuristic; fall back to an
   `[sem]` call only when the heuristic can't resolve it.
3. **Classify each claim's assertion type** via an `[sem]` call over `Statement`.
4. **Score the warrant relationship** between design tier and claim type via a fixed lookup table
   (no LLM call needed once both are classified — deterministic and auditable).
5. **Grounding check**: for every `Sources` entry, deterministically search the target evidence
   file's body text for the verbatim `quote`; fall back to bare `value` match at reduced credit.
6. **Direction check**: an `[sem]` call comparing `Expected outcome` (experiment) against
   `Statement`+`Status` (claim) for directional entailment vs. contradiction vs. irrelevance vs.
   ambiguity.
7. **Digit-leak probe**: deterministic regex over `Expected outcome`/`Metrics` for exact numbers
   (excluding stated significance thresholds like `FDR<0.05`, which are design, not result);
   applies an extra deduction, does not replace step 6.
8. **Publication-bias cross-check**:
   a. Deterministic + `[sem]` signal: does this artifact assert a clinical-intervention
      comparative/causal claim (drug/device/procedure) at all? (Most non-clinical ARAs — omics,
      ML, pure meta-analysis of observational data — will not.)
   b. If yes: search `constraints.md`/`study_design.md`/`claims.md` for an NCT/ISRCTN/EudraCT id.
   c. `[ext trial lookup]`: call the trial registry (ClinicalTrials.gov API v2 `get_trial_details`,
      or equivalent) for that id.
   d. Compare the registry's `primary_outcomes` set against outcomes actually surfaced in
      `claims.md`; compare registry `status`/`results_posted` against what `constraints.md`
      discloses; sanity-check registry `condition` against `problem.md` subject terms to catch a
      fabricated/mismatched id.
9. **Aggregate** per the weighted formula in §4.5; rescale to the suite's 0–1 reporting range.

### 4.3 `[sem]` call specifications

**Call A — design tier fallback** (only when the keyword heuristic in `classify_design_tier`
returns `unclassified_sem`):
```
You are classifying an experiment's evidentiary design tier from its Setup block.
Setup: {setup_dict}
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
You are checking DIRECTIONAL consistency only — exact numeric matching is handled by a separate
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

**Call D — clinical-intervention signal** (gates whether the publication-bias axis is
"applicable"):
```
Does this research artifact's problem statement and claims concern a clinical intervention (drug,
device, procedure, or behavioral/therapeutic intervention) being compared for effect, as opposed to
e.g. pure observational biomarker ranking, omics/mechanistic analysis, or a computational/ML method
with no clinical intervention arm?
Problem statement key excerpts: {problem_excerpt}
Claim statements: {claim_statements}
Answer strictly: YES | NO
```

### 4.4 `[ext trial lookup]` specification

- Input: an extracted registration id (regex `NCT\d{8}` or `ISRCTN\d+` or `EudraCT` pattern) found
  in `constraints.md` / `study_design.md` / `claims.md`.
- Call: `get_trial_details(id)` (ClinicalTrials.gov API v2 or equivalent registry API) →
  `{condition, primary_outcomes: [...], secondary_outcomes: [...], status, results_posted: bool}`.
- Failure modes to treat explicitly, never silently: lookup returns nothing (id doesn't resolve);
  lookup resolves but `condition` doesn't overlap the artifact's subject terms (id likely
  fabricated/mismatched — worse than absence); lookup succeeds and matches (proceed to diff).

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
    body_text: str                # flattened markdown body, used for substring grounding checks

@dataclass
class TrialRecord:
    condition: str
    primary_outcomes: list[str]
    secondary_outcomes: list[str]
    status: str                   # "completed" | "terminated" | "withdrawn" | ...
    results_posted: bool


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


# ---- Step 2: design tier (heuristic first, [sem] fallback) ----

DESIGN_TIER_KEYWORDS = {
    "rct": ["randomiz", "double-blind", "placebo-controlled", "treatment arm"],
    "observational_cohort": ["cohort", "prospective", "retrospective", "registry-based"],
    "cross_sectional": ["cross-sectional", "single time point"],
    "meta_analysis": ["network meta-analysis", "pooled", "systematic review"],
    "in_vitro_wetlab": ["assay", "sequencing", "cell line", "spatial", "pipeline"],
    "in_silico": ["simulation", "synthetic data", "held-out split", "benchmark dataset"],
    "case_study": ["case report", "single patient", "n=1"],
}

def classify_design_tier(setup: dict, sem_fn) -> str:
    blob = " ".join(str(v) for v in setup.values()).lower()
    for tier, kws in DESIGN_TIER_KEYWORDS.items():
        if any(kw in blob for kw in kws):
            return tier
    return sem_fn("classify_design_tier", setup=setup)  # Call A


# ---- Step 3+4: claim assertion type + warrant matrix ----

WARRANT_MATRIX = {
    "rct": {"causal", "comparative_superiority", "non_inferiority", "safety_adverse"},
    "observational_cohort": {"associative_correlational", "descriptive_prevalence", "safety_adverse"},
    "cross_sectional": {"descriptive_prevalence", "associative_correlational"},
    "meta_analysis": {"comparative_superiority", "non_inferiority", "associative_correlational"},
    "in_vitro_wetlab": {"mechanistic", "descriptive_prevalence"},
    "in_silico": {"mechanistic", "descriptive_prevalence"},
    "case_study": {"descriptive_prevalence"},
}
OVERREACH_PENALTY = {
    ("observational_cohort", "causal"): -0.6,
    ("cross_sectional", "causal"): -0.8,
    ("in_silico", "causal"): -0.8,
    ("case_study", "comparative_superiority"): -0.7,
}
DEFAULT_OVERREACH_PENALTY = -0.4

def entailment_subscore(design_tier: str, claim_type: str) -> float:
    if design_tier == "unclassifiable" or claim_type == "unclassifiable":
        return -0.5           # classification itself failed -> thin/ambiguous artifact, penalized
    if claim_type in WARRANT_MATRIX.get(design_tier, set()):
        return 1.0
    return OVERREACH_PENALTY.get((design_tier, claim_type), DEFAULT_OVERREACH_PENALTY)


# ---- Step 5: grounding (deterministic verbatim/value match into evidence/) ----

def grounding_subscore(claim: Claim, evidence_by_file: dict[str, EvidenceObject]) -> float:
    if not claim.sources:
        return -1.0            # Rule 16 violation: no grounding entries at all
    hits, total = 0.0, len(claim.sources)
    for src in claim.sources:
        ev = evidence_by_file.get(src["ref"])
        if ev is None:
            continue           # missing target file -> counted as a miss
        if src.get("quote") and src["quote"] in ev.body_text:
            hits += 1.0
        elif src["value"] in ev.body_text:
            hits += 0.7        # value present but not verbatim-quote-verified: partial credit
    return (hits / total) * 2 - 1        # map [0,1] -> [-1,1]


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

def condition_matches(trial_condition: str, subject_terms: list[str]) -> bool:
    tc = trial_condition.lower()
    return any(term.lower() in tc for term in subject_terms)

def publication_bias_subscore(artifact, trial_lookup_fn, sem_fn) -> float:
    applicable = sem_fn("clinical_intervention_signal",                       # Call D
                         problem_excerpt=artifact.problem_excerpt,
                         claim_statements=artifact.claim_statements) == "YES"
    if not applicable:
        # Genuinely out-of-scope axis (e.g. omics/ML paper). Penalize-don't-skip: contributes at a
        # fixed low-neutral value rather than being dropped from the denominator, so a non-clinical
        # artifact can never reach ceiling on an axis it cannot be audited against.
        return -0.2

    nct_id = find_trial_registration(artifact)
    if nct_id is None:
        return -0.8            # claims a clinical comparative effect, no locatable registration

    trial = trial_lookup_fn(nct_id)                                            # [ext trial lookup]
    if trial is None:
        return -0.8            # id present but doesn't resolve -> unverifiable, same floor as absent

    if not condition_matches(trial.condition, artifact.subject_terms):
        return -1.0            # id resolves to an unrelated trial -> fabrication/mismatch, worse than absence

    registered_primary = set(trial.primary_outcomes)
    reported = set(artifact.reported_outcomes)     # extracted from claims.md statements + evidence tables
    dropped = registered_primary - reported

    score = 1.0
    if dropped:
        score -= 0.5 * (len(dropped) / max(len(registered_primary), 1))
    if trial.status in ("terminated", "withdrawn") and "terminated" not in artifact.constraints_text.lower():
        score -= 0.4
    if trial.results_posted and artifact.claims_direction_conflicts_with(trial):
        score -= 0.6
    return max(score, -1.0)


# ---- Step 9: aggregate ----

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
        per_ground.append(grounding_subscore(c, evidence_by_file))
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
            tier = classify_design_tier(e.setup, sem_fn)
            exp_scores.append(entailment_subscore(tier, claim_type))
            dir_scores.append(direction_subscore(e.expected_outcome, c.statement, c.status, e.metrics, sem_fn))
        per_entail.append(min(exp_scores))          # weakest-link: one bad Proof entry taints the claim
        per_direction.append(min(dir_scores))

    n = max(len(claims), 1)
    entailment_score = sum(per_entail) / n
    grounding_score = sum(per_ground) / n
    direction_score = sum(per_direction) / n
    pub_bias_score = publication_bias_subscore(artifact, trial_lookup_fn, sem_fn)

    raw = (WEIGHTS["binding"] * binding_score
           + WEIGHTS["entailment"] * entailment_score
           + WEIGHTS["grounding"] * grounding_score
           + WEIGHTS["direction"] * direction_score
           + WEIGHTS["publication_bias"] * pub_bias_score)
    return (raw + 1) / 2          # rescale [-1,1] -> [0,1] for the suite's reporting convention
```

## 5. Penalize-don't-skip mapping

Every sub-check has an explicit floor for the corresponding unavailable/thin case — none of them
return `None`/N-A:

| Condition | Behavior |
|---|---|
| Claim has no `Proof` | `entailment=-1.0`, `direction=-1.0` for that claim (not excluded from the average) |
| `Proof`/`Verifies` reference doesn't resolve | `-1.0` binding finding; still included in `binding_score`'s denominator |
| Claim has no `Sources` entries | `grounding_subscore = -1.0` (Rule 16 violation, not "no data to check") |
| Design tier or claim type unclassifiable even after `[sem]` fallback | `entailment_subscore = -0.5` (ambiguity itself is a defect, not a pass-through) |
| Expected outcome too vague to judge direction | `AMBIGUOUS → -0.3`, never treated as a match |
| Artifact is non-clinical (publication-bias axis inapplicable) | Fixed `-0.2` contribution at full weight — caps the achievable ceiling rather than dropping the term |
| Clinical claim with no locatable trial id | `-0.8` — unverifiable is scored as a near-floor outcome |
| Trial id resolves but to an unrelated condition | `-1.0` — treated as worse than absence (active fabrication signal) |
| `evidence/` file cited in `Sources` doesn't exist | Counted as a miss in `grounding_subscore`'s hit ratio, dragging the ratio down, not skipped |

## 6. Why it's hard to Goodhart

- **Two of five sub-checks are purely deterministic** (binding, grounding) and operate on exact
  string/id matches against files the compiler cannot rewrite without also rewriting `evidence/`
  itself — which other metrics in the suite already separately audit for completeness/fabrication.
  There is no low-effort textual trick that raises these without the underlying artifact actually
  being more consistent.
- **The warrant-matrix check is a fixed lookup table, not a persuadable judge** — once design tier
  and claim type are classified, the pass/fail is deterministic and auditable; the only surface for
  gaming is misclassifying the design tier or claim type, which the `[sem]` calls constrain to a
  small closed label set (easy to spot-check, no room for eloquent hedging to shift a label).
- **The publication-bias axis checks against an external, third-party record** (a public trial
  registry) that the compiler has zero ability to edit. This is the strongest anti-Goodhart lever in
  the whole metric: an author/compiler can write arbitrarily persuasive prose inside the artifact
  and it still cannot manufacture a favorable ClinicalTrials.gov record. Fabricating an id is
  explicitly caught (condition mismatch) and penalized *more* than omission.
- **Padding does not help.** Because per-claim entailment/direction use `min()` over the `Proof`
  list rather than an average, and because the composite averages per-claim scores over all claims
  (not just the ones with clean links), adding more claims or more Proof/Verifies edges to look
  thorough only increases the number of places a mismatch can be caught — it cannot dilute existing
  penalties the way an averaged "percent of claims well-supported" metric could be gamed by adding
  easy padding claims alongside a few real ones.

## 7. Composition with the rest of the suite

This metric is deliberately a **joint cross-file consistency check** (`claims.md` ×
`experiments.md` × `evidence/`, cross-referencing `constraints.md`/`study_design.md` for
registration) plus one external call — it does not re-score any single file's internal
completeness. It composes cleanly alongside metrics that separately score:
- `claims.md` standalone quality (falsifiability, `Sources` formatting, comprehensiveness) —
  this metric assumes those are scored elsewhere and instead asks whether the *content* actually
  holds together across files.
- `evidence/` standalone completeness (all tables/figures filed, no fabricated data tables in
  diagram-type figures) — this metric consumes that layer's body text but doesn't re-audit its
  internal filing completeness.
- Generic ARA-verifier D1 semantic entailment — this metric is intentionally a strict superset in
  difficulty (type/design-warrant-aware, not generic support) and adds an entirely external
  publication-bias axis the verifier has no mechanism to run at all.

Because its three deterministic sub-checks (binding, grounding, digit-leak) are cheap and its two
`[sem]`/`[ext]` sub-checks are narrowly scoped (closed label sets, one external API call per
artifact), it stays runnable at scale without becoming a second general-purpose verifier.
