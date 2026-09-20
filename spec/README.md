# The GRO schema

GRO, the Grounded Research Object, is a schema for publishing scientific work. A GRO record is a
directory. It keeps the readable prose of the work and, next to it, a small set of typed files in
which every load-bearing fact is written once, given an id, and anchored to the text it came
from. The prose points at the ids; nothing is retyped.

The schema records **what is present in a piece of research**. It does not record what anyone
thinks of it. Whether the work is credible, novel, rigorous or important is decided by funders,
curators and validators, on their side, with their own methods, reading the record. Nothing
judged, fetched or resolved is ever written into a record.

The machine-readable contract is [`material.gro.openapi.yaml`](material.gro.openapi.yaml)
(OpenAPI 3.1; every field carries an example). This page is the same thing in prose.

## The record, file by file

**`PAPER.md` front matter.** Title, authors, year, venue, DOI, and a `grounding` tag saying
whether the record was compiled from full text, abstract only, or metadata only.

**`gro/temporal.yaml`.** Publication date, DOI, and the timestamp of compilation.

**`gro/refs.yaml`.** One row per reference, as cited. An external id (DOI, arXiv, dataset id)
only if it is printed in the source.

**`gro/quantities.yaml`.** One row per load-bearing number: its value, unit, comparator, role
(input or result), the verbatim quote it was transcribed from, and the claims it belongs to.

**`gro/entities.yaml`.** One row per term, method, measure, dataset, gene, organism or
population the claims name, with a stable id and an ontology cross-reference if one is printed.

**`gro/claims_typed.yaml`.** One row per claim, recording its structural form only: type
(existence, comparison, causal, prediction, ...), polarity, a logical-form line, population
scope, and links to the quantities, entities and proofs it rests on. There is no status,
quality or novelty field.

**`gro/genre.yaml`.** The paper type, the sections that type is expected to carry, which of them
are present, and which are declared absent. An honest absence is a fact, not a gap.

**`gro/contributions.yaml`.** What the authors say they contribute, each linked to the claims
that realize it. No typing of novelty, no confidence, no assessment.

Any slot not yet read from the source is `pending_extraction`. That is a "not read yet" marker,
never a deferred judgment, and it is always preferable to a plausible guess.

## Candidate layers, not active

These record things that are present in the research and were named in earlier drafts but are
implemented by no compiler today. They are listed so the boundary is visible, not as promises.

- **Citation locations.** Where in the text each reference is cited, not only the reference list.
- **Accession ids.** Trial registrations, dataset accessions and similar ids as printed in the
  paper. The id is material. Checking it against a registry is not.
- **Experiments and problem statement** as typed layers, not only prose.

The test for admitting anything: if it is present in the research, it can be schema. If it
must be fetched, resolved or judged, it is not.

## Versioning and implementers

The contract carries `info.version`. This repository is the canonical location; compilers vendor
a pinned copy and declare which version they implement. Today:

| Compiler | Repo | Implements |
|---|---|---|
| live per-turn plugin for Claude Code | `carlaost/gro-compiler` | material 0.1.1 |
| retrospective full-text compiler | `carlaost/paper2gro` | material 0.1.1 (its former measuring half is being removed) |

`sync.sh` in this directory copies the contract into the compiler repos and stamps their
`spec/SPEC_VERSION`.

## Where this came from

The shape was arrived at through a design tournament in July 2026 and a series of measurement
experiments over compiled records. Those live under [`../experiments/`](../experiments/) and are
our method for testing whether the schema is useful, not part of it. The July draft that fused
the two is kept frozen at [`../experiments/history/SPEC-2026-07.md`](../experiments/history/SPEC-2026-07.md).
