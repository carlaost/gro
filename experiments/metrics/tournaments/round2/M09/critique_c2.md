# M09 — FOL-ability (Oshima principles) — Cycle-2 critique

Metric: can a clean first-order-logic graph be built over `logic/claims.md` — net-new
formal-checkability signal. Cycle-2 round: both A (improved exp2, prior Rank 1) and B (improved exp4,
prior Rank 2) advance to cycle 3. **No final winner declared this cycle.** This critique judges how
well each closed its four named cycle-1 weaknesses, surfaces what each still gets wrong, and gives
specific cycle-3 directions on the three axes the brief foregrounds: **claims→FOL translation
soundness, graph-constructability scoring, penalize-don't-skip.**

The decisive movement this cycle: on the brief's own headline axis — *how is the solver step actually
scored* — **B leapfrogged A**. B now parses both `predicate_form` and `negation_form` against a real
grammar, grounds quantifiers, and hands the *actual formulas* to Z3 with a shared atom cache. A, by
contrast, still rests its per-claim negation verdict entirely on an LLM self-report
(`g_relation_to_notF`), and its headline "genuine Z3 upgrade" is, as implemented, decorative (see
below). But B over-corrected: its solver is now *too strict* and mis-scores the realistic
falsification-criteria pattern the shape doc itself exhibits. That symmetry — A under-verifies
negation, B over-constrains it — is the core cross-pollination axis for cycle 3.

---

## A (improved exp2) — verdict: three of four fixes land; the flagship Z3 fix does not.

### What it fixed well
- **Weakness 1 (weighting), fully addressed and arguably the best fix in either file.** Pulling
  structure-breaking defects (cycles, dangling refs) *out* of the 0.6/0.4 weighted sum and making them
  a hard override on the *final* score (Step 6, lines 428-440) is exactly right: a cyclic graph is a
  "no" to the metric's headline question, not "a clean graph that scored 0 on 40% of its axes." The
  sensitivity table (Step 6b, lines 484-495) is a genuine, honest justification — it shows rank-order
  stability across 0.5/0.5–0.7/0.3 and correctly concludes the split only needs to be "reasonable, not
  razor-edged" because the hard gate carries the load. This is the model for how to defend a magic
  number.
- **Weakness 2 ([sem] backend), addressed well.** Naming `BAAI/bge-small-en-v1.5` (local, deterministic,
  matching the no-external-API ethos), the hybrid cosine-AND-shared-entity criterion (lines 348-355),
  the calibration sweep (lines 385-391), and the lexical fallback (lines 369-382) together close the
  cycle-1 `sem_similarity=None` gap. The shared-entity *anchor* is the real insight: it kills the
  bare-cosine threshold-gaming route and the "similar verb, unrelated entities" false-positive at once.
- **Weakness 3 (stability cost), cleanly gated.** `run_b` fires only when `run_a["well_formed"]` (lines
  189-194), and the "can't be gamed" argument (lines 203-207) is correct: `well_formed=False` already
  caps the claim at 0.0, strictly worse than any stability-discounted score, so the gate creates no
  incentive gradient. Budget stated (1.2–1.6×N typical).
- **Weakness 4 (ordering), correctly fixed by construction.** Asserting `is_dag` as a precondition
  (lines 244-247) and short-circuiting the whole score at the Step 6 hard gate *before*
  `status_consistency` is ever reached makes the old arbitrary-traversal fallback dead code rather than
  a patched bug. Right call.
- Cross-pollination: the "fields used / NOT used" table (lines 66-72) is adopted cleanly and does the
  non-redundancy work in a table rather than prose.

### Remaining weaknesses
- **The flagship "genuine Z3 upgrade" is decorative — the exact flaw A claims to have fixed in exp4.**
  This is the important one. `build_status_kb` (lines 271-296) registers a shared atom per canonical
  predicate via `atom(pred)` (line 287) — but **those atoms are never asserted into any clause**. Every
  `s.add(...)` operates on the opaque per-claim `stmt[c["id"]]` booleans (lines 288-295); the `atoms`
  cache is populated and then inert. A's own Changes section (#5b, lines 34-38) sells this as sharing
  "*actual* predicate atoms across claims (not per-claim abstracted booleans, which is the exact defect
  exp4's own critique flagged)" — but as written, the KB *is* per-claim abstracted booleans plus
  `Dependencies` implications, with the predicate-atom layer doing nothing. The docstring even hedges
  this ("a full formula_F → Stmt_c biconditional … is a natural further upgrade"). Verdict: the
  status-implication SAT check over `Stmt_` booleans is genuine and useful *as a status-consistency
  check*, but the "joint predicate KB" framing is unearned. A reproduced exp4's cycle-1 decorative-Z3
  pattern while explicitly criticizing it.
- **Per-claim negation soundness is still 100% LLM self-report.** `g_relation_to_notF` is emitted by the
  Step 1 LLM (lines 156-159) and consumed directly by `score_claim` (lines 410, 416) with no symbolic
  verification that `formula_G` is actually `¬formula_F`. `formula_F` is described as "solver-opaque"
  (line 276) and never parsed. The stability re-run defends against *non-reproducible* hallucination,
  but two independent lenient passes can still *agree* on a wrong `negation` verdict. On the brief's
  "translation soundness" axis, this is now A's weakest flank — and it is precisely what B fixed.
- **`[sem]` introduces the one nondeterministic dependency the rest of the metric avoids.** A argues the
  local embedding model preserves the no-external-API ethos, but cosine values are model-version-bound
  (A acknowledges this, lines 390-391), so `SEM_THRESHOLD=0.80` is not portable and the check's verdicts
  drift with model updates. B's numeric-constant signal is fully deterministic. Worth weighing.

---

## B (improved exp4) — verdict: the strongest single fix in the round, but the fixed solver is now over-strict.

### What it fixed well
- **Weakness 1 (decorative Z3), fixed substantively — the best improvement in either file.** The
  recursive-descent parser (lines 328-405), finite-domain grounder (lines 426-460), and shared atom
  cache in `to_z3` (lines 463-482) mean the solver now consumes the *actual parsed content* of both
  formulas. `negation_consistent` (lines 497-532) checks `UNSAT(P ∧ N)` and `UNSAT(¬P ∧ ¬N)` over atoms
  that are genuinely aliased across the two formulas. This is a real, runnable, non-decorative solver
  step — exactly what the cycle-1 critique demanded, and it is now the only proposal in the field where
  the FOL content actually enters the prover. Making an ungroundable quantifier an explicit penalized
  failure (lines 426-434) rather than a skip is a bonus.
- **Weakness 2 ([sem] leg), added without a new nondeterministic call.** Reusing already-parsed numeric
  constants (lines 592-623) is elegant, and the calibration argument for *numeric* over *entity* overlap
  (lines 567-581) is sound: entity names recur trivially because the paper is *about* the entity, but a
  matching statistic at ≥3 sig-figs only recurs when one claim's conclusion is another's premise. The
  worked tie to the shape doc's C01 P-scores (line 580) grounds it.
- **Weakness 3 (boundary-safe matching), fixed.** `_boundary_match` (lines 539-553) correctly rejects
  `"0.1"` inside `"0.117"` via digit/`.` flank checks while still matching numerals embedded in prose.
- **Weakness 4 (testability seam + gated stability), both delivered.** The injected
  `translate: Callable` (lines 704-707) decouples I/O from scoring, and the stability re-run is gated to
  the borderline band `[0.05, 0.8)` (lines 655-666). The "outcome band, not compiler-controllable"
  anti-gaming argument (lines 791-796) is correct and tighter than A's justification.

### Remaining weaknesses
- **The fixed solver over-rejects the canonical falsification pattern — the most important cycle-3
  issue.** `negation_consistent` demands *both* `UNSAT(P ∧ N)` (N sufficient for ¬P) *and*
  `UNSAT(¬P ∧ ¬N)` (N necessary for ¬P) — i.e. N must be the *exact* logical negation of P. But real
  falsification criteria are almost always *sufficient conditions*, not exact negations. The shape doc's
  own C01 (02_claims.md lines 59-61) is a disjunction: "Refuted if p181_IA outranked p217_MS **or** if
  p217_MS's AUC advantage were non-significant." That is a sufficient-for-negation, not a biconditional;
  `¬P ∧ ¬N` is satisfiable (P can be false without either specific disjunct firing), so B's check returns
  `False` and scores the canonical, well-formed claim at `0.2` (line 650). B's genuine solver is thus
  *more* sound in machinery but *less* sound in scoring intent than A's, which explicitly grades
  `negation | sufficient_for_negation | neither` and awards 0.6 to the sufficient case (A lines 158, 416).
  This is the clearest place B regressed relative to what the metric should reward.
- **[sem] recall is narrow.** Numeric-constant overlap only catches entanglement routed through a shared
  *statistic*. A claim that genuinely depends on a *qualitative* prior finding (no reused number) is
  invisible to `missing_edge_candidates`. The precision argument is good; the recall gap is real and
  unacknowledged. A's entity-anchored embedding catches a class B misses.
- **Parser brittleness has no repair path.** A well-formalizable claim whose LLM output has one
  off-grammar token parses to `None` → `0.05` (lines 646-647). That is correct penalize-don't-skip
  *in principle*, but with no retry/repair a formatting slip is scored identically to genuinely
  unformalizable content. Consider a single re-ask on `ParseError` before assigning the hard-fail bucket.
- **Minor:** `missing_edge_candidates` is computed twice (once in `fragmentation_multiplier` line 629,
  once in the return dict line 745); `_sig_figs` (lines 587-589) mis-counts trailing-zero integers
  (`"100"` → 3 sig-figs). Neither is load-bearing.
- **All-`hypothesis` blind spot** is present (status multiplier is trivially SAT with everything
  unassigned) but, unlike A, B does not name it. A's explicit call-out (A lines 548-555) is better
  hygiene.

---

## Cycle-3 directions

### Axis 1 — claims→FOL translation soundness
- **A (highest-priority fix):** stop resting negation soundness on the LLM's `g_relation_to_notF`
  self-report. Adopt B's parser + grounder + shared-atom Z3 encoding to *verify* the F/¬F relation
  symbolically. Either parse `formula_F`/`formula_G` (currently "solver-opaque") for real, or drop the
  "genuine Z3" framing entirely and be honest that formalization is an LLM-structure + stability check.
  Also: fix or delete the decorative shared-atom layer in `build_status_kb` — as written it verifies
  nothing beyond the `Stmt_` implication KB.
- **B (highest-priority fix):** relax the exact-negation requirement. Make `UNSAT(P ∧ N)` (N is
  *sufficient* to falsify P) the primary gate at full or near-full credit, and treat `UNSAT(¬P ∧ ¬N)`
  (exhaustiveness) as a *bonus* tier, not a pass/fail requirement — mirroring A's
  `negation / sufficient_for_negation / neither` ladder. As-is, B penalizes the shape doc's own C01.
- **Both:** the ideal cycle-3 artifact is B's solver machinery scoring A's three-way relation ladder.

### Axis 2 — graph-constructability scoring
- **A:** the hard structural gate (cycles/dangling → `0.05 * claim_avg`) is the right shape; keep it.
  But make the `[sem]` fragmentation signal deterministic-portable, or ship B's numeric-constant signal
  *alongside* the embedding one so verdicts don't drift with model version.
- **B:** widen `[sem]` recall. Add an entity-overlap signal (A's shared-argument anchor) as a
  lower-weight second channel to the numeric-constant channel, so qualitative-dependency entanglement
  isn't invisible. Consider adopting A's hard-override treatment of cycles/dangling refs: B currently
  folds them into a `0.3`/`0.5` *multiplier* (lines 682-685), which — like exp2's cycle-1 form that A
  fixed — still lets a strong `mean_claim_score` produce a non-trivial final score on a non-DAG. A's
  argument that a broken graph is a categorical "no," not a 30% ding, applies to B too.
- **Both:** name and (eventually) close the all-`hypothesis`-trivially-SAT blind spot, or explicitly
  hand it to a `Status`-distribution cross-check and document the boundary.

### Axis 3 — penalize-don't-skip
- **A:** solid throughout; the `0.05 * claim_avg` floor (vs. flat 0.0) to avoid conflating a
  one-dangling-ref file with an empty file (lines 437-440) is a thoughtful touch. Keep it. Main gap is
  that a decorative check (the shared-atom Z3) is not a *penalty* path at all — it neither penalizes nor
  skips, it just does nothing; remove it so "every step scores something" stays true.
- **B:** add a parse-repair retry before consigning an off-grammar-but-formalizable claim to the `0.05`
  bucket, so brittleness of the grammar isn't miscounted as unformalizability. Otherwise B's
  worked-through degraded-input section (lines 750-771) remains the most complete in the field — keep it.
- **Both:** neither yet handles the `[pending: ...]` Sources convention (shape doc lines 46-47) — a
  claim whose grounding is honestly deferred should read as *thinner*, not as ungrounded/failed.
  Cycle 3 should score `[pending]` as a distinct, mildly-penalized tier rather than letting it fall
  through the constant-groundedness path as a plain miss.

---

Both proposals advance to cycle 3. A leads on graph-constructability scoring (hard structural gate,
sensitivity-justified weighting) and Goodhart bookkeeping; B leads decisively on translation soundness
(the only genuine solver-over-formulas in the field) but must fix its over-strict negation test. Convergence
target: B's solver machinery driving A's sufficient-vs-exact relation ladder and hard structural gate.
