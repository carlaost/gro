# GRO Deterministic-Tier Metrics — Results

Pure structural joins over `gro/{quantities,claims_typed,refs,entities,genre}.yaml` for 12 GRO-extended ARAs. No LLM calls, no network calls. Spec: `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md #4`.

ARAs processed: 12/12. Failures: 0.

## Per-ARA results

| ARA | quant_reconcil | claim_typing_cov | entail_precond | ref_resolvability | entity_anchoring | genre_silent_omis | overclaim_flags | broken_ref_integrity |
|---|---|---|---|---|---|---|---|---|
| che26-diagnostic-performance-of-plasma-p-tau217 | 1.000 | 1.000 | 1.000 | 0.944 | 0.000 | 0 | 0 | 0 |
| val25-blood-biomarkers-of-alzheimer-s-disease | 1.000 | 1.000 | 0.692 | 0.000 | 0.000 | 1 | 0 | 0 |
| han26-tau-pathological-activity-in-plasma-before | 1.000 | 1.000 | 1.000 | 0.190 | 0.000 | 0 | 0 | 0 |
| zim25-donanemab-in-early-symptomatic-alzheimer-s | 1.000 | 1.000 | 1.000 | 0.957 | 0.000 | 0 | 0 | 0 |
| jes26-efficacy-and-safety-of-donanemab-in | 1.000 | 1.000 | 1.000 | 0.895 | 0.000 | 0 | 0 | 0 |
| tit26-automated-high-throughput-quantification-of-plasma | 1.000 | 1.000 | 1.000 | 0.132 | 0.000 | 0 | 0 | 0 |
| gau25-single-nucleus-and-spatial-transcriptomic-profiling | 1.000 | 1.000 | 0.571 | 0.100 | 0.000 | 0 | 0 | 0 |
| zho25-microglia-networks-within-the-tapestry-of | n/a | 1.000 | 0.500 | 0.000 | 0.000 | -1 | 3 | 0 |
| aki26-molecular-signatures-of-resilience-to-alzheimer | n/a | 1.000 | 0.400 | 0.136 | 0.000 | 0 | 0 | 0 |
| cum26-alzheimer-s-disease-drug-development-pipeline | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0 | 9 | 0 |
| xu25-epidemiological-and-sociodemographic-transitions-in-the | 1.000 | 1.000 | 0.923 | 0.137 | 0.000 | 0 | 11 | 0 |
| ard25-response-of-spatially-defined-microglia-states | 1.000 | 1.000 | 0.769 | 0.000 | 0.000 | 4 | 0 | 16 |

## Corpus aggregates

| Metric | Mean | Min | Max | Notes |
|---|---|---|---|---|
| quantity_reconciliation_rate | 1.000 | 1.000 | 1.000 | 2 ARA(s) undefined (null) |
| claim_typing_coverage | 1.000 | 1.000 | 1.000 |  |
| entailment_precondition_rate | 0.821 | 0.400 | 1.000 |  |
| reference_resolvability_rate | 0.374 | 0.000 | 1.000 |  |
| entity_anchoring_rate | 0.000 | 0.000 | 0.000 |  |
| genre_silent_omissions | 0.333 | -1 | 4 | total=4, 3/12 ARAs nonzero |
| overclaim_flags | 1.917 | 0 | 11 | total=23, 3/12 ARAs nonzero |
| broken_ref_integrity | 1.333 | 0 | 16 | total=16, 1/12 ARAs nonzero |

## Parse / data-quality notes by ARA

- **zho25-microglia-networks-within-the-tapestry-of**: no quantities referenced by >=2 claims; reconciliation rate undefined (null); genre.yaml present_slots contains slot(s) not in expected_slots: ['experiments'] -- literal count formula can go negative
- **aki26-molecular-signatures-of-resilience-to-alzheimer**: no quantities referenced by >=2 claims; reconciliation rate undefined (null)
- **ard25-response-of-spatially-defined-microglia-states**: no logic/experiments.md found -- all proof_refs treated as unresolved

## computable_on_prose (baseline contrast)

Every metric above is `computable_on_prose: false` — none of them is answerable by an LLM reading the original PAPER.md prose without first re-extracting the exact typed fields the gro/ sidecars already carry:

- **quantity_reconciliation_rate**: Prose has no typed Q## ledger with a canonical value + claim_refs join; an LLM would first have to re-extract every numeral into a record before any reconciliation check exists.
- **claim_typing_coverage**: Prose claims carry no claim_type or logical_form field; assigning either is LLM inference/annotation, not extraction.
- **entailment_precondition_rate**: Prose has no explicit quantity_ref/proof_ref linkage between a claim sentence and its supporting experiment; that link is an LLM's inference, not a lookup.
- **reference_resolvability_rate**: Prose citations are free-text strings; resolvability requires an LLM/human to look each one up against a resolver, it is not a lookup over an existing field.
- **entity_anchoring_rate**: Prose entity mentions have no xref field; assigning ontology ids requires LLM-driven entity linking against an external KB.
- **genre_silent_omissions**: Prose has no expected_slots/present_slots/absent_declared fields; genre expectations must be inferred by an LLM reading the whole paper against a genre model.
- **overclaim_flags**: Prose doesn't carry population_scope/population_n as typed fields; detecting a scope/n mismatch requires LLM comprehension of the methods section.
- **broken_ref_integrity**: Prose has no explicit ref-id graph; 'broken reference' isn't a well-formed question until an LLM has typed the refs into ids in the first place.

## Interpretation

Typing the record does make the previously-blocked joins mechanically computable: all eight metrics run as pure lookups with zero LLM/network calls, and `broken_ref_integrity` in particular is a real trust signal a prose corpus cannot produce at all (it caught `ard25`, whose `claims.md` cites nine `E01`-`E09` proof references with no `logic/experiments.md` — or any experiment ledger — anywhere in the ARA to resolve them against, so every `proof_ref` on every claim in that ARA is structurally broken). `entity_anchoring_rate` is exactly 0.0 on all 12 ARAs: every one of 176 entities across the corpus carries `xref: not_specified`, so the entity spine is present as a schema but not yet populated as data -- a typed field that's uniformly empty is a different failure mode than a metric that can't be computed, and this run makes that distinction visible for the first time. `quantity_reconciliation_rate` is high wherever it's defined, but it is a weaker check than its name suggests: because each Q## is authored exactly once with a single canonical `value`, the check here reduces to whether that one value is rounding-consistent with the numeral in its own authoring quote, not an independent cross-mention reconciliation across prose/tables/abstract (that would require grounding against PAPER.md text, which is a Tier-B/A-R check, not Tier-A). `overclaim_flags` surfaces real signal: `cum26` and `xu25` (population registries/epidemiological estimates) post the corpus's highest overclaim counts because most of their claims are typed `population_estimate` with `population_n: not_specified` -- exactly the quantifier-inflation pattern the spec's over-claim rule is designed to catch.

