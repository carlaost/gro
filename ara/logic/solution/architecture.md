# Architecture

The project's "solution" spans three coordinated artifacts: the **ARA protocol** (the
representation), the **oshima API** (a system that compiles papers into structured knowledge), and
the **multi-omics embedding** (a domain representation whose synthetic points decode into candidates).
Together they instantiate the Key Insight: a structured, machine-executable knowledge object with a
human-readable layer on top.

## 1. ARA protocol — the representation (Liu et al., 2026)
Diagram evidence: `ara_figure4` (directory structure), `ara_figure5` (cross-layer bindings of a real ARA).

- **Components (four layers + manifest)**:
  - **`/logic` (Cognitive Layer)** — `problem.md`, `solution/` (architecture / algorithm /
    heuristics), `claims.md` (falsifiable assertions with proof pointers), `experiments.md`
    (verification plans), `concepts.md`, `related_work.md` (typed dependencies).
  - **`/src` (Physical Layer)** — executable code calibrated to contribution type: *kernel mode*
    (core modules only, 1–2 orders of magnitude smaller than the full repo) for algorithmic work;
    *repository mode* (full implementation + `index.md` manifest) for systemic work; plus `configs/`
    (hyperparameters + rationale + search range) and `environment.md`.
  - **`/trace` (Exploration Graph)** — `exploration_tree.yaml`: a research DAG with five typed node
    kinds (question, decision, experiment, dead_end, pivot); nesting = edges; `also_depends_on` =
    convergence. "git log for research."
  - **`/evidence` (Evidence Layer)** — `results/` (machine-readable metric tables, exact values) and
    `logs/` (curves, resource usage). Outputs only, enabling access control (withhold evidence from
    verification agents to prevent fabrication).
  - **`PAPER.md` manifest** — YAML frontmatter + layer index for ~500-token triage / progressive
    disclosure.
- **Key design choice — cross-layer forensic bindings**: the proof chain `claims.md → experiments.md
  → /evidence/` plus claim/heuristic → code links is the structural layer that PDF + GitHub +
  tracker stacks lack (C09).
- **Supporting mechanisms (agent skills)**:
  - **Live Research Manager** (`ara_figure6`): session-boundary pipeline Context Harvester → Event
    Router → Maturity Tracker, with progressive crystallization and provenance tags.
  - **ARA Compiler** (`ara_figure7`): many-to-one legacy→ARA translation, four stages (Semantic
    Deconstruction → Cognitive Mapping → Physical Grounding → Exploration Graph Extraction) with
    in-loop L1 validation.
  - **ARA Seal / review** (`ara_figure8`, `ara_figure9`): L1 structural / L2 argumentative (Rigor
    Auditor) / L3 execution; a three-stage review pipeline (conceptual → empirical → human).
  - **(Human+AI)² network** (`ara_figure10`): a shared ARA commons with Git-like /submit, /retrieve,
    /fork.

> This very artifact is a compiled ARA, so its own structure is an instance of this architecture.

## 2. oshima API — paper → structured knowledge (implementation)
Captured source under `src/execution/app/`; deliverable described in `src/artifacts.md`.

- **Components**:
  - **REST layer** (`app/api/v1/endpoints/`): papers (upload/list/get), libraries + paper
    associations, themes, jobs (`jobs-new`), storage/artifacts; health/info in `app/main.py`.
  - **Service layer** (`app/services/`): ingestion (Adobe PDF Services → JSON), extraction
    (`extract_paper.py`, DSPy claims extractor), NL→FOL (`nlp2fol/`), themes (`theme_service.py`),
    jobs (`job_service.py`).
  - **Worker pool** (`app/workers/worker_manager.py`): a `ThreadPoolExecutor` that atomically claims
    queued `extraction_runs` and runs each paper through the pipeline (claim TTL, retries,
    rate-limited LLM calls).
  - **Persistence** (`app/db/`, Supabase): Postgres + JWT/RLS auth + object storage + RPC; schemas
    in `app/models/extract.py`, `app/models/db_models.py`.
- **Pipeline** (`app/services/pipeline/storage_pipeline.py`): **Ingest → Extract (claims/evidence)
  → Attribution → NLP2FOL → Deduplication → Consolidation**, persisting claims, typed evidence
  links, FOL JSON, and library themes.
- **Mapping to ARA**: the structured claim + typed evidence (support/contradict/contextual)
  instantiate the cognitive layer's claim↔evidence binding (C10); `fol_json` adds a reasoning-ready
  representation (C11); cross-paper themes move toward a compounding commons (C12).
- **Key design choices (explicit in code/README)**: SHA256-idempotent upload; DB-based atomic job
  claiming (DB-only `JobService` replaced an earlier file-based `JobManager`); schema-constrained LLM
  output via DSPy/Pydantic; section-aware chunking for long papers. (Note: the original `jobs` router
  is disabled — "upload endpoint is broken" — and `jobs-new` is used instead.)

## 3. Multi-omics embedding — a domain representation (Otte et al., 2025)
Diagram/result evidence: `mo_figure1` (pathway network), `mo_figure2` (model), `mo_figure3`
(objective), `mo_figure4` (results).

- **Components**:
  - **Corpus builder**: download every MetaCyc pathway diagram → CSV of substrates/products/genes;
    infer gene→protein translation and enzyme→reaction roles; build interaction chains by random
    walk up to `sequence_length`; split into `context_window_size` windows; draw positive
    (co-context) and negative (random) node pairs; under-sample hub intermediates (water, O2, CO2).
  - **Embedding network** (`mo_figure2`): two separate `Linear(vocab_size, embed_dim)` layers
    (target, context) with tanh; `forward` returns the dot product of tanh(target) and tanh(context).
    Node embedding = tanh(target_embedding(node)); embedding dimension = 128.
  - **Objective** (`mo_figure3`): MSE between the dot-product prediction and the learning target
    (1 for positive pairs, 0 for negative), aligning related vectors and separating unrelated ones.
  - **Analysis**: t-SNE to 2-D, clustering, pathway enrichment, nearest-neighbor inspection,
    dot-product distribution.
- **Mapping to the project thesis**: geometry stands in for biology (C13–C15); the proposed
  *synthetic-node decoding* ("alien proteins") is exactly the human-readable layer over an AI-first
  record (G3 / Key Insight) — generate a synthetic ideal point, return nearest real candidates, and
  decode the point into a hypothesis a scientist can act on.

## Inputs / outputs across the three
| Artifact | Input | Output |
|----------|-------|--------|
| ARA protocol | a research work (logic, code, runs, results) | a four-layer agent-executable artifact |
| oshima API | paper PDFs | structured claims + typed evidence + FOL + cross-paper themes |
| Multi-omics embedding | MetaCyc pathways | a shared 128-D space; candidate pathways/proteins on decoding |
