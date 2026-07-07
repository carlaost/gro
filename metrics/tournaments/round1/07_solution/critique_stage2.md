# Stage 2 critique — `07_solution` (method layer)

## Did each winner address the stage-1 critique?

### A (= agent2, stage-1 rank 1) — all three faults fixed, cleanly.
1. **M4 loose `ENTITY_PATTERN`** → fixed. `extract_weighted_entities` now requires true ALL-CAPS
   acronyms, an embedded-digit alphanumeric ID, or a numeric quantity; a `GENERIC_STRUCTURAL_WORDS`
   blocklist drops boilerplate nouns; ubiquitous cross-domain acronyms (AUC/CI/SD/…) are down-weighted
   to 0.3. This is a genuine (corpus-free) IDF surrogate and directly kills the "Results/Table/Cohort
   recur for free" hole. The crown-jewel grounding-overlap metric is now materially harder to inflate.
2. **No dedicated assumption-quality metric** → added Metric 5, Assumption→Consequence Traceability —
   and hardened past agent1's original: it requires *both* an ID/entity link back to the assumption
   *and* explicit failure/violation language, with a Jaccard near-duplicate filter that disqualifies
   verbatim re-listing. It reuses M4's weighted extractor so the linkage must be substantive.
3. **M2 empty `evidence_flags` → 1.0** → fixed with an explicit `evidence_check_ran` attestation; only a
   confirmed-ran, zero-flags state earns 1.0; unconfirmed/unwired states floor to 0.2.

Net effect: A retained the field's single best mechanism (structural within-artifact grounding overlap)
AND absorbed the field's deepest science signal (assumption→consequence), improving it in the process.

### B (= agent1, stage-1 rank 2) — all four faults fixed, competently.
1. **M2 copy-paste hole** → fixed with graded Jaccard: near-duplicates (≥0.55) disqualified unless they
   add consequence language; only genuine paraphrase (0.2–0.55) or id/consequence cues count.
2. **M4 lenient + off-list free pass** → fixed. Off-list filenames are now scored on the same
   content-evidence basis; a file scores 0.0 if it shows zero signature hits itself or if its claimed
   genre is barely present corpus-wide — directly targeting the "architecture.md on a stat-synthesis
   review" defect the shape doc names.
3. **M3 `SOFTWARE_CALL` false-positive** → fixed; now requires camelCase/snake_case identifier + a
   non-empty arg list, so "Cohort (described above)" no longer counts.
4. **M5 inert 0.1 floor** → fixed with an explicit three-state contract (ran=False → 0.0; ran + no
   inconsistencies → 1.0; ran + inconsistencies → anchor-overlap coverage), tied to the compiler pass
   that already must populate the caveats subsection.

Both sets did the assigned work. This is decided on the merits of the improved architecture, not on
who fixed more boxes.

## WINNER: A

**Why A over B.** A's flagship metric (Assumption/Boundary Grounding Overlap) enforces cross-layer
coherence *structurally and entirely within the artifact* — constraints must echo distinctive entities
that actually recur in the method files, both of which the compiler emits together. It needs no external
pipeline input to be computable, so it is reliably live on every artifact. B's only true cross-layer
check (M5, data-quality coverage) is strong in principle but depends on an `evidence_check` input being
honestly wired from a different layer; B itself concedes it "assumes it is available." After stage 2, A
now *also* carries B's deepest idea (assumption→consequence), with a stricter dual-linkage requirement
than B's own version. So A dominates on composition: it has the structural anti-Goodhart tie B lacks,
plus a hardened copy of B's best signal. B's one genuine edge — M3's line-level reproducibility-density
in method files — is the most surface-leaning metric in either set (it counts lines carrying version
strings / `param=value`), so it does not offset A's structural advantage.

## QUALIFY the winner

**What A genuinely measures:** the *documentation rigor and internal coherence of the compiled method
layer* — whether `constraints.md` is written in paper-specific, concrete, falsifiable language (M1);
whether its named referents actually recur in the method files rather than being template boilerplate
(M4); whether stated assumptions are examined for what breaks if they fail rather than merely listed
(M5); whether method-file naming honestly matches the paper's genre and known implementation tricks are
captured (M3); and whether compiler-detected evidence-layer inconsistencies are surfaced rather than
laundered (M2). It is a strong, largely orthogonal proxy for "the constraints/method layer was genuinely
derived from and faithful to this work, and its assumptions were thought through."

**What it is NOT:** it does not measure whether the underlying science is good. A perfectly rigorous
paper and a deeply flawed one can both produce a specific, cross-referential, self-examined method layer;
A scores the honesty and specificity of the *write-up*, not the validity of the design, the correctness
of the statistics, or the truth of the conclusions.

**Where it is still gameable / limited:**
- **M4/M5 numeric channel is loose.** `NUMERIC_PATTERN` admits bare digits at full weight (only listed
  acronyms are down-weighted), so a stray shared "9" or "20" between constraints and methods can register
  as a grounding match. Real, but a residual dilution of the crown jewel's precision.
- **Transplant attack is only indirectly defended.** An author with the method files in hand can copy
  distinctive method vocabulary into `constraints.md` to inflate M4 without improving the actual quality
  of the limitation. A argues M1/M3 catch the resulting hollow bullets, but that defense is cross-metric
  and probabilistic, not structural.
- **M2 rests on an unverifiable attestation.** `evidence_check_ran` is a pipeline flag; a compiler that
  falsely sets it (with a fabricated empty flag list) claims the 1.0 path. A correctly prices the
  unverifiable state at 0.2, but the honest-1.0 path is only as trustworthy as the attestation.
- **Field-wide entity extraction is regex-shallow** — no semantic understanding, so paraphrased grounding
  (a limitation naming a concept the method describes in different words) is missed, understating good work.

**Verdict:** honest-but-limited, at the top of that band. It clears the bar of being a defensible,
jointly-constraining proxy that rewards examined, paper-specific method documentation and resists the
cheapest gaming — but it measures the rigor and faithfulness of the compiled method layer, not "good
science" directly. Trusting it as a science signal would require: replacing the regex entity channels
with semantic matching, tightening the bare-numeric match, and an independent audit trail for
`evidence_check_ran` so the 1.0 path cannot be asserted from within a single layer.
