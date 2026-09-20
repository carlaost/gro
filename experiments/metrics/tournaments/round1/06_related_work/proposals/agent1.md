# Proposal — `logic/related_work.md` (agent 1)

Assumed parsed representation (stated once, reused across all compute functions):

```python
artifact = {
    "full_blocks": [
        {
            "id": "RW01",                       # str
            "doi": "10.1093/brain/awac333",      # str, or "Not specified in paper"
            "type": "imports (data source)",     # str, enum + optional compound qualifier
            "what_changed": "...",               # str prose, may be "" / missing
            "why": "...",                        # str prose, may be "" / missing
            "claims_affected": ["C01", "C07"],   # list[str], [] if "none"/absent
            "adopted_elements": "...",           # str prose, may be "" / "none"
        },
        # ...
    ],
    "brief_refs": [
        {"author_year": "...", "doi": "...", "role": "..."},
        # ...
    ],
    "grounded_sources": [
        {"id": "...", "registration_number": "...", ...},  # non-bibliographic special case
        # ...
    ],
}
```

Any field that is missing, empty, or a generic placeholder ("none", "Not specified in paper",
"none directly (motivation)") is treated as present-but-thin and scored down — never skipped.

---

## Metric 1 — Claim-Anchored Delta Density (CADD)

**How it signals good science.** A related-work graph that ties each dependency to the specific
claim(s) it substantiates, bounds, or motivates shows the author traced *provenance of their own
conclusions*, not just assembled a reading list. High rates of "none directly (motivation)" or
missing claim links — especially concentrated on one or two claims while everything else is
unlinked — signal citation padding rather than argumentative rigor.

**Compute function.**
```python
def claim_anchored_delta_density(artifact):
    """
    Assumes artifact['full_blocks'] is a list of dicts, each with 'claims_affected': list[str]
    (empty list if the field was "none"/absent — missing linkage, not missing data, must be
    penalized per the hard constraint).
    """
    blocks = artifact.get("full_blocks", [])
    if not blocks:
        return 0.0  # no full blocks at all -> cannot anchor anything -> worst score

    GENERIC = {"none", "n/a", "none directly (motivation)"}

    def specific_claims(b):
        return [c.strip() for c in b.get("claims_affected", [])
                if c and c.strip().lower() not in GENERIC]

    anchored = sum(1 for b in blocks if specific_claims(b))
    density = anchored / len(blocks)

    distinct_claims = {c for b in blocks for c in specific_claims(b)}
    breadth = min(1.0, len(distinct_claims) / max(1, len(blocks)))

    return round(0.7 * density + 0.3 * breadth, 4)
```

**What the function does & why.** Computes the fraction of full RW blocks that name at least one
concrete claim ID, then blends in a breadth term measuring how many *distinct* claims are touched
relative to block count. This penalizes both "no linkage anywhere" and "the same one claim
rubber-stamped onto every block."

**Why it's hard to Goodhart.** Stuffing a fake claim ID into every block is cheap in isolation, but
fabricated linkage rarely coexists with genuinely specific, non-duplicated delta prose or precise
adopted-elements text — see Metrics 2 and 5, which independently penalize the vagueness/duplication
that fabricated linkage tends to travel with.

---

## Metric 2 — Delta Concreteness / Anti-Boilerplate Score

**How it signals good science.** Genuine engagement with prior work produces deltas with specific
technical content — named methods, datasets, quantities, versions (the shape doc's own example:
"N=135; MCI/prodromal AD; p-tau 217/181/231"). Templated or rushed compilation produces generic
prose that reads nearly the same across many unrelated citations. Rewarding specificity and
penalizing cross-block near-duplication favors real per-citation analysis over filler.

**Compute function.**
```python
import re
from itertools import combinations

def delta_concreteness_score(artifact):
    """
    Assumes artifact['full_blocks'] is a list of dicts with 'what_changed' and 'why' (str prose,
    possibly "" / None — empty prose must be penalized, not skipped).
    """
    blocks = artifact.get("full_blocks", [])
    if not blocks:
        return 0.0

    def concreteness(text):
        if not text or not text.strip():
            return 0.0
        numeric_hits = len(re.findall(r"\bN\s*=\s*\d+|\d+%|\b\d{2,}\b", text))
        tokens = text.split()
        cap_hits = sum(1 for i, t in enumerate(tokens)
                       if i > 0 and t[:1].isupper()
                       and t.lower() not in {"the", "this", "it", "a", "an"})
        words = max(1, len(tokens))
        return min(1.0, (numeric_hits * 2 + cap_hits) / (0.15 * words + 1))

    per_block, texts = [], []
    for b in blocks:
        wc, wy = b.get("what_changed", "") or "", b.get("why", "") or ""
        per_block.append((concreteness(wc) + concreteness(wy)) / 2)
        texts.append(wc + " " + wy)

    mean_concreteness = sum(per_block) / len(per_block)

    def jaccard(a, b):
        sa, sb = set(a.lower().split()), set(b.lower().split())
        if not sa or not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    if len(texts) > 1:
        pairs = list(combinations(texts, 2))
        overlaps = [jaccard(a, b) for a, b in pairs]
        boilerplate_penalty = sum(o for o in overlaps if o > 0.6) / len(pairs)
    else:
        boilerplate_penalty = 0.0

    return round(max(0.0, mean_concreteness - boilerplate_penalty), 4)
```

**What the function does & why.** Scores each block's "what changed"/"why" text for quantitative
and named-entity density (numbers, N=, proper-noun-like tokens), length-normalized, then subtracts
a penalty proportional to how many block-pairs share suspiciously high word overlap — the signature
of copy-pasted templated deltas across distinct citations.

**Why it's hard to Goodhart.** Padding text with random numbers or capitalized filler words raises
the raw concreteness score but is a shallow, detectable move: doing this distinctively 15+ times
without repeating phrasing is expensive, and doing it lazily (reusing the same padded phrase) is
exactly what the boilerplate-overlap term catches.

---

## Metric 3 — Citation-Footprint Completeness

**How it signals good science.** The shape doc is explicit that a compiler must "reflect the
paper's full citation footprint, not just the closest predecessors," and calls out two concrete
thinness signals: full blocks with no "brief" tier at all, and abstract-only sources with only 1–3
total RW blocks. Rewarding total footprint size plus presence of a genuine brief tier operationalizes
exactly this completeness requirement.

**Compute function.**
```python
def citation_footprint_completeness(artifact):
    """
    Assumes artifact['full_blocks'] and artifact['brief_refs'] are lists (possibly empty).
    Both empty -> no citation footprint at all -> maximal penalty, not "N/A".
    """
    n_full = len(artifact.get("full_blocks", []))
    n_brief = len(artifact.get("brief_refs", []))
    total = n_full + n_brief
    if total == 0:
        return 0.0

    size_score = min(1.0, total / 15.0)  # ~15 full blocks = doc's own "full-text compile" benchmark

    if n_brief == 0:
        brief_score = 0.0
    else:
        brief_score = min(1.0, (n_brief / total) / 0.10)

    # extra penalty: several full blocks but zero brief tier is the doc's named
    # "didn't sweep the full reference list" failure, distinct from just being thin
    coverage_sweep_penalty = 0.4 if (n_full >= 5 and n_brief == 0) else 0.0

    score = 0.5 * size_score + 0.5 * brief_score - coverage_sweep_penalty
    return round(max(0.0, min(1.0, score)), 4)
```

**What the function does & why.** Combines raw footprint size (capped near the doc's own 15-block
full-text-compile reference point) with the *share* of that footprint sitting in the brief tier, and
applies an additional penalty specifically when full blocks exist in reasonable numbers but the
brief tier is entirely absent — the named "swept only closest predecessors" failure mode.

**Why it's hard to Goodhart.** Padding with many junk one-line brief-tier stubs inflates this metric
cheaply, but junk stubs (no real DOI, generic "role" text) directly drag down Metric 5's
DOI-resolution term, so the gain here is paid for elsewhere.

---

## Metric 4 — Type–Narrative Consistency

**How it signals good science.** The `Type` enum is a compressed epistemic claim about a citation's
relationship to the paper. When the free-text `why`/`what_changed` narrative uses contradiction
language ("contradicts," "overturns," "in contrast," "fails to replicate") but the block is typed
as something anodyne like `baseline` or `imports`, that is evidence a real scientific disagreement
was flattened into a softer category — exactly the failure the doc's note about rare, often-missed
`refutes` edges warns about. Correct labeling, and finer compound labeling (`baseline / bounds`),
should be rewarded.

**Compute function.**
```python
def type_narrative_consistency(artifact):
    """
    Assumes artifact['full_blocks'] is a list of dicts with 'type', 'why', 'what_changed' (str).
    Missing/empty 'type' is treated as maximally inconsistent, not skipped.
    """
    CONTRADICTION_LEXICON = [
        "contradicts", "overturns", "in contrast", "unlike", "fails to replicate",
        "challenges", "disputes", "inconsistent with", "refutes", "undermines",
        "does not support", "no evidence for",
    ]
    blocks = artifact.get("full_blocks", [])
    if not blocks:
        return 0.0

    scores = []
    for b in blocks:
        t = (b.get("type") or "").strip().lower()
        if not t:
            scores.append(0.0)
            continue
        narrative = ((b.get("why") or "") + " " + (b.get("what_changed") or "")).lower()
        has_contra = any(kw in narrative for kw in CONTRADICTION_LEXICON)
        is_refutes = "refutes" in t

        if has_contra and not is_refutes:
            scores.append(0.0)      # flattened disagreement
        elif has_contra and is_refutes:
            scores.append(1.0)      # correctly captured
        elif "/" in t or "(" in t:
            scores.append(0.8)      # rewarded granularity (compound type)
        else:
            scores.append(0.6)      # plain, consistent-by-default
    return round(sum(scores) / len(scores), 4)
```

**What the function does & why.** Scans each block's narrative for contradiction language and
cross-checks it against whether the `Type` field actually reads `refutes`; mismatches score zero,
correct matches score highest, and compound type annotations (finer epistemic resolution) get
partial credit even without contradiction language present.

**Why it's hard to Goodhart.** Mass-relabeling everything `refutes` to chase the match bonus would
produce a type distribution wildly inconsistent with the doc's own genre-typical skews (applied-ML
papers skew `baseline`, theory papers skew `extends`/`bounds`, and `refutes` is stated to be rare) —
and it would also clash with `adopted_elements` text describing things as "kept/reused," which
implies import/extension, not refutation.

---

## Metric 5 — Provenance Verifiability

**How it signals good science.** DOIs and precisely stated `adopted_elements` are what let a
downstream agent independently verify and actually reuse what was borrowed — the doc's own worked
example gives an exact N and named assays. Broadly unresolved DOIs ("Not specified in paper") or
vague adopted-elements prose make the dependency claim unverifiable, a transparency failure, not
a stylistic one. Correctly folding in a non-bibliographic grounded source (e.g., a trial
registration) when present is a bonus for not hiding a real dependency behind a purely
bibliographic lens.

**Compute function.**
```python
import re

def provenance_verifiability(artifact):
    """
    Assumes artifact['full_blocks'] items have 'doi' (str, or "Not specified in paper") and
    'adopted_elements' (str prose, possibly "" / "none"). artifact.get('grounded_sources', [])
    is a list that may legitimately be empty; only malformed *entries* are penalized directly,
    since we have no external signal here that a grounded source was actually expected.
    """
    blocks = artifact.get("full_blocks", [])
    if not blocks:
        return 0.0

    def doi_present(doi):
        return bool(doi) and doi.strip().lower() != "not specified in paper"

    doi_rate = sum(1 for b in blocks if doi_present(b.get("doi", ""))) / len(blocks)

    def adopted_concreteness(text):
        if not text or text.strip().lower() in ("none", "n/a", ""):
            return 0.0
        quant = len(re.findall(r"\bN\s*=\s*\d+|\d+(?:\.\d+)?%|\b\d{2,}\b", text))
        named = len(re.findall(r"[A-Z][a-zA-Z0-9\-]{2,}", text))
        return min(1.0, (quant * 2 + named) / 6.0)

    adopted_score = sum(adopted_concreteness(b.get("adopted_elements", "")) for b in blocks) / len(blocks)

    grounded = artifact.get("grounded_sources", [])
    grounded_bonus = 0.0
    if grounded:
        well_formed = sum(1 for g in grounded if g.get("id") or g.get("registration_number"))
        grounded_bonus = 0.1 * (well_formed / len(grounded))

    return round(min(1.0, 0.5 * doi_rate + 0.4 * adopted_score + grounded_bonus), 4)
```

**What the function does & why.** Blends the fraction of full-tier citations carrying a real,
resolvable DOI with the quantitative/named-entity concreteness of the `adopted_elements` prose, plus
a small bonus for well-formed non-bibliographic grounded sources — together approximating how
independently checkable and reusable the paper's stated dependencies actually are.

**Why it's hard to Goodhart.** Fabricated-looking DOIs are externally falsifiable (a downstream
verifier can attempt resolution against Crossref/arXiv, outside this function's scope but a stated
limitation here); and padding `adopted_elements` with random capitalized filler to farm the
named-entity term reuses the same trick Metric 2 already penalizes when phrasing repeats across
blocks, and tends to produce adopted-elements text that traces to no real claim, which drags down
Metric 1.

---

## Combination

Metrics 1 and 5 both reward linkage to something checkable *outside* the free-text prose itself — a
real claim ID or a real DOI/quantity — so prose alone (Metric 2) can't cheaply satisfy them. Metric
2 in turn punishes exactly the repetitive, generic padding an author would need to fabricate at
scale to inflate 1 and 5 across every block: writing 15+ distinctively concrete-sounding fake
deltas is expensive, writing them lazily (reused phrasing) is what the overlap penalty catches.
Metric 3 is gameable by adding junk brief-tier stubs, but stubs without real DOIs or substantive
adopted-elements text drag down Metric 5's average, so the win is paid for elsewhere. Metric 4 is
gameable by mass-relabeling edges as `refutes`, but that produces a type distribution and
adopted-elements language ("kept/reused") that contradicts refutation — a mismatch Metric 4 itself
is built to catch, and one that clashes with the genre-typical type skew the shape doc documents.
Cheap moves that inflate one metric's surface signal — more claim tags, more DOIs, more brief
stubs, more `refutes` labels — leave a textual or structural fingerprint (duplication, vagueness,
mismatch, unverifiable IDs) that the other four metrics are specifically built to catch.
