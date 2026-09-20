# Proposer #4 — metrics for `trace/exploration_tree.yaml`

All functions assume the artifact is parsed into a Python object `artifact = {"tree": [...]}`
where each node is a `dict` matching the shape doc (shared fields `id`, `type`, `support_level`,
`source_refs`, `title`, optional `also_depends_on`, optional `children`, plus type-specific
required fields). A shared helper is used by several metrics:

```python
def _flatten(tree):
    """Depth-first flatten of the nested tree into a flat list of node dicts,
    each annotated with its integer depth. Missing/malformed tree -> empty list
    (callers must treat empty as a penalized case per the hard constraint, not a skip)."""
    out = []
    def walk(nodes, depth):
        if not isinstance(nodes, list):
            return
        for n in nodes:
            if not isinstance(n, dict):
                continue
            n = dict(n)
            n["_depth"] = depth
            out.append(n)
            walk(n.get("children", []), depth + 1)
    walk(tree.get("tree", []) if isinstance(tree, dict) else [], 0)
    return out
```

---

## 1. Candor Density (failure & rejection disclosure, genre-normalized)

**How it signals good science.** Real research trajectories involve rejected paths. A tree that
is all forward motion (only `question`→`experiment`→done) is a laundered narrative, not a
research log. The brief explicitly says dead ends are the single most valuable node type. A paper
that discloses `dead_end` and `decision`(with real `alternatives`) nodes in proportion to its
experimental volume is doing (and reporting) real science; one that reports many experiments and
zero friction is either genuinely frictionless (rare) or has been extraction-laundered.

**Compute function.**

```python
def candor_density(tree):
    """
    Input assumption: `tree` is the raw parsed artifact dict {"tree": [...]}.
    Missing/empty tree -> score 0.0 (hard-constraint: absence is penalized, not skipped).
    """
    nodes = _flatten(tree)
    if not nodes:
        return 0.0

    root_text = " ".join(
        str(n.get("title", "")) + " " + str(n.get("description", ""))
        for n in nodes if n.get("type") == "question"
    ).lower()
    synthesis_markers = ["systematic review", "meta-analysis", "network meta-analysis",
                          "scoping review", "umbrella review"]
    is_synthesis = any(m in root_text for m in synthesis_markers)

    n_experiments = sum(1 for n in nodes if n.get("type") == "experiment")
    n_dead_ends = sum(1 for n in nodes if n.get("type") == "dead_end")
    n_decisions_with_alts = sum(
        1 for n in nodes
        if n.get("type") == "decision" and len(n.get("alternatives") or []) > 0
    )
    friction = n_dead_ends + n_decisions_with_alts

    if n_experiments == 0:
        # no experimental volume at all to have generated friction from -> can't earn credit
        return 0.05

    raw_ratio = friction / n_experiments
    # synthesis genres legitimately produce friction at a lower rate (ranking-failure dead ends
    # and de-overlap decisions are rarer per-experiment than a wet-lab iteration log) — soften
    # the expected bar, but never exempt it: zero friction is still scored near-floor.
    expected_ratio = 0.15 if is_synthesis else 0.35
    score = min(1.0, raw_ratio / expected_ratio)
    if friction == 0:
        score = min(score, 0.05)  # zero disclosed friction is always near-floor, any genre
    return round(score, 3)
```

**What the function does & why.** It counts "friction" nodes (dead ends, plus decisions that
actually carry rejected alternatives) and normalizes by experiment count, since a 3-experiment
paper and a 20-experiment paper shouldn't need the same absolute friction count. It softens — but
never zeroes out — the expected bar for synthesis genres (detected via a cheap keyword sniff of
the root question's own text, not an external field) because the brief documents that reviews
legitimately produce friction differently than primary studies. Zero friction nodes always caps
the score near-floor regardless of genre, per the hard constraint that missing content is
penalized rather than excused.

**Why it's hard to Goodhart.** You could pad the tree with cheap `dead_end` nodes, but each one
requires a `hypothesis`, `failure_mode`, and `lesson` string, and Metric 2 (Evidentiary Grounding
Fidelity) checks `source_refs` against those same nodes — an invented dead end with no traceable
source reference gets crushed there. So inflating this metric directly increases exposure on
another.

---

## 2. Evidentiary Grounding Fidelity

**How it signals good science.** A trace node's *epistemic status* is only as good as its
grounding. An `explicit` node without `source_refs` is a category error the brief calls out
directly ("mismatched signaling"), and an `experiment`/`decision` node with no `evidence` is an
assertion, not a documented finding. Good science leaves an audit trail from claim to source; this
metric rewards trees that actually do that, node by node, rather than in aggregate.

**Compute function.**

```python
def grounding_fidelity(tree):
    """
    Input assumption: raw parsed artifact. Missing tree -> 0.0.
    Per-node scoring, then averaged; missing fields at the node level are penalties,
    not exclusions (every node contributes a score, never dropped from the denominator).
    """
    nodes = _flatten(tree)
    if not nodes:
        return 0.0

    def node_score(n):
        support = n.get("support_level")
        refs = n.get("source_refs") or []
        ntype = n.get("type")
        score = 0.0

        # base: explicit claims must show their work
        if support == "explicit":
            score += 0.5 if len(refs) > 0 else 0.0
        elif support == "inferred":
            # inferred nodes get credit for *acknowledging* uncertainty instead of refs;
            # but an inferred node dressed up with refs it doesn't need is fine (not penalized)
            score += 0.3

        # evidence field, where the type calls for one
        if ntype in ("experiment", "decision"):
            ev = n.get("evidence")
            has_ev = bool(ev) if not isinstance(ev, list) else len(ev) > 0
            score += 0.5 if has_ev else 0.0
        elif ntype == "dead_end":
            # dead_ends have no `evidence` field in the shape; their grounding is source_refs
            # against hypothesis/failure_mode/lesson — already captured by the support branch.
            score += 0.5 if len(refs) > 0 else 0.1
        elif ntype == "pivot":
            # a pivot's "evidence" is a real also_depends_on link to the nodes that triggered it
            score += 0.5 if n.get("also_depends_on") else 0.0
        else:  # question
            score += 0.5 if n.get("description") else 0.0

        return score  # in [0, 1]

    scores = [node_score(n) for n in nodes]
    return round(sum(scores) / len(scores), 3)
```

**What the function does & why.** Every node gets a 0–1 grounding score built from two halves:
(a) does its `support_level` claim match its actual `source_refs`, and (b) does its type-specific
content field (`evidence`, or `also_depends_on` for pivots) actually exist. Averaging per-node
(rather than checking "does the tree have refs somewhere") means a tree can't hide three
well-cited nodes to cover for eight bare assertions.

**Why it's hard to Goodhart.** Adding fake `source_refs` (e.g. `["§1"]` on every node) to farm
this metric doesn't cost anything *here*, but Metric 1's friction nodes and Metric 4's pivot
grounding both reuse the same `source_refs`/`also_depends_on` fields for cross-checks against the
actual node content (failure_mode/lesson/trigger text) — decorative refs that don't correspond to
real distinguishing content get penalized when other metrics check for that correspondence
qualitatively.

---

## 3. Alternative Substantiveness

**How it signals good science.** `decision` nodes require `alternatives`, but a required field
can be satisfied with boilerplate ("do nothing", "other approach"). Good science shows the actual
road not taken — alternatives specific enough that a reader could imagine the paper going that way.
This metric scores the *distinctiveness and concreteness* of alternatives relative to the chosen
option, not just their presence.

**Compute function.**

```python
import re

def alternative_substantiveness(tree):
    """
    Input assumption: raw parsed artifact. No decision nodes -> 0.2 floor (not skipped —
    absence of any recorded rejected alternative across the whole tree is itself a
    weak-but-not-damning signal, scored low rather than N/A).
    """
    nodes = _flatten(tree)
    decisions = [n for n in nodes if n.get("type") == "decision"]
    if not decisions:
        return 0.2

    GENERIC = {"other", "alternative", "different approach", "do nothing",
               "not doing this", "the other option", "status quo"}

    def tokens(s):
        return set(re.findall(r"[a-z0-9]+", (s or "").lower()))

    def score_decision(n):
        choice = n.get("choice") or ""
        alts = n.get("alternatives") or []
        if not alts:
            return 0.0  # required field absent -> hard floor, not excused
        choice_toks = tokens(choice)
        per_alt = []
        for a in alts:
            a_toks = tokens(a)
            if not a_toks or a.strip().lower() in GENERIC:
                per_alt.append(0.0)
                continue
            # distinctiveness: low overlap with the chosen option's own wording
            overlap = len(a_toks & choice_toks) / max(1, len(a_toks | choice_toks))
            distinct = 1.0 - overlap
            # concreteness proxy: longer, non-trivial descriptions carry more specific content
            concreteness = min(1.0, len(a_toks) / 8.0)
            per_alt.append(0.6 * distinct + 0.4 * concreteness)
        return sum(per_alt) / len(per_alt)

    return round(sum(score_decision(n) for n in decisions) / len(decisions), 3)
```

**What the function does & why.** For each `decision`, it compares each rejected alternative's
vocabulary against the chosen option's vocabulary (low word overlap = a genuinely distinct road not
taken, not a rephrasing of the winner) and against a length-based concreteness proxy, then averages
across alternatives and decisions. Zero alternatives on a decision node — even though a bare list
would technically satisfy a schema check — scores that decision at the floor.

**Why it's hard to Goodhart.** Padding with long, wordy but vacuous alternative text raises the
concreteness proxy but not the distinctiveness term if it echoes the choice's own language; padding
with totally unrelated but nonsensical text raises distinctiveness but such text is exactly what a
downstream Level-1 trace-hygiene / source-ref check (reused implicitly by Metric 2's grounding
score, since decisions carry `evidence`) would fail to justify — a decision's `evidence` field is
expected to explain *why* the choice beat the alternatives, so fabricated alternatives with no
matching evidentiary justification get penalized jointly.

---

## 4. Pivot Causal Traceability

**How it signals good science. ** A `pivot` is the highest-leverage node type for showing that a
paper's understanding *changed* — but it's also the easiest node type to fabricate, since the
brief itself notes pivots are usually the compiler's own narrative reconstruction. Good science
means the pivot is anchored: its `trigger` text should be traceable to real upstream nodes (via
`also_depends_on`), and its `support_level` should be honestly `inferred` rather than dressed up as
`explicit` (the brief explicitly flags false-explicit pivots as a form of overclaiming).

**Compute function.**

```python
def pivot_causal_traceability(tree):
    """
    Input assumption: raw parsed artifact with an id->node index buildable from _flatten.
    No pivot nodes -> 0.3 (a tree with real strategic reversals but no recorded pivot is
    a plausible gap worth a mild penalty, not a free pass or N/A).
    """
    nodes = _flatten(tree)
    if not nodes:
        return 0.0
    by_id = {n["id"]: n for n in nodes if "id" in n}
    pivots = [n for n in nodes if n.get("type") == "pivot"]
    if not pivots:
        return 0.3

    def tokens(s):
        return set(str(s or "").lower().split())

    def score_pivot(p):
        score = 0.0
        deps = p.get("also_depends_on") or []
        # 1) must link to real, resolvable prior nodes
        resolved = [d for d in deps if d in by_id]
        if resolved:
            score += 0.4
        # 2) trigger text should semantically connect to what those nodes actually found
        trigger_toks = tokens(p.get("trigger", ""))
        overlap_found = False
        for d in resolved:
            src = by_id[d]
            src_text = " ".join(str(src.get(f, "")) for f in
                                 ("result", "failure_mode", "lesson", "choice"))
            if trigger_toks & tokens(src_text):
                overlap_found = True
                break
        if overlap_found:
            score += 0.4
        # 3) honesty bonus: pivots are narrative reconstructions by default — claiming
        # `explicit` support without a dense evidence trail is overclaiming, not rigor
        if p.get("support_level") == "inferred":
            score += 0.2
        elif p.get("support_level") == "explicit" and len(p.get("source_refs") or []) >= 2:
            score += 0.2  # explicit is fine IF heavily sourced, not just asserted
        return score

    return round(sum(score_pivot(p) for p in pivots) / len(pivots), 3)
```

**What the function does & why.** For each pivot it checks three things: does it actually point
(via `also_depends_on`) at real nodes elsewhere in the tree; does its `trigger` text share
vocabulary with what those upstream nodes actually found (catching pivots whose stated cause
doesn't match any real upstream content); and does its honesty-labeling match the brief's own
guidance (an `inferred` pivot is the expected default, an `explicit` one needs real backing
refs to earn the same credit). A tree with zero pivots gets a mild, non-zero penalty rather than
being excluded, since real multi-stage research usually does involve at least one reframing.

**Why it's hard to Goodhart.** Adding `also_depends_on` to unrelated nodes to farm the linkage
bonus is caught by the trigger/text-overlap check, which requires actual vocabulary correspondence
with the pointed-to node's real content — you can't get both bonuses by pointing at an arbitrary
node. Relabeling a pivot `explicit` to look more rigorous costs you unless you also add ≥2 real
`source_refs`, which in turn feeds directly into Metric 2's grounding score, so a shortcut on one
metric shows up as a liability check on another.

---

## Combination

These four metrics interlock deliberately. Candor Density rewards trees that disclose friction
(dead ends, real decision alternatives), but adding cheap friction nodes to farm it requires
matching `source_refs`/`evidence`, which Evidentiary Grounding Fidelity checks per-node — so
padding one metric directly taxes the other. Alternative Substantiveness rewards decisions whose
rejected paths are lexically distinct and concrete, but distinct-sounding nonsense alternatives
lack the evidentiary justification Grounding Fidelity expects a decision's `evidence` field to
carry. Pivot Causal Traceability specifically targets the node type the brief flags as most prone
to narrative invention, cross-checking it against the very nodes Candor Density and Grounding
Fidelity already score — a fabricated pivot pointing at unrelated or ungrounded nodes is exposed
by trigger/content mismatch even if it superficially has `also_depends_on` filled in. In short: a
paper trying to win all four at once would need to invent friction *and* ground it in real
citations *and* make the rejected alternatives concretely distinct *and* have those alternatives
causally tie into genuinely correlated pivots — which is no longer gaming, it's just doing (and
accurately reporting) the science.
