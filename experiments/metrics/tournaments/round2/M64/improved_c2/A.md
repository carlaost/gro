# M64 — Controlled-vocabulary & latent-space anchoring (cycle 2, improved)

## Changes (cycle 2)

Base: exp1 (RANK 1, cycle-1 winner). This revision fixes the three weaknesses the cycle-1 critique
named against exp1, grafts the one idea it told exp1 to absorb from exp2, and keeps every mechanism
the critique praised (§1.4's redistribute-don't-exclude reconciliation, the OLS4 depth-from-root
specificity gate, fabrication-worse-than-omission, cached-snapshot determinism) unchanged in spirit.

1. **Coverage denominator over an independently-extracted term universe** (adopted from exp3 Step 1,
   per critique weakness (a): "score is a mean of weighted candidates, so a paper anchoring one term
   perfectly ties one anchoring twenty… selective-anchoring gaming isn't blocked"). New **Step 1**
   below enumerates the *full* anchorable-term universe from §2/§3/§11 *before* any resolution is
   attempted, runs a deterministic-schema anchorability classification pass to exclude genuinely
   paper-local/novel constructs (genre-fair, cached, not a silent drop), and requires every surviving
   universe entry to be carried through resolution — including entries the compiler never bothered to
   try, which now score `not_attempted` (Tier D, weight 0) instead of being invisible to the mean. A
   compiler can no longer inflate its average by anchoring the one easy term and ignoring nineteen
   hard ones; the raw universe count and denominator are reported alongside the ratio for auditability.
2. **Resolved-content semantic-match, closing the shallow-"resolved" gap** (adopted from exp2, per
   critique weakness (b): "a real GEO accession for the wrong dataset/species scores Tier A"). New
   **Step 2b** below runs a cheap deterministic keyword-overlap check between the resolved record's
   metadata and the ARA's own stated context (species, disease, assay, cohort) for every `resolved`
   accession; only when that check is genuinely ambiguous does it escalate to a single cached,
   temperature-0 LLM call returning exp2's 0/1/2 integer. This adds a new tier, **A− (context-
   ambiguous)**, and a new penalty, **`CONTEXT_MISMATCH_PENALTY`**, that is deliberately sized between
   "no penalty" (a genuinely resolved, genuinely matching accession) and `FABRICATION_PENALTY` (a
   dead/fake ID) — exactly the placement the critique asked for: a real-but-wrong-context ID is worse
   than a clean resolve but not as bad as a hallucinated one.
3. **An explicit latent-space/version-pin branch** (adopted from exp3's HF-registry + build-token
   idea, per critique weakness (c): "the metric name demands it and exp1 currently has no
   latent-space branch"). New candidate type in **Step 1** and resolution branch in **Step 2c** below
   cover named genome/reference-space builds (GRCh38, hg19, MNI152, T2T-CHM13, …) and named pretrained
   model/embedding checkpoints (HuggingFace Hub lookups), and — mirroring exp3 — draw a hard line
   between a *versioned/pinned* reference (full credit) and a *generic, unversioned* one ("the human
   genome", a model name with no revision/commit), which is capped at the new **A− (unpinned-latent)**
   tier rather than silently scored as fully resolved.

Everything else — the §1.2–§1.6 reasoning, the OLS4 depth-from-root gate, the definitional-relevance
padding discount, the implied-data-without-provenance check, the access-tier honesty check, and the
"why hard to Goodhart" framing — is retained and only re-numbered/extended where the three fixes above
touch it. Section numbers below match the original where unchanged so this reads as a diff-able
superset, not a rewrite.

---

## 1. Expanded reasoning

### 1.1 What it signals
An ARA is only as useful to a downstream agent as its ability to be *linked* — to other ARAs, to
public registries, to reasoning engines that operate over canonical identifiers rather than prose.
M64 asks: when this artifact names a dataset, a variable, a biomarker, a method, a reference
coordinate space, or a construct, did the compiler give it a handle that resolves outside this one
document — a real accession, a canonical-registry name, a versioned reference build, or a term that
maps onto a controlled ontology/vocabulary class — or did it leave every reference as free-floating
natural language that only a human (or an LLM re-reading the whole ARA) can disambiguate?

This is a **good-science** signal, not a cosmetic one, for three reasons:
1. **Falsifiability requires a shared referent.** A claim like "p-tau217 outperforms p-tau181" is only
   checkable against outside evidence if "p-tau217" resolves to the same analyte everyone else means
   by that string (a `ChEBI`/`UniProt`/`MeSH` sense) rather than an author-local shorthand — and, per
   fix (2) below, only if the *resolved record itself* is actually about the analyte/cohort/species the
   ARA claims, not merely an ID that happens to parse.
2. **Reproducibility requires resolvable data and resolvable computational context.** A GEO/dbGaP/
   ClinicalTrials.gov/PROSPERO identifier is the difference between "a downstream agent can *fetch*
   this dataset and check the number" and "a downstream agent has to trust the prose" — and a pinned
   genome build or model checkpoint is the difference between "a downstream agent can *reproduce this
   exact computation*" and "a downstream agent gets a plausibly-similar-but-different result."
3. **Cross-ARA linking is a compounding asset.** Every anchored term is a join key the corpus can use
   later (find every ARA touching MONDO:0004975 / Alzheimer disease; every ARA reusing GSE307990;
   every ARA built on GRCh38). Unanchored prose is a dead end for that use case even if the science
   inside is sound.

### 1.2 What it must reward
- **Live-resolvable external identifiers**: GEO (`GSE\d+`), dbGaP (`phs\d+`), SRA, ArrayExpress
  (`E-\w{4}-\d+`), EGA (`EGA[SD]\d+`), PRIDE (`PXD\d+`), ClinicalTrials.gov (`NCT\d{8}`), PROSPERO
  (`CRD\d+`) — anywhere they appear (§11 accession blocks, §2 claim Sources, §3 concept definitions)
  — **and whose resolved record's subject matches the ARA's stated context** (species, disease, assay,
  cohort — see Step 2b). A resolved-but-mismatched ID no longer earns the same credit as a resolved-
  and-confirmed one.
- **Ontology-class matches for genuine technical vocabulary** in §3 (`concepts.md`): a `Notation`/
  `Definition` pair that maps onto a specific, non-root class in MeSH/UMLS/GO/HPO/MONDO/ChEBI/UBERON/
  NCBITaxon/EDAM/STATO/UO — not a match to a near-root generic class ("disease", "process"), which is
  gameable and near-worthless.
- **Named canonical datasets/cohorts** used off the shelf (ADNI, UK Biobank, TCGA, GTEx, BioFINDER,
  TRIAD, MIMIC, ...) even when they don't carry a fresh accession in *this* ARA, because they are
  independently locatable.
- **Versioned/pinned reference-space and model anchors (NEW — latent-space branch)**: a genome or
  atlas build named with its version token (GRCh38, hg19, T2T-CHM13, MNI152, fsaverage6, ...), or a
  named pretrained model/embedding checkpoint accompanied by a resolvable revision/commit/version tag
  (e.g. a HuggingFace `model@revision` or an explicit checkpoint hash). This is the metric's literal
  "…and latent-space anchoring" half, and it is scored on the same live/versioned-resolution logic as
  the accession branch, not merely gestured at.
- **Access-tier honesty co-occurring with the anchor** (per `11_dataset.md`'s own scoring axis): an
  anchor that also states its resolvability class (open / controlled-access-via-dbGaP / by-request) is
  worth more than a bare identifier with an implied-but-unstated access claim, because it tells the
  downstream agent *how* to actually use the link.
- **Coverage, not just quality (NEW)**: an ARA that anchors most of its independently-extracted
  anchorable-term universe scores better than one that anchors a handful of easy terms and leaves the
  rest as prose, even if the anchored subset in both cases resolves cleanly. Quality-per-anchor and
  breadth-of-anchoring are now scored as genuinely separate contributions (Step 1 + Step 7).

### 1.3 What it must NOT reward
- **Keyword stuffing / tag padding.** A long `Tags:` list in `claims.md` or an inflated `concepts.md`
  is not "more anchoring" — each candidate must independently resolve *and* cross-reference into the
  claims layer to earn full weight (Step 4); unresolved padding must not raise the count of
  opportunities in the denominator for free (see §1.5/§2.4 anti-gaming), and generic-but-technical-
  sounding padding that *does* resolve is caught by the specificity depth-filter, which now drags such
  entries into Tier D rather than merely failing to help.
- **Fabricated-looking identifiers.** A string that has the *shape* of an accession (regex-plausible)
  but does not resolve against the live registry is worse than no attempt — it is either a
  hallucination or a typo, and both are compiler defects the metric must catch, not reward for
  "trying."
- **A real identifier borrowed from the wrong record (NEW).** An accession that *does* resolve on the
  live registry but whose resolved content is about a different species/disease/cohort than the ARA
  claims is not "anchoring" — it is a context mismatch that is arguably more misleading than an
  unresolved string, because it looks correct on casual inspection. This must be caught (Step 2b) and
  penalized distinctly from clean fabrication, not silently awarded Tier A.
- **Generic, unversioned reference-space claims (NEW).** Naming "the human genome" or a model family
  by bare name with no build/revision is not latent-space anchoring in the sense this metric rewards —
  it is not falsifiable to a specific, reproducible computational artifact, and must be capped below
  full credit (Step 2c).
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
- **Selective anchoring (NEW).** Anchoring one or two easy terms while leaving the paper's harder,
  more load-bearing vocabulary and dataset references unanchored must not average out to a comfortable
  score. The coverage denominator (Step 1) exists specifically to close this route.

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

**Extension for the coverage denominator and the anchorability classifier (NEW).** The same
redistribute-don't-exclude discipline applies to the two new mechanisms so they cannot reopen a
skip-shaped hole:
- The anchorability classifier (Step 1b) *excludes* an entry from the denominator only when it is
  classified `PAPER_LOCAL_NOVEL` — never for "hard to resolve" or "resolver unavailable." A term the
  resolver fails on stays in the denominator as a Tier-D `not_attempted`/`no_match` entry; it is not
  quietly removed. This is the load-bearing difference between "genre-fair exclusion" and "skip."
- If every single universe entry is classified `PAPER_LOCAL_NOVEL` (a degenerate, vanishingly rare
  case — e.g. a pure-notation theory paper whose entire vocabulary is self-defined), the denominator
  is 0; the function returns the score floor (0.0) with an explicit
  `denominator_degenerate_all_paper_local` flag rather than N/A. This is structurally identical to the
  pre-existing "empty candidate list" floor case in §2.3 and is exercised through the same code path.
- The latent-space branch (Step 2c) never treats "the ARA doesn't mention any model/genome build" as a
  defect — it only fires, and only penalizes via the unpinned-tier cap, when such a reference *is*
  present but *unversioned*. Absence of any latent-space reference at all is genre-neutral, exactly
  like §11 absence for theory papers.

### 1.5 Failure modes / gaming routes and how the design blocks them
| Gaming route | Countermeasure |
|---|---|
| Stuff `Tags:`/concept headings with generic-but-ontology-matchable words | Specificity filter rejects near-root/generic ontology hits (§2.3); only non-trivial-depth classes count, and generic hits that resolve at shallow depth now land in Tier D within the mandatory denominator, actively lowering the score rather than merely failing to raise it |
| Paste a fake/expired/mistyped accession that *looks* valid | Live resolver call required — unresolved-but-well-formed IDs score **worse** than no ID (flag: `malformed_or_dead_id`), not neutral |
| Claim "open access" without naming what's actually open vs. gated | Access-tier co-occurrence check (§2.5/Step 6) requires the qualifier to name a scope (raw vs. processed vs. metadata) |
| Inflate `concepts.md` with borrowed textbook terms to raise anchor count | Only concepts whose `Definition` demonstrably does definitional work for this paper's claims (cross-referenced against `claims.md` Tags/Statement) get full weight; purely decorative entries get a discount multiplier (Step 4) |
| Hide a real data-driven study behind a thin/absent `data/dataset.md` | Implied-data-scan (§1.4) forces a penalty even without a populated §11 to inspect |
| **(NEW) Anchor the one or two easy terms, leave the paper's harder vocabulary/dataset references as unlinked prose** | Coverage denominator (Step 1) is built from an independently-extracted universe *before* resolution is attempted; every surviving universe entry must be carried through Step 2 and lands in the mean (as Tier D if never attempted), so selective anchoring can no longer buy a high average |
| **(NEW) Borrow a real, live-resolving accession that actually belongs to a different dataset/species/cohort** | Resolved-content semantic-match (Step 2b): cheap deterministic keyword-overlap against the ARA's stated context, escalating to a cached single-call 0/1/2 LLM check only when genuinely ambiguous; confirmed mismatches drop to Tier D and incur `CONTEXT_MISMATCH_PENALTY`, distinct from and smaller than `FABRICATION_PENALTY` |
| **(NEW) Claim latent-space/reference-space anchoring by naming a model or genome generically, with no way to actually reproduce the referenced computational context** | Version-pin requirement (Step 2c): unversioned genome-build/model-family mentions are capped at Tier A− (`resolved_ambiguous`/`resolved_unpinned`, weight 0.55), never the full 1.0 a genuinely pinned reference earns |
| **(NEW) Mislabel genuinely anchorable field vocabulary as "our novel construct" to dodge the coverage requirement** | Anchorability classification (Step 1b) requires explicit paper-local-novelty textual markers ("we introduce/propose", a claimed-novel name) *and* absence from the seed known-vocabulary lists before excluding a term; classification is logged with its rationale span, so a compiler mislabeling common field terms as novel is itself an auditable, reviewable defect (not a silent free pass), and the same classifier call is cached/deterministic (temperature 0) so it cannot be gamed by re-running until a favorable label appears |

### 1.6 Relationship to assessment-critique notes / why net-new
This metric was ranked top-10 specifically as **net-new relative to the ARA verifier**: the verifier's
grounding checks (Rule 16, `Sources` quote discipline) confirm a number is *internally* traceable to
an evidence file — they say nothing about whether the *entity itself* (the dataset, the analyte, the
construct, the reference space) is externally *resolvable*, and nothing about whether an externally
resolvable ID actually points at the *right* record. M64 adds the interoperability axis (can another
ARA, another agent, or a registry lookup act on this reference, and does it act on the *correct* one)
rather than duplicating the internal-consistency axis other metrics already own. To keep that edge
tight, this workflow deliberately does **not** re-score `Sources`-quote presence, claim/evidence
matching, or `Interpretation` vs. `Evidence basis` separation — those belong to grounding-family
metrics. It only scores resolvability/translatability/context-fidelity of the referents once they're
already assumed present.

---

## 2. Generation / compute workflow

### 2.1 Inputs (artifact fields consumed)
From the ARA under evaluation (root `research/ara-library/<ara-id>/`):
- `data/dataset.md` (§11) — if present: accession blocks (`Source / access`, `Size / content`, `Key
  variables`), `Included cohorts` table, `External datasets used` bullets, `Provenance and access`.
- `logic/concepts.md` (§3) — every `## {Term}` heading + its `Notation` and `Definition` fields.
- `logic/claims.md` (§2) — every claim's `Tags` field and the `Statement`/`Evidence basis` text (for
  accession-shaped substrings, named-cohort mentions, and reference-space/model mentions that leak
  into claim prose).

### 2.2 Step-by-step procedure

**Step 0 — Parse.** Split each file into its structural blocks per the documented shapes (accession
blocks / cohort table rows for §11; concept sections for §3; claim blocks for §2). Record, per source
field, the raw text span it came from (for auditability).

**Step 1 — Universe extraction (independently-extracted, pre-resolution) [REVISED — coverage fix].**
Build the full anchorable-term *universe* before any resolution is attempted, so the denominator can
never be shaped by which terms happen to resolve easily:
- *Concept universe*: every `## {Term}` heading in §3, paired with its `Notation`.
- *Tag/claim universe*: every distinct (case-insensitive, deduplicated) `Tags` entry across all §2
  claims, plus any accession-shaped or named-canonical-dataset substring found in `Statement`/
  `Evidence basis` text that isn't already a Tag.
- *Dataset universe* (if §11 present): every accession-block header, every `Included cohorts` table
  row's `Cohort`/`Source study` pair, every `External datasets used` bullet.
- *Reference-space / latent-space universe (NEW)*: every regex/keyword hit for a genome or atlas build
  token (`GRCh3[67]`, `GRCh38`, `hg19`, `hg38`, `T2T-CHM13`, `MNI152`, `Talairach`, `fsaverage\d*`, ...)
  or a named pretrained model / embedding checkpoint mention (proper-noun model family names adjacent
  to "model", "checkpoint", "embedding", "pretrained", "fine-tuned"), wherever they appear in §2/§3
  (and §11/method cross-references if the model or build is used to *process* the dataset).
- Every universe entry is recorded with its raw text, source field, and a stable id (for later
  candidate-to-universe joins). `N_universe` = total deduplicated entries.

**Step 1b — Anchorability classification [ext: deterministic-schema classifier, cached, temperature 0]
[NEW].** For each universe entry, classify as exactly one of:
- `EXTERNAL_ANCHORABLE` — plausibly refers to an entity with an external registry/ontology/reference-
  space counterpart (named disease, biomarker, assay, gene, drug, standard measure, dataset, cohort,
  genome build, pretrained model, ...). Default classification.
- `PAPER_LOCAL_NOVEL` — the paper's own coined construct, score, or framework name, with **both** (i)
  an explicit textual marker in its defining context ("we introduce", "we propose", "novel", "our
  {framework/score/algorithm} named X") **and** (ii) no fuzzy match against the seed known-vocabulary
  lists used in Step 2. Requiring both conditions (not just an author's self-description) prevents a
  compiler from mislabeling ordinary field vocabulary as "novel" to dodge coverage — a term that
  matches a real ontology/registry entry is never eligible for this label regardless of surrounding
  prose.
`PAPER_LOCAL_NOVEL` entries are excluded from the denominator (a genuinely novel, paper-specific
construct has no external referent to fail to anchor to — genre-fair, not a defect) but are logged
with counts and their classification rationale for audit; they are never silently dropped. Everything
else — including entries the resolver will go on to fail — proceeds to Step 2. `N_denominator` =
`N_universe` − `N_paper_local_novel`. See §1.4 for the degenerate-denominator floor case.

**Step 2 — External resolution [ext: ontology/registry resolver].** For each `N_denominator` entry,
call exactly one of the following, deterministically chosen by candidate type:

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

4. **Universe entries with no matching candidate pattern** (i.e., Step 1 flagged them
   `EXTERNAL_ANCHORABLE` but neither an accession pattern, a named-canonical match, nor a viable OLS
   query term could be constructed, or the resolver call itself errors/times out) are recorded as
   `not_attempted` **(NEW)** — a distinct outcome from `no_match` for audit purposes (tooling failure
   vs. genuine absence of a match), but scored identically at Tier D. This is the mechanism that
   actually enforces the coverage denominator: a universe entry cannot vanish from the score just
   because resolution wasn't possible or wasn't tried.

**Step 2b — Resolved-content semantic-match [ext: deterministic keyword check, escalating to a cached
single-call LLM 0/1/2 judgment; NEW — context-fidelity fix].** For every accession candidate that came
back `resolved` in Step 2(1), do not yet award Tier A. Instead:
1. Extract a small context fingerprint from the ARA's own text surrounding the accession (the
   containing §11 accession block's `Provenance`/intro line, or the §2 claim's `Statement`): organism/
   species token, disease/condition token, assay/platform token, cohort name if any.
2. Extract the analogous fields from the resolver's returned payload (GEO/ClinicalTrials.gov/etc.
   record title, organism field, condition/summary text).
3. **Deterministic pass**: compute case-insensitive token overlap between the two fingerprints. If the
   organism token and at least one of {disease, assay, cohort} token overlap → `context_confirmed`
   (no LLM call needed — cheap, reproducible, no network/model dependency for the common case). If the
   organism token *conflicts* (e.g. ARA says "human", record says "Mus musculus") → `context_mismatch`
   directly, no escalation needed (a clear signal doesn't need a model call).
   Otherwise (overlap is partial/ambiguous — e.g. matching disease term but no organism field in either
   text) → escalate.
4. **LLM escalation pass** (only on ambiguous cases): a single cached, temperature-0 call presenting
   the ARA's context fingerprint and the resolved record's metadata, constrained to return exactly one
   integer: `0` = mismatch, `1` = partial/ambiguous, `2` = confirmed match (adopted from exp2). Map
   `2 → context_confirmed`, `1 → context_ambiguous`, `0 → context_mismatch`.
- Outcome recorded per accession candidate: `context_confirmed`, `context_ambiguous`, or
  `context_mismatch`. This label feeds Step 3's tier assignment directly (a `resolved` accession is no
  longer sufficient by itself for Tier A).

**Step 2c — Reference-space / latent-space resolution [ext: build-token check + HuggingFace Hub
lookup; NEW — latent-space branch].** For every reference-space/model universe entry from Step 1:
1. **Genome/atlas builds**: check the named token against a versioned, maintained enumeration of known
   builds (`GRCh37`, `GRCh38`, `hg19`, `hg38`, `T2T-CHM13`, `MNI152`, `Talairach`, `fsaverage6`, ...).
   A specific, versioned token present → `pinned_reference_space`. A generic mention with no version
   token in the same sentence/bullet ("the human reference genome", "MNI space") → `unpinned_reference_
   space`.
2. **Pretrained models / embedding checkpoints**: `GET https://huggingface.co/api/models/{name}`. A
   response that includes a resolvable `sha`/`revision`/tag matching one explicitly cited in the ARA →
   `pinned_model`. A model that resolves on the Hub but the ARA cites no revision/commit/version → 
   `unpinned_model`. No match on the Hub and no other resolvable registry → `unresolved_model`.
- Outcome recorded: `pinned_reference_space` / `pinned_model` (full credit, feeds Tier A), `unpinned_
  reference_space` / `unpinned_model` (feeds new Tier A−), or `unresolved_model` (feeds Tier D).

**Step 3 — Tier classification [REVISED — new A− tier, context/latent-space outcomes folded in].**
Collapse each candidate's Step 2/2b/2c outcome into one scoring tier:

| Tier | Criteria | Weight |
|---|---|---|
| A — Resolved-confirmed | `resolved` + `context_confirmed`, or `ontology_match`, or `pinned_reference_space`, or `pinned_model` | 1.0 |
| A− — Resolved-ambiguous / unpinned-latent (NEW) | `resolved` + `context_ambiguous`, or `unpinned_reference_space`, or `unpinned_model` | 0.55 |
| B — Recognized-canonical | `named_canonical`, or `format_valid_unverified` (PROSPERO-style) | 0.7 |
| C — Weak | `weak_match` | 0.4 |
| D — Unanchored/failed/not-attempted | `no_match`, `dead_or_mismatched`, `resolved` + `context_mismatch`, `not_attempted`, `unresolved_model` | 0.0, plus a distinct penalty per §Step 7 depending on which D-subtype fired |

Note that `resolved` + `context_mismatch` lands in Tier D (zero weight) *and* triggers
`CONTEXT_MISMATCH_PENALTY` rather than `FABRICATION_PENALTY` — the id is real, the content is wrong,
and the penalty is sized to reflect that it is a distinct, less severe (but non-trivial) failure mode
than a dead/fake identifier (§1's weakness-2 fix).

**Step 4 — Definitional-relevance discount (anti-padding, §1.5).** For each §3 concept candidate,
check whether its heading or a close synonym appears in any §2 claim's `Tags` or `Statement`. If not,
multiply its tier weight by 0.6 (it may still be a legitimately narrow, paper-specific term, but it
isn't pulling weight in the claims layer, so full anchoring credit isn't warranted).

**Step 5 — Implied-data-without-provenance check (§1.4).** Scan all §2 `Statement`/`Evidence basis`
text and §3 `Definition` text for data-driven-work signals: regex/keyword hits for `N\s*=\s*\d+`,
"cohort", "participants", "enrolled", "platform", assay/instrument names, or any accession-shaped
string. If ≥1 such signal fires AND §11 (`data/dataset.md`) is absent or has fewer than one populated
accession/cohort block, set `implied_data_without_provenance = True`.

**Step 6 — Access-tier honesty bonus/penalty.** For every Tier A/A−/B candidate sourced from a §11
accession block, check whether that block's `Source / access` line names *both* an access claim
(open/controlled/by-request) *and* a qualifier scoping which sub-part it applies to (raw vs. processed
vs. metadata). Missing the qualifier on an otherwise-resolved accession costs a fixed per-candidate
deduction (see scoring function `ACCESS_QUALIFIER_PENALTY`).

**Step 7 — Score.** Run the scoring function below over the full `N_denominator` set (not just the
subset that happened to resolve), applying the fabrication and context-mismatch penalties per
candidate.

### 2.3 Scoring function (real Python against the documented artifact shape)

```python
import re
from dataclasses import dataclass, field
from enum import Enum

class Tier(Enum):
    A_RESOLVED = 1.0
    A_MINUS_AMBIGUOUS_OR_UNPINNED = 0.55
    B_RECOGNIZED = 0.7
    C_WEAK = 0.4
    D_UNANCHORED = 0.0

class DTierReason(Enum):
    NONE = "none"
    NO_MATCH = "no_match"
    DEAD_OR_FABRICATED = "dead_or_mismatched"
    CONTEXT_MISMATCH = "context_mismatch"
    NOT_ATTEMPTED = "not_attempted"
    UNRESOLVED_MODEL = "unresolved_model"

@dataclass
class UniverseEntry:
    text: str                      # raw string as it appears in the ARA
    source_field: str              # 'dataset.accession' | 'dataset.cohort' | 'concept.heading'
                                    # | 'concept.notation' | 'claim.tags' | 'claim.statement'
                                    # | 'reference_space' | 'model_checkpoint'
    anchorability: str             # 'EXTERNAL_ANCHORABLE' | 'PAPER_LOCAL_NOVEL'

@dataclass
class Candidate(UniverseEntry):
    tier: Tier = Tier.D_UNANCHORED
    d_reason: DTierReason = DTierReason.NONE
    definitional_relevance: bool = True        # False => padding discount applies (Step 4)
    has_access_qualifier: bool | None = None   # only meaningful for dataset accessions

ACCESS_QUALIFIER_PENALTY = 6.0    # points, per resolved accession missing scope qualifier
PADDING_DISCOUNT = 0.6
FABRICATION_PENALTY = 8.0         # points, per candidate flagged dead_or_mismatched (fake/dead ID)
CONTEXT_MISMATCH_PENALTY = 4.0    # points, per real-but-wrong-context resolved ID — strictly between
                                   # "no penalty" and FABRICATION_PENALTY, per critique's requested
                                   # placement (weakness (b) fix)
IMPLIED_DATA_PENALTY = 25.0       # points, flat, if Step 5 fires

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
    universe: list[UniverseEntry],
    candidates: list[Candidate],           # resolution outcomes for every EXTERNAL_ANCHORABLE entry
    section11_present: bool,
    section11_populated: bool,             # >=1 real accession/cohort block, not just an intro paragraph
    claims_and_concepts_text: str,         # concatenated raw text of claims.md + concepts.md, for Step 5
) -> dict:
    n_universe = len(universe)
    n_paper_local = sum(1 for u in universe if u.anchorability == "PAPER_LOCAL_NOVEL")
    n_denominator = n_universe - n_paper_local

    if n_denominator == 0:
        # Degenerate case: every universe entry was classified paper-local-novel (or the universe
        # itself is empty, which should not happen since claims.md/concepts.md are mandatory-core).
        # Score the floor; do not skip.
        base = 0.0
        tier_counts = {t.name: 0 for t in Tier}
        degenerate_flag = True
    else:
        # Every EXTERNAL_ANCHORABLE universe entry MUST appear exactly once in `candidates`
        # (unresolved/untried entries are represented as Tier D / not_attempted, per Step 2(4)) —
        # this is what makes the mean a true coverage measure rather than a mean over a
        # self-selected subset.
        assert len(candidates) == n_denominator, (
            "coverage violation: every EXTERNAL_ANCHORABLE universe entry must be carried through "
            "resolution, even as not_attempted — selective omission is what this denominator exists "
            "to prevent"
        )
        raw_scores = [weighted_candidate_score(c) for c in candidates]
        base = 100.0 * (sum(raw_scores) / n_denominator)
        tier_counts = {t.name: sum(1 for c in candidates if c.tier == t) for t in Tier}
        degenerate_flag = False

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

    # Fabrication vs. context-mismatch penalties (kept distinct per weakness (b) fix)
    penalty += FABRICATION_PENALTY * sum(
        1 for c in candidates if c.d_reason == DTierReason.DEAD_OR_FABRICATED
    )
    penalty += CONTEXT_MISMATCH_PENALTY * sum(
        1 for c in candidates if c.d_reason == DTierReason.CONTEXT_MISMATCH
    )

    score = max(0.0, min(100.0, base - penalty))

    return {
        "score": round(score, 1),
        "n_universe": n_universe,
        "n_paper_local_novel_excluded": n_paper_local,
        "n_denominator": n_denominator,
        "tier_counts": tier_counts,
        "not_attempted_count": sum(1 for c in candidates if c.d_reason == DTierReason.NOT_ATTEMPTED),
        "context_mismatch_count": sum(1 for c in candidates if c.d_reason == DTierReason.CONTEXT_MISMATCH),
        "fabrication_count": sum(1 for c in candidates if c.d_reason == DTierReason.DEAD_OR_FABRICATED),
        "implied_data_without_provenance": implied_data_without_provenance,
        "denominator_degenerate_all_paper_local": degenerate_flag,
        "penalty_applied": round(penalty, 1),
        "genre_note": (
            "section11_absent_unpenalized" if not section11_present and not implied_needed
            else "section11_present" if section11_present
            else "section11_absent_but_implied_by_claims_or_concepts"
        ),
    }
```

`UniverseEntry`/`Candidate` objects are produced by Steps 1–2c's parsing/classification/resolver
pipeline (not shown as code — those are I/O-bound external calls: NCBI E-utils, ClinicalTrials.gov API
v2, EBI OLS API, HuggingFace Hub API, plus two narrowly-scoped LLM calls: Step 1b's anchorability
classifier and Step 2b's escalation-only semantic-match judge) and fed into `compute_m64`. Both LLM
calls are single-purpose, schema-constrained (one label / one integer out), and run at temperature 0
against a fixed prompt template, so — combined with cached resolver-response and cached LLM-response
snapshots — the *scoring* remains fully deterministic and reproducible even though both branches
involve network I/O and (limited, escalation-gated) model calls: re-running `compute_m64` against a
cached snapshot always reproduces the same score, which matters for tournament reproducibility.

### 2.4 Output
A single `M64` scalar in `[0, 100]` plus the structured `dict` above (universe/denominator counts,
tier breakdown, flags) attached as evidence — the flags (`implied_data_without_provenance`,
`fabrication_count`, `context_mismatch_count`, `not_attempted_count`, `denominator_degenerate_all_
paper_local`, `ACCESS_QUALIFIER_PENALTY` hits) are exactly the "penalize, don't skip" trail: even a
0-scoring ARA produces a populated, auditable reason set rather than an N/A, and the universe/
denominator counts make visible *how much of the paper's anchorable vocabulary was actually attempted*
— not just how well the attempted subset scored.

---

## 3. Why this is hard to Goodhart

- **Live external resolution, not self-report.** Steps 2/2b/2c each hit a real external system
  (NCBI/ClinicalTrials.gov registries, EBI OLS, HuggingFace Hub) rather than trusting the ARA's own
  claim that a term is "standard," an ID is "valid," or a model/build is "the one we used." A compiler
  cannot raise its score by simply asserting anchoring — the identifier, term, or reference must
  actually exist, actually match in the target system, and (new) actually be about the right subject.
- **Coverage denominator blocks selective anchoring (NEW).** Because the anchorable-term universe is
  extracted in Step 1 *before* any resolution is attempted, and every surviving universe entry must
  appear in the final candidate set (even as `not_attempted`), a compiler cannot inflate its average by
  anchoring one easy term and leaving nineteen hard ones as prose — the assertion in `compute_m64` that
  `len(candidates) == n_denominator` makes this a structural invariant of the scoring function, not a
  best-effort convention.
- **Resolved-content semantic-match blocks context laundering (NEW).** A real, live-resolving
  accession that belongs to the wrong species/disease/cohort no longer earns Tier A; Step 2b's cheap
  deterministic check (escalating to a single cached LLM judgment only when genuinely ambiguous) drops
  it to Tier D with a `CONTEXT_MISMATCH_PENALTY` distinct from fabrication. This closes the specific
  route the cycle-1 critique flagged as exp1's biggest gap: "a real GEO accession for the wrong dataset
  scores Tier A" can no longer happen silently.
- **Version-pin requirement blocks generic latent-space claims (NEW).** Naming a genome build or model
  family without a version/revision token is capped at Tier A− (0.55), never full credit — a compiler
  cannot claim latent-space anchoring credit for a reference that isn't actually reproducible to a
  specific computational artifact.
- **Fabrication is punished harder than omission, and context-mismatch sits strictly between the two.**
  An accession-shaped string that fails live resolution (`dead_or_mismatched`) scores strictly worse
  (Tier D + `FABRICATION_PENALTY`) than honestly not attempting an anchor, and a resolved-but-wrong-
  context ID (`context_mismatch`) is worse than a clean resolve but incurs a smaller, distinct penalty
  than outright fabrication (`CONTEXT_MISMATCH_PENALTY` < `FABRICATION_PENALTY`) — removing the
  incentive both to paste plausible-looking-but-fake IDs and to borrow a real-but-irrelevant one.
- **Specificity/depth filtering blocks root-term gaming.** Matching to a near-root ontology class
  (shallow `depth-from-root`) is explicitly excluded from `ontology_match`, so stuffing generic words
  ("disease," "process," "cell") cannot cheaply inflate the resolved-candidate count — and because
  these entries are now mandatory denominator members (not optional candidates), a shallow/generic
  match actively drags the score down rather than merely failing to help it.
- **Definitional-relevance cross-check blocks concept-padding.** A `concepts.md` entry that resolves to
  a real ontology class but never actually appears in any claim's `Tags`/`Statement` gets discounted
  (Step 4) — anchoring only pays full credit when the anchored term is load-bearing for the paper's
  actual claims, not merely present as decoration.
- **Anchorability mislabeling is auditable, not free.** A compiler cannot dodge the coverage
  requirement by declaring ordinary field vocabulary "novel": Step 1b's classifier requires both an
  explicit self-description marker *and* failure to match any seed known-vocabulary/registry entry
  before granting the `PAPER_LOCAL_NOVEL` exclusion, and every exclusion is logged with its rationale
  span for review — a systematically over-broad "novel" labeling pattern is itself a visible, checkable
  defect in the resulting evidence trail.
- **The implied-data check closes the "just omit §11" escape hatch.** Because absence of `data/
  dataset.md` is only free when nothing else in the ARA implies data-driven work, a compiler cannot
  dodge low anchoring scores by simply not writing a dataset section for a study that obviously has
  one (Step 5's flat penalty fires on the internal-evidence mismatch, not on the missing file alone).

## 4. Composition with the rest of the suite

M64 is intentionally orthogonal to grounding/verifier-family metrics: it never re-checks `Sources`
quote presence, claim-evidence matching, or internal claims↔concepts consistency — those own the
*internal-traceability* axis. M64 owns the *external-resolvability / interoperability / context-
fidelity* axis: can this ARA's entities be looked up, linked, reused, and reproduced outside the
document, and do the identifiers it presents actually point at what it claims. Because these axes are
measuring genuinely different failure modes (an ARA can be perfectly internally grounded yet fully
unanchored to any external vocabulary, or vice versa — richly anchored terms with sloppy internal
grounding, or worse, confidently anchored terms pointing at the wrong external record), M64 should be
aggregated as an **additive, modest-weight** component rather than averaged against grounding scores in
a way that lets either axis mask the other. Its natural place in a composite good-science score is as a
*bonus/interoperability* term layered on top of a correctness/grounding floor — a paper with excellent
internal grounding but zero anchoring should score respectably overall but visibly lose the
interoperability bonus, a paper that anchors heavily to external registries while being internally
unsound should not be able to buy its way to a high composite score through M64 alone, and (new) a
paper that anchors heavily but to the *wrong* records, or anchors only its easiest few terms, should no
longer be indistinguishable from one that anchors broadly and correctly.
