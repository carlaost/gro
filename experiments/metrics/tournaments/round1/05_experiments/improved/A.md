# Proposer 2 (improved) — metrics for `logic/experiments.md`

## Changes from stage 1

Judge ranked this proposal #1 of 4 and named it a winner, but flagged four concrete weaknesses.
Each is fixed at the compute level, not just re-argued in prose:

1. **Falsifiable Specificity — closed the "lexically-distinct-but-vacuous" gap.** The old
   tautology check only penalized outcomes that were *string-similar* to `Metrics`. That let a
   gamer write confident, directional-sounding prose that shares no vocabulary with `Metrics` at
   all — lexically "distinct," but unrelated to anything actually measured, so it was never a
   real prediction either. Added a **quantity-grounding** check: an outcome must share at least
   one concrete, non-stopword token (a named quantity/entity) with `Metrics` — reused directly
   from agent4's traceability idea, per the judge's suggestion — scored as a *triangular* function
   of token overlap so both extremes are punished: zero shared vocabulary (unrelated, ungrounded
   prediction) and near-total overlap (tautological restatement) both score low; moderate,
   genuine overlap (same named quantity, different — directional — claim about it) scores high.
2. **Referential Closure — coverage gaming is now caught in the same function, not deferred to
   prose.** Added a per-experiment `richness` gate computed inline (populated `Setup` fields +
   non-trivial `Procedure` steps) that discounts how much credit a `Verifies`/coverage claim earns
   if the experiment backing it is thin. Citing five trivial claims from one two-line experiment
   no longer buys full coverage credit — the credit is scaled by the citing experiment's own
   richness, so the padding move is caught by *this* metric's own arithmetic, not merely "assumed
   caught elsewhere."
3. **Referential Closure — explicit partial-availability degradation.** Replaced the
   binary `claim_ids present/absent` branch with a `claims_availability: float` fraction
   (1.0 = `claims.md` fully parsed, 0.0 = fully unavailable, anything between = a partially
   parsed/corrupted claims file). `verifies_score` and `coverage_score` are scaled by this
   fraction directly, so degradation is proportional and explicit rather than an
   all-or-nothing branch — satisfying "penalize, never skip" at every point along that
   continuum, not just at the two endpoints.
4. **Referential Closure — cycle detection now a hard gate, not a soft 20% weight.** A single
   dependency cycle used to only zero out one of four weighted terms (worth 20%), so a paper
   could still clear ~0.8 on this metric with a cyclic "proof." Cycle detection is now also
   applied as a multiplicative cap on the whole metric (`min(metric, 0.25)` if any cycle exists),
   since a cyclic dependency graph is a logical defect no partial credit elsewhere should be able
   to outweigh.
5. **Baseline Rigor — named comparator must recur in `Setup`/`Procedure`, computed, not argued.**
   The old `SPECIFIC_TOKEN` proper-noun/version regex rewarded any specific-looking string,
   including an invented one with no methodological backing (the judge noted this was
   "surface-farmable"). Added a **corroboration check**: specific tokens found in `Baselines` are
   now cross-checked against the same experiment's `Setup` values and `Procedure` text; only
   tokens that recur there count toward the specificity bonus. A comparator name that appears
   nowhere else in the experiment's own methodological detail is now scored as if it were generic.

Everything else (Declarative Purity, and the parts of Referential Closure / Falsifiable
Specificity / Baseline Rigor / Setup-Procedure Grounding not called out above) is unchanged from
stage 1 — the judge raised no correctness or Goodhart concerns there.

Assumed parsed schema for every metric below (a list of experiment blocks parsed from the shape
doc) — unchanged from stage 1:

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
actually exist. Crucially, "wired in" should mean wired in by *substantial* experiments — an
experiment that claims to verify five claims in one throwaway sentence is not the same
achievement as one that actually does the methodological work for each, so coverage credit is
now weighted by how developed the citing experiment actually is.

**Compute function.**

```python
def referential_closure(
    artifact: list[dict],
    claim_ids: set[str] | None,
    claims_availability: float = 1.0,
) -> float:
    """
    Assumes: artifact is list[Experiment] as above.
    claim_ids: the set of valid C## ids from claims.md (empty/None if totally unavailable).
    claims_availability: fraction of claims.md that was actually parseable, in [0, 1].
        1.0 = fully available; 0.0 = fully unavailable (claims.md missing/unparseable);
        a value in between = a corrupted/partial claims.md where only some blocks parsed.
        This makes degradation explicit and continuous rather than a binary branch:
        the less of claims.md we could confirm, the less credit any Verifies/coverage
        claim can earn -- never a skip, always a proportional penalty.
    """
    if not artifact:
        return 0.0

    exp_ids = {e["id"] for e in artifact}
    n = len(artifact)

    def richness(e: dict) -> float:
        """Inline richness gate: how developed is this experiment's own content?
        Used to discount Verifies/coverage credit earned by thin experiments, so
        citing many claims from a one-line block no longer buys full credit --
        this is the compute-level fix for 'coverage padding via trivial claims'."""
        setup = e.get("setup", {})
        procedure = e.get("procedure", [])
        setup_signal = min(1.0, len([v for v in setup.values() if v and len(v.strip()) > 3]) / 2)
        proc_signal = min(1.0, len([s for s in procedure if len(s.split()) >= 6]) / 2)
        return 0.5 * setup_signal + 0.5 * proc_signal

    exp_richness = {e["id"]: richness(e) for e in artifact}

    # (a) Verifies must resolve into claims.md's id space, weighted by citing-experiment richness.
    if not claim_ids or claims_availability <= 0.0:
        verifies_score = 0.0  # can't confirm anything resolves -> penalize, don't skip
    else:
        total_weight, resolved_weight = 0.0, 0.0
        for e in artifact:
            w = max(exp_richness[e["id"]], 0.05)  # thin experiments still count, but barely
            for cid in e.get("verifies", []):
                total_weight += w
                if cid in claim_ids:
                    resolved_weight += w
        verifies_score = (resolved_weight / total_weight if total_weight else 0.0) * claims_availability

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

    # (d) Claim coverage: what fraction of claims.md's ids are verified by >=1 SUBSTANTIAL
    # experiment here. A claim "covered" only by a thin, low-richness experiment gets partial
    # credit, not full credit -- this is the compute-level anti-padding fix.
    if not claim_ids or claims_availability <= 0.0:
        coverage_score = 0.0
    else:
        best_richness_per_claim: dict[str, float] = {}
        for e in artifact:
            w = max(exp_richness[e["id"]], 0.05)
            for cid in e.get("verifies", []):
                if cid in claim_ids:
                    best_richness_per_claim[cid] = max(best_richness_per_claim.get(cid, 0.0), w)
        covered_weight = sum(best_richness_per_claim.values())
        coverage_score = (covered_weight / len(claim_ids)) * claims_availability

    base = 0.30 * verifies_score + 0.25 * deps_score + 0.20 * acyclic_score + 0.25 * coverage_score

    # A cyclic dependency graph is a logical defect that no amount of partial credit
    # elsewhere should be able to outweigh -- hard cap, not just a 20%-weighted soft term.
    if has_cycle:
        base = min(base, 0.25)

    return base
```

**What the function does & why.** It checks four bindings that together define whether the
experiment layer is structurally real: (a) every claim cited by `Verifies` actually exists in
`claims.md`, weighted so a thin, low-content experiment's citations count for less than a
well-developed one's; (b) every `Dependencies` id actually exists among this file's own
experiment ids; (c) the dependency graph has no cycles (a cyclic "proof" is not a proof); (d) the
claims the paper makes are actually covered by at least one *substantial* experiment, not merely
name-checked by a throwaway block. Each sub-check is a fraction in [0,1], combined by weighted
average, so partial breakage produces a partial penalty rather than an all-or-nothing cliff. Where
`claims.md` is only partially parseable, `claims_availability` degrades the two claim-dependent
terms proportionally rather than as an all-or-nothing branch — still a penalty at every point on
that continuum, never a skip. A cycle additionally hard-caps the whole metric at 0.25 regardless
of how well everything else scores, since a cyclic dependency chain is a defect no other strength
should be able to buy back.

**Why it's hard to Goodhart.** You cannot inflate `verifies_score` or `coverage_score` by citing
more claim ids unless those ids genuinely exist in `claims.md` — that requires actually
coordinating the claims and experiments layers, which is real compilation work, not a free
edit to one file. The richness weighting closes the remaining gap the judge flagged: inventing
trivial claims and citing them from a bare-bones experiment no longer earns full coverage credit,
because the credit itself is scaled by how developed the citing experiment is — this is now
enforced by this function's own arithmetic, not merely assumed to be caught by a sibling metric.
Adding fake `Dependencies` to look thorough risks introducing a cycle (which now hard-caps the
entire metric at 0.25, not just docking 20%) or a dangling id (tanking `deps_score`).

---

## 2. Falsifiable Specificity of Expected Outcomes

**How it signals good science.** The shape doc requires `Expected outcome` to be
directional/relative, never a number. Good science lives in that gap: a real prediction commits
to a specific, checkable *direction about a specific measured quantity* ("DEGs concentrate in
white-matter and vascular SpDs") that could turn out false. A bad-faith or lazy compile fills this
field with one of three failure modes: (i) restating what `Metrics` already says will be measured
(a tautology — "the DEG count will be measured" is not a prediction), (ii) hedge-everything
language that can't be falsified ("results may vary by domain"), or (iii) confident, fluent,
directional-sounding prose that is simply *about something else* — lexically distinct from
`Metrics` so it dodges a naive similarity check, but ungrounded in anything the experiment
actually measures, and therefore just as vacuous as a tautology. Rewarding directional specificity
*tied to a real measured quantity*, and penalizing tautology, hedging, and ungroundedness alike,
rewards papers that actually commit to testable expectations about their own data.

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
STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "for", "to", "with", "will",
    "be", "is", "are", "than", "that", "this", "these", "those", "as", "at", "by",
    "per", "across", "between", "into", "from", "than", "not", "than",
}

def _content_tokens(text: str) -> set[str]:
    return {
        w for w in re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{3,}", text.lower())
        if w not in STOPWORDS
    }

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
        metrics_tokens = _content_tokens(metrics_text)

        stmt_scores = []
        for stmt in outcomes:
            directional_hits = len(DIRECTIONAL.findall(stmt))
            hedge_hits = len(HEDGE.findall(stmt))

            # tautology check: is this outcome just a restatement of what's measured?
            similarity = SequenceMatcher(None, stmt.lower(), metrics_text.lower()).ratio()
            tautology_penalty = max(0.0, similarity - 0.5) * 2  # >0.5 similarity starts hurting

            # quantity-grounding check (closes the "lexically-distinct-but-vacuous" gap):
            # the outcome must share at least one concrete, non-stopword token with Metrics --
            # i.e. it must be a prediction ABOUT something actually measured, not merely
            # fluent, directional-sounding prose about nothing in particular. Score this as
            # a triangular function of token overlap: zero overlap (unrelated/ungrounded) is
            # bad, near-total overlap (tautology) is also bad, moderate genuine overlap
            # (same named quantity, different directional claim about it) is the sweet spot.
            stmt_tokens = _content_tokens(stmt)
            if metrics_tokens:
                overlap = len(stmt_tokens & metrics_tokens) / max(len(stmt_tokens), 1)
            else:
                overlap = 0.0  # no Metrics content to ground against -> can't confirm, penalize
            if overlap <= 0.0:
                grounding_score = 0.0  # unrelated prediction: same failure mode as a hedge
            elif overlap <= 0.4:
                grounding_score = overlap / 0.4          # rising: 0 -> 1 as overlap: 0 -> 0.4
            else:
                grounding_score = max(0.0, 1.0 - (overlap - 0.4) / 0.6)  # falling toward tautology

            raw = (0.4 * min(directional_hits, 2) / 2
                   + 0.3 * (1.0 - min(hedge_hits, 2) / 2)
                   + 0.3 * grounding_score)
            stmt_scores.append(max(0.0, raw - tautology_penalty))

        per_exp_scores.append(sum(stmt_scores) / len(stmt_scores))

    return sum(per_exp_scores) / len(per_exp_scores)
```

**What the function does & why.** For each experiment, each `Expected outcome` statement is
scored on four axes: does it use directional/comparative vocabulary (reward), does it hedge with
non-committal language (penalize), is it merely a paraphrase of the `Metrics` field rather than a
genuine prediction (penalize via string-similarity), and — new — does it actually reference the
same named quantity that `Metrics` says will be measured, without simply restating it (the
triangular `grounding_score`). An outcome that shares no vocabulary with `Metrics` at all scores
zero on grounding even if it reads as confidently directional, closing the gap where fluent but
unrelated prose could previously pass. Missing `Expected outcome` entirely scores 0 for that
experiment, satisfying the hard constraint. Per-statement scores are averaged per experiment, then
across experiments, so one strong experiment can't hide many weak ones.

**Why it's hard to Goodhart.** Stuffing outcomes with directional buzzwords without engaging the
actual measured quantity now fails on two independent axes instead of one: the old tautology
check (if the buzzwords echo `Metrics`' own phrasing) and the new grounding check (if the
buzzwords are about a quantity `Metrics` never mentions at all). The two checks bracket the
gaming space from both sides — a gamer can no longer escape the tautology penalty simply by
picking different words, because different words that are *about nothing `Metrics` measures*
now score zero on grounding instead of slipping through. The only way to score well on both is to
write an outcome that names the same measured quantity as `Metrics` (grounding) while committing
to a genuinely different, directional claim about it (avoiding tautology) — which is exactly what
a real, falsifiable prediction requires.

---

## 3. Baseline Rigor

**How it signals good science.** `Baselines` is where a paper commits to what it's actually
being tested *against*. Per the hard constraint, `baselines: none` is not a neutral state to
skip — it must be scored down, because comparator-free evidence is inherently weaker evidence,
even when a within-study design offers some justification. Among populated baselines, a rigorous
paper names a specific comparator (a named reference standard, dataset, prior method, or
reference cohort) rather than a generic gesture ("standard comparison", "typical approach") --
and that named comparator should actually be load-bearing in the experiment's own methodology,
not just dropped into the `Baselines` line for show.

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

        specific_tokens = set(SPECIFIC_TOKEN.findall(baseline))
        word_count = max(len(baseline.split()), 1)

        # Corroboration check (closes the surface-farming gap): a specific-looking token in
        # Baselines only counts toward the bonus if it recurs in this experiment's own
        # Setup/Procedure text -- i.e. it's actually load-bearing methodological detail, not
        # a name dropped into one line to farm the regex. An invented comparator with no
        # supporting infrastructure elsewhere in the block is scored as if it were generic.
        setup_text = " ".join(str(v) for v in e.get("setup", {}).values())
        procedure_text = " ".join(e.get("procedure", []))
        corroboration_pool = setup_text + " " + procedure_text
        corroborated_tokens = {t for t in specific_tokens if t in corroboration_pool}

        density = len(corroborated_tokens) / word_count

        has_external_referent = bool(re.search(r"\b(vs\.?|reference|prior|external|cohort|"
                                                 r"comparator|control group|historical)\b",
                                                 baseline, re.I))

        score = 0.35 + 0.35 * min(density * 4, 1.0) + 0.30 * (1.0 if has_external_referent else 0.0)
        scores.append(min(score, 1.0))

    return sum(scores) / len(scores)
```

**What the function does & why.** It classifies each experiment's `Baselines` field: empty or
generic placeholder text gets a low floor score (0.15 — a real but weak signal, since some
genuinely comparator-free designs exist, but the hard constraint still requires penalizing
thinness). Non-generic baselines are scored by density of specific tokens *that recur in the same
experiment's `Setup`/`Procedure` text* — a proper noun that appears only in `Baselines` and
nowhere else in the block's own methodology no longer earns the specificity bonus — plus whether
the text names an external referent versus only an internal structural comparison. This rewards
papers that specify a comparator that is actually woven into how the experiment was run.

**Why it's hard to Goodhart.** Simply typing a longer sentence doesn't help — the score is
token-*density restricted to corroborated tokens*, not length or raw token count. Inventing a
fake-sounding specific baseline name to farm the specific-token bonus no longer works in
isolation: unless that name also appears in `Setup`/`Procedure` (meaning it would have to be
threaded through the pipeline description, sequencing/reference fields, or procedure steps too),
it contributes nothing to `density`. That corroboration requirement is now computed directly in
this function, rather than argued as a spillover effect of a separate setup-grounding metric —
fabricating a comparator name now costs a gamer real, consistent effort across two fields
simultaneously, which is the actual methodological work of specifying a comparator.

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
This same richness signal now also feeds directly into Referential Closure's coverage weighting
(metric 1) and Baseline Rigor's corroboration check (metric 3), so a thin `Setup`/`Procedure`
depresses three metrics at once, not just this one.

---

## Combination

These five metrics are chained so that gaming one tends to break another, and stage 2 made two
of those linkages explicit at the compute level rather than leaving them as prose claims. Padding
the artifact with extra experiment/claim ids to inflate **Referential Closure**'s coverage score
now requires generating experiments with genuine `Setup`/`Procedure` richness *within that same
function* — a thin, low-effort block citing many claims earns only fractional credit for each,
because coverage weight is scaled by the citing experiment's own richness. Any near-duplicate
blocks that do get generated are separately caught by **Setup/Procedure Grounding**'s
cross-experiment redundancy check and by weak, tautological, or ungrounded outcomes under
**Falsifiable Specificity** — which now also rejects the previously-open move of writing
confident, directional prose about a quantity `Metrics` never mentions. Trying to make a thin
experiment *look* rigorous by inventing a plausible-sounding numeric result ("reaches 90%
concordance") trips **Declarative Purity**; scrubbing all numbers to avoid that instead strips
out the legitimate design-threshold detail that **Setup Grounding** rewards. Dodging the cost of
a real comparator by writing `baselines: none` is directly penalized by **Baseline Rigor**, while
faking a specific-sounding comparator name is now caught *inside* Baseline Rigor itself — the
name must recur in the same experiment's `Setup`/`Procedure` text to earn credit, not merely be
plausible-looking in isolation. And a single fabricated `Dependencies` edge that creates a cycle
no longer costs a mild 20%-weighted deduction — it hard-caps **Referential Closure** at 0.25
outright. In short: a paper can't cheaply satisfy structural completeness, numeric cleanliness,
outcome specificity, comparator rigor, and methodological distinctiveness all at once without an
experiment layer that reflects genuinely separate, real, falsifiable analyses — and each of those
properties is now cross-checked by at least one other metric's own arithmetic, not just its prose.
