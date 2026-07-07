# ARA Compiler — Data Shapes Reference

This document enumerates every distinct artifact type the ARA (Agent-Native Research Artifact)
compiler emits when it compiles a paper/repo/dataset into `research/ara-library/{id}/`. It exists
so a metric-design tournament can hand each artifact type to a downstream agent **in isolation** —
each section below is self-contained: it repeats what the artifact is, why it exists, its exact
field-level shape with types, a full realistic example transcribed from a real compiled ARA, how
much of it typically appears, and — critically — what "absent" or "thin" looks like for that
artifact, because thinness/absence must be scored, not skipped.

**Sources used to build this reference**: the compiler skill definition and its four reference docs
(`ara-schema.md`, `exploration-tree-spec.md`, `validation-checklist.md`, `figure-extraction-guide.md`
under `.claude/skills/compiler/`), plus three fully compiled real ARAs read end-to-end:
- `che26-diagnostic-performance-of-plasma-p-tau217/` — a systematic review / network meta-analysis
  (secondary-data synthesis, no code, no primary dataset — the "thin src/ data/" genre).
- `huu25-apoe-e4-alzheimer-s-risk-converges/` — a wet-lab + computational genomics preprint with two
  GEO datasets and a large external analysis repo (data-rich, but the repo itself was not cloned, so
  `src/execution/` is absent even though the work has real code — captured instead in `src/artifacts.md`).
- `aki26-molecular-signatures-of-resilience-to-alzheimer/` (spot-checked for `src/execution/*.py`,
  `src/configs/*.md`, and `logic/solution/heuristics.md`) and `ali25-multimodal-self-supervised-learning-for-early/`
  (spot-checked for `heuristics.md`) and `ave25-uncovering-plaque-glia-niches-in-human/` (spot-checked
  for a `mixed`/`qualitative_sample` figure) — used for artifact subtypes the first two ARAs happened
  not to contain, so every documented shape below is grounded in a real file, not invented.

**Out of scope for this document / the tournament**: `metrics/*.json`, `metrics/*.md`, and
`logic/grounding_findings.yaml` also appear in compiled ARA directories, but they are outputs of
*downstream validators* (Seal Level 2 semantic review, citation-verification passes), not artifacts
the compiler itself emits during compilation. They are excluded from the 11 enumerated sections below.

---

## 0. Directory shape at a glance

```
PAPER.md                            # ✓ mandatory — §1
logic/
  problem.md                        # ✓ mandatory — §4
  claims.md                         # ✓ mandatory — §2
  concepts.md                       # ✓ mandatory — §3
  experiments.md                    # ✓ mandatory — §5
  related_work.md                   # ✓ mandatory — §6
  solution/
    constraints.md                  # ✓ mandatory — §7
    <method files>                  # as warranted — §7 (study_design.md, method.md, architecture.md,
                                     #   algorithm.md, heuristics.md, formalization.md, proofs.md, ...)
src/
  environment.md                    # ✓ mandatory — §10
  artifacts.md                      # as warranted — §10
  configs/*.md                      # as warranted — §10
  execution/*.{py,r,...}            # as warranted — §10
  prompts/*                         # as warranted — §10
data/
  dataset.md                        # as warranted — §11
  preprocessing.md                  # as warranted — §11
trace/
  exploration_tree.yaml             # ✓ mandatory — §8
evidence/
  README.md                         # ✓ mandatory — §9
  tables/*.md + *.png               # ✓ mandatory (one pair per numbered source table) — §9
  figures/*.md + *.png              # ✓ mandatory (one pair per numbered source figure) — §9
  proofs/*.md                       # as warranted (theory/derivation work) — §9
```

`✓` = present in **every** ARA the compiler produces, non-empty, and structurally checked by Seal
Level 1. Everything else is produced **only when the source material actually contains that kind of
content** — there is no fixed template. This "only if warranted" rule is itself something a
tournament metric can score: an ARA compiled from a systematic review correctly has no
`src/execution/`, `src/configs/`, or `heuristics.md`; forcing one in would be a fabrication, and a
genuinely code-heavy paper *lacking* `src/execution/` when a repo was provided is a coverage failure.

---

## 1. `PAPER.md` (root manifest) -- Metadata

### Artifact + path
`PAPER.md` at the ARA root, e.g. `research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/PAPER.md`.

### Purpose
The single entry point and progressive-disclosure Level-1 view (~200 tokens) of the whole ARA. An
agent reads only this file to decide whether the paper is relevant before drilling into any layer.
It is the manifest: bibliographic identity, one-paragraph synthesis of the contribution, and an
index of every other file the compiler actually generated for this paper.

### Structure

YAML frontmatter (between `---` fences) — every key is mandatory except where noted:

| Field | Type | Real example |
|---|---|---|
| `title` | string | `"Diagnostic performance of plasma p-Tau217, p-Tau181, and p-Tau231 across the Alzheimer's disease continuum: a network meta-analysis"` |
| `authors` | list[string] | `["Xiaofeng Chen", "Tingting Huang", "Chao Shi", "Shuizhi Xu", "Shuwei Fan"]` |
| `year` | int | `2026` |
| `venue` | string | `"Frontiers in Aging Neuroscience"` |
| `doi` | string (DOI or arXiv ID, or "Not specified in paper") | `"10.3389/fnagi.2026.1834591"` |
| `ara_version` | string | `"1.0"` |
| `domain` | string, free text | `"Alzheimer's disease diagnostics — blood-based biomarkers; Bayesian/frequentist network meta-analysis of diagnostic test accuracy"` |
| `keywords` | list[string], 5–10 items | `["Alzheimer's disease continuum", "diagnostic performance", "network meta-analysis", ...]` (10 items) |
| `claims_summary` | list[string], one line per main claim (mirrors `logic/claims.md` count) | `["Plasma p-tau217 measured by mass spectrometry (p217_MS) has the highest diagnostic accuracy for amyloid-beta pathology (P-score = 0.859), far outranking standard p-tau181 immunoassay (P-score = 0.117)."]` (7 lines in this ARA, one per claim group) |
| `abstract` | string, full paper abstract verbatim | (full ~250-word abstract, verbatim from the source) |

Body (markdown, after the closing `---`):

| Block | Type | Notes |
|---|---|---|
| `# {Paper Title}` | markdown H1 | repeats the title |
| `## Overview` | markdown-prose, 1–2 paragraphs | free-form synthesis of the contribution |
| `## Layer Index` | structured markdown | one sub-table per layer that actually has files (see below) |

The Layer Index is itself structured — one table per present layer, each row a
`[relative/path.md](relative/path.md) \| one-line description` pair:

- `### Cognitive Layer (/logic)` — table columns `File \| Description`
- `### Physical Layer (/src)` (sometimes titled "Implementation Layer") — table columns
  `File \| Description` or `File \| Description \| Claims` (a third column linking files to `C##` ids)
- `### Data Layer (/data)` — present only when `data/` exists
- `### Exploration Graph (/trace)` — table columns `File \| Description`, description states the node
  count, e.g. `"14-node research DAG of the review's decision trajectory"`
- `### Evidence (/evidence)` — table columns `File \| Description`; description states counts, e.g.
  `"Index of 2 tables + 3 figures"`

### A full realistic example

```markdown
---
title: "Diagnostic performance of plasma p-Tau217, p-Tau181, and p-Tau231 across the Alzheimer's disease continuum: a network meta-analysis"
authors: ["Xiaofeng Chen", "Tingting Huang", "Chao Shi", "Shuizhi Xu", "Shuwei Fan"]
year: 2026
venue: "Frontiers in Aging Neuroscience"
doi: "10.3389/fnagi.2026.1834591"
ara_version: "1.0"
domain: "Alzheimer's disease diagnostics — blood-based biomarkers; Bayesian/frequentist network meta-analysis of diagnostic test accuracy"
keywords: ["Alzheimer's disease continuum", "diagnostic performance", "network meta-analysis", "plasma biomarkers", "plasma phosphorylated tau 181", "plasma phosphorylated tau 217", "plasma phosphorylated tau 231", "mass spectrometry", "automated immunoassay", "p-tau217/Abeta42 ratio"]
claims_summary:
  - "Plasma p-tau217 measured by mass spectrometry (p217_MS) has the highest diagnostic accuracy for amyloid-beta pathology (P-score = 0.859), far outranking standard p-tau181 immunoassay (P-score = 0.117)."
  - "The p-tau217/Abeta42 ratio on automated platforms yields a significant incremental AUC gain of 0.025 (95% CI 0.005-0.045; I2 = 0%) over single-analyte assays."
abstract: "Blood-based biomarkers (BBMs) are transforming the diagnostic workflow for Alzheimer's disease (AD). ... [full abstract]"
---

# Diagnostic performance of plasma p-Tau217, p-Tau181, and p-Tau231 across the Alzheimer's disease continuum: a network meta-analysis

## Overview

This is a PRISMA-DTA systematic review and network meta-analysis (NMA) that, for the first time,
simultaneously compares plasma phosphorylated-tau isoforms ... The review is prospectively
registered on PROSPERO (CRD420261327845). No analysis code or accessioned primary dataset was
released; the work reuses extracted summary AUC statistics from established AD cohorts.

## Layer Index

### Cognitive Layer (`/logic`)
| File | Description |
|------|-------------|
| [problem.md](logic/problem.md) | Observations (biomarker/platform heterogeneity) → gaps → key insight (simultaneous NMA) |
| [claims.md](logic/claims.md) | 8 falsifiable claims (C01-C08) with pooled diagnostic-performance findings |
| [concepts.md](logic/concepts.md) | 13 technical terms (p-tau isoforms, P-score/SUCRA, NMA, AUC, ratio metric, matrices, AT(N)) |
| [experiments.md](logic/experiments.md) | 6 declarative NMA/analysis plans (E01-E06), directional only |
| [related_work.md](logic/related_work.md) | Typed dependency graph over the paper's 30 references + PROSPERO registration |
| [solution/study_design.md](logic/solution/study_design.md) | PRISMA-DTA search, inclusion/exclusion, cohort de-overlap, NMA model, ranking |
| [solution/constraints.md](logic/solution/constraints.md) | Limitations, assumptions, boundary conditions |

### Physical Layer (`/src`)
| File | Description |
|------|-------------|
| [environment.md](src/environment.md) | Analytical environment: netmeta R package, PROSPERO protocol, cohorts, data access |
| [artifacts.md](src/artifacts.md) | Non-code deliverables: PROSPERO registration, extracted summary-data (no released dataset/code) |

### Exploration Graph (`/trace`)
| File | Description |
|------|-------------|
| [exploration_tree.yaml](trace/exploration_tree.yaml) | 14-node research DAG of the review's decision trajectory |

### Evidence (`/evidence`)
| File | Description |
|------|-------------|
| [README.md](evidence/README.md) | Index of 2 tables + 3 figures |
| [tables/table1.md](evidence/tables/table1.md) | Characteristics of included studies and cohorts |
| [tables/table2.md](evidence/tables/table2.md) | SUCRA-based P-score rankings across 4 outcomes |
| [figures/figure1.md](evidence/figures/figure1.md) | PRISMA flow diagram of study selection |
| [figures/figure2.md](evidence/figures/figure2.md) | Evidence network plots (Abeta, Tau-PET) |
| [figures/figure3.md](evidence/figures/figure3.md) | Forest plots of AUC mean differences vs. p-tau181 baseline |
```

### Cardinality / variability
Exactly one `PAPER.md` per ARA — never zero, never more than one. `claims_summary` length always
equals (or closely tracks) the number of top-level claim groups in `claims.md` (self-consistency
check). The Layer Index adapts: a data-rich genomics preprint (huu25) has a `### Data Layer (/data)`
table and a `Claims` column in its Physical Layer table; a pure meta-analysis (che26) has neither the
extra column nor much in `/src`. A theory paper would instead show `evidence/proofs/` rows.

### Availability notes
`PAPER.md` itself is never absent (Seal Level 1 fails the whole ARA otherwise) — but its **richness**
varies with paper genre and is a real scoring axis:
- **Paywalled / abstract-only source**: `abstract` may be the only rich field; `domain`/`keywords`
  still populate from title+abstract, but `claims_summary` will be thin (fewer, vaguer lines) and the
  Layer Index will show correspondingly thin `logic/`/`evidence/` files — this should be *penalized*,
  not silently treated as equivalent to a full compilation.
- **doi**: for datasets/cohorts without a formal DOI, or for non-indexed preprints, this is
  `"Not specified in paper"` rather than fabricated.
- **Frontmatter/Layer-Index count mismatch** is itself a defect Seal Level 1 checks for (§12 of the
  validation checklist): if `claims_summary` lists 7 items but `claims.md` has 8 `## C##` blocks, that
  is a self-consistency failure a metric should catch.

---

## Metrics & indicators
- metadata comprehensiveness
    - the basics, persistent id and so forth
- artifact comprehensiveness
    - which artifacts are available?
    - what does this tell us about the article type

## 2. `logic/claims.md` (falsifiable claims)

### Artifact + path
`logic/claims.md`, e.g. `research/ara-library/huu25-apoe-e4-alzheimer-s-risk-converges/logic/claims.md`.

### Purpose
The paper's testable, falsifiable assertions — the "what the paper actually claims to have shown,"
stripped of narrative hedging, each traceable to a specific experiment and a specific number's exact
source location. This is the highest-value file for downstream agents deciding whether to trust or
build on the paper's findings.

### Structure
One `## C{NN}: {Short title}` block per claim (`C01`, `C02`, ... zero-padded two digits, more digits
if >99). Every block has ALL of these fields (Seal Level 1 fails a block missing any):

| Field | Type | Real example |
|---|---|---|
| `**Statement**` | markdown-prose, precise & falsifiable, numbers copied exactly (never rounded) | `"For detecting amyloid-beta (Abeta) positivity, mass-spectrometry-derived p-tau217 (p217_MS) achieved the highest rank (P-score = 0.859), followed by ..."` |
| `**Status**` | enum{`hypothesis`, `supported`, `refuted`} (can carry a parenthetical qualifier) | `supported` — or `supported (interpretation-limited by female sample size)` |
| `**Falsification criteria**` | markdown-prose: what observation would disprove this | `"Refuted if, under the same NMA on independent cohorts, p181_IA or another isoform outranked p217_MS for Abeta detection, or if p217_MS's AUC advantage over p181_IA were non-significant (95% CI crossing 0)."` |
| `**Proof**` | list[ref-id] — experiment IDs only (`E01`, `E02`, ...), never file paths | `[E01]` |
| `**Evidence basis**` | markdown-prose: exactly what the cited evidence directly shows | `"Table 2 Outcome 1 P-scores (p217_MS 0.859 > p217_Ratio 0.783 > ...); Figure 3A forest plot MDs vs. p181_IA."` |
| `**Interpretation**` | markdown-prose, optional broader synthesis kept separate from `Evidence basis` | `"All p-tau217 variants and the ratio significantly outperform the older p-tau181 immunoassay standard, which the authors argue is effectively obsolete..."` |
| `**Dependencies**` | list[ref-id] of other claim IDs, or `none` | `[C01]` or `none` |
| `**Sources**` | list of grounding entries (see below) | see below |
| `**Tags**` | comma-separated string list | `p-tau217, mass spectrometry, amyloid-beta, AUC, P-score, ranking` |

**`Sources` entry format** (one per load-bearing number in `Statement`), a hard requirement (Rule 16 /
the "Grounding discipline"):
```
`<value>` ← <file-or-section-ref> (<locator>) «<verbatim matched line>» [input|result]
```
- `<value>` — the exact number/string as it appears in the Statement, in backticks.
- `<file-or-section-ref>` — either a repo-relative evidence path (`evidence/tables/table2.md`) or a
  paper section (`§3.6`, `§4.2`).
- `«...»` — a **verbatim quote** copied from the cited location; a bare path with no quote is invalid
  and must fail validation.
- `[input]` — tags a value that was *set* (e.g. a config/recipe value); `[result]` tags a value a
  run/analysis *produced* (the overwhelmingly common tag in claims).
- `[pending: ...]` is allowed in place of a verified quote only when the source genuinely could not be
  opened this turn — it is honesty, not a shortcut, and is flagged for follow-up.

### A full realistic example

```markdown
## C01: p-tau217 by mass spectrometry has the highest diagnostic accuracy for amyloid-beta pathology
- **Statement**: For detecting amyloid-beta (Abeta) positivity, mass-spectrometry-derived p-tau217
  (p217_MS) achieved the highest rank (P-score = 0.859), followed by the p-tau217 ratio (p217_Ratio,
  P-score = 0.783) and ALZpath-based p-tau217 immunoassay (p217_ALZpath, P-score = 0.686); standard
  p-tau181 immunoassay (p181_IA) ranked last (P-score = 0.117). In the forest plot vs. the p181_IA
  baseline, p217_MS had a mean AUC difference of MD = 0.10 (95% CI 0.04-0.16).
- **Status**: supported
- **Falsification criteria**: Refuted if, under the same NMA on independent cohorts, p181_IA or
  another isoform outranked p217_MS for Abeta detection, or if p217_MS's AUC advantage over p181_IA
  were non-significant (95% CI crossing 0).
- **Proof**: [E01]
- **Evidence basis**: Table 2 Outcome 1 P-scores (p217_MS 0.859 > p217_Ratio 0.783 > p217_ALZpath
  0.686 > p217_Lumi 0.667 > p217_IA 0.412 > p217_Lilly 0.331 > p231_UGOT 0.145 > p181_IA 0.117);
  Figure 3A forest plot MDs vs. p181_IA.
- **Interpretation**: All p-tau217 variants and the ratio significantly outperform the older
  p-tau181 immunoassay standard, which the authors argue is effectively obsolete for high-precision
  diagnostics.
- **Dependencies**: none
- **Sources**:
  - `0.859` ← evidence/tables/table2.md (Table 2, Outcome 1, Rank 1) «p217_MS (0.859)» [result]
  - `0.783` ← evidence/tables/table2.md (Table 2, Outcome 1, Rank 2) «p217_Ratio (0.783)» [result]
  - `0.686` ← evidence/tables/table2.md (Table 2, Outcome 1, Rank 3) «p217_ALZpath (0.686)» [result]
  - `0.117` ← evidence/tables/table2.md (Table 2, Outcome 1, Rank 8) «p181_IA (0.117)» [result]
  - `0.10 (95% CI 0.04-0.16)` ← evidence/figures/figure3.md (Figure 3A) «p217_MS ... 0.10 [ 0.04; 0.16]» [result]
- **Tags**: p-tau217, mass spectrometry, amyloid-beta, AUC, P-score, ranking
```

### Cardinality / variability
Typically 5–8 claims per ARA (Seal Level 1 requires ≥1; the compiler's own convention aims higher but
never pads). `Dependencies` chains commonly reference an earlier "anchor" claim (e.g. C01) from
several later claims. RCT/clinical-trial ARAs tend to have claims phrased around primary/secondary
endpoints and hazard ratios; meta-analyses phrase claims around pooled P-scores/rankings; lab/omics
papers phrase claims around DEG counts and pathway enrichment (see huu25's C01: `"679 upregulated and
343 downregulated genes at FDR<0.05"`). `Status` skews heavily to `supported` in practice because
compilers extract what the paper reports as its findings; `hypothesis`/`refuted` appear for stated
ablations or explicitly disconfirmed prior expectations.

### Availability notes
`claims.md` is mandatory core — it is never entirely absent. What varies, and what a penalizing
metric should watch for:
- **Missing `Sources` entries or bare paths with no «quote»** — an automatic Seal Level 1 failure;
  in a "thin" or rushed compilation this is the single most common defect.
- **`Interpretation` collapsing into `Evidence basis`** (no separation of raw support from broader
  reading) — a quality defect the validation checklist explicitly watches for via
  "Evidence-limited wording" (Rule 10).
- **Reviews/meta-analyses**: claims often carry an extra editorializing clause (e.g. "effectively
  obsolete") that is the *authors'* interpretive gloss rather than a directly measured quantity — a
  well-compiled ARA still grounds the ranking fact but should not smuggle the value-judgment in as if
  it were equally grounded (see che26 C08, flagged in its own `grounding_findings.yaml` review with
  `context_match: false` for exactly this reason).
- **Abstract-only / paywalled sources**: claims degrade to only what the abstract states — few claims,
  each with weak "Evidence basis" (often just `§Abstract`) since section-level detail can't be
  grounded; this must read as materially thinner than a full-text compilation, not silently equal.

---

## Indicators
- claim comprehensiveness
    - are all the subfields filled
    - falsifiability
    - status
    - are claims <> results matching?
        - is there a connected clinical trial with different results reporting? -> publication bias
    - reduce relevance if abstract only
    - references & anchor claims (dependencies)
- claim novelty
- claim contradictions
- FOL-ability: comprehensiveness where easy to draw a FOL graph following Oshima principles?
- ctrld vocabulary referencability: is this using translatable, anchorable terms?

## 3. `logic/concepts.md` (technical terms)

### Artifact + path
`logic/concepts.md`, e.g. `research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/logic/concepts.md`.

### Purpose
Formal, self-contained definitions of the paper's genuine technical vocabulary — the terms a reader
must understand to parse the claims and methods. Not a glossary of borrowed/generic terms; each entry
should be something specific to this paper's contribution or field.

### Structure
One `## {Term Name}` section per concept (a plain markdown heading, not an ID scheme). Each has:

| Field | Type | Real example |
|---|---|---|
| `**Notation**` | string — LaTeX/symbolic notation, or `"—"` if none | `p217 (nodes: p217_MS, p217_Ratio, p217_ALZpath, p217_Lumi, p217_IA, p217_Lilly, p217_Serum, p217_AutoIA)` |
| `**Definition**` | markdown-prose, formal | `"Tau phosphorylated at threonine 217. In this NMA it is the top-performing isoform for detecting amyloid-beta pathology..."` |
| `**Boundary conditions**` | markdown-prose — when it applies/doesn't, or `"Not specified in paper"` | `"Performance is highest when measured by mass spectrometry or as an automated p-tau217/Abeta42 ratio."` |
| `**Related concepts**` | comma-separated list of other concept names (loose text, not IDs) | `p-tau, mass spectrometry, p-tau217/Abeta42 ratio, automated immunoassay` |

### A full realistic example

```markdown
## Network meta-analysis (NMA)
- **Notation**: NMA
- **Definition**: A meta-analytic method comparing multiple interventions/tests simultaneously by
  combining direct (head-to-head) and indirect evidence within a connected network of comparisons,
  referenced to a common comparator. Here a random-effects frequentist NMA (netmeta) compares
  biomarker+platform nodes.
- **Boundary conditions**: Requires a connected network; assumes transitivity/consistency across the
  evidence base; between-study heterogeneity captured by I2.
- **Related concepts**: network geometry, P-score, mean difference, direct/indirect evidence

## P-score (SUCRA analog)
- **Notation**: P-score in [0, 1]
- **Definition**: A frequentist ranking metric (analogous to SUCRA in Bayesian NMA) giving the
  probability that a treatment/test is better than a competing one, averaged over all competitors.
  Higher values indicate a higher probability of being the best diagnostic marker.
- **Boundary conditions**: Ranks relative performance within a specific outcome/network; not an
  absolute accuracy value.
- **Related concepts**: SUCRA, NMA, ranking, network geometry
```

### Cardinality / variability
Target is ≥5 sections (Seal Level 1 checks this as a soft count target, never a padding license); the
two ARAs read here have 13 (che26, meta-analysis with heavy method vocabulary) and 10 (huu25, wet-lab
genomics — cell-type/assay vocabulary). A theory paper's concepts skew toward formal
objects/operators with dense `Notation`; a clinical-trial ARA's concepts skew toward endpoint
definitions and instrument names with `Notation: —`.

### Availability notes
Never fully absent (mandatory core). Thinness signals to watch:
- Fewer than 5 genuine sections **is correct, not a defect**, if the paper truly introduces fewer
  distinct terms (Rule 14/15 — source-bounded, not a quota) — a metric must not penalize an honestly
  short concepts.md the same way it penalizes a padded one with borrowed/trivial terms.
- `Boundary conditions: Not specified in paper` appearing on most/all entries signals a shallow read
  of the source (the compiler didn't work hard to locate applicability limits) rather than a genuine
  absence — this is a legitimate quality signal for a tournament metric to catch, distinct from an
  honest "the paper doesn't state this."
- Abstract-only sources: concepts.md will contain only what can be defined from the title/abstract
  vocabulary — visibly fewer, shallower `Definition` fields.

---

## Indicators
- context & content novelty (evans)
- anchoredness: is there a latent layer and/or canonical dataset referenced
- internal consistency: claims <> concepts

## 4. `logic/problem.md` (problem statement)

### Artifact + path
`logic/problem.md`, e.g. `research/ara-library/huu25-apoe-e4-alzheimer-s-risk-converges/logic/problem.md`.

### Purpose
The "why" layer: what was empirically known before this work (Observations), what was missing or
broken (Gaps), the creative leap that resolves the gap (Key Insight), and the assumptions the whole
argument rests on. This is what lets a downstream agent understand *why* the paper's specific method
was chosen, not just what the method is.

### Structure

```markdown
# Problem Specification

## Observations
### O{N}: {title}
- **Statement**: {precise empirical fact, with numbers, drawn from the source's Introduction/prior work}
- **Evidence**: {citation(s) or section ref}
- **Implication**: {what this means for the problem}

## Gaps
### G{N}: {title}
- **Statement**: {what's missing or broken}
- **Caused by**: {observation IDs, e.g. O1, O2}
- **Existing attempts**: {what's been tried}
- **Why they fail**: {specific failure mode}

## Key Insight
- **Insight**: {the creative leap, precisely stated}
- **Derived from**: {observation IDs}
- **Enables**: {what solution approach this unlocks}

## Assumptions
- A1: {assumption}
- A2: {assumption}
```

| Field | Type | Real example |
|---|---|---|
| `### O{N}` heading | ref-id (O1, O2, ...) + string title | `### O2: Plasma p-tau isoforms are the most promising BBMs, but the optimal isoform is contested` |
| `**Statement**` (in O) | markdown-prose, often verbatim-quoting the source | `"Among candidate BBMs, plasma phosphorylated tau (p-tau) species are most promising. ... p-tau217 shows exceptional concordance with CSF/PET..."` |
| `**Evidence**` (in O) | string — citation list or section ref | `"§1 Introduction (Karikari et al., 2020; Mila-Aloma et al., 2022; ...)"` |
| `**Implication**` (in O) | markdown-prose | `"Inconsistent cross-cohort findings sustain an ongoing debate about which isoform is optimal..."` |
| `### G{N}` heading | ref-id (G1, G2, ...) + string title | `### G1: No consensus on the optimal p-tau isoform across disease stages` |
| `**Caused by**` (in G) | list[ref-id] of O-numbers | `O2, O5` |
| `**Existing attempts**` / `**Why they fail**` (in G) | markdown-prose | see example |
| `**Insight**` | markdown-prose, precise | `"Cast every biomarker+platform combination ... as a distinct node in a network meta-analysis..."` |
| `**Derived from**` | list[ref-id] of O-numbers | `O5, G1, G2, G3` (Key Insight may cite gaps too) |
| `**Enables**` | markdown-prose | `"A unified P-score (SUCRA-analogous) ranking that resolves the isoform, platform, and matrix debates..."` |
| `A{N}:` | ref-id + inline markdown-prose | `A2: Selecting the single most comprehensive dataset per cohort yields statistically independent nodes (no patient counted twice).` |

### A full realistic example

```markdown
### O2: Plasma p-tau isoforms are the most promising BBMs, but the optimal isoform is contested
- **Statement**: Among candidate BBMs, plasma phosphorylated tau (p-tau) species are most promising.
  Initial studies highlighted p-tau181; more recent evidence suggests p-tau217 and p-tau231 may
  offer superior accuracy and dynamic range. p-tau217 shows exceptional concordance with CSF/PET;
  p-tau231 may rise earliest in the preclinical phase; p-tau217 correlates more strongly with
  longitudinal decline and pathological staging.
- **Evidence**: §1 Introduction (Karikari et al., 2020; Mila-Aloma et al., 2022; Janelidze et al.,
  2023; Palmqvist et al., 2024; Ashton et al., 2024a,b; Ashton et al., 2021; Mattsson-Carlgren et
  al., 2023).
- **Implication**: Inconsistent cross-cohort findings sustain an ongoing debate about which isoform
  is optimal for clinical implementation.

### G1: No consensus on the optimal p-tau isoform across disease stages
- **Statement**: It is unknown which p-tau isoform (217, 181, or 231) is optimal for detecting Abeta
  pathology, tau pathology, and predicting cognitive decline, or whether the answer differs by
  disease stage.
- **Caused by**: O2, O5
- **Existing attempts**: Individual head-to-head studies and pairwise meta-analyses.
- **Why they fail**: They compare limited assay pairs in single cohorts, cannot integrate indirect
  evidence, and produce inconsistent conclusions.

## Key Insight
- **Insight**: Cast every biomarker+platform combination (e.g., p217_MS, p217_Ratio, p181_IA,
  p231_UGOT) as a distinct node in a network meta-analysis. This lets direct (head-to-head) and
  indirect evidence be integrated to rank all options simultaneously with a single reference
  comparator (p181_IA), across four separate diagnostic outcomes, while a hierarchical
  cohort-selection rule preserves statistical independence.
- **Derived from**: O5, G1, G2, G3
- **Enables**: A unified P-score (SUCRA-analogous) ranking that resolves the isoform, platform, and
  matrix debates in one framework, and supports stage-specific clinical recommendations.

## Assumptions
- A2: Selecting the single most comprehensive dataset per cohort yields statistically independent
  nodes (no patient counted twice).
```

### Cardinality / variability
Typically 3–5 Observations, 2–4 Gaps, exactly one Key Insight block, 3–5 Assumptions. RCTs tend to
have Observations framed around disease epidemiology and prior-trial results, with a single crisp Gap
("no approved therapy demonstrates X at an acceptable safety margin"); lab/mechanistic papers have
denser, more technical Observations (assay/cell-biology facts) and Gaps about unresolved cell-type or
pathway attribution; meta-analyses have Gaps about methodological fragmentation (as in the che26
example above).

### Availability notes
Mandatory core, never absent. Degradation signals:
- **Abstract-only sources** produce Observations that are just restatements of the abstract's
  background sentence, with `Evidence: Abstract` for every one of them — no section-level citations,
  no depth. This should score as materially weaker than an Observation grounded in an Introduction
  citation chain.
- **A Key Insight that merely restates the paper's method name** (rather than stating the actual
  creative leap connecting Observations/Gaps to the solution) indicates a shallow read; a real
  compiler run derives it from the actual `Derived from` chain, not the title.
- Gaps with generic `Existing attempts`/`Why they fail` (e.g. "prior work is limited") without
  specifics is a compression/laziness signal a metric should catch, distinguishable from a genuinely
  short paper by cross-checking against `related_work.md` breadth.

---

## Indicators
- reference comprehensiveness
    - citing contradicting claims
    - citing the full landscape that's relevant
        - implementation -- semantic scholar space: everything within island or k-nearest (500 ish) or undermind api
- gap
    - <> claims match
    - truthfulness compared against literature: existing attempts comprehensiveness
    - why existing attempts fail
- insight novelty & relevance
    - done before?
    - societal / science impact if solved
        - implication judgement call [sem]
- reference truthfulness (claim drift)

## 5. `logic/experiments.md` (declarative verification/analysis plans)

### Artifact + path
`logic/experiments.md`, e.g. `research/ara-library/huu25-apoe-e4-alzheimer-s-risk-converges/logic/experiments.md`.

### Purpose
"Experiment" generalized to the field's way of testing a claim — an eval run, a statistical test, a
sequencing+clustering pipeline stage, a clinical-trial analysis, a proof obligation. These are
**declarative plans, never scripts, and contain NO exact numerical results** — exact numbers live only
in `evidence/`. This file is what `claims.md`'s `Proof` field points into.

### Structure
One `## E{NN}: {Short title}` block per experiment/analysis. Every block has:

| Field | Type | Real example |
|---|---|---|
| `**Verifies**` | list[ref-id] — claim IDs from claims.md | `C01, C02, C05, C06` |
| `**Setup**` | nested key: value bullets — subkeys vary by field (`Design`, `Model`, `Hardware`, `Dataset`, `System`, `Assay`, `Sequencing`, `Pipeline`, `Reference standard`, etc. — free-form, whatever the work has) | `Assay: 10x Visium spatial gene expression, one section per donor, 31 samples` / `Pipeline: VistoSeg → SpaceRanger (GRCh38, 2020-A) → spatialLIBD QC → SpotSweeper → nnSVG → harmony → BayesSpace` |
| `**Procedure**` | numbered list[string], each an imperative step | `1. Segment slides, align capture areas, run SpaceRanger; QC spots (manual + SpotSweeper).` |
| `**Metrics**` | markdown-prose or list, what is measured (with units), NOT the value | `"per-SpD DEG counts (up/down, FDR<0.05); enriched GO terms; ancestry/sex-specific DEG counts."` |
| `**Expected outcome**` | list[string], directional/relative language ONLY — never an exact number | `"DEGs concentrate in white-matter and vascular SpDs; ancestry-specific sets differ; male-dominated sex-specific sets."` |
| `**Baselines**` | string — comparator method/group, or `none` | `"within-study comparison across SpDs."` or `"p181_IA reference comparator."` |
| `**Dependencies**` | list[ref-id] of other experiment IDs, or `none` | `E02` or `none` |

### A full realistic example

```markdown
## E03: APOE carrier DGE in spatial domains (+ ancestry- and sex-specific)
- **Verifies**: C03, C05, C06
- **Setup**: Visium pseudobulk per SpD (registration_pseudobulk, min_ncells=10); edgeR filtering;
  voomLmFit + limma.
- **Procedure**:
  1. Fit carrier model `~0 + APOE_syn + Sex + Age + Anc_Afr + pseudo_expr_chrM_ratio`, block on
     Visium slide; contrast E4+ vs E2+.
  2. Repeat with ancestry-combined covariate (carrier_Anc) and sex-combined covariate (carrier_Sex,
     excluding X/Y genes).
  3. GO overrepresentation on DEG sets (clusterProfiler).
- **Metrics**: per-SpD DEG counts (up/down, FDR<0.05); enriched GO terms; ancestry/sex-specific DEG
  counts.
- **Expected outcome**: DEGs concentrate in white-matter and vascular SpDs; ancestry-specific sets
  differ; male-dominated sex-specific sets.
- **Baselines**: within-study comparison across SpDs.
- **Dependencies**: E02
```

### Cardinality / variability
Seal Level 1 targets ≥3 blocks (never padded to hit the number). The two read ARAs have 6 (che26,
each block = one NMA outcome/subgroup analysis) and 8 (huu25, each block = one pipeline
stage/analysis: atlas-building, DGE, GO, trajectory, cross-dataset enrichment, MOFA). `Setup` subkeys
adapt heavily to genre: ML papers use `Model`/`Hardware`/`Dataset`; clinical trials use
`Population`/`Intervention`/`Endpoint`/`Randomization`; wet-lab/omics papers use
`Assay`/`Sequencing`/`Reference standard`; theory papers might replace `Procedure` steps with proof
obligations. The one invariant is **no exact numbers anywhere in this file**.

### Availability notes
Mandatory core. What signals thinness or a defect:
- **A number leaking into `Expected outcome` or `Metrics`** (e.g. "achieves 92% accuracy" instead of
  "achieves higher accuracy than baseline") is an explicit Critical Rule #3 violation — exact numbers
  belong only in `evidence/`. A metric can grep for digit patterns here as a cheap defect detector.
  (Percent symbols, CIs, and p-value thresholds that are themselves the *design* of the study — e.g. "FDR<0.05" as a stated significance threshold — are acceptable since they describe the test's decision rule, not its result.)
- **`Proof`/`Verifies` not resolving** — every `C##` cited here must exist in `claims.md` and every
  `E##` an experiment's `Dependencies` cites must exist in this same file (cross-layer binding, Seal
  Level 1 §9). A dangling reference is a structural defect.
  (Note: `Proof` lives on the *claim* block in `claims.md`, and it must point to an `E##` id here;
  `Verifies` lives on the *experiment* block here and must point back to a `C##` id in `claims.md` —
  the check runs in both directions.)
- **Systematic reviews / meta-analyses**: `Setup.Hardware`/`Model` fields are typically absent or
  `n/a`; `Setup.Design` (statistical model spec) dominates instead — this is correct, not thin.
- **Abstract-only compilation**: often produces the statutory minimum 3 experiments with generic,
  interchangeable `Procedure` steps inferred from the abstract's method sentence rather than a real
  Methods section — visibly less specific `Setup` detail than a full-text compile.

---

## indicators
- <> claim alignment [sem]
- comprehensiveness of reporting (briefly benchmark)
- taking into account existing efforts & the gap analysis
- reference reasonability

## 6. `logic/related_work.md` (typed dependency graph)

### Artifact + path
`logic/related_work.md`, e.g. `research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/logic/related_work.md`.

### Purpose
A typed graph of how this work depends on, extends, bounds, is baselined against, or refutes prior
work — preserving the paper's *full* citation footprint (not just the closest predecessors), so a
downstream agent can trace provenance of data, methods, and comparator claims.

### Structure
Full blocks for every citation with a **specific technical delta** (a dataset it supplied, a method it
contributed, a claim it bounds/extends/refutes):

```markdown
## RW{NN}: {Author et al., Year}
- **DOI**: {DOI or arXiv ID, or "Not specified in paper"}
- **Type**: {imports|bounds|baseline|extends|refutes}
- **Delta**:
  - What changed: {specific technical delta}
  - Why: {motivation}
- **Claims affected**: {claim IDs, or "none directly (motivation)"}
- **Adopted elements**: {what was kept/reused}
```

| Field | Type | Real example |
|---|---|---|
| `## RW{NN}` heading | ref-id + string | `## RW01: Janelidze et al., 2023` |
| `**DOI**` | string | `10.1093/brain/awac333` |
| `**Type**` | enum{`imports`, `bounds`, `baseline`, `extends`, `refutes`} (compound forms seen, e.g. `imports (data source)`, `imports (framework)`, `baseline / bounds`) | `imports (data source)` |
| `**Delta** → What changed` | markdown-prose | `"head-to-head comparison of 10 plasma phospho-tau assays in prodromal AD."` |
| `**Delta** → Why` | markdown-prose | `"selected as the most comprehensive head-to-head dataset for the BioFINDER-1 cohort."` |
| `**Claims affected**` | list[ref-id] of claim IDs, or `none` | `C01, C07` |
| `**Adopted elements**` | markdown-prose | `"BioFINDER-1 dataset (N=135; MCI/prodromal AD; p-tau 217/181/231; IP-MS and Simoa; CSF Abeta42/40)."` |

Beyond the full `RW##` blocks, remaining citations without a specific technical delta (background,
historical, infrastructure, inline-comparison references) are captured **briefly**, typically as a flat
bulleted list grouped under a heading like `## Background / supporting references (brief)` or folded
into an `## Additional citation footprint (briefer)` section — one bullet per reference:
`**Author et al., Year** (DOI) — one-line role.`

A special case seen in both real ARAs: a **non-bibliographic grounded source** the paper itself
depends on but that isn't an "RW" citation — e.g. a trial/review registration. This is folded in as its
own small block before the numbered RW list, e.g. `## Review registration (folded-in grounded source)`.

### A full realistic example

```markdown
## RW01: Janelidze et al., 2023
- **DOI**: 10.1093/brain/awac333
- **Type**: imports (data source)
- **Delta**:
  - What changed: head-to-head comparison of 10 plasma phospho-tau assays in prodromal AD.
  - Why: selected as the most comprehensive head-to-head dataset for the BioFINDER-1 cohort.
- **Claims affected**: C01, C07
- **Adopted elements**: BioFINDER-1 dataset (N=135; MCI/prodromal AD; p-tau 217/181/231; IP-MS and
  Simoa; CSF Abeta42/40).

## Background / supporting references (brief)
- **Hansson et al., 2023** (10.1038/s41582-023-00403-3) — blood biomarkers in clinical practice/trials; motivation.
- **Schindler et al., 2022** (10.1212/WNL.0000000000200358) — effect of race on plasma-based amyloid prediction; cross-ethnic motivation (C05).
```

### Cardinality / variability
Full `RW##` block count scales with how many primary sources/datasets/methods the paper actually
draws on: che26 (a meta-analysis synthesizing 18 studies) has 16 full RW blocks (12 "included primary
studies," 4 "conceptual/methodological anchors") plus ~19 brief background references; huu25 (a
single-cohort wet-lab study) has 18 full RW blocks (mostly method/tool citations: BayesSpace, Harmony,
spatialLIBD, RCTD, LIANA+, MOFAcellulaR, ...) plus a long "additional citation footprint" grouping
~40 more references by reference-number range. A theory paper's RW graph skews toward `extends` and
`bounds` types (prior theorems it builds on/is bounded by); a meta-analysis skews toward `imports
(data source)`; an applied ML paper skews toward `baseline` (methods it benchmarks against).

### Availability notes
Mandatory core, never structurally absent. Signals of thinness:
- **Only full RW blocks, no "brief" tier** — means the compiler didn't sweep the full References list,
  failing the coverage requirement that the ARA "reflect the paper's full citation footprint," not
  just the closest predecessors (Seal Level 1 explicitly checks for this).
- **`refutes`-type edges are rare in practice** — most papers build on rather than refute prior work;
  their absence is normal, not a defect, unless the source paper explicitly states it's overturning a
  specific prior finding and the ARA fails to capture that edge.
- Abstract-only sources: `related_work.md` will contain at most 1–3 RW blocks (whatever's citable from
  the abstract itself) and no meaningful "brief" tier — a stark, scoreable gap versus a full-text
  compile with 15+ blocks.

---

## indicators
- claim drift
- gap size / novelty
- replication bonus points
- dependency graph comprehensiveness
- method improvement

## 7. `logic/solution/` (method layer: `constraints.md` + warranted method files)

### Artifact + path
`logic/solution/constraints.md` (always present) plus zero or more sibling files named for what the
work actually has: `study_design.md`, `method.md`, `architecture.md`, `algorithm.md`,
`heuristics.md`, `formalization.md`, `proofs.md`, `design.md`. Example paths:
`research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/logic/solution/{constraints.md,study_design.md}`,
`research/ara-library/huu25-apoe-e4-alzheimer-s-risk-converges/logic/solution/{constraints.md,method.md,study_design.md}`.

### Purpose
The "how" layer: the concrete method(s) the paper used, expressed at whatever granularity and in
whatever file(s) genuinely fit this work — plus, always, the boundary conditions / assumptions /
limitations that bound how far the results generalize. There is no fixed template — the compiler
picks file names that describe THIS paper's actual method structure.

### Structure

**`constraints.md`** (always present, free-form but conventionally three sections):
```markdown
# Constraints, Assumptions, and Limitations

## Boundary conditions
- {bullet: scope limits}

## Assumptions
- A1: {assumption, may re-list from problem.md or be method-specific}

## Known limitations (§X.Y)
- **{limitation name}**: {markdown-prose}
```
Types: every bullet is markdown-prose string; assumption IDs are ref-ids (`A1`, `A2`, ...).

An additional, compiler-added subsection is common and valuable:
`## Additional caveats surfaced during compilation (data-quality notes)` — internal
inconsistencies the compiler noticed in the source (e.g. a table's row count not matching its
caption, or PRISMA-diagram arithmetic not reconciling) that are transcribed faithfully in the
evidence layer but flagged here so downstream agents don't over-trust process counts. Type: markdown-
prose bullets, each naming the specific object and the specific discrepancy.

**Method files** (`study_design.md`, `method.md`, etc.) — no fixed schema; each is markdown-prose
organized under `##`/`###` headings that mirror the paper's own Methods structure. Common recurring
sub-patterns across genres:
- Clinical/review genre (`study_design.md`): `## Reporting standard and registration`,
  `## Search strategy and data sources`, `## Inclusion / exclusion criteria`,
  `## Statistical analysis`, `## Outcomes analyzed`.
- Omics/wet-lab genre (`study_design.md` + `method.md`): `## Cohort`, `## Assays (paired, per donor)`,
  `## Analysis pipeline (high level)`, `## Statistical models`, and a separate detailed `method.md`
  with per-substage QC parameters (`## Visium raw processing & QC`, `## snRNA-seq clustering`, ...),
  each line densely grounded with exact pipeline values (`"BayesSpace v1.11.0 spatialCluster(nrep=20000)
  over k=2..28; optimal k=9"`).
- ML/architecture genre (not in the two read ARAs, per schema): `architecture.md` (component graph:
  name/purpose/inputs/outputs/interactions per component), `algorithm.md` (LaTeX formulation +
  reconstructed pseudocode + complexity analysis "only if the paper states or clearly implies it").

**`heuristics.md`** (present only when the paper states implementation tricks/gotchas — optional even
among method-file-rich ARAs; neither che26 nor huu25 has one, but `ali25-multimodal-self-supervised-
learning-for-early` does). One `## H{NN}: {description}` block per heuristic:

| Field | Type | Real example |
|---|---|---|
| `**Rationale**` | markdown-prose | `"The learned gate α=σ(w^T[1_MRI,1_PET]) drives α→1 (so (1-α)→0) when PET is missing, enabling robust MRI-only inference..."` |
| `**Sensitivity**` | enum{`low`,`medium`,`high`} or `"Not specified in paper"` | `high — §3.8 plans to remove histogram matching / ComBat / both and measure cross-site impact (results not reported)` |
| `**Bounds**` | string — acceptable range/limits, or `"Not specified in paper"` | `α∈[0,1]; late fusion at embedding level` |
| `**Code ref**` | list[ref-path] to a real `src/execution/` file, or `"Not specified"` | `[src/execution/ssl_losses.py]` |
| `**Source**` | string — section/table in paper | `§3.4, Eq. 8, Figure 5` |

### A full realistic example

`constraints.md` (che26):
```markdown
## Boundary conditions
- Scope is limited to **blood-based p-tau biomarkers** (plasma or serum) for AD; only isoforms
  p-tau217, p-tau181, p-tau231 on platforms MS/Simoa/MSD/Lumipulse were compared.
- Findings are relative **rankings (P-scores) and AUC mean differences vs. a p181_IA baseline**, not
  absolute pooled sensitivity/specificity/AUC for each marker.

## Assumptions
- A2: Selecting the single most comprehensive dataset per cohort yields statistically independent
  nodes (no patient double-counted).

## Known limitations (§4.5)
- **Batch effects**: although platforms were adjusted for, batch effects in manual immunoassays may
  still exist.

## Additional caveats surfaced during compilation (data-quality notes)
- **Table 1 vs. its caption**: Table 1 lists **12 cohort rows**, but its caption says it details "the
  6 core representative cohorts..." ADNI is named in the caption and abstract as a screened
  overlapping cohort but has **no row** in Table 1. The 12 tabulated cohorts also do not equal the
  stated 18 studies / 24 datasets.
```

A heuristic block (from `ali25-multimodal-self-supervised-learning-for-early/logic/solution/heuristics.md`):
```markdown
## H03: Train-time PET→MRI distillation for MRI-only deployment
- **Rationale**: When both modalities are present in training, distilling stop-gradient PET
  embeddings into the MRI pathway (Eq. 11) retains molecular knowledge for later MRI-only inference.
- **Sensitivity**: Not specified in paper
- **Bounds**: Active only for subjects with PET; training-only (not at inference)
- **Code ref**: [src/execution/ssl_losses.py](../../src/execution/ssl_losses.py)
- **Source**: §3.4, Eq. 11
```

### Cardinality / variability
`constraints.md`: always exactly one file, 2–4 top-level sections, several bullets each. Method files:
0 to 3+ additional files depending on how the paper's method decomposes — che26 has just
`study_design.md` (one method file, since it's pure statistical synthesis); huu25 has
`study_design.md` + `method.md` (cohort/pipeline design split from detailed per-substage QC
parameters). `heuristics.md`, when present, typically has 3–8 `H##` blocks.

### Availability notes
`constraints.md` is mandatory core — never absent, though it can be thin (a bare "no limitations
stated" is a red flag, since essentially every paper states some caveat). Beyond it:
- **`heuristics.md` correctly absent** for most papers — do NOT penalize its absence generically; only
  penalize it when the paper visibly states implementation tricks/gotchas (e.g. an ML paper with an
  "Implementation details" subsection) and none were captured.
- **Method-file naming forced onto the wrong genre** is itself a defect: e.g. a `training.md`/
  `model.md` appearing for a paper that trained no model, or an `architecture.md` for a pure
  statistical-synthesis review — Seal Level 1 explicitly flags this (§2 of the validation checklist).
- **Data-quality-caveats subsection missing** when the source table/figure numbers actually don't
  reconcile (as in che26's Table 1 vs. caption mismatch) is a coverage gap a metric can specifically
  probe by cross-checking `evidence/` tables' own internal-consistency notes against whether
  `constraints.md` mentions them.
- Abstract-only sources: `constraints.md` reduces to whatever caveats the abstract itself states
  (often none), and no method file is generated at all beyond the bare mandatory `constraints.md` —
  a stark, easily-detected floor case.

---

## Indicators (solution/method layer)
**constraints indicators**
- conditionality: how generalizable is this?
- validity given claim <> experiment gaps or match
- assumption realisticness & validity & fairness: is this a dreamcase scenario or real
- limitation validity (does this add new conditions for existing hypotheses, maybe under constraints)
**method indicators**
- method validity
- method -> constraint reasonability
- method novelty
- method verification status (widely accepted method vs generalizing something specific that may not apply; justified/reasoned/explained?)
- solid combination of perspectives (e.g. wet lab & computational) vs a single one? reflected in constraints?
**heuristics indicators**
- does this reflect the constraints or are we not accounting for the heuristics sufficiently
- is this there? should always be (there's always some abstraction)
- how far is this removed from the optimum?

## 8. `trace/exploration_tree.yaml` (the exploration DAG)

### Artifact + path
`trace/exploration_tree.yaml`, e.g. `research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/trace/exploration_tree.yaml`.

### Purpose
The "git log" for the research — a structured, traversable record of the paper's actual decision
trajectory: every question asked, experiment run, decision made with rejected alternatives, dead end
hit, and pivot taken. **Dead-end nodes are the single most valuable node type for downstream agents**
because they save future work from rediscovering known failures.

### Structure
Top-level YAML key `tree:`, a list of nodes; nodes nest via a `children:` list (primary DAG structure)
plus an `also_depends_on:` list on any node for cross-edges beyond simple nesting (turning the nested
tree into a true DAG). Every node, regardless of type, has:

| Field | Type | Example |
|---|---|---|
| `id` | string, `N{NN}` | `N04` |
| `type` | enum{`question`, `experiment`, `dead_end`, `decision`, `pivot`} | `experiment` |
| `support_level` | enum{`explicit`, `inferred`} | `explicit` |
| `source_refs` | list[string] (recommended for `explicit` nodes; table/figure/section refs) | `["Table 2 Outcome 1", "Figure 3A", "§3.2"]` |
| `title` | string | `"NMA of diagnostic accuracy for amyloid-beta positivity (E01)"` |
| `also_depends_on` | list[ref-id] (optional; DAG convergence only) | `[N04]` |
| `children` | list[node] (optional — absent for `dead_end`, which is always a leaf) | — |

Type-specific **required** fields beyond the shared set:

| Type | Required fields | Type |
|---|---|---|
| `question` | `description` | markdown-prose |
| `experiment` | `result`; optional `evidence` | `result`: markdown-prose; `evidence`: list[ref-id \| string] mixing claim IDs and figure/table/section refs, e.g. `[C01, C08]` or `["Figure 3"]` |
| `decision` | `choice`, `alternatives`; optional `evidence` | `choice`: string; `alternatives`: list[string]; `evidence`: string (informal, prose — not a list here) |
| `dead_end` | `hypothesis`, `failure_mode`, `lesson` | all markdown-prose strings |
| `pivot` | `from`, `to`, `trigger` | all strings |

### A full realistic example (one of each node type, drawn from real trees)

```yaml
tree:
  - id: N01
    type: question
    support_level: explicit
    source_refs: ["§1 Introduction", "§2 Methods", "Abstract"]
    title: "Which plasma p-tau isoform, platform, and matrix is optimal across the AD continuum?"
    description: "No consensus exists on the optimal p-tau isoform (217/181/231), analytical platform (MS vs. immunoassay), or matrix (plasma vs. serum) for detecting Abeta pathology, tau pathology, and predicting cognitive decline. The review asks this simultaneously via network meta-analysis."
    children:
      - id: N03
        type: decision
        support_level: explicit
        source_refs: ["§2.3"]
        title: "Hierarchical de-overlapping of shared cohorts (crucial step)"
        choice: "For each shared cohort (BioFINDER-1/2, ADNI, TRIAD, WRAP), select only the single most comprehensive dataset (or one per distinct clinical outcome)."
        alternatives:
          - "Pool all studies naively (double-counts patients)"
          - "Exclude all overlapping cohorts entirely"
        evidence: "Yielded 24 statistically independent datasets from 18 publications; preserves statistical independence."
        children:
          - id: N04
            type: experiment
            support_level: explicit
            source_refs: ["Table 2 Outcome 1", "Figure 3A", "§3.2"]
            title: "NMA of diagnostic accuracy for amyloid-beta positivity (E01)"
            result: "p217_MS ranked first (P-score 0.859), then p217_Ratio (0.783) and p217_ALZpath (0.686); p181_IA ranked last (0.117). p217_MS AUC advantage vs. baseline MD 0.10 [0.04; 0.16]."
            evidence: [C01, C08]

  - id: N05
    type: experiment
    support_level: explicit
    source_refs: ["§3.6", "Supplementary Table S2"]
    title: "Meta-analysis of the incremental AUC gain from the ratio (E02)"
    result: "Ratio vs. single-analyte gave a significant MD of 0.025 (95% CI 0.005-0.045) with zero heterogeneity (I2 = 0%)."
    also_depends_on: [N04]
    evidence: [C02]

  - id: N11
    type: dead_end
    support_level: explicit
    source_refs: ["Table 2", "§4.1"]
    title: "Standard p-tau181 immunoassay as a high-precision AD marker"
    hypothesis: "p-tau181 (the historical plasma standard) would remain competitive for high-precision diagnosis and staging."
    failure_mode: "p181_IA ranked last or near-last on every outcome (Abeta 0.117; MCI-to-AD 0.159; Tau-PET 0.090; platform 0.006) and failed to discriminate Tau-PET status."
    lesson: "Standard p-tau181 is effectively obsolete for high-precision AD diagnostics (P-score < 0.20); use p-tau217 variants instead."

  - id: N14
    type: pivot
    support_level: inferred
    title: "Reframe isoform choice as a stage-dependent 'relay' rather than a single winner"
    from: "Seeking one universally optimal p-tau isoform"
    to: "A relay: p-tau231 for earliest asymptomatic amyloidosis, p-tau217 for symptomatic diagnosis/staging/prognosis"
    trigger: "Divergent subgroup rankings (N09, N12): p-tau231 tops the preclinical subgroup while p-tau217 dominates symptomatic outcomes."
    also_depends_on: [N09, N12]
```

### Cardinality / variability
Target is ~8+ nodes for a rich paper, but this is source-bounded, never a quota — a paper that hides
its failures yields a smaller, honest tree. The two read ARAs have 14 nodes (che26: 1 question, 4
decisions, 6 experiments, 2 dead_ends, 1 pivot) and 17 nodes (huu25: 1 question, 2 decisions, 9
experiments, 4 dead_ends, 1 pivot). `dead_end`/`decision` nodes are expected whenever the paper reveals
ablations, rejected alternatives, or explicit design choices, but must never be invented to hit a
count — a systematic review with no stated failed approaches legitimately has zero `dead_end` nodes.
`support_level: inferred` is common specifically on `pivot` nodes, since a pivot is usually the
compiler's own narrative reconstruction of the paper's trajectory rather than something the paper
states in so many words — real trees mark this honestly rather than dressing an inferred pivot up as
`explicit`.

### Availability notes
Mandatory core — the file must exist and parse as valid YAML with a `tree:` key, but its **richness**
is the single biggest genre-dependent variable in the whole ARA:
- **Reviews/meta-analyses have no first-person "we tried and failed" narrative** in the way a single
  wet-lab study does — their dead_ends instead come from the paper's own explicit ranking failures
  (e.g. che26's N11: p181_IA is a "dead end" only in the sense that the review's own data shows it
  fails as a diagnostic — this is a legitimate, explicit dead_end even in a synthesis genre).
- **A tree with zero `dead_end`/`decision` nodes** is not automatically a defect — it can mean the
  paper genuinely reports no rejected alternatives — but combined with a `support_level: explicit`
  paper of a genre known to involve iteration (e.g. a method paper), it is a strong signal of shallow
  extraction and should be scored down.
- **Invented/unsupported nodes are the specific thing Seal Level 1's "Trace Hygiene" check targets**:
  any `dead_end`, `decision`, or `experiment` node not traceable to the source material fails outright
  — a metric can spot-check `source_refs` against the paper the same way the validator does.
  Corresponding is the softer companion check ("no synthetic trace history"): a node with no
  `source_refs` and `support_level: explicit` (mismatched signaling) is itself a defect even short of
  outright invention.
- **Abstract-only compilation**: the tree collapses to essentially one `question` node and maybe one
  `experiment` node paraphrasing the abstract's method sentence — no decisions, no dead ends, because
  none of that granularity is recoverable from an abstract. This is the clearest "floor" example for
  this artifact.

---

## indicators
- did this start from a logical place, i.e. where the current literature left off
- are there abandoned paths that are reasoned about and explained
- is there enough on the abandoned paths to let others avoid the same potholes (context, constraints, heuristics, methods, reasoning)?
- is the dag validly structured?
- how comprehensive is this (esp. if a clinical trial report is available)
- does this include references that are in the according claim references?
- does this miss references that a search bot deems relevant? (penalize prev work for not making abandoned paths available/discoverable/comprehensive enough)
- does this add substantial coverage over a hypothesis in terms of failure modes

## 9. `evidence/` (README.md index + `tables/*.md` + `figures/*.md`)

### Artifact + path
`evidence/README.md`, `evidence/tables/table{N}.md` (+ sibling `.png`), `evidence/figures/figure{N}.md`
(+ sibling `.png`); optionally `evidence/proofs/{name}.md` for theory/derivation work (not present in
either fully-read example ARA, but specified by the schema for theorem/lemma statements + proof
sketches). Example: `research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/evidence/{README.md,tables/table1.md,tables/table2.md,figures/figure1.md,figures/figure2.md,figures/figure3.md}` (plus matching `.png` files).

### Purpose
The grounded, verbatim record of every numbered table and figure in the source, transcribed
completely and in order — the raw material every number in `claims.md` ultimately traces back to.
This is a **systematic sweep**, not a sample: every `Table N`/`Figure N` in the main text (and
appendices) gets filed, or is explicitly accounted for in `README.md` with a reason if deliberately
skipped (e.g. an exact duplicate, or supplementary material not present in the fetched source).

### Structure

**`evidence/README.md`** — an index:
```markdown
# Evidence Index

## Tables
| File | Source | Claims | Description |
|------|--------|--------|-------------|
| [tables/{name}.md](tables/{name}.md) | Table N, §X.Y | C01, C02 | {one sentence} |

## Figures
| File | Source | Claims | Description |
|------|--------|--------|-------------|
| [figures/{name}.md](figures/{name}.md) | Figure N, §X.Y | C03 | {one sentence} |

## Completeness note / Supplementary objects — accounted for, not filed
{prose explaining exactly what was filed, what wasn't, and why}
```
Fields: `File` = ref-path; `Source` = string (`"Table 2, §3.2-3.5"`); `Claims` = list[ref-id] or `—`;
`Description` = one-line string. The closing prose section is mandatory-in-spirit even though
free-form: it must state the exact count of numbered objects in the source and confirm none were
silently skipped, or name precisely which ones were not filed and why.

**`evidence/tables/{name}.md`** (+ sibling `.png`):

| Field | Type | Real example |
|---|---|---|
| `# Table {N} - {Caption or short description}` | markdown H1 | `# Table 2 - Ranking of diagnostic accuracy based on SUCRA values` |
| `**Source**` | string | `"Table 2 in \"Diagnostic performance of plasma p-Tau217...\" (Chen et al., 2026), page 6"` |
| `**Caption**` | string, verbatim or near-verbatim | `"Ranking of diagnostic accuracy based on SUCRA values."` |
| `**Screenshot**` | ref-filename | `table2.png` |
| `**Extraction type**` | enum{`raw_table`, `derived_subset`} | `raw_table` |
| (if `derived_subset`) `**Derived from**` | ref-filename of the parent raw table | `` `table3_imagenet_validation.md` `` |
| table body | markdown-table, exact cell values, never rounded | see example below |
| `**Notes**` (optional) | markdown-prose bullets — caveats, internal-consistency flags | see example below |

**`evidence/figures/{name}.md`** (+ sibling `.png`) — shared header on every figure regardless of
type, then a type-specific body:

| Field | Type | Real example |
|---|---|---|
| `**Source**` | string | `"Figure 3, Section 3.2 / 3.4, page 6"` |
| `**Caption**` | string, verbatim/near-verbatim | full caption text |
| `**Screenshot**` | ref-filename | `figure3.png` |
| `**Figure type**` | enum{`quantitative_plot`, `diagram`, `qualitative_sample`, `mixed`} | `quantitative_plot` |
| `**Extraction method**` | enum{`exact_from_labels`, `digitized_estimate`, `visual_description`} | `exact_from_labels` |
| `**Reading confidence**` | enum{`high`, `medium`, `low`} | `high` |

Type-specific body:
- **`quantitative_plot`**: `**Plot kind**` enum{line,bar,scatter,box,histogram,heatmap,forest plot,...};
  `**Axes**` string stating label/units/**scale** (`linear`|`log`) for X and Y; a markdown data table
  (columns = X + one per series; values `≈`-prefixed if `digitized_estimate`, bare if
  `exact_from_labels`); a `## Trend summary` prose paragraph (mandatory even when exact points are
  unreadable — in that case `Reading confidence: low` plus the trend summary substitutes for the
  table).
- **`diagram`**: NO data table. A `## Visual description` block with `**Components**`,
  `**Connections**`, `**Annotations**`, `**What it conveys**` — all markdown-prose strings.
- **`qualitative_sample`**: NO data table. A `## Visual description` block with `**Shows**`,
  `**Demonstrates**`, `**Supports**` (the last a claim/gap ref-id).
- **`mixed`**: figure is split per panel, each panel classified and handled per its own type (a
  diagram panel gets a Visual description, a data panel gets a table) — never collapsed together.

### A full realistic example

`evidence/tables/table2.md` (raw_table):
```markdown
# Table 2 - Ranking of diagnostic accuracy based on SUCRA values

**Source**: Table 2 in "Diagnostic performance of plasma p-Tau217, p-Tau181, and p-Tau231 across the
Alzheimer's disease continuum: a network meta-analysis" (Chen et al., 2026), page 6
**Caption**: "Ranking of diagnostic accuracy based on SUCRA values." Footnote: "SUCRA (surface under
the cumulative ranking) and P-scores for each biomarker across different diagnostic outcomes."
**Screenshot**: table2.png
**Extraction type**: raw_table

Values are P-scores (SUCRA analog, 0-1); higher = higher probability of being the best test. "—" = no
entry (fewer nodes ranked for that outcome).

| Rank | Outcome 1: diagnostic accuracy (Aβ pathology) — Biomarker (P-score) | ... |
|------|--------------------------------------------------------------------|-----|
| 1 | p217_MS (0.859) | ... |
| 8 | p181_IA (0.117) | ... |

**Notes**:
- Node labels: p217 = p-tau217, p181 = p-tau181, p231 = p-tau231; MS = mass spectrometry...
- p217_MS ranks 1st on all four outcomes.
```

`evidence/figures/figure3.md` (`quantitative_plot`, `exact_from_labels`):
```markdown
# Figure 3 - Relative diagnostic performance of plasma p-tau biomarkers vs. p-Tau181 (IA)
- **Source**: Figure 3, Section 3.2 / 3.4, page 6
- **Caption**: "Relative diagnostic performance of plasma p-tau biomarkers compared to p-Tau181 (IA). ..."
- **Screenshot**: figure3.png
- **Figure type**: quantitative_plot
- **Extraction method**: exact_from_labels
- **Reading confidence**: high
- **Plot kind**: forest plot (two panels)
- **Axes**: Panel A — X = AUC Difference vs. p-Tau181 (Baseline), linear, ticks at −0.15..0.15; Y = biomarker (categorical).

## Panel A — AUC Difference vs. p-Tau181 for detecting amyloid-β pathology
| Biomarker (Site_Platform) | MD | 95% CI |
|---------------------------|------|--------------|
| p217_MS | 0.10 | [0.04; 0.16] |
| p231_UGOT | 0.00 | [−0.07; 0.07] |

## Trend summary
Panel A: p217_MS, p217_Ratio, p217_ALZpath, and p217_Lumi have 95% CIs excluding 0 (significant AUC
advantage over p-tau181); p217_IA, p217_Lilly, and p231_UGOT have CIs crossing 0 (not significant).
```

`evidence/figures/figure1.md` (`diagram`, `visual_description`) — the PRISMA flow diagram:
```markdown
# Figure 1 - PRISMA flow diagram of study selection
- **Figure type**: diagram
- **Extraction method**: visual_description
- **Reading confidence**: high

## Visual description
- **Components**: "Records identified from Pubmed, Embase, Cochrane, WOS (n = 179+311+256+195)" →
  "Records removed before screening" → "Records screened (n = 601)" → ... → "Studies included (n=18)".
- **Connections**: standard top-down PRISMA flow with right-pointing arrows to exclusion boxes.
- **What it conveys**: the funnel from initial database records to the final 18 included studies.

## Transcribed numbers (verbatim from the diagram)
| Stage | Value |
|-------|-------|
| Records screened | n = 601 |
| Studies included in review | n = 18 |

**Data-quality caveats**: the database counts (179+311+256+195 = 941) do not reconcile with 601
screened after removing 219 duplicates; values are transcribed exactly as printed, not corrected.
```

### Cardinality / variability
Exactly one pair (`.md` + `.png`) per numbered table and per numbered figure in the source, no more,
no fewer — che26 has 2 tables + 3 figures (all filed); huu25 has 0 numbered main-text tables (all 17
tables are supplementary) + 6 numbered main-text figures (all filed). `quantitative_plot` is the most
common figure type in quantitative papers; `diagram` dominates in method-overview figures (PRISMA
flows, pipeline schematics, network-geometry plots); `qualitative_sample` appears for representative
images/failure cases; `mixed` appears for multi-panel figures combining several of the above (seen in
`ave25-uncovering-plaque-glia-niches-in-human/evidence/figures/figure3.md`, a 9-panel figure with
diagram, Venn-count table, box-plot data, and representative-image panels all in one file, each
sub-scored with its own `Reading confidence`).

### Availability notes
Mandatory core, and this is the artifact where "absence must be accounted for, not skipped" is most
explicit and most checkable:
- **Every numbered object not filed must be named in `README.md` with a reason** — an ARA that quietly
  files only some of the source's tables/figures fails Seal Level 1 outright (§11, Evidence Ledger
  Completeness). This is directly checkable: count `Table N`/`Figure N` mentions in the source vs.
  files present vs. objects named as intentionally-skipped in README.
- **Supplementary-only material genuinely absent from the fetched source** (huu25's Fig S1–S47 / Table
  S1–S17 live in a separate 39MB supplement PDF not part of the fetched HTML) is the correct, honest
  form of absence — `README.md` names this explicitly rather than silently omitting it, and downstream
  layers still summarize supplementary content where it supports a claim (e.g. "Table S13 Oligo.3 DEG
  counts → C01").
- **A `quantitative_plot` with no data table and no low-confidence trend-summary fallback** is a
  structural failure — the spec requires one or the other, never neither.
- **An estimated reading mislabeled `exact_from_labels`** (should be `digitized_estimate` with `≈`
  markers) is a specific, checkable honesty violation the validation checklist calls out.
- **A `diagram`/`qualitative_sample` file containing a fabricated numeric table** is an explicit
  violation (Critical Rule #11) — these types must never masquerade as quantitative.
- Paywalled/abstract-only sources: **`evidence/` is the artifact hit hardest** — typically zero or
  near-zero tables/figures filed (nothing to screenshot), which should read as a near-total loss of
  grounding capacity, not a small gap, since almost every claim's `Sources` entry depends on this
  layer existing.

---

## indicators
- does evidence include fig + data + code for e2e reproducibility (reproducibility: constraints, experimental setup & comprehensive reporting)
- ev <> claim match
- ev <> constraints
- ev <> method
- reproduction value: does this confirm existing hypotheses (replication vs a new perspective on the same thing)

## 10. `src/environment.md` + `src/artifacts.md` / `src/configs/*.md` / `src/execution/*`

### Artifact + path
`src/environment.md` (always present); `src/artifacts.md`, `src/configs/{name}.md`,
`src/execution/{module}.{py,r,...}`, `src/prompts/*` (all "as warranted"). Examples:
`research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/src/{environment.md,artifacts.md}`;
`research/ara-library/huu25-apoe-e4-alzheimer-s-risk-converges/src/{environment.md,artifacts.md}`;
`research/ara-library/aki26-molecular-signatures-of-resilience-to-alzheimer/src/{execution/pretrained_model.py,configs/pipeline_parameters.md}`.

### Purpose
The concrete, physical implementation layer — reproducibility metadata plus whatever real
code/config/artifact content the source actually contains, captured in native form rather than
re-encoded as prose. The governing rule: **capture every concrete artifact that exists; never
manufacture one that doesn't.** A prose-only method already lives in `logic/solution/` — duplicating
it here as a fabricated code stub is explicitly forbidden.

### Structure

**`src/environment.md`** (mandatory core, one per ARA):

| Field | Type | Real example |
|---|---|---|
| `**Language/runtime**` | string, or `"analytical — none"` for non-computational work | `"R versions 4.3 to 4.5 (Bioconductor 3.18 to 3.21); Python (nuclei-count workflow, LIANA+); Shell"` |
| `**Framework**` | string | `` `netmeta` R package, version **4.5.2** `` |
| `**Hardware**` | string, or `"n/a"` | `"Joint High Performance Computing Exchange (JHPCE) cluster, Johns Hopkins Bloomberg School..."` |
| `**Data sources**` | string/list | GEO accessions, cohort names, access levels |
| `**Key dependencies**` | string/list, versioned | `"SpaceRanger v2.1.0 (+ v4.0.1 segment), CellRanger v7.2.0; ... edgeR v4.6.2, limma v3.64.1, ..."` |
| `**Protocols**` | string | `"PRISMA-DTA. Prospectively registered on PROSPERO, CRD420261327845."` |
| `**Random seeds**` | string, or `"Not specified in paper"`/`"n/a"` | `"Not specified in paper (BayesSpace nrep=20000... are stated; explicit RNG seeds are in repo log files, not the manuscript)."` |

Often extended with a `## Code availability` subsection (markdown-prose explaining *why* no code
exists, when that's the case) and a `## Data availability` subsection (verbatim quote of the paper's
own Data Availability Statement).

**`src/artifacts.md`** (for non-code deliverables, or when a repo exists but wasn't cloned/captured
into `src/execution/`) — one block per artifact:

```markdown
## {Artifact name}
- **File(s) in repo**: {real path(s), verified to exist, or "not a repo file" for registrations}
- **Nature**: {tool / library / skill spec / system / dataset / registration}
- **What it does / contains**: {grounded description}
- **How to use / run**: {entry point, command, or interface}
- **Claims supported**: {C## ids, or "all"}
```
Field types: all markdown-prose strings except `Claims supported` (list[ref-id] or `all`).

**`src/configs/{name}.md`** — one file per config category the work actually has (e.g.
`pipeline_parameters.md`, `assay_parameters.md`), each a sequence of per-parameter blocks:

```markdown
## {Parameter name}
- **Value**: {exact value}
- **Rationale**: {why this value, or "Not specified in paper"}
- **Search range**: {if mentioned}
- **Sensitivity**: {low|medium|high|"Not specified in paper"}
- **Source**: {section/table}
```

**`src/execution/{module}.py`** (or `.r`, etc.) — present only when the source provides concrete
code-shaped content. First line always declares grounding:
```python
# Grounding: transcribed   — adapted from repo code; cite file:line in docstrings
# Grounding: reconstructed — from explicit paper pseudocode/equations; cite §/eq
```
`transcribed` files are copied faithfully in native form (full function bodies, real imports, real
CLI/argparse/logging scaffolding) — never stripped to signatures-only. `reconstructed` files are
minimal stubs of only the novel mechanism, typed signatures using only source-stated names, with
unspecified logic left as `raise NotImplementedError("Not specified in paper")`.

### A full realistic example

`src/environment.md` (che26 — the "no code" case, explicitly justified):
```markdown
# Environment

This is an **analytical secondary-data study** (systematic review + network meta-analysis). No
primary data were collected, no model was trained, and no analysis code or accessioned dataset was
released by the authors.

- **Language/runtime**: R (Foundation for Statistical Computing). Version not specified in paper.
- **Framework**: `netmeta` R package, version **4.5.2** — random-effects frequentist network
  meta-analysis (§2.5).
- **Hardware**: n/a (statistical synthesis of summary data).
...

## Code availability
No Code Availability statement; no GitHub/GitLab/Zenodo/OSF/Dryad repository is referenced in the
article or found via web search (sources.yaml, verified). As a summary-data NMA, no analysis code was
released — hence no `src/execution/` code files (a `.py` stub reconstructed from the prose methodology
would only duplicate `logic/solution/study_design.md`).
```

`src/artifacts.md` (huu25 — the "repo exists but wasn't cloned" case):
```markdown
## LFF_spatial_ERC analysis pipeline (R + Shell + Python)
- **File(s) in repo**: GitHub `LieberInstitute/LFF_spatial_ERC` (default branch `devel`). Verified
  top-level entries: `code/`, `processed-data/`, `raw-data/`, ... (verified via GitHub contents API).
- **Nature**: Full end-to-end analysis pipeline (specialized to this project's data).
- **What it does / contains**: `code/` numbered stages: `00_project_prep`, `01_spaceranger`, ...
  `14_MOFA` — multicellular factor analysis (Figure 6). ...
- **How to use / run**: `git clone` (README notes this may take up to an hour due to size); open
  `LFF_spatial_ERC.Rproj`; run stage scripts on an HPC/JHPCE-like environment.
- **Claims supported**: all (C01–C08).
```

`src/execution/pretrained_model.py` (aki26 — the `transcribed` case, real notebook code kept native):
```python
# Grounding: transcribed
# Source: pretrained_model.ipynb (author repo AkilaRanjith/Molecular-Signatures-of-Resilience...); code cells only (outputs stripped).

import os
import scanpy as sc
import scvi
...
vae_q = scvi.model.SCANVI.load_query_data(adata_query, "path to downloaded pretrained exc model")
vae_q.train(max_epochs=200, n_samples_per_label=2000, plan_kwargs=dict(weight_decay=0.0), check_val_every_n_epoch=10)
```

A config block (aki26 `src/configs/pipeline_parameters.md`):
```markdown
### Minimum genes per nucleus (initial → final)
- **Value**: initial filter <200 genes removed (→549,074); final cutoff **300** genes (tested 200–500)
- **Rationale**: Ex5 has low gene counts; 300 balances retention vs quality; separate rescue of
  200–300-gene nuclei (62,498; 48,849 kept at 99% scANVI probability).
- **Sensitivity**: high (drove a dedicated sensitivity analysis).
- **Source**: Methods; Supplementary Fig. 8.
```

### Cardinality / variability
`environment.md`: always exactly one. `artifacts.md`: 0–1 file but internally 1–4+ blocks (che26 has
3: PROSPERO registration, extracted summary-data, underlying cohorts; huu25 has 3: the analysis
pipeline, released processed-data objects, interactive web apps + Zenodo archive). `configs/`: 0 to
several files, each with anywhere from 3 (woj25's two-assay config) to a dozen+ per-parameter blocks
(aki26's pipeline_parameters.md has ~20). `execution/`: 0 to many files; when a repo is provided as
input, every real runnable file of substance (≥~30 lines or a named module/entrypoint) must be
captured, not merely pointed at.

### Availability notes
This is the artifact whose absence is most tightly conditioned on paper genre, and getting it wrong
in either direction is a checkable defect:
- **Correct absence**: a pure meta-analysis/systematic review with no released code (che26) legitimately
  has `environment.md` + `artifacts.md` and nothing else — Seal Level 1 explicitly forbids fabricating
  a `.py` stub here, since it would just duplicate `study_design.md`.
- **Correct near-absence despite real code existing**: huu25's underlying work has a full ~15GB GitHub
  repo with real R/Python/Shell code, yet `src/execution/` is legitimately absent in this ARA because
  the compiler explicitly did not clone the repo (stated in `artifacts.md`) — this is flagged
  in-artifact as a scope decision, not silently hidden. A tournament metric evaluating "does src/
  capture real code" must distinguish this honestly-disclosed non-capture from a silent coverage
  failure where a provided repo's code was dropped without comment.
- **Failure mode to penalize**: a provided repo's real source files reduced to a pointer in
  `artifacts.md` instead of being copied into `src/execution/` — explicitly called out as a FAIL
  condition in the validation checklist (§5, Implementation layer).
- **Failure mode to penalize (other direction)**: a `.py`/pseudo-code stub manufactured from a
  prose-only method description, or code with invented API names/constants/function bodies not
  traceable to any real source — also an explicit FAIL condition.
- **Grounding tag missing or wrong** on any `src/execution/*.py` file — every such file must open with
  `# Grounding: transcribed` or `# Grounding: reconstructed`; absence of this line is itself a defect.
- Abstract-only sources: `environment.md` is reduced to whatever the abstract states about
  methodology (often nothing computational at all) — `artifacts.md`/`configs/`/`execution/` are all
  absent, correctly, since nothing concrete is knowable.

---

## indicators
- re-use
- FAIR
- reproducibility
- added value / novelty / field expansion
- env <> evidence / method / constraints(claim) match

## 11. `data/dataset.md` (+ `data/preprocessing.md`)

### Artifact + path
`data/dataset.md`, optionally `data/preprocessing.md`. Present only for data-driven work. Examples:
`research/ara-library/che26-diagnostic-performance-of-plasma-p-tau217/data/dataset.md` (secondary
summary-data reuse case), `research/ara-library/huu25-apoe-e4-alzheimer-s-risk-converges/data/dataset.md`
(primary-data-generation case).

### Purpose
Provenance, access, and structural description of the dataset(s) the work is built on — whether the
paper *generated* new data (with accessions, consent/IRB, and technical specs) or merely *reused*
existing summary statistics from prior studies. This is what tells a downstream agent whether the
work's numbers are independently reproducible from public data or gated behind consortium access.

### Structure
Free-form markdown-prose organized under `##` headings; no fixed field schema, but recurring
sub-blocks across both genres:

| Section | Type | Notes |
|---|---|---|
| Intro paragraph | markdown-prose | states data type (primary-generated vs. secondary-reused), total N, and whether primary patient-level data were released |
| `## {Accession} — {short description}` (one per generated dataset) | markdown-prose, structured sub-bullets | present only for primary-data-generation papers |
| `**Provenance**` (within an accession block) | string | how/what was generated, instrument, depth |
| `**Source / access**` (within an accession block) | string, states **access tier explicitly** | `"GEO record/metadata and processed data are **open**. **Raw sequencing reads are controlled access via dbGaP**"` |
| `**Size / content**` (within an accession block) | string, exact dims | `"SpatialExperiment spe_ERC_annotated = 30,494 genes × 122,202 in-tissue spots"` |
| `**Licensing / consent**` (within an accession block) | string | IRB/consent framework |
| `**Key variables**` (within an accession block) | list/string | covariates available |
| `## Provenance and access` (secondary-reuse genre) | markdown-prose | states release status verbatim from the paper's Data Availability Statement |
| `## Included cohorts` (secondary-reuse genre) | markdown-table | cohort-level provenance table (see example) |
| `## External datasets used (not generated here)` | markdown-prose bullets | cross-referenced datasets used only for validation/enrichment, not the study's own data |
| `## Consent / ethics` | markdown-prose | IRB numbers, or "not applicable at the review level" for secondary-data work |
| `## Preprocessing` | markdown-prose, or pointer to `data/preprocessing.md` / `logic/solution/method.md` | QC/cleaning/normalization steps |

### A full realistic example

Primary-data-generation genre (huu25):
```markdown
## GSE307990 — Visium spatially-resolved transcriptomics (SRT), human ERC
- **Provenance**: Generated in this study; 10x Genomics Visium Spatial Gene Expression, one section
  per donor (31 samples), NovaSeq 6000, min 60,000 reads/spot; SpaceRanger v2.1.0 (GRCh38, 2020-A).
- **Source / access**: NCBI GEO accession GSE307990 — https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE307990 .
  GEO record/metadata and processed data are **open**. **Raw sequencing reads are controlled access
  via dbGaP** (postmortem human genomic data).
- **Size / content**: Processed SpatialExperiment `spe_ERC_annotated` = 30,494 genes × 122,202
  in-tissue spots (post-QC), 9 annotated spatial domains.
- **Licensing / consent**: Postmortem human tissue under IRB #12-24 (Maryland DoH), WCG #20111080
  (Santa Clara ME), NIH #90-M-0142 (NIMH IRP), informed consent from legal next-of-kin.
- **Key variables**: APOE carrier (E2+/E4+), ancestry (AA/EA), sex, age, Braak (18 donors), CERAD,
  pTau status (t+/t−), spatial domain, Visium slide.
```

Secondary-reuse genre (che26):
```markdown
## Provenance and access
- **Type**: secondary summary data extracted from published diagnostic-accuracy studies.
- **Release status**: no accessioned dataset; "included in the article/Supplementary material,
  further inquiries can be directed to the corresponding author." (Data Availability statement, verbatim).
- **Registration**: PROSPERO CRD420261327845 (open).

## Included cohorts (from Table 1; access controlled/by-request via each consortium)
| Cohort | Source study | N | Disease stage | Reference standard | Platform/manufacturer |
|--------|--------------|---|---------------|--------------------|-----------------------|
| BioFINDER-1 | Janelidze et al. (2023) | 135 | MCI (prodromal AD) | CSF Abeta42/40 | IP-MS and Simoa |
| TRIAD | Benedet et al. (2026) | 100 | AD continuum | Amyloid-PET | Automated IA (serum focus) |

## Consent / ethics
- Not applicable at the review level (secondary summary data). Individual cohorts carry their own
  IRB approvals and consent (not restated in this article).
```

### Cardinality / variability
0 or 1 `data/` directory per ARA (che26 and huu25 both have exactly one `data/dataset.md`; a pure
theory or code-tool paper would have none). Number of accession/cohort blocks scales with how many
distinct datasets the work touches — huu25 has 2 generated accessions + 4 external reference datasets;
che26 has 12 reused cohorts (from Table 1) + 3 additionally-named screened cohorts. `preprocessing.md`
as a *separate* file is less common than folding preprocessing into `logic/solution/method.md` (as
huu25 does) — both are valid; which one the compiler picks tracks how much QC/preprocessing detail
exists relative to the rest of the method.

### Availability notes
`data/` is the most genre-conditioned "as warranted" directory in the schema:
- **Correctly absent**: pure theory papers, tool/spec releases with no dataset, and code-only papers
  legitimately have no `data/` directory at all — this must not be penalized as a gap.
- **Access-tier honesty is the key scoring axis** for data-driven work: a well-compiled
  `dataset.md` states explicitly which parts are open (metadata, processed objects) vs.
  controlled-access (raw reads via dbGaP, cohort data via consortium request) — collapsing this
  distinction into a blanket "available" or "not available" is a real defect a metric can check by
  looking for the co-occurrence of both an access claim and its qualifier.
- **Secondary-reuse papers cannot have a `Preprocessing` section describing raw-data QC** (there is no
  raw data) — their `dataset.md` correctly ends at cohort-level provenance; expecting cell/read-level
  QC parameters here would be a genre-mismatched expectation.
- **Internal count mismatches**: che26's own `dataset.md` explicitly flags that its 12 tabulated
  cohorts don't sum to the paper's stated "18 studies / 24 independent datasets" — a well-compiled
  ARA surfaces this discrepancy rather than silently picking one number, and a metric can check
  whether such stated-vs-tabulated mismatches are flagged anywhere in the ARA (here, cross-referenced
  in `constraints.md` too) rather than left uncommented.
- Abstract-only sources: `data/dataset.md`, if generated at all, will state only the sample size/
  population mentioned in the abstract (e.g. "N=4,736 participants") with no accession, no access
  tier, no cohort table — a clear floor case distinguishable from a real provenance record.

---

## Final enumerated artifact list (drives the tournament)

| # | Artifact | Path pattern | Mandatory core? |
|---|---|---|---|
| 1 | Root manifest | `PAPER.md` | Yes |
| 2 | Claims | `logic/claims.md` | Yes |
| 3 | Concepts | `logic/concepts.md` | Yes |
| 4 | Problem statement | `logic/problem.md` | Yes |
| 5 | Experiments (analysis plans) | `logic/experiments.md` | Yes |
| 6 | Related work (typed dependency graph) | `logic/related_work.md` | Yes |
| 7 | Solution / method layer | `logic/solution/constraints.md` + warranted method files (`study_design.md`, `method.md`, `heuristics.md`, `architecture.md`, `algorithm.md`, ...) | `constraints.md` yes; siblings as warranted |
| 8 | Exploration tree (research DAG) | `trace/exploration_tree.yaml` | Yes |
| 9 | Evidence (index + tables + figures) | `evidence/README.md`, `evidence/tables/*.md`, `evidence/figures/*.md` (+ `.png` siblings; `evidence/proofs/*.md` as warranted) | Yes |
| 10 | Implementation / reproduction layer | `src/environment.md` (+ `src/artifacts.md`, `src/configs/*.md`, `src/execution/*` as warranted) | `environment.md` yes; rest as warranted |
| 11 | Dataset descriptors | `data/dataset.md` (+ `data/preprocessing.md`) | As warranted (data-driven work only) |

11 top-level artifact sections, above the "Final enumerated artifact list" summary table.

## indicators
- re-use
- FAIR
- reproducibility
- added value / novelty / field expansion
- data <> evidence / method / constraints(claim) match
- data homogeneity & standard adherence
- referencing existing controlled vocabs or latent spaces

