# M14 (Reference-landscape completeness) — critique, round 2 cycle 1

## Verdicts + ranks

- **exp2 — Rank 1.** Highest external weight (coverage 0.34 + contradiction 0.16 = 0.50) and the only proposal with a real coverage taxonomy (direct / near_direct / conceptual / missed) plus relation-weighted, genre-sensitive contradiction scoring. Best preserves the net-new edge.
- **exp1 — Rank 2.** Cleanest single dominant external term (external_coverage 0.30) and the sharpest Goodhart mechanism in the field: an explicit high-relevance missed-neighbor penalty that directly operationalizes "don't miss what a search bot would surface." Strong deterministic `block_specificity`.
- **exp4 — Rank 3.** Most implementation-complete parsers and the only trace score that actually cross-references the external gold set, but dilutes the external signal across 7 components (recall only 0.25), weakening the edge the brief says to protect.
- **exp3 — Rank 4.** External recall weighted just 0.25; its reverse-precision anti-padding term is Goodhart-fragile and its contradiction default of 1.0 is too lenient.

## WINNERS: exp2, exp1

## Winner critiques + cycle-2 directions

### exp2 (Rank 1)
Sharp critique:
- The **conceptual-coverage tier is both the best idea and the biggest new Goodhart hole**. Crediting a paper whose result is summarized without citation rewards genuine landscape awareness (resists citation-format gaming) — but an LLM asked "is this idea covered" is exploitable by vague prose that name-drops concepts. The `confidence >= 0.75` + "at least one concrete problem ID" gate is too weak.
- `coverage_score` relies on `p.get("importance", 0.5)` but **`importance` is never defined** — where it comes from (relevance score? citation percentile? Undermind confidence?) is hand-waved. A load-bearing weight cannot be undefined.
- `cross_layer_score` (0.13) is regex keyword-counting (`rw_relation_words`, a boolean `trace_lit`). This is stuffable by sprinkling words like "baseline/contradict/prior" — it does not verify typed deltas attach to real refs.
- `contradiction_score` returns 0.65 when no contradictory paper is found, but **does not distinguish "search genuinely surfaced none" from "search failed."** A failed API call should not earn the same partial credit as a clean negative result.
- Averaging in `coverage_score` dilutes the cost of missing the top 1-2 canonical/contradictory neighbors — there is no asymmetric penalty like exp1's `miss_penalty`.

Cycle-2 directions:
1. Harden conceptual coverage: require the covering Observation/Gap to contain a **specific matching artifact** (a number, named method, dataset, or cohort that appears in the external paper's abstract), not topic overlap. Add a guard: if conceptual coverage exceeds, say, 40% of total covered weight, cap or penalize it — a real footprint should be mostly direct citations.
2. Define `importance` deterministically (e.g., `0.5*relevance + 0.3*citation-percentile-within-knn500 + 0.2*relation_boost`) and document it.
3. Replace `cross_layer_score` keyword counts with a role-alignment sub-score over parsed `RW##` blocks (require type + delta + claims_affected, like exp4's `role_alignment`), and require trace lit-grounding to be verified against external terms rather than a regex boolean.
4. Gate the 0.65 contradiction default on `search_available`; drop toward 0 when retrieval failed.
5. Borrow exp1's asymmetric high-importance missed-neighbor penalty so missing a canonical/contradictory paper hurts more than missing a background one.

### exp1 (Rank 2)
Sharp critique:
- **`trace_landscape` (0.10) never touches the external landscape** — it only counts internal decision/dead_end nodes and measures their prose specificity. For a *reference-landscape* metric the trace term should verify that abandoned paths / dead ends correspond to externally-surfaced inferior or overturned approaches. exp4 does this; exp1 does not.
- `contra_recall = |ara ∩ contra| / |contra|` returns **0 when the contradiction set `K` is empty**, unfairly penalizing genres with no discoverable contradictions (the brief warns against expecting refutations everywhere). This is the exact failure exp2/exp4 avoid with a partial-credit default.
- Close-neighbor recall uses the **full LLM-selected close set (cap 80) as the denominator**, so the score is highly sensitive to the `relevance >= 0.72` threshold and the cap — an ARA is implicitly expected to cite up to 80 papers. Recall against an over-large gold set understates good-but-focused ARAs.
- Only DOI/title matches earn coverage credit; **no conceptual-coverage path**, so an ARA that correctly summarizes a finding without a formal citation scores zero on it (exp2 is better here).

Cycle-2 directions:
1. Make `trace_landscape` cross-reference the external gold set (token/entity overlap between dead_end/pivot node text and externally-flagged inferior/contradictory approaches), not just internal specificity.
2. Give `contra_recall` a genre-sensitive default (partial credit) when `K` is empty *and* search succeeded; keep it near 0 only when search failed.
3. Recall against a **capped, importance-ranked gold set** (e.g., top-25 by relevance) rather than all ≤80, so focused-but-complete ARAs aren't underscored; keep the separate `miss_penalty` for uncited very-high-relevance papers (this is the proposal's best feature — keep and strengthen it by weighting misses by relation type).
4. Add a conceptual-coverage tier (from exp2) so genuine but uncited landscape awareness earns partial credit, with the same specific-artifact guard proposed for exp2.

## Losers

- **exp3:** External recall carries only 0.25 of the score — weakest preservation of the net-new edge the brief mandates. Its `anti_padding_score` computes reverse-precision against the S2 top-500, penalizing legitimate source citations that search simply didn't surface (Goodhart-fragile in reverse), and `external_recall_score` returns contradiction_component = 1.0 when no contradiction is found — too lenient.
- **exp4:** The most runnable and its trace term is the field's best, but it spreads the external signal across 7 components with recall at just 0.25, diluting the external-literature recall that is this metric's entire reason for ranking top-10; also carries a "compliance check" section that is noise, not scoring.
