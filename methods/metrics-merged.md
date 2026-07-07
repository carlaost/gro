# All Possible Metrics — Merged Reference

This document merges the metric-design source documents into one place, so we have a single
list of **every metric, check, indicator draft, and measurable surface** the ARA program has produced
or catalogued:

1. **`DATA_SHAPES.md`** — the *measurement surfaces*: every artifact the ARA compiler emits, its
   field-level shape, and — critically — what "absent" or "thin" looks like for each (thinness/absence
   is itself a scoreable signal, not a skip). It also now carries Carla's per-artifact **Indicators**
   blocks (the rough drafts of what each shape *affords* — see Part E).
2. **`VERIFIER_COMPARISON.md`** — the *existing verifier* (ARA Seal): its L1 deterministic gates and
   L2 six semantic dimensions, plus how our tournament metrics map onto them.
3. **`TOURNAMENT_SUMMARY.md`** — the round-1 *tournament winners*: 11 per-artifact metric sets (≈55
   concrete computable metrics) that won a blind, adversarial, two-stage tournament, each with its
   judge's qualification.
4. **`tournament2/METRICS_CANDIDATES.md`** — the *rough indicator metric drafts*: Carla's per-artifact
   indicator blocks harvested into **64 candidate metrics (M01–M64)**, then pruned/merged/ranked into
   23 survivors, a top-10, and a net-new "MISSING" list. This is the "what the artifacts afford" layer
   (Part E) — the widest inventory of *possible* metrics, most of which reach beyond what round-1 or
   the verifier do.

Read this as four layers of the same question — **what can be measured on a compiled research
artifact, what each shape affords as an indicator, what the verifier already measures, and what our
tournament produced** — followed by the cross-cutting synthesis (overlaps, extensions, gaps).

> **Note on the two tournaments.** Round-1 (Part C) built metrics *blind to what already existed* and
> converged on honest-but-limited, offline, single-file proxies. Carla's indicator drafts (Part E)
> then deliberately push into the territory round-1 avoided — external literature, novelty, cross-layer
> and cross-source verification — and are the seed pool for a round-2 *per-metric* tournament. Part E is
> therefore the most forward-looking section: the possibilities, not yet the built set.

---

# PART A — Measurement surfaces (from `DATA_SHAPES.md`)

The 11 artifact types the compiler emits into `research/ara-library/{id}/`. Each is a surface a metric
can score; for each, the "thinness / absence" column is what a penalizing metric must catch rather
than skip.

| # | Artifact | Path | Mandatory core? | What can be measured / what "thin or absent" looks like |
|---|----------|------|-----------------|----------------------------------------------------------|
| 1 | Root manifest | `PAPER.md` | Yes | Frontmatter completeness; `claims_summary` count vs. `claims.md`; Layer-Index self-consistency. **Thin:** abstract-only source → sparse `claims_summary`, thin Layer Index; frontmatter/index count mismatch is a defect. |
| 2 | Claims | `logic/claims.md` | Yes | Presence of all 8 fields per `C##`; grounded `Sources` (value ∈ verbatim «quote»); falsifiability criteria; dependency chains. **Thin:** bare source paths with no quote (auto-fail); `Interpretation` collapsing into `Evidence basis`; abstract-only → few claims, weak evidence basis. |
| 3 | Concepts | `logic/concepts.md` | Yes | ≥5 genuine terms; substantive boundary conditions; non-circular distinct definitions; notation↔prose agreement. **Thin:** `Boundary conditions: Not specified` on most entries; padded borrowed/textbook terms. |
| 4 | Problem statement | `logic/problem.md` | Yes | Observation→Gap→Insight graph resolves (no orphans); section-anchored citations; concrete `Why they fail`; concrete assumptions. **Thin:** `Evidence: Abstract` on every O; Key Insight that just restates the method name; generic "prior work is limited". |
| 5 | Experiments (analysis plans) | `logic/experiments.md` | Yes | ≥3 `E##` blocks; directional-only `Expected outcome` (NO exact numbers); named+typed baselines; metric↔setup vocabulary consistency; valid dependency DAG. **Thin:** exact number leaking into `Expected outcome` (defect); dangling `Proof`/`Verifies` refs; abstract-only → generic interchangeable procedures. |
| 6 | Related work (typed dependency graph) | `logic/related_work.md` | Yes | Full `RW##` blocks with concrete `Delta`; typed edges (imports/bounds/baseline/extends/refutes); both full + brief citation tiers. **Thin:** only full blocks, no brief tier (didn't sweep References); abstract-only → 1–3 blocks, no brief tier. |
| 7 | Solution / method layer | `logic/solution/constraints.md` + warranted method files | `constraints.md` yes | Concrete boundary/assumption referents; data-quality caveats surfaced (not laundered); method-file names match genre; assumption→consequence traceability; heuristics captured when the paper states tricks. **Thin:** "no limitations stated" (red flag); wrong-genre method files; missing caveat when evidence numbers don't reconcile. |
| 8 | Exploration tree (research DAG) | `trace/exploration_tree.yaml` | Yes | Valid YAML with node type-specific fields; specific `dead_end` failure_mode/lesson; deliberated `decision` alternatives; anchored `pivot`; `also_depends_on` convergence; support-level calibration. **Thin:** zero dead_ends/decisions on an iterative-genre paper; `explicit` node with no `source_refs`; abstract-only → one question node. |
| 9 | Evidence (index + tables + figures) | `evidence/README.md`, `tables/*.md`, `figures/*.md` (+ `.png`) | Yes | Complete sweep (every numbered Table/Figure filed or accounted for with a reason); extraction-method honesty (`exact_from_labels` vs `digitized_estimate ≈`); type-body conformance; numeric reconciliation; claim-grounding links. **Thin:** silently filed only some objects (auto-fail); estimate mislabeled as exact; abstract-only → near-zero evidence (near-total grounding loss). |
| 10 | Implementation / reproduction layer | `src/environment.md` (+ `artifacts.md`, `configs/*.md`, `execution/*`) | `environment.md` yes | Environment metadata concreteness; grounding tags (`transcribed`/`reconstructed`); capture proportionality vs. what the repo claims exists; config rationale↔sensitivity; artifact→claim traceability. **Thin:** provided repo's real code reduced to a pointer (fail); fabricated stub from prose-only method (fail); missing/wrong grounding tag. |
| 11 | Dataset descriptors | `data/dataset.md` (+ `preprocessing.md`) | As warranted (data work only) | Access-tier honesty (open vs. controlled, not blanket "available"); provenance/size specificity (real accessions, dims, instruments); internal count self-audit; genre-scope fidelity (generation claim ⇒ real accession); ethics/consent; preprocessing traceability. **Thin:** blanket "available"; secondary-reuse fabricating raw-QC language; abstract-only → sample size only, no accession. |

**Governing principle across all 11:** everything not in "mandatory core" is emitted *only when the
source actually contains it*. Forcing an artifact in where the genre doesn't warrant it (a `.py` stub
for a meta-analysis, an `architecture.md` for a statistical review) is a **fabrication defect**;
omitting one the source clearly warrants (a provided repo's code) is a **coverage failure**. Both are
scoreable.

---

# PART B — The Verifier / ARA Seal (from `VERIFIER_COMPARISON.md`)

The ARA Seal is a two-level review of a **single** ARA's internal epistemic integrity (not scored
against a library, not verified against the outside world except at L1 §10).

## B.1 Level 1 — deterministic structural gates (pass/fail, mechanical)

| Check | What it verifies |
|-------|------------------|
| Directory/file existence | Mandatory-core dirs/files exist and are non-empty. |
| Field-level regex | e.g. each `## C\d+` carries Statement/Sources/Status/Falsification/Proof/Evidence basis/Interpretation; `experiments.md` ≥3 `E##`; `concepts.md` ≥5 sections. |
| Count checks (§5) | Source-bounded *targets, not quotas* — honest thin content passes, fabricated filler fails. |
| Evidence quality (§6) | Every table/figure has `Source`, a sibling `.png`, a markdown table (tables), and declared `Figure type`/`Extraction method`/`Reading confidence` (figures). |
| Exploration tree (§8) | Parses as YAML; `tree` key; every node has `id`/`type`/`support_level` + type-specific required fields. |
| Cross-layer binding (§9) | Every `E##` in a claim's `Proof` exists in `experiments.md`; every `C##` in an experiment's `Verifies` exists in `claims.md`; heuristic `Code ref` paths resolve; tree `evidence:` refs are claim IDs. |
| **Citation verification (§10)** | Every referenced `file:line` exists; each `Sources` «quote» is present at the cited line and the number matches the value inside the quote. **The one L1 check that reaches outside the ARA into the provided repo/PDF.** |
| Evidence-ledger completeness (§11) | Declared counts match actual files. |
| Self-consistency (§12) | ARA-authored derived numbers recompute. |

## B.2 Level 2 — semantic epistemic review (LLM, scored 1–5 per dimension)

| Dim | Name | Judges |
|-----|------|--------|
| **D1** | Evidence Relevance | Does cited evidence *substantively* support each claim, **type-aware** (causal→ablation, generalization→heterogeneous, improvement→baseline, descriptive→sampling, scoping→bounds)? |
| **D2** | Falsifiability Quality | Are falsification criteria actionable, non-trivial, scope-matched, independently testable? |
| **D3** | Scope Calibration | Do claims assert exactly what evidence supports (over/under-claiming, assumption explicitness, generalization boundaries, qualifier consistency)? |
| **D4** | Argument Coherence | Does the arc observations→gaps→insight→solution→claims→evidence hold, every gap addressed, no cross-layer contradiction? |
| **D5** | Exploration Integrity | Dead-ends specific, decisions genuinely deliberated, no claim advocating a rebutted branch, honest negatives? |
| **D6** | Methodological Rigor | Adequate baselines, ablations, statistical reporting, metric-claim alignment, reproducibility? |

**Output:** one `level2_report.json` — grade (Strong Accept … Reject, mean of six with floor rules),
per-dimension strengths/weaknesses/suggestions, severity-ranked findings with verbatim
`evidence_span`, `questions_for_authors`. **Stance:** constructive, calibrated (most competent ARAs
land 3–4), artifact-only at L2, no structural re-checks (L1 owns those).

---

# PART C — The Tournament metrics (from `TOURNAMENT_SUMMARY.md`)

11 artifacts × a 2-stage blind tournament (4 proposers → 2 finalists → revise vs. critique → 1
winner). Every winning metric is a pure Python function returning `[0,1]`, penalize-don't-skip, with
an explicit Goodhart argument. **~55 concrete metrics total.** Each set's judge verdict was the same:
*honest-but-limited proxy — measures compilation quality, not scientific truth.*

### 01. `paper_manifest` (`PAPER.md`) — Winner A
1. Frontmatter/Body Self-Consistency
2. Claim Falsifiability & Precision Density
3. Epistemic Transparency of Absence
4. Domain–Claim Lexical Grounding (IDF-weighted)
5. Layer-Index Evidentiary Density per Claim
6. Identifier & Bibliographic Integrity (honest `"Not specified"` scored equal to a valid ID)
> *Verdict:* manifest-integrity + disclosure-honesty proxy; four of six are hygiene checks. Does not clear "measures good science."

### 02. `claims` (`logic/claims.md`) — Winner B
1. Falsifiability Operationalization & Boilerplate Score
2. Grounding Fidelity & Numeric Coverage Score
3. Grounded Evidence–Interpretation Separation Score
4. Dependency Graph Integrity Score (acyclic, non-free-riding, non-flat DAG)
5. Evidentiary Concentration & Transitive Anchor Fragility Score
6. Status–Documentation Calibration Score (selective-reporting detector)
> *Verdict:* measures rigor, not scientific truth. Grounding verifies `value ∈ quote`, not `quote ∈ real source`.

### 03. `concepts` (`logic/concepts.md`) — Winner A
1. Boundary-Condition Substantiveness (BCS)
2. Concept Graph Coherence (CGC)
3. Definition Distinctiveness & Grounding (DDG)
4. Notation–Prose Extraction Fidelity (NPEF)
> *Verdict:* honest extraction-quality proxy; catches shallow extraction, which correlates with but ≠ shallow science.

### 04. `problem` (`logic/problem.md`) — Winner A
1. Evidential Grounding Depth
2. Argument-Graph Connectivity (O→G→Insight resolves, no orphans)
3. Insight Synthesis Specificity (anti-restatement)
4. Gap Failure-Mode Specificity
5. Assumption Risk Exposure
> *Verdict:* honest compile-quality proxy; only internal id-references validated, nothing checks citations against a real bibliography.

### 05. `experiments` (`logic/experiments.md`) — Winner B
1. Falsifiability Density
2. Comparator Rigor & Diversity (baselines named + typed internal/external)
3. Method–Measurement Internal Consistency
4. Triangulation / Verification Load (claims-bound, ≥2 textually distinct experiments)
5. Structural Integrity & Anti-Padding (DAG + cross-block similarity)
> *Verdict:* structural rigor, ultimately lexical; no contact with `evidence/` or ground truth.

### 06. `related_work` (`logic/related_work.md`) — Winner A
1. Delta Concreteness Score
2. Provenance-Grounding Score
3. Claims-Linkage Grounding Ratio (substantiation gate + template-duplication penalty)
4. Footprint Tiering Completeness (full + brief tiers)
5. Type–Narrative Consistency
> *Verdict:* measures compilation craft; DOIs unverified (well-formed but fabricated passes).

### 07. `solution` (method layer) — Winner A
1. Concrete-Referent Density
2. Data-Quality-Caveat Coverage (with "scan-actually-ran" attestation)
3. Method-Genre Coherence & Heuristics-Omission Audit
4. Assumption/Boundary Grounding Overlap (IDF-weighted)
5. Assumption→Consequence Traceability
> *Verdict:* **top of the honest-but-limited band** — Assumption→Consequence is the deepest science signal in the pool (examines failure modes, not just presence).

### 08. `exploration_tree` (`trace/exploration_tree.yaml`) — Winner A
1. Grounded Failure Disclosure Score (two-signal genre floor softener)
2. Convergent Synthesis Score (real cross-branch `also_depends_on` + topical coherence)
3. Decision Deliberation Depth
4. Pivot Traceability & Consequence
5. Support-Level Calibration
> *Verdict:* honest disclosure-integrity proxy, **leaning strong**; Convergent Synthesis is a structural analog of independent corroboration.

### 09. `evidence` (`evidence/`) — Winner A
1. Sweep Completeness
2. Extraction-Method Honesty (`exact_from_labels` vs `digitized_estimate ≈`)
3. Type-Body Structural Conformance
4. Claims-Grounding Coverage
5. Numeric Reconciliation Transparency
> *Verdict:* honest hygiene on 4/5 axes; #4 (claims-grounding) is the most Goodhartable (uniform rubber-stamping → 1.0). **Most externally-checkable pair: #1 + #5.**

### 10. `implementation` (`src/`) — Winner B
1. Capture Proportionality
2. Grounding-Tag & Citation Integrity (`transcribed`/`reconstructed` + real citation or honest stub)
3. Configuration Rationale–Sensitivity Calibration
4. Environment Metadata Concreteness & Transparency
5. Claim-Traceability of Captured Artifacts
> *Verdict:* reproducibility-reporting hygiene; proxy for good record-keeping, not good science.

### 11. `dataset` (`data/dataset.md` + `preprocessing.md`) — Winner A
1. Access-Tier Honesty
2. Provenance & Size Specificity
3. Internal Discrepancy Self-Audit
4. **Genre-Scope Fidelity** (generation claim ⇒ verifiable accession) — *single most Goodhart-resistant metric in the tournament*
5. Ethics/Consent Coverage Conditioned on Data Genre
6. Preprocessing Traceability Proportional to Raw-Data Claims
> *Verdict:* honest provenance-documentation proxy, not validity.

---

# PART D — Cross-cutting synthesis (verifier ↔ tournament)

## D.1 How the tournament metrics map onto the verifier's L2 dimensions

| Verifier L2 dimension | Overlapping tournament metrics | Relationship |
|---|---|---|
| **D1 Evidence Relevance** | `05` Falsifiability Density / Method–Measurement Consistency / Triangulation; `02` Grounding Fidelity | Partial, weaker — ours is lexical, D1 is semantic type-aware entailment. |
| **D2 Falsifiability Quality** | `02` Falsifiability Operationalization; `05` Falsifiability Density; `01` Claim Falsifiability | **Strong overlap + extension** — we operationalize D2 into deterministic scores. |
| **D3 Scope Calibration** | `07` Concrete-Referent / Assumption→Consequence / Grounding Overlap; `03` BCS; `02` Evidence–Interpretation Separation | Partial — we measure assumption concreteness, **not over-claiming**. |
| **D4 Argument Coherence** | `04` Argument-Graph Connectivity / Insight Specificity; `03` CGC; `02` Dependency Graph Integrity | Within-layer only — **no whole-ARA arc check**. |
| **D5 Exploration Integrity** | all five `08` tree metrics | **Strong overlap + extension** — tightest mapping; lacks only rebutted-branch consistency (tree↔claims). |
| **D6 Methodological Rigor** | `05` Comparator Rigor; `10` Environment/Grounding/Capture; `11` Provenance/Preprocessing | Overlap, differently sliced — **no ablation coverage / statistical reporting / metric-claim alignment**. |

`06_related_work` and `09_evidence` have **no L2 home** — the verifier only gates them structurally at
L1, so our tournament produced *L2-flavored* metrics for layers the verifier judges only structurally.

## D.2 Where the tournament EXTENDS the verifier
1. Per-artifact granularity (11 independent scores) vs. one collapsed grade.
2. Computable/deterministic `[0,1]` vs. LLM-graded (reproducible, cheap, corpus-comparable).
3. Penalize-don't-skip discipline (absent artifact scores *worse than* present-but-mediocre).
4. Explicit per-metric Goodhart analysis + cross-metric combination defenses.
5. Quantitative structural checks the verifier states only qualitatively (cycle detection, convergence detection, orphan detection).
6. Honest-absence-symmetry design (honest "Not specified" scored equal to a real value).
7. Coverage of layers the verifier under-judges at L2 (`06`, `09`).

## D.3 What the tournament is MISSING (the verifier does these; we don't)
1. **Cross-layer / whole-ARA integration** (D4 arc: gap→insight→solution→claim→evidence).
2. **Rebutted-branch consistency** (D5, critical — tree↔claims cross-check).
3. **Over-claiming detection** (D3 — universal scope vs. narrow evidence).
4. **Type-aware evidence entailment** (D1 — claim type dictates required experiment design).
5. **Ablation coverage / statistical reporting / metric-claim alignment** (D6).
6. **L1 deterministic gates as a prerequisite floor** — incl. §10 quote-at-cited-line *external* check into the source repo/PDF.
7. **A single unified, calibrated verdict** with severity-ranked located findings.
8. **Holistic epistemic-integrity judgement** — "do all layers tell the same story."

## D.4 The one finding every judge reached independently
All 11 winners are **honest-but-limited proxies**. Every metric operates on regex/lexical/structural
signals over the ARA's **own text** — none resolves an external fact (no DOI fetch, no live-registry
check, no source-PDF verification, no truth check). By construction, a *well-compiled record of bad
science* and a *well-compiled record of good science* are **indistinguishable** to every metric in the
pool. The recurring exploits are the same across all 11: length-as-quality, boilerplate/templated
padding, fabricated-but-internally-consistent content, honest-absence-vs-fabrication asymmetry, and
genre/thinness false positives.

## D.5 The four most promising metrics to actually build (with the external step each needs)
1. **`09` Sweep Completeness + Numeric Reconciliation** — add a screenshot-vs-transcription OCR/vision spot check → converts "internally consistent" to "verified against source."
2. **`11` Genre-Scope Fidelity** — replace the accession format-regex with a live registry lookup (GEO/SRA/dbGaP/PROSPERO) → "looks like a real ID" becomes "is a real ID."
3. **`07` Assumption→Consequence Traceability** — add an LLM-judge semantic match (consequence actually describes a failure mode of *that* assumption).
4. **`02` Grounding Fidelity + `09` cross-referenced** — promote from single-file to whole-ARA (claims' quotes checked against `evidence/`'s filed tables, not just `claims.md`'s own prose).

**General prerequisite named by every judge:** *external verification* — a live registry, the source
PDF/screenshot, a cross-artifact claim ledger, or a calibration set of human-labeled strong/weak ARAs.
Until that exists, the whole tournament is a **compilation-honesty and internal-coherence detector**,
not a measure of whether the science is good.

---

# PART E — Candidate indicator metrics: what the artifacts afford (from Carla's `Indicators` blocks → `tournament2/METRICS_CANDIDATES.md`)

This is the layer Parts A–D do not contain: not what the compiler *emits* (A), nor what the verifier /
round-1 tournament already *score* (B/C/D), but what each artifact shape **affords as a good-science
indicator** — Carla's rough per-artifact `Indicators` drafts, harvested and organized. Many of these
deliberately require an external tool (`[ext]`) or semantic judgement (`[sem]`) — i.e. they aim past
the offline/single-file ceiling round-1 hit.

## E.1 Full extraction — 64 candidate metrics (M01–M64), by artifact

| M-id | Name | Artifact | Intent |
|---|---|---|---|
| M01 | Metadata comprehensiveness | §1 PAPER.md | Basics present + a persistent id (DOI/accession) |
| M02 | Artifact comprehensiveness / article-type inference | §1 PAPER.md | Which layers exist, and what that implies about paper genre |
| M03 | Claim comprehensiveness (subfields/falsifiability/status) | §2 claims | All claim subfields filled, falsifiable, status set |
| M04 | Claims ↔ results matching (+ publication-bias) | §2 claims | Do claims match reported results; cross-check a connected clinical trial reporting different results |
| M05 | Abstract-only relevance discount | §2 claims | Down-weight relevance when source is abstract-only |
| M06 | References & anchor claims (dependencies) | §2 claims | Dependency chains resolve; anchor claims identified |
| M07 | Claim novelty | §2 claims | Are the claims new vs prior literature |
| M08 | Claim contradictions | §2 claims | Internal (claim↔claim) and external contradictions |
| M09 | FOL-ability (Oshima principles) | §2 claims | Can a first-order-logic graph be drawn cleanly over the claims |
| M10 | Controlled-vocabulary referenceability | §2 claims | Uses translatable, anchorable (ontology-mappable) terms |
| M11 | Context & content novelty (Evans) | §3 concepts | Novelty of concept space in Evans sense |
| M12 | Anchoredness (latent layer / canonical dataset) | §3 concepts | Is there a latent layer / canonical dataset referenced |
| M13 | Internal consistency: claims ↔ concepts | §3 concepts | Concepts cover/agree with the vocabulary claims use |
| M14 | Reference-landscape comprehensiveness | §4 problem | Cites full relevant landscape (island / k-NN ~500 / undermind) incl. contradicting claims |
| M15 | Gap ↔ claims match | §4 problem | Do stated gaps line up with what claims resolve |
| M16 | Gap truthfulness vs literature | §4 problem | Existing-attempts completeness + why-they-fail accuracy vs real lit |
| M17 | Insight novelty & relevance (+ impact) | §4 problem | Done before? societal/science impact if solved [sem] |
| M18 | Reference truthfulness / claim drift | §4 problem | Cited sources actually say what they're cited for |
| M19 | Experiment ↔ claim alignment | §5 experiments | Experiments actually test the claims they verify [sem] |
| M20 | Comprehensiveness of reporting (benchmark) | §5 experiments | Reporting completeness, briefly benchmarked |
| M21 | Experiments account for existing efforts & gap | §5 experiments | Design reflects prior efforts + gap analysis |
| M22 | Reference reasonability | §5 experiments | Are cited comparators/refs reasonable |
| M23 | Claim drift | §6 related_work | Same as M18 at the related-work layer |
| M24 | Gap size / novelty | §6 related_work | Magnitude/novelty of the delta over prior work |
| M25 | Replication bonus points | §6 related_work | Credit for replicating/confirming prior work |
| M26 | Dependency-graph comprehensiveness | §6 related_work | Citation dependency graph is complete |
| M27 | Method improvement | §6 related_work | Does the work improve on the cited method |
| M28 | Conditionality / generalizability | §7 constraints | How far do results generalize |
| M29 | Validity given claim ↔ experiment gaps/match | §7 constraints | Constraint validity in light of claim/experiment fit |
| M30 | Assumption realism, validity & fairness | §7 constraints | Dreamcase vs real-world assumptions |
| M31 | Limitation validity | §7 constraints | Do limitations add real new conditions on the hypotheses |
| M32 | Method validity | §7 method | Is the method sound |
| M33 | Method → constraint reasonability | §7 method | Do method choices justify the stated constraints |
| M34 | Method novelty | §7 method | Is the method new |
| M35 | Method verification status | §7 method | Widely-accepted method vs over-generalized/unjustified one |
| M36 | Combination of perspectives | §7 method | Multi-lens (e.g. wet-lab × computational) vs single, reflected in constraints |
| M37 | Heuristics reflect constraints | §7 heuristics | Are heuristics consistent with the constraints |
| M38 | Heuristics presence | §7 heuristics | There is always some abstraction — is it captured |
| M39 | Heuristics distance from optimum | §7 heuristics | How far the heuristic sits from the optimum |
| M40 | Started from a logical place | §8 tree | Did the DAG start where the literature left off |
| M41 | Abandoned paths reasoned & explained | §8 tree | Dead-ends are reasoned about, not bare |
| M42 | Abandoned-path pothole sufficiency | §8 tree | Enough context to let others avoid the pothole |
| M43 | DAG validly structured | §8 tree | Is the DAG structurally valid |
| M44 | Tree comprehensiveness (vs clinical-trial report) | §8 tree | Coverage, esp. when a clinical-trial report is available |
| M45 | Tree includes claim references | §8 tree | Tree evidence refs match the claim references |
| M46 | Misses search-bot-relevant references | §8 tree | Penalize omitting abandoned paths a search bot deems discoverable |
| M47 | Hypothesis failure-mode coverage | §8 tree | Substantial coverage of a hypothesis's failure modes |
| M48 | E2E reproducibility (fig+data+code) | §9 evidence | Evidence bundles figure + data + code for end-to-end reproduction |
| M49 | Evidence ↔ claim match | §9 evidence | Evidence substantiates the claims [sem] |
| M50 | Evidence ↔ constraints | §9 evidence | Evidence consistent with stated constraints |
| M51 | Evidence ↔ method | §9 evidence | Evidence consistent with the method |
| M52 | Reproduction value | §9 evidence | Confirms existing hypotheses (replication) vs new perspective |
| M53 | Re-use | §10 src | Are components re-used |
| M54 | FAIR | §10 src | Findable/Accessible/Interoperable/Reusable compliance |
| M55 | Reproducibility | §10 src | Reproducibility of the implementation layer |
| M56 | Added value / novelty / field expansion | §10 src | Does the code/artifact expand the field |
| M57 | Env ↔ evidence/method/constraints match | §10 src | Environment consistent with the other layers |
| M58 | Re-use | §11 data | Are datasets re-used |
| M59 | FAIR | §11 data | Dataset FAIR compliance |
| M60 | Reproducibility | §11 data | Reproducibility from the data layer |
| M61 | Added value / novelty / field expansion | §11 data | Does the dataset expand the field |
| M62 | Data ↔ evidence/method/constraints match | §11 data | Dataset consistent with the other layers |
| M63 | Data homogeneity & standard adherence | §11 data | Homogeneity + adherence to data standards |
| M64 | Referencing controlled vocabs / latent spaces | §11 data | Data references existing controlled vocabularies / latent spaces |

## E.2 Ranked survivors (after prune + merge)

Ranked by: (i) net-new vs verifier, (ii) tighter than verifier where overlapping, (iii) down-weighted
if a pure re-implementation of a round-1 winner or a verifier gate. `[ext]` = needs an external tool;
`[sem]` = needs LLM semantic judgement.

| Rank | Survivor | Name | Constituents | vs round-1 / verifier | Needs |
|---|---|---|---|---|---|
| 1 | S1 (M14) | Reference-landscape completeness | M14,M16,M21,M22,M26,M40,M46 | **strictly net-new** (neither reaches external lit) | [ext] |
| 2 | S2 (M17) | Novelty vs literature | M07,M11,M17,M24,M34 | net-new ("done before?" out of scope for both) | [ext][sem] |
| 3 | S3 (M18) | Claim drift / reference truthfulness | M18,M23 | tighter than L1 §10 (source-supports-it, not self-quote) | [ext][sem] |
| 4 | S4 (M19) | Claim↔Experiment↔Evidence entailment (+ publication-bias) | M04,M13,M15,M19,M29,M49 | = verifier D1, beyond round-1; trial-registry bias check beats both | [sem][ext] |
| 5 | S5 (M48) | End-to-end reproducibility bundle (fig+data+code) | M48,M55,M60 | tighter than D6 (tri-layer, cross-layer) | cross-layer |
| 6 | S6 (M36) | Multi-perspective triangulation | M36 | net-new (absent from both) | [sem] |
| 7 | S7 (M30) | Assumption realism & limitation validity | M28,M30,M31 | tighter than round-1 07 + verifier D3 (realism, not just concreteness/explicitness) | [sem] |
| 8 | S8 (M32) | Method validity & verification status | M32,M33,M35 | tighter facet of verifier D6 | [sem] |
| 9 | S9 (M64) | Controlled-vocabulary & latent-space anchoring | M10,M12,M64 | net-new interoperability signal | [ext] |
| 10 | S10 (M09) | FOL-ability (Oshima) | M09 | net-new formal-checkability signal | [ext]/[sem] |
| 11 | S11 (M08) | Claim contradictions | M08 | broader than D4 (claim↔claim + external) | [sem][ext] |
| 12 | S12 (M42) | Abandoned-path pothole sufficiency | M42 | richer than round-1 08 / D5 (reusable-to-prevent-repeat) | [sem] |
| 13 | S13 (M47) | Hypothesis failure-mode coverage | M47 | completeness axis beyond disclosure | [sem] |
| 14 | S14 (M44) | Tree comprehensiveness vs clinical-trial report | M44 | net-new (external registry) | [ext] |
| 15 | S15 (M53) | Reuse & FAIR-ness | M53,M54,M58,M59 | FAIR-as-standard net-new | [ext] |
| 16 | S16 (M56) | Added value / field expansion | M56,M61 | net-new (overlaps S2 novelty) | [ext][sem] |
| 17 | S17 (M25) | Replication vs novel-perspective value | M25,M52 | net-new | [sem][ext] |
| 18 | S18 (M50) | Resource↔spec grounding | M50,M51,M57,M62 | = verifier D4 territory, structural | [sem] |
| 19 | S19 (M37) | Heuristics adequacy | M37,M38,M39 | presence is round-1; distance-from-optimum net-new | [sem] |
| 20 | S20 (M20) | Reporting comprehensiveness / benchmark | M20 | overlaps round-1 05 + D6 | [sem] |
| 21 | S21 (M02) | Artifact comprehensiveness / article-type | M02 | mostly proxied by round-1 01 + L1 | — |
| 22 | S22 (M63) | Data homogeneity & standard adherence | M63 | net-new | [ext] |
| 23 | S23 (M05) | Genre / abstract-only relevance discount | M05 | already handled by round-1 penalize-don't-skip | — |

**Pruned** (pure duplicates of a round-1 winner or an L1 gate): M01 (↔ round-1 01 + L1 frontmatter),
M03 (↔ round-1 02 + D2 + L1 regex), M06 (↔ round-1 02 dependency + L1 §9), M27 (subsumed by S2/S8),
M43 (↔ round-1 08 + L1 §8), M45 (↔ L1 §9 + round-1 08).

## E.3 Top 10 to tournament first (max signal beyond round-1 + verifier)

1. **S1 — Reference-landscape completeness** `[ext]` — the clearest hole; neither round-1 nor verifier reaches external literature.
2. **S2 — Novelty vs literature** `[ext][sem]` — "done before?" is structurally impossible offline and out of scope for L2.
3. **S3 — Claim drift / reference truthfulness** `[ext][sem]` — turns L1 §10's self-quote check into a real does-the-source-support-it check.
4. **S4 — Claim↔Experiment↔Evidence entailment (+ publication-bias)** `[sem][ext]` — D1 semantically, beyond round-1; trial-registry bias cross-check beats both.
5. **S5 — End-to-end reproducibility bundle** (fig+data+code, cross-layer).
6. **S6 — Multi-perspective triangulation** `[sem]` — wholly absent from both.
7. **S7 — Assumption realism & limitation validity** `[sem]` — tighter than round-1 07 concreteness and D3 explicitness.
8. **S8 — Method validity & verification status** `[sem]` — tighter facet of D6.
9. **S9 — Controlled-vocabulary & latent-space anchoring** `[ext]` — net-new interoperability signal.
10. **S10 — FOL-ability (Oshima)** `[ext]/[sem]` — net-new formal-checkability signal.

## E.4 MISSING — net-new signals neither round-1 nor the verifier capture

- **Publication-bias detection via registry cross-reference** (M04): match a claim to a registered/completed trial and flag divergent reported outcomes. Needs a trial-registry lookup; currently one buried sub-bullet.
- **External novelty / "done-before" resolution** against the literature island / k-NN neighborhood (undermind / semantic-scholar) — the dependency the entire round-1 pool was explicitly built *without*.
- **FOL-graph constructability (Oshima)** as a formal, tool-checkable rigor signal — no tooling/operationalization exists yet.
- **Controlled-vocabulary / ontology anchoring & latent-space referenceability** — cross-artifact; needs an ontology/latent-space resolver; enables cross-ARA interoperability nothing else scores.
- **Multi-perspective (wet-lab × computational) triangulation strength** — completely uncovered.
- **Heuristic "distance from the optimum" (M39)** — a genuinely novel, hard signal (how far the chosen shortcut sits from the ideal); named but fully under-specified.
- **Data homogeneity & standards adherence (M63)** — adherence to field data standards, distinct from provenance hygiene.
- **"Started where the literature left off" positioning (M40)** — external-lit-anchored trajectory check on the exploration tree.

**How Part E relates to the novelty comparison.** Nearly every top-10 survivor is `[ext]`/`[sem]` and
several are novelty/literature-positioning checks (S1, S2, S16, S14, M40) — i.e. Carla's indicator
drafts are already reaching toward exactly the **external, novelty axis** the Metascience Novelty
Indicators Challenge / LENS occupies (see `NOVELTY_INDICATORS_COMPARISON.md`). Part E is where our
toolkit's roadmap and the external benchmark's territory start to converge.

---

## Sources
- `research/metrics/v3/tournament/DATA_SHAPES.md` (incl. Carla's per-artifact `Indicators` blocks)
- `research/metrics/v3/tournament/VERIFIER_COMPARISON.md`
- `research/metrics/v3/tournament/TOURNAMENT_SUMMARY.md`
- `research/metrics/v3/tournament2/METRICS_CANDIDATES.md` (64-candidate ledger → survivors → top-10 → missing)
