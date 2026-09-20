# Proposer 4 — metrics for `logic/experiments.md`

Assumed parsed representation for all functions below: `artifact["experiments"]` is a list of dicts,
one per `## E{NN}` block, each with keys:
`id` (str), `verifies` (list[str] of claim ids, possibly empty), `setup` (dict[str,str] of subkey→value),
`procedure` (list[str] of steps), `metrics` (str or list[str]), `expected_outcome` (str or list[str]),
`baselines` (str, possibly `"none"`), `dependencies` (list[str] of experiment ids, possibly empty).
A field that is structurally absent from the source markdown is represented as `None`; a field present
but empty/whitespace is represented as `""` or `[]`. These are treated identically (both = missing) by
every function below, per the hard constraint.

---

## 1. Numeric-Leakage / Result-Contamination Score

**How it signals good science.** `experiments.md` is declarative-plan-only: exact results belong in
`evidence/`. A plan that already contains a result number (e.g. "achieves 92% accuracy") isn't a plan at
all — it's a write-up dressed as a plan, meaning the "experiment" was designed retrospectively to fit a
result the authors already had. Plans free of leaked numbers are evidence the plan was actually
committed to *before* the outcome was known, which is the entire epistemic point of a declarative
verification plan.

**Compute function.**
```python
import re

# Allowed: significance/decision-rule syntax that describes the TEST'S DESIGN, not its result.
_THRESHOLD_WHITELIST = re.compile(
    r"""(
        [pq]\s*[<>=]\s*0?\.\d+          |  # p<0.05, q < 0.01
        FDR\s*[<>=]\s*0?\.\d+           |  # FDR<0.05
        \d+%\s*CI                       |  # 95% CI (naming the interval type, not its bound)
        n\s*=\s*\d+                     |  # sample-size notation is a design fact, not a result
        \b(alpha|α)\s*=\s*0?\.\d+
    )""",
    re.IGNORECASE | re.VERBOSE,
)
_NUMBER = re.compile(r"\d+(\.\d+)?%?")

def numeric_leakage_score(artifact: dict) -> float:
    """Assumes artifact['experiments'] as described above.
    Only Metrics and Expected outcome are checked (Setup/Procedure may legitimately
    contain numbers, e.g. hardware specs, dose amounts, model sizes)."""
    exps = artifact.get("experiments") or []
    if not exps:
        return 0.0
    scores = []
    for e in exps:
        metrics = e.get("metrics")
        outcome = e.get("expected_outcome")
        if not metrics or not outcome:
            scores.append(0.0)  # missing field -> penalize, never skip
            continue
        text = " ".join(metrics) if isinstance(metrics, list) else str(metrics)
        text += " " + (" ".join(outcome) if isinstance(outcome, list) else str(outcome))
        whitelisted_spans = {m.span() for m in _THRESHOLD_WHITELIST.finditer(text)}
        leaked = 0
        for m in _NUMBER.finditer(text):
            if not any(m.start() >= s and m.end() <= en for s, en in whitelisted_spans):
                leaked += 1
        scores.append(1.0 / (1.0 + leaked))
    return sum(scores) / len(scores)
```

**What it does & why.** For each experiment, it concatenates the `Metrics` and `Expected outcome` text,
strips out number-shaped substrings that are actually part of an allowed *design-rule* syntax (a p-value
threshold, an FDR cutoff, a stated CI type, a sample-size declaration), and counts what's left. Any
remaining bare number is a leaked result. The score decays smoothly (`1/(1+leaked)`) so one stray number
isn't catastrophic but a `Results`-shaped paragraph masquerading as a plan is punished hard. Missing
`Metrics`/`Expected outcome` is scored 0, not skipped.

**Why it's hard to Goodhart.** The cheap counter-move — deleting all numbers, including legitimate
threshold syntax like `FDR<0.05` — doesn't help gaming, because the whitelist already protects those; a
paper removing real design thresholds to "look cleaner" only makes its `Metrics`/`Procedure` vaguer,
which directly tanks Metric 2 and Metric 3 below (they reward specific, checkable predictions). The
metric can't be beaten by adding vague language either, since vagueness has no numbers to leak but scores
near-zero elsewhere.

---

## 2. Directional Falsifiability of Expected Outcomes

**How it signals good science.** The shape doc mandates "directional/relative language ONLY." A
prediction that says *how* the result should come out (a specific direction, comparison, or ranking) is
falsifiable before the fact; a prediction that only hedges ("may show differences," "could vary") commits
to nothing and can never be wrong. Good science stakes out a falsifiable position pre-registration-style,
even without a number.

**Compute function.**
```python
import re

_HEDGE = {"may","might","could","possibly","potentially","perhaps","presumably","likely","suggests"}
_DIRECTIONAL = {"higher","lower","greater","less","fewer","more","increase","decrease","reduce",
                "elevate","concentrate","dominant","enrich","exceed","outperform","converge",
                "diverge","differ","shift","precede","correlate","absent","depleted","upregulate",
                "downregulate","larger","smaller","earlier","later"}

def _tokens(s: str) -> list:
    return re.findall(r"[a-zA-Z]+", s.lower())

def directional_falsifiability_score(artifact: dict) -> float:
    """Assumes expected_outcome is str or list[str]."""
    exps = artifact.get("experiments") or []
    if not exps:
        return 0.0
    scores = []
    for e in exps:
        outcome = e.get("expected_outcome")
        if not outcome:
            scores.append(0.0)
            continue
        lines = outcome if isinstance(outcome, list) else [outcome]
        toks = _tokens(" ".join(lines))
        if len(toks) < 3:
            scores.append(0.0)  # too short to stake out a real claim
            continue
        directional_hits = sum(1 for t in toks if t in _DIRECTIONAL)
        hedge_hits = sum(1 for t in toks if t in _HEDGE)
        per_line_directional = sum(
            1 for ln in lines if any(t in _DIRECTIONAL for t in _tokens(ln))
        ) / len(lines)
        raw = per_line_directional - 0.15 * hedge_hits
        scores.append(max(0.0, min(1.0, raw)))
    return sum(scores) / len(scores)
```

**What it does & why.** Tokenizes each `Expected outcome` line and checks two word lists: directional
markers (comparative, ranking, or shift language) and hedge markers (modal uncertainty language that
retreats from commitment). It scores the *fraction of outcome lines that stake out a directional claim*,
then subtracts a penalty per hedge word found anywhere in the field. An experiment with no
`Expected outcome`, or one shorter than 3 words, scores 0 — brevity below that threshold is almost always
a stub, not a real prediction.

**Why it's hard to Goodhart.** Padding the field with directional-sounding buzzwords without hedges is
the obvious attack, but directional words only score if they appear *in a genuine relative comparison* —
gluing "higher" onto unrelated prose doesn't fix that this is checked jointly with Metric 3
(traceability): invented directional language that doesn't correspond to anything in `Metrics` scores
well here but zero there. And reflexively adding concrete-sounding numbers to look more "specific" instead
of directional language is caught by Metric 1.

---

## 3. Metric–Outcome Traceability (anti "measurement theater")

**How it signals good science.** Good experimental design predicts an outcome *for every quantity it
proposes to measure*. Listing measurements without committing to what you expect them to show ("we will
measure X, Y, Z" with an `Expected outcome` that never mentions X, Y, or Z) is measurement theater —
padding the `Metrics` field to look thorough while keeping the actual falsifiable commitment vague or
narrow. Real pre-specified analysis plans tie each measured quantity to a stated expectation.

**Compute function.**
```python
import re

_STOP = {"the","a","an","of","and","or","per","with","in","for","to","on","by","is","are","at"}

def _keyphrases(field) -> list:
    """Split a Metrics-like field into discrete measured-quantity phrases."""
    text = " ".join(field) if isinstance(field, list) else str(field or "")
    parts = re.split(r"[;,]|\n-\s*", text)
    return [p.strip() for p in parts if p.strip()]

def _content_words(phrase: str) -> set:
    return {w for w in re.findall(r"[a-zA-Z]+", phrase.lower()) if w not in _STOP and len(w) > 2}

def metric_outcome_traceability(artifact: dict) -> float:
    """Assumes metrics and expected_outcome are str or list[str]."""
    exps = artifact.get("experiments") or []
    if not exps:
        return 0.0
    scores = []
    for e in exps:
        metrics_field = e.get("metrics")
        outcome_field = e.get("expected_outcome")
        if not metrics_field or not outcome_field:
            scores.append(0.0)
            continue
        metric_phrases = _keyphrases(metrics_field)
        if not metric_phrases:
            scores.append(0.0)
            continue
        outcome_text = " ".join(outcome_field) if isinstance(outcome_field, list) else str(outcome_field)
        outcome_words = _content_words(outcome_text)
        covered = 0
        for phrase in metric_phrases:
            phrase_words = _content_words(phrase)
            if phrase_words & outcome_words:
                covered += 1
        scores.append(covered / len(metric_phrases))
    return sum(scores) / len(scores)
```

**What it does & why.** Splits `Metrics` into individual measured-quantity phrases (delimited by
semicolons/commas/list items — matching the shape doc's "markdown-prose or list" format), reduces each
phrase and the whole `Expected outcome` text to content words (stripping stopwords), and checks lexical
overlap. The score is the fraction of declared metrics that have *some* echo in the stated expectation.
An experiment that measures five things but only predicts one gets partial credit; one that lists metrics
with zero corresponding predictions scores 0.

**Why it's hard to Goodhart.** The cheap fix is to cram every metric noun into `Expected outcome`
verbatim — but doing so without genuine directional content (see Metric 2) produces a list-of-nouns
`Expected outcome`, which scores near-zero on falsifiability. To win both metrics simultaneously the
authors have to write an outcome sentence that is *both* directional *and* actually about each declared
metric — which is exactly the real, non-gamed target behavior.

---

## 4. Baseline / Comparator Resolvability

**How it signals good science.** A claim is only interpretable relative to a comparator: "DEGs
concentrate in white matter" means nothing scientifically without knowing what it's being compared
against. The shape doc allows `Baselines: none`, but per this tournament's hard constraint, an absent
comparator is a real weakness to be scored down, not a neutral/exempt state — a study with no baseline at
all supports much weaker inference than one with a named comparator group, model, or reference standard.

**Compute function.**
```python
import re

_GENERIC_FILLER = {"standard","typical","usual","normal","baseline","comparison","default","control"}

def baseline_resolvability_score(artifact: dict) -> float:
    """Assumes baselines is a single str field (or None if the field is structurally absent)."""
    exps = artifact.get("experiments") or []
    if not exps:
        return 0.0
    scores = []
    for e in exps:
        b = e.get("baselines")
        if b is None or not str(b).strip():
            scores.append(0.0)  # field structurally missing -> hardest penalty
            continue
        b_clean = str(b).strip()
        if b_clean.lower() == "none":
            scores.append(0.1)  # legitimate value per shape doc, but still an absent comparator
            continue
        words = re.findall(r"[a-zA-Z]+", b_clean.lower())
        if len(words) < 3:
            scores.append(0.2)  # too short to name anything concrete
            continue
        generic_ratio = sum(1 for w in words if w in _GENERIC_FILLER) / len(words)
        has_specific_marker = bool(
            re.search(r"[A-Z][a-zA-Z]+(_[a-zA-Z0-9]+)?", b_clean.replace(b_clean[0], b_clean[0], 1))
            or re.search(r"\bvs\.?\b|\bcompared to\b|\breference\b|\bcohort\b|\bstudy\b", b_clean, re.I)
        )
        score = 0.5 + 0.4 * has_specific_marker - 0.5 * generic_ratio
        scores.append(max(0.1, min(1.0, score)))
    return sum(scores) / len(scores)
```

**What it does & why.** Distinguishes four tiers per experiment: field structurally absent (score 0,
worst — the compiler didn't even populate it), value literally `"none"` (score 0.1 — a legitimately
declared but absent comparator, still penalized per the tournament's hard rule), a too-short/non-specific
string (low score), and a substantive comparator description, which is scored up when it contains named
markers (a proper-noun-looking token, "vs.", "compared to", "reference", "cohort") and down in proportion
to generic filler words that could describe any study ("standard," "typical").

**Why it's hard to Goodhart.** Writing `Baselines: standard comparator` to avoid the `"none"` penalty
scores only marginally better (~0.2–0.3) because the generic-filler ratio kills it — you can't escape the
floor without naming something real, and inventing a fake-sounding but specific comparator (e.g. a made-up
reference-standard name) creates a `Setup`/`Procedure` inconsistency that Metric 5's parsimony check below
is positioned to catch when the invented baseline is never mentioned in `Procedure`.

---

## 5. Claim-Coverage Parsimony & Structural Reference Integrity

**How it signals good science.** Two failure modes both indicate a hollow experiment block: (a) an
experiment that resolves nothing — cites no claim in `Verifies`, or points `Dependencies` at an `E##` id
that doesn't exist in the file — is structurally decorative; (b) an experiment that claims to verify a
large number of claims while providing only a thin, generic `Procedure`/`Setup` is overclaiming — it's
trying to look load-bearing for many conclusions without doing proportionally more methodological work.
Real experiments verify a proportionate number of claims for the amount of procedural detail they contain.

**Compute function.**
```python
def claim_coverage_parsimony(artifact: dict) -> float:
    """Assumes verifies: list[str]; dependencies: list[str]; procedure: list[str];
    setup: dict[str,str]. All ids compared as-is (strings)."""
    exps = artifact.get("experiments") or []
    if not exps:
        return 0.0
    all_ids = {e.get("id") for e in exps if e.get("id")}
    scores = []
    for e in exps:
        verifies = e.get("verifies") or []
        deps = e.get("dependencies") or []
        procedure = e.get("procedure") or []
        setup = e.get("setup") or {}

        if not verifies:
            scores.append(0.0)  # orphan experiment, verifies nothing -> missing input, penalize
            continue

        dangling = [d for d in deps if d not in all_ids and str(d).lower() != "none"]
        dangling_penalty = 0.3 * len(dangling)

        richness = len(procedure) + len(setup)
        if richness == 0:
            scores.append(0.0)  # no procedural substance at all
            continue
        fanout_ratio = len(verifies) / richness
        # A ratio around/under ~0.5 (e.g. 3 claims backed by 6+ setup/procedure items) is healthy;
        # much higher ratios mean many claims resting on very little described work.
        overclaim_penalty = max(0.0, fanout_ratio - 0.5) * 0.6

        score = 1.0 - dangling_penalty - overclaim_penalty
        scores.append(max(0.0, min(1.0, score)))
    return sum(scores) / len(scores)
```

**What it does & why.** First checks two structural-integrity facts that are fully computable from this
one artifact: every experiment must cite at least one claim in `Verifies` (an experiment citing none is
scored 0 outright), and every id in `Dependencies` must resolve to a real experiment in the same file
(each dangling reference costs 0.3). Then it computes a "fan-out ratio" — claims verified per unit of
described procedural substance (`len(Procedure) + len(Setup)` keys) — and penalizes experiments whose
claim load is disproportionate to their described method, which is a proxy for an experiment stretched
thin across many conclusions.

**Why it's hard to Goodhart.** Padding `Procedure` with filler steps to dilute the fan-out ratio directly
increases apparent richness but produces generic, low-information steps — which this metric can't detect
alone, but which correlates with the vague/generic language that Metrics 2 and 4 already penalize (real
directional predictions and named comparators are hard to fabricate for steps that don't actually exist).
Conversely, trimming `Verifies` down to just one claim to avoid the overclaim penalty reduces the
experiment's evidentiary value, which would need to be compensated elsewhere in `claims.md`'s `Proof`
fields — a cost outside this file the authors can't hide.

---

## Combination

These five metrics are jointly hard to game because each obvious cheap fix for one directly damages
another. Adding real numbers to look "rigorous" wins nothing on falsifiability but gets caught by Numeric
Leakage (1). Writing vague, hedge-heavy outcomes to dodge leakage tanks Directional Falsifiability (2).
Padding `Metrics` with buzzwords to look thorough only helps if they're echoed with real directional
content in `Expected outcome` — satisfying Traceability (3) without satisfying (2) is nearly impossible,
and satisfying both requires the field to actually say something specific and checkable. Declaring a fake
or generic baseline to escape the `"none"` floor in Baseline Resolvability (4) requires filler language
that (4)'s own generic-word penalty already discounts. And inflating an experiment's apparent
authority by citing many claims in `Verifies` without deepening `Procedure`/`Setup` is caught directly by
Claim-Coverage Parsimony (5), while padding `Procedure` to dodge that produces generic steps that are
implicitly penalized by how thin and non-specific the rest of the block reads under (2) and (4). A paper
can't cheaply satisfy all five at once — it has to actually write a specific, falsifiable, well-baselined,
internally consistent plan, which is exactly what "good science" in a declarative experiments file means.
