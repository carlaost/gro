# Experiments

## E01: Deterministic-tier sidecar extension (12 ARAs)
**Arms**: One arm — extend all 12 already-compiled ARAs with five typed YAML sidecars each: `quantities.yaml` (`Q##`, one canonical typed record per load-bearing number), `claims_typed.yaml` (`C##` with `claim_type`, `logical_form`, `quantity_refs`, `concept_refs`, `proof_refs`, `population_scope`, `population_n`), `refs.yaml` (`R##` with `external_id` and a `resolvable` boolean), `entities.yaml` (`EN` records with `xref`), `genre.yaml` (`paper_type`, `expected_slots`, `present_slots`, `absent_declared`).

**Method**: Extraction rule was "no guessing": `not_specified` used for any field lacking ARA-internal grounding; honest absences (no printed DOI, no released dataset, no code) recorded as such rather than filled. Every sidecar file was validated with `yaml.safe_load` and passed a cross-reference consistency check (each `quantity_ref`/`concept_ref`/`depends_on` resolves to a real id).

**Result**: All 12 ARAs extended; sidecars produced under each ARA's `gro/` directory. This extension phase is the input the metrics phase (E02) consumes; its success is confirmed downstream by `aras_failed: []` in `results.json`.

---

## E02: Corpus-wide Tier-A metric computation (8 metrics × 12 ARAs)
**Arms**: One arm — compute all eight Tier-A metrics (`quantity_reconciliation_rate`, `claim_typing_coverage`, `entailment_precondition_rate`, `reference_resolvability_rate`, `entity_anchoring_rate`, `genre_silent_omissions`, `overclaim_flags`, `broken_ref_integrity`) as pure structural joins over the five sidecars per ARA — no LLM calls, no network calls.

**Method**: Run over all 12 ARAs; record per-ARA and corpus-aggregate (mean/min/max) values in `results.json`/`results.md`.

**Result**: All 12 ARAs processed; zero failures (`aras_failed: []`). One real bug surfaced during development: several ARAs (zim25, jes26, xu25, ard25) print negative numbers with the Unicode minus (U+2212) rather than ASCII hyphen-minus, which silently dropped the sign in the reconciliation lexer until normalized — `jes26` was misread as 0.667 instead of the correct 1.000 before the fix. Corpus aggregates after the fix:

| Metric | Mean | Min | Max | Coverage |
|---|---|---|---|---|
| quantity_reconciliation_rate | 1.000 | 1.000 | 1.000 | defined on 10/12 (2 null) |
| claim_typing_coverage | 1.000 | 1.000 | 1.000 | defined on 12/12 |
| entailment_precondition_rate | 0.821 | 0.400 | 1.000 | defined on 12/12 |
| reference_resolvability_rate | 0.374 | 0.000 | 1.000 | defined on 12/12 |
| entity_anchoring_rate | 0.000 | 0.000 | 0.000 | defined on 12/12 |
| genre_silent_omissions | 0.333 (mean) | −1 | 4 | total 4; 3/12 nonzero |
| overclaim_flags | 1.917 (mean) | 0 | 11 | total 23; 3/12 nonzero |
| broken_ref_integrity | 1.333 (mean) | 0 | 16 | total 16; 1/12 nonzero |

---

## E03: Case study — `broken_ref_integrity` on `ard25`
**Arms**: One arm — apply the `broken_ref_integrity` join (does each `proof_ref` cited by a claim resolve to a real experiment/evidence id?) across all 12 ARAs.

**Method**: Structural join between `claims_typed.yaml` `proof_refs` and each ARA's experiment ledger (`logic/experiments.md` or equivalent).

**Result**: `ard25` scores 16 — its `claims.md` cites nine proof references (E01–E09, and E10/E11) with no `logic/experiments.md` or any experiment ledger anywhere in the ARA to resolve them against, so all 16 `proof_ref` occurrences across its claims are structurally broken. `ard25`'s own `genre.yaml` commentary independently documents that several layer files its `PAPER.md` claims to contain (experiments, concepts, related_work) do not actually exist on disk. The same metric returns 0 for all other 11 ARAs.

---

## E04: Case study — `entity_anchoring_rate` corpus-wide
**Arms**: One arm — compute the fraction of entities with `xref != not_specified` per ARA, across all `entities.yaml` sidecars.

**Method**: Structural join/count over `entities.yaml` `xref` field, corpus-wide (176 entities total across 12 ARAs).

**Result**: 0.000 for every one of the 12 ARAs — every one of the 176 entities in the corpus carries `xref: not_specified`. The schema slot exists and the metric runs without error; the compilation pass simply never populated a single ontology cross-reference.

---

## E05: Case study — `reference_resolvability_rate` spread
**Arms**: One arm — compute the fraction of refs with `resolvable == true` per ARA, across all `refs.yaml` sidecars.

**Method**: Structural join/count over `refs.yaml` `resolvable` boolean, per ARA and corpus-aggregate.

**Result**: Ranges from 0.000 to 1.000 across the corpus (mean 0.374). `cum26` posts 1.000 (all 10 refs carry printed DOIs); `val25`, `zho25`, and `ard25` post 0.000 (every ref has `external_id: not_specified`). The spread indicates the reference-resolution step of the extension was applied unevenly across the corpus rather than as a uniform stage.

---

## E06: Case study — `overclaim_flags` concentration
**Arms**: One arm — apply the overclaim rule (a `population_estimate`-typed claim with `population_n: not_specified` is flagged) across all 12 ARAs' `claims_typed.yaml`.

**Method**: Structural join/count over `claims_typed.yaml` `claim_type` and `population_n` fields, per ARA and corpus-aggregate.

**Result**: Total 23 flags across the corpus. `cum26` (9/10 claims) and `xu25` (11/13 claims) account for 20 of the 23; the third contributor is `zho25` (3). These are the pipeline/registry-census and GBD epidemiological ARAs, whose claims are typed `population_estimate` with `population_n: not_specified`. The remaining 10 ARAs post zero.

---

## E07: Case study — `genre_silent_omissions` negative-count artifact (`zho25`)
**Arms**: One arm — compute `count(expected_slots) − count(present_slots) − count(absent_declared)` per ARA's `genre.yaml`.

**Method**: Literal structural count over the three slot sets in `genre.yaml`, per ARA and corpus-aggregate.

**Result**: Corpus total 4, nonzero on 3/12 ARAs. `zho25` returns **−1**: its `genre.yaml` lists `experiments` in `present_slots` but not in `expected_slots`, driving the literal count formula negative. Reported as-is (not clamped), documented as a real signal that the count-based formula is fragile against a `present_slot` value outside the `expected_slots` set.

---

## E08: Prose-baseline contrast (`computable_on_prose`)
**Arms**: One arm — for each of the 8 metrics, determine and record whether it is answerable as a lookup on the original prose `PAPER.md`, and if not, why not.

**Method**: Per-metric documentation in `results.json`'s `metric_definitions`, stating `computable_on_prose: true/false` and a `prose_reason` string.

**Result**: All eight metrics are `computable_on_prose: false`. Each failure reason has the same shape: the typed field the metric reads is simply not present in prose (e.g., prose claims carry no `claim_type`/`logical_form`; prose citations are free-text strings with no `resolvable` field; prose entity mentions have no `xref`; prose has no `expected_slots`/`present_slots`/`absent_declared` triple). After extension (E01+E02), the same eight metrics run as structural joins with identical results run-to-run.

---

## E09: Ground-truth discrimination check (not run)
**Arms**: Would require an arm with an externally labeled corpus of "strong" and "weak" science ARAs, and a check of whether the eight Tier-A metric values separate the two labels.

**Method**: Not performed in this experiment. No external ground truth (quality label independent of the artifact) was constructed or applied.

**Result**: No discrimination test was run, and none of the eight metrics computed in E02–E07 reads anything other than the `gro/` sidecars authored from the ARA itself. This is consistent with — and does not attempt to overturn — the parent v3 metrics tournament's negative result that a metric reading only the artifact "cannot, in principle, verify anything about the world outside that file." The absence of this test is reported as a limitation, not an oversight.
