# experiment/ — deterministic-tier extension experiment

The first empirical test of the GRO idea: take existing compiled ARAs, generate GRO **deterministic-tier extensions** (typed sidecars), and compute the deterministic ideal metrics over the extended shape. The question is narrow and precise: *does typing the record convert metrics that were not deterministically computable on prose into pure structural joins, and what do the numbers show?*

**Answer: yes on computability.** All eight Tier-A metrics ran corpus-wide with no LLM and no network, identically run-to-run, over 12 ARAs — and one (`broken_ref_integrity`) caught a real structural defect prose cannot express. **But deliberately narrow:** deterministic tier only; the anchored tier (real DOI/registry resolution) and judged tier (novelty, entailment quality) were not run; the extensions are themselves LLM-authored (a fidelity ceiling); and nothing here tests whether the metrics discriminate good science from bad.

## Contents

- **[`gro-experiment-paper.pdf`](gro-experiment-paper.pdf)** / **[`EXPERIMENT_PAPER.md`](EXPERIMENT_PAPER.md)** — the write-up (5pp).
- **`gro_metrics.py`** — the metric implementation (pure structural joins over the sidecars; no LLM, no network). Re-runnable: `python3 gro_metrics.py`.
- **`results.json`** / **`results.md`** — the actual program output (12 ARAs, 0 failures). *These numbers were independently re-run and verified against the committed code.*
- **`extensions/<slug>/`** — the GRO deterministic-tier sidecars generated per ARA (`quantities.yaml`, `claims_typed.yaml`, `refs.yaml`, `entities.yaml`, `genre.yaml`), 12 ARAs × 5 files. These are copies; they also live alongside each source ARA in the parent repo at `research/ara-library/<slug>/gro/`.

## Headline numbers (corpus, 12 ARAs)

| Metric | Mean | Reads |
|---|---|---|
| quantity_reconciliation_rate | 1.000 (10/12 defined) | typed quantities |
| claim_typing_coverage | 1.000 | claim_type + logical_form present |
| entailment_precondition_rate | 0.821 | claim ↔ quantity(result) ↔ proof link |
| reference_resolvability_rate | 0.374 | refs with a printed resolvable id |
| entity_anchoring_rate | 0.000 | entities with an ontology xref (uniformly empty — a real, now-visible gap) |
| genre_silent_omissions | total 4 | expected − present − declared-absent slots |
| overclaim_flags | total 23 | generality-tier claims missing n (concentrated in cum26, xu25) |
| broken_ref_integrity | total 16 | dangling proof/quantity/concept refs (all in ard25 — a genuine structural defect) |

The load-bearing result is a *before/after about computability*, not a quality verdict: on raw prose none of these eight is a lookup (the field the metric reads does not exist until typed); after extension every one is a join. What the deterministic tier certifies is the coherence of a typed record — not the correctness, validity, or importance of the science, and not anything about the world outside the file. See the paper's §5–6 for the full boundary.
