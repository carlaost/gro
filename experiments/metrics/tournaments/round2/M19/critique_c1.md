# M19 — Judge critique, cycle 1

Metric: Claim↔Experiment↔Evidence type-aware entailment + clinical-trial-registry publication-bias
cross-check. Judged on: genuine type-aware entailment (not lexical/topic overlap); a concrete,
runnable workflow that turns the registry publication-bias check into a *deterministic* signal;
Goodhart-resistance; penalize-don't-skip; and preserving the net-new edge over verifier D1 (the
registry leg must beat both round-1 and the verifier, which only does internal semantic support).

---

## Per-expander verdicts

### exp2 — VERDICT: WINNER (rank 1)

The tightest fit to the brief. Type-awareness is realized as a **deterministic warrant matrix**:
`design_tier × claim_type → warranted | overreach_penalty`. Classification is split from scoring —
design tier via keyword heuristic (with a narrow `[sem]` fallback only when it can't resolve) and
claim type via a closed-label `[sem]` call — so the pass/fail lands on a fixed, auditable table
rather than on a persuadable judge. This is the single most Goodhart-resistant realization of
"type-aware" in the field: once the two labels are set, no eloquent hedging can move the score, and
the explicit `OVERREACH_PENALTY` entries (`observational→causal`, `cross_sectional→causal`,
`in_silico→causal`, `case_study→comparative`) directly encode the overclaiming failure mode the
metric exists to catch.

It also follows the brief's own steer most faithfully: it reads the ledger note ("verifier does D1;
pub-bias beats both") and *acts on it* — pub-bias gets the largest single weight (0.30), justified
as the net-new capability, and the entailment half is deliberately made type/design-warrant-aware
so it doesn't duplicate D1's flat "is there support." Anti-padding is real: `min()` over the Proof
list (weakest-link) plus averaging per-claim over *all* claims means adding easy claims or padding
Verifies edges only creates more places to be caught. The fabricated-NCT guard (condition-mismatch
scored *worse* than absence) and the digit-leak probe are concrete deterministic signals. Grounding
is a deterministic verbatim/value substring match into `evidence/` body text. Penalize-don't-skip is
handled per-branch with an explicit table (non-clinical = fixed −0.2 at full weight, caps the
ceiling rather than dropping the term; clinical-with-no-id = −0.8; unresolvable id = −0.8;
condition-mismatch = −1.0).

Weaknesses: the design-tier keyword heuristic is brittle (`"assay"→wetlab`, `"pipeline"→wetlab`
could misfire on ML-with-pipeline setups) — mitigated but not eliminated by the `[sem]` fallback.
The warrant matrix's `WARRANT_MATRIX`/`OVERREACH_PENALTY` coverage is sparse (many `(tier, type)`
pairs fall to `DEFAULT_OVERREACH_PENALTY = −0.4` with no rationale). Grounding trusts substring
presence, which is weaker than exp1/exp3's re-derivation from the actual evidence values.

### exp3 — VERDICT: WINNER (rank 2)

The strongest *anti-citation-laundering* design, which is precisely where this metric must beat
verifier D1. Its `[sem]` entailment call is instructed to **re-derive the direction/magnitude/
significance relationship from the raw transcribed evidence values, ignoring narrative gloss** —
this attacks the exact gap the brief names (D1 checks "does a source exist and quote-match"; this
checks "does the source, correctly read, actually license the number's *use* in the argument").
Type-awareness is realized as **genre-appropriate evidentiary rubrics** (CI discipline for
statistical synthesis, FDR-threshold discipline for omics, proof-closure for theory,
primary-vs-secondary endpoint framing for clinical) — the richest, most field-honest notion of
"type-aware" of the four, and genre is inferred from `Setup` subkeys actually present, not
self-declared.

Two mechanisms other proposals lack: (1) `citation_set_mismatch` cross-checks `claims.md.Sources`
against `evidence/README.md`'s claim→object map — gaming one artifact without the other is caught;
(2) an `availability_floor` computed in Step 0 that **multiplicatively caps the entire score** — the
cleanest realization of penalize-don't-skip in the set, because a thin/dangling artifact cannot be
rescued by good-looking downstream sub-scores. It also names the actual MCP tools it would call
(`get_trial_details`, `analyze_endpoints`), making the registry leg concretely runnable in this
environment, and it explicitly frames composition as multiplicative gating (a comprehensive set of
unentailed claims scores *worse* than a sparse entailed one) rather than a weighted sum that lets
comprehensiveness offset unsoundness.

Weaknesses: the type-awareness lives inside one `[sem]` call ("apply the genre-appropriate
standard") rather than in a deterministic structure, so it leans harder on the LLM applying five
different rubrics consistently — less auditable/spot-checkable than exp2's warrant matrix. Genre
inference is a simple keyword heuristic with no fallback. The registry sub-scores
(`not_applicable_genre = 0.6`) are a touch generous for an axis that can't be audited at all.

### exp1 — VERDICT: strong, rank 3 (loser)

Deepest reasoning and the best single anti-Goodhart lever — `evidence_fetch` is a *required non-LLM
argument*, so Prompt C's `independently_corroborated`/`circular` flags are checked against fetched
bytes rather than the LLM's memory of them. The ordinal `TYPE_RANK` ladder (existence <
correlational < comparative/predictive < causal) with a hard type-sufficiency gate is a clean,
deterministic type-aware core, and the five documented gaming routes are the most thoroughly
reasoned in the set. Loses to exp2/exp3 on two counts: (1) a self-inconsistency — it argues "a
single badly-overclaimed claim should not be diluted away by many well-behaved ones," then aggregates
with an unweighted **mean** across claims, which does exactly that dilution (exp2/exp4 use `min`,
exp3 uses a multiplicative floor cap); (2) it weights entailment 0.7 / pub-bias 0.3, slightly
softer on the net-new edge the brief prizes than exp2's explicit "pub-bias is the largest single
weight." Excellent proposal; edged out, not wrong.

### exp4 — VERDICT: rank 4 (loser)

Sharpest per-type entailment *rubrics* of all four — "a ranking claim of N items is not entailed by
evidence showing only the top item," "correlational cannot entail causal → cap at PARTIAL,"
"empirical cannot entail a proof-type claim" — and type is derived from design not wording, with an
explicit `design_vs_phrasing_mismatch` detector. But it dilutes the brief's core: the
publication-bias axis extends to a `[sem]` **literature-contradiction search** (semantic-scholar/
undermind) for non-clinical genres, which is scope creep away from the "clinical-trial-registry
check turned into a *deterministic* signal" the brief specifically asks for, and is the least
deterministic leg of any proposal. The structural gate is weighted only 0.15 and grounding-weight
discounts voting power without ever zeroing thin claims. Strong ideas, weakest brief fit.

---

## WINNERS: exp2, exp3

### Winner critiques + cycle-2 directions

**exp2** — Keep the warrant matrix as the deterministic type-aware core; it's the most auditable and
hardest-to-game mechanism in the tournament. Cycle-2 fixes:
- Harden design-tier classification: the keyword heuristic will misclassify hybrid setups
  (ML-with-`pipeline`, omics-with-`cohort`). Make the `[sem]` fallback the default for any setup
  that trips *two or more* tier keyword sets, and log tier-classification confidence into the score.
- Fill in the warrant matrix: the sparse `OVERREACH_PENALTY` table dumps most `(tier, type)` pairs
  into a flat `−0.4` default with no rationale. Enumerate the full grid (or at least justify the
  default per row) so the penalty gradient is principled and auditable.
- Upgrade grounding from substring-presence to exp3-style **re-derivation against the evidence
  values** — substring match alone is beatable by a locator-correct but semantically-wrong cite,
  which is the precise laundering route that beats verifier D1.
- Justify the `min()`-over-Proof vs mean-over-claims aggregation interaction explicitly (show a
  worked example that a padding attack can't dilute a real overreach penalty).

**exp3** — Keep the re-derive-from-raw-evidence instruction, the `citation_set_mismatch` cross-check,
and the multiplicative `availability_floor` — all three are load-bearing and net-new vs D1. Cycle-2
fixes:
- Make type-awareness more deterministic/auditable: lift the genre-rubric out of the single `[sem]`
  call into an explicit structure (borrow exp2's warrant matrix or exp4's per-type rubric table) so
  the pass/fail isn't concentrated in one LLM judgment applying five rubrics from memory.
- Add a genre-inference fallback (currently keyword-only, no `[sem]` backstop) and score
  genre-classification confidence.
- Tighten `not_applicable_genre = 0.6`: an axis that categorically can't be audited should cap the
  achievable ceiling lower (align with exp2's stricter non-clinical floor), so a non-clinical ARA
  can't approach ceiling on a leg it's exempt from.
- Spell out the fabricated/mismatched-NCT guard as sharply as exp2 does (condition-overlap check
  scored worse than honest absence) — exp3 checks status/results/primary-vs-secondary but is thinner
  on the "id resolves to an unrelated trial" fabrication case.

Cross-pollination for cycle-2: exp2's **deterministic warrant matrix** + exp3's
**re-derive-from-raw-evidence grounding, citation cross-check, and multiplicative availability
floor** are complementary and together dominate either alone — the merged design should pair a fixed
type-warrant table with evidence-value re-derivation and a hard availability cap.

### Loser one-liners
- **exp1**: deepest reasoning and the best anti-Goodhart lever (required non-LLM `evidence_fetch`),
  but self-inconsistent mean-over-claims aggregation undercuts its own "don't dilute overreach" goal
  and it under-weights the net-new pub-bias edge.
- **exp4**: sharpest per-type entailment rubrics, but its non-clinical literature-search pub-bias
  path is scope creep away from the brief's demand for a *deterministic clinical-registry signal*.
