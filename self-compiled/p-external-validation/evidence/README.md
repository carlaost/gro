# Evidence pointers

This ARA compiles `research/metrics/v4-gro/EXTERNAL_VALIDATION_PAPER.md`. It does not duplicate
the underlying data files — it points to them. All numbers in `logic/claims.md` are grounded in
the paper's own prose (quoted verbatim in each claim's `Sources` block); the artifacts below are
the raw evidence the paper's prose summarizes, kept in place at their original repo location.

## Primary synthesis

- `research/metrics/v4-gro/external_validation.json` — the synthesis file for this experiment:
  `corpus` (the six ARA slugs and their role — trial vs observational/NMA), `reference_resolvability`
  (per-ARA sampled/resolved/observed/declared rates + pooled/mean stats), `novelty_distribution`
  (per-claim verdict counts and per-ARA breakdown), `registry_findings` + `registry_summary` (the
  two donanemab papers' concordance-gap classification), `retractions` (per-paper retraction
  counts), `answers` (the paper's own computability/differentiation/hard-limit summary), and
  `caveats` (the limitations list §5 of the paper draws from).

## Per-ARA raw evidence

- `research/metrics/v4-gro/external/*.json` — one file per ARA (`zim25`, `jes26`, `che26`, `val25`,
  `han26`, `tit26`), each holding that ARA's `reference_resolution`, `novelty`, `registry` /
  `registry_note`, `retractions`, and free-text `notes` — the per-paper detail that
  `external_validation.json` aggregates.

## Prior (deterministic-tier) experiment referenced by this paper

- `research/metrics/v4-gro/results.json` — Tier-A (deterministic) metric results over the same/
  related corpus; `spec_reference`, `tier`, `aras_processed`/`aras_failed`, `metric_definitions`,
  `per_ara` + `per_ara_diagnostics`, `corpus_aggregates`. This is the artifact the paper contrasts
  itself against in §1 ("its `reference_resolvability_rate` there meant only whether an
  `external_id` string was *printed and typed as resolvable*; no DOI was ever fetched").
- `research/metrics/v4-gro/results.md` — narrative companion to `results.json`.
- `research/metrics/v4-gro/EXPERIMENT_PAPER.md` — the full write-up of the deterministic-tier
  experiment this paper positions itself against.

## Independently-run rubric scoring (not cited numerically in this paper, adjacent artifact)

- `research/metrics/v4-gro/seal/*.json` — one file per ARA (12 ARAs, a superset of the six used
  here), each with `dimensions`, `overall_score`, `recommendation`, `findings` — a Level-2-style
  epistemic scoring pass. Not referenced by number in `EXTERNAL_VALIDATION_PAPER.md`; kept here as
  adjacent evidence infrastructure for the same corpus.
- `research/metrics/v4-gro/benchmark.json` and `research/metrics/v4-gro/benchmark.py` — benchmark
  harness (`per_ara`, `benchmark`, `note`) for the metrics pipeline; adjacent infrastructure, not
  cited numerically in the external-validation paper.

## Spec and framing

- `research/metrics/v3/tournament/IDEAL_FORMAT_SPEC.md` §1, §7 — the GRO tier framing (Tier A
  deterministic / Tier B anchored / Tier C judged) and the independence-limitation language
  ("pipeline-independence, necessary not sufficient... except L3's non-LLM matcher") that C08
  draws on.

## Note on scope

The paper is explicit that "Per-ARA evidence JSON is under `external/`; the synthesis is
`external_validation.json`. Every id and outcome cited below came from a live MCP response — none
were invented" (§2). This ARA treats that same evidence as authoritative and does not re-derive or
re-fetch it; `logic/claims.md` cites the paper's prose, which in turn is grounded in these files.
