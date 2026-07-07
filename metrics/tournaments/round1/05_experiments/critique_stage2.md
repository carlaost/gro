# Stage 2 critique — `logic/experiments.md`

## (1) Did each winner address the stage-1 critique?

### A (Proposer 2 / stage-1 agent2) — yes, all four, at the compute level
- **Tautology "lexically-distinct-but-vacuous" gap → fixed.** `Falsifiable Specificity` now adds a
  triangular `grounding_score` on token overlap between `Expected outcome` and `Metrics`: zero
  overlap (ungrounded prose) and near-total overlap (tautology) both score low, moderate genuine
  overlap scores high. This directly closes the hole I flagged ("distinct" could mean "unrelated")
  and is real arithmetic, not prose.
- **Partial `claims.md` availability + coverage-via-trivial-claims → fixed.** Replaced the binary
  present/absent branch with a continuous `claims_availability` float scaling both claim-dependent
  terms, and added an inline `richness()` gate so coverage credit for a claim is scaled by the
  citing experiment's own `Setup`/`Procedure` development. The anti-padding linkage is now computed
  in this function, not asserted.
- **`baseline_rigor` surface-farming → fixed.** Specific tokens in `Baselines` only count toward the
  density bonus if they *recur* in the same experiment's `Setup`/`Procedure` (corroboration pool).
  A comparator name dropped only into the `Baselines` line now scores as generic.
- **Cycle punishment too soft → fixed.** A cycle now hard-caps the whole metric at `min(base, 0.25)`,
  not just zeroing one 20%-weighted term.

### B (Proposer 1 / stage-1 agent1) — yes, all four, at the compute level
- **Brittle hardcoded genre dictionaries → fixed.** `Method–Measurement Fit` dropped the genre
  buckets entirely for a genre-agnostic within-block consistency check (does `Metrics` vocab recur
  in this block's own `Setup`/`Procedure`?), plus a `copy_penalty` for the degenerate verbatim-copy
  win. This is the cleaner fix — it stops penalizing legitimate free-form `Setup` (e.g. systematic
  reviews) and can't be farmed by keyword-stuffing every genre at once.
- **Magic numbers → fixed and justified.** `diversity_bonus` went from an unjustified `×1.1` to an
  additive `+0.15` with a stated rationale (comparator diversity is binary/structural, so a
  multiplicative bonus rewards the wrong files); the `0.7/0.3` triangulation blend became a
  multiplicative structural gate.
- **Triangulation blind to real claims → fixed.** `triangulation_load` now takes `claim_ids` as a
  required input, zeroes credit for dangling citations, and folds a `dangling_ratio` into the gate.
  Missing `claim_ids` returns 0 (penalty, not skip).
- **`SequenceMatcher` order-sensitivity → fixed.** Both the fake-triangulation detector and the
  anti-padding check switched to order-invariant token-set Jaccard, with the padding floor retuned
  (0.4→0.3) for the Jaccard scale. This closes the reorder/rename evasion.

Both winners did the work. Neither merely re-argued in prose; each converted its critique into
arithmetic. This is a genuinely close call.

## (2) WINNER: B

### Why B over A
The tie-breaker is *what each set's strongest, most-differentiated metric actually measures*.

- B's crown jewel, **Triangulation / Verification Load**, measures the deepest science signal in
  the whole field: a claim corroborated by two or more *genuinely distinct* experiments is harder
  to explain away as a single methodological artifact. Independent replication of support is a real
  property of good science, not a text surface — and B now binds it to `claims.md`'s real id space
  and gates it multiplicatively so a few well-triangulated claims can't buy back a file of orphaned
  or dangling citations. A has claim *coverage* (breadth: is each claim backed by ≥1 experiment),
  which is more mechanical — a 1:1 experiment-per-claim mapping satisfies it. Depth beats breadth
  here.
- B's **Method–Measurement Fit** (genre-agnostic within-block grounding) is less Goodhartable than
  A's **Setup/Procedure Grounding**, which still rewards `CONCRETE_TOKEN` density — CamelCase/version
  jargon that is farmable by jargon injection (A leans on the cross-experiment redundancy check to
  catch this indirectly). B's grounding requires `Metrics` vocab to be anchored in the same block's
  method text and directly penalizes the copy-paste degenerate case.
- B spends all five metric slots on science-quality properties (falsifiability, comparator rigor,
  method-measurement consistency, triangulation, structural integrity). A spends one slot on
  `Declarative Purity`, a numeric-leakage *defect detector* — useful compiler-hygiene, but it
  measures compile discipline, not science.

A is excellent and arguably has the single most Goodhart-resistant metric for *structural
completeness* (richness-weighted cross-layer closure with a hard cycle cap). If the goal were
"is this artifact wired together and compiled carefully," A wins. For "does this measure good
science," B's triangulation-centered set edges it.

## (3) QUALIFY the winner

**What B genuinely measures.** B is an honest, well-interlocked measure of the *structural and
lexical hallmarks of a carefully-constructed experiment plan*: (a) whether predictions are
directional/falsifiable and lexically tied to what's measured; (b) whether comparators are named
and typed (internal vs external); (c) whether stated measurements are anchored in the block's own
method description; (d) whether claims are cited by multiple textually-distinct experiments that
actually exist in `claims.md`; (e) whether the dependency graph is a valid, non-padded DAG. It
honors the hard constraint throughout — every missing/empty field is an active penalty, missing
`claim_ids` returns 0, and thin/short files are floored, never skipped. The metrics interlock via
shared token-overlap computation, so most single-axis gaming moves leave a fingerprint on a second
metric.

**Where it is still gameable or limited.**
- **Everything is lexical.** "Independent corroboration" in Triangulation is operationalized as
  *token-set distinctness* of `Setup`+`Procedure`, not methodological independence. Two experiments
  that are the same method described in genuinely different vocabulary would score as independent
  support; conversely two truly distinct methods sharing heavy shared jargon could collapse into
  one. It measures textual diversity of support, which correlates with — but is not — real
  triangulation.
- **Grounding is vocabulary overlap.** A sophisticated author who threads consistent real-sounding
  terminology across `Setup`/`Procedure`/`Metrics`/`Expected outcome` can satisfy Metrics 1 and 3
  without the underlying study being sound. The checks reward internal lexical coherence, which a
  fluent bad-faith compile can manufacture.
- **No contact with `evidence/` or ground truth.** B never checks whether the plan's expected
  outcomes were actually borne out, whether the experiments were run, or whether the claims are
  true. It scores the *plan's* internal quality, blind to real-world validity.
- **Binary claims.md dependency.** Unlike A's continuous `claims_availability`, B treats
  `claim_ids` as all-or-nothing; a partially-parsed claims file isn't modeled (it satisfies the
  hard constraint, but degrades less gracefully than A).

**What it would take to trust it.** Semantic (not lexical) grounding and independence checks — e.g.
an LLM-judge or embedding-based assessment of whether two experiments are *methodologically*
independent and whether an outcome is a real prediction about a measured quantity — plus binding to
`evidence/` to confirm the plan connects to actual results. Calibration against a labeled set of
strong vs. abstract-only compiles would be needed to trust the absolute scores.

**Does it clear the bar?** Honest-but-limited. B measures structural rigor and lexical coherence
that are strongly *correlated* with careful science and is meaningfully Goodhart-resistant against
cheap single-file edits. It does not measure scientific validity or true methodological
independence, and a determined, fluent gamer operating at the semantic level can still score well.
It is the best available proxy in this field, not a measure of good science itself.
