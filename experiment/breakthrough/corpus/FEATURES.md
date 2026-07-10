# Breakthrough-metric features — what each one means and where it comes from

Every feature below is computed per paper from that paper's GRO sidecars. The crucial
distinction is **provenance** — three very different sources, and the metric must not
conflate them:

- **[PAPER→LLM]** — the LLM compiler read *this paper's own text* and made a judgment. Not
  verified against outside sources, not informed by what happened after the paper.
- **[PRIOR-ART]** — resolved against *earlier* external literature (the paper's own reference
  list + an OpenAlex search for pre-publication near-neighbors). Backward-looking.
- **[FOLLOW-ON]** — derived from *later* literature citing this paper (the citation graph).
  Forward-looking. On a 2025–2026 corpus these are near-empty and unreliable.

There is **no feature that reads the follow-on literature's *assessment* of the paper** — we
have citation *counts* (follow-on), but no downstream replication/refutation signal. That gap
is itself a finding.

---

## Contribution features — from `contributions.yaml`  [PAPER→LLM]

`contributions.yaml` is the answer to "what does this paper claim to contribute, and how novel
is each claim *on its face*?" It is produced by the **LLM compiler reading the paper** — it is
**not** compiled from follow-on citations and **not** externally verified. Each contribution is
**double-typed**: `author_framed_type` (how the authors pitch it) vs `compiler_assessed_type`
(the compiler's own call, from a closed taxonomy), plus a `typing_rationale`. An **anti-puffery
lock** requires each contribution to point (`realized_in`) at real claims in the paper, else it
is voided. So these features measure *the compiler's reading of the paper's stated novelty* —
a judgment, reproducible and auditable, but a judgment.

The closed novelty taxonomy and its weights: `new_paradigm` 1.0, `new_method` 0.8,
`new_finding` 0.7, `refutation` 0.6, `synthesis` 0.35, `incremental_improvement` 0.15,
`replication` 0.1.

- **`contribution`** — the current composite of peak+mean (`0.6·peak + 0.4·wmean`). ρ vs experts +0.51.
- **`contrib_peak`** — the single best `weight × confidence` contribution. "Does it have ≥1 strong contribution?" ρ +0.38.
- **`contrib_wmean`** — confidence-weighted *mean* novelty weight across all contributions. Depth, not breadth — **cannot be inflated by padding** with shallow items. ρ +0.50.
- **`n_contribs`** — raw count of contributions. Breadth; weakly positive but gameable. ρ +0.35.
- **`n_puffery`** — count of contributions voided by the anti-puffery lock (claimed but not realized in any claim). A red flag. ρ ≈ 0.

## Delta features — from `delta_ledger.yaml`  [PAPER→LLM, baseline is PRIOR-ART]

The ledger of *comparative* claims: "this paper's number X vs prior work's number Y." The
paper's own value is a `Q##` (extracted from the paper); the baseline is an `XQ##` (an
off-paper prior-work number). The **LLM extracts** each comparison and tags a `delta_status`
(quantified / qualitative_only / claimed_unresolved / not_claimed) and a `baseline_verification`
(source_verified / self_reported / unverified). Verified quantified deltas score highest.
Empirically these are **report tells** — reports/re-estimates announce many big quantified deltas.

- **`delta`** — composite `0.7·max + 0.3·(fraction quantified+verified)`. ρ −0.20.
- **`delta_max`** — the single largest verified delta magnitude. Genre signature of a re-estimate / trial readout. ρ −0.21.
- **`n_deltas`** — raw count of comparative deltas. Strongest single report-tell. ρ −0.32.
- **`frac_quant_verified`** — fraction of deltas that are quantified AND source-verified. ρ −0.13.

## Prior-art / novelty features — from `sota_anchor.yaml`  [PRIOR-ART]

### SHARED DEFINITION of `overlap` (canonical — mirror of SPEC.md L8)

The **precedence neighborhood** is the set of *earlier* works closest to this paper, built from
its reference list plus an OpenAlex search for pre-publication near-neighbors. Each neighbor
carries an **`overlap` ∈ [0,1] = the fraction of THIS paper's core contribution already covered
by that prior work** (0 = unrelated; 1 = a near-duplicate that already did this). To be a *shared*
definition it must be computed the same way for every paper — the reference implementation is a
deterministic OpenAlex measure (bibliographic-coupling Jaccard and/or topic-vector cosine), NOT a
per-agent LLM guess (the v5 corpus used inconsistent per-agent overlaps and this is why the signal
did not transfer).

Aggregate the neighborhood into three numbers, each with distinct meaning:
- **`min_overlap`** — connectedness (very low = barely attached to any prior art).
- **`mean_overlap`** — neighborhood density (the core *convergence* signal).
- **`max_overlap`** — closest-predecessor (near-duplicate detector; high = not a breakthrough regardless of the rest).

**`resolvability` ∈ [0,1]** = fraction of the paper's references that resolved to an external id.
It gates confidence: novelty credit is scaled by resolvability so an *unresolved* neighborhood
(spuriously low overlap) cannot masquerade as genuine distance. If a paper is entirely unresolvable,
novelty → 0 (conservative); realistically DOI/reference resolution is high, so this rarely bites.

### Two metrics from one measurement (see RESULTS_PAPER §7b)

Overlap reads with **opposite sign** for two distinct research virtues:
- **breakthrough / novelty = `1 − overlap`** — distance from prior work.
- **convergence / consolidation = `+ overlap`** — proximity to, and pulling-together of, prior work.

A paper can be high on one and low on the other. This work validated the breakthrough reading; the
convergence metric is defined but **not yet validated** (needs its own labeled panel).

- **`anchor`** — LEGACY composite scoring *resolution success* (real neighborhood + 2nd resolver = 1.0; compiler-estimated = 0.2). Known bug: rewards *that it resolved*, not overlap. ρ +0.20 for spurious reasons. Superseded by the min/mean/max definition above.
- **`anchor_mean_overlap` / `anchor_max_overlap` / `anchor_min_overlap`** — the aggregates above (ρ vs experts on the noisy v5 data: −0.39 / −0.49 / −0.18; i.e. `1−mean` ≈ +0.39). Right construct, but does not transfer here due to inconsistent per-agent overlap scoring.
- **`anchor_n`** — number of neighbors resolved (a resolvability proxy).

## Follow-on / impact features — from the citation graph  [FOLLOW-ON]

Derived from OpenAlex citations *to* this paper within the corpus. **These are the only
forward-looking signals — and they are dead on a recent corpus** (2025–2026 papers have not
accrued downstream edges yet). Reported for completeness; do not build a metric on them here.

- **`uptake_per_year`** — in-corpus citations, age-normalized. ρ ≈ 0.00 (dead).
- **`cd_index`** — Funk–Owen-Smith disruption index (consolidating vs disrupting citers). ρ −0.10 (dead / dominated by lineage density).
- **`year`** — publication year. A control, not a quality signal.

---

## What is NOT in the substrate (candidate extensions)

If the ideal metric needs a signal that isn't here, that is a finding worth reporting, not a
dead end. Known gaps: no downstream **replication/refutation** signal (only raw citation
counts); no **cross-object contribution/credit graph** (inter-paper builds_on / contradicts
edges are unmaterialized); no **peer/review sentiment**; `contributions` novelty is the
*compiler's* reading, never checked against how the field actually reacted.
