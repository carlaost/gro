# Stage 2 critique — `logic/related_work.md`

## (1) Did each winner address the stage-1 critique?

### A (agent1) — yes, all three, and it absorbed the field's best idea
- **Concreteness (Metric 2) was surface-gameable.** Fixed decisively: numeric/named-entity tokens
  in the delta prose now earn near-full credit *only if they echo into* `adopted_elements`
  (unechoed tokens discounted to 0.25x). This is exactly the Adopted↔Delta cross-field coherence
  device that stage-1 called "the single best anti-Goodhart device in the field" — agent1 imported
  it wholesale while keeping its own differentiators. It also retains a boilerplate/template
  penalty (pairwise Jaccard over blocks) that catches mass-cloned deltas — a gaming vector nothing
  else in the set covers.
- **Metric 4 (Type–Narrative) was mostly inert.** Fixed: `imports`/`baseline` now require a
  concrete `adopted_elements` entry; `extends`/`bounds` require generalization/limitation
  vocabulary. It now discriminates on the common type cases, not just the rare `refutes` edge.
- **CADD breadth was spreadable.** Fixed with a `substantiated()` gate: a claim tag counts toward
  density/breadth only if the block carries ≥6 words of delta prose *and* a non-generic
  adopted-elements entry. This ties claim linkage to real content and cross-prices it against
  Metrics 2/4/5.

### B (agent2) — yes, all three, cleanly
- **Added Metric 5 (DOI Resolvability + Type-Narrative)** — closes the two real gaps stage-1
  flagged (no provenance-verifiability term, no use of the `Type` enum). Its DOI sub-score is
  actually more faithful to the shape doc than A's: it grades the documented `"Not specified in
  paper"` sentinel at 0.5 (honest-but-unfollowable) distinct from a blank field at 0.0, whereas A
  collapses both to zero.
- **Generalized Metric 3's degeneracy guard** — replaced the binary `distinct==1` halving with an
  entropy+richness diversity term. This is the more mathematically careful answer to the exact
  stage-1 ask.
- **Hardened Metric 2** with stemming + a concrete-marker specificity floor so terse-but-real
  blocks aren't punished.

Both did the assigned work well, and the two sets have converged: A adopted B's cross-field echo;
B adopted A's type-narrative check.

## (2) WINNER: A

Post-revision, A is the more complete anti-gaming surface. Three decisive edges over B:
1. **Template-duplication penalty.** A's Metric 2 subtracts a boilerplate penalty for block-pairs
   with >0.6 word overlap. B has *no* cross-block duplication defense anywhere — a gamer can clone
   one genuinely-good block 15 times and B's per-block averages stay high while A's collapses.
   Mass-cloning is the cheapest attack on an averaged per-block set; only A defends it.
2. **Substantiation over distribution.** A's `substantiated()` gate makes a claim tag worthless
   unless the block has real prose + adopted content, cross-pricing fabrication across four metrics.
   B's entropy+richness is elegant but only measures the *shape* of the claim-ID distribution, not
   whether any linked block is substantive — a fabricator who spreads real-looking-but-empty tags
   across distinct IDs satisfies B's diversity term.
3. **Denser interlock.** A's combination genuinely taxes one field (`adopted_elements`) from four
   metrics at once; B concedes its DOI half "buys nothing on Metrics 1-4," i.e. sits partly
   orthogonal to the interlock.

B's only clear win — the nuanced DOI sentinel handling — is real but narrow, and doesn't offset
A's structural coverage. This reverses the stage-1 ranking precisely because A, in stage 2,
absorbed B's marquee device while B could not absorb A's template penalty or substantiation gate.

## (3) QUALIFY the winner

**What A genuinely measures:** the *craftsmanship and faithfulness of the compiler's related-work
extraction* — whether deltas are concrete and internally coherent (delta echoes into adopted
elements), whether citations are load-bearing (linked to substantiated claims), whether the full
citation footprint was swept (two-tier completeness), whether type labels match their own prose,
and whether dependencies are provenance-verifiable. This is a well-built, constraint-honest set:
every metric penalizes missing/empty/generic input and never skips or returns N/A.

**What it does NOT measure:** the scientific quality of the underlying paper. A meticulous compile
of a mediocre paper scores high; a sloppy compile of a landmark paper scores low. It measures
*extraction quality*, which is at best a precondition/proxy for good science, not good science
itself.

**Where it is still gameable / limited:**
- **DOIs are unverified.** A well-formed but fabricated DOI passes (A concedes this — resolution is
  out of scope). The provenance term checks syntax, not existence.
- **Every "semantic" check is lexicon- or pattern-based.** Type-narrative consistency, contradiction
  detection, generalization vocabulary, and concreteness are all keyword/regex heuristics. A writer
  who learns the lexicons can satisfy them without doing the corresponding epistemic work — writing
  "generalizes to" earns the `extends` credit regardless of whether a generalization occurred.
- **It cannot distinguish true from fabricated content.** The cross-field echo and substantiation
  gates raise the *cost* of fabrication (you must fake multiple fields consistently and without
  repetition), but a determined, coherent fabricator still passes. The defense is economic, not
  epistemic.
- **Claim IDs are trusted, not validated.** No check confirms a named claim actually exists or is
  actually supported by the cited source; only that the block has enough prose to look real.

**What it would take to trust it:** external DOI/arXiv resolution against Crossref; a claims-ledger
cross-reference so `claims_affected` IDs are validated against the artifact's real claims; and a
semantic reviewer (not a lexicon) to confirm type labels and contradiction/generalization language
reflect the source. A's own combination section repeatedly, and honestly, offloads exactly these to
"outside this function's scope."

**Verdict:** Honest-but-limited. It clears the bar for measuring *related-work compilation quality*
rigorously and is genuinely hard to game cheaply. It does **not** clear the bar of "measures good
science" — it measures a faithful proxy for one upstream input to good science, with the deepest
checks resting on beatable lexical heuristics.
