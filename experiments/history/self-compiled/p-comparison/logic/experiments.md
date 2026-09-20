# Experiments (Analyses)

> Grounding: full-text, self-authored paper. Each block reconstructs one analysis reported in `research/metrics/v4-gro/COMPARISON_PAPER.md`, run over the fixed 12-ARA corpus (che26, val25, han26, zim25, jes26, tit26, gau25, zho25, aki26, cum26, xu25, ard25). Underlying computed artifacts are in `research/metrics/v4-gro/` (see `../evidence/README.md`); this file records the method and result as reported, not a re-derivation.

## E01: Substrate benchmark H1 — GRO typed extension vs raw ARA prose, metric held constant
- **Verifies**: C01, C02, C03
- **Setup**:
  - Corpus: all 12 ARAs.
  - Arms: (a) raw ARA prose, parsed from `claims.md` / `related_work.md` / `experiments.md`; (b) GRO typed sidecars (the compiled typed graph).
  - Metrics run identically on both arms where expressible: quote_consistency, entailment_precondition, reference_resolvability, broken_ref_rate.
  - External ground truth: live PubMed lookups on reference resolvability, for the anchored subset.
  - Tooling: `benchmark.py`, producing `benchmark.json`.
- **Procedure**:
  1. Identify which of the 8 GRO deterministic metrics have any expression on unstructured prose (4 of 8 do: quote/entailment/reference-resolvability/broken-ref family).
  2. Run those 4 metrics on both the prose arm and the typed arm for each of the 12 ARAs.
  3. For reference resolvability, additionally check a sample of references against live PubMed to obtain an external-truth value per ARA.
  4. Compute per-metric mean absolute difference between prose and typed values across the 4 shared constructs.
  5. Compute per-arm MAE against the PubMed-truth value for reference resolvability.
  6. Time typed-field lookup vs prose parsing for reference resolvability across the 12-ARA corpus.
- **Metrics**: mean |prose − typed| per shared construct; MAE(arm, truth) for reference resolvability; wall-clock time per lookup (ms).
- **Expected outcome**: If typing were a free, faithful re-encoding, |prose − typed| ≈ 0 and typed MAE ≤ prose MAE. The paper reports the opposite on fidelity (typed MAE 0.44 > prose MAE 0.31) while confirming the speed/determinism win (0.05 ms vs 4.9 ms).
- **Baselines**: raw ARA prose is the baseline arm; live PubMed is the ground-truth baseline for reference resolvability.
- **Dependencies**: none

## E02: Substrate benchmark H2 — GRO metrics vs Seal L2, head-to-head
- **Verifies**: C04
- **Setup**:
  - Corpus: all 12 ARAs (Seal reviews all 12; GRO covers all 12).
  - Instruments: GRO's 8 deterministic + 4 anchored/judged metrics vs Seal L2's six-dimension (D1-D6) semantic review producing an overall score and recommendation.
  - Cost accounting: LLM token usage per ARA for a full Seal L2 review, vs 0 for GRO's deterministic metrics.
- **Procedure**:
  1. Run GRO's full metric battery and Seal L2's full review independently on all 12 ARAs.
  2. Compare on coverage, determinism/reproducibility, compute cost, auditability, external-truth-checkability.
  3. Identify specific per-ARA cases where one instrument catches something the other structurally cannot (e.g. che26 C05 scope over-generalization — Seal D3 flags it; GRO `overclaim_flags` = 0 because `population_n` is stated, not missing).
- **Metrics**: coverage (n ARAs scored / 12); LLM tokens per ARA; qualitative catch/miss inventory per dimension.
- **Expected outcome**: Neither instrument dominates; GRO wins on cost/coverage/auditability, Seal wins on semantic-judgment reach. Reported result matches this expectation — "not a winner, complementary."
- **Baselines**: none (head-to-head comparison, no external baseline).
- **Dependencies**: none

## E03: Three-way Spearman rank correlation across GRO, v3, and Seal
- **Verifies**: C05
- **Setup**:
  - Corpus: all 12 ARAs, plus a robustness check excluding ard25 (n = 11).
  - Scores compared: Seal overall score, GRO structural health score, v3 artifact-trust score, one value per ARA per instrument.
- **Procedure**:
  1. Assemble the three per-ARA score vectors (Seal overall, GRO health, v3 trust) across all 12 ARAs.
  2. Compute Spearman rank correlation for each of the three instrument pairs, with p-values.
  3. Repeat excluding ard25 to check whether the single point of three-way agreement (ard25) is driving the result.
- **Metrics**: Spearman rho and p per pair, computed on n = 12 and n = 11.
- **Expected outcome**: If the three instruments measured the same underlying "quality" construct, all three pairwise correlations would be strongly positive. The reported result shows GRO-vs-v3 strongly positive (rho = 0.678, p = 0.015) but Seal-vs-either structural instrument near zero and trending negative once ard25 is excluded.
- **Baselines**: none (internal cross-instrument comparison).
- **Dependencies**: [E02]

## E04: v3 coverage/architecture audit against GRO
- **Verifies**: C06
- **Setup**:
  - Corpus: all 12 ARAs.
  - v3 fields checked: `rank_eligible`, `extractive_fidelity` (pending vs computed), `semantic_grounding` (judge-scored vs pending).
  - GRO fields checked: per-metric null/failure count across all 12 ARAs.
- **Procedure**:
  1. Tabulate which ARAs have `rank_eligible = true` in v3 (found: che26, tit26, cum26 — 3/12).
  2. Tabulate which ARAs have non-pending `extractive_fidelity` and `semantic_grounding` values (4/12 each).
  3. Tabulate GRO's per-metric null/failure rate across all 12 ARAs (0 failures; only structural nulls on `quantity_reconciliation_rate` for zho25, aki26).
  4. Attribute the coverage gap to v3's dependency on an LLM re-reading the source PDF (only run for 3-4 ARAs) vs GRO's dependency only on the typed graph that exists on every compiled ARA.
- **Metrics**: fraction of corpus with a non-pending/non-null score, per instrument.
- **Expected outcome**: GRO's coverage should exceed v3's because GRO's metrics require no additional LLM pass beyond the compilation the ARA already has. Reported result: GRO 12/12 (100%) vs v3 3/12 (25%) fully scored.
- **Baselines**: none (architecture audit, not a performance comparison).
- **Dependencies**: none

## E05: External validation of reference_resolvability_rate against live PubMed
- **Verifies**: C07
- **Setup**:
  - Subset: the 6-ARA anchored cluster (che26, val25, han26, zim25, jes26, tit26).
  - Declared value: GRO's self-declared `reference_resolvability_rate` per ARA (computed from whether the compiler captured a DOI at compile time).
  - Observed value: live PubMed resolution of a sample of each ARA's cited references.
- **Procedure**:
  1. For each of the 6 anchored ARAs, sample references from the ARA's reference ledger.
  2. Query live PubMed for each sampled reference to determine whether it independently resolves.
  3. Compare the declared `reference_resolvability_rate` to the observed PubMed-resolution rate, per ARA and as a corpus mean.
  4. Diagnose the gap: per GRO's own conclusion, the deterministic metric "scores DOI-capture completeness rather than reference verifiability."
- **Metrics**: declared rate vs observed rate, per ARA and corpus mean; gap magnitude.
- **Expected outcome**: If the declared metric measured true verifiability, declared ≈ observed. Reported result: declared mean 0.5197 vs observed mean 0.9583, a ≈0.44 gap, with val25/han26/tit26 as the sharpest individual mismatches.
- **Baselines**: live PubMed is the ground-truth baseline.
- **Dependencies**: [E01]

## E06: che26 case study — v3 extractive_fidelity vs GRO ledger-consistency metrics
- **Verifies**: C08
- **Setup**:
  - ARA: che26 (diagnostic performance of plasma p-tau217, network meta-analysis).
  - v3 metric: `extractive_fidelity` (re-reads the source PDF, flags unsupported/contradicted/distorted claims).
  - GRO metrics: `quantity_reconciliation_rate`, `entailment_precondition_rate` (both check the ledger's canonical value against its own quote; neither touches the source PDF).
- **Procedure**:
  1. Run v3's `extractive_fidelity` pass on che26 against its source paper.
  2. Independently run GRO's `quantity_reconciliation_rate` and `entailment_precondition_rate` on the same ARA's typed ledger.
  3. Compare: identify the specific claim/statistic where the two disagree (a forest-plot MD statistic).
- **Metrics**: extractive_fidelity score (0-1); quantity_reconciliation_rate, entailment_precondition_rate (0-1 each).
- **Expected outcome**: If GRO's ledger-consistency checks were a valid proxy for source fidelity, a fabrication caught by v3 should also depress GRO's scores. Reported result: v3 extractive_fidelity = 0.625 (catches the fabricated MD = 0.10, 95% CI 0.04-0.16, absent from the source) while GRO scores both ledger-consistency metrics 1.0 (clean) on the same ARA.
- **Baselines**: the source PDF is the ground truth for extractive fidelity.
- **Dependencies**: [E04]

## E07: ard25 case study — three-instrument convergence on a structurally broken ARA
- **Verifies**: C09
- **Setup**:
  - ARA: ard25 (response of spatially defined microglia states, preclinical mechanistic study).
  - Instruments: GRO structural health score, v3 artifact-trust score, Seal L2 overall score + D5 (Exploration Integrity).
  - Known defect: ard25's compiled artifact is missing `logic/experiments.md`.
- **Procedure**:
  1. Compute GRO's `broken_ref_integrity` for ard25 (found: 16/16, 100% of proof_refs).
  2. Compute v3's structural gates for ard25 (`seal_L1 = false`, `all_links_resolve = false`, `low_trust = true`).
  3. Run Seal L2's full review on ard25, noting D5 (Exploration Integrity) and the overall recommendation.
  4. Rank ard25 against all 11 other ARAs on each instrument's score independently.
  5. Diagnose the shared root cause via ard25's own compilation diagnostics (missing `logic/experiments.md`).
- **Metrics**: GRO health score, v3 artifact-trust score, Seal overall score and recommendation, broken_ref_integrity count.
- **Expected outcome**: If the three instruments measure unrelated things, catastrophic structural breakage should still be visible to all three, since it is not a subtle scope/quality judgment but a missing file. Reported result: GRO 0.000 (last of 12), v3 0.150 (last of 12), Seal 3.0/"Reject" (last of 12) — the sole three-way agreement in the corpus.
- **Baselines**: the other 11 ARAs in the corpus serve as the comparison set for "worst-ranked."
- **Dependencies**: [E03]

## E08: Metric reliability audit — GRO's own best/most-uncertain ranking and formula-defect check
- **Verifies**: C10
- **Setup**:
  - All 8 GRO deterministic + 4 anchored/judged metrics, scored across all 12 ARAs.
  - Reliability criteria: consistency of firing, resistance to gaming, coverage, and (where available) agreement with an external anchored check.
- **Procedure**:
  1. Tabulate each metric's corpus statistic, coverage (n ARAs nonzero/defined), and known construct-validity concerns (§3.3 of the paper).
  2. For `genre_silent_omissions`, inspect the formula `count(expected) − count(present) − count(absent_declared)` against per-ARA `present_slots`/`expected_slots` enums.
  3. Identify the case (zho25) where `present_slots` includes a slot outside `expected_slots`, producing a negative count.
- **Metrics**: per-metric corpus stat, coverage fraction, reliability verdict (best / middle / most uncertain).
- **Expected outcome**: A well-specified counting formula should never return a negative "number of omissions." Reported result: zho25 scores `genre_silent_omissions` = −1, confirming the formula defect.
- **Baselines**: none (internal formula audit).
- **Dependencies**: none
