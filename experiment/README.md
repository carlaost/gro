# experiment/ — empirical tests of the GRO idea

Three connected experiments over the same corpus of compiled ARAs, each with a short paper. Together they move from "can we type the record" → "does the typed record validate against the world" → "how do the three ways of judging an ARA compare."

## 1. Deterministic-tier computability (`gro_metrics.py`, `results.json`, `gro-experiment-paper.*`)
Generated GRO deterministic-tier typed sidecars for 12 compiled ARAs and computed the eight Tier-A metrics over them (pure structural joins, no LLM/network). **Result:** typing the record converts prose-blocked metrics into deterministic joins; `broken_ref_integrity` caught a real structural defect. Numbers independently re-run and verified. See `gro-experiment-paper.pdf`. Extensions per ARA are in `extensions/<slug>/`.

## 2. External-ground-truth validation (`external-validation/`)
The anchored + judged tiers, run against **real** sources via live tools (ClinicalTrials.gov + PubMed): reference resolution, trial-registry outcome concordance (the two donanemab papers → NCT04437511), prior-literature novelty, retraction checks. Raw evidence per ARA in `external-validation/evidence/`. **Sharpest result:** the deterministic `reference_resolvability_rate` (declared corpus mean 0.52) is *falsified* by the anchored check (observed 0.96) — the self-declared metric measures DOI-capture completeness, not real verifiability. The external-validation half of the spec's §7.1 experiment; a full good-vs-bad discrimination test still needs a labelled contrast set (this corpus has no known-bad papers). See `external-validation/gro-external-validation-paper.pdf`.

## 3. Three-way comparison (`comparison/`) — the capstone
Over the same 12 ARAs, three ways to judge an ARA held side by side: **(a) GRO ideal metrics** (best vs most uncertain), **(b) the first ARA-inferred metric design (v3)**, **(c) the ARA verifier / Seal L2** six-dimension review. Full paper with tables + four figures: **`comparison/gro-comparison-paper.pdf`** (13pp). Per-ARA Seal reviews in `../seal/`; the three parallel analyses in `comparison/analyses/`; figures in `comparison/figures/`.

**Headline findings:**
- **Coverage is architectural.** GRO scores 12/12 ARAs and Seal reviews 12/12, but the v3 first design is `rank_eligible` on only **3/12** — its paper-quality signals gate on a full-text re-read that most ARAs don't support. Typing the record makes metrics uniformly computable.
- **The three are complementary, not competing.** Deterministic (GRO Tier A) = auditable structural fact; anchored (PubMed/registry) = reliable external check; judged (Seal) = calibrated human-like verdict. Each catches what the others miss — e.g. Seal's D3 flags che26's over-generalization (C05) where GRO `overclaim_flags` = 0; GRO's `broken_ref_integrity` = 16 gives ard25 an auditable count where v3 only has a boolean.
- **They converge on the extremes.** ard25 is "structurally worst" on all three (Seal Reject 3.0, GRO broken_ref 16, v3 trust 0.15); the p-tau217/donanemab cluster scores high across the board.
- **None discriminates good-from-bad alone**, and the corpus contains no known-bad papers — the standing limit the whole program names.

Figures: coverage bar, GRO metric heatmap, Seal-dimension heatmap, three-way concordance scatter (colour = Seal recommendation, size = GRO issue count).
