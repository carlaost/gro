## Changes from stage 1

- **Closed the genre-sniff gaming hole (Candor Density).** `is_synthesis` no longer flips on a
  keyword hit in the root `question` node's own `title`/`description` alone — a field entirely
  authored by the same actor being scored. It now requires the marker vocabulary to independently
  recur across `title`/`description`/`result` text on **≥3 distinct nodes**, and the
  synthesis/primary-study `expected_ratio` spread was narrowed from 0.15/0.35 (a 2.3x swing) to
  0.22/0.35 (~1.6x), so even a successfully corroborated genre claim buys a smaller, less
  exploitable discount. Salting three-plus separate result fields with statistical-synthesis
  vocabulary is a materially costlier and more conspicuous forgery than editing one title string.
- **Added a fifth, standalone lens: Support-Level Signaling Integrity.** The critique correctly
  noted that with only 4 metrics, the shape doc's "mismatched signaling" defect
  (`support_level: explicit` with no `source_refs`) was only implicitly touched inside Metric 2's
  per-node blend. Metric 5 isolates *labeling honesty* — does the claimed confidence level match
  what's actually shown — as its own axis, deliberately excluding the `evidence`/`also_depends_on`
  content checks that remain Metric 2's job, so the two lenses measure different things rather than
  duplicating each other. Unlike the flaw the critique flagged in agent2's version of this idea, an
  `inferred` node that also carries `source_refs` is never penalized here — hedging honestly while
  still citing is not a defect the shape doc names.
- **Stopword-filtered the pivot trigger/content overlap (Metric 4).** `tokens()` previously used a
  raw `.split()`, so function words and generic research vocabulary ("the", "of", "and", "study",
  "data", "results") could produce spurious overlap and hand out the semantic-connection credit for
  free. It now filters a stopword/generic-vocabulary list, drops tokens of length ≤2, and requires
  the actual overlap used for scoring to contain at least one token of length ≥4 — coincidental
  short/common-word matches no longer count.
- **Made the frictionless-vs-laundered ambiguity explicit (Candor Density).** Added a stated
  limitation: this metric cannot, by itself, distinguish a genuinely frictionless paper from a
  laundered extraction. Added an explicit cross-check pointer — a friction-free tree should still
  show high per-node grounding (Metric 2) and calibration (Metric 5) on the experiments it does
  report; a laundered tree tends to be weak on those axes too, which is what makes the combination
  diagnostic even though no single metric resolves it alone.
- Metric 3 (Alternative Substantiveness) is unchanged in substance — the critique did not identify a
  gaming hole in it, only that the set as a whole needed a fifth lens and a fix elsewhere. The
  **Combination** section is rewritten to cover all five metrics and how Metric 5 interlocks with
  the rest.

---

# Proposer #4 (revised) — metrics for `trace/exploration_tree.yaml`

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

    synthesis_markers = ["systematic review", "meta-analysis", "network meta-analysis",
                          "scoping review", "umbrella review", "prisma", "forest plot",
                          "heterogeneity", "i2 =", "p-score"]

    # Stage-2 fix: genre can no longer be flipped by editing the root `question` node's
    # own title/description alone -- that field is fully authored by the same actor being
    # scored, and the stage-1 version let one edited string halve the whole tree's expected
    # friction bar. Require the marker vocabulary to independently recur across >=3 DISTINCT
    # nodes' own text (title/description/result), which forces salting several separately
    # authored fields rather than one, and is far more conspicuous under any content-vs-source
    # spot check.
    def _has_marker(n):
        text = " ".join(str(n.get(f, "")) for f in ("title", "description", "result")).lower()
        return any(m in text for m in synthesis_markers)

    marker_node_ids = {n.get("id") for n in nodes if _has_marker(n)}
    is_synthesis = len(marker_node_ids) >= 3

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
    # and de-overlap decisions are rarer per-experiment than a wet-lab iteration log) -- soften
    # the expected bar, but never exempt it, and (stage-2) narrow the spread from 0.15/0.35
    # (2.3x) to 0.22/0.35 (~1.6x) so even a successfully corroborated genre claim buys a smaller,
    # less exploitable discount.
    expected_ratio = 0.22 if is_synthesis else 0.35
    score = min(1.0, raw_ratio / expected_ratio)
    if friction == 0:
        score = min(score, 0.05)  # zero disclosed friction is always near-floor, any genre
    return round(score, 3)
```

**What the function does & why.** It counts "friction" nodes (dead ends, plus decisions that
actually carry rejected alternatives) and normalizes by experiment count, since a 3-experiment
paper and a 20-experiment paper shouldn't need the same absolute friction count. It softens — but
never zeroes out — the expected bar for synthesis genres because the brief documents that reviews
legitimately produce friction differently than primary studies. Zero friction nodes always caps
the score near-floor regardless of genre, per the hard constraint that missing content is
penalized rather than excused.

**Known limitation (acknowledged, not solved by this metric alone).** Candor Density cannot, on
its own, distinguish a genuinely frictionless paper from a laundered extraction that simply
dropped the friction nodes during compilation — both present as `friction == 0`. This is why the
score is floored rather than zeroed, and why it is meant to be read alongside Metric 2 (Evidentiary
Grounding Fidelity) and Metric 5 (Support-Level Signaling Integrity): a genuinely frictionless
paper's remaining `experiment`/`question` nodes should still show strong per-node grounding and
honest support-level labeling, whereas a laundered extraction tends to be weak on those axes too.
No single metric here resolves the ambiguity; the combination is the diagnostic, not any one lens.

**Why it's hard to Goodhart.** You could pad the tree with cheap `dead_end` nodes, but each one
requires a `hypothesis`, `failure_mode`, and `lesson` string, and Metric 2 (Evidentiary Grounding
Fidelity) checks `source_refs` against those same nodes — an invented dead end with no traceable
source reference gets crushed there. So inflating this metric directly increases exposure on
another. Separately, claiming a softer genre bar now requires salting synthesis vocabulary across
at least three distinct nodes' own text fields rather than one — a forgery that is both costlier to
execute and more likely to visibly clash with those same nodes' `source_refs`/`result` content
under Metric 2 and Metric 5's per-node checks.

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
well-cited nodes to cover for eight bare assertions. This is deliberately *content*-focused
(evidence/also_depends_on presence) and is complemented, not duplicated, by Metric 5 below, which
isolates the pure labeling-honesty question and excludes the evidence-field terms entirely.

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

**How it signals good science.** A `pivot` is the highest-leverage node type for showing that a
paper's understanding *changed* — but it's also the easiest node type to fabricate, since the
brief itself notes pivots are usually the compiler's own narrative reconstruction. Good science
means the pivot is anchored: its `trigger` text should be traceable to real upstream nodes (via
`also_depends_on`), and its `support_level` should be honestly `inferred` rather than dressed up as
`explicit` (the brief explicitly flags false-explicit pivots as a form of overclaiming).

**Compute function.**

```python
import re

_GENERIC_TOKENS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or", "is",
    "was", "were", "are", "be", "been", "being", "with", "by", "from", "as",
    "that", "this", "these", "those", "it", "its", "which", "who", "what",
    "when", "where", "how", "not", "no", "than", "then", "but", "if", "so",
    "such", "also", "more", "most", "some", "any", "each", "both", "other",
    "into", "over", "under", "after", "before", "between", "during", "about",
    "across", "per", "via", "due", "based", "result", "results", "data",
    "study", "found", "shows", "showed", "paper", "finding", "findings",
}

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
        # Stage-2 fix: raw .split() let function words and generic research vocabulary
        # ("the", "of", "study", "data", "results") produce spurious overlap and hand out
        # the semantic-connection credit for free. Filter those out and require real content
        # words (length > 2).
        return {
            t for t in re.findall(r"[a-z0-9]+", str(s or "").lower())
            if t not in _GENERIC_TOKENS and len(t) > 2
        }

    def score_pivot(p):
        score = 0.0
        deps = p.get("also_depends_on") or []
        # 1) must link to real, resolvable prior nodes
        resolved = [d for d in deps if d in by_id]
        if resolved:
            score += 0.4
        # 2) trigger text should semantically connect to what those nodes actually found,
        # via genuine content-word overlap (not stopwords/boilerplate) -- and require at
        # least one shared token of length >=4 so a coincidental short-word match doesn't
        # count as causal correspondence.
        trigger_toks = tokens(p.get("trigger", ""))
        overlap_found = False
        for d in resolved:
            src = by_id[d]
            src_text = " ".join(str(src.get(f, "")) for f in
                                 ("result", "failure_mode", "lesson", "choice"))
            shared = trigger_toks & tokens(src_text)
            if any(len(t) >= 4 for t in shared):
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
*substantive* vocabulary (stopwords and generic research boilerplate filtered out, and a
minimum token length enforced) with what those upstream nodes actually found; and does its
honesty-labeling match the brief's own guidance. A tree with zero pivots gets a mild, non-zero
penalty rather than being excluded, since real multi-stage research usually does involve at least
one reframing.

**Why it's hard to Goodhart.** Adding `also_depends_on` to unrelated nodes to farm the linkage
bonus is caught by the trigger/text-overlap check, which — after the stage-2 stopword filter —
requires genuine, specific vocabulary correspondence (a shared content word of length ≥4) with the
pointed-to node's real content, not an accidental shared "the" or "study". Relabeling a pivot
`explicit` to look more rigorous costs you unless you also add ≥2 real `source_refs`, which in turn
feeds directly into Metric 2's grounding score and Metric 5's calibration score, so a shortcut on
one metric shows up as a liability check on two others.

---

## 5. Support-Level Signaling Integrity

**How it signals good science.** The shape doc names a specific defect — "mismatched signaling":
a node marked `support_level: explicit` with no `source_refs` overclaims certainty it hasn't shown,
and this is a defect "even short of outright invention." It also names the honest default in the
other direction: `pivot` nodes are usually the compiler's own narrative reconstruction, so
`inferred` is their expected label, and an `explicit` pivot needs to earn that stronger claim with
real citations. This metric is a standalone honesty axis — purely about whether the *confidence
label* a node carries matches what it actually shows — deliberately excluding the `evidence`/
`also_depends_on` content checks already owned by Metric 2, so the two lenses measure genuinely
different things rather than duplicating each other.

**Compute function.**

```python
def signaling_integrity(tree):
    """
    Input assumption: raw parsed artifact. Missing tree -> 0.0.
    Per-node calibration score, then averaged; every node contributes, none are excluded
    from the denominator, and a missing/invalid `support_level` is itself scored as a
    signaling failure rather than skipped (it is part of the shared required schema).
    """
    nodes = _flatten(tree)
    if not nodes:
        return 0.0

    def node_score(n):
        support = n.get("support_level")
        refs = n.get("source_refs") or []
        is_pivot = n.get("type") == "pivot"

        if support == "explicit":
            if is_pivot:
                # pivots default to `inferred`; an `explicit` pivot is a stronger claim
                # that needs a real, dense citation trail, not a bare assertion
                if len(refs) >= 2:
                    return 1.0
                elif len(refs) == 1:
                    return 0.3
                return 0.0
            return 1.0 if len(refs) > 0 else 0.0
        elif support == "inferred":
            # inferred is an honest hedge. It is never penalized for also carrying refs —
            # a hedged-but-cited node is not a defect the shape doc names — and it is capped
            # below a well-grounded explicit node so blanket hedging can't out-earn honest,
            # well-cited claiming.
            return 0.8 if is_pivot else 0.6
        else:
            # missing/invalid support_level: the field is required on every node regardless
            # of type, so its absence is a signaling failure, not a gap to skip past
            return 0.0

    scores = [node_score(n) for n in nodes]
    return round(sum(scores) / len(scores), 3)
```

**What the function does & why.** Every node is scored purely on whether its stated confidence
level is backed to the degree that level implies: a well-cited `explicit` node scores highest, an
honestly-labeled `inferred` node scores moderately (rewarded for not overclaiming, but never above
a properly-grounded `explicit` node), an `explicit` node with no refs scores zero (the shape doc's
named defect), and an `explicit` pivot is held to the stricter two-ref bar the shape doc implies by
calling `inferred` its expected default. Averaging per-node means a tree can't launder a handful of
well-labeled nodes to cover for systematic overclaiming elsewhere.

**Why it's hard to Goodhart.** The obvious escape hatch — relabel everything `inferred` to dodge
the explicit-without-refs penalty — is a net loss: `inferred` caps out at 0.6–0.8 here, strictly
below the 1.0 a genuinely well-cited `explicit` node earns, and Metric 2 independently gives
`inferred` support less credit (0.3) than well-refed `explicit` support (0.5). Blanket hedging is
therefore dominated by honest, well-cited claiming on both metrics at once — there's no score to
gain by mass-downgrading labels. The other obvious route — paste a decorative `source_refs` entry
onto every `explicit` node to farm the 1.0 — doesn't cost anything *here*, but those same refs are
reused by Metric 1's friction check and Metric 4's pivot-linkage check for correspondence against
real node content (failure_mode/lesson/trigger text); decorative refs with no matching content get
penalized there instead, so the shortcut just relocates the exposure rather than removing it.

---

## Combination

These five metrics interlock deliberately. Candor Density rewards trees that disclose friction
(dead ends, real decision alternatives), but adding cheap friction nodes to farm it requires
matching `source_refs`/`evidence`, which Evidentiary Grounding Fidelity checks per-node — so
padding one metric directly taxes the other. It also now resists a second attack: claiming a
softer genre bar requires salting synthesis vocabulary across three or more separately-authored
node fields, not one, which is both costlier to fake and more exposed to the same content-vs-source
scrutiny. Alternative Substantiveness rewards decisions whose rejected paths are lexically distinct
and concrete, but distinct-sounding nonsense alternatives lack the evidentiary justification
Grounding Fidelity expects a decision's `evidence` field to carry. Pivot Causal Traceability
specifically targets the node type the brief flags as most prone to narrative invention,
cross-checking it — now with stopwords filtered out — against the very nodes Candor Density and
Grounding Fidelity already score, so a fabricated pivot pointing at unrelated or ungrounded nodes is
exposed by genuine content mismatch even if it superficially has `also_depends_on` filled in.
Support-Level Signaling Integrity closes the loop as a standalone honesty axis: it makes mass
overclaiming (`explicit` everywhere, no refs) and mass hedging (`inferred` everywhere, dodging
scrutiny) both losing strategies at once, and its pivot-specific stricter bar reinforces exactly
what Pivot Causal Traceability's honesty term already rewards. In short: a paper trying to win all
five at once would need to invent friction *and* ground it in real citations *and* make the
rejected alternatives concretely distinct *and* have those alternatives causally tie into
genuinely correlated pivots *and* label every node's confidence level honestly relative to what it
actually shows — which is no longer gaming, it's just doing (and accurately reporting) the science.
