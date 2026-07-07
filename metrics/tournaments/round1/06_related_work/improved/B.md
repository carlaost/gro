# Proposal — `logic/related_work.md` (agent 1, improved)

## Changes from stage 1

The critique ranked this entry #2, praising **CADD**'s claim-breadth blend, **Type–Narrative
Consistency**'s use of the `Type` enum's epistemic content (the flattened-`refutes` catch), and
**Provenance Verifiability**'s grounded-source handling — but named three concrete weaknesses.
All three are fixed below; Metrics 3 and 5 are unchanged in mechanism but their prose now reflects
the new interlocks.

1. **Metric 2 (Delta Concreteness) was surface-gameable.** Counting capitalized tokens rewards
   proper-noun-shaped filler with nothing behind it. Fixed by requiring cross-field echo: a
   number or entity in `what_changed`/`why` now only earns full credit if it also appears in
   `adopted_elements` (borrowing the shape doc's own worked example, where "N=135," "p-tau
   217/181/231" show up in *both* fields). Unechoed numeric/entity tokens are heavily discounted
   (0.25x) rather than zeroed, so a block whose `why` is pure motivation prose (no reusable
   element to echo) isn't nuked for being honestly non-technical — but floating numbers that
   appear nowhere else in the block, the padding signature, no longer buy a free ride.

2. **Metric 4 (Type–Narrative Consistency) was mostly inert.** It only discriminated when the
   rare contradiction lexicon fired; the common types (`imports`, `baseline`, `extends`,
   `bounds`) all fell into an undifferentiated 0.6/0.8 middle. Fixed by adding two new checks
   that fire on the *common* cases: `imports`/`baseline` blocks are now cross-checked against
   whether `adopted_elements` actually names something concrete (an import/baseline label with
   no real adopted dependency behind it is now penalized, not ignored), and `extends`/`bounds`
   blocks are checked against generalization/limitation vocabulary in the narrative. The rare
   `refutes` check is preserved unchanged.

3. **CADD (Metric 1) breadth term was spreadable.** Scattering fabricated claim IDs one-per-block
   cheaply inflated the distinct-claims breadth term. Fixed by adding a `substantiated()` gate:
   a claim link now only counts toward density *or* breadth if the block also carries non-trivial
   delta prose (≥6 words across `what_changed`+`why`) and a non-generic `adopted_elements` entry.
   A bare `claims_affected: [C01]` tag on an otherwise-empty block no longer moves the metric at
   all — it has to be a genuinely worked block, not just a tagged one.

Everything else — the artifact shape, the hard-constraint posture (missing/empty/generic fields
are scored down, never skipped or treated as N/A), Metrics 3 and 5's mechanisms, and the overall
five-metric interlocking strategy — carries over from stage 1, with the Combination section
updated to describe the new interlocks.

---

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
    GENERIC_ADOPTED = {"none", "n/a", ""}

    def specific_claims(b):
        return [c.strip() for c in b.get("claims_affected", [])
                if c and c.strip().lower() not in GENERIC]

    def substantiated(b):
        # A claim link only counts if the block backs it with real content -- kills the
        # "tag a claim ID onto an otherwise-empty block" move that inflated stage-1 breadth.
        wc = (b.get("what_changed") or "").strip()
        wy = (b.get("why") or "").strip()
        ae = (b.get("adopted_elements") or "").strip().lower()
        has_prose = len((wc + " " + wy).split()) >= 6
        has_adopted = ae not in GENERIC_ADOPTED
        return has_prose and has_adopted

    anchored_blocks = [b for b in blocks if specific_claims(b) and substantiated(b)]
    density = len(anchored_blocks) / len(blocks)

    distinct_claims = {c for b in anchored_blocks for c in specific_claims(b)}
    breadth = min(1.0, len(distinct_claims) / max(1, len(blocks)))

    return round(0.7 * density + 0.3 * breadth, 4)
```

**What the function does & why.** Computes the fraction of full RW blocks that name at least one
concrete claim ID *and* back it with real delta prose and a non-generic adopted-elements entry,
then blends in a breadth term over only those substantiated blocks. This penalizes "no linkage
anywhere," "the same one claim rubber-stamped onto every block," and — new in this revision —
"claim IDs scattered thinly across many bare blocks to farm breadth."

**Why it's hard to Goodhart.** Stuffing a fake claim ID into every block used to be nearly free;
now it only counts if the block also carries ≥6 words of delta prose and a non-generic
`adopted_elements` entry, which drags the fabricator straight into Metric 2's cross-field echo
check and Metric 5's DOI/adopted-concreteness terms. Fabricating both the tag and the supporting
prose 15+ times without the numbers/entities ever recurring across fields, and without repeating
phrasing, is expensive — and doing it lazily is exactly what Metrics 2 and 5 catch.

---

## Metric 2 — Delta Concreteness / Cross-Field Echo Score

**How it signals good science.** Genuine engagement with prior work produces deltas with specific
technical content that *recurs* across fields — the shape doc's own example states "N=135;
MCI/prodromal AD; p-tau 217/181/231" in `adopted_elements`, and the same cohort facts implicitly
motivate the `what_changed`/`why` text. A number or named entity that shows up in the delta prose
but nowhere else in the block is a weaker signal than one that echoes into what was actually
adopted; the latter shows a real, checkable connection between "why this citation matters" and
"what was taken from it."

**Compute function.**
```python
import re
from itertools import combinations

def delta_concreteness_score(artifact):
    """
    Assumes artifact['full_blocks'] is a list of dicts with 'what_changed', 'why', and
    'adopted_elements' (str prose, possibly "" / None — empty prose must be penalized, not
    skipped).
    """
    blocks = artifact.get("full_blocks", [])
    if not blocks:
        return 0.0

    def tokenize(text):
        return set(re.findall(r"[a-z0-9]+", (text or "").lower()))

    def numeric_entity_tokens(text):
        nums = set(re.findall(r"n\s*=\s*\d+|\d+(?:\.\d+)?%|\b\d{2,}\b", (text or "").lower()))
        tokens = (text or "").split()
        caps = {t.strip(",.;:()").lower() for i, t in enumerate(tokens)
                if i > 0 and t[:1].isupper() and t.lower() not in {"the", "this", "it", "a", "an"}}
        return nums | caps

    per_block, texts = [], []
    for b in blocks:
        wc, wy = b.get("what_changed", "") or "", b.get("why", "") or ""
        ae = b.get("adopted_elements", "") or ""
        delta_text = wc + " " + wy
        candidate_tokens = numeric_entity_tokens(delta_text)
        words = max(1, len(delta_text.split()))

        if not candidate_tokens:
            per_block.append(0.0)
        else:
            ae_tokens = tokenize(ae)
            echoed = sum(1 for t in candidate_tokens if tokenize(t) & ae_tokens)
            raw_density = len(candidate_tokens) / (0.15 * words + 1)
            echo_fraction = echoed / len(candidate_tokens)
            # Unechoed numbers/entities are heavily discounted (0.25x), not zeroed, so an
            # honestly non-technical "why" (pure motivation, nothing to adopt) isn't nuked --
            # but floating numbers that appear nowhere else in the block, the padding
            # signature, no longer earn near-full credit the way raw counting did.
            per_block.append(min(1.0, raw_density * (0.25 + 0.75 * echo_fraction)))
        texts.append(delta_text)

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

**What the function does & why.** Scores each block's delta prose for quantitative/named-entity
density, but now weights that density by how much of it *echoes into* `adopted_elements` — the
same cross-field coherence idea the critique flagged as the field's single best anti-Goodhart
device — then subtracts a penalty proportional to how many block-pairs share suspiciously high
word overlap, the signature of copy-pasted templated deltas.

**Why it's hard to Goodhart.** Padding text with random numbers or capitalized filler no longer
pays off unless the fabricator *also* plants matching tokens in `adopted_elements`, which means
faking this metric now requires faking a second, independently-checked field in a mutually
consistent way — and doing that 15+ times without repeating phrasing (caught by the boilerplate
term) or drifting into claim IDs that Metric 1's `substantiated()` gate can't verify is
substantially more expensive than the stage-1 version.

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
was flattened into a softer category — the failure the doc's note about rare, often-missed
`refutes` edges warns about. But `refutes` mismatches are rare by construction; the common types
(`imports`, `baseline`, `extends`, `bounds`) deserve their own consistency checks so the metric
actually discriminates on the typical case, not just the exceptional one.

**Compute function.**
```python
def type_narrative_consistency(artifact):
    """
    Assumes artifact['full_blocks'] is a list of dicts with 'type', 'why', 'what_changed',
    'adopted_elements' (str). Missing/empty 'type' is treated as maximally inconsistent, not
    skipped.
    """
    CONTRADICTION_LEXICON = [
        "contradicts", "overturns", "in contrast", "unlike", "fails to replicate",
        "challenges", "disputes", "inconsistent with", "refutes", "undermines",
        "does not support", "no evidence for",
    ]
    GENERALIZATION_LEXICON = [
        "extends", "generalizes", "broader", "builds on", "extension of",
        "more general", "additional condition", "relaxes",
    ]
    LIMITATION_LEXICON = [
        "bounded by", "limited to", "only applies when", "constrains", "restricts",
        "under the assumption", "does not hold when", "fails outside",
        "boundary condition", "upper bound", "lower bound",
    ]

    blocks = artifact.get("full_blocks", [])
    if not blocks:
        return 0.0

    def has_concrete_adoption(b):
        ae = (b.get("adopted_elements") or "").strip().lower()
        return ae not in ("", "none", "n/a") and len(ae.split()) >= 4

    scores = []
    for b in blocks:
        t = (b.get("type") or "").strip().lower()
        if not t:
            scores.append(0.0)
            continue
        narrative = ((b.get("why") or "") + " " + (b.get("what_changed") or "")).lower()
        has_contra = any(kw in narrative for kw in CONTRADICTION_LEXICON)
        is_refutes = "refutes" in t
        is_import_baseline = ("imports" in t) or ("baseline" in t)
        is_extends_bounds = ("extends" in t) or ("bounds" in t)

        if has_contra and not is_refutes:
            scores.append(0.0)          # flattened disagreement
        elif has_contra and is_refutes:
            scores.append(1.0)          # correctly captured
        elif is_import_baseline:
            # the common case: an imports/baseline label needs a real, checkable
            # dependency behind it, not just the label itself.
            scores.append(1.0 if has_concrete_adoption(b) else 0.3)
        elif is_extends_bounds:
            has_gen = any(kw in narrative for kw in GENERALIZATION_LEXICON)
            has_lim = any(kw in narrative for kw in LIMITATION_LEXICON)
            if ("extends" in t and has_gen) or ("bounds" in t and has_lim) or (has_gen and has_lim):
                scores.append(1.0)      # type matches its own epistemic content
            else:
                scores.append(0.5)      # asserted but unsubstantiated extends/bounds claim
        elif "/" in t or "(" in t:
            scores.append(0.8)          # rewarded granularity (compound type)
        else:
            scores.append(0.6)          # plain, consistent-by-default
    return round(sum(scores) / len(scores), 4)
```

**What the function does & why.** Scans each block's narrative for contradiction language and
cross-checks it against `refutes` as before, but now also checks the two most common type
families against their own epistemic content: `imports`/`baseline` blocks must show a concrete,
non-generic `adopted_elements` entry to earn full credit, and `extends`/`bounds` blocks must show
generalization or limitation vocabulary matching their specific label. This turns the metric from
one that only fires on rare refutation edges into one that discriminates across the type
distribution most papers actually have.

**Why it's hard to Goodhart.** Mass-relabeling everything `refutes` still produces a type
distribution wildly inconsistent with the doc's genre-typical skews and clashes with
"kept/reused" adopted-elements language. The new checks close the remaining escape hatch:
mass-labeling everything `imports`/`baseline` to dodge the extends/bounds vocabulary check now
requires a genuinely concrete `adopted_elements` entry for every single block, which feeds
directly into Metric 1's `substantiated()` gate and Metric 5's adopted-concreteness term — so
gaming this metric now costs the same currency (real, specific adopted-elements prose) that two
other metrics already price.

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
limitation here). Padding `adopted_elements` with random capitalized filler to farm the
named-entity term now also has to survive Metric 2's cross-field echo check (the padded tokens
would need to *not* appear in `adopted_elements` to avoid Metric 2 catching them there too, which
is self-contradictory with the goal of farming this metric) and Metric 4's
`has_concrete_adoption` gate on `imports`/`baseline` types — so a single fabricated
`adopted_elements` string is now cross-priced by three metrics instead of one.

---

## Combination

Metrics 1 and 5 both reward linkage to something checkable *outside* the free-text prose itself — a
real claim ID or a real DOI/quantity — so prose alone (Metric 2) can't cheaply satisfy them, and
Metric 1's new `substantiated()` gate means a claim ID only counts when the block behind it is
real. Metric 2 punishes exactly the repetitive, generic padding an author would need to fabricate
at scale to inflate 1 and 5 across every block, and now specifically requires that concrete-looking
numbers/entities in the delta prose *echo* into `adopted_elements` — the same field Metrics 1, 4,
and 5 all independently price, so a fabricated `adopted_elements` string is now cross-checked by
four metrics, not one. Metric 3 is gameable by adding junk brief-tier stubs, but stubs without real
DOIs or substantive adopted-elements text drag down Metric 5's average, so the win is paid for
elsewhere. Metric 4 is gameable by mass-relabeling edges as `refutes`, but that produces a type
distribution and adopted-elements language ("kept/reused") that contradicts refutation; it is
gameable by mass-relabeling as `imports`/`baseline` instead, but that route now requires a
genuinely concrete `adopted_elements` entry on every block, which is exactly the input Metrics 1,
2, and 5 already meter. Cheap moves that inflate one metric's surface signal — more claim tags,
more DOIs, more brief stubs, more `refutes`/`imports` labels — leave a textual or structural
fingerprint (duplication, vagueness, mismatch, unverifiable IDs, unechoed numbers) that the other
four metrics are specifically built to catch, and the stage-2 revisions tighten exactly the three
seams (breadth-spreading in Metric 1, surface concreteness in Metric 2, an inert common-case check
in Metric 4) that were still loose after stage 1.
