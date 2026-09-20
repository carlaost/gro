# Tournament metric M19: Claim↔Experiment↔Evidence entailment (+ publication-bias)

- **Primary artifact**: §5 experiments (cross §2,§3,§4,§7,§9)
- **Primary shape file**: research/metrics/v3/tournament/shapes/05_experiments.md (read this; for the cross-layer artifacts noted above you MAY also consult research/metrics/v3/tournament/DATA_SHAPES.md for the other sections)

## What this metric is (from the assessment-critique ranked ledger)
Do experiments/evidence actually (type-aware) entail the claims they verify, and does a clinical-trial-registry cross-check surface publication bias (connected trial reporting different results)? [sem]+[ext trial lookup]. Verifier does D1 semantically; the publication-bias cross-check beats both round-1 and verifier.

## Your job
Expand the reasoning + build a generation/compute WORKFLOW for THIS metric per the EXPAND_BRIEF. Honor penalize-don't-skip (missing/thin inputs score down, never N/A; availability is itself part of the score). This metric ranked in the TOP 10 specifically because it is net-new vs the ARA verifier or scoped tighter — preserve that edge.
