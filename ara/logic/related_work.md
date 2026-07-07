# Related Work

Typed dependency graph for the project. Works with a specific technical delta get full `RW` blocks;
the broader citation footprint of the two papers is preserved more briefly at the end.

## RW01: Starace et al., 2025 — PaperBench
- **DOI**: arXiv (PaperBench)
- **Type**: imports / baseline
- **Delta**:
  - What changed: ARA consumes PaperBench's 8,921 expert reproduction-rubric requirements (23
    ICML-2024 papers) as expert-verified claim decompositions and as the reproduction test bed.
  - Why: provides ground-truth specification requirements and difficulty-stratified tasks.
- **Claims affected**: C03, C04
- **Adopted elements**: rubric requirements; paper corpus.

## RW02: Wijk et al., 2025 — RE-Bench / METR MALT
- **DOI**: METR RE-Bench
- **Type**: imports / baseline
- **Delta**:
  - What changed: ARA ingests 24,008 agent runs / 46,303 failure episodes (MALT trajectories) as
    `trace/` dead-end nodes; RE-Bench's five open-ended tasks are the extension test bed.
  - Why: supplies real failure-trace corpora and extension tasks.
- **Claims affected**: C05, C06, C07
- **Adopted elements**: run trajectories; extension tasks.

## RW03: Wilkinson et al., 2016 — FAIR principles
- **DOI**: 10.1038/sdata.2016.18
- **Type**: bounds / extends
- **Delta**:
  - What changed: FAIR standardizes data findability/accessibility/interoperability/reuse but says
    nothing about the structure of research arguments; ARA adds epistemic + execution structure.
  - Why: positions ARA as complementary structural layer, not a metadata schema.
- **Claims affected**: C09
- **Adopted elements**: the reuse/interoperability goal.

## RW04: Mikolov et al., 2013 — Word2Vec
- **DOI**: NeurIPS 2013 (Distributed representations of words and phrases)
- **Type**: imports
- **Delta**:
  - What changed: the multi-omics model directly adapts the Word2Vec architecture/objective from NLP
    word vectors to pathway nodes ("based on the Word2Vec architecture").
  - Why: vector arithmetic / directional semantics motivate omics-as-directions.
- **Claims affected**: C13, C14
- **Adopted elements**: two-tower target/context embedding; analogy of directional relations.

## RW05: Caspi / Altman et al., 2014 — MetaCyc
- **DOI**: 10.1093/nar/gkt1103 (Nucleic Acids Research 42(D1):D459–D471)
- **Type**: imports (data source)
- **Delta**:
  - What changed: MetaCyc's curated pathway/reaction networks are the training corpus; substrates,
    products, and genes are extracted from every pathway diagram.
  - Why: provides the multi-omics relational data.
- **Claims affected**: C13, C15
- **Adopted elements**: pathway/reaction networks.

## RW06: Raman & Chandra, 2009 — Flux Balance Analysis
- **DOI**: 10.1093/bib/bbp011 (Briefings in Bioinformatics 10(4):435–449)
- **Type**: bounds (motivation)
- **Delta**:
  - What changed: FBA needs detailed multi-omics pathway knowledge to optimize flux — the gap the
    embedding aims to fill.
  - Why: motivates a learned multi-omics representation.
- **Claims affected**: C13
- **Adopted elements**: pathway-optimization use case.

## RW07: Single-modality molecular fingerprints (ECFP/Morgan; MACCS Keys; SMILES Transformer)
- **DOI**: ECFP (Rogers & Hahn 2010 / Morgan); MACCS (Durant et al. 2002, 10.1021/ci010132r);
  SMILES Transformer (Honda et al. 2019, arXiv:1911.04738)
- **Type**: bounds / contrast
- **Delta**:
  - What changed: prior fingerprints are structure-based, functional-group-based, or single-molecule
    learned — all single-modality; the paper proposes a fingerprint encapsulating multi-omics layers.
  - Why: contrast establishes the multi-omics contribution.
- **Claims affected**: C13
- **Adopted elements**: the "fingerprint" framing.

## RW08: Agent-oriented standards — AGENTS.md; Agent Skills; Claude Code/Agent SDK
- **DOI**: OpenAI 2025 (AGENTS.md); Anthropic 2025a (Agent Skills); Anthropic 2025b (Claude Code SDK)
- **Type**: imports
- **Delta**:
  - What changed: ARA's Live Manager, Compiler, and Rigor Auditor are implemented as natural-language
    *skills* on the Claude Agent SDK; the oshima implementation also uses Anthropic/DSPy and OpenAI.
  - Why: lets the tooling improve with the base model and need no custom infra.
- **Claims affected**: C08, C10, C11
- **Adopted elements**: skill format; agent SDK.

## RW09: Experiment trackers — MLflow; Weights & Biases
- **DOI**: Zaharia et al. 2018 (MLflow); Biewald 2020 (W&B)
- **Type**: baseline
- **Delta**:
  - What changed: trackers record runs but leave knowledge siloed and unlinked across layers.
  - Why: Table 5 comparison baseline for cross-layer coverage.
- **Claims affected**: C09
- **Adopted elements**: run/metric logging concept.

## RW10: Post-hoc tacit-knowledge & discrepancy studies (Li et al. 2026; Baumgärtner & Gurevych 2026; Kon 2025 — EXP-Bench)
- **DOI**: Li et al. 2026 ("What papers don't tell you"); SciCoQA 2026; EXP-Bench 2025
- **Type**: refutes-status-quo / bounds
- **Delta**:
  - What changed: prior work recovers tacit knowledge *after* publication (up to 10.9% PaperBench
    gains) and finds LLMs detect <46% of paper–code discrepancies and ~0.5% end-to-end experiment
    success; ARA instead encodes the knowledge at authoring time.
  - Why: motivates capture-at-source over post-hoc reconstruction.
- **Claims affected**: C01, C04
- **Adopted elements**: the information-gap framing.

## Briefer citation footprint
- **Structured-science precursors** (each formalizes a fragment; ARA unifies execution + decision
  history): Nanopublications (Groth 2010); RO-Crate (Soiland-Reyes 2022); ORKG (Jaradeh 2019); Whole
  Tale (Brinckman 2019); Discovery Engine (Baulin 2025); PROV-O (Lebo 2013).
- **Reproducibility / tacit knowledge / publication bias** (background for `problem.md`): Medawar
  1963; Kuhn 1962; Polanyi 1966; Franco 2014; Rosenthal 1979; Baker 2016; Stodden 2016; Pineau 2021.
- **Workflow engines / notebooks**: Snakemake (Köster 2012); Nextflow (Di Tommaso 2017); CWL
  (Crusoe 2022); Literate Programming (Knuth 1984); Rule et al. 2018.
- **Failure traces / autonomous research agents**: Zhu 2025; Zhang 2025; Yang 2024; Lu 2024 (AI
  Scientist); Boiko 2023; Schmidgall 2025; Baek 2025.
- **LLM-as-judge pathologies**: Zheng et al. 2023 (motivates deterministic verdict computation, C09).
- **Multi-omics integration & pathway prediction** (background for the domain case): Lopez-Ibáñez
  et al. 2021 (BMC Bioinformatics 22(1):320); Liao/Ozcan et al. 2023 (Open moa, Bioinformatics
  39(11)); Singh/van der Hooft et al. 2022; Subramanian/Verma et al. 2020; Muller/Shiryan/Borenstein
  2024 (Nature Comm.); Hussain/Mohsin et al. 2022.
- **Author's own essays** (problem framing, not external citations): Ostmann, "Papers Block
  Scientific Progress" (2026); Ostmann & Otte, "Alien Proteins" (2026).
