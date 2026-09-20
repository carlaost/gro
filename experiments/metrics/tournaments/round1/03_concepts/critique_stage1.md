# Stage-1 critique — `logic/concepts.md`

Judge: metascientist + incentive designer. Four blind proposals for scoring the ARA compiler's
`concepts.md` artifact. All four converge on the same core battery (boundary-condition depth,
notation grounding, definitional specificity, cross-entry redundancy, concept-graph closure); they
differ in compute sharpness, hard-constraint discipline, and how well each aligns to the *specific*
quality signals the shape doc names (near-universal "Not specified" = shallow read, not honest
absence; borrowed/generic terms = padding; honestly-short docs must not be punished as padded).

A structural caveat that binds all four: `concepts.md` is a compiler artifact, so every metric here
is at best a *transitive* proxy for the source paper's rigor. The proposals that win are the ones
whose signals plausibly track the paper's science (does the source state its own scope? is its
vocabulary genuinely relational?) rather than the compiler's verbosity.

## One-line verdict + rank

1. **agent4** — Most complete battery (5 metrics); only proposal that implements the shape doc's
   "near-universal placeholder = shallow read" signal (BCS ≥80% penalty) and the only notation metric
   (NPEF) that is bidirectional AND does not punish honest `Notation: —`.
2. **agent3** — Cleanest hard-constraint discipline (no free-credit branches) and the sharpest single
   anti-game move in the field: BCIS's boundary-vs-definition paraphrase detector. Distinct circularity
   metric (DCP) is well-motivated. Loses points for dropping notation entirely.
3. **agent1** — Competent, broad (5 metrics), strong combination essay, but its notation metric hands
   a flat 0.6 "mild pass" to notation-absent concepts (free credit, self-admittedly hand-waved), and
   its individual metrics are the plain-vanilla versions of moves agent3/agent4 sharpen.
4. **agent2** — Solid prose but contains a correctness flaw that mis-measures good science: its
   notation-binding metric penalizes legitimately prose-only (clinical/endpoint) artifacts, directly
   contradicting the shape doc.

## WINNERS: agent4, agent3

---

## Winner critique + Stage-2 directions

### agent4 (rank 1)
Strengths:
- **BCS** is the only boundary metric that operationalizes the shape doc's key distinction: it scores
  each `Not specified` at 0 AND applies a multiplicative 0.3 penalty when ≥80% of entries are blank,
  correctly reading uniform absence as a shallow-read signal rather than an honestly under-specified
  paper. This is the single most shape-doc-aware move across all 16 metrics.
- **NPEF** is the best notation metric in the tournament: it is bidirectional (symbol leaks into prose
  with `Notation: —` → 0, catching a *missed extraction*; notation declared but never grounded → 0.5,
  catching decorative notation) and scores honest absence at 0.8 rather than punishing it — respecting
  the shape doc's note that clinical/endpoint vocab legitimately has `Notation: —`. Compare agent1's
  0.6 free-pass and agent2's outright penalty.
- **Definition Distinctiveness** multiplies circularity × templating × length so any single failure
  mode caps the score — a genuinely jointly-hard-to-game construction.

Weaknesses / Stage-2 directions:
- **GVR (#5) is your weakest link — fix or cut it.** A hardcoded English stoplist of 26 terms is
  surface-level, brittle, and (as you concede) defeated by a rename ("control group" → "reference
  cohort"). It also can't scale across fields. Either replace it with a corpus-relative genericness
  signal (e.g., score a heading down if its definition's vocabulary is near-identical to the same term
  as defined across many other ARAs — genuine paper-specific terms won't be), or fold the intent into
  the definition-specificity axis and drop the standalone stoplist. Right now it's a "measures surface"
  metric in a set otherwise reaching for science.
- **CGC reciprocity is over-demanding.** Weighting reciprocity at 0.3 penalizes legitimately
  *hierarchical* or *directional* vocabularies (a method presupposes an object; the object need not
  cite the method back). Real coherent concept graphs are often not reciprocal. Lower this weight or
  replace reciprocity with weakly-connected-component coverage. Also justify or drop the arbitrary
  `density*4` scaling.
- **Borrow agent3's paraphrase check into BCS.** BCS currently rewards any long, cue-bearing boundary
  sentence; it can't yet catch a boundary field that is just the Definition re-pasted with a "requires"
  bolted on. Add BCIS-style boundary-vs-definition token-overlap gating.

### agent3 (rank 2)
Strengths:
- **BCIS's paraphrase detector** (boundary field scored 0.2 when >0.6 token-overlap with the
  Definition) is the field's cleverest anti-Goodhart move — it closes the exact loophole the other
  three leave open, where a lazy compiler copies the definition into the boundary field to dodge the
  placeholder penalty. No other proposal detects this.
- **Cleanest hard-constraint compliance.** Empty → 0.0 everywhere; no "mild pass" free-credit branches
  (contrast agent1's 0.6). Nothing is silently skipped or N/A'd.
- **DCP (circularity)** is correctly argued as a *distinct* failure mode from brevity/genericness, with
  a length-discount that anticipates the "bury the circular clause in a long paragraph" dodge.

Weaknesses / Stage-2 directions:
- **You dropped notation entirely — add it back.** `Notation` is a first-class field in the shape and a
  real quality signal (declared-but-ungrounded notation = decorative; symbols stranded in prose with
  `Notation: —` = missed extraction). Adopt agent4's bidirectional NPEF design specifically because it
  does *not* punish honest `Notation: —` (scores it 0.8), avoiding the trap agent2 fell into.
- **CID doesn't distinguish scattered vs universal absence.** Add the shape doc's shallow-read signal:
  a near-universal empty `Related concepts` should incur an extra penalty beyond the per-concept cost,
  the same way agent4's BCS treats near-universal `Not specified`.
- **CID uses in-degree coverage but ignores orphan references.** Agent4's orphan-rate term catches
  fabricated cross-references to non-existent headings; consider adding it so padding `Related` with
  invented names is actively penalized, not merely uncredited.

---

## Why the losers lost

**agent1 (rank 3).** A perfectly competent five-metric set with the strongest combination essay, but it
never sharpens past the generic version of each idea. Its fatal small flaw is in **Notation-to-Prose
Grounding**: concepts with `Notation: —` receive a flat **0.6** "mild pass," which the author explicitly
frames as avoiding "free credit or unfair punishment" — but 0.6 *is* free credit that lifts the mean of
an otherwise weak, notation-free document, and it dilutes the metric's discriminating power. Its
**Boundary-Condition Depth** and **Definitional Specificity** are near-duplicates of agent4's BCS and
agent3's DGS but lack agent4's shallow-read penalty and agent3's paraphrase gate. Its **Boilerplate-
Uniformity Penalty** (SequenceMatcher over full strings) is workable but cruder than agent2/agent4's
shingle/Jaccard approaches. Nothing is wrong enough to disqualify it; it is simply strictly dominated on
the boundary and notation axes by the two winners.

**agent2 (rank 4).** Well-written and its Cross-Entry Redundancy Penalty (5-word shingles + Jaccard,
combining average and worst-pair overlap) is the best redundancy metric in the tournament. But it is
sunk by a correctness flaw in **Notation-Prose Binding**: the `coverage` term (`with_notation /
len(concepts)`) means a legitimately prose-only artifact — clinical/endpoint vocabulary with
`Notation: —` throughout, which the shape doc explicitly calls *legitimate and non-thin* — scores 0 on
this metric. The proposal thus penalizes an entire class of good science for a field the source paper
correctly has no notation for. This is the exact "measures surface, not science" failure the brief
warns against, and it is baked into the metric's structure rather than being a tunable weight. With only
four metrics and one of them structurally mis-aligned, agent2 lands last.
