# Constraints, Assumptions & Limitations

## Boundary conditions
- **Domain scope (ARA)**: The ARA protocol is defined and evaluated for ML/computational research;
  the Physical Layer and Exploration Graph may not generalize to wet-lab or theoretical work, and
  all benchmarks are CS/ML (ARA paper §10).
- **Capability-relative sufficiency**: "Sufficient" is defined against a *sufficiently capable
  coding agent*. What is sufficient today may differ as agents improve (ARA paper §3); evaluation
  results are tied to specific base models (Sonnet 4.5 / 4.6).
- **Workflow assumption**: The Live Research Manager assumes an AI-native development workflow where
  decisions and runs pass through agent sessions.
- **oshima**: Captures the genuine application source; vendored deps, generated code, tests,
  playground/scripts, and two legacy/disabled job-handling generations were not transcribed (see
  `src/artifacts.md` and `evidence/README.md` skip notes). The repo contains theme embeddings but no
  semantic-search-over-embeddings endpoint was found in the captured routers.
- **Multi-omics**: Trained only on curated MetaCyc pathways; the embedding has no explicit
  structural/locational dimension; edges are binary (no interaction strength/confidence).

## Assumptions
- A1: Research increasingly runs through AI-native workflows (enables capture-as-you-go).
- A2: A sufficiently capable coding agent is the reproduction target (capability-relative sufficiency).
- A3: Curated pathway databases approximate real interaction networks well enough to learn a useful
  embedding.
- A4: Even an AI-first record needs a human-readable layer to be useful for human-led science.

## Known limitations & open problems
### From the ARA protocol (explicit)
- **Fidelity ceiling of the Compiler**: it cannot recover information absent from the source PDF;
  any PDF-accessible information missing from the ARA is a compilation failure, but missing-from-PDF
  detail is unrecoverable.
- **L2 orphan-experiment blind spot**: the Rigor Auditor detects only ~22% of orphan experiments →
  proposed fix is to move orphan detection into deterministic L1 (C08).
- **LLM-as-judge pathologies**: grade inflation (17 of 23 ARAs rounded up to clear Accept) and
  finding–score decoupling (22 of 23 critical flags did not lower the dimension score) → proposal:
  LLMs generate findings, verdict computed deterministically.
- **Trace can constrain a strong agent** (C07): preserved traces can box in a sufficiently capable
  agent → proposed mechanism: tag trace nodes with model-class provenance so successors can discount
  stale claims.
- **Result fabrication reduced, not eliminated** (C11): fabrication occurred in 2 baseline runs and
  1 ARA run; evidence isolation mitigates but does not remove it.
- **Aspirational / not-yet-implemented**: adversarial robustness, sandboxed execution, content
  anomaly detection, granular trace access control, and major-revision schema migration.
- **Extension harness fragility**: four engineering failure modes (SDK buffer crash, OOM mass-batch
  scoring, premature "session complete", scorer timeout) required fixes to sustain 8h runs
  (`ara_table13`).

### From the multi-omics case (explicit)
- **Missing structural/functional dimension**: sequence and 3-D structure information is only
  implicitly present in the pathway network — flagged future work.
- **Binary-edge information loss**: MetaCyc edges carry no interaction strength/confidence;
  lower-confidence and pathway-irrelevant interactions are lost.
- **Curation bias**: MetaCyc networks are curated, not direct experimental results — biased toward
  model organisms and well-understood disease networks.
- **Cross-tissue / cross-domain data scarcity**: annotated pathways thin out away from model
  organisms; a protein seen in one domain is unlikely to generalize its embedding to others.
- **Data-harmonization mismatch**: differential-expression data has a different interpretation
  (correlation ≠ chemical-reaction linkage); within a single omics type, cross-platform data often
  cannot be harmonized cleanly (Miao Guo, per "Alien Proteins" essay).
- **Unknown nodes / generative use**: embeddings for nodes absent from MetaCyc are proposed via
  summing one-hot encodings of known related nodes (method proposed, not validated); a general
  bijective atom/sequence→embedding mapping for generative ("alien protein") use is future work.
- **No quantitative benchmark**: validation is qualitative (t-SNE, enrichment, one case study);
  no accuracy metrics or baseline comparison are reported (inferred — no metrics table exists).

### Synthesis-level (project)
- The unifying thesis (G3 / Key Insight — an AI-first record needs a human-readable decoding layer)
  is a *position* argued from the author's essays and the multi-omics decoding idea, not an
  empirically tested claim; it is recorded in `problem.md`, not `claims.md`.
