# M64 — Controlled-vocabulary & latent-space anchoring — Critique (cycle 1)

Metric: are terms/data anchored to real controlled vocabularies / canonical datasets / latent
spaces (translatable, referenceable via an [ext] ontology/registry resolver)? Net-new
interoperability signal for cross-ARA linking. Judged on: expanded reasoning; a concrete/runnable
resolver→deterministic sub-score workflow; Goodhart-resistance; penalize-don't-skip; genuinely
net-new vs the grounding-family metrics.

---

## Per-expander verdicts

### exp1 — RANK 1 (WINNER)

Verdict: the most rigorous and internally-coherent design in the set. Three things put it on top.

- **Best-argued penalize-don't-skip.** §1.4 is the sharpest reconciliation any expander offers:
  the opportunity space spans §2+§3+§11 *jointly*, and §2/§3 (claims.md/concepts.md) are
  mandatory-core, so there is *never* a zero-opportunity case — genre-correct §11 absence
  redistributes weight rather than skipping, and the "implied-data-without-provenance" flag
  (Step 5, regex over `N=`, cohort, platform, accession-shaped strings) fires the penalty on the
  ARA's *own internal evidence* that data should exist, not on a blanket rule. This threads the
  brief's hard constraint against the shape doc's "correctly absent" note without contradiction.
- **Concrete specificity gating that is actually deterministic.** The OLS4 depth-from-root check
  (`/ancestors`; `ontology_match` requires score ≥70 AND depth ≥3, else `weak_match`/`no_match`)
  is the single most concrete anti-root-term-gaming mechanism across all four — it turns "don't
  reward trivial generic hits" from a slogan into a computed threshold.
- **Fabrication punished harder than omission.** `dead_or_mismatched` → Tier D + `FABRICATION_PENALTY`,
  strictly worse than no attempt. Removes the incentive to paste plausible-but-fake accessions.
  Scoring is fully deterministic given cached resolver snapshots (explicitly called out for
  tournament reproducibility).

Weaknesses (→ cycle 2): (a) **No coverage denominator over an independently-extracted term
universe.** Score is a *mean* of weighted candidates, so a paper anchoring one term perfectly ties
one anchoring twenty — and selective-anchoring gaming (anchor the easy terms, skip the hard ones)
isn't blocked the way exp3/exp4 block it. (b) **"Resolved" is shallow**: `resolved` = HTTP 200 +
accession echoed, with no check that the resolved *record's subject* matches the ARA's stated
context. A real GEO accession for the wrong dataset/species scores Tier A. This is exp2/exp3's
central improvement and exp1's biggest gap.

### exp3 — RANK 2 (WINNER)

Verdict: the most *complete* design, and the only one that takes the "latent-space" half of the
metric name seriously as a runnable check.

- **Coverage over an independently-extracted universe.** Step 1 builds the anchorable-term universe
  from concepts.md + claims.md *before* resolution is attempted, so cherry-picking which terms to
  anchor doesn't move the denominator — directly closing the selective-anchoring route exp1 leaves
  open. This is the strongest structural Goodhart-resistance in the set.
- **Latent-space anchoring is real, not gestured at.** Version-pin requirement (GRCh38 not "the
  human genome"; unversioned hits capped at `resolved_ambiguous`=0.4) plus a HuggingFace Hub
  `/api/models/{name}` lookup *requiring a revision/commit or version tag* is the only concrete
  embedding/reference-space resolver proposed. Given the metric is literally "…& latent-space
  anchoring," this coverage matters.
- **Two-stage LLM gating done right.** Anchorability classification (Step 2) runs *before* resolver
  spend and carves out paper-local/novel constructs so they're excluded from the denominator
  unpenalized (genre fairness); the relevance check (Step 4) confirms the resolved definition
  matches the ARA's own `Definition` sense — catching the trivial-generic-match route exp1 misses.
- **Nuanced penalize-don't-skip:** 0.15 floor for absent-data vs strictly-0.0 for
  present-but-unaccessioned (the compiler "had the chance and produced nothing" is worse than
  silent absence), `resolution_error` logged distinctly from `not_found` so degraded tool access
  can't silently improve scores by dropping unchecked terms.

Weaknesses (→ cycle 2): (a) **Genre-exclusion softness.** For a verified theory paper `S_data` is
*excluded from the denominator* (with a 0.1 floor only if both components are excluded). It reports
`n/a` for audit and gates on active verification, so it's defensible — but it is the one place the
design leans toward "skip," and exp1's redistribute-don't-exclude approach is cleaner against the
hard constraint. (b) Relevance/anchorability lean on LLM calls; adopt exp1's deterministic
depth-from-root threshold as a cheaper, non-LLM specificity gate where possible.

### exp2 — RANK 3 (loser)

One genuinely important idea — the **semantic-match check** (LLM returns 0/1/2 on whether the
resolved record's subject matches the ARA's cited context, keeping only the integer) — is the best
answer in the set to context-mismatched real IDs, and both winners should absorb it. But the
overall design is less disciplined: the scoring normalization (`raw/n` landing in ~[-0.8, 1.65]
before clamping, with layered `min()` caps and a −0.4 hard floor) is convoluted and hard to reason
about relative to exp1's clean 0–100, and it is more LLM-dependent than exp1/exp3 without exp3's
independently-extracted coverage universe. Strong instincts, rougher execution.

### exp4 — RANK 4 (loser)

Solid tiering (Tier1 full / Tier2 ×0.6 versioned / Tier3 no-credit), a clean availability table,
a cross-layer consistency check, and good latent-space *examples*. But it has the weakest
penalize-don't-skip of the four: `NOT_APPLICABLE_FLOOR = 0.5` returns a fixed mid-scale constant
for genre-correct absence, which reads much closer to a soft "skip" than exp1's redistribution or
exp3's verified exclusion-with-audit. Its specificity gating is also the weakest — `entity_name_match`
token-overlap doesn't guard against trivial generic ontology hits ("cancer"→MeSH) the way exp1's
depth filter or exp3's relevance check do — and its coverage denominator is anchored on dataset.md
rather than an independent concepts/claims universe.

---

## WINNERS: exp1, exp3

Rationale: exp1 and exp3 are the two most concrete and most defensible, and they are strongly
*complementary*. exp1 owns determinism (depth-from-root specificity threshold, cached-snapshot
reproducibility, fabrication>omission) and the cleanest penalize-don't-skip reconciliation; exp3
owns coverage-over-independent-universe (anti-selective-anchoring), genuine latent-space
resolution (version-pin + HF model registry), and the LLM relevance gate. Merging their strengths —
and grafting on exp2's resolved-content semantic-match — yields the target design.

## Cycle-2 directions for winners

**exp1:**
1. Add a **coverage denominator over an independently-extracted term universe** (adopt exp3 Step 1):
   extract the anchorable universe from §2+§3 before resolution so selective anchoring can't game
   the mean. Report raw counts alongside the ratio.
2. Deepen "resolved": add a **resolved-content semantic-match** (adopt exp2's 0/1/2 integer check,
   or a deterministic name-overlap variant) so a real-but-context-mismatched accession can't earn
   Tier A. Reconcile with your fabrication penalty (a mismatched-content hit should sit between
   `resolved` and `dead`).
3. Add explicit **latent-space/version-pin handling** (adopt exp3's HF-registry + build-token
   check) — the metric name demands it and exp1 currently has no latent-space branch.

**exp3:**
1. Tighten the **genre-exclusion** toward exp1's redistribute-don't-exclude framing so the hard
   "never N/A" constraint is honored without any component ever leaving the denominator; keep the
   active-verification + audit-note discipline.
2. Add exp1's **deterministic depth-from-root threshold** as a non-LLM specificity gate feeding the
   relevance check, to cut LLM dependence and make the specificity call reproducible.
3. Specify the **cached-resolver-snapshot reproducibility** guarantee exp1 makes explicit, so the
   two LLM passes plus network I/O still yield a re-runnable deterministic score.

## Loser one-liners

- **exp2:** Best single idea (resolved-content semantic-match) — winners should absorb it — but
  convoluted normalization and heavier LLM dependence without a coverage universe.
- **exp4:** Good tiering and cross-layer consistency, but the 0.5 NOT_APPLICABLE floor is the
  weakest penalize-don't-skip in the set and its specificity gating doesn't block trivial generic
  matches.
