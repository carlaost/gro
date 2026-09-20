# Does typed extension make prose-blocked metrics deterministically computable? A deterministic-tier GRO experiment over 12 compiled ARAs

**Source paper**: `research/metrics/v4-gro/EXPERIMENT_PAPER.md`

## Summary

Twelve already-compiled Agent-Native Research Artifacts (ARAs) were extended with five deterministic-tier GRO sidecars each (`quantities.yaml`, `claims_typed.yaml`, `refs.yaml`, `entities.yaml`, `genre.yaml`), and the eight Tier-A ("deterministic") metrics from the GRO spec were then computed as pure structural joins over those sidecars — zero LLM calls, zero network calls. All eight metrics are marked `computable_on_prose: false` on the raw prose ARA, because the fields they read (`claim_type`, `logical_form`, `quantity_ref`/`proof_ref` links, `resolvable`, `xref`, `expected_slots`/`present_slots`/`absent_declared`, `population_n`) simply don't exist until someone types them. After extension, all eight ran as deterministic lookups across all 12 ARAs with zero failures, and one of them (`broken_ref_integrity`) caught a real structural defect — a proof-reference graph in `ard25` with no experiment ledger to resolve against (16/16 broken). The result is explicitly narrow: this is the deterministic tier only (no anchored DOI/registry resolution, no judged novelty/entailment review); the sidecars were themselves LLM-generated, which caps fidelity; and no test was run of whether these metrics discriminate good science from bad, because every metric reads only the typed artifact, never the outside world.

## Layer index

- `logic/problem.md` — the observations and gaps motivating the experiment (why the deterministic tier's computability was an open question, and why "does it discriminate quality" is explicitly out of scope).
- `logic/claims.md` — 11 load-bearing findings (C01–C11), each with a falsifiable statement, status, falsification criteria, proof reference, and verbatim-quoted sources.
- `logic/experiments.md` — 9 experiment/analysis blocks (E01–E09): the extension phase, the corpus-wide metric run (incl. the Unicode-minus bug), five per-metric case studies, the prose-baseline contrast, and the (not-run) ground-truth discrimination check.
- `evidence/README.md` — pointers to the underlying run artifacts (`results.json`, `results.md`, `gro_metrics.py`, per-ARA `gro/*.yaml` sidecars, `seal/`).
