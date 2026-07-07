# Evidence Index

> This ARA compiles `research/metrics/v4-gro/COMPARISON_PAPER.md`, one of our own metascience research outputs. All quoted numbers in `../logic/claims.md` and `../logic/experiments.md` are copied verbatim from that paper's text/tables. The computed artifacts the paper's tables and figures were generated from are **not duplicated here** — they live in `research/metrics/v4-gro/` alongside the paper, and are pointed to below.

## Source paper
| File | Description |
|------|-------------|
| [`../../../metrics/v4-gro/COMPARISON_PAPER.md`](../../../metrics/v4-gro/COMPARISON_PAPER.md) | The full comparison paper this ARA compiles ("Three Ways to Judge an Agent-Native Research Artifact") |
| [`../../../metrics/v4-gro/EXPERIMENT_PAPER.md`](../../../metrics/v4-gro/EXPERIMENT_PAPER.md) | Companion paper on the GRO metric design experiment (not compiled into this ARA; background only) |
| [`../../../metrics/v4-gro/EXTERNAL_VALIDATION_PAPER.md`](../../../metrics/v4-gro/EXTERNAL_VALIDATION_PAPER.md) | Companion paper on the external validation methodology behind Tier B (not compiled into this ARA; background only) |
| [`../../../metrics/v4-gro/gro-comparison-paper.pdf`](../../../metrics/v4-gro/gro-comparison-paper.pdf) / `.html` | Rendered versions of the source paper |

## Computed artifacts (back the paper's numbers, referenced by filename in `Sources:` lines)
| File | Description | Backs |
|------|-------------|-------|
| [`../../../metrics/v4-gro/results.json`](../../../metrics/v4-gro/results.json) / `results.md` | Full GRO metric run over all 12 ARAs: per-metric per-ARA values, corpus stats, reliability verdicts | C07, C09, C10 |
| [`../../../metrics/v4-gro/benchmark.py`](../../../metrics/v4-gro/benchmark.py) / [`benchmark.json`](../../../metrics/v4-gro/benchmark.json) | The H1/H2 substrate benchmark: per-ARA `prose` vs `typed` vs `truth` blocks for the 4 shared metrics, plus timing data | C01, C02, C03 |
| [`../../../metrics/v4-gro/compare/gro_metrics_analysis.json`](../../../metrics/v4-gro/compare/gro_metrics_analysis.json) | GRO's self-ranking of its own metrics by reliability (best-3 / most-uncertain-3), corpus-wide stats, cross-cutting caveats | C10 |
| [`../../../metrics/v4-gro/compare/gro_vs_v3.json`](../../../metrics/v4-gro/compare/gro_vs_v3.json) | Coverage, construct-mapping, agreement/divergence comparison of GRO vs the v3 metric design | C06, C08, C09 |
| [`../../../metrics/v4-gro/compare/vs_seal.json`](../../../metrics/v4-gro/compare/vs_seal.json) | Head-to-head GRO vs Seal L2 comparison: per-ARA scorecard, catch/miss inventory, three-way rank correlation | C04, C05, C09 |
| [`../../../metrics/v4-gro/external_validation.json`](../../../metrics/v4-gro/external_validation.json) | Corpus-level summary of the externally anchored check (declared vs observed reference-resolvability, retractions, novelty, registry concordance) | C07 |
| [`../../../metrics/v4-gro/external/`](../../../metrics/v4-gro/external/) | Per-ARA live PubMed/registry lookup results for the 6-ARA anchored cluster (che26, val25, han26, zim25, jes26, tit26) | C07 |
| [`../../../metrics/v4-gro/seal/`](../../../metrics/v4-gro/seal/) | Per-ARA Seal Level 2 review JSON (D1-D6 scores, overall, recommendation, narrative findings) for all 12 ARAs | C04, C05, C08, C09 |
| [`../../../metrics/v4-gro/figures/`](../../../metrics/v4-gro/figures/) | Rendered figures referenced in the paper (`[[FIG:...]]` markers): tier_coverage, bench_coverage, bench_fidelity, bench_shape_speed, gro_metric_grid, verifier_vs_gro, seal_dimensions, three_way_rank | all |

## Underlying 12-ARA corpus (what GRO/v3/Seal were run against)
The 12 ARAs scored by this comparison (che26, val25, han26, zim25, jes26, tit26, gau25, zho25, aki26, cum26, xu25, ard25) are separately compiled artifacts under `research/ara-library/` and `research/data/lib/`; they are the *subjects* of this comparison paper, not evidence for it, and are not re-indexed here. Per-ARA scores from each instrument are captured in the `compare/*.json` and `seal/*.json` files above.

## Numbered objects not filed
The paper's `[[FIG:...]]` figure placeholders correspond 1:1 to files in `../../../metrics/v4-gro/figures/`, listed above rather than duplicated as separate evidence-table rows, since they are illustrations of the same underlying JSON data already indexed.
