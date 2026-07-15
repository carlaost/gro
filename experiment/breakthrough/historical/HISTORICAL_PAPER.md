# Does a publication-time breakthrough metric predict what the field actually did?

## A longitudinal validation against downstream citations

*Written 2026-07-15. Follow-on to* **"Measuring breakthrough-ness on new papers — how far a GRO metric gets, and the ceiling above it"** *(the v5 breakthrough paper, `research/metrics/v5-breakthrough/RESULTS_PAPER.md`), which built and adversarially tournament-tuned a breakthrough metric over the GRO substrate and validated it only against an LLM expert panel. v5's own §9–§10 named the decisive open test: replace the LLM ground truth with the real world. This is that test.*

## Abstract

**The question, stated as a prediction task:** given a paper *at publication time only* — holding out everything that cited it afterward — can a metric predict its eventual **breakthrough effect** (did the field pivot on it?) or its **convergence effect** (did it consolidate a field?). v5 built the candidate metric (`max(peak, cwmean)` over typed contributions) and validated it only against an LLM expert panel (ρ ≈ 0.58 same-model, but ≈ 0.34 cross-model — ≈⅓ shared-model bias). Here the target carries **no LLM at all**: **72 Alzheimer's papers from 2004–2010**, metric computed from full text at publication time (typed **twice — Claude and GPT-5.5**), the outcome read from **15–20 years of downstream citations** as a Funk–Owen-Smith disruption index (breakthrough = disruptive; convergence = consolidating). **Answer: no, for either effect.** Predicting breakthrough: Spearman −0.16 (95% CI [−0.56, +0.28]), classification **AUC 0.35** (below chance). Predicting convergence: ρ +0.16 (CI [−0.29, +0.57]), **AUC 0.58** (barely above chance). Both straddle chance — the metric predicts neither — though it leans, weakly and symmetrically, *toward convergence and away from breakthrough*. The two models' metrics agree only ρ ≈ 0.17, so there isn't even a stable construct; meanwhile the two v5 LLM *judge panels* agree at ρ = 0.89. **LLMs agree with LLMs; no LLM-derived metric agrees with the field.**

## 1. Why this study

v5 built the metric and validated it against a blind LLM expert panel, reaching ρ ≈ 0.58 (held-out, same model family). But it then showed (§9) that most of that number was **shared-method variance**: re-judging with GPT-5.5 dropped the correlation to ≈ 0.34, and building the metric with GPT *flipped* the bias toward the GPT panel. Two LLMs agreeing about what *sounds* like a breakthrough is not evidence that either tracks what *becomes* one. The only ground truth that settles this carries no LLM at all: **what the field actually did next**. That signal is uncomputable on recent papers (no downstream citations yet) — which is exactly why v5 deferred it and why this is a separate, longitudinal study.

## 2. What we did (and why each choice)

- **Corpus — historical, so the future has already happened.** 72 Alzheimer's papers published **2004–2010** (16–22 years of downstream record), pulled from OpenAlex with tight AD relevance and **stratified across the impact distribution** (citations 13–3,280) so the sample spans eventual duds *and* eventual landmarks — the contrast a discrimination test requires. Final full-text set: **35/72**, split **LOW=20 / MID=8 / HIGH=7** (the paywalled low-cite tail was the hardest to obtain and is the essential control class).
- **Predictor — the exact v5 metric, at publication time.** `max(peak, cwmean)` over typed contributions, computed from each paper's **full text**, with the typing agent told explicitly to use **no hindsight** about later impact. (v5's first pass used abstracts only, which compressed the metric's variance; full text here decompresses it — Claude range 0.28–0.80.)
- **Dual-model — to separate signal from model idiosyncrasy.** Contributions were typed **independently by Claude and by GPT-5.5** (via `codex`), and we report each model's metric, their agreement, and their consensus (average). If a "contribution depth" construct is real, the two should agree and both should track the field.
- **Ground truth — downstream citations, no LLM.** For each paper we built its mature citer set from OpenAlex and computed a **Funk–Owen-Smith disruption index (mDI)**: does later work cite this paper *while dropping its predecessors* (disruptive → a step-change) or *alongside* them (consolidating → convergence)? We also report raw citation count (impact). The **breakthrough** reading is `metric vs +mDI`; the **convergence** reading is `metric vs −mDI`.

## 3. Results

Every pairwise overlap, across both corpora:

![Overlap map](figures/overlap_figure.png)

*Left — correlation network (edge width strictly ∝ |ρ|, blue = positive, red = negative). The two LLM judge panels sit on a thick edge (ρ=0.89); each metric links to its own-model panel moderately (0.49–0.54) and cross-model a bit less (0.41); the two model metrics link only thinly to each other (0.16); and both link to field disruption on thin red (negative) edges (−0.17, −0.27). Right — the exact Spearman matrix. "—" marks pairs not co-measurable: the LLM panels were run on the recent corpus (no mature citations) and field disruption on the historical corpus, so panel↔field was never measured on shared papers — which is why the two validations use different paper sets and are never cross-substituted.*

**The two prediction tasks** (consensus metric, n=27 with ≥10 mature citers; rank skill = Spearman, decision skill = AUC of top-tercile classification where 0.5 = chance):

| prediction task | Spearman ρ (95% CI) | AUC |
|---|---|---|
| **Breakthrough** — predict eventual disruption | −0.16 ([−0.56, +0.28]) | **0.35** (below chance) |
| **Convergence** — predict eventual consolidation | +0.16 ([−0.29, +0.57]) | **0.58** (≈ chance) |

Per model on the breakthrough task: Claude −0.27, GPT −0.17. **Dual-model agreement:** Claude-FT vs GPT-FT metric ρ = +0.17 — so there isn't even a stable "contribution depth" to validate. Raw-citation impact: ρ ≈ +0.05 (the metric doesn't track attention either). **For contrast (v5, recent corpus):** the two LLM judge *panels* agree at ρ = 0.89.

Both tasks straddle chance — the publication-time metric predicts **neither** the breakthrough nor the convergence effect. The one interpretable regularity is the *symmetry*: it anti-predicts breakthrough (AUC 0.35) and weakly predicts convergence (AUC 0.58). Insofar as contribution-depth leans anywhere, it leans toward *consolidating/well-received* work, not disruptive work — consistent with the metascience result that disruptive papers are not the most-cited (in this corpus disruption and citation count anti-correlate, ρ = −0.18).

## 4. Interpretation

- **Neither effect is predictable.** On the strongest test we can run — real 15–20-year outcomes, no LLM in the ground truth — the publication-time metric predicts *neither* breakthrough (AUC 0.35) *nor* convergence (AUC 0.58) above chance. It leans weakly toward convergence, but not reliably.
- **No stable construct.** Claude and GPT typing agree only ρ ≈ 0.17. There is not even a model-independent "contribution depth" for the field to fail to match — the metric is substantially an artifact of *which* model read the paper.
- **The 0.89 vs ≈0 gap is the whole story.** LLM judges agree with LLM judges (0.89); LLM-derived metrics do not agree with the field (≤0). v5's ρ≈0.58 was two LLMs sharing a prior about what sounds important — vindicated directly: when the grader is the world, the signal is gone.
- **Disruptive ≠ cited.** In this corpus mature disruption and citation count anti-correlate (ρ = −0.18), so "landmark" and "step-change" are largely disjoint sets; the metric predicts neither.

## 5. Limitations

- **n = 27** papers with both full-text dual-model metrics and ≥10 mature citers (35 full-text of 72; 4 low-cite still ungathered). CIs are wide; this is "no reliable signal," not a proven exact zero.
- **Single domain, single vintage** (Alzheimer's, 2004–2010). Generalization to other fields is untested.
- **Disruption proxy.** mDI over a capped citer window is a standard but noisy disruption estimate; results are reported across citer-count thresholds and are sign-unstable at very small n.
- **Access wall (itself a finding).** Historical full text is heavily paywalled; the low-cite control papers required manual retrieval. The substrate's premise — "compile the literature" — is access-blocked for exactly the historical controls a discrimination study needs.

## 6. Conclusion

The v5 metric is a **triage prior that flags LLM-perceived contribution depth**, not a validated breakthrough forecaster. Three independent strengthenings — cross-model panels (v5 §9), full-text typing, and dual-model computation — all converge on the same verdict against real field outcomes: **no reliable predictive power**. To move past this, a metric needs either (a) a genuinely model-independent signal (the two LLMs' 0.17 agreement says contribution-typing isn't one), or (b) a signal built from the downstream record itself (replication, reuse, stance edges) rather than from a single reading of the paper. Building the metric *from* the field-response graph — not asking an LLM to predict it — is the direction this null points to.

---

### Reproduction
All under `research/metrics/v6-historical/`: `fetch_historical.py` (corpus), `fulltext/` + `ingest_pdfs.py` (full text), `type_ft_claude_workflow.js` + `type_ft_gpt.py` (dual-model typing → `metric_pubtime_ft_{claude,gpt}.json`), `compute_disruption.py` (→ `disruption.json`), `make_overlap_fig.py` (the figure), `RESULTS_ft.md`. All correlations Spearman, recomputed from raw data; ground truth carries no LLM.
