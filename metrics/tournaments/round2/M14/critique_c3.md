# M14 (Reference-landscape completeness) — critique, round 2 cycle 3 (FINAL)

**WINNER: A** (former exp2, Rank 1). Both finalists executed their cycle-2 directions faithfully; A
wins on the soundness and runnability of its *core* recall signal, not on component count.

---

## Did both address cycle-2?

**A** — all four cycle-3 directions closed, and the most important one (the anchor extractor) closed
thoroughly:
- The `has_specific_anchor`/`extract_anchors` rewrite drops bare years and bare integers, requires
  numeric anchors to carry a decimal/percent/`n=`, and filters named entities against a `COMMON_TOKENS`
  stoplist. The exact vague-prose attack the cycle-2 critique flagged ("Alzheimer… 2023… Network")
  no longer clears the gate by construction. This was A's single worst liability and it is genuinely fixed.
- `title_similarity` placeholder replaced with a real `token_set_ratio` at a reachable `0.60`, with
  exact DOI/S2-ID/arXiv resolution preferred first. `external_grounding` is now a live, discriminating
  sub-term instead of a near-zero floor.
- Deterministic S2-only `relation_type` classifier (Step 3.5a) keyed off retrieval provenance, plus a
  `relation_classification_ran` gate that returns `0.0` (not a free `1.0`) when candidates exist but
  were never classified. Closes the degraded-mode collapse.
- `near_direct` use-requirement via `field_role_signal`: bare-bibliography matches drop 0.85→0.35.
- Added a full end-to-end `run_m14` runbook.

**B** — all five directions closed, plus a genuinely sharp sixth (relation-classification degradation):
- Conceptual tier lifted from a damped `0.05` to a full `0.18` sub-weight — the guard is now
  load-bearing rather than cosmetic, which was the *point* of the direction.
- Shared `extract_artifacts` fully specified and explicitly excludes 2-letter disease/domain
  abbreviations ("AD") — a concrete, correct improvement.
- `trace_external_grounding` tightened: 0.32 floor + shared-artifact match + best-vs-runner-up margin.
- `api_available` collapsed from triple-counted to a single `availability` term.
- `has_ref_match` now resolves into the external `L∪K` set, not the ARA's own bibliography.
- Fix #6: `classification_failed` tracking + a 30%-failure threshold that forces `api_available=False`.
  This is a genuinely thoughtful anti-laundering guard and, in isolation, a hair more robust than A's
  binary `relation_classification_ran`.

Both are honest, both are net-new vs the ARA verifier, both preserve their dominant-external-term edge.
This was a close final.

## What A genuinely measures

External-literature *recall with role alignment*. It builds an independent expectation set
(`island ∪ knn500` from Semantic Scholar references/citations/recommendations + optional Undermind),
attaches a deterministic `importance` and `relation_type` to every candidate, then scores whether the
ARA's `problem.md`/`related_work.md` cover that set — weighted so canonical/contradictory/competing
misses hurt most, and so uncited "conceptual" coverage is capped at 40% and gated on a distinctive
shared anchor. It is not a measure of "good science" in the abstract; it is a tightly-scoped measure of
**literature humility** — did the compiler know what a competent search would immediately surface. That
is exactly the hole the brief names, and A stays honestly inside that scope.

## Why A over B — the deciding axis

Both center external recall. The decider is *how independent of LLM judgment the gold set and its
weights actually are* — the metric's entire claim rests on the expectation set being generated
independently of the ARA.

- **A's expectation set and its importance/relation weights are LLM-free.** `island`/`knn500` come from
  S2 retrieval + embedding similarity; `importance` is `0.5·rank + 0.3·citation_percentile +
  0.2·relation_boost`, all deterministic; `relation_type` is assigned from *retrieval provenance*
  (which query/endpoint surfaced the paper) plus regex signal. An LLM enters A only for the
  *conceptual-coverage* judgment, which is capped at 40% and deterministically re-checked against
  `has_specific_anchor`. So the core recall signal is auditable and reproducible run-to-run.
- **B's gold set is partly LLM-constructed.** Membership in `L` (the top-25 recall denominator) and each
  candidate's `importance` depend on a per-candidate LLM `relevance`/`relation` classification. B's own
  fix #6 concedes this: when that classification degrades on >30% of the pool, B forces
  `api_available=False` and the whole score collapses to a degraded run. That is the correct safety
  behavior, but it exposes that B's central "independent landscape" is only as stable as an LLM
  batch-classification pass. A's equivalent machinery keeps running deterministically under the same
  conditions.

That is a real soundness edge on the one property M14 must protect. A also ships a complete `run_m14`
orchestration, making it directly implementable; B's scoring function is complete but its retrieval/
classification glue is described in prose across sections.

Neither B advantage overturns this: B's single-dominant-external-term structure is philosophically
cleaner, but A's external terms (`coverage 0.28 + miss_penalty 0.12 + contradiction 0.14 = 0.54`) still
form a majority and are not diluted into irrelevance the way round-1's exp3/exp4 were. B's fix #6 is
slightly more robust than A's classification gate, but it guards a weakness (LLM-sourced relations) that
A largely does not have.

## Runnability of A's workflow

Sound and runnable. Every scoring path is deterministic Python against the documented `04_problem.md`
shape; the S2 endpoints, query provenance tags, Undermind prompt, and LLM conceptual-coverage prompt are
all specified with explicit output→sub-score conversion. The `run_m14` runbook sequences parse → query →
retrieve → classify relations → importance → coverage → score with typed I/O. The remaining
implementer-supplied wrappers (`semantic_scholar_retrieve`, `dedupe_by_paper_id`, etc.) are thin I/O, and
every decision they feed is fully pinned. No step is left to discretion.

## Where A is still gameable or limited (the honest qualification)

- **`high_importance_miss_penalty` still returns `1.0` on several "nothing to penalize" branches**
  (empty pool, `total_importance == 0`, genuinely-no-high-stakes-after-classification). Each is
  defensible individually, but a thin/awkward landscape can still collect a full 0.12·1.0 on this
  component without demonstrating anything. The cycle-3 `relation_classification_ran` gate only catches
  *total* non-classification, not a landscape that lands weakly in the high-stakes buckets.
- **`importance` is a heuristic, not a ground truth.** Inverse-rank + citation percentile + a
  hand-set `relation_boost` table decide which misses are "landmark." Citation-count percentile
  structurally under-weights genuinely important *recent* work — a known bias A inherits, not solves.
- **Provenance-based `relation_type` is coarse.** A "contradiction_query"-surfaced paper is labeled
  `contradictory` largely because of the query that found it; the deterministic regex terms are a
  blunt secondary signal. This is more robust than depending on Undermind, but it can mislabel, and the
  contradiction subscore rides on it.
- **The conceptual-coverage LLM judgment remains the one non-deterministic core input**, bounded by the
  40% cap and the anchor re-check but not eliminated.
- **It measures recall of a machine-generated candidate set, which is a proxy for "reference-landscape
  completeness," not the thing itself.** A high score means "the ARA covers what S2/Undermind surface,"
  which can still miss a paper no search surfaces, and can over-credit coverage of a bloated retrieval.

## Does it clear the bar?

Yes — as an **honest, tightly-scoped external-recall metric that genuinely beats the ARA verifier on
external-literature recall**, which is precisely why M14 ranked top-10. It does not, and does not claim
to, measure "good science" in general; it measures whether the problem framing is grounded in the real
prior-work neighborhood, with the independent expectation set and the asymmetric miss penalty giving it
real Goodhart resistance that a citation-count metric would lack. It sits in the "genuinely measures its
scoped target, honestly limited beyond it" tier — which for a net-new external-recall metric is exactly
where it should be. A is the winner.
