# Stage-1 critique — `01_paper_manifest`

Judge: metascientist + incentive designer. Four blind proposals for scoring the `PAPER.md` root
manifest. The field converged hard: all four center on the same two metrics — (a) claim-count
self-consistency (`claims_summary` length vs. the count baked into the `claims.md` Layer-Index
description) and (b) quantitative density of `claims_summary` (regex for numbers/CI/p/AUC). The
tournament is therefore decided on the *third through fifth* metrics: which sets reach past
compiler-surface features toward something that actually tracks scientific quality, and whose
mechanism design is sharpest.

## One-line verdicts + rank

1. **agent2 — RANK 1.** The only set whose non-core metrics genuinely reach past surface: conditional
   *Epistemic Transparency of Absence* and *Evidentiary Density per Claim* both measure research
   virtues, not artifact bulk. No glaring compute bug. Best combination logic.
2. **agent4 — RANK 2.** Contains the single strongest "measures real science" metric in the entire
   field (*Identifier & Pre-registration Provenance Rigor* — PROSPERO/OSF pre-registration is the
   textbook Nosek/Ioannidis defense against HARKing/p-hacking). Sharp adversarial framing. Dragged
   down by one genuinely broken metric (*Synthesis Value-Add* rewards drift from the abstract).
3. **agent1 — RANK 3.** Competent, well-calibrated, and its *Biblio Honesty* metric shows the sharpest
   incentive-design insight of the whole field (honest "Not specified" scores EQUAL to a valid DOI,
   removing the fabrication incentive). But the set as a whole never leaves surface: counts, digits,
   keyword genericity, string-format checks.
4. **agent3 — RANK 4.** A near-duplicate of agent1 that is strictly weaker at the margins: honest-DOI
   scores 0.6 vs. a valid DOI's 1.0 (re-introducing the very fabrication incentive agent1 designed
   out), and a `min(rows/2, 1.0)` layer-completeness rule structurally caps the trace layer at 0.5 for
   *every* ARA (the shape doc shows `/trace` almost always has exactly one file).

## WINNERS: agent2, agent4

---

## Winner critique + Stage-2 directions

### agent2 (Rank 1)

**Why it wins.** It is the only proposal that spends two of its five metrics on things a
metascientist actually cares about rather than on compiler surface:

- *Metric 3 — Epistemic Transparency of Absence.* This is the standout idea of the tournament. It only
  rewards "no code/data released" disclosure language *conditional on the layer actually being thin*,
  capping disclosed-thinness at 0.75 (still below a rich artifact, honoring the shape doc's "thin =
  penalized" rule). It is Goodhart-resistant by construction — sprinkling disclosure prose onto a
  rich-layer paper hits a branch that is never reached, so it buys nothing. This captures scientific
  honesty about limitations, a genuine virtue, not a surface feature.
- *Metric 5 — Evidentiary Density per Claim.* Normalizing trace-node and evidence-artifact counts by
  claim count is a real overclaiming detector, and the combination logic is sound: splitting one
  finding into many `claims_summary` lines to game density elsewhere directly *lowers* this ratio.

**Sharp critiques (fix in Stage 2):**
1. **Metric 2's floor logic is fragile.** `if vague_pat.search(line) and score == 0.0: score = 0.05`
   only floors a claim as near-worthless if it has zero numbers AND hedging. A claim like "the method
   may improve accuracy by 5%" scores 0.4 (number present) despite being hedged/unfalsifiable. The
   hedging penalty should *subtract* regardless of numeric presence, not act only as a fallback.
2. **Metric 3 disclosure regex is English-surface and shallow.** It rewards the *presence* of a
   phrase, so a compiler that learns the trigger words gets 0.75 for free on any thin paper. Tie the
   reward to whether the disclosed gap is *consistent with* the actual (thin) layer state you already
   detected — you have `thin_physical`/`thin_data` in hand; require the disclosure to name the
   specific missing layer, not just any absence phrase.
3. **Metric 4 (Domain–Claim grounding) hard-codes a 10-word stoplist** — too small to be robust; a
   buzzword-padded domain will still overlap. Consider IDF-style weighting or a larger stoplist.
4. **No bibliographic-identity metric at all.** agent2 dropped DOI/author/year integrity entirely.
   That is a real coverage gap versus agent1/3/4 — the manifest's *primary* job is bibliographic
   identity. Stage 2 should add an identifier-integrity metric (borrow agent1's honest-NA-equals-valid
   design, not agent3's).

### agent4 (Rank 2)

**Why it wins.** *Metric 2 — Identifier & Pre-registration Provenance Rigor* is the best single metric
in the tournament for the stated judging persona: it explicitly rewards a named pre-registration
(PROSPERO / OSF / ClinicalTrials.gov / protocols.io) in the overview, which is a real institutional
defense against p-hacking and HARKing — not an artifact-surface feature. Its adversarial-combination
writeup is also the most rigorous ("the cheapest way to inflate any one actively damages another").
Metric 1's use of `/tables/` and `/figures/` *path* matching (vs. agent1/2/3's looser filename
substring) is the most precise self-consistency implementation of the four.

**Sharp critiques (fix in Stage 2):**
1. **Metric 5 (Synthesis Value-Add) is broken as written — top priority fix.** It scores
   `1.0 - overlap_ratio`, i.e. it *rewards* `claims_summary` lines whose vocabulary is DISJOINT from
   the abstract. A claim entirely unrelated to the abstract scores 1.0. This directly rewards
   hallucination/drift — the opposite of good science, and a straight compute-soundness failure
   against what the metric claims to measure. Redesign so the reward peaks at *moderate* overlap
   (grounded in the abstract) plus *added quantitative content* (numbers/metrics not in the abstract),
   and drops for BOTH near-total copy AND near-total disjunction.
2. **Metric 2's pre-registration reward is genre-biased.** Pre-registration is expected for
   RCTs/systematic reviews but not for theory papers, ML preprints, or datasets. As written a great
   theory paper caps at 0.6. Either gate the 0.4 registration weight on detected genre, or reframe it
   as "verifiability provenance" (code/data DOI counts too), so it isn't a flat penalty on non-trial
   science.
3. **Metric 4's `copy_penalty`** penalizes keywords that are verbatim title substrings — but a keyword
   *should* often echo the title. This risks penalizing honest extraction; soften or drop.
4. **Metric 1 uses exact-equality booleans** where agent1/2 use proportional scoring. Brittle: a 7-vs-8
   claim count scores a hard 0 identical to a 7-vs-70 count. Consider proportional partial credit.

---

## Why the losers lost

**agent1 (Rank 3).** Technically the cleanest, best-calibrated set of the four, and its *Metric 5 —
Biblio Honesty* contains the single sharpest incentive-design move in the tournament: scoring the
honest `"Not specified in paper"` fallback *equal* to a valid DOI, which removes any reward for the
compiler to fabricate a plausible-looking identifier. Its Layer-Substantiveness calibration
(`expected_rows` trace=1) is also correct where agent3's is not. It lost because the *set as a whole*
never escapes compiler surface: Metric 1 (count agreement + H1==title), Metric 2 (digit regex),
Metric 3 (row counts + digit-presence), Metric 4 (keyword genericity), Metric 5 (string-format
checks) are all measuring artifact hygiene, not scientific quality. Against agent2's transparency and
agent4's pre-registration metrics, it brings no metric that reaches toward what "good science"
actually is. A very strong runner-up — its honesty-metric design should be harvested into the Stage-2
winner.

**agent3 (Rank 4).** A near-carbon-copy of agent1 (self-consistency, quant density, layer completeness,
biblio integrity, abstract grounding) that is strictly worse at every point of difference. Its *Metric
4* scores honest `"Not specified in paper"` at 0.6 versus a valid DOI's 1.0 — the exact opposite of
agent1's insight, re-introducing a fabrication incentive. Its *Metric 3* (`min(present_rows / 2.0,
1.0)` per core layer) demands two substantive rows for full credit, structurally capping the
Exploration-Graph layer at 0.5 for essentially every ARA, since the shape doc shows `/trace` normally
holds a single `exploration_tree.yaml` — so a perfectly compiled manifest is penalized by
construction. It offers no metric agent1 doesn't have and executes the shared ones less carefully.
