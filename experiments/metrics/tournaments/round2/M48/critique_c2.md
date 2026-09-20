# M48 — End-to-end reproducibility bundle — Judge critique, cycle 2

Middle round: both A (improved exp1) and B (improved exp3) advance to cycle 3. No final winner
declared. Both entrants executed their cycle-1 directions cleanly; the remaining work is convergence
plus a set of second-order defects each still carries.

Metric recap: per the brief, M48 is scoped at §9 evidence with §10/§11 as cross-layer dependencies —
"do figure + data + code co-exist across layers for actual end-to-end replication?" Graded, penalize-
don't-skip, honest-disclosure vs silent-gap vs fabrication distinguished, tighter than verifier D6.

---

## A (improved exp1) — object-indexed triangulation + anchor-gated linking

### Cycle-1 directions: all four addressed
1. **Strict `min()` → soft-min.** Done — §2.6 harmonic mean with an explicit hard-zero rule. The
   `[0.01,1,1]` vs `[0.01,0.01,0.01]` brittleness is genuinely fixed while a true zero still caps.
2. **Anchor-gate `linked`.** Done — §2.5 adds anchor extraction (Steps 1/2) and a `linked` /
   `linked_no_anchor` / contradiction-refused ladder. Imports exp4's mechanism as instructed.
3. **Explicit fabrication tier hard-capping.** Done — §2.3 `evidence_leg_result` returns `0.0` +
   `fabricated:True` for a Critical-Rule-#11 object, and the §2.6 hard-zero rule propagates it to the
   whole bundle. Also extended to code/data legs on a stated contradiction. This closes the gap vs
   exp3's whole-bundle fabrication cap.
4. **Evidence-leg-as-fidelity drift.** Addressed with the §1.7 scope note — the evidence leg is
   reframed as a ground-truth *gate* (coarse five-bucket tiers, fabrication exact) rather than a
   fine-grained fidelity grade. This is the right framing and defuses the redundancy worry.

A remains the truest reading of the brief: §9-object-indexed, per-object triangulation, enumerable
"penalize missing any leg." That anchoring must survive to the final metric.

### Remaining weaknesses
1. **Anchor extraction/matching is still LLM-mediated — now softer than B on the very axis exp4 was
   praised for.** Steps 1/2 have the LLM emit `anchors`, and Step 3's `code_anchor_check` /
   `data_anchor_check` ("agree"/"disagree") is an LLM judgment. B moved this to fully deterministic
   regex extraction + counted matches (its STEP 2.5). The cycle-1 note wanted exp4's anchor idea as
   "the concrete test behind linked" and "falsifiable"; an LLM saying "these two values agree" is less
   falsifiable than a greppable literal match. This is now A's single softest surface.
2. **Harmonic mean may be too generous for a disclosed-but-absent leg.** With evidence=1.0, code=1.0,
   data=0.3 (honest, reasoned data absence), the bundle is `3/(1+1+3.33) ≈ 0.56` — an ARA that
   *cannot be reproduced at all on the data leg* scores a middling 0.56, nearly double its weakest
   leg. Soft-min was requested to kill `min()` brittleness, but A has not checked that the softness
   doesn't over-credit a structurally broken bundle. The weakest-link *intent* wants this closer to
   0.3–0.4.
3. **Unfiled objects are not claims-weighted — the exact gap B fixed.** §2.7 assigns every unfiled
   object `weight = claims_weight_floor` (=1), flat. So a missing headline table that was supposed to
   support 10 claims costs the same as a missing trivial one. The README `Claims` column lists claims
   for unfiled objects too (it is the completeness ledger), so this is parseable and should be used.
   A imported claims-weighting for *filed* objects but left the more important case — a silently
   dropped headline object — under-penalized.
4. **`linked_no_anchor` (0.85) is a soft, gameable escape hatch.** The tier fires when "neither side
   has any extractable anchor." A compiler that keeps its code/data descriptions anchor-free (no n=,
   no version, no accession) can reliably land 0.85 for a plausible-sounding semantic match while
   never exposing a checkable value — strictly easier than risking a `disagree`. The asymmetric-anchor
   case (object has n=601, matched item has none) is also under-specified: the prompt's
   `no_anchors_available` vs `linked_no_anchor` ("neither side") boundary is ambiguous and could
   silently route a half-anchored match to 0.85. Tighten: presence of an anchor on the object side
   should *require* a match on the item side to clear `linked`, and anchor-free-both should sit below
   0.85.
5. **Theory/proof evidence objects unhandled.** The shape doc specifies `evidence/proofs/{name}.md`
   for derivation work. A's Step 1 `type` enum has no proof/theorem value and `evidence_leg_result`
   has no branch for it. A pure-theory ARA (data-leg genre-exempt, code disclosed-absent) will have
   its evidence objects fall through to the `0.2` default. Add an explicit proof-type path.

### Cycle-3 directions for A
- **Make anchor extraction + matching deterministic** (adopt B's regex/structural pass); keep the LLM
  only for the semantic "does this item's *purpose* cover this object" judgment, not for the numeric
  agree/disagree verdict.
- **Recalibrate the aggregator's aggressiveness.** Either weight the harmonic mean toward the minimum
  (e.g. a power/soft-min with p<0 tunable, or blend `0.5*min + 0.5*harmonic`), or show worked numbers
  demonstrating a single 0.3 leg lands the bundle near 0.3–0.4, not 0.56. State the target explicitly.
- **Claims-weight unfiled objects** using the README `Claims` column, so a dropped headline object
  dominates the penalty.
- **Lower / gate `linked_no_anchor`** and resolve the asymmetric-anchor case so anchor-free matches
  can't be farmed.
- **Add a proof/theorem evidence path** to Step 1's enum and `evidence_leg_result`.

---

## B (improved exp3) — graded disclosure table + deterministic arithmetic

### Cycle-1 directions: all four addressed
1. **Credit ordering fixed.** `GENRE_CORRECT_DISCLOSED = 0.60 > DISCLOSED_BUT_DEAD = 0.55`. Correct
   and well-argued (honest scope statement > broken promise).
2. **Claims-weighting imported into FIG.** Done — `fig_completeness_ratio` is now
   `1 + |claims|`-weighted per object. B's argument for confining weighting to FIG (the only
   object-indexed leg) rather than smearing it across all legs is sound.
3. **SCOPE demoted to a gate.** Done — SCOPE leaves the harmonic pool and becomes a post-combination
   multiplier (`scope_gate`), capped at 1.0 so verbose prose can't farm co-equal credit, while
   missing/thin still floors it to 0.35. This is a clean resolution of the §7-redundancy worry and the
   executability-vs-interpretability distinction (§1.5) is a genuinely good conceptual contribution.
4. **Coherence made deterministic.** Done, and further than asked — STEP 2.5 replaces the LLM 0–3
   coherence integer with regex anchor extraction + counted matches/contradictions. This is now B's
   standout: strictly tighter than exp4, which still let an LLM judge anchor agreement.

### Remaining weaknesses
1. **Still whole-leg, not §9-object-indexed — the core structural divergence from the brief.** The
   cycle-1 critique flagged this and it persists. DATA and CODE are graded as single whole-ARA legs; a
   strong dataset+pipeline that produced Figure 1 credits the entire DATA/CODE leg even if Figure 2's
   inputs are orphaned. Claims-weighting the FIG *completeness ratio* is a partial move toward
   object-indexing but does not make the data/code legs per-object. The anchor pass catches *some*
   cross-leg disconnection but only globally (any shared anchor anywhere), not per-object. This is the
   principal reason B is not, on its own, the faithful reading of the metric's scope.
2. **Computed-but-unused deterministic signals — a real completeness gap for a "fixed-arithmetic"
   metric.** Two STEP 1 structural fields never enter `compute_m48`:
   - `access_tier_stated` — the data-access-honesty defect (§11's blanket "data available" collapsing
     open vs controlled) is called out in §1.3 as "must be scored as a coherence violation," but STEP
     2.5's anchor patterns only cover accession/n/version/seed/param — *not* access-tier vagueness — and
     `access_tier_stated` is never read in the scoring function. So the specific honesty defect the
     brief and shape doc most emphasize is not actually penalized anywhere in B's arithmetic.
   - `grounding_all_tagged` — the mandatory grounding-tag audit ("missing tag => hard flag") is
     computed but not consumed; it is left entirely to STEP 3's LLM `fabricated_or_mismatched`
     classification, undercutting the "deterministic where possible" claim.
   Wire both into the scoring (e.g. `access_tier_stated=False` forces a data-leg coherence/ceiling
   penalty; missing grounding tag hard-caps the code leg deterministically).
3. **Coherence floor of 0.55 for an active contradiction is too soft — the same defect cycle-1 dinged
   exp4 for.** A literal numeric contradiction across legs (dataset says n=482 for cohort A,
   constraints says n=410 for the same cohort) means the layers demonstrably do not correspond, yet it
   only multiplies the final score by 0.55. Contrast A, which refuses the specific link outright
   (downgrades that object to `unlinked_present`). A contradiction is stronger evidence of a broken
   bundle than mere no-linkage; B should cap it far harder (toward exp1's treatment), not at a 45%
   haircut.
4. **Deterministic ≠ correct: anchor-key normalization is fragile.** STEP 2.5 keys anchors by
   `(type, normalized_label)` with `n=` "keyed by nearest cohort/dataset name if one appears in the
   same sentence, else keyed generically as 'n'." Two different cohorts both falling back to the
   generic "n" key can produce a spurious `contradiction` (→ 0.55 cap) or a spurious `match` (→
   inflated coherence). Going fully deterministic bought auditability at the cost of semantic
   robustness that A's LLM check retains. The normalization rules need hardening (require a named
   entity to key an `n=`; drop unkeyable anchors rather than bucketing them generically).
5. **Numbered-object universe parsing is fuzzy.** `fig_completeness_ratio` counts the object universe
   by regex over "Table \d+"/"Figure \d+" across Source/PAPER.md/prose; repeated mentions and
   supplementary-vs-main-text objects (the huu25 case in the shape doc: 0 main-text tables, 17
   supplementary) will mis-count without dedup and a main/supplementary split. Specify the dedup and
   the supplementary-accounting rule.

### Cycle-3 directions for B
- **Move toward per-object linking**, or at minimum decompose the DATA/CODE legs per evidence object
  so an orphaned headline figure can't be masked by a well-linked one elsewhere. This is the
  convergence toward A and the brief's scope.
- **Wire `access_tier_stated` and `grounding_all_tagged` into the deterministic scoring** so the
  data-access-honesty defect and the grounding-tag audit are penalized without relying on the LLM.
- **Cap active contradictions much harder** than the 0.55 coherence floor — treat a contradiction as
  near-fatal to the affected leg, per A's surgical downgrade.
- **Harden anchor-key normalization** so generic `n` fallbacks can't create spurious matches or
  contradictions.
- **Specify object-universe dedup + main/supplementary accounting** for `fig_completeness_ratio`.

---

## Convergence note for cycle 3

The two entrants are now cleanly complementary halves of the ideal metric, exactly as the cycle-1
convergence note predicted, and cycle 3 should merge rather than pick:

- **From A:** §9-object-indexed per-object triangulation (the faithful scope), the per-object
  fabrication hard-cap, and the surgical treatment of an anchor contradiction (refuse the link, don't
  just haircut the whole score).
- **From B:** the deterministic regex anchor-extraction-and-match pass (strictly more falsifiable than
  A's LLM anchor check), the graded honest/silent/dead/fabricated `LEG_CREDIT` table with the
  now-correct ordering, and the SCOPE-as-interpretability-gate idea (a genuinely good, non-redundant
  contribution B originated).
- **Both must fix:** aggregator calibration (soft-min should land a single weak leg near that leg, not
  midway); claims-weighting applied to *missing* objects, not just filed ones; and the theory/proof
  evidence path plus the data-access-tier-honesty defect, neither of which either entrant currently
  scores correctly.

The target final metric: §9-object-indexed (A) + per-object soft-min weakest-link over evidence/data/
code with a graded honest/silent/fabrication credit table (B) + `linked` gated on *deterministically*
extracted shared anchors (B's mechanism, A's contradiction-refusal semantics) + SCOPE as a shallow
interpretability gate (B) — calibrated so a single broken or disclosed-absent leg dominates the score.
