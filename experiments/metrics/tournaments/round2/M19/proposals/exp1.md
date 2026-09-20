# M19 — Claim↔Experiment↔Evidence Entailment (+ publication-bias cross-check)

Expander 1

## 1. Expanded reasoning

### 1.1 What this indicator is actually measuring

Seal Level 1 already checks that every `Proof` id on a claim resolves to a real `E##` block and every
`Verifies` id on an experiment resolves back to a real `C##` block (`DATA_SHAPES.md` §5 "Availability
notes" — cross-layer binding), and the ARA verifier's own "D1" pass does a first semantic look at
claim↔experiment consistency. That structural resolution is necessary but shallow: a dangling-reference
check (or even a same-topic semantic-similarity check) cannot tell you that the experiment, as
*designed*, is capable of supporting what the claim actually asserts. Two failure shapes look identical
under pure reference-resolution but are opposite in scientific value:

- **Good**: `C01` states a P-score ranking (`p217_MS 0.859 > ... > p181_IA 0.117`), `Proof: [E01]`,
  and `E01`'s `Setup.Design` is an NMA over exactly those nodes, `Metrics` is "P-score per node," and
  `Expected outcome` is "isoform ranking differs by platform" — the experiment's design *type* matches
  the claim's assertion *type* (a comparative ranking claim needs a comparative-ranking design).
- **Bad but reference-clean**: a claim stated as *causal* ("assay X drives outcome Y") whose `Proof`
  experiment is a purely observational cross-sectional correlation with no intervention/perturbation
  arm. `Proof`/`Verifies` both resolve fine; the claim is still not entailed by the evidence, because
  the experiment's design cannot license the claim's causal register. This is the exact gap this metric
  exists to close, and it is why it beat the verifier's D1 check and every round-1 candidate: it is
  **type-aware** entailment, not reference-resolution or topic-similarity.

The **publication-bias cross-check** is a second, independent axis that piggybacks on the same claim↔
experiment pair but reasons *outward* to a registry the paper does not control: if the work is
registrable (RCT, meta-analysis with PROSPERO, a preregistered OSF study), does the *as-compiled*
claim/outcome set match what was registered *before* results were known? A claim that quietly reports a
secondary/exploratory endpoint as if it were a clean confirmatory finding, or omits a pre-registered
primary endpoint that presumably came back null, is the single most consequential "good science" defect
this metric can catch that nothing else in the suite reaches (concepts/problem/constraints layers never
see the registry; the evidence layer only sees what the paper *chose* to report).

### 1.2 What it must reward

- A `C##`→`E##` pair where the experiment's `Setup`/`Procedure`/`Metrics` design-type is sufficient for
  the claim's assertion-type (existence, correlational, comparative/ranking, predictive, causal/
  mechanistic — see §2.1 taxonomy below), AND the `Expected outcome` direction in `experiments.md`
  agrees with the `Statement` direction in `claims.md`, AND the `Evidence basis` cites `evidence/`
  objects that independently carry the asserted numbers (not just restated prose).
- A `Falsification criteria` that is actually testable by the cited experiment's `Metrics` — i.e. the
  experiment could, in principle, have produced the falsifying observation. A falsification criterion
  that references a condition the experiment's design structurally cannot detect (e.g. "refuted if
  effect reverses in an independent cohort" when `Baselines: none` and no replication arm exists) is a
  paper-tautology, not a real falsifiable claim, and should be scored down even though it "looks"
  rigorous.
- Registered work (trial ID, PROSPERO CRD, OSF DOI discoverable in `src/environment.md` /
  `logic/solution/constraints.md` / `logic/related_work.md`) whose reported primary/secondary outcome
  set in `claims.md` matches the pre-registered outcome set, with no direction flips.

### 1.3 What it must NOT reward

- **Reference-resolution masquerading as entailment.** `Proof`/`Verifies` both existing and pointing at
  something on-topic is necessary, not sufficient — do not let a clean cross-reference substitute for
  the type-aware check.
- **Circular grounding**: `Evidence basis` in `claims.md` that merely re-states the `Statement` in
  different words without adding an independently-sourced number/quote is not entailment; the metric
  must diff `Evidence basis` against the actual `evidence/tables|figures/*.md` content the `Sources`
  entries point at, not just check that a `Sources` entry exists (Seal Level 1 already checks existence
  of the quote; this metric checks that the quoted evidence *actually supports the specific assertion*,
  including its direction and its comparison set).
- **Status inflation**: `Status: supported` when the design type is weaker than the claim's register
  (observational design + causal claim language) should be scored down regardless of how well-grounded
  the underlying numbers are — the numbers can be perfectly real and the *inference* still overclaimed.
- **Vague, always-true `Expected outcome`/Falsification pairs** ("results will differ across groups")
  that trivially "match" any reported outcome — these should score as weak entailment, not strong,
  because they carry no discriminating power.

### 1.4 Failure modes / gaming routes and why they're hard to sustain

1. **Weasel-word `Expected outcome`.** A compiler (or an adversarial ARA author) could make every
   `Expected outcome` maximally vague so it "matches" whatever the evidence says. Countermeasure: the
   [sem] entailment call explicitly scores *specificity* of the expected-outcome/claim pairing (does it
   name a direction, a comparator, a magnitude class) — vagueness caps the entailment sub-score low
   rather than defaulting high, which is the opposite incentive from naive keyword-matching metrics.
2. **Padding `Verifies`/`Proof` density.** Splitting one experiment into several near-duplicate blocks,
   or citing many `E##` per claim, to look thoroughly verified. Countermeasure: the per-claim score is
   the *max* type-aware entailment across its cited experiments, not a count or sum — duplication buys
   nothing.
3. **Overclaiming registration compliance.** Citing a registry ID that doesn't actually correspond to
   the reported outcomes (wrong trial, or a registration for a *different* analysis than what's
   reported). Countermeasure: the trial-lookup step matches on population/intervention/primary-endpoint
   text similarity, not just presence of an ID string — a mismatched ID scores as a registry *failure*,
   worse than no ID at all, because it is a misleading-provenance signal.
4. **Selective non-disclosure of registration.** Simply not mentioning a known registry ID to dodge the
   cross-check. Countermeasure: for any claim whose `Setup` fields look clinical-trial-shaped
   (`Population`/`Intervention`/`Randomization`/`Endpoint` present) or meta-analytic
   (`Design` mentions systematic review/NMA), absence of a discoverable registration is *itself* scored
   down under the availability rule (§3.5) rather than skipped — you cannot game the check by omission,
   because omission is the penalized condition, not a neutral one.
5. **Gaming the [sem] classifier with confident-sounding language.** A `Statement` phrased with
   hedge-free, declarative causal language over what is actually observational data. Countermeasure: the
   classifier is anchored on `Setup`/`Procedure` (what was actually done), not on the rhetorical
   register of `Statement`/`Interpretation` — it classifies the *experiment's* capability independent of
   how confidently the claim is worded, then compares that capability against what the claim asserts.

### 1.5 Composition with the rest of the suite

This metric assumes claim/experiment/evidence *structural* validity is checked elsewhere (Seal Level 1
cross-binding, grounding-source existence) — it does not re-do that gate, it consumes its output as a
precondition and *additionally* penalizes structural failures found along the way (a dangling `Proof` or
a `Sources` entry with no quote directly lowers this metric's score too, since a broken link is also an
entailment failure — you cannot entail a claim from evidence you can't resolve). It is deliberately
narrower than a generic "grounding" metric (it does not re-score `concepts.md` vocabulary quality or
`related_work.md` citation coverage) and deliberately deeper than the verifier's D1 pass (type-aware
design-sufficiency + external registry cross-check, not topic-level semantic match). It composes
multiplicatively rather than additively with a general grounding/fabrication metric: a claim can be
well-grounded (real numbers, real quotes) yet still fail *this* metric on inferential overreach, and a
claim can pass this metric's design-sufficiency check yet still fail a grounding metric if the numbers
are fabricated — the two failure modes are orthogonal, which is why this metric is net-new rather than
redundant.

---

## 2. Generation / compute workflow

### 2.1 Inputs (exact artifact fields)

From `logic/claims.md`, per `C##` block: `Statement`, `Status`, `Falsification criteria`, `Proof`
(list of `E##`), `Evidence basis`, `Sources` (list of `value ← path (locator) «quote» [input|result]`).

From `logic/experiments.md`, per `E##` block: `Verifies` (list of `C##`), `Setup` (nested key:value,
genre-dependent subkeys), `Procedure`, `Metrics`, `Expected outcome`, `Baselines`, `Dependencies`.

Cross-layer (read-only, per EXPAND_BRIEF's named sections):
- `logic/concepts.md` — resolves domain vocabulary used to classify claim/metric type (e.g. recognizing
  "P-score"/"SUCRA" as ranking constructs, "hazard ratio" as survival-analysis constructs).
- `logic/problem.md` (`Key Insight`, `Assumptions`) — used only to detect a mismatch between the paper's
  stated epistemic ambition and the claim's assertion register (e.g. Key Insight framed as descriptive
  but a downstream claim asserts a causal mechanism nothing in problem.md motivates).
- `logic/solution/constraints.md` + sibling method files (`study_design.md`, etc.) — supplies `Design`
  type, registration statements (PROSPERO CRD, trial ID, OSF DOI), and `Boundary conditions`/
  `Known limitations` that bound how far a claim's design-type can license its assertion.
- `evidence/README.md` + `evidence/tables/*.md` + `evidence/figures/*.md` — the ground truth every
  `Sources` entry must resolve into; used to independently re-derive whether the cited object actually
  contains the asserted comparison/direction/magnitude class.
- `src/environment.md` `Protocols` field — secondary source of registration IDs when not in
  `constraints.md`.

### 2.2 Step-by-step procedure

**Step 0 — Parse and structurally bind.** For every `C##` in `claims.md`, resolve every `Proof` id
against `experiments.md`; for every `E##`, resolve every `Verifies` id back against `claims.md`.
Unresolved ids are recorded as `binding_defects` (do not drop the claim — it still gets scored, at the
structural-defect floor per §3.5).

**Step 1 — Classify each claim's assertion type.** [sem] call (see §2.3 prompt A) over
`Statement` + `Falsification criteria` + `concepts.md` entries referenced by the claim's `Tags`/prose.
Output: one of `existence | correlational | comparative_ranking | predictive | causal_mechanistic`,
plus a `specificity` score (0–1: does the statement name a direction/comparator/magnitude class, or is
it a vague hedge).

**Step 2 — Classify each cited experiment's design sufficiency.** [sem] call (see §2.3 prompt B) over
the experiment's `Setup`/`Procedure`/`Metrics`/`Baselines`, plus the relevant `constraints.md`/
`study_design.md` `Design` field. Output: the *maximum* assertion type this design could license
(same enum as Step 1), plus a `design_confidence` (0–1, reflecting things like presence of a
comparator/`Baselines`, randomization language, replication/independent-cohort language).

**Step 3 — Type-aware entailment score per (C##, E##) pair.** Deterministic rule, not an LLM call,
applied to the outputs of Steps 1–2 (see the `TYPE_RANK` ordering in the code below) plus an [sem]
directional-match call (prompt C) that checks whether `Expected outcome` in the experiment agrees in
*direction* with the claim `Statement`, and whether `Evidence basis` in the claim is independently
corroborated by the actual `evidence/` object content (fetched and diffed programmatically, not just
asserted by the LLM) rather than being circular.

**Step 4 — Registry / publication-bias cross-check.** For each ARA:
1. Regex-scan `src/environment.md`, `logic/solution/constraints.md`, and `logic/related_work.md`'s
   "Review registration (folded-in grounded source)" block for a trial identifier
   (`NCT\d{8}`), a PROSPERO CRD (`CRD\d+`), or an OSF DOI (`10\.17605/OSF\.IO/\w+`).
2. If found: call the registry lookup (`mcp__claude_ai_Clinical_Trials__get_trial_details` for an NCT
   id; a plain web/OSF/PROSPERO fetch otherwise) and extract the registered primary/secondary outcome
   list and population/intervention description.
3. [sem] call (prompt D) comparing the registered outcome set against the full set of `Statement`s in
   `claims.md` whose `Setup` (via their `Proof` experiments) looks clinical/meta-analytic: flag
   `outcome_switching` (a claim reports a non-registered outcome as primary), `omission`
   (a registered primary outcome has no corresponding claim at all), or `direction_conflict`.
4. If a clinical/meta-analytic `Setup` signature is detected (see `_looks_registrable` below) but no
   identifier is found anywhere in the ARA: this is scored as a registry **failure**, not skipped
   (§3.5).
5. If the work is genuinely non-registrable-genre (no clinical/meta-analytic `Setup` signature anywhere,
   e.g. a pure wet-lab mechanistic paper or a theory paper), the publication-bias sub-score is not
   blank — it is set to a documented low-but-nonzero floor (`NONCLINICAL_FLOOR`, see code) reflecting
   that no external falsification channel exists for this genre; this keeps the metric monotonic
   (never rewards absence) while not conflating "not applicable" with "clean bill of health."

**Step 5 — Aggregate.** Combine per-claim entailment (Step 3) and the registry cross-check (Step 4)
into the final `[0,1]` score per the weighted formula in §2.4, folding in the structural-defect
penalties from Step 0.

### 2.3 [sem] prompts (exact)

**Prompt A — claim type + specificity classification**
```
You are classifying the assertion-type of a scientific claim, for entailment auditing.

Claim statement: "{statement}"
Falsification criteria: "{falsification_criteria}"
Relevant concept definitions (verbatim from concepts.md): {concept_snippets}

Classify the claim's assertion type as exactly one of:
- existence           (something exists / was observed / occurs)
- correlational        (an association between two things, no causal claim)
- comparative_ranking   (X outperforms/ranks above/differs from Y on a metric)
- predictive           (a model/rule forecasts an outcome, evaluated out-of-sample)
- causal_mechanistic   (X causes Y via a mechanism; requires an intervention/manipulation)

Also rate specificity 0.0-1.0: does the statement commit to a concrete direction, comparator, and
magnitude class (0.0 = fully vague/hedge, 1.0 = fully concrete, e.g. names the compared entities and
the direction of the effect)?

Return strict JSON: {"type": "<one of the five>", "specificity": <float>, "rationale": "<one sentence>"}
```

**Prompt B — experiment design sufficiency**
```
You are auditing whether an experiment's DESIGN (not its results) is capable of supporting different
classes of scientific assertion.

Setup: {setup_block}
Procedure: {procedure_block}
Metrics: {metrics_block}
Baselines: {baselines_field}
Design/statistical-model text from constraints.md or study_design.md (if any): {design_text}

Of the five assertion types [existence, correlational, comparative_ranking, predictive,
causal_mechanistic], which is the STRONGEST type this design could legitimately support, purely from
its structure (e.g. presence of a comparator/control arm and manipulation → causal_mechanistic
eligible; single-arm observational measurement → correlational or existence only; held-out
evaluation → predictive eligible; multi-arm ranked comparison → comparative_ranking eligible)?

Also rate design_confidence 0.0-1.0 for how cleanly the design supports even that strongest type
(0.0 = design is ambiguous/underspecified, 1.0 = textbook-clean for the type, e.g. explicit
randomization language, explicit independent replication/held-out cohort, explicit control arm).

Return strict JSON: {"max_supported_type": "<one of the five>", "design_confidence": <float>,
"rationale": "<one sentence>"}
```

**Prompt C — directional match + circularity check**
```
Claim statement: "{statement}"
Claim evidence basis (from claims.md): "{evidence_basis}"
Claim Sources quotes (verbatim from claims.md Sources field): {sources_quotes}
Actual evidence/ object content the Sources entries point to (fetched programmatically):
{evidence_object_excerpts}
Experiment expected outcome (from experiments.md): "{expected_outcome}"

Answer three yes/no questions with one sentence of justification each:
1. direction_match: does the experiment's Expected outcome agree in DIRECTION (not exact numbers) with
   the claim's Statement?
2. independently_corroborated: does the fetched evidence/ object content actually contain the specific
   comparison/number/direction the claim's Evidence basis asserts (not just topically related, but the
   SAME comparison)?
3. circular: does the claim's Evidence basis merely restate the Statement in different words, without
   citing anything the fetched evidence/ content adds independently?

Return strict JSON: {"direction_match": <bool>, "independently_corroborated": <bool>,
"circular": <bool>, "justification": "<=3 sentences>"}
```

**Prompt D — registry cross-check**
```
Registered study record (from trial/PROSPERO/OSF registry lookup):
  Population/eligibility: {registered_population}
  Intervention/exposure: {registered_intervention}
  Primary outcome(s): {registered_primary_outcomes}
  Secondary outcome(s): {registered_secondary_outcomes}
  Registration date: {registration_date}

Claims reported in this ARA that plausibly relate to the same study (Statement + Status for each):
{candidate_claim_statements}

For each registered primary outcome, state whether it: (a) is reported in the claims as a primary
finding, (b) is reported in the claims as a secondary/incidental finding, (c) is not reported in the
claims at all (silent omission).
For each reported claim, state whether its outcome was: (a) pre-registered as primary, (b)
pre-registered as secondary but promoted to primary framing in the claims (outcome switching),
(c) not pre-registered at all (a post-hoc/exploratory finding presented without that caveat).

Return strict JSON: {"omitted_primary_outcomes": [<string>...], "outcome_switching_claims": [<C## ids>],
"undisclosed_posthoc_claims": [<C## ids>], "clean": <bool>}
```

### 2.4 Deterministic scoring function

```python
"""
M19: Claim<->Experiment<->Evidence entailment (+ publication-bias cross-check)

Assumes upstream helpers (not shown) that:
  - parse claims.md / experiments.md / constraints.md / environment.md / related_work.md into the
    dict shapes used below (one dict per ## block, keys matching the DATA_SHAPES.md field names)
  - fetch evidence/ object content for a given Sources path+locator
  - call the [sem] LLM with a given prompt string and return parsed JSON (call_llm)
  - call the clinical-trial / registry lookup for a given identifier (lookup_registry)
"""

import re
from dataclasses import dataclass, field

TYPE_RANK = {
    "existence": 0,
    "correlational": 1,
    "comparative_ranking": 2,
    "predictive": 2,          # predictive and comparative_ranking are treated as siblings,
                               # neither strictly implies the other
    "causal_mechanistic": 3,
}

NCT_RE = re.compile(r"\bNCT\d{8}\b")
PROSPERO_RE = re.compile(r"\bCRD\d+\b")
OSF_RE = re.compile(r"\b10\.17605/OSF\.IO/\w+\b", re.IGNORECASE)

CLINICAL_SETUP_KEYS = {"population", "intervention", "randomization", "endpoint"}
META_ANALYTIC_MARKERS = ("systematic review", "network meta-analysis", "meta-analysis", "prisma")

NONCLINICAL_FLOOR = 0.35  # documented low-but-nonzero floor: "no external falsification channel
                          # exists for this genre" is worse than a clean registry match (1.0) but
                          # better than a detected registry failure (0.0) -- never silently == "N/A"

STRUCTURAL_DEFECT_PENALTY = 0.5   # multiplicative penalty per unresolved Proof/Verifies id
MISSING_QUOTE_PENALTY = 0.5       # multiplicative penalty per Sources entry with no verbatim quote


@dataclass
class ClaimEntailment:
    claim_id: str
    entailment_score: float
    binding_defects: int
    notes: str = ""


def _setup_signature(setup_block: dict) -> set[str]:
    return {k.strip().lower() for k in setup_block.keys()}


def _looks_registrable(claim: dict, experiments_by_id: dict) -> bool:
    """A claim 'looks registrable' if any experiment it cites has clinical-trial-shaped Setup keys,
    or if constraints/study_design text names a systematic-review/meta-analysis design."""
    for eid in claim.get("proof", []):
        exp = experiments_by_id.get(eid)
        if not exp:
            continue
        if _setup_signature(exp.get("setup", {})) & CLINICAL_SETUP_KEYS:
            return True
        design_text = " ".join(str(v) for v in exp.get("setup", {}).values()).lower()
        if any(m in design_text for m in META_ANALYTIC_MARKERS):
            return True
    return False


def _find_registry_ids(environment_md: str, constraints_md: str, related_work_md: str) -> dict:
    blob = "\n".join([environment_md, constraints_md, related_work_md])
    return {
        "nct": NCT_RE.findall(blob),
        "prospero": PROSPERO_RE.findall(blob),
        "osf": OSF_RE.findall(blob),
    }


def score_claim_entailment(
    claim: dict,
    experiments_by_id: dict,
    evidence_fetch,      # callable(path, locator) -> str, fetches evidence/ object excerpt
    call_llm,            # callable(prompt: str) -> dict, the [sem] call
) -> ClaimEntailment:
    binding_defects = 0
    proof_ids = claim.get("proof", [])
    if not proof_ids:
        # A claim with no Proof at all cannot be entailed by definition -- score at floor,
        # not skipped.
        return ClaimEntailment(claim["id"], 0.0, 1, "no Proof experiments cited")

    # Step 0: structural binding check (penalize-don't-skip: dangling refs lower, never N/A)
    resolved_experiments = []
    for eid in proof_ids:
        exp = experiments_by_id.get(eid)
        if exp is None or claim["id"] not in exp.get("verifies", []):
            binding_defects += 1
        else:
            resolved_experiments.append(exp)

    if not resolved_experiments:
        return ClaimEntailment(claim["id"], 0.0, binding_defects,
                                "all cited experiments dangling or non-reciprocal")

    # Step 0b: Sources-quote completeness (missing quote = grounding-for-entailment defect)
    sources = claim.get("sources", [])
    missing_quotes = sum(1 for s in sources if not s.get("quote"))
    quote_penalty = MISSING_QUOTE_PENALTY ** missing_quotes

    # Step 1: claim assertion type + specificity
    concept_snippets = claim.get("_related_concept_defs", "")
    type_resp = call_llm(PROMPT_A.format(
        statement=claim["statement"],
        falsification_criteria=claim["falsification_criteria"],
        concept_snippets=concept_snippets,
    ))
    claim_type = type_resp["type"]
    specificity = float(type_resp["specificity"])

    best_pair_score = 0.0
    best_notes = ""
    for exp in resolved_experiments:
        # Step 2: experiment design sufficiency
        design_resp = call_llm(PROMPT_B.format(
            setup_block=exp["setup"],
            procedure_block=exp["procedure"],
            metrics_block=exp["metrics"],
            baselines_field=exp["baselines"],
            design_text=exp.get("_design_text_from_constraints", ""),
        ))
        max_type = design_resp["max_supported_type"]
        design_confidence = float(design_resp["design_confidence"])

        # type-sufficiency: does the design's max supported type meet or exceed the claim's
        # assertion type on the ordinal TYPE_RANK ladder?
        sufficiency = 1.0 if TYPE_RANK[max_type] >= TYPE_RANK[claim_type] else 0.0
        # a design that's *more* than sufficient doesn't get extra credit; a design that's
        # insufficient caps the whole pair at a hard, low ceiling regardless of directional match
        if sufficiency == 0.0:
            pair_score = 0.15 * design_confidence  # near-floor: type mismatch is disqualifying
            best_pair_score = max(best_pair_score, pair_score)
            continue

        # Step 3: directional match + circularity (evidence fetched programmatically, not just
        # asserted by the LLM)
        evidence_excerpts = [
            evidence_fetch(s["path"], s["locator"]) for s in sources if s.get("path")
        ]
        match_resp = call_llm(PROMPT_C.format(
            statement=claim["statement"],
            evidence_basis=claim["evidence_basis"],
            sources_quotes=[s["quote"] for s in sources],
            evidence_object_excerpts=evidence_excerpts,
            expected_outcome=exp["expected_outcome"],
        ))

        direction_ok = bool(match_resp["direction_match"])
        corroborated = bool(match_resp["independently_corroborated"])
        circular = bool(match_resp["circular"])

        pair_score = design_confidence
        pair_score *= 1.0 if direction_ok else 0.3
        pair_score *= 1.0 if corroborated else 0.2
        pair_score *= 0.4 if circular else 1.0
        # specificity gate: vague, always-true claim/expected-outcome pairs cap out low even if
        # everything else checks out, per the anti-weasel-wording rule in section 1.4(1)
        pair_score *= max(specificity, 0.25)

        best_pair_score = max(best_pair_score, pair_score)
        best_notes = match_resp.get("justification", "")

    final = best_pair_score * quote_penalty * (STRUCTURAL_DEFECT_PENALTY ** binding_defects)
    return ClaimEntailment(claim["id"], final, binding_defects, best_notes)


def score_publication_bias(
    claims: list[dict],
    experiments_by_id: dict,
    environment_md: str,
    constraints_md: str,
    related_work_md: str,
    lookup_registry,     # callable(kind, identifier) -> dict registry record
    call_llm,
) -> float:
    registrable_claims = [c for c in claims if _looks_registrable(c, experiments_by_id)]

    ids = _find_registry_ids(environment_md, constraints_md, related_work_md)
    any_id = ids["nct"] or ids["prospero"] or ids["osf"]

    if not registrable_claims and not any_id:
        # Genuinely non-registrable genre (e.g. wet-lab mechanistic, theory/proof paper):
        # documented floor, not skipped, not conflated with "clean."
        return NONCLINICAL_FLOOR

    if registrable_claims and not any_id:
        # Clinical/meta-analytic-shaped work with NO discoverable registration: this is the
        # registry-failure case -- scored down hard, not skipped, per section 2.2 step 4.4.
        return 0.0

    # Registration found: pull the record and cross-check.
    kind, identifier = next(
        (k, v[0]) for k, v in (("nct", ids["nct"]), ("prospero", ids["prospero"]),
                                ("osf", ids["osf"])) if v
    )
    record = lookup_registry(kind, identifier)

    check = call_llm(PROMPT_D.format(
        registered_population=record.get("population", "not specified"),
        registered_intervention=record.get("intervention", "not specified"),
        registered_primary_outcomes=record.get("primary_outcomes", []),
        registered_secondary_outcomes=record.get("secondary_outcomes", []),
        registration_date=record.get("registration_date", "unknown"),
        candidate_claim_statements=[
            {"id": c["id"], "statement": c["statement"], "status": c["status"]}
            for c in registrable_claims
        ],
    ))

    if check["clean"]:
        return 1.0

    n_flags = (
        len(check.get("omitted_primary_outcomes", []))
        + len(check.get("outcome_switching_claims", []))
        + len(check.get("undisclosed_posthoc_claims", []))
    )
    # each independent flag type is a real, distinct publication-bias signal; compound penalty,
    # floor at 0.05 (never exactly 0 for a *found and checked* registry -- 0.0 is reserved for
    # "registrable but no registry found at all," which is a strictly worse condition)
    return max(0.05, 0.6 ** n_flags)


def score_m19(
    claims: list[dict],
    experiments: list[dict],
    environment_md: str,
    constraints_md: str,
    related_work_md: str,
    evidence_fetch,
    lookup_registry,
    call_llm,
    entailment_weight: float = 0.7,
    pub_bias_weight: float = 0.3,
) -> dict:
    experiments_by_id = {e["id"]: e for e in experiments}

    per_claim = [
        score_claim_entailment(c, experiments_by_id, evidence_fetch, call_llm)
        for c in claims
    ]
    # unweighted mean across claims -- a single badly-overclaimed claim should not be diluted away
    # by many well-behaved ones; a metric whose job is catching overreach must not let volume hide it
    entailment_component = (
        sum(p.entailment_score for p in per_claim) / len(per_claim) if per_claim else 0.0
    )

    pub_bias_component = score_publication_bias(
        claims, experiments_by_id, environment_md, constraints_md, related_work_md,
        lookup_registry, call_llm,
    )

    final_score = entailment_weight * entailment_component + pub_bias_weight * pub_bias_component

    return {
        "score": round(final_score, 4),
        "entailment_component": round(entailment_component, 4),
        "publication_bias_component": round(pub_bias_component, 4),
        "per_claim": per_claim,
    }
```

### 2.5 Notes on the scoring design

- **Weighting (0.7 / 0.3)**: entailment is claim-level and fires on every ARA regardless of genre;
  publication-bias is a single ARA-level signal. Weighting it lower prevents one registry check from
  dominating a score built from potentially many claims, while the `NONCLINICAL_FLOOR`/`0.0`-failure
  split ensures it still moves the needle meaningfully (0.3 of the total score) whenever it fires.
- **Why the type-mismatch branch caps at `0.15 * design_confidence` rather than 0**: a claim that
  overreaches its design still deserves a nonzero, low score if the *design itself* was executed
  cleanly (a well-run observational study over-narrated as causal is a worse outcome than a sloppy
  observational study, but not equally bad as a fabricated design) — this keeps the metric from
  being a single binary trapdoor, preserving graded signal for the tournament's aggregate scoring.
- **Why `evidence_fetch` is a required, non-LLM argument**: the independent-corroboration check must
  read the actual `evidence/tables|figures/*.md` bytes, not trust the LLM's memory of them — this is
  what makes Prompt C's `independently_corroborated`/`circular` flags checkable rather than
  self-reported, and is the concrete mechanism that prevents an ARA from gaming the check by writing
  confident-sounding but unverified `Evidence basis` prose.

## 3. Why this is hard to Goodhart, and how it composes

Because the entailment score is capped by the *weaker* of (a) the design-type ceiling (an ordinal,
LLM-adjudicated but structurally-anchored classification tied to `Setup`/`Procedure`, not to the
claim's own rhetoric) and (b) independent corroboration against fetched `evidence/` bytes, an ARA cannot
raise its score by writing more confident claims, more verbose `Evidence basis` prose, or more
cross-references — all three of those levers are exactly the ones a compiler under score-pressure would
reach for first, and all three are neutralized: confidence is ignored by Prompt B (which reads only the
design, not the claim), verbosity without an independently-corroborating quote is caught by Prompt C's
`circular` flag, and reference density is neutralized by taking the max (not sum) over cited
experiments per claim. The publication-bias check pulls its ground truth from a registry outside the
ARA's own text entirely, so it cannot be gamed from within the compiled artifact at all — the only way
to improve that sub-score is to actually register a genuinely registrable study and actually report
consistent outcomes, or to be a genre where no such registry exists (which the `NONCLINICAL_FLOOR`
still keeps below a clean pass). It composes with the rest of the suite as a strictly additional,
orthogonal axis: it does not re-score grounding-existence (Seal Level 1's job) or vocabulary/novelty
(concepts/related-work metrics' job); it isolates and scores *inferential validity of the claim given
its own cited evidence*, plus one external-registry check nothing else in the artifact stack reaches.
