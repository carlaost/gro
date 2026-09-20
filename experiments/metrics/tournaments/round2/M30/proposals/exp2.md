# M30 — Assumption realism & limitation validity — Expansion (expander 2)

## 1. What this metric is actually rewarding

Round-1 metric 07 (concreteness) asks: *is each stated assumption/limitation specific rather than
vague?* Verifier D3 (explicitness) asks: *are assumptions/limitations stated at all, with IDs, rather
than left implicit?* Both are **form** checks — they pass a paper that writes crisp, well-labeled, but
dishonest or empty boilerplate. M30 is the **content-truth** check that sits on top of both:

1. **Assumption realism/fairness** — for each declared assumption `Ai`, is it something the method
   actually needs and that could plausibly be false in this domain (a real constraint), or is it a
   *dreamcase* convenience — an idealization stated as if trivial that quietly assumes away the hardest
   part of the problem (no confounding, no measurement error, representative sampling, i.i.d. draws,
   correct model specification) with no acknowledgment of how often/how badly it fails in this kind of
   study?
2. **Limitation validity** — does each declared limitation add a **genuinely new condition** on how far
   the results generalize, or is it a restatement of a boundary condition/assumption already declared
   elsewhere, or a generic hedge ("further work is needed to confirm these findings in larger cohorts")
   that would be equally true of almost any paper in the field and therefore carries ~0 bits of
   information?
3. **Coverage** — cross-referenced against the method file(s), are there well-known, field-standard
   caveats attached to the design choices actually used (single-center, retrospective, small N,
   unvalidated instrument, no control arm, convenience sample, post-hoc subgroup, self-report,
   cross-sectional) that go **unmentioned** in both `Assumptions` and `Known limitations`? A method
   section that visibly uses a convenience sample but never states that as either an assumption or a
   limitation is failing exactly the thing this metric exists to catch.

## 2. What it must reward vs. must not

**Reward:**
- Assumptions that are load-bearing (the method breaks or the conclusion weakens if false) and stated
  plainly as assumptions rather than smuggled into the method's phrasing.
- Assumptions accompanied by any signal of their own plausibility (frequency in the field, a citation,
  a sensitivity check, or at minimum an acknowledgment that the assumption is strong).
- Limitations that name a specific mechanism and a specific direction/magnitude of likely bias (e.g.
  "self-report outcome measurement likely inflates the treatment effect via demand characteristics")
  over generic hedges.
- Internal consistency: every design choice with a well-known field caveat is addressed *somewhere* in
  constraints.md (as boundary condition, assumption, or limitation — the metric does not care which
  bucket, only that the risk surfaces).

**Must not reward:**
- Padding: many assumption/limitation bullets that are near-duplicates or restate the same idea in
  different words (a compiler or author gaming bullet *count*).
- Uncontroversial filler assumptions ("we assume the statistical software computed correctly") used to
  inflate the appearance of rigor without adding real constraint information.
- Boilerplate limitations ("sample size may limit generalizability," "further research is warranted")
  that are template-fillable regardless of what the paper actually did.
- Restating a boundary condition verbatim as a "limitation" to look like two things when it's one.
- Confident-sounding realism language ("this assumption is standard in the field") used as a substitute
  for actually being realistic — the workflow below treats unsupported *assertions* of plausibility as
  weaker evidence than a cited or field-corroborated one.

## 3. Failure modes / gaming routes and how the design closes them

| Gaming route | Countermeasure in this workflow |
|---|---|
| Pad with many trivial/uncontroversial assumptions to look thorough | Per-assumption **triviality/load-bearing** classification; trivial assumptions get near-zero weight regardless of how many there are; aggregate uses a capped, diminishing-returns sum, not a raw count |
| Pad with near-duplicate limitation bullets | Pairwise semantic-dedup pass before scoring; duplicates collapse to one scored instance and count against the "distinctiveness" sub-score |
| State only the easy/defensible assumptions, omit the load-bearing shaky one | Independent **omission scan** over the method file(s) for field-standard caveat triggers, cross-checked against constraints.md — a used-but-unsurfaced risk is a direct penalty term, found without relying on what the paper chose to disclose |
| Generic boilerplate limitations that are true of any paper in the genre | Boilerplate-phrase classifier (semantic, not keyword-matched only) scores generic hedges near zero informativeness; a limitations section that is *entirely* boilerplate scores like a missing section |
| Restate boundary conditions as limitations for double credit | Cross-bullet dedup runs *across* the three buckets (boundary conditions / assumptions / limitations), not just within one |
| Leave constraints.md thin/near-empty and hope the metric can't tell without other metrics catching it | Explicit availability/thinness gate (§5) that scores down rather than skipping, per the hard constraint below |
| Assert plausibility without support ("this is a standard assumption") to farm a good realism score | The realism classifier requires the judge to independently assess plausibility from domain knowledge, not defer to the paper's own framing; unsupported self-assessment is capped below field-corroborated plausibility |

## 4. Availability is part of the score (penalize, never skip)

`constraints.md` is mandatory in the artifact shape and is never truly absent — but it can be a bare
stub, and the `Assumptions` / `Known limitations` subsections can each independently be empty. This
metric treats emptiness/thinness as a **scored fact**, not a reason to abstain:

- `constraints.md` file missing from the artifact entirely → **floor score** (treated as the worst
  possible realism/validity outcome, not N/A), plus a flag that the artifact itself is defective at the
  structural level (this should also fail Seal Level 1, but M30 does not rely on that — it scores the
  absence directly).
- `Assumptions` section present but empty, or `Known limitations` section present but empty → each
  contributes its sub-score as **0**, not excluded from the denominator. An artifact with zero stated
  assumptions is not "assumption-free," it is failing to disclose them, and is scored accordingly.
- Abstract-only source artifacts (per the shape doc's "stark, easily-detected floor case") legitimately
  have nothing to score beyond whatever the abstract itself states — this workflow still runs the same
  pipeline over whatever exists (possibly zero bullets), which naturally produces a low-but-defined
  score rather than a skip. The metric does not special-case abstract-only sources into an exemption.

## 5. Generation / compute workflow

### 5.0 Inputs (artifact fields, per `07_solution.md`)

```python
# Parsed from logic/solution/constraints.md (+ sibling method files) per the documented shape.
constraints = {
    "file_present": bool,                 # does constraints.md exist at all
    "boundary_conditions": [str, ...],     # bullets, [] if section missing/empty
    "assumptions": [{"id": "A1", "text": str}, ...],   # [] if missing/empty
    "limitations": [{"name": str, "text": str}, ...],  # [] if missing/empty
    "data_quality_caveats": [str, ...],    # compiler-added subsection, [] if absent
}
method_files = [
    {"filename": "study_design.md", "sections": {"## Cohort": str, ...}},
    # 0..N sibling files, per shape doc's genre-dependent list
]
evidence_tables_flags = [str, ...]  # optional: internal-consistency notes already surfaced
                                     # elsewhere in evidence/ (e.g. che26's Table1/caption
                                     # mismatch); OPTIONAL cross-layer input — if unavailable,
                                     # step 5.4's caveat-reconciliation check scores 0 for that
                                     # sub-term rather than being skipped (still penalized, not N/A).
```

### 5.1 Parse + dedup pass (deterministic)

1. Extract the three bullet lists from `constraints.md` as-is.
2. Run pairwise semantic-similarity dedup **across all three buckets combined** (boundary conditions,
   assumptions, limitations) — any pair above a similarity threshold is a duplicate; keep the more
   specific of the pair as the scored instance, mark the other as `redundant` (contributes to the
   distinctiveness penalty, not to real content).
   - [sem] call: `dedup_pairs(bullets: list[str]) -> list[(i, j, is_duplicate: bool)]`. Prompt: *"Do
     bullets A and B state the same underlying constraint/condition, even if worded differently? Answer
     true/false only."* This can be done with embedding cosine similarity + an LLM tie-breaker near the
     threshold; either is acceptable, the contract is the boolean output per pair.

### 5.2 Per-assumption realism classification [sem]

For each surviving (non-duplicate) assumption `Ai`:

**Prompt (LLM judge, structured JSON output):**
```
You are assessing one stated methodological assumption from a research paper's constraints section.

Paper domain/method context: {method_files rendered as markdown, truncated to relevant sections}
Assumption: "{assumption.text}"

Answer as JSON:
{
  "load_bearing": true|false,        // would the method's conclusions materially change if this
                                      // assumption were false, given the method described above?
  "plausibility": "well_supported" | "plausible_unverified" | "convenient_but_shaky" | "implausible",
  "support_given": true|false,       // does the paper offer any citation, rationale, or sensitivity
                                      // check for why this assumption should hold, beyond asserting it?
  "is_dreamcase": true|false,        // does this assumption erase the central difficulty of the
                                      // problem (e.g. "no confounding," "no measurement error",
                                      // "representative sample") without qualification?
  "rationale": "<= 2 sentences"
}
```

**Deterministic mapping to a per-assumption score `s(Ai) ∈ [0,1]`:**
```python
PLAUSIBILITY_WEIGHT = {
    "well_supported": 1.0,
    "plausible_unverified": 0.7,
    "convenient_but_shaky": 0.3,
    "implausible": 0.0,
}

def score_assumption(j: dict) -> float:
    base = PLAUSIBILITY_WEIGHT[j["plausibility"]]
    if j["is_dreamcase"] and not j["support_given"]:
        base *= 0.3          # unqualified dreamcase assumption is heavily punished
    if not j["load_bearing"]:
        base *= 0.4          # trivial/non-load-bearing assumptions can't carry much score
                              # (kills the "pad with uncontroversial assumptions" gaming route)
    if j["support_given"]:
        base = min(1.0, base + 0.15)   # small bonus for any offered justification
    return base
```

### 5.3 Per-limitation validity classification [sem]

For each surviving (non-duplicate) limitation:

**Prompt (LLM judge, structured JSON output):**
```
You are assessing one stated "known limitation" from a research paper, given the paper's already-
declared boundary conditions and assumptions (so you can detect restatement).

Boundary conditions: {list}
Assumptions: {list}
Limitation under review: "{limitation.text}"

Answer as JSON:
{
  "restates_existing": true|false,   // does this just re-say a boundary condition/assumption
                                      // already listed above, rather than adding new information?
  "generic_boilerplate": true|false, // is this a template-fillable hedge that would be equally
                                      // true of most papers in this genre regardless of what was
                                      // actually done (e.g. "larger studies are needed")?
  "specifies_mechanism": true|false, // does it name a specific causal mechanism for the limitation?
  "specifies_direction": true|false, // does it state which direction/magnitude of bias results?
  "rationale": "<= 2 sentences"
}
```

**Deterministic mapping:**
```python
def score_limitation(j: dict) -> float:
    if j["restates_existing"] or j["generic_boilerplate"]:
        return 0.05   # near-zero, not zero: a restated/boilerplate bullet is still a bullet,
                       # but carries essentially no informational content
    score = 0.5
    if j["specifies_mechanism"]:
        score += 0.3
    if j["specifies_direction"]:
        score += 0.2
    return min(1.0, score)
```

### 5.4 Omission scan — unsurfaced field-standard caveats [sem]

1. Scan `method_files` (all sections) for design-choice triggers with well-known standard caveats:
   single-center / single-cohort, retrospective, small-N, unvalidated instrument, no control/comparator
   arm, convenience/self-selected sample, post-hoc subgroup analysis, self-report outcome, cross-
   sectional design, industry funding/COI-adjacent design choices, missing-data handling without
   sensitivity analysis.
   - [sem] call: `scan_design_risks(method_files_text: str) -> list[{"trigger": str, "evidence_quote": str}]`.
     Prompt: *"List design choices in this Methods text that carry a well-known, field-standard
     methodological caveat (e.g. single-center, retrospective, small N, self-report, no control arm,
     post-hoc subgroup, unvalidated instrument). For each, quote the exact sentence that reveals the
     choice."*
2. [sem] call: `is_surfaced(trigger: str, constraints_bullets: list[str]) -> bool` — *"Does any of these
   boundary-condition/assumption/limitation bullets address the caveat associated with '{trigger}'?"*
3. Also reconcile against `evidence_tables_flags` if available (per shape doc: numbers that don't
   reconcile between a table and its caption should be flagged in constraints.md's "Additional caveats"
   subsection): for each externally-known internal-inconsistency flag, check `data_quality_caveats` for
   a matching entry.
4. Every triggered-but-unsurfaced risk is a fixed penalty (see §5.5). If `evidence_tables_flags` is
   unavailable, that specific check contributes 0 (its own worst case), not a skip — consistent with
   penalize-don't-skip.

### 5.5 Aggregate score (final scoring function)

```python
def compute_m30(constraints: dict, method_files: list, evidence_tables_flags: list | None,
                 llm_judge) -> dict:
    """
    Returns {"score": float in [0,100], "components": {...}, "flags": [...]}.
    llm_judge exposes: dedup_pairs, judge_assumption, judge_limitation, scan_design_risks, is_surfaced.
    """
    flags = []

    # --- Hard floor: artifact structurally missing ---
    if not constraints.get("file_present", False):
        return {"score": 0.0, "components": {}, "flags": ["constraints.md absent — structural floor"]}

    boundary = constraints.get("boundary_conditions", [])
    assumptions = constraints.get("assumptions", [])
    limitations = constraints.get("limitations", [])
    caveats = constraints.get("data_quality_caveats", [])

    all_bullets = (
        [("boundary", b) for b in boundary]
        + [("assumption", a["text"]) for a in assumptions]
        + [("limitation", l["text"]) for l in limitations]
    )

    # --- 5.1 dedup across all buckets ---
    dup_pairs = llm_judge.dedup_pairs([t for _, t in all_bullets]) if len(all_bullets) > 1 else []
    redundant_idx = {j for (i, j, is_dup) in dup_pairs if is_dup}  # keep i, drop j
    kept = [b for idx, b in enumerate(all_bullets) if idx not in redundant_idx]
    kept_assumptions = [a for a in assumptions if ("assumption", a["text"]) in kept]
    kept_limitations = [l for l in limitations if ("limitation", l["text"]) in kept]

    n_redundant = len(redundant_idx)
    if n_redundant:
        flags.append(f"{n_redundant} bullet(s) redundant across boundary/assumption/limitation buckets")

    # --- Availability gate (penalize, never skip) ---
    # An artifact with zero assumptions AND zero limitations is scored at its floor for those
    # components, not excluded from the metric.
    availability_penalty = 0.0
    if len(assumptions) == 0:
        flags.append("no assumptions declared")
        availability_penalty += 0.5
    if len(limitations) == 0:
        flags.append("no limitations declared")
        availability_penalty += 0.5
    # thin-but-nonempty: fewer stated items than method-file complexity would predict
    expected_min = max(1, len(method_files))  # crude complexity proxy: >=1 assumption per method file
    if 0 < len(assumptions) < expected_min:
        flags.append("assumptions thinner than method complexity suggests")
        availability_penalty += 0.15
    if 0 < len(limitations) < expected_min:
        flags.append("limitations thinner than method complexity suggests")
        availability_penalty += 0.15

    # --- 5.2 assumption realism ---
    if kept_assumptions:
        a_scores = []
        for a in kept_assumptions:
            j = llm_judge.judge_assumption(a["text"], method_files)
            a_scores.append(score_assumption(j))
            if j["is_dreamcase"] and not j["support_given"]:
                flags.append(f"{a['id']}: unqualified dreamcase assumption")
        assumption_component = sum(a_scores) / len(a_scores)
    else:
        assumption_component = 0.0

    # --- 5.3 limitation validity ---
    if kept_limitations:
        l_scores = []
        for l in kept_limitations:
            j = llm_judge.judge_limitation(l["text"], boundary, [a["text"] for a in assumptions])
            l_scores.append(score_limitation(j))
            if j["restates_existing"]:
                flags.append(f"limitation '{l['name']}' restates an existing boundary/assumption")
            if j["generic_boilerplate"]:
                flags.append(f"limitation '{l['name']}' is generic boilerplate")
        limitation_component = sum(l_scores) / len(l_scores)
    else:
        limitation_component = 0.0

    # --- 5.4 omission scan ---
    all_bullet_texts = [t for _, t in all_bullets] + caveats
    risks = llm_judge.scan_design_risks("\n\n".join(
        sec for f in method_files for sec in f.get("sections", {}).values()
    ))
    unsurfaced = [r for r in risks if not llm_judge.is_surfaced(r["trigger"], all_bullet_texts)]
    for r in unsurfaced:
        flags.append(f"unsurfaced field-standard risk: {r['trigger']} ({r['evidence_quote'][:80]})")
    omission_penalty = min(0.6, 0.15 * len(unsurfaced))  # capped so one metric can't zero the score alone

    if evidence_tables_flags:
        unreconciled = [f for f in evidence_tables_flags if f not in caveats]
        for f in unreconciled:
            flags.append(f"evidence inconsistency not reflected in constraints.md caveats: {f}")
        omission_penalty = min(0.6, omission_penalty + 0.1 * len(unreconciled))
    elif evidence_tables_flags is None:
        # unavailable cross-layer input: scored at its own worst case for this sub-term, not skipped
        omission_penalty = min(0.6, omission_penalty + 0.1)
        flags.append("evidence-layer reconciliation check unavailable — scored as worst case, not skipped")

    # --- Aggregate ---
    content_score = 0.5 * assumption_component + 0.5 * limitation_component
    content_score = max(0.0, content_score - omission_penalty)
    final = max(0.0, content_score - availability_penalty)

    return {
        "score": round(final * 100, 1),
        "components": {
            "assumption_realism": round(assumption_component, 3),
            "limitation_validity": round(limitation_component, 3),
            "omission_penalty": round(omission_penalty, 3),
            "availability_penalty": round(availability_penalty, 3),
            "n_redundant_bullets": n_redundant,
        },
        "flags": flags,
    }
```

Notes on the function:
- All three penalty channels (availability, redundancy, omission) are **subtractive from a
  content-quality base**, not multiplicative gates that could zero out an otherwise-good score from one
  bad sub-check alone (`omission_penalty` is capped at 0.6) — except the single true structural floor
  (constraints.md entirely absent), which is an intentional hard zero because that is a different kind
  of failure (artifact malformation, not epistemic weakness).
- Every branch that could tempt an "N/A" — no assumptions, no limitations, no evidence-layer input,
  zero method files — instead produces a defined penalty term. There is no code path that returns
  `None`/skip.

## 6. Why this is hard to Goodhart

- **The judge reasons from the method's actual content, not from surface wording.** Realism and
  load-bearing-ness are assessed by an LLM reading the method file(s) alongside each assumption — an
  author/compiler can't satisfy the check by choosing better *words* for a weak assumption; the judge is
  asked whether the conclusion would change if it were false, which depends on what the method actually
  does.
- **The omission scan is adversarial to non-disclosure.** It doesn't grade what was declared in
  isolation — it independently searches the method text for standard risk triggers and checks whether
  *any* of them went unaddressed. Hiding the shakiest assumption by simply not writing it down no longer
  helps, because the scan finds it from the method description itself.
- **Padding is actively punished, not merely unrewarded.** The cross-bucket dedup pass means restating
  a boundary condition as a limitation, or splitting one caveat into three bullets, reduces (via the
  redundancy flag) rather than inflates the score. Triviality weighting (`load_bearing=false → ×0.4`)
  means stacking uncontroversial assumptions doesn't move the average up.
- **Boilerplate has a named, checked category.** Generic hedges are not merely "not rewarded" — the
  limitation-validity prompt explicitly detects genre-boilerplate phrasing and scores it near zero,
  closing the cheapest gaming route (copy a stock limitations paragraph into every paper).
- **No skip/NA branch exists to exploit.** Because every missing-input path is a scored penalty (§5.5),
  an artifact can't improve its score by omitting a subsection and hoping the metric abstains — thinness
  is itself evidence against the paper.

## 7. Composition with the rest of the suite

- **vs. round-1 07 (concreteness):** 07 asks whether each bullet is specific in *form* (numbers,
  named quantities, no vague hand-waving). M30 assumes bullets may already be concrete and asks whether
  they are *true/fair/informative in content*. A paper can score high on 07 (crisply worded assumptions)
  and low on M30 (a crisply worded but unrealistic dreamcase assumption), and vice versa (a vaguely
  worded but genuinely load-bearing and honestly-hedged limitation). The two are not redundant; a
  paper that games one does not automatically game the other.
- **vs. verifier D3 (explicitness):** D3 checks presence/labeling (are assumptions given IDs, are
  limitations under a named heading). M30 assumes presence and asks whether presence is *substantive*.
  A stub `## Assumptions` section with one throwaway bullet passes D3 (it exists, it's labeled) but
  scores near the availability floor under M30.
- **Net-new signal:** M30 is the only metric in this artifact's coverage that reads the method file(s)
  independently to check for *unsurfaced* risk — every other constraints-focused check is
  declaration-scoped (grades what's written). This closes the specific gap the assessment-critique
  flagged this metric for: neither round-1 07 nor verifier D3 judges realism/fairness, and this
  workflow operationalizes that judgment concretely rather than leaving it as an unscored "deeper
  signal" aspiration.
- **Downstream composability:** the returned `flags` list is designed to be human/agent-legible on its
  own (each flag names the specific bullet or trigger), so it can feed a paper-level red-flag rollup
  alongside other metrics' flags without needing to re-parse `constraints.md`.

M30 expander2: done
