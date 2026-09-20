# Stage 2 critique — `11_dataset`

Judge: metascientist + incentive designer. Artifact: `data/dataset.md` (+ `data/preprocessing.md`).
Contestants: improved/A.md (stage-1 agent1, rank 1) vs improved/B.md (stage-1 agent2, rank 2).

## Did each winner address my stage-1 critique?

### A (was agent1) — 3 directions, all addressed

1. **Access-Tier over-penalizing single-tier data — FIXED, well.** The old 0.5 catch-all is split into
   four buckets: bare single-tier claim (0.3, the lazy "available" pattern), single-tier scoped to a
   named data layer (0.65), explicit affirmative all-open disclaimer (0.9), and genuine open+gated
   contrast (1.0). This is exactly the correction I asked for and it honors the shape doc's "all-open is
   legitimate, not a defect" point without collapsing it into the lazy-blanket bucket. The `ALL_OPEN_RE`
   is a reasonable, checkable trigger.
2. **Discrepancy Self-Audit row-count-only — FIXED.** Now runs two typed reconciliation axes: stated
   *count* aggregates (studies/datasets/cohorts) vs. row count, and stated *participant/sample* aggregates
   vs. a summed `N`-column. A mismatch on either routes through the flagged/silent branch. This catches
   che26's real arithmetic mismatch, which the old version would have missed. Notably, the unit-typing is
   *precise* — it only compares count-units against rows and N-units against the summed column, avoiding
   spurious cross-type matches.
3. **No preprocessing-traceability axis — FIXED** by adding metric 6 (Preprocessing Traceability
   Proportional to Raw-Data Claims), lifted from agent3's best idea, with QC vocabulary deduped by
   *dimension* (filtering / normalization / batch correction / exclusion / pipeline version) so
   keyword-stuffing one term is capped. Correctly scores secondary-reuse (no raw claim) as full credit —
   a scored outcome, not a skip — satisfying the hard constraint.

Critically, A **retained** its Genre-Scope Fidelity metric (metric 4), which I singled out in stage 1 as
the standout orthogonal Goodhart check no rival has: a "generated in this study" claim must be backed by
a real accession ID in the block header. A now covers six axes including the pool's single hardest-to-fake
honesty signal.

### B (was agent2) — 4 directions, all addressed

1. **Ambiguous access-tier construct — FIXED, cleanly.** Split into two explicitly named sub-scores:
   (A) per-claim qualification density, (B) document-level layer differentiation, combined 0.6/0.4. This
   is good construct hygiene and the worked landing point (single-tier fully-qualified → 0.92) is sensible.
   One residual: construct (B) rewards using ≥2 distinct data-*layer* words, which is not the same as
   open-vs-gated *tier* contrast — "raw open, processed open" (two layers, no gating) still scores 1.0 on
   differentiation. B renamed it honestly to "names more than one data layer," so this is disclosed
   slippage rather than a hidden bug, but A's 1.0 bucket (requires co-occurring open AND gated language)
   is the truer contrast measure.
2. **Discrepancy row-count-only — FIXED** with summed-N-column reconciliation. Sound. Minor: it grabs
   *all* ≤4-digit integers from the intro as candidate stated numbers, which is noisier than A's typed
   approach (a citation year like "2023" enters the candidate set), though the set-intersection logic
   makes accidental false-reconciliation unlikely in practice.
3. **Preprocessing scored as binary presence — FIXED** by scoring `min(distinct QC dimensions / 3, 1.0)`
   across five deduped categories. Same fix A applied to the same underlying critique.
4. **Density constant asserted, not justified — DONE, and this is B's best work.** B actually calibrated
   against huu25 and che26, and calibration *surfaced two real bugs*: (i) the genomics-only regex set
   floored the entire secondary-reuse genre to 0.0 despite che26's PROSPERO ID, cited source studies, and
   populated 6-column table — a genre-fairness defect that would have been ungamed-but-unfair; (ii) a
   short stub with one lucky hit saturated the ratio off a tiny denominator. Both fixed (citation +
   registration regexes, per-cell table credit, and a `length_factor` discount). Post-fix the three cases
   the shape doc distinguishes (rich primary, rich secondary, abstract-only floor) now separate correctly
   (~1.0 / ~1.0 / ~0.05). This is exactly the empirical, self-adversarial rigor the brief rewards.

Both sets addressed every direction. Neither dodged.

## WINNER: A

A wins on the two axes the brief weights most heavily — Goodhart-resistance and combination logic — while
matching B everywhere else:

- **A retains the single most Goodhart-resistant metric in the entire tournament** (Genre-Scope Fidelity:
  "generated in this study" ⇒ verifiable accession in header). This is an orthogonal, cheap-to-check,
  hard-to-fake honesty signal targeting hallucinated provenance directly. B has no equivalent; its
  genre-consistency metric checks that secondary-reuse doesn't fabricate raw QC (a negative check A also
  has) but never ties a generation *claim* to a verifiable *identifier*.
- **A's discrepancy logic is sounder.** Typed unit-matching (counts→rows, N→summed column) is less noisy
  and less spuriously satisfiable than B's "all ≤4-digit intro integers" candidate set.
- **A's access-tier 1.0 bucket is the truer construct** — it requires genuine open+gated co-occurrence,
  whereas B's top differentiation bucket can be earned by two same-tier layers.
- **Coverage:** A ends at six interlocking axes including the retained standout; B at five.

B's genuine edge is calibration discipline — it is the only set that ran its own numbers and caught two
real bugs, which is admirable and is the reason this was close. But that rigor is applied to a *surface*
metric (specificity density) and hardens B against unfairness rather than adding a deeper science signal.
A's Genre-Scope check is a structural honesty test B simply lacks. Decisive edge to A.

## QUALIFY THE WINNER

**What A genuinely measures:** the *documentation quality and internal honesty of the dataset descriptor*
— (1) how specifically access tiers are disclosed (open vs. controlled, scoped to a named data layer),
(2) how concretely provenance is stated (accession IDs, exact dimensions, named instruments), (3) whether
the artifact's own stated aggregates reconcile with its tabulated rows and summed N, (4) whether content
is genre-appropriate and generation claims carry verifiable accessions, (5) whether ethics/consent is
disclosed in a genre-appropriate way, and (6) whether a QC trail scales to the raw-data claims made. It is
a strong, well-interlocked proxy for *provenance-documentation discipline* — the trait of a compiler (and
a paper) that actually engaged with its own data pipeline rather than writing boilerplate.

**Where it is still gameable / limited:**

- **Every metric is a text/token-presence check, not a truth check.** All six count regex-matched
  identifiers, keywords, and structural patterns in the artifact text. They verify that checkable-*looking*
  tokens are present and mutually consistent — not that the tokens are *true*. A compiler emitting a
  fabricated-but-internally-consistent record (invented accession IDs, a plausible IRB number, a real
  instrument name, a cohort table whose N column sums correctly to a stated total) would score highly. The
  "hard to Goodhart" essays repeatedly lean on the phrase "an auditor checking the linked GEO/dbGaP
  record" — but the metric itself never resolves an accession against a real registry. External
  verification is assumed, not performed.
- **The interlock raises the cost of *cheap* gaming, not *careful* gaming.** Buzzword-padding fails
  because it collides with the specificity and genre checks — this is real and valuable. But a determined
  adversary who fabricates a fully coherent provenance record defeats the whole set, because internal
  consistency is exactly what the metrics reward and fabrication-with-consistency is what they cannot
  distinguish from truth.
- **It measures the compiler as much as the science.** A meticulous compiler over a mediocre paper can
  score well; these axes reward documentation of provenance, not the validity of the study's inferences,
  the appropriateness of its cohorts, or whether the data support the claims.

**What it would take to trust it as a "good science" measure:** bind the identifier checks to live
registry resolution (GEO/SRA/dbGaP/PROSPERO lookups confirming the accession exists and its stated access
tier matches the record), and confirm IRB/consent tokens against the source paper. With that grounding
layer, A would move from "did the compiler write a checkable-looking record" to "is the record true."

**Verdict on the bar:** A does **not** clear the strong bar of "measures good science" in the deep sense
(validity of the data or the inferences). It **does** clear "measures good, honest documentation of data
provenance" — and it is the most Goodhart-resistant, best-interlocked, genre-aware instrument in the pool
for that target. Honest-but-limited: a high-quality provenance-discipline proxy, not a science-validity
oracle.

WINNER: A
