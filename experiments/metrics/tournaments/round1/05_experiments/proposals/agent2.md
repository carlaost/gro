# Proposer 2 — metrics for `logic/experiments.md`

Assumed parsed schema for every metric below (a list of experiment blocks parsed from the shape doc):

```python
Experiment = {
    "id": str,                       # "E03"
    "verifies": list[str],           # ["C03","C05","C06"]
    "setup": dict[str, str],         # {"Assay": "...", "Pipeline": "..."} free-form keys
    "procedure": list[str],          # numbered imperative steps, in order
    "metrics": str,                  # prose or list rendered as one string; what is measured
    "expected_outcome": list[str],   # directional/relative statements only
    "baselines": str,                # comparator description, or literal "none"
    "dependencies": list[str],       # other E## ids, or []
}
# artifact = list[Experiment], all blocks from one logic/experiments.md file
```

Where a metric needs cross-artifact information (e.g. the set of valid `C##` ids from
`claims.md`), I say so explicitly and treat that information being *unavailable* as a
penalized state, per the hard constraint — never as "skip this check."

---

## 1. Referential & Structural Closure

**How it signals good science.** A declarative experiment plan is only meaningful if it is
actually wired into the paper's claim graph: every claim it says it verifies must exist, every
dependency it says it needs must exist, and the dependency graph must be acyclic (E03 cannot
depend on E05 which depends on E03). A paper that gets this right has an experiment layer that
is a real, checkable scaffold for the argument, not decorative prose. A paper that gets it wrong
either wasn't compiled carefully or — worse — is asserting connections to claims that don't
actually exist.

**Compute function.**

```python
def referential_closure(artifact: list[dict], claim_ids: set[str] | None) -> float:
    """
    Assumes: artifact is list[Experiment] as above.
    claim_ids is the set of valid C## ids from claims.md, or None/empty if unavailable
    (unavailability is itself penalized below, per the hard constraint).
    """
    if not artifact:
        return 0.0

    exp_ids = {e["id"] for e in artifact}
    n = len(artifact)

    # (a) Verifies must resolve into claims.md's id space.
    if not claim_ids:
        verifies_score = 0.0  # can't confirm anything resolves -> penalize, don't skip
    else:
        total_refs, resolved = 0, 0
        for e in artifact:
            for cid in e.get("verifies", []):
                total_refs += 1
                if cid in claim_ids:
                    resolved += 1
        verifies_score = resolved / total_refs if total_refs else 0.0  # no Verifies at all = 0

    # (b) Dependencies must resolve within this same file.
    total_deps, resolved_deps = 0, 0
    for e in artifact:
        for did in e.get("dependencies", []):
            total_deps += 1
            if did in exp_ids and did != e["id"]:
                resolved_deps += 1
    deps_score = 1.0 if total_deps == 0 else resolved_deps / total_deps

    # (c) Dependency graph must be a DAG (no cycles).
    graph = {e["id"]: e.get("dependencies", []) for e in artifact}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {eid: WHITE for eid in exp_ids}
    has_cycle = False

    def dfs(u):
        nonlocal has_cycle
        color[u] = GRAY
        for v in graph.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                has_cycle = True
            elif color[v] == WHITE:
                dfs(v)
        color[u] = BLACK

    for eid in exp_ids:
        if color[eid] == WHITE:
            dfs(eid)
    acyclic_score = 0.0 if has_cycle else 1.0

    # (d) Claim coverage: what fraction of claims.md's ids are verified by >=1 experiment here.
    if not claim_ids:
        coverage_score = 0.0
    else:
        verified_ids = {cid for e in artifact for cid in e.get("verifies", [])}
        coverage_score = len(verified_ids & claim_ids) / len(claim_ids)

    return 0.30 * verifies_score + 0.25 * deps_score + 0.20 * acyclic_score + 0.25 * coverage_score
```

**What the function does & why.** It checks four bindings that together define whether the
experiment layer is structurally real: (a) every claim cited by `Verifies` actually exists in
`claims.md`; (b) every `Dependencies` id actually exists among this file's own experiment ids;
(c) the dependency graph has no cycles (a cyclic "proof" is not a proof); (d) the claims the
paper makes are actually covered by at least one experiment (an unverified claim is a claim
resting on nothing). Each sub-check is a fraction in [0,1], combined by weighted average, so
partial breakage produces a partial penalty rather than an all-or-nothing cliff — except where
information is simply unavailable (no `claim_ids`), which is scored as 0 rather than skipped.

**Why it's hard to Goodhart.** You cannot inflate `verifies_score` or `coverage_score` by citing
more claim ids unless those ids genuinely exist in `claims.md` — that requires actually
coordinating the claims and experiments layers, which is real compilation work, not a free
edit to one file. Adding fake `Dependencies` to look thorough risks introducing a cycle (tanking
`acyclic_score`) or a dangling id (tanking `deps_score`). And padding coverage by inventing
low-content claims just to "verify" them is caught by the falsifiability and setup-grounding
metrics below, which score the content quality of what verifies what.

---

## 2. Falsifiable Specificity of Expected Outcomes

**How it signals good science.** The shape doc requires `Expected outcome` to be
directional/relative, never a number. Good science lives in that gap: a real prediction commits
to a specific, checkable *direction* ("DEGs concentrate in white-matter and vascular SpDs")
that could turn out false. A bad-faith or lazy compile fills this field with either (i) restating
what `Metrics` already says will be measured (a tautology — "the DEG count will be measured" is
not a prediction) or (ii) hedge-everything language that can't be falsified ("results may vary
by domain"). Rewarding directional specificity and penalizing tautology/hedging rewards papers
that actually commit to testable expectations.

**Compute function.**

```python
import re
from difflib import SequenceMatcher

DIRECTIONAL = re.compile(
    r"\b(higher|lower|greater|less|increase|decrease|reduce|elevate|concentrate|enrich|"
    r"differ|exceed|outperform|correlate|associate|consistent with|dominant|dominated|"
    r"absent|present in|shift|converge|diverge)\b", re.I)
HEDGE = re.compile(
    r"\b(may|might|could|possibly|potentially|some|various|certain|to some extent|"
    r"depending on)\b", re.I)

def falsifiable_specificity(artifact: list[dict]) -> float:
    """Assumes: artifact is list[Experiment]; expected_outcome and metrics are strings/lists
    already flattened to a single string per experiment for text analysis."""
    if not artifact:
        return 0.0

    per_exp_scores = []
    for e in artifact:
        outcomes = e.get("expected_outcome", [])
        if not outcomes:
            per_exp_scores.append(0.0)  # missing outcome -> penalize, not skip
            continue

        metrics_text = " ".join(e.get("metrics", "")) if isinstance(e.get("metrics"), list) \
            else (e.get("metrics") or "")

        stmt_scores = []
        for stmt in outcomes:
            directional_hits = len(DIRECTIONAL.findall(stmt))
            hedge_hits = len(HEDGE.findall(stmt))
            # tautology check: is this outcome just a restatement of what's measured?
            similarity = SequenceMatcher(None, stmt.lower(), metrics_text.lower()).ratio()
            tautology_penalty = max(0.0, similarity - 0.5) * 2  # >0.5 similarity starts hurting

            raw = 0.6 * min(directional_hits, 2) / 2 + 0.4 * (1.0 - min(hedge_hits, 2) / 2)
            stmt_scores.append(max(0.0, raw - tautology_penalty))

        per_exp_scores.append(sum(stmt_scores) / len(stmt_scores))

    return sum(per_exp_scores) / len(per_exp_scores)
```

**What the function does & why.** For each experiment, each `Expected outcome` statement is
scored on three axes: does it use directional/comparative vocabulary (reward), does it hedge
with non-committal language (penalize), and is it merely a paraphrase of the `Metrics` field
rather than a genuine prediction about direction (penalize via string-similarity check). Missing
`Expected outcome` entirely scores 0 for that experiment, satisfying the hard constraint. The
per-statement scores are averaged per experiment, then across experiments, so one strong
experiment can't hide many weak ones.

**Why it's hard to Goodhart.** Stuffing outcomes with directional buzzwords ("increase",
"differ") without engaging with the actual measured quantity raises `directional_hits` but, if
those buzzwords just echo the `Metrics` field's own vocabulary, the tautology penalty via
`SequenceMatcher` catches the restatement. Removing hedges by asserting maximal confidence on
every outcome is fine scientifically (that's the point) but only works if the outcome is
genuinely distinct from the metric description — cheap paraphrase-and-reverse tricks still trip
the similarity threshold.

---

## 3. Baseline Rigor

**How it signals good science.** `Baselines` is where a paper commits to what it's actually
being tested *against*. Per the hard constraint, `baselines: none` is not a neutral state to
skip — it must be scored down, because comparator-free evidence is inherently weaker evidence,
even when a within-study design offers some justification. Among populated baselines, a rigorous
paper names a specific comparator (a named reference standard, dataset, prior method, or
reference cohort) rather than a generic gesture ("standard comparison", "typical approach").

**Compute function.**

```python
GENERIC_BASELINE_TERMS = re.compile(
    r"^\s*(none|n/?a|standard|typical|usual|baseline|comparison)\.?\s*$", re.I)
SPECIFIC_TOKEN = re.compile(r"[A-Z][A-Za-z0-9_\-]{2,}|GRCh\d+|p\d{3}|v\d+(\.\d+)*")

def baseline_rigor(artifact: list[dict]) -> float:
    """Assumes: artifact is list[Experiment]; baselines is a string, possibly 'none'."""
    if not artifact:
        return 0.0

    scores = []
    for e in artifact:
        baseline = (e.get("baselines") or "").strip()
        if not baseline or GENERIC_BASELINE_TERMS.match(baseline):
            scores.append(0.15)  # absent/generic is penalized, not skipped
            continue

        # reward named, specific comparators: proper nouns, codes, versioned references
        specific_tokens = len(set(SPECIFIC_TOKEN.findall(baseline)))
        word_count = max(len(baseline.split()), 1)
        density = specific_tokens / word_count

        # a bare "within-study comparison across X" is more specific than "none" but
        # still weaker than a named external comparator -- reward named external referents more
        has_external_referent = bool(re.search(r"\b(vs\.?|reference|prior|external|cohort|"
                                                 r"comparator|control group|historical)\b",
                                                 baseline, re.I))

        score = 0.35 + 0.35 * min(density * 4, 1.0) + 0.30 * (1.0 if has_external_referent else 0.0)
        scores.append(min(score, 1.0))

    return sum(scores) / len(scores)
```

**What the function does & why.** It classifies each experiment's `Baselines` field: empty or
generic placeholder text gets a low floor score (0.15, not 0 and not skipped — it's a real but
weak signal, since some genuinely comparator-free designs exist but the hard constraint still
requires penalizing thinness). Non-generic baselines are scored by density of specific tokens
(proper nouns, versioned references, codes like `p181_IA`) and whether the text names an
external referent (a real comparator group/method) versus only an internal structural
comparison. This rewards papers that actually specify what they're testing against.

**Why it's hard to Goodhart.** Simply typing a longer sentence doesn't help — the score is
token-*density* and named-referent detection, not length. Inventing a fake-sounding specific
baseline name (e.g., a made-up reference cohort) to farm the specific-token bonus is possible in
isolation, but a fabricated comparator with no real basis tends to also be unsupported by
`Setup`/`Procedure` detail (metric 5 below penalizes generic, non-integrated setups), so a
fabricated baseline that isn't backed by matching methodological detail elsewhere gets caught
there.

---

## 4. Declarative Purity (numeric-leakage defect detector)

**How it signals good science.** The shape doc states a hard invariant: no exact numerical
results anywhere in `logic/experiments.md` — those belong only in `evidence/`. A paper that
leaks a result number into `Expected outcome` or `Metrics` ("achieves 92% accuracy" instead of
"achieves higher accuracy than baseline") has violated the separation between *plan* and
*result*, which is itself evidence of a sloppier, less disciplined compile (or an attempt to
smuggle a favorable-sounding number past the declarative-plan discipline). This is a defect
detector, not a positive-construction metric: fewer leaks is straightforwardly better science
communication.

**Compute function.**

```python
THRESHOLD_CONTEXT = re.compile(
    r"(FDR|p|alpha|q)\s*[<>≤≥]\s*0?\.\d+|CI\s*[:=]?\s*\[?[\d.]+", re.I)
RESULT_NUMBER = re.compile(
    r"\b\d{1,3}(\.\d+)?\s*%|"                       # bare percentages
    r"\b(achiev|reach|obtain|yield|record|score[ds]?)\w*\s+(a\s+|an\s+)?\d|"  # "achieved 92"
    r"\bn\s*=\s*\d+\b|"                              # exact sample-size-as-result
    r"\bincreas\w*\s+by\s+\d|\bdecreas\w*\s+by\s+\d",
    re.I)

def declarative_purity(artifact: list[dict]) -> float:
    """Assumes: artifact is list[Experiment]; checks Expected outcome and Metrics text only
    (Setup/Procedure may legitimately contain design numbers like sample sizes, doses)."""
    if not artifact:
        return 0.0

    total_fields, violations = 0, 0
    for e in artifact:
        fields_to_check = list(e.get("expected_outcome", []))
        metrics = e.get("metrics", "")
        fields_to_check.append(metrics if isinstance(metrics, str) else " ".join(metrics))

        for text in fields_to_check:
            total_fields += 1
            if not text:
                continue
            # strip legitimate design-threshold statements before checking for leaked results
            scrubbed = THRESHOLD_CONTEXT.sub("", text)
            if RESULT_NUMBER.search(scrubbed):
                violations += 1

    if total_fields == 0:
        return 0.0  # no checkable content at all -> penalize
    return 1.0 - (violations / total_fields)
```

**What the function does & why.** It scans only the two fields the shape doc says must never
contain exact numbers (`Expected outcome`, `Metrics`), first removing legitimate
threshold/decision-rule patterns (`FDR<0.05`, `p<0.05`, CIs used as *design* specification) so
those aren't falsely flagged, then searching the remainder for patterns that look like leaked
results — bare percentages, "achieved/scored N", exact `n=` used as a result rather than a
design parameter, "increased by N". The score is the fraction of checked fields with no leakage.
Zero checkable content (an empty file) is penalized to 0, not skipped.

**Why it's hard to Goodhart.** The obvious gaming move — scrub every number to guarantee a
perfect score — removes real design information along with it, but real design information
(thresholds, protocol parameters) is exactly what the setup-grounding metric (#5) rewards in
`Setup`. So over-scrubbing numbers to win this metric costs specificity points elsewhere. And
since threshold-style numbers are explicitly whitelisted, a paper doesn't need to hide legitimate
statistical design choices to score well here — only actual leaked results.

---

## 5. Setup/Procedure Operational Grounding (with cross-experiment redundancy check)

**How it signals good science.** A real experiment plan reads as if someone who actually ran
(or deeply understands) the study wrote it: `Setup` uses genre-appropriate, populated fields
with concrete named tools/parameters/versions, and `Procedure` steps are specific imperative
actions, not generic filler. The shape doc explicitly flags the opposite failure mode:
"abstract-only compilation" produces the statutory minimum experiments with "generic,
interchangeable Procedure steps ... visibly less specific" than a real compile. A distinguishing
symptom of that failure mode is that procedures across *different* experiments start to read as
near-duplicates of each other, because they were all inferred from the same one-sentence method
description rather than from genuinely different pipeline stages.

**Compute function.**

```python
from difflib import SequenceMatcher

CONCRETE_TOKEN = re.compile(
    r"[A-Z][A-Za-z0-9]*[A-Z0-9][A-Za-z0-9]*|"     # CamelCase / acronym tool names (SpaceRanger)
    r"\bv?\d+(\.\d+)+\b|"                          # versions (2020-A style handled loosely)
    r"\b[A-Za-z]+\d+[A-Za-z]*\b")                  # alnum codes (GRCh38, chrM)

GENERIC_STEP = re.compile(
    r"^\s*(analyze|process|evaluate|assess|examine)\s+(the\s+)?data\.?\s*$", re.I)

def setup_procedure_grounding(artifact: list[dict]) -> float:
    """Assumes: artifact is list[Experiment]; setup is dict[str,str], procedure is list[str]."""
    if not artifact:
        return 0.0

    exp_scores = []
    procedures_joined = []

    for e in artifact:
        setup = e.get("setup", {})
        procedure = e.get("procedure", [])

        if not setup:
            setup_score = 0.0  # missing Setup -> penalize
        else:
            populated = [v for v in setup.values() if v and len(v.strip()) > 3]
            concrete_hits = sum(len(CONCRETE_TOKEN.findall(v)) for v in populated)
            setup_score = min(1.0, 0.4 * (len(populated) / max(len(setup), 1))
                               + 0.6 * min(concrete_hits / max(len(populated), 1), 2) / 2)

        if not procedure:
            proc_score = 0.0  # missing Procedure -> penalize
        else:
            generic_steps = sum(1 for step in procedure if GENERIC_STEP.match(step))
            specific_steps = sum(1 for step in procedure if len(step.split()) >= 6)
            proc_score = max(0.0, (specific_steps - generic_steps) / len(procedure))

        exp_scores.append(0.5 * setup_score + 0.5 * proc_score)
        procedures_joined.append(" ".join(procedure))

    base_score = sum(exp_scores) / len(exp_scores)

    # cross-experiment redundancy penalty: near-duplicate procedures across different
    # experiments is the "abstract-only compilation" tell.
    n = len(procedures_joined)
    if n < 2:
        redundancy_penalty = 0.0
    else:
        sims = []
        for i in range(n):
            for j in range(i + 1, n):
                if procedures_joined[i] and procedures_joined[j]:
                    sims.append(SequenceMatcher(None, procedures_joined[i],
                                                 procedures_joined[j]).ratio())
        avg_sim = sum(sims) / len(sims) if sims else 0.0
        redundancy_penalty = max(0.0, avg_sim - 0.4) * 1.5  # duplication above 0.4 similarity hurts

    return max(0.0, base_score - redundancy_penalty)
```

**What the function does & why.** Per experiment, it scores `Setup` on breadth (how many of its
declared fields are actually populated with non-trivial content) and concreteness (density of
named tools/versions/codes like `SpaceRanger`, `GRCh38`), and scores `Procedure` on how many
steps are genuinely specific imperative actions versus generic filler ("analyze the data").
It then adds an artifact-level penalty: it pairwise-compares every experiment's procedure text
against every other's, and if procedures across *different* experiments (which should describe
different pipeline stages/analyses) are suspiciously similar on average, it penalizes the whole
artifact — this directly targets the shape doc's named failure mode of interchangeable,
abstract-inferred procedures.

**Why it's hard to Goodhart.** Padding `Setup` with long but vague text doesn't help because the
score rewards *concrete-token density*, not raw length. Writing elaborate, verbose procedure
steps to dodge the `GENERIC_STEP` regex is possible per-experiment, but if the same elaborate
verbosity is reused (even reworded superficially) across experiments that are supposed to
describe distinct stages, the cross-experiment `SequenceMatcher` redundancy check catches the
pattern — you cannot cheaply generate N experiments that are each individually detailed *and*
collectively distinct without doing the real methodological work of having N distinct stages.

---

## Combination

These five metrics are chained so that gaming one tends to break another. Padding the artifact
with extra experiment/claim ids to inflate **Referential Closure**'s coverage score requires
generating real, distinct experiment content — but any resulting near-duplicate, low-effort
blocks get caught by **Setup/Procedure Grounding**'s cross-experiment redundancy check and by
weak, tautological outcomes under **Falsifiable Specificity**. Trying to make a thin experiment
*look* rigorous by inventing a plausible-sounding numeric result ("reaches 90% concordance")
trips **Declarative Purity**; scrubbing all numbers to avoid that instead strips out the
legitimate design-threshold detail that **Setup Grounding** rewards. Dodging the cost of a real
comparator by writing `baselines: none` is directly penalized by **Baseline Rigor**, while
faking a specific-sounding comparator name without matching methodological detail is exposed by
**Setup Grounding**'s concreteness check finding no supporting infrastructure for it. In short: a
paper can't cheaply satisfy structural completeness, numeric cleanliness, outcome specificity,
comparator rigor, and methodological distinctiveness all at once without an experiment layer
that reflects genuinely separate, real, falsifiable analyses.
