# Stage-2 critique — `01_paper_manifest`

Judge: metascientist + incentive designer. Two improved sets (A = proposer 2, B = proposer 4) for
scoring the `PAPER.md` root manifest. Both were competent stage-1 finalists; both returned with all
four flagged defects addressed. This stage decides on which *set*, jointly, best measures science
rather than compiler surface — and qualifies the winner honestly.

## Did each winner address the stage-1 critique?

### A (proposer 2) — all four addressed, cleanly.
1. **Metric 2 hedging floor** — fixed correctly. The hedging penalty (`-0.5`, floored at 0.05) now
   applies unconditionally after the additive score, so "may improve accuracy by 5%" lands near the
   floor instead of surviving at 0.4. This is the right fix and it is real.
2. **Metric 3 disclosure regex** — fixed well and this is the sharpest improvement in either set.
   Disclosure credit is now keyed *per actually-thin layer* (thin physical → needs code-specific
   language; thin data → needs dataset-specific language), with graded credit (0.75 / 0.4 / 0.15). A
   single learned trigger phrase can no longer cover both branches. Genuinely harder to game.
3. **Metric 4 stoplist** — fixed adequately. ~6× larger stoplist plus a crude length/`_GENERIC_ACADEMIC`
   IDF proxy. Still corpus-free and hand-curated (brittle at the edges), but materially better.
4. **Missing bibliographic metric** — fixed by *harvesting the right insight*. New Metric 6 explicitly
   copies agent1's honest-`"Not specified in paper"` == valid-DOI design (1.0 == 1.0), and correctly
   rejects agent3's regression. This closes the coverage gap the manifest's primary job demanded.

### B (proposer 4) — all four addressed; one fix is arbitrary.
1. **Metric 5 (was broken)** — the compute-soundness bug (rewarding abstract-disjoint claims) is
   gone. But the replacement — a triangular reward peaking at `overlap_ratio == 0.5` — hard-codes an
   unjustified magic number. Legitimately grounded claims that reuse the abstract's technical
   vocabulary heavily (a normal, honest pattern) are penalized as "copied," and there is no principled
   reason the ideal grounding sits at exactly 50% token overlap. The `anchor_bonus` half (a numeric
   anchor *not* already in the abstract) is the sound half and does real work; the shape half is
   honest-but-arbitrary. Net: no longer broken, but only half-repaired.
2. **Metric 2 genre bias** — fixed well. A genre detector gates the bar: trial-like genres still held
   to formal pre-registration; general genres get full credit for any checkable verifiability artifact
   (code/data/protocol). Hard constraint preserved (0.0 for none). This is the strongest single metric
   in the whole tournament and the fix removed its one real defect.
3. **Metric 4 copy_penalty** — fixed correctly; per-keyword title-substring penalty dropped, replaced
   by a whole-list novelty gate that only fires on the true degenerate case.
4. **Metric 1 exact-equality** — fixed correctly; proportional `_closeness` partial credit, with
   missing data still hard-zeroed. Clean.

## WINNER: A

Reasoning. Both sets closed every gap, so the decision is on the *set as a joint instrument*.

- **A reaches past compiler surface in two of six metrics and kept both intact**: Metric 3 (epistemic
  transparency of absence) and Metric 5 (evidentiary density per claim) measure genuine research
  virtues — honesty about limitations, and proportion of evidence to claims (a real overclaiming
  detector). A then *added* the bibliographic-identity metric it was missing, harvesting the
  tournament's best incentive-design move (honest-absence == valid identifier). It ends with the
  broadest coverage and no broken or arbitrary metric.
- **B owns the single best metric (verifiability/pre-registration provenance) but is thinner as a
  set**: only that one metric truly reaches past surface, and its Metric 5 fix substitutes an
  arbitrary 0.5-overlap peak for the old bug. Metrics 1, 3, 4 remain hygiene checks.

A's combination logic is also jointly tighter across more levers: inflating claim count trips Metric
1, dressing hedged claims in numbers is blocked in Metric 2, buzzword-padding is discounted in Metric
4, faking a rich layer must survive Metrics 1 and 5, and DOI fabrication buys nothing over honest
absence in Metric 6. Six levers that each depress another when pulled alone. B's couplings are real
but fewer, and lean on the arbitrary Metric 5.

The margin is narrow — B's Metric 2 is the best individual metric either team produced, and a future
composite should absolutely borrow it. But as a *set*, A is the more honest, better-covered, less
arbitrary instrument.

## Qualification of the winner (be honest, not celebratory)

**What A genuinely measures.** Manifest *internal integrity and disclosure honesty*: (1) does the
manifest's self-reported arithmetic agree with its own structure (claim counts, table/figure counts);
(2) are the claim one-liners quantified and unhedged rather than vague; (3) when a layer is genuinely
thin, does the prose specifically own the gap; (4) do the domain/keyword tags share real technical
vocabulary with the content; (5) is evidence indexed in rough proportion to claims; (6) are the
bibliographic identifiers well-formed or honestly absent. Four of these six are essentially
*coherence, honesty, and hygiene of the compiled manifest* — not measures of the underlying paper's
scientific quality. Two (Metrics 3 and 5) reach toward research virtues, and they are the reason A
wins.

**Where it is still gameable or limited.**
- Every "science-reaching" signal is ultimately an English-surface regex. Metric 3 still pays 0.75 to
  a compiler that learns the *layer-specific* disclosure phrasing on a thin paper; it detects
  disclosure *language*, not disclosure *truth*. It cannot tell an honest limitation from a
  well-phrased one.
- Metric 2's falsifiability signal rewards the *presence* of numbers/CI/comparison tokens; a fabricated
  but well-formed statistic ("AUC 0.94 vs 0.71, p<0.001") scores high. It measures precision of
  *phrasing*, not correctness of *findings*.
- Metric 5's per-claim evidence ratio is a proportionality heuristic; it cannot judge whether the
  tables/figures actually support the claims, only that a proportionate number were indexed.
- Metric 4's IDF proxy is corpus-free and hand-curated, so it is brittle to domains its stoplist
  doesn't anticipate.
- The set has *no* metric touching the actual scientific content behind the manifest (method
  soundness, evidence–claim entailment, novelty) — by design, since it scores `PAPER.md` alone, but
  that is the ceiling on what it can claim.

**What it would take to trust it.** Ground the disclosure/precision signals in the layers they point
at — cross-check Metric 3's claimed gap against the real `/src` and `/data` contents; verify Metric
2's numbers resolve to values in `evidence/`; confirm Metric 5's indexed evidence actually entails the
claims. Until the manifest metrics are validated against the layers they summarize, A measures a
faithful, honest, internally-coherent *manifest* — a necessary precondition for trusting an ARA, not
proof of good science.

**Verdict.** A does **not** clear the bar of "measures good science." It is honest-but-limited: a
strong, Goodhart-resistant proxy for manifest integrity and disclosure honesty, with two metrics that
genuinely gesture at research virtues but remain surface-level regex signals. It is the right
instrument for its stated job (auditing the Level-1 manifest) and should not be oversold as a science
detector.

## Reply

`01_paper_manifest stage2 winner: A — honest manifest-integrity proxy, limited reach`
