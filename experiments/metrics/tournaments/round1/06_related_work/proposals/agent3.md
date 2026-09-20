# Proposer #3 — metrics for `logic/related_work.md`

All functions assume the artifact has been parsed into this representation:

```python
artifact = {
    "full_blocks": [
        {
            "id": "RW01",
            "author_year": "Janelidze et al., 2023",
            "doi": "10.1093/brain/awac333",          # or "Not specified in paper" or None/""
            "type": "imports (data source)",          # one of imports|bounds|baseline|extends|refutes, compound forms allowed
            "what_changed": "head-to-head comparison of 10 plasma phospho-tau assays in prodromal AD.",
            "why": "selected as the most comprehensive head-to-head dataset for the BioFINDER-1 cohort.",
            "claims_affected": ["C01", "C07"],         # [] or ["none"] if "none directly (motivation)"
            "adopted_elements": "BioFINDER-1 dataset (N=135; MCI/prodromal AD; p-tau 217/181/231; IP-MS and Simoa; CSF Abeta42/40).",
        },
        ...
    ],
    "brief_refs": [
        {"author_year": "Hansson et al., 2023", "doi": "10.1038/s41582-023-00403-3", "role": "blood biomarkers in clinical practice/trials; motivation."},
        ...
    ],
    "grounded_source_block": None,   # or {"title": ..., "text": ...} for a folded-in non-bibliographic source
}
```

If the whole artifact is missing/empty, every function below treats `full_blocks == []` (and `brief_refs == []`) as the degenerate case and returns the metric's floor score, not `None`/N-A.

---

## 1. DOI Resolvability Rate

**How it signals good science.** The stated purpose of this artifact is to let a downstream agent
*trace provenance* of data, methods, and comparator claims. A DOI (or arXiv ID) is the one field that
actually makes a citation machine-followable — "Not specified in paper" is a dead end. A compiler (and,
transitively, a paper's own citation discipline) that resolves DOIs for most of its footprint is doing
the actual archival work good science requires; one that shrugs into placeholder text for most entries
is producing a graph that *looks* structured but isn't actually traceable.

**Compute function.**

```python
import re

def doi_resolvability_rate(artifact: dict) -> float:
    """
    Assumes: artifact["full_blocks"] is a list of dicts with a "doi" string field;
    artifact["brief_refs"] is a list of dicts with a "doi" string field.
    A block counts as "resolved" if its doi field, once stripped, matches a DOI
    (10.xxxx/...) or an arXiv id pattern, and is not a placeholder string.
    Full blocks are weighted 2x brief refs, since full blocks are where the ARA's
    own provenance claims (deltas, adopted elements) live and most need grounding.
    """
    doi_pattern = re.compile(r"^(10\.\d{4,9}/\S+|arxiv[:\s]?\d{4}\.\d{4,5}(v\d+)?)$", re.I)
    placeholders = {"", "not specified in paper", "none", "n/a", "na", "not available"}

    def is_resolved(doi):
        if doi is None:
            return False
        s = doi.strip().lower()
        if s in placeholders:
            return False
        return bool(doi_pattern.match(doi.strip()))

    full = artifact.get("full_blocks", [])
    brief = artifact.get("brief_refs", [])

    if not full and not brief:
        return 0.0  # empty footprint: hard floor, never N/A

    full_w, brief_w = 2.0, 1.0
    total_weight = len(full) * full_w + len(brief) * brief_w
    if total_weight == 0:
        return 0.0

    resolved_weight = (
        sum(full_w for b in full if is_resolved(b.get("doi")))
        + sum(brief_w for b in brief if is_resolved(b.get("doi")))
    )
    return round(resolved_weight / total_weight, 4)
```

**What the function does & why.** It walks every full and brief reference, classifies its `doi` field
as a genuine resolvable identifier or a placeholder/absence, and returns a weighted fraction resolved
(full blocks count double, since they're the ones the ARA leans on for delta/claim provenance). An
empty artifact returns `0.0` rather than skipping — no footprint means no traceability, full stop.

**Why it's hard to Goodhart.** You can't fabricate DOIs cheaply and get away with it: DOIs are
externally checkable strings (format-checkable here, resolvable-checkable downstream), so a fake
`10.xxxx/fake` either fails the regex if sloppy or fails resolution the moment anyone clicks it —
and this metric is designed to be paired with a downstream resolution check, not just a format check,
so format-only gaming is a temporary win at best. Padding the graph with real-but-irrelevant DOIs to
inflate the rate collides with Metric 3 (delta specificity) and Metric 4 (claim grounding), because
padding entries tend to have thin/generic deltas and no claim linkage.

---

## 2. Tiered-Coverage Completeness

**How it signals good science.** The shape doc is explicit: a related-work graph with *only* full
`RW##` blocks and no "brief" tier is a documented failure signature — it means the compiler (and by
extension the underlying paper-reading process) never swept the full reference list, so the graph
silently narrows to "closest predecessors" instead of the paper's true citation footprint. Good science
reporting is honest about its *entire* intellectual debt, not just the convenient, load-bearing part.

**Compute function.**

```python
def tiered_coverage_completeness(artifact: dict) -> float:
    """
    Assumes: artifact["full_blocks"] and artifact["brief_refs"] are lists (possibly empty).
    Rewards (a) the mere presence of a brief tier once there is any real footprint to speak of,
    and (b) a brief:full ratio in the range observed in real full-text compiles (roughly 1:1 to 2:1;
    see che26 ~1.2x, huu25 ~2.2x). Under-scales smoothly rather than cliff-dropping, so a legitimately
    small paper isn't crushed, but a zero-brief graph is capped low regardless of full-block count.
    """
    full = artifact.get("full_blocks", [])
    brief = artifact.get("brief_refs", [])
    n_full, n_brief = len(full), len(brief)

    if n_full == 0 and n_brief == 0:
        return 0.0

    # Abstract-only signature: 1-3 full blocks, no brief tier at all -> explicit stark gap per shape doc.
    if n_brief == 0:
        return 0.05 if n_full <= 3 else 0.15  # some full-only graphs may be real but are still uncovered

    ratio = n_brief / max(n_full, 1)
    ratio_score = min(ratio / 1.0, 1.0)          # full credit once brief >= full count
    presence_score = 1.0
    return round(0.4 * presence_score + 0.6 * ratio_score, 4)
```

**What the function does & why.** It first handles the empty case as a hard floor. Then it applies the
explicit "no brief tier" penalty from the shape doc's own availability notes, scaled slightly by whether
the full-block count itself looks like an abstract-only compile (≤3) or a suspiciously large full-only
graph (>3, still penalized but a notch less harshly since some signal exists). Once a brief tier exists
at all, it rewards the brief:full ratio up to parity, matching what real full-text compiles look like.

**Why it's hard to Goodhart.** You could dump dozens of low-effort one-line brief entries to inflate
the ratio cheaply — but that directly trades off against Metric 1 (those entries usually lack resolvable
DOIs, since low-effort brief-stuffing skips lookup) and against Metric 5 (adopted-elements concreteness
stays untouched by brief-tier padding, so the "full" side of the ledger doesn't move, capping the
combined score). You also can't just relabel full blocks as brief to hit the ratio, because that shrinks
`n_full`, which is exactly the denominator this metric is trying to keep honest relative to claim/delta
richness measured elsewhere.

---

## 3. Delta Specificity & Non-Template Score

**How it signals good science.** The whole point of a full `RW##` block is that it carries a *specific
technical delta* — "what changed" and "why" tied to concrete facts (a dataset size, an assay, a named
method), not a boilerplate sentence that could be copy-pasted onto any citation. Specific, mutually
distinct deltas are strong evidence the paper (and the extraction process) actually engaged each cited
work individually — the hallmark of careful scholarship over citation-list padding.

**Compute function.**

```python
import re

def delta_specificity_score(artifact: dict) -> float:
    """
    Assumes: each full block has "what_changed" and "why" strings.
    Specificity indicator per block: presence of a number/quantity token (N=, %, digit sequences,
    units) or a multi-word capitalized proper noun (dataset/method/tool name) in "what_changed",
    combined with a minimal length floor.
    Template indicator across blocks: mean pairwise Jaccard similarity of "what_changed" word-sets;
    high average similarity implies the deltas were stamped from a shared template rather than
    written per-citation.
    """
    number_or_unit = re.compile(r"(\bN\s*=\s*\d+|\d+(\.\d+)?\s?(%|mm|ml|kg|years?|patients?|cohort)|\b\d{2,}\b)", re.I)
    proper_noun_run = re.compile(r"\b([A-Z][a-zA-Z0-9\-]+(\s+[A-Z][a-zA-Z0-9\-]+){1,})\b")

    full = artifact.get("full_blocks", [])
    if not full:
        return 0.0

    def specificity(block):
        text = (block.get("what_changed") or "").strip()
        if len(text.split()) < 5:
            return 0.0
        has_signal = bool(number_or_unit.search(text) or proper_noun_run.search(text))
        return 1.0 if has_signal else 0.3  # some credit for length, most credit needs a concrete marker

    per_block_scores = [specificity(b) for b in full]
    mean_specificity = sum(per_block_scores) / len(per_block_scores)

    # Pairwise near-duplicate / template detection over "what_changed" text.
    texts = [set((b.get("what_changed") or "").lower().split()) for b in full]
    sims = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i], texts[j]
            if not a or not b:
                sims.append(1.0)  # empty deltas are treated as maximally template-like (penalized)
                continue
            jaccard = len(a & b) / len(a | b)
            sims.append(jaccard)
    avg_sim = sum(sims) / len(sims) if sims else 0.0
    template_penalty = max(0.0, avg_sim - 0.25) * 1.3  # tolerate some natural domain-vocabulary overlap

    return round(max(0.0, mean_specificity - template_penalty), 4)
```

**What the function does & why.** For every full block it checks whether the "what changed" text
carries a concrete, checkable marker (a number, a unit, a named dataset/method) rather than being
generic filler, and averages that across the graph. It then separately measures how textually similar
the deltas are to *each other*; if they're suspiciously uniform (a sign of template stamping or
copy-paste extraction) it subtracts a penalty. Empty deltas count as fully template-like, not skipped.

**Why it's hard to Goodhart.** Padding every delta with a random number or a capitalized phrase to
trip the regex is detectable by the template-similarity term the moment the same trick is repeated
across blocks — inserting the same kind of filler number ("N=100" everywhere) raises `avg_sim` and
eats the gain. Writing genuinely varied text to dodge the similarity penalty, without any real
number/entity content, is caught by the per-block specificity check instead. Beating both at once
requires actually writing distinct, concrete deltas per citation — which is the behavior being measured.

---

## 4. Claim-Grounding Density

**How it signals good science.** A related-work edge that names the specific claim IDs it supports,
bounds, or is baselined against demonstrates the paper's argument is actually *wired* to its citations,
not just gesturing at a literature. `"none directly (motivation)"` is a legitimate value for background
citations, but a graph where *almost every* full block claims direct linkage to *the same one or two*
claim IDs, or where *no* block ever links to a claim, are both signs of shallow or fabricated grounding
rather than real argumentative structure.

**Compute function.**

```python
def claim_grounding_density(artifact: dict) -> float:
    """
    Assumes: each full block has "claims_affected" as a list of claim-id strings, or a list
    containing a single sentinel like "none" (case-insensitive) when not directly tied to a claim.
    Missing/absent field is treated as "none" (i.e., ungrounded), not skipped.
    """
    full = artifact.get("full_blocks", [])
    if not full:
        return 0.0

    def claim_ids(block):
        raw = block.get("claims_affected")
        if not raw:
            return []
        return [c for c in raw if c and c.strip().lower() not in {"none", "n/a", "na"}]

    per_block = [claim_ids(b) for b in full]
    grounded_frac = sum(1 for ids in per_block if ids) / len(full)

    all_refs = [cid for ids in per_block for cid in ids]
    if not all_refs:
        return 0.0  # nothing links to any claim: floor, not N/A

    unique_claims = len(set(all_refs))
    # Diversity guards against "blanket-tag every RW block with the same claim ID" gaming.
    diversity = unique_claims / len(all_refs)

    # Expect a healthy graph to ground a meaningful minority-to-majority of full blocks (not 0%, not
    # necessarily 100% -- background/motivation-only RW blocks are legitimate).
    grounded_score = min(grounded_frac / 0.5, 1.0)  # full credit once >=50% of blocks are claim-linked
    diversity_score = min(diversity / 0.5, 1.0)     # full credit once linked claims aren't all the same ID

    return round(0.5 * grounded_score + 0.5 * diversity_score, 4)
```

**What the function does & why.** It separates "linked to a real claim ID" from the legitimate `none`
sentinel, computes what fraction of full blocks carry real linkage, and separately checks whether the
claim IDs referenced are diverse (not all pointing at one claim, which would suggest indiscriminate
tagging rather than genuine per-citation argument-wiring). Both sub-scores saturate at a realistic
target rather than demanding 100%, since motivation-only background citations are expected to exist.

**Why it's hard to Goodhart.** Tagging every RW block with the same convenient claim ID to inflate
`grounded_frac` is directly caught by the `diversity_score` term. Manufacturing many distinct fake claim
IDs to beat diversity requires those IDs to actually exist and be referenced elsewhere in the ARA's
claims ledger — an internal-consistency check outside this file but implied by the artifact's own
cross-referencing design — and doing so convincingly means writing real, distinguishable deltas per
claim, which pulls directly against the cheap, generic text patterns Metric 3 punishes.

---

## 5. Adopted-Elements Concreteness

**How it signals good science.** "Adopted elements" is where the ARA states exactly what was *reused*
from prior work — a dataset with its N, a specific tool version, a named parameter set. This is the
field a downstream agent or auditor would use to actually reproduce or sanity-check what was borrowed.
Vague adopted-elements text ("used their approach", "built on their method") signals the extraction (and
possibly the paper itself) never pinned down what was concretely inherited — a reproducibility gap
disguised as a citation.

**Compute function.**

```python
import re

def adopted_elements_concreteness(artifact: dict) -> float:
    """
    Assumes: each full block has an "adopted_elements" string (possibly empty/missing).
    Concreteness indicators: sample-size markers (N=...), parenthetical specification lists,
    numeric/unit tokens, or multiple distinct named entities (capitalized multi-word terms).
    Blocks with type "refutes" or "bounds" are exempted from a bare "no adoption" penalty only
    when adopted_elements is explicitly empty AND the type does not imply adoption -- otherwise
    empty is scored as a concrete failure, not skipped.
    """
    n_marker = re.compile(r"\bN\s*=\s*\d+", re.I)
    numeric_unit = re.compile(r"\d+(\.\d+)?\s?(%|years?|patients?|ml|mg|kg|-\w+)?")
    named_entities = re.compile(r"\b([A-Z][a-zA-Z0-9\-]{2,})\b")

    full = artifact.get("full_blocks", [])
    if not full:
        return 0.0

    def concreteness(block):
        text = (block.get("adopted_elements") or "").strip()
        edge_type = (block.get("type") or "").lower()
        if not text:
            # "bounds"/"refutes" edges legitimately may adopt nothing -- still score low, not N/A,
            # since the shape doc treats missing/thin fields as penalized, never skipped.
            return 0.1 if ("bounds" in edge_type or "refutes" in edge_type) else 0.0
        score = 0.0
        if n_marker.search(text):
            score += 0.4
        if numeric_unit.search(text):
            score += 0.2
        entity_hits = len(set(named_entities.findall(text)))
        if entity_hits >= 2:
            score += 0.4
        elif entity_hits == 1:
            score += 0.2
        return min(score, 1.0)

    scores = [concreteness(b) for b in full]
    return round(sum(scores) / len(scores), 4)
```

**What the function does & why.** For each full block it looks for the concrete fingerprints of real
reuse — an explicit sample size, a numeric/unit quantity, or multiple named entities (dataset/tool/
method names) — and scores accordingly. Empty adopted-elements text scores at or near zero rather than
being skipped, with a small allowance for edge types (`bounds`/`refutes`) where "nothing adopted" is
plausible but still not free.

**Why it's hard to Goodhart.** Stuffing "adopted_elements" with a fake `N=` and a string of capitalized
words to farm points produces text that collides with Metric 3's template-similarity check if repeated
across blocks, and produces entities that don't correspond to anything in the DOI-resolved source
(checkable by cross-referencing Metric 1's resolved DOI against the named dataset/tool, even if that
cross-check lives outside this function's scope) — a fabricated concrete detail is exactly the kind of
claim that's cheap to write but expensive to fake consistently across a paper's whole RW graph.

---

## Combination

These five metrics are built to tax each other's cheap wins. Inflating **DOI Resolvability** by
padding the footprint with real-but-irrelevant citations dilutes **Delta Specificity** and **Claim
Grounding Density**, because padding entries carry generic deltas and no claim linkage. Inflating
**Tiered-Coverage Completeness** by dumping low-effort brief entries doesn't touch the full-block side
at all, so **Adopted-Elements Concreteness** and **Delta Specificity** stay flat and the combined score
barely moves. Gaming **Delta Specificity** with templated-but-varied filler text collides with **Claim
Grounding Density**'s diversity check once the same trick is reused to fabricate claim linkage, and
collides with **Adopted-Elements Concreteness** if the same fabricated entities are reused there too.
Blanket-tagging every block with one claim ID to farm **Claim Grounding Density** is caught by its own
diversity term, and doing it convincingly (distinct claims, distinct justifying text) requires exactly
the kind of specific, non-template writing that **Delta Specificity** already rewards honestly. In
short: the cheap move for any one metric is either invisible to it (coverage padding) or actively
punished by at least one other metric (specificity/grounding/concreteness triangle), so a low-effort
paper cannot cheaply clear all five at once — only a graph with real, resolvable, distinct, claim-wired,
concretely-described prior-work relationships can.
