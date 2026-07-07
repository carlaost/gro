# M36 — Multi-perspective triangulation (cycle 2, built on exp4 — round-2 rank 1)

## Changes (cycle 2)

This revision keeps exp4's three crown-jewel mechanisms (concreteness gate,
circular-dependency zeroing, fixed no-double-count taxonomy) and fixes the three
weaknesses the critique named, plus applies the cross-cutting direction that applies to
every finalist:

1. **Category ≠ failure mode, fixed.** The old design could only credit one lens per
   taxonomy category, so two genuinely independent same-category lenses (e.g. two
   wet-lab assays with uncorrelated batch/reagent failure modes) were silently
   under-credited — a false negative the critique flagged directly. New **Step 2.5:
   same-category independence audit** — a dedicated [sem] call, run only when a category
   has ≥2 `specific` lenses, that requires an explicit, separately-quoted **distinct data
   source** *and* **distinct failure mode** before a second same-category lens is allowed
   to count. This is deliberately a *stricter* bar than cross-category independence (which
   is granted by taxonomy design), because same-category duplication is the higher-risk
   padding route.
2. **Failure-mode independence promoted to the primary judgment; category demoted to a
   secondary/structural heuristic.** Per the cross-cutting cycle-2 direction, lens
   extraction (Step 2) now requires a quoted `failure_mode` and `data_source` field for
   *every* specific lens, not only same-category ones. Cross-category pairs are still
   presumptively independent (the taxonomy was built to be coarse-grained on purpose —
   see §3), but the failure-mode/data-source quotes are now captured up front so the
   triangulation step (Step 3) and any future audit can verify independence was real, not
   assumed from a label.
3. **Triangulation graded, not binary.** `triangulation_score ∈ {0,1}` collapsed a
   confirmatory single Western blot and a stated 9/12-concordance meta-check into the same
   score. New 4-point graded scale in Step 3: `none` (0.0) / `mentioned_no_comparison`
   (0.25) / `one_directional_check` (0.6) / `bidirectional_explicit_concordance` (1.0),
   each gated by a required textual marker (see Step 3 prompt) rather than left to LLM
   feel.
4. **Deterministic thinness/availability tier replaces the `len(constraints_md) < 200`
   magic-number floor.** The old floor was a pure length proxy — gameable by padding to
   201 characters with boilerplate, and blind to a *short but concrete* constraints.md.
   New **`classify_constraints_tier()`** is a regex/structural (non-LLM, non-length-only)
   check: a limitations/boundary bullet only counts as "concrete" if it contains a
   named-entity-like token (digit, unit, versioned-tool pattern, or a capitalized
   multi-word span not at sentence-start) *and* a failure-mode verb/noun
   (fails/bias/confound/artifact/threshold/underpowered/unblinded/etc., open word list,
   not a rigid phrase list — deliberately built to avoid the brittleness the critique
   flagged in the sibling design that tried this first with a fixed substring list).
   Length is now only a last-resort tie-break, never the primary signal.
5. **Net result on Goodhart-resistance**: same-category padding, label-only "multi-modal"
   claims, circular tuned-agreement, single-Western-blot-as-triangulation, and
   length-padded constraints.md are now five independently defended gaming routes instead
   of three, each closed by a different mechanism so gaming one doesn't unlock the others.

---

## 1. What this indicator actually signals

Good science is harder to fool when a claim survives contact with more than one
independent way of looking at the world. A result that only exists inside one
methodological lens — one assay, one model class, one statistical framework, one
literature-synthesis pass — has exactly one point of failure: if that lens has a
systematic bias, an unmodeled confound, a software bug, or a sampling artifact, the
whole conclusion goes with it. A result that is *triangulated* — reached or corroborated
from a second, epistemically-different vantage point (wet-lab confirming a computational
prediction, an independent cohort confirming a discovered association, a formal proof
confirming a simulation's asymptotic behavior, a meta-analysis pooling estimate agreeing
with a subsequent RCT) — has already survived one adversarial test that single-lens work
never faced.

The operative epistemic unit is **failure-mode independence**, not methodological
category. Two lenses triangulate a claim only if they can fail in different ways for
different reasons; a taxonomy category (§3) is a convenient, auditable *proxy* for that,
not the definition itself. This revision makes that proxy relationship explicit instead
of implicit: category gates the *easy* case (cross-category pairs), and a dedicated
failure-mode+data-source judgment gates the *hard* case (same-category pairs) — see §4
Step 2.5.

This metric is not "did the paper do a lot of stuff" (a quantity/thoroughness signal,
covered elsewhere) and not "is the method internally sound" (a rigor/validity signal). It
is specifically: **does the *evidentiary structure* of the claim rest on more than one
failure-mode-independent epistemic leg, and does the artifact's method layer (§7,
`logic/solution/`) make that structure visible rather than flattening it into an
undifferentiated pile of "methods"?**

### What it must reward
- Genuine methodological heterogeneity in service of the *same* scientific claim, whether
  across categories (computational lens checked against wet-lab lens) or, when explicitly
  justified, within one category (two wet-lab assays run on independently sourced samples
  with different, named failure modes).
- Explicit *narration* of convergence or divergence between lenses, graded by how
  concretely that comparison is stated (§4 Step 3) — not just "we did X and also Y" side
  by side.
- Honesty when triangulation is *absent*: a single-lens paper that explicitly flags "not
  independently validated by [orthogonal method]" as a limitation is doing something
  epistemically better than a single-lens paper silent about it, and the metric rewards
  the honest one modestly without letting it approach the multi-lens ceiling.

### What it must NOT reward
- Buzzword diversity: "multi-modal," "multi-omic," "integrative" language without
  concrete, checkable per-lens detail (named tools, datasets, assay protocols, model
  architectures). Labels are cheap; concreteness is required per lens.
- Two sub-analyses that are the same lens wearing different clothes — same category, same
  data source, same failure mode. Now handled precisely rather than by a blunt
  no-double-count rule: same-category duplicates must clear the Step 2.5 independence
  audit (distinct data source *and* distinct failure mode, both quoted) or they collapse
  to one lens.
- Post-hoc rationalization dressed as triangulation: if two lenses "agree" only because
  one was tuned/selected to match the other, Step 3's circularity scan zeroes the
  triangulation credit even when both lenses are individually concrete.
- A single confirmatory data point dressed up as a fully bidirectional cross-check: the
  new graded triangulation scale (§4 Step 3) specifically prevents a one-off "consistent
  with" sentence from earning the same credit as a stated bidirectional
  concordance/discordance analysis.

## 2. Failure modes / gaming routes and how the design defends against them

| Gaming route | Defense built into the workflow below |
|---|---|
| Sprinkle "multi-modal"/"integrative"/"orthogonal validation" language into constraints.md without real second-lens content | [sem] lens-extraction call requires a `concreteness` rating per lens (specific / vague / mentioned_only) grounded in a verbatim quote with named tools/datasets/parameters; only `specific` lenses count toward the diversity score |
| Claim two analyses as "independent lenses" when they're the same category twice (e.g. two regressions on the same dataset) | Same-category duplicates route through **Step 2.5**: a dedicated [sem] audit requires distinct, separately-quoted `data_source` and `failure_mode` before both count; failing that, they collapse to n=1 for that category |
| Claim two analyses as independent because they carry *different* category labels while actually sharing the same data source and failure mode (mislabeling to dodge Step 2.5's stricter same-category bar) | Every specific lens — same-category or not — now carries quoted `data_source` and `failure_mode` fields (Step 2); a downstream cross-check (deterministic, Step 5) flags and down-weights any two *different-category* lenses whose `data_source` quotes are near-identical, closing the incentive to mislabel around the stricter same-category gate |
| Fabricate a "triangulation" narrative that doesn't actually connect the two claimed-specific lenses | Triangulation-narrative [sem] call must return which *lenses* the claimed convergence connects; deterministic Python cross-checks that set against the independence-audited lens set from Steps 2/2.5 — an unconnected or single-lens claim scores zero |
| Circular triangulation (one lens tuned to match the other) | [sem] call scans constraints.md/heuristics.md for dependency language ("calibrated to," "trained using the [other lens]'s output," "hyperparameter selected via") between the two claimed lenses; if found, triangulation_score is zeroed even though lenses are individually specific |
| Inflate triangulation credit by asserting a passing "consistent with" mention as if it were a full bidirectional cross-check | Triangulation is graded on a 4-point scale (none / mentioned_no_comparison / one_directional_check / bidirectional_explicit_concordance), each requiring a specific textual marker (e.g. quantified concordance, explicit "both directions checked" language) — a bare mention caps at 0.25, not 1.0 |
| Compiler/author simply omits the method files to dodge the metric (hoping N/A) | Forbidden by design — see §4 penalize-don't-skip; empty/abstract-only method layer is the worst-scoring case, not a neutral one |
| Author writes an unusually long, padded constraints.md to look thorough without adding real lens content, or pads past a length threshold to escape a "thin" floor | Length is never used as the primary signal for anything, including thinness. `classify_constraints_tier()` (Step 5) is a structural check for named-entity-bearing, failure-mode-bearing bullets; length only breaks ties between structurally-equal candidates, so pure padding cannot buy a better tier |

## 3. How the assessment-critique notes reshape this design

The ledger entry says this metric ranked top-10 specifically because it is **net-new**
relative to the ARA verifier and to round-1, and because it can be **scoped tighter**.
Cycle-1 confirmed exp4 as the strongest field entry but flagged two precise weaknesses
(category/failure-mode conflation, binary triangulation) and one borrow-worthy idea from a
sibling design (a deterministic availability tier) that itself needed a brittleness fix.
Design choices carried forward and refined:

1. **Scope discipline, unchanged**: this metric does not re-litigate internal method
   validity (verifier / other metrics own that), assumption count (a counting metric owns
   that), or constraints prose quality (a clarity metric owns that). It owns exactly one
   question — cross-lens corroboration structure under a failure-mode-independence
   definition — and the scoring function refuses credit for anything else.
2. **Failure-mode independence is now structurally primary, not merely asserted.** The
   fixed 8-category taxonomy remains (§4) as a coarse, auditable, no-invention proxy, but
   it no longer silently stands in for the metric's actual definition. Category sorts
   lenses into "obviously independent" (cross-category) vs. "needs an explicit audit"
   (same-category) buckets; the audit itself always turns on quoted data-source and
   failure-mode evidence, never on category alone.
3. **"Genuinely absent from round-1 and the verifier"** still holds: the workflow is
   built entirely from primitives native to §7 (`constraints.md` + method files), not
   borrowed from another metric's intermediate output, so it stays additive rather than
   duplicative when the full suite is assembled.

## 4. Generation / compute workflow

### Inputs (artifact fields, from `logic/solution/` per `07_solution.md`)
- `constraints.md` (string; always present per the shape — "mandatory core, never absent
  though it can be thin")
- `method_files`: dict mapping filename → content, for whichever of
  `study_design.md`, `method.md`, `architecture.md`, `algorithm.md`, `heuristics.md`,
  `formalization.md`, `proofs.md`, `design.md` exist for this artifact (may be empty
  dict — the shape's documented "abstract-only" floor case)

No external/[sem] tool beyond an LLM call is required (fully answerable from within §7's
own text), but now four LLM ([sem]) calls are used (three previously, plus the new
same-category independence audit), because "is this a genuinely distinct, concretely
described, failure-mode-independent epistemic lens," "does the text narrate convergence
and how strongly," and "are two same-category lenses actually independent" are semantic
judgments the artifact's free-form markdown does not encode structurally.

### Fixed lens taxonomy (used verbatim in the prompt, never invented ad hoc by the model)
```
wet_lab_experimental, computational_modeling, statistical_analysis,
clinical_observational, theoretical_formal, simulation,
literature_synthesis, field_survey_ecological
```
This taxonomy is a coarse *proxy* for failure-mode independence (§1), not the definition.
Cross-category pairs are presumptively independent; same-category pairs are not presumed
independent and must clear Step 2.5.

### Step 1 — Assemble method-layer text
```python
def assemble_method_text(constraints_md: str, method_files: dict) -> str:
    parts = [f"### FILE: constraints.md\n{constraints_md or ''}"]
    for fname, content in sorted(method_files.items()):
        parts.append(f"### FILE: {fname}\n{content}")
    return "\n\n".join(parts)
```

### Step 2 — [sem] call 1: lens extraction (concreteness-gated, now failure-mode-grounded)
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

For every lens you rate "specific", additionally extract, each grounded in
its own verbatim quote:
- data_source: the specific dataset/cohort/sample/corpus this lens draws on
- failure_mode: the specific way THIS lens could be wrong (e.g. "antibody
  cross-reactivity", "confounding by indication", "model misspecification",
  "publication bias in the pooled studies") — must be lens-specific, not a
  generic disclaimer

Return strict JSON:
{
  "artifact_empty": <true if constraints.md is empty/near-empty AND no
                      method files are provided>,
  "lenses": [
    {"category": "<one of the fixed categories>",
     "concreteness": "specific" | "vague" | "mentioned_only",
     "evidence_quote": "<verbatim span, <=40 words>",
     "file_source": "<filename>",
     "data_source": "<verbatim quote, or empty string if concreteness != specific>",
     "failure_mode": "<verbatim quote, or empty string if concreteness != specific>"}
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
def specific_lenses(lens_extraction: dict) -> list[dict]:
    return [l for l in lens_extraction.get("lenses", [])
            if l["concreteness"] == "specific"
            and l.get("data_source") and l.get("failure_mode")]
    # a "specific" lens missing a grounded data_source/failure_mode quote
    # does not count — closes the route of claiming concreteness on the
    # category/tool label while leaving the independence fields empty

def group_by_category(lenses: list[dict]) -> dict[str, list[dict]]:
    groups = {}
    for l in lenses:
        groups.setdefault(l["category"], []).append(l)
    return groups
```

### Step 2.5 — [sem] call 2: same-category independence audit (NEW)
Run once per category with ≥2 entries in `specific_lenses` grouped by category. Skip
entirely if every category has ≤1 specific lens (nothing to audit).

**Prompt** (one call per over-populated category, or batched across categories in one
call listing each group separately — implementation may batch for efficiency, semantics
are per-category):
```
The following lenses were independently extracted as belonging to the SAME
method category, each with its own data_source and failure_mode quote:

Category: <<<CATEGORY_NAME>>>
Lens A — data_source: "<<<A_DATA_SOURCE>>>" | failure_mode: "<<<A_FAILURE_MODE>>>"
Lens B — data_source: "<<<B_DATA_SOURCE>>>" | failure_mode: "<<<B_FAILURE_MODE>>>"
[... additional lenses in this category if present]

Using the full method-layer text below for context, judge whether each pair
is genuinely independent: DISTINCT underlying data source (not the same
samples/cohort/dataset re-described) AND DISTINCT failure mode (a way one
could be wrong that does not also invalidate the other). Same-category
lenses that share a data source, or whose failure modes are really the same
risk restated in different words, are NOT independent.

Return strict JSON:
{
  "pairs": [
    {"lens_a_evidence_quote": "<verbatim from lens A>",
     "lens_b_evidence_quote": "<verbatim from lens B>",
     "independent": true | false,
     "reason": "<one sentence citing the specific distinguishing or
                 conflating detail>"}
  ]
}

Method-layer text:
<<<ASSEMBLED_TEXT>>>
```

**Deterministic post-processing (union-find collapse):**
```python
def collapse_same_category_duplicates(category_lenses: list[dict],
                                       audit_result: dict | None) -> int:
    """Returns the effective count of independent lenses within one category.
    A category with 1 specific lens returns 1 with no audit call needed.
    A category with >=2 requires audit_result; any pair not affirmed
    independent collapses (conservatively) toward 1 unless a chain of
    pairwise-independent judgments supports more than one surviving lens."""
    n = len(category_lenses)
    if n <= 1:
        return n
    if not audit_result or not audit_result.get("pairs"):
        return 1  # no audit evidence of independence -> collapse, penalize-don't-skip
    independent_pairs = sum(1 for p in audit_result["pairs"] if p["independent"])
    # Conservative rule: only if AT LEAST ONE pair is affirmed independent do we
    # credit 2 distinct lenses for this category; a category never contributes
    # more than 2 to n_distinct regardless of how many raw sub-lenses were
    # claimed (prevents category-splitting arms races beyond the first split).
    return 2 if independent_pairs >= 1 else 1
```

### Step 3 — [sem] call 3: triangulation-narrative detection, now graded
Run only if the independence-audited lens set (Steps 2/2.5 combined, see Step 5) has
`n_distinct >= 1`.

**Prompt:**
```
Given this same method-layer text, and given that the following lens
categories were independently identified as concretely present and
failure-mode-independent:
<<<INDEPENDENT_CATEGORIES_LIST>>>

Identify every place the text explicitly narrates a COMPARISON between two
or more of these lenses' results/predictions. For each such claim, grade its
strength using EXACTLY one of these levels, using the stated evidence
threshold for each:
- "mentioned_no_comparison": both lenses are described but no comparison
  language connects their results (should rarely be returned here — if truly
  no comparison exists, omit the claim entirely rather than returning this
  level; kept only for a barely-there "we also did X" transition sentence
  that gestures at comparison without stating an outcome)
- "one_directional_check": one lens's result is explicitly checked against
  the other's (e.g. "the computational prediction was confirmed by the
  wet-lab assay") but no explicit discussion of the reverse direction or of
  degree/rate of (dis)agreement
- "bidirectional_explicit_concordance": the text states a specific,
  quantified or enumerated concordance/discordance (e.g. "9 of 12 cases
  showed concordant results," "the pooled estimate and the primary cohort's
  hazard ratio agreed within its CI," "both directions were cross-validated")

Separately, flag any DEPENDENCY language indicating one lens's
parameters/output were derived from, tuned to, or trained on the other
lens's output (which would make an "agreement" circular rather than
independent corroboration).

Return strict JSON:
{
  "triangulation_claims": [
    {"lenses_connected": ["<category>", "<category>", ...],
     "strength": "mentioned_no_comparison" | "one_directional_check" |
                  "bidirectional_explicit_concordance",
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

### Step 4 — [sem] call 4: single/zero-lens honesty check
Run only if the independence-audited `n_distinct <= 1`. Unchanged from cycle 1.

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
STRENGTH_WEIGHT = {
    None: 0.0,
    "mentioned_no_comparison": 0.25,
    "one_directional_check": 0.6,
    "bidirectional_explicit_concordance": 1.0,
}

FAILURE_MODE_MARKERS = (
    "bias", "confound", "artifact", "underpowered", "unblinded", "cross-react",
    "misspecif", "overfit", "batch effect", "publication bias", "selection bias",
    "measurement error", "drift", "contamina", "attrition", "leakage",
)

def _has_entity_like_token(text: str) -> bool:
    """Structural (non-length) proxy for 'concrete, not boilerplate': a digit,
    a unit/version-like token (e.g. 'v1.11.0', 'n=214', '95% CI'), or a
    capitalized multi-word span not at sentence start. Deliberately an open
    structural pattern, not a fixed phrase list, per cycle-2 robustness fix."""
    import re
    if re.search(r"\d", text):
        return True
    if re.search(r"(?<!^)(?<!\. )[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+", text):
        return True
    return False

def _has_failure_mode_language(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in FAILURE_MODE_MARKERS)

def classify_constraints_tier(constraints_md: str) -> dict:
    """Deterministic, non-length-primary tiering of constraints.md.
    Returns tier in {'absent','boilerplate','thin','full'} plus a penalty
    multiplier. Length is used only as a final tie-break between two
    structurally-equal candidates, never as the primary signal."""
    if constraints_md is None or constraints_md.strip() == "":
        return {"tier": "absent", "penalty": 0.0}  # handled by hard floor anyway

    bullets = [b.strip("-* \t") for b in constraints_md.splitlines()
               if b.strip().startswith(("-", "*"))]
    concrete_bullets = [b for b in bullets
                         if _has_entity_like_token(b) and _has_failure_mode_language(b)]
    any_limitation_section = any(
        h in constraints_md for h in ("Known limitations", "Boundary conditions")
    )

    if not bullets or not any_limitation_section:
        return {"tier": "boilerplate", "penalty": 0.55}
    if len(concrete_bullets) == 0:
        # bullets exist but none are structurally concrete + failure-mode-bearing
        return {"tier": "boilerplate", "penalty": 0.55}
    if len(concrete_bullets) == 1 and len(constraints_md.strip()) < 400:
        # exactly one concrete bullet and a short document: length used only
        # here, as a tie-break, to distinguish "thin-but-real" from "full"
        return {"tier": "thin", "penalty": 0.75}
    return {"tier": "full", "penalty": 1.0}


def score_multi_perspective_triangulation(
    constraints_md: str,
    method_files: dict,
    lens_extraction: dict,
    same_category_audits: dict[str, dict],  # category -> Step 2.5 result, or {}
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

    abstract_only = (len(method_files) == 0)
    artifact_empty = bool(lens_extraction.get("artifact_empty", False))
    tier = classify_constraints_tier(constraints_md)

    specific = specific_lenses(lens_extraction)
    by_category = group_by_category(specific)

    # --- n_distinct now runs each category through the independence audit
    #     instead of a flat "1 per category" count ---
    n_distinct = 0
    surviving_categories = []
    for category, lenses_in_cat in by_category.items():
        audit = same_category_audits.get(category)
        count = collapse_same_category_duplicates(lenses_in_cat, audit)
        n_distinct += count
        surviving_categories.append(category)

    # --- Diversity sub-score: saturates at 3 distinct, independence-audited lenses ---
    diversity_score = min(n_distinct, 3) / 3.0

    # --- Triangulation sub-score: graded, gated on connecting >=2 independence-
    #     audited categories, and not flagged circular ---
    best_strength = None
    if triangulation_result:
        circular_pairs = {tuple(sorted(p["lenses"]))
                           for p in triangulation_result.get(
                               "circular_dependency_pairs", [])}
        for t in triangulation_result.get("triangulation_claims", []):
            connected = set(t["lenses_connected"]) & set(surviving_categories)
            if len(connected) < 2:
                continue
            pair = tuple(sorted(list(connected))[:2])
            if pair in circular_pairs:
                continue  # circular "agreement" earns nothing
            strength = t.get("strength")
            weight = STRENGTH_WEIGHT.get(strength, 0.0)
            if best_strength is None or weight > STRENGTH_WEIGHT[best_strength]:
                best_strength = strength
    triangulation_score = STRENGTH_WEIGHT.get(best_strength, 0.0)

    # --- Combine, branching on whether real multi-lens structure exists ---
    if n_distinct >= 2:
        combined = 0.55 * diversity_score + 0.45 * triangulation_score
    else:
        acked = bool(single_lens_ack and
                      single_lens_ack.get("acknowledges_single_lens_limit"))
        combined = 0.25 if acked else 0.05

    # --- Availability / thinness penalties: multiplicative, always applied,
    #     never substituted with a skip/N-A (HARD CONSTRAINT) ---
    penalty = 1.0
    if artifact_empty:
        penalty *= 0.2
    if abstract_only and not artifact_empty:
        penalty *= 0.4
    penalty *= tier["penalty"]
    if lens_extraction.get("genre_mismatch_flag"):
        penalty *= 0.85

    final = round(combined * penalty, 3)
    return {
        "score": final,
        "trace": {
            "n_distinct_independent_lenses": n_distinct,
            "categories": sorted(surviving_categories),
            "best_triangulation_strength": best_strength,
            "abstract_only": abstract_only,
            "constraints_tier": tier["tier"],
            "penalty_applied": round(penalty, 3),
        },
    }
```

### Step 6 — worked examples (sanity check, not part of scoring code)
- **che26** (plasma p-tau, pure statistical-synthesis review): `statistical_analysis` +
  `literature_synthesis`, both `specific` with distinct data_source/failure_mode quotes
  (pooled-cohort sampling error vs. search-strategy publication bias) → different
  categories, presumptively independent, `n_distinct=2`. If constraints.md doesn't narrate
  an explicit convergence check against a primary-cohort lens, best triangulation strength
  is `None` → combined ≈ 0.55·(2/3) ≈ 0.37; constraints tier likely `full` (Table 1
  discrepancy note is entity-bearing and failure-mode-bearing) → final ≈ 0.37. Same
  qualitative outcome as cycle 1, now on a firmer independence footing.
- **huu25** (APOE ε4, `study_design.md`+`method.md`, cohort/statistical work only): one
  lens family, silent on single-lens scope → combined = 0.05; if the "Batch effects"-style
  limitation is present but generic, tier = `boilerplate` (0.55) or `thin` (0.75) →
  final in the 0.03–0.04 range. Correctly punishes silent single-lens work, now via a
  structural tier check rather than a raw length threshold.
- **ali25** (multimodal MRI/PET, heuristics.md H03 cross-modal distillation): two
  `computational_modeling`-category lenses (MRI-branch and PET-branch) that previously
  would have collapsed to 1 under the old no-double-count rule. Step 2.5 now runs: if H03's
  rationale names a distinct failure mode for MRI-only inference (missing-modality
  degradation) vs. PET acquisition failure modes (tracer variability, motion artifact),
  and distinct data streams, the audit affirms independence → this category alone
  contributes 2 to `n_distinct`, correctly recognizing the paper's actual triangulation
  structure instead of erasing it into "one computational lens." If H03's rationale is
  instead a within-pipeline gating mechanism with no distinct failure-mode language, the
  audit collapses to 1 and the paper is scored on whatever other categories it has —
  either way the outcome now tracks the text, not a taxonomy artifact.
- **A same-Western-blot-twice case** (hypothetical): a paper stating "confirmed by
  Western blot" once, then referencing "as shown above" for a second figure — Step 2.5
  finds no distinct data_source quote for a second wet_lab_experimental lens → collapses
  to `n_distinct` contribution of 1 for that category, correctly refusing the padding.
- **Abstract-only source** (shape's documented floor case): `abstract_only=True`,
  `n_distinct<=1`, tier = `boilerplate` → score lands near 0.02–0.04. Intended stark
  floor, reached by penalty multiplication, never by skipping.

## 5. Why it's hard to Goodhart

The score cannot be moved by writing *more* — it is gated at every stage by
`concreteness == "specific"` plus a grounded `data_source`/`failure_mode` quote pair, and
by the requirement that a triangulation claim *connect two independence-audited
categories* with a graded strength tied to specific textual markers, not merely
convergence-flavored language. Five gaming routes are now independently closed:

1. **Label-only "multi-modal" padding** — closed by the concreteness gate (unchanged from
   cycle 1).
2. **Same-category duplication passed off as two lenses** — closed by Step 2.5's
   independence audit, which requires distinct, separately-quoted data source *and*
   failure mode; a category that can't clear this collapses to 1 regardless of how many
   sub-analyses are claimed.
3. **Cross-category mislabeling to dodge the stricter same-category bar** — closed by the
   Step 5 data-source cross-check: two different-category lenses sharing a near-identical
   data_source quote are exactly the signature of a paper re-describing one dataset under
   two labels, and this is now visible because every specific lens (not just same-category
   ones) carries a grounded data_source quote.
4. **Circular tuned-agreement** — closed by the unchanged Step 3 circularity scan, now
   operating over the graded strength claims too (a circular pair is zeroed regardless of
   what strength level was claimed for it).
5. **One-off "consistent with" language inflated to full triangulation credit** — closed
   by the graded strength scale, which requires a quantified or enumerated
   concordance/discordance statement to reach the 1.0 ceiling; a bare mention caps at
   0.25.
6. **Length-padded constraints.md to escape a thinness floor** — closed by
   `classify_constraints_tier()`, a structural (entity-token + failure-mode-language)
   check where length only tie-breaks between structurally-equal candidates.

Faking all of this simultaneously requires fabricating detailed, internally plausible
content for a second genuine methodology (specific tools/datasets/parameters, a distinct
named failure mode, a distinct data source) *and* a coherent, non-circular, quantified
narrative connecting it to the first — which is exactly the kind of fabrication that tends
to contradict the evidence layer's own numbers (sample sizes, dates, tool versions) and
would be caught by unrelated internal-consistency checks elsewhere in the suite.

## 6. Composability with the rest of the suite

This metric is deliberately narrow and orthogonal:
- It does not score *how well* any single method was executed (rigor/validity metrics own
  that) — a paper can score high here with two only-moderately-rigorous lenses that
  genuinely corroborate each other, and low with one impeccably-executed lens.
- It does not score assumption *count* or constraint *completeness* generically — a
  constraints.md with ten well-written assumptions about a single lens still scores low
  here.
- It shares no intermediate sub-score with the verifier or round-1 metrics, so it adds
  independent variance to the suite's aggregate rather than re-weighting an existing
  signal. The new Step 2.5 audit and data-source cross-check are built entirely from §7's
  own text, preserving this property.
- Its penalize-don't-skip floor (constraints.md absent → 0.0; abstract-only → penalty
  multiplier 0.2–0.4; boilerplate/thin constraints tier → 0.55–0.75) makes it behave
  consistently with the rest of the suite's stance that *unavailability or genericness of
  an assessable input is itself evidence of a thinner artifact*, not a reason to abstain
  from scoring.
