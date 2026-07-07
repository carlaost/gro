# metrics/tournaments/ — how the metrics were selected

Two blind, adversarial tournaments. The point of the format is that a metric can't be graded by whoever proposed it: independent proposers, a separate judge, critique-driven refinement.

## Round 1 — per artifact surface

For each of the 11 artifact surfaces (paper manifest, claims, concepts, problem, experiments, related work, solution, exploration tree, evidence, implementation, dataset): four clean-room proposers (no sight of any existing metric) each proposed metrics → a meta-science judge picked the best two → both improved against critique → the judge picked one winner. ~88 subagents.

- **[`round1-summary.md`](round1-summary.md)** — the summary: per-artifact winner + the cross-artifact synthesis (this is where the "hygiene, not truth" finding surfaced, blind, corroborating [`../findings.md`](../findings.md)).
- **[`round1-log.md`](round1-log.md)** — the run log.
- **[`round1-proposer-brief.md`](round1-proposer-brief.md)**, **[`round1-critique-brief.md`](round1-critique-brief.md)** — the briefs the proposers and judge worked from.
- **[`round1/`](round1/)** — per artifact (`01_paper_manifest/` … `11_dataset/`): `proposals/` (the four-agent field), `critique_stage1.md` + `critique_stage2.md` (**the judgements**), `improved/` (**the winning refined proposals**, A and B).

## Round 2 — per metric

The TOP-10 survivors from the ledger each ran a `4 → 2 → 1` tournament over three refine cycles.

- **[`round2-log.md`](round2-log.md)**, **[`round2-expand-brief.md`](round2-expand-brief.md)** — the log and the expander brief.
- **[`round2/`](round2/)** — per metric (`M09`, `M14`, `M17`, `M18`, `M19`, `M30`, `M32`, `M36`, `M48`, `M64`): `brief.md`, `proposals/` (the field), `critique_c1.md` + `critique_c2.md` (**the judgements** across cycles), `improved_c2/` + `improved_c3/` (**the winning refined proposals** per cycle).

## How to read a tournament outcome

Start at `round1-summary.md` for the verdicts and the synthesis. To see a specific metric's reasoning, open its subdir: the `critique_*` files are the judge's argument for the winner and against the losers; the `improved_*` folders are the surviving designs. The full four-agent field is in `proposals/` so the judgement can be checked against what it chose between.
