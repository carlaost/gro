# Claims

Load-bearing design assertions of the GRO Unified Format Specification. Because this is a
format/architecture spec rather than an empirical-results paper, "Proof" experiments (`logic/experiments.md`)
are the design/critique analyses — the three-stage draft → adversarial-critique → revision process, and the
specific arithmetic/boundary analyses it produced — not statistical trials.

---

## C01: The format partitions every metric into exactly three rigor tiers
- **Statement**: GRO assigns every afforded metric to exactly one of three rigor tiers — Tier A deterministic (layers L1–L5, pure functions over a frozen input set), Tier B anchored (layers L6–L8, deterministic given a pinned external resolver), Tier C judged (protocols P1–P4, reproducible-not-deterministic) — and the funder-facing dossier is required to display each row's tier on its face rather than collapsing to one number.
- **Status**: supported
- **Falsification criteria**: a shipped metric in §4's catalogue that cannot be assigned one of {D, A-R, R-J} (or an explicit mixed tag), or a dossier row in §5 that reports a score without its tier label.
- **Proof**: [E01]
- **Evidence basis**: §1 "Architecture: three rigor tiers over one id-graph" (diagram + prose); §5 Credibility Dossier
- **Dependencies**: none
- **Sources**:
  - `3 tiers (A/B/C)` ← §1 architecture diagram «TIER C · JUDGED ... TIER B · ANCHORED ... TIER A · DETERMINISTIC» [input]
  - `dossier tier labelling` ← §5 «Every rigor class is labelled *on its face*, so no A-R or R-J number is dressed as deterministic» [result]
- **Tags**: architecture, tiers, id-graph, dossier

## C02: Full-density Tier-C judgement costs on the order of 10³–10⁴ judge inferences per mid-size GRO and does not scale to a 100k-paper corpus
- **Statement**: Running P1–P4 fully on every element of a mid-size GRO (~40 claim↔evidence edges) — with P1 ≥3 model families × sealed-N runs, P2 J≥3 judges × R≥3 runs (~12 verdicts) per edge plus INVARIANCE_AUDIT/CALIBRATION_REPORT, P3 ≥5 judges × ≥3 families plus a blind BCR twin ensemble, and P4 K≥3 judges × ≥2 families — costs on the order of 10³–10⁴ judge inferences, and this does not scale to a hundred-thousand-paper corpus at full density.
- **Status**: supported
- **Falsification criteria**: a demonstrated full-density Tier-C run at 100k-corpus scale within the stated cost envelope, or an arithmetic recount from the stated per-protocol multipliers landing outside the claimed 10³–10⁴ order of magnitude for a ~40-edge GRO.
- **Proof**: [E02]
- **Evidence basis**: §9 (Tier C shared machinery), "Cost and scale (must-fix #11)"; §7 "The Tier-C apparatus does not run at corpus scale"
- **Dependencies**: [C01]
- **Sources**:
  - `10³–10⁴ judge inferences` ← §9 must-fix #11 «a mid-size GRO (say ~40 claim↔evidence edges) incurs on the order of **10³–10⁴ judge inferences** if every protocol runs fully on every element. This does **not** scale to a hundred-thousand-paper corpus at full density» [result]
  - `P2 J≥3×R≥3 (~12 verdicts)/edge` ← §9 must-fix #11 «P2 J≥3 × R≥3 (~12 verdicts) *per edge* + INVARIANCE_AUDIT + CALIBRATION_REPORT» [input]
  - `~40 claim↔evidence edges` ← §9 must-fix #11 «a mid-size GRO (say ~40 claim↔evidence edges)» [input]
- **Tags**: cost-model, tier-c, judge-inference, corpus-scale

## C03: Cross-layer provenance uses five distinct hash/normalization regimes with no shared identity
- **Statement**: GRO deliberately runs five distinct provenance/normalization regimes — L1 raw-byte `source_anchor.sha256`, the QUANT canonical-lexer normalization for numeric comparison, L6 `NORM_v1` content/quote hashing, L3 derived-text `text_hash`, and L4's substring-containment double-lock (not a hash) — such that the same quote hashed under L1 and L6 will not match, and cross-layer identity is established only by id reference, never by hash equality.
- **Status**: supported
- **Falsification criteria**: discovery of a single hash function shared across L1/L3/L6/L4 that makes their outputs directly comparable, or a validator that relies on cross-regime hash equality rather than id reference.
- **Proof**: [E03]
- **Evidence basis**: §3 provenance-regime table; §7 "Three provenance regimes, no single cross-layer hash identity"
- **Dependencies**: none
- **Sources**:
  - `5 regimes` ← §3 provenance-regime table rows «L1 `source_anchor.sha256` / L1 numeric comparison (lexer) / L6 `content_hash`/`quote_hash` (`NORM_v1`) / L3 `embedding_anchor.text_hash` / L4 `ledger_ref` double-lock» [input]
  - `no hash equality across layers` ← §3 «the *same* quote hashed under L1 (raw) and L6 (`NORM_v1`) will **not** match, and L4's double-lock is containment, not identity. Cross-layer identity is by **`id` reference**, never by hash equality» [result]
- **Tags**: provenance, hashing, cross-layer, honest-limitation

## C04: Self-reported provenance can only lower, never raise, a novelty confidence score
- **Statement**: In P1 novelty scoring, ensemble agreement produces the base confidence, but a self-reported provenance tag applies a fixed monotone-down-only cap — `reviewer_confirmed` → cap 1.0, `author-authored` → cap 0.6, `ai-suggested` → cap 0.3 — and any upgrade of that cap requires independent machine-checkable evidence (e.g., independent REFGRAPH corroboration), never the self-report itself.
- **Status**: supported
- **Falsification criteria**: a code path in which a self-reported provenance tag raises confidence without an independent corroborating check, or a cap value observed to differ from {1.0, 0.6, 0.3} for the three named tiers.
- **Proof**: [E04]
- **Evidence basis**: §8 P1 "Three blocking fixes," fix (1)
- **Dependencies**: [C01]
- **Sources**:
  - `caps: 1.0 / 0.6 / 0.3` ← §8 P1 fix(1) «reviewer_confirmed → cap 1.0; author-authored → cap 0.6; ai-suggested → cap 0.3» [result]
  - `monotone-down only` ← §8 P1 fix(1) «the provenance ceiling is a cap, never a confidence value, and it can only ever lower a score... So self-report can only ever *hurt* your own score; raising it is independently gated» [result]
- **Tags**: self-report, confidence-ceiling, novelty, anti-gaming

## C05: The "contested" entailment disposition is pinned to floor above refuted, closing the refutation-dilution exploit
- **Statement**: P2's effective-verdict severity lattice is `refuted/contradicted < not_supported < contested < weakly_supported < supported < strongly_supported`; "contested" always floors at the `not_supported` level, and any run yielding a grounded `refuted/contradicted` verdict sets the edge's floor to `refuted` (not `contested`), so a would-be-refuted edge cannot be diluted into "contested" by adding lenient judge runs.
- **Status**: supported
- **Falsification criteria**: an observed edge where a grounded refuted/contradicted run coexists with a final "contested" (rather than "refuted") disposition, or a "contested" score credited above the "not_supported" floor.
- **Proof**: [E05]
- **Evidence basis**: §8 P2 "FIX (must-fix #6) — where the contested floor sits, pinned"
- **Dependencies**: [C01]
- **Sources**:
  - `severity lattice ordering` ← §8 P2 must-fix #6 «`refuted/contradicted < not_supported < contested < weakly_supported < supported < strongly_supported`» [result]
  - `refutation is sticky` ← §8 P2 must-fix #6 «if any run yields `refuted/contradicted` with a valid grounded `evidence_span`, the edge's floor is set to **`refuted`, not `contested`**... Steering a refutation into contested is therefore **not profitable**» [result]
- **Tags**: entailment, contested-floor, anti-gaming, severity-lattice

## C06: True statistical decorrelation is earned only once in the whole system — L3 Arm A
- **Statement**: Of every "independent" verification pass in GRO (L1 `external_fidelity`, L6 `semantic_review`, L7 `CorrespondenceAssessment`, the L7 planned-outcome extractor, and every Tier-C judge panel), only L3's Arm A — a non-LLM literal/synonym matcher — is genuinely decorrelated from the authoring pipeline; every other pass satisfies a four-part `pipeline_independent` test (distinct pipeline id, distinct model family, distinct prompt-lineage hash, packet-only inputs) that is necessary but not sufficient, because it cannot rule out shared-pretraining-corpus correlation between two different LLM families.
- **Status**: supported
- **Falsification criteria**: a demonstrated measurement (not assertion) of statistical independence for any pass other than L3 Arm A, or a documented case where two "pipeline_independent" LLM families produced correlated errors traceable to shared pretraining data, invalidating the "necessary, not sufficient" framing.
- **Proof**: [E06]
- **Evidence basis**: §6 L3 "This is the one place 'decorrelated' is fully earned"; §7 "Independence is pipeline-independence"
- **Dependencies**: none
- **Sources**:
  - `4-part independence test` ← §5 (Tier B intro) must-fix #5 «(i) distinct `authoring_pipeline_id`; (ii) distinct model *family*...; (iii) distinct `prompt_lineage_hash`...; (iv) inputs restricted to the mechanically-assembled packet» [result]
  - `only L3 Arm A decorrelated` ← §7 «Only L3 Arm A (a non-LLM literal matcher) earns genuine decorrelation. A compromised or correlated "independent" pass defeats the corresponding anti-fabrication claim» [result]
- **Tags**: independence, decorrelation, pipeline-independent, honest-limitation

## C07: The undisclosed-prior-art cap is bounded by neighborhood coverage, not a total guarantee
- **Statement**: P1 hard-caps novelty magnitude at "incremental" when the single highest-similarity published-before `q_auto` neighbor is neither cited nor addressed by a typed relation edge; this cap reliably fires only when that predecessor is inside the `q_auto` neighborhood, and because the neighborhood is rebuilt from a post-cutoff snapshot (temporal leakage flagged, not eliminated) and embedding-evasion of `q_auto` is an open question, the cap is not a guarantee against a predecessor the neighborhood evades or misses.
- **Status**: hypothesis
- **Falsification criteria**: any measured rate of embedding-evasion success against `q_auto`, or a documented instance where an in-neighborhood predecessor failed to trigger the incremental cap.
- **Proof**: [E07]
- **Evidence basis**: §8 P1 "Three blocking fixes," fix (2); §7 "The undisclosed-prior-art cap is bounded by neighborhood coverage"
- **Dependencies**: none
- **Sources**:
  - `cap mechanism` ← §8 P1 fix(2) «If the single highest-similarity published-before `q_auto` neighbor is neither cited NOR addressed by a typed relation edge, magnitude is hard-capped at `incremental`» [result]
  - `boundedness` ← §8 P1 fix(2) «this cap **reliably fires when the predecessor is in-neighborhood and reliably spares when it is not**, but it is **not** a guarantee against a predecessor evaded or missed by the neighborhood» [result]
- **Tags**: novelty, prior-art, bounded-defense, honest-limitation

## C08: Genre-shopping defense is deterministic for anchorable genres and a bounded residual for narrative ones
- **Statement**: For anchorable genres, GRO's structural corroborator forces and clears expected slots deterministically, so genre-shopping cannot silently shrink the coverage denominator; for purely narrative genres (empty anchor set) there is no deterministic clear, and a nonzero, magnitude-bounded false-absence residual remains, attributed to a distinct `contested_ttl_lazy_omission` bucket and surfaced as a corpus `classifier_error_signal`.
- **Status**: hypothesis
- **Falsification criteria**: a measured false-absence rate for narrative-genre GROs that is unbounded (grows without a stated ceiling) rather than the claimed magnitude-bounded residual, or evidence that anchorable-genre shopping does shrink the denominator despite the structural corroborator.
- **Proof**: [E07]
- **Evidence basis**: §6 L5 "Over-claim corrected (over-claim #2)"; §7 "Genre-shopping is bounded, not eliminated"
- **Dependencies**: none
- **Sources**:
  - `bounded-not-eliminated claim` ← §6 L5 over-claim #2 «for anchorable genres, shopping cannot silently shrink the denominator... for purely narrative genres (empty anchor set) there is no deterministic clear, so a nonzero residual false-absence remains — floored, magnitude-bounded, attributed to a distinct `contested_ttl_lazy_omission` bucket» [result]
- **Tags**: genre, anti-gaming, bounded-defense, honest-limitation

## C09: Registry outcome-switching detection (M04) is bounded by joinability, not universal
- **Statement**: M04 direction-switch detection requires `planned_direction`/`planned_measure` parsed from free-text registry records and, for numeric switches, a posted registry number that most PROSPERO protocols and many NCT entries do not carry; coverage is reported explicitly as `m04_joinable_rate` / `m04_direction_joinable_rate` rather than assumed, so "publication-bias afforded" is scoped to the joinable fraction of the corpus, not the whole corpus.
- **Status**: supported
- **Falsification criteria**: a corpus audit showing `m04_joinable_rate` is not published/tracked in practice, or M04 being applied/credited on registry entries lacking a posted numeric outcome.
- **Proof**: [E08]
- **Evidence basis**: §5 L1 "registry_ref.registered_value coverage is bounded"; §6 L7 "FIX (must-fix #10)"; §7 "M04 outcome-switching is bounded by extractability and posted-value availability"
- **Dependencies**: none
- **Sources**:
  - `most PROSPERO/NCT lack posted numeric outcomes` ← §5 L1 missing/underspecified #3 «Most PROSPERO protocols and many NCT entries carry *no* posted numeric outcome; for those, `registered_value = not_posted`» [input]
  - `m04_joinable_rate reported not assumed` ← §5 L1 missing/underspecified #3 «The *fraction of corpus where the join is even possible* is reported as `m04_joinable_rate`, not assumed» [result]
- **Tags**: registry, outcome-switching, bounded-coverage, honest-limitation

## C10: Three Class-C blind-reconstruction passes bound (but do not eliminate) the compiler's content-selection residual
- **Statement**: Because determinism cannot close what the compiler chooses to type as load-bearing, GRO adds exactly three Class-C-reproducible (not deterministic) blind-reconstruction passes — `numeral_reconstruction` (L1), `claim_coverage` (L2), and `assumption_coverage`/BCR (P3) — each diffing a firewalled, independent extraction ensemble against the compiler's typed set to surface uncovered load-bearing content, making wholesale non-typing "harder and visible," not impossible.
- **Status**: supported
- **Falsification criteria**: identification of a fourth blind-reconstruction pass claimed to be deterministic (not Class-C), or evidence that wholesale non-typing remains as easy/invisible after the three passes as before them.
- **Proof**: [E01]
- **Evidence basis**: §0 axiom 3; §7 "The compiler selects the content that gets recomputed"
- **Dependencies**: none
- **Sources**:
  - `exactly 3 named passes` ← §7 «Three reproducible blind-reconstruction passes (`numeral_reconstruction`, `claim_coverage`, `assumption_coverage`/BCR) diff an independent extraction against the typed set and score the gap» [result]
  - `bounded not eliminated` ← §7 «Wholesale non-typing is *harder and visible*, not impossible» [result]
- **Tags**: blind-reconstruction, coverage, class-c, honest-limitation

## C11: A separate XQ## ledger resolves the L1/L8 baseline_value id conflict and is exempt from numeral_coverage
- **Statement**: Off-paper (prior-work) numbers are typed into a distinct ledger `external_quantities.yaml` under the `XQ##` id space — never as `Q##` — carrying the prior-work `source_anchor` and a `baseline_verification` block, and `XQ##` records are explicitly exempt from `numeral_coverage`, because that audit governs only numerals appearing in this paper's own prose/tables, not externally-fetched baseline values.
- **Status**: supported
- **Falsification criteria**: an `XQ##` record found subject to `numeral_coverage` scoring, or a `baseline_value` typed as `Q##` rather than `XQ##` in a compiled GRO.
- **Proof**: [E08]
- **Evidence basis**: §3 "FIX (must-fix #3) — the L1↔L8 baseline_value conflict is resolved by a distinct id space"
- **Dependencies**: none
- **Sources**:
  - `XQ## ledger, exempt from numeral_coverage` ← §3 must-fix #3 «off-paper numbers live in a **separate ledger `external_quantities.yaml` under the `XQ##` id space.**... are **exempt from `numeral_coverage`** (which governs only numerals appearing in *this* paper's prose/tables)» [result]
- **Tags**: id-namespace, external-quantities, numeral-coverage, design-fix

## C12: The n-expectation promotion closes the omit-n free pass only above a generality threshold
- **Statement**: For claims tagged with generality `population_estimate` or `claimed_universal`, a populated `n` (or an explicit `n_not_recoverable{reason, anchor}`) becomes an expected slot, so omitting it is scored as a violated expectation (`UNDER_SPECIFIED_EXPECTED`, penalized) rather than protected honest absence; below that generality tier, a missing `n` remains honest absence and is scored neutrally.
- **Status**: supported
- **Falsification criteria**: a `population_estimate` or `claimed_universal` claim observed to omit `n` without an `n_not_recoverable` reason and without being penalized, or a below-threshold-generality claim penalized for a missing `n`.
- **Proof**: [E08]
- **Evidence basis**: §0 axiom 4 "Known tension, now explicit"; §6 L2 "Sharpest defense — the over-claim field-diff, with its expectation promoted"
- **Dependencies**: none
- **Sources**:
  - `n as expected slot above threshold` ← §0 axiom 4 «for any claim whose generality tag is `population_estimate` or `claimed_universal`, a populated `n` (or an explicit `n_not_recoverable` with a reason anchor) is an **expected slot**, so omitting it *is* a violated expectation and is penalized. Below that generality tier, missing `n` remains honest absence» [result]
- **Tags**: over-claim, generality, honest-absence, design-fix
