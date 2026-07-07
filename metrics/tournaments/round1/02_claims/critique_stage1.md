# Stage 1 Critique — artifact `claims` (`logic/claims.md`)

Judge: metascience / incentive-design panel. Four proposers, 5 metrics each, scored on
(a) measures SCIENCE vs. surface features, (b) Goodhart-resistance under honest scrutiny,
(c) the hard constraint (assume inputs, penalize missing — never skip/N/A), (d) compute
soundness against the documented shape, (e) joint (set-level) gaming resistance.

All four independently landed on the same backbone — Falsifiability Operationalization,
Grounding Fidelity, Dependency-Graph Integrity, and a Status-diversity / candor metric. The
tournament is therefore decided almost entirely on *execution details*: whether the grounding
check verifies `value ∈ quote`, whether the dependency check detects cycles, whether the
status-diversity check has a credibility filter, and whether the fifth metric measures a real
structural property of the science or just a lexicon of surface words.

---

## (1) One-line verdict per proposer

- **agent1 — Rank 3 (7.0/10).** Disciplined hard-constraint handling (explicit floors
  everywhere; uniquely models `dependencies_present` to distinguish a structurally-absent field
  from a legit `none`), but its core grounding metric never checks that the claimed value appears
  *inside* the verbatim quote, and its dependency metric has **no cycle detection** — two gaps its
  rivals close.
- **agent2 — Rank 1 (8.7/10). WINNER.** Best grounding metric in the field (verifies
  `value ∈ quote`, locator presence, `[pending]`, and tag discipline), plus two genuinely
  *structural* metrics — Evidentiary Triangulation and Anchor Fragility — that measure whether a
  paper's apparent breadth reduces to one dataset. Cross-claim boilerplate detection. Only real gap:
  no evidence/interpretation-separation metric.
- **agent3 — Rank 4 (6.6/10).** Complete coverage and the single best dependency metric (cycle +
  dangling + isolation + a precise "laundering" subset check), but repeatedly defends its
  anti-gaming claims by punting to "a downstream cross-check or human skim would catch it" —
  outside the metric's own compute — and its status-diversity metric has **no credibility filter**,
  so a token `refuted` claim games it.
- **agent4 — Rank 2 (8.4/10). WINNER.** Grounding metric as strong as agent2's (`value ∈ quote`),
  forward-reference detection in the dependency graph, and a genuinely novel fifth metric
  (Status–Documentation Calibration) that measures whether disconfirming results are documented as
  richly as confirmed ones. Honest about where a metric is weak on its own.

**WINNERS: agent2, agent4**

---

## (2) Why these two

agent2 and agent4 are the only two whose grounding metric — the single most important check for this
artifact, since Rule 16 grounding discipline *is* the artifact's core epistemic guarantee — actually
verifies that the claimed `value` string appears **inside** the `«quote»`. Both also detect cycles,
both gate their status-diversity metric behind a credibility/richness filter so a filler
non-`supported` claim earns nothing, and both add a fifth metric that measures a real structural
property of the underlying science rather than scanning for a hand-list of adjectives. agent1 and
agent3 each miss at least one of these on their most load-bearing metric.

---

## (3) Per-winner critique + stage-2 directions

### WINNER — agent2 (Rank 1)

**What's strong.**
- **M2 Grounding Fidelity & Precision Integrity is the best grounding metric across all four
  proposals.** It is the only one (with agent4) that checks `s.get('value','') in quote` — i.e., it
  catches *silent rounding and paraphrase*, the exact failure the shape doc warns about ("numbers
  copied exactly (never rounded)"). It also separates coverage (Statement→Sources), validity
  (real locator + non-pending quote), precision (value verbatim in quote), and tag discipline into
  four independently-weighted terms. Coverage is correctly computed "from the Statement's numbers
  outward, not the source list inward," which structurally defeats padding `Sources`.
- **M3 Evidentiary Triangulation and M4 Anchor Fragility measure SCIENCE, not surface.** These are
  the standouts of the whole tournament. M3's monoculture penalty (does one experiment ID account
  for >50% of all `Proof` references across the claim set?) detects the case where "the paper's
  entire apparent breadth reduces to one dataset... re-described many times" — a real bad-science
  signature no other proposer captures. M4's reliance-share × weakness formulation correctly makes a
  heavily-depended-upon *but well-grounded* anchor cost nothing, while a heavily-depended-upon *thin*
  anchor dominates the risk — the genuine single-point-of-failure case.
- **M1 FOS's cross-claim boilerplate detector** (pairwise `SequenceMatcher` over all falsification
  criteria) catches template-filling that agent1/agent3/agent4 miss, and its `novelty_ratio` (new
  tokens vs. the Statement) is a sharper "is this a real alternative outcome or a restatement" test
  than a bare entity-overlap flag.
- **M5's credibility filter** only counts a `refuted`/`hypothesis` claim toward diversity if it
  carries real quoted sources — the correct defeat of the token-filler-claim attack.

**What's weak.**
- **No evidence/interpretation-separation metric.** This is the one shape-doc-flagged defect
  (`Interpretation` collapsing into `Evidence basis`; the che26 "effectively obsolete"
  value-smuggling example) that agent2 leaves entirely uncovered, while agent1/3/4 all address it.
  For an artifact whose validation checklist *explicitly* watches for this (Rule 10), that is a
  genuine coverage hole.
- **M4 Anchor Fragility conflates "few dependents" with "low risk."** `reliance_share =
  n_dependents / n_claims` counts only *direct* dependents, so a long transitive chain
  (C05→C04→C03→C02→C01) understates how much actually rests on C01. The prose claims "directly or as
  counted by direct dependents" but the code only does direct.
- **M3's multiplicity reward is mildly Goodhartable in a way the monoculture check doesn't fully
  close:** a compiler can split one experiment into `E01a/E01b` to inflate distinct-ID counts. The
  monoculture penalty keys on *reference share*, not on whether the IDs are genuinely independent
  experiments — the metric has no notion of experiment independence beyond the ID string.
- **M2's `tag_ratio` (0.15 weight) is close to free surface points** — every well-formed entry
  carries `[input]`/`[result]` by spec, so this term rewards field-population more than science.

**Stage-2 directions.**
1. **Add a sixth metric (or fold into M2/M4) for evidence/interpretation separation** — port the
   best version (agent4's vocab-overlap collapse detector + evaluative-term smuggling scan, which is
   more robust than a pure lexicon). Without it the set has a named blind spot.
2. **Make M4 reliance-share transitive** — compute the transitive closure of dependents (or a
   PageRank-style reliance weight) so anchors carrying long chains are correctly scored as
   high-reliance.
3. **Harden M3 against ID-splitting** — either credit experiment multiplicity only when the distinct
   IDs also map to distinct `Sources[*].ref` evidence files, or explicitly note this is out of
   scope. Right now the "genuinely different experiments" claim in the write-up over-promises what
   the code checks.
4. **Down-weight or drop `tag_ratio`** in M2; it is the one near-free surface term in an otherwise
   excellent metric.

### WINNER — agent4 (Rank 2)

**What's strong.**
- **M2 Grounding Fidelity ties agent2 for best-in-field.** `validity_ratio × coverage_ratio` is a
  clean multiplicative gate: "a claim can't score well by having one perfectly-quoted source next to
  five numbers nobody grounded." It checks `value in quote`, locator presence, and gives
  `[pending]` a principled 0.3 (honest but unverified) — a more defensible treatment than agent1's
  binary broken/not-broken.
- **M5 Status–Documentation Calibration is the most original metric in the tournament and measures a
  real science property.** Instead of merely counting non-`supported` claims, it asks whether the
  *documentation effort* (falsification length, evidence length, source count) is **symmetric across
  status buckets** — the `disparity_penalty = max(bucket_avg) − min(bucket_avg)`. This directly
  operationalizes selective reporting: "documentation effort tracked what the authors wanted to
  emphasize, not what's true." Its anti-gaming argument is airtight: a token `hypothesis` claim
  either clears the richness bar (real work) or *widens* the disparity penalty.
- **M4's forward-reference check** (`index[d] >= index[c]` flags a claim depending on a
  later-numbered one) is a compiler-ordering-error detector no other proposer has, and its cycle
  check hard-zeroes the whole score.
- **Intellectual honesty.** M3's write-up openly states the metric "has no cost on this metric alone
  ... which is exactly why it's combined with grounding and calibration below." This is precisely
  the kind of clear-eyed reasoning the joint-hardness argument needs, and it is correct — it does not
  overclaim single-metric robustness the way agent3 repeatedly does.

**What's weak.**
- **M1 and M5 both proxy operational content partly through raw length** (`len(fals.split())/15`,
  `len(evidence.split())/20`). Length is the most Goodhartable surface feature there is — a compiler
  can pad prose to farm both. M1 mitigates with the number/comparator terms; M5's `_status_richness`
  is 40% falsification-length + 30% evidence-length and only 30% source count, so it is more
  length-exposed than it should be. A verbose-but-empty compiler scores well on richness.
- **M5's disparity penalty can fire on legitimate structure.** A single `refuted` ablation claim
  that is genuinely terse (because there's little to say) versus richly-documented supported claims
  produces a disparity penalty even when nothing dishonest happened. The metric assumes symmetric
  documentation is always the ideal; sometimes a null result *is* a one-liner.
- **M3's evaluative-term list is a fixed 17-word lexicon** — trivially dodged by synonyms
  ("outdated" for "obsolete", "leading" for "best"). Shared weakness with agent1/agent3, but real.
- **M4's forward-reference penalty assumes claims are emitted in dependency order.** The shape doc
  says anchors are "commonly" C01, not always; a valid artifact could legitimately reference a claim
  numbered later, and this would be penalized as a "bad ref." The assumption should be stated or
  relaxed.

**Stage-2 directions.**
1. **Replace length proxies with content proxies.** In M1 and especially M5's `_status_richness`,
   swap raw word-count for something gaming-resistant: distinct grounded numbers, distinct source
   refs, presence of a comparator/threshold. Length should be at most a small tiebreaker.
2. **Make M5's disparity penalty asymmetric/threshold-gated.** Only penalize when the *better*-
   documented bucket is `supported` and the *worse* is non-`supported` (the selective-reporting
   direction), and add a small floor so a legitimately terse null result isn't punished.
3. **Grow M3's lexicon into a small embedding/synonym set or a "value-judgment without a source
   quote" test** (borrow agent1's idea: an evaluative word is only a leak if it does *not* appear in
   a `Sources` quote — i.e., the authors didn't actually say it). That converts a brittle word-list
   into a grounded check.
4. **Relax or document M4's ordering assumption** — key forward/dangling detection on graph
   reachability rather than numeric index, or state explicitly that emission order is assumed
   topological.

---

## (4) Per-loser rationale

**agent1 (Rank 3) — lost on the two most load-bearing checks.** The set is well-engineered on the
hard constraint: it is the *only* proposer to model `dependencies_present` so it can distinguish a
structurally-missing field (floor score 0.0) from a legitimate `none` (0.7), which is exactly the
kind of "penalize missing, never skip" discipline the rules demand. But its flagship M1 (Grounding
Coverage & Quote Fidelity) only checks that a source's `value` textually appears among the
`Sources[*].value` blob and that the quote is *non-empty* — it never checks that the value appears
**inside the quote**. That means the whole metric can be satisfied by copying the Statement's numbers
into invented `value` fields with any placeholder quote, and agent1's own defense concedes the real
catch happens "within the compiler's Seal Level 1 check" — *outside the metric's scope*, which the
brief says to dock. Compounding this, M4 has no cycle detection (a circular `C03→C05→C03`
justification passes clean), which agent2/3/4 all catch. Good discipline, but beaten on substance by
the two winners on the artifact's single most important property.

**agent3 (Rank 4) — best dependency metric, weakest anti-gaming rigor.** M5 DGIL is arguably the
finest single metric in the tournament: it combines cycle detection, dangling-reference penalty,
isolation penalty, and a precise "laundering" check (`own_proof ⊆ parent_proof` — a claim that
declares a dependency but adds no evidence of its own is a restatement dressed as a new finding).
But the set repeatedly earns its Goodhart-resistance on credit it hasn't computed: M2 FOI's defense
is that fake statistical vocabulary "would read as nonsense... which a downstream cross-check, or a
human skim, would catch," and M3 RNHR's defense is that a mislabeled `refuted` claim's mismatch is
"directly checkable by cross-reading" — both explicitly outside the metric's own compute. Per the
brief, a metric that relies on an out-of-scope reviewer to close its gaming loophole is docked.
Concretely, RNHR has **no credibility filter** (unlike agent2's M5 and agent4's M5), so tacking on a
single token `refuted`/`hypothesis` claim flips its monoculture penalty for free; and its M1 GCFS,
like agent1's, never verifies `value ∈ quote`. Complete coverage, one excellent metric, but the
per-metric robustness sits a clear notch below the two winners.

---

claims stage1 winners: agent2, agent4
