# M64 — Controlled-vocabulary & latent-space anchoring (expander 4)

## 1. Expanded reasoning

### What this indicator is actually claiming
An ARA's `data/dataset.md` (cross-referenced against `logic/claims.md` and
`logic/concepts.md`) contains a set of *named entities*: genes, cell types, diseases, drugs,
instruments, cohort/accession identifiers, variable names, spatial domains, and so on. Good
science, in the sense this metric targets, is not merely that the data exist — it's that the
data are described using terms that **resolve outside the paper's own vocabulary**: to a
controlled ontology (HGNC, MONDO, HPO, UBERON, ChEBI, LOINC, SNOMED-CT, Cell Ontology), to a
canonical accession/dataset registry (GEO, dbGaP, SRA, ENA, PRIDE, PROSPERO, ClinicalTrials.gov),
or to a named, versioned latent space / embedding / reference atlas (e.g. a specific scRNA-seq
reference atlas build, a specific pretrained embedding model + checkpoint). Anchoring is what
makes an ARA's data **translatable and referenceable** by another agent or another ARA without
that agent having to re-derive the paper's private naming conventions from prose.

This is explicitly a *cross-ARA interoperability* signal, not a data-quality or reproducibility
signal per se (those are covered elsewhere — access-tier honesty, accession presence, etc., live
in other metrics per §11's own scoring axes). M64's unique surface is: **can a downstream agent
take a term out of this artifact and look it up / align it / merge it with another ARA's terms
without ambiguity?**

### What it must reward
- Explicit ontology-ID or accession-ID co-occurrence with a natural-language term — not just the
  term alone. E.g. "APOE ε4" is a name; "APOE (HGNC:613), rs429358/rs7412 ε4 haplotype" is
  anchored. "GSE307990" is an accession anchor for the dataset itself.
- Versioned/named latent spaces: "SpaceRanger v2.1.0 (GRCh38, 2020-A)" anchors the coordinate
  system the spatial data live in; a stated reference genome build, a stated embedding model
  name+checkpoint, a stated cell-type reference atlas (e.g. "Allen Brain Atlas M1 taxonomy v3")
  are all latent-space anchors even when no formal ontology ID exists.
- Registry-level anchors for the *dataset as a whole*, not just its variables: GEO/dbGaP/SRA/ENA
  accessions, PROSPERO registration numbers, ClinicalTrials.gov NCT IDs — these make the dataset
  itself referenceable, which is a distinct and stackable win on top of variable-level anchoring.
- Consistent anchoring across the ARA — the same entity should resolve to the same ID everywhere
  it appears (dataset.md, claims.md, concepts.md). Reward internal consistency, not just presence.

### What it must NOT reward
- Cosmetic name-dropping of a standard's *name* without an actual resolvable identifier ("we use
  standard gene nomenclature" with zero HGNC IDs anywhere is not anchoring — it's a claim of
  anchoring).
- Anchoring only the trivial/easy terms (e.g. species name, "Homo sapiens") while leaving the
  paper's actual key variables (disease subtypes, custom cell-type labels, custom risk scores)
  completely un-anchored. The score must be entity-coverage-weighted, not presence-weighted.
- Over-rewarding sheer volume of anchors — a paper that anchors 40 trivial terms and 0 load-bearing
  ones should not outscore one that anchors 5 load-bearing ones precisely. Weight by whether the
  anchored term is one of the paper's *own key variables* (per the `dataset.md` "Key variables"
  field or `concepts.md`) vs. incidental background vocabulary.
- Penalizing genre-mismatched expectations: a pure theory/tool paper with no `data/` directory is
  not a controlled-vocabulary failure — see §4 (availability) below. Do not force ontology-lookup
  behavior onto artifacts that structurally cannot have it.

### Failure modes / gaming routes
1. **ID-stuffing**: pasting a block of unrelated ontology IDs (e.g. a copy-pasted MeSH term list)
   that don't correspond 1:1 to terms actually used in the paper's variables/claims, to inflate a
   naive "count of IDs present" score. Countered by requiring each anchor to be *co-located* with
   the term it anchors (same sentence/bullet) and cross-checked against `concepts.md`'s actual
   concept list — an ID with no matching concept-list term is not credited.
2. **Wrong-registry gaming**: anchoring to an easily-satisfied but low-value registry (e.g. a
   generic Wikipedia/Wikidata link) to claim "anchored" status without real domain-ontology
   rigor. Countered by an anchor-type tier (see workflow §2.3) — only tier-1/tier-2 registries earn
   full credit; generic/general-purpose links earn partial credit at best.
3. **Selective anchoring**: anchoring only benign, well-known terms while leaving the paper's
   actual novel/contested terminology (its own coined variable names, ad hoc severity scores)
   un-anchored — exactly where a downstream agent most needs resolution. Countered by weighting
   coverage over the paper's *own* declared key-variable list, not over all nouns in the document.
4. **Stale/broken anchors**: citing an accession or ontology ID that is real-looking but wrong,
   retracted, or unresolvable. This metric's [ext] step is exactly the check that catches this —
   an LLM-only pass cannot distinguish "looks like a GEO accession" from "is a live GEO accession,"
   so the external resolver call is load-bearing, not decorative.
5. **Latent-space anchoring theater**: naming a reference atlas or embedding model without a
   version/checkpoint/build (e.g. "we used a standard scRNA-seq reference" with no name at all, or
   a name with no version) — this is the latent-space equivalent of ID-stuffing without
   resolvability, and must be scored as unanchored, not partially anchored.

### Why hard to Goodhart
The score is gated on an **external, adversarial resolution step** — [ext] ontology/registry
lookups against live databases (OLS/BioPortal for ontologies, NCBI/EBI/PROSPERO/CT.gov APIs for
accessions) that the paper's authors do not control and cannot game by writing convincing prose.
An LLM grader alone could be fooled by plausible-looking fake IDs or by term-dropping without real
identifiers; wiring in the actual resolver call means the score reflects whether the anchor
*resolves*, not whether it merely reads as anchored. Combined with the concept-list cross-check
(an anchor must correspond to something the ARA itself lists as a key concept/variable) and the
key-variable coverage weighting (anchoring must hit the paper's own declared important terms, not
padding), gaming requires either (a) fabricating IDs that happen to resolve to real, matching
entities — effectively requiring genuine research to fake — or (b) genuinely doing the anchoring
work, which is the desired behavior.

### Composition with the rest of the suite
This is explicitly flagged as **net-new** vs. the base ARA verifier (which checks structural
presence/shape compliance, not cross-registry resolvability) and net-new vs. other tournament
metrics that check access-tier honesty or accession *presence* (a metric could confirm "an
accession is present" without ever checking that its constituent variable names resolve to
controlled vocabulary — that's this metric's unique surface). It composes additively: a
dataset.md can score well on access-tier honesty (a different metric) while scoring poorly here
(present accession, but zero ontology-anchored variables), and vice versa. It also generalizes
beyond §11 — the same anchoring check applies to entities appearing in `concepts.md` (§3) and
`claims.md` (§2), which is why this metric's primary artifact is §11 "cross §2, §3": the dataset
descriptor is the anchor point, but the terms it should be consistent with live upstream.

---

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields)
From the target ARA:
- `data/dataset.md` (required trigger file — absence handling per §4)
- `data/preprocessing.md` (if present — may contain additional instrument/pipeline/reference terms)
- `logic/concepts.md` (§3) — cross-reference source: the ARA's own declared key concepts/entities
- `logic/claims.md` (§2) — cross-reference source: entities load-bearing for the paper's claims
- Specifically within `dataset.md`: the `**Key variables**` field (accession-block genre), the
  `## Included cohorts` table (secondary-reuse genre), and any `**Provenance**` / `**Size /
  content**` fields naming instruments, genome builds, pipeline versions, or reference atlases.

### 2.2 Step-by-step procedure

**Step 0 — Availability gate.**
Check whether `data/` exists at all for this ARA.
- If `data/` is legitimately absent (genre-check: does `PAPER.md` / `logic/problem.md` classify
  this as a pure-theory, tool/spec, or code-only work with no dataset claim anywhere in
  `logic/claims.md`?) → this is a **structural non-applicability**, not a penalized gap. Per the
  hard constraint this is still scored, not skipped: assign the metric's defined **floor-neutral
  score** for genuinely-inapplicable artifacts (see scoring function `NOT_APPLICABLE_FLOOR`,
  distinct from the *penalized* floor for data-driven papers that simply omitted anchoring).
- If the ARA's own claims/problem statement imply a dataset exists (e.g. claims reference sample
  sizes, cohorts, or measurements) but `data/dataset.md` is missing → this IS a penalized gap:
  score at the hard **PENALIZED_MISSING** floor (near-zero, not N/A), because availability itself
  is part of the score per the hard constraint.

**Step 1 — Entity extraction (LLM call, deterministic-output contract).**
Extract every named entity from `dataset.md` (+ `preprocessing.md` if present) that is a candidate
for controlled-vocabulary or latent-space anchoring: genes/proteins, diseases/phenotypes, cell
types/tissues, drugs/compounds, instruments/platforms, reference genome builds, pipeline software
+ version, embedding/reference-atlas names + version, and dataset-level identifiers (accessions,
registration numbers).

Prompt (exact):
```
You are extracting anchorable entities from a research-artifact dataset descriptor.
Read the text below. List every distinct entity that COULD be anchored to a controlled
vocabulary, ontology, accession registry, or named/versioned reference resource. For each entity
output a JSON object with:
  - "term": the exact surface string as it appears in the text
  - "entity_type": one of ["gene_protein","disease_phenotype","cell_type_tissue","drug_compound",
    "instrument_platform","genome_build","pipeline_software","reference_atlas_embedding",
    "dataset_accession","other"]
  - "has_explicit_id": true if an ID/accession/version already appears adjacent to the term in the
    text (e.g. "APOE (HGNC:613)", "GSE307990", "SpaceRanger v2.1.0"), false otherwise
  - "adjacent_id_string": the exact ID string if has_explicit_id is true, else null
Output ONLY a JSON array, no prose.

TEXT:
<<dataset.md + preprocessing.md content>>
```

**Step 2 — Key-variable weighting (deterministic, no LLM).**
Load `logic/concepts.md` and the `**Key variables**` field(s) from `dataset.md`. Build a set
`KEY_TERMS` (lowercased, whitespace-normalized) from these two sources. For each extracted entity
from Step 1, set `is_key = term.lower() in KEY_TERMS or fuzzy_match(term, KEY_TERMS) >= 0.85`
(fuzzy match via simple token-overlap ratio — deterministic, no LLM needed). This produces the
coverage weight: `weight = 2 if is_key else 1`.

**Step 3 — External resolution [ext] (the load-bearing anti-Goodhart step).**
For every entity with `has_explicit_id == true`, issue a resolver lookup against the registry
implied by its `entity_type`:
- `gene_protein` → HGNC/NCBI Gene API lookup on the ID
- `disease_phenotype` → MONDO/HPO lookup (OLS API) on the ID
- `cell_type_tissue` → Cell Ontology / UBERON (OLS API)
- `drug_compound` → ChEBI / ChEMBL lookup (semantic-scholar or ChEMBL resolver already available
  in this environment)
- `dataset_accession` → GEO/dbGaP/SRA/ENA/PROSPERO/ClinicalTrials.gov API, by prefix pattern match
  (`GSE\d+`→GEO, `phs\d+`→dbGaP, `NCT\d+`→ClinicalTrials.gov, `CRD\d+`→PROSPERO, etc.)
- `genome_build`, `pipeline_software`, `reference_atlas_embedding` → no formal ontology exists for
  most of these; instead check for the **presence of a version/build string** (regex: contains a
  version number, a genome-build token like `GRCh38`/`GRCm39`, or a dated release) — this is the
  "named + versioned" bar substituting for formal resolvability.

For each lookup, record `resolved: bool` (registry returned a live, matching record) and, where
applicable, `entity_name_match: bool` (the registry's canonical name for that ID token-overlaps the
extracted `term`, catching mismatched/copy-paste IDs).

Entities with `has_explicit_id == false` are recorded as `resolved = false` by construction (no ID
to check) but are retained for the coverage denominator — this is what penalizes term-dropping
without anchors.

**Step 4 — Aggregate to sub-scores, then final score.**

```python
from dataclasses import dataclass

@dataclass
class Entity:
    term: str
    entity_type: str
    has_explicit_id: bool
    is_key: bool          # from Step 2
    resolved: bool         # from Step 3 (False if no id or lookup failed/mismatched)

NOT_APPLICABLE_FLOOR = 0.5      # genuinely no-data ARA; neutral, not punished, not rewarded
PENALIZED_MISSING = 0.05        # data implied by claims but dataset.md absent entirely
PENALIZED_THIN = 0.15           # dataset.md present but zero extractable entities / abstract-only

def score_M64(data_available: bool, claims_imply_dataset: bool,
              entities: list[Entity]) -> float:
    # Step 0: availability gate
    if not data_available:
        return NOT_APPLICABLE_FLOOR if not claims_imply_dataset else PENALIZED_MISSING

    if len(entities) == 0:
        # dataset.md exists but is abstract-only / no extractable entities
        return PENALIZED_THIN

    # weighted coverage: fraction of (key-weighted) entities that are anchored AND resolved
    total_weight = sum(2 if e.is_key else 1 for e in entities)
    anchored_weight = sum(
        (2 if e.is_key else 1)
        for e in entities
        if e.has_explicit_id and e.resolved
    )
    coverage = anchored_weight / total_weight if total_weight > 0 else 0.0

    # penalty for id-stuffing: entities with an id that FAILED to resolve/match are worse than
    # entities with no id at all (signals fabricated or careless anchoring)
    n_present_ids = sum(1 for e in entities if e.has_explicit_id)
    n_failed_ids = sum(1 for e in entities if e.has_explicit_id and not e.resolved)
    stuffing_penalty = (n_failed_ids / n_present_ids) * 0.3 if n_present_ids > 0 else 0.0

    # dataset-level registry bonus: does the dataset itself (not just variables) carry a
    # resolvable accession/registration?
    dataset_level = [e for e in entities if e.entity_type == "dataset_accession"]
    dataset_level_bonus = 0.1 if any(e.resolved for e in dataset_level) else 0.0

    raw = coverage - stuffing_penalty + dataset_level_bonus
    return max(0.0, min(1.0, raw))
```

**Step 5 — Cross-layer consistency check (bonus/deduction, deterministic).**
For entities flagged `is_key`, verify the same `adjacent_id_string` (or a resolvable equivalent)
also appears near the corresponding term in `logic/concepts.md` / `logic/claims.md` where that term
recurs. Inconsistent IDs for the same term across the ARA (e.g. `HGNC:613` in `dataset.md` but a
different/no ID for "APOE" in `concepts.md`) trigger a flat `-0.05` deduction per inconsistency,
floor-clamped at 0. This is cheap (string/ID match, no extra LLM call) and enforces the
"resolves the same way everywhere" reward from §1.

### 2.3 Anchor-type tiers (used to gate what counts as "resolved" in Step 3)
- **Tier 1 (full credit)**: domain ontology with stable ID scheme (HGNC, MONDO, HPO, UBERON, Cell
  Ontology, ChEBI, LOINC, SNOMED-CT) or canonical data registry (GEO, dbGaP, SRA, ENA, PRIDE,
  PROSPERO, ClinicalTrials.gov) — resolver call confirms live record + name match.
- **Tier 2 (partial credit, ×0.6)**: named+versioned pipeline/software, genome build, or reference
  atlas/embedding with no formal ontology but a checkable version string (regex match only, no
  external call needed/available).
- **Tier 3 (no credit)**: generic encyclopedic links (Wikipedia/Wikidata), bare tool names with no
  version, or "standard nomenclature" claims with no ID.

Apply the tier multiplier to each `resolved` credit in Step 4's `anchored_weight` sum.

### 2.4 [sem]/[ext] call summary
- `[ext]` ontology resolver: OLS (Ontology Lookup Service) API or BioPortal API, queried per
  extracted ID string, entity_type-routed as in Step 3.
- `[ext]` registry resolver: NCBI E-utilities (GEO/dbGaP/SRA), EBI ENA API, PROSPERO search API,
  ClinicalTrials.gov API v2 — queried per accession-shaped string.
- `[ext]` ChEMBL resolver (available in this environment) for drug/compound entities.
- No `[sem]` (semantic-scholar) call is needed for this metric — it is a resolvability check, not
  a literature-grounding check (that's a different metric's surface).

---

## 3. Availability / penalize-don't-skip summary

| Situation | Treatment |
|---|---|
| No `data/` and no dataset implied anywhere in claims/problem | `NOT_APPLICABLE_FLOOR` (0.5) — genre-correct absence, neither rewarded nor punished |
| Dataset implied by claims but `data/dataset.md` missing | `PENALIZED_MISSING` (0.05) — availability itself scored down |
| `dataset.md` present but abstract-only (no accession, no key-variable detail) | `PENALIZED_THIN` (0.15) — present but unanchorable by construction |
| `dataset.md` present, entities extractable, but none carry explicit IDs | Falls out of the coverage formula naturally (near 0, since `anchored_weight` ≈ 0) — not a special case, just low coverage |
| IDs present but fail external resolution (fabricated/mismatched) | Coverage formula excludes them AND `stuffing_penalty` actively subtracts — worse than not claiming an ID at all |
| Full anchoring across key variables + dataset-level accession + cross-layer consistency | Score approaches 1.0 |

This directly honors the hard constraint: every branch produces a **score**, never a skip/N-A
placeholder outside the one deliberate `NOT_APPLICABLE_FLOOR` case for genre-correct absence — and
even that floor is a fixed neutral constant fed into the suite's aggregate, not an excluded/ignored
metric slot.
