# Proposer #3 — metrics for `trace/exploration_tree.yaml`

Shared helper assumed available to every compute function below (not re-stated each time):

```python
def flatten(tree):
    """Yield every node dict in the DAG, walking `children` recursively.
    A node reached via `also_depends_on` only (not nested under `children`)
    is NOT re-walked here -- also_depends_on is a reference, not a container."""
    for node in tree:
        yield node
        if node.get("children"):
            yield from flatten(node["children"])

def all_node_ids(nodes):
    return {n["id"] for n in nodes}
```

Input assumption for every metric: `artifact` is `{"tree": [...]}` parsed from YAML, possibly
`{"tree": []}` or even `{}` if the file is malformed/empty. Every function treats a missing/empty
tree as the worst case, not a skip.

---

## 1. Grounded Dead-End Yield

**How it signals good science.** The brief states dead-end nodes are the single most valuable
node type for downstream agents, and that a review's dead-ends look different (ranking failures)
from a wet-lab paper's (tried-and-failed). What both have in common is that a *real* dead-end always
comes with a specific failure mode and a specific citation to where that failure is shown — a
fabricated or lazily-invented dead-end has a vague `hypothesis`/`failure_mode`/`lesson` and no
`source_refs`. So instead of just counting `dead_end` nodes, we count dead-ends that are actually
*grounded*: explicit support, non-empty `source_refs`, and a `lesson` that is not a restatement of
the `hypothesis`. This rewards papers/compilations that surface real, citable failures, and refuses
credit for dead-ends manufactured to pad the count.

**Compute function.**
```python
def grounded_dead_end_yield(artifact):
    # Assumes: artifact["tree"] is a list (possibly empty/missing -> worst case).
    nodes = list(flatten(artifact.get("tree") or []))
    total = len(nodes)
    if total == 0:
        return 0.0

    def is_grounded(n):
        if n.get("type") != "dead_end":
            return False
        has_fields = all(n.get(k) for k in ("hypothesis", "failure_mode", "lesson"))
        if not has_fields:
            return False
        explicit = n.get("support_level") == "explicit"
        sourced = bool(n.get("source_refs"))
        # lesson must add information beyond hypothesis, not just echo it
        hyp = str(n.get("hypothesis", "")).strip().lower()
        lesson = str(n.get("lesson", "")).strip().lower()
        non_trivial_lesson = lesson != hyp and len(lesson) > 10
        return explicit and sourced and non_trivial_lesson

    grounded = sum(1 for n in nodes if is_grounded(n))
    # Yield relative to tree size, not an absolute count, so padding the tree with
    # unrelated experiment/question nodes can't dilute the denominator into a free win,
    # and a single well-grounded dead-end in a small honest tree still scores meaningfully.
    return grounded / total
```

**What the function does & why.** It walks every node, flags `dead_end` nodes that (a) have all
three required fields filled with real content, (b) are marked `explicit` (an `inferred` dead-end is
the compiler guessing a failure happened, which is weaker evidence), (c) carry at least one
`source_refs` entry, and (d) whose `lesson` is not just a copy of the `hypothesis`. It divides the
count of such grounded dead-ends by total node count, giving a density score in `[0,1]`.

**Why it's hard to Goodhart.** You can't win this by inventing many `dead_end` nodes — each fake one
needs a real, checkable `source_refs` pointer, which is exactly what Seal Level 1's trace-hygiene
check (and any downstream verifier) will catch by looking at the actual paper. Padding with
`support_level: inferred` dead-ends doesn't help since those are excluded. Writing a `lesson` that's
just a paraphrase of `hypothesis` is excluded too, closing the cheap "fill the fields with filler
text" route.

---

## 2. Signaling Integrity Rate

**How it signals good science.** The shape doc calls out a precise defect: a node marked
`support_level: explicit` but missing `source_refs` is "mismatched signaling" — a soft form of the
same problem as outright invention. Good science extraction is honest about its own evidentiary
basis at the node level, not just in aggregate. This metric directly measures that internal honesty:
across nodes claiming to be `explicit`, what fraction actually back that claim with a citation?

**Compute function.**
```python
def signaling_integrity_rate(artifact):
    # Assumes: artifact["tree"] is a list; nodes may omit source_refs/support_level entirely.
    nodes = list(flatten(artifact.get("tree") or []))
    explicit_nodes = [n for n in nodes if n.get("support_level") == "explicit"]

    if not explicit_nodes:
        # No explicit claims anywhere is itself suspicious for anything beyond an
        # abstract-only floor tree -- score low rather than skipping, per the hard constraint.
        return 0.05

    backed = sum(1 for n in explicit_nodes if n.get("source_refs"))
    rate = backed / len(explicit_nodes)

    # Extra penalty: pivots are explicitly called out as usually *should* be `inferred`.
    # A tree that marks its pivots `explicit` without source_refs is doubly suspect.
    bad_pivots = sum(
        1 for n in nodes
        if n.get("type") == "pivot" and n.get("support_level") == "explicit" and not n.get("source_refs")
    )
    penalty = 0.1 * bad_pivots
    return max(0.0, rate - penalty)
```

**What the function does & why.** It isolates every node claiming `explicit` support and checks
what fraction actually carries `source_refs`. A tree with zero explicit nodes at all scores a fixed
low floor (0.05) rather than N/A, since a compilation that can't cite anything explicitly is thin by
construction. It then applies an extra penalty per `pivot` node that claims `explicit` without a
citation, since the shape doc specifically flags pivots as usually being the compiler's own
inference — an `explicit`-but-uncited pivot is a compounded red flag.

**Why it's hard to Goodhart.** The cheap escape hatch — mark everything `inferred` to avoid needing
citations — is closed by metric 1 and metric 4 below, which both reward `explicit` + sourced content
over `inferred` content. So a paper can't raise this metric by demoting its support levels; it has
to actually attach real `source_refs`, which are independently checkable against the source paper.

---

## 3. DAG Convergence Density

**How it signals good science.** A tree that is really just a straight nested list (every node has
exactly one parent, no `also_depends_on`) is describing a *narrative*, not a *research process* —
real research revisits earlier findings, an experiment builds on two prior threads, a pivot is
triggered by the collision of separate lines of investigation. The brief's own example shows this:
N05's `also_depends_on: [N04]` and N14's `also_depends_on: [N09, N12]`. Genuine convergence — a node
depending on more than just its immediate parent — is evidence the extraction captured real
cross-referencing in the paper's argument, not just its section order.

**Compute function.**
```python
def dag_convergence_density(artifact):
    # Assumes: artifact["tree"] is a list; also_depends_on entries are node-id strings.
    nodes = list(flatten(artifact.get("tree") or []))
    total = len(nodes)
    if total < 2:
        return 0.0  # a single-node (abstract-only floor) tree has no process to converge

    ids = all_node_ids(nodes)
    valid_edges = 0
    dangling_edges = 0
    for n in nodes:
        for ref in (n.get("also_depends_on") or []):
            if ref in ids and ref != n.get("id"):
                valid_edges += 1
            else:
                dangling_edges += 1  # points nowhere or self-loop: worse than no edge

    # Density relative to node count (a bigger tree needs more edges to show the same
    # convergence rate); dangling/self edges actively subtract, since a broken cross-ref
    # is worse evidence of DAG-ness than simply having none.
    raw = valid_edges / total
    penalty = dangling_edges / total
    return max(0.0, min(1.0, raw - penalty))
```

**What the function does & why.** It counts `also_depends_on` edges that resolve to a real,
distinct node in the same tree, normalized by tree size (so this isn't just "more edges wins" —
a two-node tree with one edge and a 40-node tree with one edge are very different in density).
Edges that point to a non-existent id or to themselves are subtracted rather than ignored, since a
broken cross-reference is worse signal than an absent one (it suggests sloppy or fabricated
extraction rather than a genuinely linear paper).

**Why it's hard to Goodhart.** Simply sprinkling `also_depends_on: [N01]` everywhere to inflate the
edge count is caught two ways: (a) any edge to an id that doesn't correspond to a real, independently
grounded node is worthless once combined with metric 2 (the target node itself still needs its own
support to matter), and (b) real convergence in the brief's example always co-occurs with a `pivot`
whose `trigger` text plausibly explains *why* two threads merged — metric 4 checks exactly that
correspondence, so cross-edges added without a matching narrative payoff don't help there.

---

## 4. Pivot Traceability

**How it signals good science.** A `pivot` is the highest-value "the paper changed its mind" event
in the trace, but it is also the type most prone to the compiler inventing a tidy narrative arc that
the paper didn't actually take. The shape doc says a *good* pivot's `trigger` should point back to
the specific evidence that forced the reframe (per the worked example, N14's trigger cites divergent
subgroup rankings from N09 and N12, and is wired up via `also_depends_on`). A pivot that is just
prose with no linkage back to the nodes it claims triggered it is unfalsifiable narrative dressing.

**Compute function.**
```python
def pivot_traceability(artifact):
    # Assumes: artifact["tree"] is a list. A tree with zero pivots is legitimate (many
    # papers never reframe), but we can't return N/A -- score reflects "no demonstrated
    # reframing capacity was needed or found," which is a real (if mild) information floor.
    nodes = list(flatten(artifact.get("tree") or []))
    ids = all_node_ids(nodes)
    pivots = [n for n in nodes if n.get("type") == "pivot"]

    if not pivots:
        return 0.2  # low-but-nonzero floor: absence of a pivot is common and not damning,
                     # but per the hard constraint it cannot score as well as a demonstrated one.

    def score_one(p):
        has_fields = all(p.get(k) for k in ("from", "to", "trigger"))
        if not has_fields:
            return 0.0
        distinct = str(p["from"]).strip().lower() != str(p["to"]).strip().lower()
        linked = bool(set(p.get("also_depends_on") or []) & ids)
        honestly_labeled = p.get("support_level") == "inferred" or bool(p.get("source_refs"))
        return (0.4 * distinct) + (0.4 * linked) + (0.2 * honestly_labeled)

    return sum(score_one(p) for p in pivots) / len(pivots)
```

**What the function does & why.** For every `pivot` node it checks three things and averages a
partial score: the reframe is substantive (`from` != `to`, not a cosmetic restatement), the trigger
is backed by an actual `also_depends_on` link into the tree (not just asserted in prose), and the
node is labeled honestly — either it admits `inferred` (the expected default per the shape doc) or,
if it claims `explicit`, it backs that with `source_refs`. A tree with no pivots gets a fixed low
floor rather than a skip, reflecting that we cannot verify reframing capacity that isn't there.

**Why it's hard to Goodhart.** Writing a plausible-sounding `from`/`to` pair costs nothing on its
own, but the `also_depends_on` link requirement means the pivot must point at real prior nodes —
and those prior nodes only carry weight if they themselves are grounded (metric 1/2). So a
fabricated pivot pointing at fabricated dead-ends/experiments gets caught upstream; a pivot pointing
at real nodes constrains the pivot's claimed trigger to be checkable against real source material.

---

## 5. Decision Deliberation Depth

**How it signals good science. ** A `decision` node with one alternative that's a strawman (e.g.
"pool everything naively" as the sole rejected option) signals a token nod to rigor rather than real
deliberation. Good science documents multiple genuinely considered alternatives and gives a
substantive reason (in `evidence`) for the choice made — exactly the pattern in the worked example's
N03 (two distinct rejected alternatives, plus quantified evidence: "24 statistically independent
datasets from 18 publications").

**Compute function.**
```python
def decision_deliberation_depth(artifact):
    # Assumes: artifact["tree"] is a list; `alternatives` is a list[str], `evidence` a string.
    nodes = list(flatten(artifact.get("tree") or []))
    decisions = [n for n in nodes if n.get("type") == "decision"]

    if not decisions:
        return 0.15  # low floor: some genres (e.g. abstract-only) legitimately have none,
                      # but per the hard constraint absence still scores below presence.

    def score_one(d):
        choice = str(d.get("choice", "")).strip()
        alts = [str(a).strip() for a in (d.get("alternatives") or []) if str(a).strip()]
        if not choice or not alts:
            return 0.0
        # distinctness: alternatives shouldn't just restate the choice
        alts_distinct = sum(1 for a in alts if a.lower() != choice.lower())
        breadth = min(alts_distinct, 3) / 3.0          # >=3 distinct alternatives saturates
        has_evidence = bool(str(d.get("evidence", "")).strip())
        sourced = bool(d.get("source_refs"))
        return 0.5 * breadth + 0.3 * has_evidence + 0.2 * sourced

    return sum(score_one(d) for d in decisions) / len(decisions)
```

**What the function does & why.** For each `decision` node it rewards having multiple *distinct*
rejected alternatives (capped so a paper can't just win by listing ten trivial variants), requires
a non-empty `evidence` justification for the choice, and gives a small bonus for `source_refs`. It
averages across all decisions so one well-argued decision buried among several thin ones doesn't
fully rescue the score.

**Why it's hard to Goodhart.** Padding `alternatives` with near-duplicates of the chosen option is
explicitly excluded by the distinctness filter. Listing many alternatives without `evidence` caps
out at 0.5 rather than 1.0, so volume alone can't substitute for justification. And because
`evidence` here is free-text prose (per the shape doc, `decision.evidence` is informal, not a ref
list), a paper padding it with vague text rather than the specific quantified payoff (like N03's "24
independent datasets") is exactly the kind of thin claim the Level-2 semantic layer (evidence
grounding for claims generally) is built to catch on the neighboring artifacts — it isn't free here.

---

## Combination

Each metric alone has a cheap-looking exploit, but the exploits collide with each other. Padding the
tree with fabricated `dead_end` nodes to win metric 1 requires real `source_refs`, which is exactly
what metric 2 (signaling integrity) checks — a fabricated ref either doesn't exist (fails a
downstream hygiene check) or, if honestly left uncited, tanks metric 1's groundedness filter and
metric 2's explicit/sourced ratio simultaneously. Inflating `also_depends_on` edges to win metric 3
only pays off if the target nodes are themselves grounded and if a `pivot` plausibly explains the
convergence (metric 4) — spurious edges among ungrounded or unrelated nodes score worse than no edges
at all under metric 3's dangling-edge penalty. Dressing up pivots with confident `explicit` labels to
avoid metric 2's penalty directly fights metric 4's honesty term, which prefers `inferred` pivots
(as the shape doc says real pivots usually are) unless real citations back the stronger claim. And
padding `decision` alternatives or evidence with filler text wins nothing under metric 5's
distinctness/evidence-presence checks, while genuinely thin decision-making (one strawman
alternative, no evidence) simultaneously fails to feed any convergent DAG structure for metric 3 or
grounded dead-ends for metric 1 — a tree gamed on one axis stays visibly poor on the others, and a
tree that scores well across all five has to have actually reconstructed a sourced, cross-linked,
honestly-labeled decision trajectory rather than a single cheaply-inflated dimension of it.
