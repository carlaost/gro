# Tail Synthesis Log — completion of `wf_f0bc615b-a88`

Run `wf_c4cbff37-887` (tail). Completed the stages the original tournament lost to a rate limit: the VALIDITY + HARDSIGNALS refine round, the review gate on all 12 finalists, and the agent-driven draft → adversarial-critique → final synthesis. 25 agents, 0 errors, ~1.70M tokens. All agents ran on Claude Opus 4.8.

## Review gate verdicts

| Gap | Class | Verdict | Sent back once? |
|-----|-------|---------|-----------------|
| QUANT | A | accept_with_nits | yes |
| CLAIMFOL | A | accept_with_nits | no |
| ENTITY | A | accept | yes |
| EDGES | A | accept_with_nits | yes |
| GENRE | A | accept_with_nits | yes |
| REFGRAPH | B | accept_with_nits | yes |
| REGISTRY | B | accept_with_nits | no |
| NOVELANCHOR | B | accept_with_nits | no |
| NOVELSCORE | C | accept_with_nits | yes |
| ENTAIL | C | accept_with_nits | yes |
| VALIDITY | C | accept_with_nits | yes |
| HARDSIGNALS | C | accept_with_nits | no |

All 12 accepted (`accept` or `accept_with_nits`); no gap left in `revise` after the bounded send-back. 7 of 12 were sent back once and hardened on the second pass.

## Adversarial critique of the draft (what the final had to resolve)

**Verdict:** needs_major_revision

### Internal inconsistencies (6)
- §5 dossier vs §4 catalogue on grounding. The Credibility Dossier prints 'Integrity (Tier A - deterministic) grounding 0.98' as a deterministic integrity number. But §4 tags 'Numeric grounding fidelity (value in quote in source)' as D->A-R, explicitly '+ independent external_fidelity audit,' and L1 itself splits reconcile_status (Class A) from external_fidelity (written ONLY by the independent pass). Grounding-to-source is A-R, not deterministic; the dossier files it under the deterministic tier and drops the qualifier. The two-axis firewall that is L1's whole point is collapsed back into one number at the funder surface.
- §0 axiom 3 ('the author/compiler that states a fact never certifies it; self-assertion defaults to zero credit') contradicts the entire Tier-A scoring model. reconcile_status (L1), parse/typecheck and FOL-ability (L2), node projection and COV coverage (L4), paper_type_declared (L5) are all compiler-authored and all scored. The escape hatch ('deterministic recomputation, not certification') hides that the compiler still *chooses the content* being recomputed - which numbers are load-bearing, which prose becomes a C##/logical form - and that choice is scored via denominators the spec claims 'no agent controls.'
- Axiom 1 ('render prose FROM it OR reconcile prose AGAINST it') vs the round-trip anti-fabrication claim (VALIDITY 'prose<->sidecar agreement is itself an anti-fabrication check'; EDGES 'prose authored independently, edges reconciled against it'; §7 'agreement-between-views is an anti-fabrication signal'). If prose is RENDERED from the ledger (mode 1), agreement is guaranteed by construction and proves nothing. The anti-fabrication signal exists only in RECONCILE mode (independent authoring). Axiom 1 permits the vacuous mode, so the claimed signal is not guaranteed by the format.
- Tier-C shared machinery says 'confidence is ensemble agreement, never self-report,' but P1's provenance-ceiling keys a novelty-axis cap on self-reported provenance tags (author-authored->0.6, ai-suggested->0.3, reviewer_confirmed->1.0). These provenance tags live in the extraction log and are compiler/author-set; reviewer_confirmed is a 'Seal-L2 flag' whose setter is unspecified. A confidence-shaping quantity is thus keyed on a self-report, contradicting the shared invariant.
- 'Shared VerificationRecord type hoisted across L6 and L7' unifies a name, not a schema. L6's verifier result vocabulary is {verified, mismatch, ambiguous, pending, unresolved, grey_lit}; L7's VerificationRecord.result is the six-value {resolved_match, mismatch, not_found, unreachable, ambiguous, not_checked}; the hash fields differ (L6 content_hash over NORM_v1(extract_text) vs L7 registry_record_hash + snapshot_sha256). One shared type cannot carry two incompatible enums and two hash regimes.
- 'contested is scored as a floor so manufacturing ambiguity buys nothing' is only sound if the floor sits at or below the worst genuine verdict. P2 emits an effective_verdict that includes over-claim caps and (via COMPOSE) scope/entailment combinations that can be worse than 'not-supported.' If a would-be refuted/contradicted edge can be steered to 'contested' and floored *above* the refuted score, manufacturing contested is strictly profitable for exactly the claims most worth catching. The spec never pins where the floor sits relative to a refutation bucket.

### Over-claims (6)
- 'FOL-ability (M09)' and 'Claim<->claim contradiction (M08)' are tagged pure D (deterministic). What is deterministic is the PARSE of the authored DSL line into an AST and the CK-gated SAT over it. Whether the logical form faithfully captures the paper's claim is 'prose<->FOL fidelity (the real fabrication surface),' which the spec itself concedes is Class B/C. So '0 contradictions' is a deterministic statement about the compiler's own logical forms, not about the paper. A compiler that emits weak or vacuous forms deterministically produces zero contradictions and high FOL-ability - the over-claim field-diff catches quantifier inflation but not under-formalization. Determinism is claimed for the wrapper, not the content.
- 'Genre-shopping can never silently shrink the denominator' is contradicted three paragraphs earlier by the narrative-genre carve-out: purely narrative genres (empty anchor set) 'have no deterministic clear,' so the residual false-absence is 'floored, bounded, attributed to classifier_error_signal.' For narrative genres shopping IS possible, merely bounded. 'Never' should be 'bounded for anchorable genres, a bounded fudge for narrative ones.'
- P1's comparator-completeness cap ('burying the closest predecessor is structurally worthless') rests on the q_auto neighborhood surfacing that predecessor. §7 concedes the neighborhood is rebuilt from a POST-cutoff index snapshot (temporal leakage 'flagged, not eliminated') and that 'embedding-evasion of the q_auto neighborhood remains an honest open question.' If q_auto can be evaded or is temporally contaminated, the cap neither reliably fires nor reliably spares - it is not a structural guarantee.
- 'Machine-checked independence from the authoring pipeline' (L7, L1, P1) checks that authoring_pipeline_id differs, which proves pipeline-id-distinctness, not statistical independence. §7 half-admits this ('not a compromised independent pass'), but the body repeatedly upgrades id-distinctness to 'decorrelated' / 'correlated hallucination cannot manufacture agreement.' That decorrelation claim is only earned by L3's Arm A (a genuinely non-LLM literal matcher). For L1 external_fidelity, L6 semantic_review, L7 CorrespondenceAssessment, and every Tier-C panel, the 'independent' pass is another LLM whose correlation with the author LLM is asserted, not measured.
- 'E2E reproducibility bundle: fig+data+code+protocol (S5/M48)' is tagged D (deterministic). The format can only check PRESENCE and cross-layer LINKAGE of artifacts; it cannot execute the code to confirm the figure reproduces. Shipping non-running code plus a matching figure passes the 'bundle' check. Presence-as-reproducibility is precisely the Goodhart substitution the doc claims to defeat elsewhere.
- 'Reproducible run-to-run' for Tier A is asserted broadly, but Tier-A metrics inherit non-deterministic upstream inputs: FOL-ability requires 'resolved' (L3, A-R, needs pinned resolver + LLM Arm B), and claim/contradiction detection requires the compiler's semantic lowering. The determinism is real only downstream of a frozen set of LLM-authored inputs; the spec sells it as end-to-end.

### Cross-layer conflicts (5)
- Three incompatible provenance/hash regimes are presented as one 'everything is pinned and hashed' story. L1 uses source_anchor.sha256 over raw bytes at a file+line_range. L6 uses content_hash = sha256(NORM_v1(extract_text(bytes, extractor_id))) and quote_hash under NORM_v1. L3 uses embedding_anchor.text_hash over DERIVED text. L1's numbers go through the QUANT canonical lexer (NFKC + grouping/decimal/dash normalization), a fourth normalization. The 'same' quote hashed under L1 (raw sha256) and under L6 (NORM_v1) will not match, and L4's ledger_ref double-lock is a substring check ('edge-attr subset quote subset text'), not a hash - so no single provenance identity spans the layers that are claimed to share one.
- L8 requires delta_ledger.magnitude.claimed_value AND baseline_value to be Q## ids into L1. But baseline_value is the PRIOR WORK's externally-fetched reported number (it carries a fetch_timestamp on the prior work's own reported value). L1 is defined as 'each load-bearing number authored once in THIS paper' and numeral_coverage forces every numeral 'in prose/tables' to be tagged. A prior-work baseline may never appear in this paper's prose at all. Either L1 must hold quantities that are not this paper's (breaking its definition and the coverage audit), or baseline_value cannot be a Q## (breaking L8's 'quantities are cited never copied' rule). §3 asserts the latter unification without resolving this.
- registry_authority maps every id-TYPE to an owning file and REGISTRY-RECONCILE hard-fails on any projection/ledger disagreement, but the id space includes types that the compile-time projection cannot faithfully contain: verdict ids live in append-only Tier-C logs written AFTER the deterministic skeleton by independent judges, and edge fingerprints/cg-nodes are computed. If registry_authority covers Tier-C verdict ids, nodes.yaml cannot be a faithful projection at compile time (the verdicts do not exist yet) without judges writing into the graph - violating the 'judges ride the graph, never author it' invariant. If it does not cover them, then 'every id resolves against a provably faithful projection' has an unstated exemption. The scope of registry_authority over Tiers B/C is undefined.
- The omission attack is only half-closed. L4 COV coverage is computed over NODES not prose, which catches RELABELING a typed fact (speculative-waiver bucket). But a fact the compiler never types - a claim buried in prose that is never given a C##, an assumption never entered - never becomes a node and is invisible to node-set coverage. L1 has numeral_coverage forcing every prose numeral into the ledger; there is NO analogous claim_coverage forcing every prose assertion into a C##, nor an assumption_coverage. So wholesale omission of claims/assumptions escapes the very layer that advertises 'closing the omission attack.'
- Honest-absence symmetry directly disarms the over-claim field-diff. The diff trips 'forall-over-sample' only when n is present; the spec states n=null -> UNDER_SPECIFIED, scored EQUAL to honest presence. Therefore the cheapest evasion of an over-generality penalty is to omit n, which the absence axiom protects. Axiom 4's carve-out ('penalized only when a deterministic expectation is violated') and the over-claim check are in tension: the check REQUIRES n to fire, so omitting n is a designed-in free pass, not a violated expectation.

### Missing / under-specified (7)
- P1 scores on 'discipline' - 'discipline pct p68,' 'per-discipline MAE/ICC,' 'within-discipline isotonic calibration,' 'cross-discipline percentile via reference-cohort CDF.' No layer in the id namespace (§3) emits a discipline field. Genre taxonomy emits paper_type, which is not discipline. Confirmed absent from all twelve source designs (grep of TOURNAMENT_DESIGNS.md finds 'discipline' only in the unrelated sense 'penalize-don't-skip discipline'). This is the canonical 'one layer assumes a field another never emits' defect, and the entire cross-discipline funder-ranking proposition rests on it.
- The 'independent resolver (not the compiler) attests planned_direction' for M04 outcome-switching presumes a designed step that extracts planned_direction / planned_measure as structured fields from a registry record. Registries (PROSPERO, ClinicalTrials.gov) store outcomes as free text; parsing planned_direction out of them is itself a Class-C semantic extraction that is designed nowhere. M04 is tagged 'afforded, A-R' but hides this un-built semantic resolver.
- L1 registry_ref{registered_value} presumes registries expose a posted numeric result to join against. Most registry records (PROSPERO protocols, many NCT entries) carry no posted numeric outcome. The fraction of the corpus where the M04 join can even run is never bounded; 'publication-bias afforded' overstates coverage.
- Independence is claimed as 'machine-checked' but the mechanism (authoring_pipeline_id inequality) is never specified to rule out shared model family, shared prompt lineage, or shared training corpus. What actually makes two passes independent, and how it is verified rather than declared, is the load-bearing gap under half the anti-fabrication claims.
- Total per-GRO judge cost is never quantified against the coda's 'hundred-thousand-paper corpus' promise. Tier C alone demands: P1 >=3 vendors x sealed pre-registered N runs; P2 J>=3 x R>=3 pool (~12 verdicts) per edge plus an INVARIANCE_AUDIT and CALIBRATION_REPORT; P3 >=5 judges over >=3 families plus a blind BCR twin ensemble; P4 K>=3 over >=2 families - each with rotating calibration governance. Scalability/feasibility of the reliability apparatus is asserted, not shown.
- The 'listed non-load-bearing' escape in L1's numeral_coverage is self-declared and lacks an independent check. A wrong or inconvenient numeral can be dumped into the non-load-bearing list; the audit only forces a numeral to be tagged, matched, OR listed - it does not verify that a listed numeral is truly non-load-bearing.
- 'ranking_ref -> ordinal/ranking integrity' is tagged D but never says what it checks beyond internal consistency of stated rank vs stated score. Whether a surrogate ranking (e.g. a network-meta-analysis P-score) was correctly computed requires the underlying data and is not afforded; 'ranking integrity' is oversold.

### Must-fix before final (11)
- Re-tag the metrics catalogue and the funder dossier so no compiler-authored-content metric is presented as 'deterministic': FOL-ability, contradiction detection, grounding fidelity, and M48 reproducibility must show their A-R/Class-C dependency at the funder surface, not only in a footnote. Grounding 0.98 must not sit under 'Tier A deterministic.'
- Introduce a discipline field with an owning ledger (or redefine P1's normalization to run over a field the format actually emits). Until then, cross-discipline percentile ranking - the headline funder affordance - is unsupported.
- Resolve the L1<->L8 baseline_value conflict: either define a distinct external-quantity id space for prior-work numbers (not Q##), or explicitly extend L1 to hold non-paper quantities and exempt them from numeral_coverage. State which.
- Define registry_authority's scope over Tiers B and C explicitly, and state how nodes.yaml stays a faithful projection when Tier-C verdict ids are minted after compile time by independent judges. Reconcile with the 'judges never author the graph' invariant.
- Specify what 'machine-checked independence' verifies beyond authoring_pipeline_id inequality, and downgrade every 'decorrelated' claim that rests on two LLMs to the strength the mechanism actually supports (only L3 Arm A earns genuine decorrelation).
- Pin where the P2 'contested' floor sits relative to a refuted/contradicted verdict and prove that steering a refutation into contested is not profitable; otherwise contested-as-floor is a laundering path for the worst claims.
- Add a claim_coverage (and assumption_coverage) forcing mechanism analogous to L1's numeral_coverage, or drop the claim that node-set coverage 'closes the omission attack' - it currently closes only relabeling, not wholesale non-typing.
- Add an independent check that a numeral listed 'non-load-bearing' is truly non-load-bearing, or acknowledge the non-load-bearing list as a residual self-declared Goodhart surface.
- Unify or rename the L6/L7 VerificationRecord: either make them genuinely one schema (one result enum, one hash model) or stop claiming a hoisted shared type and describe two related-but-distinct records.
- Design (or explicitly defer with an honest limitation) the planned_direction/planned_measure extraction step from free-text registry records; without it M04 is not 'afforded.'
- State the aggregate per-GRO inference cost of the Tier-C apparatus and reconcile it with the hundred-thousand-paper-corpus claim, or scope the corpus claim down.

## Refined finalists (VALIDITY, HARDSIGNALS) — the cut-off refine round, now run

### VALIDITY
**Merge rationale:** FROM B (Sonnet 5 / #2, kept as the spine): the four-file typed sidecar with honest-null symmetry; the deterministic set-difference for limitation novelty (`new_condition_added` computed, not asserted) — the only genuine determinism gain in the field; the citation-existence gate on method status; the severity-weighted FLOOR (not mean) — the only anti-dilution mechanism in the field; median+MAD dispersion; calibration-gated judge inclusion with visible exclusion; the produced-vs-input separation (report lives outside the compiler write surface); and the test-retest agreement meta-metric. FROM A (gpt-5.5-codex / #1, kept for the reproducibility half the judge said both winners must steal): the frozen-hash + rubric_version + calibration_set_id + judge_distribution + for/against panel record (`validity_panel_run`); the richer AssumptionRecord link structure (used_by, consequences, failure_modes→probe IDs, fairness groups); and the stress_probes with expected_breakpoint declared before judging. STOLEN FROM #3 (the judge's top pick, whose device was underspecified): Blind Counterfactual Reconstruction, here fully specified with an input firewall, ensemble stabilization, and the reconstructed∖declared omission set feeding the severity floor — this is the centerpiece anti-anchoring mechanism and it directly implements the mandate to redact self-assessment. STOLEN FROM #0: the genre-conditioned `validity_manifest` with `expected_validity_surfaces` (anti-omission: absence becomes checkable), `known_invalid_conditions` on method cards, and `expected_failure_signature` declared before judging. CUT: A's separate compiler-authored `domain_priors.yaml` — folded into an externally-governed Domain Baseline Registry that entries only POINT AT by ID, because a compiler authoring its own priors is a fabrication surface (B's insight); A's dense-prose schema presentation, replaced by B's clean typed YAML (judge critique: A's blobs were hard to validate/implement); heavy reliance on `sensitivity.quantitative_check` being populated, demoted to honest-null-first and lightly weighted (addresses B's own open question that most papers never report it). ADDED beyond both: the explicit deterministic/judged interface table (§A), two-stage structural enforcement of for/against-before-verdict, and separated within-family vs cross-family dispersion reporting to detect model-family bias.

**Residual risks:**
- A well-crafted fabricated ledger entry that cites real claim IDs but mischaracterizes the actual mechanism passes every deterministic gate; only the Class-C panel can catch it, so the verdict is never fully fabrication-proof — this is why Plane 2 stays judged.
- Blind reconstruction is itself an LLM step: if the ensemble shares a training-corpus blind spot, it may systematically fail to reconstruct a genuinely novel-but-necessary assumption, under-counting omissions for exactly the frontier work funders most care about. Reconstruction dispersion is reported but cannot fully bound this.
- The Domain Baseline Registry and calibration sets are new, expensive infrastructure with real governance/circularity risk; coverage is dense in reporting-guideline fields (RCTs, meta-analyses) and thin-to-absent in novel/interdisciplinary work, so the reliable-anchored fraction silently shrinks to fully-semantic precisely where it matters most. Disclosed via not_specified + degraded-mode flags, not solved.
- The whole panel is not run at every compile (compute/labor cost of ≥5 cross-family judges + human audit tier), so scores go stale relative to a living ARA; staleness is versioned but not eliminated.
- Registry/calibration-set version churn makes historical scores incomparable to new ones unless versions are pinned in every report; who is accountable when a calibration set is later found mislabeled is unresolved.
- No consensus benchmark exists for what test-retest agreement or ensemble diversity counts as 'reproducible enough' to publish a verdict rather than withhold it — the threshold is currently a governance choice, not a derived constant.
- Cross-field portability of 'reference prior' / 'standard practice' may fracture the single registry taxonomy into non-interoperable per-field sub-registries.

<details><summary>Full refined design</summary>

# The Realism Ledger + Blind-Reconstruction Validity Panel (BR-AMVP)

A two-plane design. **Plane 1 (deterministic, compiler-authored)** is a typed sidecar ledger that makes the *inputs* to a realism judgement computable and forces honest-absence symmetry. **Plane 2 (judged, produced/versioned)** is the Blind-Reconstruction Assumption-realism & Method-Validity Panel — a reproducible Class-C verdict record whose single most important anti-gaming device is that the "what should be here" baseline is generated *without ever reading the paper's own assumptions*, so the paper's narrative cannot anchor the judge. The two planes never share a write surface: Plane 1 lives under `logic/solution/validity/` (compiler writes it), Plane 2 lives under `trace/validity_panel/{run_id}.yaml` (only the protocol writes it, never hand-edited).

---

## A. The hard architectural split: deterministic vs. judged

The Class-C mandate says: separate the deterministic structural half from the judged half. This is not a slogan here — it is an interface. Every metric is decomposed into a **deterministic pre-gate** (pure code, no LLM, perfectly reproducible) and a **judged residual** (Class C). The pre-gate can only ever *cap or floor* a score or *route* an item; it never invents realism. If the pre-gate fails, the judged step never runs (you cannot judge the realism of an assumption whose source_anchor quote does not exist at the cited locator).

| Step | Plane | Reproducible? |
|---|---|---|
| Schema validation; every required field present or explicit `not_specified`/empty-list | 1 | Deterministic pass/fail |
| Foreign-key resolution (`affected_claims ⊆ C##`, `method_ref`/`anchored_in` resolve, `reference_prior.ref`/`verification_evidence.ref` resolve into `refs.yaml`) | 1 | Deterministic |
| Source-anchor quote verification (cited quote present at cited locator — reuse L1 §10 machinery) | 1 | Deterministic |
| Limitation novelty: set-difference of `scope_narrowing` axis vs. union of all `applicability_conditions` (M31 part a) | 1 | Deterministic set-op |
| Method-status credit gate: `status: widely_accepted` credited only if ≥1 `verification_evidence` resolves to a real citation/ablation (M32/M35 half) | 1 | Deterministic existence check |
| Perspective presence: count tags whose `anchored_in` resolves to a *distinct* real method/experiment section (M36 half) | 1 | Deterministic join |
| Base-rate lookup against pinned Domain Baseline Registry snapshot | 1 | Deterministic given snapshot version |
| **Blind counterfactual reconstruction** → declared∖reconstructed omission set | 1.5 | Semantic per-pair match, but computed blind to paper framing; ensemble-stabilized, dispersion reported |
| Realism verdict per assumption; limitation consequentiality; `applicability_match`; cross-lens triangulation genuineness | 2 | Judged — reproducibility *measured*, not assumed |

Everything above the blind-reconstruction line is genuinely deterministic and is where the affordance-gap doc's Class-A determinism is recovered. Everything below is honestly Class C and gets the full reproducibility apparatus in §D.

---

## B. Plane 1 — the typed sidecar ledger (`logic/solution/validity/`)

Six files, each rendered round-trippably into the human-readable `constraints.md` (prose stays the reading view; the sidecar is the joinable view; agreement between the two is itself a checkable anti-fabrication metric). **Every field carries first-class `not_specified` / `not_applicable` / empty-list values scored EQUAL to an honest resolved value** — this is the honest-absence symmetry both finalists and the affordance-gap doc's design-tension #1 demand, and without it the sidecar just relocates the Goodhart surface.

### B.1 `validity_manifest.yaml` — genre-conditioned expected surfaces (stolen from #0's anti-omission mechanism)
```yaml
paper_type: diagnostic_test_accuracy_nma      # enum, not free text
expected_validity_surfaces:                    # which surfaces this genre MUST address
  - surface: reference_standard_validity        # {declared | not_applicable + reason}
    status: declared
  - surface: cohort_independence
    status: declared
  - surface: external_validity_across_ancestry
    status: declared
  - surface: individual_level_generalization
    status: not_applicable
    reason: "aggregate synthesis; no patient-level claims made"
```
This converts silent absence into checkable absence (affordance-gap §2.6): an *expected-but-undeclared* surface is a coverage defect; an *explicitly n/a* surface is honest. The manifest is the first input to blind reconstruction (§C).

### B.2 `assumptions.yaml` — merged AssumptionRecord (A's link-richness + B's severity/necessity/reference_prior/testedness)
```yaml
- id: A02
  statement: "Selecting the single most comprehensive dataset per cohort yields statistically independent nodes."
  stated_by: explicit                    # explicit | inferred
  kind: independence                     # typed enum
  necessity: load_bearing                # load_bearing | convenience | robustness_check_only | not_specified
  used_by: {claims: [C01,C02,C05], methods: [MV01]}
  consequence_if_false:
    failure_mode: "Duplicated patients inflate evidence, biasing P-scores upward for over-represented nodes."
    affected_claims: [C01,C02,C05]
    severity: invalidates_main_claim     # invalidates_main_claim | narrows_scope | negligible | not_specified
  applicability_conditions:
    - {condition: "accurate cohort-overlap screening at selection", scope: population, source_anchor: {...}}
  sensitivity: {level: not_specified, quantitative_check: not_specified}   # honest-null-first (see residual risk)
  reference_prior:
    domain_baseline_ref: "baseline:nma-cohort-independence-v2"   # ID into external registry, NOT a compiler-authored prior
    alignment: matches_known_standard                            # populated deterministically FROM the registry, not by the compiler
    note: "De-dup by patient ID is the PRISMA-DTA/Cochrane NMA standard control."
  tested_in_paper: no                    # yes_sensitivity_analysis | yes_ablation | no | not_applicable
  fairness: {affected_groups: [{entity_id: POP_underrepresented_ancestry}], concern: "threshold transportability", evidence_status: not_specified}
  source_anchor: {file: "logic/solution/study_design.md", locator: "§3.2", quote: "the most comprehensive dataset ... was selected to avoid double-counting"}
```

### B.3 `limitations.yaml` — B's determinism gain (the only genuine one across the field)
`new_condition_added` is **computed, not asserted**: a pure set-difference between this limitation's `scope_narrowing.axis` and the union of every `applicability_conditions.scope` already declared across `assumptions.yaml`. `true` only if it narrows scope along an axis/population not already covered. This is M31's core question made deterministic-where-possible.
```yaml
- id: L01
  statement: "Residual batch effects in manual immunoassays may persist despite platform adjustment."
  relates_to_assumptions: [A02]
  scope_narrowing: {axis: measurement_platform, population_or_setting: "manual (non-automated) immunoassay results"}
  new_condition_added: true              # COMPUTED by set-difference; compiler cannot set this
  not_duplicate_of_assumption: {value: true, rationale: "adds a platform axis, not a restatement of independence"}
  residual_risk: high
  source_anchor: {...}
```

### B.4 `methods.yaml` — method verification (A's status/overgeneralization + #0's known_invalid_conditions + B's citation-gated credit)
```yaml
- id: MV01
  method_ref: "logic/solution/study_design.md#nma"
  method_family: diagnostic_test_accuracy_network_meta_analysis
  status: widely_accepted_in_field       # credited ONLY if verification_evidence resolves (deterministic gate)
  verification_evidence:
    - {type: prior_validation_citation, ref: "refs:rucker2015netmeta"}
    - {type: internal_sensitivity_check, ref: {file: "evidence/tables/table2.md", locator: "excl. high-RoB studies"}}
  required_assumptions: [A02, A04]
  known_invalid_conditions:              # from #0 — declared before judging
    - "network disconnected across an outcome"
    - "strong intransitivity between direct/indirect comparisons"
  overgeneralization_risks: [{claim: C01, risk: "ranking overread as individual-patient superiority"}]
  applicability_match:
    claim: "network confirmed connected/transitive across all four outcomes"
    source_anchor: {file: "logic/solution/study_design.md", locator: "§3.4", quote: "network geometry confirmed connected"}
  novelty: established_use
```

### B.5 `perspectives.yaml` — anchored tags (B); a tag with no resolvable distinct anchor is dropped, not scored.

### B.6 `stress_probes.yaml` — A + #0: expected_breakpoint AND `expected_failure_signature` declared *before* the panel scores; `run_status: run|not_run` with `absence_reason`. A preregistered probe with a declared breakpoint counts even when unrun — this rewards honesty about what could not be executed.

**Dependencies (shared with the affordance-gap prescription):** this layer requires the sibling `refs.yaml` (normalized citation table) and `quantities.yaml` (typed quantity ledger) to exist, so `reference_prior.ref` / `verification_evidence.ref` / `sensitivity.quantitative_check` resolve by ID rather than re-parsed prose.

---

## C. The centerpiece: Blind Counterfactual Reconstruction (BCR)

This is #3's "single best anti-gaming device," which the judge flagged as underspecified. Here it is specified. **It attacks the exact failure mode of "read the chain and grade if it feels real": the paper's own framing anchoring the judge.**

**Reconstruction agent inputs (what it CAN see):** `claims.md` statements + `claim_type` (redacted of authorial hedges/confidence language), `method_family` from `methods.yaml`, `paper_type` + `expected_validity_surfaces` from the manifest, `quantities.yaml`, the resolved `refs.yaml` neighborhood, and the Domain Baseline Registry base-rate entries for `(field, method_family)`.

**Withheld (what it CANNOT see):** `assumptions.yaml`, `limitations.yaml`, `constraints.md` prose, and the paper's Discussion/Limitations section. This is the redaction-of-self-assessment mandate, enforced as an input firewall.

**Task:** "Enumerate the assumptions a competent study of `paper_type` P, using `method_family` M, asserting claims C over quantities Q, MUST rely on for its main claims to hold — each with kind, why load-bearing, and failure mode if violated. Then enumerate the limitations such a study necessarily has." Output is emitted in the *identical* typed shape as AssumptionRecord/LimitationRecord, so it joins.

**Stabilization (BCR is itself Class C, so it gets ensembled too):** run the reconstruction across the same diverse model-family ensemble as the panel. The **consensus reconstructed set** = assumptions appearing in ≥⌈n/2⌉ independent reconstructions. Report reconstruction dispersion as its own number.

**Deterministic set operations over consensus_reconstructed vs. declared:**
- `coverage = |declared ∩ reconstructed| / |reconstructed|` → assumption-disclosure completeness (anti-omission).
- `omitted_load_bearing = (reconstructed ∖ declared)` filtered to `necessity=load_bearing` → **the sharpest signal**: load-bearing assumptions the method itself demands that the paper never disclosed. Each is a validity defect that the severity floor (§D.7) prevents diluting.
- `over_declared = declared ∖ reconstructed` → routed to the panel: genuine extra disclosure (credit) vs. padding (no credit).

The ∩/∖ operations require a per-pair "does reconstructed R_k match declared D_j?" judgement — this is semantic and I will not pretend otherwise. But it is a radically constrained yes/no per pair, made *blind to the paper's rhetoric*, and it is exactly the constrained-input-to-a-cheaper-judge move the affordance-gap doc §4 says is the most a format can do for Class C.

---

## D. Plane 2 — the Calibrated Validity Panel (BR-AMVP protocol)

Produces `trace/validity_panel/{run_id}.yaml`. Run at funding-review / ARA-comparison time (not every compile). It turns each ledger entry into a reproducible verdict. Every item of the Class-C mandate maps to a concrete mechanism:

**D.1 Identical templated probes (minimize judge degrees of freedom).** One stress-probe per ledger entry from a fixed template keyed by `kind`/`severity`/`tested_in_paper` — identical structure for every ARA of the same assumption kind. This is the single biggest lever against framing variance. Template carries the statement, failure_mode, affected_claims, the consensus-reconstructed baseline, and the registry base rate.

**D.2 For/against BEFORE verdict, structurally enforced (two-stage).** Stage 1: the judge emits ONLY `for` (strongest case it is standard) and `against` (strongest known violation/edge case) — the verdict enum is not in the stage-1 schema and cannot be written. Stage 2: given its own frozen stage-1 text, the judge emits `realism_verdict ∈ {dreamcase_idealized, contested_in_field, standard_in_field, not_evaluable}` + `confidence` + one-sentence rationale. A verdict with an empty `for` or `against` is rejected by the validator. This defeats verdict-first rationalization, not merely records it.

**D.3 Redacted self-assessment.** The probe shows the assumption *statement* and the reconstructed baseline + registry base rate; it does NOT show the paper's own "we believe this is reasonable" prose or its stated confidence. Anchoring language is stripped at probe-assembly time.

**D.4 Ensemble across model FAMILIES (not temperatures).** ≥5 judges spanning ≥3 distinct model families, to avoid correlated failure — B's explicit point. Within-family and cross-family dispersion are reported *separately*, so a verdict that only holds within one family is visibly fragile.

**D.5 Versioned calibration anchor + calibration-gated inclusion.** Interleave, blind to the judge, items from a versioned expert-labeled calibration set (known-hard exemplars spanning dreamcase→standard) among the real items in the same batch. Score each judge's `calibration_accuracy` against the labels; judges below a published threshold (e.g. 0.7) are excluded from the aggregate **and the exclusion is recorded, not hidden**. The calibration set is curated by a neutral metascience body, NOT the scoring platform — otherwise the whole Class-C layer is circular.

**D.6 Aggregate via median + dispersion, never mean.** Per item: median verdict + MAD dispersion. Any item with high dispersion OR (high severity AND low realism verdict) → `flag_for_human_review: true`, routing the highest-stakes ~10-20% to a human domain-expert spot-audit pool.

**D.7 Severity-weighted floor at roll-up (the only anti-dilution mechanism in the field — B's, kept).** ARA-level score is a floor function, not an average, over per-item verdicts weighted so that `untested (tested_in_paper=no) + load_bearing + high-severity` assumptions dominate. One fabricated load-bearing unrealistic assumption cannot be buried under a pile of trivially-true ones. **The `omitted_load_bearing` set from §C feeds directly into this floor** — an undisclosed method-mandated assumption counts against the score as if it were declared-and-unrealistic.

**D.8 Frozen-hash + snapshot discipline (stolen from #1/Finalist A — "the missing reproducibility half").** The report records `inputs_frozen_hashes` (of every ledger file + refs + quantities), `rubric_version`, `calibration_set_version`, `registry_snapshot_version`, and each judge's `calibration_accuracy` and `included_in_aggregate` flag. Full for/against transcripts are retained: the audit trail IS the product.

**D.9 Reproducibility is MEASURED, not assumed (rerun-delta).** Re-run the identical `(rubric_version, calibration_set_version, registry_snapshot_version)` against the same frozen ledger and publish the **test-retest agreement rate** (fraction of items whose median_verdict is unchanged) as a confidence envelope printed alongside every score. If the ecosystem lets protocol health degrade (stale calibration, under-diverse ensemble), this number drops visibly instead of hiding inside a confident float.

### Produced record (shape)
```yaml
protocol_version: "BR-AMVP-1.0"
run_id: "2026-07-07T00:00:00Z_che26_run1"
frozen_inputs: {assumptions_sha: ..., refs_sha: ..., quantities_sha: ...}
rubric_version: "v1.0"; calibration_set_version: "calib-dta-nma-v3"; registry_snapshot_version: "dbr-2026-06"
reconstruction:
  ensemble_n: 5; consensus_reconstructed_ids: [R1..R9]; reconstruction_dispersion: 0.12
  coverage: 0.78
  omitted_load_bearing: [{recon_id: R7, kind: transitivity, failure_mode: "..."}]   # method demands it; paper never declared it
  over_declared: [{assumption_id: A11, panel_route: padding_check}]
judges:
  - {judge_id: fam_A_t0.2, family: A, calibration_accuracy: 0.92, included: true}
  - {judge_id: fam_B_t0.5, family: B, calibration_accuracy: 0.55, included: false}   # gated out, visible
per_item:
  - target: A02; metric: M30
    for: "matches PRISMA-DTA cohort-independence standard; de-overlap documented"
    against: "registry cross-matching can miss undocumented cohort mergers"
    median_verdict: standard_in_field; within_family_mad: 0.05; cross_family_mad: 0.11
    base_rate: {corpus: dta_nma, prevalence_declaring: 0.61, prevalence_with_sensitivity_analysis: 0.18}
    flag_for_human_review: false
arc_summary:                              # severity-weighted floor, NOT mean
  assumption_realism_score: 0.74; high_risk_untested_or_omitted: [R7]
  limitation_validity_score: 0.74; method_validity_score: 0.88
protocol_health: {test_retest_agreement: 0.91, ensemble_families: 3, calibration_pass_rate: 0.8}
```

---

## E. Metrics afforded + concrete anti-Goodhart defenses

- **M30 assumption realism & fairness** — severity-weighted floor of per-assumption median verdicts, with `omitted_load_bearing` folded in. *Exploit:* pad with trivial true assumptions to dilute one unrealistic load-bearing one → **defeated by the severity-weighted floor** (worst load-bearing item dominates). *Exploit:* omit a load-bearing assumption entirely so there's nothing to grade → **defeated by BCR** (reconstruction surfaces it as `omitted_load_bearing` and it counts against the floor). *Exploit:* fabricate a `reference_prior` to inflate realism → **defeated because `alignment` is populated only from a resolved registry entry**; an unresolvable/fabricated anchor is capped at `not_specified` (= honest absence, never rewarded above it). *Exploit:* judge sycophancy → **defeated by forced for/against-before-verdict, calibration-gated inclusion, and published rerun-delta**.
- **M31 limitation validity** — part (a) deterministic set-difference (`new_condition_added`); part (b) panel judges whether the added condition is specific+consequential. *Exploit:* restate a declared boundary as "new" → **defeated by the pure set-difference join**. *Exploit:* vague "results may not generalize" → **fails the structural test** (must name a typed `scope_narrowing.axis`/population) before a judge even runs.
- **M32/M35 method validity & verification status** — status credit is a **deterministic citation-existence gate**; `applicability_match` is panel-judged against specific claim/experiment IDs. *Exploit:* assert `widely_accepted` with no citation → **capped at `not_specified`-equivalent**. *Exploit:* boilerplate justification → **must anchor to specific claim IDs + the method's `known_invalid_conditions`**, giving the judge a structural check to fail it against.
- **M36 multi-perspective adequacy** — deterministic count of distinct anchored tags; panel judges genuine cross-lens stress-testing for ≥2 resolved perspectives. *Exploit:* self-label one analysis under two tags → **dropped unless each anchors to a genuinely distinct section**. *Exploit:* two lenses co-exist but never cross-check → **the judge specifically probes for triangulation evidence**, calibration-gated.
- **Protocol-health meta-metric (rerun-delta)** — the check on whether the above can be trusted at all in a given run; published every time so silent degradation is visible.

---

## F. Worked example (che26, amyloid-PET diagnostic NMA)
The paper declares A02 (cohort independence) but its `constraints.md` never states a **transitivity** assumption. Plane 1 validates A02's schema and resolves its anchors deterministically; `reference_prior` resolves to `baseline:nma-cohort-independence-v2` → `alignment: matches_known_standard` (compiler could not have set this itself). BCR — reading only the claims, `method_family=dta_nma`, and the registry — reconstructs R7 "direct/indirect comparisons are transitive," a load-bearing requirement of *any* NMA. Set-difference: R7 ∈ `reconstructed ∖ declared`, `necessity=load_bearing` → `omitted_load_bearing`. The panel, blind to the paper's framing, returns `standard_in_field` for A02 (median, cross-family MAD 0.11) but the undisclosed R7 pulls the severity-weighted floor down and flags for human review. Rerun-delta 0.91 is published as the confidence envelope. A vibe-check judge reading the paper's confident Methods section would have missed R7 entirely — that is the value of blind reconstruction.

---

## G. Honest limits (what is NOT made deterministic)
The verdict itself stays Class C. A sufficiently well-written fabricated ledger entry that cites real claim IDs but *mischaracterizes the mechanism* can pass every deterministic gate — this residual is precisely why Plane 2 exists and is judged, not asserted. What the design delivers is: the *inputs* (what breaks, how sensitive, is there field precedent, was it tested, what did the method silently require) are deterministic and auditable; the verdict is reproducible-and-contestable (frozen inputs, versioned rubric/calibration/registry, cross-family ensemble, published dispersion + rerun-delta) rather than fabricated-deterministic or a single-shot vibe.

</details>

### HARDSIGNALS
**Merge rationale:** SPINE FROM B (FLCG): the tiered tagged-union comparator (measured_ablation > external_benchmark > theoretical_bound > argued > not_applicable) is the mandate's "separate the deterministic structural half from the judged half" made structural — distance is arithmetic for tiers 1-3 and only judged for tier 4. Kept: the shared judge_panels.yaml, the ID-joined four-axis independence, the integrity-violation auto-downgrade on failed external resolution, honest-null symmetry.

STOLEN FROM A (FrontierTriangulation): the richer, harder frontier half — objective_vector, frozen_candidate_set (now hash-pinned), Pareto rank percentile, and uncertainty — folded into B's measured/benchmark tiers so multi-objective frontiers are first-class rather than B's single-number-only comparator.

STOLEN FROM #3: the compiler/evaluator/judge producer separation (so the compiler is never pressured to invent a frontier — judged slots are literally emitted as pending_judge); the circularity_check (fail if the optimum is the heuristic re-dressed); and first-class orthogonal/insufficient_info corroboration verdicts.

STOLEN FROM #1: OBI/controlled-vocab method_class anchoring and the adversarial missing-candidate audit baked into the frontier protocol.

FIXES TO B's FIVE NAMED GAPS: (1) tier≠confidence — confidence is now a DERIVED evaluator table decoupling "how obtained" (tier) from "how much to trust" (confidence). (2) unnormalized distance — a structured distance object with a bounded normalized_regret whose denominator is a DECLARED reference_floor, which simultaneously fixes A's unconstrained-normalizer flaw; returns not_normalizable honestly rather than faking a [0,1]. (3) unspecified product — triangulation_strength = independence × agreement fully specified, with explicit per-axis independence, min-over-pairs weakest-link, same-data-forced-0, and CI-overlap/sign-match agreement formulas. (4) vanity rerun — the reproducibility check now perturbs ordering/seeds/adds a held-out third family and reports within-run IQR + cross_family_spread + rerun-delta as three distinct stability signals. (5) hand-waved calibration — concrete versioned+hashed corpus, named steward, private canaries, and a per-run calibration_accuracy gate that drops miscalibrated judges from the aggregate.

CLOSED #3's OWN HOLE: not_specified independence axes count as NOT independent (conservative) and trigger insufficient_info past a threshold — the exact opposite of #3's denominator-exclusion that let a lazy compiler fake 1.0 independence.

CUT: #1's ordinal self-reported overlap levels (the gameable self-report the design exists to eliminate) and any bare-point-estimate judged score.

**Residual risks:**
- Tier-laundering: a mechanically-valid but strawman-handicapped ablation passes tier-1 checks; judging whether a counterfactual is FAIR is itself Class C. The missing-candidate audit mitigates but does not close this.
- Calibration-corpus capture and pretraining contamination: canaries + calibration_accuracy gating raise the cost of a memorized/gamed corpus but depend on a steward institution that does not yet exist and on canaries refreshing faster than leakage.
- Design is non-self-sufficient: tiers 1-3 distance and axis independence degrade to prose-parsing without the sibling quantities.yaml, refs.yaml, and OBI method/dataset xref layers.
- Perspective granularity gaming: OBI anchoring plus weakest-link/min and same-data-forced-0 bound but do not eliminate splitting perspectives upward or lumping them downward to dodge the independence audit.
- Cross-heuristic / cross-domain distance is deliberately left un-aggregable (not_normalizable rather than a faked [0,1]) — a funder wanting one composite M39 number will not get one, by design.
- Judge-ensemble cost and cross-family availability: a meaningful ensemble needs ≥2 structurally distinct model families at temp 0 plus a perturbed rerun, which is expensive per argued heuristic and per qualitative triangulation.

<details><summary>Full refined design</summary>

## Frontier & Corroboration Ledger (FCL) — hardened finalist

A thin typed sidecar that makes two currently-missing objects explicit and *separates three producers* so the compiler is never pressured to invent numbers:

1. **Compiler** emits only structural, source-anchorable fields (tiers, comparator refs, counterfactuals, perspective axes, findings). It never writes a distance for the judged tier and never writes a corroboration verdict — those slots are emitted as `pending_judge`.
2. **A deterministic evaluator** (post-compile, no LLM, replayable) computes every arithmetic quantity: tier-1/2/3 distance, independence score, quantitative/directional agreement, triangulation strength, and *derived* confidence.
3. **A bounded Class-C judge protocol** fills only the irreducibly semantic slots: argued-tier distance, qualitative agreement, the shared-confound corroboration verdict, and the adversarial missing-candidate audit — and writes them into a shared, versioned, calibration-anchored panel ledger.

This tri-partite split is the central anti-fabrication move: the *only* place a number can be invented is the judged slot, and that slot is redacted, ensembled, calibration-scored, and rerun-checked.

---

### Component 1 — Heuristic block extension (in-place, `logic/solution/heuristics.md`)

Adds the minimum vocabulary to even ask "distance from what?", emitted by the compiler:

- `shortcut_dimension : enum{compute_cost, sample_size, approximation_error, assumption_strength, search_space_pruning, generalization_scope, other}` — required.
- `ideal_counterfactual : string` — required; plain-language non-shortcut approach, independent of whether it was ever measured.
- `frontier_ref : F## | not_applicable` — required.

(existing Rationale/Sensitivity/Bounds/Code ref/Source unchanged.)

---

### Component 2 — `logic/solution/frontier.yaml` (the reference-frame ledger)

One record per applicable heuristic. **Tagged union keyed by evidentiary tier**, merging B's tier spine with A's multi-objective richness in the measured/benchmark tiers.

```
id                    : F## — required
heuristic_ref         : H## — required, must resolve
shortcut_dimension    : enum (mirrors heuristics.md)
ideal_counterfactual  : string
applicability         : enum{applicable, not_applicable}
not_applicable_reason : string — required iff not_applicable; source-anchored
tier                  : enum{measured_ablation, external_benchmark, theoretical_bound, argued, not_applicable}
objective_vector      : list[{id, name, direction, quantity_ref}] | null   # A's contribution; >1 entry ⇒ multi-objective/Pareto
frozen_candidate_set  : {candidates: [ref-ids], frozen_hash, constraints}   # A's frozen feasible set; hash pins it against post-hoc editing
comparator            : tagged-union (shape depends on tier — see below)
circularity_check     : {frontier_method_class, heuristic_method_class, distinct: bool}  # #3: fail if optimum IS the heuristic re-dressed
# ---- fields below are NOT compiler-emitted ----
distance              : {raw, normalized_regret, ...}  # evaluator (tiers 1-3) OR judge (argued); see Distance spec
confidence            : enum{high, medium, low, null}  # DERIVED by evaluator, never asserted
missing_candidate_audit : {ran: bool, stronger_candidate_found: bool, note}  # judge protocol
source_anchor         : {value_ids|ref_ids, source_file, locator, quote} — required unless not_applicable
```

`comparator` shapes:
- `measured_ablation: {heuristic_quantity_id, ideal_quantity_id}` (+ optional per-objective quantity refs for the multi-objective case) — both into `quantities.yaml`.
- `external_benchmark: {ref_id→refs.yaml, reported_value, unit, registry_snapshot_date}`.
- `theoretical_bound: {ref_id, bound_value, bound_type, unit}`.
- `argued: {judge_panel_id}` → `judge_panels.yaml`.
- `not_applicable`: null.

#### Distance spec (fixes B's "unnormalized distance" **and** A's "unconstrained regret normalizer")

`distance` is a structured object carrying *both* a raw arithmetic gap and a bounded regret whose denominator is a **declared reference floor**, not a free normalizer:

```
distance:
  raw: {value, unit, direction, ci}                 # always, arithmetic for tiers 1-3
  normalized_regret:
    method: enum{baseline_relative, bound_relative, pareto_rank_percentile, not_normalizable}
    reference_floor: ref-id | null                  # the baseline/random/trivial anchor; REQUIRED unless not_normalizable
    value: [0,1] | null
    clipped: bool                                   # true if heuristic fell outside [floor, ideal]; flagged, not hidden
```

- `baseline_relative`: `regret = |ideal − heuristic| / |ideal − reference_floor|`. Bounded [0,1] iff heuristic ∈ [floor, ideal]; otherwise clip to [0,1] and set `clipped=true`.
- `bound_relative`: same shape against a theoretical bound.
- `pareto_rank_percentile` (multi-objective): fraction of the `frozen_candidate_set` the heuristic Pareto-dominates. Deterministic over the frozen set.
- `not_normalizable`: honest null when no bounded reference floor exists or objectives are incomparable. **We do not fake a [0,1] number to enable aggregation** — distance stays a per-heuristic disclosure (see open questions).

The denominator is now *always* a declared, source-anchored `reference_floor`, closing A's "unconstrained normalizer" and giving B a bounded number.

#### Confidence derivation (fixes B's "tier ≠ confidence")

`confidence` is **decoupled from tier** and computed by an explicit evaluator table — tier says *how the comparator was obtained*, confidence says *how much to trust the distance*:

| tier | comparator_match | dispersion | ⇒ confidence |
|---|---|---|---|
| measured_ablation | same fold/cohort/run (shared experiment id in source_anchor) + narrow CI | — | high |
| measured_ablation | mismatched fold/construct | — | medium (+ "counterfactual not matched" flag) |
| external_benchmark / theoretical_bound | resolver-verified value matches | — | high |
| external_benchmark | resolver fails or value contradicts | — | **auto-downgrade to `argued` + integrity-violation flag** |
| argued | — | judge IQR small ∧ rerun stable ∧ calibration-accuracy ≥ threshold | high |
| argued | — | any of those fails | medium / low |
| not_applicable | — | — | null |

---

### Component 3 — `judge_panels.yaml` (shared ensemble ledger; serves both metrics)

One reusable elicitation record for both Class-C overlays (argued-tier distance, corroboration verdict). This is where the class mandate is discharged.

```
id                  : JP##
purpose             : enum{frontier_distance, triangulation_corroboration}
target_ref          : F## | T##
calibration_set_id  : versioned corpus id (e.g. distance-calib-v3)  # see Calibration spec
prompt_version      : frozen rubric text hash (for replay)
blinding            : {self_assessment_redacted: true}              # mandate: redact self-assessment
judges: list[K≥3] of
  {model_id, model_family, decoding_temp: 0.0,
   for:     [structured pro points],     # mandate: for/against BEFORE verdict — schema orders these before verdict_value
   against: [structured con points],
   verdict_value: number,
   calibration_accuracy: [0,1]}          # judge's accuracy on embedded gold exemplars this run
constraints:
  - model_family must span ≥2 distinct families  # mandate: cross-family ensemble
  - a judge with calibration_accuracy < threshold is EXCLUDED from aggregate and flagged
aggregate           : {median, iqr, n_judges, cross_family_spread}  # DERIVED; cross_family_spread = between-family verdict range
reproducibility_check:
  {rerun_id, perturbation: [reorder_inputs, reseed, held_out_third_family],
   rerun_median, delta, stable: bool}     # see Rerun spec
```

#### Rerun spec (fixes B's "vanity rerun")

The reproducibility check is a **meaningfully perturbed** rerun, not an identical replay:
- perturbs input ordering, reseeds, and substitutes a held-out judge from a *third* model family (or a paraphrase-invariant prompt at the same `prompt_version` semantics).
- reports three distinct stability signals — the mandate's "dispersion + rerun-delta" made concrete:
  1. within-run `iqr` (agreement among judges this run),
  2. `cross_family_spread` (a low IQR with high cross-family spread is the real hidden instability B's design missed),
  3. `delta` between run and perturbed rerun, with `stable = delta ≤ disclosed_threshold`.
- Instability *discounts confidence* (per the table above); it is never hidden.

#### Calibration spec (fixes B's "hand-waved calibration corpus")

The corpus does real anti-gaming work rather than merely "anchoring the rubric":
- **Content**: expert-labeled `{stimulus, gold_label, gold_rationale, difficulty}` exemplars spanning known-good heuristics, known-bad shortcuts, honest no-optimum cases (distance corpus); known-genuine vs known-spurious corroboration cases (triangulation corpus).
- **Governance**: named steward body; each release is versioned + content-hashed with a change-log; a run pins `calibration_set_id`.
- **Contamination guard**: (a) a private canary subset held out of every published release and refreshed each version; (b) each panel embeds N gold items and scores every judge's `calibration_accuracy`; a judge below threshold is dropped from the aggregate. This converts the calibration set from a prompt decoration into a per-run reliability gate — the auditability anchor the mandate demands.

---

### Component 4 — `logic/perspectives.yaml` (independent-lens registry)

Compiler-emitted; makes "a perspective" an ID-joined object so independence is a structural join, not a self-report.

```
id            : P##
label         : string
type          : enum{wet_lab_experimental, computational_simulation, statistical_inference,
                     observational_cohort, literature_meta_analytic, theoretical_derivation,
                     expert_elicitation, other}
data_source_id: dataset-ledger ref | novel_this_work | not_specified
method_class  : ref into OBI/controlled-vocab method ontology (sibling M64/S9), NOT free text  # #1's ontology anchoring
team          : string | not_specified
assumption_set: list[A## refs] (may be empty)
instruments   : list[string]
produces      : list[quantity-ledger refs]   # exhaustive-by-construction: every quantity bearing on a claim
```

Exhaustive-by-construction (every perspective producing a claim-relevant quantity must be registered) is what makes agreement cherry-picking a *detectable coverage gap* rather than an invisible omission.

---

### Component 5 — `logic/triangulations.yaml` (perspective × claim corroboration edges)

```
id            : T##
claim_ref     : C##
perspectives  : list[P##], length ≥2
independence  : {axes:{data_source, method_class, team, assumption_set}: 'same'|'differ'|'not_specified',
                 score, insufficient_info: bool}     # evaluator; see formula
agreement     : {method: enum{quantitative_pooled, directional_concordance, qualitative_concordance},
                 perspective_findings:[{perspective, quantity_id, direction, value}],
                 score: [0,1] | null}                 # evaluator for quant/directional; null→judge for qualitative
triangulation_strength : [0,1] | null                 # evaluator; explicit formula below
corroboration_judgment : {judge_panel_id, verdict, for, against, confidence}   # pending_judge until protocol runs
```

#### Explicit functions (fixes B's "unspecified product" and #3's independence-inflation hole)

**Independence** — over the four axes, per pair:
- `differ` counts toward independence; `same` and **`not_specified` both count as NOT independent** (conservative — this closes #3's Goodhart hole where `not_specified` was excluded from the denominator to fake 1.0).
- `pair_independence = count(differ) / 4`.
- If a pair shares an identical `data_source_id`, that pair's independence is forced to 0 (same data ⇒ not triangulation; routed to the S17/M25 replication metric).
- If ≥ 2 of 4 axes are `not_specified` for a pair, set `insufficient_info: true`, `score: null` → routed to the judge, never scored as high independence.
- **For >2 perspectives: `independence.score = min over all pairs` (weakest link)**, not mean — prevents padding a genuine pair with decorative lenses.

**Agreement** ∈ [0,1]:
- `quantitative_pooled`: `1 − normalized_distance` via CI-overlap between the perspectives' quantity ledger values (deterministic formula, same normalizer discipline as frontier distance).
- `directional_concordance`: fraction of perspective pairs with matching `direction` sign (deterministic).
- `qualitative_concordance`: `null` → judge.

**Triangulation strength**: `triangulation_strength = independence.score × agreement.score`, computed **only when both are non-null**, ∈ [0,1]. Fully specified, no hidden composition.

**Corroboration verdict** (Class C overlay) enum, extended with #3's honest states:
`{strong_corroboration, weak_corroboration, spurious_agreement, conflicting, orthogonal, insufficient_info}`. Required whenever `triangulation_strength ≥ disclosed_threshold` OR `agreement.method = qualitative_concordance` OR `insufficient_info`. The judge's for/against is scoped to exactly two questions: (a) an undeclared shared confound the four axes miss (same reference genome, same PI behind two "team" strings, same upstream preprocessing); (b) whether agreement is substantive or coincidental given effect sizes. A structurally-perfect record can still be downgraded to `spurious_agreement` — and that downgrade, shown beside the structural strength, is the headline number.

---

### Protocols (producer-tagged)

- **Ablation-Anchored Frontier (tier 1, deterministic evaluator).** Join the two comparable quantities; compute `raw` distance + `normalized_regret` against the declared reference floor; propagate CIs; set confidence via the table (downgrade if folds mismatch). Rerun ⇒ identical value.
- **External Frontier Resolution (tiers 2–3, deterministic + resolver).** Cite comparator by `ref_id`; a versioned resolver confirms `reported_value`/`bound_value` at a pinned `registry_snapshot_date`. On resolution failure or contradiction, auto-downgrade to `argued` **and flag an integrity violation** (scores strictly worse than an honest argued declaration). Mirrors the existing DOI-verification pattern.
- **Argued-Tier Distance Elicitation (tier 4, Class C).** Show 3–5 frozen calibration exemplars (never the full corpus); redact the paper's self-assessment; run K≥3 judges across ≥2 families at temp 0, for/against before verdict; drop low-calibration-accuracy judges; report median + IQR + cross_family_spread; run the perturbed rerun; derive confidence.
- **Perspective Independence Audit (deterministic evaluator).** Join on the four axis IDs; apply the independence formula incl. `not_specified`-conservative and same-data-forced-0 rules; route `insufficient_info` and independence-0 pairs away from triangulation credit.
- **Corroboration Verdict Elicitation (Class C overlay).** Judge sees only the T## structured fields + source spans (not the paper's "we triangulated X" narrative); for/against scoped to shared-confound and substantive-vs-coincidental; verdict incl. orthogonal/insufficient_info; perturbed rerun for stability.
- **Adversarial Missing-Candidate Audit (Class C, #1's contribution, applies to frontier + Pareto).** One judge role proposes a candidate that *should* be in `frozen_candidate_set`/feasible set but isn't; if a stronger candidate is found, the frozen set is flagged incomplete and the distance is marked provisional. Directly attacks the "invent an easy optimum / omit hard candidates" exploit.
- **Circularity Check (deterministic where method_class IDs exist; #3's contribution).** Fail the frontier if its derivation `method_class` equals the heuristic's `method_class` — the "optimum" would just be the heuristic re-dressed.

---

### Metrics afforded

- **Frontier Coverage & Tier-Honesty Index** — fraction of H## with a frontier record + tier declared; distribution across tiers; fraction of `not_applicable` carrying a substantive vs placeholder reason. `[deterministic]`. *Anti-Goodhart:* padding trivial heuristics fails the sibling comprehensiveness metric (M38); `not_applicable` scores **equal** to a resolved frontier, removing the incentive to dodge, while a boilerplate reason is visibly distinguishable.
- **Measured/Bound Distance-from-Optimum (tiers 1-3)** — `raw` + `normalized_regret` read off `frontier.yaml.distance`. `[reliable-anchored]`. *Anti-Goodhart:* external comparators must resolve and match or auto-downgrade+flag; the declared reference floor bounds the normalizer; circularity check blocks self-referential optima.
- **Argued Distance-from-Optimum (tier 4, M39's core)** — median panel verdict + IQR + cross_family_spread + rerun-delta as the confidence band, never a bare point. `[semantic-judged]`. *Anti-Goodhart:* self-assessment redacted; ≥2 families; calibration-accuracy gate drops lenient/miscalibrated judges; for/against-before-verdict; missing-candidate audit.
- **Perspective Independence Score (structural half of S6/M36)** — `count(differ)/4` with not_specified-conservative, same-data-forced-0, weakest-link-over-pairs. `[deterministic]`. *Anti-Goodhart:* axes are joins to sibling typed IDs, so a relabeled pipeline is mechanically caught; not_specified cannot inflate; independence-0 routed to the replication metric.
- **Agreement Score (structural half)** — CI-overlap / sign-match, deterministic; qualitative deferred to judge. `[deterministic]`. *Anti-Goodhart:* exhaustive perspective registry makes an omitted relevant lens a detectable coverage gap, not a hidden cherry-pick.
- **Triangulation Strength & Corroboration Verdict (S6/M36's core)** — `independence × agreement`, overlaid with a judge verdict that can downgrade to spurious/orthogonal/insufficient_info. `[semantic-judged]`. *Anti-Goodhart:* judge for/against scoped exactly to the undeclared shared confound the four axes cannot see; the structural score and the downgrade are reported side by side.

---

### Worked example (abbreviated)

`H03` (train-time PET→MRI distillation, `assumption_strength`) → `F03`, tier `measured_ablation`, comparator `{heuristic_quantity_id: Q41 (MRI-only AUC 0.812), ideal_quantity_id: Q42 (joint 0.843)}`, `reference_floor: Q40` (chance AUC 0.5). Evaluator: `raw = 0.031 AUC [0.018,0.044]`; `normalized_regret.method = baseline_relative`, `value = |0.843−0.812|/|0.843−0.5| = 0.090`; folds match ⇒ `confidence: high`; circularity distinct. No judge needed.

`F09` (NP-hard assignment) → tier `not_applicable`, reason source-anchored to RW04 Thm 2; distance null; confidence null; scored equal to a resolved frontier.

`T04` (claim C06, P01 Visium DGE vs P03 ROSMAP coloc): axes `{data_source: differ, method_class: differ, team: differ, assumption_set: same}` ⇒ independence 0.75; `directional_concordance` both upregulated ⇒ agreement 1.0; strength 0.75. Judge panel JP15 for/against surfaces "both anchor to the same APOE genotyping calls upstream" ⇒ verdict `weak_corroboration`, confidence medium — the structural 0.75 and the confound-driven downgrade are shown together.

---

### Tradeoffs (honest)

- **Non-self-sufficient by design.** Tiers 1-3 and axis independence collapse to prose-parsing without three sibling layers: a typed `quantities.yaml`, a resolvable `refs.yaml`, and controlled-vocab/OBI method + dataset xrefs. Without them the design offers nothing beyond an unaided judge — an honest degradation we declare, not hide.
- **Tier-laundering residual.** A technically-real but strawman-handicapped ablation passes the mechanical tier-1 checks; judging counterfactual *fairness* is itself Class C. The missing-candidate audit attacks it but does not close it.
- **Perspective granularity is fuzzy.** OBI anchoring bounds but does not eliminate hair-splitting perspective count up or lumping lenses down; the weakest-link min and same-data-forced-0 rules blunt the upward exploit.
- **Bootstrapping + governance cost.** Most existing ARAs start with near-empty ledgers until the calibration corpora and bounds/benchmark resolver exist; corpus governance and pretraining-contamination remain institutional problems the format can gate (canaries, calibration-accuracy) but not solve alone.
- **Write-surface doubling.** Prose + sidecar must agree — itself a new checkable anti-fabrication signal, but a real cost.

---

### Open questions

- Cross-domain aggregation: can distance ever roll into a funder-facing composite when the unit is field-specific (AUC vs log-runtime vs [0,1] judge scale)? We deliberately return `not_normalizable` rather than fake it; M39 may have to stay an un-aggregable per-heuristic disclosure.
- Is four independence axes enough, or does temporal independence (same team/method, different era) deserve a fifth in some fields?
- Corpus governance: single curator (capture risk) vs crowdsourced (drift/gaming); how aggressively must canaries refresh to stay ahead of contamination?
- Genre neutrality: a paper with zero applicable heuristics / zero multi-perspective claims should score `not_applicable` (neutral) — but distinguishing that from a silent gap needs the sibling `paper_type`/`expected_layers` manifest, so silence is read as neither honesty nor omission by default.

</details>
