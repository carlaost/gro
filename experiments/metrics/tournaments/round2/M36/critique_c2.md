# M36 — Multi-perspective triangulation — Round 2, Cycle 2 critique

Metric: does the work combine epistemically-independent lenses (wet-lab × computational,
simulation × observation, formal × empirical) rather than one, and do the constraints reflect
that combination? [sem]. Net-new vs round-1 and the ARA verifier. Both entries below advance to
cycle 3 (no winner declared this cycle) — the goal here is to name each design's remaining holes
precisely and set up the convergence work for cycle 3.

Lineage: **A** = the cycle-1 rank-1 design (exp4: concreteness gate + circular-dependency zeroing
+ fixed no-double-count taxonomy) revised against its three named weaknesses plus the cross-cutting
direction. **B** = the cycle-1 rank-2 design (exp3: fully multiplicative chain + deterministic
availability tier) with exp4's circularity check, exp2's `n_effective`, a recalibrated ceiling, and
a structural boilerplate detector imported.

Both did the assigned c1 fixes. The interesting question for c3 is which *skeleton* to keep, because
the two now differ on the single most important design choice: **how integration/triangulation
enters the score.** A adds it (diversity + triangulation); B multiplies it (integration is a
necessary factor). That divergence drives most of what follows.

---

## A (built on exp4) — critique

**What landed well.** The graded 4-point triangulation scale (`none / mentioned_no_comparison /
one_directional_check / bidirectional_explicit_concordance`), each pinned to a required textual
marker, is a clean fix to the binary-triangulation weakness and is the best-specified integration
grader in either design — B should borrow the marker definitions verbatim. The 4-level
`classify_constraints_tier` (absent/boilerplate/thin/full) is finer than B's 3-tier gate and
correctly demotes length to a last-resort tie-break. The same-category independence audit (Step 2.5)
with separately-quoted `data_source` + `failure_mode` is a real fix to the category/failure-mode
conflation. `genre_mismatch_flag` is a sensible extra that B lacks.

**A1 — The diversity term is a large additive floor that rewards juxtaposition without
triangulation. (Most serious.)** For `n_distinct >= 2`, `combined = 0.55·diversity + 0.45·triangulation`.
Diversity saturates at `min(n_distinct,3)/3`, so **three concrete independent lenses with a
triangulation strength of `None` still score `0.55·1.0 = 0.55` before penalties** — no narrated
comparison of any kind required. This is precisely the "juxtaposition without integration" case that
§1 says the metric must NOT reward, and it is the *same additive single-axis surface* that dropped
exp2 to rank 3 in c1 ("lens count alone buys ~0.45"). A has reintroduced it at 0.55. Pile up three
concretely-described, genuinely-independent-but-never-compared lenses and the metric pays out more
than half its range for what is structurally a pile of methods. The multiplicative winners were
picked over exp2 specifically to close this; A's additive combine step re-opens it. This is A's
central liability going into c3.

**A2 — A claimed anti-gaming defense is described but not implemented.** The Table-1 row and §5
point 3 both assert a "downstream cross-check (deterministic, Step 5)" that "flags and down-weights
any two *different-category* lenses whose `data_source` quotes are near-identical" — the defense
against mislabeling one dataset under two category tags to dodge the stricter same-category bar.
**No such comparison exists anywhere in the Step 5 code.** `score_multi_perspective_triangulation`
never computes string similarity between the `data_source` quotes of different-category lenses; the
quotes are captured (Step 2) but never cross-checked. So gaming route #3 in A's own table is
currently undefended vaporware. Either implement it (a deterministic near-duplicate check over
cross-category `data_source` strings that collapses matched lenses) or stop claiming it.

**A3 — Cross-category pairs are still trusted on the category label alone — the cross-cutting
direction is only half-applied.** The c1 cross-cutting note said failure-mode independence should be
the *primary* judgment for **all** pairs, category a secondary heuristic. A applies a real
failure-mode audit only to *same-category* pairs (Step 2.5); *cross-category* pairs are declared
"presumptively independent" purely by taxonomy label and never audited for a shared failure mode or
shared data source. Two different-category lenses that both ultimately fail on the same contaminated
cohort, the same upstream normalization, or the same annotation source are counted as two
independent legs by A. Combined with A2 (the mislabel cross-check being missing), A's cross-category
independence rests entirely on a label — exactly the conflation the direction told the design to
move away from. B does not have this hole (it audits every pair).

**A4 — Circularity check misses multi-lens triangulation claims.** In Step 5, for a triangulation
claim connecting three or more categories, `pair = tuple(sorted(list(connected))[:2])` reduces the
claim to only its first two sorted categories before the `pair in circular_pairs` test. If the
circular pair is any *other* 2-subset of the connected set (e.g. claim connects {A,B,C}, circular
pair is {B,C}, sorted-first-two is {A,B}), the circular claim survives and takes full graded weight.
The circularity zeroing — A's crown-jewel mechanism — should test *every* pair within the connected
set, not one arbitrary subset.

**A5 — Minor: docstring/code drift and residual brittleness.**
- `collapse_same_category_duplicates` docstring promises a "chain of pairwise-independent judgments"
  / union-find that supports more than one surviving lens; the code just returns `2 if
  independent_pairs >= 1 else 1`. Harmless (the ≤2 cap is a defensible anti-arms-race choice) but the
  docstring overstates the logic — align them.
- `FAILURE_MODE_MARKERS` is a fixed English substring tuple, yet §change-4 claims A "deliberately
  built [it] to avoid the brittleness the critique flagged in the sibling design that tried this
  first with a fixed substring list." It *is* a fixed substring list, just longer, and English-only.
  Drop the overclaim; the residual brittleness is real and shared with B (see cross-cutting below).

---

## B (built on exp3) — critique

**What landed well.** B is the more faithful execution of the cross-cutting direction: Step 2a runs a
dedicated adversarial failure-mode independence pass over **every** pair regardless of modality, and
`modality` is explicitly demoted to a non-binding tag — so two same-tag lenses with distinct quoted
failure modes can count, and two different-tag lenses with the same underlying failure mode do not.
The circularity import (Step 2b) is a true hard-zero on manufactured agreement, and the
`n_effective` construction sharply collapses "3 lenses, two correlated." The fully multiplicative
chain means integration is a *necessary* condition, not a purchasable axis — structurally this is
the stronger Goodhart posture, and it does not have A1 or A3. The `[0,1]`/`×100` fix and the
structural-first boilerplate detector both landed. Worked cases carry real arithmetic.

**B1 — The hard-zero integration gate destroys discrimination at the low-middle. (Most serious.)**
Because `integ_factor = 0.0` whenever `n_effective >= 2` and there is no usable integration
evidence, **two genuinely independent, concretely-described lenses reported without an explicit
cross-reference sentence score exactly 0.0** — identical to an abstract-only thin compile with no
lenses at all. That is too blunt. A paper that brings two failure-mode-independent lenses to bear on
the same claim, even without a narrated "we compared them" step, has strictly more triangulation
value than a single-lens paper, and much more than an empty compile; collapsing all three to 0 loses
exactly the signal the metric exists to grade. The hard zero is correct and valuable for the
*circular* case (manufactured agreement genuinely deserves zero) but over-applied to the merely
*un-narrated* case. Recommend: keep the hard zero only when integration is superseded by circularity
(fabricated agreement); for honest-but-unintegrated multi-lens work, floor integration at a small
positive value so the multiplicative chain still discriminates it above single-lens and above empty.
This also reduces B's dependence on a single [sem] call flipping the whole score between ~0 and ~0.5.

**B2 — Independence enters the score twice, with a cliff at 0.6.** A pair's independence gates
`n_effective` (binary: counts only if `independence_score >= 0.6 and not circular`) *and* multiplies
the score again via `independence_agg`. So independence is double-counted, and the binary 0.6 cutoff
reintroduces a discontinuity the graded `independence_agg` was meant to smooth: a two-lens paper with
`independence_score = 0.59` gets `n_effective = 0 → base 0.0 → total 0`, while `0.60` gets `base 0.65`
then `×(0.4+0.6·0.6)` — a jump from 0 to ~0.3 across one hundredth of the independence scale. Pick
one role for independence, or make the `n_effective` membership test graded/hysteretic rather than a
hard threshold, so a borderline-independent pair degrades smoothly instead of falling off a cliff.

**B3 — Minor: residual English-list brittleness and cost.** `FAILURE_VERBS` / `GENERIC_PHRASES` are
fixed English lists; the c1 critique asked for a *structural* check, and B did add the concrete-noun
+ failure-verb pairing, but the failure-verb half is still a fixed English substring list (shared
residue with A5). `_has_concrete_noun` also drops tokens with attached punctuation (`w[1:].isalpha()`
fails on `"MRI,"`), a small false-negative. And Step 2a/2b are O(n²) [sem] calls (bounded by the
4-lens sampling cap) versus A's O(1) cross-category + on-demand same-category audits — a real cost
difference to weigh, not a correctness issue.

---

## Cross-cutting (applies to both, resolve in cycle 3)

1. **Integration is the fork in the road.** A under-penalizes un-integrated juxtaposition (A1, floor
   0.55); B over-penalizes it (B1, exactly 0). Neither calibration is right. The correct shape is
   monotone and non-degenerate: `single honest lens < two independent lenses reported side-by-side <
   two lenses one-directionally checked < two lenses with bidirectional stated concordance`, with
   circular "agreement" pushed *below* the honest single lens. Cycle 3 should land this ordering
   explicitly with worked cases at each rung.
2. **Failure-mode independence for *all* pairs, not just same-category.** B does this; A does not
   (A3). Whatever skeleton c3 keeps, cross-category pairs must be audited for shared failure
   mode/data source, and the mislabel cross-check A described (A2) must be actually implemented.
3. **Residual English-substring brittleness in the failure-mode/limitation detectors** (A's
   `FAILURE_MODE_MARKERS`, B's `FAILURE_VERBS`/`GENERIC_PHRASES`) is unresolved in both. The c1 ask
   was structural, not phrase-list; the concrete-noun pairing is structural but the verb half is
   still a fixed English list. Consider having the [sem] extraction return a boolean "this bullet
   names a lens-specific, non-generic limitation" grounded in a quote, and use the substring lists
   only as a cheap pre-filter — moving the semantic judgment where it belongs.
4. **Output scale.** A returns `[0,1]`; B returns `[0,100]`. Trivial, but pick one for c3 so the
   two are directly comparable and suite-aggregation is unambiguous.

---

## Cycle-3 directions

**For A:**
1. **Kill the additive diversity floor (A1).** Make integration multiplicative or at least gate
   diversity by it: e.g. `combined = diversity_score · triangulation_score` (with a small floor on
   triangulation for honest-but-unintegrated multi-lens work per cross-cutting #1), so three
   never-compared lenses cannot buy 0.55. This is the single change that most determines whether A is
   viable against B's multiplicative posture.
2. **Implement the cross-category `data_source` near-duplicate cross-check you already claim (A2),**
   and audit cross-category pairs for shared failure mode (A3) — don't trust the taxonomy label.
3. **Fix the circularity check to test every pair in a multi-lens connected set (A4),** not the
   first sorted 2-subset.
4. Align the `collapse_same_category_duplicates` docstring with the ≤2 cap, and drop the
   "avoided the fixed substring list" overclaim (A5).

**For B:**
1. **Soften the integration hard-zero to apply only to circular/superseded integration (B1);** floor
   honest-but-unintegrated multi-lens work at a small positive `integ_factor` so the metric
   discriminates it above single-lens and above empty, and so one [sem] call no longer swings the
   score between ~0 and ~0.5.
2. **Resolve the double-counted independence and the 0.6 cliff (B2)** — either drop independence as a
   separate multiplier (letting `n_effective` carry it) or make `n_effective` membership graded.
3. **Adopt A's graded 4-point triangulation strength scale with its textual markers** in place of the
   binary integration_score, and A's 4-level constraints tier for finer low-end resolution.
4. Fix `_has_concrete_noun` punctuation handling and address the shared failure-verb brittleness
   (cross-cutting #3).

**Convergence note for c3:** the target artifact is B's fully-multiplicative skeleton with pairwise
failure-mode + circularity audits (its Goodhart posture and faithful application of the cross-cutting
direction are the field's best), carrying A's graded triangulation scale + 4-tier constraints
classifier + genre-mismatch flag, with B1's integration cliff softened and the honest-but-
unintegrated rung calibrated per cross-cutting #1. A's job in c3 is to prove its additive combine can
be repaired without becoming B; B's job is to prove its multiplicative chain can discriminate the
low-middle without the hard-zero cliff. Whichever fixes its central liability (A1 for A, B1 for B)
more convincingly should carry the merged design.
