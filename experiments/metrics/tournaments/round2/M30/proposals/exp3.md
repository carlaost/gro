# M30 — Assumption realism & limitation validity — Expansion + Workflow

Artifact: `logic/solution/constraints.md` (§7 "Boundary conditions / Assumptions / Known
limitations [/ Additional caveats]"), always-present per the shape doc.

## 1. Why this indicator signals good science

Every method rests on a set of conditions it needs to hold, and every method fails somewhere.
Good science is distinguished less by *having* assumptions and limitations (everyone does) than by
two much rarer properties:

- **The assumptions it chose to make are the ones the real-world data/setting actually approximates**,
  not the ones that happen to make the analysis tractable or the result look strong. A paper that
  assumes "no missing data," "perfectly calibrated instruments," or "class-balanced population" when
  its own cohort description says otherwise is quietly relocating the hard part of the problem outside
  the paper's scope — a *dreamcase* assumption. A paper that assumes "measurements are made with
  device-reported precision (±X, per manufacturer spec)" when that is in fact the best available
  characterization of the instrument is a *realistic* assumption — an honest idealization, not an
  evasion.
- **The limitations it states actually narrow the claim.** "Batch effects in manual immunoassays may
  still exist despite adjustment" tells a reader a specific mechanism under which the pooled estimate
  could be biased, in a specific direction, for a specific subset of platforms. "Future work should
  validate in larger, more diverse cohorts" tells the reader nothing they didn't already know about
  every study ever published — it is a hedge, not a limitation, and its presence should not be treated
  as equivalent to a genuine one.

This is a *fairness-of-self-assessment* signal: does the paper's stated model of its own weaknesses
match reality, or is it decorative. It is one of the few places a compiled artifact can catch a paper
that is locally rigorous (correct stats, clean pipeline, explicit assumptions list) but globally
misleading (the assumptions list is curated to avoid naming the thing that would actually threaten the
conclusion).

## 2. What it must reward / must not reward

**Reward:**
- Assumptions that are falsifiable/checkable against the paper's own cohort, instrumentation, or
  design as described elsewhere in the artifact (§2 problem, §5/§6 evidence) — i.e., assumptions
  stated in a form a reader could actually go verify or contest.
- Assumptions whose plausibility is *argued*, even briefly ("Selecting the single most comprehensive
  dataset per cohort yields independent nodes" is checkable; a one-clause justification of *why* that's
  plausible given the source registries would be even stronger, and should score higher than the same
  assumption asserted bare).
- Limitations that name a mechanism + a direction/magnitude of likely bias, or a specific
  subpopulation/condition/regime where the result may not hold.
- Limitations that engage with something the compiler's own evidence layer or problem layer *shows* is
  fragile (e.g., a small/non-representative subgroup visible in a table, a design choice flagged
  elsewhere as unusual) — i.e., internal consistency between what the paper admits and what the paper
  actually did.

**Must not reward:**
- Sheer *count* of assumptions/limitations (padding with many trivial ones must not outscore one
  substantive one — see Goodharting below).
- Generic, template-shaped hedges: "further research is needed," "results may not generalize,"
  "sample size limits statistical power" stated with no specifics (which subgroup, how much power, what
  would change) is boilerplate, not content, however true it is in general.
- Assumptions copied verbatim from a field's stock disclaimer list (e.g., every diagnostic-accuracy
  meta-analysis says "we assume no publication bias") when the paper visibly makes no attempt to check
  or bound that assumption (no funnel plot, no Egger's test) — restating a known risk is not the same
  as engaging with it.
- Length/verbosity as a proxy for genuineness — a long limitations section can be all boilerplate; a
  two-line one can be devastating and precise.

## 3. Failure modes / gaming routes (and how the design resists them)

1. **Padding**: add many low-stakes assumptions/limitations to dilute the denominator and hide the one
   dreamcase assumption among many innocuous ones. Resisted by scoring the *worst-offender* alongside
   the mean (see §5.7 — a single flagrant dreamcase assumption should be able to cap the score even if
   nine others are fine), not a simple average that padding can wash out.
2. **Boilerplate substitution**: swap a genuine limitation for template language that pattern-matches
   the *shape* of a good limitation ("Limited by X" prefix) without content. Resisted by requiring the
   [sem] judge to check for a named mechanism/direction/scope, not just section-heading presence — this
   is exactly why the metric needs semantic judgment rather than a keyword/regex check (which round-1 07
   and verifier D3 already do at the concreteness/explicitness layer — see §4).
3. **Selective omission**: state realistic assumptions for the parts of the method that are already
   solid, and simply omit the assumption that would be most damaging (rather than stating it falsely).
   This is the hardest gaming route because it's a *sin of omission* and non-obvious from constraints.md
   alone. Resisted (partially) by the cross-layer coverage check in §5.6: cross-referencing evidence-
   layer internal-consistency notes and problem-layer cohort/design description against what
   constraints.md admits — an omission that is visible elsewhere in the artifact (e.g. evidence/ already
   flags a table inconsistency that constraints.md never mentions) is directly catchable; a omission
   invisible anywhere in the artifact is a genuine blind spot no artifact-only metric can fully close,
   which is why this metric is scoped to "coverage of what's checkable from the artifact," not "omniscient
   detection of unstated flaws."
4. **Compiler-faithfulness gaming**: since this metric grades content the *compiler* transcribed from
   the *paper*, a compiler could underscore its own artifact by paraphrasing a paper's limitation into
   vaguer language, or overscore by inventing specificity the paper doesn't have. This is a fidelity
   concern (belongs to Seal Level 1 / a separate faithfulness metric), not something M30 can or should
   try to fix — M30 assumes the transcription is faithful and scores the *content* as transcribed. Where
   the shape doc's "Additional caveats surfaced during compilation" subsection exists, that IS
   compiler-added content and is treated as bonus signal (§5.7), not penalized for being compiler-voice
   rather than paper-voice.

## 4. What's net-new vs round-1 07 and verifier D3 (preserve this edge)

- **Round-1 07** (per the ledger note) checks *concreteness* — are assumptions/limitations phrased
  as specific, checkable statements rather than vague prose. That is a *syntactic/structural* property:
  does the sentence have a subject, a scope, a number.
- **Verifier D3** checks *explicitness* — are assumptions/limitations present and enumerated at all
  (structural presence, e.g. did the compiler produce `A1`, `A2`, ... ref-ids and a limitations list),
  not whether they are true-to-the-paper's-actual-risk-profile.
- **M30 is a semantic judgment layer on top of both**: an assumption can be maximally concrete
  ("A2: Selecting the single most comprehensive dataset per cohort yields statistically independent
  nodes") and maximally explicit (has a ref-id, sits in the Assumptions section) while still being
  *unrealistic/unfair* if, say, the paper's own cohort description shows overlapping registries that
  make that independence assumption implausible. Concreteness and explicitness are necessary but not
  sufficient; M30 is the metric that asks "concrete and explicit — but is it *true and honest*." This
  is why M30 requires [sem] (an LLM or human judgment call against domain plausibility / cross-artifact
  consistency) where 07 and D3 can be done by pattern/structure checks alone. Preserve this scoping:
  **M30's Step 1–2 below must never degrade into a concreteness/presence check** — those are already
  covered elsewhere and re-scoring them here is redundant, not net-new.

## 5. Generation / compute workflow

### 5.1 Inputs

- `logic/solution/constraints.md` — REQUIRED. Sections: `## Boundary conditions`, `## Assumptions`
  (bulleted, `A{n}: text`), `## Known limitations (§X.Y)` (bulleted, `**name**: text`), optional
  `## Additional caveats surfaced during compilation (data-quality notes)`.
- Cross-reference context (used only for the Step 4 coverage check, not for re-deriving Step 1–2):
  - `logic/problem/*.md` — cohort/design/data description (to check assumption plausibility against
    what the paper says about its own data).
  - `evidence/*` internal-consistency notes (e.g. table-vs-caption mismatches) — to check whether a
    visible internal inconsistency is acknowledged in constraints.md.
- No external [sem] calls beyond the LLM judgment calls specified below — this metric does not need
  semantic-scholar/undermind/FOL/clinical-trial lookups; the "realism" check is against the *artifact's
  own internal evidence*, not against the outside literature (external plausibility-checking is a
  different, more expensive metric and would duplicate other suite members that already do
  literature-grounding).

### 5.2 Step 0 — Availability & structural pre-check (deterministic, always runs, never skipped)

```python
import re

def parse_constraints(md_text: str) -> dict:
    """Parse constraints.md into its sections. Returns empty lists (not None) for
    absent sections -- absence is data, not an excuse to skip."""
    def section(name):
        m = re.search(rf"^##\s*{name}.*?\n(.*?)(?=^##\s|\Z)", md_text,
                       re.MULTILINE | re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""

    def bullets(block):
        return [b.strip("-* \t") for b in block.splitlines() if b.strip().startswith(("-", "*"))]

    boundary_raw = section("Boundary conditions")
    assumptions_raw = section("Assumptions")
    limitations_raw = section(r"Known limitations")
    caveats_raw = section("Additional caveats")

    assumptions = []
    for b in bullets(assumptions_raw):
        m = re.match(r"(A\d+):\s*(.*)", b)
        assumptions.append({"id": m.group(1), "text": m.group(2)} if m else {"id": None, "text": b})

    limitations = []
    for b in bullets(limitations_raw):
        m = re.match(r"\*\*(.+?)\*\*:\s*(.*)", b)
        limitations.append({"name": m.group(1), "text": m.group(2)} if m else {"name": None, "text": b})

    return {
        "present": bool(md_text.strip()),
        "boundary_conditions": bullets(boundary_raw),
        "assumptions": assumptions,
        "limitations": limitations,
        "caveats": bullets(caveats_raw),
    }


BOILERPLATE_PATTERNS = [
    r"future (work|research|studies)",
    r"further (validation|research|study)",
    r"(larger|more diverse|bigger) (sample|cohort|dataset)s?",
    r"generaliz\w* (may|might|could) (be|not)",
    r"limited by (sample size|power)\.?$",
]

def is_boilerplate_shell(text: str) -> bool:
    """Cheap deterministic pre-filter: does this sentence match a known hedge template
    with NO additional specific noun (mechanism/subgroup/number)? Used only to flag
    candidates for the [sem] judge to double-check -- never used alone to score."""
    t = text.strip().lower()
    return any(re.search(p, t) for p in BOILERPLATE_PATTERNS) and len(t.split()) < 14


def structural_floor(parsed: dict) -> float:
    """Deterministic floor multiplier in [0,1]. Penalizes missing/thin structure outright
    -- this NEVER returns None/NA; absence always maps to a low number, per penalize-
    don't-skip."""
    if not parsed["present"]:
        return 0.0  # constraints.md itself missing -- should not happen (mandatory), but
                    # if it does, floor the metric rather than skipping it.
    score = 1.0
    if len(parsed["assumptions"]) == 0:
        score *= 0.35  # no assumptions ever stated is a red flag per the shape doc
    if len(parsed["limitations"]) == 0:
        score *= 0.25  # "no limitations stated" is an explicit red flag in the shape doc
    elif len(parsed["limitations"]) == 1 and is_boilerplate_shell(parsed["limitations"][0]["text"]):
        score *= 0.4  # sole limitation present but it's a bare hedge shell
    return score
```

### 5.3 Step 1 — [sem] Assumption realism judgment

For each parsed assumption, call an LLM with the assumption text plus whatever problem-layer /
evidence-layer context is available (cohort description, design description). One call per assumption
(batchable into one call with a list, but scored per-item):

**Prompt (exact):**
```
You are auditing one stated ASSUMPTION from a compiled research paper for realism and fairness.

ASSUMPTION (verbatim from the paper's method/constraints section):
"{assumption_text}"

CONTEXT from the same paper (cohort/design/data description, evidence-layer notes; may be partial):
{context_block}

Judge this assumption on one axis: is it a REALISTIC idealization (a condition that plausibly holds,
or is honestly and precisely characterized, given what this paper's own data/method are) or a
DREAMCASE assumption (a convenient simplification that plausibly does NOT hold for this paper's
actual setting, and that -- if false -- would materially threaten the paper's conclusions)?

Respond with strict JSON:
{
  "label": "realistic" | "dreamcase" | "unclear_insufficient_context",
  "confidence": <float 0-1>,
  "conflict_with_context": "<quote or paraphrase of the specific context detail that conflicts with
     this assumption, or null if none found>",
  "rationale": "<1-2 sentences>"
}

Rules:
- Label "unclear_insufficient_context" ONLY if the context block truly gives no basis to judge --
  do not use it to avoid a judgment you find difficult.
- An assumption that is standard/unavoidable in the field (e.g. i.i.d. sampling for a randomized
  trial) is "realistic" even if technically an idealization, UNLESS this paper's own context shows
  a specific reason it doesn't hold here.
```

**Deterministic reduction of the LLM output → sub-score:**
```python
def assumption_subscore(judgment: dict) -> float:
    label = judgment["label"]
    conf = judgment["confidence"]
    if label == "realistic":
        return 0.6 + 0.4 * conf          # realistic: 0.6-1.0, scaled by confidence
    if label == "dreamcase":
        return 0.3 * (1 - conf)          # dreamcase: 0-0.3, WORSE as confidence rises
    # "unclear_insufficient_context" -- penalize (don't skip): missing context to judge
    # realism is itself a coverage gap in the artifact, not a free pass.
    return 0.35
```

### 5.4 Step 2 — [sem] Limitation genuineness judgment

For each parsed limitation:

**Prompt (exact):**
```
You are auditing one stated LIMITATION from a compiled research paper.

LIMITATION (verbatim):
"{name}: {limitation_text}"

Judge whether this limitation states a GENUINE NEW CONDITION -- a specific mechanism, subgroup,
regime, or scenario under which the paper's conclusions would plausibly NOT hold, with enough
specificity that a reader could in principle check for it or design a follow-up study targeting it
-- versus a BOILERPLATE HEDGE that is true of nearly any study in the field and adds no paper-specific
information (e.g. generic calls for larger samples, more diverse cohorts, or future validation with
no named mechanism).

Respond with strict JSON:
{
  "label": "genuine_new_condition" | "boilerplate_hedge" | "restates_an_assumption",
  "specificity_score": <float 0-1, how paper-specific/checkable this is>,
  "names_direction_or_mechanism": <true|false>,
  "rationale": "<1-2 sentences>"
}

Use "restates_an_assumption" if this "limitation" is actually just re-describing something already
listed under Assumptions rather than adding new information.
```

**Reduction:**
```python
def limitation_subscore(judgment: dict) -> float:
    label = judgment["label"]
    spec = judgment["specificity_score"]
    if label == "genuine_new_condition":
        base = 0.5 + 0.5 * spec
        return min(1.0, base + (0.1 if judgment["names_direction_or_mechanism"] else 0))
    if label == "restates_an_assumption":
        return 0.25  # non-informative even if well-written
    return 0.15 * spec  # boilerplate_hedge: near-zero regardless of how polished
```

### 5.5 Step 3 — Cross-layer coverage check (deterministic + light [sem])

```python
def coverage_gap_penalty(constraints: dict, evidence_consistency_notes: list[str]) -> float:
    """If the evidence layer already contains an internal-consistency red flag (e.g. table
    vs caption mismatch, a visibly small/skewed subgroup) that constraints.md's caveats/
    limitations never mention, that's a specific, checkable omission. Penalty in [0, 0.3]."""
    if not evidence_consistency_notes:
        return 0.0
    mentioned_text = " ".join(
        c for c in constraints["caveats"] + [l["text"] for l in constraints["limitations"]]
    ).lower()
    unmentioned = [n for n in evidence_consistency_notes
                   if not _semantically_referenced(n, mentioned_text)]  # [sem] containment check
    return min(0.3, 0.1 * len(unmentioned))

def _semantically_referenced(note: str, haystack: str) -> bool:
    # [sem]: one short LLM call — "Does this text substantively acknowledge the issue described
    # in NOTE (even if worded differently)? Answer yes/no." Cheap boolean, batchable.
    ...
```

### 5.6 Step 4 — Worst-offender guard (anti-padding)

```python
def worst_offender_cap(assumption_scores: list[float], limitation_scores: list[float]) -> float:
    """A single flagrant dreamcase assumption or single hollow-limitations-only section should
    cap the metric even if other items are fine -- prevents padding from washing out one bad
    offender via averaging (see Goodharting §3.1)."""
    worst = min(assumption_scores + limitation_scores, default=0.0)
    if worst < 0.15:
        return 0.5  # hard cap: can't exceed 0.5 if any single item is near-flagrant
    return 1.0  # no cap
```

### 5.7 Final scoring function

```python
def score_m30(constraints_md_text: str,
              problem_context: str,
              evidence_consistency_notes: list[str],
              llm_call) -> dict:
    """
    llm_call: callable(prompt: str) -> dict (parsed JSON), the [sem] interface.
    Returns a dict with the final score in [0,1] plus the component breakdown, so the
    score is always auditable -- never a bare number.
    """
    parsed = parse_constraints(constraints_md_text)
    floor = structural_floor(parsed)

    if floor == 0.0:
        return {"score": 0.0, "reason": "constraints.md missing/empty", "components": {}}

    assumption_scores = []
    for a in parsed["assumptions"]:
        prompt = ASSUMPTION_PROMPT.format(assumption_text=a["text"], context_block=problem_context)
        judgment = llm_call(prompt)
        assumption_scores.append(assumption_subscore(judgment))
    if not assumption_scores:
        assumption_scores = [0.35]  # no assumptions: penalize via a placeholder low score,
                                     # do not drop this term from the aggregate

    limitation_scores = []
    for l in parsed["limitations"]:
        prompt = LIMITATION_PROMPT.format(name=l["name"], limitation_text=l["text"])
        judgment = llm_call(prompt)
        limitation_scores.append(limitation_subscore(judgment))
    if not limitation_scores:
        limitation_scores = [0.15]  # no limitations at all: penalize hard, don't skip

    gap_penalty = coverage_gap_penalty(parsed, evidence_consistency_notes)
    cap = worst_offender_cap(assumption_scores, limitation_scores)

    mean_assumption = sum(assumption_scores) / len(assumption_scores)
    mean_limitation = sum(limitation_scores) / len(limitation_scores)

    # Limitations weighted slightly higher than assumptions: a genuine limitation is rarer
    # and more informative than a realistic assumption (which is closer to table stakes).
    raw = 0.45 * mean_assumption + 0.55 * mean_limitation
    raw -= gap_penalty
    raw = max(0.0, raw)
    raw *= floor
    final = min(raw, cap)

    return {
        "score": round(final, 3),
        "components": {
            "structural_floor": floor,
            "mean_assumption_realism": round(mean_assumption, 3),
            "mean_limitation_genuineness": round(mean_limitation, 3),
            "coverage_gap_penalty": gap_penalty,
            "worst_offender_cap": cap,
            "n_assumptions": len(parsed["assumptions"]),
            "n_limitations": len(parsed["limitations"]),
        },
    }
```

The `components` breakdown is always returned (not just the scalar) so downstream review can see
*why* a paper scored low — e.g., distinguishing "thin/absent inputs" (structural_floor) from "stated
plenty but it's all dreamcase/boilerplate" (semantic subscores) from "omitted a visible internal
inconsistency" (coverage_gap_penalty). This also makes the metric self-documenting for the
penalize-don't-skip audit: every missing/thin-input path above produces a low *number*, never a null/
"N/A" return, and the reason is always attached.

## 6. Why it's hard to Goodhart

- **Semantic judgment resists surface mimicry**: unlike concreteness (07) or explicitness (D3), which
  can be gamed by writing assumptions/limitations that merely *look* structured (numbered, specific
  nouns), M30's judges are asked directly whether the content is honest/informative, so cosmetic
  compliance (a well-formatted boilerplate sentence) does not automatically score well — see the
  boilerplate-hedge branch in §5.4, which scores near-zero regardless of specificity_score wording
  because `label` gates the range, not just a continuous feature.
- **Worst-offender cap defeats padding**: §5.6 makes it strictly worse, not neutral, to bury one
  dreamcase assumption among many fine ones — a pure average is the classic padding exploit and this
  design explicitly avoids relying on one.
- **Cross-layer coverage check makes omission partially visible**: gaming by silence (never mentioning
  the worst limitation) is checkable whenever the omission is independently visible elsewhere in the
  artifact (evidence-layer inconsistency notes); it is not perfectly closed (an omission invisible
  everywhere in the artifact is undetectable from the artifact alone, which is an honest scope
  boundary, not a design flaw a bigger prompt could fix).
- **No reward for verbosity or count**: both subscore functions are per-item and label-gated, and the
  aggregate is a mean (not a sum), so adding more items cannot inflate the score — the floor
  computation in §5.2 even penalizes the pathological case of zero items.

## 7. Composition with the rest of the suite

- **Complements round-1 07 (concreteness)** and **verifier D3 (explicitness)**: those two are cheap,
  reliable structural gates that should run first/always; M30 is the expensive semantic layer that only
  matters once structure is confirmed present. A suite ordering of "07/D3 gate structure → M30 grades
  content" avoids M30 wasting [sem] calls on artifacts that are trivially deficient (M30's own
  `structural_floor` mirrors this by shortcutting to 0.0 when constraints.md is absent).
- **Reads but does not duplicate the evidence-layer internal-consistency metric**: §5.5's coverage
  check *consumes* another metric's output (evidence-layer table/caption-mismatch flags) as a penalty
  input rather than re-deriving it, keeping the two metrics complementary instead of redundant — this
  directly addresses the assessment-critique's "redundancy/verifier-overlap" concern named in the
  brief.
- **Independent failure axis from correctness/rigor metrics elsewhere in the suite** (e.g. statistical-
  method-appropriateness metrics score whether the *analysis* is valid given the stated assumptions;
  M30 scores whether the *stated assumptions themselves* are honest). A paper can score high on "used
  the analysis correctly given its assumptions" and low on M30 (correct analysis, dishonest
  assumptions) or vice versa — these should NOT be collapsed into one number upstream of the final
  suite aggregation, since they diagnose different failure modes for a reader deciding how much to
  trust the paper.
