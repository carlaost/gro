# M30 — Assumption realism & limitation validity — Judge critique, cycle 2

Cycle-2 middle round: **both A and B advance to cycle 3; no final winner is declared here.** This
critique scores how each addressed its five cycle-1 directions (+ the absorbed cross-lane idea),
surfaces residual/newly-introduced weaknesses, and gives concrete cycle-3 directions.

Reminder of the defining axis: M30's edge over round-1 07 (concreteness) and verifier D3 (explicitness)
is that it **reads the method independently to catch unsurfaced risk** rather than only re-grading
declared bullets. A = exp2 lineage (method-text omission scan, quote-grounded, higher compute).
B = exp4 lineage (judge genre-recall `missing_known_threats` + deterministic string caps, single [sem]
call). Both must also hold penalize-don't-skip and Goodhart-resistance.

---

## A (base exp2) — cycle-2 assessment

**Directions addressed — all five, cleanly:**
1. **Cost cut — done.** Five per-item call *types* collapsed to five per-*artifact* batched calls
   (dedup tie-break, `judge_assumptions_batch`, `judge_limitations_batch`, `scan_design_risks`,
   `is_surfaced_batch`), with embedding-cosine dedup escalating only a borderline band to one LLM call.
   The call inventory in §5.0 is explicit and honest.
2. **Quote-verification gate — done, and argued.** `verify_and_filter_risks` discards any trigger whose
   `evidence_quote` isn't a normalized substring/fuzzy match of `method_files`, with the false-positive
   cost stated in §6 ("a hallucinated trigger must never cost the artifact points"). Discarded triggers
   are flagged but never penalized — correct.
3. **Thinness proxy replaced — done.** `expected_min_items = max(1, len(verified_risks))` replaces
   `len(method_files)`, and the double-penalty (thinness charged separately per bucket) is fixed to a
   single combined check. This is a genuine correctness fix, not just a swap.
4. **Worked example — done.** §8 traces che26 to `score = 29.5` with the full component vector, and
   §8's counterfactual exercises the worst-offender cap on both binding and non-binding branches. This
   was the credibility gap vs. exp4 in cycle 1; it's closed.
5. **Worst-offender cap — done.** Adopted from exp3 as a ceiling (`min(final, 0.5)`), not a zeroing,
   with the good rationale that it must stay distinguishable from the structural floor.

**Residual / newly-introduced weaknesses:**

- **Worst-offender cap over-triggers on non-load-bearing items.** `if a_scores and min(a_scores) <=
  0.10` fires for *any* assumption scoring ≤0.10 — including a trivial, non-load-bearing "implausible"
  assumption, which `score_assumption` maps to `0.0` (base 0.0, ×0.4 still 0.0). So a throwaway
  implausible aside caps an otherwise-strong artifact at 0.5. The cap's *intent* (per §2/§3 and B's
  parallel design) is a flagrant **load-bearing** lapse. This is the clearest fix for cycle 3.
- **Flat 0.1 penalty for a missing *optional* input is penalize-don't-skip applied too literally.**
  When `evidence_tables_flags is None`, §5.4 adds `omission_penalty += 0.1` and calls it "worst case."
  But this input is documented as optional and is not something the artifact author controls — it's a
  harness wiring condition. Every artifact run without that input eats a fixed 0.1 hit. Contrast B,
  which distinguishes "no triggering inconsistency existed" (neutral) from "an inconsistency was
  dropped" (penalized). A conflates "we couldn't check" with "the paper failed" — that punishes honest
  artifacts for a tooling gap.
- **New asserted thresholds, unjustified.** The dedup bands (`>=0.87` dup, `<0.72` non-dup) and the
  `fuzzy_ratio >= 0.90` verification cutoff are asserted with no sensitivity discussion — ironically the
  exact critique leveled at exp4 in cycle 1. At minimum, name the failure modes at each boundary.
- **`fuzzy_ratio(q, corpus)` is under-specified and likely wrong as written.** A sentence-length quote
  compared against the entire concatenated corpus with a plain ratio will score near zero on length
  mismatch; this needs `partial_ratio` (as B correctly uses) or a windowed/per-sentence match. As
  written the fuzzy fallback may never fire, leaving only exact `q in corpus`.
- **Cost gap persists.** Five batched calls is a real improvement but still 5× B's single call. Not
  disqualifying, but the compute differentiator that cost exp2 nothing in cycle 1 rankings is only
  partly neutralized.

**Cycle-3 directions for A:**
1. **Gate the worst-offender cap on load-bearing.** Fire only when a flagrant assumption is
   `load_bearing=true` (or a bucket is wholly near-zero). A trivial implausible aside must not cap the
   artifact.
2. **Rework the optional-evidence-input handling.** Adopt B's distinction: score the evidence-layer
   reconciliation term *neutral* when no inconsistency flag existed to surface, and penalize only when a
   flag existed and was dropped. Do not charge a fixed 0.1 for the input simply being unwired.
3. **Fix/spec the fuzzy match** (`partial_ratio` or windowed) and **justify or derive the dedup/verify
   thresholds** (state the boundary failure modes, or add a narrow LLM tie-break as you did for dedup).
4. **Consider merging calls further or defend the 5-call cost.** Even a one-line justification of why 5
   batched calls is acceptable (vs. B's 1) would close the loop, or fold `is_surfaced_batch` into the
   omission scan call.

---

## B (base exp4) — cycle-2 assessment

**Directions addressed — all six, and the mechanisms are sound:**
1. **Grounded `missing_known_threats` — done.** `design_choice_quote` required per threat +
   `filter_grounded_threats` (partial_ratio ≥90) discards ungrounded threats. Closes the invention route
   without a second LLM call — the intended "partway to exp2's rigor" move.
2. **Two-band boilerplate — done.** `hard_cap` (≥0.85 + no paper-specific marker) vs. `ambiguous`
   (0.55–0.85, deferred to the same judge) vs. `clear`. This directly fixes the "specific limitation
   sharing stock nouns gets flattened" failure and removes one asserted single cutoff.
3. **Cross-bucket dedup — done.** `novelty_backstop` generalized to canonical-priority pairwise across
   all three buckets + within-bucket, catching the split-bullet and boundary→assumption restatement
   routes.
4. **Caveat coverage scored — done.** Now a weighted term (0.50/0.35/0.15) rather than an audit note.
5. **Expanded worked example — done.** Three branches (content / availability floor / missing-threats
   with grounding quote).
6. **Worst-offender guard absorbed — done**, and correctly gated on `dreamcase AND load_bearing=yes`
   (contrast A's over-broad trigger — B got this right).

**Residual / newly-introduced weaknesses:**

- **The signature mechanism is silently disabled — and its absence is not penalized — when no method
  excerpt is supplied.** `filter_grounded_threats` returns `[]` if `method_excerpt` is falsy, so
  `missing_threat_penalty = 0`. An artifact (or a harness run) with no method excerpt pays *zero*
  omission penalty and thus scores *higher*. This is a penalize-don't-skip violation on exactly the
  arm that earns B its tighter-than-concreteness edge, and a live gaming incentive (withhold/omit the
  excerpt to dodge the omission check). This is B's most important cycle-3 fix.
- **Branch 2 of the worked example is arithmetically wrong, exposing a design leak.** §3.9 claims the
  empty-`constraints.md` case yields `final = 0.0`. But with no evidence flags,
  `caveat_coverage_score` defaults to `1.0` (the "neutral-full" branch), so
  `raw_score = 0.50*0 + 0.35*0 + 0.15*1.0 = 0.15`, and `final = 100 * 0.0875 * 0.15 ≈ 1.3`, not `0.0`.
  The stated 0.0 is incorrect, and the underlying issue is real: **the free 0.15 caveat baseline leaks
  through the availability floor.**
- **The neutral-full caveat default is dead weight in the common case and compresses range.** Most
  artifacts have no evidence-layer flags, so 15% of the score is a constant `1.0`, and the two real
  sub-targets are squeezed into 85% of the range for every such artifact. Consider dropping the caveat
  term from the denominator (renormalize to 0.59/0.41 over assumption/limitation) when no flags exist,
  so the primary targets keep full discriminating weight and the floor-leak disappears.
- **Redundancy backstop got only half the two-band treatment.** Cycle-1 direction 2 asked for
  paraphrase handling on *both* boilerplate and redundancy. B added the ambiguous-band judge tie-break
  to boilerplate but left `novelty_backstop` on a lone asserted `token_set_ratio >= 0.8` — still blind
  to low-overlap paraphrase restatement (the exact weakness cycle 1 named). The fix that was applied to
  boilerplate should be mirrored here.
- **`has_paper_specific_marker` regex is clinical-genre-biased.** `\d|%|assay|platform|cohort|subgroup`
  hard-codes clinical/omics vocabulary; a non-numeric ML or math-genre specific limitation won't match,
  so `hard_cap` fires more readily off-genre. Broaden or make the marker set genre-aware.

**Cycle-3 directions for B:**
1. **Make the missing-excerpt case penalize, don't skip.** If no method excerpt is available, either
   fall back to genre-level threat recall with an explicit lower ceiling, or apply a defined thinness
   penalty for the un-checkable omission arm — never a silent zero-penalty pass. This is the top fix.
2. **Fix Branch 2 and the caveat-baseline leak.** Renormalize weights when no evidence flags exist (so
   caveat coverage is only in the formula when there's something to cover), and re-derive Branch 2 to
   the corrected number.
3. **Extend the two-band / judge tie-break to `novelty_backstop`.** Add an ambiguous redundancy band
   resolved by the (same) judge or embedding cosine, so paraphrase-level restatement isn't missed and
   the last lone asserted `0.8` cutoff is retired.
4. **De-bias the paper-specific-marker regex** to non-clinical genres (ML/math), or key it off the
   detected genre.

---

## Cross-cutting notes for cycle 3 (both lanes)

- **Inter-rater divergence on che26's A2.** A judges A2 `dreamcase / convenient_but_shaky` → 0.09 and
  fires the cap; B judges A2 `realism: unclear` → no cap. The *same* assumption scores very differently
  across the two lanes, which means the rubric anchor separating "dreamcase" from "unclear/real" is
  under-specified. Whichever design survives should tighten that anchor (a worked example of each label
  on the same bullet), since the whole metric pivots on this call.
- **Neither lane actually derives the evidence-layer inconsistency itself** — both depend on an upstream
  `evidence_flags` / `evidence_tables_flags` input. The shape file frames the Table-1/caption mismatch
  as "a coverage gap a metric can specifically probe." A cycle-3 stretch goal for either lane: sketch how
  the flag would be computed (or state explicitly that it is an upstream contract), rather than assuming
  it arrives pre-computed.
- **Convergence opportunity.** A's quote-grounded method-text omission scan is the Goodhart-hardest
  omission mechanism; B's single-call cost + grounding filter is the cheapest and most auditable. The
  strongest cycle-3 artifact would keep A's independent method scan while adopting B's single-call
  economy and its correctly-gated worst-offender guard — and both should fix penalize-don't-skip on the
  omission arm (A: don't over-charge missing optional input; B: don't zero-penalty a missing excerpt).
