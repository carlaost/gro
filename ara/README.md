# ARA research-record

This is the Agent-Native Research Artifact (ARA) that **documents the research program that produced GRO** — the self-describing record of the work, not a testbed input. It is included here because the program critiques the ARA format from the inside, and this is the artifact that captured that journey as it happened.

It is a snapshot of the parent repo's `research/ara/`, trimmed to the research-record layers (the ~6 MB of testbed figure binaries under `evidence/figures/` and the physical `src/` layer are omitted; they are corpus inputs, not outcomes of this work).

## Layout

- **`PAPER.md`** — root manifest.
- **`logic/`** — the *current best understanding*: crystallized claims (C01–C16), concepts, problem, experiments, solution. Mutable, present-state snapshots.
- **`trace/`** — append-only journey record: `exploration_tree.yaml` (the research DAG — decisions, experiments, dead ends, incl. the GRO nodes N51–N54), `sessions/` (per-day session records), `pm_reasoning_log.yaml` (the process manager's own decisions).
- **`staging/`** — the crystallization buffer: interpretive observations (O01–O31) awaiting a closure signal before they become typed claims. This includes the GRO-relevant findings (O30 the trust-relocation critique; O31 the layer-cake coherence check).

## How to read the GRO thread specifically

- Nodes **N50–N54** in `trace/exploration_tree.yaml`: the metric tournament → affordance gap → format tournament → GRO spec → the public write-ups.
- Observations **O27–O31** in `staging/observations.yaml`: the negative-result convergence, the external-benchmark axis finding, and the two GRO critiques.
- Session **`trace/sessions/2026-07-07_001.yaml`**: the day the GRO spec was finalized.

Note: this is a record of process, staged and crystallized under a progressive-crystallization discipline — an observation is not a settled claim until a closure signal fired. Provenance tags (`user` / `ai-suggested` / `ai-executed` / `user-revised`) mark who introduced each item.
