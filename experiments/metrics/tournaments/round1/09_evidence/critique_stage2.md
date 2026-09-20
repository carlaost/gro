# Stage 2 critique — `09_evidence`

## (1) Did each winner address the stage-1 critique?

### A (= agent1) — all three points addressed, cleanly, with no collateral damage
- **Soft floors killed.** `sweep_completeness_score` now returns `0.0` (not `0.2`) when no numbered
  reference exists anywhere to reconstruct a ceiling; `numeric_reconciliation_transparency` returns
  `0.0` (not `0.4`) when nothing is arithmetically checkable; `extraction_honesty_score` and
  `claims_grounding_coverage` both hard-`0.0` on an empty evidence base. This is now genuine
  hard-constraint discipline, not a shrug, and the rationale (a real scientific table almost always
  carries at least one labeled count) is defensible.
- **Substance gate added.** `is_substantive_trend()` (numbers + ≥2 named-entity-like tokens) is now
  applied in BOTH Metric 2's fallback-validity check and Metric 3's `quantitative_plot` branch — the
  exact gap named in stage 1. A one-sentence placeholder trend summary can no longer farm either metric.
- **Fragile last-int heuristic replaced.** Metric 5 now extracts every *labeled* total (`n=`, total,
  screened, included, identified, records, studies) from caption and prose and tries each as a
  reconciliation target, closing the "rephrase the caption so the inconvenient count isn't last"
  dodge. Solid.

All five metrics remain live, content-sensitive, and mutually coupled after the fixes.

### B (= agent3) — all three points addressed, but two of the fixes cost signal
- **`self_scrutiny_score` rewritten.** The stage-1 metric fired on any non-summing pair (branding
  nearly every honest artifact inconsistent); it now fires only on an anchored near-miss — an
  explicit `a+b+c` expression the compiler itself wrote, or a column literally labeled `total`/`sum`,
  landing in the narrow "should-match-but-doesn't" band. Correct fix. **But** the metric is now
  near-inert for typical artifacts: most evidence sets contain no verbatim sum expression and no
  `total`-labeled column, so the function collapses to the no-finding branch and returns a constant
  (`0.6`/`0.25`) driven by boilerplate-detection rather than by real self-scrutiny. It fixed a
  false-positive machine by turning it into a rarely-firing one — honest, but this metric now
  contributes little live signal to the combination.
- **Neutral 0.5 reframed.** Now `0.6` only if anchored verification language (discrepancy word +
  ≥2 real numbers) appears elsewhere, else a real `0.25` penalty. Good — but see above: this branch
  is what fires most of the time.
- **Per-object `max_v` made explicit.** Done, and the cross-kind named-skip leak in Metric 1 was
  also fixed (a nice catch beyond the critique). **But** Metric 2 ships an acknowledged-unreachable
  branch (the `conf == "low" and table and not trend` case inside the `else`, kept "for schema
  robustness") — a small compute-soundness blemish the stage-1 brief explicitly weighs.

B's signature strengths survive intact: `claim_grounding_score`'s distinct-ratio + justified-unlinked
terms and `source_locatability_score`'s page/screenshot/caption decomposition remain the best
claim-and-provenance signals in the field.

---

## (2) WINNER: A

A resolved every stage-1 point without weakening any metric, and keeps five live, sound,
mutually-coupled checks. B fixed its broken metric correctly but rendered `self_scrutiny_score`
near-inert (a constant for most artifacts) and left an unreachable branch in Metric 2 — so B, post-fix,
effectively runs ~four live metrics plus one boilerplate-detector, against A's five. On uniform compute
soundness and a joint combination where gaming one metric still costs another, A is the more trustworthy
system.

This is a genuinely close call, and the decisive trade is stated plainly in the qualifier below: B is
better on the layer's single most important dimension, and A wins on everything else.

---

## (3) QUALIFY the winner

**What A genuinely measures.** Epistemic *hygiene* of the evidence layer, along five axes: (1) whether
the systematic sweep is complete or gaps are named-with-a-reason (with a sharp reason-keyword window
check that defeats bare-mention skip-listing and junk-file padding); (2) internal honesty of extraction
labels — `≈`-vs-`exact` consistency in both directions, no numeric tables smuggled into diagrams,
recursing into `mixed` panels; (3) type-body structural conformance with a real substance gate on
low-confidence fallbacks; (4) claims-grounding *coverage* with a thinness penalty; (5) numeric
reconciliation transparency anchored on labeled totals. Axes 1, 2, 3, and 5 are strong, honest,
hard-constraint-respecting measures of transcription discipline and self-consistency.

**Where it is still gameable or limited.**
- **Its claims-grounding metric (M4) is the soft spot — and it sits on the layer's core purpose.**
  M4 credits raw coverage (fraction of rows carrying a non-empty `Claims` column) with only a size
  penalty. Uniform rubber-stamping of one real claim ID onto every row drives coverage to `1.0`. A's
  defense — "fabricated links are caught by cross-referencing claims.md" — is real but *out of scope
  for a blind single-artifact judge*. B's distinct-claim-set ratio guarded exactly this within the
  artifact; A does not. So A measures the evidence→claims grounding function only at the coverage
  level, and that measurement is the most Goodhartable in the set.
- **M1's ceiling is inferred from the max referenced object number.** Non-contiguous numbering, or a
  highest-numbered object that is never referenced in a source string, mis-estimates the ceiling in
  either direction. It also depends on source strings actually carrying "Table N"/"Figure N".
- **M2/M5 only catch honesty relative to the artifact's own internal tells** (`≈` markers, labeled
  totals). A compiler that never estimates and never prints a labeled total sidesteps the positive
  signal — though the new `0.0` floors now punish total absence rather than rewarding it.
- **Nothing here verifies the numbers are actually right against the source.** Every check is
  internal-consistency or provenance-shape; correctness of transcription still needs the screenshots
  plus a human / Level-2 pass.

**What it would take to trust it.** Bolt B's distinct-claim-set / specificity guard onto M4 so
grounding can't be won by blanket-stamping; pair the set with a cross-artifact resolver that confirms
claim IDs actually resolve in `claims.md`, and a screenshot-vs-transcription spot check for M2/M5's
fidelity claims.

**Does it clear "measures good science"?** Honest-but-limited. A robustly and Goodhart-resistantly
measures the *honesty and completeness* of the evidence layer — real epistemic hygiene, jointly hard to
game across four of its five metrics. But it measures the layer's core scientific function — grounding
claims in evidence — only at a coverage level that a single uniform edit can inflate. It is a trustworthy
honesty-and-completeness instrument, not yet a trustworthy grounding instrument.
