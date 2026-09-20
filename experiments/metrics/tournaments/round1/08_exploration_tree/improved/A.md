# Proposer #2 — metrics for `trace/exploration_tree.yaml` (improved)

## Changes from stage 1

1. **Dropped the `inferred + has_refs + not pivot` half-penalty in `support_level_calibration`.**
   The shape doc never says a hedged node that also cites `source_refs` is a defect —
   `source_refs` are explicitly "recommended," not restricted to `explicit` nodes. That penalty was
   a manufactured smell that could punish good, well-cited extraction for the crime of being honest
   about uncertainty. Removed outright rather than papered over with a replacement penalty the shape
   doc doesn't actually license; `calibration` now tracks only the one mismatch the shape doc names
   in so many words — `explicit` with no `source_refs`.
2. **Stopword-filtered the lexical-overlap proxy** used in both `convergent_synthesis_score` and
   `pivot_traceability_score`, and raised the bar from "any shared token" to "≥2 shared content
   words." A single shared word like "study" or "results" no longer buys an edge the
   real-topical-correspondence credit.
3. **Capped and re-gated the `density_bonus`** in `grounded_failure_disclosure_score` so it only
   grows with *well-formed* dead ends (individual node score ≥ 0.6), not raw dead-end count, and
   lowered its ceiling from 0.3 to 0.15. Padding with more dead ends no longer buys bonus unless
   each one clears a real quality bar.
4. **Softened the zero-dead-end floor with a corroborated genre signal.** Instead of a flat 0.05/0.15
   penalty for any tree with no `dead_end` nodes, a tree gets a less punitive floor (0.25) only when
   *two independent signals* both point to synthesis genre: the root question's own text uses
   synthesis vocabulary, **and** its `experiment` nodes' `result` text independently carries
   ranking/pooled-effect vocabulary (p-score, pooled, heterogeneity, forest plot, etc.). Requiring
   the second, harder-to-fake signal closes the obvious hole where a compiler just injects
   "systematic review" into the question title to buy a softer bar — the experiment content itself
   would also have to look like real synthesis output across multiple nodes, which is far more
   costly to fabricate convincingly. Non-synthesis-signaled trees keep the original harsh floor,
   since the shape doc is explicit that zero dead ends in an iteration-heavy genre is a shallow-
   extraction signal.

All five metrics, their intent, and the combination argument are otherwise unchanged from stage 1;
edits below are scoped to the specific defects the critique identified.

---

All compute functions assume the parsed artifact `tree` is a dict `{"tree": [...]}` whose top-level
list holds node dicts that nest via a `children` list, exactly per the shape doc. Every function
below assumes these shared helpers exist (defined once, reused everywhere):

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

# Stage-2 fix: generic academic filler words no longer count as "shared vocabulary."
_STOPWORDS = {
    'this', 'that', 'these', 'those', 'with', 'from', 'have', 'been', 'were',
    'which', 'their', 'also', 'into', 'such', 'than', 'then', 'when', 'while',
    'about', 'after', 'before', 'because', 'across', 'further', 'overall',
    'using', 'based', 'showed', 'shown', 'found', 'study', 'studies', 'data',
    'result', 'results', 'analysis', 'significant', 'significantly',
    'compared', 'between', 'among', 'within', 'each', 'both', 'some', 'more',
    'most', 'only', 'same', 'other', 'including', 'yielded',
}

def words(s):
    """Content-word bag-of-words for lexical-overlap checks. Filters both
    short tokens and a generic-academic-filler stoplist so that boilerplate
    ("these results showed significant data") can't fake topical correspondence."""
    return {
        w for w in (tok.lower().strip('.,()') for tok in (s or '').split())
        if len(w) > 3 and w not in _STOPWORDS
    }

# Stage-2 addition: corroborated genre sniff for the zero-dead-end floor.
_SYNTHESIS_QUESTION_WORDS = (
    'systematic review', 'meta-analysis', 'meta-analytic',
    'network meta-analysis', 'nma', 'pooled', 'umbrella review',
)
_SYNTHESIS_RESULT_WORDS = (
    'p-score', 'ranked', 'rank ', 'pooled', 'heterogeneity', 'i2',
    'forest plot', 'network meta-analysis', 'md ', ' or ', ' hr ', '95% ci',
)

def looks_like_synthesis_genre(nodes):
    """Two independent signals must agree before we treat a tree as
    review/meta-analysis genre: (a) the root question's own text uses
    synthesis vocabulary, and (b) experiment nodes' `result` text
    independently carries ranking/pooled-effect vocabulary. Requiring (b)
    closes the hole where a compiler just injects 'systematic review' into
    the question title to buy a softer bar -- faking synthesis-flavored
    result text across multiple experiment nodes is much costlier."""
    questions = [n for n in nodes if n.get('type') == 'question']
    root_text = ' '.join(
        str(q.get(f, '')) for q in questions for f in ('title', 'description')
    ).lower()
    text_signal = any(w in root_text for w in _SYNTHESIS_QUESTION_WORDS)

    experiments = [n for n in nodes if n.get('type') == 'experiment']
    exp_hits = sum(
        1 for e in experiments for w in _SYNTHESIS_RESULT_WORDS
        if w in str(e.get('result', '')).lower()
    )
    experiment_signal = len(experiments) >= 2 and exp_hits >= 2
    return text_signal and experiment_signal
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
        # room the tree had to reveal one. Soften only when two independent
        # signals corroborate a genuinely dead-end-poor genre (stage-2 fix).
        if looks_like_synthesis_genre(nodes):
            return 0.25
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
    # Stage-2 fix: bonus now scales with *well-formed* dead ends only (score >= 0.6),
    # not raw count, and its ceiling is halved (0.3 -> 0.15) so padding with more
    # dead ends can't buy density credit unless each one clears a real quality bar.
    well_formed = sum(1 for s in node_scores if s >= 0.6)
    density_bonus = min(well_formed / total * 0.75, 0.15)
    return min(sum(node_scores) / len(node_scores) * 0.7 + density_bonus, 1.0)
```

**What it does & why.** Finds every `dead_end` node, scores each on citation grounding, field
completeness, specificity, and honest support-level labeling, then averages and adds a small bonus
for how much of the tree's real estate is spent on *well-formed* disclosed failure. Zero dead ends is
capped low regardless of tree size because the artifact spec calls dead ends source-bounded, not
optional decoration — a rich tree with none is treated as thin extraction, not a clean paper, unless
the tree independently shows the two corroborating synthesis-genre signals (synthesis vocabulary in
the root question *and* ranking/pooled-effect vocabulary across multiple experiment results), in
which case the floor is only moderately softened, not waived — the shape doc still expects a
synthesis paper's own ranking failures to surface as dead ends when they exist.

**Why it's hard to Goodhart.** Padding with fabricated dead ends only works if each one also carries
plausible `source_refs`, all three required fields, and a specific lesson — cheap invented nodes
(bare title + vague lesson, no refs) score near zero individually and drag the average down. Adding
many *low-effort* dead ends no longer even buys the density bonus, since that bonus now counts only
nodes that already scored ≥0.6 on the real quality checks — so cheap padding is doubly wasted: it
doesn't help the average and it doesn't help the bonus. Claiming synthesis genre to dodge the
zero-dead-end floor requires also fabricating plausible ranking/pooled-effect language across at
least two separate experiment nodes' `result` fields, which is far costlier than editing one question
title, and any such invented experiment content is independently exposed to the same
source-groundedness scrutiny the paper's other content faces.

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
            # Stage-2 fix: require >=2 shared *content* words (stopword-filtered),
            # not just any single shared token, so boilerplate can't fake overlap.
            shared = words(src_text) & words(tgt_text)
            overlap = len(shared) >= 2
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
id (broken/likely invented), and rewards the rest more when the citing node's own text shares at
least two stopword-filtered content words with the cited node's text (a proxy for "this
cross-reference is topically real, not decorative") and when the citing node also carries its own
`evidence`. A tree with zero real DAG edges is capped low.

**Why it's hard to Goodhart.** Sprinkling arbitrary `also_depends_on: [Nxx]` pointers to inflate the
score is cheap to attempt but the lexical-overlap check pulls the weight *negative* for edges that
share fewer than two real content words with their target, and same-branch/dangling edges are actively
penalized rather than ignored — so random edge-adding is a net negative unless the edges are topically
coherent, which requires actually writing consistent node content. Raising the bar from "any shared
token" to "≥2 shared content words" also closes the cheaper version of this hole, where two nodes
happen to both use a generic word like "study" or "results" and farm the overlap bonus for free.

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
node. Unchanged from stage 1: the critique's stage-2 directions for this proposal targeted metrics 1,
2, 4, and 5 specifically, and this metric had no identified defect.

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
            # Stage-2 fix: require >=2 shared stopword-filtered content words,
            # matching the same tightened bar used in convergent_synthesis_score.
            shared = trigger_words & words(target_text)
            if len(shared) >= 2:
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
and whether the pivot's own trigger language actually shares real content vocabulary (≥2 stopword-
filtered content words, not boilerplate) with those nodes, plus basic completeness (`from`/`to` both
present, trigger non-trivial length). Pivots marked `explicit` but untraceable are penalized harder
than untraceable `inferred` ones, since the shape doc says `inferred` is the honest default for
pivots (a narrative reconstruction), while `explicit` is a stronger claim that demands backing.

**Why it's hard to Goodhart.** A cheap fake pivot (nice-sounding `from`/`to` prose, no
`also_depends_on`) is capped at ~0.3; adding fake `also_depends_on` ids without matching vocabulary in
the trigger text earns the dependency-presence credit but not the overlap credit, and if those ids are
shared with Metric 2's edges, incoherent cross-references get punished there too — so the same
fabricated edge can't cheaply score well on both metrics at once. Tightening the overlap bar to ≥2
content words (instead of any single shared token) closes the cheapest version of this hole, where a
trigger sentence happens to share one generic word with its target and collects the overlap credit
for free.

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
        # Stage-2 fix: dropped the old "inferred + has_refs + not pivot" half
        # penalty. The shape doc calls source_refs "recommended," never says
        # a hedged node citing its refs is a defect -- that penalty punished
        # honest, well-cited extraction for no reason the spec supports.
    calibration = 1 - min(mismatches / total, 1.0)

    pivots = [n for n in nodes if n.get('type') == 'pivot']
    if pivots:
        frac_inferred = sum(1 for p in pivots if p.get('support_level') == 'inferred') / len(pivots)
        pivot_honesty = frac_inferred
    else:
        pivot_honesty = 0.2  # hard constraint: no pivots surfaced at all is thin, score down a bit

    return round(0.7 * calibration + 0.3 * pivot_honesty, 3)
```

**What it does & why.** Counts how often a node's confidence label is unsupported by its citations —
the one mismatch the shape doc actually names ("mismatched signaling": `explicit` with no
`source_refs`) — and separately tracks whether pivots, which the shape doc says are usually inferred,
are honestly labeled as such rather than uniformly marked `explicit` to look more authoritative.
Removing the old inverse-smell penalty means the metric no longer manufactures a defect out of a
compiler being conservative and still citing its sources.

**Why it's hard to Goodhart.** Marking everything `inferred` to dodge the "explicit needs refs"
penalty tanks Metrics 1, 3, and 4's grounding terms (which all reward `explicit`+`source_refs`
combinations more than `inferred` alone) and reduces the perceived reliability the other metrics
credit; marking everything `explicit` with copy-pasted or repeated `source_refs` to pass this metric
risks tripping the same-source-refs-everywhere pattern that a hygiene check (not this metric, but the
broader system) would flag, and does nothing to help Metrics 2–4, which need real per-node
distinctions, not uniform labeling. Dropping the inverse-smell penalty removes the one previously
exploitable asymmetry — a compiler could no longer be penalized simply for being honest about
uncertainty while still citing evidence, so there's no longer an incentive to *strip* legitimate
`source_refs` from `inferred` nodes just to avoid a manufactured smell.

---

## Combination

These five metrics are jointly hard to game because they reward *correlated but distinct* costly
behaviors: Metric 1 wants well-cited, specific dead ends (and now only credits *well-formed* ones
toward its density bonus); Metric 3 wants substantive decision alternatives; Metric 4 wants pivots
textually and structurally anchored to the nodes that caused them, via a real (≥2-content-word)
overlap bar; Metric 2 wants cross-branch edges that are topically coherent under that same tightened
bar, not decorative; and Metric 5 wants the `explicit`/`inferred` labels to actually track citation
backing, without penalizing honest hedging. A cheap way to win any one of them tends to actively lose
points on at least one other: padding with fabricated dead ends (Metric 1) with no real basis will
lack the source_refs and specificity Metric 1 itself checks, and won't even buy the density bonus
unless individually well-formed; any fake `also_depends_on` pointers used to make them look connected
get penalized by Metric 2's overlap check, now harder to fake with single shared words; inflating
decisions with vague alternatives (Metric 3) doesn't help pivot traceability or synthesis; claiming a
softer synthesis-genre floor in Metric 1 requires also fabricating ranking-style language across
multiple experiment results, which is exposed to the same source-groundedness scrutiny as everything
else; mass-labeling nodes `explicit` to look rigorous tanks Metric 5 the moment `source_refs` aren't
genuinely present, and gaming Metric 5 by mass-labeling `inferred` instead drags down the grounding
terms in Metrics 1, 3, and 4 — with no remaining incentive to strip legitimate citations from honestly
hedged nodes. A paper can't cheaply top all five without doing the actual work: citing real failures,
weighing real alternatives, and drawing real, checkable connections between the nodes that make up its
trajectory.
