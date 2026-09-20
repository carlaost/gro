# Metric proposals — `logic/problem.md` (agent1)

Assumed parsed representation for all functions below:

```python
artifact = {
    "observations": [
        {"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str},
        ...
    ],
    "gaps": [
        {"id": "G1", "title": str, "statement": str, "caused_by": ["O1", "O2"],
         "existing_attempts": str, "why_fail": str},
        ...
    ],
    "key_insight": {"insight": str, "derived_from": ["O1", "G1"], "enables": str},  # or None/{} if absent
    "assumptions": [{"id": "A1", "text": str}, ...],
}
```

---

## 1. Evidentiary Grounding Depth

**How it signals good science**: A claim inherited from prior literature is only as trustworthy as its
traceability. An Observation backed by a named citation chain or section reference lets a reader (or a
downstream agent) go verify the fact independently. An Observation whose `Evidence` field is just
`"Abstract"` or empty is a restated impression, not a checked fact — it cannot be audited. Depth and
distinctness of citation grounding is a direct proxy for how carefully the source's background claims
were checked before being used as a premise.

**Compute function**:

```python
import re

def evidentiary_grounding_depth(artifact: dict) -> float:
    """
    Assumes artifact["observations"] is a list of dicts with an "evidence" string field
    (possibly empty/missing). Missing observations entirely -> score 0 (penalize, not skip).
    """
    obs = artifact.get("observations", [])
    if not obs:
        return 0.0

    citation_pat = re.compile(r"[A-Z][a-zA-Z\-]+(?:\s+et\s+al\.)?,?\s*\(?\d{4}\)?")
    section_pat = re.compile(r"(§|section|introduction|methods|results|discussion)", re.I)
    generic_pat = re.compile(r"^\s*(abstract|background|n/?a|unknown|none)\s*\.?\s*$", re.I)

    scores = []
    for o in obs:
        ev = (o.get("evidence") or "").strip()
        if not ev:
            scores.append(0.0)
            continue
        if generic_pat.match(ev):
            scores.append(0.15)  # abstract-only restatement, per shape doc's degradation note
            continue
        n_citations = len(set(citation_pat.findall(ev)))
        has_section = bool(section_pat.search(ev))
        # 1 citation + no section ref is decent; multiple distinct citations plus a
        # section anchor is the strongest signal. Cap so a citation-stuffed field
        # doesn't dominate.
        s = min(1.0, 0.35 * min(n_citations, 3) + (0.25 if has_section else 0.0))
        # a field with prose but neither a citation nor a section ref is weak but not zero
        scores.append(max(s, 0.1 if len(ev) > 20 else 0.0))

    return sum(scores) / len(scores)
```

**What the function does & why**: For every Observation it inspects the `Evidence` string. Empty
fields score 0. Fields matching known generic placeholders (`"Abstract"`, `"Background"`, `"N/A"`)
score low (0.15) — this directly operationalizes the shape doc's stated degradation signal that
abstract-only sources produce evidence fields with no depth. Otherwise it counts distinct
author-year citation tokens and checks for a section anchor (`§`, "Introduction", etc.), rewarding
both distinctness of citations and a locatable position in the source. The per-observation scores are
averaged; an artifact with zero Observations scores 0 outright (missing input is penalized, not
skipped).

**Why it's hard to Goodhart**: Stuffing an Evidence field with fabricated `Author (Year)`-shaped
strings is detectable as a strategy but cheap to produce in isolation — the countermeasure is that
this metric is paired with Metric 2 (Structural Integrity) and Metric 3 (Insight Synthesis), which
require those same Observations to actually feed into a Gap or the Key Insight's `Derived from` chain.
Fabricated evidence sitting on an orphan, unused Observation gets caught by Metric 2. Padding with
many near-duplicate citations for a single fact is capped at 3 citations counted, so citation-count
inflation has a hard ceiling per Observation.

---

## 2. Causal-Chain Structural Integrity

**How it signals good science**: A real scientific argument is a directed graph: Observations feed
Gaps, Gaps and Observations feed the Key Insight. If that graph is well-formed — every reference
resolves, and every node is actually used downstream — the author built the argument compositionally.
If Observations sit unreferenced by any Gap or the Insight (padding), or if `Caused by` / `Derived
from` point at IDs that don't exist (sloppy or fabricated cross-referencing), the "why" layer is
decorative rather than load-bearing.

**Compute function**:

```python
def causal_chain_structural_integrity(artifact: dict) -> float:
    """
    Assumes artifact has "observations" (list with "id"), "gaps" (list with "id",
    "caused_by": list[str]), and "key_insight" (dict with "derived_from": list[str], or
    None/missing). No Key Insight -> heavily penalized, since it is documented as
    mandatory/never-absent core.
    """
    obs = artifact.get("observations", [])
    gaps = artifact.get("gaps", [])
    insight = artifact.get("key_insight") or {}

    obs_ids = {o["id"] for o in obs if o.get("id")}
    gap_ids = {g["id"] for g in gaps if g.get("id")}
    all_ids = obs_ids | gap_ids

    if not obs_ids or not insight or not insight.get("insight", "").strip():
        return 0.0  # missing mandatory core -> penalize, never N/A

    # 1. Reference validity: every caused_by / derived_from id must resolve to a real node.
    refs = []
    for g in gaps:
        refs.extend(g.get("caused_by") or [])
    refs.extend(insight.get("derived_from") or [])
    if not refs:
        ref_validity = 0.0  # no cross-referencing at all is itself a failure
    else:
        valid = sum(1 for r in refs if r in all_ids)
        ref_validity = valid / len(refs)

    # 2. Utilization: fraction of Observations actually cited by >=1 Gap or the Insight.
    cited_obs = set()
    for g in gaps:
        cited_obs |= set(o for o in (g.get("caused_by") or []) if o in obs_ids)
    cited_obs |= set(o for o in (insight.get("derived_from") or []) if o in obs_ids)
    utilization = len(cited_obs) / len(obs_ids)

    return 0.5 * ref_validity + 0.5 * utilization
```

**What the function does & why**: It builds the set of valid Observation/Gap IDs, then checks two
things. First, reference validity — do all the `Caused by` and `Derived from` pointers actually
resolve to real nodes (catches broken/fabricated cross-refs). Second, utilization — what fraction of
Observations are actually cited by a downstream Gap or the Key Insight (catches padding: Observations
added for volume that never do argumentative work). The two are averaged. A missing Key Insight or
empty Observation list scores 0 flat, since the shape doc states this core is mandatory and never
legitimately absent.

**Why it's hard to Goodhart**: You cannot inflate utilization by just adding more `caused_by`/`derived_from`
references without them resolving — invalid IDs tank ref_validity. You cannot pad Observations for volume
(which would help Metric 1's average less directly, but helps "looks thorough") without hurting
utilization, since new Observations must actually get cited somewhere to avoid being orphans. Wiring
every Observation into every Gap indiscriminately to force utilization to 1.0 is itself checkable by
Metric 3, since a Key Insight or Gap that claims to derive from everything but engages textually with
nothing will fail the synthesis overlap check there.

---

## 3. Insight Synthesis Sweet-Spot

**How it signals good science**: The Key Insight is supposed to be a genuine creative leap that
recombines specific elements from multiple Observations/Gaps into a new relational claim — not a
verbatim restatement of one source sentence (shallow read, or literally just the method's name dressed
up), and not a claim disconnected from anything it cites (fabricated post-hoc justification). Real
synthesis draws lexical/conceptual material from at least two distinct upstream nodes while adding
new relational content of its own — this shows up as moderate, multi-source textual overlap rather
than near-total overlap with a single source or near-zero overlap with all of them.

**Compute function**:

```python
import re

_STOP = {"the","a","an","of","to","and","in","on","for","with","that","this","is","are",
         "as","by","be","or","which","from","its","it","was","were","at","into","across"}

def _tokenize(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in _STOP and len(w) > 2}

def insight_synthesis_sweet_spot(artifact: dict) -> float:
    """
    Assumes key_insight has "insight" (str) and "derived_from" (list of O/G ids), and
    that observations/gaps carry enough text (statement/implication/why_fail) to compare
    against. Missing insight, empty derived_from, or unresolved derived_from ids all
    penalize to 0 -- never skipped as N/A.
    """
    insight = artifact.get("key_insight") or {}
    insight_text = insight.get("insight", "").strip()
    derived_from = insight.get("derived_from") or []
    if not insight_text or not derived_from:
        return 0.0

    obs_by_id = {o["id"]: o for o in artifact.get("observations", [])}
    gap_by_id = {g["id"]: g for g in artifact.get("gaps", [])}

    insight_tokens = _tokenize(insight_text)
    if not insight_tokens:
        return 0.0

    overlaps = []
    for ref in derived_from:
        node = obs_by_id.get(ref) or gap_by_id.get(ref)
        if node is None:
            overlaps.append(0.0)  # dangling ref -> counts as zero engagement, not skipped
            continue
        source_text = " ".join(str(node.get(f, "")) for f in
                                ("statement", "implication", "why_fail", "existing_attempts"))
        source_tokens = _tokenize(source_text)
        if not source_tokens:
            overlaps.append(0.0)
            continue
        jacc = len(insight_tokens & source_tokens) / len(insight_tokens | source_tokens)
        overlaps.append(jacc)

    if not overlaps:
        return 0.0

    num_engaged = sum(1 for x in overlaps if x >= 0.05)
    max_overlap = max(overlaps)

    # Sweet spot: engages with >=2 distinct sources, and no single source is near-copied.
    multi_source_score = min(1.0, num_engaged / 2.0)
    copy_penalty = 1.0 if max_overlap <= 0.55 else max(0.0, 1.0 - (max_overlap - 0.55) / 0.45)
    disconnection_penalty = 0.0 if max_overlap >= 0.04 else max_overlap / 0.04

    return multi_source_score * copy_penalty * (1.0 if max_overlap >= 0.04 else disconnection_penalty)
```

**What the function does & why**: It tokenizes the Insight text and, separately, the text of every
node it claims to derive from. For each cited source it computes Jaccard word overlap. It then scores
three things jointly: (a) how many distinct sources the Insight meaningfully engages with (`>= 0.05`
overlap) — synthesis across >=2 sources is rewarded up to a cap; (b) whether any single source is
almost entirely copied (`max_overlap > 0.55` starts penalizing — this is the "Key Insight that merely
restates" failure mode flagged in the shape doc); (c) whether the Insight is completely disconnected
from everything it claims to derive from (`max_overlap < 0.04` — near-zero overlap with cited material
suggests fabricated derivation). Dangling `derived_from` references count as zero engagement rather
than being dropped from consideration, satisfying the "penalize missing, don't skip" constraint.

**Why it's hard to Goodhart**: Pushing the Insight text to be very different from all cited sources
(to avoid looking like a copy) directly triggers the disconnection penalty. Pushing it to closely
paraphrase one rich source to look "grounded" triggers the copy penalty. The only way to score well is
to actually pull specific content from two-or-more distinct upstream nodes and state a new relation
between them — which is a reasonable operational stand-in for "an actual creative leap happened."
Gaming this requires hand-authoring an Insight that legitimately recombines two sources in
moderate-overlap language, which is expensive and, notably, is just... doing the thing correctly.

---

## 4. Assumption Concreteness & Falsifiability

**How it signals good science**: Assumptions are where an argument admits its unexamined risk. Good
science states assumptions concretely enough that a reader could, in principle, go check or attack
them (e.g., "selecting the single most comprehensive dataset per cohort yields statistically
independent nodes"). Vague, hedge-heavy assumptions ("this generally holds," "results are typically
robust") give the appearance of intellectual honesty while conceding nothing checkable — they are
unfalsifiable by construction.

**Compute function**:

```python
import re

_HEDGES = {"may","might","could","generally","typically","often","usually","likely",
           "presumably","should","probably","tends to","in most cases"}

def assumption_concreteness(artifact: dict) -> float:
    """
    Assumes artifact["assumptions"] is a list of {"id": str, "text": str}.
    Empty/missing list -> score 0 (the shape doc lists this as mandatory core, 3-5 typical).
    """
    assumptions = artifact.get("assumptions", [])
    if not assumptions:
        return 0.0

    num_pat = re.compile(r"\d+(\.\d+)?%?")
    cap_term_pat = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")  # multi-word proper/technical terms

    scores = []
    for a in assumptions:
        text = (a.get("text") or "").strip()
        if not text:
            scores.append(0.0)
            continue
        words = text.split()
        length_score = min(1.0, len(words) / 15.0)  # very short assumptions read as generic

        has_number = bool(num_pat.search(text))
        has_named_term = bool(cap_term_pat.search(text))
        concreteness_bonus = 0.25 * has_number + 0.25 * has_named_term

        hedge_count = sum(text.lower().count(h) for h in _HEDGES)
        hedge_penalty = min(0.5, 0.15 * hedge_count)

        s = max(0.0, min(1.0, 0.5 * length_score + concreteness_bonus - hedge_penalty))
        scores.append(s)

    return sum(scores) / len(scores)
```

**What the function does & why**: For each assumption it rewards length (a genuine mechanistic
assumption usually takes a full clause to state; a 3-word assumption is almost always generic filler),
the presence of numbers/quantities, and the presence of multi-word technical/named terms (proxy for
domain specificity). It penalizes hedge words that let an assumption escape falsification without
adding information. The per-assumption scores are averaged; a missing or empty assumptions list scores
0, since the shape doc documents this section as mandatory core.

**Why it's hard to Goodhart**: Padding an assumption with filler words to hit the length threshold
without hedges or specificity only gets partial credit (length is half-weighted, and rambling
non-technical prose won't trigger the named-term or numeric bonuses). Removing hedge words while
leaving the underlying claim just as vague (e.g., "X holds" instead of "X may hold") avoids the hedge
penalty but still fails to gain the concreteness bonus, so it caps out around 0.5. To score well you
need an assumption that is both long enough to state a real mechanism and specific enough to contain a
number or a named technical term — which is a reasonable proxy for "this assumption could actually be
checked."

---

## 5. Gap Failure-Mode Specificity (Anti-Boilerplate)

**How it signals good science**: A rigorous problem statement explains, in specific mechanistic terms,
why prior attempts at closing a Gap failed (e.g., "compare limited assay pairs in single cohorts,
cannot integrate indirect evidence"). A lazy or compressed one falls back to generic boilerplate
("prior work is limited," "existing methods are insufficient") that could be pasted into any paper in
any field. Specificity here is a direct signal that the author actually understood the failure modes
of prior work rather than gesturing at them.

**Compute function**:

```python
import re

_BOILERPLATE = [
    r"prior (work|studies|methods) (is|are) limited",
    r"existing (methods|approaches|work) (is|are) (insufficient|inadequate|limited)",
    r"no (comprehensive|systematic) (study|approach|method)",
    r"(further|more) (research|work|study) is needed",
    r"(has|have) not been (fully|adequately) (explored|studied|addressed)",
]
_BOILERPLATE_RE = [re.compile(p, re.I) for p in _BOILERPLATE]

def gap_failure_mode_specificity(artifact: dict) -> float:
    """
    Assumes artifact["gaps"] is a list of dicts with "existing_attempts" and "why_fail"
    string fields. No gaps -> score 0 (Gaps are mandatory core per the shape doc).
    """
    gaps = artifact.get("gaps", [])
    if not gaps:
        return 0.0

    mechanism_markers = re.compile(
        r"(cannot|fail to|because|due to|since|only|single|limited to|assume[sd]?|"
        r"ignore[sd]?|conflat(e|ed)|overfit|underpowered|confound)", re.I
    )

    scores = []
    for g in gaps:
        text = " ".join([g.get("existing_attempts", "") or "", g.get("why_fail", "") or ""]).strip()
        if not text:
            scores.append(0.0)
            continue

        boiler_hits = sum(1 for pat in _BOILERPLATE_RE if pat.search(text))
        boiler_penalty = min(1.0, 0.4 * boiler_hits)

        has_mechanism = bool(mechanism_markers.search(text))
        length_score = min(1.0, len(text.split()) / 20.0)

        s = max(0.0, (0.6 * length_score + 0.4 * has_mechanism) - boiler_penalty)
        scores.append(s)

    return sum(scores) / len(scores)
```

**What the function does & why**: For every Gap it concatenates `Existing attempts` and `Why they
fail`, then checks two things: whether the text matches known generic-boilerplate phrasing (penalized
directly — this is the exact compression/laziness signal the shape doc calls out), and whether it
contains causal-mechanism language ("cannot," "because," "conflates," "underpowered," etc.) alongside
sufficient length. A Gap with no `existing_attempts`/`why_fail` content at all scores 0, and an
artifact with no Gaps scores 0 overall, since Gaps are documented mandatory core.

**Why it's hard to Goodhart**: The boilerplate blocklist catches the cheapest evasion (literally
pasting a stock phrase). Swapping in synonyms for the same generic claim ("existing techniques are
lacking") without adding a mechanism still fails the `has_mechanism` check, since generic-limitation
language rarely contains genuine causal/mechanistic markers — you'd have to actually state a specific
failure mechanism to pass, which is again just doing the underlying scientific work of diagnosing why
prior approaches failed.

---

## Combination

These five metrics are jointly hard to game because each one taxes a different, mutually exclusive
gaming strategy for the same content. Fabricating rich-looking citations to inflate Metric 1
(Evidentiary Grounding) does nothing unless that Observation is actually wired into a Gap or the
Insight — which Metric 2 (Structural Integrity) checks independently via utilization. Wiring every
Observation into every downstream node to force Metric 2's utilization to 1.0 requires the Key
Insight/Gaps to textually engage with all of them, which Metric 3 (Insight Synthesis) checks via
per-source overlap — indiscriminate wiring without real engagement shows up as either near-zero
overlap (disconnection penalty) or, if you paste source text in to fake engagement, near-total overlap
(copy penalty). Writing an Insight that closely paraphrases a rich Observation to dodge the
disconnection penalty in Metric 3 directly triggers its copy penalty. Padding Assumptions with wordy
but still-vague filler to beat Metric 4's length threshold fails its concreteness bonus (no numbers,
no named terms), and stripping hedge words without adding specificity only reaches a middling score.
Rephrasing generic Gap-failure boilerplate with synonyms to dodge Metric 5's blocklist still needs to
introduce genuine mechanism language to pass its second check, which is the same work as actually
diagnosing the failure. In short: passing all five requires an argument that is evidenced, structurally
connected, genuinely synthesized (not copied, not invented), concretely falsifiable in its assumptions,
and specific about failure mechanisms — which is a fair operational definition of "the why-layer was
actually done carefully," not merely decorated to look that way.
