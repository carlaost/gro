---
title: "desciencemodel — Agent-Native Scientific Knowledge Representation (compiled project artifact)"
authors:
  - "Carla Ostmann (project lead / compiler)"
  - "drawing on: Jiachen Liu et al. (ARA protocol, 2026)"
  - "Lennart B. Otte, Christer Hogstrand, Adil Mardinoglu, Miao Guo (multi-omics, 2025)"
year: 2026
venue: "ARA — compiled project artifact (not a single published paper)"
doi: "n/a — sources: arXiv:2604.24658v3 (ARA); doi:10.69997/sct.136974 / LAPSE:2025.0524 (multi-omics)"
ara_version: "1.0"
domain: "Scientific knowledge representation; agent-native research infrastructure; computational biology (case study)"
keywords:
  - agent-native research artifact
  - scientific knowledge representation
  - reproducibility
  - exploration graph
  - claims and evidence
  - first-order logic extraction
  - multi-omics embeddings
  - human-readable AI-first records
claims_summary:
  - "C01: ARA raises agent QA accuracy (93.7% vs 72.4%)"
  - "C02: ARA's understanding gains are largest on failure-knowledge questions (+65.7%)"
  - "C03: ARA improves reproduction (64.4% vs 57.4%), widening with difficulty"
  - "C04: Published artifacts under-specify reproduction (only 45.4% fully specified)"
  - "C05: Most agent exploration compute is failed work (90.2% of cost)"
  - "C06: Preserved failure traces accelerate the first useful extension move"
  - "C07: Trace value is capability-relative and can constrain a stronger agent"
  - "C08: The L2 Rigor Auditor catches high-severity flaws but misses orphan experiments"
  - "C09: ARA covers all five agent-native dimensions; existing tools cover at most two"
  - "C10: The oshima API ingests papers and extracts structured claims with typed evidence"
  - "C11: The oshima API converts extracted statements into first-order logic"
  - "C12: The oshima API synthesizes cross-paper themes over a library"
  - "C13: A Word2Vec-style shared embedding co-locates omics modalities into meaningful clusters"
  - "C14: Pairwise embedding dot-products are bimodal, separating related from unrelated nodes"
  - "C15: Embedding proximity recovers known cross-omics biochemical relationships"
abstract: "This artifact is the compiled research object for the desciencemodel project on agent-native scientific knowledge representation: how scientific knowledge should be represented, published, and reused when AI agents — not only humans — read, reason over, and extend it. It integrates four sources into one ARA. The ARA protocol (Liu et al., 2026) supplies the representation: a four-layer agent-executable package (logic, code+specs, exploration graph, evidence) with cross-layer forensic bindings, plus skills for live capture, compilation, and review; its evaluations show large gains in agent understanding and reproduction and quantify the information and failure-cost taxes of narrative papers. The oshima API supplies a working implementation that ingests paper PDFs into structured claims, typed evidence, first-order logic, and cross-paper themes. The multi-omics embedding (Otte et al., 2025) supplies a domain case in which geometry stands in for biology and a synthetic point can decode into candidate pathways or 'alien proteins.' Two essays by the project lead frame the problem (the paper as a bottleneck; citations as a broken proxy) and the synthesizing thesis: even an AI-first record needs a human-readable decoding layer to drive human-led science."
---

# desciencemodel — Agent-Native Scientific Knowledge Representation

## Overview

The *desciencemodel* project asks how scientific knowledge should be represented for an era in which
AI agents read, reproduce, and extend research. This ARA compiles four sources into one knowledge
object: the **ARA protocol** (the representation and its evaluation), the **oshima API** (a concrete
system that turns papers into structured claims/evidence/logic/themes), the **multi-omics embedding**
(a domain case where a shared vector space encodes cross-omics biology and decodes into candidate
discoveries), and two **essays** by the project lead that frame the problem and the unifying thesis —
that an AI-first record still needs a human-readable layer on top.

This file is itself an instance of the architecture it documents (see `logic/solution/architecture.md`).

## Layer Index

### Cognitive Layer (`/logic`)
| File | Description |
|------|-------------|
| [problem.md](logic/problem.md) | Observations → gaps → key insight (across all four sources + essays) |
| [claims.md](logic/claims.md) | 15 falsifiable claims (C01–C15), grounded by source |
| [concepts.md](logic/concepts.md) | 16 technical concepts spanning the protocol, the system, and the domain |
| [experiments.md](logic/experiments.md) | 11 verification plans (E01–E11) |
| [related_work.md](logic/related_work.md) | Typed dependency graph (RW01–RW10) + full citation footprint |
| [solution/constraints.md](logic/solution/constraints.md) | Boundary conditions, assumptions, limitations |
| [solution/architecture.md](logic/solution/architecture.md) | The ARA protocol, the oshima system, and the multi-omics model |

### Physical Layer (`/src`)
| File | Description | Claims |
|------|-------------|--------|
| [environment.md](src/environment.md) | Runtime/deps/hardware for the oshima implementation | C10–C12 |
| [artifacts.md](src/artifacts.md) | The oshima API as a deliverable (endpoints, capabilities) | C10–C12 |
| [execution/app/](src/execution/) | 21 transcribed core source files (FastAPI service, extraction, NL→FOL, themes, workers) | C10, C11, C12 |

### Exploration Graph (`/trace`)
| File | Description |
|------|-------------|
| [exploration_tree.yaml](trace/exploration_tree.yaml) | 24-node research DAG: questions, decisions, experiments, dead ends, a pivot |

### Evidence (`/evidence`)
| File | Description |
|------|-------------|
| [README.md](evidence/README.md) | Index of 14 tables + 19 figures (15 ARA + 4 multi-omics), each with screenshot |

## Source materials
Staged under `research/sources/`: the ARA paper PDF, the multi-omics paper PDF, and the two essays
(`substack/`). The oshima API code lives at its repo (`/Users/carlaostmann/code/oshima/api`) and is
transcribed into `src/execution/`.
