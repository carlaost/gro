# M19 — Judge critique, cycle 2

Metric: Claim↔Experiment↔Evidence type-aware entailment + clinical-trial-registry publication-bias
cross-check. Cycle-2 round: both A and B advance to cycle 3 (no final winner this cycle). A descends
from the cycle-1 winner exp2 (deterministic warrant matrix, now cross-pollinated with exp3's
re-derivation grounding + availability floor); B descends from exp3 (re-derive-from-raw-evidence +
availability floor, now cross-pollinated with a deterministic per-genre checklist in the spirit of
exp2's matrix). Judged on the same axes as cycle 1: genuine type-aware entailment (not lexical
overlap), a runnable *deterministic* registry cross-check, Goodhart-resistance, penalize-don't-skip,
and preserving the net-new edge over verifier D1.

Verdict: both are materially improved over cycle 1 and both closed the specific weaknesses they were
tasked with. Neither is yet the strongest possible design because each still carries a real,
correctable defect the other has already solved. The cycle-3 job is convergence, not divergence — the
two designs are now close enough that the ideal metric is a specific merge, detailed at the end.

---

## Track A (warrant-grid lineage)

### What cycle 2 got right
- **The warrant grid is now formula-derived and I verified it is internally consistent.** The four
  cycle-1 hand-specified cells reproduce exactly (`observational_cohort×causal=−0.6`,
  `cross_sectional×causal=−0.8`, `in_silico×causal=−0.8`, `case_study×comparative=−0.7`), and the
  remaining cells follow deterministically from `KIND_ELIGIBILITY` + `OVERREACH_CEILING` +
  `ASSERTION_STRENGTH`. This is the single most auditable type-aware core in the tournament and it
  directly answers the cycle-1 "sparse matrix, flat −0.4 default" complaint. Keep it.
- **Grounding is now two-layered** (deterministic substring gate → Call E re-derivation), and the
  `MISREAD`-floors-the-claim rule is the correct realization of "beats a locator-correct,
  semantically-wrong citation" — exactly the D1-beating route the brief prizes. Keep it.
- **`blended_aggregate = 0.5·mean + 0.5·min` with a proven bound (§6.1) is the correct fix** to the
  inter-claim padding hole the tournament flagged (for exp1, and honestly for exp2). The worked
  example is correct.
- Publication-bias two-axis overlap (condition **and** intervention, with an explicit `−0.5`
  one-axis-overlap bucket) is a genuine sharpening of the fabricated-NCT guard, and the
  outcome-switching stack (`−0.3` on top of the proportional drop) is a real new signal.

### Weaknesses to fix in cycle 3
1. **The `gap ≤ 0` branch penalizes legitimate under-claiming as if it were a defect.** Any
   kind-ineligible pair whose claim strength is *below* the design's ceiling returns a flat `−0.2`.
   That bucket includes `rct×descriptive_prevalence`, `rct×associative_correlational`,
   `meta_analysis×descriptive_prevalence`. But an RCT reporting the descriptive prevalence of its own
   sample, or an associational sub-finding, is **not overclaiming at all** — it is a weaker claim than
   the design could support, which is the safe direction. Penalizing it `−0.2` is a false positive that
   will dock honest, conservative artifacts. The grid conflates "wrong *kind* of evidence" (a real
   defect: cohort claiming mechanism with no assay) with "correct design making a claim humbler than it
   could" (not a defect). Cycle 3 should split these: under-claiming relative to the ceiling should be
   ≈0 (neutral), not −0.2; only *kind-orthogonal* claims (design produces no evidence bearing on this
   claim type at all) deserve the mild penalty.
2. **The confidence-tax multipliers (1.1 / 1.15) are hand-picked and unjustified** — ironic in a cycle
   whose headline was replacing hand-picked constants with derived ones. Same for the case-study
   `−0.1` generalizability surcharge. These are defensible in direction but need a stated rationale or
   a derivation, or the cycle-1 "no rationale" critique simply reappears one level down.
3. **The publication-bias outcome diff is naive set arithmetic and will false-positive in practice.**
   `dropped = set(trial.primary_outcomes) - set(artifact.reported_outcomes)` compares registry outcome
   *strings* ("Change from baseline in HbA1c at 24 weeks") against outcome labels extracted from
   `claims.md`. These will essentially never string-match, so `dropped` is almost always non-empty and
   the proportional penalty fires spuriously. This is the metric's headline net-new axis resting on
   string equality that does not hold. It must become a semantic match — either `analyze_endpoints`
   (which B correctly names) or a dedicated closed-label `[sem]` "is registry outcome X reported in
   these claims, and framed as primary or secondary?" call. Relatedly, `artifact.reported_outcomes` and
   `artifact.reported_outcomes_framed_as_primary` are consumed but never specified — where do they come
   from, and "framed_as_primary" is itself a semantic judgment needing a call.
4. **The external return shape is invented.** `TrialRecord.results_summary: str` (free-text posted
   results feeding Call F) is not what ClinicalTrials.gov API v2 returns — results come as structured
   outcome-measure + statistical-analysis modules, not a prose summary. Call F as written needs an
   adapter step that synthesizes that string; that synthesis is unspecified and is itself a place bias
   can be laundered. B is more honest here (names `get_trial_details` + `analyze_endpoints` and diffs
   structured fields).
5. **Minor: the "padding cannot dilute" claim is per-axis, not per-metric.** The §6.1 bound caps the
   *entailment axis* at `0.5+0.5·min`; one overreach claim caps that axis at ~0.10, but it is only 0.25
   of the weighted sum, so a clean pub-bias (0.30) + clean grounding can still lift the composite well
   above what the prose implies. This is arguably correct design (one bad claim shouldn't zero a whole
   artifact) but the framing oversells it — state the composite-level consequence honestly. Conversely,
   `min`-across-*all*-claims means one genuinely borderline/`unclassifiable` claim (→ −0.5) pins the
   axis for an otherwise-honest large artifact; watch that this doesn't over-penalize legitimate
   heterogeneity.
6. **Minor: digit-leak regex robustness.** `NUMBER_LEAK` will fire on legitimate design descriptors
   that can appear in `Metrics`/`Expected outcome` (sample counts "n=31", platform names "10x") and its
   post-number lookahead `(?!\s*(?:FDR|CI|alpha))` assumes threshold keywords *follow* the number,
   whereas the corpus writes them before ("FDR<0.05", handled separately by `ALLOWED_THRESHOLD`). Low
   stakes (it is a −0.3 nudge, not a gate) but tighten it or it will nick honest artifacts.

---

## Track B (checklist / availability-floor lineage)

### What cycle 2 got right
- **The graded checklist (`0.4 + 0.6·checklist_score`) is the right replacement for cycle-1's binary
  0.4-vs-1.0 cliff**, and lifting the per-genre rubric into an enumerable `GENRE_CHECKLIST` with
  per-item rationales is a genuine auditability win — a reviewer can now spot-check one boolean against
  its cited value. Crucially, only the *resolved genre's* three items are asked, so the model applies
  one rubric, not five from memory — that is the substantive part of the cycle-1 "don't concentrate
  five rubrics in one call" fix, and it's real.
- **`resolve_genre` with a scored keyword vote + `[sem]` fallback on low-margin/tie + confidence cap on
  keyword-vs-constraints disagreement** is exactly the fallback the critique asked for, and carrying
  `genre_confidence` into two downstream penalties (entailment multiplier and the non-clinical ceiling)
  is a clean way to make ambiguity cost something.
- **The fabrication-guard ordering is correct and well-priced**: `no_overlap` (0.0) < unresolvable
  (0.05) < honest absence (0.10). This closes exp3's cycle-1 gap on "id resolves to an unrelated trial"
  and does it with a dedicated `condition_overlap_fn` closed-label call kept separate from the
  endpoint-framing call (good for independent audit).
- **Naming the real MCP tools** (`get_trial_details`, `analyze_endpoints`) and diffing structured
  registry fields keeps the registry leg concretely runnable — A should copy this.
- The §1.3 #6 analysis of the genre-mislabeling escape hatch (obscure a clinical `Setup` to dodge into
  the cushier non-clinical bucket) is a sharp, self-found Goodhart route and the confidence-scaled
  ceiling is a reasonable price on it.

### Weaknesses to fix in cycle 3
1. **This is the big one: B still aggregates across pairs with a plain unweighted mean.**
   `artifact_score = sum(p["score"]) / len(pairs)`. That is precisely the padding-dilution failure mode
   the tournament docked exp1 for and that A explicitly proved bounded — one contradicted claim (score
   ≈0) among 20 clean pairs yields ~0.95. B inherited exp3's multiplicative `availability_floor` (which
   defends against *thinness/dangling refs*, an artifact-global property) but has **no defense against
   inter-pair padding** (a per-claim property). The floor does not help here. B must adopt A's
   `blended_aggregate` (or a min/multiplicative gate) across pairs. As written, B's Goodhart story has a
   hole A has already closed.
2. **B dropped the deterministic verbatim-presence grounding gate that A kept.** B folds grounding into
   the entailment `[sem]` call and `evidence_availability` only checks that a locator *resolves to an
   object with a non-empty body* — not that the cited quote/value actually appears in that body. B
   explicitly assumes Seal-L1 verified verbatim quotes (§1.4), but that means a locator-correct,
   quote-*fabricated* citation is defended against only by the LLM noticing during re-derivation, with
   no cheap deterministic backstop. A's substring gate is a strictly cheaper and more robust first line;
   B should adopt it (also saves `[sem]` cost by short-circuiting outright fabrication).
3. **The registry lookup runs per (claim, experiment) pair, not once per artifact.** In
   `compute_M19_artifact` every pair calls `compute_M19` → `publication_bias_subscore` →
   `registry_lookup_fn`. For a clinical artifact whose 10 claims cite one trial, that is 10 identical
   external calls, and worse, `resolve_genre` runs per-experiment so different experiments could land in
   different genre branches → inconsistent bias treatment within one artifact. Dedupe: resolve
   trial-linkage and run the external leg once per distinct NCT id per artifact, then attach the result
   to the relevant pairs. This also matters because B is billed as "the most expensive metric" — don't
   multiply the expensive leg by pair count needlessly.
4. **Keyword-vote genre inference is contaminated by generic subkeys.** `GENRE_KEYWORDS` matches on
   `Setup` subkey *names*, but "Design" (in the `statistical_synthesis` set) is a subkey that clinical
   and ML setups also carry, and "reference standard"/"pipeline" can co-occur in hybrid omics/ML work.
   The confidence formula will therefore misfire on exactly the hybrid setups cycle-1 warned about
   (ML-with-pipeline, omics-with-cohort). The `[sem]` fallback catches the *low-margin* case, but a
   confidently-wrong keyword vote (one spurious generic-subkey match dominating) never triggers the
   fallback. Consider voting on subkey *values* / content, not just key names, or lowering the
   confidence-fallback threshold.
5. **Residual (small) perverse incentive in the non-clinical ceiling.** Tightening to
   `0.35·(0.5+0.5·conf)` ∈ [0.175, 0.35] reduces but does not eliminate the gap over honest
   unregistered-clinical (0.10): a confidently-non-clinical artifact still out-scores an honest
   unregistered trial ~3.5× on this axis. The defense (you can only get high confidence by genuinely
   looking non-clinical) is reasonable, but state explicitly why 0.35 is the right ceiling rather than,
   say, ≤ the honest-clinical-reconciled floor. This is a judgment call, not a bug — but justify the
   number.
6. **Minor: `condition_overlap_fn` population extraction is fragile.**
   `experiment_setup.get("Population") or experiment_setup.get("Cohort")` returns `None` for clinical
   setups that describe population inside `Intervention`/`Endpoint` prose or under a different subkey,
   silently weakening the overlap check. Specify a fallback (e.g. fall back to the claim statement text)
   rather than passing `None` into the `[sem]` call.

---

## Cycle-3 directions

Both tracks are now good; the strongest cycle-3 artifact is a **specific merge**, because A and B have
each solved the other's principal remaining defect. Do not re-litigate the parts both already got right
(re-derivation grounding, availability/structural floor, fabrication-guard ordering, named MCP tools,
graded scoring). Focus:

### On type-aware entailment (the core the whole metric turns on)
- **Reconcile the two type taxonomies — they are complementary, not competing, and cycle 3 must state
  the relationship explicitly.** A classifies `(design_tier × claim_type)` and asks *"is this design
  entitled to make a claim of this strength/kind?"* (a **warrant** question). B classifies `genre` and
  runs a per-genre rigor checklist asking *"given the field, were its evidentiary rules followed?"* (an
  **execution** question). These are orthogonal and the best metric does **both**: use A's warrant grid
  as the gate (deterministic, auditable, catches overclaiming) **and** B's genre checklist as the
  item-level rigor check (catches CI-crossing-null, unthresholded DEG counts, unclosed proofs). A claim
  should have to pass the warrant grid *and* the genre checklist; neither alone is sufficient. This is
  the single highest-value cycle-3 move.
- **Unify the classification machinery.** A now has scored confidence + `[sem]` fallback on *design
  tier*; B has the same on *genre*; both should share one confidence-aware classifier pattern
  (keyword/heuristic → `[sem]` fallback on zero/tie/low-margin → confidence tax downstream), applied to
  whatever label(s) the merged taxonomy needs. Fix B's generic-subkey contamination (vote on values,
  not just key names) while doing this.
- **Fix A's `gap ≤ 0` false positive**: under-claiming relative to a design's ceiling is the safe
  direction and should score ≈neutral, not −0.2. Reserve penalties for kind-orthogonal or overreaching
  pairs.
- **Adopt A's `blended_aggregate` (proven bound) at both intra- and inter-claim levels, everywhere** —
  this is non-negotiable for B, whose plain-mean-over-pairs is the metric's current worst Goodhart
  hole. Keep A's `min`-over-Proof intra-claim.

### On the publication-bias cross-check (the net-new edge over D1 — protect it)
- **Replace A's string-set outcome diff with semantic endpoint matching.** This is the most important
  registry-leg fix: outcome-dropping and outcome-switching detection must run through `analyze_endpoints`
  (structured registry outcome measures) plus a closed-label `[sem]` "is registry outcome X reported in
  these claims, and is it framed as primary or secondary?" call — not `set(...) - set(...)` over label
  strings that will never match. B's endpoint-framing routing is the model to copy.
- **Specify the real external return shape.** Drop A's invented free-text `results_summary`; consume the
  actual ClinicalTrials.gov v2 structured results/outcome/status modules. Where a prose direction check
  is needed (A's Call F), derive it from the structured posted-results fields, and say how.
- **Keep A's two-axis overlap (condition AND intervention) with the explicit one-axis intermediate
  bucket** over B's single `condition_overlap_fn` — the two-axis version catches the "right disease,
  wrong drug" laundering case that a single overlap label blurs. Merge B's clean fabrication-ordering
  (`no_overlap < unresolvable < honest-absence`) onto A's two-axis structure.
- **Run the external leg once per distinct trial id per artifact, not per pair** (B's current
  inefficiency and a source of within-artifact genre inconsistency), and attach the single result to
  every claim that cites that trial.
- **Both: preserve penalize-don't-skip on the non-clinical branch, but converge on one justified
  ceiling.** A uses a fixed `−0.2` at full weight; B uses `0.35·(0.5+0.5·conf)`. Pick one, and justify
  the number against the honest-unregistered-clinical floor so a non-clinical (or genre-obscured)
  artifact can never approach ceiling on a leg it cannot be audited against, and cannot out-score an
  honestly-disclosed unregistered trial by an unprincipled margin.

### Cross-cutting
- Merge A's deterministic verbatim/value grounding gate into B (cheap fabrication backstop before the
  expensive `[sem]` re-derivation).
- State the composite-level (not just per-axis) consequence of the anti-padding bound honestly.
- Give every remaining hand-picked constant (A's confidence-tax multipliers and case-study surcharge; B's
  checklist ladder coefficients and non-clinical ceiling) either a one-line rationale or a derivation —
  the cycle-2 theme was "no unjustified constants," and it should hold at every level.
