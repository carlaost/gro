# Validator Reliability — inter-rater check of the [sem] judges (P8)

Addresses **P8** in `research/metrics/v3/critiques/cycle1.md`: the [sem] LLM judges that produced
`research/metrics/v3/sem_findings/<slug>.yaml` are themselves unvalidated instruments, and the
project's own trace (N12/N13) documents that LLM judges inflate grades. Before any judge output is
trusted we need inter-rater reliability. This report re-judges a gold subset with an **independent
second rater** (a fresh model session that never saw the frozen findings, the sem code, or this
critique) and measures agreement against the frozen findings.

**Method.** Rater A = the frozen `sem_findings/<slug>.yaml` (rater of record). Rater B = an
independent judge given only `research/ara-library/<slug>/logic/claims.md` and the underlying source
files it cites (`research/data/lib/<slug>/metadata.md`, `PAPER.md`, `evidence/**`, and where present
the local `paper.pdf`). Rater B judged **first**, blind, then results were compared. Three fields per
claim: `evidence_relevance.relevant` (bool), `falsifiability.verdict`
(post_hoc_inversion | real_precommitted | trivial | absent), `scope_calibration.verdict`
(calibrated | over_claim | under_claim). Cohen's κ implemented by hand, stdlib only
(κ = (pₒ − pₑ)/(1 − pₑ), pₑ from the product of each rater's marginals; multi-class handled by
summing the diagonal for pₒ and Σ marginal products for pₑ). n = 20.

---

## 1. Gold subset (20 claims, 5 ARAs)

Chosen to span ≥5 ARAs and to include every contested finding named in the critique plus uncontested
controls:

| # | ARA | Claim | Why included |
|---|-----|-------|-------------|
| 1–5 | the25 | C01–C05 | **Contested**: DOR-certainty over-extension flagged on all five assays |
| 6–7 | the25 | C06, C07 | Uncontested controls (relevant=true; a `real`/`trivial` falsifiability pair) |
| 8–9 | jes26 | C01, C02 | Uncontested controls (well-grounded RCT endpoints) |
| 10 | jes26 | C09 | **Contested**: "amyloid clearance maintained" |
| 11 | huu25 | C01 | Uncontested control |
| 12 | huu25 | C02 | **Contested**: "MAPT also downregulated" |
| 13–14 | huu25 | C03, C08 | Controls (C08 = the ARA's one `real_precommitted`) |
| 15–18 | cum26 | C01, C02, C03, C06 | **Contested**: cum26 falsifiability (all judged `real_precommitted`) |
| 19–20 | woj25 | C02, C05 | Uncontested pair from the one previously-`usable` ranker |

---

## 2. Per-field agreement and Cohen's κ

| Field | Raw agreement | Expected (chance) | Cohen's κ | Landis–Koch band |
|-------|--------------:|------------------:|----------:|------------------|
| `evidence_relevance.relevant` (binary) | **19/20 = 0.950** | 0.530 | **+0.894** | almost perfect |
| `scope_calibration.verdict` (3-class) | **19/20 = 0.950** | 0.530 | **+0.894** | almost perfect |
| `falsifiability.verdict` (4-class) | **10/20 = 0.500** | 0.515 | **−0.031** | none (≈ chance / worse) |

Confusion matrices (frozen → independent):

- **evidence_relevance**: (F,F)=7, (T,T)=12, (T→F)=1. Single disagreement: woj25 C05.
- **scope_calibration**: (over,over)=7, (calib,calib)=12, (calib→over)=1. Single disagreement: woj25 C05.
- **falsifiability**: (post_hoc,post_hoc)=8, (real,real)=1, (trivial,trivial)=1,
  **(post_hoc→real)=5, (real→post_hoc)=5**. Ten disagreements, evenly split in both directions.

---

## 3. The disagreements — claim by claim

### 3a. `falsifiability` — 10/20 disagreements, the whole field is unreliable

The two raters agree on *whether a criterion exists* and its wording, but split almost coin-flip on
the **post_hoc_inversion ↔ real_precommitted** boundary — the exact boundary the metric monetizes
into `falsifiability_quality`. κ = −0.031 means the frozen verdicts carry essentially **no signal a
second competent rater reproduces**.

- **the25 C01–C05 (5 claims): frozen=post_hoc_inversion, independent=real_precommitted.**
  Same criterion text ("a comparably powered meta-analysis … yields a higher pooled AUROC/DOR").
  Rater A reads it as a same-data rerun (negation-by-construction); Rater B reads "a *different*,
  future meta-analysis on a different study base" as an independent external test. **Both readings are
  defensible** — the criterion is genuinely ambiguous about whether the re-analysis uses the same 113
  studies. This is not one rater being wrong; it is the category boundary being under-defined.
- **cum26 C01, C02, C03, C06 (4 claims): frozen=real_precommitted, independent=post_hoc_inversion.**
  The mirror-image disagreement, and the more consequential one. Rater A credits "re-enumerate
  ClinicalTrials.gov / compare against DrugBank" as an independent external check. Rater B read
  `concepts.md`/`experiments.md` and found those *are the exact data source and method the census
  already used* ("repurposing status is determined by comparing pipeline agents against DrugBank" —
  identical to the proposed falsification), so re-running them is a same-pipeline recount, not an
  independent test. **Here I judge Rater B (independent) closer to right**: re-doing the paper's own
  enumeration with the paper's own rules is reproducibility, not falsification. This directly
  undercuts the frozen `falsifiability_quality` scores that let cum26 (a narrative census with no
  experiments) score well.
- **the25 C06: frozen=real_precommitted, independent=post_hoc_inversion.** Re-applying QUADAS-2 to
  the same 113 studies. Reasonable both ways; leans Rater B (same study set).

**Net:** every disagreement is a `post_hoc_inversion`/`real_precommitted` swap. The κ≈0 is not noise
around a good instrument — it is the instrument's central distinction failing to replicate. The
critique's P6 ("falsifiability_quality ranks compiler-authored text; retire as paper-ranker") is
**independently corroborated**: two raters cannot even agree what the compiler-authored criterion
*is*, let alone rank papers by it.

### 3b. `evidence_relevance` and `scope_calibration` — 1 disagreement each, both on woj25 C05

- **woj25 C05: frozen relevant=true / scope=calibrated; independent relevant=false / scope=over_claim.**
  Rater B digitized `evidence/figures/figure4.md` and found that in the validation cohort's CSF, the
  single-site p-tau217 fold-change (~9.2) exceeds the double-phospho p-tau217&231 (~4.3), contradicting
  the Statement's "highest … in **both** CSF and plasma" — and noted the Statement conspicuously omits a
  validation-CSF number while citing the other three matrix/cohort cells. Rater A accepted the three
  cited numbers and did not reconstruct the omitted cell. **Rater B is more rigorous here** (it checked
  the cell the claim left out); but this is a single borderline call, and the fold-change read from a
  digitized figure is itself uncertain. Both fidelity fields still land at κ=0.894.

---

## 4. Do the two raters independently confirm the contested findings are COMPILER errors, not PAPER flaws?

Yes — unanimously, and I verified each against the in-repo source myself:

- **the25 C01–C05 (DOR-certainty).** `research/data/lib/the25.../metadata.md` FINDINGS attaches
  "(…, moderate/low certainty of evidence)" to sensitivity, specificity, and AUROC for every assay,
  but states each diagnostic odds ratio **bare** (e.g. "diagnostic odds ratio of 50·7 (40·6–63·4)").
  The claims.md Statement's "**all** at moderate certainty of evidence" is a clause the **compiler
  added** on top of a faithful transcription of the numbers. Not a paper flaw — the paper never graded
  the DOR. (Also independently recorded in the ARA's own `logic/grounding_findings.yaml`: "the source
  sentence attaches no GRADE certainty qualifier to this DOR … the certainty attribution is not
  grounded.") Both raters: relevant=false, scope=over_claim. **Confirmed compiler transcription error.**
- **jes26 C09 ("clearance maintained").** The source Discussion (§4) says *"the rate of amyloid
  **reaccumulation** was comparable to that seen with the natural history of the disease."* The
  Statement's "amyloid **clearance was maintained** after treatment completion" is the **opposite**
  framing, with **no Sources quote covering the clause** (its three quotes cover only the 154-week
  effect, the 29% progression figure, and the 74.8% placebo figure). This is a compiler-introduced
  **inversion**, echoed identically in `study_design.md` and `experiments.md`. Both raters:
  relevant=false, scope=over_claim. **Confirmed compiler inversion — the woj25/N13-class bug.**
- **huu25 C02 (MAPT).** The cited §2.6 quote lists the downregulated set as "PLP1, MAG, MAL, MBP,
  SOX10, and OPALIN." **MAPT appears in no Sources quote and in no evidence file** (checked
  `figure5.md`; `grounding_findings.yaml` also has no MAPT entry). "MAPT also downregulated" is an
  **ungrounded compiler addition**. Both raters: relevant=false, scope=over_claim. **Confirmed
  compiler insertion.**

So the three "over-claim / irrelevance" findings that the [sem] judges use to *discriminate* papers
are, on independent re-judgment, **100% compiler-transcription/insertion errors** — added clauses, a
flipped conclusion, an ungrounded gene. The critique's P2/P3 diagnosis holds under a second rater:
**these judges are compiler-fidelity detectors, not paper-quality rankers.** Every flaw they catch is
in the extractive layer, not in the underlying science; C16 (the "faithful re-view" axiom that
licenses paper-ranking) is empirically false on exactly these claims.

---

## 5. Bottom line — are these judges reliable enough that their output should count?

**Split verdict, and it cuts against the leaderboard:**

1. **Fidelity-type judgments are reliable (κ ≈ 0.89) but measure the wrong thing.** The near-perfect
   agreement on `evidence_relevance` and `scope_calibration` is real — two independent raters
   reproduce the same flags. But **every non-trivial flag is a compiler error**, so a reliable
   instrument here is a reliable *compiler-QA* instrument. High κ does not rescue the label: it
   confirms the critique's core claim that these are fidelity detectors wearing a paper-quality label.
   Both fields should be **rerouted to the trust/fidelity axis** (P2), where their reliability is an
   asset, and must **not** count toward `usable` paper-rankers.

2. **`falsifiability_quality` is not reliable at all (κ = −0.031) and should not count in any form.**
   Its central `post_hoc_inversion` vs `real_precommitted` distinction is at chance between two
   competent raters. A metric whose per-item verdicts a second rater cannot reproduce cannot rank
   papers, cannot be `validated`, and cannot be `judge_scored` with a straight face. This
   independently confirms P6 (retire it as a paper-ranker).

3. **On the headline "3 validated paper-rankers":** of the three fields the [sem] tier turns into
   rankers, two (evidence_relevance, scope_calibration) are reliable-but-are-fidelity-metrics, and one
   (falsifiability_quality) is unreliable outright. **None survives as a science-quality paper-ranker.**
   Per P8's ask — report κ *before* any judge output counts — the honest reading is: the fidelity
   judges' output may count **as compiler-fidelity signal on the trust axis**; the falsifiability
   judge's output should **not count at all** until the category boundary is operationalized and
   re-tested. This is consistent with the critique's "honest usable count: 0–1."

**Caveats.** n = 20, single reviewer pair, single topic (AD biomarkers/therapeutics); κ CIs are wide
at this n (treat the two 0.89 values as "high" and the −0.03 as "≈0", not as three-decimal truths).
Several sources are abstract-only (the25) or PDF-absent (huu25), so "compiler error" is judged against
the best in-repo source, not always the full paper — which is itself P4. A larger, multi-model panel
is the proper next step; but even this minimal check is decisive on the two load-bearing questions:
the contested findings are compiler errors (confirmed), and the falsifiability ranker is unreliable
(confirmed).
