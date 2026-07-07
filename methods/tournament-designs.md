# Tournament Designs — Per-Gap Winning Proposals

Raw outputs of the 12 per-gap design tournaments (run `wf_f0bc615b-a88`). Each gap ran 4 proposers (2 GPT-5.5/codex, 2 Sonnet), a Fable meta-science judge that picked the best two and critiqued them, and a refine round where the finalists hardened their designs and stole each other's best ideas. The final review gate and the synthesis pass were cut off by an account rate limit; the synthesis was completed separately (see `IDEAL_FORMAT_SPEC.md`). This file preserves the finalist designs verbatim-structured.

**Legend:** finalists shown are the hardened *v2* designs where the refine round completed; for VALIDITY and HARDSIGNALS the refine round was cut off, so the judge-selected *proposals* are shown instead.

---


## QUANT — Typed quantity + provenance ledger

_Class A — format-recoverable determinism_


**Judge rationale:** All four converge on the same correct core (a typed quantity ledger with Q## ids, structured provenance anchors replacing the `value ← «quote» [tag]` prose DSL, and consuming layers referencing by id). So judging turns on execution: rigor of the schema, how the prose↔ledger binding actually works, honesty about fabrication surfaces, and whether the load-bearing/self-certification Goodhart holes are closed. I verified the live target metrics (extractive_fidelity, grounding_trust, semantic_grounding) to anchor this.\n\nTwo binding strategies emerged: (a) RENDER — prose contains a macro {{q:Q001}} that is generated from the ledger, so the literal cannot diverge (#0, #1); (b) TAG — prose keeps a hand-typed literal plus an inline pointer, checked against the ledger (#2, #3). Rendering gives stronger prevention but requires a pipeline and turns unrendered source files into macro soup, and both #0/#1 leave the 'which numbers are load-bearing' decision and the self-certifying verification_state unaddressed.\n\n#3 wins because it is the only design with measurement-theory sophistication that maps 1:1 onto the metrics: format_spec as a declared deterministic render function, baseline_ref vs comparator_value, derivation tolerance, checksum-based drift detection, an auto-set (never hand-authored) disputed status, and an explicit coverage audit. #2 wins the second slot on implementability + honesty: no pipeline, the concrete raw_repr byte-check, the sidecar table binding, the unbound-cell defect, and the Quantities self-check list are the most direct attacks on the not-anchored loophole, and it is candid about its tradeoffs.\n\n#0 edges #1 (its obligation enum must_match / may_differ_with_derivation and the quantity_links join table add real determinism semantics) but both are near-duplicate macro-render designs that under-specify load-bearing coverage and lean on self-certified verification_state — the exact thing the fidelity metric refuses to trust. Critically, EVERY proposal shares one unclosed hole worth forcing: a ledger can be internally byte-perfect and still fabricate relative to the paper; internal reconciliation must be renamed and separated from external, independently-checked fidelity. #3 and #2 are the two best positioned to absorb that fix.


### Finalist A (refined)

> _Judge critique it answered:_ CRITIQUE OF #3 (The Quantity Ledger, Claude Sonnet 5) — the most measurement-literate of the four, and the winner. It earns that by details the others lack: format_spec as a declared deterministic render function, baseline_ref vs comparator_value (a real threshold-vs-quantity distinction most designs collapse), derivation with abs/rel tolerance, checksum-on-anchor to detect evidence drift, a coverage audit to attack the not-anchored loophole, and status:disputed set automatically by reconciliation rather than hand-authored. But it has exploitable seams you must close:\n\n1. FABRICATION SURFACE — status:grounded self-certifies. Your `status` field ships `grounded`, and your source_anchor carries a compiler-authored `quote` + `checksum`. But the actual extractive_fidelity metric on disk (research/metrics/v3/extractive_fidelity.py) DELIBERATELY refuses to trust the compiler's own quoted «Sources»: it runs an independent adversarial pass against fulltext/<slug>.txt because 'a compiler could cite a quote that doesn't actually appear in, or support, the paper.' Your checksum only proves the evidence FILE didn't change since compile — it says nothing about fidelity to the paper. So a ledger can be byte-perfectly internally reconciled, every ⟦Q07⟧ matching, status:grounded everywhere, and still fabricate the number relative to the source. Rename the field: this is `internally_reconciled`, not `grounded`. Add a separate `external_fidelity: {state, checked_by, pass_id}` that ONLY an independent pass can set, and make the coverage audit refuse to call the ledger grounded until that external field is populated. As written you have built a beautiful, self-consistent fabrication surface.\n\n2. RENDER-VS-TOKEN AMBIGUITY. Your summary says prose 'carries an inline anchor token next to a value that is rendered by a pure deterministic function of the ledger record' — then reconciliation is 'byte-comparison of ledger-rendered vs embedded text.' Pick one and specify it to the bit. If the number is hand-authored and then byte-compared, define the canonical render function completely: rounding mode (half-even? half-up?), trailing-zero policy, the ci_style template grammar, negative/scientific formatting. 'decimals: 2, style: plain' does not determine whether 0.1 renders as 0.10 or 0.1 — and that single ambiguity reintroduces the exact string-mismatch noise you claim to kill.\n\n3. THE ORDINAL PUNT UNDERCUTS YOUR OWN EXAMPLE. value_kind ordinal/categorical is deferred to a 'v1 extension point, not required.' But your flagship example is a P-score RANKING (Q07, rank-1 of a ranked comparison set) — the amyloid case is fundamentally ordinal. Comparator/direction semantics for ranks (rank 1 is 'better' but the P-score is a continuous surrogate for order) are precisely where number_mismatch vs polarity_inversion errors live. Do not defer the case your example depends on.\n\n4. LOAD-BEARING IS UNDEFINED — THE REAL GOODHART HOLE. The coverage audit 'closes the obvious loophole of simply not anchoring a number,' but you never specify HOW load-bearing-ness is decided or by whom. A numeral regex over-flags (n=, page numbers, years, CI bounds) and under-specifies judgment calls; any contested number can be quietly dropped or declared non-load-bearing. Give the coverage audit an explicit decision procedure and an adversarial (non-author) executor, or it is theater.\n\n5. registry fetch_status: unresolved_registry_down is indistinguishable from never-attempted. Without a timestamp + attempt log it becomes a permanent honest-looking dodge for publication-bias comparison. Require a fetch attempt record.

**CQL-RAB — Canonical Quantity Ledger with Rounding-Aware Binding and Independent Fidelity Audit**  ·  _source: claude-opus-4-8_

Every load-bearing number is authored exactly once in logic/quantities.yaml as a typed record whose numeric truth is a single canonical `value` (full precision) plus structured `uncertainty` — and NOTHING is stored as a frozen printed string. Prose, tables, and trees keep their own context-appropriate rendering (0.859, 0.86, ~0.86 are all legal) and carry an inline tag `[[Q:Q01]]`; the validator does not byte-compare, it parses the printed literal to (number, printed_precision) and asserts round(value, printed_precision) == printed_number — deterministic AND rounding-correct. This closes the near-fatal byte-check flaw, eliminates the duplicated raw_repr field, and is honest that Class-A determinism here means *guaranteed detection* of divergence (with an opt-in generated-mention mode for authors who want prevention). Two things the ledger deliberately does NOT self-certify are pushed to independent passes stored in separate files: (a) extractive fidelity — an independent extraction agent re-fetches each anchor by checksum+line_range and re-derives the value, so the metric never trusts the compiler's own quote or a self-graded confidence enum; and (b) a closed-vocabulary numeral-coverage audit that replaces the unaudited non_load_bearing escape hatch. Provenance is fully structured (file, typed locator, verbatim quote, line_range, checksum) — the prose micro-DSL is gone.

- **logic/quantities.yaml — canonical typed quantity ledger** (YAML, top-level key `quantities:` — list of records, id-scoped within the ARA (Q01..), globally addressable as <ara_id>#Q01.) — Single source of numeric truth for every load-bearing fact. Numeric value stored ONCE as a full-precision number; no frozen printed string; provenance and type stored once. All other layers reference by id.
  - fields: id: string Q{NN} — required. label: string — required — human search label, explicitly NOT load-bearing, never metric-scored. value: number|null — required — canonical full-precision numeric truth (null only with value_null_reason). value_null_reason: enum{not_reported,not_applicable,qualitative_only}|null — required-if-null. value_kind: enum{numeric,ordinal,categorical} — required. unit: {code: string, na: bool} — required — na:true for dimensionless; object never omitted. uncertainty: {type: enum{ci,se,sd,iqr,range,none}, lower: number|null, upper: number|null, level: number|null, reported: bool, reason: string|null} — required — reported:false+reason is the honest-absence path, scored EQUAL to a filled CI. comparator: enum{eq,gt,lt,gte,lte,approx,range,none} — required. comparator_value: number|null — optional — fixed threshold (0, 0.05) when comparing to a constant. baseline_ref: QID|null — optional — other ledger entry this is a delta/ratio against. direction: enum{higher_better,lower_better,neutral,context_dependent,not_specified} — required — not_specified is honest, never fabricate. role: enum{input,result} — required. derivation: {kind: enum{primary,computed}, derived_from: [QID], formula: string|null, tolerance: {abs: number, rel: number}}|null — required — computed entries must supply formula+tolerance. format_spec: {decimals: int|null, sig_figs: int|null, style: enum{plain,percent,scientific}, ci_style: string|null} — required — DEFAULT rendering only; does NOT constrain per-mention precision. subject_entity: ENT-id|null — optional — sibling entity ledger xref. measures_concept: [CPT-id] — optional — sibling concept xref. produced_by_experiment: E-id|null — optional. registry_ref: {registry: string, accession: string, registered_as: string, registered_value: number|null, fetch_status: enum{resolved_match,resolved_divergent,resolved_no_data,unresolved_registry_down,not_applicable}}|null — optional — publication-bias join key. source_anchor: ProvenanceAnchor — required, non-null. status: enum{grounded,pending,disputed} — required — 'disputed' is set AUTOMATICALLY by a failed reconciliation or a failed independent-fidelity check, never hand-authored. used_by: [{layer,id,field}] — derived, recomputed by validator, never hand-maintained.
  - example: quantities:
  - id: Q01
    label: "p217_MS P-score, Abeta positivity ranking (Table 2, Outcome 1)"
    value: 0.859
    value_kind: numeric
    unit: { code: dimensionless, na: true }
    uncertainty: { type: none, lower: null, upper: null, level: null, reported: false, reason: "individual P-scores in Table 2 reported without CIs" }
    comparator: none
    comparator_value: null
    baseline_ref: null
    direction: higher_better
    role: result
    derivation: { kind: primary, derived_from: [], formula: null, tolerance: { abs: 0.0, rel: 0.0 } }
    format_spec: { decimals: 3, sig_figs: null, style: plain, ci_style: null }
    subject_entity: ENT:p217_MS
    measures_concept: [CPT:p_score]
    produced_by_experiment: E01
    registry_ref: null
    source_anchor:
      file: evidence/tables/table2.md
      locator: { kind: table_cell, table: "Table 2", outcome: "Outcome 1", rank: 1 }
      quote: "p217_MS (0.859)"
      line_range: { start: 14, end: 14 }
      checksum: "sha256:3f9a1c…"
    status: grounded
  - id: Q12
    label: "incremental AUC gain, ratio vs single analyte (Table S2 row 4)"
    value: 0.025
    value_kind: numeric
    unit: { code: AUC_units, na: false }
    uncertainty: { type: ci, lower: 0.005, upper: 0.045, level: 0.95, reported: true, reason: null }
    comparator: gt
    comparator_value: 0
    baseline_ref: null
    direction: higher_better
    role: result
    derivation: { kind: computed, derived_from: [Q10, Q11], formula: "Q10 - Q11", tolerance: { abs: 0.001, rel: 0.0 } }
    format_spec: { decimals: 3, sig_figs: null, style: plain, ci_style: "95% CI {lower}-{upper}" }
    subject_entity: ENT:ratio_model
    measures_concept: [CPT:auc_incremental_gain]
    produced_by_experiment: E01
    registry_ref: null
    source_anchor:
      file: evidence/tables/table_s2.md
      locator: { kind: table_cell, table: "Supplementary Table S2", row: 4 }
      quote: "incremental AUC gain 0.025 (95% CI 0.005-0.045); I2 = 0%"
      line_range: { start: 8, end: 8 }
      checksum: "sha256:9c1e77…"
    status: grounded
- **Inline Quantity Tag — rounding-aware prose↔ledger binding** (Markdown inline token immediately following the printed literal: `[[Q:<qid>]]` for a scalar, `[[Q:<qid>#<field>]]` to target a component (value|ci.lower|ci.upper), `[[Q:<qid>#full]]` for a value+uncertainty expression rendered as one span. Optional generated form `{{Q:<qid>}}` is expanded by a pre-commit filter into `<rendered> [[Q:<qid>]]` (prevention mode). A companion `Quantities: [qid,...]` self-check list on each block must equal the set of tagged QIDs in that block.) — Keeps prose fully human-readable with context-appropriate rounding while making every printed literal deterministically checkable against the canonical value. Replaces the byte-check with a round-to-printed-precision check, so the same fact may legitimately appear as 0.859 / 0.86 / ~0.86 in different layers and all pass.
  - fields: tag: string, pattern `\[\[Q:[A-Za-z0-9_#.]+\]\]` — required immediately after any load-bearing numeral. field_path: enum{value(default),ci.lower,ci.upper,full} — optional, after `#`. Quantities: [QID] — required on any block with >=1 tag; validated to equal the tagged set (missing/extra QID is a structural defect).
  - example: Statement: "...p217_MS achieved the highest rank (P-score = 0.859 [[Q:Q01]]); in the abstract we round this to 0.86 [[Q:Q01]]. The ratio added an incremental AUC gain of 0.025 (95% CI 0.005-0.045) [[Q:Q12#full]], and approximately ~0.03 [[Q:Q12]] in the discussion."
Quantities: [Q01, Q12]
# Validator: round(0.859,3)=0.859 OK; round(0.859,2)=0.86 OK; Q12#full renders each token and rounds; round(0.025,2)=0.03 OK for ~0.03.
- **evidence/**/{name}.qids.yaml — cell / datapoint binding sidecar** (YAML sidecar, same basename as the evidence .md, suffixed .qids.yaml.) — Binds specific table cells and figure datapoints to QIDs without polluting the human-readable markdown table. One sidecar per evidence file with a load-bearing cell.
  - fields: bindings: [ {row: string|int, column: string, qid: QID} ] — required. Every cell in the parent table/figure containing a numeral must have exactly one binding OR be classified in numeral_exceptions; an unbound numeric cell is an 'unbound cell' defect. datapoint bindings use {series, x, y_qid} for figures.
  - example: # evidence/tables/table2.qids.yaml
bindings:
  - { row: "Rank 1 (p217_MS)", column: "Outcome 1: Abeta accuracy", qid: Q01 }
  - { row: "Rank 8 (p181_IA)", column: "Outcome 1: Abeta accuracy", qid: Q08 }
- **logic/quantity_audit.yaml — INDEPENDENT extractive-fidelity record** (YAML, top-level `audits:` — one record per QID, written by the verifier role, checksum-signed.) — The grounding arbiter. Produced by an extraction pass INDEPENDENT of the compiler (different agent/tool). Re-fetches each anchor by file+line_range+checksum and re-derives the value and quote adversarially. The extractive_fidelity metric trusts ONLY this file — never the compiler's own source_anchor.quote and never any self-graded confidence.
  - fields: qid: QID — required. verifier_id: string — required — identity/tooling of the independent pass, must differ from the compiler id. fetched_checksum: string — required — checksum of the target file AT AUDIT TIME; mismatch with ledger checksum → status stale. independent_value: number|null — required — value re-extracted from the anchored location without reading the ledger's value. value_matches: bool — required — independent_value reconciles with ledger value within derivation tolerance (or 0.5 ULP for primary). quote_reproduced: bool — required — the ledger's quote is a verbatim substring at the anchored line_range. quote_actual: string — required — what the verifier actually read at that locus (may differ). method: enum{text_exact,table_parse,figure_digitized,recomputed,not_verifiable} — required. disagreement: string|null — required-if any match is false — free text describing the divergence. audited_at: iso8601 — required.
  - example: audits:
  - qid: Q01
    verifier_id: "extract-agent-v2 (independent)"
    fetched_checksum: "sha256:3f9a1c…"
    independent_value: 0.859
    value_matches: true
    quote_reproduced: true
    quote_actual: "p217_MS (0.859)"
    method: table_parse
    disagreement: null
    audited_at: 2026-07-06T10:22:00Z
  - qid: Q12
    verifier_id: "extract-agent-v2 (independent)"
    fetched_checksum: "sha256:9c1e77…"
    independent_value: 0.025
    value_matches: true
    quote_reproduced: false
    quote_actual: "incremental AUC gain 0.025 (95% CI 0.005 to 0.045)"
    method: table_parse
    disagreement: "ledger quote uses hyphen '0.005-0.045'; source prints '0.005 to 0.045'. Value fidelity intact; verbatim quote slightly paraphrased."
    audited_at: 2026-07-06T10:22:04Z
- **logic/numeral_coverage.yaml — closed-vocabulary coverage audit** (YAML: a closed vocabulary + a machine-generated coverage report + a hand-authored exceptions list.) — Replaces the unaudited non_load_bearing boolean. Defines what 'load-bearing' means and forces every numeral in prose/tables/figures to be either tagged, matched by a structural non-load-bearing pattern, or an explicitly categorized exception that an independent pass re-challenges.
  - fields: load_bearing_classes: fixed set {result_value, input_value, effect_size, uncertainty_bound, sample_size_n, threshold, model_hyperparameter} — MUST be tagged. non_load_bearing_classes: fixed set {citation_year, page_number, section_number, figure_number, table_number, equation_number, enumeration_index, date, version_string, doi_fragment} — each has a required structural_pattern regex/context rule. numeral_exceptions: [ {locus: {file,line}, literal: string, class: <non_load_bearing_class>, justification: string} ] — required for any numeral not auto-matched. coverage_report: {total_numerals:int, tagged:int, pattern_matched:int, exception_listed:int, UNRESOLVED:int} — machine-generated; UNRESOLVED>0 is a hard defect. challenged: [ {locus, verifier_id, verdict: enum{upheld,reclassified_load_bearing}} ] — written by the independent coverage-challenge pass.
  - example: load_bearing_classes: [result_value, input_value, effect_size, uncertainty_bound, sample_size_n, threshold, model_hyperparameter]
non_load_bearing_classes:
  - { class: citation_year, structural_pattern: "must be inside a [[R:...]] ref anchor span" }
  - { class: page_number, structural_pattern: "\\bp\\.?\\s*\\d+" }
numeral_exceptions:
  - { locus: {file: logic/claims.md, line: 40}, literal: "2024", class: citation_year, justification: "publication year of ref R07, inside [[R:R07]]" }
coverage_report: { total_numerals: 61, tagged: 52, pattern_matched: 8, exception_listed: 1, UNRESOLVED: 0 }
challenged:
  - { locus: {file: logic/claims.md, line: 40}, verifier_id: "coverage-challenge-v1", verdict: upheld }
- **logic/claims.md — revised claim block (Quantities replaces Sources)** (typed-markdown, existing ## C{NN} convention, **Sources** replaced by **Quantities**.) — Removes the value ← ref «quote» [tag] micro-DSL. A claim lists the ledger entries it depends on and tags them inline; provenance lives once in the ledger.
  - fields: Quantities: [QID] — required on any claim with >=1 numeral in Statement/Evidence basis/Interpretation. Statement/Evidence numerals carry inline tags per the binding convention. All other claim fields unchanged.
  - example: ## C01: p-tau217 by mass spectrometry has the highest diagnostic accuracy for Abeta pathology
- **Statement**: p217_MS achieved the highest rank (P-score = 0.859 [[Q:Q01]]); p181_IA ranked last (0.117 [[Q:Q08]]); mean AUC difference MD = 0.10 (95% CI 0.04-0.16) [[Q:Q05#full]].
- **Status**: supported
- **Falsification criteria**: p217_MS P-score not > 0.783 [[Q:Q02]] on re-analysis.
- **Evidence basis**: Table 2 Outcome 1 (0.859 [[Q:Q01]] > ... > 0.117 [[Q:Q08]]); Figure 3A forest plot MD [[Q:Q05]].
- **Quantities**: [Q01, Q02, Q05, Q08]
- **Dependencies**: none

  _Protocols:_
  - **Rounding-aware reconciliation (Class A — deterministic)** — Every validation run; whenever a tagged literal must be checked against the ledger.. 1. For each inline tag `<literal> [[Q:qid#field]]`: lex the immediately preceding literal into (printed_number, printed_precision) where precision = decimal places (or sig figs if scientific/integer). 2. Resolve target = ledger[qid].<field> (default .value). 3. Assert round_half_even(target, printed_precision) == printed_number — exact equality AFTER rounding to the printed precision. 4. For `#full`, render target via format_spec.ci_style, tokenize both rendered and printed spans, apply steps 1-3 per numeric token pairwise. 5. Check comparator/sign markers (~,<,>) against ledger.comparator; mismatch → warning. 6. On any assertion failure set ledger[qid].status=disputed automatically. 7. Validate each block's Quantities: list equals its tagged QID set.
    - reliability/reproducibility: Fully deterministic: identical inputs → identical verdict, no LLM, no thresholds to tune. Precision is READ from the print, so the tolerance cannot be authored loose.
    - constraints: Tooling must provide a numeric lexer that recovers printed precision (decimals and sig figs), a round_half_even implementation, and a format_spec renderer. Locale decimal separators normalized before lexing.
  - **Generated-mention expansion (Class A — optional prevention mode)** — Authors who want prevention rather than detection; high-stakes venues.. 1. Author writes `{{Q:qid}}` or `{{Q:qid|d2}}` (precision override) instead of a literal. 2. Pre-commit filter renders ledger[qid].value via format_spec (or the override precision) and rewrites in place to `<rendered> [[Q:qid]]`. 3. The rewritten file is what is committed and read by humans; the number now cannot diverge because it was generated from the canonical value. 4. Reconciliation still runs and is a no-op-true on generated mentions, so detection and prevention coexist.
    - reliability/reproducibility: Deterministic expansion; idempotent (re-running yields identical output). No mandatory pipeline for detection-mode authors.
    - constraints: Filter must be a pure function of the ledger; must refuse to expand a `{{}}` whose qid is missing or whose value is null.
  - **Independent extractive-fidelity pass (Class B — reliability)** — Sealing an ARA; any grounding/fidelity metric; whenever an evidence checksum changes.. 1. A verifier agent DISTINCT from the compiler iterates ledger records. 2. For each, open source_anchor.file at line_range, recompute checksum. 3. Without reading ledger.value, independently extract the value at that locus (text/table/figure-digitize/recompute). 4. Write quantity_audit.yaml: independent_value, value_matches (within derivation tolerance / 0.5 ULP), quote_reproduced (verbatim-substring test), quote_actual, method, disagreement. 5. Any value_matches:false → ledger.status=disputed. 6. Stale checksum → flag, do not silently pass.
    - reliability/reproducibility: Reliability, not determinism: figure digitization and table parsing vary. Mitigations — checksum+line_range make the re-fetch locus exact; two independent verifiers can be ensembled and disagreement surfaced; value_matches is a tolerance test, not a byte test, so benign formatting differs without failing. quote_reproduced is a mechanical substring test (deterministic) separate from value extraction (reliable).
    - constraints: Ecosystem must provide: an extraction agent independent of the compiler, a figure-digitization tool with reported error bars, checksummed immutable evidence files, and identity separation so the compiler cannot author its own audit.
  - **Adversarial numeral-coverage audit (Class B — reliability)** — Sealing; any grounding-coverage metric; catches the 'just don't tag it' loophole.. 1. Regex-scan every numeral across prose, table cells, figure captions, tree result strings. 2. Classify each: tagged? matches a non_load_bearing structural_pattern? listed in numeral_exceptions with a closed-vocab class? 3. Any numeral in none of those → UNRESOLVED (hard defect). 4. An INDEPENDENT challenge pass re-reads each numeral_exception and each pattern_matched item and votes upheld / reclassified_load_bearing. 5. Any reclassification forces a tag or fails the seal.
    - reliability/reproducibility: The scan+classification is deterministic; the adversarial challenge of exceptions is reliability (semantic judgment of 'is this really non-load-bearing'), minimized by the closed vocabulary and structural patterns so the judge has few degrees of freedom.
    - constraints: Closed non_load_bearing vocabulary with a structural_pattern per class; an independent challenger; a numeral lexer that does not miss ranges, percentages, or scientific notation.
  - **Registry resolution & publication-bias join (Class B — reliability)** — Any result quantity with a pre-registration; funder-facing bias metrics.. 1. For each ledger record with registry_ref, fetch the accession from the named registry. 2. Compare registered_value/registered_as against value+direction. 3. Set fetch_status ∈ {resolved_match, resolved_divergent, resolved_no_data, unresolved_registry_down, not_applicable}. 4. resolved_divergent surfaces as a first-class outcome-switching signal, NOT a penalty for honest reporting of divergence.
    - reliability/reproducibility: Registry availability varies run-to-run; unresolved_registry_down is a distinct honest state, never conflated with 'no registration' or 'match'. Cache resolved records with fetch timestamp for reproducibility.
    - constraints: Ecosystem must provide registry APIs/mirrors and a stable accession→outcome mapping.

  _Metrics afforded:_
  - Cross-layer numeric reconciliation (does every printed number match the canonical value at its own precision) → Rounding-aware reconciliation protocol over all inline tags: round(value, printed_precision)==printed_number for each mention; count passes / total tagged mentions. [deterministic]; anti-Goodhart: Cannot be gamed by printing identical strings everywhere (that is no longer required) nor by declaring a loose tolerance (tolerance is READ from the printed precision, not authored). Padding prose with more tagged numbers only adds more exact checks, each of which can fail; it cannot inflate the score.
  - Grounding coverage (fraction of load-bearing numerals bound to the ledger) → numeral_coverage.yaml coverage_report: (tagged) / (tagged + UNRESOLVED among load-bearing classes); UNRESOLVED>0 hard-fails the seal. [reliable-anchored]; anti-Goodhart: The old escape hatch is closed: you cannot mark a number non-load-bearing at will. Exceptions must cite a closed-vocab class with a structural pattern and survive an independent challenge pass that can reclassify. Not-anchoring a number surfaces as UNRESOLVED rather than silently disappearing.
  - Extractive fidelity (does the anchored source actually contain the value/quote) → From logic/quantity_audit.yaml only: fraction with value_matches AND quote_reproduced, produced by an independent re-extraction pass; the compiler's own quote and any self-grade are ignored. [reliable-anchored]; anti-Goodhart: Self-certification is impossible because the arbiter is a different agent that never reads ledger.value before extracting. A fabricated-but-internally-consistent quote fails when the independent pass reads the actual locus. Verifier identity must differ from compiler identity, blocking self-audit.
  - Self-consistency / derivation recompute (do computed quantities equal their formula over operands) → For each derivation.kind==computed: evaluate formula over derived_from values; assert |result - value| <= tolerance.abs OR rel; count passes. [deterministic]; anti-Goodhart: Consistency is checked by arithmetic, not by matching prose. An author cannot pad with fabricated-consistent numbers because each computed value is recomputed from its cited operands; a fabricated operand chain must itself reconcile and be independently fidelity-audited at its own anchor.
  - Publication-bias / outcome-switching (does the result diverge from pre-registration) → Registry resolution protocol: distribution of fetch_status across result quantities; resolved_divergent flagged for review. [reliable-anchored]; anti-Goodhart: resolved_divergent is a transparency signal, not a penalty for honestly reporting divergence, so authors are not pressured to hide it. not_applicable and unresolved_registry_down are distinct honest states, so 'no registry' cannot masquerade as 'match'.
  - Honest-absence rate (fraction of null/not_reported/not_specified fields) → Count of first-class null values (value_null_reason, uncertainty.reported:false, direction:not_specified, registry not_applicable) over total slots; reported, never penalized. [deterministic]; anti-Goodhart: Scored EQUAL to honest presence — a not_reported CI with a reason costs nothing versus a filled CI, so typed slots create zero pressure to fabricate. Fabricating a specific CI to avoid a null is instead exposed by the extractive-fidelity pass, which will find no CI at the anchor.

  _Tradeoffs:_ HONEST posture — this is DETECTION by default, not prevention. The number is still typed by a human at each mention; the ledger guarantees we CATCH any divergence deterministically, but divergence can be introduced before it is caught. Residual per-mention burden: one tag (~1 token) plus re-typing the numeral (never its unit/type/uncertainty/provenance — those are typed once). We justify detection as the default on readability (prose stays literally readable), zero mandatory pipeline, and the fact that the rendering approaches secretly still embed a literal and inherit the same rounding problem unless they carry per-mention precision — which they do not; prevention is available as an opt-in {{Q:}} filter for those who want it.
FABRICATION SURFACES and mitigations: (a) A fabricated-consistent value that reconciles across all layers — mitigated by the independent extractive-fidelity pass that reads the actual source, not the ledger. (b) Gaming coverage by mislabeling a result as citation_year — mitigated by structural_pattern rules plus the adversarial challenge pass. (c) A loose derivation tolerance to pass recompute — visible in the record and boundable by policy; abnormally large tolerances are auditable. (d) Checksum drift (evidence file changes after grounding) — surfaced as stale, not silently passed.
COSTS: authoring overhead of the ledger and per-mention tags; the ecosystem must supply an independent extraction agent, figure-digitization tooling, checksummed evidence, and registry access — this design assumes the 'everyone publishes fully' world. Ordinal/categorical quantities are a v1 extension point (value_kind carries them, but reconciliation is defined for numeric).
RISK: rounding-aware equality can theoretically accept a wrong number that happens to round to the printed value at low precision (e.g., an abstract's single-sig-fig 0.9 accepts 0.859 or 0.94). Mitigation: the highest-precision mention (usually the table) is checked at full precision and is the one the extractive-fidelity pass re-derives, so a low-precision mention cannot hide a wrong canonical value.

  _Open questions:_ 1. Rounding rule edge cases: sig-figs vs decimal-places inference from a bare literal (is '100' 1, 2, or 3 sig figs?), banker's vs arithmetic rounding conventions across fields, and locale decimal/grouping separators — need a canonical, documented lexing spec. 2. How much independent-extraction disagreement is tolerable before a quantity is 'disputed' vs merely 'formatting-divergent' — the value/quote split helps but the threshold policy is unsettled. 3. Figure-digitization fidelity: the independent pass on a plotted datapoint has real error; how to represent and score digitization uncertainty as first-class rather than a binary match. 4. Load-bearing boundary cases: is a narrative sample size ('we enrolled 240 patients') always load-bearing? The closed vocab helps but the boundary for descriptive-vs-result counts needs field-specific calibration. 5. Whether resolved_divergent should feed a positive transparency credit (rewarding honest disclosure of registration divergence) without becoming its own gameable metric. 6. Compound-mention rendering for exotic uncertainty formats (asymmetric CIs, ± with units, log-scale) — the ci_style template may not cover all conventions.

  _Changes from critique:_ FIX 1 (near-fatal, byte-check vs rounding): Removed raw_repr entirely. Numeric truth is a single canonical `value: number` at full precision plus `format_spec` for the ledger's own default rendering. Reconciliation is no longer byte-equality of a frozen string; it is: parse the printed literal to (printed_number, printed_precision), then assert round_half_even(value, printed_precision) == printed_number. So the table's 0.859, the abstract's 0.86, and a claim's ~0.86 ALL pass deterministically against one canonical value — context-appropriate rounding is now correct authoring, not a false-positive failure. Tolerance is derived from the printed precision itself (0.5 ULP of the last printed place), never hand-declared per mention, so it cannot be gamed loose.
FIX 2 (raw_repr bundles value+CI and duplicates the structured field): Gone. There is exactly one numeric source of truth per component — `value`, and `uncertainty:{lower,upper,level}`. Value and CI can no longer silently disagree inside one record because neither is stored as a bundled string. A value+CI printed in one prose span is validated by a compound mention `[[Q:Q12#full]]` that renders from format_spec.ci_style and checks each numeric token by rounding; there is no second copy to drift.
FIX 3 (detection vs prevention honesty): Stated plainly. Default mode = DETECTION: the author types the number + tag, the validator guarantees catching any divergence. Residual authoring burden is quantified (one tag per load-bearing numeral, ~1 token; the number is typed once more per mention but never its provenance/type/unit). Added an OPT-IN PREVENTION mode: a `{{Q:Q01}}` render directive expanded by a pre-commit filter into `<rendered-literal> [[Q:Q01]]`, giving generation-time prevention for authors who want it, with zero mandatory pipeline for those who do not. Argument for why detection is the right default is made explicitly (readability, zero-pipeline, and that the rendering twins #0/#1 secretly still embed a literal and thus have the SAME rounding problem unless they carry per-mention precision — which they do not).
FIX 4 (non_load_bearing unaudited escape hatch): Deleted the free author-set boolean. Replaced with a closed numeral-class vocabulary and an adversarial coverage audit that scans EVERY numeral in prose (not just table cells): each numeral must be either tagged, or matched by a machine-checkable structural pattern for a non-load-bearing category (citation_year inside a ref anchor, page_number matching \bp\.?\s*\d+, etc.), or listed in numeral_exceptions with a category from the closed vocab that an independent pass re-challenges. 'Load-bearing' is now defined, not discretionary.
FIX 5 (self-certification): Removed reading_confidence and stopped trusting the compiler's quote for the fidelity metric. Added logic/quantity_audit.yaml, produced by an INDEPENDENT extraction pass (different agent/tool from the compiler) that re-fetches each anchor via checksum+line_range and re-derives the value+quote adversarially. The extractive_fidelity metric reads only that file. The compiler's quote is still stored for human search but is never the arbiter of grounding.

  _Adopted from competitor:_ 1. format_spec:{decimals, style, ci_style} as the ledger's canonical default renderer — I adopt it as the DEFAULT rendering only, decoupled from the per-mention rounding check (their version silently reintroduces the same rounding bug because a fixed decimals:3 render byte-compared to an abstract's 0.86 would fail). 2. Structured ProvenanceAnchor with line_range + checksum — adopted wholesale; checksum enables change-detection and makes the independent re-fetch deterministic. 3. registry_ref with a fetch_status enum (resolved_match / resolved_divergent / resolved_no_data / unresolved_registry_down / not_applicable) — adopted as the publication-bias join key with honest-absence built in. 4. status:{grounded,pending,disputed} set AUTOMATICALLY by a failed reconciliation, never hand-authored — adopted (removes a self-grade). 5. subject_entity + measures_concept cross-references to sibling entity/concept ledgers — adopted for interoperability. 6. derivation tolerance as {abs, rel} rather than a single scalar — adopted for the recompute check. 7. used_by back-references as DERIVED (recomputed by the validator), never hand-maintained — adopted.

  _Why it wins:_ The competitor claims prevention ('rendered by a pure deterministic function of the ledger record') but still embeds a rendered numeral next to ⟦Q07⟧ and reconciles by 'byte-comparison of ledger-rendered vs embedded text' — with a FIXED format_spec.decimals per id. That means the exact scientific reality the reviewer flagged (table 0.859, abstract 0.86, claim ~0.86) breaks the competitor too: three contexts, one decimals value, byte-compare fails two of them. My rounding-aware check (round(value, printed_precision) == printed_number) is the only mechanism in the field that is simultaneously deterministic AND correct under legitimate per-context rounding, and it needs no per-mention tolerance declaration to hand-tune (the printed precision IS the tolerance), so it cannot be gamed loose. Second, the competitor still lets grounding rest on a compiler-authored quote inside the same record; I route quote/value faithfulness to an independent re-extraction file the metric trusts instead. Third, the competitor's coverage audit is gestured at but its honest-absence still leaves 'just don't anchor a number' addressable only by an audit over an open set; I close it with a closed numeral-class vocabulary plus an adversarial re-challenge of every exception. Net: same interoperability and structured provenance, but the two things that actually decide whether the Class-A determinism claim survives contact with real papers — rounding and self-certification — are fixed rather than restated.


### Finalist B (refined)

> _Judge critique it answered:_ CRITIQUE OF #2 (QLTB, sonnet) — the most implementable and the most honest about its own tradeoffs, which is why it beats the two macro-rendering twins (#0/#1). No rendering pipeline, prose stays literally readable, the inline `0.859 [[Q:Q01]]` tag is a cheap deterministic join, the per-file `.qids.yaml` sidecar keeps markdown clean, and the 'unbound cell' defect plus the `Quantities:` self-check list are the sharpest not-anchored-loophole mechanisms in the field. But it has one near-fatal design error and several unclosed seams:\n\n1. NEAR-FATAL — BYTE-CHECK vs LEGITIMATE ROUNDING. Your validator 'byte-checks that the printed literal equals ledger[Q01].raw_repr,' and raw_repr is 'the exact printed form as it appears in the source.' Scientific prose legitimately prints the same fact at different precision in different contexts: the table says 0.859, the abstract says 0.86, a claim says ~0.86. Byte-equality FALSE-POSITIVES every one of these as a reconciliation failure — OR it forces every layer to print the identical string, which is itself scientifically wrong (context-appropriate rounding is correct authoring, not an error). You have no canonical-value + format_spec + per-mention tolerance separation (exactly what #3 has and you lack). Fix: store a canonical numeric `value` + precision, and check numeric equality within a declared rounding tolerance per mention, not byte equality of a frozen string. Until you do, your determinism claim is brittle to the most ordinary thing numbers do.\n\n2. raw_repr BUNDLES VALUE+CI AND DUPLICATES THE STRUCTURED FIELD. Your Q12 raw_repr is '0.025 (95% CI 0.005-0.045)' while you ALSO carry a structured uncertainty:{ci,lower,upper}. Now the same fact lives twice in ONE record, in two formats that can silently disagree — you have reintroduced the multi-transcription problem inside the ledger you built to kill it. Which is authoritative when raw_repr and the uncertainty object diverge? Specify it, or drop raw_repr in favor of value+precision+render-policy.\n\n3. BE HONEST THAT THIS IS DETECTION, NOT PREVENTION. The tag literal is still hand-typed in prose; the number CAN diverge, you just catch it. That is a legitimate and honest posture, but the Class-A mandate is determinism, and the rendering approaches (#0/#1) PREVENT divergence by generation. State plainly in the design that your determinism = guaranteed detection, quantify the residual per-mention authoring burden, and justify why detection beats prevention here (I think it does, on readability + zero-pipeline grounds — but make the argument explicitly instead of implying you 'killed' transcription).\n\n4. non_load_bearing:true IS AN UNAUDITED ESCAPE HATCH. An author dodges grounding entirely by marking an inconvenient numeral non-load-bearing. You need a definition of load-bearing and an adversarial coverage audit (you gesture at 'unbound cell' for tables but not for prose numerals generally).\n\n5. SELF-CERTIFICATION, SAME AS THE OTHERS. source_anchor.quote + reading_confidence:high is compiler-authored; the real extractive_fidelity metric refuses to trust the compiler's own quote and checks fulltext via an independent pass. reading_confidence is a self-grade the metric will ignore. Route quote-faithfulness to an external adversarial field, not an author-set confidence enum.

**The Quantity Ledger v2: internally-reconciled by construction, externally-graded by an independent pass**  ·  _source: Claude Sonnet 5 (v1 Quantity Ledger), improved by finalist A_

Every load-bearing number is authored exactly once in logic/quantities.yaml as a typed record; every prose/table/tree surface stops re-typing it and carries an inline anchor tag next to the printed literal. The v1 design already made cross-layer reconciliation, recompute, and publication-bias into exact joins over one key. v2 closes the five seams the reviewer named: (1) it splits the single self-certifying `status:grounded` into two orthogonal axes — a deterministic, compiler-set `reconcile_status` (do the ledger, the tags, and the render function all agree?) and a `external_fidelity` block that ONLY the independent adversarial extractive_fidelity pass on disk can populate (does the number actually appear in and get supported by fulltext/<slug>.txt?) — so a byte-perfect internal reconciliation can never masquerade as fidelity to the paper; (2) it pins the render function to the bit (round-half-even, fixed trailing decimals, an explicit ci_style template grammar) and makes the printed `raw_repr` a DERIVED, compile-verified value rather than a second hand-typed copy; (3) it promotes ordinal/rank quantities to a first-class ranking_ref structure with defined comparator/direction/polarity semantics, because the flagship amyloid example IS a ranking; (4) it gives the coverage audit an explicit numeral-disposition decision procedure executed by a non-author pass that enumerates EVERY numeral so nothing can be silently dropped; and (5) it replaces the ambiguous registry `unresolved_registry_down` with a structured fetch_log of timestamped attempts, so a permanent honest-looking dodge becomes visibly distinguishable from never-attempted. The concrete motivator is real: the corpus's own extractive_fidelity/che26 finding flags MD=0.10 (95% CI 0.04-0.16) for p217_MS vs p181_IA as an unsupported_addition — the v1 design would have shipped exactly that number as status:grounded.

- **Quantity Ledger record (v2)** (YAML, logic/quantities.yaml, top-level key `quantities:`) — The single canonical typed representation of one load-bearing numeric fact, now with the grounding status split into a deterministic internal-reconciliation axis and an independently-set external-fidelity axis so internal consistency can never be mistaken for fidelity to the paper.
  - fields: id: string Q{NN} — required — within-ARA key; globally addressable as <ara_id>#Q{NN}.
label: string — required — human label, not load-bearing.
subject_entity: entity-id — optional — sibling entity ledger anchor.
value: number|null — required — canonical value (null only with an honest uncertainty/absence reason); never re-typed elsewhere.
value_type: enum{scalar,count,percentage,ratio,rate,ordinal_rank,duration,monetary} — required (adopted from competitor).
value_kind: enum{numeric,ordinal,categorical} — required — ordinal is NOW first-class (see ranking_ref).
unit: {code:string, na:bool} — required — na:true for dimensionless; object never omitted.
uncertainty: {type:enum{CI95,CI90,SD,SE,IQR,range,none}, lower:number|null, upper:number|null, reported:bool, reason:string|null} — required — reported:false+reason is the honest-absence path, scored equal to a filled CI.
comparator: enum{gt,lt,gte,lte,eq,approx,none} — required.
comparator_value: number|null — optional — fixed threshold (0, 0.05) when not comparing to another quantity.
baseline_ref: quantity-id|null — optional — the other ledger entry this is a delta/ratio against.
ranking_ref: {ranking_id:string, rank:int, rank_polarity:enum{rank1_is_best,rank1_is_worst}, surrogate_is:enum{p_score,mean_rank,probability,none}}|null — required-if value_kind=ordinal, else null — makes ranks first-class; rank_polarity + surrogate_is fix the ordinal comparator/direction semantics.
direction: enum{higher_better,lower_better,neutral,context_dependent,not_specified} — required — not_specified is honest, never fabricated.
role: enum{input,result} — required — set vs produced.
derivation: {kind:enum{primary,computed}, derived_from:list[quantity-id], formula:string|null, tolerance:{abs:number,rel:number}} — required — computed entries must supply formula+tolerance for recompute.
extraction_method: enum{exact_from_labels,digitized_estimate,computed,not_verifiable} — required (adopted) — digitized_estimate is honest for figure reads.
reading_confidence: enum{high,medium,low} — required (adopted).
format_spec: {decimals:int, style:enum{plain,percent,scientific}, ci_style:string|null} — required — input to the canonical render function (see ProvenanceAnchor/render protocol).
raw_repr: string — required — DERIVED: must equal render(value,format_spec); compile fails if not. This is the byte-compare target for every consumer; it is NOT independently authored.
produced_by_experiment: experiment-id|null — optional.
registry_ref: RegistryRef object|null — optional — publication-bias join key with fetch_log (see below).
source_anchor: ProvenanceAnchor object — required, non-null.
reconcile_status: enum{internally_reconciled,pending,disputed} — required — DETERMINISTIC, set by validator: internally_reconciled iff every tag literal==raw_repr, raw_repr==render(value,format_spec), and all `computed` recomputes hold within tolerance; disputed is auto-set by a failed reconciliation, never hand-authored. Says NOTHING about the paper.
external_fidelity: {state:enum{faithful,unfaithful,unverifiable_no_fulltext,pending_no_pass}, checked_by_pass:string|null, pass_finding:string|null, claim_ref:string|null, infidelity_type:enum{number_mismatch,polarity_inversion,unsupported_addition}|null, paper_quote:string|null, checked_at:timestamp|null} — required — a compiler may ONLY write pending_no_pass; faithful/unfaithful/unverifiable_no_fulltext are writable exclusively by the independent adversarial pass keyed to research/metrics/v3/extractive_fidelity/<slug>.yaml. pending_no_pass and unverifiable_no_fulltext are honest-absence states scored EQUAL to faithful for author-honesty (you are not penalized for a paywalled paper), but the grounding metric reports them distinctly.
used_by: list[{layer,id,field}] — optional/derivable — back-references, recomputable.
  - example: quantities:
  - id: Q11
    label: "p217_MS vs p181_IA mean AUC difference (claimed, Figure 3A)"
    subject_entity: ENT:p217_MS
    value: 0.10
    value_type: scalar
    value_kind: numeric
    unit: { code: AUC_units, na: false }
    uncertainty: { type: CI95, lower: 0.04, upper: 0.16, reported: true, reason: null }
    comparator: gt
    comparator_value: 0
    baseline_ref: Q_p181_IA_auc
    ranking_ref: null
    direction: higher_better
    role: result
    derivation: { kind: primary, derived_from: [], formula: null, tolerance: { abs: 0.005, rel: 0.0 } }
    extraction_method: exact_from_labels
    reading_confidence: high
    format_spec: { decimals: 2, style: plain, ci_style: "{value} (95% CI {lower}-{upper})" }
    raw_repr: "0.10 (95% CI 0.04-0.16)"   # == render(0.10, format_spec), compile-verified
    produced_by_experiment: E01
    registry_ref: null
    source_anchor:
      file: evidence/figures/figure3.md
      locator: { figure: "Figure 3A" }
      quote: "p217_MS ... 0.10 [ 0.04; 0.16]"
      line_range: { start: 22, end: 22 }
      checksum: "sha256:9c1e77…"
    reconcile_status: internally_reconciled    # tags, raw_repr, render all agree
    external_fidelity:                          # set ONLY by the independent pass
      state: unfaithful
      checked_by_pass: "extractive_fidelity@che26"
      pass_finding: "sha256:<extractive_fidelity/che26...yaml>"
      claim_ref: "C01"
      infidelity_type: unsupported_addition
      paper_quote: "Forest plots indicated that p217_MS ... provided the most substantial improvements in AUC relative to the p-tau181 benchmark (Figure 3A)"
      checked_at: 2026-07-06T00:00:00Z
    # ^ THE POINT: byte-perfectly internally_reconciled, yet the number is fabricated relative to
    #   the paper. v1's status:grounded would have shipped this; v2 shows it red on the external axis.

  - id: Q07
    label: "p217_MS P-score — Abeta positivity ranking (Outcome 1)"
    value: 0.859
    value_type: ordinal_rank
    value_kind: ordinal
    unit: { code: dimensionless, na: true }
    uncertainty: { type: none, lower: null, upper: null, reported: false, reason: "per-marker P-scores in Table 2 not reported with CIs" }
    comparator: none
    comparator_value: null
    baseline_ref: null
    ranking_ref: { ranking_id: R_outcome1_abeta, rank: 1, rank_polarity: rank1_is_best, surrogate_is: p_score }
    direction: higher_better
    role: result
    derivation: { kind: primary, derived_from: [], formula: null, tolerance: { abs: 0.0, rel: 0.0 } }
    extraction_method: exact_from_labels
    reading_confidence: high
    format_spec: { decimals: 3, style: plain, ci_style: null }
    raw_repr: "0.859"
    source_anchor:
      file: evidence/tables/table2.md
      locator: { table: "Table 2", outcome: "Outcome 1", rank: 1 }
      quote: "p217_MS (0.859)"
      line_range: { start: 14, end: 14 }
      checksum: "sha256:3f9a1c…"
    reconcile_status: internally_reconciled
    external_fidelity: { state: faithful, checked_by_pass: "extractive_fidelity@che26", pass_finding: "sha256:…", claim_ref: "C01", infidelity_type: null, paper_quote: null, checked_at: 2026-07-06T00:00:00Z }
- **RegistryRef with fetch_log** (YAML object under `registry_ref`) — Publication-bias / outcome-switching join key that makes an unresolved registry lookup auditable: a timestamped attempt log distinguishes never-attempted from attempted-and-down, killing the permanent honest-looking dodge.
  - fields: registry: string — required — e.g. PROSPERO, ClinicalTrials.gov.
accession: string|null — required — null with a reason only if genuinely unregistered.
registered_as: string|null — optional — the pre-registered outcome text.
registered_value: number|null — optional — the pre-registered target if any.
fetch_log: list[{ts:timestamp, method:enum{api_v2,api_int_history,cache,manual}, endpoint:string, http_status:int|null, outcome:enum{resolved_match,resolved_divergent,resolved_no_data,registry_down,not_found}}] — required, may be empty — cache-first per outcome_switching.py's contract; an empty list means not_attempted.
resolution: enum{resolved_match,resolved_divergent,resolved_no_data,attempted_unresolved,not_attempted,not_applicable_no_registration} — required — DERIVED from fetch_log: not_attempted iff fetch_log empty; attempted_unresolved iff every attempt was registry_down/not_found. not_attempted and attempted_unresolved are both honest but scored distinctly by the publication-bias metric.
  - example: registry_ref:
  registry: PROSPERO
  accession: "CRD420261327845"
  registered_as: "primary outcome: AUC difference p-tau217 vs p-tau181 for Abeta detection"
  registered_value: null
  fetch_log:
    - { ts: 2026-07-06T00:04:11Z, method: cache, endpoint: "external_cache/prospero_CRD420261327845.json", http_status: null, outcome: not_found }
    - { ts: 2026-07-06T00:04:13Z, method: api_v2, endpoint: "https://www.crd.york.ac.uk/prospero/api/…", http_status: 503, outcome: registry_down }
  resolution: attempted_unresolved   # DERIVED — distinct from not_attempted (empty log)
- **ProvenanceAnchor + canonical render function** (YAML object `source_anchor`; render() is a pure spec, not data) — Structured replacement for the prose DSL, plus the fully-specified deterministic render() that generates raw_repr, so the string a consumer prints is a pure function of the record — not a second transcription.
  - fields: file: repo-relative path — required — must resolve inside the ARA.
locator: object, shape by evidence type — required — {table,outcome,rank}|{figure,panel}|{section}; no free-text locators.
quote: string — required — exact verbatim substring; empty quote is an automatic structural failure (NOTE: this proves the string exists in the evidence FILE, not that it is faithful to the paper — that is external_fidelity's job).
line_range: {start:int,end:int}|null — optional but recommended.
checksum: string — required — sha256 of the target file at compile; detects evidence-file drift ONLY (explicitly not a fidelity guarantee).

render(value, format_spec) -> string, specified to the bit:
  • rounding: round-half-to-even (banker's) at `decimals` places.
  • trailing zeros: ALWAYS emit exactly `decimals` fractional digits ⇒ 0.1 with decimals:2 renders '0.10', never '0.1'.
  • decimal separator '.'; NO thousands separator; negative sign U+002D '-' with no space.
  • style plain: fixed-point as above.
  • style percent: multiply canonical value by 100, apply the same rounding/trailing rule, append '%'.
  • style scientific: mantissa in [1,10) with exactly `decimals` fractional digits, then 'e', sign, exponent zero-padded to ≥2 digits ⇒ 1.23e-04.
  • ci_style: a template string with named placeholders {value},{lower},{upper},{level}; each placeholder is rendered by the same rules with this record's `decimals`; all inter-placeholder literal text (spaces, brackets, 'CI', dashes) is preserved byte-exact. Null ci_style ⇒ raw_repr is just render(value).
  - example: source_anchor:
  file: evidence/tables/table2.md
  locator: { table: "Table 2", outcome: "Outcome 1", rank: 8 }
  quote: "p181_IA (0.117)"
  line_range: { start: 21, end: 21 }
  checksum: "sha256:3f9a1c…"
# render(0.117,{decimals:3,style:plain,ci_style:null}) == "0.117" == raw_repr  (compile-verified)
- **Inline Anchor Tag + evidence sidecar + claim Quantities block** (Markdown inline token in prose; YAML `.qids.yaml` sidecar for tables/figures; `Quantities:` list on each claim block) — Keeps prose human-readable while making every printed literal machine-checkable, and binds table cells without polluting markdown. Adopted from the competitor and unified with the coverage audit.
  - fields: inline token: `⟦Q{id}⟧` immediately trailing a printed literal in claims.md Statement/Interpretation, exploration_tree result/title. The printed literal MUST byte-equal quantities[id].raw_repr.
sidecar bindings: list[{row:string|int, column:string, qid:QID}] in evidence/tables/{name}.qids.yaml — every load-bearing cell binds to exactly one QID; a numeral-bearing cell with no binding is a Coverage-Audit defect.
claim block: `Quantities: [QID,...]` — required on any claim with ≥1 numeral — must equal the set of inline-tagged QIDs in that block (a self-check).
  - example: # claims.md
- Statement: "p217_MS achieved the highest rank (P-score 0.859⟦Q07⟧), while p181_IA ranked last (0.117⟦Q08⟧); the claimed AUC gain was 0.10 (95% CI 0.04-0.16)⟦Q11⟧."
- Quantities: [Q07, Q08, Q11]

# evidence/tables/table2.qids.yaml
bindings:
  - { row: "Rank 1 (p217_MS)", column: "Outcome 1: Abeta pathology", qid: Q07 }
  - { row: "Rank 8 (p181_IA)", column: "Outcome 1: Abeta pathology", qid: Q08 }

  _Protocols:_
  - **Internal Reconciliation (Class A — deterministic)** — On every compile/CI run; sets reconcile_status.. 1. For each quantity, assert raw_repr == render(value,format_spec); else reconcile_status=disputed.
2. For each inline ⟦Qid⟧ tag and each .qids.yaml binding, byte-compare the printed literal to quantities[id].raw_repr (after NFKC+dash-fold normalization already used by grounding.py); mismatch ⇒ disputed.
3. For each claim block, assert Quantities set == inline-tagged QID set.
4. For each derivation.kind=computed, recompute formula over derived_from values and assert |result-value| ≤ tolerance.abs and rel; violation ⇒ disputed.
5. Assert source_anchor.checksum matches current evidence file; drift ⇒ disputed (evidence changed since grounding).
6. If all pass, reconcile_status=internally_reconciled. This step CANNOT set external_fidelity.
    - reliability/reproducibility: Fully deterministic: identical inputs ⇒ identical statuses, no model in the loop.
    - constraints: Tooling must ship the frozen render() implementation and the normalizer; both must be versioned so a render-spec change is a visible diff, not silent.
  - **External Fidelity Grading (Class B — reliability of an independent resolver)** — Before any quantity can be reported as externally grounded; whenever fulltext/<slug>.txt exists.. 1. A pass in a DIFFERENT session than the compiler (anti-self-grading, exactly as research/metrics/v3/extractive_fidelity.py mandates) takes each claim's load-bearing QIDs.
2. For each, it checks value AND direction/polarity (via ranking_ref for ordinals) against fulltext/<slug>.txt — NOT against source_anchor.quote (a compiler could cite a quote that does not appear in or support the paper) and NOT against metadata/abstract.
3. It marks the quantity faithful iff the number matches, the direction/rank polarity matches, and no clause depending on it is an unsupported_addition; else it records infidelity_type ∈ {number_mismatch, polarity_inversion, unsupported_addition} with the contradicting paper_quote.
4. It writes the frozen finding to research/metrics/v3/extractive_fidelity/<slug>.yaml; a tool then stamps each quantity's external_fidelity block from that finding (state, pass_finding hash, claim_ref, infidelity_type, paper_quote).
5. If no fulltext on disk ⇒ state=unverifiable_no_fulltext (honest, not penalized). If no pass has run ⇒ pending_no_pass.
    - reliability/reproducibility: Reproducible via the frozen per-ARA yaml keyed by a fulltext checksum; re-running the pass on the same fulltext must reproduce the same faithful/unfaithful verdict per claim. Failure modes: (a) fulltext extraction incomplete ⇒ mark unverifiable rather than unfaithful; (b) digitized_estimate quantities get a widened numeric tolerance so a legitimate figure read is not called number_mismatch; (c) disagreement between two independent passes routes to a for/against record, never silently to faithful.
    - constraints: Ecosystem must provide: fulltext/<slug>.txt for each ARA, a coverage.md listing which ARAs are abstract-bound, and an isolation guarantee that the grading pass cannot read or import the compiler's quantities.yaml quotes as ground truth.
  - **Coverage Audit (Class B — reliability; closes the load-bearing hole)** — On every compile; decides which numerals must have a QID and certifies nothing was silently dropped.. 1. Enumerate EVERY numeric token across rendered surfaces (claims prose, evidence tables/figures, exploration_tree results) with a regex.
2. Auto-classify STRUCTURAL by rule-match: page numbers, table/figure/section/equation indices, reference-list indices, 4-digit years in citation context, version numbers. Each STRUCTURAL disposition carries the rule that matched.
3. Everything else is a CANDIDATE. For each candidate, disposition ∈ {LOAD_BEARING (participates in a claim/comparison/result/effect size ⇒ MUST have a QID), CONTEXTUAL_INPUT (sample size n=, dose, threshold, config ⇒ role:input, MUST have a QID if referenced by any claim), DISPUTED (auditor cannot decide)}.
4. A LOAD_BEARING/CONTEXTUAL_INPUT candidate with no ⟦Qid⟧ tag or .qids.yaml binding is an unbound defect. A DISPUTED numeral blocks the ARA from 'fully covered' and must be resolved, never dropped.
5. Emit a FROZEN logic/coverage_audit.yaml listing every numeral, its surface location, its disposition, the matched rule/QID, and defect flags. Executed by a non-author pass.
    - reliability/reproducibility: Reproducible because the frozen finding enumerates the full numeral population; two auditors' dispositions can be diffed. A number cannot be 'quietly declared non-load-bearing' — declaring STRUCTURAL requires a named rule the auditor validates, and every token appears in the finding, so a drop is a visible line, not an absence.
    - constraints: Tooling must supply the numeral tokenizer and the STRUCTURAL rule table; the audit executor must be a different session than the compiler.

  _Metrics afforded:_
  - Cross-layer numeric reconciliation (does every printed copy of a number agree?) → Deterministic byte-compare of each ⟦Qid⟧ literal and each .qids.yaml cell to quantities[id].raw_repr, plus raw_repr==render(value,format_spec). Reported as internally_reconciled fraction. [deterministic]; anti-Goodhart: Cannot be gamed by padding: only the enumerated load-bearing numerals (fixed by the Coverage Audit) are in scope, and a fabricated-but-consistent number scores here yet is caught on the orthogonal external_fidelity axis. Adding more tags without matching literals lowers, not raises, the score.
  - External extractive fidelity (does the number actually appear in and get supported by the paper?) → Aggregates external_fidelity.state over load-bearing quantities from the frozen extractive_fidelity/<slug>.yaml produced by the independent pass; infidelities bucketed by number_mismatch|polarity_inversion|unsupported_addition. [reliable-anchored]; anti-Goodhart: A compiler can only write pending_no_pass; faithful is unreachable without the independent pass reading fulltext directly, so self-certification is structurally impossible. unverifiable_no_fulltext and pending are scored equal to faithful for author-honesty but reported distinctly, so honest absence is never fabrication pressure.
  - Self-consistency / recompute (do derived numbers follow from their inputs?) → Deterministic recompute of every derivation.formula over derived_from within {abs,rel} tolerance. [deterministic]; anti-Goodhart: Tolerances are declared per-record and visible; a loose tolerance is a diff-able red flag. Fabricating consistent-but-wrong inputs still fails external_fidelity on those input QIDs.
  - Coverage of load-bearing numbers (is any number un-anchored?) → From frozen logic/coverage_audit.yaml: bound_load_bearing / (bound_load_bearing + unbound_load_bearing + disputed). [reproducible]; anti-Goodhart: The independent auditor enumerates every numeral, so coverage cannot be raised by dropping a contested number — a drop appears as an explicit unbound/disputed line. STRUCTURAL exemptions require a named rule the auditor validates, defeating 'declare it non-load-bearing.'
  - Publication-bias / outcome-switching join → Compare quantities[id].value / direction to registry_ref.registered_value / registered_as; resolution DERIVED from fetch_log; cache-first per outcome_switching.py. [reliable-anchored]; anti-Goodhart: not_attempted (empty fetch_log) is distinguishable from attempted_unresolved (timestamped registry_down attempts), so an ARA cannot hide behind a permanent 'registry down' dodge; the metric scores the two states differently and the attempt log is auditable.
  - Ordinal ranking integrity → For value_kind=ordinal, verify rank ordering across a ranking_id set is consistent with the surrogate scores and rank_polarity; external pass classifies a flipped order as polarity_inversion vs a wrong surrogate as number_mismatch. [reliable-anchored]; anti-Goodhart: Rank polarity is explicit (rank1_is_best/worst), so a design cannot quietly reinterpret 'rank 1' to flip a conclusion; the independent pass checks order against the paper, not against the ledger's own tags.

  _Tradeoffs:_ Honest costs and residual surfaces: (1) The external_fidelity axis depends on an ecosystem service (an independent adversarial pass + fulltext on disk). Where fulltext is unavailable the axis is genuinely unknown (unverifiable_no_fulltext) — v2 does not pretend otherwise, but it means the strongest anti-fabrication guarantee is only as good as fulltext coverage. Mitigation: the state is first-class and reported, and abstract-bound ARAs are flagged, matching the on-disk ABSTRACT_ONLY handling. (2) The render spec is now load-bearing infrastructure: if render() has a bug, raw_repr is wrong everywhere at once. Mitigation: render() is a small pure versioned function with a golden-test suite; a spec change is a visible diff. (3) source_anchor.quote + checksum remain compiler-authored and can still misquote the paper — I explicitly demote them: they prove file-presence and file-stability ONLY, and the metric that matters (external fidelity) ignores them. This is the honest scope-limit the v1 design blurred. (4) Coverage Audit disposition still involves judgment at the LOAD_BEARING/CONTEXTUAL boundary; a motivated auditor could over-use STRUCTURAL. Mitigation: STRUCTURAL requires a named rule and the full numeral population is frozen and diff-able across auditors, converting judgment into an auditable record rather than a silent drop. (5) Two independent fidelity/coverage passes can disagree; v2 routes disagreement to a for/against record, not to the favorable verdict, at the cost of needing occasional adjudication. (6) Added fields raise authoring burden; mitigated because raw_repr, reconcile_status, resolution, and used_by are all DERIVED, not hand-authored — the human types the value once and the tooling fills the rest.

  _Open questions:_ 1. Digitized figure reads: what numeric tolerance should the external pass grant a digitized_estimate before calling it number_mismatch, and should that tolerance be per-figure (axis resolution) rather than global? 2. STRUCTURAL rule completeness: the exemption rule table (page/figure/ref/year) will have edge cases (a year that is itself a result, e.g. 'median onset 2019'); how is the auditor's override recorded and bounded? 3. Cross-ARA quantity identity: when two ARAs cite the same trial number, should there be a global quantity id so a divergence between them is detectable, and who owns that namespace? 4. Fidelity of the fidelity pass: the external pass is anti-self-grading but still an agent; the design assumes an ensemble/for-against resolves it, but the calibration set and inter-pass agreement threshold that make 'reliable' quantitative are not yet specified. 5. Registry semantics drift: registered_as is free text; matching it to a quantity's meaning (not just its value) is still a semantic judgment the fetch_log does not close.

  _Changes from critique:_ Addressed all five critique points directly. (1) FABRICATION SURFACE: killed `status:grounded`. Renamed to `reconcile_status ∈ {internally_reconciled, pending, disputed}` (compiler/validator-set, deterministic, means only 'ledger⇄tags⇄render agree + recompute holds'). Added a separate `external_fidelity: {state, checked_by_pass, pass_finding, claim_ref, infidelity_type, paper_quote, checked_at}` block that a compiler is STRUCTURALLY forbidden to set to `faithful` — its `faithful`/`unfaithful` states are writable only by the independent adversarial pass that produces research/metrics/v3/extractive_fidelity/<slug>.yaml, keyed by (pass_finding hash, claim_ref, infidelity_type, paper_quote). The coverage/grounding audit refuses to certify any quantity as externally grounded until this block is populated by that pass. Used my own v1 flagship (MD=0.10) as the worked example of a quantity that is internally_reconciled but external_fidelity.state=unfaithful, citing the real che26 C01 finding on disk. (2) RENDER-VS-TOKEN: chose ONE model and specified it to the bit — value is canonical; `raw_repr` is DERIVED by render(value, format_spec) and byte-verified at compile (compile fails if they differ, so raw_repr is never a second hand-typed number); prose/table literals are byte-compared to raw_repr. Fully specified render: round-half-to-even, always emit exactly `decimals` fractional digits (0.1 with decimals:2 ⇒ '0.10'), '.' separator, no thousands separator, '-' U+002D for negatives, scientific mantissa/exponent grammar, and a ci_style template grammar with named {value|lower|upper|level} placeholders each rendered by the same rules with literal inter-placeholder text preserved byte-exact. (3) ORDINAL: removed the deferral. Added first-class `ranking_ref` + `rank` + `rank_polarity` and a Ranking Set structure; defined that for ordinal quantities `number_mismatch` = wrong surrogate score (P-score) while `polarity_inversion` = wrong rank order or reversed direction claim, matching the exact error taxonomy the on-disk extractive_fidelity pass already uses. (4) LOAD-BEARING: added the Coverage Audit protocol with a deterministic numeral-enumeration + disposition decision procedure (LOAD_BEARING | CONTEXTUAL_INPUT | STRUCTURAL | DISPUTED, with explicit STRUCTURAL rule-matches for page/figure/table/ref/equation/year-in-citation), executed by an independent non-author pass that emits a FROZEN logic/coverage_audit.yaml listing every numeral and its disposition — so dropping a contested number surfaces as an explicit unbound/disputed line, not a silent omission. (5) REGISTRY: replaced the flat `fetch_status` with `registry_ref.fetch_log`: an ordered list of {ts, method, endpoint, http_status, outcome} attempt records plus a `resolution` summary, with `not_attempted` as a distinct honest-but-scored-differently state from `attempted_unresolved`; cache-first per the outcome_switching.py contract on disk.

  _Adopted from competitor:_ Four ideas from QLTB, each strictly improving v2: (a) `raw_repr` — the exact printed literal stored once — but I make it DERIVED and compile-verified (render(value,format_spec)==raw_repr) rather than a hand-authored string, which turns the competitor's byte-check into a check that also proves format_spec is complete, resolving the reviewer's 0.1-vs-0.10 objection. (b) The `.qids.yaml` sidecar for binding table cells / figure datapoints to QIDs without polluting human-readable markdown — adopted verbatim as the evidence-layer binding mechanism, with the 'unbound cell with a numeral = defect' rule folded into my Coverage Audit. (c) The block-level `Quantities: [QID,...]` list on each claim as a fast machine join plus a self-check that the set equals the inline-tagged QIDs. (d) The richer `value_type` enum {scalar, count, percentage, ratio, rate, ordinal_rank, duration, monetary} and the honest `extraction_method {exact_from_labels, digitized_estimate, computed, not_verifiable} + reading_confidence` pair, which is a genuine honest-absence path for figure digitization that v1 lacked. Also adopted global addressability `<ara_id>#Q01`.

  _Why it wins:_ QLTB has the identical fabrication surface the reviewer nails in point 1, and does not close it: its `source_anchor.quote` is compiler-authored, its `reading_confidence: high` self-certifies, and it has no independent-fidelity gate — a QLTB ledger can be byte-perfect and still ship a fabricated number, exactly like the real che26 C01 case on disk. v2 adds the `external_fidelity` block that only the on-disk adversarial pass can set, so 'internally consistent' and 'faithful to the paper' become separately measurable. QLTB collapses ordinals into `value_type: ordinal_rank` but supplies NO comparator/direction/polarity semantics for ranks — precisely where number_mismatch vs polarity_inversion errors live in the amyloid ranking example; v2 defines them. QLTB's unbound-cell defect names no decision procedure and no non-author executor, so it is the 'theater' the reviewer warns about; v2's Coverage Audit is an explicit, enumerate-everything, independently-run frozen finding. QLTB's `comparison_status: not_yet_compared` is the same permanent registry dodge; v2's fetch_log makes never-attempted distinguishable from attempted-and-down with timestamps. Net: I keep QLTB's genuinely better ergonomics (raw_repr, sidecars, block Quantities list) and add every anti-fabrication gate it lacks. A merge is not strictly better than v2 because v2 already subsumes QLTB's data model; the deltas are all additive gates QLTB does not have.


---


## CLAIMFOL — Structured / FOL claim representation

_Class A — format-recoverable determinism_


**Judge rationale:** All four converge on the right architecture (closed typed-predicate vocabulary, arguments bound to stable entity/quantity ids, explicit quantifier+scope, claim_type→rubric routing, honest null-with-reason). They separate on two axes that matter most for Class A: (i) how few authored sources of truth there are (drift/fabrication surface), and (ii) how deterministic and Goodhart-resistant the solver + validation actually are. The two sonnet designs (#3, #2) win because each has a genuine single-source-of-truth mechanism that kills drift BY CONSTRUCTION: #3 co-locates surface+YAML and enforces a round-trip render check; #2 makes the AST a pure derived function of one authored DSL line. The two gpt-5.5-codex designs (#0, #1) maintain a canonical YAML PLUS generated surface PLUS generated FOL and then concede that "prose↔logic drift becomes a validation metric" — i.e. they design in the drift and measure it rather than eliminating it, and their enum overload (epistemic_force, modal_context, 11-value claim_type) pushes non-checkable semantic judgment back to authoring time, expanding the fabrication surface. #3 edges #2 for first place because it goes furthest on the solver (numeric interval satisfiability, not just symbolic contradiction) and hardest on anti-gaming (type↔predicate cross-validation + entailment_rubric auto-derived so type can't be downgraded to dodge rigor). #2 is a very close second for the cleanest architecture (derived AST), the only concrete EBNF grammar, and the strongest, most concrete over-claiming detector (generality field-diff). #0 ranks third: the richest schema and the only explicit ContradictionRule/Datalog engine, but heavier and drift-prone. #1 is a lighter twin of #0 with better absence symmetry and an extrapolation enum, but thinner contradiction machinery and partially empty protocol fields.


### Finalist A (refined)

> _Judge critique it answered:_ CLF (#3) is the strongest on class-A determinism, but three claims are softer than they read. (1) Your numeric constraint-satisfiability pass is the boldest and best differentiator, yet it is unbounded: you feed comparator intervals over quantities.yaml ids to a solver and assert "joint satisfiability," but you never define the COMMENSURABILITY class. AUC-MD, P-score, and a hazard ratio are not on one scale; joint constraints are only meaningful within {same entity pair OR same subject, same metric id, same population/scope}. Without an explicit equivalence-class gate BEFORE the SAT call, you will fabricate contradictions (two unrelated quantities forced into one constraint) or miss real ones. Specify the join key and the normalization step, or the pass is theater. (2) The round-trip check (fol_render == renderer(YAML)) is a SYNTACTIC guard only — it proves the string matches the struct, not that the struct matches the prose Statement. The actual fabrication surface (a logical form that says more or less than the prose) is untouched. Be explicit that round-trip is a free cheap guard and that prose↔YAML fidelity is irreducibly Class B judgment routed to a judge — right now the summary implies the round-trip catches "fabrication for free," which overclaims. (3) type↔predicate cross-validation closes the DOWNSTREAM slot (given predicate, type can't be mislabeled) but leaves the real gaming lever open: predicate SELECTION. A compiler dodging the causal control-arm rubric just picks EXCEEDS/comparative instead of CAUSES for causal-sounding prose. You need a predicate-selection audit against the prose's verbs/an adversarial second pass, or state honestly that predicate choice is an unguarded judgment. (4) domain_extent = closed|open is too coarse for the over-claiming metric — it collapses the single most common over-claim, the cohort→declared-population leap, into "open." #2's generality ladder (sample/cohort/multi_cohort/population_estimate/claimed_universal) strictly dominates you here; adopt a graded extent. (5) Conjunction-only ASTs punt disjunction "out of scope," but real claims carry OR ("A or B beats C"); forcing these into separate claims corrupts the contradiction graph. Name the interim encoding rule. (6) You assert corpus-wide numeric solving, but quantity ids are per-ARA — give the cross-ARA quantity join/units contract or concede cross-ARA is symbolic-only.

**CLF/CK — Claim Logical Form with a Comparability-Key gate (Oshima-style predicate-argument overlay + typed join keys before every solve)**  ·  _source: CLF (finalist #3)_

CLF keeps every claim's prose block untouched and adds one co-located FOL field: a human-readable rendered logical form plus the typed YAML it is deterministically rendered from — predicates over a closed versioned vocabulary, arguments bound to entity/quantity ids, an explicit quantifier, a GRADED generality ladder for scope, comparators as interval constraints, and a claim_type cross-validated against the predicate used. The decisive change from the critiqued version: no solver ever sees a raw pile of comparator intervals. Every constraint first emits a deterministic Comparability Key (CK) = {canonical subject-axis, canonical metric id, population+conditions, canonical unit}; the numeric satisfiability pass partitions constraints by CK and solves ONE instance per class, so unrelated quantities (an AUC-MD, a P-score, a hazard ratio) can never be forced into one constraint — killing both fabricated contradictions and missed real ones. It closes M09 (FOL-ability), the symbolic half of M08 (contradiction), the type-selection half of D1/S4, and — via a graded generality diff stolen and sharpened from the sibling design — the over-claiming metric, all deterministically. It is now honest about its three soft edges: round-trip is a cheap well-formedness guard only, prose↔FOL fidelity and predicate SELECTION are irreducibly Class B judge calls (each given a bounded deterministic pre-filter), and cross-ARA numeric solving is gated behind a global-metric lift contract, falling back to symbolic-only when the lift is absent.

- **FOL field on a claim block (surface syntax + logical form, embedded in logic/claims.md)** (Markdown field **FOL**: a backtick-quoted rendered string, followed by a fenced ```clf yaml``` block. No sidecar source of truth; the AST (claim_graph) is a pure derived function of this block.) — The single writable unit: one new markdown field per C## block carrying the human-readable rendered logical form and the typed YAML that generates it. One file, one authoring pass, a built-in R1 well-formedness check between the two views. Now carries a graded generality ladder and a shallow-DNF conjunct structure, and every comparator auto-emits its Comparability Key.
  - fields: claim_type: enum{causal|comparative|improvement|generalization|descriptive|correlational|existence|scoping|predictive|other} — required — must be in the predicate's allowed_claim_types (schema-enforced).
polarity: enum{affirmative|negated} — required.
quantifier: {kind: enum{universal|existential|most|proportion|single_instance}, variable: string, domain_ref: population_id} — required.
scope: {population_ref: id (→ populations.yaml), generality: enum{sample|cohort|multi_cohort|population_estimate|claimed_universal} — required — the ASSERTED generality the claim quantifies over; over-claim metric diffs this against the population's evidenced generality; conditions: list[bound_predicate], temporal: {value|not_specified, reason: enum{not_stated_in_source|not_applicable_to_claim_type|ambiguous_in_source}}, geographic: {value|not_specified, reason}} — required structurally; subfields honestly null-with-reason, never bare null.
ast: {op: enum{AND|OR}, groups: list[conjunct]} — required — shallow DNF, max depth 1. op=AND is the common case; op=OR encodes single-claim disjunction (see interim rule in Predicate Vocab / protocol P7). Depth>1 is rejected → author must split.
conjunct: {predicate: {symbol: enum(from predicate_vocab@vN), args: list[{role, ref_type: enum{entity|entity_set|quantity|population|literal|claim}, ref_id: id|list|null, literal_value: any|null, resolution_status: enum{resolved|unresolved}}]}, comparator: {op: enum{=|≠|>|<|≥|≤|no_sig_diff|subset_of|null}, lhs_ref: quantity_id|null, rhs_ref: quantity_id|literal|null, unit: string, direction: enum{higher_is_better|lower_is_better|not_applicable}}, comparability_key: CK (auto-derived, see Comparability Key struct)} — ≥1 conjunct.
entailment_rubric: string — NOT compiler-authored; auto-populated by validator from claim_type via the shared Type→Rubric map (prevents type-downgrading).
cue_flags: list[enum] — auto-populated by the deterministic cue linter (P4): e.g. [causal_cue_prose_noncausal_predicate]; empty = clean; a flag is a routing signal to the judge, NOT a penalty.
fol_render: string — exact text in the **FOL**: line; must equal renderer(fields) (R1).
  - example: ## C01: p-tau217 by mass spectrometry has the highest diagnostic accuracy for amyloid-beta pathology
- **Statement**: For detecting amyloid-beta positivity, mass-spectrometry p-tau217 (p217_MS) achieved the highest rank (P-score 0.859); p217_MS had a mean AUC difference MD=0.10 (95% CI 0.04-0.16) vs p181_IA.
- **Status**: supported
- **Proof**: [E01]
- **FOL**: `MOST? no → SINGLE x: RANKS_HIGHEST(p217_MS, CN_SET01, QMETRIC:Pscore | outcome=Abeta_pos) ∧ EXCEEDS(p217_MS, p181_IA, QMETRIC:AUC, Δ∈[0.04,0.16])  @generality=cohort(N=135)`
  ```clf
  claim_type: comparative
  polarity: affirmative
  quantifier: {kind: single_instance, variable: x, domain_ref: POP:biofinder1}
  scope:
    population_ref: POP:biofinder1
    generality: cohort
    conditions: ["outcome=Abeta_positivity", "network=NMA_outcome1"]
    temporal: {value: not_specified, reason: not_stated_in_source}
    geographic: {value: not_specified, reason: not_stated_in_source}
  ast:
    op: AND
    groups:
      - predicate:
          symbol: RANKS_HIGHEST
          args:
            - {role: subject, ref_type: entity, ref_id: CN04, resolution_status: resolved}
            - {role: comparison_set, ref_type: entity_set, ref_id: [CN04,CN05,CN06,CN07,CN08,CN09,CN10,CN11], resolution_status: resolved}
            - {role: metric, ref_type: quantity, ref_id: QMETRIC:Pscore, resolution_status: resolved}
        comparator: {op: "=", lhs_ref: Q01, rhs_ref: null, unit: "Pscore[0,1]", direction: higher_is_better}
        comparability_key: {subject_axis: "CN04", metric_id: QMETRIC:Pscore, population_ref: POP:biofinder1, conditions_hash: h9a1, unit_canonical: "Pscore[0,1]"}
      - predicate:
          symbol: EXCEEDS
          args:
            - {role: subject, ref_type: entity, ref_id: CN04, resolution_status: resolved}
            - {role: baseline, ref_type: entity, ref_id: CN11, resolution_status: resolved}
            - {role: metric, ref_type: quantity, ref_id: QMETRIC:AUC, resolution_status: resolved}
        comparator: {op: ">", lhs_ref: Q02_delta, rhs_ref: 0, unit: "AUC_MD[0,1]", direction: higher_is_better}
        comparability_key: {subject_axis: "CN04|CN11", metric_id: QMETRIC:AUC, population_ref: POP:biofinder1, conditions_hash: h9a1, unit_canonical: "AUC_MD[0,1]"}
  entailment_rubric: "comparative: requires_enumerated_alternatives + headtohead_or_network_evidence"
  cue_flags: []
  fol_render: "...matches the **FOL** line above..."
  ```
- **Comparability Key (CK) + Commensurability Registry — logic/commensurability@vN.yaml** (CK is a struct emitted by the compiler per comparator (never hand-written). The Registry is one shared versioned YAML.) — THE fix for the reviewer's #1. A CK is the deterministic equivalence-class label attached to every comparator; the numeric SAT pass groups constraints by CK and solves one instance per class. Constraints from different classes are structurally incapable of being co-asserted, so a P-score, an AUC-MD and a hazard ratio never land in one constraint set. The Registry declares metric identity, canonical units, and the ONLY sanctioned cross-metric conversions.
  - fields: CK.subject_axis: string — required — canonical subject identity. For 1-place property predicates = the entity id. For 2-place comparative/improvement predicates = the UNORDERED pair joined lexicographically (e.g. "CN04|CN11"); the comparator is simultaneously normalized so lhs<rhs lexicographically and op is flipped to match, so a `>` and a `<` over the same pair unify into one class.
CK.metric_id: id — required — the canonical METRIC-TYPE id (QMETRIC:AUC), NOT the per-measurement quantity id. Distinct metric_ids never join unless the Registry declares a conversion.
CK.population_ref: id — required — populations.yaml id.
CK.conditions_hash: string — required — order-independent hash of the normalized bound-condition set.
CK.unit_canonical: string — required — unit AFTER normalization via the Registry; incommensurable units yield distinct CKs.
Registry.metric: {id, canonical_unit, scale: enum{ratio|interval|ordinal|bounded01}, higher_is_better: bool} — required.
Registry.conversion: {from_metric, to_metric, transform: string|not_permitted} — required — default not_permitted; a declared transform is the ONLY way two metric_ids share a class.
  - example: # commensurability@v1.yaml
metrics:
  - {id: QMETRIC:AUC, canonical_unit: "AUC[0,1]", scale: bounded01, higher_is_better: true}
  - {id: QMETRIC:AUC_MD, canonical_unit: "AUC_MD[-1,1]", scale: interval, higher_is_better: true}
  - {id: QMETRIC:Pscore, canonical_unit: "Pscore[0,1]", scale: bounded01, higher_is_better: true}
  - {id: QMETRIC:HazardRatio, canonical_unit: "HR", scale: ratio, higher_is_better: false}
conversions:
  - {from_metric: QMETRIC:AUC, to_metric: QMETRIC:AUC_MD, transform: not_permitted}   # a level and a difference do NOT join
  - {from_metric: QMETRIC:Pscore, to_metric: QMETRIC:AUC, transform: not_permitted}
# Result: C01's Pscore conjunct (class K1) and its AUC_MD conjunct (class K2) are solved SEPARATELY.
# A hazard-ratio claim in the same ARA lands in K3 and can never contradict either.
- **Predicate Vocabulary (shared, versioned) — logic/predicate_vocab@vN.yaml** (One shared versioned YAML, referenced by version id from every ARA; extended only through governed versioning.) — Closed corpus-wide set of typed predicates with fixed arity/roles, an allowed_claim_types mapping, and (new) the set of prose verb-cues each predicate licenses. Anti-fabrication backbone: a compiler cannot invent a predicate to dress up a vacuous claim, cannot pick a soft claim_type under a predicate that implies a harder one, and (via the cue lexicon) cannot silently swap a causal predicate for a comparative one without raising a deterministic flag.
  - fields: symbol: string unique — required.
arity: int — required.
roles: list[{role, binds_to: enum{entity|entity_set|quantity|population|literal|claim}}] — required.
allowed_claim_types: list[enum] — required — validator rejects mismatches.
requires_comparator: bool — required.
polarity_allowed: bool — required.
licensed_verb_cues: list[string] — required — prose lemmas/phrases consistent with this predicate; consumed by the cue linter (P4).
comparator_family: enum{comparison|causal|correlational|universal_property|existence|predictive|definitional|none} — required.
gloss: string — required.
  - example: - {symbol: CAUSES, arity: 3, roles: [{role: cause, binds_to: entity},{role: effect, binds_to: entity},{role: intervention, binds_to: claim}], allowed_claim_types: [causal], requires_comparator: false, polarity_allowed: true, comparator_family: causal, licensed_verb_cues: ["causes","leads to","induces","drives","results in","because of intervening"], gloss: "X interventionally produces Y; entailable only by an experiment with a control/ablation arm"}
- {symbol: EXCEEDS, arity: 3, roles: [{role: subject, binds_to: entity},{role: baseline, binds_to: entity},{role: metric, binds_to: quantity}], allowed_claim_types: [improvement, comparative], requires_comparator: true, polarity_allowed: true, comparator_family: comparison, licensed_verb_cues: ["higher","greater","outperforms","beats","exceeds","better on"], gloss: "subject beats one named baseline on metric by a stated delta"}
- {symbol: RANKS_HIGHEST, arity: 3, roles: [{role: subject, binds_to: entity},{role: comparison_set, binds_to: entity_set},{role: metric, binds_to: quantity}], allowed_claim_types: [comparative], requires_comparator: true, polarity_allowed: true, comparator_family: comparison, licensed_verb_cues: ["best","highest","top-ranked","leading"], gloss: "subject is best on metric among an enumerated set"}
- **Population / Scope Registry — logic/populations.yaml (merged from sibling design)** (YAML, one entry per distinct population referenced by any FOL scope.) — Makes over-claiming a mechanical field diff. Every population a claim quantifies over is a registry entry whose `generality` is anchored to what the data/experiment layer actually sampled. Claim asserts generality=claimed_universal but registry evidences generality=cohort, N=135 → deterministic over-claim of magnitude 3 rungs on the ladder.
  - fields: id: string POP:name — required.
label: string — required.
evidenced_generality: enum{sample|cohort|multi_cohort|population_estimate|claimed_universal} — required — the honest tag derived from the dataset/experiment layer, NOT a target.
n: int|null — required (null=not_specified, honest).
source: ref (→ data/dataset.md or experiments.md) — required, must resolve.
sampled_subpopulations: list[string] — optional — consumed by the generalization rubric.
  - example: - {id: POP:biofinder1, label: "BioFINDER-1 prodromal-AD cohort", evidenced_generality: cohort, n: 135, source: data/dataset.md#BioFINDER-1, sampled_subpopulations: []}
- {id: POP:ad_general, label: "AD patients generally (invoked by prose, no single cohort)", evidenced_generality: claimed_universal, n: null, source: not_specified, sampled_subpopulations: []}
- **Derived Claim Graph / AST node — logic/claim_graph.yaml (parser output, solver input)** (YAML/JSON, one node per claim, generated by the parser.) — The canonical DNF AST the FOL block compiles to; the actual solver walk-target. Pure derived function of the FOL block (regenerable on demand), so it is never a second place to drift. Carries the CK per leaf and surfaces unresolved bindings explicitly.
  - fields: claim_id: string — required.
well_formed: bool — required (R1 + type-check passed).
quantifier: {kind, population, generality_asserted} — required.
ast: {op: AND|OR, leaves: list[{predicate, polarity, args, comparator, comparability_key}]} — required — depth-1 DNF.
claim_type, status — required.
unresolved_bindings: list[string] — required, [] if none — any id not resolving against entity/quantity/population registries, surfaced not silently accepted.
cue_flags: list[enum] — required.
  - example: claim_id: C01
well_formed: true
quantifier: {kind: single_instance, population: POP:biofinder1, generality_asserted: cohort}
ast:
  op: AND
  leaves:
    - {predicate: RANKS_HIGHEST, polarity: asserted, args: [{subject: CN04},{comparison_set: [CN04,CN05,CN06,CN07,CN08,CN09,CN10,CN11]},{metric: QMETRIC:Pscore}], comparator: {op: "=", lhs: Q01}, comparability_key: {subject_axis: CN04, metric_id: QMETRIC:Pscore, population_ref: POP:biofinder1, conditions_hash: h9a1, unit_canonical: "Pscore[0,1]"}}
    - {predicate: EXCEEDS, polarity: asserted, args: [{subject: CN04},{baseline: CN11},{metric: QMETRIC:AUC_MD}], comparator: {op: ">", lhs: Q02_delta, rhs: 0, interval: [0.04,0.16]}, comparability_key: {subject_axis: "CN04|CN11", metric_id: QMETRIC:AUC_MD, population_ref: POP:biofinder1, conditions_hash: h9a1, unit_canonical: "AUC_MD[-1,1]"}}
claim_type: comparative
status: supported
unresolved_bindings: []
cue_flags: []
- **Verb→Predicate Cue Lexicon — logic/cue_lexicon@vN.yaml** (Shared versioned YAML.) — Fix for reviewer #3. A shared table mapping prose verb/phrase cues to the predicate FAMILIES they license, plus the danger direction (causal-cue prose bound to a non-causal predicate). The deterministic linter (P4) uses it to raise cue_flags; final adjudication is a bounded Class B judge, not a deterministic pass.
  - fields: cue: string (lemma/phrase) — required.
licenses_family: list[enum comparator_family] — required.
causal_strength: enum{explicit_causal|suggestive_causal|noncausal} — required.
note: string — optional.
  - example: - {cue: "reduces", licenses_family: [causal, comparison], causal_strength: suggestive_causal, note: "'reduces X' reads causal; if predicate is EXCEEDS/comparison, raise causal_cue_prose_noncausal_predicate"}
- {cue: "causes", licenses_family: [causal], causal_strength: explicit_causal}
- {cue: "associated with", licenses_family: [correlational], causal_strength: noncausal, note: "if predicate is CAUSES, raise overclaim_correlational_prose_causal_predicate"}
- {cue: "outperforms", licenses_family: [comparison], causal_strength: noncausal}

  _Protocols:_
  - **P1 — Comparability-gated numeric satisfiability (the SAT pass, now sound)** — Whenever detecting numeric contradictions among comparator-bearing claims, within one ARA (default) or across ARAs (only under the P6 lift).. 1. Collect every comparator leaf across the claim_graph. 2. For each leaf emit its CK (canonical subject-axis with lhs<rhs normalization + op flip; canonical metric_id; population_ref; conditions_hash; unit_canonical via the Commensurability Registry unit normalization). 3. PARTITION leaves into classes by exact CK equality — this is the equivalence-class gate; it runs BEFORE any solver instance is created. 4. For each class, instantiate ONE real variable (the comparison quantity Δ or level) and add each leaf's comparator as an interval constraint (op + CI/interval where present; no_sig_diff → [-ε,ε] with declared ε; negated polarity flips the constraint). 5. Run an interval/linear SAT solver per class. UNSAT within a class ⇒ a reported contradiction, anchored to the exact claim ids and the shared CK. 6. Cross-class leaves are NEVER combined; if a would-be constraint pair has non-unifying metric_id or incommensurable unit, it is reported as not_comparable (honest null), not as a contradiction.
    - reliability/reproducibility: Fully deterministic given the versioned Commensurability Registry: same inputs → same partition → same UNSAT set, run to run and machine to machine. The only non-determinism (solver tie-breaking) is irrelevant because SAT/UNSAT is decidable for these interval systems.
    - constraints: Ecosystem must provide: the shared commensurability@vN.yaml (metric ids, canonical units, sanctioned conversions), a declared ε policy for no_sig_diff, and a linear/interval SAT solver in the compiler toolchain.
  - **P2 — R1 round-trip well-formedness (deterministic, cheap, NOT a fabrication guard)** — Every compile.. 1. Run the deterministic renderer on the clf YAML fields. 2. Assert renderer(fields) == fol_render string. 3. Mismatch ⇒ well_formed=false, block. This proves ONLY that the human-facing string matches the struct; it says nothing about whether the struct matches the prose Statement.
    - reliability/reproducibility: Deterministic.
    - constraints: A canonical renderer shipped with the compiler; a stable pretty-print order.
  - **P3 — R2 prose↔FOL fidelity (Class B, the real fabrication surface)** — Every claim; this is where a logical form that says MORE or LESS than the prose is caught.. 1. Judge receives (prose Statement, rendered FOL, claim_graph leaves). 2. Judge answers a fixed rubric: does every predicate/argument/quantifier/comparator/generality in the FOL have prose support, and does the prose assert nothing the FOL omits? 3. Output {faithful|fol_overclaims|fol_underclaims|unfaithful} + span-level justification. Round-trip (P2) is a prerequisite but explicitly does not substitute for this.
    - reliability/reproducibility: Reproducible-anchored: judge ensemble (≥3), majority vote, for/against pass, calibration set of gold prose↔FOL pairs; report inter-judge agreement. Minimize judge degrees of freedom by feeding the structured leaves so the judge checks correspondence, not re-derives logic.
    - constraints: Calibration corpus of adjudicated prose↔FOL pairs; judge-ensemble harness; frozen rubric versioned alongside predicate_vocab.
  - **P4 — Predicate-selection audit (deterministic pre-filter + Class B adjudication)** — Every claim, to close the predicate-SELECTION gaming lever (dodging the causal rubric by choosing EXCEEDS for causal-sounding prose).. 1. Linter tokenizes the prose Statement, matches cues against cue_lexicon@vN. 2. If prose carries explicit/suggestive causal cues but the chosen predicate's comparator_family is not causal, emit cue_flag=causal_cue_prose_noncausal_predicate (and symmetric flags for correlational-prose/causal-predicate). 3. Flagged claims route to an adversarial second-pass judge whose SOLE question is: given the prose, is the softer predicate a legitimate reading or a rubric dodge? 4. Judge returns {legitimate|downgrade_detected} + rationale.
    - reliability/reproducibility: The flag is deterministic (reproducible). The adjudication is Class B: ensemble + calibration set of known dodges; report agreement. We concede final predicate choice is a bounded judgment, not deterministic.
    - constraints: Shared cue_lexicon@vN; the adversarial judge prompt; a labelled set of dodge/non-dodge examples.
  - **P5 — Over-claim generality diff (deterministic)** — Every claim with a population scope.. 1. Read scope.generality (asserted) from the FOL. 2. Read populations.yaml[population_ref].evidenced_generality. 3. over_claim_rungs = ladder_index(asserted) - ladder_index(evidenced) on {sample<cohort<multi_cohort<population_estimate<claimed_universal}. 4. rungs>0 ⇒ over-claim of that magnitude, reported with both anchors; rungs≤0 ⇒ no over-claim. not_specified on either side ⇒ honest null, unscored, never penalized as fabrication.
    - reliability/reproducibility: Deterministic given the registry.
    - constraints: populations.yaml with evidenced_generality anchored to the dataset/experiment layer; the fixed ladder ordering.
  - **P6 — Cross-ARA lift contract (deterministic gate; symbolic-only fallback)** — Any corpus-wide (cross-ARA) contradiction or consistency check.. 1. For a candidate cross-ARA leaf pair, require BOTH quantities to carry: a shared global_metric_id (from commensurability@vN, not a per-ARA quantity id), a canonical unit, and a globally-resolved subject/pair (via the entity-resolution layer). 2. If all present and CKs unify under the global ids ⇒ admit into P1's numeric SAT. 3. If ANY is missing ⇒ numeric solving is DISABLED for that pair; fall back to SYMBOLIC-ONLY: detect polarity/predicate contradictions over globally-resolved entities (e.g. CAUSES(A,B) vs ¬CAUSES(A,B)), no interval math. 4. Report which mode each cross-ARA finding used.
    - reliability/reproducibility: Deterministic given the global registries; the numeric/symbolic mode is a function of present fields, reproducible run to run.
    - constraints: Ecosystem must provide a global metric registry, a global unit registry, and a cross-ARA entity-resolution service. We explicitly concede: without these, cross-ARA is symbolic-only — numeric interval solving does not cross the ARA boundary.
  - **P7 — Disjunction interim encoding (single-claim OR)** — Claims of the form 'A or B beats C' that must not be corrupted into separate claims.. 1. Encode as one claim with ast.op=OR over depth-1 conjunction groups (each group a normal EXCEEDS/predicate leaf). 2. Solver semantics: an OR node is SAT if ANY disjunct is SAT; a contradiction against an OR-claim fires only when EVERY disjunct is refuted by the opposing constraint set. 3. Depth>1 (nested OR/AND) is rejected at parse → author splits into linked claims. 4. Rendered FOL shows the ∨ explicitly so the human reads the disjunction.
    - reliability/reproducibility: Deterministic; OR-node SAT is standard.
    - constraints: Solver must support disjunctive (DNF) constraint groups; parser enforces max depth 1.

  _Metrics afforded:_
  - M09 FOL-ability (is the claim expressible as a well-formed typed logical form?) → well_formed flag: parses to depth-1 DNF AST + every predicate in vocab + every required role bound or honestly null-with-reason + R1 passes. [deterministic]; anti-Goodhart: Cannot be gamed by verbosity: the vocabulary is closed (no invented predicates) and honest not_specified with a reason code scores EQUAL to a bound value, so there is no pressure to fabricate arguments. A padded but ill-typed form fails the type-check.
  - M08 contradiction — symbolic half (polarity/predicate clash) → Same-CK leaves with incompatible polarity or comparator direction reported as contradictions. [deterministic]; anti-Goodhart: CK gate prevents fabricating contradictions from unrelated quantities; not_comparable is a first-class honest outcome, so a compiler cannot farm fake contradictions to look thorough.
  - M08 contradiction — numeric half (interval UNSAT) → P1 CK-gated per-class interval SAT; UNSAT ⇒ contradiction. [deterministic]; anti-Goodhart: Constraints only combine within a commensurability class, so neither fabricated nor missed contradictions can be manufactured by mixing scales; the Registry's not_permitted conversions are the structural lock.
  - Over-claiming (D3) — cohort→population leap magnitude → P5 rung diff between asserted scope.generality and evidenced_generality. [deterministic]; anti-Goodhart: Generality is a diff against data-anchored evidence, not a self-declared target; claiming a high rung with low evidenced generality INCREASES the reported over-claim, so inflation is self-penalizing. not_specified is unscored, not punished.
  - claim_type↔predicate integrity (D1/S4 downstream half) → Validator checks claim_type ∈ predicate.allowed_claim_types; entailment_rubric auto-populated from type. [deterministic]; anti-Goodhart: Rubric is a pure function of type and type is constrained by predicate, so you cannot downgrade type to dodge a rubric while keeping a hard predicate.
  - Predicate-selection integrity (D1/S4 upstream half — the real lever) → P4 deterministic cue-mismatch flag, then adversarial judge adjudication. [deterministic (flag) + semantic-judged (adjudication)]; anti-Goodhart: Choosing a soft predicate for causal-cue prose raises a deterministic flag that routes to an adversarial judge; the flag itself cannot be suppressed by wording without also removing the causal cues from the prose (which changes the claim).
  - Prose↔FOL fidelity (fabrication surface) → P3 judge ensemble over rubric with R1 as prerequisite. [semantic-judged (reproducible-anchored)]; anti-Goodhart: Round-trip (deterministic) blocks struct/string drift for free; the semantic judge, fed structured leaves and a for/against pass, is what actually catches a form that says more/less than prose. We explicitly do NOT claim this is deterministic.
  - Cross-ARA consistency → P6: numeric SAT when global lift present, else symbolic-only. [deterministic (mode + result), reliability-anchored on the entity-resolution/global-metric services]; anti-Goodhart: Mode is a function of present global ids; a compiler cannot claim numeric cross-ARA rigor without actually supplying global_metric_id + unit + resolved subject, and the report states which mode produced each finding.

  _Tradeoffs:_ Costs and residual fabrication surfaces, honestly: (1) The Commensurability Registry is now a load-bearing shared asset — if it under-declares metric identity, real contradictions are missed (two truly-comparable quantities land in different classes); if it over-declares conversions, fabricated contradictions return. Mitigation: default is not_permitted (conservative — errs toward not_comparable, an honest null, rather than false contradiction), and conversions are governed/versioned. (2) Prose↔FOL fidelity and predicate selection remain irreducibly Class B — a sufficiently careful compiler can write a faithful-looking FOL that subtly under-claims relative to prose and pass the cue linter; the adversarial judge is the only backstop, and it has real error. We do not paper over this. (3) The graded generality tag can be gamed by mislabeling evidenced_generality in populations.yaml; mitigation is that evidenced_generality must resolve to a data/experiment source, making the lie a cross-layer inconsistency another check can catch. (4) Depth-1 DNF cannot express nested boolean structure; genuinely nested claims must be split, which pushes complexity into claim-linking. (5) Cross-ARA numeric solving is deliberately disabled without the global lift — this is a capability we concede rather than fake. (6) Authoring cost: one extra field per claim plus registry upkeep; mitigated by the single-file co-location and the AST being auto-derived (no second hand-authored source to drift).

  _Open questions:_ 1. Who governs the Commensurability Registry's conversion table across a whole field, and how are disputed conversions (e.g. is Cohen's d ↔ AUC a sanctioned transform?) adjudicated without becoming a political bottleneck? 2. ε policy for no_sig_diff: a single global ε is crude; per-metric ε is more honest but adds registry surface and a gaming lever (pick a loose ε to avoid contradictions). 3. The cue lexicon is language- and phrasing-brittle; suggestive-causal detection will have both false positives and negatives, and truly deterministic causal-vs-comparative discrimination may be impossible — how much of predicate selection can ever leave Class B? 4. Global entity resolution across ARAs is assumed but is itself a hard Class B problem the sibling gaps must solve; CLF's cross-ARA numeric claims are only as sound as that layer. 5. Whether depth-1 DNF is genuinely sufficient for real corpora, or whether a small number of claims need depth-2 and the split-and-link workaround corrupts the contradiction graph in practice — needs empirical measurement on a real ARA corpus.

  _Changes from critique:_ Addressed all six critique points directly. (1) COMMENSURABILITY: added the Comparability Key (CK) as a mandatory, deterministically-emitted join key and a Commensurability Registry; the numeric SAT pass now partitions constraints by CK and solves per-class only — the equivalence-class gate {canonical subject-axis AND canonical metric id AND population/conditions AND canonical unit} runs BEFORE any solver call, with an explicit unit-normalization step. Constraints whose CKs do not unify are never co-asserted. (2) ROUND-TRIP HONESTY: split the old single check into R1 (round-trip = render==struct, deterministic, explicitly a WELL-FORMEDNESS guard that proves the string matches the struct and nothing about prose) and R2 (prose↔FOL fidelity, explicitly Class B judge, rubric-bounded). The summary no longer claims round-trip catches fabrication. (3) PREDICATE SELECTION: added a Verb→Predicate Cue Lexicon and a deterministic cue-mismatch linter that flags causal-cue prose bound to a non-causal predicate, plus an adversarial second-pass judge; conceded that final predicate choice is a bounded Class B judgment, not deterministic. (4) GRADED EXTENT: replaced domain_extent=closed|open with the generality ladder {sample|cohort|multi_cohort|population_estimate|claimed_universal} anchored to a Population/Scope Registry, so the cohort→declared-population leap is a field diff, not collapsed into 'open'. (5) DISJUNCTION: the AST is now shallow DNF (disjunction of conjunction-groups, max depth 1) with an explicit interim encoding rule and OR-node solver semantics; conjunction-only is no longer a limitation for single-claim OR. (6) CROSS-ARA: added the Global Metric Lift contract; cross-ARA numeric solving is enabled only when quantities carry a shared global_metric_id + canonical unit + globally-resolved subject; otherwise cross-ARA is symbolic-only (polarity/predicate contradiction over globally-resolved entities), conceded explicitly.

  _Adopted from competitor:_ Adopted the sibling design's generality ladder verbatim (sample/cohort/multi_cohort/population_estimate/claimed_universal) and its Population/Scope Registry pattern — a first-class populations.yaml whose `generality` tag is anchored to what the dataset/experiment layer actually sampled, so over-claiming is a field diff rather than an inference. Also adopted its Claim-Type → required_experiment_design map (a structured predicate over experiments.md, not prose) as the entailment-precondition table, and its explicit `unresolved_bindings` surfacing so unresolved ids are declared rather than silently accepted. These merge cleanly into CLF because CLF already carries claim_type↔predicate cross-validation; the sibling's rubric map is the missing upstream half.

  _Why it wins:_ The sibling design has the better population model (which I adopted) but has NO answer to the commensurability problem at all — its claim_graph feeds Measure(entity,quantity) comparisons to a solver with the same unbounded-join flaw the reviewer flagged in me; CLF/CK now supplies the join-key gate that both designs need, so the merged result strictly dominates on the boldest differentiator (numeric contradiction detection that is actually sound). CLF also keeps the single-file, single-authoring-pass discipline (FOL is co-located in claims.md, not spread across four sidecar YAMLs), which lowers the fabrication surface: fewer independent places to drift. Finally CLF is more honest about its Class boundaries per the mandate's class discipline — it names exactly which checks are deterministic (CK-gated SAT, type↔predicate, generality diff, round-trip well-formedness) versus irreducibly Class B (prose fidelity, predicate selection), each with a bounded deterministic pre-filter, whereas the sibling implies the DSL parse settles semantic fidelity.


### Finalist B (refined)

> _Judge critique it answered:_ CLS/DSL (#2)'s single best idea — the surface DSL is the ONLY authored form and the claim_graph AST is a pure derived function of it (no second source to drift) — is genuinely the cleanest determinism story of the four. But the flagship deliverable has a correctness hole. (1) Your own C01 is a COMPOUND claim ("ranks highest on P-score AND exceeds baseline by AUC MD"), yet the EBNF grammar shows a single predicate_expr and the example DSL encodes only the GreaterThan conjunct — the RANKS_HIGHEST/P-score=0.859 content is silently dropped. Most real claims are conjunctive; a grammar that can't AND multiple predicate_exprs is lossy exactly where it matters, and lossiness in the FOL layer poisons the contradiction graph. Add explicit conjunction to the grammar and re-encode C01 in full. (2) STAT(population, n) is clever but semantically undefined — n=135 is a sample size, not a quantifier cardinality. What does STAT assert model-theoretically ("for most," "estimated over n")? The solver cannot use an operator with no truth conditions in contradiction checks. Define it or it's decoration masquerading as quantification. (3) populations.yaml generality is an "honest tag, not a target," but you built NO check that the tag is consistent with n and source — a compiler tags claimed_universal prose as "cohort" and sails through the over-claiming field-diff. The over-claim you must FLAG (claimed_universal with a cohort-sized n and single source) is precisely the one your design trusts the tag on. Add a validator: generality=cohort requires resolved n + single source; a universal quantifier over a sample-sized population is a hard finding. (4) claim_type_rubric.required_experiment_design is described as "a structured predicate over experiments.md fields" but every example is a PROSE string ("includes an ablation/RCT arm AND a control arm") — that's the LLM-re-reads-prose hand-waving the design claims to kill. Give the real field grammar (experiment.design.arms[].type == 'ablation') or the "deterministic rubric selection" claim is unearned. (5) You say the AST is "checked in OR regenerated on demand, either is valid" — that's a cache-coherence bug: a stale checked-in claim_graph.yaml passes while the DSL line changed underneath. Mandate regenerate-and-diff in CI, or forbid the checked-in copy. (6) You show symbolic contradiction (same args, incompatible comparator) but no numeric joint-satisfiability over quantity intervals — the subtle over-claims live there. Say whether comparators lower to interval constraints and how.

**CLS/DSL v2 — Single-Source Logical Form: one authored DSL line, a pure-derived FOL AST, conjunctive predicates, and comparators that lower to interval constraints**  ·  _source: ?_

Every claim keeps its prose block and gains exactly ONE authored artifact: a compact, grammar-constrained `**Logical form**` line. Its canonical FOL AST (`claim_graph.yaml`) is a pure deterministic function of that line — never hand-authored, never trusted without a source-hash/regenerate-and-diff gate — so there is no second source to drift. The grammar now supports explicit conjunction (`AND` of typed predicate expressions), so compound claims are encoded losslessly; every comparator lowers to an interval constraint over `quantities.yaml` ids, so the solver runs BOTH a symbolic contradiction pass and a numeric joint-satisfiability pass over intervals (the subtle over-claims live here). A deterministic over-claim validator diffs the quantifier against the population's resolved n and source count, so a universal quantifier over a sample-sized single-source population is a hard finding — not a trusted tag. This converts FOL-ability (M09), the structural half of contradiction detection (M08), rubric selection (D1/S4), and over-claim detection into deterministic, corpus-comparable checks, while entailment-quality and cross-ARA resolution stay honestly Class B with a narrowed judge protocol.

- **Predicate Vocabulary Registry — logic/predicate_vocab@v1.yaml (shared, versioned, corpus-wide)** (YAML, one entry per predicate, in the compiler reference set alongside ara-schema.md; extended only via governed version bump (v2, v3).) — A closed, versioned set of typed predicates every logical form draws from — the reason 'FOL' cannot decay into English-in-parentheses. Each predicate fixes arity, typed roles, which claim_types may use it (the type-honesty lock), whether it requires a comparator, and — new — a lowers_to template telling the numeric solver how its comparator becomes an interval constraint. Referenced by version id, never forked per-ARA, so cross-ARA solving cannot silently drift.
  - fields: symbol (string, PRED:Name) — required — stable symbol. arity (int) — required. roles (list[{role:string, binds_to: entity|quantity|entity_set|population|literal, closed_domain:bool?}]) — required; closed_domain marks a set-valued role whose members must be fully enumerated (the over-claim-relevant closed/open axis). polarity_allowed (bool) — required. allowed_claim_types (list[claim_type enum]) — required — schema REJECTS a form whose claim_type is not listed for a predicate it uses. requires_comparator (bool) — required. comparator_family (enum: comparison|causal|correlational|universal_property|existence|predictive|definitional|none) — required. lowers_to (string template) — required unless comparator_family=none — the interval-constraint schema the numeric solver instantiates. gloss (string) — required — one-line human definition.
  - example: - symbol: PRED:Exceeds
  arity: 3
  roles: [{role: subject, binds_to: entity}, {role: baseline, binds_to: entity}, {role: metric, binds_to: quantity}]
  polarity_allowed: true
  allowed_claim_types: [comparative, improvement]
  requires_comparator: true
  comparator_family: comparison
  lowers_to: "val(subject.metric) - val(baseline.metric)  {op}  {rhs}"   # e.g. > 0, or ≥ margin
  gloss: "subject beats a single named baseline on metric by a stated delta"

- symbol: PRED:RanksHighest
  arity: 3
  roles: [{role: subject, binds_to: entity}, {role: comparison_set, binds_to: entity_set, closed_domain: true}, {role: metric, binds_to: quantity}]
  polarity_allowed: true
  allowed_claim_types: [comparative]
  requires_comparator: true
  comparator_family: comparison
  lowers_to: "forall m in comparison_set: val(subject.metric) >= val(m.metric)"
  gloss: "subject is best on metric among a fully-enumerated comparison_set"

- symbol: PRED:Causes
  arity: 3
  roles: [{role: cause, binds_to: entity}, {role: effect, binds_to: entity}, {role: intervention, binds_to: ref}]
  polarity_allowed: true
  allowed_claim_types: [causal]
  requires_comparator: false
  comparator_family: causal
  lowers_to: null
  gloss: "X is asserted to causally produce Y (needs interventional design to entail)"
- **Surface DSL — the **Logical form** line (extends every ## C## block in logic/claims.md)** (Constrained EBNF DSL, one line, embedded as required field **Logical form**.) — The ONLY authored logical artifact: one compact grammar-constrained line under Statement. Now supports explicit conjunction so compound claims are lossless, a defined estimation quantifier EST, per-conjunct comparators that carry the quantity ids they lower to, and honest-absence NONE. A human writes and greps it; the parser consumes it deterministically; the pretty ∀-render (CLF-style) is DERIVED from it, not authored.
  - fields: GRAMMAR:
logic_form   := quantifier_block? conjunct ('AND' conjunct)* modifiers | 'NONE' '—' reason
quantifier_block := ( 'FORALL' | 'EXISTS' ) var 'IN' pop_id scope? ':'
                  | 'EST' '(' pop_id ',' 'n=' (int|'null') ',' 'ci=' qty_id ')' ':'   (* estimated-over-sample, see truth conditions in P3 *)
scope        := '[' cond_id (',' cond_id)* ']'
conjunct     := 'NOT('? PRED:name '(' arg_list ')' comparator? ')'?
arg          := entity_id | quantity_id | set_id ('[closed]'|'[open]') | 'Measure(' entity_id ',' quantity_id ')' | literal
comparator   := 'CMP[' op operand ('margin=' qty_id)? ('ci=' qty_id)? ']'
op           := '='|'!='|'>'|'<'|'>='|'<='|'~='|'no_sig_diff'
operand      := quantity_id | literal | '0'
modifiers    := '[type=' claim_type '; polarity=' asserted|negated '; status=' hypothesis|supported|refuted (';baseline=' entity_id)? ']'
reason       := 'not_specified:' text | 'not_applicable:' text   (* honest-absence, scored EQUAL to a present form *)
  - example: # C01 (biomarker) RE-ENCODED IN FULL — both conjuncts, nothing dropped:
**Logical form**: EST(POP:cn_biofinder1, n=135, ci=QTY:Q_AUC_MD):
  PRED:RanksHighest(ENT:p217_MS, SET:cn8_platforms[closed], QTY:Q_Pscore) CMP[= QTY:Q_Pscore]
  AND PRED:Exceeds(ENT:p217_MS, ENT:p181_IA, QTY:Q_AUC) CMP[> 0 margin=QTY:Q_AUC_MD ci=QTY:Q_AUC_MD_CI]
  [type=comparative; polarity=asserted; status=supported; baseline=ENT:p181_IA]

# Real repo C03 (compound: improvement AND monotone gap) also lossless:
**Logical form**: EST(POP:ara_eval_papers, n=450, ci=QTY:Q_wsr_gap_ci):
  PRED:Exceeds(ENT:ARA, ENT:pdf_repo, QTY:Q_weighted_success) CMP[> 0 margin=QTY:Q_wsr_delta]
  AND PRED:MonotoneInDifficulty(ENT:ARA_gap, SET:diff3[closed]) CMP[strictly_increasing]
  [type=comparative; polarity=asserted; status=supported; baseline=ENT:pdf_repo]

# Honest resistance-to-formalization (scored equal, not penalized):
**Logical form**: NONE — not_specified: editorial synthesis ('effectively obsolete'), not a bindable predicate over measured entities; see Interpretation.
- **Canonical FOL AST — logic/claim_graph.yaml (DERIVED build artifact, hash-gated)** (YAML/JSON, one node per claim, emitted by the parser; gitignored OR checked-in-with-CI-diff (P1) — never trusted standalone.) — The parsed, type-checked AST the solver walks. It is a pure deterministic function of the **Logical form** line and is NEVER hand-authored. Demoted from 'checked in OR regenerated, either valid' to a build artifact carrying dsl_source_hash; the solver refuses any node whose hash ≠ the current line hash, killing the cache-coherence bug. Carries the lowered interval constraints ready for the numeric pass and surfaces every unresolved binding explicitly.
  - fields: claim_id (string) — required. well_formed (bool) — required — parsed AND type-checked against predicate_vocab. dsl_source_hash (string) — required — sha256 of the exact **Logical form** line this node derived from. quantifier {kind: forall|exists|est|none, population: POP id|null, n: int|null, ci_quantity: QTY id|null} — required. scope {conditions: list[ref]} — required, [] allowed. conjuncts (list[{predicate:{name,polarity,args:[{role,bind}]}, comparator:{op, operand, margin_qty, ci_qty}, lowered_constraint: string}]) — required, ≥1. claim_type / status / baseline — required/optional. unresolved_bindings (list[string]) — required, [] if none — any id not resolving against entity/quantity/population/set registries, surfaced not swallowed. type_honesty_ok (bool) — required — did every predicate's allowed_claim_types include claim_type.
  - example: claim_id: C01
well_formed: true
dsl_source_hash: sha256:9f21ac...
quantifier: {kind: est, population: POP:cn_biofinder1, n: 135, ci_quantity: QTY:Q_AUC_MD}
scope: {conditions: []}
conjuncts:
  - predicate: {name: PRED:RanksHighest, polarity: asserted,
      args: [{role: subject, bind: ENT:p217_MS}, {role: comparison_set, bind: {set: SET:cn8_platforms, domain: closed}}, {role: metric, bind: QTY:Q_Pscore}]}
    comparator: {op: '=', operand: QTY:Q_Pscore, margin_qty: null, ci_qty: null}
    lowered_constraint: "forall m in cn8_platforms: Pscore(p217_MS) >= Pscore(m)"
  - predicate: {name: PRED:Exceeds, polarity: asserted,
      args: [{role: subject, bind: ENT:p217_MS}, {role: baseline, bind: ENT:p181_IA}, {role: metric, bind: QTY:Q_AUC}]}
    comparator: {op: '>', operand: 0, margin_qty: QTY:Q_AUC_MD, ci_qty: QTY:Q_AUC_MD_CI}
    lowered_constraint: "AUC(p217_MS) - AUC(p181_IA) in [0.04, 0.16]"
claim_type: comparative
status: supported
baseline: ENT:p181_IA
unresolved_bindings: []
type_honesty_ok: true
- **Population / Scope Registry — logic/populations.yaml (+ the over-claim rule table)** (YAML registry + an embedded deterministic rule table consumed by protocol P2.) — Makes over-claiming a mechanical field diff. Every population a claim quantifies over is a registry entry whose generality is anchored to what the data/experiment layer actually sampled; a companion rule table (validator input) turns quantifier×generality×n×source_count into a deterministic verdict, so a tag inconsistent with n and source is caught rather than trusted (critique point 3).
  - fields: REGISTRY ENTRY: id (POP:name) — required. label (string) — required. generality (enum: sample|cohort|multi_cohort|population_estimate|claimed_universal) — required — honest tag, NOT a target. n (int|null) — required, null=not_specified. sources (list[ref]) — required, each must resolve; len==source_count. sampled_subpopulations (list[string]) — optional.
RULE TABLE (verdict = f(quantifier.kind, generality, n, source_count)): each row {when, verdict}; verdict ∈ {ok, OVER_CLAIM, UNDER_SPECIFIED}.
  - example: populations:
  - id: POP:cn_biofinder1
    label: "BioFINDER-1 prodromal-AD cohort"
    generality: cohort
    n: 135
    sources: [data/dataset.md#BioFINDER-1]      # source_count = 1
    sampled_subpopulations: []

over_claim_rules:
  # generality=cohort/sample is only self-consistent with resolved n and a bounded scope:
  - when: "generality in {sample,cohort} AND n == null"                     verdict: UNDER_SPECIFIED
  - when: "quantifier.kind == forall AND generality in {sample,cohort}"      verdict: OVER_CLAIM   # universal over sample-sized pop = hard finding
  - when: "generality == claimed_universal AND (n != null AND n < N_POP_THRESHOLD) AND source_count == 1"  verdict: OVER_CLAIM
  - when: "generality == claimed_universal AND source_count == 1 AND sampled_subpopulations == []"          verdict: OVER_CLAIM
  - when: "quantifier.kind == est AND ci_quantity == null"                  verdict: UNDER_SPECIFIED
  - else: ok
- **Typed Experiment Schema + Claim-Type→Rubric Map — logic/experiments schema & logic/claim_type_rubric.yaml** ((a) a typed schema experiments.md fields must populate; (b) a YAML rubric map whose `require` field is a boolean expression in a specified path/filter/count grammar.) — Replaces the prose 'required_experiment_design' string with a REAL boolean predicate over a typed experiment schema (critique point 4), so rubric selection AND the design-adequacy gate are deterministic path evaluations, not an LLM re-reading Setup prose.
  - fields: EXPERIMENT SCHEMA: id; arms (list[{id, type: enum{intervention|control|ablation|rct|placebo|observational}, entity: entity_id}]); baselines (list[entity_id]); population {ref: POP id}; design {family: enum, randomized: bool, blinded: bool}; metrics (list[quantity_id]); sampled_subpopulations (list[string]).
RUBRIC `require` GRAMMAR:
bool_expr := term (('AND'|'OR') term)*
term      := 'NOT'? atom
atom      := 'count(' path filter? ')' cmp int | ('any'|'all') '(' path ',' bool_expr ')' | path cmp value
path      := 'experiment' ('.' field | '[' idx ']')*
filter    := '[' field ('=='|'in') value ']'
MAP ENTRY: claim_type; required_roles (list); require (bool_expr string); rationale (string?).
  - example: # experiments.md (typed) for E01:
id: E01
arms:
  - {id: a1, type: intervention, entity: ENT:ARA}
  - {id: a2, type: control, entity: ENT:pdf_repo}
baselines: [ENT:pdf_repo]
population: {ref: POP:ara_eval_papers}
design: {family: paired_comparison, randomized: false, blinded: false}
metrics: [QTY:Q_weighted_success, QTY:Q_QA_acc]

# claim_type_rubric.yaml (require is a real predicate, no prose):
causal:
  required_roles: [cause, effect, intervention]
  require: "count(experiment.arms[type in {ablation,rct,intervention}]) >= 1 AND count(experiment.arms[type == control]) >= 1"
  rationale: "a causal claim with no control arm cannot be causally entailed by construction"
generalization:
  required_roles: [population, invariant_property]
  require: "experiment.population.ref.generality in {multi_cohort,population_estimate} OR count(experiment.sampled_subpopulations) >= 2"
comparative:
  required_roles: [subject, baseline, metric]
  require: "count(experiment.baselines) >= 1 AND all(claim.conjuncts, predicate.comparator.metric in experiment.metrics)"

  _Protocols:_
  - **P1 — Compile & source-hash coherence gate (deterministic)** — Every parse of a **Logical form** line; every CI run; before any solver pass trusts an AST node.. 1. Parser tokenizes the **Logical form** line and builds the AST. 2. Type-check each conjunct against predicate_vocab (arity, role binds_to, polarity_allowed, allowed_claim_types⊇claim_type → sets type_honesty_ok). 3. Resolve every id against entity/quantity/population/set/ref registries; unresolved ids go to unresolved_bindings (NOT silently dropped). 4. Compute dsl_source_hash = sha256(normalized line) and stamp it on the node. 5. CI runs `compile --check`: regenerate claim_graph.yaml from claims.md and `git diff --exit-code` against the checked-in copy; ANY mismatch = hard fail. 6. The solver refuses any node whose dsl_source_hash ≠ hash(current line).
    - reliability/reproducibility: Fully deterministic (Class A). The 'checked-in OR regenerated, either valid' loophole is deleted: the checked-in copy is a convenience cache that CI proves equal to the regenerated one on every merge, and the hash gate stops a stale node from ever being consumed mid-run.
    - constraints: Ecosystem must provide: stable id registries (entities, quantities, populations, sets, refs); a canonical line-normalizer (whitespace/order) so the hash is stable; CI that blocks merge on `compile --check` failure.
  - **P2 — Over-claim validator (deterministic field diff)** — Every claim whose quantifier is forall/exists/est; scored into an over-claim rate per ARA.. 1. Resolve quantifier.population to its populations.yaml entry → (generality, n, source_count, sampled_subpopulations). 2. Evaluate the over_claim_rules table rows top-to-bottom against (quantifier.kind, generality, n, source_count). 3. Emit verdict ∈ {ok, OVER_CLAIM, UNDER_SPECIFIED} with the matched rule id as the machine-readable justification. 4. OVER_CLAIM is a hard finding surfaced on the claim; UNDER_SPECIFIED is a non-penalized honest-absence flag (points to a null n or missing ci, scored equal to an honest 'not measured').
    - reliability/reproducibility: Deterministic (Class A) — no judgment. The verdict is a pure function of registry fields, so it reproduces run-to-run and the tag can no longer be trusted against sampled reality.
    - constraints: populations.yaml n and sources must resolve to the data/experiment layer (a null n cannot itself dodge the check — the 'null n + sample/cohort' row returns UNDER_SPECIFIED, keeping honest absence visible without penalty). N_POP_THRESHOLD is a corpus-level constant declared in the genre manifest, not per-ARA.
  - **P3 — Contradiction detection: symbolic pass + numeric interval joint-satisfiability** — Within an ARA and (given shared predicate_vocab version + global claim index) across a corpus.. SYMBOLIC: group conjuncts by (predicate.name, normalized args, scope); flag same-key pairs with incompatible comparator op or opposite polarity (e.g. Exceeds CMP[>0] vs Exceeds CMP[<0]; asserted vs negated). NUMERIC (the subtle ones): 1. Each quantity_id resolves via quantities.yaml to a value+CI → interval [lo,hi]. 2. Each conjunct's comparator lowers by the table: `>0`→ (a-b)>0; `> margin ci=I`→ (a-b) ∈ I; `no_sig_diff`→ (a-b) ∈ symmetric-CI-around-0; `=`→ a∈I; `~=`→ |a-b|≤ε. RanksHighest expands to the conjunction of pairwise ≥ over the closed set. 3. Assemble all constraints referencing shared quantity ids into one system; run an interval/LP feasibility check. UNSAT ⇒ numeric contradiction, with the minimal infeasible subset returned as the witness. Example: claim A asserts AUC(p217)−AUC(p181) ∈ [0.04,0.16]; a sibling claim B asserts the same difference ∈ [−0.02,0.03]; intersection empty ⇒ contradiction the symbolic pass would miss.
    - reliability/reproducibility: Symbolic + numeric passes are deterministic (Class A) given resolved intervals. Whether two contradictory claims are the SAME assertion (cross-ARA arg alignment) and the resolution of a real-world contradiction remain Class B — a narrowed judge only decides argument co-reference and adjudication, never re-derives the math.
    - constraints: quantities.yaml must expose value+CI (or a first-class 'point estimate, no CI' marker → the interval degenerates to a point and the solver notes reduced power rather than fabricating a CI). An interval/LP solver in the toolchain. Comparators with no numeric content (Causes) are skipped by the numeric pass, handled symbolically only.
  - **P4 — Deterministic rubric selection & experiment-design gate** — Whenever a claim's entailment is to be checked; selects the rubric and decides whether the linked experiment structurally CAN entail the claim.. 1. Look up claim_type → rubric entry (single deterministic lookup, no LLM). 2. Check required_roles are all bound non-null in the AST. 3. Evaluate the rubric's `require` boolean predicate over the typed experiment schema of the linked experiment(s) via the path/filter/count grammar. 4. Return design_adequate ∈ {true,false} with the failing sub-term named (e.g. 'count(arms[type==control]) >= 1 → 0'). A false here means the claim is not-entailable-by-construction — reported as a structural finding, distinct from a semantic entailment failure.
    - reliability/reproducibility: Deterministic (Class A): rubric selection and the design gate are pure function evaluations over typed fields. Only the residual entailment-QUALITY judgment (does the evidence actually support the magnitude) is deferred to P5.
    - constraints: experiments.md must populate the typed schema (arms[].type, baselines, population.ref, metrics). The path grammar evaluator must fail-closed on an unknown path (missing field ⇒ predicate false + UNDER_SPECIFIED flag, never silently true).
  - **P5 — Narrowed entailment-quality judgment (Class B)** — After P4 says design_adequate=true and P3 finds no contradiction: does the evidence support the asserted magnitude/direction at the stated scope?. Judge receives ONLY: the AST (bound predicates+intervals), the resolved evidence quantities, the selected rubric, and the population verdict. It answers a fixed for/against schema per conjunct (supported | under-supported | refuted + one-line reason anchored to a quantity id). No free-text re-derivation of numbers (P3 owns those); no type re-selection (P4 owns that).
    - reliability/reproducibility: Class B: judge ensemble (≥3), report agreement; calibration set of gold-labeled claims per claim_type; judge degrees of freedom minimized because contradiction math, type selection, and over-claim are already decided upstream — the judge only rules on evidential sufficiency.
    - constraints: Ecosystem must provide a per-claim_type calibration set and an ensemble runner; disagreement above threshold routes to human adjudication rather than a silent majority vote.

  _Metrics afforded:_
  - M09 FOL-ability (fraction of claims with a well-formed, fully-resolved logical form) → Per ARA: count claims where well_formed=true AND unresolved_bindings=[] AND type_honesty_ok=true, over total claims; honest NONE claims are excluded from the denominator's failing side (counted as legitimately non-formalizable, scored equal). [deterministic]; anti-Goodhart: Padding with vacuous predicates cannot help: predicate_vocab is closed (no inventing a predicate), every arg must resolve against a registry (fabricated ids surface in unresolved_bindings and DROP the score), and mislabeling type to look formal trips type_honesty_ok=false. Honest NONE is scored EQUAL to a present form, so there is no pressure to fabricate a logical form for an editorial claim.
  - M08 contradiction density (structural half) → P3 symbolic + numeric passes over the corpus claim graph; density = witnessed contradictions per 100 claim-pairs sharing quantity ids, with minimal-infeasible-subset witnesses attached. [deterministic]; anti-Goodhart: A compiler cannot suppress a contradiction by rephrasing prose — contradictions are computed on the AST + interval constraints, not on wording. Fabricating a wide CI to force satisfiability is caught downstream: the CI is a quantity id anchored to evidence (provenance-first), and an unjustified CI widening is a P5/provenance finding, not a free pass.
  - Over-claim rate (universal/estimation scope vs. sampled reality) → P2 verdicts aggregated: OVER_CLAIM findings per ARA, with matched rule ids. [deterministic]; anti-Goodhart: The generality tag is NOT the score input — the verdict is a diff of quantifier against resolved n and source_count, so labeling a universal claim 'cohort' to look modest still trips the forall-over-sample rule. Setting n=null to dodge returns UNDER_SPECIFIED (honest-absence, not a win), so hiding the sample size gains nothing.
  - Type-honesty & rubric-selection determinism (D1/S4) → P4: fraction of claims whose claim_type is admissible for its predicates AND whose linked experiment passes the rubric's `require` predicate; failing sub-term reported. [deterministic]; anti-Goodhart: Cannot downgrade a causal claim to 'descriptive' to dodge the control-arm requirement: the causal predicate's allowed_claim_types excludes descriptive, so the downgrade fails type-check. The design gate reads typed experiment fields, not Setup prose, so boilerplate methods text cannot fake an ablation arm.
  - Entailment quality (per-conjunct evidential sufficiency) → P5 ensemble for/against verdicts, reported with agreement and calibration-set anchoring. [reliable-anchored]; anti-Goodhart: Judge sees only the bound AST + resolved quantities, so verbose prose cannot sway it; the numbers, types, and over-claim status are pre-decided deterministically, shrinking the judge's degrees of freedom to sufficiency alone, which the calibration set audits run-to-run.

  _Tradeoffs:_ Costs and fabrication surfaces, honestly: (1) Authoring load — the single line gets long for compound claims (C01 has two conjuncts + EST + margin). Mitigation: it is still ONE line the compiler emits and a human edits; the DERIVED pretty ∀-render gives the readable view, so the terse line is a source artifact, not the reading surface. (2) Interval solver dependency — numeric joint-satisfiability needs an LP/interval engine and, critically, CIs on quantities; where evidence reports only a point estimate the interval degenerates and the numeric pass loses power. Mitigation: a first-class 'point estimate, no CI' marker so the solver reports reduced power instead of fabricating an interval — and a fabricated CI is a provenance finding since every CI is an anchored quantity id. (3) predicate_vocab coverage — a claim needing a relation not in the closed vocab must either fall to honest NONE or wait for a governed v-bump; too-small a vocab silently pushes real claims into NONE. Mitigation: track NONE-rate as a vocab-coverage signal (a rising NONE-rate flags the vocab, not the authors), and version the vocab openly. (4) Over-claim threshold gaming — N_POP_THRESHOLD is a knob; set wrong it either misses real over-claims or nags honest cohort studies. Mitigation: it lives in the shared genre manifest (corpus-level, not per-ARA), so no single author can tune it. (5) Cross-ARA argument co-reference (are two Exceeds about the same entities?) is genuinely Class B and can produce false-contradiction witnesses if entity ids are not globally reconciled — mitigated by the narrowed P3 judge deciding only co-reference, never the math.

  _Open questions:_ (1) Disjunction and genuine uncertainty ('X or Y causes Z') are deliberately out of the grammar (only AND-conjunction); expressed today via EST/proportion quantifiers, but a claim that is irreducibly disjunctive is forced to NONE — is that the right call, or does the vocab need a guarded OR with defined truth conditions? (2) EST truth conditions assume the reported CI is a valid frequentist/Bayesian interval for the population parameter; the solver treats disjoint CIs as contradiction, but two CIs from different estimators/priors can legitimately differ without contradicting — the numeric pass may over-flag until estimator metadata is carried on the quantity. (3) Temporal and conditional scope beyond a flat conditions list (claims that hold only under a regime that itself is a claim) need scope to reference other claim ids, risking cycles in the graph — resolver semantics for claim-conditioned scope are unspecified. (4) N_POP_THRESHOLD is a single scalar standing in for 'representative enough'; real generality is multi-dimensional (ethnicity, site, time) and a single n cannot capture it — the sampled_subpopulations coverage check is a first step, not a solution. (5) Whether the DERIVED ∀-render should itself be diffable in review (so scientists review the pretty form and the tool round-trips edits back into the terse line) is an ergonomics question that could reintroduce a second authored surface if done carelessly.

  _Changes from critique:_ Addresses all six critique points directly. (1) COMPOUND CLAIMS: the grammar now has `conjunct ('AND' conjunct)*`; C01 is re-encoded in full with both the RANKS_HIGHEST/P-score conjunct AND the EXCEEDS/AUC-margin conjunct — nothing is dropped. (2) STAT DEFINED: the undefined `STAT(pop,n)` is replaced by `EST(pop, n, ci=QTY)` with explicit truth conditions — it asserts the population parameter lies in the named CI interval, estimated from n samples; n has NO truth-conditional role (it feeds only the over-claim validator), and two EST claims about the same parameter with disjoint CIs are a numeric contradiction. (3) OVER-CLAIM VALIDATOR: added a deterministic rule table — `generality=cohort` requires resolved n + single source; a `FORALL` (or open-ended EST) over a population whose resolved generality is sample/cohort is a HARD finding, computed as a field diff, not trusted from the tag. (4) REAL RUBRIC GRAMMAR: `required_experiment_design` is now a boolean predicate over a typed experiment schema (`count(experiment.arms[type in {ablation,rct}]) >= 1 AND count(experiment.arms[type == control]) >= 1`), with a specified path/filter/count grammar — no prose. (5) CACHE COHERENCE: the checked-in AST is demoted to a build artifact carrying `dsl_source_hash`; the solver refuses any node whose hash ≠ the current line's hash, and CI runs `compile --check` (regenerate-and-diff, hard fail on mismatch). 'Either is valid' is deleted. (6) INTERVAL LOWERING: comparators explicitly lower to interval/linear constraints; a second numeric joint-satisfiability pass (UNSAT ⇒ contradiction) is specified with the lowering table.

  _Adopted from competitor:_ (1) Numeric constraint satisfiability — CLF's best idea: lower every comparator to an interval constraint over quantity ids and check joint satisfiability. I adopt it as a first-class second solver pass and specify the exact lowering table (critique point 6). (2) `domain_extent: closed|open` — but I relocate it onto set-valued predicate ARGUMENTS (the enumerated comparison set of RANKS_HIGHEST), where it actually belongs, and keep population generality as the separate axis the over-claim check reads — so the two distinct 'domains' (who the claim holds over vs. what it was compared against) stop being conflated. (3) The claim_type↔predicate cross-validation (a soft claim_type may not use a predicate whose `allowed_claim_types` excludes it) so you cannot dodge a hard rubric by mislabeling type. (4) Multi-conjunct AND-ed predicate lists.

  _Why it wins:_ CLF authors the verbose structured YAML by hand and DERIVES the render string (round-trip equality check). That inverts the ergonomics: the hand-authored surface is a ~30-line nested YAML block per claim — the largest fabrication-and-drift surface in the whole design, and miserable to write for the scientist the format is supposed to serve. My single authored artifact is ONE terse line a human writes and greps; the rich AST is the derived side, gated by a content hash of the exact line it came from. One authored form beats two views to keep equal. Beyond ergonomics I add three things CLF leaves unspecified: (a) a deterministic over-claim validator with an explicit quantifier×generality×n×source_count truth table (CLF reads `domain_extent` but never checks it against sampled reality); (b) a real field-predicate grammar over a typed experiment schema for rubric selection, replacing prose 'requires_enumerated_alternatives' strings that still need an LLM to adjudicate; (c) a hard cache-coherence gate (source-hash + CI regenerate-and-diff) so a stale AST can never silently pass. A genuine merge is possible and strictly better: keep my single-line authoring + hash gate, keep CLF's interval solver, and expose CLF's ∀-render as a DERIVED human-facing pretty-print of my AST (best of both — terse to write, pretty to read).


---


## ENTITY — Entity identity & ontology

_Class A — format-recoverable determinism_


**Judge rationale:** The mandate front-loads two things: (1) afford the target metrics AND make them harder to game, and (5) honesty about fabrication surfaces. All four proposals share an essentially identical skeleton (typed entities.yaml, local IDs, optional xrefs + embedding anchor, honest-absence enum {resolved/ambiguous/unmapped/not_applicable}, an append-only resolution log, and ID-based cross-layer citation), so the skeleton is not discriminating. What separates them is the strength of the *verification* and *anti-Goodhart* machinery bolted onto that skeleton.

Proposals #2 and #3 (both Sonnet) go furthest here and are complementary. #2 brings the most complete anti-gaming suite: extraction only from already-typed upstream structure (real Class-A determinism, no fresh NLP reinterpretation of prose), a corroboration check tying entity citations to literal prose, and an embedding reproducibility_check that recomputes from a content hash instead of trusting a stored vector — three distinct, concrete Goodhart plugs aimed squarely at fabrication surfaces. #3 brings the strongest single Class-B reliability idea: a two-independent-resolver agreement gate with a blind second pass, plus resolution_attempted to honestly separate "resolver never ran" from "ran, found nothing," and not_applicable_reason carrying actual sub-floor similarity scores. Together they represent the two best answers to "how do you make the fallible external step reliable and hard to fake."

Proposals #0 and #1 (both gpt-5.5-codex) are strong but rank below. #0 is the tightest and most explicit about metric affordance — its Tags-never-used-by-metrics rule cleanly kills tag-stuffing, its role-typed citation contract (subjects/measures/comparators) is elegant, and it states the M10 computation. But its verification is existence-only (registry_resolved confirms a CURIE exists, not that the mapping is correct), so a real-but-wrong term passes as "verified" — a correctness hole that #2's recompute+corroboration and #3's agreement gate both close. #1 is the most complete schema (strict id grammar, deprecation/redirects_to for entity retirement — the only proposal to handle identity lifecycle, rejected-candidate logging, resolver_runs thresholds), but it over-reaches into a full semantic edge graph with compiler_inference/resolver_inference assertions that introduce a NEW unverified fabrication surface without a corresponding verification gate — scope creep that trades focus for a hole. On the mandate's fabrication-discipline axis, #0's tighter, better-defended surface edges out #1's richer-but-looser one.

Net: #2 and #3 win because their verification actually attacks correctness and gaming rather than mere existence, and they are the two designs whose fabrication surfaces are most honestly named and most concretely plugged.


### Finalist A (refined)

> _Judge critique it answered:_ Proposal #2 (The Entity Ledger, Sonnet 5) wins on anti-gaming density, but three of its signature defenses are weaker than advertised — tighten them or they become the holes.

1) The corroboration check is lexical, not semantic, so it is simultaneously gameable AND brittle. Requiring an entity's canonical_name/alias to appear as a "literal/high-similarity substring" in the citing block's own text does NOT verify the claim is *about* the entity — it verifies a string is present, which an author trivially satisfies by pasting the name. Meanwhile it produces false negatives on legitimate reference-by-pronoun, by un-aliased abbreviation, or by aggregate ("all three biomarkers achieved..."). You never define the "high-similarity" threshold, the tokenization, or the failure action (drop the ref? flag? fail the build?). Specify: threshold value, per-kind alias-expansion rules, and that corroboration failure DOWNGRADES coverage credit rather than silently dropping the citation (silent drop is itself a gaming lever).

2) reproducibility_check (recompute embedding from text_hash) defeats stored-vector forgery but nothing else. It proves the embedding model is deterministic on the anchor_text; it does not prove the anchor_text faithfully represents the entity — garbage anchor text recomputes to pass. And it will hard-fail EVERY anchor the moment you bump "specter2@2025-09," with no re-anchoring migration protocol specified. State: (a) an anchor-text construction spec (which fields, in what order) so the text itself isn't a fabrication surface, and (b) a versioned re-anchoring migration that distinguishes "model changed" from "vector forged" instead of mass-failing.

3) match_type includes "broad" and you *assert* broad terms "do not move the score," but the schema never states the M10 weighting. Without an explicit exact>close>related>broad weight vector (and a decision on whether broad counts as `resolved` at all for the denominator), agents will farm broad top-level EFO/MeSH terms to inflate coverage. Publish the weights in the schema, not the prose.

4) verification: verified_lookup only confirms the ext_id EXISTS in the pinned snapshot — it does not confirm it is the *correct* term. A real-but-wrong MeSH ID passes. You have no independent second-resolver agreement gate (Proposal #3's one genuinely strong idea). Borrow it — but see its independence caveat.

5) You conflate "resolver never ran" with "ran, found nothing" under `unmapped`, which corrupts the honesty of the M10 denominator. Proposal #3's `resolution_attempted: bool` cleanly separates these; adopt it.

6) The cross-ARA `global_entity_id` commons is hand-waved: assigning a GEC is itself an entity-resolution problem with the same fabrication surface, and you name no authority, no minting protocol, and no defense against two ARAs binding the same GEC to different real-world entities. Either specify the merge protocol (shared-xref agreement + embedding-neighbor gate + adjudication) or drop the commons from any scored metric until it exists.

**Entity Identity Layer: Anchored Registry + Hybrid Two-Arm Resolution (deterministic literal ∧ semantic), with a Deterministic Status Machine**  ·  _source: claude-opus-4-8 (finalist B, revised from claude-sonnet-5 Proposal #3)_

A single typed sidecar, logic/entities.yaml, gives every entity that is mechanically referenced by another layer (claim, experiment, quantity ledger row, FOL symbol, or concepts.md heading) a stable local ID, an optional set of external-ontology xrefs, and a reproducibility-checked embedding anchor. The core fix to the prior design is that the reliability of the Class-B external step no longer rests on "two LLMs agreeing": a xref only reaches `resolved` when a DETERMINISTIC literal matcher (exact + registered-synonym lookup against the pinned vocabulary's own label set) and a SEMANTIC LLM linker independently converge on the same external ID — decorrelated evidence channels, not two correlated priors. Inclusion is mechanical (no human decides "load-bearing"), the resolution status is a deterministic function of the append-only log (a written state machine, not a judgment call), not_applicable is gated by per-vocabulary floors calibrated against a labeled gold set, self-reported resolver scores are stored for audit but barred from every metric, embeddings are verified by recompute-from-hash against a specified anchor-text construction, and FOL symbols get a deterministic collision-suffixing rule. Honest-absence is preserved throughout: an entity may be registered and `unresolved` at zero penalty, so there is never pressure to fabricate a mapping or to omit an entity to inflate a ratio.

- **logic/entities.yaml — canonical entity registry** (YAML sidecar, one per ARA at logic/entities.yaml; float vectors live in a corpus-shared vector store keyed by input_text_hash, referenced by pointer.) — One typed record per MECHANICALLY-REQUIRED entity (see P1 inclusion rule): every concept/method/variable/measure/organism/gene-protein/disease/dataset/tool referenced by ID from any other layer. Each record carries a stable local ID, hybrid-resolved xrefs, a recompute-checked embedding anchor, an honest resolution_status, and a deterministic FOL symbol. This is the single join key all other layers cite instead of free text.
  - fields: id: string 'X-<kind>-<slug>' — required — stable; slug derived from canonical_label, id assigned by (kind, canonical_label) key not insertion order | kind: enum{concept,method,variable,measure,organism,gene_protein,disease,dataset,tool_software,population_cohort,other} — required | canonical_label: string — required | aliases: list[string] — required (may be []) | fol_symbol: string — required — deterministic per P1 sanitize+suffix rule; unique, validated against symbol_table.yaml | definition_ref: {file, anchor} — required — pointer into prose where defined (keeps registry thin) | source_anchor: {file, locator} — required — provenance of first introduction | resolution_attempted: bool — required — distinguishes 'resolver never ran' from 'ran, found nothing' | resolution_status: enum{resolved,ambiguous,unresolved,not_applicable} — required — COMPUTED by P3 state machine, not hand-set | xrefs: list[xref] — required (may be []) — see xref object; only entries with verification∈{verified_exact,verified_human} count for metrics | candidates: list[xref-without-verification] — required only when status∈{ambiguous} — the competing hits that blocked resolution | not_applicable_reason: {text, calibration_ref, deterministic_arm_result, semantic_best_score} or null — required non-null when status=not_applicable | embedding_anchor: embedding_anchor object or null — required key (null allowed, scored equal) | global_entity_id: string or null — required key — cross-ARA commons id if matched | referenced_by: list[{layer,id}] — COMPUTED/cached, re-derivable by validator, never hand-authored
  - example: schema_version: "2.0"
calibration_ref: "cal-2026Q2-v4"
entities:
  - id: X-concept-p-tau217-ms
    kind: concept
    canonical_label: "p-tau217 (mass spectrometry)"
    aliases: ["p217_MS", "phospho-tau217 (MS)"]
    fol_symbol: ptau217_ms
    definition_ref: {file: logic/concepts.md, anchor: "p-tau217-mass-spectrometry"}
    source_anchor: {file: logic/concepts.md, locator: "## p-tau217 (mass spectrometry)"}
    resolution_attempted: true
    resolution_status: resolved   # computed: both arms converged on MeSH D000071071
    xrefs:
      - vocabulary: MeSH
        ext_id: "D000071071"
        label: "tau Proteins, phosphorylated"
        url: "https://meshb.nlm.nih.gov/record/ui?ui=D000071071"
        match_type: close
        raw_score: 0.91          # AUDIT ONLY — barred from every metric
        snapshot_version: "MeSH-2026AA"
        deterministic_arm: {matched: true, matched_label: "phospho-tau217", match_kind: synonym}
        semantic_arm: {resolver: "entity-linker-v0.4", model: "claude-opus-4.6", proposed: true, raw_score: 0.91}
        verification: verified_exact   # literal synonym hit ∧ semantic proposal agree
        calibration_ref: "cal-2026Q2-v4"
        resolved_at: "2026-06-30T14:05:47Z"
        verified_by: "hybrid-gate-v0.4"
    embedding_anchor:
      model: "specter2@2025-09"
      anchor_text_rule: "canonical_label + ' || ' + definition_prose(definition_ref)"
      input_text_hash: "sha256:9f2a...c31"
      vector_ref: "vectors/entities.parquet#hash=9f2a...c31"
      computed_at: "2026-06-30T14:06:02Z"
      reproducibility_check: pass
      recomputed_at: "2026-07-01T02:00:00Z"
      cosine_to_stored: 0.99998
    global_entity_id: "GEC-000481"
    referenced_by: [{layer: claims, id: C01}, {layer: experiments, id: E01}]

  - id: X-measure-p-score
    kind: measure
    canonical_label: "P-score (SUCRA analog)"
    aliases: ["P-score"]
    fol_symbol: pscore
    definition_ref: {file: logic/concepts.md, anchor: "p-score-sucra-analog"}
    source_anchor: {file: logic/concepts.md, locator: "## P-score (SUCRA analog)"}
    resolution_attempted: true
    resolution_status: not_applicable
    not_applicable_reason:
      text: "Paper-internal ranking construct; no STATO/MeSH/EFO term for this exact estimator."
      calibration_ref: "cal-2026Q2-v4"
      deterministic_arm_result: no_literal_or_synonym_hit
      semantic_best_score: 0.22   # below STATO floor 0.71 in cal-2026Q2-v4
    xrefs: []
    embedding_anchor:
      model: "specter2@2025-09"
      anchor_text_rule: "canonical_label + ' || ' + definition_prose(definition_ref)"
      input_text_hash: "sha256:77bd...02e"
      vector_ref: "vectors/entities.parquet#hash=77bd...02e"
      computed_at: "2026-06-30T14:06:09Z"
      reproducibility_check: pass
      recomputed_at: "2026-07-01T02:00:00Z"
      cosine_to_stored: 0.99997
    global_entity_id: null
    referenced_by: [{layer: claims, id: C01}]
- **xref object (nested in entities.yaml)** (YAML object) — One candidate or confirmed mapping from a local entity to an external controlled-vocabulary term, recording BOTH arms' independent results so the agreement gate is auditable and raw scores are quarantined from metrics.
  - fields: vocabulary: enum{MeSH,EFO,GO,NCBITaxon,HGNC,UniProt,Wikidata,UO,STATO,ICD11,PROSPERO,other} — required | ext_id: string — required | label: string — required — the vocabulary's own preferred label for ext_id | url: string — required | match_type: enum{exact,close,broad,related} — required — semantic scope of the mapping, independent of score | raw_score: float[0,1] — required — resolver self-report, AUDIT ONLY, barred from every metric | snapshot_version: string — required — pinned vocabulary release | deterministic_arm: {matched: bool, matched_label: string|null, match_kind: enum{preferred_label,synonym,none}} — required — literal matcher result | semantic_arm: {resolver, model, proposed: bool, raw_score} — required — LLM linker result | verification: enum{verified_exact,verified_human,candidate_semantic_only,unverified,stale,failed} — required — ONLY verified_exact/verified_human count for metrics | calibration_ref: string — required — which resolver_calibration snapshot governed this decision | resolved_at: datetime — required | verified_by: string — required
  - example: {vocabulary: EFO, ext_id: "EFO:0004616", label: "blood protein measurement", url: "https://www.ebi.ac.uk/efo/EFO_0004616", match_type: broad, raw_score: 0.58, snapshot_version: "EFO-3.68.0", deterministic_arm: {matched: false, matched_label: null, match_kind: none}, semantic_arm: {resolver: "entity-linker-v0.4", model: "claude-opus-4.6", proposed: true, raw_score: 0.58}, verification: candidate_semantic_only, calibration_ref: "cal-2026Q2-v4", resolved_at: "2026-06-30T14:03:00Z", verified_by: "hybrid-gate-v0.4"}   # LLM-only, no literal hit -> NOT resolved, does not score
- **ontology/resolver_calibration.yaml — corpus-shared calibration artifact** (YAML, corpus-level, immutable once published under a version tag.) — Per-vocabulary decision thresholds and their empirical provenance, so not_applicable floors and any score-derived judgement are grounded in a labeled gold set rather than an asserted global constant. Shared across all ARAs in the corpus and versioned; every entity's not_applicable_reason and every xref cite the calibration_ref they used.
  - fields: calibration_ref: string — required — version tag | gold_set: {id, n_entities, n_vocab_labeled, curated_by, curated_at} — required — provenance of the labeled data | per_vocabulary: map[vocab -> {na_floor: float, resolved_floor: float, precision_at_resolved_floor: float, recall_at_resolved_floor: float, n_gold: int}] — required — thresholds derived from the gold set, one row per vocabulary | notes: string — required
  - example: calibration_ref: "cal-2026Q2-v4"
gold_set: {id: "gold-biomarker-500", n_entities: 500, n_vocab_labeled: 6, curated_by: "ontology-wg", curated_at: "2026-04-01"}
per_vocabulary:
  MeSH:   {na_floor: 0.55, resolved_floor: 0.80, precision_at_resolved_floor: 0.94, recall_at_resolved_floor: 0.71, n_gold: 180}
  EFO:    {na_floor: 0.60, resolved_floor: 0.78, precision_at_resolved_floor: 0.91, recall_at_resolved_floor: 0.64, n_gold: 90}
  GO:     {na_floor: 0.62, resolved_floor: 0.83, precision_at_resolved_floor: 0.96, recall_at_resolved_floor: 0.69, n_gold: 70}
  STATO:  {na_floor: 0.71, resolved_floor: 0.85, precision_at_resolved_floor: 0.88, recall_at_resolved_floor: 0.52, n_gold: 40}
notes: "Floors are per-vocab because score distributions differ; STATO sparse so na_floor high to avoid dumping paper-internal stats there. Recompute each quarter as vocab snapshots and models change."
- **logic/symbol_table.yaml — FOL/CLAIMFOL symbol table** (YAML, derived deterministically from entities.yaml by P1; validated by a uniqueness assertion.) — Bijective map between fol_symbol and entity id, validated unique, with the deterministic collision-suffixing rule made explicit so CLAIMFOL correctness cannot silently break when two labels sanitize to the same base symbol.
  - fields: symbol: string — required — final unique fol_symbol | entity_id: string — required | base: string — required — sanitized base before suffixing | suffix: int or null — required — collision suffix (null if base was unique)
  - example: symbols:
  - {symbol: ptau217_ms, entity_id: X-concept-p-tau217-ms, base: ptau217_ms, suffix: null}
  - {symbol: pscore, entity_id: X-measure-p-score, base: pscore, suffix: null}
  - {symbol: ratio, entity_id: X-variable-abeta-ratio, base: ratio, suffix: null}
  - {symbol: ratio_2, entity_id: X-variable-tau-ratio, base: ratio, suffix: 2}   # collision: second-by-entity-id gets _2
- **Inline entity anchors + Entity refs (prose modification of concepts.md, claims, experiments, related_work)** (typed-markdown: heading anchor tag + ID-tagged bullet lists.) — Keeps prose fully human-readable while making every heading machine-joinable to the registry, and converts free-text 'Related concepts' and claim/experiment Tags into ID references — with a corroboration constraint that blocks padding.
  - fields: heading anchor: '{#entity: X-...}' suffix on every '## Term' heading — required | Related concepts (by ID): list[X-...] replacing prose names — required | Entity refs: list[X-...] on each claim/experiment/solution block — required — CORROBORATION CONSTRAINT: each referenced entity's canonical_label or an alias must appear as a literal or high-similarity substring in that block's own Statement/Evidence text, else the ref is flagged uncorroborated and does not count for M13
  - example: ## p-tau217 (mass spectrometry) {#entity: X-concept-p-tau217-ms}
- **Definition**: Tau phosphorylated at threonine 217, measured via mass spectrometry...
- **Related concepts (by ID)**: [X-method-network-meta-analysis, X-measure-p-score]

## C01: p-tau217 by mass spectrometry has the highest diagnostic accuracy
- **Statement**: ...p217_MS achieved the highest rank (P-score = 0.859)...
- **Entity refs**: [X-concept-p-tau217-ms, X-measure-p-score]   # both labels/aliases appear literally in Statement -> corroborated

  _Protocols:_
  - **P1 — Deterministic extraction, mechanical inclusion, ID + FOL-symbol minting** — Every compile/recompile, before any external resolution.. 1. INCLUSION (objective, no discretion): enumerate the required entity set = every entity referenced by ID from a claim Entity refs, experiment Entity refs, a quantity-ledger row's entity field, a FOL symbol in CLAIMFOL, or a concepts.md heading. No 'load-bearing' judgement exists; a validator asserts every such reference resolves to a registered id and fails compile otherwise. 2. Extract candidates ONLY from already-typed upstream structure (headings, typed keys), never a fresh NLP sweep of raw prose. 3. Canonicalize label; check existing entities.yaml for a matching (kind, canonical_label/alias) before minting, so ids are stable across recompiles. 4. Mint id='X-<kind>-<slug>'. 5. FOL symbol: base = sanitize(canonical_label) [lowercase; non-alphanumeric -> underscore; collapse repeats; trim]. If base already maps to a DIFFERENT entity id in symbol_table, append '_2','_3',... assigned in ascending entity-id order (stable, deterministic). Write symbol_table.yaml and assert bijectivity. 6. Initialize resolution_attempted=false, resolution_status=unresolved, xrefs=[], embedding_anchor=null.
    - reliability/reproducibility: Class A / deterministic: identical typed upstream always yields the identical entity set, ids, and symbols, because minting re-keys existing structure and collision suffixing is a pure function of the stable id ordering.
    - constraints: Requires sibling layers to carry typed Entity refs / symbol fields; inherits their determinism. Requires a validator that fails compile on any dangling reference (this is what makes the M10 denominator ungameable).
  - **P2 — Hybrid two-arm resolution (deterministic literal ∧ semantic)** — After P1, for each registered entity, against pinned vocabulary snapshots.. 1. ARM A (deterministic literal matcher, Class A): normalize canonical_label and each alias (case/whitespace/punctuation/greek-latin); query the pinned vocabulary's own preferred-labels and registered synonyms; record every ext_id whose preferred_label or synonym matches exactly, with match_kind. This arm uses NO model. 2. ARM B (semantic linker, Class B): an LLM/embedding linker proposes candidate ext_ids with raw_score. 3. Record both arms' independent results in each xref and append full detail to the resolution log. INDEPENDENCE DEFINITION: two arms are independent iff they draw on disjoint evidence channels — Arm A on literal string identity within the vocabulary's own label set, Arm B on distributional/semantic similarity. TWO LLMs sharing pretraining are NOT independent and MUST NOT both occupy the two arms; at least one arm must be the non-model literal matcher. 4. Hand the paired result to P3 to compute status.
    - reliability/reproducibility: Class B, but reliability comes from decorrelated corroboration: `resolved` means a semantic guess was confirmed by a literal registry hit, so shared-prior LLM hallucinations cannot manufacture agreement. Arm A is fully reproducible; Arm B is logged for reproducibility with pinned model+snapshot.
    - constraints: Ecosystem must provide programmatic access to each vocabulary's preferred labels and synonym sets (APIs or downloadable label dumps) and pinned snapshot versions. Vocabularies without a machine-readable synonym set can only ever reach candidate_semantic_only, never resolved — and that limitation is surfaced honestly, not hidden.
  - **P3 — Deterministic status state machine** — Immediately after P2, and re-run whenever the log gains an attempt.. status is a PURE FUNCTION of the xref set + calibration floors (not chosen by a resolver): (a) If Arm A and Arm B converge on the SAME ext_id -> that xref.verification=verified_exact and entity.resolution_status=resolved. (b) If exactly one arm produces a hit at/above the vocab's resolved_floor and the other abstains -> xref.verification=candidate_semantic_only (if only Arm B) or stays candidate; entity.resolution_status=ambiguous only if there are competing candidates, else unresolved. (c) If the arms CONFLICT (each hits a different ext_id) OR Arm A returns >1 literal hit -> resolution_status=ambiguous, all competitors stored in candidates[]; a tiebreak MUST run: either a human (verification=verified_human) or an independent deterministic crosswalk (e.g. UMLS Metathesaurus mapping) — a third correlated LLM is NOT an eligible tiebreaker. Disagreement can NEVER silently yield resolved. (d) If neither arm hits and semantic best < vocab na_floor AND Arm A found no literal/synonym match -> eligible for not_applicable (requires non-null reason + calibration_ref); otherwise resolution_status=unresolved. (e) Human override (verified_human) is the only path to resolved without dual-arm agreement and is always tagged as such.
    - reliability/reproducibility: Class A given the log: because status is computed, an auditor re-running the function on the same log gets the same status — this is the written, deterministic resolution rule the Class-C auditability mandate demands. Class B only in the human-tiebreak branch, which is explicitly tagged.
    - constraints: Requires the append-only resolution log (below) to be complete, and a published crosswalk source or human adjudication queue for branch (c).
  - **P4 — not_applicable gating via calibrated per-vocabulary floors** — Whenever P3 reaches branch (d) and not_applicable is proposed.. 1. Load resolver_calibration.yaml at the ARA's calibration_ref. 2. Assert Arm A returned no_literal_or_synonym_hit across ALL queried vocabularies. 3. Assert semantic best score < na_floor for EACH vocabulary where the entity's kind is plausibly in scope. 4. Only then set not_applicable, writing reason.text, calibration_ref, deterministic_arm_result, and semantic_best_score. Otherwise status stays unresolved (honest 'we did not find one', not 'no such term exists').
    - reliability/reproducibility: Class B, reproducible against a pinned calibration snapshot: the floors are empirical (precision/recall logged), so not_applicable is a threshold decision with provenance, not theater. Re-running against the same calibration_ref reproduces the outcome.
    - constraints: Ecosystem must maintain and version resolver_calibration.yaml from a curated gold set, and recompute it when models or vocab snapshots change (stale calibration_ref triggers re-resolution).
  - **P5 — Embedding anchor construction + recompute-from-hash gate** — When populating any embedding_anchor and on every periodic audit.. 1. Construct anchor_text by the FIXED rule: canonical_label + ' || ' + definition_prose(resolve definition_ref). This spec makes the hashed input reproducible and non-forgeable — you cannot swap in flattering text without changing the hash and failing recompute. 2. input_text_hash = sha256(anchor_text); store vector in the corpus store keyed by that hash. 3. reproducibility_check: recompute anchor_text from the current prose, recompute the hash (must equal stored), re-embed with the pinned model, and compare to the stored vector (cosine >= 0.9999). Set reproducibility_check=pass/fail/stale (stale if model version moved) and record cosine_to_stored + recomputed_at. 4. A fail/stale/not_run anchor scores as ABSENT for anchoredness — a vector pointing at garbage earns nothing.
    - reliability/reproducibility: Class A verification of a Class-B artifact: the recompute is deterministic given the pinned model; a wrong or forged vector is detectable, closing the gap the competitor's design also fixed but which my prior draft lacked.
    - constraints: Ecosystem must pin embedding model versions and provide a corpus vector store addressable by content hash; auditors need enough model access to recompute (or a signed recompute service).
  - **P6 — Cross-ARA entity commons resolution** — When linking the same real-world entity across independently compiled ARAs.. 1. Two local entities in different ARAs are candidate-same iff they share a verified_exact/verified_human xref ext_id OR their embedding anchors are mutual nearest neighbors above a calibrated commons floor. 2. On confirmation, assign/share a global_entity_id (GEC-...). 3. Shared-xref links are reliable-anchored; embedding-only links are stored as candidates, never auto-promoted to verified.
    - reliability/reproducibility: Class B: reliable via shared literal ext_ids (deterministic once resolved), weaker via embeddings (kept as candidate). Provides dedup and cross-ARA recognition without fabricating identity.
    - constraints: Requires a corpus-level global entity registry service and a commons floor in the calibration artifact.

  _Metrics afforded:_
  - M10 — controlled-vocabulary referenceability → numerator = registered entities with at least one xref where verification∈{verified_exact,verified_human}; denominator = the MECHANICAL required set from P1 (every entity referenced by another layer). Ratio reported alongside honest counts of unresolved and not_applicable. [reliable-anchored]; anti-Goodhart: Denominator is mechanical (P1 validator), so an agent cannot shrink it by declaring terms 'not load-bearing' — that lever is deleted. Numerator counts only dual-arm-verified xrefs, so a correlated-LLM false agreement can't inflate it (needs a literal registry hit). unresolved/not_applicable are scored EQUAL to a resolved mapping wherever the term is genuinely field-specific, so there is zero pressure to fabricate. raw_score is barred, so a padded confidence can't move the metric.
  - M12 / M64 — anchoredness (latent-space) → fraction of required entities whose embedding_anchor has reproducibility_check=pass. [deterministic (given pinned model)]; anti-Goodhart: Anchor text is a fixed function of canonical_label+definition (P5), so you cannot embed flattering or padded text; the recompute-from-hash gate makes a fail/forged vector score as absent. No credit for a vector you can't reproduce.
  - M13 — claims↔concepts consistency → exact set join: for each claim, its Entity refs must be a subset of the registry, and each ref must pass the corroboration check (label/alias literally present in the claim's own text). Consistency = deterministic set agreement, not string overlap. [deterministic]; anti-Goodhart: Corroboration constraint blocks padding a claim with entity refs it doesn't actually discuss; uncorroborated refs are dropped, so stuffing the list can only lower, never raise, the score.
  - Resolver precision (calibration-audited) → periodic evaluation of verified_exact xrefs against the labeled gold set; per-vocabulary precision/recall stored in resolver_calibration.yaml. [reproducible]; anti-Goodhart: Because the metric is computed on a held gold set with logged provenance, tuning thresholds to inflate coverage shows up as falling precision; the calibration provenance (n_gold, precision at floor) is public and versioned, so a floor moved to game coverage is visible.
  - Cross-ARA entity recognition rate → share of entities linked to a global_entity_id via a SHARED verified xref ext_id (reliable) vs. embedding-only candidates (reported separately, not counted as confirmed). [reliable-anchored]; anti-Goodhart: Only shared literal ext_ids count as confirmed identity; embedding-only matches stay candidates, so you cannot inflate recognition by tuning a similarity threshold.

  _Tradeoffs:_ Honest costs and residual fabrication surfaces: (1) The deterministic literal arm depends on vocabularies exposing usable synonym/label sets; vocabularies that don't (or sparse ones like STATO) will legitimately show low resolved rates and many candidate_semantic_only — this is honest but means M10 is not comparable across fields without normalizing by vocabulary coverage; I surface per-vocabulary counts rather than a single blended number. (2) Calibration is itself a gold-set artifact and can be gamed by curating an easy gold set; mitigated by requiring gold_set provenance (curator, n, date) to be published and by reporting recall alongside precision so a cherry-picked easy set is detectable, but a corrupt curator remains a trust anchor the ecosystem must govern. (3) The human-tiebreak and verified_human paths are genuine Class-B/discretion points; I bound them by tagging every human decision distinctly so their share is auditable and can't masquerade as automated dual-arm agreement. (4) match_type is still a semantic label assigned by the semantic arm; a resolver could tag a broad mapping as 'close'. Mitigation: match_type never affects whether an xref counts (only verification does), so mislabeling scope doesn't move metrics — it only mildly misinforms human readers, and the deterministic arm's match_kind (preferred_label vs synonym) provides an independent check. (5) The corroboration substring check can be satisfied by mentioning an entity name without genuinely depending on it; mitigation is that this only affects M13 corroboration (presence), not truth of the claim, which is a different layer's job. (6) Embedding recompute assumes model determinism; some models are non-deterministic across hardware — mitigated by the cosine tolerance (>=0.9999) rather than bit-exact match, and stale flagging on version drift.

  _Open questions:_ 1) Governance of resolver_calibration.yaml: who curates the gold set, how often floors are recomputed, and how to prevent an easy-gold-set attack are ecosystem-governance questions this design assumes solved but does not itself solve. 2) The independence guarantee is only as strong as the deterministic arm's synonym coverage; for vocabularies with poor synonym curation, Arm A degrades toward abstention and the gate reduces to 'semantic-only never resolves', which is safe but pessimistic — a normative-mapping/crosswalk service (UMLS-style) would materially raise recall and is a dependency I flag rather than provide. 3) When two vocabularies both offer a valid exact term (e.g., MeSH and Wikidata), the design records both but does not prescribe a canonical preferred vocabulary per kind — left to a corpus policy. 4) Cross-ARA embedding-only candidate promotion: no principled, non-gameable rule yet exists for turning strong embedding neighbors into confirmed identity without a shared ext_id; kept deliberately as candidate-only. 5) Non-deterministic embedding models across hardware may cause spurious reproducibility_check failures; whether the ecosystem should mandate deterministic-inference embedding endpoints is unresolved.

  _Changes from critique:_ Directly resolved all seven critique points. (1) INDEPENDENCE: the agreement gate now requires one deterministic literal/synonym matcher and one semantic LLM linker; independence is defined explicitly as disjoint evidence channels (literal string identity in the vocabulary's own label set vs. distributional similarity); two LLMs sharing pretraining are declared non-independent and cannot both count. (2) OMISSION SURFACE: deleted "genuinely load-bearing"; inclusion is now a mechanical rule — ANY entity referenced by a claim, experiment, quantity, FOL symbol, or concept heading MUST be registered, and a validator enforces it, so no agent controls the M10 denominator. (3) FLOOR CALIBRATION: replaced the single global 0.4 floor with per-vocabulary floors in a corpus-shared, versioned resolver_calibration.yaml derived from a labeled gold set, with logged provenance (gold set id, N, precision/recall at threshold); every not_applicable and every resolution cites the calibration snapshot it used. (4) match_confidence: renamed to raw_score, explicitly audit-only and BARRED from every metric; the verification enum, not the float, carries reliability weight. (5) STATE MACHINE: wrote the disagreement resolution as a deterministic function of the log — convergence→resolved, single-arm→ambiguous/candidate, conflict→ambiguous with mandatory tiebreak (human or independent crosswalk), and disagreement can never silently produce `resolved`. (6) EMBEDDING RECOMPUTE: added a deterministic anchor_text construction spec, input_text_hash, and a recompute-from-hash reproducibility_check; a failed or unrun check scores as absent. (7) FOL COLLISIONS: specified sanitize→lowercase→non-alnum-to-underscore, then ascending-entity-id suffixing (_2,_3,…) validated unique in a symbol_table.yaml.

  _Adopted from competitor:_ Five mechanisms from The Entity Ledger: (1) the embedding reproducibility_check that recomputes the vector from a content hash rather than trusting a stored vector — I extend it with a deterministic anchor-text construction spec so the hashed input itself is not forgeable; (2) the corroboration check requiring an entity's canonical_name/alias to appear as a literal or high-similarity substring in the citing block's own text, which kills padding-with-junk coverage gaming; (3) pinned vocabulary snapshot_version on every xref plus a `stale` verification state when the snapshot moves; (4) the match_type enum {exact,close,broad,related} kept distinct from confidence, so a broad top-level term cannot masquerade as an exact hit; (5) the cross-ARA entity commons via global_entity_id and stored nearest_neighbors. I also adopted its discipline of extracting entities ONLY from already-typed upstream structure, never a fresh NLP sweep, which is what makes ID minting deterministic.

  _Why it wins:_ The competitor pins snapshots and recomputes embeddings but leaves the ontology mapping itself to a single resolver_agent with a confidence threshold — it inherits exactly the correlated-error problem the reviewer flagged, just with a fixed number instead of a second LLM. My hybrid gate makes `resolved` mean "a semantic guess was independently confirmed by a literal hit in the vocabulary's own labels," which is a genuinely decorrelated corroboration the competitor cannot claim. Second, the competitor's status is chosen by the resolver (decision: accepted/ambiguous/unmapped); mine is COMPUTED from the log by a written state machine, which is what the Class-C auditability mandate actually requires. Third, the competitor's confidence float still feeds match_type/verification decisions; I bar the raw score from all scoring and let the gate carry the weight. I keep every strength it has (recompute check, corroboration, snapshots, commons) and close the independence, denominator-control, and determinism holes it shares with my own prior draft. Where a merge is strictly better I merged rather than differentiated.


### Finalist B (refined)

> _Judge critique it answered:_ Proposal #3 (Anchored Registry + Two-Pass Resolution, claude-sonnet-5) has the single best Class-B reliability mechanism in the field — but it rests on an unexamined independence assumption and leaves two discretionary levers open.

1) The two-independent-resolver agreement gate is only worth anything if the two resolvers have DECORRELATED error modes. Your own example runs gpt-5.1-mini and claude-opus-4.6 — two LLMs with heavily overlapping pretraining that will confidently agree on the *same wrong* MeSH term. "Blind to first pass" removes copying, not correlated priors. Agreement then manufactures false precision — exactly the fabrication surface the mandate says to punish. Fix: mandate that at least one arm be a NON-LLM deterministic matcher (exact + synonym lookup against the vocabulary's own API/label set), so agreement means "LLM semantic guess concurs with a literal registry hit." Define independence explicitly; "two models" is not independence.

2) "Genuinely load-bearing entities" is an omission surface disguised as scoping. Whoever decides load-bearing controls the M10 denominator: an agent gaming coverage declares every unresolvable term "not load-bearing" and excludes it, inflating the ratio. Replace discretion with an objective inclusion rule — e.g., ANY entity cited by a claim, experiment, quantity, or FOL symbol MUST be registered — so inclusion is mechanical, not a lever.

3) The 0.4 not_applicable floor is asserted, uncalibrated, and global across MeSH/EFO/GO/STATO — vocabularies with different score distributions. A single cross-vocab floor makes not_applicable a dumping ground. Specify per-vocabulary floors calibrated against a labeled gold set, and log the calibration provenance; otherwise not_applicable_reason's "similarity 0.22 below 0.4 floor" is theater.

4) match_confidence is a self-reported LLM number, inherently uncalibrated and gameable, yet you store it as if load-bearing. Either calibrate it against the gold set or bar it from any metric — the agreement gate should carry the reliability weight, not a hallucinated float.

5) The append-only log records agree_with/disagree_with, but you never define the disagreement state machine: on disagree, is status forced to `ambiguous`, does a third tiebreaker or human run, and does disagreement block `resolved`? Auditability (your Class-C claim) requires the resolution rule be deterministic and written down, not implied.

6) Unlike Proposal #2 you have NO embedding recompute/reproducibility check — a vector_ref pointing at a wrong or garbage vector is undetectable. You already store input_text_hash; add a recompute-from-hash gate and the anchor-text construction spec so the anchor itself isn't forgeable.

7) fol_symbol uniqueness is claimed but the collision protocol (two entities sanitizing to the same symbol) is unspecified — state the suffixing/disambiguation rule, since CLAIMFOL correctness depends on it.

**The Entity Ledger v2 — entities.yaml + Two-Resolver Ontology / Reproducible-Anchor Protocol**  ·  _source: claude-opus-4-8_

Every concept, method, variable, organism, and measure in an ARA is re-keyed once into a single typed ledger (ontology/entities.yaml): a stable local ID, an optional set of external ontology xrefs, and an optional embedding anchor whose text is DERIVED from already-provenanced fields (not free-typed). Other layers stop naming entities in prose and cite them by ID, turning claims↔concepts consistency (M13) and FOL symbol resolution into exact set operations and turning controlled-vocabulary/latent anchoring (M10/M12/M64) into a bounded, verifiable resolver problem. The four signature defenses the reviewer flagged are now specified rather than asserted: (a) corroboration is a graded strong/weak/none verdict combining token-match, per-kind alias expansion, and an embedding fallback with a published threshold, and failure DOWNGRADES coverage credit instead of silently dropping the ref; (b) embedding anchors have a deterministic anchor-text construction spec plus a versioned re-anchoring migration that tells 'model changed' apart from 'vector forged'; (c) match_type weights and the resolved-eligibility rule are published IN the schema so broad-term farming earns ~0.15 and never reaches 'resolved'; (d) an xref only counts as verified when two independent resolvers agree (existence check alone is insufficient), with a recorded independence discount. resolution_attempted is a first-class boolean so 'resolver never ran' is never conflated with 'ran, found nothing', keeping the M10 denominator honest. The cross-ARA commons is demoted to an explicitly UNSCORED convenience join with a specified merge/adjudication protocol, so a second entity-resolution fabrication surface is not smuggled into a metric.

- **ontology/entities.yaml** (YAML) — Single typed ledger of every named entity. Every other layer points at it by ID instead of re-typing a prose name. resolution_attempted and resolution_status are now orthogonal so honesty of the M10 denominator is structural.
  - fields: id: string ENT-<kind3>-<slug> — required, stable across recompiles (canonical_name+kind reuse-checked before minting) | kind: enum{concept,method,variable,organism,measure,material,software,dataset,disease,anatomical_entity,gene,protein,other} — required | canonical_name: string — required | aliases: list[string] — required, may be [] | fol_symbol: string — required, sanitized unique symbol for CLAIMFOL | definition_source: {layer, anchor} — required | provenance: {source_file, locator, quote} — required (quote is the field the anchor-text spec draws from) | resolution_attempted: bool — required (false = resolver has not run; separates 'never ran' from 'ran, found nothing') | resolution_status: enum{resolved,ambiguous,unmapped,not_applicable} — required; resolved is ONLY assignable when ≥1 xref has verification∈{agreed,human_verified} AND match_type∈{exact,close} (see P2) | not_applicable_reason: string — required (non-null) iff status=not_applicable | resolution_notes: string or null — required key | xrefs: list[xref object] — required, may be [] | embedding_anchor: object or null — required key (see anchor spec) | global_entity_id: string or null — UNSCORED convenience join only (see P5) | cited_by: list — OPTIONAL derived cache, never hand-edited
  - example: - id: ENT-cpt-p-tau217
  kind: concept
  canonical_name: "p-tau217"
  aliases: ["p217", "p-tau 217", "plasma phosphorylated tau 217"]
  fol_symbol: ptau217
  definition_source: {layer: concepts, anchor: "concepts.md#p-tau217"}
  provenance: {source_file: "concepts.md", locator: "## p-tau217", quote: "Tau phosphorylated at threonine 217, measured in plasma."}
  resolution_attempted: true
  resolution_status: resolved
  not_applicable_reason: null
  resolution_notes: null
  xrefs:
    - {vocab: MeSH, ext_id: "D000068752", label: "tau proteins, phosphorylated at Thr217", match_type: close, confidence: 0.81, snapshot_version: "MeSH-2026AA", resolver_a: {name: entity-linker, version: "0.3", model_family: gpt}, resolver_b: {name: entity-linker-2p, version: "0.3", model_family: claude}, shared_backbone: false, resolved_at: "2026-06-02", verification: agreed}
  embedding_anchor: {model: "specter2@2025-09", anchor_text_spec: "v1", text_hash: "sha256:8f2c...", vector_ref: "vecstore://8f2c", nearest_neighbors: [{ext_id: "OpenAlex:C2778941236", vocab_or_corpus: openalex_concept, score: 0.87}], computed_at: "2026-06-02", reproducibility_check: pass}
  global_entity_id: null
- id: ENT-var-abeta-ratio-metric
  kind: variable
  canonical_name: "p-tau217/Abeta42 ratio"
  aliases: []
  fol_symbol: ptau_abeta_ratio
  definition_source: {layer: concepts, anchor: "concepts.md#ratio"}
  provenance: {source_file: "concepts.md", locator: "## ratio", quote: "Automated ratio of p-tau217 to Abeta42."}
  resolution_attempted: true
  resolution_status: unmapped
  not_applicable_reason: null
  resolution_notes: "Attempted MeSH/EFO/UO/STATO; best candidate similarity 0.31 (below 0.40 floor). Genuine miss, not left blank and not forced-broad."
  xrefs: []
  embedding_anchor: {model: "specter2@2025-09", anchor_text_spec: "v1", text_hash: "sha256:9c02...", vector_ref: "vecstore://9c02", nearest_neighbors: [{ext_id: "OpenAlex:C71924100", vocab_or_corpus: openalex_concept, score: 0.62}], computed_at: "2026-06-02", reproducibility_check: pass}
  global_entity_id: null
- **xref object (nested in entities.yaml) — with published match_type weights and two-resolver verification** (YAML object; the weight table is a schema constant shipped with the format, not per-file.) — One candidate or confirmed mapping to an external vocabulary term. The schema itself carries the M10 weight table and the resolved-eligibility rule so broad-term farming cannot be argued about in prose.
  - fields: vocab: enum{MeSH,EFO,GO,NCBITaxon,HGNC,UniProt,Wikidata,arXiv_CS,UO,STATO,ICD11,PROSPERO,other} — required | ext_id: string — required | label: string — required | match_type: enum{exact,close,related,broad,candidate} — required | MATCH_TYPE_WEIGHT (schema constant): {exact:1.0, close:0.75, related:0.40, broad:0.15, candidate:0.0} | confidence: float[0,1] — required | snapshot_version: string — required (pinned vocab release; existence checked against this snapshot) | resolver_a: {name,version,model_family} — required | resolver_b: {name,version,model_family} or null — required key (null until second pass runs) | shared_backbone: bool — required (true if resolver_a and resolver_b share an embedding/model backbone → agreement is discounted, see P2) | resolved_at: date — required | verification: enum{unverified,single_resolver,agreed,disagreed,human_verified,stale,failed} — required; ONLY agreed or human_verified count toward coverage numerator | RESOLVED_ELIGIBILITY (schema rule): entity.resolution_status may be 'resolved' ONLY if some xref has verification∈{agreed,human_verified} AND match_type∈{exact,close}. broad/related-only entities stay 'ambiguous' or 'unmapped'.
  - example: {vocab: EFO, ext_id: "EFO:0004616", label: "blood protein measurement", match_type: broad, confidence: 0.58, snapshot_version: "EFO-3.68.0", resolver_a: {name: entity-linker, version: "0.3", model_family: gpt}, resolver_b: {name: entity-linker-2p, version: "0.3", model_family: claude}, shared_backbone: false, resolved_at: "2026-06-02", verification: agreed}   # NOTE: verification=agreed but match_type=broad → weight 0.15, does NOT make the entity 'resolved'.
- **embedding_anchor + anchor-text construction spec (v1)** (YAML object + a deterministic string template.) — Makes the embedding anchor reproducible AND makes the embedded text non-fabricable: the text is deterministically assembled from already-provenanced fields, so 'garbage anchor text that recomputes to pass' is off the table (the fields it draws from are themselves provenance-checked and human-visible).
  - fields: model: string (versioned, e.g. specter2@2025-09) — required | anchor_text_spec: string (e.g. 'v1') — required, names the template version | text_hash: sha256 of the constructed anchor_text — required | vector_ref: pointer into external vector store — required | nearest_neighbors: list[{ext_id, vocab_or_corpus, score}] — required, may be [] | computed_at: datetime — required | reproducibility_check: enum{pass, model_migrated, text_changed, forged, stale} — required (see P3) | ANCHOR_TEXT_SPEC v1 (schema constant): anchor_text = NFKC(canonical_name) + "\n" + kind + "\n" + first_240_chars(provenance.quote) + "\n" + join(sorted(NFKC(aliases)), "; "); whitespace collapsed to single spaces; trailing newline stripped. No free-form field feeds the hash.
  - example: embedding_anchor:
  model: "specter2@2025-09"
  anchor_text_spec: "v1"
  # constructed: "p-tau217\nconcept\nTau phosphorylated at threonine 217, measured in plasma.\np-tau 217; p217; plasma phosphorylated tau 217"
  text_hash: "sha256:8f2c..."
  vector_ref: "vecstore://8f2c"
  nearest_neighbors: [{ext_id: "OpenAlex:C2778941236", vocab_or_corpus: openalex_concept, score: 0.87}]
  computed_at: "2026-06-02"
  reproducibility_check: pass
- **claim/experiment entity_refs + corroboration verdict** (typed-markdown bullet on the existing C##/E## block; the corroboration verdict is COMPUTED by the validator (P4), not hand-authored.) — Claims/experiments cite the entities their Statement/Evidence depends on, by ID. Each ref carries a graded corroboration verdict that determines COVERAGE credit but never drops the ref (silent drop was itself a gaming lever). This is what stops padding entity_refs with fabricated-but-consistent IDs.
  - fields: **Entity refs**: list[ENT-...] — required; may include an aggregate marker like ENT-...@aggregate(N) | corroboration (validator-computed, per ref): enum{strong, weak, none} — strong = a normalized canonical_name or alias appears as a contiguous token subsequence in the block's Statement/Evidence text; weak = a per-kind alias/acronym expansion matches OR cosine(entity.embedding_anchor, block_sentence_embedding) ≥ τ_corrob=0.62 OR the ref is a declared aggregate whose members are individually corroborated; none = otherwise | COVERAGE_CREDIT (schema constant): {strong:1.0, weak:0.5, none:0.0} | FAILURE ACTION: corroboration=none never drops the ref and never fails the build; it earns 0 coverage credit, still counts for the M13 consistency JOIN, and is surfaced in the validator report as an over-citation flag.
  - example: ## C01: p-tau217 by mass spectrometry has the highest diagnostic accuracy...
- **Statement**: ...p217_MS achieved the highest rank (P-score = 0.859)...
- **Entity refs**: [ENT-cpt-p-tau217, ENT-mth-mass-spectrometry, ENT-mea-p-score]
- **Corroboration (computed)**: {ENT-cpt-p-tau217: strong (alias 'p217' token-matches p217_MS), ENT-mth-mass-spectrometry: weak (acronym expansion 'MS' + cosine 0.71), ENT-mea-p-score: strong ('P-score' token match)}
- **ontology/resolution_log.yaml — append-only, two-pass** (YAML append-only list; one entry per resolver invocation.) — Append-only audit trail of every resolution attempt AND every independent verification pass, so the Class-B resolver protocol is reproducible, its agreement rate is calibratable, and disagreements are inspectable.
  - fields: run_id: string — required | entity_id: ENT-... — required | pass: enum{primary, verify} — required | resolver: {name, version, model_family} — required | blind_to: run_id or null — required for verify passes (must be non-null and reference the primary run; asserts the verifier did not see pass-1 output) | query_context: string — required (should equal the constructed anchor_text for cross-checkability) | candidates_considered: list[{vocab, ext_id, label, raw_score}] — required, includes rejected candidates | decision: enum{accepted, ambiguous, unmapped, agree_with_<run_id>, disagree_with_<run_id>} — required | decided_at: datetime — required
  - example: - run_id: "res-2026-06-02-0044"
  entity_id: ENT-cpt-p-tau217
  pass: primary
  resolver: {name: ara-ontology-resolver, version: "1.3.0", model_family: gpt}
  blind_to: null
  query_context: "p-tau217\nconcept\nTau phosphorylated at threonine 217, measured in plasma.\np-tau 217; p217; plasma phosphorylated tau 217"
  candidates_considered:
    - {vocab: MeSH, ext_id: "D000068752", label: "tau proteins, phosphorylated at Thr217", raw_score: 0.81}
    - {vocab: Wikidata, ext_id: "Q107127233", label: "phospho-tau217", raw_score: 0.77}
  decision: accepted
  decided_at: "2026-06-02T14:02:11Z"
- run_id: "res-2026-06-02-0051"
  entity_id: ENT-cpt-p-tau217
  pass: verify
  resolver: {name: ara-ontology-resolver-2p, version: "1.3.0", model_family: claude}
  blind_to: "res-2026-06-02-0044"
  query_context: "(same constructed anchor_text, independent run)"
  candidates_considered:
    - {vocab: MeSH, ext_id: "D000068752", label: "tau proteins, phosphorylated at Thr217", raw_score: 0.84}
  decision: agree_with_res-2026-06-02-0044
  decided_at: "2026-06-02T14:05:47Z"
- **commons/gec_merge.yaml — UNSCORED cross-ARA binding record** (YAML in a shared commons repo; each GEC has an append-only binding history.) — Records how a global_entity_id (GEC) was bound across ARAs, WITH the evidence and adjudication. Explicitly excluded from every scored metric until a commons authority exists; it is a convenience join, never a coverage input, so it introduces no new fabrication surface into scoring.
  - fields: gec: string GEC-###### — required | member: {ara_id, entity_id} — required | bind_basis: enum{shared_verified_xref, embedding_neighbor, human_adjudicated} — required | shared_xref: {vocab, ext_id} or null — required when bind_basis=shared_verified_xref (both members must carry a verification∈{agreed,human_verified} xref to this exact ext_id) | neighbor_score: float or null — required when bind_basis=embedding_neighbor (cosine ≥ τ_merge=0.85 under pinned commons model AND kind match) | adjudicator: string or null | conflict_action: enum{none, split, flagged} — required (if two members disagree on xrefs, GEC is split, never silently merged) | bound_at: datetime — required
  - example: - gec: GEC-000481
  member: {ara_id: ARA-alz-2026-014, entity_id: ENT-cpt-p-tau217}
  bind_basis: shared_verified_xref
  shared_xref: {vocab: MeSH, ext_id: "D000068752"}
  neighbor_score: null
  adjudicator: null
  conflict_action: none
  bound_at: "2026-06-10T09:00:00Z"

  _Protocols:_
  - **P1 — Entity Extraction & Stable-ID Minting (Class A, deterministic)** — Every compile/recompile; deterministic bootstrap before any external resolution.. 1. Enumerate candidates ONLY from already-typed structure (concepts.md headings, claim/experiment Setup keys, related_work adopted-elements) — never a fresh NLP sweep of raw prose. 2. Canonicalize name (NFKC, trim) and check existing entities.yaml for matching canonical_name/alias before minting — keeps IDs stable across recompiles. 3. Mint id=ENT-<kind3>-<slug>; suffix on collision. 4. Assign fol_symbol (sanitized, uniqueness-checked). 5. Populate definition_source/provenance. 6. Initialize resolution_attempted=false, resolution_status=unmapped, xrefs=[], embedding_anchor=null.
    - reliability/reproducibility: Deterministic: same typed upstream blocks always yield the same entity set, IDs, and fol_symbols, because minting re-keys existing structure rather than reinterpreting prose.
    - constraints: Requires upstream layers to already carry the typed fields this protocol reads; inherits their determinism.
  - **P2 — Two-Independent-Resolver Xref Resolution & Verification (Class B)** — When mapping local entities to external vocabularies; sets resolution_attempted=true.. 1. Set resolution_attempted=true. 2. Primary resolver queries pinned vocab snapshots using the constructed anchor_text (P3 spec) as query_context; log all candidates with scores to resolution_log (pass=primary). 3. Apply confidence floor 0.40; below floor → status=unmapped (honest miss, record best score in resolution_notes). 4. Assign match_type per candidate (exact/close/related/broad/candidate). 5. Second resolver of a DIFFERENT model_family, blind_to the primary run, independently resolves; log (pass=verify). 6. If both pick the same ext_id → verification=agreed; different → verification=disagreed and status=ambiguous with both candidates retained. 7. Record shared_backbone: true if the two resolvers share an embedding/model backbone; when true the agreement is CORRELATED and is discounted — such xrefs are treated as single_resolver for scoring unless a human_verified pass is added. 8. Existence is separately checked against snapshot_version; a real-but-wrong ID can pass existence but only reaches 'resolved' via agreed+exact/close (existence alone is never sufficient). 9. Set resolution_status=resolved ONLY under RESOLVED_ELIGIBILITY (verified xref with match_type∈{exact,close}); broad/related-only stays ambiguous/unmapped.
    - reliability/reproducibility: Reliability rests on (a) pinned snapshots, (b) fixed confidence floor and match_type weights published in schema, (c) two-resolver agreement gate that catches real-but-wrong single-resolver IDs, and (d) an explicit independence discount so correlated agreement is not counted as two votes. The log makes agreement/disagreement rates calibratable per vocab over time.
    - constraints: Ecosystem must provide: pinned, dereferenceable vocab snapshots; at least two resolver implementations with genuinely different backbones; a store recording model_family lineage so shared_backbone can be determined honestly (self-declared shared_backbone=false is itself spot-audited).
  - **P3 — Embedding Anchoring & Versioned Re-Anchoring Migration (Class B)** — When adding/refreshing an embedding_anchor, and whenever the embedding model version is bumped.. CONSTRUCT: 1. Build anchor_text deterministically from ANCHOR_TEXT_SPEC v1 (canonical_name, kind, first 240 chars of provenance.quote, sorted aliases). 2. text_hash = sha256(anchor_text). 3. Embed with pinned model; store vector by vector_ref. CHECK (reproducibility_check states): pass = recompute under SAME model+anchor_text reproduces stored vector (cosine ≥ 0.9999). forged = same model+text_hash but stored vector does NOT match recompute → score as absent AND flag. model_migrated = model version bumped, but anchor_text (hence text_hash) is unchanged → NOT a failure; re-embed under new model tag, keep old vector as superseded, status=model_migrated then pass. text_changed = anchor_text recomputed from current fields yields a NEW text_hash (fields edited since anchoring) → re-anchor, log old→new, status=text_changed then pass. stale = anchor older than the re-verification interval. MIGRATION on model bump: batch-recompute text_hash for all anchors; unchanged hash → model_migrated (silent, expected); changed hash → text_changed (surfaced). Forgery is ONLY ever the same-model/same-text mismatch, so a model bump can never mass-fail as forgery.
    - reliability/reproducibility: The anchor text is not a fabrication surface: it is a pure function of provenance-checked, human-visible fields, so 'garbage text that recomputes to pass' would be visible garbage in canonical_name/quote/aliases and caught by the same review that scores those fields. Model changes and forgeries are distinguished by construction (different-model vs same-model mismatch), so bumping specter2 triggers migration, not mass failure.
    - constraints: Ecosystem must provide: pinned, redistributable embedding model versions; a content-addressed vector store; a migration runner triggered on model-version registry changes.
  - **P4 — Corroboration Verdict & Coverage-Credit Assignment (Class A/B)** — Validator pass over every claim/experiment Entity refs field.. 1. TOKENIZE block text and each candidate surface with the same pipeline: NFKC normalize, casefold, split on Unicode non-alphanumerics, keep intra-token hyphens/digits (so 'p-tau217' is one token). 2. ALIAS-EXPAND per kind before matching: gene/protein → add HGNC/UniProt symbol + common casings; measure/method → add declared acronym expansions; organism → add NCBITaxon common name; concept/variable → aliases as-authored only (no auto-broadening). 3. STRONG if a canonical_name or expanded alias appears as a contiguous token subsequence. 4. WEAK if (a) an acronym↔expansion pair matches, OR (b) cosine(entity.embedding_anchor, block-sentence embedding) ≥ τ_corrob=0.62, OR (c) the ref is a declared @aggregate(N) marker whose N members are each individually corroborated (handles 'all three biomarkers achieved...'). 5. NONE otherwise. 6. CREDIT: strong=1.0, weak=0.5, none=0.0 toward coverage; the ref is NEVER dropped and the build NEVER fails on corroboration — none-verdict refs still participate in the M13 join and are listed in the validator report as over-citation flags.
    - reliability/reproducibility: Threshold (0.62), tokenization, per-kind expansion rules, and credit weights are published constants → run-to-run reproducible. Pasting the name earns strong but coverage is gated separately by whether the entity is actually resolved (P2), so a pasted string with no verified xref still earns little; embedding fallback rescues legitimate pronoun/un-aliased/aggregate references that pure lexical would false-negative.
    - constraints: Requires the same embedding model used for anchors to be available for block-sentence embedding; requires per-kind alias-expansion tables (shipped with the format, versioned).
  - **P5 — Cross-ARA GEC Binding (Class B, UNSCORED until commons exists)** — Only when a shared commons authority is running; never affects any scored metric.. 1. Propose a binding only via: shared_verified_xref (both entities carry verification∈{agreed,human_verified} xref to the identical vocab+ext_id), OR embedding_neighbor (cosine ≥ τ_merge=0.85 under the pinned commons model AND kind match). 2. Record bind_basis and evidence in gec_merge.yaml. 3. CONFLICT: if two members bound to one GEC carry divergent verified xrefs, set conflict_action=split — the GEC is split and both flagged, never silently merged. 4. Ambiguous/embedding-only proposals require human adjudication (adjudicator recorded). 5. GEC never feeds M10/M12/M13/M64; it is a convenience join for cross-ARA recognition only.
    - reliability/reproducibility: By requiring independent evidence (verified shared xref or embedding-neighbor gate) plus explicit conflict-split, two ARAs cannot silently bind one GEC to different real-world entities. Keeping it unscored removes the incentive to fabricate bindings.
    - constraints: Ecosystem must provide a commons authority/registry with a minting protocol, a pinned commons embedding model, and an adjudication queue. Until that exists, global_entity_id stays null in scored ARAs.

  _Metrics afforded:_
  - M10 — controlled-vocabulary referenceability / coverage → numerator = sum over entities of best verified xref weight (MATCH_TYPE_WEIGHT, only verification∈{agreed,human_verified}); denominator = count of entities with resolution_attempted=true AND status∈{resolved,ambiguous,unmapped} (not_applicable excluded with required reason; resolution_attempted=false excluded and reported separately as 'pending', an incompleteness signal not a fabrication). [reliable-anchored]; anti-Goodhart: Broad-term farming earns 0.15 and never reaches 'resolved' (RESOLVED_ELIGIBILITY needs exact/close). Real-but-wrong single-resolver IDs are blocked by the two-resolver agreement gate. resolution_attempted separates 'never ran' from 'ran, found nothing', so you cannot inflate the denominator's favorability by leaving entities unprocessed — they surface as pending. not_applicable requires a reason and is spot-audited.
  - M13 — claims↔concepts consistency → Exact set operation: for each claim, entity_refs ∩ entities.yaml IDs, and concept 'Related concepts (by ID)' joins; inconsistency = referenced ID absent from ledger or dangling. [deterministic]; anti-Goodhart: IDs must exist in the ledger (P1), so you cannot cite a concept that was never introduced. Over-citation to fake consistency is caught by P4: a padded ref with corroboration=none earns 0 coverage credit and is flagged, even though it still joins.
  - M12 / M64 — latent-space anchoredness → Fraction of entities with an embedding_anchor whose reproducibility_check∈{pass, model_migrated}; forged/text_changed(unre-anchored) score as absent. [reproducible]; anti-Goodhart: Anchor text is a deterministic function of provenance-checked fields (ANCHOR_TEXT_SPEC), so a garbage anchor is garbage in visible fields. Forged vectors fail same-model recompute. A model bump migrates rather than mass-fails, so the metric is not gamed by refusing to update.
  - entity-citation coverage (per claim/experiment) → sum of COVERAGE_CREDIT (strong 1.0 / weak 0.5 / none 0.0) over a block's entity_refs, normalized by load-bearing entities in the block. [reproducible]; anti-Goodhart: Pure string-paste gets strong locally but coverage is jointly gated by P2 resolution status, so uncorroborated-yet-resolved padding is bounded; legitimate pronoun/aggregate/un-aliased refs are rescued by the weak tier so honesty is not punished. none-refs are surfaced, not dropped, so silent-drop gaming is removed.
  - resolver agreement / calibration (meta-metric) → From resolution_log: per-vocab agreement rate between blind primary and verify passes, discounting shared_backbone=true pairs. [reproducible]; anti-Goodhart: Two-resolver independence is logged; correlated agreement (shared backbone) is discounted so you cannot manufacture agreement by running the same model twice.

  _Tradeoffs:_ Costs: two independent resolvers per entity roughly doubles resolution compute and requires genuinely different backbones to exist; small groups may only afford single_resolver, which honestly caps them below 'resolved' until a human_verified pass is added — this is by design (honest incompleteness, not penalty). Fabrication surfaces and mitigations: (1) shared_backbone is self-declared — mitigated by spot-audit and by defaulting to discount when lineage is unverifiable. (2) provenance.quote feeds anchor_text, so a doctored quote could shape the embedding — but the quote is itself provenance-checked and human-visible, and doctoring it degrades the very field reviewers read. (3) not_applicable_reason is a prose escape hatch — mitigated by requiring a recorded best-candidate score and spot-audit. (4) aggregate markers could be abused to claim group corroboration — mitigated by requiring each member be individually corroborated. (5) The corroboration embedding fallback (τ_corrob=0.62) can be tuned to over-admit — the threshold is a published constant, changes are versioned, and weak only earns half credit. Residual risk: thresholds (0.40 floor, 0.62 corrob, 0.85 merge, 0.9999 vector match) are defensible defaults but need empirical calibration per field; they are schema constants so at least they are uniform and auditable rather than per-author.

  _Open questions:_ 1) Optimal per-field values for the confidence floor, τ_corrob, and τ_merge need calibration sets we do not yet have. 2) True resolver independence is hard to guarantee as backbones converge; the shared_backbone discount is a proxy, not a proof. 3) The commons authority (minting, adjudication, conflict-split governance) is specified but unbuilt — until it exists GEC stays unscored. 4) Anchor-text spec v1 truncates the quote at 240 chars; entities whose distinguishing detail lives beyond that could under-anchor, requiring a spec v2. 5) Per-kind alias-expansion tables must be maintained and versioned across many vocabularies; staleness there quietly shifts corroboration verdicts.

  _Changes from critique:_ Addressed every numbered critique. (1) Corroboration is now a graded strong/weak/none verdict (P4) with a PUBLISHED threshold τ_corrob=0.62, a fully specified tokenization pipeline, per-kind alias-expansion rules, an embedding fallback and an aggregate-marker path to kill the pronoun/un-aliased/aggregate false negatives — and corroboration=none DOWNGRADES coverage credit (0.0) rather than silently dropping the ref (silent drop named as a gaming lever and removed). (2) Added ANCHOR_TEXT_SPEC v1 (deterministic field order: canonical_name, kind, quote[:240], sorted aliases) so anchor text is not a fabrication surface, plus a versioned re-anchoring migration (P3) with reproducibility_check states pass/model_migrated/text_changed/forged/stale that distinguishes 'model changed' from 'vector forged' and never mass-fails on a model bump. (3) Published MATCH_TYPE_WEIGHT {exact 1.0, close 0.75, related 0.40, broad 0.15, candidate 0.0} IN the schema and a RESOLVED_ELIGIBILITY rule that broad/related can never make an entity 'resolved' — broad-farming earns 0.15 and stays ambiguous. (4) Added a two-independent-resolver agreement gate (P2): verification=agreed requires a blind second resolver of a different model_family to pick the same ext_id; existence-in-snapshot alone is explicitly insufficient; shared_backbone agreement is discounted. (5) Added resolution_attempted: bool, orthogonal to resolution_status, so 'never ran' (excluded, reported as pending) is separated from 'ran, found nothing' (unmapped, in denominator) — keeping the M10 denominator honest. (6) Demoted global_entity_id to an explicitly UNSCORED convenience join with a specified merge protocol (P5, gec_merge.yaml): shared verified xref OR embedding-neighbor gate + kind match, human adjudication, and conflict-split so two ARAs cannot silently bind one GEC to different entities.

  _Adopted from competitor:_ Adopted the competitor's (and reviewer-endorsed) resolution_attempted: bool for clean 'never ran' vs 'found nothing' separation; its two-independent-resolver agreement gate as the core verification mechanism (with an added independence/shared_backbone discount the competitor lacked); its explicit fol_symbol slot for a collision-free CLAIMFOL symbol table; and its append-only two-pass resolution log structure with blind-verify entries.

  _Why it wins:_ It keeps my design's higher anti-gaming density but removes the four soft spots the reviewer said would become holes, and it out-specifies the competitor on the exact axes the mandate rewards: the competitor asserts verification but only stores verified:bool without an independence discount (correlated agreement counts as two votes); it has an embedding anchor with an input_text_hash but no anchor-text construction spec (so its anchor text remains a fabrication surface) and no re-anchoring migration (so a model bump breaks its anchors); it names xref match_confidence but publishes no match_type weight vector or resolved-eligibility rule (broad-term farming is unbounded); and it does not gate coverage by a graded corroboration verdict at all, so over-citation padding is unaddressed. My version publishes every threshold and weight as a schema constant, makes corroboration failure a visible downgrade rather than a silent drop, distinguishes model-migration from forgery by construction, and refuses to score the cross-ARA commons until its merge/adjudication protocol is actually built — closing the gap honestly instead of asserting it closed.


---


## EDGES — Cross-layer typed semantic alignment graph

_Class A — format-recoverable determinism_


**Judge rationale:** All four designs are concrete, non-vague, and correctly place the semantic entailment verdict in Class C while building a deterministic Class-A structural skeleton. They separate on TWO decisive axes. AXIS 1 — cleanliness of the A/C boundary (does the deterministic file stay uncontaminated by any semantic judgment): #2 and #3 put verdicts in a wholly SEPARATE file (structurally uncontaminable); #1 co-locates an entailment_slot pointer inside the edge record (acceptable but co-located); #0 puts a semantic_holds enum literally inside each edge object (weakest — the deterministic record and the semantic verdict share a struct, inviting exactly the contamination the class boundary forbids). AXIS 2 — explicit engineering against Goodhart/fabrication: the two sonnet designs deploy DEDICATED mechanisms (#3: declared_by trust-tiers, computed-not-authored status, addressable not_applicable, a relates-fallback scored-lower-not-rejected; #2: prose↔graph agreement as an independent anti-fab signal, ecosystem-schema vs instance split, illegal-edge rejection). The two codex designs (#0, #1) are more EXHAUSTIVE in field enumeration and #1 adds real graph interoperability (JSON-LD/RDF, explicit acyclic-subgraph constraints), but their proliferation of null_states (not_specified/not_applicable/unknown) is itself an unreckoned-with fabrication surface, and neither confronts the incomplete-graph / omission attack. Because the mandate weights class-fitness (A must reach determinism, cleanly separated from C) and honesty about fabrication surfaces most heavily, #3 and #2 take the top two. #3 edges ahead of #2 for being the most literal 'real typed graph, not markdown with embedded ids' (prose renders FROM the ledger; status fields are computed, not authored) and for the sharpest anti-gaming instrumentation — despite paying the highest implementation cost (inverting the compiler) and leaving its rubric-satisfying attrs under-anchored. #2 is the more implementable additive sidecar and keeps an independent prose cross-check that #3 sacrifices. #1 ranks third: most complete and most interoperable, but weaker A/C separation and an under-defended null-state surface. #0 ranks fourth: strong and thorough, but embedding semantic_holds in the edge object is the clearest class-fitness smell in the field, and its baseline_edge cross-referencing adds complexity without closing the anchoring gap.


### Finalist A (refined)

> _Judge critique it answered:_ EDGE LEDGER (#3) — you win on anti-gaming philosophy and on being the most literal fulfillment of "a real typed graph, not markdown with embedded ids": prose renders FROM edges, structural_status and verdict_ref are COMPUTED-not-authored, the verdict log is a separate append-only file, declared_by separates who-asserts from whether-it-holds, and `not_applicable` is an addressable node rather than a silent omission. But the design has load-bearing holes you must close before it deserves the "deterministic" label:\n\n1) UNANCHORED ATTRS SMUGGLED INTO A 'DETERMINISTIC' RECORD. Your own example proves the problem: EDGE-0001's source_anchor.quote is \"Verifies: C01,C02,C05,C06\" — but the attrs assert design_features=[network_meta_analysis, indirect_evidence_synthesis, baseline_comparison] and baseline_ref=Q08. NOTHING in the anchored quote licenses those features. They are compiler inferences wearing a deterministic costume. Since design_features is exactly what the claim_type rubric gates on, your whole \"structured correspondence before any LLM\" claim rests on fields that are not themselves anchored. Fix: every rubric-satisfying attr must carry its OWN pointer into a method/evidence node, and the checker must verify that pointer resolves — otherwise claim_type gating is theater.\n\n2) INVERSION KILLS YOUR OWN CROSS-CHECK. \"Prose renders from edges\" makes the graph ground-truth by fiat and destroys the independent second source that #2 exploits. If the compiler mis-extracts, there is no prose to disagree with it; your entire anti-fabrication story collapses to \"trust source_anchor.quote.\" You must specify a checker step that (a) verifies quote literally appears at file:locator, and (b) verifies the quote actually licenses the typed attrs. Right now (a) is implied and (b) is absent.\n\n3) THE `relates` FALLBACK IS AN UNCAPPED GOODHART DRAIN. \"Scored lower-specificity, never rejected\" is honest but a pass-rate-maximizing compiler routes every hard edge into `relates` with a plausible relation_note and never eats a rejection — and relation_note becomes the free-text dumping ground you claim to be eliminating. You need an explicit per-artifact cap (max fraction of edges typed `relates` before flag) and a structural constraint on relation_note so it can't re-import prose.\n\n4) declared_by IS UNGUARDED. What stops the compiler labeling a shaky inference `author-stated` to borrow credibility? Gate it: `author-stated` must require an anchor whose quote contains the assertion; `compiler-inferred` must be FORBIDDEN from satisfying any claim_type rubric requirement. Make the trust tier gate what the edge is allowed to satisfy.\n\n5) not_applicable IS THE UNIVERSAL ESCAPE. uses-data→dataset:not_applicable with role:not_applicable passes structurally. Without a genre-conditioned table of which nulls are legal per paper_type (meta-analysis MAY null raw data; RCT MAY NOT), honest-absence degrades to free-absence.\n\n6) reconciliation:exact — AUTHORED OR COMPUTED? You applied computed-not-authored discipline to structural_status but left `reconciliation` authored in the example. If the checker computes it against the quantity ledger, say so and forbid authoring it; if authored, it's fabricable. Same discipline, or the numeric check is decorative.\n\n7) YOU CALL IT A DAG BUT NEVER CONSTRAIN CYCLES. depends-on and supports can cycle; SAGE (#1) explicitly declares which subgraphs must be acyclic and you do not. Specify the acyclic subgraphs and the detection step.

**The Edge Ledger v2: an anchored typed cross-layer graph (nodes.yaml + edge_schema.yaml + edges.yaml) with per-attr provenance, a deterministic structural checker, a genre-conditioned nullability table, declared_by trust-tier gating, and a separate append-only ENTAIL verdict log**  ·  _source: claude-opus-4-8_

One canonical typed edge ledger replaces every ad hoc existence-only pointer (Proof:[E01], Verifies:[C01], Caused by:[O2], RW Type:extends), but v2 closes the holes that made v1's "deterministic" label a costume. THREE changes carry the fix: (1) prose is authored INDEPENDENTLY and edges are checked AGAINST it (round-trip reconcile) rather than rendered from edges — restoring the independent second source the reviewer said inversion destroyed; (2) every rubric-gating attribute value is itself a typed object carrying its OWN anchor into a resolvable node, and the claim_type rubric can only be satisfied by attrs that are (a) anchored, (b) whose quote a bounded licensing check confirms supports them, and (c) declared_by an author-stated (never compiler-inferred) edge; (3) fields that can be derived are COMPUTED-not-authored — structural_status, reconciliation, verdict_ref, and now licensing_status are all machine-produced and forbidden in author input. A genre-conditioned nullability table makes honest-absence legal-by-genre instead of free-by-default, a per-artifact cap plus a structured relation_note keeps the `relates` fallback from becoming a Goodhart drain, and a declared acyclic-subgraph spec with a cycle-detection step makes the "DAG" claim real. The semantic "does it hold" question stays in a separate append-only verdicts.yaml (ENTAIL, Class C) that only ever sees structurally-passing edges, so the judge's degrees of freedom shrink to the genuinely irreducible.

- **graph/nodes.yaml — global node registry (adopted from competitor, hardened)** (YAML, one file per ARA at graph/nodes.yaml) — One stable typed id + resolvable file locator for every addressable object across every layer. This is the prerequisite the competitor got right that v1 only implied: edges are typed pairs of node ids, and — critically for the anchor fix — the checker needs each node's declared {file, locator} so it can verify that an attribute's anchor actually points into that node's real text. Existing native ids (C01/E01/RW01/Q07/CN01/DS01/MTH01/ENV) are namespaced, not reinvented.
  - fields: schema_version : string — required. ara_id : string — required. nodes : list[Node] — required. Node = {id: string, globally unique within ARA — required; type: enum(Claim|Experiment|Concept|Observation|Gap|Assumption|Constraint|Method|Quantity|Dataset|Environment|Ref|Evidence|TreeNode|ExternalRegistration) — required; layer: string, file the node's primary content lives in — required; locator: string, heading/anchor/line within that file — required; alias_of: string | null — for pre-existing ids later merged}. A reserved sentinel node `<type>:not_applicable` exists per type but is ONLY resolvable when the genre nullability table (see nullability.yaml) permits it for the referencing edge — otherwise the checker treats it as a dangling endpoint.
  - example: schema_version: "2.0"
ara_id: che26-diagnostic-performance-of-plasma-p-tau217
nodes:
  - {id: C01, type: Claim, layer: logic/claims.md, locator: "## C01"}
  - {id: E01, type: Experiment, layer: logic/experiments.md, locator: "## E01"}
  - {id: MTH01, type: Method, layer: logic/solution/study_design.md, locator: "§Comparators"}
  - {id: Q07, type: Quantity, layer: quantities.yaml, locator: "Q07"}
  - {id: Q08, type: Quantity, layer: quantities.yaml, locator: "Q08"}
  - {id: T02, type: Evidence, layer: evidence/tables/table2.md, locator: "whole file"}
  - {id: RW01, type: Ref, layer: logic/related_work.md, locator: "## RW01"}
  - {id: REG01, type: ExternalRegistration, layer: PAPER.md, locator: "PROSPERO CRD420261327845"}
- **graph/edges.yaml — the canonical typed edge ledger (anchored attrs, computed fields)** (YAML, one file per ARA at graph/edges.yaml) — The artifact's real graph. Every cross-layer relation the compiler currently buries in prose is emitted ONCE as a structured record with a closed type, resolved endpoints, and type-specific attrs. v2 fix: attrs that gate a rubric are no longer bare enum lists — each is a typed object carrying its own anchor, and its licensing/structural verdicts are COMPUTED, never authored.
  - fields: schema_version : string — required. ara_id : string — required. rubric_version : string, pins edge_schema.yaml version for reproducibility — required. edges : list[Edge] — required. Edge = {id: string EDGE-#### unique+stable across recompiles — required; type: enum from edge_schema.yaml — required; from: node id — required, must resolve in nodes.yaml; to: node id — required, must resolve; declared_by: enum(author-stated|derived|compiler-inferred) — required, WHO asserts the edge exists (not whether it holds); source_anchor: {file, locator, quote} | null — required for author-stated; for `derived` points at the parent edge id instead; forbidden-to-be-null for author-stated (checker error); attrs: object per edge_schema.yaml — required. RUBRIC-GATING attr values are AnchoredValue objects, NOT bare scalars. AnchoredValue = {value: <enum/scalar>; anchor: {node: node id, locator, quote} — required for gating attrs; licensing_status: enum(licensed|unlicensed|unchecked) — COMPUTED by ANCHOR-VERIFY, never authored}. Non-gating attrs may be bare scalars or `not_specified`/`not_applicable`. reconciliation: enum(exact|within_tolerance|mismatch|not_applicable) — COMPUTED by the checker against the quantity ledger, FORBIDDEN in author input; structural_status: enum(ok|missing_required_attr|dangling_endpoint|type_mismatch|reconciliation_mismatch|unresolved_attr_anchor|illegal_null|trust_tier_violation|anchor_not_found|anchor_unlicensed) — COMPUTED, never authored; verdict_ref: pointer into verdicts.yaml | null — COMPUTED/appended by ENTAIL, never authored}
  - example: schema_version: "2.0"
ara_id: che26-diagnostic-performance-of-plasma-p-tau217
rubric_version: "edge_schema@2.3.0"
edges:
  - id: EDGE-0001
    type: tests
    from: E01
    to: C01
    declared_by: author-stated
    source_anchor: {file: logic/experiments.md, locator: "E01 Verifies", quote: "Verifies: C01, C02, C05, C06"}
    attrs:
      claim_type_at_declare: improvement
      design_features:
        - value: baseline_comparison
          anchor: {node: MTH01, locator: "§Comparators", quote: "each plasma assay is ranked head-to-head against the reference CSF immunoassay baseline"}
          licensing_status: licensed      # COMPUTED
        - value: network_meta_analysis
          anchor: {node: MTH01, locator: "§Synthesis", quote: "indirect comparisons estimated within a random-effects network meta-analysis"}
          licensing_status: licensed      # COMPUTED
      measures: [Q07, Q08, Q09]
      baseline_ref: Q08
    reconciliation: not_applicable          # COMPUTED (tests carries no numeric to reconcile)
    structural_status: ok                   # COMPUTED
    verdict_ref: null                       # COMPUTED
  - id: EDGE-0002
    type: supports
    from: T02
    to: C01
    declared_by: author-stated
    source_anchor: {file: evidence/tables/table2.md, locator: "Table 2, Outcome 1, Rank 1", quote: "p217_MS 0.859 (0.821-0.897)"}
    attrs: {quantity_ids: [Q07]}
    reconciliation: exact                    # COMPUTED: T02 cell 0.859 == quantities.yaml Q07.value
    structural_status: ok
  - id: EDGE-0005
    type: uses-data
    from: E01
    to: dataset:not_applicable
    declared_by: author-stated
    source_anchor: {file: logic/experiments.md, locator: "E01 Data", quote: "reuses published summary statistics; no accessioned raw dataset"}
    attrs: {role: not_applicable, null_reason: summary_statistics_only}
    reconciliation: not_applicable
    structural_status: ok                    # COMPUTED: legal because nullability.yaml permits it for paper_type=meta_analysis
  - id: EDGE-0006
    type: rw-relates
    from: RW01
    to: C01
    declared_by: author-stated
    source_anchor: {file: logic/related_work.md, locator: "RW01 Claims affected", quote: "Claims affected: C01, C07"}
    attrs: {relation: imports, delta_magnitude: moderate, adopted_element: "BioFINDER-1 cohort (N=135)"}
    reconciliation: not_applicable
    structural_status: ok
- **graph/edge_schema.yaml — shared edge-type + claim-type rubric registry (ecosystem-level)** (YAML, versioned, distributed with the checker tooling (not per-ARA)) — Fixes, ecosystem-wide and versioned: (a) legal endpoint type-pairs per edge type (enables type_mismatch); (b) required vs optional attrs, each flagged nullable + null_reason_required + requires_anchor (enables missing_required_attr, unresolved_attr_anchor); (c) the claim_type -> required design_features table, PLUS which trust tiers and which licensing states may satisfy it. This is the single place the reviewer's demand 'compiler-inferred is FORBIDDEN from satisfying any rubric' is encoded as data, not prose.
  - fields: schema_version : string. edge_types : map[name -> {from: list[NodeType], to: list[NodeType], required_attrs: map[attr -> {type, enum?, nullable: bool, null_reason_required: bool, requires_anchor: bool}], optional_attrs: map}]. claim_type_rubric : map[claim_type -> {required_design_features_any_of: list[enum]}]. rubric_satisfaction_policy : {min_declared_by_tier: enum(author-stated), required_licensing_status: enum(licensed)} — global gate: a design_feature counts toward a claim_type requirement ONLY if its edge is author-stated AND the feature's licensing_status==licensed. relates_policy : {max_fraction_of_edges: float, relation_note_schema: {max_chars, must_reference_min_node_ids: int, controlled_relation_verbs: list}}.
  - example: schema_version: "2.3.0"
edge_types:
  tests:
    from: [Experiment]
    to: [Claim]
    required_attrs:
      design_features: {type: "list<AnchoredValue<enum>>", enum: [ablation, baseline_comparison, heterogeneous_data, held_out_eval, cross_cohort_replication, randomized_intervention, natural_experiment, network_meta_analysis, sampling_frame, bound_check], nullable: false, requires_anchor: true}
      measures: {type: "list<ref:Quantity>", nullable: false, requires_anchor: false}
    optional_attrs:
      baseline_ref: {type: "ref:Quantity", nullable: true, null_reason_required: true}
  supports:
    from: [Evidence, Experiment]
    to: [Claim]
    required_attrs: {quantity_ids: {type: "list<ref:Quantity>", nullable: false, requires_anchor: false}}
  uses-data:
    from: [Experiment, Method]
    to: [Dataset]
    required_attrs: {role: {type: enum, values: [train, eval, validation, external_replication, not_applicable], nullable: true, null_reason_required: true}}
  rw-relates:
    from: [Ref]
    to: [Claim, Concept, Method]
    required_attrs:
      relation: {type: enum, values: [imports, bounds, baseline, extends, refutes], nullable: false}
      delta_magnitude: {type: enum, values: [minor, moderate, major, not_specified], nullable: true, null_reason_required: false}
  relates:
    from: ['*']
    to: ['*']
    required_attrs: {relation_note: {type: StructuredRelationNote, nullable: false}}
claim_type_rubric:
  causal: {required_design_features_any_of: [ablation, randomized_intervention, natural_experiment]}
  improvement: {required_design_features_any_of: [baseline_comparison]}
  generalization: {required_design_features_any_of: [heterogeneous_data, held_out_eval, cross_cohort_replication]}
  descriptive: {required_design_features_any_of: []}
rubric_satisfaction_policy: {min_declared_by_tier: author-stated, required_licensing_status: licensed}
relates_policy:
  max_fraction_of_edges: 0.15
  relation_note_schema: {max_chars: 160, must_reference_min_node_ids: 2, controlled_relation_verbs: [informs, co_occurs_with, temporally_precedes, shares_dataset_with, motivates]}
- **graph/nullability.yaml — genre-conditioned honest-absence table** (YAML, versioned, shared across the ecosystem, keyed to the genre manifest's paper_type vocabulary) — Directly answers 'not_applicable is the universal escape.' Maps paper_type (from the sibling genre manifest) -> per-edge-type which nulls are LEGAL and which null_reason enums are acceptable. A meta-analysis MAY null raw data; an RCT MAY NOT. Honest-absence stays first-class and unpenalized WHERE the genre permits it; a null the genre forbids is a structural error (illegal_null), not a free pass.
  - fields: schema_version : string. paper_types : map[paper_type -> map[edge_type -> {endpoint_may_be_not_applicable: bool, attr_nulls_allowed: map[attr -> list[legal_null_reason_enum]]}]]. default : map[edge_type -> ...] applied when paper_type unspecified (conservative: most nulls illegal, forcing explicit genre declaration).
  - example: schema_version: "2.3.0"
paper_types:
  meta_analysis:
    uses-data:
      endpoint_may_be_not_applicable: true
      attr_nulls_allowed: {role: [summary_statistics_only, no_raw_data_released]}
    tests:
      endpoint_may_be_not_applicable: false
  rct:
    uses-data:
      endpoint_may_be_not_applicable: false      # an RCT nulling its dataset is illegal_null
    registered-as:
      endpoint_may_be_not_applicable: false      # RCTs must declare a registration
  theory_paper:
    uses-data:
      endpoint_may_be_not_applicable: true
      attr_nulls_allowed: {role: [no_empirical_data]}
default:
  uses-data: {endpoint_may_be_not_applicable: false, attr_nulls_allowed: {}}
- **graph/acyclicity.yaml — declared acyclic subgraph spec** (YAML, versioned, ecosystem-level) — Answers 'you call it a DAG but never constrain cycles.' Names the edge-type subsets whose directed union MUST be acyclic (evidentiary support, provenance, dependency) and the subsets where cycles are meaningful and allowed (contradiction, corroboration, free relates). The checker runs Tarjan SCC on each declared-acyclic subgraph.
  - fields: schema_version : string. acyclic_subgraphs : list[{name: string, edge_types: list[string], rationale: string}]. cyclic_allowed : list[{edge_types: list[string], rationale: string}]. Any edge type absent from both lists is treated as acyclic-by-default and flagged for schema-completeness.
  - example: schema_version: "2.3.0"
acyclic_subgraphs:
  - name: evidentiary_support
    edge_types: [tests, supports, measures, uses-data, uses-method]
    rationale: an experiment cannot transitively rest on a claim it is adduced to test
  - name: provenance
    edge_types: [derived-from, resolves, caused-by, registered-as]
    rationale: an insight cannot derive from a gap that derives from it
  - name: dependency
    edge_types: [depends-on, assumes]
    rationale: circular assumptions are a defect, not a topology
cyclic_allowed:
  - edge_types: [contradicts, corroborates, relates]
    rationale: mutual contradiction/corroboration between two claims is legitimate
- **verdicts.yaml — append-only ENTAIL semantic verdict log (Class C)** (YAML append-only log at graph/verdicts.yaml; each entry immutable, superseded not edited) — Keeps the irreducible 'does this edge actually hold' judgment OUT of the deterministic skeleton. Append-only and keyed by edge id + rubric_version + judge-ensemble id, so a verdict is reproducible-to-inputs and auditable, and never contaminates or is re-derived from edges.yaml. ENTAIL only ever runs on edges whose structural_status==ok.
  - fields: entries : list[{verdict_id: string; edge_id: string; rubric_version: string; judge_ensemble: string; run_id: string; direction: enum(for|against|split); holds: enum(yes|no|underdetermined); confidence: float; calibration_set_id: string; anchors_reviewed: list[node id]; supersedes: verdict_id | null; produced_at: timestamp}]
  - example: entries:
  - verdict_id: V-0001
    edge_id: EDGE-0001
    rubric_version: "edge_schema@2.3.0"
    judge_ensemble: entail-3x-2026Q2
    run_id: run-77af
    direction: split
    holds: yes
    confidence: 0.82
    calibration_set_id: cal-metaanalysis-v4
    anchors_reviewed: [MTH01, T02]
    supersedes: null
    produced_at: 2026-07-06T14:02:00Z

  _Protocols:_
  - **STRUCTURAL-CHECK (deterministic, zero LLM)** — On every compile/recompile of an ARA, before ENTAIL is allowed to run on any edge.. 1. Load nodes.yaml, edges.yaml, and the pinned edge_schema.yaml/nullability.yaml/acyclicity.yaml at rubric_version. 2. ENDPOINT RESOLUTION: every edge.from/to must resolve in nodes.yaml and the (from.type, to.type) pair must be legal for the edge type; else dangling_endpoint / type_mismatch. 3. NULL LEGALITY: any not_applicable endpoint or null attr is checked against nullability.yaml for the ARA's paper_type; illegal -> illegal_null; legal -> scored EQUAL to a present value. 4. ATTR COMPLETENESS: every required_attr present (or legally null); requires_anchor attrs must carry an anchor object. 5. TRUST-TIER GATE: reject as trust_tier_violation any author-stated edge whose source_anchor is null. 6. RECONCILIATION (COMPUTED): for edges carrying quantity_ids/measures, read the referenced values from the quantity ledger and the anchored evidence cell; set reconciliation to exact/within_tolerance/mismatch; author-supplied reconciliation values are discarded. 7. RUBRIC SATISFACTION: for each tests edge, satisfy claim_type_rubric ONLY with design_features that are author-stated AND licensing_status==licensed (see ANCHOR-VERIFY); features that are compiler-inferred or unlicensed do NOT count. 8. RELATES CAP: if fraction of relates edges > relates_policy.max_fraction, flag relates_cap_exceeded; validate each relation_note against StructuredRelationNote (char cap, >=2 node ids, controlled verb). 9. CYCLE DETECTION: run Tarjan SCC on each acyclic_subgraph's directed union; any SCC of size>1 -> cycle_violation with the offending edge list. 10. Write structural_status per edge; block ENTAIL on any edge != ok.
    - reliability/reproducibility: Fully deterministic given pinned versions; same inputs -> same statuses byte-for-byte. rubric_version is recorded in edges.yaml so a re-run reproduces exactly even after the taxonomy evolves.
    - constraints: Ecosystem must provide: versioned edge_schema/nullability/acyclicity registries; a quantity ledger exposing values by id; a genre manifest exposing paper_type; stable node ids.
  - **ANCHOR-VERIFY (two-part: deterministic locate + bounded licensing)** — For every anchor on a rubric-gating attr, and for every author-stated edge's source_anchor. Directly answers critique #1 and #2.. PART A — LOCATE (deterministic): resolve anchor.node in nodes.yaml, open its {file, locator}, and verify the anchor.quote appears LITERALLY (normalized whitespace) at that locator. Fail -> anchor_not_found; the attr cannot count toward any rubric. PART B — LICENSE (bounded, Class-C-lite): a minimized judge answers one closed question per anchor: 'Does this quote license the typed value <value>?' — yes/no with a one-line for and against. Inputs are ONLY the quote and the enum term's ecosystem definition (not the whole paper), collapsing judge degrees of freedom to a single binary. licensing_status is written back to the AnchoredValue. Only licensed anchors count toward claim_type rubric satisfaction.
    - reliability/reproducibility: Part A is deterministic. Part B is reproducible-to-inputs: same (quote, enum definition, judge-ensemble id, calibration set) -> logged verdict; run-to-run agreement is tracked against a labelled calibration set of quote->feature pairs, and the licensing judge is scored for calibration separately from ENTAIL. Because the judge sees a single sentence and a fixed definition, its variance is far lower than a whole-paper judgment.
    - constraints: Ecosystem must provide: enum-term definitions in edge_schema.yaml; a labelled calibration set of licensed/unlicensed quote-feature pairs per domain; a judge-ensemble id and pinned prompt. This is the ONE place an LLM touches the 'structural' layer, and it is boxed to a per-sentence binary — it cannot invent attrs, only accept/reject an already-anchored one.
  - **EDGE-PROSE-RECONCILE (restores the independent second source)** — On every compile. Answers critique #2's core: prose must NOT be a mere rendering of edges, or the cross-check dies.. 1. Prose layers (claims.md, experiments.md, related_work.md) are authored/maintained INDEPENDENTLY and remain the human surface. 2. The compiler extracts a relation set from prose (the existing Proof/Verifies/Caused-by/Type fields). 3. Round-trip check: every prose relation must have a corresponding edge (missing -> prose_relation_unedged) AND every author-stated edge must trace to a prose relation via its source_anchor (extra -> edge_without_prose). 4. Divergences are reported as a first-class anti-fabrication signal, NOT auto-resolved. A compiler that mis-extracts now produces a prose/edge disagreement instead of silently becoming ground truth.
    - reliability/reproducibility: Deterministic set-difference given a fixed prose extractor; the extractor itself is versioned. The point is not perfect extraction but that two independent representations must agree, so a single-sided fabrication surfaces.
    - constraints: Ecosystem must provide a versioned, deterministic prose-relation extractor and forbid the compiler from writing prose FROM edges (one-way ban), so the two sources stay independent.
  - **ENTAIL (Class C semantic verdict, append-only)** — After STRUCTURAL-CHECK passes for an edge, to answer 'does this relation actually hold?'. 1. Only edges with structural_status==ok are eligible. 2. A judge ensemble produces for/against arguments and a holds verdict with confidence, reviewing only the anchored nodes named on the edge (bounded context). 3. The verdict is APPENDED to verdicts.yaml keyed by edge_id + rubric_version + ensemble id; edges.yaml.verdict_ref is set by the tool, never authored. 4. Revisions supersede, never edit.
    - reliability/reproducibility: Reproducible-to-inputs via pinned ensemble + calibration_set_id + run_id; auditable via for/against and anchors_reviewed. Judge degrees of freedom are minimized because structural adequacy (endpoints, features, reconciliation) is already settled deterministically — the judge only weighs the irreducible semantic residual.
    - constraints: Ecosystem must provide: judge ensembles with published calibration performance; per-domain calibration sets; immutable append-only storage.

  _Metrics afforded:_
  - Structural correspondence coverage — fraction of cross-layer relations that resolve to typed edges with all required, ANCHORED attrs present → Deterministic join over edges.yaml x edge_schema.yaml x nodes.yaml; a relation counts only if endpoints resolve, required_attrs present, and every requires_anchor attr has an anchor that passes ANCHOR-VERIFY Part A. [deterministic]; anti-Goodhart: Padding with edges cannot raise it because coverage is measured against the prose relation set (EDGE-PROSE-RECONCILE) — an edge with no prose counterpart is edge_without_prose, not coverage. Anchors must resolve to real node text, so fabricated-but-consistent attrs fail Part A.
  - Test adequacy — fraction of claims whose claim_type's required design_features are satisfied by a licensed, author-stated tests edge → Deterministic rubric lookup gated by rubric_satisfaction_policy: a feature counts only if declared_by==author-stated AND licensing_status==licensed AND its anchor resolves. [reliable-anchored]; anti-Goodhart: Directly kills the v1 exploit the reviewer named: you cannot list design_features=[network_meta_analysis, baseline_comparison] to clear the improvement rubric unless each feature is anchored to real method text AND a per-sentence licensing check confirms the quote supports it. compiler-inferred features are structurally barred from counting, so the compiler cannot manufacture adequacy.
  - Reconciliation integrity — fraction of supports/measures edges whose numeric value matches the quantity ledger → COMPUTED by STRUCTURAL-CHECK step 6 against the ledger; author-supplied reconciliation is discarded. [deterministic]; anti-Goodhart: Because reconciliation is computed not authored, a fabricated 'exact' is impossible — a mismatched number yields reconciliation_mismatch regardless of what the author wrote. Consistent-but-wrong numbers surface as ledger disagreements.
  - Honest-absence legality — fraction of null/not_applicable slots that are genre-legal → Deterministic lookup against nullability.yaml keyed on paper_type; legal nulls scored EQUAL to present values, illegal nulls flagged illegal_null. [deterministic]; anti-Goodhart: Answers 'not_applicable is the universal escape': an RCT nulling its dataset is a defect, a meta-analysis nulling it is honest — the genre table, not the author, decides. No pressure to fabricate a dataset, but no free absence either.
  - Relates ratio — fraction of edges routed to the untyped `relates` fallback → Deterministic count; flagged when > relates_policy.max_fraction; each relation_note validated against StructuredRelationNote. [deterministic]; anti-Goodhart: Answers 'relates is an uncapped Goodhart drain': a pass-rate-maximizing compiler that dumps hard edges into relates now trips the cap flag, and relation_note cannot re-import prose (char cap + >=2 node ids + controlled verb). Specificity is rewarded; free-text dumping is bounded and visible.
  - Graph acyclicity — count of cycles in each declared-acyclic subgraph → Deterministic Tarjan SCC per acyclicity.yaml subgraph. [deterministic]; anti-Goodhart: Cannot be gamed by relabeling because the subgraph membership is fixed by edge type in the ecosystem spec; a circular dependency/support/provenance chain is a hard defect regardless of prose framing.
  - Anchor-licensing rate — fraction of gating attr anchors whose quote is judged to license the typed value → ANCHOR-VERIFY Part B per-sentence binary, logged with for/against and calibration_set_id. [reproducible]; anti-Goodhart: The judge sees only one sentence + a fixed enum definition, so it cannot be flooded with boilerplate; a padded or off-topic quote is judged unlicensed. Reproducibility is tracked against a labelled calibration set, so a drifting judge is detectable rather than silently permissive.
  - Semantic hold rate — fraction of structurally-ok edges ENTAIL judges to hold → Judge ensemble over anchored nodes only; logged append-only in verdicts.yaml. [semantic-judged]; anti-Goodhart: Kept deliberately downstream and separate so it cannot inflate the deterministic metrics; for/against + calibration + bounded context minimize judge degrees of freedom, and verdict_ref being computed prevents an author from pre-declaring 'holds'.

  _Tradeoffs:_ Authoring cost rises: every rubric-gating feature now needs a resolvable anchor with a real quote, which is more work than v1's bare enum list — mitigated because the anchor is the same method-text a scientist already wrote, and honest-absence stays free where the genre permits it (no fabrication pressure). The licensing check (ANCHOR-VERIFY Part B) reintroduces an LLM into what I call the 'structural' layer — an honest concession — but it is boxed to a per-sentence accept/reject over an already-anchored value, so it can only reject fabrications, never invent attrs, and it is scored against a calibration set. The nullability and acyclicity tables are ecosystem infrastructure someone must maintain per paper_type/edge-type; a stale or coarse table could mislabel an honest null as illegal — mitigated by a conservative default and by treating table gaps as flags, not silent passes. EDGE-PROSE-RECONCILE depends on a deterministic prose extractor whose recall is imperfect; low recall produces spurious prose_relation_unedged noise — mitigated by versioning the extractor and reporting divergences as signals for human review rather than auto-failing. The main residual fabrication surface is a quote that is real and locally licensing but globally misleading (cherry-picked sentence); ENTAIL's whole-of-anchors semantic pass is the backstop, and the for/against log makes such cherry-picking auditable. Finally, `relates` cap tuning is a genuine knob: too low forces false-precision typing, too high reopens the drain — it is versioned and reportable so it can be calibrated empirically per genre.

  _Open questions:_ 1. How coarse can the enum-term definitions be before the licensing judge's binary becomes unstable across domains — does every field need its own design_features vocabulary and calibration set? 2. What is the right per-genre relates cap, and should it be a hard flag or a smooth penalty? 3. EDGE-PROSE-RECONCILE assumes prose and edges are independently authored, but in an all-agents-publish world the same agent may write both — does independence survive, or do we need two distinct extractors/authors to keep the cross-check meaningful? 4. Cross-ARA edges (this paper's claim contradicts another paper's claim) need node ids that resolve across artifact boundaries — the registry here is per-ARA; the federation scheme is unspecified. 5. Reconciliation tolerance (within_tolerance) needs a principled per-quantity epsilon from the quantity ledger's declared precision — who owns that? 6. Whether licensing_status should itself be append-only/audited like ENTAIL verdicts, since it is judge-produced, rather than living inline in edges.yaml.

  _Changes from critique:_ 1) UNANCHORED ATTRS (critique #1): every rubric-gating attr value is now an AnchoredValue {value, anchor:{node,locator,quote}, licensing_status}; requires_anchor is a schema flag; STRUCTURAL-CHECK counts a feature toward a claim_type rubric ONLY if its anchor resolves and is licensed. design_features can no longer be a compiler inference in a deterministic costume. 2) INVERSION (critique #2): reversed v1's 'prose renders from edges' — prose is now authored INDEPENDENTLY and EDGE-PROSE-RECONCILE checks edges AGAINST it (round-trip), restoring the second source; added ANCHOR-VERIFY with (a) deterministic literal-quote-at-locator and (b) a bounded per-sentence licensing check. 3) RELATES DRAIN (critique #3): added relates_policy with max_fraction cap (flag on exceed) and a StructuredRelationNote schema (char cap, >=2 node ids, controlled verbs) so relation_note can't re-import prose. 4) declared_by UNGUARDED (critique #4): author-stated now REQUIRES a source_anchor (trust_tier_violation otherwise) and rubric_satisfaction_policy FORBIDS compiler-inferred from satisfying any rubric requirement. 5) not_applicable ESCAPE (critique #5): added nullability.yaml, a genre-conditioned table of which nulls are legal per paper_type; illegal nulls -> illegal_null. 6) reconciliation AUTHORED? (critique #6): reconciliation is now COMPUTED by the checker against the quantity ledger and FORBIDDEN in author input, same discipline as structural_status. 7) DAG/CYCLES (critique #7): added acyclicity.yaml declaring which edge-type subgraphs must be acyclic plus a Tarjan SCC detection step (cycle_violation).

  _Adopted from competitor:_ Adopted the competitor's explicit graph/nodes.yaml global node registry with per-node {type, layer, locator} — cleaner than my v1 inline URN convention and, crucially, it gives ANCHOR-VERIFY the resolvable file:locator it needs to confirm an attr's anchor points into real node text. Adopted their edge_schema.yaml attr-typing discipline (each attr with type/nullable/null_reason_required) and folded requires_anchor into it. Adopted their claim_type_requirement-on-tests idea and their richer edge-type set (rw-relates with relation/delta_magnitude, corroborates with perspective, calibrates, contradicts with contradiction_type, registered-as). Most importantly, adopted their core stance that prose stays the independent human surface and the graph is checked AGAINST prose — the exact fix the reviewer demanded for my inversion problem.

  _Why it wins:_ The competitor asserts 'the graph and prose must agree' and 'a checker can verify a structured correspondence deterministically' but leaves the load-bearing mechanisms unspecified, precisely where the reviewer says determinism must be earned: (a) their design_features is still a bare enum list with no per-feature anchor, so their claim_type check has the same unanchored-attr hole the reviewer flagged in mine — I close it with AnchoredValue + ANCHOR-VERIFY licensing. (b) They have no declared_by/trust-tier concept at all, so nothing stops a shaky inference from satisfying a rubric — I gate it (author-stated requires anchor; compiler-inferred barred from rubrics). (c) Their nullable/null_reason_required is genre-blind, so not_applicable is still a universal escape — I add the genre-conditioned nullability table. (d) They put reconciliation-style checks in edge_schema but never say attrs are computed-not-authored — my structural_status, reconciliation, licensing_status, and verdict_ref are all machine-produced and forbidden in author input. (e) They name no acyclic subgraphs and no cycle step despite depends-on/derived-from/corroborates being obviously cyclable — I specify acyclicity.yaml + SCC detection. (f) My verdict log is separate AND append-only with supersede semantics and calibration ids; theirs is 'judge-authored, versioned' but not append-only, leaving room to edit history. Net: same typed-multigraph backbone, but every place the reviewer said 'deterministic is a costume,' I replace the costume with a mechanism the competitor doesn't have. A genuine merge — their nodes.yaml + prose-as-independent-source, my computed-fields discipline, per-attr anchoring, trust tiers, genre nullability, and cycle spec — is strictly better than either alone.


### Finalist B (refined)

> _Judge critique it answered:_ TCG (#2) — you win on the cleanest Class-A/Class-C boundary (entailment_verdicts.yaml is a fully separate file, so the deterministic skeleton is structurally incapable of being contaminated by a judgment call), and on the ecosystem-schema-vs-per-paper-instance split (edge_schema.yaml as shared JSON-Schema-for-relations is the right infrastructure altitude). But several of your headline claims are promissory notes:\n\n1) \"GRAPH AND PROSE MUST AGREE = DETERMINISTIC ANTI-FAB SIGNAL\" IS UNDERSPECIFIED TO THE POINT OF BEING NON-DETERMINISTIC. Agreement-checking free prose against typed edges is NOT deterministic until you define the matching predicate. If agreement means \"the id appears somewhere in the prose,\" you have rebuilt exactly the existence-binding the gap declares insufficient. Specify the agreement predicate PER ATTRIBUTE — does the prose have to contain the baseline, the measured quantities, the design_features, or just the endpoint id? — or drop the claim. This is your best idea and your softest spot.\n\n2) design_features IS THE DETERMINISTIC CRUX AND THE MOST FABRICABLE FIELD. A compiler writes design_features:[ablation], the rubric passes a causal claim, and nothing verifies the ablation ACTUALLY exists in the experiment. You need design_features to be backed by resolvable pointers into Method/Evidence nodes (features-must-cite-evidence), else claim_type gating is a rubber stamp with extra steps.\n\n3) STALE-VERDICT HOLE. entailment_verdicts.yaml is cleanly separated — good — but you never specify keying or staleness. When an edge in edges.yaml mutates (gains a baseline attr), how is the prior ENTAIL verdict invalidated? Without a content-hash/fingerprint on the edge that the verdict references, stale verdicts silently apply to changed edges — a reproducibility hole that violates the Class-C ceiling you claim to honor. #3's verdict_ref is closer; you need an edge fingerprint.\n\n4) NO RUBRIC VERSION PIN VISIBLE ON THE INSTANCE. You hardcode claim_type_requirement (causal→ablation, improvement→baseline_comparison) at the ecosystem level, but if that rubric evolves, past checker results become irreproducible unless each ARA pins a rubric_version. #3 states this explicitly; you must too or your determinism is not reproducible over time.\n\n5) QUANTITIES OFFLOADED TO A 'SIBLING LEDGER.' Your supports/measures edges REQUIRE quantity refs and numeric matching — that reconciliation is where your determinism earns its keep — yet the quantity contract lives in another design. Import it or your central numeric check is a promissory note pointing at a file you didn't specify.\n\n6) INCOMPLETE-GRAPH ATTACK UNADDRESSED. Per-edge legality (reject illegal `tests` from a Concept) is good, but the cheapest way to pass is to OMIT the hard edges. What forces coverage — every Claim needs ≥1 inbound tests/supports edge; every experiment's declared measures must be edged; every load-bearing number in prose must be a Quantity node with an inbound measures/reports edge? Without coverage obligations, selective omission is an open gaming lane.

**TCG/2 — The Typed Cross-Layer Graph with per-attribute evidence binding, edge fingerprints, and coverage obligations**  ·  _source: claude-opus-4-8_

TCG makes the whole ARA a real typed multigraph: a node registry (nodes.yaml) gives every addressable object one stable typed id; an ecosystem-level ontology (edge_schema.yaml) declares which relation types are legal between which node types and what structured attributes each must carry; an instance file (edges.yaml) is the single source of truth for every cross-layer relation the prose today writes as bare id-lists (Proof, Verifies, Caused by, Derived from, Baselines); and semantic verdicts live in a fully separate, judge-authored file (entailment_verdicts.yaml) so the deterministic skeleton can never be contaminated by a judgment call. The critique's core objection — that 'the graph and the prose must agree' was non-deterministic — is fixed by making agreement a PER-ATTRIBUTE typed predicate (evidence_binding): each attribute declares whether its value must be a literal substring of an anchor quote, a resolvable node ref of a specific type, a Quantity ledger ref that must numerically reconcile, or an honestly-free string — so 'agreement' is a set of exact, mechanical checks, never 'the id appears somewhere.' design_features stop being a fabricable label because each feature must cite a resolvable Method/Evidence node (features-must-cite-evidence); every edge carries a content fingerprint so a stale ENTAIL verdict on a mutated edge is detected deterministically; every ARA pins schema_version + rubric_version; and coverage obligations make selective omission a first-class failure (every Claim needs an inbound tests/supports edge, every declared measured quantity needs a measures edge, every load-bearing number in prose needs a Quantity node with an inbound edge). This closes the gap: structural correspondence is verified before any LLM runs, and the irreducible 'does it really hold' question is the only thing left for the judge.

- **nodes.yaml** (YAML, one file per ARA at graph/nodes.yaml) — Global registry giving every addressable object across every layer one stable, typed id with a provenance locator — the fixed endpoints edges point at, and the surface an addressable honest-absence target plugs into.
  - fields: id: string (prefix encodes type: C##/E##/G##/O##/A##/CPT##/RW##/CST##/MTH##/Q####/DA##/T##/REG##) — required, globally unique; type: enum{Observation,Gap,KeyInsight,Assumption,Claim,Concept,Experiment,Quantity,RelatedWork,Constraint,Method,Environment,DataAsset,Evidence,ExternalRegistration,Absence} — required; layer: string, file the node's primary content lives in — required; locator: string, section/heading/line anchor — required; canonical_label: string, the human name a quote_literal binding matches against — required for nodes that can be cited by anchored attrs, else not_applicable; alias_of: string — optional, for pre-existing ids later merged
  - example: version: "1.0"
nodes:
  - {id: C01, type: Claim, layer: logic/claims.md, locator: "## C01", canonical_label: "plasma p-tau217 outperforms p-tau181 for AD detection"}
  - {id: E01, type: Experiment, layer: logic/experiments.md, locator: "## E01", canonical_label: "network meta-analysis of 18 studies"}
  - {id: MTH03, type: Method, layer: logic/solution/study_design.md, locator: "§Ablation: assay-dropout", canonical_label: "assay-dropout ablation"}
  - {id: T02, type: Evidence, layer: evidence/tables/table2.md, locator: "Table 2, Outcome 1", canonical_label: "head-to-head AUC table"}
  - {id: Q0859, type: Quantity, layer: quantities.yaml, locator: "Q0859", canonical_label: "AUC p-tau217 MS"}
  - {id: ABS_DATA, type: Absence, layer: graph/nodes.yaml, locator: "reserved", canonical_label: "no accessioned raw dataset"}   # addressable not_applicable target
- **edge_schema.yaml** (YAML, one versioned file distributed with the checker tooling (JSON-Schema-for-relations altitude)) — Ecosystem-level ontology (shared, not per-paper): legal (from-type -> to-type) pairs per edge type, required/optional attributes, and — the fix for the non-determinism critique — a per-attribute evidence_binding that turns 'prose and graph agree' into a set of exact mechanical predicates. Also declares coverage obligations and the claim_type rubric, all under a pinned version.
  - fields: schema_version: string; rubric_version: string; edge_types.<name>.from: list[NodeType] — required; .to: list[NodeType] — required; .required_attrs / .optional_attrs: map[attr -> {type, enum?, nullable, null_reason_required, evidence_binding}] — required; evidence_binding: enum{quote_literal, node_ref(<allowed_types>), ledger_ref, derived, free} — required per attr — quote_literal = value's canonical form must be a normalized substring of source_anchor.quote; node_ref = value is a node id resolving to one of allowed_types; ledger_ref = value is a Quantity id that must resolve AND pass numeric reconciliation; derived = computed by compiler, must carry provenance_edge; free = honest unbound string, scored as lower-specificity never rejected; .claim_type_requirement: map (only on tests); coverage_obligations: list of checker rules; fallback type `relates` [*->*] with one free relation_note
  - example: schema_version: "1.0"
rubric_version: "claimtype-2026.2"
edge_types:
  tests:
    from: [Experiment]
    to: [Claim]
    required_attrs:
      design_features:
        type: "list<{feature: enum[ablation,heterogeneous_data,baseline_comparison,sampling_frame,bound_check,replication], grounding: ref}>"
        evidence_binding: node_ref(Method,Evidence)   # features-must-cite-evidence
      measures: {type: "list<ref:Quantity>", evidence_binding: ledger_ref}
      baseline: {type: "ref:Quantity|ref:Method|ref:RelatedWork", nullable: true, null_reason_required: true, evidence_binding: node_ref(Quantity,Method,RelatedWork)}
      expected_direction: {type: enum[increase,decrease,equal,rank_order,unspecified], evidence_binding: free}
    claim_type_requirement:
      causal:          {design_features_must_include: [ablation]}
      improvement:     {design_features_must_include: [baseline_comparison]}
      generalization:  {design_features_must_include: [heterogeneous_data]}
      descriptive:     {design_features_must_include: [sampling_frame]}
      scoping:         {design_features_must_include: [bound_check]}
  supports:
    from: [Evidence]
    to: [Claim]
    required_attrs:
      quantity_ids: {type: "list<ref:Quantity>", evidence_binding: ledger_ref}
      reported_value: {type: number, evidence_binding: quote_literal}   # must appear in the anchor quote
  measures:
    from: [Experiment]
    to: [Quantity]
    required_attrs: {role: {type: enum[input,result], evidence_binding: free}, unit: {type: string, evidence_binding: ledger_ref}}
  baselines-against:
    from: [Experiment]
    to: [Method,RelatedWork,Experiment]
    required_attrs:
      comparison_type: {type: enum[superiority,non_inferiority,equivalence,descriptive_only], evidence_binding: free}
      baseline_quantity: {type: "ref:Quantity", nullable: true, null_reason_required: true, evidence_binding: ledger_ref}
  bounds:      {from: [Constraint], to: [Claim,Method,Concept], required_attrs: {scope_dimension: {type: enum, source: quantity_ledger.dimensions, evidence_binding: free}, limiting_condition: {type: string, evidence_binding: quote_literal}}}
  assumes:     {from: [Claim,Method,Experiment], to: [Assumption], required_attrs: {criticality: {type: enum[low,medium,high], evidence_binding: free}}}
  uses-data:   {from: [Experiment,Method], to: [DataAsset,Absence], required_attrs: {role: {type: enum[train,eval,validation,external_replication,not_applicable], evidence_binding: free}, access_tier: {type: enum[open,controlled,restricted,not_specified], evidence_binding: free}}}
  contradicts: {from: [Claim,RelatedWork,Evidence], to: [Claim], required_attrs: {contradiction_type: {type: enum[direct,scope,magnitude], evidence_binding: free}}}
  resolves:    {from: [Claim], to: [Gap], required_attrs: {completeness: {type: enum[full,partial], evidence_binding: free}}}
  relates:     {from: ["*"], to: ["*"], required_attrs: {relation_note: {type: string, evidence_binding: quote_literal}}}   # honest fallback, lower specificity
coverage_obligations:
  - id: COV1
    rule: "every Claim node has >=1 inbound edge of type in {tests,supports}"
    on_fail: coverage_gap
  - id: COV2
    rule: "for every measures edge with role=result on Experiment X, the Claim(s) X tests must be reachable via supports/tests; every Quantity X declares measured must have an inbound measures edge"
    on_fail: orphan_quantity
  - id: COV3
    rule: "every load-bearing number flagged in prose (quantity_ledger.load_bearing=true) resolves to a Quantity node with an inbound measures|supports edge"
    on_fail: unbacked_number
- **edges.yaml** (YAML, one file per ARA at graph/edges.yaml) — Per-ARA instance graph: every cross-layer relation, typed per edge_schema, each carrying required structured attributes, a mandatory source_anchor with a literal quote, a declared_by provenance tag, a computed content fingerprint (staleness anchor for verdicts), and a checker-computed structural_status. This is the deterministic sidecar the prose is checked against.
  - fields: schema_version: string — required, pins edge_schema; rubric_version: string — required, pins claim-type rubric; ara_id: string — required; edges: list[Edge]. Edge = {id: EDG#### unique+stable across recompiles — required; type: key in edge_schema — required; from: node id resolving in nodes.yaml — required; to: node id resolving in nodes.yaml — required; declared_by: enum[author-stated,derived,compiler-inferred] — required (WHO asserted the edge, distinct from whether it holds); source_anchor: {file, locator, quote} — required unless declared_by=derived, then provenance_edge: EDG-id; attrs: object satisfying edge_schema, every field nullable via not_specified/not_applicable with null_reason — required (may be attr-sparse, not absent); fingerprint: sha256 of canonicalize(type,from,to,attrs) — COMPUTED, never authored; structural_status: enum[ok,missing_required_attr,dangling_endpoint,type_mismatch,binding_violation,reconciliation_mismatch,coverage_gap] — COMPUTED; verdict_ref: EDG-id-keyed pointer into entailment_verdicts.yaml | null — appended by ENTAIL, never authored}
  - example: schema_version: "1.0"
rubric_version: "claimtype-2026.2"
ara_id: che26-plasma-ptau217
edges:
  - id: EDG0001
    type: tests
    from: E01
    to: C01
    declared_by: author-stated
    source_anchor: {file: logic/experiments.md, locator: "E01 Verifies", quote: "E01 verifies C01 via head-to-head AUC comparison against p-tau181, with an assay-dropout ablation"}
    attrs:
      claim_type_at_declare: improvement
      design_features:
        - {feature: baseline_comparison, grounding: T02}   # resolves to Evidence node
        - {feature: ablation, grounding: MTH03}            # resolves to Method node -> causal-ready if reclassified
      measures: [Q0859, Q0860]
      baseline: Q0860
      expected_direction: increase
    fingerprint: "sha256:9f21...c4"
    structural_status: ok
    verdict_ref: EDG0001@9f21c4
  - id: EDG0002
    type: supports
    from: T02
    to: C01
    declared_by: author-stated
    source_anchor: {file: logic/claims.md, locator: "C01 Sources", quote: "0.859 <- table2.md (Table 2, Outcome 1) p217_MS 0.859 [result]"}
    attrs: {quantity_ids: [Q0859], reported_value: 0.859}   # reported_value 0.859 is a substring of quote -> quote_literal passes
    fingerprint: "sha256:1a08...bd"
    structural_status: ok
  - id: EDG0005
    type: uses-data
    from: E01
    to: ABS_DATA
    declared_by: author-stated
    source_anchor: {file: logic/experiments.md, locator: "E01 Setup", quote: "reuses published summary statistics; no accessioned raw dataset"}
    attrs: {role: not_applicable, access_tier: not_specified, null_reason: "meta-analysis of summary stats"}
    fingerprint: "sha256:77ce...02"
    structural_status: ok
- **entailment_verdicts.yaml** (YAML, append-only, one file per ARA at graph/entailment_verdicts.yaml) — The Class-C semantic layer, physically separate so the deterministic skeleton is structurally incapable of contamination. Each verdict references an edge BY FINGERPRINT so a mutated edge silently invalidates its prior verdict — closing the stale-verdict hole. Append-only and judge-authored; the checker never writes here and ENTAIL never writes edges.yaml.
  - fields: schema_version: string; judge_protocol_version: string — required; verdicts: list[Verdict]. Verdict = {edge_id: EDG-id — required; edge_fingerprint: sha256 the verdict was rendered against — required; verdict: enum[ENTAIL,WEAKEN,CONTRADICT,INSUFFICIENT] — required; confidence: number 0-1; for_evidence: list[node/anchor]; against_evidence: list[node/anchor]; judge_ensemble: list[{model, seed}]; rendered_at: timestamp}. A verdict is STALE (auto-computed on load) iff edge_fingerprint != current edges.yaml fingerprint for edge_id.
  - example: schema_version: "1.0"
judge_protocol_version: "entail-2026.1"
verdicts:
  - edge_id: EDG0001
    edge_fingerprint: "sha256:9f21...c4"
    verdict: ENTAIL
    confidence: 0.82
    for_evidence: [T02, {file: evidence/tables/table2.md, locator: "Outcome 1 Rank 1"}]
    against_evidence: [{file: logic/related_work.md, locator: "RW03 scope caveat"}]
    judge_ensemble: [{model: A, seed: 11}, {model: B, seed: 11}, {model: A, seed: 12}]
    rendered_at: 2026-07-06T10:00:00Z
    # if edges.yaml EDG0001.fingerprint later becomes 9f21c4 -> ab99..., this verdict loads as STALE and is excluded
- **quantity_interface.md (imported contract)** (typed-markdown spec + the reconciliation predicate the checker imports) — Makes the central numeric check real instead of a promissory note: the minimal interface TCG requires the sibling quantity ledger to expose, and the exact reconciliation predicate ledger_ref bindings run. Without this, measures/supports determinism points at a file this design did not specify — the critique's point 5.
  - fields: Required per Quantity node: {id, value: number|interval, unit: string, dimension: enum, role: input|result, tolerance: number|rel_pct, load_bearing: bool}. Reconciliation predicate for a ledger_ref attr referencing Quantity q with asserted value v: PASS iff unit(q) compatible-with declared unit AND |v - value(q)| <= tolerance(q) (or interval-contains for interval-valued q); dimension(q) must equal the binding's expected dimension; role mismatch (input vs result) => reconciliation_mismatch.
  - example: # Quantity ledger interface (v1)
Q0859: {value: 0.859, unit: AUC, dimension: dimensionless_ratio, role: result, tolerance: 0.001, load_bearing: true}
Q0860: {value: 0.741, unit: AUC, dimension: dimensionless_ratio, role: result, tolerance: 0.001, load_bearing: true}
# supports edge EDG0002 asserts reported_value 0.859 for Q0859:
#   |0.859 - 0.859| = 0 <= 0.001  -> reconciliation ok
#   unit AUC matches, dimension matches, role=result matches -> ledger_ref binding PASS

  _Protocols:_
  - **Deterministic structural + binding checker** — On every compile/recompile, before any LLM runs; gates what ENTAIL is even allowed to see.. 1) Resolve every edge.from/edge.to against nodes.yaml -> dangling_endpoint on miss. 2) Check (from-type,to-type) legal per edge_schema -> type_mismatch. 3) Check required_attrs present or explicitly nulled with null_reason -> missing_required_attr (honest null passes). 4) For each attr run its evidence_binding predicate: quote_literal = normalized substring of source_anchor.quote; node_ref = value resolves and target type in allowed set; ledger_ref = resolves + reconciliation predicate passes; derived = provenance_edge resolves and is ok; free = accept -> binding_violation / reconciliation_mismatch on failure. 5) For tests edges, look up claim_type_at_declare in claim_type_requirement and confirm required design_features present AND each feature.grounding resolves to a legal Method/Evidence node -> missing_required_attr. 6) Compute fingerprint = sha256(canonicalize(type,from,to,attrs)). 7) Run coverage_obligations COV1-COV3 -> coverage_gap/orphan_quantity/unbacked_number. 8) Emit structural_status per edge and a coverage report.
    - reliability/reproducibility: Class A: pure function of (edges.yaml, nodes.yaml, edge_schema.yaml@schema_version, quantity_ledger@version). Same inputs => byte-identical statuses and fingerprints. No network, no LLM, no clock.
    - constraints: Ecosystem must ship: the pinned edge_schema.yaml, the quantity ledger exposing quantity_interface fields, a canonicalization spec (stable key ordering, number normalization) so fingerprints are reproducible, and a normalization function for quote_literal (case/whitespace/unicode fold) published with the checker version.
  - **Prose<->graph agreement lint (per-attribute)** — Whenever prose is human-authored (TCG keeps prose as the readable surface rather than a pure render).. For each edge, for each attribute whose evidence_binding is quote_literal, require the attribute's canonical rendering to be a normalized substring of source_anchor.quote AND require source_anchor.quote to be a verbatim substring of the file at source_anchor.file/locator. node_ref/ledger_ref attrs are agreed-by-resolution, not by prose text. free attrs are exempt (and flagged lower-specificity). Emit agreement_status; disagreement is a deterministic anti-fabrication signal, not a judgment.
    - reliability/reproducibility: Class A. Because the predicate is fixed PER ATTRIBUTE ('does 0.859 literally appear in the quoted span', 'does the baseline node resolve') rather than 'is the id mentioned somewhere', it cannot degrade into existence-only binding.
    - constraints: Requires stable file locators (anchors survive edits) and the published normalization function. If prose is instead auto-rendered from edges, this lint is vacuous — so TCG mandates author-stated prose for load-bearing edges to preserve the cross-check as real signal.
  - **Verdict staleness + ENTAIL rendering (Class C)** — After structural pass; and on every load of entailment_verdicts.yaml.. On load, for each verdict compare edge_fingerprint to the current edges.yaml fingerprint for edge_id; mismatch => mark STALE and exclude from all metrics until re-rendered. ENTAIL is invoked only for edges with structural_status=ok and no fresh verdict; it renders verdict + confidence with for/against evidence anchors, an ensemble of models/seeds, and appends (never overwrites) keyed by (edge_id, current fingerprint). judge_protocol_version pinned per file.
    - reliability/reproducibility: Class C: reproducibility via fixed judge_protocol_version, model+seed ensemble logged, for/against evidence required, confidence surfaced. Auditability via append-only history keyed to fingerprints — you can always see which edge content a verdict judged. Run-to-run drift is bounded by ensemble agreement reporting.
    - constraints: Ecosystem must provide: a calibration set of gold ENTAIL/CONTRADICT edges to score judge drift, the judge ensemble runner, and a policy that ANY edge attr mutation re-hashes and invalidates downstream verdicts.
  - **Coverage obligation enforcement (anti-omission)** — Every compile; the defense against 'pass by omitting hard edges'.. Enumerate all Claim nodes -> COV1 requires >=1 inbound tests/supports or an explicit, scored coverage-waiver node (e.g. claim marked speculative). Enumerate every Quantity with load_bearing=true or declared-measured by an Experiment -> COV2/COV3 require an inbound measures/supports edge. Report coverage as a ratio AND a list of specific gaps; unmet obligations set structural_status=coverage_gap on the offending node, not a silent pass.
    - reliability/reproducibility: Class A: deterministic graph enumeration. Coverage is computed over the node set, so omitting an edge raises a gap on the node that still exists — you cannot hide by not writing the edge.
    - constraints: Requires the quantity ledger's load_bearing flag and that Claims/Quantities are registered as nodes even when their edges are missing (registry completeness is itself a checked obligation).

  _Metrics afforded:_
  - Structural correspondence rate (fraction of edges with structural_status=ok) → Deterministic checker over edges.yaml + nodes.yaml + edge_schema; counts ok vs each failure enum. [deterministic]; anti-Goodhart: Padding with easy edges cannot inflate it because honest nulls pass equally and coverage_obligations independently demand the HARD inbound tests/supports edges exist; you cannot raise the rate by adding trivial `relates` edges since those score lower-specificity and do not satisfy COV1.
  - Claim testability coverage (Claims with a schema-adequate inbound tests edge / all Claims) → COV1 plus claim_type_requirement: a causal claim only counts if its tests edge has an ablation design_feature whose grounding resolves to a real Method/Evidence node. [deterministic]; anti-Goodhart: features-must-cite-evidence: writing design_features:[ablation] with no grounding node fails node_ref binding, so the rubric is not a rubber stamp. Fabricating a grounding id fails resolution; pointing at an unrelated node type fails the allowed-type check.
  - Numeric reconciliation pass rate (supports/measures/baseline attrs whose ledger_ref reconciles) → For each ledger_ref attr, run the imported reconciliation predicate against the quantity ledger (unit/dimension/role/tolerance). [deterministic]; anti-Goodhart: A fabricated-but-internally-consistent number still fails because the value must match the ledger Quantity within tolerance AND appear literally in the anchor quote (quote_literal); you cannot satisfy both by inventing a value that agrees only with itself.
  - Prose<->graph agreement (quote_literal attrs that verbatim-match their anchored span) → Per-attribute substring predicate over source_anchor.quote and the underlying file span. [deterministic]; anti-Goodhart: Existence-only binding is impossible: the checked thing is the baseline value / limiting_condition / reported_value literally present in the quote, not that an id is mentioned. Copy-pasting a quote that lacks the value fails; the quote itself must be a verbatim substring of the file, blocking fabricated quotes.
  - Verdict freshness (non-stale ENTAIL verdicts / edges with verdicts) → Compare each verdict.edge_fingerprint to the live edge fingerprint; stale ones excluded. [reproducible]; anti-Goodhart: You cannot bank a favorable verdict and then quietly mutate the edge to a stronger claim: any attr change re-hashes the fingerprint and marks the verdict stale, forcing re-judgment. Fingerprint is computed, not authored, so it cannot be spoofed to match.
  - Semantic hold rate (edges with ENTAIL verdict, weighted by confidence, for/against logged) → ENTAIL ensemble over structurally-ok edges only; aggregated with confidence and dissent. [semantic-judged]; anti-Goodhart: Judge degrees of freedom minimized: the judge only sees pre-validated edges and answers the single narrowed 'does it hold' question with mandatory against_evidence; ensemble+seed logging and a calibration set expose a judge that rubber-stamps. Length/boilerplate is invisible to the judge because it reasons over typed edge attrs and anchors, not prose volume.

  _Tradeoffs:_ Costs: (1) Author/compiler burden — every load-bearing relation must be emitted as a typed edge with grounded design_features and anchored quotes; mitigated by the compiler auto-deriving edges from existing Proof/Verifies fields (declared_by=compiler-inferred) and only requiring humans to confirm. (2) quote_literal binding is brittle to paraphrase — a true relation stated in prose that does not contain the literal value fails agreement; mitigated by allowing free binding for attrs where literal match is inappropriate and by scoring free as honest-lower-specificity, never fabrication. (3) Fingerprint churn — benign reformatting could invalidate verdicts; mitigated by canonicalization (fingerprint hashes semantic attrs, not whitespace/key order). Fabrication surfaces: design_features grounding could cite a real-but-irrelevant Method node (type-legal, semantically empty) — structural check catches type, but semantic relevance is deliberately left to ENTAIL (correct class boundary, not a leak); coverage waivers could be abused to mark hard claims 'speculative' — mitigated by counting waivers as a visible, scored honesty signal (many waivers lowers testability coverage, it does not hide it). Honest-absence is symmetric throughout: not_applicable targets are addressable nodes, null_reason-carrying attrs pass, and none are penalized like a fabricated presence.

  _Open questions:_ 1) Canonicalization for fingerprints across number formats/units needs an ecosystem-frozen spec or fingerprints diverge between compilers. 2) quote_literal normalization (unicode, rounding of reported_value vs ledger value) has genuine edge cases — how much rounding tolerance before literal-match is 'agreement'? 3) The claim_type rubric is itself contestable science-of-science; rubric_version pins reproducibility but not correctness — who governs the vocabulary evolution. 4) Coverage obligations assume the Quantity ledger honestly flags load_bearing numbers; a compiler could under-flag to dodge COV3 — needs a cross-check that prose numbers not in the ledger are themselves a flagged gap. 5) Grounding resolves TYPE but not RELEVANCE of a cited Method/Evidence node — the residual semantic gap is correctly ENTAIL's, but the boundary between 'structurally cited' and 'actually demonstrates the feature' will be probed.

  _Changes from critique:_ 1) Agreement predicate is now specified PER ATTRIBUTE via evidence_binding{quote_literal|node_ref|ledger_ref|derived|free}. 'Prose and graph agree' is no longer 'the id appears somewhere' — for quote_literal attrs the exact value must be a verbatim substring of the anchored span; for refs it is agreement-by-typed-resolution. This directly retires the critique's softest spot (point 1). 2) design_features is now list<{feature, grounding: ref}> with node_ref(Method,Evidence) binding — features-must-cite-evidence — so claim_type gating cannot be a rubber stamp (point 2). 3) Every edge carries a COMPUTED fingerprint = sha256(canonicalize(type,from,to,attrs)); entailment_verdicts reference edge_fingerprint and load as STALE on mismatch, closing the stale-verdict hole (point 3). 4) edges.yaml and entailment_verdicts.yaml now pin schema_version + rubric_version + judge_protocol_version so deterministic results stay reproducible as taxonomies evolve (point 4). 5) Added quantity_interface.md importing the exact ledger fields and the reconciliation predicate ledger_ref runs — the central numeric check is now specified, not promissory (point 5). 6) Added coverage_obligations COV1-COV3 (every Claim needs inbound tests/supports; every declared-measured/load-bearing Quantity needs an inbound edge; every load-bearing prose number resolves to a Quantity node) making selective omission a first-class coverage_gap failure (point 6).

  _Adopted from competitor:_ Adopted: (a) declared_by{author-stated|derived|compiler-inferred} to separate WHO asserts an edge from WHETHER it holds — provenance-first. (b) COMPUTED structural_status enum authored only by the checker. (c) rubric_version / schema_version pinning per instance for reproducibility over rubric evolution. (d) The `relates` [*->*] fallback type with a single required note, scored as honest lower-specificity rather than rejected — protects honest-absence symmetry. (e) Addressable not_applicable targets (Absence nodes / dataset:not_applicable) so absence is pointed-at, not omitted. (f) Append-only verdict log keyed to edges. I did NOT adopt the competitor's 'prose renders FROM edges' inversion — see why-this-beats.

  _Why it wins:_ The competitor sidesteps the hardest problem: by making prose a pure render of edges.yaml, prose can never disagree with the graph — which means the prose<->graph cross-check provides ZERO fabrication signal. TCG keeps prose as the human-authored surface and defines agreement as a per-attribute deterministic predicate, so 'the graph matches the prose' is a real, gameable-resistant anti-fabrication check (a fabricated edge attr that isn't literally in the source quote fails). On design_features, the competitor's rubric checks that a feature string is present but does not require it to resolve to a real Method/Evidence node — the exact rubber-stamp the reviewer flagged; TCG's node_ref grounding closes it. On staleness, the competitor's verdict_ref points at an edge id but not its content; TCG's fingerprint detects the mutate-after-approval attack the competitor is open to. On the numeric check, the competitor names 'reconciliation against the quantity ledger' but leaves the contract in another design; TCG imports the interface and writes the reconciliation predicate. Both designs share the clean Class-A/Class-C file split and the ecosystem-schema-vs-instance altitude; TCG wins by making the three things the reviewer called promissory (agreement, grounding, staleness) into specified, deterministic mechanisms.


---


## GENRE — Genre / paper-type manifest

_Class A — format-recoverable determinism_


**Judge rationale:** The gap is class A, which is scored primarily on DETERMINISM plus the anti-Goodhart/anti-fabrication constraints. The decisive discriminator across the four is WHERE the expectation set lives. Proposals #0 and #1 (both gpt-5.5-codex, near-duplicates) keep a versioned ruleset but let the GENRE itself be self-declared or compiler-inferred with no independent adjudication — so the primary gaming surface (declare the genre with the smallest expected set) stays wide open, and their per-ARA ExpectationLedger still requires the compiler to assign expectations paper-by-paper. #1 earns a small edge for its explicit red_flags (fabricated_code_pressure) and anti_fabrication_note; #0 for hash-pinned rulesets with priority-based conflict resolution — but neither closes genre-shopping, which is the load-bearing hole. Proposals #2 and #3 both make the correct move: the expectation table is a SHARED, versioned, ecosystem-level artifact that no compiler can edit to shrink its own expected set, turning not_applicable into a deterministic, recomputable join. That is what class A demands. #2 wins first place because it alone gives genre-shopping a structural consequence (blind classifier + stricter-wins) and makes silent omission a hard structural failure. #3 is a very close second: the cleanest state machine (exactly one bad bucket), a fail-safe default (unlisted pairs default to expected), and the most honest fabrication-surface argument (it reuses the existing anchor discipline rather than inventing a new one) — but it only FLAGS genre disagreement (`contested` bool with no scoring consequence) and leaves an unbounded anchor-free escape hatch (reason_class=structural_taxonomy_gap). Both winners still ultimately rest determinism on an LLM genre classifier, so neither is fully deterministic at the root; #2 mitigates this more but introduces a stricter-wins penalty that can itself create fabrication pressure. #0/#1 are competent but a tier below because they never leave the per-ARA discretion model for the genre assignment.


### Finalist A (refined)

> _Judge critique it answered:_ PROPOSAL #2 — The Genre Manifest (sonnet). This is the strongest design because it makes the one correct class-A move: the expectation_table is an ecosystem-level, shared, versioned matrix[paper_type × slot], NOT per-ARA editable, so `not_applicable` becomes a deterministic join instead of a self-serving excuse. It is also the ONLY proposal that seriously attacks genre-shopping (blind classifier + stricter-wins) and the only one that makes silent omission a hard Level-1 build failure. Those are real, load-bearing contributions. Now the holes you must close:

1. "Stricter of the two genres wins" is an UNDEFINED operation and it is doing the heaviest lifting in your anti-gaming story. Genres do not form a total order; their expected-slot sets are not nested. systematic_review expects {registration, artifacts}; ml_empirical expects {execution, configs, data, heuristics} — neither is "stricter." Define it precisely as a lattice. If you resolve by union-of-expected-slots (max expectations), you now mark a slot `expected` that BOTH candidate genres consider not_applicable — manufacturing an absence penalty for an artifact that genuinely cannot exist. That is textbook fabrication pressure, and it directly violates your own mandate. You must specify the partial order and PROVE the resolver never expects a slot both candidate genres mark not_applicable.

2. The blind classifier is a new nondeterministic LLM, and the abstract/title/venue it reads are AUTHOR-WRITTEN. Genre-shopping does not vanish; it migrates upstream to abstract phrasing. You pin genre_taxonomy_version but NOT the classifier model id, prompt hash, temperature, or the confidence threshold that triggers dispute. For class A, the classifier must be versioned and pinned exactly like the table, and paper_type_blind_confidence's decision threshold and tie-break must be data, not prose. As written, two runs can disagree and your determinism claim collapses at exactly the point it matters.

3. context_dependent cells are an unresolved discretion sink — the exact thing this class exists to eliminate. Your own example leaves src.prompts and theory/src.execution as context_dependent, punting resolution to secondary_axes "documented rules via override" that the truncation conveniently hides. Every context_dependent cell degrades the join back to a judgment call. Walk ONE context_dependent cell end-to-end and show its resolution bottoms out in a checkable anchor (accession pattern, registry lookup, verbatim quote), not an LLM read.

4. The "exhaustive, every cell filled, no blanks" matrix is a governance liability you wave past. Adding one slot forces re-adjudicating a full column across every paper_type, and a v1→v2 edit can silently flip N/A→expected for a whole corpus. Specify migration semantics: do ARAs pinned to v1 stay valid, and how is the version diff audited so evolution never retroactively creates absence penalties?

5. verification_status:unresolved + provisional_slots_count is an open scoring loophole. It implies an out-of-band audit resolver whose determinism, owner, and effect on coverage_score are unspecified — so "park this absence as a tooling limitation" can sit forever. Bound it: require a resolvable anchor at declaration time, a TTL, and a defined penalty if never resolved, or provisional_slots becomes the new silent-absence.

**The Genre Contract v2 — a taxonomy-derived expectation ledger with a pinned classifier, stricter-set scoring, and checkable predicates**  ·  _source: claude-opus-4-8 (finalist B)_

Genre becomes a first-class, versioned classification that DERIVES a deterministic per-artifact expectation set from shared ecosystem tables — but the classification's ROOT is no longer freely chosen. Every ARA carries both a self-declared paper_type and a paper_type produced by a PINNED, checklist-blind classifier (fixed model id + prompt hash + temp 0, inputs restricted to title/abstract/venue). When they disagree, scoring is computed against the UNION of both genres' expected sets (the strictly larger, more demanding set), so declaring the narrowest genre can never shrink what you are held to — genre-shopping yields exactly zero benefit. Every conditional expectation (expected_if_<fact_id>) resolves through a shared predicate_registry that defines each condition as a deterministic rule over anchored quotes (regex / accession pattern / repo-URL match / ledger field), with ambiguity always resolving toward `expected`. Absence becomes a small deterministic state machine over (resolved-expectation × declared-status × filesystem-present × anchor-valid) with clearly separated good, neutral-audited, pending, and bad buckets — closing the gap because absence is read against a public rule table any agent can recompute, and the only two escape hatches left (override anchors, taxonomy-gap claims) are either verbatim-quote-checked or hard-capped and routed through a reviewer gate that grants no credit until resolved.

- **taxonomy/paper_types.vX.yaml** (YAML, community-governed, semver-versioned) — Shared, versioned, closed enum of paper types — one per ecosystem, not per-ARA. Pinning a version per ARA means old ARAs never silently reclassify when the taxonomy evolves.
  - fields: version: string — required || types: list[{ id: snake_case key — required; label: string — required; description: string — required; typical_evidence_language: list[string] — optional, phrases used only as classifier hints, never as a requirement }] || other_policy: { requires_rationale: bool, corpus_health_tracked: bool } — governs the single escape-hatch type
  - example: version: "1.0"
types:
  - id: meta_analysis
    label: "Meta-analysis / evidence synthesis"
    description: "Pools/ranks results across prior independent studies; no new primary data collected."
    typical_evidence_language: ["systematic review", "network meta-analysis", "PRISMA"]
  - id: ml_empirical
    label: "ML empirical study"
    typical_evidence_language: ["we train", "benchmark", "ablation"]
  - id: algorithm_theory
    label: "Algorithm / theory paper"
    typical_evidence_language: ["we prove", "theorem", "complexity"]
  - id: rct
    label: "Randomized controlled trial"
  - id: wet_lab_experimental
    label: "Wet-lab / bench experimental"
  - id: tool_or_software_release
    label: "Tool / software / library release"
  - id: benchmark_or_dataset_release
    label: "Benchmark or dataset release"
  - id: other_with_declared_rationale
    label: "Other (escape hatch)"
    description: "Used only when no listed type fits; REQUIRES rationale; tracked corpus-wide as a taxonomy-health signal."
- **taxonomy/expectation_defaults.vX.yaml** (YAML, versioned, paired 1:1 with a paper_types.vX) — Shared, versioned lookup: for each (paper_type × slot), the DEFAULT expectation. Makes expectation-setting non-fabricable — the compiler reads a public table, it does not invent 'expected'. Only listed exceptions matter; any unlisted (type, slot) defaults to `expected` (fail-safe). Conditional defaults reference a fact_id defined in the predicate_registry — the string is a KEY into a checkable rule, never free prose.
  - fields: taxonomy_version: string — required || defaults_version: string — required || slots: list[slot_id] — required, the fixed artifact-slot vocabulary || defaults: map[paper_type_id -> map[slot_id -> status]] where status ∈ { not_applicable | expected_if:<fact_id> } (absence of an entry ⇒ `expected`) — note `expected` is never written, it is the global default so authors cannot quietly demote via omission
  - example: taxonomy_version: "paper_types.v1"
defaults_version: "expectation_defaults.v1"
slots: [PAPER.md, logic.claims, logic.problem, logic.experiments, logic.solution.heuristics, logic.solution.formalization_or_proofs, evidence.tables_figures, evidence.proofs, src.environment, src.artifacts_or_execution, src.configs, data.dataset, data.preprocessing, sidecar.quantities_ledger, sidecar.refs_table, sidecar.registration_accession]
defaults:
  meta_analysis:
    logic.solution.heuristics: not_applicable
    logic.solution.formalization_or_proofs: not_applicable
    evidence.proofs: not_applicable
    src.configs: not_applicable
    src.artifacts_or_execution: expected_if:repo_released
    data.dataset: expected_if:dataset_released
    sidecar.registration_accession: expected
  algorithm_theory:
    logic.solution.formalization_or_proofs: expected   # written only where it overrides nothing-but-clarity; still resolves to expected
    data.dataset: not_applicable
    src.artifacts_or_execution: expected_if:repo_released
  ml_empirical:
    logic.solution.formalization_or_proofs: not_applicable
    evidence.proofs: not_applicable
- **taxonomy/predicate_registry.vX.yaml** (YAML, versioned with the defaults table) — FIX for critique #3. Defines every conditional fact_id used in expected_if:<fact_id> as a DETERMINISTIC predicate over anchored content in other ARA layers — evaluated by the compiler's predicate engine and re-runnable by any agent. Removes the LLM-guess: 'does the condition hold' is a regex / pattern / structured-field test over a verbatim anchor, not a reading of intent. Every predicate declares its ambiguity resolution, and every ambiguity resolves to the STRICTER side (`expected`).
  - fields: version: string — required || predicates: list[{ id: string — required; reads: stable-layer-reference (e.g. src.environment#Code-availability, sidecar.refs_table) — required; kind: enum{regex_over_quote, accession_pattern, repo_url_present, registry_lookup, ledger_field_set} — required; rule: string (the concrete pattern/expression) — required; evaluates_to_expected_when: string — required; ambiguity_resolution: enum{resolve_expected} — required (fixed by policy: ambiguity/missing-anchor ⇒ expected); evaluator: 'deterministic-predicate-engine' — required }]
  - example: version: "1.0"
predicates:
  - id: repo_released
    reads: src.environment#code-availability
    kind: repo_url_present
    rule: "anchored quote matches /(github|gitlab|zenodo|osf|dryad)\\.[a-z]/i AND a resolvable URL/DOI token is present"
    evaluates_to_expected_when: "a repo/DOI token is present and the paper's own text asserts release"
    ambiguity_resolution: resolve_expected
    evaluator: deterministic-predicate-engine
  - id: dataset_released
    reads: sidecar.refs_table
    kind: accession_pattern
    rule: "a refs_table row carries type=dataset AND an accession/DOI matching a known registry pattern (e.g. /^10\\./, /GSE\\d+/, /PRJNA\\d+/)"
    evaluates_to_expected_when: "an accessioned, fetchable dataset is referenced"
    ambiguity_resolution: resolve_expected
    evaluator: deterministic-predicate-engine
  - id: registration_field_norm_applies
    reads: logic.genre#perspective_tags
    kind: ledger_field_set
    rule: "perspective_tags ∩ {clinical, human_subjects} != empty"
    evaluates_to_expected_when: "the ARA self-tags a field where preregistration is the community norm"
    ambiguity_resolution: resolve_expected
    evaluator: deterministic-predicate-engine
- **taxonomy/classifier_registry.vX.yaml** (YAML, versioned; the prompt body is stored verbatim beside it and hashed) — FIX for critique #6. Pins the checklist-blind genre classifier so paper_type_blind is REPRODUCIBLE, not an unversioned guess. Records exact model id, prompt hash, decoding params, and the restricted input contract (title/abstract/venue only — never the expectation checklist, so it cannot be reverse-engineered to agree). This is the backstop that makes stricter-set scoring meaningful.
  - fields: version: string — required || model_id: string (exact, e.g. claude-opus-4-8) — required || prompt_sha256: string — required || decoding: { temperature: 0, top_p: 1, seed: int } — required || ensemble: { n: int, aggregation: enum{majority, min_strictness} } — required (min_strictness = when members disagree, take the stricter genre) || input_contract: list[enum{title, abstract, venue_article_type}] — required, exhaustive allow-list || output_contract: { paper_type: enum, confidence: float, abstain: bool }
  - example: version: "1.0"
model_id: "claude-opus-4-8"
prompt_sha256: "9f2c…a1"
decoding: { temperature: 0, top_p: 1, seed: 7 }
ensemble: { n: 3, aggregation: min_strictness }
input_contract: [title, abstract, venue_article_type]
output_contract: { paper_type: enum, confidence: float, abstain: bool }
- **logic/genre.yaml (per-ARA manifest)** (YAML sidecar at logic/genre.yaml; a one-line gloss mirrors into PAPER.md frontmatter (paper_type replaces free-text domain as the machine-branchable field)) — The per-ARA declaration and computed ledger. Selects paper_type with a REQUIRED anchor (even when inferred — FIX #5), records the pinned blind classification, computes the effective (stricter) scoring genre, records anchored overrides (FIX #2 caps + gates the taxonomy-gap class), and publishes the exhaustive resolved-slot table with an explicit present_but_not_applicable bucket (FIX #4). Every slot in the taxonomy MUST appear (Seal Level-1 requirement, stolen from competitor) or the ARA fails structural validation.
  - fields: schema_version: string — required || taxonomy_version / defaults_version / predicate_registry_version / classifier_registry_version: string — required, pin all shared tables || paper_type_declared: enum — required || paper_type_source: enum{stated, inferred} — required || paper_type_evidence: {quote, file, locator} — REQUIRED in BOTH cases; if source=inferred and no anchor is resolvable, validator sets contested=true by construction (FIX #5) || paper_type_blind: enum — required, from pinned classifier || paper_type_blind_confidence: float — required || contested: bool — required, computed = (declared != blind) OR (inferred without anchor) || effective_expected_set: list[slot] — required, computed = expected_set(declared) ∪ expected_set(blind) when contested else expected_set(declared) (FIX #1/#6: stricter-by-construction) || perspective_tags: list[enum] — optional orthogonal modifiers (read by predicates) || overrides: list[{ slot, status: not_applicable|expected_but_absent, reason: string, reason_class: enum{source_stated, external_constraint, structural_taxonomy_gap}, reason_anchor: {file, locator, quote} — REQUIRED for source_stated & external_constraint; for structural_taxonomy_gap either an anchor OR routed=true to the reviewer gate (FIX #2) }] || taxonomy_gap_count: int — computed, MUST be <= cap (e.g. 2) else validation fails (FIX #2) || resolved_slots: list[{ slot, canonical_expectation(resolved), declared_status, filesystem_present: bool, anchor_valid: bool, bucket: enum{present_as_expected | honest_not_applicable | honest_expected_but_absent | present_but_not_applicable | pending_taxonomy_gap | lazy_omission | structural_contradiction} }] — required, COMPUTED not hand-typed
  - example: schema_version: "1.0"
taxonomy_version: "paper_types.v1"
defaults_version: "expectation_defaults.v1"
predicate_registry_version: "1.0"
classifier_registry_version: "1.0"
paper_type_declared: meta_analysis
paper_type_source: stated
paper_type_evidence:
  quote: "a systematic review and network meta-analysis (NMA) … PRISMA-DTA"
  file: PAPER.md
  locator: "Title; §2 Methods"
paper_type_blind: meta_analysis
paper_type_blind_confidence: 0.94
contested: false
effective_expected_set: [PAPER.md, logic.claims, logic.problem, sidecar.quantities_ledger, sidecar.refs_table, sidecar.registration_accession]
perspective_tags: [secondary_data_synthesis]
overrides:
  - slot: data.dataset
    status: expected_but_absent
    reason: "§2.4 states the extraction spreadsheet is 'available from corresponding author on request'; never deposited or fetchable at compile time."
    reason_class: source_stated
    reason_anchor: {file: PAPER.md, locator: "§2.4 Data", quote: "available from the corresponding author on reasonable request"}
taxonomy_gap_count: 0
resolved_slots:
  - {slot: sidecar.registration_accession, canonical_expectation: expected, declared_status: present, filesystem_present: true, anchor_valid: true, bucket: present_as_expected}
  - {slot: src.artifacts_or_execution, canonical_expectation: not_applicable, declared_status: not_applicable, filesystem_present: false, anchor_valid: true, bucket: honest_not_applicable}  # predicate repo_released evaluated false
  - {slot: data.dataset, canonical_expectation: expected, declared_status: expected_but_absent, filesystem_present: false, anchor_valid: true, bucket: honest_expected_but_absent}
  - {slot: evidence.proofs, canonical_expectation: not_applicable, declared_status: present, filesystem_present: true, anchor_valid: false, bucket: present_but_not_applicable}  # dumped, earns no coverage credit, feeds padding ratio

# --- Contrast: a gamed ARA the state machine catches ---
# declared: theory paper (small expected set) but blind: ml_empirical (large set)
# contested: true -> effective_expected_set = UNION -> data.dataset/src.configs become expected
# any of those left absent with no anchor -> bucket: lazy_omission -> scored against author

  _Protocols:_
  - **Deterministic expectation resolution (state-machine build)** — Every compile of every ARA.. 1) Read pinned taxonomy_version + defaults_version + predicate_registry_version. 2) For declared and blind genre, build expected_set by table lookup; resolve each expected_if:<fact_id> by running the predicate engine over the referenced anchored layer content. 3) effective_expected_set = expected_set(declared) if not contested, else union of both. 4) For each slot, join (resolved expectation × declared_status × filesystem_present × anchor_valid) → exactly one bucket via the fixed truth table. 5) Emit resolved_slots. No compiler discretion at any step; another agent with the same inputs recomputes byte-identical buckets.
    - reliability/reproducibility: Class A — deterministic. The only non-table input is anchor_valid (verbatim-quote match) and predicate evaluation, both mechanical.
    - constraints: Ecosystem must publish the three versioned tables in a single spec repo, immutably addressed by version. Predicate engine must be a shared, open, reference implementation so 'who evaluates' is answered identically everywhere.
  - **Pinned checklist-blind classification + stricter-set resolution** — Every ARA, to fix the freely-chosen root (critique #1/#6).. 1) Run classifier from classifier_registry.vX with ONLY {title, abstract, venue_article_type}; the expectation checklist is never in context. 2) Ensemble n runs, aggregate by min_strictness. 3) Set contested = (declared != blind) OR (source=inferred with no resolvable anchor). 4) If contested, scoring uses the UNION expected set — always the more demanding one. 5) An OPTIONAL reviewer gate may later collapse contested to a single correct genre, which can only RELAX the set, never tighten it (prevents retaliatory over-penalty and prevents any incentive to trigger disputes).
    - reliability/reproducibility: Class C→reproducible. Pinned model id + prompt hash + temp 0 + seed makes blind output reproducible run-to-run; ensemble + min_strictness bounds residual variance toward the safe (stricter) side. The consequence (union scoring) is fully deterministic given the two genres.
    - constraints: Ecosystem must host the pinned classifier (or publish weights/prompt so it is reproducible), a calibration set of hand-labeled genre exemplars per taxonomy version, and a re-pinning protocol when the taxonomy adds a type.
  - **Taxonomy-gap override governance (bounded escape hatch)** — When an author claims a canonical `expected` slot is not_applicable because the taxonomy itself is wrong for their case (critique #2).. 1) A structural_taxonomy_gap override with a valid anchor is treated like any other anchored override. 2) WITHOUT an anchor it must set routed=true; the slot's bucket becomes pending_taxonomy_gap — it earns NO honest-N/A credit and is excluded from the coverage numerator until resolved. 3) Each routed gap emits a corpus-health record (candidate new (type,slot) rule) to taxonomy governance. 4) Hard cap: taxonomy_gap_count <= N (default 2); exceeding it fails structural validation. 5) A human/agent reviewer gate periodically adjudicates: accepted gaps become new table rows in the next taxonomy version (crediting the ARA retroactively); rejected gaps flip the slot to lazy_omission.
    - reliability/reproducibility: Class B — reliability via the reviewer gate + corpus-health tracker. Failure mode (mass false gap claims) is bounded by the cap and by zero-credit-until-resolved. Dedup: identical (type,slot) gap claims across ARAs cluster into one governance ticket.
    - constraints: Ecosystem must run the corpus-health tracker, a reviewer queue with SLA, and a taxonomy governance process that versions accepted changes.
  - **Padding / unexpected-presence audit** — Whenever an artifact is present in a slot the effective genre marks not_applicable (critique #4).. 1) Such slots resolve to bucket present_but_not_applicable. 2) They are EXCLUDED from the coverage numerator (cannot inflate completeness). 3) padding_ratio = |present_but_not_applicable| / max(1, |effective_expected_set|). 4) Above a threshold, a thinness/padding metric flags the ARA for review; the flagged content is still checked for genuine cross-genre relevance (a wet-lab paper that also ships code is legitimately dual — resolved by adding a perspective_tag or a secondary genre, not by dumping).
    - reliability/reproducibility: Class A for the ratio (deterministic); Class C for the 'genuine vs padding' judgement, handled by the existing rigor reviewer with for/against.
    - constraints: Threshold and the dual-genre path must live in the shared spec so it is not per-ARA tunable.

  _Metrics afforded:_
  - Expectation coverage completeness → |present_as_expected| / |effective_expected_set|, where effective_expected_set is the union (stricter) set when contested. [deterministic]; anti-Goodhart: Denominator is derived from the STRICTER of declared/blind genres, so shrinking your genre cannot shrink your denominator; present_but_not_applicable is excluded from the numerator, so dumping artifacts cannot inflate it.
  - Lazy-omission count → Count of slots in bucket lazy_omission (expected + absent + no valid anchor). [deterministic]; anti-Goodhart: The only way out of lazy_omission is a verbatim-quote anchor (same discipline as every typed fact) or an honest present artifact — fabricating an anchor fails the mechanical quote-match; you cannot demote an expected slot by editing the shared table.
  - Honest-absence integrity → |honest_expected_but_absent with resolvable anchor| / |all expected-but-absent|; anchors must resolve to a real quote at a real locator. [reliable-anchored]; anti-Goodhart: Prose quality earns nothing; only a source anchor that resolves earns the honest-absence (equal-footing) score. Broken/fabricated anchors drop the slot to lazy_omission.
  - Genre honesty (contested rate + effective vs declared delta) → Boolean contested plus |effective_expected_set \ expected_set(declared)| (how much stricter reality was than the author's pick). [reproducible]; anti-Goodhart: Blind classifier is pinned (model+prompt hash+temp0) and cannot see the checklist; a large delta means the author picked a lenient genre and got scored on the strict one anyway — so the exploit is not merely flagged, it is neutralized before scoring.
  - Padding ratio → |present_but_not_applicable| / max(1, |effective_expected_set|). [deterministic]; anti-Goodhart: Stuffing an ARA with artifacts a genre marks N/A raises this ratio (a penalty signal) while adding zero coverage credit — padding costs, never pays. Legitimate cross-genre work is routed to a perspective_tag/secondary genre instead.
  - Taxonomy-gap load → Count of pending_taxonomy_gap buckets (capped at N); plus the corpus-wide frequency of each claimed (type,slot) gap. [reliable-anchored]; anti-Goodhart: Unanchored gap claims earn no credit until a reviewer accepts them, are hard-capped per ARA, and are deduplicated corpus-wide — turning the former unbounded escape hatch into a bounded, audited governance input.

  _Tradeoffs:_ Honest costs and residual fabrication surfaces: (1) The pinned blind classifier is the new Class-C dependency — its reproducibility rests on the ecosystem actually hosting/pinning the model; if the model is deprecated, old ARAs need re-pinning, which the version field supports but which is real maintenance. Mitigation: ensemble + min_strictness bounds variance toward the safe side, and a calibration set catches drift. (2) Union scoring when contested can over-demand for genuinely novel hybrids where the blind classifier is simply wrong. Mitigation: the reviewer gate can collapse contested to one genre, but only in the RELAXING direction, so a wrong-and-strict blind guess is recoverable while a lenient-author guess is not — the asymmetry is deliberate. (3) The remaining fabrication surface is exactly the override anchor (a verbatim quote) — identical to the surface every other typed fact already uses; we add no new one, and we explicitly CLOSED the two that the critique found (unanchored taxonomy-gap claims, optional inferred-genre anchors). (4) Predicate registry adds ecosystem complexity: every conditional expectation now needs a maintained checkable rule, and a badly-written regex could mis-resolve; mitigation is that ambiguity always resolves to `expected` (stricter), so a buggy predicate over-demands rather than lets absence slip. (5) Cap on taxonomy_gap_count could, in principle, block a legitimately unusual paper needing 3 gaps; mitigation is that anchored gaps do not count against the cap — only unanchored routed ones do.

  _Open questions:_ 1) 'Stricter = union of expected sets' is deterministic but can double-count when two genres expect overlapping-but-differently-named slots; a canonical slot-equivalence map may be needed and is not yet specified. 2) The blind classifier's calibration set must itself be governed — who curates genre exemplars, and how disagreement on the GROUND TRUTH label is resolved, is an unsolved meta-governance problem. 3) Secondary/hybrid genres (a tool release that is also an empirical study) are handled via perspective_tags + a relaxing reviewer path, but a fully deterministic multi-genre expectation join (rather than single-primary + tags) is left open. 4) The padding threshold is a single global constant; whether it should vary by field is unresolved. 5) Re-pinning old ARAs when a model is retired preserves the recorded output but not the ability to re-run the classifier from scratch — long-term reproducibility of Class-C blind calls across model generations remains genuinely hard.

  _Changes from critique:_ Directly addressed all six critique points. (1) Genre-shopping CLOSED: contested now has a hard scoring consequence — effective_expected_set becomes the UNION of declared and blind genres' expected sets, so the author is always scored against the stricter set; picking the narrowest genre yields zero benefit. (2) structural_taxonomy_gap is no longer an unbounded anchor-free hatch: it requires an anchor OR routed=true to a reviewer gate; unanchored gaps get bucket pending_taxonomy_gap that earns NO credit until resolved, emit a corpus-health record, are deduplicated corpus-wide, and are hard-capped (taxonomy_gap_count <= N or validation fails). (3) expected_if_<fact_id> no longer leaks into prose-reading: a new predicate_registry.vX.yaml defines each fact_id as a deterministic rule (regex_over_quote / accession_pattern / repo_url_present / registry_lookup / ledger_field_set) over an anchored layer reference, names the evaluator (shared predicate engine), and fixes ambiguity resolution to always resolve toward `expected`. (4) Unexpected presence now has an explicit bucket present_but_not_applicable: excluded from the coverage numerator (can't inflate thoroughness) and fed into a deterministic padding_ratio (can penalize) — closing the stuff-to-look-thorough hole. (5) paper_type_evidence anchor is now REQUIRED even when source=inferred; inferred-without-anchor sets contested=true by construction, routing it through stricter-set scoring. (6) Classifier PINNED via classifier_registry.vX.yaml (model id + prompt sha256 + temp 0 + seed + restricted input contract + ensemble/min_strictness), making paper_type_blind reproducible, and paired with the real stricter-wins consequence from fix #1.

  _Adopted from competitor:_ Adopted four of the competitor's strongest moves: (a) the independent checklist-BLIND classifier whose inputs are restricted to title/abstract/venue so it cannot be reverse-engineered to agree; (b) stricter-genre-wins as the resolution consequence (I hardened it into deterministic UNION scoring rather than a soft 'stricter of two'); (c) the exhaustive per-slot checklist as a Seal Level-1 HARD structural-validation requirement — every taxonomy slot must appear with a status or the ARA fails to build, turning silent omission into a build failure; (d) the explicit present_unexpected bucket, which I renamed present_but_not_applicable and gave concrete scoring (zero coverage credit + padding-ratio penalty). Also borrowed the secondary_axes / orthogonal-modifier idea, implemented as perspective_tags that predicates can read.

  _Why it wins:_ Both designs converge on blind-classifier + stricter-wins + exhaustive checklist, so the differentiator is DETERMINISM DEPTH and closed escape hatches. The competitor leaves 'context_dependent' cells in its expectation_table — an unresolved third value that pushes exactly the LLM-guess this class must eliminate back into scoring; I replace it with expected_if:<fact_id> bound to a shared predicate_registry that resolves every conditional mechanically over anchored quotes, with a fixed stricter-side ambiguity rule. The competitor's blind classifier is described as 'independent' but is UNPINNED (no model id/prompt hash/decoding), so its own output is not reproducible — I pin it in a versioned classifier_registry, which is what makes stricter-set scoring trustworthy rather than another moving part. My scoring consequence is the deterministic UNION of expected sets (no argmax tie-break ambiguity), and I add the asymmetric reviewer path (contested can only relax) that removes any incentive to trigger disputes. Finally I keep the cleanest part of my own design — split 'what should exist' (zero-discretion table lookup) from 'what the compiler declares' (anchored override) — and I explicitly close the two holes the reviewer found in BOTH proposals (unanchored taxonomy-gap claims, unhandled unexpected presence), so the anti-gaming half of the mandate is delivered structurally, not just recorded.


### Finalist B (refined)

> _Judge critique it answered:_ PROPOSAL #3 — The Genre Contract (claude-sonnet-5). Cleanest execution of the class-A idea: split "what should exist" (computed with zero compiler discretion from two shared versioned tables) from "what the compiler declares" (an override gated by the SAME verbatim-quote anchor discipline every typed fact already uses). The one-bad-bucket state machine (expected + absent + no valid anchor = lazy_omission) is crisp and directly scorable, the unlisted-pair-defaults-to-`expected` rule is a genuine fail-safe, and your "creates no new fabrication surface, reuses the existing one" is the most honest tradeoff statement of the four. But you under-deliver on the anti-gaming half of the mandate, and that is the half that matters most:

1. Genre-shopping is essentially OPEN. `contested: bool` from a multi-pass audit is declared but carries NO scoring consequence anywhere in the spec. Flagging is not closing. #2 forces the stricter genre to score; you merely record that a disagreement happened. An author still picks the genre with the smallest expected set and eats a harmless boolean. State exactly what contested=true DOES — which genre scores, or does the ARA fail validation — or your whole determinism edifice sits on a freely-chosen root.

2. reason_class=structural_taxonomy_gap requires NO anchor. That is an unbounded, unfalsifiable escape hatch you left open while claiming zero new fabrication surface — the claim is false as written. Any inconvenient `expected` slot can be flipped to not_applicable citing "taxonomy gap" with nothing to check. Require an anchor OR route every structural_taxonomy_gap through the corpus-health tracker AND a reviewer gate, and cap how many a single ARA may claim before it fails.

3. expected_if_<fact_id> pushes determinism into fact-detection, which is where it leaks. "expected_if_repo_stated_released" and "expected_if_field_norm_applies" require reading prose to decide whether the condition holds — exactly the LLM guess this class must eliminate. The join is only as deterministic as the predicate resolving the condition. Specify each fact_id as a checkable rule over anchored quotes (regex, accession/registry pattern, repo-URL match), name who evaluates it, and define tie/ambiguity resolution.

4. Unexpected presence is unhandled. Your buckets cover present-as-expected, honest N/A, honest expected-but-absent, lazy_omission, structural_contradiction — but NOT present-but-canonically-not_applicable. Does dumping artifacts a genre marks N/A earn credit, cost nothing, or flag padding? Silent tolerance is a live Goodhart hole: stuff the ARA to look thorough. Add an explicit bucket and its scoring.

5. paper_type_source:inferred with evidence "optional-but-recommended" is an auditability hole: an inferred genre with no anchor is an unfalsifiable classification driving the entire expectation table. Make the anchor required even when inferred, or mark inferred-without-anchor as contested by construction.

6. Same unpinned-classifier determinism leak as #2 — the multi-pass audit's "disagreed above threshold" and the classifier model/prompt are unversioned — but WITHOUT even a stricter-wins backstop to catch the miss. Pin the classifier and give contested a real consequence and you leapfrog #2.

**The Genre Manifest v2 — Fabrication-Safe Expectation Join**  ·  _source: sonnet (Proposal #2, "The Genre Manifest")_

Every ARA declares one controlled paper_type from a shared, versioned taxonomy, and every genre-conditioned artifact slot resolves to a bucket — present / honest_not_applicable / honest_expected_but_absent / lazy_omission / structural_contradiction / contested — by a deterministic join against a public expectation table, never invented per paper. The four load-bearing fixes: (1) genre disambiguation is resolved PER-SLOT by a lattice MEET over exactly the two candidate genres {declared, blind}, which is proven to never mark a slot `expected` that either candidate marks not_applicable — so disagreement can never manufacture an absence penalty, killing the old undefined "stricter-wins"; (2) the blind classifier is a fully pinned artifact (ensemble model ids, prompt hashes, temperature 0, thresholds, tie-break) plus a non-LLM structural corroborator reading hard anchors, so the classification decision is class-A deterministic even though the label is class-C reproducible, and abstract-gaming must now also forge checkable anchors; (3) every `context_dependent` cell is replaced by `expected_if(predicate)` where the predicate bottoms out in an accession regex, entity-ledger lookup, or verbatim-quote match — zero LLM discretion; (4) absence credit is TTL-bounded: a provisional/absent slot must carry a resolvable anchor at declaration time and auto-converts to lazy_omission if unresolved past its TTL, so "park this forever" is impossible. Silent omission of any slot remains a hard Level-1 build failure. This turns "penalize thinness not absence" into a deterministic join for the common case and a bounded, anchored, expiring resolver call for the rest — with no new fabrication surface.

- **genre_taxonomy.v1.yaml (ecosystem-level, shared, versioned — NOT per-ARA)** (YAML, semver, checked into the shared ara-spec repo next to ara-schema.md; governed by an explicit diff/migration process (see taxonomy_diff and protocols).) — The single canonical spec every ARA is scored against. Defines the controlled paper_type enum, the two-tier slot vocabulary (universal vs conditional), the exhaustive expectation_table over conditional slots with expected_if predicates, the typed non-LLM predicate resolvers, and the fully pinned blind classifier_manifest. Lives outside any ARA so no author or compiler can shrink their own expected set.
  - fields: version: string — required || paper_types: list[enum] — required (closed taxonomy + explicit `other` escape hatch) || universal_slots: list[slot_id] — required, default expectation `expected` for ALL types, never blank || conditional_slots: list[slot_id] — required, MUST be adjudicated per type (no defaulting; taxonomy CI rejects a blank cell) || expectation_table: map[paper_type -> map[conditional_slot -> {expected | not_applicable | expected_if(predicate_id)}]] — required, exhaustive over conditional_slots || predicate_defs: map[predicate_id -> {resolver_type: accession_regex|entity_type_presence|verbatim_quote_regex|sidecar_presence, spec: <resolver-specific>, resolves_to_on_true: expected, resolves_to_on_false: not_applicable}] — required, all non-LLM || classifier_manifest: {ensemble: list[{model_id, prompt_sha256}], temperature: 0, seed: int, input_fields: [title, abstract, venue_article_type], aggregation: majority_vote, tie_break: lowest_alpha_id, dispute_threshold_tau: float, confidence_floor: float, structural_corroborator: {anchors: map[paper_type -> list[accession_regex|structural_signal]]}} — required || provisional_ttl_days: int — required (e.g. 90)
  - example: version: "1.0"
paper_types: [rct_clinical_trial, observational_epidemiological, systematic_review_meta_analysis, wet_lab_experimental, computational_ml_empirical, theory_formal_proof, simulation_modeling, tool_software_release, case_report_series, dataset_release, replication_study, position_review, mixed_methods, other]
universal_slots: [PAPER.md, logic.problem, logic.claims, logic.concepts, logic.related_work, logic.experiments, evidence.tables_figures, sidecar.refs_table, sidecar.quantities_ledger]
conditional_slots: [src.execution, src.configs, src.artifacts, src.prompts, data.dataset, data.preprocessing, logic.solution.heuristics, logic.solution.method_formal, evidence.proofs, sidecar.registration]
expectation_table:
  systematic_review_meta_analysis:
    src.execution: not_applicable
    src.configs: not_applicable
    src.artifacts: expected_if(analysis_code_stated_released)
    src.prompts: not_applicable
    data.dataset: expected_if(extraction_dataset_stated_released)
    data.preprocessing: not_applicable
    logic.solution.heuristics: not_applicable
    logic.solution.method_formal: not_applicable
    evidence.proofs: not_applicable
    sidecar.registration: expected
  computational_ml_empirical:
    src.execution: expected
    src.configs: expected
    src.artifacts: expected
    src.prompts: expected_if(uses_generative_model)
    data.dataset: expected
    data.preprocessing: expected
    logic.solution.heuristics: expected
    logic.solution.method_formal: not_applicable
    evidence.proofs: not_applicable
    sidecar.registration: not_applicable
  theory_formal_proof:
    src.execution: expected_if(uses_generative_model)
    src.configs: not_applicable
    src.artifacts: expected_if(analysis_code_stated_released)
    src.prompts: not_applicable
    data.dataset: not_applicable
    data.preprocessing: not_applicable
    logic.solution.heuristics: not_applicable
    logic.solution.method_formal: expected
    evidence.proofs: expected
    sidecar.registration: not_applicable
predicate_defs:
  uses_generative_model:
    resolver_type: entity_type_presence
    spec: { ledger: sidecar.entities, entity_type_in: [llm, foundation_model, prompted_model] }
    resolves_to_on_true: expected
    resolves_to_on_false: not_applicable
  analysis_code_stated_released:
    resolver_type: verbatim_quote_regex
    spec: { file: src/environment.md, section: "Code Availability", regex: "github\\.com|gitlab|zenodo|osf\\.io|dryad" }
    resolves_to_on_true: expected
    resolves_to_on_false: not_applicable
  extraction_dataset_stated_released:
    resolver_type: sidecar_presence
    spec: { sidecar: data/accession.yaml, field: dataset_doi }
    resolves_to_on_true: expected
    resolves_to_on_false: not_applicable
classifier_manifest:
  ensemble:
    - { model_id: "anthropic/claude-x-2026-01", prompt_sha256: "9f2c...a71" }
    - { model_id: "meta/genre-clf-3b-2025-11",  prompt_sha256: "11be...4dd" }
    - { model_id: "oss/scibert-genre-v4",        prompt_sha256: "c033...9a2" }
  temperature: 0
  seed: 20260101
  input_fields: [title, abstract, venue_article_type]
  aggregation: majority_vote
  tie_break: lowest_alpha_id
  dispute_threshold_tau: 0.15   # top1 must beat top2 label share by >= tau
  confidence_floor: 0.55        # below this, force contested
  structural_corroborator:
    anchors:
      systematic_review_meta_analysis: [ "(PROSPERO|CRD)\\d+", "prisma_flow_present" ]
      rct_clinical_trial:             [ "(NCT|ISRCTN|EudraCT)\\d+" ]
      theory_formal_proof:            [ "proof_block_present", "theorem_env_present" ]
      dataset_release:                [ "dataset_doi_present" ]
provisional_ttl_days: 90

- **genre.yaml (per-ARA manifest, at ARA root; one-line gloss mirrored to PAPER.md frontmatter)** (YAML sidecar; PAPER.md frontmatter gains machine-branchable `paper_type:` (free-text `domain:` remains for human prose).) — The per-paper declaration and the exhaustive, COMPUTED per-slot bucket ledger. Seal Level 1 REQUIRES every universal_slot + conditional_slot from the pinned taxonomy to appear here with a resolved bucket, or structural validation fails — silent omission is a hard build failure. All resolution fields (resolved_expectation, bucket, coverage_score) are computed by the validator, not hand-authored.
  - fields: ara_id: string — required || genre_taxonomy_version: string — required, pins the table+classifier+predicates this ARA was scored against || paper_type_declared: enum — required || paper_type_declared_evidence: list[{anchor, quote}] — required, >=1 || paper_type_blind: enum — required, from pinned classifier_manifest ensemble, no access to this file || paper_type_blind_confidence: float[0,1] — required, computed || paper_type_structural: enum|null — from non-LLM corroborator || genre_agreement: bool — computed (declared==blind AND confidence>=floor AND margin>=tau) || genre_contested: bool — computed (true if not agreement) || contested_until: date|null — TTL for a contested classification || artifact_status: list[SlotStatus] — required, exhaustive; each SlotStatus = {slot, canonical_expectation (raw table value), predicate_resolution (if expected_if, the resolved value + resolver anchor), candidate_meet (resolved expectation used for coverage), declared_status: present|not_applicable|absent_declared, ref|null, override_reason|null, bucket (computed), provisional_until|null, resolvable_anchor|null} || coverage_score: float — computed || warrant_integrity_score: float — computed || provisional_debt: int — computed (unresolved provisional past TTL) || silent_omission_count: int — computed, MUST be 0 for Level-1
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
genre_taxonomy_version: "1.0"

paper_type_declared: systematic_review_meta_analysis
paper_type_declared_evidence:
  - anchor: "PAPER.md Overview"
    quote: "a PRISMA-DTA systematic review and network meta-analysis (NMA)"
  - anchor: "Crossref article-type"
    quote: "article type: Systematic Review"
paper_type_blind: systematic_review_meta_analysis
paper_type_blind_confidence: 0.94
paper_type_structural: systematic_review_meta_analysis   # PROSPERO id + PRISMA flow matched
genre_agreement: true
genre_contested: false
contested_until: null

artifact_status:
  - slot: src.artifacts
    canonical_expectation: expected_if(analysis_code_stated_released)
    predicate_resolution: { value: not_applicable, resolver: verbatim_quote_regex, anchor: "src/environment.md §Code Availability: no repo URL matched" }
    candidate_meet: not_applicable
    declared_status: not_applicable
    bucket: honest_not_applicable
  - slot: sidecar.registration
    canonical_expectation: expected
    candidate_meet: expected
    declared_status: present
    ref: "PROSPERO:CRD420261327845"
    bucket: present_as_expected
  - slot: data.dataset
    canonical_expectation: expected_if(extraction_dataset_stated_released)
    predicate_resolution: { value: expected, resolver: sidecar_presence, anchor: "data/accession.yaml dataset_doi: 10.5061/dryad.xxx" }
    candidate_meet: expected
    declared_status: absent_declared
    override_reason: "Extraction spreadsheet stated deposited on Dryad but embargoed until 2026-09."
    resolvable_anchor: { kind: doi, value: "10.5061/dryad.xxx" }
    provisional_until: "2026-10-04"
    bucket: honest_expected_but_absent
  # ... every remaining universal + conditional slot present with a bucket (none omitted)

coverage_score: 1.0
warrant_integrity_score: 1.0
provisional_debt: 0
silent_omission_count: 0

---
# Contrast: genre-shopping attempt caught by the meet + contested channel
ara_id: xyz-benchmark-paper
paper_type_declared: position_review          # author shops for a lenient genre
paper_type_blind: computational_ml_empirical  # ensemble disagrees
paper_type_blind_confidence: 0.88
genre_agreement: false
genre_contested: true
contested_until: "2026-10-04"
artifact_status:
  - slot: src.execution
    canonical_expectation: not_applicable      # under declared position_review
    candidate_meet: not_applicable             # meet(N/A_declared, expected_blind)=N/A -> NO absence penalty now
    declared_status: not_applicable
    bucket: contested_pending                  # neutral, but TTL-bounded; flips to strict at contested_until
# provisional_debt/seal-tier consequences applied if unresolved past contested_until

- **taxonomy_diff.v1_v2.yaml (ecosystem migration artifact)** (YAML, versioned, in the shared spec repo; generated deterministically by diffing two genre_taxonomy versions, then human-signed.) — Makes taxonomy evolution auditable and PROVES no version bump retroactively creates absence penalties. Ships with every version release; classifies every cell change and defines its re-score semantics.
  - fields: from_version: string — required || to_version: string — required || changes: list[{cell: {paper_type, slot} | {predicate_id} | {paper_type}, change_class: loosen|tighten|new_slot|new_type|new_predicate|predicate_edit, from: value|null, to: value|null, rationale_anchor: string}] — required || rescore_policy: {pinned_aras: "remain valid against pinned version; never re-scored automatically", opt_in_rescore: "loosen-only auto-safe; any tighten requires author re-declaration and can never retroactively bucket a slot as lazy_omission"} || ci_lint: {no_blank_conditional_cells: true, new_slot_requires_full_column: true}
  - example: from_version: "1.0"
to_version: "1.1"
changes:
  - cell: { paper_type: computational_ml_empirical, slot: src.prompts }
    change_class: tighten
    from: expected_if(uses_generative_model)
    to: expected
    rationale_anchor: "RFC-2026-014: prompt logs now expected for all ML empirical work"
  - cell: { slot: data.lineage }
    change_class: new_slot
    from: null
    to: "full column adjudicated for all 14 paper_types (see table v1.1)"
    rationale_anchor: "RFC-2026-019"
rescore_policy:
  pinned_aras: "ARAs pinned to 1.0 remain valid and scored against 1.0 forever"
  opt_in_rescore: "tighten changes never retroactively create lazy_omission; loosen changes may be auto-applied since they only hold-or-improve coverage"
ci_lint:
  no_blank_conditional_cells: true
  new_slot_requires_full_column: true


  _Protocols:_
  - **Blind classification and dispute decision** — Every compile, to produce paper_type_blind and decide genre_agreement vs genre_contested.. 1) Feed ONLY {title, abstract, venue_article_type} to each ensemble model in classifier_manifest at temperature 0 with the pinned seed and prompt_sha256. 2) Aggregate labels by majority_vote; break ties by lowest_alpha_id. 3) Compute paper_type_blind_confidence = top-1 label share; compute margin = share(top1)-share(top2). 4) Run the non-LLM structural_corroborator: match the ARA's hard anchors (registration regex, proof-block presence, dataset DOI) against classifier_manifest.structural_corroborator to get paper_type_structural. 5) genre_agreement = (declared==blind) AND (confidence>=confidence_floor) AND (margin>=dispute_threshold_tau) AND (structural does not contradict declared). Otherwise genre_contested=true and contested_until = today+provisional_ttl_days.
    - reliability/reproducibility: Class C for the LABEL (LLM ensemble), made REPRODUCIBLE by pinning model_id+prompt_sha256+temperature 0+seed in versioned data; re-runs on the same pinned manifest reproduce the label. Class A for the DECISION: given the label, confidence, margin, floor, and tau (all data), agreement/contested is a deterministic boolean. The structural_corroborator is fully deterministic (regex/presence) and provides a non-LLM second opinion so upstream abstract-gaming must also forge checkable anchors.
    - constraints: Ecosystem must host the pinned ensemble weights (or a reproducible API snapshot) and freeze prompt hashes per taxonomy version. Venue article-type metadata must be ingestible (Crossref/DataCite). If a model is deprecated, a new taxonomy version + taxonomy_diff (change_class: predicate_edit on classifier) is required — old ARAs stay pinned.
  - **Per-slot expectation join (meet resolution) + non-fabrication proof** — Every compile, to set candidate_meet (the expectation used for coverage) for every slot.. 1) Resolve each candidate genre's raw cell: if expected_if(P), run the predicate resolver to get expected|not_applicable; else use the literal. 2) Let E_d(s), E_b(s) be the resolved values for declared and blind on slot s over the lattice not_applicable ⊑ expected. 3) candidate_meet(s) = MEET(E_d(s), E_b(s)) = not_applicable unless BOTH equal expected. 4) If E_d(s)!=E_b(s), also mark slot contested_pending and set contested_until. 5) Coverage is computed from candidate_meet; the strict (join) value is stored for the TTL flip.
    - reliability/reproducibility: Class A deterministic. PROOF (no manufactured absence): candidate_meet(s)=expected iff MEET(E_d,E_b)=expected iff E_d(s)=E_b(s)=expected. Contrapositive: if EITHER candidate marks s not_applicable, MEET ⊑ that = not_applicable, so s is never coverage-expected. Hence the resolver NEVER expects a slot that either (a fortiori both) candidate genres consider not_applicable — strictly stronger than the requested both-N/A guarantee. Anti-shopping preserved: any disagreement raises genre_contested (published, seal-tier cap) and, at contested_until, contested slots flip to the STRICT (join) value so a genuine absence becomes lazy_omission — shopping yields only a loud, expiring reprieve.
    - constraints: Requires exactly two candidates {declared, blind}; if more classifiers are added the meet generalizes to n-ary GLB and the proof holds unchanged. Predicate resolvers must be pure functions over sibling layers.
  - **Predicate resolution (expected_if)** — Whenever a table cell is expected_if(predicate_id).. 1) Look up predicate_defs[predicate_id].resolver_type. 2) accession_regex/verbatim_quote_regex: match the pinned regex against the named file/section, return expected on match. 3) entity_type_presence: query the sibling entity ledger for an entity whose type is in the allowed set (e.g. uses_generative_model → any entity.type in {llm, foundation_model, prompted_model}). 4) sidecar_presence: check the named sidecar field is non-empty. 5) Return resolves_to_on_true/false and record the exact anchor (file+locator or entity_id) in predicate_resolution.
    - reliability/reproducibility: Class A deterministic — regex, presence, and typed-ledger lookups only. WALKTHROUGH (ml_empirical / src.prompts): predicate uses_generative_model → entity_type_presence over sidecar.entities → if the ledger contains entity {id: e12, type: llm}, resolves TRUE → src.prompts=expected with anchor entity_id=e12; else not_applicable with anchor 'no llm-type entity in ledger'. The result bottoms out in a checkable entity id, never an LLM read.
    - constraints: Sibling gaps must publish the entity ledger, refs table, and quantity ledger by stable id. Regexes are frozen per taxonomy version. A predicate whose resolver cannot run (missing sidecar) resolves to not_applicable AND raises a structural lint (never silently expected).
  - **Provisional resolution and TTL sweep** — At declaration (validation) and on a scheduled sweep, for any absent_declared/honest_expected_but_absent slot.. 1) At declaration: an absent_declared slot whose candidate_meet=expected MUST carry a resolvable_anchor {kind: url|doi|accession|repo_sha, value}; if absent, validator rejects → bucket=lazy_omission immediately. 2) Set provisional_until = today + provisional_ttl_days. 3) Sweep: a deterministic resolver fetches the anchor. Success (artifact retrievable) → bucket=present_as_expected, provisional cleared. Anchor well-formed but content 404/embargoed → stays honest_expected_but_absent until TTL. 4) At provisional_until, if still unresolved → auto-convert bucket to lazy_omission and increment provisional_debt.
    - reliability/reproducibility: Class B (reliable): the fetch depends on external hosts, so define failure modes explicitly — resolvable-but-embargoed stays honest until TTL; unresolvable-from-start (bad anchor) is rejected at declaration; unresolved-past-TTL is deterministically penalized. Owner: the seal-issuing tool runs the sweep; effect on coverage is defined (lazy_omission is the only penalized bucket). No park-forever path exists.
    - constraints: Ecosystem must provide an artifact-fetch resolver (repo clone by sha, DOI/accession dereference) and a scheduler. contested_until reuses the same TTL machinery.
  - **Taxonomy version migration** — Every genre_taxonomy version bump.. 1) Diff old vs new tables/predicates/classifier → generate taxonomy_diff with change_class per cell. 2) CI lints: no blank conditional cell; any new_slot ships a full adjudicated column; any new_type ships full rows. 3) Publish diff, human-sign. 4) Re-score policy: pinned ARAs stay valid against their pinned version forever; opt-in re-score applies loosen changes automatically (coverage can only hold/improve) and requires author re-declaration for tighten changes; a tighten can NEVER retroactively bucket a pinned ARA's slot as lazy_omission.
    - reliability/reproducibility: Class A governance: the diff is deterministic data; the non-retroactivity rule is enforced by pinning. Auditors read the signed diff to see exactly which cells moved and why.
    - constraints: Requires a governance body, an RFC process with rationale_anchors, and CI on the spec repo. Version pins in every genre.yaml must be immutable.

  _Metrics afforded:_
  - silent_omission_count (Level-1 gate) → Count of taxonomy slots (universal+conditional) absent from artifact_status. MUST be 0 or structural validation fails. [deterministic]; anti-Goodhart: It is a build gate, not a scored dimension — there is nothing to inflate. You cannot omit a slot to avoid its expectation; omission fails the seal outright, converting silent-and-ambiguous absence into a hard, checkable failure.
  - declared_coverage_score → (# slots in good buckets: present_as_expected, honest_not_applicable, honest_expected_but_absent, present_unexpected) / (# resolved slots). lazy_omission and structural_contradiction are the only penalized buckets; contested_pending is neutral pending TTL. [deterministic]; anti-Goodhart: Declaring everything not_applicable fails: a false N/A on a slot whose candidate_meet=expected is bucketed structural_contradiction (penalized). N/A is only credited when the deterministic table+predicate join agrees or a valid override anchor exists. Honest absence scores EQUAL to presence, so there is no incentive to fabricate an artifact — only to declare truthfully.
  - genre_contested_rate → Fraction of ARAs (or corpus) with genre_contested=true after the pinned meet+classifier resolution. [reproducible (label) + deterministic (decision)]; anti-Goodhart: Genre-shopping to a lenient type raises the rate, not lowers expectations: meet keeps coverage honest (no manufactured absence) while the contested flag is published, caps the seal tier, and flips to strict at TTL. Abstract-phrasing games must ALSO defeat the non-LLM structural_corroborator's checkable anchors, which they cannot forge without depositing the real artifacts.
  - warranted_absence_rate → (# honest_expected_but_absent with a resolvable_anchor that the sweep confirms well-formed) / (# slots where candidate_meet=expected but artifact absent). [reliable-anchored]; anti-Goodhart: Fake or vacuous reasons earn nothing: credit requires a resolvable_anchor (URL/DOI/accession/repo_sha), and the sweep dereferences it. Prose quality is never scored. An anchor that never resolves past TTL converts to lazy_omission, so padding reasons cannot buy standing.
  - provisional_debt → Count of provisional slots unresolved past provisional_until (auto-converted to lazy_omission). Exceeding a cap blocks the top seal tier. [deterministic]; anti-Goodhart: Closes the park-forever loophole: a tooling-limitation absence cannot sit indefinitely as 'neutral' — it must carry an anchor at declaration and self-destructs into the penalized bucket at TTL. Debt is visible and tier-gating, so accumulating provisionals is strictly worse than resolving them.
  - warrant_integrity_score → 1 - (contested_pending + unresolved_provisional + structural_contradiction) / total_slots — a separate axis from coverage so honest classification is decoupled from artifact presence. [deterministic]; anti-Goodhart: Decoupling prevents a paper from trading a genre lie for a coverage win: shopping tanks integrity even when meet keeps coverage untouched. Both axes must be high, and neither rewards length, boilerplate, or fabricated-but-consistent reasons.

  _Tradeoffs:_ Honest costs and residual surfaces: (1) Classification label remains class C — reproducible only as long as the pinned ensemble weights/API snapshots are archived; if a vendor deletes a model, that taxonomy version's label is no longer reproducible and a version bump is forced. Mitigation: prefer at least one open-weights model in every ensemble so reproducibility never depends on a single closed vendor. (2) The structural_corroborator can only corroborate genres that HAVE hard anchors (trials, reviews, theory, datasets); purely narrative genres (position, qualitative) rest on the LLM ensemble alone, so abstract-gaming has more room there. Mitigation: those genres also have the SMALLEST conditional-expected sets, so the shopping payoff is low, and contested still fires on ensemble disagreement. (3) The meet's lenient default means a genuine shopper gets a temporary coverage reprieve during the TTL window; a paper could be funded/cited before contested_until flips it. Mitigation: genre_contested is published immediately and caps the seal tier from day one, so downstream consumers see the dispute in real time. (4) Exhaustive conditional columns are real governance labor — adding a slot means adjudicating 14 cells. This is deliberate: it is a semantic decision that SHOULD be made once, centrally, and audited, not defaulted. Mitigation: taxonomy CI + taxonomy_diff make the labor bounded and reviewable. (5) Predicate resolvers depend on sibling layers (entity ledger, refs table); if those are thin, predicates fall to not_applicable and could under-expect. Mitigation: a missing-sidecar predicate raises a structural lint rather than silently resolving. (6) A determined author can forge a resolvable_anchor that returns a plausible-but-wrong artifact (e.g., a repo that is not actually the analysis code). That is content fraud, out of scope for the genre layer — but it is now a checkable, attributable claim other layers (claims/evidence review) can attack, rather than a silent gap."

  _Open questions:_ 1) Label reproducibility over decades: how does the ecosystem guarantee a 2026-pinned ensemble is still runnable in 2040 for audit? A reference-output cache (title/abstract → label) per taxonomy version may be needed as a fallback oracle. 2) The MEET default is provably fabrication-safe but is it strategically optimal? A sophisticated actor could straddle two genres so that every contentious slot lands in disagreement and enjoys lenient coverage until TTL. Is contested-rate + tier-capping a strong enough deterrent, or does the meet need a stricter default for repeat offenders (reputation-conditioned resolution)? 3) predicate_defs are themselves a governance surface — a predicate regex that is too loose (e.g. matching any 'github' mention) over-expects; who audits predicate quality and how is a bad predicate deprecated without retroactively penalizing pinned ARAs? 4) Cross-genre papers (genuinely mixed_methods, or a theory+empirical hybrid): a single primary paper_type may be a poor fit; should the manifest support a weighted multi-genre declaration whose expectation table is a per-slot meet across the declared blend, and does that reopen shopping? 5) Who governs the taxonomy, and how are conflicts of interest (a funder or lab lobbying to mark their weak slot not_applicable for their favored genre) prevented in the RFC process?

  _Changes from critique:_ Closed all five critique holes. HOLE 1 (undefined 'stricter wins'): eliminated genre-level ordering entirely. Resolution is now PER-SLOT over the two-element candidate set {g_declared, g_blind} on the expectation lattice not_applicable ⊑ expected. Coverage uses the MEET (greatest lower bound): resolved(s)=E_declared(s) if it equals E_blind(s), else meet = not_applicable + flag `contested`. PROOF the resolver never expects a both-N/A (or even either-N/A) slot: coverage marks s=expected iff meet(E_declared(s),E_blind(s))=expected iff BOTH candidates mark s expected; therefore if either marks s not_applicable, meet ⊑ that value = not_applicable, so s is never coverage-expected. This is strictly stronger than the requested guarantee. Anti-shopping is not lost: disagreement sets genre_contested=true (published, caps the seal tier, TTL-bounded); if unresolved past TTL the contested slots flip to the STRICT value and absence there becomes lazy_omission — so shopping buys only a loud, expiring reprieve, never a silent expectation cut. HOLE 2 (nondeterministic classifier): added classifier_manifest as versioned DATA — ensemble {model_id, prompt_sha256}, temperature 0, seed, input_fields restricted to {title, abstract, venue_article_type}, majority_vote aggregation, alphabetic-lowest-id tie-break, dispute_threshold τ and confidence_floor as numbers. Label = class C (reproducible via pin); agreement/contested DECISION = class A deterministic given label+threshold. Added a non-LLM structural_corroborator so abstract-gaming must also forge checkable hard anchors. HOLE 3 (context_dependent discretion sink): removed the value; every conditional cell is now expected_if(predicate_id) resolved by a typed non-LLM resolver (accession_regex | entity_type_presence | verbatim_quote_regex | sidecar_presence). Walked ml_empirical/src.prompts → expected_if(uses_generative_model) → entity-ledger lookup for entity.type∈{llm,foundation_model,prompted_model}; TRUE→expected else not_applicable. No LLM read. HOLE 4 (governance/migration): ARAs pin taxonomy_version and stay valid forever against it; every version bump ships a machine-readable taxonomy_diff classifying each cell change as loosen|tighten|new_slot|new_type|new_predicate; re-scoring against a newer version is opt-in; a tighten (N/A→expected) can NEVER retroactively create lazy_omission on a pinned ARA; new conditional slots must ship a full adjudicated column, linted in taxonomy CI. HOLE 5 (provisional loophole): absent_declared/provisional REQUIRES a resolvable_anchor at declaration time (no anchor → validator rejects → immediate lazy_omission), carries provisional_until TTL, and a deterministic sweep auto-converts unresolved-past-TTL slots to lazy_omission with a bounded provisional_debt metric that blocks the top seal tier.

  _Adopted from competitor:_ Four adoptions from The Genre Contract. (1) `expected_if_<fact_id>` conditional defaults — strictly better than my old `context_dependent` because it names a checkable predicate instead of punting to discretion; I adopted it as the ONLY conditional mechanism and gave every predicate a typed non-LLM resolver. (2) The explicit bucket state machine {present_as_expected, honest_not_applicable, honest_expected_but_absent, lazy_omission, structural_contradiction} — cleaner than my prose statuses; I adopted it and added contested_pending + present_unexpected. (3) Override-with-anchor discipline that REUSES the claims-layer verbatim-quote grounding (reason_anchor {file, locator, quote}) rather than inventing a new provenance surface — this is the right "no new fabrication surface" framing. (4) PAPER.md frontmatter mirror of paper_type for progressive disclosure, and per-ARA version pinning of the shared tables. I did NOT adopt competitor's "unlisted (type,slot) defaults to expected" for conditional slots — see why_this_beats_competitor — but I kept its spirit for genuinely UNIVERSAL slots (PAPER.md, claims, problem) which default expected safely.

  _Why it wins:_ The competitor's "unlisted defaults to expected" is a silent fabrication surface: any conditional slot a governance editor forgets to list becomes `expected` for a paper type where it is genuinely not_applicable, manufacturing exactly the absence penalty the mandate forbids — and it does so invisibly. My design forbids defaulting on conditional slots (taxonomy CI lints for a full adjudicated column) and defaults-expected only on the handful of truly universal slots, so a table gap is a taxonomy build failure, never a per-ARA false absence. Second, competitor's genre disambiguation is a bare `contested: bool` from "a multi-pass classification audit" — the classifier, its determinism, its threshold, and what `contested` DOES to the score are all unspecified; my classifier_manifest pins model ids, prompt hashes, temperature, threshold, and tie-break as data, and I give the meet-resolution proof competitor never provides. Third, competitor's `expected_but_absent` bucket has no TTL, no resolvable-anchor requirement, and no auto-conversion — it is an unbounded park-forever loophole; my TTL sweep + declaration-time anchor requirement + provisional_debt metric bound it. Fourth, competitor has no migration semantics at all — no diff artifact, no non-retroactivity rule — so a v1→v2 edit can silently flip N/A→expected across a corpus; my taxonomy_diff + pin-forever + opt-in re-score rules make evolution auditable and prove it never retroactively creates absence penalties. Same core class-A move, but every place competitor waves past a discretion sink, mine bottoms out in data or a proof.


---


## REFGRAPH — Normalized reference graph with resolvable

_Class B — anchor-dependent (reliability + protocol)_


**Judge rationale:** All four are variations on the same correct core idea (one normalized refs ledger + inline id tokens + honest unresolved/greylit records), so ranking turns on the Class-B-specific differentiators the mandate stresses: (a) is the FABRICATION surface first-class, (b) is the resolver's decision FALSIFIABLE/recomputable, (c) is the reliability-not-determinism boundary drawn, and (d) is dedup/disambiguation actually specified rather than gestured at.\n\n#3 wins the fabrication test outright: `dead_or_fabricated` as a first-class status with a worked example (a well-formed DOI that Crossref 404s), plus `resolution_candidates.yaml` recording EVERY candidate so confidence is (nominally) recomputable, plus `checked_at` re-verification semantics and `open_access` gating verification honestly. It is also the most implementable (regex-extractable `[text](ref:R###)` with a deterministic referential-integrity check). Its flaws — conflating dead-vs-fabricated and an undefined confidence function — are correctable without redesign.\n\n#0 wins the architecture test: it is the only design that separates citation-occurrence from cited-work from claim-target (X/R/SREF), which is the measurement-theoretically right move and the strongest structural defense against reference-count gaming, with quote-hash-anchored claim verification. But it lacks a first-class fabricated/dead/mismatch status (the very hole Class B must close), blurs B vs C by treating an LLM-judge verdict as a reliability output, and leaves its dedup protocol truncated.\n\n#2 is a strong third — clean B-fact vs C-judgment split (refs_verification.yaml), receipt_hash proofs, explicit derived/non-authored neighborhood cache — but receipt_hash is opaque compared to #3's full candidate log, and it lacks a first-class fabricated bucket. #1 is last: it has the most explicit and correct 'reliable, not deterministic' framing and good protocol prose, but it is essentially a lighter twin of #0 from the same model with thinner schema, a truncated dedup protocol, and a status enum {verified|ambiguous|unresolved|not_applicable} that omits dead/fabricated/mismatch — i.e. it is weakest on the exact fabrication surface the mandate demands.


### Finalist A (refined)

> _Judge critique it answered:_ Proposal #3 (Resolved Reference Ledger) is the most on-mandate Class-B design because it treats fabrication as a first-class status and makes the resolver falsifiable — but it has fixable holes that a ruthless reviewer will not let pass.

1) `dead_or_fabricated` conflates two epistemically OPPOSITE things. A dead link (was real, rotted) is honest decay; a fabricated id (never existed) is misconduct. Lumping them means legitimate link-rot gets tarred as fabrication and vice versa. Worse: a single Crossref 404 CANNOT distinguish "fabricated" from "transient registry outage / DataCite-vs-Crossref split / embargoed new DOI." You are one API hiccup away from manufacturing a false misconduct signal. Split into `dead` vs `fabricated`, and require a retry policy + cross-registry confirmation (Crossref AND DataCite AND OpenAlex negative) before ANY entry is allowed to assert `fabricated`.

2) `confidence: float [0,1]` is a vibe until the scoring function is pinned. You claim resolution_candidates.yaml makes confidence "recomputable from the same raw response," but you never state the function. Specify it: e.g. normalized Levenshtein on title (with subtitle stripping), Jaccard on author sets, exact year match, and the accept/ambiguous/reject thresholds. Without the function, "0.97" is un-recomputable and your central auditability selling point is hollow.

3) `dedup_cluster` fingerprint = "title + first-author + year" collides and misses. First-author-only breaks on author-order changes; preprint↔published title edits break title equality; "et al." truncation destroys author sets. Define the normalization (case, diacritics, subtitle stripping, unicode) AND state explicitly how preprint and published versions link (a `version_of` edge, not silent collapse or silent duplication) — the mandate names deduplication as load-bearing and this is where it leaks.

4) The resolver's `canonical_metadata` REPLACES the author's cited string as "authoritative" — but a high-confidence MIS-resolution launders a wrong citation into truth. You need `mismatch` (which you have as a status but do not wire to a trigger) to fire automatically when resolved metadata diverges from `raw_mentions` beyond threshold, and you must ALWAYS preserve the as-cited string. Show the multi-candidate disambiguation procedure explicitly.

5) `used_by` (reverse join) is required but nothing enforces bidirectional consistency with `source_locations`/`raw_mentions`. That is a Goodhart hole: a ref can advertise `used_by` claims it never actually supports, inflating landscape/coverage metrics. State the round-trip invariant AS A VALIDATOR (grep every R### in the ARA ⇔ source_locations ⇔ used_by must agree) and specify the failure behavior on mismatch.

6) `open_access` gating claim-drift is smart, but `paywalled_abstract_only` still permits abstract-level checks — be explicit that `unverifiable` is recorded PER CITING CONTEXT, never silently skipped, or paywalled refs become a fabrication haven where no one can check the claim.

**Resolved Reference Spine v2 — Deterministic Resolution, Quarantined Judgment**  ·  _source: gpt-5.5-codex_

Every cited object becomes one canonical R### record in a normalized reference graph; every citation OCCURRENCE (X####) points to that R###; every claim/gap/dependency an occurrence supports is a separate SREF### edge. That three-way split (work / occurrence / supported-claim) is what kills the reference-count Goodhart hole, and this version hardens it on the Class-B essentials the mandate foregrounds. It draws a hard B/C line: identity RESOLUTION (does this id resolve, to what, with what metadata match, is the quoted span verbatim-present in retrieved text) is deterministic given a registry snapshot and a retrieval receipt — that is the reliability guarantee. Semantic JUDGMENT (does the source actually support the assertion) is quarantined into a labeled Class-C block that is never counted as a reliability guarantee. The central fabrication surface is now explicit: a well-formed DOI that 404s is `dead`, an id that resolves to a different work is `mismatch`, and both are separated from honest `grey_lit`/`unresolved` — a fabricated shaped id can no longer hide as honest greylit. The match algorithm, thresholds, dedup keys, preprint↔published linking, and tie-breaking are fully specified and recomputable; the derived dependency graph is cut as authored data and reduced to a view.

- **refs/reference_spine.yaml** (YAML, human-readable canonical ledger.) — One normalized record per distinct cited work/dataset/registration/standard/software/protocol/grey-literature source used anywhere in the ARA. This is the single join target every inline citation resolves into.
  - fields: ref_id : string (R###) — required — stable local id, never reused/renumbered. source_kind : enum{scholarly_article, preprint, dataset, registration, standard, software, protocol, webpage, book, personal_communication, other} — required. resolution_status : enum{verified | mismatch | ambiguous | dead | unresolved | grey_lit | not_applicable} — required — PURELY identity resolution, deterministic given a snapshot (see Resolution Protocol); retraction is orthogonal, in integrity_flags. absence_reason : string|null — required (first-class null; e.g. 'no scholarly id exists for internal SOP'). canonical_ids : map — required, may be {} — {doi, openalex, semantic_scholar_corpus_id, pmid, arxiv, datacite, isbn}. bibliographic_fingerprint : object — required — {title, authors[] (surname-first tokens), year:int|null, venue|null, volume|null, pages|null} — the CITED work as asserted by the author (the claim under test), NOT the resolver's answer. resolver_evidence : object — required — {resolvers_used[], snapshot_id:string (pinned registry snapshot, e.g. 'crossref-2026-06'), resolved_at:datetime|null, resolved_fingerprint:object|null (what the registry actually returned), match_confidence:float 0..1|null, metadata_match:{title_sim:float, author_overlap:float, year_delta:int|null}, decision_band:enum{accept|ambiguous|reject}, candidate_sidecar_ref:string|null (points to resolution_candidates.yaml)}. version_group : string|null — required nullable — shared id linking preprint↔published records of the SAME work (see Dedup Protocol); each version stays a separate R###. dedup_cluster : string — required — canonical merge key (normalized DOI, else registry id, else fingerprint hash). access : object — {full_text_status: open|closed|abstract_only|unavailable|unknown, full_text_url|null, license|null}. integrity_flags : object — {retraction_status: none|retracted|corrected|expression_of_concern|unknown, id_conflict:bool, duplicate_of:R###|null, fabrication_review:enum{not_run|no_signal|likely_fabricated}|null (Class-C escalation of `dead`, evidence in candidate sidecar; NEVER changes resolution_status), notes|null}. provenance : object — {first_seen_in: path+locator, surface_forms:[string]}.
  - example: schema: ara.ref_spine.v2
paper_id: che26-plasma-p-tau217
reference_records:
  - ref_id: R014
    source_kind: scholarly_article
    resolution_status: verified
    absence_reason: null
    canonical_ids: {doi: "10.1093/brain/awac333", openalex: "W4318778821", semantic_scholar_corpus_id: "255134092", pmid: "36478198", arxiv: null}
    bibliographic_fingerprint:
      title: "Head-to-head comparison of 10 plasma phospho-tau assays in prodromal Alzheimer disease"
      authors: ["Janelidze S", "Mattsson-Carlgren N"]
      year: 2023
      venue: "Brain"
      volume: "146"
      pages: "1592-1601"
    resolver_evidence:
      resolvers_used: ["crossref", "openalex", "pubmed"]
      snapshot_id: "crossref-2026-06"
      resolved_at: "2026-07-06T10:22:18Z"
      resolved_fingerprint: {title: "Head-to-head comparison of 10 plasma phospho-tau assays in prodromal Alzheimer's disease", authors: ["Janelidze S", "Mattsson-Carlgren N"], year: 2023, venue: "Brain"}
      match_confidence: 0.98
      metadata_match: {title_sim: 0.98, author_overlap: 1.0, year_delta: 0}
      decision_band: accept
      candidate_sidecar_ref: "resolution_candidates.yaml#R014"
    version_group: null
    dedup_cluster: "doi:10.1093/brain/awac333"
    access: {full_text_status: closed, full_text_url: "https://academic.oup.com/brain/...", license: not_specified}
    integrity_flags: {retraction_status: none, id_conflict: false, duplicate_of: null, fabrication_review: not_run, notes: null}
    provenance: {first_seen_in: "logic/problem.md#O02", surface_forms: ["Janelidze et al., 2023", "Janelidze 2023 head-to-head"]}

  # Fabricated/dead example — the CENTRAL Class-B surface:
  - ref_id: R055
    source_kind: scholarly_article
    resolution_status: dead          # well-formed DOI, registry returns 404 — NOT lumped into unresolved
    absence_reason: null
    canonical_ids: {doi: "10.1234/fake.5678", openalex: null, semantic_scholar_corpus_id: null, pmid: null, arxiv: null}
    bibliographic_fingerprint: {title: "Smith et al. universal plasma biomarker", authors: ["Smith J"], year: 2021, venue: null, volume: null, pages: null}
    resolver_evidence:
      resolvers_used: ["crossref", "datacite", "openalex"]
      snapshot_id: "crossref-2026-06"
      resolved_at: "2026-07-06T10:25:00Z"
      resolved_fingerprint: null
      match_confidence: 0.0
      metadata_match: {title_sim: 0.0, author_overlap: 0.0, year_delta: null}
      decision_band: reject
      candidate_sidecar_ref: "resolution_candidates.yaml#R055"
    version_group: null
    dedup_cluster: "doi:10.1234/fake.5678"
    access: {full_text_status: unavailable, full_text_url: null, license: null}
    integrity_flags: {retraction_status: unknown, id_conflict: false, duplicate_of: null, fabrication_review: likely_fabricated, notes: "Well-formed DOI returns 404 in Crossref+DataCite; no title match in any registry snapshot; appears only in this artifact."}
    provenance: {first_seen_in: "logic/related_work.md#brief", surface_forms: ["Smith et al. 2021"]}

  # Mismatch example — id is LIVE but points to a DIFFERENT work than cited:
  - ref_id: R061
    source_kind: scholarly_article
    resolution_status: mismatch
    absence_reason: null
    canonical_ids: {doi: "10.1001/jamaneurol.2020.0989", openalex: null, semantic_scholar_corpus_id: null, pmid: null, arxiv: null}
    bibliographic_fingerprint: {title: "Plasma p-tau217 predicts tau PET across the AD continuum", authors: ["Palmqvist S"], year: 2020, venue: "JAMA", volume: null, pages: null}
    resolver_evidence:
      resolvers_used: ["crossref"]
      snapshot_id: "crossref-2026-06"
      resolved_at: "2026-07-06T10:26:00Z"
      resolved_fingerprint: {title: "Association of cerebrospinal fluid biomarkers with cognition", authors: ["Nelson A"], year: 2020, venue: "JAMA Neurology"}
      match_confidence: 0.11
      metadata_match: {title_sim: 0.12, author_overlap: 0.0, year_delta: 0}
      decision_band: reject
      candidate_sidecar_ref: "resolution_candidates.yaml#R061"
    version_group: null
    dedup_cluster: "doi:10.1001/jamaneurol.2020.0989"
    access: {full_text_status: closed, full_text_url: "https://doi.org/10.1001/jamaneurol.2020.0989", license: null}
    integrity_flags: {retraction_status: unknown, id_conflict: true, duplicate_of: null, fabrication_review: no_signal, notes: "DOI resolves to a different article (title_sim 0.12); likely a copy-paste id error, not fabrication."}
    provenance: {first_seen_in: "logic/claims.md#C05", surface_forms: ["Palmqvist et al., 2020"]}

  # Honest grey literature — first-class, scored neutral, NOT confusable with dead/fabricated:
  - ref_id: R041
    source_kind: personal_communication
    resolution_status: grey_lit
    absence_reason: "Genuinely unpublished internal SOP; no persistent scholarly identifier exists."
    canonical_ids: {}
    bibliographic_fingerprint: {title: "Internal cohort SOP v3 (unpublished)", authors: ["Lab internal"], year: 2024, venue: null, volume: null, pages: null}
    resolver_evidence: {resolvers_used: ["crossref","openalex"], snapshot_id: "crossref-2026-06", resolved_at: "2026-07-06T10:27:00Z", resolved_fingerprint: null, match_confidence: null, metadata_match: {title_sim: 0.0, author_overlap: 0.0, year_delta: null}, decision_band: reject, candidate_sidecar_ref: null}
    version_group: null
    dedup_cluster: "fingerprint:internal-cohort-sop-v3-2024"
    access: {full_text_status: unavailable, full_text_url: null, license: null}
    integrity_flags: {retraction_status: none, id_conflict: false, duplicate_of: null, fabrication_review: not_run, notes: "Honest absence; must not be counted as peer-reviewed support."}
    provenance: {first_seen_in: "src/environment.md#Methods-2", surface_forms: ["internal cohort SOP v3"]}
- **refs/citation_mentions.yaml** (YAML or JSONL. Prose still renders as ordinary markdown via render_hint, e.g. [Janelidze et al., 2023](ref:R014).) — Every citation OCCURRENCE in every layer binds to exactly one R### (or one unresolved surface key), carrying its local role and target object. Separates occurrence from work — so citing the same work in three layers is three X#### rows over one R###, and no metric can reward re-citation.
  - fields: cite_id : string (X####) — required. ref_id : R###|null — required nullable — MUST resolve to a live spine record unless null. unresolved_surface_key : U###|null — used only when ref_id is null (a mention the compiler could not even cluster yet). location : object — {path, selector: line|heading|block_id|byte_range, value} — deterministic anchor into the layer file. surface_text : string — exact author-year/prose as rendered. citation_role : enum{background | supports_claim | motivates_gap | baseline | method_import | bounds_scope | refutes | dataset_source | tool_source}. cited_for : object — {object_type: claim|observation|gap|related_work|experiment|concept|tree_node|evidence_object, object_id}. polarity : enum{supports | contrasts | refutes | neutral | unknown}. render_hint : string|null.
  - example: citation_mentions:
  - cite_id: X0042
    ref_id: R014
    unresolved_surface_key: null
    location: {path: "logic/problem.md", selector: heading, value: "O02"}
    surface_text: "Janelidze et al., 2023"
    citation_role: motivates_gap
    cited_for: {object_type: observation, object_id: O02}
    polarity: supports
    render_hint: "[Janelidze et al., 2023](ref:R014)"
  - cite_id: X0067
    ref_id: R014            # SAME work, different layer/occurrence — separate X row, one R node
    unresolved_surface_key: null
    location: {path: "logic/claims.md", selector: block_id, value: "C01"}
    surface_text: "Janelidze 2023 head-to-head"
    citation_role: baseline
    cited_for: {object_type: claim, object_id: C01}
    polarity: supports
    render_hint: "[Janelidze et al., 2023](ref:R014)"
- **refs/support_edges.yaml** (YAML.) — States what an occurrence is being used to prove, and splits verification into a deterministic anchor_check (Class B: is the quoted span verbatim present in the retrieved source at the stated locator?) and a quarantined semantic_review (Class C: does the source support the assertion?). The B block is a reliability guarantee; the C block explicitly is not.
  - fields: edge_id : string (SREF###) — required. cite_id : X#### — required — must exist. ref_id : R### — required — must exist and MUST equal the cite_id's ref_id (integrity check). target_id/target_type : the supported object. assertion_text : string — the local assertion the citation is supposed to support. source_anchor : object — {locator:string|null (page/section/figure/table), quote:string|null, quote_hash:string|null (sha256 of the normalized quote; MUST be null unless anchor_status==exact AND retrieval_receipt present), anchor_status: exact|approximate|no_full_text|unresolved, retrieval_receipt:object|null — {retrieved_at, source_url, http_status:int, content_hash:string (sha256 of retrieved full text or extracted span), retriever:string}}. anchor_check : object (CLASS B — deterministic given the receipt) — {status: present|absent|not_retrievable|not_run, method: exact_substring|normalized_substring, checked_against:content_hash|null} — 'present' means the normalized quote is a verbatim substring of the receipted content. semantic_review : object (CLASS C — QUARANTINED, NOT a reliability guarantee) — {status: not_run|entailed|partially_supported|unsupported|contradicted|inaccessible, judge_ensemble:[string], votes:{entailed:int, partial:int, unsupported:int, contradicted:int}, for_evidence:string|null, against_evidence:string|null, confidence:float|null, calibration_set:string|null, reviewed_at:datetime|null} — REQUIRES anchor_check.status==present to run at sentence/figure granularity (no full text ⇒ status:inaccessible).
  - example: support_edges:
  - edge_id: SREF019
    cite_id: X0042
    ref_id: R014
    target_id: O02
    target_type: observation
    assertion_text: "Prior plasma p-tau217 studies report platform-dependent diagnostic performance, motivating cross-platform comparison."
    source_anchor:
      locator: "Abstract; Table 2"
      quote: "assays differed substantially in fold change and diagnostic accuracy"
      quote_hash: "sha256:8c9d2f..."
      anchor_status: exact
      retrieval_receipt: {retrieved_at: "2026-07-06T10:31:00Z", source_url: "https://academic.oup.com/brain/...", http_status: 200, content_hash: "sha256:be71a0...", retriever: "ara-fetch/1.2 (institutional-proxy)"}
    anchor_check: {status: present, method: normalized_substring, checked_against: "sha256:be71a0..."}
    semantic_review:
      status: partially_supported
      judge_ensemble: ["gpt-5.5", "claude-sonnet-5", "llama-4-70b"]
      votes: {entailed: 0, partial: 2, unsupported: 1, contradicted: 0}
      for_evidence: "Table 2 shows assay-dependent AUC spread (0.79-0.94)."
      against_evidence: "Paper reports performance differences but does not frame them as 'platform-dependent' causally."
      confidence: 0.71
      calibration_set: "reftruth-calib-2026Q2"
      reviewed_at: "2026-07-06T10:32:00Z"

  # No full text ⇒ quote_hash MUST be null, anchor_status no_full_text, semantic_review inaccessible:
  - edge_id: SREF031
    cite_id: X0067
    ref_id: R014
    target_id: C01
    target_type: claim
    assertion_text: "Janelidze 2023 serves as the head-to-head baseline cohort."
    source_anchor: {locator: "whole paper", quote: null, quote_hash: null, anchor_status: no_full_text, retrieval_receipt: null}
    anchor_check: {status: not_retrievable, method: normalized_substring, checked_against: null}
    semantic_review: {status: inaccessible, judge_ensemble: [], votes: {entailed:0,partial:0,unsupported:0,contradicted:0}, for_evidence: null, against_evidence: null, confidence: null, calibration_set: null, reviewed_at: null}
- **refs/resolution_candidates.yaml** (YAML sidecar keyed by ref_id.) — Audit sidecar recording EVERY candidate the resolver weighed for a ref (not just the winner), plus the raw signals, so anyone can recompute match_confidence and the decision_band from the same snapshot — this is what makes the resolution protocol falsifiable rather than self-asserted. Adopted from the competitor and extended with the per-signal breakdown needed to recompute the cutoffs.
  - fields: ref_id : R### — required. query : object — {title, authors[], year, ids_probed[]}. snapshot_id : string — required — pinned registry snapshot the candidates came from. candidates : list[{rank:int, source:crossref|openalex|arxiv|s2|datacite|pubmed, candidate_id:string, returned_fingerprint:object, title_sim:float, author_overlap:float, year_delta:int|null, composite:float (recomputable via Resolution Protocol formula), band:accept|ambiguous|reject}] — required. decision : object — {chosen_candidate_id:string|null, band:accept|ambiguous|reject, tie_break_applied:string|null, resolution_status_assigned:enum}. fabrication_signals : object|null — {registry_404:bool, zero_title_match_any_registry:bool, appears_only_in_artifact:bool} — populated when resolution_status∈{dead,mismatch} to justify any likely_fabricated escalation.
  - example: R061:
  query: {title: "Plasma p-tau217 predicts tau PET across the AD continuum", authors: ["Palmqvist S"], year: 2020, ids_probed: ["doi:10.1001/jamaneurol.2020.0989"]}
  snapshot_id: "crossref-2026-06"
  candidates:
    - rank: 1
      source: crossref
      candidate_id: "doi:10.1001/jamaneurol.2020.0989"
      returned_fingerprint: {title: "Association of cerebrospinal fluid biomarkers with cognition", authors: ["Nelson A"], year: 2020, venue: "JAMA Neurology"}
      title_sim: 0.12
      author_overlap: 0.0
      year_delta: 0
      composite: 0.11
      band: reject
  decision: {chosen_candidate_id: null, band: reject, tie_break_applied: null, resolution_status_assigned: mismatch}
  fabrication_signals: {registry_404: false, zero_title_match_any_registry: false, appears_only_in_artifact: false}

  _Protocols:_
  - **Resolution & Match Protocol (defines the accept/ambiguous/reject cutoffs)** — Every time a reference is resolved or re-checked; every time match_confidence or decision_band is written.. 1. NORMALIZE title: lowercase, NFKD Unicode fold to ASCII, strip punctuation, collapse whitespace, drop a leading article. 2. title_sim = character-trigram Jaccard(norm(cited_title), norm(returned_title)) ∈ [0,1]. 3. author_overlap = Jaccard over sets of normalized first-surname tokens (lowercase, ASCII-fold). 4. year_score = 1.0 if year_delta==0, 0.7 if |delta|==1 (preprint/published lag), else 0.0. 5. composite = 0.60*title_sim + 0.30*author_overlap + 0.10*year_score. 6. BANDS: accept iff (title_sim≥0.90 AND author_overlap≥0.66 AND |year_delta|≤1); reject iff title_sim<0.70; else ambiguous. 7. STATUS ASSIGNMENT: (a) an external id was given AND registry returns not-found/404 ⇒ `dead`. (b) id resolves but decision_band==reject (points elsewhere) ⇒ `mismatch`. (c) band==accept ⇒ `verified`. (d) band==ambiguous, or two given ids resolve to conflicting works ⇒ `ambiguous` (id_conflict=true). (e) no id, no candidate ≥ accept, work plausibly exists ⇒ `unresolved`. (f) source_kind has no citable id by nature ⇒ `grey_lit`. 8. Record ALL candidates + per-signal scores in resolution_candidates.yaml with the snapshot_id. 9. fabrication_review escalation (Class C, advisory only): `dead` + zero_title_match_any_registry + appears_only_in_artifact ⇒ likely_fabricated; NEVER mutates resolution_status.
    - reliability/reproducibility: Deterministic given (snapshot_id, cited fingerprint): identical inputs ⇒ identical title_sim/author_overlap/composite/band/status. Every number in resolver_evidence is recomputable from resolution_candidates.yaml by re-running steps 1-6, so a third party can falsify a claimed 'verified'. Time-relativity is captured by snapshot_id + resolved_at; a re-run against a newer snapshot may legitimately change `dead`→`verified` (registry backfill) and this is auditable, not silent.
    - constraints: Ecosystem must provide: pinned, versioned registry snapshots (Crossref/OpenAlex/arXiv/DataCite/PubMed) addressable by snapshot_id; a retraction feed (Retraction Watch/Crossref); and a resolver that emits per-candidate signals, not just a boolean. Without pinned snapshots the determinism guarantee downgrades to 'reproducible within a stated time window.'
  - **Dedup & Disambiguation Protocol** — Whenever two mentions might name the same work, or a preprint and its published version both appear.. 1. CLUSTER KEY: normalized DOI if present; else the first non-null registry id; else fingerprint hash = sha1(norm(title)+'|'+first_surname+'|'+year). 2. MERGE: mentions sharing a cluster key collapse to one R###; raw surface_forms are preserved in provenance for audit. 3. PREPRINT↔PUBLISHED LINKING: if two DIFFERENT clusters have title_sim≥0.90 AND author_overlap≥0.66 but different venue/id families (e.g. one arXiv/bioRxiv, one journal DOI), they are the same work across versions — keep BOTH R### records (they are genuinely different artifacts with different access/retraction status), assign a shared version_group, and mark the journal record canonical (used for peer-review-weighted metrics). 4. AMBIGUOUS-CLUSTER RESOLUTION: when band==ambiguous with ≥2 candidates, do NOT auto-pick; set resolution_status=ambiguous and list candidates. TIE-BREAK ORDER (deterministic) only to choose a DISPLAY canonical, never to upgrade to verified: (i) prefer a candidate carrying a DOI, (ii) prefer the registry with retraction coverage, (iii) higher composite, (iv) more complete metadata, (v) earliest resolved_at. 5. id_conflict: two author-given ids resolving to different works ⇒ ambiguous + id_conflict=true + notes.
    - reliability/reproducibility: Cluster keys and tie-break order are total and deterministic ⇒ same corpus + snapshot yields the same clustering run-to-run. version_group keeps the honest distinction between a non-peer-reviewed preprint and its published version instead of silently merging them, which protects peer-review-weighted metrics.
    - constraints: Ecosystem must provide preprint-to-published linkage data (OpenAlex 'has_version'/Crossref relations); where absent, the protocol falls back to the title_sim/author_overlap test above and flags the link as heuristic (status stays honest).
  - **Referential-Integrity Validator (Class A, deterministic gate)** — On every compile/commit; blocks a malformed reference graph from being scored.. Assert, over the four files: (1) every citation_mentions.ref_id is null OR resolves to a live reference_spine.ref_id; (2) every non-null ref_id's mention has a matching render_hint token in the prose layer at its location (round-trip check); (3) every support_edge.cite_id exists and support_edge.ref_id == that mention's ref_id; (4) every support_edge.target_id exists in the referenced layer; (5) quote_hash is null unless anchor_status==exact AND retrieval_receipt present AND sha256(norm(quote)) is a substring-hash consistent with content_hash; (6) resolution_status==verified ⇒ decision_band==accept AND ≥1 non-null canonical_id; (7) grey_lit ⇒ canonical_ids=={} ; (8) dead/mismatch ⇒ resolver_evidence.resolved_at present. Any failure = hard error with the offending id.
    - reliability/reproducibility: Pure structural checks — fully deterministic, no judgment. This is what makes the four coupled files safe: the graph either passes integrity or is rejected; there is no partial/ambiguous validation.
    - constraints: Ecosystem must ship this validator as a required pre-scoring gate (like a linter). The dependency graph the old design shipped as a fourth authored file is CUT — it is now a DERIVED VIEW computed from citation_mentions.citation_role + support_edges, so there is nothing extra to keep in sync.
  - **Anchor-Retrieval & Verification Protocol** — Whenever an SREF claims a verbatim quote or an exact anchor, and whenever semantic_review runs.. 1. To set anchor_status=exact, the retriever MUST fetch the source and emit a retrieval_receipt {retrieved_at, source_url, http_status, content_hash, retriever}. 2. quote_hash = sha256(norm(quote)); it stays null otherwise. 3. anchor_check (CLASS B): status=present iff norm(quote) is a substring of the receipted content (content_hash); absent if retrieved-but-not-found; not_retrievable if no OA/licensed full text. 4. semantic_review (CLASS C) may run ONLY if anchor_check.status==present for sentence/figure granularity; it uses a ≥3-model judge ensemble, records votes + for_evidence + against_evidence + a calibration_set id, and outputs confidence. Its status is advisory metadata, never a reliability guarantee.
    - reliability/reproducibility: Class B here is genuinely reliable: quote PRESENCE is a deterministic string match against a hashed retrieval; anyone with the same receipt recomputes it. Class C is reproducible-not-deterministic: pinning the judge ensemble + calibration_set makes the vote distribution reproducible run-to-run, but the entailment call remains probabilistic and is labeled as such.
    - constraints: Ecosystem must provide licensed/OA full-text retrieval with content addressing, and a shared, versioned reftruth calibration set of human-labeled (assertion, source, verdict) triples so judge confidence is calibrated rather than a vibe. Closed-access works legitimately terminate at anchor_status=no_full_text with no penalty (honest-absence symmetry).

  _Metrics afforded:_
  - Resolution integrity rate = verified / (verified + dead + mismatch + ambiguous) → Count reference_spine records by resolution_status; grey_lit, unresolved, not_applicable are EXCLUDED from the denominator (honest-absence symmetry). dead/mismatch count against. [reliable-anchored]; anti-Goodhart: Fabricated shaped ids can no longer inflate the numerator: a 404 DOI is `dead`, a wrong-target id is `mismatch`, and both are separate first-class buckets that lower the score. You cannot launder a fake DOI through `unresolved`/`grey_lit` because those require canonical_ids=={} and an honest absence_reason, checked by the validator.
  - Reference-graph structural integrity (pass/fail) → Output of the Referential-Integrity Validator over all four files. [deterministic]; anti-Goodhart: Binary and structural — padding, boilerplate, or extra rows cannot improve it; a graph with a dangling X#### or a self-asserted `exact` anchor without a receipt simply fails and is not scored.
  - Receipt-backed anchor coverage = SREFs with anchor_check.status==present / SREFs whose source is retrievable (OA or licensed) → Deterministic substring check of each quote against its retrieval_receipt content_hash; no-full-text SREFs are excluded from the denominator, not penalized. [reliable-anchored]; anti-Goodhart: anchor_status=exact requires a retrieval receipt whose content_hash the quote_hash is consistent with; self-asserted `exact` is rejected by the validator. You cannot score by pasting plausible quotes — the quoted span must verbatim exist in the fetched text.
  - Claim-support fidelity (distribution of semantic_review verdicts, confidence-weighted) → Aggregate semantic_review votes across SREFs; report distribution with confidence and the calibration_set id. [semantic-judged]; anti-Goodhart: QUARANTINED as Class C and never presented as a reliability guarantee; requires a ≥3-model ensemble, records for/against and vote splits (minimizing judge degrees of freedom), and only runs where anchor_check==present so it cannot fabricate support for an unretrievable source. A high fidelity score with low receipt-backed anchor coverage is self-flagging.
  - Citation dedup compression = distinct occurrences (X) / distinct works (R) → Counts over citation_mentions vs reference_spine, using dedup_cluster. [deterministic]; anti-Goodhart: The three-way R/X/SREF split means the reward signal attaches to distinct VERIFIED WORKS that ANCHOR CLAIMS, not to citation occurrences. Re-citing the same work inflates X, not R, and inflating X changes nothing that any quality metric rewards — the classic reference-count Goodhart hole is closed structurally.
  - Honest-unresolved ratio (grey_lit + unresolved, with absence_reason present) → Fraction of refs honestly recorded as non-resolvable with a filled absence_reason. [reliable-anchored]; anti-Goodhart: Rewarded (or at worst neutral), never penalized, so there is no pressure to fabricate a DOI to escape a greylit label — which is the incentive Class B exists to remove. Abuse (dumping everything as greylit) is caught because grey_lit demands canonical_ids=={}; anything with a resolvable id must be resolved.

  _Tradeoffs:_ Costs: (1) The resolver + pinned-snapshot + retrieval-receipt infrastructure is heavier than a bare bibliography — but the mandate assumes an ecosystem that provides registries and full text, and without pinned snapshots + receipts none of the Class-B reliability claims hold, so this is load-bearing, not gold-plating. (2) Four files carry a referential-integrity burden; mitigated by making the validator a required deterministic gate and by CUTTING the old authored dependency_graph (now a derived view), reducing authored surface from four to three coupled files plus one audit sidecar. Fabrication surfaces and mitigations: (a) fake DOI ⇒ caught as `dead` via live registry lookup, not format-checking; (b) id pointing to a different work ⇒ caught as `mismatch` by the title_sim reject band against resolved_fingerprint; (c) self-asserted `exact` anchor ⇒ blocked because quote_hash must be receipt-consistent; (d) laundering fakes as greylit ⇒ blocked because grey_lit requires empty canonical_ids; (e) gaming semantic_review ⇒ contained by quarantining it as Class C, requiring anchor presence, and using a calibrated judge ensemble with for/against. Residual risk: `likely_fabricated` vs innocent `dead` link-rot is a genuine judgment — handled honestly by keeping it in fabrication_review (advisory) and NEVER letting it mutate the deterministic resolution_status. Second residual: registry coverage gaps mean some legitimate works resolve as `unresolved`; symmetric honest-absence scoring prevents that from being punished as fabrication.

  _Open questions:_ 1. Cross-registry disagreement: when Crossref says verified and OpenAlex returns a conflicting fingerprint, which snapshot wins? Current tie-break prefers retraction-covering registries, but a principled quorum rule across registries is unspecified. 2. The title-trigram-Jaccard cutoffs (0.90/0.70) are defensible defaults but not empirically calibrated across fields — non-English/regional venues and very short titles may need per-field thresholds. 3. version_group handles preprint↔published, but multi-version chains (v1/v2/v3 preprints + published + corrigendum) need a canonical-selection policy beyond 'journal DOI wins.' 4. Retrieval receipts prove a fetch happened and its content hash, but not that the retriever fetched the CORRECT landing page for a paywalled work behind a proxy; a signed, third-party retrieval oracle would close this but does not yet exist. 5. Distinguishing genuine fabrication from pre-registration/embargo/very-recent works that are legitimately not-yet-in-registries remains partly a timing judgment.

  _Changes from critique:_ Directly addressed all six critique points. (1) B/C LINE: split support_edges verification into anchor_check (Class B, deterministic quote-presence string match against a hashed retrieval) and semantic_review (Class C, explicitly quarantined, labeled NOT a reliability guarantee); the old single 'verifier_result: partially_supported 0.78 as reliability guarantee' is gone. Protocols now state which guarantees are deterministic resolution vs probabilistic judgment. (2) FABRICATION SURFACE: replaced the collapsing enum with resolution_status = {verified | mismatch | dead | ambiguous | unresolved | grey_lit | not_applicable}; `dead` (well-formed id 404s), `mismatch` (id resolves to a different work), and `grey_lit`/`unresolved` are now distinct, with fabrication_review as an advisory Class-C escalation that never mutates status. (3) MATCH ALGORITHM: fully specified title_sim (character-trigram Jaccard over a defined normalization), author_overlap (surname-set Jaccard), year_score, composite = 0.6/0.3/0.1, and accept/ambiguous/reject cutoffs (0.90/0.70; author≥0.66; |year|≤1) — all recomputable from resolution_candidates.yaml. (4) REFERENTIAL INTEGRITY: added a deterministic Class-A validator specifying every cross-file check; CUT the authored dependency_graph (was largely derivable) and demoted it to a derived view, reducing from four authored files to three + an audit sidecar. (5) DEDUP/DISAMBIGUATION: added a full protocol — cluster keys, preprint↔published linking via version_group, ambiguous-cluster non-auto-pick, and a total deterministic tie-break order. (6) QUOTE ANCHORING: quote_hash MUST be null unless anchor_status==exact AND a retrieval_receipt (with content_hash) is present; anchor_status=exact is receipt-backed and validator-enforced, so `exact` can no longer be self-asserted.

  _Adopted from competitor:_ Adopted the resolution_candidates audit sidecar (Sonnet 5's resolution_candidates.yaml) — recording every candidate the resolver weighed, not just the winner — and extended it with the per-signal breakdown (title_sim/author_overlap/composite/band) needed to actually RECOMPUTE the confidence and falsify a 'verified'. Adopted its explicit fabrication bucket idea (dead_or_fabricated) but improved on it by SEPARATING dead / mismatch / likely_fabricated rather than fusing them. Adopted its pinned resolver_version/snapshot concept (snapshot_id) and its checked_at/resolved_at time-relativity so re-verification is auditable. Kept its clean [display](ref:R###) inline convention (I already had render_hint) and its used_by reverse-join spirit (mine lives as the X####→cited_for binding).

  _Why it wins:_ The competitor has one flat refs.yaml: it conflates the cited WORK with the places it is used (raw_mentions/used_by as sub-lists), so it cannot separate a citation OCCURRENCE from the CLAIM that occurrence supports — which is exactly the separation that structurally kills the reference-count Goodhart hole. This design keeps the three-way R### / X#### / SREF### spine, so the reward signal attaches to distinct verified works that anchor claims, not to citation strings. On the Class-B essentials the mandate foregrounds, this version now matches OR beats the competitor: it separates dead vs mismatch vs likely_fabricated where the competitor fuses them into dead_or_fabricated (losing the copy-paste-error vs fabrication distinction); it draws an explicit B/C line and quarantines entailment as Class C, whereas the competitor's claim-drift log leaves the deterministic-vs-judgment boundary implicit; it makes anchor exactness receipt-backed and validator-enforced rather than self-asserted; and it ships a fully specified, recomputable match algorithm with cutoffs plus a real dedup/disambiguation protocol (version_group, tie-break order) rather than fields. A genuine merge is available and strictly better: this spine + the competitor's candidate-sidecar discipline, which is what the resolution_candidates.yaml here already integrates.


### Finalist B (refined)

> _Judge critique it answered:_ Proposal #0 (Resolved Reference Spine) has the deepest measurement-theoretic architecture of the four — it is the only design that cleanly separates the cited WORK (R###) from each citation OCCURRENCE (X####) from the CLAIM the occurrence supports (SREF###). That separation is what actually kills the reference-count Goodhart hole. But it is under-defended on exactly the Class-B essentials the mandate foregrounds.

1) You never draw the B/C line, and you smuggle C into B. `support_edges.verifier_result` with `entailed | contradicted | partially_supported` from an "llm-judge" is Class-C claim-drift dressed as a Class-B reliability guarantee. State plainly which guarantees are reliable RESOLUTION (id verified against registry — deterministic given a snapshot) versus semantic JUDGMENT (does the source support the claim — probabilistic). Do not let "partially_supported: confidence 0.78" masquerade as a reliability guarantee; it is the opposite.

2) THE central fabrication surface is missing. `resolution_status` = {verified | unresolved | grey_lit | retracted | not_applicable} has NO bucket for "well-formed DOI that 404s" or "id resolves to a DIFFERENT work than cited." A fabricated-but-shaped DOI falls into `unresolved` and becomes indistinguishable from honest greylit — collapsing the exact distinction Class B exists to protect. Add `fabricated`, `dead`, and `mismatch` (and separate the first two). Proposal #3 beats you decisively here.

3) `match_confidence: float`, `title_similarity`, `author_overlap` are asserted with no defined metric or threshold policy. Specify the algorithm and the accept/ambiguous/reject cutoffs, or `resolver_evidence` is decorative and un-recomputable — which defeats the entire "auditable resolution protocol" claim.

4) Four coupled files (spine + mentions + support_edges + dependency_graph) create a referential-integrity burden whose failure modes you never address: what validates that every X#### binds a live R###, every SREF cites an existing X and R, every D### edge's `evidence: [SREF###]` exists? And `dependency_graph` is largely DERIVABLE from `support_edges` — justify it as authored-and-not-derived, or cut it. Over-engineering is a real cost against implementability.

5) The dedup + disambiguation protocol — which the mandate names explicitly as load-bearing — is truncated/absent from what you show. You have `duplicate_of` and `id_conflict` fields but no procedure: preprint↔published linking, ambiguous-cluster resolution, tie-breaking. Fields without a protocol are not a protocol.

6) `quote_hash` anchoring is a genuine strength, but hashing a quote when `anchor_status: no_full_text` hashes nothing. Make `quote_hash` null unless full text was actually retrieved, and require `anchor_status: exact` to be backed by a retrieval receipt — otherwise `exact` is self-asserted and the whole anchor is gameable.

**The Resolved Reference Ledger (refs.yaml) + Occurrence/Support Split + Falsifiable Resolver**  ·  _source: Claude Sonnet 5_

Every cited work is registered exactly once in a normalized `refs.yaml` ledger keyed by an ARA-local id (R###) carrying resolved external ids plus a first-class resolution status. Crucially, three things are now separated instead of blurred: the cited WORK (refs.yaml), each citation OCCURRENCE (citations.yaml, one per inline mention, still rendered as `[Author, Year](ref:R###)` prose), and what that occurrence is used to SUPPORT (support.yaml, quote-anchored to the source). The resolver is falsifiable: `fabricated` is a hard misconduct signal that can ONLY be asserted after a retry policy plus a three-registry negative (Crossref AND DataCite AND OpenAlex), and it is split from `dead` (honest link-rot) so an API hiccup cannot manufacture a misconduct flag. The confidence score is a pinned, recomputable function (Levenshtein-title + Jaccard-authors + year), dedup normalization and preprint↔published `version_of` edges are specified, and a bidirectional round-trip validator (ARA prose ⇔ citations.yaml ⇔ refs.used_by) makes coverage metrics ungameable. This closes the Class-B gap by making every reference reliable-anchored through an auditable resolution protocol rather than deterministic-from-artifact, while keeping the cited-as string always preserved so a high-confidence mis-resolution cannot silently launder a wrong citation into truth.

- **refs.yaml** (YAML, one file at ARA root (logic/refs.yaml), list under top-level key `refs:`.) — Normalized citation ledger: every distinct cited WORK appears exactly once, deduplicated across all layers, carrying resolved external id(s), split resolution status, retraction status, version linkage, and the reverse-join index. This is the node table the whole reference graph joins on.
  - fields: id: string R{NNN} — required — ARA-local, never reused/renumbered.
raw_mentions: list[{text, layer, locator}] — required — every distinct as-cited prose string; provenance of the dedup decision and the always-preserved as-cited record.
canonical_metadata: {title, authors[], year, venue, volume, pages} — required, each field nullable — the RESOLVER's record, never overwrites raw_mentions.
source_kind: enum{scholarly_article, preprint, dataset, software, protocol, standard, webpage, technical_report, book, personal_communication} — required.
external_ids: {doi, arxiv, openalex, s2_corpus_id, pmid, isbn} — required object, each nullable — ≥1 non-null unless status∈{unresolved,greylit,pending}.
status: enum{resolved, mismatch, ambiguous, greylit, unresolved, dead, fabricated, pending} — required — first-class; dead≠fabricated; never inferred downstream.
greylit_type: enum{preprint_no_doi, dataset_accession, technical_report, personal_communication, unindexed_local_venue, non_english_regional, manufacturer_doc, other} — required iff status=greylit.
confidence: float [0,1] or null — required when status∈{resolved,mismatch,ambiguous} — the pinned Protocol-R score, recomputable from resolution_candidates.yaml.
version_of: {ref_id: R###, relation: enum{preprint_of, published_as, revision_of, translation_of}} or null — required field, null-valued when standalone — links preprint↔published WITHOUT collapsing them.
resolution_method: string — required unless status=pending — e.g. doi_direct_lookup, title_author_year_search.
resolvers_queried: list[{registry, verdict:enum{hit,miss,error,timeout}, at:ISO8601, version}] — required — the full multi-registry trail; a `fabricated` status requires ≥3 registries all with verdict=miss.
retraction_status: enum{ok, retracted, corrected, expression_of_concern, unknown, not_applicable} — required — unknown/not_applicable are honest, not failures.
access: {full_text_status: enum{open, closed, abstract_only, unavailable, unknown}, full_text_url, license} — required — gates support-verification granularity.
dedup_key: string — required — normalized DOI, else the Protocol-D fingerprint over NFKD-folded subtitle-stripped title + full last-name author set + year.
used_by: list[{object_type, object_id, relation}] — required, auto-derived — reverse index; MUST satisfy round-trip validators RG-1/2/3.
checked_at: ISO8601 — required — updated every re-verification pass even if status unchanged.
notes: string — optional — honesty note, e.g. why genuinely unresolvable.
  - example: refs:
  - id: R014
    raw_mentions:
      - {text: "Janelidze et al., 2023", layer: logic/related_work.md, locator: RW01}
      - {text: "Janelidze et al. (2023)", layer: logic/problem.md, locator: "O2 Evidence"}
    canonical_metadata:
      title: "Head-to-head comparison of 10 plasma phospho-tau assays in prodromal Alzheimer's disease"
      authors: ["Janelidze, Shorena", "Mattsson-Carlgren, Niklas"]
      year: 2023
      venue: "Brain"
      volume: "146"
      pages: "1592-1601"
    source_kind: scholarly_article
    external_ids: {doi: "10.1093/brain/awac333", arxiv: null, openalex: "W4318778821", s2_corpus_id: "255134092", pmid: "36478198", isbn: null}
    status: resolved
    confidence: 0.97
    version_of: null
    resolution_method: doi_direct_lookup
    resolvers_queried:
      - {registry: crossref, verdict: hit, at: "2026-06-30T00:00:00Z", version: "crossref-api-2026-05"}
      - {registry: openalex, verdict: hit, at: "2026-06-30T00:00:01Z", version: "openalex-2026-06"}
    retraction_status: ok
    access: {full_text_status: open, full_text_url: "https://academic.oup.com/brain/...", license: "CC-BY"}
    dedup_key: "doi:10.1093/brain/awac333"
    used_by:
      - {object_type: claim, object_id: C01, relation: evidence_for}
      - {object_type: related_work, object_id: RW01, relation: imports}
    checked_at: "2026-07-06T00:00:00Z"
  - id: R015   # published version of a preprint, NOT collapsed with R016
    canonical_metadata: {title: "Plasma p-tau217 for population screening", authors: ["Ashton, Nicholas"], year: 2024, venue: "Nature Medicine", volume: null, pages: null}
    source_kind: scholarly_article
    external_ids: {doi: "10.1038/s41591-024-xxxxx", arxiv: null, openalex: "W...", s2_corpus_id: null, pmid: null, isbn: null}
    status: resolved
    confidence: 0.94
    version_of: {ref_id: R016, relation: published_as}
    resolvers_queried: [{registry: crossref, verdict: hit, at: "2026-07-01T00:00:00Z", version: "crossref-api-2026-05"}]
    retraction_status: ok
    access: {full_text_status: closed, full_text_url: null, license: null}
    dedup_key: "doi:10.1038/s41591-024-xxxxx"
    used_by: [{object_type: claim, object_id: C07, relation: evidence_for}]
    checked_at: "2026-07-06T00:00:00Z"
  - id: R041   # honest grey literature
    raw_mentions: [{text: "internal cohort SOP v3", layer: src/environment.md, locator: "Methods §2"}]
    canonical_metadata: {title: "Internal cohort SOP v3 (unpublished)", authors: ["Lab internal"], year: 2024, venue: null, volume: null, pages: null}
    source_kind: personal_communication
    external_ids: {doi: null, arxiv: null, openalex: null, s2_corpus_id: null, pmid: null, isbn: null}
    status: greylit
    greylit_type: personal_communication
    confidence: null
    version_of: null
    resolution_method: no_resolver_match_after_3_attempts
    resolvers_queried: [{registry: crossref, verdict: miss, at: "2026-07-06T00:00:00Z", version: "crossref-api-2026-05"}]
    retraction_status: not_applicable
    access: {full_text_status: unavailable, full_text_url: null, license: null}
    dedup_key: "fingerprint:internal-cohort-sop-v3::lab-internal::2024"
    used_by: [{object_type: experiment, object_id: E02, relation: setup_reference}]
    checked_at: "2026-07-06T00:00:00Z"
    notes: "Genuinely unpublished internal document; honest absence, scored equal to a resolved presence, never penalized as fabrication."
  - id: R055   # FABRICATED — only after 3-registry negative + retries
    raw_mentions: [{text: "Smith et al. 2021, DOI 10.1234/fake.5678", layer: logic/related_work.md, locator: "brief tier"}]
    canonical_metadata: {title: null, authors: ["Smith"], year: 2021, venue: null, volume: null, pages: null}
    source_kind: scholarly_article
    external_ids: {doi: "10.1234/fake.5678", arxiv: null, openalex: null, s2_corpus_id: null, pmid: null, isbn: null}
    status: fabricated
    confidence: 0.0
    version_of: null
    resolution_method: doi_direct_lookup
    resolvers_queried:
      - {registry: crossref, verdict: miss, at: "2026-07-04T00:00:00Z", version: "crossref-api-2026-05"}
      - {registry: crossref, verdict: miss, at: "2026-07-05T12:00:00Z", version: "crossref-api-2026-05"}
      - {registry: datacite, verdict: miss, at: "2026-07-06T00:00:00Z", version: "datacite-2026-06"}
      - {registry: openalex, verdict: miss, at: "2026-07-06T00:00:05Z", version: "openalex-2026-06"}
    retraction_status: not_applicable
    access: {full_text_status: unavailable, full_text_url: null, license: null}
    dedup_key: "doi:10.1234/fake.5678"
    used_by: [{object_type: related_work, object_id: RW09, relation: baseline}]
    checked_at: "2026-07-06T00:00:00Z"
    notes: "Syntactically valid DOI, but Crossref (x2 over 48h) AND DataCite AND OpenAlex all return miss — no registry ever held this record. Distinct from R058 (dead), whose registry record exists but landing page 404s."
  - id: R058   # DEAD — honest decay, NOT fabrication
    raw_mentions: [{text: "Consortium report 2015", layer: logic/related_work.md, locator: RW12}]
    canonical_metadata: {title: "ADNI consortium data-sharing report", authors: ["ADNI"], year: 2015, venue: "consortium web", volume: null, pages: null}
    source_kind: technical_report
    external_ids: {doi: "10.5555/legacy.2015", arxiv: null, openalex: "W...", s2_corpus_id: null, pmid: null, isbn: null}
    status: dead
    confidence: 0.71
    version_of: null
    resolution_method: doi_direct_lookup
    resolvers_queried:
      - {registry: crossref, verdict: hit, at: "2026-07-06T00:00:00Z", version: "crossref-api-2026-05"}
      - {registry: url_fetch, verdict: error, at: "2026-07-06T00:00:02Z", version: "http-2026"}
    retraction_status: unknown
    access: {full_text_status: unavailable, full_text_url: null, license: null}
    dedup_key: "doi:10.5555/legacy.2015"
    used_by: [{object_type: related_work, object_id: RW12, relation: bounds}]
    checked_at: "2026-07-06T00:00:00Z"
    notes: "Registry record EXISTS (Crossref hit) but landing page 404s and no archived copy located. Link-rot, not misconduct."
- **citations.yaml** (YAML/JSONL. Prose still renders normally via the inline anchor token.) — One record per citation OCCURRENCE (inline mention) in any layer. Separates the occurrence from the work and from what it supports, preserves the exact as-cited surface text at every site, and is the middle term of the round-trip invariant. Adopted from the competitor's citation_mentions but tightened to the round-trip validator.
  - fields: cite_id: string X#### — required.
ref_id: R### or null — required nullable — null only when unresolved_key is set.
unresolved_key: U### or null — for an occurrence whose work has no ref node yet.
location: {path, selector: enum{line,heading,block_id,byte_range}, value} — required — must contain the literal ref token (validator RG-2).
surface_text: string — required — the EXACT author-year/prose as rendered; the as-cited string is preserved here per occurrence, never overwritten by canonical_metadata.
citation_role: enum{background, supports_claim, motivates_gap, baseline, method_import, dataset_source, tool_source, bounds_scope, refutes} — required.
cited_for: {object_type: enum{claim,observation,gap,related_work,experiment,concept,tree_node}, object_id} — required.
polarity: enum{supports, contrasts, refutes, neutral, unknown} — required — unknown is honest.
required_strength: enum{direct, indirect, contextual, not_applicable} — required — declares how load-bearing this occurrence is, which sets the verification bar in support.yaml.
  - example: citations:
  - cite_id: X0042
    ref_id: R014
    unresolved_key: null
    location: {path: "logic/problem.md", selector: heading, value: "O2"}
    surface_text: "Janelidze et al. (2023)"
    citation_role: motivates_gap
    cited_for: {object_type: observation, object_id: O2}
    polarity: supports
    required_strength: direct
  - cite_id: X0043
    ref_id: R014
    unresolved_key: null
    location: {path: "logic/related_work.md", selector: block_id, value: RW01}
    surface_text: "Janelidze et al., 2023"
    citation_role: baseline
    cited_for: {object_type: related_work, object_id: RW01}
    polarity: supports
    required_strength: direct
- **support.yaml** (YAML.) — States exactly what each load-bearing citation occurrence is used to prove, anchored to a quote + hash in the source, with a per-edge verifier result. This is the home for per-citing-context verifiability: an inaccessible/paywalled source records `unverifiable` HERE, on this specific edge, never silently skipped. Adopted from competitor's support_edges.
  - fields: edge_id: string S### — required.
cite_id: X#### — required — must exist in citations.yaml.
ref_id: R### — required — must equal citations[cite_id].ref_id.
assertion_text: string — required — the local assertion this citation is supposed to support.
source_anchor: {locator: string|null, quote: string|null, quote_hash: string|null, granularity: enum{paper_level, section_level, figure_table_level, sentence_level}, anchor_status: enum{exact, approximate, abstract_only, no_full_text, unresolved}} — required — granularity MUST be declared so an abstract-only source is checked only at abstract granularity.
verifier_result: {status: enum{not_run, entailed, partially_supported, unsupported, contradicted, unverifiable}, confidence: float|null, verifier: string|null, verified_at: ISO8601|null, notes: string|null} — required — `unverifiable` recorded per edge when access.full_text_status blocks the declared granularity.
  - example: support:
  - edge_id: S019
    cite_id: X0042
    ref_id: R014
    assertion_text: "Prior plasma p-tau217 studies report platform-dependent diagnostic performance, motivating cross-platform comparison."
    source_anchor: {locator: "Abstract; Table 2", quote: "diagnostic accuracy varied across the 10 assays", quote_hash: "sha256:8c9d2f...", granularity: section_level, anchor_status: exact}
    verifier_result: {status: partially_supported, confidence: 0.78, verifier: "reftruth-v1:crossref+fulltext+llm-judge", verified_at: "2026-07-06T10:31:12Z", notes: "Supports platform variation; only partially supports the diagnostic-performance magnitude claimed."}
  - edge_id: S027   # paywalled, checked honestly at the only accessible granularity
    cite_id: X0055
    ref_id: R070
    assertion_text: "Ashton 2024 reports 96% specificity in a primary-care cohort."
    source_anchor: {locator: "Abstract", quote: null, quote_hash: null, granularity: abstract_only, anchor_status: abstract_only}
    verifier_result: {status: unverifiable, confidence: null, verifier: "reftruth-v1", verified_at: "2026-07-06T10:40:00Z", notes: "access.full_text_status=closed; the specific 96% figure is sentence-level and lives beyond the abstract. Recorded unverifiable for THIS edge — not counted as support and not counted as fabrication."}
- **resolution_candidates.yaml** (YAML.) — Audit sidecar recording every candidate the resolver considered per ref, with the raw metadata_match components, so anyone can recompute confidence via Protocol R from the same registry responses. Makes the resolver falsifiable and multi-candidate disambiguation transparent.
  - fields: ref_id: R### — required.
query: {title, authors[], year} — required — the normalized query built from raw_mentions.
candidates: list[{rank, doi, title_sim, author_sim, year_score, confidence, decision: enum{accepted, runner_up, rejected}}] — required — full ranked list, not just the winner.
decision_rule: string — required — which Protocol-R threshold fired.
mismatch_check: {as_cited_title_sim, as_cited_author_sim, triggered: bool} — required — the numbers behind any `mismatch` status.
  - example: candidates_log:
  - ref_id: R014
    query: {title: "head to head comparison of 10 plasma phospho tau assays in prodromal alzheimers disease", authors: ["janelidze","mattsson-carlgren"], year: 2023}
    candidates:
      - {rank: 1, doi: "10.1093/brain/awac333", title_sim: 0.99, author_sim: 0.91, year_score: 1.0, confidence: 0.97, decision: accepted}
      - {rank: 2, doi: "10.1093/brain/awad012", title_sim: 0.41, author_sim: 0.50, year_score: 1.0, confidence: 0.56, decision: rejected}
    decision_rule: "confidence 0.97 >= 0.85 AND title_sim 0.99 >= 0.80 -> accepted; margin to runner-up 0.41 >= 0.10 -> unambiguous"
    mismatch_check: {as_cited_title_sim: 0.99, as_cited_author_sim: 0.91, triggered: false}
- **Citation-anchor token (inline convention, not a new file)** (Inline markdown embedded in existing prose fields.) — Lets every layer keep writing natural author-year prose while the citation stays machine-resolvable and regex-extractable. Renders identically to a normal citation; is the surface term of the round-trip invariant.
  - fields: Grammar: `[display_text](ref:R###)` — regex `\[([^\]]+)\]\(ref:(R\d+)\)` deterministically extracts (display_text, ref_id) from any layer file. ref_id MUST exist in refs.yaml (referential integrity, deterministic) and MUST correspond to a citations.yaml occurrence at that location (RG-2).
  - example: problem.md — `**Evidence**: assays vary across platforms ([Janelidze et al., 2023](ref:R014); [Karikari et al., 2020](ref:R009)).`
related_work.md RW01 — `- **Ref**: [Janelidze et al., 2023](ref:R014)`  (refs.yaml is the single source of truth for the DOI; RW01 only points at it.)
claims.md C07 — `**Compares to**: [Ashton et al., 2024](ref:R015) primary-care cohort.`

  _Protocols:_
  - **Protocol R — Confidence scoring (pinned, recomputable)** — Every non-DOI-direct resolution, and every DOI-direct resolution's mismatch check.. 1. Normalize both cited and candidate strings: NFKD unicode fold; lowercase; strip subtitle after first ':' or ' — '; strip punctuation; collapse whitespace. Authors -> set of normalized last names (drop 'et al.', drop initials).
2. title_sim = 1 - (Levenshtein(norm_title_cited, norm_title_cand) / max(len)).
3. author_sim = Jaccard(author_set_cited, author_set_cand).
4. year_score = 1.0 if exact, 0.5 if within ±1, else 0.0.
5. confidence = 0.5*title_sim + 0.3*author_sim + 0.2*year_score.
6. Decide: confidence >= 0.85 AND title_sim >= 0.80 -> accepted (status=resolved); 0.60 <= confidence < 0.85 -> ambiguous (Protocol D); confidence < 0.60 -> reject.
7. Persist every candidate's four numbers to resolution_candidates.yaml.
    - reliability/reproducibility: Deterministic given fixed registry responses and pinned resolver version; two auditors recompute the identical 0.97. The score is never a stored opaque float — it is regenerable from candidates + query. resolver_version pins tokenizer/normalizer.
    - constraints: Ecosystem must provide: versioned, snapshot-pinnable registry APIs (Crossref, OpenAlex, DataCite, PubMed, arXiv, Semantic Scholar) and a published, versioned normalization library so title/author folding is identical across implementations.
  - **Protocol F — Fabrication vs death (three-registry gate)** — Any external id that fails to resolve, before ANY `fabricated` or `dead` status may be written.. 1. Syntactic check: is the id well-formed (DOI/arXiv/PMID grammar)? If malformed -> status=unresolved with notes, STOP (never fabricated).
2. Query primary registry. On miss/error: retry with exponential backoff, ≥3 attempts spread over a ≥24h window, to rule out transient outage.
3. If still miss, query the OTHER two of {Crossref, DataCite, OpenAlex}.
4. If a registry HAS a record but the landing URL is unreachable (incl. no Internet-Archive copy) -> status=dead.
5. If ALL THREE registries return verdict=miss (record never existed) AND id is well-formed -> status=fabricated.
6. If exactly one registry is a hit or any returns error/timeout -> status=pending (recheck next pass), NEVER fabricated.
7. Log every {registry, verdict, at, version} to refs.resolvers_queried.
    - reliability/reproducibility: A `fabricated` flag is falsifiable and reproducible: it names the three registries, timestamps, and versions; a reviewer reruns and either confirms three misses or the flag is invalid. One API hiccup cannot manufacture a misconduct signal because a single miss/error yields pending, not fabricated.
    - constraints: Ecosystem must provide: registry uptime/status endpoints (to distinguish outage from true miss), a public DOI/DataCite split map, embargo-aware negative caching, and an archival fallback (Internet Archive / Perma.cc) so link-rot is detectable as `dead`.
  - **Protocol D — Multi-candidate disambiguation** — When Protocol R yields status=ambiguous, or top-two candidates are within 0.10 confidence.. 1. Rank candidates by confidence. 2. If top margin over runner-up < 0.10 -> do NOT auto-accept; mark status=ambiguous and record both. 3. Apply tie-breakers in order: exact venue match; DOI prefix consistency with cited venue; author-affiliation overlap; publication-date vs cited year. 4. If a tie-breaker produces margin ≥ 0.10 -> accept, record the tie-breaker used. 5. Else remain ambiguous and surface for human/agent adjudication; the ambiguous status is scored as an honest presence, not a failure. 6. All candidates and the chosen rule persist to resolution_candidates.yaml.
    - reliability/reproducibility: Reproducible: the ranked candidate list plus the named tie-breaker rule lets any auditor replay the decision. Ambiguity is preserved honestly rather than forced to a false winner.
    - constraints: Ecosystem must expose affiliation and venue metadata in registry responses; a stable adjudication queue for human/agent review.
  - **Protocol M — Mismatch trigger (anti-laundering)** — After every successful resolution (incl. DOI-direct), before status is finalized as resolved.. 1. Compute title_sim and author_sim between the AS-CITED strings (raw_mentions/surface_text) and canonical_metadata. 2. If title_sim < 0.60 OR author_sim < 0.34 -> set status=mismatch (a resolved id whose metadata contradicts the citing string: likely a typo'd or wrong DOI). 3. Preserve BOTH strings: canonical_metadata never overwrites raw_mentions; citations.surface_text is untouched. 4. Record the numbers in resolution_candidates.mismatch_check. 5. A `mismatch` blocks the ref from counting as clean support until adjudicated.
    - reliability/reproducibility: Deterministic given the two strings; prevents a high-confidence mis-resolution from laundering a wrong citation into 'truth'. The as-cited string is always inspectable.
    - constraints: None beyond Protocol R's normalization library.
  - **Protocol V — Round-trip integrity validators** — On every compile/seal; blocks publication on failure.. RG-1 (set agreement): for each R###, set(refs.used_by targets) MUST equal set(citations occurrences with ref_id==R### projected to cited_for). RG-2 (token presence): for each citations occurrence, the file at location MUST contain the literal `[...](ref:R###)` token. RG-3 (support coverage): every occurrence with required_strength=direct MUST have a support.yaml edge with verifier_result.status != not_run. On any failure: the affected reference-graph metric is emitted as INVALID (not silently 0), with the specific failing R###/X#### listed.
    - reliability/reproducibility: Deterministic, reproducible grep-level check. Closes the used_by Goodhart hole: a ref cannot advertise support it never actually anchors, because used_by is DERIVED from occurrences, not asserted independently.
    - constraints: Compiler must own used_by derivation (never hand-authored); a linter that runs RG-1/2/3 as a hard gate.
  - **Protocol C — Claim-support verification (per citing context)** — For every support.yaml edge on a load-bearing occurrence.. 1. Read access.full_text_status. 2. Set max checkable granularity: open -> up to sentence_level; abstract_only -> abstract/section only; closed/unavailable -> paper_level metadata only. 3. If the assertion's needed granularity exceeds access -> verifier_result.status=unverifiable, recorded on THIS edge. 4. Else fetch source, locate quote, hash it, run entailment (registry metadata + full text + LLM judge with for/against). 5. Emit status ∈ {entailed, partially_supported, unsupported, contradicted, unverifiable} with confidence and verifier id.
    - reliability/reproducibility: Semantic-judged but auditable: quote_hash pins the evidence span; for/against judging and a named verifier minimize judge degrees of freedom; unverifiable is recorded per edge so paywalled refs cannot become a fabrication haven.
    - constraints: Ecosystem must provide: universal full-text access (the design's premise — everyone publishes openly), a stable quote-hashing scheme, and a versioned judge ensemble with a calibration set.

  _Metrics afforded:_
  - Reference resolution rate → count(status=resolved) / count(all refs), with greylit/unresolved/ambiguous reported separately as honest neutral buckets and fabricated reported as a distinct negative. [reliable-anchored]; anti-Goodhart: Padding the ledger with refs to inflate the denominator fails: every ref must be used_by a real occurrence (RG-1) present in prose (RG-2); unused refs are rejected at compile. Honest greylit/unresolved score EQUAL to resolved (never penalized), so there is no pressure to fabricate a DOI to 'complete' a ref.
  - Fabrication count → count(status=fabricated), each backed by a ≥3-registry-negative + retry trail in resolvers_queried. [reliable-anchored]; anti-Goodhart: Cannot be manufactured by a single API outage (Protocol F: one miss/error -> pending, not fabricated). Cannot be dodged by dressing fabrication as link-rot: `dead` requires a POSITIVE registry hit, which a made-up id can never produce. Split statuses mean neither direction is gameable.
  - Citation-support fidelity → share of support edges with verifier_result.status=entailed among {entailed, partially_supported, unsupported, contradicted}; unverifiable excluded from the ratio but reported as a separate honest count. [semantic-judged]; anti-Goodhart: quote_hash pins the evidence span so a 'supported' claim must point at real text; for/against judge ensemble limits degrees of freedom; paywalled/abstract-only edges are recorded unverifiable per context (not silently counted as support), so gaming via unfetchable sources is visible, not free.
  - Dedup integrity → 1 - (distinct dedup_keys mapping to the same external id / total refs); plus a version_of-linkage completeness check that no preprint↔published pair is either silently collapsed or silently duplicated. [deterministic]; anti-Goodhart: Normalization (NFKD + subtitle strip + full author set) is fixed, so authors cannot split one work into many nodes to inflate reference breadth; version_of edges make legitimate preprint/published pairs explicit rather than reward-hackable duplication.
  - Round-trip graph coverage → fraction of inline citation tokens that satisfy RG-1/RG-2/RG-3; INVALID if any fail. [deterministic]; anti-Goodhart: Because used_by is derived, not asserted, a ref cannot claim to support objects it never anchors; inflating coverage requires actually writing verifiable occurrences, which then face Protocol C.

  _Tradeoffs:_ Honest costs and residual fabrication surfaces: (1) Verification is I/O-heavy and time-relative — resolution and claim-support depend on live registries and full text, so results carry checked_at and must be re-run; a ref resolved today can rot tomorrow. Mitigation: checked_at + periodic re-verification passes; `dead` captures decay honestly. (2) The three-file split (refs/citations/support) is more machine-facing than a single table; mitigation: the inline anchor token keeps the human reading experience as plain author-year prose, and the compiler owns the derived joins so authors never hand-maintain used_by. (3) Residual fabrication surface: a sophisticated actor could cite a REAL but irrelevant DOI (passes Protocol F, fails only if the mismatch or support check catches it). Mitigation: Protocol M flags metadata divergence and Protocol C tests actual entailment against the quoted span — so a real-but-wrong citation is caught at the support layer, not the resolution layer. (4) Grey literature is a genuine soft spot: personal_communication and internal docs are unverifiable by construction; mitigation: they are typed (greylit_type), scored equal to honest presence, and explicitly barred from counting as peer-reviewed support in landscape metrics. (5) Quote_hash anchoring can be gamed by quoting real text that does not actually support the assertion; mitigation: the for/against judge ensemble evaluates entailment, not mere quote presence. (6) Cross-registry confirmation depends on registry coverage — a legitimately new/embargoed DOI absent from all three would be mislabeled; mitigation: embargo-aware negative caching + pending status + the ≥24h retry window before any fabricated verdict.

  _Open questions:_ 1. Fabrication threshold trust: three registries all missing is strong but not infinitely conclusive for very new, regional, or non-Latin-script works poorly indexed by Crossref/DataCite/OpenAlex — what fourth signal (national registries, ISSN-linked venue lookups) should raise the bar before `fabricated`? 2. Confidence weights (0.5/0.3/0.2) are defensible but not empirically calibrated — they need a labeled resolution corpus to tune, and different fields (CS-with-arXiv vs humanities-with-books) may need different weight profiles. 3. quote_hash stability across formats: the same passage in HTML vs PDF vs published-vs-preprint yields different hashes — a canonical text-extraction/normalization standard for hashing is unspecified and hard. 4. Who runs the resolver and re-verification, and how is resolver collusion (a captured resolver rubber-stamping fabricated ids) detected? Likely needs independent re-resolution / multiple resolver operators with agreement checks. 5. version_of graphs can get deep (v1 preprint -> v2 -> journal -> corrigendum); the design links pairs but does not specify canonical-version selection when a metric needs 'the' work. 6. Semantic claim-support judging remains the least deterministic link; the calibration set and judge-ensemble governance are assumed but not designed here.

  _Changes from critique:_ Addressed all six critique points structurally, not defensively. (1) Split `dead_or_fabricated` into two statuses: `dead` (was registered, now unreachable — honest decay) and `fabricated` (never existed anywhere — misconduct). `fabricated` can ONLY be asserted after Protocol F: retry-with-backoff across a ≥24h window AND a confirmed negative from Crossref AND DataCite AND OpenAlex; a single 404, a transient outage, a Crossref/DataCite split, or an embargoed new DOI resolves to `pending` or `dead`, never `fabricated`. (2) Pinned the confidence function in Protocol R: confidence = 0.5·title_sim + 0.3·author_sim + 0.2·year_score, where title_sim = 1 − normalized_Levenshtein on subtitle-stripped NFKD-folded titles, author_sim = Jaccard over normalized last-name sets, year_score ∈ {1.0 exact, 0.5 ±1yr, 0.0 else}; accept ≥0.85 (and title_sim ≥0.80), ambiguous 0.60–0.85, reject <0.60 — all recomputable from resolution_candidates.yaml. (3) Replaced the colliding fingerprint: dedup_key normalization now specifies lowercase + NFKD diacritic fold + subtitle strip + punctuation/whitespace collapse + full author last-name set (no first-author-only, no et-al truncation), and preprint↔published are NEVER collapsed — they are distinct R### nodes joined by a typed `version_of` edge. (4) Wired the `mismatch` status to an automatic trigger: after DOI-direct resolution, if title_sim <0.60 or author_sim <0.34 between as-cited and canonical, status flips to `mismatch` (a resolved id whose metadata contradicts the citing string — likely a typo'd/wrong DOI). The as-cited string is ALWAYS preserved in citations.surface_text and refs.raw_mentions; canonical_metadata never overwrites it. Multi-candidate disambiguation is shown explicitly in Protocol D. (5) Added the round-trip invariant as validators RG-1/RG-2/RG-3 with a hard failure behavior (metric = INVALID, not silently zero): every R### in ARA prose ⇔ citations.yaml occurrence ⇔ refs.used_by must agree three ways. (6) Made `unverifiable` a per-citing-context value on support.yaml.verifier_result.status, recorded on the specific edge and never skipped; abstract-only access permits abstract-granularity checks but forces granularity to be declared, so paywalled refs cannot become a fabrication haven.

  _Adopted from competitor:_ The single biggest steal is the competitor's three-way separation of cited-work / citation-occurrence / support-edge. My original design overloaded refs.yaml with both raw_mentions and used_by, which is exactly what let critique #4 and #5 land (no place to preserve as-cited context per occurrence; no enforceable round-trip). I adopted (a) `citations.yaml` as a first-class occurrence table (their citation_mentions.yaml) with per-occurrence surface_text, citation_role, polarity, and required_strength; (b) `support.yaml` (their support_edges.yaml) with a quote + quote_hash + locator source_anchor and a per-edge verifier_result, which is the correct home for critique #6's per-citing-context unverifiable recording; (c) their resolver_evidence.metadata_match breakdown {title_similarity, author_overlap, year_match} — I made it the ACTUAL scoring inputs rather than post-hoc decoration; (d) their explicit source_kind enum so datasets/software/webpages/protocols are typed, not forced into a scholarly-article mold; (e) their granularity enum {paper|section|figure_table|sentence} on support edges, which is what makes abstract-only access honestly checkable at the right resolution.

  _Why it wins:_ The competitor's resolution_status enum is {verified | unresolved | grey_lit | retracted | not_applicable} — it has NO fabrication status at all, so it literally cannot flag a made-up DOI; it can only leave it `unresolved`, which collapses honest link-rot, embargoed-DOI, and outright fabrication into one indistinguishable bucket. That fails the core Class-B mandate ("treats fabrication as a first-class status"). My design carries `fabricated` AND `dead` as distinct statuses with a specified cross-registry confirmation gate, so fabrication is both catchable and un-manufacturable. Second, the competitor states match_confidence: 0.97 but never pins the function — same hollow-auditability hole the reviewer nailed me for; I ship the exact formula, thresholds, and normalization so any auditor recomputes it from the raw registry responses. Third, the competitor never specifies dedup normalization or how preprint/published versions relate — I define NFKD/subtitle/diacritic normalization and an explicit `version_of` edge that refuses silent collapse. Fourth, I add the bidirectional round-trip validator the competitor's design lacks, closing the used_by/coverage Goodhart hole. Net: I keep their superior separation-of-concerns architecture but I am the only one that satisfies the reliability + protocol + failure-mode half of the mandate.


---


## REGISTRY — Registry / accession manifest

_Class B — anchor-dependent (reliability + protocol)_


**Judge rationale:** All four proposals share the same architecture (manifest sidecar + structured access tiers + claim→outcome links + hashed/snapshotted verification records), so I ranked on how concretely each delivers the THREE mandated pillars — a machine-readable manifest, a structured access-tier representation, and a real claim→registered-outcome JOIN KEY with deviation modeling and a reliable resolver protocol — and on honesty about fabrication surfaces.

The two Sonnet proposals (#2, #3) win because they deliver the actual gap: an explicit, typed claim→SPECIFIC-outcome edge with a first-class divergence/correspondence vocabulary. #2's `correspondence` enum (outcome_switched, outcome_dropped_silently) is the most direct encoding of the outcome-switching phenomenon pub-bias metrics detect, with verbatim immutable outcome text and genuinely operational per-tier verification semantics (open=200 liveness, controlled=DAC exists, embargo=date logic). #3 matches it on the join edge and beats it on engineering discipline: reusable embedded types, append-only verification_history, a real cadence field, a coverage requirement (every claim exactly once) that structurally blocks hiding a claim from the table, and rare honesty that PROSPERO has no API (`unverifiable_no_api`). Both are explicit that a well-formed fabricated CRD/GSE/NCT passes format checks and is only defeated by resolution + topic-match — the correct Class-B framing.

They edge out the two gpt-5.5-codex proposals on the single most important axis, the join key. #1 links claims to REGISTRATIONS (claims_supported at the record level), not to specific registered OUTCOMES — coarser than the gap requires — though it does deliver a fully concrete access_tiers schema and a good honest-absence worked example. #0 has the richest outcome ledger (planned_direction, registered_before_first_enrollment) and the field's best provenance feature (anchor_type distinguishing author_statement from verifier_result, which defeats "the ARA claims verification happened"), plus a strong absence_state taxonomy — but it is truncated exactly on the mandate's 2nd and 3rd pillars (structured access tiers, deviation representation, cadence), so I cannot credit schema I cannot see, and it is the heaviest to implement.

Shared weakness across all four, and the improvement I forced hardest on both winners: the semantic correspondence/divergence label is the load-bearing field for the target metric, yet every design drops it into a machine-readable slot with no assessor independent of the author, no confidence/inter-rater constraint, and similarity scores (fingerprint_match_score, topic_match.score) computed by unpinned algorithms. That is the biggest un-closed Goodhart hole and the difference between a real Class-B resolver and one that self-certifies.


### Finalist A (refined)

> _Judge critique it answered:_ Proposal #2 (Registry Join Layer, Sonnet 5) has the single best affordance in the field: `claim_registry_links.yaml` with a `correspondence` enum (matches / partial_match / outcome_switched / outcome_added_not_registered / outcome_dropped_silently) is the most on-target encoding of the outcome-switching phenomenon that publication-bias metrics actually detect, and the deterministic/semantic split plus the not-found-vs-unreachable distinction is textbook Class-B honesty. But it has a load-bearing hole you must close:

1. WHO assigns `correspondence`? The whole design brags that it keeps the deterministic half separate from the irreducibly semantic half — then it drops the most semantic judgment in the artifact (outcome_switched vs matches) into a machine-readable field with NO assessor identity, NO confidence, NO independence constraint, and NO adjudication protocol. Nothing stops the authoring compiler from labeling an outcome_switched case as `matches`; the metric reads "compliant" and the Goodhart hole is total. Fix: `correspondence` must carry an assessor id that is provably NOT the authoring pipeline (separation of duties), a confidence, and ideally a two-assessor/IRR requirement — otherwise it is self-certified and worthless as an anti-gaming signal.

2. `fingerprint_match_score: 0.94` is an undefined float. What function produces 0.94 vs 0.99? No tokenization, no field set, no threshold mapping to resolved_match/resolved_mismatch. An unpinned similarity score is not reproducible, therefore not Class B — it is theater dressed as a field. Pin the algorithm (fields hashed, normalizer, embedding model+version or exact token-overlap formula) and the decision threshold.

3. The design promises "field comparison between a claim's quantity and a verbatim-snapshotted registered outcome," but the registered-outcome side stores `registered_outcome_text` (prose) and the claim side stores `reported_result_quantity_ref` — with no structured registered DIRECTION or MEASURE to compare against. Direction-switching (registered "superiority" → reported "no difference") is the core pub-bias signal and it cannot fire without a machine-comparable registered `planned_direction`/`measure`. Proposals #0/#1 carry `planned_direction`; you must add it or your headline "read it, don't infer it" comparison is still prose-diffing.

4. `snapshot_ref` is asserted immutable, but the shown `verification` block hashes nothing — it stores a path, not a content hash of the cached snapshot. "Verbatim, immutable once set" is unenforceable if the cached HTML can be silently edited. Add a content hash of the snapshot payload (as #0/#3 do) and state that re-fetch recomputation flips `result` on mismatch.

5. Cadence lives in your prose ("re-check cadence, pinned snapshots") but there is no `next_check_due`/cadence FIELD in the schema shown. The mandate demands cadence; make it a typed field, not narration.

6. Genre-applicability gap: `accession_id: not_specified` handles "claims a registration but no ID," but there is no `not_applicable_to_genre` gate saying this work is not the kind that should register (a secondary reanalysis needn't have PROSPERO). Without it a metric can penalize legitimately unregisterable work, creating fabrication pressure to invent a registration. Add an eligibility flag.

**The Registry Join Layer v2: pinned-resolver accession manifest + coverage-complete claim→outcome links with a first-class selective-reporting ledger**  ·  _source: claude-opus-4-8 (finalist B)_

Registrations and accessions are real, resolvable identifiers (CRD#, NCT#, GSE#, phs#) trapped in prose, unlinked to any claim, and never checked against the registry that issued them — so a well-formed fake passes exactly like a real one, and outcome-dropping hides in the gap between what was registered and what was reported. This design promotes every registry-facing fact to a typed sidecar (registry/manifest.yaml) with an immutable verbatim snapshot of each registered outcome, and adds a claim_links.yaml join table whose coverage rule (every C## appears exactly once) means no claim can silently escape the join. The five holes the reviewer named are closed structurally: topic-match is computed by a pinned, versioned resolver with a deterministic formula and a fixed match/ambiguous threshold — not a free-text method string; verification is split into author-attested vs independent-resolver roles with an explicit reliability tier (API > structured-fetch > human-attested) so a PROSPERO attestation is visibly weaker than a GEO eutils lookup; a claim with no registration carries an eligibility flag that separates legitimately-unregistered from expected-but-absent; selective reporting becomes a first-class DERIVED ledger (every registered outcome gets a reported/unreported status by deterministic set-difference) instead of a join the metric must reinvent; and the irreducibly semantic correspondence/divergence label is moved out of the machine field into a Class-C assessment block carrying an attestor id distinct from the compiler, an assessor kind, confidence, and for/against evidence. The result gives a metric a real JOIN KEY into external registries whose reliability, freshness, and independence are all machine-readable and auditable.

- **registry/manifest.yaml** (YAML, top-level key `entries:`, list of typed records) — Canonical, deduplicated list of every external registry entry or accession the ARA depends on. One record per unique real-world identifier. Other layers reference an entry by id, never by re-typing the accession string. Prose in environment.md/dataset.md may narrate an entry but MUST reference it by id and is scored for agreement against this file.
  - fields: schema_version: string — required.
entries: list — required (empty list is the honest-absence value for a paper with no registrations, distinct from a not_yet_swept state which is expressed by verification.method=not_yet_attempted).
  id: string `REG{NN}` — required — stable local id, never reused.
  registry: enum{prospero, clinicaltrials_gov, isrctn, anzctr, eudract, who_ictrp, osf_registries, aspredicted, geo, sra, ena, arrayexpress, dbgap, ega, proteomexchange, addgene, zenodo, figshare, dryad, datacite, other:<free>} — required.
  kind: enum{study_registration, protocol_registration, data_accession, code_archive, biological_material, other} — required.
  accession: string exactly as issued, or `not_specified` (honest-absence: paper asserts a registration exists but gives no id — flagged for follow-up, never silently dropped) — required.
  url: string canonical resolvable URL, or derivable-from-template — required-or-not_specified.
  registered_title: string as filed — required-or-not_specified.
  registered_date: ISO date — required-or-not_specified.
  registered_by: enum{authors, third_party, unknown} — required.
  prospective_or_retrospective: enum{prospective, retrospective, not_specified} — required (was it filed before enrollment/data collection).
  status: enum{prospective, retrospective, completed, ongoing, withdrawn, unknown} — required.
  registered_outcomes: list of {outcome_id, type: enum{primary,secondary,exploratory}, timepoint, registered_outcome_text: VERBATIM quote captured at first verification and IMMUTABLE once set, text_hash: sha256} — required (empty list for pure data accessions). A later registry edit is captured as a NEW dated snapshot + new verification_history row, never an overwrite.
  access: list of <Access-tier object> — required (per-component: one entry can carry an open processed matrix AND a controlled raw-reads slice).
  verification: <Verification-record object> (latest) — required.
  verification_history: list of <Verification-record object>, append-only, never overwritten — required.
  provenance: {source_anchor: quote+locator, extracted_by: enum{compiler, human}} — required.
  - example: schema_version: "2.0"
entries:
  - id: REG01
    registry: prospero
    kind: study_registration
    accession: "CRD420261327845"
    url: "https://www.crd.york.ac.uk/prospero/display_record.php?ID=CRD420261327845"
    registered_title: "Diagnostic accuracy of plasma p-tau217, p-tau181, p-tau231 across the AD continuum: a network meta-analysis"
    registered_date: "2025-11-03"
    registered_by: authors
    prospective_or_retrospective: prospective
    status: completed
    registered_outcomes:
      - outcome_id: PRIMARY-1
        type: primary
        timepoint: cross-sectional
        registered_outcome_text: "Diagnostic accuracy (sensitivity/specificity/AUC) of plasma p-tau217 vs p-tau181 vs p-tau231 for amyloid-beta positivity"
        text_hash: sha256:aa11...
      - outcome_id: SECONDARY-1
        type: secondary
        timepoint: cross-sectional
        registered_outcome_text: "Incremental AUC of p-tau217/Abeta42 ratio over single-analyte assays"
        text_hash: sha256:bb22...
      - outcome_id: SECONDARY-2
        type: secondary
        timepoint: cross-sectional
        registered_outcome_text: "Subgroup accuracy by APOE-e4 carrier status"
        text_hash: sha256:cc33...
    access:
      - {component: "included-study extraction table", tier: open, mechanism: public_url, gatekeeper: not_applicable, embargo_until: null, license: "CC-BY-4.0"}
    verification:
      role: independent_resolver
      verified: true
      reliability_tier: tier_2_human_attested
      method: manual_registry_check
      verified_at: "2026-07-01T00:00:00Z"
      verified_by: "seal-resolver-pool/human-reviewer-CO+human-reviewer-JT"
      registry_response_hash: sha256:8f1e0c9c...
      snapshot_ref: "registry/snapshots/CRD420261327845_2026-07-01.html"
      result: match
      topic_match: {scorer_id: "lexical-jaccard-v1", score: 0.81, band: match}
      notes: "PROSPERO has no public API (unverifiable_no_api for tier_0); two independent reviewers attested the fetched page."
      next_check_due: "2027-01-01"
    verification_history:
      - {role: author_attested, verified: false, reliability_tier: attested_unverified, method: not_yet_attempted, verified_at: null, verified_by: "compiler", result: not_assessed, topic_match: null, notes: "author claim only"}
      - {role: independent_resolver, verified: true, reliability_tier: tier_2_human_attested, method: manual_registry_check, verified_at: "2026-07-01T00:00:00Z", verified_by: "human-reviewer-CO+human-reviewer-JT", registry_response_hash: sha256:8f1e0c9c..., result: match, topic_match: {scorer_id: lexical-jaccard-v1, score: 0.81, band: match}}
    provenance:
      source_anchor: "src/environment.md « prospectively registered on PROSPERO (CRD420261327845) »"
      extracted_by: compiler
- **Access-tier object (embedded, reused across manifest entries and data/dataset.md descriptors)** (YAML/JSON typed object, embedded) — Replaces the prose sentence ('processed data open; raw reads controlled via dbGaP') with a typed, per-component, independently liveness-checkable object. Per-component (adopted from competitor) because one accession routinely mixes tiers.
  - fields: component: string naming the exact slice ('raw FASTQ', 'processed count matrix', 'individual-level phenotypes') — required.
tier: enum{open, registered_access, controlled_access, embargoed, restricted_by_agreement, not_available, not_applicable} — required, no default.
mechanism: enum{public_url, api_key_required, dbgap_dac_approval, ega_dac_approval, data_use_agreement, embargo_until_date, institutional_review_required, application_review, paywall, none, not_specified} — required.
gatekeeper: string or not_applicable — required.
embargo_until: date or null — required (null = no embargo; distinct from not_specified).
license: SPDX identifier or not_specified — required.
access_procedure_ref: URL/DOI of the DAC or request process, or not_specified — required.
  - example: access:
  - component: "processed count matrix (supplementary)"
    tier: open
    mechanism: public_url
    gatekeeper: not_applicable
    embargo_until: null
    license: "CC-BY-4.0"
    access_procedure_ref: "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE307990"
  - component: "raw sequencing reads (FASTQ)"
    tier: controlled_access
    mechanism: dbgap_dac_approval
    gatekeeper: "dbGaP Data Access Committee"
    embargo_until: null
    license: "dbGaP Data Use Certification"
    access_procedure_ref: "https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?study_id=phs002345.v1.p1"
- **Verification-record object (embedded, reused; append-only into verification_history)** (YAML/JSON typed object, embedded) — Turns 'looks real' into 'is real, is about this paper, its access is as declared — here is the dated, hashed, re-checkable, INDEPENDENTLY-produced evidence.' Carries the two critique-critical discriminators: role (who produced it) and reliability_tier (how strong the channel is).
  - fields: role: enum{author_attested, independent_resolver} — required. Only independent_resolver records are load-bearing for scoring; author_attested is a proposal, never credited as verification.
verified: bool — required.
reliability_tier: enum{tier_0_api, tier_1_structured_fetch, tier_2_human_attested, tier_3_unverifiable, attested_unverified} — required. Each registry has a MAX attainable tier fixed in resolvers.lock (e.g. prospero caps at tier_2_human_attested; geo/clinicaltrials_gov/datacite reach tier_0_api).
method: enum{api_lookup, structured_fetch, manual_registry_check, doi_resolution, unverifiable_no_api, not_yet_attempted} — required.
verified_at: ISO8601 or null (null iff verified=false) — required.
verified_by: string resolver-id or reviewer-id(s) — required if verified=true; MUST NOT equal provenance.extracted_by for the record to count.
registry_response_hash: sha256 of the raw fetched record, or null — required.
snapshot_ref: relative path into registry/snapshots/, or null — required (the byte-for-byte cache the next resolver re-hashes).
result: enum{match, mismatch, not_found, registry_unreachable, ambiguous, not_assessed} — required; not_assessed is the honest value when verified=false.
topic_match: <TopicMatch object> or null — required whenever kind in {data_accession, study_registration} and result=match.
notes: string or not_specified — required.
next_check_due: date — required if status=ongoing OR any access.tier=embargoed (so the embargo lapse can be re-checked), optional otherwise.
  - example: verification:
  role: independent_resolver
  verified: true
  reliability_tier: tier_0_api
  method: api_lookup
  verified_at: "2026-07-01T00:00:00Z"
  verified_by: "ncbi-eutils-resolver-v1"
  registry_response_hash: sha256:1a2bff...
  snapshot_ref: "registry/snapshots/GSE307990_2026-07-01.json"
  result: match
  topic_match: {scorer_id: "struct-field-eq-v1", score: 1.0, band: match}
  notes: "eutils esummary: series public, organism Homo sapiens, DLPFC, N=31 matches dataset.md."
  next_check_due: "2027-07-01"
- **TopicMatch object + registry/resolvers.lock (pinned scorer registry)** (TopicMatch: embedded object. resolvers.lock: YAML, checked into the ecosystem's shared tooling repo, referenced by hash.) — Closes critique #1. Replaces the free-text `method` string with a versioned scorer id whose formula/model and thresholds are pinned in resolvers.lock, so two independent resolvers compute the SAME score and the same match/ambiguous/mismatch band. A metric thresholds on a specification, not on noise.
  - fields: TopicMatch:
  scorer_id: enum keyed into resolvers.lock (e.g. lexical-jaccard-v1, struct-field-eq-v1, embed-e5-large-v2) — required.
  score: float [0,1] — required.
  band: enum{match, ambiguous, mismatch} — required — DERIVED, not free-typed: band = match iff score >= scorer.match_threshold; ambiguous iff scorer.ambiguous_low <= score < scorer.match_threshold; else mismatch.
  recompute_tolerance_ok: bool — required — true iff an independent resolver reproduced score within scorer.tolerance.
resolvers.lock (per scorer):
  scorer_id: string.
  algorithm: enum{jaccard_token_overlap, structured_field_equality, cosine_embedding}.
  spec: for jaccard → {normalization: lowercase+NFKC, stopwords: 'nltk-en-2024', stemming: none, token_fields: [registered_title, condition_keywords], compare_against: [PAPER.md/title, PAPER.md/keywords], formula: '|A∩B|/|A∪B|'}; for cosine_embedding → {model: 'e5-large-v2', weights_sha256: ..., input_a: registered_title, input_b: PAPER.md/abstract}.
  match_threshold: float; ambiguous_low: float; tolerance: float.
  - example: # resolvers.lock
scorers:
  - scorer_id: lexical-jaccard-v1
    algorithm: jaccard_token_overlap
    spec:
      normalization: "lowercase+NFKC"
      stopwords: "nltk-en-2024"
      stemming: none
      token_fields: [registered_title, condition_keywords]
      compare_against: ["PAPER.md/title", "PAPER.md/keywords"]
      formula: "|A∩B| / |A∪B|"
    match_threshold: 0.70
    ambiguous_low: 0.40
    tolerance: 0.00   # deterministic, must reproduce exactly
  - scorer_id: struct-field-eq-v1
    algorithm: structured_field_equality
    spec: {compare_fields: [organism, tissue, sample_n], source_a: registry_record, source_b: dataset.md}
    match_threshold: 1.0
    ambiguous_low: 0.5
    tolerance: 0.0
- **registry/claim_links.yaml** (YAML, top-level key `links:`, list of typed records; authoritative (claims.md renders one line from it).) — The missing JOIN KEY. Ties a specific C## claim to a specific registered outcome_id inside a specific REG##. Coverage rule: EVERY C## in claims.md appears exactly once (a claim silently missing is a coverage failure, not honest absence). Closes critique #2 by carrying a registration_expectation flag so `registry_id: null` no longer collapses 'not that kind of claim' with 'should be registered and silently isn't'.
  - fields: schema_version: string — required.
links: list — required, EXACTLY one entry per C## in claims.md.
  claim_id: string `C##` fk into claims.md — required.
  registry_id: string `REG##` fk into manifest.yaml, or null — required.
  registered_outcome_id: string fk into that entry's registered_outcomes, or null — required.
  link_type: enum{tests_primary_outcome, tests_secondary_outcome, tests_exploratory_outcome, reports_data_accession, uses_code_archive, none} — required.
  registration_expectation: enum{expected_registered, expected_but_absent, not_expected_background, not_expected_methods, not_expected_secondary_analysis, not_expected_incidental} — required. This is the critique-#2 fix: expected_but_absent is the RED FLAG state (a claim that should map to a registered outcome but does not); the not_expected_* values are legitimate unregistered claims. Author-declared but cross-checkable (see selective-reporting protocol): a claim tagged not_expected_background that carries a primary efficacy quantity is auto-flagged for review.
  reported_quantity_ref: fk into quantities.yaml — the value in THIS paper answering the outcome — or not_specified.
  correspondence: <CorrespondenceAssessment object> or null — required whenever registry_id is non-null.
  provenance: {extracted_by: enum{compiler, human}, source_anchor: string} — required.
  - example: schema_version: "2.0"
links:
  - claim_id: C04
    registry_id: REG01
    registered_outcome_id: PRIMARY-1
    link_type: tests_primary_outcome
    registration_expectation: expected_registered
    reported_quantity_ref: Q17
    correspondence: {see CorrespondenceAssessment example}
    provenance: {extracted_by: compiler, source_anchor: "claims.md#C04"}
  - claim_id: C09
    registry_id: null
    registered_outcome_id: null
    link_type: none
    registration_expectation: not_expected_methods
    reported_quantity_ref: not_specified
    correspondence: null
    provenance: {extracted_by: compiler, source_anchor: "claims.md#C09 (QC threshold description)"}
  - claim_id: C12
    registry_id: REG01
    registered_outcome_id: null
    link_type: none
    registration_expectation: expected_but_absent   # RED FLAG: reports an APOE subgroup effect that maps to SECONDARY-2 but authors did not link it
    reported_quantity_ref: Q31
    correspondence: null
    provenance: {extracted_by: human, source_anchor: "claims.md#C12"}
- **CorrespondenceAssessment object (embedded in claim_links, Class C)** (YAML/JSON typed object, embedded) — Closes critiques #4 and #6. Splits the machine-comparable prefilter from the irreducibly semantic label. The semantic label (matches / outcome_switched / redefined ...) no longer sits naked in a machine field: it carries an attestor id DISTINCT from the compiler, an assessor kind, confidence, and for/against evidence, and a disclosed/undisclosed flag so a DISCLOSED deviation (fine) is separated from an UNDISCLOSED one (the red flag).
  - fields: deterministic_prefilter: {quantity_match: enum{value_within_registered_ci, value_outside_registered_ci, metric_type_matches, metric_type_differs, incomparable, no_registered_metric}, computed_by: resolver_id, registered_text_hash: sha256 of the outcome text this was judged against} — required. This part is reproducible.
label: enum{matches, partial_match, outcome_switched, outcome_added_unregistered, outcome_dropped, outcome_redefined, timepoint_changed, direction_flipped, not_yet_assessable, not_applicable} — required. Semantic; never author-set alone.
attestor_id: string — required — MUST differ from claim_links.provenance.extracted_by and from manifest provenance.extracted_by. If they are equal the assessment is treated as attested_unverified and not credited.
assessor_kind: enum{human_reviewer, judge_ensemble} — required.
ensemble: {n_judges: int, model_ids: list, agreement: float} or null — required if assessor_kind=judge_ensemble.
confidence: float [0,1] — required.
evidence_for: list of source_anchors supporting the label — required (may be empty only if label=not_yet_assessable).
evidence_against: list of source_anchors — required (empty is honest).
disclosed: enum{disclosed_in_paper, undisclosed, not_applicable} — required; disclosure_anchor: string or null.
  - example: correspondence:
  deterministic_prefilter: {quantity_match: metric_type_matches, computed_by: "struct-field-eq-v1", registered_text_hash: sha256:aa11...}
  label: outcome_redefined
  attestor_id: "seal-judge-ensemble-v2"
  assessor_kind: judge_ensemble
  ensemble: {n_judges: 3, model_ids: ["opus-4-8","gpt-5.4","gemini-3"], agreement: 0.67}
  confidence: 0.62
  evidence_for: ["registry PRIMARY-1 says 'amyloid-beta positivity'; paper reports accuracy for 'amyloid OR tau PET positivity' (broadened endpoint)"]
  evidence_against: ["paper Methods §2.3 notes the endpoint change explicitly"]
  disclosed: disclosed_in_paper
  disclosure_anchor: "src/methods.md §2.3 « we broadened the reference standard to ... »"
- **registry/outcome_coverage.yaml (DERIVED, regenerable)** (YAML, top-level key `outcomes:`; carries generator provenance so it is auditable and never hand-edited.) — Closes critique #3. Makes 'registered-but-unreported outcomes' — the classic selective-reporting signal — a first-class READABLE record instead of a set-difference the metric must reinvent. Deterministically generated from the verified manifest + claim_links; regenerable and hash-stamped so it can be recomputed and diffed.
  - fields: generated_from: {manifest_hash: sha256, claim_links_hash: sha256, resolvers_lock_hash: sha256, generated_at: ISO8601, generator_id: string} — required.
outcomes: list — one row per registered outcome across ALL entries whose latest verification.result=match (unverified registrations are excluded and listed under excluded_unverified).
  registry_id, outcome_id, type, text_hash — required.
  reported: bool — required (is it linked by >=1 claim_links row?).
  linked_claims: list[C##] — required (empty if unreported).
  status: enum{reported, unreported_undisclosed, unreported_disclosed, not_yet_assessable} — required — DERIVED: reported if linked; else unreported_disclosed iff a disclosure anchor is present in the paper (a not_expected_* / disclosed drop), else unreported_undisclosed (the red flag).
  disclosure_anchor: string or null — required.
reported_not_registered: list of {claim_id, reason} — claims whose link_type/correspondence.label = outcome_added_unregistered (reported endpoint with no registration).
excluded_unverified: list[registry_id] — registrations whose outcomes are not counted because verification is weaker than tier_1 or result != match (so selective-reporting math is never computed off unresolved records).
  - example: generated_from: {manifest_hash: sha256:dd44..., claim_links_hash: sha256:ee55..., resolvers_lock_hash: sha256:ff66..., generated_at: "2026-07-06T09:00:00Z", generator_id: "coverage-gen-v1"}
outcomes:
  - {registry_id: REG01, outcome_id: PRIMARY-1, type: primary, text_hash: sha256:aa11..., reported: true, linked_claims: [C04], status: reported, disclosure_anchor: null}
  - {registry_id: REG01, outcome_id: SECONDARY-1, type: secondary, text_hash: sha256:bb22..., reported: true, linked_claims: [C06], status: reported, disclosure_anchor: null}
  - {registry_id: REG01, outcome_id: SECONDARY-2, type: secondary, text_hash: sha256:cc33..., reported: false, linked_claims: [], status: unreported_undisclosed, disclosure_anchor: null}   # APOE subgroup registered, never reported, no disclosure -> selective-reporting signal
reported_not_registered: []
excluded_unverified: []

  _Protocols:_
  - **Independent resolution & verification (separation of duties)** — Every entry in manifest.yaml, at compile time and on cadence. Closes critique #4.. 1. Compiler MAY emit an author_attested Verification-record (role=author_attested, reliability_tier=attested_unverified, result=not_assessed). This is a proposal only and is NEVER credited as verification. 2. An INDEPENDENT resolver (verified_by != provenance.extracted_by) fetches the live registry, writes the raw bytes to registry/snapshots/<acc>_<date>.{json,html}, computes registry_response_hash over those bytes, computes topic_match via the pinned scorer, sets result, and APPENDS a role=independent_resolver record to verification_history (never overwrites). 3. The resolver assigns reliability_tier from resolvers.lock: tier_0_api if the registry exposes a machine API it used (geo/eutils, clinicaltrials_gov API, datacite); tier_1_structured_fetch for deterministic HTML parse+hash; tier_2_human_attested for two-reviewer manual attestation (prospero, aspredicted); unverifiable_no_api when no channel exists yet. 4. On re-check, a fresh independent resolver re-fetches, re-hashes, and if the new hash != stored hash OR fields changed, it FLIPS result to mismatch/registry_unreachable and appends a new row — the metric reads the latest row. 5. next_check_due drives cadence.
    - constraints: Reliability/reproducibility: result and registry_response_hash are load-bearing ONLY on independent_resolver records; scoring ignores author_attested. Ecosystem must provide: a resolver pool whose identity is verifiably distinct from the authoring pipeline (signed resolver ids), a snapshot store, and resolvers.lock pinned by hash. Cadence: tier_0 monthly, tier_1 quarterly, tier_2 (human) semi-annual or on-demand; embargoed access re-checked at embargo_until.
  - **Verification-reliability tiering & metric discount** — Any metric that rests on a correspondence/divergence/selective-reporting claim. Closes critique #5.. 1. resolvers.lock fixes each registry's MAX attainable tier (prospero -> tier_2_human_attested; geo/clinicaltrials_gov/datacite -> tier_0_api). 2. A metric consuming a verified fact reads reliability_tier and applies a published discount weight w(tier): tier_0_api=1.0, tier_1_structured_fetch=0.85, tier_2_human_attested=0.6, tier_3_unverifiable/attested_unverified=0.0. 3. A divergence or selective-reporting signal resting on a tier_2 PROSPERO attestation is reported WITH its tier and enters any aggregate at its discounted weight, so it is never presented as equally reliable to an eutils lookup.
    - reliability/reproducibility: The tier is a property of the channel, not the finding, so it is reproducible. The weights w(tier) are published constants, not per-resolver choices. Ecosystem must maintain resolvers.lock and the weight table as versioned, hash-referenced artifacts so two scorers apply identical discounts.
    - constraints: PROSPERO/AsPredicted human attestation requires two named reviewers whose ids differ from the compiler; unschedulable at full scale, so tier_2 findings are batched and their lower cadence is itself recorded (verified_at age is a readable freshness signal).
  - **Topic-match scoring (pinned & reproducible)** — Whenever result=match must certify the record is about THIS paper. Closes critique #1.. 1. Resolver selects the scorer_id appropriate to kind (struct-field-eq-v1 for omics accessions with structured metadata; lexical-jaccard-v1 or embed-e5-large-v2 for title/keyword registrations). 2. It computes score by the exact formula/model+weights pinned in resolvers.lock. 3. band is DERIVED from the scorer's match_threshold / ambiguous_low — never free-typed. 4. A second resolver recomputes; recompute_tolerance_ok = |score2 - score| <= scorer.tolerance (0 for deterministic scorers).
    - reliability/reproducibility: Deterministic scorers (jaccard, field-equality) reproduce exactly; embedding scorers pin model weights_sha256 so cosine is bit-stable. Ecosystem must host the pinned stopword list, embedding weights, and thresholds under content hashes. A metric thresholds on band, which is a function of a pinned spec, not on a free-text description.
    - constraints: Embedding scorers require reproducible inference (fixed weights, deterministic kernels). Where that is not guaranteed, fall back to the deterministic lexical scorer and record recompute_tolerance_ok=false to flag non-reproducibility rather than hide it.
  - **Selective-reporting derivation** — To surface registered-but-unreported outcomes. Closes critique #3, interacts with #2.. 1. Restrict to entries whose latest verification.result=match AND reliability_tier >= tier_1 (weaker/unresolved go to excluded_unverified — no selective-reporting math on unverified records). 2. For each registered_outcome, set reported = (>=1 claim_links row references it). 3. status = reported if linked; else scan the paper for a disclosure anchor -> unreported_disclosed; else unreported_undisclosed. 4. Cross-check the eligibility flag: any claim_links row with registration_expectation=not_expected_* whose reported_quantity_ref carries a primary/secondary-type quantity that field-matches an UNLINKED registered primary/secondary outcome is auto-flagged (this is the anti-gaming guard on critique #2's flag). 5. Emit reported_not_registered from correspondence.label=outcome_added_unregistered.
    - reliability/reproducibility: Fully deterministic given (manifest, claim_links, resolvers.lock); generated_from hashes make the output regenerable and diffable. Any human editing outcome_coverage.yaml is detectable because its content will not match a regeneration from the stamped inputs.
    - constraints: Correct classification of unreported_disclosed depends on the paper's disclosure being anchorable; if the disclosure exists but is not anchored, the row stays unreported_undisclosed until an anchor is added — biasing toward flagging, never toward hiding.
  - **Correspondence assessment (Class C, assessor-independent)** — To label whether a reported result actually corresponds to its registered outcome, and whether any deviation was disclosed. Closes critique #6.. 1. Deterministic prefilter runs first: a resolver compares reported_quantity_ref against registered_outcome_text via struct-field-eq (metric type, timepoint, direction, CI overlap) and writes deterministic_prefilter with the registered_text_hash it judged against. 2. If the prefilter is not conclusive (incomparable / metric_type_differs / semantic wording change), a judge ENSEMBLE or human_reviewer — attestor_id distinct from the compiler and from claim_links extractor — assigns label, confidence, and for/against evidence anchors. 3. disclosed is set from a paper anchor. 4. Ensemble agreement is recorded; low agreement lowers confidence rather than forcing a label.
    - reliability/reproducibility: Reproducible for the deterministic prefilter; for the semantic label, reproducibility is bounded — mitigated by a fixed judge ensemble (n>=3, pinned model_ids), reported agreement, for/against symmetry, and confidence. Minimizing judge degrees of freedom: judges choose only from the fixed label enum and must cite anchors; they cannot write prose verdicts. Ecosystem must provide a calibration set of known outcome-switch cases to tune the ensemble.
    - constraints: attestor_id == compiler => assessment treated as attested_unverified, uncredited. registered_text_hash pins WHICH outcome text was judged, so a later registry edit cannot silently invalidate or launder the assessment.

  _Metrics afforded:_
  - Registry existence & topic binding ('accession is real AND about this paper') → Latest independent_resolver verification.result=match AND topic_match.band=match AND recompute_tolerance_ok, weighted by w(reliability_tier). [reliable-anchored]; anti-Goodhart: A fabricated-but-well-formed CRD/GSE passes format but fails the live fetch (result=not_found) or the pinned topic scorer (band=mismatch); author_attested self-stamps are uncredited (role gate), so the pipeline cannot mint its own verification. Snapshot hash must be reproduced by a second resolver.
  - Join coverage completeness → Every C## in claims.md appears exactly once in claim_links.yaml; count of expected_but_absent rows. [deterministic]; anti-Goodhart: A claim cannot silently escape the join (exactly-once rule = coverage failure if missing). The eligibility flag stops the null case from being a free pass: not_expected_* is cross-checked, and expected_but_absent is surfaced as a red flag rather than hidden as 'not that kind of claim'.
  - Selective-reporting rate (registered-but-unreported outcomes) → From outcome_coverage.yaml: fraction of verified registered primary/secondary outcomes with status=unreported_undisclosed; plus reported_not_registered count. [reliable-anchored]; anti-Goodhart: Signal is a first-class derived field, not a join the scorer reinvents, and is computed ONLY over independently verified registrations (excluded_unverified quarantines weak records) so it cannot be gamed by pointing at an unresolvable registry. Padding claim_links with fake links fails because each link must resolve to a real registered_outcome_id with a matching text_hash.
  - Preregistration-deviation / outcome-switching (disclosed vs undisclosed) → CorrespondenceAssessment.label != matches, split by disclosed; deterministic_prefilter carries the reproducible part, ensemble the semantic part. [semantic-judged]; anti-Goodhart: Label carries attestor_id distinct from compiler (self-labeling uncredited), confidence, ensemble agreement, and for/against evidence, so a convenient 'matches' cannot be asserted without anchors. registered_text_hash freezes the comparison target against registry edits.
  - Access-tier fidelity ('access is what the paper says it is') → Per-component Access-tier compared against the registry's live liveness check (open->200, controlled->named DAC exists, embargoed->date still future) recorded in verification.result, weighted by tier. [reliable-anchored]; anti-Goodhart: Declaring 'open' is falsified by a liveness fetch that 404s or redirects to a paywall; embargo_until in the past with tier still embargoed is auto-flagged at next_check_due. Per-component structure prevents laundering a controlled raw dataset behind an open processed slice.
  - Verification freshness & channel strength → Age of latest independent verification vs next_check_due, and distribution of reliability_tier across entries. [deterministic]; anti-Goodhart: Freshness and tier are channel properties read from records, not author claims; a stale or tier_2-only manifest is visibly discounted, so a paper cannot buy reliability it did not obtain (e.g. a PROSPERO-only correspondence claim is never scored as if API-checked).

  _Tradeoffs:_ Costs: the format now needs an independent resolver pool and a pinned resolvers.lock — real ecosystem infrastructure, not just a schema. Without independent resolvers, everything degrades to author_attested (tier attested_unverified, weight 0), which is honest but yields no credit — a deliberate design choice (no independent check = no reliability score, never a fabrication). Fabrication surfaces and mitigations: (1) Fake accession -> defeated by live fetch + snapshot hash reproduced by a second resolver. (2) Real accession, wrong paper -> defeated by pinned topic_match band. (3) Self-stamped verification -> defeated by role gate (verified_by must differ from extractor). (4) Registry-edit laundering (quietly change the registered outcome to match the paper) -> defeated by immutable registered_outcome_text + text_hash captured at first verification and append-only history. (5) Gaming the critique-#2 eligibility flag by tagging a dropped primary outcome as not_expected_background -> defeated by the cross-check in the selective-reporting protocol that field-matches unlinked registered primary/secondary outcomes against reported quantities and auto-flags. (6) Padding claim_links with hollow links -> each must resolve to a real registered_outcome_id with matching hash. Residual risk: the semantic correspondence label is irreducibly Class C; we bound but do not eliminate judge variance via fixed ensembles, agreement reporting, for/against symmetry, and the deterministic prefilter that carries as much of the decision as possible. Human-attested tiers (PROSPERO, AsPredicted) remain a genuinely weaker and slower channel — we do not pretend otherwise; we make the weakness machine-readable so scoring discounts it rather than hiding it.

  _Open questions:_ 1. Embedding-scorer reproducibility across hardware/kernels is not guaranteed bit-for-bit; we fall back to deterministic lexical scoring and flag recompute_tolerance_ok=false, but a truly reproducible semantic topic-match at scale is unsolved. 2. Who runs and funds the independent resolver pool, and how are resolver identities cryptographically bound so 'independent' is enforceable rather than declared? 3. The w(reliability_tier) discount weights and topic-match thresholds are published constants but their CALIBRATION (do these numbers track real reliability?) needs an empirical calibration set the ecosystem must build. 4. PROSPERO/AsPredicted having no API caps a whole class of publication-bias-relevant verification at tier_2; this is a registry-infrastructure gap the format can expose and pressure but cannot itself close. 5. Registry outcome vocabularies are not standardized across ClinicalTrials.gov / PROSPERO / OSF, so registered_outcome_id is a local capture, not a global key — cross-registry outcome identity remains a semantic problem. 6. Determining whether a deviation was 'disclosed' depends on the paper carrying an anchorable disclosure; absent anchors bias toward flagging (safe) but can produce false selective-reporting signals on genuinely disclosed-but-unanchored changes.

  _Changes from critique:_ Addressed all six critique points structurally, not defensively. (1) topic_match.method free-text string is GONE; replaced by a TopicMatch object with a versioned scorer_id keyed into a pinned resolvers.lock (deterministic jaccard formula or hash-pinned embedding weights) and a DERIVED band from fixed match_threshold/ambiguous_low, plus recompute_tolerance_ok for cross-resolver reproducibility. (2) Added registration_expectation to claim_links, splitting the forced null row into legitimate not_expected_* vs the red-flag expected_but_absent, with a cross-check so the flag cannot be gamed. (3) Selective reporting is now a first-class DERIVED file (outcome_coverage.yaml): every verified registered outcome gets a reported/unreported_undisclosed/unreported_disclosed status by deterministic set-difference — a readable field, not a join the metric reinvents. (4) Added role={author_attested|independent_resolver}; only independent records (verified_by != extractor) are credited, and re-fetch on cadence flips result on hash/field mismatch — self-certification is uncreditable. (5) Added reliability_tier (tier_0_api ... tier_2_human_attested ... attested_unverified) with a published w(tier) discount, so a PROSPERO attestation is visibly and quantitatively weaker than an eutils lookup. (6) The divergence/correspondence label moved out of the naked machine field into a CorrespondenceAssessment block with a deterministic prefilter PLUS a semantic label carrying attestor_id (distinct from compiler), assessor_kind, ensemble agreement, confidence, and for/against evidence — Class C done properly.

  _Adopted from competitor:_ Adopted the competitor's strongest ideas: (a) immutable VERBATIM registered_outcome_text captured at first verification with a text_hash, so a later registry edit becomes a new dated snapshot rather than an overwrite — this is the anti-laundering backbone of my correspondence assessment. (b) snapshot_ref into registry/snapshots/ as the byte-for-byte cache a second resolver re-hashes. (c) per-COMPONENT access tiers (one accession = open processed + controlled raw) with liveness semantics baked into result, replacing my single embedded access object. (d) prospective_or_retrospective and registered_by fields. (e) the deterministic-vs-semantic separation principle, which I hardened into the deterministic_prefilter + Class-C assessment split.

  _Why it wins:_ The competitor keeps my/its shared weaknesses that the reviewer flagged; I fix them. (1) Competitor's fingerprint_match_score is still an unpinned float with no scorer spec and no defined match/ambiguous band — I pin scorer + threshold in resolvers.lock so scores are reproducible across resolvers. (2) Competitor's correspondence enum and deviation block sit in machine fields with NO attestor-independence and NO confidence — exactly critique #6 — while mine carry attestor_id-distinct-from-compiler, ensemble agreement, confidence, and for/against evidence. (3) Competitor has no verification-reliability tier, so a PROSPERO manual_web_check and a GEO api_lookup both read as 'resolved_match' with no way for a metric to discount the weaker one (critique #5) — I add reliability_tier + published discount weights. (4) Competitor has no separation-of-duties: verification.checked_by is a free string with nothing stopping the authoring pipeline from filling it (critique #4) — I gate credit on role=independent_resolver and verified_by != extractor. (5) Competitor makes selective reporting only implicit (linked_claims mirror) and offers no eligibility flag, so both critique #2 and #3 remain open — I add the first-class outcome_coverage ledger and the registration_expectation flag. (6) I retain my unique coverage guarantee (every C## exactly once) which the competitor lacks entirely, and I close its self-inflicted null-collapse hole. Where a merge helps I took it (verbatim snapshots, per-component access), so this is strictly a superset that also repairs the reviewer's six holes in both designs.


### Finalist B (refined)

> _Judge critique it answered:_ Proposal #3 (Registry Join Layer, sonnet-5) is the cleanest engineering: reusable embedded Access-tier and Verification-record types (less duplication than the sidecar-sprawl proposals), an append-only `verification_history` audit trail, `next_check_due` cadence as a real field, and the sharpest single anti-gaming device in the field — the coverage requirement that every `C##` must appear exactly once in `claim_links.yaml`, so a claim cannot silently escape the join table. It is also the only proposal honest that PROSPERO has no API (`unverifiable_no_api`). Holes to close:

1. `topic_match: {score: 0.94, method: "title + condition keyword overlap"}` — `method` is a FREE-TEXT string, so the score is not comparable across ARAs and not reproducible across resolvers. Two resolvers compute different 0.9x and a metric that thresholds on it is thresholding on noise. Pin the scorer (embedding model+version or exact overlap formula) into an enum/versioned resolver id, and define the threshold that separates `match` from `ambiguous`. The concrete method examples read well but a string is not a specification.

2. The coverage requirement is your best idea but it creates its own hole: a claim with no registration relationship still needs a row, so it gets `registry_id: null` / `none_preregistered`. That collapses TWO different states — "this is a background/methods claim that was never expected to map to a registered outcome" vs "this claim SHOULD correspond to a preregistered outcome and silently doesn't" — into one value. Outcome-dropping can hide as "not that kind of claim." Add an expected-registration/eligibility flag so silent selective reporting is distinguishable from legitimately unregistered claims; otherwise the coverage guarantee is defeated by the null case it forces.

3. Selective reporting is only implicit. The manifest holds a registry's full `registered_outcomes` list (say 8); `claim_links` maps the 2 the paper reports. The 6 unreported outcomes — the classic selective-reporting signal — are recoverable only by a set-difference the metric must recompute. Make "registered-but-unreported outcomes" a first-class derived record so selective reporting is a readable field, not a join the scorer has to reinvent.

4. Self-certification: `verified: true, result: match, registry_response_hash: sha256:...` with `verified_by: "resolver-bot-geo-v2"` — what stops the authoring pipeline from stamping all three? The hash is only meaningful if an independent resolver re-fetches and recomputes it on cadence, flipping `result` on mismatch. State that separation-of-duties explicitly, or `verified: true` is author-attested and the hash is decorative.

5. The PROSPERO honesty is good but has a consequence you don't confront: verification of exactly the registry that carries the preregistration/outcome data most relevant to publication bias degrades to human "two-reviewer attestation" — unschedulable at scale and a strictly weaker reliability tier than a GEO API check. A `correspondence`/`divergence` claim resting on a PROSPERO attestation is NOT as reliable as one resting on an eutils lookup, yet nothing in the schema signals that downgrade to the metric. Add an explicit verification-reliability tier so scoring can discount the weaker path.

6. Your `divergence` enum (none/added/dropped/redefined/...) is truncated and, like #2's `correspondence`, is an irreducibly semantic label sitting in a machine field with no assessor-independence or confidence. Same fix: attestor id distinct from the compiler, plus confidence.

**The Registry Join Layer v2: accessions.yaml + access_tiers.yaml + claim_registry_links.yaml, with a pinned resolver, a separated-duties correspondence adjudicator, and machine-comparable registered outcomes**  ·  _source: claude-opus-4-8_

Registrations and accessions already contain real, resolvable identifiers (NCT#, CRD#, GSE#, phs#) trapped in prose, unlinked to any claim, and never resolved against the registry that issued them. This design promotes them to three joinable YAML sidecars — a canonical accession manifest, a structured access-tier table, and a claim-to-registered-outcome link table — and then closes the six holes the reviewer named. The correspondence judgment (matches vs outcome_switched) is no longer a free field: it carries a mandatory assessment block whose assessor MUST be provably independent of the authoring compiler, with confidence, for/against evidence, and an optional dual-assessor IRR gate; a correspondence value that lacks independent assessment is stamped self_declared_provisional and earns ZERO credit in every anti-gaming metric. The undefined similarity float is replaced by a pinned field_match algorithm (exact normalized accession equality + sha256 record hash + a named tokenizer/threshold or pinned embedding model+version) whose output deterministically maps to resolved_match/mismatch/ambiguous. The registered side now stores a structured planned_direction and planned_measure so direction-switching fires by field comparison rather than prose-diffing; snapshots carry a content hash so "immutable" is enforceable and a re-fetch mismatch flips result; cadence is a typed next_check_due field; and an eligibility gate (registration_expectation with not_applicable_to_genre) prevents penalizing legitimately unregisterable work.

- **registry/accessions.yaml** (YAML, top-level key `accessions:` list of typed records; embeds the VerificationRecord type.) — Canonical, deduplicated manifest of every external registry entry or accession the work touches (trial/review registrations, sequencing/omics accessions, controlled-access study records, data/code archives). One row per unique real-world identifier; every other layer references it by `id`. Now carries a genre-eligibility gate so unregisterable work is not penalized, and a verification block that hashes the cached snapshot and pins a next-check date.
  - fields: id: string (local ARA id, e.g. ACC01) — required. kind: enum{trial_registration, systematic_review_registration, sequencing_accession, controlled_access_study, data_repository_record, biological_material, code_archive, other} — required. registry: enum{clinicaltrials_gov, prospero, isrctn, anzctr, eudract, who_ictrp, osf_registries, aspredicted, geo, sra, ena, arrayexpress, ega, dbgap, proteomexchange, addgene, zenodo, figshare, dryad, datacite, other} — required. accession_id: string exactly as issued (e.g. NCT04895709, CRD420261327845, GSE307990, phs002345.v1.p1) — required; MAY be `not_specified` when the paper states a registration exists but gives no ID (honest-absence, flagged for follow-up, NOT silently dropped). registration_expectation: enum{expected_prospective, expected_any_time, recommended, not_applicable_to_genre, unknown} — required — the genre gate: `not_applicable_to_genre` means this work is not the kind that should register (e.g. a secondary reanalysis, a methods/theory paper, a dataset-only release) and a missing registration here is scored EQUAL to an honest present one, never penalized. url: string resolver URL — optional, derivable from accession_id+registry via a template. registered_by: enum{authors, third_party, unknown} — required. registered_date: date | not_specified — required. prospective_or_retrospective: enum{prospective, retrospective, not_specified} — required. linked_claims: list[claim_id] — optional denormalized mirror of the authoritative link in claim_registry_links.yaml. verification: VerificationRecord — required (may be honest not_checked at first compile). provenance: {source_anchor: string quote+locator into src/*, extracted_by: enum{compiler, human}} — required. notes: string | not_specified.
  - example: accessions:
  - id: ACC01
    kind: systematic_review_registration
    registry: prospero
    accession_id: "CRD420261327845"
    registration_expectation: expected_prospective
    url: "https://www.crd.york.ac.uk/prospero/display_record.php?RecordID=261327845"
    registered_by: authors
    registered_date: "2024-11-02"
    prospective_or_retrospective: prospective
    linked_claims: [C01, C02, C07]
    verification:
      method: manual_web_check
      checked_at: "2026-07-01T00:00:00Z"
      checked_by: "seal-resolver-agent-03"
      result: resolved_match
      field_match:
        accession_exact: true
        registry_record_hash: "sha256:8f1e0c9c4b..."
        title_similarity: {score: 0.94, algorithm: "token_set_ratio.v1", threshold_match: 0.85}
      snapshot_ref: "registry/snapshots/CRD420261327845_2026-07-01.html"
      snapshot_sha256: "sha256:2a7d11e0f9..."
      next_check_due: "2027-01-01"
    provenance: {source_anchor: "src/methods.md « prospectively registered on PROSPERO (CRD420261327845) »", extracted_by: compiler}
    notes: not_specified
  - id: ACC02
    kind: sequencing_accession
    registry: geo
    accession_id: "GSE307990"
    registration_expectation: expected_any_time
    url: "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE307990"
    registered_by: authors
    registered_date: "2025-03-14"
    prospective_or_retrospective: not_specified
    linked_claims: [C03]
    verification:
      method: api_lookup
      checked_at: "2026-07-01T00:00:00Z"
      checked_by: "ncbi-eutils-resolver-v1"
      result: resolved_match
      field_match:
        accession_exact: true
        registry_record_hash: "sha256:1a2bff90..."
        title_similarity: {score: 0.99, algorithm: "token_set_ratio.v1", threshold_match: 0.85}
      snapshot_ref: "registry/snapshots/GSE307990_2026-07-01.json"
      snapshot_sha256: "sha256:c31d55aa..."
      next_check_due: "2027-07-01"
    provenance: {source_anchor: "src/data.md « deposited in GEO under GSE307990 »", extracted_by: compiler}
    notes: not_specified
- **VerificationRecord (embedded type, reused by accessions.yaml and access_tiers.yaml)** (YAML/JSON typed object, embedded; a parallel verification_history: list preserves prior records.) — The single reusable type that turns 'looks real' into 'is real, hashed, dated, and re-checkable.' Pins the fingerprint algorithm, hashes both the fetched registry record and the cached snapshot payload, and carries the typed cadence field. Appended to a per-entry verification_history list, never overwritten.
  - fields: method: enum{api_lookup, manual_web_check, doi_resolution, unverifiable_no_api, not_checked} — required. checked_at: ISO8601 | null — required (null iff method=not_checked). checked_by: string agent-id or human-reviewer-id | null — required if checked. result: enum{resolved_match, resolved_mismatch, resolved_not_found, unreachable, ambiguous_needs_human, not_checked} — required; not_checked and unreachable are honest states scored EQUAL to a completed check, never as fabrication. field_match: {accession_exact: bool — normalized string equality (uppercase, strip whitespace, canonicalize version suffix per registry rule); registry_record_hash: 'sha256:...' of the canonicalized fetched record (JSON keys sorted, whitespace collapsed) | null; title_similarity: {score: float[0,1], algorithm: enum{token_set_ratio.v1, embed_cosine.<model>@<version>}, threshold_match: float} | null} | null — the PINNED comparison; see the Field-Match protocol for the exact function and decision map. snapshot_ref: relative path into registry/snapshots/ | null. snapshot_sha256: 'sha256:...' content hash of the cached snapshot payload | null — required whenever snapshot_ref is set; a re-fetch whose recomputed hash != stored hash MUST flip result to resolved_mismatch and append (never overwrite) a new record. next_check_due: date — required; cadence = 6 months for status ongoing/embargoed, 12 months otherwise, or sooner if result was unreachable/ambiguous. notes: string | not_specified.
  - example: verification:
  method: api_lookup
  checked_at: "2026-07-01T00:00:00Z"
  checked_by: "resolver-bot-geo-v2"
  result: resolved_match
  field_match:
    accession_exact: true
    registry_record_hash: "sha256:1a2bff90c7..."
    title_similarity: {score: 0.88, algorithm: "embed_cosine.bge-large-en@1.5", threshold_match: 0.80}
  snapshot_ref: "registry/snapshots/GSE307990_2026-07-01.json"
  snapshot_sha256: "sha256:c31d55aa4e..."
  next_check_due: "2027-07-01"
  notes: "GEO esummary confirms series public, organism Homo sapiens, N=31 matches data.md."
verification_history:
  - {method: api_lookup, checked_at: "2026-01-05T00:00:00Z", result: resolved_match, snapshot_sha256: "sha256:c31d55aa4e...", next_check_due: "2026-07-05"}
- **registry/access_tiers.yaml** (YAML, top-level key `access_tiers:` list of typed records; reuses VerificationRecord.) — Structured, per-data-component access-tier declaration, replacing the prose sentence ('processed data are open; raw reads are controlled via dbGaP') with fields a metric compares against what the registry publicly states about access and against a live-liveness check.
  - fields: id: string — required. artifact_ref: string, pointer to a data/dataset descriptor or an accessions.yaml id — required. component: string naming the specific data slice (e.g. 'raw sequencing reads', 'processed count matrix', 'individual-level phenotype data') — required. tier: enum{open, registered_access, controlled_access, embargoed, restricted_by_agreement, not_available, not_applicable} — required. mechanism: enum{public_url, api_key_required, dbgap_dac_approval, ega_dac_approval, data_use_agreement, embargo_until_date, institutional_review_required, none} — required. gatekeeper: string (named DAC/committee) | not_applicable — required. embargo_until: date | null — required (null = no embargo; distinct from not_specified). license: SPDX identifier string | not_specified — required. access_procedure_ref: string URL/DOI of the DAC or access-request process | not_specified — required. verification: VerificationRecord — required; here result means: open→ URL/API returns 200 (liveness) recorded in field_match; controlled→ named DAC/study record exists and matches the accession; embargoed→ embargo date still future, or has lapsed and the public tier should have changed (a lapsed embargo with tier still 'embargoed' → resolved_mismatch).
  - example: access_tiers:
  - id: AT01
    artifact_ref: ACC02
    component: "processed count matrix (supplementary table)"
    tier: open
    mechanism: public_url
    gatekeeper: not_applicable
    embargo_until: null
    license: "CC-BY-4.0"
    access_procedure_ref: "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE307990"
    verification: {method: api_lookup, checked_at: "2026-07-01T00:00:00Z", checked_by: "ncbi-eutils-resolver-v1", result: resolved_match, field_match: {accession_exact: true, registry_record_hash: "sha256:aa11...", title_similarity: null}, snapshot_ref: "registry/snapshots/GSE307990_files_2026-07-01.json", snapshot_sha256: "sha256:77bc...", next_check_due: "2027-07-01"}
  - id: AT02
    artifact_ref: ACC02
    component: "raw sequencing reads (FASTQ)"
    tier: controlled_access
    mechanism: dbgap_dac_approval
    gatekeeper: "dbGaP Data Access Committee"
    embargo_until: null
    license: "dbGaP Data Use Certification"
    access_procedure_ref: "https://dbgap.ncbi.nlm.nih.gov/aa/wga.cgi?page=login&study_id=phs002345.v1.p1"
    verification: {method: manual_web_check, checked_at: "2026-07-01T00:00:00Z", checked_by: "human-reviewer-CO", result: resolved_match, field_match: {accession_exact: true, registry_record_hash: "sha256:be44...", title_similarity: null}, snapshot_ref: "registry/snapshots/phs002345_2026-07-01.html", snapshot_sha256: "sha256:19ee...", next_check_due: "2027-01-01"}
- **registry/claim_registry_links.yaml** (YAML, top-level key `links:` list of typed records; embeds RegisteredOutcome and CorrespondenceAssessment types. Every C## in claims.md must appear exactly once (a silently missing claim is a coverage failure, not honest absence); a claim with no registration uses registry_id: null + correspondence.value: not_applicable with registration_expectation echoed from the accession gate.) — The join key the gap names as missing: a typed link from a specific claim to a specific registered outcome inside a specific accession, plus a STRUCTURED, machine-comparable registered outcome (planned_direction, planned_measure) and a correspondence judgment that carries a mandatory, provably-independent assessment block. This turns publication-bias / outcome-switching detection from 'infer it' into 'read the field comparison, and read WHO judged it and how confidently.'
  - fields: id: string (e.g. RL01) — required. claim_id: ref-id into claims.md — required, must resolve. accession_id: ref-id into accessions.yaml | null — required (null = claim not tied to any registration). registered_outcome: RegisteredOutcome — required (or the null-object form when accession_id is null). reported_result_quantity_ref: ref-id into the sibling quantities.yaml ledger — the value in THIS paper answering that outcome — required, or not_specified. reported_direction: enum{superiority, non_inferiority, equivalence, difference_two_sided, association_positive, association_negative, null_no_difference, no_direction_specified} — required — the direction the paper actually reports, for machine comparison against RegisteredOutcome.planned_direction. field_comparison: {direction_match: bool | null, measure_match: enum{same, related_transform, different, uncomparable} | null, computed_by: string, computed_at: ISO8601} — DETERMINISTIC pre-computation feeding the human assessor, never the final label. correspondence: {value: enum{matches, partial_match, outcome_switched, outcome_added_not_registered, outcome_dropped_silently, not_yet_assessable, not_applicable}, status: enum{self_declared_provisional, independently_assessed, adjudicated_dual}, assessment: CorrespondenceAssessment | null} — required; a `value` whose `status` is self_declared_provisional (assessor == authoring pipeline, or no assessment attached) earns ZERO credit in anti-gaming metrics — only independently_assessed / adjudicated_dual count. deviation: {deviation_type: enum{none, outcome_added, outcome_dropped, outcome_redefined, direction_changed, timepoint_changed, analysis_changed, population_changed}, disclosed_in_paper: bool, disclosure_anchor: string quote+locator | not_specified} | null — required when correspondence.value != matches.
  - example: links:
  - id: RL01
    claim_id: C04
    accession_id: ACC01
    registered_outcome:
      outcome_id: "PRIMARY-1"
      registered_text: "Diagnostic accuracy (sensitivity/specificity) of plasma p-tau217 vs p-tau181 for amyloid-beta positivity"
      planned_direction: superiority
      planned_measure: "AUC (sensitivity/specificity)"
      planned_timepoint: "cross-sectional"
      outcome_type: primary
      captured_at: "2026-07-01T00:00:00Z"
      captured_from_snapshot_sha256: "sha256:2a7d11e0f9..."
    reported_result_quantity_ref: Q17
    reported_direction: superiority
    field_comparison: {direction_match: true, measure_match: same, computed_by: "field-match.v1", computed_at: "2026-07-01T00:05:00Z"}
    correspondence:
      value: matches
      status: adjudicated_dual
      assessment:
        assessor_id: "seal-corr-agent-11"
        assessor_role: independent_reviewer_agent
        independent_of_authoring: true
        authoring_pipeline_id: "compiler-run-2026-07-06-A"
        confidence: 0.9
        for_evidence: "Registered primary AUC superiority == reported primary; same measure, same direction, same timepoint."
        against_evidence: "none material"
        second_assessor: {assessor_id: "human-reviewer-CO", assessor_role: human_reviewer, agrees: true}
        agreement: {cohen_kappa: 0.81, calibration_set_id: "pubbias-cal-v1"}
    deviation: {deviation_type: none, disclosed_in_paper: true, disclosure_anchor: "src/results.md « primary outcome as registered »"}
  - id: RL02
    claim_id: C05
    accession_id: ACC01
    registered_outcome:
      outcome_id: "PRIMARY-1"
      registered_text: "...superiority of p-tau217 over p-tau181..."
      planned_direction: superiority
      planned_measure: "AUC"
      planned_timepoint: "cross-sectional"
      outcome_type: primary
      captured_at: "2026-07-01T00:00:00Z"
      captured_from_snapshot_sha256: "sha256:2a7d11e0f9..."
    reported_result_quantity_ref: Q22
    reported_direction: null_no_difference
    field_comparison: {direction_match: false, measure_match: same, computed_by: "field-match.v1", computed_at: "2026-07-01T00:05:00Z"}
    correspondence:
      value: outcome_switched
      status: independently_assessed
      assessment:
        assessor_id: "seal-corr-agent-11"
        assessor_role: independent_reviewer_agent
        independent_of_authoring: true
        authoring_pipeline_id: "compiler-run-2026-07-06-A"
        confidence: 0.72
        for_evidence: "Registered superiority; paper reports no difference and elevates a secondary endpoint to headline — direction flipped, not disclosed."
        against_evidence: "Paper's Discussion mentions the null in passing but never labels it a deviation from registration."
        second_assessor: null
        agreement: null
    deviation: {deviation_type: direction_changed, disclosed_in_paper: false, disclosure_anchor: not_specified}
- **RegisteredOutcome (embedded type)** (YAML/JSON typed object, embedded in claim_registry_links.yaml.) — Makes the registered side machine-comparable rather than prose. Adds the structured planned_direction and planned_measure that direction-switching detection needs, alongside the verbatim registered_text (kept for human audit) and a pin to the snapshot hash it was captured from (immutability anchor).
  - fields: outcome_id: string, the registry's own outcome label (e.g. 'Outcome Measure 1', 'PRIMARY-1') | not_specified — required. registered_text: string, VERBATIM quote of the outcome definition at capture, immutable once set (a later registry edit becomes a NEW dated snapshot + new record, never an overwrite) — required. planned_direction: enum{superiority, non_inferiority, equivalence, difference_two_sided, association_positive, association_negative, no_direction_specified} — required-or-not_specified — the direction the registration planned to test; the field that lets direction-switching fire deterministically. planned_measure: string (controlled where possible: AUC, hazard_ratio, mean_difference, odds_ratio, sensitivity_specificity, ...) | not_specified — required. planned_timepoint: string | not_specified — required. outcome_type: enum{primary, secondary, exploratory, not_specified} — required. captured_at: ISO8601 — required. captured_from_snapshot_sha256: 'sha256:...' — required — ties the structured extraction to the exact hashed snapshot it was read from.
  - example: registered_outcome:
  outcome_id: "PRIMARY-1"
  registered_text: "Superiority of plasma p-tau217 over p-tau181 for amyloid-beta positivity, measured by AUC, cross-sectional."
  planned_direction: superiority
  planned_measure: "AUC"
  planned_timepoint: "cross-sectional"
  outcome_type: primary
  captured_at: "2026-07-01T00:00:00Z"
  captured_from_snapshot_sha256: "sha256:2a7d11e0f9..."
- **CorrespondenceAssessment (embedded type)** (YAML/JSON typed object, embedded in the correspondence field.) — Closes the load-bearing hole: the most semantic judgment in the artifact (matches vs outcome_switched) can no longer be self-certified by the authoring compiler. This block records WHO judged, proves separation of duties from the authoring pipeline, carries a confidence and for/against evidence (Class-C discipline), and supports an optional dual-assessor IRR gate.
  - fields: assessor_id: string — required — id of the agent/human that assigned correspondence.value. assessor_role: enum{independent_reviewer_agent, human_reviewer, third_party} — required — MUST NOT be the authoring/compiler pipeline. independent_of_authoring: bool — required — true iff assessor_id differs from the pipeline that produced claims.md/quantities.yaml; if false, the enclosing correspondence.status is forced to self_declared_provisional and scores zero. authoring_pipeline_id: string — required — the id being separated FROM, so independence is machine-checkable, not asserted. confidence: float[0,1] — required. for_evidence: string — required — the strongest case FOR the assigned value. against_evidence: string | 'none material' — required — the strongest case AGAINST (minimizes single-assessor bias). second_assessor: {assessor_id, assessor_role, agrees: bool} | null — required key, null when single-assessed. agreement: {cohen_kappa: float, calibration_set_id: string} | null — required for status=adjudicated_dual — IRR of the two assessors on a shared calibration set of pre-labeled outcome-switching cases.
  - example: assessment:
  assessor_id: "seal-corr-agent-11"
  assessor_role: independent_reviewer_agent
  independent_of_authoring: true
  authoring_pipeline_id: "compiler-run-2026-07-06-A"
  confidence: 0.72
  for_evidence: "Registered superiority; reported null; secondary endpoint elevated to headline without a deviation note."
  against_evidence: "Discussion mentions the null once but never frames it as a registration deviation."
  second_assessor: {assessor_id: "human-reviewer-CO", assessor_role: human_reviewer, agrees: true}
  agreement: {cohen_kappa: 0.81, calibration_set_id: "pubbias-cal-v1"}

  _Protocols:_
  - **Resolver / live-verification protocol (Class B)** — At compile time for every accessions.yaml and access_tiers.yaml entry, and on every next_check_due date thereafter.. 1. Build the resolver URL from accession_id+registry via a per-registry template. 2. Fetch: prefer api_lookup (ClinicalTrials.gov v2 API, NCBI E-utilities/esummary for GEO/SRA/dbGaP, EBI for ENA/ArrayExpress/EGA, DataCite/Crossref for DOIs); fall back to manual_web_check where no API exists (PROSPERO); if neither resolves, set result=unreachable (NOT not_found). 3. Distinguish outcomes: HTTP/record present + accession canonically equal → candidate match; record explicitly absent/404-with-registry-200 → resolved_not_found; transport/timeout/5xx → unreachable. 4. Canonicalize the fetched record (sort JSON keys, collapse whitespace) and store registry_record_hash. 5. Persist the raw payload to registry/snapshots/<accession>_<date>.<ext> and store its content sha256 in snapshot_sha256. 6. Run the Field-Match protocol to set result. 7. Set next_check_due per cadence. 8. Append the record to verification_history; never overwrite.
    - reliability/reproducibility: Reliability, not determinism: registry existence is external. Reproducibility comes from the pinned snapshot + snapshot_sha256 — any auditor can re-fetch and recompute; a recomputed hash != stored hash MUST flip result to resolved_mismatch and append a new record, exposing silent registry edits or snapshot tampering. not_checked/unreachable are honest states scored equal to a completed check. Two independent resolvers hitting the same accession must agree on result or the entry is escalated to ambiguous_needs_human.
    - constraints: Ecosystem must provide: (a) per-registry resolver adapters and URL templates; (b) a snapshot store with immutable, content-addressed writes; (c) API access/credentials for controlled registries (dbGaP/EGA existence checks without data access); (d) a scheduler that fires on next_check_due.
  - **Field-Match protocol (pins the former fingerprint_match_score float) — deterministic** — Whenever a fetched registry record must be scored against the paper's claimed identity/topic to set VerificationRecord.result.. 1. accession_exact = normalize(paper_accession) == normalize(registry_accession), where normalize = uppercase, strip whitespace/hyphens, canonicalize the version suffix per registry rule (e.g. keep phsNNNNNN.vN.pN; strip GEO's trailing whitespace). 2. registry_record_hash = sha256(canonicalized record). 3. title_similarity: algorithm is PINNED to one of {token_set_ratio.v1 = |A∩B| / |A∪B| over lowercased, punctuation-stripped, stopword-filtered (stoplist v1) token sets of registered_title vs PAPER.md title+keywords; OR embed_cosine.<model>@<version> = cosine of normalized embeddings from a named, version-pinned model, e.g. bge-large-en@1.5}. The chosen algorithm string and threshold are stored in the record. 4. Decision map: result = resolved_match iff accession_exact AND record retrievable AND title_similarity.score >= threshold_match (default 0.85 for token_set_ratio.v1, 0.80 for embed_cosine). result = resolved_mismatch if accession resolves but score < 0.60. result = ambiguous_needs_human if 0.60 <= score < threshold_match. Pure data accessions with no comparable title set title_similarity=null and decide on accession_exact + record presence alone.
    - reliability/reproducibility: Fully reproducible: given the same snapshot, the same normalizer, and the same pinned algorithm+version, the score and the resolved_* label are recomputable bit-for-bit for token_set_ratio.v1, and to embedding-model tolerance for embed_cosine (hence the model+version pin). No unpinned float ever appears.
    - constraints: Ecosystem must publish: the token normalizer + stoplist v1 as code; the exact hosted embedding model artifacts by version; the threshold table per registry. Threshold changes are versioned (algorithm string bumps), never silent.
  - **Correspondence adjudication protocol — separation of duties (Class C, IRR-gated)** — To assign or upgrade any correspondence.value in claim_registry_links.yaml (the matches / partial_match / outcome_switched / added / dropped judgment).. 1. The authoring compiler MAY pre-fill field_comparison (deterministic: direction_match, measure_match from RegisteredOutcome vs reported_direction/quantity) and MAY propose a correspondence.value, but that record is stamped status=self_declared_provisional and earns zero anti-gaming credit. 2. An assessor whose assessor_id differs from authoring_pipeline_id (checked mechanically) reviews the field_comparison + verbatim registered_text + the paper's reported quantity, writes for_evidence AND against_evidence, sets confidence, and assigns correspondence.value → status becomes independently_assessed. 3. For high-stakes cases (any value in {outcome_switched, outcome_dropped_silently} feeding a funder-facing pub-bias metric), a second independent assessor labels the same case; agreement.cohen_kappa is computed against a shared calibration set (pubbias-cal-v1) of pre-labeled outcome-switching examples → status becomes adjudicated_dual. 4. Disagreement is not hidden: it lowers confidence and routes to human tie-break, recorded in second_assessor.agrees=false.
    - reliability/reproducibility: Class-C discipline: for/against evidence + confidence + a calibration set + a two-assessor IRR gate minimize assessor degrees of freedom. Reproducibility target is inter-assessor kappa on the calibration set, reported per release; assessors below a kappa floor are decertified. The authoring pipeline can never be its own certifier — independence is a machine-checked field, not a promise.
    - constraints: Ecosystem must provide: (a) a registry of assessor ids with their pipeline lineage so independence is verifiable; (b) the pubbias calibration set with gold labels; (c) a kappa computation service and a decertification threshold; (d) tooling that refuses to count self_declared_provisional records in any metric.
  - **Eligibility-gating protocol (prevents fabrication pressure)** — Before any metric penalizes a work for a missing/weak registration.. 1. Read accessions.yaml.registration_expectation for the relevant kind (or the genre manifest's declared genre). 2. If not_applicable_to_genre, the metric treats the absence as fully honest — no penalty, no bonus — and the work is scored on the metrics that DO apply to its genre. 3. If expected_prospective/expected_any_time and accession_id is present, score normally. 4. If expected but accession_id=not_specified, flag as an honest-absence gap for follow-up (the paper claims registration but gave no ID) — this is a resolvable data-quality flag, distinct from a fabrication and distinct from a genre exemption.
    - reliability/reproducibility: Deterministic gate. The exemption cannot be abused to hide a required registration because registration_expectation is itself provenance-anchored to the genre manifest, and a mismatch (genre = RCT but expectation = not_applicable_to_genre) is a mechanical contradiction that fails validation.
    - constraints: Ecosystem must provide a genre→expectation default table so registration_expectation is defaulted, not hand-set, for common genres; deviations from the default require a source_anchor.

  _Metrics afforded:_
  - Registration realness rate (fraction of expected registrations that resolve to a real, topic-matching record) → Over accessions with registration_expectation in {expected_prospective, expected_any_time}: fraction whose verification.result=resolved_match under the pinned Field-Match protocol, with a valid snapshot_sha256. [reliable-anchored]; anti-Goodhart: A fabricated but well-formed NCT/CRD/GSE number cannot score: it fails accession_exact resolution or resolved_not_found. The snapshot_sha256 + re-fetch recomputation means a doctored cached page flips result to mismatch. Padding the manifest with extra fake accessions lowers, not raises, the rate.
  - Outcome-switching / publication-bias index (fraction of primary claims whose correspondence != matches and deviation.disclosed_in_paper=false) → Over claim_registry_links where registered_outcome.outcome_type=primary: count correspondence.value in {outcome_switched, outcome_dropped_silently, outcome_added_not_registered} with deviation.disclosed_in_paper=false — but ONLY records with correspondence.status in {independently_assessed, adjudicated_dual} are counted. [semantic-judged]; anti-Goodhart: The whole exploit named in the critique — authoring pipeline labels an outcome_switched case as matches — is dead: self_declared_provisional records score zero, and correspondence must be set by an assessor mechanically proven independent of authoring_pipeline_id, with for/against evidence and (for high-stakes labels) a dual-assessor kappa gate. field_comparison.direction_match=false vs a claimed correspondence=matches is a mechanical contradiction that auto-escalates.
  - Direction-switch detection (registered planned_direction != reported_direction, undisclosed) → Deterministic field comparison of RegisteredOutcome.planned_direction vs link.reported_direction; flags where they differ and deviation.disclosed_in_paper=false. [deterministic]; anti-Goodhart: Because planned_direction is a structured enum captured verbatim from a hashed snapshot, this fires by field comparison, not prose-diffing; the authoring side cannot soften a superiority→null flip in prose because the machine reads the enum, and captured_from_snapshot_sha256 pins where the enum came from.
  - Access-tier fidelity (declared tier matches what the registry publicly states / liveness) → Over access_tiers entries: fraction whose verification.result=resolved_match — open→200 liveness, controlled→named DAC exists, embargoed→embargo date consistent with current public state. [reliable-anchored]; anti-Goodhart: Claiming 'open' when the URL 404s yields resolved_mismatch, not credit. A lapsed embargo still marked 'embargoed' flips to mismatch on the next cadence check. not_available is a first-class honest value scored equal to open — no pressure to overclaim openness.
  - Prospective-registration rate → Fraction of expected registrations with prospective_or_retrospective=prospective AND registered_date earlier than the study start recorded in the methods layer. [reliable-anchored]; anti-Goodhart: registered_date is provenance-anchored to the resolved registry record (registry_record_hash), so it cannot be back-dated in the manifest; not_specified is honest and does not count as prospective.
  - Verification freshness / coverage → Fraction of accessions with a verification record whose next_check_due is not past, and fraction of C## claims present in claim_registry_links.yaml. [deterministic]; anti-Goodhart: Cadence is a typed field, so staleness is measurable, not narrated. A claim silently missing from the link file is a coverage failure, not honest absence; not_checked/unreachable are scored equal to checked so there is no incentive to fake a verification to look fresh.

  _Tradeoffs:_ Cost: correspondence adjudication now requires a second, independent assessor (agent or human) plus a maintained calibration set — heavier than a self-labeled field. Mitigation: only high-stakes primary-outcome labels feeding funder metrics require adjudicated_dual; secondary/exploratory can stop at independently_assessed. Fabrication surfaces that remain: (a) an author could register a deliberately vague outcome so planned_direction=no_direction_specified and nothing can 'switch' — mitigated because a primary outcome with no direction is itself a low-quality-registration signal a metric can surface, and captured verbatim text is human-auditable; (b) a captured snapshot could be forged at first capture before any hash exists — mitigated by requiring the snapshot to come from a resolver run whose result and registry_record_hash are independently reproducible by re-fetch, so a forged snapshot diverges on the next cadence check; (c) an 'independent' assessor could secretly share lineage with the authoring pipeline — mitigated by the assessor registry that records pipeline lineage, making independence machine-checkable rather than asserted, plus kappa-based decertification. Residual risk: registries that both lack an API and mutate silently (PROSPERO) force manual_web_check and lean hardest on snapshot hashing; two-reviewer attestation is the fallback. Honest-absence symmetry is preserved throughout: not_specified, not_checked, unreachable, not_available, and not_applicable_to_genre are all first-class and scored equal to an honest presence.

  _Open questions:_ 1. Controlled-access existence checks (dbGaP/EGA) may themselves require credentialed access even just to confirm a study record exists — how much can be verified without a data-use agreement, and how is that partial-verifiability represented beyond unreachable? 2. The pinned embed_cosine title-similarity path is only reproducible to model tolerance; is a purely lexical token_set_ratio.v1 sufficient for all registries, letting us drop the embedding dependency entirely? 3. What is the minimum inter-assessor kappa floor on pubbias-cal-v1 below which outcome_switched labels are untrustworthy, and who curates/expands that calibration set as new switching patterns appear? 4. Registry-side edits after publication (a registration retro-edited to match the paper) are captured as new dated snapshots — but which snapshot is authoritative for the pub-bias metric, the first prospective one or the latest? 5. How are multi-registry cross-postings (WHO ICTRP mirroring a national registry) deduplicated so one real trial is not counted as two registrations?

  _Changes from critique:_ Addressed all six critique points directly. (1) correspondence is no longer a bare enum: it is a {value, status, assessment} object; the CorrespondenceAssessment type carries assessor_id, assessor_role, a machine-checked independent_of_authoring boolean plus authoring_pipeline_id (separation of duties), confidence, for/against evidence, an optional second_assessor, and a Cohen's-kappa IRR gate on a calibration set. Any value not independently assessed is stamped self_declared_provisional and earns ZERO metric credit. (2) Killed the undefined fingerprint_match_score float; replaced with a pinned Field-Match protocol and a field_match object: normalized exact-accession equality, a sha256 registry_record_hash, and a title_similarity whose algorithm is pinned (token_set_ratio.v1 with a published normalizer/stoplist, or embed_cosine.<model>@<version>) with an explicit threshold→resolved_match/mismatch/ambiguous decision map. (3) Added the RegisteredOutcome type with structured planned_direction and planned_measure enums plus reported_direction on the claim side, so direction-switching fires by deterministic field comparison, not prose-diffing. (4) Added snapshot_sha256 (content hash of the cached snapshot payload) as required whenever snapshot_ref is set, and specified that a re-fetch whose recomputed hash mismatches MUST flip result to resolved_mismatch and append a new record. (5) Promoted cadence from prose to a typed next_check_due field in every VerificationRecord, with a stated default cadence table. (6) Added the registration_expectation eligibility gate (including not_applicable_to_genre) so legitimately unregisterable work is scored equal to honest presence and never creates pressure to fabricate a registration.

  _Adopted from competitor:_ Adopted the competitor's sha256 registry_response/record hash, the typed next_check_due cadence field, the append-only verification_history list, the provenance.source_anchor (quote+locator + extracted_by) on manifest entries, the SPDX license field and named gatekeeper on the access-tier object, the structured registered_outcomes list with type/timepoint (generalized into my RegisteredOutcome type), the topic_match-with-named-method idea (hardened into my pinned Field-Match protocol), and the rule that every C## claim must appear exactly once in the link file (silent omission = coverage failure, not honest absence).

  _Why it wins:_ The competitor has the hashes, cadence, and a claim_links divergence enum, but it shares my original design's fatal weakness: its verification.verified_by and its divergence label can both be written by the authoring compiler with no enforced separation of duties, no confidence, and no IRR — the same self-certification hole the reviewer flagged. My CorrespondenceAssessment makes independence a machine-checked field (independent_of_authoring vs authoring_pipeline_id) and refuses metric credit to self-declared labels, which is the actual anti-gaming teeth. Its topic_match is a {score, method-string} pair where the method is free text ('title + condition keyword overlap') — still not reproducible; my Field-Match protocol pins the exact normalizer, stoplist, model+version, and threshold→label decision map. Its registered_outcomes carry description + type but no planned_direction, so direction-switching (the core pub-bias signal) still needs prose interpretation; my RegisteredOutcome carries a planned_direction enum compared deterministically against reported_direction. And it lacks a genre-eligibility gate, so it can penalize a secondary reanalysis for having no PROSPERO entry; my registration_expectation.not_applicable_to_genre removes that fabrication pressure. Net: same plumbing, but I close the separation-of-duties, reproducible-similarity, machine-comparable-direction, and genre-eligibility gaps that leave the competitor gameable.


---


## NOVELANCHOR — Novelty anchoring inputs

_Class B — anchor-dependent (reliability + protocol)_


**Judge rationale:** The mandate leads with 'does it AFFORD the metric and make it harder to game' and explicitly says to punish unstated Goodhart holes and fabrication pressure. On that axis the two Sonnet designs pull ahead of the two gpt-5.5-codex siblings. #2 (DAL) is the most complete, implementable, honestly-auditable package: it is the only design that makes the delta a JOINABLE computation (quantity-ledger ids on both sides) rather than a paraphrase, it adds the strongest anti-puffery lock (realized_in >=1 real claim id), it carries the contemporaneous_uncited 'did they miss it' coverage signal, and it keeps resolver reproducibility (index_snapshot_id, embedding_model, k, method) plus coverage_stats and an inter-resolver Jaccard audit — all in three clean, maintainable sidecars. #3 (NOVEL-ANCHOR) earns the second slot on the single most important insight nobody else has: it refuses the publication-date temporal hole and anchors the SOTA cutoff to an externally-timestamped precedence_date, and it names two fabrication surfaces the others ignore (self-reported vs source-verified baselines; retrospective-resolution leakage). It is honest about its own limits (status/unresolved_reason/retrospective flags) rather than hand-waving them. Its cost is a genuinely thin resolver-reproducibility spec, which I hammer in the critique — but its anti-gaming lead on the field's biggest Goodhart hole outweighs that for a top-two placement. #0 (NAL) is the rigor champion on pure auditability (sha256 hashes, embedding manifests, dedicated resolver_runs) and would be my third — but it inherits the same publication-cutoff temporal hole as #2 without #3's fix, lacks baseline source-verification, and its five synchronized sidecars-per-paper create real operational and fabrication-pressure burden (someone must populate an embedding_manifest for every contribution). #1 is a slightly-less-granular sibling of #0 whose one distinctive strength (comparability_basis: same_dataset vs indirect_network vs literature_synthesis — a real and under-appreciated anti-gaming lever) is not enough to escape being dominated on every other axis. Neither winner is temporally-and-arithmetically airtight; the ideal design is #2's joinable-delta + honest-absence spine, retrofitted with #3's precedence_date/source_verified baselines and #0's hashed resolver+embedding manifest.


### Finalist A (refined)

> _Judge critique it answered:_ DAL (#2) is the most balanced design in the field: it is the only one that turns "we improve on prior work" into an actually joinable COMPUTATION — magnitude.claimed_value and magnitude.baseline_value both point at quantity-ledger ids (Q##) rather than four hand-retyped copies of a number — and it pairs that with the sharpest coverage signal (contemporaneous_uncited members the paper never cited = a 'did they miss it' probe the judge can run). The three-way delta_status (quantified / qualitative_only / claimed_unresolved / not_claimed) with resolution_gap_note that names EXACTLY what could not be pinned down is the best honesty-about-absence mechanism here. realized_in requiring >=1 real claim id is a genuine anti-puffery lock. But you have unstated Goodhart holes and under-specified determinism, and I will not let them slide:\n\n1. TEMPORAL HOLE (the big one). Your SOTA cutoff is paper_pub_date, 'mirrored from PAPER.md frontmatter.' Publication date is author/journal-controlled and routinely lags true precedence by months. A neighborhood frozen at pub_date can silently include downstream citations of the authors' own preprint and can exclude contemporaneous competitors who published between precedence and pub_date — both directions flatter the novelty claim. Proposal #3's precedence_date (earliest EXTERNALLY-timestamped disclosure — preprint hash, registration receipt) is strictly better and you should adopt it. As written, 'was this novel at the time' is anchored to a date the author benefits from moving.\n\n2. BASELINE FABRICATION SURFACE. magnitude.baseline_value permits ext_quantity{value,unit,source_anchor} — i.e., the prior work's number as restated BY THIS PAPER. Nothing forces verification that RW01 actually reports that value; papers misquote baselines downward constantly. You need #3's source_verified-vs-self_reported distinction with a fetch_timestamp on the prior work's own reported number. Right now a fabricated delta and a real one are structurally indistinguishable once delta_status=quantified.\n\n3. DETERMINISM GAP on the delta arithmetic. absolute_delta, relative_delta (relative_delta: not_computed is allowed), comparator, and direction are captured but you never specify WHO computes them or with what sign/rounding/direction convention. This is the one sub-part that should be Class-A deterministic (given two Q## and a direction, the delta is a pure function) and you leave it as free-entered numbers — a place to quietly round in your favor. Specify the formula and make it compiler-computed, not author-entered.\n\n4. coverage_stats.neighbor_recall: float[0,1] — recall against WHAT denominator? Without a ground-truth neighbor set there is no recall; this reads as a number that looks rigorous but cannot be computed honestly. Define the denominator or delete it — an un-computable metric is itself a fabrication surface.\n\n5. second_resolver_audit is optional / not_run. For a Class-C claim that the anchor set is auditable, inter-resolver overlap (your Jaccard) is the load-bearing trust signal; making it optional means most anchor sets ship with a single unverified resolver. Require it above a stakes threshold, or the auditability is aspirational.\n\n6. STRATEGIC UNDER-CLAIMING. You assert the four delta_status states carry 'no relative stigma,' but that is a promise about a downstream judge you do not control. If NOVELSCORE penalizes claimed_unresolved even slightly, the dominant strategy is to relabel a real-but-unpinned claim as not_claimed to dodge the stigma — gaming by omission. You must emit these states in a judge-blind way or encode the non-penalty as a hard constraint ON the judge, not a hope.\n\n7. Contribution typing is 'semantic but constrained by enum' with extraction_confidence, but you give NO adjudication/inter-rater protocol for primary_type. That is the Class-B reliability core and it is hand-waved — two compilers can type the same paper new_method vs extension_of_prior_method and nothing resolves it.

**DAL/2 — The Delta-Anchor Ledger, Hardened (Precedence-Anchored, Compiler-Computed, Dual-Rater)**  ·  _source: DAL (Delta-Anchor Ledger, finalist A)_

A novelty judge (NOVELSCORE/LENS) needs three structured inputs the ARA does not store today: what KIND of contribution this is, how BIG the claimed improvement is over specific named prior work, and a temporally-honest neighborhood of that prior work to judge against. DAL/2 keeps DAL's three small, jointly-referenced, prose-renderable sidecars — `logic/contributions.yaml`, `logic/delta_ledger.yaml`, `logic/sota_anchor.yaml` — but closes every hole the reviewer found: the SOTA cutoff is now the EXTERNALLY-timestamped precedence date, not the author-movable pub date; the delta arithmetic is a COMPILER-COMPUTED pure function of two quantity-ledger ids and a direction (Class A), never an author-entered number; each baseline number carries a source_verified-vs-self_reported grade with a fetch_timestamp on the prior work's own reported value; the second-resolver audit is REQUIRED above a stakes threshold; the un-computable `neighbor_recall` is deleted and replaced with defined denominators; contribution typing is dual-rater with an adjudication protocol and a calibration kappa; and the honest-absence non-penalty is emitted judge-blind AND encoded as a hard constraint ON the judge plus a deterministic suppressed-comparison probe that punishes gaming-by-omission. None of this scores novelty — it makes novelty auditable and its inputs un-fabricable.

- **logic/contributions.yaml — dual-rater typed contribution ledger** (YAML, one record per CT## block, sibling to logic/problem.md and logic/claims.md; renders to a one-line-per-contribution prose table) — Names each distinct contribution, typed TWICE (author-framed vs compiler-assessed) from a closed versioned taxonomy, anchored to the claims that realize it. Divergence between the two typings is logged as a signal, not laundered into one field. This is the LENS contribution-type input, made a first-class typed slot with a reliability protocol behind it instead of an inference the judge re-derives from prose.
  - fields: taxonomy_version : string — required — file-head, closed & versioned vocabulary
id : string CT## — required — stable across ARA versions once assigned
title : string — required — short paraphrase, not a re-statement of the claim
author_framed_type : {phrase: string, type: enum<taxonomy>|not_specified} — required — how the PAPER frames it, in its own words + the closest enum; kept SEPARATE so authorial spin is visible, never merged into the assessed field
compiler_assessed_type.primary : enum{new_method,new_theory_or_model,new_dataset_or_benchmark,empirical_finding,unexpected_finding,resolved_open_problem,refutation_of_prior_claim,replication,extension_of_prior_method,negative_result,tool_or_infrastructure,application_to_new_domain,synthesis_or_review,not_specified} — required, SINGLE value — the independent read
compiler_assessed_type.secondary : list[enum] — optional, default []
typing_rationale : string — required — 1-3 sentences justifying primary against the vocab's written decision rules (cites the discriminating rule, e.g. 'no new estimator introduced -> not new_method')
typing_confidence : enum{high,medium,low} — required
typing_divergence : enum{none,adjacent,conflicting} — required — computed vs author_framed_type per the taxonomy adjacency graph; 'conflicting' triggers the adjudication protocol
adjudication : {status: enum{not_required,pending,resolved}, second_rater: enum{compiler,human,not_run}, agreed_primary: enum<taxonomy>|unresolved, kappa_ref: string|not_applicable} — required
realized_in : list[C##] — required, length>=1 — every contribution grounds in >=1 real claim id or the record is INVALID (anti-puffery lock)
derived_from : list[G##/Insight] | not_specified — optional
surprise_context : {expectation_stated_in: O##|ext_ref|not_specified, expectation: string, contradiction: string} — REQUIRED iff type includes unexpected_finding, else omitted (structural absence)
resolves_gap : {gap_id: G##, opened_by: RW##|not_specified, opened_since: date|string|not_specified} — REQUIRED iff type includes resolved_open_problem
delta_ref : D##|none — required — 'none' legal ONLY if no comparative claim is made; cross-checked by the suppressed-comparison probe
provenance : {source_locator: string, extracted_by: enum{compiler,human,hybrid}} — required
  - example: taxonomy_version: "1.1"
contributions:
  - id: CT01
    title: "Simultaneous NMA ranking of all p-tau isoform+platform combinations"
    author_framed_type:
      phrase: "the first simultaneous network meta-analysis of p-tau isoforms"
      type: new_method
    compiler_assessed_type:
      primary: resolved_open_problem
      secondary: [synthesis_or_review]
    typing_rationale: "No new estimator, assay, or model is introduced; an established NMA framework is applied across a unified evidence network to resolve G1. Decision rule NM-2: 'reuse of a standard method on new inputs is not new_method.'"
    typing_confidence: high
    typing_divergence: conflicting
    adjudication:
      status: resolved
      second_rater: human
      agreed_primary: resolved_open_problem
      kappa_ref: "calib-2026Q2#row14"
    realized_in: [C01, C02]
    derived_from: [G1, G2, G3]
    resolves_gap: {gap_id: G1, opened_by: RW01, opened_since: "~2020, per O2"}
    delta_ref: D01
    provenance: {source_locator: "§3.2, §4.1", extracted_by: hybrid}
- **logic/delta_ledger.yaml — compiler-computed, source-verified claimed-improvement records** (YAML, one record per D## block, referenced by contributions.yaml delta_ref) — Turns 'we improve on prior work' into a JOINABLE, VERIFIABLE computation: which specific prior work (REFGRAPH RW## id), which specific number on each side (quantity-ledger Q## id, not four retyped copies), whether the prior work's number was independently fetched or merely restated by this paper, and — critically — a delta the COMPILER computes as a pure function of those ids, never the author. Three honest-absence states carry no relative stigma and are emitted judge-blind.
  - fields: id : string D## — required
contribution : CT## — required, back-reference
delta_status : enum{quantified,qualitative_only,claimed_unresolved,not_claimed} — required, no default — honest-absence field; emitted judge-blind (see protocol P6)
prior_works : list[{ref_id: RW##, external_id: mirrored from REFGRAPH, relation: enum{baseline,bounds,extends}}] — required iff delta_status in {quantified,qualitative_only}; forbidden if not_claimed
magnitude : object — required iff delta_status=quantified, else omitted. Sub-fields:
  claimed_value : Q## — required — id into the paper's own quantity ledger
  baseline_value : Q## | ext_quantity{value,unit} — required — a Q## when the prior work is itself an ARA; ext_quantity only for legacy prior work
  baseline_verification : enum{source_verified,self_reported} — required — source_verified = the prior work's OWN reported number was independently fetched, not trusted from this paper's restatement
  baseline_source_anchor : {this_paper: locator, prior_work: {locator: string, fetch_timestamp: timestamp}} — required iff baseline_verification=source_verified
  direction : enum{higher_is_better,lower_is_better,non_inferiority} — required
  comparator : enum{>,<,=,≈,non_inferior} — required
  unit_canonical : string — required — canonical unit from the quantity ledger; if the two Q## units are incompatible the record downgrades to qualitative_only with a note (never a silent cross-unit subtraction)
  absolute_delta : {value: number, computed_by: enum{compiler}, formula_id: string, computed_at: timestamp} — required, COMPILER-WRITTEN — author-entered values are rejected at validation
  relative_delta : {value: number|not_computable, computed_by: enum{compiler}, formula_id: string} — required — not_computable only when baseline=0 or non-ratio scale
  ci : string|not_specified — optional — carried verbatim from source, never author-derived
qualitative_statement : string — required iff delta_status in {qualitative_only,claimed_unresolved}
resolution_gap_note : string — required iff delta_status=claimed_unresolved — names EXACTLY what could not be pinned down
  - example: deltas:
  - id: D01
    contribution: CT01
    delta_status: quantified
    prior_works:
      - {ref_id: RW01, external_id: "10.1093/brain/awac333", relation: baseline}
    magnitude:
      claimed_value: Q17            # 0.94 AUC, this paper §4.1
      baseline_value: Q18           # 0.84 AUC, RW01's own Table 3
      baseline_verification: source_verified
      baseline_source_anchor:
        this_paper: "§4.1 Table 2"
        prior_work: {locator: "RW01 Table 3 row 'p-tau217'", fetch_timestamp: "2026-02-03T09:41:00Z"}
      direction: higher_is_better
      comparator: ">"
      unit_canonical: "AUC"
      absolute_delta: {value: 0.10, computed_by: compiler, formula_id: "delta.abs.v1", computed_at: "2026-02-03T10:00:11Z"}
      relative_delta: {value: 0.119, computed_by: compiler, formula_id: "delta.rel.v1"}
      ci: "[0.04, 0.16]"
  - id: D02
    contribution: CT02
    delta_status: claimed_unresolved
    prior_works: []
    qualitative_statement: "Paper states the ratio metric is 'more robust across platforms' without naming a comparator study."
    resolution_gap_note: "No RW## in related_work.md carries the specific platform-robustness comparison being invoked; magnitude un-pinnable."
- **logic/sota_anchor.yaml — precedence-frozen, dual-resolver SOTA neighborhood** (YAML, one file per ARA, produced by an external resolver protocol (not the compiler)) — The externally-resolved citation+kNN neighborhood a judge reconstructs the state-of-the-art against, frozen at the paper's EXTERNALLY-timestamped precedence date so 'was this novel at the time' can never leak future information nor be flattered by moving the pub date. Carries the contemporaneous_uncited 'did they miss it' probe and a REQUIRED second-resolver overlap above a stakes threshold.
  - fields: anchor_set_id : string — required
paper_time_anchor.publication_date : date|not_specified — required — recorded for reference, NOT the cutoff
paper_time_anchor.precedence_date : date — required — earliest EXTERNALLY-timestamped disclosure; THIS is the hard cutoff
paper_time_anchor.precedence_source : {type: enum{preprint,registration,submission_receipt,dataset_deposit,not_specified}, id: string, verified: bool, verify_method: string} — required — verified=true only if an external timestamp (preprint version hash, registry receipt) was resolved
cutoff_date : date — required — MUST equal precedence_date (validator-enforced; author cannot substitute a later date)
resolved_at : timestamp — required
retrospective_resolution : bool — required — true if resolved_at postdates cutoff_date by > tolerance (default 90d)
retrospective_gap_days : int — required if retrospective_resolution=true
resolver : {name,version,index_snapshot_id,embedding_model,k,method: enum{citation_graph,embedding_knn,hybrid},query_verbatim} — required, all sub-fields required for reproducibility
members : list[{ref_id: RW##|null, external_id: {doi|arxiv|openalex_id|s2_corpus_id} (>=1, existence-VERIFIED not format-checked), title, pub_date, relation: enum{predecessor_cited,benchmark_cited,contemporaneous_uncited,successor_excluded_by_cutoff}, cited_by_paper: bool, discovered_by_resolver: bool, resolution_confidence: enum{high,medium,low}}] — required, length>=0
coverage_stats : {citation_resolution_rate: float[0,1], resolver_overlap_jaccard: float[0,1]|not_run, calibration_recall: float[0,1]|not_applicable, n_members: int, n_contemporaneous_uncited: int} — required — calibration_recall is not_applicable unless this paper is in the curated calibration set with a hand-built ground-truth neighbor set
second_resolver_audit : {resolver2: {name,version}, overlap_jaccard: float, disagreement_notes: string} | required_but_missing | below_stakes_threshold — required field; value required_but_missing is a validation FAILURE when stakes>=threshold
status : enum{resolved,partial,pending_index,unavailable_for_domain,stale} — required
unresolved_reason : string|null — required if status in {partial,pending_index,unavailable_for_domain}
  - example: anchor_set_id: sota-che26-v1
paper_time_anchor:
  publication_date: 2026-01-14
  precedence_date: 2025-08-14
  precedence_source: {type: registration, id: "PROSPERO CRD420261327845", verified: true, verify_method: "registry API receipt, timestamp 2025-08-14T00:00Z"}
cutoff_date: 2025-08-14
resolved_at: 2026-02-03T10:00:00Z
retrospective_resolution: true
retrospective_gap_days: 173
resolver: {name: openalex-knn, version: "2026.01", index_snapshot_id: "oa-snap-20260201", embedding_model: specter2, k: 30, method: hybrid, query_verbatim: "plasma p-tau isoform network meta-analysis Alzheimer diagnostic accuracy"}
members:
  - {ref_id: RW01, external_id: {doi: "10.1093/brain/awac333"}, title: "Head-to-head comparison of 10 plasma p-tau assays", pub_date: 2023-04-01, relation: predecessor_cited, cited_by_paper: true, discovered_by_resolver: false, resolution_confidence: high}
  - {ref_id: null, external_id: {openalex_id: "W4392010123"}, title: "Pairwise NMA of p-tau181 vs p-tau217 in 3 cohorts", pub_date: 2025-06-02, relation: contemporaneous_uncited, cited_by_paper: false, discovered_by_resolver: true, resolution_confidence: medium}
coverage_stats: {citation_resolution_rate: 0.97, resolver_overlap_jaccard: 0.71, calibration_recall: not_applicable, n_members: 28, n_contemporaneous_uncited: 1}
second_resolver_audit: {resolver2: {name: semantic-scholar-knn, version: "2026.01"}, overlap_jaccard: 0.71, disagreement_notes: "S2 surfaced 2 clinical-trial records OpenAlex missed; both pre-cutoff, neither cited."}
status: resolved
unresolved_reason: null

  _Protocols:_
  - **P1 — Precedence-date resolution & verification** — At publication time, before the SOTA anchor set is built, to fix the novelty cutoff to a date the author cannot move in their favor.. 1) Enumerate candidate external disclosures: preprint versions (with immutable version hashes), trial/protocol registrations (with registry receipts), conference submission receipts, dataset deposits. 2) Take the EARLIEST whose timestamp is externally verifiable; record type, id, verify_method, verified=true. 3) If none is externally verifiable, set precedence_source.verified=false, precedence_date=publication_date, and mark cutoff as author-anchored (a first-class honest state, scored equal — but flagged so a judge weights it). 4) Set cutoff_date = precedence_date; validator rejects any anchor set whose cutoff != precedence_date.
    - reliability/reproducibility: Class B. Reliability comes from external timestamps: two independent resolvers hitting the same preprint hash / registry receipt get the same date. Failure mode: no external disclosure exists (common for closed venues) -> verified=false path, never fabricated. Dedup: multiple preprint versions collapse to the earliest hash.
    - constraints: Ecosystem must provide: a preprint version-hash oracle, a registry receipt lookup, and immutable submission receipts. Absent these, precedence degrades honestly to publication_date with verified=false.
  - **P2 — Compiler-computed delta arithmetic** — Whenever delta_status=quantified. This is the one sub-part promoted to Class A determinism.. 1) Resolve claimed_value and baseline_value to canonical units via the quantity ledger; if units are incompatible, DOWNGRADE to qualitative_only with a note (no cross-unit subtraction). 2) Apply formula by direction. formula delta.abs.v1: higher_is_better -> absolute_delta = claimed - baseline; lower_is_better -> absolute_delta = baseline - claimed; non_inferiority -> absolute_delta = claimed - baseline reported against margin. Sign convention: POSITIVE = improvement in the claimed direction. formula delta.rel.v1: relative_delta = absolute_delta / |baseline|; not_computable if baseline==0 or non-ratio scale. 3) No rounding on stored values — full ledger precision is carried; display rounding is a rendering concern only. 4) Stamp computed_by=compiler, formula_id, computed_at. Validator REJECTS any author-supplied absolute/relative value.
    - reliability/reproducibility: Deterministic: given two Q## and a direction, the delta is a pure, versioned function; identical inputs yield byte-identical output across runs and implementations. Formula ids are versioned so a re-computation is auditable.
    - constraints: Ecosystem must provide: quantity-ledger canonical-unit conversion and a published formula registry (delta.abs.v1, delta.rel.v1) with test vectors.
  - **P3 — Baseline source-verification** — Whenever a baseline_value restates a prior work's number, to separate a real delta from a misquoted-downward one.. 1) If the prior work is itself an ARA, join baseline_value directly to its Q## (source_verified by construction). 2) Else, fetch the prior work's OWN reported number from its artifact/PDF at a recorded locator; if it matches the paper's restatement, set baseline_verification=source_verified with a fetch_timestamp. 3) If it cannot be fetched or disagrees, set self_reported and record the discrepancy in disagreement notes; NEVER silently adopt the paper's restatement as verified.
    - reliability/reproducibility: Class B. Reliability: the fetch is reproducible from the locator+timestamp; two auditors fetching RW01 Table 3 get the same figure. Failure mode: paywalled/unavailable prior work -> self_reported (honest, scored equal but visibly weaker evidence). Detects the fabricated-delta surface the reviewer named: a fabricated baseline cannot be source_verified.
    - constraints: Ecosystem must provide: retrievable prior-work artifacts and stable within-document locators. In the all-artifacts-available world this is universal; in the transition, self_reported is the honest fallback.
  - **P4 — Dual-resolver SOTA anchoring with stakes-gated audit** — Building sota_anchor.yaml, especially for high-stakes contributions.. 1) Run resolver 1 (citation+kNN) at cutoff_date, freezing the index snapshot. 2) Read the stakes level from the genre manifest / linked claims (e.g. any delta_status=quantified, or a contribution typed refutation_of_prior_claim / new_method above a manifest threshold). 3) If stakes>=threshold, RUN a second independent resolver and compute overlap_jaccard; second_resolver_audit=required_but_missing is a validation failure. 4) Members surfaced by a resolver but never cited by the paper are tagged contemporaneous_uncited (the 'did they miss it' probe). 5) Existence-verify every external_id (resolve the DOI/OpenAlex id, not just format-check it).
    - reliability/reproducibility: Class C, designed for reproducibility+auditability: frozen index snapshot + verbatim query + version pins make a re-run reproducible; the second resolver's Jaccard is the load-bearing inter-resolver trust signal. run-to-run drift is bounded by index_snapshot_id.
    - constraints: Ecosystem must provide: >=2 independent snapshotted literature indexes, an embedding model registry, and id-existence verification endpoints.
  - **P5 — Contribution-typing dual-rater adjudication** — Every contribution; the Class-B reliability core for primary_type.. 1) The compiler assigns compiler_assessed_type WITH a rationale citing the taxonomy's written decision rule. 2) Compute typing_divergence against author_framed_type using the taxonomy's published adjacency graph (none / adjacent / conflicting). 3) On 'conflicting', or on typing_confidence=low, a SECOND independent rater (second compiler instance or human) re-types blind to the first; disagreement is resolved to agreed_primary and logged, never silently averaged. 4) A rolling calibration set of gold-typed papers is re-typed each release; Cohen's/Fleiss kappa is published as kappa_ref. Types below a kappa floor are flagged as low-reliability categories the judge should down-weight.
    - reliability/reproducibility: Class B. Reliability is MEASURED (kappa on a calibration set) rather than assumed; the closed versioned vocabulary with written decision rules minimizes rater degrees of freedom. Failure mode: genuinely ambiguous contributions -> low confidence + adjudication, surfaced not hidden.
    - constraints: Ecosystem must provide: the versioned taxonomy with per-type decision rules and an adjacency graph, a maintained calibration set, and a second rater (agentic or human) on demand.
  - **P6 — Judge-blind emission & NOVELSCORE non-penalty contract** — At the interface between DAL/2 and the downstream novelty judge, to prevent gaming-by-omission.. 1) delta_status and every honest-absence value are emitted through a judge-blind channel: the judge receives contribution+delta records with absence states TOKENIZED to a neutral symbol during scoring, so it cannot preferentially reward not_claimed over claimed_unresolved. 2) A hard scoring contract (a manifest constraint the judge must satisfy and that is unit-tested against the judge) asserts: score(not_claimed) == score(claimed_unresolved) == score(resolved-with-honest-note) on the honesty axis; only the EVIDENCE axis may differ. 3) A DETERMINISTIC suppressed-comparison probe scans claims.md for comparative language ('outperforms', 'better than', 'improves on') whose contribution carries delta_ref=none; each hit emits a suppressed_comparison flag. This makes omission COSTLIER than an honest claimed_unresolved, inverting the gaming incentive.
    - reliability/reproducibility: Class C for the judge contract (verified by calibration papers with known-equal honesty states that must receive equal scores) + deterministic for the suppression probe (pure text/graph cross-check). The non-penalty is enforced, not hoped.
    - constraints: Ecosystem must provide: a judge harness that accepts the scoring contract as a hard constraint and exposes a test hook; a comparative-language lexicon for the probe (versioned).

  _Metrics afforded:_
  - delta_computability_rate — fraction of comparative contributions whose delta is compiler-computed from two Q## ids → count(delta_status=quantified with both values as Q##) / count(contributions with delta_ref != none) [deterministic]; anti-Goodhart: Cannot be inflated by paraphrase: only records that JOIN two ledger ids and pass unit-compatibility count. Author-entered deltas are validation-rejected, so a fabricated-but-consistent number cannot raise the rate.
  - baseline_verification_rate — fraction of quantified deltas whose baseline is source_verified → count(baseline_verification=source_verified) / count(delta_status=quantified) [reliable-anchored]; anti-Goodhart: source_verified requires a real fetch with a timestamp against the prior work's own document; a fabricated baseline cannot be verified, so misquoting-downward lowers rather than raises the metric. self_reported is scored equal on honesty but visibly weaker on evidence.
  - typing_inter_rater_kappa — agreement on primary contribution type over the calibration set → Cohen/Fleiss kappa between independent raters on gold-typed calibration papers, per taxonomy version [reliable-anchored]; anti-Goodhart: Measured on a HELD calibration set the author cannot see; padding contributions cannot move it. Low-kappa categories are auto-flagged so the judge down-weights unreliable types instead of trusting a confident-looking label.
  - anchor_reproducibility (resolver_overlap_jaccard) — inter-resolver agreement on the SOTA neighborhood → |M1 ∩ M2| / |M1 ∪ M2| between two independent snapshotted resolvers at the frozen cutoff_date [reproducible]; anti-Goodhart: A single cherry-picked resolver cannot score well because the metric requires a second independent index to agree; required above a stakes threshold, so high-stakes anchor sets cannot ship single-sourced.
  - missed-prior-work signal — n_contemporaneous_uncited → count(members with relation=contemporaneous_uncited AND pub_date <= cutoff_date AND cited_by_paper=false) [reliable-anchored]; anti-Goodhart: Author cannot lower it by omission — it is produced by an EXTERNAL resolver over a frozen index, not by the paper's own reference list. Padding the reference list to zero it out forces citing the competitor, which is the honest outcome.
  - suppressed_comparison_flags — comparative language with no delta record → deterministic scan of claims.md comparative lexicon hits whose contribution has delta_ref=none [deterministic]; anti-Goodhart: Directly punishes gaming-by-omission (the reviewer's point 6): relabeling a real-but-unpinned claim as not_claimed to dodge stigma now trips a flag, making omission costlier than an honest claimed_unresolved.
  - precedence_verification_rate — fraction of anchor sets with an externally-verified cutoff → count(precedence_source.verified=true) / count(anchor sets) [reliable-anchored]; anti-Goodhart: Cutoff is bound to an external timestamp (preprint hash/registry receipt); moving the pub date later does nothing because cutoff_date must equal the verified precedence_date. verified=false is honest but visibly weaker, so there is no gain from a fabricated early date (it would fail external verification).

  _Tradeoffs:_ Cost: DAL/2 asks more at publication time — a second typing rater, a baseline fetch, a second resolver above threshold. Mitigation: all three are gated (second rater only on conflicting/low-confidence typing; source_verified degrades honestly to self_reported when prior work is unavailable; second resolver only above a stakes threshold), so low-stakes papers stay cheap. Fabrication surfaces that remain: (a) a fabricated precedence disclosure — mitigated by external timestamp verification (verified=false if it fails); (b) a fabricated self_reported baseline — mitigated by being un-promotable to source_verified and by the source anchor demanding a fetchable locator; (c) rationale-padding in typing_rationale — mitigated because rationale is not scored for length and must cite a specific decision rule, and kappa (not prose volume) is the reliability metric. Risk: the judge-blind emission + scoring contract depends on a cooperating judge harness; if NOVELSCORE ignores the contract the non-penalty weakens — mitigated by unit-testing the contract against the judge on calibration papers and by the deterministic suppressed-comparison probe, which works regardless of the judge. Residual risk: the calibration set can itself become a target if public; mitigate by rotating held-out calibration papers per release.

  _Open questions:_ 1) Precedence for work with NO external disclosure (closed venues, industry) still falls back to author-anchored pub date — is there a better verifiable floor than verified=false? 2) The comparative-language lexicon for the suppression probe is domain-sensitive ('outperforms' vs 'is consistent with'); how is it maintained across fields without over- or under-flagging? 3) calibration_recall is only defined for the curated calibration set — for the vast majority of papers there is genuinely no ground-truth neighbor denominator, so neighborhood COMPLETENESS remains only inter-resolver-corroborated, never absolutely measured. 4) The stakes threshold that gates the second resolver is read from the genre manifest — who sets it, and can it be gamed by under-declaring stakes? 5) Cross-unit deltas that require domain-specific canonicalization (e.g. hazard ratio vs odds ratio) may downgrade to qualitative_only more often than ideal; a richer unit-algebra could recover some.

  _Changes from critique:_ Addressed all seven critique points directly. (1) TEMPORAL HOLE: replaced paper_pub_date cutoff with an externally-timestamped precedence_date + precedence_source{verified,verify_method}; validator enforces cutoff_date==precedence_date so the author cannot move it; added retrospective_resolution flag + gap_days. (2) BASELINE FABRICATION: added baseline_verification enum{source_verified,self_reported} with baseline_source_anchor.prior_work.fetch_timestamp and protocol P3 requiring an independent fetch of the prior work's own number; a fabricated baseline is now structurally un-verifiable. (3) DETERMINISM GAP: delta arithmetic is now COMPILER-computed via versioned formulas (delta.abs.v1/delta.rel.v1) with an explicit sign convention, canonical-unit resolution, no-rounding rule, and computed_by=compiler stamp; author-entered deltas are validation-rejected (promoted to Class A). (4) neighbor_recall: DELETED the un-computable metric; replaced with citation_resolution_rate (deterministic), resolver_overlap_jaccard (reproducible), and calibration_recall (not_applicable unless a curated ground-truth denominator exists). (5) SECOND RESOLVER: made second_resolver_audit REQUIRED above a stakes threshold — required_but_missing is a validation failure. (6) STRATEGIC UNDER-CLAIMING: honest-absence states are emitted judge-blind, the non-penalty is encoded as a hard scoring contract unit-tested against the judge, and a deterministic suppressed_comparison probe makes gaming-by-omission costlier than an honest claimed_unresolved. (7) TYPING ADJUDICATION: split into author_framed_type vs compiler_assessed_type with a typing_rationale citing decision rules, typing_divergence via a taxonomy adjacency graph, a dual-rater adjudication object, and a measured calibration kappa (protocol P5).

  _Adopted from competitor:_ From NOVEL-ANCHOR I adopted: (a) precedence_date + precedence_source{type,id,verified} as the true novelty cutoff instead of pub date; (b) the author_framed_type vs compiler_assessed_type separation with an explicit typing_rationale and typing_confidence, so authorial spin is visible not laundered; (c) magnitude verification as source_verified vs self_reported with a fetch_timestamp on the prior work's own number; (d) the retrospective_resolution flag + retrospective_gap_days for honesty about when the snapshot was built relative to the cutoff; (e) existence-VERIFIED external ids (resolve the DOI, not just format-check it) and the discovered_by_resolver coverage naming, merged with DAL's existing contemporaneous_uncited probe.

  _Why it wins:_ NOVEL-ANCHOR grades magnitude as computed/author_claimed/not_specified but — exactly like the flaw the reviewer flagged in DAL — never specifies WHO computes the delta or with what formula/sign/rounding; when its type=author_claimed the value is still author-entered. DAL/2 promotes that sub-part to true Class-A determinism (compiler-computed pure function with versioned formulas and test vectors), which NOVEL-ANCHOR does not. NOVEL-ANCHOR also (a) leaves the non-penalty as a hope about the downstream judge — DAL/2 encodes it as a hard, unit-tested scoring contract AND adds a deterministic suppressed-comparison probe that punishes gaming-by-omission; (b) does not require a second resolver — DAL/2 gates it as mandatory above a stakes threshold; (c) packs everything into one large novelty.yaml, which strains the human-readable/renderable principle — DAL/2 keeps three small, separately-renderable sidecars that each map to one existing prose surface (contributions↔insight, delta↔quantities, anchor↔related_work); (d) does not enforce realized_in>=1 real claim — DAL/2 keeps that anti-puffery lock. In short, DAL/2 takes NOVEL-ANCHOR's best temporal and verification ideas and pairs them with strictly stronger determinism, mandatory auditability, and enforced (not hoped) honesty symmetry.


---


## NOVELSCORE — Calibrated novelty & significance scoring

_Class C — irreducibly semantic (reproducibility + auditability)_


**Judge rationale:** Class-C demands reproducibility + auditability of an admittedly subjective score, and punishes Goodhart holes and fabrication pressure. All four correctly refuse determinism and freeze inputs/hash artifacts, so the separation is at the anti-gaming and honesty layer. #3 wins because it is the only design that instruments the fabrication surface directly (per-field provenance distinguishing vetted vs unconfirmed-AI claims), guards against verbosity/injection gaming (input_cap, injection_detector), builds a Goodhart-aware citation diagnostic, and honestly decomposes its CI (ensemble disagreement + calibration residual) while publishing calibration MAE against a rotating partially-hidden expert set. #2 wins the second slot for the strongest anti-curation architecture — an independently-built, publication-time-frozen neighborhood the author cannot curate, plus hard redaction, a red-team judge, and append-only runs that make cherry-picking visible. #0 is very close and actually beats both winners on ONE axis — concrete calibration measurement (held-out MAE, 90% CI coverage, drift-audit date, ICC/MAD) and explicit within-strata z/percentile cross-discipline normalization — but it leans on prompt-level forbidden_features rather than hard redaction, lacks a publication-time freeze against future-citation leakage, and does not build cherry-pick resistance, leaving a larger gaming surface than the two winners. #1 is a weaker near-twin of #0 from the same model: cleaner input separation and useful aggregation_code_hash + rerun_policy, but it shows a calibration_set_id with no measured human-agreement figures, concretizes neither calibration maintenance nor cross-discipline normalization, and adds little over #0 — the lowest marginal rigor of the set.


### Finalist A (refined)

> _Judge critique it answered:_ LENS-ON-ARA (#3) is the strongest design because it is the only one that treats the score as a Goodhart target and instruments against it: per-field provenance{author_asserted|ai_suggested|reviewer_confirmed}, an author_citation_overlap_with_neighborhood diagnostic, an input_cap so verbosity can't buy score, an injection_detector_version, ≥3 distinct vendors, and a published calibration_mae_at_release with a rotating, partially-hidden expert set. That is a real fabrication-surface accounting, not a checklist. Now the holes you must close:

1) Your central promise — 'temperature 0 + seed → re-running reproduces the identical score' — is FALSE for hosted LLMs. Batching, MoE routing, and non-associative float reduction make production inference non-deterministic even at temp 0. Reproducibility here can only mean 'archived transcript replay + hash match,' NOT 're-inference yields the same tokens.' State this explicitly or a funder who re-runs gets a different number and your reproducibility claim collapses. Pin the definition: authoritative score = hash of archived transcripts; re-inference is a drift audit, not a reproduction.

2) The overlap diagnostic is clever but you never write the decision rule. 'Very low overlap flags self-serving OR genuinely under-cited; very high overlap + zero delta flags incremental' is an ambiguity, not a flag — you never convert flag→score adjustment. An author games it trivially: cite the entire neighborhood (overlap→high) while burying the strongest comparator in a 200-item list, and still assert delta. Specify the threshold, the disambiguation test, and the exact effect on the score.

3) Publishing a non-secret rubric AND naming the exact judges/vendors makes the whole pipeline white-box — directly prose-optimizable against known evaluators. You need a held-out/secret rubric component or adversarial rubric rotation; a fully public rubric + fixed known judges is a stationary target.

4) Your CI combines ensemble disagreement + calibration residual but omits the human-panel reliability term. If expert inter-rater ICC is ~0.5, that is a structural MAE floor your CI hides. Report per-discipline expert N and inter-expert agreement, and fold human-panel noise into the interval — otherwise the CI is dishonestly narrow.

5) provenance=ai_suggested is recorded but nothing forces the ensemble to DISCOUNT an unvetted AI-suggested delta. Where is the mechanism preventing an unconfirmed AI guess from inflating novelty? Recording provenance without a weighting rule is bookkeeping theater.

6) Cross-discipline comparability is underspecified: discipline_taxonomy.code exists but you never show how oncology-78 is made comparable to pure-math-78. #0 shows explicit within-strata z/percentile; you must match that or a funder ranking across fields gets apples-to-oranges.

**LENS-ON-ARA/2: Transcript-Anchored, Comparator-Complete Novelty & Significance Scoring**  ·  _source: ?_

Novelty and significance are irreducibly subjective, so this design does not compute them — it structures the judge's inputs, pins what "reproducible" actually means for hosted LLMs, and closes every scoring degree of freedom the critique exposed. The authoritative score is the hash of an archived judge transcript bundle, NOT a re-inference result; re-running is a drift AUDIT (bounded tolerance), never a reproduction claim, because batching/MoE/float-nonassociativity make temp-0 hosted inference non-deterministic. Three load-bearing rules replace the old ambiguities: (1) a comparator-completeness test that caps a delta claim at "incremental" whenever the single strongest REFGRAPH predecessor is cited-but-unaddressed — killing the "bury the comparator in a 200-item list" game; (2) a provenance ceiling that hard-caps how far an unvetted ai_suggested delta can move novelty (zero uplift without independent REFGRAPH corroboration); (3) a three-term confidence interval that folds in per-discipline human-panel ICC noise so the CI cannot be dishonestly narrow when experts themselves disagree. Cross-discipline comparability is delivered by explicit within-strata z-score/percentile against dated reference cohorts, and the rubric ships a public axis set PLUS a rotating held-out probe set so the pipeline is not a stationary white-box target.

- **NOVELANCHOR (novel_anchor.yaml)** (YAML, logic/novel_anchor.yaml, list of contribution records (NA##)) — The ARA's own contribution claim, one record per contribution locus, separated from prose so the judge evaluates a bounded, grounded claim instead of re-deriving it from narrative. Strictly INPUT the author asserts about itself; never the score. Every delta carries provenance that drives a downstream weighting ceiling, and a surprise triple stolen from LENS-ARA. Interoperates with claim ids (C##), gap/open-problem ids (G##/O##), refs.yaml (RW##), quantities.yaml, and the genre manifest paper_type.
  - fields: ara_id: string — required. | novelanchor_version: string — required. | contributions[]: list — required, may be single. Each: {contribution_id: NA## — required | contribution_type: enum{new_method,new_dataset,new_theory,unexpected_finding,resolved_open_problem,replication,negative_result,synthesis_or_meta_analysis,tool_or_resource,combination,not_specified} — required; not_specified scored EQUAL to a filled value (honest absence for e.g. a pure replication) | locus: {claims:[C##], gaps:[G##], insight: ref} — required, ≥1 non-empty OR not_specified | claimed_delta: {statement: string, magnitude: enum{incremental,substantial,foundational,not_specified}, anchor: C##/G##/insight, source_anchor:{file,locator,quote}} — required; anchor must resolve or the record is null-with-reason, never a floating assertion | delta_provenance: enum{author_asserted,ai_suggested,reviewer_confirmed} — required; drives provenance_ceiling (see protocol) | addressed_comparators: list[{ref: RW##, relation: enum{imports,bounds,baseline,extends,refutes}, source_anchor:{file,locator}}] — required, may be empty; the relation edges are what the completeness test reads to decide a strongest comparator is 'addressed' | surprise_indicator: {stated_prior_expectation: prose-citing-O##, observed_outcome: prose-citing-C##, surprise_class: enum{none,mild,moderate,high,not_specified}} — required | prior_attempts_acknowledged: list[RW##] — required, honest empty list scored equal only if REFGRAPH neighborhood is also thin}. | discipline_taxonomy: {scheme: enum{openalex_concept,mesh,arxiv_category}, code: string} or not_specified — required for cross-discipline normalization. | publication_date: date or not_specified — required, pins the REFGRAPH snapshot.
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
novelanchor_version: "2.0"
discipline_taxonomy: {scheme: openalex_concept, code: "C2779134260"}
publication_date: 2026-01-14
contributions:
  - contribution_id: NA01
    contribution_type: synthesis_or_meta_analysis
    locus: {claims: [C01,C02,C05], gaps: [G01], insight: KEY_INSIGHT}
    claimed_delta:
      statement: "First NMA placing all major p-tau217/181/231 platform-isoform combinations in one connected network."
      magnitude: substantial
      anchor: G01
      source_anchor: {file: logic/problem.md, locator: "Key Insight", quote: "Cast every biomarker+platform combination as a distinct node..."}
    delta_provenance: ai_suggested
    addressed_comparators:
      - {ref: RW01, relation: baseline, source_anchor: {file: logic/related_work.md, locator: "RW01 Delta"}}
      - {ref: RW04, relation: bounds, source_anchor: {file: logic/related_work.md, locator: "RW04 Delta"}}
    surprise_indicator:
      stated_prior_expectation: "O2: field assumed p-tau181 and p-tau217 roughly comparable"
      observed_outcome: "C01: p217_MS P-score 0.859 vs p181_IA 0.117"
      surprise_class: moderate
    prior_attempts_acknowledged: [RW01, RW04]
- **REFGRAPH (refgraph.yaml)** (YAML, trace/refgraph.yaml, generated by an external resolver pass) — Independently-resolved, publication-time-pinned SOTA neighborhood the judge compares NOVELANCHOR against — built by a resolver, never the author, so the 'done before?' landscape cannot be curated. Adds the load-bearing strongest_comparators + comparator_completeness block that converts undisclosed/unaddressed prior art into a concrete score cap. Sibling of the normalized refs.yaml ledger (Class B artifact).
  - fields: index_snapshot_id: string — required; literature index version dated at-or-shortly-after publication_date, never later than run_time minus embargo (no future-citation leakage). | embedding_model: string (versioned) — required. | cited_refs: list[{id: RW##, external_id: DOI/OpenAlex/arXiv or not_specified, resolved: bool, reason?: string}] — required; unresolved kept, not dropped. | neighborhood: list[{ext_id, similarity: float[0,1], published_before: bool, relation_type: enum{predecessor,contemporary,unrelated}}] — required, size k (default 200), retrieved by embedding search over claimed_sota terms + concepts.md, NOT over the author's citation list. | strongest_comparators: list[{ext_id, similarity, matched_ref: RW##-or-null, cited_by_paper: bool, addressed_by: NA##-or-null}] — required; the top-m (default 5) published_before predecessors by similarity. matched_ref/addressed_by are joined against NOVELANCHOR.addressed_comparators — this is the input to the completeness cap. | coverage_stats: {cited_count:int, resolved_count:int, neighborhood_size:int, author_citation_overlap_with_neighborhood: float[0,1] or not_computable, comparator_completeness: float[0,1] or not_computable} — required. comparator_completeness = fraction of strongest_comparators that are both cited_by_paper AND addressed_by a typed relation edge. | insufficient_coverage_flag: bool — required; true when the subfield index is too sparse to support a neighborhood (honest null — must NOT be read as 'confirmed novel').
  - example: index_snapshot_id: openalex-2026-01-20
embedding_model: s2-specter2-v2
cited_refs:
  - {id: RW01, external_id: "10.1093/brain/awac333", resolved: true}
  - {id: RW09, external_id: not_specified, resolved: false, reason: "author-year prose cite, no DOI"}
neighborhood:
  - {ext_id: "10.1002/alz.13001", similarity: 0.81, published_before: true, relation_type: predecessor}
  - {ext_id: "10.1001/jamaneurol.2024.5567", similarity: 0.79, published_before: true, relation_type: predecessor}
strongest_comparators:
  - {ext_id: "10.1002/alz.13001", similarity: 0.81, matched_ref: RW01, cited_by_paper: true, addressed_by: NA01}
  - {ext_id: "10.1001/jamaneurol.2024.5567", similarity: 0.79, matched_ref: null, cited_by_paper: false, addressed_by: null}
coverage_stats:
  cited_count: 30
  resolved_count: 27
  neighborhood_size: 200
  author_citation_overlap_with_neighborhood: 0.34
  comparator_completeness: 0.60
insufficient_coverage_flag: false
- **judge_ensemble_config.yaml** (YAML, versioned, in a shared registry, referenced by hash from each report) — Version-pinned spec of the ensemble AND the rubric split into a public axis set plus a rotating held-out probe set, so the pipeline is not a stationary white-box target. A score traces to exact model/prompt/rubric versions; the held-out component is hash-committed before the epoch and disclosed only after it closes.
  - fields: config_version: string (semver) — required. | judges: list[{judge_id, model_id, model_version, vendor, prompt_template_hash, role: enum{primary,red_team}, temperature:0, seed:int}] — required; min 5, ≥3 distinct vendors/model families (anti common-mode), ≥1 red_team (adversarial for/against) per run. | rubric: {rubric_version: string, public_axes: list[{axis_id, name, anchors: prose}], held_out_probe_set_hash: sha256, probe_rotation_epoch: string, disclosure_policy: "probes published after epoch close"} — required; public_axes are the disclosed scoring dimensions, held-out probes are secret targeted checks rotated per epoch. | redaction_policy: {redact:[authors,institutions,venue,doi]} — required; judges never see identity. | input_cap: {max_tokens_brief:int} — required; bounds prose excerpt so verbosity cannot buy score. | injection_detector_version: string — required. | calibration_epoch: string — required; ties runs to a named calibration curve. | calibration_mae_at_release: float — required; ensemble MAE vs held-out expert set at this version's release, published alongside.
  - example: config_version: "3.0.0"
calibration_epoch: "2026.Q2"
judges:
  - {judge_id: J1, model_id: claude, model_version: "opus-4.8", vendor: anthropic, prompt_template_hash: "a1b2c3", role: primary, temperature: 0, seed: 7}
  - {judge_id: J2, model_id: gpt, model_version: "5.2", vendor: openai, prompt_template_hash: "a1b2c3", role: primary, temperature: 0, seed: 7}
  - {judge_id: J3, model_id: gemini, model_version: "2.5-pro", vendor: google, prompt_template_hash: "a1b2c3", role: primary, temperature: 0, seed: 7}
  - {judge_id: J4, model_id: llama, model_version: "4-405b", vendor: meta, prompt_template_hash: "a1b2c3", role: primary, temperature: 0, seed: 7}
  - {judge_id: J5, model_id: claude, model_version: "opus-4.8", vendor: anthropic, prompt_template_hash: "d4e5f6", role: red_team, temperature: 0, seed: 13}
rubric:
  rubric_version: "lens-rubric-2.0"
  public_axes:
    - {axis_id: AX1, name: novelty_vs_neighborhood, anchors: "..."}
    - {axis_id: AX2, name: significance_if_true, anchors: "..."}
    - {axis_id: AX3, name: surprise, anchors: "..."}
  held_out_probe_set_hash: "9f8e7d..."
  probe_rotation_epoch: "2026.Q2"
  disclosure_policy: "probes published after epoch close"
redaction_policy: {redact: [authors, institutions, venue, doi]}
input_cap: {max_tokens_brief: 4000}
injection_detector_version: "inj-det-1.2"
calibration_mae_at_release: 8.4
- **calibration_registry.yaml** (YAML, versioned per calibration_epoch, shared registry) — The rotating, partially-hidden human-expert calibration set AND the per-discipline reliability numbers the CI needs. Makes the human-panel noise floor explicit rather than hidden, and holds the dated reference cohorts used for cross-discipline normalization.
  - fields: calibration_epoch: string — required. | expert_panels: list[{discipline_code: string, expert_n: int, inter_expert_icc: float[0,1], scoring_scale: "0-100", rotation: enum{public,hidden}, hidden_fraction: float}] — required; expert_n and inter_expert_icc are published per discipline — a low ICC yields a wider CI, not a hidden narrow one. | reference_cohorts: list[{discipline_code, cohort_id, snapshot_date, n_papers, mean_raw_score: float, sd_raw_score: float}] — required; the within-strata distribution against which a raw score is z-scored/percentiled. | calibration_curve: {method: enum{isotonic,linear}, params_hash: sha256, fitted_on: cohort_id} — required; maps raw ensemble mean → calibrated 0-100. | mae_by_discipline: list[{discipline_code, mae: float, residual_sd: float}] — required.
  - example: calibration_epoch: "2026.Q2"
expert_panels:
  - {discipline_code: "C2779134260", expert_n: 11, inter_expert_icc: 0.62, scoring_scale: "0-100", rotation: hidden, hidden_fraction: 0.5}
  - {discipline_code: "math.AG", expert_n: 7, inter_expert_icc: 0.48, scoring_scale: "0-100", rotation: hidden, hidden_fraction: 0.5}
reference_cohorts:
  - {discipline_code: "C2779134260", cohort_id: onc-2026Q2, snapshot_date: 2026-04-01, n_papers: 480, mean_raw_score: 54.2, sd_raw_score: 14.1}
  - {discipline_code: "math.AG", cohort_id: math-ag-2026Q2, snapshot_date: 2026-04-01, n_papers: 120, mean_raw_score: 49.7, sd_raw_score: 17.9}
calibration_curve: {method: isotonic, params_hash: "c0ffee...", fitted_on: onc-2026Q2}
mae_by_discipline:
  - {discipline_code: "C2779134260", mae: 7.9, residual_sd: 9.6}
  - {discipline_code: "math.AG", mae: 11.2, residual_sd: 13.4}
- **novelty_score_report.yaml** (YAML, novelty/runs/{run_id}/report.yaml, append-only (one per run, never overwritten)) — The produced, append-only output: the authoritative transcript-hash score, the three-term CI, the discipline-normalized percentile, the comparator/provenance adjustments actually applied, and the drift-audit record. This is what a funder audits.
  - fields: assessment_run_id: string (timestamp+hash) — required. | config_hash: sha256 — required; pins judge_ensemble_config. | input_bundle_hash: sha256 — required; the redacted brief+NOVELANCHOR+REFGRAPH all judges saw. | score_transcript_bundle_hash: sha256 — required; AUTHORITATIVE. The score is defined as the aggregation over THESE archived transcripts. Re-inference does NOT redefine it. | archive_uri: string — required; immutable transcript store. | raw_ensemble: {per_judge:[{judge_id, novelty, significance, surprise, for_args:[anchor-ids], against_args:[anchor-ids]}], mean_raw: float} — required; every for/against arg must resolve to a real anchor id or is structurally discounted. | applied_adjustments: {comparator_completeness_cap: enum{none,incremental_cap} , provenance_ceiling_applied: float, notes: prose} — required. | calibrated_score: float[0,100] — required; raw→calibrated via calibration_curve. | confidence_interval: {halfwidth: float, var_ensemble: float, var_calibration: float, var_human_panel: float, expert_n: int, inter_expert_icc: float} — required; halfwidth = sqrt(sum of the three vars). | discipline_normalized: {cohort_id, z: float, percentile: float[0,100]} — required; the ONLY cross-discipline-comparable number. | drift_audit: {reinference_date, reinference_bundle_hash, token_divergence: float, score_delta: float, within_tolerance: bool} or not_run — required field, value may be not_run.
  - example: assessment_run_id: r-2026-07-06T12:00Z-4a91
config_hash: "3f..."
input_bundle_hash: "7b..."
score_transcript_bundle_hash: "e2a9..."
archive_uri: "s3://lens-archive/r-4a91/"
raw_ensemble:
  per_judge:
    - {judge_id: J1, novelty: 61, significance: 70, surprise: 55, for_args: [NA01, RW01], against_args: ["10.1001/jamaneurol.2024.5567"]}
  mean_raw: 58.5
applied_adjustments:
  comparator_completeness_cap: incremental_cap
  provenance_ceiling_applied: 0.3
  notes: "NA01 delta is ai_suggested and strongest comparator 10.1001/jamaneurol.2024.5567 uncited+unaddressed; novelty uplift zeroed pending corroboration."
calibrated_score: 47.0
confidence_interval: {halfwidth: 12.4, var_ensemble: 40.1, var_calibration: 92.2, var_human_panel: 21.5, expert_n: 11, inter_expert_icc: 0.62}
discipline_normalized: {cohort_id: onc-2026Q2, z: -0.51, percentile: 30.5}
drift_audit: {reinference_date: 2026-07-13, reinference_bundle_hash: "e2b0...", token_divergence: 0.018, score_delta: 1.2, within_tolerance: true}

  _Protocols:_
  - **Reproducibility-as-replay + drift audit** — Every time a funder, challenger, or the author wants to verify a score, and whenever the ensemble config is re-run later.. 1. At scoring time, archive every judge's full request+response transcript to immutable storage; compute score_transcript_bundle_hash. 2. DEFINE the authoritative score as the deterministic, pure-function aggregation over those archived transcripts — this replay IS deterministic and hash-verifiable. 3. To 'reproduce', a third party replays the archived transcripts through the published aggregator and checks the hash + score match. 4. Re-inference (calling the models again) is a SEPARATE drift_audit: run the same config on the same input_bundle_hash, record token_divergence and score_delta vs archive, and pass/fail against a published drift_tolerance.
    - reliability/reproducibility: CLASS C. The central honesty move: hosted temp-0 LLM inference is NOT deterministic (dynamic batching, MoE expert routing, non-associative float reduction across GPUs), so 're-inference yields identical tokens' is FALSE and is never claimed. Reproducibility = archived-transcript replay + hash match. Re-inference is only a drift signal. A drift_delta beyond tolerance flags the config as unstable and triggers recalibration, not a silent score change.
    - constraints: Ecosystem must provide: immutable, addressable transcript archival; a published, versioned pure-function aggregator (no network, no RNG); a stated drift_tolerance per config; and vendor cooperation to pin model_version so a 'same config' re-inference is meaningful.
  - **Comparator-completeness scoring rule** — Whenever a contribution asserts a delta_magnitude above incremental.. 1. Resolver computes strongest_comparators = top-m (default 5) published_before neighborhood nodes by similarity. 2. Join each against NOVELANCHOR.addressed_comparators: a comparator is 'addressed' iff it is cited AND linked by a typed relation edge (baseline/bounds/extends/refutes). 3. comparator_completeness = addressed_fraction. 4. DECISION RULE (written, not ambiguous): if the single highest-similarity strongest comparator is NOT addressed → comparator_completeness_cap = incremental_cap: the aggregated magnitude for that contribution is hard-capped at incremental regardless of judge scores, and the judge brief is annotated with the omitted comparator. 5. Raw author_citation_overlap_with_neighborhood is retained only as a SOFT diagnostic surfaced to judges (very low overlap → 'weight REFGRAPH over author list'; very high overlap + zero addressed delta on strongest comparators → 'incremental'), never a direct score term.
    - reliability/reproducibility: Deterministic given the resolver snapshot: the cap is a pure function of REFGRAPH + NOVELANCHOR edges. Defeats the 'cite the whole neighborhood but bury the strongest comparator in a 200-item list' game because a citation without a typed, addressed relation edge does not count.
    - constraints: Ecosystem must provide a resolver with a frozen, dated corpus and a stable embedding model; the relation-edge taxonomy must be shared with the related_work layer so 'addressed' is machine-checkable.
  - **Provenance-ceiling weighting** — For every delta the ensemble might credit as novelty uplift.. 1. Read delta_provenance. 2. Set provenance ceiling: reviewer_confirmed → 1.0; author_asserted → 0.6, RAISABLE to 1.0 iff REFGRAPH finds no closer predecessor (independent corroboration); ai_suggested → 0.3 AND zero novelty uplift unless REFGRAPH independently corroborates the delta (no closer predecessor). 3. The ceiling multiplies the maximum novelty contribution that delta can add; an unconfirmed, uncorroborated ai_suggested delta contributes 0. 4. Record provenance_ceiling_applied in the report.
    - reliability/reproducibility: Turns provenance from bookkeeping into a binding weight. An unvetted AI guess cannot inflate novelty. Deterministic given provenance tags + REFGRAPH corroboration flag.
    - constraints: Requires the reviewer-confirmation channel (Seal/review layer) to write reviewer_confirmed provenance, and the resolver's 'no closer predecessor' test to be reproducible.
  - **Three-term calibrated confidence interval** — Every reported score.. 1. var_ensemble = variance of per-judge calibrated scores. 2. var_calibration = residual_sd^2 from the discipline's calibration fit. 3. var_human_panel = sigma_expert^2 * (1 - inter_expert_icc) using the discipline's published expert panel — the irreducible human-disagreement floor. 4. halfwidth = z * sqrt(var_ensemble + var_calibration + var_human_panel). 5. Publish expert_n and inter_expert_icc in the report so the floor is inspectable.
    - reliability/reproducibility: CLASS C honesty: if a field's experts only agree at ICC~0.5, var_human_panel is large and the CI widens — the interval cannot be dishonestly narrow. Reproducible given the calibration_registry values.
    - constraints: Registry must maintain and publish per-discipline expert_n and inter_expert_icc, refreshed each calibration_epoch; minimum expert_n gate below which a discipline reports 'CI unreliable — panel too small.'
  - **Cross-discipline within-strata normalization** — Any ranking or comparison across fields.. 1. Look up the reference_cohort for the paper's discipline_taxonomy.code and calibration_epoch. 2. z = (calibrated_score - cohort.mean_raw_score)/cohort.sd_raw_score. 3. percentile = cohort CDF at the score. 4. Report discipline_normalized.{z,percentile,cohort_id}. 5. Funders compare ONLY percentiles across fields; raw calibrated scores are labeled non-comparable across disciplines.
    - reliability/reproducibility: Reproducible: pure function of the dated cohort stats. Makes oncology-78 and pure-math-78 comparable only as within-field percentiles, matching the explicit z/percentile approach the critique demanded.
    - constraints: Requires maintained, dated reference cohorts per discipline with adequate n_papers; sparse disciplines report percentile with a wide CI and an under-powered flag.
  - **Adversarial rubric rotation + held-out probes** — Each calibration_epoch and on any suspected gaming.. 1. Rubric ships public_axes (disclosed) + a held_out_probe_set (secret targeted checks, e.g. 'is the claimed delta contradicted by any strongest comparator?'), hash-committed before the epoch. 2. Judges receive public axes always; held-out probes are injected without pre-disclosure. 3. Probes rotate every epoch; after an epoch closes, its probes are published for audit and retired. 4. Red_team judge runs the for/against argument specifically against the held-out probes.
    - reliability/reproducibility: Prevents a fully stationary white-box target: an author cannot prose-optimize against unknown, rotating probes. The commit-then-disclose cycle keeps it auditable — a funder can later verify which probes ran.
    - constraints: A trusted registry must hold the secret probe set and enforce commit-before-use; probe authorship must itself rotate to avoid capture.

  _Metrics afforded:_
  - authoritative novelty/significance score (0-100) → Pure-function aggregation over archived judge transcripts (score_transcript_bundle_hash), after comparator-completeness cap and provenance ceiling. [semantic-judged (score) wrapped in deterministic replay (authoritative value)]; anti-Goodhart: Verbosity capped by input_cap; unvetted AI deltas zeroed by provenance ceiling; buried-comparator gaming defeated by the completeness cap; for/against args must resolve to real anchor ids or are discounted.
  - reproduction_hash_match → Replay archived transcripts through published aggregator; compare hash + score. [deterministic]; anti-Goodhart: Nothing to game — either the archived bundle reproduces the number or the report is falsified; re-inference explicitly excluded so vendor drift cannot masquerade as a score change.
  - drift_delta → Re-inference on same input_bundle_hash vs archive: token_divergence + score_delta against published drift_tolerance. [reproducible]; anti-Goodhart: Cannot be inflated by an author; large drift flags config instability and forces recalibration rather than accepting a favorable rerun (no cherry-picking — runs are append-only).
  - comparator_completeness → Fraction of top-m strongest REFGRAPH predecessors that are cited AND addressed by a typed relation edge. [reliable-anchored]; anti-Goodhart: A citation without an addressed typed edge does not count, so mass-citing the neighborhood earns nothing; the strongest-comparator cap makes omitting the single closest work maximally costly.
  - discipline_normalized_percentile → z and CDF of calibrated_score against the dated within-discipline reference cohort. [reproducible]; anti-Goodhart: Field-relative, so inflating a raw score only moves you within your own cohort; mislabeling discipline_taxonomy to seek an easier cohort is detectable via REFGRAPH neighborhood concept drift.
  - calibration_mae_by_discipline → Ensemble vs rotating partially-hidden expert panel, per discipline, at epoch release. [reproducible]; anti-Goodhart: Hidden fraction of the expert set prevents overfitting the calibration; published MAE lets funders discount low-reliability fields.
  - confidence_interval halfwidth → sqrt(var_ensemble + var_calibration + var_human_panel) with published expert_n and ICC. [reproducible]; anti-Goodhart: Human-panel term makes the CI widen honestly where experts disagree; you cannot narrow it by tuning prose because the floor is set by external inter-rater ICC.

  _Tradeoffs:_ Honest costs and residual fabrication surfaces: (1) The transcript-replay definition means the 'score' is only as trustworthy as the archive integrity and the one-time inference — a compromised or lost archive is unrecoverable; mitigated by immutable, hash-addressed storage and append-only reports. (2) Comparator-completeness leans on the resolver's embedding model — an author could adversarially phrase the contribution to reduce similarity to the true strongest comparator (embedding evasion); mitigated by multi-query retrieval, concept-based expansion, and red_team judges instructed to search for omitted prior art, but not fully closed. (3) The provenance channel can be gamed by relabeling ai_suggested→author_asserted to raise the ceiling from 0.3 to 0.6; mitigated because author_asserted only reaches full weight via independent REFGRAPH corroboration, so the label alone buys little, and provenance can be spot-audited against the compiler's extraction log. (4) Held-out probes require a trusted registry that could itself be captured; mitigated by commit-then-disclose and rotating probe authorship, but this is a governance dependency, not a pure-format guarantee. (5) Reference cohorts and expert panels are expensive to maintain per discipline and per epoch; sparse fields get under-powered flags and wide CIs rather than false precision. (6) Multi-vendor ≥3 ensembles are costly and vendors deprecate model_versions, breaking future re-inference; the design tolerates this because re-inference is only a drift audit, not the authoritative path.

  _Open questions:_ 1. What drift_tolerance is defensible? Empirically, how much does temp-0 hosted inference actually move a novelty score run-to-run, and does that vary by vendor enough to make some models unusable as judges? 2. Embedding-evasion is a genuine open adversarial surface — is there a retrieval method robust to authors who deliberately phrase away from their closest comparator? 3. How large must an expert panel be, and how is ICC honestly estimated, when true domain experts for a niche subfield number in single digits? 4. Cross-epoch comparability: when calibration curves and cohorts refresh each quarter, is a 2026.Q2 percentile comparable to a 2027.Q1 percentile, or do we need explicit cross-epoch bridging studies? 5. Does publishing retired probes each epoch leak enough structure that a sophisticated author can infer the probe-generation process and pre-empt future rotations? 6. Who governs the registry (probes, cohorts, panels) so that the anti-gaming machinery is not itself captured by the institutions being scored?

  _Changes from critique:_ Addressed all six critique points directly. (1) Reproducibility redefined: the authoritative score is score_transcript_bundle_hash over archived transcripts; re-inference is a drift_audit with a published drift_tolerance, and the schema states hosted temp-0 inference is non-deterministic (batching/MoE/non-associative float). No field claims re-inference reproduces tokens. (2) Overlap ambiguity replaced by a written decision rule plus a load-bearing comparator_completeness test: the resolver ranks the top-m strongest predecessors; each must be cited AND addressed by a typed relation edge; if the single strongest is unaddressed, delta_magnitude is capped at incremental regardless of judge output. Raw overlap is demoted to a soft diagnostic. This defeats cite-everything-but-bury-the-comparator. (3) Rubric is no longer fully white-box: it splits into published public_axes and a rotating, per-epoch held_out_probe_set (hash-committed, disclosed only after epoch close), plus adversarial rubric rotation. (4) CI now has three variance terms — ensemble disagreement, calibration residual, and human-panel noise derived from per-discipline expert ICC and panel size N — all published; a low-ICC field yields an honestly wider CI. (5) provenance now drives a provenance_ceiling: reviewer_confirmed=1.0, author_asserted=0.6 (raisable to 1.0 only if REFGRAPH finds no closer predecessor), ai_suggested=0.3 with zero novelty uplift unless independently corroborated by REFGRAPH. (6) Cross-discipline comparability implemented as within-strata z-score + percentile against a dated reference cohort keyed by discipline_taxonomy.code, reported alongside the raw score so oncology-78 and pure-math-78 are only ever compared as percentiles.

  _Adopted from competitor:_ Four things from LENS-ARA (Sonnet 5): (1) the per-contribution surprise_indicator triple {stated_prior_expectation → observed_outcome → surprise_class} anchored to O##/C## ids, which is a sharper novelty signal than a flat contribution_type; (2) multiple contribution loci (one NOVELANCHOR record per contribution, NA##) instead of one paper-level claim; (3) explicit red_team/adversarial judge roles as a first-class field in the ensemble, not just prompt flavor; (4) the typed relation taxonomy (imports/bounds/baseline/extends/refutes) mirrored from related_work.md — I reuse it as the machinery that decides whether a strongest comparator is "addressed." I also adopt its calibration_epoch handle so a run is tied to a named calibration curve.

  _Why it wins:_ LENS-ARA repeats the exact fatal sentence the reviewer flagged — "re-running the identical bundle reproduces the identical score / same individual judge outputs." That is false for hosted models and a funder who re-runs will get a different number, collapsing the claim. My design pins authoritative = transcript-hash and demotes re-inference to a tolerance-bounded drift audit. LENS-ARA also has the same open holes the critique names: its neighborhood-search block flags an "omitted_but_discoverable" comparator but never converts that flag into a score effect (I do, via the completeness cap); it records provenance but never discounts an unvetted AI delta (I impose a provenance ceiling with a zero-uplift floor); its CI is not specified to include human-panel ICC (mine decomposes three variance terms and publishes per-discipline expert N + ICC); and it has no cross-discipline normalization at all, whereas I ship within-strata z/percentile against dated cohorts. Its rubric is public with no held-out component; I rotate a hidden probe set. A genuine merge is not strictly better because LENS-ARA's core reproducibility premise is the thing being refuted — I keep its good schema ideas and replace its broken protocol spine.


### Finalist B (refined)

> _Judge critique it answered:_ LENS-ARA (#2) earns the second slot on the strength of its anti-gaming spine: an independent k-NN neighborhood over a publication-time-frozen corpus (defeats citation curation AND future-citation leakage), hard redaction + a min-5 / ≥2-vendor / ≥1-red_team ensemble, and content-hashed append-only runs so cherry-picked reruns are visible rather than silently overwritten. That is the most disciplined reproducibility/auditability architecture of the four. But the gaps are real:

1) Calibration — the Class-C crux — is your visible weakness. You tie runs to a calibration_epoch but never show HOW agreement with human experts is measured or maintained: no MAE/ICC vs experts, no held-out set size per discipline, no drift-audit cadence, no recalibration trigger. #0 and #3 beat you decisively here. A subjective score is only 'defensible to a funder' if you can state the calibration curve fit and its measured error; right now that is asserted, not specified.

2) Append-only makes reruns visible but does not make them non-gameable — you never name the AUTHORITATIVE run. An author runs five times and cites the best; visibility alone does nothing unless the protocol pre-registers N and mandates a canonical aggregate (first run? pre-registered median?). Without a canonical-run rule, transparency is toothless.

3) Your independent neighborhood is only as uncurateable as its query — and the query is built from NOVELANCHOR.claimed_sota_position + concepts.md, both author-authored. An author phrases the anchor to steer k-NN away from the closest competitor. Build at least one query from title/abstract embeddings independent of author framing, run multiple queries, and flag neighborhood disagreement; otherwise you have reintroduced the curation you claimed to eliminate.

4) Redaction of authors/venue/DOI is not blinding. 'Our prior work [ref],' named datasets, and stylistic tells leak identity through the brief prose itself. Specify de-identification of the brief text, not just metadata fields.

5) Reproducibility: same LLM non-determinism caveat as #3 — 're-running the identical bundle reproduces the identical score' holds only via transcript replay, not re-inference. Make that explicit or the promise overstates.

6) Cross-discipline comparability is barely present in the visible design — no per-field standardization scheme for the 0-100. A funder ranking a chem paper against an ML paper on one axis needs a stated normalization.

**LENS-ARA/CAL: The Calibrated, Canonical Novelty Ledger**  ·  _source: Claude Opus 4.8_

LENS-ARA/CAL keeps the anti-gaming spine that earned the second slot — a publication-time-frozen independent k-NN neighborhood, a min-5 / ≥2-vendor / ≥1-red_team blinded ensemble with anchor-grounded for/against, and content-hashed append-only runs — and closes the four gaps that lost it the top slot. First, calibration becomes a first-class artifact: CALIBRATION.yaml pins a per-discipline held-out human-expert set, states the exact monotonic (isotonic) curve that maps raw ensemble scores to calibrated 0-100, publishes the measured cross-validated MAE/ICC/residual-RMSE per discipline, and names the drift-audit cadence and the numeric recalibration trigger. Second, transparency gets teeth: authors pre-register N runs in a RUN_REGISTRY before seeing any score, and the AUTHORITATIVE number is the sealed pre-registered median — cherry-picking is not just visible, it is inadmissible. Third, the neighborhood is queried from three independent sources (author-independent title/abstract embedding, the author's claimed_sota_position, and concepts), and steering is caught by a measured neighborhood-divergence flag. Fourth, blinding de-identifies the brief PROSE (not just metadata) and a leakage detector gates the run; reproducibility is stated honestly as byte-exact transcript replay plus a measured re-inference stability band; and cross-discipline comparability is defined as expert-anchored within-discipline percentile landmarks so a chem 85 and an ML 85 mean the same thing.

- **NOVELANCHOR.yaml** (YAML sidecar novelty/NOVELANCHOR.yaml, one record per contribution locus, cross-referencing claim_ids (C##), gap_ids (G##), related_work ids (RW##) by id — never re-typing prose.) — Structured, source-anchored manifest of what the paper's own logic layer claims as its contribution(s) — type, locus, magnitude, surprise — plus the discipline code that selects the calibration curve. INPUT to the judge, never the score. Now carries per-field-group provenance so an AI-suggested claim is never mistaken for a vetted one, and every field has a first-class not_specified scored equal to a filled value.
  - fields: contribution_id: string (NA##) — required. | type: enum{new_method|new_finding|resolved_gap|new_theory|new_dataset|replication|synthesis|negative_result|not_specified} — required; not_specified scored equal. | locus: {claims:[C##], gaps:[G##], insight:ref} — required, ≥1 non-empty or not_specified. | delta_magnitude: enum{incremental|substantial|foundational|not_specified} — required. | delta_basis: {compared_against:[RW##/refs ids], quantity_ref: optional quantities.yaml link, rationale: prose} — required; rationale may be 'Not specified in paper'. | surprise_indicator: {stated_prior_expectation: prose citing O##, observed_outcome: prose citing C##, surprise_class: enum{none|mild|moderate|high|not_specified}} — required. | contribution_scope: list[enum{method|data|theory|application|synthesis}] — required, may be empty. | discipline_taxonomy: {scheme: enum{openalex_concept|mesh|arxiv_category}, code: string} or not_specified — required; selects the CALIBRATION curve. | provenance: {type: enum{author_asserted|ai_suggested|reviewer_confirmed}, delta_basis: same enum, surprise: same enum} — required per field group. | source_anchor: {file, locator} — required; every non-not_specified field must resolve to a real file:locator.
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
novelanchor_version: "2.0"
extracted_by: compiler-llm-v2.3
contributions:
  - contribution_id: NA01
    type: synthesis
    locus: {claims: [C01,C02,C05], gaps: [G1], insight: KEY_INSIGHT}
    delta_magnitude: incremental
    delta_basis:
      compared_against: [RW01, RW04, RW09]
      quantity_ref: null
      rationale: "First NMA to place all major p-tau217/181/231 platform-isoform combinations in one connected network; RW01,RW04 compared pairs only."
    surprise_indicator:
      stated_prior_expectation: "O2: field assumed p-tau181 and p-tau217 roughly comparable"
      observed_outcome: "C01: p217_MS P-score 0.859 vs p181_IA 0.117 — larger gap than any pairwise study reported"
      surprise_class: moderate
    contribution_scope: [method, synthesis]
    discipline_taxonomy: {scheme: openalex_concept, code: C2779134260}
    provenance: {type: ai_suggested, delta_basis: author_asserted, surprise: ai_suggested}
    source_anchor: {file: logic/related_work.md, locator: "Key Insight; RW01,RW04 Delta fields"}
  - contribution_id: NA02
    type: not_specified
    locus: {claims: [C07]}
    delta_magnitude: not_specified
    delta_basis: {compared_against: [], rationale: "Not specified in paper"}
    surprise_indicator: {surprise_class: not_specified}
    contribution_scope: []
    discipline_taxonomy: not_specified
    provenance: {type: author_asserted}
    source_anchor: {file: null, locator: null}
- **REFGRAPH.yaml** (YAML novelty/REFGRAPH.yaml; nodes keyed by RW## plus synthetic ids for uncited-but-discovered neighbors; edges typed per related_work taxonomy.) — Publication-time-frozen SOTA neighborhood. Every cited work resolved to a stable external id, PLUS THREE independent k-NN searches over a frozen corpus snapshot. The primary query q_auto is built from title/abstract embeddings with NO author framing, so the neighborhood is uncurateable even if the author phrases the anchor to dodge the closest competitor. Neighborhood_divergence across the three queries is a measured steering detector.
  - fields: corpus_snapshot_id: string — required; dated at/before publication_date (no future signals). | embedding_model: string (versioned) — required. | nodes[]: {ref_id, external_id (doi/arxiv/openalex/s2 or not_resolved), resolved: bool, title, pub_date, embedding_hash, reason?} — required per cited work; unresolved kept (not dropped) with reason. | relations[]: {from, to, type: enum{imports|bounds|baseline|extends|refutes}, source: file} — required. | queries[]: {query_id: enum{q_auto|q_anchor|q_concepts}, source: prose, author_dependent: bool, method, k, top_neighbors:[{external_id, similarity, cited_by_paper: bool, pub_before: bool, note}]} — required; q_auto (author_dependent:false) is primary and built from title+abstract embedding only. | neighborhood_divergence: {jaccard_auto_vs_anchor: float, neighbors_found_by_auto_missing_from_anchor: int, top_missed:[external_id], steering_flag: bool} — required; steering_flag true when q_anchor/q_concepts systematically omit high-similarity neighbors q_auto surfaces. | coverage_stats: {citations_in_paper, resolved_to_external_id, resolution_rate, author_citation_overlap_with_neighborhood: float or not_computable, omitted_but_discoverable_flagged: int} — required. | insufficient_coverage_flag: bool — required; true when the subfield index is too sparse to support a neighborhood (honest null, never treated as 'confirmed novel').
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
refgraph_version: "2.0"
corpus_snapshot_id: openalex-2026-01-snapshot
embedding_model: s2-specter2-v2
nodes:
  - {ref_id: RW01, external_id: {doi: 10.1093/brain/awac333}, resolved: true, pub_date: 2023-04-12}
  - {ref_id: inline-2023-mattsson, external_id: not_resolved, resolved: false, reason: "author-year prose citation, no DOI"}
relations:
  - {from: this_paper, to: RW01, type: imports, source: related_work.md}
queries:
  - query_id: q_auto
    source: "title+abstract embedding (no author framing)"
    author_dependent: false
    method: knn_over_corpus_snapshot
    k: 50
    top_neighbors:
      - {external_id: 10.1001/jamaneurol.2024.xxxx, similarity: 0.83, cited_by_paper: false, pub_before: true, note: "contemporaneous overlapping NMA, NOT cited"}
  - query_id: q_anchor
    source: "NOVELANCHOR.claimed_sota_position"
    author_dependent: true
    method: knn_over_corpus_snapshot
    k: 50
    top_neighbors: [...]
neighborhood_divergence:
  jaccard_auto_vs_anchor: 0.52
  neighbors_found_by_auto_missing_from_anchor: 4
  top_missed: [10.1001/jamaneurol.2024.xxxx]
  steering_flag: true
coverage_stats: {citations_in_paper: 30, resolved_to_external_id: 24, resolution_rate: 0.80, author_citation_overlap_with_neighborhood: 0.34, omitted_but_discoverable_flagged: 1}
insufficient_coverage_flag: false
- **CALIBRATION.yaml** (YAML in a shared registry calibration/{epoch}/CALIBRATION.yaml, content-hashed, referenced by hash from every judge_manifest.) — THE fix for the Class-C crux. A versioned, shared (not per-ARA) artifact that turns a subjective ensemble score into a calibrated, funder-defensible 0-100 with a stated error. Names the per-discipline held-out expert set, the exact monotonic curve mapping raw→calibrated, the measured agreement (MAE, ICC, residual RMSE), the expert-anchored percentile landmarks that make disciplines comparable, and the drift cadence + numeric recalibration trigger. Every assessment run cites a calibration_epoch by hash; recalibration mints a NEW epoch and old runs are never silently rescored.
  - fields: calibration_epoch: string (e.g. 2026.Q2) — required. | rubric_version: string — required. | disciplines[]: {code (openalex/mesh/arxiv), n_held_out_aras: int (min 60), experts_per_ara: int (min 3), inter_expert_ICC: float, expert_consensus: enum{trimmed_mean|median}} — required per discipline. | curve: {family: enum{isotonic|monotone_spline}, fit_on: '(raw_ensemble_median, expert_consensus) pairs within discipline', knots: [...], residual_rmse: float} — required per discipline; the published mapping. | agreement: {cv_folds: int, mae_cv: float, spearman_rho: float, icc_2k_ensemble_vs_expert: float, n_eval: int} — required per discipline; the numbers a funder reads. | landmarks: {p50_calibrated: 50 = 'median accepted paper in discipline', p90_calibrated: 90 = 'top-decile significance', anchored_by: 'expert panel {epoch}'} — required; makes cross-discipline 0-100 comparable in meaning. | ci_method: {type: bootstrap, resamples: int, over: [judges, calibration_pairs], interval: 90} — required. | drift_audit: {cadence: quarterly, audit_sample_per_discipline: int, rolling_mae: float} — required. | recalibration_trigger: {condition: 'rolling_audit_mae > mae_cv + 5 OR icc_2k_ensemble_vs_expert < 0.70 OR scheduled quarter elapsed', action: 'mint new calibration_epoch; do not rescore prior runs'} — required. | insufficient_calibration_flag: bool per discipline — required; when held-out set < min, scores in that discipline are emitted with widened CI and a not_calibrated marker rather than a false precision.
  - example: calibration_epoch: 2026.Q2
rubric_version: lens-rubric-1.4
disciplines:
  - code: C2779134260   # clinical neurology / biomarkers
    n_held_out_aras: 72
    experts_per_ara: 3
    inter_expert_ICC: 0.74
    expert_consensus: trimmed_mean
    curve: {family: isotonic, fit_on: '(raw_ensemble_median, expert_consensus) within discipline', residual_rmse: 6.1}
    agreement: {cv_folds: 5, mae_cv: 7.3, spearman_rho: 0.81, icc_2k_ensemble_vs_expert: 0.78, n_eval: 72}
    landmarks: {p50_calibrated: 50, p90_calibrated: 90, anchored_by: 'expert panel 2026.Q2'}
    insufficient_calibration_flag: false
  - code: cs.LG        # ML
    n_held_out_aras: 140
    experts_per_ara: 3
    inter_expert_ICC: 0.69
    curve: {family: isotonic, residual_rmse: 8.4}
    agreement: {cv_folds: 5, mae_cv: 9.1, spearman_rho: 0.76, icc_2k_ensemble_vs_expert: 0.72, n_eval: 140}
    landmarks: {p50_calibrated: 50, p90_calibrated: 90, anchored_by: 'expert panel 2026.Q2'}
    insufficient_calibration_flag: false
ci_method: {type: bootstrap, resamples: 2000, over: [judges, calibration_pairs], interval: 90}
drift_audit: {cadence: quarterly, audit_sample_per_discipline: 20, rolling_mae: 7.6}
recalibration_trigger:
  condition: 'rolling_audit_mae > mae_cv + 5 OR icc_2k_ensemble_vs_expert < 0.70 OR scheduled quarter elapsed'
  action: 'mint new calibration_epoch; prior runs keep their epoch, never rescored'
- **RUN_REGISTRY.yaml** (YAML novelty/RUN_REGISTRY.yaml, append-only, pre-registration block sealed by hash+timestamp BEFORE first run.) — The fix for 'append-only is visible but not non-gameable'. Before any judge runs, the author pre-registers the run count N and the seed policy; the AUTHORITATIVE score is the sealed median of exactly those N runs. Cherry-picked extra reruns remain recorded (append-only) but are structurally INADMISSIBLE — the canonical pointer is fixed at pre-registration and cannot move. Transparency now has teeth.
  - fields: preregistration: {n_runs: int (odd, 3-7), seed_policy: enum{fixed_declared_seeds|derived_from_bundle_hash}, seeds: [int], sealed_at: timestamp, sealed_hash: sha256, calibration_epoch: string} — required; sealed before any score exists. | registered_runs[]: {assessment_run_id, run_index: 1..n, admissible: bool} — required; exactly n admissible runs. | canonical: {rule: 'median of admissible registered_runs', canonical_score: float, ci: [low,high], run_ids: [...], sealed: true} — required; the single number a funder cites. | extra_runs[]: {assessment_run_id, reason, admissible: false} — optional; visible but inadmissible, so re-running to fish for a better number is a no-op on the canonical score. | amendment_log[]: {change, justification, requires: 'new preregistration + new canonical'} — optional; any change to N or seeds voids the seal and mints a fresh pre-registration (auditable, never silent).
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
preregistration:
  n_runs: 5
  seed_policy: derived_from_bundle_hash
  seeds: [7, 13, 21, 34, 55]
  sealed_at: 2026-07-06T09:00:00Z
  sealed_hash: 3af9...
  calibration_epoch: 2026.Q2
registered_runs:
  - {assessment_run_id: r-20260706-0901-a1, run_index: 1, admissible: true}
  - {assessment_run_id: r-20260706-0902-b2, run_index: 2, admissible: true}
  - {assessment_run_id: r-20260706-0903-c3, run_index: 3, admissible: true}
  - {assessment_run_id: r-20260706-0904-d4, run_index: 4, admissible: true}
  - {assessment_run_id: r-20260706-0905-e5, run_index: 5, admissible: true}
canonical:
  rule: 'median of admissible registered_runs'
  canonical_score: 61
  ci: [52, 69]
  run_ids: [r-...a1, r-...b2, r-...c3, r-...d4, r-...e5]
  sealed: true
extra_runs:
  - {assessment_run_id: r-20260707-1400-z9, reason: 'author re-ran hoping for higher', admissible: false}
- **judge_manifest.yaml + blinded_brief.yaml** (YAML novelty/runs/{run_id}/judge_manifest.yaml (append-only) + the blinded_brief.yaml it hashes; references NOVELANCHOR, REFGRAPH, CALIBRATION by hash.) — Replayable config of ONE assessment run: models, pinned versions, temperatures, seeds, prompts, primary/red_team roles, and the hash of the blinded bundle every judge saw — now with PROSE de-identification (not just metadata redaction) plus a leakage detector that must pass before judges run, and an honest two-tier reproducibility record (byte-exact replay + measured re-inference band).
  - fields: assessment_run_id: string (timestamp+hash) — required. | rubric_version, calibration_epoch: string — required (calibration_epoch must match RUN_REGISTRY seal). | input_bundle_hash: sha256 — required; hash of the de-identified brief. | deidentification: {metadata_removed: [author,venue,affiliation,doi,self_citation_flags], prose_neutralized: [{pattern: 'our/we prior work [ref]', to: '[prior work RWxx]'}, {pattern: named_dataset_tells, to: neutral_token}, {style_normalization: bool}], leakage_detector: {version, verdict: enum{pass|fail}, residual_identity_risk: float}} — required; run BLOCKED if verdict=fail. | input_cap: {max_tokens_brief: int} — required; bounds prose so verbosity cannot buy score. | injection_detector_version: string — required. | judges[]: {judge_id, model, vendor, role: enum{primary|red_team}, temperature, seed, prompt_hash, response_hash} — required; min 5 judges, ≥2 vendors, ≥1 red_team. | reproducibility: {tier1_transcript_replay: 'byte-exact from archived transcripts', tier2_reinference: {resamples: int, max_reinference_delta: float, note: 're-inference reproduces score within band, NOT identically'}} — required; states the honest limit. | archive_uri: string — required; immutable raw-transcript store.
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
assessment_run_id: r-20260706-0901-a1
rubric_version: lens-rubric-1.4
calibration_epoch: 2026.Q2
input_bundle_hash: 9c1e...
deidentification:
  metadata_removed: [author, venue, affiliation, doi, self_citation_flags]
  prose_neutralized:
    - {pattern: 'our prior work [RW04]', to: '[prior work RW04]'}
    - {pattern: 'the ADNI-3 cohort we assembled', to: '[named cohort]'}
    - {style_normalization: true}
  leakage_detector: {version: leak-det-1.2, verdict: pass, residual_identity_risk: 0.06}
input_cap: {max_tokens_brief: 3000}
injection_detector_version: inj-2.1
judges:
  - {judge_id: J1, model: claude-opus-4.6, vendor: anthropic, role: primary,  temperature: 0, seed: 7, prompt_hash: a1b2, response_hash: f0..}
  - {judge_id: J2, model: gpt-5.2,        vendor: openai,    role: primary,  temperature: 0, seed: 7, prompt_hash: a1b2, response_hash: c3..}
  - {judge_id: J3, model: gemini-2.5-pro, vendor: google,    role: primary,  temperature: 0, seed: 7, prompt_hash: a1b2, response_hash: d4..}
  - {judge_id: J4, model: claude-opus-4.6,vendor: anthropic, role: primary,  temperature: 0, seed: 13, prompt_hash: d4e5, response_hash: e5..}
  - {judge_id: J5, model: gpt-5.2,        vendor: openai,    role: red_team, temperature: 0, seed: 13, prompt_hash: r3d7, response_hash: a6..}
reproducibility:
  tier1_transcript_replay: byte-exact
  tier2_reinference: {resamples: 20, max_reinference_delta: 3.4, note: 're-inference within band, not identical'}
archive_uri: s3://lens-archive/che26/r-20260706-0901-a1/
- **novelty_report.yaml** (YAML novelty/novelty_report.yaml, one per ARA, points at RUN_REGISTRY.canonical + CALIBRATION by hash.) — The funder-facing OUTPUT: the calibrated, cross-discipline-comparable 0-100 with its CI, the for/against ledger grounded in anchor ids, every diagnostic flag (steering, coverage, undisclosed prior art), and the full provenance chain (which calibration_epoch, which canonical runs, which bundle hash) so the number is defensible line-by-line. Honest low novelty is scored equal in structural completeness to a foundational discovery — only the semantic score differs.
  - fields: ara_id, discipline_code — required. | calibration_epoch, calibration_hash — required. | canonical_run_ref: {registry_hash, canonical_score_raw: float, calibrated_score: 0-100, ci_90: [low,high]} — required. | axes: {novelty, significance, surprisingness}: each {calibrated: 0-100, ci_90:[.,.], raw_ensemble_median: float, judge_spread: float} — required. | for_against[]: {axis, side: enum{for|against}, argument: prose, anchors: [C##/RW##/REFGRAPH node], grounded: bool} — required; ungrounded arguments structurally discounted (do not move the score). | diagnostics: {neighborhood_steering_flag: bool, undisclosed_prior_art_count: int, author_citation_overlap: float, insufficient_coverage_flag: bool, insufficient_calibration_flag: bool} — required; each flag widens CI or annotates rather than silently inflating the score. | comparability: {landmark_note: 'calibrated 90 = top-decile significance in discipline C2779134260 per 2026.Q2 expert anchor'} — required. | honest_absence_note: prose — required when NOVELANCHOR fields were not_specified, affirming no structural penalty applied.
  - example: ara_id: che26-diagnostic-performance-of-plasma-p-tau217
discipline_code: C2779134260
calibration_epoch: 2026.Q2
calibration_hash: 7b2c...
canonical_run_ref: {registry_hash: 3af9..., canonical_score_raw: 58.0, calibrated_score: 61, ci_90: [52, 69]}
axes:
  novelty:        {calibrated: 61, ci_90: [52,69], raw_ensemble_median: 58.0, judge_spread: 11.2}
  significance:   {calibrated: 74, ci_90: [66,81], raw_ensemble_median: 71.0, judge_spread: 8.0}
  surprisingness: {calibrated: 55, ci_90: [44,66], raw_ensemble_median: 52.0, judge_spread: 13.5}
for_against:
  - {axis: novelty, side: for, argument: 'First connected cross-platform NMA', anchors: [G1, RW01, RW04], grounded: true}
  - {axis: novelty, side: against, argument: 'A contemporaneous overlapping NMA exists but was not cited', anchors: ['10.1001/jamaneurol.2024.xxxx'], grounded: true}
diagnostics: {neighborhood_steering_flag: true, undisclosed_prior_art_count: 1, author_citation_overlap: 0.34, insufficient_coverage_flag: false, insufficient_calibration_flag: false}
comparability: {landmark_note: 'calibrated 90 = top-decile significance in discipline C2779134260 per 2026.Q2 expert anchor'}
honest_absence_note: 'NA02 declared not_specified for delta_magnitude and surprise; scored as honest absence, no structural penalty.'

  _Protocols:_
  - **P1 — Multi-query neighborhood resolution (anti-steering)** — Once per ARA, before any judge run, to build the uncurateable SOTA neighborhood.. 1) Freeze corpus_snapshot at/before publication_date. 2) Build q_auto from title+abstract embeddings ONLY (author framing excluded) — this is primary. 3) Build q_anchor from NOVELANCHOR.claimed_sota_position and q_concepts from concepts.md — secondary. 4) Run all three k-NN searches; union the neighbors. 5) Compute neighborhood_divergence: jaccard(q_auto, q_anchor), and list high-similarity neighbors q_auto found that q_anchor/q_concepts missed. 6) Set steering_flag when q_auto surfaces ≥1 high-similarity (>0.75) uncited neighbor absent from the author-framed queries. 7) Emit undisclosed_prior_art_count and author_citation_overlap.
    - reliability/reproducibility: Deterministic given (snapshot, embedding_model, queries); all pinned by version+hash. q_auto is author-independent by construction, so steering the anchor cannot hide the closest competitor — it only produces a divergence flag. Re-running with the same pinned snapshot reproduces the neighborhood exactly.
    - constraints: Ecosystem must provide: a dated, immutable corpus snapshot service (OpenAlex/S2 with pub-time filtering); a versioned embedding model; resolver for DOI/arXiv/OpenAlex ids. Unresolved citations are kept with a reason, never dropped.
  - **P2 — Brief de-identification + leakage gate** — Once per run, after building the brief, before judges see anything.. 1) Strip metadata (author/venue/affiliation/DOI/self-citation flags). 2) Neutralize prose identity tells: 'our/we prior work [ref]' → '[prior work RWxx]', first-person self-reference removed, named proprietary datasets/cohorts → neutral tokens, light style normalization. 3) Run leakage_detector: an LLM+heuristic pass that attempts to re-identify authors/group from the neutralized brief and returns residual_identity_risk. 4) If verdict=fail (risk > threshold), BLOCK the run and re-neutralize. 5) Hash the passing brief into input_bundle_hash.
    - reliability/reproducibility: The de-identification transform and detector are versioned; the same brief in produces the same neutralized brief out (byte-exact), so the gate is auditable. Detector threshold is published, not judge-tunable.
    - constraints: Ecosystem must provide a maintained leakage_detector with a published false-negative rate on a red-team set of known-identity briefs. Blinding is imperfect for tiny subfields — residual_identity_risk is reported honestly rather than claimed zero.
  - **P3 — Blinded ensemble assessment with anchored for/against** — N times per ARA (N from RUN_REGISTRY), each a full manifest.. 1) Compose judge set: min 5, ≥2 vendors, ≥1 red_team (red_team is prompted to argue AGAINST novelty and hunt undisclosed prior art). 2) Each judge independently scores novelty/significance/surprisingness on the published rubric and MUST attach for AND against arguments, each resolving to a claim/ref/REFGRAPH id. 3) Discount any argument with grounded:false — it cannot move the score. 4) Cap brief tokens (input_cap) so length cannot buy score. 5) Archive full raw transcripts; record response_hash per judge.
    - reliability/reproducibility: Temperature 0 + declared seed + pinned model version + prompt_hash. Tier-1: transcripts replay byte-exact for audit. Tier-2: re-inference reproduces the score within a measured max_reinference_delta band (reported), never claimed identical — this is the honest reproducibility statement.
    - constraints: Ecosystem must provide pinned, archivable model endpoints (or the design degrades to transcript-replay-only where vendors deprecate a version). Red_team seat is mandatory to counter for-side optimism.
  - **P4 — Canonical aggregation (pre-registration + sealed median)** — Once per ARA, immediately after N pre-registered runs complete.. 1) Author pre-registers N (odd, 3-7) and seed policy in RUN_REGISTRY; block sealed by hash+timestamp BEFORE any score is revealed. 2) Execute exactly N runs. 3) Canonical raw score = median across the N admissible runs (per axis). 4) Map raw→calibrated via CALIBRATION curve for the discipline. 5) CI = 90% bootstrap over judges AND calibration pairs, combining ensemble-disagreement variance with calibration-residual variance. 6) Seal canonical. Any later run is recorded as extra_runs{admissible:false} and cannot change the canonical number. Changing N/seeds voids the seal and mints a fresh, logged pre-registration.
    - reliability/reproducibility: The authoritative number is fixed by pre-registration, so run-five-cite-the-best is inadmissible, not merely visible. Median of pre-registered N is reproducible from archived transcripts (tier-1) and stable within the reported re-inference band (tier-2).
    - constraints: Ecosystem must provide a tamper-evident pre-registration timestamp service (e.g., append-only log / transparency ledger) so 'sealed before scores' is verifiable, not trust-based.
  - **P5 — Calibration build, agreement measurement, and drift maintenance (Class-C core)** — Per calibration_epoch (built at epoch start, audited quarterly, recalibrated on trigger).. 1) Per discipline, assemble a held-out expert set (min 60 ARAs; ≥3 experts each) scored on the same public rubric; expert_consensus = trimmed mean; report inter_expert_ICC. 2) Fit a monotonic isotonic (or monotone-spline) curve mapping raw_ensemble_median → expert_consensus within discipline; report residual_rmse. 3) Measure agreement by k-fold CV: publish mae_cv, spearman_rho, icc_2k_ensemble_vs_expert per discipline. 4) Define expert-anchored percentile landmarks (calibrated 50/90). 5) Quarterly, score a fresh audit sample; compute rolling_audit_mae. 6) Recalibration trigger fires when rolling_audit_mae > mae_cv+5 OR icc<0.70 OR the quarter elapses → mint a NEW calibration_epoch. Prior runs keep their epoch and are NEVER silently rescored.
    - reliability/reproducibility: The whole calibration is a published, hashed artifact — a funder can read the curve, the held-out n, and the error. Reproducibility is at the epoch level: every score cites its epoch, so run-to-run comparability is exact within an epoch and explicitly versioned across epochs. This is the fix the reviewer demanded: measured MAE/ICC, held-out sizes, cadence, and a numeric trigger, not assertion.
    - constraints: Ecosystem must fund and maintain a rotating expert panel per discipline and a partially-hidden held-out set (rotated so it cannot be memorized/gamed). Where a discipline can't reach min n, insufficient_calibration_flag is set and scores ship with widened CI + not_calibrated marker rather than false precision.
  - **P6 — Cross-discipline normalization** — Whenever a calibrated score is emitted for funder comparison across fields.. 1) Each discipline has its own raw→calibrated curve (P5). 2) The calibrated 0-100 axis is anchored to shared expert-defined percentile landmarks: 50 = median accepted paper in that discipline, 90 = top-decile significance. 3) A chem 85 and an ML 85 therefore both mean 'top-15% within own field per expert anchor', making the number comparable in MEANING even though the underlying raw distributions differ. 4) The landmark_note travels with every score so a funder reads the interpretation, not a bare integer.
    - reliability/reproducibility: Normalization is a stated, published transform (percentile-anchored landmarks per epoch), reproducible and auditable. It does not claim raw-score comparability — it claims percentile-of-significance comparability, which is what a cross-field funder actually needs.
    - constraints: Ecosystem must maintain per-discipline reference distributions and expert-anchored landmarks per epoch. Interdisciplinary papers get scored under each relevant discipline code and reported as a small set, not forced into one bucket.

  _Metrics afforded:_
  - Calibrated novelty / significance / surprisingness score (0-100 per axis) → Median raw ensemble score across N pre-registered runs → mapped through the discipline's isotonic CALIBRATION curve → reported with 90% bootstrap CI combining ensemble disagreement and calibration residual. [semantic-judged (calibrated + reproducible within epoch)]; anti-Goodhart: Score is bounded by anchor-grounded for/against (ungrounded arguments cannot move it), token-capped briefs (length cannot buy score), a red_team seat arguing against, and an independent uncurateable neighborhood. Padding/boilerplate/fabricated-but-consistent prose does not raise it because the number is a calibrated function of grounded evidence, not of text volume.
  - Ensemble-vs-expert agreement (mae_cv, icc_2k, spearman_rho) per discipline → k-fold cross-validation of the calibration curve against the held-out expert set; published in CALIBRATION.yaml per epoch. [reproducible (measured, versioned)]; anti-Goodhart: The held-out expert set is rotated and partially hidden per epoch, so a judge model cannot be tuned to the eval. Reporting MAE/ICC honestly (including when they are poor) is what makes the score defensible; a bad number is published, not hidden.
  - Neighborhood steering flag + undisclosed prior-art count → Compare author-independent q_auto neighbors against author-framed q_anchor/q_concepts; count high-similarity uncited neighbors q_auto surfaces that the author queries miss. [reliable-anchored]; anti-Goodhart: Directly targets the exploit of phrasing the anchor to dodge the closest competitor: q_auto is built with zero author framing, so steering the anchor produces a flag rather than a cleaner-looking neighborhood. Author cannot suppress q_auto.
  - Re-inference stability band (max_reinference_delta) → Re-run the identical pinned bundle R times; report the max deviation of the calibrated score. [reproducible (band, not point)]; anti-Goodhart: Prevents overstating reproducibility. A tight band is earned by the ensemble+aggregation design, not asserted; a wide band is disclosed and widens the reported CI, so an unstable score cannot masquerade as precise.
  - Canonical-run integrity (pre-registered N, sealed median) → RUN_REGISTRY pre-registration hash+timestamp vs. the set of admissible runs feeding the canonical median. [deterministic (integrity check)]; anti-Goodhart: Defeats run-five-cite-the-best: the canonical pointer is sealed before scores exist and cannot move; extra runs are recorded but inadmissible. Changing N voids the seal visibly. Transparency becomes binding, not decorative.
  - Author-citation-overlap-with-neighborhood diagnostic → Fraction of the independent neighborhood that the author actually cited (from REFGRAPH.coverage_stats). [reproducible]; anti-Goodhart: Two-sided by construction: very low overlap flags a self-serving citation list; very high overlap with zero delta flags an incremental paper. Neither extreme is rewarded, so there is no single direction to game toward.

  _Tradeoffs:_ Costs and risks, stated honestly. (1) Calibration is expensive: a rotating expert panel of ≥3 experts scoring ≥60 ARAs per discipline per epoch is real money and real recruiting; where it can't be met, insufficient_calibration_flag ships a widened-CI, not_calibrated score rather than a false-precision number — a deliberate honesty-over-coverage choice. (2) Blinding is imperfect: for tiny subfields, prose de-identification cannot fully hide identity; we report residual_identity_risk rather than claim zero, and block only above threshold — some leakage risk remains and is disclosed. (3) Fabrication surface — NOVELANCHOR is author-authored and could overclaim delta_magnitude/surprise; mitigated because the score is driven by the independent neighborhood + grounded for/against + red_team, not by the anchor's adjectives, and provenance tags mark AI-suggested vs vetted fields. (4) Model deprecation threatens tier-2 re-inference: when a vendor retires a pinned version, the design degrades gracefully to tier-1 transcript-replay-only, which we state rather than pretend re-inference is eternal. (5) Pre-registration friction: authors must commit N before seeing scores, which some will resent; the alternative (movable canonical) is the exploit itself, so we accept the friction. (6) Cross-discipline landmarks depend on expert panels defining 'median accepted' / 'top-decile' — subjective anchors, but published and versioned so a funder can contest them. (7) Isotonic curves can overfit small held-out sets; k-fold CV error is published so overfit shows up as a large mae_cv rather than hiding.

  _Open questions:_ 1) How to keep the held-out expert calibration set both large enough for tight CV error AND unpredictable enough to resist memorization by frontier judge models — rotation helps but the frontier moves fast. 2) Inter-expert ICC is itself only ~0.7 in subjective significance judgement; the calibrated score can be no more reliable than the human ceiling it targets, and we have not solved how to represent 'the experts themselves disagree' beyond widening the CI. 3) Truly interdisciplinary or paradigm-creating work may fall outside every discipline's reference distribution, where percentile landmarks are ill-defined — the current fallback (report under multiple codes) is a patch, not a theory. 4) Adversarial prose that survives the leakage detector but still steers a judge subtly (framing effects the detector doesn't catch) remains an open red-team frontier. 5) Whether re-inference stability bands should feed back into recalibration triggers (an unstable ensemble is arguably a drift signal) is unresolved. 6) The corpus snapshot's completeness at publication time is assumed; genuinely undisclosed or embargoed prior art absent from the index cannot be caught by k-NN and remains a blind spot.

  _Changes from critique:_ Addressed all six critique points directly. (1) CALIBRATION — added a full CALIBRATION.yaml artifact plus a Calibration & Drift protocol: per-discipline held-out expert set (min 60 ARAs, ≥3 experts each), stated isotonic-regression curve fit, published k-fold-CV MAE + ICC(2,k) + residual RMSE per discipline, quarterly drift-audit cadence, and a concrete numeric recalibration trigger (rolling audit MAE > release MAE + 5, or ensemble-vs-expert ICC < 0.70). The confidence interval now explicitly combines ensemble-disagreement variance with calibration-residual variance via bootstrap. (2) CANONICAL RUN — added RUN_REGISTRY.yaml: author pre-registers N (odd, 3-7) and a seed policy BEFORE any score is revealed; the authoritative score is the sealed median of exactly those N runs; extra runs are recorded but structurally inadmissible. (3) NEIGHBORHOOD STEERING — REFGRAPH now runs three independent queries (author-independent title/abstract embedding q_auto is primary; q_anchor and q_concepts are secondary) and reports neighborhood_divergence with a steering_flag when author-framed queries systematically miss neighbors q_auto finds. (4) BLINDING — added a Brief De-identification protocol that neutralizes prose identity tells ('our prior work [ref]' → '[prior work RWxx]', normalizes named-dataset/style tells) with a leakage_detector that must pass before judges run. (5) REPRODUCIBILITY HONESTY — reproducibility is now two-tier and explicit: tier-1 byte-exact transcript replay for audit, tier-2 measured re-inference stability band (max_reinference_delta) reported per run; the score is never claimed identical under re-inference, only within a measured band. (6) CROSS-DISCIPLINE — added expert-anchored percentile landmarks (calibrated 50 = median accepted paper in discipline; 90 = top-decile significance) so the 0-100 axis is comparable in meaning across fields even though raw curves differ.

  _Adopted from competitor:_ Adopted from LENS-ON-ARA: (a) per-field-group provenance enum {author_asserted, ai_suggested, reviewer_confirmed} on NOVELANCHOR so an unconfirmed AI guess is distinguishable from a vetted claim; (b) discipline_taxonomy {scheme: openalex_concept|mesh|arxiv_category, code} to key the per-discipline calibration curve — this is the hook that makes cross-discipline normalization concrete; (c) author_citation_overlap_with_neighborhood as an explicit diagnostic (very low overlap flags a self-serving citation list; very high overlap with zero delta flags an incremental paper); (d) insufficient_coverage_flag as an honest null so a sparse-index subfield is never silently scored 'confirmed novel'; (e) input_cap.max_tokens_brief so verbosity cannot buy score; (f) injection_detector_version on the ensemble config; (g) publishing the ensemble's MAE alongside the config version — which I extended from a single float into a full per-discipline calibration record.

  _Why it wins:_ The competitor named calibration_mae_at_release as a single scalar but never specified the curve, the held-out set, per-discipline error, the drift cadence, or a recalibration trigger — the exact things the reviewer said a funder needs; LENS-ARA/CAL specifies all of them as a versioned, auditable artifact with a stated fit and cross-validated error bars. The competitor's protocol has no canonical-run rule at all, so it is silently vulnerable to the run-five-cite-the-best attack that the reviewer flagged for me; my RUN_REGISTRY pre-registration + sealed-median makes the authoritative number binding, not merely visible. My neighborhood defeats query-steering with three independent queries and a measured divergence flag, where the competitor still builds its neighborhood partly from author-authored claimed_sota_position. I retain the stronger anti-gaming spine the reviewer already credited me for (independent frozen k-NN, content-hashed append-only, red_team seat) and add the competitor's best hooks on top, so this design dominates rather than trades.


---


## ENTAIL — Type-aware entailment / alignment quality

_Class C — irreducibly semantic (reproducibility + auditability)_


**Judge rationale:** All four proposals share the correct core architecture (deterministic per-edge packet + type-conditioned rubric dispatch + adversarial multi-judge + mandatory span grounding + calibration), so the ranking is decided entirely by how each handles the FOUR things that actually determine Class C fitness: (a) confidence provenance, (b) measured run-to-run stability, (c) Goodhart/fabrication defenses, and (d) the packet-assembler bottleneck.

WINNERS. #3 (Entailment Court) and #2 (TREV) are the only two that (i) explicitly reject self-reported confidence and derive it from an external signal, and (ii) build concrete anti-gaming machinery. #3 wins the top slot because it is the ONLY proposal that operationalizes the mandate's literal phrase 'stable run-to-run' as a first-class, versioned stability audit, and because its Structural Pre-Check shows measurement-theory maturity — it spends determinism where determinism is available and reserves the LLM for genuinely ambiguous residue, which is exactly the right Class-C posture (don't launder mechanical checks through a stochastic judge). It also cleanly unifies entailment (D1/S4/M19/M49) with scope calibration (D3) as the same slot-match against different rubric fields. #2 takes second because its anti-gaming design is actually the tightest of the four — agreement-rate-as-confidence, contested-never-force-resolved, and planted-negatives that GATE trust in a rubric+judge combo — and its 'exact substring already in the packet' span rule is the most mechanically enforceable grounding constraint proposed. #2 edges out both gpt-5.5-codex entries decisively on the trust-gating idea.

WHY NOT #1/#0. #1 (VERITAS) is genuinely strong — median_with_adversarial_floor is the most concrete aggregation rule submitted, and scope_revision (judge proposes the narrower supported claim) is a nice touch — but it leaks judge degrees of freedom via allowed_context ('bounded extra context'), keeps a required self-reported confidence[0,1] on every ballot, and, fatally for Class C, ASSERTS reproducibility through temperature=0 pinning rather than MEASURING it: no stability audit, no calibration-based trust gate. #0 (EDGE-TRIALS) has the richest claim-type taxonomy and real benchmark-level kappa/false-entailed thresholds, but its verdict record carries a self-reported confidence[0,1] whose downstream exclusion it never states (an ambiguity that is itself a fabrication surface), it burns a judge call on every single edge (no structural pre-check), and its reproducibility story stops at benchmark kappa rather than per-verdict run-to-run stability. Both gpt entries are also truncated exactly at the protocols/aggregation section — the part where the hardest commitments live — so I can only credit what's shown, and what's shown is measurably behind #2/#3 on confidence provenance and stability measurement.

The decisive axis was honesty about the two surfaces every one of these designs actually depends on: the confidence number and the packet assembler. #2 and #3 are the only two that get the confidence number right; both still under-govern the assembler (I flag it in each critique), but they lead the field.


### Finalist A (refined)

> _Judge critique it answered:_ The Entailment Court is the strongest submission because it is the only one that treats "stable run-to-run" as something to MEASURE (the sampled stability audit) rather than something to ASSERT via temperature=0 pinning. But that best asset is also its most underspecified, and it hides three real holes:

1. STABILITY AUDIT MEASURES NOTHING AS WRITTEN. "Re-run k times, measure run-to-run agreement" — with pinned model + prompt_hash + temperature 0, your k re-runs are near-identical by construction, so the audit will report spuriously high stability and certify reproducibility you didn't earn. The actual Class C threat is (a) provider nondeterminism at t=0 and (b) cross-version drift when a judge model bumps. Your audit must perturb something semantically inert — paraphrase-invariant prompt variants, quantity-row-order shuffles, judge-panel-order permutation — and gate on INVARIANCE across those. As specified, it audits determinism theater, not stability.

2. CONFIDENCE PROVENANCE IS A CATEGORY ERROR. calibrated_confidence is "derived from CALIBRATION_REPORT accuracy-by-rubric." That is a per-BUCKET property: two edges with the same rubric+panel receive identical confidence no matter that one was unanimous and the other was a 2-1 knife-fight. You threw away the per-edge agreement signal that TREV keeps. Either fuse agreement-rate (edge-level) with rubric accuracy (bucket-level) explicitly, or state which one wins — silently labeling a contested edge with the bucket's average accuracy is itself a fabrication surface, because the number reads as "how sure are we about THIS verdict" when it is not.

3. THE STRUCTURAL PRE-CHECK IS A NEW GOODHART HOLE, NOT JUST A COST SAVER. Disposing of mechanically-obvious failures without an LLM call is smart, but the moment authors learn which fields the pre-check reads, they stuff a nominal `baseline` field (or rename it to dodge disqualification) to route a weak claim past the cheap gate into the more gameable panel — or a valid claim gets structurally killed on a naming mismatch. The pre-check needs its own audit record, an adversarial test suite against ITSELF, and a "pre-check overturned on appeal" escape valve. Right now it is an ungoverned deterministic filter sitting upstream of everything.

4. disallowed_evidence PATTERNS SMUGGLE BACK THE DOF YOU CLAIM TO REMOVE. "observational_correlation_only" and "single_arm_pre_post_no_control" require SOMEONE to classify the evidence into a pattern. If the judge does it, it is an ungoverned semantic step — exactly what your dossier was supposed to eliminate. Specify who tags evidence with these patterns and how that tagging is itself reproducible/audited.

5. ENTAILMENT vs SCOPE VERDICT INTERACTION IS UNDEFINED. You proudly reuse one protocol for D1/S4/M19/M49 AND D3, but verdict=entailed_strong with scope_verdict=overclaims is a legal, contradictory-looking pair. Downstream metrics will double-count or disagree unless you specify precedence (does an overclaim cap the entailment bucket?).

6. HONESTY GAP ON TRUST REVOCATION. You have a CALIBRATION_REPORT with accuracy-by-rubric but never state the false-entailed threshold or what happens when a rubric+judge combo falls below it — are past verdicts under that combo retroactively marked untrusted? TREV gates trust explicitly; you must too, or "calibrated" is decorative.

**TREV/2 — Typed-Rubric Entailment Verification with Governed Assembly, Blind Calibration, and a Recompute Contract**  ·  _source: Claude Opus 4.8 (finalist B, TREV lineage)_

TREV/2 keeps the winning core — confidence is ensemble agreement (never self-report), a first-class never-force-resolved `contested` state, machine-executable rubric checks, and planted-negative gating — and repairs the six load-bearing gaps. It gives confidence real resolution by voting over J judges × R runs and reporting a bootstrap interval plus a calibration-derived confidence, so one dissenter can no longer flip trust. It kills the contested escape hatch with a defined, non-gameable disposition: contested is scored as a `not_entailed` floor (no support credit, never worse), so engineering a borderline claim buys nothing. It makes the assembler accountable to the rubric: a coverage manifest must prove the packet contains every field and every disconfirming quantity the rubric interrogates, and an omission audit records what QUANT/EDGES held but the packet excluded — an ungrounded packet is rejected, not judged. Calibration moves to a two-tier public-anchor + private-rotating-blind set with a prompt-freeze-before-draw rule, so overfitting the known planted cases is detectable and gated. Finally it specifies a real recompute contract (stratified sampled re-run on any version bump, contested always re-run) rather than merely detecting staleness. It still does not make entailment deterministic — it makes the inputs deterministic, the assembly auditable, the confidence resolved, and the run-to-run recompute policy explicit.

- **RUBRIC (type-conditioned entailment rubric, coverage-driving)** (YAML, append-only central registry (shared infra), referenced by rubric_id + version from every packet and verdict) — Ecosystem-shared, versioned codebook mapping claim_type -> the design elements + disconfirming quantities evidence must exhibit to entail that claim type. Now also (a) declares interrogated_fields that GOVERN the assembler's coverage guarantee, (b) carries disallowed_evidence patterns (stolen from competitor) for a zero-LLM structural pre-check, and (c) carries a contested_threshold learned from the calibration set rather than a hand-picked 0.66.
  - fields: rubric_id: string — required. claim_type: enum{causal,generalization,improvement,descriptive,scoping,existence,correlational,theoretical} — required. required_design_elements: list[{id, description, machine_check: string|null (deterministic pre-check expression), semantic: bool}] — required, >=1. interrogated_fields: list[{field_ref, kind: enum{quantity_type, design_field, scope_field}, disconfirmer: bool}] — required — the exhaustive set the assembler MUST cover or flag; disconfirmer=true marks fields whose ABSENCE the adversarial pass needs (e.g. heterogeneity_I2, subgroup_CI). disallowed_evidence: list[string] — required, may be empty (patterns that structurally cannot satisfy this type, e.g. observational_correlation_only for causal). disqualifying_conditions: list[string] — required. scope_checks: list[string] — required (the D3 sub-rubric). verdict_enum: fixed [entailed, partially_entailed, not_entailed, insufficient_evidence] — required. contested_threshold: float — required — learned as the raw-agreement level below which calibration accuracy drops under target (not hand-set). version: semver — required. prompt_freeze_ref: string — required — hash+timestamp of the judge prompt frozen for this rubric version (see calibration protocol). superseded_by: string|null.
  - example: rubric_id: RUBRIC-improvement-v2
claim_type: improvement
required_design_elements:
  - id: baseline_comparator
    machine_check: "exists q in packet.quantities where role=baseline and q.id in claim.quantities_cited.comparators"
    semantic: false
  - id: statistical_comparison
    machine_check: "packet.delta.ci != null or packet.delta.p_value != null"
    semantic: false
  - id: same_population_comparison
    machine_check: null
    semantic: true
interrogated_fields:
  - {field_ref: quantity.role=baseline, kind: quantity_type, disconfirmer: false}
  - {field_ref: quantity.role=delta.ci, kind: quantity_type, disconfirmer: false}
  - {field_ref: quantity.type=heterogeneity_I2, kind: quantity_type, disconfirmer: true}
  - {field_ref: design.population_overlap_adjustment, kind: design_field, disconfirmer: true}
  - {field_ref: scope.population, kind: scope_field, disconfirmer: false}
disallowed_evidence:
  - single_arm_no_comparator
  - baseline_from_unadjusted_different_population
disqualifying_conditions:
  - "No baseline quantity present anywhere in packet.quantities."
scope_checks:
  - "claim.scope.population must not exceed union of cited quantities' source cohorts."
verdict_enum: [entailed, partially_entailed, not_entailed, insufficient_evidence]
contested_threshold: 0.72   # learned: below this raw-agreement, calibrated accuracy < 0.85
version: 2.0.0
prompt_freeze_ref: "sha256:1c0a...@2026-04-01T00:00:00Z"
- **ENTAIL_PACKET (governed, coverage-audited judge input)** (YAML, one file per edge, produced at compile/verify time, content-hashed) — The single object a judge ever sees, assembled by a mechanical join over CLAIMFOL+EDGES+QUANT — no LLM, no prose. Upgraded so the assembler is accountable: it must (1) pull every rubric-interrogated field INCLUDING disconfirmers (not just the claim's chosen support), (2) emit a coverage_manifest proving each interrogated field is present or a declared gap, and (3) emit an omission_audit of in-scope QUANT/EDGES facts it excluded and why. Replaces the shallow completeness_flag with a rubric-conditioned coverage_status that distinguishes an evidence defect from an assembly defect.
  - fields: packet_id — required. packet_hash: sha256 of canonicalized content — required. assembler_version: semver — required. edge_id — required. rubric_id — required (fixes the interrogation set). claim: {id, claim_type, statement_excerpt (verbatim, <=400 chars), scope} — required. counterparty: {id, relation, design_summary (verbatim), population, baseline_ref} — required. quantities: list[{id, value, unit, ci, role, type, source_anchor:{file,locator,quote}}] — required — MUST include every quantity the claim cites, every id the edge declares as measures, AND every quantity in the experiment's QUANT scope matching an interrogated_field with disconfirmer=true. coverage_manifest: list[{interrogated_field_ref, satisfied_by: packet_element_id|null, status: enum{present, gap_evidence_absent_in_source, gap_present_but_not_joinable}}] — required — one row per rubric.interrogated_fields entry. omission_audit: list[{source_id, source_layer, reason_excluded}] — required, may be empty — every in-scope QUANT/EDGES fact NOT placed in the packet, with a machine reason. coverage_status: enum{complete, incomplete_evidence_absent, incomplete_assembly_defect} — required, DERIVED from coverage_manifest (assembly_defect if any status=gap_present_but_not_joinable). packet_valid: bool — required — FALSE if coverage_status=incomplete_assembly_defect; an invalid packet is re-assembled, never judged.
  - example: packet_id: PKT-C01-E01
packet_hash: sha256:7ac9...
assembler_version: 3.1.0
edge_id: EDG-014
rubric_id: RUBRIC-improvement-v2
claim:
  id: C01
  claim_type: improvement
  statement_excerpt: "p217_MS achieved the highest rank (P-score=0.859) ... p181_IA ranked last (0.117)."
  scope: {population: "prodromal/MCI, BioFINDER-1 + 17 cohorts", generalization_bound: "not claimed beyond prodromal/MCI"}
counterparty:
  id: E01
  relation: tests
  design_summary: "Random-effects frequentist NMA (netmeta); P-score ranking over 8 nodes; p181_IA reference."
  population: "18 studies, 24 cohort-datasets, de-overlapped"
  baseline_ref: Q-013
quantities:
  - {id: Q-014, value: 0.859, unit: P-score, role: treatment, type: result, source_anchor: {file: evidence/tables/table2.md, locator: "T2 O1 R1", quote: "p217_MS (0.859)"}}
  - {id: Q-013, value: 0.117, unit: P-score, role: baseline, type: result, source_anchor: {file: evidence/tables/table2.md, locator: "T2 O1 R8", quote: "p181_IA (0.117)"}}
  - {id: Q-021, value: 0.10, unit: AUC-MD, ci: "[0.04;0.16]", role: delta, type: result, source_anchor: {file: evidence/figures/figure3.md, locator: "3A", quote: "0.10 [ 0.04; 0.16]"}}
  - {id: Q-030, value: 41.2, unit: I2-percent, role: heterogeneity, type: heterogeneity_I2, source_anchor: {file: evidence/tables/table3.md, locator: "T3 O1", quote: "I^2 = 41.2%"}}   # disconfirmer pulled even though claim never cites it
coverage_manifest:
  - {interrogated_field_ref: quantity.role=baseline, satisfied_by: Q-013, status: present}
  - {interrogated_field_ref: quantity.role=delta.ci, satisfied_by: Q-021, status: present}
  - {interrogated_field_ref: quantity.type=heterogeneity_I2, satisfied_by: Q-030, status: present}
  - {interrogated_field_ref: design.population_overlap_adjustment, satisfied_by: null, status: gap_evidence_absent_in_source}
  - {interrogated_field_ref: scope.population, satisfied_by: claim.scope.population, status: present}
omission_audit:
  - {source_id: Q-045, source_layer: QUANT, reason_excluded: "different outcome (Outcome 2), not in edge's declared measures"}
coverage_status: incomplete_evidence_absent   # one honest gap, but NOT an assembly defect
packet_valid: true
- **ENTAIL_VERDICT (single judge-run output, defect-typed)** (YAML, one record per (packet, judge, run)) — One judge-run's structured, span-grounded assessment of one packet against its rubric — the atomic unit the ensemble votes over. Now the interrogation is anchored to coverage_manifest rows so a judge cannot invent a missing-evidence excuse, and insufficient_evidence must name a defect_type distinguishing a real evidence gap from an assembly gap (the latter is impossible since packet_valid gates it, so insufficient_evidence can only mean evidence_absent_in_source).
  - fields: verdict_id, packet_id, packet_hash, rubric_id — required. judge:{model_id, role: independent_judge, temperature, seed, run_index, prompt_hash} — required (run_index makes J×R runs addressable). verdict: enum from rubric.verdict_enum — required. required_elements_met: list[{id, met: bool|na, evidence_span: exact substring of a quote already in the packet — deterministically validated, else verdict rejected}] — required, one per rubric requirement. disconfirmer_findings: list[{interrogated_field_ref, present_in_packet: bool, undermines_claim: bool, evidence_span}] — required, one per disconfirmer field — forces the adversarial pass to actually inspect I2/CI/overlap. scope_calibration: {claimed_scope, evidence_scope, verdict: enum{matched, over_claimed, under_claimed, unresolvable}} — required (D3 output). insufficient_reason: {defect_type: enum{evidence_absent_in_source} | null} — required-nullable — non-null ONLY when verdict=insufficient_evidence. for_argument / against_argument: string <=150 words each — required (dual pass). confidence_self_reported: float — recorded, explicitly NOT used downstream. timestamp — required.
  - example: verdict_id: V-EDG014-claude-r2
packet_id: PKT-C01-E01
packet_hash: sha256:7ac9...
rubric_id: RUBRIC-improvement-v2
judge: {model_id: claude-opus-4.6, role: independent_judge, temperature: 0.3, seed: 20260706, run_index: 2, prompt_hash: sha256:9f2a...}
verdict: partially_entailed
required_elements_met:
  - {id: baseline_comparator, met: true, evidence_span: "p181_IA (0.117)"}
  - {id: statistical_comparison, met: true, evidence_span: "0.10 [ 0.04; 0.16]"}
  - {id: same_population_comparison, met: false, evidence_span: "18 studies, 24 cohort-datasets, de-overlapped"}
disconfirmer_findings:
  - {interrogated_field_ref: quantity.type=heterogeneity_I2, present_in_packet: true, undermines_claim: true, evidence_span: "I^2 = 41.2%"}
  - {interrogated_field_ref: design.population_overlap_adjustment, present_in_packet: false, undermines_claim: true, evidence_span: null}
scope_calibration: {claimed_scope: "prodromal/MCI", evidence_scope: "prodromal/MCI, de-overlapped", verdict: matched}
insufficient_reason: null
for_argument: "Baseline and treatment ranked under one connected NMA model; delta CI excludes zero."
against_argument: "I^2=41.2% signals moderate heterogeneity and no population-overlap adjustment is stated; ranking stability across the 8-node network is not guaranteed, so 'highest rank' is weakly rather than strongly entailed."
confidence_self_reported: 0.71
timestamp: 2026-07-06T14:02:00Z
- **ENTAIL_CONSENSUS (ensemble-aggregated verdict with resolved confidence + disposition + recompute status)** (YAML, append-only per edge (new consensus supersedes, never overwrites)) — The one durable, per-edge fact the rest of the ecosystem reads (D1/S4/M19/M49/D3). Aggregates J×R verdicts; reports BOTH a bootstrap agreement interval (resolution, fixes critique 1) and a calibration-derived confidence (accuracy-anchored, stolen from competitor); attaches a defined contested_disposition (fixes critique 2); and carries recompute_status governed by the recompute contract (fixes critique 6).
  - fields: edge_id, claim_id, experiment_or_evidence_id, rubric_id, packet_hash — required. ensemble: {judges: list[model_id], runs_per_judge: int, n_valid_verdicts, n_rejected_verdicts (ungrounded spans discarded)} — required. verdict_tally: map[verdict_enum->count] — required, deterministic. consensus_verdict — required, plurality of tally. raw_agreement: float = max(tally)/n_valid — required (kept for transparency). agreement_ci: {lo, hi, method: 'bootstrap_over_JxR', n_resamples} — required — the resolved confidence interval that replaces the 3-point float. calibrated_confidence: float[0,1] — required — read from CALIBRATION_REPORT accuracy for (rubric, judge_panel, raw_agreement bucket) on the BLIND set; null if the combo is ungated. contested: bool = raw_agreement < rubric.contested_threshold OR agreement_ci.lo < rubric.contested_threshold — required. contested_disposition: enum{none, scored_as_not_entailed_floor, escalated_pending} — required — non-gameable rule: contested edges are scored as not_entailed for any support-rewarding metric (no credit) AND flagged escalated_pending; never scored worse than not_entailed (honest-absence symmetry). scope_calibration_consensus — required. dissent_record: list[{judge, run_index, verdict, reason}] — required when contested. calibration_report_ref — required. recompute_status: enum{current, stale_flagged, revalidated_by_sample, superseded} — required. supersedes / superseded_by — appeal trail.
  - example: edge_id: EDG-014
claim_id: C01
experiment_or_evidence_id: E01
rubric_id: RUBRIC-improvement-v2
packet_hash: sha256:7ac9...
ensemble: {judges: [claude-opus-4.6, gpt-5.4, gemini-3-pro], runs_per_judge: 4, n_valid_verdicts: 11, n_rejected_verdicts: 1}
verdict_tally: {entailed: 3, partially_entailed: 7, not_entailed: 1, insufficient_evidence: 0}
consensus_verdict: partially_entailed
raw_agreement: 0.636
agreement_ci: {lo: 0.55, hi: 0.82, method: bootstrap_over_JxR, n_resamples: 2000}
calibrated_confidence: 0.81
contested: false   # ci.lo 0.55 < 0.72 threshold? -> actually true here; shown resolving below
contested_disposition: none
scope_calibration_consensus: matched
dissent_record: []
calibration_report_ref: CAL-2026Q3-blind
recompute_status: current
supersedes: null
- **CALIBRATION_REPORT (two-tier: public anchor + private rotating blind, gating + generalization gap)** (YAML, central infra, one per (quarter, rubric-family), append-only) — The trust gate. Splits calibration into a PUBLIC frozen anchor set (used to develop and freeze judge prompts, fully reproducible) and a PRIVATE rotating blind set (refreshed each quarter, never shown to rubric/prompt authors). Gating uses the BLIND set's false-entailed rate; the anchor-minus-blind accuracy gap is the overfitting detector. This is what fixes critique 3 — you can no longer tune to the known planted cases.
  - fields: calibration_id — required. quarter — required. rubric_ids_covered: list — required. anchor_set: {set_hash, n_cases, public: true, planted_negatives: int} — required. blind_set: {set_hash, n_cases, drawn_at: timestamp, released_after_prompt_freeze: bool} — required — released_after_prompt_freeze MUST be true for gating to count. per_combo: list[{rubric_id, judge_panel_hash, anchor_accuracy, blind_accuracy, blind_false_entailed_rate, generalization_gap: float = anchor_accuracy - blind_accuracy, gated: bool}] — required. gate_rule: string — required (e.g. 'trusted iff blind_false_entailed_rate <= 0.05 AND generalization_gap <= 0.10'). accuracy_by_agreement_bucket: map[bucket -> blind_accuracy] — required — the lookup that populates ENTAIL_CONSENSUS.calibrated_confidence.
  - example: calibration_id: CAL-2026Q3-blind
quarter: 2026Q3
rubric_ids_covered: [RUBRIC-improvement-v2, RUBRIC-causal-v3]
anchor_set: {set_hash: sha256:aa11..., n_cases: 120, public: true, planted_negatives: 40}
blind_set: {set_hash: sha256:bb22..., n_cases: 90, drawn_at: 2026-07-01T00:00:00Z, released_after_prompt_freeze: true}
per_combo:
  - {rubric_id: RUBRIC-improvement-v2, judge_panel_hash: sha256:cc33..., anchor_accuracy: 0.94, blind_accuracy: 0.88, blind_false_entailed_rate: 0.03, generalization_gap: 0.06, gated: false}
  - {rubric_id: RUBRIC-causal-v3, judge_panel_hash: sha256:cc33..., anchor_accuracy: 0.96, blind_accuracy: 0.79, blind_false_entailed_rate: 0.11, generalization_gap: 0.17, gated: true}   # overfit + leaks false-entailed -> UNTRUSTED
gate_rule: "trusted iff blind_false_entailed_rate <= 0.05 AND generalization_gap <= 0.10"
accuracy_by_agreement_bucket: {"[0.5,0.66)": 0.74, "[0.66,0.8)": 0.85, "[0.8,1.0]": 0.93}
- **STABILITY_AUDIT (sampled run-to-run reproducibility record)** (YAML, central infra, append-only per (quarter, judge_panel_version)) — First-class, versioned reproducibility evidence (stolen and hardened from competitor). On a stratified sample of edges, re-run the full J×R panel k times on the SAME packet_hash and measure verdict stability. This both feeds the recompute contract's drift tolerance and gives auditors a direct run-to-run number instead of a claim.
  - fields: audit_id — required. sample: {n_edges, stratified_by: [claim_type, raw_agreement_bucket]} — required. k_repeats — required. per_edge: list[{edge_id, verdict_mode, verdict_flip_rate, agreement_ci_width_mean}] — required. panel_stability: {verdict_flip_rate_overall, contested_flip_rate} — required. drift_tolerance_used — required (the threshold the recompute contract consumes).
  - example: audit_id: STAB-2026Q3-panelA
sample: {n_edges: 200, stratified_by: [claim_type, raw_agreement_bucket]}
k_repeats: 5
per_edge:
  - {edge_id: EDG-014, verdict_mode: partially_entailed, verdict_flip_rate: 0.10, agreement_ci_width_mean: 0.22}
panel_stability: {verdict_flip_rate_overall: 0.07, contested_flip_rate: 0.19}
drift_tolerance_used: 0.10

  _Protocols:_
  - **Governed Assembly + Coverage Guarantee** — Once per edge before any judge is invoked.. 1. Look up RUBRIC by claim_type -> get interrogated_fields (incl. disconfirmers) and machine_checks. 2. Mechanical join CLAIMFOL+EDGES+QUANT copy-by-reference (no LLM, no paraphrase). 3. Disconfirmer pull: for every interrogated_field with disconfirmer=true, scan the experiment's full QUANT scope and place any matching quantity in the packet EVEN IF the claim never cites it (this is what un-disarms the adversarial judge). 4. Emit coverage_manifest: one row per interrogated_field, status present / gap_evidence_absent_in_source / gap_present_but_not_joinable. 5. Emit omission_audit: every in-scope QUANT/EDGES fact left out, with a machine reason. 6. Derive coverage_status and packet_valid; if any manifest row is gap_present_but_not_joinable, packet_valid=false -> re-assemble, do not judge. 7. Content-hash the packet.
    - reliability/reproducibility: Assembly is fully deterministic given source hashes + assembler_version, so packet_hash is reproducible. The coverage_manifest makes the assembler's recall auditable: a reviewer can diff omission_audit against QUANT to catch a suppressed disconfirmer. gap_present_but_not_joinable vs gap_evidence_absent_in_source cleanly separates an assembly defect from a genuine evidence gap.
    - constraints: Ecosystem must provide: a typed QUANT ledger with role/type tags (heterogeneity, CI, subgroup), EDGES that declare experiment scope so 'in-scope QUANT' is well-defined, and a canonicalization spec so packet_hash is stable across tools.
  - **Structural Pre-Check (zero-LLM disposition)** — After assembly, before spending any judge call.. 1. Evaluate every rubric.required_design_elements.machine_check and rubric.disallowed_evidence pattern deterministically over the packet. 2. If a disqualifying_condition or disallowed_evidence pattern matches, emit consensus_verdict=not_entailed with method=structural_pre_check and skip the panel. 3. Otherwise pass the packet to the ensemble.
    - reliability/reproducibility: Deterministic and free; removes mechanically-obvious failures from the semantic budget and prevents judges from 'rescuing' a claim that structurally cannot be entailed (e.g. improvement claim with no baseline anywhere).
    - constraints: machine_check expressions must be evaluated by a shared, versioned checker; the checker version is stamped so a pre-check verdict is reproducible.
  - **Ensemble Adjudication with Runs-per-Judge + Bootstrap Confidence** — For every packet that survives the pre-check.. 1. Run J>=3 cross-provider judges, each R>=3 times (independent seeds; optional temperature>0 and packet-field-order shuffle to probe stability). 2. Each run emits an ENTAIL_VERDICT with span-grounded required_elements_met AND disconfirmer_findings; any verdict whose evidence_span is not an exact packet substring is REJECTED, not counted. 3. Tally the J×R valid verdicts. 4. consensus_verdict = plurality. 5. raw_agreement = max(tally)/n_valid; agreement_ci = bootstrap over the J×R pool. 6. calibrated_confidence = CALIBRATION_REPORT lookup for (rubric, panel, agreement bucket) on the blind set. 7. contested = raw_agreement < threshold OR ci.lo < threshold.
    - reliability/reproducibility: J×R (e.g. 3×4=12) gives the confidence real resolution and a bootstrap interval, so a single dissenter no longer flips trust — it widens the interval instead. Seeds + prompt_hash + packet_hash make each run reproducible; STABILITY_AUDIT measures residual run-to-run flip rate directly. Confidence is never self-reported: it is agreement (resolution) cross-checked against measured blind-set accuracy (calibration).
    - constraints: Cost scales with J×R — priced explicitly: pre-check + contested-only deep runs keep the average J×R small. Ecosystem must fund >=3 independent providers and a bootstrap utility with a fixed resample seed for reproducibility.
  - **Blind-Rotating Calibration + Gating (prompt-freeze-before-draw)** — Per quarter, and whenever a rubric or judge prompt version changes.. 1. Authors develop and FREEZE judge prompts against the PUBLIC anchor set; record prompt_freeze_ref (hash+timestamp) in the RUBRIC. 2. AFTER freeze, an independent party draws the quarter's PRIVATE blind set (fresh planted negatives + held-out real cases), never shown to prompt/rubric authors. 3. Run the frozen panel over both sets; compute anchor_accuracy, blind_accuracy, blind_false_entailed_rate, generalization_gap. 4. Apply gate_rule; a combo that leaks false-entailed on the blind set OR shows a large generalization gap is UNTRUSTED — its verdicts carry calibrated_confidence=null and are excluded from support-rewarding metrics. 5. Publish accuracy_by_agreement_bucket for the confidence lookup.
    - reliability/reproducibility: The freeze-before-draw rule makes overfitting the known planted cases mechanically detectable (generalization_gap) and un-rewarding (gating). Rotation prevents a static id from being memorized. Anchor set stays public so calibration itself is reproducible; blind set stays private so it cannot be gamed.
    - constraints: Ecosystem must run an independent calibration authority that (a) curates rotating blind cases, (b) enforces the freeze timestamp ordering, and (c) publishes only aggregate accuracy, never blind cases, until the quarter closes.
  - **Contested Disposition + Escalation (no escape hatch)** — Whenever contested=true.. 1. Set contested_disposition=scored_as_not_entailed_floor: for every support-rewarding downstream metric (D1/S4/M19/M49), a contested edge counts EXACTLY as not_entailed — no support credit. 2. Simultaneously flag escalated_pending for human/arbiter review; resolution can later supersede the consensus. 3. Never score contested worse than not_entailed (honest-absence symmetry) and never silently drop it from scoring.
    - reliability/reproducibility: Deterministic mapping from contested -> not_entailed floor closes the incentive to engineer borderline claims: triggering contest yields the same zero credit as an honest not_entailed, so there is nothing to win. Escalation preserves honesty — genuinely hard cases still get a human path — without creating a scoring exemption.
    - constraints: Downstream metric specs must import this disposition rule; an arbiter/human review queue must exist for escalated_pending edges.
  - **Recompute Contract** — On any judge model version bump, rubric version bump, assembler version bump, or packet_hash change.. 1. Detect the delta via stamped hashes/versions; mark affected ENTAIL_CONSENSUS records stale_flagged. 2. Draw a stratified sample (by claim_type, agreement bucket) and re-run the full panel. 3. Compare to STABILITY_AUDIT drift_tolerance: if sample verdict-flip rate <= tolerance, bulk-mark the population revalidated_by_sample (no full re-run); if > tolerance, require full re-run and mark superseded on replacement. 4. Contested edges are ALWAYS fully re-run regardless of sample outcome. 5. Every transition is append-only and timestamped.
    - reliability/reproducibility: Turns staleness DETECTION into a defined recompute POLICY: readers always know whether a record is current, sample-revalidated, or superseded, and the sample-vs-full decision is governed by a measured drift number, not a guess.
    - constraints: Ecosystem CI must trigger the contract on registry/model version bumps; must retain old records (append-only) so supersession is auditable; must budget the sampled re-run.

  _Metrics afforded:_
  - Per-edge entailment quality (feeds D1/S4/M19/M49) → consensus_verdict from J×R ensemble over a governed packet, with contested mapped to not_entailed floor. [semantic-judged]; anti-Goodhart: Verdict rides on span-grounded citations that must exactly substring-match packet quotes (ungrounded verdicts discarded); the packet is a fixed exhibit, so a claim cannot be padded into support. Contested cannot be used to escape a not_entailed score. Only calibration-gated judge combos count.
  - Verdict confidence (resolution + accuracy) → agreement_ci bootstrap over J×R runs, cross-checked against blind-set accuracy_by_agreement_bucket to produce calibrated_confidence. [reproducible]; anti-Goodhart: Confidence is never self-reported; it is ensemble agreement (now resolved to an interval, not a 3-point float) validated against measured accuracy on a rotating BLIND set, so a judge cannot inflate its own certainty and a combo cannot inflate accuracy by memorizing static planted cases.
  - Assembler coverage integrity → Fraction of interrogated_fields with status=present vs declared gaps, plus omission_audit completeness, per packet. [deterministic]; anti-Goodhart: A packet is invalid (not judged) if a rubric-interrogated field is present-in-source but not joined; disconfirmer quantities are force-pulled regardless of what the claim cites, so an author cannot win by having the assembler quietly omit the I2/CI that would sink the claim.
  - Scope calibration / over-claiming (D3) → scope_calibration_consensus over the same panel using rubric.scope_checks — same protocol, different rubric fields. [semantic-judged]; anti-Goodhart: over_claimed requires a cited evidence_scope span; a claim cannot broaden scope for free because the mismatch is grounded in the packet's population fields.
  - Calibration trust / false-entailed rate → blind_false_entailed_rate + generalization_gap per (rubric, judge_panel) on the private rotating set. [reliable-anchored]; anti-Goodhart: Freeze-before-draw + rotation make prompt overfitting detectable (generalization_gap) and un-rewarding (gating drops confidence to null and excludes the combo from support metrics).
  - Run-to-run stability → verdict_flip_rate and contested_flip_rate from k repeated panels on identical packet_hash (STABILITY_AUDIT). [reproducible]; anti-Goodhart: Measured directly on frozen inputs, so instability cannot be hidden; also sets the drift_tolerance the recompute contract consumes, preventing 'silently stale' verdicts from passing as current.

  _Tradeoffs:_ Cost: J×R cross-provider runs plus a per-quarter blind calibration authority and stability audits are materially more expensive than a single-judge read — mitigated by the deterministic structural pre-check (obvious failures cost 0 LLM calls), by reserving deep J×R only for packets that survive pre-check, and by the recompute contract's sampled (not full) revalidation. Fabrication surfaces: (a) an author could try to keep a disconfirming quantity out of QUANT entirely so the assembler cannot pull it — mitigated because coverage_manifest then records gap_evidence_absent_in_source, which a causal/improvement rubric treats as failing its interrogated field, so hiding evidence reads as missing evidence, not as support; honest-absence symmetry still holds because a truly not-measured quantity scores the same as an honestly-declared absence, never as a fabrication. (b) A rubric author could weaken interrogated_fields to make claims easy — mitigated by central, versioned, ecosystem-shared rubrics with the blind-set gate: a lax rubric leaks false-entailed on the blind set and gets its combo untrusted. Residual risk: bootstrap confidence still degenerates toward the 3-point grid if R is set to 1 — the design REQUIRES R>=3 and reports agreement_ci width so a saturated/low-resolution confidence is visible rather than hidden. Contested floor risk: mapping contested to not_entailed slightly under-credits genuinely hard-but-true claims — mitigated by the escalated_pending human path that can later supersede, so the floor is a scoring default, not a permanent verdict. The calibration authority is a new trusted third party and a single point of governance failure — mitigated by making anchor sets public and gate_rules published so the authority's own decisions are auditable.

  _Open questions:_ 1. How large must the private blind set be, per rubric family, to estimate blind_false_entailed_rate at <=0.05 with tight enough CIs — and who funds refreshing genuinely novel adversarial cases each quarter without them leaking? 2. Optimal J and R under a real budget: is 3×4 enough for stable agreement_ci on high-stakes edges, and should R scale with observed instability? 3. Cross-provider judge correlation — if all frontier judges share training data, ensemble agreement may overstate independence; we need a measured judge-correlation term to discount calibrated_confidence, which this design flags but does not yet compute. 4. The disconfirmer pull depends on QUANT tagging heterogeneity/CI/subgroup types correctly upstream; if that ledger is thin, coverage_manifest will honestly report gaps but the adversarial layer stays weak — how much of entailment quality is actually bottlenecked on QUANT richness rather than on judging. 5. Drift tolerance for the recompute contract is currently a single scalar; whether it should be per-claim_type (causal verdicts may be more model-sensitive than existence verdicts) is unresolved.

  _Changes from critique:_ Addressed all six critique points directly. (1) Confidence resolution: added runs-per-judge R>=3 so voting is over J×R (e.g. 12) verdicts, replaced the 3-point float with a bootstrap agreement_ci plus a calibration-derived calibrated_confidence; contested now triggers on ci.lo, so one dissenter widens the interval instead of flipping trust. (2) Contested escape hatch closed: added contested_disposition=scored_as_not_entailed_floor — contested counts exactly as not_entailed for every support-rewarding metric (no credit, never worse), plus escalated_pending human path; engineering a borderline claim now buys nothing. (3) Blind rotating calibration: split into a public frozen anchor set and a private quarterly blind set with a prompt-freeze-before-draw rule, gate on blind_false_entailed_rate, and a generalization_gap overfitting detector. (4) Assembler governed: added a rubric-driven coverage_manifest, force-pull of disconfirmer quantities regardless of what the claim cites, and an omission_audit of excluded in-scope facts; an assembly-defect packet is rejected, not judged. (5) Rubric-conditioned completeness: replaced completeness_flag with coverage_status derived from the manifest and a defect_type separating evidence_absent_in_source from present_but_not_assembled. (6) Recompute contract: defined explicit triggers, stratified sampled re-run vs full re-run keyed to a measured drift tolerance, always-re-run for contested, and a recompute_status enum on every consensus record.

  _Adopted from competitor:_ Adopted the Structural Pre-Check (deterministic disposition of mechanically-obvious failures with zero LLM calls) and disallowed_evidence patterns in the rubric; the calibrated_confidence idea (confidence read from a calibration report's accuracy-by-rubric rather than from agreement alone); the first-class sampled STABILITY_AUDIT (re-run k times, measure run-to-run flip rate) as a versioned artifact; the candidate_evidence_files 'judge may quote ONLY from these' constraint, generalized into the span-must-substring-match-the-packet rule; and the observation that the SAME protocol computes both entailment quality and D3 scope calibration against different rubric fields.

  _Why it wins:_ The competitor keeps confidence anchored to a calibration report but never resolves the underlying agreement signal — with min_judges=3 and no runs-per-judge it inherits the same near-binary agreement TREV was criticized for; TREV/2 adds J×R bootstrap resolution on top of calibration, so it has both resolution and accuracy. The competitor's dossier lists candidate_evidence_files but has no coverage guarantee that the disconfirming quantities are actually present, so its adversarial for/against is still theater over whatever the join happened to pull; TREV/2's coverage_manifest + forced disconfirmer pull + omission_audit make assembler recall provable and auditable. The competitor stores calibrated_confidence but its gold set is a static periodic report with no freeze-before-draw or generalization-gap defense, so it is overfittable in exactly the way both designs were warned about; TREV/2's public-anchor/private-blind split with prompt-freeze ordering makes overfitting detectable and un-rewarding. Neither competitor field defines what happens to a contested/ambiguous edge downstream nor specifies a recompute policy on version bumps; TREV/2 nails both with the not_entailed floor and the sampled recompute contract. Net: same shared strengths, but TREV/2 removes the three structural escape hatches (saturated confidence, curated exhibit, static gold set) that the competitor leaves open.


### Finalist B (refined)

> _Judge critique it answered:_ TREV is the sharpest anti-gaming design of the four: confidence = ensemble agreement rate (never self-report), a first-class `contested` state that is never force-resolved, machine-executable rubric checks, and planted-negative calibration that GATES whether a rubric+judge combo is trusted at all. That gating is the single best Goodhart defense in the whole field. But the tight design has load-bearing gaps:

1. YOUR CONFIDENCE IS A 3-POINT SCALE WEARING A FLOAT COSTUME. agreement_rate = max(tally)/n_valid with three judges only ever emits {0.33, 0.66, 1.0}. Calling that a float and threshold-ing `contested` at 0.66 means one dissenter flips the entire trust state. Either grow the ensemble (cost you must price) or bootstrap agreement over runs-per-judge so the confidence has resolution. As-is, confidence is nearly binary and trivially saturated.

2. CONTESTED-NEVER-RESOLVED IS HONEST BUT CREATES AN ESCAPE HATCH. You never define what downstream metrics (D1/S4/M19/M49) DO with a contested edge. If contested edges are dropped from scoring, you have handed authors an incentive to write borderline claims engineered to trigger contest and thereby escape being scored `not_entailed`. Contested must carry a defined, non-gameable disposition — a penalty or a neutral floor — not a silent exemption.

3. PLANTED NEGATIVES ARE KNOWN TO THE RUBRIC AUTHORS. Your best move self-destructs if the calibration set is static and referenced by a fixed id ("ara-entailment-calibration-2026q2"). A judge prompt tuned against that set overfits the known planted cases and still waves through novel adversarial claims — you have measured the wrong thing. You need held-out, rotating, blind-refreshed planted negatives and a policy that judge prompts are frozen BEFORE seeing the current quarter's set.

4. THE PACKET ASSEMBLER IS AN UNGOVERNED EPISTEMIC BOTTLENECK. evidence_span must be "an exact substring of a quote already in the packet" — mechanically checkable, excellent — but it means a judge can only ground a contradiction on spans the deterministic join chose to include. If the assembler pulls the confirming P-score and omits the disconfirming heterogeneity/CI span, the adversarial judge is structurally disarmed: it cannot cite what isn't there. Your for/against discipline is only as adversarial as the assembler's recall. You need a coverage guarantee — the packet must provably contain the disconfirming quantities/design fields the rubric interrogates — and an audit of assembler omissions, or the whole "adversarial" layer is theater over a pre-curated exhibit.

5. completeness_flag IS TOO SHALLOW. It is deterministic on "missing_quantities" only. A packet can be `complete` on quantities yet omit the control/ablation design field a causal rubric requires. Completeness must be RUBRIC-CONDITIONED: does the packet contain every field this claim_type's rubric will interrogate? Otherwise a causal claim gets judged `insufficient_evidence` for a reason that is really an assembly defect, not an evidence defect.

6. STALENESS DETECTION ≠ RECOMPUTE POLICY. You stamp packet_hash + rubric_hash + judge version so re-runs are checkable — good — but never specify the trigger: when a judge model version bumps, are all ENTAIL_CONSENSUS records invalidated, re-run on a sample, or left stale-but-flagged? A reproducibility protocol has to define the recompute contract, not just detect that something changed.

**The Entailment Court v2 — governed structural gate + invariance-audited adversarial adjudication with explicit trust revocation**  ·  _source: Claude Opus 4.8_

Every claim↔experiment↔evidence EDGE is tried like a case, not read like an essay, but v2 fixes the six holes that let the old version certify reproducibility it never earned. Reproducibility is now MEASURED as invariance under semantically-inert perturbations (paraphrase-variant prompts, quantity-row shuffles, panel-order permutations, within-tier judge swaps) plus repeated t=0 runs to catch provider nondeterminism and a pinned shadow panel to catch cross-version drift — never as near-identical re-runs of a pinned prompt. Confidence stops being a category error: an edge carries BOTH a per-edge panel_agreement and a per-bucket rubric_reliability, fused by a published, monotone-capping formula so a 2-1 knife-fight can never inherit the bucket's average accuracy. The deterministic Structural Gate that disposes of mechanically-obvious failures is now itself governed — it matches on anchored quantity ROLE (not field name), emits an audit record per rule fired, is graded against an adversarial self-test suite of field-stuffing decoys and naming-variant valid claims, and every disqualification has an appeal valve that forces the edge into the full panel. Disqualifying evidence patterns are split into mechanical predicates (compiled over typed slots, run deterministically in the gate) and genuinely-semantic ones (asked as calibrated panel questions with span grounding) — no ungoverned single-actor tagging survives. Entailment and scope verdicts compose through a published precedence lattice into one deterministic effective_verdict (an overclaim caps entailment), and a CALIBRATION_REPORT with a hard false_entailed threshold explicitly revokes trust on any rubric+panel combo that fails it, retroactively marking every verdict it produced.

- **RUBRIC_REGISTRY.yaml** (YAML, versioned (semver), referenced by rubric_id+version+content-hash from every verdict; maintained centrally, append-only, superseded never deleted) — Ecosystem-wide, versioned catalog of one entailment rubric per CLAIMFOL claim_type. Converts 'infer what kind of test this claim needs' into a deterministic lookup and shrinks the judge to a closed checklist. v2 change: every disqualifier is TYPED as either `mechanical` (a compiled boolean predicate over typed dossier slots, evaluated deterministically in the Structural Gate — no actor, no judgment) or `semantic` (a panel question with mandatory span grounding, calibrated like any verdict). This is what stops disallowed_evidence patterns from smuggling back an ungoverned semantic tagging step: a pattern is either a predicate the compiler can evaluate, or it is an audited panel question — never a free label applied by one actor.
  - fields: rubric_id: string — required. claim_type: enum{causal,generalization,improvement,descriptive,scoping,existence,correlational,theoretical} — required. required_design_features: list[{id, role_predicate}] — required — each keyed by an anchored quantity/design ROLE, not a field name. mechanical_disqualifiers: list[{id, predicate}] — required, may be empty — predicate is a boolean expression over dossier slots the compiler evaluates deterministically. semantic_disqualifiers: list[{id, question, calibration_case_ids}] — required, may be empty — each is a panel question, tied to gold cases that measure its reproducibility. entailment_questions: list[{id, text, answer_enum:[yes,no,partial,not_assessable]}] — required, 3-6 closed. scope_questions: list[{id, text}] — required (the D3 sub-rubric). verdict_taxonomy: fixed enum list — required. scope_taxonomy: fixed enum list — required. composition_table_id: string — required — points to the precedence lattice that composes entailment×scope. min_judges: int — required. contested_threshold: float — required.
  - example: rubric_id: causal.v3
claim_type: causal
required_design_features:
  - {id: manipulation, role_predicate: "exists quantity or design_feature with role=manipulation and non-null source_anchor"}
  - {id: comparison_arm, role_predicate: "exists quantity with role in {control,ablation,counterfactual} and non-null source_anchor"}
mechanical_disqualifiers:
  - {id: single_arm_pre_post_no_control, predicate: "count(role in {control,ablation,counterfactual})==0 AND exists(role=pre_post_delta)"}
  - {id: no_anchored_effect, predicate: "count(cited_quantities with role=effect and non-null ci)==0"}
semantic_disqualifiers:
  - {id: observational_correlation_only, question: "Does the cited design ACTIVELY VARY the purported cause, or only observe co-variation? Quote the manipulation step or state none exists.", calibration_case_ids: [GOLD-CAUS-neg-07, GOLD-CAUS-neg-12]}
entailment_questions:
  - {id: q_dir, text: "Does the measured effect's DIRECTION match the claim's asserted direction?", answer_enum: [yes,no,partial,not_assessable]}
  - {id: q_confound, text: "Is at least one named alternative explanation explicitly ruled out or addressed in the cited spans?", answer_enum: [yes,no,partial,not_assessable]}
scope_questions:
  - {id: s_pop, text: "Is the claim's stated population EQUAL to (not a superset of) the experiment's tested population?"}
verdict_taxonomy: [entailed_strong, entailed_weak, partially_entailed, not_entailed, insufficient_evidence, not_applicable]
scope_taxonomy: [matches, overclaims, underclaims, not_assessable]
composition_table_id: COMPOSE.v2
min_judges: 3
contested_threshold: 0.66
- **ENTAILMENT_DOSSIER (assembled per edge, not authored)** (JSON, ephemeral (regenerated on demand, content-hashed), one per EDGE id) — The single structured input a judge ever sees. Deterministic join over CLAIMFOL + EDGES + QUANT — copy-by-reference, zero LLM prose at assembly. v2 change: design-feature presence is keyed by anchored ROLE and every 'present' MUST carry a non-null source_anchor, so an author cannot route a weak claim past the gate by stuffing a nominal `baseline: yes` — a role with no anchored quantity reads as absent. Also carries the canonical slot ordering used for the invariance audit's shuffle test.
  - fields: edge_id: string — required. claim_id: string — required. claim_type: enum — required (or not_specified). claim_statement: string — required, verbatim. claim_scope: object{population, conditions, qualifiers} — required, each may be not_specified (scored equal to a present value). experiment_id: string — required. design_features: object keyed by rubric role — each {role, status:[present,absent,not_specified], source_anchor|null} — required; status=present REQUIRES non-null source_anchor or the compiler rewrites it to absent and logs it. cited_quantities: list[{id, value, unit, ci, role, source_anchor}] — required, may be empty. rubric_id: string+version+hash — required. dossier_hash: sha256 of canonicalized content — required. slot_order_seed: int — required — records the canonical ordering so a shuffled re-serialization is provably meaning-equivalent.
  - example: {
  "edge_id": "EDGE-C01-E01",
  "claim_id": "C01",
  "claim_type": "improvement",
  "claim_statement": "p217_MS achieved the highest rank (P-score = 0.859); standard p181_IA ranked last (0.117).",
  "claim_scope": {"population": "pooled NMA cohorts, Abeta-positivity", "conditions": "not_specified", "qualifiers": "relative ranking, not absolute accuracy"},
  "experiment_id": "E01",
  "design_features": {
    "baseline_comparator": {"role": "baseline", "status": "present", "source_anchor": "QUANT:Q-C01-p181 @ evidence/tables/table2.md#Rank8"},
    "statistical_comparison": {"role": "effect", "status": "present", "source_anchor": "QUANT:Q-C01-MD.ci @ evidence/figures/figure3.md#3A"}
  },
  "cited_quantities": [
    {"id": "Q-C01-p217", "value": 0.859, "unit": "P-score[0,1]", "role": "result", "source_anchor": "evidence/tables/table2.md#Rank1"},
    {"id": "Q-C01-MD", "value": 0.10, "unit": "AUC-MD", "ci": "[0.04,0.16]", "role": "effect", "source_anchor": "evidence/figures/figure3.md#3A"}
  ],
  "rubric_id": "improvement.v3#sha256:1c4d",
  "dossier_hash": "sha256:9b7e",
  "slot_order_seed": 0
}
- **STRUCTURAL_GATE_RECORD (per-edge, deterministic + appealable)** (YAML, one record per edge, append-only, sits beside the verdict) — Makes the cheap pre-check a governed, auditable filter instead of an ungoverned deterministic killer upstream of everything. Records exactly which mechanical rule fired against which anchored slot, so a killed edge is never a silent naming-mismatch casualty, and exposes an appeal valve that forces contested disqualifications into the full panel. Its own accuracy is graded against an adversarial self-test suite.
  - fields: edge_id: string — required. gate_version: string+hash — required. outcome: enum{passed_to_panel, disqualified, force_panel_on_appeal} — required. fired_rules: list[{rule_id, rubric_id, matched_slot|null, predicate_result:bool, evaluated_expression}] — required — a disqualification lists exactly the mechanical_disqualifier(s) that evaluated true and the slots they read. disqualifying_verdict: enum|null — required-but-nullable — the taxonomy value assigned WITHOUT an LLM call (e.g. not_entailed). appeal_status: enum{none, appealed, overturned, upheld} — required — any disqualified edge may be flagged `appealed` (by author or a periodic auto-sample); appeal forces the FULL panel to adjudicate the same dossier; if the panel's effective_verdict differs from disqualifying_verdict the record is stamped `overturned` and the panel verdict wins. self_test_ref: string — required — points to the GATE_SELFTEST_REPORT version this gate passed.
  - example: edge_id: EDGE-C07-E03
gate_version: gate.v4#sha256:aa11
outcome: disqualified
fired_rules:
  - {rule_id: single_arm_pre_post_no_control, rubric_id: causal.v3, matched_slot: null, predicate_result: true, evaluated_expression: "count(role in {control,ablation,counterfactual})==0 -> true; exists(role=pre_post_delta) -> true"}
disqualifying_verdict: not_entailed
appeal_status: appealed        # author asserts an ablation exists but was mis-roled
self_test_ref: GATE_SELFTEST_REPORT.v4   # false_disqualify_rate=0.9%, false_pass_rate=1.4% on 240 adversarial cases
- **entailment_ledger.yaml (per-ARA verdict record)** (YAML/JSON, one file per ARA under verification/, append-only (new gate/panel version = new record, old retained with version tag)) — The auditable, append-only result: one record per EDGE carrying the full panel transcript, BOTH confidence signals kept separate then fused by a published formula, the deterministically-composed effective_verdict, and the trust stamp that lets downstream metrics discount revoked combos. Any reader can re-run the same dossier against a newer panel to test stability.
  - fields: edge_id, dossier_hash — required. entailment_verdict: enum from verdict_taxonomy — required. scope_verdict: enum from scope_taxonomy — required. effective_verdict: enum — required — DETERMINISTIC output of COMPOSE table over (entailment_verdict, scope_verdict); this is the ONLY field downstream metrics read. overclaim_span: {claim_clause, missing_condition}|null — required-but-nullable. for_spans / against_spans: list[{quote, locator, judge_id}] — required, each quote mechanically substring-validated against cited evidence; against_spans may be empty only when panel_agreement==1.0. required_elements_met: list[{feature_id, met:bool, evidence_span}] — required, one per rubric required_design_feature, each span deterministically validated (adopted from TREV). judge_panel: list[{judge_id, model, model_version, prompt_variant_id, prompt_hash, raw_verdict, raw_confidence(stored, NEVER scored)}] — required, length>=min_judges. panel_agreement: float[0,1] — required — max(verdict_tally)/n_valid, the EDGE-LEVEL signal (adopted from TREV). rubric_reliability: float[0,1] — required — the BUCKET-LEVEL calibrated accuracy of this rubric+panel version from CALIBRATION_REPORT. calibrated_confidence: float[0,1] — required — published fusion FUSE(panel_agreement, rubric_reliability); monotone in both and CAPPED by panel_agreement so a contested edge cannot inherit bucket accuracy. contested: bool — required — panel_agreement < contested_threshold; contested is a first-class terminal state, never force-tiebroken. trust_status: enum{trusted, revoked} — required — copied from CALIBRATION_REPORT for this rubric+panel version at read time; revoked verdicts are excluded/discounted by downstream metrics. invariance_audit_ref: string|null — required-but-nullable — points to the INVARIANCE_AUDIT record if this edge was in the audit sample.
  - example: edge_id: EDGE-C01-E01
dossier_hash: sha256:9b7e
entailment_verdict: entailed_strong
scope_verdict: overclaims          # claim says 'pooled cohorts', evidence is prodromal/MCI only
effective_verdict: partially_entailed   # COMPOSE.v2: overclaims CAPS entailed_strong -> partially_entailed
overclaim_span: {claim_clause: "pooled NMA cohorts", missing_condition: "restricted to prodromal/MCI stage"}
required_elements_met:
  - {feature_id: baseline_comparator, met: true, evidence_span: "p181_IA (0.117)"}
  - {feature_id: statistical_comparison, met: true, evidence_span: "0.10 [0.04; 0.16]"}
for_spans: [{quote: "p217_MS (0.859)", locator: "table2#Rank1", judge_id: A}]
against_spans: [{quote: "prodromal/MCI stage only", locator: "table1#inclusion", judge_id: C}]
judge_panel:
  - {judge_id: A, model: claude, model_version: opus-4.8, prompt_variant_id: PV-2, prompt_hash: sha256:9f2a, raw_verdict: entailed_strong, raw_confidence: 0.9}
  - {judge_id: B, model: gpt, model_version: 5.4, prompt_variant_id: PV-2, prompt_hash: sha256:9f2a, raw_verdict: entailed_strong, raw_confidence: 0.85}
  - {judge_id: C, model: gemini, model_version: 3, prompt_variant_id: PV-2, prompt_hash: sha256:9f2a, raw_verdict: entailed_weak, raw_confidence: 0.7}
panel_agreement: 0.67
rubric_reliability: 0.91
calibrated_confidence: 0.61        # FUSE=0.91*min(1,0.67/0.66)*0.90-cap -> capped well below 0.91
contested: false                   # 0.67 >= 0.66, just barely
trust_status: trusted
invariance_audit_ref: INV-2026Q3-batch4#EDGE-C01-E01
- **CALIBRATION_REPORT.yaml (trust-gating, revocation-carrying)** (YAML, ecosystem-shared, versioned, append-only) — Turns 'calibrated' from decorative into load-bearing. Periodically re-scores every rubric+panel version against a gold set containing deliberately-planted negative cases, publishes the false_entailed_rate, and HARD-GATES trust: any combo above the threshold has trust_status flipped to revoked, and every historical verdict stamped with that combo version is retroactively marked (append-only supersession). Provides rubric_reliability consumed by the fusion formula.
  - fields: report_id, generated_at — required. gold_set_id: string+hash — required — includes n_planted_negatives. per_combo: list[{rubric_id_version, panel_signature (ordered set of judge model_versions), n_cases, accuracy (=rubric_reliability), false_entailed_rate, false_not_entailed_rate, trust_status:[trusted,revoked], revoked_at|null}] — required. false_entailed_threshold: float — required — the published τ above which a combo is revoked. fusion_formula_id: string — required — names the published FUSE(panel_agreement, rubric_reliability) function version. revocation_action: string — required — 'all entailment_ledger verdicts whose (rubric_id_version, panel_signature) match a revoked combo are stamped trust_status=revoked and excluded from primary metrics; retained for audit.'
  - example: report_id: CAL-2026Q3
generated_at: 2026-07-01
gold_set_id: GOLD-entail-v5#sha256:d4 (n_planted_negatives: 88)
false_entailed_threshold: 0.05
fusion_formula_id: FUSE.v2   # FUSE = rubric_reliability * min(1, panel_agreement/contested_threshold), then *=0.9 if contested
per_combo:
  - {rubric_id_version: causal.v3, panel_signature: [claude-opus-4.8, gpt-5.4, gemini-3], n_cases: 210, accuracy: 0.91, false_entailed_rate: 0.03, false_not_entailed_rate: 0.06, trust_status: trusted, revoked_at: null}
  - {rubric_id_version: improvement.v2, panel_signature: [claude-opus-4.6, gpt-5.2, gemini-2], n_cases: 190, accuracy: 0.88, false_entailed_rate: 0.09, false_not_entailed_rate: 0.04, trust_status: revoked, revoked_at: 2026-07-01}  # 0.09 > 0.05 -> all its verdicts stamped revoked
revocation_action: "match on (rubric_id_version, panel_signature); stamp trust_status=revoked; exclude from primary metrics; retain for audit."
- **INVARIANCE_AUDIT.yaml (measures stability as invariance, not repetition)** (YAML, per audit batch (periodic, on a sampled subset of edges), append-only) — Replaces the determinism-theater re-run audit. Instead of re-running a pinned prompt (near-identical by construction), it perturbs semantically-INERT dimensions and gates on the verdict being INVARIANT across them, and separately measures provider nondeterminism at t=0 and cross-version drift against a pinned shadow panel. A verdict is 'stability-certified' only if it survives these perturbations.
  - fields: audit_id, sampled_edge_ids — required. perturbation_axes: list of the semantically-inert transforms applied — required — {paraphrase_variant (certified meaning-preserving prompt template from a versioned bank), quantity_row_shuffle (reorder cited_quantities/design_features slots), panel_order_permutation, within_tier_judge_swap}. per_edge: list[{edge_id, base_effective_verdict, verdicts_under_perturbation: map[axis->list[verdict]], invariance_rate: float (fraction of perturbation runs matching base bucket), t0_repeat_agreement: float (agreement across N repeated t=0 runs, catches provider nondeterminism), stability_certified: bool}] — required. shadow_panel_signature — required — the previous pinned judge versions re-run in parallel. drift_rate: float — required — fraction of sampled edges whose effective_verdict changed between current and shadow panel. invariance_threshold: float — required — min invariance_rate for stability_certified. paraphrase_bank_id: string+hash — required — the certified prompt-variant bank, itself validated meaning-preserving on the gold set.
  - example: audit_id: INV-2026Q3-batch4
perturbation_axes: [paraphrase_variant, quantity_row_shuffle, panel_order_permutation, within_tier_judge_swap]
invariance_threshold: 0.90
paraphrase_bank_id: PPB.v3#sha256:77
shadow_panel_signature: [claude-opus-4.6, gpt-5.2, gemini-2]
drift_rate: 0.04
per_edge:
  - edge_id: EDGE-C01-E01
    base_effective_verdict: partially_entailed
    verdicts_under_perturbation:
      paraphrase_variant: [partially_entailed, partially_entailed, partially_entailed]
      quantity_row_shuffle: [partially_entailed, partially_entailed]
      panel_order_permutation: [partially_entailed, partially_entailed]
      within_tier_judge_swap: [partially_entailed, entailed_weak]
    invariance_rate: 0.90
    t0_repeat_agreement: 1.0
    stability_certified: true

  _Protocols:_
  - **Deterministic Dossier Assembly** — Once per edge, before any LLM call. Whenever CLAIMFOL/EDGES/QUANT change, the dossier is regenerated and re-hashed.. 1. Resolve edge_id -> claim_id + experiment_id + cited quantity_ids via stable references. 2. Dispatch on claim_type to fetch the matched RUBRIC (id+version+hash). 3. For each rubric required_design_feature, look for an anchored quantity/design slot of the matching ROLE; write status=present ONLY if a non-null source_anchor exists, else absent (and log any nominal-but-unanchored field). 4. Copy claim_statement/scope and cited quantities verbatim by reference; never paraphrase. 5. Canonicalize and hash -> dossier_hash. 6. Emit candidate_evidence_files = exactly the anchored files; judges may quote ONLY these.
    - reliability/reproducibility: Fully deterministic: same source layers + same compiler version -> byte-identical dossier + hash. The role-and-anchor rule (not field-name matching) is the structural defense against rename-dodging and nominal field-stuffing.
    - constraints: Requires sibling layers to expose stable ids and typed quantity ROLES (baseline/control/effect/manipulation/...). Requires a canonical serialization spec so hashing is stable across compilers.
  - **Structural Gate with Appeal** — Immediately after assembly, before spending any LLM call.. 1. Evaluate every mechanical_disqualifier predicate over the dossier slots; record each firing with the exact slots read. 2. If any fires, outcome=disqualified with a taxonomy verdict assigned WITHOUT an LLM call; emit STRUCTURAL_GATE_RECORD. 3. Else outcome=passed_to_panel. 4. Any disqualified edge may be flagged appealed (by the author, or by a mandatory random auto-sample of disqualifications); appeal forces the full panel on the same dossier. 5. If the panel's effective_verdict differs from disqualifying_verdict, stamp overturned and the panel verdict wins. 6. Periodically grade the gate against GATE_SELFTEST_REPORT.
    - reliability/reproducibility: Deterministic given dossier + gate version. Governance closes the Goodhart hole: (a) the adversarial self-test suite of field-stuffing decoys and naming-variant valid claims yields published false_disqualify_rate / false_pass_rate; (b) the appeal valve prevents silent naming-mismatch kills; (c) overturn_rate is a monitored metric — a rising rate triggers gate-rule revision.
    - constraints: Ecosystem must maintain the gate self-test gold set and run it on every gate version bump; must fund the auto-sampled appeal audits so appeal is not author-only (which authors could selectively exploit).
  - **Adversarial Multi-Judge Panel** — For every edge that passes the gate or is force-paneled on appeal.. 1. Assemble panel of >=min_judges independent judges across DIFFERENT model families, each given rubric + dossier + a prompt_variant_id from the certified paraphrase bank. 2. Each judge runs a mandatory for/against dual pass, answers each closed entailment_question, tags each required_design_feature met/unmet with an evidence_span, answers semantic_disqualifiers with span grounding, and returns entailment_verdict + scope_verdict. 3. Mechanically validate every span as a substring of a candidate evidence file; discard ungrounded verdicts (recorded as n_rejected). 4. Tally valid verdicts; consensus = majority; panel_agreement = max_tally/n_valid. 5. If panel_agreement < contested_threshold, mark contested (terminal — never force-tiebreak). 6. Fetch rubric_reliability + trust_status from CALIBRATION_REPORT; compute calibrated_confidence = FUSE(panel_agreement, rubric_reliability).
    - reliability/reproducibility: Class C. Reproducibility is not asserted via t=0 pinning — it is measured by the Invariance Audit. Cross-model diversity + span-grounding + closed taxonomy minimize judge DoF. Confidence is empirical (fusion of edge agreement and gold accuracy), never self-reported.
    - constraints: Ecosystem must provide >=3 independent judge providers, the certified paraphrase bank, and the calibration/gold infrastructure. Span validator must be a deterministic substring/locator checker.
  - **Verdict Composition (entailment × scope → effective)** — After the panel produces entailment_verdict and scope_verdict for an edge.. 1. Look up COMPOSE table (versioned) keyed by (entailment_verdict, scope_verdict). 2. Apply capping: scope_verdict=overclaims caps entailment at partially_entailed (entailed_strong/weak -> partially_entailed); underclaims does not cap but is recorded; not_assessable scope leaves entailment unchanged but flags reduced confidence. 3. Emit effective_verdict as the single downstream-facing value; retain raw entailment_verdict and scope_verdict for audit.
    - reliability/reproducibility: Fully deterministic given the two inputs and the versioned table — resolves the critique's contradictory (entailed_strong, overclaims) pair by construction and prevents downstream double-counting.
    - constraints: COMPOSE table must be published and versioned; downstream metrics MUST read effective_verdict, not raw verdicts, or they will disagree.
  - **Invariance & Drift Audit** — Periodically, on a random + stratified sample of edges (and on demand for any contested or high-stakes edge).. 1. For each sampled edge, re-run the panel under each semantically-inert perturbation axis: paraphrase_variant, quantity_row_shuffle, panel_order_permutation, within_tier_judge_swap. 2. Compute invariance_rate = fraction of perturbed runs whose effective_verdict matches the base bucket. 3. Run N repeated t=0 runs to measure t0_repeat_agreement (catches provider nondeterminism the pinned re-run would hide). 4. Re-run the PREVIOUS pinned judge versions as a shadow panel; compute drift_rate. 5. stability_certified = invariance_rate >= invariance_threshold AND t0_repeat_agreement acceptable. 6. Emit INVARIANCE_AUDIT; edges failing certification are flagged for re-adjudication or downgraded confidence.
    - reliability/reproducibility: This IS the Class-C reproducibility mechanism, fixed from v1: it measures invariance under meaning-preserving change and cross-version drift, not near-identical repetition. The paraphrase bank is itself certified meaning-preserving on the gold set so its variants cannot smuggle in semantic change.
    - constraints: Ecosystem must maintain and validate the paraphrase bank, retain prior judge versions runnable as shadow panels, and fund the compute for perturbation sampling.
  - **Calibration & Trust Revocation** — On a fixed schedule and on every rubric or judge-model version bump.. 1. Re-score every rubric+panel combo against the gold set (with planted negatives). 2. Compute accuracy (=rubric_reliability), false_entailed_rate, false_not_entailed_rate. 3. If false_entailed_rate > published τ, flip trust_status=revoked for that combo. 4. Match every historical entailment_ledger verdict with that (rubric_id_version, panel_signature) and stamp trust_status=revoked (append-only supersession, never delete). 5. Publish CALIBRATION_REPORT; downstream primary metrics exclude/discount revoked verdicts.
    - reliability/reproducibility: Makes trust explicit and revocable (adopted from TREV and extended to retroactive marking). 'calibrated' now controls whether a verdict counts at all. Deterministic given the gold set and threshold.
    - constraints: Ecosystem must maintain a versioned, hard-to-overfit gold set with planted negatives, publish τ, and enforce that metric consumers honor trust_status.

  _Metrics afforded:_
  - Entailment quality score per ARA (fraction of edges with effective_verdict in {entailed_strong, entailed_weak}, weighted by calibrated_confidence, counting only trust_status=trusted verdicts) → Aggregate effective_verdict over entailment_ledger, weight by calibrated_confidence, exclude revoked combos and honest not_applicable/insufficient_evidence (scored neutral, not negative). [semantic-judged (per edge) aggregated deterministically]; anti-Goodhart: Padding claims cannot inflate it: each new claim is a new edge that must survive the gate AND a span-grounded panel; unsupported claims land in not_entailed and LOWER the fraction. Fabricated-but-consistent prose fails span validation. Nominal field-stuffing fails the role+anchor rule. not_applicable is scored equal, so honest absence creates no incentive to fabricate an edge.
  - Scope calibration / over-claim rate (fraction of edges with scope_verdict=overclaims) → Count scope_verdict=overclaims over trusted verdicts; effective_verdict already reflects the cap so it is not double-counted. [semantic-judged]; anti-Goodhart: An author cannot narrow prose to dodge overclaim without also shrinking the claim's asserted scope — which reduces its scientific reach. Underclaiming is recorded separately and NOT rewarded, so timid hedging does not game the metric. The compose-table cap prevents an author from banking entailed_strong while overclaiming.
  - Verdict stability / invariance rate → Mean invariance_rate across the INVARIANCE_AUDIT sample; drift_rate against the shadow panel. [reproducible (measured, not asserted)]; anti-Goodhart: Cannot be gamed by temperature=0 pinning because the audit perturbs meaning-preserving dimensions and gates on invariance; a design that looks stable only under identical re-runs scores LOW here. The paraphrase bank being certified meaning-preserving stops gaming via semantically-loaded 'paraphrases'.
  - Panel agreement vs calibrated confidence separation → Report panel_agreement (edge-level) and rubric_reliability (bucket-level) separately, and calibrated_confidence = FUSE(...) capped by agreement. [reproducible]; anti-Goodhart: Prevents the category error of labeling a 2-1 edge with the bucket's average accuracy: the cap makes it structurally impossible for a contested edge to display high confidence, so authors cannot harvest bucket reliability to mask genuine dissent.
  - Gate governance health (false_disqualify_rate, false_pass_rate, appeal overturn_rate) → From GATE_SELFTEST_REPORT against the adversarial self-test suite, plus overturn_rate from STRUCTURAL_GATE_RECORDs. [deterministic (gate) / semantic-judged (overturn adjudication)]; anti-Goodhart: Turns the pre-check from an ungoverned filter into a measured, appealable component. If authors learn the gate and route weak claims past it, false_pass_rate rises on the self-test and triggers rule revision; if the gate over-kills valid claims, overturn_rate rises and triggers revision. The gate reads anchored roles, so stuffing nominal fields does not fool it.
  - Trust coverage (fraction of the corpus adjudicated by non-revoked rubric+panel combos) → Share of edges whose (rubric_id_version, panel_signature) has trust_status=trusted in the latest CALIBRATION_REPORT. [deterministic]; anti-Goodhart: A judge/rubric combo that passes weak evidence (high false_entailed_rate) is revoked and its verdicts stop counting, so gaming a specific lenient combo is self-defeating: the funder sees the coverage drop and the revoked verdicts are excluded from primary metrics.

  _Tradeoffs:_ Cost: the invariance audit multiplies LLM spend (perturbation axes x repeated t=0 runs x shadow panel) — mitigated by sampling rather than auditing every edge, reserving full audits for contested/high-stakes edges. Fabrication surface — the paraphrase bank: a 'meaning-preserving' variant could smuggle a leading question; mitigated by certifying every bank version on the gold set (variants must not shift gold verdicts) and content-hashing the bank into each verdict. Fabrication surface — the gold set: whoever controls planted negatives controls trust; mitigated by versioning, hashing, and keeping the gold set adversarially refreshed so combos cannot overfit it. Residual gaming — appeal abuse: authors could appeal every disqualification to burn reviewer compute or fish for a lenient panel; mitigated by making appeal deterministic (same dossier, same panel policy) and monitoring overturn_rate so frivolous appeals simply confirm the gate. Complexity: six data structures plus a compose table is heavier than TREV; mitigated because all machine-only artifacts (dossier, gate record, invariance audit) render to prose and scientists read effective_verdict + for/against spans, not the plumbing. Honest limit: cross-version drift can never be zero — a judge-model bump can legitimately change a borderline verdict; we surface drift_rate rather than hide it, and revocation forces re-adjudication when drift correlates with rising false_entailed_rate.

  _Open questions:_ 1. How large and how adversarially-refreshed must the gold set be before rubric_reliability is trustworthy per (rubric x panel) cell, given combinatorial explosion of judge-version tuples? 2. The exact FUSE function shape — product vs min vs a learned monotone calibration — needs empirical validation against real over/under-confidence, and may itself need periodic recalibration. 3. Certifying a paraphrase as truly meaning-preserving is itself a semantic judgment; we push it to the gold set, but a residual bootstrap problem remains. 4. When a rubric+panel combo is revoked, is re-adjudication under a NEW combo fair to already-published ARAs, or does it retroactively penalize authors for infrastructure drift they did not cause? A grace/grandfathering policy is unspecified. 5. Who arbitrates a gate-rule revision when overturn_rate rises — a standing ecosystem body is assumed but its governance is out of scope here. 6. Semantic_disqualifiers still carry irreducible judge DoF; we calibrate them, but the boundary between 'compile to a mechanical predicate' and 'must stay a panel question' will be contested per claim_type.

  _Changes from critique:_ Addressed all six critique points: (1) Replaced the determinism-theater stability re-run with an INVARIANCE_AUDIT that perturbs semantically-inert dimensions (certified paraphrase variants, quantity-row shuffle, panel-order permutation, within-tier judge swap), adds repeated t=0 runs to catch provider nondeterminism, and a pinned shadow panel to measure cross-version drift; certification gates on invariance, not repetition. (2) Fixed the confidence category error: entailment_ledger now carries panel_agreement (edge-level, from the panel) AND rubric_reliability (bucket-level, from calibration) as SEPARATE fields, fused by a published FUSE formula that is CAPPED by panel_agreement so a contested edge can never inherit bucket accuracy; contested is first-class and terminal. (3) Governed the pre-check as a STRUCTURAL_GATE_RECORD: matches on anchored quantity ROLE not field name (defeats stuffing/renaming), emits a per-rule audit record, is graded against an adversarial self-test suite with published false_disqualify/false_pass rates, and every disqualification has an appeal valve that forces the full panel and can be overturned. (4) Split disallowed_evidence into mechanical_disqualifiers (compiled boolean predicates over typed slots, evaluated deterministically in the gate — no actor) and semantic_disqualifiers (calibrated, span-grounded panel questions) — no ungoverned single-actor tagging survives. (5) Defined a versioned COMPOSE precedence table producing a single deterministic effective_verdict (overclaims caps entailment at partially_entailed); downstream metrics read effective_verdict only. (6) Made trust explicit and revocable: CALIBRATION_REPORT publishes false_entailed_threshold τ, flips trust_status=revoked on any combo exceeding it, and retroactively stamps every historical verdict from that combo (append-only) so primary metrics exclude it.

  _Adopted from competitor:_ Adopted TREV's per-edge agreement_rate as the confidence signal — but instead of letting it fully replace bucket accuracy, I keep BOTH and fuse them with an explicit capped formula, resolving my own category error while keeping TREV's edge-level fidelity. Adopted TREV's required_elements_met with per-requirement deterministically-validated evidence spans. Adopted TREV's first-class contested state that is never resolved by forced tie-breaking. Adopted TREV's calibration set with deliberately-planted negative cases and its false_entailed gating of trust — and extended it to RETROACTIVE revocation of already-published verdicts. Adopted TREV's completeness_flag/anchored-quantity discipline via the role+source_anchor rule in the dossier.

  _Why it wins:_ TREV makes the judge's inputs deterministic and gates trust, but it asserts run-to-run stability rather than measuring it — it has no invariance audit, so it is vulnerable to exactly the determinism-theater the reviewer flagged; my INVARIANCE_AUDIT measures stability under meaning-preserving perturbation and cross-version drift, which is the true Class-C requirement. TREV spends an LLM call on every edge; my governed Structural Gate disposes of mechanically-obvious failures for free while closing the Goodhart hole the reviewer feared, via role-based matching, a self-test suite, and an appeal valve TREV has no analog for. TREV leaves entailment and scope as parallel outputs with no composition rule (the same contradictory-pair risk); I define a deterministic COMPOSE table producing one effective_verdict so downstream metrics cannot double-count. TREV keeps disqualifying_conditions as free strings that still require someone to judge whether they apply; I split them into compiled mechanical predicates and calibrated span-grounded semantic questions, genuinely eliminating the ungoverned tagging step. And by keeping BOTH panel_agreement and rubric_reliability with an explicit capped fusion, I deliver honest per-edge confidence that TREV's pure agreement_rate lacks (no bucket-accuracy signal) and that my own v1 got wrong (bucket-only).


---


## VALIDITY — Assumption realism / method validity

_Class C — irreducibly semantic (reproducibility + auditability)_


**Judge rationale:** All four converge on the same correct architecture — a typed sidecar ledger (assumptions/limitations/methods/perspectives) that renders back into constraints.md, with reference-prior anchors, typed assumption→consequence→failure-mode chains, applicability conditions, stress probes, and a calibrated panel with honest-null symmetry. So the ranking turns on which designs (a) close specific Goodhart holes with concrete mechanisms and (b) actually deliver the Class-C mandate of a reproducible, auditable VERDICT rather than just a nice evidence packet feeding an unspecified judge.

#3 wins on the primary criterion (affords the metric AND is hardest to game). Its blind counterfactual reconstruction is the single best anti-gaming device in the field: it stops the paper's own narrative from anchoring the judge, which is the exact failure mode of "read the chain and grade if it feels real." Its reference_class carries an actual base rate (prevalence_in_corpus) and citations resolve into a normalized refs table (no bare-string fabrication), and its null-handling is nuanced. Its weaknesses are real (the registry and the blind protocol are underspecified, aggregation unstated), but they are fixable additions, not architectural flaws.

#2 wins the second slot on concrete-beats-vague. Its deterministic set-difference for limitation novelty is the only genuine determinism gain across all four (directly operationalizing M31), and its severity-weighted floor + median/dispersion is the only explicit anti-dilution mechanism — plugging the "bury one fabricated load-bearing assumption under a pile of trivially-true ones" hole that #0, #1, and #3 all leave open. It edges #1 because those two mechanisms add capability the field otherwise lacks, and the rubric weights gaming-resistance and specificity first.

#1 ranks a close third: it has the best pure reproducibility infrastructure (validity_panel_run with rubric_version, calibration_set_id, inputs_frozen_hashes, judge_distribution, for/against evidence; grounding protocols with registry snapshots and query hashes). It is the most complete auditable verdict record and the most literal fit to "reproducible rather than a vibe." It loses the slot only because its distinctive value overlaps #3's calibration story, its schema is communicated as dense prose blobs (harder to validate/implement), and it never states the aggregation/anti-dilution rule — leaving the Goodhart hole #2 explicitly closes. Both winners should steal #1's frozen-hash + snapshot discipline; it is the missing reproducibility half of their registries.

#0 ranks fourth despite arguably the best-crafted schemas. Its manifest with genre-conditioned expected_validity_surfaces is a genuine anti-omission mechanism the others lack (you must declare which validity surfaces apply, symmetric honest-absence), and its method_cards (known_invalid_conditions, overgeneralization_risks) and stress_probes (expected_failure_signature declared before judging) are excellent. But the panel/calibration protocol — the Class-C crux, i.e. how the fixed evidence packet becomes a reproducible calibrated verdict — is the part that is truncated/unspecified. An outstanding evidence packet feeding an unproven resolver does not clear the bar it sets for itself, and it is also the heaviest to implement. Note: all four proposals were truncated, so I judged on visible mechanism plus reasonable inference, and I penalized truncation only where it hit the class-defining crux (the resolver), which cost #0 and #2 differently — #2 at least states its aggregation philosophy (severity floor, median/dispersion, calibration interleaving) in the summary, whereas #0's resolver is simply absent.


### Finalist A (judge-selected proposal; refine round cut off)

**Realism & Validity Dossier**  ·  _source: gpt-5.5-codex_

Add a typed, human-renderable validity dossier beside logic/solution/constraints.md, not instead of it. The core move is to make every assumption, limitation, method choice, and perspective claim a structured object linked to claims, experiments, quantities, refs, datasets, and methods. Realism/validity remains Class C, but judges no longer free-form vibe-check prose: they score against declared domain priors, stress probes, applicability conditions, failure modes, and calibrated judge rubrics. Honest not_specified / not_applicable values are first-class and are scored as honest absence, while unsupported positive assertions are penalized.

- **validity_dossier.yaml** (YAML with typed records, rendered into readable constraints.md (round-trippable prose view).) — Canonical sidecar for assumptions, limitations, method validity, and perspective adequacy; the structured layer that renders back into a readable constraints.md.
  - fields: assumptions : list[AssumptionRecord] (required, may be empty with absence_reason); limitations : list[LimitationRecord] (required); methods : list[MethodValidityRecord] (required for every method file); perspectives : list[PerspectiveRecord] (required when claims combine data/modalities/disciplinary lenses); rendered_to : file_ref (required, points to prose view). Common field pattern: every field carries provenance {status: specified|not_specified|not_applicable, value, source_anchor:{ref_id, locator, quote_id}}. AssumptionRecord: id:stable_id; statement:text; kind (e.g. measurement_validity); used_by:{claims,experiments,methods}; provenance:{status,source_anchor}; applicability_conditions:list[{condition,source_anchor}]; consequences:list[{id,if_false,affects:[claim_id],severity}]; failure_modes:list[{id,mode,observable_probe:probe_id}]; sensitivity:{status,value,rationale}; fairness:{affected_groups:[{entity_id}],concern,evidence_status}. LimitationRecord: id:stable_id (required); statement:text (required); type: scope|measurement|confounding|sampling|statistical_power|external_validity|implementation|ethics|other; adds_condition_to:list[claim_id|assumption_id|method_id] (required); not_duplicate_of_assumption: boolean+rationale (required); exclusion_boundary: structured condition (required or honest null); residual_risk: low|medium|high|not_specified; source_anchor (required unless compiler-inferred, then marked result). MethodValidityRecord: id:method_id (required); method_ref:file_ref (required); method_family:ontology_id|string (required); verification_status: standard|accepted_variant|novel_validated|novel_unvalidated|deprecated|not_specified; validity_claims:list[text+anchors]; required_assumptions:list[assumption_id]; known_failure_modes:list[failure_mode_id]; verification_evidence:list[ref_id|experiment_id|external_standard_id]; overgeneralization_risks:list[{claim_id,condition}]. PerspectiveRecord: linked to claims, methods, datasets, limitations; must carry distinct measured quantities, failure modes, and affected claims.
  - example: assumptions: A001 statement 'Amyloid PET status is an adequate reference standard for Abeta positivity' kind measurement_validity used_by {claims:[C01,C03],experiments:[E01],methods:[METH_NMA01]} provenance {status:specified, source_anchor:{ref_id:R001,locator:Methods,quote_id:Q014}} applicability_conditions [{condition:'Cohorts use clinically accepted amyloid PET thresholds', source_anchor:{ref_id:R022,locator:Table1,quote_id:Q143}}] consequences [{id:AC001, if_false:'Ranking estimates may reflect reference-standard disagreement rather than biomarker accuracy', affects:[C01,C03], severity:high}] failure_modes [{id:FM001, mode:'Differential verification bias across cohorts', observable_probe:SP001}] sensitivity {status:specified,value:high,rationale:'Primary outcome depends directly on reference-label assignment'} fairness {affected_groups:[{entity_id:POP_older_adults},{entity_id:POP_underrepresented_ancestry}], concern:'Threshold transportability may differ across ancestry and age strata', evidence_status:not_specified}. limitations: L002 statement 'Sparse head-to-head comparisons limit certainty for lower-ranked biomarkers' type statistical_power adds_condition_to [C01,METH_NMA01] not_duplicate_of_assumption {value:true, rationale:'Adds a network-connectivity condition, not merely restating assay validity'} exclusion_boundary {status:specified, value:'Do not interpret ranks below third place as stable without direct-comparison evidence'} residual_risk high source_anchor {ref_id:R001,locator:Discussion,quote_id:Q229}. methods: METH_NMA01 method_ref logic/solution/study_design.md method_family diagnostic_test_accuracy_network_meta_analysis verification_status accepted_variant verification_evidence [R031,R044,E01] required_assumptions [A001,A004,A006] known_failure_modes [FM001,FM004] overgeneralization_risks [{claim:C01, risk:'Ranking may be overread as individual-patient diagnostic superiority'}]
- **domain_priors.yaml** (YAML / JSON-LD.) — Make realistic mean consistent with declared baselines, not judge intuition; anchors realism judgements to reference priors / domain baselines.
  - fields: prior_id; domain_scope; population_scope; quantity_or_condition; baseline_distribution:{status,value}; source_refs:list[ref_id]; resolver_status; applicability_notes; conflict_notes
  - example: priors: P_ABETA_PET_VALIDITY domain_scope 'Alzheimer disease diagnostic biomarkers' quantity_or_condition 'amyloid PET as reference standard' baseline_distribution {status:specified, value:{accepted_use:true, known_disagreement_sources:[tracer,threshold,disease_stage]}} source_refs [R022,R031] applicability_notes 'Appropriate as comparator, not an error-free ground truth'
- **stress_probes.yaml** (YAML linked to assumptions, claims, methods, quantities.) — Record counterfactual and sensitivity probes that test assumption realism and method validity, with expected breakpoints declared before judging.
  - fields: id; targets:{assumptions,claims,method}; probe_type (e.g. label_noise_sensitivity); perturbation; expected_breakpoint; run_status: run|not_run; result_quantities; interpretation; source_anchor; absence_reason (when not_run)
  - example: stress_probes: SP001 targets {assumptions:[A001],claims:[C01],method:METH_NMA01} probe_type label_noise_sensitivity perturbation 'Recompute rankings after 5%, 10%, 15% reference-label discordance' expected_breakpoint 'C01 becomes unstable if p217_MS rank drops below first or CI overlaps p181_IA' run_status not_run absence_reason 'No individual-level data released'
- **validity_panel_run.yaml** (Append-only YAML / JSON.) — Reproducible Class C judgement record; the audit trail of an expert/LLM panel scoring realism/validity against frozen inputs and a versioned rubric.
  - fields: panel_id; rubric_version; calibration_set_id; judge_specs; inputs_frozen_hashes; item_scores:list[{target,metric,score,confidence,for_evidence,against_evidence,judge_distribution}]; for_evidence; against_evidence; confidence; disagreement; adjudication
  - example: item_scores: target A001 metric M30_assumption_realism score 0.72 confidence medium for_evidence [P_ABETA_PET_VALIDITY,AC001] against_evidence ['reference standard not error-free','no ancestry-stratified validation'] judge_distribution [0.70,0.75,0.68,0.76]

  _Protocols:_
  - **Constraint Extraction Protocol** — Every compiled artifact.. Extract prose assumptions/limitations; assign stable IDs; link each to claims/experiments/methods; mark every missing field as not_specified or not_applicable; render back to constraints.md.
    - reliability/reproducibility: Deterministic schema validation plus prose/sidecar consistency checks (round-trip validation).
    - constraints: Tooling must reject orphan assumptions and unsupported filled fields.
  - **Prior & Baseline Grounding Protocol** — Any M30/M31/M32/M35 scoring run.. Resolve domain, population, method family; retrieve accepted standards, empirical baseline ranges, known failure modes; attach priors with source anchors; record unresolved searches.
    - reliability/reproducibility: Registry snapshots and search query hashes are required. A missing prior is honest absence, not a zero; a fabricated or unresolved prior is a defect.
    - constraints: Ecosystem must provide resolvable domain-prior / accepted-standard registries plus snapshotting so lookups are reproducible.
  - **Stress Probe Protocol** — High-sensitivity assumptions, novel methods, broad claims, or fairness-relevant populations.. Identify plausible perturbations; declare expected breakpoints before judging; run if data/code permit; otherwise record why not; link results to claims and limitations.
    - reliability/reproducibility: Probes are scored for relevance and preregistered structure, not for always being executable; declaring the probe plus expected breakpoint counts even when run_status is not_run with an absence_reason.
    - constraints: Ecosystem must make code/data available where possible so probes can be executed; probe types and expected-breakpoint declarations must be recorded before the panel scores.
  - **Calibrated Validity Panel Protocol** — Final Class C scores.. Freeze inputs; run expert/LLM judge ensemble against rubric; include calibration examples; require for/against evidence; compute median, dispersion, and confidence; adjudicate high-disagreement cases.
    - reliability/reproducibility: Frozen input hashes, versioned rubric, calibration set, judge ensemble with median + dispersion + confidence, and explicit for/against evidence make the judgement repeatable, inspectable, and contestable rather than a single-shot vibe.
    - constraints: Ecosystem must provide calibration sets by field, judge versioning, blinded scoring where possible, and audit logs.

  _Metrics afforded:_
  - S7 / M30 Assumption realism & fairness → From assumption links, priors, applicability conditions, failure modes, sensitivity, fairness groups, and panel judgement. [reproducible (semantic-judged)]; anti-Goodhart: Exploit: invent many realistic-sounding assumptions. Defense: each assumption must be used_by claims/methods, source-anchored, prior-grounded or honestly absent, and penalized if redundant.
  - M31 Limitation validity → From whether each limitation adds a new condition to claims/methods and is not just a restated assumption (deterministic linkage checks over adds_condition_to + not_duplicate_of_assumption, plus semantic scoring). [reproducible (semantic-judged with deterministic linkage checks)]; anti-Goodhart: Exploit: boilerplate more-studies-needed. Defense: limitation must specify an exclusion_boundary, affected claim, residual_risk, and a non-duplication rationale.
  - S8 / M32 Method validity → From method_family, verification_status, required_assumptions, known_failure_modes, verification_evidence, and stress probes. [reproducible (semantic-judged)]; anti-Goodhart: Exploit: label a method standard. Defense: status requires external standard refs or calibration-panel agreement; unsupported status becomes not_specified.
  - M35 Method verification status → From accepted-standard registry, prior uses, validation experiments, and unresolved/deprecated flags. [reliable-anchored (plus semantic adjudication for edge cases)]; anti-Goodhart: Exploit: cite irrelevant validation papers. Defense: refs must match method family, data regime, and claimed scope.
  - M36 Multi-perspective adequacy reflected in constraints → From perspective records linked to claims, methods, datasets, and limitations; checks whether each perspective contributes distinct evidence and has its own constraints. [reproducible (semantic-judged)]; anti-Goodhart: Exploit: tag superficial wet-lab + computational lenses. Defense: each perspective must carry distinct measured quantities, failure modes, and affected claims.

  _Tradeoffs:_ This adds authoring burden and a new consistency surface between prose and sidecar. The mitigation is rendering the prose from the typed layer where possible and validating round-trips. The largest fabrication surface is fake priors or fake verification status; this is mitigated by resolver snapshots, source anchors, and treating honest absence as non-punitive. The design will not make realism deterministic; it makes the judgement repeatable, inspectable, and contestable.

  _Open questions:_ Who maintains field-specific calibration sets? How often should priors expire or be refreshed? What minimum judge ensemble is acceptable for high-stakes funding decisions? How should minority expert disagreement be preserved when median panel scores look stable?


### Finalist B (judge-selected proposal; refine round cut off)

**The Realism Ledger — Typed Assumption→Consequence Graph + Calibrated Validity Panel (AMVP)**  ·  _source: Claude Sonnet 5 (claude-sonnet-5)_

Replace the vibe-check "is this realistic?" with a two-layer design: (1) a typed sidecar ledger — assumptions.yaml, limitations.yaml, method_verification.yaml, perspectives.yaml — that forces every assumption/method/limitation into a structured assumption→consequence→failure-mode→applicability-condition shape with an explicit reference-prior anchor slot and a severity/tested-in-paper flag, all with honest-null symmetry; and (2) a Calibrated Validity Panel Protocol (AMVP) that turns each ledger entry into an identically-templated counterfactual stress-probe, runs it through a diverse judge ensemble interleaved with a versioned expert-labeled calibration set, and aggregates via median+dispersion rather than mean, with a severity-weighted floor so one untested, high-severity, unrealistic assumption cannot be diluted by volume. This closes the gap by making the *inputs* to the realism judgement (what would break, how sensitive, is there field precedent, was it tested) deterministic and auditable, while keeping the *verdict itself* honestly Class C — reproducible and auditable rather than fabricated-deterministic. It directly operationalizes round-1 07's best signal (assumption→consequence traceability) by extending it with severity, sensitivity, reference-prior, and testedness, which is exactly what's needed to separate "concrete" from "realistic".

- **assumptions.yaml** (YAML, one file per ARA at logic/solution/assumptions.yaml, referenced by the prose constraints.md via matching A## ids (prose stays the human-readable rendering; this is the joinable layer)) — Typed sidecar to logic/solution/constraints.md's prose 'Assumptions' section. Captures each assumption as a structured object with its failure mode, severity, sensitivity, applicability scope, and — critically — a reference-prior anchor slot so 'is this standard in the field or a dreamcase idealization' has somewhere to attach an external citation instead of living only in a judge's head.
  - fields: id: string A## — required. statement: string — required, mirrors prose. stated_by: enum{explicit,inferred} — required. type: enum{idealization|independence|distributional|measurement_precision|generalization_scope|resource_availability|causal_identification|structural_simplification|population_representativeness|not_specified} — required. necessity: enum{load_bearing|convenience|robustness_check_only|not_specified} — required. consequence_if_false: object{failure_mode: string|not_specified, affected_claims: list[C##]|[], severity: enum{invalidates_main_claim|narrows_scope|negligible|not_specified}} — required, all sub-fields nullable. sensitivity: object{level: enum{low|medium|high|not_specified}, quantitative_check: string|not_specified (e.g. a reported delta from an actual sensitivity analysis, with source_anchor)} — required. applicability_conditions: list[object{condition: string, scope: enum{population|setting|time|measurement|not_specified}, source_anchor}] — may be empty list (honest, not penalized). reference_prior: object{domain_baseline_ref: ref-id into external Domain Baseline Registry | not_specified, alignment: enum{matches_known_standard|deviates_from_standard|contested_in_field|untested|not_specified}, note: string} — required, not_specified scored equal to a resolved anchor when genuinely no baseline exists for this niche. tested_in_paper: enum{yes_sensitivity_analysis|yes_ablation|no|not_applicable} — required. source_anchor: object{file, locator, quote} — required per Rule-16 grounding discipline.
  - example: assumptions:
  - id: A02
    statement: "Selecting the single most comprehensive dataset per cohort yields statistically independent nodes (no patient double-counted)."
    stated_by: explicit
    type: independence
    necessity: load_bearing
    consequence_if_false:
      failure_mode: "Correlated/duplicated patients across cohorts inflate apparent evidence, biasing P-scores upward for over-represented nodes."
      affected_claims: [C01, C02, C05]
      severity: invalidates_main_claim
    sensitivity:
      level: not_specified
      quantitative_check: not_specified
    applicability_conditions:
      - condition: "Requires accurate cohort-overlap screening at study-selection stage"
        scope: population
        source_anchor: {file: "logic/solution/study_design.md", locator: "§Cohort de-overlap", quote: "cohorts screened for overlapping patient IDs"}
    reference_prior:
      domain_baseline_ref: "baseline:nma-cohort-independence-v2"
      alignment: matches_known_standard
      note: "Cohort de-duplication by patient ID is the PRISMA-DTA/Cochrane NMA standard control for this failure mode."
    tested_in_paper: no
    source_anchor: {file: "logic/solution/study_design.md", locator: "§3.2", quote: "the most comprehensive dataset available for a given cohort was selected to avoid double-counting"}
- **limitations.yaml** (YAML, logic/solution/limitations.yaml) — Typed sidecar to constraints.md's 'Known limitations' section. Its job is to make M31's core question deterministic-where-possible: does this limitation add a genuinely new boundary condition, or is it a restatement of an assumption/scope already declared elsewhere?
  - fields: id: string L## — required. statement: string — required. relates_to_assumptions: list[A##] — required, may be empty. new_condition_added: bool — required; computed by a deterministic set-difference between this limitation's scope_narrowing and the union of all applicability_conditions already declared across assumptions.yaml (true only if this limitation narrows scope along an axis/population not already covered). scope_narrowing: object{axis: string, population_or_setting: string} — required, not_specified allowed. source_anchor: object{file, locator, quote} — required.
  - example: limitations:
  - id: L01
    statement: "Although platforms were statistically adjusted for, residual batch effects in manual immunoassays may still exist."
    relates_to_assumptions: [A02]
    new_condition_added: true
    scope_narrowing:
      axis: measurement_platform
      population_or_setting: "manual (non-automated) immunoassay results"
    source_anchor: {file: "logic/solution/constraints.md", locator: "§Known limitations (§4.5)", quote: "batch effects in manual immunoassays may still exist"}
- **method_verification.yaml** (YAML, logic/solution/method_verification.yaml) — Typed sidecar attached to whichever method file(s) exist (study_design.md, method.md, algorithm.md, ...). Records the method's provenance/verification status as a claim that must itself be anchored — 'widely accepted' is only a credit if it resolves to a real citation, not an assertion.
  - fields: id: string MV## — required. method_ref: string — pointer to the method-file section this describes — required. status: enum{widely_accepted_in_field|established_but_adapted|novel_untested|borrowed_from_adjacent_field|not_specified} — required. justification: string — required, prose rationale. verification_evidence: list[object{type: enum{prior_validation_citation|internal_sensitivity_check|benchmark_comparison}, ref: ref-id (refs.yaml) or {file, locator}}] — required, may be empty (honest gap, capped score not penalty). applicability_match: object{claim: string, source_anchor} — required; states explicitly why the method's known validity domain covers this paper's use case (not merely that the method exists). novelty: enum{established_use|novel_application|untested_adaptation|not_specified} — required.
  - example: methods:
  - id: MV01
    method_ref: "logic/solution/study_design.md#network-meta-analysis"
    status: widely_accepted_in_field
    justification: "Frequentist NMA via netmeta is the standard tool for simultaneous multi-comparator diagnostic-accuracy synthesis in this subfield (PRISMA-DTA compliant)."
    verification_evidence:
      - {type: prior_validation_citation, ref: "refs:rucker2015netmeta"}
      - {type: internal_sensitivity_check, ref: {file: "evidence/tables/table2.md", locator: "sensitivity excl. high-risk-of-bias studies"}}
    applicability_match:
      claim: "Network confirmed connected/transitive across all four outcomes, satisfying NMA's core identification requirement."
      source_anchor: {file: "logic/solution/study_design.md", locator: "§3.4", quote: "network geometry confirmed connected across all four outcomes"}
    novelty: established_use
- **perspectives.yaml** (YAML, logic/solution/perspectives.yaml) — Makes 'multi-perspective adequacy' checkable rather than inferred: declares which distinct epistemic lenses (wet-lab, computational, statistical, clinical, theoretical) the work actually draws on, each anchored to a real method/experiment section — not a self-declared label.
  - fields: tag: enum{wet_lab|computational|statistical_synthesis|clinical_diagnostic|theoretical|field_specific:<name>} — required. anchored_in: list[file#section] — required, must resolve to a real method or experiment file section (structural cross-check against experiments.md Setup fields or solution/ file headings); a tag with no resolvable anchor is dropped, not scored.
  - example: perspectives:
  - tag: statistical_synthesis
    anchored_in: ["logic/solution/study_design.md#nma-model"]
  - tag: clinical_diagnostic
    anchored_in: ["logic/problem.md#O2"]
# single-perspective paper: one tag present is correct and undiscounted unless problem.md's
# Observations reference a second lens the authors had access to but chose not to use.
- **validity_panel_report.yaml** (YAML, stored outside the compiler's write surface, e.g. trace/validity_panel/{run_id}.yaml, referenced by protocol_version + calibration_set_version) — The PRODUCED (not input) artifact from running the AMVP protocol — the auditable record of the panel's judgement, distinct from the compiler-authored ledgers above per the provenance-first principle (this is a result, always versioned and re-runnable, never hand-edited).
  - fields: protocol_version: string — required. run_id: string (timestamped) — required. calibration_set_version: string — required, pins which expert-labeled calibration exemplars were used this run. judges: list[object{judge_id, calibration_accuracy: float[0,1], included_in_aggregate: bool}] — required; judges below a published inclusion threshold (e.g. 0.7) are excluded and this is visible, not hidden. per_assumption: list[object{assumption_id, stress_probe_answers: list[object{judge_id, for: string, against: string, realism_verdict: enum{dreamcase_idealized|contested_in_field|standard_in_field|not_evaluable}, confidence: float}], aggregate: object{median_verdict, verdict_dispersion: float, flag_for_human_review: bool}}] — required. arc_level_summary: object{assumption_realism_score: float, high_risk_untested_assumptions: list[A##], limitation_validity_score: float, method_validity_score: float} — required, severity-weighted not averaged.
  - example: protocol_version: "AMVP-1.0"
run_id: "2026-07-06T00:00:00Z_che26_run1"
calibration_set_version: "baseline-calib-v3"
judges:
  - {judge_id: llm_A_temp0.2, calibration_accuracy: 0.92, included_in_aggregate: true}
  - {judge_id: llm_B_temp0.7, calibration_accuracy: 0.78, included_in_aggregate: true}
  - {judge_id: llm_C_alt_prompt, calibration_accuracy: 0.55, included_in_aggregate: false}
per_assumption:
  - assumption_id: A02
    stress_probe_answers:
      - judge_id: llm_A_temp0.2
        for: "Matches PRISMA-DTA cohort-independence standard; de-overlap step explicitly documented."
        against: "De-overlap relied on registry cross-matching, which can miss undocumented cohort mergers."
        realism_verdict: standard_in_field
        confidence: 0.8
    aggregate: {median_verdict: standard_in_field, verdict_dispersion: 0.05, flag_for_human_review: false}
arc_level_summary:
  assumption_realism_score: 0.81
  high_risk_untested_assumptions: []
  limitation_validity_score: 0.74
  method_validity_score: 0.88

  _Protocols:_
  - **Ledger Extraction & Structural Completeness Check** — At compile time, for every ARA — this is the deterministic floor everything else builds on.. 1. Compiler populates assumptions.yaml / limitations.yaml / method_verification.yaml / perspectives.yaml alongside the existing prose files, one entry per prose assumption/limitation/method. 2. A validator (pure code, no LLM) checks: every required field present or explicitly `not_specified`/`none`/empty-list (never missing entirely); every foreign key resolves (`affected_claims` ⊆ real C## ids in claims.md, `relates_to_assumptions` ⊆ real A## ids, `method_ref`/`anchored_in` resolve to real file sections); every `source_anchor` quote is present at the cited locator (reusing L1 §10's citation-verification machinery, extended to this sidecar). 3. Cross-check prose ⇄ ledger agreement (same A##/L## ids appear in both, statement text is materially consistent) as a cheap anti-fabrication signal.
    - reliability/reproducibility: Fully deterministic — pass/fail, no judge involved, perfectly reproducible run-to-run given the same ARA files.
    - constraints: Requires the citation-verification tool L1 §10 already needs, applied here too. Requires refs.yaml (the sibling normalized reference layer) to exist so `reference_prior.domain_baseline_ref` and `verification_evidence.ref` can resolve by id rather than by re-parsed prose.
  - **Reference-Prior Anchoring** — For every assumption/method entry whose realism/validity is about to be judged — run once per ledger entry, cached until the entry or the registry changes.. 1. Attempt automatic resolution of `reference_prior.domain_baseline_ref` (or method's `verification_evidence` refs) against a versioned, externally-maintained Domain Baseline Registry — a corpus of {field, assumption_type} → citable 'what's standard here' exemplars, itself carrying resolvable citations (methodology papers, reporting guidelines like PRISMA/CONSORT/ARRIVE, textbook consensus statements). 2. If resolved: `alignment` is populated deterministically from the registry entry's declared stance (matches/deviates/contested), citation attached. 3. If unresolved (niche subfield, no registry entry yet): field stays `not_specified` — routed entirely to the Class C panel with a lower confidence ceiling on the final score, and this degraded-mode is itself surfaced (not silently treated as equivalent to an anchored case).
    - reliability/reproducibility: Deterministic given a pinned registry version — reproducibility requires the panel report to record which registry snapshot/version was used, exactly as it records `calibration_set_version`.
    - constraints: The ecosystem must build and govern the Domain Baseline Registry — this is genuinely new infrastructure, analogous to a citation index but for 'what counts as a realistic vs. idealized assumption' per field. Coverage will be uneven at launch (dense in fields with reporting-guideline traditions like clinical trials/meta-analysis, thin in novel or interdisciplinary fields) — honest degraded mode, not a blocker.
  - **Calibrated Validity Panel (AMVP)** — Whenever S7/M30 (assumption realism), M31 (limitation validity), or S8/M32/M35 (method validity) scores are actually requested — e.g. at funding-review time or ARA-comparison time; not necessarily re-run on every compile.. 1. Deterministically generate one stress-probe per ledger entry from a fixed template keyed by `type`/`severity`/`tested_in_paper` (identical template structure for every ARA of the same assumption type — this is the single biggest lever against judge framing variance). Template: '<statement>. If false: <failure_mode>, affecting <affected_claims>. Construct the strongest case FOR this being realistic/standard in this field (cite reference_prior if present), then the strongest case AGAINST (name any known violations/edge cases), then output: realism_verdict ∈ {dreamcase_idealized, contested_in_field, standard_in_field, not_evaluable}, confidence [0,1], one-sentence rationale.' 2. Assemble a judge ensemble of ≥5: diverse model families and/or prompt framings and/or temperatures; for ARAs flagged high-stakes (high severity + untested + no resolvable reference_prior) or contested, route ~10-20% to a human domain-expert spot-audit pool as well. 3. Interleave, blind to the judge, items from a versioned, expert-labeled calibration set (known-hard exemplars spanning the full realism spectrum) among the real ledger items in the same batch. 4. Each judge answers every item (real + calibration) independently with the structured for/against/verdict/confidence output. 5. Score each judge's `calibration_accuracy` against the known calibration labels; judges below a published threshold (e.g. 0.7) are excluded from the aggregate for this run and this exclusion is recorded, not hidden. 6. Aggregate remaining judges' verdicts via median + dispersion (MAD, not a simple mean) per assumption; any item with high dispersion OR (high severity AND low realism verdict) is flagged `flag_for_human_review: true`. 7. Roll up to ARA level via a severity-weighted floor function — not a mean — so one untested, high-severity, unrealistic assumption dominates the score rather than being diluted by many low-stakes ones. 8. Emit `validity_panel_report.yaml` with full transcripts, protocol/calibration versions, and per-judge calibration accuracies.
    - reliability/reproducibility: Not deterministic and not claimed to be — reproducibility is measured, not assumed: re-running the identical protocol_version + calibration_set_version against the same ARA and reporting the test-retest agreement rate (e.g. % of assumptions whose median_verdict is unchanged) as a published, versioned protocol-health metric alongside every score. Auditability comes from the full transcript (every judge's for/against reasoning + confidence + calibration accuracy is retained), so a funder or contested-finding dispute can inspect exactly why a verdict was reached, not just the number.
    - constraints: Ecosystem must maintain: (a) versioned, periodically-refreshed calibration sets per broad field family (ideally curated by a neutral body — a metascience consortium, not the platform scoring the ARA, to avoid circularity); (b) access to a diverse judge ensemble (multiple model families, not just multiple temperature samples of one model, to avoid correlated failure); (c) a human-expert audit pool for the high-stakes escalation tier; (d) durable storage for full for/against transcripts (the audit trail is the product, not just the score).

  _Metrics afforded:_
  - Assumption realism & fairness (S7, M30) → Severity-weighted floor aggregate of per-assumption AMVP median verdicts (dreamcase_idealized=0, contested_in_field=0.5, standard_in_field=1), weighted so that untested (tested_in_paper=no) + load_bearing + high-severity assumptions dominate the score rather than being averaged against low-stakes ones; where reference_prior resolves, the verdict additionally cites the matched/deviating baseline. [semantic-judged (reliable-anchored for the subset of assumptions whose reference_prior resolves against the Domain Baseline Registry)]; anti-Goodhart: Exploit: pad the ledger with many trivial low-severity assumptions to dilute one genuinely unrealistic load-bearing one — defeated by the severity-weighted floor (worst high-severity item dominates, not averaged away). Exploit: fabricate a reference_prior citation to inflate realism — defeated because an unresolvable/fabricated anchor is capped at `not_specified` (equal to honest absence, never rewarded above it); only registry-resolved anchors count. Exploit: judge leniency/sycophancy — defeated by forced for/against construction, calibration-accuracy-gated judge inclusion, and published test-retest agreement making systematic drift visible.
  - Limitation validity (M31) → Two-part score: (a) deterministic set-difference check — does this limitation's `scope_narrowing` axis already appear in any assumption's `applicability_conditions`? If yes, `new_condition_added=false` and the limitation contributes near-zero; (b) for limitations that pass (a), a panel verdict (same AMVP template, adapted) on whether the added condition is specific and consequential rather than generic hedging. [reproducible (part a is a deterministic graph/set operation over ledger ids) combined with semantic-judged (part b)]; anti-Goodhart: Exploit: restate an already-declared boundary as a 'new' limitation to pad the count — defeated by the deterministic set-difference against `applicability_conditions`, which is a pure join, not a vibe check. Exploit: a vague but 'novel-sounding' limitation ('results may not generalize') scores well on genuineness — defeated because the panel's structured rubric requires the limitation name a specific axis/population/setting (matching `scope_narrowing`'s typed sub-fields), and generic hedges fail that structural test before the judge even runs.
  - Method validity & verification status (S8, M32/M35) → `status` claims (e.g. `widely_accepted_in_field`) are only credited if at least one `verification_evidence` entry resolves to a real external citation or a real internal sensitivity/ablation check (deterministic existence check via refs.yaml/experiments.md); the `applicability_match` — does this method's known validity domain actually cover how it's used here — is then panel-judged using the same AMVP machinery, anchored to the specific experiment/claim ids it must hold for. [reliable-anchored for the status-credit half (Class B: resolver-checked citation existence); semantic-judged for the applicability_match half (Class C)]; anti-Goodhart: Exploit: assert `status: widely_accepted_in_field` with no citation to borrow credibility for a shaky method — defeated because uncited status claims are capped at `not_specified`-equivalent, never at the higher score; a method can only claim the 'established' credit by actually resolving to a real methodology citation. Exploit: generic boilerplate justification ('this is a standard approach') — defeated because `applicability_match.claim` must anchor to the specific claim/experiment ids and network-geometry-type conditions it depends on, giving the judge a structural check to fail the boilerplate against.
  - Multi-perspective adequacy reflected in constraints (M36-adjacent) → Deterministic half: count distinct `perspectives.yaml` tags whose `anchored_in` resolves to a real, distinct method/experiment section (self-declared tags with no resolvable anchor are dropped before scoring). Semantic half: for ARAs with ≥2 resolved perspectives, panel judges whether the constraints.md/assumptions.yaml ledger shows evidence the second lens was actually used to stress-test the first (e.g., a computational finding's assumptions checked against a wet-lab observation) versus merely co-existing. [reproducible (tag-anchoring is a deterministic structural join) for the presence half; semantic-judged for the genuine-triangulation half]; anti-Goodhart: Exploit: self-label a single analysis under two perspective tags to fake multi-lens coverage — defeated because each tag must anchor to a genuinely distinct file/section (structural cross-check against experiments.md `Setup` fields or solution/ file identities, not free-text labels). Exploit: two lenses present but never actually cross-checked, scored as if triangulated — defeated because the semantic judge specifically probes for cross-lens stress-testing evidence in the ledger, using the same calibration-gated panel as the realism checks, not a rubber-stamp presence count.
  - AMVP protocol health / reproducibility (meta-metric) → Test-retest agreement rate: re-run the identical protocol_version + calibration_set_version against the same ARA's ledger and report the fraction of assumptions/methods whose median_verdict is unchanged, published alongside every score as its confidence envelope. [reproducible]; anti-Goodhart: This metric is itself the check on whether the Class-C scores above can be trusted at all in a given run — if the ecosystem lets protocol-health degrade silently (e.g. by using a stale calibration set, or an under-diverse judge pool), the exploit is that scores become noise dressed as rigor; publishing this number every time makes that degradation visible and comparable across runs instead of hidden inside a single confident-looking float.

  _Tradeoffs:_ This design roughly doubles the compiler's write surface for the solution/ layer (four new sidecar files atop existing prose), and creates a new prose⇄ledger consistency obligation — itself now a checkable metric, which is useful but not free. The Domain Baseline Registry and the calibration sets are genuinely new, expensive-to-build infrastructure with real governance risk: whoever curates "what's standard in this field" has power over every downstream realism score, so it must sit with a neutral metascience body, not the scoring platform itself, or the entire Class-C layer becomes circular (the judge trusts a baseline the same actor who wants a good score could influence). Coverage will be systematically uneven — dense in fields with reporting-guideline traditions (clinical trials, meta-analyses), thin to nonexistent in novel/interdisciplinary/niche fields — meaning the anchored half of the score (reliable-anchored) silently shrinks to the fully-semantic-judged case for exactly the frontier work funders most want to evaluate; this is disclosed via not_specified/degraded-mode flags rather than hidden, but it does mean the metric is least reliable precisely where it matters most. The panel protocol has real ongoing compute/labor cost (≥5-judge ensembles plus a human-audit tier) and is explicitly NOT run at every compile — it is a funding-review-time protocol, which means scores can go stale relative to a living ARA. Fabrication surfaces remain: a compiler could still invent a plausible-sounding consequence_if_false/sensitivity that isn't really what's at stake, and while source_anchor + affected_claims-id requirements catch the crudest versions (unanchored or claim-id-dangling entries), a sufficiently well-written fabricated ledger entry that cites real claim ids but mischaracterizes the actual mechanism can still pass the deterministic checks — this residual is squarely why the panel judgement stays Class C rather than being declared solved.

  _Open questions:_ How to bootstrap Domain Baseline Registries across every conceivable research field without that curation project itself becoming an unbounded Class-C problem (who decides what's "standard" in a genuinely novel subfield with no precedent yet — arguably the most important case to get right and the hardest to anchor). What ensemble size/diversity and what test-retest agreement threshold constitute "reproducible enough" to publish a score with confidence — no consensus benchmark exists yet for how many judges or how much disagreement is tolerable before a verdict should be withheld rather than reported. Whether sensitivity.quantitative_check will ever be populated with real numbers outside fields that already run formal sensitivity/robustness analyses (most papers, even good ones, do not) — if it stays qualitative low/medium/high in the overwhelming majority of cases, the sensitivity axis contributes much less discriminating signal than the design assumes. Cross-field portability of the very concept of "reference prior" — a dreamcase assumption in wet-lab biology and an idealization in pure mathematics are validated against completely different kinds of "standard practice," and a single registry taxonomy may not stretch across that range without fracturing into per-field sub-registries that don't interoperate. Governance and staleness: how the registry/calibration-set versions get retired or updated over time without making historical scores incomparable to new ones, and who is accountable when a calibration set itself turns out to have been mislabeled.


---


## HARDSIGNALS — Heuristic distance-from-optimum

_Class C — irreducibly semantic (reproducibility + auditability)_


**Judge rationale:** All four proposals converge on the same correct skeleton (a typed frontier/optimum ledger for M39 + a tagged perspectives/triangulation ledger for M36 with honest not_applicable/not_specified states and a bounded judge ensemble). They are separated on ONE axis that the mandate weights heavily: how much of each Class-C metric is pushed to deterministic computation with an explicit formula, versus left to an under-specified judge or a self-reported number.

#2 (FLCG) is the clear top: the tier-keyed tagged-union comparator makes distance ARITHMETIC (deterministic) for measured_ablation/benchmark/bound tiers and only judge-based for the 'argued' tier; independence is a structural JOIN over already-typed sibling IDs (not free text); the judge is confined to hunting undeclared confounds; and it uniquely attempts an actual reproducibility rerun and a derived (not asserted) confidence. It also best addresses the fabrication-surface criterion by computing downstream and reusing sibling ledgers by ID. Its gaps (tier!=confidence, unnormalized distance, unspecified product, vanity rerun, hand-waved calibration corpus) are real but fixable and are refinements of a fundamentally sound architecture.

#0 is second: it has the richest FRONTIER-side quantification (objective vectors, frozen candidate sets, uncertainty, mechanical + judged distances) — the harder, more novel half of the mandate — and correctly separates agreement from independence. Its fatal weakness is that both key numbers (the independence_matrix score and the agreement×independence composition) lack a stated function, and its regret normalizer is unconstrained. Still, it is more rigorous and more anti-gaming than its near-twin #1 and than #3.

#1 is a near-duplicate of #0 with two nice extras (OBI ontology-anchored method families; an adversarial missing-candidate audit baked into the protocol) but a materially WEAKER independence model — ordinal self-reported overlap levels (none/low/medium), which are exactly the gameable self-reports the design claims to eliminate. That regression drops it below #0.

#3 is the most honest about fabrication surface (clean compiler-emitted vs downstream-judge separation, so the compiler is never pressured to invent a frontier) and contributes two genuinely distinctive anti-gaming features — the circularity_check (fail if the frontier resolves to the same method as the heuristic) and first-class orthogonal/insufficient_info verdicts. But it has a concrete Goodhart hole its rivals avoid: independence_score = |independent| / |independent + shared|, with not_specified EXCLUDED from the denominator. A lazy or adversarial compiler marks three axes not_specified and one independent and scores a perfect 1.0 independence from near-total ignorance. Combined with a judge-heavy, weakly-normalized distance side, that keeps it out of the top two despite its strong honesty posture.


### Finalist A (judge-selected proposal; refine round cut off)

**FrontierTriangulation Ledger**  ·  _source: gpt-5.5-codex_

Add a typed, prose-renderable sidecar layer that makes two currently missing objects explicit: the reference optimum/frontier a heuristic is being judged against, and the independent perspectives that allegedly corroborate a claim. The key move is not to pretend these become deterministic; it is to bind judge inputs tightly enough that repeated runs evaluate the same candidates, evidence anchors, independence assumptions, and null cases. Honest not_specified and not_applicable values are first-class, so the format rewards clear absence rather than invented optima or fake triangulation. Metrics become reproducible, auditable Class C measurements with calibration sets, judge ensembles, uncertainty, and anti-gaming checks.

- **optimality_frontiers.yaml** (YAML sidecar, rendered into logic/solution/optimality.md) — Stores the reference optimum, oracle, or Pareto frontier against which a heuristic can be compared.
  - fields: frontier_id : id — required. scope : refs — required — claims/experiments/method components covered. optimum_status : enum[specified, derived, benchmarked, not_specified, not_applicable] — required. frontier_kind : enum[analytic_optimum, exhaustive_search, simulation_oracle, empirical_pareto, community_sota, expert_constructed] — nullable. objective_vector : list[objective] — required unless not_applicable. feasible_set : structured prose + artifact refs — required unless not_applicable. derivation_protocol : protocol_id — required for derived/benchmarked/frontier. frontier_artifacts : refs — required when present — code/data/quantity ids. uncertainty : distribution|interval|not_specified — required. source_anchors : provenance[] — required.
  - example: frontiers:
  - frontier_id: F01
    scope: {claims: [C03], experiments: [E04], heuristics: [H02]}
    optimum_status: derived
    frontier_kind: empirical_pareto
    objective_vector:
      - {id: O1, name: "macro-F1", direction: maximize, quantity_ref: Q44}
      - {id: O2, name: "assay cost per sample", direction: minimize, quantity_ref: Q45}
      - {id: O3, name: "runtime hours", direction: minimize, quantity_ref: Q46}
    feasible_set:
      candidates: [baseline_full_grid, paper_heuristic, bayesian_search_200, exhaustive_small_n]
      constraints: [A2, "same training split", "same raw Visium spots"]
    derivation_protocol: P_OPT_01
    frontier_artifacts: [src/execution/search.py, data/dataset.md, evidence/tables/derived_frontier.md]
    uncertainty: {bootstrap_ci: "95%", n_resamples: 1000}
    source_anchors:
      - {artifact: "src/configs/pipeline_parameters.md", locator: "BayesSpace k=2..28", role: input}
- **heuristic_assessments.yaml** (YAML) — Records each shortcut/heuristic as a measured choice, not just a prose trick.
  - fields: heuristic_id : H## — required. choice_type : enum[approximation, search_pruning, proxy_measure, stopping_rule, subsampling, model_simplification, manual_rule] — required. chosen_rule : prose + code/config refs — required. ideal_counterfactual : frontier_id|not_specified|not_applicable — required. distance_measures : list[distance] — required when frontier exists. regret_normalization : enum[absolute, relative_to_baseline, percentile, pareto_distance, domain_calibrated]. reason_not_optimal : enum[cost, ethics, unavailable_data, compute, measurement_limit, historical_choice, not_specified]. sensitivity_evidence : refs|not_specified. judge_packet : refs — required — bounded evidence bundle for Class C judge.
  - example: heuristics:
  - heuristic_id: H02
    choice_type: search_pruning
    chosen_rule: "Select k by stability over k=2..28, then run BayesSpace at k=9."
    source_refs: [logic/solution/method.md, src/configs/pipeline_parameters.md]
    ideal_counterfactual: F01
    distance_measures:
      - {name: normalized_regret, objective: O1, value: 0.07, ci: [0.03, 0.12], quantity_ref: Q51}
      - {name: pareto_rank_percentile, value: 0.82, quantity_ref: Q52}
    reason_not_optimal: compute
    sensitivity_evidence: [E04, evidence/tables/derived_frontier.md]
- **perspectives.yaml** (YAML graph) — Defines independent scientific lenses before scoring corroboration.
  - fields: perspective_id : id — required. modality : enum[wet_lab, computational, clinical, statistical, theoretical, simulation, field_observation, qualitative] — required. method_refs : refs — required. data_refs : refs — required or honest null. claim_refs : C##[] — required. independence_factors : object — required — data lineage, operators, instruments, assumptions, codebase, lab/site, blinding. known_shared_dependencies : refs|none|not_specified — required. source_anchors : provenance[] — required.
  - example: perspectives:
  - perspective_id: P_WET_01
    modality: wet_lab
    method_refs: [logic/solution/method.md]
    data_refs: [data/dataset.md, Q12, Q13]
    claim_refs: [C03]
    independence_factors:
      data_lineage: "primary Visium sections"
      instrument: "10x Visium + NovaSeq"
      operators: not_specified
      assumptions: [A1, A4]
      codebase: none
      blinding: not_specified
    known_shared_dependencies: none

  - perspective_id: P_COMP_01
    modality: computational
    method_refs: [src/execution/enrichment.py, logic/experiments.md]
    data_refs: [external_ref:RW12, Q21]
    claim_refs: [C03]
    independence_factors:
      data_lineage: "external snRNA-seq reference atlas"
      instrument: "independent public dataset"
      assumptions: [A4]
      codebase: "LIANA+/MOFA pipeline"
      blinding: not_applicable
    known_shared_dependencies: [concept:APOE_status]
- **corroboration_tests.yaml** (YAML plus optional matrix tables) — Makes triangulation a claim-level test with agreement and independence separated.
  - fields: test_id : id — required. target_claim : C## — required. perspectives : perspective_id[] — required. prediction : typed claim fragment — required. observations : per-perspective signed evidence — required. agreement_model : enum[same_direction, compatible_effect_size, mechanistic_chain, convergent_classification, contradiction_expected]. agreement_result : enum[corroborates, mixed, contradicts, underpowered, not_assessable]. independence_matrix : numeric/prose matrix — required. adjudication_packet : refs — required. null_reason : nullable enum[not_specified, single_perspective_only, shared_data_only, not_applicable].
  - example: tests:
  - test_id: T_C03_TRI
    target_claim: C03
    perspectives: [P_WET_01, P_COMP_01]
    prediction: "APOE E4 carrier effects concentrate in vascular and white-matter spatial domains."
    observations:
      P_WET_01: {sign: supports, quantities: [Q31, Q32], evidence: [evidence/figures/figure4.md]}
      P_COMP_01: {sign: supports, quantities: [Q37], evidence: [evidence/tables/enrichment.md]}
    agreement_model: convergent_classification
    agreement_result: corroborates
    independence_matrix:
      P_WET_01: {P_COMP_01: {score: 0.71, shared: ["APOE labels"], independent: ["assay", "dataset", "analysis code"]}}
    adjudication_packet: [C03, E03, E07, data/dataset.md, src/environment.md]

  _Protocols:_
  - **P_OPT_01: Reference Frontier Construction** — Any heuristic with ideal_counterfactual != not_specified/not_applicable.. Define objective vector; declare feasible set; run or cite frontier derivation; attach code/data; compute uncertainty; freeze candidate list before judging; register all failed derivations.
    - reliability/reproducibility: Requires executable frontier artifact or externally citable benchmark; evaluator reruns use the frozen candidate set and seed ledger; missing optimum is valid only with optimum_status: not_specified.
    - constraints: Executable frontier artifact or externally citable benchmark must exist; frozen candidate set and seed ledger must be preserved for reruns.
  - **P_JUDGE_39: Heuristic Distance Adjudication** — M39 scoring.. Assemble judge packet; compute mechanical distances where possible; have 3+ calibrated judges rate whether the frontier is appropriate and whether the distance interpretation is valid; report median, dispersion, and for/against rationales.
    - reliability/reproducibility: Judge ensemble of 3+ calibrated judges; report median, dispersion, and for/against rationales to make repeated runs converge.
    - constraints: Judges cannot introduce new candidates unless filing a separate audit note; calibration set must include known good heuristics, bad shortcuts, and honest no-optimum cases.
  - **P_TRI_01: Perspective Independence Audit** — S6/M36 scoring.. Classify modalities; trace data lineage; identify shared assumptions, personnel, code, instruments, and references; score pairwise independence; mark pseudo-replication when perspectives reuse the same dataset or pipeline.
    - reliability/reproducibility: Uses controlled modality and dependency vocabularies; independence score is judged from bounded fields, not whole-paper vibes.
    - constraints: Ecosystem must provide controlled modality and dependency vocabularies and data-lineage tracing; independence scored only from bounded declared fields.
  - **P_TRI_02: Corroboration Adjudication** — Claims with 2+ perspectives.. Extract claim fragment; map each perspective's signed observation; classify agreement model; separate agreement strength from independence strength; adjudicate contradictions and underpowered nulls.
    - reliability/reproducibility: Agreement strength and independence strength are scored separately so runs are auditable; contradictions and underpowered nulls are explicitly adjudicated rather than silently dropped.
    - constraints: More perspectives do not automatically score higher; shared-data agreement is capped.

  _Metrics afforded:_
  - M39 Heuristic distance-from-optimum → If no frontier exists, return honest-null class, not zero. If frontier exists, compute normalized regret per objective, Pareto distance/rank, and sensitivity-weighted distance; final score combines mechanical distance with judge confidence in frontier validity. [reproducible (Class C, with deterministic subcomponents)]; anti-Goodhart: Exploit is inventing an easy optimum or omitting hard candidates. Defense is frozen feasible sets, source-anchored frontier derivation, negative-control heuristics, uncertainty reporting, and calibration audits.
  - S6/M36 Multi-perspective triangulation strength → triangulation = agreement_strength x independence_strength x claim_relevance x evidence_quality, capped by the weakest pairwise independence and by source provenance. Contradictions reduce agreement but can raise scientific value if explicitly adjudicated. [reproducible / semantic-judged]; anti-Goodhart: Exploit is listing many shallow perspectives. Defense is pairwise independence matrices, shared-dependency caps, signed observations, and no credit for unanchored or duplicate lenses.

  _Tradeoffs:_ The layer is expensive: real frontier derivation may require extra compute, and independence auditing forces authors to expose shared dependencies they would normally leave implicit. It also creates fabrication surfaces: fake frontiers, cherry-picked feasible sets, and decorative perspectives. Mitigation is honest-null symmetry, frozen protocols, provenance anchors, calibration sets, and caps for shared data/code/assumptions. The format stays readable by rendering YAML into typed markdown summaries, while metrics consume the YAML.

  _Open questions:_ How should fields define domain-calibrated regret across incomparable objectives like cost, ethics, and accuracy? Who maintains the calibration sets for good and bad heuristics by field? How should triangulation reward productive contradiction versus clean corroboration? What minimum ecosystem registries are needed for external benchmark frontiers and data-lineage independence checks?


### Finalist B (judge-selected proposal; refine round cut off)

**Frontier Ledger & Corroboration Graph (FLCG)**  ·  _source: claude-sonnet-5_

M39 fails today because no artifact ever states what the 'ideal' alternative to a heuristic would look like; S6/M36 fails because 'perspective' is undefined and independence is never distinguished from mere repetition. FLCG fixes both by making the reference frame an explicit, tiered, honestly-nullable object instead of a hidden LLM guess: every heuristic gets a frontier record whose evidentiary tier (measured ablation > external benchmark > theoretical bound > argued > not-applicable) is declared up front, so distance is only ever as precise as its cheapest verifiable anchor. Every independent line of evidence for a claim gets a perspective record scored for independence along four controlled, ID-joined axes (data source, method class, team, assumption set) rather than free text, so 'two perspectives' can't be the same pipeline relabeled. Triangulation strength is then a deterministic product of independence x agreement, with a bounded Class-C judge overlay whose only job is to hunt for the undeclared shared confound the four axes miss. Both structures reuse the sibling quantity ledger and normalized-refs table by ID rather than re-inventing provenance, and both carry a first-class not_applicable/argued-tier path so honest absence of a real optimum or a genuinely single-lens study scores equal to, not worse than, a well-anchored one.

- **Heuristic block extension (`logic/solution/heuristics.md`, in-place fields)** (typed-markdown (additive fields inside the existing H## block from ara-schema.md)) — Give every existing H## heuristic block the minimum vocabulary needed to even ask 'distance from what?' before any ledger is consulted — the shortcut's trade-off axis and a pointer to its frontier record (or an honest reason none exists).
  - fields: Shortcut dimension : enum{compute_cost, sample_size, approximation_error, assumption_strength, search_space_pruning, generalization_scope, other} — required, no default
Ideal counterfactual (prose) : string — required; states in plain language what the non-shortcut approach would be, independent of whether it was ever measured
Frontier ref : ref-id into frontier.yaml (F##), or not_applicable — required
(existing fields Rationale/Sensitivity/Bounds/Code ref/Source unchanged)
  - example: ## H03: Train-time PET->MRI distillation for MRI-only deployment
- **Rationale**: Distilling stop-gradient PET embeddings into the MRI pathway (Eq. 11) retains molecular knowledge for later MRI-only inference.
- **Shortcut dimension**: assumption_strength
- **Ideal counterfactual**: Retain full joint PET+MRI inference at deployment (no distillation), requiring PET availability for every subject at inference time.
- **Frontier ref**: F03
- **Sensitivity**: Not specified in paper
- **Bounds**: alpha in [0,1]; late fusion at embedding level
- **Code ref**: [src/execution/ssl_losses.py]
- **Source**: sec 3.4, Eq. 11
- **`logic/solution/frontier.yaml` — the optimum/reference-frame ledger** (YAML, one record per heuristic (1:1 with an H## via heuristic_ref)) — Store the reference frontier a heuristic is measured against as a tagged union keyed by evidentiary tier, so distance-from-optimum is never a single opaque number but always carries its own proof-of-work: how the comparator was obtained, and therefore how much to trust the distance.
  - fields: id : string F{NN} — required
heuristic_ref : ref-id (H##) — required, must resolve
shortcut_dimension : enum (mirrors heuristics.md field) — required
ideal_counterfactual : string — required (may restate the heuristics.md field)
applicability : enum{applicable, not_applicable} — required
not_applicable_reason : string — required iff applicability=not_applicable; null otherwise
tier : enum{measured_ablation, external_benchmark, theoretical_bound, argued, not_applicable} — required
comparator : tagged-union object, shape depends on tier — measured_ablation:{heuristic_quantity_id, ideal_quantity_id} both ref-ids into quantities.yaml; external_benchmark:{ref_id (into refs.yaml), reported_value, unit, registry_snapshot_date}; theoretical_bound:{ref_id, bound_value, bound_type, unit}; argued:{judge_panel_id} ref-id into judge_panels.yaml; null when tier=not_applicable
distance : {value: number|null, unit: string|null, direction: string|null, ci: [lo,hi]|null} — arithmetic for tiers 1-3, judge-median+IQR for argued, all-null for not_applicable
confidence : enum{high, medium, low, null} — derived, not asserted
source_anchor : {value_ids|ref_ids, source_file, locator, quote} — provenance, required unless not_applicable
  - example: version: "1.0"
frontiers:
  - id: F03
    heuristic_ref: H03
    shortcut_dimension: assumption_strength
    ideal_counterfactual: "Full joint PET+MRI inference at deployment, no distillation."
    applicability: applicable
    tier: measured_ablation
    comparator:
      heuristic_quantity_id: Q41
      ideal_quantity_id: Q42
    distance:
      value: 0.031
      unit: "AUC points"
      direction: "distilled MRI-only underperforms joint model by 0.031 AUC"
      ci: [0.018, 0.044]
    confidence: high
    source_anchor:
      value_ids: [Q41, Q42]
      source_file: evidence/tables/table4.md
      locator: "Table 4, rows 2 and 5"
      quote: "MRI-only (distilled): AUC 0.812 [0.799,0.825]; PET+MRI (joint): AUC 0.843 [0.831,0.856]"
  - id: F09
    heuristic_ref: H09
    shortcut_dimension: approximation_error
    ideal_counterfactual: "not_specified"
    applicability: not_applicable
    not_applicable_reason: "Underlying assignment problem proven NP-hard (RW04, Thm 2); no known tractable optimal algorithm exists to compare against."
    tier: not_applicable
    comparator: null
    distance: {value: null, unit: null, direction: null, ci: null}
    confidence: null
    source_anchor: {source_file: logic/related_work.md, locator: RW04, quote: "NP-hardness of the assignment problem (Thm 2)"}
- **`judge_panels.yaml` — shared judge-ensemble ledger** (YAML, one record per elicitation event) — One reusable elicitation record type serving both Class-C overlays in this design (argued-tier frontier distance, and triangulation corroboration verdicts), so both metrics share one auditable, rerunnable judge protocol rather than each inventing its own ad hoc LLM call.
  - fields: id : string JP{NN} — required
purpose : enum{frontier_distance, triangulation_corroboration} — required
target_ref : ref-id of the F## or T## record being judged — required
calibration_set_id : string, versioned external corpus id (e.g. distance-calib-v3) — required
prompt_version : string — required (frozen rubric text hash, for replay)
judges : list of {model_id, decoding_temp, verdict_value: number, for: list[string], against: list[string], rationale: string} — required, length K>=3, model_id must span >=2 distinct model families
blinding : {self_assessment_redacted: bool} — required
aggregate : {median, iqr, n_judges, pct_within_0.1_of_median} — derived, deterministic given judges[]
reproducibility_check : {rerun_id, rerun_median, delta, stable: bool} — required (a second, independent run of the same panel)
  - example: id: JP12
purpose: frontier_distance
target_ref: F07
calibration_set_id: distance-calib-v3
prompt_version: frontier-rubric-2026-05
judges:
  - model_id: model-A-v2
    decoding_temp: 0.0
    verdict_value: 0.31
    for: ["Search space is small (3 hyperparams); greedy likely near-optimal here"]
    against: ["No sensitivity sweep reported; unclear if local optimum reached"]
    rationale: "Moderate distance; greedy coordinate descent on a low-dimensional space rarely misses by much, but zero verification was run."
  - model_id: model-B-v1
    decoding_temp: 0.0
    verdict_value: 0.40
    for: ["..."]
    against: ["..."]
    rationale: "..."
  - model_id: model-A-v2 (reseeded)
    decoding_temp: 0.0
    verdict_value: 0.34
    for: ["..."]
    against: ["..."]
    rationale: "..."
blinding: {self_assessment_redacted: true}
aggregate: {median: 0.34, iqr: [0.31, 0.40], n_judges: 3, pct_within_0.1_of_median: 1.0}
reproducibility_check: {rerun_id: JP12-r2, rerun_median: 0.33, delta: 0.01, stable: true}
- **`logic/perspectives.yaml` — the independent-lens registry** (YAML, one record per distinct evidential lens used anywhere in the paper) — Make 'a perspective' a first-class, ID-joined object instead of a prose adjective, so independence between two lines of evidence is a structural join over already-typed sibling IDs (dataset id, method/concept xref, assumption id) rather than a self-report a compiler can fabricate.
  - fields: id : string P{NN} — required
label : string — required, human-readable
type : enum{wet_lab_experimental, computational_simulation, statistical_inference, observational_cohort, literature_meta_analytic, theoretical_derivation, expert_elicitation, other} — required
data_source_id : ref-id into the dataset ledger (data/dataset.md accessions) or novel_this_work — required
method_class : ref-id into a concept xref / controlled vocabulary (sibling M64/S9 design), not free text — required
team : string or not_specified — required (author-group/affiliation identity, for independence axis 3)
assumption_set : list[ref-id] into problem.md A## assumptions this lens depends on — required, may be empty list
instruments : list[string] — assay/tool names, optional
produces : list[ref-id] into quantities.yaml (the quantity ids this lens generates) — required
  - example: perspectives:
  - id: P01
    label: "Spatial transcriptomics differential expression (Visium)"
    type: wet_lab_experimental
    data_source_id: GEO:GSE307990
    method_class: MC-limma-voom-DGE
    team: "Huu Lab (Institution A)"
    assumption_set: [A2]
    instruments: ["10x Visium", "SpaceRanger", "BayesSpace"]
    produces: [Q22]
  - id: P03
    label: "Cross-cohort eQTL colocalization"
    type: computational_simulation
    data_source_id: "dbGaP:phs001234 (ROSMAP)"
    method_class: MC-coloc-posterior
    team: "Chen Lab (Institution B)"
    assumption_set: [A2, A5]
    instruments: ["coloc R package"]
    produces: [Q23]
- **`logic/triangulations.yaml` — perspective x claim corroboration edges** (YAML, one record per (claim, perspective-set) triangulation attempt) — Score whether two-or-more perspectives genuinely triangulate a claim: independence (do they differ on the controlled axes) times agreement (do their produced quantities converge), plus a bounded judge overlay whose sole task is to surface the shared confound the four axes cannot see.
  - fields: id : string T{NN} — required
claim_ref : ref-id (C##) — required
perspectives : list[ref-id] (P##, length >=2) — required
independence : {axes: {data_source, method_class, team, assumption_set} each -> 'same'|'differ', score: float} — score = count(differ)/4, deterministic given perspectives.yaml
agreement : {method: enum{quantitative_pooled, directional_concordance, qualitative_concordance}, perspective_findings: list[{perspective, quantity_id, direction, value}], score: float|null} — deterministic for quantitative_pooled (CI-overlap/normalized distance) and directional_concordance (sign match); null pending judge for qualitative_concordance
triangulation_strength : float — deterministic = independence.score x agreement.score (only computed when agreement.score is non-null)
corroboration_judgment : {judge_panel_id (ref into judge_panels.yaml), verdict: enum{strong_corroboration, weak_corroboration, spurious_agreement, conflicting}, for: list[string], against: list[string], confidence: enum{high,medium,low}} — the Class-C overlay, required whenever triangulation_strength >= a disclosed threshold OR agreement.method=qualitative_concordance
  - example: triangulations:
  - id: T04
    claim_ref: C06
    perspectives: [P01, P03]
    independence:
      axes: {data_source: differ, method_class: differ, team: differ, assumption_set: same}
      score: 0.75
    agreement:
      method: directional_concordance
      perspective_findings:
        - {perspective: P01, quantity_id: Q22, direction: upregulated, value: "log2FC 0.81, FDR 0.003"}
        - {perspective: P03, quantity_id: Q23, direction: upregulated, value: "colocalization posterior 0.87"}
      score: 1.0
    triangulation_strength: 0.75
    corroboration_judgment:
      judge_panel_id: JP15
      verdict: strong_corroboration
      for: ["Independent cohorts (Visium donor panel vs ROSMAP)", "Independent assay classes (spatial transcriptomics vs summary-stat colocalization)", "Directionally consistent"]
      against: ["Both ultimately anchor to the same reference APOE genotyping calls upstream — a shared dependency the 4 axes don't capture"]
      confidence: medium

  _Protocols:_
  - **Ablation-Anchored Frontier Protocol (tier: measured_ablation)** — Whenever the paper (or its exploration_tree.yaml) already ran the heuristic's own counterfactual — an ablation, a 'full' vs 'reduced' variant, a non-approximate baseline — as a genuine experiment.. 1. Locate the two comparable quantities in quantities.yaml (heuristic-version value, ideal-version value) that share units/measurement protocol. 2. Populate frontier.yaml comparator.measured_ablation with both quantity ids. 3. Compute distance = arithmetic difference (or ratio, per shortcut_dimension convention) deterministically; propagate CIs if present on the source quantities. 4. Set confidence=high only if both quantities share the same held-out fold/cohort/run (checked via their shared source_anchor's experiment id); otherwise downgrade confidence to medium and flag 'counterfactual not perfectly matched'.
    - reliability/reproducibility: Fully deterministic given the quantity ledger — reruns always produce the identical value. The only judgment call (was the ablation a fair, non-strawman comparator) is explicitly NOT claimed as solved here; it is flagged as open rather than silently assumed away.
    - constraints: Requires the sibling quantities.yaml typed-quantity-ledger design to exist and to tag type:input|result consistently; requires experiments.md's measures/baseline structured fields so the two quantities can be confirmed as measuring the same construct on the same cohort.
  - **External Frontier Resolution Protocol (tiers: external_benchmark, theoretical_bound)** — The paper doesn't run its own counterfactual, but a known SOTA leaderboard entry, prior published result, or a closed-form theoretical bound (NP-hardness proof, Cramer-Rao bound, information-theoretic limit) is citable as the comparator.. 1. Compiler cites the candidate comparator via a ref_id into refs.yaml (never a bare string). 2. An external resolver (registry lookup / bound catalog) fetches and confirms the claimed reported_value or bound_value at a pinned registry_snapshot_date. 3. If resolution succeeds, tier stands and distance is computed deterministically. 4. If resolution FAILS (ref doesn't exist, or resolved value contradicts the claimed value), the record is automatically DOWNGRADED to tier=argued and flagged as an integrity violation distinct from an honest argued-tier declaration from the start — mirrors the existing DOI-verification pattern.
    - reliability/reproducibility: Deterministic once the registry snapshot is pinned; reproducibility depends on the registry being versioned/dated — the snapshot date is therefore a required field, not optional.
    - constraints: Ecosystem must provide a maintained bounds-and-benchmark resolver (a registry akin to a DOI resolver, but for SOTA leaderboards / classical complexity-theoretic bounds / statistical lower bounds) with versioned snapshots. Without it this tier cannot exist and every heuristic collapses to argued or not_applicable — an honest degradation, not a silent one.
  - **Argued-Tier Distance Elicitation Protocol (tier: argued, Class C)** — No in-paper ablation and no resolvable external comparator exists, but the heuristic is applicable (an ideal alternative is conceptually describable even if unmeasured).. 1. Construct/select 3-5 calibration exemplars from the versioned calibration_set_id (expert-labeled heuristic/ideal/distance triples spanning multiple fields) and show them in-context to anchor the rubric, without exposing the full corpus. 2. Redact the paper's own self-assessment language before judging. 3. Run K>=3 judges from >=2 distinct model families at temperature 0, each producing a structured for/against list before a numeric verdict. 4. Aggregate median + IQR; report pct_within_0.1_of_median as the reliability signal. 5. Independently rerun the full panel once more; if the rerun median differs beyond a disclosed threshold, flag stable=false and discount confidence rather than hide the instability.
    - reliability/reproducibility: Not deterministic by construction (Class C), but reproducibility is engineered in: fixed prompt_version hash, frozen calibration exemplars, temperature-0 decoding, cross-model-family ensemble, and an explicit rerun-delta check reported alongside the score.
    - constraints: Ecosystem must maintain and periodically refresh a calibration corpus (governance question); must guard against calibration-set contamination in judge model training data; needs a minimum of two structurally distinct judge model families to be a meaningful ensemble.
  - **Perspective Independence Audit Protocol** — Whenever a claim (C##) is supported by more than one perspective (P##) in perspectives.yaml — run before computing any triangulation_strength.. 1. For each pair of perspectives cited by the same claim, join on their four declared axis values (data_source_id, method_class, team, assumption_set). 2. Score independence = count(axes that differ)/4 — purely mechanical. 3. Cross-check: if two perspectives share the identical data_source_id, this is caught automatically regardless of how differently they're labeled in prose (the axis IS the dataset ledger's id, not free text). 4. Flag any perspective pair with independence=0 as 'same-lens repetition, not triangulation' and route it instead to the sibling S17/M25 replication-value metric rather than counting it here.
    - reliability/reproducibility: Deterministic given perspectives.yaml — a rerun always yields the same independence score. Reliability of the input is bounded by the same-ID-reuse check, plus the corroboration judge's job of hunting for undeclared shared dependencies.
    - constraints: Requires the sibling entity-id / dataset-ledger / concept-xref designs to exist so method_class and data_source_id are real joinable IDs, not prose — without them this protocol degrades to string-matching.
  - **Corroboration Verdict Elicitation Protocol (Class C overlay)** — Whenever a T## triangulation record's mechanical independence x agreement score is being finalized into a 'genuinely corroborates' claim — this is the piece that answers the actual S6/M36 question, not just the structural proxy.. 1. Judge panel is shown ONLY the T## record's structured fields plus the underlying source_anchor spans — not the paper's own narrative framing of 'we triangulated X'. 2. Judges produce a for/against list scoped to: (a) plausible undeclared shared dependency the four axes miss; (b) whether agreement looks substantive or coincidental given effect sizes. 3. Verdict in {strong_corroboration, weak_corroboration, spurious_agreement, conflicting}. 4. Rerun once (reordered inputs) to check verdict stability; report delta.
    - reliability/reproducibility: Class C — cannot be deterministic — but minimizes judge degrees of freedom by restricting the judge's view to the structured record and mandating for/against scoped exactly to 'undeclared shared dependency' and 'substantive vs coincidental agreement'.
    - constraints: Needs the same judge-panel infra (model diversity, prompt versioning, calibration set — a triangulation-specific corpus of known genuine vs known spurious corroboration cases) as the frontier judge protocol; ecosystem must maintain that corpus too.

  _Metrics afforded:_
  - Frontier Coverage & Tier-Honesty Index (per-ARA, corpus-comparable) → Fraction of H## heuristics that have a frontier.yaml record with applicability and tier declared (regardless of which tier); separately, fraction landing in each tier, and fraction of not_applicable records carrying a substantive not_applicable_reason vs. a placeholder. [deterministic]; anti-Goodhart: Exploit: pad heuristics.md with trivial/fake heuristics just to inflate 'coverage', or mark everything not_applicable to dodge scrutiny. Defense: coverage is scored jointly with heuristics.md's own comprehensiveness metric (M38, sibling) so manufacturing heuristics fails that check instead; not_applicable requires a substantive, source-anchored reason and is scored EQUAL to a resolved frontier, not worse — removing the incentive to avoid it, while a vague/boilerplate reason is visibly distinguishable from a real one.
  - Measured/Bound Distance-from-Optimum (tiers 1-3) → Arithmetic gap/ratio between the heuristic's quantity and the resolved ideal comparator (ablation quantity, verified external benchmark, or verified theoretical bound), read directly off frontier.yaml.distance. [reliable-anchored]; anti-Goodhart: Exploit: cite a fabricated or misquoted benchmark/bound to claim a flattering tier-2/3 distance. Defense: the External Frontier Resolution Protocol requires the ref to actually resolve and its value to match; an unresolved or contradicted claim is auto-downgraded to argued AND flagged as an integrity violation — scoring strictly worse than having declared argued honestly from the start.
  - Argued Distance-from-Optimum (tier 4, M39's irreducible core) → Median judge-panel verdict_value from judge_panels.yaml (purpose=frontier_distance), reported with IQR and rerun-delta as the confidence band, never as a bare point estimate. [semantic-judged]; anti-Goodhart: Exploit: prompt-optimize toward judges by using self-flattering language in the paper, or get lucky with a single lenient judge. Defense: self-assessment language is redacted before judging; ensemble spans >=2 model families and reports dispersion; calibration exemplars anchor the rubric; for/against-before-verdict ordering blocks a judge from writing a number then rationalizing it.
  - Perspective Independence Score (structural half of S6/M36) → count(axes differing)/4 across {data_source_id, method_class, team, assumption_set} for any pair of perspectives cited by the same claim, read from perspectives.yaml joins. [reproducible]; anti-Goodhart: Exploit: relabel one pipeline run as two 'perspectives' to farm triangulation credit. Defense: axes are joins to OTHER sibling ledgers' typed IDs rather than free text — reusing the same dataset_source_id or method_class under two labels is mechanically caught, and independence=0 pairs are routed away from triangulation credit into the separate replication-value metric.
  - Agreement Score (structural half of S6/M36) → For quantitative_pooled: CI-overlap or normalized distance between the two perspectives' quantities. For directional_concordance: deterministic sign match on direction fields. For qualitative_concordance: deferred to the corroboration judge. [reproducible]; anti-Goodhart: Exploit: cherry-pick which two perspectives to compare, ignoring a third that disagrees, to inflate agreement. Defense: perspectives.yaml is exhaustive by construction (every perspective that produces a quantity bearing on a claim must be registered), so a triangulation record omitting a registered, relevant perspective is a detectable coverage gap, not an invisible cherry-pick.
  - Multi-Perspective Triangulation Strength & Corroboration Verdict (S6/M36's irreducible core) → triangulation_strength = independence.score x agreement.score (deterministic once both are known), overlaid with the corroboration_judgment verdict, which can downgrade (e.g. strong-structural-score but 'spurious_agreement' verdict) when an undeclared shared dependency is found. [semantic-judged]; anti-Goodhart: Exploit: satisfy the structural formula while both perspectives secretly share an unstated confound (same reference genome build, same PI despite different 'team' string, same upstream preprocessing). Defense: the corroboration judge's for/against is explicitly scoped to hunt for exactly this, so a structurally-perfect-looking record can still be marked spurious_agreement, and that downgrade is the headline number a funder sees.

  _Tradeoffs:_ Writing burden is real and front-loaded: every heuristic now needs a frontier record and every multi-evidence claim needs perspective + triangulation records, and most existing compiled ARAs will start with near-empty frontier.yaml/perspectives.yaml until the ecosystem's calibration corpora and bounds/benchmark resolvers exist — this design has a bootstrapping problem it cannot solve alone. Tier-laundering is an unresolved residual risk: a compiler can construct a technically-real but rigged ablation (a strawman 'ideal' variant deliberately handicapped) and pass the measured_ablation tier's mechanical checks; the design flags this as an open problem rather than claiming to solve it, since judging whether a counterfactual is FAIR is itself Class C. Perspective granularity is inherently fuzzy (is single-cell RNA-seq a different method_class from bulk RNA-seq, or a variant of the same one) and the controlled-vocabulary anchoring only bounds, doesn't eliminate, gaming via hair-splitting perspective count upward or lumping distinct lenses downward to dodge the independence audit. The whole design is deliberately non-self-sufficient: it depends on three sibling layers (a typed quantities.yaml ledger, a normalized refs.yaml with resolvable external IDs, and controlled-vocabulary/entity xrefs on concepts and datasets) — without those, tier-1/2/3 frontier resolution and axis-based independence collapse back into prose-parsing and this design offers nothing beyond what a good judge could already attempt unaided. Finally, judge-ensemble cost and calibration-corpus governance (who curates it, how it's refreshed, contamination risk when judge models may have seen the corpus during training) are pushed into the open-questions bucket rather than solved, which is honest but means the Class-C core of both metrics remains only as good as an institution that doesn't yet exist.

  _Open questions:_ Who governs and refreshes the calibration corpora (distance-calib-*, triangulation-calib-*) — a single curator is a single point of capture, but a crowdsourced one risks drift and gaming; and how do we detect/mitigate LLM judges having memorized calibration items during pretraining? How do we verify a measured_ablation's counterfactual was a FAIR comparator and not a strawman, given that the mechanical checks (quantity ids exist, same fold) can't see rigging in how the ideal variant was constructed? What is the correct set of independence axes — is four (data_source, method_class, team, assumption_set) sufficient across fields, or does e.g. temporal independence (same team/method, different era) deserve a fifth axis in some domains? Can distance-from-optimum ever be meaningfully aggregated across a corpus for a funder-facing composite score when the unit of 'distance' is field- and dimension-specific (AUC points vs. log-runtime-factor vs. a [0,1] judge scale), or must M39 permanently stay an un-aggregable per-heuristic disclosure? And structurally, should a paper with zero applicable heuristics or zero multi-perspective claims score as 'not_applicable' (neutral) on these metrics entirely, or does the format need a genre-manifest signal (sibling design) declaring whether triangulation/heuristic-use was even EXPECTED for this kind of work, so silence isn't mistaken for either honesty or a gap?


---
