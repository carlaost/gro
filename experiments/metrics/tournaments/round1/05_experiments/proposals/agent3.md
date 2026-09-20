# Proposer 3 — metrics for `logic/experiments.md`

Assumed parsed representation for all functions below: a list of experiment dicts,
```python
# experiments: List[dict], each dict has keys:
#   "id": str                      # e.g. "E03"
#   "verifies": List[str]          # claim ids, e.g. ["C03","C05"]
#   "setup": Dict[str, str]        # free-form subkeys -> value strings
#   "procedure": List[str]         # numbered imperative steps, in order
#   "metrics": str                 # prose or joined list, what is measured
#   "expected_outcome": List[str]  # directional claims, never exact numbers
#   "baselines": str               # comparator description or "none"
#   "dependencies": List[str]      # other E## ids, or []
```
A missing/empty field is represented as `""`, `[]`, or `{}` — never absent from the dict.

---

## 1. Numeric-Leakage Discipline

**How it signals good science.** `experiments.md` is a *pre-registration-style* plan: it must commit to what will be measured and which direction the result should point *before* stating the result itself. A paper that leaks an exact number ("achieves 92% accuracy") into `Metrics`/`Expected outcome` is retro-fitting its plan to a result it already has — the plan stopped being a real ex-ante commitment. Clean separation of plan-language from result-language is itself evidence the plan was written to constrain the analysis, not narrate it after the fact.

**Compute function.**
```python
import re

# Assumption: each experiment dict has "metrics" (str) and "expected_outcome" (List[str]).
# Assumption: acceptable numeric patterns (decision-rule thresholds, not results) are
# excluded: FDR/p-value/alpha thresholds and CIs stated as the test's own cutoff.
_THRESHOLD_OK = re.compile(
    r'(FDR|p|alpha|q)\s*[<>=]\s*0?\.\d+|95%\s*CI', re.IGNORECASE
)
_NUMBER = re.compile(r'\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\b')

def numeric_leakage_discipline(experiments):
    if not experiments:
        return 0.0
    per_exp_scores = []
    for exp in experiments:
        text_fields = [exp.get("metrics", "") or ""] + list(exp.get("expected_outcome", []) or [])
        joined = " ".join(text_fields)
        if not joined.strip():
            per_exp_scores.append(0.0)  # missing content -> penalized, not skipped
            continue
        # strip acceptable threshold mentions before counting leaked numbers
        stripped = _THRESHOLD_OK.sub("", joined)
        leaks = len(_NUMBER.findall(stripped))
        words = max(len(joined.split()), 1)
        leak_rate = leaks / words
        per_exp_scores.append(max(0.0, 1.0 - min(leak_rate * 20, 1.0)))
    return sum(per_exp_scores) / len(per_exp_scores)
```

**What the function does & why.** For every experiment it pools the `Metrics` and `Expected outcome` text, strips out numeric mentions that are legitimate design parameters (significance thresholds, stated CIs used as the test's decision rule), then counts remaining bare numbers/percentages. It converts leak density into a 0–1 score per experiment (more leaked numbers → lower score) and averages across the artifact. An experiment with empty `Metrics`/`Expected outcome` scores 0 — silence is not neutral, it's a missing-plan defect under the hard constraint.

**Why it's hard to Goodhart.** The cheap gaming move — deleting all numbers from these fields — doesn't help a paper score well elsewhere: metric #2 below explicitly *rewards* directional/comparative language, which real, informative predictions tend to carry alongside legitimate design numbers (thresholds), so an author who strips too aggressively to dodge leakage detection also strips the specificity that #2 and #3 reward. Authors can't simultaneously maximize "no numbers at all" and "richly specific, falsifiable, comparative prediction."

---

## 2. Falsifiability / Directionality Score

**How it signals good science.** Good science states a prediction sharp enough to be wrong. `Expected outcome` should read like a hypothesis ("DEGs concentrate in white-matter SpDs; ancestry-specific sets differ") not a hedge ("results may show interesting patterns depending on data"). The presence of comparative/directional predicates (higher/lower/concentrate/differ/no effect/enriched/absent-in) is a proxy for a falsifiable commitment; vague hedge language is a proxy for a plan that can't be wrong, and can't be wrong is not testable.

**Compute function.**
```python
import re

# Assumption: exp["expected_outcome"] is List[str] of directional/prose predictions.
_DIRECTIONAL = re.compile(
    r'\b(higher|lower|greater|fewer|more|less|increase[sd]?|decrease[sd]?|'
    r'concentrat\w*|differ\w*|enrich\w*|dominant|dominated|absent|reduce[sd]?|'
    r'no (effect|difference|change)|outperform\w*|underperform\w*|correlat\w*)\b',
    re.IGNORECASE,
)
_HEDGE = re.compile(
    r'\b(may|might|could|possibly|potentially|some|various|interesting|'
    r'certain|depending|appropriate|as needed|to be determined)\b',
    re.IGNORECASE,
)

def falsifiability_score(experiments):
    if not experiments:
        return 0.0
    scores = []
    for exp in experiments:
        outcomes = exp.get("expected_outcome", []) or []
        if not outcomes:
            scores.append(0.0)
            continue
        joined = " ".join(outcomes)
        n_dir = len(_DIRECTIONAL.findall(joined))
        n_hedge = len(_HEDGE.findall(joined))
        n_statements = max(len(outcomes), 1)
        raw = (n_dir - n_hedge) / n_statements
        scores.append(max(0.0, min(raw, 1.0)))
    return sum(scores) / len(scores)
```

**What the function does & why.** Counts directional/comparative predicate hits versus hedge-word hits within each experiment's `Expected outcome`, normalizes by number of outcome statements, and clamps to [0,1]. Experiments with no outcome statements score 0 (mandatory field, missing = penalized). A plan dense in "concentrates," "differs," "no effect" scores high; one dense in "may," "possibly," "depending" scores low or zero.

**Why it's hard to Goodhart.** An author can sprinkle directional words cheaply ("X is higher than Y") without real content, but that move only inflates this one axis — it does nothing for metric #3 (which demands the *procedure* actually be specific enough to produce that comparison) or metric #4 (dependency/verification structure). A fake directional claim decoupled from a concrete procedure is exposed by cross-checking against #3's low score, and the "Combination" paragraph below makes this pairing explicit.

---

## 3. Procedure Executability Density

**How it signals good science.** A `Procedure` step that names a specific method, tool, model, parameter, or reference standard ("Fit carrier model `~0 + APOE_syn + Sex + Age`", "SpaceRanger (GRCh38, 2020-A)") is one a third party could actually attempt to reproduce. A step that says "analyze the data" or "perform statistical tests" is unfalsifiable filler — it could describe any study. Executability density (named, checkable operations per step) is a direct proxy for whether the plan actually constrains what happens next, which is a precondition for reproducibility and for the plan being falsifiable at all.

**Compute function.**
```python
import re

# Assumption: exp["procedure"] is List[str], each an imperative step (numbered list flattened).
_NAMED_TOKEN = re.compile(
    r'([A-Z][a-zA-Z0-9]{2,}|`[^`]+`|\b\d+(\.\d+)?[a-zA-Z%]*\b|\b[A-Za-z]+\d[A-Za-z0-9]*\b)'
)
_GENERIC_VERBS = re.compile(
    r'^\s*(analyze|assess|evaluate|examine|investigate|study|process|review)\b',
    re.IGNORECASE,
)

def procedure_executability(experiments):
    if not experiments:
        return 0.0
    scores = []
    for exp in experiments:
        steps = exp.get("procedure", []) or []
        if not steps:
            scores.append(0.0)
            continue
        step_scores = []
        for step in steps:
            named_hits = len(_NAMED_TOKEN.findall(step))
            words = max(len(step.split()), 1)
            density = named_hits / words
            is_generic_lead = bool(_GENERIC_VERBS.match(step))
            s = min(density * 5, 1.0)
            if is_generic_lead and named_hits == 0:
                s = 0.0
            step_scores.append(s)
        scores.append(sum(step_scores) / len(step_scores))
    return sum(scores) / len(scores)
```

**What the function does & why.** For each procedure step it counts "named tokens" — capitalized proper nouns, backtick-quoted formulas/code, version/parameter-like tokens (`GRCh38`, `2020-A`) — as a proxy for concrete, checkable content, normalizes by step length, and zeroes out steps that open with a bare generic verb ("analyze...") and contain no named content at all. It averages step scores per experiment, then averages across experiments. Missing `Procedure` scores 0.

**Why it's hard to Goodhart.** Padding steps with random capitalized words or tool names not actually used would inflate this score, but such fabricated specificity is exposed jointly by `Setup` consistency (an experiment claiming to run "SpaceRanger" with no `Setup.Pipeline`/`Setup.Assay` mentioning it is internally incoherent) and by metric #4's dependency check, which rewards procedures that plausibly build on one another rather than freestanding jargon-drops. Cheap jargon injection into isolated, dependency-less experiments doesn't help the joint score.

---

## 4. Cross-Reference & Dependency Structure Integrity

**How it signals good science.** Real multi-stage research has *structure*: later analyses build on earlier ones (`Dependencies: E02`), and every experiment is tied to a specific claim it exists to test (`Verifies: C03, C05`). An artifact where every experiment is verified-and-isolated with no dependencies, or where dependency/verification references dangle (point to ids that don't exist in this same file), signals either a flat abstract-only compilation (Seal Level 1's documented failure mode) or a structurally broken extraction. This metric rewards a **valid, resolving, non-trivial dependency graph** and claim coverage.

**Compute function.**
```python
def dependency_structure_integrity(experiments):
    # Assumption: exp["id"], exp["verifies"] (List[str]), exp["dependencies"] (List[str]).
    if not experiments:
        return 0.0
    ids = {e["id"] for e in experiments}
    n = len(experiments)

    dangling = 0
    total_dep_refs = 0
    has_any_dependency_edge = False
    unverified = 0

    # cycle check via DFS
    graph = {e["id"]: list(e.get("dependencies", []) or []) for e in experiments}
    visiting, visited, cyclic = set(), set(), False

    def dfs(node):
        nonlocal cyclic
        if node in visiting:
            cyclic = True
            return
        if node in visited or node not in graph:
            return
        visiting.add(node)
        for nxt in graph[node]:
            dfs(nxt)
        visiting.discard(node)
        visited.add(node)

    for e in experiments:
        deps = e.get("dependencies", []) or []
        for d in deps:
            total_dep_refs += 1
            if d not in ids:
                dangling += 1
            else:
                has_any_dependency_edge = True
        if not e.get("verifies", []):
            unverified += 1
        dfs(e["id"])

    dangling_rate = dangling / total_dep_refs if total_dep_refs else 0.0
    unverified_rate = unverified / n
    # a purely flat graph (zero edges) across >=3 experiments is itself suspicious
    flatness_penalty = 0.0 if has_any_dependency_edge or n < 3 else 0.4

    score = 1.0
    score -= 0.5 * dangling_rate
    score -= 0.4 * unverified_rate
    score -= flatness_penalty
    score -= 0.3 if cyclic else 0.0
    return max(0.0, score)
```

**What the function does & why.** Builds the id set and dependency graph from the artifact alone (no external `claims.md` needed — dangling `Dependencies` are checked against ids *within this file*, per the shape doc's own cross-binding rule), penalizes dangling dependency refs, penalizes experiments with an empty `Verifies` list, penalizes a totally flat graph (no experiment depends on any other) once there are enough experiments that a real pipeline should show structure, and penalizes cycles (which are never legitimate in a procedural pipeline). It returns a floor-clamped composite in [0,1].

**Why it's hard to Goodhart.** Adding fake `Dependencies` edges to look structured risks creating a cycle (heavily penalized) or pointing at a nonexistent id (dangling, penalized); adding real-looking sequential ids (E01→E02→E03→...) as a pure formality is caught in combination with #3, since a manufactured dependency chain with no corresponding procedural continuity (later steps don't actually reference or use earlier steps' outputs) will show low `Setup`/`Procedure` coherence — something a semantic reviewer or companion consistency metric can flag, and which this metric alone can't be gamed into faking without that visible procedural echo.

---

## Combination

These four metrics are jointly hard to game because each targets a different axis of the same underlying discipline, and cheap gaming moves on one axis actively damage another. Stripping numbers to win Numeric-Leakage Discipline (#1) removes exactly the kind of concrete, quantified design language that Procedure Executability (#3) rewards. Inflating Falsifiability (#2) with generic directional words ("X is higher than Y") without real methodological grounding is exposed by low Procedure Executability (#3), since a genuine directional prediction should trace to a specific measurement procedure capable of producing it. Padding Procedure steps with unearned jargon to win #3 is exposed by Dependency Structure Integrity (#4), which checks whether experiments actually chain together into a coherent pipeline rather than reading as isolated jargon-dense islands. And fabricating dependency edges to win #4 risks dangling references or cycles, both directly penalized, or produces a structurally-connected-but-content-empty pipeline that #2 and #3 independently catch. A paper that is genuinely well-designed — sharp, falsifiable, procedurally concrete, and structurally coherent — scores well on all four at once; a paper gaming any single axis pays a visible cost on at least one of the others.
