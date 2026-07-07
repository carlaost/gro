# Stage 2 critique — `10_implementation`

## Did each winner address the stage-1 critique?

### A (was agent 2) — yes, all four points, cleanly.
1. **Free-pass exits closed.** `capture_to_claim_gap` now routes a mentioned-but-unenumerated repo
   into a vagueness penalty (0.15/0.3) instead of the old 0.7/1.0 free pass, reusing `repo_mentioned`.
   This was the metric's biggest hole and it is genuinely plugged — you can no longer dodge the ratio
   by writing vaguer prose.
2. **Enumeration de-brittled.** Number-word/count-noun detection ("fourteen stages", "12 scripts")
   added, and — importantly — combined with the token tally via `max()`, not sum, so restating the
   same scale five ways cannot inflate the denominator. Good defensive design.
3. **Length free pass dropped** in `disclosed_scope_honesty`; specificity is now token-only.
4. **Compute smells fixed** (explicit join, dedup of paths, `looks_full_bodied` raised to ~30 to
   match the shape doc's own substance bar, with a named-entrypoint carve-out).

### B (was agent 4) — yes, all four, and it addressed the deeper ones more ambitiously.
1. **Surface `NAMED_TOOL_RE` killed.** Replaced with `_grounded_named_tool`, which credits a token
   only if it is in a known-tool lexicon OR actually recurs in `execution/` content. This converts a
   pure capitalization proxy into a genuine cross-layer check — the single best fix in either set.
2. **Length free passes removed** in both `grounding_integrity` and `config_calibration`; fallbacks
   now require specific tokens (named registries, non-clone language, version/parameter-shaped text).
3. **Fabrication gap partially closed** via optional `claim_inventory`: cited `C##` ids are verified
   against the real claim set when visible, and degrade gracefully (documented) when not.
4. **Variance discount generalized** from `config_calibration` to `claim_traceability` (uniform
   "all") and `grounding_integrity` (all-`reconstructed` when a repo is claimed) — its best device,
   now applied in three places.

Both did the assigned homework. This is decided on the merits of the improved sets.

## WINNER: B

### Why B over A

- **Less residual surface.** After revision, A still contains one length gate that does real work:
  `environment_specificity_score` grants full 1.0 credit on `version_re.search(text) or len(text) > 40`.
  The `len > 40` disjunct is exactly the verbosity proxy the brief warns against, and it sits on the
  full-credit path, not a fallback. B's equivalent (`environment_concreteness`) removed length
  entirely and now requires a version number and a *corroborated* tool name (lexicon or execution
  recurrence) to reach 1.0. On the one dimension both sets cover the same way, B is strictly harder
  to game.
- **Cross-layer verification.** B's `_grounded_named_tool` and `claim_inventory` checks reach outside
  the implementation layer to corroborate claims against `execution/` content and the claims layer.
  That is the strongest form of Goodhart resistance available here — you cannot satisfy it with
  in-layer text alone. A has no equivalent cross-layer hook.
- **Broader, non-redundant coverage.** B spends its fifth slot on `claim_traceability`, a distinct
  audit dimension (does each artifact block tie to a real, specific claim?) that A does not cover at
  all. A's five metrics are excellent but cluster more tightly around capture/grounding.
- **More structural traps.** Three uniformity discounts vs. A's zero. The brief rewards SETs that are
  jointly hard to game; B has more independent mechanisms that fire on lazy uniform labeling.

A's `capture_to_claim_gap` remains the single most elegant *individual* idea in the whole tournament
— a real quantitative claimed-vs-captured ratio — and B has nothing quite as sharp. But the brief
judges the SET, and B's set is broader, cross-references other layers, and carries less surface
residue after revision. It is the sounder whole.

## QUALIFY the winner

**What B genuinely measures.** Honesty and traceability of the reproducibility-metadata layer: (1)
whether captured code's declared provenance (`transcribed`/`reconstructed`) matches its actual shape
and cites a source; (2) whether the presence/absence of `execution/` is consistent with what
`artifacts.md` claims and, when absent, whether that absence is *specifically* disclosed vs. silently
dropped; (3) whether config parameters carry rationale in proportion to their stated sensitivity;
(4) whether environment fields are concrete-and-corroborated vs. honestly-flagged-absent vs.
silently-blank; (5) whether artifact blocks tie to real, specific claim ids. In one phrase: it
measures **honest, traceable implementation reporting** — reproducibility hygiene.

**Where it is still gameable or limited.**
- **It scores disclosure discipline, not scientific quality.** A methodologically weak paper with
  meticulous, honest, well-tagged metadata scores high; a strong paper with sloppy metadata scores
  low. That is the correct thing for *this* layer to measure, but it is a proxy for good
  record-keeping, not for good science. Do not read a high B score as "this is good science."
- **Residual length gate.** `capture_proportionality`'s che26-style branch still uses
  `len(code_avail) > 40` to grant 0.7 — the one place B did not fully purge the length heuristic. A
  40-character genre justification clears it.
- **Fabrication defense is conditional.** The claim-id verification only bites when `claim_inventory`
  is wired in; absent that, invented `C##` ids still earn near-full credit. The strongest anti-fraud
  device is optional and, per the doc, often unavailable to a single-layer metric.
- **Version/tool concreteness is falsifiable-in-principle, not verified.** A fabricated version
  string that happens to match the lexicon or is echoed into a stub's imports would pass; B relies on
  cross-layer *inconsistency* to catch fabrication, which only works if the fabrication is
  incomplete.
- **Grounding shape checks are shallow** (line counts, keyword presence, `NotImplementedError`
  idiom). They detect gross mislabeling, not a competent forgery that mimics the right shape.

**What it would take to trust it.** Wire `claim_inventory` in as mandatory rather than optional;
verify cited source locations (file:line, section/table) against the actual source rather than mere
presence; remove the last `len > 40` gate; and pair it with an independent content-fidelity check
(does transcribed code actually match the referenced repo file). Even then it certifies
reproducibility hygiene, not result validity.

**Bar check.** B does NOT clear "measures good science" in the strong sense — it cannot distinguish
sound methodology from honest bookkeeping about unsound methodology. It clears a narrower, real bar:
it is an **honest-but-limited** measure of whether the implementation layer faithfully and traceably
reports what exists, and it is meaningfully Goodhart-resistant within that scope because its highest
scores require cross-layer corroboration that in-layer padding cannot fake.
