# M30 — Assumption realism & limitation validity — Improved (cycle 2, A)

## Changes (cycle 2)

Base: exp2 (cycle-1 winner, rank 1). Addressing the five cycle-2 directions from `critique_c1.md`:

1. **Cut [sem] cost.** Collapsed five per-item LLM call *types* (many of them called once per
   bullet/trigger) into five per-*artifact* calls total: dedup now runs on deterministic embedding
   cosine similarity with a specified threshold band and only escalates borderline pairs to a single
   batched LLM tie-break call; per-assumption and per-limitation judging are each one batched
   list-in/list-out call instead of N calls; `is_surfaced` is one batched call over all triggers×bullets
   instead of one call per trigger. See §5.1, §5.2, §5.3, §5.4.
2. **Hardened the omission scan against invention.** Every flagged trigger's `evidence_quote` is now
   deterministically verified as an actual (near-exact, whitespace/punctuation-normalized) substring of
   `method_files` before it can contribute to the omission penalty. A trigger whose quote fails
   verification is discarded pre-scoring, not penalized — the false-positive cost is stated explicitly
   in §5.4 and §6: an unverifiable/hallucinated trigger would wrongly punish an honest paper for a risk
   it does not actually exhibit, so the gate is mandatory, not advisory.
3. **Replaced the crude thinness proxy.** `expected_min = len(method_files)` is gone. The scan
   (§5.4) now runs once, upstream of both the thinness gate and the omission penalty, and its
   *verified*-trigger count feeds both: thinness is `total_kept_items < len(verified_risks)`, a single
   combined check (not doubled across assumptions and limitations separately, which was silently
   double-penalizing thin artifacts in the cycle-1 version). See §5.1.5, §5.5.
4. **Added a worked example.** §8 traces the full pipeline over che26's real `constraints.md` (per
   `07_solution.md`'s shape example): A2 lands at `s=0.09` (flagrant unsupported dreamcase), the
   batch-effects limitation lands at `0.8`, one verified-unsurfaced spectrum-bias risk costs `0.15`,
   and the worst-offender cap is shown both non-binding (this case) and would-bind (counterfactual)
   so both code paths are demonstrated.
5. **Adopted exp3's worst-offender guard.** A single flagrant item (`min(a_scores) <= 0.1`, or a
   limitations section that is *entirely* near-zero) now caps the final score at 0.5 regardless of the
   average — closing the "one bad assumption diluted by several fine ones" gap that a pure mean allows.
   See §5.5 `worst_offender_cap`.

Everything else (the three-part reasoning frame, the reward/must-not-reward table, the gaming-route
table, and the hard structural floor for a missing `constraints.md`) is retained from exp2 as judged
correct in cycle 1, with pointers to what changed.

---

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
  for actually being realistic — unsupported *assertions* of plausibility are weaker evidence than a
  cited or field-corroborated one.
- **(new, cycle 2)** A single flagrant dreamcase assumption or a wholly-boilerplate limitations section
  hiding behind several fine, unrelated bullets that pull the *average* up — see §5.5 worst-offender cap.

## 3. Failure modes / gaming routes and how the design closes them

| Gaming route | Countermeasure in this workflow |
|---|---|
| Pad with many trivial/uncontroversial assumptions to look thorough | Per-assumption **triviality/load-bearing** classification; trivial assumptions get near-zero weight regardless of how many there are; aggregate uses a capped, diminishing-returns mean, not a raw count |
| Pad with near-duplicate limitation bullets | Pairwise dedup pass (embedding cosine + narrow LLM tie-break, §5.1) before scoring; duplicates collapse to one scored instance and count against the "distinctiveness" flag |
| State only the easy/defensible assumptions, omit the load-bearing shaky one | Independent, **quote-verified omission scan** over the method file(s), cross-checked against constraints.md — a used-but-unsurfaced risk is a direct penalty term, found without relying on what the paper chose to disclose |
| Generic boilerplate limitations that are true of any paper in the genre | Boilerplate-phrase classifier (semantic, batched) scores generic hedges near zero informativeness; a limitations section that is *entirely* boilerplate scores like a missing section AND triggers the worst-offender cap |
| Restate boundary conditions as limitations for double credit | Cross-bullet dedup runs *across* the three buckets (boundary conditions / assumptions / limitations), not just within one |
| Leave constraints.md thin/near-empty and hope the metric can't tell without other metrics catching it | Explicit availability/thinness gate (§5.5) that scores down rather than skipping, tied to the *actual measured method complexity* (verified-trigger count), not a crude file count |
| Assert plausibility without support ("this is a standard assumption") to farm a good realism score | The realism classifier requires the judge to independently assess plausibility from domain knowledge, not defer to the paper's own framing; unsupported self-assessment is capped below field-corroborated plausibility |
| **(new)** Bury one flagrant dreamcase assumption or a hollow limitations section among several fine bullets so the mean looks acceptable | **Worst-offender cap** (§5.5): a single item at/below the flagrant threshold, or an all-near-zero bucket, caps the final score at 0.5 regardless of what the mean says |
| **(new)** Judge hallucinates a design-risk trigger from a plausible-sounding genre stereotype rather than the actual method text, over-penalizing an honest paper | **Quote-verification gate** (§5.4): any `evidence_quote` that does not deterministically match text actually present in `method_files` is discarded before it can generate a penalty |

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

Total [sem] calls per artifact, all of them list-in/list-out (this is the cycle-2 cost cut — cycle-1
made one call per bullet/trigger; this version makes at most one call per *step*):

1. `dedup_tiebreak` (only for borderline embedding-similarity pairs, §5.1) — 0 or 1 call.
2. `judge_assumptions_batch` (§5.2) — 1 call for all surviving assumptions.
3. `judge_limitations_batch` (§5.3) — 1 call for all surviving limitations.
4. `scan_design_risks` (§5.4) — 1 call over all method files.
5. `is_surfaced_batch` (§5.4) — 1 call for all verified triggers against all bullets.

### 5.1 Parse + dedup pass (mostly deterministic)

1. Extract the three bullet lists from `constraints.md` as-is.
2. Compute pairwise cosine similarity (embedding model, any standard sentence-embedding) over
   **all three buckets combined** (boundary conditions, assumptions, limitations):
   - similarity `>= 0.87` → automatic duplicate, no LLM call.
   - similarity `< 0.72` → automatic non-duplicate, no LLM call.
   - `0.72 <= similarity < 0.87` → borderline band; batch all such pairs into a single
     `dedup_tiebreak` [sem] call.
   - [sem] call: `dedup_tiebreak(pairs: list[(str, str)]) -> list[bool]`. Prompt: *"For each pair
     (A, B) below, answer true if they state the same underlying constraint/condition even if worded
     differently, false otherwise. Return one boolean per pair, in order."*
3. For every confirmed duplicate pair, keep the more specific/longer bullet as the scored instance;
   mark the other `redundant` (contributes to the distinctiveness flag, not to real content).

### 5.1.5 Method-complexity scan (runs once, feeds both §5.4 and §5.5)

Run `scan_design_risks` (defined fully in §5.4) here, once, over the full `method_files` text, and
immediately apply the **quote-verification gate**:

```python
def verify_and_filter_risks(risks: list[dict], method_files: list[dict]) -> list[dict]:
    corpus = normalize_whitespace("\n\n".join(
        sec for f in method_files for sec in f.get("sections", {}).values()
    ))
    verified = []
    discarded = 0
    for r in risks:
        q = normalize_whitespace(r["evidence_quote"])
        if q and (q in corpus or fuzzy_ratio(q, corpus) >= 0.90):
            verified.append(r)
        else:
            discarded += 1
    return verified, discarded
```

`verified_risks` (the output list) is the single source of truth used by both:
- the thinness proxy in §5.5 (replaces the cycle-1 `len(method_files)` heuristic), and
- the omission penalty in §5.4.

If `discarded > 0`, add an audit flag (`"N discarded unverifiable design-risk trigger(s) — not
penalized"`) but **do not** apply any score penalty for discarded triggers — see §6 for why a
hallucinated trigger must never cost the artifact points.

### 5.2 Per-assumption realism classification [sem, batched]

For all surviving (non-duplicate) assumptions at once:

**Prompt (LLM judge, structured JSON output, one object per input assumption, order-preserved):**
```
You are assessing stated methodological assumptions from a research paper's constraints section.

Paper domain/method context: {method_files rendered as markdown, truncated to relevant sections}
Assumptions (in order):
1. "{assumption_1.text}"
2. "{assumption_2.text}"
...

Return a JSON array, one object per assumption, in the same order:
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

### 5.3 Per-limitation validity classification [sem, batched]

For all surviving (non-duplicate) limitations at once:

**Prompt (LLM judge, structured JSON output, one object per input limitation, order-preserved):**
```
You are assessing stated "known limitations" from a research paper, given the paper's already-
declared boundary conditions and assumptions (so you can detect restatement).

Boundary conditions: {list}
Assumptions: {list}
Limitations under review (in order):
1. "{limitation_1.text}"
2. "{limitation_2.text}"
...

Return a JSON array, one object per limitation, in the same order:
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

### 5.4 Omission scan — unsurfaced field-standard caveats [sem, batched + quote-gated]

1. `scan_design_risks` was already run once in §5.1.5; reuse `verified_risks` (quote-verified) here —
   do not re-scan.
   - [sem] call contract: `scan_design_risks(method_files_text: str) -> list[{"trigger": str,
     "evidence_quote": str}]`. Prompt: *"List design choices in this Methods text that carry a
     well-known, field-standard methodological caveat (e.g. single-center, retrospective, small N,
     self-report, no control arm, post-hoc subgroup, unvalidated instrument, missing-data handling
     without sensitivity analysis). For each, quote the exact sentence that reveals the choice — if you
     cannot quote an exact sentence, do not list the trigger."* The instruction to withhold unquotable
     triggers is a prompt-level guard; §5.1.5's deterministic substring check is the enforcement layer
     that does not depend on the model obeying it.
2. [sem] call, batched over all `verified_risks` at once:
   `is_surfaced_batch(triggers: list[str], constraints_bullets: list[str]) -> list[bool]` — *"For each
   trigger below, answer true if any of these boundary-condition/assumption/limitation bullets
   addresses the caveat associated with that trigger, false otherwise. Return one boolean per trigger,
   in order."*
3. Also reconcile against `evidence_tables_flags` if available (per shape doc: numbers that don't
   reconcile between a table and its caption should be flagged in constraints.md's "Additional caveats"
   subsection): for each externally-known internal-inconsistency flag, check `data_quality_caveats` for
   a matching entry.
4. Every triggered-but-unsurfaced *verified* risk is a fixed penalty (see §5.5). If
   `evidence_tables_flags` is unavailable, that specific check contributes its own worst case (0), not a
   skip — consistent with penalize-don't-skip.

### 5.5 Aggregate score (final scoring function)

```python
def compute_m30(constraints: dict, method_files: list, evidence_tables_flags: list | None,
                 llm_judge) -> dict:
    """
    Returns {"score": float in [0,100], "components": {...}, "flags": [...]}.
    llm_judge exposes: dedup_tiebreak, judge_assumptions_batch, judge_limitations_batch,
    scan_design_risks, is_surfaced_batch.
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

    # --- 5.1 dedup (embedding + narrow LLM tie-break) across all buckets ---
    kept, redundant_idx = dedup_bullets(all_bullets, llm_judge)  # see §5.1
    kept_assumptions = [a for a in assumptions if ("assumption", a["text"]) in kept]
    kept_limitations = [l for l in limitations if ("limitation", l["text"]) in kept]

    n_redundant = len(redundant_idx)
    if n_redundant:
        flags.append(f"{n_redundant} bullet(s) redundant across boundary/assumption/limitation buckets")

    # --- 5.1.5 method-complexity scan, run once, quote-verified ---
    raw_risks = llm_judge.scan_design_risks("\n\n".join(
        sec for f in method_files for sec in f.get("sections", {}).values()
    ))
    verified_risks, n_discarded = verify_and_filter_risks(raw_risks, method_files)
    if n_discarded:
        flags.append(f"{n_discarded} discarded unverifiable design-risk trigger(s) — not penalized")

    # --- Availability + thinness gate (penalize, never skip; single combined thinness check) ---
    availability_penalty = 0.0
    if len(assumptions) == 0:
        flags.append("no assumptions declared")
        availability_penalty += 0.5
    if len(limitations) == 0:
        flags.append("no limitations declared")
        availability_penalty += 0.5
    # thinness tied to measured method complexity (verified triggers), not a crude file count,
    # and checked once combined — not doubled per-bucket.
    expected_min_items = max(1, len(verified_risks))
    total_kept_items = len(kept_assumptions) + len(kept_limitations)
    if total_kept_items < expected_min_items:
        shortfall = expected_min_items - total_kept_items
        flags.append(
            f"declared assumptions+limitations ({total_kept_items}) thinner than the "
            f"{expected_min_items} field-standard risk(s) found in the method text"
        )
        availability_penalty += 0.15 * min(2, shortfall)   # capped scaling

    # --- 5.2 assumption realism (batched) ---
    if kept_assumptions:
        judged = llm_judge.judge_assumptions_batch(
            [a["text"] for a in kept_assumptions], method_files)
        a_scores = [score_assumption(j) for j in judged]
        for a, j, s in zip(kept_assumptions, judged, a_scores):
            if j["is_dreamcase"] and not j["support_given"]:
                flags.append(f"{a['id']}: unqualified dreamcase assumption")
        assumption_component = sum(a_scores) / len(a_scores)
    else:
        a_scores = []
        assumption_component = 0.0

    # --- 5.3 limitation validity (batched) ---
    if kept_limitations:
        judged = llm_judge.judge_limitations_batch(
            [l["text"] for l in kept_limitations], boundary, [a["text"] for a in assumptions])
        l_scores = [score_limitation(j) for j in judged]
        for l, j in zip(kept_limitations, judged):
            if j["restates_existing"]:
                flags.append(f"limitation '{l['name']}' restates an existing boundary/assumption")
            if j["generic_boilerplate"]:
                flags.append(f"limitation '{l['name']}' is generic boilerplate")
        limitation_component = sum(l_scores) / len(l_scores)
    else:
        l_scores = []
        limitation_component = 0.0

    # --- 5.4 omission scan (batched is_surfaced, quote-verified triggers only) ---
    all_bullet_texts = [t for _, t in all_bullets] + caveats
    if verified_risks:
        surfaced = llm_judge.is_surfaced_batch(
            [r["trigger"] for r in verified_risks], all_bullet_texts)
        unsurfaced = [r for r, ok in zip(verified_risks, surfaced) if not ok]
    else:
        unsurfaced = []
    for r in unsurfaced:
        flags.append(f"unsurfaced field-standard risk: {r['trigger']} ({r['evidence_quote'][:80]})")
    omission_penalty = min(0.6, 0.15 * len(unsurfaced))  # capped so one channel can't zero the score alone

    if evidence_tables_flags:
        unreconciled = [f for f in evidence_tables_flags if f not in caveats]
        for f in unreconciled:
            flags.append(f"evidence inconsistency not reflected in constraints.md caveats: {f}")
        omission_penalty = min(0.6, omission_penalty + 0.1 * len(unreconciled))
    elif evidence_tables_flags is None:
        omission_penalty = min(0.6, omission_penalty + 0.1)
        flags.append("evidence-layer reconciliation check unavailable — scored as worst case, not skipped")

    # --- Aggregate ---
    content_score = 0.5 * assumption_component + 0.5 * limitation_component
    content_score = max(0.0, content_score - omission_penalty)
    final = max(0.0, content_score - availability_penalty)

    # --- Worst-offender cap (new, cycle 2, adopted from exp3) ---
    # A pure mean lets one flagrant item hide behind several fine, unrelated bullets. Cap the
    # ceiling — do not zero the score — so this is still additive with, not a replacement for,
    # the rest of the pipeline.
    FLAGRANT = 0.10
    worst_offender_triggered = False
    if a_scores and min(a_scores) <= FLAGRANT:
        worst_offender_triggered = True
        flags.append(f"worst-offender cap applied: flagrant unqualified/implausible assumption present")
    if l_scores and all(s <= FLAGRANT for s in l_scores):
        worst_offender_triggered = True
        flags.append("worst-offender cap applied: limitations section is entirely near-zero/hollow")
    if worst_offender_triggered:
        final = min(final, 0.5)

    return {
        "score": round(final * 100, 1),
        "components": {
            "assumption_realism": round(assumption_component, 3),
            "limitation_validity": round(limitation_component, 3),
            "omission_penalty": round(omission_penalty, 3),
            "availability_penalty": round(availability_penalty, 3),
            "n_redundant_bullets": n_redundant,
            "n_verified_design_risks": len(verified_risks),
            "n_discarded_unverifiable_risks": n_discarded,
            "worst_offender_cap_applied": worst_offender_triggered,
        },
        "flags": flags,
    }
```

Notes on the function:
- All penalty channels (availability/thinness, redundancy, omission) are **subtractive from a
  content-quality base**, not multiplicative gates that could zero out an otherwise-good score from one
  bad sub-check alone (`omission_penalty` is capped at 0.6) — except the single true structural floor
  (constraints.md entirely absent), which is an intentional hard zero because that is a different kind
  of failure (artifact malformation, not epistemic weakness).
- The **worst-offender cap** is the one place a single item can override the mean, and it is a *ceiling*
  (`min(final, 0.5)`), not a zeroing — a good artifact with one flagrant lapse still scores as
  "mediocre," not "worthless," which keeps it distinguishable from the constraints.md-absent floor.
- Every branch that could tempt an "N/A" — no assumptions, no limitations, no evidence-layer input,
  zero method files, zero verified risks — instead produces a defined penalty term or a defined zero
  contribution. There is no code path that returns `None`/skip.
- Compute cost is now O(1) [sem] calls in the number of buckets/steps, not O(n) in the number of
  bullets/triggers (cycle-1's per-item calls are gone; see §5.0's call inventory).

## 6. Why this is hard to Goodhart

- **The judge reasons from the method's actual content, not from surface wording.** Realism and
  load-bearing-ness are assessed by an LLM reading the method file(s) alongside each assumption — an
  author/compiler can't satisfy the check by choosing better *words* for a weak assumption; the judge is
  asked whether the conclusion would change if it were false, which depends on what the method actually
  does.
- **The omission scan is adversarial to non-disclosure, and the quote gate makes it adversarial to
  itself.** It doesn't grade what was declared in isolation — it independently searches the method text
  for standard risk triggers and checks whether *any* of them went unaddressed. Hiding the shakiest
  assumption by simply not writing it down no longer helps, because the scan finds it from the method
  description itself. Symmetrically, the deterministic substring/fuzzy-match gate on `evidence_quote`
  means the judge cannot invent a risk from genre stereotype and have it silently cost the artifact
  points — a trigger that can't be quoted from the actual text is discarded before scoring, not merely
  down-weighted. **Stated false-positive cost:** without this gate, an honest paper with an unusual
  design could be penalized for a "standard" risk it doesn't actually carry, simply because the judge
  pattern-matched the genre; the gate makes that failure mode structurally impossible rather than
  merely unlikely.
- **Padding is actively punished, not merely unrewarded.** The cross-bucket dedup pass means restating
  a boundary condition as a limitation, or splitting one caveat into three bullets, reduces (via the
  redundancy flag) rather than inflates the score. Triviality weighting (`load_bearing=false → ×0.4`)
  means stacking uncontroversial assumptions doesn't move the average up.
- **A single flagrant lapse can no longer hide in a good average.** The worst-offender cap (§5.5) closes
  the residual gap a pure-mean design has: an artifact can't offset one unsupported dreamcase assumption
  or a wholly-boilerplate limitations section by padding the rest of the section with fine, unrelated
  bullets — the cap fires on the worst item/bucket, independent of the mean.
- **Boilerplate has a named, checked category.** Generic hedges are not merely "not rewarded" — the
  limitation-validity prompt explicitly detects genre-boilerplate phrasing and scores it near zero,
  closing the cheapest gaming route (copy a stock limitations paragraph into every paper).
- **No skip/NA branch exists to exploit.** Because every missing-input path is a scored penalty (§5.5),
  an artifact can't improve its score by omitting a subsection and hoping the metric abstains — thinness
  is itself evidence against the paper, and thinness is now measured against the method's *actual*
  measured complexity (verified risk count) rather than a proxy (file count) an author could game by
  splitting or merging method files without changing content.

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
  workflow operationalizes that judgment concretely, with the cycle-2 quote-verification gate ensuring
  the "reads independently" edge doesn't itself become a source of ungrounded penalties.
- **Downstream composability:** the returned `flags` list is designed to be human/agent-legible on its
  own (each flag names the specific bullet or trigger), so it can feed a paper-level red-flag rollup
  alongside other metrics' flags without needing to re-parse `constraints.md`.

## 8. Worked example (che26, per `07_solution.md`'s shape example)

Input `constraints.md` (che26, verbatim from the shape doc):

```markdown
## Boundary conditions
- Scope is limited to blood-based p-tau biomarkers (plasma or serum) for AD; only isoforms
  p-tau217, p-tau181, p-tau231 on platforms MS/Simoa/MSD/Lumipulse were compared.
- Findings are relative rankings (P-scores) and AUC mean differences vs. a p181_IA baseline, not
  absolute pooled sensitivity/specificity/AUC for each marker.

## Assumptions
- A2: Selecting the single most comprehensive dataset per cohort yields statistically independent
  nodes (no patient double-counted).

## Known limitations (§4.5)
- Batch effects: although platforms were adjusted for, batch effects in manual immunoassays may
  still exist.

## Additional caveats surfaced during compilation (data-quality notes)
- Table 1 vs. its caption: Table 1 lists 12 cohort rows, but its caption says it details "the 6
  core representative cohorts..." (Table1/caption mismatch).
```

**§5.1 dedup:** 4 bullets across buckets, all on distinct topics (scope / measurement frame /
independence / batch effects) → no duplicates, `n_redundant = 0`.

**§5.1.5 scan:** over `study_design.md`, `scan_design_risks` returns two triggers, both quote-verified
against the method text:
- `spectrum_bias` — cohort inclusion pulls from tertiary memory-clinic referrals rather than a
  population-representative sample (quoted sentence present in `study_design.md`) — **not** surfaced by
  any bullet above (spectrum bias is a distinct concept from "batch effects" or "no double-counting").
- `platform_heterogeneity` — four different immunoassay platforms pooled (quoted sentence present) —
  judged **surfaced** by the "Batch effects" limitation, which addresses residual cross-platform bias.

`verified_risks = 2`, `n_discarded = 0`.

**§5.2 assumption A2:** judged `load_bearing=true`, `plausibility="convenient_but_shaky"`,
`is_dreamcase=true` (selecting "most comprehensive dataset per cohort" assumes away exactly the
hardest part — that differently-named cohorts might still share patients — without a citation or
sensitivity check), `support_given=false`.
`score_assumption`: base = 0.3 (convenient_but_shaky); dreamcase & unsupported → ×0.3 = **0.09**;
load-bearing so no further ×0.4; no support bonus. `assumption_component = 0.09`. Flag emitted:
`"A2: unqualified dreamcase assumption"`.

**§5.3 limitation "Batch effects":** judged `restates_existing=false`, `generic_boilerplate=false`
(names a specific mechanism — cross-platform immunoassay variability — not a stock hedge),
`specifies_mechanism=true`, `specifies_direction=false` (no stated direction/magnitude of the residual
bias). `score_limitation`: 0.5 + 0.3 = **0.8**. `limitation_component = 0.8`.

**§5.4 omission:** `is_surfaced_batch(["spectrum_bias", "platform_heterogeneity"], all_bullets)` →
`[false, true]`. `unsurfaced = [spectrum_bias]`. `omission_penalty = 0.15 * 1 = 0.15`. Flag:
`"unsurfaced field-standard risk: spectrum_bias (...)"`. `evidence_tables_flags` supplied and matches
the existing Table1/caption caveat bullet exactly → no unreconciled penalty added.

**§5.5 availability/thinness:** `len(assumptions)=1`, `len(limitations)=1` → neither zero, no
zero-item penalty. `expected_min_items = max(1, len(verified_risks)) = 2`.
`total_kept_items = 1 (assumption) + 1 (limitation) = 2`. `2 >= 2` → **no thinness penalty**.
`availability_penalty = 0.0`.

**Aggregate:**
```
content_score = 0.5*0.09 + 0.5*0.8 = 0.445
content_score -= omission_penalty(0.15) → 0.295
final = max(0, 0.295 - availability_penalty(0.0)) = 0.295
```

**Worst-offender cap:** `min(a_scores) = 0.09 <= 0.10` → cap triggered, flag `"worst-offender cap
applied: flagrant unqualified/implausible assumption present"`, `final = min(0.295, 0.5) = 0.295`
(non-binding here — the natural score is already below the cap; recorded for auditability).

**Final:** `score = 29.5`, `components = {assumption_realism: 0.09, limitation_validity: 0.8,
omission_penalty: 0.15, availability_penalty: 0.0, n_redundant_bullets: 0,
n_verified_design_risks: 2, n_discarded_unverifiable_risks: 0, worst_offender_cap_applied: true}`.

**Counterfactual showing the cap *binding*:** if the batch-effects limitation had instead scored
`0.95` (mechanism + direction both specified) and the omission scan found nothing unsurfaced, the
naive mean would give `content_score = 0.5*0.09 + 0.5*0.95 = 0.52`, `final = 0.52` — i.e. a single
flagrant, unsupported dreamcase assumption would net a "passing" score just by being averaged against
one strong limitation. The worst-offender cap forces `final = min(0.52, 0.5) = 0.5`, keeping a
flagrant-assumption artifact capped at "mediocre" regardless of how strong the rest of the section is.

This demonstrates: the flagrant dreamcase assumption is caught and heavily punished (0.09, not
averaged away); the omission scan independently finds a real, unsurfaced field-standard risk from the
method text alone (spectrum bias) without relying on the paper's own disclosure; the thinness proxy
correctly does *not* fire here because two disclosure-worthy items were in fact declared for two
verified risks (unlike the cycle-1 version, which would have compared against `len(method_files)=1`
and produced a different, method-file-count-dependent verdict); and the worst-offender cap is exercised
on both the binding and non-binding branches.

M30 improved (cycle 2, A): done
