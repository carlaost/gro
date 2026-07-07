# Stage 2 Critique — artifact `claims` (`logic/claims.md`)

Mapping: **A = agent2** (Proposer 2), **B = agent4** (Proposer 4). Both were stage-1 winners.
Both improved sets are strong and each fully executed the directions I gave. The decision comes
down to structural coverage, robustness of the shared checks, and — decisively — measurement
*validity* on the artifact's most common real-world case.

---

## (1) Did each winner address the stage-1 critique?

### A (agent2) — all four directions addressed
1. **Add evidence/interpretation-separation metric** → **Done.** New **Metric 6** scans
   `Evidence basis`/`Statement` for evaluative language *and only penalizes it when the word is
   absent from the claim's own `Sources` quotes* (the grounded-leak test I asked for), plus a
   token-overlap collapse check on `Interpretation`. Closes the one named coverage hole.
2. **Make M4 reliance-share transitive** → **Done.** M4 now walks the full transitive closure of
   dependents; the write-up correctly notes that reshaping a chain to look shallower no longer
   reduces the anchor's transitive-dependent count.
3. **Harden M3 against ID-splitting** → **Done, and then some.** Canonicalizes `E01a/E01b → E01`
   *and* collapses two distinct IDs that resolve to an identical `Sources[*].ref` set, with an
   extra penalty for claims whose multiplicity depended on a collapsed split.
4. **Down-weight/drop `tag_ratio`** → **Done.** Tag discipline is now only a capped (−0.05)
   compliance-floor deduction, never a rewarded dimension.

### B (agent4) — all four directions addressed, plus a rebuilt structural metric
1. **Replace length proxies with content proxies** → **Done.** M1 drops `len(fals.split())/15`
   for a *novel-number* proxy (numbers in `Falsification` new vs. `Statement`) + cross-claim
   boilerplate similarity. M6 (`_status_richness`) is now built purely from verified-quote count,
   distinct-ref count, and operational-falsification presence — word count removed entirely.
2. **Make M6 disparity penalty asymmetric/threshold-gated** → **Done.** Fires only in the
   selective-reporting direction (`supported` richer than the worst non-`supported` bucket) and
   only past a 0.15 floor, so a legitimately terse null result is not punished.
3. **Grow M3 lexicon into a grounded "value-judgment without a source quote" test** → **Done.**
   Same grounded-leak construction as A's M6.
4. **Relax/document M4 ordering assumption** → **Done.** Forward-reference is now an explicitly
   *soft*, low-weighted heuristic, cleanly separated from objective dangling/self-reference errors,
   with the non-guaranteed ordering assumption stated in a comment.
5. **Bonus:** rebuilt anchor-fragility + monoculture as a new **M5** keyed on `Sources[*].ref`
   *from the ground up* (not `Proof`-ID strings), so ID-splitting is structurally impossible rather
   than patched after the fact.

Both cleared their assignments. This is now a contest between two competent 6-metric sets.

---

## (2) Decision

**WINNER: B (agent4).**

Three substantive edges, in order of weight:

- **Measurement validity on the common case.** The shape doc states plainly that `Status` "skews
  heavily to `supported`… because compilers extract what the paper reports as its findings" — an
  all-`supported` ARA (especially a meta-analysis) is *normal*, not a bad-science signal. A's
  **M5 (Status Diversity)** penalizes this hard: an honest all-`supported`, no-qualifier claim set
  scores near **0** (credible-diversity term = 0, plus the scaling `shortfall` penalty). That is a
  false penalty on legitimate science and the weakest link in A's set — it drifts toward measuring
  a surface label distribution rather than science. B's **M6 (Status–Documentation Calibration)**
  handles the same case far more defensibly: its primary signal is *documentation symmetry across
  status buckets* (selective reporting), the all-`supported` monoculture penalty is secondary and
  capped at 0.4, so an honest all-`supported` set lands around 0.6 rather than 0. B measures the
  right thing (was the disconfirming result documented as rigorously as the confirmed one?) instead
  of demanding a status distribution the artifact has no reason to exhibit.

- **More complete dependency-structure coverage.** B carries *two* structural metrics: **M4
  (Dependency Graph Integrity)** — cycles (hard-zero), dangling refs, self-reference, **free-riding**
  (a dependent claim with zero sources of its own = re-assertion dressed as a new finding), and a
  flat-list penalty — *and* **M5 (transitive anchor fragility + monoculture)**. A folds only cycle
  detection into its single M4 and has no free-rider or dangling-reference check. Free-riding in
  particular is a real bad-science signature A leaves uncovered.

- **Cleaner monoculture construction.** B credits evidence distinctness by `Sources[*].ref` from
  the start, so splitting one experiment into `E01a/E01b` cannot manufacture diversity — the metric
  is *structurally* immune. A reaches the same place, but via a more convoluted canonicalize-then-
  collapse patch over `Proof` cluster IDs that has more edge-case surface.

A's genuine advantage — an explicit per-claim triangulation *reward* (M3) — is the weaker kind of
signal: rewarding proof multiplicity mildly incentivizes citing more experiment IDs, whereas B
captures the real signal (does apparent breadth collapse to one dataset?) as a *penalty* only,
without the reward's downside. Not enough to offset the three edges above.

**WINNER: B**

---

## (3) Qualification of the winner — honest, not celebratory

**What B genuinely measures.** B is a six-axis proxy for *epistemic hygiene and compilation rigor*,
computed directly over the fields the shape doc mandates:
- **Auditability** (M2): every load-bearing number in a `Statement` is traceable to a verbatim
  quote at a locator, with the value appearing *inside* the quote — this catches silent rounding
  and fabricated grounding, and is the single most load-bearing check for this artifact.
- **Operational falsifiability** (M1): rejection conditions carry checkable numbers/comparators and
  are claim-specific, not templated.
- **Fact/gloss separation** (M3): evaluative language is confined to `Interpretation` or grounded
  in a source quote, not smuggled into `Evidence basis` as if measured.
- **Structural soundness** (M4): the claim graph is an acyclic, non-free-riding, non-flat DAG.
- **Non-concentration + anchor robustness** (M5): breadth doesn't reduce to one dataset, and no
  long dependency chain rests on one thin anchor.
- **Documentation symmetry** (M6): disconfirming results are documented as rigorously as confirmed
  ones.

Together these measure whether the claims are **checkable, structurally distributed, and candidly
reported** — and the joint-hardness argument (no single edit raises all six without doing the real
grounding work) largely holds because the six metrics key on six different, non-independently-
manipulable fields.

**Where it is still gameable or limited.**
- **It measures the compilation, not the paper's truth.** Every check runs over the ARA's own
  fields. A well-compiled artifact of a *wrong* paper scores as high as a well-compiled artifact of
  a correct one — B rewards faithful, auditable transcription of claims, not whether the claims are
  true, important, or reproducible. This is the fundamental ceiling.
- **Grounding fidelity (M2) verifies `value ∈ quote`, not `quote ∈ real source`.** A fabricated
  quote that happens to contain the claimed value passes. B correctly notes M2 can't reach outside
  the artifact to the actual paper; the check is "is this internally consistent and precise," not
  "does the cited location really say this."
- **The leak checks (M3) rest on partial-coverage regex/lexicon.** A synonym outside the pattern
  dodges detection. B is honest that coverage is necessarily partial; the mitigation (a dodged term
  only helps a compiler trying to sound authoritative, and the *safe* move is to quote it) is sound
  but not airtight.
- **Anchor fragility / monoculture (M5) infer "independent evidence" from distinct `ref` strings.**
  Two genuinely dependent analyses written into different evidence files read as independent. It
  measures *reference* diversity, a proxy for — not a guarantee of — evidentiary independence.
- **M6's richness is a floor'd proxy.** A verbose-but-thin compiler can no longer farm it with word
  count, but two well-grounded sources max out the "richness" signal, so it saturates and can't
  distinguish "adequately grounded" from "exhaustively grounded."

**What it would take to trust it.** (a) Cross-check a sample of `Sources` quotes against the actual
cited paper/evidence file — to close the "internally consistent but fabricated" gap in M2/M5.
(b) Human or model spot-audit of the leak-check misses to confirm the regex isn't systematically
dodged. (c) Calibration against a labeled set of known-good vs. known-thin ARAs to confirm the
weights track expert judgment rather than just field-population.

**Does it clear "measures good science"?** **Honest-but-limited — it does not clear the full bar,
and B is candid about this.** It is an excellent measure of *whether an ARA's claims are
auditable, structurally coherent, and candidly reported* — i.e., good scientific *bookkeeping and
compilation discipline*. It is not, and cannot be from these fields alone, a measure of whether the
underlying science is correct or significant. Within that honest scope it is the stronger of the
two finalists: more complete structural coverage, structurally (not cosmetically) hardened against
ID-splitting, and — the deciding factor — it does not punish the legitimate all-`supported` artifact
that the shape doc says is the norm.

---

02_claims stage2 winner: B — measures rigor, not scientific truth
