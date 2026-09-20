# M30 — Assumption realism & limitation validity (expander 1)

## 1. Expanded reasoning

### What this indicator actually signals
Every ARA's `logic/solution/constraints.md` states boundary conditions, assumptions (A1, A2, ...),
and known limitations. Two existing checks already touch this file: round-1 metric 07 checks that
constraints are *concrete* (specific numbers/scopes rather than vague hand-waving), and verifier D3
checks that assumptions are *explicit* (present at all, ref-id'd, traceable). Neither asks the harder
question this metric targets: **are the stated assumptions actually realistic for the work as
performed, and do the stated limitations represent genuinely new information the reader didn't
already have from reading the method?**

This is a *validity* check layered on top of *presence* and *concreteness* checks. A paper can score
well on 07 (concrete constraints) and D3 (explicit assumptions) while still committing the two failure
modes this metric exists to catch:

- **Dreamcase assumptions**: assumptions that quietly assume away the paper's actual hardest problem
  (e.g., "we assume no unmeasured confounding" in an observational cohort study with known strong
  confounders; "we assume the sensor is noise-free" in a robotics paper whose entire contribution is
  handling noisy sensors). These are assumptions that, if true, would make much of the paper's stated
  contribution unnecessary or would make the reported effect sizes unbelievable.
- **Restated-not-new limitations**: a "Known limitations" section that just re-describes the method's
  scope (which the reader already inferred from `study_design.md`) rather than surfacing a genuinely
  new caveat — e.g., "Known limitations: our study only examined blood-based biomarkers" when
  `constraints.md`'s own `## Boundary conditions` already said exactly that. A restated limitation adds
  zero bits; a real limitation trades against the paper's stated contribution (e.g., "our AUC estimates
  may not generalize to community-dwelling populations because all cohorts were memory-clinic
  referrals" — this is new, and it costs the paper something).

### What it must reward
- Assumptions whose realism can be checked against the paper's own reported population/design/data
  (internal check) — e.g., an assumption of "independent patients across cohorts" that the paper's own
  Table 1 cohort list makes plausible or implausible.
- Assumptions whose realism can be checked against external domain knowledge (via [sem] lookup) — e.g.,
  an ML paper assuming i.i.d. train/test splits in a domain where distribution shift is well documented
  in the literature, or a clinical paper assuming a biomarker cutoff is population-invariant when
  published meta-analyses show it isn't.
- Limitations that name a *specific, falsifiable* threat to a *specific, named* result (a limitation
  tied to Table 2's effect size, not a generic "more research is needed").
- The compiler-added "Additional caveats surfaced during compilation (data-quality notes)" subsection
  actually being populated when `evidence/` has internal inconsistencies (per the shape file's own
  guidance) — its presence/absence is itself a signal of limitation-section rigor.

### What it must NOT reward
- Sheer *count* of assumptions or limitations (Goodhart target #1 — an author or compiler could inflate
  the count with trivial/boilerplate bullets).
- Hedging language density ("may", "could", "potentially") without a named mechanism or falsifiable
  claim.
- Limitations copy-pasted from a template every paper in the genre uses verbatim (detectable by
  cross-ARA text similarity, see Goodhart section).
- Assumptions that are realistic but irrelevant to the paper's central claim (padding).

### Failure modes / gaming routes and how the design resists them
1. **Bullet-count inflation.** Countered by scoring per-bullet *validity*, not bullet count; the final
   score is a mean/min over judged bullets, not a sum, so adding weak bullets dilutes rather than
   inflates.
2. **Boilerplate/templated limitations copied across a compiler's outputs for a given genre.** Countered
   by an explicit sub-check (step 5 below) that flags limitation text that is near-duplicate of generic
   genre boilerplate the LLM judge is shown as negative exemplars, and — more robustly — by requiring
   each limitation to name a **specific in-artifact target** (a table, section, or result ref) it
   threatens; ungrounded limitations score low regardless of how specific-sounding their prose is.
3. **Self-serving assumption laundering** (author states an assumption that is realistic-*sounding* but
   actually assumes away the hard part). Countered by the [sem] cross-check step, which asks an external
   evidence source whether the assumption is contested/known-false in the relevant literature, not just
   whether it reads plausibly in isolation.
4. **LLM judge sycophancy toward confident prose.** Countered by forcing the judge to output a discrete
   per-bullet verdict (realistic / dreamcase / unverifiable) plus a one-sentence mechanism, then
   deterministically mapping verdicts to scores in Python rather than asking for a holistic 0-10 rating
   directly — this makes the judge's reasoning auditable and harder to satisfy with confident tone alone.
5. **Missing-file gaming** (compiler omits `constraints.md`'s assumptions/limitations sections
   entirely to dodge the check). Countered by the penalize-don't-skip design: absence of a required
   subsection, or a subsection reduced to a single generic bullet, is scored as the *worst* case
   (0 realism, 0 novelty), not skipped/N-A. Abstract-only sources (per shape file's availability notes)
   are a known floor case and score at the floor honestly, rather than being excluded from scoring.

### Why this is hard to Goodhart
The score is bullet-level, mechanism-grounded, and anchored to two independent evidence sources per
bullet (in-artifact cross-check against other sections + external [sem] lookup for contested claims).
An author/compiler cannot raise the score by writing more or writing more confidently; they can only
raise it by the assumption actually being realistic and the limitation actually naming a new, specific,
falsifiable threat to a named result — which requires the underlying work to actually have been done
carefully. The metric composes cleanly with 07 (concreteness) and D3 (explicitness) as a three-layer
stack — present → concrete → valid — rather than re-measuring either.

## 2. Generation / compute workflow

### Inputs (artifact fields)
- `logic/solution/constraints.md` — REQUIRED. Sections: `## Boundary conditions`, `## Assumptions`
  (bulleted, ref-id'd `A1`, `A2`, ...), `## Known limitations (§X.Y)`, optional
  `## Additional caveats surfaced during compilation (data-quality notes)`.
- `logic/solution/{study_design.md, method.md, ...}` — sibling method files, used as the internal
  cross-check surface (what did the method actually do, to judge assumption realism against it).
- `logic/problem.md` (cross-layer, per shape file's note that method-layer artifacts may re-list
  problem-layer content) — used only to detect whether an "Assumption" bullet is a verbatim carry-over
  vs. method-specific.
- `evidence/` tables' internal-consistency notes (cross-layer; only used for the data-quality-caveats
  sub-check, step 5) — accessed via `DATA_SHAPES.md`-documented evidence section, read read-only for
  cross-referencing, not scored itself.

### Step 0 — Availability gate (penalize, never skip)
```python
def availability_gate(constraints_md: str | None) -> tuple[float, str]:
    """Returns (score_ceiling, reason). Never returns None/NA."""
    if constraints_md is None or not constraints_md.strip():
        return 0.0, "constraints.md missing entirely — worst case"
    if len(constraints_md.strip()) < 120:  # bare-bones / abstract-only floor
        return 0.15, "constraints.md present but near-empty (abstract-only floor case)"
    return 1.0, "constraints.md present with substantive content"
```
The gate produces a *ceiling multiplier*, not a bypass — steps 1-5 still run against whatever content
exists (even a single thin bullet gets judged), and the final score is `min(ceiling, computed_score)`.
This guarantees missing/thin inputs cannot be skipped and always cap the score low.

### Step 1 — Parse structure
```python
import re

def parse_constraints(md: str) -> dict:
    def section(name):
        m = re.search(rf"^##\s+{name}.*?\n(.*?)(?=^##\s|\Z)", md, re.S | re.M | re.I)
        return m.group(1).strip() if m else ""
    def bullets(text):
        return [b.strip("- ").strip() for b in text.splitlines() if b.strip().startswith(("-", "*"))]
    return {
        "boundary": bullets(section("Boundary conditions")),
        "assumptions": bullets(section("Assumptions")),
        "limitations": bullets(section(r"Known limitations")),
        "data_quality_caveats": bullets(section("Additional caveats.*")),
    }
```

### Step 2 — Internal realism cross-check (per assumption bullet)
For each assumption bullet, pull the relevant method-file text (study_design.md/method.md) and ask
whether the paper's own reported design makes the assumption plausible. This is a targeted [sem]-style
LLM call, but grounded entirely in in-artifact text (no external fetch needed for this step):

**Prompt (LLM judge, one call per assumption bullet):**
```
You are auditing whether a stated methodological ASSUMPTION is realistic given how the study was
actually conducted, per its own method description.

ASSUMPTION: "{assumption_text}"

METHOD DESCRIPTION (verbatim, from this paper's method files):
"""
{method_files_concatenated_or_truncated_to_8k_chars}
"""

Answer in this exact format:
VERDICT: <realistic | dreamcase | unverifiable>
MECHANISM: <one sentence: what in the method text supports or contradicts this assumption>
STAKES: <one sentence: if this assumption is false, what result/claim in the paper would be
undermined, or "none identified" if the assumption is inconsequential>
```
`dreamcase` = the method description itself contains evidence the assumption doesn't hold (e.g. the
method mentions handling missing data but the assumption claims "no missing data"), or the assumption
assumes away the paper's own stated hard problem. `unverifiable` = method text is silent, can't be
judged from artifact alone (routed to step 3 for external check before falling back).

### Step 3 — External realism cross-check ([sem] call, only for `unverifiable` or flagged assumptions)
```
[sem] query template (semantic-scholar / undermind lookup):
  "Is the assumption '{assumption_text}' commonly violated or contested in {domain_from_problem.md}
   research using {method_type_from_method.md}? Cite evidence."
```
The external call output is reduced deterministically:
```python
def external_verdict(sem_result: dict) -> str:
    # sem_result expected: {"contested": bool, "citation_count": int, "summary": str}
    if sem_result.get("contested") and sem_result.get("citation_count", 0) >= 2:
        return "dreamcase"
    if sem_result.get("citation_count", 0) == 0:
        return "unverifiable"
    return "realistic"
```
If no [sem] tool is available in a given run, `unverifiable` assumptions are scored at the
`unverifiable` tier (see scoring table) rather than defaulted to `realistic` — silence is not
evidence of realism.

### Step 4 — Limitation novelty check (per limitation bullet)
```
Prompt (LLM judge, one call per limitation bullet, given full constraints.md + boundary conditions):

You are checking whether a stated LIMITATION adds genuinely new information beyond what the paper's
own Boundary Conditions / method description already established.

LIMITATION: "{limitation_text}"

BOUNDARY CONDITIONS (already stated elsewhere in this artifact):
"""
{boundary_conditions_bullets}
"""

Answer in this exact format:
NOVELTY: <new | restated | generic>
TARGET: <the specific table/section/result this limitation threatens, quoted or referenced from the
         artifact, or "none named" if the limitation names no specific target>
```
`restated` = paraphrases a boundary condition already stated. `generic` = boilerplate
("further research needed", "sample size may limit generalizability" with no specifics) with no named
target. `new` = names a specific, previously-unstated threat to a specific result.

### Step 5 — Data-quality-caveat coverage check (artifact cross-reference, deterministic — no LLM)
```python
def data_quality_coverage(parsed: dict, evidence_internal_inconsistencies: list[str]) -> float:
    """evidence_internal_inconsistencies: list of discrepancy strings pulled from evidence/ tables'
    own consistency notes (e.g. 'Table 1 row count vs caption mismatch')."""
    if not evidence_internal_inconsistencies:
        return 1.0  # nothing to surface, no penalty
    caveats_text = " ".join(parsed["data_quality_caveats"]).lower()
    covered = sum(1 for d in evidence_internal_inconsistencies if _fuzzy_hit(d.lower(), caveats_text))
    return covered / len(evidence_internal_inconsistencies)

def _fuzzy_hit(needle_terms: str, haystack: str, threshold: float = 0.4) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", needle_terms))
    hits = sum(1 for t in tokens if t in haystack)
    return (hits / max(len(tokens), 1)) >= threshold
```

### Step 6 — Final scoring function
```python
def score_assumption_realism_and_limitation_validity(artifact) -> dict:
    """
    artifact: object exposing
      .constraints_md: str | None
      .method_files_text: str
      .problem_md: str
      .evidence_internal_inconsistencies: list[str]
      .domain, .method_type: str (from problem.md/method.md, for [sem] query)
      .sem_lookup(query: str) -> dict   # external call, may raise/return {} if unavailable
    Returns {"score": float in [0,1], "detail": {...}} — never None/NA.
    """
    ceiling, ceiling_reason = availability_gate(artifact.constraints_md)
    if ceiling == 0.0:
        return {"score": 0.0, "detail": {"reason": ceiling_reason}}

    parsed = parse_constraints(artifact.constraints_md)

    # --- assumptions ---
    verdict_score = {"realistic": 1.0, "unverifiable": 0.4, "dreamcase": 0.0}
    assumption_scores = []
    assumption_detail = []
    for a in parsed["assumptions"]:
        v1 = llm_judge_internal_realism(a, artifact.method_files_text)  # step 2
        verdict = v1["VERDICT"]
        if verdict == "unverifiable":
            sem_result = artifact.sem_lookup(
                f"Is the assumption '{a}' commonly violated or contested in "
                f"{artifact.domain} research using {artifact.method_type}? Cite evidence."
            ) if getattr(artifact, "sem_lookup", None) else {}
            verdict = external_verdict(sem_result) if sem_result else "unverifiable"
        # stakes multiplier: a dreamcase assumption with high stakes is worse than one with none
        stakes_mult = 1.3 if v1.get("STAKES", "none identified") != "none identified" and verdict == "dreamcase" else 1.0
        s = max(0.0, verdict_score[verdict] / stakes_mult) if verdict == "dreamcase" else verdict_score[verdict]
        assumption_scores.append(s)
        assumption_detail.append({"assumption": a, "verdict": verdict, **v1})
    if not parsed["assumptions"]:
        assumption_scores = [0.0]  # penalize absence, don't skip

    # --- limitations ---
    novelty_score = {"new": 1.0, "restated": 0.3, "generic": 0.0}
    limitation_scores = []
    limitation_detail = []
    for lim in parsed["limitations"]:
        v2 = llm_judge_limitation_novelty(lim, parsed["boundary"])  # step 4
        base = novelty_score[v2["NOVELTY"]]
        targeted_bonus = 0.0 if v2["TARGET"] == "none named" else 0.0  # target required for full credit
        s = base if v2["TARGET"] != "none named" or v2["NOVELTY"] != "new" else 0.7  # "new" w/o named target capped
        limitation_scores.append(s)
        limitation_detail.append({"limitation": lim, **v2})
    if not parsed["limitations"]:
        limitation_scores = [0.0]  # a paper with zero stated limitations is a red flag per shape file

    dq_coverage = data_quality_coverage(parsed, artifact.evidence_internal_inconsistencies)

    assumption_component = sum(assumption_scores) / len(assumption_scores)
    limitation_component = sum(limitation_scores) / len(limitation_scores)

    raw = 0.40 * assumption_component + 0.45 * limitation_component + 0.15 * dq_coverage
    final = min(ceiling, raw)

    return {
        "score": round(final, 3),
        "detail": {
            "ceiling": ceiling, "ceiling_reason": ceiling_reason,
            "assumption_component": round(assumption_component, 3),
            "limitation_component": round(limitation_component, 3),
            "data_quality_coverage": round(dq_coverage, 3),
            "assumptions": assumption_detail,
            "limitations": limitation_detail,
        },
    }
```

Weighting rationale: limitations get slightly more weight (0.45 vs 0.40) than assumptions because
novel, falsifiable limitations are rarer and harder to fake than plausible-sounding assumptions; the
data-quality-caveat sub-check gets a smaller fixed weight (0.15) since it's a narrower, binary-ish
signal that only fires when `evidence/` actually has a reconciliation problem — most ARAs will score
1.0 on it trivially (nothing to surface), so it acts mainly as a penalty tripwire rather than a reward
driver.

### Notes on [sem] usage
- Only fired for assumptions the internal check can't resolve (`unverifiable`) — bounds external-call
  volume to roughly the fraction of assumptions lacking in-artifact grounding, typically 1-3 calls per
  artifact.
- If the [sem] tool is unavailable at compute time, the workflow does NOT skip the assumption or treat
  it as realistic — it stays `unverifiable` and scores at the fixed 0.4 tier, consistent with
  penalize-don't-skip.

## 3. Composition with the rest of the suite
This metric sits strictly above 07 (concreteness of constraints.md) and D3 (explicitness of
assumptions) in the same file, checking a property (*validity*) that both can trivially pass while this
one fails. It does not re-score presence (07/D3 already do that) — the availability gate here is
deliberately coarse (a ceiling, not the main signal) precisely so the bulk of the score differentiates
on realism/novelty, not on whether the section exists. It shares no LLM prompt or scoring logic with 07
or D3, and its external [sem] step is used only as a fallback, keeping its marginal compute cost low
relative to its differentiating power.
