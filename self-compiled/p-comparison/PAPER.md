---
title: "Three Ways to Judge an Agent-Native Research Artifact: A metascience comparison of GRO ideal metrics, an ARA-inferred metric design (v3), and a semantic verifier (Seal Level 2) over 12 compiled ARAs"
authors: [dasmodel research]
year: 2026
venue: "internal research paper"
ara_version: "1.0"
grounding: full-text (own research output; source = COMPARISON_PAPER.md + benchmark.json/results.json/compare/*.json/external_validation.json/seal/*.json)
domain: "Metascience / evaluation methodology for Agent-Native Research Artifacts (ARAs), Alzheimer's disease corpus"
keywords: [ARA evaluation, GRO metrics, Seal Level 2, extractive fidelity, semantic verification, substrate benchmark, Spearman correlation, deterministic metrics, external validation]
claims_summary:
  - "The GRO typed-graph extension makes 4 of 8 metrics computable that have no expression at all on raw ARA prose."
  - "On the 4 metrics expressible on both shapes, typing changes values materially and can reduce fidelity against external ground truth (prose MAE 0.31 vs typed MAE 0.44 on reference resolvability)."
  - "Typed-field lookups are ~100x faster and bit-identical on rerun versus prose parsing."
  - "GRO metrics beat Seal L2 on coverage (12/12 vs 12/12-but-costly), determinism, and cost (0 vs ~66k LLM tokens/ARA); Seal reaches semantic judgments GRO cannot."
  - "Seal's overall score is statistically uncorrelated with GRO structural health (rho=-0.011) and v3 artifact-trust (rho=0.035), while GRO and v3 correlate strongly with each other (rho=0.678, p=0.015)."
  - "v3's LLM-dependent design fully scores only 3/12 ARAs (25%) versus GRO's 12/12 (100%) - an architectural reach gap."
  - "GRO's own reference_resolvability_rate metric is falsified by its own externally anchored PubMed check (declared mean 0.5197 vs observed 0.9583)."
  - "v3's extractive_fidelity catches a fabricated forest-plot statistic in che26 (MD=0.10, CI 0.04-0.16) that GRO's ledger-consistency metrics score as clean (1.0/1.0)."
  - "ard25 is the sole ARA where all three instruments independently agree it is worst, due to genuine structural breakage (missing logic/experiments.md)."
  - "The genre_silent_omissions formula has a defect that produces a nonsensical negative value (zho25 = -1)."
abstract: "We compare three approaches to evaluating Agent-Native Research Artifacts (ARAs) over a fixed corpus of 12 ARAs in the Alzheimer's disease / neurodegeneration domain: (1) GRO ideal metrics - eight deterministic metrics over the typed ARA graph plus four externally anchored/judged checks; (2) v3, the first ARA-inferred metric design (extractive_fidelity, six paper_rankers, composite artifact_trust); (3) Seal Level 2, a calibrated semantic reviewer scoring six epistemic dimensions. The approaches differ enormously in reach (GRO 12/12, v3 fully scores 3/12, Seal 12/12 but at high LLM cost) and measure near-orthogonal constructs (Seal overall vs GRO health rho=-0.011; Seal vs v3 trust rho=0.035; GRO vs v3 rho=0.678, p=0.015). The primary result is a substrate benchmark: (H1) the GRO typed-graph extension vs raw ARA prose with metric logic held constant, and (H2) GRO metrics vs the Seal verifier. The extension's value is affordance, cost, and determinism, not fidelity on metrics the ARA prose already encodes; the verifier is complementary to, not beaten by, the deterministic metrics. No single approach discriminates good science from bad science alone. Limitations: anchored/judged evidence exists for only half the corpus (the biomarker/trial cluster), there is no external good-vs-bad ground-truth set, and n=12 in a single sub-domain."
---

# Three Ways to Judge an Agent-Native Research Artifact

> **Grounding note: full-text, self-authored.** This ARA compiles `research/metrics/v4-gro/COMPARISON_PAPER.md`, one of our own metascience outputs, treating its reported findings as claims. Every number below is copied verbatim from the paper's text/tables; the underlying computed artifacts it draws on (`benchmark.json`, `results.json`, `compare/gro_vs_v3.json`, `compare/vs_seal.json`, `compare/gro_metrics_analysis.json`, `external_validation.json`, `external/*.json`, `seal/*.json`) live alongside the paper in `research/metrics/v4-gro/` and are pointed to (not re-derived) in `evidence/README.md`.

## Overview

This paper runs a three-way metascience comparison of instruments for judging Agent-Native Research Artifacts (ARAs) over a fixed 12-ARA corpus of Alzheimer's-disease/neurodegeneration papers: **GRO ideal metrics** (deterministic + reliable-anchored + reproducible-judged, Tier A/B/C), the earlier **v3 ARA-inferred metric design** (extractive_fidelity + paper_rankers + artifact_trust), and the **Seal Level 2 semantic verifier** (six epistemic dimensions, D1-D6).

The paper's primary result (its "substrate benchmark," §2) is not "GRO vs v3" but two sharper questions run directly via `benchmark.py`/`benchmark.json`: **H1** - does the GRO typed-graph extension beat the raw ARA prose shape when the metric logic is held constant? **H2** - how do the GRO metrics stand against the Seal verifier? The extension wins on affordance (4/8 metrics only exist on the typed shape), cost, and determinism (~100x faster, bit-identical), but does **not** win on fidelity for the metrics the raw ARA prose already expresses - on the one construct with external ground truth, raw prose is closer to PubMed truth than the typed sidecar. Against Seal, GRO wins coverage/cost/auditability while Seal alone reaches semantic judgments (scope calibration, argument coherence, conflict-of-interest) that no structural field encodes.

The paper's second-order results (§3-§5) rank GRO's own metrics by reliability, hold GRO against the older v3 design (an architectural reach gap: v3 fully scores 3/12 ARAs vs GRO's 12/12), and hold both against Seal L2, finding the three instruments' scores are **near-orthogonal**: Seal's overall score is statistically uncorrelated with GRO structural health (Spearman rho = -0.011) and with v3 artifact-trust (rho = 0.035), while the two structural instruments (GRO, v3) correlate strongly with each other (rho = 0.678, p = 0.015). The one point of three-way agreement is ard25, a genuinely structurally broken ARA every instrument independently ranks worst. The paper concludes the three tiers are complementary, not competing, and stops short of claiming any of them discriminates good science from bad science in general, given the corpus has zero known-bad papers.

## Layer Index

### Cognitive Layer (`/logic`)
| File | Description |
|------|-------------|
| [problem.md](logic/problem.md) | Observations (O01-O08) and gaps (G01-G05) the paper addresses: reach differences, orthogonal constructs, no discrimination test, half-corpus anchoring, single-domain n |
| [claims.md](logic/claims.md) | 10 falsifiable claims (C01-C10) covering the substrate benchmark (H1/H2), the metric-reliability ranking, the v3 reach gap, the three-way correlation structure, and the sharpest catch-divergences |
| [experiments.md](logic/experiments.md) | 8 experiment/analysis blocks (E01-E08) matching the Proof refs in claims.md |

### Evidence (`/evidence`)
| File | Description |
|------|-------------|
| [README.md](evidence/README.md) | Pointer to the underlying computed artifacts in `research/metrics/v4-gro/` (results.json, benchmark.json, compare/, external/, seal/, figures/) that back the paper's numbers |
