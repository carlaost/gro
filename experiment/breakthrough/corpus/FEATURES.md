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

The **resolver-produced** precedence neighborhood: the set of *earlier* works closest to this
paper, built from the paper's actual reference list plus an OpenAlex search for
pre-publication near-neighbors it may have missed. Each neighbor carries an `overlap` in [0,1]
= how much this paper's contribution is already covered by that prior work. **Dense, high-overlap
neighborhood = incremental/update; sparse, low-overlap = genuinely novel / near first-in-field.**
Overlaps are LLM/resolver estimates against real resolved neighbors (not made up, not follow-on).

- **`anchor`** — the *current* scoring of the anchor (rewards resolution success: real neighborhood + 2nd resolver = 1.0; compiler-estimated = 0.2). NOTE: this rewards *that it resolved*, not density — a known bug. ρ −0.20.
- **`anchor_mean_overlap`** — mean overlap across neighbors. **The real novelty signal**: low = novel. Use `(1 − anchor_mean_overlap)` as a positive novelty term. ρ −0.19 (so `1−` is +0.19).
- **`anchor_max_overlap`** — the single closest prior work's overlap. High = there's a near-duplicate predecessor.
- **`anchor_n`** — number of neighbors resolved. Very few + low overlap can indicate first-in-field (or just an unresolved anchor — be careful).

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
