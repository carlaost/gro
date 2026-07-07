# M64 — Controlled-vocabulary & latent-space anchoring (expander 1)

## 1. Expanded reasoning

### 1.1 What it signals
An ARA is only as useful to a downstream agent as its ability to be *linked* — to other ARAs, to
public registries, to reasoning engines that operate over canonical identifiers rather than prose.
M64 asks: when this artifact names a dataset, a variable, a biomarker, a method, or a construct, did
the compiler give it a handle that resolves outside this one document — a real accession, a
canonical-registry name, or a term that maps onto a controlled ontology/vocabulary class — or did it
leave every reference as free-floating natural language that only a human (or an LLM re-reading the
whole ARA) can disambiguate?

This is a **good-science** signal, not a cosmetic one, for three reasons:
1. **Falsifiability requires a shared referent.** A claim like "p-tau217 outperforms p-tau181" is only
   checkable against outside evidence if "p-tau217" resolves to the same analyte everyone else means
   by that string (a `ChEBI`/`UniProt`/`MeSH` sense) rather than an author-local shorthand.
2. **Reproducibility requires resolvable data.** A GEO/dbGaP/ClinicalTrials.gov/PROSPERO identifier is
   the difference between "a downstream agent can *fetch* this dataset and check the number" and "a
   downstream agent has to trust the prose."
3. **Cross-ARA linking is a compounding asset.** Every anchored term is a join key the corpus can use
   later (find every ARA touching MONDO:0004975 / Alzheimer disease; every ARA reusing GSE307990).
   Unanchored prose is a dead end for that use case even if the science inside is sound.

### 1.2 What it must reward
- **Live-resolvable external identifiers**: GEO (`GSE\d+`), dbGaP (`phs\d+`), SRA, ArrayExpress
  (`E-\w{4}-\d+`), EGA (`EGA[SD]\d+`), PRIDE (`PXD\d+`), ClinicalTrials.gov (`NCT\d{8}`), PROSPERO
  (`CRD\d+`) — anywhere they appear (§11 accession blocks, §2 claim Sources, §3 concept definitions).
- **Ontology-class matches for genuine technical vocabulary** in §3 (`concepts.md`): a `Notation`/
  `Definition` pair that maps onto a specific, non-root class in MeSH/UMLS/GO/HPO/MONDO/ChEBI/UBERON/
  NCBITaxon/EDAM/STATO/UO — not a match to a near-root generic class ("disease", "process"), which is
  gameable and near-worthless.
- **Named canonical datasets/cohorts** used off the shelf (ADNI, UK Biobank, TCGA, GTEx, BioFINDER,
  TRIAD, MIMIC, ...) even when they don't carry a fresh accession in *this* ARA, because they are
  independently locatable.
- **Access-tier honesty co-occurring with the anchor** (per `11_dataset.md`'s own scoring axis): an
  anchor that also states its resolvability class (open / controlled-access-via-dbGaP / by-request) is
  worth more than a bare identifier with an implied-but-unstated access claim, because it tells the
  downstream agent *how* to actually use the link.

### 1.3 What it must NOT reward
- **Keyword stuffing / tag padding.** A long `Tags:` list in `claims.md` or an inflated `concepts.md`
  is not "more anchoring" — each candidate must independently resolve; unresolved padding must not
  raise the count of opportunities in the denominator for free (see §2.4 anti-gaming).
- **Fabricated-looking identifiers.** A string that has the *shape* of an accession (regex-plausible)
  but does not resolve against the live registry is worse than no attempt — it is either a
  hallucination or a typo, and both are compiler defects the metric must catch, not reward for
  "trying."
- **Root-level / trivial ontology hits.** Matching "cell" to a top-level Cell Ontology node or "gene"
  to a root GO term is not genuine anchoring; it must be down-weighted or rejected (specificity check,
  §2.3).
- **Borrowed/generic terms treated as if they were the paper's contribution.** Per §3's own
  availability notes, `concepts.md` is supposed to hold the paper's *genuine* technical vocabulary —
  anchoring credit should concentrate on those entries, not on incidental mentions of well-known field
  jargon that isn't actually doing definitional work in the paper.
- **A theory/no-data paper being punished for lacking §11.** Per `11_dataset.md`'s explicit
  availability notes, `data/` is "correctly absent" for pure theory, tool/spec, and code-only work.
  This metric must not treat that absence as equivalent to a data-driven paper that simply forgot to
  anchor its dataset (see §1.4 for how the workflow reconciles this with the brief's penalize-don't-
  skip constraint).

### 1.4 Reconciling genre-correct absence with "never skip"
The brief's hard constraint says the metric must never emit N/A for missing/thin inputs — availability
is itself part of the score. The `11_dataset.md` shape file says genre-appropriate absence of §11 must
not be penalized as a gap. These are not actually in conflict once the metric is scoped correctly:
**the metric's opportunity space spans §2+§3+§11 jointly, and §2/§3 (`claims.md`/`concepts.md`) are
mandatory-core and never absent.** So there is never a case with zero opportunities to score. What
changes by genre is *reweighting*, not skipping:

- If §11 is present → it carries real weight (anchoring datasets/accessions is exactly what it's for).
- If §11 is genuinely absent (theory/tool/code-only — detected by an implied-data-scan over §2/§3
  finding no dataset/cohort/N=-style language) → its weight is redistributed onto §2+§3 at full
  credit; absence itself costs nothing extra.
- If §11 is absent or thin *while §2/§3 imply data-driven work* (claims cite an "N=", a cohort, a
  platform, an accession-shaped string, or concepts.md defines assay/cohort vocabulary) → that
  mismatch is itself scored as a defect (the "implied-data-without-provenance" flag), because
  unavailability of an artifact the work's own claims presuppose *is* an input, exactly as the brief
  requires. This preserves "never skip" without punishing legitimately data-free science — the
  distinguishing test is evidence *inside the ARA itself* that data should exist, not a blanket rule.

### 1.5 Failure modes / gaming routes and how the design blocks them
| Gaming route | Countermeasure |
|---|---|
| Stuff `Tags:`/concept headings with generic-but-ontology-matchable words | Specificity filter rejects near-root/generic ontology hits (§2.3); only non-trivial-depth classes count |
| Paste a fake/expired/mistyped accession that *looks* valid | Live resolver call required — unresolved-but-well-formed IDs score **worse** than no ID (flag: `malformed_or_dead_id`), not neutral |
| Claim "open access" without naming what's actually open vs. gated | Access-tier co-occurrence check (§2.5) requires the qualifier to name a scope (raw vs. processed vs. metadata) |
| Inflate `concepts.md` with borrowed textbook terms to raise anchor count | Only concepts whose `Definition` demonstrably does definitional work for this paper's claims (cross-referenced against `claims.md` Tags/Statement) get full weight; purely decorative entries get a discount multiplier |
| Hide a real data-driven study behind a thin/absent `data/dataset.md` | Implied-data-scan (§1.4) forces a penalty even without a populated §11 to inspect |

### 1.6 Relationship to assessment-critique notes / why net-new
This metric was ranked top-10 specifically as **net-new relative to the ARA verifier**: the verifier's
grounding checks (Rule 16, `Sources` quote discipline) confirm a number is *internally* traceable to
an evidence file — they say nothing about whether the *entity itself* (the dataset, the analyte, the
construct) is externally *resolvable*. M64 adds the interoperability axis (can another ARA, another
agent, or a registry lookup act on this reference) rather than duplicating the internal-consistency
axis other metrics already own. To keep that edge tight, this workflow deliberately does **not**
re-score `Sources`-quote presence, claim/evidence matching, or `Interpretation` vs. `Evidence basis`
separation — those belong to grounding-family metrics. It only scores resolvability/translatability of
the referents once they're already assumed present.

---

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields consumed)
From the ARA under evaluation (root `research/ara-library/<ara-id>/`):
- `data/dataset.md` (§11) — if present: accession blocks (`Source / access`, `Size / content`, `Key
  variables`), `Included cohorts` table, `External datasets used` bullets, `Provenance and access`.
- `logic/concepts.md` (§3) — every `## {Term}` heading + its `Notation` and `Definition` fields.
- `logic/claims.md` (§2) — every claim's `Tags` field and the `Statement` text (for accession-shaped
  substrings and named-cohort mentions that leak into claim prose).

### 2.2 Step-by-step procedure

**Step 0 — Parse.** Split each file into its structural blocks per the documented shapes (accession
blocks / cohort table rows for §11; concept sections for §3; claim blocks for §2). Record, per source
field, the raw text span it came from (for auditability).

**Step 1 — Candidate extraction.**
- *Accession-shaped candidates*: regex-scan §11 accession-block headers/`Source / access` lines, §2
  `Tags` + `Statement`, and §3 `Definition` text for the identifier patterns in §1.2.
- *Named-canonical-dataset candidates*: fuzzy-match (case-insensitive substring + Levenshtein ≤2 on
  tokens) against a curated seed list of canonical cohort/consortium names (ADNI, UK Biobank, TCGA,
  GTEx, BioFINDER, TRIAD, MIMIC-III/IV, GEO, dbGaP, PRIDE, 1000 Genomes, gnomAD, ...; list is
  versioned and extensible, not exhaustive by design — misses fall through to Step 2's ontology call).
- *Vocabulary candidates*: every §3 concept heading + its `Notation` token(s); every §2 `Tags` entry.

**Step 2 — External resolution [ext: ontology/registry resolver].** For each candidate, call exactly
one of the following, deterministically chosen by candidate type:

1. **Accession-shaped candidates → live registry lookup**, e.g.:
   - GEO: `GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=<ID>[Accession]&retmode=json`
   - ClinicalTrials.gov: `GET https://clinicaltrials.gov/api/v2/studies/<NCT_ID>`
   - dbGaP/ArrayExpress/EGA/PRIDE: analogous accession-resolution endpoints for each registry.
   - PROSPERO has no public API — treat a well-formed `CRD\d+` as `format_valid_unverified` (a
     distinct, lower tier than a live-confirmed hit; never silently upgraded to "resolved").
   - Outcome recorded: `resolved` (HTTP 200 + accession echoed back in payload), `dead_or_mismatched`
     (200 but content doesn't match / 404), or `format_valid_unverified`.

2. **Vocabulary / free-text candidates → ontology lookup**, using the EBI Ontology Lookup Service
   (OLS) as the canonical `[ext]` call:
   ```
   GET https://www.ebi.ac.uk/ols4/api/search?q=<term>&exact=false&ontology=mesh,chebi,go,hp,mondo,uberon,ncbitaxon,efo,edam,stato,uo
   ```
   Prompt/query construction: `<term>` = the concept heading text (e.g. `"p-tau217"`), retried once
   with the `Notation` string if the heading yields no hits (e.g. `"p217"`). Take the top-scoring
   result per ontology; record its `iri`, `ontology_name`, `label`, `score` (OLS relevance score,
   0–100), and its **depth-from-root** in that ontology's class hierarchy (via the term's `/ancestors`
   endpoint — a shallow-depth hit like depth ≤2 is treated as a generic/root-level match).
   - Outcome recorded: `ontology_match` (score ≥ 70 AND depth ≥ 3), `weak_match` (score 40–69, or
     depth 3 but score <70), or `no_match` (score <40 or best hit is depth ≤2).

3. **Named-canonical-dataset candidates matched in Step 1** are recorded as `named_canonical` directly
   (no live call needed — the value is in being independently locatable by name, not in a fresh API
   round-trip); optionally corroborated by a single OLS/registry lookup on the name if time budget
   allows, but this is not required for scoring.

**Step 3 — Tier classification.** Collapse each candidate's Step 2 outcome into one scoring tier:

| Tier | Criteria | Weight |
|---|---|---|
| A — Resolved-external | `resolved` accession, or `ontology_match` | 1.0 |
| B — Recognized-canonical | `named_canonical`, or `format_valid_unverified` (PROSPERO-style) | 0.7 |
| C — Weak | `weak_match` | 0.4 |
| D — Unanchored/failed | `no_match`, `dead_or_mismatched` | 0.0 (and `dead_or_mismatched` additionally sets a `fabrication_flag`) |

**Step 4 — Definitional-relevance discount (anti-padding, §1.5).** For each §3 concept candidate,
check whether its heading or a close synonym appears in any §2 claim's `Tags` or `Statement`. If not,
multiply its tier weight by 0.6 (it may still be a legitimately narrow, paper-specific term, but it
isn't pulling weight in the claims layer, so full anchoring credit isn't warranted).

**Step 5 — Implied-data-without-provenance check (§1.4).** Scan all §2 `Statement`/`Evidence basis`
text and §3 `Definition` text for data-driven-work signals: regex/keyword hits for `N\s*=\s*\d+`,
"cohort", "participants", "enrolled", "platform", assay/instrument names, or any accession-shaped
string. If ≥1 such signal fires AND §11 (`data/dataset.md`) is absent or has fewer than one populated
accession/cohort block, set `implied_data_without_provenance = True`.

**Step 6 — Access-tier honesty bonus/penalty.** For every Tier A/B candidate sourced from a §11
accession block, check whether that block's `Source / access` line names *both* an access claim
(open/controlled/by-request) *and* a qualifier scoping which sub-part it applies to (raw vs. processed
vs. metadata). Missing the qualifier on an otherwise-resolved accession costs a fixed per-candidate
deduction (see scoring function `ACCESS_QUALIFIER_PENALTY`).

**Step 7 — Score.** Run the scoring function below.

### 2.3 Scoring function (real Python against the documented artifact shape)

```python
import re
from dataclasses import dataclass, field
from enum import Enum

class Tier(Enum):
    A_RESOLVED = 1.0
    B_RECOGNIZED = 0.7
    C_WEAK = 0.4
    D_UNANCHORED = 0.0

@dataclass
class Candidate:
    text: str                     # raw string as it appears in the ARA
    source_field: str             # 'dataset.accession' | 'dataset.cohort' | 'concept.heading'
                                   # | 'concept.notation' | 'claim.tags' | 'claim.statement'
    tier: Tier
    fabrication_flag: bool = False
    definitional_relevance: bool = True   # False => padding discount applies (Step 4)
    has_access_qualifier: bool | None = None  # only meaningful for dataset accessions

ACCESS_QUALIFIER_PENALTY = 6.0   # points, per resolved accession missing scope qualifier
PADDING_DISCOUNT = 0.6
FABRICATION_PENALTY = 8.0        # points, per candidate flagged dead_or_mismatched
IMPLIED_DATA_PENALTY = 25.0      # points, flat, if Step 5 fires

DATA_SIGNAL_RE = re.compile(
    r"\bN\s*=\s*\d+\b|\bcohort\b|\bparticipants\b|\benrolled\b|\bplatform\b|"
    r"GSE\d+|phs\d+|NCT\d{8}|CRD\d+|E-\w{4}-\d+|EGA[SD]\d+|PXD\d+",
    re.IGNORECASE,
)

def weighted_candidate_score(c: Candidate) -> float:
    w = c.tier.value
    if not c.definitional_relevance and c.source_field.startswith("concept"):
        w *= PADDING_DISCOUNT
    return w

def compute_m64(
    candidates: list[Candidate],
    section11_present: bool,
    section11_populated: bool,   # >=1 real accession/cohort block, not just an intro paragraph
    claims_and_concepts_text: str,   # concatenated raw text of claims.md + concepts.md, for Step 5
) -> dict:
    if not candidates:
        # claims.md / concepts.md are mandatory-core and always yield >=1 candidate in practice
        # (every concept heading and every claim's Tags field is a candidate slot); an empty
        # candidate list means parsing failed or the ARA is degenerate — score the floor, do not skip.
        base = 0.0
    else:
        raw_scores = [weighted_candidate_score(c) for c in candidates]
        base = 100.0 * (sum(raw_scores) / len(raw_scores))

    # Step 5: implied-data-without-provenance
    implied_needed = bool(DATA_SIGNAL_RE.search(claims_and_concepts_text)) and not section11_present
    thin_when_present = section11_present and not section11_populated
    implied_data_without_provenance = implied_needed or (
        section11_present and thin_when_present and
        bool(DATA_SIGNAL_RE.search(claims_and_concepts_text))
    )
    penalty = 0.0
    if implied_data_without_provenance:
        penalty += IMPLIED_DATA_PENALTY

    # Step 6: access-tier honesty
    for c in candidates:
        if c.source_field == "dataset.accession" and c.tier in (Tier.A_RESOLVED, Tier.B_RECOGNIZED):
            if c.has_access_qualifier is False:
                penalty += ACCESS_QUALIFIER_PENALTY

    # fabrication penalty
    penalty += FABRICATION_PENALTY * sum(1 for c in candidates if c.fabrication_flag)

    score = max(0.0, min(100.0, base - penalty))

    return {
        "score": round(score, 1),
        "n_candidates": len(candidates),
        "tier_counts": {t.name: sum(1 for c in candidates if c.tier == t) for t in Tier},
        "implied_data_without_provenance": implied_data_without_provenance,
        "fabrication_flags": sum(1 for c in candidates if c.fabrication_flag),
        "penalty_applied": round(penalty, 1),
        "genre_note": (
            "section11_absent_unpenalized" if not section11_present and not implied_needed
            else "section11_present" if section11_present
            else "section11_absent_but_implied_by_claims_or_concepts"
        ),
    }
```

`Candidate` objects are produced by Steps 1–2's parsing/resolver pipeline (not shown as code — those
are I/O-bound external calls: NCBI E-utils, ClinicalTrials.gov API v2, EBI OLS API) and fed into
`compute_m64`. The function is fully deterministic given the resolver outcomes, so re-running it
against a cached resolver-response snapshot always reproduces the same score (important for tournament
reproducibility — the *scoring* is deterministic even though the resolver calls are network I/O).

### 2.4 Output
A single `M64` scalar in `[0, 100]` plus the structured `dict` above (tier breakdown, flags) attached
as evidence — the flags (`implied_data_without_provenance`, `fabrication_flags`,
`ACCESS_QUALIFIER_PENALTY` hits) are exactly the "penalize, don't skip" trail: even a 0-scoring ARA
produces a populated, auditable reason set rather than an N/A.

---

## 3. Why this is hard to Goodhart

- **Live external resolution, not self-report.** Both branches of Step 2 hit a real external system
  (NCBI/ClinicalTrials.gov registries, EBI OLS) rather than trusting the ARA's own claim that a term is
  "standard" or an ID is "valid." A compiler cannot raise its score by simply asserting anchoring —
  the identifier or term must actually exist and actually match in the target system.
- **Fabrication is punished harder than omission.** An accession-shaped string that fails live
  resolution (`dead_or_mismatched`) scores strictly worse (Tier D + `FABRICATION_PENALTY`) than
  honestly not attempting an anchor. This removes the incentive to paste plausible-looking-but-fake
  IDs to farm Tier-A-shaped credit.
- **Specificity/depth filtering blocks root-term gaming.** Matching to a near-root ontology class
  (shallow `depth-from-root`) is explicitly excluded from `ontology_match`, so stuffing generic words
  ("disease," "process," "cell") cannot cheaply inflate the resolved-candidate count.
- **Definitional-relevance cross-check blocks concept-padding.** A `concepts.md` entry that resolves to
  a real ontology class but never actually appears in any claim's `Tags`/`Statement` gets discounted
  (Step 4) — anchoring only pays full credit when the anchored term is load-bearing for the paper's
  actual claims, not merely present as decoration.
- **The implied-data check closes the "just omit §11" escape hatch.** Because absence of `data/
  dataset.md` is only free when nothing else in the ARA implies data-driven work, a compiler cannot
  dodge low anchoring scores by simply not writing a dataset section for a study that obviously has
  one (Step 5's flat penalty fires on the internal-evidence mismatch, not on the missing file alone).

## 4. Composition with the rest of the suite

M64 is intentionally orthogonal to grounding/verifier-family metrics: it never re-checks `Sources`
quote presence, claim-evidence matching, or internal claims↔concepts consistency — those own the
*internal-traceability* axis. M64 owns the *external-resolvability / interoperability* axis: can this
ARA's entities be looked up, linked, and reused outside the document. Because the two axes are
measuring genuinely different failure modes (an ARA can be perfectly internally grounded yet fully
unanchored to any external vocabulary, or vice versa — richly anchored terms with sloppy internal
grounding), M64 should be aggregated as an **additive, modest-weight** component rather than averaged
against grounding scores in a way that lets either axis mask the other. Its natural place in a
composite good-science score is as a *bonus/interoperability* term layered on top of a
correctness/grounding floor — a paper with excellent internal grounding but zero anchoring should score
respectably overall but visibly lose the interoperability bonus, and a paper that anchors heavily to
external registries while being internally unsound should not be able to buy its way to a high
composite score through M64 alone.
