# Experiments

Declarative verification plans. Directional only — exact numbers live in `evidence/`. Experiments
E01–E06 are the ARA paper's evaluations; E07–E09 verify the oshima implementation by inspection/
execution; E10–E11 are the multi-omics paper's analyses.

## E01: Agent understanding via paired QA
- **Verifies**: C01, C02
- **Setup**:
  - Model: a fresh Claude Sonnet 4.6 sub-agent per question; grading by Claude Opus 4.6
  - Dataset: 450 questions (15 questions × 30 targets) in 3 categories — A (fidelity), B (detail),
    C (failure/dead-end knowledge)
  - System: each work presented twice — as ARA, and as PDF+repo baseline (paired)
- **Procedure**:
  1. For each target and each presentation, answer the same questions in isolation.
  2. Grade each answer 1.0 / 0.5 / 0.0 against a reference.
  3. Compare ARA vs baseline overall and per category.
- **Metrics**: QA accuracy (fraction correct); token usage.
- **Expected outcome**: ARA > baseline overall; the gap is largest for Category C (failure) questions.
- **Baselines**: PDF + repository.
- **Dependencies**: none

## E02: Reproduction success, stratified by difficulty
- **Verifies**: C03
- **Setup**:
  - Model: both agents Claude Sonnet 4.6 (14–20M token budgets); blinded Opus 4.6 judge
  - Dataset: 15 PaperBench papers → 150 tasks / 1,743 rubric requirements, difficulty-stratified
  - System: expected results masked from the reproduction agent
- **Procedure**:
  1. Reproduce each paper from ARA vs from PDF+repo.
  2. Score rubric requirements; weight success by difficulty (easy:medium:hard = 1:2:3).
  3. Compare weighted success and the per-difficulty gap.
- **Metrics**: difficulty-weighted reproduction success; per-difficulty success.
- **Expected outcome**: ARA > baseline; the advantage grows from easy to hard.
- **Baselines**: PDF + repository.
- **Dependencies**: E03

## E03: Information-gap quantification of published artifacts
- **Verifies**: C04, C05
- **Setup**:
  - Dataset: 8,921 PaperBench reproduction requirements (23 papers); 24,008 RE-Bench runs
  - System: classify each requirement's specification status; analyze run outcomes vs cost
- **Procedure**:
  1. Classify each reproduction requirement as fully / partially / un-specified; tabulate gap types.
  2. Partition agent runs into above/below-reference; attribute token and dollar cost to each.
  3. Compute the failed-to-success cost ratio.
- **Metrics**: fraction fully specified; gap-type distribution; share of cost in failed runs.
- **Expected outcome**: a minority of requirements are fully specified; the majority of dollar cost
  is in failed runs.
- **Baselines**: none (descriptive analysis).
- **Dependencies**: none

## E04: Open-ended extension on RE-Bench
- **Verifies**: C06, C07
- **Setup**:
  - Model: Claude Agent SDK agents on two base models (Sonnet 4.6 and Sonnet 4.5); 8h SLURM, $50 cap
  - Dataset: 5 RE-Bench open-ended extension tasks (beat-reference by editing `solution.py`)
  - System: ARA agent given preserved MALT failure traces vs paper-only agent; beat-reference fairness filter
- **Procedure**:
  1. Run both agents on each task; log score over wall-clock time.
  2. Record time-to-first-useful-move and final score per task and per base model.
  3. Compare across base-model capability.
- **Metrics**: time to first useful move; task score trajectory; final score.
- **Expected outcome**: with the weaker base model, preserved traces speed the first useful move and
  help final score; with a stronger base model, the trace can constrain and the ordering can invert.
- **Baselines**: paper-only agent.
- **Dependencies**: none

## E05: Rigor-Auditor mutation benchmark (L2 review)
- **Verifies**: C08
- **Setup**:
  - Dataset: 23 ARAs × 5 injection types, each ARA its own oracle
  - System: the L2 Rigor Auditor scores six dimensions; injections include fabricated results,
    rebutted-branch leak, over-claim, missing-falsification, and orphan experiment
- **Procedure**:
  1. Inject one controlled flaw at a time into each ARA.
  2. Run the auditor; record whether it flags the injected flaw.
  3. Compute detection rate per injection type and overall.
- **Metrics**: per-injection-type detection rate; overall detection rate.
- **Expected outcome**: near-complete detection of high-severity injections; low detection of orphan
  experiments.
- **Baselines**: none.
- **Dependencies**: none

## E06: Dimensional coverage comparison of representation tools
- **Verifies**: C09
- **Setup**:
  - System: five agent-native dimensions (incl. cross-layer bindings) evaluated for PDF, GitHub,
    experiment trackers, and ARA
- **Procedure**:
  1. For each tool, assess coverage of each dimension (present / partial / absent).
  2. Tabulate and compare.
- **Metrics**: dimensions covered per tool.
- **Expected outcome**: existing tools cover at most two dimensions; ARA covers all five.
- **Baselines**: PDF, GitHub, experiment trackers.
- **Dependencies**: none

## E07: oshima ingestion + structured claim/evidence extraction (system verification)
- **Verifies**: C10
- **Setup**:
  - System: the oshima FastAPI service (`src/execution/app/`), Supabase backend, DSPy/OpenAI/Anthropic extractors
  - Data: a paper PDF uploaded via the papers endpoint
- **Procedure**:
  1. Upload a PDF; confirm an `extraction_run` is enqueued and processed.
  2. Inspect the produced records for claims (with confidence/centrality) and evidence typed
     support/contradict/contextual against the `extract.py` schema.
  3. Confirm section-aware chunking on a long paper.
- **Metrics**: presence and schema-validity of extracted claims and typed evidence.
- **Expected outcome**: ingested papers yield schema-valid structured claims and typed evidence.
- **Baselines**: none.
- **Dependencies**: none

## E08: oshima NL→FOL conversion (system verification)
- **Verifies**: C11
- **Setup**:
  - System: the NL2FOL pipeline (`app/services/nlp2fol/`), CoreNLP + SUMO/WordNet
- **Procedure**:
  1. Pass extracted statements through the pipeline.
  2. Inspect the stored `fol_json` for typed first-order-logic structure.
  3. Confirm logical deduplication consumes the FOL representation.
- **Metrics**: presence/well-formedness of FOL output for extracted statements.
- **Expected outcome**: statements are stored as typed FOL representations usable for deduplication.
- **Baselines**: none.
- **Dependencies**: E07

## E09: oshima cross-paper theme synthesis (system verification)
- **Verifies**: C12
- **Setup**:
  - System: the theme service (`app/services/themes/theme_service.py`) over a library of papers
- **Procedure**:
  1. Associate multiple papers with a library.
  2. Run theme synthesis (full and incremental).
  3. Inspect resulting themes for aggregation across papers' claims.
- **Metrics**: presence of cross-paper themes spanning >1 paper.
- **Expected outcome**: themes aggregate claims across the library.
- **Baselines**: none.
- **Dependencies**: E07

## E10: Multi-omics embedding clustering analysis
- **Verifies**: C13
- **Setup**:
  - Model: Word2Vec-style two-tower network; 128-dim embeddings
  - Dataset: MetaCyc pathways → sampled interaction chains → positive/negative context pairs
- **Procedure**:
  1. Train embeddings; reduce to 2-D via t-SNE.
  2. Cluster; recolor the same projection by omics modality.
  3. Run pathway enrichment per cluster.
- **Metrics**: cluster separability; modality intermixing; per-cluster functional coherence.
- **Expected outcome**: distinct clusters with intermixed modalities; clusters share functional
  characteristics.
- **Baselines**: none reported (qualitative).
- **Dependencies**: none

## E11: Multi-omics relatedness validation (dot-product + nearest neighbor)
- **Verifies**: C14, C15
- **Setup**:
  - Model: the trained 128-dim embeddings
- **Procedure**:
  1. Compute pairwise dot products across all embeddings; inspect the distribution.
  2. For a query node, retrieve the most-similar embedding; check the relation against MetaCyc.
- **Metrics**: shape of the dot-product distribution; biochemical validity of nearest neighbors.
- **Expected outcome**: a bimodal dot-product distribution; nearest neighbors are documented
  metabolic relations.
- **Baselines**: none reported (qualitative / single case study).
- **Dependencies**: E10
