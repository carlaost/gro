# Metric tournament — orchestration log (durable state; resume from here)

Goal: for EACH artifact the ARA compiler emits, run a 2-stage tournament to discover Goodhart-resistant
"good-science" metrics, clean-room (proposers have NO knowledge of any existing metrics).

## Structure per artifact
- Stage 1: 4 BLIND proposer agents (Sonnet) → each writes a metric list to tournament/<artifact>/proposals/agentN.md
  → Fable critique reads all 4, picks 2 winners + critiques → tournament/<artifact>/critique_stage1.md
- Stage 2: 2 winners improve per critique → tournament/<artifact>/improved/{A,B}.md
  → Fable critique picks 1 + qualifies its results → tournament/<artifact>/critique_stage2.md

## The one constraint on proposers
A metric ASSUMES its inputs are available and computes anyway. Missing input → PENALIZE inside the metric
(score down), NEVER skip / return N/A. Unavailability MAY itself be an input to a metric. Otherwise free range.
Each metric: {name, how it signals good science, compute fn (code), what the fn does & why, why it + the
combination is not Goodhart-able}.

## Status
- [ ] DATA_SHAPES.md (artifact enumeration + shapes) — agent dispatched
- artifact tournaments: pending DATA_SHAPES artifact list

## Outcomes (one line per artifact as completed)
- 01_paper_manifest → winner A — honest manifest-integrity proxy, limited reach
- 02_claims → winner B — measures rigor, not scientific truth
- 03_concepts → winner A — honest extraction-quality proxy, not science
- 04_problem → winner A — honest-but-limited compile-quality proxy
- 05_experiments → winner B — measures structural rigor, ultimately lexical
- 06_related_work → winner A — measures compilation craft, not science
- 07_solution → winner A — structural grounding plus examined-rigor signal
- 08_exploration_tree → winner A — honest disclosure-integrity proxy, not quality
- 09_evidence → winner A — honest hygiene, claim-grounding stays gameable
- 10_implementation → winner B — honest-but-limited reproducibility-reporting hygiene measure
- 11_dataset → winner A — honest provenance-documentation proxy, not validity

TOURNAMENT_SUMMARY.md written: 11 artifacts, per-artifact metric lists + qualifiers, and a
cross-artifact synthesis (recurring theme: winners measure compilation/documentation hygiene,
not scientific validity; common Goodhart vectors: length-as-quality proxies, boilerplate
padding, fabricated-but-internally-consistent content, genre false positives).

## DEFINITION OF DONE (do not stop until met)
**Per-artifact DoD:** all 4 stages recorded on disk for that artifact —
  (1) proposals/agent{1,2,3,4}.md exist, (2) critique_stage1.md exists (names the 2 winners + critique),
  (3) improved/{A,B}.md exist, (4) critique_stage2.md exists (names 1 winner + qualifies its results);
  and a one-line outcome appended to the "Outcomes" section below.
**Total DoD:** every artifact in DATA_SHAPES.md's final list has met per-artifact DoD, AND a final
  TOURNAMENT_SUMMARY.md is written (the single winning metric-set per artifact + cross-artifact synthesis).
**Resume rule:** on any wake, read this log's Outcomes + scan tournament/*/ for the first artifact missing
  any of the 4 stage files, and continue from there. Do NOT stop while any artifact is incomplete.
**Only-stop conditions:** total DoD met (→ write summary, then stop), OR a hard session/spend limit
  (→ checkpoint here + ScheduleWakeup past reset + resume), never on convergence/judgment.

### Stage-1 winners (recorded as critiques land)
- 02_claims: agent2 (A), agent4 (B)
- 01_paper_manifest: agent2 (A), agent4 (B)
- 03_concepts: agent4 (A), agent3 (B)
- 04_problem: agent4 (A), agent2 (B)
- 05_experiments: agent2 (A), agent1 (B)
- 06_related_work: agent2 (A), agent1 (B)
- 07_solution: agent2 (A), agent1 (B)
- 02_claims DONE: winner B (measures rigor, not scientific truth)
- 08_exploration_tree: agent2 (A), agent4 (B)
- 01_paper_manifest DONE: winner A (honest manifest-integrity proxy, limited reach)
- 04_problem DONE: winner A (honest-but-limited compile-quality proxy)
- 09_evidence: agent1 (A), agent3 (B)
- 11_dataset: agent1 (A), agent2 (B)
- 10_implementation: agent2 (A), agent4 (B)
