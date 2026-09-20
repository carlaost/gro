# Proposer 4 — metrics for `logic/related_work.md`

Assumed parsed representation (shared by all compute functions below):

```python
# artifact: dict
# {
#   "full_blocks": [
#       {
#           "ref_id": "RW01",
#           "author_year": "Janelidze et al., 2023",
#           "doi": "10.1093/brain/awac333",   # or "Not specified in paper" or None
#           "type": "imports (data source)",  # raw string, may be compound: "baseline / bounds"
#           "delta_what": "head-to-head comparison of 10 plasma phospho-tau assays in prodromal AD.",
#           "delta_why": "selected as the most comprehensive head-to-head dataset for the BioFINDER-1 cohort.",
#           "claims_affected": ["C01", "C07"],   # [] or ["none"] if "none directly (motivation)"
#           "adopted_elements": "BioFINDER-1 dataset (N=135; MCI/prodromal AD; ...).",  # or "" / "none"
#       },
#       ...
#   ],
#   "brief_blocks": [
#       {"author_year": "Hansson et al., 2023", "doi": "10.1038/s41582-023-00403-3", "role": "blood biomarkers ...; motivation."},
#       ...
#   ],
# }
```

If `artifact` is missing entirely, or `full_blocks` is empty, every metric below returns its floor score
(never `None`/N/A) — per the hard constraint, absence is evidence, not a skip.

---

## Metric 1: Delta Specificity Density

**How it signals good science.** The `Delta → What changed` / `Why` prose is the only place the
compiler explains *what specific technical content* was taken from or contrasted with a prior work.
Concrete deltas (named datasets, sample sizes, effect sizes, named methods/algorithms, quantitative
comparisons) mean the compiler actually engaged with the cited paper's technical content. Generic,
templated prose ("builds on prior work in this area", "related methodology") is the fingerprint of a
compile that copied a citation list without reading deltas out of the source paper — it gives a
downstream agent nothing to verify or reuse. More specificity = more grounded provenance = better
science.

**Compute function.**

```python
import re

def delta_specificity_density(artifact: dict) -> float:
    """
    Assumes: artifact["full_blocks"] is a list of dicts with "delta_what"/"delta_why" string fields
    (possibly empty/missing). No other artifact fields are read.
    Returns a score in [0, 1]; empty/missing artifact -> 0.0 (penalized, not skipped).
    """
    blocks = artifact.get("full_blocks", []) if artifact else []
    if not blocks:
        return 0.0

    number_pat = re.compile(r"\b\d[\d.,%]*\b")                 # N=135, 10 assays, 92%, effect sizes
    named_entity_pat = re.compile(r"\b([A-Z][a-zA-Z0-9+\-]*(?:\s+[A-Z][a-zA-Z0-9+\-]*)?)\b")
    domain_noun_pat = re.compile(
        r"\b(dataset|cohort|assay|model|algorithm|benchmark|method|framework|"
        r"protocol|pipeline|corpus|library|score|metric|trial|registry)\b", re.I
    )
    generic_phrases = [
        "prior work", "related work", "builds on", "in this area", "similar approach",
        "existing literature", "previous studies", "as discussed",
    ]

    def score_block(b: dict) -> float:
        text = " ".join([b.get("delta_what") or "", b.get("delta_why") or ""]).strip()
        if not text:
            return 0.0
        s = 0.0
        if number_pat.search(text):
            s += 0.4
        if len(named_entity_pat.findall(text)) >= 1:
            s += 0.3
        if domain_noun_pat.search(text):
            s += 0.3
        low = text.lower()
        if any(p in low for p in generic_phrases) and len(text) < 80:
            s *= 0.3   # short + boilerplate -> heavily discount even if it hit other buckets
        return min(s, 1.0)

    return sum(score_block(b) for b in blocks) / len(blocks)
```

**What the function does & why.** For every full `RW##` block it scores the combined delta text on
three concrete signals — a number/quantity, a capitalized named entity (dataset/method proper noun),
and a domain noun indicating a technical artifact class — and heavily discounts short, boilerplate-only
text even if it happens to trip a keyword. The block scores are averaged into a single [0,1] density
for the artifact. Missing artifact or empty block list returns the floor (0.0).

**Why it's hard to Goodhart.** Padding deltas with numbers or named entities that don't correspond to
anything real is detectable by cross-checking against the paper text at review time (Level 2 semantic
review), and doing so convincingly for every RW block is exactly as much work as writing a real,
specific delta — there's no cheap shortcut. Simply repeating one template phrase with swapped-in numbers
across many blocks would still pass this metric alone, which is why it's paired with Metric 3 (fan-in),
which independently checks that deltas connect to distinct, real claim IDs.

---

## Metric 2: Adopted-Elements Concreteness (Reuse Traceability)

**How it signals good science.** `Adopted elements` is the field that lets a downstream agent actually
*reuse* something (a dataset, a trained model, a preprocessing step) rather than just read about it.
For `imports` and `baseline` edges especially, this field is the operational payload — if a paper claims
to import a dataset but can't say what, concretely, was adopted (cohort size, modality, version), the
"import" edge is decorative citation, not real provenance. The more concrete and specific the adopted
elements, the more the RW graph functions as an actual reuse map rather than a bibliography.

**Compute function.**

```python
def adopted_elements_concreteness(artifact: dict) -> float:
    """
    Assumes: artifact["full_blocks"] have "type" (str) and "adopted_elements" (str, possibly empty/"none").
    Only blocks whose type contains 'imports', 'baseline', or 'extends' are scored — these are the
    edge types that make an explicit reuse claim. Returns score in [0, 1]; no such blocks -> 0.0.
    """
    import re
    number_pat = re.compile(r"\b\d[\d.,%]*\b")
    domain_noun_pat = re.compile(
        r"\b(dataset|cohort|N\s*=|assay|model|checkpoint|weights|code|repository|"
        r"pipeline|hyperparameter|library|protocol|split|benchmark)\b", re.I
    )

    blocks = artifact.get("full_blocks", []) if artifact else []
    reuse_blocks = [b for b in blocks if any(
        t in (b.get("type") or "").lower() for t in ("imports", "baseline", "extends")
    )]
    if not reuse_blocks:
        return 0.0   # no reuse-claiming edges at all -> nothing to trace -> penalize

    def score_block(b: dict) -> float:
        ae = (b.get("adopted_elements") or "").strip().lower()
        if ae in ("", "none", "n/a", "not applicable"):
            return 0.0   # claims reuse-type edge but names nothing adopted -> hard fail for this block
        s = 0.1  # non-empty floor
        if number_pat.search(ae):
            s += 0.5
        if domain_noun_pat.search(ae):
            s += 0.4
        return min(s, 1.0)

    return sum(score_block(b) for b in reuse_blocks) / len(reuse_blocks)
```

**What the function does & why.** It restricts attention to edges that structurally *claim* reuse
(`imports`/`baseline`/`extends`), then scores each one's `Adopted elements` text for concrete,
checkable content (a quantity like a cohort size, a named artifact class). An edge typed as a reuse
relationship but with an empty or "none" adopted-elements field scores zero for that block — the type
label made a promise the content didn't keep, which is exactly the kind of thinness the hard constraint
requires to be penalized rather than skipped.

**Why it's hard to Goodhart.** You can't inflate this by adding more `imports`/`baseline` blocks unless
you also write concrete adopted-elements text per block — and empty/vague text is scored at or near
zero, so mass-labeling everything `imports` to look thorough (which would also wreck Metric 4's
entropy) actively drags this metric down rather than up.

---

## Metric 3: Claim Fan-in Corroboration

**How it signals good science.** The artifact's own stated purpose is to let "a downstream agent trace
provenance of data, methods, and comparator claims." That means the RW graph's real job is to *connect*
to the claims graph, not just enumerate citations. A claim whose only grounding is a single, unexamined
antecedent is weaker than one corroborated (or explicitly bounded/refuted) by multiple, differently-typed
prior works. This metric rewards claims with multi-edge, type-diverse lineage and penalizes an RW graph
that is structurally disconnected from any claim (every block says "none directly").

**Compute function.**

```python
from collections import defaultdict

def claim_fanin_corroboration(artifact: dict) -> float:
    """
    Assumes: artifact["full_blocks"] have "claims_affected" (list[str], possibly ["none"] or [])
    and "type" (str). Groups blocks by the claim IDs they touch and rewards claims backed by
    >=2 distinct RW blocks of >=2 distinct primary types. Returns score in [0, 1].
    """
    blocks = artifact.get("full_blocks", []) if artifact else []
    if not blocks:
        return 0.0

    def primary_type(t: str) -> str:
        t = (t or "").lower()
        for tok in ("imports", "bounds", "baseline", "extends", "refutes"):
            if tok in t:
                return tok
        return "unknown"

    claim_to_blocks = defaultdict(list)
    linked_block_count = 0
    for b in blocks:
        cids = [c for c in (b.get("claims_affected") or []) if c and c.lower() != "none"]
        if cids:
            linked_block_count += 1
        for c in cids:
            claim_to_blocks[c].append(primary_type(b.get("type")))

    if not claim_to_blocks:
        return 0.0   # nothing in the RW graph ties to a claim at all -> fully disconnected -> penalize

    def claim_score(types_list):
        n = len(types_list)
        diversity = len(set(types_list))
        if n == 1:
            return 0.2          # single unexamined antecedent
        base = 0.5 + 0.1 * min(n, 3)     # more corroborating edges, capped
        bonus = 0.2 if diversity >= 2 else 0.0
        return min(base + bonus, 1.0)

    per_claim = [claim_score(v) for v in claim_to_blocks.values()]
    coverage = linked_block_count / len(blocks)   # how much of the RW graph participates in claim-linking
    return (sum(per_claim) / len(per_claim)) * (0.5 + 0.5 * coverage)
```

**What the function does & why.** It inverts the usual per-citation view and groups by claim ID instead:
for each claim referenced anywhere in `Claims affected`, it counts how many RW blocks back it and how
many distinct edge types (import/bounds/baseline/extends/refutes) those blocks span, rewarding
multi-sourced, type-diverse corroboration over single-antecedent claims. It then scales the average by
`coverage` — the fraction of full RW blocks that link to *any* claim at all — so an artifact where most
blocks are stamped "none directly" (decorative citations disconnected from the argument) is penalized
even if the few linked claims look well-corroborated.

**Why it's hard to Goodhart.** Fabricating claim IDs to inflate fan-in requires those IDs to exist and
be internally consistent with the claims artifact (checkable by cross-reference at review time), and
faking type diversity per claim means writing distinct, non-templated deltas for each contributing
block — which is exactly what Metric 1 already prices in. Simply attaching every RW block to the same
one or two claim IDs to farm "coverage" produces a lopsided, obviously-degenerate claim_to_blocks
distribution rather than genuine diverse corroboration, and does nothing for Metrics 1/2/4.

---

## Metric 4: Engagement-Mode Non-Degeneracy (Type Entropy)

**How it signals good science.** The five edge types (`imports`, `bounds`, `baseline`, `extends`,
`refutes`) exist because a rigorous related-work compile distinguishes *functionally different*
relationships to prior work — "this gave us our data" is not the same epistemic move as "this bounds
what we can claim" or "this is what we benchmark against." A compile that stamps nearly every citation
with the same type (usually the laziest one, `imports`) has collapsed that distinction and is not doing
the discriminating work the schema asks for, regardless of how many blocks it has.

**Compute function.**

```python
import math
from collections import Counter

def engagement_mode_entropy(artifact: dict) -> float:
    """
    Assumes: artifact["full_blocks"] have a "type" string (possibly compound, e.g. "baseline / bounds").
    Returns normalized Shannon entropy over primary types in [0, 1]. <=1 block, or missing -> 0.0
    (a single or absent data point cannot demonstrate non-degenerate engagement, so it is penalized,
    not treated as an automatic pass for small N).
    """
    blocks = artifact.get("full_blocks", []) if artifact else []
    if len(blocks) <= 1:
        return 0.0

    canonical = ("imports", "bounds", "baseline", "extends", "refutes")

    def primary_types(t: str) -> list:
        t = (t or "").lower()
        hits = [c for c in canonical if c in t]
        return hits or ["unknown"]

    counts = Counter()
    for b in blocks:
        for pt in primary_types(b.get("type")):
            counts[pt] += 1

    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log(p) for p in probs if p > 0)
    max_entropy = math.log(min(len(canonical), max(len(counts), 2)))
    return entropy / max_entropy if max_entropy > 0 else 0.0
```

**What the function does & why.** It buckets each full RW block's type string into the canonical five
categories (a block with a compound type like `baseline / bounds` contributes to both), tallies the
distribution, and computes normalized Shannon entropy. A monoculture (everything `imports`) scores near
0; a graph that spreads meaningfully across two or more genuinely distinct roles scores higher. One or
zero blocks cannot demonstrate non-degenerate engagement by definition, so that case is floored rather
than excused.

**Why it's hard to Goodhart.** Relabeling blocks with different type tags to farm entropy without
changing anything else produces types that don't match their delta text or claim linkage — a `refutes`
edge with a delta that reads like an `imports` edge (a dataset description, no counter-finding) is
exactly the kind of mismatch a semantic reviewer or Metric 1's specificity check will surface, since
genuine `bounds`/`refutes`/`extends` deltas require different vocabulary (limitation, contradiction,
generalization) than `imports`/`baseline` deltas (dataset, comparator). Cheap relabeling to game this
metric produces text that scores poorly against Metric 1 and creates claim-type mismatches that dilute
Metric 3.

---

## Metric 5: Citation-Sweep Completeness (Full/Brief Structural Check)

**How it signals good science.** The shape's own documentation states explicitly: an artifact with
*only* full `RW##` blocks and no "brief" tier means the compiler failed to sweep the paper's full
reference list — the opposite of what looks like thoroughness (many full blocks) is actually diagnostic
of a truncated compile (e.g., abstract-only source material). A properly swept related-work graph should
show both a curated set of full-delta blocks *and* a non-trivial brief tier capturing the rest of the
citation footprint, because real papers cite far more than their closest technical predecessors.

**Compute function.**

```python
def citation_sweep_completeness(artifact: dict) -> float:
    """
    Assumes: artifact has "full_blocks" (list) and "brief_blocks" (list), both possibly empty.
    Returns score in [0, 1]. The presence of a brief tier is a near-mandatory gate: per the shape
    doc, full-blocks-only is itself evidence of an unswept reference list, not evidence of rigor.
    """
    full = artifact.get("full_blocks", []) if artifact else []
    brief = artifact.get("brief_blocks", []) if artifact else []
    n_full, n_brief = len(full), len(brief)
    total = n_full + n_brief

    if total == 0:
        return 0.0

    if n_brief == 0:
        # Full-only: per shape doc this is a specific, named failure mode (unswept reference list),
        # not "thorough but terse." Cap low regardless of how many full blocks exist; a handful of
        # full blocks with zero brief tier (abstract-only pattern) scores at the very bottom.
        return 0.15 if n_full >= 8 else 0.05

    # Both tiers present: reward footprint size (diminishing returns) and a reasonable brief share,
    # since a healthy sweep has substantially more brief refs than full ones (12 full / 19 brief and
    # 18 full / ~40 brief are the documented reference points).
    import math
    size_component = min(math.log1p(total) / math.log1p(50), 1.0)   # saturates around ~50 total refs
    brief_share = n_brief / total
    share_component = min(brief_share / 0.5, 1.0)   # reward brief share up to 50%+ of footprint
    return 0.3 + 0.7 * (0.5 * size_component + 0.5 * share_component)
```

**What the function does & why.** It first checks the structural gate called out by the shape doc: no
brief tier at all is a named failure mode, so that branch is capped low no matter how many full blocks
exist (deliberately counter-intuitive — more full blocks alone does not buy a higher score here). When
both tiers exist, it rewards a larger total citation footprint (log-scaled, saturating around the
documented ~50-reference range seen in real ARAs) and a healthy brief-to-total share, matching the
observed pattern that brief references substantially outnumber full ones in well-swept compiles.

**Why it's hard to Goodhart.** Padding the brief tier with junk one-liners to clear the gate is cheap in
isolation, but brief-tier entries contribute nothing to Metrics 1–4 (which only read `full_blocks`), so
padding brief and starving full simultaneously tanks specificity, reuse-traceability, fan-in, and
entropy. Padding the full tier instead to chase the size component reintroduces the exact vague-delta,
empty-adopted-elements, monotype problem that Metrics 1, 2, and 4 already punish.

---

## Combination

These five metrics are read from disjoint or cross-checking slices of the same graph, so a cheap move
that helps one tends to actively hurt at least one other. Mass-adding full `RW##` blocks to look
comprehensive (helps Metric 5's size component) requires either reusing generic delta language (which
craters Metric 1) or relabeling types to appear diverse without matching content (which craters Metric 4
and creates claim-type mismatches Metric 3 penalizes). Padding the brief tier to clear Metric 5's
structural gate does nothing for Metrics 1–3 since those only score full blocks, and starves the full
tier of effort. Attaching fabricated or repetitive claim IDs to farm Metric 3's fan-in requires those IDs
to be real and requires distinct, type-diverse deltas per contributing block — feeding back into Metric 1
and Metric 4's requirements rather than sidestepping them. And claiming reuse (`imports`/`baseline`/
`extends` types) without concrete adopted-elements content is free to attempt but scores zero on Metric
2 by construction, so the only way to score well across all five is to actually do the work: sweep the
full reference list, write specific and distinct deltas per edge type, name what was concretely adopted,
and wire citations into the claims they actually support.
