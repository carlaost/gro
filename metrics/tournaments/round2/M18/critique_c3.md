# M18 Cycle-3 Critique (FINAL): Claim Drift / Reference Truthfulness

Final cycle. One winner. Metric = do the problem-layer citations actually say what they are cited
for, checked against the REAL external source ([ext]+[sem]) — net-new vs the verifier's L1 §10,
which only confirms the quoted string appears at a cited line inside the ARA. Judged on: what it
genuinely measures, soundness/runnability of the source-fetch+entailment workflow, residual
gameability/limits, and whether it clears "measures good science" and beats the L1 §10
self-quote check vs an honest-but-limited baseline.

Both proposals converged architecturally and both closed all four of their assigned cycle-2
directions in prose. The decision turns on which final version is actually *sound and runnable* as
written — the criterion this metric family is judged on — because the cross-cutting cycle-2 note
told each side to import the other's stronger half, and both claim to have done so.

---

## WINNER: B

## What B genuinely measures

B checks citation truthfulness at the atomic-claim level against the real cited source: for each
load-bearing problem unit (Observation Statement/Implication, Gap Statement/Existing attempts/Why
they fail, Key Insight bridge, source-bearing Assumptions) it resolves the citation, retrieves
source text, and scores support along four scientifically meaningful axes — `scope_match`,
`polarity_match`, `specificity_match`, `number_match`. That decomposition is a genuine measure of
*scientific* drift: it separates "associated with → predicts" (polarity), "mice → patients"
(scope), "may improve → improves" (specificity), and fabricated/mismatched effect sizes (number),
which are exactly the drift modes the brief names. It is not a citation-count or
quote-presence proxy. This clears "measures good science."

## Soundness / runnability of the fetch + entailment workflow

B's workflow is runnable end-to-end and its worked examples are arithmetically self-consistent:

- Step 0 deterministically bounds the external-call budget (fixed caps, deterministic tie-break
  favoring numeric/comparative/causal units where drift hides, overflow scored not dropped).
- Step 3/4 resolution and retrieval use discrete rubric tiers (1.0/0.75/0.45/0.20/0.0), not
  fragile continuous arithmetic, so the deterministic sub-scores actually reproduce.
- The Step 6 bundle example (`direct`+`contradicted` → 0.69 without cap, `min(0.69,0.15)=0.15`
  with cap) and the Step 8 unit example (`mean(0.15,0.90)=0.525` → `min(0.525,0.35)=0.35`) both
  check out by hand. The contradiction-laundering hole is closed at *two* levels (atomic-claim
  bundle cap 0.15, unit cap 0.35) with the arithmetic shown both ways.
- The resolution-only overflow score is now fully deterministic (`max` over per-citation scores,
  risk-tiered 0.35/0.50 ceiling) plus an artifact-level `overflow_fraction > 0.30` → 0.85
  multiplier, closing the "pad the artifact to bury a claim in the unaudited pool" route rather
  than asserting it away.
- The cycle-3 semantic `external_dependency_signal` (text-only classification off `problem.md`,
  independent of whether `related_work.md` exists) imports A's one genuine advantage — the RW
  role audit now fires on a *described* dependency, not just a literal `RW##`/title token — and
  the paraphrase-evasion worked example ("pairwise meta-analyses…" with no id) demonstrates it.

## Why B beats A here (the deciding factor)

A also fixed its critical bug — the cycle-3 `any_contradicted` ceiling applied last after `max()`
is now genuinely correct, and worked example O4 (contradicted+direct → 0.10) verifies it. On the
contradiction axis the two are now even, and A independently hardened its dependency signal. So
the decision falls to A's *other* mandated fix — direction 2, `match_score` for the dominant
title-less author-year citation shape — and that fix is **arithmetically broken as written**:

- A defines `content_component`'s default path as `domain_term_jaccard(domain_terms_from_unit_text,
  candidate_title_and_abstract_tokens)`, explicitly "Jaccard similarity of ... tokens between the
  two token sets" (A, lines 330-333). `domain_terms` is ~5-13 tokens; a title+abstract token set
  is ~100-200 tokens. Even if every domain term appears, Jaccard = |∩|/|∪| ≈ 5/150 ≈ 0.03 — it is
  structurally tiny whenever one set dwarfs the other.
- A's Unit O2 worked example asserts `content_component = 0.82`, giving `match_score = 0.919` →
  clean resolve. That 0.82 is not achievable under A's own Jaccard definition against a full
  abstract; the honest number is ~0.03, giving `match_score ≈ 0.45*0.03 + 0.30 + 0.25 ≈ 0.56` →
  **identity_uncertain**. That re-creates precisely the cycle-2 mis-calibration the critique
  flagged as fatal: essentially every well-formed real ARA citation (author-year lists, no title —
  the dominant shape per `04_problem.md` §4) gets systematically routed to identity_uncertain,
  forced to metadata_only, and support-capped at partial. A's central calibration example is thus
  not reproducible, and the fix that was supposed to make the metric not spuriously fail real ARAs
  does not hold. (Containment/overlap rather than Jaccard would fix it, but A specified Jaccard and
  ran the example on a number Jaccard cannot produce.)

B carries no equivalent load-bearing arithmetic that fails to reproduce. Its resolution/support
scores are tiered rubric values, and its two contradiction worked examples verify by hand. For a
metric family judged on "sound, runnable, deterministic sub-scores," a headline formula whose own
worked example is numerically impossible is the disqualifier, and it lands on A.

## Does B clear "measures good science" and beat the L1 §10 self-quote check?

Yes to both. The Step 5 prompt states explicitly: "Quoted text appears in the source is NOT the
same as the source supports this claim — judge the latter," and forbids outside knowledge, so a
verbatim-correct-but-misrepresenting quote (the exact failure L1 §10 cannot catch) is scored
`contradicted`/`unsupported`. Versus an honest-but-limited baseline that merely re-confirms the
quote exists locally, B measures the strictly harder external-entailment question along four drift
axes and penalizes availability gaps (paywall, unresolved, abstract-only) in the denominator
rather than skipping — honoring penalize-don't-skip. The edge over the verifier is real and
preserved.

## Residual gameability / limits of the winner (honest qualification)

- **Semantic dependency detection is an LLM sub-score gated at confidence ≥ 0.6.** This introduces
  mild non-determinism into *whether* the 0.15 RW-role weight activates. It is backstopped by the
  literal `referenced_rw_ids` path and by penalize-don't-skip (an unresolved trigger floors at
  0.0, never skips), so the failure direction is under-trigger, not silent free-pass — acceptable,
  but it is the one place the metric is not fully deterministic.
- **Thin-description residual evasion.** A dependency described so vaguely it reads as generic
  ("prior work") can still slip under the classifier. B correctly argues this thinness is already
  taxed by the specificity/locatability penalties, so there is no cost-free evasion zone — but the
  boundary is a judgment call, not a hard rule.
- **Overflow ceiling still grants up to 0.35-0.50 with zero entailment checking** for units past
  the Step 0 cap. Mitigated by the 0.85 overflow-fraction multiplier and the fact that §4-typical
  cardinality (3-5 Observations, 2-4 Gaps) sits well below the caps so overflow rarely binds — but
  on an adversarially inflated artifact this is the softest surface.
- **Single-LLM entailment judge** remains the ultimate arbiter of support; the rubric anchors and
  schema validation constrain it, but a systematically generous judge is not fully defended
  against. This is inherent to the metric class, shared by both proposals.

None of these rise to the level of A's non-reproducible identity formula. B is the sound, runnable,
Goodhart-resistant final version, and it now carries A's semantic-dependency strength as well.

---

**M18 WINNER: B**
