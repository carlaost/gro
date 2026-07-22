# GRO material layers

The GRO layer lives in `<ARA>/gro/` and is compiled ON TOP of the ARA logic layer. It is
**pure material compilation**: a structured record of what is actually present in the
research. It contains **no metrics and no judgments** — no novelty typing, no comparison to
prior work, no significance/breakthrough scoring. Those are a separate, not-yet-converged
concern and are never written here.

All files are YAML. `pending_extraction` marks a structural slot whose value has not yet been
compiled from the material — a "not yet read" marker, never a judgment being deferred.

Reading the source to fill these fields is itself compilation: transcribe what the material
says. Classifying a claim's *form* (e.g. it is a prediction) or listing the *sections present*
is material structuring, not an evaluation of merit.

---

### `temporal.yaml` — dates present in the material (deterministic)
```yaml
pub_date: YYYY-MM-DD          # from PAPER.md year
doi: "…" | pending_extraction
fetch_timestamp: <compile time, UTC>
note: "dates present in the material"
```
No `precedence_date` / `cutoff_date` — those frame novelty windows for a metric, out of scope.

### `refs.yaml` — the reference spine (references present)
```yaml
refs:
  - id: R01
    raw: "the reference string as cited"
    external_id: <DOI/arXiv/dataset id> | not_specified   # only if the id is actually present
    resolvable: true | false                              # whether external_id resolves — a material fact
```

### `quantities.yaml` — load-bearing numbers, verbatim-grounded
```yaml
quantities:
  - id: Q01
    value: 40
    unit: "claim-evidence edges"
    comparator: exact | approx | ge | le | gt | lt | range   # the comparator present in the text
    role: input | result                                     # a value set vs. a value a run produced
    source_ref: "logic/claims.md#C02"
    quote: "verbatim line copied from the source containing the number"   # REQUIRED (grounding)
    claim_refs: [C02]
```
Every number is transcribed from an open source, never written from memory. A row with a
value but no `quote` is invalid (ungrounded).

### `entities.yaml` — the entity spine
```yaml
entities:
  - id: EN-<kind>-<slug>          # e.g. EN-method-differential-expression
    term: "canonical term as written"
    kind: method | concept | measure | dataset | tool | organism | gene | quantity
    xref: <external id> | not_specified
```

### `claims_typed.yaml` — claims by their structural form (not their merit)
```yaml
claims:
  - id: C01                       # a REAL logic/claims.md id (seeded deterministically)
    claim_type: generalization | prediction | existence | comparison | mechanism | definition
    polarity: positive | negative
    logical_form: "∀x ∈ …: predicate(x)"     # a formal restatement of what the claim asserts
    population_scope: claimed_universal | sample | single_case
    quantity_refs: [Q01]          # Q## this claim's numbers map to
    concept_refs: [EN-…]          # entities the claim names
    proof_refs: [E01]             # evidence/experiment ids
    depends_on: [C00]             # other claim ids
```
This structures the claim; it never rates it. There is no status/quality/novelty field.

### `genre.yaml` — genre contract (sections present vs absent)
```yaml
paper_type: "e.g. empirical results | format/architecture spec | review | methods"
expected_slots: [ … sections this genre would be expected to contain … ]
present_slots:  [ … of those, the ones actually present in the material … ]
absent_declared: [ … expected slots honestly declared absent … ]
```

### `contributions.yaml` — author-stated contributions, linked to claims
```yaml
contributions:
  - id: CT01
    statement: "the contribution as the authors state it"
    realized_in: [C01, C02]       # the REAL claims that realize this contribution
```
`realized_in` must be non-empty and point at real C## — a referential-integrity requirement
(a stated contribution is linked to the claims that actually carry it). There is **no**
`compiler_assessed_type`, `confidence`, novelty typing, or adjudication — assessing a
contribution's type or novelty is metric construction, not material compilation.

---

## What is explicitly NOT here (it belongs to the separate metric layer)

- novelty / contribution typing, confidence, adjudication
- comparative deltas against prior work (`delta_ledger`)
- off-paper external baselines (`external_quantities`)
- precedence neighborhoods / SOTA anchors (`sota_anchor`)
- rigor tiering (Tier A/B/C) and any significance/breakthrough scoring

If a turn produces any of the above, it is metric work — do not write it into `gro/`.
