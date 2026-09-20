# Metric-Design Tournament — Summary

11 ARA-compiler artifacts. Each ran a 2-stage tournament: 4 blind proposers → judge picked 2
finalists → both revised in response to a stage-1 critique → judge picked 1 winner and qualified
it. Below: per-artifact winner (metric names + judge's qualification), then a cross-artifact
synthesis. Sourced from `research/metrics/v3/tournament/<artifact>/improved/<WINNER>.md` and
`critique_stage2.md` for each of the 11 artifacts.

---

## 01. `paper_manifest` (`PAPER.md`) — Winner: A

**Metrics:**
1. **Frontmatter/Body Self-Consistency** — does the manifest's self-reported claim/table/figure counts agree with the document's own structure.
2. **Claim Falsifiability & Precision Density** — do `claims_summary` one-liners carry numbers, CIs/comparisons, unhedged.
3. **Epistemic Transparency of Absence** — when code/data layers are thin, does the prose name the specific gap (not a generic trigger phrase).
4. **Domain–Claim Lexical Grounding** — do `domain`/`keywords` share real (IDF-weighted) technical vocabulary with the content.
5. **Layer-Index Evidentiary Density per Claim** — is trace/evidence volume roughly proportional to the number of claims asserted.
6. **Identifier & Bibliographic Integrity** — DOI/authors/year/venue well-formed, with honest `"Not specified in paper"` scored equal to a valid identifier.

**Judge's qualification:** Measures "manifest internal integrity and disclosure honesty" — four of six metrics are coherence/hygiene checks; only #3 and #5 gesture at research virtues, and even those are English-surface regex (detect disclosure *language*, not disclosure *truth*; reward precision of *phrasing*, not correctness of *findings*). No metric touches the actual scientific content behind the manifest. **Verdict: does not clear "measures good science" — honest manifest-integrity proxy, limited reach.**

---

## 02. `claims` (`logic/claims.md`) — Winner: B

**Metrics:**
1. **Falsifiability Operationalization & Boilerplate Score** — falsification criteria carry checkable numbers/comparators specific to the claim, not templated across claims.
2. **Grounding Fidelity & Numeric Coverage Score** — every asserted number traces to a verbatim, located quote.
3. **Grounded Evidence–Interpretation Separation Score** — evaluative language is confined to `Interpretation` or grounded in a source quote, not smuggled into fact fields.
4. **Dependency Graph Integrity Score** — claim-dependency graph is an acyclic, non-free-riding, non-flat DAG.
5. **Evidentiary Concentration & Transitive Anchor Fragility Score** — breadth doesn't collapse to one dataset; no long dependency chain rests on one thin anchor.
6. **Status–Documentation Calibration Score** — disconfirming/hypothesis claims are documented as rigorously as confirmed ones (selective-reporting detector).

**Judge's qualification:** A six-axis proxy for "whether the claims are checkable, structurally distributed, and candidly reported." Fundamental ceiling: "every check runs over the ARA's own fields... a well-compiled artifact of a wrong paper scores as high as a well-compiled artifact of a correct one." Grounding fidelity verifies `value ∈ quote`, not `quote ∈ real source`. **Verdict: honest-but-limited — measures rigor, not scientific truth.**

---

## 03. `concepts` (`logic/concepts.md`) — Winner: A

**Metrics:**
1. **Boundary-Condition Substantiveness (BCS)** — boundary text is a genuine, non-paraphrased limiting clause, not boilerplate or a copy of the definition.
2. **Concept Graph Coherence (CGC)** — the vocabulary resolves into one connected structure, referencing real headings, without requiring artificial mutual citation.
3. **Definition Distinctiveness & Grounding (DDG)** — definitions are non-circular, mutually distinct, and anchored to the paper's own specifics rather than portable textbook prose.
4. **Notation–Prose Extraction Fidelity (NPEF)** — declared notation agrees with symbols actually used in the prose.

**Judge's qualification:** "Every signal scores what the compiler wrote, not whether the paper did careful science... this catches shallow extraction, which correlates with but is not identical to shallow science." DDG's grounding cue is a soft multiplier spoofable by inserting deictic phrases ("in this analysis") plus a stray number. A carried over one hard-constraint leak (missing vs. honestly-absent notation scored identically) that the losing finalist had fixed. **Verdict: honest-but-limited — honest extraction-quality proxy, not science.**

---

## 04. `problem` (`logic/problem.md`) — Winner: A

**Metrics:**
1. **Evidential Grounding Depth** — Observations cite section-anchored, multi-author-year citations, not "Evidence: Abstract" restatements or duplicated citation blocks.
2. **Argument-Graph Connectivity** — Observation→Gap→Insight reference graph resolves to real ids with no orphans or dead ends.
3. **Insight Synthesis Specificity (anti-restatement)** — the Key Insight draws on ≥2 upstream nodes and shares *distinctive* (non-boilerplate) vocabulary with each, not generic "we propose" filler.
4. **Gap Failure-Mode Specificity** — `Existing attempts`/`Why they fail` name specific methods/numbers and anchor to a real Observation id.
5. **Assumption Risk Exposure** — stated assumptions are concrete/checkable conditions, not vague truisms.

**Judge's qualification:** "Verifies form, not truth... a problem statement with fabricated-but-well-formatted citations... internally-consistent-but-wrong `caused_by` edges... would score near the top." Only *internal* id-references are validated; nothing checks citations against a real bibliography. **Verdict: honest-but-limited — honest-but-limited compile-quality proxy.**

---

## 05. `experiments` (`logic/experiments.md`) — Winner: B

**Metrics:**
1. **Falsifiability Density** — `Expected outcome` statements are directional/comparative, unhedged, and lexically tied to what `Metrics` actually measures.
2. **Comparator Rigor & Diversity** — baselines are named and typed (internal vs. external), with credit for mixing both types.
3. **Method–Measurement Internal Consistency** — `Metrics` vocabulary is anchored in the same block's own `Setup`/`Procedure` text (genre-agnostic, anti-copy-paste).
4. **Triangulation / Verification Load (claims-bound)** — a claim is corroborated by ≥2 *textually distinct* experiments that resolve to real ids in `claims.md`.
5. **Structural Integrity & Anti-Padding** — dependency graph is a valid DAG over real ids; cross-block textual similarity flags copy-paste padding.

**Judge's qualification:** "Everything is lexical... a sophisticated author who threads consistent real-sounding terminology... can satisfy Metrics 1 and 3 without the underlying study being sound." "Independent corroboration" in triangulation is token-set distinctness, not methodological independence. No contact with `evidence/` or ground truth. **Verdict: honest-but-limited — measures structural rigor, ultimately lexical.**

---

## 06. `related_work` (`logic/related_work.md`) — Winner: A

**Metrics:**
1. **Delta Concreteness Score** — "what changed"/"why" text carries concrete markers (numbers, acronyms, effect sizes) over generic filler.
2. **Provenance-Grounding Score** — "Adopted elements" and "Delta → What changed" share vocabulary (cross-field coherence, not two independently fabricated blobs).
3. **Claims-Linkage Grounding Ratio** — a "substantiated" gate requires real prose + adopted content before a claim tag counts, with a template-duplication penalty across blocks.
4. **Footprint Tiering Completeness** — the citation sweep covers both a full and a brief tier, not just the closest predecessors.
5. **Type–Narrative Consistency** — the declared `Type` (imports/baseline/extends/bounds/refutes) is substantiated by matching prose (generalization/contradiction language, real adopted elements).

**Judge's qualification:** "A meticulous compile of a mediocre paper scores high; a sloppy compile of a landmark paper scores low. It measures extraction quality." Every "semantic" check is lexicon/regex-based; DOIs are unverified (well-formed but fabricated passes); claim IDs are trusted, never validated against a real ledger. **Verdict: honest-but-limited — measures compilation craft, not science.**

---

## 07. `solution` (method layer) — Winner: A

**Metrics:**
1. **Concrete-Referent Density** — boundary conditions/assumptions/limitations name concrete referents (numbers, acronyms, section pointers), not generic hedges.
2. **Data-Quality-Caveat Coverage** — evidence-layer-detected inconsistencies are surfaced in `constraints.md`, not silently laundered (with an explicit "scan-actually-ran" attestation).
3. **Method-Genre Coherence & Heuristics-Omission Audit** — method-file names match their actual content genre; visible implementation tricks are captured in `heuristics.md`.
4. **Assumption/Boundary Grounding Overlap** — constraint-layer named entities (IDF-weighted) actually recur in the method files, not boilerplate.
5. **Assumption→Consequence Traceability** — each assumption is traced to a real, non-duplicated statement of what breaks if it's false.

**Judge's qualification:** "A scores the honesty and specificity of the write-up, not the validity of the design, the correctness of the statistics, or the truth of the conclusions." An author with the method files in hand can transplant distinctive vocabulary into `constraints.md` to inflate the grounding-overlap metric without improving the limitation's actual quality — the defense against this is cross-metric and probabilistic, not structural. **Verdict: honest-but-limited, at the top of that band — structural grounding plus examined-rigor signal.**

---

## 08. `exploration_tree` (`trace/exploration_tree.yaml`) — Winner: A

**Metrics:**
1. **Grounded Failure Disclosure Score** — `dead_end` nodes are cited, complete, and specific (not decorative or absent), with a genre-corroborated (two-signal) floor softener for synthesis papers.
2. **Convergent Synthesis Score** — cross-branch `also_depends_on` edges are structurally real (not same-lineage/dangling) and topically coherent (≥2 shared content words).
3. **Decision Deliberation Depth** — `decision` nodes name substantive rejected alternatives with real evidence, not rubber-stamp phrases.
4. **Pivot Traceability & Consequence** — pivots are anchored to upstream nodes with real shared vocabulary, not free-floating narrative.
5. **Support-Level Calibration** — `explicit` labels require `source_refs`; pivots default honestly to `inferred`.

**Judge's qualification:** "It measures whether a research trace was disclosed with integrity... not the quality of the underlying science directly." Lexical overlap is a weak semantic proxy — two nodes can share topical nouns with no genuine causal connection; a determined author writing coherent-but-fabricated content still passes. Every anti-Goodhart argument reduces to "faking this is expensive," not "faking this is caught," absent an upstream source-grounding check the metric set doesn't itself perform. **Verdict: honest-but-limited, leaning strong — honest disclosure-integrity proxy, not quality.**

---

## 09. `evidence` (`evidence/`) — Winner: A

**Metrics:**
1. **Sweep Completeness** — every numbered table/figure referenced anywhere is either filed or named with a real reason in the completeness note.
2. **Extraction-Method Honesty** — `exact_from_labels` vs. `digitized_estimate` (`≈`) labels are internally consistent; no numeric tables smuggled into diagrams.
3. **Type-Body Structural Conformance** — each figure/table type's mandatory body fields are actually filled, with a substance gate on low-confidence fallback trend text.
4. **Claims-Grounding Coverage** — fraction of filed tables/figures carrying a non-empty `Claims` link, discounted for thin evidence sets.
5. **Numeric Reconciliation Transparency** — labeled totals (n=, screened, included) either reconcile with inner numbers or are explicitly flagged as mismatched.

**Judge's qualification:** Strong, hard-constraint-respecting measure of "transcription discipline and self-consistency" on 4 of 5 axes. But the layer's *core purpose* metric (#4, claims-grounding) is "the most Goodhartable in the set" — uniform rubber-stamping of one real claim ID onto every row drives coverage to 1.0, and the losing finalist's distinct-claim-set guard (which would have closed this) was not adopted. Nothing verifies numbers against the source; only internal consistency. **Verdict: honest-but-limited — honest hygiene, claim-grounding stays gameable.**

---

## 10. `implementation` (`src/` reproduction layer) — Winner: B

**Metrics:**
1. **Capture Proportionality** — `execution/` coverage is proportionate to what the repo/`artifacts.md` actually claims exists, rewarding honest disclosure of scope decisions over silent gaps or fabricated code.
2. **Grounding-Tag & Citation Integrity** — every `execution/*` file self-declares `transcribed`/`reconstructed` with a real citation or an honest `NotImplementedError` stub; uniform "all reconstructed" against a claimed repo is discounted.
3. **Configuration Rationale–Sensitivity Calibration** — parameter rationale is filled in proportion to declared sensitivity, discounting uniform/decorative sensitivity labeling.
4. **Environment Metadata Concreteness & Transparency** — environment fields are concrete-and-corroborated (cross-referenced against `execution/` content or a known-tool lexicon) vs. honestly-flagged-absent vs. silently blank.
5. **Claim-Traceability of Captured Artifacts** — artifact blocks tie to real, specific claim ids (verified against a `claim_inventory` when available), not blanket "all."

**Judge's qualification:** "A methodologically weak paper with meticulous, honest, well-tagged metadata scores high; a strong paper with sloppy metadata scores low... it is a proxy for good record-keeping, not for good science." Fabrication defense (claim-id verification) is conditional on an optional cross-layer input often unavailable to a single-layer metric; grounding-shape checks (line counts, keyword presence) detect gross mislabeling, not competent forgery. **Verdict: honest-but-limited — honest-but-limited reproducibility-reporting hygiene measure.**

---

## 11. `dataset` (`data/dataset.md` + `preprocessing.md`) — Winner: A

**Metrics:**
1. **Access-Tier Honesty** — open/gated disclosure is scoped to a named data layer or an explicit all-open claim, not a lazy blanket "available."
2. **Provenance & Size Specificity** — real accession IDs, numeric dimensions, and named instruments/platforms back the data description.
3. **Internal Discrepancy Self-Audit** — stated aggregate counts (studies/participants) reconcile against tabulated row counts *and* summed N-columns, or the mismatch is explicitly flagged.
4. **Genre-Scope Fidelity** — secondary-reuse content doesn't fabricate raw-QC language; primary-generation "generated in this study" claims require a real accession id.
5. **Ethics/Consent Coverage Conditioned on Data Genre** — IRB/consent is disclosed (or explicitly marked not-applicable), genre-appropriately.
6. **Preprocessing Traceability Proportional to Raw-Data Claims** — a QC trail spans multiple distinct dimensions (filtering, normalization, batch correction, exclusion, versioning) in proportion to the raw-data claim strength.

**Judge's qualification:** Retains "the single most Goodhart-resistant metric in the entire tournament" (Genre-Scope Fidelity's generation-claim-requires-accession check). But: "every metric is a text/token-presence check, not a truth check... a compiler emitting a fabricated-but-internally-consistent record... would score highly." The interlock raises the cost of *cheap* gaming, not *careful* gaming. **Verdict: honest-but-limited — honest provenance-documentation proxy, not validity.**

---

# CROSS-ARTIFACT SYNTHESIS

## 1. The recurring theme: hygiene, not truth

Every one of the 11 winners was judged an **honest-but-limited proxy** — never "measures good
science" in the strong sense. The specific flavor of "limited" is nearly identical across all 11:
each metric set scores *what the compiler wrote about the paper*, not *whether the paper's science
is true, important, or valid*. The judges' own words repeat the same finding independently across
artifacts with no apparent coordination: "measures the compilation, not the paper's truth" (02,
06), "scores the trace, not the paper" (08), "measures the compiler as much as the science" (11),
"cannot distinguish sound methodology from honest bookkeeping about unsound methodology" (10).

This is not a coincidence of eleven separately weak designs — it's structural. Every metric in
every winning set operates on **regex/lexical/structural signals computed over the ARA's own
text**: token overlap, citation-pattern matching, DAG well-formedness, presence/absence of hedge
words, cross-field vocabulary echo. None of the 44 finalist submissions (2 per artifact × ~2 rounds)
resolves an external fact — no metric fetches a DOI, checks a GEO accession against a live
registry, verifies a quoted source against the actual PDF, or confirms a claim is true. That's not
an oversight; it's the boundary condition of the exercise: these are **artifact-level, single-file,
offline metrics** by design, and a metric that only ever reads one Markdown/YAML file cannot, in
principle, verify anything about the world outside that file.

**What that means:** these metrics *can* measure compilation/documentation quality — internal
consistency, honesty of self-disclosure, structural completeness, resistance to templated padding —
and several do so with real engineering care (multi-field cross-checks, DAG integrity, IDF-weighted
grounding, hard hard-constraint discipline on missing inputs). They **cannot**, as a class, measure
"good science" in the sense of correctness, validity, reproducibility of *findings*, or truth of
*claims* — because that requires comparing the artifact against something outside itself (the
source paper, a live registry, a replication). A "well-compiled record of bad science" and a
"well-compiled record of good science" are, by construction, indistinguishable to every metric in
this tournament. The tournament's own judges converged on labeling this the same way independently
across all 11 artifacts, which is itself a strong signal that the finding is real rather than an
artifact of any one judge's taste.

## 2. Did any artifact reach genuine scientific quality?

No. Every winner was explicitly denied the "measures good science" bar by its judge. The closest
approaches, ranked by how far they push past pure hygiene:

- **07 (`solution`)** — judged "honest-but-limited, at the top of that band" — its
  Assumption→Consequence Traceability metric is singled out across multiple critiques as "the
  deepest science signal in this set" because it distinguishes *stating* an assumption from
  *examining its failure mode*, a genuine epistemic-effort signal, not just a presence check.
- **08 (`exploration_tree`)** — "honest-but-limited, leaning toward the stronger side of that
  line" — Convergent Synthesis Score is called out as doing real work distinguishing DAG
  convergence from mere tree nesting, a structural analog of independent corroboration.
- **11 (`dataset`)** — retains what its own judge calls "the single most Goodhart-resistant metric
  in the entire tournament" (Genre-Scope Fidelity), because tying a generation *claim* to a
  verifiable accession *identifier* is one of the few checks in the whole tournament that is
  falsifiable against something concrete (a real ID format) rather than pure vocabulary matching.
- **02 (`claims`)** is the most explicit about the ceiling: "measures rigor, not scientific truth"
  is the artifact's own reply line, cleanly separating "auditable and candidly reported" from
  "true and important."

None of these clears the bar. They're the pool's *best* proxies, not exceptions to the finding.

## 3. Recurring Goodhart-vulnerabilities

The same handful of exploits recur across nearly every artifact's stage-1→stage-2 arc (evidence
that they are generic to this class of metric, not artifact-specific bugs):

- **Length/verbosity as a free proxy for quality.** Nearly every stage-1 submission had at least
  one metric that rewarded raw text length or word count as a stand-in for substance (01, 02, 04,
  09, 10, 11). Every stage-2 winner had to strip this out in favor of *specific* tokens (numbers,
  named entities, structural markers) — but the fix is never fully closed; residual length gates
  survive into several winners (e.g., 10's `len(code_avail) > 40` branch).
- **Boilerplate/templated padding across repeated structures** (claims, experiments, related-work
  blocks, dead-end nodes). Fixed via cross-item similarity checks (Jaccard/SequenceMatcher) in 02,
  05, 06, 08 — but Jaccard-on-tokens is itself gameable by a "fluent bad-faith compile" that
  threads consistent, varied-but-generic vocabulary (noted explicitly in 03, 05, 07).
  Duplication of a rich block/answer across many claims to fake breadth (02's boilerplate
  falsification text, 05's cloned experiment blocks, 06's mass-cloned deltas).
- **Fabricated-but-internally-consistent content.** The single most-repeated limitation across all
  11 qualifiers: a metric that checks internal coherence (value appears in its own cited quote,
  DOI is well-formed, accession ID matches a regex, claim id is `C\d{2,}`-shaped) cannot
  distinguish a real fact from a *fabricated but self-consistent* one. Named explicitly in 02
  ("fabricated quote that happens to contain the claimed value passes"), 04, 06 ("well-formed but
  fabricated DOI passes"), 09, 10, 11 ("a determined adversary who fabricates a fully coherent
  provenance record defeats the whole set").
- **Honest-absence vs. fabrication asymmetry, when not designed carefully, incentivizes lying.**
  Several winning designs explicitly and correctly fix this (01's Metric 6 scores honest
  `"Not specified in paper"` equal to a valid DOI; 11's all-open disclaimer credited near-full
  rather than punished as "uncontrasted"), but the reverse failure — an under-designed honesty
  sentinel that scores *worse* than a real value — recurs as a stage-1 flaw across multiple
  artifacts and had to be explicitly corrected.
- **Genre/thinness false positives.** Metrics calibrated on a rich-paper assumption
  over-penalize legitimate genre variation (systematic reviews with no code, meta-analyses that
  are all-`supported`, all-open datasets, secondary-reuse papers with no raw QC). Every
  artifact's stage-2 revision had to add a genre-detection escape hatch — and every escape hatch
  is itself a new Goodhart surface (fake the genre signal to buy the softer bar), requiring a
  second, corroborating signal to close (08's two-signal genre gate is the most carefully built
  instance of this pattern).

## 4. Most promising metrics to actually build

Ranked by (a) how much real signal they carry beyond hygiene, and (b) how tractable the next
engineering step is:

1. **09's Sweep Completeness + Numeric Reconciliation Transparency (evidence layer).** Already the
   most externally-checkable pair in the tournament — reconstructing an implied ceiling of
   numbered objects from the artifact's own cross-references, and reconciling labeled totals
   against inner arithmetic, are structural, low-ambiguity checks. **To build:** wire in a
   screenshot-vs-transcription spot check (even a cheap OCR/vision diff against the cited source
   image) to convert "internally consistent" into "verified against source" — this is the
   shortest path in the pool from proxy to ground-truth check.

2. **11's Genre-Scope Fidelity (generation claim ⇒ verifiable accession).** The pool's most
   concretely falsifiable check: a claim ("generated in this study") is tied to an identifier with
   a checkable format. **To build:** replace the format-regex with a live registry resolution call
   (GEO/SRA/dbGaP/PROSPERO lookup) confirming the accession exists and its access tier matches the
   claim — turns "looks like a real ID" into "is a real ID," closing the tournament's most-cited
   residual gap.

3. **07's Assumption→Consequence Traceability.** The clearest signal of genuine epistemic effort
   (not just presence, but examination) in the pool. **To build:** needs semantic (not lexical)
   matching between an assumption and its stated consequence — an LLM-judge pass confirming the
   consequence text actually describes a causal failure mode of *that* assumption, not just shared
   vocabulary, would close the largest remaining gap (a fluent compiler can currently satisfy the
   entity+failure-cue regex without real reasoning).

4. **02's Grounding Fidelity + Dependency Graph Integrity, cross-referenced against 09's evidence
   layer.** Individually these are within-artifact checks; combined across artifacts (claims'
   cited quotes checked against evidence/'s filed tables, not just claims.md's own prose) they
   would close the tournament's most repeated specific hole — "value appears in its own quote"
   becoming "value appears in the actual cited table." **To build:** this requires the
   multi-artifact cross-referencing every judge said was "outside this function's scope" — i.e.,
   promoting several of these from single-file metrics to whole-ARA metrics.

**General prerequisite across all four:** every judge names the same missing ingredient —
*external verification* (a live registry, the source PDF/screenshot, a cross-artifact claim
ledger, or a calibration set of human-labeled strong/weak ARAs). Until that layer exists, the
tournament's best output is a well-engineered, mutually-reinforcing family of **compilation-honesty
and internal-coherence detectors** — genuinely useful for catching lazy or templated extraction,
but explicitly not a measure of whether the underlying science is good.
