# M18 Cycle-1 Critique: Claim Drift / Reference Truthfulness

Metric: do cited sources actually say what they're cited for, checked against the REAL external
source ([ext]+[sem]) — net-new vs the verifier's L1 §10, which only confirms the quote appears at a
cited line inside the ARA. Judged on: reasoning correctness; a concrete/sound/runnable
generation-compute workflow that turns source-fetch + entailment into deterministic sub-scores;
Goodhart-resistance; penalize-don't-skip; and preservation of the edge over L1 §10.

All four share the same skeleton (parse problem.md [+ related_work.md] → build claim units →
resolve real sources via [sem]/DOI/PMID/arXiv → retrieve full-text/abstract → LLM support label →
deterministic mapping → aggregate with availability/thinness penalties). They separate on depth,
determinism quality, and Goodhart-resistance.

---

## Per-expander verdicts

### exp2 — RANK 1

Correctness: strong. Best reward/not-reward framing plus the most complete drift taxonomy
(`wrong_population`, `wrong_outcome`, `wrong_method`, `wrong_direction`, `wrong_magnitude`,
`causal_overreach`, `review_as_primary`, `speculation_as_fact`, `role_mismatch`, `too_vague`,
`source_identity_uncertain`).

Workflow: the deepest and most operational.
- Retrieval-status taxonomy is the richest: `full_text / abstract_only / metadata_only / unresolved
  / contradictory_identity`, each with a distinct deterministic penalty (0 / -0.15 / -0.35 / -0.55 /
  -0.70). `contradictory_identity` is a real insight — it catches the case where a wrong paper is
  resolved and "supports" the claim, a truthfulness failure the others miss.
- Step 6 cross-layer role-drift audit is the single strongest edge-preserver in the field: it checks
  that each `RW##` typed role (imports/baseline/bounds/extends/refutes) matches what the real source
  actually is, reusing the support prompt with the role + Delta fields as the claim. This goes well
  beyond L1 §10 and beyond "does the source support the sentence" into "does the dependency graph
  itself tell the truth."
- Deterministic unit scoring is thorough: specificity penalty when high-specificity claims lack
  `direct` support, missing-citation floor (0.05), contradiction cap (0.10), and a multi-source
  anti-laundering rule (max support minus 0.05 per extra unresolved/unsupported source, cap -0.20).
- Robustness: JSON schema validation with one retry then fallback to `unverifiable`/0 — the only
  proposal that handles malformed LLM output explicitly.
- Final function is additive and transparent: `0.55*obs_gap + 0.20*insight_assumption + 0.15*role +
  0.10*rw_coverage`, with `parse_ok=False → 0.05`.

Goodhart: strong. Role-drift + contradictory-identity + multi-source hygiene close the obvious
gaming routes (citation stuffing, laundering through related_work, resolving a look-alike paper).

Penalize-don't-skip: exemplary. Unresolved/metadata-only heavily penalized, nothing dropped from the
denominator, missing RW gets coverage penalty not N/A.

Weaknesses: many moving penalty constants with no calibration note; the additive `rw_role`/`rw_coverage`
terms fire even when the problem layer needs no external RW support, slightly diluting the
problem-primary focus.

### exp4 — RANK 2

Correctness: the best conceptual writeup of the four. The major/moderate/minor drift stratification
is precise, and it is the only proposal to make the L1 §10 edge explicit and central: it separates
"quoted text exists" from "the cited source supports this assertion" in prose AND in the scoring
prompt. Directly targets the exact gap the brief asks us to protect.

Workflow: concrete, deterministic, and efficient.
- Graded resolution score (1.0/0.75/0.45/0.20/0.0) AND graded retrieval quality
  (1.0/0.75/0.45/0.20/0.0) — treats availability as a continuous part of truthfulness rather than a
  bolt-on, which is more faithful to "availability is part of the score."
- Multi-dimensional support judgment (`scope_match`, `polarity_match`, `specificity_match`,
  `number_match`, `evidence_role`) multiplied into the label base — a finer entailment decomposition
  than exp1's booleans, and `evidence_role` (primary_result / review_background / method_source /
  editorial_or_speculative) captures review-as-primary drift cleanly.
- Contradiction scored NEGATIVE (-0.35), not floored at 0 — the most aggressive penalize-don't-skip
  stance on outright false citations.
- Efficiency: deterministic sentence-split first, LLM atomization only for multi-assertion
  sentences — sound and runnable.
- Bundle scoring `0.70*best + 0.30*mean_truth - 0.15*unsupported_fraction` is solid anti-laundering.
- Availability/thinness multipliers are stated as workflow-computed semantic flags
  (`all_observation_evidence_is_abstract`, `parseable_external_citation_count==0`, unresolved
  fraction > 0.5), avoiding the brittle regex trap exp3 falls into.

Goodhart: strong; the quote-vs-support separation plus graded locatability defeats vague-claim and
quote-laundering routes.

Penalize-don't-skip: strong and continuous.

Weaknesses: deliberately de-scopes related_work.md to source-resolution context only — it does NOT
audit RW role truthfulness (exp2 does). Defensible given the primary artifact is §4 problem, and it
compensates with a deeper problem-layer analysis, but it does less net-new cross-layer work than
exp2. That single gap is why it ranks 2, not 1.

### exp1 — RANK 3

Correctness: solid, clean reward/not-reward and gaming-route sections. No errors.

Workflow: good on reproducibility — a deterministic minimum audit set with explicit caps (8 obs / 6
gaps / all key-insight links / 8 RW) and a deterministic tie-break sort (`has_number,
has_comparator, has_causal_verb, claim_length, artifact_order`); the only proposal to bound cost
deterministically. Source resolution names concrete domain tools (ClinicalTrials.gov, PubMed/Europe
PMC, arXiv). Support grading uses labels + boolean drift flags with fixed penalties.

Why it ranks below exp2/exp4: (a) support is graded with boolean flags rather than a graded
entailment decomposition, so it is coarser; (b) it has no cross-layer role-drift audit; (c) the
final formula is the weakest — `clamp(0.80*truth_core + 0.20*truth_core*availability)` reduces to
`truth_core*(0.80 + 0.20*availability)`, so availability can only swing the score between 0.80x and
1.0x of truth_core and can never pull a thin-but-confidently-graded artifact down hard. That
under-delivers on the "availability is part of the score / thin scores down" mandate the brief
stresses.

### exp3 — RANK 4

Correctness: fine; adds a useful "effect of critique notes" section restating the net-new edge.

Workflow: the most literally runnable code (real regex parsing, `availability_score`,
`thinness_penalty`, multiplicative `judgment_score`). Two-prompt atomize+judge design is clean. Good
anti-laundering `claim_unit_score` (0.65*best + 0.35*mean).

Why it ranks last: the concrete code is also its weakness on Goodhart-resistance. The
availability/thinness heuristics are brittle string checks that are trivially gamed — `if "brief"
not in related_work_md.lower()` is defeated by putting the word "brief" anywhere; abstract-only
detection only matches an exact lowercase `abstract`; the DOI check keys on the literal string "Not
specified in paper". A metric whose whole point is resisting gaming should not hinge on substring
presence. It also folds LLM self-reported `confidence` in as a multiplier (floor 0.25), adding a
self-report gaming surface the others avoid. No cross-layer role audit.

---

## WINNERS: exp2, exp4

---

## Per-winner cycle-2 directions

### exp2
- Calibrate the penalty constants: the retrieval-status penalties, flag penalties, and multi-source
  decrements are asserted, not grounded. Add a short rationale or a tiny worked example
  (2-3 units through to a final number) so the constants are defensible and reproducible.
- Make the RW role-drift terms conditional: only let `rw_role`/`rw_coverage` weigh in when the
  problem layer actually depends on external RW support; otherwise redistribute weight to the
  problem-layer terms so a paper with a thin-but-honest related_work isn't dragged down for work it
  didn't need to do. Keep the audit, gate the weight.
- Adopt exp4's explicit "quoted text exists ≠ source supports assertion" instruction inside the
  support prompt — exp2's taxonomy implies it but doesn't state it, and it is the crux of the L1 §10
  edge.
- Specify the source-selection confidence threshold that separates a clean resolve from
  `contradictory_identity` (e.g. title/author/year agreement rule), so that determination is
  deterministic rather than left to the model.

### exp4
- Add a bounded, deterministic cross-layer role-drift check (borrow exp2 Step 6) as a small
  additional component — this is the one place exp2 is stronger. Keep problem.md primary (dominant
  weight) but score whether related_work.md typed roles match the real source when RW is present;
  penalize-don't-skip when absent. This closes exp4's only real gap and would make it a genuine
  co-leader.
- Bound cost deterministically the way exp1 does (audit-set caps + deterministic tie-break sort) so
  large problem layers don't blow up the external-call budget non-reproducibly.
- Pin down how the multi-dimensional match sub-scores (`scope_match`, `polarity_match`, etc.) are
  elicited reliably — either a rubric/anchors in the prompt or a validation+retry step (borrow
  exp2's JSON-validation robustness) so the multiplicative combination isn't noise-amplifying.
- Sanity-check the negative-contradiction propagation with a worked example: confirm a single
  contradicted source in a multi-source bundle produces the intended sharp drop after the
  `max(0.0, ...)` flooring, and that it isn't silently laundered by a co-cited supporting source.

---

## Per-loser one-liners
- exp1: Solid and the most cost-reproducible (deterministic audit caps + tie-break), but coarser
  boolean-flag grading, no cross-layer role audit, and a final formula where availability can only
  scale truth_core 0.80–1.0x — too weak on the thin-scores-down mandate.
- exp3: Most literally runnable, but its availability/thinness scoring hinges on brittle,
  trivially-gamed substring checks (`"brief"`, exact `abstract`, `"Not specified in paper"`) and an
  LLM self-confidence multiplier — the weakest Goodhart-resistance of the four.
