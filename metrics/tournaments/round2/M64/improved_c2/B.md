# M64 — Controlled-vocabulary & latent-space anchoring (cycle-2, expander B — built on exp3)

## Changes (cycle 2)

This revision starts from exp3 (cycle-1 rank 2, joint winner) and fixes the three weaknesses the
cycle-1 critique named for it, plus grafts the one idea from the losing exp2 design that the
critique explicitly told both winners to absorb:

1. **Genre-exclusion softness → redistribute-don't-exclude, with an active anti-gaming tripwire.**
   Cycle-1 exp3 handled a verified theory paper by dropping `S_data` from the weighted denominator.
   Mathematically that already behaves like redistribution (the surviving weight goes to
   `S_concept`), but the critique is right that the *framing* and the *verification discipline* were
   the weak point: "verified no dataset claim anywhere in ARA" was checked once, informally, with no
   deterministic cross-check, which leaves a gaming route (mislabel data-bearing work as
   theory-genre to dodge the 0.15/0.0 data floor). §4.1 below replaces this with an explicit
   **implied-data-without-provenance scan** (adapted from exp1's regex tripwire over `N=`, cohort,
   platform, sequencing, assay, corpus tokens in `claims.md`/`concepts.md`/`problem.md`/
   `solution/`) that must return clean *before* the genre exemption is granted, and the weight
   transfer itself is logged as an explicit `redistribution` event (not a silent `exclude` branch),
   so the audit trail shows the reallocation happened for a checked reason, not by default.
2. **Deterministic depth-from-root gate added (cuts LLM dependence, adds a second Goodhart wall).**
   Cycle-1 exp3 leaned on two LLM calls (anchorability classification, relevance check) to block
   generic-term gaming. §5.4a below inserts exp1's OLS4 `/ancestors` depth check as a deterministic
   pre-filter that runs *before* the LLM relevance call: any OLS4-sourced hit with match score < 70
   OR ontology depth-from-root < 3 is capped at `resolved_ambiguous` (0.4) without ever invoking the
   LLM. The LLM relevance check (§5.5) now only fires on hits that clear the deterministic gate,
   cutting LLM calls roughly in half on typical concept lists and making the "is this a trivial
   generic hit" call reproducible from cached ontology data alone.
3. **Cached-resolver-snapshot reproducibility specified.** Cycle-1 exp3 described live resolver
   calls with no reproducibility contract. §5.4b now requires every external call to be recorded in
   a per-ARA-run snapshot manifest (`{query, endpoint, http_status, response_hash, timestamp}`) and
   requires `m64_score` to accept an optional `resolver_cache`; a second run against the same
   manifest must reproduce a bit-identical score. Cache misses are distinguished from genuine
   `not_found` (as `resolution_error`, unchanged from cycle 1) and are additionally logged as
   `snapshot_incomplete` for tournament reproducibility audits.
4. **Grafted exp2's resolved-content semantic-match — and closed a gap exp3 didn't have this for at
   all.** Cycle-1 exp3 only ran a relevance/subject check on *concept* terms (§5.5); it had **no**
   subject-match check on *dataset accessions* — an accession could be a real, live, correctly-typed
   GEO/SRA/NCT ID for the *wrong* dataset (wrong species, wrong tissue, wrong cohort) and still score
   `1.0` under cycle-1 `score_data`, which only checked existence + access-tier co-occurrence. §5.6a
   adds a deterministic organism/tissue-token cross-check (context_line vs. resolved record summary)
   with an LLM fallback for ambiguous cases, on the exp2 0/1/2 model (`match`/`partial`/`mismatch`).
   A `mismatch` accession is now scored as `dead_or_mismatched`, which triggers the fabrication
   penalty in change 5 below rather than the flat 0.0 dead-link score.
5. **Fabrication punished strictly harder than omission, on both axes.** Cycle-1 exp3 scored a dead
   or non-existent accession/term at `0.0` — identical to what an honest zero-anchoring compile would
   floor to in the worst case, so "attempt and fail/fabricate" and "never attempted" were not
   distinguishable in the arithmetic. §5.6b/§5.7 introduce `FABRICATION_PENALTY = -0.15` applied to
   any accession or concept term classified `dead` (accession-shaped string, resolver reports
   not-found) or `dead_or_mismatched` (resolves but subject-check says mismatch), making its
   per-item contribution `-0.15` rather than `0.0`. This is bounded per item (floor `-0.15`, not
   unbounded) but is enough that one fabricated/mismatched accession among honest omissions pulls
   the mean below the honest-absence floor (0.15), and a section that is *entirely* fabricated
   entries goes negative before final clamping — the negative pre-clamp value is preserved in the
   audit log (`raw_score_prefloor`) even though the reported `m64_score` clamps at 0.0, so a
   tournament comparison between "said nothing" and "said something fake" is not lost to clamping.

Everything else — the anchorable-term-universe extraction run before resolution (Step 1), the
anchorability classification carve-out for paper-local constructs, the version-pin requirement for
reference genomes/embedding models, and the §4 penalize-don't-skip floors for absent/thin inputs —
is carried over from exp3 essentially unchanged, since the critique found no fault with them.

---

## 1. What this metric is actually measuring

M64 is an **interoperability** signal, not a correctness or completeness signal. Every other metric
on `data/dataset.md` / `logic/claims.md` / `logic/concepts.md` asks "is this true / thorough /
well-cited?" M64 asks a different question entirely: **can another agent, reading this ARA cold,
programmatically resolve its vocabulary and datasets to something outside the document itself?** An
ARA whose concepts and data are anchored to controlled vocabularies (MeSH, HGNC, UMLS, ChEBI, Cell
Ontology, OBI, DOID, SNOMED-CT), canonical dataset registries (GEO, SRA, dbGaP, ArrayExpress,
PROSPERO, ClinicalTrials.gov/NCT), or versioned/named latent spaces (a specific reference genome
build, a specific named+versioned embedding model) is one that a downstream agent can **cross-link**
without re-reading prose. An ARA that uses only free-text, un-anchored jargon is an epistemic
island: correct or not, it cannot be machine-linked to anything else.

This is why it ranked top-10 as **net-new vs. the ARA verifier**: the semantic verifier checks
internal consistency and grounding-to-source; it does not check whether the *terms themselves* point
outward to a resolvable external identifier space, and it does not check whether a resolvable
identifier actually refers to the *thing this paper means* rather than a same-shaped but different
referent. M64 is built to see exactly both.

### What it must reward
- Concept/claim terms that map to a **specific, resolvable identifier** in a real controlled
  vocabulary or registry (not just "this word appears in a dictionary somewhere").
- Dataset references that carry an **accession** (GEO, dbGaP, SRA, PROSPERO, NCT) rather than a bare
  description ("we used public RNA-seq data").
- **Version-pinned** latent/reference spaces — a genome build (GRCh38, not "the human genome"), a
  named+versioned embedding model/checkpoint, a specific ontology release — because an unversioned
  reference is not actually translatable.
- **Co-occurrence of identifier + access-tier statement** for data (per §11's own scoring axis): an
  anchored-but-access-opaque accession is only half-anchored for a downstream agent that needs to
  know if it can actually pull the data.
- **Subject-correct resolution**: a resolvable, live, well-typed accession or ontology hit is only
  worth full credit if the resolved record's subject (organism, tissue, disease, assay) matches what
  this ARA actually claims about it. A real ID pointing at the wrong thing is not anchoring; it's a
  false cross-link that would mislead a downstream agent that trusted it.

### What it must NOT reward
- Namedropping generic scientific words that happen to have *some* MeSH/UMLS entry (e.g. "cancer",
  "protein", "cell") — resolvability of trivial general vocabulary is not a signal of good science,
  it's a floor every paper clears for free. The metric gates on **relevance- and specificity-weighted**
  resolution, via a deterministic ontology-depth check first and an LLM sense-match check second (see
  §5.4a/§5.5).
- Fabricated-looking accessions or DOI-shaped strings that are never externally checked — anchoring
  must be **verified by an actual resolver call**, not by regex pattern-matching a GSE-shaped string
  and assuming it's real — and, new in this revision, a fabricated or subject-mismatched hit must
  score **strictly worse** than an honest non-attempt (§5.6b/§5.7).
- Over-tagging: an ARA that appends a long list of popular ontology terms unrelated to its actual
  claims to farm coverage. Anchor terms must be drawn from concepts.md's own genuine terms and
  claims.md's own cited Sources — never from an independently generated keyword list.
- Papers that legitimately have **no** anchorable vocabulary (pure theory/proof papers whose
  concepts are formal objects) being scored as if they failed an anchoring test they were never
  eligible to pass on the *concept* axis — but see §4 on penalize-don't-skip: this genre nuance
  changes the *interpretation* of a low score, not whether the metric computes one, and (new in this
  revision) the genre claim itself must clear a deterministic cross-check before it is trusted.

## 2. Failure modes / gaming routes

| Gaming route | Why it fails against this design |
|---|---|
| Paste real-looking but fake accessions (`GSE999999`) | Step 3 does a live (or cached-snapshot, §5.4b) resolver/registry call, not string matching; a dead accession is `dead`, scored at `FABRICATION_PENALTY = -0.15`, strictly worse than an honest omission (0.15 floor) — new in this revision, closing the gap where cycle-1 fabrication and cycle-1 omission both landed at the same 0.0. |
| Paste a real, live, correctly-typed accession for the wrong dataset/species/cohort | **New gap closed in this revision.** §5.6a runs a subject-match check (deterministic organism/tissue-token cross-check with LLM fallback) on every resolved accession, not just concept terms; a `mismatch` is `dead_or_mismatched` and takes the same `-0.15` penalty as a dead link — cycle-1 exp3 had no check here at all and would have scored this 1.0. |
| Pad concepts.md with generic anchorable words to inflate coverage | Step 2's [sem] relevance gate plus the new deterministic depth-from-root filter (§5.4a) require both an ontology-depth ≥3 hit AND a sense match to the ARA's own `Definition` field; a generic word either fails depth (capped at 0.4) or fails sense-match (0.0), and Step 5 still down-weights terms whose usage frequency in claims.md is near-zero. |
| Cite a vague/unversioned reference space to *look* anchored without being pin-precise | Step 3b explicitly checks for a version token; unversioned hits are capped at `resolved_ambiguous` (0.4), never `resolved_exact`. |
| Anchor only the *easy* boilerplate terms and leave the paper's actual novel-but-anchorable entities un-anchored | Coverage is computed over the anchorable-term *universe* extracted independently from concepts.md + claims.md before resolution is attempted (Step 1), so cherry-picking which terms to bother anchoring doesn't change the denominator. |
| Claim "latent space anchoring" via a proprietary/inaccessible embedding with no way for another agent to actually obtain the same space | Step 3c requires the space to be either (a) a named public checkpoint/artifact resolvable via a model registry lookup, or (b) accompanied by a public accession for the embedding weights/vectors themselves; unresolvable-in-practice claims score `not_resolved`. |
| Mislabel data-bearing work as "theory genre" to dodge the data-axis floor entirely | **New in this revision.** §4.1's implied-data-without-provenance scan runs a deterministic regex sweep over `claims.md`/`concepts.md`/`problem.md`/`solution/` for empirical-data tokens (`N=`, cohort, participants, sequencing, assay, corpus, dataset, platform) before any theory-genre exemption is granted; a hit overrides the exemption and forces the stricter "data implied but undescribed" floor (0.0, not the 0.15 absence floor — see §4.1), because implying data exists while describing none is worse than never mentioning data at all. |
| Re-run the metric hoping resolver flakiness randomly improves a borderline score | §5.4b's cached-resolver-snapshot manifest makes a given ARA-run's score reproducible from the recorded manifest; a fresh live run that disagrees with the snapshot is itself a flagged discrepancy for tournament auditing, not a free re-roll. |

## 3. Why hard to Goodhart, and composition with the suite

Hard to Goodhart because the score is gated on an **external, non-authorable resolution step** — the
paper's author (or the compiler) cannot make a term "more anchored" by writing better prose; they can
only do it by actually using the correct canonical identifier, which either resolves or doesn't, and
resolves *to the paper's own stated sense and subject* or doesn't. Cycle-2 adds a second,
non-LLM-authorable wall on top: ontology depth-from-root is a structural property of the ontology
graph itself (§5.4a), so an author cannot argue their way to a deeper node the way they might phrase
prose to sound more specific to an LLM grader. The subject-match check (§5.6a) closes the remaining
route where a real-but-wrong identifier could previously earn full credit. The fabrication-penalty
stacking (§5.6b) removes the expected-value incentive to gamble on a plausible-looking fake
accession, since a caught fabrication now costs more than never attempting. And because coverage is
computed over an independently-extracted term universe (Step 1, unchanged from exp3), gaming by
selective anchoring still doesn't move the number.

Composition: M64 sits orthogonally to (a) claims comprehensiveness/grounding metrics (internal
evidentiary support, not external resolvability), (b) data access-tier honesty metrics on §11 (is
access stated accurately, not whether the accession resolves at all or resolves to the right
subject — M64 subsumes "does the accession exist and refer to the right thing," leaving "is the
access tier honestly qualified" to its sibling metric; the two share raw extraction but score
different axes and should not double-penalize the same defect), and (c) novelty/FOL-ability metrics
on concepts.md (the near-opposite concern — anchoring rewards mapping to *existing* canonical space,
novelty rewards genuine new contribution; a well-designed ARA scores well on both by anchoring its
borrowed/standard vocabulary while its genuinely novel terms correctly score low on anchoring and
high on novelty). This keeps M64 a clean net-new axis rather than a restatement of any neighbor.

## 4. Penalize-don't-skip

Per the hard constraint, unavailability is itself an input, never an N/A. This cycle tightens the
genre-exemption path specifically (§4.1) while keeping the rest of exp3's floors, which the cycle-1
critique did not fault.

### 4.1 Data axis — redistribute, don't exclude, and verify before exempting (revised)

- **`data/dataset.md` absent, and no theory-genre claim**: `S_data = 0.15` (fixed floor, unchanged
  from cycle 1) — most ARAs describing empirical work should carry at least one anchorable accession
  or registered protocol, so bare absence is informative and scored low.
- **`data/dataset.md` present, with dataset descriptions but zero resolvable accessions**:
  `S_data = 0.0`, strictly below silent absence, because the compiler *had the chance* to anchor and
  produced nothing (unchanged from cycle 1).
- **`data/dataset.md` present, with one or more accessions that are `dead` or `dead_or_mismatched`**:
  each such entry contributes `FABRICATION_PENALTY = -0.15` to the per-accession average (§5.6b),
  which can push `S_data` below the 0.15 absence floor or even negative — new in this revision (see
  change 5).
- **Genuinely data-free genres (pure theory/proof papers)**: identified by cross-checking
  `logic/problem.md`/`solution/` for the presence of any empirical dataset reference at all. **New in
  this revision**: this check is now a two-part deterministic gate, not a single inference:
  1. *Absence check* (unchanged): no `data/` directory, and no external-dataset citation anywhere in
     `logic/solution/`.
  2. *Implied-data tripwire* (new): a regex sweep over `claims.md`, `concepts.md`, `problem.md`, and
     every file in `solution/` for empirical-data tokens — `\bN\s*=\s*\d+\b`, `cohort`, `participant`,
     `subjects?`, `sequencing`, `assay`, `corpus`, `dataset`, `platform`, `accession`. If this sweep
     is **clean** (no hits), the theory-genre exemption is granted: `S_data` is reported as
     `n/a (genre-verified: no data/ directory, no external-dataset citation in solution/, and no
     empirical-data token found in claims.md/concepts.md/problem.md/solution/ — see audit log for
     full token sweep)`, and its weight (0.55) is **redistributed** to `S_concept` (weight becomes
     1.0). This redistribution is logged as an explicit `redistribution` event in the output object
     (`weight_redistribution: {"from": "s_data", "to": "s_concept", "amount": 0.55, "reason":
     "genre-verified theory, implied-data sweep clean"}`), not a silent renormalization, so the
     audit trail shows *why* the weight moved rather than presenting a bare 1-component average.
  2b. If the implied-data sweep instead **fires** (any token match) while `data/dataset.md` is still
     absent, the theory-genre exemption is **denied** regardless of what the compiler or a prior pass
     claimed: this is treated as *data implied but undescribed*, scored `S_data = 0.0` (the
     present-but-unaccessioned floor, not the 0.15 absence floor), because implying empirical work
     exists without describing it at all is a worse compile defect than never mentioning data — an
     author can't dodge the data axis by mislabeling the genre while `claims.md` still talks about
     `N=312 participants`.
- This closes the cycle-1 critique's "leans toward skip" finding: the genre exemption is never
  granted by default or by a single soft inference — it requires a clean deterministic sweep, it is
  reported as an explicit weight *redistribution* (matching exp1's framing) rather than a denominator
  *exclusion*, and a false theory claim is automatically caught and penalized rather than trusted.

### 4.2 Concept axis (unchanged from exp3)

- **`concepts.md` has fewer than 3 genuinely anchorable terms**: still compute `S_concept` over
  whatever universe exists (even n=1); the aggregator reports raw counts alongside the ratio so a
  downstream reviewer can distinguish "3/3 anchored, high confidence" from "1/1 anchored, low
  confidence" without the metric itself collapsing to N/A.

### 4.3 Resolver failure (unchanged from exp3, reproducibility contract added in §5.4b)

- **Resolver call fails/times out (network/API unavailable)**: scored as `not_resolved` (0.0) for
  that term, logged distinctly as `resolution_error` vs. genuine `not_found`, contributes to the
  denominator either way, and (new) is additionally recorded as `snapshot_incomplete` in the
  resolver-cache manifest so a degraded-tool-access run is flagged for tournament reproducibility
  review rather than silently accepted as a clean score.

## 5. Generation / compute workflow

### 5.1 Inputs (exact artifact fields) — unchanged from exp3
- `data/dataset.md`: all `## {Accession} — ...` block headers, `**Source / access**` strings,
  `## Included cohorts` table (`Source study` / registration numbers), `## External datasets used`
  bullets.
- `logic/concepts.md`: every `## {Term Name}` heading + its `**Notation**`, `**Definition**`,
  `**Related concepts**` fields.
- `logic/claims.md`: every `**Sources**` entry's `<value>` and `«verbatim quote»`, plus `**Tags**`
  per claim.
- **New**: `logic/problem.md` and every file in `logic/solution/` — read for the implied-data
  tripwire (§4.1) only; not otherwise part of the anchoring universe.

### 5.2 Step 1 — Extract candidate anchor universe (deterministic + regex) — unchanged from exp3

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
            line_start = dataset_md.rfind("\n", 0, m.start()) + 1
            line_end = dataset_md.find("\n", m.end())
            line = dataset_md[line_start: line_end if line_end != -1 else None]
            hits.append({"registry": source, "id": m.group(0), "context_line": line})
    return hits

def extract_concept_terms(concepts_md: str) -> list[dict]:
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

### 5.2b Step 1b — Implied-data tripwire (new, deterministic)

```python
IMPLIED_DATA_TOKENS = re.compile(
    r"\bN\s*=\s*\d+\b|\bcohorts?\b|\bparticipants?\b|\bsubjects?\b|\bsequencing\b|"
    r"\bassay\b|\bcorpus\b|\bdatasets?\b|\bplatform\b|\baccessions?\b", re.I)

def implied_data_sweep(claims_md: str, concepts_md: str, problem_md: str,
                        solution_files: dict[str, str]) -> dict:
    hits = {}
    for label, text in {"claims.md": claims_md, "concepts.md": concepts_md,
                         "problem.md": problem_md, **solution_files}.items():
        found = IMPLIED_DATA_TOKENS.findall(text)
        if found:
            hits[label] = sorted(set(m.lower() for m in found))
    return {"clean": not hits, "hits_by_file": hits}
```

### 5.3 Step 2 — [sem] anchorability + relevance classification (LLM call, per concept term) — unchanged from exp3

For every extracted concept term, one LLM call classifies whether it *should* be anchorable and, if
so, to which vocabulary family — this runs before any external resolver call, to avoid wasting
resolver budget on genuinely paper-local constructs (which must NOT be penalized).

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
excluded from the anchoring denominator entirely (the deliberate genre-fairness carve-out — a novel
construct is not an anchoring failure).

### 5.4 Step 3 — [ext] resolver calls, per anchorable term / accession — unchanged dispatch table from exp3

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
| GEO/SRA/dbGaP/ArrayExpress/NCT/PROSPERO accessions | Direct registry existence check: GEO `acc.cgi?acc={id}&targ=self&form=text&view=quick`, NCBI Entrez `esearch`/`esummary` (SRA/dbGaP), ClinicalTrials.gov API v2 `GET /studies/{nct_id}`, PROSPERO search page lookup by CRD number |

#### 5.4a Step 3.5 — Deterministic depth-from-root gate (new, adapted from exp1)

For every OLS4-sourced hit (disease_phenotype, chemical_compound, cell_type, assay_instrument,
statistical_method families), before any LLM relevance call:

```python
def ols4_specificity_gate(hit: dict) -> dict:
    """
    hit = {"ols4_score": float, "iri": str, "ontology": str}
    Calls OLS4 /api/ontologies/{ontology}/terms/{iri}/ancestors
    and counts ancestor path length to the ontology root.
    """
    depth = ols4_ancestor_depth(hit["ontology"], hit["iri"])  # thin HTTP wrapper, cached (5.4b)
    specific = hit["ols4_score"] >= 70 and depth >= 3
    return {
        "specific": specific,
        "depth": depth,
        "gate": "pass_deterministic" if specific else "weak_match_capped",
    }
```

- `specific = True` → hit proceeds to the LLM relevance check (§5.5) for a final sense-match verdict.
- `specific = False` → hit is capped at `resolved_ambiguous` (0.4) **without invoking the LLM at
  all** — this is a purely structural property of the ontology graph (a term one hop from root, e.g.
  a bare "disease" or "cell" node, cannot be a specific technical sense no matter how the LLM might
  be prompted), so it is both cheaper and non-authorable by prose quality.
- Non-OLS4 families (gene_protein, reference_genome_build, embedding_model, raw accessions) have no
  ontology-depth concept and skip this gate, proceeding directly to their existing exact-match /
  version-token checks (§5.5 relevance still applies to gene_protein hits, since gene symbols can
  still collide with unrelated senses in rare cases).

#### 5.4b Cached-resolver-snapshot reproducibility (new)

```python
def resolve_term(term: dict, resolver_cache: dict | None = None) -> dict:
    """
    resolver_cache: optional {(endpoint, query): {"http_status": int, "body_hash": str,
                     "body": str, "timestamp": str}} snapshot manifest.
    Dispatch order:
      1. If (endpoint, query) is in resolver_cache, use the cached response verbatim
         (bit-identical re-run guarantee).
      2. Else make the live call, then WRITE the result into resolver_cache under the
         same key before returning, so a fresh run produces a new complete manifest.
      3. If the live call fails/times out, record status "resolution_error" AND flag
         "snapshot_incomplete": true in the manifest entry (see §4.3).
    Returns the best-match hit (or None) plus its definition/summary text for the
    relevance check, and whether a version token was present for build/model-type
    families. (Registry dispatch per §5.4 table; implementation is a thin HTTP wrapper,
    omitted here since it is pure I/O, not scoring logic.)
    """
    raise NotImplementedError("registry dispatch + cache — see table above and 5.4b contract")
```

A tournament re-score against a saved `resolver_cache` manifest must reproduce the identical
`m64_score` output; any live re-run that disagrees with a prior manifest is itself flagged
(`manifest_drift`) for review rather than silently accepted as the new truth.

### 5.5 Step 4 — [sem] relevance check (LLM call, only for terms that clear §5.4a or lack a depth concept)

**Exact prompt:**
```
Term as used in this paper: "{name}" — "{definition}"
Candidate external match found: "{resolved_id}" — "{resolved_summary}"

Does the external match refer to the SAME specific concept as used in this paper
(not just a superficially similar or more generic sense)? Answer strictly as JSON:
{ "match": "exact" | "partial" | "mismatch", "reason": "<one sentence>" }
```

### 5.6 Step 5 — Deterministic scoring (revised)

#### 5.6a Data-accession subject-match check (new)

```python
ORGANISM_TISSUE_TOKENS = re.compile(
    r"\bhuman\b|\bmouse\b|\bmm10\b|\bGRCh3[78]\b|\bpostmortem\b|\bplasma\b|\bbrain\b|"
    r"\bblood\b|\btumor\b|\bcell line\b", re.I)

def accession_subject_match(context_line: str, resolved_summary: str) -> dict:
    """
    Deterministic first pass: extract organism/tissue tokens from both the ARA's own
    context_line (surrounding the accession in dataset.md) and the resolver's returned
    summary text; if both are non-empty and disjoint, it's a deterministic mismatch.
    If either side is empty or the token sets overlap, escalate to the same LLM
    match-check schema as Step 4 (0/1/2-style: exact/partial/mismatch) using the
    context_line as "term as used" and resolved_summary as "candidate match" — this is
    exp2's resolved-content semantic-match, grafted onto the data axis where cycle-1
    exp3 had no subject check at all.
    """
    ctx_tokens = set(t.lower() for t in ORGANISM_TISSUE_TOKENS.findall(context_line))
    res_tokens = set(t.lower() for t in ORGANISM_TISSUE_TOKENS.findall(resolved_summary))
    if ctx_tokens and res_tokens and ctx_tokens.isdisjoint(res_tokens):
        return {"match": "mismatch", "reason": "deterministic organism/tissue token disjoint set"}
    return None  # signal: escalate to LLM relevance check, same prompt shape as Step 4
```

#### 5.6b Scoring with fabrication-penalty stacking (revised)

```python
FABRICATION_PENALTY = -0.15

def score_term(anchorable_term: dict, resolution: dict | None, relevance: dict | None,
                gate: dict | None, versioned: bool) -> float:
    if resolution is None or not resolution.get("exists", False):
        return FABRICATION_PENALTY if resolution is not None and resolution.get("attempted_as_real_id") \
            else 0.0  # dead: an accession/ID-shaped string that was checked and doesn't exist
                      # scores the fabrication penalty; a term correctly classified
                      # anchorable=false never reaches this function at all (excluded upstream)
    if relevance is not None and relevance["match"] == "mismatch":
        return FABRICATION_PENALTY  # dead_or_mismatched: resolves, but to the wrong thing
    if gate is not None and not gate["specific"]:
        return 0.4  # resolved_ambiguous, deterministic cap, no LLM needed
    if relevance is None:
        return 0.0  # resolver hit but no relevance check available -> unverified, 0
    if relevance["match"] == "partial":
        return 0.4  # resolved_ambiguous
    return 1.0 if versioned or anchorable_term["vocabulary_family"] not in (
        "reference_genome_build", "embedding_model") else 0.4


def score_concepts(concept_terms: list[dict]) -> tuple[float, dict]:
    anchorable = [t for t in concept_terms if t["anchorable"]]
    if not anchorable:
        return None, {"note": "no anchorable terms in concepts.md — see §4.1 genre handling for "
                               "whether this triggers redistribution"}
    scores = [score_term(t, t["resolution"], t["relevance"], t.get("gate"), t["versioned"])
              for t in anchorable]
    return sum(scores) / len(scores), {"n_anchorable": len(anchorable), "raw_scores": scores}


def score_data(dataset_accessions: list[dict]) -> tuple[float, float]:
    """Returns (clamped_score, raw_prefloor_score) — raw is preserved for audit per change 5."""
    if not dataset_accessions:
        return 0.15, 0.15  # floor for present-but-unaccessioned data section; see §4.1
    per_accession = []
    for acc in dataset_accessions:
        exists = acc["resolution"]["exists"]
        subject = acc.get("subject_match")  # from 5.6a, deterministic or LLM-escalated
        has_access_tier = bool(re.search(
            r"\b(open|controlled|restricted|by[- ]request|embargo)\b",
            acc["context_line"], re.I))
        if not exists:
            per_accession.append(FABRICATION_PENALTY)  # dead accession-shaped string
        elif subject is not None and subject["match"] == "mismatch":
            per_accession.append(FABRICATION_PENALTY)  # dead_or_mismatched, new in this revision
        elif has_access_tier:
            per_accession.append(1.0)
        else:
            per_accession.append(0.6)  # resolves + subject OK, access-tier ambiguity not stated inline
    raw = sum(per_accession) / len(per_accession)
    return max(raw, 0.0), raw  # clamp for the headline score; raw kept for audit/tournament use


def m64_score(dataset_md: str, concepts_md: str, claims_md: str, problem_md: str,
              solution_files: dict[str, str]) -> dict:
    accessions = extract_dataset_accessions(dataset_md)
    concept_terms = extract_concept_terms(concepts_md)
    # ... classify each concept term via Step 2, resolve anchorable ones + accessions via
    #     Step 3/3.5 (with resolver_cache per 5.4b), relevance-check via Step 4,
    #     subject-match accessions via 5.6a ...

    s_concept, concept_meta = score_concepts(concept_terms)

    sweep = implied_data_sweep(claims_md, concepts_md, problem_md, solution_files)
    theory_genre_absence_verified = (not dataset_md) and no_external_dataset_cited(solution_files)

    if theory_genre_absence_verified and sweep["clean"]:
        s_data, data_meta = None, {
            "note": "n/a (genre-verified: no data/ directory, no external-dataset citation, "
                    "implied-data token sweep clean — see audit log)",
            "sweep": sweep,
        }
        weight_redistribution = {"from": "s_data", "to": "s_concept", "amount": 0.55,
                                  "reason": "genre-verified theory, implied-data sweep clean"}
    elif theory_genre_absence_verified and not sweep["clean"]:
        # tripwire fired: genre claim overridden, treat as data-implied-but-undescribed
        s_data, data_meta = 0.0, {"note": "data implied but undescribed — genre exemption denied",
                                   "sweep": sweep}
        weight_redistribution = None
    else:
        s_data, raw_prefloor = score_data(accessions)
        data_meta = {"n_accessions": len(accessions), "raw_score_prefloor": raw_prefloor}
        weight_redistribution = None

    if s_data is None:
        final = s_concept if s_concept is not None else 0.1  # both excluded: floor, never N/A
        weights_used = {"s_concept": 1.0}
    else:
        vals, weights = [s_data], [0.55]
        if s_concept is not None:
            vals.append(s_concept); weights.append(0.45)
        wsum = sum(weights)
        final = sum(v * w for v, w in zip(vals, weights)) / wsum
        weights_used = {"s_data": weights[0] / wsum,
                         **({"s_concept": weights[1] / wsum} if s_concept is not None else {})}

    return {
        "m64_score": round(max(final, 0.0), 3),
        "s_data": s_data, "data_meta": data_meta,
        "s_concept": s_concept, "concept_meta": concept_meta,
        "weights_used": weights_used,
        "weight_redistribution": weight_redistribution,
    }
```

### 5.7 Worked examples (revised to show the new mechanics)

- **huu25** (`GSE307990`, "GEO record/metadata and processed data are **open**. **Raw sequencing
  reads are controlled access via dbGaP**"): accession resolves live, `context_line` says "human,
  postmortem" and the resolved GEO summary also says "Homo sapiens, entorhinal cortex" →
  `subject_match: exact`, access-tier qualifier co-occurs → `per_accession = 1.0`. "APOE carrier
  (E2+/E4+)" classifies anchorable=true (gene_protein), resolves via HGNC to `APOE`, relevance=exact
  → `score=1.0`. A paper-local composite score classifies anchorable=false and drops out of the
  denominator, unpenalized. Unchanged from cycle 1 — the new checks don't touch a correctly-anchored
  case.
- **che26** (PROSPERO `CRD420261327845`): PROSPERO ID resolves, `context_line` and resolved record
  both reference the same review title/cohort set → `subject_match: exact`, contributes 1.0 to
  `s_data`. Unchanged from cycle 1.
- **New adversarial case — subject mismatch**: suppose a compiled ARA cites `GSE307990` (a real,
  live human-brain accession) while describing a mouse-tissue experiment in its own prose. §5.6a's
  deterministic organism-token check finds `{human, postmortem, brain}` on the resolver side and
  `{mouse}` in `context_line` — disjoint sets → `subject_match: mismatch` without needing an LLM
  call. `score_data` assigns this accession `FABRICATION_PENALTY = -0.15`; if it is the only
  accession in the ARA, `s_data = -0.15` raw, clamped to `0.0` for the headline `m64_score` but
  `raw_score_prefloor: -0.15` is preserved in `data_meta` for audit — strictly worse than an honest
  abstract-only compile with `s_data = 0.15`. Cycle-1 `score_data` would have scored this `1.0`
  (existence + access-tier only), the exact gap the cycle-1 critique flagged against exp1/exp2.
- **New adversarial case — genre mislabeling caught**: suppose a compiler labels an ARA "theory" and
  omits `data/dataset.md`, but `claims.md` still states "N=312 participants were assessed by the
  novel index." The implied-data sweep (§4.1/§5.2b) fires on `N=312` and `participants`; the theory
  exemption is denied; `S_data` is forced to `0.0` (data-implied-but-undescribed) rather than the
  0.15 absence floor or a silent `n/a`. Cycle-1 exp3's single informal "verified no dataset claim"
  check had no mechanism to catch this.
- **Abstract-only source** (no accession, no cohort table, just "N=4,736 participants"):
  `dataset_accessions = []`, and the implied-data sweep fires on `claims.md`'s `N=4,736` token — but
  since `data/dataset.md` is *not* absent here (it exists, just thin/abstract-only), the theory-genre
  branch never applies in the first place; this correctly falls through to `score_data([]) = 0.15`,
  the ordinary present-but-thin floor, not the stricter 0.0 — the tripwire in §4.1 only overrides a
  *claimed absence*, it does not further penalize an honestly-thin-but-present `dataset.md`.
