# The metrics — reward what citations punish

*The incentive-design program that motivates GRO. Metrics are the entry point: they are the lever (nothing changes until what counts changes) and the diagnostic (trying to compute good metrics reveals what the record must be). GRO is the substrate this inquiry demanded — see [`SPEC.md`](SPEC.md).*

The full program lives in [`metrics/`](metrics/); the design tournaments that produced it are in [`metrics/tournaments/`](metrics/tournaments/). This page is the landing point.

## The thesis

Citations are a Goodharted proxy: they reward *citable* work (reviews, positive results) and are structurally blind to negative results, replications, refutations, and reuse. The goal is to measure — and let funders reward — that invisible labor, defended against gaming not by one clever number but by a **diversity of independent signals** and a process where no metric is graded by its own author.

## Seven directions

1. reproducibility & specification completeness
2. claim & evidence integrity
3. process transparency & **negative knowledge** — dead-end density, failure-knowledge preservation, negative-result share
4. novelty & dependency structure, incl. a **corrective-science score** weighting refutations above imports
5. ★ the **cross-library claim graph** — a knowledge graph whose edges are *evidential* (corroboration, contradiction, replication depth, reuse) rather than social; the direct alternative to the citation network
6. real-world grounding (trial registries, chemical databases, datasets)
7. representation quality as a trust weight

Detail: [`metrics/directions.md`](metrics/directions.md).

## The negative result (why this reframed the program)

Running 64 candidate indicators over a structured corpus produced the headline finding:

> **metrics computed over a record's own structure measure the fidelity of the record, not the quality of the science.**

A well-compiled record of bad science and of good science were indistinguishable; zero of six paper-level rankers survived; genuine signal appeared only at the claim level, anchored to external ground truth. Full write-up: [`metrics/findings.md`](metrics/findings.md). This is what forced the substrate question — see [`methods/affordance-gap.md`](methods/affordance-gap.md).

## The ideal metrics (TOP 10)

The highest-signal survivors of the tournaments, tagged by the rigor tier each can honestly reach — **[det]** deterministic join · **[anc]** reliable given an external resolver · **[jud]** calibrated judge, forever. (Ledger: [`metrics/candidates.md`](metrics/candidates.md); rigor-class catalogue: [`SPEC.md`](SPEC.md) §4.)

| # | Metric | Reaches | What it rewards that citations can't |
|---|---|---|---|
| 1 | Reference-landscape completeness | **[anc]** | citing the true neighborhood incl. contradicting work; not missing what a search agent finds |
| 2 | Novelty vs the literature | **[anc][jud]** | "done before?" for claim/insight/gap/method, resolved not asserted |
| 3 | Claim drift / reference truthfulness | **[anc][jud]** | whether cited sources actually support what they're cited for |
| 4 | Claim ↔ experiment ↔ evidence entailment (+ publication-bias) | **[det+jud][anc]** | does the evidence entail the claim given its type; registry outcome-switch flag |
| 5 | End-to-end reproducibility bundle | **[det]** | figure + data + code co-exist and cross-link (presence/linkage, not execution) |
| 6 | Multi-perspective triangulation | **[det+jud]** | corroboration across genuinely independent lenses vs one pipeline relabeled |
| 7 | Assumption realism & limitation validity | **[jud]** | realistic load-bearing assumptions; limitations that add real conditions |
| 8 | Method validity & verification status | **[jud]** | sound, accepted method vs over-generalized stretch |
| 9 | Controlled-vocabulary & latent-space anchoring | **[anc]** | terms/data anchored to ontologies/canonical datasets → cross-record interop |
| 10 | FOL-ability | **[det+jud]** | a clean first-order-logic graph over the claims (contradiction/scope checkable) |

Plus three flagships the top-10 presupposes:

- **the cross-library evidential claim graph** — every metric above is a query over it; the structural alternative to the citation network.
- **negative-knowledge density** — dead-end density and whether an abandoned path carries enough context to save the next lab. Citations can't see a dead end at all.
- **the corrective-science score** — replications and refutations weighted *above* imports; the cleanest inversion of the citation incentive.

## Where existing efforts fall short

Three efforts, three orthogonal axes, none calibrated against the others, none covering the reward-what-citations-punish set:

- **citations** → social attention (Goodharted, blind to the above).
- **the ARA-style rigor seal** → internal *integrity* (coherent, falsifiable, grounded) as one LLM grade; never asks "is it novel / does it matter"; calibrated to nothing external. (Comparison: [`metrics/verifier-comparison.md`](metrics/verifier-comparison.md).)
- **LENS / the Metascience Novelty Indicators Challenge** → *novelty*, externally calibrated to expert ratings — but only novelty, and it reads whole papers, not a structured record. (Positioning: [`metrics/novelty-comparison.md`](metrics/novelty-comparison.md).)

The gap is a **substrate** gap first — most of the ideal set can't be computed until the record carries the right shapes. That is what GRO is for.

## First discrimination result (2026-07 — the experiment below has now been run)

The open test was run on one axis — **breakthrough-ness** — over 66 recent + 72 historical (2004–2010) Alzheimer's papers ([`experiment/breakthrough/`](experiment/breakthrough/)). It is the program's first contact with external ground truth, and the result is sobering and reported in full:

- The one signal that carries is the **L8 contribution-typing** (metric #2's substrate), aggregated as `max(peak, cwmean)`. The prior-art `overlap`/`sota_anchor` axis (metric #2's novelty half), the delta ledger, and genre added **no transferable signal**.
- Its measured skill **collapses as the LLM is removed from the ground truth**: ρ≈**0.58** vs a same-model LLM expert panel (held-out) → ρ≈**0.34** vs an *independent* model family (≈⅓ was shared-method bias — the lean flips when the metric is built by the other model, Steiger p=0.003) → ρ≈**0** vs a *real-world, LLM-free* ground truth (mature citation-disruption of the historical papers over 15–20 years; 95% CI [−0.38, +0.14]).
- So the metric flags **LLM-perceived contribution depth**, which is *not shown to be* field-reshaping impact. This is the §"negative result" one level up: structure-derived metrics measure the record's fidelity, and here even an externally-anchored novelty attempt, when its ground truth is finally the real world, does not discriminate.
- **Caveat (honest):** the historical test used abstract-only typing (full text is paywalled for that vintage — an access wall that is itself a finding), which compresses the predictor's variance and makes this a *weak* test — a null on a weak test, not proof of zero. A full-text, multi-domain historical corpus is the sharpening move.

Full write-up: [`experiment/breakthrough/RESULTS_PAPER.pdf`](experiment/breakthrough/RESULTS_PAPER.pdf). SPEC §7a records the same status against the shape.

## Steps forward

1. **emit the shapes** so the [det] tier computes (the GRO typed sidecars — done for the corpus above).
2. **build the resolvers** for the [anc] tier (literature index, registries, ontologies).
3. **stand up calibration** sets + judge ensembles for the [jud] tier — and prefer **cross-model or real-world** ground truth over a same-family LLM panel (the shared-method-bias lesson above).
4. **sharpen the discrimination test**: full-text (not abstract-only) historical compile across multiple domains and vintages, trained against real disruption rather than only correlated — the one move that could turn the current null into signal, or confirm it.

## How the metrics were built (tournaments)

Two blind, adversarial tournaments so no metric is graded by its author. **Round 1** (per artifact surface): four clean-room proposers → judge picks two → critique → one winner, across all 11 surfaces. **Round 2** (per metric, from the TOP-10 ledger): `4 → 2 → 1` with three refine cycles. Winners, judge critiques, and the full field are in [`metrics/tournaments/`](metrics/tournaments/) — round-1 summary at [`metrics/tournaments/round1-summary.md`](metrics/tournaments/round1-summary.md).
