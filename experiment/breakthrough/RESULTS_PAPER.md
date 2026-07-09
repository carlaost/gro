# Measuring breakthrough-ness on new papers — how far a GRO metric gets, and the ceiling above it

*Written 2026-07-09 (v2, supersedes the 2026-07-08 draft). Companion to `breakthrough-metric.md` ("Do we have a scientific-breakthrough metric? — assessment + design"), which argued no metric in the program measures breakthroughs, decomposed "breakthrough" into three signals (disruption / significance / realized uptake), and named three blockers.*

## Abstract

We asked whether a metric computed over GRO's structured sidecars can rank recent papers by breakthrough-ness the way domain experts do. We GRO-compiled **66 recent (2025–2026) Alzheimer's papers**, rated each with a blind, prior-art-grounded **3-persona expert panel** (0–100), and searched for the best metric — including via a 16→4→2→1 design tournament — under a strict **held-out train/test split**.

Three results, in order of importance:

1. **We are far from the ceiling, and the ceiling is measurable.** A single expert judge predicts the panel at **ρ ≈ 0.97** (leave-one-judge-out) — that is the best any predictor could do. Our best metric reaches **ρ ≈ 0.57** on held-out papers. So the metric captures **~59% of the achievable rank signal**; ~40 points of correlation are lost between *reading the paper* and *the GRO feature vector*. **We have not hit a ceiling** — and the residual gap is *structured* (specific paper genres the features cannot see), not noise, so a better data shape can genuinely close it.

2. **The simplest metric wins; complexity overfits.** The best metric is a **single feature** — the compiler's mean assessed contribution-novelty (`contrib_wmean`), ρ ≈ 0.57 held-out with *no* train→test gap. Every richer formula the tournament produced climbed the training score and failed to transfer (winner: 0.77 train → 0.53 test). The shipped composite manages only ρ ≈ 0.30.

3. **The generalizing signal is the compiler's reading of the paper — not the "GRO-native" machinery.** The prior-art anchor and delta-ledger shapes we invested most in did not transfer. This is either a real finding (contribution-typing is what matters) or a warning that our LLM metric and our LLM panel share a bias — distinguishable only on a second corpus.

The honest deliverable: a **one-feature triage metric** at 0.57, a **measured ceiling** at 0.97, and a precise list of the three GRO extensions — a normalized genre field, a clean anchor-confidence field, and a downstream-stance edge — needed to climb toward it.

---

## 1. Features and metrics — definitions (read this first)

Every metric below is deterministic arithmetic over per-paper GRO sidecars. What matters is that the sidecars come from **three sources with different epistemic status** — conflating them is the shipped metric's core error.

**Provenance tags used throughout:**
- **[PAPER→LLM]** — the compiler read *this paper's text* and made a typed judgment. Not externally verified; blind to what happened after publication.
- **[PRIOR-ART]** — resolved against *earlier* literature (the paper's references + an OpenAlex search for pre-publication near-neighbors).
- **[FOLLOW-ON]** — from *later* papers citing this one (the citation graph).

**The features** (each defined on first use; full dictionary in `corpus/FEATURES.md`):

| feature | provenance | definition |
|---|---|---|
| `contribution` | [PAPER→LLM] | composite `0.6·peak + 0.4·wmean` over the paper's typed contributions |
| `contrib_wmean` | [PAPER→LLM] | **confidence-weighted _mean_ novelty weight across a paper's contributions.** Each contribution is typed by the compiler from a closed taxonomy (`new_paradigm` 1.0 … `replication` 0.1); wmean is a *mean*, so it cannot be inflated by padding a paper with shallow contributions. **This is the winning metric.** |
| `contrib_peak` | [PAPER→LLM] | the single strongest `weight × confidence` contribution ("does it have ≥1 landmark result?") |
| `n_contribs` | [PAPER→LLM] | raw count of contributions (breadth; gameable) |
| `n_puffery` | [PAPER→LLM] | contributions voided by the anti-puffery lock (claimed but not tied to a real claim) |
| `delta` / `delta_max` / `n_deltas` | [PAPER→LLM, baseline PRIOR-ART] | the paper's quantified comparisons-vs-prior-work: composite / largest magnitude / count |
| `anchor_mean_overlap` | [PRIOR-ART] | mean overlap of the resolved prior-art neighborhood — **high = dense prior art (incremental); low = sparse (novel).** `(1 − overlap)` is a novelty signal |
| `anchor_max_overlap` | [PRIOR-ART] | overlap of the single closest prior work (near-duplicate detector) |
| `anchor_n` | [PRIOR-ART] | how many prior works resolved (doubles as a resolution-confidence proxy) |
| `anchor` | [PRIOR-ART] | composite scoring *resolution success* (a known-buggy field: rewards that the neighborhood resolved, not its density) |
| `uptake_per_year` / `cd_index` | [FOLLOW-ON] | age-normalized in-corpus citations / disruption index — **structurally dead on a 2025–2026 corpus** (no downstream edges yet) |

**Key definition — "contribution."** `contributions.yaml` is the compiler's answer to *"what does this paper claim to contribute, and how novel is each claim on its face?"* Each entry is **double-typed**: `author_framed_type` (the authors' pitch) vs `compiler_assessed_type` (the compiler's own call), with a rationale and an anti-puffery lock. So `contrib_wmean` measures **the compiler's reading of the paper's stated contributions, in isolation** — reproducible and auditable, but a judgment, never checked against how the field reacted. That distinction drives every result.

## 2. Corpus and method

- **Corpus:** 66 recent (2025–2026) Alzheimer's papers in `research/ara-library/`, each GRO-compiled with L8 sidecars; **all 66 SOTA anchors genuinely resolved** (references + live OpenAlex), verified via `corpus/audit_l8.py`.
- **Ground truth — prior-art-grounded expert panel.** Each paper rated 0–100 by three blind personas (clinical trialist, molecular neuroscientist, metascience analyst). Each judge received a **prior-art reading list** — the titles/years of the paper's resolved precedence neighborhood, but **not** the metric's overlap *scores* (to avoid circularity with the anchor feature) — and rated *advance beyond that specific prior art*. Score = **mean** of the three judges (mean, not median, so a lone dissenting judge counts). Raw votes in `corpus/expert_votes_raw_grounded.json`.
- **Held-out evaluation.** 40 train / 26 test, stratified by expert score (`corpus/split.json`). Formula search (including the tournament) happens on **train only**; the test set is scored **once**, by the organizer, via `corpus/apply_formula.py`. No test information ever entered the design loop.
- **Grounding sanity-check.** Re-judging with vs without the prior-art brief agreed at ρ = 0.97 on rank but deflated borderline scores (mean 29.6 → 24.7) — SOTA context makes judges correctly harsher on work that only *sounds* novel. So the grounded panel is the right target.

## 3. The shipped metric is weak, for a diagnosable reason

`significance = 0.40·contribution + 0.40·delta + 0.20·anchor` reaches only **ρ ≈ 0.30** (all 66). Per-feature correlation with the grounded panel shows it is worse than its own best part:

| feature | ρ vs experts |
|---|---|
| `contribution` / `contrib_wmean` | **+0.57 / +0.56** (the real signal) |
| `contrib_peak` | +0.46 |
| `anchor_n` | +0.35 |
| `anchor` (composite) | +0.20 |
| `delta` / `delta_max` / `n_deltas` | −0.09 / −0.09 / −0.15 |
| `anchor_mean_overlap` / `anchor_max_overlap` | −0.39 / −0.49 |
| `uptake_per_year` / `cd_index` | −0.03 / −0.08 (dead) |

80% of the composite's weight is on `contribution + delta`, and `delta` points the wrong way. Strip to the one good component and it roughly doubles.

## 4. The tournament, and the overfitting it exposed

A **16→4→2→1 critique-carrying tournament** (`tournament16_workflow.js`): 16 clean-room contestants (Sonnet) each designed a formula, hill-climbing on the train split; a judge critiqued residuals and advanced the strongest; every later round saw the critiques. It converged on a principled-looking winner (`depth × novelty × resolution-confidence`). Then we scored everything on the **held-out test** — the paper's core table:

| metric | train (40) | **held-out test (26)** | all (66) |
|---|---|---|---|
| **plain depth** `0.5·peak + 0.5·wmean` | 0.546 | **0.572** | 0.569 |
| **`contrib_wmean` alone (1 feature)** | 0.533 | **0.571** | 0.564 |
| tournament winner (depth×novelty×conf) | 0.771 | 0.534 | 0.687 |
| depth × novelty (no gate) | 0.693 | 0.455 | 0.604 |
| v1 draft (depth − delta report-tells) | 0.712 | 0.449 | 0.641 |
| novelty alone (`1 − max_overlap`) | 0.627 | 0.266 | 0.494 |
| shipped `significance` | 0.141 | 0.503 | 0.304 |

Read the train-vs-test columns: **plain depth has no gap (0.55→0.57); every elaboration has a large one.** The tournament, by optimizing train ρ, walked into overfitting 40 points. Its real result is *negative*: the added machinery does not generalize.

**Honesty note on models (as requested).** Contestants ran `claude-sonnet-5` (verified from transcripts). The judges were requested as Fable but **silently fell back to `claude-opus-4-8`** (the `'fable'` alias didn't resolve; it needs `'claude-fable-5'`). Moot for the conclusion — the *selected* winner loses to a one-feature baseline on held-out data regardless of who selected it.

## 5. The adopted metric

**Use `contrib_wmean`** (the compiler's confidence-weighted mean assessed contribution-novelty): **ρ ≈ 0.57 vs grounded experts on held-out papers, with no overfitting.** Even across persona (trialist / neuroscientist / metascientist ≈ 0.5–0.57). It ranks real discoveries on top and floors every annual report and burden re-estimate. A usable **triage prior**, not an oracle. (A rank correlation on n=26 has a wide CI, so plain depth does not *significantly* beat the elaborate metrics — but that is the argument: if machinery can't beat one feature on unseen data despite fitting train harder, it isn't justified.)

## 6. How far from the experts — the ceiling (the headline)

The right yardstick is not zero, it is **how well the experts predict each other.** Leave-one-judge-out — one persona predicting the mean of the other two — gives the best score any predictor could achieve given panel noise:

| | ρ |
|---|---|
| **Ceiling** (single judge → panel) | **0.97** |
| Our best metric (`contrib_wmean`, held-out) | **0.57** |
| Shipped composite | 0.30 |

**We are at ~59% of the achievable ceiling — not near it.** The ~0.40 gap is the information lost between reading the paper and the GRO feature vector. And it is **structured**, not noise — the biggest metric-vs-expert disagreements cluster on genres the features cannot distinguish:

- `sal26` (plasma-tau biomarker): experts 61, metric floors it — a real advance the compiler under-typed.
- `kes25` (diagnosis review): experts 31, metric ranks it *last* — reviews the field values.
- `cum26` / `wan25c` (drug-pipeline review, burden re-estimate): experts ~6, metric over-rates them — pure genre confusion.

Because the errors are systematic, better data shapes can close the gap. This is not a wall.

## 7. Why the winner is principled — the sign-flip point

The v1 draft subtracted `delta`. That was theoretically wrong, not just weak. A negatively-correlated feature may be sign-flipped only if it is a **true inverse construct** (`1 − overlap` = novelty: causal, generalizes) — not if it is a **confound proxy** (`n_deltas` correlates with breakthrough only because report-genre papers pile up deltas *in this corpus*). Test: *would intervening on the feature causally change breakthrough-ness?* Adding a quantified comparison to a real discovery should not lower its score — so `delta` must not be subtracted. The held-out numbers confirm the theory: the delta-hack underperforms doing nothing.

## 8. How GRO needs to be extended — to climb toward 0.97

All 16 contestants independently reported the substrate is missing signals the ideal metric needs. The 38 proposals cluster into three asks, and §6's residuals say which would help most:

1. **A normalized `genre.primary` on every paper** (19 proposals) — *highest confidence.* The metric's worst errors (`cum26`, `kes25`, `wan25c`) are genre confusions. GRO emits `genre.yaml` but inconsistently schematized (some papers carry `genre.primary` + `novelty_prior`, most only free-text `paper_type`). A controlled vocabulary (`primary_research | surveillance_report | review | trial_readout | method_paper`) on all papers would let a metric detect genre *directly* instead of laundering it through delta-counts.
2. **A `downstream_assessment` / stance edge** (4 proposals) — *highest ceiling, slowest.* Per-citer: does later work *confirm/extend* vs *contest/supersede/fail-to-replicate*? The substrate has citation *counts* (dead) and the compiler's *untested* reading, but nothing for **how the field reacted** — the materialized "cross-object contribution graph" (observation O31), and the only path to measuring *realized* impact and to breaking the shared-LLM-bias worry (§9).
3. **A standalone `anchor_resolution_confidence ∈ [0,1]`** (14 proposals) — *marginal.* Splits resolution-success from the buggy density reward in `anchor`; the winner had to repurpose `anchor_n` for lack of it.

## 9. The caveat that outranks the extensions

Our signal (`contrib_wmean`, an LLM's reading) and our target (an LLM panel — inter-judge ρ ≈ 0.96, implausibly high for independent humans) **may share a model bias.** The 0.57 might be two LLMs agreeing with themselves rather than a transferable notion of breakthrough. We cannot tell on this data. Before building any extension, the cheap decisive test is: **run `contrib_wmean` against a second, non-AD corpus, ideally with a few human ratings.** If 0.57 holds, the metric is real and the genre/stance extensions are worth building; if it collapses, we have been measuring an echo.

## 10. Where this leaves the program

The assessment paper said "no metric measures breakthroughs, and we can't compute one on the current shape." This sharpens it: **the shipped composite is weak (0.30); the best available metric is a single contribution-depth feature (0.57 held-out); the achievable ceiling is 0.97; and the ~0.40 gap is structured signal a better data shape can attack — starting with a normalized genre field.** Enriching the metric with GRO's prior-art/delta machinery overfits and is not recommended. Next: validate on a second domain against human raters, then build `genre.primary`.

---

### Reproduction
All under `research/metrics/v5-breakthrough/`: `corpus/compute_corpus.py` (features → `corpus_scored.json`), `corpus/FEATURES.md` (dictionary), `gro_extend_workflow.js` (anchor resolution), `expert_panel_sota_workflow.js` + `corpus/briefs/*` (grounded panel), `corpus/split.json` (40/26), `tournament16_workflow.js` → `corpus/tournament16_result.json`, `corpus/apply_formula.py "<formula>" --split train|test|all` (reproduces every ρ in §4/§6). All correlations recomputed from raw data by the organizer; models read from transcripts (Sonnet contestants, Opus judges).
