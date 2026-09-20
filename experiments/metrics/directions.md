# Good-science metrics over a 140-paper ARA library

**Question.** If you compile ~140 works into ARAs — each with a PDF, ideally a code repo, and some
with linked clinical-trial records and datasets — what can you actually *count*, and which of those
counts are proxies for **good science**?

**Why this exists.** The ARA project's premise is that the two things we measure today — narrative
prose (for reviewers) and citation counts (for "impact") — are the wrong measures. Citations are a
Goodharted proxy: once counting them became the target they stopped tracking quality, and they
reward citable work (reviews, positive results) over neglected work (negative results, replications).
So the goal is *not* one number. It is **many independent, structure-derived signals**, each hard to
fake without actually doing the good-science thing it measures. Diversity is the defense against
Goodhart.

This doc has two parts and an appendix:
- **Part I — the metrics**, explained: seven directions, what each counts and why it counts.
- **Part II — how to compute them**, grounded in the concrete ARA artifact shapes (which files,
  which fields, which operations).
- **Appendix A** — a field-level inventory of the artifact shapes the recipes read from.

Every metric is tagged: **Scope** = `local` (one artifact) · `graph` (across the 140) · `grounded`
(needs an external DB/dataset); and a computation class = `[det]` deterministic parse/graph op,
`[sem]` semantic judgment (LLM extracts findings, score computed deterministically from them), or
`[ext]` external lookup.

---

# Part I — The metrics

## Direction 1 — Reproducibility & specification completeness
*The Engineering Tax made countable: "could a capable agent rebuild this from the artifact alone?"*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **Spec-completeness rate** | % of reproduction-critical requirements *fully* specified (vs partial/absent) | local | sem |
| **Gap-type profile** | missing items by kind (hyperparameters, data, seeds, hardware) | local | sem |
| **Cross-layer binding resolvability** | fraction of claim→experiment→evidence→code links that resolve | local | det |
| **Executable-reproduction rate (L3)** | did the code run and reproduce the central claim under a budget? (0/partial/1) | local | ext |
| **Environment completeness** | are runtime, deps+versions, hardware, data sources, seeds all present? | local | det |

**Virtue:** reproducibility. A work that fully specifies itself is one others build on without
rediscovering tacit detail. **Gameability:** completeness padding — guard by scoring only
*reproduction-critical* fields against a rubric. The L3 executable check is hardest to fake: the code
runs or it doesn't.

## Direction 2 — Claim & evidence integrity
*Rigor and honesty at the level of individual assertions — the machine version of peer review.*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **Claim-grounding ratio** | load-bearing numbers backed by a verified verbatim source quote | local | det |
| **Evidence relevance (D1)** | claims whose cited evidence *substantively* supports them | local | sem |
| **Falsifiability quality (D2)** | claims with actionable, non-trivial, scope-matched falsification criteria | local | sem |
| **Scope calibration (D3)** | claims whose stated scope ≤ what the evidence supports (flag over-claims) | local | sem |
| **Orphan counts** | experiments with no claim + claims with no evidence + evidence with no claim | local | det |
| **Status-honesty mix** | ratio of hypothesis / supported / refuted claims | local | det |

**Virtue:** epistemic soundness. Good science claims exactly what it shows, states how it could be
wrong, and grounds every number. A library where 100% of claims are "supported" and none are
falsifiable is a red flag. **Gameability:** trivial falsification criteria — the D2 non-triviality
check exists for this. Because LLM judges inflate grades (the paper documents it, node N13), compute
every `[sem]` number *deterministically from the extracted findings*, never from a judge's score.

## Direction 3 — Process transparency & negative knowledge
*The Storytelling Tax inverted into a virtue. This is what citations structurally cannot see.*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **Dead-end density** | `dead_end` nodes/paper carrying hypothesis + failure_mode + lesson | local | det |
| **Failure-knowledge preservation** | share of failed exploration retained vs discarded (normally-lost 113× / 90.2% of cost) | local | det |
| **Decision branching factor** | `decision` nodes recording the *alternatives considered*, not just the choice | local | det |
| **Explicit-vs-inferred ratio** | trace nodes grounded in source (`explicit`) vs reconstructed (`inferred`) | local | det |
| **Negative-result share** | claims with `status: refuted` + dead-ends carrying a transferable lesson | local + graph | det |

**Virtue:** honesty about process; preservation of expensive failure knowledge — the most reusable
part of research and the exact thing narrative publication deletes. Rewarding documented dead-ends
flips the incentive citations create. **Gameability:** fabricated dead-ends — require each to bind to
real evidence/trace (the compiler already forbids synthetic trace history), and weight dead-ends that
were later *reused* by another artifact (Direction 5).

## Direction 4 — Novelty & dependency structure
*Replace "cited N times" with "what did it actually do to the prior work."*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **Typed-delta profile** | outgoing related-work edges by type: extends / refutes / bounds vs imports / baseline | local + graph | det |
| **Corrective-science score** | edges that `refute` or `bound` prior work (weighted above `imports`) | graph | det |
| **Novel-claim count** | claims flagged `original: true` and FOL-distinct from existing library claims | graph | det+sem |
| **Concept-introduction rate** | genuinely new concepts defined vs borrowed terms | graph | sem |

**Virtue:** novelty and corrective contribution. A paper that refutes or bounds a prior result does
high-value work citations often *penalize*. Typing the edge captures the intellectual move, not the
name-drop. **Gameability:** over-tagging "refutes" — validate refutation edges against whether the
refuted claim's evidence is actually addressed (a D1-style check).

## Direction 5 — Cross-library claim graph  ★ flagship
*Once claims are typed and FOL-normalized across all 140, you get a knowledge graph whose edges are
evidential, not social — a genuine alternative to the citation network.*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **Corroboration count** | independent papers whose evidence `supports` the same FOL-equivalent claim | graph | det |
| **Contradiction / contested score** | papers whose evidence `contradicts` a claim → flags unsettled science | graph | det |
| **Replication depth** | a claim independently L3-reproduced by ≥N distinct artifacts | graph | ext |
| **Knowledge reuse ("real impact")** | how often a paper's claims/artifacts are imported/extended/reproduced by *later* ARAs | graph | det |
| **Claim redundancy rate** | fraction of library claims that are FOL-duplicates of others | graph | det |
| **Evidence-weighted confidence** | aggregate support − contradiction, weighted by each source's rigor score | graph | det |

**Virtue:** corroboration, replication, and *actual* reuse — what citation counts pretend to measure
but don't. "How many independent, rigorous artifacts reproduced or built on this claim" is what
impact was always supposed to mean. **Gameability:** self-citation rings — down-weight edges inside
the same author/lab cluster; require reuse edges to bind to a real claim/artifact, not a bibliography
entry. Contested-claim surfacing is *anti*-gameable: it rewards finding disagreement, not consensus.

## Direction 6 — Real-world grounding & translation
*Use the connected clinical-trial data, drug databases, and datasets to check whether a claim touches
reality. Where the biomedical library earns its keep — and where "alien protein" candidates get
filtered from fantasy.*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **Dataset connectivity** | claims backed by an *actually attached* dataset (not just a described one) | local + grounded | det |
| **Bench-to-trial linkage** | claims that map to a registered trial on ClinicalTrials.gov | grounded | ext |
| **Claim-vs-endpoint concordance** | for claims that reached a trial, did the trial's endpoints support them? | grounded | ext+sem |
| **Target / compound resolvability** | drug/target claims whose entities resolve in ChEMBL with known bioactivity | grounded | ext |
| **Candidate plausibility filter** | synthetic-node ("alien protein") outputs whose nearest real neighbor is close enough to be buildable | grounded | ext |

**Virtue:** translation and external validity. A claim that survives contact with a registered trial,
a real target, or an attached dataset is worth more than one that only lives in prose. **Gameability:**
low — you can't fake a ClinicalTrials.gov ID or a ChEMBL bioactivity record; the risk is coverage
bias (only biomedical claims are checkable this way).

## Direction 7 — Artifact / representation quality (meta)
*Not about the science, about the record — needed to normalize and weight every metric above.*

| Metric | Counts | Scope | Class |
|---|---|---|---|
| **ARA Seal level attained** | L1 (structural) / L2 (epistemic) / L3 (executable) reached per artifact | local | det+sem |
| **Compilation fidelity** | share of PDF-accessible information actually captured in the ARA (recall) | local | sem |
| **Auditor-blindspot flags** | orphan experiments the L2 auditor misses (only 22% caught) — better done in L1 | local | det |

**Virtue:** trustworthiness of the measurement substrate. Every other metric is only as good as the
compilation it runs on; a low-fidelity ARA silently corrupts the library-level graph. Use these to
*weight* contributions in Directions 4–5.

---

# Part II — How to compute, given the ARA artifact shapes

Each ARA is a directory (see Appendix A for the exact fields). Two extra substrates exist:
- the **oshima store** — a DB of per-paper `Claim` (with `original`, `confidence`,
  `centrality_percentage`), typed `Evidence` (`direction ∈ {support, contradict, contextual}`),
  `fol_json` (SUMO+WordNet FOL AST), and cross-paper `themes` over a `library`;
- **external DBs** via MCP — ClinicalTrials.gov, ChEMBL, PubMed — plus any attached datasets.

Notation: `claims.md::Cxx.Field` means "the `Field` of block `Cxx` in `logic/claims.md`."

## D1 — Reproducibility & specification completeness

- **Spec-completeness rate** `[sem]`. Inputs: `src/environment.md`, `src/configs/*`,
  `src/execution/*`, `logic/experiments.md::E*.Setup`. Procedure: instantiate a per-domain rubric of
  reproduction-critical requirements (reuse a PaperBench-style list, or auto-derive from `E*.Setup`
  slots: model, data, hardware, seeds, hyperparameters); for each requirement have an LLM label
  `full | partial | absent` with the source line it found; **score = full / total**, computed from
  the labels, not asked of the LLM. Output: fraction ∈ [0,1]. (This is exactly the paper's 45.4%
  headline, re-run per artifact.)
- **Gap-type profile** `[sem]`. Same labels, grouped by requirement kind → a histogram (matches the
  paper's "missing hyperparameters = 26.2%").
- **Cross-layer binding resolvability** `[det]`. Parse the four link types and check each resolves:
  `claims.md::Cxx.Proof`→`experiments.md::E*`; `experiments.md::Exx.Verifies`→`claims.md::C*`;
  `evidence/README.md` rows→claim IDs; `heuristics.md::Hxx.Code ref`→a real `src/execution/` path;
  tree `evidence:`→claim IDs. Output: resolved / total links.
- **Environment completeness** `[det]`. Presence-check the `src/environment.md` fields
  (Language/runtime, Framework+versions, Hardware, Data sources, Key dependencies, Protocols,
  Random seeds). Output: present / 7.
- **Executable-reproduction rate (L3)** `[ext]`. Run the ARA-Seal L3 protocol: sandbox
  `src/execution/` with `evidence/` masked, reproduce the central claim (highest
  `centrality_percentage`) under a compute budget, compare to `evidence/` directionally. Output:
  `0 | partial | 1`.

## D2 — Claim & evidence integrity

- **Claim-grounding ratio** `[det]`. For each `claims.md::Cxx`, count load-bearing numbers in
  `Statement` and how many appear in a `Sources` entry with a real `«verbatim quote»` (the compiler's
  `# Grounding` discipline). Verify by re-opening `file:line`/`trace-node:field` and string-matching
  the quote. Output: grounded numbers / total; a bare path or absent quote counts as ungrounded.
- **Evidence relevance (D1)** `[sem]`. For each `Cxx.Proof`→`Exx` pair, infer claim type from
  Statement cues (causal/generalization/improvement/descriptive/scoping) and have an LLM emit a
  finding: does `Exx.Setup/Procedure/Metrics` address the claim, and is the design type-appropriate
  (causal→ablation, improvement→baseline, …)? Score = share of pairs with a "relevant" finding.
- **Falsifiability quality (D2)** `[sem]`. Per `Cxx.Falsification criteria`, LLM emits findings on
  actionability, non-triviality, scope-match, independence; score = share passing all four.
- **Scope calibration (D3)** `[sem]`. Compare universal scope markers ("all", "any", "SOTA across")
  in `Statement` against the conditions in `Evidence basis` / linked `E*.Setup`; flag substantial
  gaps. Output: over-claim count and under-claim count (evidence with no claim).
- **Orphan counts** `[det]`. Set diffs over the cross-layer maps: experiments with empty
  `Verifies`-inbound, claims with empty `Proof`, evidence rows with empty `Claims`.
- **Status-honesty mix** `[det]`. Tally `claims.md::C*.Status`. Output: the distribution; flag
  artifacts with 0 falsifiable or 0 non-supported claims.

## D3 — Process transparency & negative knowledge

All `[det]`, parsing `trace/exploration_tree.yaml`:
- **Dead-end density** = count of `type: dead_end` nodes that have non-empty `hypothesis` +
  `failure_mode` + `lesson`, ÷ claim count.
- **Decision branching factor** = mean `len(alternatives)` over `type: decision` nodes.
- **Explicit-vs-inferred ratio** = `support_level: explicit` ÷ all nodes.
- **Failure-knowledge preservation** = dead_end+pivot nodes ÷ total nodes (proxy for how much of the
  branching survived compilation); if run-cost logs are attached, compute retained-failed-tokens ÷
  total-failed-tokens directly.
- **Negative-result share** `[det/graph]` = (`refuted` claims + lesson-bearing dead-ends) ÷ total
  claims, aggregated across the library.

## D4 — Novelty & dependency structure

- **Typed-delta profile / Corrective-science score** `[det]`. Parse `related_work.md::RW*.Type`
  (`imports | bounds | baseline | extends | refutes`). Profile = per-type counts; corrective score =
  `w·(refutes+bounds) + extends` with `w>1`.
- **Novel-claim count** `[det+sem]`. Take oshima `Claim.original == true`; then FOL-dedup its
  `fol_json` against all library claims (below) and keep the distinct ones. Output: distinct original
  claims.
- **Concept-introduction rate** `[sem]`. `concepts.md` terms an LLM labels as newly-defined-here vs
  borrowed (cross-check against earlier-dated ARAs' concept sets).

## D5 — Cross-library claim graph  ★

First build the graph (once, over all 140):
1. **Nodes** = every oshima `Claim` across papers, carrying `original`, `confidence`,
   `centrality_percentage`, and its `fol_json`.
2. **Merge** FOL-equivalent claims into a *claim-cluster*: normalize `fol_json` ASTs
   (SUMO type + WordNet sense) and merge when they unify within a threshold τ (an open parameter —
   see below). Each cluster = one "scientific assertion" independent of wording.
3. **Edges** = oshima `Evidence` linking a paper to a cluster, typed `support | contradict |
   contextual`; plus `related_work.md` edges (`extends/refutes/bounds/imports`) mapped onto clusters;
   plus L3 reproduction results.

Then the metrics are graph queries `[det]` (except replication `[ext]`):
- **Corroboration count**(cluster) = #distinct papers with a `support` edge.
- **Contradiction/contested score**(cluster) = #`contradict` edges; contested = both support and
  contradict present.
- **Claim redundancy rate** = 1 − (#clusters ÷ #claims).
- **Knowledge reuse ("real impact")**(paper) = #later ARAs with an `extends`/`refutes`/reproduces
  edge into that paper's clusters, time-ordered by `PAPER.md::year`; discount edges within one
  author/lab cluster.
- **Evidence-weighted confidence**(cluster) = Σ(support·rigor) − Σ(contradict·rigor), where `rigor`
  is that source paper's D1/D2/D7 composite (the trust weight).
- **Replication depth**(cluster) `[ext]` = #distinct artifacts whose L3 run reproduced it.

## D6 — Real-world grounding & translation `[ext]`

- **Dataset connectivity** `[det]`. Fraction of claims whose evidence resolves to an attached file in
  `data/` (parse `evidence/README.md` + `data/dataset.md`), not merely a described dataset.
- **Bench-to-trial linkage** `[ext]`. For each high-centrality claim, extract intervention/condition
  entities and query ClinicalTrials.gov (`search_trials`); a match with a real NCT ID = linked.
- **Claim-vs-endpoint concordance** `[ext+sem]`. For linked claims, pull `get_trial_details` /
  `analyze_endpoints`; LLM emits a finding whether the trial's outcome supports/refutes/is-neutral to
  the claim; score computed from findings.
- **Target/compound resolvability** `[ext]`. Extract drug/target/compound mentions; resolve via
  ChEMBL (`target_search`, `compound_search`, `get_bioactivity`); resolvable-with-bioactivity = grounded.
- **Candidate plausibility filter** `[ext]`. For multi-omics synthetic-node outputs, compute nearest
  real neighbor distance in the embedding; if within a buildability threshold, cross-check the
  neighbor in ChEMBL; far neighbor ⇒ flagged "alien protein" (buildable-in-principle, not yet real).

## D7 — Artifact / representation quality (meta)

- **ARA Seal level** `[det+sem]`. L1 = run the deterministic structural validator (Seal Level 1
  checklist); L2 = run the rigor-reviewer six-dimension audit but keep the numeric verdict
  deterministic from findings; L3 = the executable check from D1. Output: highest level passed.
- **Compilation fidelity** `[sem]`. Sample PDF-accessible facts (numbers, tables, sections) and check
  each is captured somewhere in the ARA; recall = captured / sampled.
- **Auditor-blindspot flags** `[det]`. The orphan-experiment check from D2 run as a deterministic L1
  gate (the paper shows L2 only catches 22% of orphans — move it to L1).

## Composition
- **Two axes.** Every metric sits on *scope* (local → graph → grounded) and *virtue* (reproducibility,
  rigor, transparency, novelty, corroboration, translation). A scorecard should span both so no single
  gameable number dominates.
- **Trust-weighting.** D7 + D1–D2 become the `rigor` weight on D4–D5: a corroboration edge from a
  high-fidelity, L3-reproduced, well-calibrated artifact counts more than one from a thin PDF-only
  compile.
- **Deterministic verdicts, never judge scores.** For every `[sem]` metric, an LLM produces *findings*;
  the number is computed from the findings list — because the paper documents LLM-as-judge grade
  inflation and finding–score decoupling (trace nodes N12/N13).
- **Reward what citations punish.** Dead-ends, refutations, contested claims, replications — the
  neglected, low-citation activities that are nonetheless good science. That inversion is the point.

## Biggest leverage, in order
1. **Cross-library claim graph (D5)** — the actual replacement for the citation network.
2. **Executable reproduction + spec completeness (D1)** — hardest to fake, most objective.
3. **Process transparency / negative knowledge (D3)** — unique to the ARA structure.
4. **Real-world grounding (D6)** — turns the biomedical subset into ground truth.

## Open design questions
- **Rubric source (D1)** — reuse a PaperBench-style rubric or auto-derive per-domain from `E*.Setup`?
- **FOL-equivalence threshold τ (D5)** — how aggressively to merge claims before corroboration/dedup
  goes noisy.
- **Author/lab entity layer** — needed to discount self-reuse rings in D5; the ARAs don't carry it yet.
- **Coverage bias (D6)** — biomedical claims are externally checkable; theory/ML claims are not. Don't
  let "checkable" masquerade as "better."

---

# Appendix A — ARA artifact shapes (what the recipes read)

**`PAPER.md`** — YAML frontmatter: `title, authors, year, venue, doi, ara_version, domain, keywords,
claims_summary[], abstract`; body Layer Index tables (file → description, `/src` table also has a
Claims column).

**`logic/claims.md`** — `## C{NN}` blocks: `Statement`, `Sources` (`<value> ← <ref> «verbatim» [input|result]`),
`Status` (hypothesis|untested|testing|supported|weakened|refuted|withdrawn), `Falsification criteria`,
`Proof` ([E##]), `Evidence basis`, `Interpretation`, `Dependencies` ([C##]), `Tags`.

**`logic/experiments.md`** — `## E{NN}` blocks: `Verifies` ([C##]), `Setup` (Model/Hardware/Dataset/System),
`Procedure`, `Metrics`, `Expected outcome` (directional, no exact numbers), `Baselines`, `Dependencies`.

**`logic/problem.md`** — `O{N}` (Statement/Evidence/Implication), `G{N}` (Statement/Caused by/Existing
attempts/Why they fail), `Key Insight`, `Assumptions`.

**`logic/concepts.md`** — `## Term`: Notation, Definition, Boundary conditions, Related concepts.

**`logic/related_work.md`** — `RW{NN}`: DOI, `Type` (imports|bounds|baseline|extends|refutes), Delta,
Claims affected, Adopted elements.

**`logic/solution/`** — `constraints.md`; `heuristics.md` `H{NN}` (Rationale/Sensitivity/Bounds/Code
ref/Source); `architecture.md`/`algorithm.md` as warranted.

**`src/`** — `environment.md` (runtime/framework/hardware/data sources/deps/protocols/seeds);
`configs/*`; `execution/*.py` (first line `# Grounding: transcribed|reconstructed`); `artifacts.md`;
`data/` (dataset.md/preprocessing.md).

**`trace/exploration_tree.yaml`** — nested nodes: `id, type` (question|decision|experiment|dead_end|pivot),
`support_level` (explicit|inferred), `source_refs`, `provenance`, `status`, `children`,
`also_depends_on`; type-specific: `choice/alternatives/evidence` (decision), `result/evidence`
(experiment), `hypothesis/failure_mode/lesson` (dead_end), `from/to/trigger` (pivot).

**`evidence/`** — `README.md` index (file → Source → Claims → Description); `tables/*.md`+`.png`;
`figures/*.md`+`.png` (Figure type / Extraction method / Reading confidence).

**oshima store** (from `src/execution/app/models/extract.py`) — `Claim{claim, explanation, claim_id,
verbatim_statement, rephrased_statement, original:bool, confidence:0-1, centrality_percentage:0-100}`;
`Evidence{evidence, explanation, evidence_id, direction: support|contradict|contextual}`; `fol_json`
(SUMO+WordNet FOL AST, from `nlp2fol/`); `themes` over a `library`'s claims (`themes/theme_service.py`).

**External** (MCP) — ClinicalTrials.gov (`search_trials`, `get_trial_details`, `analyze_endpoints`);
ChEMBL (`target_search`, `compound_search`, `get_bioactivity`); PubMed.

---

# Critiques, responses, and V2 paths forward

The wave-1 test run (10 OA Alzheimer's-biomarker ARAs; see `research/metrics/coverage-gaps.md`)
surfaced six critiques of the V1 design. Each is recorded here with my response (defense vs.
learning) and the concrete change it drove in **V2** (`research/metrics/v2/`).

| # | Critique | Response | V2 path forward |
|---|----------|----------|-----------------|
| 1 | **Compiler, not science.** Near-ceiling, zero-variance metrics (falsifiability presence 1.0, binding 0.99, seal 0.97) measure the compiler's consistency, not paper quality; woj25's grounding 0.0 is a *compile* defect, not an authorship defect. | **Learning.** V1 conflated artifact-quality with paper-quality. | Tag every metric `paper_quality` vs `artifact_quality`; report them in separate blocks. Artifact-quality feeds the trust-weight, never the paper ranking. |
| 2 | **Gates ≠ rankers.** Binding resolvability and seal-L1 are L1 *validity gates* (a well-formed ARA must pass them), not continuous quality rankers — averaging them is a category error. | **Learning.** Mislabeled hygiene as quality. | Split `gates` (binary pass/fail hygiene) from `rankers` (continuous, genre-scoped quality). Never rank on a gate. |
| 3 | **Genre-blindness.** Scoring `0` for L3 / dead-ends / negative-results on clinical papers penalizes a paper for its genre. | **Learning (biggest).** | Classify each ARA's genre; an **applicability model** returns `N/A (genre)` where a genre structurally lacks a dimension; rank only *within* a genre. |
| 4 | **Grounding presence ≠ truth.** The grounding ratio only checks a `«quote»` is *present*, not that it is real or supports the number — so 1.0 means "quote-decorated," not "verifiably grounded." | **Learning (self-caught over-claim).** | **Verified grounding**: re-open the cited in-repo file and confirm the `«quote»` string is actually there. Report `presence` vs `verified` vs `unverifiable_in_repo` (§/PDF refs). |
| 5 | **ML-shaped spec proxy.** Spec-completeness scored ML slots (Model/Hardware/Dataset/System) → ~0 for every clinical paper. | **Learning.** | **Dropped in V2, not implemented (RC11):** V2 removed spec-completeness entirely rather than reimplementing it — there is no spec ranker in `compute_metrics_v2.py`. A genre-parameterized clinical rubric is a `[sem]` task, deferred to the trust axis; it is *not* a delivered V2 fix. (Originally listed here as a rubric; corrected to match the code.) |
| 6 | **Adversarial test-bed.** 10 single-genre, backprocessed, code-free, non-cross-citing papers is near-worst-case; much apparent failure is test-design. | **Defense — but my error to own.** Metrics are for cross-genre, at-scale, native-capture use. | Add a **discrimination diagnostic** (per-metric variance/range across the library) that flags non-informative metrics automatically, so the tool self-reports when a corpus can't exercise a metric. |

**What V2 is not fixing yet** (needs more than a reshape): the real D5 FOL claim graph (needs the oshima
typed-evidence/`fol_json` layer), the `[sem]` LLM-judge pass, and the `[ext]` ClinicalTrials/ChEMBL
enrichment. V2 is a *scoring-model* redesign over the same deterministic inputs, plus verified grounding.

## Round-2 critique of the V2 responses (the reviewer answers back, 2026-07-05)

V2 fixes the two most embarrassing *surface* bugs (averaging hygiene gates into quality; scoring
presence-only grounding) and adds a genuinely good self-diagnostic. But it treats symptoms: the core
disease — **every number is still computed from the compiler's reconstruction, with no external ground
truth** — is untouched, and three of the "fixes" are cosmetic, unimplemented, or actively misleading.
Per-response rebuttal:

| # | V2's move | Round-2 rebuttal | Verdict |
|---|-----------|------------------|---------|
| 1 | Tag `paper_quality` vs `artifact_quality`. | **Cosmetic.** In the actual output *every* ranker is tagged `paper_quality` — including `grounding_verified` and `environment_completeness`, which are still substantially compiler-determined (see #4). The split is asserted by a string label, not by anything the metric measures. The conflation moved into the `gates` block (`all_links_resolve` fails for kes25/pal25/sal26/woj25 — a *compiler* failure now reported as an artifact-hygiene gate), it didn't get separated. | Relabeled, not fixed |
| 2 | Split binary `gates` from continuous `rankers`. | **Legitimate, and the best structural change** — but it quietly concedes that ~half of V1's signals carry zero ranking information, and one gate (`all_links_resolve`) is still a compiler-consistency check masquerading as artifact hygiene. Honest, but it *shrinks* the system more than it improves it. | Real improvement |
| 3 | Genre-aware applicability; `N/A(genre)` not 0; rank within genre. | **Fixes fairness, destroys ranking power, and rests on a broken classifier.** The genre labeler is first-match keyword matching and is already **wrong for cum26** (a drug-development *pipeline review* labeled `clinical_trial`), which corrupts both its applicability and its within-genre bucket. Worse: splitting 10 papers across 6 genres atomizes the corpus into **singletons** — meta_analysis=1, cohort=1, guideline (with checkable grounding)=1 — so "compare like with like" produces one-paper rankings you cannot rank. Correct in principle, comparatively powerless at n=10. | Right idea, unusable here + fragile |
| 4 | **Verified grounding**: re-open the cited file, confirm the `«quote»` is there. | **The single real fix — and it exposes the disease it was meant to cure.** (a) It's computable for only **4/10** ARAs; the other 6 cite `paper.pdf`/§refs and return `None`, so the metric now measures a *compiler choice* (cite in-repo evidence vs cite the PDF), which the comparison doc itself calls "the dominant, uncontrolled factor" — that is critique #1 reappearing *inside* the fix. (b) It still only checks the quote **string exists**, not that it **supports the number or the claim**; a compiler that pastes a real table cell next to a wrong assertion still scores 1.0. "presence ≠ truth" became "quote-string-in-file ≠ truth" — narrowed, not closed. The diagnostic flags it `low_variance` (n=4): even where computable, it doesn't discriminate. | Half-fix; still compiler-bound |
| 5 | Genre-parameterized clinical spec rubric. | **Not implemented — vaporware in the table.** V2 *dropped* spec-completeness entirely (there is no spec ranker in `compute_metrics_v2.py`); the row presents a deletion as a delivered fix. | Not done |
| 6 | **Discrimination diagnostic** (per-ranker variance → flag non-informative metrics). | **Honest and useful, but it gives false confidence: variance is not validity.** It correctly greys out `falsifiability_presence` (non-discriminating) and `grounding_verified` (low-variance). But it **greenlights the three fabricated/blind metrics as "discriminating"** — `dead_end_density`, `corrective_science_score`, `negative_result_share` — precisely because compiler artifacts *vary*. A metric can be confidently, discriminatingly wrong. The diagnostic measures spread, never correctness, so it launders the round-1 defects as passing signals. | Useful, but misleading here |

**What V2 left completely untouched** (the round-1 findings that actually mattered):

- **Fabricated dead-ends survive.** che26 still scores `dead_end_density = 0.25` and `negative_result_share = 0.2` — both driven *entirely* by the compiler-manufactured straw dead-ends N11/N12 (che26 is a meta-analysis with no exploration process). V2 relabeled their "genre baseline" but still counts the fiction, and the diagnostic now certifies it as "discriminating."
- **`corrective_science_score` still has `refutes = 0` library-wide** and is still driven by `bounds`/`extends` re-labeling of baselines. Kept as a ranker, unchanged, flagged "discriminating."
- **The genuine negative result is still invisible.** woj25 C04 (a real null) is still `status: supported`; `negative_result_share` still can't see it.
- **No external validation, still.** Nothing checks any metric against expert rating, held-out reproduction, or retraction. The discrimination diagnostic is *not* validation — it answers "does this vary?", never "is this right?".

**Net:** V2 is a competent, honest engineering reshape that makes the system *admit* more of what it
can't do (N/A-for-genre, low-variance flags) and fixes grounding presence-inflation for the 4 papers
where it's checkable. It does **not** move the project one step toward measuring good science rather
than compiler behavior. The prerequisites from round 1 stand and are the only things that would make
"good-science metric" more than an assertion: (i) validate ≥1 ranker against an external quality
signal; (ii) compute grounding/dead-ends/status against the **source PDFs**, not the compiler's YAML;
(iii) run on a heterogeneous, code-shipping, cross-citing corpus so the dead rankers (L3, D5) can
actually vary; (iv) add a *validity* check (does the quote support the number/claim), not just a
variance check. Until then V2 is a better-instrumented way to measure the same wrong thing.

# Change log
- **2026-07-05** — Created. Read the ARA paper (Liu et al. 2026, arXiv:2604.24658v3: framing p1,
  Table 4 Rigor-Auditor detection, Table 5 five agent-native dimensions), the ARA Compiler skill +
  schema, the rigor-reviewer's six review dimensions, and the compiled `research/ara/`. Drafted the
  seven metric directions and this file. This session's research process is also recorded in the ARA
  trace: question node **N27** in `research/ara/trace/exploration_tree.yaml`; observations
  **O01–O03** (staged, not yet crystallized) in `research/ara/staging/observations.yaml`; turn 3 of
  `research/ara/trace/sessions/2026-07-05_001.yaml`.
- **2026-07-05** — Added Part II (computation recipes grounded in artifact shapes) and Appendix A
  (field inventory), after confirming the oshima `Claim`/`Evidence` schema in
  `research/ara/src/execution/app/models/extract.py`.
- **2026-07-05** — Ran V1 over 10 OA ARAs (`research/metrics/`), then added the "Critiques, responses,
  and V2 paths forward" section from the test-run review. Implemented **V2** in `research/metrics/v2/`
  (genre-aware applicability, gates-vs-rankers split, verified grounding, paper- vs artifact-quality
  provenance, discrimination diagnostic) and a V1↔V2 comparison (`research/metrics/v2/comparison_v1_v2.md`).
- **2026-07-05** — Round-2 critique of the V2 responses added to the "Critiques, responses, and V2
  paths forward" section (reviewer's rebuttal, per-response verdicts + what V2 left untouched). Bottom
  line: V2 fixes surface bugs (gate/rank split, presence→verified grounding) but the fabricated
  dead-ends, `refutes=0` corrective score, blind negative-result share, and the absence of any external
  validation all survive; the discrimination diagnostic measures variance, not validity, and greenlights
  the fabricated metrics. Also flagged: genre classifier mislabels cum26, genre-split atomizes n=10 into
  unrankable singletons, verified grounding computable for only 4/10, and the crit-#5 clinical spec
  rubric is listed as a fix but was dropped, not implemented.
