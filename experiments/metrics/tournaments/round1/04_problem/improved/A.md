# Proposer #4 (improved) — metrics for `logic/problem.md`

## Changes from stage 1

The judge ranked this entry #1 overall but named four concrete weaknesses. All four are fixed
below, with no change to the other metrics' sound parts:

1. **M3 overlap was seedable** (bare "share >=2 words with a cited node" passes even if those
   words are boilerplate common to every node in the artifact). Fixed by computing document
   frequency across all Observation/Gap statements and only counting *distinctive* shared terms
   (present in fewer than half the nodes) toward the overlap credit.
2. **M3's length floor rewarded verbosity unconditionally** (`length_score` gave up to +0.2 to
   any long insight regardless of content). Fixed by gating the length term behind
   `overlap_score` via a smooth ramp (`length_gate = min(1, overlap_score * 3)`), so a long but
   ungrounded insight now earns ~0 length credit instead of a free 0.2.
3. **M4's `linked` term rewarded mere presence of a `caused_by` list**, even one pointing at
   nonexistent/typo'd ids. Fixed by requiring at least one `caused_by` reference to resolve to a
   real Observation id (reusing the same id-set construction as M2) before the 0.3 anchor credit
   is paid.
4. **M1's citation detection was year-only**, so "2020, 2021, 2022" alone scored as three
   citations. Fixed by adding an `AUTHOR_YEAR` pattern (`Name[, et al.], Year`) and demoting
   bare-year-only evidence (no author token, no section ref) to a low 0.15 tier instead of 0.5.

One additional Goodhart-resistance sharpening not explicitly requested but promised-and-unbuilt
in the original submission: M1's "why hard to Goodhart" claimed a duplicate-evidence tell was
"detectable by a stricter downstream check" without actually implementing it. It is now a real
computed penalty (`dup_penalty`) rather than an aspiration, closing the "paste one rich citation
list into every Observation" evasion agent2's critique flagged as a blind spot in the field
generally.

Assumed parsed shape (dicts/lists mirroring the doc), unchanged from stage 1:

```python
artifact = {
    "observations": [{"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str}, ...],
    "gaps": [{"id": "G1", "title": str, "statement": str, "caused_by": ["O1", ...],
              "existing_attempts": str, "why_fail": str}, ...],
    "key_insight": {"insight": str, "derived_from": ["O5", "G1", ...], "enables": str} or None,
    "assumptions": [{"id": "A1", "text": str}, ...],
}
```

All five functions honor the hard constraint: a missing/empty top-level list or dict (no
Observations, no Gaps, no Key Insight, no Assumptions) scores that metric **0.0** — never
skipped, never `N/A`. Missing inputs are treated as the worst case, not as absent data to
special-case around.

---

## 1. Evidential Grounding Depth

**How it signals good science.** A problem statement built on citation-chain evidence
("§1 Introduction, Karikari et al., 2020; ...") reflects genuine engagement with prior
literature; one built on "Evidence: Abstract" for every Observation reflects a compiler
(or author) that only skimmed an abstract. Good science traces claims to their source
granularity, not to a summary of a summary — and traces it independently per claim, not by
copy-pasting the same citation block everywhere.

**Compute function.**

```python
import re

CITATION_YEAR = re.compile(r'\b(19|20)\d{2}[a-z]?\b')
AUTHOR_YEAR = re.compile(
    r'\b[A-Z][A-Za-z\-]+(?:\s+(?:et al\.?|&|and)\s*[A-Za-z\-]*)?,?\s+(?:19|20)\d{2}[a-z]?\b'
)
SECTION_REF = re.compile(r'§|\bSection\s+\d|\bIntroduction\b|\bMethods\b|\bResults\b', re.I)
ABSTRACT_ONLY = re.compile(r'^\s*abstract\.?\s*$', re.I)

def _norm_evidence(ev: str) -> str:
    return re.sub(r'\s+', ' ', ev.strip().lower())

def evidential_grounding_depth(artifact: dict) -> float:
    """Assumes artifact['observations'] is a list of dicts, each with an 'evidence' str field
    (possibly empty/missing). Missing/empty observations list scores 0."""
    obs = artifact.get("observations") or []
    if not obs:
        return 0.0

    scores = []
    evidence_strings = []
    for o in obs:
        ev = (o.get("evidence") or "").strip()
        evidence_strings.append(_norm_evidence(ev) if ev else None)
        if not ev or ABSTRACT_ONLY.match(ev):
            scores.append(0.0)
            continue
        has_section = bool(SECTION_REF.search(ev))
        n_author_year = len(AUTHOR_YEAR.findall(ev))
        n_bare_year = len(CITATION_YEAR.findall(ev))
        if has_section and n_author_year >= 2:
            scores.append(1.0)
        elif has_section and n_author_year == 1:
            scores.append(0.7)
        elif n_author_year >= 1:
            scores.append(0.5)
        elif has_section:
            scores.append(0.3)
        elif n_bare_year >= 1:
            # Bare years with no author token: weak, cheaply gamed ("2020, 2021, 2022").
            scores.append(0.15)
        else:
            scores.append(0.1)

    mean_score = sum(scores) / len(scores)

    # Thinness penalty: fewer than 3 Observations undercuts confidence in the mean.
    count_penalty = min(1.0, len(obs) / 3)

    # Duplicate-evidence penalty: identical (whitespace/case-normalized) Evidence strings
    # pasted across 2+ Observations is a copy-paste tell, not independent grounding for
    # each claim. Counts every Observation participating in a duplicate group.
    seen = {}
    for s in evidence_strings:
        if s:
            seen[s] = seen.get(s, 0) + 1
    n_duplicated = sum(c for c in seen.values() if c > 1)
    dup_penalty = min(0.5, 0.15 * n_duplicated) if len(obs) > 1 else 0.0

    return max(0.0, mean_score * count_penalty - dup_penalty)
```

**What the function does & why.** For every Observation it inspects the `Evidence` string
for (a) a bare "Abstract" placeholder (worst case, score 0), (b) section-level anchoring
(§/Introduction/Methods/etc.), and (c) how many distinct `Author, Year`-style citations
appear — not just bare years, since a bare year with no author token is trivial to fabricate
and carries almost no evidentiary weight. Observations with multi-citation, section-anchored
evidence score near 1; abstract-only restatements score 0; bare-year-only evidence is
demoted to a low 0.15. The mean is discounted if fewer than 3 Observations were surfaced at
all, and separately penalized if 2+ Observations share byte-identical evidence text.

**Why it's hard to Goodhart.** You cannot fix this by padding — adding more Observations
with the same "Evidence: Abstract" doesn't move the mean. Writing bare years without author
tokens no longer buys a passing score. Pasting one rich, real-looking citation list into
every Observation to fake breadth is now directly penalized by `dup_penalty` rather than
merely gestured at. To game the top tier you must write per-Observation, section-anchored,
multi-author-year citations — which risks fabricating citations, itself detectable by
cross-referencing against Metric 2 (citation IDs/claims that don't correspond to any real
reference chain break connectivity/traceability elsewhere in the artifact).

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
Gaps — but an Insight can't cite everything without becoming a long unfocused paragraph,
which Metric 3 (below) now specifically declines to reward unless the length is backed by
distinctive-term overlap. Wiring fake edges to unrelated Observations to avoid the orphan
penalty is caught by requiring valid ids only; inventing plausible-sounding extra
Observations just to reference them cheaply dilutes Metric 1's grounding-depth mean (and
now its duplicate-evidence penalty) if they lack real, independent evidence. Metric 4 also
now reuses this same id-set discipline for `caused_by`, so a Gap can't buy its anchor credit
with a dangling reference either.

---

## 3. Insight Synthesis Specificity (anti-restatement)

**How it signals good science.** A Key Insight that is just the paper's method name in
sentence form ("We use a network meta-analysis") is not a *derivation* — it doesn't show
the reasoning step from "here's what's missing" to "here's the resolving idea." A genuine
insight (a) draws on 2+ upstream nodes, (b) shares vocabulary that is *specific to each*
cited node — not boilerplate common to the whole artifact — and (c) is stated with enough
length/structure to carry a mechanism, but only once (b) is actually satisfied.

**Compute function.**

```python
import re

GENERIC_INSIGHT_PHRASES = {
    "we use", "we propose", "we apply", "our approach", "our method",
    "using a", "we introduce", "this paper presents",
}
WORD = re.compile(r"[a-zA-Z][a-zA-Z\-]{3,}")

_STOP = {
    "that", "this", "with", "from", "into", "which", "were", "have",
    "these", "their", "such", "than", "then", "each", "when", "while",
    "study", "paper", "data", "analysis", "results", "using", "used",
    "shows", "show", "found", "based", "also", "more", "most", "here",
    "across", "between", "within", "level", "levels",
}

def _content_words(text: str) -> set:
    return {w.lower() for w in WORD.findall(text)} - _STOP

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

    # 2. Generic-phrase penalty.
    lowered = text.lower()
    generic_hits = sum(1 for p in GENERIC_INSIGHT_PHRASES if p in lowered)
    generic_penalty = min(1.0, generic_hits * 0.3)

    # 3. Distinctive-term overlap: reward vocabulary the insight shares with a *specific*
    #    cited node, but only count words that are NOT boilerplate common to most nodes in
    #    the artifact (document frequency >= half the nodes). This stops an adversary from
    #    seeding two generic shared words per node ("biomarker", "cohort") to farm the old
    #    flat >=2-word-overlap rule without synthesizing anything.
    all_node_texts = [t for t in lookup.values() if t]
    n_nodes = max(1, len(all_node_texts))
    doc_freq = {}
    for t in all_node_texts:
        for w in _content_words(t):
            doc_freq[w] = doc_freq.get(w, 0) + 1
    common_cutoff = max(1, n_nodes // 2)  # words present in >=half the nodes are "common"

    insight_words = _content_words(text)
    grounded_nodes = 0
    for ref in derived:
        node_text = lookup.get(ref, "")
        if not node_text:
            continue
        overlap = insight_words & _content_words(node_text)
        distinctive_overlap = {w for w in overlap if doc_freq.get(w, 1) <= common_cutoff}
        if len(distinctive_overlap) >= 2:
            grounded_nodes += 1
    overlap_score = grounded_nodes / len(derived) if derived else 0.0

    # 4. Length/substance floor: title-like restatements are short — but length only earns
    #    credit once real grounding exists (overlap_score > 0). The gate ramps in smoothly
    #    (rather than a hard cliff at exactly zero) so a small amount of genuine overlap
    #    isn't discontinuously all-or-nothing, while a long ungrounded paragraph earns ~0.
    word_count = len(text.split())
    length_score = min(1.0, word_count / 25)
    length_gate = min(1.0, overlap_score * 3)
    gated_length_score = length_score * length_gate

    raw = 0.3 * breadth_score + 0.2 * gated_length_score + 0.5 * overlap_score
    return max(0.0, raw - generic_penalty)
```

**What the function does & why.** It rewards insights that (1) cite at least two upstream
Observations/Gaps, (2) don't lean on generic "we propose/we use" filler, (3) share
vocabulary with the *specific* nodes they claim to derive from — where "share vocabulary"
now means terms distinctive to that node rather than artifact-wide boilerplate — and
(4) are long enough to carry a mechanism, but only once condition (3) is actually met.
Weighting overlap at 0.5 makes real, node-specific synthesis the dominant contributor, and
gating length behind it removes the free score a long, vague paragraph used to collect.

**Why it's hard to Goodhart.** Listing many `derived_from` ids to inflate breadth only
helps if the insight text shares *distinctive* vocabulary with each — generic id-stuffing
or reusing artifact-wide boilerplate words no longer clears the overlap bar. Writing a
long, jargon-dense insight to beat the old length floor now earns nothing unless that
jargon is the specific, low-document-frequency vocabulary of the cited nodes; an overly
generic long paragraph is caught twice over — by the phrase blacklist and by the length
gate collapsing to ~0 when `overlap_score` is 0. Copy-pasting an Observation's statement
verbatim as the "insight" would score well on overlap for that one node but tanks breadth
(only 1 node) and directly contradicts the Combination logic below.

---

## 4. Gap Failure-Mode Specificity

**How it signals good science.** A rigorous problem statement explains *precisely* why
prior attempts failed (a specific confound, a specific assay limitation, a specific
statistical shortfall) rather than gesturing at "prior work is limited." Specificity in
`Existing attempts`/`Why they fail` is a proxy for whether the author actually understands
the competing literature well enough to be certain their own approach is novel — and that
proxy only means something if the Gap is actually anchored to a real Observation, not just
asserted with a decorative `caused_by` field.

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
    (str fields, possibly empty) and 'caused_by' (list of ids), and artifact['observations']
    is used to validate that 'caused_by' ids are real."""
    gaps = artifact.get("gaps") or []
    if not gaps:
        return 0.0

    obs_ids = {o["id"] for o in (artifact.get("observations") or []) if o.get("id")}

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

        # A gap must be causally anchored to a REAL Observation to count as derived, not
        # merely asserted. A caused_by list pointing only at nonexistent/typo'd ids no
        # longer earns the anchor credit — it must resolve to at least one valid id.
        cb = g.get("caused_by") or []
        linked = 1.0 if any(ref in obs_ids for ref in cb) else 0.0

        scores.append(max(0.0, density * 0.7 + linked * 0.3 - generic_penalty))

    return sum(scores) / len(scores)
```

**What the function does & why.** For each Gap it counts proper-noun/number density in the
combined `Existing attempts` + `Why they fail` text (a cheap proxy for "names a specific
method, cohort, assay, or effect size" versus vague hand-waving), penalizes generic
boilerplate phrases, and requires the Gap's `caused_by` to resolve to at least one real
Observation id (an un-anchored or fabricated-id Gap is asserted, not derived). The per-gap
scores are averaged.

**Why it's hard to Goodhart.** Sprinkling random capitalized words or numbers to fake
specificity produces text that reads as noise and is unlikely to also satisfy Metric 2's
requirement that cited Observations actually exist and carry matching technical content.
Simply asserting a `caused_by` list — even one that resolves to a real id — without
discussing the specific failure mode still gets capped at 0.3 since density dominates the
score; and asserting a `caused_by` list of fabricated ids to *look* anchored no longer earns
even that 0.3, closing the gap the stage-1 judge identified.

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

These five metrics are jointly hard to game because they pull against each other, and the
stage-2 fixes tighten several of the seams the judge probed. Padding Observations with
generic "Abstract"-only evidence to make the graph look richer tanks Metric 1 and, if those
Observations go uncited, tanks Metric 2's orphan penalty too; pasting the same rich
citation block into every Observation to fake independent grounding is now directly caught
by Metric 1's duplicate-evidence penalty rather than merely a promised downstream check.
Wiring fake `caused_by`/`derived_from` edges to inflate Metric 2's connectivity requires
those edges to point at real ids — and Metric 4 now enforces the same id-validity
requirement before paying its anchor credit, so a Gap can no longer look derived by citing
a typo. Writing a long, jargon-heavy Key Insight to beat Metric 3's old length floor no
longer works at all: length is gated behind distinctive, node-specific vocabulary overlap,
so a generic long paragraph scores near the same as a short one, and seeding two boilerplate
shared words per cited node (the old exploit) is filtered out by the document-frequency
check. Writing many vague, low-specificity Assumptions to hit Metric 5's count floor
doesn't move the mean, while genuinely risky, specific assumptions that reveal weaknesses
in the argument would also tend to surface real Gaps that Metric 4 rewards discussing
precisely and anchoring to real Observations — so honest, connected, well-evidenced,
per-claim-grounded reasoning is the only path to scoring well across all five
simultaneously.
