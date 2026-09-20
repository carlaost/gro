# M09 — FOL-ability (Oshima principles) — Cycle-1 critique

Metric: can a clean first-order-logic graph be built over `logic/claims.md` — net-new
formal-checkability signal. Judged on: reasoning; concrete/runnable workflow (claims→FOL
translation + graph-constructability → deterministic sub-score, incl. how the FOL-solver / `[sem]`
step is actually scored); Goodhart-resistance; penalize-don't-skip; genuine net-new-ness.

The decisive axis this round: the brief explicitly asks *how the solver / `[sem]` step is scored*.
Two proposals name `[ext] FOL` but implement the "solver" as just another LLM call (exp1, exp3).
Two implement a genuine deterministic/symbolic solver step (exp2, exp4). That, plus Goodhart depth,
separates the field.

---

## exp1 — verdict: STRONG, but the "solver" is an LLM. Rank 3.

**Strengths.** Best single conceptual insight in the field: the explicit separation of *coverage*
(how many claims) from *graph-ness* (how connected/consistent the entailment structure is), with a
matching countermeasure — `edge_vocabulary_consistency` actively *subtracts* credit for cosmetic
`Dependencies` padding rather than merely under-rewarding it. Multiplicative per-claim scoring
(`c*f*n*g`) correctly makes cleanliness conjunctive. Cycle detection as a hard deterministic cap
(0.2), applied after and independent of the per-claim LLM scores, is exactly right. The `[sem]`
handling is the most disciplined of anyone's: a *fallback disambiguator* that can only lift a term
out of a penalized-ambiguous state, never substitute for formalization — thoughtfully scoped.
Penalize-don't-skip is thorough (thinness dampener, pending-fraction, bad-source floor).

**Weakness that drops it below the winners.** The ledger's `[ext] FOL` step (Step 3) is an LLM
formalizer emitting JSON, and the negation check (Step 4) is a second LLM call. There is **no
symbolic solver anywhere** — nothing is ever handed to a theorem prover or SAT/SMT backend, even
though the whole reasoning section is built around "could be fed to a theorem prover." The metric
therefore rests entirely on two LLM judgments plus deterministic graph checks. That is defensible,
but on the brief's explicit "how is the solver step scored" axis it is materially thinner than exp2
(runnable status-consistency solver + Z3 upgrade path) and exp4 (actual Z3). Given how close exp1
is on every other axis, this is the tiebreaker.

---

## exp2 — verdict: WINNER. Rank 1.

**Strengths.** The only proposal that concretely operationalizes *both* the solver step *and* the
`[sem]` step the brief calls out, and scores both:

- **Solver step (Step 4, `[ext] FOL` status-consistency):** treats `Status` as a truth assignment
  (supported→True, refuted→False, hypothesis→unassigned) and walks the `Dependencies` DAG for
  assignments a first-order reasoner would reject (a `supported` claim resting on a `refuted` or
  unresolved-`hypothesis` ancestor). Crucially, it ships a **runnable standalone** deterministic
  version (`nx.ancestors` + topological sort) *and* names the Z3 upgrade path — so it's real today,
  not aspirational. `consistency_penalty` scales with violation count.
- **`[sem]` step (Step 5, missing-edge detection):** the sharpest anti-gaming idea in the field.
  It uses semantic predicate overlap to catch the dominant evasion — a compiler writing
  `Dependencies: none` on every claim to trivially pass cycle/consistency checks while the claims
  are obviously logically entangled. `fragmentation_penalty` punishes exactly this. No other
  proposal closes this route (exp4 explicitly *ignores* `[sem]`).
- **Stability re-run (Step 2):** two independent formalization passes at different
  temperature/paraphrase, scored by Jaccard on predicate sets *and* agreement on the F/¬F verdict.
  This is the single best defense against a lenient/sycophantic formalizer rubber-stamping
  incoherent input — hallucinated structure doesn't reproduce. Genuinely distinctive.
- **Goodhart section is the most complete**, including the status-gaming route (mark everything
  `hypothesis` to dodge contradiction detection) and why it self-defeats via the `g_relation_to_notF`
  ceiling and the shape doc's own "Status skews supported" prior.
- Penalize-don't-skip is clean: hard-0 on missing `Falsification criteria`/`Dependencies`,
  `thinness_penalty` capping `graph_score` for <5-claim compilations, LLM-timeout→`well_formed=False`.

**Weaknesses (for cycle 2).** (1) The 0.6/0.4 formalizability/graph split is asserted, not
justified — defend or sensitivity-test it. (2) `missing_edge_candidates` is wired with
`sem_similarity=None` in the aggregate call — the actual semantic model is unspecified; name a
concrete embedding/similarity backend and the ≥2-shared-predicate threshold's calibration. (3) The
stability re-run doubles LLM cost per claim — note the budget and whether it's gated to only
borderline `well_formed` cases. (4) `status_consistency` iterates `g.nodes` when the graph is
cyclic, but cycles should already have hard-failed `dag_penalty`; make the ordering explicit.

---

## exp4 — verdict: WINNER. Rank 2.

**Strengths.** The most runnable and the most scoping-disciplined proposal, and the only one with a
genuine symbolic solver in the loop:

- **Real solver:** `status_consistency_multiplier` composes one global KB in Z3 (supported→assert,
  refuted→assert¬, `Dependencies`→implication `claim → dependency`) and checks `sat` — a genuine
  SMT consistency pass over the whole asserted claim set, penalizing the artifact if the composed KB
  is contradictory. This is the closest anyone gets to the "hand it to a theorem prover" promise.
- **Sharpest scoping discipline:** explicitly enumerates the fields it uses (`Statement`, `Status`,
  `Falsification criteria`, `Dependencies`, `Sources` values only) *and* the fields it deliberately
  does **not** touch (`Proof`, `Evidence basis`, `Interpretation`, `Tags`) — the cleanest guarantee
  of non-redundancy with grounding/SL1 metrics in the whole field.
- **All scoring is deterministic code over the LLM's structured output** — the translator emits only
  FOL text; every accept/reject (syntax, negation-consistency, constant-groundedness, cycle-freedom,
  status-consistency) is non-LLM. Strong anti-Goodhart posture.
- **Best penalize-don't-skip worked-through section** in the field: absent file, abstract-only, bare-
  path Sources, and zero-clean-claims are each traced through the exact code path and scored down
  distinctly (e.g. zero-clean → ×0.5, not zeroed, so it reads worse than a handful-clean but better
  than no-claims-file). The per-claim score ladder (0.0 / 0.05 / 0.2 / 0.2+0.3g / 1.0) is legible
  and defensible. Sparse-graph penalty (<3 clean claims) defeats padding-with-easy-claims, reinforced
  by `constants_grounded` zeroing content-free boolean claims.

**Weaknesses (for cycle 2, one is important).** (1) **The Z3 negation check is partly decorative.**
In `negation_consistent`, the real discriminating work is the *lexical* symbol-overlap check; the Z3
block (`Not(And(P,notP))`, `Or(P,notP)`, `P==Not(notP)`) over abstracted booleans is trivially `sat`
by construction and verifies nothing semantic — the FOL content of `predicate_form`/`negation_form`
never actually enters the solver. Either make the solver genuinely consume the formulas (share a
real signature, check `predicate_form ∧ negation_form` UNSAT with the actual predicates) or drop the
Z3 theater here and be honest that negation-consistency is a lexical + LLM-structure check. (2) **No
`[sem]` step at all** — Step 3's heading says `[sem]/[ext]` but the workflow never uses semantic
search, and the "none-everywhere `Dependencies`" gaming route exp2 catches is left open. Address the
`[sem]` leg the brief asks about. (3) `constants_grounded` substring match (`c in s or s in c`) will
false-positive on short numerals (e.g. `"0.1"` matching inside `"0.117"`); tighten to token/boundary
match. (4) Per-claim uses `call_fol_translator` internally, coupling I/O to scoring — exp3's injected
`llm_calls` interface is cleaner for testability; consider adopting it.

---

## exp3 — verdict: STRONG framing, workflow diverges from it. Rank 4.

**Strengths.** The best *philosophical* articulation of the metric: FOL-ability as "is the claim's
own prose already doing the logical work, such that formalization is lossless transcription rather
than lossy interpretation" (the Oshima reading). The `assumptions_injected` + `residual_prose`
self-reports, cross-checked against the statement text, are a genuinely good idea for detecting
formalization theater — rewarding claims that need *no invented predicates*. The injected `llm_calls`
interface keeps the aggregator pure and testable (cleanest engineering of the field). Worked example
against the shape doc's real C01 grounds the whole thing.

**Weaknesses that drop it to rank 4.** (1) **Reasoning-implementation gap:** the section builds its
whole case on "two independent formalization attempts *converge*," but the implemented workflow does
a single generation + a single negation-verifier — there is no convergence diff / stability re-run
(exp2 actually implements this). The headline claim isn't in the code. (2) **No solver:** the
verifier is an LLM emitting an `entailment_score` float; nothing symbolic, weakest of the field on
the brief's explicit solver axis. (3) **Additive per-claim scoring** (weighted sum) is more gameable
than exp1/exp4's multiplicative/gated forms — a strong grounding score can partly mask a weak
negation. (4) `assumption_penalty` rests on a crude `_keyword_overlap` heuristic (>3-char word hit)
that is itself easy to game and noisy. Solid proposal, but out-executed on every measured axis.

---

WINNERS: exp2, exp4

## Cycle-2 directions for winners

- **exp2:** justify/sensitivity-test the 0.6/0.4 weighting; name the concrete `[sem]` similarity
  backend and calibrate the ≥2-shared-predicate threshold; state the stability-re-run budget and
  whether it's gated to borderline claims; make the cyclic-graph node ordering in
  `status_consistency` explicit.
- **exp4:** fix the decorative Z3 negation check — make the solver genuinely consume the formulas or
  drop it and be honest about the lexical+structure check; add the missing `[sem]` leg (and the
  none-everywhere `Dependencies` gaming route it closes); tighten `constants_grounded` to
  boundary/token match; adopt an injected LLM-call interface for testability.
- **Cross-pollination:** exp4 should borrow exp2's `[sem]` missing-edge detector and stability
  re-run; exp2 should borrow exp4's explicit "fields NOT used" scoping declaration and its Z3
  status-KB `sat` check as the upgrade for its own Step 4.
