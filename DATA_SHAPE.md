# GRO data shape — the canonical, current reference

*The single source of truth for a GRO record's structure: every emitted sidecar, its rigor tier, id space, provenance, fields, and a real example value (OpenAPI-style). Normative target: [`SPEC.md`](SPEC.md). What is emitted vs still specified-only: [`SPEC.md §7a`](SPEC.md). Live instances: `experiment/**/gro/` and the parent corpus's `ara-library/*/gro/`.*

---

## What a GRO record is

A GRO is a **directory**. It keeps human-readable prose (`PAPER.md` + `logic/` drill-downs) but **every load-bearing fact also exists as a typed record**, addressed by a stable id, that the prose binds back to. Facts are sorted into **three rigor tiers** kept physically separate, so a self-certified number is never dressed up as an externally-checked one.

| Tier | meaning | how far it can be trusted |
|---|---|---|
| **A — deterministic** | typed quantities, claim logical form, entities, genre | exact, reproducible — a structural join over authored data |
| **B — anchored** | references, external quantities, deltas, SOTA neighborhood, temporal | reliable *given a pinned resolver*; failures are first-class honest states, not blanks |
| **C — reproducible-judged** | contribution typing, novelty/significance | a calibrated judge, never deterministic; the format only pins its inputs |

**Provenance tags** (used per field below — conflating them is the mistake the whole program warns against):
- **[PAPER→LLM]** — the compiler read *this paper's text* and made a typed judgment. Not externally verified; blind to what happened after publication.
- **[PRIOR-ART]** — resolved against *earlier* literature (references + an OpenAlex search for pre-publication near-neighbors).
- **[FOLLOW-ON]** — from *later* papers citing this one (the citation graph). **Structurally empty on recent papers.**

---

## Status: emitted vs specified (read before trusting the tree)

The compiler **emits the 10 sidecars below** (verified 66/66 across the reference corpus, `temporal` 62/66): a **Tier-A record layer + the L8 novelty tier + prose + exploration trace**. Specified in `SPEC.md` but **not yet materialized**: the L4 cross-object graph (`nodes`/`edges` — the inter-paper "particle layer"), the derived hash-gated Tier-A objects (`claim_graph` AST, `symbol_table`), L6 `citation_mentions`/`support_edges`, L7 registry-join ledgers, and the P1–P4 report objects. **Manifest gap:** `PAPER.md`'s layer index currently lists only the inherited prose layers; the `gro/` sidecar bundle is emitted beside the record but not yet declared in the manifest (no `bind_mode`).

---

## The 10 emitted sidecars (`gro/`)

### `quantities.yaml` — `Q##` · Tier A · [PAPER→LLM]
Every load-bearing number authored *in this paper*, typed once and addressed by id; prose and all other layers cite the `Q##`, never re-type the value.

| field | type | meaning |
|---|---|---|
| `id` | `Q##` | canonical id |
| `value` | number | the number |
| `unit` | string | unit / measure (`log2FC`, `FDR`, `percent`, …) |
| `comparator` | enum | `none \| vs_baseline \| vs_arm` |
| `ci_low` / `ci_high` | number \| `not_specified` | CI bounds if reported |
| `role` | enum | `result \| input \| parameter` |
| `source_ref` | string | location in source (`paper.pdf p6`) |
| `quote` | string | verbatim sentence the value came from (grounding) |
| `claim_refs` | `[C##]` | claims this number supports |

```yaml
quantities:
  - id: Q01
    value: 1.75
    unit: log2FC
    comparator: none
    role: result
    source_ref: "paper.pdf p6"
    quote: "increase in the proportion of Ex5 neurons in high vs low pathology cases in BA9 (log2-fold change = 1.75)"
    claim_refs: [C01]
```

### `external_quantities.yaml` — `XQ##` · Tier B · [PRIOR-ART]
Off-paper prior-work numbers used as comparison baselines. A **separate id space** from `Q##` (they carry someone else's `fetch_timestamp` and are exempt from this paper's numeral-coverage audit).

| field | type | meaning |
|---|---|---|
| `id` | `XQ##` | id |
| `value` | number | prior-work number |
| `unit` | string | unit |
| `description` | string | what it is + which prior work |
| `source_anchor.external_id` | DOI/id | resolvable source |
| `source_anchor.fetch_timestamp` | datetime | when fetched |
| `baseline_verification` | enum | `source_verified \| self_reported \| unverified` |

```yaml
external_quantities:
  - id: XQ02
    value: 3.03
    unit: percent
    description: "Ex5 proportion of excitatory cells in the Green et al. 2024 prefrontal reference"
    source_anchor: { external_id: "10.1038/s41586-024-07871-6", fetch_timestamp: 2026-07-07T00:00:00Z }
    baseline_verification: source_verified
```

### `claims_typed.yaml` — `C##` · Tier A · [PAPER→LLM]
Each load-bearing claim, typed and given a first-order-logic line so contradictions/scope are machine-checkable; binds to its quantities, entities, evidence.

| field | type | meaning |
|---|---|---|
| `id` | `C##` | id |
| `claim_type` | enum | `comparison \| existence \| causal \| association \| …` |
| `polarity` | enum | `positive \| negative \| null` |
| `logical_form` | string | FOL rendering |
| `population_n` | int \| `not_specified` | sample size if stated |
| `population_scope` | enum | `cohort \| subgroup \| invitro \| model \| …` |
| `quantity_refs` | `[Q##]` | numbers it rests on |
| `concept_refs` | `[EN-*]` | entities involved |
| `proof_refs` | `[E##]` | experiments / evidence |
| `depends_on` | `[C##]` | claim dependencies |

```yaml
claims:
  - id: C01
    claim_type: comparison
    polarity: positive
    logical_form: "increases_with(Ex5_proportion, pathology, BA9) AND significant(GLMM_FDR=0.008, BA9)"
    population_scope: cohort
    quantity_refs: [Q01, Q02, Q03]
    concept_refs: [EN-population-ex5, EN-concept-resilience_neuronal]
    proof_refs: [E03]
    depends_on: [C02, C10]
```

### `entities.yaml` — `EN-*` · Tier A · [PAPER→LLM]
One record per entity mechanically referenced by another layer (genes, cell types, methods, concepts), with a stable id and optional ontology xref for cross-record interop.

| field | type | meaning |
|---|---|---|
| `id` | `EN-<kind>-<slug>` | stable id |
| `term` | string | human-readable name |
| `kind` | enum | `concept \| measure \| method \| dataset \| organism \| …` |
| `xref` | ontology id \| `not_specified` | external anchor if resolved |

```yaml
entities:
  - id: EN-population-ex5
    term: "Ex5 (resilient L4 IT excitatory subtype)"
    kind: concept
    xref: not_specified
```

### `genre.yaml` — · Tier A · [PAPER→LLM]
Declared record type + which content slots that type expects; **absence of an expected slot becomes a declared, checkable fact** rather than a silent omission.

| field | type | meaning |
|---|---|---|
| `paper_type` | string | controlled genre label |
| `expected_slots` | `[string]` | slots this genre should carry |
| `present_slots` | `[string]` | slots actually present |
| `absent_declared` | `[string]` | expected-but-absent, declared honestly |

```yaml
paper_type: molecular_neuropathology_single_cell_omics
expected_slots: [claims, experiments, evidence, dataset]
present_slots:  [claims, experiments, evidence, dataset]
absent_declared: []
```

### `refs.yaml` — `R##` · Tier B · [PRIOR-ART]
One canonical record per cited work, resolved to an external id; unresolvable refs are flagged, not hidden.

| field | type | meaning |
|---|---|---|
| `id` | `R##` | id |
| `raw` | string | reference as printed |
| `external_id` | DOI/id | resolved canonical id |
| `resolvable` | bool | resolved to a real external record? |

```yaml
refs:
  - id: R03
    raw: "Mathys et al., 2023 — single-cell atlas of cognition/resilience to AD [ref 8]"
    external_id: 10.1016/j.cell.2023.08.039
    resolvable: true
```

### `contributions.yaml` — `CT##` · Tier C → L8 · [PAPER→LLM]  ⟵ *the breakthrough-metric input*
What the paper claims to contribute, **double-typed**: how the authors frame it vs. the compiler's own call from a closed novelty taxonomy, with a rationale. An **anti-puffery lock** voids any contribution not realized in a real claim. **This is the only field the breakthrough metric reads** (see Learnings below).

| field | type | meaning |
|---|---|---|
| `id` | `CT##` | id |
| `author_framed_type` | string | the authors' framing |
| `compiler_assessed_type.primary` | enum | `new_paradigm \| new_method \| new_finding \| refutation \| synthesis \| incremental_improvement \| replication` |
| `compiler_assessed_type.confidence` | 0–1 | compiler confidence |
| `typing_rationale` | string | why this type |
| `typing_divergence` | enum | `none \| adjacent \| conflicting` (author vs compiler) |
| `adjudication` | enum | `not_triggered \| <blind-second-rater outcome>` |
| `realized_in` | `[C##]` | claims that realize it (empty ⇒ voided) |

```yaml
contributions:
  - id: CT02
    author_framed_type: key_resilience_factor
    compiler_assessed_type: { primary: new_finding, confidence: 0.75 }
    typing_rationale: "Nominates KCNIP4 as a molecular resilience factor upregulated in resilient Ex5 L4 neurons; new gene-level finding grounded in prior KChIP4 biology."
    typing_divergence: none
    adjudication: not_triggered
    realized_in: [C04, C05, C06, C09]
```

### `delta_ledger.yaml` — `D##` · Tier B · [PAPER→LLM, baseline PRIOR-ART]
Each quantified comparison of this paper's number vs an off-paper baseline. `claimed_value` is a `Q##`; `baseline_value` an `XQ##`; deltas are **compiler-computed, never author-entered**. Honesty states are first-class.

| field | type | meaning |
|---|---|---|
| `id` | `D##` | id |
| `delta_status` | enum | `quantified \| qualitative_only \| claimed_unresolved \| not_claimed` |
| `claimed_value` | `Q##` | this paper's number |
| `baseline_value` | `XQ##` \| `not_specified` | prior-work number |
| `absolute_delta` / `relative_delta` | number \| `not_specified` | compiler-computed |
| `baseline_verification` | enum | `source_verified \| self_reported` |
| `note` | string | what the comparison is + why the status |

```yaml
deltas:
  - id: D02
    delta_status: quantified
    claimed_value: Q16          # 34.42% (this paper, BA17)
    baseline_value: XQ04        # 0.33% (SEA-AD DLPFC atlas)
    absolute_delta: 34.09
    relative_delta: 103.303
    baseline_verification: source_verified
    note: "Ex5 spatial enrichment vs prefrontal atlas — establishes BA17-specialization of the resilient L4 IT subtype."
```

### `sota_anchor.yaml` — · Tier B · [PRIOR-ART]
A resolver-produced neighborhood of the closest *preceding* works, each with an `overlap` ∈ [0,1] (fraction of this paper's contribution the prior work already covers), frozen at an externally-timestamped `precedence_date`.

**Two metrics from one measurement:** **breakthrough = `1 − overlap`** (distance from prior art); **convergence = `+ overlap`** (consolidation). *Empirical status: both unvalidated — see Learnings; use a `overlap` measure validated to track prior-art distance before trusting either.*

| field | type | meaning |
|---|---|---|
| `precedence_date` / `cutoff_date` | date | frozen prior-art horizon |
| `provenance` | enum | `openalex_resolved \| reference_resolved \| compiler_estimated` |
| `neighborhood[].ref` | `R##` | a prior work |
| `neighborhood[].overlap` | 0–1 | fraction of this paper's contribution it covers |
| `neighborhood[].contemporaneous_uncited` | bool | near-neighbor the paper failed to cite |
| `overlap_jaccard_second_resolver` | 0–1 | independent second-pass corroboration |
| `retrospective_resolution` | object | later-supersession signal + `gap_days` |

```yaml
precedence_date: 2026-01-01
provenance: openalex_resolved
neighborhood:
  - { ref: R03, overlap: 0.35, contemporaneous_uncited: false }   # Mathys 2023 — framework-level overlap only
  - { ref: R05, overlap: 0.30, contemporaneous_uncited: false }   # same lab, vulnerability direction
overlap_jaccard_second_resolver: 0.22
```

### `temporal.yaml` — · Tier B · [PRIOR-ART/FOLLOW-ON]
Publication + fetch timestamps that pin every anchored/forward-looking signal to a time axis (required for precedence and any longitudinal metric).

| field | type | meaning |
|---|---|---|
| `pub_date` | date | publication date |
| `doi` | string | canonical id |
| `fetch_timestamp` | datetime | when external anchoring ran |
| `note` | string | provenance note |

```yaml
pub_date: 2026-01-01
doi: "10.1038/s41467-026-68920-4"
fetch_timestamp: 2026-07-07T00:00:00Z
note: "pub_date seeds the corpus temporal spine"
```

---

## Learnings that constrain how this shape is used

From the v5 breakthrough paper and the v6 longitudinal validation ([`experiment/breakthrough/`](experiment/breakthrough/)):

- **Only `contributions.yaml` typing carries any breakthrough signal** at publication time; the `[PRIOR-ART]` `sota_anchor` overlap, the `delta_ledger`, and `genre` added **no transferable signal**.
- That signal is **shared-model bias, largely**: contribution-depth agreed with a same-model LLM panel at ρ≈0.58 but an independent model at only ≈0.34, and the two models' own metrics agree only ρ≈0.17 — so there is **no stable model-independent "contribution depth."**
- Against **real field outcomes** (15–20-yr citation disruption, no LLM), neither the metric nor a **direct LLM judge** predicts breakthrough (ρ≈0). Both — metric and judge — instead predict **citations/attention** (ρ≈0.5). **LLMs have learned the *attention* axis, not the *breakthrough* axis.**
- **The `[FOLLOW-ON]` fields are structurally empty** on recent records and are where a *real* breakthrough/convergence signal would have to come from — which is why the next design step (SPEC successor) proposes building metrics **from the field-response graph** (replication, reuse, stance edges) rather than from a single reading of the paper. Candidate new shapes under evaluation: **reference-set dispersion**, **atypical-combination score**, **novel-entity introduction rate**, **stance-to-prior-art edges**. A shape earns a place in `SPEC.md` only if it lifts *held-out field prediction*.

**Bottom line for anyone building on this shape today:** the deterministic/anchored layers (`quantities`, `claims_typed`, `entities`, `refs`, `genre`) are the trustworthy, computable core (record *fidelity*). The L8 novelty tier is adversarially-hardened but **empirically unvalidated as a quality/breakthrough signal** — treat `contributions`-derived scores as "LLM-perceived contribution depth / likely attention," not "breakthrough."
