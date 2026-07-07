# Concepts

Cross-source technical vocabulary for agent-native scientific knowledge representation. Terms are
grouped by source but form one shared conceptual space for the project.

## Agent-Native Research Artifact (ARA)
- **Notation**: —
- **Definition**: A file-system protocol that replaces the narrative paper with an agent-executable
  research package structured around four layers — scientific logic (`/logic`), executable code with
  full specifications (`/src`), an exploration graph (`/trace`), and evidence grounding every claim
  (`/evidence`) — unified by a `PAPER.md` manifest. Grounded in the principle *Knowledge over
  Narrative*.
- **Boundary conditions**: Defined and evaluated for ML/computational research; generalization to
  wet-lab/theoretical work is stated as future work (ARA paper §10).
- **Related concepts**: Cognitive/Physical/Exploration/Evidence Layer, Cross-layer forensic bindings.

## Storytelling Tax / Engineering Tax
- **Notation**: —
- **Definition**: The two structural costs of compiling research into a linear narrative. The
  *Storytelling Tax* is the erasure of branching process and failure knowledge to fit a linear
  story; the *Engineering Tax* is the gap between reviewer-sufficient prose and agent-sufficient
  specification (unwritten tacit knowledge, cf. Polanyi 1966).
- **Boundary conditions**: Costs are tolerable for human readers, critical for AI agents.
- **Related concepts**: ARA, Sufficiency.

## Cognitive / Physical / Exploration / Evidence Layers
- **Notation**: `/logic`, `/src`, `/trace`, `/evidence`
- **Definition**: The four ARA layers. `/logic` = problem, solution (architecture/algorithm/
  heuristics), falsifiable claims with proof pointers, experiment plans, concepts, typed related
  work. `/src` = executable code + configs + environment, calibrated to contribution type. `/trace`
  = the exploration graph (research DAG). `/evidence` = raw machine-readable results and logs that
  ground claims.
- **Boundary conditions**: Evidence holds outputs only, enabling access control (withholding
  evidence from verification agents to prevent fabrication).
- **Related concepts**: ARA, Cross-layer forensic bindings, Proof chain.

## Exploration Graph (research DAG)
- **Notation**: `trace/exploration_tree.yaml`
- **Definition**: A nested-YAML directed acyclic graph recording the research process with five
  typed node kinds — **question, decision, experiment, dead_end, pivot** — where nesting encodes
  parent→child edges and `also_depends_on` encodes convergence. Described as "git log for research."
  `dead_end` nodes carry hypothesis + failure mode + lesson.
- **Boundary conditions**: Nodes declare `support_level: explicit` (grounded in source) or
  `inferred` (reconstructed).
- **Related concepts**: Storytelling Tax, Progressive crystallization.

## Cross-layer forensic bindings
- **Notation**: —
- **Definition**: Explicit, machine-traversable links connecting a claim to its experiment(s), the
  experiment to its evidence, and claims/heuristics to the code that implements them. Recovering
  this lineage from legacy sources is termed *forensic reconstruction* — "the core compilation
  problem."
- **Boundary conditions**: The structural layer that PDF + GitHub + tracker stacks lack.
- **Related concepts**: Proof chain, ARA Compiler.

## Progressive crystallization
- **Notation**: —
- **Definition**: The discipline by which raw observations are *staged* and only mature into typed
  formal entries (claims, heuristics, concepts) when a closure signal appears — topic abandonment,
  explicit affirmation, empirical resolution, or artifact commitment — never prematurely.
- **Boundary conditions**: Applied by the Live Research Manager at session boundaries; trace events
  are appended continuously while knowledge events are staged.
- **Related concepts**: Live Research Manager, Provenance tags.

## Live Research Manager
- **Notation**: —
- **Definition**: A natural-language agent *skill* that captures decisions and dead ends during
  ordinary development via a three-stage retrospective pipeline (Context Harvester → Event Router →
  Maturity Tracker), tagging every entry with provenance {user, ai-suggested, ai-executed,
  user-revised}.
- **Boundary conditions**: Silent, framework-independent; assumes an AI-native workflow.
- **Related concepts**: Progressive crystallization, ARA Compiler.

## ARA Compiler
- **Notation**: —
- **Definition**: A many-to-one agent skill that translates legacy inputs (PDF + repo + rubrics +
  trajectory logs) into a single ARA via four top-down stages — Semantic Deconstruction → Cognitive
  Mapping → Physical Grounding → Exploration Graph Extraction — with in-loop ARA Seal Level 1
  validation.
- **Boundary conditions**: Fidelity is bounded by the source; PDF-accessible information missing
  from the ARA is a compilation failure, but information absent from the PDF cannot be recovered.
- **Related concepts**: Forensic reconstruction, ARA Seal.

## ARA Seal (Levels 1–3) / Rigor Auditor
- **Notation**: L1 / L2 / L3
- **Definition**: A three-level machine-verifiable credential. **L1 Structural Integrity**
  (deterministic, seconds); **L2 Argumentative Rigor** (an LLM "Rigor Auditor" scores six
  dimensions 1–5 — evidence relevance, falsifiability quality, methodological rigor, scope
  calibration, argument coherence, exploration integrity); **L3 Execution Reproducibility**
  (sandboxed, evidence-isolated, scaled-down directional checks). Issues a Seal Certificate.
- **Boundary conditions**: L2 has an orphan-experiment blind spot; LLM-judge auditing shows grade
  inflation, motivating deterministic verdict computation.
- **Related concepts**: Three-stage review pipeline, Cross-layer forensic bindings.

## Sufficiency (capability-relative)
- **Notation**: —
- **Definition**: An ARA is *sufficient* if a sufficiently capable coding agent can reproduce the
  core claim zero-shot from the artifact alone. The criterion is relative to agent capability, so
  artifacts remain valid as agents advance.
- **Boundary conditions**: Defined against a coding-agent reproduction target.
- **Related concepts**: ARA, Engineering Tax.

## Structured claim & typed evidence (oshima)
- **Notation**: `Claim`, `Evidence` (Pydantic schemas, `src/execution/app/models/extract.py`)
- **Definition**: In the oshima implementation, an original authorial *claim* extracted from a paper
  (with confidence and centrality), and *evidence* linked to a claim and typed as
  support / contradict / contextual. The machine-usable instantiation of the ARA cognitive layer's
  claim↔evidence binding.
- **Boundary conditions**: Extracted via schema-constrained LLM output over section-aware chunks.
- **Related concepts**: Cross-layer forensic bindings, NL→FOL.

## NL→FOL representation (oshima)
- **Notation**: `fol_json`
- **Definition**: The conversion of natural-language statements into first-order-logic ASTs typed
  with SUMO ontology + WordNet senses, via a CoreNLP pipeline; stored as JSON to enable logical
  deduplication and machine reasoning over claims.
- **Boundary conditions**: Implemented as a multi-stage pipeline
  (`src/execution/app/services/nlp2fol/`).
- **Related concepts**: Structured claim, Cross-paper themes.

## Multi-omics shared embedding
- **Notation**: 128-dimensional node vectors
- **Definition**: A single vector space holding genes, proteins, enzymes, and small molecules
  together, where omics modalities are *directions* and proximity encodes interaction strength;
  learned Word2Vec-style from pathway sequences so that geometry stands in for biology.
- **Boundary conditions**: Trained on curated MetaCyc pathways; lacks an explicit structural/
  locational dimension; binary edges lose interaction strength.
- **Related concepts**: Context pair, Pathway sequence, Synthetic-node decoding.

## Context pair (positive / negative)
- **Notation**: target = 1 / 0
- **Definition**: Two pathway nodes co-occurring within a `context_window_size` form a positive pair
  (learning target 1); randomly drawn unrelated nodes form negative pairs (target 0). The training
  signal that aligns related vectors and separates unrelated ones (MSE on the dot product).
- **Boundary conditions**: Highly common intermediates (water, O2, CO2) are under-sampled.
- **Related concepts**: Multi-omics shared embedding, Pathway sequence.

## Synthetic-node decoding ("alien proteins")
- **Notation**: —
- **Definition**: The proposed use of an embedding space to generate a *synthetic ideal* point (an
  ideal protein/pathway that would explain a disease), then return the nearest real entities as
  candidates; when the nearest real neighbor is far, the point names something biology has not made
  yet — a plausible but non-existent "alien protein," buildable in principle. The synthetic point
  *decodes* back into human-readable hypotheses — the human-readable layer over an AI-first record.
- **Boundary conditions**: Conceptual proposal (Ostmann & Otte essay); the model also generates
  infeasible candidates, so outputs must be filtered and experimentally validated.
- **Related concepts**: Multi-omics shared embedding, Key Insight (G3).
