# Working in this repo

This repository is the home of GRO, the Grounded Research Object: **a schema for publishing
scientific work**. GRO records what is present in a piece of research. It does not measure,
score, rank or judge anything; that is done by funders, curators and validators on their side.
The experiments under `experiments/` are our method for testing whether the schema is useful,
nothing more. Never describe GRO through "signals", "rigor tiers", "credibility" or "eval".

## Two files every session reads first and writes before ending

Both are gitignored. If either is missing, create it from the description here.

1. **`WORKING-NOTES.md`**: Open items, dated Decisions with reasons, and a dated Log of what each
   session did. Read it before doing anything. Append a Log line before ending any turn that
   changed something. Record every decision Carla makes, with her reason.

2. **`SCHEMA-LEARNINGS.md`**: the running list of what we learn about the schema by using it,
   one dated entry per observation, never deleted. **You must add to it whenever you compile a
   record, read a compiled record, run or read an experiment, or notice that a field, enum or
   slot does not fit what the research contains.** Do this even if Carla did not ask. An
   observation that a field forced a choice the source did not support is exactly what this
   file is for. Observations are not schema changes; changes happen in `spec/` and go in
   WORKING-NOTES Decisions.

## Dogfooding

This repo records its own work as a research record in `ara/`. At the end of a turn with
research-significant activity, run the `research-manager` skill (ara root is `ara/`), then the
gro-compiler skill from `~/code/gro-compiler/skills/gro-compiler/SKILL.md` with `<ARA>=ara`
(material only, writes `ara/gro/`). Skip both on empty turns.

## Layout

- `spec/` the schema: the contract (`material.gro.openapi.yaml`), its prose page, `sync.sh`.
- `experiments/` our method: metrics work, runs, and `history/` (the frozen July draft; unedited).
- `ara/` this project's own research record and material layer.

Do not edit anything under `experiments/history/` or the results in `experiments/runs/`.
Commit only when Carla asks.
