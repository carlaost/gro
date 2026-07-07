# Evidence pointers

This ARA is a compiled record of an experiment already run in-repo. It does not duplicate the underlying data; it points to it.

## Primary source paper

- `research/metrics/v4-gro/EXPERIMENT_PAPER.md` — the source document this ARA compiles.

## Run artifacts (this experiment)

- `research/metrics/v4-gro/results.json` — machine-readable output: `aras_processed` (12 ARA ids), `aras_failed` ([]), per-metric `metric_definitions` (each with `computable_on_prose: false` and a `prose_reason`), per-ARA metric values, and corpus aggregates. This is the source of every numeric value in `logic/claims.md`.
- `research/metrics/v4-gro/results.md` — human-readable rendering of the same run: per-ARA table, corpus-aggregate table, parse/data-quality notes by ARA (incl. the `zho25` negative-genre-count note and the `ard25` missing-experiment-ledger note), and the `computable_on_prose` baseline-contrast section.
- `research/metrics/v4-gro/gro_metrics.py` — the metric-computation code implementing the eight Tier-A joins (`quantity_reconciliation_rate`, `claim_typing_coverage`, `entailment_precondition_rate`, `reference_resolvability_rate`, `entity_anchoring_rate`, `genre_silent_omissions`, `overclaim_flags`, `broken_ref_integrity`), including the Unicode-minus (U+2212) normalization fix referenced in C10.
- `research/metrics/v4-gro/seal/*.json` — one JSON record per ARA (12 files), likely a validation/seal pass over each ARA's `gro/` sidecars; consult directly for per-ARA sidecar-validation detail beyond what `results.json` aggregates.

## The 12 GRO-extended ARAs (sidecars under test)

Each ARA's five deterministic-tier sidecars live under its own `gro/` directory in the ARA library, e.g.:
- `research/ara-library/ard25-response-of-spatially-defined-microglia-states/gro/{quantities,claims_typed,refs,entities,genre}.yaml` (the ARA cited in C07 for `broken_ref_integrity`)
- `research/ara-library/cum26-alzheimer-s-disease-drug-development-pipeline/gro/*.yaml` (cited in C05, C08)
- `research/ara-library/xu25-epidemiological-and-sociodemographic-transitions-in-the/gro/*.yaml` (cited in C08, C10)
- `research/ara-library/zho25-microglia-networks-within-the-tapestry-of/gro/*.yaml` (cited in C02, C05, C08, C09)
- and the remaining 8: `che26-diagnostic-performance-of-plasma-p-tau217`, `val25-blood-biomarkers-of-alzheimer-s-disease`, `han26-tau-pathological-activity-in-plasma-before`, `zim25-donanemab-in-early-symptomatic-alzheimer-s`, `jes26-efficacy-and-safety-of-donanemab-in` (cited in C10), `tit26-automated-high-throughput-quantification-of-plasma`, `gau25-single-nucleus-and-spatial-transcriptomic-profiling`, `aki26-molecular-signatures-of-resilience-to-alzheimer` (cited in C02) — all under `research/ara-library/<id>/gro/`.

## Adjacent artifacts (later work, not the basis of this ARA's claims)

The `v4-gro/` directory also contains later, separate analyses that build on this run but are out of scope here — do not cite them for claims in this ARA:
- `research/metrics/v4-gro/benchmark.json` / `benchmark.py` — a separate benchmarking pass (unrelated experiment; check its own paper before citing).
- `research/metrics/v4-gro/external/`, `external_validation.json`, `EXTERNAL_VALIDATION_PAPER.md` — the anchored/Tier-B external-validation follow-up, explicitly **not run** as part of this deterministic-tier experiment (see C11 / §5 of the source paper).
- `research/metrics/v4-gro/COMPARISON_PAPER.md`, `compare/`, `figures/` — a later comparison paper, not the source of this ARA.

## Spec and parent-program references (context, not this ARA's own evidence)

- `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md` — the GRO spec defining Tier A/B/C and the eight Tier-A metric definitions (§1, §4, §7 cited in the source paper's limitations).
- `research/metrics/v3/tournament/TOURNAMENT_SUMMARY.md` §1 — the parent negative result quoted in C11 ("a well-compiled record of bad science and a well-compiled record of good science are... indistinguishable to every metric").
