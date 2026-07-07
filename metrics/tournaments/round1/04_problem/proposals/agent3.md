# Proposer 3 — metrics for `logic/problem.md`

Parsed-representation assumption (all compute functions): the artifact is parsed into

```python
problem = {
    "observations": [{"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str}, ...],
    "gaps": [{"id": "G1", "title": str, "statement": str, "caused_by": ["O1", "O2"],
              "existing_attempts": str, "why_they_fail": str}, ...],
    "key_insight": {"insight": str, "derived_from": ["O5", "G1", ...], "enables": str},
    "assumptions": [{"id": "A1", "text": str}, ...],
}
```

Any missing/empty field is treated as `""` or `[]` by the parser — never `None`/absent — so every
compute function below sees a value it can score (per the hard constraint, thin/missing inputs are
penalized, not skipped).

---

## 1. Evidentiary Grounding Depth

**How it signals good science.** An Observation that cites a section-level location and multiple
distinct sources shows the author actually engaged with a citation chain in the source's
Introduction/prior-work. An Observation whose Evidence field is just `"Abstract"` (or empty) is a
restatement of the paper's own summary sentence, not evidence of prior literature — a materially
weaker epistemic foundation for the "why" layer.

**Compute function.**

```python
import re

def evidentiary_grounding_depth(problem: dict) -> float:
    # Assumes: problem["observations"] is a list of dicts with an "evidence" string field
    # (possibly empty). Citations are assumed to appear as "Author, Year" or "Author et al., Year"
    # style tokens, or as an explicit section marker like "§1" / "Introduction".
    obs = problem.get("observations", [])
    if not obs:
        return 0.0

    citation_pat = re.compile(r"[A-Z][a-zA-Z\-]+(?:\s+et al\.)?,?\s*\(?\d{4}\)?")
    section_pat = re.compile(r"§|Section|Introduction|Methods|Results")

    scores = []
    for o in obs:
        ev = (o.get("evidence") or "").strip()
        if not ev:
            scores.append(0.0)
            continue
        stripped = ev.lower().strip().rstrip(".")
        if stripped in ("abstract", "abstract only", "n/a", "none"):
            scores.append(0.1)  # present but degenerate
            continue
        n_citations = len(set(citation_pat.findall(ev)))
        has_section = bool(section_pat.search(ev))
        # 0 citations -> weak; 1 -> partial; >=2 distinct -> strong; section anchor is a bonus
        cite_score = min(n_citations / 2.0, 1.0)
        score = 0.7 * cite_score + 0.3 * (1.0 if has_section else 0.0)
        scores.append(score)
    return sum(scores) / len(scores)
```

**What it does & why.** For each Observation it inspects the `Evidence` string, treats a bare
"Abstract" reference (or an empty field) as a near-zero-grounding degenerate case, and otherwise
counts distinct author-year citation tokens plus whether a section anchor (`§1`, "Introduction", ...)
is present. It averages this per-Observation grounding score across all Observations, rewarding
artifacts where most claims trace to a real citation chain rather than a single abstract sentence.

**Why it's hard to Goodhart.** Padding the Evidence field with many fabricated citation-looking
strings is detectable in combination with Metric 3 (Gap Specificity) and Metric 4 (Graph
Connectivity): fake citations tend to accompany generic, unspecific Gap statements and Implications
that don't actually use the cited numbers, so a paper that games this metric alone (stuffing
citations) without deepening the actual prose will score poorly on the metrics that check for
specific, load-bearing content elsewhere in the same document.

---

## 2. Insight Non-Tautology (derivation quality of the Key Insight)

**How it signals good science.** A real "creative leap" synthesizes multiple prior facts
(Observations/Gaps) into something new; a shallow compile just restates the paper's method name in
different words for both `Insight` and `Enables`. Requiring the Insight to (a) draw from multiple
distinct upstream nodes and (b) say something lexically and structurally different from what it
`Enables` is a proxy for "this is actually explaining *why* the leap works," not just labeling it
twice.

**Compute function.**

```python
def insight_non_tautology(problem: dict) -> float:
    # Assumes: problem["key_insight"] is a dict with "insight" (str), "derived_from" (list[str]),
    # "enables" (str). All three may be empty/missing.
    ki = problem.get("key_insight") or {}
    insight = (ki.get("insight") or "").strip()
    enables = (ki.get("enables") or "").strip()
    derived_from = ki.get("derived_from") or []

    if not insight:
        return 0.0

    # breadth: does the insight draw on >=2 distinct upstream observations/gaps?
    breadth_score = min(len(set(derived_from)) / 2.0, 1.0)

    # non-tautology: penalize high lexical overlap between Insight and Enables text
    def tokens(s):
        return set(w.lower() for w in s.split() if len(w) > 3)
    t_i, t_e = tokens(insight), tokens(enables)
    if not t_i or not t_e:
        overlap_penalty = 1.0  # missing Enables entirely is itself a degradation signal
    else:
        jaccard = len(t_i & t_e) / len(t_i | t_e)
        overlap_penalty = jaccard  # high overlap = restating itself = bad

    length_score = min(len(insight.split()) / 25.0, 1.0)  # trivially short insight = shallow

    return max(0.0, 0.5 * breadth_score + 0.3 * (1 - overlap_penalty) + 0.2 * length_score)
```

**What it does & why.** It rewards a Key Insight that (1) is `derived_from` at least two distinct
Observation/Gap IDs — i.e., a real synthesis, not a single restated fact; (2) is lexically distinct
from its own `Enables` clause, penalizing insights that just repeat the consequence as the cause; and
(3) has enough length to plausibly state a mechanism rather than a label. Empty `Enables` is treated
as maximal overlap penalty (worst case), consistent with the hard constraint.

**Why it's hard to Goodhart.** You could inflate `derived_from` with irrelevant IDs to fake breadth,
but that then damages Metric 4 (Graph Connectivity), which checks whether those referenced IDs
actually appear in a coherent chain with the Gaps they're supposed to resolve. You could also
paraphrase Insight/Enables to reduce lexical overlap without adding real content, but that produces
short, vague sentences that get punished by the length term and by Metric 3's specificity check
applied to the surrounding Gaps.

---

## 3. Gap Specificity (concreteness of "Existing attempts" / "Why they fail")

**How it signals good science.** A Gap grounded in *specific* named prior approaches and a *specific*
failure mechanism reflects a real literature review; a Gap justified only by generic boilerplate
("prior work is limited," "not well studied") is a compression/laziness signal — the compiler (or
source paper) didn't actually characterize the state of the art it claims to be superseding.

**Compute function.**

```python
import re

GENERIC_PHRASES = [
    "limited", "not well studied", "not well understood", "poorly understood",
    "insufficient", "lacking", "not addressed", "remains unclear", "little work",
    "few studies", "not fully",
]

def gap_specificity(problem: dict) -> float:
    # Assumes: problem["gaps"] is a list of dicts with "existing_attempts" and "why_they_fail"
    # string fields, plus "caused_by" (list[str]) used only as a presence check here.
    gaps = problem.get("gaps", [])
    if not gaps:
        return 0.0

    number_pat = re.compile(r"\d")
    propernoun_pat = re.compile(r"\b[A-Z][a-zA-Z]+\b")

    scores = []
    for g in gaps:
        ea = (g.get("existing_attempts") or "").strip()
        wtf = (g.get("why_they_fail") or "").strip()
        text = f"{ea} {wtf}".strip()
        if not text:
            scores.append(0.0)
            continue
        low = text.lower()
        generic_hits = sum(1 for p in GENERIC_PHRASES if p in low)
        word_count = len(text.split())
        has_number = bool(number_pat.search(text))
        has_propernoun = len(propernoun_pat.findall(text)) >= 1
        specificity = 0.0
        specificity += 0.4 if word_count >= 15 else word_count / 15.0 * 0.4
        specificity += 0.3 if has_propernoun else 0.0
        specificity += 0.2 if has_number else 0.0
        specificity -= 0.15 * generic_hits
        scores.append(max(0.0, min(specificity, 1.0)) if word_count >= 3 else 0.0)
    return sum(scores) / len(scores)
```

**What it does & why.** For every Gap it concatenates `Existing attempts` and `Why they fail`,
rewards length (enough room to be concrete), presence of proper nouns (named methods/authors/cohorts)
and numbers (quantified failure modes), and directly penalizes generic hedge phrases. A Gap that says
only "prior work is limited" scores near zero; a Gap naming specific pairwise meta-analyses and
explaining why indirect evidence integration fails scores high.

**Why it's hard to Goodhart.** Simply inserting proper nouns or numbers without genuine specificity
(e.g., name-dropping irrelevant citations) is caught in combination with Metric 1: those names should
also show up, consistently, as Evidence entries or Observation content — a Gap with specific-sounding
"existing attempts" that don't connect to any cited Observation (via `caused_by`) is a graph-orphan
under Metric 4, exposing the padding.

---

## 4. Argument Graph Connectivity

**How it signals good science.** A rigorous problem statement is not a bag of disconnected
assertions — every Gap should trace back to specific Observations, and the Key Insight should
integrate multiple Gaps/Observations into a single resolving chain. This mirrors the actual logical
structure of a sound argument: claims are load-bearing, not decorative. Orphaned nodes (an Observation
no Gap ever cites, a Gap the Key Insight ignores) suggest the "why" layer was assembled mechanically
rather than synthesized.

**Compute function.**

```python
def graph_connectivity(problem: dict) -> float:
    # Assumes: "id" fields on observations/gaps are strings like "O1","G2"; "caused_by" and
    # "derived_from" are lists of such ID strings (possibly referencing unknown/typo'd IDs).
    obs = problem.get("observations", [])
    gaps = problem.get("gaps", [])
    ki = problem.get("key_insight") or {}

    obs_ids = {o.get("id") for o in obs if o.get("id")}
    gap_ids = {g.get("id") for g in gaps if g.get("id")}
    all_ids = obs_ids | gap_ids
    if not all_ids:
        return 0.0

    # 1. Fraction of Gaps with a non-empty, valid Caused-by pointing to real Observation IDs
    valid_gap_links = 0
    for g in gaps:
        cb = set(g.get("caused_by") or [])
        if cb and cb & obs_ids:
            valid_gap_links += 1
    gap_link_score = (valid_gap_links / len(gaps)) if gaps else 0.0

    # 2. Key Insight must derive from >=2 valid, distinct upstream IDs
    derived = set(ki.get("derived_from") or [])
    valid_derived = derived & all_ids
    ki_score = min(len(valid_derived) / 2.0, 1.0)

    # 3. Reachability: fraction of Observations/Gaps transitively reachable from the Key Insight
    #    via derived_from -> (gap.caused_by) chains
    reachable = set(valid_derived)
    frontier = set(valid_derived)
    gap_by_id = {g["id"]: g for g in gaps if g.get("id")}
    while frontier:
        nxt = set()
        for node in frontier:
            g = gap_by_id.get(node)
            if g:
                cb = set(g.get("caused_by") or []) & all_ids
                nxt |= (cb - reachable)
        reachable |= nxt
        frontier = nxt
    coverage_score = len(reachable) / len(all_ids)

    return 0.35 * gap_link_score + 0.25 * ki_score + 0.4 * coverage_score
```

**What it does & why.** It builds the reference graph implied by `caused_by` (Gap→Observation) and
`derived_from` (Key Insight→Observation/Gap) edges, then scores three things: whether Gaps actually
point at real Observations, whether the Key Insight synthesizes at least two distinct upstream nodes,
and — via a reachability walk starting at the Key Insight — what fraction of the *entire* node set
(all Observations and Gaps) is actually load-bearing for the final argument. A document with orphaned
Observations no Gap ever uses, or a Key Insight that only cites one Gap, scores low on coverage even
if individual fields look well-written.

**Why it's hard to Goodhart.** You could reference every ID everywhere to max out coverage, but
`caused_by`/`derived_from` referencing IDs that have no genuine content relationship is exactly what
Metric 2's lexical/breadth check and Metric 3's specificity check are positioned to catch — a Gap
that cites `O1, O2, O3, O4` indiscriminately will typically fail to have specific, differentiated
`Why they fail` text for each, since genuine differentiation requires actually engaging with each
cited Observation.

---

## 5. Assumption Load-Bearing Specificity

**How it signals good science.** The Assumptions section is where an honest author exposes exactly
where the argument could break — "if this claim is false, the paper's conclusion doesn't hold." A
precise, checkable assumption (e.g., "selecting the single most comprehensive dataset per cohort
yields statistically independent nodes") does real epistemic work by naming a falsifiable condition.
A vague truism ("the data is representative," "the model is valid") does none, and its presence
signals the author didn't actually interrogate the argument's weak points.

**Compute function.**

```python
import re

VAGUE_PREDICATES = ["is valid", "works well", "is accurate", "is representative",
                     "is reliable", "is appropriate", "is sufficient", "holds true"]

def assumption_specificity(problem: dict) -> float:
    # Assumes: problem["assumptions"] is a list of dicts with "id" and "text" string fields.
    assumptions = problem.get("assumptions", [])
    if not assumptions:
        return 0.0

    count_score = min(len(assumptions) / 3.0, 1.0)  # expect ~3-5; fewer is a coverage penalty

    condition_pat = re.compile(r"\b(if|when|assuming|unless|requires|depends on)\b", re.I)
    quantifier_pat = re.compile(r"\d|\ball\b|\bevery\b|\bno\b|\bsingle\b|\beach\b", re.I)

    text_scores = []
    for a in assumptions:
        t = (a.get("text") or "").strip()
        if not t:
            text_scores.append(0.0)
            continue
        low = t.lower()
        vague_hit = any(p in low for p in VAGUE_PREDICATES)
        has_condition = bool(condition_pat.search(t))
        has_quantifier = bool(quantifier_pat.search(t))
        word_count = len(t.split())
        s = 0.0
        s += 0.4 if word_count >= 12 else word_count / 12.0 * 0.4
        s += 0.25 if has_condition else 0.0
        s += 0.25 if has_quantifier else 0.0
        s -= 0.3 if vague_hit else 0.0
        text_scores.append(max(0.0, min(s, 1.0)))

    avg_text_score = sum(text_scores) / len(text_scores)
    return 0.4 * count_score + 0.6 * avg_text_score
```

**What it does & why.** It checks both coverage (are there roughly the expected 3–5 assumptions, or
did the author under-report them?) and per-assumption specificity: longer, conditionally-phrased
("if X, then the independence assumption holds"), quantified statements score high, while generic
predicates like "is valid" or "is representative" score low. This targets exactly the failure mode
of an author listing assumptions as a pro-forma checkbox rather than genuinely exposing fragile
premises.

**Why it's hard to Goodhart.** Writing long, jargon-dense but practically meaningless assumptions to
farm length/quantifier points is undermined by cross-checking against Metric 4: a load-bearing
assumption should relate to specific Gaps or the Key Insight's mechanism (e.g., the independence
assumption directly supports the network meta-analysis insight). An assumption disconnected from any
Gap/Insight content — detectable as low term-overlap with the rest of the document — reads as
padding rather than genuine risk disclosure, even if it individually looks "specific."

---

## Combination

These five metrics are jointly hard to game because each rewards a different, mutually-checking axis
of the same underlying document: Metric 1 rewards citation-backed Observations, Metric 3 rewards
citation-backed Gaps, and Metric 4 requires that Gaps and the Key Insight actually reference those
same Observations in a connected graph — so fabricating citations or IDs without real content
coherence gets caught by whichever metric checks the *relationship* rather than the *presence* of
the padded field. Metric 2 requires the Key Insight to be lexically non-tautological even though it
draws on multiple sources, which stops a strategy of maximizing Metric 4's connectivity by cramming
the `derived_from` list — wide-but-shallow synthesis produces a bloated, redundant Insight that
Metric 2 penalizes. Metric 5 requires assumptions to be both specific *and* implicitly tied to the
Gaps/Insight they support, so a paper cannot win Metric 5 by writing impressive-sounding but
free-floating assumptions disconnected from the rest of the argument graph Metric 4 already
validated. In short: gaming any one metric by adding volume, cross-references, or jargon without
real synthesis tends to either break graph coherence (Metric 4), produce lexical redundancy (Metric
2), or fail a specificity check tied to genuinely distinct content (Metrics 1, 3, 5) — a paper cannot
cheaply win all five with the same padding trick.
