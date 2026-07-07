# Verifier vs. Tournament Metrics — A Rigorous Comparison

**Question.** How does the existing ARA "verifier" (the ARA Seal review system) judge an ARA, and
to what extent do our tournament-winning good-science metrics *extend* that judgement — what were we
missing that the verifier already does, and how did they implement things versus how we did?

**Sources.**
- Verifier L2: `~/.claude/skills/rigor-reviewer/SKILL.md`,
  `~/.claude/skills/rigor-reviewer/references/review-dimensions.md`
- Verifier L1: `~/.claude/skills/compiler/references/validation-checklist.md`
- Ours: `research/metrics/v3/tournament/TOURNAMENT_SUMMARY.md` and the 11 per-artifact winners under
  `research/metrics/v3/tournament/<artifact>/improved/<WINNER>.md`

---

## 1. The verifier in brief

The ARA Seal is a **two-level review of a single ARA**. Its stance is auditing one artifact's
*internal epistemic integrity* — not scoring it against a library, not verifying it against the
outside world.

### Level 1 — deterministic structural gates (`validation-checklist.md`)

A pass/fail gate run before any semantic review. It is entirely mechanical and checks *presence,
shape, and cross-link consistency*, not quality:

- **Directory/file existence** — mandatory-core dirs (`logic/`, `logic/solution/`, `src/`, `trace/`,
  `evidence/`) and mandatory files (`PAPER.md`, `logic/claims.md`, …) exist and are non-empty.
- **Field-level regex checks** — e.g. `logic/claims.md` must have `## C\d+` blocks each carrying
  `**Statement**`, `**Sources**`, `**Status**`, `**Falsification criteria**`, `**Proof**`,
  `**Evidence basis**`, `**Interpretation**`; `experiments.md` ≥3 `## E\d+` blocks; `concepts.md`
  ≥5 `## ` sections; etc.
- **Count checks** (§5) — source-bounded *targets, not quotas* (Rule 14): honest thin content passes,
  fabricated filler fails.
- **Evidence quality** (§6) — every `evidence/tables/*.md` and `figures/*.md` has a `**Source**`, a
  sibling `.png` screenshot, a Markdown table (tables), and declared `Figure type` / `Extraction
  method` / `Reading confidence` (figures).
- **Exploration tree** (§8) — parses as YAML, has `tree` key, every node has `id`/`type`/
  `support_level`, type-specific required fields (`dead_end` needs `hypothesis`/`failure_mode`/
  `lesson`; `decision` needs `choice`/`alternatives`; `pivot` needs `from`/`to`/`trigger`).
- **Cross-layer binding** (§9) — every `E\d+` in a claim's `**Proof**` exists in `experiments.md`;
  every `C\d+` in an experiment's `**Verifies**` exists in `claims.md`; heuristic `Code ref` paths
  resolve; tree `evidence:` refs are claim IDs.
- **Citation verification** (§10) — every referenced `file:line` exists; each `**Sources**` entry's
  verbatim «quote» is present at the cited line and the asserted number matches the value inside the
  quote. This is the one L1 area that reaches *outside* the ARA to the provided repo/PDF.
- **Evidence-ledger completeness** (§11), **self-consistency** (§12) — declared counts match actual
  files; ARA-authored derived numbers recompute.

### Level 2 — semantic epistemic review (`SKILL.md`)

A single LLM reviewer that assumes L1 passed and does **not** re-check any structure. It reads the
whole ARA and scores six dimensions 1–5, each with strengths / weaknesses / suggestions:

| Dim | Name | Judges |
|-----|------|--------|
| **D1** | Evidence Relevance | Does cited evidence *substantively* support each claim (type-aware: causal→ablation, generalization→heterogeneous, improvement→baseline, descriptive→sampling, scoping→bounds)? |
| **D2** | Falsifiability Quality | Are falsification criteria actionable, non-trivial, scope-matched, independently testable? |
| **D3** | Scope Calibration | Do claims assert exactly what evidence supports (over/under-claiming, assumption explicitness, generalization boundaries, qualifier consistency)? |
| **D4** | Argument Coherence | Does the arc observations→gaps→insight→solution→claims→evidence hold, with every gap addressed and no cross-layer contradiction? |
| **D5** | Exploration Integrity | Are dead-ends specific, decisions genuinely deliberated, no claim advocating a rebutted branch, honest negatives? |
| **D6** | Methodological Rigor | Adequate baselines, ablations, statistical reporting, metric-claim alignment, reproducibility? |

**Procedure (7 steps).** (1) Read the ARA in a fixed order; (2) parse entities (claims, experiments,
heuristics, observations/gaps, tree nodes); (3) build working maps (`claim_proof_map`,
`experiment_verifies_map`, `claim_dependency_edges`, `gap_set`, `rejected_nodes`, `decision_nodes`);
(4) evaluate each dimension by semantic reasoning; (5) compile severity-ranked findings
(critical/major/minor/suggestion, each with verbatim `evidence_span`, observation, reasoning,
suggestion); (6) compute the overall grade as the **mean of the six scores** mapped to Strong Accept
/ Accept / Weak Accept / Weak Reject / Reject (with floor rules, e.g. any dimension =1 → Reject);
(7) write one `level2_report.json`.

**Stance.** L2 explicitly is *constructive, calibrated* (most competent ARAs land 3–4), *balanced*
(look for strengths), *artifact-only* (no code execution, no external fetch — "take the ARA's
reported evidence at face value"), and does *no* structural re-checks (L1 owns those). Its unit of
judgement is the **whole ARA collapsed into one grade**.

---

## 2. Side-by-side: verifier dimensions ↔ our per-artifact metrics

Our tournament produced 11 metric sets, one per ARA layer/artifact, each a bundle of computable
Python functions. The verifier's six L2 dimensions are cross-cutting semantic judgements. The map:

| Verifier L2 dimension | Our overlapping / extending metrics (artifact → metric) | Relationship |
|---|---|---|
| **D1 Evidence Relevance** (type-aware claim↔experiment entailment) | `05_experiments`: *Falsifiability Density* (outcome lexically tied to what `Metrics` measures), *Method–Measurement Internal Consistency*, *Triangulation / Verification Load* (claim corroborated by ≥2 textually distinct experiments); `02_claims`: *Grounding Fidelity & Numeric Coverage* | **Partial overlap, weaker.** We check that a claim *links to* experiments and that experiment vocabulary is internally consistent; the verifier judges whether the experiment *design actually entails the claim type*. Our checks are lexical; D1 is semantic. |
| **D2 Falsifiability Quality** (actionable, non-trivial, scope-matched, independent) | `02_claims`: *Falsifiability Operationalization & Boilerplate* (novel-number + comparator, cross-claim boilerplate penalty); `05_experiments`: *Falsifiability Density*; `01_paper_manifest`: *Claim Falsifiability & Precision Density* | **Strong overlap + extension.** This is our closest analog. We *operationalize* D2 into a deterministic score (does the criterion carry a checkable number/comparator not copied across claims). The verifier assesses "actionable" and "independently testable" semantically — we cannot test *independence*, they can. |
| **D3 Scope Calibration** (over/under-claim, assumption explicitness, boundaries) | `07_solution`: *Concrete-Referent Density*, *Assumption→Consequence Traceability*, *Assumption/Boundary Grounding Overlap*; `03_concepts`: *Boundary-Condition Substantiveness*; `02_claims`: *Grounded Evidence–Interpretation Separation* | **Partial overlap.** We measure whether assumptions/boundaries are *concrete and traced to consequences* — a real slice of D3's "assumption explicitness." We do **not** detect over-claiming (universal scope marker vs. narrow evidence) — that requires reading claim scope against evidence scope, which no single-file metric does. |
| **D4 Argument Coherence** (obs→gap→insight→solution→claims→evidence arc; gap coverage; cross-layer consistency) | `04_problem`: *Argument-Graph Connectivity* (Obs→Gap→Insight graph resolves, no orphans), *Insight Synthesis Specificity*; `03_concepts`: *Concept Graph Coherence*; `02_claims`: *Dependency Graph Integrity* | **Overlap only within-layer.** We check coherence *inside* `problem.md` (the O→G→Insight sub-graph) and *inside* `claims.md` (dependency DAG). The verifier checks coherence *across* layers (does the solution implement the insight, do claims cover the solution, is every gap addressed by a claim). We have **no whole-ARA arc check**. |
| **D5 Exploration Integrity** (dead-end specificity, decision deliberation, rebutted-branch consistency, honest negatives) | `08_exploration_tree`: *Grounded Failure Disclosure*, *Decision Deliberation Depth*, *Pivot Traceability & Consequence*, *Convergent Synthesis*, *Support-Level Calibration* | **Strong overlap + extension.** This is our single tightest mapping: our five tree metrics deterministically operationalize almost every D5 check (specific `failure_mode`/`lesson`, real rejected `alternatives`, pivot anchoring). The one D5 check we **lack**: *rebutted-branch consistency* — "no claim advocates a `dead_end`/`pivot` approach," which is cross-layer (tree ↔ claims) and rated `critical` by the verifier. |
| **D6 Methodological Rigor** (baselines, ablations, statistics, metric-claim alignment, reproducibility) | `05_experiments`: *Comparator Rigor & Diversity* (baselines named + typed internal/external), *Method–Measurement Internal Consistency*; `10_implementation`: *Environment Metadata Concreteness*, *Grounding-Tag & Citation Integrity*, *Capture Proportionality*; `11_dataset`: *Provenance & Size Specificity*, *Preprocessing Traceability* | **Overlap, differently sliced.** We check *baseline presence/typing* and *reproducibility metadata concreteness* (reproducibility signals ≈ D6's last check). We do **not** check *ablation coverage* (multi-component claim → isolating experiment) or *statistical reporting* (variance/CI/n-runs) or *metric-claim alignment* as such — these need cross-referencing claims to experiments. |

Two of our artifacts have **no D-dimension home** in the verifier: `06_related_work` (delta
concreteness, footprint tiering, type–narrative consistency) and `09_evidence` (sweep completeness,
extraction-method honesty, numeric reconciliation). These are things the verifier pushes down to **L1**
(evidence-ledger completeness §11, evidence quality §6, related-work `## RW\d+`/`Delta` field checks
§4) rather than judging semantically at L2. So our tournament produced *L2-flavored* metrics for
layers the verifier only touches *structurally* at L1.

---

## 3. Where our metrics EXTEND the judgement

Concrete additions our tournament makes that the verifier does not do:

1. **Per-artifact granularity instead of one collapsed grade.** The verifier emits a single mean over
   six dimensions; a strong claims layer and a weak evidence layer average into one number. Our 11
   metric sets score *each layer independently* (`01_paper_manifest` … `11_dataset`), so a weak
   `evidence/` layer is visible even when `claims.md` is excellent. This is finer diagnostic
   resolution than any single L2 grade.

2. **Computable / deterministic scoring vs. LLM-graded.** Every one of our winners is a pure Python
   function returning `[0,1]` (e.g. `02`'s `grounding_fidelity_score`, `08`'s
   `grounded_failure_disclosure_score`). They are reproducible, cheap, non-stochastic, and
   library-comparable — you can run all 11 over 1,000 ARAs and rank them. The verifier's D1–D6 are
   LLM reasoning: higher-ceiling but non-deterministic, un-reproducible run-to-run, and not directly
   comparable across a corpus.

3. **The penalize-don't-skip constraint.** Every tournament function treats a missing/thin/empty input
   as a *penalized outcome it computes to*, never an N/A it skips (e.g. `07`'s
   `concrete_referent_density` returns `0.0` when `constraints.md` is absent; `07`'s
   `data_quality_caveat_coverage` returns `0.2` for an *unconfirmed* scan via the `evidence_check_ran`
   attestation, refusing to reward an unverifiable "nothing to report" as a pass). The verifier can
   note an absence in a finding but has no formal rule that an absent artifact scores *worse than*
   a present-but-mediocre one — it simply reviews what's there.

4. **Explicit Goodhart analysis per metric.** Each winning metric ships a "Why it's hard to Goodhart"
   section and a cross-metric "Combination" argument showing how cheap exploits on one metric are
   punished by another (e.g. `02`'s inventing a novel falsification number helps M1 but tanks M2's
   grounding check; `08`'s padding dead-ends fails the well-formedness bar *and* the density bonus).
   The verifier has no adversarial/anti-gaming model at all — it trusts the ARA at face value.

5. **Quantitative structural checks the verifier states only qualitatively.** We turned qualitative
   D-checks into hard structural computations: `02`'s three-color-DFS cycle detection + free-riding +
   transitive-anchor-fragility on the dependency graph; `08`'s ancestor-aware cross-branch
   `also_depends_on` convergence detection; `04`'s orphan/dead-end detection on the O→G→Insight graph.
   The verifier reasons about coherence in prose; we compute it.

6. **The honest-absence-symmetry design.** Several winners explicitly score honest disclosure of a gap
   *equal to* a real value rather than punishing it (`01`'s Metric 6 scores `"Not specified in paper"`
   equal to a valid DOI; `11`'s all-open disclaimer credited near-full). This anti-incentive-to-lie
   design is more principled than the verifier's implicit handling.

7. **Coverage of layers the verifier under-judges at L2.** Our `06_related_work` and `09_evidence`
   metric sets bring L2-style quality signals (delta concreteness, extraction-method honesty, numeric
   reconciliation transparency) to layers the verifier only structurally gates at L1.

---

## 4. What WE were missing

The verifier does several things no tournament metric does. These are real gaps:

1. **Cross-layer / whole-ARA integration.** The verifier's defining move — D4 Argument Coherence —
   checks the *arc across layers*: gaps in `problem.md` → key insight → `solution/architecture.md` →
   `claims.md` → `evidence/`. Every one of our metrics is single-file by construction ("artifact-level,
   single-file, offline metrics" — TOURNAMENT_SUMMARY §1). We have no analog for "does the solution
   implement the insight" or "is every gap addressed by a claim." The judges repeatedly flagged that
   the highest-value next step (`02`+`09` cross-reference) requires "promoting several of these from
   single-file metrics to whole-ARA metrics" — i.e. exactly what the verifier already does.

2. **Rebutted-branch consistency (D5, `critical`).** The verifier flags "any claim that advocates an
   approach marked `dead_end` or `pivot` in the tree." This is a tree↔claims cross-check; our
   `08_exploration_tree` set operates only inside the tree and cannot see it.

3. **Over-claiming detection (D3).** "Statement uses universal scope while evidence covers narrow
   conditions" — the verifier reads a claim's scope against its evidence's scope. Our `03`/`07`
   boundary metrics check whether boundaries are *concrete*, never whether a claim *over-reaches* its
   evidence. Rated critical-if-extreme by the verifier; we have nothing.

4. **Type-aware evidence entailment (D1).** The verifier infers claim type from statement cues and
   requires the matching experiment design (causal→ablation, improvement→baseline, …). Our `05`
   metrics check comparator presence and lexical method-metric consistency but never reason about
   *what design a claim's logical type demands*.

5. **Ablation coverage, statistical reporting, metric-claim alignment (D6).** The verifier flags
   single-run results for quantitative claims, missing ablations for multi-component claims, and
   metrics that don't measure what the claim asserts. Our `05` set touches baselines and internal
   consistency but not ablations, variance/CI/n-runs, or true metric-claim alignment.

6. **The L1 deterministic gates as a prerequisite floor.** The verifier runs a whole deterministic
   layer *before* semantic review — existence, field regex, YAML validity, cross-link resolution,
   verbatim-quote-at-cited-line, evidence-ledger sweep, self-consistency recomputation. Our tournament
   assumes a parsed representation and never re-validates structure. In particular, L1 §10's
   *quote-present-at-cited-line + value-matches-quote* check reaches into the source repo/PDF — an
   external-verification step the entire tournament was found to lack (TOURNAMENT_SUMMARY §4: "every
   judge names the same missing ingredient — external verification").

7. **A single unified, calibrated verdict with severity-ranked findings.** The verifier produces one
   grade (Strong Accept … Reject) plus a sorted findings list each with verbatim evidence, reasoning,
   and a fix suggestion, and `questions_for_authors`. Our output is 11 independent `[0,1]` vectors
   with no roll-up, no accept/reject decision, and no per-finding located evidence spans. We measure;
   we do not adjudicate.

8. **Holistic epistemic-integrity judgement.** D4/D5 together ask "do all layers tell the *same
   story*." No token/regex metric can catch a coherent-but-contradictory narrative across files. The
   verifier's LLM can.

---

## 5. Implementation contrast: how they built it vs. how we built it

| Aspect | Verifier (ARA Seal) | Tournament (ours) |
|---|---|---|
| **Producer** | One LLM reviewer, given the whole ARA directory | 4 *blind* proposer agents per artifact → judge picks 2 finalists → both revise against a stage-1 critique → judge picks 1 winner (2-stage tournament × 11 artifacts) |
| **Unit of analysis** | Whole ARA, all layers at once | One layer/file per metric set, in a clean-room (proposers didn't see each other) |
| **What runs** | LLM semantic reasoning over parsed entities + working maps | Deterministic Python functions returning `[0,1]` |
| **Structure** | L1 deterministic gate (pass/fail) → L2 six dimensions scored 1–5 | 11 independent metric bundles, 4–6 metrics each, no gate |
| **Scoring** | Per-dimension qualitative anchors → mean → grade band | Per-metric computable score, penalize-don't-skip, explicit Goodhart/Combination argument |
| **Output** | One `level2_report.json`: grade, per-dim strengths/weaknesses/suggestions, severity-ranked findings with verbatim `evidence_span`, `questions_for_authors` | 11 metric specs (code + rationale); a `TOURNAMENT_SUMMARY.md` synthesis; no per-ARA verdict |
| **External reach** | L1 §10 checks quotes/values against the real source repo/PDF; L2 is artifact-only | None — every metric reads one Markdown/YAML file offline |
| **Orchestration** | Single-pass, single agent | Resumable multi-agent orchestration (`status.py`, `TOURNAMENT_LOG.md`), blind proposers, adversarial critique rounds |

**What each buys and costs.** The verifier's single-LLM whole-ARA approach *buys* semantic reach
(type-aware entailment, cross-layer coherence, over-claim detection) and a decision (a grade, ranked
findings) — and *costs* determinism, reproducibility, corpus-comparability, and any anti-gaming
guarantee (it trusts the text). Our blind-tournament clean-room approach *buys* reproducible,
cheap, library-comparable, Goodhart-hardened per-layer scores with an explicit penalize-unavailability
discipline — and *costs* everything cross-layer and everything requiring reasoning or external ground
truth. The tournament's own judges converged, independently across all 11 artifacts, on the same
ceiling: our metrics measure "what the compiler wrote about the paper, not whether the paper's science
is true" (TOURNAMENT_SUMMARY §1) — precisely the semantic/external gap the verifier's L2 and L1 §10
are built to close.

---

## 6. Bottom line

**Verdict: complementary, with genuine extension on two of six dimensions.** Our metrics are neither a
full reinvention of the verifier nor merely redundant with it. They are a **deterministic,
per-layer, Goodhart-hardened operationalization** of a *subset* of the verifier's judgement —
strongest exactly where a check reduces to computable structure over one file:

- **Genuine extension (we do it better/harder than the verifier):** D2 Falsifiability and D5
  Exploration Integrity. Our `02`/`05` falsifiability metrics and our five `08` tree metrics turn
  qualitative D2/D5 anchors into reproducible, gaming-resistant scores the verifier can only judge by
  hand. We also *extend coverage* to `06_related_work` and `09_evidence`, which the verifier gates
  only structurally at L1.
- **Complementary (only the verifier does it):** D1 type-aware entailment, D3 over-claiming, D4
  whole-ARA argument arc, D6 ablation/statistics/metric-alignment, the rebutted-branch cross-check,
  the L1 deterministic gates, and any external verification of quotes/values against the source.

**Single highest-value merge:** slot our 11 computable metric sets *under the verifier's L2 dimensions
as deterministic sub-scores* — a hybrid where L1 gates structure, our functions produce reproducible
per-dimension evidence (D2 ← `02`/`05` falsifiability; D5 ← `08`'s five tree metrics; D3 ← `07`'s
assumption metrics; D6 ← `05`/`10`/`11`), and the LLM reviewer spends its judgement budget only on the
cross-layer / semantic / external-verification checks that no single-file function can compute (D4,
over-claiming, type-aware entailment, rebutted-branch consistency). That grounds the verifier's
soft grades in hard sub-scores while reserving the LLM for exactly the gaps the tournament proved it
cannot close.
