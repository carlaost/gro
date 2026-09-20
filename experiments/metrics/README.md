# metrics/ — the incentive-design program

The "reward what citations punish" program: the metrics, the code that computes them, the negative-result experiments, and the design tournaments that selected them. This is the work that motivated the GRO substrate; the headline is one level up in [`../METRICS.md`](../METRICS.md).

## Contents

**Specifications & findings**
- [`directions.md`](directions.md) — the seven metric directions + the governing thesis.
- [`candidates.md`](candidates.md) — the indicator ledger: 64 candidates → 23 survivors → TOP-10.
- [`merged.md`](merged.md) — the full merged metric suite (four sources).
- [`data-shapes.md`](data-shapes.md) — the artifact surfaces the metrics compute over.
- [`findings.md`](findings.md) — **the negative result** (fidelity, not quality).
- [`novelty-comparison.md`](novelty-comparison.md) — positioning vs LENS / the Metascience Novelty Indicators Challenge.
- [`verifier-comparison.md`](verifier-comparison.md) — positioning vs the ARA rigor seal (integrity, not novelty/fidelity).
- [`library-metrics.md`](library-metrics.md) — the computed metrics over the test library (summary).

**`analysis/`** — supporting analysis: `comparison-v2-v3.md`, `validator-reliability.md`, `compiler-model.md`, `plan.md`, `loop-log.md` (the autonomous-loop record).

**`code/`** — the compute. `claim_graph.py` (the flagship cross-library evidential claim graph), `compute_metrics_v3.py` (the metric runner), plus the experiment modules: `extractive_fidelity.py`, `grounding.py`, `outcome_switching.py`, `detectors.py`, `external.py`, `library_graph.py`, `sem_metrics.py`. This code runs over the ARA testbed — it is the instrument, not part of the GRO spec.

**`tournaments/`** — the two blind adversarial tournaments that produced the metrics; winners + judgements. See [`tournaments/README.md`](tournaments/README.md).

## The one open experiment

The negative result left a question the whole program turns on: do the affordance-derived metrics actually **discriminate** good science from bad, over real literature, validated against external ground truth (trial-registry concordance, retraction/correction records, prior-literature novelty)? That experiment has not been run. It is the prime next step.
