# M17 — Novelty vs literature (+ impact) — Round 2, Cycle 1 critique

Metric M17 = "done before?" for claims/insight/gap/method/concept against external literature,
plus societal/science impact-if-solved. Net-new edge: the internal verifier judges internal scope
and never done-before; M17 must *leave the artifact* and check the outside world via [ext]/[sem]
calls, converting them into deterministic sub-scores, honoring penalize-don't-skip, and resisting
Goodhart.

Judging axes: (1) reasoning correctness; (2) concrete/runnable generation-compute workflow with
real [ext]/[sem] steps → deterministic sub-scores; (3) Goodhart-resistance under scrutiny;
(4) penalize-don't-skip (unresolvable external search scores down, never N/A); (5) preserves the
net-new external edge (never collapses into an internal-consistency/verifier duplicate).

---

## Per-expander verdict + rank

### Rank 1 — exp1 (WINNER)

**Verdict: strongest.** Sharpest grasp of *why* the metric is net-new, and the only design whose
core score is almost entirely external-grounding with internal structure relegated to an
availability multiplier rather than blended into the headline number.

Strengths:
- **Dual differently-biased retrieval as a hard requirement**: semantic-scholar (lexical/citation
  graph) AND undermind (embedding/semantic recall), with a unit credited novel only if *both* come
  back clean. This is the strongest anti-relabeling / anti-term-substitution mechanism in the field;
  an author controls their own prose but not two independent external indexes.
- **Retrieval confidence is a first-class, scored term**: unsearchable=0, both-indexes-empty=0.6
  (capped provisional novelty, never certainty), real candidates=1.0. Correctly refuses to treat
  "search returned nothing" as proof of novelty — directly closes the "pick an obscure domain to
  win" route.
- **Fixed, artifact-driven unit set** (KI 1.0, all Gaps 0.8, highest-in-degree anchor claim 0.6,
  method 0.5) removes the cherry-pick-the-easy-unit route — the LLM does not get to choose which
  contribution to defend.
- **Self-disclosure asymmetry** (§6.4): an externally-found strong match that is *disclosed* in a
  real RW block with Type+Delta is penalized far less (0.05) than a silent one (0.30). This rewards
  honest lit-review rigor and punishes obscured non-novelty — a genuinely clever, hard-to-game
  incentive.
- **Impact rubric is fed only structural facts** (dependent-claim count, ClinicalTrials.gov
  field-activity count) with an explicit instruction to ignore the paper's own enthusiasm language;
  ClinicalTrials.gov [ext] is used only as an impact signal and explicitly *not* as a novelty
  signal (an active trial pipeline ≠ the specific gap is closed). Correct, careful separation.
- Deterministic overlap→strength map with hard-fail on malformed LLM JSON (no silent default);
  per-unit strength = max over candidates ("one strong match means done-before").

Weaknesses / scrutiny (fixable, cycle-2 material):
- **Composite bug undermining the confidence discount.** In `score_M17`, for a *searchable* unit
  whose two queries return nothing, `unit_prior_art_strength` returns 0.0 (empty candidates), and
  `effective_strength = strength*conf + (1-conf)*1.0*(searchable==False) + penalty` reduces to
  `0*0.6 + 0.4*0 + 0 = 0`, so novelty ≈ 1.0. The stated intent — cap empty-search novelty via the
  0.6 confidence — is computed but never actually bites. As written, a well-formed query that finds
  nothing still scores full novelty, contradicting §6.2's design narrative.
- The `effective_strength` line is genuinely muddled — the author's own note admits the branch
  logic is confusing and partly vestigial. Needs to be rewritten as a clean, testable function.
- `n_dependent_claims` is computed by constructing throwaway `{"id": u.unit_id}` dicts and matching
  gap ids against claim `dependencies`; brittle and probably miscounts. Needs a real gap→claim
  dependency traversal.

Net: conceptually the best-aligned with the brief's central demands (net-new edge + Goodhart), with
concrete code that has a real but localized composite bug. The framework is right; the arithmetic
needs repair.

### Rank 2 — exp2 (WINNER)

**Verdict: strongest of the "comprehensive" designs.** Most complete, most runnable, cleanest
multiplicative composition, and a dimension-separated matching scheme that is a strong
relabeling defense in its own right.

Strengths:
- **Dimension-separated overlap classification.** The LLM classifier returns `matched_dimensions` /
  `missing_dimensions` over {problem, method, claim, population, outcome, concept} and buckets into
  already_done / close_predecessor / enabling_background / unrelated. Because a match must line up
  on the *technical core dimensions*, pure terminological relabeling (same mechanism, new words)
  cannot dodge it — a solid Goodhart defense even without a second index.
- **Multiplicative per-target novelty**: `specificity * literature_coverage * delta_quality *
  (1 - done_before_penalty)`. A single `already_done` hit (penalty 1.0) zeroes that target cleanly;
  vagueness (low specificity) and missing delta each independently gate the score. No single lever
  can be gamed in isolation.
- **Penalize-don't-skip done cleanly**: classifier failure → `candidate_overlap="unknown"`,
  confidence 0, scored as *partial close-predecessor risk* (0.25), never ignored; explicit
  `precondition_penalty` for external_search_failed / trial_lookup_failed /
  >half-targets-unparseable / related-work-too-thin, applied as a multiplier. Nothing routes to N/A.
- Concrete, genre-aware [ext]/[sem] calls: Semantic Scholar relevance + exact-phrase queries,
  ClinicalTrials.gov for clinical/interventional targets, arXiv for formal-method targets, each with
  an explicit "failure to query is penalized" clause.
- The full `m17_score` reference function is complete and directly runnable given the target/flag
  inputs; sub-scores are all deterministic; interpretation bands are provided.

Weaknesses / scrutiny (cycle-2 material):
- **`literature_coverage` is multiplied *into* novelty**, defined as `min(1, relevant_candidates/10)`.
  This means a genuinely novel gap in a sparse literature (few relevant comparators retrieved)
  scores *low* novelty — it conflates "we couldn't retrieve a comparator set" with "not novel." It
  is defensibly conservative (can't win by being obscure, consistent with penalize-don't-skip), but
  it also penalizes true novelty and should be reframed as a *confidence* term (à la exp1's
  retrieval_confidence) rather than a straight multiplier on the novelty verdict.
- Single retrieval family (Semantic Scholar variants). The dimension-separated classifier partly
  compensates, but it lacks exp1's independent second-index guarantee against relabeling.
- Impact and novelty both lean on the same retrieved-metadata bundle; the impact prompt is
  well-guarded against hype but could double-count retrieval quality.

Net: the most polished, complete, and immediately-executable design, with a strong independent
relabeling defense and textbook penalize-don't-skip. The coverage-as-multiplier choice is its one
real correctness smell.

### Rank 3 — exp4 (loser)

Granular comparator (separate same_gap / same_key_idea / same_method_or_concept / already_solved),
comparator-confidence weighting by abstract availability, a "fatal prior-art" backstop
(`0.35 * max_done_before`), explicit external-failure handling, and the best audit/reporting fields
(top_prior_art_matches with DOI + rationale). But `unit_novelty_score` dilutes the done-before
signal (only 0.45 weight on `1-done_before`, the rest specificity/cross-layer/retrieval), so a
fully-done-before unit can still score ~0.4 novelty before the separate fatal penalty compensates —
muddled double-handling; single index; weaker relabeling guarantee than exp1/exp2.

### Rank 4 — exp3 (loser)

Most deterministic machinery (Jaccard entity/mechanism/objective overlap + embedding cosine + LLM
relation classes + disclosure-reward), and complete runnable code. But it dilutes the net-new edge
most: roughly half the weighted score (availability_richness, gap_specificity,
literature_positioning, scope_honesty = 0.15+0.15+0.15+0.05) is internal artifact-quality grading
that overlaps the verifier and the related-work-comprehensiveness metric, leaving external_novelty
at only 0.35. Against the brief's central instruction to *preserve the external done-before edge*,
this is the weakest — it drifts back toward an internal-consistency check.

---

## WINNERS: exp1, exp2

---

## Winner critiques + cycle-2 directions

### exp1 — cycle-2 directions
1. **Fix the composite so retrieval confidence actually bites.** Rewrite `effective_strength` as a
   clean function where an empty-but-well-formed search yields *provisional* novelty capped by the
   0.6 confidence (e.g. `novelty_credit = 1 - strength`, then blend toward a neutral prior with
   weight `(1 - conf)` so empty search cannot reach full novelty). Provide a unit test table for the
   three regimes: unsearchable, searchable-empty, searchable-with-hits.
2. **Repair `n_dependent_claims`** with a real gap→claim dependency traversal instead of throwaway
   dicts; state exactly which edge in `claims.md` Dependencies constitutes "depends on this gap."
3. **Specify the undermind/[sem] contract concretely** (endpoint, params, what "strong overlap"
   threshold means) so the dual-index requirement is runnable, not aspirational.
4. Keep the disclosure asymmetry and structural-only impact rubric intact — they are the design's
   crown jewels; do not water them down.

### exp2 — cycle-2 directions
1. **Reframe `literature_coverage`.** Split it into (a) a retrieval-*confidence* term that discounts
   the novelty *verdict* toward a neutral prior when the comparator set is thin, and (b) keep the
   penalize-don't-skip intent — but stop letting a sparse-literature true-novel gap collapse to ~0
   novelty purely for lack of retrieved comparators. Borrow exp1's `retrieval_confidence` shape.
2. **Add a second, differently-biased retrieval pass** (embedding/semantic recall) to harden the
   relabeling defense, since the current single-family search leans entirely on the LLM classifier.
3. Make explicit how impact avoids double-counting retrieval quality already used in novelty.
4. Preserve the dimension-separated classifier and the multiplicative per-target gating — they are
   the strongest parts.

---

## Loser one-liners
- **exp3**: Best deterministic code, but ~half the score is internal artifact-quality grading that
  duplicates the verifier/related-work metric — dilutes the net-new external edge the brief most
  wants preserved.
- **exp4**: Granular comparator and good auditability, but `unit_novelty_score` dilutes the
  done-before signal (0.45 weight) and then re-adds a separate fatal penalty — muddled
  double-handling, single index, weaker relabeling guarantee than the winners.
