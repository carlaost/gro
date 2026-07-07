# Stage-2 critique — `logic/concepts.md`

Judge: metascientist + incentive designer. Two improved sets: **A** = former agent4 (stage-1 rank 1),
**B** = former agent3 (stage-1 rank 2). Both were told to fix three named gaps.

## Did each winner address the stage-1 critique?

### A (former agent4) — yes, all three, and via the right mechanism

1. **GVR stoplist — cut, not patched.** The hardcoded 26-term English stoplist (the single most
   "measures-surface-not-science" liability in either set, defeated by a rename) is *retired*, its
   intent folded into **DDG**'s grounding term: instead of matching term strings, it asks whether the
   *definition* anchors into the paper's own specifics (deictic phrasing, a concrete number, or genuine
   use in another concept's `Related` list). This survives the "control group → reference cohort" rename
   that GVR could not. Cutting rather than 1-for-1 replacing was exactly the instruction. Metric count
   4→ intentionally.
2. **CGC reciprocity — de-weighted correctly.** Reciprocity dropped from a load-bearing 0.3 to a 0.1
   bonus; a 0.4-weighted weakly-connected-component coverage term takes over as the primary connectivity
   signal, so a legitimately hierarchical/directional vocabulary is no longer capped. The unjustified
   `density*4` is replaced with a defended `n*2` expected-edges target grounded in the shape doc's own
   ~3–4-per-entry `Related` lists.
3. **BCS paraphrase gate — added.** A boundary field with >0.6 token-overlap with the Definition now
   scores 0.2, closing the copy-paste dodge. NPEF carried over unchanged (was named best-in-field).

### B (former agent3) — yes, all three, largely by adopting A's designs

1. **Notation re-added.** New NPEF is bidirectional (stranded symbol under `Notation: —` → 0; declared
   but ungrounded → 0.5) and scores honest `"—"` at 0.8 — and goes one step further than A by scoring a
   *truly missing* field (`""`) at 0.0 as a hard-constraint defect (see below).
2. **CID scattered-vs-universal — added.** A 0.3 multiplicative shallow-read penalty for ≥80% blank
   `Related concepts`, mirroring BCS's document-level logic.
3. **Orphan references — added.** A near-miss-orphan penalty (difflib 0.75–1.0 against real headings)
   that catches fabricated pseudo-sibling names while sparing genuine field jargon.

Both fully complied. This is a close final.

## WINNER: A

Two reasons decide it, both aligned to the brief's central axis (is the SET *jointly* hard to game?):

1. **A's within-metric multiplicative gating is structurally more Goodhart-resistant.** A collapsed
   circularity, templating, length, and grounding into one metric (DDG) combined multiplicatively, so
   any single failure mode *caps* the definition score. B keeps groundedness (DGS) and circularity (DCP)
   as separate metrics averaged into a 5-metric mean — so gaming grounding still leaves circularity
   credit intact, and each individual weakness is diluted by 1/5 rather than gating the whole. The brief
   rewards "gaming one hurts another"; A builds that *inside* its scoring, not just across metrics.
2. **A eliminated the field's worst surface proxy rather than surviving with it.** Cutting GVR removes a
   metric that measured English-word surface; B never carried that liability but also made a more
   incremental, additive set of improvements. A's edit is the more decisive move toward "measures
   science."

B is genuinely better on **one** dimension: hard-constraint discipline on notation. B's NPEF scores a
missing field (`""`) at 0.0 (defect) and reserves 0.8 for the honest `"—"`. **A's carried-over NPEF
treats `""` and `"—"` identically** (`notation in ("", "-", "—")` → 0.8 if no symbol leaks), so a
genuinely *missing* mandatory field earns 0.8 free credit — a real hard-constraint leak the "unchanged"
carry-over preserved. This is a defect in the winner, noted below, but it is one branch of one of four
metrics and does not outweigh A's structural advantage.

## Qualification of the winner (A)

**What it genuinely measures.** Compiler *extraction fidelity and internal coherence* of the concepts
artifact: whether boundary fields carry non-boilerplate, non-paraphrased limiting language (BCS);
whether the vocabulary resolves into one connected structure with references that point at real
headings (CGC); whether definitions are non-circular, non-templated, long enough, and anchored to the
paper's own specifics (DDG); and whether declared notation agrees with the prose (NPEF). These are
well-constructed, and the joint-gaming argument mostly holds: no single cheap uniform edit raises one
metric without degrading another.

**Where it is still gameable or limited.**
- **It is a transitive proxy, not a measure of the source paper's science.** Every signal scores what
  the *compiler wrote*, not whether the *paper* did careful science. A shallow paper compiled diligently
  scores well; a rigorous paper compiled lazily scores poorly. The brief's "measures SCIENCE not
  surface" bar is only *indirectly* met — this catches shallow extraction, which correlates with but is
  not identical to shallow science.
- **DDG grounding is soft and partially spoofable.** Grounding is a 0.5–1.0 multiplier keyed on deictic
  cues ("in this", "here"), any digit, or being referenced elsewhere. Inserting "in this analysis" plus
  a stray number into each definition raises grounding cheaply; A's defense (length floor + pairwise
  similarity) only bites if the padding is *bulk-identical*, so a compiler writing varied, plausible,
  but still generic definitions with sprinkled deixis can score respectably without genuine paper-
  specificity.
- **The NPEF `""`-vs-`"—"` leak** (above): a missing mandatory notation field scores 0.8, not 0.0 —
  a hard-constraint miss B fixed and A did not.
- **CGC connectivity can be partly faked** by routing references through a hub; A correctly notes this
  earns coverage but not density/DDG payoff, so the collision defense is real but not airtight for small
  `n`.

**What it would take to trust it.** (a) Fix the NPEF missing-field branch to 0.0 (borrow B's `""`
handling — trivial). (b) Cross-artifact validation: check DDG's numbers/comparisons against the paper's
claims/methods artifacts so invented grounding leaves a detectable contradiction. (c) Corpus-relative
grounding (score a definition down if near-identical to the same term across many other ARAs) to catch
the "varied but generic" definitions the current deixis heuristic misses. (d) Calibration against
human-rated concepts.md samples to confirm the score ordering tracks perceived extraction quality.

**Verdict: honest-but-limited.** A does not clear the strong bar of "measures good science" — it cannot,
being one step removed from the paper. It clears the achievable bar for this artifact: a well-engineered,
mostly-jointly-hard-to-game measure of *concept-extraction quality*, with one real hard-constraint leak
and a grounding term that is softer than its prose claims. Trustworthy as a shallow-extraction detector;
not trustworthy as a verdict on the underlying paper's rigor.

WINNER: A
