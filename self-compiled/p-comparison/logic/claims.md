# Claims

> Grounding: full-text, self-authored paper. Every load-bearing number is copied verbatim from `research/metrics/v4-gro/COMPARISON_PAPER.md`, tagged `[result]` where it is a computed finding of this comparison, `[input]` where it is a corpus/setup fact the comparison takes as given. Section refs (`§n`) point into COMPARISON_PAPER.md; filenames (`benchmark.json`, etc.) point to the computed artifacts the paper's tables/figures were generated from, described in `../evidence/README.md`.

## C01: The GRO extension's primary value is making inexpressible metrics computable, not improving expressible ones
- **Statement**: Of the 8 GRO deterministic metrics, only 4 (quote/entailment/reference-resolvability/broken-ref family) have any expression on raw ARA prose at all; the other 4 (claim-typing, entity-anchoring, over-claim, genre) are computable **only** on the typed sidecar shape, because the raw ARA has no field to read.
- **Status**: supported
- **Falsification criteria**: A demonstration that claim-typing, entity-anchoring, over-claim, or genre_silent_omissions can be computed directly from unstructured ARA prose without first typing the graph.
- **Proof**: [E01]
- **Evidence basis**: §2.1 substrate benchmark (H1), run via `benchmark.py`/`benchmark.json` over the 12-ARA corpus.
- **Dependencies**: none
- **Sources**:
  - `4 of 8 metrics prose-expressible` ← benchmark.json / §2.1 «Only 4 of the 8 GRO metrics have *any* prose form; the other 4 — claim-typing, entity-anchoring, over-claim, genre — are computable **only** on the typed shape (the raw ARA has no field to read).» [result]
- **Tags**: substrate-benchmark, H1, affordance, GRO-extension

## C02: Typing an already-expressible metric changes its value and can reduce fidelity against external ground truth
- **Statement**: On the 4 constructs expressible on both the raw ARA prose and the GRO typed shape, the substrate materially changes the computed value (mean |prose − typed| = 0.21 / 0.17 / 0.28 across the shared constructs), and on the one construct with independent external ground truth (reference resolvability, checked against live PubMed), raw prose is *closer* to the ground truth than the typed sidecar: MAE 0.31 (prose) vs 0.44 (typed).
- **Status**: supported
- **Falsification criteria**: A rerun of the benchmark showing prose and typed values converge (|prose − typed| ≈ 0) on the shared constructs, or showing the typed sidecar's MAE against PubMed truth is equal to or better than the prose MAE.
- **Proof**: [E01]
- **Evidence basis**: §2.1, second and third paragraphs; `benchmark.json` per-ARA `prose`/`typed`/`truth` blocks (e.g. che26, val25 shown in the benchmark data).
- **Dependencies**: [C01]
- **Sources**:
  - `mean |prose − typed| = 0.21 / 0.17 / 0.28` ← benchmark.json / §2.1 «On the 4 shared constructs the substrate *materially changes the value* (mean |prose − typed| = 0.21 / 0.17 / 0.28)» [result]
  - `MAE 0.31 (prose) vs 0.44 (typed)` ← benchmark.json / §2.1 «on the one construct with external ground truth, the **raw ARA prose is closer to PubMed truth than the typed sidecar (MAE 0.31 vs 0.44)** — the LLM extension conservatively under-declared resolvable references that the prose (carrying the actual DOIs) captured.» [result]
- **Tags**: substrate-benchmark, H1, fidelity, reference-resolvability, LLM-drift

## C03: Typed-field lookups are ~100x faster than prose parsing and deterministic on rerun
- **Statement**: Reading a typed field for reference resolvability takes ~0.05 ms per ARA versus ~4.9 ms parsing prose, across the 12-ARA corpus, and the typed-field result is bit-identical on rerun (deterministic), whereas prose parsing is not guaranteed to be.
- **Status**: supported
- **Falsification criteria**: A timing rerun showing typed-field lookup is not substantially faster than prose parsing, or showing typed-shape results vary across reruns on identical input.
- **Proof**: [E01]
- **Evidence basis**: §2.1, "Where typing wins unambiguously..." paragraph.
- **Dependencies**: [C01]
- **Sources**:
  - `0.05 ms vs 4.9 ms across 12 ARAs` ← benchmark.json / §2.1 «reading a typed field is ~100× faster than parsing prose (reference resolvability 0.05 ms vs 4.9 ms across 12 ARAs) and is bit-identical on rerun.» [result]
- **Tags**: substrate-benchmark, H1, cost, determinism, GRO-extension

## C04: GRO metrics win coverage/cost/determinism against Seal L2; Seal alone reaches semantic judgments GRO structurally cannot
- **Statement**: Head-to-head, the GRO metrics win coverage (12/12), determinism/reproducibility, compute cost (0 LLM tokens vs ~66,000 tokens per ARA for a Seal review), auditability (every score traces to a typed field), and external-truth-checkability. Seal wins on reaching semantic judgments — e.g. it flags che26's claim C05 as an over-generalization (D3 = 3) where GRO's `overclaim_flags` = 0 for that ARA, because GRO's rule only fires when `population_n` is literally missing.
- **Status**: supported
- **Falsification criteria**: A cost/coverage audit showing Seal L2 reviews cost fewer LLM tokens than reported, or a case where GRO's `overclaim_flags` correctly flags a scope over-generalization that has a stated sample size (which the current rule structurally cannot do).
- **Proof**: [E02]
- **Evidence basis**: §2.2 (H2 verdict) and §4.2 (che26 C05 example).
- **Dependencies**: none
- **Sources**:
  - `12/12 coverage, 0 vs ~66k LLM tokens/ARA` ← compare/vs_seal.json / §2.2 «the **GRO metrics win** coverage (12/12), determinism/reproducibility, compute cost (**0 LLM tokens** vs ~66k tokens per ARA for a Seal review), auditability (every score traces to a typed field), and external-truth-checkability.» [result]
  - `che26 overclaim_flags = 0 vs Seal D3 = 3` ← seal/che26-diagnostic-performance-of-plasma-p-tau217.json / §4.2 «GRO `overclaim_flags` = 0 here, because its rule fires only when `population_n` is literally missing. Seal flags C05 verbatim … The cohort sizes *are* named, so the structural rule is satisfied — detecting the overreach requires knowing what statistical test the claim needs.» [result]
- **Tags**: substrate-benchmark, H2, complementarity, Seal-L2, overclaim

## C05: Seal's overall score is statistically uncorrelated with both structural instruments, which correlate strongly with each other
- **Statement**: Across the 12-ARA corpus, Spearman rank correlation of Seal overall score vs GRO structural health is rho = −0.011 (p = 0.974); Seal overall vs v3 artifact-trust is rho = 0.035 (p = 0.913); GRO health vs v3 artifact-trust is rho = 0.678 (p = 0.015). Excluding ard25 (n = 11), the Seal-vs-structural correlations trend negative (−0.318 and −0.258) while GRO-vs-v3 stays positive (0.582, p = 0.060).
- **Status**: supported
- **Falsification criteria**: A recomputation of the Spearman correlations on the same 12-ARA per-instrument scores yielding a statistically significant positive correlation between Seal overall and either structural instrument.
- **Proof**: [E03]
- **Evidence basis**: §4.4 correlation table.
- **Dependencies**: none
- **Sources**:
  - `Seal vs GRO health rho = -0.011 (p=0.974)` ← compare/vs_seal.json / §4.4 «Seal overall vs GRO health | **−0.011** | 0.974 | −0.318»  [result]
  - `Seal vs v3 trust rho = 0.035 (p=0.913)` ← compare/vs_seal.json / §4.4 «Seal overall vs v3 artifact-trust | **0.035** | 0.913 | −0.258» [result]
  - `GRO health vs v3 trust rho = 0.678 (p=0.015)` ← compare/gro_vs_v3.json / §4.4 «GRO health vs v3 artifact-trust | **0.678** | 0.015 | 0.582 (p = 0.060)» [result]
- **Tags**: correlation, orthogonality, Seal-L2, v3, GRO, three-way

## C06: v3's LLM-dependent design fully scores only 3/12 ARAs; GRO scores all 12/12 — an architectural reach gap
- **Statement**: v3 achieves `rank_eligible = true` for only 3/12 ARAs (che26, tit26, cum26; 25%) and computes non-pending `extractive_fidelity` for only 4/12 (che26 0.625, jes26 0.9, tit26 1.0, cum26 1.0), with `pending` on the other 8/12; GRO processes 12/12 ARAs with 0 failures, the only nulls being `quantity_reconciliation_rate` on zho25 and aki26 (structurally vacuous, not a failure).
- **Status**: supported
- **Falsification criteria**: A rerun of v3's `extractive_fidelity`/`semantic_grounding` pass on the full 12-ARA corpus that returns non-pending scores for more than 4/12 ARAs without additional source-PDF re-ingestion.
- **Proof**: [E04]
- **Evidence basis**: §4 ("3.1 The coverage gap is architectural").
- **Dependencies**: none
- **Sources**:
  - `v3 fully scores 3/12 (25%); GRO 12/12` ← compare/gro_vs_v3.json / §4 «v3 could **fully score 3/12 ARAs (25%)**; GRO scored **all 12/12 (100%)**.» [result]
  - `extractive_fidelity computed on 4/12: che26 0.625, jes26 0.9, tit26 1.0, cum26 1.0` ← compare/gro_vs_v3.json / §4 «v3 `extractive_fidelity` computed (non-pending): 4/12 — che26 (0.625), jes26 (0.9), tit26 (1.0), cum26 (1.0); `pending` on the other 8/12.» [result]
- **Tags**: coverage, reach, v3, architecture, LLM-dependency

## C07: GRO's own reference_resolvability_rate metric is falsified by its own externally anchored PubMed check
- **Statement**: The declared corpus-mean `reference_resolvability_rate` is 0.5197, versus an independently observed mean of 0.9583 via live PubMed lookups on the 6-ARA anchored subset — a gap of ≈0.44. Per-ARA: val25 declares 0.0 (0/55) but PubMed resolves 9/12 sampled refs; han26 declares 0.19 but resolves 1.0; tit26 declares 0.132 but resolves 1.0.
- **Status**: supported (self-falsifying: the metric is shown wrong by another metric in the same battery)
- **Falsification criteria**: A rerun of the PubMed-anchored check on val25/han26/tit26's sampled references returning resolution rates consistent with the declared `reference_resolvability_rate` values (i.e. near 0.0/0.19/0.132 respectively) rather than near 1.0.
- **Proof**: [E05]
- **Evidence basis**: §3.2, first item ("The three most uncertain").
- **Dependencies**: none
- **Sources**:
  - `declared 0.5197 vs observed 0.9583` ← external_validation.json / §3.2 «Declared corpus mean **0.5197** vs. independently observed **0.9583** (a ≈0.44 gap).» [result]
  - `val25 declares 0.0 (0/55), PubMed resolves 9/12; han26 declares 0.19, resolves 1.0; tit26 declares 0.132, resolves 1.0` ← external/val25-blood-biomarkers-of-alzheimer-s-disease.json, external/han26-tau-pathological-activity-in-plasma-before.json, external/tit26-automated-high-throughput-quantification-of-plasma.json / §3.2 «val25 declares 0.0 (0/55) but PubMed resolved 9/12 sampled refs; han26 declares 0.19 but resolves 1.0; tit26 declares 0.132 but resolves 1.0.» [result]
- **Tags**: reference-resolvability, external-validation, tier-B, construct-validity, self-falsification

## C08: v3's extractive_fidelity catches a fabricated forest-plot statistic in che26 that GRO's ledger-consistency metrics score as clean
- **Statement**: v3's `extractive_fidelity` = 0.625 for che26 catches a fabricated forest-plot statistic (MD = 0.10, 95% CI 0.04–0.16) that appears nowhere in the source paper. GRO's `quantity_reconciliation_rate` = 1.0 and `entailment_precondition_rate` = 1.0 for the same ARA — both clean — because those metrics only check the ledger against its own quote and never touch the source PDF.
- **Status**: supported
- **Falsification criteria**: A re-verification of che26's forest-plot statistic against the original source paper showing the MD = 0.10 (95% CI 0.04–0.16) figure is in fact present in the source (i.e. not fabricated).
- **Proof**: [E06]
- **Evidence basis**: §4 ("3.3 Agreement and divergence," "Sharpest divergence — che26").
- **Dependencies**: [C06]
- **Sources**:
  - `v3 extractive_fidelity = 0.625, fabricated MD=0.10 (CI 0.04-0.16); GRO quantity_reconciliation_rate=1.0, entailment_precondition_rate=1.0` ← compare/gro_vs_v3.json / §4 «v3 `extractive_fidelity` = 0.625 catches a **fabricated forest-plot statistic** (MD = 0.10, 95% CI 0.04–0.16) that appears nowhere in the source. GRO scores this same ARA `quantity_reconciliation_rate` = 1.0 and `entailment_precondition_rate` = 1.0 — clean — because those metrics only check the ledger against its own quote and never touch the PDF.» [result]
- **Tags**: fidelity, che26, v3-vs-GRO, divergence, source-verification

## C09: ard25 is the sole ARA where GRO, v3, and Seal independently agree it is worst, and the cause is genuine structural breakage
- **Statement**: ard25 is ranked worst by all three instruments (GRO health 0.000, v3 trust 0.150, Seal overall 3.0 / "Reject"), converging on the same underlying defect: a missing `logic/experiments.md` file that produces `broken_ref_integrity` = 16/16 (100% of proof_refs) in GRO and a "dangling reference" verdict in Seal's D5 (Exploration Integrity = 1).
- **Status**: supported
- **Falsification criteria**: Restoring ard25's missing `logic/experiments.md` file and rerunning all three instruments; if GRO health, v3 trust, and Seal overall no longer converge on ranking it worst among the 12, the claim of genuine (rather than compilation-artifact) breakage is undermined for the metric level but the three-way agreement finding itself would need re-examination.
- **Proof**: [E07]
- **Evidence basis**: §4.4 ("The single point of three-way agreement is **ard25**") and §4.5 (divergence table, ard25 row); §3.3 (also flagged, broken_ref_integrity).
- **Dependencies**: [C05]
- **Sources**:
  - `GRO 0.000, v3 0.150, Seal 3.0 Reject` ← seal/ard25-response-of-spatially-defined-microglia-states.json, compare/gro_vs_v3.json / §4.1 scorecard table, ard25 row: «ard25 | 4 | 3 | 4 | 4 | 1 | 2 | 3.0 | **Reject** | 0.000 | 0.150» [result]
  - `broken_ref_integrity = 16/16 due to missing logic/experiments.md` ← results.json / §3.3 «`broken_ref_integrity` is 100% concentrated in one ARA (ard25 = 16/16); ard25's own diagnostics attribute this to a missing `logic/experiments.md` file, not genuinely broken citations» [result]
- **Tags**: ard25, three-way-agreement, structural-breakage, convergence

## C10: The genre_silent_omissions metric has a formula defect that produces a nonsensical negative value
- **Statement**: `genre_silent_omissions` is computed as `count(expected) − count(present) − count(absent_declared)`, which can go negative when a genre's `present_slots` includes a slot outside its own `expected_slots` list — observed for zho25, which scores −1.
- **Status**: supported
- **Falsification criteria**: A corrected formula (or corrected `present_slots`/`expected_slots` enum alignment) rerun on zho25 that no longer produces a negative value while preserving the metric's intended meaning; failure to reproduce the −1 value on a fresh rerun.
- **Proof**: [E08]
- **Evidence basis**: §3.3 ("Also flagged (construct-validity concerns)"), first bullet.
- **Dependencies**: none
- **Sources**:
  - `zho25 = −1` ← results.json / §3.3 «**`genre_silent_omissions`** has a documented formula bug: `count(expected) − count(present) − count(absent_declared)` can go **negative** (zho25 = −1) when a genre's `present_slots` includes a slot outside its own `expected_slots` list.» [result]
- **Tags**: genre_silent_omissions, formula-defect, construct-validity, zho25
