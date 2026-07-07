# Proposer #4 — metrics for `logic/problem.md`

Assumed parsed shape (dicts/lists mirroring the doc):

```python
artifact = {
    "observations": [{"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str}, ...],
    "gaps": [{"id": "G1", "title": str, "statement": str, "caused_by": ["O1", ...],
              "existing_attempts": str, "why_fail": str}, ...],
    "key_insight": {"insight": str, "derived_from": ["O5", "G1", ...], "enables": str} or None,
    "assumptions": [{"id": "A1", "text": str}, ...],
}
```

---

## 1. Evidential Grounding Depth

**How it signals good science.** A problem statement built on citation-chain evidence
("§1 Introduction, Karikari et al., 2020; ...") reflects genuine engagement with prior
literature; one built on "Evidence: Abstract" for every Observation reflects a compiler
(or author) that only skimmed an abstract. Good science traces claims to their source
granularity, not to a summary of a summary.

**Compute function.**

```python
import re

CITATION_YEAR = re.compile(r'\b(19|20)\d{2}[a-z]?\b')
SECTION_REF = re.compile(r'§|\bSection\s+\d|\bIntroduction\b|\bMethods\b|\bResults\b', re.I)
ABSTRACT_ONLY = re.compile(r'^\s*abstract\s*$', re.I)

def evidential_grounding_depth(artifact: dict) -> float:
    """Assumes artifact['observations'] is a list of dicts, each with an 'evidence' str field
    (possibly empty/missing). Missing/empty observations list scores 0."""
    obs = artifact.get("observations") or []
    if not obs:
        return 0.0

    scores = []
    for o in obs:
        ev = (o.get("evidence") or "").strip()
        if not ev or ABSTRACT_ONLY.match(ev):
            scores.append(0.0)
            continue
        has_section = bool(SECTION_REF.search(ev))
        n_years = len(CITATION_YEAR.findall(ev))
        if has_section and n_years >= 2:
            scores.append(1.0)
        elif has_section and n_years == 1:
            scores.append(0.7)
        elif n_years >= 1:
            scores.append(0.5)
        elif has_section:
            scores.append(0.3)
        else:
            scores.append(0.1)

    mean_score = sum(scores) / len(scores)
    # Thinness penalty: fewer than 3 Observations undercuts confidence in the mean.
    count_penalty = min(1.0, len(obs) / 3)
    return mean_score * count_penalty
```

**What the function does & why.** For every Observation it inspects the `Evidence` string
for (a) a bare "Abstract" placeholder (worst case, score 0), (b) section-level anchoring
(§/Introduction/Methods/etc.), and (c) how many distinct year-tagged citations appear.
Observations with multi-citation, section-anchored evidence score near 1; abstract-only
restatements score 0. The mean is then discounted if the paper only surfaced fewer than 3
Observations at all, since a short list makes the mean less trustworthy and itself signals
thin engagement.

**Why it's hard to Goodhart.** You cannot fix this by padding — adding more Observations
with the same "Evidence: Abstract" doesn't move the mean. To game it you must actually
write plausible-looking section refs and years, which risks fabricating citations —
detectable by cross-referencing against Metric 2 (citation IDs that don't correspond to
any real reference chain break connectivity/traceability elsewhere in the artifact) and by
simple pattern checks for repeated identical "Evidence" strings across Observations (a
copy-paste tell that a stricter downstream check can flag).

---

## 2. Argument-Graph Connectivity

**How it signals good science.** Good scientific reasoning is a connected DAG: every Gap
traces to the Observation(s) that expose it, and the Key Insight synthesizes multiple
upstream nodes into a resolution. Dangling Observations (context nobody uses), Gaps with
no upstream cause, or an Insight that cites nothing real are signs of a stitched-together
narrative rather than a derived one.

**Compute function.**

```python
def argument_graph_connectivity(artifact: dict) -> float:
    """Assumes artifact has 'observations' (list w/ 'id'), 'gaps' (list w/ 'id', 'caused_by'
    list of ids), and 'key_insight' (dict w/ 'derived_from' list of ids, or None/missing)."""
    obs = artifact.get("observations") or []
    gaps = artifact.get("gaps") or []
    insight = artifact.get("key_insight")

    if not obs or not gaps or not insight:
        return 0.0

    obs_ids = {o["id"] for o in obs if o.get("id")}
    gap_ids = {g["id"] for g in gaps if g.get("id")}
    valid_ids = obs_ids | gap_ids

    referenced = set()
    invalid_refs = 0
    total_refs = 0

    for g in gaps:
        cb = g.get("caused_by") or []
        total_refs += len(cb)
        for ref in cb:
            if ref in obs_ids:
                referenced.add(ref)
            else:
                invalid_refs += 1

    derived = insight.get("derived_from") or []
    total_refs += len(derived)
    for ref in derived:
        if ref in valid_ids:
            referenced.add(ref)
        else:
            invalid_refs += 1

    if total_refs == 0:
        return 0.0  # no edges at all: pure list of assertions, no argument

    orphan_obs = sum(1 for oid in obs_ids if oid not in referenced)
    orphan_gaps = sum(1 for gid in gap_ids if gid not in derived)
    total_nodes = len(obs_ids) + len(gap_ids)

    penalty = (invalid_refs + orphan_obs + orphan_gaps) / max(total_nodes, 1)
    return max(0.0, 1.0 - penalty)
```

**What the function does & why.** It builds the id sets for Observations and Gaps, then
walks every `caused_by` and `derived_from` edge, counting (a) references to ids that don't
exist (fabricated/typo'd traceability — a real defect), (b) Observations nobody's Gap or
the Insight ever cites (orphans — decoration, not argument), and (c) Gaps the Key Insight
never resolves (dead ends). The score is 1 minus the fraction of nodes/edges that are
broken or dangling. A fully-wired graph (every Observation feeds a Gap or the Insight,
every Gap feeds the Insight, no bad ids) scores 1.0.

**Why it's hard to Goodhart.** Simply adding `caused_by`/`derived_from` links to game
connectivity requires those ids to be real and requires the Insight to actually cite most
Gaps — but an Insight can't cite everything without becoming a long unfocused
paragraph, which Metric 3 (below) penalizes for lacking a crisp derivation. Wiring fake
edges to unrelated Observations to avoid the orphan penalty is caught by requiring valid
ids only; inventing plausible-sounding extra Observations just to reference them cheaply
dilutes Metric 1's grounding-depth mean if they lack real evidence.

---

## 3. Insight Synthesis Specificity (anti-restatement)

**How it signals good science.** A Key Insight that is just the paper's method name in
sentence form ("We use a network meta-analysis") is not a *derivation* — it doesn't show
the reasoning step from "here's what's missing" to "here's the resolving idea." A genuine
insight (a) draws on 2+ upstream nodes, (b) shares specific technical vocabulary with those
specific nodes (evidence it's actually synthesizing them, not paraphrasing a title), and
(c) is stated with enough length/structure to carry a mechanism, not just a label.

**Compute function.**

```python
import re

GENERIC_INSIGHT_PHRASES = {
    "we use", "we propose", "we apply", "our approach", "our method",
    "using a", "we introduce", "this paper presents",
}
WORD = re.compile(r"[a-zA-Z][a-zA-Z\-]{3,}")

def _content_words(text: str) -> set:
    stop = {"that", "this", "with", "from", "into", "which", "were", "have",
            "these", "their", "such", "than", "then", "each", "when", "while"}
    return {w.lower() for w in WORD.findall(text)} - stop

def insight_synthesis_specificity(artifact: dict) -> float:
    """Assumes artifact['key_insight'] is a dict with 'insight' (str) and 'derived_from'
    (list of ids), and artifact['observations']/['gaps'] are lists of dicts with 'id' and
    'statement' fields, used to look up the text of each derived_from node."""
    insight = artifact.get("key_insight")
    if not insight or not (insight.get("insight") or "").strip():
        return 0.0

    text = insight["insight"].strip()
    derived = insight.get("derived_from") or []

    lookup = {}
    for o in artifact.get("observations") or []:
        if o.get("id"):
            lookup[o["id"]] = o.get("statement", "")
    for g in artifact.get("gaps") or []:
        if g.get("id"):
            lookup[g["id"]] = g.get("statement", "")

    # 1. Breadth of synthesis: must draw on >=2 distinct upstream nodes.
    breadth_score = min(1.0, len(derived) / 2)

    # 2. Length/substance floor: title-like restatements are short.
    word_count = len(text.split())
    length_score = min(1.0, word_count / 25)

    # 3. Generic-phrase penalty.
    lowered = text.lower()
    generic_hits = sum(1 for p in GENERIC_INSIGHT_PHRASES if p in lowered)
    generic_penalty = min(1.0, generic_hits * 0.3)

    # 4. Grounding overlap: how many of the cited nodes actually share distinctive
    #    vocabulary with the insight text (evidence of real synthesis, not name-dropping ids).
    insight_words = _content_words(text)
    grounded_nodes = 0
    for ref in derived:
        node_text = lookup.get(ref, "")
        if not node_text:
            continue
        overlap = insight_words & _content_words(node_text)
        if len(overlap) >= 2:
            grounded_nodes += 1
    overlap_score = grounded_nodes / len(derived) if derived else 0.0

    raw = 0.3 * breadth_score + 0.2 * length_score + 0.5 * overlap_score
    return max(0.0, raw - generic_penalty)
```

**What the function does & why.** It rewards insights that (1) cite at least two upstream
Observations/Gaps, (2) are long enough to state a mechanism rather than a label, (3) don't
lean on generic "we propose/we use" filler, and, most heavily, (4) actually share specific
vocabulary with the *specific* nodes they claim to derive from — i.e. the insight text
isn't just floating free of the ids it lists. Weighting overlap at 0.5 makes real synthesis
the dominant contributor.

**Why it's hard to Goodhart.** Listing many `derived_from` ids to inflate breadth only
helps if the insight text actually shares vocabulary with each — bare id-stuffing without
matching content tanks the overlap term. Writing a long, jargon-dense insight to beat the
length floor risks lower overlap unless the jargon genuinely comes from the cited nodes'
statements, and an overly generic long paragraph gets caught by the phrase blacklist.
Copy-pasting an Observation's statement verbatim as the "insight" would score well here but
directly contradicts the Combination logic below (see below).

---

## 4. Gap Failure-Mode Specificity

**How it signals good science.** A rigorous problem statement explains *precisely* why
prior attempts failed (a specific confound, a specific assay limitation, a specific
statistical shortfall) rather than gesturing at "prior work is limited." Specificity in
`Existing attempts`/`Why they fail` is a proxy for whether the author actually understands
the competing literature well enough to be certain their own approach is novel.

**Compute function.**

```python
import re

GENERIC_FAILURE_PHRASES = [
    "prior work is limited", "not well understood", "insufficient data",
    "limited data", "further research is needed", "not fully explored",
    "remains unclear", "is understudied", "has not been addressed",
]
PROPER_NOUN_OR_NUMBER = re.compile(r'\b[A-Z][a-zA-Z]{2,}\b|\b\d+(\.\d+)?%?\b')

def gap_failure_specificity(artifact: dict) -> float:
    """Assumes artifact['gaps'] is a list of dicts with 'existing_attempts', 'why_fail'
    (str fields, possibly empty) and 'caused_by' (list of ids)."""
    gaps = artifact.get("gaps") or []
    if not gaps:
        return 0.0

    scores = []
    for g in gaps:
        ea = (g.get("existing_attempts") or "").strip()
        wf = (g.get("why_fail") or "").strip()
        combined = f"{ea} {wf}".strip()

        if not combined:
            scores.append(0.0)
            continue

        lowered = combined.lower()
        generic_hits = sum(1 for p in GENERIC_FAILURE_PHRASES if p in lowered)
        specific_markers = len(PROPER_NOUN_OR_NUMBER.findall(combined))
        word_count = len(combined.split())

        # Specificity density: named entities/numbers per 20 words, capped at 1.
        density = min(1.0, specific_markers / max(1, word_count / 20))
        generic_penalty = min(1.0, generic_hits * 0.4)

        # A gap must also be causally anchored (non-empty caused_by) to count as real.
        linked = 1.0 if (g.get("caused_by") or []) else 0.0

        scores.append(max(0.0, density * 0.7 + linked * 0.3 - generic_penalty))

    return sum(scores) / len(scores)
```

**What the function does & why.** For each Gap it counts proper-noun/number density in the
combined `Existing attempts` + `Why they fail` text (a cheap proxy for "names a specific
method, cohort, assay, or effect size" versus vague hand-waving), penalizes generic
boilerplate phrases, and requires the Gap to actually be `caused_by` at least one
Observation (an un-anchored Gap is asserted, not derived). The per-gap scores are averaged.

**Why it's hard to Goodhart.** Sprinkling random capitalized words or numbers to fake
specificity produces text that reads as noise and is unlikely to also satisfy Metric 2's
requirement that the Gap's cited `caused_by` Observations actually contain matching
technical content (a stricter grounding check could cross-reference — and even without
that, human/LLM judges reviewing the full artifact will catch nonsense proper nouns).
Simply asserting `caused_by` links without discussing the specific failure mode still gets
capped at 0.3 since density dominates the score.

---

## 5. Assumption Risk Exposure

**How it signals good science.** Good scientists state the assumptions that, if false,
would break their argument — not vague truisms nobody could disagree with. A problem
statement with concrete, checkable assumptions ("no patient counted twice," "the assay's
linear range covers the observed concentrations") exposes real risk surface for critique.
A statement with 0–1 assumptions, or assumptions that are unfalsifiable platitudes,
signals the author never stress-tested their own argument.

**Compute function.**

```python
import re

VAGUE_TRUISMS = [
    "more data", "is important", "is useful", "in general", "may help",
    "should improve", "is expected to", "is likely to be beneficial",
]
CONCRETE_MARKERS = re.compile(
    r'\bif\b|\bwhen\b|\bno\b.*\b(twice|more than once)\b|\d+(\.\d+)?%?|\bassume[sd]?\b.*\bthat\b',
    re.I,
)

def assumption_risk_exposure(artifact: dict) -> float:
    """Assumes artifact['assumptions'] is a list of dicts with a 'text' str field."""
    assumptions = artifact.get("assumptions") or []
    if not assumptions:
        return 0.0

    scores = []
    for a in assumptions:
        text = (a.get("text") or "").strip()
        if not text:
            scores.append(0.0)
            continue
        lowered = text.lower()
        vague_hits = sum(1 for v in VAGUE_TRUISMS if v in lowered)
        concrete = bool(CONCRETE_MARKERS.search(text))
        word_count = len(text.split())

        base = 0.5 if concrete else 0.15
        length_bonus = min(0.3, word_count / 40)
        vague_penalty = min(0.5, vague_hits * 0.3)
        scores.append(max(0.0, base + length_bonus - vague_penalty))

    mean_score = sum(scores) / len(scores)

    # Count-based shape: too few (<2) signals no real risk surfaced; too many near-duplicate
    # (proxy: many assumptions but low mean specificity) doesn't help either.
    count_factor = min(1.0, len(assumptions) / 2)
    return mean_score * count_factor
```

**What the function does & why.** Each assumption is checked for concreteness markers
(conditionals, explicit exclusion conditions, numeric thresholds) versus a blacklist of
vague truisms, with a length bonus for assumptions substantial enough to state a real
condition. The mean is scaled down if there are fewer than 2 assumptions total (an
argument resting on 0–1 stated assumptions almost certainly has unstated ones).

**Why it's hard to Goodhart.** Piling on many short vague assumptions to hit the count
floor doesn't help — the mean specificity term drags the score back down, and the count
scaling caps out at 2 so there's no reward for quantity beyond that. Writing artificially
long, jargon-stuffed assumptions to farm the length bonus without a real conditional
structure is capped at a low `base` score (0.15) since the concreteness regex requires an
actual conditional/threshold pattern, not just length.

---

## Combination

These five metrics are jointly hard to game because they pull against each other. Padding
Observations with generic "Abstract"-only evidence to make the graph look richer tanks
Metric 1 and, if those Observations go uncited, tanks Metric 2's orphan penalty too.
Wiring fake `caused_by`/`derived_from` edges to inflate Metric 2's connectivity requires
those edges to point at real ids whose content overlaps with the citing text — cheap fake
edges get punished by Metric 3's overlap term (for the Insight) or Metric 4's causal-anchor
requirement (for Gaps). Writing a long, jargon-heavy Key Insight to beat Metric 3's length
floor risks reading as generic filler, which both Metric 3's phrase blacklist and Metric
5's vague-truism blacklist are tuned to catch (the same rhetorical shortcuts recur across
Insight and Assumptions). And stating many vague, low-specificity Assumptions to hit
Metric 5's count floor doesn't move the mean, while genuinely risky, specific assumptions
that reveal weaknesses in the argument would also tend to surface real Gaps that Metric 4
rewards discussing precisely — so honest, connected, well-evidenced reasoning is the only
path to scoring well across all five simultaneously.
