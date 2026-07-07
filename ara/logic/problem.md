# Problem Specification

> **Project framing.** This ARA is the research artifact for Carla Ostmann's *desciencemodel*
> project on **agent-native scientific knowledge representation**: how scientific knowledge should
> be represented, published, and reused when AI agents — not only humans — read, reason over, and
> extend it. It draws on four sources: the ARA protocol paper (Liu et al., 2026), a concrete
> implementation (the *oshima* paper-ingestion API), a domain case study (Otte et al., 2025,
> multi-omics embeddings), and two of the author's essays.

## Observations

### O1: The narrative paper is a lossy compression of the research process
- **Statement**: Publication compresses a branching, iterative research process into a linear
  narrative, discarding failed experiments, rejected hypotheses, and the exploration process (the
  "Storytelling Tax"), and leaving a gap between reviewer-sufficient prose and agent-sufficient
  specification (the "Engineering Tax").
- **Evidence**: ARA paper, Abstract & §1; figures `ara_figure1` (PDF-lossy vs ARA-lossless),
  `ara_figure2` (branching vs linear).
- **Implication**: What is tolerable for human readers becomes critical when AI agents must
  understand, reproduce, and extend the work.

### O2: Published artifacts systematically under-specify reproduction
- **Statement**: Across an expert reproduction rubric, only 45.4% of reproduction-critical
  requirements are fully specified in the published artifact; missing hyperparameters alone account
  for 26.2% of gaps.
- **Evidence**: ARA paper §7.1, `ara_table8`, `ara_table9`, `ara_figure3`.
- **Implication**: Reproduction agents (and humans) must guess unstated details, lowering
  reproduction success.

### O3: Most agent exploration compute is failed work that never reaches the paper
- **Statement**: In large agent run corpora, below-reference (failed) runs account for 90.2% of
  total dollar cost (and 59.2% of tokens); the median failed-to-success token ratio is 113×.
- **Evidence**: ARA paper §7.4, `ara_table10`.
- **Implication**: The most expensive part of research — the failures — is exactly what narrative
  compilation discards, so successors repeat it.

### O4: The paper has become conflated with scientific output, and citations a broken proxy for quality
- **Statement**: Researchers work "on a paper" rather than on ideas, and citation counts —
  originally a relevance signal — become a scalable proxy for merit, conflating influence with
  quality. By Goodhart's Law, once the measure becomes the target it ceases to be a good measure,
  incentivizing citable work (reviews, positive results) over neglected work (negative results,
  replications).
- **Evidence**: Ostmann, "Papers Block Scientific Progress" (2026-04-15),
  `research/sources/substack/papers-block-scientific-progress.md`.
- **Implication**: Fixing metrics alone is insufficient; the unit of scientific output (the paper)
  itself must be reconceived.

### O5: Existing structured-science standards each cover only a fragment of agent-native needs
- **Statement**: FAIR, nanopublications, RO-Crate, ORKG, experiment trackers (MLflow, W&B), and
  agent-doc standards (AGENTS.md) each formalize one aspect (data metadata / atomic claims /
  archival bundles / structured contributions / runs / agent instructions) but none jointly provide
  execution semantics, cross-layer bindings, and decision history. Existing tools cover ≤2 of 5
  agent-native dimensions.
- **Evidence**: ARA paper §2 & §8, `ara_table5`.
- **Implication**: A new structural layer is needed, not another metadata schema.

### O6: Biological knowledge is siloed per-omics and lacks a shared, machine-usable representation
- **Statement**: ML embeddings exist for individual biological entities (metabolites, proteins,
  genes, enzymes) but are specialized to single omics and lack cross-modal context, while disease
  progression and biosynthesis are governed by multi-layered networks integrating diverse omics.
- **Evidence**: Otte et al. 2025, Abstract & §1; `mo_figure1`.
- **Implication**: Representing scientific knowledge for machines in a domain (biology) requires a
  shared space where cross-omics relations are first-class — a concrete instance of the general
  representation problem.

## Gaps

### G1: No representation makes the full research object machine-executable
- **Statement**: There is no widely adopted representation in which an AI agent can navigate a
  work's reasoning, code+specs, exploration history, and evidence, with the links between them.
- **Caused by**: O1, O5.
- **Existing attempts**: Narrative PDFs + GitHub + trackers (siloed); FAIR/nanopubs/RO-Crate/ORKG
  (partial). 
- **Why they fail**: They keep knowledge unlinked across silos (no cross-layer forensic bindings).

### G2: Process knowledge (failures, decisions) is destroyed at authoring time
- **Statement**: The branching exploration and its dead ends — the most costly knowledge (O3) — is
  not captured as it happens, so it cannot be preserved.
- **Caused by**: O1, O3.
- **Existing attempts**: Post-hoc tacit-knowledge recovery from papers.
- **Why they fail**: They reconstruct after the fact and still leave decision history unmodeled.

### G3: An AI-first knowledge representation is not directly actionable by humans
- **Statement**: Representations optimized for machines (e.g. embedding spaces, FOL stores) are not
  human-readable; "none of us speak vector." Without a decoding/human-readable layer, an AI-first
  record cannot drive human hypotheses, designs, or interventions.
- **Caused by**: O6 + the move toward machine-readable science.
- **Existing attempts**: Raw embedding spaces; structured stores.
- **Why they fail**: They surface vectors/logic, not decoded hypotheses a scientist can act on.

### G4: Review cannot scale to machine-generated/large research output
- **Statement**: Human peer review is the bottleneck, and LLM-as-judge review exhibits grade
  inflation and finding–score decoupling.
- **Caused by**: O1, O4, and the growth of agent-produced work.
- **Existing attempts**: LLM-as-judge auditors.
- **Why they fail**: They round up to Accept and do not let critical findings lower scores.

## Key Insight
- **Insight**: Treat the evolving **knowledge object** — not the paper — as primary
  ("Knowledge over Narrative"), and represent it as a structured, machine-executable artifact with
  explicit cross-layer links (reasoning ↔ code/specs ↔ exploration history ↔ evidence). Capture the
  process (including failures) *as it happens*, validate it with machine-checkable credentials, and
  — crucially — keep a **human-readable layer on top of the AI-first record** so the machine
  representation decodes back into hypotheses, designs, datasets, and protocols a scientist can act
  on. The narrative paper becomes one compiled *view* of this object, not the object itself.
- **Derived from**: O1, O3, O5, O6; Ostmann essays; ARA protocol; oshima implementation;
  multi-omics case.
- **Enables**: Agent-native artifacts (ARA) that improve understanding and reproduction; live
  capture of process; systems (oshima) that compile papers into structured claims/evidence/logic;
  and domain representations (multi-omics embeddings) whose synthetic points decode into actionable
  candidates ("alien proteins").

## Assumptions
- A1: Research increasingly runs through AI-native workflows, so capture-as-you-go and
  agent-executable artifacts are feasible.
- A2: A "sufficiently capable coding agent" is the reproduction target; sufficiency is
  capability-relative, so artifacts remain valid as agents improve (ARA paper §3).
- A3: For the biological case, curated pathway databases (MetaCyc) approximate real interaction
  networks well enough to learn a useful embedding (Otte et al.).
- A4: Even an AI-first record needs a human-readable layer to be useful for human-led science
  (Ostmann, "Alien Proteins").
