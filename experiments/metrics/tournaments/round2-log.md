# Metric tournament — ROUND 2 (per proposed metric) — orchestration log (durable; resume from here)

Goal: take Carla's per-artifact PROPOSED metrics (the `## indicators` blocks in ../tournament/DATA_SHAPES.md),
prune/merge/rank them (assessment-critique), then run a per-metric tournament on the survivors.

## Flow
1. Assessment-critique (Fable, DONE-when METRICS_CANDIDATES.md exists): extract → prune → merge → RANK,
   weighting UP metrics NOT in the ARA verifier or where ours are scoped better. Emits ranked ledger + TOP 10 + MISSING.
2. Per surviving metric (TOP 10 first), a 4→2→1 tournament across 3 refine cycles:
   - Cycle 1: 4 EXPANDER agents — expand the metric's reasoning + build a generation/compute WORKFLOW
     for it (per EXPAND_BRIEF.md), taking the assessment-critique into account → Fable picks 2.
   - Cycle 2: the 2 improve → Fable critiques (keep 2).
   - Cycle 3: improve → Fable picks 1 + qualifies.
3. After TOP 10: check usage caps / headroom; continue down the ranking while reasonable, until out.

## Implementer model policy
- Expanders/improvers = **Codex** (`codex:codex-rescue`) WHILE it has usage; on a Codex usage/quota error, FALL BACK to **Sonnet** for that agent and thereafter. Reviewer/judge = **Fable** always.

## The one hard constraint (unchanged)
Metrics ASSUME input availability and PENALIZE missing/thin inputs (never skip/N-A); unavailability may
itself be an input. Availability of the artifact/field is itself a scoring indicator.

## Research manager
ON for this whole effort — run the research-manager epilogue each turn (per Carla).

## DEFINITION OF DONE
- Per-metric DoD: cycle1 (4 expanders + critique_c1 naming 2), cycle2 (2 improved + critique_c2), cycle3
  (2 improved + critique_c3 naming 1 winner + qualifier), all on disk under tournament2/<Mid>/; one-line outcome logged.
- Round DoD: TOP 10 complete (+ as many further-ranked as headroom allowed), and TOURNAMENT2_SUMMARY.md written
  (per-metric winner + workflow + qualifier; cross-metric synthesis; explicit note on which beat/So the verifier).
- Resume rule: run status2.py; for each metric with a LAUNCH action fire it; set markers; stop only on Round DoD or a hard limit (then checkpoint + ScheduleWakeup past reset).

## Status
- [ ] assessment-critique (METRICS_CANDIDATES.md) — dispatched
- [ ] status2.py built (keyed on TOP-10 M-ids once ledger lands)
- [ ] per-metric tournaments
- [ ] TOURNAMENT2_SUMMARY.md

## Assessment-critique DONE (METRICS_CANDIDATES.md)
64 proposed → 23 survivors. TOP 10 (tournament order), all chosen as net-new vs the ARA verifier or tighter-scoped:
M14 reference-landscape completeness [ext] · M17 novelty-vs-literature [ext][sem] · M18 claim-drift/reference-truthfulness [ext][sem] ·
M19 claim↔experiment↔evidence entailment + publication-bias [sem][ext] · M48 e2e-reproducibility bundle (fig+data+code) ·
M36 multi-perspective triangulation [sem] · M30 assumption realism & limitation validity [sem] · M32 method validity & verification [sem] ·
M64 controlled-vocab/latent-space anchoring [ext] · M09 FOL-ability (Oshima) [ext]/[sem].
Merges: re-use/FAIR/reproducibility/added-value cluster + X↔Y-consistency family collapsed; claim-drift(§4,§6) unified. Full ledger + MISSING list in METRICS_CANDIDATES.md.

## Per-metric tournament — IN PROGRESS
- status2.py built (10 metrics, 3-cycle 4→2→1 state machine + launched markers). Per-metric briefs + dirs created.
- Validating Codex implementer path on M14 first (4 Codex expanders launched). If Codex works → batch remaining 9; if Codex usage-errors → fall back to Sonnet.
- M14 c1 winners: exp2 (A), exp1 (B)

## CODEX EXHAUSTED (workspace out of credits) — FALLBACK TO SONNET for all implementers (expanders/improvers) from here. Reviewer stays Fable. M14 c2 improvers failed on Codex → re-run on Sonnet.
- M18 c1 winners: exp2 (A), exp4 (B)
- M48 c1 winners: exp1 (A), exp3 (B)
- M17 c1 winners: exp1 (A), exp2 (B)
- M19 c1 winners: exp2 (A), exp3 (B)
- M30 c1 winners: exp2 (A), exp4 (B)
- M36 c1 winners: exp4 (A), exp3 (B)
- M64 c1 winners: exp1 (A), exp3 (B)
- M32 c1 winners: exp1 (A), exp3 (B)
- M09 c1 winners: exp2 (A), exp4 (B)
- M14 DONE: WINNER A (sound external-literature recall; honestly-limited proxy)
- M18 DONE: WINNER B (sound arithmetic drift-check; A's identity formula non-reproducible)

## CHECKPOINT — 2026-07-06: HALTED on org monthly spend limit

**Stop cause:** Org monthly spend limit reached. All new subagents fail with
"You've hit your org's monthly spend limit." This is a HARD limit (not a rolling
usage window) — requires a manual raise via `/usage-credits` or claude.ai/admin-settings/usage.
No ScheduleWakeup set: a monthly cap does not auto-reset tonight.

**Final winners locked (critique_c3.md present): 2/10**
- M14 → WINNER A ("sound external recall, honestly-limited proxy")
- M18 → WINNER B ("sound arithmetic; A's identity formula non-reproducible")

**Ready to resume (per status2.py):**
- M17: i3 done (A+B) → LAUNCH final critique (pick 1 + qualify)
- M19, M48, M36, M30, M32, M64, M09: LAUNCH 2 cycle-3 improvers each
- Stale .imp3_launched markers cleared for M48/M36/M30/M32/M64 so resume re-fires cleanly.

**To resume:** run `python3 status2.py`, fire the LAUNCH actions it reports
(implementers on Sonnet, reviewer on Fable), loop until all 10 have critique_c3.md,
then write TOURNAMENT2_SUMMARY.md and capture round-2 results to the ARA.
