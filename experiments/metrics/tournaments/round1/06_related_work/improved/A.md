# Proposer 2 — metrics for `logic/related_work.md`

## Changes from stage 1

- **Added Metric 5 — DOI Resolvability & Type-Narrative Consistency.** The critique flagged that the
  set had *no provenance-verifiability term at all* and *no use of the `Type` enum's epistemic
  content*, despite the shape doc stressing machine-followable provenance and a genre-dependent but
  meaningful `Type` field. This is a genuinely new metric, not a relabel: it scores DOI/arXiv-ID
  resolvability per block (with an explicit, non-zero-but-discounted score for the documented
  `"Not specified in paper"` sentinel, distinct from a blank field) and a type-narrative check
  generalized across *all five* `Type` values — not just the rare `refutes` case agent1 flagged, but
  also `imports`/`baseline` (must show real adopted elements) and `extends`/`bounds` (must show
  generalization/limitation language) — so it discriminates on the common cases, addressing the same
  weakness the critique separately identified in agent1's narrower version of this idea.
- **Generalized Metric 3's degeneracy guard.** The old check only fired on `distinct == 1`; a gamer
  spreading fabricated links across two IDs escaped entirely. Replaced the binary halving with an
  entropy-and-richness diversity term computed over the full claim-ID distribution, which scales
  smoothly and specifically penalizes "few distinct IDs smeared across many blocks" regardless of
  whether that count is one, two, or three.
- **Hardened Metric 2 against terse-but-real blocks.** Bare token-set overlap under-scored a
  genuinely specific but short `adopted_elements` field (e.g., a five-token dataset citation with an
  `N=` and an assay acronym) as if it were thin. Added light stemming/normalization to the tokenizer
  so trivial morphological variants (`assay`/`assays`, `compare`/`compared`) count as matches, plus a
  concrete-marker specificity floor so honest brevity backed by a real number/acronym/hyphenated term
  isn't penalized the way padding-free emptiness is.
- **Updated the Combination section** to explain how Metric 5 closes against the other four rather
  than sitting outside the interlock, and to be candid about DOI-verification's scope (syntactic/
  sentinel-based, not network resolution) the way the field's more careful entries were.

---

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
    STRONG_MARKERS = [   # same "this text is concrete" signal as Metric 1
        r'\bN\s*=\s*\d+', r'\d+(\.\d+)?\s*%', r'\bp\s*[<=]\s*0?\.\d+',
        r'\b[A-Za-z][A-Za-z0-9]*[-/][A-Za-z0-9]+\b', r'\b[A-Z]{2,}\b',
    ]

    def normalize(w):
        w = w.lower()
        # light stemming: collapse simple plural/verb-suffix variants so
        # "assay"/"assays", "compare"/"compared" don't count as non-overlap
        for suffix in ('ies', 'ing', 'ed', 's'):
            if w.endswith(suffix) and len(w) - len(suffix) >= 3:
                return w[: -len(suffix)]
        return w

    def tokenize(s):
        return set(normalize(w) for w in re.findall(r'[A-Za-z][A-Za-z0-9\-]{2,}', s or ''))

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

        # specificity: token count, OR a floor for text that is terse but
        # carries a strong concrete marker (a dataset N=, an assay acronym, a
        # hyphenated technical token). Honest brevity backed by a real
        # marker shouldn't be scored like padding-free emptiness just
        # because the field is short.
        token_specificity = min(1.0, len(adopted_tokens) / 8)
        has_strong_marker = any(re.search(p, adopted) for p in STRONG_MARKERS)
        specificity = max(token_specificity, 0.6 if has_strong_marker else 0.0)

        linkage = len(overlap) / max(1, min(len(adopted_tokens), len(delta_tokens)))
        scores.append(0.5 * specificity + 0.5 * linkage)

    return sum(scores) / len(scores)
```

**What the function does & why.** For each block it checks whether "Adopted elements" is meaningfully
populated (empty is an outright failure for `imports`/`baseline` types, which by definition reuse
something concrete). Where populated, it tokenizes both fields with light stemming so trivial
morphological drift isn't mistaken for a broken provenance chain, and rewards blocks where (a) the
adopted-elements text is itself specific — either by raw token count or, for terse-but-real entries, by
carrying a concrete marker like `N=135` or an assay acronym — and (b) those tokens actually recur in
the delta description, i.e. the two fields are telling one consistent story instead of being
independently fabricated.

**Why it's hard to Goodhart.** Padding "Adopted elements" with unrelated jargon inflates specificity
but tanks the linkage term because those tokens won't reappear in "Delta → What changed" — and
vice-versa. The specificity floor only activates on genuine concrete markers (numbers, acronyms,
hyphenated technical tokens), so it can't be gamed by adding filler words to pad token count past 8;
you either have a real marker or you don't. To win this metric you have to make the two fields
genuinely consistent, which is exactly the auditable-provenance property being measured.

---

## 3. Claims-Linkage Grounding Ratio

**How it signals good science.** A related-work graph exists to let a downstream agent trace *which
claim* each external dependency actually supports or bounds. A full RW block whose "Claims affected"
is perpetually "none directly (motivation)" is an untethered citation — present in the graph but not
doing epistemic work for any specific claim. The fraction of full blocks with real claim linkage
measures how much of the citation footprint is actually load-bearing versus decorative — and the
*shape* of that linkage (spread across genuinely distinct claims vs. funneled through a small clique of
IDs) tells you whether the attribution is real per-dependency work or a shortcut to avoid the "none"
penalty.

**Compute function.**
```python
import math
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
    linked_blocks = [b for b in blocks if b.get('claims_affected')]
    linked = len(linked_blocks)
    ratio = linked / n
    if linked == 0:
        return 0.0

    all_ids = [cid for b in linked_blocks for cid in (b.get('claims_affected') or [])]
    counts = Counter(all_ids)
    distinct = len(counts)
    total = len(all_ids)

    if n <= 3:
        # too few blocks to judge a distribution shape -- the plain ratio stands
        return ratio

    # Evenness: Shannon entropy of the claim-ID distribution, normalized so a
    # single ID stamped everywhere scores 0 and a spread-out distribution
    # scores near 1.
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs) if distinct > 1 else 0.0
    max_entropy = math.log2(max(2, distinct))
    evenness = entropy / max_entropy if max_entropy > 0 else 0.0

    # Richness: are distinct claim IDs keeping pace with how many blocks
    # claim a linkage at all, or is a small clique of IDs (one, two, three...)
    # being smeared across every linked block regardless of block count?
    richness = min(1.0, distinct / max(1, linked))

    diversity = 0.5 * evenness + 0.5 * richness
    return ratio * (0.5 + 0.5 * diversity)
```

**What the function does & why.** It computes the plain fraction of full blocks that name at least one
real claim ID, then discounts that ratio by a diversity term over the full claim-ID distribution:
evenness (entropy-based — is one ID dominating?) and richness (does the number of distinct IDs scale
with how many blocks claim a linkage, or is it stuck at a small constant?). A graph where every block
points at the same claim, or where two IDs are smeared across ten blocks, gets a materially discounted
ratio; a graph where distinct claims scale with linked blocks keeps close to the raw ratio.

**Why it's hard to Goodhart.** The old binary "only penalize if `distinct == 1`" guard let a gamer
escape by fabricating two or three IDs instead of one. The entropy+richness formulation closes that
gap smoothly: richness alone catches "few IDs, many blocks" regardless of the exact distinct count, and
evenness catches "many IDs but one dominant one." Diversifying enough to satisfy both terms converges
toward the honest behavior the metric wants — real, varied, per-dependency attribution — rather than
toward finding the smallest number of distinct labels that dodges a single threshold. Fabricated links
are also invisible to this metric alone but get exposed by Metric 2 (a fabricated claim link rarely
tracks a genuine Adopted/Delta connection) when the two are read jointly.

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

## 5. DOI Resolvability & Type-Narrative Consistency Score

**How it signals good science.** Two first-class fields in the shape spec carry real epistemic content
that Metrics 1-4 never touch. First, `**DOI**` exists precisely so a downstream agent can *follow*
provenance mechanically instead of trusting prose — the shape doc's own example fields distinguish a
resolvable identifier from the honest sentinel `"Not specified in paper"`; a genuinely missing field is
a different (worse) failure than a documented absence. Second, `**Type**` is not decoration: the spec
documents that `refutes` edges should appear when a source explicitly contradicts prior work, that
`imports`/`baseline` types definitionally reuse something concrete, and that `extends`/`bounds` types
describe a generalization or a limiting scope. A compiler that flattens a paper's actual disagreement
with prior work into a bland `baseline` label, or slaps `extends` on a block with no generalization
language anywhere in it, has degraded the graph's typed structure into an untyped one wearing labels.

**Compute function.**
```python
import re

def doi_and_type_narrative_score(artifact: dict) -> float:
    """
    Assumes `artifact['full_blocks']` is a list of dicts, each with string keys:
      'doi'   -- DOI/arXiv string, OR the literal shape-spec sentinel
                 "Not specified in paper", OR '' if the field was simply never
                 populated (a real compiler defect, distinct from the sentinel).
      'type'  -- e.g. 'imports (data source)', 'baseline / bounds', 'refutes'.
      'delta_what', 'delta_why', 'adopted_elements' -- prose fields.
    Missing full_blocks -> 0.0.
    """
    blocks = artifact.get('full_blocks', [])
    if not blocks:
        return 0.0

    DOI_RE = re.compile(r'^10\.\d{4,9}/\S+$')
    ARXIV_RE = re.compile(r'^(arxiv:)?\d{4}\.\d{4,5}(v\d+)?$', re.I)
    SENTINEL = 'not specified in paper'

    CONTRADICTION = [
        r'\bcontradicts?\b', r'\boverturns?\b', r'\bconflicts? with\b',
        r'\bno evidence (for|of)\b', r'\bfails? to replicate\b',
        r'\bin contrast to\b', r'\bdisputes?\b', r'\brefutes?\b',
    ]
    GENERALIZATION = [
        r'\bgeneraliz\w*\b', r'\bextends? to\b', r'\bbroaden\w*\b',
        r'\bunder the assumption\b', r'\brestrict\w* to\b',
        r'\bboundary condition\b', r'\bdoes not hold\b', r'\bonly (holds|applies)\b',
    ]
    EMPTY_MARKERS = {'', 'n/a', 'none', 'not specified', 'not applicable'}

    def doi_score(doi):
        d = (doi or '').strip()
        if d.lower() == SENTINEL:
            return 0.5   # honestly disclosed real-world absence: still unresolvable,
                         # but not the same failure as an unfilled field
        if DOI_RE.match(d) or ARXIV_RE.match(d):
            return 1.0
        return 0.0        # blank, malformed, or placeholder -- a real provenance gap

    def has_any(patterns, text):
        return any(re.search(p, text or '', re.I) for p in patterns)

    def type_score(btype, delta_text, adopted):
        t = (btype or '').lower()
        roles = set(re.findall(r'imports|bounds|baseline|extends|refutes', t))
        if not roles:
            return 0.7   # unrecognized/compound label we can't parse: neutral, not a free pass

        role_scores = []
        for role in roles:
            if role == 'refutes':
                role_scores.append(1.0 if has_any(CONTRADICTION, delta_text) else 0.2)
            elif role in ('imports', 'baseline'):
                thin = (adopted or '').strip().lower() in EMPTY_MARKERS
                role_scores.append(0.2 if thin else 1.0)
            else:  # extends, bounds
                role_scores.append(1.0 if has_any(GENERALIZATION, delta_text) else 0.5)
        # a compound type (e.g. "baseline / bounds") only needs to substantiate
        # one of its declared roles to avoid double-punishing a legitimate blend
        return max(role_scores)

    scores = []
    for b in blocks:
        delta_text = f"{b.get('delta_what','')} {b.get('delta_why','')}"
        d_score = doi_score(b.get('doi'))
        t_score = type_score(b.get('type'), delta_text, b.get('adopted_elements'))
        scores.append(0.5 * d_score + 0.5 * t_score)

    return sum(scores) / len(scores)
```

**What the function does & why.** Each block gets a DOI sub-score that distinguishes a resolvable
identifier (full credit), the documented `"Not specified in paper"` sentinel (partial credit — honest
but unfollowable), and a genuinely blank/malformed field (zero — a real compiler defect, never
silently skipped). It also gets a type-narrative sub-score that checks the `Type` label against the
block's own prose: `refutes` needs contradiction language or it's an unsubstantiated escalation;
`imports`/`baseline` need real adopted elements or the "reuse" implied by the label didn't happen;
`extends`/`bounds` need generalization/limitation language or the scope claim implied by the label is
undemonstrated. This deliberately covers all five `Type` values, not only the rare `refutes` edge, so
it discriminates on the common cases most blocks will actually exercise.

**Why it's hard to Goodhart.** Full DOI *resolution* (an actual network lookup) is out of scope for a
function scoring a static artifact — this metric only checks syntactic conformance to a DOI/arXiv
pattern or the honest sentinel, so a fabricated but well-formed DOI string is a blind spot for this
metric in isolation. But a compiler fabricating DOIs wholesale gains nothing on Metrics 1-4, which read
entirely different fields — you cannot win this metric by inventing identifiers without also having to
separately fake concrete deltas, real provenance overlap, and genuine claim linkage. The type-narrative
half is harder to cheat than it looks: mass-relabeling everything to `extends`/`bounds` to dodge the
`imports`/`baseline` reuse check just shifts the burden to needing generalization language in every
delta, which itself has to stay consistent with Metric 1's concreteness signal and Metric 2's
Adopted↔Delta echo — so gaming one role's check tends to break another block's requirement rather than
sliding the whole set into a lenient corner.

---

## Combination

These five metrics are jointly hard to game because they interlock across the same underlying fields
from different angles. Metric 1 rewards concrete language in the Delta fields, but that concreteness
only pays off in Metric 2 if the same concrete tokens are echoed in "Adopted elements" — so keyword
stuffing to win Metric 1 in isolation actively fails Metric 2's consistency check. Metric 3 rewards real
per-block claim attribution with a smooth diversity penalty (entropy + richness) that closes the escape
hatch a binary degeneracy check left open, and fabricating claim IDs to win it cheaply is exposed both
by that diversity term and by the fact that a fabricated claim link rarely coheres with a genuine
Adopted/Delta pairing under Metric 2. Metric 4 rewards a complete two-tier footprint, but padding either
tier to win it dilutes the average concreteness/provenance/claims-linkage scores computed over the
(now larger) full-block set — you cannot cheaply inflate coverage without also diluting quality. Metric
5 adds the two fields the first four never touch — DOI verifiability and the `Type` label's narrative
truthfulness — and it interlocks the same way: a block cannot win the `imports`/`baseline` half of
Metric 5 without real adopted elements, which is exactly what Metric 2 also demands of that same field;
it cannot win the `extends`/`bounds` half without generalization language that has to coexist with
Metric 1's concreteness requirement on the same Delta text; and fabricating DOIs to inflate its other
half buys nothing on Metrics 1-4, which never read the DOI field at all. A paper that wants to win all
five must actually write specific, mutually-consistent, claim-linked, honestly-typed, and
provenance-verifiable deltas across a complete citation sweep — which is exactly what "good
related-work compilation" means.
