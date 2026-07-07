# Proposer 1 (improved) — metrics for `logic/experiments.md`

## Changes from stage 1

- **Metric 3 rebuilt.** The hardcoded `_GENRE_SETUP_KEYS` / `_GENRE_METRIC_VOCAB` dictionaries
  were brittle (the critique noted they'd penalize legitimate free-form `Setup` fields, e.g.
  systematic reviews whose `Design` subkey doesn't match any fixed genre bucket) and farmable
  (stuff all genre keywords at once). Replaced with a genre-agnostic **internal consistency**
  check: does the vocabulary in `Metrics` actually recur in *this block's own* `Setup`/`Procedure`
  text? This works for any genre with zero fixed vocabulary, and adds a new anti-circularity
  penalty for the degenerate way to win it — copy-pasting `Setup` verbatim into `Metrics`.
- **Metric 2's `diversity_bonus`** changed from an unjustified multiplicative `×1.1` to an
  additive `+0.15`, with the reasoning made explicit: comparator-class diversity is a binary
  structural property (present/absent), so a multiplicative bonus is the wrong shape — it
  rewards files that already have a high `base` score more than files that most need the
  incentive, which is backwards.
- **Metric 4 now takes `claim_ids`, the id space of `claims.md`, as a required input.** Per the
  tournament's hard constraint, `claims.md` is assumed available; a caller that omits it is a
  missing-input condition and the metric returns `0.0`, not a fallback to trusting this file's
  self-reported `Verifies` targets (the critique correctly flagged that a purely-internal
  triangulation metric can't tell a real claim from an invented one). Citations to nonexistent
  claim ids now earn zero triangulation credit and feed an explicit `dangling_ratio` penalty.
- **Metrics 4 and 5's similarity checks switched from raw `SequenceMatcher` on full text to
  token-set Jaccard overlap.** The critique noted `SequenceMatcher` is "sensitive to boilerplate
  phrasing" — concretely, reordering procedure steps or renaming variables can suppress its
  longest-common-substring-style ratio while leaving the underlying analysis identical. Bag-of-
  words Jaccard is invariant to order and survives light rewording, closing that evasion for both
  the fake-triangulation detector (Metric 4) and the anti-padding detector (Metric 5). Metric 5's
  padding-similarity floor was retuned (0.4 → 0.3) to match the generally-lower baseline that
  Jaccard similarity produces versus `SequenceMatcher`.
- **Metric 4's triangulation/orphan blend changed from an additive `0.7/0.3` average to a
  multiplicative gate**, `mean_triangulation * (0.5 + 0.5*orphan_ratio) * (1 - dangling_ratio)`.
  The critique flagged the `0.7/0.3` weights as arbitrary; the deeper problem was that *any*
  additive blend lets a handful of beautifully-triangulated claims buy back a file where most
  experiments are orphaned dead weight or cite claims that don't exist. A multiplicative gate
  cannot be bought back that way — both properties (real corroboration *and* structural
  completeness) must hold simultaneously.
- **Metric 1 now checks vocabulary sharing between `Expected outcome` and `Metrics`** (using the
  same tokenizer introduced for Metric 3's grounding check), discounting directional statements
  that predict something the protocol never measures. This was previously claimed only in prose
  ("Combination" argued the metrics interlock) — it is now a real compute-level dependency
  between Metric 1 and Metric 3, closing the gap the critique explicitly asked for ("make that
  linkage compute-level, not just prose," raised against the other finalist but equally true of
  this entry's unproven interlock claims).
- Metric 5 and the general DAG/cardinality logic are otherwise unchanged — the critique had no
  complaints there.

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
#
# claim_ids: set[str], the id space declared in claims.md (e.g. {"C01","C02",...}). Assumed
# available per the hard constraint; the scorer must be called with it, not left optional.
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
rewards `Expected outcome` statements that stake out a directional/comparative claim, penalizes
both hedging and leaked exact numbers (a different way of dodging falsifiable-but-qualitative
commitment), and — new in this revision — checks that the claim is actually *about* something the
experiment measures, not free-floating rhetoric.

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
_STOPWORDS = {"the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "with", "is", "are",
              "be", "this", "that", "than", "from", "by", "as", "at", "will", "was", "were",
              "which", "across", "between", "not", "no", "per"}

def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z][a-z\-]{2,}", text.lower()) if t not in _STOPWORDS}

def falsifiability_density(experiments: list[dict]) -> float:
    scores = []
    for exp in experiments:
        outs = exp.get("expected_outcome") or []
        metric_vocab = _tokens(" ".join(exp.get("metrics") or []))
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
            base = max(0.0, 1.0 - 0.3 * hedges)
            # NEW: a directional claim only counts as falsifiable *by this protocol* if it shares
            # vocabulary with something the experiment's own Metrics field actually measures.
            # Bold direction about an unmeasured quantity is unfalsifiable-in-practice even if
            # it's grammatically a clean prediction.
            grounded = bool(metric_vocab) and bool(_tokens(s) & metric_vocab)
            stmt_scores.append(base if grounded else base * 0.4)
        scores.append(sum(stmt_scores) / len(stmt_scores))
    return sum(scores) / len(scores) if scores else 0.0
```

**What it does & why.** For every `Expected outcome` bullet, the function checks (a) no leaked
exact number, (b) a directional/comparative verb or adjective, and (c) — new — that the bullet's
vocabulary overlaps with the experiment's `Metrics` field, i.e. the prediction is about a quantity
this protocol is actually built to check. Bullets that pass all three get up to 1.0 (discounted for
hedge words); bullets whose direction targets nothing in `Metrics` are capped at `0.4×base` rather
than credited in full. An experiment with no `Expected outcome` scores 0 outright.

**Why it's hard to Goodhart.** Writing bold directional prose for every bullet is cheap, but now
that prose must lexically connect to the `Metrics` field to earn full credit — disconnecting them
to avoid also tripping Metric 3's grounding check (below) directly caps this metric at 0.4×base.
Confident direction with `Baselines: none` and no other experiment touching the same claim still
reads as unsupported bravado under Metrics 2 and 4.

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
    # Additive, not multiplicative (changed from stage 1's ×1.1). Mixing comparator classes is a
    # binary structural property of the plan — present or absent — not something that should
    # scale with how high `base` already is. A multiplicative bonus rewards files that are
    # already comparator-rich more than files that most need the incentive, which is backwards
    # for a scoring signal. Fixed at 15% of the max score, capped at 1.0.
    diversity_bonus = 0.15 if len(distinct_nonnone) >= 2 else 0.0
    return min(1.0, base + diversity_bonus)
```

**What it does & why.** Classifies each experiment's `Baselines` string into `none` (0.0),
`internal` (0.5, e.g. "within-study comparison across SpDs"), or `external` (1.0, named reference
standard / prior published method / benchmark). Averages across experiments, then adds a flat 0.15
credit if the file mixes internal *and* external comparators rather than leaning on one type
everywhere — a study that only ever compares itself to itself is missing a class of failure mode
no matter how many times it does so.

**Why it's hard to Goodhart.** Writing `Baselines: reference standard XYZ` everywhere is cheap
text, but a fabricated or irrelevant "reference standard" pasted into every block starts to look
identical across experiments (low lexical variety), which drags down Metric 5's anti-padding
check, and if `Metrics`/`Procedure` never actually engage with that comparator (no matched
vocabulary), it now also fails Metric 3's internal-consistency check directly.

---

## Metric 3: Method–Measurement Internal Consistency (anti-genericity, genre-agnostic)

**How it signals good science.** Real methods sections produce measurements that are entailed by
the method actually described: whatever `Metrics` claims to measure should be traceable to
instruments, variables, or steps named in that same block's `Setup`/`Procedure`. When `Metrics`
uses vocabulary with no anchor anywhere else in the block, that's the shape doc's own
"abstract-only compilation" signature — a plan reverse-engineered from an abstract sentence rather
than derived from a real protocol. (Stage-1 tried to detect this via fixed genre→vocabulary
dictionaries; the critique correctly flagged that as brittle for legitimate free-form `Setup`
fields — e.g. systematic reviews whose `Setup.Design` dominates and whose `Hardware`/`Model` are
correctly absent — and farmable by keyword-stuffing every genre's terms at once. This revision
drops genre buckets entirely in favor of within-block grounding.)

**Compute function.**
```python
import re
from difflib import SequenceMatcher

_STOPWORDS = {"the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "with", "is", "are",
              "be", "this", "that", "than", "from", "by", "as", "at", "will", "was", "were",
              "which", "across", "between", "not", "no", "per"}

def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z][a-z\-]{2,}", text.lower()) if t not in _STOPWORDS}

def method_measurement_fit(experiments: list[dict]) -> float:
    scores = []
    for exp in experiments:
        setup = exp.get("setup") or {}
        procedure = exp.get("procedure") or []
        metrics = exp.get("metrics") or []
        if not setup or not metrics:
            scores.append(0.0)   # missing Setup or Metrics -> penalized, not skipped
            continue

        setup_text = " ".join(f"{k} {v}" for k, v in setup.items())
        proc_text = " ".join(procedure)
        metrics_text = " ".join(metrics)

        ground_vocab = _tokens(setup_text) | _tokens(proc_text)
        metric_tokens = _tokens(metrics_text)
        if not metric_tokens:
            scores.append(0.0)
            continue

        grounded = metric_tokens & ground_vocab
        grounding_ratio = len(grounded) / len(metric_tokens)

        # Anti-circularity: the degenerate way to max out grounding_ratio is to paste Setup
        # verbatim into Metrics. That isn't a real measurement statement, it's a restatement, so
        # penalize near-verbatim copying proportionally to how close it is to a clone.
        copy_sim = SequenceMatcher(None, metrics_text.lower(), (setup_text + " " + proc_text).lower()).ratio()
        copy_penalty = max(0.0, copy_sim - 0.6) / 0.4   # 0 below 0.6 similarity, ramps to 1 at 1.0

        scores.append(max(0.0, grounding_ratio * (1.0 - 0.5 * copy_penalty)))
    return sum(scores) / len(scores) if scores else 0.0
```

**What it does & why.** For each experiment, builds a vocabulary from `Setup` + `Procedure` and
checks what fraction of `Metrics`'s meaningful terms are actually anchored somewhere in that
vocabulary — i.e., is this experiment measuring things it plausibly produces, or reciting generic
outcome language untethered to its own described protocol? A high grounding ratio achieved by
copy-pasting `Setup` into `Metrics` (rather than genuinely restating what's measured) is separately
detected and discounted. Missing `Setup` or `Metrics` scores 0. This works identically for wet-lab,
ML, clinical, theory, or free-form genres — including systematic reviews, whose `Design`-only
`Setup` is legitimate rather than thin — because it never consults a fixed genre dictionary.

**Why it's hard to Goodhart.** Stuffing `Metrics` with terms that also appear in `Setup`/`Procedure`
means either (a) those terms are genuinely descriptive of the protocol, which is exactly the
desired behavior, or (b) the author pads `Setup` with the same buzzwords to manufacture overlap —
but padding `Setup` with terms unconnected to real `Procedure` steps drags down Metric 5's
anti-padding check (which measures cross-block textual distinctiveness) and produces `Expected
outcome` statements under Metric 1 that either share the padding vocabulary (and thus predict
something never really instrumented) or don't (and are capped at 0.4×). Verbatim-copy gaming is
directly caught by the `copy_penalty` term.

---

## Metric 4: Triangulation / Verification Load (claims-bound)

**How it signals good science.** A claim resting on exactly one experiment is one dropped assay
away from unsupported. A claim independently corroborated by two *genuinely different* experiments
(different `Setup`/`Procedure`, not a near-clone) is much harder to explain away by a single
methodological artifact. This metric rewards claim-level triangulation, discounts "fake"
triangulation from near-duplicate experiments, and — new in this revision — only counts
corroboration against claim ids that actually exist in `claims.md`, so an experiment can't harvest
triangulation credit by "verifying" an invented id.

**Compute function.**
```python
import re
from collections import defaultdict

_STOPWORDS = {"the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "with", "is", "are",
              "be", "this", "that", "than", "from", "by", "as", "at", "will", "was", "were",
              "which", "across", "between", "not", "no", "per"}

def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z][a-z\-]{2,}", text.lower()) if t not in _STOPWORDS}

def _exp_tokens(exp: dict) -> set[str]:
    setup_txt = " ".join(f"{k} {v}" for k, v in (exp.get("setup") or {}).items())
    proc_txt = " ".join(exp.get("procedure") or [])
    return _tokens(setup_txt + " " + proc_txt)

def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def triangulation_load(experiments: list[dict], claim_ids: set[str],
                        similarity_threshold: float = 0.6) -> float:
    # claim_ids: the id space declared in claims.md. Per the hard availability constraint,
    # claims.md is assumed available to the scorer; a caller that can't supply claim_ids is a
    # missing-input condition, not license to fall back on trusting this file's own
    # self-reported `Verifies` targets (which would let an experiment "verify" a fabricated
    # claim id for free credit).
    if not claim_ids:
        return 0.0

    by_id = {e["id"]: e for e in experiments if e.get("id")}
    claim_to_exps = defaultdict(list)
    total_citations = 0
    dangling_citations = 0
    nonempty_verifies = 0
    for exp in experiments:
        v = exp.get("verifies") or []
        if v:
            nonempty_verifies += 1
        for c in v:
            total_citations += 1
            if c not in claim_ids:
                dangling_citations += 1   # citing a nonexistent claim id: zero credit for it
                continue
            claim_to_exps[c].append(exp["id"])

    if not claim_to_exps:
        return 0.0   # no claim ever verified by anything resolvable -> fully penalized

    claim_scores = []
    for claim, exp_ids in claim_to_exps.items():
        token_sets = [_exp_tokens(by_id[eid]) for eid in exp_ids if eid in by_id]
        independent = 0
        used = [False] * len(token_sets)
        for i in range(len(token_sets)):
            if used[i]:
                continue
            independent += 1
            used[i] = True
            for j in range(i + 1, len(token_sets)):
                if not used[j] and _jaccard(token_sets[i], token_sets[j]) >= similarity_threshold:
                    used[j] = True   # bag-of-words overlap: survives reordered/renamed near-clones
        claim_scores.append(min(1.0, independent / 2))

    mean_triangulation = sum(claim_scores) / len(claim_scores)
    orphan_ratio = nonempty_verifies / len(experiments) if experiments else 0.0
    dangling_ratio = dangling_citations / total_citations if total_citations else 0.0

    # Multiplicative gate, not an additive blend (stage 1 used an unjustified 0.7/0.3 average).
    # Structural completeness (few orphans, few dangling citations) and real corroboration
    # (mean_triangulation) are both necessary conditions for good triangulation, not fungible
    # ones -- an additive blend lets a handful of beautifully-triangulated claims buy back a file
    # where most experiments are orphaned dead weight or cite invented claims. A multiplicative
    # gate cannot be bought back that way.
    structural_gate = (0.5 + 0.5 * orphan_ratio) * (1.0 - dangling_ratio)
    return mean_triangulation * structural_gate
```

**What it does & why.** Builds a claim→experiments map from every `Verifies` list, dropping
citations to claim ids absent from `claims.md` and tallying them as `dangling_citations`. For each
resolvable claim, greedily clusters its supporting experiments by token-set (bag-of-words)
similarity of `Setup`+`Procedure`; near-duplicates collapse into a single unit of "independent
support," so 2+ truly distinct experiments score 1.0, exactly 1 (or N clones of one design) scores
0.5. The file-level score multiplies mean claim triangulation by a structural gate built from the
fraction of experiments that verify anything resolvable at all, and by the inverse of the dangling-
citation rate — an experiment block with an empty or unresolvable `Verifies` is dead weight, and a
plan that cites nonexistent claims is penalized on both counts.

**Why it's hard to Goodhart.** Cloning an experiment block to fake two independent lines of
evidence is neutralized by the Jaccard-based similarity-collapse step, which — unlike stage 1's
raw `SequenceMatcher` — survives the cheap evasion of reordering procedure steps or renaming
variables while keeping the underlying analysis identical (bag-of-words overlap is order-
invariant). Cloned blocks also inflate Metric 5's cross-block similarity signal. Inventing a claim
id to "verify" for free triangulation credit is now directly zeroed out by the `claim_ids`
resolution check, and the multiplicative structural gate means a plan can't average away a high
orphan/dangling rate by being very good at triangulating the few claims it does resolve.

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
import re
from itertools import combinations

_STOPWORDS = {"the", "a", "an", "of", "in", "on", "to", "for", "and", "or", "with", "is", "are",
              "be", "this", "that", "than", "from", "by", "as", "at", "will", "was", "were",
              "which", "across", "between", "not", "no", "per"}

def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z][a-z\-]{2,}", text.lower()) if t not in _STOPWORDS}

def _exp_tokens(exp: dict) -> set[str]:
    setup_txt = " ".join(f"{k} {v}" for k, v in (exp.get("setup") or {}).items())
    proc_txt = " ".join(exp.get("procedure") or [])
    return _tokens(setup_txt + " " + proc_txt)

def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

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

    # 3. anti-padding: average pairwise token-set (bag-of-words) similarity of Setup+Procedure.
    # Changed from stage 1's raw SequenceMatcher, which is sensitive to boilerplate phrasing and
    # can be evaded by reordering steps or renaming variables while keeping the same analysis;
    # Jaccard overlap on token sets is order-invariant and catches that evasion.
    token_sets = [_exp_tokens(e) for e in experiments]
    pair_sims = [_jaccard(a, b) for a, b in combinations(token_sets, 2)]
    avg_sim = sum(pair_sims) / len(pair_sims) if pair_sims else 0.0
    # Floor recalibrated 0.4 -> 0.3: bag-of-words Jaccard runs structurally lower at baseline
    # than SequenceMatcher's longest-common-substring-style ratio (shared connective phrasing
    # inflates SequenceMatcher more than it inflates a set-overlap measure), so the same real-
    # world padding sensitivity now sits at a lower numeric floor.
    padding_penalty = max(0.0, avg_sim - 0.3) / 0.7

    return dangling_frac * (1.0 - 0.7 * padding_penalty)
```

**What it does & why.** First enforces the ≥3-block cardinality floor (fewer is scored 0, treating
thinness as a penalty rather than a smaller-but-valid case). Then checks every `Dependencies`
reference resolves to a real `E##` in the same file, and that the dependency graph has no cycles
(a hard, structural failure that zeroes the score outright). Finally it measures average pairwise
bag-of-words similarity of `Setup`+`Procedure` across all experiment pairs; a high average
similarity across a small set of blocks is the signature of copy-paste padding to hit the minimum
count, penalized proportionally, on a floor recalibrated for the Jaccard scale.

**Why it's hard to Goodhart.** You cannot pad the count with near-identical blocks without
triggering the anti-padding penalty here, and — unlike stage 1 — superficially reordering steps or
renaming variables no longer escapes detection, since token-set overlap ignores order. Making the
blocks lexically different while keeping the same `Verifies`/claim targets now reads as fabricated
triangulation under Metric 4's own token-set similarity-collapse logic, applied to the identical
underlying text.

---

## Combination

These five metrics interlock so that no cheap edit wins more than one at a time, and several of
those interlocks are now real shared computation rather than asserted in prose. Confident,
directional `Expected outcome` prose (Metric 1) only earns full credit when it shares vocabulary
with what `Metrics` actually measures — the same grounding vocabulary Metric 3 checks against
`Setup`/`Procedure` — so an author can't win Metric 1 with prose disconnected from a real
measurement without simultaneously being capped by Metric 3's internal-consistency check. A
confident direction with `Baselines: none` and no comparator (Metric 2) or no independent
corroboration (Metric 4) still reads as unsupported bravado. Metric 4's triangulation is now bound
to `claims.md`'s real id space, so inventing a claim to "verify" earns nothing, and its
multiplicative structural gate means orphaned or dangling `Verifies` citations can't be
diluted away by cherry-picked strong triangulation elsewhere in the file. Any attempt to win
triangulation or cardinality by duplicating or lightly rewording experiment blocks — including the
cheap trick of reordering steps or renaming variables — is caught by the same token-set-overlap
logic shared between Metric 4's fake-triangulation detector and Metric 5's anti-padding check. A
paper genuinely doing multiple distinct, well-instrumented, claims-grounded, cross-validated
analyses scores well on all five; a paper gaming any single axis (ungrounded bold prose, invented
baselines, keyword-stuffed or copy-pasted metrics, invented claim ids, cloned or reordered blocks)
now leaves a fingerprint that at least one other metric is built to detect directly, not just
argued to detect.
