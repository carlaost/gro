# M36 — Multi-perspective triangulation (expander 2)

## 1. Expanded reasoning

### What it signals
Single-lens results are only as trustworthy as that lens's own failure modes: a computational
prediction can be an artifact of model bias; a wet-lab assay can be an artifact of batch effects,
reagent lots, or observer expectation. When a paper independently arrives at the same conclusion
through two or more methodologically orthogonal routes — wet-lab × computational, simulation ×
observational cohort, statistical meta-analysis × mechanistic model, qualitative expert read ×
quantitative pipeline — the chance that *all* lenses share the same blind spot drops sharply. This
is classic triangulation: convergent evidence from independent failure modes is structurally
stronger than the same volume of evidence from one method repeated. M36 rewards papers whose
`logic/solution/` layer shows (a) genuinely independent lenses were combined, (b) they were used to
cross-check rather than merely juxtapose, and (c) `constraints.md` demonstrates the authors
understood what each lens can and cannot prove, including where the *combination* itself has an
unaddressed gap (e.g., "computational hits were validated in only N=3 wet-lab replicates, not
powered to detect the effect size claimed for the full computational cohort").

### What it must reward
- **Genuine methodological orthogonality**: lenses whose systematic errors don't correlate (different
  data source, different instrument/assay, different modeling assumptions, different investigator
  role).
- **Explicit cross-validation intent**: the method files state that one lens's output was checked
  against another's, not just that both were performed.
- **Constraints that track the composite**: `constraints.md` names a limitation *specific to* each
  lens, plus (when relevant) an interaction-level caveat about the seam between lenses (calibration,
  sample-size mismatch, temporal/cohort mismatch between the wet-lab and computational arms).

### What it must NOT reward
- **Counting sections, not lenses.** A paper with `study_design.md` + `method.md` + `heuristics.md`
  for a single computational pipeline is not "multi-perspective" — those are stages of one lens, not
  independent lenses. The metric must actively distinguish *pipeline decomposition* (many files, one
  lens) from *triangulation* (possibly one file, multiple lenses).
- **Token secondary analyses.** A one-sentence "we also searched the literature to confirm plausibility"
  bolted onto an otherwise single-lens paper should not count as a second lens — it must be
  substantive enough to have its own extractable method detail and its own stated limitation.
- **Correlated pseudo-lenses.** Two computational models fit to the same dataset with the same
  preprocessing are not independent lenses even if described as "two approaches" — same failure
  modes, same data source.
- **Single-lens work being treated as defective.** A pure statistical-synthesis review (like the
  che26 example in the shape doc, which has only `study_design.md`) is not doing anything wrong by
  being single-lens; it simply does not earn this metric's bonus. This must not leak into a
  global penalty — M36 is additive credit for triangulation, not a tax on legitimate single-method
  work. (The floor/degenerate cases below are about *thinness/unavailability*, not single-lens-ness
  per se.)

### Failure modes / gaming routes
1. **Padding for the metric**: authors (or a compiler trying to score well) inflate an incidental
   mention into a "lens" — countered by requiring each lens to have *substantive, quoted* method
   content and by an independence check that rejects lenses without their own failure-mode profile.
2. **Narrative triangulation without evidentiary triangulation**: prose claims "confirmed across
   modalities" without the method files actually describing a comparison step — countered by
   requiring the integration evidence to cite a concrete comparison (a stated concordance metric,
   a replication count, a stated agreement/disagreement outcome), not just adjectives.
3. **Constraints boilerplate**: a generic "results should be interpreted with caution" limitation
   copy-pasted regardless of which lenses were used — countered by requiring the constraints
   reflection check to match specific lens IDs, not just presence of *a* limitations section.
4. **Genre-forced files masquerading as a second lens**: e.g., an `architecture.md` appearing for a
   paper with no actual model (a known Seal-Level-1 defect per the shape doc's Availability notes) —
   this must be flagged and treated as a data-quality defect that *suppresses* the lens count rather
   than inflating it.
5. **Compiler under- or over-splitting files**: because method-file naming is genre-free-form, a
   compiler could split one lens across multiple files (inflating apparent richness) or merge two
   real lenses into one file (deflating it). The extraction step must operate on *content*, not file
   count, precisely to be robust to this.

### How the assessment-critique's notes reshape the design
The ledger entry says this metric is "genuinely absent from both round-1 and the verifier" and
ranked top-10 specifically for being net-new/tightly scoped. Two scoping decisions follow directly:
- **Do not re-litigate generic data-quality caveats.** The shape doc's "Additional caveats surfaced
  during compilation" subsection (table/caption mismatches, PRISMA arithmetic) is the natural
  territory of a *different* metric (data-quality/internal-consistency). M36 only inspects caveats
  that are specific to the multi-lens combination — it must not double-count a generic caveat as
  "reflecting triangulation" just because it happens to sit in the same file.
- **Stay inside `logic/solution/`.** Corroborating that the lenses' results actually agreed (e.g., by
  reading `evidence/` tables) would overlap with an ARA-verifier-style cross-artifact consistency
  check and would require reading artifacts outside this metric's assigned scope. M36 is scoped to
  whether the *method as designed and bounded* shows real triangulation intent and honesty about its
  seams — not whether the numbers in a different layer happen to reconcile. This keeps the metric
  cheap, unambiguous in scope, and non-redundant with verifier-style cross-checks.

## 2. Generation / compute workflow

### Inputs (artifact fields)
From `logic/solution/` only:
- `constraints.md` (always present) — full text, all sections including the optional
  "Additional caveats surfaced during compilation" subsection.
- All sibling method files present (`study_design.md`, `method.md`, `architecture.md`,
  `algorithm.md`, `heuristics.md`, `design.md`, `formalization.md`, `proofs.md`, or any others) —
  full text of each, tagged with filename.
- Structural metadata: which files exist (used for the genre-mismatch check), and whether
  `constraints.md` is the degenerate "abstract-only" floor case (bare or near-empty, no method file
  at all beyond it — per the shape doc's Availability notes).

No `[sem]` calls to Semantic Scholar / Undermind / clinical-trial lookups are needed — the entire
signal lives inside this one artifact section. One LLM (`[sem]`, used here as "semantic/LLM
extraction" not literature search) call is required because "is this a genuinely independent lens"
and "does this constraint specifically address that lens" are semantic judgments, not
string-matchable.

### Step 1 — Assemble input bundle (deterministic)
```python
def assemble_bundle(constraints_md: str, method_files: dict[str, str]) -> dict:
    """method_files: {filename: content}, e.g. {"study_design.md": "...", "method.md": "..."}"""
    abstract_only = (
        len(method_files) == 0
        and len(constraints_md.strip()) < 400  # bare/near-empty per shape-doc floor case
    )
    return {
        "constraints_md": constraints_md,
        "method_files": method_files,
        "abstract_only_floor_case": abstract_only,
    }
```

### Step 2 — Single `[sem]` extraction call
Concatenate `constraints.md` + all method files (each clearly delimited with a filename header) and
send ONE structured-extraction prompt:

> **Prompt (`[sem]`, extraction, temperature 0):**
> "You are extracting structural facts from a paper's method/constraints layer. Below is the full
> text of `constraints.md` and every method file this paper's compiler produced, each preceded by
> `### FILE: <name>`.
>
> A **lens** is an independent methodological route to evidence — it has its own data source and its
> own characteristic failure modes (examples: wet-lab/experimental assay, computational/statistical
> model or simulation, systematic-review/meta-analytic pooling, clinical/observational cohort,
> qualitative/expert judgment). Two sub-steps of the *same* pipeline (e.g., preprocessing then
> modeling on the same dataset) are ONE lens, not two. Two models fit to the same data with the same
> preprocessing are ONE lens.
>
> Return strict JSON:
> ```
> {
>   "lenses": [
>     {"id": "L1", "taxonomy": "<wet-lab|computational|statistical-meta-analytic|observational-clinical|simulation|literature-synthesis|qualitative-expert|other>",
>      "substantive": true|false,   // false if only a token/one-line mention with no extractable method detail
>      "evidence_quote": "<verbatim short quote establishing this lens>",
>      "source_file": "<filename>"}
>   ],
>   "independence_pairs": [
>     {"a": "L1", "b": "L2", "independent": true|false,
>      "reason": "<why their failure modes are/aren't correlated>"}
>   ],
>   "integration_evidence": [
>     {"lenses": ["L1","L2"], "strength": "none|mentioned|cross_validated",
>      "quote": "<verbatim evidence, or empty string if strength=none>"}
>     // strength=cross_validated requires a stated comparison outcome (concordance stat, replication
>     // count, explicit agreement/disagreement finding) — not just "both were done"
>   ],
>   "constraints_reflection": [
>     {"lens_id": "L1", "has_specific_limitation": true|false,
>      "quote_or_empty": "<verbatim limitation naming this lens's own failure mode, or empty>"}
>   ],
>   "interaction_level_caveat_present": true|false,   // a caveat about the SEAM between lenses
>                                                       // (sample-size/cohort/timing mismatch between
>                                                       // arms, calibration between modalities, etc.)
>   "interaction_level_caveat_quote": "<verbatim or empty>",
>   "genre_mismatch_flag": true|false,   // a method file's genre clearly doesn't fit what the paper did
>                                          // (e.g. architecture.md for a paper that trained no model)
>   "genre_mismatch_note": "<one line or empty>"
> }
> ```
> Only mark `independent: true` when the two lenses' errors plausibly do not correlate. Only mark
> `substantive: true` when the lens has real extractable method content beyond a passing mention.
> Be conservative — under-crediting a borderline lens is preferred to over-crediting."

### Step 3 — Deterministic scoring from the extraction JSON
```python
from itertools import combinations

def score_triangulation(bundle: dict, extraction: dict) -> dict:
    """
    bundle: output of assemble_bundle()
    extraction: parsed JSON from the [sem] call in Step 2
    Returns {"score": float in [0,1], "components": {...}, "notes": [...]}
    """
    notes = []

    # --- Hard floor: degenerate / unavailable input ---
    # Penalize-don't-skip: an abstract-only artifact cannot be scored N/A, it scores at the floor.
    if bundle["abstract_only_floor_case"]:
        return {
            "score": 0.0,
            "components": {"lens_count": 0, "integration": 0.0, "constraints_reflection": 0.0},
            "notes": ["floor: constraints.md is abstract-only / no method files present — "
                      "cannot demonstrate triangulation, scored at floor rather than skipped"],
        }

    lenses = extraction.get("lenses", [])
    substantive = [l for l in lenses if l.get("substantive")]
    ids_substantive = {l["id"] for l in substantive}

    # Independence: keep only pairs among substantive lenses marked independent
    indep_pairs = [
        p for p in extraction.get("independence_pairs", [])
        if p["a"] in ids_substantive and p["b"] in ids_substantive and p.get("independent")
    ]

    # Build the count of lenses that participate in at least one independent pair
    # (a "lens" with no independent partner doesn't contribute to triangulation, even if substantive —
    # e.g. three lenses where only two are mutually independent means effective n=2, not 3)
    triangulating_ids = set()
    for p in indep_pairs:
        triangulating_ids.add(p["a"])
        triangulating_ids.add(p["b"])
    n_effective = len(triangulating_ids)

    # --- Component A: lens count & independence (0..1) ---
    if n_effective <= 1:
        A = 0.0
        notes.append("single-lens (or no independently-corroborated lens pair): "
                     "no triangulation bonus — not a defect in itself, just no credit here")
    elif n_effective == 2:
        A = 0.5
    else:  # 3+
        A = 1.0

    # Genre mismatch is a data-quality defect on this artifact section: suppress, don't zero out,
    # since it may still coexist with real content elsewhere in the same files.
    if extraction.get("genre_mismatch_flag"):
        A *= 0.5
        notes.append(f"genre mismatch flagged: {extraction.get('genre_mismatch_note','')}")

    # --- Component B: integration / cross-validation strength (0..1) ---
    relevant_integration = [
        e for e in extraction.get("integration_evidence", [])
        if set(e.get("lenses", [])) <= triangulating_ids and len(e.get("lenses", [])) >= 2
    ]
    if not triangulating_ids or not relevant_integration:
        B = 0.0
    else:
        strength_map = {"none": 0.0, "mentioned": 0.5, "cross_validated": 1.0}
        B = max(strength_map.get(e.get("strength", "none"), 0.0) for e in relevant_integration)

    # --- Component C: constraints reflect the multi-lens composition (0..1) ---
    if not triangulating_ids:
        C = 0.0
    else:
        reflect = {
            r["lens_id"]: r.get("has_specific_limitation", False)
            for r in extraction.get("constraints_reflection", [])
        }
        covered = sum(1 for lid in triangulating_ids if reflect.get(lid))
        per_lens_frac = covered / len(triangulating_ids)
        interaction_bonus = 0.25 if extraction.get("interaction_level_caveat_present") else 0.0
        C = min(1.0, 0.75 * per_lens_frac + interaction_bonus)
        if per_lens_frac == 0.0:
            notes.append("constraints.md does not name a limitation specific to any identified lens "
                         "— boilerplate risk")

    score = 0.45 * A + 0.30 * B + 0.25 * C

    return {
        "score": round(score, 4),
        "components": {"lens_count_independence": A, "integration": B, "constraints_reflection": C,
                        "n_effective_lenses": n_effective},
        "notes": notes,
    }
```

### Worked contrast (illustrative, not literal example data)
- A paper with `study_design.md` describing a wet-lab CRISPR screen AND `method.md` describing an
  independent computational off-target prediction pipeline, where the text states "N=12 top
  computational hits were tested in the wet-lab screen; 9/12 replicated (75% concordance)," and
  `constraints.md` has a limitation naming the screen's power and a separate one naming the
  prediction model's training-data bias, plus a caveat that the two arms used non-overlapping cell
  lines: `n_effective=2`, `A=0.5`, integration `strength=cross_validated` → `B=1.0`, `C≈1.0` →
  score ≈ 0.45·0.5 + 0.30·1.0 + 0.25·1.0 = 0.775.
- The che26-style pure statistical-synthesis review (`study_design.md` only, one lens): `n_effective≤1`
  → `A=0,B=0,C=0` → score 0. Correct: no triangulation claim was ever made, so no credit, no
  penalty beyond simply not scoring on this axis.
- A paper claiming "validated computationally and experimentally" but whose method files show the
  "experimental" step is one confirmatory Western blot for a single protein with no comparison
  statistic stated, and `constraints.md` never mentions the blot's limitations: lenses may extract
  as substantive and independent (`A=0.5`), but `integration_evidence.strength="mentioned"` not
  `cross_validated` (`B=0.5`) and `constraints_reflection` per-lens coverage is 0 (`C≈0`) → score ≈
  0.225 — correctly low despite the marketing language.

## 3. Why hard to Goodhart, and composition with the suite

**Hard to Goodhart** because the score requires *three independent things to align*: (1) a lens must
be substantive enough to survive extraction as having real, quotable method content — not a
sentence fragment; (2) it must be judged independent of the other lens on failure-mode grounds, which
resists gaming by simply relabeling one pipeline's stages as two "lenses" (the independence check
explicitly instructs the extractor to treat same-data/same-preprocessing variants as one lens); and
(3) the constraints layer must separately, and specifically, name each lens's own limitation — a
generic disclaimer does not satisfy this. An author or compiler would have to genuinely run and
report two orthogonal methods, connect them with a real comparison outcome, *and* honestly scope
each one's limits, to max the score — at which point they have simply done better science, which is
the point. The floor case (abstract-only artifact) is scored at 0 rather than skipped, so thin
compilation cannot be gamed into a neutral/missing score either.

**Composition with the rest of the suite**: M36 is deliberately narrow — it does not re-score
generic internal-consistency/data-quality caveats (that belongs to a data-quality-caveats metric
over `evidence/`), and it does not check whether the lenses' *numeric results* actually agree (that
would be an ARA-verifier-style cross-artifact reconciliation, out of scope for a single-section
metric). It only asks: was more than one methodologically orthogonal route to evidence actually
used, was it used to check itself, and does the paper own up to where that combination is still
weak. This keeps it additive rather than double-counting with structural/rigor metrics elsewhere in
the suite, and preserves its top-10 justification of being genuinely new coverage.
