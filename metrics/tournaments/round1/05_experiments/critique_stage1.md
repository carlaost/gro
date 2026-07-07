# Stage 1 critique — `logic/experiments.md`

## One-line verdicts + rank

1. **agent2** — The most rigorous set: cross-layer `Referential Closure` + claim coverage, a genuine anti-restatement tautology check in `Falsifiable Specificity`, and a cross-experiment redundancy check that targets the shape doc's own "abstract-only compilation" failure mode; cleanly honors the hard constraint including when `claim_ids` is unavailable.
2. **agent1** — Best-interlocked set; `Triangulation / Verification Load` (independent corroboration with similarity-collapse to defeat cloning) is the single strongest "measures science, not surface" metric in the field, backed by clean DAG/cycle integrity and genre-fit.
3. **agent4** — Contains the best single idea (`Metric–Outcome Traceability` / anti "measurement theater"), but weaker compute (a no-op regex, crude fan-out "richness", no cycle detection) drops it below the top two.
4. **agent3** — Competent and clean, but only 4 metrics and three of them are lexical word-counting proxies; no cross-layer binding, no triangulation, no claim coverage — the most surface-leaning set.

## WINNERS: agent2, agent1

---

## Per-winner critique + stage-2 directions

### agent2 (winner)
Sharp strengths:
- `Referential & Structural Closure` is the only proposal that verifies `Verifies` ids actually resolve into `claims.md`'s id space AND scores claim *coverage* (fraction of claims backed by ≥1 experiment). This is real compilation work to satisfy, not a one-file edit — genuinely Goodhart-resistant. Crucially it treats unavailable `claim_ids` as a *penalty* (0), not a skip, which is exactly the hard constraint.
- `Falsifiable Specificity`'s tautology check (SequenceMatcher between `Expected outcome` and `Metrics`) is the field's best defense against "prediction" that merely restates what will be measured — a real anti-surface move.
- `Setup/Procedure Grounding`'s cross-experiment redundancy penalty directly targets the documented abstract-only-compilation tell (interchangeable procedures).

Weaknesses to fix in stage 2:
- The tautology penalty and `directional_hits` both lean on hardcoded vocab / string-similarity; a determined gamer can write directional prose that is lexically distinct from `Metrics` yet still vacuous. Consider requiring the directional claim to reference a *named quantity* that also appears in `Metrics` (borrow agent4's traceability idea) so "distinct" can't mean "unrelated."
- `Referential Closure` weights 55% (verifies+coverage) on an external file; state explicitly how the metric degrades when `claims.md` is partially available, and confirm coverage isn't gameable by inventing trivial claims (you assert the other metrics catch this — make that linkage compute-level, not just prose).
- `baseline_rigor`'s `SPECIFIC_TOKEN` proper-noun/version regex is surface-farmable; tie the named comparator to whether it recurs in `Setup`/`Procedure` (you argue this in prose but don't compute it).
- No explicit DAG/cycle check like agent1's — `deps_score` catches dangling but acyclicity is only in `acyclic_score` at 20%; confirm a single cycle is punished hard enough.

### agent1 (winner)
Sharp strengths:
- `Triangulation / Verification Load` is the standout: it rewards a claim corroborated by *genuinely distinct* experiments and uses similarity-collapse so cloning a block to fake two independent lines of evidence yields no credit. This measures an actual property of good science (independent replication of support) rather than any text surface.
- `Structural Integrity & Anti-Padding` does real DAG + cycle detection and a pairwise-similarity padding penalty against the min-3-block headcount gate.
- `Method–Measurement Fit` is a smart abstract-only-compilation detector (genre inferred from `Setup` keys must match `Metrics` vocab).

Weaknesses to fix in stage 2:
- `_GENRE_SETUP_KEYS` / `_GENRE_METRIC_VOCAB` are hardcoded and brittle; unrecognized genres get a flat 0.3, which risks penalizing legitimate free-form fields (the shape doc stresses `Setup` subkeys are free-form). Either broaden coverage or replace the fixed vocab with an internal consistency check (does `Metrics` vocab echo terms actually present in this block's `Setup`/`Procedure`?), which is genre-agnostic and less gameable.
- The `diversity_bonus = 1.1` in `Comparator Rigor` and the `0.7/0.3` blends in `Triangulation` are arbitrary magic numbers — justify or tune.
- Triangulation depends only on this file's `Verifies` lists; it can't tell a real claim from an invented one. Consider optionally binding to `claims.md` (borrow agent2's referential closure) so triangulation counts only over claims that actually exist.
- `SequenceMatcher` on full Setup+Procedure text is O(n²) and sensitive to boilerplate phrasing; consider token-set overlap to reduce false "independence" from trivial rewording.

---

## Why the losers lost

**agent4** had the single best novel metric — `Metric–Outcome Traceability`, which flags "measurement theater" when `Metrics` lists quantities that `Expected outcome` never predicts — and `Claim-Coverage Parsimony`'s fan-out idea is genuinely interesting. It lost on compute soundness. `baseline_resolvability_score`'s specific-marker check contains a no-op — `b_clean.replace(b_clean[0], b_clean[0], 1)` replaces the first char with itself and does nothing, so the "proper-noun" detection is effectively broken. The parsimony "richness" proxy (`len(procedure) + len(setup)` with a hard 0.5 ratio cutoff) is crude and would penalize a legitimately efficient experiment that verifies several tightly-related claims. And unlike agents 1/2/3, agent4 has *no cycle detection anywhere* — only dangling-reference checks — so a `Dependencies` cycle passes clean. Strong ideas, too many rough edges to trust the numbers.

**agent3** is clean and its `Cross-Reference & Dependency Structure Integrity` adds a nice touch (a flat, edge-less graph across ≥3 experiments is itself penalized). But with only 4 metrics and three of them (`Numeric-Leakage Discipline`, `Falsifiability/Directionality`, `Procedure Executability Density`) being lexical word-counting proxies, it measures more surface than science. `Procedure Executability` counts capitalized/backtick tokens as a reproducibility proxy — directly farmable by jargon injection, which it concedes and offloads to "a semantic reviewer or companion metric" it doesn't provide. It has no cross-layer claim binding and no triangulation, so it never checks whether experiments actually corroborate claims or each other — the two properties that most separate real science from a well-formatted plan. Solidly built, but the least differentiated and most Goodhartable set.
