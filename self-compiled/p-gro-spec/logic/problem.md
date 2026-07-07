# Problem: observations and gaps

## Observations — what prior artifact formats fail to afford (each layer's stated "Kills")

### O01: Load-bearing numbers get re-typed and drift
Prior formats let one number be re-typed up to four times across prose/table/abstract/discussion; reconciliation then degrades to fuzzy string-matching of copies rather than a single canonical value.
> "one load-bearing number re-typed up to four times; reconciliation degraded to fuzzy string-matching of copies" (L1 · QUANT)

### O02: Claims carry a status but no logical structure
Claims are prose with a `Status` field but no `claim_type`, no logical form, and no way to measure over-claiming (quantifier inflation vs. the underlying `n`).
> "claims are prose with a `Status` but no `claim_type`, no logical structure, no over-claim measurement" (L2 · CLAIMFOL)

### O03: Concepts/methods/variables are unmapped prose headings
Nothing binds a paper's named concepts, methods, and measures to a controlled vocabulary or gives them a stable, resolvable identity.
> "concepts/methods/variables are prose headings; nothing maps them to controlled vocabulary" (L3 · ENTITY)

### O04: The id system supports only existence binding
Ids let you say "this thing exists" but not express typed relations between claims, evidence, and experiments as a real graph.
> "the id system supported only *existence* binding" (L4 · EDGES)

### O05: Genre-conditional absence is silent, and domain is free text
When a paper's genre makes a slot inapplicable, that silently looks identical to an omission; "domain" is an unconstrained free-text field with no expectation table behind it.
> "genre-conditionality expressed as *silent absence*; `domain` free text" (L5 · GENRE)

### O06: Citations are format-checked, never resolved
DOIs and other citation ids live only in full related-work blocks; when present they are checked for well-formedness, never actually resolved against an external index.
> "DOIs live only in full related-work blocks; present DOIs are format-checked, not resolved" (L6 · REFGRAPH)

### O07: Registry accessions are trapped in prose and outcome-dropping is invisible
Resolvable trial/registry ids (NCT/CRD/GSE/phs) sit unlinked to claims in prose, are never checked against the issuing registry, and selective outcome-reporting between what was registered and what was reported is hidden.
> "resolvable ids trapped in prose, unlinked to claims, never checked against the issuing registry; outcome-dropping hidden between registered and reported" (L7 · REGISTRY)

### O08: Novelty judgement lacks the structured inputs it needs
A novelty judge needs contribution *kind*, a claimed *magnitude* over *named* prior work, and a temporally honest precedence neighborhood — none of which prior formats provide as typed data.
> "a novelty judge needs contribution *kind*, claimed *magnitude* over *named* prior work, and a temporally honest neighborhood" (L8 · NOVELANCHOR)

### O09: A presupposed `discipline` field has no owner
P1's cross-discipline funder proposition (percentile ranking across fields) rests on a `discipline` field that no layer in the pre-critique draft actually emitted.
> "P1's entire cross-discipline funder proposition rested on a `discipline` field no layer emitted" (must-fix #2)

### O10: The Tier-C judge apparatus is expensive with no stated scale accounting
Full P1–P4 judgement is costly per element, and the pre-critique draft did not state whether or how this apparatus was meant to scale to a large corpus.
> "The Tier-C apparatus is expensive: per GRO, roughly P1 ≥3 families × sealed-N runs; P2 J≥3 × R≥3... This does **not** scale to a hundred-thousand-paper corpus at full density" (must-fix #11)

## Gaps — what remains open or only partially closed in this revision

### G01: Class-C judgement is irreducibly semantic
No format change makes novelty, significance, entailment quality, assumption realism, or distance-from-optimum deterministic; GRO makes these reproducible and auditable, not computable.
> "No format change makes novelty, significance, entailment quality, assumption realism, or distance-from-optimum deterministic." (§7)

### G02: "Independence" is asserted pipeline-distinctness, not measured statistical decorrelation (outside one layer)
Every "independent" check in the system except L3 Arm A rests on asserted, not measured, decorrelation between LLM families, and cannot rule out shared-pretraining-corpus correlation.
> "L1 `external_fidelity`, L6 `semantic_review`, L7 `CorrespondenceAssessment`... rest on *asserted*, not measured, decorrelation. Only L3 Arm A... earns genuine decorrelation." (§7)

### G03: The compiler still selects what gets typed
Determinism cannot close the residual gaming surface of which numbers/claims/assumptions the compiler chooses to formalize; three Class-C blind-reconstruction passes bound but do not eliminate this.
> "The compiler selects the content that gets recomputed... they are Class-C, bounded by independent-labeler recall, not deterministic guarantees." (§7)

### G04: Genre-shopping residual for narrative genres
Purely narrative genres (empty anchor set) have no deterministic clear against genre-shopping, leaving a magnitude-bounded false-absence residual.
> "for purely narrative genres... there is no deterministic clear; a nonzero, magnitude-bounded false-absence residual remains" (§7)

### G05: Prior-art cap depends on neighborhood coverage
The undisclosed-prior-art cap only fires reliably when the predecessor is inside the `q_auto` neighborhood; temporal leakage is flagged not eliminated, and embedding-evasion is an open question.
> "burying an in-neighborhood predecessor is worthless; burying one the neighborhood misses or that leakage contaminates is not structurally prevented." (§7)

### G06: Outcome-switching detection bounded by registry joinability
M04 needs free-text extraction of planned outcomes plus, for numeric switches, a posted registry value that most PROSPERO/NCT records lack.
> "'publication-bias afforded' means 'afforded on the joinable fraction,' not universally." (§7)

### G07: Tier-C does not run at corpus scale
Only a tiered triage-plus-audit-sample execution model is proposed for corpus-scale deployment; screening bias in the cheap pre-filter is bounded by the audit sample, not eliminated.
> "Triage-screening bias (a cheap screener mis-skipping an edge) is a residual the audit sample bounds but does not eliminate." (§7)

### G08: No single cross-layer hash identity
Three-plus distinct hash/normalization regimes coexist by design; cross-layer identity is only by id reference, never by hash equality.
> "'Everything is pinned and hashed' means each surface is pinned under *its* regime, not that one hash spans them." (§7)
