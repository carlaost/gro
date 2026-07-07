# Tournament 2 — Metric Candidates Ledger

Harvested from the per-artifact **Indicators / Metrics & indicators** blocks Carla added to
`research/metrics/v3/tournament/DATA_SHAPES.md` (11 ARA-compiler artifacts). Each bullet (and its
scope sub-notes) is a proposed good-science metric. This ledger extracts, assesses, prunes, merges,
and ranks them into a candidate set for a per-metric tournament, then flags what is still missing.

Reference context:
- **Round-1 winners** = `TOURNAMENT_SUMMARY.md` (11 per-artifact winning metric sets — all judged
  "honest-but-limited proxies": single-file, offline, lexical/structural, **no external verification**).
- **ARA verifier** = `VERIFIER_COMPARISON.md` (Seal **L1** deterministic gates + **L2** six semantic
  dimensions D1–D6; L2 is artifact-only/no external fetch; L1 §10 is the *only* step that reaches the
  source PDF/repo).

Legend — **Follows?**: can it be computed/assessed from that artifact's documented shape honoring
penalize-don't-skip (yes / partial / no). **Better?**: is Carla's scoping tighter than the verifier's
overlap. **[sem]** = needs LLM semantic judgement; **[ext]** = needs an external tool
(semantic-scholar / undermind / clinical-trial registry / FOL solver / ontology resolver).

---

## A. Full extraction (flat, 64 candidates)

| M-id | Name | Artifact(s) | Intent (one line) |
|---|---|---|---|
| M01 | Metadata comprehensiveness | §1 PAPER.md | Basics present + a persistent id (DOI/accession) |
| M02 | Artifact comprehensiveness / article-type inference | §1 PAPER.md | Which layers exist, and what that implies about paper genre |
| M03 | Claim comprehensiveness (subfields/falsifiability/status) | §2 claims | All claim subfields filled, falsifiable, status set |
| M04 | Claims ↔ results matching (+ publication-bias) | §2 claims | Do claims match reported results; cross-check a connected clinical trial reporting different results |
| M05 | Abstract-only relevance discount | §2 claims | Down-weight relevance when source is abstract-only |
| M06 | References & anchor claims (dependencies) | §2 claims | Dependency chains resolve; anchor claims identified |
| M07 | Claim novelty | §2 claims | Are the claims new vs prior literature |
| M08 | Claim contradictions | §2 claims | Internal (claim↔claim) and external contradictions |
| M09 | FOL-ability (Oshima principles) | §2 claims | Can a first-order-logic graph be drawn cleanly over the claims |
| M10 | Controlled-vocabulary referenceability | §2 claims | Uses translatable, anchorable (ontology-mappable) terms |
| M11 | Context & content novelty (Evans) | §3 concepts | Novelty of concept space in Evans sense |
| M12 | Anchoredness (latent layer / canonical dataset) | §3 concepts | Is there a latent layer / canonical dataset referenced |
| M13 | Internal consistency: claims ↔ concepts | §3 concepts | Concepts cover/agree with the vocabulary claims use |
| M14 | Reference-landscape comprehensiveness | §4 problem | Cites full relevant landscape (island / k-NN ~500 / undermind) incl. contradicting claims |
| M15 | Gap ↔ claims match | §4 problem | Do stated gaps line up with what claims resolve |
| M16 | Gap truthfulness vs literature | §4 problem | Existing-attempts completeness + why-they-fail accuracy vs real lit |
| M17 | Insight novelty & relevance (+ impact) | §4 problem | Done before? societal/science impact if solved [sem] |
| M18 | Reference truthfulness / claim drift | §4 problem | Cited sources actually say what they're cited for |
| M19 | Experiment ↔ claim alignment | §5 experiments | Experiments actually test the claims they verify [sem] |
| M20 | Comprehensiveness of reporting (benchmark) | §5 experiments | Reporting completeness, briefly benchmarked |
| M21 | Experiments account for existing efforts & gap | §5 experiments | Design reflects prior efforts + gap analysis |
| M22 | Reference reasonability | §5 experiments | Are cited comparators/refs reasonable |
| M23 | Claim drift | §6 related_work | Same as M18 at the related-work layer |
| M24 | Gap size / novelty | §6 related_work | Magnitude/novelty of the delta over prior work |
| M25 | Replication bonus points | §6 related_work | Credit for replicating/confirming prior work |
| M26 | Dependency-graph comprehensiveness | §6 related_work | Citation dependency graph is complete |
| M27 | Method improvement | §6 related_work | Does the work improve on the cited method |
| M28 | Conditionality / generalizability | §7 constraints | How far do results generalize |
| M29 | Validity given claim ↔ experiment gaps/match | §7 constraints | Constraint validity in light of claim/experiment fit |
| M30 | Assumption realism, validity & fairness | §7 constraints | Dreamcase vs real-world assumptions |
| M31 | Limitation validity | §7 constraints | Do limitations add real new conditions on the hypotheses |
| M32 | Method validity | §7 method | Is the method sound |
| M33 | Method → constraint reasonability | §7 method | Do method choices justify the stated constraints |
| M34 | Method novelty | §7 method | Is the method new |
| M35 | Method verification status | §7 method | Widely-accepted method vs over-generalized/unjustified one |
| M36 | Combination of perspectives | §7 method | Multi-lens (e.g. wet-lab × computational) vs single, reflected in constraints |
| M37 | Heuristics reflect constraints | §7 heuristics | Are heuristics consistent with the constraints |
| M38 | Heuristics presence | §7 heuristics | There is always some abstraction — is it captured |
| M39 | Heuristics distance from optimum | §7 heuristics | How far the heuristic sits from the optimum |
| M40 | Started from a logical place | §8 tree | Did the DAG start where the literature left off |
| M41 | Abandoned paths reasoned & explained | §8 tree | Dead-ends are reasoned about, not bare |
| M42 | Abandoned-path pothole sufficiency | §8 tree | Enough context/constraints/heuristics/method/reasoning to let others avoid the pothole |
| M43 | DAG validly structured | §8 tree | Is the DAG structurally valid |
| M44 | Tree comprehensiveness (vs clinical-trial report) | §8 tree | Coverage, esp. when a clinical-trial report is available |
| M45 | Tree includes claim references | §8 tree | Tree evidence refs match the claim references |
| M46 | Misses search-bot-relevant references | §8 tree | Penalize omitting abandoned paths a search bot deems relevant/discoverable |
| M47 | Hypothesis failure-mode coverage | §8 tree | Substantial coverage of a hypothesis's failure modes |
| M48 | E2E reproducibility (fig+data+code) | §9 evidence | Evidence bundles figure + data + code for end-to-end reproduction |
| M49 | Evidence ↔ claim match | §9 evidence | Evidence substantiates the claims [sem] |
| M50 | Evidence ↔ constraints | §9 evidence | Evidence consistent with stated constraints |
| M51 | Evidence ↔ method | §9 evidence | Evidence consistent with the method |
| M52 | Reproduction value | §9 evidence | Confirms existing hypotheses (replication) vs new perspective |
| M53 | Re-use | §10 src | Are components re-used |
| M54 | FAIR | §10 src | Findable/Accessible/Interoperable/Reusable compliance |
| M55 | Reproducibility | §10 src | Reproducibility of the implementation layer |
| M56 | Added value / novelty / field expansion | §10 src | Does the code/artifact expand the field |
| M57 | Env ↔ evidence/method/constraints match | §10 src | Environment consistent with the other layers |
| M58 | Re-use | §11 data | Are datasets re-used |
| M59 | FAIR | §11 data | Dataset FAIR compliance |
| M60 | Reproducibility | §11 data | Reproducibility from the data layer |
| M61 | Added value / novelty / field expansion | §11 data | Does the dataset expand the field |
| M62 | Data ↔ evidence/method/constraints match | §11 data | Dataset consistent with the other layers |
| M63 | Data homogeneity & standard adherence | §11 data | Homogeneity + adherence to data standards |
| M64 | Referencing controlled vocabs / latent spaces | §11 data | Data references existing controlled vocabularies / latent spaces |

---

## B. Ranked survivor ledger

After pruning and merging (see merge note, §E). Survivors are shown as merged metrics citing their
constituent M-ids. Ranked by: (i) net-new vs verifier, (ii) tighter than verifier where overlapping,
(iii) down-weighted if a pure re-implementation of a round-1 winner or a verifier gate.

| Rank | Survivor (id) | Name | Artifact(s) | Constituents | Follows? | Round-1 overlap | Verifier overlap / better? | Needs | Rationale |
|---|---|---|---|---|---|---|---|---|---|
| 1 | S1 (M14) | Reference-landscape completeness | §4,§6,§8 | M14,M16,M21,M22,M26,M40,M46 | partial | none (offline) | none (L2 no external fetch) — **strictly net-new** | [ext] semantic-scholar/undermind | The single biggest gap the whole round-1 pool + verifier both lack: does the ARA cite the true relevant island / k-NN neighborhood, name contradicting work, and not miss what a search bot would surface. Highest signal. |
| 2 | S2 (M17) | Novelty vs literature | §2,§3,§4,§6,§7 | M07,M11,M17,M24,M34 | partial | none | none — net-new; verifier judges internal scope, never "done before" | [ext]+[sem] | Claim/insight/gap/method/concept novelty all reduce to a done-before? check against external lit — impossible for a single-file metric, absent from the verifier. Includes societal/science-impact judgement. |
| 3 | S3 (M18) | Claim drift / reference truthfulness | §4,§6 | M18,M23 | partial | none | L1 §10 checks quote-at-cited-line **inside the ARA**; Carla wants drift **against the real cited source** — tighter/deeper | [ext]+[sem] | Verifier's only external reach (L1 §10) confirms the ARA quoted itself faithfully, not that the citation supports the assertion. Carla's version is a true drift check. |
| 4 | S4 (M19) | Claim↔Experiment↔Evidence entailment (+ publication-bias) | §2,§3,§4,§5,§7,§9 | M04,M13,M15,M19,M29,M49 | partial | 05 Triangulation / 02 Grounding (lexical only) | **verifier D1** (type-aware entailment) — round-1 lacks it; Carla adds a clinical-trial-registry publication-bias cross-check the verifier also lacks → **better** | [sem]+[ext] (trial lookup) | The core "does the evidence actually entail the claim" axis. Verifier does D1 semantically but round-1 could not; the publication-bias sub-note (M04) is net-new beyond both. |
| 5 | S5 (M48) | End-to-end reproducibility bundle | §9,§10,§11 | M48,M55,M60 | partial | 09/10/11 touch pieces (single-file) | verifier D6 mentions reproducibility, not the fig+data+code **tri-layer bundle** — Carla's cross-layer framing is tighter | cross-layer | Whether figure + data + code co-exist for actual replication is a whole-ARA question neither the single-file round-1 metrics nor D6 fully pose. |
| 6 | S6 (M36) | Multi-perspective triangulation | §7 method | M36 | yes | none | none — net-new | [sem] | Whether the work combines lenses (wet-lab × computational) rather than one, and whether constraints reflect that. Genuinely absent from both. |
| 7 | S7 (M30) | Assumption realism & limitation validity | §7 constraints | M28,M30,M31 | partial | 07 Assumption→Consequence (concreteness only) | **verifier D3** assumption explicitness — Carla asks realism/fairness/dreamcase-vs-real + whether limitations add genuine new conditions → **materially tighter** | [sem] | Round-1 07 checks assumptions are *concrete*; verifier checks they're *explicit*. Neither judges whether they're *realistic/fair*. That judgement is the deeper science signal. |
| 8 | S8 (M32) | Method validity & verification status | §7 method | M32,M33,M35 | partial | none direct | **verifier D6** methodological rigor — Carla's "widely-accepted vs over-generalized/unjustified method" is a tighter, specific facet | [sem] | Distinguishes a validated standard method from one over-generalized beyond its warrant — a rigor axis D6 only gestures at. |
| 9 | S9 (M64) | Controlled-vocabulary & latent-space anchoring | §2,§3,§11 | M10,M12,M64 | partial | none | none — net-new | [ext] ontology resolver | Are terms/data anchored to real controlled vocabularies / canonical datasets / latent spaces (translatable, referenceable). Absent from both; enables cross-ARA interoperability. |
| 10 | S10 (M09) | FOL-ability (Oshima) | §2 claims | M09 | partial | none | none — net-new | [ext] FOL solver / [sem] | Can a clean first-order-logic graph be built over the claims. Novel formal-checkability signal, nothing comparable exists. |
| 11 | S11 (M08) | Claim contradictions | §2 claims | M08 | partial | none | verifier D4 catches cross-layer contradiction, not claim↔claim or claim↔external — Carla broader | [sem]+[ext] | Internal claim-set consistency + contradiction vs external findings. |
| 12 | S12 (M42) | Abandoned-path pothole sufficiency | §8 tree | M42 | yes | 08 Grounded Failure Disclosure (present/specific) | verifier D5 dead-end specificity — Carla's "enough context/constraints/heuristics/method/reasoning to let others avoid it" is a **richer** bar | [sem] | Pushes past "is the dead-end specific" to "is it reusable to prevent repeat failure" — tighter than both. |
| 13 | S13 (M47) | Hypothesis failure-mode coverage | §8 tree | M47 | partial | 08 partial | none direct | [sem] | Does the trace add substantial failure-mode coverage over a hypothesis — a completeness axis beyond disclosure. |
| 14 | S14 (M44) | Tree comprehensiveness vs clinical-trial report | §8 tree | M44 | partial | none | none — net-new | [ext] clinical-trial registry | Coverage benchmarked against an external registered/completed trial. External, net-new. |
| 15 | S15 (M53) | Reuse & FAIR-ness | §10,§11 | M53,M54,M58,M59 | partial | 10/11 provenance hygiene (partial) | none (FAIR not an explicit verifier axis) | [ext] registry | FAIR compliance + reuse; partially proxied by round-1 provenance metrics but FAIR-as-standard is net-new. |
| 16 | S16 (M56) | Added value / field expansion | §10,§11 | M56,M61 | partial | none | none — net-new but overlaps S2 novelty | [ext]+[sem] | Does the artifact/dataset expand the field. Overlaps S2; ranked lower to avoid double-counting novelty. |
| 17 | S17 (M25) | Replication vs novel-perspective value | §6,§9 | M25,M52 | partial | none | none — net-new | [sem]+[ext] | Credits confirming prior work (replication) distinctly from offering a new perspective. |
| 18 | S18 (M50) | Resource↔spec grounding | §9,§10,§11 | M50,M51,M57,M62 | partial | none | **verifier D4** cross-layer coherence (semantic) — Carla's is same territory, structural | [sem] | evidence/env/data consistent with constraints/method. Real, but heavily overlaps D4; kept for determinism. |
| 19 | S19 (M37) | Heuristics adequacy | §7 heuristics | M37,M38,M39 | partial | 07 Heuristics-Omission Audit (presence) | none for realism | [sem] | Presence + constraint-reflection + distance-from-optimum. Presence part is round-1; distance-from-optimum is net-new (see MISSING). |
| 20 | S20 (M20) | Reporting comprehensiveness / benchmark | §5 experiments | M20 | yes | 05 Comparator Rigor (overlaps) | verifier D6 statistical reporting — overlap | [sem] | Somewhat covered by both; modest add. |
| 21 | S21 (M02) | Artifact comprehensiveness / article-type | §1 PAPER.md | M02 | yes | 01 winner (Layer-Index density) overlaps | L1 existence gates overlap | — | Light; mostly proxied by round-1 01 + L1. Kept low. |
| 22 | S22 (M63) | Data homogeneity & standard adherence | §11 data | M63 | partial | none | none — net-new | [ext] standard registry | Adherence to data standards + homogeneity; under-specified but net-new. |
| 23 | S23 (M05) | Genre / abstract-only relevance discount | §2 (cross-cutting) | M05 | yes | round-1 thinness penalties (many) | L1 count-target genre handling | — | Cross-cutting modifier already largely handled by round-1 penalize-don't-skip + genre escape hatches. Lowest. |

### Pruned (not carried as survivors)
- **M01** Metadata comprehensiveness — pure dup of round-1 01 *Identifier & Bibliographic Integrity* + L1 frontmatter checks; no better scoping.
- **M03** Claim comprehensiveness (subfields/falsifiability/status) — pure dup of round-1 02 winner + verifier D2 + L1 field regex.
- **M06** References & anchor claims — dup of round-1 02 *Dependency Graph Integrity* + L1 §9 cross-link.
- **M43** DAG validly structured — dup of round-1 08 + L1 §8 YAML/type gates.
- **M45** Tree includes claim references — dup of L1 §9 cross-layer binding + round-1 08.
- **M27** Method improvement — subsumed into S2 (novelty) / S8 (method); no independent scope.

---

## TOP 10

The ten highest-priority survivors — these tournament first. Chosen for maximum signal beyond what
the round-1 winners and the ARA verifier already do (net-new, or overlapping-but-tighter):

1. **S1 (M14) — Reference-landscape completeness** [ext]. Neither round-1 nor verifier reaches the external literature at all; this is the clearest hole.
2. **S2 (M17) — Novelty vs literature** [ext][sem]. "Done before?" for claims/insight/gap/method — structurally impossible for offline single-file metrics and out of scope for L2.
3. **S3 (M18) — Claim drift / reference truthfulness** [ext][sem]. Turns L1 §10's self-quote check into a real does-the-source-support-it check.
4. **S4 (M19) — Claim↔Experiment↔Evidence entailment (+ publication-bias)** [sem][ext]. Verifier D1 semantically, round-1 could not; the trial-registry publication-bias cross-check beats both.
5. **S5 (M48) — End-to-end reproducibility bundle** (fig+data+code, cross-layer).
6. **S6 (M36) — Multi-perspective triangulation** [sem]. Wholly absent from both.
7. **S7 (M30) — Assumption realism & limitation validity** [sem]. Tighter than round-1 07 concreteness and verifier D3 explicitness.
8. **S8 (M32) — Method validity & verification status** [sem]. Tighter facet of verifier D6.
9. **S9 (M64) — Controlled-vocabulary & latent-space anchoring** [ext]. Net-new interoperability signal.
10. **S10 (M09) — FOL-ability (Oshima)** [ext]/[sem]. Net-new formal-checkability signal.

---

## MISSING (net-new)

Good-science signals these artifacts imply that **neither** the round-1 winners **nor** the verifier
capture, and which Carla's list gestures at but under-specifies — worth adding as first-class
tournament metrics:

- **Publication-bias detection via registry cross-reference** (M04 sub-note): match a claim to a
  registered/completed clinical trial and flag divergent reported outcomes. Needs a clinical-trial
  registry lookup; currently one buried sub-bullet.
- **External novelty/"done-before" resolution** against the literature island / k-NN neighborhood
  (undermind / semantic-scholar). The dependency the entire round-1 pool was explicitly built without.
- **FOL-graph constructability (Oshima)** as a formal, tool-checkable rigor signal — no tooling or
  operationalization exists yet.
- **Controlled-vocabulary / ontology anchoring & latent-space referenceability** — cross-artifact,
  needs an ontology/latent-space resolver; enables cross-ARA interoperability nothing else scores.
- **Multi-perspective (wet-lab × computational) triangulation strength** — completely uncovered.
- **Heuristic "distance from the optimum" (M39)** — a genuinely novel, hard signal (how far is the
  chosen shortcut from the ideal); Carla names it but leaves it fully under-specified.
- **Data homogeneity & standards adherence (M63)** — adherence to field data standards, distinct from
  provenance hygiene.
- **"Started where the literature left off" positioning (M40)** — external-lit-anchored trajectory
  check on the exploration tree.

---

## E. Merge decisions (one paragraph)

Three cross-artifact families were unified per the brief. The **re-use / FAIR / reproducibility /
added-value** cluster appears near-verbatim in §10 (src) and §11 (data) and echoes in §9 (evidence);
I split it by *what it actually measures* rather than by artifact — a **reuse+FAIR** metric (S15), an
**end-to-end reproducibility bundle** spanning evidence+src+data (S5), an **added-value/field-expansion**
metric (S16, folded toward the novelty family to avoid double-counting), and a **replication-vs-new-
perspective** metric (S17, merging §6's replication bonus with §9's reproduction value). The **X ↔ Y
consistency** family was consolidated into two survivors: a semantic **claim↔experiment↔evidence
entailment** metric (S4, absorbing claim↔results, gap↔claims, claim↔concepts, and the §7 claim↔experiment
validity note) and a structural **resource↔spec grounding** metric (S18, merging evidence/env/data ↔
constraints/method). **Claim drift** (§4 reference-truthfulness and §6 claim-drift) merged into one
external-verification metric (S3). Beyond the mandated three, I clustered the scattered **novelty**
bullets (claim/concept/insight/gap/method) into S2 and the scattered **literature-landscape** bullets
(full-landscape citation, existing-attempts truthfulness, missing-refs, reasonable-refs, dependency-
graph completeness) into S1, since all reduce to the same external-literature capability the round-1
tournament deliberately lacked. Six candidates were pruned outright as pure re-implementations of a
round-1 winner or an L1 gate (M01, M03, M06, M27, M43, M45).
