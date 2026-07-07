# M36 — Multi-perspective triangulation (expander 4)

## 1. What this indicator actually signals

Good science is harder to fool when a claim survives contact with more than one
independent way of looking at the world. A result that only exists inside one
methodological lens — one assay, one model class, one statistical framework, one
literature-synthesis pass — has exactly one point of failure: if that lens has a
systematic bias, an unmodeled confound, a software bug, or a sampling artifact, the
whole conclusion goes with it. A result that is *triangulated* — reached or
corroborated from a second, epistemically-different vantage point (wet-lab confirming
a computational prediction, an independent cohort confirming a discovered association,
a formal proof confirming a simulation's asymptotic behavior, a meta-analysis pooling
estimate agreeing with a subsequent RCT) — has already survived one adversarial test
that single-lens work never faced.

This metric is not "did the paper do a lot of stuff" (that's a quantity/thoroughness
signal, already covered elsewhere in the suite) and not "is the method internally
sound" (that's a rigor/validity signal). It is specifically: **does the *evidentiary
structure* of the claim rest on more than one independent epistemic leg, and does the
artifact's method layer (§7, `logic/solution/`) make that structure visible rather than
flattening it into an undifferentiated pile of "methods"?**

### What it must reward
- Genuine methodological heterogeneity in service of the *same* scientific claim: e.g.
  a computational/predictive lens whose output is checked against a wet-lab/experimental
  lens; a statistical-synthesis lens (meta-analysis) whose pooled estimate is compared
  against a primary-cohort lens; a theoretical/formal lens (a proof or bound) whose
  prediction is checked against a simulation or empirical lens.
- Explicit *narration* of convergence or divergence between lenses — not just "we did X
  and also Y" side by side, but a stated comparison: agreement, disagreement, and (if
  divergent) how the divergence was handled or left as an open limitation.
- Honesty when triangulation is *absent*: a single-lens paper that explicitly flags "not
  independently validated by [orthogonal method]" as a limitation is doing something
  epistemically better than a single-lens paper that is silent about it, and the metric
  must be able to tell the two apart and reward the honest one somewhat, even though
  neither reaches the ceiling reserved for genuine multi-lens convergence.

### What it must NOT reward
- Buzzword diversity: a paper that lists "multi-modal," "multi-omic," or "integrative"
  in its abstract/constraints without the method files containing concrete, checkable
  detail (named tools, datasets, assay protocols, model architectures) for more than one
  lens. Labels are cheap; the metric must require *concreteness* per lens, not just a
  category tag.
- Two sub-analyses that are really the same lens wearing different clothes (e.g., two
  different statistical tests both run on the same single dataset are not
  "triangulation" — they are robustness-within-a-lens, which other suite metrics already
  cover). Triangulation requires the lenses to be *epistemically independent* — different
  failure modes, different data sources, or different theoretical assumptions.
- Post-hoc rationalization dressed as triangulation: if two lenses "agree" only because
  one was tuned/selected to match the other (e.g., a computational model whose
  hyperparameters were chosen using the wet-lab result it's then claimed to "confirm"),
  the constraints/heuristics layer would typically reveal this dependency (heuristics.md
  Bounds/Rationale, or constraints.md assumptions) — the workflow below explicitly checks
  for this circularity signal and down-weights it rather than crediting it as
  independent confirmation.

## 2. Failure modes / gaming routes and how the design defends against them

| Gaming route | Defense built into the workflow below |
|---|---|
| Sprinkle "multi-modal"/"integrative"/"orthogonal validation" language into constraints.md without real second-lens content | [sem] lens-extraction call requires a `concreteness` rating per lens (specific / vague / mentioned_only) grounded in a verbatim quote with named tools/datasets/parameters; only `specific` lenses count toward the diversity score |
| Claim two analyses as "independent lenses" when they're the same lens twice (e.g. two regressions on the same dataset) | Lens taxonomy is fixed and coarse-grained (8 categories, §3 below); the same category can't be double-counted, and the [sem] call is explicitly instructed to reject same-category duplicates |
| Fabricate a "triangulation" narrative that doesn't actually connect the two claimed-specific lenses | Triangulation-narrative [sem] call must return which *categories* the claimed convergence connects, and deterministic Python cross-checks that set against the categories found `specific` in the lens-extraction call — an unconnected or single-lens "triangulation" claim scores zero |
| Circular triangulation (one lens tuned to match the other) | [sem] call scans constraints.md/heuristics.md for dependency language ("calibrated to," "trained using the [other lens]'s output," "hyperparameter selected via") between the two claimed lenses; if found, triangulation_score is zeroed even though lenses are individually specific |
| Compiler/author simply omits the method files to dodge the metric (hoping N/A) | Forbidden by design — see §4 penalize-don't-skip; empty/abstract-only method layer is the worst-scoring case, not a neutral one |
| Author writes an unusually long, padded constraints.md to look thorough without adding real lens content | Length is never used as a proxy for anything except a floor thinness check; the diversity/triangulation scores are driven only by the [sem]-extracted, concreteness-gated content |

## 3. How the assessment-critique notes reshape this design

The ledger entry says this metric ranked top-10 specifically because it is **net-new**
relative to the ARA verifier and to round-1, and because it can be **scoped tighter**.
Two design choices follow directly:

1. **Scope discipline**: this metric does *not* try to re-litigate whether the method is
   internally valid (verifier / other metrics own that), how many assumptions are listed
   (a counting metric would own that), or whether the constraints are well-written prose
   (a clarity metric would own that). It owns exactly one question — cross-lens
   corroboration structure — and the scoring function below refuses to give credit for
   anything else (e.g. a beautifully detailed single-lens `method.md` scores low here on
   purpose, even though it might score high on a "method detail" metric).
2. **"Genuinely absent from round-1 and the verifier"** means there is no existing
   sub-score to reuse or overlap-check against; the workflow is therefore built entirely
   from primitives native to §7 (`constraints.md` + method files), not borrowed from
   another metric's intermediate output, so it stays additive rather than duplicative
   when the full suite is assembled.

## 4. Generation / compute workflow

### Inputs (artifact fields, from `logic/solution/` per `07_solution.md`)
- `constraints.md` (string; always present per the shape — "mandatory core, never absent
  though it can be thin")
- `method_files`: dict mapping filename → content, for whichever of
  `study_design.md`, `method.md`, `architecture.md`, `algorithm.md`, `heuristics.md`,
  `formalization.md`, `proofs.md`, `design.md` exist for this artifact (may be empty
  dict — the shape's documented "abstract-only" floor case)

No external/[sem] tool beyond an LLM call is required (no semantic-scholar / undermind /
FOL / clinical-trial lookup needed — this metric is fully answerable from within §7's own
text), but three LLM ([sem]) calls are used because "is this a genuinely distinct,
concretely-described epistemic lens" and "does the text narrate convergence" are semantic
judgments the artifact's free-form markdown does not encode structurally.

### Fixed lens taxonomy (used verbatim in the prompt, never invented ad hoc by the model)
```
wet_lab_experimental, computational_modeling, statistical_analysis,
clinical_observational, theoretical_formal, simulation,
literature_synthesis, field_survey_ecological
```

### Step 1 — Assemble method-layer text
```python
def assemble_method_text(constraints_md: str, method_files: dict) -> str:
    parts = [f"### FILE: constraints.md\n{constraints_md or ''}"]
    for fname, content in sorted(method_files.items()):
        parts.append(f"### FILE: {fname}\n{content}")
    return "\n\n".join(parts)
```

### Step 2 — [sem] call 1: lens extraction (concreteness-gated)
**Prompt** (sent once per artifact):
```
You are given the full method-layer text of a research artifact (its
constraints.md plus zero or more method files, each prefixed with its
filename).

Fixed lens taxonomy (use ONLY these category names):
wet_lab_experimental, computational_modeling, statistical_analysis,
clinical_observational, theoretical_formal, simulation,
literature_synthesis, field_survey_ecological

For each category, decide whether the text describes the work as ACTUALLY
EMPLOYING that lens with concrete, checkable detail (named tools, assays,
software, models, datasets, cohorts, or parameters) as opposed to a passing
mention or a label with no substance. Do not invent categories outside the
list. Do not count the same underlying analysis twice under two categories.

Return strict JSON:
{
  "artifact_empty": <true if constraints.md is empty/near-empty AND no
                      method files are provided>,
  "lenses": [
    {"category": "<one of the fixed categories>",
     "concreteness": "specific" | "vague" | "mentioned_only",
     "evidence_quote": "<verbatim span, <=40 words>",
     "file_source": "<filename>"}
  ],
  "genre_mismatch_flag": <true if a method file's name/content clashes with
                           what the paper actually appears to be, e.g. a
                           model.md for a paper that trained no model>,
  "genre_mismatch_note": "<one sentence or empty string>"
}

Method-layer text:
<<<ASSEMBLED_TEXT>>>
```

**Deterministic post-processing:**
```python
def specific_lens_categories(lens_extraction: dict) -> set:
    return {l["category"] for l in lens_extraction.get("lenses", [])
            if l["concreteness"] == "specific"}
```

### Step 3 — [sem] call 2: triangulation-narrative detection
Run only if `len(specific_lens_categories(...)) >= 1` (skip the call, don't
skip the score, if zero — step 6 handles the zero-lens floor directly).

**Prompt:**
```
Given this same method-layer text, and given that the following lens
categories were independently identified as concretely present:
<<<SPECIFIC_CATEGORIES_LIST>>>

Identify every place the text explicitly narrates a COMPARISON between two
or more of these lenses' results/predictions — convergence, divergence, or
mixed — as opposed to just describing each lens separately with no stated
comparison. Separately, flag any DEPENDENCY language indicating one lens's
parameters/output were derived from, tuned to, or trained on the other
lens's output (which would make an "agreement" circular rather than
independent corroboration).

Return strict JSON:
{
  "triangulation_claims": [
    {"lenses_connected": ["<category>", "<category>", ...],
     "direction": "convergent" | "divergent" | "mixed",
     "evidence_quote": "<verbatim span, <=40 words>"}
  ],
  "circular_dependency_pairs": [
    {"lenses": ["<category>", "<category>"],
     "evidence_quote": "<verbatim span>"}
  ]
}

Method-layer text:
<<<ASSEMBLED_TEXT>>>
```

### Step 4 — [sem] call 3: single/zero-lens honesty check
Run only if `len(specific_lens_categories(...)) <= 1`.

**Prompt:**
```
Given constraints.md's "Boundary conditions" and "Known limitations"
sections (below), does the text explicitly acknowledge that the work's
conclusions rest on a single methodological approach and have not been
independently corroborated by an orthogonal method or data source (e.g.
"not experimentally validated," "computational prediction only," "no
independent cohort confirms this association")?

Return strict JSON:
{"acknowledges_single_lens_limit": true|false,
 "evidence_quote": "<verbatim span or empty string>"}

Boundary conditions + Known limitations text:
<<<EXTRACTED_SECTIONS>>>
```

### Step 5 — deterministic scoring function
```python
def score_multi_perspective_triangulation(
    constraints_md: str,
    method_files: dict,
    lens_extraction: dict,
    triangulation_result: dict | None,
    single_lens_ack: dict | None,
) -> dict:
    """Returns {'score': float in [0,1], 'trace': {...}} — never returns
    None/N-A; every branch produces a real, penalized number."""

    # --- Hard floor: constraints.md itself is the mandatory core artifact ---
    if constraints_md is None or constraints_md.strip() == "":
        return {"score": 0.0,
                "trace": {"reason": "constraints.md missing/empty — "
                                     "mandatory core artifact absent"}}

    thin_constraints = len(constraints_md.strip()) < 200
    abstract_only = (len(method_files) == 0)
    artifact_empty = bool(lens_extraction.get("artifact_empty", False))

    specific = [l for l in lens_extraction.get("lenses", [])
                if l["concreteness"] == "specific"]
    categories = {l["category"] for l in specific}
    n_distinct = len(categories)

    # --- Diversity sub-score: saturates at 3 distinct concrete lenses ---
    diversity_score = min(n_distinct, 3) / 3.0

    # --- Triangulation sub-score: only counts claims that connect >=2 of
    #     the *specific* categories actually found, and are not flagged
    #     circular ---
    valid_triangulation = []
    if triangulation_result:
        circular_pairs = {tuple(sorted(p["lenses"]))
                           for p in triangulation_result.get(
                               "circular_dependency_pairs", [])}
        for t in triangulation_result.get("triangulation_claims", []):
            connected = set(t["lenses_connected"]) & categories
            if len(connected) < 2:
                continue
            pair = tuple(sorted(list(connected))[:2])
            if pair in circular_pairs:
                continue  # circular "agreement" earns nothing
            valid_triangulation.append(t)
    triangulation_score = 1.0 if valid_triangulation else 0.0

    # --- Combine, branching on whether real multi-lens structure exists ---
    if n_distinct >= 2:
        combined = 0.55 * diversity_score + 0.45 * triangulation_score
    else:
        acked = bool(single_lens_ack and
                      single_lens_ack.get("acknowledges_single_lens_limit"))
        # Honesty about single-lens scope is rewarded modestly but can
        # never approach the multi-lens ceiling.
        combined = 0.25 if acked else 0.05

    # --- Availability / thinness penalties: multiplicative, always applied,
    #     never substituted with a skip/N-A (HARD CONSTRAINT) ---
    penalty = 1.0
    if artifact_empty:
        penalty *= 0.2      # nothing to assess beyond a bare constraints.md
    if abstract_only and not artifact_empty:
        penalty *= 0.4      # constraints exist but no method files at all
    if thin_constraints:
        penalty *= 0.7
    if lens_extraction.get("genre_mismatch_flag"):
        penalty *= 0.85     # method-file genre mismatch undercuts trust in
                             # the lens read itself

    final = round(combined * penalty, 3)
    return {
        "score": final,
        "trace": {
            "n_distinct_specific_lenses": n_distinct,
            "categories": sorted(categories),
            "triangulated": bool(valid_triangulation),
            "abstract_only": abstract_only,
            "thin_constraints": thin_constraints,
            "penalty_applied": round(penalty, 3),
        },
    }
```

### Step 6 — worked examples (sanity check, not part of scoring code)
- che26 (plasma p-tau, pure statistical-synthesis review, per `07_solution.md`'s own
  example): likely `statistical_analysis` + `literature_synthesis` both `specific`
  (search strategy + pooled P-scores) → `n_distinct=2`; if constraints.md doesn't narrate
  an explicit convergence check between the synthesis estimate and any primary-cohort
  lens, `triangulation_score=0` → combined ≈ 0.55·(2/3) ≈ 0.37, likely no penalty →
  final ≈ 0.37. Correctly mediocre: real methodological breadth, but no stated
  cross-checking narrative.
- huu25 (APOE ε4, `study_design.md`+`method.md`): if these describe cohort/statistical
  work only (one lens family), and constraints.md doesn't flag the single-lens scope →
  combined = 0.05, likely thin-constraints penalty may or may not apply → very low.
  Correctly punishes silent single-lens work.
- ali25 (multimodal MRI/PET with heuristics.md on cross-modal distillation): plausibly
  `computational_modeling` + a second concrete lens depending on whether PET acquisition
  is described with wet-lab/clinical-observational concreteness, and heuristics.md's H03
  rationale is exactly the kind of convergence narrative call 2 is built to catch →
  potential for the high end of the range if triangulation is genuinely narrated.
- Abstract-only source (shape's documented floor case, no method files beyond bare
  constraints.md): `abstract_only=True`, almost certainly `n_distinct<=1` and
  `thin_constraints=True` → score lands near 0.02–0.05. This is the intended stark floor,
  reached by penalty multiplication, never by skipping.

## 5. Why it's hard to Goodhart

The score cannot be moved by writing *more* — it is gated at every stage by
`concreteness == "specific"` (verbatim, checkable detail) and by the requirement that a
triangulation claim *connect two already-specific categories* rather than merely use
convergence-flavored language. Faking it requires fabricating detailed, internally
plausible content for a second genuine methodology (specific tools/datasets/parameters)
*and* a coherent, non-circular narrative connecting it to the first — which is exactly
the kind of fabrication that tends to contradict the evidence layer's own numbers
(sample sizes, dates, tool versions) and would be caught by unrelated internal-
consistency checks elsewhere in the suite. Padding constraints.md with generic caveats
raises length but not concreteness, and length is explicitly not used as a positive
signal anywhere in the scoring function (only as a `thin_constraints` floor check on the
low end). Circularity detection (Step 3) also closes the cheapest real gaming route —
claiming "confirmation" from a lens that was itself calibrated to the first.

## 6. Composability with the rest of the suite

This metric is deliberately narrow and orthogonal:
- It does not score *how well* any single method was executed (rigor/validity metrics
  own that) — a paper can score high here with two only-moderately-rigorous lenses that
  genuinely corroborate each other, and low with one impeccably-executed lens.
- It does not score assumption *count* or constraint *completeness* generically — a
  constraints.md with ten well-written assumptions about a single lens still scores low
  here.
- It shares no intermediate sub-score with the verifier or round-1 metrics (per the
  ledger's own note that this signal is genuinely absent from both), so it adds
  independent variance to the suite's aggregate rather than re-weighting an existing
  signal.
- Its penalize-don't-skip floor (constraints.md absent → 0.0; abstract-only → penalty
  multiplier 0.2–0.4) makes it behave consistently with the rest of the suite's stance
  that *unavailability of an assessable input is itself evidence of a thinner artifact*,
  not a reason to abstain from scoring.
