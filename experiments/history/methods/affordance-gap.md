# What the Metrics Want vs. What ARA Emits — An Affordance-Gap Critique

**Question this doc answers:** if we take every metric we have drafted — not the honest-but-limited
versions the round-1 tournament actually built, but their *ideal* forms, i.e. what each `Indicators`
block in `DATA_SHAPES.md` and each `M##`/`S##` candidate in `ALL_METRICS_MERGED.md` is *reaching for*
even where it isn't yet feasible — then **what data format would let us compute them**, and **where
does the ARA compiler's current output shape fall short of affording it?**

The framing is deliberately about *affordance*, not correctness. A metric is not merely "hard" or
"easy"; it makes an implicit *demand on the shape of the data*. "Do the claims match the concepts"
demands that claims and concepts share resolvable identifiers. "Is this novel vs. the literature"
demands that every cited work resolve to an external entity you can embed. "Does the claim's number
match the source" demands that the number exist as one canonical typed value, not three hand-typed
prose copies. **Most of our ideal metrics are blocked not because the information is missing from the
ARA, but because it is stored in a shape only an LLM can re-extract — which defeats the determinism
the whole tournament was built to prize.** That is the thesis of this document.

**Inputs read for this critique:** `DATA_SHAPES.md` (the 11 emitted artifact shapes + Carla's
per-artifact `Indicators` drafts), `ALL_METRICS_MERGED.md` (round-1 winners, verifier L1/L2, the
64-candidate `M##` ledger and its `S##` survivors), `NOVELTY_INDICATORS_COMPARISON.md` (the external
LENS axis), and the compiler skill's `ara-schema.md` (the authoritative output field spec).

---

## 1. The core mismatch, stated once

The ARA format is a **progressive-disclosure prose format**. Its design center is: a human or agent
reads `PAPER.md` (~200 tokens), drills into a Level-2 markdown layer, then into a Level-3 detail file,
each written to be *read*. Structure exists (YAML frontmatter, `exploration_tree.yaml`, `C##`/`E##`
IDs, the `value ← ref «quote» [tag]` Sources line) but it is **structure-in-prose**: identifiers
embedded in markdown bullets, references written as author-year strings, numbers re-typed verbatim in
three or four places, entities named in free text.

Our metrics — especially the ideal round-2 ones — want the opposite. They want to run **computation
over a typed, resolvable, externally-anchored knowledge graph**: set operations over IDs, joins over
typed quantities, lookups against live registries, embeddings of a resolved citation neighborhood.
There is a genuine impedance mismatch between "optimized to be read" and "optimized to be computed
over," and almost every gap below is a specific instance of it.

This yields a clean three-way classification of *why* a given ideal metric is blocked, which the rest
of the doc uses:

| Class | The blocker | Can a format change fix it? | Example ideal metrics |
|---|---|---|---|
| **A — Format-recoverable determinism** | ARA *has* the information but stores it as prose, so the metric must LLM-re-extract it (non-deterministic, lossy) instead of reading a typed field. | **Yes.** Emit the same fact as typed data → the metric becomes a deterministic join/set-op. | claims↔concepts consistency (M13), cross-layer numeric reconciliation, dependency-graph structure (M26), provenance parsing, artifact/genre inference (M02) |
| **B — Anchor-dependent** | The metric needs an external resolver (registry, literature index, ontology). The format's job is only to emit *resolvable anchors* so the resolver can run. | **Partially.** Format can't do the lookup, but it can *guarantee every entity carries a resolvable ID*. Today anchors are patchy. | reference-landscape completeness (M14/S1), publication-bias (M04), access-tier verification, tree-vs-registry (M44), controlled-vocab anchoring (M10/M64) |
| **C — Irreducibly semantic / calibration** | The metric is a value judgement (novelty, significance, realism, entailment quality) that needs an LLM judge and/or a human-calibrated ground-truth set. No format change makes it deterministic. | **No.** Format can only *feed the judge cleaner, pre-structured inputs* so it is cheaper and more consistent — never substitute for the calibration layer. | novelty vs. literature (S2), assumption realism (S7), claim↔experiment entailment quality (S4), significance/LENS |

The practical upshot: **a large fraction of our "we can't build this" list is actually Class A** — a
format problem masquerading as a feasibility problem. Those are the cheapest, highest-leverage fixes,
because they *restore determinism we are currently throwing away by emitting prose.* Class B fixes are
about discipline (never emit an unresolvable reference). Class C is the honest hard ceiling — and even
there the format can meaningfully lower the LLM-judge's cost and variance.

---

## 2. The ARA's canonical failure mode: information present, shape wrong (Class A)

Six recurring shape defects block whole *families* of metrics at once. These are the ones worth fixing
first because the compiler already knows the answer — it just writes it down un-computably.

### 2.1 Numbers live as prose in three-plus places, never as one canonical typed value

A single load-bearing result — say `p217_MS P-score 0.859` — is transcribed **four times** in a
well-compiled ARA:

1. in `claims.md` `**Statement**` prose (`"...highest rank (P-score = 0.859)..."`),
2. in that claim's `**Sources**` line (`` `0.859` ← evidence/tables/table2.md ... «p217_MS (0.859)» [result] ``),
3. in `evidence/tables/table2.md`'s markdown cell (`p217_MS (0.859)`),
4. in `trace/exploration_tree.yaml`'s `result:` prose (`"p217_MS ranked first (P-score 0.859)..."`).

Every "does X match Y" numeric metric — round-1 `02` Grounding Fidelity, `09` Numeric Reconciliation,
the priority build "claims' quotes checked against `evidence/`'s filed tables" (Merged §D.5.4), and the
ideal M49 evidence↔claim / M50 evidence↔constraints / M51 evidence↔method — is reduced to **fuzzy
string-matching four hand-typed copies of the same number**. Rounding, unit drift (`0.10` vs
`0.10 (95% CI 0.04–0.16)`), or a transcription slip breaks the match, and the metric cannot tell a real
inconsistency from a formatting one.

- **Ideal affordance:** one **typed quantity ledger** — `quantities.yaml` — where each load-bearing
  value is a record `{id, value, unit, ci, comparator, direction, type: input|result, source_anchor}`.
  Claims, evidence tables, and tree nodes *reference the quantity by id* instead of re-typing it.
  Numeric reconciliation becomes a deterministic join; publication-bias (compare `value` to a
  registry's reported value) becomes a field comparison; effect-size / magnitude metrics become
  arithmetic. This single change converts a cluster of Class-A "lexical proxy" metrics into exact ones.
- **Where ARA falls short:** the schema has no canonical quantity object. The `Sources` line is the
  closest thing, but it is a per-claim prose DSL (§2.4 below), not a shared referenceable ledger, and
  it deliberately re-quotes the number rather than pointing at a single source of truth.

### 2.2 Claims carry no *type*, so type-aware entailment is uncomputable at the source

Verifier D1 and ideal S4 (Claim↔Experiment↔Evidence entailment) are explicitly **type-aware**: a
*causal* claim demands an ablation, a *generalization* claim demands heterogeneous data, an
*improvement* claim demands a baseline, a *descriptive* claim demands a sampling frame. But the ARA
claim schema records only `Status ∈ {hypothesis, supported, refuted}` — **there is no `claim_type`
field.** A metric that wants to check "does the cited experiment design match what this claim *type*
requires" must first *infer the type from prose*, i.e. do the hard semantic step before it can even
begin the check.

- **Ideal affordance:** a `claim_type` enum on every claim (`causal | generalization | improvement |
  descriptive | scoping | existence | ...`). This is cheap to emit, it is exactly the pivot D1 turns
  on, and it converts "infer type then check" into "read type then check" — collapsing a Class-C step
  into a Class-A one for the *type-selection* half of the metric (the entailment judgement itself stays
  Class C, but it now runs the *right* rubric deterministically).
- **Where ARA falls short:** absent entirely. `Tags` are free-text keywords, not a type.

### 2.3 Entities (concepts, methods, variables) have no stable or external identifiers

`concepts.md` keys concepts by a prose `## Term Name` heading; `Related concepts` is a loose comma
list of *other prose names*; claims tie to concepts only through free-text `Tags`. Nothing maps a
concept to a controlled vocabulary (MeSH, EFO, GO, arXiv taxonomy, Wikidata QID) or to an embedding
anchor.

This blocks an entire cluster: M13 (claims↔concepts internal consistency — currently fuzzy string
overlap between `Tags` and headings), M10 (controlled-vocabulary referenceability), M12/M64
(anchoredness / latent-space referenceability), and it *undermines* M09 (FOL-ability), because you
cannot build a clean first-order graph over predicates and entities that have no stable symbols.

- **Ideal affordance:** each concept carries an optional `xref` to an ontology/vocabulary ID and/or a
  canonical embedding; claims reference concepts *by ID*. Then claims↔concepts consistency is a set
  operation, controlled-vocab coverage is a resolvable-fraction, and cross-ARA interoperability (the
  same concept recognized across papers) becomes possible — the thing M64 is really after.
- **Where ARA falls short:** no ontology hooks anywhere in the schema. `Notation` captures LaTeX
  symbols, not entity identity. This is a **Class B** gap (needs an external entity-linker to *fill*
  the xref) with a **Class A** consequence (once filled, the downstream consistency checks are exact).

### 2.4 Provenance is a hand-formatted prose micro-DSL, not a data schema

The grounding line —
`` `<value>` ← <ref> (<locator>) «<verbatim quote>» [input|result] `` — encodes exactly the fields a
grounding metric wants as columns (value, source ref, locator, verbatim span, input-vs-result tag).
But it is emitted as free-form markdown bullets, so every metric that consumes it (round-1 `02`, the
whole §10 quote-at-cited-line check, S3 claim-drift) must **re-parse a hand-typed string** whose exact
punctuation the compiler/LLM will inevitably vary.

- **Ideal affordance:** structured provenance records (`{value_id, source_file, locator, quote,
  tag}`), one per grounded value, either as YAML sidecars or as the `source_anchor` on the quantity
  ledger (§2.1). Grounding fidelity, numeric reconciliation, and the external quote-at-source check all
  become robust joins rather than regexes over prose.
- **Where ARA falls short:** the DSL is prose by design (it reads well inline under a claim), and its
  robustness depends on the model formatting it identically every time — a brittle contract for a
  deterministic metric.

### 2.5 Cross-layer references resolve *within* the ARA but carry no semantic edge type

The ID system (`C##`, `E##`, `RW##`, `N##`, `O##`, `G##`) supports **existence** checks (L1 §9:
`Proof→E##` resolves, `Verifies→C##` resolves) but not **alignment** checks. Every ideal "X ↔ Y match"
metric — M19 experiment↔claim, M15 gap↔claims, M50/M51 evidence↔constraints/method, M57/M62
env/data↔everything — needs an edge that says *how* X relates to Y and *whether that relation holds*,
which the current binding does not carry. The link `C01.Proof = [E01]` tells you E01 exists; it does
not tell you E01's design actually tests C01.

- **Ideal affordance:** this is where the format hits its honest limit. The *existence* half is Class A
  (already afforded). The *holds?* half is Class C (semantic). But the format can still narrow the
  judge's job: typed claims (§2.2) + a typed quantity ledger (§2.1) + explicit `measures`/`compares`
  fields on experiments would let the entailment judge check a *structured* correspondence
  (claim.type ⇒ required design present? claim.quantity ∈ experiment.measured_quantities?) rather than
  reading four prose blobs.
- **Where ARA falls short:** experiments record `Metrics` and `Expected outcome` as prose with
  directional language, never as structured "this experiment measures quantity Q against baseline B" —
  so even the checkable skeleton of entailment is unavailable without NLP.

### 2.6 Genre-conditionality is expressed as *absence*, which is ambiguous

The governing "only if warranted" rule (a meta-analysis correctly has no `src/execution/`; forcing one
is fabrication) is epistemically right but **computationally ambiguous**: a missing `heuristics.md`
means one of (a) the paper genuinely states no heuristics, (b) the compiler was lazy, (c) the genre
doesn't warrant it — and *the format records nothing that distinguishes these.* Yet nearly every
`Availability notes` block in `DATA_SHAPES.md` instructs metrics to "penalize thinness but not honest
absence" — a distinction the format gives the metric no signal to make except by cross-checking other
layers with an LLM. M02 (artifact comprehensiveness / article-type inference) and S21 want to *derive*
genre from which layers exist; but genre is exactly what you need to *know first* to judge whether an
absence is honest.

- **Ideal affordance:** a **paper-type / genre manifest** — `paper_type: meta_analysis | rct |
  observational | theory | ml_empirical | wet_lab | tool_release | ...` plus an explicit
  `expected_layers` (or per-artifact `warranted: true/false/n_a` declaration). Then absence becomes
  *checkable against a declared expectation* — an omitted-but-expected layer is a coverage failure, an
  omitted-and-declared-n/a layer is honest, and no LLM guess is needed to tell them apart.
- **Where ARA falls short:** `domain` is free text, not an enum a metric can branch on, and there is no
  per-layer warranted-ness declaration. Absence is silent.

---

## 3. Anchor-dependent gaps: what ARA must emit to let an external resolver run (Class B)

These metrics can never be deterministic from the ARA alone — they need a registry, a literature
index, or an ontology. But the format still controls whether the resolver *can* be pointed at anything.
The discipline is: **every external entity the ARA names must resolve to a stable identifier stored in
a machine-readable place.** ARA does this well for some entity kinds and badly for others.

### 3.1 References are strings in most layers, IDs in one

This is the single widest Class-B hole, and it gates the most valuable ideal metrics: S1
reference-landscape completeness, S2 novelty vs. literature ("done before?"), S3 claim-drift /
reference-truthfulness, M16 gap truthfulness vs. literature, M26 dependency-graph comprehensiveness,
M40 "started where the literature left off," and LENS-style novelty/SOTA reconstruction.

- **What ARA gets right:** `related_work.md` full `RW##` blocks carry a `DOI` field. Datasets and
  registrations carry real resolvable IDs (GEO `GSE307990`, PROSPERO `CRD420261327845`, dbGaP) — these
  are genuinely better than citation strings.
- **Where it falls short — three distinct failures:**
  1. **Coverage:** citations *outside* the full `RW##` blocks — `problem.md`'s `Evidence` fields, the
     "brief tier" of `related_work.md`, inline mentions — are **author-year prose strings with no
     DOI**. The paper's full citation footprint is exactly what a landscape/novelty metric must
     resolve, and most of it is un-IDed.
  2. **No normalization:** there is no single citation table that every layer points into by ID. The
     same work cited in `problem.md` (as "Janelidze et al., 2023") and `related_work.md` (as `RW01`
     with a DOI) is not linked — a metric must entity-resolve prose to reconnect them.
  3. **Unverified even where present:** the round-1 `06` judge flagged that DOIs are format-checked, not
     resolved — "well-formed but fabricated passes." A resolvable-*looking* ID that no registry
     confirms is worse than none, because it passes the cheap check.
- **Ideal affordance:** a normalized `refs.yaml` — every cited work once, with a resolvable ID
  (DOI / arXiv / OpenAlex / S2 corpus ID), and every inline citation in *every* layer referencing it by
  that ID. Then: fetch → embed → k-NN neighborhood → landscape coverage, claim-drift (does the resolved
  source actually support the claim it's cited for), and novelty positioning all become *possible*
  (still `[ext]`/`[sem]`, but no longer blocked at the parsing step).

### 3.2 Registrations and accessions are resolvable — but buried in prose and unlinked to claims

Publication-bias detection (M04, the single most-cited "MISSING" signal) needs: match a claim to its
registered/completed-trial primary outcome, flag divergence. ARA stores the registration *string*
(good) but (a) inside `environment.md`/`data/dataset.md` prose, so a metric must NLP-extract it, and
(b) **nothing links a specific claim to a specific registered endpoint** — there is no field "this
claim corresponds to registered outcome X." So even with a live registry, the format gives you no join
key between the claim and the registry record.

- **Ideal affordance:** promote accessions/registrations to a machine-readable manifest (they already
  exist as strings — this is nearly free), and add an optional `registered_as` link on claims that
  correspond to a preregistered outcome. Then genre-scope fidelity (`11`, our most Goodhart-resistant
  metric) upgrades from "accession *looks* real" to "accession *is* real," and publication-bias becomes
  a claim↔registry field comparison.
- **Where ARA falls short:** access-tier honesty is a scoring axis `DATA_SHAPES` explicitly praises,
  but it lives as a prose sentence ("processed data are **open**; raw reads are **controlled access via
  dbGaP**"); a metric checking access-tier must parse that sentence rather than read `access:
  {processed: open, raw: controlled_dbgap}`.

### 3.3 Novelty has raw material but no external anchor and no contribution-typing

LENS-style novelty (Class C at its core, but Class B in its *inputs*) needs SOTA reconstruction (the
resolved, embedded citation neighborhood — see §3.1), plus contribution *typing* (new method vs.
unexpected finding vs. resolved open problem) and delta *magnitude*. ARA's `problem.md`
(`Key Insight / Derived from / Enables`) and `related_work.md` typed edges (`extends / bounds /
refutes`) are genuinely good raw material for an *internal* novelty narrative — but there is no field
for contribution type, none for delta magnitude, and the edges resolve to internal IDs, not external
embeddings.

- **Ideal affordance:** a `contribution_type` + `delta_magnitude` field on the key-insight / RW edges,
  and (per §3.1) resolvable external anchors so "done before?" can be asked against a real neighborhood.
  These don't *make* novelty deterministic — they pre-structure the inputs so a LENS-style judge runs
  cheaper and more consistently, which is the most the format can do for a Class-C metric.

---

## 4. The irreducible ceiling: what no format change can afford (Class C)

Honesty requires naming what the format *cannot* fix, so we don't over-promise the affordance-complete
rewrite in §6.

- **Novelty & significance as a calibrated score** (LENS's whole axis). Even a perfectly typed,
  fully-anchored ARA cannot tell you whether a contribution is *important* without an LLM judge and a
  human-labeled calibration set. `NOVELTY_INDICATORS_COMPARISON.md` §2 is right: the calibration
  asymmetry is the deepest gap, and it is not a data-shape gap. The format can feed the judge; it
  cannot be the judge.
- **Entailment / alignment *quality*** (does E01 *really* test C01; does the evidence *substantively*
  support the claim — D1, S4). The format can supply the structured skeleton (§2.5) and the right
  rubric selector (§2.2), but the final "holds?" is semantic.
- **Assumption realism, method validity, limitation validity** (S7, S8 — M30/M31/M32/M35). "Is this a
  dreamcase or a real-world assumption" is a domain value-judgement. Typed fields can make the
  *assumption → consequence* structure explicit (round-1 `07`'s deepest metric already leans on this),
  but realism itself is Class C.
- **Heuristic distance-from-optimum** (M39). Named in the MISSING list, genuinely novel, and not a
  format problem — there is no "optimum" stored anywhere to measure distance against.
- **Multi-perspective triangulation strength** (S6/M36 — wet-lab × computational). The format can *tag*
  perspectives; whether they genuinely corroborate is semantic.

For all of these, the correct architecture is the hybrid the other docs already point at: **the format
change lowers Class-C cost and variance by handing the LLM judge clean, typed, pre-linked inputs
instead of raw prose** — but the judge and its calibration set remain load-bearing. The format's job is
to shrink the surface the judge must reason over, not to eliminate it.

---

## 5. Per-metric-family affordance verdict

Consolidated map from *ideal metric family* → *the data affordance it demands* → *what ARA emits* →
*class and verdict*. Read "Afforded?" as: can the metric run *deterministically and reliably* on the
current output shape?

| Ideal metric family (M##/S##/D#) | Affordance it demands | ARA's current shape | Class | Afforded? |
|---|---|---|---|---|
| Numeric reconciliation, evidence↔claim number match (`09`, `02`, M49–M51) | One canonical typed quantity, referenced everywhere | Number re-typed as prose in claim + Sources + table + tree | **A** | ✗ — string-matches 4 copies |
| Type-aware claim↔experiment↔evidence entailment (D1, S4, M19) | `claim_type` field + structured experiment `measures`/`baseline` | `Status` only; experiment metrics as prose | **A→C** | ✗ — type must be inferred; entailment stays semantic |
| Claims↔concepts internal consistency (M13) | Claims reference concepts by ID | Free-text `Tags` vs. prose headings | **A** | ~ — fuzzy overlap only |
| Controlled-vocab / ontology / latent-space anchoring (M10, M12, M64) | Concept `xref` to ontology ID / embedding | Prose `## Term`, LaTeX `Notation` | **B** | ✗ — no anchors to resolve |
| FOL-ability, Oshima (M09, S10) | Stable predicate/entity symbols | Prose entities, no symbol table | **A/B** | ✗ — nothing clean to build a graph over |
| Dependency-graph comprehensiveness (M26) | Normalized citation graph with external IDs | `RW##` DOIs only; rest author-year prose | **B** | ~ — partial, un-normalized |
| Reference-landscape completeness, novelty positioning (S1, S2, M14, M16, M40) | Every citation → resolvable external ID → embeddable neighborhood | DOIs in full RW blocks only; footprint mostly un-IDed | **B/C** | ✗ — most of the footprint can't be resolved |
| Claim-drift / reference truthfulness (S3, M18/M23) | Resolvable source + fetchable text to check support | Author-year strings; DOIs unverified | **B/C** | ✗ — blocked at resolution |
| Publication-bias via registry (M04) | Accession/registration as data + claim→registered-outcome link | Registration string in prose; no claim link | **B** | ✗ — no join key to registry |
| Access-tier verification, genre-scope fidelity (`11`) | Structured access tiers + live-registry lookup | Prose access sentence; format-only ID check | **B** | ~ — honest-*looking*, not verified |
| Genre / article-type inference; honest-absence vs. lazy-omission (M02, S21, S23) | `paper_type` enum + per-layer `warranted` declaration | Free-text `domain`; silent absence | **A** | ✗ — absence is ambiguous |
| Grounding fidelity (value ∈ quote) (`02`, L1 §10) | Structured provenance records | Prose `value ← ref «quote» [tag]` DSL | **A** | ~ — works but brittle re-parse |
| Falsifiability quality, scope calibration (D2, D3, `01`/`02`/`05`) | Falsification criteria + claim scope as evaluable text | Present as prose fields (genuinely well-shaped) | **C** | ~ — well-fed, judge still needed |
| Exploration integrity, dead-end disclosure (D5, `08`, M41/M42/M47) | Typed nodes with failure_mode/lesson | `exploration_tree.yaml` — **the best-shaped artifact** | **A/C** | ✓ structure / ~ quality |
| Tree comprehensiveness vs. clinical-trial report; misses discoverable refs (M44, M46) | Tree nodes carrying *external* work IDs | `source_refs` point into the paper only | **B** | ✗ — no outward anchors |
| Novelty/significance calibrated score (LENS) | LLM judge + human calibration set | — (no surface at all) | **C** | ✗ — irreducible |
| E2E reproducibility bundle fig+data+code (S5, M48) | Cross-layer presence + linkage of evidence/data/code | Layers exist but link by prose/genre convention | **A** | ~ — checkable if layers were declared-linked |
| Reuse & FAIR-ness (S15, M53–M55) | Resolvable artifact/dataset IDs + license as data | Prose in `environment.md`/`artifacts.md` | **A/B** | ~ — parseable, not structured |

Pattern: the ✗-Class-A rows are the **cheap wins** (restore determinism the format is discarding); the
✗-Class-B rows are **discipline + one resolver** (never emit an unresolvable reference); the ✗/~-Class-C
rows are the **honest ceiling** (feed the judge better, keep the judge).

---

## 6. What an affordance-complete ARA would add (without breaking what works)

The prescription is *not* "make ARA a database." Its prose layers are its strength for the human/agent
reader and for the Class-C judges, which read prose well. The prescription is **emit a thin typed
sidecar alongside the prose** — the same facts the compiler already produces, in a shape a metric can
join on — so that Class-A determinism is recovered and Class-B/C inputs are pre-linked. Seven additions,
each mapped to the families it unblocks:

1. **`quantities.yaml` — a typed quantity ledger.** Each load-bearing number once, as `{id, value,
   unit, ci, comparator, direction, type, source_anchor}`; claims / evidence / tree reference by ID
   instead of re-typing. *Unblocks:* numeric reconciliation, evidence↔claim/method/constraint number
   matching, effect-size, publication-bias comparison. (§2.1)
2. **`claim_type` on every claim** (`causal | generalization | improvement | descriptive | scoping |
   …`). *Unblocks:* type-aware entailment rubric selection (D1/S4) — makes the judge run the *right*
   check deterministically. (§2.2)
3. **Concept `xref` + claim→concept-by-ID.** Optional ontology/vocabulary/embedding anchor per concept;
   claims cite concepts by ID. *Unblocks:* claims↔concepts consistency (exact), controlled-vocab
   anchoring, cross-ARA interoperability, cleaner FOL symbols. (§2.3)
4. **`refs.yaml` — one normalized citation table**, every cited work with a resolvable external ID
   (DOI/arXiv/OpenAlex/S2), every inline citation in every layer pointing by ID. *Unblocks:* the entire
   reference-landscape / novelty / claim-drift / dependency-graph cluster — the widest and highest-value
   hole. (§3.1)
5. **Structured provenance records** replacing (or shadowing) the prose `Sources` DSL, folded into the
   quantity ledger's `source_anchor`. *Unblocks:* robust grounding fidelity + quote-at-source checks
   without brittle re-parsing. (§2.4)
6. **A `paper_type` / genre manifest with per-layer `warranted` declarations.** *Unblocks:* honest-
   absence-vs-lazy-omission disambiguation, article-type inference, genre-aware scoring floors —
   removes the LLM guess the "penalize thinness not absence" rule currently requires. (§2.6)
7. **External-anchor manifest + optional claim→registered-outcome / claim→contribution-type links.**
   Promote accessions/registrations to machine-readable, link claims to registered endpoints, tag
   contribution type + delta magnitude. *Unblocks:* verified genre-scope fidelity, publication-bias,
   and pre-structured novelty inputs. (§3.2, §3.3)

**Two design tensions to hold while doing this**, both real and both flagged by the source docs:

- **Typed fields invite fabrication.** Prose makes `"Not specified in paper"` and honest absence
  natural; a typed slot pressures the compiler (or the model) to fill it, and a filled-but-invented
  field passes a structural check the way a fabricated-but-well-formed DOI already does. Every added
  field must carry a first-class `not_specified` / `null` value scored *equal to* an honest absence
  (the "honest-absence symmetry" round-1 already engineered), or the sidecar just relocates the
  Goodhart surface.
- **Readability vs. computability is a genuine trade, not a free lunch.** The sidecar approach keeps the
  prose for the reader and adds structure for the metric — but it doubles the compiler's write surface
  and creates a *new* consistency obligation (prose and sidecar must agree, itself now a checkable
  metric). That is acceptable, even useful (agreement-between-views is a strong anti-fabrication
  signal), but it should be a deliberate choice, not a silent one.

---

## 7. One-paragraph synthesis

Most of what our ideal metrics want is **already inside the ARA** — the compiler extracts claim types
implicitly, grounds numbers, names every citation, states access tiers, records genre. The reason we
keep concluding "honest-but-limited proxy, needs an external step" is only *partly* the true external
ceiling (novelty, calibration, semantic entailment — Class C, irreducible). A large share is **Class A:
the format writes computable facts as prose, forcing every metric to LLM-re-extract them and thereby
surrendering the determinism the tournament exists to provide.** The highest-leverage move is not more
metrics or more LLM judges — it is a thin typed sidecar (a quantity ledger, a normalized reference
table, claim-typing, concept xrefs, a genre manifest) that hands each metric a join key instead of a
paragraph. That recovers exact scoring for a whole family of "matching/consistency/reconciliation"
metrics for near-free, converts the reference/novelty cluster from *impossible* to merely *`[ext]`*,
and — for the genuinely semantic metrics that will always need a judge — shrinks the prose surface the
judge must reason over, lowering its cost and its variance. ARA doesn't lack the knowledge; it lacks
the *shape*.

---

## Sources
- `research/metrics/v3/tournament/DATA_SHAPES.md` — the 11 emitted artifact shapes + per-artifact `Indicators` drafts (the "ideal metric" seeds).
- `research/metrics/v3/tournament/ALL_METRICS_MERGED.md` — round-1 winners, verifier L1/L2, the M01–M64 candidate ledger, S1–S23 survivors, top-10, and MISSING list.
- `research/metrics/v3/tournament/NOVELTY_INDICATORS_COMPARISON.md` — the external LENS / novelty axis and the calibration-asymmetry argument.
- `~/.claude/skills/compiler/references/ara-schema.md` — the authoritative compiler output field spec.
