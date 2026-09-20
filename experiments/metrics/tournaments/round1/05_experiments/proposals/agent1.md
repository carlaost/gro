# Proposer 1 — metrics for `logic/experiments.md`

Assumed parsed representation for all functions below (stated once, shared):

```python
# experiments: list[dict], one dict per "## E{NN}: ..." block, each with:
#   id:                str            e.g. "E03"
#   verifies:           list[str]      claim ids, e.g. ["C03","C05","C06"]  (missing -> [])
#   setup:              dict[str,str]  subkey -> free text, e.g. {"Assay": "..."} (missing -> {})
#   procedure:          list[str]      numbered steps as strings (missing -> [])
#   metrics:            list[str]      metric/measurement statements (missing -> [])
#   expected_outcome:   list[str]      directional statements (missing -> [])
#   baselines:          str            comparator text, or "none" (missing -> "")
#   dependencies:       list[str]      other E## ids (missing -> [])
```

All scores are normalized to `[0, 1]`, higher = better science. Every function treats a
missing/empty/absent field as an active penalty input, never as "N/A" — per the hard constraint.

---

## Metric 1: Falsifiability Density

**How it signals good science.** A plan that commits to a specific, checkable direction
("DEGs concentrate in white-matter SpDs") can be wrong, and being provably wrong under the
prescribed `Metrics` is exactly what makes an experiment worth running. A plan that only hedges
("may show some differences") can never be disconfirmed by the described procedure — it is
compatible with any result, which is the signature of unfalsifiable pseudo-science. This metric
rewards `Expected outcome` statements that stake out a directional/comparative claim and
penalizes both hedging and — per the shape doc's own defect rule — leaked exact numbers, which
are a different way of dodging falsifiable-but-qualitative commitment (smuggling precision that
belongs in `evidence/` instead of taking an interpretable directional stand here).

**Compute function.**
```python
import re

_DIRECTIONAL = re.compile(
    r"\b(higher|lower|greater|less|more|fewer|increas\w*|decreas\w*|no (effect|difference|change)|"
    r"differ\w*|concentrat\w*|dominant|exceed\w*|outperform\w*|converg\w*|correlat\w*|"
    r"anti-?correlat\w*|absent|enrich\w*|favor\w*|reduc\w*|elevat\w*|attenuat\w*|amplif\w*|"
    r"shift\w*|revers\w*|invert\w*|worse|better)\b", re.I)
_HEDGE = re.compile(r"\b(may|might|could|possibly|potentially|perhaps|somewhat|certainly|likely|unclear)\b", re.I)
_NUMBER_LEAK = re.compile(r"\d+(\.\d+)?\s*%|\b\d{2,}\b")  # crude leaked-result detector

def falsifiability_density(experiments: list[dict]) -> float:
    scores = []
    for exp in experiments:
        outs = exp.get("expected_outcome") or []
        if not outs:
            scores.append(0.0)   # missing Expected outcome -> penalized, not skipped
            continue
        stmt_scores = []
        for s in outs:
            if _NUMBER_LEAK.search(s):
                stmt_scores.append(0.0)          # leaked result = defect, not a bonus for "specificity"
                continue
            if not _DIRECTIONAL.search(s):
                stmt_scores.append(0.0)          # no committed direction = unfalsifiable filler
                continue
            hedges = len(_HEDGE.findall(s))
            stmt_scores.append(max(0.0, 1.0 - 0.3 * hedges))
        scores.append(sum(stmt_scores) / len(stmt_scores))
    return sum(scores) / len(scores) if scores else 0.0
```

**What it does & why.** For every `Expected outcome` bullet in every experiment block, the
function checks (a) it isn't secretly leaking an exact number (a Critical-Rule-#3 style defect),
and (b) it contains a directional/comparative verb or adjective. Bullets that pass get a score of
1.0, discounted for hedge words that let the author wriggle out of a clean confirm/disconfirm.
Bullets that are pure hedge, vacuous, or numerically leaky score 0. An experiment with no
`Expected outcome` at all scores 0 outright. The file's score is the mean over experiments.

**Why it's hard to Goodhart.** Simply writing bold directional prose for every bullet ("X will be
much higher than Y") is cheap in isolation, but bold, ungrounded direction-claims that aren't tied
to a real comparator collapse Metric 2 (Comparator Rigor) and Metric 4 (Triangulation) below — a
confident direction with `Baselines: none` and no other experiment touching the same claim reads
as unsupported bravado, not rigor.

---

## Metric 2: Comparator Rigor & Diversity

**How it signals good science.** Claims are only as strong as what they're measured against.
An experiment plan that never says what it's being compared to (`Baselines: none`, or nothing at
all) cannot distinguish signal from noise, batch effects, or chance. Good science diversifies its
comparators across a study — some internal (within-study contrasts) and some external (named
reference standards, published cohorts, prior methods) — because triangulating against both types
catches different failure modes (internal comparators catch batch/context confounds; external
comparators catch generalization failure).

**Compute function.**
```python
import re

_NONE_PAT = re.compile(r"^\s*(none|n/?a|not applicable)\s*\.?\s*$", re.I)
_EXTERNAL_HINTS = re.compile(
    r"\b(reference|gold standard|published|prior (study|work|method)|external|"
    r"cohort|registry|consortium|catalog|benchmark|standard)\b", re.I)
_INTERNAL_HINTS = re.compile(r"\b(within-study|self-|before/after|baseline period|internal)\b", re.I)

def comparator_rigor(experiments: list[dict]) -> float:
    cats = []
    for exp in experiments:
        b = (exp.get("baselines") or "").strip()
        if not b or _NONE_PAT.match(b):
            cats.append(("none", 0.0))
        elif _EXTERNAL_HINTS.search(b):
            cats.append(("external", 1.0))
        elif _INTERNAL_HINTS.search(b) or len(b) > 0:
            cats.append(("internal", 0.5))
    if not cats:
        return 0.0
    base = sum(v for _, v in cats) / len(cats)
    distinct_nonnone = {c for c, v in cats if v > 0}
    diversity_bonus = 1.1 if len(distinct_nonnone) >= 2 else 1.0
    return min(1.0, base * diversity_bonus)
```

**What it does & why.** Classifies each experiment's `Baselines` string into `none` (0.0),
`internal` (0.5, e.g. "within-study comparison across SpDs"), or `external` (1.0, named reference
standard / prior published method / benchmark). Averages across experiments, then applies a small
multiplicative bonus if the file mixes internal *and* external comparators rather than leaning on
one type everywhere — a study that only ever compares itself to itself is missing a class of
failure mode no matter how many times it does so.

**Why it's hard to Goodhart.** Writing `Baselines: reference standard XYZ` everywhere is cheap
text, but a fabricated or irrelevant "reference standard" pasted into every block starts to look
identical across experiments (low lexical variety), which drags down Metric 5's anti-padding
check, and if the `Metrics`/`Procedure` fields never actually engage with that comparator (no
matched vocabulary), it fails Metric 3's fit check.

---

## Metric 3: Method–Measurement Fit (genre coherence, anti-genericity)

**How it signals good science.** Real methods sections produce measurements that are entailed by
the method: a spatial-omics assay yields DEG counts and FDR-thresholded gene sets, not "accuracy";
a model-eval yields accuracy/AUC/loss, not "enriched GO terms." When `Metrics` is genre-mismatched
or so generic it would fit any paper unchanged, that's the shape doc's own "abstract-only
compilation" signature — a plan reverse-engineered from an abstract sentence rather than derived
from a real protocol.

**Compute function.**
```python
_GENRE_SETUP_KEYS = {
    "wetlab":    {"assay", "sequencing", "reference standard", "pipeline"},
    "ml":        {"model", "hardware", "dataset"},
    "clinical":  {"population", "intervention", "endpoint", "randomization"},
    "theory":    {"design", "proof", "model"},
}
_GENRE_METRIC_VOCAB = {
    "wetlab":   {"fdr", "deg", "fold change", "expression", "enrichment", "go term", "cluster", "count"},
    "ml":       {"accuracy", "auc", "loss", "f1", "precision", "recall", "error rate", "latency"},
    "clinical": {"hazard ratio", "odds ratio", "ci", "risk", "survival", "response rate", "event rate"},
    "theory":   {"bound", "complexity", "convergence", "proof obligation", "lemma", "invariant"},
}

def method_measurement_fit(experiments: list[dict]) -> float:
    scores = []
    for exp in experiments:
        setup_keys = {k.strip().lower() for k in (exp.get("setup") or {}).keys()}
        metrics_text = " ".join(exp.get("metrics") or []).lower()
        if not setup_keys or not metrics_text:
            scores.append(0.0)   # missing Setup or Metrics -> penalized
            continue
        best_genre, best_overlap = None, 0
        for genre, keys in _GENRE_SETUP_KEYS.items():
            overlap = len(setup_keys & keys)
            if overlap > best_overlap:
                best_genre, best_overlap = genre, overlap
        if best_genre is None:
            scores.append(0.3)   # unrecognized genre: neutral-low, not zero (free-form is allowed)
            continue
        vocab = _GENRE_METRIC_VOCAB[best_genre]
        hits = sum(1 for term in vocab if term in metrics_text)
        scores.append(min(1.0, hits / 2))   # 2+ genre-appropriate metric terms = full credit
    return sum(scores) / len(scores) if scores else 0.0
```

**What it does & why.** Infers each experiment's genre from which `Setup` subkeys are present
(e.g. `Assay`/`Sequencing` → wet-lab), then checks whether `Metrics` uses vocabulary that plausibly
belongs to that genre. An experiment with a wet-lab `Setup` but ML-flavored metrics (or vaguely
generic metrics with zero genre-specific terms) scores low. Missing `Setup` or `Metrics` is scored
0, not skipped.

**Why it's hard to Goodhart.** Stuffing `Metrics` with keywords from every genre at once to
guarantee a hit is detectable as boilerplate: it makes experiments look interchangeable, which is
exactly what Metric 5's cross-block similarity check is built to catch, and disconnected
keyword-stuffing without matching `Procedure` steps will also read as unfalsifiable filler under
Metric 1 (no real measurement to make the `Expected outcome` checkable against).

---

## Metric 4: Triangulation / Verification Load

**How it signals good science.** A claim resting on exactly one experiment is one dropped assay
away from unsupported. A claim independently corroborated by two *genuinely different* experiments
(different `Setup`/`Procedure`, not a near-clone) is much harder to explain away by a single
methodological artifact. This metric rewards claim-level triangulation and explicitly discounts
"fake" triangulation — two experiments that verify the same claim but are near-duplicates of each
other in `Setup`+`Procedure` text (i.e., the same analysis run twice, not two independent tests).

**Compute function.**
```python
from difflib import SequenceMatcher
from collections import defaultdict

def _exp_text(exp: dict) -> str:
    setup_txt = " ".join(f"{k}:{v}" for k, v in (exp.get("setup") or {}).items())
    proc_txt = " ".join(exp.get("procedure") or [])
    return (setup_txt + " " + proc_txt).lower()

def triangulation_load(experiments: list[dict], similarity_threshold: float = 0.85) -> float:
    by_id = {e["id"]: e for e in experiments if e.get("id")}
    claim_to_exps = defaultdict(list)
    nonempty_verifies = 0
    for exp in experiments:
        v = exp.get("verifies") or []
        if v:
            nonempty_verifies += 1
        for c in v:
            claim_to_exps[c].append(exp["id"])

    if not claim_to_exps:
        return 0.0   # no claim ever verified by anything -> fully penalized

    claim_scores = []
    for claim, exp_ids in claim_to_exps.items():
        texts = [_exp_text(by_id[eid]) for eid in exp_ids if eid in by_id]
        independent = 0
        used = [False] * len(texts)
        for i in range(len(texts)):
            if used[i]:
                continue
            independent += 1
            used[i] = True
            for j in range(i + 1, len(texts)):
                if not used[j] and SequenceMatcher(None, texts[i], texts[j]).ratio() >= similarity_threshold:
                    used[j] = True   # near-duplicate: doesn't count as extra independent support
        claim_scores.append(min(1.0, independent / 2))

    mean_triangulation = sum(claim_scores) / len(claim_scores)
    orphan_penalty_term = nonempty_verifies / len(experiments) if experiments else 0.0
    return 0.7 * mean_triangulation + 0.3 * orphan_penalty_term
```

**What it does & why.** Builds a claim→experiments map from every `Verifies` list, then for each
claim greedily clusters its supporting experiments by textual similarity of `Setup`+`Procedure`;
near-duplicates collapse into a single unit of "independent support." A claim backed by 2+ truly
distinct experiments scores 1.0; backed by exactly 1 (or by N clones of the same design) scores
0.5; the file-level score blends mean claim triangulation with the fraction of experiments that
verify anything at all (an experiment block with an empty `Verifies` is dead weight, penalized).

**Why it's hard to Goodhart.** Cloning an experiment block to fake two independent lines of
evidence is directly neutralized by the similarity-collapse step in this metric, and cloned blocks
also inflate the cross-block similarity signal that Metric 5 uses to detect padding — so the same
move that would try to win this metric loses Metric 5.

---

## Metric 5: Structural Integrity & Anti-Padding

**How it signals good science.** A research plan is a graph, not a list: `Dependencies` must form
a valid DAG over real experiment ids (a cycle or a dangling reference is a logical impossibility,
not a stylistic nit), and the file must contain genuinely distinct analyses rather than the
statutory minimum of three interchangeable, templated blocks manufactured to pass a headcount
gate (the shape doc explicitly flags "abstract-only compilation" producing generic, boilerplate
experiments as a defect).

**Compute function.**
```python
from difflib import SequenceMatcher
from itertools import combinations

def structural_integrity(experiments: list[dict]) -> float:
    ids = {e["id"] for e in experiments if e.get("id")}
    n = len(experiments)

    if n < 3:
        return 0.0   # below Seal L1 minimum cardinality -> treated as thin/absent, not partial

    # 1. dangling reference check
    all_deps = [d for e in experiments for d in (e.get("dependencies") or [])]
    valid_deps = [d for d in all_deps if d in ids]
    dangling_frac = 1.0 if not all_deps else len(valid_deps) / len(all_deps)

    # 2. cycle check (DFS)
    graph = {e["id"]: [d for d in (e.get("dependencies") or []) if d in ids] for e in experiments if e.get("id")}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    has_cycle = False
    def dfs(u):
        nonlocal has_cycle
        color[u] = GRAY
        for v in graph.get(u, []):
            if color.get(v) == GRAY:
                has_cycle = True
            elif color.get(v) == WHITE:
                dfs(v)
        color[u] = BLACK
    for node in graph:
        if color[node] == WHITE:
            dfs(node)
    if has_cycle:
        return 0.0   # a dependency cycle is a hard structural defect

    # 3. anti-padding: average pairwise similarity of Setup+Procedure text
    def exp_text(exp):
        setup_txt = " ".join(f"{k}:{v}" for k, v in (exp.get("setup") or {}).items())
        return (setup_txt + " " + " ".join(exp.get("procedure") or [])).lower()
    texts = [exp_text(e) for e in experiments]
    pair_sims = [SequenceMatcher(None, a, b).ratio() for a, b in combinations(texts, 2)]
    avg_sim = sum(pair_sims) / len(pair_sims) if pair_sims else 0.0
    padding_penalty = max(0.0, avg_sim - 0.4) / 0.6   # 0 below 0.4 sim, ramps to 1 at sim=1.0

    return dangling_frac * (1.0 - 0.7 * padding_penalty)
```

**What it does & why.** First enforces the ≥3-block cardinality floor (fewer is scored 0, treating
thinness as a penalty rather than a smaller-but-valid case). Then checks every `Dependencies`
reference resolves to a real `E##` in the same file, and that the dependency graph has no cycles
(a hard, structural failure that zeroes the score outright — you cannot depend on your own
prerequisite). Finally it measures average pairwise textual similarity of `Setup`+`Procedure`
across all experiment pairs; a high average similarity across a small set of blocks is the
signature of copy-paste padding to hit the minimum count, and is penalized proportionally.

**Why it's hard to Goodhart.** You cannot pad the count with near-identical blocks without
triggering the anti-padding penalty here directly; you also cannot fix that by making the blocks
superficially different (renaming variables, reordering steps) while keeping the same
`Verifies`/claim targets, because that starts to look like fabricated triangulation under Metric 4
once the similarity-collapse logic there is applied to the same text.

---

## Combination

These five metrics are built to interlock so that no cheap edit wins more than one at a time.
Confident, directional `Expected outcome` prose (Metric 1) is worthless — and reads as bravado
rather than rigor — unless it's backed by a real, specific comparator (Metric 2) and genre-matched
measurements (Metric 3). Comparators and measurements in turn only count as real evidence if they
attach to a claim that's independently triangulated rather than trivially self-cited (Metric 4).
And any attempt to win triangulation or cardinality by duplicating or lightly rewording experiment
blocks is caught directly by the anti-padding and DAG-integrity checks in Metric 5, whose
similarity detector is the same lexical-overlap logic used to discount fake triangulation in
Metric 4. A paper that is genuinely doing multiple distinct, well-instrumented, cross-validated
analyses scores well on all five; a paper gaming any single axis (bold prose, invented baselines,
keyword-stuffed metrics, cloned blocks) creates a textual or structural fingerprint that drags down
at least one of the others.
