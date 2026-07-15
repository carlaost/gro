# Measuring breakthrough-ness on new papers — how far a GRO metric gets, and the ceiling above it

*Written 2026-07-09 (v2, supersedes the 2026-07-08 draft). Companion to `breakthrough-metric.md` ("Do we have a scientific-breakthrough metric? — assessment + design"), which argued no metric in the program measures breakthroughs, decomposed "breakthrough" into three signals (disruption / significance / realized uptake), and named three blockers.*

## Abstract

We asked whether a metric computed over GRO's structured sidecars can rank recent papers by breakthrough-ness the way domain experts do. We GRO-compiled **66 recent (2025–2026) Alzheimer's papers**, rated each with a blind, prior-art-grounded **3-persona expert panel** (0–100), and searched for the best metric — including via a 16→4→2→1 design tournament — under a strict **held-out train/test split**.

**Headline (§10):** the strongest test removes the LLM from the ground truth — 72 historical (2004–2010) papers, metric computed at publication time, validated against what the field *actually did* (mature citation disruption over 15–20 years). The metric shows **no reliable predictive power** (ρ near zero, sign-unstable). Against a same-family LLM panel the same metric scored ρ ≈ 0.58; against reality, nothing. Everything below explains how we got there and why.

Findings, in order of importance:

1. **We are far from the ceiling, and the ceiling is measurable.** A single expert judge predicts the same-family panel at **ρ ≈ 0.97** (leave-one-judge-out); two *different* model families (Claude, GPT-5.5) agree at **ρ ≈ 0.89**. Our best metric reaches ρ ≈ 0.58 against the same-family panel but only **ρ ≈ 0.34 against the independent model** (§3, §9). So even against the more honest cross-model target the metric captures well under half the achievable signal. **We have not hit a ceiling** — the gap is structured, not noise.

2. **The simplest metric wins; complexity overfits.** The best metric is a **single feature** — the compiler's assessed contribution-novelty, adopted as `max(peak, cwmean)` (§5) — held-out ρ ≈ 0.58 vs the Claude panel with *no* train→test gap. Every richer formula the tournament produced climbed the training score and failed to transfer (winner: 0.77 train → 0.53 test). The shipped composite manages only ρ ≈ 0.30.

3. **The generalizing signal is the compiler's reading of the paper — and it is partly shared-model bias.** The one feature that transfers, `contrib_wmean`/`max(peak,cwmean)`, is the ARA compiler's (Claude's) typing of the paper's contributions. We tested the bias worry directly by re-judging all 66 papers with a **different model family (GPT-5.5)**. Two findings: (a) the *ground truth is robust* — the GPT and Claude panels agree at **ρ ≈ 0.90**, so breakthrough ranking is largely model-independent, not a Claude artifact; but (b) the *metric's headline number is inflated* — it agrees with the same-family Claude panel at ρ ≈ 0.53–0.58 (held-out) but only **ρ ≈ 0.34 against the independent GPT panel** (the gap is not single-judge noise — controlled). So roughly a third of the apparent skill was Claude-agreeing-with-Claude (Steiger p=0.003). Building the metric with GPT too confirms it: the lean **flips sides** (each model's metric prefers its own panel), and a **consensus metric averaging both model families beats either alone** (~0.47–0.59) — a cheap debiasing. The metric's honest transferable performance is **~0.34–0.43, not 0.57**. We also tested **genre** (deterministic from OpenAlex): no held-out improvement; excluded.

4. **A second metric is conceptually there — but the shared measurement it needs isn't.** Prior-art *overlap* would read with opposite sign for two constructs: low overlap = **breakthrough/novelty** (distance from prior art), high = **convergence/consolidation** (pulling a field together). Tempting — but when we actually built overlap two ways (per-agent LLM, and deterministic OpenAlex concept-cosine) they came out **uncorrelated (ρ 0.02) and both invalid** as a breakthrough signal (concept-cosine even inverts, mistaking generic reports for novel work). So the duality is a clean hypothesis on an **underdetermined measurement** — real overlap, validated to track prior-art distance, is a prerequisite for either metric.

**The decisive test (§10):** we removed the LLM from the ground truth entirely — 72 historical (2004–2010) AD papers, metric computed at publication time, validated against *mature field disruption* over the following 15–20 years. The metric shows **no reliable predictive power** (ρ near zero, sign-unstable). Against a same-family LLM panel it scored ~0.58; against reality, nothing. The honest deliverable is therefore a **triage prior that flags LLM-perceived contribution depth** — not a validated breakthrough forecaster — plus a clear diagnosis of why (shared-method bias, §9) and what would be needed to do better (full-text multi-domain historical training, §11).

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
| `contrib_wmean` | [PAPER→LLM] | confidence-weighted *mean* novelty weight across a paper's contributions (types from a closed taxonomy `new_paradigm` 1.0 … `replication` 0.1). Un-paddable, but *dilutes* a lone landmark — see `contrib_max_peak_cwmean`. |
| `contrib_peak_wconf` | [PAPER→LLM] | the single strongest `novelty_weight × confidence` contribution. |
| **`contrib_max_peak_cwmean`** | [PAPER→LLM] | **`max(peak, cwmean)` — the ADOPTED metric.** Better-of standout-or-depth; count-independent (one landmark scores the same with or without minor companions). See §5. |
| `contrib_peak` | [PAPER→LLM] | the single strongest `weight × confidence` contribution ("does it have ≥1 landmark result?") |
| `n_contribs` | [PAPER→LLM] | raw count of contributions (breadth; gameable) |
| `n_puffery` | [PAPER→LLM] | contributions voided by the anti-puffery lock (claimed but not tied to a real claim) |
| `delta` / `delta_max` / `n_deltas` | [PAPER→LLM, baseline PRIOR-ART] | the paper's quantified comparisons-vs-prior-work: composite / largest magnitude / count |
| `overlap` (min/mean/max) | [PRIOR-ART] | **the shared measurement (see SPEC.md): fraction of this paper's contribution already covered by each resolved prior-art neighbor, in [0,1].** `mean` = neighborhood density; `max` = closest-predecessor (near-duplicate detector); `min` = connectedness. Read two ways (§7b): **breakthrough = `1 − overlap`; convergence = `+ overlap`.** |
| `resolvability` | [PRIOR-ART] | fraction of the paper's references that resolved to an external id — the confidence in the overlap estimate (novelty is discounted when low, so an unresolved neighborhood cannot masquerade as distance). *Unreliable in this corpus — see §7b/§8.* |
| `anchor` | [PRIOR-ART] | legacy composite scoring *resolution success* — a known-buggy field that rewards that the neighborhood resolved, not its overlap. Superseded by the min/mean/max definition above. |
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

**Use `max(peak, cwmean)`** over the paper's typed contributions — where `peak` = the single strongest `novelty_weight × confidence` contribution and `cwmean` = the confidence-weighted mean. Held-out **ρ ≈ 0.58 vs the grounded Claude panel** (statistically tied with plain `cwmean` at 0.57).

**Why the `max`, not the mean (a fix, per the count-independence principle).** A confidence-weighted *mean* has a dilution flaw: a paper with one landmark contribution plus ten minor ones scores *lower* than the same landmark alone — which is wrong, since one genuine breakthrough is a breakthrough regardless of how many small results accompany it. Taking `max(peak, cwmean)` removes the count-dependence: the score is the *better of* "has one standout contribution" or "is deep on average," so `{one big}` and `{one big + ten small}` score identically. Pure `peak` alone is too noisy (one over-confidently-typed contribution spikes it → held-out 0.45); `cwmean` provides a floor. The `max` blend keeps the non-dilution property without the noise. It ranks real discoveries on top and floors every annual report and burden re-estimate. A usable **triage prior**, not an oracle.

*(Caveat: on n=26 held-out the CI is wide, so `max(peak,cwmean)` does not *significantly* beat `cwmean` or the overfit tournament formulas — the case for it is the non-dilution property plus no overfitting, not a measured edge.)*

## 6. How far from the experts — the ceiling (the headline)

The right yardstick is not zero, it is **how well expert readers predict each other.** Two yardsticks matter — within the same model family, and across families (the latter is the more honest bar for a metric built from one model's reading):

| | ρ |
|---|---|
| **Same-family ceiling** (one Claude persona → Claude panel, leave-one-out) | **0.97** |
| **Cross-model agreement** (Claude panel ↔ GPT-5.5 panel) | **0.89** |
| Our best metric vs Claude panel (held-out) | 0.58 |
| **Our best metric vs GPT-5.5 (held-out, the honest number)** | **0.34** |
| Shipped composite | 0.30 |

**Against the cross-model bar the metric captures well under half the signal — not near the ceiling.** Two readers of *different* model families still agree at 0.89, so the target is real; the metric just doesn't reach it. The gap is **structured**, not noise — the biggest metric-vs-expert disagreements cluster on genres the features cannot distinguish:

- `sal26` (plasma-tau biomarker): experts 61, metric floors it — a real advance the compiler under-typed.
- `kes25` (diagnosis review): experts 31, metric ranks it *last* — reviews the field values.
- `cum26` / `wan25c` (drug-pipeline review, burden re-estimate): experts ~6, metric over-rates them — pure genre confusion.

Because the errors are systematic, better data shapes can close the gap. This is not a wall.

## 7. Why the winner is principled — the sign-flip point

The v1 draft subtracted `delta`. That was theoretically wrong, not just weak. A negatively-correlated feature may be sign-flipped only if it is a **true inverse construct** (`1 − overlap` = novelty: causal, generalizes) — not if it is a **confound proxy** (`n_deltas` correlates with breakthrough only because report-genre papers pile up deltas *in this corpus*). Test: *would intervening on the feature causally change breakthrough-ness?* Adding a quantified comparison to a real discovery should not lower its score — so `delta` must not be subtracted. The held-out numbers confirm the theory: the delta-hack underperforms doing nothing.

## 7b. A second metric fell out — convergence vs breakthrough

The most interesting conceptual result was unplanned. Prior-art **overlap** — computed per resolved neighbor as the fraction of this paper's contribution already covered by that neighbor — is a *single measurement* that a metric can read with **opposite sign for two different constructs**:

- **Breakthrough / novelty = `1 − overlap`** (distance from prior work). A genuine advance sits *far* from what exists.
- **Convergence / consolidation = `+ overlap`** (proximity to, and pulling together of, prior work). A synthesis, a unifying framework, or a field-consolidating review sits *close* to many prior works — and that is valuable, just not *breakthrough*.

We set out to build the first and, in specifying the overlap shape, defined the second. The three aggregates carry distinct meaning and belong in the shared definition:

- **`max` overlap** — the single closest predecessor. High max = a near-duplicate exists ⇒ *not* a breakthrough regardless of the rest (this is what should have caught the `cum26` pipeline review, whose max overlap was 0.93 while its mean looked deceptively novel).
- **`mean` overlap** — neighborhood density. High mean = a crowded, incremental space; the core convergence signal.
- **`min` overlap** — connectedness. Very low min = the work is barely attached to any prior art (either genuinely first-in-field, or unresolved — hence the resolvability discount below).

**Conceptually these are different research virtues** — a paper can be high on one and low on the other (a bold-but-isolated hypothesis: high breakthrough, low convergence; a masterful synthesis: low breakthrough, high convergence). But the empirical test below shows the duality is, so far, **conceptually elegant and empirically undefined.**

**We built the standardized overlap two ways — and the axis does not survive.** We computed overlap deterministically from OpenAlex (concept-vector cosine over each paper's prior related works — `build_neighborhood_openalex.py`) to replace the inconsistent per-agent LLM overlaps. Three findings, all sobering:
1. **The two operationalizations are uncorrelated (ρ ≈ 0.02, n=27).** "Overlap" was never one construct — the LLM agents and the deterministic measure disagree completely (e.g. the 2025 facts report: deterministic overlap 0.25 "looks novel" vs LLM overlap 0.60 "incremental").
2. **The deterministic measure inverts the hypothesis.** On the 28 papers where a neighborhood could be built, `breakthrough = 1 − overlap` correlates *negatively* with experts (all −0.15, held-out −0.39). The reason: concept-cosine conflates *genericness* with *distance* — a broad surveillance report has a diffuse concept vector and thus low cosine to any specific work (looks "far/novel"), while a focused discovery in an active area scores high cosine (looks "close"). It fails oppositely to the LLM version.
3. **Neither beats depth**, and coverage is only 28/66 (OpenAlex lacks usable related-works for the more peripheral papers — a biasing confound on top of everything else).

So the honest status: **the overlap axis is underdetermined on this substrate** — two reasonable measures are uncorrelated and both invalid as a breakthrough signal. The breakthrough/convergence duality remains a clean *hypothesis* but is **not something the current data can deliver**; it requires an overlap measure that is *validated to track prior-art distance* (not genericness, not per-agent taste) plus, for convergence, its own labeled panel. Depth stays the only signal that generalizes.

## 8. How GRO needs to be extended — to climb toward 0.97

All 16 contestants independently reported the substrate is missing signals the ideal metric needs. The 38 proposals cluster into three asks, and §6's residuals say which would help most:

1. **A *validated* overlap measure — the hard open problem, not a formatting fix.** We defined a shared `overlap` (min/mean/max + resolvability) in `SPEC.md` and built it deterministically from OpenAlex — but §7b shows both that and the per-agent LLM version are uncorrelated and invalid (concept-cosine mistakes generic reports for novel work; coverage only 28/66). So the ask is not "pick a rubric" but "produce an overlap that is *validated to track prior-art distance*" — e.g. embedding distance in a citation-trained space (SPECTER2) evaluated against a labeled novel/incremental set. Until then, neither the breakthrough-novelty nor the convergence reading is computable.

   *Note on genre (tested, not adopted).* Contestants proposed a normalized `genre.primary` field, so we fetched genre deterministically from OpenAlex and tested it. The clean signal available (`type: review`) is redundant with contribution depth, and the surveillance-report distinction is not in OpenAlex `type`; genre-conditioning **hurt** held-out ranking (0.57 → 0.50). Genre is therefore **excluded from the metric**. A finer, validated genre classifier might help, but it is not the easy win the residuals suggested.
2. **A `downstream_assessment` / stance edge** (4 proposals) — *highest ceiling, slowest.* Per-citer: does later work *confirm/extend* vs *contest/supersede/fail-to-replicate*? The substrate has citation *counts* (dead) and the compiler's *untested* reading, but nothing for **how the field reacted** — the materialized "cross-object contribution graph" (observation O31), and the only path to measuring *realized* impact and to breaking the shared-LLM-bias worry (§9).
3. **A standalone `anchor_resolution_confidence ∈ [0,1]`** (14 proposals) — *marginal.* Splits resolution-success from the buggy density reward in `anchor`; the winner had to repurpose `anchor_n` for lack of it.

## 9. Shared-model bias — tested with a second model family (and partly confirmed)

The metric's signal (`max(peak,cwmean)`) is the ARA compiler's reading, and the compiler is Claude; the expert panel was also Claude (Opus, three personas, inter-persona ρ ≈ 0.96). So the 0.57 could be two Claudes agreeing with themselves. We tested it directly by **re-judging all 66 papers with GPT-5.5** (`codex exec`, same SOTA-grounded metascientist protocol; `run_codex_panel.py`).

| comparison | ρ (all-66) | ρ (held-out) |
|---|---|---|
| **Claude panel vs GPT-5.5 panel** (cross-model agreement) | **0.89** | — |
| metric vs Claude panel (3-persona mean) | 0.54 | **0.58** |
| metric vs Claude single metascientist | 0.52 | 0.53 |
| **metric vs GPT-5.5** (independent model) | 0.41 | **0.34** |

Two conclusions, and we control the obvious confound (GPT is a single judge, the Claude mean averages three): a single Claude persona still reaches 0.53 held-out, and a single Claude judge tracks the 3-mean at ρ 0.99 — so the metric's 0.53→0.34 drop across model families is a **real model effect, not single-judge noise.**

1. **The ground truth is largely real, not a Claude artifact.** A different model family reproduces the breakthrough ranking at **ρ ≈ 0.89–0.90**. The panel is not measuring something Claude-specific; breakthrough-ness is a mostly model-independent construct. This is the reassuring half.
2. **But the metric's headline is inflated by shared bias.** It agrees with same-family Claude at ~0.53–0.58 yet only **~0.34 against the independent GPT panel.** About a third of the apparent skill was Claude-agreeing-with-Claude. The metric's honest, transferable performance is **~0.34 held-out** — real (well above zero, against a different model) but materially weaker than the AD-Claude number advertised.

**The apparent paradox — how can the panels agree at 0.89 yet the metric agree more with Claude (0.58) than GPT (0.34)?** No contradiction: it is the signature of shared-method variance. Decompose each judge's scores as `CONSENSUS + model_quirk + noise`. The panels correlate at 0.89 because CONSENSUS dominates — the two model families largely agree on what a breakthrough is. But the metric is a Claude compiler feature, so it carries `CONSENSUS + Claude_quirk`. Correlated against Claude it collects CONSENSUS *plus* the shared quirk (0.58); against GPT it collects CONSENSUS only, since GPT's quirk is uncorrelated with a Claude feature (0.34). The ≈0.24 gap *is* that shared Claude idiosyncrasy — and it is statistically real, not sampling noise: a Steiger test for the two dependent correlations gives **Z = 2.95, p = 0.003**. But it is *small in absolute terms*: the two panels share ≈83% of their variance (r²), so the model-specific quirk is only ≈17% of each. The tell for why a small quirk moves the metric so much: were the metric a *strong* predictor, both correlations would converge on the dominant CONSENSUS; it is precisely because the metric is weak (it captures only ~⅓ of the variance) that a 17% shared-quirk slice is a large *fraction* of what the metric picks up.

**We confirmed this is shared-method bias — not a Claude quality edge — by building the metric with GPT too.** Re-typing every paper's contributions with GPT-5.5 (same taxonomy) yields a GPT-authored metric, giving a 2×2 of {metric builder} × {panel} (held-out ρ):

| | vs Claude panel | vs GPT panel |
|---|---|---|
| **Claude-built metric** | **0.58** | 0.34 |
| **GPT-built metric** | 0.43 | **0.43** |

The advantage **flips sides**: each model's metric leans toward its own panel (the diagonal wins). That is the definition of shared-method variance, now shown in both directions. Two further findings: the Claude- and GPT-built metrics agree with each other only **ρ = 0.16** — the two models type contributions very differently — yet a **consensus metric (their average) beats either single-model metric against both panels** (ρ 0.59 vs Claude, 0.47 vs GPT, held-out). Averaging across model families cancels each one's private quirk and keeps the shared signal — a concrete debiasing recipe.

![Shared-method bias, proven both directions](figures/paradox_figure.png)
*Top: the Claude-built metric's real per-paper agreement with each panel (n=66) — tighter to Claude (0.58) than GPT (0.44). Bottom-left: the 2×2 — each metric leans toward its own model's panel (diagonal), and the consensus metric (green) beats both. Bottom-right: consensus dominates (~83% shared), and each metric sits inside it but leans to its maker's side; the two metrics agree only ρ=0.16.*

So the metric survives the bias test — but diminished. Its honest transferable performance is **~0.34–0.43** (cross-model / consensus), not the ~0.58 the same-family setup suggested. Two takeaways carry forward: **(a)** report cross-model or consensus numbers, never same-family; **(b)** a consensus-of-model-families metric is the cheapest available debiasing. The deeper fix — a ground truth with no LLM at all — is the historical/longitudinal test (§10): does the publication-time metric predict what the field *actually did next*.

## 10. The decisive test — does the metric predict what the field actually did? (No.)

Every number so far is the metric agreeing with an *LLM's opinion*. The strongest possible test removes the LLM from the ground truth entirely: take **historical** papers, compute the metric from the paper text *at publication time* (no hindsight), and check whether it predicts which papers actually **reshaped the field** — measured by mature disruption on the now-complete citation graph.

**Setup (`research/metrics/v6-historical/`):** 72 Alzheimer's papers published **2004–2010**, sampled *stratified across impact* (citations 13–3,280; from ordinary papers to landmarks like Braak staging), tight AD relevance. Predictor: `max(peak,cwmean)` typed by Claude from title+abstract, told explicitly to use no hindsight. Ground truth: a Funk–Owen-Smith **disruption index (mDI)** over each paper's ≤5-year citer set from OpenAlex — high = later work built on the paper while dropping its predecessors (a step-change); low = consolidating. No LLM touches the ground truth.

**Result: the publication-time metric does not predict mature disruption.** Spearman ρ hovers around zero and is *not sign-stable* across citer-reliability thresholds — −0.13 (n=62, citers≥10), +0.23 (n=37, ≥30), +0.16 (n=23, ≥50); top-metric-quartile papers were if anything slightly *less* disruptive than the bottom (mean mDI −0.52 vs −0.39). It predicts total citations no better (ρ ≈ −0.06). There is **no robust signal in either direction.**

This is the most important result in the paper. Against a real-world, LLM-free ground truth — what the field actually did over 15–20 years — the metric that scored ρ ≈ 0.58 against a same-family LLM panel shows **no reliable forecasting power**. That is exactly what the shared-method-bias analysis (§9) predicted: much of the panel agreement was two LLMs sharing a prior about what *sounds* important, not a signal for what *becomes* important.

**Honest caveats (this is a weak test of a possibly-real effect, not proof of zero):** (a) abstract-only typing compressed the metric's variance badly (23 unique values across 62 papers, a pile-up at 0.70) — low predictor variance attenuates any correlation; a full-text compile would sharpen it. (b) mDI over a capped citer set is a noisy disruption proxy, especially for low-citer papers (hence the sign flip as the threshold rises). (c) n=62, single domain, single vintage. Still: the strongest test available returned no support for the metric, and no amount of caveat converts a null into a forecast.

## 11. Where this leaves the program

The assessment paper said "no metric measures breakthroughs, and we can't compute one on the current shape." This sharpens it, and the arc runs downhill honestly:
- Against a **same-family LLM panel** the best metric (`max(peak,cwmean)`) looks decent: ρ ≈ 0.58 held-out (§5–6).
- Against an **independent model** it drops to ρ ≈ 0.34, and building the metric with GPT flips the bias — so ~⅓ was LLM shared-method variance, not signal (§9).
- Against **real-world outcomes** (historical papers vs mature field disruption, no LLM in the ground truth) it shows **no reliable predictive power at all** (§10).

The through-line: each time we removed an LLM from the loop, the metric got weaker, and when we removed it entirely the signal vanished. The shipped composite is weak (0.30); no structural feature we tried (genre, overlap, delta) adds transferable signal; and the one feature that does travel — the compiler's contribution-typing — measures *how novel a paper sounds to an LLM reading it*, which is not the same as *whether it reshaped the field*. That gap is the real finding.

What would actually move this: (1) a **full-text** historical compile (abstract-only typing crippled the §10 test) across **multiple domains and vintages**, with the disruption ground truth as the target to *train against*, not just correlate; (2) **human breakthrough ratings** where obtainable; (3) a **validated `overlap`** measure (§7b/§8). Absent those, the honest product is a *triage prior that flags LLM-perceived contribution depth* — useful for sorting a reading pile, not for forecasting breakthroughs.

---

### Reproduction
All under `research/metrics/v5-breakthrough/`: `corpus/compute_corpus.py` (features → `corpus_scored.json`), `corpus/FEATURES.md` (dictionary), `gro_extend_workflow.js` (anchor resolution), `expert_panel_sota_workflow.js` + `corpus/briefs/*` (grounded panel), `corpus/split.json` (40/26), `tournament16_workflow.js` → `corpus/tournament16_result.json`, `corpus/apply_formula.py "<formula>" --split train|test|all` (reproduces every ρ in §4/§6). All correlations recomputed from raw data by the organizer; models read from transcripts (Sonnet contestants, Opus judges).
