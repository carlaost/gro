# Three Ways to Judge an Agent-Native Research Artifact

### A metascience comparison of GRO ideal metrics, an ARA-inferred metric design (v3), and a semantic verifier (Seal Level 2) over 12 compiled ARAs

---

## 0. Abstract

We compare three distinct approaches to evaluating **Agent-Native Research Artifacts (ARAs)** — machine-readable knowledge packages compiled from published papers — over a fixed corpus of **12 ARAs** in the Alzheimer's disease / neurodegeneration domain. The three approaches occupy different **rigor tiers**:

1. **GRO ideal metrics (Tier A, deterministic + reliable-anchored + reproducible-judged).** A battery of metrics computed over the ARA's typed graph (claims, quantities, references, entities, genre), plus a smaller set of externally anchored checks (live PubMed / registry lookups) run on the biomarker/trial half of the corpus.
2. **The first ARA-inferred metric design (v3).** An earlier tournament-selected battery — `extractive_fidelity`, six `paper_rankers`, and a composite `artifact_trust` — that layers a partial source-text semantic check on top of structural completeness logic.
3. **The ARA verifier (Seal Level 2).** A calibrated semantic reviewer that reads the argument and scores six epistemic dimensions (D1–D6), producing a per-ARA recommendation from Strong Accept to Reject.

Three findings organize the paper. **First**, the approaches differ enormously in *reach*: GRO scores all 12/12 ARAs; v3 fully scores only 3/12; Seal scores all 12 but through human-grade semantic labor. **Second**, they measure *near-orthogonal constructs*: Seal's overall score is essentially uncorrelated with GRO's structural health (Spearman ρ = −0.011) and with v3 artifact-trust (ρ = 0.035), while the two structural instruments correlate strongly with each other (ρ = 0.678, p = 0.015). **Third**, no single approach discriminates good science from bad science on its own — each catches real defects the other two are structurally blind to. We argue the three tiers are **complementary, not competing**: a deterministic structural floor, an externally anchored middle, and a judged semantic ceiling. We are explicit about the limits: the anchored/judged evidence exists for only half the corpus, there is **no external good-vs-bad ground-truth set**, and n = 12 in a single sub-domain.

---

## 1. Setup

### 1.1 The 12-ARA corpus

All 12 ARAs were compiled from published Alzheimer's / neurodegeneration papers and carry GRO "ideal" data shapes (a typed claim/quantity/reference/entity/genre graph). They fall into two natural clusters that matter for everything downstream:

- A **biomarker + trial cluster** (6 ARAs): che26, val25, han26, zim25, jes26, tit26 — the p-tau217 assay and donanemab-trial papers. **These are the only ARAs with any externally anchored or judged-tier evidence.**
- A **biology / epidemiology / pipeline cluster** (6 ARAs): gau25, zho25, aki26, cum26, xu25, ard25 — assessed on deterministic-tier metrics only.

| Slug | Short description | Genre (GRO paper-type) | # claims |
|---|---|---|---|
| che26 | Diagnostic performance of plasma p-tau217 (network meta-analysis) | systematic_review_meta_analysis | 8 |
| val25 | Blood biomarkers of AD (SNAC-K observational cohort) | observational_epidemiology | 13 |
| han26 | VeraBIND Tau — plasma tau pathological activity | diagnostic_accuracy_study | 12 |
| zim25 | Donanemab in early symptomatic AD (long-term extension) | randomized_controlled_trial (LTE) | 12 |
| jes26 | Efficacy and safety of donanemab | randomized_controlled_trial | 10 |
| tit26 | Automated high-throughput plasma p-tau quantification | diagnostic_accuracy_study | 11 |
| gau25 | Single-nucleus + spatial transcriptomic profiling | primary_experimental | 14 |
| zho25 | Microglia networks (narrative review) | narrative_review_survey | 14 |
| aki26 | Molecular signatures of resilience to AD | molecular_neuropathology_single_cell_omics | 10 |
| cum26 | AD drug-development pipeline census | clinical_pipeline_registry_census | 10 |
| xu25 | Epidemiological & sociodemographic transitions | epidemiological_secondary_analysis | 13 |
| ard25 | Response of spatially defined microglia states | preclinical_mechanistic_study | 13 |

### 1.2 The three approaches

- **GRO ideal metrics.** Eight deterministic metrics computed over the typed ARA graph, every one flagged `computable_on_prose: false` — they *only* exist because the compiler typed the graph, and they *never read the source PDF*. Plus four externally anchored/judged metrics (retractions, external reference-resolvability, prior-literature novelty, trial-registry concordance) run against live PubMed / ClinicalTrials.gov for the 6-ARA biomarker cluster.
- **v3 (first ARA-inferred design).** `extractive_fidelity` (an LLM re-reads the source and flags unsupported/contradicted/distorted claims), six `paper_rankers`, and a composite `artifact_trust` (grounding_trust, environment_completeness, falsifiability_presence, compiler_fidelity, gate_pass_ratio). v3 **degrades to `pending` rather than fabricating a score** when it lacks the input to judge.
- **Seal Level 2.** A semantic reviewer scoring six dimensions on a 1–5 scale — **D1 Evidence Relevance, D2 Falsifiability Quality, D3 Scope Calibration, D4 Argument Coherence, D5 Exploration Integrity, D6 Methodological Rigor** — then an overall score and a recommendation.

### 1.3 The three rigor tiers

The cleanest way to read the whole comparison is as three tiers of epistemic warrant:

| Tier | What it answers | How | Primary instrument here |
|---|---|---|---|
| **Tier A — deterministic** | "Is the artifact internally well-formed?" | Pure lookup / arithmetic over typed fields; no comprehension, no external call | GRO deterministic metrics; v3 structural components |
| **Tier B — reliable-anchored** | "Do its external referents actually exist?" | Live query to an authority the author can't edit (PubMed, registry) | GRO retractions / external ref-resolution / registry |
| **Tier C — reproducible-judged / semantic** | "Is the underlying science any good?" | LLM/human reads the argument and judges | GRO novelty verdict (judged); Seal L2 (semantic) |

The central empirical claim of this paper is that these tiers are **near-orthogonal in practice** and each is **necessary but not sufficient**.

[[FIG:tier_coverage]]

---

## 2. The GRO ideal metrics: best vs. most uncertain

GRO's own analysis ranks its metrics by reliability. The top-3 are metrics that fire consistently and are hard to game; the bottom-3 are metrics whose *construct validity* is in doubt — including one that is directly falsified by GRO's own anchored check.

### 2.1 The three best

1. **`claim_typing_coverage` (deterministic).** 1.0 across all 12/12 ARAs, 0 nulls. A pure structural presence/enum check (`claim_type ∈ enum AND logical_form ≠ not_specified`) with no external dependency. Gaming it would require fabricating a non-empty logical form for *every* claim — a visible, checkable artifact. Zero variance across five very different genres is evidence the check is well-specified, not trivially true. **Caveat: this same zero variance means it has no discriminating power in this corpus.**
2. **`quantity_reconciliation_rate` (deterministic).** 1.0 across all 10/12 ARAs where it is defined (null for zho25, aki26 — structurally vacuous, no quantity cited by ≥2 claims). An arithmetic cross-check between two independently authored fields (the ledger's canonical value vs. the numeral embedded in the claim's own quote). The only blemish is coverage, not correctness.
3. **`retractions` (reliable-anchored).** 0 found across all 6 externally-checked ARAs and their top-cited references, each verified via itemized live PubMed publication-type queries. Anchored to an authority the ARA author cannot edit. **Caveat: floor effect — the corpus contains no known-bad papers, so this is proven trustworthy, not proven discriminating.**

### 2.2 The three most uncertain

1. **`reference_resolvability_rate` (self-declared / deterministic).** The one metric with a direct ground-truth check on the *same quantity* — and the ground truth contradicts it. Declared corpus mean **0.5197** vs. independently observed **0.9583** (a ≈0.44 gap). val25 declares 0.0 (0/55) but PubMed resolved 9/12 sampled refs; han26 declares 0.19 but resolves 1.0; tit26 declares 0.132 but resolves 1.0. Per GRO's own conclusion, the deterministic metric "scores DOI-capture completeness rather than reference verifiability" — it measures whether the compiler captured a DOI at compile time, not whether the reference is real.
2. **Prior-literature novelty verdict (reproducible-judged).** 22.6% of checked claims (7/31) land in `cannot_determine`; verdicts split almost evenly across all four categories (novel 32.3% / incremental 32.3% / cannot_determine 22.6% / previously_reported 12.9%). Each verdict rests on an LLM judgment over a PubMed search, and the methodology surfaces its own limit — "absence of a PubMed hit is not strong evidence of absence." Only 31 claims across 6/12 ARAs are covered at all.
3. **Trial-registry concordance (anchored + judged).** Only 2 trial papers exist to check (zim25, jes26), and **both are post-hoc analyses of the exact same trial, NCT04437511** — so, per the source file, "registry-concordance evidence is effectively a single data point." The concordance-gap verdict (post-hoc CDR-Global HR, plasma p-tau217, LTE-vs-ADNI comparisons added beyond registered outcomes) is real but generalizes to nothing. 10/12 ARAs have registry = null.

### 2.3 Also flagged (construct-validity concerns)

- **`genre_silent_omissions`** has a documented formula bug: `count(expected) − count(present) − count(absent_declared)` can go **negative** (zho25 = −1) when a genre's `present_slots` includes a slot outside its own `expected_slots` list.
- **`broken_ref_integrity`** is 100% concentrated in one ARA (ard25 = 16/16); ard25's own diagnostics attribute this to a missing `logic/experiments.md` file, not genuinely broken citations — the metric conflates "cites a nonexistent id" with "cites a real id in a ledger the compiler never found."
- **`overclaim_flags`** concentrates almost entirely in two genres (xu25 epidemiological projections = 11/13; cum26 pipeline census = 9/10) that structurally traffic in population-level estimates lacking a single sample-size field — raising the question of whether it flags overclaiming or just a genre feature.
- **`entity_anchoring_rate`** = 0.0 for all 12/12 ARAs — a corpus-wide pipeline gap (no ARA does ontology linking), reliably measured but with zero discriminating power.

### 2.4 Per-metric summary

| GRO metric | Tier | Corpus stat | Coverage | Reliability verdict |
|---|---|---|---|---|
| claim_typing_coverage | deterministic | mean 1.0 (min 1.0, max 1.0) | 12/12 | **Best** — but non-discriminating |
| quantity_reconciliation_rate | deterministic | mean 1.0 | 10/12 (2 null) | **Best** — coverage gap only |
| retractions | anchored | 0 found | 6/12 | **Best** — floor effect |
| entailment_precondition_rate | deterministic | mean 0.821 (0.4–1.0) | 12/12 | Middle — real spread, useful |
| external reference-resolvability | anchored | observed mean 0.958 | 6/12 | Middle — sound check, small sample |
| genre_silent_omissions | deterministic | total 4 (min −1, max 4) | 3/12 nonzero | Middle — formula defect (can go negative) |
| overclaim_flags | deterministic* | total 23 (max 11) | 3/12 nonzero | Middle — genre-blindness / construct doubt |
| broken_ref_integrity | deterministic | total 16 (all ard25) | 1/12 nonzero | Middle — single-ARA compilation artifact |
| entity_anchoring_rate | deterministic | 0.0 everywhere | 12/12 | Middle — reliable, zero discrimination |
| reference_resolvability_rate | deterministic | mean 0.374 (0.0–1.0) | 12/12 | **Most uncertain** — falsified by anchored check |
| prior-lit novelty verdict | judged | 31 claims, 22.6% cannot_determine | 6/12 | **Most uncertain** — search-phrasing dependent |
| trial-registry concordance | anchored + judged | 2 papers, same trial | 2/12 | **Most uncertain** — n = 1 trial |

\*`overclaim_flags` is nominally deterministic but scored over LLM-typed `population_scope` / `population_n` fields.

### 2.5 The full deterministic grid

Every deterministic metric, every ARA. `CTC` and `EAR` are constant (1.0 and 0.0) and carry no discriminating information; the action is in the middle columns.

| ARA | QuantRecon | Entailment | RefResolv | GenreOmit | Overclaim | BrokenRef |
|---|---|---|---|---|---|---|
| che26 | 1.00 | 1.00 | 0.944 | 0 | 0 | 0 |
| val25 | 1.00 | 0.692 | 0.000 | 1 | 0 | 0 |
| han26 | 1.00 | 1.00 | 0.190 | 0 | 0 | 0 |
| zim25 | 1.00 | 1.00 | 0.957 | 0 | 0 | 0 |
| jes26 | 1.00 | 1.00 | 0.895 | 0 | 0 | 0 |
| tit26 | 1.00 | 1.00 | 0.132 | 0 | 0 | 0 |
| gau25 | 1.00 | 0.571 | 0.100 | 0 | 0 | 0 |
| zho25 | null | 0.500 | 0.000 | −1 | 3 | 0 |
| aki26 | null | 0.400 | 0.136 | 0 | 0 | 0 |
| cum26 | 1.00 | 1.00 | 1.000 | 0 | 9 | 0 |
| xu25 | 1.00 | 0.923 | 0.137 | 0 | 11 | 0 |
| ard25 | 1.00 | 0.769 | 0.000 | 4 | 0 | 16 |

[[FIG:gro_metric_grid]]

---

## 3. Held against the first ARA-inferred design (v3)

### 3.1 The coverage gap is architectural

v3 could **fully score 3/12 ARAs (25%)**; GRO scored **all 12/12 (100%)**.

- v3 `rank_eligible = true`: only che26, tit26, cum26.
- v3 `extractive_fidelity` computed (non-pending): 4/12 — che26 (0.625), jes26 (0.9), tit26 (1.0), cum26 (1.0); `pending` on the other 8/12.
- v3 `semantic_grounding` judge-scored: 4/12; `pending` on 8/12.
- GRO: 12/12 processed, 0 failed; the only metric-level nulls are `quantity_reconciliation_rate` on zho25 and aki26 (structurally vacuous).

The gap is not incidental. **Every GRO metric is `computable_on_prose: false` and computes over the typed graph that exists on every compiled ARA.** v3's `extractive_fidelity` and `paper_rankers` additionally require an LLM to re-read the source PDF and judge fidelity/novelty — a pass wired up (frozen judge findings) for only 3–4 ARAs. So **v3 trades reach for depth** (it verifies extraction against source prose, but only where the pass was run) while **GRO trades depth for reach** (it runs everywhere, but only checks the ARA's own internal consistency and never sees the source paper).

### 3.2 Construct overlap

| Construct | v3 metric | GRO metric | Relationship |
|---|---|---|---|
| Claim-to-source fidelity | `extractive_fidelity` (re-reads source PDF) | `quantity_reconciliation_rate` + `entailment_precondition_rate` (ledger self-consistency only) | **GRO strictly weaker** — it cannot catch a claim that is faithful to its own record but was never true of the source. v3's is the only construct in either system that re-checks the source text. |
| Reference / citation integrity | `artifact_trust.gates.all_links_resolve` (boolean) | `reference_resolvability_rate` (continuous) + `broken_ref_integrity` (count) | Same target; **GRO more diagnostic** (continuous rate/count vs. a single pass/fail bit). |
| Claim scope / overreach | `semantic_grounding` (judge-scored, 4/12) | `overclaim_flags` (mechanical scope-label vs. missing-n) | Different axis of the same worry; GRO's runs everywhere but is a narrow, genre-correlated proxy. |
| Genre-appropriate completeness | genre used only as an eligibility label | `genre_silent_omissions` | GRO adds this construct outright; v3 has no analog. |

**GRO-only constructs (no v3 analog):** `entity_anchoring_rate` (0.0 corpus-wide), `broken_ref_integrity`, `genre_silent_omissions`, `overclaim_flags`.
**v3-only constructs (no GRO analog):** `corrective_science_score`, `dead_end_density` / `negative_result_share`, `translation_trial_linkage`, `novel_claim_count` — the paper_rankers.

v3's own tournament headline — **0/6 usable paper_rankers** — is confirmed on this corpus: `corrective_science_score` is `invalid_fabricated` on 12/12; `negative_result_share` is `pending_sem` on 12/12; `translation_trial_linkage` is self-annotated "superseded" on 12/12; `dead_end_density` is fabricated or vacuous; `semantic_grounding` is judge-scored on only 4/12; `novel_claim_count` is `pending_sem` even where a value exists. None reaches a fully valid corpus-wide state.

### 3.3 Agreement and divergence

- **Sharpest divergence — che26.** v3 `extractive_fidelity` = 0.625 catches a **fabricated forest-plot statistic** (MD = 0.10, 95% CI 0.04–0.16) that appears nowhere in the source. GRO scores this same ARA `quantity_reconciliation_rate` = 1.0 and `entailment_precondition_rate` = 1.0 — clean — because those metrics only check the ledger against its own quote and never touch the PDF. **GRO's structural checks cannot substitute for source verification even where both nominally target "fidelity."**
- **Second-sharpest divergence — cum26.** v3's *best* ARA (fidelity 1.0, semantic_grounding 0.941, 8/8 NCTs verified) is GRO's *most-overclaiming* ARA (`overclaim_flags` = 9/10). Perfectly faithful extraction of a source that itself makes unscoped population claims.
- **tit26.** v3 marks it clean (fidelity 1.0, all gates pass), but GRO's continuous `reference_resolvability_rate` = 0.132 exposes that most references are unverifiable — a distinction v3's boolean gate cannot make.
- **Sharpest agreement — ard25.** v3 gates (`seal_L1 = false`, `all_links_resolve = false`, `low_trust = true`) and GRO counts (`broken_ref_integrity` = 16, `genre_silent_omissions` = 4, both corpus maxima) converge on the same "structurally worst" verdict — GRO supplying the auditable counts v3's booleans compress away.

---

## 4. Held against the ARA verifier (Seal L2)

### 4.1 Per-ARA Seal scorecard

Seal dimensions: **D1** Evidence Relevance · **D2** Falsifiability Quality · **D3** Scope Calibration · **D4** Argument Coherence · **D5** Exploration Integrity · **D6** Methodological Rigor (each 1–5).

| ARA | D1 | D2 | D3 | D4 | D5 | D6 | Overall | Recommendation | GRO health | v3 trust |
|---|---|---|---|---|---|---|---|---|---|---|
| che26 | 4 | 4 | 3 | 4 | 4 | 3 | 3.7 | Weak Accept | 0.982 | 0.944 |
| val25 | 5 | 4 | 5 | 5 | 4 | 5 | **4.7** | **Strong Accept** | 0.564 | 0.615 |
| han26 | 4 | 4 | 4 | 4 | 5 | 3 | 4.0 | Weak Accept | 0.730 | 1.000 |
| zim25 | 4 | 3 | 4 | 5 | 4 | 2 | 3.7 | Weak Accept | 0.986 | 0.931 |
| jes26 | 4 | 4 | 4 | 5 | 3 | 3 | 3.8 | Weak Accept | 0.965 | 0.974 |
| tit26 | 4 | 4 | 4 | 5 | 3 | 4 | 4.0 | Accept | 0.711 | 0.917 |
| gau25 | 4 | 4 | 5 | 5 | 4 | 4 | 4.3 | Accept | 0.557 | 0.685 |
| zho25 | 4 | 3 | 4 | 4 | 2 | 2 | 3.2 | Weak Accept | 0.143 | 0.178 |
| aki26 | 4 | 4 | 4 | 5 | 5 | 4 | 4.3 | Accept | 0.268 | 0.919 |
| cum26 | 4 | 3 | 4 | 5 | 4 | 4 | 4.0 | Accept | 0.550 | 0.970 |
| xu25 | 4 | 4 | 4 | 5 | 5 | 3 | 4.2 | Accept | 0.264 | 0.754 |
| ard25 | 4 | 3 | 4 | 4 | 1 | 2 | 3.0 | **Reject** | 0.000 | 0.150 |

[[FIG:seal_dimensions]]

### 4.2 What Seal catches that neither metric set can

- **Scope over-generalization with a *stated* n (che26, D3 = 3).** GRO `overclaim_flags` = 0 here, because its rule fires only when `population_n` is literally missing. Seal flags C05 verbatim: *"a generalization claim that overreaches its evidence type … a P-score of 1.00 computed within only two Han Chinese cohorts (Huashan N=297, Greater Bay N=425) with no reported formal ethnicity-by-biomarker interaction test."* The cohort sizes *are* named, so the structural rule is satisfied — detecting the overreach requires knowing what statistical test the claim needs. Comprehension, not a field lookup.
- **Evidence-source mismatch (che26).** C03's "reduce the need for tau-PET scans by ~80%" is *"sourced from an unrelated external reference (Therriault et al., 2021) … not derived from this NMA's own AUC/P-score outputs."* No structural field encodes argument coherence.
- **Uncorrected multiplicity (jes26, zim25, val25).** A recurring methodological judgment: *"No multiplicity correction is applied … yet every claim is nonetheless labeled 'supported' with uniform confidence."* No GRO or v3 field maps to it.
- **Sponsor / conflict-of-interest and reproducibility (zim25, D6 = 2).** *"Sponsor-only authorship (all 18 authors are Eli Lilly employees) … no released analysis code, no stated software version … several supplementary figures/tables … absent from the provided PDF."* No structural field maps to authorship or funding conflicts.

### 4.3 What the deterministic metrics catch that Seal misses or softens

- **Citation-graph integrity — no Seal dimension asks it.** val25 has **0/55 references resolvable** (`reference_resolvability_rate` = 0.0), yet Seal's D1 = 5 and overall = 4.7 (Strong Accept). Not a contradiction — D1 asks whether quoted evidence matches the claim, not whether the works-cited ledger resolves externally — but a reader of the Seal alone would never learn the bibliography doesn't resolve. Same blind spot: zho25 (0.0), ard25 (0.0), gau25 (0.1), tit26 (0.132).
- **Exact auditable counts where Seal narrates.** ard25: GRO `broken_ref_integrity` = 16/16 (100% of proof_refs). Seal converges narratively — *"every claim's verification-plan linkage is a dangling reference"* (D5 = 1) — but GRO supplies the precise fraction Seal's prose compresses into a floor-rule Reject.
- **Genre-blindness cutting the other way.** GRO `overclaim_flags` fires on 9/10 (cum26) and 11/13 (xu25) claims; Seal's D3 = 4 for both does **not** corroborate an overclaiming problem — these are census/GBD genres that legitimately state population-level estimates without a sample size. Here the *deterministic* metric is the one over-flagging.
- **A formula breaking at a genre edge.** zho25 `genre_silent_omissions` = −1 (a nonsensical negative from the literal count formula on a review genre); Seal instead reasons in prose that exploration integrity is *"honestly disclaimed rather than fabricated … effectively unscoreable"* (D5 = 2). Genre-aware judgment the rigid formula cannot make.

### 4.4 Do the three rank consistently?

Spearman rank correlation across the 12 ARAs:

| Pair | ρ (all 12) | p | ρ (excl. ard25, n=11) |
|---|---|---|---|
| Seal overall vs GRO health | **−0.011** | 0.974 | −0.318 |
| Seal overall vs v3 artifact-trust | **0.035** | 0.913 | −0.258 |
| GRO health vs v3 artifact-trust | **0.678** | 0.015 | 0.582 (p = 0.060) |

Seal is **essentially uncorrelated** with both structural instruments, which correlate strongly with **each other**. The single point of three-way agreement is **ard25** — a structurally broken ARA (empty trace, missing `logic/experiments.md`) that every instrument independently ranks last. Remove it, and the Seal-vs-structural correlations trend **negative**, while GRO and v3 stay positive with each other. The two mechanical instruments agree about what "complete" looks like; neither agrees with what the calibrated reviewer considers "good."

**Illustrative inversions:**

- **val25** — Seal's #1 (4.7, Strong Accept) but #6 on GRO health and #10 on v3 trust (0% ref resolvability, environment_completeness 0.143). Faithfully scoped, well-evidenced, rigorously falsifiable — with real structural holes.
- **zim25** and **che26** — #1–2 on both structural instruments (GRO 0.986 / 0.982) but only #9–10 on Seal, capped by D6 rigor concerns (sponsor-only authorship, uncorrected multiplicity) invisible to structural metrics.

[[FIG:three_way_rank]]

### 4.5 The sharpest catch-divergences

[[FIG:divergence]]

| ARA | Instrument that catches it | What it catches | The other two |
|---|---|---|---|
| che26 | **v3** only | Fabricated forest-plot statistic (MD 0.10, CI 0.04–0.16) | GRO 1.0/1.0 (blind); Seal flags a *different* issue (C05 scope) |
| che26 | **Seal** only (D3) | Cross-ethnic overgeneralization from 2 cohorts, no interaction test | GRO overclaim = 0 (n is stated); v3 silent |
| val25 | **GRO** only | 0/55 references resolvable | Seal D1 = 5, overall 4.7; v3 pending |
| cum26/xu25 | **GRO** flags, arguably wrongly | 9/10 and 11/13 "overclaims" | Seal D3 = 4 (genre-appropriate); v3 clean |
| zim25 | **Seal** only (D6) | Sponsor-only authorship, no code, missing supplements | GRO 0.986 (#1); v3 0.931 |
| ard25 | **All three** | Missing experiments ledger → dangling proof refs | Three-way agreement (the lone case) |

---

## 5. Synthesis: three complementary tiers

The correlation structure is not a defect in any instrument — it is the empirical signature of the tier gap.

- **Tier A (deterministic — GRO structural, v3 structural components)** answers pure lookups over typed fields: does this ref resolve, does this claim carry a logical form, does this quantity match its quote. Zero comprehension of scientific quality. It catches **catastrophic breakage** (ard25) that no reviewer should read past, and it surfaces **facts a semantic rubric never asks about** (broken-ref counts, 0%-resolvable bibliographies). It is **necessary** — but it correlates near-zero with quality.
- **Tier B (reliable-anchored — GRO retractions / external ref-resolution / registry)** answers "do the external referents exist," via authorities the author cannot edit. It is the tier that **falsified GRO's own deterministic `reference_resolvability_rate`** (declared 0.52 vs. observed 0.96). Its power in *this* corpus is capped by a floor effect: no known-bad papers, so it is proven trustworthy, not proven discriminating.
- **Tier C (judged / semantic — GRO novelty verdict, Seal L2)** reads the argument and asks whether claims overreach their evidence and whether the methodology is rigorous for the genre. It catches scope overreach, multiplicity risk, and conflict-of-interest that **no structural field encodes**. It is the only tier that tracks "good science" — and it is the most expensive and the least reproducible.

**No single approach discriminates good-vs-bad alone.** v3's `extractive_fidelity` caught a fabricated statistic that GRO structurally cannot see (che26). GRO caught a 0%-resolvable bibliography that Seal's rubric never examines (val25). Seal caught a cross-ethnic overgeneralization and a sponsor-COI that neither metric can represent (che26, zim25). The three are near-orthogonal signals, and an ARA pipeline needs **Tier A/B structural gates before Tier C semantic review** — a deterministic floor to reject the structurally broken cheaply, an anchored middle to confirm external referents, and a judged ceiling for the epistemic call — **not one instead of the others.**

---

## 6. Limitations

We are deliberately conservative about what this comparison establishes.

1. **No external good-vs-bad ground-truth set.** The corpus contains **zero known-bad papers** — 0 retractions, no concealed outcome-switching, all references ultimately real. High reliability on `retractions` and external ref-resolution reflects a **floor/ceiling effect on a uniformly legitimate corpus**, not proof any instrument would correctly flag a fabricated or retracted paper. GRO's external validation says so directly: this "validates external computability and surfaces concordance/compilation gaps, but it is NOT a full good-vs-bad discrimination test."
2. **The anchored/judged tiers exist for only half the corpus.** All Tier-B/Tier-C metric evidence comes from the 6-ARA p-tau217/donanemab cluster. Every "most uncertain" verdict about anchored/judged metrics is itself demonstrated on **half the corpus, in one narrow clinical/biomarker sub-domain**. The `trial-registry concordance` finding rests on a **single trial** (NCT04437511) analyzed by two papers.
3. **LLM-authored extensions carry their own uncertainty.** Seal L2 is an LLM semantic reviewer; GRO's novelty verdicts are LLM judgments over PubMed searches whose outcomes are **phrasing-dependent** (22.6% `cannot_determine`); `overclaim_flags` is scored over LLM-typed fields. None of these has an independent human adjudicator in this study, so the Tier-C signal is itself unvalidated against expert consensus.
4. **Small, single-domain n.** Twelve ARAs, all Alzheimer's / neurodegeneration, split 6/6 across two clusters. The Spearman correlations (ρ = −0.011, 0.035, 0.678) are estimated on n = 12 (n = 11 excluding ard25); confidence intervals are wide and the near-zero Seal-vs-structural result should be read as "no detectable positive relationship in this sample," not "proven independence."
5. **Known metric defects remain unfixed in the reported numbers.** `genre_silent_omissions` can go negative (zho25 = −1); `broken_ref_integrity` conflates missing-ledger with broken-citation (ard25); the deterministic `reference_resolvability_rate` measures DOI-capture, not verifiability. These are reported as-is for honesty, not corrected.

The defensible conclusion is narrow and, we think, robust: **structural completeness is necessary but not sufficient, the three tiers measure near-orthogonal things on this corpus, and a credible ARA-evaluation pipeline must run all three rather than treat any one as a proxy for the others.**
