# Stage 1 critique — `07_solution` (method layer)

## One-line verdicts + rank

- **Agent2 — RANK 1.** Tightest set; "Assumption/Boundary Grounding Overlap" (M4) is the single best anti-Goodhart mechanism in the field — it structurally ties `constraints.md` to the method files so fabricated specificity can't score. Genre+heuristics-omission audit (M3) is disciplined.
- **Agent1 — RANK 2.** Only proposal with a genuinely *deeper* science signal: "Assumption → Consequence Traceability" (M2) measures examined vs. decorative rigor. Cross-layer data-quality coverage (M5) honors the hard constraint explicitly.
- **Agent3 — RANK 3.** Careful and comprehensive, best heuristic handling (M5), but by its own admission all five metrics "key off the same underlying scientific virtue" — five specificity detectors on different surfaces, no orthogonal cross-layer check.
- **Agent4 — RANK 4.** Leans hardest into the surface/presence proxies the brief warns against (field-population, §-token presence, compiler-process rigor "independent of whether the paper was rigorous"); weakest Goodhart-resistance and real compute-soundness bugs.

## WINNERS: agent2, agent1

---

## Per-winner critique + Stage-2 directions

### Agent2 (winner)
Strongest because it is the only set whose flagship metric (M4, Grounding Overlap) enforces cross-layer coherence *structurally* rather than by hand-waving — to fake concrete constraints you must make them echo real method-file vocabulary, which is just doing the work. M3's decision to penalize heuristics-omission *only* when trick-language is present respects the shape doc's warning against penalizing correct absence.

Stage-2 must fix:
1. **M4's `ENTITY_PATTERN` is too loose.** `\b[A-Z][a-zA-Z]{2,}\d*\b` matches sentence-initial capitals and generic words ("Results", "Table", "Cohort") that trivially recur in method files, inflating overlap for free. Restrict to distinctive entities (acronyms `[A-Z]{2,}`, alphanumerics like `p-tau217`, versioned tools) and IDF/rarity-weight so common words don't count. This is the crown jewel — harden it.
2. **No dedicated assumption-quality metric.** Assumptions are only folded into M1's concrete-referent count. Add an examined-rigor check — borrow agent1's assumption→consequence idea — so the set rewards understanding *what breaks if an assumption is false*, not just whether it names a number.
3. **M2's empty `evidence_flags` returns 1.0.** Distinguish "cross-check ran and found no flags" from "flag list was never populated"; the latter should not earn a perfect score.

### Agent1 (winner)
Wins the #2 slot on M2 (Assumption→Consequence Traceability) — the deepest "measures science" idea in the tournament — plus M5's explicit, hard-constraint-honoring cross-layer caveat check.

Stage-2 must fix:
1. **M2's linkage test is gameable by copy-paste.** Overlap of "2 of first-6 words" credits verbatim duplication of assumption text into a limitation. The claimed defense (that this taxes M1) is indirect; add explicit near-duplicate detection so re-listing doesn't count as tracing a consequence.
2. **M4 genre-fit is too lenient and has a free pass.** `hits / max(2, len(sig)//2)` gives full marks for just 2 keyword hits, and unrecognized filenames get a flat 0.5 — so a wrong-genre file with an off-list name escapes entirely. Directly target the shape doc's named defect (`architecture.md` on a stat-synthesis review) rather than a soft keyword ratio.
3. **M3's `SOFTWARE_CALL = [A-Z][a-zA-Z]+\s*\(` false-positives** on any capitalized word before a paren ("Cohort ("). Tighten to real call syntax.
4. **M5 floors everyone to 0.1 when `evidence_inconsistencies` is absent.** Specify how that input is reliably wired from the evidence layer, or the metric is inert in practice.

---

## Why the losers lost

**Agent3** is the most careful loser — its M5 (Heuristic Capture Completeness) is the best-reasoned heuristic treatment in the field (penalizes trick-language-present-but-absent, gives correct-absence 0.7, discounts "Not specified" placeholders). But it lost on *architecture*: its own Combination section concedes all five metrics "key off the same underlying scientific virtue — specific, checkable, locus-tied content vs. boilerplate." M1 (limitation traceability), M2 (reproducibility density), M3 (assumption falsifiability), M4 (genre-fit) are four specificity/locus detectors pointed at different surfaces, not orthogonal metrics. Crucially it has *no* cross-layer coherence test — nothing like agent2's grounding overlap or agent1's assumption→consequence linkage — so its entire Goodhart defense rests on the assertion that "fabrication in one place looks anomalous when read jointly," which is exactly the weak, unenforced claim the brief says to attack. Agent1 beat it by pairing comparable specificity detectors with a genuine examined-rigor signal and a real cross-layer check.

**Agent4** lost on the brief's core criterion: it measures surface, not science. M2 (Limitation Section-Anchoring Ratio) counts §/Table token presence and the proposal itself concedes "a compiler could fabricate §4.5 freely" — a self-admitted Goodhart hole with only hand-waving defense. M3 (Heuristic Field-Completeness) is field-population counting. M5 (Compiler Self-Disclosure) explicitly measures "the compilation process's rigor, independent of whether the underlying paper itself was rigorous" — i.e. compiler behavior, precisely the artifact-surface signal the brief says loses. Compute soundness is also weak: M1's `entity_marker` = `([A-Z][a-zA-Z0-9\-]{2,}\s?){1,4}` matches any capitalized token including sentence-initial words, so nearly every assumption trips the "named entity" signal and testability is trivially inflated. The set reads as a bag of independent presence/format proxies rather than a jointly-constraining system.
