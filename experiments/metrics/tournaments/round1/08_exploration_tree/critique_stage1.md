# Stage 1 critique — `08_exploration_tree`

## One-line verdicts + rank

1. **agent2** — Only entry that distinguishes genuine cross-branch convergence from redundant same-lineage `also_depends_on`, and adds a unique cross-cutting Support-Level Calibration honesty metric; strongest interlock.
2. **agent4** — Genre-normalized Candor Density is the most principled answer to "science vs. surface," and its alternatives metric (generic blocklist + distinctness + concreteness) is best-in-class; loses a notch for only 4 lenses and a genre-sniff gaming hole.
3. **agent3** — Correct, clean, hard-constraint-compliant, but every metric is a softer variant of the winners': exact-string distinctness, no same-branch edge detection, pivot linkage with no content check.
4. **agent1** — Flagship Falsification Density divides friction nodes by *total* node count, perversely penalizing experiment-rich honest trees and incentivizing experiment suppression / friction padding; measures node-type ratio (surface) over science.

## WINNERS: agent2, agent4

---

## Per-winner critique + Stage-2 directions

### agent2 (Grounded Failure Disclosure, Convergent Synthesis, Decision Deliberation Depth, Pivot Traceability & Consequence, Support-Level Calibration)

**Why it wins.** `Convergent Synthesis Score` is the single best DAG treatment in the field: via `flatten_with_ancestors` it discards `also_depends_on` edges that merely point at an ancestor/descendant (already implied by nesting) and requires citing/cited node *text overlap* before crediting an edge. This closes the "point `also_depends_on` at your own parent to farm edge density" hole that agent1 and agent3 both leave wide open. `Support-Level Calibration` is a genuinely novel fifth lens: it operationalizes the shape doc's "mismatched signaling" defect and the "pivots should default to `inferred`" guidance as a standalone honesty axis that cross-cuts the other four, making the set jointly hard to game (mass-`explicit` tanks calibration; mass-`inferred` tanks the grounding terms in metrics 1/3/4).

**Stage-2 improvements.**
- **Drop or justify the `inferred + has_refs + not pivot` half-penalty** in `support_level_calibration`. The shape doc says `source_refs` are *recommended* and never says a hedged node that also cites is a defect — penalizing a compiler for citing while honestly labeling `inferred` is a manufactured smell that could punish good extraction. Remove it or replace with something the shape doc actually flags.
- **Stopword-filter the lexical-overlap proxy.** `words()` keeps any token >3 chars, so generic shared words ("study", "data", "these", "results") trigger false-positive overlap on `Convergent Synthesis` and `Pivot Traceability`. Filter a content-word stoplist (or require ≥2 shared content words) so overlap tracks topical correspondence, not boilerplate.
- **Cap the `density_bonus` contribution in `grounded_failure_disclosure_score`.** It still mildly rewards adding more dead-ends; make the bonus contingent on each added dead-end being individually well-formed, or lower its ceiling.
- **Borrow agent4's genre-awareness for the zero-dead-end floor.** Capping a dead-end-free tree at 0.05 regardless of genre over-penalizes an honest systematic review with no stated failed approaches (the shape doc explicitly says this is legitimate). Soften the floor when the root question reads as a synthesis genre.

### agent4 (Candor Density, Evidentiary Grounding Fidelity, Alternative Substantiveness, Pivot Causal Traceability)

**Why it wins.** `Candor Density` is the most metascientifically honest metric in the tournament: it normalizes friction by *experiment count* and *genre* rather than by raw node count, directly answering the shape doc's point that reviews produce friction differently than wet-lab papers — and thereby avoiding agent1's backwards incentive. `Alternative Substantiveness` is the best decision metric: an explicit `GENERIC` blocklist ("do nothing", "status quo") plus jaccard distinctness-from-choice plus a concreteness proxy defeats the three obvious padding routes at once. `Pivot Causal Traceability` requires `trigger` text to share vocabulary with the *actual content* (`result`/`failure_mode`/`lesson`) of the nodes it points at — real anti-fabrication.

**Stage-2 improvements.**
- **Close the genre-sniff gaming hole.** `is_synthesis` is decided by keyword-matching the root question's own text, and synthesis lowers `expected_ratio` (0.15 vs 0.35) — so a primary-study compiler could inject "systematic review" into the question title to *halve* the friction it must disclose. Derive genre from a more tamper-resistant signal, or don't let the softer bar be reachable by free text the same actor writes.
- **Add a fifth lens covering support-level/signaling integrity.** With only 4 metrics, the `explicit`-without-`source_refs` "mismatched signaling" defect is only implicitly touched inside `grounding_fidelity`. A standalone calibration axis (cf. agent2 metric 5, agent3 metric 2) would harden the set and add an independent honesty lever.
- **Stopword-filter the pivot trigger/content overlap.** `tokens()` uses raw `.split()`, so function words ("the", "of", "and") can produce spurious overlap and hand out the 0.4 semantic-connection credit for free. Filter stopwords / require content-word intersection.
- **Acknowledge the frictionless-vs-laundered ambiguity explicitly.** Candor Density cannot distinguish a genuinely frictionless paper from a laundered extraction; state this limitation and consider a cross-check against grounding density.

---

## Why the losers lost

**agent1.** Its flagship `falsification_density` divides qualifying (`dead_end` + `decision`-with-≥2-alts) nodes by *total* node count. This makes an honest, experiment-rich tree score badly by construction — huu25 (9 experiments, 4 dead_ends of 17 nodes) caps near 0.24 even when every failure is fully grounded — and creates a perverse incentive to suppress or under-report experiments and pad friction to raise the ratio. That is measuring node-type *proportion* (a surface feature of the tree) rather than scientific quality, the exact failure mode the brief warns against, and it sits at the top of the set. Secondary weaknesses compound it: `evidence_traceability`'s specificity bonus fires on *any digit in a ref string*, trivially farmed with "Table 1" everywhere; and `dag_convergence` counts an `also_depends_on` edge to a direct ancestor as valid, redundant with nesting (the very hole agent2 closes). The combination essay is well-argued, but the core incentive is backwards.

**agent3.** Everything computes correctly and the hard constraint is respected, but each metric is a strictly softer version of the winners', so its combination essay overstates what the code actually enforces. `decision_deliberation_depth` tests distinctness only via `a.lower() != choice.lower()` (exact-string), so a near-duplicate alternative with one word changed passes — agent1 and agent4 use jaccard/token overlap. `dag_convergence_density` counts any `also_depends_on` to a resolvable distinct node as valid, including a direct ancestor, so parent-pointing games it — agent2's ancestor tracking catches this. `pivot_traceability`'s `linked` term is mere id-set intersection with no requirement that the pivot's `trigger` correspond to the pointed-at node's content — agent2 and agent4 both verify text overlap. With no content-correspondence check anywhere, its anti-Goodhart guarantees are weaker than claimed; a safe, sound entry that is simply out-engineered.
