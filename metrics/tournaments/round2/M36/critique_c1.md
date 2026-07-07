# M36 — Multi-perspective triangulation — Round 2, Cycle 1 critique

Metric: does the work combine epistemically-independent lenses (wet-lab × computational,
simulation × observation, formal × empirical) rather than one, and do the constraints reflect
that combination? [sem]. Net-new vs round-1 and the ARA verifier.

All four expanders converge on the same correct core skeleton — semantic lens extraction gated on
independence, an integration/cross-check requirement, a constraints-reflects-the-combination check,
and a penalize-don't-skip floor for absent/thin method layers. So the field is judged on the
*quality of the anti-gaming design*, the *rigor of the scoring composition*, and the *net-new
mechanisms* each adds beyond that shared baseline. The decisive lens (from the brief) is: can a
paper fake "multi-perspective" by name-dropping methods, and does the scoring resist single-axis
gaming?

---

## Per-expander verdict

### exp4 — RANK 1
**Verdict: strongest.** Adds the two mechanisms most directly aimed at the brief's stated gaming
concern ("fake multi-perspective by name-dropping"):
- **Concreteness gate** (`specific` / `vague` / `mentioned_only`, each requiring a verbatim ≤40-word
  quote naming tools/datasets/parameters); only `specific` lenses count. This is the most direct
  possible defense against label-only "multi-omic/integrative/orthogonal-validation" padding.
- **Circular-dependency detection** (Step 3): scans for language showing one lens was tuned/trained
  on the other's output, and *zeroes* the triangulation score when found. This is genuinely net-new
  — none of the other three catch the "computational model whose hyperparameters were chosen using
  the wet-lab result it then 'confirms'" failure, which is the single most epistemically important
  way a triangulation claim can be hollow. It is also invisible to the verifier.
- **Fixed 8-category taxonomy with no double-counting**: structurally forbids relabeling one
  pipeline's stages as multiple lenses, without depending on the LLM's discretion.

Scoring is well-behaved: diversity saturates at 3 concrete lenses, triangulation is gated on
connecting ≥2 *already-specific, non-circular* categories, and availability/thinness penalties are
multiplicative and always applied. Worked examples (che26/huu25/ali25/abstract-only) are concrete
and calibration-sane. Penalize-don't-skip is honored cleanly (constraints.md absent → 0.0;
abstract-only → 0.2–0.4 multiplier).

Weakness: the coarse fixed taxonomy conflates "category" with "failure mode," so two genuinely
independent same-category lenses (e.g. two wet-lab assays with uncorrelated failure modes) get
under-credited — a real, if defensible, tradeoff (the metric's own definition is failure-mode
independence, which the taxonomy only approximates). Triangulation is binary (1.0/0.0) where exp2/3
grade it. Net: the anti-name-drop and anti-circularity machinery outweighs these.

### exp3 — RANK 2
**Verdict: strong; best-articulated Goodhart resistance.** Two distinguishing strengths:
- **Fully multiplicative composition** — `base_lens_score(n) × (0.5+0.5·indep) × (0.5+0.5·integ) ×
  (0.4+0.6·refl) × availability_multiplier`. This is the cleanest structural argument in the field
  that no single axis (long lens list, or eloquent boilerplate, or one high sub-score) can buy a
  high score; every factor must be high simultaneously. Directly closes the "inflate one dimension"
  route.
- **Deterministic availability tier** (`absent`/`thin`/`full`) driven by a non-LLM boilerplate check
  (`is_boilerplate_constraints`) that operationalizes the shape doc's own "bare 'no limitations
  stated' is a red flag" note. This adds genuine determinism *outside* the LLM calls and is the
  most rigorous penalize-don't-skip treatment of the four — thinness caps the ceiling regardless of
  what got extracted, so "compile thin to dodge extraction" is a losing move.

The 0.4–0.6 confidence "logged but not counted" band keeps the extractor honest about uncertainty.
Worked cases are explicit and defend the demanding calibration (strong case reaches only 41.7/100).

Weaknesses: the boilerplate substring list is English-brittle (a floor heuristic, acceptable). The
docstring says `[0,1]` but the function returns `×100` — cosmetic inconsistency. The compressed
top-of-range (~42 for a genuinely strong paper) risks poor discrimination among good papers when
aggregated, though the reasoning defends it. Independence is a single scalar multiplier rather than
per-pair, so it can't express "3 lenses but two are correlated" as sharply as exp2's n_effective.

### exp2 — RANK 3
**Verdict: good; best scope discipline, weaker scoring.** Genuine strengths: the **n_effective**
construction (only lenses participating in ≥1 independent pair count toward triangulation) is the
most elegant handling of "3 lenses, two correlated → effective n=2" in the field. Its
composition/scope reasoning is the sharpest — explicitly refusing to re-score generic data-quality
caveats (leaves them to a data-quality metric) and refusing to reach into `evidence/` to reconcile
numbers (leaves that to verifier-style checks), which best preserves the net-new, tightly-scoped
edge. A single efficient sem call. Worked contrasts carry real arithmetic.

Weaknesses that drop it below exp3/exp4: (1) **additive scoring** (`0.45·A + 0.30·B + 0.25·C`) means
lens count + independence alone buys up to 0.45 with zero integration and zero constraints work — a
real single-axis gaming surface that the multiplicative designs (exp3/exp4) close. (2) Bundling
extraction + independence + integration + reflection into **one sem call** is efficient but less
adversarial than a dedicated independence/circularity pass; self-consistency bias makes the model
less likely to overturn its own lens labels. No circularity check.

### exp1 — RANK 4
**Verdict: solid baseline, least differentiated.** Real strength: the **dedicated adversarial
independence-audit as a separate call** (Step 3) that collapses pseudo-lenses sharing a data
source/assumptions back to `independent_lens_count` — a genuinely good anti-gaming move that exp2
folded (weaker) into one call. Reasoning on the epistemic case (uncorrelated failure modes) is
crisp, and the integration multiplier (0.40/0.70/1.00) plus constraints multiplier are sensible.

Weaknesses: the scoring uses hand-tuned magic numbers with the least justification of the four, and
the single-lens branch awards a bonus via a **substring match** (`"boundary"`/`"scope is limited"`
in constraints_text) — a small but real Goodharting surface (trivially satisfiable) even if capped
at 0.20. It also takes `SemOutputs` as *precomputed* (Step 6), so it is the least end-to-end/runnable
as written. No concreteness gate and no circularity detection, so it is the least defended against
the brief's specific name-dropping concern. Nothing here is net-new relative to what exp3/exp4 do
better.

---

## WINNERS: exp4, exp3

### Winner critiques + cycle-2 directions

**exp4** — Keep the concreteness gate, circularity detection, and no-double-count taxonomy; these
are the metric's crown jewels. Cycle-2 fixes:
1. **Decouple "category" from "failure mode."** The coarse 8-category taxonomy under-credits two
   independent same-category lenses (two wet-lab assays with uncorrelated batch/reagent failure
   modes). Add a within-category independence sub-judgment: allow a second same-category lens to
   count only if the sem call affirms *distinct data source AND distinct failure mode* with a quote.
   This preserves the anti-padding intent while fixing the false-negative.
2. **Grade triangulation instead of binary.** Replace `triangulation_score ∈ {0,1}` with a
   strength scale (mentioned / one-directional-check / bidirectional-with-stated-concordance-or-
   discordance) as exp2/exp3 do — a single confirmatory Western blot should not score the same as a
   stated 9/12 concordance.
3. **Borrow exp3's deterministic thinness/availability tier** to replace the ad-hoc `thin =
   len<200` char check, so the floor logic is principled rather than a magic constant.

**exp3** — Keep the multiplicative chain and the deterministic availability tier; these are the
best-justified anti-gaming and penalize-don't-skip mechanisms in the field. Cycle-2 fixes:
1. **Import exp4's circularity check** — the one epistemically-critical gaming route exp3 currently
   misses (tuned-to-match "agreement"). Add it as a hard zero on `integration_score`.
2. **Import exp2's n_effective** — replace the single scalar `independence_score` multiplier with
   per-pair independence so "3 lenses, two correlated" collapses to effective n=2 sharply rather
   than being softened into one 0.0–1.0 knob.
3. **Recalibrate the ceiling.** A genuinely strong triangulated paper topping out at ~42/100
   compresses discrimination among good papers; either widen the range or document explicitly how
   this metric's output is normalized before suite aggregation.
4. **Fix the `[0,1]` docstring vs `×100` return** inconsistency, and make the boilerplate detector
   robust to non-English/paraphrased caveats (e.g. structural check: any limitations bullet with a
   concrete noun + failure-mode verb, rather than a fixed phrase list).

Cross-cutting cycle-2 direction for both: the metric's definition is *failure-mode* independence,
but every expander operationalizes it partly via method-category labels. The winner of cycle-2
should make failure-mode independence the primary, explicitly-quoted judgment and treat category as
a secondary heuristic — this is where the metric is most likely to be either over- or under-crediting.

### Loser one-liners
- **exp2**: Elegant n_effective and the best scope discipline in the field, but additive scoring
  lets lens-count buy ~0.45 with no integration, and its single bundled sem call is less adversarial
  — strong ideas worth harvesting into a winner, not a standalone winner.
- **exp1**: Sound baseline with a good dedicated independence-audit call, but hand-tuned magic
  numbers, a substring-gameable single-lens bonus, a precomputed-SemOutputs (non-end-to-end)
  workflow, and no concreteness/circularity defenses leave it the least differentiated and least
  Goodhart-resistant.
