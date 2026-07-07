# External-ground-truth validation of the GRO metrics

**Source paper**: `research/metrics/v4-gro/EXTERNAL_VALIDATION_PAPER.md` — "Can the anchored and
judged GRO tiers be computed against external ground truth? A partial s7.1 experiment over six
Alzheimer's ARAs"

**ARA type**: self-compiled (own research; findings treated as claims)

## Summary

This paper runs a partial version of the GRO metrics spec's s7.1 step — *validate the anchored
(Tier B) and judged (Tier C) tiers against external ground truth* — the two tiers a prior
deterministic-tier experiment explicitly deferred because they require leaving the artifact. Over
a six-ARA, all-Alzheimer's-domain corpus (two donanemab trial papers on the same trial,
NCT04437511; three plasma-biomarker studies; one first-in-literature tau-seeding-assay preprint),
the tiers issued live MCP calls to PubMed and ClinicalTrials.gov to resolve references, check
novelty against indexed literature, join trial claims to registered outcomes, and search for
retractions. Result: 64/67 sampled references resolved to matching PubMed records (far above the
self-declared 0.520 mean rate, exposing a semantic gap in what "resolvable" measures); 31 headline
claims produced novelty verdicts spanning the full spectrum (10 novel, 10 incremental, 7
cannot_determine, 4 previously_reported) that separate the corpus on a novelty axis; both trial
papers joined cleanly to NCT04437511 with transparent post-hoc endpoint elevation but no concealed
outcome switching; zero retractions surfaced anywhere. The paper's central, deliberately honest
conclusion is that this demonstrates **external computability** (the tiers can reach and use real
external records) but **not good-versus-bad discrimination**, because the corpus contains zero
known-bad papers — that test requires a labelled contrast set of retracted/fabricated-reference
papers against a matched clean set, which is named as the explicit next step.

## Layer index

- `logic/problem.md` — what the prior (deterministic-tier) experiment left untested, and the two
  gaps this experiment targets
- `logic/claims.md` — C01–C08, the paper's load-bearing findings, each with sourced numbers
- `logic/experiments.md` — E01–E04, the four live-MCP analyses run over the six-ARA corpus
- `evidence/README.md` — pointers to `results.json`, `external_validation.json`, `external/*.json`,
  `benchmark.json`, and `seal/*.json`
