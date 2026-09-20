# Stage 1 critique — `09_evidence`

## One-line verdicts + rank

1. **agent1 — WINNER.** Most uniformly sound compute; the reason-keyword *window* check in `sweep_completeness_score` is the sharpest single anti-gaming mechanism in the field (a bare "Figure 9" mention earns nothing without a nearby reason word).
2. **agent3 — WINNER.** Richest science-measurement: `claim_grounding_score`'s distinct-ratio + unjustified-unlinked terms and the `source_locatability_score` page/screenshot decomposition are the best claim-and-provenance signals of any proposal — despite one badly broken arithmetic metric.
3. **agent2 — LOSES (close 3rd).** Uniformly functional, and `is_substantive_trend` (numbers+entities gate on trend-summaries) is a genuinely good anti-boilerplate idea, but the raw-table rounding heuristic is noisy and the arithmetic check is narrow.
4. **agent4 — LOSES.** Cleanest hard-constraint discipline, but omits any claims-grounding metric (the layer's core purpose) and ships a completely dead discrepancy check.

## WINNERS: agent1, agent3

---

## Winner critiques + Stage-2 directions

### agent1
Strengths: `sweep_completeness_score` reconstructs the implied numbered-object ceiling from numbers actually referenced in the artifact and demands each integer up to that ceiling be filed *or* named next to a real reason word — this defeats both junk-file padding and bare-mention skip-listing, exactly the two cheap attacks. `extraction_honesty_score` cross-checks `≈` markers against the declared method in both directions and recurses into `mixed` panels. Good combination narrative.

Weaknesses to fix in Stage 2:
- **Soft floors violate the hard constraint.** Metric 1 returns `0.2` when the note is unparseable and Metric 5 returns `0.4` when nothing is arithmetically checkable. The brief says missing/uncheckable inputs must be *penalized*, not given a comfortable mid-floor. Drive these toward 0 or justify the floor as a genuine penalty, not a shrug.
- **Structural conformance rewards presence, not substance.** Metric 3 counts a `quantitative_plot` conformant if `trend_summary` is merely non-empty — trivially gamed with one placeholder sentence. Borrow agent2's `is_substantive_trend` (require numbers + named entities) so the low-confidence fallback can't be farmed with filler.
- **Metric 5's caption-aggregate heuristic** (target = last integer in caption) is fragile; state its failure modes and consider anchoring to a labeled total (n=, total, screened) rather than positional last-int.

### agent3
Strengths: `claim_grounding_score` is the best in the field — coverage + distinct-claim-set ratio (kills rubber-stamping one claim ID onto every row) + an unlinked-only-if-described check that refuses to wave through unexplained gaps. `source_locatability_score` correctly returns hard `0.0` on an empty evidence base (matching the spec's "near-total loss of grounding capacity" note). `extraction_consistency_score` weights structural failures and type-masquerading at 2x and treats missing fields as violations.

Weaknesses to fix in Stage 2:
- **`self_scrutiny_score` (Metric 3) is broken.** `mismatch_detected` is set `True` whenever *any* pair of numbers fails to sum to a third — which is true for almost every table with ≥3 numbers. As written it flags nearly all honest artifacts as inconsistent and demands a discrepancy caveat everywhere. Rewrite the detector to fire only on a genuine near-miss additive relationship (a subset that *almost* reconciles to a stated total within tolerance but not exactly), the actual PRISMA-style signal — or replace it with agent1's caption-aggregate combinations approach.
- **Metric 3's neutral 0.5** for "no detectable inconsistency" is a mid-floor; decide whether that clears the hard constraint or should be reframed as a genuine "no self-check capability" penalty.
- **Metric 2's `/(3*checks)` normalization** is arbitrary; make the max-possible-violation denominator explicit per object so the 2x weights are interpretable.

---

## Why the losers lost

**agent2** is the most competent of the two losers and functionally complete — no dead metric — with two genuinely good ideas (`is_substantive_trend`'s numbers+entities anti-boilerplate gate, and `claim_traceability_density`'s concentration penalty on over-repeated claim IDs). It loses on two counts. First, `extraction_honesty`'s raw-table rounding check penalizes decimals ending in `0` (`clean_share > 0.8 → 0.4`) — but honest verbatim transcription of round-valued source data would be punished as if fabricated, a noisy proxy that can fight the very fidelity it wants. Second, `arithmetic_self_consistency` only detects arithmetic the transcriber literally wrote as an explicit `\d+\+\d+` string, so it misses all table-grid reconciliation (the common case) and reduces to a narrow, easily-avoided check. Solid but less ambitious and less distinctive than agent3 on the dimensions that matter most.

**agent4** has the cleanest hard-constraint discipline of all four (explicit `0.0` on missing notes, penalized gaps rather than skips throughout), and `provenance_specificity_score`'s four-component source decomposition is good. But it loses decisively on two structural problems. First, it has **no claims-grounding/traceability metric at all** — the shape doc frames `evidence/` as precisely "the raw material every number in `claims.md` traces back to," and agent4 spends that slot on provenance instead, leaving the single most science-relevant dimension unmeasured. Second, `discrepancy_flagging_rate`'s `_has_sum_mismatch` **never returns `True` on any code path** (the author even flags it as a "conservative proxy") — the entire metric is inert, always collapsing to `0.0` or `0.5` and never crediting a real flagged discrepancy. A dead metric plus a missing core dimension is too much to overcome.
