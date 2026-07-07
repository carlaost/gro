# Stage 2 critique — `logic/problem.md`

A = Proposer #4 (stage-1 Rank 1). B = Proposer #2 (stage-1 Rank 2).

## Did each winner address the stage-1 critique?

### A (Proposer #4) — all four directions addressed, cleanly

1. **M3 overlap seedable → fixed.** `insight_synthesis_specificity` now computes document frequency
   across all Observation/Gap statements and only counts *distinctive* shared terms
   (`doc_freq[w] <= common_cutoff`, cutoff = half the nodes) toward `grounded_nodes`. Seeding two
   artifact-wide boilerplate words per cited node no longer clears the bar. This is exactly the fix
   I asked for.
2. **M3 length floor rewarded verbosity → fixed.** Length credit is now gated: `length_gate =
   min(1, overlap_score * 3)`, `gated_length_score = length_score * length_gate`. A long ungrounded
   paragraph earns ~0, and the ramp avoids a hard cliff. Correct.
3. **M4 `linked` rewarded mere presence → fixed.** `linked = 1.0 if any(ref in obs_ids ...)` now
   requires a `caused_by` reference to resolve to a real Observation id, reusing M2's id set. A
   fabricated/typo'd link no longer buys the 0.3 anchor credit.
4. **M1 citation year-only → fixed.** Added `AUTHOR_YEAR` pattern; bare-year-only evidence is demoted
   to 0.15 instead of scoring as multiple citations. Correct.
   Plus an unrequested but genuine improvement: `dup_penalty` on byte-identical evidence strings across
   Observations — this ports agent2's best original idea (the paste-one-citation-list-everywhere tell)
   into M1, which was A's main blind spot at stage 1.

### B (Proposer #2) — all four directions addressed, also cleanly

1. **M2 diversity penalty over-penalized thin cases → fixed.** Penalty now only fires when
   `len(nonempty_sets) >= 2`; honest short problem statements no longer eat a flat 0.3.
2. **M2 exact-match generic check → fixed.** Replaced with a normalized regex catching "Abstract.",
   "See abstract", "Abstract, p.3", "N/A", etc.
3. **M3 unjustified 0.55 band → fixed.** Replaced with a `[0.35, 0.75]` plateau scoring 1.0, linear
   falloff to the true extremes. Sound.
4. **Insight↔Assumption redundancy → added.** M5 now discounts (×0.3) assumptions whose vocabulary is
   >70% drawn from the Key Insight, not just from a Gap.

Both did honest, responsive work. Neither shipped a regression.

## WINNER: A

Rationale. B closed its gaps well, but A closed the exact deficits that separated it from #1 while
*also* absorbing B's two signature advantages, erasing B's comparative edge:

- **A now has citation-duplication detection** (`dup_penalty`) — the mechanism that was uniquely B's
  at stage 1. B's diversity penalty is still slightly better-targeted (it compares citation *sets*,
  catching near-duplicates, whereas A only catches byte-identical strings), but A's version covers the
  dominant evasion.
- **A already had Gap→Insight integration** (M2's `orphan_gaps` term counts gaps the Insight never
  cites) — B's other claimed unique check. So B's two distinguishing ideas are both now present in A.
- **A's Insight metric remains the best-targeted in the field.** The `GENERIC_INSIGHT_PHRASES`
  blacklist directly operationalizes the shape doc's named "Key Insight merely restates the method
  name" degradation signal, and per-node *distinctive*-term overlap is a more robust synthesis proxy
  than B's aggregate novelty-band Jaccard. B's plateau fix is good but still measures synthesis in
  aggregate against a concatenation of source text, which is a coarser instrument.
- **Compute soundness / directness** favored A at stage 1 and the stage-2 edits preserved it. A's fixes
  are all local and readable; nothing became more brittle.

B is a very close second and would be a defensible pick; the margin is directness plus the fact that A
now contains B's best ideas but not vice versa.

## Qualifying the winner

**What A genuinely measures.** A scores the *depth, internal consistency, and formatting discipline of
a problem-framing artifact*: (M1) whether Observations carry section-anchored, author-year,
non-duplicated citations rather than "Abstract"-only restatements; (M2) whether the Observation→Gap→
Insight reference graph resolves to real ids with no orphans or dead-end gaps; (M3) whether the Key
Insight draws on ≥2 upstream nodes and shares node-specific (not boilerplate) vocabulary with them,
without generic "we propose" filler; (M4) whether Gaps name specific prior methods/numbers and anchor
to a real Observation; (M5) whether Assumptions state checkable conditions rather than truisms. This is
a strong, well-constructed proxy for *whether the compiler (or author) actually engaged with the prior
literature and reasoned in a connected way*, and it reliably separates a shallow, abstract-only, or
method-name-restating compile from a thorough one. It honors the hard constraint throughout: every
missing top-level structure scores 0.0, never N/A.

**Where it is still gameable or limited.**
- **It verifies form, not truth.** Every signal is lexical/structural. A problem statement with
  fabricated-but-well-formatted citations (`AUTHOR_YEAR` strings that name nonexistent papers),
  internally-consistent-but-wrong `caused_by` edges, and proper-noun-dense but factually false failure
  modes would score near the top. The anti-Goodhart argument that "fabrication breaks connectivity
  elsewhere" only holds for *internal* id references (M2); it does **not** validate external citations
  against any bibliography. This is the metric set's central limitation.
- **M4's specificity is a proper-noun/number density count.** It rewards named entities and numbers,
  not a genuine causal explanation of failure; a real-but-irrelevant entity dump can inflate it.
- **M3's distinctive-term filter is statistically thin.** With the typical ~7 nodes (3–5 Observations
  + 2–4 Gaps), the document-frequency cutoff operates on tiny counts, so "distinctive" is noisy.
- **Thresholds are hand-set, not calibrated.** The tier values (1.0/0.7/0.5/0.15), the 25-word length
  scale, the ×0.3 discounts, and the /2 count floors are reasonable but uncalibrated against a labeled
  corpus of strong vs. weak artifacts.

**What it would take to trust it.** (1) Cross-reference citations against the artifact's actual
`related_work.md` / bibliography to establish external validity — the single biggest gap. (2) A
semantic/LLM pass confirming that `caused_by`/`derived_from` edges are causally coherent and that the
Insight actually resolves the cited Gaps, rather than merely sharing vocabulary. (3) Threshold
calibration against human-rated artifacts.

**Verdict: honest-but-limited.** A does not clear the strong bar of "measures good science" — it cannot
distinguish good science from well-articulated, internally-consistent bad (or fabricated) science. It
does clear a narrower, real bar: it robustly measures the *thoroughness and internal coherence of the
problem-framing compile* and reliably catches the exact degradation signals the shape doc names
(abstract-only grounding, method-name-restating insights, generic gaps, orphan nodes). As a
compile-quality / author-engagement signal it is trustworthy; as a direct measure of scientific merit
it is a good proxy with a known, unclosed hole around external factual validity.

WINNER: A
