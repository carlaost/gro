# Claims

Falsifiable assertions for the *desciencemodel* project, drawn from four sources. Claims are tagged
by source: `[ara-paper]` (Liu et al., 2026), `[oshima]` (the implementation, grounded in
`src/execution/`), `[multi-omics]` (Otte et al., 2025). Carla Ostmann's higher-order thesis is
stated as the Key Insight in `problem.md` and is not repeated here as a single falsifiable claim.

Numbers are copied exactly from source; each load-bearing number carries a `**Sources**` quote.

---

## C01: ARA improves agent understanding (QA accuracy)
- **Statement**: Providing a work as an ARA instead of a PDF+repo raises a coding agent's
  question-answering accuracy on that work (93.7% vs 72.4%, +21.3% over 450 paired outcomes).
- **Sources**: [93.7% / 72.4% / +21.3% / 450 ← ARA paper Abstract & §7.2/Table 3 «overall accuracy 93.7% vs. 72.4% (+21.3%) on 450 paired outcomes»]
- **Status**: supported
- **Falsification criteria**: On the same paired QA protocol, ARA accuracy ≤ PDF+repo accuracy.
- **Proof**: [E01]
- **Evidence basis**: `ara_table3` reports per-category and overall QA accuracy with token usage.
- **Interpretation**: The structural layers (esp. exploration + evidence) carry information a PDF omits.
- **Dependencies**: —
- **Tags**: ara-paper, understanding, evaluation

## C02: ARA's understanding gains are largest on failure-knowledge questions
- **Statement**: The ARA advantage is concentrated in questions about failures/dead ends
  (Category C), where ARA wins by +65.7%.
- **Sources**: [+65.7% ← ARA paper §7.2/Table 3 «ARA wins +65.7%»]
- **Status**: supported
- **Falsification criteria**: The Category-C (failure) accuracy gap is ≤ the Category-A/B gaps.
- **Proof**: [E01]
- **Evidence basis**: `ara_table3` (category A fidelity / B detail / C failure).
- **Interpretation**: Confirms the exploration graph is the load-bearing layer for process knowledge.
- **Dependencies**: C01
- **Tags**: ara-paper, exploration-graph, understanding

## C03: ARA improves reproduction, and the advantage widens with difficulty
- **Statement**: ARA raises difficulty-weighted reproduction success (64.4% vs 57.4%), with the gap
  growing from easy to hard tasks.
- **Sources**: [64.4% / 57.4% ← ARA paper Abstract & §7.3 «difficulty-weighted success rate of 64.4% vs. 57.4%»]; [+4.9% easy / +5.6% medium / +8.5% hard ← ARA paper Fig 11 (`ara_figure11`)]
- **Status**: supported
- **Falsification criteria**: ARA ≤ baseline weighted success, or the per-difficulty gap is not
  monotonically increasing.
- **Proof**: [E02]
- **Evidence basis**: `ara_table11` (per-paper success by difficulty), `ara_figure11`, `ara_figure13`.
- **Interpretation**: Harder reproductions depend more on the unstated detail ARA preserves.
- **Dependencies**: C04
- **Tags**: ara-paper, reproduction, evaluation

## C04: Published artifacts systematically under-specify reproduction
- **Statement**: Only 45.4% of reproduction-critical requirements are fully specified in published
  artifacts, with missing hyperparameters the largest single gap type at 26.2%.
- **Sources**: [45.4% ← ARA paper §7.1/Table 8 «only 45.4% are fully specified»]; [26.2% ← ARA paper Table 9 (`ara_table9`)]
- **Status**: supported
- **Falsification criteria**: >50% of reproduction requirements are fully specified in the source artifact.
- **Proof**: [E03]
- **Evidence basis**: `ara_table8` (gap by category), `ara_table9` (gap-type distribution), `ara_figure3`.
- **Interpretation**: Motivates the Physical Layer's full-specification requirement (the Engineering Tax).
- **Dependencies**: —
- **Tags**: ara-paper, engineering-tax, information-gap

## C05: Most agent exploration compute is failed work that compilation discards
- **Statement**: Below-reference (failed) runs account for 90.2% of total dollar cost (and 59.2% of
  tokens), and the median failed-to-success token ratio is 113×.
- **Sources**: [90.2% / 59.2% ← ARA paper §7.4/Table 10 «failed runs account for 90.2% of total dollar cost (and 59.2% of tokens)»]; [113× ← ARA paper §1/Table 10 (`ara_table10`)]
- **Status**: supported
- **Falsification criteria**: Failed runs are a minority of total exploration cost.
- **Proof**: [E03]
- **Evidence basis**: `ara_table10` (below-reference exploration cost).
- **Interpretation**: The discarded failures are the most expensive knowledge — the Storytelling Tax quantified.
- **Dependencies**: —
- **Tags**: ara-paper, storytelling-tax, exploration

## C06: Preserved failure traces accelerate the first useful extension move
- **Statement**: An agent given the prior run's preserved failure trace reaches its first useful
  extension move much sooner than a paper-only agent (e.g. rust_codecontests: first commit at
  t≈9 min vs t≈395 min; triton: score 0.47 at t≈11 min vs first score at t≈37 min).
- **Sources**: [9 min / 395 min ← ARA paper §7.4 «rust_codecontests ARA commits at t=9 min vs paper at t=395 min»]; [0.47 / 11 min / 37 min ← ARA paper §7.4 «triton ARA scores 0.47 at t=11 min vs paper first score at t=37 min»]
- **Status**: supported
- **Falsification criteria**: The ARA (trace-equipped) agent is not faster to its first useful move
  than the paper-only agent across the extension tasks.
- **Proof**: [E04]
- **Evidence basis**: `ara_figure12` (extension trajectories ×5), `ara_table12` (task card).
- **Interpretation**: Trace preservation transfers "where not to dig," saving rediscovery cost.
- **Dependencies**: C05
- **Tags**: ara-paper, extension, exploration-graph

## C07: Trace value is capability-relative and can constrain a stronger agent
- **Statement**: The benefit of a preserved trace depends on the gap between the trace's capability
  and the agent's; a sufficiently capable agent can be constrained by the prior-run box (on Sonnet
  4.5 the result inverts: ARA 0.27 vs paper 0.64 on triton; ARA 0.73 vs paper 1.03 on restricted_mlm).
- **Sources**: [0.27 / 0.64 ← ARA paper §7.4/Fig 14 (`ara_figure14`) «ARA 0.27 vs paper 0.64 on triton»]; [0.73 / 1.03 ← ARA paper §7.4/Fig 15 (`ara_figure15`) «0.73 vs 1.03 on restricted_mlm»]
- **Status**: supported
- **Falsification criteria**: ARA ≥ paper agent on every extension task regardless of base model capability.
- **Proof**: [E04]
- **Evidence basis**: `ara_figure14`, `ara_figure15` (Sonnet 4.5 extension trajectories).
- **Interpretation**: Argues for tagging trace nodes with model-class provenance so successors can discount stale claims.
- **Dependencies**: C06
- **Tags**: ara-paper, extension, limitation

## C08: The L2 Rigor Auditor catches high-severity injections but has an orphan-experiment blind spot
- **Statement**: On a mutation benchmark the L2 auditor detects high-severity injections well
  (100% fabricated / rebutted-leak / over-claim; 91% missing-falsification) but only 22% of orphan
  experiments, for 82.6% overall.
- **Sources**: [100% / 91% / 22% / 82.6% ← ARA paper §7.5/Table 4 (`ara_table4`) «100% fabricated/rebutted-leak/over-claim; 91% missing-falsification; 22% orphan; 82.6% overall»]
- **Status**: supported
- **Falsification criteria**: The auditor achieves high recall on orphan experiments, or misses
  high-severity injection classes.
- **Proof**: [E05]
- **Evidence basis**: `ara_table4` (detection rates by injection type), `ara_table14` (per-paper × per-injection).
- **Interpretation**: Orphan detection is structural and should move into deterministic L1.
- **Dependencies**: —
- **Tags**: ara-paper, review-system, ara-seal

## C09: ARA covers all five agent-native dimensions; existing tools cover at most two
- **Statement**: Across five agent-native dimensions (incl. cross-layer bindings), PDF, GitHub, and
  experiment trackers are each partial or absent, while ARA covers all five.
- **Sources**: [≤2 of 5 / all 5 ← ARA paper §8/Table 5 (`ara_table5`) — dimensional coverage comparison]
- **Status**: supported
- **Falsification criteria**: A single existing tool covers all five dimensions including cross-layer bindings.
- **Proof**: [E06]
- **Evidence basis**: `ara_table5` (dimensional coverage PDF/GitHub/Tracker/ARA).
- **Interpretation**: The differentiator is the cross-layer forensic binding, not any single layer.
- **Dependencies**: —
- **Tags**: ara-paper, comparison, related-work

## C10: The oshima API ingests papers and extracts structured claims with typed evidence
- **Statement**: The oshima implementation ingests paper PDFs and produces machine-structured
  *claims* (with confidence and centrality) and *evidence* typed as support / contradict /
  contextual, via schema-constrained LLM extraction with section-aware chunking.
- **Sources**: [support/contradict/contextual ← `src/execution/app/models/extract.py` (Pydantic `Evidence` schema with typed relation); claim+evidence extraction ← `src/execution/app/services/extract/extract_paper.py` («PaperExtractor.extract_both», chunked claim+evidence extraction)]
- **Status**: supported
- **Falsification criteria**: The captured code does not define typed evidence relations or does not
  extract claims from ingested papers.
- **Proof**: [E07]
- **Evidence basis**: Source files `app/models/extract.py`, `app/services/extract/extract_paper.py`,
  `app/services/ingest/ingest_pdf.py`, `app/api/v1/endpoints/papers.py`.
- **Interpretation**: A working instantiation of the ARA cognitive layer's claim↔evidence binding.
- **Dependencies**: —
- **Tags**: oshima, implementation, claims-evidence

## C11: The oshima API converts extracted statements into first-order logic
- **Statement**: Extracted natural-language statements are converted into first-order-logic
  representations (SUMO + WordNet typed ASTs) and stored as `fol_json`, enabling logical
  deduplication and machine reasoning.
- **Sources**: [SUMO/WordNet FOL, `fol_json` ← `src/execution/app/services/nlp2fol/complete_pipeline_processor.py` & `logic_mapper.py` (CompletePipelineProcessor.process_claims_and_evidence, NL→FOL mapping)]
- **Status**: supported
- **Falsification criteria**: The captured NL2FOL pipeline does not produce/store an FOL
  representation of extracted statements.
- **Proof**: [E08]
- **Evidence basis**: `app/services/nlp2fol/complete_pipeline_processor.py`, `app/services/nlp2fol/logic_mapper.py`.
- **Interpretation**: Moves beyond text toward a reasoning-ready representation of claims.
- **Dependencies**: C10
- **Tags**: oshima, implementation, formal-logic

## C12: The oshima API synthesizes cross-paper themes over a library
- **Statement**: Papers are organized into libraries and the system synthesizes cross-paper *themes*
  over all library claims (full and incremental modes).
- **Sources**: [cross-paper themes ← `src/execution/app/services/themes/theme_service.py` (ThemeService over library claims); library endpoints ← `src/execution/app/api/v1/endpoints/library_papers.py`]
- **Status**: supported
- **Falsification criteria**: The captured theme service does not aggregate claims across multiple
  papers in a library.
- **Proof**: [E09]
- **Evidence basis**: `app/services/themes/theme_service.py`, `app/api/v1/endpoints/themes.py`.
- **Interpretation**: A step toward a compounding knowledge commons over many works.
- **Dependencies**: C10
- **Tags**: oshima, implementation, synthesis

## C13: A Word2Vec-style shared embedding co-locates omics modalities and forms biochemically meaningful clusters
- **Statement**: Training a two-tower (target/context) network on MetaCyc pathway sequences yields a
  128-dimensional shared space in which different omics modalities are intermixed (not segregated)
  and form distinct clusters whose members share functional characteristics (e.g. a cluster of
  pyrimidine nucleotide biosynthesis nodes).
- **Sources**: [128 ← Otte et al. §"Results" «128-dimensional vectors for every node»]; [well distributed ← Otte et al. p.2319 «different pathway modalities are well distributed in the space despite genes being less abundant in the left half»]; [distinct islands ← Otte et al. p.2319 «In the space we find distinct islands which according to our objective we expect to represent interacting/ related pathway nodes»]
- **Status**: supported
- **Falsification criteria**: t-SNE shows modality-segregated regions, or a single undifferentiated
  blob with no functionally coherent clusters.
- **Status note**: Qualitative validation (t-SNE + enrichment), no quantitative benchmark reported.
- **Proof**: [E10]
- **Evidence basis**: `mo_figure4` (a: t-SNE clusters; b: by omics type, intermixed), `mo_figure1`.
- **Interpretation**: Geometry can stand in for cross-omics biology — the representation hypothesis for the domain.
- **Dependencies**: —
- **Tags**: multi-omics, embedding, representation

## C14: Pairwise embedding dot-products are bimodal, separating related from unrelated nodes
- **Statement**: The distribution of dot products across all embeddings is a mixture of two
  distributions — a broad, lower peak for related nodes and a sharp, narrow peak for unrelated nodes.
- **Sources**: [mixture of two distribution ← Otte et al. p.2319 «The overall distribution of dot products between all embeddings (Fig. 4d) follows the shape of a mixture of two distribution. One distribution belonging to related nodes with a smaller but wider peak and the other distribution of unrelated nodes with a sharp narrow peak»]
- **Status**: supported
- **Falsification criteria**: The dot-product distribution is unimodal (no separable related-pair shoulder).
- **Proof**: [E11]
- **Evidence basis**: `mo_figure4` (panel d, dot-product distribution).
- **Interpretation**: The learned geometry encodes a usable relatedness signal.
- **Dependencies**: C13
- **Tags**: multi-omics, embedding, validation

## C15: Embedding proximity recovers known cross-omics biochemical relationships
- **Statement**: Nearest neighbors in the space correspond to documented metabolic relations — e.g.
  UDP-alpha-D-galactose's neighbor encodes phosphoglucomutase-1 (PGM1), consistent with MetaCyc.
- **Sources**: [UDP-alpha-D-galactose / PGM1 ← Otte et al. p.2318 «we take UDP-alpha-D-galactose and its related node in the embedding space which encodes phosphoglucomutase-1 (PGM1)… MetaCyc indeed states UDP-alpha-D-galactose as an intermediate in carbohydrate metabolism, and its relation to phosphoglucomutase-1 (PGM1) lies in its role in glucose and galactose metabolism»]
- **Status**: supported
- **Falsification criteria**: Nearest neighbors of a node have no documented metabolic relation in
  MetaCyc (beyond the single reported case study).
- **Status note**: Single worked example plus "similar results for other pairs"; no systematic recall reported.
- **Proof**: [E11]
- **Evidence basis**: `mo_figure4` (panel c) + §"Results" case study.
- **Interpretation**: Supports the synthetic-node-decoding vision (nearest real neighbors as candidates).
- **Dependencies**: C13
- **Tags**: multi-omics, embedding, case-study

## C16: The compiler critique — metrics measure the paper only on extractive layers; homogenization and fabrication layers are invalid as paper signals
<!-- CONFLICT: see trace N47 — cycle-1 [sem] judges found extractive-layer INFIDELITY (jes26 C09 polarity inversion, the25 added certainty qualifiers, huu25 ungrounded MAPT), challenging the "extractive = faithful re-view" premise. Awaiting Carla's adjudication: keep C16 as-is / narrow it to "extractive is faithful ONLY where per-ARA fidelity is verified" / withdraw. Do not silently resolve. -->
- **Statement**: An ARA metric equals a metric on the underlying paper only where it reads an
  *extractive* layer (claims, numbers, evidence tables — a faithful re-view). It does not on the other
  two layer classes: (a) *homogenization* — presence-proxy fields the compiler fills for every paper
  from a fixed template (falsifiability-field-exists, links-resolve) measure field-population, not the
  paper's rigor, so they cannot rank papers even under a perfect compiler; (b) *fabrication* — where the
  ARA schema demands a layer the source lacks (an exploration trace / dead-ends for a review or
  meta-analysis), the compiler invents content, so the metric measures the compiler's writing, not the
  paper. Concretely on the wave-1/2 corpus: `refutes = 0` corpus-wide (corrective score runs on
  baseline-relabeling), che26 `dead_end_density = 0.25` comes entirely from fabricated nodes N11/N12
  ("p-tau181 would remain competitive"), and woj25 C04 (a real null, AUC 0.514) is filed `status:
  supported` so the negative-result metric scores it zero. Corollary (survives a perfect compiler):
  compiler-fidelity and metric-validity are independent axes — a faithful re-view adds no external
  ground truth, so validity still requires an outside yardstick.
- **Sources**: [refutes = 0 ← research/metrics/v2/critiques-round2.md:51 «lib-wide RW types = 34 imports / 14 bounds / 11 extends / 9 baseline / **0 refutes**» [result]]; [che26 dead_end_density = 0.25 ← research/metrics/v2/critiques-round2.md:39 «che26 (meta_analysis) dead_end_density=0.25, negative_result_share=0.2, both entirely from compiler-invented nodes N11/N12» [result]]; [woj25 C04 AUC 0.514 ← research/metrics/v2/critiques-round2.md:63 «woj25 C04 — "plasma p-tau181&231 fails to differentiate, Cohen's d<0.2, AUC 0.514" — status: supported, counted as non-negative» [result]]
- **Status**: supported
- **Provenance**: user-revised
- **Falsification criteria**: A homogenization-layer presence proxy is shown to discriminate real
  paper-level rigor; OR a schema-demanded fabricated layer (dead-ends on a synthesis-genre paper) is
  shown to bind to an author-documented failure rather than a reframed conclusion; OR an extractive-layer
  metric is shown to diverge systematically from the paper's actual reported content.
- **Proof**: [research/metrics/v2/critiques-round2.md (RC3/RC4/RC5), metrics-critique.md §2-§4, staging O06/O11/O17/O18]
- **Interpretation**: This is the design contract for V3 (N40): build/keep metrics on extractive layers,
  strip fabrication via the RC3/4/5 detectors, and route homogenization proxies off the paper ranking to
  the artifact-trust axis. It does NOT close RC1/RC2 — external validity remains open by construction.
- **Dependencies**: —
- **Tags**: metrics, compiler-critique, methodology, v3-design
