# Stage 1 critique — `logic/problem.md`

All four proposers independently landed on nearly the same five-metric skeleton: (1) evidentiary
grounding depth of Observations, (2) argument-graph connectivity / traceability, (3) Key-Insight
synthesis quality, (4) Gap failure-mode specificity, (5) Assumption concreteness. Because the
conceptual coverage is identical, the tournament turns on *implementation soundness*, *how directly
each metric targets the failure modes the shape doc actually names*, and *whether the anti-gaming
claims survive scrutiny*. That is the axis I judged on.

## One-line verdicts + rank

- **agent4 — RANK 1.** Cleanest, most compute-sound set; its Insight metric is the only one that
  directly attacks the documented "Key Insight merely restates the method name" failure (generic-phrase
  blacklist) *and* checks per-node vocabulary overlap against the specific `derived_from` nodes.
- **agent2 — RANK 2.** Carries two genuinely novel Goodhart-resistant ideas no one else has: a
  citation-diversity penalty (M2) that catches the same-citation-pasted-everywhere tell, and an
  assumption-vs-Gap redundancy discount (M5). Traceability also uniquely checks Gap→Insight integration.
- **agent1 — RANK 3.** Most articulate combination argument and a clever insight "sweet-spot" band,
  but its penalty thresholds are set so permissively they rarely fire, and it lacks the cross-node
  checks that make 2 and 4 hard to game.
- **agent3 — RANK 4.** Its Insight metric compares Insight text to its own `Enables` clause — a poor
  synthesis proxy that misses the exact restatement failure the shape doc flags — and its Gap
  proper-noun regex fires on any sentence-initial capital, gutting the specificity signal.

## WINNERS: agent4, agent2

---

## Per-winner critique + Stage-2 directions

### agent4 (Rank 1)

Strengths: The Insight Synthesis metric (M3) is the best-targeted in the field — it combines a
`GENERIC_INSIGHT_PHRASES` blacklist ("we use", "we propose") that directly operationalizes the shape
doc's "restates the method name" degradation signal, with a per-node overlap check (`grounded_nodes`
requiring >=2 shared content words with each *specific* cited node, weighted 0.5). This is a more
robust construction than agent1's single-band Jaccard because it verifies synthesis node-by-node
rather than in aggregate. `argument_graph_connectivity` (M2) cleanly counts invalid refs + orphan
observations + orphan gaps as a single node-fraction penalty and correctly returns 0.0 when
`total_refs == 0` (a bag of assertions with no edges). Discrete grounding tiers in M1 plus the
sub-3-observation `count_penalty` are sound and readable.

Stage-2 improvement directions:
1. **M3 overlap is seedable.** `grounded_nodes` triggers on merely 2 shared content words with a node;
   an adversary can seed two of each cited node's distinctive words into the insight. Move to
   distinctive-term overlap (down-weight terms that appear in *most* nodes; reward terms rare across
   the artifact but shared between insight and one node), or require overlap proportional to node length.
2. **M3 length floor rewards verbosity.** `length_score = min(1, word_count/25)` gives a free 0.2 for a
   long insight regardless of content. Gate the length term behind nonzero overlap, or replace with a
   floor rather than a linear reward.
3. **M4 `linked` term rewards mere presence.** `linked = 1.0 if caused_by else 0.0` gives 0.3 for *any*
   `caused_by` list, even one pointing at nonexistent IDs. Require the `caused_by` to contain at least
   one valid Observation ID (reuse M2's id set) so fabricated links don't earn the anchor credit.
4. **M1 citation detection is year-only.** `CITATION_YEAR` counts bare 4-digit years, gameable by
   writing years. Pair it with an author-token pattern (agent1/agent2/agent3 all use `Author, Year`)
   so "2020, 2021, 2022" alone doesn't score as three citations.

### agent2 (Rank 2)

Strengths: Two anti-gaming mechanisms that are unique in this field and directly answer "would gaming
this metric produce better science or just a better proxy?" — (a) M2's **diversity penalty** docks
Observations whose citation sets are near-identical, catching the "paste one rich citation list into
every Observation" evasion that agents 1/3/4 are all blind to; (b) M5's **redundancy discount** (×0.3)
on assumptions whose vocabulary >70% overlaps a Gap statement, catching assumptions that are just
reworded Gaps padded in for graph coverage. M1's `traceability_completeness` is the only connectivity
metric that separately scores Gap→Insight integration (`gap_integration`), catching listed-but-never-
resolved Gaps. M3's opposing novelty/relevance sub-scores are a legitimate two-sided construction.

Stage-2 improvement directions:
1. **M2 diversity penalty over-penalizes honest thin cases.** When `len(obs) > 1` but only one
   Observation legitimately carries citations, the `len(nonempty_sets) > 1` branch fails and a flat
   0.3 penalty applies ("can't prove diversity"). A genuinely short 2-Observation problem statement is
   punished as if it gamed the metric. Scale the penalty by how many Observations *should* have had
   citations, or only apply it when 2+ Observations share an identical nonempty set.
2. **M2 generic check is exact-match only.** `ev.lower() in GENERIC` misses "Abstract." (trailing
   period), "see abstract", "Abstract, p.3". Use a normalized/regex match as agents 1/3/4 do.
3. **M3 novelty band center (0.55) is unjustified.** `novelty_component = 1 - abs(novelty - 0.55)/0.55`
   hard-codes an optimal 55% novel-vocabulary ratio with no grounding; a legitimate insight that
   heavily reuses precise technical terms from its sources could be scored as "too much restatement."
   Either justify the band empirically against real artifacts or widen it to a plateau (e.g. flat max
   across 0.35–0.75) so honest variation isn't punished.
4. **Extend the redundancy idea to the Insight↔Assumption axis.** M5 checks assumption-vs-Gap
   redundancy; also check that assumptions aren't just the Insight restated, closing the last cheap
   padding path.

---

## Why the losers lost

**agent1 (Rank 3).** Strong writing and the "Insight Synthesis Sweet-Spot" is a genuinely good idea in
principle — penalize both near-copy (`max_overlap > 0.55`) and disconnection (`max_overlap < 0.04`).
The problem is calibration: Jaccard overlap between a short insight and a concatenation of four source
fields (`statement + implication + why_fail + existing_attempts`) will almost never approach 0.55, so
the copy penalty is effectively dead, and the 0.04 disconnection floor is so low that an almost-
unrelated insight still passes. The result is a band that rewards nearly anything with two engaged
sources. More decisively, agent1 lacks the cross-node checks that make the winners hard to game: no
citation-diversity penalty (M1 can be beaten by pasting one citation list everywhere), no Gap→Insight
integration check (M2 only does obs-utilization + ref-validity), and no assumption-redundancy check
(M4 is pure per-item length/number/hedge scoring). It is dominated by agent2 on Goodhart-resistance
and by agent4 on directness, without a compensating edge.

**agent3 (Rank 4).** Two implementation defects sink it. First, its Insight metric (M2,
`insight_non_tautology`) measures lexical overlap between the Insight and its own `Enables` clause —
but the shape doc's named failure is an Insight that "merely restates the paper's method name," which
would *not* necessarily overlap with the `Enables` text, so the metric misses the very failure it
should catch; meanwhile a legitimately good insight whose consequence naturally echoes its mechanism
gets penalized. Second, M3 (`gap_specificity`) uses `propernoun_pat = r"\b[A-Z][a-zA-Z]+\b"` and
awards 0.3 whenever `>= 1` match exists — but every sentence starts with a capital letter, so
`has_propernoun` is true for essentially all non-empty Gap text, making the strongest sub-signal a
near-constant. Its one real strength — the transitive reachability walk in M4 (Insight →
`derived_from` → Gap `caused_by`), the most sophisticated graph traversal of the four — is not enough
to offset a broken insight metric and a near-useless specificity signal.
