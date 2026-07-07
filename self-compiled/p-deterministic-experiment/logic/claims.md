# Claims

## C01: Typed sidecar extension converts all eight Tier-A metrics from LLM-blocked to deterministic structural joins
- **Statement**: After extending 12 already-compiled ARAs with five typed GRO sidecars each, all eight Tier-A metrics — each of which is `computable_on_prose: false` on the raw prose ARA — run as pure structural joins with zero LLM calls and zero network calls, processing all 12 ARAs with 0 failures.
- **Status**: supported
- **Falsification criteria**: Would be falsified if any of the eight metrics required an LLM or network call at compute time (as opposed to at sidecar-authoring time), or if any of the 12 ARAs failed to process.
- **Proof**: [E01], [E02], [E08]
- **Evidence basis**: EXPERIMENT_PAPER.md §1–§2 ("Method"), §4 ("The honest contrast: extraction vs. join").
- **Dependencies**: none
- **Sources**:
  - `computable_on_prose: false` (all 8 metrics) ← §1 «every one of them is marked `computable_on_prose: false`» [input]
  - `no LLM calls, no network calls` ← §2 «The eight Tier-A metrics were then computed as pure structural joins over the five sidecars — no LLM calls, no network calls.» [result]
  - `All 12 ARAs processed; zero failures` ← §2 «All 12 ARAs processed; zero failures.» [result]
- **Tags**: computability, deterministic-tier, gro-spec, corpus-run

## C02: `quantity_reconciliation_rate` is 1.000 wherever defined, but is defined on only 10/12 ARAs and is a weaker check than its name implies
- **Statement**: `quantity_reconciliation_rate` has mean/min/max = 1.000/1.000/1.000 across the corpus, but is undefined (`null`) for 2 of 12 ARAs (no quantity referenced by ≥2 claims); moreover, because each `Q##` is authored once with a single canonical value, the check reduces to "is this value rounding-consistent with the numeral in its own authoring quote," not an independent cross-mention reconciliation across abstract/table/discussion prose.
- **Status**: supported
- **Falsification criteria**: Would be falsified if the metric were defined on all 12 ARAs, or if a value other than 1.000 appeared where it is defined, or if the underlying check were shown to perform genuine independent cross-mention reconciliation rather than a single-value self-consistency check.
- **Proof**: [E02]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table), §3 (¶ on zho25/aki26 null), §5 (limitations, weak-check discussion).
- **Dependencies**: [C01]
- **Sources**:
  - `1.000 / 1.000 / 1.000; defined on 10/12 ARAs; 2 undefined (null)` ← §3 «quantity_reconciliation_rate | 1.000 | 1.000 | 1.000 | defined on 10/12 ARAs; 2 undefined (null) — no quantity referenced by ≥2 claims» [result]
  - weak-check characterization ← §5 «because each `Q##` is authored once with one canonical value, the check reduces to "is this value rounding-consistent with the numeral in its own authoring quote," not an independent cross-mention reconciliation across abstract/table/discussion prose» [result]
- **Tags**: quantity-reconciliation, null-coverage, fidelity-ceiling

## C03: `claim_typing_coverage` is 1.000 across the full corpus
- **Statement**: `claim_typing_coverage` (fraction of claims with a valid `claim_type` AND a non-empty `logical_form != not_specified`) is 1.000 (mean, min, and max) across all 12 ARAs, defined on 12/12.
- **Status**: supported
- **Falsification criteria**: Would be falsified by any ARA scoring below 1.000, or by the metric being undefined for any ARA.
- **Proof**: [E02]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table).
- **Dependencies**: [C01]
- **Sources**:
  - `1.000 / 1.000 / 1.000; defined on 12/12` ← §3 «claim_typing_coverage | 1.000 | 1.000 | 1.000 | defined on 12/12» [result]
- **Tags**: claim-typing, coverage, corpus-wide

## C04: `entailment_precondition_rate` averages 0.821 with a range of 0.400–1.000 across the corpus
- **Statement**: `entailment_precondition_rate` (fraction of claims with ≥1 result-role `quantity_ref` AND ≥1 `proof_ref`) has mean 0.821, min 0.400, max 1.000, defined on 12/12 ARAs.
- **Status**: supported
- **Falsification criteria**: Would be falsified by a corpus mean outside 0.821, or a minimum/maximum outside the 0.400–1.000 range as computed by the same join.
- **Proof**: [E02]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table).
- **Dependencies**: [C01]
- **Sources**:
  - `0.821 / 0.400 / 1.000; defined on 12/12` ← §3 «entailment_precondition_rate | 0.821 | 0.400 | 1.000 | defined on 12/12» [result]
- **Tags**: entailment-precondition, corpus-wide

## C05: `reference_resolvability_rate` spans the full 0.000–1.000 range across the corpus, exposing uneven application of the reference-typing step
- **Statement**: `reference_resolvability_rate` (fraction of refs with `resolvable == true`) has corpus mean 0.374 and ranges from 0.000 (val25, zho25, ard25 — every ref `external_id: not_specified`) to 1.000 (cum26 — all 10 refs carry printed DOIs), indicating the reference-resolution step of the extension was applied unevenly rather than uniformly across the corpus.
- **Status**: supported
- **Falsification criteria**: Would be falsified if the metric's range collapsed to a narrow band (indicating uniform application) or if cum26 or val25/zho25/ard25 scored differently under the same join.
- **Proof**: [E05]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table + "reference_resolvability_rate varies..." paragraph).
- **Dependencies**: [C01]
- **Sources**:
  - `0.374 / 0.000 / 1.000` ← §3 «reference_resolvability_rate | 0.374 | 0.000 | 1.000 | defined on 12/12» [result]
  - `cum26 = 1.000; val25, zho25, ard25 = 0.000` ← §3 «cum26 posts 1.000 (all 10 refs carry printed DOIs); val25, zho25, and ard25 post 0.000 (every ref has `external_id: not_specified`).» [result]
- **Tags**: reference-resolvability, pipeline-inconsistency

## C06: `entity_anchoring_rate` is exactly 0.000 across all 12 ARAs and all 176 entities
- **Statement**: `entity_anchoring_rate` (fraction of entities with `xref != not_specified`) is 0.000 for every one of the 12 ARAs, uniformly — every one of the 176 entities in the corpus carries `xref: not_specified` — even though the metric is defined and runs without error on 12/12.
- **Status**: supported
- **Falsification criteria**: Would be falsified if any single ARA's entity-anchoring rate were nonzero, or if the total entity count across the corpus were not 176.
- **Proof**: [E04]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table + "entity_anchoring_rate is exactly 0.000..." paragraph).
- **Dependencies**: [C01]
- **Sources**:
  - `0.000 / 0.000 / 0.000; defined on 12/12; uniformly empty` ← §3 «entity_anchoring_rate | 0.000 | 0.000 | 0.000 | defined on 12/12; uniformly empty» [result]
  - `all 12 ARAs and all 176 entities; xref: not_specified` ← §3 «`entity_anchoring_rate` is exactly 0.000 across all 12 ARAs and all 176 entities. Every entity carries `xref: not_specified`.» [result]
- **Tags**: entity-anchoring, unpopulated-schema, null-result

## C07: `broken_ref_integrity` caught a real structural defect unique to `ard25` — all 16 of its proof-reference occurrences are broken
- **Statement**: `broken_ref_integrity` returns 16 for `ard25` — its `claims.md` cites nine proof references (E01–E09, and E10/E11) with no `logic/experiments.md` or any experiment ledger anywhere in the ARA to resolve them against, so all 16 `proof_ref` occurrences across its claims are structurally broken — while the metric returns 0 for all other 11 ARAs (corpus total 16, nonzero on 1/12).
- **Status**: supported
- **Falsification criteria**: Would be falsified if `ard25` had a `logic/experiments.md` or equivalent ledger that resolved its proof_refs, or if any other ARA in the corpus also scored nonzero on this metric, or if the total across the corpus were not 16.
- **Proof**: [E03]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table + "The joins compute, and one of them found a real defect" paragraph).
- **Dependencies**: [C01]
- **Sources**:
  - `1.333 (mean) / 0 / 16; total = 16; 1/12 ARAs nonzero` ← §3 «broken_ref_integrity | 1.333 (mean) | 0 | 16 | total = 16; 1/12 ARAs nonzero» [result]
  - `ard25: nine proof references... no logic/experiments.md... all 16 proof_ref occurrences... structurally broken` ← §3 «`broken_ref_integrity` caught `ard25`: its `claims.md` cites nine proof references (E01–E09, and E10/E11) with no `logic/experiments.md` — or any experiment ledger — anywhere in the ARA to resolve them against, so all 16 `proof_ref` occurrences across its claims are structurally broken.» [result]
  - `same metric returns 0 for the other 11 ARAs` ← §3 «The same metric returns 0 for the other 11 ARAs, confirming it is not firing spuriously.» [result]
- **Tags**: broken-ref-integrity, structural-defect, case-study

## C08: `overclaim_flags` concentrates in the two population-scale genres, accounting for 20 of the corpus's 23 total flags
- **Statement**: `overclaim_flags` (a `population_estimate`-typed claim with `population_n: not_specified`) totals 23 across the corpus (mean 1.917, max 11); `cum26` (9/10 claims) and `xu25` (11/13 claims) together account for 20 of the 23, with `zho25` contributing the remaining 3; the other 10 ARAs post zero.
- **Status**: supported
- **Falsification criteria**: Would be falsified if the corpus total were not 23, if cum26+xu25 accounted for fewer than 20 of the total, or if any of the other 10 ARAs scored nonzero.
- **Proof**: [E06]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table + "overclaim_flags concentrates..." paragraph).
- **Dependencies**: [C01]
- **Sources**:
  - `1.917 (mean) / 0 / 11; total = 23; 3/12 ARAs nonzero` ← §3 «overclaim_flags | 1.917 (mean) | 0 | 11 | total = 23; 3/12 ARAs nonzero» [result]
  - `cum26 (9/10 claims) and xu25 (11/13 claims) account for 20 of the 23 total flags; the third contributor is zho25 (3)` ← §3 «cum26 (9/10 claims) and xu25 (11/13 claims) account for 20 of the 23 total flags; the third contributor is zho25 (3). ... The other 10 ARAs post zero.» [result]
- **Tags**: overclaim-flags, quantifier-inflation, population-scale-genres

## C09: `genre_silent_omissions` totals 4 across the corpus and goes negative (−1) for `zho25` due to a present-slot outside the expected set
- **Statement**: `genre_silent_omissions` (`count(expected_slots) − count(present_slots) − count(absent_declared)`) totals 4 across the corpus (mean 0.333, nonzero on 3/12 ARAs) and is **−1** for `zho25`, because its `genre.yaml` lists `experiments` in `present_slots` but not in `expected_slots`, driving the literal count formula negative.
- **Status**: supported
- **Falsification criteria**: Would be falsified if the corpus total were not 4, if `zho25`'s value were not −1, or if `zho25`'s `genre.yaml` did not in fact list `experiments` as present-but-not-expected.
- **Proof**: [E07]
- **Evidence basis**: EXPERIMENT_PAPER.md §3 (results table + closing paragraph on zho25's negative count).
- **Dependencies**: [C01]
- **Sources**:
  - `0.333 (mean) / −1 / 4; total = 4; 3/12 ARAs nonzero` ← §3 «genre_silent_omissions | 0.333 (mean) | −1 | 4 | total = 4; 3/12 ARAs nonzero» [result]
  - `zho25's genre_silent_omissions is −1 ... genre.yaml lists experiments in present_slots but not in expected_slots` ← §3 «zho25's `genre_silent_omissions` is **−1** — a genuine internal-consistency artifact: its `genre.yaml` lists `experiments` in `present_slots` but not in `expected_slots`, driving the literal `count(expected) − count(present) − count(absent_declared)` formula negative.» [result]
- **Tags**: genre-silent-omissions, negative-count, formula-fragility

## C10: A Unicode-minus (U+2212) parsing bug caused `jes26` to be misread as 0.667 instead of the correct 1.000, before normalization fixed it
- **Statement**: During development of the metrics phase, several ARAs (zim25, jes26, xu25, ard25) print negative numbers using the Unicode minus sign (U+2212) rather than ASCII hyphen-minus; this silently dropped the sign in the reconciliation lexer until normalized, causing `jes26` to be misread as 0.667 instead of its correct value of 1.000.
- **Status**: supported
- **Falsification criteria**: Would be falsified if `jes26`'s pre-fix computed value were not 0.667, if its post-fix value were not 1.000, or if the root cause were something other than the U+2212 character being dropped by the lexer.
- **Proof**: [E02]
- **Evidence basis**: EXPERIMENT_PAPER.md §2 ("Metrics phase").
- **Dependencies**: [C01]
- **Sources**:
  - `several ARAs (zim25, jes26, xu25, ard25) print negative numbers with the Unicode minus (U+2212)... jes26 was misread as 0.667 instead of the correct 1.000` ← §2 «During development one real bug surfaced and was fixed: several ARAs (zim25, jes26, xu25, ard25) print negative numbers with the Unicode minus (U+2212), which silently dropped the sign in the reconciliation lexer until normalized — jes26 was misread as 0.667 instead of the correct 1.000.» [result]
- **Tags**: parsing-bug, unicode-minus, reproducibility, bug-fix

## C11: The deterministic tier does not and cannot test whether these metrics discriminate good science from bad, because every metric reads only the typed artifact
- **Statement**: No external ground truth (a labeled good/bad-science corpus) was used in this experiment; none of the eight deterministic metrics computed here reads anything other than the `gro/` sidecars, so they measure compilation and documentation integrity — internal consistency, self-declared-field coverage, id-graph soundness — and not the correctness, validity, or importance of the underlying findings, consistent with the parent v3 metrics tournament's finding that a metric reading only the artifact "cannot, in principle, verify anything about the world outside that file."
- **Status**: hypothesis
- **Falsification criteria**: Would be falsified by constructing an external, artifact-independent good/bad-science label set and showing that any of the eight deterministic metrics (or a combination of them) systematically separates the labels above chance.
- **Proof**: [E09]
- **Evidence basis**: EXPERIMENT_PAPER.md §5 ("No test of whether the metrics discriminate good science from bad").
- **Dependencies**: [C01]
- **Sources**:
  - `no external ground truth... did not label any ARA as strong or weak science` ← §5 «There is no external ground truth in this experiment. We did not label any ARA as strong or weak science and check whether the metrics separate them.» [input]
  - `Every one of the eight deterministic metrics reported here reads only the gro/ sidecars` ← §5 «Every one of the eight deterministic metrics reported here reads only the `gro/` sidecars. They measure compilation and documentation integrity ... and nothing about the correctness, validity, or importance of the underlying findings.» [result]
  - parent tournament quote ← §5 «"a well-compiled record of bad science and a well-compiled record of good science are, by construction, indistinguishable to every metric in this tournament," because a metric that reads only the artifact "cannot, in principle, verify anything about the world outside that file."» [input]
- **Tags**: limitation, no-ground-truth, inherited-negative-result, quality-discrimination
