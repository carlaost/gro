# Metric proposals — `trace/exploration_tree.yaml` (agent1)

Shared helper assumed available to all compute functions below:

```python
def flatten(tree):
    """tree: list of top-level node dicts (the value of the `tree:` key).
    Returns a flat list of all node dicts, walking `children` recursively."""
    out = []
    def walk(nodes):
        for n in nodes or []:
            out.append(n)
            walk(n.get("children"))
    walk(tree)
    return out

def jaccard(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
```

---

## 1. Falsification & Alternative-Weighing Density

**How it signals good science.** Good science is defined as much by what was ruled out as by
what was confirmed. A tree that records `dead_end` nodes and `decision` nodes with genuine
rejected `alternatives` is capturing the paper's negative-result and rejected-path history — the
exact content the shape doc calls "the single most valuable node type for downstream agents."
A tree that is 100% `experiment`/`question` nodes, with no failure or choice-weighing recorded,
is very likely either a paper that hid its failures or a shallow compile that only lifted the
positive-result narrative. Either way, more (well-supported) falsification content is better.

**Compute function.**

```python
def falsification_density(tree):
    """Input: `tree` = list of top-level node dicts as parsed from the `tree:` key.
    Assumes each node has at least `id`, `type`, `source_refs` (list or None); `decision`
    nodes may have `alternatives` (list or None)."""
    nodes = flatten(tree)
    total = len(nodes)
    if total == 0:
        return 0.0  # unparsable/empty tree: worst case, not skipped

    weighted = 0.0
    for n in nodes:
        refs = n.get("source_refs") or []
        if n["type"] == "dead_end":
            weighted += 1.0 if refs else 0.5  # unsupported dead end still counts, but less
        elif n["type"] == "decision" and len(n.get("alternatives") or []) >= 2:
            weighted += 1.0 if refs else 0.5

    return min(1.0, weighted / total)
```

**What the function does & why.** It flattens the DAG, then for every node checks whether it is
a `dead_end`, or a `decision` that actually names two-or-more rejected `alternatives` (a
`decision` with zero or one alternative is closer to a bare assertion than a real weighing of
options). Each qualifying node contributes full weight if it also carries `source_refs` (grounded
in the paper) and half weight if not (asserted but unanchored). The sum is normalized by total
node count, so a tree padded with filler `experiment`/`question` nodes doesn't dilute the
denominator's meaning — it directly lowers the score, correctly penalizing padding as well as
absence.

**Why it's hard to Goodhart.** Simply inventing `dead_end` nodes to inflate this score is caught
by Metric 2 (Evidence Traceability), since fabricated nodes tend to lack real `source_refs` and
so only earn half credit here while actively dragging Metric 2 down. Inventing plausible-looking
but generic `alternatives` text (e.g., "do nothing") is caught by Metric 5, which explicitly
scores alternatives for lexical distinctness from the chosen path.

---

## 2. Evidence Traceability & Citation Granularity

**How it signals good science.** Real research trajectories are anchored in specific tables,
figures, and sections — not vague gestures at "the paper." The shape doc explicitly flags a node
marked `support_level: explicit` with no `source_refs` as a defect ("mismatched signaling"), and
notes richer/more specific refs (e.g., `"Table 2 Outcome 1"`, `"Figure 3A"`) versus vague ones
(e.g., just `"Abstract"`). A tree whose explicit claims are pinned to specific loci is more
auditable and less likely to be a hallucinated trajectory.

**Compute function.**

```python
def evidence_traceability(tree):
    """Input: `tree` as above. Assumes each node has `support_level` in {explicit, inferred}
    and `source_refs` (list[str] or None)."""
    nodes = flatten(tree)
    explicit_nodes = [n for n in nodes if n.get("support_level") == "explicit"]
    if not explicit_nodes:
        return 0.0  # nothing to ground the tree's claims in at all: worst case

    markers = ("table", "figure", "fig", "§", "section", "supplementary", "appendix", "eq")

    scores = []
    for n in explicit_nodes:
        refs = n.get("source_refs") or []
        if not refs:
            scores.append(0.0)  # explicit claim, zero refs: mismatched signaling, penalized
            continue
        specific = sum(
            1 for r in refs
            if any(m in r.lower() for m in markers) or any(c.isdigit() for c in r)
        )
        frac_specific = specific / len(refs)
        scores.append(0.3 + 0.7 * frac_specific)  # nonempty floor + specificity bonus

    return sum(scores) / len(scores)
```

**What the function does & why.** It isolates nodes claiming `explicit` support (the ones making
a factual claim about the paper, as opposed to `inferred` narrative reconstruction), then checks
each one's `source_refs`. An explicit node with no refs scores zero outright. One with refs gets a
baseline plus a bonus proportional to how many of those refs are locus-specific (contain a table/
figure/section marker or a digit) versus generic. Averaging across all explicit nodes rewards
trees that are consistently, specifically cited rather than a few well-cited nodes hiding many
vague ones.

**Why it's hard to Goodhart.** Padding `source_refs` with junk strings that merely contain a
digit or the word "table" to farm the specificity bonus produces refs that a downstream Trace
Hygiene spot-check (verifying refs against the actual paper) would flag as invented — the shape
doc explicitly calls out invented nodes/refs as a hard failure mode elsewhere in the pipeline.
Within this metric set, junk refs also don't help Metric 4 (pivot grounding) or Metric 1, so
there's no incentive spillover from gaming this one alone.

---

## 3. DAG Convergence Index

**How it signals good science.** The shape doc distinguishes a merely-nested `children` tree from
a *true DAG* enabled by `also_depends_on` cross-edges — e.g., a later experiment building on an
earlier one (`N05` depending on `N04`), or a pivot synthesizing two divergent experimental threads
(`N14` depending on `N09` and `N12`). Real research is rarely a strict tree: results get reused,
combined, and revisited. A tree with zero cross-edges is either a genuinely simple, linear study
or — more often for anything nontrivial — a compile that only captured the surface narrative and
missed how later steps actually build on earlier ones.

**Compute function.**

```python
def dag_convergence(tree):
    """Input: `tree` as above. Assumes each node has `id` (str) and optional
    `also_depends_on` (list[str] of node ids)."""
    nodes = flatten(tree)
    total = len(nodes)
    if total == 0:
        return 0.0

    ids = {n["id"] for n in nodes}
    valid_edges, dangling = 0, 0
    for n in nodes:
        for ref in (n.get("also_depends_on") or []):
            if ref in ids:
                valid_edges += 1
            else:
                dangling += 1

    if valid_edges == 0:
        return 0.05  # purely linear/tree-shaped, no captured convergence: near-floor

    density = min(1.0, (valid_edges / total) * 2.5)
    dangling_penalty = dangling / (valid_edges + dangling)
    return density * (1 - dangling_penalty)
```

**What the function does & why.** It counts `also_depends_on` edges whose target actually exists
in the tree ("valid") versus ones that point to a nonexistent id ("dangling" — a broken or
fabricated reference). A tree with zero valid cross-edges is scored near zero, since it's
indistinguishable from a shallow, un-synthesized extraction. Otherwise, edge density (edges per
node, capped) is scaled down by the fraction of edges that are dangling, so a compiler that adds
convergence edges carelessly (pointing at ids that don't exist) is punished rather than rewarded
for the raw edge count.

**Why it's hard to Goodhart.** Adding `also_depends_on` edges between unrelated real nodes to
inflate density is constrained because it only helps if the *target* node is itself a substantive
node — and Metric 4 separately checks that pivot triggers point at `experiment`/`dead_end`/
`decision` nodes specifically, not arbitrary ones, so random cross-wiring doesn't pay off there.
Pointing edges at fabricated ids is directly punished by the dangling-edge penalty in this same
metric.

---

## 4. Pivot Grounding Score

**How it signals good science. ** A `pivot` node is a claim that the research *changed direction*
because of evidence — the shape doc's own example ties `N14`'s pivot to a `trigger` explaining
divergent subgroup results and wires it via `also_depends_on: [N09, N12]` to the specific
experiments that caused the reframe. A pivot that isn't tied to any real prior evidence node, or
whose `from`/`to` text is just a rephrasing of the same idea, is narrative decoration rather than
a documented change of scientific direction — the opposite of good science tracking.

**Compute function.**

```python
def pivot_grounding(tree):
    """Input: `tree` as above. Assumes pivot nodes have `from`, `to`, `trigger` (str) and
    optional `also_depends_on` (list[str])."""
    nodes = flatten(tree)
    id_map = {n["id"]: n for n in nodes}
    pivots = [n for n in nodes if n["type"] == "pivot"]

    if not pivots:
        return 0.15  # no reframing captured at all: low, not skipped

    causal_types = {"experiment", "dead_end", "decision"}
    scores = []
    for p in pivots:
        deps = p.get("also_depends_on") or []
        grounded = any(
            d in id_map and id_map[d]["type"] in causal_types for d in deps
        )
        trigger = (p.get("trigger") or "").strip()
        has_trigger = len(trigger) > 15

        frm = (p.get("from") or "").strip()
        to = (p.get("to") or "").strip()
        is_real_shift = bool(frm) and bool(to) and jaccard(frm, to) < 0.6

        scores.append(sum([grounded, has_trigger, is_real_shift]) / 3)

    return sum(scores) / len(scores)
```

**What the function does & why.** For each pivot, it checks three independent things: (a) does it
point via `also_depends_on` at a real, causally-relevant node (an experiment, dead end, or
decision — not another question or pivot), (b) does it state a substantive `trigger` (more than a
token gesture), and (c) are `from` and `to` actually lexically distinct (a genuine reframe, not
the same sentence twice). A tree with no pivots at all gets a low fixed floor rather than being
skipped, per the hard constraint, since we cannot verify reframing rigor that isn't present.

**Why it's hard to Goodhart.** Fabricating a pivot with a long, verbose `trigger` string doesn't
help unless it also links to a real causal node (checked structurally against `id_map`), and
copy-pasting `from` into a paraphrased `to` is caught by the Jaccard-distinctness check.
Manufacturing a fake supporting experiment node to ground the pivot would raise this score but
directly costs Metric 2 (that fabricated node likely lacks specific `source_refs`) and Metric 3
(a fabricated id used only for this purpose adds an edge but no real density elsewhere).

---

## 5. Alternatives Substance Score

**How it signals good science.** `decision` nodes are supposed to represent a real fork in the
road — the shape doc's own example (`N03`) lists two concretely different, clearly-worse
`alternatives` ("pool all studies naively," "exclude overlapping cohorts entirely") next to the
`choice` actually made, plus `evidence` explaining why. A `decision` with a token or absent
`alternatives` list, or alternatives that are just a restatement of the choice, signals the
compiler (or the paper) isn't actually documenting a considered trade-off.

**Compute function.**

```python
def alternatives_substance(tree):
    """Input: `tree` as above. Assumes `decision` nodes have `choice` (str) and
    `alternatives` (list[str] or None); `evidence` (str or None)."""
    nodes = flatten(tree)
    decisions = [n for n in nodes if n["type"] == "decision"]
    if not decisions:
        return 0.1  # no decision nodes to assess trade-off documentation at all

    scores = []
    for d in decisions:
        alts = d.get("alternatives") or []
        choice = d.get("choice") or ""
        if not alts:
            scores.append(0.0)
            continue

        count_score = min(1.0, len(alts) / 2)  # reward >=2 genuine alternatives
        distinctness = [1 - jaccard(a, choice) for a in alts]
        avg_distinct = sum(distinctness) / len(distinctness)
        has_evidence = 1.0 if (d.get("evidence") or "").strip() else 0.3

        scores.append(0.4 * count_score + 0.4 * avg_distinct + 0.2 * has_evidence)

    return sum(scores) / len(scores)
```

**What the function does & why.** For every `decision`, it rewards having at least two
alternatives (one alternative is a weak trade-off signal; zero is none at all), rewards those
alternatives being lexically distinct from the actual `choice` (not a copy with minor edits — a
real rival option), and gives a smaller bonus for the free-text `evidence` field being populated
(explaining *why* the choice won). Averaging across decisions means a tree can't hide a few thin
decisions behind one rich one.

**Why it's hard to Goodhart.** Padding `alternatives` with near-duplicates of the `choice` text to
hit the count threshold is directly punished by the Jaccard-distinctness term. Writing verbose,
plausible-sounding but fabricated alternatives risks the same Trace Hygiene exposure as fabricated
`dead_end`/`decision` nodes generally (Metric 1's grounding requirement and Metric 2's citation
check apply to the same nodes), so invented substance doesn't pay off in isolation.

---

## Combination

These five metrics are jointly hard to game because they pull on the same small set of levers from
different, conflicting angles. Padding the tree with fabricated `dead_end`/`decision` nodes to
raise Falsification Density (1) or Alternatives Substance (5) only pays off if those nodes also
carry specific `source_refs`, which Evidence Traceability (2) checks independently and a Trace
Hygiene spot-check would falsify outright. Wiring fake `also_depends_on` edges to inflate DAG
Convergence (3) either points at nonexistent ids (directly penalized by the dangling-edge term) or
at real-but-irrelevant nodes, which fails Pivot Grounding's (4) requirement that a pivot's
dependencies be causally-typed (`experiment`/`dead_end`/`decision`) nodes. And manufacturing a
dramatic-sounding pivot to look like a documented reframe (4) requires either real supporting
evidence — which then has to survive Evidence Traceability — or a genuinely distinct `from`/`to`
pair, which is exactly the kind of specific, checkable content that's expensive to fabricate
convincingly across five independent lenses at once. A tree can cheaply win one axis by inventing
content, but inventing content without matching citations, distinctness, and structural grounding
loses points elsewhere — the only way to score well on all five is to have an actual, well-cited,
non-trivial decision trajectory.
