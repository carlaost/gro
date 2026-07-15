# The Grounded Research Object (GRO) — Unified Format Specification

### A scientific publishing format whose unit of record computes its own credibility, so funders can measure which work is both rigorous and important — and can see exactly where that measurement stops being deterministic

> **Scope of this document.** This is the single normative spec, synthesized from twelve gap-tournament winners (QUANT, CLAIMFOL, ENTITY, EDGES, GENRE, REFGRAPH, REGISTRY, NOVELANCHOR, NOVELSCORE, ENTAIL, VALIDITY, HARDSIGNALS) against the affordance gaps in `AFFORDANCE_GAP.md` and the metric suite in `ALL_METRICS_MERGED.md`. It supersedes the `IDEAL_FORMAT_SPEC.md` draft and is the **post-adversarial** revision: every must-fix from the red-team critique is resolved below either by a design change or by an explicit, labelled demotion to §7 (Honest limitations). Where a claim in the earlier draft was an over-claim, it has been re-tagged in place, not quietly dropped — the changed tag is the record of the fix.

---

## 0. Design axioms

Six rules bind every layer. They are why the format is a credibility engine and not merely a schema. Two of them were sharpened by the critique and now carry explicit boundaries.

1. **Author each load-bearing fact exactly once, as typed data; then bind prose to it in one of two declared modes.** Every load-bearing fact has one canonical typed record; every other mention is a *tagged rendering* that binds back by id. But the binding mode is now **explicit per surface and is itself scored**, because the two modes have different evidentiary value:
   - **RENDER mode** — prose is generated *from* the ledger. Agreement is guaranteed by construction and therefore proves nothing about fabrication; it only guarantees internal consistency.
   - **RECONCILE mode** — prose is authored *independently* of the ledger and a checker verifies agreement after the fact. Only here is view-agreement an anti-fabrication signal.
   Every surface declares `bind_mode ∈ {render, reconcile}`. The anti-fabrication "agreement-between-views" credit (VALIDITY round-trip, EDGES prose-independent reconciliation) is awarded **only for `reconcile` surfaces**, and the count of reconcile-vs-render surfaces is reported, not assumed. The earlier draft's blanket "agreement is an anti-fabrication signal" was an over-claim; it holds only in reconcile mode (see §7).

2. **Deterministic facts and semantic judgements live in physically separate files.** Ledgers and structural checks are pure functions of authored data. Every "does this hold / is this novel / is this realistic" verdict lives in an append-only, content-hashed, judge-authored log that *references* the deterministic skeleton by id and can never be edited into it.

3. **The author/compiler that states a fact never *certifies* it — but it does *select* it, and selection is scored as a bounded, audited residual, not as zero-cost.** Fidelity, resolution, genre, correspondence, and novelty verdicts are produced by *independent* passes, machine-checked for independence (§ below and L3). Self-*assertion* of a verdict defaults to zero credit. **The honest concession the earlier draft buried:** deterministic recomputation is not certification, but the compiler still *chooses the content* that gets recomputed — which numbers are load-bearing, which prose becomes a `C##`, which assertions become nodes. That selection is a residual gaming surface that determinism cannot close. It is attacked by three reproducible *blind reconstruction* passes that diff an independent extraction against the compiler's typed set — `numeral_coverage` (L1), `claim_coverage` (L2, new), `assumption_coverage` / BCR (P3) — and any gap they find is scored. These passes are **Class-C reproducible, not deterministic**; §7 states the residual plainly.

4. **Honest absence is scored equal to honest presence, everywhere — except where a *deterministic expectation* is violated.** `not_specified` / `not_applicable` / `unresolved` / `not_claimed` are first-class, scored equal to a filled field. A typed slot never creates fabrication pressure. Absence is penalized *only* when a deterministic expectation is violated (an expected-and-omitted genre slot, a suppressed comparison, a load-bearing fact recovered by a blind reconstruction pass but absent from the typed set). **Known tension, now explicit:** the L2 over-claim field-diff needs `n` to fire, and `n=null` returns `UNDER_SPECIFIED` scored equal to presence — so omitting `n` is an absence the axiom protects. This is resolved by promoting the *expectation*: for any claim whose generality tag is `population_estimate` or `claimed_universal`, a populated `n` (or an explicit `n_not_recoverable` with a reason anchor) is an **expected slot**, so omitting it *is* a violated expectation and is penalized. Below that generality tier, missing `n` remains honest absence. See L2 and §7.

5. **Everything external is pinned and hashed — but "hashed" is not one hash regime.** Resolvers, index snapshots, blind classifiers, judge ensembles, calibration sets, vocabularies, and taxonomies are versioned, hash-referenced artifacts. Two labs re-running get the same inputs; drift is *measured*, not assumed away. **The critique's cross-layer point, now owned:** there are deliberately *three* provenance/hash regimes (raw-byte `source_anchor.sha256` at file+range for L1; `NORM_v1` content/quote hashing for L6; derived-text `text_hash` for L3), plus the QUANT lexer normalization for numeric comparison and L4's substring double-lock (not a hash). No single provenance identity spans all layers, and the spec no longer pretends one does — see the provenance-regime table in §3 and §7.

6. **Gaming is defeated structurally where it can be, and *bounded and surfaced* where it cannot.** Length never scores (every metric is a ratio or a join, not a count). Every self-certifiable field is split into a deterministic axis plus an independently produced one. Each named exploit hits a specific defense in the layer that owns it. Where a defense is *bounded* rather than *total* (narrative-genre shopping, embedding-evasion of the novelty neighborhood, non-load-bearing numeral dumping, content-selection), the bound is named at the metric and repeated in §7 — "never" claims that the critique falsified have been demoted to "bounded."

---

## 1. Architecture: three rigor tiers over one id-graph

```
                          ┌───────────────────────────────────────────────────────┐
   TIER C · JUDGED        │ P1 Novelty/Significance    P2 Typed-Rubric Entailment   │ reproducible,
   (irreducibly semantic) │ P3 Realism/Validity        P4 Frontier/Triangulation    │ human-calibrated,
   append-only, hashed    │ + blind reconstruction diffs (claim/assumption/numeral) │ transcript-hash = truth
                          └───────────────────────▲───────────────────────────────┘
                                                  │ reads by id; verdict ids NOT in the compile-time projection
                          ┌───────────────────────┴───────────────────────────────┐
   TIER B · ANCHORED      │ L6 Reference Spine   L7 Registry Join   L8 Delta/SOTA   │ reliable given a
   (external resolution)  │ ── resolve ids to the outside world ──                  │ PINNED resolver;
   pinned resolvers,      │ shared VerificationRecord CORE + per-target profiles    │ failures quarantined
   quarantined judgement  └───────────────────────▲───────────────────────────────┘
                                                  │ references by id
                          ┌───────────────────────┴───────────────────────────────┐
   TIER A · DETERMINISTIC │ L1 Quantity Ledger   L2 Claim Logical Form              │ exact + reproducible
   (the computable core)  │ L3 Entity Spine*     L4 Cross-Layer Graph   L5 Genre*   │ DOWNSTREAM of a
   one canonical record   │ registry_authority reconciles the id namespace (Tier A) │ frozen input set;
   per fact, addressed by id  *L3 resolution and L5 label are A-R/pinned, not pure  │ pure functions
                          └───────────────────────────────────────────────────────┘
```

**Tier A** makes the facts the artifact already contains *computable* — pure functions of authored data, exact and reproducible **given a frozen input set**. The critique's correction is folded in: some Tier-A *metrics* consume upstream inputs that are themselves A-R (L3 `resolved`, the compiler's semantic lowering into logical form). Those metrics are deterministic *downstream of* the frozen LLM-authored inputs, not end-to-end. The catalogue in §4 now tags this explicitly. **Tier B** reaches outside the artifact; identity resolution is deterministic given a pinned resolver, the irreducible judgement is quarantined and audited, every failure mode is a first-class honest state. **Tier C** answers what no format change makes deterministic; it is *reproducible and auditable* — reading the deterministic graph, never authoring it, verdicts in append-only content-hashed logs.

---

## 2. The unit of record

A GRO is a directory. It keeps ARA's progressive-disclosure prose (readable `PAPER.md`, drill-down layers) — prose is the strength for the human reader and for the Tier-C judges — but every load-bearing fact *also* exists as a typed record the prose binds to (render or reconcile, §0.1). File inventory:

```
GRO://{id}/
  PAPER.md                         # root manifest; each prose surface declares bind_mode
  meta.yaml                        # NEW: paper_type (→L5), discipline_ref (→§3 discipline ledger)
  logic/
    quantities.yaml                # L1  QUANT      — canonical typed numbers  (Q##)
    external_quantities.yaml       # L1' NEW       — prior-work / off-paper numbers (XQ##)
    claims.md                      # L2  CLAIMFOL   — prose + one **Logical form** line per C##
    claim_graph.yaml               # L2  DERIVED, hash-gated AST (never hand-authored)
    entities.yaml                  # L3  ENTITY     — one record per mechanically-referenced entity
    symbol_table.yaml              # L3  DERIVED bijective fol_symbol ↔ entity id
    experiments.md                 # typed experiment schema (arms/baselines/metrics)  (E##)
    problem.md                     # observations O##, gaps G##
    contributions.yaml             # L8  NOVELANCHOR — contributions  (CT##)
    delta_ledger.yaml              # L8  NOVELANCHOR — comparative deltas  (D##)
    sota_anchor.yaml               # L8  NOVELANCHOR — resolver-produced precedence neighborhood
    solution/
      constraints.md               # reconcile-mode surface against ↓
      validity/                    # P3 VALIDITY plane-1 sidecar (assumptions/limitations/methods/…)
      heuristics.md                # P4 shortcut_dimension / ideal_counterfactual / frontier_ref
    genre.yaml                     # L5  GENRE      — declared type + verbatim anchor (rest COMPUTED)
  refs/
    reference_spine.yaml           # L6  REFGRAPH   — one canonical work  (R###)
    citation_mentions.yaml         # L6  REFGRAPH   — one occurrence  (CX####)
    support_edges.yaml             # L6  REFGRAPH   — one support edge  (SREF###)
    resolution_candidates.yaml     # L6  falsifiable per-candidate scores
  registry/
    accessions.yaml + manifest.yaml# L7  REGISTRY   — accessions (ACC-*), registered outcomes (OUT##)
    access_tiers.yaml              # L7  per-component access matrix
    claim_registry_links.yaml      # L7  the JOIN KEY: every C## ↦ exactly one outcome_id
    outcome_coverage.yaml          # L7  DERIVED selective-reporting ledger
    planned_outcome_extraction/    # L7  NEW: Class-C structured extraction of planned_* from free text
  graph/
    nodes.yaml                     # L4  EDGES      — PROJECTION over Tier-A ledgers (mints nothing)
    edges.yaml                     # L4  typed edges (computed fingerprint/status/verdict_ref)
    frontier.yaml + perspectives.yaml + triangulations.yaml   # P4 HARDSIGNALS
  evidence/  data/  src/           # tables, figures, datasets, code (as the genre warrants — L5)
  trace/
    verdicts/                      # TIER C append-only, content-hashed, judge-authored
      entailment_verdicts.yaml     # P2
      licensing_signals.yaml       # L4 anchor-licensing signals (never gate inline)
      novelty_report.yaml          # P1
      validity_panel/{run_id}.yaml # P3
      frontier_panel/…             # P4
      coverage_reconstruction/     # NEW: claim/assumption/numeral blind-diff results (Class-C)
    exploration_tree.yaml          # research DAG (ARA's best-shaped artifact, retained)
```

The **decisive structural invariant**: the two write-surfaces never touch. The compiler writes Tier-A/B *skeleton* facts it can ground; independent resolver, extraction, classifier, and judge passes write everything that certifies those facts, into physically separate append-only files. A validator (`written_by` discipline, REFGRAPH V9–V11) *forbids* the compiler from ever writing a resolution confidence, a fidelity verdict, a match hash, or a judge vote.

---

## 3. Shared, non-conflicting ID namespace

Every layer addresses every other layer through one registry; each id pattern has exactly one owning ledger; and EDGES' **`registry_authority`** table (type → owning file) makes disagreement a hard-fail — **for the Tier-A id space it governs** (scope now bounded explicitly, below).

| ID pattern | Owning ledger | Layer | What it names |
|---|---|---|---|
| `Q##` | `logic/quantities.yaml` | L1 | one canonical typed quantity **stated in this paper** |
| `XQ##` | `logic/external_quantities.yaml` | L1′ | one **off-paper** number (prior-work reported value, external baseline) |
| `C##` | `logic/claims.md` | L2 | one claim (prose block + logical-form line) |
| *(cg-nodes)* | `logic/claim_graph.yaml` | L2 | DERIVED AST conjuncts (hash-gated, never authored) |
| `E##` | `logic/experiments.md` | L4 | one experiment / analysis plan |
| `O##`,`G##` | `logic/problem.md` | — | observations, gaps |
| `EN-<kind>-<slug>` | `logic/entities.yaml` | L3 | one entity (concept/method/measure/variable) |
| *(fol_symbol)* | `logic/symbol_table.yaml` | L3 | DERIVED bijective FOL symbol for an `EN-*` |
| `DISC-<code>` | `meta.yaml` → `discipline_vocab@vN` | **meta** | one **discipline** label (NEW; see below) |
| `R###` | `refs/reference_spine.yaml` | L6 | one distinct cited **work** |
| `CX####` | `refs/citation_mentions.yaml` | L6 | one citation **occurrence** |
| `SREF###` | `refs/support_edges.yaml` | L6 | one support edge (occurrence → claim/gap) |
| `ACC-<reg>-<id>` | `registry/accessions.yaml` | L7 | one real-world accession (NCT/CRD/GSE/phs/DOI) |
| `OUT##` | `registry` (`registered_outcomes`) | L7 | one registered outcome |
| `CT##` | `logic/contributions.yaml` | L8 | one contribution |
| `D##` | `logic/delta_ledger.yaml` | L8 | one comparative-delta claim |
| *(edge fingerprints)* | `graph/edges.yaml` | L4 | one typed cross-layer edge |
| *(verdict ids)* | `trace/verdicts/*` | Tier C | one judged verdict (append-only, **outside `registry_authority` scope**) |

**Namespace reconciliations forced by the merge:**

- **`X` overload resolved:** entities are `EN-<kind>-<slug>`; citation occurrences are `CX####`.
- **`E` overload resolved:** experiments keep `E##`; entities carry `EN-`, referenced from L2 slots as `EN-*`, never bare `E`.
- **`R###` vs `RW##`:** L6 owns the canonical work id `R###`. NOVELANCHOR's `RW##` are **views onto `R###`**. One citation identity.

**FIX (must-fix #2) — the `discipline` field now has an owner.** The critique correctly found that P1's entire cross-discipline funder proposition rested on a `discipline` field no layer emitted. It is now a first-class field: `meta.yaml` carries `discipline_ref: [DISC-*]` (one or more), drawn from a pinned ecosystem `discipline_vocab@vN` (a closed, versioned taxonomy — e.g. an OECD Fields-of-Science-derived enum). It is set by the same pinned GENRE-style blind classifier that sets `paper_type` (majority-vote ensemble, `prompt_sha256`, τ, floor), **not** self-declared by the compiler, and its confidence is reported. Discipline is therefore an **A-R (pinned-reproducible) label, not deterministic**, and every P1 metric that keys on it (percentile CDF, per-discipline isotonic calibration) inherits that class — reflected in §4 and the dossier. Where the classifier cannot resolve a discipline above τ (interdisciplinary/frontier work), `discipline_ref = contested` and cross-discipline percentile ranking is **withheld** for that GRO rather than faked (see §7).

**FIX (must-fix #3) — the L1↔L8 baseline_value conflict is resolved by a distinct id space.** The critique showed that `baseline_value` (a *prior work's* externally-fetched number, carrying a `fetch_timestamp` on someone else's reported value) cannot be a `Q##` without breaking L1's definition ("each load-bearing number authored once *in this paper*") and its `numeral_coverage` audit. **Resolution chosen and stated:** off-paper numbers live in a **separate ledger `external_quantities.yaml` under the `XQ##` id space.** `XQ##` records carry the prior-work `source_anchor` (external DOI/receipt + `fetch_timestamp`) and a `baseline_verification` block, and are **exempt from `numeral_coverage`** (which governs only numerals appearing in *this* paper's prose/tables). L8 `delta_ledger.magnitude`: `claimed_value` is a `Q##` (this paper's number), `baseline_value` is an `XQ##` (the prior work's number). The delta formulas resolve both to canonical units before arithmetic. "Quantities are cited, never copied" now reads precisely: *this-paper* numbers are cited as `Q##`, *off-paper* numbers as `XQ##`; neither is ever retyped, and the two never collide in `numeral_coverage`.

**Provenance-regime table (must-own cross-layer conflict).** There is no single hash identity across layers, by design; here is the honest map:

| Layer | What is hashed / normalized | Regime |
|---|---|---|
| L1 `source_anchor.sha256` | raw bytes at file + `line_range` | raw SHA-256 |
| L1 numeric comparison | printed literal → QUANT canonical lexer (NFKC → grouping/decimal/dash/exponent fold → comparator/percent split → precision recovery → round-half-even) | lexer normalization (not a stored hash) |
| L6 `content_hash` / `quote_hash` | `sha256(NORM_v1(extract_text(bytes, extractor_id)))` | `NORM_v1` (NFKD-fold/lowercase/whitespace-collapse) |
| L3 `embedding_anchor.text_hash` | over **derived** text from provenanced fields | `text_hash` over derived text |
| L4 `ledger_ref` double-lock | edge-attr ⊆ quote ⊆ ARA-internal text | **substring containment, not a hash** |

The consequence the draft hid and now states: the *same* quote hashed under L1 (raw) and L6 (`NORM_v1`) will **not** match, and L4's double-lock is containment, not identity. Cross-layer identity is by **`id` reference**, never by hash equality. §7 carries this as a named limitation.

**FIX (must-fix #4) — `registry_authority` scope over Tiers B and C is now explicit.** `registry_authority` governs **only the Tier-A id space** (`Q##/XQ##/C##/E##/EN-*/…` and the Tier-B *skeleton* ids the compiler mints, `R###/CX####/ACC-*/OUT##/CT##/D##`). `graph/nodes.yaml` is a **compile-time projection over exactly this governed set** and mints nothing; STRUCTURAL-CHECK step 0 (REGISTRY-RECONCILE) hard-fails the artifact (`registry_desync`) on any projection/ledger disagreement over a *governed* id. **Tier-C verdict ids are explicitly out of scope.** They are minted *after* compile time by independent judges into append-only logs, and they are **never projected into `nodes.yaml`**. Edges that need a verdict carry a `verdict_ref` that resolves *out to* the append-only log at read time (a late-binding pointer), not an id the projection must contain. This preserves both invariants simultaneously: (a) "every governed `from`/`to` resolves against a provably faithful projection," and (b) "judges ride the graph by id, never author it" — a judge writing a verdict never adds a node or edge; it only appends a record that an existing edge's `verdict_ref` points at. The earlier draft left this scope undefined; the exemption is now stated, not latent.

---

# TIER A — the deterministic core (downstream of a frozen input set)

Pure functions of authored data. Every metric here is exact and reproducible **once its upstream inputs are frozen**; where an input is itself A-R (L3 `resolved`, semantic lowering), the metric's class is annotated in §4.

## L1 · Quantity Ledger — *canonical typed numbers with rounding-aware, lexer-pinned binding* (QUANT)

**Kills:** one load-bearing number re-typed up to four times; reconciliation degraded to fuzzy string-matching of copies.

**Emits.** Each load-bearing *in-paper* number is authored once in `logic/quantities.yaml` (`Q##`); each load-bearing *off-paper* number once in `external_quantities.yaml` (`XQ##`). Prose/tables/tree carry an inline tag next to a context-rounded literal — `0.859 [[Q:Q07]]`; table cells bind via `.qids.yaml` sidecars; each claim block carries a `Quantities:[QID]` self-check. Provenance lives once as `source_anchor{file, typed-locator, quote, line_range, sha256}`.

**Schema core.** One full-precision `value:number` (**never** a frozen string) + `uncertainty`, `unit{code,na}`, `comparator/comparator_value`, `baseline_ref`, `direction`, `role`, `derivation{kind,derived_from,formula,tolerance{abs,rel}}`, `format_spec`, `registry_ref{fetch_log, registered_value?}`, and `ranking_ref{ranking_id,rank,rank_polarity,surrogate_is}`. `raw_repr = render(value,format_spec)` survives **only** as the ledger's default rendering.

**Reconciliation (rounding-aware).** Per mention: lex the printed literal to `(printed_number, printed_precision)`; assert `round_half_even(value, printed_precision) == printed_number`; tolerance = 0.5 ULP of the last printed place, read from the print. Table `0.859`, abstract `0.86`, discussion `~0.86` all pass against one `value`.

**Canonical lexer spec.** NFKC; strip declared locale grouping separators only in valid 3-digit positions and coerce decimal separator to `.`; fold Unicode dashes/minus to `-`, `E`→`e`; split leading `~≈<>≤≥±` and trailing `%` into comparator/percent tokens. Precision recovery: (a) decimal point → precision = fractional-digit count incl. trailing zeros; (b) bare integer → EXACT-to-unit (0dp) UNLESS an approx marker is present, then leading-significant-figures; (c) scientific → mantissa fractional digits, require exponent equality; (d) percent → precision in the percent domain. Rounding is round-half-even, matching `render()`.

**Anti-laundering mandate.** Each `Q##` designates a `canonical_mention` = the highest-precision mention (normally the source table cell), checked at full printed precision AND the exact locus the independent fidelity pass re-derives. A mention printing more digits than `value` carries is a defect; a coarse mention can never be the sole check.

**`numeral_coverage` — and its honest residual (must-fix #8).** The audit forces every numeral in *this paper's* prose/tables to be tagged, matched, or explicitly listed non-load-bearing. **The critique's true finding is conceded:** the `non_load_bearing[]` list is *self-declared* and the audit only checks the trichotomy, not the truthfulness of the "non-load-bearing" label — a wrong or inconvenient number can be dumped there. Mitigations now specified, and the residual named: (a) each `non_load_bearing` entry MUST carry a machine-checkable `reason ∈ {enum}` (page-furniture / date / sample-id / citation-year / axis-tick / duplicate-of[Q##]) with an anchor, and out-of-enum reasons are rejected; (b) a Class-C blind pass (`numeral_reconstruction`, in `coverage_reconstruction/`) independently flags any listed numeral that appears inside a *comparative or result* sentence and routes it to `contested_non_load_bearing`, which scores against the honesty ledger. This makes dumping *costlier and visible* but **does not make it deterministically impossible** — the residual self-declared surface is listed in §7.

**Two orthogonal axes (the fabrication firewall).** `reconcile_status ∈ {internally_reconciled, pending, disputed}` (Class-A deterministic; `disputed` auto-set) versus `external_fidelity{state, infidelity_type, paper_quote, checked_by_pass}` writable **only** by the independent adversarial pass mapping 1:1 onto on-disk `extractive_fidelity.py`. The worked example — internally byte-perfect yet `unfaithful MD=0.10` (the real che26 C01 fabrication) — shows internal consistency and paper-fidelity are separately measured. **Grounding-to-source is therefore A-R, not D**, and the dossier now says so (must-fix #1).

**`registry_ref.registered_value` coverage is bounded (missing/underspecified #3).** The join to a posted registry number only runs where the registry actually exposes one. Most PROSPERO protocols and many NCT entries carry *no* posted numeric outcome; for those, `registered_value = not_posted` (honest absence, scored neutral) and the M04 numeric join simply does not run. The *fraction of corpus where the join is even possible* is reported as `m04_joinable_rate`, not assumed — "publication-bias afforded" is scoped to that rate (§7).

## L2 · Claim Logical Form — *one authored logical line; everything richer is derived* (CLAIMFOL)

**Kills:** claims are prose with a `Status` but no `claim_type`, no logical structure, no over-claim measurement.

**Emits.** One `**Logical form**` field per claim in `logic/claims.md`: a single grammar-constrained DSL line (the ONLY authored logical artifact) plus a *derived* pretty ∀-render. All richer structure is a pure function of that line.

**Schema core.** (1) `claim_graph.yaml` — DERIVED, hash-gated AST: shallow-DNF conjuncts (depth-1, AND with guarded OR + OR-node solver semantics), each carrying predicate + polarity + typed args, a comparator that *lowers to an interval constraint* over `Q##`/`XQ##`, and a Comparability Key; fields `well_formed`, `dsl_source_hash`, `unresolved_bindings[]`, `type_honesty_ok`. (2) `predicate_vocab@vN.yaml`. (3) `commensurability@vN.yaml` + per-comparator **Comparability Key**. (4) `populations.yaml` — generality ladder {sample < cohort < multi_cohort < population_estimate < claimed_universal} + over-claim rule table. (5) typed experiment schema + `claim_type_rubric.yaml` with boolean `require`.

**The Comparability Key** is the decisive safeguard: the numeric-SAT pass compares only constraints sharing a CK, so it cannot "prove a contradiction" between an accuracy and a runtime. CK conversions default to `not_permitted`, erring to honest `not_comparable`.

**Determinism split — corrected (over-claim #1, #7).** DETERMINISTIC (Class A): parse + typecheck of the authored DSL; source-hash + CI regenerate-and-diff coherence gate; CK-gated numeric interval SAT (UNSAT ⇒ contradiction candidate with minimal-infeasible-subset witness); symbolic polarity/comparator contradiction; over-claim field-diff; type↔predicate integrity; rubric selection. **Explicitly conceded, not tagged D at the funder surface:** whether the logical form *faithfully captures the paper's claim* is prose↔FOL fidelity — **Class B/C, the real fabrication surface.** Therefore "0 contradictions" and "FOL-ability" are deterministic statements about *the compiler's own logical forms*, not about the paper. A compiler emitting weak/vacuous forms deterministically yields zero contradictions and high FOL-ability. The over-claim field-diff catches quantifier *inflation* but **not under-formalization**. Two defenses now attach to the content, not just the wrapper: (a) a `vacuity_check` — a logical form with no comparator, no quantified variable bound to a population, and no predicate above arity-1 is flagged `low_content` and *excluded from* the "0 contradictions" credit rather than silently boosting it; (b) `claim_coverage`, below. The §4 tags for M08/M09 are downgraded to **D (form) + A-R/R-J (fidelity)**.

**Sharpest defense — the over-claim field-diff, with its expectation promoted (axiom-4 tension, cross-layer #5).** The self-declared generality tag is not the score input: the verdict diffs the quantifier against `n` + `source_count` resolved to the data layer. Mislabeling a universal claim as "cohort" still trips forall-over-sample. **Fix for the omit-`n` free pass:** for `population_estimate`/`claimed_universal` claims, a populated `n` (or explicit `n_not_recoverable{reason, anchor}`) is an **expected slot**; omitting it is a *violated expectation* (`UNDER_SPECIFIED_EXPECTED`, penalized), not protected honest absence. Below that tier, missing `n` stays honest-equal. `NONE`/`not_specified` scored equal to a present form elsewhere.

**`claim_coverage` (must-fix #7) — new.** L4 node-set coverage closes *relabeling* but not *wholesale non-typing*: a claim buried in prose and never given a `C##` becomes no node and is invisible. There is no way to make "every prose assertion is typed" *deterministic* (that is the extraction problem itself), so this is a **Class-C reproducible** pass, honestly classed: a blind claim-extraction ensemble (firewalled from the typed set, `NORM`-templated, ≥3 model families) reconstructs load-bearing assertions from `PAPER.md`, filters to load-bearing, and diffs against the `C##` set → `uncovered_load_bearing_claims`, fed to the honesty ledger. The §4 claim is corrected accordingly: node-set coverage **closes relabeling deterministically; wholesale non-typing is caught only by this reproducible blind diff, not deterministically** (§7).

## L3 · Entity Spine — *stable ids + ontology xrefs + decorrelated resolution* (ENTITY)

**Kills:** concepts/methods/variables are prose headings; nothing maps them to controlled vocabulary.

**Emits.** `logic/entities.yaml`: one record per entity *mechanically referenced by another layer*. Each carries a stable `EN-<kind>-<slug>`, a deterministic `fol_symbol` (bijective in `symbol_table.yaml`), optional `xrefs`, an `embedding_anchor` (over derived provenanced text), `resolution_attempted`, computed `resolution_status`. All other layers cite by id.

**Deterministic vs reproducible.** Inclusion is a validator rule (compile fails on any dangling ref — *no agent controls the M10 denominator*). `resolution_status` is a pure function of an append-only log via a written state machine. The only LLM step is semantic Arm B; reliability comes from **decorrelated corroboration** — an xref reaches `verified_exact` only when a **NON-LLM literal/synonym matcher (Arm A)** and the semantic linker independently converge, with thresholds from a shared `resolver_calibration.yaml`. `raw_score` is audit-only.

**This is the *one* place "decorrelated" is fully earned (must-fix #5).** Arm A is a genuine non-LLM literal matcher against the vocabulary's own labels, so correlated hallucination *structurally* cannot manufacture an Arm-A hit and broad terms cannot earn one. Every *other* "independent" pass in this spec (L1 `external_fidelity`, L6 `semantic_review`, L7 `CorrespondenceAssessment`, all Tier-C panels) is **another LLM**, and its correlation with the author LLM is **asserted by construction (distinct pipeline id / family / prompt lineage), not measured.** Throughout this document the word "decorrelated" is now reserved for L3 Arm A; every other independence claim is stated as **"pipeline-independent (necessary, not sufficient)"** — see the independence definition below and §7.

**Three imports the merge preserves.** *Graded corroboration:* strong/weak/none verdict; `corroboration=none` downgrades credit to 0 *while the ref still joins M13 and surfaces as over-citation* — never silent-drop. *Commons demotion:* `global_entity_id`/cross-ARA recognition are UNSCORED diagnostics, excluded from M10/M12/M13/M64. *Re-anchoring migration:* `reproducibility_check` is a five-state machine {pass, model_migrated, text_changed, forged, stale}; `forged` is ONLY same-model/same-text mismatch and scores absent.

## L4 · Typed Cross-Layer Graph — *the artifact as a real multigraph* (EDGES)

**Kills:** the id system supported only *existence* binding.

**Emits.** Per-GRO `nodes.yaml` (a compile-time PROJECTION over the *governed* Tier-A/skeleton id set, §3) and `edges.yaml` (typed edges with computed fingerprint/`structural_status`/`verdict_ref`); ecosystem `edge_schema.yaml`; versioned `nullability.yaml`/`acyclicity.yaml`; imported `quantity_interface.md`; physically-separate append-only `entailment_verdicts.yaml` + `licensing_signals.yaml`.

**Five hardenings that make "deterministic" real:**
1. **Node-id authority** (§3, scope now bounded to Tier A + skeleton): REGISTRY-RECONCILE hard-fails on any projection/ledger disagreement over a governed id; Tier-C verdict ids are out of scope and reached by late-binding `verdict_ref`.
2. **Coverage over the node set — with its bound stated:** COV1/COV2/COV3 are computed over NODES, closing the *relabeling* omission attack (a speculative claim still declares `claim_type`, stays under the rubric, lands in a `covered_by_waiver` bucket that *lowers* testability coverage — relabeling is visible and costed). **What it does NOT close:** a fact never typed at all. That residual is caught only by the Class-C `claim_coverage`/`assumption_coverage` blind diffs (L2, P3), not deterministically.
3. **One trust-tier semantics:** `trust_tier_map` collapses edge `declared_by`, tree `support_level`, code `Grounding` onto AUTHOR_STATED > DERIVED > INFERRED; `rubric_satisfaction_policy` in canonical tiers (min DERIVED; INFERRED barred).
4. **Deterministic gate, LLM demoted:** test-adequacy is gated SOLELY by node_ref grounding (feature resolves to a type-legal Method/Evidence node at trust ≥ DERIVED); zero LLM. ANCHOR-VERIFY Part B is demoted to append-only, stale-on-mutation `licensing_signals.yaml` that MUST NOT gate any edge. Metrics: **test-adequacy (grounded)** + **feature-licensing rate (signal)**.
5. **Value-less `ledger_ref` double-lock + ceiling:** the checker verifies edge-attr ⊆ quote ⊆ ARA-internal text (**INTERNAL** correspondence, metric renamed **internal numeric reconciliation** — *not* source fidelity). A value-less `measures` `ledger_ref` reconciles role=result, producer-experiment agreement, and completeness (COV2).

## L5 · Genre Contract — *absence becomes declared, checkable, and bidirectionally corroborated* (GENRE)

**Kills:** genre-conditionality expressed as *silent absence*; `domain` free text.

**Emits.** (1) Ecosystem `genre_taxonomy.vX.yaml`: closed `paper_type` enum (+`other`); two-tier slot vocabulary; exhaustive `expectation_table[type][slot] ∈ {expected | not_applicable | expected_if(predicate_id)}`; typed **non-LLM** `predicate_defs`; a fully pinned `classifier_manifest` (ensemble model_ids + `prompt_sha256` + temp0 + seed, inputs {title, abstract, venue_article_type}, majority_vote, τ, floor) — **which also emits `discipline_ref` into `meta.yaml`** (§3); a non-LLM `structural_corroborator`. (2) Per-GRO `genre.yaml`: compiler writes only `paper_type_declared` + ≥1 verbatim anchor; everything else COMPUTED.

**Determinism split.** The genre *label* is Class-C made *reproducible* by pinning. `paper_type_structural` is Class-A: type *t* iff EXACTLY ONE type's anchor set matches (else null). Adjudication over {declared, blind} sets `genre_resolution ∈ {agreement | cleared_structural_to_declared | refuted_structural_to_blind | contested_anchorless}`.

**The corroborator does bidirectional work.** *CONTESTED-CLEAR:* structural == declared ≠ blind → collapse to {declared}, relax to `expected_set(declared)`, no TTL; the mirror (structural == blind) resolves strict immediately, closing shop-and-coast. Only `contested_anchorless` runs a **meet + TTL** (flip fires only on anchorless slots; two owned clears precede TTL). On disagreement, scoring uses the **union (meet) of both genres' expected sets**.

**Over-claim corrected (over-claim #2).** The draft's "genre-shopping can never silently shrink the denominator" was falsified by its own narrative-genre carve-out. Corrected claim: **for anchorable genres, shopping cannot silently shrink the denominator (structural corroborator forces and clears slots); for purely narrative genres (empty anchor set) there is no deterministic clear, so a nonzero residual false-absence remains — floored, magnitude-bounded, attributed to a distinct `contested_ttl_lazy_omission` bucket, and surfaced as a corpus `classifier_error_signal`.** "Never" is now "bounded for anchorable genres, a bounded and surfaced fudge for narrative ones" (§7).

**Metrics:** deterministic coverage over the meet; `silent_omission_count` (Level-1 gate); decoupled `warrant_integrity_score`; TTL-bounded `provisional_debt`; `classifier_error_signal`.

---

# TIER B — anchor layers (reliable, not deterministic)

Deterministic *given a pinned resolver*; the irreducible judgement quarantined; every failure mode a first-class honest state.

**Shared verification core (must-fix #9) — one core, two profiles, not one enum.** The draft claimed a single hoisted `VerificationRecord`; the critique correctly showed L6 and L7 carry *incompatible* result enums and hash regimes. Resolution: a shared **abstract `VerificationRecordCore`** carries the fields that genuinely are identical — `method`, `snapshot_ref`, `snapshot_sha256`, `next_check_due`, append-only `verification_history`, and a shared **outcome lattice** `{resolved_match, mismatch, ambiguous, unreachable, not_checked, not_applicable}`. Two **profiles extend it**, and the spec no longer pretends the extensions unify:
- **`RefVerification` (L6)** adds `content_hash`/`quote_hash` under `NORM_v1(extract_text(bytes, extractor_id))`, and two *domain* states `{pending, grey_lit}` that map onto the core lattice for scoring (`pending→not_checked`, `grey_lit→not_applicable`).
- **`RegistryVerification` (L7)** adds `registry_record_hash` (over the fetched registry record), and `not_found` maps to core `mismatch`-adjacent `unreachable`/`mismatch` per a documented rule.

So there is **one shared outcome lattice and one cadence/history model** (that is the real reuse), but **two hash regimes and two domain-state extensions** (that is the real difference). The document describes them as *"a shared core with two related-but-distinct profiles,"* not "one type."

**The independence mechanism, specified (must-fix #5, missing #4).** "Machine-checked independence" now has a precise, verifiable definition used identically by L1/L6/L7/P1–P4: a pass is `pipeline_independent` of authoring iff **all** hold and are checked from logged manifests — (i) distinct `authoring_pipeline_id`; (ii) distinct model *family* (not merely distinct deployment); (iii) distinct `prompt_lineage_hash` (no shared prompt ancestor); (iv) inputs restricted to the mechanically-assembled packet, not the compiler's free prose. This is **necessary, not sufficient**: it rules out the trivial self-certification and shared-prompt collusion, but it **cannot** rule out shared pretraining-corpus correlation between two different LLM families — that correlation is *asserted, not measured*, everywhere except L3 Arm A (which is non-LLM and therefore genuinely decorrelated). Every downstream claim is worded to this strength; §7 states the residual.

## L6 · Resolved Reference Spine — *every citation resolves to a real external id* (REFGRAPH)

**Kills:** DOIs live only in full related-work blocks; present DOIs are format-checked, not resolved.

**Emits — three object types joined on ids:** `reference_spine.yaml` (`R###`, resolved external ids + first-class resolution status); `citation_mentions.yaml` (`CX####`, exact `surface_text` → `R###`; prose renders as `[Janelidze et al., 2023](ref:R014)`); `support_edges.yaml` (`SREF###`, occurrence → claim/gap). `resolution_candidates.yaml` logs every candidate with per-signal scores.

**Four fixes.** *Division of labor (`written_by`):* the LLM compiler emits ONLY the groundable skeleton (`R###` ledger, inline tokens, `surface_text`, bibliographic fingerprint, canonical ids only where literally printed) with `resolution_status=pending`, resolver/verifier fields null; scored NEUTRAL. Validators **V9–V11 FORBID** the compiler from writing `match_confidence`, `resolved_fingerprint`, `content_hash`, `retrieval_receipt`, `quote_hash`, or judge votes. *Anchor discipline:* Class-B deterministic `anchor_check` + Class-C quarantined `semantic_review` (an LLM pass, `pipeline_independent`, *not* decorrelated — §7); `quote_hash` null unless a `retrieval_receipt` with `content_hash` is present AND `anchor_check` confirms verbatim substring. *Pinned hashing (`NORM_v1`).* *Bibliography-sourced queries:* resolver query built from the reference-list entry, not the bare inline mention; `query_source` logged; verified/mismatch/ambiguous require `query_source != inline_only_insufficient`.

**Sharpest defense:** reward attaches to distinct VERIFIED works that ANCHOR claims — re-citing inflates `CX` not `R`; honest pending/unresolved/grey_lit score equal to resolved.

## L7 · Registry Join Layer — *accessions become verifiable join keys; outcome-switching becomes visible* (REGISTRY)

**Kills:** resolvable ids trapped in prose, unlinked to claims, never checked against the issuing registry; outcome-dropping hidden between registered and reported.

**Emits.** `accessions.yaml`/`manifest.yaml` (registry enum, kind, accession, `registered_by`, `prospective_or_retrospective`, genre-gated `registration_expectation`, per-entry `registered_outcomes`); `access_tiers` objects; a `RegistryVerification` profile (above); `claim_registry_links.yaml` — the **JOIN KEY** tying a `C##` to a registered `OUT##`, coverage-complete; DERIVED hash-stamped `outcome_coverage.yaml`.

**FIX (must-fix #10) — planned_direction/planned_measure extraction is now a *designed, honestly-bounded* step, not a hidden assumption.** The critique correctly found M04 presumed structured `planned_direction`/`planned_measure` that registries store as **free text**. Parsing them out is itself Class-C semantic extraction. It is now designed in `registry/planned_outcome_extraction/`: a **`pipeline_independent`** (necessary-not-sufficient) extraction ensemble reads the *fetched registry record snapshot* (not the paper) and emits `RegisteredOutcome.planned_direction`/`planned_measure` with `evidence_span` substring-validated against the snapshot, `confidence`, and an `extractable ∈ {structured, parsed_from_free_text, not_extractable}` flag. The subsequent `field_comparison` (planned vs reported direction) is deterministic **given** the extracted fields. **Coverage is bounded and reported, not assumed:** M04 direction-switch detection runs only where `extractable != not_extractable`; the `m04_direction_joinable_rate` is published. M04 is therefore tagged **A-R (extraction) + D (comparison given extraction), bounded by joinable-rate** — not a blanket "afforded."

**Schema the merge combines:** manifest-level `registered_outcomes` + `outcome_coverage.yaml` AND structured `RegisteredOutcome.planned_*`/`reported_direction`/`field_comparison`. A `CorrespondenceAssessment` splits a deterministic prefilter from the semantic label, carrying `assessor_id`, machine-checked `pipeline_independent` vs `authoring_pipeline_id`, confidence, for/against evidence, optional dual-assessor κ. The free-float similarity is pinned in `resolvers.lock`.

**Determinism split.** Deterministic floor = join-coverage completeness, structured anchors, direction field-comparison (given extraction), snapshot re-hash. Reproducible = live resolution, pinned scorer bands, **and the planned_* extraction**. Irreducibly Class-C = the correspondence *label*.

**Sharpest defense:** correspondence/verification credit is gated on `pipeline_independent` from authoring, DEFAULTING to zero (`self_declared_provisional`); a well-formed fake dies on live fetch + second-resolver hash reproduction. Honest-unresolved symmetry is structural.

## L8 · Delta-Anchor Ledger — *structured inputs that make novelty scorable* (NOVELANCHOR)

**Kills:** a novelty judge needs contribution *kind*, claimed *magnitude* over *named* prior work, and a temporally honest neighborhood.

**Emits three prose-renderable sidecars.** `contributions.yaml` — one `CT##`, typed TWICE: `author_framed_type` vs `compiler_assessed_type.primary` (closed taxonomy) with `typing_rationale`; `typing_divergence{none, adjacent, conflicting}`; `conflicting`/low-confidence triggers a blind second rater + `adjudication`, reliability MEASURED as κ on a rotating held-out set. Anti-puffery lock: `realized_in ≥ 1` real `C##`. `delta_ledger.yaml` — one `D##`; `delta_status{quantified, qualitative_only, claimed_unresolved, not_claimed}`; `magnitude.claimed_value` is a `Q##`, `baseline_value` is an **`XQ##`** (fix #3); `absolute_delta`/`relative_delta` are **compiler-computed via versioned formulas** (`delta.abs.v1`/`delta.rel.v1`, explicit sign convention, canonical-unit resolution) — author-entered deltas rejected; `baseline_verification{source_verified, self_reported}` with `fetch_timestamp`. `sota_anchor.yaml` — resolver-produced (NOT compiler-written) citation + kNN neighborhood frozen at an **externally-timestamped `precedence_date`**, validator-enforced `cutoff_date == precedence_date`; `contemporaneous_uncited` members; existence-verified external ids; required second-resolver `overlap_jaccard` above a stakes threshold; `retrospective_resolution` + `gap_days`.

**Determinism split (honest).** Class A = delta arithmetic only (pure function of one `Q##` + one `XQ##` + direction). Class B = precedence, baseline fetch, typing (κ-measured). Class C-reproducible = the neighborhood. Honesty axis (equal across not_claimed/claimed_unresolved/verified=false/self_reported) separated from evidence axis.

**Sharpest defense — the suppressed-comparison probe.** A deterministic scan flags claims with comparative language whose contribution has `delta_ref=none`, making omission *costlier* than an honest `claimed_unresolved`. Judge-independent.

**Shared `overlap` definition (normative; added 2026-07-09 from the breakthrough-metric experiment).** Each neighbor in `sota_anchor.yaml` carries **`overlap ∈ [0,1]` = the fraction of THIS paper's core contribution already covered by that prior work** (0 = unrelated; 1 = near-duplicate). To be comparable across papers `overlap` MUST be computed by one fixed procedure — the reference implementation is a **deterministic OpenAlex measure** (bibliographic-coupling Jaccard of `referenced_works`, and/or topic-vector cosine), NOT a per-agent LLM estimate. The neighborhood emits three aggregates — **`min_overlap`** (connectedness), **`mean_overlap`** (density), **`max_overlap`** (closest-predecessor / near-duplicate detector) — plus **`resolvability ∈ [0,1]`** = fraction of references resolved to an external id, which gates confidence (novelty credit is scaled by `resolvability` so an unresolved neighborhood cannot masquerade as distance). *Why normative:* the v5 breakthrough experiment found overlap conceptually correct but empirically non-transferable **solely because 66 agents scored it 66 different ways** — a shared procedure is the fix.

**Two metrics from one measurement (breakthrough vs convergence) — a hypothesis, gated on a validated `overlap`.** In principle `overlap` reads with opposite sign for two distinct virtues, and a downstream metric MUST declare which it computes: **breakthrough / novelty = `1 − overlap`** (distance from prior work); **convergence / consolidation = `+ overlap`** (proximity to, and pulling-together of, prior work). A record can be high on one and low on the other. **Empirical status (v5 breakthrough experiment): NOT yet supported.** Two overlap implementations — per-agent LLM scoring and deterministic OpenAlex concept-cosine — came out *uncorrelated* (ρ≈0.02) and *both invalid* as a breakthrough signal (concept-cosine mistakes topically-generic surveillance reports for novel work). So this section is a **specification of intent, not a validated capability**: it is blocked until `overlap` is produced by a measure *validated to track prior-art distance* (candidate: SPECTER2 citation-space embedding distance, evaluated against a labeled novel/incremental set), and convergence additionally needs its own labeled panel. The validated breakthrough metric on this corpus is contribution-depth (`contrib_wmean`), which does not use `overlap`.

---

# TIER C — judgement protocols (reproducible, not deterministic)

Shared machinery: the judge only ever sees a **mechanically-assembled packet** (LLM-free at assembly); **confidence is ensemble agreement, never self-report**; the authoritative score is the **hash of an archived transcript**; re-running is a *drift audit* under inert perturbations, never a byte-identity claim; **calibration is a versioned artifact** (public frozen anchor + private rotating blind, publishing per-discipline MAE/ICC); **`contested` is a first-class disposition scored as a floor** whose position is now pinned (P2, must-fix #6).

**Cost and scale (must-fix #11) — stated, not asserted.** The Tier-C apparatus is expensive: per GRO, roughly P1 ≥3 families × sealed-N runs; P2 J≥3 × R≥3 (~12 verdicts) *per edge* + INVARIANCE_AUDIT + CALIBRATION_REPORT; P3 ≥5 judges × ≥3 families + a blind BCR twin ensemble; P4 K≥3 × ≥2 families. Order-of-magnitude: a mid-size GRO (say ~40 claim↔evidence edges) incurs on the order of **10³–10⁴ judge inferences** if every protocol runs fully on every element. This does **not** scale to a hundred-thousand-paper corpus at full density, and the spec no longer claims it does. The reconciliation is an explicit **tiered execution model**:
- **Full corpus (all GROs):** Tier A + Tier B run in full (deterministic + single-resolver passes are cheap and are the floor funders gate on).
- **Tier C on triage + sample:** the *sealed-N* and full panels run (a) on funder-**shortlisted** GROs on demand, and (b) on a **random audit sample** of the rest sized to bound corpus-level calibration error. Non-shortlisted GROs carry Tier-C fields as `pending_judge` (honest absence, scored neutral) until pulled.
- **Within a GRO:** P2's full J×R panel runs on **sampled + gate-flagged edges** (all `mechanical_disqualifier` hits, all edges a cheap screening judge marks non-trivial), not blindly on all edges; the INVARIANCE_AUDIT runs on a sub-sample.

So the honest scope is: **deterministic/anchored credibility at corpus scale; calibrated judged credibility at triage-and-sample scale.** §7 carries this as a structural limitation, not a solved problem.

## P1 · Calibrated Novelty & Significance (NOVELSCORE)

Consumes L8 + L6 (independently-resolved, publication-time-pinned SOTA neighborhood). Emits typed sidecars: `NOVELANCHOR.yaml`, `REFGRAPH.yaml` (publication-time-frozen kNN from THREE queries — author-independent `q_auto` primary + `q_anchor`/`q_concepts` — with `neighborhood_divergence`/`steering_flag` + `strongest_comparators`), `CALIBRATION.yaml`, `RUN_REGISTRY.yaml` (pre-registered N, sealed median), `judge_manifest` + `blinded_brief`, `novelty_report.yaml`.

**Three blocking fixes.** (1) **Self-assessment DISCOUNTED via a *monotone-down* provenance ceiling (internal-inconsistency #4).** The critique noted a confidence-shaping quantity keyed on self-reported provenance tags contradicts "confidence is ensemble agreement, never self-report." Resolution: the provenance ceiling is **a cap, never a confidence value, and it can only ever lower a score.** Ensemble agreement still *produces* the confidence; the provenance tag only *caps* it: reviewer_confirmed → cap 1.0; author-authored → cap 0.6; ai-suggested → cap 0.3. Crucially, **any upgrade of the cap requires independent machine-checkable evidence, never the self-report**: author-authored rises to 1.0 *only* on independent REFGRAPH corroboration; ai-suggested earns novelty uplift *only* if the independent neighborhood finds no closer predecessor; and `reviewer_confirmed` is a **Seal-L2 flag whose setter is now specified** — it may be written *only* by the rigor-reviewer pass (a `pipeline_independent` reviewer), is spot-auditable against the extraction log, and the compiler writing it is a V-class violation. So self-report can only ever *hurt* your own score; raising it is independently gated. No self-report shapes confidence upward. (2) **Undisclosed-prior-art flag — now *bounded*, not "structural" (over-claim #3).** If the single highest-similarity published-before `q_auto` neighbor is neither cited NOR addressed by a typed relation edge, magnitude is hard-capped at `incremental`. **Honest downgrade:** this cap relies on `q_auto` *surfacing* that predecessor, and §7 concedes the neighborhood is rebuilt from a post-cutoff snapshot (temporal leakage flagged, not eliminated) and that embedding-evasion of `q_auto` is an open question. So the cap **reliably fires when the predecessor is in-neighborhood and reliably spares when it is not**, but it is **not** a guarantee against a predecessor evaded or missed by the neighborhood. Tagged accordingly. (3) **White-box rubric broken:** `public_axes` + rotating hash-committed `held_out_probe_set` disclosed only after epoch close; red-team judge runs held-out probes; ensemble floor ≥3 distinct vendors/families.

**Coherence reconciled:** within-discipline isotonic calibration (raw→0–100) is separate from cross-discipline comparability (reference-cohort CDF percentile). **Both key on `discipline_ref` (§3), which is an A-R pinned label** — so the percentile is A-R, not deterministic, and is **withheld** where `discipline_ref = contested`.

**Sharpest defense:** RUN_REGISTRY sealed median makes run-five-cite-the-best *inadmissible*; the comparator cap (bounded as above) + monotone-down provenance ceiling make burying the closest in-neighborhood predecessor and inflating via unvetted AI adjectives worthless.

## P2 · Typed-Rubric Entailment (ENTAIL)

Tries every claim↔experiment↔evidence edge (L4) as a case. Emits a deterministic `ENTAILMENT_DOSSIER` — an LLM-free join over L2 + L4 + L1, copy-by-reference, content-hashed; design-feature presence keyed by anchored quantity ROLE with a non-null `source_anchor` (a nominal `baseline: yes` with no anchor is rewritten to `absent`). Judges may quote ONLY the dossier's anchored files.

**Deterministic half split from judged half.** A governed **Structural Gate** evaluates `mechanical_disqualifiers` (compiled boolean predicates over typed slots), zero LLM, emits a `STRUCTURAL_GATE_RECORD`, is graded against an adversarial self-test suite (published false_disqualify/false_pass rates), every disqualification carries an appeal valve (overturn_rate monitored). Disqualifiers typed `mechanical` (in-gate) vs `semantic` (calibrated panel).

**Judged half with real confidence resolution.** An adversarial multi-family panel (J≥3 providers, `pipeline_independent`) runs each judge R≥3 times; agreement voted over a J×R pool, reported as bootstrap `agreement_ci`; `contested = agreement_ci.lo < contested_threshold`. Every element grounded in an `evidence_span` substring-validated against the dossier. A versioned COMPOSE table fuses entailment × scope into one `effective_verdict` (overclaim caps entailment). `calibrated_confidence` read from a per-combo `accuracy_by_agreement_bucket` lookup, non-decreasing across buckets.

**FIX (must-fix #6) — where the `contested` floor sits, pinned.** The draft never fixed `contested` relative to a refutation, so steering a refuted edge into `contested` could be profitable. Now pinned on the effective-verdict **severity lattice** (worst→best): `refuted/contradicted < not_supported < contested < weakly_supported < supported < strongly_supported`. **`contested` floors at the level of `not_supported`, which is strictly *above* `refuted/contradicted` — and that is the point of the fix, stated as a rule: a would-be-refuted edge is NOT allowed to reach `contested` by manufactured disagreement.** Two mechanisms enforce it: (a) `contested` is a disposition on the *agreement* axis, applied only *after* the COMPOSE effective_verdict is computed; if any run yields `refuted/contradicted` with a valid grounded `evidence_span`, the edge's floor is set to **`refuted`, not `contested`** (a grounded refutation is sticky and cannot be diluted by adding lenient runs). (b) `contested` scores at the `not_supported` floor, so manufacturing ambiguity out of a merely `weakly_supported` edge *loses* credit, and manufacturing it out of a `refuted` edge is impossible (mechanism a). Steering a refutation into contested is therefore **not profitable** — it either fails (grounded refutation sticks) or costs (drops to `not_supported` floor). This ordering is published in the COMPOSE table.

**Reproducibility measured.** `INVARIANCE_AUDIT` re-runs sampled edges under inert perturbations + repeated t=0 + a pinned shadow panel (`drift_rate`). A `CALIBRATION_REPORT` with planted negatives (public-anchor/private-blind) hard-gates trust: any combo exceeding false_entailed τ is **revoked and its verdicts retroactively excluded**.

**Sharpest defense — trust revocation:** gaming a lenient combo revokes it and drops its verdicts; padding claims only adds edges that must survive gate + span-grounded J×R panel + the refutation-sticky floor.

## P3 · Realism & Validity Dossier (VALIDITY)

Two-plane Class-C. **Plane 1:** compiler-authored typed sidecar under `logic/solution/validity/` (`validity_manifest`, `assumptions`, `limitations`, `methods`, `perspectives`, `stress_probes`), **round-trippable to `constraints.md` in reconcile mode** so prose↔sidecar agreement is a genuine anti-fabrication check (§0.1); resolves by id against sibling `refs.yaml`/`quantities.yaml`/`claim_type`. **Plane 2:** protocol-only verdict record at `trace/validity_panel/{run_id}.yaml`. Planes never share a write surface.

**Deterministic/judged split.** Each metric decomposes into a pure-code pre-gate (schema/FK/quote-anchor verification, method-status citation-existence gate, perspective distinct-anchor join, M31 axis set-difference) that can only cap/floor/route — never invent realism — plus a Class-C judged residual. Pre-gate failure blocks the judge.

**Sharpest device — Blind Counterfactual Reconstruction (BCR), and `assumption_coverage`.** An ensemble reconstructs the method-mandated assumptions a competent study must rely on, *firewalled from the paper's own assumptions/limitations/Discussion*. `reconstructed ∖ declared`, filtered to load-bearing, yields `omitted_load_bearing` — fed to the floor as declared-and-unrealistic. **This is the `assumption_coverage` mechanism the omission-attack fix (must-fix #7) requires** — it catches assumptions never typed at all, complementing L2's `claim_coverage` for claims and L1's `numeral_reconstruction` for numbers. All three are **Class-C reproducible, not deterministic**, and are the honest answer to "the compiler chooses the content" (§0.3, §7). The BCR pass is `pipeline_independent`, not decorrelated (§7).

**Two fixes.** (1) **Floor severed from self-report:** `min_i[realism_i + (1−w_i)(1−realism_i)]` sources `necessity`/`severity` for `w_i` ONLY from independent labels (BCR-twin blind values, or panel-judged with declared fields redacted); `tested_in_paper` is the sole self-reported input, deterministically checkable against `experiments.yaml`. Declared severity < independent severity is a `severity_understatement_defect`. (2) **One closed axis vocabulary:** `scope_axis_vocab@v1` used identically by `scope_narrowing.axis` and `applicability_conditions.scope`, pinned, frozen with `rubric_version`; out-of-vocab values rejected, not coerced.

**Reproducibility measured:** identical templated probes; for/against before verdict; ≥5 judges over ≥3 families with within/cross-family MAD; median + MAD aggregation; neutral-body calibration set; frozen input hashes; published test-retest delta.

## P4 · Frontier & Triangulation (HARDSIGNALS)

Supplies the surface M39 lacks ("no optimum stored anywhere"). **Tri-partite producer split:** (1) compiler emits only source-anchorable structural fields, `pending_judge` in every semantic slot; (2) a deterministic replayable evaluator computes every arithmetic quantity; (3) a bounded Class-C judge fills ONLY argued-tier distance, qualitative agreement, the shared-confound corroboration verdict, and a missing-candidate audit — redacted, ensembled, calibration-gated, rerun-checked.

**Schema core.** `heuristics.md` gains `shortcut_dimension`, `ideal_counterfactual`, `frontier_ref`. `frontier.yaml` is a tagged union keyed by `tier{measured_ablation, external_benchmark, theoretical_bound, argued, not_applicable}`, carrying a tier-shaped `comparator`, `objective_vector`, hash-pinned `frozen_candidate_set`, a `circularity_check`, structured `distance{raw, normalized_regret}`. `perspectives.yaml` + `triangulations.yaml` + `judge_panels.yaml`.

**Deterministic vs judged.** Tiers 1–3 deterministic/anchored: raw arithmetic gap + a bounded `normalized_regret` whose denominator is a **declared, source-anchored `reference_floor`**; `not_normalizable → null`, never a faked [0,1]. Tier 4 argued distance semantic-judged: K≥3 judges, ≥2 families, temp 0, for/against before verdict, self-assessment redacted, median + IQR + cross_family_spread + perturbed-rerun delta. **Confidence decoupled from tier.** Triangulation corroboration = **independence × agreement** — where "independence" here means the lenses genuinely differ on *controlled axes* (a structural check), which is stronger than the pipeline-id independence of the judges reading them.

**Sharpest defenses:** `not_specified` counts as NOT-independent (closes denominator-exclusion Goodhart); same-data-forced-0; weakest-link `min` over pairs; declared `reference_floor` bounds the normalizer; resolver-fail auto-downgrades to argued **plus an integrity-violation flag** (fails closed); a per-run `calibration_accuracy` gate drops miscalibrated judges against a canary-protected corpus.

---

## 4. Metrics catalogue, tagged by rigor class

**D = deterministic (Tier A) · A-R = reliable-anchored (Tier B) · R-J = reproducible-judged (Tier C).** Tags now reflect the critique's corrections: any metric whose *content* (not just wrapper) depends on an LLM-authored or resolver input shows the mixed class.

| Metric family (merged suite) | Afforded by | Class |
|---|---|---|
| Cross-layer numeric reconciliation, self-consistency recompute (`09`, M49–M51) | L1 × L4 | **D** |
| Numeric **grounding-to-source** fidelity (value ∈ quote ∈ **source**) (`02`, L1 §10) | L1 recompute (D) **+ independent `external_fidelity` audit** | **A-R** (not D) |
| Ordinal / ranking integrity — *internal consistency of stated rank↔score only; surrogate-computation NOT afforded* | L1 `ranking_ref` | **D (internal only)** |
| Numeral-coverage (tagged/matched/listed) | L1 `numeral_coverage` | **D** |
| Non-load-bearing truthfulness (residual self-declared) | L1 `numeral_reconstruction` blind diff | **R-J** (bounded) |
| **FOL-ability** (M09) — *form is D; faithful capture of the paper is not* | L2 form (D) + prose↔FOL fidelity + `vacuity_check` | **D (form) + R-J (fidelity)** |
| **Claim↔claim contradiction** (M08) — symbolic + CK-gated numeric over authored forms | L2 (+ CK gate); fidelity of forms is R-J | **D (over forms) + R-J (fidelity)** |
| Over-claiming / scope calibration (D3) | L2 populations field-diff (n-expectation promoted) × P2 residual | **D + R-J** |
| Claim-type ↔ experiment-design adequacy (D1) | L2 × L4 | **D** |
| Claims ↔ concepts consistency (M13) | L2 × L3 (set op); L3 `resolved` input is A-R | **D (downstream of A-R L3)** |
| **Claim-coverage** (wholesale non-typing) | L2 blind claim-reconstruction diff | **R-J** (bounded) |
| Controlled-vocab / latent anchoring (M10/M12/M64) | L3 (decorrelated two-arm; Arm A non-LLM) | **A-R** (genuinely decorrelated) |
| Cross-ARA entity-recognition (diagnostic only) | L3 commons (UNSCORED) | A-R (unscored) |
| Cross-layer alignment coverage / testability (M15/M50/M51/M57), test-adequacy (grounded) | L4 node_ref grounding | **D** |
| Internal numeric reconciliation (edge-attr ⊆ quote ⊆ **internal** text) | L4 `ledger_ref` double-lock (containment, not hash) | **D** |
| Feature-licensing rate (signal, non-gating) | L4 `licensing_signals.yaml` | R-J (signal) |
| Honest-absence vs lazy-omission, article-type (M02, S21) | L5 meet + `silent_omission_count`; **narrative-genre residual bounded** | **D** (label pinned) + bounded residual |
| Genre honesty (declared-vs-blind contested rate) | L5 corroborator | **D** (label pinned-reproducible) |
| Discipline label (for P1 normalization) | meta.yaml pinned blind classifier | **A-R** (withheld if contested) |
| Reference-landscape completeness (S1/M14/M16/M40/M26) | L6 | **A-R** |
| Claim-drift / reference truthfulness (S3/M18/M23) | L6 `anchor_check` (D) × L6 `semantic_review` (pipeline-independent LLM) × P2 | **A-R + R-J** |
| Citation dedup / anti-count-inflation | L6 (`CX` inflates, `R` does not) | **D + A-R** |
| Registry realness & topic binding (`11`) | L7 live fetch + 2nd-resolver hash | **A-R** |
| **Publication-bias / outcome-switching (M04)** — *bounded by joinable-rate; planned_\* is Class-C extraction* | L7 `outcome_coverage` × planned_outcome_extraction (A-R) × direction field-comparison (D given extraction) × L1 `registry_ref` | **A-R (extraction) + D (comparison)**, bounded |
| Access-tier fidelity | L7 `access_tiers` liveness | **A-R** |
| Prospective-registration rate, verification freshness | L7 `RegistryVerification` profile | **A-R** |
| Delta-computability, baseline-verification, missed-prior-work | L8 (delta arithmetic over Q##+XQ## **D**; precedence/baseline **A-R**) | **D + A-R** |
| Contribution-typing inter-rater κ; suppressed-comparison flags | L8 (probe judge-independent **D**; κ measured) | **D + A-R** |
| **Novelty & significance, calibrated (S2/M07/M11/M17/M24/M34)** | P1 on L6 + L8; percentile keys on A-R discipline; prior-art cap bounded | **R-J** (percentile withheld if discipline contested) |
| Entailment quality / evidence relevance (D1/S4/M19/M49) | P2 on L1+L2+L4; contested floors at not_supported, refutation sticky | **R-J** |
| Assumption realism, method & limitation validity (S7/S8/M28–M35) | P3 (+ deterministic pre-gates; BCR = assumption_coverage) | **R-J** (D floor) |
| Heuristic distance-from-optimum (M39) | P4 tiers 1–3 **A-R** / tier 4 **R-J** | A-R + R-J |
| Multi-perspective triangulation (S6/M36) | P4 (axis-independence structural **D**, agreement **R-J**) | **D + R-J** |
| Exploration/dead-end integrity (D5/M41/M42/M47) | L4 tree edges + verdict log | **D + R-J** |
| **Reproducibility-artifact completeness — presence + cross-layer linkage ONLY; code is NOT executed** (S5/M48) | L1 × L4 × L7 + artifacts under L5 warrant | **D (presence+linkage), NOT execution-verified** |
| Reuse & FAIR-ness (S15/M53–M55/M58–M60) | L3 + L6 + L7 resolvable ids + license-as-data | **A-R** |
| Data homogeneity & standard adherence (S22/M63) | L3 xrefs + L7 access/standards | **A-R** |

Anti-Goodhart posture is uniform *within the limits each class allows*: **length never scores**; **fabrication always has an independent second checker** — but that checker is *genuinely decorrelated only at L3 Arm A*; everywhere else it is *pipeline-independent (necessary, not sufficient)*; **honest absence scores equal to honest presence** except where a deterministic expectation is violated; every self-certifiable field is split into a deterministic axis plus an independently produced one. The **M48 "reproducibility" metric is presence+linkage, not execution** — the format cannot run the code, so a non-running bundle with a matching figure passes the *completeness* check and must be read as such (§7).

---

## 5. Funder-facing output — the Credibility Dossier

A GRO reduces, for a program officer, to one decomposed decision object — **never a single collapsed number**. Every rigor class is labelled *on its face*, so no A-R or R-J number is dressed as deterministic (must-fix #1):

```
GRO://che26-diagnostic-performance-of-plasma-p-tau217   discipline: DISC-clin-neuro (pinned, conf 0.91)
├─ Integrity (Tier A · deterministic)      ● reconciliation PASS · 0 contradictions [over authored forms]
│                                            · over-claim 0.04 · 0 registry_desync · numeral-coverage 1.00
├─ Grounding-to-source (Tier B · reliable) ● fidelity 0.98  [independent external_fidelity audit — A-R,
│                                            not deterministic; 1 numeral contested-non-load-bearing]
├─ Anchoring (Tier B · reliable)           ● 100% refs resolved · 1 accession registry-verified
│                                            · 1 outcome-switch FLAGGED (M04 joinable) · access tiers honest
├─ Novelty & significance (Tier C)         ● 71/100 [CI 63–78] · discipline pct p68 [A-R label]
│                                            · provenance-ceiling applied (down-only) · no undisclosed
│                                            · in-neighborhood prior art [cap bounded by q_auto coverage]
├─ Support quality (Tier C)                ● entailment 0.86 · 1 contested edge (floored at not_supported,
│                                            not above refuted) · 0 refuted · calibration-trusted
├─ Validity (Tier C)                       ● assumptions realistic (2 flagged · 1 BCR-omitted, floored)
│                                            · single-perspective (declared) · frontier: argued-tier only
├─ Coverage (Tier C · reproducible)        ● 0 uncovered load-bearing claims · 0 omitted assumptions
│                                            [blind-reconstruction diffs — not deterministic]
└─ Honesty ledger                          ● 0 lazy omissions · 3 honest not-applicable
                                             · 1 outcome-switch disclosed · 2 data-quality caveats
```

Every dot is drillable to its evidence — the anchor, the verbatim quote, the resolver receipt, the judge transcript hash, the calibration epoch. **Each dot also carries its rigor class on its face**: "Grounding-to-source" is a Tier-B row, not folded into Integrity; "0 contradictions" reads "over authored forms"; novelty percentile reads "A-R label" and is *withheld* (not faked) when discipline is contested; M48 would read "presence+linkage, not executed." A funder can **rank a portfolio on the novelty + significance axis, gate on the integrity + anchoring floors, and read support + validity + coverage as risk** — and can *audit any score to its source and to its rigor class*. Provisional dispositions (`contested`, `provisional_debt`, `classifier_error_signal`, `severity_understatement_defect`, `contested_non_load_bearing`, `uncovered_load_bearing_claims`) are surfaced, never hidden inside an average. Fund the work that is both rigorous and important, defensibly — and know exactly where "defensibly" is deterministic, where it is merely reliable, and where it is a calibrated judgement.

---

## 6. Ecosystem dependencies

GRO is not self-sufficient by design; Tiers B/C and several Tier-A checks collapse without shared, versioned, hash-referenced ecosystem artifacts. These are declared, not hidden.

**Vocabularies & taxonomies (Tier A/B):** `predicate_vocab@vN`; `commensurability@vN` + Comparability-Key defs; `populations` generality ladder + over-claim rule table (now with the `n`-expectation promotion); `scope_axis_vocab@v1`; `genre_taxonomy.vX`; **`discipline_vocab@vN`** (new — closed field-of-science enum, drives P1 normalization); contribution-type taxonomy + adjacency graph; per-kind entity alias tables; `edge_schema` (+ coverage_obligations, trust_tier_map, `registry_authority` **scoped to Tier A + skeleton**), `nullability.yaml`, `acyclicity.yaml`.

**Resolvers, pinned (Tier B):** shared `resolvers.lock`; reference resolver + external-index snapshot (OpenAlex/S2/DOI/arXiv) with `extractor_id`/`NORM_v1`; registry resolver (NCT/CRD/GSE/phs) + the two `VerificationRecordCore` profiles (`RefVerification`, `RegistryVerification`); **the planned-outcome extraction ensemble (L7, `pipeline_independent`)**; the entity two-arm resolver (**non-LLM literal matcher** + semantic linker) + `resolver_calibration.yaml`; pinned embedding models with `index_snapshot_id` for L8 kNN and L3 anchors; a commons authority (diagnostic, unscored).

**Classifiers, pinned (Tier A):** the GENRE `classifier_manifest` (emitting both `paper_type` and `discipline_ref`) and its non-LLM `structural_corroborator`.

**Calibration & governance sets (Tier C):** per-discipline human-labeled sets publishing MAE/ICC/Spearman; public frozen anchor + private rotating blind sets; NOVELSCORE's rotating hash-committed `held_out_probe_set`; ENTAIL's planted-negative suite driving trust revocation; VALIDITY's `domain_priors.yaml`/Domain Baseline Registry + neutral-body set; HARDSIGNALS' canary-protected calibration corpus; L8's rotating held-out κ set; **the blind-reconstruction ensembles for `claim_coverage`/`assumption_coverage`/`numeral_reconstruction`** (Tier-C, `pipeline_independent`).

**Hashing & determinism primitives (three regimes, not one — §3):** raw-byte `source_anchor.sha256` (L1); `NORM_v1` (L6 titles + content/quote); `text_hash` over derived text (L3); the QUANT canonical lexer (L1 numeric comparison); L4 substring containment (not a hash); content-hash transcript archival for every Tier-C verdict.

**Ecosystem to-do for full Tier-B/C reliability:** curate per-discipline calibration sets and the discipline vocabulary; stand up pinned resolvers with index snapshots; **build and calibrate the free-text planned-outcome extraction step (L7)**; version and freeze all vocabularies/taxonomies; operate the commons authority; govern the rotating blind/probe sets against capture; **resource the tiered Tier-C execution model (triage + audit-sample) — full-density Tier C does not run at corpus scale (§7).**

---

## 7. Honest limitations

**Class-C is irreducible.** No format change makes novelty, significance, entailment quality, assumption realism, or distance-from-optimum deterministic. GRO makes them reproducible and auditable; the human calibration set and the judge ensemble remain load-bearing. The format shrinks the surface the judge reasons over and pins its inputs — it does not become the judge.

**"Deterministic" is downstream of a frozen LLM-authored input set, not end-to-end (over-claim #6).** FOL-ability, claim/contradiction detection, and claims↔concepts consistency are deterministic *over the compiler's own authored forms and L3's `resolved` set*; those inputs are themselves A-R (pinned resolver + LLM lowering). "0 contradictions" and "FOL-ability high" are exact statements about the wrapper, not proof about the paper — a compiler emitting weak/vacuous forms deterministically scores well on both. The `vacuity_check` excludes empty forms from the credit and the over-claim diff catches inflation, but **under-formalization is only caught by the Class-C `claim_coverage` blind diff, not deterministically.**

**The compiler selects the content that gets recomputed (axiom-3 residual).** Determinism cannot close *what the compiler chooses to type*. Three reproducible blind-reconstruction passes (`numeral_reconstruction`, `claim_coverage`, `assumption_coverage`/BCR) diff an independent extraction against the typed set and score the gap, but they are **Class-C, bounded by independent-labeler recall**, not deterministic guarantees. Wholesale non-typing is *harder and visible*, not impossible.

**Independence is pipeline-independence (necessary, not sufficient) — decorrelation is earned only at L3 Arm A (over-claim #4, missing #4).** "Machine-checked independence" verifies distinct pipeline id + model family + prompt-lineage hash + packet-only inputs. It rules out self-certification and shared-prompt collusion; it does **not** measure statistical independence and **cannot** rule out shared-pretraining-corpus correlation between two LLM families. L1 `external_fidelity`, L6 `semantic_review`, L7 `CorrespondenceAssessment`, the L7 planned-outcome extractor, and every Tier-C panel rest on *asserted*, not measured, decorrelation. Only L3 Arm A (a non-LLM literal matcher) earns genuine decorrelation. A compromised or correlated "independent" pass defeats the corresponding anti-fabrication claim.

**Reproducibility of hosted LLMs is measured, not guaranteed.** Batching, MoE routing, float non-associativity mean re-inference is not byte-identical. Tier-C "reproducibility" is the hash of an archived transcript (authoritative) plus a measured invariance-under-inert-perturbation band — never an identity claim.

**The Tier-C apparatus does not run at corpus scale (must-fix #11).** Full-density P1–P4 costs ~10³–10⁴ judge inferences per mid-size GRO. The design runs deterministic + anchored credibility on the full corpus, and full calibrated judgement only on funder-shortlisted GROs plus a random audit sample; within a GRO, P2's panel runs on sampled/gate-flagged edges. So the corpus-scale promise is honestly **"deterministic and anchored at 100k scale; calibrated-judged at triage-and-sample scale,"** not full Tier C on every paper. Triage-screening bias (a cheap screener mis-skipping an edge) is a residual the audit sample bounds but does not eliminate.

**Genre-shopping is bounded, not eliminated (over-claim #2).** For anchorable genres the structural corroborator forces and clears slots, so shopping cannot silently shrink the denominator. For purely narrative genres (empty anchor set) there is no deterministic clear; a nonzero, magnitude-bounded false-absence residual remains, attributed to `contested_ttl_lazy_omission` and surfaced as a corpus `classifier_error_signal`. GENRE multi-anchor ties resolve to null (can under-detect a genuine clear); the Class-B dispute gate is a real reliability dependency.

**The undisclosed-prior-art cap is bounded by neighborhood coverage (over-claim #3).** The P1 comparator cap fires reliably only when the closest predecessor is inside the `q_auto` neighborhood. The neighborhood is rebuilt from a post-cutoff index snapshot (temporal leakage flagged, not eliminated), and embedding-evasion of `q_auto` remains an open question. So burying an in-neighborhood predecessor is worthless; burying one the neighborhood misses or that leakage contaminates is not structurally prevented.

**M04 outcome-switching is bounded by extractability and posted-value availability (missing #2, #3).** Direction-switch detection needs `planned_direction`/`planned_measure` parsed from free-text registry records (a Class-C extraction, now designed but calibration-dependent) and, for numeric switches, a posted registry number that most PROSPERO/NCT records do not carry. Coverage is reported as `m04_direction_joinable_rate` / `m04_joinable_rate`; "publication-bias afforded" means "afforded on the joinable fraction," not universally.

**M48 is completeness, not reproducibility.** The format checks presence and cross-layer linkage of figure+data+code+protocol; it cannot execute code. A non-running bundle with a matching figure passes the completeness check. This is labelled on the dossier and in §4; true execution-reproducibility is out of format scope.

**`ranking_ref` checks internal consistency only (missing #7).** It verifies stated rank ↔ stated score/polarity coherence. Whether a surrogate ranking (e.g. a network-meta-analysis P-score) was *correctly computed* requires the underlying data and is not afforded.

**The non-load-bearing numeral list is a residual self-declared surface (must-fix #8).** `numeral_coverage` forces the tagged/matched/listed trichotomy and enum'd reasons, and `numeral_reconstruction` routes list entries appearing in result/comparative sentences to `contested_non_load_bearing`. Dumping an inconvenient number is *costlier and visible* but not deterministically impossible; the residual is scored, not eliminated.

**Three provenance regimes, no single cross-layer hash identity (cross-layer #1).** L1 raw-byte SHA-256, L6 `NORM_v1`, L3 derived `text_hash`, plus the QUANT lexer normalization and L4 substring containment. The *same* quote hashed under L1 and L6 will not match; cross-layer identity is by `id` reference only. "Everything is pinned and hashed" means each surface is pinned under *its* regime, not that one hash spans them.

**`registry_authority` exempts Tier-C verdict ids (cross-layer #3).** It governs the Tier-A + skeleton id space; verdict ids are minted post-compile by judges into append-only logs and are never projected into `nodes.yaml`, reached instead by late-binding `verdict_ref`. This is the stated exemption that keeps both "faithful projection" and "judges never author the graph" true simultaneously.

**Honest absence still buys a bounded pass on under-generality (axiom-4 tension, cross-layer #5).** The over-claim diff needs `n` to fire; promoting `n` to an expected slot for `population_estimate`/`claimed_universal` claims closes the free pass *for those tiers* (omitting `n` becomes a violated expectation), but below that tier missing `n` remains protected honest absence, and a claim mislabeled to a lower generality tier to dodge the expectation is caught only by the (Class-C) quantifier field-diff, not deterministically.

**The write-surface doubles, and only reconcile-mode agreement is a signal (internal-inconsistency #3).** Emitting typed sidecars alongside prose creates a consistency obligation. Where prose is *rendered from* the ledger (`bind_mode: render`), agreement is guaranteed by construction and proves nothing about fabrication; the anti-fabrication signal exists only on `reconcile`-mode surfaces (independently authored, then checked). The format reports the render/reconcile split and awards agreement credit only to reconcile surfaces — the doubled write-surface is a real cost, deliberately taken.

**Calibration governance can be captured, and cross-discipline comparison is a modeling choice.** Rotating blind sets, held-out probe sets, and domain-prior registries are institutional trust anchors; their integrity (canary protection, rotation, neutral-body curation) is an operational ceiling the format gates but cannot solve. Discipline itself is an A-R pinned label; where it is contested the cross-discipline percentile is withheld, so the headline funder ranking is *unavailable for interdisciplinary/frontier work*, not faked. Cross-epoch percentile bridging remains an open question.

**Deterministic-but-bounded confidence.** ENTAIL and HARDSIGNALS calibrated confidence is monotone *across buckets*, not at every agreement value (isotonic regression is the flagged successor). L3 re-anchoring `forged` is only same-model/same-text mismatch; a model migration that also alters text routes to re-anchoring, not forgery.

**Non-self-sufficiency is structural.** Tiers 1–3 of HARDSIGNALS collapse without sibling `quantities.yaml`/`refs.yaml`/method-ontology xrefs; `not_applicable` scored equal to a resolved frontier means anti-dodging rests entirely on source-anchor enforcement. Tier-laundering (strawman-handicapped ablations) and calibration-corpus contamination are named residual ceilings the format gates but does not eliminate.

---

## 7a. Implementation status — spec vs what the compiler emits today (as of 2026-07-15)

This spec is the target shape. The compiler as run over the 66-paper Alzheimer's corpus emits a **proper subset**, and honesty requires stating the gap in one place.

**Emitted today, per artifact, in a `gro/` sidecar directory (66/66 unless noted):**
`quantities.yaml` (Q##) · `external_quantities.yaml` (XQ##) · `claims_typed.yaml` (C##) · `entities.yaml` · `genre.yaml` (declared `paper_type` + slot presence) · `refs.yaml` (R##, resolved) · **the L8 novelty tier** — `contributions.yaml` (CT##, double-typed) · `delta_ledger.yaml` (D##) · `sota_anchor.yaml` (resolver neighborhood + `overlap`) · `temporal.yaml` (62/66). Plus the inherited ARA prose (`logic/`, `PAPER.md`), `src/`, `evidence/`, `data/`, `trace/exploration_tree.yaml`.

**Specified but NOT yet materialized:** the derived/hash-gated Tier-A objects (`claim_graph.yaml` AST, `symbol_table.yaml`); the **L4 cross-object graph** (`nodes.yaml`/`edges.yaml` — the inter-paper "particle layer"); L6 `citation_mentions.yaml`/`support_edges.yaml`/`resolution_candidates.yaml`; the L7 registry-join ledgers (`claim_registry_links`, `outcome_coverage`); and the P1–P4 report objects (`novelty_report`, `entailment_verdicts`, validity dossier). So the operative GRO today is a **Tier-A record layer + the L8 novelty tier + prose + exploration trace** — not the full cross-object multigraph.

**Manifest gap.** `PAPER.md`'s Layer Index currently lists only the inherited ARA layers (`/logic`, `/src`, `/data`, `/trace`, `/evidence`); the `gro/` substrate layer is emitted beside the artifact but **is not declared in the manifest, and prose carries no `bind_mode`**. The GRO tier is presently an appended sidecar bundle, not a manifested, prose-bound layer. Wiring `/gro` into the manifest (and emitting `bind_mode`) is the nearest-term integration fix.

**Empirical status of the L8 breakthrough metric (v5/v6 experiments).** The one field shown to carry signal is `contributions.yaml` typing, aggregated as `max(peak, cwmean)`. Against a same-model LLM expert panel it reached ρ≈0.58 (held-out); against an independent model family ρ≈0.34 (≈⅓ was shared-method bias, Steiger p=0.003, bias flips when the metric is built by the other model); against a **real-world, LLM-free ground truth** (historical 2004–2010 papers vs mature citation-disruption) it showed **no reliable predictive power** (ρ near zero, sign-unstable). `delta`, the `overlap`/`sota_anchor` axis, and genre added no transferable signal. So L8 today is best read as **"flags LLM-perceived contribution depth,"** an adversarially-hardened but empirically-unvalidated breakthrough signal — matching this spec's Tier-C "reproducible, not deterministic; calibration is load-bearing" stance.

---

## Appendix — Provenance & method

This document is the **final synthesis** of a three-stage process: (1) the `IDEAL_FORMAT_SPEC.md` **draft**, itself merged from twelve gap-tournament winning designs (QUANT, CLAIMFOL, ENTITY, EDGES, GENRE, REFGRAPH, REGISTRY, NOVELANCHOR, NOVELSCORE, ENTAIL, VALIDITY, HARDSIGNALS) evaluated against `AFFORDANCE_GAP.md` and `ALL_METRICS_MERGED.md`; (2) an **adversarial critique** (`verdict: needs_major_revision`) enumerating internal inconsistencies, over-claims, missing/underspecified fields, cross-layer conflicts, and eleven must-fix items; (3) this **revision**, in which every must-fix is resolved either by a design change (new `XQ##` external-quantity ledger and `DISC-*` discipline ledger; scoped `registry_authority`; two-profile `VerificationRecordCore`; pinned `contested`-floor ordering; designed free-text planned-outcome extraction; `claim_coverage`/`assumption_coverage`/`numeral_reconstruction` blind diffs; specified pipeline-independence definition; tiered Tier-C execution model) or by an explicit demotion to §7 with its metric tag corrected in §4 and its label surfaced in the §5 dossier (grounding-to-source → A-R; FOL-ability/contradiction → D-over-forms + R-J-fidelity; M48 → presence+linkage not execution; genre-shopping and prior-art cap → bounded; decorrelation → reserved for L3 Arm A). Nothing flagged was silently dropped; changed tags and the expanded limitations section are the audit trail. Workflow run: `wf_f0bc615b-a88` (+ tail).
