# GRO — the Grounded Research Object

*A schema for publishing scientific work so that what is in it is addressable: every load-bearing
fact written once, given an id, anchored to the text it came from. This repository is the
canonical home of the schema. It also holds the experiments we run to test whether the schema is
useful, which are our method and not part of what anyone publishes in.*

## What a GRO record is, right now

A GRO record is a directory: the readable prose of the work plus a small set of typed files.
The contract is [`spec/material.gro.openapi.yaml`](spec/material.gro.openapi.yaml), version 0.1.1.
In prose:

| File | What it records |
|---|---|
| `PAPER.md` front matter | title, authors, year, venue, DOI, and whether the record was compiled from full text, abstract only, or metadata only |
| `gro/temporal.yaml` | publication date, DOI, compile timestamp |
| `gro/refs.yaml` | one row per reference as cited; an external id only if printed in the source |
| `gro/quantities.yaml` | one row per load-bearing number, with the verbatim quote it came from and the claims it belongs to |
| `gro/entities.yaml` | one row per term, method, measure, dataset, gene, organism or population the claims name |
| `gro/claims_typed.yaml` | one row per claim, structural form only: type, polarity, logical form, population scope, links to quantities, entities and proofs. No status or quality field |
| `gro/genre.yaml` | paper type; the sections that type expects; which are present; which are declared absent |
| `gro/contributions.yaml` | what the authors say they contribute, each linked to the claims that realize it. No novelty typing |

Any slot not yet read from the source is `pending_extraction`. Nothing in a record is fetched,
resolved or judged. Three further layers that record things present in the research are named
as candidates in [`spec/README.md`](spec/README.md); no compiler implements them yet.

## What GRO is not

GRO does not measure anything. Whether work is credible, novel, rigorous or important is decided
by funders, curators and validators, on their side, with their own methods, reading the record.
The schema's job is to make the facts they need addressable, so those readings can be specific
and checkable. It is a format people publish in, and that is all it is.

## The experiments in this repository

Under [`experiments/`](experiments/) we try to measure scientific work over compiled records.
We do this for one reason: to test whether the schema is useful the way funders need it to be,
maximally readable for the specific signals they care about. When an experiment shows a fact is
buried in prose, retyped in four places, or indistinguishable from an omission, that is a finding
about the shape, and the shape changes. The measurements themselves are not published, shipped
or maintained.

Two findings so far set the boundary. Typing the record turns prose-blocked checks into plain
joins. And a record read alone tells you how well it was compiled, not how good the science is;
any reading of quality needs something outside the record. Both are written up under
`experiments/`, with the emitter version each ran on.

## Compilers

Records are produced by the compilers under [`compilers/`](compilers/):

- [`compilers/gro-compiler/`](compilers/gro-compiler/): a Claude Code plugin that keeps a research
  project's record compiled live, at the end of every turn, from the project's ARA (Agent-Native
  Research Artifact). Install with `/plugin marketplace add carlaost/gro` then
  `/plugin install gro-compiler@gro`.
- [`compilers/paper2gro/`](compilers/paper2gro/): a retrospective compiler from a paper's full text.
  It still writes its former measuring half into records; removing that is open work.

GRO is primarily a format for new work: a shape research is born into, capturing at production
time what a paper discards. Backfilling existing literature is a supporting move, and a
backfilled record is permanently lossy, because the source was written to fit the paper's shape.

## Repository layout

```
gro/
  README.md          # you are here
  spec/              # the schema: the contract, its prose page, the sync script
  compilers/         # gro-compiler (live plugin) and paper2gro (retrospective)
  experiments/       # our method: measurement experiments over compiled records, and history
  ara/               # this project's own research record (process trace)
```

## How the shape was arrived at

Papers and citations are a Goodharted proxy for scientific quality. We asked what one would
want to measure instead, drafted 64 candidate indicators, and ran them through blind design
tournaments over a corpus of compiled Alzheimer's papers. The result was negative in a useful
way: indicators over a record's own structure read its fidelity, not its science, and most of
what blocked a good indicator was the shape of the record, not feasibility. Auditing every
blocked indicator against the shape that blocked it produced twelve format gaps; a design
tournament over those gaps produced the July 2026 draft. That draft fused the shape with
measuring machinery. The fusion was a mistake, and the current schema is what remains once
everything judged, fetched or resolved is taken out. The full history, unedited, is under
[`experiments/history/`](experiments/history/).
