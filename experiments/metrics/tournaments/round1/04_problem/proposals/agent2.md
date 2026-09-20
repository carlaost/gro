# Metric proposals — `logic/problem.md` (Proposer #2)

Assumed parsed shape (Python dict) for all functions below:

```python
problem = {
    "observations": [
        {"id": "O1", "title": str, "statement": str, "evidence": str, "implication": str},
        ...
    ],
    "gaps": [
        {"id": "G1", "title": str, "statement": str, "caused_by": ["O1", "O2"],
         "existing_attempts": str, "why_fail": str},
        ...
    ],
    "key_insight": {"insight": str, "derived_from": ["O5", "G1", "G2"], "enables": str},
    "assumptions": [{"id": "A1", "text": str}, ...],
}
```

---

## 1. Traceability Graph Completeness

**How it signals good science.** A problem statement is not a bag of facts — it's an argument
graph: Observations feed Gaps, Gaps and Observations feed the Key Insight. Real scientific reasoning
leaves every node load-bearing (nothing is asserted and then dropped) and every edge valid (nothing
points to a fact that doesn't exist). Sloppy or fabricated problem framing shows up as orphaned
Observations that go nowhere, Gaps that don't feed the eventual solution, or dangling references to
IDs that were never defined.

**Compute function.**

```python
def traceability_completeness(problem: dict) -> float:
    """
    Assumes: problem has "observations" (list), "gaps" (list, each with "caused_by": list[str]),
    "key_insight" (dict with "derived_from": list[str]). Missing/empty structures are penalized,
    not skipped.
    """
    obs_ids = {o["id"] for o in problem.get("observations", [])}
    gap_ids = {g["id"] for g in problem.get("gaps", [])}
    all_ids = obs_ids | gap_ids

    if not obs_ids or not problem.get("gaps") or not problem.get("key_insight"):
        return 0.0  # missing a core layer entirely -> lowest score, not N/A

    gaps = problem["gaps"]
    insight = problem["key_insight"]

    # 1. Referential validity: every caused_by / derived_from ref must resolve to a real ID
    refs = []
    for g in gaps:
        refs.extend(g.get("caused_by", []) or [None])  # missing field -> counts as one bad ref
    refs.extend(insight.get("derived_from", []) or [None])
    valid_refs = [r for r in refs if r in all_ids]
    ref_validity = len(valid_refs) / len(refs) if refs else 0.0

    # 2. No orphan Observations: every O should be cited by >=1 gap or by the insight
    cited_os = set()
    for g in gaps:
        cited_os.update(x for x in (g.get("caused_by") or []) if x in obs_ids)
    cited_os.update(x for x in (insight.get("derived_from") or []) if x in obs_ids)
    obs_integration = len(cited_os) / len(obs_ids)

    # 3. No orphan Gaps: every G should feed the Key Insight
    cited_gaps = set(x for x in (insight.get("derived_from") or []) if x in gap_ids)
    gap_integration = len(cited_gaps) / len(gap_ids) if gap_ids else 0.0

    return round(0.4 * ref_validity + 0.3 * obs_integration + 0.3 * gap_integration, 4)
```

**What the function does & why.** It builds the ID universe from Observations and Gaps, then checks
three things: (a) do all `caused_by`/`derived_from` pointers resolve to real nodes (catches
fabricated or sloppy cross-refs), (b) is every Observation actually used by some downstream Gap or
the Insight (catches decorative "prior work exists" filler that never does argumentative work), (c)
does every Gap actually feed the Key Insight (catches gaps that were listed but never resolved,
i.e. an unaddressed loose end in the paper's own framing). Missing sections collapse the whole score
to 0 per the hard constraint.

**Why it's hard to Goodhart.** You cannot inflate this by adding decorative Observations/Gaps,
because unintegrated nodes actively drag `obs_integration`/`gap_integration` down — the metric
rewards *density of real use*, not *count*. You also cannot fix it by wiring every O into every G
indiscriminately, because that would require the Gap's `caused_by` list to reference IDs that a
plain-language reading of the Gap's own `statement` doesn't support — which metric 4 (specificity)
and a human/LLM semantic check would catch as incoherent.

---

## 2. Evidentiary Grounding Depth

**How it signals good science.** Good science traces claims to specific, checkable sources.
"Evidence: Abstract" or a single reused citation for every Observation signals a compiler (or a
paper) that never actually engaged with the Introduction/prior-work chain — it signals compression,
not synthesis. Real problem framing draws on section-level, multi-citation evidence, and different
Observations should draw on at least partially different literature (if every Observation cites the
identical source, the "problem space" hasn't actually been surveyed).

**Compute function.**

```python
import re

def evidentiary_grounding_depth(problem: dict) -> float:
    """
    Assumes: each observation dict has an "evidence" string field (possibly empty/missing).
    Penalizes missing, generic ("Abstract"-only), or duplicated-across-the-board evidence.
    """
    obs = problem.get("observations", [])
    if not obs:
        return 0.0

    GENERIC = {"abstract", "n/a", "unknown", "unspecified", ""}
    citation_pat = re.compile(r"[A-Z][a-zA-Z\-]+(?:\s+et al\.)?,?\s*\(?\d{4}[a-z]?\)?")
    section_pat = re.compile(r"§|\bSection\b|\bIntroduction\b|\bMethods\b|\bResults\b", re.I)

    per_obs_scores = []
    citation_sets = []
    for o in obs:
        ev = (o.get("evidence") or "").strip()
        if ev.lower() in GENERIC:
            per_obs_scores.append(0.0)
            citation_sets.append(set())
            continue
        cites = set(m.group(0) for m in citation_pat.finditer(ev))
        has_section_ref = bool(section_pat.search(ev))
        depth = min(len(cites), 3) / 3.0          # more distinct citations -> more grounded, capped
        score = 0.6 * depth + 0.4 * (1.0 if has_section_ref else 0.0)
        per_obs_scores.append(score)
        citation_sets.append(cites)

    base = sum(per_obs_scores) / len(per_obs_scores)

    # Diversity penalty: if >1 observation exists but the citation sets are ~identical
    # (or all empty), the "survey" is a single fact reused, not real coverage.
    nonempty_sets = [s for s in citation_sets if s]
    if len(obs) > 1 and len(nonempty_sets) > 1:
        union = set().union(*nonempty_sets)
        overlap_ratio = 1 - (len(union) / sum(len(s) for s in nonempty_sets))
        diversity_penalty = overlap_ratio * 0.3
    else:
        diversity_penalty = 0.3 if len(obs) > 1 else 0.0  # can't prove diversity -> penalize

    return round(max(0.0, base - diversity_penalty), 4)
```

**What the function does & why.** For each Observation, it scores the `evidence` field on two axes:
how many distinct author-year citations it contains (capped, since three specific citations is
already "deep enough" — this avoids rewarding citation-dumping), and whether it names a section
(Introduction/Methods/§) rather than just "Abstract". It then applies a diversity penalty across all
Observations: if the citation sets barely differ from each other, the paper's problem framing is
built on one recycled fact, not a genuine literature survey, and the whole score is docked.

**Why it's hard to Goodhart.** Pure citation-stuffing is capped per-Observation (diminishing
returns past 3 real cites), and copy-pasting the *same* rich-looking citation list into every
Observation to defeat the per-item check gets caught by the diversity penalty, which explicitly
punishes near-identical citation sets across Observations. To win both sub-scores you need
Observations that are actually about different sub-claims drawing on different parts of the
literature — which is precisely "surveyed the field," not "gamed the regex."

---

## 3. Insight Emergence Score

**How it signals good science.** The Key Insight is supposed to be a *creative leap* — new
conceptual connective tissue that resolves the tension between what's Observed and what's Missing.
A shallow compile (or a shallow paper) just restates the method's name in that slot ("Insight: we use
a network meta-analysis"), or alternatively just concatenates the referenced Observations/Gaps
verbatim without adding anything. Genuine insight text is lexically distinct from its own citation
chain (it says something the O's/G's didn't already say) while still being clearly *about* the
Gaps it claims to resolve (checked against `enables` and the target Gaps, not the Insight's own
`derived_from` text).

**Compute function.**

```python
import re

_STOP = {"the","a","an","of","to","and","in","for","is","that","this","on","with","as","by","or","be","are"}

def _wordset(text: str) -> set:
    return {w for w in re.findall(r"[a-z]+", (text or "").lower()) if w not in _STOP and len(w) > 2}

def insight_emergence_score(problem: dict) -> float:
    """
    Assumes: problem["key_insight"] has "insight", "derived_from" (list of O/G ids), "enables".
    Assumes problem["observations"] / ["gaps"] lists to resolve derived_from ids and to find
    the gaps the insight should be addressing.
    """
    ki = problem.get("key_insight")
    if not ki or not (ki.get("insight") or "").strip():
        return 0.0

    insight_text = ki["insight"]
    insight_words = _wordset(insight_text)
    if len(insight_words) < 6:
        return 0.1  # trivial / method-name-only insight, not a stated leap

    obs_by_id = {o["id"]: o for o in problem.get("observations", [])}
    gap_by_id = {g["id"]: g for g in problem.get("gaps", [])}
    derived = ki.get("derived_from", [])
    if not derived:
        return 0.15  # ungrounded insight -- claims a leap from nothing

    source_text = " ".join(
        (obs_by_id.get(r) or gap_by_id.get(r) or {}).get("statement", "") for r in derived
    )
    source_words = _wordset(source_text)

    # Non-restatement: insight shouldn't just be a shuffle of its own source words
    overlap = len(insight_words & source_words) / len(insight_words) if insight_words else 1.0
    novelty = 1.0 - overlap  # more new vocabulary relative to sources = more of a genuine leap
    novelty_score = max(0.0, min(1.0, novelty))
    # too much novelty (near-zero overlap) means the insight is disconnected from its own
    # citation chain -- also bad. Reward a mid-band (some shared grounding, real new content).
    novelty_component = 1.0 - abs(novelty_score - 0.55) / 0.55

    # Relevance: insight + enables should engage with the actual Gap statements it targets
    target_gap_words = _wordset(" ".join(gap_by_id[g]["statement"] for g in derived if g in gap_by_id))
    enables_words = _wordset(ki.get("enables", ""))
    combined = insight_words | enables_words
    relevance = (len(combined & target_gap_words) / len(target_gap_words)
                 if target_gap_words else 0.5)  # no gap targeted directly -> neutral-low, not N/A

    return round(0.5 * max(0.0, novelty_component) + 0.5 * min(1.0, relevance), 4)
```

**What the function does & why.** It rejects empty or ungrounded insights outright, then compares
the Insight's vocabulary against the vocabulary of the Observations/Gaps it claims to derive from.
Pure restatement (near-total word overlap) and pure disconnection (near-zero overlap) are both
penalized; a real conceptual leap sits in between — recognizably connected to its sources but
introducing new synthesizing language. It then separately checks that the Insight + Enables text
actually engages with the vocabulary of the specific Gaps it targets, so an insight can't score well
by being "creative" about the wrong problem.

**Why it's hard to Goodhart.** Padding the insight with unrelated novel vocabulary to chase the
novelty band tanks the relevance term (the new words won't overlap with the target Gap's language).
Copying the Gap's own wording to chase relevance instead tanks novelty (overlap climbs back toward
pure restatement). The two sub-scores pull in opposite directions on the same text, so a cheap
one-sided edit to game either half shows up as a drop in the other.

---

## 4. Gap Specificity (Anti-Genericity)

**How it signals good science.** "Existing attempts: prior work is limited" / "Why they fail:
insufficient data" is a compression signal, not a finding — it means the author (or the compiler)
didn't actually characterize what's been tried and why it fell short. A rigorous problem framing
names the prior approaches and states a mechanistic or empirical reason they fail, which is exactly
what lets a downstream reader evaluate whether the new method actually addresses that failure mode.

**Compute function.**

```python
import re

_GENERIC_PHRASES = [
    "prior work is limited", "not well studied", "little research", "insufficient data",
    "limited data", "poorly understood", "not well understood", "few studies",
    "lack of studies", "understudied", "not been explored", "remains unclear",
]

def gap_specificity(problem: dict) -> float:
    """
    Assumes: each gap dict has "existing_attempts" and "why_fail" string fields (possibly
    missing/empty), and a "statement" field used to normalize specificity by gap length.
    """
    gaps = problem.get("gaps", [])
    if not gaps:
        return 0.0

    named_entity_pat = re.compile(r"\b[A-Z][a-zA-Z]{2,}\b|\d{4}|\bet al\.")

    scores = []
    for g in gaps:
        attempts = (g.get("existing_attempts") or "").strip()
        fail = (g.get("why_fail") or "").strip()
        if not attempts or not fail:
            scores.append(0.0)
            continue

        combined = f"{attempts} {fail}"
        combined_lower = combined.lower()

        generic_hits = sum(1 for phrase in _GENERIC_PHRASES if phrase in combined_lower)
        genericity_penalty = min(1.0, generic_hits * 0.4)

        specificity_markers = len(named_entity_pat.findall(combined))
        length_norm = max(len(combined.split()), 1)
        specificity_density = min(1.0, specificity_markers / (length_norm ** 0.5) / 2.0)

        score = max(0.0, specificity_density - genericity_penalty)
        scores.append(score)

    return round(sum(scores) / len(scores), 4)
```

**What the function does & why.** For each Gap, it requires both `existing_attempts` and `why_fail`
to be present at all (missing -> 0 for that gap). It then scans for boilerplate hand-wave phrases
(explicit penalty) and independently counts specificity markers — proper nouns, years, "et al."
tokens — that indicate the text is naming actual prior methods/studies rather than gesturing at
"prior work." The density is normalized by text length so a gap can't win purely by being long.

**Why it's hard to Goodhart.** Simply avoiding the blocklisted phrases without adding real content
doesn't help, because the score is *specificity density*, not *absence of generic phrases* — bland
paraphrases of the same vagueness ("methods to date have not sufficiently addressed this") still
score low on the named-entity/year count. Conversely, stuffing in random capitalized words or dates
to game the entity count is exposed cheaply by a semantic spot-check (or by metric 1's
referential-integrity logic, since fabricated "prior attempts" have no corresponding Observation to
have surfaced them).

---

## 5. Assumption Load-Bearing Score

**How it signals good science.** Assumptions are supposed to be the falsifiable joints where the
argument could break — "if A2 is false, the whole analysis collapses." A list of vague hedges
("results are generally reliable") isn't doing that job; neither is an assumption that's just a
Gap restated as a claim. A good Assumptions section names checkable conditions (often
quantitative/structural) that are distinct from, but clearly load-bearing for, the argument made in
the Gaps and Key Insight.

**Compute function.**

```python
import re

_HEDGE_WORDS = {"generally", "typically", "likely", "probably", "often", "usually", "may", "might", "should"}
_CHECKABLE_MARKERS = re.compile(
    r"\bno\s+\w+\s+counted\s+twice\b|\bindependent\b|\bequal\b|\bat\s+least\b|\bat\s+most\b|"
    r"\d+%|\d+\.\d+|\byields\b|\bimplies\b|\bassumes\b|\brandom\b|\bnormal(ly)?\b|\bhomogeneous\b",
    re.I,
)

def _wordset(text):
    return {w for w in re.findall(r"[a-z]+", (text or "").lower()) if len(w) > 2}

def assumption_load_bearing(problem: dict) -> float:
    """
    Assumes: problem["assumptions"] is a list of {"id","text"}; problem["gaps"] list with
    "statement" used to check redundancy; problem["key_insight"] used to check relevance
    (assumptions should plausibly matter to the insight's validity).
    """
    assumptions = problem.get("assumptions", [])
    gaps = problem.get("gaps", [])
    if not assumptions:
        return 0.0

    gap_word_union = set()
    for g in gaps:
        gap_word_union |= _wordset(g.get("statement", ""))
    ki_words = _wordset((problem.get("key_insight") or {}).get("insight", ""))
    relevance_pool = gap_word_union | ki_words

    scores = []
    for a in assumptions:
        text = (a.get("text") or "").strip()
        if not text:
            scores.append(0.0)
            continue

        words = _wordset(text)
        hedge_ratio = len(words & _HEDGE_WORDS) / max(len(words), 1)
        checkable = bool(_CHECKABLE_MARKERS.search(text))

        # redundancy: if the assumption is >70% the same vocabulary as a Gap statement,
        # it's not adding a new load-bearing condition, it's restating the problem.
        redundant = any(
            len(words & _wordset(g.get("statement", ""))) / max(len(words), 1) > 0.7
            for g in gaps
        )
        relevant = bool(words & relevance_pool)

        score = 0.4 * (1.0 if checkable else 0.0) + 0.3 * (1.0 - hedge_ratio) + 0.3 * (1.0 if relevant else 0.0)
        if redundant:
            score *= 0.3
        scores.append(max(0.0, min(1.0, score)))

    # Coverage penalty: fewer assumptions than gaps suggests under-articulated risk surface
    coverage = min(1.0, len(assumptions) / max(len(gaps), 1))

    return round((sum(scores) / len(scores)) * (0.7 + 0.3 * coverage), 4)
```

**What the function does & why.** Per assumption, it rewards concrete/checkable phrasing (numeric
thresholds, independence/equality claims, explicit "assumes/implies" structure), penalizes hedge
words that make the assumption unfalsifiable, and heavily discounts assumptions that are just a Gap
statement reworded (redundant, not load-bearing). It also requires the assumption's vocabulary to
actually connect to the Gaps/Insight (an assumption about something irrelevant to the argument isn't
doing real work). Finally it scales the whole score down if there are fewer assumptions than gaps,
since a complex multi-gap argument with only one throwaway assumption is under-articulating its own
risk surface.

**Why it's hard to Goodhart.** Adding many vague assumptions to chase the coverage ratio tanks the
per-item score (hedge words, no checkable markers), and rephrasing Gaps as fake "assumptions" to
pad the list is caught by the redundancy discount. Writing sharp, quantitative-sounding but
irrelevant assumptions (to win the checkable-marker check) fails the relevance-pool overlap test.
The three sub-checks (checkability, non-hedging, relevance-without-redundancy) target three
different cheap-gaming strategies at once.

---

## Combination

These five metrics interlock through the same underlying graph so that gaming one degrades another.
Metric 1 (Traceability) rewards *density of real use* of Observations/Gaps — so an author cannot
pad Observations with generic evidence to satisfy Metric 2 without those Observations also needing
to be cited somewhere downstream, or Metric 1 falls. Metric 2 (Grounding Depth) makes citation-
stuffing self-defeating by penalizing repeated/near-identical citation sets across Observations, so
inflating Evidence fields to look rigorous costs diversity. Metric 3 (Insight Emergence) is
adversarial to both restating sources verbatim (loses novelty) and to inventing unrelated "creative"
language (loses relevance to the actual Gaps), and it depends on Metric 1's `derived_from` graph
being real — a fabricated derivation chain shows up as source text that doesn't semantically match.
Metric 4 (Gap Specificity) punishes exactly the compression shortcut (generic "prior work is
limited" filler) that a low-effort compile would use to satisfy Metrics 1–3 quickly without doing
real synthesis work, and fabricated specificity (fake named entities) has no support in the
Observations, which a careful pass of Metric 1/2 together would flag as ungrounded. Metric 5
(Assumption Load-Bearing) closes the loop: it penalizes assumptions that are just reworded Gaps
(the cheapest way to inflate Metric 1's graph-coverage numbers by adding nodes) and requires
checkable, non-hedged content, so an author who tries to win Metric 1's coverage scores by
manufacturing extra shallow nodes anywhere in the document (Observations, Gaps, or Assumptions) gets
caught by whichever of Metrics 2–5 inspects that node's actual content.
