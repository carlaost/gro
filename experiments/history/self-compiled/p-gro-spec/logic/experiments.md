# Experiments / analyses

This spec is a design document, not an empirical-trial paper: there is no dataset run through a model.
The paper's own methodological "experiment" is the three-stage process stated in its Appendix — a
tournament-synthesized draft, an adversarial critique that produced eleven must-fix findings (plus
over-claims, missing/underspecified fields, cross-layer conflicts), and this revision, which resolves
each finding by a concrete design change or an explicit demotion to §7. The blocks below decompose
that process into the specific analyses each claim rests on.

## E01: Three-stage synthesis → adversarial critique → revision process
- **Arms**: (1) draft — merged from twelve gap-tournament-winning designs (QUANT, CLAIMFOL, ENTITY, EDGES, GENRE, REFGRAPH, REGISTRY, NOVELANCHOR, NOVELSCORE, ENTAIL, VALIDITY, HARDSIGNALS) evaluated against `AFFORDANCE_GAP.md` and `ALL_METRICS_MERGED.md`; (2) adversarial critique — `verdict: needs_major_revision`, enumerating internal inconsistencies, over-claims, missing/underspecified fields, cross-layer conflicts, eleven must-fix items; (3) this revision — resolves each must-fix by a design change or an explicit, labelled §7 demotion.
- **Method**: for every finding raised at stage 2, verify the revision text either (a) introduces a concrete new mechanism (new ledger/id-space, scoped authority table, pinned ordering, new blind-diff pass) or (b) states the residual explicitly in §7 with its §4 tag corrected.
- **Result**: every must-fix item traced to a resolution; none silently dropped. Concrete design changes introduced: `XQ##` external-quantity ledger, `DISC-*` discipline ledger, scoped `registry_authority`, two-profile `VerificationRecordCore`, pinned `contested`-floor severity ordering, designed free-text planned-outcome extraction, `claim_coverage`/`assumption_coverage`/`numeral_reconstruction` blind diffs, a specified pipeline-independence definition, and a tiered Tier-C execution model.
- **Supports**: C01, C10

## E02: Tier-C judge-inference cost arithmetic
- **Method**: take the stated per-protocol multipliers — P1 ≥3 model families × sealed-N runs; P2 J≥3 judges × R≥3 runs (~12 verdicts) per edge, plus INVARIANCE_AUDIT and CALIBRATION_REPORT; P3 ≥5 judges × ≥3 families plus a blind BCR twin ensemble; P4 K≥3 judges × ≥2 families — and apply them across a representative mid-size GRO with ~40 claim↔evidence edges to derive an order-of-magnitude judge-inference count, assuming full-density (every protocol on every element) execution.
- **Result**: 10³–10⁴ judge inferences per mid-size GRO at full density; stated as not scaling to a hundred-thousand-paper corpus, motivating the tiered execution model (full corpus at Tier A/B; Tier C on funder-shortlisted GROs + a random audit sample; within-GRO sampling of P2's J×R panel to gate-flagged edges).
- **Supports**: C02

## E03: Cross-layer provenance-regime audit
- **Method**: enumerate, layer by layer, what is hashed/normalized and under which regime — L1 raw-byte SHA-256 over `source_anchor`; L1's QUANT canonical lexer for numeric-literal comparison (not a stored hash); L6 `content_hash`/`quote_hash` under `NORM_v1`; L3 `embedding_anchor.text_hash` over derived text; L4's edge-attr ⊆ quote ⊆ internal-text double-lock (substring containment, not a hash) — and check whether any two layers share a hash function.
- **Result**: no shared hash function across layers; the same quote hashed under L1 (raw) and L6 (`NORM_v1`) does not match; cross-layer identity is established only via id reference. Table published in §3; residual re-stated in §7.
- **Supports**: C03

## E04: Provenance-ceiling (self-report confidence cap) design fix
- **Method**: respond to the internal-inconsistency finding that a confidence-shaping quantity keyed on self-reported provenance contradicts the stated rule "confidence is ensemble agreement, never self-report." Redesign the mechanism so the self-report can only act as a ceiling (never a confidence value), fix the cap schedule per provenance tier, and require independent machine-checkable evidence (not the self-report) for any upgrade of the cap.
- **Result**: cap schedule reviewer_confirmed→1.0 / author-authored→0.6 / ai-suggested→0.3; upgrades gated on independent corroboration (e.g., independent REFGRAPH finding no closer predecessor) or a Seal-L2 reviewer setting `reviewer_confirmed`, itself spot-auditable and barred to the compiler.
- **Supports**: C04

## E05: Contested-floor severity-lattice placement fix
- **Method**: respond to the finding that the draft never fixed where `contested` sits relative to a refutation, leaving room to steer a refuted edge into `contested` for profit. Define a total order over effective verdicts and a rule for how a `refuted/contradicted` run interacts with a `contested` disposition on the agreement axis.
- **Result**: six-step lattice `refuted/contradicted < not_supported < contested < weakly_supported < supported < strongly_supported`; `contested` floors at `not_supported`; any grounded refuted/contradicted run is sticky and sets the floor to `refuted`, published in the COMPOSE table.
- **Supports**: C05

## E06: Independence-mechanism specification and system-wide audit
- **Method**: define a precise, checkable test for "pipeline_independent" (distinct pipeline id; distinct model family; distinct prompt-lineage hash; packet-only inputs, no free compiler prose) and apply it to every pass in the spec claiming independence (L1 `external_fidelity`, L6 `semantic_review`, L7 `CorrespondenceAssessment`, the L7 planned-outcome extractor, L3's two arms, and every Tier-C panel).
- **Result**: every pass audited meets the four-part test except that the test itself only rules out self-certification and shared-prompt collusion, not shared-pretraining correlation between LLM families; L3 Arm A is the sole non-LLM pass and is reclassified as genuinely decorrelated, distinct from every other "pipeline-independent (necessary, not sufficient)" pass.
- **Supports**: C06

## E07: Boundedness analysis of two structural anti-gaming defenses (prior-art cap, genre-shopping)
- **Method**: for each defense the pre-critique draft described with an absolute claim ("never"/"structural"), trace the mechanism's actual trigger condition and identify the case where it does not fire — for the prior-art cap: predecessor outside the `q_auto` neighborhood (temporal leakage / embedding evasion); for genre-shopping: purely narrative genres with an empty anchor set (no structural-corroborator clear available).
- **Result**: both defenses re-tagged from "never"/"structural" to explicitly bounded, with a named residual bucket in each case (prior-art: unguaranteed against an evaded/missed neighbor; genre: `contested_ttl_lazy_omission` + corpus `classifier_error_signal`).
- **Supports**: C07, C08

## E08: Coverage/joinability and namespace-conflict accounting (XQ## exemption, m04_joinable_rate, n-expectation promotion)
- **Method**: for each of three separate findings — (i) `baseline_value` cannot be a `Q##` without breaking L1's "authored once in this paper" definition; (ii) M04's numeric join presumes a posted registry value that most PROSPERO/NCT entries lack; (iii) the over-claim field-diff needs `n` to fire, and axiom 4 protects `n=null` as honest absence, creating a free pass for exactly the claims that most need scrutiny (population estimates, universal claims) — design a targeted fix and state the resulting coverage/exemption rule explicitly rather than assuming full coverage.
- **Result**: (i) a distinct `XQ##` ledger for off-paper numbers, exempt from `numeral_coverage`; (ii) `m04_joinable_rate` / `m04_direction_joinable_rate` published as the actual joinable fraction, with the join simply not running elsewhere; (iii) `n` promoted to an expected slot for `population_estimate`/`claimed_universal` claims only, so omission at that tier is a violated expectation, while lower-tier claims keep the honest-absence protection.
- **Supports**: C09, C11, C12
