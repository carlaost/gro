# M48 — End-to-end reproducibility bundle — Expansion (expander 4)

## 1. What the indicator is actually claiming

The one-liner: "Do figure + data + code co-exist across layers for actual end-to-end replication
(constraints, setup, comprehensive reporting)?" This is a **cross-layer integration** question, not
a single-layer completeness question. Three artifact families are in scope:

- **F (figure/evidence leg)** — `evidence/` (§9): the grounded numbers a reader would need to check
  the paper's reported results against.
- **D (data leg)** — `data/dataset.md` (+ `preprocessing.md`) (§11): where the numbers in F actually
  came from, and whether a third party could get the same inputs.
- **C (code/setup leg)** — `src/environment.md` + `src/configs/*.md` + `src/execution/*` (§10): the
  runtime, parameters, seeds, and (where it exists) the literal code that turns D into F.

"End-to-end replication" means someone outside the original team could, in principle, take D, run C
under the stated environment/constraints, and reproduce (or meaningfully check) F. The metric is
**not** "does each layer individually look complete" (that's what single-layer §9/§10/§11 checks in
the rest of the suite already do) — it is **whether the three layers actually chain together** into
one coherent, attemptable pipeline, or whether they are three disconnected artifacts that happen to
sit in the same repo.

## 2. Why this signals good science

Reproducibility is the mechanism by which a claim stops being "trust me" and becomes "check me."
A paper can have a beautiful, complete evidence ledger (§9) and still be practically unreplicable if
nobody can tell what data fed the analysis or what code/parameters produced the numbers. Conversely a
paper can release code and data separately without them being *legibly connected* — the classic case
of "the repo exists, the dataset exists, but nothing tells you the config in the repo is the one that
produced Table 2." Good science bundles all three so a skeptical reader's chain of verification never
hits a dead end. This is a distinctly cross-layer signal: no single layer's own internal completeness
proves the bundle *coheres*.

## 3. What it must reward vs. must not reward

**Must reward:**
- All three legs present, mutually consistent, and traceable to each other (dataset dimensions in
  `dataset.md` match what `src/execution` or `src/configs` operate on; environment dependencies match
  what code actually imports; evidence tables/figures cite the same cohorts/accessions named in
  `dataset.md`).
- Honest, well-justified absence of a leg when the genre doesn't call for it (che26-style pure
  meta-analysis: no code because none was released, explicitly stated in `## Code availability`, and
  `data/dataset.md` correctly describes secondary summary-data reuse rather than fabricating a
  primary dataset).
- Explicit access-tier disclosure (open vs. controlled-access) rather than a blanket claim.
- Grounding-tag discipline (`transcribed` vs `reconstructed`) on every `src/execution/*` file, and
  `NotImplementedError("Not specified in paper")` stubs rather than invented logic.

**Must not reward:**
- Presence-only checklist satisfaction — a `data/dataset.md`, an `environment.md`, and an
  `evidence/` folder that exist but never reference each other (three legs, zero bundle).
- A fabricated or reconstructed-but-passed-off-as-real code stub that "fills the C leg" without any
  real grounding (Critical Rule #11-style violation: inventing API names/constants not traceable to
  source).
- A repo that was provided as input but got flattened to a one-line pointer in `artifacts.md` instead
  of real files in `src/execution/` (explicit FAIL condition per §10 availability notes) — this must
  not read as "leg C partially present," it must read as a coverage failure.
- Collapsing "open vs. controlled-access" into a single "data available" claim.
- Silent gaps: a paper whose evidence layer is clearly built on real generated data (quantitative
  tables, named cohorts, accessions in captions) but has no `data/dataset.md` at all and no
  disclosure of why.

## 4. Failure modes / gaming routes

1. **Padding one leg to average out a missing one.** If scored as a simple mean of three leg scores,
   a compiler could nail the evidence leg (easy — it's just transcription) and phone in D and C,
   still landing near 60-70%. Countered in §6 by using a sub-additive combination (geometric mean +
   hard cap), not an arithmetic mean.
2. **Fabricating a plausible-looking `dataset.md` or code stub to farm the presence check.** A
   compiler (or a bad-faith author) could write a fluent-sounding but ungrounded provenance
   paragraph or a syntactically valid but invented code stub. Countered by requiring **cross-layer
   consistency**, not just per-layer well-formedness — a fabricated leg is very likely to *not*
   numerically/nominally match the other two legs (wrong sample size, wrong parameter values, wrong
   accession format), which is checkable without needing ground truth from the original paper.
3. **Genre-laundering.** Claiming "pure theory paper, no data/code needed" to legitimately skip legs
   is a real pattern for papers that DO have empirical content. Countered by cross-checking the
   genre claim against the evidence leg itself (if §9 contains `quantitative_plot`/`raw_table`
   objects with real measured values, the "no data" claim is contradicted and must be penalized, not
   waived).
4. **Silent omission mistaken for legitimate absence.** The spec explicitly distinguishes "correctly
   absent" (huu25's uncloned 15GB repo, disclosed in `artifacts.md`) from "silently dropped." A naive
   presence-only check can't tell these apart; the workflow below requires the disclosure text itself
   to be present and specific, not just the absence of the field.
5. **Verifier-overlap gaming.** If the assessment-critique's underlying verifier (D6) already checks
   "does the ARA mention reproducibility," an author could satisfy D6 with a throwaway sentence while
   M48 should not be satisfied by that — M48 requires the structural coexistence and coherence, so a
   throwaway mention scores ~0 here even if it scores fine on D6.

## 5. How the assessment-critique notes reshape the design

The ledger note says this ranked top-10 *because* it's "net-new vs. the ARA verifier" and "scoped
tighter than verifier D6's mention of reproducibility." Two design consequences:

- **Don't re-derive D6.** D6 apparently just checks whether reproducibility is *mentioned/addressed
  somewhere*. M48 must not just re-score that same surface signal with different wording — its
  distinct value-add is the **cross-layer coherence check** (§6 step 4), which D6 cannot express
  because D6 (per the ledger description) isn't scoped as a whole-ARA structural traversal. The
  workflow below therefore weights the coherence sub-score most heavily and treats bare per-layer
  presence as necessary-but-not-sufficient.
- **Scope tightly to the three named legs, not all of §10/§11/§9.** The brief's phrase "(constraints,
  setup, comprehensive reporting)" maps onto specific §10 substructures — `environment.md` (setup),
  `configs/*.md` (constraints/parameters), `execution/*` (the code itself) — not the whole of §10.
  Similarly the D leg is scoped to `dataset.md`'s access/provenance content, not general data quality
  (there may be a separate metric for pure data quality elsewhere in the suite; redundancy is avoided
  by scoping D here strictly to "is it findable/gettable and does it match what F and C claim to
  operate on," not "is it a good dataset").

## 6. Generation / compute workflow

### Inputs (exact artifact fields)
- `evidence/README.md` (completeness-note prose + table/figure index)
- `evidence/tables/*.md`, `evidence/figures/*.md` (per-object fields: Extraction type/method, Reading
  confidence, Figure type, data tables, Notes)
- `src/environment.md` (Language/runtime, Framework, Hardware, Data sources, Key dependencies,
  Protocols, Random seeds, optional `## Code availability` / `## Data availability` subsections)
- `src/artifacts.md` (per-block: File(s) in repo, Nature, What it does, How to use, Claims supported)
- `src/configs/*.md` (per-parameter: Value, Rationale, Search range, Sensitivity, Source)
- `src/execution/*.{py,r,...}` (grounding-tag first line, body)
- `data/dataset.md` (+ `data/preprocessing.md` if present): provenance/access blocks, cohort tables,
  consent/ethics, access-tier language

### Step 1 — Leg F (evidence) structural score
Deterministic parse:
- Extract the README completeness-note prose; regex/LLM-extract the self-reported total count of
  numbered tables/figures vs. filed count vs. named-skipped-with-reason count.
- For every `evidence/figures/*.md`: verify `quantitative_plot` has either a data table or an
  explicit `Reading confidence: low` + `## Trend summary` fallback (structural FAIL if neither);
  verify `diagram`/`qualitative_sample` contain no numeric data table masquerading as extracted data;
  verify `Extraction method: exact_from_labels` co-occurs with bare (non-`≈`) values, and
  `digitized_estimate` co-occurs with `≈`-prefixed values.

### Step 2 — Leg D (data) presence/quality + genre check
- Detect genre signal from `environment.md`'s `Language/runtime` field: literal `"analytical — none"`
  or an explicit "no primary data collected" framing → candidate for legitimate D-absence.
- Cross-check against Step 1: scan filed evidence tables for signs of primary generated data
  (sample sizes, accession-like strings, "generated in this study" language in captions/notes). If
  such signals exist but `data/dataset.md` is absent or silent → **silent-gap flag** (hard penalty,
  §6 Step 5).
- If `data/dataset.md` present: score access-tier honesty by checking co-occurrence of an access
  claim ("open", "available") with its qualifier ("controlled via dbGaP", "by request",
  "Supplementary material only"); score accession completeness (real-looking accession format e.g.
  `GSE\d+`, `PROSPERO CRD\d+`); score consent/ethics presence for primary-data genre.

### Step 3 — Leg C (code/setup) presence/quality
- `environment.md` mandatory-field completeness: every field non-blank (value or explicit
  `"Not specified in paper"`/`"n/a"` — a truly blank field is a defect, an honestly-labeled unknown is
  not).
- If no `src/execution/*` files: require a `## Code availability` subsection explaining why (mirrors
  che26's justified-no-code case). Absence of both code AND this explanation → penalty.
- If `src/execution/*` files exist: every file's first line must be `# Grounding: transcribed` or
  `# Grounding: reconstructed`; `reconstructed` files must not contain function bodies with named
  constants/APIs absent from `environment.md`'s Key dependencies or `configs/*.md` (heuristic
  fabrication smell — flag for LLM adjudication in Step 4b).
- `src/artifacts.md`: check "File(s) in repo" entries read as verified real paths/URLs, not vague
  pointers, when `Nature` implies a real captured pipeline; a repo cited only by name with no
  execution files captured and no explicit "not cloned, scope decision" language is the FAIL case
  from §10's availability notes.

### Step 4 — Cross-layer coherence (the net-new signal; weighted highest)
4a. **Deterministic anchor extraction**: pull numeric/named anchors from each leg — sample sizes,
cohort names, accession IDs, dataset dimensions, hyperparameter values, dependency versions.

4b. **[sem] LLM adjudication call** — one call per ARA, given the three legs' anchor sets plus raw
text of `environment.md`, `dataset.md`, and any `configs/*.md`/`execution/*` excerpts:

```
SYSTEM: You are a strict reproducibility auditor. You will be given three excerpts from one research
artifact: (F) the evidence layer, (D) the data layer, (C) the code/environment layer. Decide whether
they describe ONE coherent, chainable pipeline or whether they are disconnected.

For each of the following, answer yes/no/not-applicable with a one-sentence reason grounded in the
text (quote the specific phrase):
1. Do sample sizes / cohort names / accessions mentioned in F also appear in D?
2. Do parameter values or dataset dimensions in C (configs/execution) match what D describes?
3. Do C's declared dependencies/environment plausibly support producing F's reported figure/table
   types (e.g. a stats-only environment producing a deep-learning figure is a mismatch)?
4. Is any leg's absence (F, D, or C) explicitly and specifically justified in the text, vs. just
   silently missing?
5. Is there any invented-looking fact in C or D (a name, package, or number) that does not trace to
   anything else in the bundle?

Output strict JSON: {"f_d_match": bool, "c_d_match": bool, "c_f_plausible": bool,
"absence_justified": bool|null, "fabrication_suspected": bool, "notes": str}
```

4c. Convert to `coherence_score ∈ [0,1]`:
`coherence_score = mean(f_d_match, c_d_match, c_f_plausible) `, then multiplied by `0.4` if
`fabrication_suspected` is true, and if any leg is missing, `absence_justified` gates whether that
leg's expected contribution to the coherence mean is dropped (justified) or counted as a hard `0`
match (unjustified/silent).

### Step 5 — Final scoring function

```python
from dataclasses import dataclass
from statistics import geometric_mean

@dataclass
class LegScore:
    presence_quality: float   # 0..1, from Steps 1-3 structural parse
    honest_absence: bool      # True if leg is absent but explicitly, specifically justified
    silent_gap: bool          # True if leg is absent/thin with no justification, contradicted
                               # by evidence in another leg
    fabrication_flag: bool    # True if content looks invented / ungrounded

FLOOR = 0.02          # legs are never literally zeroed to avoid a single bad parse nuking the score
SILENT_GAP_CAP = 0.20 # hard ceiling on the leg's own score if silently missing
FABRICATION_CAP = 0.15

def leg_final(leg: LegScore) -> float:
    if leg.fabrication_flag:
        return min(leg.presence_quality, FABRICATION_CAP)
    if leg.silent_gap:
        return min(leg.presence_quality, SILENT_GAP_CAP)
    if leg.honest_absence:
        # legitimate absence: real ceiling below "present & complete", because an
        # objectively-missing leg is still objectively less end-to-end reproducible —
        # unavailability is itself an input to the score, never a skip.
        return max(FLOOR, min(leg.presence_quality, 0.55))
    return max(FLOOR, leg.presence_quality)

def m48_score(leg_f: LegScore, leg_d: LegScore, leg_c: LegScore,
              coherence_score: float) -> float:
    """
    Returns 0..1. Sub-additive combination (geometric mean, not arithmetic mean) so that
    one badly-missing/fabricated leg drags the whole bundle down rather than being
    averaged away by the other two — this directly encodes "penalize missing any leg."
    """
    f, d, c = leg_final(leg_f), leg_final(leg_d), leg_final(leg_c)
    base = geometric_mean([max(f, FLOOR), max(d, FLOOR), max(c, FLOOR)])

    # coherence_score in [0,1] from the [sem] adjudication call (Step 4c); it can only
    # discount the base score, never inflate it above what the legs themselves earned —
    # coherence proves the legs chain together, it can't manufacture missing content.
    coherence_multiplier = 0.5 + 0.5 * coherence_score   # range [0.5, 1.0]
    score = base * coherence_multiplier

    # Hard-fail mirror of Seal Level 1 Critical Rule #11 (fabrication) and the §10 FAIL
    # condition (real repo flattened to a pointer): any fabrication flag caps the WHOLE
    # bundle, not just its own leg, since a fabricated leg poisons trust in the others'
    # claimed cross-references too.
    if leg_f.fabrication_flag or leg_d.fabrication_flag or leg_c.fabrication_flag:
        score = min(score, 0.20)

    return round(score, 4)
```

This is deliberately **not** `mean(F, D, C)`: a compiler that nails F and D but silently drops C
(a very common shortcut — evidence and dataset provenance are "free" transcription work, code
capture is the labor-intensive leg) gets capped near `geometric_mean(f, d, 0.20) * multiplier`,
which lands well below what an arithmetic mean would give, matching the brief's explicit
"penalize missing any leg" instruction rather than softly discounting it.

### Step 6 — Optional external verification call
Where `src/artifacts.md` or `data/dataset.md` cites a live external identifier (GitHub repo, GEO/SRA
accession, Zenodo DOI, PROSPERO registration), an optional deterministic external lookup (HTTP HEAD /
API call to GitHub contents API, NCBI E-utilities, or Zenodo API) confirms the identifier resolves
and, where feasible, that the repo's top-level file listing is consistent with what `artifacts.md`
claims was captured. A dead link or a repo whose real contents contradict the captured description
feeds back into `fabrication_flag`/`silent_gap` for the relevant leg. This call is optional (network
access may be unavailable at scoring time) — its absence must itself be logged as a scoring input
("external verification unattempted") rather than silently treated as "verification passed."

## 7. Why this is hard to Goodhart

- **Multi-file, cross-format consistency is expensive to fake.** Gaming this metric requires
  fabricating numbers/names in at least two independently-formatted layers (a markdown provenance
  doc AND a code/config file, or a table AND an environment doc) that agree with each other well
  enough to survive the LLM coherence check — this is strictly harder than padding one file to pass
  a single-layer checklist.
- **The geometric-mean + hard-cap combination removes the "average away the gap" strategy.** A
  bad-faith compiler cannot bank points on two easy legs (evidence transcription, a plausible-sounding
  `dataset.md`) to compensate for skipping the labor-intensive one (real code capture); the structural
  design forces roughly equal investment in all three legs to reach a high score.
- **Genre-conditioning is checked against evidence content, not self-declared.** Claiming "no data/no
  code needed" only helps the score if the evidence layer itself doesn't contradict that claim
  (Step 2's cross-check), closing the most obvious loophole (claim non-empirical genre to legally skip
  legs).
- **Fabrication caps the whole score, not just one leg's sub-score**, removing the incentive to
  fabricate a single component in isolation since the return is capped at 0.20 regardless of the
  other two legs' quality.

## 8. Composition with the rest of the suite

- **Vs. verifier D6** ("mentions reproducibility"): M48 subsumes and tightens it — a bundle can pass
  D6's mention-check trivially while scoring near-zero on M48 because M48 requires structural
  coexistence and the coherence adjudication, not a sentence. The two should not be treated as
  redundant in aggregate scoring; M48's weight should reflect that it is a strictly harder bar.
- **Vs. any single-layer §9/§10/§11 completeness metrics elsewhere in the suite**: those should own
  the "is this one layer internally well-formed" signal (Steps 1-3 above largely re-derive checks
  those metrics may already make). M48's unique contribution — and the reason it should not be
  discounted as redundant — is Step 4's cross-layer coherence score, which no single-layer metric can
  compute by construction. If the suite's final weighting has to break ties on redundancy, M48's
  weight should be concentrated on the coherence term, with the per-leg structural terms treated as
  gating/floor conditions rather than the primary differentiator.
- **Interacts with any "fabrication"/"grounding-honesty" metric elsewhere**: M48's fabrication cap
  should be the *same* fabrication signal a dedicated grounding-honesty metric would use, not an
  independently-invented one, so the two metrics agree on what counts as fabricated rather than
  disagreeing at the margin.
