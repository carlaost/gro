# M64 — Controlled-vocabulary & latent-space anchoring — Critique (cycle 2)

Metric: are terms/data anchored to real controlled vocabularies / canonical datasets / latent spaces
(translatable + referenceable via an [ext] ontology/registry resolver), *and* does a resolvable ID
point at the record this ARA actually means? Net-new interoperability axis vs. the grounding family.

**Cycle status: MIDDLE cycle — both A and B advance to cycle 3. No winner is declared here.** This
critique confirms each addressed its cycle-1 directions, flags the weaknesses that survived the merge,
and gives each design specific, non-overlapping cycle-3 work.

A = built on exp1 (cycle-1 rank 1). B = built on exp3 (cycle-1 rank 2). Both grafted exp2's
resolved-content semantic-match, as instructed.

---

## Did each address its cycle-1 critique?

**A (exp1-derived): all three directions addressed, well.**
1. *Coverage denominator over an independent universe* → Step 1 extracts the anchorable universe
   (concepts + claim Tags + accession-shaped substrings in claim prose + dataset blocks + reference-
   space tokens) *before* resolution; the `assert len(candidates) == n_denominator` invariant forces
   every surviving entry into the mean as Tier D `not_attempted` rather than letting it vanish. This is
   the strongest single closure of the selective-anchoring route in the pair.
2. *Resolved-content semantic-match* → Step 2b + the new **A− (0.55)** tier + `CONTEXT_MISMATCH_PENALTY
   = 4.0` sit exactly where the cycle-1 critique asked: a real-but-wrong-context ID is worse than a
   clean resolve, less bad than a dead/fake one (`4.0 < FABRICATION_PENALTY 8.0`). Correctly placed.
3. *Latent-space/version-pin branch* → Step 2c (build-token enumeration + HuggingFace Hub lookup,
   pinned→A / unpinned→A−). The metric name's second half is now a runnable check, not a gesture.

**B (exp3-derived): all three directions addressed; #3 only partially.**
1. *Redistribute-don't-exclude* → §4.1 replaces exp3's denominator exclusion with an explicit
   `weight_redistribution` event and gates the genre exemption behind an implied-data tripwire
   (§5.2b). Genuinely tighter than cycle-1's single informal check; the mislabel-as-theory route is
   now caught (`N=312 participants` forces `S_data = 0.0`).
2. *Deterministic depth-from-root gate* → §5.4a runs OLS4 `/ancestors` depth ≥3 AND score ≥70 as a
   non-LLM pre-filter that caps shallow hits at 0.4 *without* an LLM call. Correctly cuts LLM spend and
   makes the specificity call reproducible from cached ontology data.
3. *Cached-resolver-snapshot reproducibility* → §5.4b specifies an HTTP snapshot manifest with a
   bit-identical re-run guarantee — **but the contract covers only HTTP resolver calls.** The three LLM
   calls (Step 2 anchorability, Step 4 relevance, §5.6a subject-match fallback) are NOT in the
   manifest. Temperature-0 is not a determinism guarantee across runs; without caching the LLM
   responses, B's "bit-identical re-run" claim has a hole that A closed ("cached LLM-response
   snapshots," A §2.3). **This is B's most concrete cycle-3 fix.**

Both honor penalize-don't-skip: A returns the 0.0 floor with `denominator_degenerate_all_paper_local`
rather than N/A; B redistributes weight and floors at 0.1 if both axes drop out. Neither emits a true
N/A. (B's `data_meta` still carries the literal string `"n/a (genre-verified…)"` for the redistributed
sub-component — cosmetic, since weight is genuinely reallocated, but it reads too close to "skip"; drop
the "n/a" wording in favor of "redistributed.")

---

## The two designs have converged

Starting from opposite bases, A and B now carry nearly the same feature set: independent-universe
coverage, deterministic depth gate, resolved-content subject/context match, fabrication-strictly-worse-
than-omission, version-pinned latent-space handling, cached snapshots, redistribute-don't-exclude. The
cycle-3 decision will not turn on *which features* — it will turn on **which design specifies them
without holes and reasons cleanly about its own scoring arithmetic.** The remaining weaknesses below
are the deciding surface.

---

## A — remaining weaknesses (exp1-derived)

- **Tier ordering inversion: B (0.7) > A− (0.55).** A `named_canonical` dataset (ADNI, TCGA) earns
  Tier B = 0.7 with **no live verification at all** ("no live call needed," Step 2 branch 3), while a
  *live-resolved* accession whose context is merely ambiguous is capped at A− = 0.55, and an unpinned-
  but-real HF model is also 0.55. So an unverified name outscores a verified-but-ambiguous resolution.
  A compiler can bank 0.7 by writing a famous cohort name and never touching a registry. Either
  corroborate `named_canonical` with the optional lookup (make it mandatory) or reorder so unverified-
  by-name ≤ verified-but-ambiguous.
- **Claim-vs-code overstatement on "separate contributions."** §1.2 says quality-per-anchor and
  breadth "are now scored as genuinely separate contributions (Step 1 + Step 7)," but `compute_m64`
  emits a *single blended mean*. Coverage is folded into the mean via Tier-D `not_attempted` entries —
  which is fine and defensible — but it is one number, not two. Either report a separate coverage ratio
  sub-score (the counts are already in the dict; surface `resolved/n_denominator` as its own field) or
  soften the prose. As written it promises a decomposition the code doesn't deliver.
- **Unjustified penalty constants + point/mean interaction.** Four flat point penalties (8 / 4 / 6 / 25)
  are subtracted from a 0–100 mean with no calibration or sensitivity argument. `IMPLIED_DATA_PENALTY =
  25` can swing an otherwise well-anchored paper by a quarter of the scale on a single regex hit; a
  fabricated ID is *double-counted* (Tier D zero-weight in the mean AND −8 points). The double-count is
  defensible as deterrence but the magnitudes are arbitrary — this is the same "convoluted
  normalization" the cycle-1 critique docked exp2 for, creeping back in. Justify the constants or run a
  sensitivity check on a few worked ARAs.
- **Access-tier double-penalty risk with a sibling metric.** Step 6 folds access-qualifier honesty
  (`ACCESS_QUALIFIER_PENALTY = 6`) *into* M64. The shape doc calls access-tier honesty "the key scoring
  axis" for §11 — likely owned by a dedicated sibling metric. B explicitly defers this to avoid double-
  penalizing the same defect (B §3); A does not. Confirm no suite-mate owns access honesty, or scope it
  out.
- **A− escapes the access-qualifier check.** Step 6's code guards only `Tier.A_RESOLVED` and
  `Tier.B_RECOGNIZED`; an A− accession missing its scope qualifier pays nothing. Minor, but inconsistent
  with the intent.
- **The `assert` is a runtime crash, not a score.** `assert len(candidates) == n_denominator` turns a
  pipeline bug (a candidate silently dropped upstream) into a hard exception instead of a scored-down
  result. For tournament robustness, downgrade to a logged flag that floors/penalizes the score.
- **Underspecified extraction heuristics.** Step 1's reference-space/model universe ("proper-noun model
  family names adjacent to 'model'/'checkpoint'…") and the Step 2b context fingerprint are described in
  prose, not code — the one place B is more concrete (B ships regexes). See shared issue below.

## B — remaining weaknesses (exp3-derived)

- **LLM calls are outside the reproducibility contract (see above).** The single most important
  cycle-3 fix: extend §5.4b's snapshot manifest to cache Step 2 / Step 4 / §5.6a LLM responses, or B's
  "bit-identical re-run" guarantee is false the moment an LLM branch fires.
- **Denominator membership is decided by one un-backstopped LLM call.** §5.3's anchorability classifier
  excludes `anchorable=false` terms from the denominator "entirely" on a single LLM judgment, with no
  deterministic seed-list backstop and no audit-logging requirement. This is the softest Goodhart
  surface in either design: craft a `Definition` that reads paper-local and the LLM shrinks your
  denominator. **A hardened exactly this** (dual condition: explicit self-description marker *and* no
  fuzzy match against seed known-vocabulary lists, plus logged rationale, A Step 1b). B should adopt
  A's dual-condition + seed-list + audit-log guard verbatim.
- **Latent-space extraction gap — the branch may never fire where builds actually live.** B's inputs
  (§5.1) and extractors (§5.2) pull concept terms from `concepts.md` and accessions from `dataset.md`
  only. Reference genome builds most commonly appear in `dataset.md` provenance / `method.md` (the
  shape doc's own huu25 example: "SpaceRanger v2.1.0 (GRCh38, 2020-A)"), not as a `## {Term}` heading in
  concepts.md. Unless a build happens to be a glossed concept, B's `reference_genome_build` family is
  never populated — so the metric-name's latent-space half is present in the dispatch table (§5.4) but
  starved of inputs. Add an explicit reference-space/build-token sweep over `dataset.md` + `method.md`
  (A's Step 1 already does this).
- **Coverage universe is narrower than claimed.** §5.1 lists `claims.md` Tags/Sources as inputs, but
  the only extractor shown (`extract_concept_terms`) reads `concepts.md`. Anchorable entities that
  appear only in claim Tags or claim prose (accession-shaped strings in `Statement`) are not in B's
  universe. A extracts these. Either add the claim-universe extractor or drop the claim.md input claim.
- **No partial-credit tier for ambiguous *data* context.** `score_data` is effectively binary on
  subject match: confirmed `mismatch` → −0.15, everything else → 1.0/0.6. An ambiguous/unresolved
  subject-match defaults to full credit (`subject is None` falls through to the access-tier branch),
  whereas A routes data-context ambiguity to A− (0.55). B is more lenient here; consider an ambiguous-
  context partial tier so an unverifiable subject match isn't rewarded as if confirmed.
- **Asymmetric axis weights (S_data 0.55 / S_concept 0.45) unjustified.** Why is data weighted higher
  than the mandatory-core concept axis? State the rationale, or make it defensible per genre.

## Shared weakness (both — worth a cycle-3 note for whichever wins)

- **The subject/context-match determinism rests on a narrow, hardcoded token list.** B ships it as an
  enumerated regex (`ORGANISM_TISSUE_TOKENS`: human/mouse/mm10/GRCh38/postmortem/plasma/brain/blood/
  tumor/cell line) — brittle and human-biomedical-centric; any term outside the list yields empty sets
  and forces an LLM escalation. A describes the fingerprint abstractly and ships no code. Neither is
  right: A is underspecified, B is under-general. The winner should ship a *specified but extensible*
  fingerprint (organism + disease + assay + cohort) with a documented fallback, and state what happens
  when both sides are empty (currently: A escalates, B passes — B's "pass" is the more dangerous
  default because it awards credit to an unverifiable match).
- **The "seed known-vocabulary lists" both invoke are never enumerated.** A's anchorability guard and
  the general specificity story both lean on seed lists that are asserted, not specified. The winner
  should name the seed sources (e.g., HGNC symbols, MeSH/MONDO/ChEBI top-level term dumps, a canonical-
  cohort allow-list) and how they're built/versioned, since they gate denominator membership.

---

## Cycle-3 directions

**A (priority order):**
1. Fix the Tier B > A− inversion: make `named_canonical` require corroboration, or reorder so an
   unverified name cannot outscore a verified-but-ambiguous resolution.
2. Justify or sensitivity-test the four penalty constants; resolve the fabrication double-count
   (Tier-D-zero + flat −8) explicitly rather than incidentally. Consider expressing everything on one
   consistent scale.
3. Confirm access-tier honesty isn't owned by a sibling metric; if it is, scope Step 6 out to avoid
   double-penalty. Extend the Step 6 check to A− accessions if it stays.
4. Either surface a separate coverage-ratio sub-score or soften the "separate contributions" prose to
   match the single-mean code.
5. Downgrade the `assert` to a scored-down flag. Ship the reference-space/context-fingerprint
   extraction as code (borrow B's regexes as a starting point) and enumerate the seed lists.

**B (priority order):**
1. Bring all three LLM calls under the §5.4b snapshot/cache contract — this is required for the
   determinism claim to hold.
2. Harden the anchorability exclusion: adopt A's dual-condition (self-description marker AND no seed-
   list match) + logged rationale so denominator membership isn't a single LLM verdict.
3. Add an explicit reference-space/build-token sweep over `dataset.md` + `method.md` so the latent-
   space branch actually receives inputs; likewise add the claim-Tag/claim-prose universe extractor so
   coverage matches §5.1's stated inputs.
4. Add an ambiguous-data-context partial tier (don't default unverifiable subject matches to full
   credit). State the S_data/S_concept weight rationale.
5. Replace the `"n/a (genre-verified…)"` sub-component label with "redistributed" wording.

Both: converge the subject/context-match fingerprint on a specified-but-extensible field set and
enumerate the seed vocabulary sources.
