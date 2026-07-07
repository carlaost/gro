# M64 — Controlled-vocabulary & latent-space anchoring (expander 2)

## 1. Expanded reasoning

### What it signals
Good science is **translatable**. A claim that "p217_MS achieved P-score 0.859" is only as
independently checkable as the vocabulary it's expressed in: if `p217_MS`, the cohorts behind it, and
the ontology terms describing the disease state are anchored to canonical, externally-resolvable
identifiers (GEO/dbGaP accessions, UniProt/ChEBI/GO/HPO codes, PROSPERO registration numbers, NCT
trial IDs, DOIs, or a named/versioned latent space such as a published embedding or reference atlas),
then a downstream agent — human or machine — can *resolve* the term outside the paper's own prose and
verify it means what the paper says it means. Without anchoring, "amyloid-beta positivity" or "p-tau217"
are just strings the reader has to trust the author defined consistently with the rest of the field.
Anchoring is what turns an ARA from a self-contained narrative into a node that can be mechanically
linked into a cross-ARA knowledge graph — which is exactly why the assessment-critique flagged this as
**net-new interoperability signal**, not a restatement of internal grounding quality (that's the
`Sources`/quote-grounding discipline already covered by the ARA verifier's Rule 16 check on
`claims.md`). This metric must stay scoped to *external* namespace anchoring, not *internal*
citation-to-evidence grounding — the two are easy to conflate and collapsing them would erase the
edge that got M64 into the top 10.

### What it must reward
- Presence of **real, resolvable, contextually-matched** identifiers for the paper's load-bearing
  entities: datasets (GEO/dbGaP/SRA/ENA/ArrayExpress/PROSPERO/ClinicalTrials.gov NCT), biological/
  chemical entities (UniProt, ChEBI, GO, HPO, Cell Ontology, RRID), and — where the paper is
  computational/theoretical rather than wet-lab — named, versioned latent spaces or formal object
  systems (e.g., "UMAP embedding computed on reference atlas X v2.1", "notation follows the operator
  algebra of Y (cite)") that a reader could in principle re-derive or cross-reference.
- **Consistency of anchoring across artifacts** — the same accession/ID should appear (or be
  cross-referenced) in `data/dataset.md`, in the relevant `concepts.md` entry's `**Notation**`/
  `**Definition**`, and in `claims.md` `**Sources**` when that entity backs a load-bearing number.
  Anchoring that appears once and nowhere else the entity is used is weaker than anchoring that's
  load-bearing throughout.
- **Access-tier honesty co-occurring with anchoring** (per `11_dataset.md`'s Availability notes): an
  accession is more useful, and should score higher, when it's paired with an explicit statement of
  what part of it actually resolves to open data vs. what's gated (e.g. "GEO record is open; raw reads
  are dbGaP-controlled") — an anchor that silently overclaims openness is a defect this metric should
  catch, not just format-validate.
- **Anchoring weighted toward centrality**: terms that back an anchor claim (a claim other claims
  `**Dependencies**` on) or that appear in a claim's `**Tags**` matter more than an anchored term that's
  purely decorative background vocabulary in `concepts.md`.

### What it must NOT reward
- **ID-stuffing**: pattern-matching a string that *looks* like an accession (`GSE######`, `NCT#########`)
  is not sufficient — a syntactically valid but non-resolving or context-mismatched ID (wrong species,
  wrong disease, copy-pasted from a different paper) must score as *worse* than no ID at all, because it
  actively misleads downstream linking. This is the central Goodhart route and is why the workflow below
  requires an actual resolver call, not a regex.
- Anchoring of trivial/generic vocabulary the field already treats as common knowledge (e.g. tagging
  "control group" to a generic ontology term) while leaving the paper's actually novel/central entities
  unanchored — coverage must be weighted by whether the term is load-bearing (appears in claims/tags),
  not just counted.
- Double-crediting what the ARA verifier's grounding-discipline check (Rule 16, `Sources` quote
  requirement) already scores — this metric only fires on the *external-namespace* dimension: does the
  quoted/cited value also carry a resolvable canonical ID, not whether it's quoted-and-grounded at all.

### Failure modes / gaming routes
1. **Fabricated or malformed accessions** that pattern-match a known scheme but don't resolve →
   caught by the resolver call in step 2 of the workflow, not by format regex alone.
2. **Context-mismatched real IDs** (a real GEO accession, but for the wrong dataset/species) → caught
   by comparing the resolver's returned title/description against the ARA's stated context (semantic
   match check, step 3).
3. **Vocabulary padding**: anchoring many peripheral/generic concepts while the paper's true novel
   contribution stays unanchored → mitigated by the centrality weighting (anchored terms that are also
   referenced by claims/tags count more than isolated concepts-only anchors).
4. **Overclaiming openness**: stating an accession is "available" without the access-tier qualifier
   noted in the shape's Availability notes → explicit sub-check in the workflow, scored down.
5. **Skip-by-absence gaming**: a data-driven paper simply omitting `data/dataset.md` to dodge this
   metric entirely → explicitly forbidden by the hard constraint; see §3 penalize-don't-skip handling.

### Why it's hard to Goodhart
The score requires an [ext] round-trip: a compiler cannot satisfy this metric by writing plausible
prose alone, and cannot satisfy it by writing a plausible-looking ID alone — the ID has to actually
resolve *and* the resolved content has to semantically match the ARA's own stated context. Stuffing
more IDs without ensuring resolvability and match lowers the resolvability-rate term below (§2.4) and
therefore lowers the score. Because the check is external and adversarially cheap to fabricate against
but expensive to fake past (an LLM would need to hallucinate a genuinely resolvable, on-topic ID, which
degenerates into just... using the real one), this is a comparatively robust axis. It composes cleanly
with the rest of the suite: it does not re-score grounding-quality (internal), novelty (that's a
separate concepts-novelty indicator), or falsifiability (claims-quality indicators) — it is purely "can
this be plugged into a global vocabulary/graph," which is additive information no other metric in the
ledger captures.

## 2. Generation / compute workflow

### 2.0 Inputs (artifact fields)
- `data/dataset.md` (may be absent — see §2.3 for genre-conditioned handling), specifically:
  accession headers (`## {Accession} — ...`), `**Source / access**`, `**Key variables**`,
  `## External datasets used`, `## Included cohorts` table cells (`Source study`, `Reference standard`,
  `Platform/manufacturer`), `## Consent / ethics` (registration numbers like PROSPERO CRD#).
- `logic/concepts.md`: `**Notation**`, `**Definition**`, `**Related concepts**` per term block.
- `logic/claims.md`: `**Sources**` entries (value + file-or-section-ref + quote), `**Tags**`,
  `**Dependencies**` (to compute claim centrality / which claims are "anchor claims" other claims
  depend on).
- `PAPER.md` (light touch, only to classify genre: data-generation / data-reuse / theory-or-tool — used
  solely to set the correct denominator in §2.3, not otherwise scored here).

### 2.1 Extraction pass (deterministic, no LLM)
Scan the three files for candidate external-namespace identifiers using known schemes:

```
GEO:        GSE\d+ | GSM\d+ | GDS\d+
dbGaP:      phs\d{6}(\.v\d+\.p\d+)?
SRA/ENA:    [SED]RR\d+ | [SED]RP\d+ | PRJ[EDN][A-Z]\d+
ArrayExpr:  E-[A-Z]{4}-\d+
PROSPERO:   CRD\d{9,}
ClinTrials: NCT\d{8}
DOI:        10\.\d{4,9}/\S+
UniProt:    [OPQ][0-9][A-Z0-9]{3}[0-9] | [A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}
GO:         GO:\d{7}
HPO:        HP:\d{7}
ChEBI:      CHEBI:\d+
RRID:       RRID:[A-Za-z]+_\d+
```
Record each hit with: `{id, scheme, source_file, source_field, surrounding_context_sentence}`.
Also extract every `**Notation**` value and every `**Related concepts**` / `**Tags**` string as a
*candidate anchorable term* even when it carries no formal ID — these feed the LLM classification pass
(§2.2) so that latent-space/formalism anchoring (which has no regexable ID scheme) isn't missed.

### 2.2 [sem]/[ext] resolvability + semantic-match pass
For every extracted ID (§2.1), call the appropriate resolver:
- GEO/SRA/dbGaP/ArrayExpress → NCBI/EBI accession lookup (E-utils `esummary`, or EBI's
  identifiers.org resolver `https://identifiers.org/<scheme>:<id>`).
- Ontology codes (GO/HPO/ChEBI/UniProt) → OLS (Ontology Lookup Service) or UniProt REST lookup.
- PROSPERO → PROSPERO record lookup by CRD number.
- ClinicalTrials NCT → `mcp__claude_ai_Clinical_Trials__get_trial_details`.
- DOI → Crossref/`identifiers.org` resolution.

Each call returns `{resolved: bool, title, description}` or a 404/error → `resolved=False`.
For every `resolved=True` hit, run one semantic-match check:

> **[LLM] prompt** — "Resolver returned this record for identifier `<id>`: title=`<title>`,
> description=`<description>`. The ARA cites this identifier in the following context:
> `<surrounding_context_sentence>` (from `<source_field>` in `<source_file>`). On a 0–2 scale, does the
> resolved record's subject match the ARA's stated context for this identifier? 0 = clearly mismatched
> (wrong organism/dataset/disease/topic), 1 = partially matches (same domain, some ambiguity), 2 =
> clean match. Answer with only the integer."

Store `match_score ∈ {0,1,2}` per ID. This is the deterministic sub-score extraction point: the LLM's
free-text reasoning is discarded, only the integer is kept.

For candidate terms with **no formal ID** (from `**Notation**`/`**Related concepts**`/`**Tags**`):

> **[LLM] prompt** — "Term: `<term>`. Definition: `<definition>`. Boundary conditions:
> `<boundary_conditions>`. Classify this term into exactly one category: (A) tied to a specific named
> canonical resource, ontology, or reference dataset/latent-space that is identifiable in principle
> even though no formal ID is given in this artifact (name the resource); (B) generic/borrowed
> terminology with no controlled-vocabulary anchor available; (C) a paper-specific novel/coined term
> that is not expected to be externally anchored. Answer as `A: <resource name>` or `B` or `C`."

Category A terms without a formal ID in the artifact count as **partial anchoring** (resource
identified, but the ARA itself didn't supply the resolvable pointer — a real but lesser defect than
missing anchoring altogether, and strictly worse than a category-A term that *does* carry a formal ID
resolved in §2.1–2.2). Category C terms are excluded from the anchoring denominator entirely (novel
coinage is not a controlled-vocabulary gap — this must not be penalized, matching the shape's own
caution against genre-mismatched expectations).

### 2.3 Genre-conditioned denominator (penalize-don't-skip)
Per the hard constraint, missing `data/dataset.md` is never treated as N/A — it changes what's being
measured, not whether it's measured:

- **Data-driven genre** (paper generates or reuses a dataset; detectable via `PAPER.md` claims of N,
  cohorts, or accessions anywhere in `claims.md`/`concepts.md`) **and `data/dataset.md` absent or has
  no accession/cohort content**: this is a genre-incorrect absence. Score the dataset-anchoring
  component at its floor (0) rather than excluding it — the metric does not skip, it fails that
  component outright, dragging down the composite.
- **Theory/tool genre** (no dataset genuinely exists) **and `data/dataset.md` correctly absent**: the
  dataset-anchoring component is computed against an empty candidate set, which naturally yields a
  neutral-low rather than zero score (see `w_data` renormalization in §2.4) — this is the one case
  where absence is legitimate, but it still caps the achievable composite below what a well-anchored
  data-bearing paper could reach, since one of three anchor surfaces is structurally unavailable. This
  is the honest way to "penalize thin/missing inputs without skipping": the paper cannot be scored as if
  a surface it lacks were fully populated, but it is also not excused from being scored at all.
- **Abstract-only / thin sources** (per `11_dataset.md` Availability notes: dataset.md states only N
  with no accession, no access tier, no cohort table): treat as present-but-maximally-thin — it
  contributes hits to the extraction pass only for the bare N (no anchorable ID exists), so
  `resolvable_ids_found = 0` over a nonzero attempted-surface, which correctly floors that component
  rather than exempting it.

### 2.4 Scoring function (real Python)

```python
from dataclasses import dataclass, field
from enum import Enum

class Category(Enum):
    A_NAMED_NO_ID = "A_no_id"   # resource identified by LLM, no formal ID present
    B_GENERIC = "B"
    C_NOVEL_EXEMPT = "C"

@dataclass
class ExtractedID:
    id: str
    scheme: str
    resolved: bool
    match_score: int          # 0,1,2 ; only meaningful if resolved
    is_load_bearing: bool     # appears in claims.md Sources/Tags, or backs an anchor claim
    access_tier_honest: bool = None  # only set for dataset-scheme IDs; None if N/A

@dataclass
class UnidentifiedTerm:
    term: str
    category: Category
    is_load_bearing: bool

@dataclass
class M64Input:
    genre_is_data_driven: bool
    dataset_md_present: bool
    dataset_md_thin: bool          # abstract-only per 11_dataset.md notes
    extracted_ids: list            # list[ExtractedID]
    unidentified_terms: list       # list[UnidentifiedTerm]

def _id_score(e: ExtractedID) -> float:
    if not e.resolved:
        return -0.5 if e.is_load_bearing else -0.1   # penalize a dead/fabricated ID; worse if load-bearing
    base = e.match_score / 2.0                        # 0, 0.5, 1.0
    if e.match_score == 0:
        base = -0.3                                   # resolvable but context-mismatched: worse than absent
    weight = 1.5 if e.is_load_bearing else 1.0
    tier_bonus = 0.0
    if e.access_tier_honest is True:
        tier_bonus = 0.15
    elif e.access_tier_honest is False:
        tier_bonus = -0.25                             # overclaimed openness / collapsed access tier
    return weight * base + tier_bonus

def _term_score(t: UnidentifiedTerm) -> float:
    if t.category == Category.C_NOVEL_EXEMPT:
        return None   # excluded from denominator entirely
    weight = 1.3 if t.is_load_bearing else 1.0
    if t.category == Category.A_NAMED_NO_ID:
        return weight * 0.4     # partial credit: resource identifiable, but ARA didn't supply a pointer
    return weight * 0.0         # category B: no anchor available at all

def compute_m64(inp: M64Input) -> dict:
    id_scores = [_id_score(e) for e in inp.extracted_ids]
    term_scores = [s for t in inp.unidentified_terms if (s := _term_score(t)) is not None]
    all_scores = id_scores + term_scores

    if not all_scores:
        # No anchorable surface produced ANY candidate at all.
        # Penalize-don't-skip: this is a floor score, not N/A.
        raw = 0.0
        n = 1
    else:
        raw = sum(all_scores)
        n = len(all_scores)

    normalized = raw / n  # roughly in [-0.8, 1.65] before clamping

    # Genre-conditioned cap (2.3): theory/tool genre with correctly-absent dataset.md
    # cannot reach the same ceiling as a data-bearing paper with full anchoring, because
    # one of three anchor surfaces is structurally unavailable — not a violation, just a
    # smaller achievable maximum.
    ceiling = 1.0
    if not inp.genre_is_data_driven and not inp.dataset_md_present:
        ceiling = 0.75
    if inp.genre_is_data_driven and not inp.dataset_md_present:
        # genre-incorrect absence: hard floor regardless of concepts/claims anchoring
        normalized = min(normalized, -0.4)
    if inp.dataset_md_present and inp.dataset_md_thin:
        normalized = min(normalized, 0.2)  # abstract-only floor per Availability notes

    score = max(-1.0, min(ceiling, normalized))
    return {
        "score": round(score, 3),
        "n_ids_extracted": len(inp.extracted_ids),
        "n_ids_resolved": sum(1 for e in inp.extracted_ids if e.resolved),
        "n_terms_classified": len(inp.unidentified_terms),
        "genre_data_driven": inp.genre_is_data_driven,
        "dataset_md_present": inp.dataset_md_present,
    }
```

### 2.5 Worked shape
- huu25-style ARA (primary-data-generation): `GSE307990` extracted from `data/dataset.md`, resolved via
  GEO lookup, title/description matches "Visium spatially-resolved transcriptomics, human ERC" → 
  `match_score=2`; it's load-bearing (cited in `claims.md` C01 Sources) → high positive contribution;
  `access_tier_honest=True` because the ARA states open-metadata/dbGaP-controlled-reads split explicitly
  → `+0.15` bonus. Composite lands near ceiling.
- che26-style ARA (secondary-reuse): `PROSPERO CRD420261327845` resolves and matches → strong
  contribution; the 12 cohorts' `Source study` citations are not formal accessions but resolve as
  Category A (named published studies, LLM-identifiable resource) if no DOI is given → partial credit
  only, correctly reflecting that cohort-level anchoring here is weaker than accession-level anchoring.
- Abstract-only compilation: `dataset.md` states only "N=4,736 participants," no accession → zero
  extracted IDs, thin-floor applied (`normalized ≤ 0.2`), correctly reading as materially worse than
  either full case above without being skipped.

## 3. Composition with the suite
This metric consumes the same three artifacts several other ledger indicators touch (`claims.md`
grounding, `concepts.md` novelty/boundary-conditions quality, `dataset.md` access-tier honesty) but
scores a strictly orthogonal axis — external resolvability, not internal completeness or narrative
quality — so it adds information rather than re-weighting existing signal. It is intentionally
insensitive to prose quality and sensitive only to whether the vocabulary used is, in fact, plumbed
into the outside world.

M64 expander2: done
