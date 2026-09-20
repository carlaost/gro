# Stage 1 critique — `logic/related_work.md`

## One-line verdicts + rank

1. **agent2** — Tightest set: the Adopted↔Delta cross-field consistency check (Metric 2) is the single best anti-Goodhart device in the field; interlocking and honest about the hard constraint.
2. **agent1** — Most complete; uniquely exploits the `Type` enum for a real science signal (flattened-disagreement detection) while covering claims, concreteness, footprint, and provenance.
3. **agent3** — Comprehensive and technically clean, but the least differentiated: essentially agent1 ∪ agent2 minus their two best mechanisms; barely uses the `Type` field.
4. **agent4** — Most original ideas (claim fan-in, type entropy), but its marquee Type-Entropy metric is conceptually wrong for this artifact and rewards label diversity as much as science.

## WINNERS: agent2, agent1

---

## Per-winner critique + stage-2 directions

### agent2 (rank 1)
Sharp strengths: **Provenance-Grounding (Metric 2)** requires the `adopted_elements` tokens to actually recur in `Delta → What changed`, so keyword-stuffing one field is punished by the linkage term and vice versa — this is a genuine coherence check that costs as much to fake as to do honestly, and it correctly hard-fails empty adoption on `imports`/`baseline` types. **Claims-Linkage Grounding Ratio** with the all-same-ID degeneracy halving, and **Footprint Tiering Completeness** matching the two documented failure fingerprints (abstract-only ≤3-full/no-brief = 0.05; full-only = 0.15), are well-grounded in the shape doc.

Stage-2 directions:
- **Fill the two real gaps.** The set has (a) *no DOI/provenance-verifiability term at all* despite the shape doc stressing machine-followable provenance, and (b) *no use of the `Type` enum's epistemic content*. Add a DOI-resolvability term and a type-narrative consistency check (borrow agent1's flattened-`refutes` idea) so the set stops ignoring two first-class fields.
- **Generalize the degeneracy guard.** Metric 3 only halves when `distinct == 1`; a gamer using two IDs escapes. Replace the binary check with a diversity/entropy term over claim IDs.
- **Harden Metric 2 against terse-but-real blocks.** Bare token-set intersection under-scores a genuinely specific but short `adopted_elements`; add light normalization/stemming and a specificity floor so honest brevity isn't punished as a provenance gap.

### agent1 (rank 2)
Sharp strengths: **Type–Narrative Consistency (Metric 4)** is the best use of the `Type` enum anywhere in the field — it catches a *real* quality failure (contradiction language in prose flattened into a soft `baseline`/`imports` label, the doc's rare-and-often-missed `refutes` edge) and defends against mass-relabeling via the genre-skew argument. **CADD** blends anchoring density with distinct-claim breadth (penalizing one claim rubber-stamped everywhere), and **Provenance Verifiability** properly folds in the grounded-source special case.

Stage-2 directions:
- **Concreteness (Metric 2) is the weak link.** Counting capitalized tokens is surface-gameable (pad with proper-noun-ish filler). Ground it: require number+entity co-occurrence, or couple concreteness to agent2's Adopted↔Delta echo so padded numbers that appear in no adopted-elements text earn nothing.
- **Metric 4 is mostly inert.** It only discriminates when the contradiction lexicon fires; otherwise almost everything defaults to 0.6/0.8, a large undifferentiated middle. Extend it to check `imports`/`baseline` against presence of concrete adopted elements and `extends`/`bounds` against generalization/limitation vocabulary, so it scores the common cases, not just the rare refutation.
- **CADD breadth is spreadable.** Fabricated IDs scattered across blocks inflate breadth cheaply; tie the anchored count to whether the block's delta/adopted text actually substantiates the named claim.

---

## Why the losers lost

**agent3.** Well-engineered and constraint-honest (weighted DOI regex, template-similarity penalty, claim-diversity guard), but dominated: its five metrics — DOI Resolvability, Tiered-Coverage Completeness, Delta Specificity & Non-Template, Claim-Grounding Density, Adopted-Elements Concreteness — are effectively the union of agent1 and agent2's coverage *minus their two decisive mechanisms*. It never exploits the `Type` enum's epistemic content (no type-narrative or type-consistency check) and has no cross-field coherence device like agent2's Adopted↔Delta echo, so each metric reads an independent slice rather than taxing the others. Its anti-Goodhart story also leans repeatedly on checks that "live outside this function's scope" (downstream DOI resolution, an external claims-ledger), which is candid but means the set *as written* is more gameable than claimed. Strong runner-up, no distinctive edge.

**agent4.** Has the most original ideas — **Claim Fan-in Corroboration** (grouping by claim, rewarding multi-edge type-diverse lineage) and **Engagement-Mode Type Entropy** — but the marquee entropy metric is conceptually wrong for this artifact. The shape doc explicitly documents that healthy `Type` distributions are *genre-dependent* (meta-analyses skew `imports`, theory papers skew `extends`/`bounds`, applied-ML skews `baseline`), so rewarding high type-entropy actively penalizes honest, genre-typical compiles and rewards artificially spreading labels across blocks — a Goodhart trap dressed as a Goodhart defense, and the promised protection ("Metric 1 catches mismatches at review time") is hand-waved to a downstream semantic reviewer. Fan-in Corroboration is clever but fragile when claim linkage is sparse (the common case), and its `coverage` multiplier re-counts the same claim-linkage signal already measured, double-weighting one dimension. The set ends up measuring label diversity as much as scientific quality.
