# Stage 2 critique — `08_exploration_tree`

A = improved agent2 (Grounded Failure Disclosure, Convergent Synthesis, Decision Deliberation Depth, Pivot Traceability & Consequence, Support-Level Calibration).
B = improved agent4 (Candor Density, Evidentiary Grounding Fidelity, Alternative Substantiveness, Pivot Causal Traceability, Support-Level Signaling Integrity).

## Did each winner address the stage-1 critique?

### A (agent2) — addressed all four directions cleanly
1. **Dropped the `inferred + has_refs` half-penalty.** Done, and done for the right reason: it now tracks only the one mismatch the shape doc actually names (`explicit` with no `source_refs`). This was my strongest objection and A removed the manufactured smell outright rather than papering over it. Good.
2. **Stopword-filtered lexical overlap + raised bar to ≥2 content words.** Done in both `convergent_synthesis_score` and `pivot_traceability_score`, with a shared `words()` helper and a real stoplist that includes the exact offenders I named ("study", "data", "results"). Correct fix.
3. **Capped/re-gated the density bonus.** Now the bonus counts only dead ends scoring ≥0.6, ceiling halved to 0.15. This closes the "pad with cheap dead ends" leak properly — cheap padding is now doubly wasted (drags the average, earns no bonus).
4. **Softened the zero-dead-end floor with a corroborated genre signal.** This is the standout: instead of borrowing agent4's single-signal sniff, A requires *two independent* signals (synthesis vocab in the root question AND ranking/pooled-effect vocab across ≥2 experiment `result` fields). This is strictly more tamper-resistant than what I asked for.

### B (agent4) — addressed all four directions, one imperfectly
1. **Closed the genre-sniff hole.** `is_synthesis` now needs markers on ≥3 distinct nodes, and the discount spread was narrowed from 2.3x to ~1.6x. Both moves are right and the narrowed spread is a nice belt-and-suspenders touch I did not ask for.
2. **Added the fifth lens (Support-Level Signaling Integrity).** Done, and deliberately scoped to exclude the evidence/`also_depends_on` checks owned by Metric 2, so it is a genuine independent axis rather than a duplicate. It also correctly refuses to penalize `inferred + refs`.
3. **Stopword-filtered pivot overlap.** Done, with a length-≥4 shared-token requirement — arguably stricter than A's ≥2-content-word bar on a per-token basis.
4. **Acknowledged frictionless-vs-laundered ambiguity.** Done, with an explicit stated limitation and a cross-check pointer to Metrics 2/5. This is the most epistemically honest single passage in either submission.

Both winners genuinely addressed every direction. This is close.

## WINNER: A

The deciding factors:

1. **The genre-floor fix is materially better in A.** Both softened the synthesis-genre bar, but the danger of that softening is a primary-study compiler buying a discount by faking genre. A's two-signal-must-agree design (question vocab AND independent ranking language across multiple result fields) is a stronger lock than B's "markers on ≥3 nodes" — because in A the two signals are *different kinds* of evidence that must corroborate, whereas B's three hits can all be the same marker vocabulary salted into three titles, which a determined compiler authors just as freely as one. A closes the exact hole I flagged in B at stage 1 more thoroughly than B closed it in itself.

2. **Convergent Synthesis remains the best single metric in the field and got sharper.** A's ancestor-tracking to discard same-lineage `also_depends_on` edges is still the only real DAG-vs-nesting discrimination among all four original entries, and the ≥2-content-word overlap now guards it against boilerplate farming. B has no equivalent — its Pivot Causal Traceability checks pivot→upstream overlap, but nothing in B distinguishes a genuine cross-branch convergence edge from a redundant parent-pointer, so B's structural-synthesis signal is weaker by construction.

3. **B's edge in raw honesty framing does not outweigh A's structural edge.** B's explicit frictionless-vs-laundered disclaimer is admirable and A has nothing as candid, but it is a documentation virtue, not a scoring-power difference — and A's combination essay makes the same cross-check argument (grounding terms tank if labels are gamed) functionally, just less prominently.

B is genuinely excellent and this is the narrowest of the head-to-heads; a different judge could defensibly pick B on the strength of its fifth-lens design and its candor. A wins on the two things that most directly answer this brief's core question — measuring science not surface (the corroborated genre gate resists the surface-vocab attack better) and DAG-convergence discrimination (real integrative-reasoning signal that B lacks).

## Qualify the winner

**What A genuinely measures.** A measures *the disclosure discipline and internal consistency of an extracted research trace* — not the quality of the underlying science directly. Concretely and honestly, it measures: (1) whether disclosed failures are cited, complete, and specific; (2) whether cross-branch dependency edges are structurally real and topically coherent; (3) whether decisions name substantive, distinct alternatives with reasoned evidence; (4) whether pivots are anchored to the upstream nodes that plausibly triggered them; (5) whether confidence labels track citation backing. Jointly, a high score means the trace *looks like* an honest, well-grounded record of real iteration.

**Where it is still gameable or limited.**
- **It scores the trace, not the paper.** A compiler that faithfully extracts a genuinely shallow or bad paper into a well-formed tree scores high; the metric cannot see whether the science was actually good, only whether the record of it is disciplined and self-consistent. This is the fundamental ceiling — it measures reporting integrity as a *proxy* for scientific quality.
- **Lexical overlap is a weak semantic proxy.** ≥2 shared content words is better than 1, but two nodes can share two topical nouns without any genuine causal/logical connection. A determined author writing coherent-but-fabricated node content still passes the overlap checks — the defense is cost, not impossibility.
- **The specificity check (`any digit or ≥8 words`) is coarse** and farmable by padding a lesson with a number or filler length, though the mismatched-signaling and refs checks limit how far that carries.
- **The corroborated genre gate raises the cost of the softer floor but does not eliminate it** — a compiler willing to fabricate ranking-flavored result text across two experiment nodes still buys the discount. A judges this (correctly) as far costlier than editing one title, but it is not airtight.

**What it would take to trust it.** Two things: (a) validation that trace-disclosure scores correlate with independent judgments of scientific quality on a labeled set (otherwise the proxy is unvalidated); and (b) the Level-1 source-groundedness / trace-hygiene check running upstream, since A explicitly leans on "fabricated content is exposed to the same source scrutiny as everything else" — that scrutiny lives outside these five functions. Without upstream source verification, every anti-Goodhart argument in A reduces to "faking this is expensive," not "faking this is caught."

**Does it clear the bar of 'measures good science'?** Honest-but-limited, leaning toward the stronger side of that line. It does not directly measure good science — it measures whether a research trace was disclosed with integrity, which is a defensible and unusually Goodhart-resistant proxy given the artifact it has to work from. Within the constraint of scoring one YAML trace file, it is close to the best achievable, and the set is genuinely jointly hard to game. But it should be reported as a *disclosure-integrity* metric, not a *scientific-quality* metric, and its guarantees are contingent on an upstream source-grounding check it does not itself perform.
