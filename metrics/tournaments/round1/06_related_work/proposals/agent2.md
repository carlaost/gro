# Proposer 2 — metrics for `logic/related_work.md`

## 1. Delta Concreteness Score

**How it signals good science.** A `related_work.md` block earns its keep by stating a *specific*
technical delta ("what changed" / "why") — a dataset size, an assay name, a version number, an effect
size. Vague boilerplate ("various prior methods", "well-known techniques") is what a citation dump
looks like when nobody actually worked out the technical relationship to the prior source. More
concrete, falsifiable technical content in the Delta fields is direct evidence the artifact captured
real epistemic work, not decoration.

**Compute function.**
```python
import re

def delta_concreteness_score(artifact: dict) -> float:
    """
    Assumes `artifact['full_blocks']` is a list of dicts, each with string keys
    'delta_what' and 'delta_why' (the two Delta sub-fields of one RW## block).
    An artifact with zero full blocks (mandatory-core section wholly missing
    its substantive content) scores 0.0 -- never skipped.
    """
    blocks = artifact.get('full_blocks', [])
    if not blocks:
        return 0.0

    GENERIC_FILLER = [
        r'\bvarious (methods|studies|approaches)\b', r'\bprior work\b',
        r'\bseveral studies\b', r'\bwell[- ]known\b',
        r'\bstandard (method|approach|technique)\b', r'\bcommonly used\b',
        r'\bwidely (used|cited|adopted)\b',
    ]
    CONCRETE_MARKERS = [
        r'\bN\s*=\s*\d+', r'\d+(\.\d+)?\s*%', r'\bp\s*[<=]\s*0?\.\d+',
        r'\b[A-Za-z][A-Za-z0-9]*[-/][A-Za-z0-9]+\b',   # e.g. p-tau217, IP-MS
        r'\b\d+(\.\d+)?\b',                            # bare numbers (N, doses, versions)
        r'\b[A-Z]{2,}\b',                               # acronyms (assay/method names)
    ]

    scores = []
    for b in blocks:
        text = f"{b.get('delta_what','')} {b.get('delta_why','')}".strip()
        if not text:
            scores.append(0.0)
            continue
        filler_hits = sum(bool(re.search(p, text, re.I)) for p in GENERIC_FILLER)
        concrete_hits = sum(len(re.findall(p, text)) for p in CONCRETE_MARKERS)
        raw = concrete_hits - 2 * filler_hits
        block_score = max(0.0, min(1.0, raw / (raw + 3))) if raw > 0 else 0.0
        scores.append(block_score)

    return sum(scores) / len(scores)
```

**What the function does & why.** For every full RW block it concatenates the two Delta sub-fields and
counts concrete technical markers (numbers, percentages, p-values, hyphenated technical tokens,
acronyms) against generic filler phrases. Filler is penalized twice as hard as a concrete hit is
rewarded, so a sentence that pairs one number with three hedge-phrases still scores near zero. Blocks
with an empty Delta score 0. The artifact's score is the mean over all full blocks — one padded/thin
block drags the average down rather than being invisible.

**Why it's hard to Goodhart.** Simply injecting numbers or acronyms without semantic connection to the
rest of the block ("Adopted elements", "Claims affected") is caught by Metric 2 below, which checks
that the same technical tokens actually recur between the Delta and what was adopted. Concreteness
alone, decoupled from consistency, doesn't move the combined score.

---

## 2. Provenance-Grounding Score (Adopted ↔ Delta consistency)

**How it signals good science.** Good science is auditable: if a paper says it *adopted* a dataset or
method, the "what changed" text should name the same thing, not a disconnected laundry list bolted on
after the fact. Requiring lexical/semantic overlap between "Adopted elements" and "Delta → What
changed" tests whether the artifact preserved a genuine provenance chain (you can trace exactly which
technical objects flowed from RW## into this paper) rather than two independently-written, unlinked
prose blobs.

**Compute function.**
```python
import re

def provenance_grounding_score(artifact: dict) -> float:
    """
    Assumes `artifact['full_blocks']` is a list of dicts, each with string keys:
      'type'             -- e.g. 'imports (data source)', 'baseline', 'extends', ...
      'adopted_elements' -- prose from the Adopted-elements field
      'delta_what'       -- prose from Delta -> What changed
    Missing full_blocks -> 0.0.
    """
    blocks = artifact.get('full_blocks', [])
    if not blocks:
        return 0.0

    EMPTY_MARKERS = {'', 'n/a', 'none', 'not specified', 'not applicable'}

    def tokenize(s):
        return set(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]{2,}', s or ''))

    scores = []
    for b in blocks:
        adopted = (b.get('adopted_elements') or '').strip()
        btype = (b.get('type') or '').lower()

        if adopted.lower() in EMPTY_MARKERS:
            # imports/baseline types definitionally reuse something concrete;
            # an empty Adopted-elements field there is a real provenance gap.
            scores.append(0.0 if ('imports' in btype or 'baseline' in btype) else 0.2)
            continue

        adopted_tokens = tokenize(adopted)
        delta_tokens = tokenize(b.get('delta_what') or '')
        overlap = adopted_tokens & delta_tokens
        specificity = min(1.0, len(adopted_tokens) / 8)
        linkage = len(overlap) / max(1, min(len(adopted_tokens), len(delta_tokens)))
        scores.append(0.5 * specificity + 0.5 * linkage)

    return sum(scores) / len(scores)
```

**What the function does & why.** For each block it checks whether "Adopted elements" is meaningfully
populated (empty is an outright failure for `imports`/`baseline` types, which by definition reuse
something concrete). Where populated, it tokenizes both "Adopted elements" and "Delta → What changed"
and rewards blocks where (a) the adopted-elements text is itself specific (enough distinct tokens,
e.g. "BioFINDER-1 dataset (N=135; ... IP-MS and Simoa ...)") and (b) those tokens actually recur in the
delta description, i.e. the two fields are telling one consistent story instead of being independently
fabricated.

**Why it's hard to Goodhart.** Padding "Adopted elements" with unrelated jargon inflates specificity
but tanks the linkage term because those tokens won't reappear in "Delta → What changed" — and
vice-versa. To win this metric you have to make the two fields genuinely consistent, which is exactly
the auditable-provenance property being measured.

---

## 3. Claims-Linkage Grounding Ratio

**How it signals good science.** A related-work graph exists to let a downstream agent trace *which
claim* each external dependency actually supports or bounds. A full RW block whose "Claims affected"
is perpetually "none directly (motivation)" is an untethered citation — present in the graph but not
doing epistemic work for any specific claim. The fraction of full blocks with real claim linkage
measures how much of the citation footprint is actually load-bearing versus decorative.

**Compute function.**
```python
from collections import Counter

def claims_linkage_ratio(artifact: dict) -> float:
    """
    Assumes `artifact['full_blocks']` is a list of dicts, each with key
    'claims_affected': list[str] of claim-ID tokens (e.g. ['C01', 'C07']),
    an empty list when the block states "none directly (motivation)" or similar.
    Missing full_blocks -> 0.0.
    """
    blocks = artifact.get('full_blocks', [])
    if not blocks:
        return 0.0

    n = len(blocks)
    linked = sum(1 for b in blocks if b.get('claims_affected'))
    ratio = linked / n

    all_ids = [cid for b in blocks for cid in (b.get('claims_affected') or [])]
    if all_ids:
        distinct = len(set(all_ids))
        # if a nontrivial graph (n > 3) funnels every single linkage through
        # one repeated claim ID, that's stuffing, not per-claim grounding
        if distinct == 1 and n > 3:
            ratio *= 0.5

    return ratio
```

**What the function does & why.** It computes the plain fraction of full blocks that name at least one
real claim ID. It then checks for a degenerate pattern: if the graph has more than a handful of blocks
but every single claim-linkage points at the *same* one claim ID, that looks like a compiler (or a
paper) mechanically stamping one ID everywhere to avoid the "none" penalty rather than doing real
per-dependency attribution, so the ratio is halved.

**Why it's hard to Goodhart.** Stuffing every block with a fabricated claim ID to maximize the raw
ratio is caught by the repetition check unless the fabricator diversifies IDs — but diversifying
requires actually distributing claims plausibly across blocks, which converges toward the honest
behavior the metric wants. Fabricated links are also invisible to this metric alone but get exposed by
Metric 2 (a fabricated claim link rarely tracks a genuine Adopted/Delta connection) when the two are
read jointly.

---

## 4. Footprint Tiering Completeness

**How it signals good science.** The shape spec is explicit: a compiler that only produces full RW##
blocks with no "brief" tier failed to sweep the paper's full reference list, capturing only the closest
predecessors rather than the complete citation footprint — and an abstract-only compile (1-3 full
blocks, no brief tier) is a stark, scoreable degenerate case. Whether the artifact preserved this full
footprint (not just the "greatest hits") is itself a measure of compilation thoroughness, which is a
precondition for any of the other metrics' inputs being trustworthy.

**Compute function.**
```python
def footprint_tiering_completeness(artifact: dict) -> float:
    """
    Assumes:
      artifact['full_blocks']: list of full RW## block dicts.
      artifact['brief_refs']: list of brief-tier reference dicts (each with at
        least 'author_year' and 'role' string), possibly empty.
    Both keys defaulting to empty lists if absent -> treated as zero coverage,
    not skipped.
    """
    full_n = len(artifact.get('full_blocks', []))
    brief_n = len(artifact.get('brief_refs', []))
    total = full_n + brief_n

    if total == 0:
        return 0.0  # mandatory-core section wholly absent: worst case

    if full_n <= 3 and brief_n == 0:
        return 0.05  # matches the documented abstract-only fingerprint

    if brief_n == 0:
        return 0.15  # full blocks only: no sweep of the broader citation list

    # reward proportionate brief-tier coverage without presupposing one fixed
    # ratio (che26 vs huu25 in the shape doc show very different healthy ratios)
    brief_adequacy = min(1.0, brief_n / max(3, full_n * 0.5))
    return 0.5 + 0.5 * brief_adequacy
```

**What the function does & why.** It first handles the two documented failure fingerprints directly:
zero total references (nothing captured at all) and the "abstract-only" pattern (≤3 full blocks, no
brief tier) both score near the floor. Any nonzero full-block count with *zero* brief references also
scores low, since that means the compiler stopped after the closest predecessors. Otherwise it rewards
a brief tier that's proportionate to the full tier's size, without assuming one canonical full:brief
ratio (the spec itself shows this ratio varies a lot by paper type).

**Why it's hard to Goodhart.** Padding the brief tier with junk one-liner citations to game the ratio
is cheap on this metric alone, but each brief entry that isn't grounded in an actual reference doesn't
help (and can hurt) Metrics 1-3, which operate only on full blocks and require real technical content —
so padding the brief tier to win Metric 4 does nothing for the other three, and inflating full-block
count to avoid the "full_n <= 3" penalty forces more blocks through the concreteness/provenance/claims
gauntlet above.

---

## Combination

These four metrics are jointly hard to game because they interlock across the same underlying fields
from different angles: Metric 1 rewards concrete language in the Delta fields, but that concreteness
only pays off in Metric 2 if the same concrete tokens are echoed in "Adopted elements" — so keyword
stuffing to win Metric 1 in isolation actively fails Metric 2's consistency check. Metric 3 rewards real
per-block claim attribution, but fabricating claim IDs to win it cheaply is exposed both by its own
repetition-degeneracy check and by the fact that a fabricated claim link rarely coheres with a genuine
Adopted/Delta pairing under Metric 2. Metric 4 rewards a complete two-tier footprint, but padding either
tier to win it dilutes the average concreteness/provenance/claims-linkage scores computed over the
(now larger) full-block set — you cannot cheaply inflate coverage without also diluting quality. A
paper that wants to win all four must actually write specific, mutually-consistent, claim-linked deltas
across a complete citation sweep — which is exactly what "good related-work compilation" means.
