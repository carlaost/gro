# M64 — Controlled-vocabulary & latent-space anchoring (expander 3)

## 1. What this metric is actually measuring

M64 is an **interoperability** signal, not a correctness or completeness signal. Every other
metric on `data/dataset.md` / `logic/claims.md` / `logic/concepts.md` asks "is this true / thorough
/ well-cited?" M64 asks a different question entirely: **can another agent, reading this ARA cold,
programmatically resolve its vocabulary and datasets to something outside the document itself?**
An ARA whose concepts and data are anchored to controlled vocabularies (MeSH, HGNC, UMLS, ChEBI,
Cell Ontology, OBI, DOID, SNOMED-CT), canonical dataset registries (GEO, SRA, dbGaP, ArrayExpress,
PROSPERO, ClinicalTrials.gov/NCT), or versioned/named latent spaces (a specific reference genome
build, a specific named+versioned embedding model) is one that a downstream agent can **cross-link**
without re-reading prose — it can pivot from this ARA into the ontology graph, pull the accession,
or align embeddings from a different ARA that anchors to the same space. An ARA that uses only
free-text, un-anchored jargon is an epistemic island: correct or not, it cannot be machine-linked
to anything else.

This is why it ranked top-10 as **net-new vs. the ARA verifier**: the semantic verifier checks
internal consistency and grounding-to-source; it does not check whether the *terms themselves*
point outward to a resolvable external identifier space. Two ARAs can both pass Seal Level 1
grounding discipline while one is fully anchored (GSE307990, HGNC:APOE, DOID:10652) and the other
is prose-only ("the amyloid gene", "postmortem brain tissue") — the verifier is blind to that
difference; M64 is built to see exactly it.

### What it must reward
- Concept/claim terms that map to a **specific, resolvable identifier** in a real controlled
  vocabulary or registry (not just "this word appears in a dictionary somewhere").
- Dataset references that carry an **accession** (GEO, dbGaP, SRA, PROSPERO, NCT) rather than a
  bare description ("we used public RNA-seq data").
- **Version-pinned** latent/reference spaces — a genome build (GRCh38, not "the human genome"), a
  named+versioned embedding model/checkpoint, a specific ontology release — because an unversioned
  reference is not actually translatable (two ARAs both saying "GRCh38" can be cross-linked
  positionally; two both saying "the reference genome" cannot).
- **Co-occurrence of identifier + access-tier statement** for data (per the §11 shape doc's own
  scoring axis): an anchored-but-access-opaque accession is only half-anchored for a downstream
  agent that needs to know if it can actually pull the data.

### What it must NOT reward
- Namedropping generic scientific words that happen to have *some* MeSH/UMLS entry (e.g. "cancer",
  "protein", "cell") — resolvability of trivial general vocabulary is not a signal of good science,
  it's a floor every paper clears for free. The metric must gate on **relevance-weighted**
  resolution: does the resolved definition actually match how the term is used in *this* ARA's
  concepts.md `Definition` field, on the specific technical sense the paper needs?
- Fabricated-looking accessions or DOI-shaped strings that are never externally checked — anchoring
  must be **verified by an actual resolver call**, not by regex pattern-matching a GSE-shaped
  string and assuming it's real.
- Over-tagging: an ARA that appends a long list of popular ontology terms unrelated to its actual
  claims to farm coverage. Anchor terms must be drawn from concepts.md's own genuine terms and
  claims.md's own cited Sources — never from an independently generated keyword list.
- Papers that legitimately have **no** anchorable vocabulary (pure theory/proof papers whose
  concepts are formal objects, e.g. a topology invariant with no external registry) being scored
  as if they failed an anchoring test they were never eligible to pass on the *concept* axis — but
  see §4 on penalize-don't-skip: this genre nuance changes the *interpretation* of a low score, not
  whether the metric computes one.

## 2. Failure modes / gaming routes

| Gaming route | Why it fails against this design |
|---|---|
| Paste real-looking but fake accessions (`GSE999999`) | Step 3 does a live resolver/registry call, not string matching; a dead accession scores 0, worse than an honestly-absent one is not, because a fabricated identifier is an integrity red flag layered on top (see §4 penalty stacking). |
| Pad concepts.md with generic anchorable words to inflate coverage | Step 2's [sem] relevance check requires the resolved definition to align with the ARA's own `Definition` field for that concept, and Step 5 down-weights terms whose `Related concepts` / usage frequency in claims.md is near-zero (i.e., terms that only exist to be anchored, not to carry the paper's argument). |
| Cite a vague/unversioned reference space to *look* anchored without being pin-precise | Step 3b explicitly checks for a version token; unversioned hits are capped at `resolved_ambiguous` (0.4), never `resolved_exact`. |
| Anchor only the *easy* boilerplate terms (species, generic assay names) and leave the paper's actual novel-but-anchorable entities (specific gene variant, specific biomarker isoform) un-anchored | Coverage is computed over the anchorable-term *universe* extracted independently from concepts.md + claims.md before resolution is attempted (Step 1), so cherry-picking which terms to bother anchoring doesn't change the denominator. |
| Claim "latent space anchoring" via a proprietary/inaccessible embedding with no way for another agent to actually obtain the same space | Step 3c requires the space to be either (a) a named public checkpoint/artifact resolvable via a model registry lookup, or (b) accompanied by a public accession for the embedding weights/vectors themselves; unresolvable-in-practice claims score as `not_resolved`. |

## 3. Why hard to Goodhart, and composition with the suite

Hard to Goodhart because the score is gated on an **external, non-authorable resolution step** —
the paper's author (or the compiler) cannot make a term "more anchored" by writing better prose;
they can only do it by actually using the correct canonical identifier, which either resolves or
doesn't, and resolves *to the paper's own stated sense* or doesn't. The relevance check (matching
resolved definition to the ARA's own concept `Definition`) blocks the cheapest gaming route
(dumping resolvable-but-irrelevant vocabulary). The version-pin requirement blocks the second
cheapest route (vague-but-technically-not-wrong references). And because coverage is computed over
an independently-extracted term universe, gaming by selective anchoring doesn't move the number.

Composition: M64 sits orthogonally to (a) claims comprehensiveness/grounding metrics (which check
*internal* evidentiary support, not *external* resolvability), (b) data access-tier honesty metrics
on §11 (which check whether access is stated accurately, not whether the accession is anchored to a
registry at all — M64 subsumes "is there an accession" and adds "does it resolve," while leaving
"is the access tier honestly qualified" to its sibling metric; the two share raw extraction but
score different axes and should not double-penalize the same defect), and (c) novelty/FOL-ability
metrics on concepts.md (which ask if the vocabulary is *original*, the near-opposite concern —
anchoring rewards mapping to *existing* canonical space, novelty rewards genuine new contribution;
a well-designed ARA scores well on both by anchoring its borrowed/standard vocabulary while its
genuinely novel terms correctly score low on anchoring and high on novelty). This makes M64 a clean
net-new axis rather than a restatement of any neighbor.

## 4. Penalize-don't-skip

Per the hard constraint, unavailability is itself an input, never an N/A:

- **No `data/dataset.md` at all**: do not skip the data sub-score. Score `S_data = 0.15` (a fixed
  floor, not zero) — reflecting that *most* ARAs describing empirical work should carry at least one
  anchorable accession or registered protocol, so bare absence is informative and scored low, while
  reserving strictly-zero for the worse case of a *present* `data/dataset.md` with dataset
  descriptions but zero resolvable accessions (fabricated-looking or purely prose-described data
  with no accession attempted at all) — that case is scored `0.0`, strictly below silent absence,
  because it demonstrates the compiler *had the chance* to anchor and produced nothing. Genuinely
  data-free genres (pure theory/proof papers) are identified post-hoc by cross-checking
  `logic/problem.md`/`solution/` for the presence of any empirical dataset reference at all — if
  none exists anywhere in the ARA, this is logged as `genre: theory` and `S_data` is **excluded from
  the weighted denominator** (not silently defaulted to 1.0, and still reported in the output as
  `S_data: n/a (genre-excluded, verified no dataset claim anywhere in ARA)` for audit) — this is the
  one legitimate genre exemption, and it must be actively verified (not merely inferred from
  `data/`'s absence, since absence-with-a-cited-external-dataset in `logic/solution/` still counts).
- **`concepts.md` has fewer than 3 genuinely anchorable terms**: still compute `S_concept` over
  whatever universe exists (even n=1); a thin anchorable-term universe naturally produces a coverage
  fraction with high variance, so the aggregator additionally reports raw counts alongside the ratio
  so a downstream reviewer can distinguish "3/3 anchored, high confidence" from "1/1 anchored, low
  confidence" without the metric itself collapsing to N/A.
- **Resolver call fails/times out (network/API unavailable)**: scored as `not_resolved` (0.0) for
  that term, logged distinctly as `resolution_error` vs. genuine `not_found`, but contributes to the
  denominator either way — a metric run under degraded external-tool access must not silently
  improve scores by dropping terms it couldn't check.

## 5. Generation / compute workflow

### 5.1 Inputs (exact artifact fields)
- `data/dataset.md`: all `## {Accession} — ...` block headers, `**Source / access**` strings,
  `## Included cohorts` table (`Source study` / registration numbers), `## External datasets used`
  bullets.
- `logic/concepts.md`: every `## {Term Name}` heading + its `**Notation**`, `**Definition**`,
  `**Related concepts**` fields.
- `logic/claims.md`: every `**Sources**` entry's `<value>` and `«verbatim quote»` (for cross-checking
  which concepts are load-bearing enough to matter), plus `**Tags**` per claim.

### 5.2 Step 1 — Extract candidate anchor universe (deterministic + regex)

```python
import re

ACCESSION_PATTERNS = {
    "GEO": r"\bGSE\d+\b|\bGSM\d+\b",
    "SRA": r"\bSR[APRX]\d+\b",
    "dbGaP": r"\bphs\d{6}(\.v\d+\.p\d+)?\b",
    "ArrayExpress": r"\bE-[A-Z]{4}-\d+\b",
    "PROSPERO": r"\bCRD\d+\b",
    "ClinicalTrials": r"\bNCT\d{8}\b",
    "dbSNP": r"\brs\d+\b",
    "UniProt": r"\b[OPQ][0-9][A-Z0-9]{3}[0-9]\b",
}

def extract_dataset_accessions(dataset_md: str) -> list[dict]:
    hits = []
    for source, pattern in ACCESSION_PATTERNS.items():
        for m in re.finditer(pattern, dataset_md):
            # capture surrounding line for the access-tier co-occurrence check
            line_start = dataset_md.rfind("\n", 0, m.start()) + 1
            line_end = dataset_md.find("\n", m.end())
            line = dataset_md[line_start: line_end if line_end != -1 else None]
            hits.append({"registry": source, "id": m.group(0), "context_line": line})
    return hits

def extract_concept_terms(concepts_md: str) -> list[dict]:
    # split on '## ' headings; each block -> {name, notation, definition, related}
    blocks = re.split(r"\n## ", concepts_md)
    terms = []
    for b in blocks[1:]:
        name, _, body = b.partition("\n")
        def field(tag):
            m = re.search(rf"\*\*{tag}\*\*:\s*(.+)", body)
            return m.group(1).strip() if m else ""
        terms.append({
            "name": name.strip(),
            "notation": field("Notation"),
            "definition": field("Definition"),
            "related": field("Related concepts"),
        })
    return terms
```

### 5.3 Step 2 — [sem] anchorability + relevance classification (LLM call, per concept term)

For every extracted concept term, one LLM call classifies whether it *should* be anchorable and,
if so, to which vocabulary family — this must run before any external resolver call, to avoid
wasting resolver budget on genuinely paper-local constructs (which must NOT be penalized, per the
concepts.md shape doc's "honestly short/local vocabulary is not a defect" note).

**Exact prompt:**
```
You are classifying a technical term from a research paper's concept glossary for
external-vocabulary anchorability.

Term: "{name}"
Notation: "{notation}"
Definition: "{definition}"
Related concepts: "{related}"

Answer strictly as JSON:
{
  "anchorable": true|false,
  "vocabulary_family": "gene_protein" | "disease_phenotype" | "assay_instrument" |
                         "cell_type" | "chemical_compound" | "statistical_method" |
                         "reference_genome_build" | "embedding_model" | "none",
  "reason": "<one sentence: why this is or isn't expected to exist in a public
             controlled vocabulary/registry, independent of this paper>"
}

A term is anchorable if it names a standardized real-world entity, method, or resource
that exists independently of this paper (e.g. a gene symbol, a disease name, a named
assay, a reference genome build, a named public embedding model).
A term is NOT anchorable if it is a paper-local construct, a novel named index/score
the paper itself defines, or a purely formal/mathematical object with no external
registry (these are legitimate and must not be penalized for lacking anchoring).
```

The JSON is parsed deterministically; `anchorable=false` terms exit the pipeline here and are
excluded from the anchoring denominator entirely (they are the deliberate genre-fairness carve-out
from §1/§3 — a novel construct is not an anchoring failure).

### 5.4 Step 3 — [ext] resolver calls, per anchorable term / accession

Concrete external calls, chosen per `vocabulary_family` / registry:

| Source | External call |
|---|---|
| `gene_protein` | HGNC REST (`https://rest.genenames.org/search/{symbol}`) or NCBI Entrez `esearch` on `gene` db |
| `disease_phenotype` | OLS4 (EBI Ontology Lookup Service) `https://www.ebi.ac.uk/ols4/api/search?q={term}&ontology=doid,mesh` |
| `chemical_compound` | ChEBI via OLS4, or PubChem PUG-REST |
| `cell_type` | OLS4 against Cell Ontology (`ontology=cl`) |
| `assay_instrument` | OLS4 against OBI (`ontology=obi`) |
| `statistical_method` | OLS4 against STATO (`ontology=stato`) |
| `reference_genome_build` | Static allow-list check (GRCh37/38, mm10/39, etc.) + version-token regex — must include a build number, not just species |
| `embedding_model` | Model-registry lookup (Hugging Face Hub API `/api/models/{name}`) requiring an exact repo id **and** a revision/commit hash or version tag |
| GEO/SRA/dbGaP/ArrayExpress/NCT/PROSPERO accessions | Direct registry existence check: `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={id}&targ=self&form=text&view=quick` (GEO), NCBI Entrez `esearch`/`esummary` (SRA/dbGaP), ClinicalTrials.gov API v2 `GET /studies/{nct_id}`, PROSPERO search page lookup by CRD number |

```python
def resolve_term(term: dict) -> dict:
    """
    Dispatches to the registry-specific external call implied by
    term['vocabulary_family'], returns the best-match hit (or None) plus its
    definition/summary text for the relevance check, and whether a version
    token was present for build/model-type families.
    """
    family = term["vocabulary_family"]
    query = term["notation"] or term["name"]
    # e.g. for OLS4 families:
    #   resp = http_get(f"https://www.ebi.ac.uk/ols4/api/search?q={query}&ontology={ONTOLOGY_MAP[family]}")
    #   best = top_hit(resp) or None
    # for accessions:
    #   resp = http_get(REGISTRY_URL[family].format(id=term["id"]))
    #   best = {"exists": resp.status_code == 200, "summary": resp.text[:500]}
    # (implementation is a thin HTTP wrapper per row of the table above;
    #  omitted here since it is pure I/O, not scoring logic)
    raise NotImplementedError("registry dispatch — see table above")
```

### 5.5 Step 4 — [sem] relevance check (LLM call, per resolved hit)

Only for terms that *did* resolve to a candidate hit — confirms the resolved definition matches the
sense used in this ARA (blocks the "trivial generic match" gaming route).

**Exact prompt:**
```
Term as used in this paper: "{name}" — "{definition}"
Candidate external match found: "{resolved_id}" — "{resolved_summary}"

Does the external match refer to the SAME specific concept as used in this paper
(not just a superficially similar or more generic sense)? Answer strictly as JSON:
{ "match": "exact" | "partial" | "mismatch", "reason": "<one sentence>" }
```

### 5.6 Step 5 — Deterministic scoring

```python
def score_term(anchorable_term: dict, resolution: dict | None, relevance: dict | None,
                versioned: bool) -> float:
    if resolution is None or not resolution.get("exists", False):
        return 0.0  # not_resolved
    if relevance is None:
        return 0.0  # resolver hit but no relevance check available -> treat as unverified, 0
    if relevance["match"] == "mismatch":
        return 0.0
    if relevance["match"] == "partial":
        return 0.4  # resolved_ambiguous
    # exact match:
    return 1.0 if versioned or anchorable_term["vocabulary_family"] not in (
        "reference_genome_build", "embedding_model") else 0.4


def score_concepts(concept_terms: list[dict]) -> tuple[float, dict]:
    anchorable = [t for t in concept_terms if t["anchorable"]]
    if not anchorable:
        return None, {"note": "no anchorable terms in concepts.md — genre-excluded from denominator "
                               "if verified no external-vocabulary claim exists anywhere in ARA"}
    scores = [score_term(t, t["resolution"], t["relevance"], t["versioned"]) for t in anchorable]
    return sum(scores) / len(scores), {"n_anchorable": len(anchorable), "raw_scores": scores}


def score_data(dataset_accessions: list[dict]) -> float:
    if not dataset_accessions:
        return 0.15  # floor for present-but-unaccessioned data section; see §4
    per_accession = []
    for acc in dataset_accessions:
        exists = acc["resolution"]["exists"]
        has_access_tier = bool(re.search(
            r"\b(open|controlled|restricted|by[- ]request|embargo)\b",
            acc["context_line"], re.I))
        if not exists:
            per_accession.append(0.0)
        elif exists and has_access_tier:
            per_accession.append(1.0)
        else:
            per_accession.append(0.6)  # resolves but access-tier ambiguity not stated inline
    return sum(per_accession) / len(per_accession)


def m64_score(dataset_md: str, concepts_md: str, claims_md: str,
              genre_is_theory_verified: bool) -> dict:
    accessions = extract_dataset_accessions(dataset_md)
    # ... resolve each accession via Step 3 registry dispatch (external I/O) ...
    concept_terms = extract_concept_terms(concepts_md)
    # ... classify each via Step 2 [sem] call, resolve anchorable ones via Step 3,
    #     relevance-check via Step 4 ...

    s_concept, concept_meta = score_concepts(concept_terms)

    if genre_is_theory_verified and not accessions:
        s_data, data_meta = None, {"note": "n/a (genre-excluded, verified no dataset "
                                            "claim anywhere in ARA)"}
    else:
        s_data = score_data(accessions)
        data_meta = {"n_accessions": len(accessions)}

    components = [c for c in (s_concept, s_data) if c is not None]
    if not components:
        # both legitimately excluded (pure theory paper, zero anchorable concepts) —
        # still must not be N/A per the hard constraint: floor score, not skip
        final = 0.1
    else:
        weights = []
        vals = []
        if s_data is not None:
            vals.append(s_data); weights.append(0.55)  # data anchoring weighted higher —
                                                          # accessions are unambiguous identifiers
        if s_concept is not None:
            vals.append(s_concept); weights.append(0.45)
        wsum = sum(weights)
        final = sum(v * w for v, w in zip(vals, weights)) / wsum

    return {
        "m64_score": round(final, 3),
        "s_data": s_data, "data_meta": data_meta,
        "s_concept": s_concept, "concept_meta": concept_meta,
    }
```

### 5.7 Worked example (from the shape doc's own data)

- huu25 (`GSE307990`, "GEO record/metadata and processed data are **open**. **Raw sequencing reads
  are controlled access via dbGaP**"): accession resolves live, access-tier qualifier co-occurs in
  the same block → `per_accession = 1.0` for that entry. Concepts like "APOE carrier (E2+/E4+)"
  classify anchorable=true (gene_protein), resolve via HGNC to `APOE`, relevance=exact →
  `score=1.0`. A concept like a paper-local composite score would classify anchorable=false and
  drop out of the denominator, unpenalized.
- che26 (PROSPERO `CRD420261327845`, cohort table with no per-cohort accession, only named
  studies/authors): PROSPERO ID resolves → contributes 1.0 to `s_data`; the bare cohort names with
  no accession are not accession-pattern matches at all and are absent from the extracted universe,
  correctly reflected as thinner overall data-anchoring coverage than huu25's multi-accession block
  (fewer, not lower-scoring, entries — surfaced via the reported `n_accessions` count alongside the
  ratio, per §4).
- Abstract-only source (no accession, no cohort table, just "N=4,736 participants" per the §11
  floor case): `dataset_accessions = []`, `s_data = 0.15` floor — correctly distinguished from a
  genuine theory-paper exclusion, since this genre is data-driven but thinly compiled, not
  data-free.
