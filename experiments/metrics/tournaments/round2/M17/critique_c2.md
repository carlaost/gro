# M17 — Novelty vs literature (+ impact) — Round 2, Cycle 2 critique

Metric M17 = "done before?" for claims/insight/gap/method/concept against external literature, plus
societal/science impact-if-solved. Net-new edge: the internal verifier judges internal scope and
never done-before; M17 must *leave the artifact* via [ext]/[sem] calls, convert them into
deterministic sub-scores, honor penalize-don't-skip (unresolvable external search scores down,
never N/A), and resist Goodhart.

A = cycle-2 repair of exp1 (prior Rank 1). B = cycle-2 repair of exp2 (prior Rank 2).

**This is the middle cycle: both A and B advance to cycle 3. No final winner is picked here.**

---

## A — did it address the cycle-1 directions?

Cycle-1 gave A four directions. All four are addressed, and addressed well:

1. **Fix the composite so retrieval confidence bites (+ unit-test table).** DONE, and exceeded. The
   old `effective_strength` collapsed a searchable-but-empty unit to 0.0 prior-art (full novelty);
   the direction was "cap it via the 0.6 confidence." A rewrote it as an explicit regime function
   (`unit_effective_strength`) that blends `conf*strength + (1-conf)*UNKNOWN_INDEX_RISK_PRIOR`, and
   ships the requested unit-test table (§6.2b). The ordering it now produces —
   `searched_empty` (0.80 novelty) strictly below `searched_with_hits`+none (1.00) and both strictly
   above `unsearchable`/`retrieval_failed` (0.00) — is exactly the property cycle-1 said was missing.
   The bug is genuinely fixed, not papered over.
2. **Repair `n_dependent_claims` with a real gap→claim traversal + name the edge.** DONE (§6.3b). A
   correctly diagnosed that the old code checked a relationship the `claims.md` schema *cannot
   express* (Gap IDs never appear in `Dependencies`), and defined a concrete two-step edge:
   direct link via controlled-vocabulary term overlap (Gap terms ∩ claim Tags/Statement) + transitive
   reverse-closure over the real `Dependencies` graph. This is a real, deterministic traversal and
   the schema diagnosis is correct.
3. **Specify the undermind/[sem] contract concretely.** DONE (§6.2a): endpoints, params,
   request/response shapes, retry/backoff, and an operational definition of "strong overlap"
   (`overlap_degree ∈ {substantial, identical}`, `_OVERLAP_TO_STRENGTH ≥ 0.7`). Runnable, not
   aspirational.
4. **Keep disclosure asymmetry + structural-only impact intact.** DONE — explicitly preserved
   (Change 6), untouched.

**Bonus:** A added a fourth regime cycle-1 didn't ask for — `retrieval_failed` (API timeout/5xx) as
distinct from a clean `searched_empty` — and removed a duplicate LLM call (`judge_all_candidates`
cached once). Both are genuine improvements. This is a disciplined, surgical repair pass that did
what it was told and nothing reckless.

### A — still-weak points for cycle 3

1. **The gap→claim term-overlap edge is a NEW gaming surface, contra A's claim.** A asserts "no new
   free-text/LLM step, so no new gaming surface" (§6.3b). That's false. `n_dependent_claims` now
   rises when claim `Tags`/`Statement` share controlled-vocab terms with a Gap. An author can inflate
   impact by **tag-stuffing** — adding gap-vocabulary tags to otherwise-unrelated claims to swell the
   dependent-claim count fed to Prompt B. The transitive reverse-closure *amplifies* this: one
   tag-matched claim drags in everything downstream of it. This is exactly the kind of cheap
   structural lever the metric is supposed to resist.
2. **`searched_empty` → 0.80 novelty is generously high, only partly closing the obscurity route.**
   The gap between a clean-but-empty search (0.80) and a confirmed clean search with judged
   candidates (1.00) is only 0.20. An author who picks ultra-specific jargon so both indexes return
   nothing still banks 0.80 novelty. Compare B, whose empty-clean regime caps around 0.5 confidence
   blended toward a 0.35 prior (~0.5 novelty for a strong target). A's `conf=0.6` /
   `UNKNOWN_INDEX_RISK_PRIOR=0.5` combination should be re-examined — is 0.80 too close to full
   credit to deter strategic obscurity?
3. **`retrieval_failed` forced to worst-case (novelty 0.0) makes the score hostage to infra
   flakiness, and non-reproducible.** A single S2/Undermind timeout after one retry crushes that
   unit to zero novelty, which flows into the weighted average. This is maximally penalize-don't-skip
   — but it conflates "the artifact is non-novel" with "Anthropic's/S2's servers were down when we
   scored it." Two runs of the same artifact can yield materially different scores. There is a real
   design tension here between *penalizing the artifact* and *flagging a harness failure*; A resolves
   it entirely toward the former. Cycle 3 should confront this explicitly.

---

## B — did it address the cycle-1 directions?

Cycle-1 gave B four directions. All four are addressed, and addressed well:

1. **Reframe `literature_coverage` as a confidence discount toward a neutral prior.** DONE (§4/§5).
   B removed coverage from the multiplicative product and replaced it with `retrieval_confidence`
   blended toward `NEUTRAL_PRIOR = 0.35`. The §5 regime table is clear and the worked reasoning
   (perfect-spec sparse-literature target now lands ~0.5·raw + 0.175 instead of ~0) directly fixes
   the "sparse literature conflated with not-novel" bug cycle-1 flagged. The prior is deliberately
   below the "likely novel" band, so obscurity still doesn't win — good.
2. **Add a second, differently-biased retrieval pass.** DONE (§3). Family S (arXiv/PubMed/bioRxiv
   abstract-embedding cosine recall) is now mandatory alongside Family L (lexical/citation-graph),
   `done_before_penalty` is the max over the *union* (strict widening — a hit from either family
   fully penalizes), and confidence is capped unless both families ran. This brings B's relabeling
   defense to parity with A's dual-index guarantee.
3. **Make explicit how impact avoids double-counting retrieval quality.** DONE (§6). Impact now draws
   on a *separate, gap-level* `field_activity_query` (citation/trial counts), and `evidence_grounding`
   is computed **only from ARA-internal fields**, never from the novelty classifier's output. The
   "novelty and impact fail independently" argument is sound and the decoupling is real.
4. **Preserve dimension-separated classifier + multiplicative gating.** DONE — both retained
   verbatim; the classifier is now applied identically to both families.

This is a thorough, correct repair. B was already the most complete/runnable design and remains so;
the fixes are integrated cleanly into the full `m17_score` reference function.

### B — still-weak points for cycle 3

1. **`family_S == "unavailable"` structurally penalizes entire domains for a harness gap.** B scores
   "no embedding index configured for this artifact's domain" identically to "the index failed"
   (§3, §7): confidence → 0.0 (novelty flat at 0.35) **plus** a 0.20 global precondition penalty.
   That means every artifact in a genre with no configured embedding corpus (much of CS, materials,
   social science, engineering) permanently eats the penalty and never exceeds ~0.35 novelty on any
   target, *regardless of actual novelty*. That is not penalizing the artifact — it's penalizing the
   field for the harness's corpus coverage. This is the most important cycle-3 issue for B:
   distinguish "no index exists for this domain" (a harness/tooling limitation — arguably should
   fall back to a single-family verdict with a *disclosed, smaller* confidence cap, or hard-flag)
   from "an index exists but wasn't run" (a real failure worth the full penalty).
2. **A failed family yields HIGHER novelty (0.35) than a confirmed `already_done` target (~0).**
   Because retrieval failure blends to the neutral prior rather than the floor, a target whose
   retrieval broke floats to the middle of the novelty axis while a target confirmed done-before sinks
   near zero. The global `precondition_multiplier` (−0.20) partly compensates on the *final* score,
   but on the *novelty sub-score itself* a broken search reads as more novel than a proven copy.
   Cycle 3 should compute the end-to-end score for (family-failed) vs (confirmed already_done) side by
   side and confirm failure is never more rewarding than confirmed non-novelty. (Note: this is the
   mirror image of A's weakness #3 — A over-penalizes infra failure to 0; B under-penalizes it to the
   prior. Neither has cleanly separated "harness broke" from "artifact is/ isn't novel.")
3. **`relevant_candidates_L/S` and `exact_phrase_query_succeeded` are under-defined and gate
   confidence.** `retrieval_confidence` keys on `total_relevant = relevant_candidates_L +
   relevant_candidates_S`, but B never defines "relevant" precisely (all non-`unrelated`? only
   `already_done`+`close_predecessor`?). Likewise `exact_phrase_query_succeeded` is required for
   confidence 1.0 but it's ambiguous whether "succeeded" means "executed without error" (nearly
   always true) or "returned hits" (which would cap a genuinely-novel target at 0.7 confidence and
   quietly discount its novelty). Pin both definitions down — they directly move the score.
4. **Impact's `field_activity_query` can let a crowded field inflate `problem_scale`.** High
   citing-paper count feeds `problem_scale` upward, but a saturated field also correlates with *low*
   novelty. That's fine as two independent axes, but verify the impact prompt doesn't let "lots of
   people work on this" masquerade as "this is high-impact-if-solved" — a heavily-studied,
   already-largely-solved area could score high impact on volume alone. Minor relative to #1–#3.

---

## Cross-cutting note (informational, for cycle 3 — not a required change)

A and B have converged architecturally (dual differently-biased retrieval, retrieval-confidence
blend, decoupled impact). Their *distinguishing crown jewels* remain complementary and each still
lacks the other's:

- **A has** the self-disclosure asymmetry (0.05 disclosed vs 0.30 undisclosed prior art — rewards
  honest lit-review rigor) and fixed artifact-driven unit *weights* (KI 1.0 / Gaps 0.8 / anchor
  claim 0.6 / method 0.5, removing the cherry-pick-the-easy-unit route). **B has neither** — it means
  over targets equally, so a compiler can dilute one weak-but-central target among many easy ones.
- **B has** the dimension-separated classifier (`matched_dimensions`/`missing_dimensions` over
  problem/method/claim/population/outcome/concept) with transparent multiplicative gating. **A** uses
  a coarser single `overlap_degree → strength` map.

Cycle 3 is a fair place for each to consider adopting the other's jewel (or explicitly defending why
not), but this is optional — the primary cycle-3 work for both is the weak points listed above.

---

## Cycle-3 directions

### A — cycle-3 directions
1. **Harden the new gap→claim edge against tag-stuffing.** The controlled-vocab-overlap + transitive
   reverse-closure edge is a new impact-inflation lever. Options: require the term match to hit the
   claim `Statement` (not just `Tags`), cap the transitive-closure depth, or dampen impact when
   `n_dependent_claims` is high but the matched claims are low-`Status`/unsupported. Drop the
   incorrect "no new gaming surface" claim and analyze this route in the failure-modes section.
2. **Re-examine the `searched_empty` → 0.80 novelty ceiling.** Decide whether a clean-but-empty
   dual-index search should sit that close to a confirmed-clean search (1.00). Consider lowering
   `conf` or raising the risk prior so empty-search novelty lands further below confirmed novelty,
   tightening the strategic-obscurity route to match B's stricter cap.
3. **Separate "harness/API failure" from "artifact non-novelty" for `retrieval_failed`.** Forcing a
   single timeout to novelty 0.0 makes scores non-reproducible and punishes the artifact for infra
   downtime. Consider: escalate retries / require N clean attempts before scoring; OR emit a distinct
   `metric_uncomputable_retrieval` flag that hard-fails the run for human/retry rather than silently
   baking a low score that is indistinguishable from a real done-before verdict. State the chosen
   policy explicitly.
4. **Keep the crown jewels intact** (disclosure asymmetry, weighted unit set, structural-only impact,
   availability multiplier). Do not water them down while fixing the above.

### B — cycle-3 directions
1. **Fix the `family_S == "unavailable"` domain penalty (highest priority).** Do not let entire
   fields be capped at ~0.35 novelty because no embedding corpus is configured for their genre.
   Distinguish a genuine tooling gap (no index exists for this domain) from a real retrieval failure,
   and give the former a disclosed single-family fallback with a *named* (smaller) confidence cap, or
   a hard-flag — not the full 0.0-confidence + 0.20-penalty treatment reserved for actual failures.
2. **Verify failure is never more rewarding than confirmed non-novelty.** Show the end-to-end score
   for a family-failed target (0.35 prior + precondition multiplier) vs a confirmed `already_done`
   target (~0), and confirm the former does not out-score the latter on the final metric. If it can,
   adjust the failure handling so a broken search never reads as "more novel" than a proven copy.
3. **Pin down `relevant_candidates_L/S` and `exact_phrase_query_succeeded`.** Give exact definitions
   (which overlap classes count as "relevant"; whether "succeeded" means executed vs returned hits),
   since both gate the confidence tier and therefore the score.
4. **Guard impact against crowded-field inflation.** Ensure `field_activity_query` volume can't let a
   saturated, largely-solved area score high `problem_scale` on citation count alone; the impact
   prompt should require leverage/actionability, not just field size.
5. **Preserve the dimension-separated classifier, multiplicative per-target gating, and the
   confidence-blend shape** — these are B's strongest, correctly-net-new elements.
