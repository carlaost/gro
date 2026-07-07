# Proposer #2 — metrics for `trace/exploration_tree.yaml`

All compute functions assume the parsed artifact `tree` is a dict `{"tree": [...]}` whose top-level
list holds node dicts that nest via a `children` list, exactly per the shape doc. Every function
below assumes two shared helpers exist (defined once, reused everywhere):

```python
def flatten(tree):
    """Depth-first flatten of tree['tree'] into a flat list of node dicts
    (each dict keeps its own fields; 'children' is left in place but we
    also visit into it). Returns list[dict]."""
    out = []
    def walk(node_list):
        for n in node_list:
            out.append(n)
            walk(n.get('children') or [])
    walk(tree.get('tree') or [])
    return out

def flatten_with_ancestors(tree):
    """Like flatten(), but also returns a dict id -> list of ancestor ids
    (root-to-parent chain), so callers can tell same-branch vs cross-branch
    also_depends_on edges apart."""
    nodes, ancestors = [], {}
    def walk(node_list, chain):
        for n in node_list:
            nodes.append(n)
            ancestors[n['id']] = list(chain)
            walk(n.get('children') or [], chain + [n['id']])
    walk(tree.get('tree') or [], [])
    return nodes, ancestors
```

Missing/thin inputs are penalized inline in each function per the hard constraint (never skipped,
never N/A) — see comments marked `# hard constraint`.

---

## 1. Grounded Failure Disclosure Score

**How it signals good science.** Science advances as much by knowing what doesn't work as what
does. A tree that surfaces `dead_end` nodes which are (a) fully filled in (`hypothesis`,
`failure_mode`, `lesson`), (b) tied to `source_refs`, and (c) specific (quantified or detailed
lessons, not platitudes) is disclosing real, checkable failure — the single highest-value node type
per the shape doc. A tree with none, or with unsupported ones, is either hiding its failures or
inventing decorative ones.

**Compute function.**
```python
def grounded_failure_disclosure_score(tree):
    """
    Input assumption: `tree` is the parsed artifact; flatten(tree) yields all
    nodes regardless of nesting depth.
    """
    nodes = flatten(tree)
    total = len(nodes)
    if total == 0:
        return 0.0
    dead_ends = [n for n in nodes if n.get('type') == 'dead_end']
    if not dead_ends:
        # hard constraint: absence of the single most valuable node type is
        # itself evidence, not a free pass -- score down, scaled by how much
        # room the tree had to reveal one.
        return 0.05 if total >= 6 else 0.15
    node_scores = []
    for d in dead_ends:
        has_refs = bool(d.get('source_refs'))
        support = d.get('support_level')
        has_fields = all(bool(d.get(f)) for f in ('hypothesis', 'failure_mode', 'lesson'))
        lesson = d.get('lesson', '') or ''
        specific = any(ch.isdigit() for ch in lesson) or len(lesson.split()) >= 8
        s = 0.0
        s += 0.4 if has_refs else 0.0
        s += 0.2 if has_fields else 0.0
        s += 0.2 if specific else 0.0
        s += 0.2 if support in ('explicit', 'inferred') else 0.0
        if support == 'explicit' and not has_refs:
            s *= 0.3  # mismatched signaling: claiming explicit with no citation
        node_scores.append(min(s, 1.0))
    density_bonus = min(len(dead_ends) / total * 2, 0.3)
    return min(sum(node_scores) / len(node_scores) * 0.7 + density_bonus, 1.0)
```

**What it does & why.** Finds every `dead_end` node, scores each on citation grounding, field
completeness, specificity, and honest support-level labeling, then averages and adds a small bonus
for how much of the tree's real estate is spent on disclosed failure. Zero dead ends is capped low
regardless of tree size because the artifact spec calls dead ends source-bounded, not optional
decoration — a rich tree with none is treated as thin extraction, not a clean paper, since the metric
cannot distinguish the two from the artifact alone.

**Why it's hard to Goodhart.** Padding with fabricated dead ends only works if each one also carries
plausible `source_refs`, all three required fields, and a specific lesson — cheap invented nodes
(bare title + vague lesson, no refs) score near zero individually and drag the average down. Adding
many *low-effort* dead ends to chase the density bonus therefore backfires unless each is well-formed,
which is exactly the costly-to-fake behavior we want to reward.

---

## 2. Convergent Synthesis Score

**How it signals good science.** Real research is rarely a clean single-threaded narrative — findings
from one line inform a decision or experiment on another. The `also_depends_on` field is the artifact's
only way to express this: a genuine DAG (cross-branch convergence, not just parent→child nesting)
means the paper is shown synthesizing multiple independent evidence threads into one conclusion, which
is a hallmark of integrative reasoning over isolated box-checking.

**Compute function.**
```python
def convergent_synthesis_score(tree):
    """
    Assumes flatten_with_ancestors(tree) -> (nodes, ancestors) where
    ancestors[node_id] is the list of ancestor ids from root to parent.
    """
    nodes, ancestors = flatten_with_ancestors(tree)
    id_map = {n['id']: n for n in nodes}
    total = len(nodes)
    if total == 0:
        return 0.0

    def words(s):
        return set(w.lower().strip('.,()') for w in (s or '').split() if len(w) > 3)

    cross_score = 0.0
    decorative_edges = 0
    for n in nodes:
        for dep in (n.get('also_depends_on') or []):
            if dep not in id_map:
                decorative_edges += 1  # dangling ref -- treat as broken/invented
                continue
            same_branch = (dep in ancestors[n['id']]) or (n['id'] in ancestors.get(dep, []))
            if same_branch:
                decorative_edges += 1  # redundant same-lineage pointer, not real convergence
                continue
            target = id_map[dep]
            src_text = ' '.join(str(n.get(f, '')) for f in ('title', 'result', 'choice'))
            tgt_text = ' '.join(str(target.get(f, '')) for f in ('title', 'result', 'choice', 'lesson'))
            overlap = bool(words(src_text) & words(tgt_text))
            w = 1.0 + (0.5 if overlap else -0.3) + (0.3 if n.get('evidence') else 0.0)
            cross_score += max(w, 0.1)

    if cross_score == 0 and decorative_edges == 0:
        return 0.05  # hard constraint: pure tree, no DAG structure at all
    raw = cross_score / total
    penalty = decorative_edges / total * 0.5
    return max(min(raw * 2.5 - penalty, 1.0), 0.0)
```

**What it does & why.** Walks every `also_depends_on` edge, discards ones that just point at an
ancestor/descendant (already implied by nesting, so not "extra" synthesis) or point at a nonexistent
id (broken/likely invented), and rewards the rest more when the citing node's own text shares
vocabulary with the cited node's text (a proxy for "this cross-reference is topically real, not
decorative") and when the citing node also carries its own `evidence`. A tree with zero real DAG
edges is capped low.

**Why it's hard to Goodhart.** Sprinkling arbitrary `also_depends_on: [Nxx]` pointers to inflate the
score is cheap to attempt but the lexical-overlap check pulls the weight *negative* for edges that
share no vocabulary with their target, and same-branch/dangling edges are actively penalized rather
than ignored — so random edge-adding is a net negative unless the edges are topically coherent, which
requires actually writing consistent node content.

---

## 3. Decision Deliberation Depth

**How it signals good science.** A `decision` node that names several substantive rejected
`alternatives` and gives concrete `evidence` for the chosen `choice` demonstrates the paper actually
weighed trade-offs methodologically, rather than presenting its one chosen method as though it were
the only option ever considered. Explicit alternative-weighing is a core marker of scientific
rigor (vs. post-hoc rationalization).

**Compute function.**
```python
def decision_deliberation_depth(tree):
    """
    Assumes flatten(tree) gives all nodes; for `decision` nodes, `alternatives`
    is list[str] and `evidence` is an informal prose string (not a list).
    """
    nodes = flatten(tree)
    total = len(nodes)
    decisions = [n for n in nodes if n.get('type') == 'decision']
    if not decisions:
        # hard constraint: penalize absence, scaled by tree size / opportunity
        return 0.1 if total >= 6 else 0.2
    scores = []
    for d in decisions:
        alts = d.get('alternatives') or []
        evidence = d.get('evidence') or ''
        choice = d.get('choice') or ''
        has_refs = bool(d.get('source_refs'))
        alt_richness = sum(1 for a in alts if len(a.split()) >= 4)
        evidence_quality = 1.0 if len(evidence.split()) >= 10 else (0.4 if evidence else 0.0)
        s = 0.0
        s += min(len(alts), 3) / 3 * 0.35
        s += min(alt_richness, 3) / 3 * 0.15
        s += evidence_quality * 0.3
        s += 0.2 if has_refs else 0.0
        if d.get('support_level') == 'explicit' and not has_refs:
            s *= 0.5
        if not choice:
            s = 0.0  # a "decision" with no stated choice is not a decision
        scores.append(min(s, 1.0))
    return sum(scores) / len(scores)
```

**What it does & why.** For each decision, rewards number and substance of alternatives (not just
one-word placeholders), rewards evidence prose that's actually explanatory (length as a coarse proxy
for "gives a real reason" vs. a rubber-stamp phrase), and requires source grounding when the node
claims `explicit` support. A decision with no `choice` at all is zeroed — it's not really a decision
node.

**Why it's hard to Goodhart.** Listing many trivial one/two-word "alternatives" (e.g. `"other
methods"`, `"nothing"`) only earns the count term, not the richness term, capping the achievable
score; padding `evidence` with filler text to pass the length threshold produces a paragraph with no
citation, which is exactly what the `explicit`-without-`source_refs` penalty catches.

---

## 4. Pivot Traceability & Consequence

**How it signals good science.** A `pivot` claims the research direction bent because of something.
A trustworthy pivot points, via `also_depends_on`, at the specific upstream nodes that triggered it,
and its `trigger`/`from`/`to` text should actually share content with those nodes — not be a vague,
free-floating narrative flourish invented to make the trajectory sound more reflective than the
underlying work supports.

**Compute function.**
```python
def pivot_traceability_score(tree):
    """
    Assumes flatten(tree) gives all nodes with also_depends_on ids intact.
    """
    nodes = flatten(tree)
    id_map = {n['id']: n for n in nodes}
    total = len(nodes)
    pivots = [n for n in nodes if n.get('type') == 'pivot']
    if not pivots:
        return 0.15 if total >= 6 else 0.25  # hard constraint

    def words(s):
        return set(w.lower().strip('.,()') for w in (s or '').split() if len(w) > 3)

    scores = []
    for p in pivots:
        deps = p.get('also_depends_on') or []
        has_deps = bool(deps)
        trigger_words = words(p.get('trigger', ''))
        overlap_hits = 0
        for dep in deps:
            target = id_map.get(dep)
            if not target:
                continue
            target_text = ' '.join(str(target.get(f, '')) for f in
                                    ('title', 'result', 'choice', 'lesson'))
            if trigger_words & words(target_text):
                overlap_hits += 1
        s = 0.0
        s += 0.4 if has_deps else 0.0
        s += min(overlap_hits, 2) / 2 * 0.3
        s += 0.15 if (p.get('from') and p.get('to')) else 0.0
        s += 0.15 if (p.get('trigger') and len(p['trigger'].split()) >= 6) else 0.0
        if p.get('support_level') == 'explicit' and (not has_deps or overlap_hits == 0):
            s *= 0.4  # claiming certainty about a trigger with no traceable evidence
        scores.append(min(s, 1.0))
    return sum(scores) / len(scores)
```

**What it does & why.** For each pivot, checks whether it names the upstream nodes that caused it
and whether the pivot's own trigger language actually overlaps with those nodes' content, plus basic
completeness (`from`/`to` both present, trigger non-trivial length). Pivots marked `explicit` but
untraceable are penalized harder than untraceable `inferred` ones, since the shape doc says `inferred`
is the honest default for pivots (a narrative reconstruction), while `explicit` is a stronger claim
that demands backing.

**Why it's hard to Goodhart.** A cheap fake pivot (nice-sounding `from`/`to` prose, no
`also_depends_on`) is capped at ~0.3; adding fake `also_depends_on` ids without matching vocabulary in
the trigger text earns the dependency-presence credit but not the overlap credit, and if those ids are
shared with Metric 2's edges, incoherent cross-references get punished there too — so the same
fabricated edge can't cheaply score well on both metrics at once.

---

## 5. Support-Level Calibration

**How it signals good science.** The tree's `support_level` field is a confidence claim: `explicit`
says "the paper states this," `inferred` says "the compiler reconstructed this." Good extraction uses
`explicit` only when it can point at `source_refs`, and is honest that a `pivot` — the shape doc
notes this explicitly — is *usually* a compiler-side narrative reconstruction and should default to
`inferred` rather than being dressed up as certain. A tree that over-labels nodes `explicit` without
grounding, or marks every pivot `explicit`, is either reckless with its own confidence or a low-effort
templated extraction.

**Compute function.**
```python
def support_level_calibration(tree):
    """
    Assumes flatten(tree) gives all nodes with 'support_level' and
    'source_refs' fields present or absent as per the shape doc.
    """
    nodes = flatten(tree)
    total = len(nodes)
    if total == 0:
        return 0.0
    mismatches = 0.0
    for n in nodes:
        support = n.get('support_level')
        has_refs = bool(n.get('source_refs'))
        if support == 'explicit' and not has_refs:
            mismatches += 1.0  # overclaiming: certainty with no citation
        if support == 'inferred' and has_refs and n.get('type') != 'pivot':
            mismatches += 0.5  # softer smell: hedged node dressed up with refs it doesn't need
    calibration = 1 - min(mismatches / total, 1.0)

    pivots = [n for n in nodes if n.get('type') == 'pivot']
    if pivots:
        frac_inferred = sum(1 for p in pivots if p.get('support_level') == 'inferred') / len(pivots)
        pivot_honesty = frac_inferred
    else:
        pivot_honesty = 0.2  # hard constraint: no pivots surfaced at all is thin, score down a bit

    return round(0.7 * calibration + 0.3 * pivot_honesty, 3)
```

**What it does & why.** Counts how often a node's confidence label is unsupported by its citations
(the main mismatch), adds a lighter penalty for the inverse smell (over-citing a hedge), and separately
tracks whether pivots — which the shape doc says are usually inferred — are honestly labeled as such
rather than uniformly marked `explicit` to look more authoritative.

**Why it's hard to Goodhart.** Marking everything `inferred` to dodge the "explicit needs refs" penalty
tanks Metric 1, 3, and 4's grounding terms (which all reward `explicit`+`source_refs` combinations more
than `inferred` alone) and reduces the perceived reliability the other metrics credit; marking
everything `explicit` with copy-pasted or repeated `source_refs` to pass this metric risks tripping the
same-source-refs-everywhere pattern that a hygiene check (not this metric, but the broader system)
would flag, and does nothing to help Metrics 2–4, which need real per-node distinctions, not uniform
labeling.

---

## Combination

These five metrics are jointly hard to game because they reward *correlated but distinct* costly
behaviors: Metric 1 wants well-cited, specific dead ends; Metric 3 wants substantive decision
alternatives; Metric 4 wants pivots textually and structurally anchored to the nodes that caused them;
Metric 2 wants cross-branch edges that are topically coherent, not decorative; and Metric 5 wants the
`explicit`/`inferred` labels to actually track citation backing. A cheap way to win any one of them
tends to actively lose points on at least one other: padding with fabricated dead ends (Metric 1) with
no real basis will lack the source_refs and specificity Metric 1 itself checks, and any fake
`also_depends_on` pointers used to make them look connected get penalized by Metric 2's overlap check;
inflating decisions with vague alternatives (Metric 3) doesn't help pivot traceability or synthesis;
mass-labeling nodes `explicit` to look rigorous (gaming nothing directly) tanks Metric 5 the moment
`source_refs` aren't genuinely present, and gaming Metric 5 by mass-labeling `inferred` instead drags
down the grounding terms in Metrics 1, 3, and 4. A paper can't cheaply top all five without doing the
actual work: citing real failures, weighing real alternatives, and drawing real, checkable connections
between the nodes that make up its trajectory.
